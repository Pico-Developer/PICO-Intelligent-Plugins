#!/usr/bin/env python3
"""Probe a Perfetto trace before Spatial performance analysis.

The probe is intentionally a readiness check, not a cause analyzer. It
records trace identity, bounds, schema, row counts, process/thread identity,
and the availability of generic and Spatial-specific evidence sources.

Usage:

    python spatial_probe.py \
        --trace C:/perf-data/trace.perfetto-trace \
        --app-process com.example.spatial \
        --output C:/perf-data/trace-probe.yaml \
        --quiet

Execution flow:

1. Validate the trace file and calculate its SHA-256.
2. Run ``pico-cli perf trace load <trace> --spatial-diagnose true``.
3. Parse the returned profiler session ID.
4. Query the loaded session through ``pico-cli perf trace query``.
5. Check trace bounds, schema, row counts, generic and Spatial tables,
   tables, target processes, key threads, and the App frame-driving thread.
6. Write a compact YAML summary or, with ``--detail``, a complete YAML result
   containing the original trace path and session ID.

Typical examples:

    # Print a compact YAML summary to stdout.
    python spatial_probe.py \
        --trace C:/perf-data/trace.perfetto-trace \
        --app-process com.example.spatial

    # Save the compact YAML summary without printing it.
    python spatial_probe.py \
        --trace C:/perf-data/trace.perfetto-trace \
        --app-process com.example.spatial \
        --output C:/perf-data/trace-probe.yaml \
        --quiet

    # Save the complete YAML result, including every check and row count.
    python spatial_probe.py \
        --trace C:/perf-data/trace.perfetto-trace \
        --app-process com.example.spatial \
        --detail \
        --output C:/perf-data/trace-probe-detail.yaml \
        --quiet

    # Use a non-default profiler daemon port.
    python spatial_probe.py \
        --trace C:/perf-data/trace.perfetto-trace \
        --app-process com.example.spatial \
        --daemon-port 9501

    # Make Probe failure block the Analysis stage.
    python spatial_probe.py \
        --trace C:/perf-data/trace.perfetto-trace \
        --app-process com.example.spatial \
        --strict

Required inputs:

* ``--trace``: path to the Perfetto trace file.
* ``--app-process``: target Spatial App process/package name.

Compatibility:

* ``--package`` is an alias for ``--app-process``.
* ``--perf-command`` can override the default ``pico-cli perf`` command prefix.
* ``--query-runner`` is retained for compatibility, but the default query path is
  ``pico-cli perf trace query`` and does not require the Python ``perfetto``
  package.

The command always returns YAML. The default output is a compact summary;
``--detail`` preserves the complete machine-readable result. A successful
probe can still be partial: missing tables and signals are reported as
limitations instead of being treated as negative evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    import yaml
except ImportError as error:
    raise SystemExit(
        "Missing dependency: PyYAML. Install it with: python -m pip install pyyaml"
    ) from error


PROBE_VERSION = 1
DEFAULT_DAEMON_HOST = "127.0.0.1"
DEFAULT_DAEMON_PORT = 9500
DEFAULT_TIMEOUT_SECONDS = 120.0
DEFAULT_MIN_DURATION_SECONDS = 3.0
DEFAULT_MAX_IDENTITY_ROWS = 1000

STATUS_OBSERVED = "observed"
STATUS_NOT_OBSERVED = "not_observed"
STATUS_MISSING_EVIDENCE = "missing_evidence"
STATUS_OUT_OF_SCOPE = "out_of_scope"
STATUS_QUERY_FAILED = "query_failed"
STATUS_NOT_RECORDED = "not_recorded"
STATUS_UNSUPPORTED = "unsupported"
STATUS_UNKNOWN = "unknown"

SPATIAL_TABLE_GROUPS: dict[str, tuple[str, ...]] = {
    "spatial_frames": ("OpenXRClientSpatialFrames",),
    "spatial_abnormal_frames": ("SpatialRuntimeAbnormalFrames",),
    "spatial_bottlenecks": ("SpatialBottleneckEvents",),
    "spatial_metrics": (
        "TargetAppMetricCounterStates",
        "spatial_metrics_definitions",
    ),
}

CAPABILITY_TABLE_GROUPS: dict[str, tuple[str, ...]] = {
    "trace_bounds": ("trace_bounds",),
    "metadata": ("metadata",),
    "trace_core": ("process", "thread", "slice", "track", "thread_track"),
    "thread_states": ("thread_state",),
    "scheduling": ("sched",),
    "counters": ("counter", "counter_track"),
    "frame_timeline": (
        "actual_frame_timeline_slice",
        "expected_frame_timeline_slice",
    ),
    "gpu": ("gpu_slice", "gpu_track"),
    "arguments": ("args",),
    **SPATIAL_TABLE_GROUPS,
}


def split_command_prefix(command: str) -> list[str]:
    parts = shlex.split(command, posix=(os.name != "nt"))
    if os.name == "nt":
        parts = [part.strip("\"'") for part in parts]
    return parts


def resolve_executable(executable: str) -> str:
    resolved = shutil.which(executable)
    if resolved:
        return resolved
    if os.name == "nt" and not Path(executable).suffix:
        for suffix in (".cmd", ".bat", ".exe"):
            resolved = shutil.which(executable + suffix)
            if resolved:
                return resolved
    return executable


def build_pico_perf_command(perf_command: str, *args: str) -> list[str]:
    prefix = split_command_prefix(perf_command)
    if not prefix:
        raise ProbeError("--perf-command must not be empty")
    command = [resolve_executable(prefix[0]), *prefix[1:]]
    if "perf" not in command[1:]:
        command.append("perf")
    command.extend(str(arg) for arg in args)
    return command

THREAD_ROLE_PATTERNS: dict[str, tuple[str, ...]] = {
    "render_thread": ("%renderthread%",),
    "spatial_main": ("%spatial_main%", "%spatialmain%"),
    "engine_render": ("%eng-render%", "%eng_render%", "%engrender%"),
    "xr_wait": ("%xr_wait%", "%xrwait%"),
    "gpu_frame_end": ("%gpu_frame_end%", "%gpuframeend%"),
    "compositor": ("%compositor%",),
}


class ProbeError(RuntimeError):
    """Raised when a query backend cannot execute a probe query."""


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def first_value(rows: Sequence[Mapping[str, Any]], key: str) -> Any:
    if not rows:
        return None
    return rows[0].get(key)


def as_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class QueryBackend:
    """Small interface shared by probe query backends."""

    description = "unknown"

    def query(self, sql: str) -> list[dict[str, Any]]:
        raise NotImplementedError


class ProfilerSessionBackend(QueryBackend):
    description = "profiler_session"

    def __init__(
        self,
        session_id: str,
        daemon_host: str,
        daemon_port: int,
        perf_command: str,
        query_runner: str | None,
        timeout_seconds: float,
    ) -> None:
        self.session_id = session_id
        self.daemon_host = daemon_host
        self.daemon_port = daemon_port
        self.perf_command = perf_command
        self.timeout_seconds = timeout_seconds
        self.query_runner = (
            self._resolve_query_runner(query_runner) if query_runner else None
        )

    @staticmethod
    def _resolve_query_runner(query_runner: str | None) -> Path:
        if query_runner:
            runner_path = Path(query_runner).expanduser().resolve()
            if not runner_path.is_file():
                raise ProbeError(f"query runner does not exist: {runner_path}")
            return runner_path

        script_path = Path(__file__).resolve()
        for parent in script_path.parents:
            candidate = parent / "global" / "scripts" / "run_query.py"
            if candidate.is_file():
                return candidate
        raise ProbeError(
            "could not locate global/scripts/run_query.py; "
            "use --query-runner to provide it explicitly"
        )

    def query(self, sql: str) -> list[dict[str, Any]]:
        if self.query_runner is not None:
            command = [
                sys.executable,
                str(self.query_runner),
                "--session",
                self.session_id,
                "--daemon-host",
                self.daemon_host,
                "--daemon-port",
                str(self.daemon_port),
                "--timeout",
                str(self.timeout_seconds),
                "--sql",
                sql,
            ]
        else:
            command = build_pico_perf_command(
                self.perf_command,
                "trace",
                "query",
                "--session",
                self.session_id,
                "--sql",
                sql,
                "-p",
                str(self.daemon_port),
            )
        try:
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds + 10,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise ProbeError(f"session query timed out: {error}") from error
        except OSError as error:
            raise ProbeError(f"failed to launch query command: {error}") from error
        if completed.returncode != 0:
            details = completed.stderr.strip() or completed.stdout.strip()
            raise ProbeError(
                f"session query failed with exit code "
                f"{completed.returncode}: {details}"
            )
        try:
            payload = json.loads(completed.stdout.strip())
        except json.JSONDecodeError as error:
            payload = self._parse_prefixed_json(completed.stdout, error)
        if isinstance(payload, dict):
            for key in ("rows", "data", "result"):
                value = payload.get(key)
                if isinstance(value, list):
                    payload = value
                    break
            if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
                nested = payload["data"]
                rows = nested.get("rows") or nested.get("result")
                if isinstance(rows, list):
                    payload = rows
        if not isinstance(payload, list) or not all(
            isinstance(row, dict) for row in payload
        ):
            raise ProbeError("query runner returned a non-row JSON payload")
        return payload

    @staticmethod
    def _parse_prefixed_json(stdout: str, original_error: json.JSONDecodeError) -> Any:
        text = stdout.strip()
        for index, char in enumerate(text):
            if char not in "[{":
                continue
            try:
                return json.loads(text[index:])
            except json.JSONDecodeError:
                continue
        raise ProbeError(
            f"query command returned invalid JSON: {original_error}"
        ) from original_error


class PerfTraceLoader:
    """Load a trace through the Profiler CLI and extract its session ID."""

    SESSION_PATTERN = re.compile(
        r"(?:\[TraceLoad\]\s*)?Session:\s*([0-9a-fA-F-]+)",
        re.IGNORECASE,
    )

    def __init__(
        self,
        trace_path: Path,
        perf_command: str,
        daemon_port: int,
        timeout_seconds: float,
    ) -> None:
        self.trace_path = trace_path
        self.perf_command = perf_command
        self.daemon_port = daemon_port
        self.timeout_seconds = timeout_seconds

    def load(self) -> tuple[str, dict[str, Any]]:
        command = build_pico_perf_command(
            self.perf_command,
            "trace",
            "load",
            str(self.trace_path),
            "--spatial-diagnose",
            "true",
            "-p",
            str(self.daemon_port),
        )
        try:
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise ProbeError(f"{' '.join(command[:3])} timed out: {error}") from error
        except OSError as error:
            raise ProbeError(f"failed to launch {' '.join(command[:3])}: {error}") from error

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        combined_output = f"{stdout}\n{stderr}"
        session_match = self.SESSION_PATTERN.search(combined_output)
        load_result = {
            "command": command,
            "returncode": completed.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "spatial_diagnose": True,
            "daemon_port": self.daemon_port,
        }
        if completed.returncode != 0:
            details = stderr or stdout or f"{' '.join(command[:3])} failed without output"
            raise ProbeError(
                f"{' '.join(command[:3])} failed with exit code "
                f"{completed.returncode}: {details}"
            )
        if session_match is None:
            raise ProbeError(
                f"{' '.join(command[:3])} succeeded but no session ID was found in its output"
            )
        session_id = session_match.group(1)
        load_result["session_id"] = session_id
        return session_id, load_result


def resolve_table_names(
    schema_rows: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, str], list[str], list[str]]:
    table_map: dict[str, str] = {}
    tables: list[str] = []
    views: list[str] = []
    for row in schema_rows:
        name = row.get("name")
        object_type = str(row.get("type") or "").lower()
        if not isinstance(name, str) or not name:
            continue
        table_map[name.lower()] = name
        if object_type == "view":
            views.append(name)
        else:
            tables.append(name)
    return table_map, sorted(tables), sorted(views)


def actual_name(table_map: Mapping[str, str], requested: str) -> str | None:
    return table_map.get(requested.lower())


def make_check(
    check_id: str,
    status: str,
    message: str,
    *,
    severity: str = "info",
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    check: dict[str, Any] = {
        "id": check_id,
        "status": status,
        "severity": severity,
        "message": message,
    }
    if details:
        check["details"] = dict(details)
    return check


class ProbeRun:
    def __init__(self, arguments: argparse.Namespace) -> None:
        self.arguments = arguments
        self.result: dict[str, Any] = {
            "schema_version": 1,
            "probe_version": PROBE_VERSION,
            "generated_at_utc": utc_now(),
            "source": {},
            "trace": {},
            "processor": {},
            "schema": {
                "tables": [],
                "views": [],
                "row_counts": {},
            },
            "tables": {},
            "table_details": {},
            "identities": {},
            "checks": [],
            "limitations": [],
        }
        self.table_map: dict[str, str] = {}
        self.backend: QueryBackend | None = None

    def add_check(self, check: dict[str, Any]) -> None:
        self.result["checks"].append(check)
        if check["status"] in {
            STATUS_MISSING_EVIDENCE,
            STATUS_QUERY_FAILED,
            STATUS_UNSUPPORTED,
            STATUS_UNKNOWN,
        }:
            self.result["limitations"].append(
                f"{check['id']}: {check['message']}"
            )

    def query(self, sql: str, query_id: str) -> list[dict[str, Any]]:
        if self.backend is None:
            raise ProbeError("query backend is not initialized")
        try:
            return self.backend.query(sql)
        except ProbeError as error:
            self.add_check(
                make_check(
                    query_id,
                    STATUS_QUERY_FAILED,
                    str(error),
                    severity="error",
                )
            )
            raise

    def discover_schema(self) -> None:
        schema_sql = """
