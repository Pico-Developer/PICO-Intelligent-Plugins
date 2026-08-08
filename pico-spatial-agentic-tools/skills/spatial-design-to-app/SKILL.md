---
name: spatial-design-to-app
description: Use when creating or materially updating a product-specific PICO Spatial Android/Kotlin app from Figma, screenshot/mockup, PRD, intent, hybrid sources, or a bounded panel patch, and the task requires container, window model, panel hierarchy, layout contract, implementation, and verification. For generic empty-dir quickstarts use spatial-app-onboarding. NOT for SDK upgrades, legacy Android porting, pure code review/refactor, old-baseline D2C A/B evaluation, or performance diagnosis.
license: 'Apache-2.0'
---

# Product-Specific Source → PICO Spatial Android App

> 🔴 **Contract touchpoints** (progressive loading; read at the phase that needs them):
>
> 1. `references/workflow-contract.md` — Phase 1 / 4 / 5 / 7 artifact schemas, reflection fields, Backtrack table.
> 2. `references/architecture-conventions.md` — Phase 6 before Kotlin/Compose code: layered packages + ViewModel/UseCase/Repository + unit-test floor.
> 3. `../spatial-ui-design-style/SKILL.md` — Phase 6 before Compose UI, especially screenshot/visual codegen: PicoTheme / Material / hover / click+haptics / R1–R8 rules. This is a generation-time contract, not a final lint suggestion.

## Boundary

| Situation                                                        | Use instead                 |
| ---------------------------------------------------------------- | --------------------------- |
| Upgrade SDK / migrate deprecated APIs                            | `spatial-sdk-update`        |
| Generic empty-dir quickstart / scaffold-only first runnable demo | `spatial-app-onboarding`    |
| Migrate 2D Android app to spatial                                | `porting-android-app`       |
| Performance diagnosis                                            | `spatial-app-perf-diagnose` |
| 3D bbox / placement planning                                     | `spatial-sdk-scene-builder` |

## Routing Position

Use this skill as the primary route when the user wants a product-specific PICO Spatial Android app from Figma, screenshot/mockup, PRD, intent, hybrid sources, or a bounded existing-panel patch. For a new project, this skill owns the evidence, container, window model, and layout contract first; only the raw scaffold step is delegated to `spatial-app-onboarding` after Phase 4.

Do not use this skill for a generic empty-directory quickstart whose only goal is "create a first runnable Spatial project"; route that directly to `spatial-app-onboarding`.

## Reference index (read on demand, never preemptively)

| Read when …                                                                             | File                                                                       |
| --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Phase 1 / 3 — input mode + evidence                                                     | `references/input-normalization.md`, `references/evidence-extraction.md`   |
| Phase 3 / 5 — visual layout inference, region decomposition, repeated/state mapping     | `references/layout-inference.md`                                           |
| Phase 1.5 — adapter dispatch                                                            | `adapters/_registry.json` + the selected `adapters/*-adapter.md`           |
| Phase 1.5 — validating/editing adapter contract or registry                             | `ADAPTER_ROADMAP.md`                                                       |
| Phase 1.5 / 3 — no-visual design escalation + design-package facts → three-artifact set | `references/design-package-bridge.md`                                      |
| Phase 4 — container + window model                                                      | `references/container-decision.md`, `references/window-model-decision.md`  |
| Phase 4 — `spatial_features` includes anchor / env_mesh                                 | `references/spatial-anchor.md` _(BLOCK if anchor in WindowContainer)_      |
| Phase 5 — layout schema                                                                 | `references/layout-schema.md`                                              |
| Phase 6 — entry chain + manifest                                                        | `references/manifest-and-entry.md` + (`window-container.md` OR `stage.md`) |
| Phase 6 — gradle setup errors                                                           | `references/gradle-setup.md`                                               |
| Phase 6 — SpatialUI component whitelist                                                 | `references/spatial-ui-components.md`                                      |
| Phase 6 / figma-adapter — Figma tokens + visual feature mapping                         | `references/figma-mapping.md`                                              |
| Phase 6 / figma-adapter — SpatialUI import lookup                                       | `references/spatial-api-imports.md`                                        |
| Phase 4 / 6 — window-level components, Subwindow, floating layers                       | `references/spatial-windows-guide.md`                                      |
| Phase 6 — architecture + tests                                                          | `references/architecture-conventions.md`                                   |

## 7-phase flow

