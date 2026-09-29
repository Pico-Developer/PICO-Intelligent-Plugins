#!/usr/bin/env bash
# verify-design-style.sh
# ----------------------------------------------------------------------------
# Lint-as-skill verifier for the spatial-ui-design-style skill.
# Enforces the highest-priority rules, including design-driven color-scheme
# preservation (R1b), custom-token routing, and app-authored content-surface
# discipline (R10). See
# ../references/compliance-signals.md for the full spec.
#
# Usage:
#   verify-design-style.sh <module-or-src-path> [<more paths> ...] \
#       [--design-color <token>=<#hex>]... | [--no-design-colors] \
#       [--design-spec <path-to-design-spec.json>]
#
# Exit codes:
#   0  no errors (warnings may exist)
#   1  one or more errors
#   2  invalid invocation
#
# Notes:
#   - Scope: *.kt files under src/main/{java,kotlin}/**.
#   - Generated output (build/, generated/, *.kts, res/) is automatically
#     skipped.
#   - R1b design colors resolve in this order: `--design-color` flags, then a
#     legacy `.scratch/evidence_packet.json` next to the scanned paths. Callers
#     that genuinely have no authoritative design colors must say so with
#     `--no-design-colors`. Passing neither is an invocation error, because a
#     silent "no colors found" would turn R1b into a no-op exactly when a design
#     source exists but was not wired through.
# ----------------------------------------------------------------------------
set -euo pipefail

PATHS=()
DESIGN_COLORS=()
NO_DESIGN_COLORS="false"
DESIGN_SPEC=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --design-color)
      shift
      [[ $# -gt 0 && "$1" != --* ]] || { echo "$0: --design-color needs <token>=<#hex>" >&2; exit 2; }
      DESIGN_COLORS+=("$1")
      ;;
    --design-color=*)
      DESIGN_COLORS+=("${1#--design-color=}")
      ;;
    --no-design-colors)
      NO_DESIGN_COLORS="true"
      ;;
    --design-spec)
      shift
      [[ $# -gt 0 && "$1" != --* ]] || { echo "$0: --design-spec needs a path" >&2; exit 2; }
      DESIGN_SPEC="$1"
      ;;
    --design-spec=*)
      DESIGN_SPEC="${1#--design-spec=}"
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do PATHS+=("$1"); shift; done
      break
      ;;
    -*)
      echo "$0: unknown option: $1" >&2
      exit 2
      ;;
    *)
      PATHS+=("$1")
      ;;
  esac
  shift
done

