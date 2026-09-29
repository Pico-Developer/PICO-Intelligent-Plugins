#!/usr/bin/env python3
"""Compare an app implementation receipt with the authoritative design JSON.

The receipt is verification-only. It records implementation-side facts and
source anchors; it is never an input to code generation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


DESIGN_REQUIRED_INPUT_MODES = {"intent_only", "product_doc"}
NODE_FIELDS = (
    "kind",
    "component",
    "rendererKey",
    "content",
    "assetId",
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
            print(
                f"[design-fidelity] {error['code']} {error['path']}: "
                f"{error['message']}{detail}"
            )
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
