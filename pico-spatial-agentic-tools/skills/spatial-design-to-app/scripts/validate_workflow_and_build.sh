#!/usr/bin/env bash
# Validate the generated project, run the smoke build, enforce architecture
# conventions, unit tests, and design-style admission.
#
# There is no intermediate layout-contract JSON: the container is inferred from
# AndroidManifest meta-data and every structural rule is checked against the
# generated Kotlin. Only two handoff receipts are validated, because both record
# a decision made outside this skill (see check_handoff_receipts.py).
#
# Usage:
#   bash scripts/validate_workflow_and_build.sh <target> \
#       --input-mode <mode> --generation-mode <mode> [--visual-asset true|false] \
#       [--design-color <slot>=<#hex>]... | [--no-design-colors] \
#       [--profile patch] [--skip-*] [--allow-degraded]
#
# Step order:
#   1. handoff receipts (designer gate + scaffold-only onboarding handoff)
#   2. implementation scanner (root, entry, manifest, Stage legality, components)
#   3. Gradle sync/project discovery (CLI proxy for Android Studio sync)
#   4. smoke build (assembleDebug)
#   5. runtime launch check (installDebug + launch Activity + crash scan)
#   6. architecture conventions (check_architecture.py)
#   7. JVM unit tests (testDebugUnitTest)
#   8. spatial-ui-design-style verifier
#
# Figma MCP hooks (d2c_verify_code -> targeted fixes -> d2c_cleanup_temp) are
# agent-owned, because a shell wrapper cannot call MCP tools. See SKILL.md.
#
# The --skip-* flags are emergency hatches, except --skip-design-style which is
# intentionally a hard failure for generated Compose UI.
# ----------------------------------------------------------------------------
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <target> [--require-assumptions] [--skip-design-style] [--skip-architecture] [--skip-unit-tests] [--skip-gradle-sync] [--skip-runtime-launch] [--allow-degraded]" >&2
    exit 2
fi

TARGET="$1"
shift || true

REQUIRE_ASSUMPTIONS="false"
INPUT_MODE=""
GENERATION_MODE=""
VISUAL_ASSET="false"
PROFILE="default"
DESIGN_COLOR_ARGS=()
NO_DESIGN_COLORS="false"
SKIP_DESIGN_STYLE="false"
SKIP_ARCHITECTURE="false"
SKIP_UNIT_TESTS="false"
SKIP_GRADLE_SYNC="false"
SKIP_RUNTIME_LAUNCH="false"
ALLOW_DEGRADED="false"
while [ $# -gt 0 ]; do
    case "$1" in
        --require-assumptions)
            REQUIRE_ASSUMPTIONS="true"
            ;;
        --input-mode)
            shift; INPUT_MODE="${1:-}"
            ;;
        --generation-mode)
            shift; GENERATION_MODE="${1:-}"
            ;;
        --visual-asset)
            shift; VISUAL_ASSET="${1:-false}"
            ;;
        --profile)
            shift; PROFILE="${1:-default}"
            ;;
        --design-color)
            shift
            [ -n "${1:-}" ] || { echo "[validate] --design-color needs <slot>=<#hex>" >&2; exit 2; }
            DESIGN_COLOR_ARGS+=(--design-color "$1")
            ;;
        --no-design-colors)
            NO_DESIGN_COLORS="true"
            ;;
        --skip-design-style)
            SKIP_DESIGN_STYLE="true"
            ;;
        --skip-architecture)
            SKIP_ARCHITECTURE="true"
            ;;
        --skip-unit-tests)
            SKIP_UNIT_TESTS="true"
            ;;
        --skip-gradle-sync)
            SKIP_GRADLE_SYNC="true"
            ;;
        --skip-runtime-launch)
            SKIP_RUNTIME_LAUNCH="true"
            ;;
        --allow-degraded)
            ALLOW_DEGRADED="true"
            ;;
        *)
            echo "[validate] Unknown option: $1" >&2
            echo "Usage: $0 <target> [--require-assumptions] [--skip-design-style] [--skip-architecture] [--skip-unit-tests] [--skip-gradle-sync] [--skip-runtime-launch] [--allow-degraded]" >&2
            exit 2
            ;;
    esac
    shift
done