if [[ ${#PATHS[@]} -lt 1 ]]; then
  echo "usage: $0 <module-or-src-path> [<more paths> ...] [--design-color <token>=<#hex>]... | [--no-design-colors] [--design-spec <path>]" >&2
  exit 2
fi

if [[ ${#DESIGN_COLORS[@]} -gt 0 && "$NO_DESIGN_COLORS" == "true" ]]; then
  echo "$0: --design-color and --no-design-colors are mutually exclusive" >&2
  exit 2
fi

for entry in ${DESIGN_COLORS+"${DESIGN_COLORS[@]}"}; do
  if [[ "$entry" != *=* ]]; then
    echo "$0: invalid --design-color '$entry'; missing '=' separator; expected <token>=<#RRGGBB|#AARRGGBB>" >&2
    exit 2
  fi
  token="${entry%%=*}"
  color="${entry#*=}"
  if [[ ! "$token" =~ ^[a-z][A-Za-z0-9]*$ ]]; then
    echo "$0: invalid --design-color token name '$token'; expected lowerCamelCase, for example 'liftShadow'" >&2
    exit 2
  fi
  if [[ ! "$color" =~ ^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$ ]]; then
    echo "$0: invalid --design-color color value '$color' for token '$token'; expected #RRGGBB or #AARRGGBB (6 or 8 hex digits)" >&2
    exit 2
  fi
done

# ---------- helpers ----------
ERRORS=0
WARNINGS=0

# Pick a grep flavor that supports -P (PCRE). Fall back to extended regex.
GREP_BIN="grep"
if echo "" | grep -P "" >/dev/null 2>&1; then
  GREP_FLAGS=("-P" "-n" "-r" "--include=*.kt")
else
  GREP_BIN="grep"
  GREP_FLAGS=("-E" "-n" "-r" "--include=*.kt")
fi

EXCLUDES=(
  "--exclude-dir=build"
  "--exclude-dir=generated"
  "--exclude-dir=.gradle"
  "--exclude-dir=.idea"
  "--exclude-dir=test"
  "--exclude-dir=androidTest"
  "--exclude-dir=res"
)

MODIFIER_HOVERABLE_CALL='\.hoverable[ 	]*\('
MODIFIER_BACKGROUND_COLOR_CALL='\.background[ 	]*\([ 	]*Color\(0x'
MODIFIER_ALPHA_DISABLED_CALL='\.alpha[ 	]*\([ 	]*0\.3f[ 	]*\)'

# scan <pattern> <severity:error|warning|info> <message> [paths...]
scan() {
  local pattern="$1"; shift
  local severity="$1"; shift
  local message="$1"; shift
  local matches
  matches=$("$GREP_BIN" "${GREP_FLAGS[@]}" "${EXCLUDES[@]}" "$pattern" "$@" 2>/dev/null || true)
  if [[ -n "$matches" ]]; then
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      printf '[%s] %s :: %s\n' "$severity" "$message" "$line"
      case "$severity" in
        error) ERRORS=$((ERRORS+1));;
        warning) WARNINGS=$((WARNINGS+1));;
      esac
    done <<<"$matches"
  fi
}

# scan_multiline_error <pattern> <message> <paths...>
# Kotlin-aware scan like scan(), but allows whitespace across line breaks and
# masks comments and literals before matching. Keep one diagnostic per matching
# source line, including its original location.
scan_multiline_error() {
  local pattern="$1"; shift
  local message="$1"; shift
  local matches
  matches=$(python3 - "$pattern" "$@" <<'PY'
import os
import re
import sys
from pathlib import Path

pattern = re.compile(sys.argv[1], re.M)
excluded = {"build", "generated", ".gradle", ".idea", "test", "androidTest", "res"}
seen = set()


def mask_kotlin_non_code(source):
    masked = list(source)
    length = len(source)
    index = 0

    def blank(start, end):
        for position in range(start, end):
            if source[position] not in "\r\n":
                masked[position] = " "

    while index < length:
        if source.startswith("//", index):
            end = source.find("\n", index + 2)
            end = length if end == -1 else end
            blank(index, end)
            index = end
        elif source.startswith("/*", index):
            start = index
            depth = 1
            index += 2
            while index < length and depth:
                if source.startswith("/*", index):
                    depth += 1
                    index += 2
                elif source.startswith("*/", index):
                    depth -= 1
                    index += 2
                else:
                    index += 1
            blank(start, index)
        elif source.startswith('"""', index):
            start = index
            end = source.find('"""', index + 3)
            index = length if end == -1 else end + 3
            blank(start, index)
        elif source[index] in {'"', "'"}:
            start = index
            quote = source[index]
            index += 1
            while index < length:
                if source[index] == "\\":
                    index = min(index + 2, length)
                elif source[index] == quote:
                    index += 1
                    break
                else:
                    index += 1
            blank(start, index)
        else:
            index += 1
    return "".join(masked)


for raw_path in sys.argv[2:]:
    root = Path(raw_path)
    is_file = root.is_file()
    candidates = [root] if is_file else sorted(root.rglob("*.kt"))
    for path in candidates:
        # Match grep's root spelling (including a trailing slash); ancestors
        # outside the requested tree must not affect scan scope.
        directories = () if is_file else (
            os.path.basename(raw_path), *path.relative_to(root).parts[:-1]
        )
        if path.suffix != ".kt" or excluded.intersection(directories) or path in seen:
            continue
        seen.add(path)
        source = path.read_text(encoding="utf-8", errors="replace")
        searchable = mask_kotlin_non_code(source)
        lines = source.splitlines()
        reported = set()
        for match in pattern.finditer(searchable):
            line = searchable.count("\n", 0, match.start()) + 1
            if line not in reported:
                print(f"{path}:{line}:{lines[line - 1]}")
                reported.add(line)
PY
  )
  if [[ -n "$matches" ]]; then
    while IFS= read -r line; do
      printf '[error] %s :: %s\n' "$message" "$line"
      ERRORS=$((ERRORS+1))
    done <<<"$matches"
  fi
}

# scan_without_fixed_figma_color <pattern> <severity> <message> [paths...]
# Same as scan(), but allows explicitly annotated non-root decorative colors
# extracted from Figma / screenshots. The annotation must be on the same line:
#   // design-style: fixed-figma-color <reason or token>
scan_without_fixed_figma_color() {
  local pattern="$1"; shift
  local severity="$1"; shift
  local message="$1"; shift
  local matches
  matches=$("$GREP_BIN" "${GREP_FLAGS[@]}" "${EXCLUDES[@]}" "$pattern" "$@" 2>/dev/null || true)
  if [[ -n "$matches" ]]; then
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      if [[ "$line" == *"design-style: fixed-figma-color"* ]]; then
        continue
      fi
      printf '[%s] %s :: %s\n' "$severity" "$message" "$line"
      case "$severity" in
        error) ERRORS=$((ERRORS+1));;
        warning) WARNINGS=$((WARNINGS+1));;
      esac
    done <<<"$matches"
  fi
}

# require <pattern> <severity> <message> [paths...]
# Reports an error/warning if the pattern is NOT found at least once.
require() {
  local pattern="$1"; shift
  local severity="$1"; shift
  local message="$1"; shift
  if ! "$GREP_BIN" "${GREP_FLAGS[@]}" "${EXCLUDES[@]}" -l "$pattern" "$@" >/dev/null 2>&1; then
    printf '[%s] MISSING %s :: pattern=%s\n' "$severity" "$message" "$pattern"
    case "$severity" in
      error) ERRORS=$((ERRORS+1));;
      warning) WARNINGS=$((WARNINGS+1));;
    esac
  fi
}

