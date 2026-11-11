---
name: spatial-design-to-app
description: >-
  Use when a PICO Spatial app task needs UI design interpretation, Figma or screenshot
  extraction, container/window decisions, Compose restoration, or visual verification.
  Also supports the existing standalone UI workflow when explicitly selected.
  NOT for owning general application delivery; use spatial-app-dev-workflow as the
  development backbone. NOT for SDK migration or performance profiling.
license: 'Apache-2.0'
---

# Spatial UI Design, Implementation and Verification

> 🔴 **Mandatory reading** (progressive; read at the stage that needs it):
>
> 1. `workflow.json` — only when executing the standalone UI flow: its ordered orchestration contract, not a global app-entry router.
> 2. `references/spatial-ui-components.md` — before writing any Compose: the maintained component inventory. Verify unlisted APIs against the target SDK; absence from this inventory does not prove absence from the SDK.
> 3. `references/restoration-anti-patterns.md` — before restoring any accepted design into Compose.
> 4. `references/spatialui-web-to-compose.md` — after the designer gate for `intent_only`: `sui-*` → Compose mapping.
> 5. `references/spatial-windows-guide.md` — window-level components, Subwindow, and the floating-layer family.
> 6. `references/architecture-conventions.md` — before writing Kotlin: layered packages + ViewModel/UseCase/Repository + unit-test floor.
> 7. `../spatial-ui-ability/SKILL.md` — before implementing a required SpatialUI capability.
> 8. `../spatial-ui-design-style/SKILL.md` — before writing Compose UI: PicoTheme / tokens / hover / haptics.
> 9. `../pico-spatial-app-designer/design/design-reference/assets/icons/README.md` — when an explicit icon is required.
> 10. `references/icon-drawing.md` — when no authoritative or bundled icon accurately matches.

Generate code directly from the accepted design source. On the Designer route,
`design-spec.json` is the existing executable design IR and the primary input
for Compose generation; do not create a second intermediate layout format or
reverse-engineer structure from `preview.html`. The final container is recorded
in `AndroidManifest.xml`, the implementation structure is Kotlin, and
verification reads both back.

Use this skill for the UI portion of the current task. For complete app development,
read `spatial-app-dev-workflow` and keep its scope, app implementation coordination
and delivery requirements. A caller may load this skill for one stage without
executing the other stages. Direct entry for a UI task is valid; return the scoped
result to the caller and continue broader development under dev guidance.

## Stage-specific guidance

| Current assignment | Read / do                                                                                                   | Return                                                                          |
| ------------------ | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Design             | Input extraction and structure decisions below; `pico-spatial-app-designer` when a design package is needed | Accepted decisions, Preview/Spec and actual visual assets, with gaps identified |
| Implementation     | The accepted source, restoration/Compose references, `spatial-ui-ability` and `spatial-ui-design-style`     | Assigned code changes, asset references and implementation checks               |
| Verification       | Applicable fidelity/style/runtime checks and their references                                               | Evidence for the current build/design, failures and unverified effects          |

Do not replay an already completed design or scaffold step merely because this
skill was loaded. Apply only checks whose prerequisites and scope match the
assignment. The full legacy receipt/build aggregator validates a standalone UI
flow; do not manufacture its receipts for a scoped dev task. Device operations
remain with `pico-emulator-usage`, coordinated by the current app owner.

## When to Use

- Interpret UI design sources, including Figma, screenshot, PRD and accepted design packages.
- Design or implement visible controls, layout, Entity/panel relationships and window models within a development task.
- Review visual fidelity or perform a bounded UI patch using the current app's acceptance criteria.
- Continue an existing standalone UI Workflow Run or execute that flow when explicitly selected.

## Managed Workflow compatibility

Reading this skill or classifying an input as `intent_only` does not start a Run.
For an explicitly selected standalone UI workflow or an existing Run, load
[Standalone UI execution](references/standalone-workflow.md) and `workflow.json`.
The retained flow includes application writing and runtime verification; do not
start it inside dev's design stage as if it were a design-only child. Separate
worktrees do not isolate a shared installed package or device.

