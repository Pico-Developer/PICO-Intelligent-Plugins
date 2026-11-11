#!/usr/bin/env python3
"""Validate source/target observations and score delivered outcome fidelity.

Exit codes:
  0 - full fidelity or an explicitly approved degraded outcome
  1 - outcome is incomplete, fails the absolute floor, or has unverified core losses
  2 - artifact validation failed
  4 - outcome needs explicit degradation approval
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DIMENSIONS = {
    "page_structure": 15.0,
    "visual_layout": 15.0,
    "ui_content_style": 10.0,
    "ui_states_responsive": 10.0,
    "user_flows_interaction": 15.0,
    "scene_structure": 10.0,
    "animation_timing": 10.0,
    "view_camera": 5.0,
    "material_lighting": 10.0,
}


class ValidationError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError("document root must be an object")
    return value


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")
    return value


def validate(observations: dict[str, Any]) -> list[dict[str, Any]]:
    if observations.get("schema_version") != 1:
        raise ValidationError("schema_version must be 1")
    dimensions = observations.get("dimensions")
    if not isinstance(dimensions, list):
        raise ValidationError("dimensions must be an array")

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(dimensions):
        prefix = f"dimensions[{index}]"
        if not isinstance(item, dict):
            raise ValidationError(f"{prefix} must be an object")
        dimension_id = require_text(item.get("id"), f"{prefix}.id")
        if dimension_id not in DIMENSIONS:
            raise ValidationError(f"{prefix}.id is unknown: {dimension_id}")
        if dimension_id in seen:
            raise ValidationError(f"duplicate dimension: {dimension_id}")
        seen.add(dimension_id)

        score = item.get("score")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            raise ValidationError(f"{prefix}.score must be numeric")
        if not 0 <= float(score) <= 100:
            raise ValidationError(f"{prefix}.score must be between 0 and 100")

        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValidationError(f"{prefix}.evidence must be a non-empty array")
        for evidence_index, record in enumerate(evidence):
            evidence_prefix = f"{prefix}.evidence[{evidence_index}]"
            if not isinstance(record, dict):
                raise ValidationError(f"{evidence_prefix} must be an object")
            require_text(record.get("source"), f"{evidence_prefix}.source")
            require_text(record.get("target"), f"{evidence_prefix}.target")
            require_text(record.get("judgement"), f"{evidence_prefix}.judgement")

        losses = item.get("unverified_core_losses", [])
        if not isinstance(losses, list) or any(
            not isinstance(loss, str) or not loss.strip() for loss in losses
        ):
            raise ValidationError(
                f"{prefix}.unverified_core_losses must contain non-empty strings"
            )
        degradation_capabilities = item.get("degradation_capabilities", [])
        if not isinstance(degradation_capabilities, list) or any(
            not isinstance(capability_id, str) or not capability_id.strip()
            for capability_id in degradation_capabilities
        ):
            raise ValidationError(
                f"{prefix}.degradation_capabilities must contain non-empty strings"
            )
        implementation_gaps = item.get("implementation_gaps", [])
        if not isinstance(implementation_gaps, list) or any(
            not isinstance(capability_id, str) or not capability_id.strip()
            for capability_id in implementation_gaps
        ):
            raise ValidationError(
                f"{prefix}.implementation_gaps must contain non-empty strings"
            )
        if float(score) < 100 and not (
            degradation_capabilities or implementation_gaps
        ):
            raise ValidationError(
                f"{prefix} requires degradation_capabilities or implementation_gaps "
                "when score is below 100"
            )

        normalized.append(
            {
                "id": dimension_id,
                "weight": DIMENSIONS[dimension_id],
                "score": float(score),
                "evidence_count": len(evidence),
                "unverified_core_losses": losses,
                "degradation_capabilities": degradation_capabilities,
                "implementation_gaps": implementation_gaps,
            }
        )

    missing = set(DIMENSIONS) - seen
    if missing:
        raise ValidationError(f"missing dimensions: {', '.join(sorted(missing))}")
    return normalized


def score(
    observations: dict[str, Any],
    floor: float,
    dimension_floor: float,
    decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    dimensions = validate(observations)
    total = sum(item["score"] * item["weight"] for item in dimensions) / 100.0
    failed_dimensions = [
        item["id"] for item in dimensions if item["score"] < dimension_floor
    ]
    unverified_core_losses = [
        {"dimension": item["id"], "loss": loss}
        for item in dimensions
        for loss in item["unverified_core_losses"]
    ]
    observed_degradations = sorted(
        {
            capability_id
            for item in dimensions
            for capability_id in item["degradation_capabilities"]
        }
    )
    implementation_gaps = sorted(
        {
            capability_id
            for item in dimensions
            for capability_id in item["implementation_gaps"]
        }
    )
    decision_errors: list[str] = []
    if decision is not None:
        if decision.get("schema_version") != 1:
            decision_errors.append("degradation-decision.schema_version must be 1")
        if decision.get("status") != "approved":
            decision_errors.append("degradation-decision.status must be approved")
        approved = decision.get("approved_capabilities")
        if not isinstance(approved, list) or any(
            not isinstance(item, str) or not item.strip() for item in approved
        ):
            decision_errors.append(
                "degradation-decision.approved_capabilities must contain strings"
            )
            approved_set: set[str] = set()
        else:
            approved_set = set(approved)
        unapproved = sorted(set(observed_degradations) - approved_set)
        if unapproved:
            decision_errors.append(
                "outcome contains unapproved degradation capabilities: "
                + ", ".join(unapproved)
            )
        if not isinstance(decision.get("approval_evidence"), str) or not decision[
            "approval_evidence"
        ].strip():
            decision_errors.append(
                "degradation-decision.approval_evidence must record explicit user approval"
            )

    floor_failed = total < floor or bool(failed_dimensions)
    full = (
        total == 100
        and all(item["score"] == 100 for item in dimensions)
        and not unverified_core_losses
    )
    if implementation_gaps:
        status = "incomplete"
        passed = False
    elif unverified_core_losses or floor_failed:
        status = "failed"
        passed = False
    elif full:
        status = "full"
        passed = True
    elif decision is None:
        status = "needs_degradation_approval"
        passed = False
    elif decision_errors:
        raise ValidationError("; ".join(decision_errors))
    else:
        status = "degraded_approved"
        passed = True
    return {
        "schema_version": 1,
        "target_score": 100.0,
        "floor": floor,
        "dimension_floor": dimension_floor,
        "score": round(total, 2),
        "shortfall": round(100.0 - total, 2),
        "status": status,
        "passed": passed,
        "requires_degradation_approval": status == "needs_degradation_approval",
        "observed_degradations": observed_degradations,
        "implementation_gaps": implementation_gaps,
        "dimensions": dimensions,
        "failed_dimensions": failed_dimensions,
        "unverified_core_losses": unverified_core_losses,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--decision", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--floor",
        "--threshold",
        dest="floor",
        type=float,
        default=70.0,
        help="Absolute floor after explicit degradation approval; target remains 100.",
    )
    parser.add_argument("--dimension-floor", type=float, default=70.0)
    args = parser.parse_args()
    if not 0 <= args.floor <= 100:
        print("ERROR: floor must be between 0 and 100", file=sys.stderr)
        return 2
    if not 0 <= args.dimension_floor <= 100:
        print("ERROR: dimension floor must be between 0 and 100", file=sys.stderr)
        return 2

    try:
        result = score(
            load_json(args.observations),
            args.floor,
            args.dimension_floor,
            load_json(args.decision) if args.decision else None,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["passed"]:
        return 0
    if result["status"] == "needs_degradation_approval":
        return 4
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
