#!/usr/bin/env python3
"""Atomically finalize .pico-cli/config.json after successful initialization."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--project-name", required=True)
    parser.add_argument(
        "--mode", required=True, choices=("picoxr", "openxr", "picospatial")
    )
    parser.add_argument("--unity-version", required=True)
    parser.add_argument("--device", action="append", dest="devices", required=True)
    parser.add_argument("--business-type", required=True, choices=("toB", "toC"))
    return parser.parse_args()


def read_existing_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}

    with config_path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)

    if not isinstance(config, dict):
        raise ValueError(f"{config_path} must contain a JSON object")

    return config


def write_atomic(config_path: Path, config: dict[str, Any]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=config_path.parent,
            prefix=f".{config_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            json.dump(config, temp_file, ensure_ascii=False, indent=2)
            temp_file.write("\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = Path(temp_file.name)
        os.replace(temp_path, config_path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def main() -> None:
    args = parse_args()
    config_path = args.project_root.resolve() / ".pico-cli" / "config.json"
    config = read_existing_config(config_path)
    config.pop("sdk", None)
    config.update(
        {
            "project_name": args.project_name,
            "mode": args.mode,
            "unity_version": args.unity_version,
            "platform": "android",
            "devices": args.devices,
            "business_type": args.business_type,
            "pico_unity_init_completed": True,
        }
    )
    write_atomic(config_path, config)
    print(config_path)


if __name__ == "__main__":
    main()