| #   | Name              | Artifact                                                                     | Gate                                                                  |
| --- | ----------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 1   | Frame             | `Input Envelope`                                                             | inputs explicit                                                       |
| 1.5 | Adapter Selection | selected adapter + hook plan; execution may wait for Phase 2 workspace facts | one adapter max per current input_mode                                |
| 2   | Read              | inspection notes                                                             | (none)                                                                |
| 3   | Spec              | `Evidence Packet` + `Normalized Spec` + `Assumption Ledger`                  | normalization complete                                                |
| 4   | Decide            | `Container Decision` + `Window Model Decision`                               | legality + singularity                                                |
| 5   | Plan              | `Spatial Layout Contract` (or `Patch Contract`)                              | contract complete                                                     |
| 6   | Build             | code edits / scaffold                                                        | (verified in 7)                                                       |
| 7   | Verify            | 11-step gate / adapter hooks (see Phase 7)                                   | machine-driven + Gradle sync + runtime launch + agent-owned MCP hooks |

`incremental_patch` mode skips Phase 4 (inherit from existing module) and Phase 5 emits a `Patch Contract`.

## Operating protocol

- **Sequential & gated.** No skipping artifacts; no proceeding past a failed gate. On failure: fix the artifact, apply a conservative default and log it in `Assumption Ledger`, or ask the user only if the unresolved issue materially changes the architecture.
- **Output language.** Match the user's natural language for prose; artifact JSON keys, command names, and `Step Output` labels stay in canonical English.
- **Persistence.** Artifacts live under `<target>/.scratch/` with canonical filenames (`input_envelope.json`, `evidence_packet.json`, `normalized_spatial_spec.json`, `assumption_ledger.json`, `spatial_layout_contract.json` or `patch_contract.json`). `assumption_ledger.json` is always present; use `[]` only when no assumptions exist.
- **Resume.** If `<target>/.scratch/` already contains valid artifacts when the skill starts, do NOT re-emit them — re-run the scripts (cheap) and resume at the first missing/failing artifact. Delete `.scratch/` only on explicit "redo from scratch".
- **Step Output (Phases 1, 4, 5, 7 only).**

  ```text
  Step Output
  - Artifact: <name>
  - Summary: <1-3 lines>
  - Key fields: <bullets>
  - Reflection: <citation per workflow-contract.md>
  - Gate result: PASS | BLOCKED
  - Next action: proceed | revise | conservative default | ask user
  ```

---

## Phase 1 — Frame

Apply input-mode routing in order, first match wins:

```
Step A — incremental_patch?
  IF user names a specific file/panel/module
     AND scope ≤ 1–2 regions or components
     AND root container + window model do NOT need to change
  THEN input_mode = incremental_patch.   STOP.

Step B — otherwise classify by strongest source:
  Figma URL                     → visual_design
  screenshot / mockup image     → visual_reference
  PRD / long-form spec          → product_doc
  one-line ask only             → intent_only
  more than one of the above    → hybrid
```

| User says                                               | Routing             |
| ------------------------------------------------------- | ------------------- |
| "add a search field to `MainPanel.kt` in `myapp`"       | `incremental_patch` |
| "use this Figma to redesign `myapp`'s home page"        | `visual_design`     |
| "use this Figma to add a close button to `DetailPanel`" | `incremental_patch` |

Decide `generation_mode` (`existing_module` / `new_project`) and emit `Input Envelope` per workflow-contract.md §1. Gate: `input_mode`, `generation_mode`, target / output, `input_sources[]` all explicit.

## Phase 1.5 — Adapter Selection

Read `adapters/_registry.json`, select exactly one active adapter for the current `input_mode`, then read only that adapter. Zero / multiple active matches = BLOCKED. This phase selects the adapter and installs any `hooks.verify` / `hooks.cleanup` plan for Phase 7; it does not force evidence extraction before workspace facts exist. If the selected adapter requires target platform, root container, or existing window model, execute that adapter after Phase 2 inspection and feed its output into Phase 3. Adapters are limited to existing `evidence_packet.json` / `normalized_spatial_spec.json` / `assumption_ledger.json` schema fields; their seven-field contract lives in `ADAPTER_ROADMAP.md`.

Adapter `failure_mode` may explicitly reroute to another `input_mode` (for example Figma → screenshot fallback). In that case, revise `input_envelope.json`, return to Phase 1.5, and select exactly one adapter for the new mode. Do not chain a second adapter under the old `input_mode`, and do not silently fall back.