# design_color_token_violations <mode> <color-spec...> -- <paths...>
# Emits one tab-separated violation per line when an app-owned design color is
# missing or attempts to replace a native SpatialUI ColorScheme role.
#
# <mode> is either `colors` (declarations come from --design-color flags) or
# `legacy` (fall back to .scratch/evidence_packet.json).
design_color_token_violations() {
  python3 - "$@" <<'PY'
import json
import re
import sys
from pathlib import Path

argv = sys.argv[1:]
mode = argv[0]
separator = argv.index("--")
color_specs = argv[1:separator]
inputs = [Path(raw).resolve() for raw in argv[separator + 1 :]]

# entries: [{"hex": "#RRGGBB", "slot": "brandAccent", "origin": "..."}]
entries = []
if mode == "colors":
    for spec in color_specs:
        slot, _, hex_value = spec.partition("=")
        entries.append({"hex": hex_value, "slot": slot, "origin": "--design-color"})
else:
    evidence_files = []
    for path in inputs:
        bases = [path if path.is_dir() else path.parent]
        bases.append(bases[0].parent)
        for base in bases:
            candidate = base / ".scratch" / "evidence_packet.json"
            if candidate.is_file() and candidate not in evidence_files:
                evidence_files.append(candidate)

    for evidence_path in evidence_files:
        try:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"invalid_evidence\tR1b cannot read design colors from {evidence_path}: {exc}")
            continue
        visual = evidence.get("facts", {}).get("visual_tokens", {})
        declared = visual.get("theme_overrides") or visual.get("semantic_colors") or []
        for entry in declared:
            if (
                isinstance(entry, dict)
                and isinstance(entry.get("hex"), str)
                and re.fullmatch(r"#[0-9A-Fa-f]{6,8}", entry["hex"])
            ):
                entries.append(
                    {
                        "hex": entry["hex"],
                        "slot": entry.get("slot")
                        or entry.get("role")
                        or entry.get("status")
                        or "unnamed",
                        "origin": str(evidence_path),
                    }
                )

if not entries:
    raise SystemExit(0)

source_files = []
for path in inputs:
    candidates = [path] if path.is_file() else path.rglob("*.kt")
    for candidate in candidates:
        parts = set(candidate.parts)
        if candidate.suffix == ".kt" and not parts.intersection(
            {"build", "generated", ".gradle", ".idea", "test", "androidTest"}
        ):
            source_files.append(candidate)

def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


source = "\n".join(
    strip_comments(path.read_text(encoding="utf-8", errors="replace"))
    for path in source_files
)
source_upper = source.upper()
standard_slots = {
    "fillPrimary",
    "fillSecondary",
    "fillTertiary",
    "fillLight",
    "labelPrimary",
    "labelPrimaryLight",
    "labelSecondary",
    "labelTertiary",
    "labelQuaternary",
    "lightenHover",
    "lightenPressed",
    "error",
    "alert",
    "passable",
    "interaction",
    "dividerLine",
}
for entry in entries:
    raw = entry["hex"][1:].upper()
    literals = [f"0XFF{raw}"] if len(raw) == 6 else [f"0X{raw}", f"0X{raw[-2:]}{raw[:-2]}"]
    slot = entry["slot"]
    if slot in standard_slots:
        print(
            "native_color_role_override\t"
            f"R1b {slot} is a native SpatialUI ColorScheme role and cannot be "
            "overridden; give the custom color an app-owned token name"
        )
    elif not any(literal in source_upper for literal in literals):
        print(
            "missing_design_color\t"
            f"R1b custom design color {entry['hex']} ({slot}) is absent from "
            "the app-owned token source"
        )
PY
}

