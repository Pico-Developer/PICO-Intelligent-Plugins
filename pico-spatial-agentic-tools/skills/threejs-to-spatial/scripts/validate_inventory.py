#!/usr/bin/env python3
"""Validate Three.js source-project and semantic capability inventory artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CAPABILITY_IDS = frozenset(
    {
        "project.native-three",
        "project.typescript",
        "project.dynamic-import",
        "scene.hierarchy",
        "scene.transform",
        "scene.layers",
        "geometry.primitive",
        "geometry.buffer-static",
        "geometry.buffer-dynamic",
        "geometry.instancing",
        "asset.gltf-glb",
        "asset.usd",
        "asset.obj",
        "asset.fbx",
        "asset.hdr",
        "asset.texture",
        "asset.font",
        "asset.video",
        "material.unlit",
        "material.lambert-phong",
        "material.pbr",
        "material.shader",
        "material.raw-shader",
        "material.node-tsl",
        "lighting.ambient",
        "lighting.directional",
        "lighting.point",
        "lighting.spot",
        "lighting.ibl",
        "lighting.shadow",
        "animation.clip",
        "animation.skeletal",
        "animation.morph",
        "animation.procedural",
        "render.webgl-renderer",
        "render.webgpu-renderer",
        "render.target",
        "render.multi-camera",
        "render.layers",
        "render.postprocessing",
        "interaction.raycast",
        "interaction.pointer",
        "interaction.orbit-controls",
        "interaction.transform-controls",
        "interaction.drag",
        "view.camera-framing",
        "view.camera-presets",
        "xr.session",
        "xr.head-pose",
        "xr.controller",
        "xr.hand-tracking",
        "xr.hit-test",
        "physics.basic",
        "physics.external",
        "physics.constraints",
        "effect.points-sprite",
        "effect.particles-cpu",
        "effect.particles-gpu",
        "effect.ribbon-trail",
        "effect.decal",
        "effect.transparent-sorting",
        "audio.ambient",
        "audio.positional",
        "ui.basic-dom",
        "ui.css2d-css3d",
        "ui.complex-dom",
        "ui.layout",
        "ui.navigation",
        "ui.forms",
        "ui.overlay",
        "ui.hud",
        "ui.responsive",
        "ui.state",
        "ui.media",
        "browser.canvas2d",
        "browser.web-api",
        "runtime.frame-loop",
        "runtime.object-pool",
        "runtime.resource-lifecycle",
        "runtime.lod",
        "runtime.culling",
        "runtime.batch",
    }
)
ASSET_CAPABILITY_IDS = frozenset(
    capability_id
    for capability_id in CAPABILITY_IDS
    if capability_id.startswith("asset.")
)

CRITICALITIES = frozenset(
    {"visual_core", "interaction_core", "runtime", "infrastructure"}
)
CONFIDENCES = frozenset({"high", "medium", "low"})
LANGUAGES = frozenset({"javascript", "typescript", "mixed"})


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_source_project(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["source-project root must be an object"]
    if data.get("schema_version") != 1:
        errors.append("source-project.schema_version must be 1")
    if not is_non_empty_string(data.get("source_root")):
        errors.append("source-project.source_root must be a non-empty string")
    if data.get("language") not in LANGUAGES:
        errors.append(
            "source-project.language must be javascript, typescript, or mixed"
        )
    if not is_non_empty_string(data.get("three_version")):
        errors.append("source-project.three_version must be a non-empty string")
    if data.get("framework") != "native-three":
        errors.append("source-project.framework must be native-three")
    entrypoints = data.get("entrypoints")
    if not isinstance(entrypoints, list) or not entrypoints:
        errors.append("source-project.entrypoints must be a non-empty array")
    elif not all(is_non_empty_string(item) for item in entrypoints):
        errors.append("source-project.entrypoints must contain non-empty strings")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, dict) or not is_non_empty_string(
        dependencies.get("three")
    ):
        errors.append("source-project.dependencies.three must be present")
    return errors


def validate_inventory(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["capability-inventory root must be an object"]
    if data.get("schema_version") != 1:
        errors.append("capability-inventory.schema_version must be 1")
    capabilities = data.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        return errors + ["capability-inventory.capabilities must be a non-empty array"]

    seen: set[str] = set()
    for index, capability in enumerate(capabilities):
        prefix = f"capabilities[{index}]"
        if not isinstance(capability, dict):
            errors.append(f"{prefix} must be an object")
            continue
        capability_id = capability.get("id")
        if capability_id not in CAPABILITY_IDS:
            errors.append(f"{prefix}.id is unknown: {capability_id!r}")
        elif capability_id in seen:
            errors.append(f"{prefix}.id is duplicated: {capability_id}")
        else:
            seen.add(capability_id)
        if capability.get("criticality") not in CRITICALITIES:
            errors.append(f"{prefix}.criticality is invalid")
        if capability.get("confidence") not in CONFIDENCES:
            errors.append(f"{prefix}.confidence is invalid")
        asset_paths = capability.get("asset_paths", [])
        if capability_id in ASSET_CAPABILITY_IDS:
            if not isinstance(asset_paths, list) or not asset_paths:
                errors.append(f"{prefix}.asset_paths must be a non-empty array")
            else:
                seen_asset_paths: set[str] = set()
                for asset_index, asset_path in enumerate(asset_paths):
                    asset_prefix = f"{prefix}.asset_paths[{asset_index}]"
                    if not is_non_empty_string(asset_path):
                        errors.append(f"{asset_prefix} must be a non-empty string")
                    elif Path(asset_path).is_absolute():
                        errors.append(f"{asset_prefix} must be source-relative")
                    elif ".." in Path(asset_path).parts:
                        errors.append(f"{asset_prefix} must not traverse outside source_root")
                    elif asset_path in seen_asset_paths:
                        errors.append(f"{asset_prefix} is duplicated: {asset_path}")
                    else:
                        seen_asset_paths.add(asset_path)
        elif asset_paths:
            errors.append(f"{prefix}.asset_paths is only allowed for asset.* capabilities")
        evidence = capability.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{prefix}.evidence must be a non-empty array")
            continue
        for evidence_index, item in enumerate(evidence):
            item_prefix = f"{prefix}.evidence[{evidence_index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_prefix} must be an object")
                continue
            file_value = item.get("file")
            if not is_non_empty_string(file_value):
                errors.append(f"{item_prefix}.file must be a non-empty string")
            elif Path(file_value).is_absolute():
                errors.append(f"{item_prefix}.file must be source-relative")
            line = item.get("line")
            if not isinstance(line, int) or isinstance(line, bool) or line < 1:
                errors.append(f"{item_prefix}.line must be a positive integer")
            if not is_non_empty_string(item.get("symbol")):
                errors.append(f"{item_prefix}.symbol must be a non-empty string")
            if not is_non_empty_string(item.get("reason")):
                errors.append(f"{item_prefix}.reason must be a non-empty string")
    if "project.native-three" not in seen:
        errors.append("inventory must contain project.native-three")
    return errors


def validate_asset_files(
    source: dict[str, Any],
    inventory: dict[str, Any],
    source_project_path: Path,
) -> list[str]:
    errors: list[str] = []
    source_root = Path(source["source_root"]).expanduser()
    if not source_root.is_absolute():
        source_root = (source_project_path.parent / source_root).resolve()
    if not source_root.is_dir():
        return [f"source-project.source_root is not a directory: {source_root}"]
    for index, capability in enumerate(inventory["capabilities"]):
        if capability.get("id") not in ASSET_CAPABILITY_IDS:
            continue
        for asset_index, asset_path in enumerate(capability.get("asset_paths", [])):
            candidate = source_root / asset_path
            if not candidate.is_file():
                errors.append(
                    f"capabilities[{index}].asset_paths[{asset_index}] "
                    f"does not exist under source_root: {asset_path}"
                )
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate source-project.json and capability-inventory.json."
    )
    parser.add_argument("--source-project", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source = load_json(args.source_project)
        inventory = load_json(args.inventory)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate_source_project(source) + validate_inventory(inventory)
    if not errors:
        errors.extend(validate_asset_files(source, inventory, args.source_project))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "valid": True,
                "framework": source["framework"],
                "three_version": source["three_version"],
                "capability_count": len(inventory["capabilities"]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