if [ ! -d "$TARGET" ]; then
    echo "[validate] Target directory not found: $TARGET" >&2
    exit 2
fi

SCRATCH_DIR="$TARGET/.scratch"
mkdir -p "$SCRATCH_DIR"
VERIFICATION_SUMMARY="$SCRATCH_DIR/verification_summary.json"
DESIGN_STYLE_RESULT="$SCRATCH_DIR/design_style_result.json"
WARNINGS=()
SKIPS=()

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RECEIPT_CHECKER="$SCRIPT_DIR/check_handoff_receipts.py"
IMPL_SCANNER="$SCRIPT_DIR/scan_implementation.py"
SMOKE_BUILD="$SCRIPT_DIR/smoke_build.sh"
GRADLE_SYNC="$SCRIPT_DIR/gradle_sync_check.sh"
ARCH_CHECKER="$SCRIPT_DIR/check_architecture.py"
UNIT_TESTS="$SCRIPT_DIR/run_unit_tests.sh"
RUNTIME_LAUNCH="$SCRIPT_DIR/runtime_launch_check.sh"

# Resolve sibling spatial-ui-design-style verifier.
SKILLS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DESIGN_STYLE_VERIFIER="$SKILLS_ROOT/spatial-ui-design-style/scripts/verify-design-style.sh"

for required in "$RECEIPT_CHECKER" "$IMPL_SCANNER" "$GRADLE_SYNC" "$SMOKE_BUILD" "$RUNTIME_LAUNCH" "$ARCH_CHECKER" "$UNIT_TESTS"; do
    if [ ! -f "$required" ]; then
        echo "[validate] required script not found: $required" >&2
        exit 2
    fi
done

if [ -z "$INPUT_MODE" ] || [ -z "$GENERATION_MODE" ]; then
    echo "[validate] --input-mode and --generation-mode are required" >&2
    exit 2
fi

echo "[validate] [1/8] handoff receipts"
python3 "$RECEIPT_CHECKER" --target "$TARGET" \
    --input-mode "$INPUT_MODE" \
    --generation-mode "$GENERATION_MODE" \
    --visual-asset "$VISUAL_ASSET"

echo "[validate] [2/8] implementation scanner"
python3 "$IMPL_SCANNER" --target "$TARGET" \
    --generation-mode "$GENERATION_MODE" \
    --profile "$PROFILE"

# ---------- Gradle sync / project discovery gate ----------
echo "[validate] [3/8] Gradle sync/project discovery"
if [ "$SKIP_GRADLE_SYNC" = "true" ]; then
    SKIPS+=("gradle_sync")
    WARNINGS+=("--skip-gradle-sync supplied; Gradle project discovery / IDE sync proxy not enforced")
    echo "[validate] WARN --skip-gradle-sync supplied; Gradle project discovery / IDE sync proxy NOT enforced. The skill still requires Android Studio Sync Project with Gradle Files before first IDE run."
else
    bash "$GRADLE_SYNC" "$TARGET"
fi

echo "[validate] [4/8] smoke build"
bash "$SMOKE_BUILD" "$TARGET"

# ---------- runtime install + launch gate ----------
echo "[validate] [5/8] runtime install/launch"
if [ "$SKIP_RUNTIME_LAUNCH" = "true" ]; then
    SKIPS+=("runtime_launch")
    WARNINGS+=("--skip-runtime-launch supplied; install/launch not enforced")
    echo "[validate] WARN --skip-runtime-launch supplied; install/launch NOT enforced. The skill still requires a clean run for sign-off."
else
    bash "$RUNTIME_LAUNCH" "$TARGET"
fi

# ---------- architecture conventions gate ----------
echo "[validate] [6/8] architecture conventions"
if [ "$SKIP_ARCHITECTURE" = "true" ]; then
    SKIPS+=("architecture")
    WARNINGS+=("--skip-architecture supplied; architecture conventions not enforced")
    echo "[validate] WARN --skip-architecture supplied; architecture conventions NOT enforced. The skill still requires a clean run for sign-off."
else
    python3 "$ARCH_CHECKER" --target "$TARGET"
fi

