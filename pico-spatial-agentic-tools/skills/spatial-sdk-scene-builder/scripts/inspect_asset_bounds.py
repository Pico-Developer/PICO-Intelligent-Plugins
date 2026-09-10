#!/usr/bin/env python3
"""Inspect source-coordinate bounds and format-provided spatial metadata."""

from __future__ import annotations

import argparse
import gzip
import json
import math
import struct
import sys
from pathlib import Path
from typing import Any, Iterable, Optional


TRIMESH_EXTENSIONS = {".glb", ".gltf", ".obj", ".stl"}
USD_EXTENSIONS = {".usd", ".usda", ".usdc", ".usdz"}
SPZ_EXTENSIONS = {".spz"}
SUPPORTED_EXTENSIONS = TRIMESH_EXTENSIONS | USD_EXTENSIONS | SPZ_EXTENSIONS
SUPPORTED_FORMATS_TEXT = ", ".join(sorted(SUPPORTED_EXTENSIONS))

SPZ_HEADER_SIZE = 16
SPZ_MAGIC = 0x5053474E
SPZ_MAX_POINTS = 10_000_000
AXIS_NAMES = ("x", "y", "z")


def missing_dependency_message(dependency_name: str) -> str:
    requirements_path = Path(__file__).resolve().with_name("requirements.txt")
    return (
        f"Missing dependency '{dependency_name}'. Install script dependencies with: "
        f"pip3 install -r {requirements_path}"
    )


def finite_vector(values: Iterable[Any], label: str) -> list[float]:
    result = [float(value) for value in values]
    if len(result) != 3 or not all(math.isfinite(value) for value in result):
        raise ValueError(f"{label} must contain three finite values.")
    return result


def axis_values(values: list[float]) -> dict[str, float]:
    return dict(zip(AXIS_NAMES, values))


def build_result(
    *,
    asset_path: Path,
    min_bounds: Iterable[Any],
    max_bounds: Iterable[Any],
    unit_status: str,
    unit_evidence: str,
    meters_per_unit: Optional[float] = None,
    up_axis: Optional[str] = None,
    up_axis_status: str = "unknown",
    up_axis_evidence: str = "The source format did not establish an up axis.",
    limitations: Iterable[str] = (),
) -> dict[str, Any]:
    minimum = finite_vector(min_bounds, "minimum bounds")
    maximum = finite_vector(max_bounds, "maximum bounds")
    extents = [maximum[index] - minimum[index] for index in range(3)]

    if any(extent < 0 or not math.isfinite(extent) for extent in extents):
        raise ValueError("Bounding-box extents must be finite and non-negative.")
    if not any(extent > 0 for extent in extents):
        raise ValueError("Could not compute bounds: the asset has no non-zero extent.")

    limitation_list = list(limitations)
    normalized_up_axis = up_axis.upper() if up_axis else None
    if normalized_up_axis not in (None, "Y", "Z"):
        limitation_list.append(
            f"Unsupported up axis '{normalized_up_axis}'; native height is unresolved.",
        )

    normalized_meters_per_unit: Optional[float] = None
    meter_extents: Optional[list[float]] = None
    native_height_meters: Optional[float] = None
    height_axis: Optional[str] = None

    if meters_per_unit is not None:
        normalized_meters_per_unit = float(meters_per_unit)
        if not math.isfinite(normalized_meters_per_unit) or normalized_meters_per_unit <= 0:
            raise ValueError("metersPerUnit must be positive and finite.")
        meter_extents = [extent * normalized_meters_per_unit for extent in extents]

        if normalized_up_axis in ("Y", "Z"):
            height_index = 1 if normalized_up_axis == "Y" else 2
            height_axis = normalized_up_axis.lower()
            candidate_height = meter_extents[height_index]
            if candidate_height > 0 and math.isfinite(candidate_height):
                native_height_meters = candidate_height
            else:
                limitation_list.append(
                    f"The {normalized_up_axis}-axis extent is not positive; native height is unresolved."
                )

    return {
        "schema_version": 1,
        "asset": {
            "path": str(asset_path.resolve()),
            "format": asset_path.suffix.lower().lstrip("."),
        },
        "bounds": {
            "space": "source_coordinates",
            "min": axis_values(minimum),
            "max": axis_values(maximum),
            "extents": axis_values(extents),
        },
        "axis_metadata": {
            "up_axis": normalized_up_axis,
            "height_axis": height_axis,
            "status": up_axis_status,
            "evidence": up_axis_evidence,
        },
        "unit_metadata": {
            "status": unit_status,
            "meters_per_unit": normalized_meters_per_unit,
            "evidence": unit_evidence,
        },
        "meter_extents": axis_values(meter_extents) if meter_extents else None,
        "native_height_meters": native_height_meters,
        "limitations": limitation_list,
    }