SELECT name, type
FROM sqlite_master
WHERE type IN ('table', 'view')
ORDER BY name
""".strip()
        try:
            schema_rows = self.query(schema_sql, "schema_discovery")
        except ProbeError:
            return
        self.table_map, tables, views = resolve_table_names(schema_rows)
        self.result["schema"]["tables"] = tables
        self.result["schema"]["views"] = views
        self.add_check(
            make_check(
                "schema_discovery",
                STATUS_OBSERVED,
                f"discovered {len(tables)} tables and {len(views)} views",
                details={"table_count": len(tables), "view_count": len(views)},
            )
        )

    def probe_file(self) -> bool:
        trace_path = self.arguments.trace
        resolved_path = trace_path.expanduser().resolve()
        self.result["source"] = {
            "kind": "trace_file_pending_load",
            "trace_path": str(resolved_path),
        }
        self.result["trace"]["path"] = str(resolved_path)
        if not resolved_path.is_file():
            self.add_check(
                make_check(
                    "trace_file",
                    STATUS_MISSING_EVIDENCE,
                    f"trace file does not exist: {resolved_path}",
                    severity="error",
                )
            )
            return False
        size_bytes = resolved_path.stat().st_size
        trace_hash = sha256_file(resolved_path)
        self.result["trace"].update(
            {
                "size_bytes": size_bytes,
                "sha256": trace_hash,
            }
        )
        self.add_check(
            make_check(
                "trace_file",
                STATUS_OBSERVED if size_bytes > 0 else STATUS_MISSING_EVIDENCE,
                f"trace file is {'non-empty' if size_bytes > 0 else 'empty'}",
                severity="error" if size_bytes == 0 else "info",
                details={"size_bytes": size_bytes, "sha256": trace_hash},
            )
        )
        minimum_size = self.arguments.min_trace_bytes
        if size_bytes < minimum_size:
            self.add_check(
                make_check(
                    "trace_file_min_size",
                    STATUS_NOT_OBSERVED,
                    f"trace file is smaller than configured minimum "
                    f"{minimum_size} bytes",
                    severity="warning",
                    details={
                        "size_bytes": size_bytes,
                        "minimum_bytes": minimum_size,
                    },
                )
            )
        return size_bytes > 0

    def load_trace(self) -> bool:
        if self.arguments.trace is None:
            self.add_check(
                make_check(
                    "trace_load",
                    STATUS_QUERY_FAILED,
                    "trace path is required before loading a profiler session",
                    severity="error",
                )
            )
            return False
        loader = PerfTraceLoader(
            self.arguments.trace.expanduser().resolve(),
            self.arguments.perf_command,
            self.arguments.daemon_port,
            self.arguments.timeout,
        )
        try:
            session_id, load_result = loader.load()
        except ProbeError as error:
            self.add_check(
                make_check(
                    "trace_load",
                    STATUS_QUERY_FAILED,
                    str(error),
                    severity="error",
                )
            )
            return False
        self.arguments.session = session_id
        self.result["source"].update(
            {
                "kind": "trace_file_loaded_session",
                "trace_path": str(self.arguments.trace.expanduser().resolve()),
                "session_id": session_id,
            }
        )
        self.result["trace"]["session_id"] = session_id
        self.result["load"] = load_result
        self.add_check(
            make_check(
                "trace_load",
                STATUS_OBSERVED,
                f"trace loaded into profiler session {session_id}",
                details=load_result,
            )
        )
        return True

    def initialize_backend(self) -> bool:
        try:
            self.backend = ProfilerSessionBackend(
                self.arguments.session,
                self.arguments.daemon_host,
                self.arguments.daemon_port,
                self.arguments.perf_command,
                self.arguments.query_runner,
                self.arguments.timeout,
            )
            self.result["processor"] = {
                "mode": "profiler_session",
                "status": STATUS_UNKNOWN,
                "note": "processor identity is owned by the profiler daemon",
            }
            return True
        except ProbeError as error:
            self.add_check(
                make_check(
                    "query_backend",
                    STATUS_QUERY_FAILED,
                    str(error),
                    severity="error",
                )
            )
            return False

    def probe_bounds(self) -> None:
        bounds_table = actual_name(self.table_map, "trace_bounds")
        rows: list[dict[str, Any]] = []
        bounds_source = "trace_bounds"
        if bounds_table:
            try:
                rows = self.query(
                    f"SELECT start_ts, end_ts FROM {quote_identifier(bounds_table)} LIMIT 1",
                    "trace_bounds_query",
                )
            except ProbeError:
                return
        else:
            try:
                rows = self.backend.query(
                    "SELECT start_ts, end_ts FROM trace_bounds LIMIT 1"
                )
            except ProbeError:
                rows = []
        if not rows and actual_name(self.table_map, "slice"):
            try:
                rows = self.query(
                    """
