#!/usr/bin/env bash
# Validate the generated project, run the smoke build, enforce architecture
# conventions, unit tests, and design-style admission.
#
# There is no intermediate layout-contract JSON: the container is inferred from
# AndroidManifest meta-data and every structural rule is checked against the
# generated Kotlin. A verification-only implementation map compares code-owned
# facts with design-spec.json; it is never consumed by code generation.
#
# Usage:
#   bash scripts/validate_workflow_and_build.sh <target> \
#       --input-mode <mode> --generation-mode <mode> [--visual-asset true|false] \
#       [--design-gate-result designer_passed|user_package_passed] \
#       [--design-color <custom-token>=<#hex>]... | [--no-design-colors] \
#       [--profile patch] [--skip-*] [--allow-degraded]
#
# Preflight: invocation + design-color coverage against design-spec.json
# Step order:
#   1. intent brief + handoff receipts (designer gate + scaffold-only onboarding handoff)
#   2. implementation scanner (root, entry, manifest, Stage legality, components)
#   3. design fidelity (design-spec.json vs implementation mapping + source)
#   4. Gradle sync/project discovery (CLI proxy for Android Studio sync)
#   5. smoke build (assembleDebug)
#   6. runtime launch check (installDebug + launch Activity + crash scan)
#   7. architecture conventions (check_architecture.py)
#   8. JVM unit tests (testDebugUnitTest)
#   9. spatial-ui-design-style verifier
#
# Figma MCP hooks (d2c_verify_code -> targeted fixes -> d2c_cleanup_temp) are
# agent-owned, because a shell wrapper cannot call MCP tools. See SKILL.md.
#
# The --skip-* flags are emergency hatches, except --skip-design-style which is
# intentionally a hard failure for generated Compose UI.
# ----------------------------------------------------------------------------
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <target> --input-mode <mode> --generation-mode <mode> [--visual-asset true|false] [--design-gate-result designer_passed|user_package_passed] [--require-assumptions] [--skip-design-style] [--skip-architecture] [--skip-unit-tests] [--skip-gradle-sync] [--skip-runtime-launch] [--allow-degraded]" >&2
    exit 2
fi

TARGET="$1"
shift || true

# Invalidate the previous receipt before parsing any remaining arguments. A
# caller may read this file after any exit, including an invocation error or an
# interrupted run, so an older clean=true result must never survive the start
# of a new verification attempt.
SCRATCH_DIR=""
VERIFICATION_SUMMARY=""
SUMMARY_FINALIZED="false"

write_non_clean_summary() {
    local status="$1"
    local exit_code="${2:-}"
    python3 - "$VERIFICATION_SUMMARY" "$status" "$exit_code" <<'PY'
import json
import os
import sys
from pathlib import Path

path = Path(sys.argv[1])
status = sys.argv[2]
exit_code = sys.argv[3]
data = {
    "passed": False,
    "operational": False,
    "clean": False,
    "stale": status == "running",
    "status": status,
    "warnings": [
        "Verification has not completed successfully; no current clean result is available."
    ],
    "skips": [],
    "adapter_hooks_agent_owned": True,
}
if exit_code:
    data["exit_code"] = int(exit_code)

temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
temporary.replace(path)
PY
}

finalize_summary_on_exit() {
    local exit_code=$?
    trap - EXIT
    if [ -n "$VERIFICATION_SUMMARY" ] &&
        [ "$exit_code" -ne 0 ] &&
        [ "$SUMMARY_FINALIZED" != "true" ]; then
        write_non_clean_summary "failed" "$exit_code" || true
    fi
    exit "$exit_code"
}
trap finalize_summary_on_exit EXIT

if [ -d "$TARGET" ]; then
    SCRATCH_DIR="$TARGET/.scratch"
    mkdir -p "$SCRATCH_DIR"
    VERIFICATION_SUMMARY="$SCRATCH_DIR/verification_summary.json"
    rm -f -- "$VERIFICATION_SUMMARY"
    write_non_clean_summary "running"
fi