The following stage procedures preserve the standalone flow. A scoped caller uses
only the relevant professional guidance; an existing managed Run follows its actual
Handoff instructions and schemas without skipping required stages.

## Boundary

| Situation                                                        | Use instead                        |
| ---------------------------------------------------------------- | ---------------------------------- |
| Upgrade SDK / migrate deprecated APIs                            | `spatial-sdk-update`               |
| Generic empty-dir quickstart / scaffold-only first runnable demo | `spatial-app-onboarding`           |
| Migrate 2D Android app to spatial                                | `porting-android-app`              |
| Performance diagnosis                                            | `spatial-app-performance-workflow` |
| 3D bbox / placement planning                                     | `spatial-sdk-scene-builder`        |

## Routing Position

`spatial-app-dev-workflow` is the recommended backbone for complete application
development, including UI-heavy changes. This skill supplies UI-specific knowledge
and returns decisions, artifacts, implementation changes when assigned, and
verification evidence to its caller. It does not claim the entire task because a
visible control, Entity, layout or window changes. An isolated UI deliverable may
finish here; broader development continues with dev guidance.

### Preview-first design packages

For `write-spec-draft-1`, follow [Preview-first restoration](references/preview-first-restoration.md). It owns the new field, Editor timing, surface, icon and receipt conventions where legacy instructions below conflict. Existing scaffold and machine validation remain mandatory.

### Editor-authored content gate

When the accepted design requires editor-authored content, activate
`spatial-editor` for that portion before implementing app-owned behavior. Follow
[3D execution choice](../spatial-editor/references/3d-execution.md). Use verified
outputs from direct authoring when those fulfill the accepted design and handoff.
For a managed handoff, call `start_editor_workflow` and let the public Workflow
Service plus Editor Domain Drivers establish readiness. Do not call a dynamic
backend readiness tool as a preflight for a managed Run.

Resume this workflow after the Editor handoff returns co-located `.bundle` and
`.scenes.json` outputs when packaging is required, verified authored content
when it is not, or a structured blocker with the repair attempted and its impact.
Do not silently replace editor-authored content with Kotlin primitives.

## Input type → what to extract

Classify once, then extract the facts in this row. Different inputs justify
different extraction tactics; they all converge on the same decisions.

| input_mode          | Trigger                                                                                        | Extract                                                                                                                                                                                                               | Special handling                                                                                                                                                                                                           |
| ------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `visual_design`     | a Figma URL                                                                                    | frame hierarchy, regions, repeated structures, visible states, window-level candidates (TabBar / Toolbar / Subwindow / modal), design tokens, typography roles, assets and icons, spatial cues                        | Read "Figma inputs" below **first** — the route needs an external MCP this plugin does not ship. Fetch fails but a preview/screenshot exists → re-classify as `visual_reference` and say so. No visual fallback → BLOCKED. |
| `visual_reference`  | screenshot / mockup / UI photo                                                                 | the above, plus: **app-owned bbox** (window size derives from this, _not_ the whole screenshot), panel padding, measured region rects, repeated item sizes and gaps, sidebar / search / chips / tabs / card semantics | Read `references/layout-inference.md` first. Never treat passthrough, skybox, floor, scenery, or system safety lines as app content.                                                                                       |
| `product_doc`       | PRD / feature spec                                                                             | user tasks, page inventory, data entities, states and transitions, explicit non-goals                                                                                                                                 | No visual asset and no user-provided design package → **designer gate** first (below).                                                                                                                                     |
| `intent_only`       | one-line ask                                                                                   | app-type candidates, the single core task, implied page count                                                                                                                                                         | No visual asset and no user-provided design package → **designer gate** first (below). "Implement directly" does not skip it.                                                                                              |
| `hybrid`            | more than one of the above                                                                     | per-source facts plus the conflicts between them                                                                                                                                                                      | Resolve to one interpretation via the conflict priority below; never keep parallel truths. Contains Figma → Figma steps. No visual asset at all → designer gate.                                                           |
| `incremental_patch` | user names a file/panel/module, scope ≤ 1–2 regions, root container and window model unchanged | target files, inherited container and window model, regions touched, components and states to add, non-goals                                                                                                          | **Skip the Decide stage** (inherit). Verify with `--profile patch`.                                                                                                                                                        |

