#!/usr/bin/env python3
"""Handoff-receipt checker for spatial-design-to-app.

`spatial-design-to-app` generates code directly from design facts and does not
persist intermediate workflow JSON. Two receipts survive, because both record a
decision made *outside* this skill that cannot be re-derived from the code:

- `design_escalation_receipt.json` — proves the mandatory
  `pico-spatial-app-designer` pass actually happened and passed for a no-visual
  request. Without it, "I designed it myself" is indistinguishable from
  "a designer reviewed it".
- `onboarding_handoff.json` — proves `spatial-app-onboarding` returned a
  scaffold-only project for a `new_project` run, so onboarding did not quietly
  implement product UI that belongs to this skill.

Everything else is verified against the generated Kotlin / AndroidManifest by
`scan_implementation.py`.

Usage:
    python3 -m scripts.check_handoff_receipts --target ./myapp \\
        --input-mode intent_only --generation-mode new_project --visual-asset false
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VALID_INPUT_MODES = {
    "visual_design",
    "visual_reference",
    "product_doc",
    "intent_only",
    "hybrid",
    "incremental_patch",
}
VALID_GENERATION_MODES = {"existing_module", "new_project"}

DESIGN_ESCALATION_RECEIPT = "design_escalation_receipt.json"
ONBOARDING_HANDOFF = "onboarding_handoff.json"

# Modes that carry no visual asset of their own. `hybrid` depends on whether the
# caller actually supplied a Figma URL / screenshot / mockup.
NO_VISUAL_MODES = {"intent_only", "product_doc"}


def _print_ok(label: str, path: Path) -> None:
    print(f"[receipt-check] OK {label}: {path}")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"[receipt-check] Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[receipt-check] Invalid JSON in {path}: {exc}") from exc


def _ensure_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SystemExit(f"[receipt-check] {label} must be a JSON object")
    return value


def _require_keys(data: dict[str, Any], keys: list[str], label: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise SystemExit(f"[receipt-check] {label} is missing keys: {', '.join(missing)}")


def _require_non_empty(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"[receipt-check] {label} must be a non-empty string")


def requires_design_escalation(input_mode: str, visual_asset: bool) -> bool:
    if input_mode in NO_VISUAL_MODES:
        return True
    return input_mode == "hybrid" and not visual_asset


def validate_design_escalation_receipt(
    scratch_dir: Path,
    input_mode: str,
    visual_asset: bool,
) -> None:
    required = requires_design_escalation(input_mode, visual_asset)
    receipt_path = scratch_dir / DESIGN_ESCALATION_RECEIPT

    if not required:
        if receipt_path.exists():
            receipt = _ensure_dict(_load_json(receipt_path), "Design Escalation Receipt")
            if receipt.get("gate_required") is not False:
                raise SystemExit(
                    "[receipt-check] Design Escalation Receipt exists for an input that has a "
                    "visual asset; it must record gate_required=false"
                )
        return

    if not receipt_path.exists():
        raise SystemExit(
            f"[receipt-check] Missing required file: {receipt_path}. "
            f"input_mode={input_mode} has no visual asset, so app generation requires a "
            "completed pico-spatial-app-designer pass before code is written."
        )

    receipt = _ensure_dict(_load_json(receipt_path), "Design Escalation Receipt")
    _require_keys(
        receipt,
        [
            "schema_version",
            "phase",
            "input_mode",
            "visual_asset_present",
            "gate_required",
            "status",
            "pre_gates",
        ],
        "Design Escalation Receipt",
    )

    if receipt["input_mode"] != input_mode:
        raise SystemExit(
            f"[receipt-check] Design Escalation Receipt.input_mode={receipt['input_mode']!r} "
            f"does not match the declared input mode {input_mode!r}"
        )
    if receipt["gate_required"] is not True:
        raise SystemExit("[receipt-check] Design Escalation Receipt.gate_required must be true")
    if receipt["visual_asset_present"] is not False:
        raise SystemExit(
            "[receipt-check] Design Escalation Receipt.visual_asset_present must be false "
            "when the designer gate fires"
        )

    status = receipt["status"]
    if status == "fallback_accepted":
        raise SystemExit(
            "[receipt-check] Design Escalation Receipt.status=fallback_accepted is not a valid "
            "path for app generation. Run pico-spatial-app-designer to completion, or report "
            "BLOCKED — do not generate from shallow text extraction."
        )
    if status != "designer_passed":
        raise SystemExit(
            f"[receipt-check] Design Escalation Receipt.status={status!r} is not valid; "
            "only designer_passed permits app generation"
        )

    pre_gates = _ensure_dict(receipt["pre_gates"], "Design Escalation Receipt.pre_gates")
    _require_keys(
        pre_gates,
        ["designDocComplete", "postBuildVerdict"],
        "Design Escalation Receipt.pre_gates",
    )
    if pre_gates["designDocComplete"] is not True:
        raise SystemExit(
            "[receipt-check] Design Escalation Receipt.pre_gates.designDocComplete must be true"
        )
    if pre_gates["postBuildVerdict"] != "pass":
        raise SystemExit(
            "[receipt-check] Design Escalation Receipt.pre_gates.postBuildVerdict must be 'pass' "
            f"(got {pre_gates['postBuildVerdict']!r}); the designer's own critique gate must pass "
            "before app generation starts"
        )

    _print_ok("Design Escalation Receipt", receipt_path)


def validate_onboarding_handoff(
    scratch_dir: Path,
    input_mode: str,
    generation_mode: str,
) -> None:
    if generation_mode != "new_project" or input_mode == "incremental_patch":
        return

    handoff_path = scratch_dir / ONBOARDING_HANDOFF
    if not handoff_path.exists():
        raise SystemExit(
            f"[receipt-check] Missing required file: {handoff_path}. "
            "new_project runs must record a scaffold-only spatial-app-onboarding handoff "
            "before spatial-design-to-app resumes implementation."
        )

    handoff = _ensure_dict(_load_json(handoff_path), "Onboarding Handoff")
    _require_keys(
        handoff,
        [
            "schema_version",
            "phase",
            "producer_skill",
            "consumer_skill",
            "scaffold_only",
            "product_ui_implemented",
            "template",
            "package",
            "entry_points",
            "build_passed",
            "launch_checked",
            "resume_required",
            "resume_skill",
        ],
        "Onboarding Handoff",
    )
    if handoff["schema_version"] != 1:
        raise SystemExit("[receipt-check] Onboarding Handoff.schema_version must be 1")
    if handoff["phase"] != "6_scaffold_handoff":
        raise SystemExit("[receipt-check] Onboarding Handoff.phase must be 6_scaffold_handoff")
    if handoff["producer_skill"] != "spatial-app-onboarding":
        raise SystemExit(
            "[receipt-check] Onboarding Handoff.producer_skill must be spatial-app-onboarding"
        )
    if handoff["consumer_skill"] != "spatial-design-to-app":
        raise SystemExit(
            "[receipt-check] Onboarding Handoff.consumer_skill must be spatial-design-to-app"
        )
    if handoff["scaffold_only"] is not True:
        raise SystemExit("[receipt-check] Onboarding Handoff.scaffold_only must be true")
    if handoff["product_ui_implemented"] is not False:
        raise SystemExit(
            "[receipt-check] Onboarding Handoff.product_ui_implemented must be false; "
            "product UI belongs to spatial-design-to-app after scaffold handoff"
        )
    if handoff["template"] not in {"planar", "volumetric", "stage"}:
        raise SystemExit(
            "[receipt-check] Onboarding Handoff.template must be planar, volumetric, or stage"
        )
    _require_non_empty(handoff["package"], "Onboarding Handoff.package")
    entry_points = handoff["entry_points"]
    if not isinstance(entry_points, list) or not entry_points:
        raise SystemExit("[receipt-check] Onboarding Handoff.entry_points must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in entry_points):
        raise SystemExit(
            "[receipt-check] Onboarding Handoff.entry_points must contain non-empty strings"
        )
    if handoff["build_passed"] is not True:
        raise SystemExit("[receipt-check] Onboarding Handoff.build_passed must be true")
    if not isinstance(handoff["launch_checked"], bool):
        raise SystemExit("[receipt-check] Onboarding Handoff.launch_checked must be a boolean")
    if handoff["launch_checked"] is False:
        _require_non_empty(
            handoff.get("launch_check_note"), "Onboarding Handoff.launch_check_note"
        )
    if handoff["resume_required"] is not True or handoff["resume_skill"] != "spatial-design-to-app":
        raise SystemExit(
            "[receipt-check] Onboarding Handoff must set resume_required=true and "
            "resume_skill=spatial-design-to-app"
        )
    _print_ok("Onboarding Handoff", handoff_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Project directory")
    parser.add_argument(
        "--scratch-dir", help="Override for the scratch directory. Defaults to <target>/.scratch"
    )
    parser.add_argument("--input-mode", required=True, choices=sorted(VALID_INPUT_MODES))
    parser.add_argument("--generation-mode", required=True, choices=sorted(VALID_GENERATION_MODES))
    parser.add_argument(
        "--visual-asset",
        choices=["true", "false"],
        default="false",
        help="Whether the request carried a Figma URL, screenshot, or mockup",
    )
    args = parser.parse_args(argv)

    target = Path(args.target).expanduser().resolve()
    scratch_dir = (
        Path(args.scratch_dir).expanduser().resolve() if args.scratch_dir else target / ".scratch"
    )
    scratch_dir.mkdir(parents=True, exist_ok=True)
    visual_asset = args.visual_asset == "true"

    validate_design_escalation_receipt(scratch_dir, args.input_mode, visual_asset)
    validate_onboarding_handoff(scratch_dir, args.input_mode, args.generation_mode)

    print(
        f"[receipt-check] SUCCESS input_mode={args.input_mode} "
        f"generation_mode={args.generation_mode} visual_asset={visual_asset}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