REQUIRE_ASSUMPTIONS="false"
INPUT_MODE=""
GENERATION_MODE=""
VISUAL_ASSET="false"
DESIGN_GATE_RESULT="designer_passed"
PROFILE="default"
DESIGN_COLOR_ARGS=()
DESIGN_COLOR_VALUES=()
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
        --design-gate-result)
            shift; DESIGN_GATE_RESULT="${1:-}"
            ;;
        --profile)
            shift; PROFILE="${1:-default}"
            ;;
        --design-color)
            shift
            [ -n "${1:-}" ] || { echo "[validate] --design-color needs <slot>=<#hex>" >&2; exit 2; }
            DESIGN_COLOR_ARGS+=(--design-color "$1")
            DESIGN_COLOR_VALUES+=("$1")
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
            echo "Usage: $0 <target> --input-mode <mode> --generation-mode <mode> [--visual-asset true|false] [--design-gate-result designer_passed|user_package_passed] [--require-assumptions] [--skip-design-style] [--skip-architecture] [--skip-unit-tests] [--skip-gradle-sync] [--skip-runtime-launch] [--allow-degraded]" >&2
            exit 2
            ;;
    esac
    shift
done

if [ ! -d "$TARGET" ]; then
    echo "[validate] Target directory not found: $TARGET" >&2
    exit 2
fi

DESIGN_STYLE_RESULT="$SCRATCH_DIR/design_style_result.json"
DESIGN_SPEC="$SCRATCH_DIR/design-spec.json"
WARNINGS=()
SKIPS=()

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RECEIPT_CHECKER="$SCRIPT_DIR/check_handoff_receipts.py"
IMPL_SCANNER="$SCRIPT_DIR/scan_implementation.py"
DESIGN_FIDELITY_CHECKER="$SCRIPT_DIR/check_design_fidelity.py"
SMOKE_BUILD="$SCRIPT_DIR/smoke_build.sh"
GRADLE_SYNC="$SCRIPT_DIR/gradle_sync_check.sh"
ARCH_CHECKER="$SCRIPT_DIR/check_architecture.py"
UNIT_TESTS="$SCRIPT_DIR/run_unit_tests.sh"
RUNTIME_LAUNCH="$SCRIPT_DIR/runtime_launch_check.sh"

# Resolve sibling spatial-ui-design-style verifier.
SKILLS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DESIGN_STYLE_VERIFIER="$SKILLS_ROOT/spatial-ui-design-style/scripts/verify-design-style.sh"

for required in "$RECEIPT_CHECKER" "$IMPL_SCANNER" "$DESIGN_FIDELITY_CHECKER" "$GRADLE_SYNC" "$SMOKE_BUILD" "$RUNTIME_LAUNCH" "$ARCH_CHECKER" "$UNIT_TESTS"; do
    if [ ! -f "$required" ]; then
        echo "[validate] required script not found: $required" >&2
        exit 2
    fi
done

if [ -z "$INPUT_MODE" ] || [ -z "$GENERATION_MODE" ]; then
    echo "[validate] --input-mode and --generation-mode are required" >&2
    exit 2
fi
if [ "$DESIGN_GATE_RESULT" != "designer_passed" ] &&
    [ "$DESIGN_GATE_RESULT" != "user_package_passed" ]; then
    echo "[validate] --design-gate-result must be designer_passed or user_package_passed" >&2
    exit 2
fi

echo "[validate] [preflight] invocation and design-color contract"
python3 - "$DESIGN_SPEC" "$NO_DESIGN_COLORS" ${DESIGN_COLOR_VALUES[@]+"${DESIGN_COLOR_VALUES[@]}"} <<'PY'
import json
import sys
from pathlib import Path

spec_path = Path(sys.argv[1])
no_design_colors = sys.argv[2] == "true"
raw_colors = sys.argv[3:]


def fail(message):
    print(f"[validate] ERROR {message}", file=sys.stderr)
    raise SystemExit(2)


if raw_colors and no_design_colors:
    fail("--design-color and --no-design-colors are mutually exclusive")
if not raw_colors and not no_design_colors:
    fail(
        "custom design colors were not declared; pass --design-color "
        "<token>=<#hex> for every app-owned color, or --no-design-colors "
        "if there are none"
    )

actual = {}
for entry in raw_colors:
    token, separator, value = entry.partition("=")
    if not separator or not token or not value:
        fail(f"invalid --design-color {entry!r}; expected <token>=<#hex>")
    if token in actual:
        fail(f"duplicate --design-color token {token!r}")
    actual[token] = value