native_color_scheme_override_violations() {
  python3 - "$@" <<'PY'
import re
import sys
from pathlib import Path

inputs = [Path(raw).resolve() for raw in sys.argv[1:]]


def find_balanced_call_arguments(source: str, call_name: str):
    pattern = re.compile(rf"(?<![\w.]){re.escape(call_name)}\s*\(")
    for match in pattern.finditer(source):
        open_index = source.find("(", match.start())
        depth = 1
        index = open_index + 1
        quote = None
        triple_quote = False
        escaped = False
        while index < len(source):
            char = source[index]
            if quote:
                if triple_quote:
                    if source.startswith(quote * 3, index):
                        quote = None
                        triple_quote = False
                        index += 3
                        continue
                elif escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
                index += 1
                continue
            if source.startswith('"""', index):
                quote = '"'
                triple_quote = True
                index += 3
                continue
            if char in {'"', "'"}:
                quote = char
                index += 1
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    yield match.start(), source[open_index + 1 : index]
                    break
            index += 1


for input_path in inputs:
    candidates = [input_path] if input_path.is_file() else input_path.rglob("*.kt")
    for path in candidates:
        if path.suffix != ".kt" or set(path.parts).intersection(
            {"build", "generated", ".gradle", ".idea", "test", "androidTest"}
        ):
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
        source = re.sub(r"^\s*//.*$", "", source, flags=re.M)
        system_vars = re.findall(
            r"\bval\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*systemColorScheme\s*\([^)]*\)",
            source,
        )
        pico_theme_override = next(
            (
                start
                for start, arguments in find_balanced_call_arguments(source, "PicoTheme")
                if re.search(r"\bcolorScheme\s*=", arguments)
            ),
            None,
        )
        if pico_theme_override is not None:
            line = source.count("\n", 0, pico_theme_override) + 1
            print(
                "native_color_scheme_override\t"
                f"R1b {path}:{line} modifies the native SpatialUI ColorScheme; "
                "keep PicoTheme defaults and use app-owned color tokens directly"
            )
            continue
        patterns = [
            r"\bsystemColorScheme\s*\([^)]*\)\s*\.copy\s*\(",
            r"(?<![\w.])ColorScheme\s*\(",
        ]
        patterns.extend(rf"\b{re.escape(name)}\s*\.copy\s*\(" for name in system_vars)
        for pattern in patterns:
            match = re.search(pattern, source)
            if match:
                line = source.count("\n", 0, match.start()) + 1
                print(
                    "native_color_scheme_override\t"
                    f"R1b {path}:{line} modifies the native SpatialUI ColorScheme; "
                    "keep PicoTheme defaults and use app-owned color tokens directly"
                )
                break
PY
}

