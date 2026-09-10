import os
import re
import sys
import uuid
import signal
import shutil
import shlex
import threading
import subprocess
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import Any


FAST_PERF_NAME = "fast-perf.json"
TRACE_PERF_NAME = "trace-perf.perfetto-trace"
SIMPLE_PERF_NAME = "simple-perf.data"
SUMMARY_YAML_NAME = "collector-summary.yaml"
DEVICE_SIMPLEPERF_DATA = "/data/local/tmp/perf.data"

# 如果 trace stop 需要固定端口，可改成 "9500"
TRACE_STOP_PORT = None


class CollectorManager:
    def __init__(
        self,
        app_package,
        output_dir: Path,
        simple_perf_script: Path | None = None,
        python_cmd: str = "python",
        pico_cli: str = "pico-cli",
        serial: str | None = None,
        script_path: Path | None = None,
        command_line: list[str] | None = None,
        limitations: list[str] | None = None,
    ):
        self.app_package = app_package
        self.output_dir = output_dir
        self.simple_perf_script = simple_perf_script
        self.python_cmd = python_cmd
        self.pico_cli = pico_cli
        self.serial = serial
        self.script_path = script_path or Path(__file__).resolve()
        self.command_line = command_line or sys.argv
        self.limitations = limitations or []
        self.base_dir = Path.cwd()
        self.command_env = os.environ.copy()
        if self.serial:
            self.command_env["ANDROID_SERIAL"] = self.serial
            self.command_env["PICO_CLI_DEVICE"] = self.serial

        self.simple_perf_enabled = self.simple_perf_script is not None

        self.fast_perf_path = self.output_dir / FAST_PERF_NAME
        self.trace_perf_path = self.output_dir / TRACE_PERF_NAME
        self.simple_perf_path = self.output_dir / SIMPLE_PERF_NAME
        self.summary_yaml_path = self.output_dir / SUMMARY_YAML_NAME

        self.live_session_id = None
        self.trace_session_id = None
        self.live_report_path = None

        self.profiler_proc = None

        self.already_stopped = False
        self.lock = threading.Lock()

    def run_command_capture(self, cmd):
        print(f"\n[RUN] {' '.join(str(x) for x in cmd)}")
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
                env=self.command_env,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"command not found: {cmd[0]}; set --pico-cli to the pico-cli executable "
                "or ensure pico-cli is available on PATH"
            ) from exc
        output, _ = proc.communicate()
        print(output)
        return proc.returncode, output

    def start_live(self):
        cmd = build_pico_perf_command(self.pico_cli, "live", "start", "--app", self.app_package)
        if self.serial:
            cmd.extend(["--device", self.serial])
        code, output = self.run_command_capture(cmd)
        if code != 0:
            raise RuntimeError(f"pico-cli perf live start failed, exit code={code}")

        m = re.search(r"\[LiveStart\]\s+Started:\s+([0-9a-fA-F-]+)", output)
        if not m:
            raise RuntimeError("Cannot parse live session id")

        self.live_session_id = m.group(1)

        m2 = re.search(r"\[LiveStart\]\s+Report:\s+(.+)", output)
        if m2:
            self.live_report_path = m2.group(1).strip()

        print(f"[INFO] live session id = {self.live_session_id}")
        if self.live_report_path:
            print(f"[INFO] original live report path = {self.live_report_path}")

    def start_trace(self):
        cmd = build_pico_perf_command(
            self.pico_cli,
            "trace",
            "record",
            "--detach",
            "-o",
            str(self.trace_perf_path),
        )
        if self.serial:
            cmd.extend(["--device", self.serial])
        code, output = self.run_command_capture(cmd)
        if code != 0:
            raise RuntimeError(f"pico-cli perf trace record failed, exit code={code}")

        m = re.search(
            r"Detached recording session started:\s*([0-9a-fA-F-]+)",
            output
        )
        if m:
            self.trace_session_id = m.group(1)
            print(f"[INFO] trace session id = {self.trace_session_id}")
        else:
            print("[WARN] trace session id not found in output; stop may need manual handling")

    def start_profiler(self):
        if not self.simple_perf_enabled:
            print("[INFO] simpleperf disabled, skip app_profiler start")
            return

        cmd = [
            self.python_cmd,
            str(self.simple_perf_script),
            "-p",
            self.app_package,
            "-r",
            "--call-graph dwarf",
            "-o",
            str(self.simple_perf_path)
        ]

        print(f"\n[RUN] {' '.join(str(x) for x in cmd)}")

        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        self.profiler_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            creationflags=creationflags,
            env=self.command_env,
        )

        def pump_output():
            try:
                for line in self.profiler_proc.stdout:
                    print(f"[app_profiler] {line}", end="")
            except Exception as e:
                print(f"[WARN] profiler output reader stopped: {e}")

        t = threading.Thread(target=pump_output, daemon=True)
        t.start()

        print(f"[INFO] app_profiler pid = {self.profiler_proc.pid}")

    def stop_live(self):
        if not self.live_session_id:
            return

        cmd = build_pico_perf_command(self.pico_cli, "live", "stop", self.live_session_id)
        try:
            code, output = self.run_command_capture(cmd)
            if code != 0:
                print(f"[WARN] pico-cli perf live stop exit code={code}")
            m2 = re.search(r"\[LiveStop\]\s+Report:\s+(.+)", output)
            if m2:
                self.live_report_path = m2.group(1).strip()
        except Exception as e:
            print(f"[WARN] stop live failed: {e}")

    def stop_trace(self):
        if not self.trace_session_id:
            print("[WARN] trace session id missing, skip trace stop")
            return

        cmd = build_pico_perf_command(self.pico_cli, "trace", "stop", self.trace_session_id)
        if TRACE_STOP_PORT:
            cmd.extend(["--port", TRACE_STOP_PORT])

        try:
            code, _ = self.run_command_capture(cmd)
            if code != 0:
                print(f"[WARN] pico-cli perf trace stop exit code={code}")
        except Exception as e:
            print(f"[WARN] stop trace failed: {e}")

    def collect_live_report(self):
        if not self.live_report_path:
            print("[WARN] live report path not parsed")
            return

        candidates = []
        raw_path = Path(self.live_report_path)
        candidates.append(raw_path)
        if not raw_path.is_absolute():
            candidates.append(self.base_dir / raw_path)
            candidates.append(self.output_dir / raw_path.name)
            candidates.append(self.base_dir / "reports" / raw_path.name)
            candidates.append(self.output_dir.parent / "reports" / raw_path.name)

        src = None
        for candidate in candidates:
            if candidate.exists():
                src = candidate
                break

        if src is None:
            report_name = raw_path.name
            search_roots = [self.base_dir, self.output_dir.parent, self.output_dir]
            for root in search_roots:
                try:
                    matches = list(root.rglob(report_name))
                except Exception:
                    matches = []
                if matches:
                    src = matches[0]
                    break

        if src is None:
            print(f"[WARN] live report source not found: {self.live_report_path}")
            return

        try:
            shutil.copy2(src, self.fast_perf_path)
            if src.resolve() != self.fast_perf_path.resolve():
                src.unlink()
            parent_dir = src.parent
            if parent_dir.name.lower() == "reports":
                try:
                    parent_dir.rmdir()
                    print(f"[INFO] removed empty reports dir: {parent_dir}")
                except OSError:
                    print(f"[INFO] reports dir not empty, keep it: {parent_dir}")
            print(f"[INFO] live report copied to {self.fast_perf_path}")
        except Exception as e:
            print(f"[WARN] copy live report failed: {e}")

    def pull_simpleperf_data(self):
        cmd = [resolve_executable("adb")]
        if self.serial:
            cmd.extend(["-s", self.serial])
        cmd.extend(["pull", DEVICE_SIMPLEPERF_DATA, str(self.simple_perf_path)])
        code, _ = self.run_command_capture(cmd)
        if code != 0:
            raise RuntimeError(f"adb pull failed, exit code={code}")
        print(f"[INFO] simpleperf data pulled to {self.simple_perf_path}")

    def stop_profiler(self):
        if not self.simple_perf_enabled:
            print("[INFO] simpleperf disabled, skip app_profiler stop")
            return

        if not self.profiler_proc:
            return

        if self.profiler_proc.poll() is not None:
            print("[INFO] app_profiler already exited")
            try:
                self.pull_simpleperf_data()
            except Exception as e:
                print(f"[WARN] pull simpleperf data failed: {e}")
            return

        print("[INFO] sending Ctrl+C to app_profiler ...")

        try:
            if os.name == "nt":
                self.profiler_proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self.profiler_proc.send_signal(signal.SIGINT)

            try:
                self.profiler_proc.wait(timeout=20)
                print("[INFO] app_profiler exited gracefully")
            except subprocess.TimeoutExpired:
                print("[WARN] app_profiler did not exit after Ctrl+C in 20s")
                print("[INFO] terminating app_profiler ...")
                self.profiler_proc.terminate()
                try:
                    self.profiler_proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("[WARN] terminate timeout, killing app_profiler ...")
                    self.profiler_proc.kill()

        except Exception as e:
            print(f"[WARN] failed to stop app_profiler cleanly: {e}")

        try:
            self.pull_simpleperf_data()
        except Exception as e:
            print(f"[WARN] pull simpleperf data failed: {e}")

    def start_all(self):
        errors = []

        def wrap(name, fn):
            try:
                fn()
            except Exception as e:
                errors.append((name, e))

        threads = [
            threading.Thread(target=wrap, args=("live", self.start_live)),
            threading.Thread(target=wrap, args=("trace", self.start_trace)),
        ]
        if self.simple_perf_enabled:
            threads.append(threading.Thread(target=wrap, args=("profiler", self.start_profiler)))
        else:
            print("[INFO] simpleperf disabled, only live + trace will be collected")

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        if errors:
            for name, e in errors:
                print(f"[ERROR] start {name} failed: {e}")
            self.stop_all()
            raise RuntimeError("one or more collectors failed to start")

        print("\n[INFO] collectors started")
        print(f"[INFO] app               = {self.app_package}")
        print(f"[INFO] output dir        = {self.output_dir}")
        print(f"[INFO] live_session_id   = {self.live_session_id}")
        print(f"[INFO] trace_session_id  = {self.trace_session_id}")
        print(f"[INFO] fast perf path    = {self.fast_perf_path}")
        print(f"[INFO] trace perf path   = {self.trace_perf_path}")
        if self.simple_perf_enabled:
            print(f"[INFO] simple perf path  = {self.simple_perf_path}")
        else:
            print("[INFO] simple perf path  = <disabled>")

    def stop_all(self):
        with self.lock:
            if self.already_stopped:
                return
            self.already_stopped = True

        print("\n[INFO] stopping collectors...")
        self.stop_profiler()
        self.stop_live()
        self.stop_trace()
        self.collect_live_report()
        print("[INFO] collectors stopped")

    def verify_outputs(self):
        print("\n[INFO] verifying outputs...")

        ok = True
        warnings = []

        def check_file(label: str, path: Path, *, required: bool, min_bytes: int = 1):
            nonlocal ok
            if not path.exists():
                message = f"{label}: not found -> {path}"
                print(f"[WARN] {message}")
                warnings.append(message)
                if required:
                    ok = False
                return
            size = path.stat().st_size
            if size < min_bytes:
                message = f"{label}: too small -> {path} ({size} bytes)"
                print(f"[WARN] {message}")
                warnings.append(message)
                if required:
                    ok = False
                return
            print(f"[OK] {label}: {path} ({size} bytes)")

        check_file("fast perf", self.fast_perf_path, required=True)
        check_file("trace perf", self.trace_perf_path, required=True, min_bytes=1024 * 1024)
        if self.simple_perf_enabled:
            check_file("simple perf", self.simple_perf_path, required=True)

        if not self.simple_perf_enabled:
            print("[INFO] simple perf output check skipped because simpleperf is disabled")
            self.limitations.append("simpleperf_not_enabled")

        self.validation_warnings = warnings
        return ok

    def write_summary_yaml(self, capture_id: str, capture_time: str, duration: int, cli_version: str):
        def perf_entry(path: Path):
            if not path.exists():
                return {"path": None, "size_kb": None}
            return {"path": str(path.resolve()), "size_kb": size_in_kb(path)}

        fast_perf = perf_entry(self.fast_perf_path)
        trace_perf = perf_entry(self.trace_perf_path)
        simple_perf = perf_entry(self.simple_perf_path) if self.simple_perf_enabled else {"path": None, "size_kb": None}
        complete = bool(
            self.fast_perf_path.exists()
            and self.fast_perf_path.stat().st_size > 0
            and self.trace_perf_path.exists()
            and self.trace_perf_path.stat().st_size >= 1024 * 1024
            and (
                not self.simple_perf_enabled
                or (self.simple_perf_path.exists() and self.simple_perf_path.stat().st_size > 0)
            )
        )
        status = "complete" if complete else "partial"

        lines = [
            "collector_result:",
            "  schema_version: 1",
            f"  status: {yaml_value(status)}",
            f"  capture_id: {yaml_value(capture_id)}",
            f"  started_at: {yaml_value(capture_time)}",
            f"  package: {yaml_value(self.app_package)}",
            f"  device_serial: {yaml_value(self.serial)}",
            f"  duration_s: {yaml_value(duration)}",
            f"  output_dir: {yaml_value(str(self.output_dir.resolve()))}",
            "",
            "  artifacts:",
            "    fast_perf:",
            f"      path: {yaml_value(fast_perf['path'])}",
            f"      size_kb: {yaml_value(fast_perf['size_kb'])}",
            "      required: true",
            "    trace_perf:",
            f"      path: {yaml_value(trace_perf['path'])}",
            f"      size_kb: {yaml_value(trace_perf['size_kb'])}",
            "      required: true",
            "    simple_perf:",
            f"      path: {yaml_value(simple_perf['path'])}",
            f"      size_kb: {yaml_value(simple_perf['size_kb'])}",
            f"      required: {'true' if self.simple_perf_enabled else 'false'}",
            "",
            "  collector:",
            f"    script: {yaml_value(str(self.script_path.resolve()))}",
            f"    command: {yaml_value(format_command(self.command_line))}",
            f"    python_cmd: {yaml_value(self.python_cmd)}",
            f"    pico_cli: {yaml_value(self.pico_cli)}",
            f"    cli_version: {yaml_value(cli_version)}",
            f"    simple_perf_script: {yaml_value(str(self.simple_perf_script.resolve()) if self.simple_perf_script else None)}",
            "",
            "  warnings:",
        ]
        warnings = getattr(self, "validation_warnings", [])
        if warnings:
            lines.extend([f"    - {yaml_value(item)}" for item in warnings])
        else:
            lines[-1] = "  warnings: []"
        lines.append("  limitations:")
        if self.limitations:
            lines.extend([f"    - {yaml_value(item)}" for item in self.limitations])
        else:
            lines[-1] = "  limitations: []"

        self.summary_yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[INFO] summary yaml written to {self.summary_yaml_path}")