Routing tie-breakers:

| User says                                               | Routing             |
| ------------------------------------------------------- | ------------------- |
| "add a search field to `MainPanel.kt` in `myapp`"       | `incremental_patch` |
| "use this Figma to redesign `myapp`'s home page"        | `visual_design`     |
| "use this Figma to add a close button to `DetailPanel`" | `incremental_patch` |

If a patch turns out to require a container or window-model change, stop the
patch path and escalate to the full flow — do not silently rewrite a non-goal.

## Component rules (HARD)

Prefer SpatialUI component defaults for selection states (C0). `Button` is for a concise command (C1). Apply C0–C9 from [references/component-rules.md](references/component-rules.md) during Build.

## Reference index → [references/reference-index.md](references/reference-index.md)

## Flow

| #   | Stage   | Integrated work                                                                                                                   | Gate                                        |
| --- | ------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| 1   | Route   | input/generation mode, target, Figma prerequisite, intent-only feature brief, conditional `pico-spatial-app-designer` subworkflow | inputs explicit; required brief/design pass |
| 2   | Extract | accepted design facts, unknowns, conflicts, assumptions, JSON → Compose inventory                                                 | enough evidence to choose a container       |
| 3   | Decide  | container + window model, with rejected alternatives                                                                              | legality + singularity                      |
| 4   | Build   | on-demand `spatial-ui-ability` resolution, mandatory `spatial-ui-design-style` admission, then Kotlin/Compose/code                | all required APIs and rules resolved        |
| 5   | Verify  | design-style verifier + machine gates + Figma hooks + structural self-review                                                      | all gates green                             |

`incremental_patch` skips stage 3 and inherits the existing container and window
model. The detailed phase order and conditional rules live in `workflow.json`;
this document expands how to execute each phase.

## Operating protocol

- **Sequential and gated.** Do not proceed past a failed gate. On failure: fix the problem, apply a conservative default and state it, or ask the user only when the unresolved issue materially changes the architecture.
- **Conflict priority** (for `hybrid` and any contradictory evidence): explicit user requirement > existing module architecture > professional design deliverable > visual reference > product-doc hints > conservative default. Pick one interpretation and say why; never carry two parallel truths.
- **Conservative fallback:** `ON_PLAIN`, `single_panel`, panel-local overlay, no spatial features. Defaults are allowed; silent invention is not.
- **Output language.** Match the user's language for prose; keep enum values, command names, and `Step Output` labels in English.
- **State assumptions in the conversation.** Every architecture-impacting default must be visible in your Step Output and in the final handoff — that is what replaces the old assumption-ledger file.
- **Step Output** (stages 1, 3, 5):

  ```text
  Step Output
  - Decision: <what was decided>
  - Summary: <1-3 lines>
  - Key facts: <bullets>
  - Reflection: <citation — a concrete observed fact, or a legality-table row / rule number>
  - Gate result: PASS | BLOCKED
  - Next action: proceed | revise | conservative default | ask user
  ```

---

## Stage 1 — Route

### 1a. Classify the input

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

**No-visual classification rule (HARD).** A request that describes any feature,
page, or business flow but carries **no** Figma/screenshot/mockup **and** no
user-provided design package or structured design spec is classified as
`product_doc` (when the description is substantial) or `intent_only` (when it is
short). Both classes fire the designer gate (1c). This is decided only by
whether the user already provided an executable design — never by application
complexity, whether the prompt says "implement directly", or whether it contains
a "design" keyword. "Complete the implementation directly" on a feature-bearing,
no-visual request is still `intent_only`/`product_doc`, not a reason to skip the
gate.

