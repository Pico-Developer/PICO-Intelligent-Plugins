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
- side_navigation_item_height — explicit minimum 48dp unless authoritatively overridden
- titlebar_title_weight      — explicit primary-title weight 700 unless overridden
- titlebar_alignment         — TitleBar alignment follows title-only versus search composition
                               (advisory; accepted source overrides need review)
- titlebar_search_layout     — title + SearchField slots use the canonical
                               full-width row and weighted flexible space (warns)
- button_container_semantics — Button is not used as a rich layout/read-only shell (fails)
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
from collections.abc import Iterator
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
    text = re.sub(
        r"/\*.*?\*/",
        lambda match: "\n" * match.group(0).count("\n"),
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r"^[ \t]*//.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[ \t]*import[ \t]+.*$", "", text, flags=re.MULTILINE)
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


def _split_top_level_arguments(text: str) -> Iterator[str]:
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(text):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char in "({[":
            depth += 1
        elif char in ")}]":
            depth -= 1
        elif char == "," and depth == 0:
            yield text[start:index]
            start = index + 1
    yield text[start:]


def check_titlebar_alignment(
    kotlin_sources: list[tuple[Path, str]],
    generation_mode: str = "new_project",
    design_spec_path: Path | None = None,
    target: Path | None = None,
) -> dict[str, Any]:
    """Compare declared alignment when spec is supplied; legacy callers get advisory inference."""
    if design_spec_path is not None:
        return check_component_contracts(kotlin_sources, design_spec_path, "TitleBar", target)
    findings: list[str] = []
    evidence: list[dict[str, Any]] = []
    for path, text in kotlin_sources:
        body = strip_comments_and_imports(text)
        # Preserve offsets/lines while hiding literals and remaining inline
        # comments; a label saying "SearchField()" is not a search composable.
        body = re.sub(
            r'"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|//[^\n]*',
            lambda match: re.sub(r"[^\n]", " ", match.group(0)),
            body,
        )
        for start, title_block in _titlebar_title_blocks(body):
            has_search = bool(re.search(r"\bSearchField\s*\(", title_block))
            calls = set(re.findall(r"\b([A-Z]\w*)\s*\(", title_block))
            title_only = "Text" in calls and calls <= {"Text", "Column"}
            if not has_search and not (
                calls and calls <= {"Text", "Column", "Row", "Icon", "Image", "Button"}
            ):
                continue
            opening = body.find("(", start)
            closing = _matching_parenthesis(body, opening)
            if closing is None:
                continue
            arguments = body[opening + 1 : closing]
            # The title lambda may itself contain nested calls; inspect only
            # top-level named arguments of this TitleBar invocation.
            alignment = next(
                (
                    arg
                    for arg in _split_top_level_arguments(arguments)
                    if re.match(r"\s*titleAlignment\s*=", arg)
                ),
                "",
            )
            has_actions = any(
                re.match(r"\s*(?:leadingActions|trailingActions)\s*=", arg)
                and not re.search(r"=\s*\{\s*\}\s*$", arg)
                for arg in _split_top_level_arguments(arguments)
            )
            if has_search:
                composition = "search-containing"
            elif has_actions:
                composition = "action-containing"
            else:
                composition = "title-only" if title_only else "compound-title"
            expected = "CenterInBar" if title_only and not has_actions else "Center"
            actual = re.search(r"\bTitleAlignment\s*\.\s*(\w+)", alignment)
            line = body.count("\n", 0, start) + 1
            location = f"{path.name}:{line}"
            evidence.append(
                {
                    "location": location,
                    "expected": expected,
                    "actual": actual.group(1) if actual else "implicit_or_dynamic",
                }
            )
            if actual is None:
                # Defaults and computed alignment require SDK/source inspection.
                findings.append(
                    f"{location} has implicit or dynamic titleAlignment; verify "
                    f"TitleAlignment.{expected} against its composition and accepted source"
                )
                continue
            if actual.group(1) != expected:
                findings.append(
                    f"{location} uses TitleAlignment.{actual.group(1)}; "
                    f"{composition} TitleBars "
                    f"must use TitleAlignment.{expected} unless source evidence overrides it"
                )
    # Static scanning cannot see accepted source overrides. Keep these findings
    # advisory; source/spec and rendered review resolve the intended alignment.
    warnings = (
        findings
        if generation_mode == "new_project"
        else [
            f"{finding}; reported as a warning because existing-module scans cannot "
            "prove that this usage was introduced by the current change"
            for finding in findings
        ]
    )
    return {
        "passed": True,
        "failures": [],
        "warnings": warnings,
        "evidence": {"compositions": evidence},
    }