### Phase 1.5a — Design escalation gate (no-visual inputs)

Before extracting evidence for a no-visual request, check whether the design must be escalated to `pico-spatial-app-designer`.

- **Trigger:** `input_mode ∈ { intent_only, product_doc }`, or `hybrid` with no Figma URL and no screenshot/mockup — i.e. no visual asset of any kind is present in `input_sources[]`. When a Figma URL, screenshot, or mockup exists, this gate does NOT fire; continue directly through the existing flow.
- **Action:** stop app generation and run the `pico-spatial-app-designer` workflow to produce a design package. `pico-spatial-app-designer/workflow.json` is orchestrated by the host LLM; review isolation is a designer workflow quality gate, not a reason to skip the designer. Wait until it reports `designStatus = ready_for_design_delivery` AND `downstreamAppGenerationAllowed = yes` AND a recorded main-thread acceptance exists (three gates; sources per `references/design-package-bridge.md` §A.1).
- **Receipt:** write `<target>/.scratch/design_escalation_receipt.json` before Phase 3 whenever this gate fires. Only `status=designer_passed` is valid for no-visual app generation, and it requires all three pre-gates, `bridge_allowed=true`, and `adapter_extraction=design_package_bridge`. `status=fallback_accepted` / `adapter_extraction=shallow_text_extraction` is not a valid app-generation path.
- **After all three gates pass:** the selected adapter (`intent-adapter` / `prd-adapter`) reads the receipt, then performs a high-confidence extraction from the design package per `references/design-package-bridge.md` (6 `review/*.md` role docs + `preview.html` → the three-artifact set), then proceeds into Phase 3–7.
- **Blocked state:** if `pico-spatial-app-designer` is unavailable, the user declines the design pass, or any of the three gates fails, stop before Phase 3 and report BLOCKED with the missing designer deliverables/gates. Do not continue with shallow text extraction.
- **Invariants:** the design escalation gate does NOT change adapter singularity (each `input_mode` still resolves to exactly one active adapter), does NOT add an `input_mode`, and does NOT add any top-level schema field. The final container / window model decision still belongs to Phase 4.

Required JSON artifact before entering Phase 3:

```json
{
  "schema_version": 1,
  "phase": "1.5a_design_escalation_gate",
  "input_mode": "<input_envelope.input_mode>",
  "visual_asset_present": false,
  "gate_required": true,
  "status": "designer_passed",
  "pre_gates": {
    "designStatus": "ready_for_design_delivery",
    "downstreamAppGenerationAllowed": "yes",
    "mainThreadAcceptanceRecorded": true
  },
  "bridge_allowed": true,
  "adapter_extraction": "design_package_bridge"
}
```

`pre_gates` is required when `status=designer_passed`. `Gate result` is
not a receipt JSON field; it belongs only to the prose `Step Output` below.

Required LLM `Step Output` before entering Phase 3:

```text
Step Output
- Artifact: Design Escalation Receipt (`.scratch/design_escalation_receipt.json`)
- Summary: no-visual input requires / does not require designer gate
- JSON artifact fields: schema_version, phase, input_mode, visual_asset_present, gate_required, status, pre_gates, bridge_allowed, adapter_extraction
- Reflection: cite input_envelope.input_mode and input_sources[]
- Gate result: PASS | BLOCKED (Step Output only; do not write this as a receipt JSON field)
- Next action: run designer | bridge package | proceed
```

## Phase 2 — Read (workspace inspection, only in `existing_module` / `incremental_patch`)

Inspect: module `build.gradle.kts`, `AndroidManifest.xml`, `Main.kt`, `platform/SpatialApplication.kt`, `platform/LaunchActivity.kt`, existing `res/`. Prefer editing existing files; reuse package, manifest wiring, resources. Preserve current root container unless user explicitly asks otherwise or the requested feature is impossible. No JSON artifact — carry notes into Phase 3.

## Phase 3 — Spec

Emit, in order:

1. **Evidence Packet** — `facts` / `unknowns` / `conflicts` / `confidence`. Facts only.
2. **Normalized Spatial Spec** — `request_context` / `product_intent` / `spatial_intent` / `window_intent` / `layout_intent` / `ambiguities` / `evidence_trace`. On disagreement, pick one and explain the tie-break in `evidence_trace` (no parallel truths).
3. **Assumption Ledger** — every architecture-impacting default with `assumption` / `impact` / `confidence`.

### Visual input guardrails (HARD)