# ---------- unit-test gate ----------
echo "[validate] [7/8] unit tests"
if [ "$SKIP_UNIT_TESTS" = "true" ]; then
    SKIPS+=("unit_tests")
    WARNINGS+=("--skip-unit-tests supplied; ViewModel/UseCase tests not enforced")
    echo "[validate] WARN --skip-unit-tests supplied; ViewModel/UseCase tests NOT enforced. The skill still requires a clean run for sign-off."
else
    bash "$UNIT_TESTS" "$TARGET"
fi

# ---------- design-style admission gate ----------
echo "[validate] [8/8] design-style admission"
if [ "$SKIP_DESIGN_STYLE" = "true" ]; then
    echo "[validate] FAIL design-style admission is mandatory; --skip-design-style is not allowed for screenshot/generated Compose code" >&2
    python3 - "$DESIGN_STYLE_RESULT" <<'PY'
import json
import sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({"passed": False, "skipped": True, "summary": {"errors": 1, "warnings": 0}, "failures": ["--skip-design-style is forbidden"]}, indent=2), encoding="utf-8")
PY
    exit 1
elif [ ! -f "$DESIGN_STYLE_VERIFIER" ]; then
    echo "[validate] FAIL spatial-ui-design-style verifier not found at: $DESIGN_STYLE_VERIFIER" >&2
    python3 - "$DESIGN_STYLE_RESULT" "$DESIGN_STYLE_VERIFIER" <<'PY'
import json
import sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({"passed": False, "skipped": False, "summary": {"errors": 1, "warnings": 0}, "failures": [f"spatial-ui-design-style verifier not found: {sys.argv[2]}"]}, indent=2), encoding="utf-8")
PY
    exit 1
else
    DESIGN_STYLE_PATH=""
    for candidate in \
        "$TARGET/src/main/java" \
        "$TARGET/src/main/kotlin" \
        "$TARGET"; do
        if [ -d "$candidate" ]; then
            DESIGN_STYLE_PATH="$candidate"
            break
        fi
    done

    if [ -z "$DESIGN_STYLE_PATH" ]; then
        echo "[validate] FAIL no Compose source root found under $TARGET; design-style admission cannot run" >&2
        python3 - "$DESIGN_STYLE_RESULT" "$TARGET" <<'PY'
import json
import sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({"passed": False, "skipped": False, "summary": {"errors": 1, "warnings": 0}, "failures": [f"no Compose source root found under {sys.argv[2]}"]}, indent=2), encoding="utf-8")
PY
        exit 1
    else
        # R1b needs the authoritative design colors. With no layout contract to
        # read them from, the caller must forward them explicitly, or state that
        # there are none — otherwise the fidelity gate would silently pass.
        DESIGN_COLOR_FLAGS=()
        if [ "${#DESIGN_COLOR_ARGS[@]}" -gt 0 ]; then
            DESIGN_COLOR_FLAGS=("${DESIGN_COLOR_ARGS[@]}")
        elif [ "$NO_DESIGN_COLORS" = "true" ]; then
            DESIGN_COLOR_FLAGS=(--no-design-colors)
        else
            echo "[validate] FAIL design colors were not declared. Pass --design-color <slot>=<#hex> for every color the design deliverable specifies, or --no-design-colors if it specifies none." >&2
            python3 - "$DESIGN_STYLE_RESULT" <<'PY2'
import json
import sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({"passed": False, "skipped": False, "summary": {"errors": 1, "warnings": 0}, "failures": ["design colors not declared: pass --design-color or --no-design-colors"]}, indent=2), encoding="utf-8")
PY2
            exit 1
        fi

        echo "[validate] running spatial-ui-design-style verifier on: $DESIGN_STYLE_PATH"
        DESIGN_STYLE_LOG="$SCRATCH_DIR/design_style.log"
        if bash "$DESIGN_STYLE_VERIFIER" "$DESIGN_STYLE_PATH" "${DESIGN_COLOR_FLAGS[@]}" >"$DESIGN_STYLE_LOG" 2>&1; then
            cat "$DESIGN_STYLE_LOG"
            python3 - "$DESIGN_STYLE_RESULT" "$DESIGN_STYLE_LOG" "$DESIGN_STYLE_PATH" <<'PY'
