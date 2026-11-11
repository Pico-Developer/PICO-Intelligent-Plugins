#!/usr/bin/env python3
# Usage examples:
#   python check_device.py
#   python check_device.py --detail
#   python check_device.py --json
#   python check_device.py -s <adb_serial> --detail
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class Signal:
    name: str
    value: str
    verdict: str
    score: float
    reason: str


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


def adb_command(*args: str) -> List[str]:
    return [resolve_executable("adb"), *args]


def run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def adb_shell_getprop(serial: Optional[str], key: str) -> str:
    cmd = adb_command()
    if serial:
        cmd += ["-s", serial]
    cmd += ["shell", "getprop", key]
    code, out, err = run_cmd(cmd)
    if code != 0:
        raise RuntimeError(f"getprop {key} failed: {err or out}")
    return out.strip()


def adb_shell_getprop_optional(serial: Optional[str], key: str) -> str:
    try:
        return adb_shell_getprop(serial, key)
    except Exception:
        return ""


def adb_devices() -> List[str]:
    code, out, err = run_cmd(adb_command("devices"))
    if code != 0:
        raise RuntimeError(err or out or "adb devices failed")
    serials = []
    for line in out.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            serials.append(parts[0])
    return serials


def parse_ota_version(value: str) -> Optional[Tuple[int, int, int]]:
    """Parse ro.pico.ota.version values like 6.1.0-20260724-RELEASE."""
    if not value:
        return None
    match = re.match(r"^\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?", value)
    if not match:
        return None
    major = int(match.group(1))
    minor = int(match.group(2) or 0)
    patch = int(match.group(3) or 0)
    return major, minor, patch


def classify_pico_os_from_ota(value: str) -> Dict[str, object]:
    parsed = parse_ota_version(value)
    if parsed is None:
        return {
            "status": "UNKNOWN",
            "ota_version": value,
            "parsed_version": None,
            "reason": "ro.pico.ota.version is missing or cannot be parsed",
        }
    major, minor, patch = parsed
    return {
        "status": "PICO_OS6" if major >= 6 else "NOT_PICO_OS6",
        "ota_version": value,
        "parsed_version": f"{major}.{minor}.{patch}",
        "reason": "ro.pico.ota.version major version is >= 6"
        if major >= 6
        else "ro.pico.ota.version major version is < 6",
    }


def classify_signal(name: str, value: str) -> Signal:
    v = (value or "").strip()
    low = v.lower()

    if name == "ro.boot.qemu":
        if low == "1":
            return Signal(name, v, "emulator", 1.00, "ro.boot.qemu is 1")
        if low == "0":
            return Signal(name, v, "swan", 1.00, "ro.boot.qemu is 0")
        if low == "":
            return Signal(name, "<empty>", "unknown", 0.0, "ro.boot.qemu is absent")
        return Signal(name, v or "<empty>", "unknown", 0.0, "ro.boot.qemu must be 0 or 1")

    if name == "ro.kernel.qemu":
        if low == "1":
            return Signal(name, v, "emulator", 1.00, "ro.kernel.qemu is 1")
        if low in ("", "0"):
            return Signal(name, v or "<empty>", "swan", 1.00, "ro.kernel.qemu is 0 or absent")
        return Signal(name, v or "<empty>", "unknown", 0.0, "ro.kernel.qemu must be 0 or 1")

    return Signal(name, v, "unknown", 0.0, "No rule matched")


def summarize(signals: List[Signal]) -> Dict[str, object]:
    emu_scores = [s.score for s in signals if s.verdict == "emulator"]
    swan_scores = [s.score for s in signals if s.verdict == "swan"]

    emu_total = sum(emu_scores)
    swan_total = sum(swan_scores)
    total = emu_total + swan_total
    max_possible_total = len(signals) * 1.0

    emu_score_normalized = emu_total / max_possible_total if max_possible_total else 0.0
    swan_score_normalized = swan_total / max_possible_total if max_possible_total else 0.0

    if total == 0:
        final = "unknown"
        confidence = 0.0
    elif emu_total > swan_total:
        final = "emulator"
        confidence = emu_total / total
    else:
        final = "swan"
        confidence = swan_total / total

    return {
        "final_verdict": final,
        "confidence": round(confidence, 4),
        "emulator_score_sum": round(emu_total, 4),
        "swan_score_sum": round(swan_total, 4),
        "emulator_score_normalized": round(emu_score_normalized, 4),
        "swan_score_normalized": round(swan_score_normalized, 4),
        "max_possible_score_sum": round(max_possible_total, 4),
    }


def detect_pico(props: Dict[str, str]) -> Dict[str, object]:
    brand = (props.get("ro.product.brand") or "").strip().lower()
    manufacturer = (props.get("ro.product.manufacturer") or "").strip().lower()
    device = (props.get("ro.product.device") or "").strip().lower()
    os_info = classify_pico_os_from_ota(props.get("ro.pico.ota.version", ""))
    brand_ok = brand == "pico" or manufacturer == "pico"
    swan_ok = device == "swan"
    return {
        "is_pico_swan": brand_ok and swan_ok,
        "brand_ok": brand_ok,
        "product_device_is_swan": swan_ok,
        "os": os_info,
    }


def require_swan_identity(summary: Dict[str, object], props: Dict[str, str]) -> None:
    if summary["final_verdict"] == "swan" and not detect_pico(props)["is_pico_swan"]:
        summary["final_verdict"] = "unknown"
        summary["confidence"] = 0.0