SELECT MIN(ts) AS start_ts, MAX(ts + dur) AS end_ts
FROM slice
WHERE dur >= 0
""".strip(),
                    "trace_bounds_fallback_query",
                )
            except ProbeError:
                return
        elif not rows:
            self.add_check(
                make_check(
                    "trace_bounds",
                    STATUS_MISSING_EVIDENCE,
                    "trace bounds are unavailable because trace_bounds and slice are absent",
                    severity="error",
                )
            )
            return

        start_ns = as_int(first_value(rows, "start_ts"))
        end_ns = as_int(first_value(rows, "end_ts"))
        if start_ns is None or end_ns is None:
            self.add_check(
                make_check(
                    "trace_bounds",
                    STATUS_NOT_OBSERVED,
                    "trace bounds query returned no valid start/end timestamps",
                    severity="error",
                )
            )
            return
        duration_ns = end_ns - start_ns
        if duration_ns < 0:
            duration_ns += 2**32
            time_anomaly = {
                "kind": "uint32_wrap_suspected",
                "raw_start_ns": start_ns,
                "raw_end_ns": end_ns,
                "normalized_duration_ns": duration_ns,
            }
            self.result["trace"]["time_anomaly"] = time_anomaly
            self.result["limitations"].append(
                "trace_bounds: end_ts is lower than start_ts; "
                "normalized using a suspected uint32 wrap"
            )
            self.add_check(
                make_check(
                    "trace_time_anomaly",
                    STATUS_UNKNOWN,
                    "trace bounds appear to wrap at 32 bits; normalized duration "
                    "is retained but absolute time ordering requires caution",
                    severity="warning",
                    details=time_anomaly,
                )
            )
        else:
            time_anomaly = None
        duration_seconds = duration_ns / 1_000_000_000
        self.result["trace"].update(
            {
                "start_ns": start_ns,
                "end_ns": end_ns,
                "duration_ns": duration_ns,
                "duration_s": duration_seconds,
                "bounds_source": bounds_source,
            }
        )
        minimum_duration = self.arguments.min_duration_seconds
        duration_status = (
            STATUS_OBSERVED
            if duration_seconds >= minimum_duration
            else STATUS_NOT_OBSERVED
        )
        duration_severity = (
            "info" if duration_status == STATUS_OBSERVED else "warning"
        )
        self.add_check(
            make_check(
                "trace_bounds",
                STATUS_OBSERVED,
                f"trace duration is {duration_seconds:.3f}s",
                details={
                    "start_ns": start_ns,
                    "end_ns": end_ns,
                    "duration_ns": duration_ns,
                },
            )
        )
        self.add_check(
            make_check(
                "trace_min_duration",
                duration_status,
                f"trace duration is {'at least' if duration_status == STATUS_OBSERVED else 'below'} "
                f"the configured minimum {minimum_duration:.3f}s",
                severity=duration_severity,
                details={
                    "duration_s": duration_seconds,
                    "minimum_duration_s": minimum_duration,
                },
            )
        )

    def probe_capabilities(self) -> None:
        table_results: dict[str, int] = {}
        table_details: dict[str, Any] = {}
        row_counts: dict[str, int] = {}
        capability_table_groups = dict(CAPABILITY_TABLE_GROUPS)
        capability_table_groups["spatial_bottleneck_suggestions"] = (
            "SpatialBottleneckRuleSuggestions",
            "SpatialBottleneckRuleSuggesstions",
        )
        for capability, requested_tables in capability_table_groups.items():
            resolved_tables = {
                requested: actual_name(self.table_map, requested)
                for requested in requested_tables
            }
            present_tables = {
                requested: actual
                for requested, actual in resolved_tables.items()
                if actual is not None
            }
            missing_tables = [
                requested
                for requested, actual in resolved_tables.items()
                if actual is None
            ]
            counts: dict[str, int] = {}
            query_errors: list[str] = []
            for requested, actual in present_tables.items():
                try:
                    rows = self.query(
                        f"SELECT COUNT(*) AS row_count FROM "
                        f"{quote_identifier(actual)}",
                        f"count_{capability}_{requested}",
                    )
                    count = as_int(first_value(rows, "row_count"))
                    if count is None:
                        query_errors.append(
                            f"count for {requested} did not return an integer"
                        )
                    else:
                        counts[requested] = count
                        row_counts[actual] = count
                except ProbeError as error:
                    query_errors.append(f"{requested}: {error}")

            is_alias_group = capability == "spatial_bottleneck_suggestions"
            if query_errors:
                state = STATUS_QUERY_FAILED
            elif is_alias_group and present_tables:
                state = (
                    "recorded_populated"
                    if any(count > 0 for count in counts.values())
                    else "recorded_empty"
                )
            elif not present_tables:
                state = STATUS_UNSUPPORTED
            elif missing_tables:
                state = STATUS_MISSING_EVIDENCE
            elif any(count > 0 for count in counts.values()):
                state = "recorded_populated"
            else:
                state = "recorded_empty"

            for requested in requested_tables:
                actual = present_tables.get(requested)
                table_error = next(
                    (
                        error
                        for error in query_errors
                        if error.startswith(f"{requested}:")
                    ),
                    None,
                )
                if table_error:
                    table_state = STATUS_QUERY_FAILED
                elif actual is None:
                    table_state = STATUS_UNSUPPORTED
                elif counts.get(requested, 0) > 0:
                    table_state = "recorded_populated"
                else:
                    table_state = "recorded_empty"
                table_results[requested] = (
                    1 if table_state == "recorded_populated" else 0
                )
                table_detail: dict[str, Any] = {
                    "state": table_state,
                    "table_name": actual,
                    "row_count": counts.get(requested, 0),
                }
                if table_error:
                    table_detail["error"] = table_error
                table_details[requested] = table_detail

            group_detail = {
                "state": state,
                "required_tables": list(requested_tables),
                "present_tables": present_tables,
                "missing_tables": missing_tables,
                "row_counts": counts,
            }
            if query_errors:
                group_detail["errors"] = query_errors
            check_severity = (
                "info"
                if state in {"recorded_populated", "recorded_empty"}
                else "warning"
            )
            self.add_check(
                make_check(
                    f"capability_{capability}",
                    state,
                    f"{capability}: {state}",
                    severity=check_severity,
                    details=group_detail,
                )
            )

        self.result["tables"] = table_results
        self.result["table_details"] = table_details
        self.result["schema"]["row_counts"] = row_counts
        self.probe_time_anomalies()

    def probe_time_anomalies(self) -> None:
        slice_table = actual_name(self.table_map, "slice")
        if not slice_table:
            return
        try:
            rows = self.query(
                f"""