For screenshots/mockups, keep the main skill path concise and classify evidence by responsibility before planning. Detailed schemas and examples live in `references/workflow-contract.md` §5.
For `visual_reference` work, read `references/layout-inference.md` before finalizing `layout_intent`, `content_layout_metrics`, or `visual_content_contract`; use it to decompose regions, catch repeated/stateful structures, and sanity-check overlay relationships.

- Split visual evidence into app-owned window, window ornaments, page content, temporary floating layer, and spatial environment context.
- Do not treat passthrough / skybox / floor / scenery / system safety lines as app content unless facts prove the app owns them.
- Edge-pinned long-lived rails / tabs / toolbars are `window_chrome_ornaments[]` (`TabBar` / `Toolbar` / `Subwindow`), not page children. Not `multi_window` does not mean page content.
- `visual_reference` must carry `reference_frame`, `content_layout_metrics`, and `visual_content_contract`; derive window size from `app_owned_bbox_px`, not the full screenshot.
- Bind measured sizes and visual semantics to Phase-6 constants/components (`SideNavigation`, `SearchField`, fixed grids, asset-backed image cards) instead of magic dp or placeholder UI.

Gate: enough evidence to choose `generation_mode`, propose one `container_candidate`, compare ≥1 `window_model_candidate`. No hidden assumptions.

## Phase 4 — Decide (skip in `incremental_patch`)

Read `references/container-decision.md` and `references/window-model-decision.md`. If `spatial_features` includes anchor / env_mesh, also read `references/spatial-anchor.md` and resolve legality now.

### 4a. Container Decision

Required: `container` / `container_reason` / `container_evidence[]` / `rejected_near.{alternative, rejection_reason}` / `rejected_far.{alternative, rejection_reason}`.

### 4b. Window Model Decision

Choose one of: `single_panel`, `single_panel_with_popup`, `sidebar_content`, `master_detail`, `window_plus_subwindow`, `multi_window`. Same field requirements as 4a. Apply the Subwindow-vs-`multi_window` escalation rule from `window-model-decision.md`.

**Reflection (HARD):** `rejected_near` neighbouring, `rejected_far` distant; both `rejection_reason` MUST cite a concrete `Evidence Packet.facts.<key>`, a row of the legality table, or an escalation rule number. "not needed" / "not applicable" / "no evidence" = BLOCK. Apply legality inline — do NOT defer to Phase 7.

## Phase 5 — Plan

The contract IS the layout tree (no separate "internal" step). Required fields per workflow-contract.md §5:

If the input is screenshot/mockup-driven, consult `references/layout-inference.md` to sanity-check (do not re-derive) `regions[]`, `repeated_structures[]`, `states[]`, and `window_chrome_ornaments[]`; `layout_intent` stays frozen from Phase 3.

- `container` / `container_reason` / `window_model` / `window_reason`
- `root_fill` + `spacing_ownership[]` (whenever the design has any inset/padding/gap) — set `root_fill` (`fill_window` vs `padded_card`) explicitly and map every gap to its owning node; see `references/layout-schema.md` → "Spacing ownership & root fill". Never let codegen guess edge insets or outer margins.
- `stage_content_strategy` (whenever `container` is any `STAGE_*` mode) — one of `ecs_runtime` / `editor_bundle` / `explicit_fallback`, plus each 2D control's `AttachmentPanel` anchor + metric position. A Stage must not resolve to a flat Compose page; see `references/stage.md` → "Stage content model".
- `reference_frame` (`visual_reference` only) — screenshot px, app-owned bbox, target window dp, scale policy
- `content_layout_metrics` (`visual_reference` only) — panel padding, measured region rects, repeated item sizes/gaps. This is mandatory when generating screenshot-based page content.
- `visual_content_contract` (`visual_reference` only) — sidebar surface plus search/chip semantics when present, tab visible count/style, card content/overlay/asset policy.
- `window_chrome_ornaments[]` (when present) — `id`, `type` (`TabBar` / `Toolbar` / `Subwindow`), `placement`, `role`; ornaments are siblings of the main page, not main-page children.
- `windows[]` — `id`, `role`, `anchor`, `default_visibility`, `children`
- `regions[]` — hierarchy / states / alignment / size
- `repeated_structures[]`, `states[]`
- `evidence_trace[]` — ≥1 entry per primary window, each `fact_ref` citing a concrete `Evidence Packet.facts.<key>` or a Phase 4 decision field. "because the design says so" = BLOCK.

