#!/usr/bin/env python3
"""Validate a frozen Three.js to Spatial SDK conversion contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


MAPPING_LEVELS = frozenset({"direct", "rebuild", "approximate", "drop", "block"})
IMPLEMENTED_LEVELS = frozenset({"direct", "rebuild", "approximate"})
CONTAINERS = frozenset({"planar", "volumetric", "stage"})
OWNERSHIPS = frozenset({"kotlin_code", "source_asset", "editor_authored", "dropped"})
ASSET_PROVENANCE = frozenset(
    {"source_existing", "format_conversion", "editor_authored"}
)
SHADER_STAGES = frozenset({"surface", "vertex"})
FORBIDDEN_TERMS = (
    "webview",
    "procedural_bake",
    "generated_asset",
    "baked_from_code",
)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def allowed_ownerships(capability_id: Any, level: str) -> frozenset[str]:
    if level in {"drop", "block"}:
        return frozenset({"dropped"})
    if isinstance(capability_id, str) and capability_id.startswith("asset."):
        return frozenset({"source_asset"})
    if isinstance(capability_id, str) and capability_id.startswith("material."):
        return frozenset({"kotlin_code", "editor_authored"})
    return frozenset({"kotlin_code"})


def format_ownerships(values: frozenset[str]) -> str:
    return ", ".join(sorted(values))


def string_values(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from string_values(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from string_values(item, f"{path}[{index}]")


def validate(
    inventory: Any, mapping_report: Any, contract: Any
) -> list[str]:
    errors: list[str] = []
    if not isinstance(inventory, dict) or not isinstance(
        inventory.get("capabilities"), list
    ):
        return ["inventory.capabilities must be an array"]
    if not isinstance(mapping_report, dict) or not isinstance(
        mapping_report.get("mappings"), list
    ):
        return ["mapping-report.mappings must be an array"]
    if not isinstance(contract, dict):
        return ["conversion contract root must be an object"]
    if contract.get("schema_version") != 1:
        errors.append("conversion-contract.schema_version must be 1")
    if contract.get("target_mode") != "new-project":
        errors.append("conversion-contract.target_mode must be new-project")
    if contract.get("container") not in CONTAINERS:
        errors.append("conversion-contract.container must be planar, volumetric, or stage")
    if not non_empty_string(contract.get("sdk_version")):
        errors.append("conversion-contract.sdk_version must be a non-empty string")
    elif contract.get("sdk_version") != mapping_report.get("sdk_version"):
        errors.append("contract sdk_version must match mapping-report.sdk_version")
    for field in ("source_project", "output_project", "package_name", "app_name"):
        if not non_empty_string(contract.get(field)):
            errors.append(f"conversion-contract.{field} must be a non-empty string")

    inventory_by_id = {
        item.get("id"): item
        for item in inventory["capabilities"]
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    inventory_ids = set(inventory_by_id)
    mapping_by_id = {
        item.get("capability_id"): item
        for item in mapping_report["mappings"]
        if isinstance(item, dict)
    }
    dispositions = contract.get("capability_dispositions")
    if not isinstance(dispositions, list):
        return errors + ["conversion-contract.capability_dispositions must be an array"]

    seen: set[str] = set()
    for index, item in enumerate(dispositions):
        prefix = f"capability_dispositions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        capability_id = item.get("capability_id")
        if capability_id in seen:
            errors.append(f"{prefix}.capability_id is duplicated: {capability_id}")
        seen.add(capability_id)
        if capability_id not in inventory_ids:
            errors.append(f"{prefix}.capability_id is not in inventory: {capability_id}")
            continue
        mapping = mapping_by_id.get(capability_id)
        if mapping is None:
            errors.append(f"{prefix} has no mapping report entry")
            continue
        level = item.get("mapping_level")
        if level not in MAPPING_LEVELS:
            errors.append(f"{prefix}.mapping_level is invalid")
            continue
        if level != mapping.get("mapping_level"):
            errors.append(f"{prefix}.mapping_level does not match mapping report")
        allowed = allowed_ownerships(capability_id, level)
        mapping_ownership = mapping.get("target_ownership")
        if mapping_ownership not in allowed:
            errors.append(
                f"{prefix} mapping target_ownership must be one of "
                f"{format_ownerships(allowed)}"
            )
        ownership = item.get("ownership")
        if ownership not in OWNERSHIPS:
            errors.append(f"{prefix}.ownership is invalid")
        elif ownership not in allowed:
            errors.append(
                f"{prefix}.ownership must be one of {format_ownerships(allowed)}"
            )
        elif ownership != mapping_ownership:
            errors.append(f"{prefix}.ownership does not match mapping report")
        if level == "block":
            errors.append(f"{prefix} cannot contain a blocked capability")
        if level in IMPLEMENTED_LEVELS:
            implementation = item.get("implementation")
            if not non_empty_list(implementation):
                errors.append(f"{prefix}.implementation is required for {level}")
            else:
                for implementation_index, implementation_path in enumerate(
                    implementation
                ):
                    implementation_prefix = (
                        f"{prefix}.implementation[{implementation_index}]"
                    )
                    if not non_empty_string(implementation_path):
                        errors.append(
                            f"{implementation_prefix} must be a non-empty string"
                        )
                    elif Path(implementation_path).is_absolute():
                        errors.append(
                            f"{implementation_prefix} must be target-relative"
                        )
                    elif not implementation_path.endswith(".kt"):
                        errors.append(
                            f"{implementation_prefix} must reference Kotlin code, "
                            "not a generated asset"
                        )
        if level == "approximate":
            if not non_empty_list(item.get("visible_loss")):
                errors.append(f"{prefix}.visible_loss is required for approximate")
            if not non_empty_list(item.get("acceptance")):
                errors.append(f"{prefix}.acceptance is required for approximate")
        if level == "drop" and not non_empty_list(item.get("visible_loss")):
            errors.append(f"{prefix}.visible_loss is required for drop")

    missing = sorted(inventory_ids - seen)
    extra = sorted(seen - inventory_ids)
    if missing:
        errors.append(f"missing capability dispositions: {', '.join(missing)}")
    if extra:
        errors.append(f"unknown capability dispositions: {', '.join(extra)}")
    if set(mapping_by_id) != inventory_ids:
        errors.append("mapping report and inventory capability sets differ")

    scene = contract.get("scene")
    if not isinstance(scene, dict):
        errors.append("conversion-contract.scene must be an object")
    else:
        if not non_empty_string(scene.get("root_id")):
            errors.append("conversion-contract.scene.root_id must be non-empty")
        units = scene.get("units_to_meters")
        if not isinstance(units, (int, float)) or isinstance(units, bool) or units <= 0:
            errors.append("conversion-contract.scene.units_to_meters must be positive")
        if not non_empty_string(scene.get("forward_conversion")):
            errors.append(
                "conversion-contract.scene.forward_conversion must be non-empty"
            )

    for field in (
        "systems",
        "interactions",
        "spatial_ui",
        "cleanup",
        "approximations",
        "dropped",
    ):
        if not isinstance(contract.get(field), list):
            errors.append(f"conversion-contract.{field} must be an array")

    assets = contract.get("assets")
    actual_source_assets: set[tuple[str, str]] = set()
    editor_asset_capabilities: set[str] = set()
    if not isinstance(assets, list):
        errors.append("conversion-contract.assets must be an array")
    else:
        seen_asset_ids: set[str] = set()
        for asset_index, asset in enumerate(assets):
            prefix = f"assets[{asset_index}]"
            if not isinstance(asset, dict):
                errors.append(f"{prefix} must be an object")
                continue
            asset_id = asset.get("id")
            if not non_empty_string(asset_id):
                errors.append(f"{prefix}.id must be a non-empty string")
            elif asset_id in seen_asset_ids:
                errors.append(f"{prefix}.id is duplicated: {asset_id}")
            else:
                seen_asset_ids.add(asset_id)
            provenance = asset.get("provenance")
            if provenance not in ASSET_PROVENANCE:
                errors.append(
                    f"{prefix}.provenance must be source_existing, "
                    "format_conversion, or editor_authored"
                )
                continue
            editor_authored = provenance == "editor_authored"
            source_capability = asset.get("source_capability")
            source_record = inventory_by_id.get(source_capability)
            if editor_authored:
                if (
                    source_record is None
                    or not isinstance(source_capability, str)
                    or not source_capability.startswith("material.")
                ):
                    errors.append(
                        f"{prefix}.source_capability must reference an "
                        "inventoried material.* capability"
                    )
                    continue
            elif (
                source_record is None
                or not isinstance(source_capability, str)
                or not source_capability.startswith("asset.")
            ):
                errors.append(
                    f"{prefix}.source_capability must reference an inventoried asset.* capability"
                )
                continue
            if editor_authored:
                editor_asset_capabilities.add(source_capability)
            source_path = asset.get("source_path")
            if not non_empty_string(source_path):
                errors.append(f"{prefix}.source_path must be a non-empty string")
            elif editor_authored:
                if Path(source_path).is_absolute():
                    errors.append(
                        f"{prefix}.source_path must be target-workspace relative"
                    )
            elif source_path not in source_record.get("asset_paths", []):
                errors.append(
                    f"{prefix}.source_path is not declared by "
                    f"{source_capability}.asset_paths"
                )
            else:
                actual_source_assets.add((source_capability, source_path))
            output_path = asset.get("output_path")
            if not non_empty_string(output_path):
                errors.append(f"{prefix}.output_path must be a non-empty string")
            elif Path(output_path).is_absolute():
                errors.append(f"{prefix}.output_path must be target-relative")
            elif not output_path.startswith("app/src/main/assets/"):
                errors.append(
                    f"{prefix}.output_path must be under app/src/main/assets/"
                )
            conversion = asset.get("conversion")
            if provenance == "format_conversion" and not non_empty_string(conversion):
                errors.append(
                    f"{prefix}.conversion is required for format_conversion"
                )
            if provenance == "source_existing" and conversion not in (None, ""):
                errors.append(
                    f"{prefix}.conversion must be null for source_existing"
                )
            if editor_authored and not non_empty_string(conversion):
                errors.append(f"{prefix}.conversion is required for editor_authored")
            if editor_authored and asset.get("shader_stage") not in SHADER_STAGES:
                errors.append(
                    f"{prefix}.shader_stage must be surface or vertex for editor_authored"
                )

    for capability_id, mapping in mapping_by_id.items():
        if mapping.get("target_ownership") != "editor_authored":
            continue
        if capability_id not in editor_asset_capabilities:
            errors.append(
                f"{capability_id} is editor_authored but has no editor_authored asset contract"
            )

    expected_source_assets: set[tuple[str, str]] = set()
    for capability_id, source_record in inventory_by_id.items():
        mapping = mapping_by_id.get(capability_id, {})
        if mapping.get("target_ownership") == "source_asset":
            for source_path in source_record.get("asset_paths", []):
                expected_source_assets.add((capability_id, source_path))
    missing_assets = sorted(expected_source_assets - actual_source_assets)
    extra_assets = sorted(actual_source_assets - expected_source_assets)
    if missing_assets:
        errors.append(
            "missing source asset contracts: "
            + ", ".join(f"{capability}:{path}" for capability, path in missing_assets)
        )
    if extra_assets:
        errors.append(
            "unmapped source asset contracts: "
            + ", ".join(f"{capability}:{path}" for capability, path in extra_assets)
        )

    for value_path, value in string_values(contract):
        lowered = value.lower()
        for term in FORBIDDEN_TERMS:
            if term in lowered:
                errors.append(
                    f"{value_path} contains forbidden runtime dependency: {term}"
                )
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a frozen Three.js to Spatial SDK conversion contract."
    )
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        inventory = load_json(args.inventory)
        mapping = load_json(args.mapping)
        contract = load_json(args.contract)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate(inventory, mapping, contract)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "valid": True,
                "sdk_version": contract["sdk_version"],
                "container": contract["container"],
                "capability_count": len(contract["capability_dispositions"]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
