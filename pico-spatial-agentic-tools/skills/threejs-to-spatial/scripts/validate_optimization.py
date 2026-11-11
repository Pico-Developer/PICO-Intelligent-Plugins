"""Validate a lossless-optimization report before verification."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_TARGET_KEYS = ("device", "rom", "sdk_version", "container", "build_sha256")
CONTAINERS = frozenset({"planar", "volumetric", "stage"})
REQUIRED_BUDGET_KEYS = (
    "frame_time_ms_p95",
    "draw_calls_max",
    "texture_mesh_memory_mb",
    "startup_ms",
)
OPTIONAL_BUDGET_KEYS = ("stutter_frame_ratio", "shadergraph_warmup_ms")
MEASUREMENT_EVIDENCE_KEYS = ("evidence",)
OPTIMIZATION_EVIDENCE_KEYS = ("before_evidence", "after_evidence", "visual_parity")
STATUSES = frozenset({"passed", "needs_degradation_approval", "incomplete"})


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(non_empty_string(item) for item in value)
    )


def evidence_exists(base: Path, value: Any) -> bool:
    if not non_empty_string(value):
        return False
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.is_file()
    return (base / candidate).is_file()


def validate_target(report: dict) -> list[str]:
    errors: list[str] = []
    target = report.get("target")
    if not isinstance(target, dict):
        return ["optimization-report.target must be an object"]
    for key in REQUIRED_TARGET_KEYS:
        if not non_empty_string(target.get(key)):
            errors.append(f"optimization-report.target.{key} must be a non-empty string")
    container = target.get("container")
    if non_empty_string(container) and container not in CONTAINERS:
        errors.append("optimization-report.target.container must be planar, volumetric, or stage")
    return errors


def validate_budget(report: dict) -> list[str]:
    errors: list[str] = []
    budget = report.get("budget")
    if not isinstance(budget, dict):
        return ["optimization-report.budget must be an object"]
    for key in REQUIRED_BUDGET_KEYS:
        if not is_number(budget.get(key)) or budget[key] <= 0:
            errors.append(f"optimization-report.budget.{key} must be positive")
    for key in OPTIONAL_BUDGET_KEYS:
        if key in budget and (not is_number(budget[key]) or budget[key] <= 0):
            errors.append(f"optimization-report.budget.{key} must be positive when declared")
    return errors


def validate_coverage(report: dict) -> list[str]:
    errors: list[str] = []
    coverage = report.get("coverage")
    if not isinstance(coverage, dict):
        return ["optimization-report.coverage must be an object"]
    for key in ("pages", "states"):
        if not non_empty_string_list(coverage.get(key)):
            errors.append(
                f"optimization-report.coverage.{key} must be a non-empty string array"
            )
    return errors


def validate_measurements(report: dict, base: Path) -> list[str]:
    errors: list[str] = []
    measurements = report.get("measurements")
    if not isinstance(measurements, list) or not measurements:
        return ["optimization-report.measurements must be a non-empty array"]
    seen: set[str] = set()
    for index, item in enumerate(measurements):
        prefix = f"measurements[{index}]"
        if not isinstance(item, dict):
            errors.append(f"optimization-report.{prefix} must be an object")
            continue
        item_id = item.get("id")
        if not non_empty_string(item_id):
            errors.append(f"optimization-report.{prefix}.id must be a non-empty string")
        elif item_id in seen:
            errors.append(f"optimization-report.{prefix}.id is duplicated: {item_id}")
        else:
            seen.add(item_id)
        if not non_empty_string(item.get("metric")):
            errors.append(f"optimization-report.{prefix}.metric must be a non-empty string")
        if not is_number(item.get("budget")) or item["budget"] <= 0:
            errors.append(f"optimization-report.{prefix}.budget must be positive")
        if not is_number(item.get("value")) or item["value"] < 0:
            errors.append(
                f"optimization-report.{prefix}.value must be a non-negative number"
            )
        if not non_empty_string(item.get("unit")):
            errors.append(f"optimization-report.{prefix}.unit must be a non-empty string")
        if not non_empty_string(item.get("method")):
            errors.append(f"optimization-report.{prefix}.method must be a non-empty string")
        if not isinstance(item.get("passed"), bool):
            errors.append(f"optimization-report.{prefix}.passed must be a boolean")
        elif is_number(item.get("value")) and is_number(item.get("budget")):
            expected = item["value"] <= item["budget"]
            if item["passed"] != expected:
                errors.append(
                    f"optimization-report.{prefix}.passed must equal value <= budget"
                )
        for key in MEASUREMENT_EVIDENCE_KEYS:
            if not evidence_exists(base, item.get(key)):
                errors.append(
                    f"optimization-report.{prefix}.{key} must reference an existing file"
                )
    return errors


def validate_optimizations(
    report: dict, base: Path, capability_ids: set[str] | None
) -> list[str]:
    errors: list[str] = []
    optimizations = report.get("optimizations")
    if not isinstance(optimizations, list):
        return ["optimization-report.optimizations must be an array"]
    seen: set[str] = set()
    for index, item in enumerate(optimizations):
        prefix = f"optimizations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"optimization-report.{prefix} must be an object")
            continue
        item_id = item.get("id")
        if not non_empty_string(item_id):
            errors.append(f"optimization-report.{prefix}.id must be a non-empty string")
        elif item_id in seen:
            errors.append(f"optimization-report.{prefix}.id is duplicated: {item_id}")
        else:
            seen.add(item_id)
        capabilities = item.get("capabilities")
        if not non_empty_string_list(capabilities):
            errors.append(
                f"optimization-report.{prefix}.capabilities must be a non-empty string array"
            )
        elif capability_ids is not None:
            unknown = sorted(set(capabilities) - capability_ids)
            if unknown:
                errors.append(
                    f"optimization-report.{prefix}.capabilities are not in inventory: "
                    + ", ".join(unknown)
                )
        if not non_empty_string(item.get("action")):
            errors.append(f"optimization-report.{prefix}.action must be a non-empty string")
        if item.get("behavior_preserved") is not True:
            errors.append(
                f"optimization-report.{prefix}.behavior_preserved must be true; "
                "a behavior change is a degradation, not an optimization"
            )
        if not non_empty_string(item.get("measured_gain")):
            errors.append(
                f"optimization-report.{prefix}.measured_gain must be a non-empty string"
            )
        for key in OPTIMIZATION_EVIDENCE_KEYS:
            if not evidence_exists(base, item.get(key)):
                errors.append(
                    f"optimization-report.{prefix}.{key} must reference an existing file"
                )
    return errors


def validate_report(report_path: Path, inventory_path: Path | None) -> list[str]:
    try:
        report = load_json(report_path)
        inventory = load_json(inventory_path) if inventory_path else None
    except ValueError as exc:
        return [str(exc)]

    capability_ids: set[str] | None = None
    if inventory is not None:
        if not isinstance(inventory, dict) or not isinstance(
            inventory.get("capabilities"), list
        ):
            return ["inventory.capabilities must be an array"]
        capability_ids = {
            item.get("id")
            for item in inventory["capabilities"]
            if isinstance(item, dict) and non_empty_string(item.get("id"))
        }

    errors: list[str] = []
    if not isinstance(report, dict):
        return ["optimization report root must be an object"]
    if report.get("schema_version") != 1:
        errors.append("optimization-report.schema_version must be 1")
    errors.extend(validate_target(report))
    errors.extend(validate_budget(report))
    errors.extend(validate_coverage(report))
    errors.extend(validate_measurements(report, report_path.parent))
    errors.extend(validate_optimizations(report, report_path.parent, capability_ids))

    status = report.get("status")
    if status not in STATUSES:
        errors.append(
            "optimization-report.status must be passed, needs_degradation_approval, or incomplete"
        )
    measurements = report.get("measurements")
    if isinstance(measurements, list):
        failing = [
            item
            for item in measurements
            if isinstance(item, dict) and item.get("passed") is False
        ]
        if failing and status == "passed":
            errors.append(
                "optimization-report.status cannot be passed while a measurement fails"
            )
    if status == "passed":
        residual = report.get("residual_risks", [])
        if not isinstance(residual, list):
            errors.append("optimization-report.residual_risks must be an array")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Three.js to Spatial SDK lossless-optimization report."
    )
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--inventory", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors = validate_report(args.report, args.inventory)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    report = load_json(args.report)
    print(
        json.dumps(
            {
                "valid": True,
                "status": report["status"],
                "measurement_count": len(report["measurements"]),
                "optimization_count": len(report["optimizations"]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
