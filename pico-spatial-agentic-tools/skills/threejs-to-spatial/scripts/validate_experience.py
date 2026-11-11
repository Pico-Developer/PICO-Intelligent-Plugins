#!/usr/bin/env python3
"""Validate complete web-experience inventory and its SpatialUI mapping."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"document root must be an object: {path}")
    return value


def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(text(item) for item in value)


def unique_strings(values: list[str], field: str, errors: list[str]) -> None:
    if len(values) != len(set(values)):
        errors.append(f"{field} contains duplicate values")


def validate_evidence(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{field} must be a non-empty array")
        return
    for index, item in enumerate(value):
        prefix = f"{field}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if not text(item.get("file")):
            errors.append(f"{prefix}.file must be a non-empty string")
        line = item.get("line")
        if not isinstance(line, int) or isinstance(line, bool) or line < 1:
            errors.append(f"{prefix}.line must be a positive integer")
        if not text(item.get("reason")):
            errors.append(f"{prefix}.reason must be a non-empty string")


def validate_inventory(inventory: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if inventory.get("schema_version") != 1:
        errors.append("experience-inventory.schema_version must be 1")

    pages = inventory.get("pages")
    if not isinstance(pages, list) or not pages:
        return errors + ["experience-inventory.pages must be a non-empty array"]
    page_ids: list[str] = []
    baseline_ids: list[str] = []
    for index, page in enumerate(pages):
        prefix = f"pages[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{prefix} must be an object")
            continue
        page_id = page.get("id")
        if not text(page_id):
            errors.append(f"{prefix}.id must be a non-empty string")
            continue
        page_ids.append(page_id)
        if not text(page.get("route")):
            errors.append(f"{prefix}.route must be a non-empty string")
        for field in ("source_files", "regions", "states", "responsive_modes"):
            values = page.get(field)
            if not string_list(values):
                errors.append(f"{prefix}.{field} must be a non-empty string array")
            else:
                unique_strings(values, f"{prefix}.{field}", errors)
        states = set(page.get("states", []))
        responsive_modes = set(page.get("responsive_modes", []))
        baselines = page.get("visual_baselines")
        if not isinstance(baselines, list) or not baselines:
            errors.append(f"{prefix}.visual_baselines must be a non-empty array")
        else:
            baseline_states: set[str] = set()
            baseline_viewports: set[str] = set()
            for baseline_index, baseline in enumerate(baselines):
                baseline_prefix = (
                    f"{prefix}.visual_baselines[{baseline_index}]"
                )
                if not isinstance(baseline, dict):
                    errors.append(f"{baseline_prefix} must be an object")
                    continue
                baseline_id = baseline.get("id")
                if not text(baseline_id):
                    errors.append(f"{baseline_prefix}.id must be a non-empty string")
                else:
                    baseline_ids.append(baseline_id)
                if not text(baseline.get("evidence")):
                    errors.append(
                        f"{baseline_prefix}.evidence must be a non-empty string"
                    )
                if not text(baseline.get("viewport")):
                    errors.append(
                        f"{baseline_prefix}.viewport must be a non-empty string"
                    )
                else:
                    baseline_viewports.add(baseline["viewport"])
                    if baseline["viewport"] not in responsive_modes:
                        errors.append(
                            f"{baseline_prefix}.viewport must reference a responsive mode"
                        )
                if baseline.get("state") not in states:
                    errors.append(
                        f"{baseline_prefix}.state must reference a page state"
                    )
                else:
                    baseline_states.add(baseline["state"])
            missing_states = sorted(states - baseline_states)
            if missing_states:
                errors.append(
                    f"{prefix}.visual_baselines misses states: "
                    + ", ".join(missing_states)
                )
            missing_viewports = sorted(responsive_modes - baseline_viewports)
            if missing_viewports:
                errors.append(
                    f"{prefix}.visual_baselines misses responsive modes: "
                    + ", ".join(missing_viewports)
                )
    unique_strings(page_ids, "pages[].id", errors)
    unique_strings(baseline_ids, "pages[].visual_baselines[].id", errors)
    page_id_set = set(page_ids)

    flows = inventory.get("flows")
    if not isinstance(flows, list) or not flows:
        errors.append("experience-inventory.flows must be a non-empty array")
        flows = []
    flow_ids: list[str] = []
    for index, flow in enumerate(flows):
        prefix = f"flows[{index}]"
        if not isinstance(flow, dict):
            errors.append(f"{prefix} must be an object")
            continue
        flow_id = flow.get("id")
        if not text(flow_id):
            errors.append(f"{prefix}.id must be a non-empty string")
        else:
            flow_ids.append(flow_id)
        page_refs = flow.get("page_ids")
        if not string_list(page_refs):
            errors.append(f"{prefix}.page_ids must be a non-empty string array")
        else:
            unknown = sorted(set(page_refs) - page_id_set)
            if unknown:
                errors.append(f"{prefix}.page_ids has unknown pages: {', '.join(unknown)}")
        steps = flow.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"{prefix}.steps must be a non-empty array")
        else:
            step_ids: list[str] = []
            for step_index, step in enumerate(steps):
                step_prefix = f"{prefix}.steps[{step_index}]"
                if not isinstance(step, dict):
                    errors.append(f"{step_prefix} must be an object")
                    continue
                if not text(step.get("id")):
                    errors.append(f"{step_prefix}.id must be a non-empty string")
                else:
                    step_ids.append(step["id"])
                for field in ("action", "expected"):
                    if not text(step.get(field)):
                        errors.append(f"{step_prefix}.{field} must be non-empty")
            unique_strings(step_ids, f"{prefix}.steps[].id", errors)
        validate_evidence(flow.get("source_evidence"), f"{prefix}.source_evidence", errors)
    unique_strings(flow_ids, "flows[].id", errors)

    inputs = inventory.get("inputs")
    if not isinstance(inputs, list):
        errors.append("experience-inventory.inputs must be an array")
        inputs = []
    input_ids: list[str] = []
    for index, input_item in enumerate(inputs):
        prefix = f"inputs[{index}]"
        if not isinstance(input_item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        input_id = input_item.get("id")
        if not text(input_id):
            errors.append(f"{prefix}.id must be a non-empty string")
        else:
            input_ids.append(input_id)
        if input_item.get("page_id") not in page_id_set:
            errors.append(f"{prefix}.page_id must reference a page")
        for field in ("source_event", "expected"):
            if not text(input_item.get(field)):
                errors.append(f"{prefix}.{field} must be non-empty")
        validate_evidence(
            input_item.get("source_evidence"), f"{prefix}.source_evidence", errors
        )
    unique_strings(input_ids, "inputs[].id", errors)
    return errors


def index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items if isinstance(item, dict) and text(item.get("id"))}


def mapped_items(
    value: Any,
    id_field: str,
    field: str,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        errors.append(f"{field} must be an array")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(value):
        if not isinstance(item, dict) or not text(item.get(id_field)):
            errors.append(f"{field}[{index}].{id_field} must be a non-empty string")
            continue
        item_id = item[id_field]
        if item_id in result:
            errors.append(f"{field} contains duplicate mapping: {item_id}")
        result[item_id] = item
    return result


def mapped_string_set(value: Any, field: str, errors: list[str]) -> set[str]:
    if not isinstance(value, list) or any(not text(item) for item in value):
        errors.append(f"{field} must be a string array")
        return set()
    if len(value) != len(set(value)):
        errors.append(f"{field} contains duplicate values")
    return set(value)


def validate_contract(
    inventory: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    errors = validate_inventory(inventory)
    if errors:
        return errors
    web = contract.get("web_experience")
    if not isinstance(web, dict):
        return ["conversion-contract.web_experience must be an object"]

    source_pages = index_by_id(inventory["pages"])
    target_pages = mapped_items(
        web.get("pages"), "source_page_id", "web_experience.pages", errors
    )
    if set(target_pages) != set(source_pages):
        errors.append("web_experience.pages must map every source page exactly once")
    for page_id, source in source_pages.items():
        target = target_pages.get(page_id)
        if not target:
            continue
        if not text(target.get("composable")) or not target["composable"].endswith(".kt"):
            errors.append(f"web_experience page {page_id} must name a Kotlin composable file")
        for source_field, target_field in (
            ("regions", "mapped_regions"),
            ("states", "mapped_states"),
            ("responsive_modes", "responsive_modes"),
        ):
            target_values = mapped_string_set(
                target.get(target_field),
                f"web_experience page {page_id}.{target_field}",
                errors,
            )
            if target_values != set(source[source_field]):
                errors.append(
                    f"web_experience page {page_id} must map all {source_field}"
                )
        baseline_ids = {item["id"] for item in source["visual_baselines"]}
        target_baselines = mapped_string_set(
            target.get("visual_targets"),
            f"web_experience page {page_id}.visual_targets",
            errors,
        )
        if target_baselines != baseline_ids:
            errors.append(
                f"web_experience page {page_id} must map all visual baselines"
            )
        if not string_list(target.get("acceptance")):
            errors.append(f"web_experience page {page_id} needs acceptance criteria")

    source_flows = index_by_id(inventory["flows"])
    target_flows = mapped_items(
        web.get("flows"), "source_flow_id", "web_experience.flows", errors
    )
    if set(target_flows) != set(source_flows):
        errors.append("web_experience.flows must map every source flow exactly once")
    for flow_id, source in source_flows.items():
        target = target_flows.get(flow_id)
        if not target:
            continue
        source_steps = {item["id"] for item in source["steps"]}
        covered_steps = mapped_string_set(
            target.get("covered_steps"),
            f"web_experience flow {flow_id}.covered_steps",
            errors,
        )
        if covered_steps != source_steps:
            errors.append(f"web_experience flow {flow_id} must cover every step")
        implementation = target.get("implementation")
        if not string_list(implementation) or any(
            not item.endswith(".kt") for item in implementation
        ):
            errors.append(f"web_experience flow {flow_id} needs Kotlin implementation")
        if not string_list(target.get("acceptance")):
            errors.append(f"web_experience flow {flow_id} needs acceptance criteria")

    source_inputs = index_by_id(inventory["inputs"])
    target_inputs = mapped_items(
        web.get("inputs"), "source_input_id", "web_experience.inputs", errors
    )
    if set(target_inputs) != set(source_inputs):
        errors.append("web_experience.inputs must map every source input exactly once")
    for input_id, target in target_inputs.items():
        implementation = target.get("implementation")
        if not string_list(implementation) or any(
            not item.endswith(".kt") for item in implementation
        ):
            errors.append(f"web_experience input {input_id} needs Kotlin implementation")
        if not string_list(target.get("acceptance")):
            errors.append(f"web_experience input {input_id} needs acceptance criteria")
    return errors


def validate_verification_plan(
    inventory: dict[str, Any],
    plan: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != 1:
        errors.append("verification-plan.schema_version must be 1")
    expected_pages = {item["id"] for item in inventory["pages"]}
    expected_flows = {item["id"] for item in inventory["flows"]}
    expected_inputs = {item["id"] for item in inventory["inputs"]}
    for field, expected in (
        ("pages", expected_pages),
        ("flows", expected_flows),
        ("inputs", expected_inputs),
    ):
        actual = mapped_string_set(
            plan.get(field), f"verification-plan.{field}", errors
        )
        if actual != expected:
            errors.append(f"verification-plan.{field} must cover the complete inventory")

    expected_baselines = {
        baseline["id"]
        for page in inventory["pages"]
        for baseline in page["visual_baselines"]
    }
    views = plan.get("views")
    view_by_baseline = mapped_items(
        views, "baseline_id", "verification-plan.views", errors
    )
    if set(view_by_baseline) != expected_baselines:
        errors.append(
            "verification-plan.views must cover every visual baseline exactly once"
        )
    for baseline_id, view in view_by_baseline.items():
        for field in ("source_evidence", "target_capture"):
            if not text(view.get(field)):
                errors.append(
                    f"verification-plan view {baseline_id}.{field} must be non-empty"
                )
        if not string_list(view.get("critical_features")):
            errors.append(
                f"verification-plan view {baseline_id} needs critical_features"
            )

    interactions = plan.get("interactions")
    interaction_by_flow = mapped_items(
        interactions,
        "source_flow_id",
        "verification-plan.interactions",
        errors,
    )
    if set(interaction_by_flow) != expected_flows:
        errors.append(
            "verification-plan.interactions must cover every source flow exactly once"
        )
    covered_inputs: set[str] = set()
    for flow_id, interaction in interaction_by_flow.items():
        input_ids = mapped_string_set(
            interaction.get("source_input_ids"),
            f"verification-plan interaction {flow_id}.source_input_ids",
            errors,
        )
        unknown_inputs = sorted(input_ids - expected_inputs)
        if unknown_inputs:
            errors.append(
                f"verification-plan interaction {flow_id} has unknown inputs: "
                + ", ".join(unknown_inputs)
            )
        covered_inputs.update(input_ids)
        for field in ("precondition", "action", "expected"):
            if not text(interaction.get(field)):
                errors.append(
                    f"verification-plan interaction {flow_id}.{field} must be non-empty"
                )
    if covered_inputs != expected_inputs:
        errors.append(
            "verification-plan interactions must exercise every source input"
        )
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate complete web experience inventory and mapping."
    )
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--verification-plan", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        inventory = load_json(args.inventory)
        contract = load_json(args.contract) if args.contract else None
        verification_plan = (
            load_json(args.verification_plan) if args.verification_plan else None
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    errors = validate_inventory(inventory)
    if not errors and contract is not None:
        errors.extend(validate_contract(inventory, contract))
    if not errors and verification_plan is not None:
        errors.extend(validate_verification_plan(inventory, verification_plan))
    if contract is not None and verification_plan is None:
        errors.append(
            "--verification-plan is required when validating a conversion contract"
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "pages": len(inventory["pages"]),
                "flows": len(inventory["flows"]),
                "inputs": len(inventory["inputs"]),
                "contract_checked": contract is not None,
                "verification_plan_checked": verification_plan is not None,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
