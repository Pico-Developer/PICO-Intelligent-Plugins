#!/usr/bin/env python3
"""Fail when active Kotlin experimental opt-ins lack the application runtime gate."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ANDROID_NAMESPACE = "http://schemas.android.com/apk/res/android"
EXPERIMENTAL_META_NAME = "pico.spatial.use_experimental_api"
PICO_SPATIAL_PACKAGE = "com.pico.spatial."
EXPERIMENTAL_MARKER_PATTERN = re.compile(r"Experimental[A-Za-z0-9_]*\Z")
IMPORT_PATTERN = re.compile(
    r"^\s*import\s+"
    r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:\.\*)?)"
    r"(?:\s+as\s+([A-Za-z_]\w*))?\s*$",
    re.MULTILINE,
)
OPT_IN_USE_SITE_TARGETS = (
    "file",
    "property",
    "field",
    "get",
    "set",
    "receiver",
    "param",
    "setparam",
    "delegate",
)
OPT_IN_PATTERN = re.compile(
    r"@(?:(?:" + "|".join(OPT_IN_USE_SITE_TARGETS) + r")\s*:\s*)?"
    r"(?:kotlin\.)?OptIn\s*\("
)
APPLICATION_PLUGIN_PATTERN = re.compile(
    r"""(?x)
    (?:
        apply\s+plugin\s*:\s*['"]com\.android\.application['"]
      | id\s*\(?\s*['"]com\.android\.application['"]
    )
    """
)
LIBRARY_PLUGIN_PATTERN = re.compile(
    r"""(?x)
    (?:
        apply\s+plugin\s*:\s*['"]com\.android\.library['"]
      | id\s*\(?\s*['"]com\.android\.library['"]
    )
    """
)
MODULE_DEPENDENCY_PATTERN = re.compile(
    r"""project\s*\(\s*['"]:([A-Za-z0-9_.\-]+)['"]"""
)
CLASS_REFERENCE_PATTERN = re.compile(
    r"\b((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*)\s*::\s*class\b"
)
GRADLE_OPT_IN_PATTERN = re.compile(
    r"-(?:X)?opt-in=("
    r"com\.pico\.spatial\.(?:[A-Za-z_]\w*\.)*"
    r"Experimental[A-Za-z0-9_]*"
    r")"
)
SKIPPED_DIRECTORIES = {
    ".git",
    ".gradle",
    ".idea",
    ".scratch",
    "build",
    "node_modules",
}


def strip_comments_and_literals(text: str, *, preserve_literals: bool = False) -> str:
    """Replace comments and optionally literals while preserving newlines."""
    output: list[str] = []
    index = 0
    state = "code"
    block_depth = 0

    while index < len(text):
        if state == "code":
            if text.startswith("//", index):
                output.extend("  ")
                index += 2
                state = "line_comment"
            elif text.startswith("/*", index):
                output.extend("  ")
                index += 2
                block_depth = 1
                state = "block_comment"
            elif text.startswith('"""', index):
                output.extend('"""' if preserve_literals else "   ")
                index += 3
                state = "triple_string"
            elif text[index] == '"':
                output.append('"' if preserve_literals else " ")
                index += 1
                state = "string"
            elif text[index] == "'":
                output.append("'" if preserve_literals else " ")
                index += 1
                state = "char"
            else:
                output.append(text[index])
                index += 1
        elif state == "line_comment":
            if text[index] == "\n":
                output.append("\n")
                state = "code"
            else:
                output.append(" ")
            index += 1
        elif state == "block_comment":
            if text.startswith("/*", index):
                output.extend("  ")
                index += 2
                block_depth += 1
            elif text.startswith("*/", index):
                output.extend("  ")
                index += 2
                block_depth -= 1
                if block_depth == 0:
                    state = "code"
            else:
                output.append("\n" if text[index] == "\n" else " ")
                index += 1
        elif state == "triple_string":
            if text.startswith('"""', index):
                output.extend('"""' if preserve_literals else "   ")
                index += 3
                state = "code"
            else:
                output.append(
                    text[index]
                    if preserve_literals
                    else ("\n" if text[index] == "\n" else " ")
                )
                index += 1
        else:
            delimiter = '"' if state == "string" else "'"
            if text[index] == "\\" and index + 1 < len(text):
                output.extend(text[index : index + 2] if preserve_literals else "  ")
                index += 2
            elif text[index] == delimiter:
                output.append(delimiter if preserve_literals else " ")
                index += 1
                state = "code"
            else:
                output.append(
                    text[index]
                    if preserve_literals
                    else ("\n" if text[index] == "\n" else " ")
                )
                index += 1

    return "".join(output)


def annotation_arguments(code: str):
    """Yield balanced argument bodies from Kotlin OptIn annotations."""
    for match in OPT_IN_PATTERN.finditer(code):
        start = match.end()
        index = start
        depth = 1
        while index < len(code) and depth:
            if code[index] == "(":
                depth += 1
            elif code[index] == ")":
                depth -= 1
            index += 1
        if depth == 0:
            yield code[start : index - 1]


def is_experimental_marker(name: str) -> bool:
    return EXPERIMENTAL_MARKER_PATTERN.fullmatch(name) is not None


def marker_names_in_source(text: str) -> set[str]:
    code = strip_comments_and_literals(text)
    imports: dict[str, str] = {}
    pico_wildcard_import = False
    for match in IMPORT_PATTERN.finditer(code):
        imported_name, alias = match.groups()
        if imported_name.endswith(".*"):
            pico_wildcard_import |= imported_name.startswith(PICO_SPATIAL_PACKAGE)
            continue
        imports[alias or imported_name.rsplit(".", 1)[-1]] = imported_name

    found: set[str] = set()
    for arguments in annotation_arguments(code):
        for reference in CLASS_REFERENCE_PATTERN.findall(arguments):
            marker = reference.rsplit(".", 1)[-1]
            if "." in reference:
                if reference.startswith(PICO_SPATIAL_PACKAGE) and is_experimental_marker(
                    marker
                ):
                    found.add(marker)
                continue

            imported_name = imports.get(reference)
            if imported_name is not None:
                imported_marker = imported_name.rsplit(".", 1)[-1]
                if imported_name.startswith(
                    PICO_SPATIAL_PACKAGE
                ) and is_experimental_marker(imported_marker):
                    found.add(imported_marker)
            elif pico_wildcard_import and is_experimental_marker(reference):
                found.add(reference)
    return found


def marker_names_in_gradle(text: str) -> set[str]:
    code = strip_comments_and_literals(text, preserve_literals=True)
    return {
        qualified_name.rsplit(".", 1)[-1]
        for qualified_name in GRADLE_OPT_IN_PATTERN.findall(code)
    }


def iter_kotlin_sources(target: Path):
    for path in target.rglob("*.kt"):
        is_main_source = any(
            parent.name == "main" and parent.parent.name == "src"
            for parent in path.parents
        )
        if is_main_source and not any(part in SKIPPED_DIRECTORIES for part in path.parts):
            yield path


def iter_gradle_build_files(target: Path):
    for name in ("build.gradle", "build.gradle.kts"):
        for path in target.rglob(name):
            if not any(part in SKIPPED_DIRECTORIES for part in path.parts):
                yield path


def main_manifest_for(source: Path) -> Path | None:
    for parent in source.parents:
        if parent.name == "main" and parent.parent.name == "src":
            manifest = parent / "AndroidManifest.xml"
            return manifest if manifest.is_file() else None
    return None


def module_manifest_for(build_file: Path) -> Path | None:
    manifest = build_file.parent / "src" / "main" / "AndroidManifest.xml"
    return manifest if manifest.is_file() else None


def _classify_module(code: str) -> str:
    if APPLICATION_PLUGIN_PATTERN.search(code):
        return "application"
    if LIBRARY_PLUGIN_PATTERN.search(code):
        return "library"
    return "unknown"


def discover_modules(target: Path) -> dict[Path, dict]:
    """Return module metadata keyed by module directory."""
    modules: dict[Path, dict] = {}
    for build_file in iter_gradle_build_files(target):
        module_dir = build_file.parent
        try:
            text = build_file.read_text(encoding="utf-8")
        except OSError:
            continue
        code = strip_comments_and_literals(text, preserve_literals=True)
        kind = _classify_module(code)
        dependency_names = set(MODULE_DEPENDENCY_PATTERN.findall(code))
        modules[module_dir] = {
            "build_file": build_file,
            "kind": kind,
            "dependency_names": dependency_names,
            "manifest": module_manifest_for(build_file),
        }
    return modules


def _module_name(module_dir: Path, target: Path) -> str:
    relative = module_dir.relative_to(target).as_posix()
    if relative in {"", "."}:
        return ""
    return relative.replace("/", ":")


def _owner_module(path: Path, modules: dict[Path, dict]) -> Path | None:
    best: Path | None = None
    for module_dir in modules:
        try:
            path.relative_to(module_dir)
        except ValueError:
            continue
        if best is None or len(module_dir.parts) > len(best.parts):
            best = module_dir
    return best


def _consumer_applications(
    library_dir: Path, modules: dict[Path, dict], target: Path
) -> list[Path]:
    name_to_dir: dict[str, Path] = {}
    for module_dir in modules:
        name_to_dir[_module_name(module_dir, target)] = module_dir

    library_name = _module_name(library_dir, target)
    reverse: dict[str, set[str]] = {}
    for module_dir, info in modules.items():
        name = _module_name(module_dir, target)
        for dependency in info["dependency_names"]:
            reverse.setdefault(dependency, set()).add(name)

    visited: set[str] = set()
    pending = [library_name]
    while pending:
        current = pending.pop()
        for dependent in reverse.get(current, ()):
            if dependent not in visited:
                visited.add(dependent)
                pending.append(dependent)

    consumers: list[Path] = []
    for name in sorted(visited):
        module_dir = name_to_dir.get(name)
        if module_dir is None:
            continue
        if modules[module_dir]["kind"] == "application":
            consumers.append(module_dir)
    return consumers


def _resolve_manifests_for(
    module_dir: Path | None,
    modules: dict[Path, dict],
    target: Path,
    source_label: str,
    *,
    legacy_manifest: Path | None,
    missing_message: str,
) -> tuple[list[Path], list[str]]:
    info = modules.get(module_dir) if module_dir is not None else None
    kind = info["kind"] if info else "unknown"
    if kind == "library":
        consumers = _consumer_applications(module_dir, modules, target)
        if not consumers:
            return [], [
                f"{source_label}: experimental API opt-in in a library module has no "
                "consuming com.android.application module; cannot verify the runtime gate"
            ]
        manifests: list[Path] = []
        failures: list[str] = []
        for consumer in consumers:
            consumer_manifest = modules[consumer]["manifest"]
            if consumer_manifest is None:
                failures.append(
                    f"{source_label}: consuming application module "
                    f"'{_module_name(consumer, target) or '<root>'}' has no "
                    "src/main/AndroidManifest.xml"
                )
            else:
                manifests.append(consumer_manifest)
        return manifests, failures
    manifest = (info["manifest"] if info else None) or legacy_manifest
    if manifest is None:
        return [], [f"{source_label}: {missing_message}"]
    return [manifest], []


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def validate_manifest(manifest: Path) -> list[str]:
    try:
        root = ET.parse(manifest).getroot()
    except (ET.ParseError, OSError) as error:
        return [f"{manifest}: cannot parse application manifest: {error}"]

    applications = [element for element in root if local_name(element.tag) == "application"]
    if len(applications) != 1:
        return [
            f"{manifest}: expected exactly one direct <application> element, "
            f"found {len(applications)}"
        ]

    name_key = f"{{{ANDROID_NAMESPACE}}}name"
    value_key = f"{{{ANDROID_NAMESPACE}}}value"
    entries = [
        element
        for element in applications[0]
        if local_name(element.tag) == "meta-data"
        and element.attrib.get(name_key) == EXPERIMENTAL_META_NAME
    ]
    if not entries:
        return [
            f"{manifest}: active experimental API opt-in requires "
            f"{EXPERIMENTAL_META_NAME}=1 directly under <application>"
        ]
    if len(entries) != 1:
        return [
            f"{manifest}: expected one {EXPERIMENTAL_META_NAME} entry, "
            f"found {len(entries)}"
        ]

    value = entries[0].attrib.get(value_key)
    if value != "1":
        return [
            f"{manifest}: {EXPERIMENTAL_META_NAME} must equal 1, "
            f"found {value!r}"
        ]
    return []


def check(target: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    evidence: list[str] = []
    manifests_to_check: set[Path] = set()
    modules = discover_modules(target)

    for source in iter_kotlin_sources(target):
        try:
            markers = marker_names_in_source(source.read_text(encoding="utf-8"))
        except OSError as error:
            failures.append(f"{source}: cannot read Kotlin source: {error}")
            continue
        if not markers:
            continue

        relative = source.relative_to(target)
        evidence.append(f"{relative}: {', '.join(sorted(markers))}")
        owner = _owner_module(source, modules)
        resolved, resolution_failures = _resolve_manifests_for(
            owner,
            modules,
            target,
            str(relative),
            legacy_manifest=main_manifest_for(source),
            missing_message=(
                "experimental API opt-in has no associated src/main/AndroidManifest.xml"
            ),
        )
        failures.extend(resolution_failures)
        manifests_to_check.update(resolved)

    for build_file in iter_gradle_build_files(target):
        try:
            markers = marker_names_in_gradle(build_file.read_text(encoding="utf-8"))
        except OSError as error:
            failures.append(f"{build_file}: cannot read Gradle build file: {error}")
            continue
        if not markers:
            continue

        relative = build_file.relative_to(target)
        evidence.append(f"{relative}: {', '.join(sorted(markers))}")
        owner = _owner_module(build_file, modules)
        resolved, resolution_failures = _resolve_manifests_for(
            owner,
            modules,
            target,
            str(relative),
            legacy_manifest=module_manifest_for(build_file),
            missing_message=(
                "PICO Spatial experimental compiler opt-in cannot be associated with a "
                "module src/main/AndroidManifest.xml"
            ),
        )
        failures.extend(resolution_failures)
        manifests_to_check.update(resolved)

    for manifest in sorted(manifests_to_check):
        failures.extend(validate_manifest(manifest))
    return failures, evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Require pico.spatial.use_experimental_api=1 in each application "
            "module that contains an active Spatial SDK experimental opt-in."
        )
    )
    parser.add_argument("--target", required=True, type=Path, help="Android project root")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = args.target.resolve()
    if not target.is_dir():
        print(f"[experimental-api] FAIL target directory not found: {target}")
        return 2

    failures, evidence = check(target)
    for item in evidence:
        print(f"[experimental-api] detected {item}")
    if failures:
        for failure in failures:
            print(f"[experimental-api] ERROR {failure}")
        return 1

    if evidence:
        print("[experimental-api] PASS source and runtime opt-ins are consistent")
    else:
        print("[experimental-api] PASS no active experimental API opt-in markers found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