Also decide `generation_mode` (`existing_module` / `new_project`).

Resolve application identity once:

- `existing_module` → preserve the module's current `applicationId`.
- `new_project` with an explicit user value → preserve it unchanged. A
  `com.pico.*` or `com.picoxr.*` value is allowed only on this explicit path;
  warn that PICO system account behavior may apply.
- `new_project` without a user value → generate and persist
  `com.example.<app-slug>.p<8-lowercase-hex-characters>`. Reuse the persisted
  value on retries and later work; never generate a PICO-prefixed package.

**Gate:** input mode, generation mode, and target/output path are all explicit.

### 1b. Figma inputs (external MCP prerequisite)

**This plugin does not provision the Figma capability.** `.mcp.json` declares
only `pico-dev-knowledge` and `pico-spatial-editor`. The `d2c_*` tools below come
from the separate `codin-d2c-figma-to-code` MCP server, which the user installs
in their own host configuration. Treat it as an **external prerequisite**, not as
something the plugin guarantees.

Before extracting anything from a Figma URL, check the live tool list for:

| Tool                 | Used for                                                  | When              |
| -------------------- | --------------------------------------------------------- | ----------------- |
| `d2c_get_figma_data` | fetch the node XML + preview into a temp directory        | Stage 2 (Extract) |
| `d2c_download_icons` | export assets when the XML contains `<Icon download-url>` | Stage 4 (Build)   |
| `d2c_verify_code`    | independent fidelity review of the generated code         | Stage 5b (Verify) |
| `d2c_cleanup_temp`   | remove the temp fetch directory                           | Stage 5b (Verify) |

If the tools are absent, do **not** silently continue as if the Figma route ran:

| Situation                                                                                            | Route                                                                                                                       |
| ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `d2c_*` tools available                                                                              | Proceed on `visual_design`; the Stage 5b hooks are mandatory.                                                               |
| Tools unavailable, but the user supplied a screenshot / mockup / exported preview of the same design | Re-classify as `visual_reference`, say so explicitly, and continue. Stage 5b hooks do not apply.                            |
| Tools unavailable and no visual fallback exists                                                      | **BLOCKED.** State that the Figma route needs the `codin-d2c-figma-to-code` MCP server, and ask for it or for a screenshot. |

Record the resolution in the Stage 1 Step Output. A `visual_design` run whose
`figma_hooks_result.json` is missing because the tools were never available is a
`visual_reference` run that was mislabeled — fix the label, not the checklist.

### 1c. Managed `feature_definition` Handoff (one-line inputs only)

For `input_mode=intent_only`, intent normalization is part of the registered
public Workflow, not a Skill-side preparation step. Start the Workflow with the
unchanged intent, target, and `generationMode`; its first `feature_definition`
caller-agent Handoff produces `<target>/.scratch/intent-brief.md` and returns
the receipt consumed by the `design` module.

The Handoff preserves complete requirements and adds only the smallest missing
goal, capability, or flow details as explicit assumptions. Its prompt and
Output Schema are the execution contract. This section only describes that
Workflow behavior; do not generate the brief directly from this Skill.

### 1d. Designer gate (no-visual inputs only)

**Triggers when** `input_mode ∈ {intent_only, product_doc}`, or `hybrid` with no
Figma URL and no screenshot/mockup. When any visual asset exists, this gate does
not fire — continue straight to stage 2.

**Sole trigger criterion.** The gate fires whenever there is **no visual asset
AND no user-provided executable design package**. "Already provided an executable
design" means the **user** supplied, with the request, either a visual asset
(Figma/screenshot/mockup) or an explicit design package / structured design spec
(at least information architecture + page structure + state model). An agent's
own short plan, a self-authored outline, or "I'll plan the IA myself" does **not**
count as a user-provided design and does **not** let you bypass the gate. Do not
gate on application complexity, design depth, or the presence of a "design"
keyword — only on whether the user already provided an executable design.