SELECT
  MIN(ts) AS min_ts,
  MAX(ts) AS max_ts,
  MIN(dur) AS min_dur,
  MAX(dur) AS max_dur,
  SUM(CASE WHEN dur > 1000000000 THEN 1 ELSE 0 END) AS huge_duration_rows
FROM {quote_identifier(slice_table)}
WHERE ts >= 0 AND dur >= 0
""".strip(),
                "slice_time_sanity_query",
            )
        except ProbeError:
            return
        row = rows[0] if rows else {}
        max_duration = as_int(row.get("max_dur"))
        huge_duration_rows = as_int(row.get("huge_duration_rows")) or 0
        if max_duration is None or huge_duration_rows <= 0:
            return
        anomaly = {
            "kind": "suspicious_slice_duration",
            "max_dur_ns": max_duration,
            "huge_duration_rows": huge_duration_rows,
            "threshold_ns": 1_000_000_000,
        }
        self.result["trace"].setdefault("time_anomalies", []).append(anomaly)
        self.result["limitations"].append(
            "slice: one or more durations exceed 1 second; "
            "time-window aggregation must use bounded duration filters"
        )
        self.add_check(
            make_check(
                "slice_time_sanity",
                STATUS_UNKNOWN,
                "slice duration contains suspiciously large values",
                severity="warning",
                details=anomaly,
            )
        )

    def query_processes(
        self,
        label: str,
        names: Sequence[str],
        *,
        exact: bool = True,
    ) -> list[dict[str, Any]]:
        process_table = actual_name(self.table_map, "process")
        if not process_table:
            self.add_check(
                make_check(
                    f"process_{label}",
                    STATUS_MISSING_EVIDENCE,
                    "process table is unavailable",
                    severity="warning",
                )
            )
            return []
        predicates: list[str] = []
        for name in names:
            if exact:
                predicates.append(f"name = {sql_literal(name)}")
                predicates.append(f"name GLOB {sql_literal(name + ':*')}")
            else:
                predicates.append(
                    f"lower(name) LIKE {sql_literal('%' + name.lower() + '%')}"
                )
        sql = f"""
