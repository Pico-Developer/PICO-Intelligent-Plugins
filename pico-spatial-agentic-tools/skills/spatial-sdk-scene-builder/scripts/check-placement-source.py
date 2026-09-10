#!/usr/bin/env python3
"""Report placement violations and non-blocking implementation advisories."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Violation:
    rule: str
    file: str
    line: int
    evidence: str


@dataclass(frozen=True)
class Advisory:
    rule: str
    file: str
    line: int
    evidence: str
    rationale: str


RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "restricted-coordinate-origin",
        re.compile(r"\blocalSpatialCoordinateSpace\s*\.\s*origin\b"),
    ),
    (
        "manual-px-to-meter",
        re.compile(
            r"\b(?:metersPerPixel|pxToMeters?|pixelsToMeters?|densityToMeters?)\b"
        ),
    ),
    (
        "parallel-bounds-model",
        re.compile(r"\b(?:data\s+)?class\s+Bounds3\b"),
    ),
)

NULL_BOUNDS_OWNER = re.compile(
    r"\bgetVisualBounds\s*\([^)]*\brelativeTo\s*=\s*null\b",
    re.DOTALL,
)
RESOURCE_FACTORY = re.compile(
    r"\b(?:"
    r"MeshResource\s*\.\s*create\w*|"
    r"(?:UnlitMaterial|PhysicallyBasedMaterial|ShaderGraphMaterial)\s*\.\s*create|"
    r"PhysicsMaterialResource"
    r")\s*\("
)
MESH_FACTORY = re.compile(r"\bMeshResource\s*\.\s*create\w*\s*\(")
TARGET_INCLUSIVE_REGION = re.compile(
    r"\b(?:union|merge|include|expandToInclude)\s*\("
    r"[^;{}]*(?:target|body|occupant)\w*Bounds\b[^;{}]*\)",
    re.IGNORECASE | re.DOTALL,
)
CENTER_CONTAINMENT = re.compile(
    r"(?:"
    r"(?:target|body|occupant)\w*Bounds\s*\.\s*center\s*\.\s*[xyz]\s*"
    r"(?:<=|>=|<|>)\s*\w*(?:region|cavity|bay|slot)\w*\s*\.\s*(?:min|max)\s*\.\s*[xyz]"
    r"|"
    r"\w*(?:region|cavity|bay|slot)\w*\s*\.\s*(?:min|max)\s*\.\s*[xyz]\s*"
    r"(?:<=|>=|<|>)\s*(?:target|body|occupant)\w*Bounds\s*\.\s*center\s*\.\s*[xyz]"
    r"|"
    r"\w*(?:region|cavity|bay|slot)\w*\s*\.\s*contains\s*\(\s*"
    r"(?:target|body|occupant)\w*Bounds\s*\.\s*center"
    r")",
    re.IGNORECASE | re.DOTALL,
)
PLANNED_BOUNDS_SIGNAL = re.compile(
    r"\b(?:finalPlannedBounds|plannedFinalBounds|transformedPlannedBounds|plannedBounds)\b"
)
FIT_SCALE_ASSIGNMENT = re.compile(
    r"\b(?:fittedSceneRoot|fittedRoot)\b[^\n;]*\bscale\s*=",
    re.IGNORECASE,
)
CONTAINMENT_SIGNAL = re.compile(
    r"\b(?:allowedDeltaMin|allowedDeltaMax|contain\w*|inside\w*|cavity|safeRegion)\b",
    re.IGNORECASE,
)
EPSILON_SIGNAL = re.compile(r"\b(?:epsilon|eps|tolerance)\b", re.IGNORECASE)
REVISION_SIGNAL = re.compile(
    r"\b(?:revision|sizeKey|placedForSizes|appliedRevision)\b", re.IGNORECASE
)
OWNER_SIGNAL = re.compile(
    r"\b(?:placementOwner|boundsOwner|relativeTo\s*=\s*(?!null\b)\w+)\b",
    re.IGNORECASE,
)
SURFACE_DETAIL_SIGNAL = re.compile(
    r"\b\w*(?:eye|nose|label|decal|indicator|faceDetail)\w*\b", re.IGNORECASE
)
DEPTH_ASSIGNMENT = re.compile(r"\b(?:position\s*=\s*)?Vector3\s*\(", re.IGNORECASE)
BODY_DETAIL_CONTRACT = re.compile(
    r"\b(?:bodyBounds|bodyDepth|surfaceDetail|detailDepth|detailOffset)\b",
    re.IGNORECASE,
)


def code_only(source: str) -> str:
    """Mask Kotlin comments and string/char literals while preserving line numbers."""

    chars = list(source)
    index = 0
    state = "code"
    block_depth = 0
    while index < len(chars):
        current = chars[index]
        following = source[index : index + 3]

        if state == "code":
            if source.startswith("//", index):
                chars[index : index + 2] = [" ", " "]
                index += 2
                state = "line-comment"
                continue
            if source.startswith("/*", index):
                chars[index : index + 2] = [" ", " "]
                index += 2
                block_depth = 1
                state = "block-comment"
                continue
            if following == '"""':
                chars[index : index + 3] = [" ", " ", " "]
                index += 3
                state = "triple-string"
                continue
            if current == '"':
                chars[index] = " "
                index += 1
                state = "string"
                continue
            if current == "'":
                chars[index] = " "
                index += 1
                state = "char"
                continue
            index += 1
            continue

        if state == "line-comment":
            if current == "\n":
                state = "code"
            else:
                chars[index] = " "
            index += 1
            continue

        if state == "block-comment":
            if source.startswith("/*", index):
                chars[index : index + 2] = [" ", " "]
                block_depth += 1
                index += 2
                continue
            if source.startswith("*/", index):
                chars[index : index + 2] = [" ", " "]
                block_depth -= 1
                index += 2
                if block_depth == 0:
                    state = "code"
                continue
            if current != "\n":
                chars[index] = " "
            index += 1
            continue

        if state == "triple-string":
            if following == '"""':
                chars[index : index + 3] = [" ", " ", " "]
                index += 3
                state = "code"
                continue
            if current != "\n":
                chars[index] = " "
            index += 1
            continue

        if current == "\\" and index + 1 < len(chars):
            chars[index] = " "
            chars[index + 1] = " "
            index += 2
            continue
        if (state == "string" and current == '"') or (
            state == "char" and current == "'"
        ):
            chars[index] = " "
            index += 1
            state = "code"
            continue
        if current != "\n":
            chars[index] = " "
        index += 1

    return "".join(chars)


