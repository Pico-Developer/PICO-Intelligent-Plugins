#!/usr/bin/env python3
"""
run_query.py

Cross-platform helper for running Perfetto SQL queries through
``pico-cli perf trace query``.

Motivation
----------
Passing SQL through `pico-cli perf trace query --sql "..."` on different shells
(cmd, PowerShell, bash, zsh) hits quoting / encoding / argv-length issues.
This script lets callers pass SQL via stdin or a file, then forwards the exact
SQL string as an argv value to `pico-cli perf trace query`.

Positioning
-----------
This helper never imports Python `perfetto`, never resolves the daemon HTTP
endpoint itself, and never launches `trace_processor_shell`. Session ownership,
daemon lookup, and trace querying remain inside `pico-cli perf`.

Usage
-----
    # Query a pico-cli perf trace session.
    python run_query.py --session <sessionId> --sql-file q.sql

    # Target a specific daemon (when multiple are running)
    python run_query.py --daemon-port 9500 --session <sessionId> --sql-file q.sql

    # Named query from ./sql-queries/<name>.sql
    python run_query.py --session <sessionId> --name query_cpu

    # SQL from stdin
    echo "SELECT COUNT(*) FROM slice" | python run_query.py --session <id> --stdin

    # Inline SQL (still safe: never touches a shell)
    python run_query.py --session <id> --sql "SELECT * FROM thread LIMIT 5"
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_SQL_DIR = Path(__file__).parent / "sql-queries"
DEFAULT_DAEMON_PORT = 9500


def _force_utf8_stdio() -> None:
    """Make sure stdout/stderr use UTF-8 on Windows terminals as well."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except Exception:
                pass


def _read_sql(args: argparse.Namespace) -> str:
    provided = [n for n in ("sql", "sql_file", "name", "stdin") if getattr(args, n)]
    if len(provided) != 1:
        raise SystemExit(
            "Exactly one of --sql / --sql-file / --name / --stdin must be provided"
        )

    if args.sql:
        return args.sql
    if args.sql_file:
        return Path(args.sql_file).read_text(encoding="utf-8")
    if args.name:
        candidate = DEFAULT_SQL_DIR / f"{args.name}.sql"
        if not candidate.is_file():
            raise SystemExit(f"Named query not found: {candidate}")
        return candidate.read_text(encoding="utf-8")
    # stdin
    data = sys.stdin.read()
    if not data.strip():
        raise SystemExit("No SQL received on stdin")
    return data


def _parse_cli_rows(stdout: str) -> list[dict]:
    text = stdout.strip()
    if not text:
        return []
    candidates = [text]
    for index, char in enumerate(text):
        if char in "[{":
            candidates.append(text[index:])
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            if not all(isinstance(row, dict) for row in payload):
                raise SystemExit(f"pico-cli perf trace query returned non-object rows: {payload!r}")
            return payload
        if isinstance(payload, dict):
            for key in ("rows", "data", "result"):
                value = payload.get(key)
                if isinstance(value, list):
                    if not all(isinstance(row, dict) for row in value):
                        raise SystemExit(
                            f"pico-cli perf trace query returned non-object rows: {value!r}"
                        )
                    return value
            if isinstance(payload.get("data"), dict):
                nested = payload["data"]
                rows = nested.get("rows") or nested.get("result")
                if isinstance(rows, list):
                    if not all(isinstance(row, dict) for row in rows):
                        raise SystemExit(
                            f"pico-cli perf trace query returned non-object rows: {rows!r}"
                        )
                    return rows
    raise SystemExit(f"Failed to parse pico-cli perf trace query JSON output: {text[-1000:]}")


def _split_command_prefix(command: str) -> list[str]:
    parts = shlex.split(command, posix=(os.name != "nt"))
    if os.name == "nt":
        parts = [part.strip("\"'") for part in parts]
    return parts


def _resolve_executable(executable: str) -> str:
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
    prefix = _split_command_prefix(pico_cli)
    if not prefix:
        raise SystemExit("--pico-cli must not be empty")
    command = [_resolve_executable(prefix[0]), *prefix[1:]]
    if "perf" not in command[1:]:
        command.append("perf")
    command.extend(str(arg) for arg in args)
    return command


def main() -> int:
    _force_utf8_stdio()

    parser = argparse.ArgumentParser(
        description=(
            "Run a Perfetto SQL query through pico-cli perf trace query."
        ),
    )

    # SQL input (mutually exclusive at runtime)
    parser.add_argument("--sql", help="Inline SQL string.")
    parser.add_argument("--sql-file", help="Path to a UTF-8 .sql file.")
    parser.add_argument(
        "--name",
        help=f"Named query file under {DEFAULT_SQL_DIR} (without .sql suffix).",
    )
    parser.add_argument(
        "--stdin", action="store_true", help="Read SQL from standard input."
    )

    # Endpoint resolution
    parser.add_argument(
        "--session",
        required=True,
        help="pico-cli perf trace session ID returned by trace load.",
    )
    parser.add_argument(
        "--daemon-port",
        dest="daemon_port",
        type=int,
        default=DEFAULT_DAEMON_PORT,
        help=(
            f"Profiler daemon port (default: {DEFAULT_DAEMON_PORT}). "
            f"Set this when multiple daemons are running."
        ),
    )
    parser.add_argument(
        "--pico-cli",
        default="pico-cli",
        help="pico-cli executable or command prefix (default: pico-cli).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Pass --execute to pico-cli perf trace query.",
    )

    # Output
    parser.add_argument(
        "--out",
        help="Write JSON result to this file instead of stdout.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent (default: 2). Use 0 for compact output.",
    )

    args = parser.parse_args()

    sql = _read_sql(args)

    command = build_pico_perf_command(
        args.pico_cli,
        "trace",
        "query",
        "--session",
        args.session,
        "--sql",
        sql,
        "-p",
        str(args.daemon_port),
    )
    if args.execute:
        command.append("--execute")

    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        raise SystemExit(
            f"pico-cli perf trace query failed with exit code "
            f"{completed.returncode}: {message[-1000:]}"
        )

    rows = [] if args.execute else _parse_cli_rows(completed.stdout)

    indent = args.indent if args.indent > 0 else None
    payload = json.dumps(rows, ensure_ascii=False, indent=indent, default=str)

    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(
            f"[run_query] wrote {len(rows)} row(s) to {args.out}",
            file=sys.stderr,
        )
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    sys.exit(main())