def inspect_trimesh(asset_path: Path) -> dict[str, Any]:
    try:
        import trimesh
    except ModuleNotFoundError as error:
        raise RuntimeError(missing_dependency_message(error.name or "trimesh")) from error

    try:
        scene = trimesh.load(str(asset_path), force="scene")
        bounds = scene.bounds
    except Exception as error:
        raise RuntimeError(f"Failed to inspect mesh bounds: {error}") from error

    if bounds is None:
        raise ValueError("Could not compute bounds. The asset may be empty.")

    extension = asset_path.suffix.lower()
    if extension in {".glb", ".gltf"}:
        return build_result(
            asset_path=asset_path,
            min_bounds=bounds[0],
            max_bounds=bounds[1],
            unit_status="verified",
            unit_evidence="The glTF format defines linear distances in meters.",
            meters_per_unit=1.0,
            up_axis="Y",
            up_axis_status="verified",
            up_axis_evidence="The glTF format defines a Y-up coordinate system.",
            limitations=(
                "Source bounds do not replace final Spatial SDK Entity visual bounds.",
                "Model-forward direction and pivot semantics are not inferred.",
            ),
        )

    return build_result(
        asset_path=asset_path,
        min_bounds=bounds[0],
        max_bounds=bounds[1],
        unit_status="unknown",
        unit_evidence=f"The {extension} format does not establish physical units.",
        limitations=(
            "Obtain exporter, sidecar, or accepted project evidence before treating extents as meters.",
            "Source bounds do not replace final Spatial SDK Entity visual bounds.",
            "Up axis, model-forward direction, and pivot semantics are not inferred.",
        ),
    )


def inspect_usd(asset_path: Path) -> dict[str, Any]:
    try:
        from pxr import Usd, UsdGeom
    except ModuleNotFoundError as error:
        raise RuntimeError(missing_dependency_message("usd-core")) from error

    try:
        stage = Usd.Stage.Open(str(asset_path))
        if not stage:
            raise ValueError("The composed USD stage could not be opened.")

        bbox_cache = UsdGeom.BBoxCache(
            Usd.TimeCode.Default(),
            ["default", "proxy", "render"],
            True,
        )
        aligned_range = bbox_cache.ComputeWorldBound(stage.GetPseudoRoot()).ComputeAlignedRange()
        if aligned_range.IsEmpty():
            raise ValueError("Could not compute bounds. The composed stage may be empty.")

        minimum = aligned_range.GetMin()
        maximum = aligned_range.GetMax()
        meters_per_unit = float(UsdGeom.GetStageMetersPerUnit(stage))
        up_axis = str(UsdGeom.GetStageUpAxis(stage)).upper()
        meters_authored = bool(stage.HasAuthoredMetadata("metersPerUnit"))
        up_axis_authored = bool(stage.HasAuthoredMetadata("upAxis"))
    except Exception as error:
        raise RuntimeError(f"Failed to inspect composed USD stage: {error}") from error

    return build_result(
        asset_path=asset_path,
        min_bounds=minimum,
        max_bounds=maximum,
        unit_status="verified" if meters_authored else "defaulted",
        unit_evidence=(
            "metersPerUnit is authored on the composed USD stage."
            if meters_authored
            else "metersPerUnit is the effective USD schema default because it is not authored."
        ),
        meters_per_unit=meters_per_unit,
        up_axis=up_axis,
        up_axis_status="verified" if up_axis_authored else "defaulted",
        up_axis_evidence=(
            "upAxis is authored on the composed USD stage."
            if up_axis_authored
            else "upAxis is the effective USD schema default because it is not authored."
        ),
        limitations=(
            "Source-stage bounds do not replace final Spatial SDK Entity visual bounds.",
            "Editor-instance transforms, model-forward direction, and pivot semantics are not inferred.",
        ),
    )


