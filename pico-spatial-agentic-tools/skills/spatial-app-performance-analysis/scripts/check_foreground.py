#!/usr/bin/env python3

# usage: check_foreground.py [-h] -s SN [--app APP_ID] [--json] [--detail]
#   the following arguments are required: -s/--sn
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional


PKG_ACTIVITY_RE = re.compile(r"([A-Za-z0-9_.$]+)/(?:[A-Za-z0-9_.$]+)")
PKG_ONLY_RE = re.compile(r"\b([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+)\b")


def resolve_executable(executable: str) -> str:
    resolved = shutil.which(executable)
    if resolved:
        return resolved
    if sys.platform.startswith("win") and not Path(executable).suffix:
        for suffix in (".exe", ".cmd", ".bat"):
            resolved = shutil.which(executable + suffix)
            if resolved:
                return resolved
    return executable


def run_adb_to_file(sn: str, args: List[str]) -> str:
    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    err_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")

    out_path = out_file.name
    err_path = err_file.name
    out_file.close()
    err_file.close()

    cmd = [resolve_executable("adb"), "-s", sn, "shell", *args]

    try:
        with open(out_path, "wb") as fout, open(err_path, "wb") as ferr:
            proc = subprocess.Popen(
                cmd,
                stdout=fout,
                stderr=ferr,
                stdin=subprocess.DEVNULL,
                shell=False,
            )
            proc.wait()

        with open(out_path, "r", encoding="utf-8", errors="ignore") as f:
            stdout = f.read()

        with open(err_path, "r", encoding="utf-8", errors="ignore") as f:
            stderr = f.read()

        if proc.returncode != 0:
            raise RuntimeError(stderr.strip() or stdout.strip() or f"adb command failed: {' '.join(cmd)}")

        return stdout

    finally:
        for p in (out_path, err_path):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass


def extract_pkg_from_line(line: str) -> Optional[str]:
    m = PKG_ACTIVITY_RE.search(line)
    if m:
        return m.group(1)

    candidates = PKG_ONLY_RE.findall(line)
    blacklist_prefixes = (
        "u0", "t", "Window", "ActivityRecord", "Task", "RootTask", "Display", "Stack"
    )
    for c in candidates:
        if c.startswith(blacklist_prefixes):
            continue
        if c in {"android", "system", "null"}:
            continue
        return c
    return None


def unique_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def get_foreground_apps(sn: str) -> List[str]:
    commands = [
        ["dumpsys", "activity", "activities"],
        ["dumpsys", "activity"],
        ["dumpsys", "window"],
    ]

    keys = (
        "mResumedActivity",
        "topResumedActivity",
        "mFocusedApp",
        "mCurrentFocus",
        "ResumedActivity",
    )

    packages: List[str] = []

    for cmd in commands:
        try:
            output = run_adb_to_file(sn, cmd)
        except Exception:
            continue

        if not output:
            continue

        for line in output.splitlines():
            if any(k in line for k in keys):
                pkg = extract_pkg_from_line(line)
                if pkg:
                    packages.append(pkg)

    return unique_keep_order(packages)


def print_unix(result: Dict[str, Any], detail: bool) -> None:
    packages = result.get("foreground_apps", [])

    if detail:
        print(f"serial={result['serial']}")
        print(f"count={result.get('count', len(packages))}")
        if "app_id" in result:
            print(f"app_id={result['app_id']}")
            print(f"is_foreground={'true' if result.get('is_foreground') else 'false'}")
        print("apps:")
        for pkg in packages:
            print(pkg)
        if not packages:
            print("<none>")
        return

    if "app_id" in result:
        print("true" if result.get("is_foreground") else "false")
        return

    for pkg in packages:
        print(pkg)


def print_unix_error(serial: str, message: str, detail: bool) -> None:
    if detail:
        print(f"serial={serial}", file=sys.stderr)
        print("status=error", file=sys.stderr)
        print(f"message={message}", file=sys.stderr)
    else:
        print(message, file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query Android foreground apps via adb by device serial number"
    )
    parser.add_argument("-s", "--sn", "--serial", dest="sn", required=True, help="ADB device serial number")
    parser.add_argument("--app", "--package", dest="app", help="Package name to check, e.g. com.example.app")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--detail", action="store_true", help="Print detailed output")
    args = parser.parse_args()

    try:
        packages = get_foreground_apps(args.sn)
    except Exception as e:
        if args.json:
            print(json.dumps({
                "ok": False,
                "serial": args.sn,
                "error": str(e),
            }, ensure_ascii=False, indent=2))
        else:
            print_unix_error(args.sn, str(e), args.detail)
        return 1

    result: Dict[str, Any] = {
        "ok": True,
        "serial": args.sn,
        "foreground_apps": packages,
        "count": len(packages),
    }

    if args.app:
        result["app_id"] = args.app
        result["is_foreground"] = args.app in packages

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_unix(result, args.detail)

    return 0


if __name__ == "__main__":
    sys.exit(main())
