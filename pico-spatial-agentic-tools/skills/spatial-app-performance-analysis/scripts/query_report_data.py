#!/usr/bin/env python3
"""
query_report_data.py

用途：
  从 Perfetto trace 和可选 fast-perf.json 中提取报告渲染所需的核心数据，输出统一 JSON。
  该脚本会：
  1. 优先复用或创建 pico-cli perf trace session
  2. 复用 trace load --spatial-diagnose true 已创建的 Spatial 诊断表
  3. 查询 App 主线程帧 Bucket、超预算逐帧 dur_ms、SPR 帧 Bucket / 帧类型 / CPUTime / GPUTime Bucket
  4. 如提供 fast-perf.json，则提取 FPS 趋势和 CPU/GPU 趋势

用法示例：
  python3 scripts/query_report_data.py \
    --trace ./session-output-<timestamp>/performance-data/trace-perf.perfetto-trace \
    --fast-perf ./session-output-<timestamp>/performance-data/fast-perf.json

  python3 scripts/query_report_data.py \
    --trace ./session-output-<timestamp>/performance-data/trace-perf.perfetto-trace \
    --app-package com.example.app \
    --output ./session-output-<timestamp>/performance-data/report-data.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol

APP_BUCKET_KEYS = ["200ms+", "100~200ms", "33~100ms", "22~33ms", "11~22ms", "<11ms"]
SPR_FRAME_BUCKET_KEYS = ["33~50ms", "22~33ms", "11~22ms", "<11ms"]
SPR_FRAME_TYPE_KEYS = ["Normal", "Late", "Miss", "Early", "Discard"]
STAGE_BUCKET_KEYS = [">16ms", "12~16ms", "8~12ms", "4~8ms", "<4ms"]
DEFAULT_RENDER_COUNTER_PROCESS = "com.pico.spatial.runtime"
DEFAULT_RENDER_COUNTER_NAME = "3D Mesh Draw Call Count"
DEFAULT_RENDER_LOAD_COUNTERS_CONFIG = (
    Path(__file__).resolve().parents[1] / "references" / "render-load-counters.json"
)


REQUIRED_SPATIAL_TABLES = [
    "OpenXRClientSpatialFrames",
]


class TraceQueryClient(Protocol):
    def query_rows(self, sql: str) -> List[dict]:
        ...


def parse_session_id(output: str) -> str:
    match = re.search(
        r"(?:\[TraceLoad\]\s*)?Session:\s*([0-9a-fA-F-]+)",
        output,
        flags=re.IGNORECASE,
    )
    if not match:
        raise RuntimeError(f"无法从 pico-cli perf trace load 输出中解析 session id: {output[-1000:]}")
    return match.group(1)


def parse_cli_rows(stdout: str) -> List[dict]:
    text = stdout.strip()
    if not text:
        return []
    candidates = [text]
    first_bracket = min(
        [index for index in (text.find("["), text.find("{")) if index >= 0],
        default=-1,
    )
    if first_bracket > 0:
        candidates.append(text[first_bracket:])
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            if not all(isinstance(row, dict) for row in payload):
                raise RuntimeError(f"pico-cli perf trace query 返回了非对象数组: {payload!r}")
            return payload
        if isinstance(payload, dict):
            for key in ("rows", "data", "result"):
                value = payload.get(key)
                if isinstance(value, list):
                    if not all(isinstance(row, dict) for row in value):
                        raise RuntimeError(f"pico-cli perf trace query 返回了非对象数组: {value!r}")
                    return value
            if isinstance(payload.get("data"), dict):
                nested = payload["data"]
                rows = nested["rows"] if "rows" in nested else nested.get("result")
                if isinstance(rows, list):
                    if not all(isinstance(row, dict) for row in rows):
                        raise RuntimeError(f"pico-cli perf trace query 返回了非对象数组: {rows!r}")
                    return rows
    raise RuntimeError(f"无法解析 pico-cli perf trace query JSON 输出: {text[-1000:]}")


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


def build_pico_perf_command(pico_cli: str, *args: str) -> list[str]:
    prefix = split_command_prefix(pico_cli)
    if not prefix:
        raise RuntimeError("--pico-cli must not be empty")
    command = [resolve_executable(prefix[0]), *prefix[1:]]
    if "perf" not in command[1:]:
        command.append("perf")
    command.extend(str(arg) for arg in args)
    return command


class PicoCliTraceClient:
    def __init__(
        self,
        session_id: str,
        *,
        pico_cli: str,
        daemon_port: int,
        timeout: float,
    ) -> None:
        self.session_id = session_id
        self.pico_cli = pico_cli
        self.daemon_port = daemon_port
        self.timeout = timeout

    def _run_query(self, sql: str) -> subprocess.CompletedProcess[str]:
        command = build_pico_perf_command(
            self.pico_cli,
            "trace",
            "query",
            "--session",
            self.session_id,
            "--sql",
            sql,
            "-p",
            str(self.daemon_port),
        )
        return subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=self.timeout,
            check=False,
        )

    def query_rows(self, sql: str) -> List[dict]:
        completed = self._run_query(sql)
        if completed.returncode != 0:
            raise RuntimeError(
                "pico-cli perf trace query failed "
                f"(exit={completed.returncode}): {(completed.stderr or completed.stdout)[-1000:]}"
            )
        return parse_cli_rows(completed.stdout)


def start_pico_perf_daemon(pico_cli: str, daemon_port: int, timeout: float) -> None:
    command = build_pico_perf_command(pico_cli, "daemon", "start", "-p", str(daemon_port))
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        print(
            f"[query_report_data] pico-cli perf daemon start returned "
            f"{completed.returncode}; continuing with trace load: {message}",
            file=sys.stderr,
        )


def load_trace_with_pico_cli(
    trace_path: Path,
    *,
    pico_cli: str,
    daemon_port: int,
    timeout: float,
) -> str:
    command = build_pico_perf_command(
        pico_cli,
        "trace",
        "load",
        str(trace_path),
        "--spatial-diagnose",
        "true",
        "-p",
        str(daemon_port),
    )
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    output = f"{completed.stdout}\n{completed.stderr}"
    if completed.returncode != 0:
        raise RuntimeError(
            "pico-cli perf trace load failed "
            f"(exit={completed.returncode}): {output[-1000:]}"
        )
    return parse_session_id(output)


def exec_sql(client: TraceQueryClient, sql: str) -> List[dict]:
    return client.query_rows(sql)


def sql_string_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def ensure_spatial_diagnosis_tables(client: TraceQueryClient) -> None:
    missing: list[str] = []
    for table_name in REQUIRED_SPATIAL_TABLES:
        try:
            exec_sql(client, f"SELECT 1 AS ok FROM {table_name} LIMIT 1")
        except RuntimeError:
            missing.append(table_name)
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            "缺少 pico-cli perf trace load --spatial-diagnose true 自动生成的诊断表: "
            f"{joined}"
        )


def discover_client_package(client: TraceQueryClient) -> str:
    rows = exec_sql(
        client,
        """
        SELECT DISTINCT
          SUBSTR(
            name,
            INSTR(name, 'XRFetch ') + 8,
            INSTR(SUBSTR(name, INSTR(name, 'XRFetch ') + 9), ' ')
          ) AS name
        FROM slice
        WHERE name LIKE 'XRFetch %'
        """,
    )
    candidates = [str(row["name"]) for row in rows if row.get("name")]
    for candidate in candidates:
        if candidate == "com.pico.spatial.runtime":
            return candidate
    for candidate in candidates:
        lower = candidate.lower()
        if "spatial" in lower or "spr" in lower:
            return candidate
    if candidates:
        return candidates[0]
    raise RuntimeError("未能从 XRFetch Slice 中探测到客户端包名")


def ordered_bucket_dict(keys: Iterable[str], rows: Iterable[dict], bucket_key: str = "bucket", count_key: str = "cnt") -> Dict[str, int]:
    result = {key: 0 for key in keys}
    for row in rows:
        bucket = str(row[bucket_key])
        if bucket in result:
            result[bucket] = int(row[count_key])
    return result


def query_app_frame_buckets(client: TraceQueryClient, app_package: str) -> Dict[str, int]:
    app_package_sql = sql_string_literal(app_package)
    rows = exec_sql(
        client,
        f"""
        WITH main_frames AS (
          SELECT s.dur
          FROM slice s
          JOIN thread_track tt ON s.track_id = tt.id
          JOIN thread t ON tt.utid = t.utid
          JOIN process p ON t.upid = p.upid
          WHERE p.name = {app_package_sql}
            AND s.depth = 0
            AND s.name LIKE 'Choreographer#doFrame %'
            AND s.dur IS NOT NULL
        )
        SELECT
          CASE
            WHEN dur/1e6 >= 200 THEN '200ms+'
            WHEN dur/1e6 >= 100 THEN '100~200ms'
            WHEN dur/1e6 >= 33 THEN '33~100ms'
            WHEN dur/1e6 >= 22 THEN '22~33ms'
            WHEN dur/1e6 >= 11.11 THEN '11~22ms'
            ELSE '<11ms'
          END AS bucket,
          COUNT(*) AS cnt
        FROM main_frames
        GROUP BY bucket
        """,
    )
    return ordered_bucket_dict(APP_BUCKET_KEYS, rows)


def query_app_frame_durations_ms(client: TraceQueryClient, app_package: str) -> list[float]:
    app_package_sql = sql_string_literal(app_package)
    rows = exec_sql(
        client,
        f"""
        SELECT ROUND(s.dur / 1e6, 3) AS dur_ms
        FROM slice s
        JOIN thread_track tt ON s.track_id = tt.id
        JOIN thread t ON tt.utid = t.utid
        JOIN process p ON t.upid = p.upid
        WHERE p.name = {app_package_sql}
          AND s.depth = 0
          AND s.name LIKE 'Choreographer#doFrame %'
          AND s.dur IS NOT NULL
          AND s.dur / 1e6 >= 11.11
        ORDER BY s.ts ASC
        """,
    )
    durations: list[float] = []
    for row in rows:
        value = row.get("dur_ms")
        if value is None:
            continue
        durations.append(float(value))
    return durations


def query_spr_frame_buckets(client: TraceQueryClient) -> Dict[str, int]:
    rows = exec_sql(
        client,
        """
        SELECT
          CASE
            WHEN dur/1e6 >= 33 THEN '33~50ms'
            WHEN dur/1e6 >= 22 THEN '22~33ms'
            WHEN dur/1e6 >= 11.11 THEN '11~22ms'
            ELSE '<11ms'
          END AS bucket,
          COUNT(*) AS cnt
        FROM OpenXRClientSpatialFrames
        WHERE depth = 0
        GROUP BY bucket
        """,
    )
    return ordered_bucket_dict(SPR_FRAME_BUCKET_KEYS, rows)


def query_spr_frame_types(client: TraceQueryClient) -> Dict[str, int]:
    rows = exec_sql(
        client,
        """
        SELECT
          CASE
            WHEN name LIKE 'Late Frame %' THEN 'Late'
            WHEN name LIKE 'Miss Frame %' THEN 'Miss'
            WHEN name LIKE 'Early Frame %' THEN 'Early'
            WHEN name LIKE 'Discard Frame %' THEN 'Discard'
            ELSE 'Normal'
          END AS frame_type,
          COUNT(*) AS cnt
        FROM OpenXRClientSpatialFrames
        WHERE depth = 0
        GROUP BY frame_type
        """,
    )
    result = {key: 0 for key in SPR_FRAME_TYPE_KEYS}
    for row in rows:
        result[str(row["frame_type"])] = int(row["cnt"])
    return result


def query_stage_buckets(client: TraceQueryClient, stage_name: str) -> Dict[str, int]:
    stage_name_sql = sql_string_literal(stage_name)
    rows = exec_sql(
        client,
        f"""
        SELECT
          CASE
            WHEN dur/1e6 > 16 THEN '>16ms'
            WHEN dur/1e6 >= 12 THEN '12~16ms'
            WHEN dur/1e6 >= 8 THEN '8~12ms'
            WHEN dur/1e6 >= 4 THEN '4~8ms'
            ELSE '<4ms'
          END AS bucket,
          COUNT(*) AS cnt
        FROM OpenXRClientSpatialFrames
        WHERE name = {stage_name_sql}
        GROUP BY bucket
        """,
    )
    return ordered_bucket_dict(STAGE_BUCKET_KEYS, rows)


def query_spr_stats(client: TraceQueryClient) -> Dict[str, float | int]:
    rows = exec_sql(
        client,
        """
        SELECT
          COUNT(CASE WHEN depth = 0 THEN 1 END) AS total_frames,
          ROUND(AVG(CASE WHEN depth = 0 THEN dur END) / 1e6, 3) AS avg_frame_ms,
          ROUND(AVG(CASE WHEN name = 'CPUTime' THEN dur END) / 1e6, 3) AS avg_cpu_ms,
          ROUND(AVG(CASE WHEN name = 'GPUTime' THEN dur END) / 1e6, 3) AS avg_gpu_ms,
          ROUND(MIN(CASE WHEN depth = 0 THEN dur END) / 1e6, 3) AS min_frame_ms,
          ROUND(MAX(CASE WHEN depth = 0 THEN dur END) / 1e6, 3) AS max_frame_ms
        FROM OpenXRClientSpatialFrames
        """,
    )
    if not rows:
        return {
            "total_frames": 0,
            "avg_frame_ms": 0,
            "avg_cpu_ms": 0,
            "avg_gpu_ms": 0,
            "min_frame_ms": 0,
            "max_frame_ms": 0,
        }
    row = rows[0]
    return {
        "total_frames": int(row["total_frames"] or 0),
        "avg_frame_ms": float(row["avg_frame_ms"] or 0),
        "avg_cpu_ms": float(row["avg_cpu_ms"] or 0),
        "avg_gpu_ms": float(row["avg_gpu_ms"] or 0),
        "min_frame_ms": float(row["min_frame_ms"] or 0),
        "max_frame_ms": float(row["max_frame_ms"] or 0),
    }


def _empty_counter_payload(process_name: str, counter_name: str) -> dict[str, Any]:
    return {
        "series": [],
        "stats": {
            "count": 0,
            "avg": None,
            "max": None,
            "min": None,
            "first_ts_ns": "",
            "last_ts_ns": "",
            "process_name": process_name,
            "counter_name": counter_name,
        },
    }


def query_process_counter_series(
    client: TraceQueryClient, process_name: str, counter_name: str
) -> dict[str, Any]:
    process_name_sql = sql_string_literal(process_name)
    counter_name_sql = sql_string_literal(counter_name)
    rows = exec_sql(
        client,
        f"""
        WITH target_process AS (
          SELECT
            p.upid,
            p.pid,
            p.name AS process_name
          FROM process p
          WHERE p.name = {process_name_sql}
        ),
        target_counter_track AS (
          SELECT
            ct.id AS track_id,
            ct.name AS track_name,
            pct.upid
          FROM counter_track ct
          JOIN process_counter_track pct ON pct.id = ct.id
          JOIN target_process tp ON tp.upid = pct.upid
          WHERE ct.name = {counter_name_sql}
        ),
        samples AS (
          SELECT
            c.id,
            c.ts,
            c.value
          FROM counter c
          JOIN target_counter_track tct ON tct.track_id = c.track_id
        ),
        bounds AS (
          SELECT MIN(ts) AS first_ts
          FROM samples
        )
        SELECT
          CAST(s.ts AS TEXT) AS ts_ns,
          ROUND(s.ts / 1000000.0, 3) AS ts_ms,
          ROUND((s.ts - b.first_ts) / 1000000000.0, 3) AS time_s,
          s.value AS value
        FROM samples s
        JOIN bounds b
        ORDER BY s.ts ASC, s.id ASC
        """,
    )
    if not rows:
        return _empty_counter_payload(process_name, counter_name)

    series: list[dict[str, Any]] = []
    values: list[float] = []
    for row in rows:
        raw_value = row.get("value")
        value = float(raw_value) if isinstance(raw_value, (int, float)) else None
        if value is not None:
            values.append(value)
        series.append(
            {
                "ts_ns": str(row.get("ts_ns") or ""),
                "ts_ms": float(row["ts_ms"]) if isinstance(row.get("ts_ms"), (int, float)) else None,
                "time_s": float(row["time_s"]) if isinstance(row.get("time_s"), (int, float)) else None,
                "value": value,
            }
        )

    if not values:
        return _empty_counter_payload(process_name, counter_name)

    return {
        "series": series,
        "stats": {
            "count": len(series),
            "avg": round(sum(values) / len(values), 3),
            "max": max(values),
            "min": min(values),
            "first_ts_ns": str(series[0].get("ts_ns") or ""),
            "last_ts_ns": str(series[-1].get("ts_ns") or ""),
            "process_name": process_name,
            "counter_name": counter_name,
        },
    }


def default_render_load_counter_groups() -> list[dict[str, Any]]:
    return [
        {
            "id": "3d-render",
            "label": "3D Render",
            "process_name": DEFAULT_RENDER_COUNTER_PROCESS,
            "unit_label": "count",
            "counters": [DEFAULT_RENDER_COUNTER_NAME],
        }
    ]


def load_render_load_counter_groups(config_path: Path | None) -> list[dict[str, Any]]:
    if config_path is None:
        return default_render_load_counter_groups()
    if not config_path.exists():
        raise FileNotFoundError(f"render load counter config 不存在: {config_path}")
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    raw_groups = payload.get("groups") if isinstance(payload, dict) else None
    if not isinstance(raw_groups, list):
        raise RuntimeError("render load counter config 必须包含 groups 数组")

    groups: list[dict[str, Any]] = []
    for index, group in enumerate(raw_groups):
        if not isinstance(group, dict):
            continue
        counters = group.get("counters")
        counter_names = [str(item) for item in counters if item] if isinstance(counters, list) else []
        if not counter_names:
            continue
        process_name = str(group.get("process_name") or DEFAULT_RENDER_COUNTER_PROCESS)
        group_id = str(group.get("id") or f"group-{index + 1}")
        groups.append(
            {
                "id": group_id,
                "label": str(group.get("label") or group_id),
                "process_name": process_name,
                "unit_label": str(group.get("unit_label") or "value"),
                "counters": counter_names,
            }
        )
    return groups or default_render_load_counter_groups()


def query_render_load_counter_groups(
    client: TraceQueryClient, config_path: Path | None
) -> list[dict[str, Any]]:
    groups = []
    for group in load_render_load_counter_groups(config_path):
        counters = []
        for counter_name in group["counters"]:
            counter_payload = query_process_counter_series(
                client,
                group["process_name"],
                counter_name,
            )
            counters.append(
                {
                    "name": counter_name,
                    "process_name": group["process_name"],
                    "unit_label": group["unit_label"],
                    "series": counter_payload["series"],
                    "stats": counter_payload["stats"],
                }
            )
        groups.append(
            {
                "id": group["id"],
                "label": group["label"],
                "process_name": group["process_name"],
                "unit_label": group["unit_label"],
                "counters": counters,
            }
        )
    return groups


def to_float(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    for suffix in ["%", "Mhz", "MHz", "°C"]:
        text = text.replace(suffix, "")
    try:
        return float(text)
    except ValueError:
        return None


def build_trends(fast_perf: dict) -> tuple[list[dict], list[dict]]:
    raw = fast_perf.get("rawData") or []
    if not raw:
        return [], []

    base_time = raw[0].get("timeMs") or 0
    fps_trend = []
    cpu_gpu_trend = []
    for item in raw:
        time_ms = int(item.get("timeMs") or base_time)
        label = f"{max(0, round((time_ms - base_time) / 1000))}s"
        fps_trend.append(
            {
                "time": label,
                "app_fps": to_float(item.get("appFps")),
                "spr_fps": to_float(item.get("sysFps")),
            }
        )
        cpu_gpu_trend.append(
            {
                "time": label,
                "app_cpu": to_float(item.get("appCpu")),
                "system_cpu": to_float(item.get("systemCpu")),
                "gpu_usage": to_float(item.get("gpuUsage")),
                "gpu_freq": to_float(item.get("gpuFreq")),
                "gpu_temp": to_float(item.get("gpuTemp")),
            }
        )
    return fps_trend, cpu_gpu_trend


def query_report_metrics(
    client: TraceQueryClient,
    app_package: str | None = None,
    render_load_config: Path | None = DEFAULT_RENDER_LOAD_COUNTERS_CONFIG,
) -> dict[str, Any]:
    ensure_spatial_diagnosis_tables(client)
    client_pkg = discover_client_package(client)
    effective_app_package = app_package or client_pkg
    render_load_counter_groups = query_render_load_counter_groups(client, render_load_config)
    mesh_draw_call_count = _empty_counter_payload(
        DEFAULT_RENDER_COUNTER_PROCESS,
        DEFAULT_RENDER_COUNTER_NAME,
    )
    for group in render_load_counter_groups:
        for counter in group.get("counters", []):
            if counter.get("name") == DEFAULT_RENDER_COUNTER_NAME:
                mesh_draw_call_count = {
                    "series": counter.get("series", []),
                    "stats": counter.get("stats", {}),
                }
                break
    return {
        "app_frame_buckets": query_app_frame_buckets(client, effective_app_package),
        "app_frame_durations_ms": query_app_frame_durations_ms(client, effective_app_package),
        "spr_frame_buckets": query_spr_frame_buckets(client),
        "spr_frame_types": query_spr_frame_types(client),
        "spr_cpu_buckets": query_stage_buckets(client, "CPUTime"),
        "spr_gpu_buckets": query_stage_buckets(client, "GPUTime"),
        "spr_stats": query_spr_stats(client),
        "render_load_counter_groups": render_load_counter_groups,
        "mesh_draw_call_count_series": mesh_draw_call_count["series"],
        "mesh_draw_call_count_stats": mesh_draw_call_count["stats"],
    }


def build_report_data(
    trace_path: Path,
    fast_perf_path: Path | None = None,
    *,
    app_package: str | None = None,
    session_id: str | None = None,
    render_load_config: Path | None = DEFAULT_RENDER_LOAD_COUNTERS_CONFIG,
    pico_cli: str = "pico-cli",
    daemon_port: int = 9500,
    timeout: float = 180.0,
    start_daemon: bool = True,
) -> dict:
    fast_perf: dict[str, Any] = {}
    if fast_perf_path is not None:
        fast_perf = json.loads(fast_perf_path.read_text(encoding="utf-8"))
        if app_package is None:
            metadata_app = (fast_perf.get("metadata") or {}).get("app")
            if metadata_app:
                app_package = str(metadata_app)

    if session_id is None:
        if start_daemon:
            start_pico_perf_daemon(pico_cli, daemon_port, timeout)
        session_id = load_trace_with_pico_cli(
            trace_path,
            pico_cli=pico_cli,
            daemon_port=daemon_port,
            timeout=timeout,
        )
    client = PicoCliTraceClient(
        session_id,
        pico_cli=pico_cli,
        daemon_port=daemon_port,
        timeout=timeout,
    )
    metrics = query_report_metrics(
        client,
        app_package,
        render_load_config=render_load_config,
    )

    fps_trend, cpu_gpu_trend = build_trends(fast_perf)
    return {
        "meta": {
            "trace_path": str(trace_path),
            "fast_perf_path": str(fast_perf_path) if fast_perf_path is not None else None,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "query_source": "pico-cli perf",
            "pico_cli": pico_cli,
            "daemon_port": daemon_port,
            "session_id": session_id,
            "app_package": app_package,
            "render_load_counter_config": str(render_load_config) if render_load_config is not None else None,
        },
        **metrics,
        "fast_perf_summary": fast_perf.get("summary") if isinstance(fast_perf.get("summary"), dict) else {},
        "fps_trend": fps_trend,
        "cpu_gpu_trend": cpu_gpu_trend,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="提取报告渲染所需的 trace / fast-perf 数据")
    parser.add_argument("--trace", required=True, help="trace-perf.perfetto-trace 路径")
    parser.add_argument(
        "--fast-perf",
        help="可选 fast-perf.json 路径；缺失时仍输出 trace-derived details",
    )
    parser.add_argument(
        "--app-package",
        help="目标 App 包名；未提供时优先使用 fast-perf metadata.app，否则使用 trace 中的 XRFetch 客户端包名",
    )
    parser.add_argument("--session", help="已由 pico-cli perf trace load 创建的 session id")
    parser.add_argument(
        "--render-load-counters-config",
        default=str(DEFAULT_RENDER_LOAD_COUNTERS_CONFIG),
        help="渲染负载 counter 配置 JSON 路径",
    )
    parser.add_argument("--pico-cli", default="pico-cli", help="pico-cli 可执行文件路径或命令名")
    parser.add_argument("--daemon-port", type=int, default=9500, help="pico-cli perf daemon 端口")
    parser.add_argument("--timeout", type=float, default=180.0, help="pico-cli perf 查询超时时间，单位秒")
    parser.add_argument(
        "--no-daemon-start",
        action="store_true",
        help="未传 --session 时，不自动执行 pico-cli perf daemon start",
    )
    parser.add_argument("--output", help="输出 JSON 文件路径；不传则打印到 stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    trace_path = Path(args.trace).expanduser().resolve()
    fast_perf_path = (
        Path(args.fast_perf).expanduser().resolve() if args.fast_perf else None
    )
    if not trace_path.exists():
        raise FileNotFoundError(f"trace 文件不存在: {trace_path}")
    if fast_perf_path is not None and not fast_perf_path.exists():
        raise FileNotFoundError(f"fast-perf.json 不存在: {fast_perf_path}")

    result = build_report_data(
        trace_path,
        fast_perf_path,
        app_package=args.app_package,
        session_id=args.session,
        render_load_config=Path(args.render_load_counters_config).expanduser().resolve()
        if args.render_load_counters_config
        else None,
        pico_cli=args.pico_cli,
        daemon_port=args.daemon_port,
        timeout=args.timeout,
        start_daemon=not args.no_daemon_start,
    )
    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
