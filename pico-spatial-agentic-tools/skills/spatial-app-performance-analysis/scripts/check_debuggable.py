#!/usr/bin/env python3

# usage: check_debuggable.py [-h] -s SN --app APP [--json] [--detail]
#   the following arguments are required: -s/--sn
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any


EXIT_OK = 0
EXIT_UNKNOWN = 2


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


def print_human(result: Dict[str, Any], detail: bool = False) -> None:
    status = result["status"]
    if not detail:
        print(status)
        return

    serial = result["serial"]
    package = result["package"]
    dumpsys_result = result["checks"]["dumpsys"]
    run_as_result = result["checks"]["run_as"]

    print(status)
    print(f"  device:   {serial}")
    print(f"  package:  {package}")

    if result["reasons"]:
        print("  signals:")
        for reason in result["reasons"]:
            print(f"    - {reason}")

    print("  checks:")
    print(f"    dumpsys : {dumpsys_result['summary']}")
    if dumpsys_result.get("stderr"):
        print(f"    dumpsys!: {dumpsys_result['stderr']}")
    print(f"    run-as  : {run_as_result['summary']}")
    raw = run_as_result.get("raw")
    if raw:
        print(f"    run-as> : {raw}")


def run_cmd(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr


def adb_base(sn: str):
    adb = resolve_executable("adb")
    return [adb, "-s", sn] if sn else [adb]


def check_dumpsys(sn: str, package: str) -> Dict[str, Any]:
    cmd = adb_base(sn) + ["shell", "dumpsys", "package", package]
    code, out, err = run_cmd(cmd)
    text = (out or "") + "\n" + (err or "")
    debuggable = bool(re.search(r"\bDEBUGGABLE\b", text, re.IGNORECASE))
    package_found = not re.search(r"(Unable to find package|Unknown package|not found)", text, re.IGNORECASE)
    return {
        "ok": code == 0 and package_found,
        "returncode": code,
        "debuggable": debuggable,
        "package_found": package_found,
        "summary": "found DEBUGGABLE in dumpsys output" if debuggable else "DEBUGGABLE not found in dumpsys output",
        "stderr": err.strip(),
    }


def check_run_as(sn: str, package: str) -> Dict[str, Any]:
    cmd = adb_base(sn) + ["shell", "run-as", package, "id"]
    code, out, err = run_cmd(cmd)
    text = ((out or "") + "\n" + (err or "")).strip()

    if code == 0:
        return {
            "ok": True,
            "returncode": code,
            "debuggable": True,
            "summary": "run-as succeeded",
            "raw": text,
        }

    lowered = text.lower()
    if "package not debuggable" in lowered:
        return {
            "ok": True,
            "returncode": code,
            "debuggable": False,
            "summary": "run-as reports package not debuggable",
            "raw": text,
        }
    if "unknown package" in lowered or "is unknown" in lowered:
        return {
            "ok": False,
            "returncode": code,
            "debuggable": None,
            "summary": "package not found",
            "raw": text,
        }

    return {
        "ok": False,
        "returncode": code,
        "debuggable": None,
        "summary": "run-as returned an unexpected result",
        "raw": text,
    }


def decide(dumpsys_result: Dict[str, Any], run_as_result: Dict[str, Any]) -> Dict[str, Any]:
    reasons = []
    if dumpsys_result.get("debuggable") is True:
        reasons.append("dumpsys contains DEBUGGABLE")
    elif dumpsys_result.get("ok"):
        reasons.append("dumpsys does not contain DEBUGGABLE")

    if run_as_result.get("debuggable") is True:
        reasons.append("run-as succeeded")
    elif run_as_result.get("debuggable") is False:
        reasons.append("run-as says package not debuggable")

    if dumpsys_result.get("debuggable") is True or run_as_result.get("debuggable") is True:
        status = "DEBUGGABLE"
    elif dumpsys_result.get("debuggable") is False and run_as_result.get("debuggable") is False:
        status = "NOT_DEBUGGABLE"
    else:
        status = "UNKNOWN"

    return {"status": status, "reasons": reasons}


def main():
    parser = argparse.ArgumentParser(description="Check whether an installed Android app is debuggable via adb")
    parser.add_argument("-s", "--sn", "--serial", dest="sn", required=True, help="adb device serial number")
    parser.add_argument("--app", "--package", dest="app", required=True, help="Android package name")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--detail", action="store_true", help="print detailed human-readable output")
    args = parser.parse_args()

    dumpsys_result = check_dumpsys(args.sn, args.app)
    run_as_result = check_run_as(args.sn, args.app)
    decision = decide(dumpsys_result, run_as_result)

    result = {
        "serial": args.sn,
        "package": args.app,
        "status": decision["status"],
        "reasons": decision["reasons"],
        "checks": {
            "dumpsys": dumpsys_result,
            "run_as": run_as_result,
        },
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print_human(result, detail=args.detail)

    if result["status"] in {"DEBUGGABLE", "NOT_DEBUGGABLE"}:
        sys.exit(EXIT_OK)
    sys.exit(EXIT_UNKNOWN)


if __name__ == "__main__":
    main()