SELECT upid, pid, name, start_ts, end_ts
FROM {quote_identifier(process_table)}
WHERE {" OR ".join(predicates)}
ORDER BY start_ts, upid
LIMIT {int(self.arguments.max_identity_rows)}
""".strip()
        try:
            rows = self.query(sql, f"process_{label}_query")
        except ProbeError:
            return []
        self.result["identities"][label] = {
            "requested_names": list(names),
            "candidates": rows,
            "status": STATUS_OBSERVED if rows else STATUS_NOT_OBSERVED,
        }
        self.add_check(
            make_check(
                f"process_{label}",
                STATUS_OBSERVED if rows else STATUS_NOT_OBSERVED,
                f"{label}: found {len(rows)} process candidate(s)",
                severity="info" if rows else "warning",
                details={"candidate_count": len(rows)},
            )
        )
        return rows

    def probe_app_identity(self) -> None:
        """探测目标 App 进程与 App 帧驱动线程。"""
        try:
            package = self.arguments.package
            if package:
                self.query_processes("target_app", (package,))
            else:
                self.result["identities"]["target_app"] = {
                    "status": STATUS_OUT_OF_SCOPE,
                    "note": "--package was not provided",
                }
                self.add_check(
                    make_check(
                        "process_target_app",
                        STATUS_OUT_OF_SCOPE,
                        "target App identity was not requested because --package was omitted",
                    )
                )
            self.probe_frame_driving_threads()
        except Exception as error:
            self.result["identities"].setdefault("target_app", {})["error"] = str(error)
            self.add_check(
                make_check(
                    "probe_app_identity",
                    STATUS_QUERY_FAILED,
                    f"target App identity probe failed: {error}",
                    severity="warning",
                )
            )

    def probe_spatial_runtime_identity(self) -> None:
        """探测 Spatial Runtime、OpenXR Runtime 与 compositor 候选进程。"""
        try:
            self.query_processes(
                "spr",
                ("com.pico.spatial.runtime",),
            )
            self.query_processes(
                "openxr_runtime",
                ("com.pico.xr.openxr_runtime",),
            )
            self.query_processes(
                "compositor_candidates",
                ("compositor", "surfaceflinger"),
                exact=False,
            )
        except Exception as error:
            self.add_check(
                make_check(
                    "probe_spatial_runtime_identity",
                    STATUS_QUERY_FAILED,
                    f"Spatial Runtime identity probe failed: {error}",
                    severity="warning",
                )
            )

    def probe_identities(self) -> None:
        """保持对外入口不变，分阶段探测进程身份与关键线程。"""
        self.probe_app_identity()
        self.probe_spatial_runtime_identity()
        self.probe_threads()

    def probe_threads(self) -> None:
        thread_table = actual_name(self.table_map, "thread")
        if not thread_table:
            self.add_check(
                make_check(
                    "thread_identity",
                    STATUS_MISSING_EVIDENCE,
                    "thread table is unavailable",
                    severity="warning",
                )
            )
            return
        predicates = [
            f"lower(name) LIKE {sql_literal(pattern)}"
            for patterns in THREAD_ROLE_PATTERNS.values()
            for pattern in patterns
        ]
        sql = f"""
