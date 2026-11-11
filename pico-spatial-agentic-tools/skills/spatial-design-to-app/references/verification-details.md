### Stage 5 — Verify

#### 5a. Machine gates

When `design-spec.json` exists, write
`.scratch/design_implementation_map.json` before running the command. Follow
`./design-package-bridge.md` §E: record the current design file hash,
the implementation-side contract facts, and source anchors for every required
surface, node, state, transition, action, responsive rule, data case, and
asset. This is a verification receipt, not a second design IR: it is never an
input to Build, and its implementation values must be observed from the
finished app rather than copied blindly from the design.

```bash
bash scripts/validate_workflow_and_build.sh <target> \
    --input-mode <mode> --generation-mode <mode> [--visual-asset true] \
    [--design-gate-result user_package_passed] \
    --design-color <custom-token>=<#hex> ...   # or --no-design-colors
    [--profile patch] [--skip-*] [--allow-degraded]
```

Nine steps: handoff receipts → implementation scan → design JSON-to-App
fidelity → Gradle sync → smoke build → runtime launch → architecture → unit
tests → design-style admission.

The fidelity gate runs before Gradle. It reads the authoritative
`design-spec.json`, rejects a missing or stale implementation map, compares
layout/component/state/responsive implementation facts exactly, and verifies
that every required design entity points to existing source symbols and
evidence. A mismatch such as `layout.mode=grid`, `columns=4` in the design but
`mode=row` in the implementation receipt is a hard failure. For routes without
a `design-spec.json`, the result is explicitly `applicable=false`; no JSON
fidelity claim is made.

Pass every app-owned custom design color with `--design-color`; native
`ColorScheme` roles are not included because they must remain unchanged. Pass
`--no-design-colors` only when the design has no custom colors.

Before invoking the verifier, compare the `--design-color` arguments against
the Stage 2 custom-color inventory. Names and values must cover every
`brandColors` entry and must not use a reserved SpatialUI role name.

Design-style admission is non-optional: a missing verifier, missing source root,
verifier failure, or `--skip-design-style` all fail the run.
Its typography-ceiling findings are warnings rather than build failures, but
they must be disclosed and reviewed; a direct large `Text.style` with no
accepted-design source is an implementation fidelity defect.

When `design-spec.json` exists, design-style admission also scans actual Kotlin
for app-authored surfaces. Every `.background(...)` or content `Card(...)` must
carry a valid `design-style: design-surface <node-id>` marker whose node declares
a fill, and one node ID may mark at most one background call. Any
`.backgroundMaterial(...)`, `.border(...)`, or `BorderStroke(...)` in app
source is a hard failure. This negative scan prevents extra decoration from
being hidden by an otherwise correct implementation receipt.

App-authored background fills must match the accepted node or part's fill,
placement, and state conditions. Structural regions without a fill stay
transparent; an undeclared state inherits the part's base fill rather than
introducing a new fill. A `brandColors` entry does not authorize another use.
Preserve Native components' own default appearance. A valid marker or allowed
color alone does not prove background fidelity.

Do NOT paraphrase JSON results — read `design_fidelity_result.json.passed`,
`passed` / `failures_or_explicit_none` / `warnings_or_explicit_none` literally.
The validator writes a versioned summary using its shared `verification-summary.mjs`
helper. It captures source, resources, build configuration, tests, and design bytes
before and after the checks. Both Compose gates recompute that identity and require
the same passed check set. Do not author or copy digest fields; after an input
changes, rerun validation. Scratch outputs, build outputs, and tool caches are
excluded by the helper's single input-selection rule.

`verification_summary.json.clean: false` means a degraded run and exits non-zero
unless `--allow-degraded` was explicit. Disclose every warning and skip; never
imply a skipped gate passed.

#### 5b. Figma MCP hooks (when the input carried a Figma URL)

These tools belong to the external `codin-d2c-figma-to-code` server checked in
stage 1b — they are not provisioned by this plugin. They apply only to a run that
actually stayed on the `visual_design` route with the tools present.

Order is strict, and each tool runs **exactly once**:

1. `d2c_verify_code` — pass the files generated or materially changed in this run (exclude config, lockfiles, untouched, tooling, test, and mock files). Use `ruleContext` to ask for geometry, color, and state fidelity against the XML/preview.
2. Apply targeted fixes for **Critical / Moderate** findings only. Do not call `d2c_verify_code` a second time.
3. `d2c_cleanup_temp` — same URL and directory as the original `d2c_get_figma_data` fetch.