Persist to `<target>/.scratch/spatial_layout_contract.json`. For `incremental_patch`, emit `Patch Contract` instead.

## Phase 6 — Build

### Module mode rules

- **Existing module:** keep namespace/package, manifest wiring, entry chain. Allowed: new Compose files, new drawables/strings, new state holders. NOT allowed without explicit escalation: switching root container, changing `pico.spatial.windowcontainer.*` meta, introducing Stage-only APIs (anchor / ECS / env_mesh) inside a WindowContainer.
- **Product-specific new project request:** hand the resolved container contract
  to `spatial-app-onboarding` for the scaffold step. Pass the Phase-4 container
  decision as the upstream container contract so onboarding can select the
  matching CLI template. Resume this skill only after onboarding returns a
  runnable project handoff.

  Map the Phase-4 container contract for the onboarding handoff:
  `ON_PLAIN → planar`, `IN_VOLUME → volumetric`,
  `STAGE_MIXED|STAGE_PROGRESSIVE|STAGE_FULL → stage`. After onboarding returns,
  do NOT re-scaffold, rewrite `mainApp`, or re-insert manifest meta; build the
  requested experience on top of the generated entry point.

Entry chain: `Application.onCreate { launch(::mainApp) }` → `mainApp(scope: SpatialAppScope)` → `DefaultWindowContainer {}` or `DefaultStage {}` → `SpatialLaunchActivity`.

**Android Studio sync is mandatory for new modules.** After creating or including
a new module (`settings.gradle.kts` changed), trigger Android Studio
**Sync Project with Gradle Files** before claiming the app can be run from the
IDE. If no IDE-sync API is available to the agent, run the Gradle project
discovery proxy in Phase 7 and explicitly tell the user that Android Studio sync
is still required before the first IDE run/configuration selection.

### UI rules (layered + minimal)

- Generate UI from the Phase-5 contract only: root container → window ornaments → windows → regions → reusable components.
- Apply `spacing_ownership` / `root_fill` literally: a `fill_window` root gets an edge-to-edge background/surface with no root-level edge inset (insets go on the inner content), while a `padded_card` root carries its own outer padding/margin. Put each gap only on its declared owner — do not double-pad or drop the outer margin.
- Read `../spatial-ui-design-style/SKILL.md` before Compose UI; generated code must pass design-style admission without skip/degraded mode.
- Prefer SpatialUI built-ins and documented imports; never invent SDK names. `PicoTheme {}` wraps windowed UI; `windowConstraints(...)` is resize bounds, not first-open size.
- Keep business UI 2D unless Phase 5 justifies 3D / Stage behavior; Stage-only APIs stay out of WindowContainer flows.
- For a `STAGE_*` root, apply the declared `stage_content_strategy`: host 3D via `SpatialView` + ECS entities (`Entity()` / `Entity.load(...)` + `content.addEntity(...)`), attach 2D controls with `AttachmentPanel(id){}` positioned in meters on an ECS anchor — never a bare Compose overlay, and never a flat `Box`/`Column`/`Canvas` page. See `references/stage.md` → "Stage content model".
- Implement `window_chrome_ornaments[]` with window-level fittings, and implement `reference_frame` / `content_layout_metrics` / `visual_content_contract` through named constants, state, and components.
- Custom interactive components must follow spatial-ui-design-style indication + haptics rules, or use a built-in component that provides them.

### Architecture rules (HARD)

Read `references/architecture-conventions.md` before code. The checker enforces layered packages, thin `Main.kt`, MVI-lite state, repository boundaries, mandatory ViewModel tests, and UseCase + UseCase tests when the screen has non-trivial business rules, filtering, sorting, selection, or data transformation.

## Phase 7 — Verify (machine-driven)

Run `bash scripts/validate_workflow_and_build.sh <target>`. The canonical 11-step order, skip semantics, JSON outputs, and Figma hook ordering are in `references/workflow-contract.md`; smoke-build diagnosis is in `references/gradle-setup.md`. `spatial-ui-design-style` admission is non-optional for generated Compose UI: missing verifier, missing source root, verifier failure, or `--skip-design-style` must fail the run.

Do NOT paraphrase JSON results — read `passed` / `summary.errors` / `failures_or_explicit_none` literally. `verification_summary.json.clean: false` means a degraded run; it exits non-zero unless `--allow-degraded` was explicit. Disclose every `warnings[]` / `skips[]` entry and never imply skipped gates passed.