if spec_path.is_file():
    try:
        document = json.loads(spec_path.read_text(encoding="utf-8"))
        expected = document["theme"]["brandColors"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        fail(f"cannot read design-spec.json theme.brandColors: {exc}")
    if not isinstance(expected, dict):
        fail("design-spec.json theme.brandColors must be an object")

    errors = []
    for token, expected_value in expected.items():
        actual_value = actual.get(token)
        if actual_value is None:
            errors.append(f"missing --design-color {token}={expected_value}")
        elif (
            not isinstance(expected_value, str)
            or actual_value.casefold() != expected_value.casefold()
        ):
            errors.append(
                f"mismatched --design-color {token}: expected {expected_value}, got {actual_value}"
            )
    for token, actual_value in actual.items():
        if token not in expected:
            errors.append(f"unexpected --design-color {token}={actual_value}")
    if errors:
        fail("; ".join(errors))

print("[validate] design-color contract passed")
PY

echo "[validate] [1/9] intent brief and handoff receipts"
python3 "$RECEIPT_CHECKER" --target "$TARGET" \
    --input-mode "$INPUT_MODE" \
    --generation-mode "$GENERATION_MODE" \
    --visual-asset "$VISUAL_ASSET" \
    --design-gate-result "$DESIGN_GATE_RESULT"

echo "[validate] [2/9] implementation scanner"
python3 "$IMPL_SCANNER" --target "$TARGET" \
    --generation-mode "$GENERATION_MODE" \
    --profile "$PROFILE"

echo "[validate] [3/9] design JSON to app fidelity"
python3 "$DESIGN_FIDELITY_CHECKER" --target "$TARGET" \
    --design-spec "$DESIGN_SPEC" \
    --input-mode "$INPUT_MODE" \
    --visual-asset "$VISUAL_ASSET"

# ---------- Gradle sync / project discovery gate ----------
echo "[validate] [4/9] Gradle sync/project discovery"
if [ "$SKIP_GRADLE_SYNC" = "true" ]; then
    SKIPS+=("gradle_sync")
    WARNINGS+=("--skip-gradle-sync supplied; Gradle project discovery / IDE sync proxy not enforced")
    echo "[validate] WARN --skip-gradle-sync supplied; Gradle project discovery / IDE sync proxy NOT enforced. The skill still requires Android Studio Sync Project with Gradle Files before first IDE run."
else
    bash "$GRADLE_SYNC" "$TARGET"
fi

echo "[validate] [5/9] smoke build"
bash "$SMOKE_BUILD" "$TARGET"

# ---------- runtime install + launch gate ----------
echo "[validate] [6/9] runtime install/launch"
if [ "$SKIP_RUNTIME_LAUNCH" = "true" ]; then
    SKIPS+=("runtime_launch")
    WARNINGS+=("--skip-runtime-launch supplied; install/launch not enforced")
    echo "[validate] WARN --skip-runtime-launch supplied; install/launch NOT enforced. The skill still requires a clean run for sign-off."
else
    bash "$RUNTIME_LAUNCH" "$TARGET"
fi

# ---------- architecture conventions gate ----------
echo "[validate] [7/9] architecture conventions"
if [ "$SKIP_ARCHITECTURE" = "true" ]; then
    SKIPS+=("architecture")
    WARNINGS+=("--skip-architecture supplied; architecture conventions not enforced")
    echo "[validate] WARN --skip-architecture supplied; architecture conventions NOT enforced. The skill still requires a clean run for sign-off."
else
    python3 "$ARCH_CHECKER" --target "$TARGET"
fi

# ---------- unit-test gate ----------
echo "[validate] [8/9] unit tests"
if [ "$SKIP_UNIT_TESTS" = "true" ]; then
    SKIPS+=("unit_tests")
    WARNINGS+=("--skip-unit-tests supplied; ViewModel/UseCase tests not enforced")
    echo "[validate] WARN --skip-unit-tests supplied; ViewModel/UseCase tests NOT enforced. The skill still requires a clean run for sign-off."
else
    bash "$UNIT_TESTS" "$TARGET"
fi

# ---------- design-style admission gate ----------
echo "[validate] [9/9] design-style admission"
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
        # R1b needs the authoritative app-owned custom colors. Native
        # ColorScheme roles remain unchanged and are not forwarded.
        DESIGN_COLOR_FLAGS=()
        if [ "${#DESIGN_COLOR_ARGS[@]}" -gt 0 ]; then
            DESIGN_COLOR_FLAGS=("${DESIGN_COLOR_ARGS[@]}")
        elif [ "$NO_DESIGN_COLORS" = "true" ]; then
            DESIGN_COLOR_FLAGS=(--no-design-colors)
        else
            echo "[validate] FAIL custom design colors were not declared. Pass --design-color <custom-token>=<#hex> for every app-owned color, or --no-design-colors if there are none." >&2
            python3 - "$DESIGN_STYLE_RESULT" <<'PY2'
import json
import sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({"passed": False, "skipped": False, "summary": {"errors": 1, "warnings": 0}, "failures": ["custom design colors not declared: pass --design-color or --no-design-colors"]}, indent=2), encoding="utf-8")
PY2
            exit 1
        fi

        echo "[validate] running spatial-ui-design-style verifier on: $DESIGN_STYLE_PATH"
        DESIGN_STYLE_LOG="$SCRATCH_DIR/design_style.log"
        DESIGN_SPEC_FLAGS=()
        if [ -f "$DESIGN_SPEC" ]; then
            DESIGN_SPEC_FLAGS=(--design-spec "$DESIGN_SPEC")
        fi
        if bash "$DESIGN_STYLE_VERIFIER" "$DESIGN_STYLE_PATH" "${DESIGN_COLOR_FLAGS[@]}" ${DESIGN_SPEC_FLAGS[@]+"${DESIGN_SPEC_FLAGS[@]}"} >"$DESIGN_STYLE_LOG" 2>&1; then
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

