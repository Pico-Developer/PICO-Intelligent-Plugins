#!/usr/bin/env python3
"""Implementation-level scanner for spatial-design-to-app.

Reads the generated Kotlin and AndroidManifest.xml and validates them directly.
There is no intermediate layout-contract JSON: the container the app registers
is inferred from AndroidManifest meta-data, which is what the runtime actually
honours.

Usage:
    python3 -m scripts.scan_implementation --target ./myapp
    python3 /abs/path/to/scan_implementation.py --target ./generated-spatial-app \
        --generation-mode existing_module --profile default

It writes `<target>/.scratch/implementation_scan_result.json` with per-check
pass/fail plus concrete messages, and exits non-zero when any check fails.

Checks performed (best-effort, regex-based; never blocks on missing files):

- root_match                 — code root matches the container the manifest declares
- entry_wired                — `mainApp` / `Application.launch(::mainApp)` present
- manifest_consistency       — required windowcontainer / stage meta-data values
- stage_api_legality         — Stage-only APIs (anchor, env_mesh, ECS) stay in Stage flows
- whitelist_components       — imports do not reference invented SpatialUI symbols
- invented_component_names   — no SDK names the reference marks as non-existent
- spatialui_component_floor  — positive evidence that SpatialUI built-ins were used
                               instead of hand-rolled Box + Text equivalents (warns)
- window_chrome_ornaments    — edge-pinned chrome uses window-level fittings (warns)
- root_change_guard          — existing modules do not silently switch root architecture

The SpatialUI component vocabulary is parsed from
`references/spatial-ui-components.md` and `references/spatial-windows-guide.md`
so those documents stay the single source of truth.

This scanner is intentionally conservative: false positives are worse than
false negatives. Heuristic signals degrade to WARN, not FAIL.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


WINDOW_CONTAINERS = {"ON_PLAIN", "IN_VOLUME"}
STAGE_CONTAINERS = {"STAGE_MIXED", "STAGE_PROGRESSIVE", "STAGE_FULL"}
STAGE_MANIFEST_EXPECTATIONS = {
    "STAGE_MIXED": {
        "pico.spatial.stage.style": "1",
        "pico.spatial.stage.immersion": "0",
        "pico.spatial.stage.immersion_min": "0",
        "pico.spatial.stage.immersion_max": "0",
    },
    "STAGE_PROGRESSIVE": {
        "pico.spatial.stage.style": "2",
        "pico.spatial.stage.immersion_min": "0",
        "pico.spatial.stage.immersion_max": "100",
    },
    "STAGE_FULL": {
        "pico.spatial.stage.style": "3",
        "pico.spatial.stage.immersion": "100",
        "pico.spatial.stage.immersion_min": "100",
        "pico.spatial.stage.immersion_max": "100",
    },
}
# Patterns used to detect container invocations in code. Imports alone are ignored.
#
# CRITICAL distinction (verified against PICO SpatialSDK source):
#   - `DefaultWindowContainer` / `DefaultStage` are the app's SINGLE default root
#     (configured in AndroidManifest, guarded at runtime by
#     SUISpatialContainerManager.checkDefault(); registering two defaults throws).
#   - `WindowContainer(id=...)` / `Stage(id=...)` are SECONDARY containers opened
#     on demand via openWindowContainer(id) / openStage(id, style). MANY are
#     allowed and they do NOT count as additional roots.
#
# Therefore a shared-space `DefaultWindowContainer` that also declares
# `Stage(id=...)` entries (e.g. SpatialAppSample/stagerendering/Main.kt:23-38) is
# a VALID single-root app, not an illegal "mixed root". Only two coexisting
# *default* roots (`DefaultWindowContainer` + `DefaultStage`) are illegal.
DEFAULT_WINDOW_ROOT_PATTERN = r"\bDefaultWindowContainer\s*(?:\(|\{)"
DEFAULT_STAGE_ROOT_PATTERN = r"\bDefaultStage\s*(?:\(|\{)"
# Secondary containers always take an id argument → require an opening paren.
# `\b` prevents these from matching inside `DefaultWindowContainer` / `DefaultStage`.
SECONDARY_WINDOW_PATTERN = r"\bWindowContainer\s*\("
SECONDARY_STAGE_PATTERN = r"\bStage\s*\("

# Stage-only API hints. Patterns verified against the PICO SpatialSDK
# source (sensepack + spatialpack/core/ecs). Each manager / anchor type below
# is annotated `@RequiredFullSpace` and throws when called outside Full Space.
STAGE_ONLY_API_PATTERNS = (
    r"\bWorldTrackingManager\b",  # com.pico.spatial.sense.world.WorldTrackingManager
    r"\bPlaneTrackingManager\b",  # com.pico.spatial.sense.plane.PlaneTrackingManager
    r"\bMeshTrackingManager\b",  # com.pico.spatial.sense.mesh.MeshTrackingManager
    r"\bWorldAnchor\b",  # com.pico.spatial.sense.world.WorldAnchor
    r"\bPlaneAnchor\b",  # com.pico.spatial.sense.plane.PlaneAnchor
    r"\bMeshAnchor\b",  # com.pico.spatial.sense.mesh.MeshAnchor
    r"\bWorldTrackingResult\b",  # sealed result type
    r"\bAnchorEntity\b",  # com.pico.spatial.core.ecs.AnchorEntity
    r"\bAnchorComponent\b",  # com.pico.spatial.core.ecs.AnchorComponent
    r"\bAnchorTarget\b",  # com.pico.spatial.core.ecs.anchor.AnchorTarget
    r"\b@RequiredFullSpace\b",  # com.pico.spatial.core.annotation.RequiredFullSpace
    r"\bscene\.rayCast\b",  # raycast on scene instance (Stage-only)
    r"\bscene\.convexCast\b",  # convex cast on scene instance
    r"\bcom\.pico\.spatial\.sense\.",  # any sensepack import is Stage-only
)

ENTRY_TOKENS = (
    "mainApp",
    "launch(::mainApp)",
    "SpatialLaunchActivity",
)

# Allow-listed SpatialUI / Spatial ECS import roots. Anything else under
# `com.pico.spatial.*` is reported as a warning so reviewers can confirm.
ALLOWED_SPATIAL_PACKAGE_PREFIXES = (
    "com.pico.spatial.ui.design",
    "com.pico.spatial.ui.foundation",
    "com.pico.spatial.ui.platform",
    "com.pico.spatial.foundation",
    "com.pico.spatial.scene",
    "com.pico.spatial.physics",
    "com.pico.spatial.input",
    "com.pico.spatial.entity",
    "com.pico.spatial.runtime",
)


def container_kind(container: str | None) -> str | None:
    if container in WINDOW_CONTAINERS:
        return "window"
    if container in STAGE_CONTAINERS:
        return "stage"
    return None


# --------------------------------------------------------------------------
# Component vocabulary
#
# The whitelist is PARSED from references/spatial-ui-components.md and
# references/spatial-windows-guide.md rather than hard-coded, so the docs stay
# the single source of truth. A hard-coded copy would silently drift from the
# reference the skill tells the agent to obey.
# --------------------------------------------------------------------------

# Generic layout/text primitives. Legal to use, but they are NOT evidence that
# SpatialUI built-ins were preferred over hand-rolled UI, so they never count
# toward the component floor.
GENERIC_PRIMITIVES = frozenset(
    {
        "Box",
        "Column",
        "Row",
        "LazyColumn",
        "LazyRow",
        "Spacer",
        "Text",
        "Icon",
        "PicoTheme",
    }
)

# Names that appear in the guides as prose/material vocabulary rather than as
# callable components.
_VOCABULARY_NOISE = frozenset(
    {
        "None",
        "Regular",
        "Thick",
        "Thickest",
        "Material",
        "Tooltip",
        "Modifier",
        "Alignment",
        "Color",
        "Form",
        "Automatic",
        "Planar",
        "Volumetric",
        "TabBarPlacement",
        "CoachmarkDirection",
        "CoachmarkDefaults",
        "SpatialWindowType",
        "SpatialWindowProperties",
        "LocalSnackbarHostState",
        "SpatialAppScope",
    }
)

_TABLE_ROW_RE = re.compile(r"^\|\s*(`[^|]+`)\s*\|", re.MULTILINE)
_BACKTICK_NAME_RE = re.compile(r"`([A-Z][A-Za-z0-9]*)`")
_HEADING_RE = re.compile(r"^##\s+(.*)$", re.MULTILINE)


def _reference_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "references"


def _forbidden_names_from_components_doc(text: str) -> set[str]:
    """Names listed under 'What's NOT here (do not emit)'."""
    forbidden: set[str] = set()
    match = re.search(
        r"^##\s+What's NOT here.*?$(.*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match:
        forbidden.update(_BACKTICK_NAME_RE.findall(match.group(1)))
    # `Box` appears in that section only as the *recommended fallback* prose
    # ("generate a `Box` with a TODO"), not as a banned name.
    forbidden.discard("Box")
    # `Window` / `Screen` / `Page` are banned as Spatial *container* types, but
    # they are ordinary words that legitimately appear inside composable names
    # (HomeScreen, SettingsPage). Flagging them by bare name would be noise, and
    # this scanner treats false positives as worse than false negatives.
    forbidden -= {"Window", "Screen", "Page"}
    return forbidden


def load_component_vocabulary() -> tuple[set[str], set[str]]:
    """Returns (allowed_components, forbidden_components).

    `allowed_components` excludes generic primitives, so it answers the question
    "which SpatialUI built-ins did this code actually use?" rather than "is this
    a Compose file?".
    """
    references = _reference_dir()
    allowed: set[str] = set()
    forbidden: set[str] = set()

    components_doc = references / "spatial-ui-components.md"
    if components_doc.exists():
        text = read_text_safe(components_doc)
        forbidden = _forbidden_names_from_components_doc(text)
        # Skip the trailing prose sections so their examples do not leak in.
        body = re.split(r"^##\s+What's NOT here", text, flags=re.MULTILINE)[0]
        for cell in _TABLE_ROW_RE.findall(body):
            allowed.update(_BACKTICK_NAME_RE.findall(cell))

    windows_doc = references / "spatial-windows-guide.md"
    if windows_doc.exists():
        text = read_text_safe(windows_doc)
        for cell in _TABLE_ROW_RE.findall(text):
            allowed.update(_BACKTICK_NAME_RE.findall(cell))

    allowed -= GENERIC_PRIMITIVES
    allowed -= _VOCABULARY_NOISE
    allowed -= forbidden
    return allowed, forbidden


# --------------------------------------------------------------------------
# Container inference from AndroidManifest
#
# Replaces the former `contract.container` field: the manifest meta-data IS the
# runtime source of truth for which root the app registers, so it needs no
# intermediate JSON artifact. Mirrors the value matrix documented in
# references/manifest-and-entry.md -> "Choosing the Stage variant".
# --------------------------------------------------------------------------

WINDOW_STYLE_TO_CONTAINER = {
    "1": "ON_PLAIN",
    "2": "IN_VOLUME",
}
STAGE_STYLE_TO_CONTAINER = {
    "1": "STAGE_MIXED",
    "2": "STAGE_PROGRESSIVE",
    "3": "STAGE_FULL",
}


def parse_manifest_meta(manifests: list[tuple[Path, str]]) -> dict[str, set[str]]:
    meta: dict[str, set[str]] = {}
    for _, text in manifests:
        for name, value in re.findall(
            r'android:name="([^"]+)"[\s\S]{0,200}?android:value="([^"]+)"',
            text,
        ):
            meta.setdefault(name, set()).add(value)
    return meta


def infer_container(
    manifests: list[tuple[Path, str]],
    kotlin_sources: list[tuple[Path, str]],
) -> tuple[str | None, list[str]]:
    """Infer the declared container from manifest meta-data.

    Falls back to the code root kind when the manifest only says *which* family
    the app is in without pinning a style value.
    """
    evidence: list[str] = []
    meta = parse_manifest_meta(manifests)

    stage_styles = meta.get("pico.spatial.stage.style", set())
    for value in sorted(stage_styles):
        if value in STAGE_STYLE_TO_CONTAINER:
            container = STAGE_STYLE_TO_CONTAINER[value]
            evidence.append(f"manifest pico.spatial.stage.style={value} -> {container}")
            return container, evidence

    window_styles = meta.get("pico.spatial.windowcontainer.style", set())
    for value in sorted(window_styles):
        if value in WINDOW_STYLE_TO_CONTAINER:
            container = WINDOW_STYLE_TO_CONTAINER[value]
            evidence.append(f"manifest pico.spatial.windowcontainer.style={value} -> {container}")
            return container, evidence

    # No explicit style value: fall back to the family declared in the manifest,
    # then to the root actually invoked in code.
    if "pico.spatial.stage.id" in meta:
        evidence.append("manifest declares pico.spatial.stage.id without style -> STAGE_MIXED")
        return "STAGE_MIXED", evidence
    if "pico.spatial.windowcontainer.id" in meta:
        evidence.append(
            "manifest declares pico.spatial.windowcontainer.id without style -> ON_PLAIN"
        )
        return "ON_PLAIN", evidence

    detected, root_evidence = detect_root_kind(kotlin_sources)
    evidence.extend(root_evidence)
    if detected == "stage":
        evidence.append("no manifest meta; code root DefaultStage -> STAGE_MIXED")
        return "STAGE_MIXED", evidence
    if detected == "window":
        evidence.append("no manifest meta; code root DefaultWindowContainer -> ON_PLAIN")
        return "ON_PLAIN", evidence
    return None, evidence


def collect_kotlin_files(target: Path) -> list[Path]:
    candidates: list[Path] = []
    for sub in ("src/main", "app/src/main", "src"):
        base = target / sub
        if base.exists():
            candidates.extend(base.rglob("*.kt"))
    if not candidates:
        candidates.extend(target.rglob("*.kt"))
    # de-dupe while preserving order
    seen: set[Path] = set()
    out: list[Path] = []
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        out.append(path)
    return out


def collect_manifests(target: Path) -> list[Path]:
    out: list[Path] = []
    for sub in ("src/main/AndroidManifest.xml", "app/src/main/AndroidManifest.xml"):
        path = target / sub
        if path.exists():
            out.append(path)
    if not out:
        out.extend(target.rglob("AndroidManifest.xml"))
    return out


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def strip_comments_and_imports(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*import\s+.*$", "", text, flags=re.MULTILINE)
    return text


def detect_root_kind(kotlin_sources: list[tuple[Path, str]]) -> tuple[str | None, list[str]]:
    """Returns (root_kind, evidence_lines).

    Only the *default* container (`DefaultWindowContainer` / `DefaultStage`)
    determines the root kind. Secondary `WindowContainer(id=...)` /
    `Stage(id=...)` blocks are runtime-opened auxiliary containers and are NOT
    treated as roots — a `DefaultWindowContainer` app may legally declare
    `Stage(id=...)` entries (shared-space default + open immersive stage on
    demand). "mixed" is reported ONLY when both *default* roots coexist.
    """
    evidence: list[str] = []
    has_default_window = False
    has_default_stage = False
    for path, text in kotlin_sources:
        body = strip_comments_and_imports(text)
        if re.search(DEFAULT_WINDOW_ROOT_PATTERN, body):
            has_default_window = True
            evidence.append(f"{path.name}: default window root 'DefaultWindowContainer'")
        if re.search(DEFAULT_STAGE_ROOT_PATTERN, body):
            has_default_stage = True
            evidence.append(f"{path.name}: default stage root 'DefaultStage'")
        if re.search(SECONDARY_WINDOW_PATTERN, body):
            evidence.append(f"{path.name}: secondary WindowContainer(id=...) (not a root)")
        if re.search(SECONDARY_STAGE_PATTERN, body):
            evidence.append(f"{path.name}: secondary Stage(id=...) (not a root)")
    if has_default_window and has_default_stage:
        return "mixed", evidence
    if has_default_window:
        return "window", evidence
    if has_default_stage:
        return "stage", evidence
    return None, evidence


def check_root_match(
    container: str | None,
    kotlin_sources: list[tuple[Path, str]],
) -> dict[str, Any]:
    declared_kind = container_kind(container)
    detected, evidence = detect_root_kind(kotlin_sources)

    failures: list[str] = []
    if declared_kind is None:
        failures.append(
            "could not determine the app container from AndroidManifest meta-data "
            "(pico.spatial.windowcontainer.* / pico.spatial.stage.*) or from a "
            "DefaultWindowContainer / DefaultStage root in code"
        )
    elif detected is None:
        failures.append(
            "no DefaultWindowContainer / DefaultStage / WindowContainer / Stage root invocation found in code"
        )
    elif detected == "mixed":
        failures.append(
            "code declares BOTH a DefaultWindowContainer and a DefaultStage; "
            "only one default root is allowed (secondary WindowContainer(id=...) / "
            "Stage(id=...) are fine and do not count as roots)"
        )
    elif detected != declared_kind:
        failures.append(
            f"manifest declares {container} ({declared_kind}) but code root is {detected}"
        )
    return {
        "passed": not failures,
        "failures": failures,
        "evidence": evidence,
    }


def check_entry_wired(kotlin_sources: list[tuple[Path, str]]) -> dict[str, Any]:
    found: dict[str, list[str]] = {token: [] for token in ENTRY_TOKENS}
    for path, text in kotlin_sources:
        for token in ENTRY_TOKENS:
            if token in text:
                found[token].append(path.name)
    failures: list[str] = []
    if not found["mainApp"]:
        failures.append("no `mainApp` entry function found in any .kt file")
    return {
        "passed": not failures,
        "failures": failures,
        "evidence": {token: sorted(set(files)) for token, files in found.items() if files},
    }


def check_manifest_consistency(
    container: str | None,
    manifests: list[tuple[Path, str]],
) -> dict[str, Any]:
    failures: list[str] = []
    evidence: dict[str, Any] = {}
    if not manifests:
        return {
            "passed": True,
            "failures": [],
            "evidence": {"note": "no AndroidManifest.xml found; skipped"},
        }
    has_windowcontainer_meta = False
    has_in_volume_style = False
    manifest_meta: dict[str, set[str]] = {}
    for path, text in manifests:
        if "pico.spatial.windowcontainer.id" in text:
            has_windowcontainer_meta = True
            evidence[path.name] = "declares pico.spatial.windowcontainer.id"
        if "pico.spatial.windowcontainer.style" in text and 'value="2"' in text:
            has_in_volume_style = True
        for meta_name, meta_value in re.findall(
            r'android:name="([^"]+)"\s+android:value="([^"]+)"',
            text,
        ):
            manifest_meta.setdefault(meta_name, set()).add(meta_value)
    declared_kind = container_kind(container)
    if declared_kind == "window":
        if not has_windowcontainer_meta:
            failures.append(
                "WindowContainer flow but manifest is missing pico.spatial.windowcontainer.id meta-data"
            )
        if container == "IN_VOLUME" and not has_in_volume_style:
            failures.append(
                "container=IN_VOLUME but manifest does not set pico.spatial.windowcontainer.style=2"
            )
    elif declared_kind == "stage":
        if "pico.spatial.stage.id" not in manifest_meta:
            failures.append("Stage flow but manifest is missing pico.spatial.stage.id meta-data")
        expected = STAGE_MANIFEST_EXPECTATIONS.get(str(container), {})
        for name, expected_value in expected.items():
            actual_values = manifest_meta.get(name, set())
            if expected_value not in actual_values:
                actual = ", ".join(sorted(actual_values)) if actual_values else "<missing>"
                failures.append(
                    f"container={container} expects {name}={expected_value}, got {actual}"
                )
        if expected:
            evidence["stage_manifest"] = {
                name: sorted(manifest_meta.get(name, set())) for name in expected.keys()
            }
    return {"passed": not failures, "failures": failures, "evidence": evidence}


def check_stage_api_legality(
    container: str | None,
    kotlin_sources: list[tuple[Path, str]],
) -> dict[str, Any]:
    declared_kind = container_kind(container)
    hits: list[str] = []
    compiled = [re.compile(p) for p in STAGE_ONLY_API_PATTERNS]
    for path, text in kotlin_sources:
        for pattern in compiled:
            for match in pattern.finditer(text):
                hits.append(f"{path.name}: {match.group(0)}")

    # A window-default app MAY legally declare a secondary `Stage(id=...)` block
    # and use Stage-only APIs inside it (shared-space default + open immersive
    # stage on demand). Detect any secondary stage so we don't hard-fail that
    # legitimate pattern; regex can't scope which block an API sits in, so we
    # degrade to a warning instead of a failure when a secondary stage exists.
    has_secondary_stage = any(
        re.search(SECONDARY_STAGE_PATTERN, strip_comments_and_imports(text))
        for _, text in kotlin_sources
    )

    failures: list[str] = []
    warnings: list[str] = []
    if hits and declared_kind == "window":
        if has_secondary_stage:
            warnings.append(
                "WindowContainer default root uses Stage-only API symbols; this is "
                "legal only if they live inside a secondary Stage(id=...) block — "
                "verify scope: " + ", ".join(sorted(set(hits)))
            )
        else:
            failures.append(
                "WindowContainer flow uses Stage-only API symbols with no secondary "
                "Stage(id=...) declared: " + ", ".join(sorted(set(hits)))
            )
    return {"passed": not failures, "failures": failures, "warnings": warnings, "evidence": hits}


_IMPORT_RE = re.compile(r"^\s*import\s+([\w.]+)", re.MULTILINE)


def check_whitelist_components(
    kotlin_sources: list[tuple[Path, str]],
) -> dict[str, Any]:
    suspicious: dict[str, list[str]] = {}
    for path, text in kotlin_sources:
        for match in _IMPORT_RE.finditer(text):
            symbol = match.group(1)
            if symbol.startswith("com.pico.spatial."):
                if not any(symbol.startswith(p) for p in ALLOWED_SPATIAL_PACKAGE_PREFIXES):
                    suspicious.setdefault(symbol, []).append(path.name)
    failures: list[str] = []
    # Suspicious imports are reported as warnings (no failure) — they only
    # become failures when they look clearly invented (no `.` after the prefix).
    for symbol in suspicious:
        if symbol.endswith("."):
            failures.append(f"malformed spatial import: {symbol}")
    return {
        "passed": not failures,
        "failures": failures,
        "warnings": [
            f"unrecognized spatial import (verify against whitelist): {sym}"
            for sym in sorted(suspicious)
        ],
    }


def _invocations(combined_body: str, names: set[str]) -> set[str]:
    """Which of `names` are actually invoked (`Name(`, `Name {`, `Name<`)."""
    found: set[str] = set()
    for name in names:
        if re.search(rf"\b{re.escape(name)}\s*[\(<{{]", combined_body):
            found.add(name)
    return found


# Rough size signal: how much UI surface the module actually has. Drives which
# component floor applies, so a two-control patch is not held to the same bar as
# a full product screen.
def _ui_scale(combined_body: str, profile: str) -> tuple[str, int]:
    composables = len(re.findall(r"@Composable", combined_body))
    if profile == "patch":
        return "patch", composables
    if composables >= 5:
        return "non_trivial", composables
    return "small", composables


COMPONENT_FLOORS = {"non_trivial": 4, "small": 2, "patch": 1}


def check_spatialui_component_floor(
    kotlin_sources: list[tuple[Path, str]],
    profile: str = "default",
) -> dict[str, Any]:
    """Positive evidence that SpatialUI built-ins were used, not hand-rolled UI.

    Replaces the contract-declared `required_spatialui_components` list. Without
    a contract to name the expected components, the machine-checkable question
    becomes "did this code reach for the SpatialUI vocabulary at all, or did it
    rebuild everything out of Box + Text + clickable?".

    Reported as warnings, not failures: the floor is a heuristic and this
    scanner treats false positives as worse than false negatives. Semantic
    component choice stays an LLM-owned review item.
    """
    allowed, forbidden = load_component_vocabulary()
    if not allowed:
        # Never silently pass: an empty vocabulary means the reference docs moved
        # or the parser broke, which would disable this check entirely.
        return {
            "passed": False,
            "failures": [
                "component vocabulary could not be parsed from references/"
                "spatial-ui-components.md; cannot verify SpatialUI component usage"
            ],
            "evidence": {},
        }

    combined_body = "\n".join(strip_comments_and_imports(text) for _, text in kotlin_sources)
    used = _invocations(combined_body, allowed)
    scale, composables = _ui_scale(combined_body, profile)
    floor = COMPONENT_FLOORS[scale]

    warnings: list[str] = []
    if len(used) < floor:
        warnings.append(
            f"only {len(used)} SpatialUI built-in component(s) used ({', '.join(sorted(used)) or 'none'}); "
            f"a {scale} UI ({composables} @Composable) is expected to use at least {floor}. "
            "Prefer built-ins from references/spatial-ui-components.md over hand-rolled "
            "Box + Text + clickable equivalents."
        )

    return {
        "passed": True,
        "failures": [],
        "warnings": warnings,
        "evidence": {
            "used_components": sorted(used),
            "vocabulary_size": len(allowed),
            "ui_scale": scale,
            "composables": composables,
            "floor": floor,
        },
    }


def check_invented_component_names(
    kotlin_sources: list[tuple[Path, str]],
) -> dict[str, Any]:
    """Flag SDK names the reference explicitly says do not exist."""
    _, forbidden = load_component_vocabulary()
    if not forbidden:
        return {"passed": True, "failures": [], "evidence": {"note": "no forbidden list parsed"}}

    combined_body = "\n".join(strip_comments_and_imports(text) for _, text in kotlin_sources)
    used = _invocations(combined_body, forbidden)
    failures = [
        f"invented SDK component {name}(...) — not in references/spatial-ui-components.md; "
        "use a documented built-in or a Box with // TODO(missing-component)"
        for name in sorted(used)
    ]
    return {
        "passed": not failures,
        "failures": failures,
        "evidence": {"forbidden_used": sorted(used)},
    }


# Edge-pinned chrome that was hand-rolled instead of using TabBar / Toolbar /
# Subwindow. Formerly gated on a contract declaration; now a standalone
# anti-pattern check, with an explicit opt-out for deliberate in-page overlays.
_MANUAL_EDGE_OVERLAY_RE = re.compile(
    r"Box\s*\([^)]*\.align\s*\(\s*Alignment\."
    r"(?:CenterStart|CenterEnd|TopCenter|BottomCenter|TopStart|TopEnd|BottomStart|BottomEnd)"
    r"[\s\S]{0,500}\b(?:IconButton|Column|Row)\b"
)
_INTENTIONAL_OVERLAY_MARKER = "spatial-ui: intentional-in-page-overlay"


def check_window_chrome_ornaments(
    kotlin_sources: list[tuple[Path, str]],
) -> dict[str, Any]:
    combined_raw = "\n".join(text for _, text in kotlin_sources)
    combined_body = "\n".join(strip_comments_and_imports(text) for _, text in kotlin_sources)

    has_tabbar = re.search(r"\bTabBar\s*[\(\{]", combined_body) is not None
    has_toolbar = re.search(r"\bToolbar\s*[\(\{]", combined_body) is not None
    has_subwindow = re.search(r"\bSubwindow\s*[\(\{]", combined_body) is not None
    has_window_fitting = has_tabbar or has_toolbar or has_subwindow
    manual_edge_overlay = _MANUAL_EDGE_OVERLAY_RE.search(combined_body) is not None
    # Comments are stripped from `combined_body`, so read the marker from raw text.
    declared_intentional = _INTENTIONAL_OVERLAY_MARKER in combined_raw

    warnings: list[str] = []
    if manual_edge_overlay and not has_window_fitting and not declared_intentional:
        warnings.append(
            "edge-pinned strip looks hand-rolled with Box(Modifier.align(...)); long-lived edge "
            "navigation / action strips are window-level fittings (TabBar / Toolbar / Subwindow), "
            "not page children. See references/spatial-windows-guide.md. If this really is an "
            f"in-page overlay, mark it with `// {_INTENTIONAL_OVERLAY_MARKER} <reason>`."
        )

    return {
        "passed": True,
        "failures": [],
        "warnings": warnings,
        "evidence": {
            "has_tabbar": has_tabbar,
            "has_toolbar": has_toolbar,
            "has_subwindow": has_subwindow,
            "manual_edge_overlay": manual_edge_overlay,
            "declared_intentional": declared_intentional,
        },
    }


def check_root_change_guard(target: Path, generation_mode: str) -> dict[str, Any]:
    """Guard against silently switching an existing module's root architecture.

    Replaces the artifact-based `existing_module_root_preserved` check. Instead
    of comparing a declared `existing_root_container` field, it asks git what the
    manifest's root meta-data looked like before this run.

    Only meaningful for `existing_module` runs inside a git work tree; anywhere
    else it reports skipped rather than inventing a verdict.
    """
    if generation_mode != "existing_module":
        return {
            "passed": True,
            "failures": [],
            "evidence": {"note": f"generation_mode={generation_mode}; guard not applicable"},
        }

    manifests = collect_manifests(target)
    if not manifests:
        return {
            "passed": True,
            "failures": [],
            "evidence": {"note": "no AndroidManifest.xml found; skipped"},
        }

    failures: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, Any] = {}
    for manifest in manifests:
        try:
            completed = subprocess.run(
                ["git", "show", f"HEAD:./{manifest.relative_to(target)}"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except (OSError, ValueError):
            warnings.append(f"could not read git history for {manifest.name}; guard skipped")
            continue
        if completed.returncode != 0 or not completed.stdout.strip():
            warnings.append(f"{manifest.name} has no committed baseline; guard skipped")
            continue

        before, _ = infer_container([(manifest, completed.stdout)], [])
        after, _ = infer_container([(manifest, read_text_safe(manifest))], [])
        evidence[manifest.name] = {"before": before, "after": after}
        if before and after and container_kind(before) != container_kind(after):
            failures.append(
                f"{manifest.name}: root architecture changed from {before} to {after}. "
                "Switching a WindowContainer app to Stage (or back) is a Decide-phase "
                "change: re-run the container decision and update the manifest, entry "
                "chain, coordinates, and ornaments together — not as a build-time fix."
            )

    return {
        "passed": not failures,
        "failures": failures,
        "warnings": warnings,
        "evidence": evidence,
    }


def scan(
    target: Path,
    scratch_dir: Path | None = None,
    generation_mode: str = "unknown",
    profile: str = "default",
) -> dict[str, Any]:
    actual_scratch = scratch_dir or (target / ".scratch")
    actual_scratch.mkdir(parents=True, exist_ok=True)

    kotlin_paths = collect_kotlin_files(target)
    kotlin_sources = [(p, read_text_safe(p)) for p in kotlin_paths]
    manifest_paths = collect_manifests(target)
    manifests = [(p, read_text_safe(p)) for p in manifest_paths]

    container, container_evidence = infer_container(manifests, kotlin_sources)

    checks: dict[str, Any] = {
        "root_match": check_root_match(container, kotlin_sources),
        "entry_wired": check_entry_wired(kotlin_sources),
        "manifest_consistency": check_manifest_consistency(container, manifests),
        "stage_api_legality": check_stage_api_legality(container, kotlin_sources),
        "whitelist_components": check_whitelist_components(kotlin_sources),
        "invented_component_names": check_invented_component_names(kotlin_sources),
        "spatialui_component_floor": check_spatialui_component_floor(kotlin_sources, profile),
        "window_chrome_ornaments": check_window_chrome_ornaments(kotlin_sources),
        "root_change_guard": check_root_change_guard(target, generation_mode),
    }
    failures: list[str] = []
    warnings: list[str] = []
    for name, result in checks.items():
        for failure in result.get("failures", []):
            failures.append(f"[{name}] {failure}")
        for warning in result.get("warnings", []):
            warnings.append(f"[{name}] {warning}")

    summary = {
        "schema_version": 2,
        "scanned": {
            "kotlin_files": len(kotlin_paths),
            "manifest_files": len(manifest_paths),
        },
        "container": container,
        "container_evidence": container_evidence,
        "checks": checks,
        "failures_or_explicit_none": failures if failures else "none",
        "warnings_or_explicit_none": warnings if warnings else "none",
        "passed": not failures,
    }
    output_path = actual_scratch / "implementation_scan_result.json"
    output_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[impl-scan] WROTE {output_path}")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target", required=True, help="Project directory containing the generated sources"
    )
    parser.add_argument(
        "--scratch-dir",
        help="Optional override for the scratch directory. Defaults to <target>/.scratch",
    )
    parser.add_argument(
        "--generation-mode",
        default="unknown",
        choices=["existing_module", "new_project", "unknown"],
        help="Enables the root-architecture guard for existing_module runs",
    )
    parser.add_argument(
        "--profile",
        default="default",
        choices=["default", "patch"],
        help="Use 'patch' for bounded incremental edits (lower component floor)",
    )
    args = parser.parse_args(argv)

    target = Path(args.target).expanduser().resolve()
    scratch_dir = Path(args.scratch_dir).expanduser().resolve() if args.scratch_dir else None
    summary = scan(target, scratch_dir, args.generation_mode, args.profile)

    if isinstance(summary["warnings_or_explicit_none"], list):
        for warning in summary["warnings_or_explicit_none"]:
            print(f"[impl-scan] WARN {warning}")

    if not summary["passed"]:
        failures = summary["failures_or_explicit_none"]
        raise SystemExit("[impl-scan] BLOCKED\n- " + "\n- ".join(failures))

    print(
        f"[impl-scan] SUCCESS scanned {summary['scanned']['kotlin_files']} kotlin files, "
        f"{summary['scanned']['manifest_files']} manifest files, container={summary['container']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