SELECT utid, tid, upid, name, start_ts, end_ts
FROM {quote_identifier(thread_table)}
WHERE name IS NOT NULL
  AND ({" OR ".join(predicates)})
ORDER BY upid, utid
LIMIT {int(self.arguments.max_identity_rows)}
""".strip()
        try:
            rows = self.query(sql, "thread_identity_query")
        except ProbeError:
            return

        role_matches: dict[str, list[dict[str, Any]]] = {}
        for role, patterns in THREAD_ROLE_PATTERNS.items():
            role_matches[role] = [
                row
                for row in rows
                if any(
                    pattern.strip("%").lower() in str(row.get("name") or "").lower()
                    for pattern in patterns
                )
            ]
        self.result["identities"]["key_threads"] = role_matches
        self.add_check(
            make_check(
                "thread_identity",
                STATUS_OBSERVED if rows else STATUS_NOT_OBSERVED,
                f"found {len(rows)} key thread candidate(s)",
                severity="info" if rows else "warning",
                details={
                    "candidate_count": len(rows),
                    "roles_with_matches": [
                        role for role, matches in role_matches.items() if matches
                    ],
                },
            )
        )

    def probe_frame_driving_threads(self) -> None:
        slice_table = actual_name(self.table_map, "slice")
        track_table = actual_name(self.table_map, "track")
        thread_table = actual_name(self.table_map, "thread")
        if not slice_table or not track_table or not thread_table:
            self.result["identities"]["app_frame_driving_threads"] = {
                "status": STATUS_MISSING_EVIDENCE,
                "note": "slice, track, or thread table is unavailable",
            }
            self.add_check(
                make_check(
                    "app_frame_driving_thread",
                    STATUS_MISSING_EVIDENCE,
                    "cannot dynamically resolve Choreographer#beginSpatialFrame "
                    "without slice, track, and thread tables",
                    severity="warning",
                )
            )
            return
        sql = f"""
SELECT
  thread.utid,
  thread.tid,
  thread.upid,
  thread.name,
  COUNT(*) AS matching_slice_count,
  MIN(slice.ts) AS first_ts,
  MAX(slice.ts + slice.dur) AS last_ts
FROM {quote_identifier(slice_table)} AS slice
JOIN {quote_identifier(thread_table)} AS thread
  ON thread.utid = (
    SELECT thread_track.utid
    FROM thread_track
    WHERE thread_track.id = slice.track_id
  )