def make_output_dir(base_dir: Path = None) -> Path:
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    dirname = f"perf-data-{now}"
    if base_dir is None:
        output_dir = Path.cwd() / dirname
    else:
        output_dir = base_dir / dirname

    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir


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
    prefix = shlex.split(pico_cli, posix=(os.name != "nt"))
    if os.name == "nt":
        prefix = [token.strip("\"'") for token in prefix]
    if not prefix:
        raise RuntimeError("--pico-cli must not be empty")
    command = [resolve_executable(prefix[0]), *prefix[1:]]
    if "perf" not in command[1:]:
        command.append("perf")
    command.extend(str(arg) for arg in args)
    return command


def get_cli_version(pico_cli: str = "pico-cli") -> str:
    try:
        proc = subprocess.run(
            build_pico_perf_command(pico_cli, "--version"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            check=False,
        )
        output = (proc.stdout or "").strip()
        if proc.returncode == 0 and output:
            return output.splitlines()[0].strip()
    except Exception:
        pass
    return "unknown"


def size_in_kb(path: Path) -> int:
    return path.stat().st_size // 1024 if path.exists() else 0


def yaml_value(value):
    if value is None:
        return "null"
    text = str(value)
    if any(ch in text for ch in [":", "#", "\\", '"']) or not text or text != text.strip():
        return '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return text


def format_command(args: list[str]) -> str:
    return " ".join(str(arg) for arg in args)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Start and stop three performance collectors together."
    )
    parser.add_argument(
        "--app",
        required=True,
        help="Target app package name, e.g. com.example.galaxian"
    )
    parser.add_argument(
        "--serial",
        default=None,
        help="ADB/device serial confirmed by the pre-run check"
    )
    parser.add_argument(
        "--simple-perf-script",
        default=None,
        help="Optional path to app_profiler.py; if omitted or invalid, simpleperf collection is skipped"
    )
    parser.add_argument(
        "--output-root",
        default=".",
        help="Root directory for generated perf-data-xxxx folder"
    )
    parser.add_argument(
        "--python-cmd",
        default="python",
        help="Python executable used to run profiler script"
    )
    parser.add_argument(
        "--pico-cli",
        default="pico-cli",
        help=(
            "pico-cli executable or command prefix used for capture "
            "(default: pico-cli). On Windows the script resolves pico-cli.cmd "
            "from PATH automatically."
        ),
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Auto-stop after N seconds; unit is seconds. If omitted, stop manually with Ctrl+C or SIGTERM"
    )
    return parser.parse_args()