Before skipping the Designer for a user-provided package, confirm that it was
supplied with the request and contains information architecture, page
structure, and a state model. Stage its executable JSON at
`<target>/.scratch/design-spec.json` and record the route result as
`user_package_passed`. If any required part is absent, do not use that result;
the Designer gate remains required.

For the managed `intent_only` route, the Workflow's `design` Handoff invokes
`pico-spatial-app-designer` after the `feature_definition` output is accepted.
Follow that Handoff rather than invoking a parallel or nested app-generation
workflow.

For the declarative `product_doc` and no-visual `hybrid` routes, stop app
generation and invoke `pico-spatial-app-designer` as the mandatory design
subworkflow of this unified workflow. In every no-visual route, the design pass
must complete before extraction or code generation. Wait until `design-doc.md` is complete,
Preview has passed Critique, Write Spec has produced a valid `design-spec.json`,
referenced resources resolve or are explicitly pending 3D creation, and Consistency Review
has passed for the current package. Then write
`<target>/.scratch/design_escalation_receipt.json`:

Set `input_mode` to the current run's declared mode. Do not copy an
`intent_only` receipt into `product_doc` or no-visual `hybrid` runs.

```json
{
  "schema_version": 1,
  "phase": "designer_gate",
  "input_mode": "intent_only",
  "visual_asset_present": false,
  "gate_required": true,
  "status": "designer_passed",
  "pre_gates": {
    "designDocComplete": true,
    "designSpecValid": true,
    "previewMatchesSpec": true,
    "critiqueVerdict": "pass",
    "consistencyReviewVerdict": "pass"
  }
}
```

Valid `product_doc` receipt:

```json
{
  "schema_version": 1,
  "phase": "designer_gate",
  "input_mode": "product_doc",
  "visual_asset_present": false,
  "gate_required": true,
  "status": "designer_passed",
  "pre_gates": {
    "designDocComplete": true,
    "designSpecValid": true,
    "previewMatchesSpec": true,
    "critiqueVerdict": "pass",
    "consistencyReviewVerdict": "pass"
  }
}
```

Valid no-visual `hybrid` receipt:

```json
{
  "schema_version": 1,
  "phase": "designer_gate",
  "input_mode": "hybrid",
  "visual_asset_present": false,
  "gate_required": true,
  "status": "designer_passed",
  "pre_gates": {
    "designDocComplete": true,
    "designSpecValid": true,
    "previewMatchesSpec": true,
    "critiqueVerdict": "pass",
    "consistencyReviewVerdict": "pass"
  }
}
```

Then extract from the design package per `references/design-package-bridge.md`.

For `intent_only`, this gate has a second mandatory output before Stage 2 can
pass: read every `kind: "spatialui"` node in `design-spec.json`, then build an
in-memory conversion inventory using
`references/preview-first-restoration.md` and the selected new component README. Every declared `sui-*` component must
resolve to its production Compose API, state/callback binding, and page-level or
window-level hierarchy. A mapped component cannot become custom `Box`/`Row` UI.

**BLOCKED** if `pico-spatial-app-designer` is unavailable, the user declines the
design pass, any pre-gate fails, or a declared `sui-*` component cannot be
resolved. Do not continue with shallow text extraction or custom fallback —
`status=fallback_accepted` is rejected by the verifier.

### Stage 2 — Extract

Work from the "Input type → what to extract" table. Extract **facts first**;
never jump from raw input to Kotlin.

For `visual_design`, fetch the design first with `d2c_get_figma_data` (the stage
1b prerequisite): it writes the node XML and preview into a temp directory that
every later step reads — the token/geometry facts below, the asset downloads in
stage 4, and the `d2c_verify_code` comparison in stage 5b. Keep that directory
until stage 5b's cleanup.

Separate visual evidence by responsibility before deciding anything:

- app-owned window, window ornaments, page content, temporary floating layers, and spatial environment context are different things
- passthrough / skybox / floor / scenery / system safety lines are **not** app content unless the facts prove the app owns them
- edge-pinned long-lived rails / tabs / toolbars are window ornaments (`TabBar` / `Toolbar` / `Subwindow`), not ordinary page layout children; Compose declaration nesting does not change their attachment semantics. Not being `multi_window` does not make something page content.
- derive window size from the app-owned bbox, not the full screenshot
- for `intent_only`, read surfaces, hierarchy, component props, bindings,
  initial state, states, transitions, local actions, data cases, responsive
  rules, assets, and tokens directly from `design-spec.json`; preserve every
  `kind: "spatialui"` node through the JSON → Compose conversion inventory
- use `preview.html` only as visual acceptance evidence. Never infer a
  conflicting size, color, component, or state from its DOM/CSS; repair a
  package mismatch before continuing
- inventory every app-owned visual token before coding: surface/fill, primary
  and secondary text, divider/border, semantic state, and custom
  brand/decorative colors, plus every corner radius. Do not reduce this list to
  the primary palette. Convert CSS `rgba(...)` colors to `#AARRGGBB`; exclude
  environment simulation colors only when the design package explicitly says
  they are not app-owned.

Record unknowns and conflicts explicitly rather than resolving them silently.

**Gate:** enough evidence to propose one container and compare at least one
alternative window model.

### Stage 3 — Decide (skipped for `incremental_patch`)

Read `references/structure-decisions.md`. If the design needs `anchor` or
`env_mesh`, also read `references/spatial-anchor.md` and settle legality now.

Choose **one** container (`ON_PLAIN`, `IN_VOLUME`, `STAGE_MIXED`,
`STAGE_PROGRESSIVE`, `STAGE_FULL`) and **one** window model (`single_panel`,
`single_panel_with_popup`, `sidebar_content`, `master_detail`,
`window_plus_subwindow`, `multi_window`).

For each, record the chosen value, the reason, and the rejected nearest and most
distant alternatives. Record exactly one nearest and one most-distant rejected
alternative — do not enumerate further options. Decide is a bounded pass: once
each dimension has a chosen value with a fact-cited reason, move to Build. Re-open
Decide only to resolve a concrete downstream failure (new evidence), never to add
confidence to an already-settled decision.

**Reflection (HARD):** every rejection reason must cite a concrete observed fact,
a row of the legality table, or a numbered escalation rule. "not needed" / "not
applicable" / "no evidence" is a BLOCK. Apply legality inline — never defer it to
stage 5.

> `multi_window` cannot be proven from code by any machine check. Escalate to it
> only with concrete independent-launcher / lifecycle / placement-memory
> evidence; otherwise the answer is `Subwindow`.

Strategy names and schema examples are choices, not preferences. Select an
Editor-backed content strategy only when the current evidence or an accepted upstream
handoff requires Editor-authored content. Its presence among the available strategies
does not justify adding unrequested 3D content.

### Stage 4 — Build

Module mode, entry chain, and Android Studio sync in [references/build-module-mode.md](references/build-module-mode.md).

#### UI rules

Derive the required SpatialUI capability domains from the direct request or
accepted upstream design facts. Read `../spatial-ui-ability/SKILL.md`, then load
one matching `references/ability-*.md` for each required capability domain.
Do not preload unrelated references. Apply the **component rules C0–C9** — this
is where they bind. Full Build UI rules, architecture conventions, and
typography/spacing contract in [references/ui-rules.md](references/ui-rules.md).

### Stage 5 — Verify

Run `validate_workflow_and_build.sh <target>` with `--design-gate-result user_package_passed` when applicable. Full verification stages 5a–5d in [references/verification-details.md](references/verification-details.md).

---

## Exit checklist

Complete only when ALL 14 criteria hold → [references/exit-checklist.md](references/exit-checklist.md).

## Pitfalls → [references/pitfalls.md](references/pitfalls.md)

## Restoration conventions → [references/restoration-conventions.md](references/restoration-conventions.md)