def _matching_parenthesis(text: str, opening_index: int) -> int | None:
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(opening_index, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def _matching_brace(text: str, opening_index: int) -> int | None:
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(opening_index, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def _compose_calls(text: str, name: str) -> Iterator[tuple[int, str, int, str]]:
    """Read balanced call arguments and optional trailing content lambda."""
    for match in re.finditer(r"\b" + re.escape(name) + r"\s*\(", text):
        opening = text.find("(", match.start())
        closing = _matching_parenthesis(text, opening)
        if closing is None:
            continue
        cursor = closing + 1
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        end = _matching_brace(text, cursor) if text[cursor : cursor + 1] == "{" else None
        yield (
            match.start(),
            text[opening + 1 : closing],
            end or closing,
            (text[cursor + 1 : end] if end is not None else ""),
        )


def _named_arguments(arguments: str) -> dict[str, str]:
    result = {}
    for argument in _split_top_level_arguments(arguments):
        match = re.match(r"\s*(\w+)\s*=([\s\S]*)", argument)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def check_component_defaults(
    kotlin_sources: list[tuple[Path, str]], spec_path: Path, component: str
) -> dict[str, Any]:
    """Check concrete defaults; evidence grants only a property-specific override."""
    failures: list[str] = []
    warnings: list[str] = []
    evidence: list[dict[str, Any]] = []
    masked_sources = []
    for path, text in kotlin_sources:
        markers = []

        def mask_source(match: re.Match[str]) -> str:
            marker = re.fullmatch(r"//\s*design-node:\s*([\w., -]+)\s*", match.group(0))
            if marker:
                markers.append((match.end(), re.findall(r"[\w.-]+", marker.group(1))))
            return re.sub(r"[^\n]", " ", match.group(0))

        body = re.sub(
            r'/\*[\s\S]*?\*/|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|//[^\n]*', mask_source, text
        )
        masked_sources.append((path, body, markers))
    if not any(any(_compose_calls(body, component)) for _, body, _ in masked_sources):
        return {"passed": True, "failures": [], "warnings": [], "evidence": []}
    height = component == "SideNavigationItem"
    tag = "sui-side-navigation-item" if height else "sui-title-bar"
    key = "min-height-dp" if height else "title-font-weight"
    default = 48 if height else 700
    try:
        nodes = {
            n["id"]: n
            for n in json.loads(spec_path.read_text(encoding="utf-8"))["nodes"]
            if n.get("component") == tag
        }
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        nodes = {}
        warnings.append(
            f"{component}: accepted spec unavailable; override correspondence unverified"
        )

    def requirement(node: dict[str, Any]) -> tuple[float, bool, bool]:
        props = node.get("props") or {}
        layout = node.get("layout") or {}
        if not isinstance(props, dict) or not isinstance(layout, dict):
            warnings.append(
                f"{component} node {node['id']}: invalid property declaration; retain default"
            )
            return default, False, False
        fixed = height and "heightDp" in layout
        value = layout.get("heightDp") if fixed else props.get(key)
        if value is None:
            return default, False, False
        origin = node.get("styleOverrideEvidence", {})
        valid = (
            isinstance(origin, dict)
            and origin.get("source") in {"user", "figma", "screenshot"}
            and isinstance(origin.get("reference"), str)
            and bool(origin["reference"].strip())
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
            and value > 0
            and (height or (value <= 1000 and int(value) == value))
        )
        if not valid:
            warnings.append(
                f"{component} node {node['id']}: invalid or unevidenced {key}/height override; retain default"
            )
            return default, False, False
        return value, fixed, True

    requirements = {node_id: requirement(n) for node_id, n in nodes.items()}
    for path, body, markers in masked_sources:
        for start, args_text, _, _ in _compose_calls(body, component):
            location = f"{path.name}:{body.count(chr(10), 0, start) + 1}"
            ids = [
                node_id
                for marker_end, values in markers
                if marker_end <= start and not body[marker_end:start].strip()
                for node_id in values
            ]
            linked = [requirements[i] for i in ids if i in requirements]
            if ids and len(linked) != len(ids):
                warnings.append(
                    f"{location}: unknown {component} design-node marker; correspondence unverified"
                )
            if not linked and any(r[2] for r in requirements.values()):
                warnings.append(
                    f"{location}: explicit {key} requires a unique design-node mapping; unverified"
                )
                evidence.append({"location": location, "property": key, "verified": False})
                continue
            if len(set(linked)) > 1:
                warnings.append(
                    f"{location}: conflicting state-node {key} requirements; unverified"
                )
                evidence.append({"location": location, "property": key, "verified": False})
                continue
            expected, fixed, overridden = linked[0] if linked else (default, False, False)
            args = _named_arguments(args_text)
            actual = None
            uncertain = bool(ids and len(linked) != len(ids))
            if height:
                modifier = args.get("modifier", "")
                constraints = list(
                    re.finditer(
                        r"\.(heightIn|requiredHeightIn|height|requiredHeight|sizeIn|size|requiredSize)\s*\(([^()]*)\)",
                        modifier,
                    )
                )
                values = []
                fixed_values = []
                for c in constraints:
                    name, parameters = c.groups()
                    if name in {"heightIn", "requiredHeightIn", "sizeIn"}:
                        k = "minHeight" if name == "sizeIn" else "min"
                        parameters = _named_arguments(parameters).get(k, "")
                        if not parameters:
                            continue
                    else:
                        parameters = re.sub(r"^(?:height|size)\s*=\s*", "", parameters.strip())
                    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*\.\s*dp\s*", parameters)
                    if match:
                        values.append(float(match.group(1)))
                        if name in {"height", "requiredHeight", "size", "requiredSize"}:
                            fixed_values.append(float(match.group(1)))
                    else:
                        uncertain = True
                actual = min(values) if values else None
                if fixed:
                    actual = fixed_values[0] if len(set(fixed_values)) == 1 else None
                    if actual is not None and any(v > actual for v in values):
                        uncertain = True
                # Any explicit max smaller than the floor makes the chain suspect/incorrect.
                for m in re.finditer(
                    r"\b(?:max|maxHeight)\s*=\s*(\d+(?:\.\d+)?)\s*\.\s*dp", modifier
                ):
                    maximum = float(m.group(1))
                    if maximum < expected:
                        actual = maximum
                        uncertain = False
                known = {"clickable", "fillMaxWidth", "padding", "semantics", "testTag", "then"}
                helpers = re.findall(r"\.(\w+)\s*\(", modifier)
                if "then" in helpers:
                    uncertain = True
                if not constraints and (
                    any(h not in known for h in helpers)
                    or re.match(r"\s*(?!Modifier\b)\w+", modifier)
                ):
                    uncertain = True
            else:
                title = args.get("title", "")
                texts = list(_compose_calls(title, "Text"))
                if not texts:
                    uncertain = True
                else:
                    # Do not mistake a search placeholder or action label for a title.
                    prefix = title[: texts[0][0]]
                    if re.search(r"\b(?!(?:Column|Row|Box)\b)[A-Z]\w*\s*\(", prefix):
                        uncertain = True
                    text_args = _named_arguments(texts[0][1])
                    weight = text_args.get("fontWeight", "")
                    weights = {
                        "Bold": 700,
                        "SemiBold": 600,
                        "Normal": 400,
                        "Medium": 500,
                        "Light": 300,
                        "Thin": 100,
                        "ExtraLight": 200,
                        "ExtraBold": 800,
                        "Black": 900,
                    }
                    m = re.fullmatch(
                        r"(?:androidx\.compose\.ui\.text\.font\.)?FontWeight\.(\w+)", weight
                    )
                    n = re.fullmatch(r"FontWeight\(\s*(\d+)\s*\)", weight)
                    if m:
                        actual = weights.get(m.group(1))
                    elif n:
                        actual = int(n.group(1))
                    elif weight or "style" in text_args:
                        uncertain = True
            satisfied = actual is not None and (
                actual == expected if fixed or not height else actual >= expected
            )
            verified = satisfied and not uncertain
            record = {
                "location": location,
                "nodes": ids,
                "property": key,
                "expected": expected,
                "source": "explicit" if overridden else "default",
                "actual": actual,
                "verified": verified,
            }
            evidence.append(record)
            if uncertain:
                warnings.append(
                    f"{location}: dynamic/opaque {key} cannot be verified; expected {expected}"
                )
            elif not satisfied:
                failures.append(
                    f"{location}: {key} expected {expected} ({record['source']}), actual {actual if actual is not None else 'missing explicit constraint'}"
                )
    return {
        "passed": not failures,
        "failures": failures,
        "warnings": warnings,
        "evidence": evidence,
    }


def check_side_navigation_spacing(
    kotlin_sources: list[tuple[Path, str]],
    design_spec_path: Path,
) -> dict[str, Any]:
    """Advisory canonical checks only; source overrides and opaque helpers need review."""
    warnings: list[str] = []
    evidence: list[dict[str, Any]] = []
    sources = []
    for path, text in kotlin_sources:
        body = strip_comments_and_imports(text)
        body = re.sub(
            r'"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|//[^\n]*',
            lambda m: re.sub(r"[^\n]", " ", m.group(0)),
            body,
        )
        sources.extend((path, body, call) for call in _compose_calls(body, "SideNavigation"))
    if not sources:
        return {"passed": True, "failures": [], "warnings": [], "evidence": []}
    header_override = item_padding_override = gap_override = False
    try:
        spec = json.loads(design_spec_path.read_text(encoding="utf-8"))
        nodes = {node["id"]: node for node in spec["nodes"]}
        policies = set()
        for node in nodes.values():
            if node.get("component") != "sui-side-navigation":
                continue
            policy = node.get("props", {}).get("spacing-policy")
            pending = [node["id"]]
            seen = set()
            overridden = False
            while pending:
                node_id = pending.pop()
                if node_id in seen:
                    continue
                seen.add(node_id)
                child = nodes[node_id]
                overridden |= any(k in child.get("layout", {}) for k in ("paddingDp", "gapDp"))
                overridden |= "contentPadding" in child.get("props", {})
                is_item = child.get("component") == "sui-side-navigation-item"
                # Header spacing and parent-list gap are different owners.
                descendants = list(child.get("children", []))
                visited = set()
                contains_items = is_item
                while descendants:
                    descendant_id = descendants.pop()
                    if descendant_id in visited:
                        continue
                    visited.add(descendant_id)
                    descendant = nodes[descendant_id]
                    contains_items |= descendant.get("component") == "sui-side-navigation-item"
                    descendants.extend(descendant.get("children", []))
                header_override |= not contains_items and "paddingDp" in child.get("layout", {})
                item_padding_override |= is_item and (
                    "contentPadding" in child.get("props", {})
                    or "paddingDp" in child.get("layout", {})
                )
                gap_override |= (
                    contains_items and not is_item and "gapDp" in child.get("layout", {})
                )
                pending.extend(child.get("children", []))
            if policy is None:
                policy = "explicit" if overridden else "canonical"
            elif policy == "canonical" and overridden:
                policy = "explicit"  # Do not overwrite child source overrides.
            policies.add(policy)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        policies = set()
    if policies != {"canonical"}:
        warnings.append(
            f"SideNavigation spacing was not statically verified: check {design_spec_path} "
            "for explicit overrides, mixed policies, or missing/invalid spec. Resolve each "
            "props[spacing-policy] before applying the canonical example."
        )
        # Continue with independent properties; an explicit spacing policy alone
        # is not authority to cancel every restoration default.

    def has_dp(text: str, key: str, value: int) -> bool:
        return bool(re.search(r"\b" + key + r"\s*=\s*" + str(value) + r"(?:\.0)?\.dp\b", text))

    for path, body, (start, arguments, _, content) in sources:
        location = f"{path.name}:{body.count(chr(10), 0, start) + 1}"
        args = _named_arguments(arguments)
        header = args.get("header", "")
        problems = []
        boxes = list(_compose_calls(header, "Box"))
        if header_override:
            problems.append("header padding has explicit overrides; verify source correspondence")
        elif not boxes:
            problems.append("missing or opaque header title Box")
        else:
            _, box_args, _, box_content = boxes[0]
            box = _named_arguments(box_args)
            modifier = box.get("modifier", "")
            if not (
                re.search(r"\.height\(\s*96(?:\.0)?\.dp\s*\)", modifier)
                and all(
                    has_dp(modifier, k, v) for k, v in (("start", 8), ("top", 31), ("bottom", 31))
                )
                and box.get("contentAlignment") == "Alignment.CenterStart"
                and re.search(r"\bText\s*\(", box_content)
            ):
                problems.append(
                    "unverified 96dp centered title Box with start 8dp and top/bottom 31dp"
                )
        if "contentPadding" in args:
            problems.append("SideNavigation contentPadding overrides the canonical SDK inset")
        searches = list(_compose_calls(header, "SearchField"))
        spacers = list(_compose_calls(header, "Spacer"))
        if searches:
            search_start, search_args, search_end, _ = searches[0]
            search_modifier = _named_arguments(search_args).get("modifier", "")
            if "padding" in search_modifier:
                problems.append(
                    "SearchField inset requires spec review; canonical top inset is 0dp"
                )
            if not any(
                pos > search_end and re.search(r"\.height\(\s*28(?:\.0)?\.dp\s*\)", a)
                for pos, a, _, _ in spacers
            ):
                problems.append("missing or opaque 28dp Spacer after SearchField")
            # A spacer or padded header before search shifts its visible content top.
            if any(pos < search_start for pos, _, _, _ in spacers):
                problems.append("unexpected Spacer before SearchField")
        elif spacers:
            problems.append("title-only header must omit the search Spacer")
        for _, column_args, _, _ in _compose_calls(header, "Column"):
            if re.search(r"\.padding\s*\(", _named_arguments(column_args).get("modifier", "")):
                problems.append("whole header Column padding requires spec review")
        items = list(_compose_calls(content, "SideNavigationItem"))
        columns = list(_compose_calls(content, "Column"))
        if not items:
            problems.append("item composition is opaque; verify item padding and parent list gap")
        for item_start, item_args, _, _ in items:
            padding = _named_arguments(item_args).get("contentPadding", "")
            if item_padding_override:
                problems.append("item padding has explicit overrides; verify source correspondence")
            elif not all(
                has_dp(padding, k, v)
                for k, v in (("start", 16), ("top", 8), ("end", 8), ("bottom", 8))
            ):
                problems.append(
                    "missing or dynamic item contentPadding: start 16dp, top/end/bottom 8dp"
                )
            parents = [c for c in columns if c[0] < item_start < c[2]]
            parent = max(parents, key=lambda c: c[0]) if parents else None
            arrangement = (
                _named_arguments(parent[1]).get("verticalArrangement", "") if parent else ""
            )
            if gap_override:
                problems.append("list gap has explicit overrides; verify source correspondence")
            elif not re.fullmatch(r"Arrangement\.spacedBy\(\s*4(?:\.0)?\.dp\s*\)", arrangement):
                problems.append("missing or dynamic 4dp gap on the item-containing Column")
        if policies == {"canonical"}:
            evidence.append({"location": location, "policy": "canonical", "verified": not problems})
        for problem in dict.fromkeys(problems):
            warnings.append(
                f"{location}: {problem}; check spec spacing-policy/overrides and the canonical SideNavigation example."
            )
    return {"passed": True, "failures": [], "warnings": warnings, "evidence": evidence}


def check_component_contracts(
    kotlin_sources: list[tuple[Path, str]],
    spec_path: Path,
    component: str,
    target: Path | None = None,
) -> dict[str, Any]:
    """Advisory source/spec comparisons; markers and receipts locate, never prove values."""
    target = target or spec_path.parent.parent
    warnings: list[str] = []
    evidence: list[dict[str, Any]] = []
    tag = "sui-title-bar" if component == "TitleBar" else "sui-list-item"
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        nodes = {n["id"]: n for n in spec["nodes"] if n.get("component") == tag}
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        nodes = {}
        warnings.append(
            f"{component} spec unavailable at {spec_path}; check the accepted spec before applying defaults; source/spec correspondence is unverified."
        )
    try:
        receipt = json.loads(
            (spec_path.parent / "design_implementation_map.json").read_text(encoding="utf-8")
        )
        mappings = receipt.get("source_mappings", [])
        if not isinstance(mappings, list):
            mappings = []
    except (OSError, ValueError, AttributeError):
        mappings = []
    calls = []
    bodies = {}
    for path, text in kotlin_sources:
        markers = []

        def mask(match: re.Match[str]) -> str:
            token = match.group(0)
            marker = re.fullmatch(r"//\s*design-node:\s*([\w., -]+)\s*", token)
            if marker:
                markers.append((match.end(), re.findall(r"[\w.-]+", marker.group(1))))
            return re.sub(r"[^\n]", " ", token)

        body = re.sub(r'/\*[\s\S]*?\*/|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|//[^\n]*', mask, text)
        bodies[path.resolve()] = body
        for start, args, end, _ in _compose_calls(body, component):
            ids = [
                node_id
                for marker_end, values in markers
                if marker_end <= start and not body[marker_end:start].strip()
                for node_id in values
            ]
            calls.append(
                {
                    "path": path,
                    "start": start,
                    "end": end,
                    "args": _named_arguments(args),
                    "ids": ids,
                    "location": f"{path}:{body.count(chr(10), 0, start) + 1}",
                }
            )
    if not calls and not nodes:
        return {"passed": True, "failures": [], "warnings": [], "evidence": []}
    links: dict[str, list[int]] = {}
    for node_id in nodes:
        candidates = [i for i, call in enumerate(calls) if node_id in call["ids"]]
        if not candidates:
            # A mapping may narrow to a function, but only one call can be resolved.
            for mapping in mappings:
                if not isinstance(mapping, dict) or f"node:{node_id}" not in mapping.get(
                    "design_refs", []
                ):
                    continue
                name = mapping.get("file")
                if not isinstance(name, str):
                    continue
                source_path = (target / name).resolve()
                if not source_path.is_relative_to(target.resolve()):
                    continue
                body = bodies.get(source_path, "")
                ranges = []
                for symbol in mapping.get("symbols", []):
                    if not isinstance(symbol, str):
                        continue
                    for match in re.finditer(r"\bfun\s+" + re.escape(symbol) + r"\s*\(", body):
                        opening = body.find("(", match.start())
                        closing = _matching_parenthesis(body, opening)
                        if closing is None:
                            continue
                        brace = body.find("{", closing)
                        end = _matching_brace(body, brace) if brace >= 0 else None
                        if end is not None and not body[closing + 1 : brace].strip():
                            ranges.append((brace, end))
                candidates.extend(
                    i
                    for i, call in enumerate(calls)
                    if call["path"].resolve() == source_path
                    and not call["ids"]
                    and any(a < call["start"] < b for a, b in ranges)
                )
        candidates = sorted(set(candidates))
        if len(candidates) == 1:
            links[node_id] = candidates
        else:
            warnings.append(
                f"{spec_path} node {node_id}: {len(candidates)} matching {component} calls; correspondence unverified. Add a unique // design-node: {node_id} immediately before the call, or narrow source_mappings to its function."
            )
    for call in calls:
        for node_id in call["ids"]:
            if node_id not in nodes:
                warnings.append(
                    f"{call['location']}: design-node {node_id} is not a {tag} node in the accepted spec; check the marker/component mapping."
                )
    for node_id, node in nodes.items():
        props = node.get("props", {})
        if not isinstance(props, dict):
            props = {}
        if component == "TitleBar":
            value = props.get("title-alignment")
            if value not in ("center", "center-in-bar"):
                warnings.append(
                    f"{spec_path} node {node_id}: missing/invalid title-alignment. Explicitly select center or center-in-bar in spec; do not rely on SDK defaults or restore-time inference."
                )
        else:
            policy = props.get("spacing-policy")
            if policy not in ("canonical", "explicit"):
                warnings.append(
                    f"{spec_path} node {node_id}: missing/invalid spacing-policy. Record canonical for maintained 16dp internal padding, or explicit with internal-padding-dp; legacy omission is only a fallback, not a verified declaration."
                )
    for index, call in enumerate(calls):
        declaration_valid = True
        matched = [node_id for node_id, indices in links.items() if index in indices]
        label = f"{call['location']} nodes {', '.join(matched) or 'unmapped'}"
        if not matched:
            warnings.append(
                f"{label}: source/spec correspondence unverified; add a design-node marker or source mapping before claiming this call matches the design."
            )
        expected_values = []
        for node_id in matched:
            props = nodes[node_id].get("props", {})
            if not isinstance(props, dict):
                props = {}
            if component == "TitleBar":
                expected_values.append(
                    {"center": "Center", "center-in-bar": "CenterInBar"}.get(
                        props.get("title-alignment")
                    )
                )
            elif props.get("spacing-policy", "canonical") == "canonical":
                declaration_valid &= props.get("spacing-policy") == "canonical"
                if "internal-padding-dp" in props:
                    declaration_valid = False
                    warnings.append(
                        f"{label}: canonical mode also declares internal-padding-dp; check whether this is an explicit override and set the policy accordingly."
                    )
                expected_values.append(dict.fromkeys(("start", "top", "end", "bottom"), 16))
            elif props.get("spacing-policy") == "explicit":
                value = props.get("internal-padding-dp")
                if (
                    isinstance(value, dict)
                    and set(value) == {"start", "top", "end", "bottom"}
                    and all(type(v) in (int, float) and v >= 0 for v in value.values())
                ):
                    expected_values.append(value)
                else:
                    warnings.append(
                        f"{label}: explicit padding lacks four numeric internal-padding-dp edges; record the accepted values in spec, not layout.paddingDp."
                    )
                    expected_values.append(None)
            else:
                expected_values.append(None)
        expected = (
            expected_values[0]
            if expected_values and all(v == expected_values[0] for v in expected_values)
            else None
        )
        if matched and expected is None:
            warnings.append(
                f"{label}: expected value unresolved or shared nodes disagree; check spec declarations and state-to-parameter branches manually."
            )
        key = "titleAlignment" if component == "TitleBar" else "padding"
        expression = call["args"].get(key, "")
        actual = None
        if component == "TitleBar":
            match = re.fullmatch(r"TitleAlignment\.(Center|CenterInBar)", expression)
            actual = match.group(1) if match else None
        else:
            # Deliberately limited to the maintained uniform literal example.
            match = re.fullmatch(r"PaddingValues\(\s*(\d+(?:\.\d+)?)\.dp\s*,?\s*\)", expression)
            actual = (
                dict.fromkeys(("start", "top", "end", "bottom"), float(match.group(1)))
                if match
                else None
            )
            if not expression:
                actual = {"start": 16, "top": 16, "end": 4, "bottom": 16}
        if not expression:
            warnings.append(
                f"{label}: missing {key}; "
                + (
                    "SDK ListItem default end=4dp. Check spec overrides; canonical requires padding = PaddingValues(16.dp). Modifier.padding and TrailingGap do not replace internal padding."
                    if component == "ListItem"
                    else "declare the spec-selected TitleAlignment explicitly; omission cannot prove design parity."
                )
            )
        elif actual is None:
            warnings.append(
                f"{label}: {key}={expression} is unverified by this limited scanner. "
                f"Expected {expected if expected is not None else 'resolve from spec'}. Trace variables/helpers or manually verify this spelling; keep correct code, or use "
                + (
                    "PaddingValues(16.dp) for canonical mode."
                    if component == "ListItem"
                    else "the explicit TitleAlignment enum from spec."
                )
            )
        elif expected is not None and actual != expected:
            warnings.append(
                f"{label}: {key} mismatch; expected {expected}, actual {actual}. Check explicit source overrides; otherwise restore the accepted spec value."
            )
        evidence.append(
            {
                "location": call["location"],
                "nodes": matched,
                "expected": expected,
                "actual": actual,
                "verified": bool(matched)
                and declaration_valid
                and expected is not None
                and actual == expected
                and bool(expression),
            }
        )
    return {"passed": True, "failures": [], "warnings": warnings, "evidence": evidence}


def _titlebar_title_blocks(text: str) -> Iterator[tuple[int, str]]:
    for match in re.finditer(r"\bTitleBar\s*\(", text):
        opening_index = text.find("(", match.start())
        closing_index = _matching_parenthesis(text, opening_index)
        if closing_index is None:
            continue
        arguments = text[opening_index + 1 : closing_index]
        title_match = re.search(r"\btitle\s*=\s*\{", arguments)
        if title_match is None:
            continue
        brace_start = opening_index + 1 + title_match.end() - 1
        brace_end = _matching_brace(text, brace_start)
        if brace_end is not None and brace_end < closing_index:
            yield match.start(), text[brace_start + 1 : brace_end]


def check_titlebar_search_layout(
    kotlin_sources: list[tuple[Path, str]],
) -> dict[str, Any]:
    """Warn when a composed title/search slot misses the canonical distribution."""
    warnings: list[str] = []
    evidence: list[dict[str, Any]] = []
    weighted_spacer = re.compile(
        r"\bSpacer\s*\([\s\S]*?\bweight\s*\(\s*1(?:\.0)?f\s*\)",
    )
    for path, text in kotlin_sources:
        body = strip_comments_and_imports(text)
        for start, title_block in _titlebar_title_blocks(body):
            if not re.search(r"\bSearchField\s*\(", title_block):
                continue
            row_match = re.search(r"\bRow\s*\(", title_block)
            row_arguments = ""
            row_body = ""
            if row_match is not None:
                row_open = title_block.find("(", row_match.start())
                row_close = _matching_parenthesis(title_block, row_open)
                if row_close is not None:
                    row_arguments = title_block[row_open + 1 : row_close]
                    row_brace = row_close + 1
                    while row_brace < len(title_block) and title_block[row_brace].isspace():
                        row_brace += 1
                    if row_brace < len(title_block) and title_block[row_brace] == "{":
                        row_end = _matching_brace(title_block, row_brace)
                        if row_end is not None:
                            row_body = title_block[row_brace + 1 : row_end]

            has_full_width = bool(re.search(r"\.fillMaxWidth\s*\(", row_arguments))
            has_weighted_spacer = bool(weighted_spacer.search(row_body))
            has_fixed_spacing = bool(
                re.search(r"\bArrangement\s*\.\s*spacedBy\s*\(", row_arguments)
            )
            line = body.count("\n", 0, start) + 1
            location = f"{path.name}:{line}"
            evidence.append(
                {
                    "location": location,
                    "fill_max_width": has_full_width,
                    "weighted_spacer": has_weighted_spacer,
                    "fixed_spacing": has_fixed_spacing,
                }
            )
            if not has_full_width or not has_weighted_spacer:
                warnings.append(
                    f"{location} composes SearchField in the TitleBar title slot without the "
                    "canonical Row(Modifier.fillMaxWidth()) and Spacer(Modifier.weight(1f)); "
                    "confirm that the accepted design explicitly overrides this default"
                )
            elif has_fixed_spacing:
                warnings.append(
                    f"{location} combines the canonical weighted title/search spacer with "
                    "Arrangement.spacedBy; keep the fixed gap only when the accepted design "
                    "explicitly requires it"
                )

    return {
        "passed": True,
        "failures": [],
        "warnings": warnings,
        "evidence": {"title_search_slots": evidence},
    }


def _button_calls(text: str) -> Iterator[tuple[int, str, int]]:
    for match in re.finditer(r"\bButton\s*\(", text):
        opening_index = text.find("(", match.start())
        closing_index = _matching_parenthesis(text, opening_index)
        if closing_index is None:
            continue
        lambda_index = closing_index + 1
        while lambda_index < len(text) and text[lambda_index].isspace():
            lambda_index += 1
        if lambda_index < len(text) and text[lambda_index] == "{":
            yield match.start(), text[opening_index + 1 : closing_index], lambda_index + 1


def check_button_container_semantics(
    kotlin_sources: list[tuple[Path, str]],
) -> dict[str, Any]:
    """Reject generated Button content containers; comments cannot suppress failures."""
    findings: dict[tuple[str, int], set[str]] = {}
    for path, text in kotlin_sources:
        body = strip_comments_and_imports(text)
        for start, arguments, content_start in _button_calls(body):
            line = body.count("\n", 0, start) + 1
            content_prefix = body[content_start : content_start + 120]
            reasons: set[str] = set()
            if re.match(r"\s*Column\s*[\(\{]", content_prefix):
                reasons.add("wraps a Column")
            if re.search(r"\benabled\s*=\s*false\b", arguments) and re.search(
                r"\bonClick\s*=\s*\{\s*\}", arguments
            ):
                reasons.add("is disabled with an empty onClick")
            if reasons:
                findings.setdefault((path.name, line), set()).update(reasons)

    failures = [
        f"{file}:{line} Button {' and '.join(sorted(reasons))}; Button is a concise "
        "command, not a card, selectable rich layout, metadata group, or read-only "
        "surface. Prefer ListItem, a custom layout with spatial hover plus "
        "clickable/selectable, or a plain read-only layout. Generated Button content "
        "is limited to a concise command label, optional icons, and loading state; "
        "focus, hover, click requirements, and comments do not grant an exemption."
        for (file, line), reasons in sorted(findings.items())
    ]
    return {
        "passed": not failures,
        "failures": failures,
        "warnings": [],
        "evidence": {
            "findings": [
                {"file": file, "line": line, "reasons": sorted(reasons)}
                for (file, line), reasons in sorted(findings.items())
            ],
        },
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
    design_spec_path: Path | None = None,
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
        "titlebar_alignment": check_titlebar_alignment(
            kotlin_sources,
            generation_mode,
            design_spec_path or actual_scratch / "design-spec.json",
            target,
        ),
        "list_item_padding": check_component_contracts(
            kotlin_sources,
            design_spec_path or actual_scratch / "design-spec.json",
            "ListItem",
            target,
        ),
        "titlebar_search_layout": check_titlebar_search_layout(kotlin_sources),
        "side_navigation_item_height": check_component_defaults(
            kotlin_sources,
            design_spec_path or actual_scratch / "design-spec.json",
            "SideNavigationItem",
        ),
        "titlebar_title_weight": check_component_defaults(
            kotlin_sources, design_spec_path or actual_scratch / "design-spec.json", "TitleBar"
        ),
        "side_navigation_spacing": check_side_navigation_spacing(
            kotlin_sources, design_spec_path or actual_scratch / "design-spec.json"
        ),
        "button_container_semantics": check_button_container_semantics(kotlin_sources),
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
    parser.add_argument(
        "--design-spec", help="Accepted design spec; defaults to scratch-dir/design-spec.json"
    )
    args = parser.parse_args(argv)

    target = Path(args.target).expanduser().resolve()
    scratch_dir = Path(args.scratch_dir).expanduser().resolve() if args.scratch_dir else None
    summary = scan(
        target,
        scratch_dir,
        args.generation_mode,
        args.profile,
        Path(args.design_spec).expanduser().resolve() if args.design_spec else None,
    )

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
