#!/usr/bin/env python3
"""Validate a processed Unity Android export and compare verification APKs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Optional


ARM64_MACHINE = 183
MIN_16K_ALIGNMENT = 0x4000


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_properties(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")) or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def is_elf64_aarch64(path: Path) -> tuple[bool, str]:
    header = path.read_bytes()[:20]
    if len(header) < 20 or header[:4] != b"\x7fELF":
        return False, "not an ELF file"
    if header[4] != 2:
        return False, f"ELF class is {header[4]}, expected ELF64"
    if header[5] != 1:
        return False, f"ELF data encoding is {header[5]}, expected little-endian"
    machine = int.from_bytes(header[18:20], "little")
    if machine != ARM64_MACHINE:
        return False, f"ELF machine is {machine}, expected AArch64 ({ARM64_MACHINE})"
    return True, "ELF64 AArch64"


def add_error(result: dict[str, Any], message: str) -> None:
    result["errors"].append(message)


def add_warning(result: dict[str, Any], message: str) -> None:
    result["warnings"].append(message)


def validate_project(project: Path, manifest_path: Path, result: dict[str, Any]) -> None:
    required = [
        project / "settings.gradle",
        project / "launcher" / "build.gradle",
        project / "unityLibrary" / "build.gradle",
        project / "gradle.properties",
        manifest_path,
    ]
    for path in required:
        if not path.is_file():
            add_error(result, f"Required file is missing: {path}")

    if result["errors"]:
        return

    forbidden_files: list[str] = []
    forbidden_dirs = {
        "build",
        ".gradle",
        ".cxx",
        "Il2CppOutputProject",
        "symbols",
    }
    forbidden_suffixes = {".apk", ".aab", ".keystore", ".jks"}
    for path in project.rglob("*"):
        relative = path.relative_to(project)
        if ".git" in relative.parts:
            continue
        if path.is_dir() and (
            path.name in forbidden_dirs
            or path.name.endswith("_BurstDebugInformation_DoNotShip")
        ):
            forbidden_files.append(str(relative))
        elif path.is_file() and (
            path.name == "local.properties" or path.suffix.lower() in forbidden_suffixes
        ):
            forbidden_files.append(str(relative))
    if forbidden_files:
        add_error(
            result,
            "Processed project contains forbidden outputs: "
            + ", ".join(sorted(forbidden_files)[:20]),
        )

    library_gradle = (project / "unityLibrary" / "build.gradle").read_text(
        encoding="utf-8-sig"
    )
    if not re.search(r"jni\.srcDirs\s*=\s*\[\s*\]", library_gradle):
        add_error(result, "unityLibrary/build.gradle does not clear jni.srcDirs")
    if not re.search(
        r"tasks\.named\(['\"]buildIl2Cpp['\"]\)"
        r"\.configure\s*\{\s*enabled\s*=\s*false\s*\}",
        library_gradle,
    ):
        add_error(result, "unityLibrary/build.gradle does not disable buildIl2Cpp")
    if "tasks.register('buildIl2Cpp')" not in library_gradle and (
        'tasks.register("buildIl2Cpp")' not in library_gradle
    ):
        add_error(result, "The original buildIl2Cpp task body is missing")

    properties = parse_properties(project / "gradle.properties")
    for key in ("unityProjectPath", "unity.projectPath"):
        if properties.get(key, ""):
            add_error(result, f"{key} must be empty in gradle.properties")
    if properties.get("unity.abiFilters") != "arm64-v8a":
        add_error(result, "unity.abiFilters must be arm64-v8a")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        add_error(result, f"Cannot parse {manifest_path}: {error}")
        return

    application_id = properties.get("unity.applicationId")
    if manifest.get("application_id") != application_id:
        add_error(
            result,
            "Manifest application_id does not match gradle.properties "
            f"({manifest.get('application_id')} != {application_id})",
        )

    launcher_gradle = (project / "launcher" / "build.gradle").read_text(
        encoding="utf-8-sig"
    )
    application_match = re.search(
        r"\bapplicationId\s+[\"']([^\"']+)[\"']", launcher_gradle
    )
    if not application_match or application_match.group(1) != application_id:
        add_error(result, "launcher applicationId does not match gradle.properties")

    native_dir = project / "unityLibrary" / "src" / "main" / "jniLibs" / "arm64-v8a"
    actual_libraries = {
        path.name: sha256_file(path) for path in sorted(native_dir.glob("*.so"))
    }
    expected_libraries = {
        item["name"]: item["sha256"]
        for item in manifest.get("native_inventory", [])
        if "name" in item and "sha256" in item
    }
    if actual_libraries != expected_libraries:
        add_error(result, "jniLibs inventory does not match .vibelab-prebuilt.json")

    for path in sorted(native_dir.glob("*.so")):
        valid, detail = is_elf64_aarch64(path)
        if not valid:
            add_error(result, f"{path.name}: {detail}")

    il2cpp_path = native_dir / "libil2cpp.so"
    if not il2cpp_path.is_file():
        add_error(result, "libil2cpp.so is missing from arm64-v8a jniLibs")
    elif manifest.get("il2cpp_so_sha256") != sha256_file(il2cpp_path):
        add_error(result, "libil2cpp.so hash does not match the manifest")

    metadata_files = [
        path
        for path in project.rglob("global-metadata.dat")
        if ".git" not in path.relative_to(project).parts
    ]
    if len(metadata_files) != 1:
        add_error(
            result,
            f"Expected one global-metadata.dat, found {len(metadata_files)}",
        )
    elif manifest.get("global_metadata_sha256") != sha256_file(metadata_files[0]):
        add_error(result, "global-metadata.dat hash does not match the manifest")

    result["project"] = {
        "path": str(project),
        "application_id": application_id,
        "native_library_count": len(actual_libraries),
        "il2cpp_sha256": actual_libraries.get("libil2cpp.so"),
        "manifest": str(manifest_path),
    }


def apk_inventory(apk: Path) -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(apk) as archive:
        for info in archive.infolist():
            match = re.fullmatch(r"lib/arm64-v8a/([^/]+\.so)", info.filename)
            if not match:
                continue
            content = archive.read(info)
            inventory[match.group(1)] = {
                "sha256": hashlib.sha256(content).hexdigest(),
                "size": len(content),
                "compressed": info.compress_type != zipfile.ZIP_STORED,
            }
    return inventory


def run_zipalign(zipalign: Path, apk: Path) -> tuple[bool, str]:
    completed = subprocess.run(
        [str(zipalign), "-c", "-P", "16", "-v", "4", str(apk)],
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    return completed.returncode == 0, output.strip()


def read_load_alignment(readelf: Path, library: Path) -> Optional[int]:
    completed = subprocess.run(
        [str(readelf), "-lW", str(library)],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    alignments: list[int] = []
    for line in completed.stdout.splitlines():
        fields = line.split()
        if fields and fields[0] == "LOAD":
            try:
                alignments.append(int(fields[-1], 16))
            except ValueError:
                continue
    return min(alignments) if alignments else None


def inspect_apk(
    apk: Path,
    zipalign: Optional[Path],
    readelf: Optional[Path],
    page_size_policy: str,
    result: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    if not apk.is_file():
        add_error(result, f"APK is missing: {apk}")
        return {}
    try:
        inventory = apk_inventory(apk)
    except (OSError, zipfile.BadZipFile) as error:
        add_error(result, f"Cannot inspect APK {apk}: {error}")
        return {}
    if not inventory:
        add_error(result, f"APK has no arm64-v8a native libraries: {apk}")
        return inventory

    if zipalign:
        if not zipalign.is_file():
            add_error(result, f"zipalign is missing: {zipalign}")
        else:
            aligned, output = run_zipalign(zipalign, apk)
            if not aligned:
                add_error(result, f"zipalign validation failed for {apk}: {output}")

    alignments: dict[str, str] = {}
    if readelf:
        if not readelf.is_file():
            add_error(result, f"llvm-readelf is missing: {readelf}")
        else:
            with tempfile.TemporaryDirectory(prefix="vibelab-apk-") as temp_dir:
                temp_root = Path(temp_dir)
                with zipfile.ZipFile(apk) as archive:
                    for name in sorted(inventory):
                        entry = f"lib/arm64-v8a/{name}"
                        extracted = temp_root / name
                        extracted.write_bytes(archive.read(entry))
                        valid, detail = is_elf64_aarch64(extracted)
                        if not valid:
                            add_error(result, f"{apk.name}/{name}: {detail}")
                            continue
                        alignment = read_load_alignment(readelf, extracted)
                        if alignment is None:
                            add_error(
                                result,
                                f"Could not read LOAD alignment for {apk.name}/{name}",
                            )
                            continue
                        alignments[name] = hex(alignment)
                        if alignment < MIN_16K_ALIGNMENT:
                            message = (
                                f"{apk.name}/{name} has LOAD alignment "
                                f"{hex(alignment)}, below 0x4000"
                            )
                            if page_size_policy == "fail":
                                add_error(result, message)
                            else:
                                add_warning(result, message)

    result.setdefault("apks", {})[str(apk)] = {
        "native_library_count": len(inventory),
        "native_inventory": inventory,
        "load_alignments": alignments,
    }
    return inventory


def validate_gradle_log(path: Path, result: dict[str, Any]) -> None:
    if not path.is_file():
        add_error(result, f"Gradle verification log is missing: {path}")
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(r":unityLibrary:buildIl2Cpp\s+SKIPPED", text):
        add_error(result, "Final Gradle log does not show buildIl2Cpp SKIPPED")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, help="Processed Gradle project")
    parser.add_argument("--manifest", type=Path, help="Prebuilt manifest path")
    parser.add_argument("--before-apk", type=Path)
    parser.add_argument("--after-apk", type=Path)
    parser.add_argument("--expected-il2cpp", help="Expected libil2cpp.so SHA-256")
    parser.add_argument("--zipalign", type=Path)
    parser.add_argument("--readelf", type=Path)
    parser.add_argument("--gradle-log", type=Path)
    parser.add_argument(
        "--page-size-policy", choices=("warn", "fail"), default="warn"
    )
    parser.add_argument("--json-output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result: dict[str, Any] = {"errors": [], "warnings": []}

    if not args.project and not args.before_apk and not args.after_apk:
        add_error(result, "Provide --project and/or APK paths")

    if args.project:
        project = args.project.resolve()
        manifest = (
            args.manifest.resolve()
            if args.manifest
            else project / ".vibelab-prebuilt.json"
        )
        validate_project(project, manifest, result)

    before_inventory: dict[str, dict[str, Any]] = {}
    after_inventory: dict[str, dict[str, Any]] = {}
    if args.before_apk:
        before_inventory = inspect_apk(
            args.before_apk.resolve(),
            args.zipalign.resolve() if args.zipalign else None,
            args.readelf.resolve() if args.readelf else None,
            args.page_size_policy,
            result,
        )
    if args.after_apk:
        after_inventory = inspect_apk(
            args.after_apk.resolve(),
            args.zipalign.resolve() if args.zipalign else None,
            args.readelf.resolve() if args.readelf else None,
            args.page_size_policy,
            result,
        )
    if args.before_apk and args.after_apk and before_inventory != after_inventory:
        add_error(result, "Before/after APK native inventories differ")

    if args.expected_il2cpp:
        expected = args.expected_il2cpp.lower()
        for label, inventory in (
            ("before APK", before_inventory),
            ("after APK", after_inventory),
        ):
            if inventory and inventory.get("libil2cpp.so", {}).get("sha256") != expected:
                add_error(result, f"{label} libil2cpp.so hash differs from baseline")

    if args.gradle_log:
        validate_gradle_log(args.gradle_log.resolve(), result)

    result["ok"] = not result["errors"]
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