FINAL_STATUS="passed"
FINAL_EXIT_CODE=0
if [ "$CLEAN" != "true" ]; then
    if [ "$ALLOW_DEGRADED" = "true" ]; then
        FINAL_STATUS="degraded"
    else
        FINAL_STATUS="failed"
        FINAL_EXIT_CODE=1
    fi
fi

python3 - "$VERIFICATION_SUMMARY" "$CLEAN" "$ALLOW_DEGRADED" "$FINAL_STATUS" "$FINAL_EXIT_CODE" "${WARNINGS[@]+"${WARNINGS[@]}"}" -- "${SKIPS[@]+"${SKIPS[@]}"}" <<'PY'
import json
import os
import sys
from pathlib import Path

path = Path(sys.argv[1])
clean = sys.argv[2] == "true"
allow_degraded = sys.argv[3] == "true"
status = sys.argv[4]
exit_code = int(sys.argv[5])
rest = sys.argv[6:]
split = rest.index("--") if "--" in rest else len(rest)
warnings = rest[:split]
skips = rest[split + 1:] if split < len(rest) else []
data = {
    "passed": clean,
    "operational": True,
    "clean": clean,
    "stale": False,
    "status": status,
    "allow_degraded": allow_degraded,
    "warnings": warnings,
    "skips": skips,
    "adapter_hooks_agent_owned": True,
    "note": "clean=false means a gate was skipped or degraded; --allow-degraded is operational-only, not skill-complete. Figma runs are still pending until the agent completes the d2c verify/cleanup hooks and records figma_hooks_result.json.",
}
if exit_code:
    data["exit_code"] = exit_code
temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
temporary.replace(path)
PY
SUMMARY_FINALIZED="true"

echo "[validate] WROTE $VERIFICATION_SUMMARY"
if [ "$CLEAN" = "true" ]; then
    echo "[validate] MACHINE GATES PASSED clean: handoff receipts + implementation scan + design fidelity + Gradle sync/project discovery + smoke build + runtime launch + architecture + unit tests + design-style passed. Figma runs remain pending until agent-owned d2c hooks write figma_hooks_result.json"
else
    echo "[validate] DEGRADED: machine gates completed with warnings/skips; exit 0 with --allow-degraded is operational-only, not skill-complete. See $VERIFICATION_SUMMARY and disclose warnings/skips in handoff"
    if [ "$FINAL_EXIT_CODE" -ne 0 ]; then
        echo "[validate] FAIL degraded run requires explicit --allow-degraded to exit 0" >&2
        exit "$FINAL_EXIT_CODE"
    fi
fi