def print_cli_output(signals: List[Signal], summary: Dict[str, object], serial: str, props: Dict[str, str]) -> None:
    name_w = max(len("DIMENSION"), max(len(s.name) for s in signals))
    value_w = max(len("VALUE"), min(50, max(len(s.value if s.value else "<empty>") for s in signals)))
    verdict_w = max(len("VERDICT"), max(len(s.verdict) for s in signals))
    score_w = len("SCORE")

    title = "ADB Device Classification"
    sep = "=" * len(title)
    print(sep)
    print(title)
    print(sep)
    print(f"Serial      : {serial}")
    print(f"Final       : {summary['final_verdict']}")
    print(f"Confidence  : {summary['confidence']:.2%}")
    print(f"PICO OS     : {classify_pico_os_from_ota(props.get('ro.pico.ota.version', ''))['status']}")
    print("")

    header = (
        f"{'DIMENSION':<{name_w}}  "
        f"{'VALUE':<{value_w}}  "
        f"{'VERDICT':<{verdict_w}}  "
        f"{'SCORE':>{score_w}}  "
        f"REASON"
    )
    print(header)
    print("-" * len(header))

    for s in signals:
        value = s.value if s.value else "<empty>"
        if len(value) > value_w:
            value = value[: value_w - 3] + "..."
        print(
            f"{s.name:<{name_w}}  "
            f"{value:<{value_w}}  "
            f"{s.verdict:<{verdict_w}}  "
            f"{s.score:>{score_w}.2f}  "
            f"{s.reason}"
        )

    print("")
    print("Summary")
    print("-------")
    print(f"Emulator score sum        : {summary['emulator_score_sum']:.2f}")
    print(f"Swan score sum            : {summary['swan_score_sum']:.2f}")
    print(f"Emulator normalized score : {summary['emulator_score_normalized']:.2%}")
    print(f"Swan normalized score     : {summary['swan_score_normalized']:.2%}")
    print(f"Max possible score sum    : {summary['max_possible_score_sum']:.2f}")
    print("Rule                      : ro.boot.qemu, then ro.kernel.qemu when boot is absent")


def print_simple_output(summary: Dict[str, object], serial: str, props: Dict[str, str]) -> None:
    pico = detect_pico(props)
    print(f"device={summary['final_verdict']} | confidence={summary['confidence']:.2%}")
    print(f"serial={serial}")
    print(f"is_pico_swan={'true' if pico['is_pico_swan'] else 'false'}")
    print(f"pico_os={pico['os']['status']}")


def print_json(signals: List[Signal], summary: Dict[str, object], serial: str, props: Dict[str, str]) -> None:
    pico = detect_pico(props)
    data = {
        "serial": serial,
        "device_info": {
            "ro.boot.qemu": props.get("ro.boot.qemu", ""),
            "ro.kernel.qemu": props.get("ro.kernel.qemu", ""),
            "ro.product.brand": props.get("ro.product.brand", ""),
            "ro.product.manufacturer": props.get("ro.product.manufacturer", ""),
            "ro.product.device": props.get("ro.product.device", ""),
            "ro.pico.ota.version": props.get("ro.pico.ota.version", ""),
        },
        "is_pico_swan": pico["is_pico_swan"],
        "pico_os": pico["os"]["status"],
        "pico": pico,
        "summary": summary,
        "signals": [s.__dict__ for s in signals],
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify a PICO target as emulator or Swan via adb")
    parser.add_argument("-s", "--serial", "--sn", dest="serial", help="Device serial; if omitted, auto-select the only online device")
    parser.add_argument("--json", action="store_true", help="Output result in JSON format")
    parser.add_argument("--detail", action="store_true", help="Output detailed analysis")
    args = parser.parse_args()

    serial = args.serial
    if not serial:
        serials = adb_devices()
        if not serials:
            print("No online adb device detected.", file=sys.stderr)
            return 2
        if len(serials) > 1:
            print("Multiple devices detected. Please use -s to specify a serial:", file=sys.stderr)
            for s in serials:
                print(f"- {s}", file=sys.stderr)
            return 2
        serial = serials[0]

    props = {
        "ro.boot.qemu": adb_shell_getprop(serial, "ro.boot.qemu"),
        "ro.product.brand": adb_shell_getprop_optional(serial, "ro.product.brand"),
        "ro.product.manufacturer": adb_shell_getprop_optional(serial, "ro.product.manufacturer"),
        "ro.product.device": adb_shell_getprop_optional(serial, "ro.product.device"),
        "ro.pico.ota.version": adb_shell_getprop_optional(serial, "ro.pico.ota.version"),
    }
    if not props["ro.boot.qemu"]:
        props["ro.kernel.qemu"] = adb_shell_getprop(serial, "ro.kernel.qemu")

    order = ["ro.boot.qemu"] if props["ro.boot.qemu"] else ["ro.kernel.qemu"]
    signals = [classify_signal(k, props.get(k, "")) for k in order]
    summary = summarize(signals)
    require_swan_identity(summary, props)

    if args.json:
        print_json(signals, summary, serial, props)
    elif args.detail:
        print_cli_output(signals, summary, serial, props)
    else:
        print_simple_output(summary, serial, props)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as e:
        print(f"Execution failed: {e}", file=sys.stderr)
        raise SystemExit(1)
