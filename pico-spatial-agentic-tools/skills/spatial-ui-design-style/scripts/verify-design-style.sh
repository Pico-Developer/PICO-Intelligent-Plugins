#!/usr/bin/env bash
# verify-design-style.sh
# ----------------------------------------------------------------------------
# Lint-as-skill verifier for the spatial-ui-design-style skill.
# Enforces the four highest-priority rules (R1-R4), including design-driven
# color-scheme injection (R1b), token-routing checks
# (R5-R7), and migrated D2C checklist heuristics (R8). See
# ../references/compliance-signals.md for the full spec.
#
# Usage:
#   verify-design-style.sh <module-or-src-path> [<more paths> ...] \
#       [--design-color <slot>=<#hex>]... | [--no-design-colors]
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
while [[ $# -gt 0 ]]; do
  case "$1" in
    --design-color)
      shift
      [[ $# -gt 0 ]] || { echo "$0: --design-color needs <slot>=<#hex>" >&2; exit 2; }
      DESIGN_COLORS+=("$1")
      ;;
    --design-color=*)
      DESIGN_COLORS+=("${1#--design-color=}")
      ;;
    --no-design-colors)
      NO_DESIGN_COLORS="true"
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
  echo "usage: $0 <module-or-src-path> [<more paths> ...] [--design-color <slot>=<#hex>]... | [--no-design-colors]" >&2
  exit 2
fi

if [[ ${#DESIGN_COLORS[@]} -gt 0 && "$NO_DESIGN_COLORS" == "true" ]]; then
  echo "$0: --design-color and --no-design-colors are mutually exclusive" >&2
  exit 2
fi

for entry in ${DESIGN_COLORS+"${DESIGN_COLORS[@]}"}; do
  if [[ ! "$entry" =~ ^[A-Za-z_][A-Za-z0-9_]*=#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$ ]]; then
    echo "$0: invalid --design-color '$entry'; expected <slot>=<#RRGGBB|#AARRGGBB>" >&2
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
MODIFIER_CLICKABLE_CALL='\.clickable[ 	]*[\(\{]'
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

# file_has_code_pattern <pattern> <file>
# Grep-like per-file predicate that ignores Kotlin line/block comments. This
# prevents commented-out imports or chained calls from satisfying mandatory
# design-style requirements.
file_has_code_pattern() {
  local pattern="$1"
  local file="$2"
  python3 - "$pattern" "$file" <<'PY'
import re
import sys

pattern, path = sys.argv[1], sys.argv[2]
try:
    text = open(path, encoding="utf-8").read()
except OSError:
    sys.exit(1)
text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
text = re.sub(r"^\s*//.*$", "", text, flags=re.M)
sys.exit(0 if re.search(pattern, text) else 1)
PY
}

# design_color_scheme_violations <mode> <color-spec...> -- <paths...>
# Emits one tab-separated violation per line when authoritative design colors
# exist but app code does not inject those exact values through a custom
# PicoTheme color scheme.
#
# <mode> is either `colors` (declarations come from --design-color flags) or
# `legacy` (fall back to .scratch/evidence_packet.json).
design_color_scheme_violations() {
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

# entries: [{"hex": "#RRGGBB", "slot": "labelPrimary", "origin": "..."}]
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
required_scheme_roles = [
    "fillPrimary",
    "fillSecondary",
    "fillTertiary",
    "fillLight",
    "labelPrimaryLight",
    "labelPrimary",
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
]

origins = sorted({entry["origin"] for entry in entries})
if not re.search(r"PicoTheme\s*\([^)]*\bcolorScheme\s*=", source, flags=re.S):
    print(
        "missing_custom_theme\t"
        f"R1b design colors were declared ({', '.join(origins)}), but no "
        "PicoTheme(colorScheme = ...) injection was found"
    )

def call_body(open_paren: int) -> str:
    depth = 0
    for index in range(open_paren, len(source)):
        char = source[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return source[open_paren + 1:index]
    return ""

system_vars = re.findall(
    r"\bval\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*systemColorScheme\s*\([^)]*\)",
    source,
)
copy_patterns = [r"systemColorScheme\s*\([^)]*\)\s*\.copy\s*\("]
copy_patterns.extend(rf"\b{re.escape(name)}\s*\.copy\s*\(" for name in system_vars)
copy_bodies = []
for pattern in copy_patterns:
    for match in re.finditer(pattern, source):
        copy_bodies.append(call_body(match.end() - 1))

best_body = max(
    copy_bodies,
    key=lambda body: sum(
        bool(re.search(rf"\b{re.escape(role)}\s*=", body))
        for role in required_scheme_roles
    ),
    default="",
)
missing_roles = [
    role
    for role in required_scheme_roles
    if not re.search(rf"\b{re.escape(role)}\s*=", best_body)
]
if not system_vars and not re.search(r"\bsystemColorScheme\s*\(", source):
    missing_scheme_parts = ["systemColorScheme(...)"]
else:
    missing_scheme_parts = []
if not copy_bodies:
    missing_scheme_parts.append(".copy(...)")
if missing_roles:
    missing_scheme_parts.append("roles: " + ", ".join(missing_roles))
if missing_scheme_parts:
    print(
        "incomplete_system_color_scheme\t"
        "R1b design-driven themes must define all 16 ColorScheme roles "
        "explicitly from systemColorScheme(...); missing "
        + "; ".join(missing_scheme_parts)
    )

for entry in entries:
    raw = entry["hex"][1:].upper()
    literals = [f"0XFF{raw}"] if len(raw) == 6 else [f"0X{raw}", f"0X{raw[-2:]}{raw[:-2]}"]
    slot = entry["slot"]
    literal_pattern = "(?:" + "|".join(re.escape(value) for value in literals) + ")"
    if slot in standard_slots:
        direct_mapping = re.search(
            rf"\b{re.escape(slot.upper())}\s*=\s*COLOR\s*\(\s*{literal_pattern}",
            source_upper,
        )
        token_mapping = False
        assignment = re.search(
            rf"\b{re.escape(slot)}\s*=\s*([A-Za-z_][A-Za-z0-9_.]*)",
            source,
        )
        if assignment:
            token_name = assignment.group(1).split(".")[-1]
            token_mapping = bool(
                re.search(
                    rf"\b(?:const\s+)?val\s+{re.escape(token_name)}\s*=\s*"
                    rf"COLOR\s*\(\s*{literal_pattern}",
                    source_upper,
                    flags=re.I,
                )
            )
        if not direct_mapping and not token_mapping:
            print(
                "missing_role_value_mapping\t"
                f"R1b design color {entry['hex']} must be mapped exactly to "
                f"ColorScheme.{slot}"
            )
    elif not any(literal in source_upper for literal in literals):
        print(
            "missing_design_color\t"
            f"R1b design color {entry['hex']} ({slot}) is absent from app theme/token source"
        )
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

# unresolved_text_color_violations <paths...>
# Emits one violation for each SpatialUI Text call that neither supplies an
# explicit color nor documents deliberate LocalContentColor inheritance.
unresolved_text_color_violations() {
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

def call_end(code: str, open_paren: int):
    depth = 0
    quote = None
    index = open_paren
    while index < len(code):
        if quote == '"""':
            if code.startswith('"""', index):
                quote = None
                index += 3
                continue
        elif quote:
            if code[index] == "\\":
                index += 2
                continue
            if code[index] == quote:
                quote = None
        elif code.startswith('"""', index):
            quote = '"""'
            index += 3
            continue
        elif code[index] in {'"', "'"}:
            quote = code[index]
        elif code[index] == "(":
            depth += 1
        elif code[index] == ")":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None

for path in source_files:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(
        r"import\s+com\.pico\.spatial\.ui\.design\.(?:Text|\*)",
        raw,
    ):
        continue

    code = strip_comments_preserving_lines(raw)
    raw_lines = raw.splitlines()
    for match in re.finditer(r"\bText\s*\(", code):
        prefix = code[max(0, match.start() - 12) : match.start()]
        if re.search(r"\bfun\s+$", prefix):
            continue
        open_paren = code.find("(", match.start())
        end = call_end(code, open_paren)
        if end is None:
            continue
        body = code[open_paren + 1 : end]
        if re.search(r"\bcolor\s*=", body):
            continue

        start_line = code.count("\n", 0, match.start())
        end_line = code.count("\n", 0, end)
        annotation_start = max(0, start_line - 1)
        annotation = "\n".join(raw_lines[annotation_start : end_line + 1])
        marker = re.search(
            r"design-style:\s*inherited-content-color\s+([A-Za-z_][A-Za-z0-9_.]*)",
            annotation,
        )
        if marker:
            continue

        print(
            "unresolved_text_color\t"
            f"R9 {path}:{start_line + 1} Text has no explicit color and no "
            "'design-style: inherited-content-color <provider>' marker; "
            "PicoTheme does not provide LocalContentColor, so this can render "
            "black on dark glass"
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
scan    'MaterialTheme\(' error 'R1 MaterialTheme leaked into app code; use PicoTheme' "${PATHS[@]}"
scan    'MaterialTheme\.(colorScheme|typography)' error 'R1 use PicoTheme.colorScheme / PicoTheme.typography' "${PATHS[@]}"

echo "-- R1b design colors drive PicoTheme"
# Resolution order: --design-color flags, else the legacy evidence packet.
# Neither present and no explicit --no-design-colors => invocation error, so a
# caller that simply forgot to forward its design colors cannot turn R1b into a
# silent no-op.
if [[ ${#DESIGN_COLORS[@]} -gt 0 ]]; then
  design_color_errors=$(design_color_scheme_violations colors "${DESIGN_COLORS[@]}" -- "${PATHS[@]}")
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
    design_color_errors=$(design_color_scheme_violations legacy -- "${PATHS[@]}")
  else
    echo "[error] R1b design colors were neither passed via --design-color nor found in .scratch/evidence_packet.json; pass --no-design-colors to assert there are none" >&2
    ERRORS=$((ERRORS+1))
    design_color_errors=""
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
echo "-- R6 indication & haptics"
# Per-file check: a file that uses .clickable(...) or .clickable { ... } MUST also reference
# LocalIndication.current and controllerHapticFeedback somewhere in the same
# file. (The previous tree-wide `require` was too lenient and never failed in
# practice.)
clickable_files=$("$GREP_BIN" "${GREP_FLAGS[@]}" "${EXCLUDES[@]}" -l "$MODIFIER_CLICKABLE_CALL" "${PATHS[@]}" 2>/dev/null || true)
if [[ -n "$clickable_files" ]]; then
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    if ! file_has_code_pattern "$MODIFIER_CLICKABLE_CALL" "$f"; then
      continue
    fi
    if ! file_has_code_pattern 'LocalIndication\.current' "$f"; then
      printf '[warning] R6 clickable() without LocalIndication.current :: %s\n' "$f"
      WARNINGS=$((WARNINGS+1))
    fi
    if ! file_has_code_pattern 'controllerHapticFeedback' "$f"; then
      printf '[error] R6 clickable() without shared controllerHapticFeedback :: %s\n' "$f"
      ERRORS=$((ERRORS+1))
    fi
  done <<<"$clickable_files"
fi

# ---------- R7 — library-private tokens ----------
echo "-- R7 library-private token imports"
scan 'import com\.pico\.spatial\.ui\.design\.tokens\.(DimensionTokens|ColorTokens)' error 'R7 do not import @RestrictTo(LIBRARY) tokens' "${PATHS[@]}"

# ---------- R8 — migrated SpatialUI checklist heuristics ----------
echo "-- R8 migrated SpatialUI checklist heuristics"
scan 'import[ 	]+androidx\.compose\.material3(\.|$)' error 'R8 Material3 package import; prefer com.pico.spatial.ui.design.* built-ins' "${PATHS[@]}"
scan 'import[ 	]+androidx\.compose\.material(\.|$)' error 'R8 Material package import; Material (v1) component import; prefer com.pico.spatial.ui.design.* built-ins' "${PATHS[@]}"
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

# ---------- R9 — every Text foreground must resolve ----------
echo "-- R9 resolved text foregrounds"
text_color_errors=$(unresolved_text_color_violations "${PATHS[@]}")
if [[ -n "$text_color_errors" ]]; then
  while IFS=$'\t' read -r _ message; do
    [[ -z "$message" ]] && continue
    printf '[error] %s\n' "$message"
    ERRORS=$((ERRORS+1))
  done <<<"$text_color_errors"
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