# material_shape_violations <paths...>
# Emits one tab-separated violation for each view-level backgroundMaterial call
# whose modifier chain does not establish a clip before the material. A
# deliberately rectangular material must carry the explicit exception marker.
material_shape_violations() {
  python3 - "$@" <<'PY'
import re
import sys
from pathlib import Path

inputs = [Path(raw).resolve() for raw in sys.argv[1:]]
source_files = []
for path in inputs:
    candidates = [path] if path.is_file() else path.rglob("*.kt")
    for candidate in candidates:
        parts = set(candidate.parts)
        if candidate.suffix == ".kt" and not parts.intersection(
            {"build", "generated", ".gradle", ".idea", "test", "androidTest"}
        ):
            source_files.append(candidate)

def strip_comments_preserving_lines(text: str) -> str:
    def blank(match: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    return re.sub(r"//[^\n]*", blank, text)

for path in source_files:
    raw = path.read_text(encoding="utf-8", errors="replace")
    code = strip_comments_preserving_lines(raw)
    raw_lines = raw.splitlines()
    code_lines = code.splitlines()

    for index, line in enumerate(code_lines):
        if not re.search(r"\.backgroundMaterial\s*\(", line):
            continue

        start = index
        while start >= 0 and index - start <= 24:
            if re.search(r"\b(?:Modifier|modifier)\b", code_lines[start]):
                break
            if start < index and not code_lines[start].strip():
                start += 1
                break
            start -= 1
        if start < 0 or index - start > 24:
            start = index

        annotation_start = max(0, start - 1)
        annotation_text = "\n".join(raw_lines[annotation_start : index + 1])
        if "design-style: rectangular-material" in annotation_text:
            continue

        chain_before_material = "\n".join(code_lines[start : index + 1])
        material_offset = chain_before_material.find(".backgroundMaterial")
        prefix = chain_before_material[:material_offset]
        if re.search(r"\.clip\s*\(", prefix):
            continue

        print(
            "missing_material_clip\t"
            f"R4b {path}:{index + 1} backgroundMaterial must be preceded by "
            ".clip(shape) in the same modifier chain; use "
            "// design-style: rectangular-material <reason> only for an "
            "explicitly rectangular design"
        )
PY
}

content_border_violations() {
  python3 - "$@" <<'PY'
import re
import sys
from pathlib import Path

inputs = [Path(raw).resolve() for raw in sys.argv[1:]]

def strip_comments_preserving_lines(text: str) -> str:
    def blank(match: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    return re.sub(r"//[^\n]*", blank, text)

for input_path in inputs:
    candidates = [input_path] if input_path.is_file() else input_path.rglob("*.kt")
    for path in candidates:
        if path.suffix != ".kt" or set(path.parts).intersection(
            {"build", "generated", ".gradle", ".idea", "test", "androidTest"}
        ):
            continue
        code = strip_comments_preserving_lines(
            path.read_text(encoding="utf-8", errors="replace")
        )
        for pattern, label in (
            (r"\.border\s*\(", "Modifier.border"),
            (r"\bBorderStroke\s*\(", "BorderStroke"),
        ):
            for match in re.finditer(pattern, code):
                line = code.count("\n", 0, match.start()) + 1
                print(
                    "content_border\t"
                    f"R10 {path}:{line} {label} is an app-authored content border; "
                    "use spacing, alignment, typography, or one surface owner"
                )
PY
}

design_surface_violations() {
  python3 - "$@" <<'PY'
import json
import re
import sys
from pathlib import Path

spec_path = Path(sys.argv[1]).resolve()
inputs = [Path(raw).resolve() for raw in sys.argv[2:]]

try:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"invalid_design_spec\tR10 cannot read design spec {spec_path}: {exc}")
    raise SystemExit(0)

theme = spec.get("theme") if isinstance(spec, dict) else None
if isinstance(theme, dict) and "rootMaterial" in theme:
    print(
        "invalid_design_material\t"
        "R10 design spec declares rootMaterial, which is not part of the design contract"
    )

allowed = set()
for node in spec.get("nodes", []) if isinstance(spec, dict) else []:
    if not isinstance(node, dict) or not isinstance(node.get("id"), str):
        continue
    appearance = node.get("appearance")
    if not isinstance(appearance, dict):
        continue
    if "material" in appearance:
        print(
            "invalid_design_material\t"
            f"R10 design node {node['id']!r} declares material, which is not part "
            "of the appearance contract"
        )
    fill = appearance.get("fill")
    if isinstance(fill, str) and fill.strip():
        if node.get("kind") in {"layout", "domain_visual"}:
            print(
                "structural_design_surface\t"
                f"R10 design node {node['id']!r} ({node.get('kind')}) declares "
                "fill; structural regions must remain transparent"
            )
        else:
            allowed.add(node["id"])

def strip_comments_preserving_lines(text: str) -> str:
    def blank(match: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    return re.sub(r"//[^\n]*", blank, text)

marker_pattern = re.compile(
    r"design-style:\s*design-surface\s+([A-Za-z0-9][A-Za-z0-9._:-]*)"
)
surface_usages = {}

for input_path in inputs:
    candidates = [input_path] if input_path.is_file() else input_path.rglob("*.kt")
    for path in candidates:
        if path.suffix != ".kt" or set(path.parts).intersection(
            {"build", "generated", ".gradle", ".idea", "test", "androidTest"}
        ):
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        code = strip_comments_preserving_lines(raw)
        raw_lines = raw.splitlines()
        for match in re.finditer(r"\.backgroundMaterial\s*\(", code):
            line = code.count("\n", 0, match.start()) + 1
            print(
                "app_authored_material\t"
                f"R10 {path}:{line} backgroundMaterial is not allowed when "
                "restoring a design package"
            )
        has_spatial_card = bool(
            re.search(
                r"import\s+com\.pico\.spatial\.ui\.design\.(?:Card|\*)",
                code,
            )
        )
        patterns = [(r"\.background\s*\(", "background")]
        if has_spatial_card:
            patterns.append((r"\bCard\s*\(", "Card"))

        matches = []
        for pattern, label in patterns:
            for match in re.finditer(pattern, code):
                prefix = code[max(0, match.start() - 12) : match.start()]
                if label == "Card" and re.search(r"\bfun\s+$", prefix):
                    continue
                matches.append((match.start(), label))

        for offset, label in sorted(matches):
            line_index = code.count("\n", 0, offset)
            annotation = "\n".join(raw_lines[max(0, line_index - 3) : line_index + 1])
            marker = marker_pattern.search(annotation)
            if marker is None:
                print(
                    "unmapped_design_surface\t"
                    f"R10 {path}:{line_index + 1} {label} has no nearby "
                    "'design-style: design-surface <node-id>' marker"
                )
                continue
            node_id = marker.group(1)
            if node_id not in allowed:
                print(
                    "unknown_design_surface\t"
                    f"R10 {path}:{line_index + 1} marker names {node_id!r}, "
                    "but that design node declares no fill"
                )
                continue
            surface_usages.setdefault(node_id, []).append(
                f"{path}:{line_index + 1}"
            )

for node_id, locations in sorted(surface_usages.items()):
    if len(locations) > 1:
        print(
            "duplicate_design_surface\t"
            f"R10 design surface {node_id!r} is implemented by {len(locations)} "
            f"background calls ({', '.join(locations)}); each fill node may own "
            "at most one app-authored background implementation"
        )
PY
}

# ---------- inputs ----------
echo "==> spatial-ui-design-style verifier"
echo "    paths: ${PATHS[*]}"
if [[ ${#DESIGN_COLORS[@]} -gt 0 ]]; then
  echo "    design colors: ${DESIGN_COLORS[*]}"
elif [[ "$NO_DESIGN_COLORS" == "true" ]]; then
  echo "    design colors: none declared (--no-design-colors)"
fi
echo

# ---------- R1 — PicoTheme wrapping ----------
echo "-- R1 PicoTheme wrapping"
# Accept both `PicoTheme(` (with explicit args) and `PicoTheme {` (trailing
# lambda) — both are valid call sites for the wrapper.
require 'PicoTheme[ \t]*[\({]' error 'R1 PicoTheme wrapping is required' "${PATHS[@]}"
scan_multiline_error '\bMaterialTheme\s*[({]' 'R1 MaterialTheme leaked into app code; use PicoTheme' "${PATHS[@]}"
scan    'MaterialTheme\.(colorScheme|typography)' error 'R1 use PicoTheme.colorScheme / PicoTheme.typography' "${PATHS[@]}"

echo "-- R1b native ColorScheme preservation and custom colors"
native_color_scheme_errors=$(native_color_scheme_override_violations "${PATHS[@]}")
if [[ -n "$native_color_scheme_errors" ]]; then
  while IFS=$'\t' read -r _ message; do
    [[ -z "$message" ]] && continue
    printf '[error] %s\n' "$message"
    ERRORS=$((ERRORS+1))
  done <<<"$native_color_scheme_errors"
fi

# Resolution order: --design-color flags, else the legacy evidence packet.
# Neither present and no explicit --no-design-colors => invocation error, so a
# caller that simply forgot to forward its design colors cannot turn R1b into a
# silent no-op.
if [[ ${#DESIGN_COLORS[@]} -gt 0 ]]; then
  design_color_errors=$(design_color_token_violations colors "${DESIGN_COLORS[@]}" -- "${PATHS[@]}")
elif [[ "$NO_DESIGN_COLORS" == "true" ]]; then
  design_color_errors=""
  echo "[info] R1b skipped: caller declared no authoritative design colors"
else
  legacy_found="false"
  for candidate_path in "${PATHS[@]}"; do
    base="$candidate_path"
    [[ -f "$base" ]] && base="$(dirname "$base")"
    if [[ -f "$base/.scratch/evidence_packet.json" || -f "$base/../.scratch/evidence_packet.json" ]]; then
      legacy_found="true"
      break
    fi
  done
  if [[ "$legacy_found" == "true" ]]; then
    design_color_errors=$(design_color_token_violations legacy -- "${PATHS[@]}")
  else
    echo "$0: R1b design colors were neither passed via --design-color nor found in .scratch/evidence_packet.json; pass --no-design-colors to assert there are none" >&2
    exit 2
  fi
fi
if [[ -n "$design_color_errors" ]]; then
  while IFS=$'\t' read -r _ message; do
    [[ -z "$message" ]] && continue
    printf '[error] %s\n' "$message"
    ERRORS=$((ERRORS+1))
  done <<<"$design_color_errors"
fi

# ---------- R2 — built-in design components first (soft) ----------
echo "-- R2 built-in design preference (soft check)"
require 'import com\.pico\.spatial\.ui\.design\.' info 'R2 no design import found; ensure built-ins were considered' "${PATHS[@]}"
scan    '@Composable\s+fun\s+My[A-Z]\w*Button' warning 'R2 custom *Button — confirm built-in com.pico.spatial.ui.design.Button does not fit' "${PATHS[@]}"

# ---------- R3 — custom hover MUST use spatialHoverEffect ----------
echo "-- R3 hover effect"
scan "$MODIFIER_HOVERABLE_CALL" error 'R3 custom hover via hoverable() — use Modifier.spatialHoverEffect' "${PATHS[@]}"
# Hand-rolled hover scale: any animateFloatAsState near scale/scaleX/scaleY,
# combined with a hovered-state collector. Two narrower patterns instead of
# one wide regex (the wide regex almost never matched real code).
scan 'collectIsHoveredAsState\(' info 'R3 collectIsHoveredAsState detected — confirm hover is driven by Modifier.spatialHoverEffect, not hand-rolled scale' "${PATHS[@]}"
scan 'animateFloatAsState\(' info 'R3 animateFloatAsState detected near hover scope — confirm it is not hand-rolling hover; prefer Modifier.spatialHoverEffect' "${PATHS[@]}"

# ---------- R4 — window-root background respects system glass ----------
echo "-- R4 window-root background"
# Forbidden: hardcoded color background anywhere
scan_without_fixed_figma_color "$MODIFIER_BACKGROUND_COLOR_CALL" error 'R4 hardcoded color literal as background; use PicoTheme.colorScheme.* and respect the system glass' "${PATHS[@]}"
# Forbidden: stacking glass + solid color on the same chain (best-effort regex)
scan 'backgroundMaterial\([^)]*\)[ \t\r\n.]*background\(' error 'R4 stacking backgroundMaterial + .background — pick exactly one' "${PATHS[@]}"

echo "-- R4b view-level material shape"
material_shape_errors=$(material_shape_violations "${PATHS[@]}")
if [[ -n "$material_shape_errors" ]]; then
  while IFS=$'\t' read -r _ message; do
    [[ -z "$message" ]] && continue
    printf '[error] %s\n' "$message"
    ERRORS=$((ERRORS+1))
  done <<<"$material_shape_errors"
fi

# Window root containers — emit info reminders so the reviewer can confirm
# the right off-switch was flipped. Use ERE-safe alternation (bare `|`) since
# the previous escaped form (`\|`) does not work under POSIX -E.
container_files=$("$GREP_BIN" "${GREP_FLAGS[@]}" "${EXCLUDES[@]}" -l \
    'DefaultWindowContainer|WindowContainer[ \t]*\(|Augment[ \t]*\(|Subwindow[ \t]*\{|Stage[ \t]*\{' \
    "${PATHS[@]}" 2>/dev/null || true)
if [[ -n "$container_files" ]]; then
  override_files=$("$GREP_BIN" "${GREP_FLAGS[@]}" "${EXCLUDES[@]}" -l \
      'backgroundMaterial\([^)]*enable[ \t]*=[ \t]*true|design-style:[ \t]*opaque-root' \
      "${PATHS[@]}" 2>/dev/null || true)
  if [[ -n "$override_files" ]]; then
    echo "[info] R4 custom-glass / opaque-root override detected — confirm the right off-switch is set:"
    echo "       - DefaultWindowContainer  → AndroidManifest \`pico.spatial.windowcontainer.materialbackground=\"0\"\`"
    echo "       - WindowContainer(...) / Augment(...) → DSL parameter \`enableMaterialBackground = false\`"
    echo "       - Stage { ... } has no glass switch; no override is expected on its root"
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      printf '       %s\n' "$f"
    done <<<"$override_files"
  fi
fi
# Soft check: any non-default WindowContainer(...) call should declare
# enableMaterialBackground explicitly when overriding the default behavior.
# Note: deep semantic check — "root Box paints solid color while DSL switch is
# still default true" — is delegated to the reviewer LLM (see judge.md);
# grep cannot reliably localize the root Box across multi-line layouts.
if "$GREP_BIN" "${GREP_FLAGS[@]}" "${EXCLUDES[@]}" -l 'WindowContainer[ \t]*\(' "${PATHS[@]}" >/dev/null 2>&1; then
  scan 'WindowContainer\([^)]*enableMaterialBackground[ \t]*=[ \t]*true[^)]*\)' info 'R4 WindowContainer(... enableMaterialBackground = true ...) — defaults to true; explicit `true` is fine, but make sure no solid background is painted on the root' "${PATHS[@]}"
  scan 'properties[ \t]*=[ \t]*\{[^}]*enableMaterialBackground[ \t]*=[ \t]*false' info 'R4 properties = { enableMaterialBackground = false } — DSL-style off-switch detected; confirm root Box uses backgroundMaterial(...) or `// design-style: opaque-root` + Modifier.background(<role>)' "${PATHS[@]}"
fi

# ---------- R5 — theme-role routing ----------
echo "-- R5 theme-role routing"
scan_without_fixed_figma_color 'Color\(0x[0-9A-Fa-f]{6,8}\)' error 'R5 hardcoded color literal; use PicoTheme.colorScheme.* unless this is an annotated fixed Figma/screenshot color' "${PATHS[@]}"
scan 'TextStyle\(fontSize\s*=' error 'R5 hardcoded typography; use PicoTheme.typography.*' "${PATHS[@]}"
scan "$MODIFIER_ALPHA_DISABLED_CALL" error 'R5 hardcoded disabled alpha 0.3f; use LocalDisableAlpha.current' "${PATHS[@]}"

# ---------- R6 — indication / haptics ----------
echo "-- R6 indication & optional haptics"
# Modifier.clickable uses LocalIndication.current by default. Haptic feedback is
# an optional enhancement, so neither requires a file-level admission check.

# ---------- R7 — library-private tokens ----------
echo "-- R7 library-private token imports"
scan 'import com\.pico\.spatial\.ui\.design\.tokens\.(DimensionTokens|ColorTokens)' error 'R7 do not import @RestrictTo(LIBRARY) tokens' "${PATHS[@]}"

# ---------- R8 — migrated SpatialUI checklist heuristics ----------
echo "-- R8 migrated SpatialUI checklist heuristics"
scan_multiline_error '(?<![\w.])androidx\s*\.\s*compose\s*\.\s*material3\b' 'R8 Material3 package import or fully qualified reference; prefer com.pico.spatial.ui.design.* built-ins' "${PATHS[@]}"
scan_multiline_error '(?<![\w.])androidx\s*\.\s*compose\s*\.\s*material\b' 'R8 Material package import or fully qualified reference; Material (v1) component import; prefer com.pico.spatial.ui.design.* built-ins' "${PATHS[@]}"
scan 'import com\.pico\.spatial\.ui\.design\.AlertDialog' error 'R8 AlertDialog belongs to com.pico.spatial.ui.design.windows.AlertDialog' "${PATHS[@]}"
scan 'collectAsState\([ 	]*\)' warning 'R8 collectAsState() in UI; prefer collectAsStateWithLifecycle() for ViewModel state' "${PATHS[@]}"
scan 'key[ 	]*=[ 	]*\{[ 	]*(index|it\.hashCode\(\))[ 	]*\}' warning 'R8 unstable lazy key; prefer stable item id' "${PATHS[@]}"
scan 'remember[ 	]*\{[ 	]*mutableStateOf\((true|false)\)[ 	]*\}' info 'R8 remember boolean UI state; use rememberSaveable for popup/dialog/menu/subwindow visibility' "${PATHS[@]}"
scan '\.padding\([^)]*horizontal[ 	]*=[^)]*,[^)]*(bottom|top|start|end)[ 	]*=' error 'R8 invalid Modifier.padding overload; use start/end/top/bottom instead of mixing horizontal with side params' "${PATHS[@]}"
scan 'PicoTheme\.colorScheme\.(accent|primary|secondary|background|surface|onSurface|onPrimary)\b' error 'R8 guessed Material-style colorScheme role; use PicoTheme roles or Vibrant' "${PATHS[@]}"
scan '\.background\([^)]*,[ 	]*(RoundedCornerShape|CircleShape|shape)[^)]*\)\.clickable' warning 'R8 background(shape).clickable can mismatch hover/hit shape; prefer clip(shape).spatialHoverEffect().clickable().background()' "${PATHS[@]}"
scan '\.clickable[ 	]*[\(\{][^\r\n]*\.spatialHoverEffect[ 	]*\(' warning 'R8 hover after clickable; prefer clip().spatialHoverEffect().clickable()' "${PATHS[@]}"
scan '\.background\([^)]*\)\.(fillMaxWidth|fillMaxSize|width|height|size)\(' warning 'R8 layout modifier after background; put size/layout before decoration' "${PATHS[@]}"
scan 'modifier\.(fillMaxWidth|fillMaxSize|width|height|size)\(' info 'R8 fixed layout appended to incoming modifier; confirm caller override is not blocked or use Modifier.defaults.then(modifier)' "${PATHS[@]}"
scan 'padding\((start|bottom|end|top)[ 	]*=[ 	]*[0-9]{2,3}\.dp' info 'R8 large directional padding detected; confirm this is not manual TabBar/Toolbar avoidance' "${PATHS[@]}"
scan 'Text\("(✕|×|x|X)"' warning 'R8 handmade close glyph; prefer IconButton + vector icon' "${PATHS[@]}"
scan 'https?://(picsum\.photos|placehold\.co|via\.placeholder\.com|dummyimage\.com)' warning 'R8 hardcoded placeholder URL in UI; bind image URLs from uiState/repository data' "${PATHS[@]}"

# ---------- R10 — content surface discipline ----------
echo "-- R10 content surface discipline"
content_border_errors=$(content_border_violations "${PATHS[@]}")
if [[ -n "$content_border_errors" ]]; then
  while IFS=$'\t' read -r _ message; do
    [[ -z "$message" ]] && continue
    printf '[error] %s\n' "$message"
    ERRORS=$((ERRORS+1))
  done <<<"$content_border_errors"
fi

if [[ -n "$DESIGN_SPEC" ]]; then
  design_surface_errors=$(design_surface_violations "$DESIGN_SPEC" "${PATHS[@]}")
  if [[ -n "$design_surface_errors" ]]; then
    while IFS=$'\t' read -r _ message; do
      [[ -z "$message" ]] && continue
      printf '[error] %s\n' "$message"
      ERRORS=$((ERRORS+1))
    done <<<"$design_surface_errors"
  fi
else
  echo "[info] R10 design-surface trace skipped: no --design-spec supplied"
fi

# ---------- summary ----------
echo
echo "==> spatial-ui-design-style verifier summary"
printf '    errors:   %d\n' "$ERRORS"
printf '    warnings: %d\n' "$WARNINGS"

if [[ $ERRORS -gt 0 ]]; then
  echo "    result:   FAIL"
  exit 1
fi
echo "    result:   PASS"
exit 0
