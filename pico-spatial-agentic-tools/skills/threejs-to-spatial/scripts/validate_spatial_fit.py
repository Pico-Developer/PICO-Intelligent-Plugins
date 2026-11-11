#!/usr/bin/env python3
"""Validate externally captured Spatial region bounds and scene fit calculations."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Any


EPSILON = 1e-4
EXPECTED_MEASUREMENT_METHOD = "runtime-clipping-box"
EXPECTED_SOURCE_PRODUCER = "three-runtime-aabb-probe"
EXPECTED_TARGET_PRODUCER = "spatialview-visible-region-probe"
EXPECTED_SOURCE_SPACE = "three-world-source-units"
EXPECTED_TARGET_SPACE = "spatial-view-local-px"
RUNTIME_BOUNDS_POLICIES = {
    "exact",
    "conservative-contains-expected",
}
AXIS_INDEX = {"x": 0, "y": 1, "z": 2}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(non_empty_string(item) for item in value)
    )


def finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=EPSILON, abs_tol=EPSILON)


def vector3(value: Any, path: str, errors: list[str]) -> list[float] | None:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(not finite_number(item) for item in value)
    ):
        errors.append(f"{path} must contain three finite numbers")
        return None
    return [float(item) for item in value]


def aabb(
    value: Any,
    path: str,
    errors: list[str],
    *,
    require_volume: bool,
) -> tuple[list[float], list[float], list[float]] | None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return None
    minimum = vector3(value.get("min"), f"{path}.min", errors)
    maximum = vector3(value.get("max"), f"{path}.max", errors)
    size = vector3(value.get("size"), f"{path}.size", errors)
    if minimum is None or maximum is None or size is None:
        return None
    for axis in range(3):
        if maximum[axis] < minimum[axis]:
            errors.append(f"{path}.max[{axis}] must be >= min[{axis}]")
        expected_size = maximum[axis] - minimum[axis]
        if not close(size[axis], expected_size):
            errors.append(
                f"{path}.size[{axis}] must equal max[{axis}] - min[{axis}]"
            )
        if size[axis] < 0 or (require_volume and size[axis] <= 0):
            comparator = "positive" if require_volume else "non-negative"
            errors.append(f"{path}.size[{axis}] must be {comparator}")
    if not require_volume and not any(item > 0 for item in size):
        errors.append(f"{path} must have at least one positive dimension")
    return minimum, maximum, size


def contains(
    outer: tuple[list[float], list[float], list[float]],
    inner: tuple[list[float], list[float], list[float]],
) -> bool:
    return all(
        inner[0][axis] >= outer[0][axis] - EPSILON
        and inner[1][axis] <= outer[1][axis] + EPSILON
        for axis in range(3)
    )


def same_aabb(
    left: tuple[list[float], list[float], list[float]],
    right: tuple[list[float], list[float], list[float]],
) -> bool:
    return all(
        close(left[group][axis], right[group][axis])
        for group in range(3)
        for axis in range(3)
    )


def uniform_scale_limit(
    bounds: tuple[list[float], list[float], list[float]],
    outer: tuple[list[float], list[float], list[float]],
    axis_mapping: list[tuple[int, int]],
    units: float,
    translation: list[float],
) -> list[float]:
    limits: list[float] = []
    for target_axis, (source_axis, sign) in enumerate(axis_mapping):
        low = bounds[0][source_axis] * units
        high = bounds[1][source_axis] * units
        if sign < 0:
            low, high = -high, -low
        if low < -EPSILON:
            limit = (outer[0][target_axis] - translation[target_axis]) / low
            if limit > 0:
                limits.append(limit)
        if high > EPSILON:
            limit = (outer[1][target_axis] - translation[target_axis]) / high
            if limit > 0:
                limits.append(limit)
    return limits


def point_list(value: Any, path: str, errors: list[str]) -> list[list[float]] | None:
    if not isinstance(value, list) or len(value) != 8:
        errors.append(f"{path} must contain exactly eight points")
        return None
    points: list[list[float]] = []
    for index, item in enumerate(value):
        point = vector3(item, f"{path}[{index}]", errors)
        if point is not None:
            points.append(point)
    return points if len(points) == 8 else None


def same_points(left: list[list[float]], right: list[list[float]]) -> bool:
    unmatched = list(right)
    for point in left:
        match = next(
            (
                index
                for index, candidate in enumerate(unmatched)
                if all(close(point[axis], candidate[axis]) for axis in range(3))
            ),
            None,
        )
        if match is None:
            return False
        unmatched.pop(match)
    return not unmatched


def corners_for_box(
    bounds: tuple[list[float], list[float], list[float]],
) -> list[list[float]]:
    return [
        [float(x), float(y), float(z)]
        for x, y, z in product(
            (bounds[0][0], bounds[1][0]),
            (bounds[0][1], bounds[1][1]),
            (bounds[0][2], bounds[1][2]),
        )
    ]


def aabb_from_points(
    points: list[list[float]],
) -> tuple[list[float], list[float], list[float]]:
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return minimum, maximum, [
        maximum[axis] - minimum[axis] for axis in range(3)
    ]


def context_fingerprint(context: dict[str, Any]) -> str:
    canonical = json.dumps(
        context,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    value = 0x811C9DC5
    for byte in canonical.encode("utf-8"):
        value ^= byte
        value = (value * 0x01000193) & 0xFFFFFFFF
    return f"fnv1a32:{value:08x}"


def probe_measurement(
    value: Any,
    path: str,
    errors: list[str],
    *,
    expected_kind: str,
    expected_producer: str,
    expected_space: str,
    aabb_key: str,
    require_volume: bool,
    converted_corners_key: str | None,
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return None
    if value.get("schema_version") != 1:
        errors.append(f"{path}.schema_version must be 1")
    if value.get("measurement_kind") != expected_kind:
        errors.append(f"{path}.measurement_kind must be {expected_kind}")

    producer = value.get("producer")
    if not isinstance(producer, dict):
        errors.append(f"{path}.producer must be an object")
    else:
        if producer.get("id") != expected_producer:
            errors.append(f"{path}.producer.id must be {expected_producer}")
        if producer.get("version") != 1:
            errors.append(f"{path}.producer.version must be 1")

    captured_at = value.get("captured_at_utc")
    if not non_empty_string(captured_at):
        errors.append(f"{path}.captured_at_utc must be a non-empty ISO timestamp")
    else:
        try:
            parsed = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError
        except ValueError:
            errors.append(f"{path}.captured_at_utc must include a timezone")

    context = value.get("context")
    if not isinstance(context, dict) or not context:
        errors.append(f"{path}.context must be a non-empty object")
        context = None
    elif value.get("context_fingerprint") != context_fingerprint(context):
        errors.append(f"{path}.context_fingerprint does not match context")

    raw_value = value.get("raw_box")
    raw_bounds = aabb(
        raw_value,
        f"{path}.raw_box",
        errors,
        require_volume=require_volume,
    )
    if isinstance(raw_value, dict) and raw_value.get("space") != expected_space:
        errors.append(f"{path}.raw_box.space must be {expected_space}")
    raw_corners = point_list(value.get("raw_corners"), f"{path}.raw_corners", errors)
    if (
        raw_bounds is not None
        and raw_corners is not None
        and not same_points(raw_corners, corners_for_box(raw_bounds))
    ):
        errors.append(f"{path}.raw_corners must be the eight raw_box corners")

    declared = aabb(
        value.get(aabb_key),
        f"{path}.{aabb_key}",
        errors,
        require_volume=require_volume,
    )
    derived = raw_bounds
    if converted_corners_key is not None:
        converted = point_list(
            value.get(converted_corners_key),
            f"{path}.{converted_corners_key}",
            errors,
        )
        derived = aabb_from_points(converted) if converted is not None else None
    if declared is not None and derived is not None and not same_aabb(declared, derived):
        source = converted_corners_key or "raw_corners"
        errors.append(f"{path}.{aabb_key} must be derived from {source}")

    if context is not None and expected_producer == EXPECTED_SOURCE_PRODUCER:
        if not non_empty_string(context.get("state_id")):
            errors.append(f"{path}.context.state_id must be non-empty")
        if not non_empty_string(context.get("root_uuid")):
            errors.append(f"{path}.context.root_uuid must be non-empty")
        if not non_empty_string(context.get("three_revision")):
            errors.append(f"{path}.context.three_revision must be non-empty")
        object_count = context.get("object_count")
        if (
            not isinstance(object_count, int)
            or isinstance(object_count, bool)
            or object_count <= 0
        ):
            errors.append(f"{path}.context.object_count must be a positive integer")

    if context is not None and expected_producer == EXPECTED_TARGET_PRODUCER:
        if context.get("coordinate_from") != "view-local-px":
            errors.append(f"{path}.context.coordinate_from must be view-local-px")
        if context.get("coordinate_to") != "spatial-view-local-meters":
            errors.append(
                f"{path}.context.coordinate_to must be spatial-view-local-meters"
            )
        if not non_empty_string(context.get("sdk_version")):
            errors.append(f"{path}.context.sdk_version must be non-empty")
        view_size = vector3(
            context.get("view_size_px"),
            f"{path}.context.view_size_px",
            errors,
        )
        if (
            raw_bounds is not None
            and view_size is not None
            and any(
                not close(view_size[axis], raw_bounds[2][axis])
                for axis in range(3)
            )
        ):
            errors.append(f"{path}.context.view_size_px must match raw_box.size")

    return {
        "aabb": declared,
        "context": context,
    }


def load_probe_file(
    reference: Any,
    base_dir: Path,
    path: str,
    errors: list[str],
) -> tuple[dict[str, Any] | None, Path | None]:
    if not non_empty_string(reference):
        errors.append(f"{path} must be a non-empty JSON file path")
        return None, None
    probe_path = Path(reference)
    if not probe_path.is_absolute():
        probe_path = base_dir / probe_path
    probe_path = probe_path.resolve()
    try:
        value = load_json(probe_path)
    except ValueError as exc:
        errors.append(f"{path} cannot be loaded: {exc}")
        return None, probe_path
    if not isinstance(value, dict):
        errors.append(f"{path} must reference a JSON object")
        return None, probe_path
    return value, probe_path


def parse_axis_mapping(value: Any, errors: list[str]) -> list[tuple[int, int]] | None:
    if not isinstance(value, list) or len(value) != 3:
        errors.append("conversion-contract.scene.axis_mapping must have three entries")
        return None
    parsed: list[tuple[int, int]] = []
    names: list[str] = []
    for index, item in enumerate(value):
        if (
            not isinstance(item, str)
            or len(item) != 2
            or item[0] not in "+-"
            or item[1] not in AXIS_INDEX
        ):
            errors.append(
                f"conversion-contract.scene.axis_mapping[{index}] "
                "must be one of +x, -x, +y, -y, +z, -z"
            )
            continue
        names.append(item[1])
        parsed.append((AXIS_INDEX[item[1]], 1 if item[0] == "+" else -1))
    if len(parsed) != 3:
        return None
    if set(names) != set(AXIS_INDEX):
        errors.append(
            "conversion-contract.scene.axis_mapping must use each source axis once"
        )
        return None
    return parsed


def state_bounds(
    value: Any,
    path: str,
    aabb_key: str,
    errors: list[str],
    *,
    require_evidence: bool,
) -> dict[str, tuple[list[float], list[float], list[float]]]:
    if not isinstance(value, list) or not value:
        errors.append(f"{path} must be a non-empty array")
        return {}
    result: dict[str, tuple[list[float], list[float], list[float]]] = {}
    for index, item in enumerate(value):
        prefix = f"{path}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        state_id = item.get("state_id")
        if not non_empty_string(state_id):
            errors.append(f"{prefix}.state_id must be a non-empty string")
            continue
        if state_id in result:
            errors.append(f"{prefix}.state_id is duplicated: {state_id}")
            continue
        bounds = aabb(
            item.get(aabb_key),
            f"{prefix}.{aabb_key}",
            errors,
            require_volume=False,
        )
        if require_evidence and not non_empty_string_list(item.get("evidence")):
            errors.append(f"{prefix}.evidence must be a non-empty string array")
        if bounds is not None:
            result[state_id] = bounds
    return result


def source_state_bounds(
    value: Any,
    path: str,
    base_dir: Path,
    errors: list[str],
) -> dict[str, tuple[list[float], list[float], list[float]]]:
    if not isinstance(value, list) or not value:
        errors.append(f"{path} must be a non-empty array")
        return {}
    result: dict[str, tuple[list[float], list[float], list[float]]] = {}
    for index, item in enumerate(value):
        prefix = f"{path}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        state_id = item.get("state_id")
        if not non_empty_string(state_id):
            errors.append(f"{prefix}.state_id must be a non-empty string")
            continue
        if state_id in result:
            errors.append(f"{prefix}.state_id is duplicated: {state_id}")
            continue
        bounds = aabb(
            item.get("aabb_source"),
            f"{prefix}.aabb_source",
            errors,
            require_volume=False,
        )
        if not non_empty_string_list(item.get("evidence")):
            errors.append(f"{prefix}.evidence must be a non-empty string array")
        probe_value, _ = load_probe_file(
            item.get("measurement_file"),
            base_dir,
            f"{prefix}.measurement_file",
            errors,
        )
        measurement = (
            probe_measurement(
                probe_value,
                f"{prefix}.measurement",
                errors,
                expected_kind="source-scene-aabb",
                expected_producer=EXPECTED_SOURCE_PRODUCER,
                expected_space=EXPECTED_SOURCE_SPACE,
                aabb_key="aabb_source",
                require_volume=False,
                converted_corners_key=None,
            )
            if probe_value is not None
            else None
        )
        if measurement is not None:
            context = measurement["context"]
            if isinstance(context, dict) and context.get("state_id") != state_id:
                errors.append(f"{prefix}.measurement.context.state_id must match state_id")
            measured_bounds = measurement["aabb"]
            if (
                bounds is not None
                and measured_bounds is not None
                and not same_aabb(bounds, measured_bounds)
            ):
                errors.append(
                    f"{prefix}.aabb_source must match the runtime measurement"
                )
        if bounds is not None:
            result[state_id] = bounds
    return result


def validate_contract(
    contract: Any,
    contract_path: Path,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    profiles: dict[str, dict[str, Any]] = {}
    if not isinstance(contract, dict):
        return ["conversion contract root must be an object"], profiles
    scene = contract.get("scene")
    if not isinstance(scene, dict):
        return ["conversion-contract.scene must be an object"], profiles

    units = scene.get("units_to_meters")
    if not finite_number(units) or units <= 0:
        errors.append("conversion-contract.scene.units_to_meters must be positive")
        units = None
    if not non_empty_string_list(scene.get("unit_evidence")):
        errors.append(
            "conversion-contract.scene.unit_evidence must be a non-empty string array"
        )
    axis_mapping = parse_axis_mapping(scene.get("axis_mapping"), errors)

    spatial_fit = scene.get("spatial_fit")
    if not isinstance(spatial_fit, dict):
        return errors + ["conversion-contract.scene.spatial_fit must be an object"], profiles
    source = source_state_bounds(
        spatial_fit.get("source_bounds"),
        "conversion-contract.scene.spatial_fit.source_bounds",
        contract_path.parent,
        errors,
    )
    raw_profiles = spatial_fit.get("profiles")
    if not isinstance(raw_profiles, list) or not raw_profiles:
        errors.append(
            "conversion-contract.scene.spatial_fit.profiles must be a non-empty array"
        )
        return errors, profiles

    for profile_index, profile in enumerate(raw_profiles):
        prefix = f"conversion-contract.scene.spatial_fit.profiles[{profile_index}]"
        if not isinstance(profile, dict):
            errors.append(f"{prefix} must be an object")
            continue
        profile_id = profile.get("id")
        if not non_empty_string(profile_id):
            errors.append(f"{prefix}.id must be a non-empty string")
            continue
        if profile_id in profiles:
            errors.append(f"{prefix}.id is duplicated: {profile_id}")
            continue

        visible = profile.get("visible_region")
        visible_bounds = None
        if not isinstance(visible, dict):
            errors.append(f"{prefix}.visible_region must be an object")
        else:
            if visible.get("measurement_method") != EXPECTED_MEASUREMENT_METHOD:
                errors.append(
                    f"{prefix}.visible_region.measurement_method must be "
                    f"{EXPECTED_MEASUREMENT_METHOD}"
                )
            if not non_empty_string_list(visible.get("evidence")):
                errors.append(
                    f"{prefix}.visible_region.evidence must be a non-empty string array"
                )
            visible_bounds = aabb(
                visible.get("aabb_m"),
                f"{prefix}.visible_region.aabb_m",
                errors,
                require_volume=True,
            )
            probe_value, measurement_path = load_probe_file(
                visible.get("measurement_file"),
                contract_path.parent,
                f"{prefix}.visible_region.measurement_file",
                errors,
            )
            measurement = (
                probe_measurement(
                    probe_value,
                    f"{prefix}.visible_region.measurement",
                    errors,
                    expected_kind="target-visible-region",
                    expected_producer=EXPECTED_TARGET_PRODUCER,
                    expected_space=EXPECTED_TARGET_SPACE,
                    aabb_key="aabb_m",
                    require_volume=True,
                    converted_corners_key="converted_corners_m",
                )
                if probe_value is not None
                else None
            )
            if measurement is not None:
                context = measurement["context"]
                if isinstance(context, dict) and context.get("profile_id") != profile_id:
                    errors.append(
                        f"{prefix}.visible_region.measurement.context.profile_id "
                        "must match profile id"
                    )
                measured_bounds = measurement["aabb"]
                if (
                    visible_bounds is not None
                    and measured_bounds is not None
                    and not same_aabb(visible_bounds, measured_bounds)
                ):
                    errors.append(
                        f"{prefix}.visible_region.aabb_m must match the runtime "
                        "measurement"
                    )

        usable = profile.get("usable_region")
        usable_bounds = None
        if not isinstance(usable, dict):
            errors.append(f"{prefix}.usable_region must be an object")
        else:
            if not non_empty_string(usable.get("rationale")):
                errors.append(f"{prefix}.usable_region.rationale must be non-empty")
            usable_bounds = aabb(
                usable.get("aabb_m"),
                f"{prefix}.usable_region.aabb_m",
                errors,
                require_volume=True,
            )
            if (
                visible_bounds is not None
                and usable_bounds is not None
                and not contains(visible_bounds, usable_bounds)
            ):
                errors.append(f"{prefix}.usable_region must be inside visible_region")

        fit = profile.get("fit")
        if not isinstance(fit, dict):
            errors.append(f"{prefix}.fit must be an object")
            continue
        reference_state_id = fit.get("reference_state_id")
        if not non_empty_string(reference_state_id):
            errors.append(f"{prefix}.fit.reference_state_id must be non-empty")
        elif reference_state_id not in source:
            errors.append(
                f"{prefix}.fit.reference_state_id must reference source_bounds"
            )
        uniform_scale = fit.get("uniform_scale")
        if not finite_number(uniform_scale) or uniform_scale <= 0:
            errors.append(f"{prefix}.fit.uniform_scale must be positive")
            uniform_scale = None
        translation = vector3(
            fit.get("translation_m"),
            f"{prefix}.fit.translation_m",
            errors,
        )
        if not non_empty_string(fit.get("rationale")):
            errors.append(f"{prefix}.fit.rationale must be non-empty")
        runtime_bounds_policy = fit.get("runtime_bounds_policy", "exact")
        if runtime_bounds_policy not in RUNTIME_BOUNDS_POLICIES:
            errors.append(
                f"{prefix}.fit.runtime_bounds_policy must be one of "
                + ", ".join(sorted(RUNTIME_BOUNDS_POLICIES))
            )
            runtime_bounds_policy = "exact"
        if (
            runtime_bounds_policy == "conservative-contains-expected"
            and not non_empty_string(fit.get("runtime_bounds_rationale"))
        ):
            errors.append(
                f"{prefix}.fit.runtime_bounds_rationale must be non-empty "
                "for conservative-contains-expected"
            )
        target = state_bounds(
            fit.get("state_aabbs_m"),
            f"{prefix}.fit.state_aabbs_m",
            "aabb_m",
            errors,
            require_evidence=False,
        )
        if set(target) != set(source):
            errors.append(
                f"{prefix}.fit.state_aabbs_m must cover every source_bounds state"
            )

        if (
            units is not None
            and uniform_scale is not None
            and axis_mapping is not None
            and translation is not None
        ):
            for state_id, source_aabb in source.items():
                declared = target.get(state_id)
                if declared is None:
                    continue
                minimum: list[float] = []
                maximum: list[float] = []
                factor = float(units) * float(uniform_scale)
                for target_axis, (source_axis, sign) in enumerate(axis_mapping):
                    low = source_aabb[0][source_axis] * factor
                    high = source_aabb[1][source_axis] * factor
                    if sign < 0:
                        low, high = -high, -low
                    minimum.append(low + translation[target_axis])
                    maximum.append(high + translation[target_axis])
                calculated = (
                    minimum,
                    maximum,
                    [maximum[index] - minimum[index] for index in range(3)],
                )
                if not same_aabb(calculated, declared):
                    errors.append(
                        f"{prefix}.fit.state_aabbs_m[{state_id}] does not match "
                        "the source AABB, units, axis mapping, scale, and translation"
                    )
                if visible_bounds is not None and not contains(
                    visible_bounds, declared
                ):
                    errors.append(
                        f"{prefix}.fit.state_aabbs_m[{state_id}] exceeds visible_region"
                    )

            reference = source.get(reference_state_id)
            declared_reference = target.get(reference_state_id)
            if (
                reference is not None
                and usable_bounds is not None
                and declared_reference is not None
            ):
                limits = uniform_scale_limit(
                    reference,
                    usable_bounds,
                    axis_mapping,
                    float(units),
                    translation,
                )
                if visible_bounds is not None:
                    for source_aabb in source.values():
                        limits.extend(
                            uniform_scale_limit(
                                source_aabb,
                                visible_bounds,
                                axis_mapping,
                                float(units),
                                translation,
                            )
                        )
                expected_scale = min(limits) if limits else None
                if expected_scale is None or not close(float(uniform_scale), expected_scale):
                    errors.append(
                        f"{prefix}.fit.uniform_scale must be derived from the "
                        "reference-state usable_region and all-state visible_region"
                    )
                if not contains(usable_bounds, declared_reference):
                    errors.append(
                        f"{prefix}.fit reference state must be inside usable_region"
                    )

        profiles[profile_id] = {
            "visible": visible_bounds,
            "measurement_path": measurement_path if isinstance(visible, dict) else None,
            "states": target,
            "runtime_bounds_policy": runtime_bounds_policy,
        }
    return errors, profiles


def validate_runtime_result(
    result: Any,
    contract_profiles: dict[str, dict[str, Any]],
    result_path: Path,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(result, dict):
        return ["verification result root must be an object"]
    spatial_fit = result.get("spatial_fit")
    if not isinstance(spatial_fit, dict):
        return ["verification-result.spatial_fit must be an object"]
    raw_profiles = spatial_fit.get("profiles")
    if not isinstance(raw_profiles, list) or not raw_profiles:
        return ["verification-result.spatial_fit.profiles must be a non-empty array"]

    seen: set[str] = set()
    for profile_index, profile in enumerate(raw_profiles):
        prefix = f"verification-result.spatial_fit.profiles[{profile_index}]"
        if not isinstance(profile, dict):
            errors.append(f"{prefix} must be an object")
            continue
        profile_id = profile.get("id")
        if not non_empty_string(profile_id):
            errors.append(f"{prefix}.id must be a non-empty string")
            continue
        if profile_id in seen:
            errors.append(f"{prefix}.id is duplicated: {profile_id}")
            continue
        seen.add(profile_id)
        expected = contract_profiles.get(profile_id)
        if expected is None:
            errors.append(f"{prefix}.id is not declared by the conversion contract")
            continue

        visible = profile.get("visible_region")
        runtime_visible = None
        if not isinstance(visible, dict):
            errors.append(f"{prefix}.visible_region must be an object")
        else:
            if visible.get("measurement_method") != EXPECTED_MEASUREMENT_METHOD:
                errors.append(
                    f"{prefix}.visible_region.measurement_method must be "
                    f"{EXPECTED_MEASUREMENT_METHOD}"
                )
            if not non_empty_string_list(visible.get("evidence")):
                errors.append(
                    f"{prefix}.visible_region.evidence must be a non-empty string array"
                )
            runtime_visible = aabb(
                visible.get("aabb_m"),
                f"{prefix}.visible_region.aabb_m",
                errors,
                require_volume=True,
            )
            probe_value, measurement_path = load_probe_file(
                visible.get("measurement_file"),
                result_path.parent,
                f"{prefix}.visible_region.measurement_file",
                errors,
            )
            measurement = (
                probe_measurement(
                    probe_value,
                    f"{prefix}.visible_region.measurement",
                    errors,
                    expected_kind="target-visible-region",
                    expected_producer=EXPECTED_TARGET_PRODUCER,
                    expected_space=EXPECTED_TARGET_SPACE,
                    aabb_key="aabb_m",
                    require_volume=True,
                    converted_corners_key="converted_corners_m",
                )
                if probe_value is not None
                else None
            )
            if measurement is not None:
                context = measurement["context"]
                if isinstance(context, dict) and context.get("profile_id") != profile_id:
                    errors.append(
                        f"{prefix}.visible_region.measurement.context.profile_id "
                        "must match profile id"
                    )
                measured_bounds = measurement["aabb"]
                if (
                    runtime_visible is not None
                    and measured_bounds is not None
                    and not same_aabb(runtime_visible, measured_bounds)
                ):
                    errors.append(
                        f"{prefix}.visible_region.aabb_m must match the runtime "
                        "measurement"
                    )
            if (
                measurement_path is not None
                and expected["measurement_path"] is not None
                and measurement_path == expected["measurement_path"]
            ):
                errors.append(
                    f"{prefix}.visible_region.measurement_file must be a fresh "
                    "runtime capture, not the contract measurement"
                )
            if (
                runtime_visible is not None
                and expected["visible"] is not None
                and not same_aabb(runtime_visible, expected["visible"])
            ):
                errors.append(
                    f"{prefix}.visible_region differs from the frozen contract"
                )

        raw_states = profile.get("states")
        states = state_bounds(
            raw_states,
            f"{prefix}.states",
            "measured_aabb_m",
            errors,
            require_evidence=True,
        )
        expected_states = expected["states"]
        if set(states) != set(expected_states):
            errors.append(f"{prefix}.states must cover every contracted fit state")
        for state_index, state in enumerate(
            raw_states if isinstance(raw_states, list) else []
        ):
            if not isinstance(state, dict):
                continue
            state_id = state.get("state_id")
            if state.get("clipped") is not False:
                errors.append(
                    f"{prefix}.states[{state_index}].clipped must be false"
                )
            measured = states.get(state_id)
            planned = expected_states.get(state_id)
            if measured is None:
                continue
            if runtime_visible is not None and not contains(runtime_visible, measured):
                errors.append(
                    f"{prefix}.states[{state_index}].measured_aabb_m "
                    "exceeds the runtime visible_region"
                )
            if planned is not None:
                policy = expected["runtime_bounds_policy"]
                if policy == "exact" and not same_aabb(measured, planned):
                    errors.append(
                        f"{prefix}.states[{state_index}].measured_aabb_m "
                        "differs from the frozen fit"
                    )
                if (
                    policy == "conservative-contains-expected"
                    and not contains(measured, planned)
                ):
                    errors.append(
                        f"{prefix}.states[{state_index}].measured_aabb_m "
                        "must contain the frozen fit under "
                        "conservative-contains-expected"
                    )

    missing_profiles = sorted(set(contract_profiles) - seen)
    if missing_profiles:
        errors.append(
            "verification-result.spatial_fit is missing profiles: "
            + ", ".join(missing_profiles)
        )
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Spatial region probe artifacts and scene fit; "
            "this command does not measure the runtime."
        )
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--verification-result", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        contract = load_json(args.contract)
        verification_result = (
            load_json(args.verification_result)
            if args.verification_result is not None
            else None
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors, profiles = validate_contract(contract, args.contract)
    if verification_result is not None and not errors:
        errors.extend(
            validate_runtime_result(
                verification_result,
                profiles,
                args.verification_result,
            )
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "valid": True,
                "profile_count": len(profiles),
                "state_count": sum(
                    len(profile["states"]) for profile in profiles.values()
                ),
                "runtime_validated": verification_result is not None,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