**Backtrack:** after 2 consecutive failures at the same check, return to the originating phase per the Backtrack table in `references/workflow-contract.md`. Edit the offending artifact first; do not silently rewrite code that contradicts an unchanged contract.

**Structural review** (LLM-owned, semantic): repeated structures preserved as templates; selected/disabled/highlighted states represented in state holders; no UI added beyond input; in `existing_module` mode, reuse module resources before adding new ones.

---

## Exit checklist

Run is complete only when ALL hold:

1. `validate_workflow_and_build.sh <target>` exits 0 **and** `<target>/.scratch/verification_summary.json.clean == true`. Only Gradle sync / runtime launch may be environment-degraded, and degraded runs are not complete unless explicitly accepted in handoff.
2. For new modules, Android Studio **Sync Project with Gradle Files** has been triggered, or the final handoff explicitly states that the user must trigger it before first IDE run because no IDE sync API was available.
3. `legality_check_result.json`, `implementation_scan_result.json`, `gradle_sync_result.json`, `architecture_check_result.json`, `unit_tests_result.json` all → `"passed": true`.
4. `design_style_result.json.passed == true` and design-style verifier → 0 errors; no `--skip-design-style` / degraded bypass.
5. If the selected adapter declares hooks, `adapter_hooks_result.json.passed == true` and verify / cleanup hooks ran in the registry order.
6. None of the hard-fail conditions in `workflow-contract.md` triggered.

Final handoff:

```text
- Container: <chosen + why>
- Window model: <chosen + why>
- Mode: <existing module update | new scaffold | incremental_patch>
- Path: <module path | output path>
- Designer gate: <passed | blocked | not_required>
- Bridge mode: <design_package_bridge | not_applicable>
- Android Studio sync: <done | user must run Sync Project with Gradle Files>
- Assumptions: <explicit list or 'none'>
- Remaining inferred/mock parts: <list>
- Workflow artifacts: Input Envelope / Design Escalation Receipt when required / Evidence Packet / Normalized Spec / Assumption Ledger / Spatial Layout Contract (or Patch Contract)
```

## Pitfalls (do not)

- skip workspace inspection when the user names a module (default to `existing_module`)
- restate Phase 3 in Phase 5 (the contract IS the layout tree)
- defer container × feature legality to Phase 7 (decide inline in Phase 4)
- confuse overlay with window — popup menus stay in one panel
- record spacing without an owner, or leave `root_fill` implicit — every inset/padding/gap needs one owner in `spacing_ownership`, and `fill_window` vs `padded_card` must be explicit (avoids edge-inset-on-fill and missing-outer-margin bugs)
- emit a `STAGE_*` root as a flat Compose page (`Box`/`Column`/`Canvas`) or drop immersive content into a 2D WindowContainer tree — declare a `stage_content_strategy`, host 3D via `SpatialView`+ECS, and attach 2D controls with `AttachmentPanel` on an anchor, never a bare overlay
- treat a `DefaultWindowContainer` + secondary `Stage(id=…)` app as a "mixed root" — that is a valid single-root app; only two coexisting _default_ roots are illegal
- carry `TabBar`/`Toolbar`/`Subwindow` into a Stage, or `AttachmentPanel` into a window — keep each surface to its own toolkit (see `container-decision.md` → responsibility boundaries)
- migrate a container to fix a compile/visual symptom — a container change re-runs Phase 4 and updates the contract first, then Main.kt/manifest/coordinates/ornaments/runtime launch
- escalate to `multi_window` without independent launcher / lifecycle / placement memory evidence
- invent SDK names; only the whitelist
- over-spatialize a 2D settings UI (most belong in `ON_PLAIN`)
- implement screenshot spatial background, passthrough, floor/trees/skybox, or system safety lines as app content
- fill Step Output with mechanical PASS — Reflection must cite a fact-key or legality-table row
- run the full 7-phase flow on a small patch; use `incremental_patch` mode
- emit code before reading `architecture-conventions.md` and `spatial-ui-design-style/SKILL.md`

**Honesty:** A 2D reference under-specifies a spatial app. State explicitly when passthrough / skybox / depth / hover / haptics / gestures were inferred; flag that anchors and Full Space behaviors require a device.

**Clarification:** ask the user only when one of these is truly unresolved — no visual reference is available, target module / output cannot be inferred, multiple window interpretations are equally plausible and materially change the app structure, or package / namespace conflict cannot be resolved safely. Otherwise proceed with the safest default and state the assumption.
