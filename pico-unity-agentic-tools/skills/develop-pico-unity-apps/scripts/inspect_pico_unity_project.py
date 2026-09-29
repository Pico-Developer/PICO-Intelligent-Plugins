#!/usr/bin/env python3
"""Read-only inventory for Unity projects that target PICO Unity SDK."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from collections.abc import Iterable


SKIP_DIRS = {
    ".git",
    ".idea",
    ".vs",
    ".vscode",
    "Build",
    "Builds",
    "Library",
    "Logs",
    "MemoryCaptures",
    "obj",
    "Temp",
    "UserSettings",
}

TEXT_EXTENSIONS = {
    ".asmdef",
    ".asset",
    ".cs",
    ".gradle",
    ".json",
    ".manifest",
    ".md",
    ".prefab",
    ".properties",
    ".shader",
    ".txt",
    ".unity",
    ".xml",
    ".yaml",
    ".yml",
}

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_EXAMPLES = 8

MODE_PATTERNS = {
    "pico_xr": [
        re.compile(r"\bByteDance\.PICO\.XR\b"),
        re.compile(r"\bPXR_Manager\b"),
        re.compile(r"\bENABLE_PICO_XR_SDK\b"),
    ],
    "unity_openxr": [
        re.compile(r"\bByteDance\.PICO\.OpenXR\b"),
        re.compile(r"\bUnity\.XR\.OpenXR\.Features\.PICOSupport\b"),
        re.compile(r"\bPICO Support\b"),
    ],
    "pico_spatial": [
        re.compile(r"\bByteDance\.PICO\.Spatial\b"),
        re.compile(r"\bSpatialCamera\b"),
        re.compile(r"\bMultiSpatial\b"),
    ],
}

LEGACY_PATTERNS = {
    "Unity.XR.PXR": re.compile(r"\bUnity\.XR\.PXR\b"),
    "Unity.XR.OpenXR.Features.PICOSupport": re.compile(
        r"\bUnity\.XR\.OpenXR\.Features\.PICOSupport\b"
    ),
    "Pico.Platform": re.compile(r"\bPico\.Platform\b"),
}

FEATURE_PATTERNS = {
    "xr_interaction_toolkit": re.compile(
        r"\bXRInteraction|XR Interaction Toolkit|com\.unity\.xr\.interaction\.toolkit\b",
        re.IGNORECASE,
    ),
    "xr_hands": re.compile(r"\bXRHand|XR Hands|com\.unity\.xr\.hands\b", re.IGNORECASE),
    "ar_foundation": re.compile(
        r"\bARFoundation|AR Foundation|com\.unity\.xr\.arfoundation\b",
        re.IGNORECASE,
    ),
    "eye_tracking": re.compile(r"\bEyeTracking|Eye Tracking|ETFR\b", re.IGNORECASE),
    "hand_tracking": re.compile(r"\bHandTracking|Hand Tracking\b", re.IGNORECASE),
    "body_tracking": re.compile(r"\bBodyTracking|Body Tracking\b", re.IGNORECASE),
    "face_tracking": re.compile(r"\bFaceTracking|Face Tracking\b", re.IGNORECASE),
    "passthrough": re.compile(r"\bPassthrough|Video Seethrough|\bVST\b", re.IGNORECASE),
    "spatial_anchor": re.compile(r"\bSpatialAnchor|Spatial Anchor\b", re.IGNORECASE),
    "spatial_mesh": re.compile(r"\bSpatialMesh|Spatial Mesh\b", re.IGNORECASE),
    "foveation": re.compile(r"\bFoveat|FFR|ETFR\b", re.IGNORECASE),
    "composition_layer": re.compile(r"\bComposition Layer|Compositor Layer\b", re.IGNORECASE),
}

PACKAGE_PREFIXES = (
    "com.unity.inputsystem",
    "com.unity.render-pipelines.universal",
    "com.unity.xr",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a Unity project for PICO SDK mode and configuration evidence."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Unity project root or a path inside the project (default: current directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print machine-readable JSON.",
    )
    return parser.parse_args()


def find_project_root(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if all((candidate / name).is_dir() for name in ("Assets", "Packages", "ProjectSettings")):
            return candidate

    direct_children = []
    try:
        direct_children = [path for path in current.iterdir() if path.is_dir()]
    except OSError:
        return None

    matches = [
        child
        for child in direct_children
        if all((child / name).is_dir() for name in ("Assets", "Packages", "ProjectSettings"))
    ]
    return matches[0] if len(matches) == 1 else None


def read_text(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def iter_text_files(root: Path) -> Iterable[Path]:
    scan_roots = [root / "Assets", root / "Packages", root / "ProjectSettings"]
    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for path in scan_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                relative_parts = path.relative_to(root).parts
            except ValueError:
                continue
            if any(part in SKIP_DIRS for part in relative_parts):
                continue
            yield path


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def get_unity_version(root: Path) -> str | None:
    text = read_text(root / "ProjectSettings" / "ProjectVersion.txt")
    match = re.search(r"^m_EditorVersion:\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def get_packages(root: Path) -> tuple[dict[str, str], list[str]]:
    manifest_path = root / "Packages" / "manifest.json"
    text = read_text(manifest_path)
    if not text:
        return {}, ["Packages/manifest.json is missing or unreadable."]

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        return {}, [f"Packages/manifest.json is invalid JSON: {error}"]

    dependencies = payload.get("dependencies", {})
    if not isinstance(dependencies, dict):
        return {}, ["Packages/manifest.json has no dependency object."]

    selected = {
        str(name): str(version)
        for name, version in dependencies.items()
        if str(name).startswith(PACKAGE_PREFIXES)
        or "pico" in str(name).lower()
        or "spatial" in str(name).lower()
        or "openxr" in str(name).lower()
        or "pico" in str(version).lower()
        or "spatial" in str(version).lower()
    }
    return dict(sorted(selected.items())), []


def collect_pattern_evidence(
    root: Path,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, list[str]],
    dict[str, dict[str, Any]],
    int,
]:
    mode_counts: dict[str, int] = defaultdict(int)
    mode_examples: dict[str, list[str]] = defaultdict(list)
    legacy_examples: dict[str, list[str]] = defaultdict(list)
    feature_counts: dict[str, int] = defaultdict(int)
    feature_examples: dict[str, list[str]] = defaultdict(list)
    scanned = 0

    for path in iter_text_files(root):
        text = read_text(path)
        if not text:
            continue
        scanned += 1
        rel = relative(path, root)

        for mode, patterns in MODE_PATTERNS.items():
            if any(pattern.search(text) for pattern in patterns):
                mode_counts[mode] += 1
                if len(mode_examples[mode]) < MAX_EXAMPLES:
                    mode_examples[mode].append(rel)

        for name, pattern in LEGACY_PATTERNS.items():
            if pattern.search(text) and len(legacy_examples[name]) < MAX_EXAMPLES:
                legacy_examples[name].append(rel)

        for feature, pattern in FEATURE_PATTERNS.items():
            if pattern.search(text):
                feature_counts[feature] += 1
                if len(feature_examples[feature]) < MAX_EXAMPLES:
                    feature_examples[feature].append(rel)

    modes = {
        mode: {
            "matching_files": mode_counts.get(mode, 0),
            "examples": mode_examples.get(mode, []),
        }
        for mode in MODE_PATTERNS
    }
    features = {
        feature: {
            "matching_files": feature_counts.get(feature, 0),
            "examples": feature_examples.get(feature, []),
        }
        for feature in FEATURE_PATTERNS
        if feature_counts.get(feature, 0)
    }
    return modes, dict(legacy_examples), features, scanned


def extract_project_settings(root: Path) -> dict[str, Any]:
    player_text = read_text(root / "ProjectSettings" / "ProjectSettings.asset")
    graphics_text = read_text(root / "ProjectSettings" / "GraphicsSettings.asset")
    quality_text = read_text(root / "ProjectSettings" / "QualitySettings.asset")

    fields = {
        "minimum_android_api_raw": r"^\s*AndroidMinSdkVersion:\s*(.+?)\s*$",
        "target_android_api_raw": r"^\s*AndroidTargetSdkVersion:\s*(.+?)\s*$",
        "target_architectures_raw": r"^\s*targetArchitectures:\s*(.+?)\s*$",
        "scripting_backend_block_present": r"^\s*scriptingBackend:\s*$",
        "color_space_raw": r"^\s*m_ActiveColorSpace:\s*(.+?)\s*$",
        "graphics_jobs_raw": r"^\s*graphicsJobs:\s*(.+?)\s*$",
        "multithreaded_rendering_raw": r"^\s*m_MTRendering:\s*(.+?)\s*$",
        "default_orientation_raw": r"^\s*defaultScreenOrientation:\s*(.+?)\s*$",
        "application_entry_raw": r"^\s*applicationEntry:\s*(.+?)\s*$",
    }

    result: dict[str, Any] = {}
    for key, pattern in fields.items():
        match = re.search(pattern, player_text, re.MULTILINE)
        if match:
            result[key] = match.group(1) if match.lastindex else True

    graphics_api_match = re.search(
        r"^\s*-\s*m_BuildTarget:\s*AndroidPlayer\s*$"
        r"\s*m_APIs:\s*(\S+)\s*$"
        r"\s*m_Automatic:\s*(\S+)\s*$",
        player_text,
        re.MULTILINE,
    )
    if graphics_api_match:
        result["android_graphics_apis_hex_raw"] = graphics_api_match.group(1)
        result["android_graphics_apis_automatic_raw"] = graphics_api_match.group(2)

    result["render_pipeline_asset_configured"] = bool(
        re.search(r"m_CustomRenderPipeline:\s*\{fileID:\s*(?!0\b)", graphics_text)
        or re.search(r"m_RenderPipelineAsset:\s*\{fileID:\s*(?!0\b)", quality_text)
    )
    result["custom_android_manifest"] = (
        root / "Assets" / "Plugins" / "Android" / "AndroidManifest.xml"
    ).exists()
    return result


def get_authoritative_mode_signals(root: Path) -> dict[str, list[str]]:
    signals: dict[str, list[str]] = defaultdict(list)
    player_text = read_text(root / "ProjectSettings" / "ProjectSettings.asset")
    editor_build_text = read_text(root / "ProjectSettings" / "EditorBuildSettings.asset")

    if re.search(r"\bENABLE_PICO_OPENXR_SDK\b", player_text):
        signals["unity_openxr"].append(
            "ProjectSettings/ProjectSettings.asset: ENABLE_PICO_OPENXR_SDK"
        )
    if re.search(r"\bENABLE_PICO_XR_SDK\b", player_text):
        signals["pico_xr"].append(
            "ProjectSettings/ProjectSettings.asset: ENABLE_PICO_XR_SDK"
        )
    if re.search(r"\bcom\.unity\.xr\.openxr\.settings", editor_build_text):
        signals["unity_openxr"].append(
            "ProjectSettings/EditorBuildSettings.asset: Unity OpenXR settings"
        )

    spatial_settings = root / "ProjectSettings" / "PICO Spatial"
    if spatial_settings.exists():
        signals["pico_spatial"].append(
            "ProjectSettings/PICO Spatial: dedicated Spatial settings"
        )

    return dict(signals)


def infer_mode(
    modes: dict[str, dict[str, Any]],
    authoritative_signals: dict[str, list[str]],
) -> dict[str, Any]:
    authoritative_modes = [
        mode for mode, evidence in authoritative_signals.items() if evidence
    ]
    if len(authoritative_modes) == 1:
        mode = authoritative_modes[0]
        return {
            "mode": mode,
            "confidence": "high",
            "reason": "Authoritative project configuration: "
            + "; ".join(authoritative_signals[mode]),
        }
    if len(authoritative_modes) > 1:
        return {
            "mode": "mixed-or-ambiguous",
            "confidence": "low",
            "reason": f"Conflicting authoritative mode signals: {authoritative_signals}.",
        }

    ranked = sorted(
        (
            (mode, int(details["matching_files"]))
            for mode, details in modes.items()
            if int(details["matching_files"]) > 0
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    if not ranked:
        return {
            "mode": "unknown",
            "confidence": "none",
            "reason": "No PICO mode-specific source or serialized evidence was found.",
        }

    top_mode, top_count = ranked[0]
    second_count = ranked[1][1] if len(ranked) > 1 else 0
    if second_count == 0:
        confidence = "high" if top_count >= 2 else "medium"
    elif top_count >= second_count * 3:
        confidence = "medium"
    else:
        return {
            "mode": "mixed-or-ambiguous",
            "confidence": "low",
            "reason": f"Multiple mode signals are present: {ranked}.",
        }

    return {
        "mode": top_mode,
        "confidence": confidence,
        "reason": f"{top_count} matching files; next mode has {second_count}.",
    }


def build_warnings(
    inferred: dict[str, Any],
    legacy: dict[str, list[str]],
    settings: dict[str, Any],
    packages: dict[str, str],
) -> list[str]:
    warnings: list[str] = []
    if inferred["mode"] == "unknown":
        warnings.append("No development mode could be inferred; confirm the PICO Portal selection.")
    elif inferred["mode"] == "mixed-or-ambiguous":
        warnings.append(
            "Strong signals from multiple PICO modes exist; verify providers, assemblies, and namespaces."
        )

    if legacy:
        warnings.append(
            "Legacy PICO namespaces were found; migrate deliberately and check serialized components."
        )

    minimum_api = settings.get("minimum_android_api_raw")
    if isinstance(minimum_api, str) and minimum_api.isdigit() and int(minimum_api) < 29:
        warnings.append("The detected raw Android minimum API value is below 29.")

    if settings.get("custom_android_manifest"):
        warnings.append(
            "A custom AndroidManifest.xml exists; inspect manifest merge and SDK-generated permissions."
        )

    if not any("inputsystem" in name for name in packages):
        warnings.append("Unity Input System was not found in manifest.json.")
    return warnings


def inspect(root: Path) -> dict[str, Any]:
    packages, package_errors = get_packages(root)
    modes, legacy, features, scanned = collect_pattern_evidence(root)
    settings = extract_project_settings(root)
    authoritative_signals = get_authoritative_mode_signals(root)
    inferred = infer_mode(modes, authoritative_signals)

    return {
        "project_root": str(root),
        "unity_version": get_unity_version(root),
        "packages": packages,
        "package_errors": package_errors,
        "inferred_mode": inferred,
        "authoritative_mode_signals": authoritative_signals,
        "mode_evidence": modes,
        "legacy_namespace_evidence": legacy,
        "feature_evidence": features,
        "project_settings_raw": settings,
        "scanned_text_files": scanned,
        "warnings": build_warnings(inferred, legacy, settings, packages),
        "notes": [
            "This tool is read-only.",
            "Unity serialized enum values are reported as raw values; confirm them in the Editor.",
            "Mode inference is evidence-based and must be confirmed in PICO Portal/XR settings.",
        ],
    }


def print_human(report: dict[str, Any]) -> None:
    print("PICO Unity project inventory")
    print(f"Project: {report['project_root']}")
    print(f"Unity: {report['unity_version'] or 'unknown'}")
    inferred = report["inferred_mode"]
    print(
        f"Inferred mode: {inferred['mode']} "
        f"(confidence: {inferred['confidence']}; {inferred['reason']})"
    )
    print(f"Scanned text files: {report['scanned_text_files']}")

    print("\nRelevant packages:")
    if report["packages"]:
        for name, version in report["packages"].items():
            print(f"  - {name}: {version}")
    else:
        print("  - none detected")

    print("\nMode evidence:")
    for mode, details in report["mode_evidence"].items():
        print(f"  - {mode}: {details['matching_files']} matching files")
        for example in details["examples"][:3]:
            print(f"      {example}")

    print("\nDetected feature signals:")
    if report["feature_evidence"]:
        for feature, details in sorted(report["feature_evidence"].items()):
            print(f"  - {feature}: {details['matching_files']} matching files")
    else:
        print("  - none detected")

    print("\nProject settings (raw evidence):")
    if report["project_settings_raw"]:
        for name, value in sorted(report["project_settings_raw"].items()):
            print(f"  - {name}: {value}")
    else:
        print("  - no recognized settings")

    if report["legacy_namespace_evidence"]:
        print("\nLegacy namespaces:")
        for namespace, examples in report["legacy_namespace_evidence"].items():
            print(f"  - {namespace}")
            for example in examples[:3]:
                print(f"      {example}")

    print("\nWarnings:")
    if report["warnings"]:
        for warning in report["warnings"]:
            print(f"  - {warning}")
    else:
        print("  - none from static inspection")

    print("\nConfirm raw settings in Unity PICO Portal and Project Validation.")


def main() -> int:
    args = parse_args()
    root = find_project_root(Path(args.path))
    if root is None:
        print(
            "Error: no unique Unity project root was found. "
            "Pass a directory containing Assets, Packages, and ProjectSettings.",
            file=sys.stderr,
        )
        return 2

    report = inspect(root)
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
