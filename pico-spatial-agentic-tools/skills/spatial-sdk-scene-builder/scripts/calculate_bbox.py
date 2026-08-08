#!/usr/bin/env python3

import sys
import os
import argparse
import gzip
import struct

TRIMESH_EXTENSIONS = {".glb", ".gltf", ".obj", ".stl"}
USD_EXTENSIONS = {".usdz"}
SPZ_EXTENSIONS = {".spz"}
SUPPORTED_EXTENSIONS = TRIMESH_EXTENSIONS | USD_EXTENSIONS | SPZ_EXTENSIONS
SPZ_HEADER_SIZE = 16
SPZ_MAGIC = 0x5053474E
SPZ_MAX_POINTS = 10_000_000


def missing_dependency_message(dependency_name):
    return (
        f"Missing dependency '{dependency_name}'. Install script dependencies with: "
        "pip3 install -r ./skills/spatial-sdk-scene-builder/scripts/requirements.txt"
    )


def calculate_bbox_trimesh(file_path):
    try:
        try:
            import trimesh
        except ModuleNotFoundError as e:
            raise RuntimeError(missing_dependency_message(e.name or "trimesh")) from e

        scene = trimesh.load(file_path, force="scene")
        bounds = scene.bounds

        if bounds is None:
            raise ValueError("Could not compute bounding box. Model might be empty.")

        min_bounds = bounds[0]
        max_bounds = bounds[1]

        width = max_bounds[0] - min_bounds[0]
        height = max_bounds[1] - min_bounds[1]
        depth = max_bounds[2] - min_bounds[2]

        return {
            "min": [float(min_bounds[0]), float(min_bounds[1]), float(min_bounds[2])],
            "max": [float(max_bounds[0]), float(max_bounds[1]), float(max_bounds[2])],
            "dimensions": {"width": float(width), "height": float(height), "depth": float(depth)},
        }
    except Exception as e:
        raise RuntimeError(f"Failed to extract bounding box: {str(e)}")


def calculate_bbox_usd(file_path):
    try:
        try:
            from pxr import Usd, UsdGeom
        except ModuleNotFoundError as e:
            raise RuntimeError(missing_dependency_message("usd-core")) from e

        stage = Usd.Stage.Open(file_path)
        if not stage:
            raise ValueError(f"Failed to open USD file: {file_path}")

        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default", "proxy", "render"])
        root_prim = stage.GetPseudoRoot()
        bound = bbox_cache.ComputeWorldBound(root_prim)

        # bound is a Gf.BBox3d, bound.ComputeAlignedRange() returns a Gf.Range3d
        aligned_range = bound.ComputeAlignedRange()

        if aligned_range.IsEmpty():
            raise ValueError("Could not compute bounding box. Model might be empty.")

        min_bounds = aligned_range.GetMin()
        max_bounds = aligned_range.GetMax()

        width = max_bounds[0] - min_bounds[0]
        height = max_bounds[1] - min_bounds[1]
        depth = max_bounds[2] - min_bounds[2]

        return {
            "min": [float(min_bounds[0]), float(min_bounds[1]), float(min_bounds[2])],
            "max": [float(max_bounds[0]), float(max_bounds[1]), float(max_bounds[2])],
            "dimensions": {"width": float(width), "height": float(height), "depth": float(depth)},
        }
    except Exception as e:
        raise RuntimeError(f"Failed to extract bounding box: {str(e)}")


def read_spz_signed_int24(data, offset):
    value = data[offset] | (data[offset + 1] << 8) | (data[offset + 2] << 16)
    if value & 0x800000:
        value -= 0x1000000
    return value


def calculate_bbox_spz(file_path):
    try:
        with gzip.open(file_path, "rb") as spz_file:
            data = spz_file.read()

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
            raise ValueError("Could not compute bounding box. SPZ has no points.")
        if num_points > SPZ_MAX_POINTS:
            raise ValueError(f"SPZ has too many points: {num_points}.")

        position_bytes_per_point = 9
        positions_size = num_points * position_bytes_per_point
        positions_end = SPZ_HEADER_SIZE + positions_size
        if len(data) < positions_end:
            raise ValueError("SPZ payload is truncated before the positions array ends.")

        scale = 1.0 / (1 << fractional_bits)
        min_bounds = [float("inf"), float("inf"), float("inf")]
        max_bounds = [float("-inf"), float("-inf"), float("-inf")]

        for point_index in range(num_points):
            point_offset = SPZ_HEADER_SIZE + point_index * position_bytes_per_point
            for axis in range(3):
                component_offset = point_offset + axis * 3
                value = read_spz_signed_int24(data, component_offset) * scale
                min_bounds[axis] = min(min_bounds[axis], value)
                max_bounds[axis] = max(max_bounds[axis], value)

        width = max_bounds[0] - min_bounds[0]
        height = max_bounds[1] - min_bounds[1]
        depth = max_bounds[2] - min_bounds[2]

        return {
            "min": [float(min_bounds[0]), float(min_bounds[1]), float(min_bounds[2])],
            "max": [float(max_bounds[0]), float(max_bounds[1]), float(max_bounds[2])],
            "dimensions": {"width": float(width), "height": float(height), "depth": float(depth)},
        }
    except Exception as e:
        raise RuntimeError(f"Failed to extract bounding box: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract the bounding box dimensions from a 3D model file"
    )
    parser.add_argument("file_path", help="Absolute or relative path to the 3D model file")

    args = parser.parse_args()
    file_path = args.file_path

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        print(f"Error: Unsupported file format: {ext}. Supported formats: {supported}.")
        sys.exit(1)

    print(f"Parsing {ext} file: {file_path}")

    try:
        if ext in TRIMESH_EXTENSIONS:
            bbox = calculate_bbox_trimesh(file_path)
        elif ext in USD_EXTENSIONS:
            bbox = calculate_bbox_usd(file_path)
        elif ext in SPZ_EXTENSIONS:
            bbox = calculate_bbox_spz(file_path)
        else:
            raise RuntimeError(f"Unsupported file format: {ext}")

        print("Bounding Box Data:")

        min_vals = bbox["min"]
        max_vals = bbox["max"]

        print(f"Min: [{', '.join(f'{x:.4f}' for x in min_vals)}]")
        print(f"Max: [{', '.join(f'{x:.4f}' for x in max_vals)}]")

        dims = bbox["dimensions"]
        print(
            f"Dimensions: Width={dims['width']:.4f}, Height={dims['height']:.4f}, Depth={dims['depth']:.4f}"
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
