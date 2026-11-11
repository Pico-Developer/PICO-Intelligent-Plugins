#!/usr/bin/env python3
"""Compare an app implementation receipt with the authoritative design JSON.

The receipt is verification-only. It records implementation-side facts and
source anchors; it is never an input to code generation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


DESIGN_REQUIRED_INPUT_MODES = {"intent_only", "product_doc"}
NODE_FIELDS = (
    "kind",
    "purpose",
    "designNotes",
    "parts",
    "visualStates",
    "regions",
    "textBehavior",
    "component",
    "rendererKey",
    "content",
    "assetId",
    "role",
    "trigger",
    "relationship",
    "presentation",
    "props",
    "bindings",
    "events",
    "layout",
    "appearance",
    "textStyle",
    "children",
    "visibleInStates",
    "accessibilityLabel",
)
ACTION_FIELDS = (
    "purpose",
    "type",
    "transitionId",
    "binding",
    "value",
    "payload",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--input-mode", required=True)
    parser.add_argument("--visual-asset", choices=("true", "false"), default="false")
    parser.add_argument(
        "--design-spec",
        type=Path,
        help="Defaults to <target>/design-spec.json.",
    )
    parser.add_argument(
        "--implementation-map",
        type=Path,
        help="Defaults to <target>/.scratch/design_implementation_map.json.",
    )
    return parser.parse_args()


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_fields(value: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: value[field] for field in fields if field in value}


def keyed_projection(
    values: Any,
    fields: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    if not isinstance(values, list):
        return {}
    result: dict[str, Any] = {}
    for value in values:
        if not isinstance(value, dict) or not isinstance(value.get("id"), str):
            continue
        if fields is None:
            result[value["id"]] = {key: item for key, item in value.items() if key != "id"}
        else:
            result[value["id"]] = select_fields(value, fields)
    return result


def build_contract(spec: dict[str, Any]) -> dict[str, Any]:
    if spec.get("schemaVersion") != "write-spec-draft-1":
        raise ValueError("Unsupported design schemaVersion; expected write-spec-draft-1")
    data_cases = spec.get("dataCases")
    return {
        "initialStateId": spec.get("initialStateId"),
        "surfaces": keyed_projection(spec.get("surfaces")),
        "nodes": keyed_projection(spec.get("nodes"), NODE_FIELDS),
        "states": keyed_projection(spec.get("states")),
        "transitions": keyed_projection(spec.get("transitions")),
        "actions": keyed_projection(spec.get("actions"), ACTION_FIELDS),
        "responsiveRules": keyed_projection(spec.get("responsiveRules")),
        "dataCases": sorted(data_cases) if isinstance(data_cases, dict) else [],
        "assets": keyed_projection(
            spec.get("assets"),
            ("kind", "src", "alt"),
        ),
    }


def required_design_refs(contract: dict[str, Any]) -> set[str]:
    refs = {"state-model:initial"}
    categories = (
        ("surface", "surfaces"),
        ("node", "nodes"),
        ("state", "states"),
        ("transition", "transitions"),
        ("action", "actions"),
        ("responsive-rule", "responsiveRules"),
        ("asset", "assets"),
    )
    for prefix, key in categories:
        values = contract.get(key)
        if isinstance(values, dict):
            refs.update(f"{prefix}:{item_id}" for item_id in values)
    data_cases = contract.get("dataCases")
    if isinstance(data_cases, list):
        refs.update(f"data-case:{case_id}" for case_id in data_cases)
    for node_id, node in contract.get("nodes", {}).items():
        notes = node.get("designNotes", {})
        if isinstance(notes, dict):
            refs.update(f"behavior:{node_id}:{i}" for i, _ in enumerate(notes.get("behaviors", [])))
    return refs


def add_error(
    errors: list[dict[str, Any]],
    code: str,
    path: str,
    message: str,
    *,
    expected: Any = None,
    actual: Any = None,
) -> None:
    error: dict[str, Any] = {"code": code, "path": path, "message": message}
    if expected is not None:
        error["expected"] = expected
    if actual is not None:
        error["actual"] = actual
    errors.append(error)


def compare_values(
    expected: Any,
    actual: Any,
    path: str,
    errors: list[dict[str, Any]],
) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            add_error(
                errors,
                "fact_mismatch",
                path,
                "implementation fact has the wrong type",
                expected=expected,
                actual=actual,
            )
            return
        for key in sorted(expected.keys() - actual.keys()):
            add_error(
                errors,
                "missing_fact",
                f"{path}/{key}",
                "implementation receipt is missing a design fact",
                expected=expected[key],
            )
        for key in sorted(actual.keys() - expected.keys()):
            add_error(
                errors,
                "unexpected_fact",
                f"{path}/{key}",
                "implementation receipt declares a fact absent from the design",
                actual=actual[key],
            )
        for key in sorted(expected.keys() & actual.keys()):
            compare_values(expected[key], actual[key], f"{path}/{key}", errors)
        return

    if isinstance(expected, list):
        if not isinstance(actual, list) or expected != actual:
            add_error(
                errors,
                "fact_mismatch",
                path,
                "implementation list differs from the design",
                expected=expected,
                actual=actual,
            )
        return

    if expected != actual:
        add_error(
            errors,
            "fact_mismatch",
            path,
            "implementation fact differs from the design",
            expected=expected,
            actual=actual,
        )


def resolve_source_path(target: Path, raw_path: Any) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        return None
    candidate = (target / raw_path).resolve()
    try:
        candidate.relative_to(target.resolve())
    except ValueError:
        return None
    return candidate


def check_source_mappings(
    target: Path,
    mappings: Any,
    required_refs: set[str],
    errors: list[dict[str, Any]],
) -> dict[str, int]:
    if not isinstance(mappings, list):
        add_error(
            errors,
            "invalid_source_mappings",
            "/source_mappings",
            "source_mappings must be an array",
        )
        return {"required": len(required_refs), "mapped": 0}

    mapped_refs: set[str] = set()
    for index, mapping in enumerate(mappings):
        path = f"/source_mappings/{index}"
        if not isinstance(mapping, dict):
            add_error(errors, "invalid_source_mapping", path, "mapping must be an object")
            continue

        source_path = resolve_source_path(target, mapping.get("file"))
        if source_path is None:
            add_error(
                errors,
                "invalid_source_path",
                f"{path}/file",
                "source file must be a relative path inside the target",
                actual=mapping.get("file"),
            )
            source_text = ""
        elif not source_path.is_file():
            add_error(
                errors,
                "missing_source_file",
                f"{path}/file",
                "mapped source file does not exist",
                actual=mapping.get("file"),
            )
            source_text = ""
        else:
            source_text = source_path.read_text(encoding="utf-8", errors="replace")

        for list_name in ("symbols", "evidence"):
            values = mapping.get(list_name)
            if not isinstance(values, list) or not values:
                add_error(
                    errors,
                    f"missing_{list_name}",
                    f"{path}/{list_name}",
                    f"{list_name} must contain at least one source token",
                )
                continue
            for value in values:
                if not isinstance(value, str) or not value:
                    add_error(
                        errors,
                        f"invalid_{list_name}",
                        f"{path}/{list_name}",
                        f"{list_name} entries must be non-empty strings",
                    )
                elif source_text and value not in source_text:
                    add_error(
                        errors,
                        "source_evidence_missing",
                        f"{path}/{list_name}",
                        f"source token not found in {mapping.get('file')}",
                        actual=value,
                    )

        design_refs = mapping.get("design_refs")
        if not isinstance(design_refs, list) or not design_refs:
            add_error(
                errors,
                "missing_design_refs",
                f"{path}/design_refs",
                "design_refs must contain at least one contract reference",
            )
            continue
        for design_ref in design_refs:
            if not isinstance(design_ref, str):
                add_error(
                    errors,
                    "invalid_design_ref",
                    f"{path}/design_refs",
                    "design refs must be strings",
                    actual=design_ref,
                )
                continue
            if design_ref not in required_refs:
                add_error(
                    errors,
                    "unknown_design_ref",
                    f"{path}/design_refs",
                    "source mapping references an unknown design entity",
                    actual=design_ref,
                )
            if design_ref in mapped_refs:
                add_error(
                    errors,
                    "duplicate_design_ref",
                    f"{path}/design_refs",
                    "design entity is mapped more than once",
                    actual=design_ref,
                )
            mapped_refs.add(design_ref)

    for design_ref in sorted(required_refs - mapped_refs):
        add_error(
            errors,
            "unmapped_design_ref",
            "/source_mappings",
            "design entity has no implementation source mapping",
            expected=design_ref,
        )
    return {"required": len(required_refs), "mapped": len(required_refs & mapped_refs)}


def check_planar_default_size(
    target: Path, contract: dict[str, Any], errors: list[dict[str, Any]]
) -> None:
    """Check the primary Planar launch size in real source, not receipt claims."""
    surfaces = contract.get("surfaces", {})
    initial = contract.get("states", {}).get(contract.get("initialStateId"), {})
    roots = initial.get("surfaceRoots", {})
    candidates = [
        (key, value)
        for key, value in surfaces.items()
        if value.get("type", "").lower() == "planar" and (not roots or key in roots)
    ]
    # Multiple independent launch windows need explicit per-window ownership.
    if len(candidates) != 1:
        return
    surface_id, surface = candidates[0]
    size = surface.get("defaultSize", {})
    if size.get("unit") != "dp" or not all(k in size for k in ("width", "height")):
        return
    expected = [size["width"], size["height"]]
    android = "{http://schemas.android.com/apk/res/android}"
    observed = []
    for manifest in target.glob("**/src/main/AndroidManifest.xml"):
        try:
            tree = ET.parse(manifest)
        except (OSError, ET.ParseError) as exc:
            add_error(errors, "invalid_manifest", str(manifest), str(exc))
            continue
        for activity in tree.findall("./application/activity"):
            launch = any(
                any(
                    x.get(android + "name") == "android.intent.action.MAIN"
                    for x in intent.findall("action")
                )
                and any(
                    x.get(android + "name") == "android.intent.category.LAUNCHER"
                    for x in intent.findall("category")
                )
                for intent in activity.findall("intent-filter")
            )
            if not launch:
                continue
            metadata = {
                x.get(android + "name"): x.get(android + "value")
                for x in activity.findall("meta-data")
            }
            if metadata.get("pico.spatial.windowcontainer.style", "1") not in ("0", "1"):
                continue
            raw = metadata.get("pico.spatial.windowcontainer.defaultsize", "")
            unit = metadata.get("pico.spatial.windowcontainer.defaultsize.unit", "dp")
            try:
                dimensions = [float(x) for x in raw.lower().split("x")]
            except ValueError:
                dimensions = []
            observed.append({"file": str(manifest.relative_to(target)), "size": raw, "unit": unit})
            if dimensions == expected and unit == "dp":
                return
    add_error(
        errors,
        "planar_default_size_mismatch",
        f"/surfaces/{surface_id}/defaultSize",
        "launcher manifest defaultsize must match spec defaultSize; windowConstraints only sets resize bounds",
        expected={"size": expected, "unit": "dp"},
        actual=observed,
    )


def check_volume_sizes(target, contract, mappings, errors):
    for sid, surface in contract.get("surfaces", {}).items():
        if surface.get("type") != "volume":
            continue
        size = surface.get("defaultSize", {})
        expected = [size.get(k) for k in ("width", "height", "depth")]
        if size.get("unit") != "dp" or any(
            not isinstance(v, (float, int)) or isinstance(v, bool) or v <= 0 for v in expected
        ):
            add_error(
                errors,
                "volume_size",
                f"/surfaces/{sid}",
                "Volume needs positive width, height, depth in dp",
            )
            continue
        matched = False
        for mapping in mappings if isinstance(mappings, list) else []:
            if not isinstance(mapping, dict):
                continue
            design_refs = mapping.get("design_refs")
            if not isinstance(design_refs, list) or f"surface:{sid}" not in design_refs:
                continue
            source = (target / str(mapping.get("file", ""))).resolve()
            if not source.is_relative_to(target.resolve()) or not source.is_file():
                continue
            code = source.read_text(encoding="utf-8")
            # Keep the scope explicit: marker identifies the container call, not a body Box.
            pattern = (
                r"//\s*design-style:\s*volume-container\s+"
                + re.escape(sid)
                + r"\s*\n\s*WindowContainer\s*\((.*?)defaultSize\s*=\s*WindowContainerSize\s*\(([^)]*)\)"
            )
            for match in re.finditer(pattern, code, re.S):
                prefix = match[1]
                if "{" in prefix or not re.search(r"form\s*=\s*Form\.Volumetric\b", prefix):
                    continue
                found = [
                    re.search(r"\b" + k + r"\s*=\s*(\d+(?:\.\d+)?)\.dp\b", match[2])
                    for k in ("width", "height", "depth")
                ]
                if all(found) and [float(m[1]) for m in found] == expected:
                    matched = True
        if not matched:
            add_error(
                errors,
                "volume_size_unverified",
                f"/surfaces/{sid}/defaultSize",
                "Cannot confirm Volume size in mapped source: use a marked WindowContainer call with explicit Form.Volumetric and named dp defaultSize, or extend the supported source adapter. Receipt values alone do not prove dimensions.",
            )


def check_model_deliveries(target, contract, receipt, errors):
    deliveries = receipt.get("model_deliveries", {})
    for nid, node in contract.get("nodes", {}).items():
        notes = node.get("designNotes", {})
        if (
            node.get("kind") != "domain_visual"
            or not isinstance(notes, dict)
            or "assetStatus" not in notes
        ):
            continue
        item = deliveries.get(nid) if isinstance(deliveries, dict) else None
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("resourcePaths"), list)
            or not item["resourcePaths"]
        ):
            add_error(
                errors,
                "model_delivery_missing",
                f"/nodes/{nid}",
                "Model needs delivered resources or an authored-content result, not the Preview placeholder",
            )
            continue
        paths = list(item["resourcePaths"])
        if notes.get("assetStatus") == "to-create":
            paths.append(item.get("authoringResultPath"))
        for raw in paths:
            source = (target / raw).resolve() if isinstance(raw, str) and raw else None
            if (
                source is None
                or not source.is_relative_to(target.resolve())
                or not source.is_file()
                or source.stat().st_size == 0
            ):
                add_error(
                    errors,
                    "model_resource_missing",
                    f"/model_deliveries/{nid}",
                    "Delivered model resource/Editor result must resolve to a nonempty project file",
                    actual=raw,
                )
            elif source.suffix.lower() in {".svg", ".html", ".png", ".jpg"}:
                add_error(
                    errors,
                    "model_placeholder",
                    f"/model_deliveries/{nid}",
                    "A flat Preview asset cannot stand in for the delivered model",
                    actual=raw,
                )


def write_result(output_path: Path, result: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    target = args.target.resolve()
    scratch = target / ".scratch"
    output_path = scratch / "design_fidelity_result.json"
    spec_path = (args.design_spec or target / "design-spec.json").resolve()
    map_path = (args.implementation_map or scratch / "design_implementation_map.json").resolve()

    if not spec_path.is_file():
        applicable = args.input_mode in DESIGN_REQUIRED_INPUT_MODES or (
            args.input_mode == "hybrid" and args.visual_asset == "false"
        )
        errors: list[dict[str, Any]] = []
        if applicable:
            add_error(
                errors,
                "missing_design_spec",
                str(spec_path),
                "this input mode requires an authoritative design-spec.json",
            )
        result = {
            "passed": not applicable,
            "applicable": applicable,
            "design_spec": str(spec_path),
            "implementation_map": str(map_path),
            "summary": {"errors": len(errors), "required_refs": 0, "mapped_refs": 0},
            "errors": errors,
        }
        write_result(output_path, result)
        print(
            "[design-fidelity] "
            + ("FAIL required design-spec.json is missing" if applicable else "NOT APPLICABLE")
        )
        return 1 if applicable else 0

    errors = []
    if not map_path.is_file():
        add_error(
            errors,
            "missing_implementation_map",
            str(map_path),
            "design-spec.json exists but its implementation mapping receipt is missing",
        )
        result = {
            "passed": False,
            "applicable": True,
            "design_spec": str(spec_path),
            "implementation_map": str(map_path),
            "summary": {"errors": 1, "required_refs": 0, "mapped_refs": 0},
            "errors": errors,
        }
        write_result(output_path, result)
        print(f"[design-fidelity] FAIL implementation map missing: {map_path}")
        return 1

    try:
        spec = read_json(spec_path)
        receipt = read_json(map_path)
    except (OSError, json.JSONDecodeError) as exc:
        add_error(errors, "invalid_json", "/", f"cannot read verification inputs: {exc}")
        result = {
            "passed": False,
            "applicable": True,
            "design_spec": str(spec_path),
            "implementation_map": str(map_path),
            "summary": {"errors": 1, "required_refs": 0, "mapped_refs": 0},
            "errors": errors,
        }
        write_result(output_path, result)
        print(f"[design-fidelity] FAIL {exc}")
        return 1

    if not isinstance(spec, dict) or not isinstance(receipt, dict):
        if not isinstance(spec, dict):
            add_error(
                errors,
                "invalid_root",
                "/design_spec",
                "design-spec.json root must be an object",
                actual=type(spec).__name__,
            )
        if not isinstance(receipt, dict):
            add_error(
                errors,
                "invalid_root",
                "/implementation_map",
                "design_implementation_map.json root must be an object",
                actual=type(receipt).__name__,
            )
        actual_hash = sha256(spec_path)
        result = {
            "passed": False,
            "applicable": True,
            "design_spec": str(spec_path),
            "design_spec_sha256": actual_hash,
            "implementation_map": str(map_path),
            "summary": {"errors": len(errors), "required_refs": 0, "mapped_refs": 0},
            "errors": errors,
        }
        write_result(output_path, result)
        print(f"[design-fidelity] FAIL {len(errors)} error(s)")
        for error in errors:
            detail = f" actual={error['actual']!r}" if "actual" in error else ""
            print(f"[design-fidelity] {error['code']} {error['path']}: {error['message']}{detail}")
        return 1

    if spec.get("schemaVersion") != "write-spec-draft-1":
        add_error(
            errors,
            "unsupported_design_schema_version",
            "/design_spec/schemaVersion",
            "Unsupported design schemaVersion; expected write-spec-draft-1",
        )
        write_result(
            output_path,
            {
                "passed": False,
                "applicable": True,
                "design_spec": str(spec_path),
                "implementation_map": str(map_path),
                "summary": {"errors": 1, "required_refs": 0, "mapped_refs": 0},
                "errors": errors,
            },
        )
        print("[design-fidelity] FAIL unsupported design schemaVersion")
        return 1

    contract = build_contract(spec)

    if receipt.get("schema_version") != 1:
        add_error(
            errors,
            "unsupported_schema_version",
            "/schema_version",
            "implementation map schema_version must be 1",
            expected=1,
            actual=receipt.get("schema_version"),
        )

    design_spec_meta = receipt.get("design_spec")
    actual_hash = sha256(spec_path)
    if not isinstance(design_spec_meta, dict):
        add_error(
            errors,
            "missing_design_spec_metadata",
            "/design_spec",
            "implementation map must identify the design spec and its SHA-256",
        )
    else:
        if design_spec_meta.get("path") != "design-spec.json":
            add_error(
                errors,
                "wrong_design_spec_path",
                "/design_spec/path",
                "implementation map must target design-spec.json",
                expected="design-spec.json",
                actual=design_spec_meta.get("path"),
            )
        if design_spec_meta.get("sha256") != actual_hash:
            add_error(
                errors,
                "stale_design_spec_hash",
                "/design_spec/sha256",
                "implementation map was not produced for the current design spec",
                expected=actual_hash,
                actual=design_spec_meta.get("sha256"),
            )

    implementation = receipt.get("implementation")
    if isinstance(implementation, dict):
        compare_values(contract, implementation, "/implementation", errors)
    else:
        add_error(
            errors,
            "missing_implementation_contract",
            "/implementation",
            "implementation map must record implementation-side design facts",
        )

    check_planar_default_size(target, contract, errors)
    check_volume_sizes(target, contract, receipt.get("source_mappings"), errors)
    check_model_deliveries(target, contract, receipt, errors)
    refs = required_design_refs(contract)
    coverage = check_source_mappings(
        target,
        receipt.get("source_mappings"),
        refs,
        errors,
    )
    result = {
        "passed": not errors,
        "applicable": True,
        "design_spec": str(spec_path),
        "design_spec_sha256": actual_hash,
        "implementation_map": str(map_path),
        "summary": {
            "errors": len(errors),
            "required_refs": coverage["required"],
            "mapped_refs": coverage["mapped"],
        },
        "errors": errors,
    }
    write_result(output_path, result)

    if errors:
        print(f"[design-fidelity] FAIL {len(errors)} error(s)")
        for error in errors:
            detail = f" expected={error['expected']!r}" if "expected" in error else ""
            detail += f" actual={error['actual']!r}" if "actual" in error else ""
            print(f"[design-fidelity] {error['code']} {error['path']}: {error['message']}{detail}")
        return 1

    print(
        f"[design-fidelity] PASS {coverage['mapped']}/{coverage['required']} design entities mapped"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