def print_result(output_dir, ok):
    print("\n[RESULT]")
    print(f"[RESULT] output directory: {output_dir}")
    print(f"[RESULT] summary yaml    : {output_dir / SUMMARY_YAML_NAME}")
    if ok:
        print("The acquisition processes have been completed and the results have been saved to separate directories.")
    else:
        print("The collection has ended, but some output has not been detected. Please check the console log.")


def finalize_capture(mgr: CollectorManager, output_dir: Path, capture_id: str, capture_time: str, duration: int, cli_version: str):
    ok = mgr.verify_outputs()
    mgr.write_summary_yaml(capture_id=capture_id, capture_time=capture_time, duration=duration, cli_version=cli_version)
    print_result(output_dir, ok)
    return ok


def main():
    args = parse_args()

    output_root = Path(args.output_root).resolve()
    output_dir = make_output_dir(output_root)

    print(f"[INFO] created output directory: {output_dir}")

    simple_perf_script = None
    if args.simple_perf_script:
        candidate = Path(args.simple_perf_script).expanduser().resolve()
        if candidate.exists() and candidate.is_file():
            simple_perf_script = candidate
            print(f"[INFO] simpleperf script enabled: {simple_perf_script}")
        else:
            print(f"[WARN] invalid --simple-perf-script, simpleperf will be skipped: {candidate}")
    else:
        print("[INFO] --simple-perf-script not provided, simpleperf will be skipped")

    capture_started_at = datetime.now()
    capture_start_ts = time.time()
    capture_time = capture_started_at.strftime("%Y%m%d-%H%M%S")
    capture_id = f"spf-{uuid.uuid4().hex}"
    cli_version = get_cli_version(args.pico_cli)
    limitations = []
    if args.duration is None:
        limitations.append("duration_not_fixed")
    elif args.duration < 30:
        limitations.append("duration_less_than_30s")

    mgr = CollectorManager(
        app_package=args.app,
        output_dir=output_dir,
        simple_perf_script=simple_perf_script,
        python_cmd=args.python_cmd,
        pico_cli=args.pico_cli,
        serial=args.serial,
        script_path=Path(__file__).resolve(),
        command_line=sys.argv,
        limitations=limitations,
    )

    def current_duration() -> int:
        if args.duration is not None:
            return int(args.duration)
        return max(0, int(time.time() - capture_start_ts))

    def finish_and_exit(exit_code: int):
        duration = current_duration()
        ok = finalize_capture(
            mgr=mgr,
            output_dir=output_dir,
            capture_id=capture_id,
            capture_time=capture_time,
            duration=duration,
            cli_version=cli_version,
        )
        if exit_code == 0 and not ok:
            exit_code = 2
        sys.exit(exit_code)

    def handle_sigterm(signum, frame):
        print(f"\n[INFO] received signal {signum}, stopping...")
        mgr.stop_all()
        finish_and_exit(0)

    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        mgr.start_all()
        print("\n[INFO] Capturing...")
        if args.duration is not None:
            print(f"[INFO] Stop after {args.duration} seconds")
            start_time = time.time()
            while True:
                time.sleep(1)
                if time.time() - start_time >= args.duration:
                    print(f"\n[INFO] duration {args.duration} seconds reached, stopping...")
                    mgr.stop_all()
                    finish_and_exit(0)
        else:
            print("[INFO] Press Ctrl+C or send SIGTERM signal to stop.")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] keyboard interrupt received")
        mgr.stop_all()
        finish_and_exit(0)
    except Exception as e:
        print(f"[FATAL] {e}")
        mgr.stop_all()
        finish_and_exit(1)


if __name__ == "__main__":
    main()