def collect_kotlin_files(scan_inputs: list[Path]) -> tuple[list[Path], list[Violation]]:
    files: set[Path] = set()
    violations: list[Violation] = []

    for scan_input in scan_inputs:
        if not scan_input.exists():
            violations.append(
                Violation(
                    rule="missing-source-path",
                    file=str(scan_input),
                    line=0,
                    evidence="The requested source path does not exist.",
                )
            )
            continue
        if scan_input.is_file():
            if scan_input.suffix != ".kt":
                violations.append(
                    Violation(
                        rule="non-kotlin-source-path",
                        file=str(scan_input),
                        line=0,
                        evidence="Explicit --source files must use the .kt suffix.",
                    )
                )
                continue
            files.add(scan_input)
            continue
        files.update(path for path in scan_input.rglob("*.kt") if path.is_file())

    return sorted(files), violations


def line_for(masked: str, position: int) -> int:
    return masked.count("\n", 0, position) + 1


def source_line(source: str, line: int) -> str:
    lines = source.splitlines()
    if line <= 0 or line > len(lines):
        return ""
    return lines[line - 1].strip()


def latest_match_start(pattern: re.Pattern[str], text: str, end: int) -> int:
    latest = -1
    for match in pattern.finditer(text, 0, end):
        latest = match.start()
    return latest


def inside_spatial_update(masked: str, position: int) -> bool:
    update_start = latest_match_start(
        re.compile(r"\bupdate\s*=\s*(?:\w+@)?\s*\{"), masked, position
    )
    if update_start < 0 or position - update_start > 8000:
        return False
    later_boundary = max(
        latest_match_start(re.compile(r"\binitial\s*=\s*\{"), masked, position),
        latest_match_start(re.compile(r"\bonDispose\s*\{"), masked, position),
        latest_match_start(re.compile(r"\bfun\s+\w+\s*\("), masked, position),
    )
    return update_start > later_boundary