⚠ Cleanup must never run before verify: verify reads the temporary XML and
preview files that the fetch wrote, so cleaning up first strips the evidence the
visual fixes depend on.

Record the outcome in `.scratch/figma_hooks_result.json`.

#### 5c. Structural and visual self-review (LLM-owned)

The fidelity receipt is traceability evidence, not a Kotlin semantic proof or a
pixel comparator. Inspect the running app against the accepted preview or
visual source. The machine cannot check these — do them yourself:

- repeated structures preserved as templates, not copy-pasted blocks
- selected / disabled / highlighted states represented in state holders
- **window model actually matches the built structure** (one primary surface for `single_panel` / `sidebar_content` / `master_detail`; a popup is not a second window)
- **`multi_window` is justified by disconnected-surface evidence** — no machine check covers this
- no UI invented beyond the input
- inspect actual app-authored background calls and their condition branches
  using source mappings; compare each with the accepted node/part base and
  state fills. Added fills, changed colors/placement, and extra state conditions
  are fidelity defects. The receipt alone cannot establish this check. Record
  unresolved dynamic expressions as unverified rather than passing them; use
  existing relevant runtime evidence when available without adding a capture
  or screenshot-driven repair loop.
- in `existing_module` mode, module resources reused before adding new ones
- every icon follows the declared source priority and
  [Image and icon sources](./preview-first-restoration.md#image-and-icon-sources);
  packaged SVGs and bitmaps preserve the accepted files, bundled native vectors
  match their catalog source, and icon slots retain semantic tint and
  accessibility text without tinting multicolor artwork

Review implementation through source/spec inspection and the clean
machine-validation receipt. Do not capture runtime screenshots or compare the
App with the Preview after Compose implementation. There is no screenshot-driven
visual repair path. Preserve the existing source repair, build, validation, and
launch requirements; disclose unresolved source/spec findings without reopening
or mutating the frozen design.

For Planar, restore `surface.windowBackground ?? "material"` through the owning
Native WindowContainer configuration. Default to enabled Material.Regular;
only an explicit transparent request with `windowBackgroundEvidence` disables
the background. For the primary manifest-owned window, materialbackground is
1 for material and 0 for transparent. Keep the container. Do not copy Preview's
#DAD6D3 environment, #CACACA fallback, outline or shadow into Compose, or apply
the primary-window setting to independent Subwindows. Volume/Stage gain no new
material requirement. Browser stage fitting does not change Native placement.

Check accepted layout and window facts in source. Restore directional
layout.paddingDp to physical Compose edges (absolutePadding for a direct
mapping), not uniform padding or an invented inset. For Subwindows, inspect the
accepted attachment declarations and selection-update wiring. This source
review does not establish runtime geometry or visibility.

Run the machine gates once to green. Structural self-review is a single pass, not
a loop; if all gates in the Exit checklist hold, stop and report. Re-enter a stage
only through the Backtrack rule (5d) on an actual repeated failure (new evidence),
never to gather extra confidence on already-green gates.

#### 5d. Backtrack

After 2 consecutive failures at the same check, return to the originating stage
instead of patching code again:

| Failure signal                                                   | Go back to                     |
| ---------------------------------------------------------------- | ------------------------------ |
| `stage_api_legality` failures                                    | Decide (container)             |
| `root_change_guard` failures                                     | Decide + Build entry wiring    |
| `root_match` / `entry_wired` / `manifest_consistency` failures   | Build (manifest + entry chain) |
| `invented_component_names` failures                              | Build (component selection)    |
| `spatialui_component_floor` / `window_chrome_ornaments` warnings | Build (component selection)    |
| `design_fidelity_result.json` fact / coverage failures           | Build (JSON → app mapping)     |
| `design_fidelity_result.json` stale hash                         | Extract, then rebuild mapping  |
| `design_style_result.json` failures                              | Build (design-style admission) |
| Smoke build `Unresolved reference: <Component>`                  | Build (component whitelist)    |
| Smoke build `IllegalStateException: not in Full Space`           | Decide (container)             |

Fix the cause at that stage; do not silently rewrite code that contradicts an
unchanged decision.

