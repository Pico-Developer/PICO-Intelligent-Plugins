#!/usr/bin/env python3
"""Validate a capability mapping and calculate the migration admission score.

Exit codes:
  0 - artifacts are valid and the project is fully admitted or user-approved
  1 - artifact validation failed
  3 - artifacts are valid but the project is rejected
  4 - artifacts are valid but explicit degradation approval is required
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


WEIGHTS = {
    "visual_core": 3.0,
    "interaction_core": 3.0,
    "runtime": 2.0,
    "infrastructure": 0.0,
}
COEFFICIENTS = {
    "direct": 1.0,
    "rebuild": 1.0,
    "approximate": 0.55,
    "drop": 0.0,
    "block": 0.0,
}
CORE = frozenset({"visual_core", "interaction_core"})
OWNERSHIPS = frozenset({"kotlin_code", "source_asset", "editor_authored", "dropped"})
DEGRADATION_OUTCOMES = frozenset(
    {"api_unavailable", "semantic_mismatch", "runtime_failed", "performance_failed"}
)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def mapping_errors(inventory: Any, report: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(inventory, dict) or not isinstance(
        inventory.get("capabilities"), list
    ):
        return ["inventory.capabilities must be an array"]
    if not isinstance(report, dict):
        return ["mapping report root must be an object"]
    if report.get("schema_version") != 1:
        errors.append("mapping-report.schema_version must be 1")
    sdk_version = report.get("sdk_version")
    if not isinstance(sdk_version, str) or not sdk_version.strip():
        errors.append("mapping-report.sdk_version must be a non-empty string")

    inventory_by_id = {
        item.get("id"): item
        for item in inventory["capabilities"]
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    inventory_ids = list(inventory_by_id)
    mappings = report.get("mappings")
    if not isinstance(mappings, list):
        return errors + ["mapping-report.mappings must be an array"]

    seen: set[str] = set()
    for index, item in enumerate(mappings):
        prefix = f"mappings[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        capability_id = item.get("capability_id")
        if capability_id in seen:
            errors.append(f"{prefix}.capability_id is duplicated: {capability_id}")
        seen.add(capability_id)
        level = item.get("mapping_level")
        if level not in COEFFICIENTS:
            errors.append(f"{prefix}.mapping_level is invalid: {level!r}")
            continue
        ownership = item.get("target_ownership")
        if ownership not in OWNERSHIPS:
            errors.append(f"{prefix}.target_ownership is invalid: {ownership!r}")
        expected_ownerships = (
            frozenset({"dropped"})
            if level in {"drop", "block"}
            else frozenset({"source_asset"})
            if isinstance(capability_id, str) and capability_id.startswith("asset.")
            else frozenset({"kotlin_code", "editor_authored"})
            if isinstance(capability_id, str) and capability_id.startswith("material.")
            else frozenset({"kotlin_code"})
        )
        if ownership not in expected_ownerships:
            errors.append(
                f"{prefix}.target_ownership must be one of "
                f"{', '.join(sorted(expected_ownerships))} for "
                f"{capability_id} mapped as {level}"
            )
        if not isinstance(item.get("conversion_rule"), str) or not item[
            "conversion_rule"
        ].strip():
            errors.append(f"{prefix}.conversion_rule must be a non-empty string")
        if not isinstance(item.get("quality_loss"), list):
            errors.append(f"{prefix}.quality_loss must be an array")
        if not non_empty_list(item.get("validation")):
            errors.append(f"{prefix}.validation must be a non-empty array")
        if level in {"direct", "rebuild", "approximate"}:
            if not non_empty_list(item.get("spatial_primitive")):
                errors.append(
                    f"{prefix}.spatial_primitive is required for {level}"
                )
            evidence = item.get("version_evidence")
            if not non_empty_list(evidence):
                errors.append(f"{prefix}.version_evidence is required for {level}")
            else:
                for evidence_index, record in enumerate(evidence):
                    if not isinstance(record, dict):
                        errors.append(
                            f"{prefix}.version_evidence[{evidence_index}] must be an object"
                        )
                        continue
                    if record.get("sdk_version") != sdk_version:
                        errors.append(
                            f"{prefix}.version_evidence[{evidence_index}].sdk_version "
                            "must match mapping-report.sdk_version"
                        )
                    for key in ("source", "symbol"):
                        if not isinstance(record.get(key), str) or not record[key].strip():
                            errors.append(
                                f"{prefix}.version_evidence[{evidence_index}].{key} "
                                "must be a non-empty string"
                            )
        if level in {"approximate", "drop", "block"} and not non_empty_list(
            item.get("quality_loss")
        ):
            errors.append(f"{prefix}.quality_loss is required for {level}")
        criticality = inventory_by_id.get(capability_id, {}).get("criticality")
        requires_degradation_evidence = level == "block" or (
            level in {"approximate", "drop"} and criticality != "infrastructure"
        )
        if requires_degradation_evidence:
            if not non_empty_string(item.get("degradation_reason")):
                errors.append(f"{prefix}.degradation_reason is required for {level}")
            attempts = item.get("native_attempts")
            if not non_empty_list(attempts):
                errors.append(f"{prefix}.native_attempts is required for {level}")
            else:
                for attempt_index, attempt in enumerate(attempts):
                    attempt_prefix = f"{prefix}.native_attempts[{attempt_index}]"
                    if not isinstance(attempt, dict):
                        errors.append(f"{attempt_prefix} must be an object")
                        continue
                    for key in ("approach", "evidence", "limitation"):
                        if not non_empty_string(attempt.get(key)):
                            errors.append(
                                f"{attempt_prefix}.{key} must be a non-empty string"
                            )
                    if attempt.get("outcome") not in DEGRADATION_OUTCOMES:
                        errors.append(f"{attempt_prefix}.outcome is invalid")

    missing = sorted(set(inventory_ids) - seen)
    extra = sorted(seen - set(inventory_ids))
    if missing:
        errors.append(f"missing mappings: {', '.join(missing)}")
    if extra:
        errors.append(f"unknown mappings: {', '.join(extra)}")
    return errors


def validate_decision(
    decision: Any,
    degraded_capabilities: list[str],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(decision, dict):
        return ["degradation decision root must be an object"]
    if decision.get("schema_version") != 1:
        errors.append("degradation-decision.schema_version must be 1")
    if decision.get("status") != "approved":
        errors.append("degradation-decision.status must be approved")
    approved = decision.get("approved_capabilities")
    if not isinstance(approved, list) or any(
        not non_empty_string(item) for item in approved
    ):
        errors.append(
            "degradation-decision.approved_capabilities must contain strings"
        )
    elif set(approved) != set(degraded_capabilities):
        errors.append(
            "degradation-decision.approved_capabilities must exactly match "
            "the degraded capability set"
        )
    if not non_empty_string(decision.get("approval_evidence")):
        errors.append(
            "degradation-decision.approval_evidence must record explicit user approval"
        )
    return errors


def score(
    inventory: dict[str, Any],
    report: dict[str, Any],
    floor: float,
    decision: dict[str, Any] | None = None,
) -> dict:
    capability_by_id = {
        item["id"]: item for item in inventory["capabilities"]
    }
    mapping_by_id = {
        item["capability_id"]: item for item in report["mappings"]
    }
    weighted_total = 0.0
    weighted_retained = 0.0
    hard_blockers: list[str] = []
    low_confidence_core: list[str] = []
    degraded_capabilities: list[str] = []
    counts: Counter[str] = Counter()

    for capability_id, capability in capability_by_id.items():
        criticality = capability["criticality"]
        level = mapping_by_id[capability_id]["mapping_level"]
        weight = WEIGHTS[criticality]
        weighted_total += weight
        weighted_retained += weight * COEFFICIENTS[level]
        counts[level] += 1
        if level == "block":
            hard_blockers.append(capability_id)
        if criticality in CORE and capability["confidence"] == "low":
            low_confidence_core.append(capability_id)
        if weight > 0 and level in {"approximate", "drop"}:
            degraded_capabilities.append(capability_id)

    score_value = (
        round(weighted_retained / weighted_total * 100.0, 2)
        if weighted_total
        else 0.0
    )
    if hard_blockers or low_confidence_core or score_value < floor:
        status = "rejected"
        admitted = False
    elif score_value == 100.0:
        status = "full"
        admitted = True
    elif decision is None:
        status = "needs_degradation_approval"
        admitted = False
    else:
        status = "degraded_approved"
        admitted = True
    return {
        "schema_version": 1,
        "target_score": 100.0,
        "floor": floor,
        "score": score_value,
        "shortfall": round(100.0 - score_value, 2),
        "status": status,
        "admitted": admitted,
        "requires_degradation_approval": status == "needs_degradation_approval",
        "degraded_capabilities": sorted(degraded_capabilities),
        "hard_blockers": sorted(hard_blockers),
        "low_confidence_core": sorted(low_confidence_core),
        "weighted_total": round(weighted_total, 2),
        "weighted_retained": round(weighted_retained, 2),
        "counts": {
            level: counts.get(level, 0) for level in COEFFICIENTS
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score a Three.js to Spatial SDK capability mapping."
    )
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--decision", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--floor",
        "--threshold",
        dest="floor",
        type=float,
        default=70.0,
        help="Absolute floor after explicit degradation approval; target remains 100.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 0 <= args.floor <= 100:
        print("ERROR: floor must be between 0 and 100", file=sys.stderr)
        return 1
    try:
        inventory = load_json(args.inventory)
        mapping = load_json(args.mapping)
        decision = load_json(args.decision) if args.decision else None
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = mapping_errors(inventory, mapping)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    preliminary = score(inventory, mapping, args.floor)
    if decision is not None and preliminary["status"] == "needs_degradation_approval":
        decision_errors = validate_decision(
            decision, preliminary["degraded_capabilities"]
        )
        if decision_errors:
            for error in decision_errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
    result = score(inventory, mapping, args.floor, decision)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False))
    if result["admitted"]:
        return 0
    if result["status"] == "needs_degradation_approval":
        return 4
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