WHERE lower(slice.name) LIKE '%choreographer#beginspatialframe%'
  AND slice.dur BETWEEN 0 AND 1000000000
GROUP BY thread.utid, thread.tid, thread.upid, thread.name
ORDER BY matching_slice_count DESC
LIMIT {int(self.arguments.max_identity_rows)}
""".strip()
        try:
            rows = self.query(sql, "app_frame_driving_thread_query")
        except ProbeError:
            self.result["identities"]["app_frame_driving_threads"] = {
                "status": STATUS_QUERY_FAILED,
            }
            return
        status = STATUS_OBSERVED if rows else STATUS_NOT_OBSERVED
        self.result["identities"]["app_frame_driving_threads"] = {
            "status": status,
            "candidates": rows,
            "resolution_method": "Choreographer#beginSpatialFrame slice",
        }
        self.add_check(
            make_check(
                "app_frame_driving_thread",
                status,
                f"found {len(rows)} frame-driving thread candidate(s)",
                severity="info" if rows else "warning",
                details={"candidate_count": len(rows)},
            )
        )

    def finalize(self) -> None:
        table_states = self.result["tables"]
        core_ready = all(
            table_states.get(name) == 1
            for name in ("process", "thread", "track", "thread_track", "slice")
        )
        bounds_ready = "start_ns" in self.result["trace"]
        duration_ready = any(
            check["id"] == "trace_min_duration"
            and check["status"] == STATUS_OBSERVED
            for check in self.result["checks"]
        )
        backend_failed = any(
            check["id"] == "query_backend"
            and check["status"] == STATUS_QUERY_FAILED
            for check in self.result["checks"]
        )
        trace_file_valid = any(
            check["id"] == "trace_file"
            and check["status"] == STATUS_OBSERVED
            for check in self.result["checks"]
        )
        trace_usable = (
            (trace_file_valid or self.arguments.session is not None)
            and not backend_failed
            and bounds_ready
            and core_ready
        )
        analyze_ready = trace_usable and duration_ready
        blocking_checks = [
            check["id"]
            for check in self.result["checks"]
            if check["severity"] == "error"
        ]
        self.result["verdict"] = {
            "trace_usable": trace_usable,
            "analyze_ready": analyze_ready,
            "analyze_mode": (
                "spatial_trace"
                if analyze_ready
                else "trace_with_limitations"
            ),
            "blocking_checks": blocking_checks,
        }
        self.result["status"] = (
            "error"
            if backend_failed
            or any(
                check["id"] == "trace_file"
                and check["status"] == STATUS_MISSING_EVIDENCE
                for check in self.result["checks"]
            )
            else "complete"
            if not self.result["limitations"]
            else "partial"
        )

    def run(self) -> dict[str, Any]:
        file_valid = self.probe_file()
        if not file_valid:
            self.finalize()
            return self.result
        if not self.load_trace():
            self.finalize()
            return self.result
        if not self.initialize_backend():
            self.finalize()
            return self.result
        self.discover_schema()
        if not self.table_map:
            self.finalize()
            return self.result
        self.probe_bounds()
        self.probe_capabilities()
        self.probe_identities()
        self.finalize()
        return self.result


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe Perfetto trace readiness for Spatial performance analysis."
    )
    parser.add_argument(
        "--trace",
        type=Path,
        required=True,
        help="Absolute or relative path to a Perfetto trace.",
    )
    parser.add_argument(
        "--app-process",
        "--package",
        dest="package",
        required=True,
        help="Target Spatial App process/package name.",
    )
    parser.add_argument(
        "--query-runner",
        help=(
            "Compatibility path to global/scripts/run_query.py. "
            "By default spatial_probe uses pico-cli perf trace query directly."
        ),
    )
    parser.add_argument(
        "--perf-command",
        default="pico-cli perf",
        help="Profiler CLI command prefix used to load the trace (default: pico-cli perf).",
    )
    parser.add_argument("--daemon-host", default=DEFAULT_DAEMON_HOST)
    parser.add_argument("--daemon-port", type=int, default=DEFAULT_DAEMON_PORT)
    parser.add_argument(
        "--output",
        type=Path,
        help="Write probe output to this path; stdout is still used unless --quiet.",
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Output the complete YAML result instead of the compact summary.",
    )
    parser.add_argument(
        "--min-duration-seconds",
        type=float,
        default=DEFAULT_MIN_DURATION_SECONDS,
        help=f"Minimum duration check (default: {DEFAULT_MIN_DURATION_SECONDS}).",
    )
    parser.add_argument(
        "--min-trace-bytes",
        type=int,
        default=1,
        help="Warn when the trace is smaller than this size (default: 1).",
    )
    parser.add_argument(
        "--max-identity-rows",
        type=int,
        default=DEFAULT_MAX_IDENTITY_ROWS,
        help=f"Maximum process/thread candidates to retain (default: {DEFAULT_MAX_IDENTITY_ROWS}).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Query timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS}).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return exit code 2 when the probe is not ready for Analysis.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Do not print the formatted result to stdout when --output is provided.",
    )
    return parser.parse_args(argv)


def format_duration(seconds: Any) -> str:
    if not isinstance(seconds, (int, float)):
        return "unknown"
    return f"{seconds:.3f}s"


def format_process_identity(value: Mapping[str, Any] | None) -> str:
    if not value:
        return "not found"
    candidates = value.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return str(value.get("status", "unknown"))
    identities: list[str] = []
    for candidate in candidates[:3]:
        if not isinstance(candidate, Mapping):
            continue
        name = str(candidate.get("name") or "?")
        pid = candidate.get("pid")
        upid = candidate.get("upid")
        identities.append(f"{name} pid={pid} upid={upid}")
    suffix = " ..." if len(candidates) > 3 else ""
    return "; ".join(identities) + suffix


def format_thread_identity(value: Mapping[str, Any] | None) -> str:
    if not value:
        return "not found"
    candidates = value.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return str(value.get("status", "unknown"))
    identities: list[str] = []
    for candidate in candidates[:3]:
        if not isinstance(candidate, Mapping):
            continue
        identities.append(
            f"{candidate.get('name', '?')} "
            f"tid={candidate.get('tid', '?')} "
            f"utid={candidate.get('utid', '?')}"
        )
    suffix = " ..." if len(candidates) > 3 else ""
    return "; ".join(identities) + suffix


def format_key_threads(value: Mapping[str, Any] | None) -> str:
    if not value:
        return "not found"
    labels: list[str] = []
    for role, candidates in value.items():
        if not isinstance(candidates, list) or not candidates:
            continue
        first = candidates[0]
        if isinstance(first, Mapping):
            labels.append(
                f"{role}={first.get('name', '?')}/tid={first.get('tid', '?')}"
            )
            if len(candidates) > 1:
                labels[-1] += f"+{len(candidates) - 1}"
    return "; ".join(labels) if labels else "not found"


def build_summary_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    verdict = payload.get("verdict")
    verdict = verdict if isinstance(verdict, Mapping) else {}
    trace = payload.get("trace")
    trace = trace if isinstance(trace, Mapping) else {}
    source = payload.get("source")
    source = source if isinstance(source, Mapping) else {}
    identities = payload.get("identities")
    identities = identities if isinstance(identities, Mapping) else {}
    tables = payload.get("tables")
    tables = tables if isinstance(tables, Mapping) else {}
    limitations = payload.get("limitations")
    limitations = limitations if isinstance(limitations, list) else []

    if verdict.get("analyze_ready") is True:
        readiness = "ready"
    elif verdict.get("trace_usable") is True:
        readiness = "partial"
    else:
        readiness = "blocked"

    def identity_summary(value: Mapping[str, Any] | None) -> Any:
        if not value:
            return None
        candidates = value.get("candidates")
        if not isinstance(candidates, list):
            return {"status": value.get("status", "unknown")}
        return {
            "status": value.get("status", "unknown"),
            "candidates": [
                {
                    key: candidate.get(key)
                    for key in ("name", "pid", "upid", "tid", "utid")
                    if key in candidate
                }
                for candidate in candidates[:5]
                if isinstance(candidate, Mapping)
            ],
            "candidate_count": len(candidates),
        }

    return {
        "status": payload.get("status"),
        "verdict": {
            "readiness": readiness,
            "trace_usable": verdict.get("trace_usable"),
            "analyze_ready": verdict.get("analyze_ready"),
            "analyze_mode": verdict.get("analyze_mode"),
        },
        "trace": {
            "path": source.get("trace_path") or trace.get("path"),
            "session_id": source.get("session_id") or trace.get("session_id"),
            "sha256": trace.get("sha256"),
            "start_ns": trace.get("start_ns"),
            "end_ns": trace.get("end_ns"),
            "duration_s": trace.get("duration_s"),
        },
        "processes": {
            "app": identity_summary(identities.get("target_app")),
            "spr": identity_summary(identities.get("spr")),
            "openxr_runtime": identity_summary(identities.get("openxr_runtime")),
            "compositor": identity_summary(identities.get("compositor_candidates")),
        },
        "threads": {
            "frame_driver": identity_summary(
                identities.get("app_frame_driving_threads")
            ),
            "key_threads": format_key_threads(identities.get("key_threads")),
        },
        "tables": dict(tables),
        "limitations": limitations,
    }


def write_output(
    payload: Mapping[str, Any],
    output_path: Path | None,
    detail: bool,
) -> None:
    document = dict(payload) if detail else build_summary_payload(payload)
    rendered = yaml.safe_dump(
        document,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    if output_path is not None:
        resolved_output = output_path.expanduser().resolve()
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def build_fatal_result(message: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "probe_version": PROBE_VERSION,
        "generated_at_utc": utc_now(),
        "status": "error",
        "checks": [
            make_check(
                "probe",
                STATUS_QUERY_FAILED,
                message,
                severity="error",
            )
        ],
        "limitations": [message],
        "verdict": {
            "trace_usable": False,
            "analyze_ready": False,
            "analyze_mode": "unavailable",
            "blocking_checks": ["probe"],
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    try:
        if arguments.min_duration_seconds < 0:
            raise ValueError("--min-duration-seconds must be non-negative")
        if arguments.min_trace_bytes < 0:
            raise ValueError("--min-trace-bytes must be non-negative")
        if arguments.max_identity_rows < 1:
            raise ValueError("--max-identity-rows must be positive")
        probe_result = ProbeRun(arguments).run()
    except (OSError, ProbeError, ValueError) as error:
        probe_result = build_fatal_result(str(error))

    if arguments.output is not None:
        write_output(probe_result, arguments.output, arguments.detail)
        if not arguments.quiet:
            write_output(probe_result, None, arguments.detail)
    else:
        write_output(probe_result, None, arguments.detail)

    if probe_result.get("status") == "error":
        return 1
    if arguments.strict and not probe_result.get("verdict", {}).get("analyze_ready"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