def read_spz_signed_int24(data: bytes, offset: int) -> int:
    value = data[offset] | (data[offset + 1] << 8) | (data[offset + 2] << 16)
    if value & 0x800000:
        value -= 0x1000000
    return value


def inspect_spz(asset_path: Path) -> dict[str, Any]:
    try:
        with gzip.open(asset_path, "rb") as spz_file:
            data = spz_file.read()
    except Exception as error:
        raise RuntimeError(f"Failed to read SPZ payload: {error}") from error

    if len(data) < SPZ_HEADER_SIZE:
        raise ValueError("SPZ payload is shorter than the 16-byte header.")

    magic, version, num_points, sh_degree, fractional_bits, flags, reserved = struct.unpack(
        "<IIIBBBB", data[:SPZ_HEADER_SIZE]
    )
    if magic != SPZ_MAGIC:
        raise ValueError("Invalid SPZ magic number.")
    if version not in (2, 3):
        raise ValueError(f"Unsupported SPZ version: {version}.")
    if sh_degree > 3:
        raise ValueError(f"Unsupported SPZ spherical harmonics degree: {sh_degree}.")
    if flags & ~0x01:
        raise ValueError(f"Unsupported SPZ flags: {flags}.")
    if reserved != 0:
        raise ValueError("Invalid SPZ reserved header byte.")
    if num_points <= 0:
        raise ValueError("Could not compute bounds. SPZ has no points.")
    if num_points > SPZ_MAX_POINTS:
        raise ValueError(f"SPZ has too many points: {num_points}.")

    position_bytes_per_point = 9
    positions_end = SPZ_HEADER_SIZE + num_points * position_bytes_per_point
    if len(data) < positions_end:
        raise ValueError("SPZ payload is truncated before the positions array ends.")

    fixed_point_scale = 1.0 / (1 << fractional_bits)
    minimum = [float("inf"), float("inf"), float("inf")]
    maximum = [float("-inf"), float("-inf"), float("-inf")]

    for point_index in range(num_points):
        point_offset = SPZ_HEADER_SIZE + point_index * position_bytes_per_point
        for axis in range(3):
            component_offset = point_offset + axis * 3
            value = read_spz_signed_int24(data, component_offset) * fixed_point_scale
            minimum[axis] = min(minimum[axis], value)
            maximum[axis] = max(maximum[axis], value)

    return build_result(
        asset_path=asset_path,
        min_bounds=minimum,
        max_bounds=maximum,
        unit_status="unknown",
        unit_evidence="The SPZ payload does not establish a physical meter conversion.",
        limitations=(
            "Bounds include point centers only and do not expand Gaussian radii.",
            "Obtain radius-aware runtime visual bounds before claiming rendered containment or non-overlap.",
            "Up axis, model-forward direction, and pivot semantics are not inferred.",
        ),
    )


def inspect_asset(asset_path: Path) -> dict[str, Any]:
    if not asset_path.exists():
        raise FileNotFoundError(f"Asset not found: {asset_path}")
    if not asset_path.is_file():
        raise ValueError(f"Asset path is not a file: {asset_path}")

    extension = asset_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported asset format '{extension}'. Supported formats: {SUPPORTED_FORMATS_TEXT}."
        )

    if extension in TRIMESH_EXTENSIONS:
        return inspect_trimesh(asset_path)
    if extension in USD_EXTENSIONS:
        return inspect_usd(asset_path)
    return inspect_spz(asset_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect source-coordinate bounds and format-provided spatial metadata."
    )
    parser.add_argument(
        "asset_path",
        type=Path,
        help=f"Absolute or relative 3D asset path. Supported formats: {SUPPORTED_FORMATS_TEXT}.",
    )
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()

    try:
        result = inspect_asset(args.asset_path.expanduser())
    except Exception as error:
        json.dump(
            {
                "schema_version": 1,
                "error": {
                    "asset_path": str(args.asset_path),
                    "message": str(error),
                },
            },
            sys.stderr,
            indent=None if args.compact else 2,
            sort_keys=True,
        )
        sys.stderr.write("\n")
        return 1

    json.dump(result, sys.stdout, indent=None if args.compact else 2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