def collect_advisories(path: Path, source: str, masked: str) -> list[Advisory]:
    advisories: list[Advisory] = []

    def add(rule: str, match: re.Match[str], rationale: str) -> None:
        line = line_for(masked, match.start())
        advisories.append(
            Advisory(
                rule=rule,
                file=str(path),
                line=line,
                evidence=source_line(source, line),
                rationale=rationale,
            )
        )

    for match in NULL_BOUNDS_OWNER.finditer(masked):
        add(
            "unnamed-bounds-owner",
            match,
            "A hard runtime result is easier to compare when getVisualBounds uses "
            "one named evidence owner instead of relativeTo = null.",
        )

    mesh_calls: dict[str, list[re.Match[str]]] = {}
    for match in MESH_FACTORY.finditer(masked):
        line_end = masked.find("\n", match.start())
        if line_end < 0:
            line_end = len(masked)
        call_key = re.sub(r"\s+", "", masked[match.start() : line_end])
        mesh_calls.setdefault(call_key, []).append(match)
    for matches in mesh_calls.values():
        if len(matches) > 1:
            add(
                "repeated-identical-mesh-factory",
                matches[1],
                f"The same mesh factory expression appears {len(matches)} times; "
                "consider one scene-lifetime mesh per geometry specification.",
            )

    for match in RESOURCE_FACTORY.finditer(masked):
        if inside_spatial_update(masked, match.start()):
            add(
                "resource-factory-in-spatial-update",
                match,
                "Resource construction in SpatialView.update can repeat on resize or "
                "recomposition; prefer a scene-lifetime construction path.",
            )

    fit_match = FIT_SCALE_ASSIGNMENT.search(masked)
    if fit_match and not PLANNED_BOUNDS_SIGNAL.search(masked):
        add(
            "fit-without-planned-final-bounds",
            fit_match,
            "A fit transform is present without a visible transformed planned-bounds "
            "record; compare planned and visual envelopes in the same owner space.",
        )

    containment_match = CONTAINMENT_SIGNAL.search(masked)
    if containment_match:
        missing = [
            name
            for name, pattern in (
                ("named owner", OWNER_SIGNAL),
                ("epsilon", EPSILON_SIGNAL),
                ("revision or size key", REVISION_SIGNAL),
            )
            if not pattern.search(masked)
        ]
        if missing:
            add(
                "containment-evidence-incomplete",
                containment_match,
                "The focused source contains containment logic but no visible "
                + ", ".join(missing)
                + "; review whether another selected file supplies that evidence.",
            )

    for match in CENTER_CONTAINMENT.finditer(masked):
        add(
            "center-only-containment",
            match,
            "A target center can be inside while its final volume protrudes; verify the "
            "required min/max faces from final body visual bounds.",
        )

    for match in TARGET_INCLUSIVE_REGION.finditer(masked):
        add(
            "target-inclusive-region",
            match,
            "A region that already includes the target cannot independently prove "
            "containment.",
        )

    detail_match = SURFACE_DETAIL_SIGNAL.search(masked)
    if (
        detail_match
        and DEPTH_ASSIGNMENT.search(masked)
        and not BODY_DETAIL_CONTRACT.search(masked)
    ):
        add(
            "surface-detail-depth-without-body-contract",
            detail_match,
            "Foreground-facing details appear in a scene with depth transforms but no "
            "visible body/detail depth contract; review whether Z is being used only "
            "for front-view visibility.",
        )

    return advisories


def evaluate(scan_inputs: list[Path]) -> dict[str, object]:
    files, violations = collect_kotlin_files(scan_inputs)
    advisories: list[Advisory] = []
    signals = {
        "getVisualBounds": 0,
        "BoundingBox": 0,
        "convertPosition": 0,
        "meshResourceFactory": 0,
        "materialResourceFactory": 0,
    }

    for path in files:
        source = path.read_text(encoding="utf-8", errors="replace")
        masked = code_only(source)
        for signal in ("getVisualBounds", "BoundingBox", "convertPosition"):
            signals[signal] += len(re.findall(rf"\b{signal}\b", masked))
        signals["meshResourceFactory"] += len(MESH_FACTORY.findall(masked))
        signals["materialResourceFactory"] += len(RESOURCE_FACTORY.findall(masked)) - len(
            MESH_FACTORY.findall(masked)
        )
        advisories.extend(collect_advisories(path, source, masked))
        for rule, pattern in RULES:
            for match in pattern.finditer(masked):
                line = masked.count("\n", 0, match.start()) + 1
                evidence = source.splitlines()[line - 1].strip()
                violations.append(
                    Violation(
                        rule=rule,
                        file=str(path),
                        line=line,
                        evidence=evidence,
                    )
                )

    if not files and not violations:
        violations.append(
            Violation(
                rule="missing-kotlin-source",
                file=", ".join(str(path) for path in scan_inputs),
                line=0,
                evidence="No Kotlin files found.",
            )
        )

    return {
        "schema_version": 3,
        "passed": not violations,
        "scan_inputs": [str(path) for path in scan_inputs],
        "kotlin_file_count": len(files),
        "signals": signals,
        "violations": [asdict(item) for item in violations],
        "advisories": [asdict(item) for item in advisories],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument(
        "--source",
        action="append",
        type=Path,
        help="Kotlin file or focused source directory to scan; repeat for multiple paths.",
    )
    scope.add_argument(
        "--source-root",
        type=Path,
        help="One placement-specific source root to scan recursively.",
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    scan_inputs = args.source or [args.source_root]
    result = evaluate(scan_inputs)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