import json
import re
import sys
from pathlib import Path
result_path = Path(sys.argv[1])
log_path = Path(sys.argv[2])
source_path = sys.argv[3]
log = log_path.read_text(encoding="utf-8", errors="replace")
errors = int(re.search(r"errors:\s+(\d+)", log).group(1)) if re.search(r"errors:\s+(\d+)", log) else 0
warnings = int(re.search(r"warnings:\s+(\d+)", log).group(1)) if re.search(r"warnings:\s+(\d+)", log) else 0
result_path.write_text(json.dumps({"passed": True, "skipped": False, "source_path": source_path, "log": str(log_path), "summary": {"errors": errors, "warnings": warnings}, "failures": []}, indent=2, ensure_ascii=False), encoding="utf-8")
PY
        else
            status=$?
            cat "$DESIGN_STYLE_LOG"
            python3 - "$DESIGN_STYLE_RESULT" "$DESIGN_STYLE_LOG" "$DESIGN_STYLE_PATH" "$status" <<'PY'
import json
import re
import sys
from pathlib import Path
result_path = Path(sys.argv[1])
log_path = Path(sys.argv[2])
source_path = sys.argv[3]
status = int(sys.argv[4])
log = log_path.read_text(encoding="utf-8", errors="replace")
errors = int(re.search(r"errors:\s+(\d+)", log).group(1)) if re.search(r"errors:\s+(\d+)", log) else 1
warnings = int(re.search(r"warnings:\s+(\d+)", log).group(1)) if re.search(r"warnings:\s+(\d+)", log) else 0
failures = [line for line in log.splitlines() if line.startswith("[error]")]
result_path.write_text(json.dumps({"passed": False, "skipped": False, "source_path": source_path, "log": str(log_path), "exit_code": status, "summary": {"errors": errors, "warnings": warnings}, "failures": failures}, indent=2, ensure_ascii=False), encoding="utf-8")
PY
            exit "$status"
        fi
    fi
fi

if [ "$INPUT_MODE" = "visual_design" ] || [ "$INPUT_MODE" = "hybrid" ]; then
    echo "[validate] Figma MCP hook handoff"
    echo "[validate] A shell wrapper cannot call MCP tools. If this run consumed a Figma URL, now run d2c_verify_code exactly once, apply targeted Critical/Moderate fixes, then run d2c_cleanup_temp exactly once, and write .scratch/figma_hooks_result.json. Cleanup must never run before verify."
fi

CLEAN="true"
if [ "${#WARNINGS[@]}" -gt 0 ] || [ "${#SKIPS[@]}" -gt 0 ]; then
    CLEAN="false"
fi

python3 - "$VERIFICATION_SUMMARY" "$CLEAN" "$ALLOW_DEGRADED" "${WARNINGS[@]+"${WARNINGS[@]}"}" -- "${SKIPS[@]+"${SKIPS[@]}"}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
clean = sys.argv[2] == "true"
allow_degraded = sys.argv[3] == "true"
rest = sys.argv[4:]
split = rest.index("--") if "--" in rest else len(rest)
warnings = rest[:split]
skips = rest[split + 1:] if split < len(rest) else []
data = {
    "passed": clean,
    "operational": True,
    "clean": clean,
    "allow_degraded": allow_degraded,
    "warnings": warnings,
    "skips": skips,
    "adapter_hooks_agent_owned": True,
    "note": "clean=false means a gate was skipped or degraded; --allow-degraded is operational-only, not skill-complete. Figma runs are still pending until the agent completes the d2c verify/cleanup hooks and records figma_hooks_result.json.",
}
path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
PY

echo "[validate] WROTE $VERIFICATION_SUMMARY"
if [ "$CLEAN" = "true" ]; then
    echo "[validate] MACHINE GATES PASSED clean: handoff receipts + implementation scan + Gradle sync/project discovery + smoke build + runtime launch + architecture + unit tests + design-style passed. Figma runs remain pending until agent-owned d2c hooks write figma_hooks_result.json"
else
    echo "[validate] DEGRADED: machine gates completed with warnings/skips; exit 0 with --allow-degraded is operational-only, not skill-complete. See $VERIFICATION_SUMMARY and disclose warnings/skips in handoff"
    if [ "$ALLOW_DEGRADED" != "true" ]; then
        echo "[validate] FAIL degraded run requires explicit --allow-degraded to exit 0" >&2
        exit 1
    fi
fi
