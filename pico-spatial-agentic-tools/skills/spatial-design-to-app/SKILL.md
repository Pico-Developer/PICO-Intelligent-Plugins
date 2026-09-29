---
name: spatial-design-to-app
description: Use when creating a product-specific PICO Spatial Android/Kotlin app, or when an existing-app change adds/removes visible controls or alters product layout, visual design/fidelity, panel hierarchy, or the container/window model. For behavior-only existing-app changes that preserve visible UI and spatial structure use spatial-app-dev-workflow; for generic empty-dir quickstarts use spatial-app-onboarding. NOT for SDK upgrades, legacy Android porting, pure code review/refactor, old-baseline D2C A/B evaluation, or performance diagnosis.
license: 'Apache-2.0'
---

# Product-Specific Source → PICO Spatial Android App

> 🔴 **Mandatory reading** (progressive; read at the stage that needs it):
>
> 1. `workflow.json` — before routing: the authoritative unified orchestration
>    contract, including the one-line Designer gate and integrated UI stages.
> 2. `references/spatial-ui-components.md` — before writing any Compose: the component whitelist. Names outside it do not exist.
> 3. `references/restoration-anti-patterns.md` — before restoring any accepted
>    design into Compose: implementation patterns that preserve visual bounds.
> 4. `references/spatialui-web-to-compose.md` — after the designer gate for
>    `intent_only`: the complete `sui-*` → production Compose mapping.
> 5. `references/spatial-windows-guide.md` — window-level components, Subwindow, and the floating-layer family.
> 6. `references/architecture-conventions.md` — before writing Kotlin: layered packages + ViewModel/UseCase/Repository + unit-test floor.
> 7. `../spatial-ui-ability/SKILL.md` — before implementing a required SpatialUI
>    capability: route to only the matching ability reference(s).
> 8. `../spatial-ui-design-style/SKILL.md` — before writing Compose UI: PicoTheme / tokens / hover / haptics. A generation-time contract, not a final lint.
> 9. `../pico-spatial-app-designer/references/icon-selection.md` — when an
>    explicit icon is required: source priority and bundled ICON 7.0 lookup.
> 10. `references/icon-drawing.md` — when no authoritative, SDK, or bundled icon
>     accurately matches, or when an icon needs a material repair.

Generate code directly from the accepted design source. On the Designer route,
`design-spec.json` is the existing executable design IR and the primary input
for Compose generation; do not create a second intermediate layout format or
reverse-engineer structure from `preview.html`. The final container is recorded
in `AndroidManifest.xml`, the implementation structure is Kotlin, and
verification reads both back.

`workflow.json` makes this one app-generation workflow. It conditionally invokes
`pico-spatial-app-designer`, resolves implementation capabilities through
`spatial-ui-ability`, and applies `spatial-ui-design-style` as a mandatory
build/verification contract. Do not activate those three as parallel
app-generation workflows.

## Managed Workflow entry

For a short `intent_only` request, run the registered public
`spatial-design-to-app` Workflow instead of manually advancing this document's
stages. Start it with the user's unchanged intent, a workspace-relative target,
`generationMode`, and the user's `applicationId` when one was explicitly
provided. Complete each `caller-agent` Handoff using its supplied instructions
and Output Schema, then resume the same public Run.

The managed route owns the bounded sequence
`feature_definition -> design -> design_review -> compose_app -> compose_review`.
Its first `feature_definition` caller-agent Handoff owns intent normalization
and creation of `<target>/.scratch/intent-brief.md`. Do not create or overwrite
that artifact from the Skill entry path; follow the Handoff instructions and
Output Schema, then resume the same Run.
Do not start a nested `spatial-design-to-app` Workflow from its `compose-app`
Handoff; use the implementation and validator sections below as that task's
contract. A recoverable SDK, device, network, authentication, or permission
problem leaves the Handoff unanswered and the Run in `waiting`.

Figma, screenshot, long-form PRD, hybrid, and incremental-patch requests still
use the source-specific routing below until those prerequisites are represented
by a maintained Workflow package.

## Boundary

| Situation                                                        | Use instead                        |
| ---------------------------------------------------------------- | ---------------------------------- |
| Upgrade SDK / migrate deprecated APIs                            | `spatial-sdk-update`               |
| Generic empty-dir quickstart / scaffold-only first runnable demo | `spatial-app-onboarding`           |
| Migrate 2D Android app to spatial                                | `porting-android-app`              |
| Performance diagnosis                                            | `spatial-app-performance-analysis` |
| 3D bbox / placement planning                                     | `spatial-sdk-scene-builder`        |

## Routing Position

Primary route when the user wants a product-specific PICO Spatial Android app
from Figma, screenshot/mockup, PRD, intent, hybrid sources, or a bounded
existing-panel patch. This skill owns the evidence, container, and window model;
only the raw scaffold step is delegated to `spatial-app-onboarding`.

For an existing app, use this skill when the change adds or removes visible
controls or alters layout, visual fidelity, panel hierarchy, or the
container/window model. Route behavior-only changes that preserve those facts
to `spatial-app-dev-workflow`; naming a file or panel alone does not select this
skill.

Do not use this skill for a generic empty-directory quickstart whose only goal is
"create a first runnable Spatial project" — route that to
`spatial-app-onboarding`.

### Editor-authored content gate

When the accepted design requires editor-authored scenes, assets, visual
composition, materials, lighting, particles, or effects, activate
`spatial-editor` for that portion before implementing app-owned behavior. Call
`start_editor_workflow` and let the public Workflow Service plus Editor Domain
Drivers establish readiness; do not call a dynamic backend readiness tool as a
preflight. An initial lifecycle status does not prove unavailability. Follow one
structured public Run recovery state before degrading to an App/ECS fallback.

Resume this workflow only after the Editor handoff returns co-located `.bundle`
and `.scenes.json` outputs, a supported authored-content result that does not
need packaging, or a structured failure record containing the readiness error,
recovery attempted, degraded scope, and user-visible impact. Never silently
replace editor-authored content with Kotlin primitives.

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

Read `references/spatial-ui-components.md` before writing UI; read
`references/spatial-windows-guide.md` when the design has window-level or
floating structure.

- **C0 — Preserve component colors and readable pairs.** Prefer SpatialUI
  component defaults for selection, toggle, and interaction states. When a
  component provides state-aware content color to a slot, leave `Text.color` /
  `Icon.tint` unspecified so the slot inherits it. On an ordinary app-owned
  surface, choose an intentional foreground for the actual background. When
  custom state colors are required, use the component `colors` API when
  available and consider each state's effective foreground and background
  together. Either color may remain unchanged when the resulting pair stays
  readable. Never infer white text or a dark fill merely because a state is
  selected.
- **C1 — Prefer built-ins.** If a whitelisted component matches the semantics, use it. Do not hand-roll an equivalent from `Box` + `Text` + `clickable`. `scan_implementation.py` warns when a UI uses too few SpatialUI built-ins.
- **C2 — Never invent SDK names.** Names outside the whitelist do not exist. When nothing fits, emit `Box` with `// TODO(missing-component): <description>` rather than inventing `SpatialButton` / `XRPanel`. Invented names are a hard failure.
- **C3 — Edge-pinned chrome is window-level.** Long-lived edge navigation / action strips are `TabBar` / `Toolbar` / `Subwindow` **siblings** of the main panel, not page children. Do not hand-roll `Box(Modifier.align(...))` capsule rows. `TabBar` / `Toolbar` take no `modifier` — the system owns their placement. For a deliberate in-page overlay, mark it `// spatial-ui: intentional-in-page-overlay <reason>`.
- **C4 — Semantics over appearance.** Search box → `SearchField`, not `TextField` + a magnifier icon. Filters/tags → `ButtonChip` / `RemovableChip` / `ToggleableChip`. In-page side nav → `SideNavigation` / `SideNavigationItem`. Segmented switch → `SegmentControl` / `SegmentItem`.
- **C5 — Smallest floating explanation first.** `in-page overlay` → `SpatialPopup` → `Subwindow` → `multi_window`. Short confirmation → `AlertDialog`; heavy modal → `Sheet`; teaching bubble → `CoachmarkBox`; transient feedback → `SnackbarHost` (a host + state pair, not a standalone composable).
- **C6 — No direct Material imports.** `androidx.compose.material3.*` / `material.*` are rejected by the design-style verifier.
- **C7 — Custom interactive components** must follow the design-style hover + haptics rules (`Modifier.spatialHoverEffect`; modifier order `clip → background → spatialHoverEffect → clickable`), or use a built-in that already provides them.
- **C8 — Designer JSON components map to SpatialUI Compose.** For
  `intent_only`, every `kind: "spatialui"` node in `design-spec.json` must be
  converted through `references/spatialui-web-to-compose.md`. Do not reproduce
  a mapped component with Compose primitives. JSON props/events become typed
  state and callbacks; node children become composable content. Use
  `preview.html` only to compare the accepted visual result.
- **C9 — Reuse icons before drawing.** Resolve icon sources in this order:
  user/Figma asset, existing app asset, SDK-owned semantic icon, exact bundled
  ICON 7.0 match, then a newly drawn icon. A catalog miss is not permission to
  choose a merely similar symbol. When a new or materially repaired icon is
  required, follow `references/icon-drawing.md`; preserve the accepted 24 x 24
  SVG geometry in the Android VectorDrawable and render it with theme tint.

## Reference index (read on demand, never preemptively)

| Read when …                                                                                    | File                                                                  |
| ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Extract — decomposing a screenshot/mockup into regions, repeated structures, spacing ownership | `references/layout-inference.md`                                      |
| Route / Extract — no-visual input: designer gate + design-package facts                        | `references/design-package-bridge.md`                                 |
| Decide — container, window model, legality tables, escalation rules                            | `references/structure-decisions.md`                                   |
| Decide — `anchor` / `env_mesh` requested (BLOCK inside a WindowContainer)                      | `references/spatial-anchor.md`                                        |
| Decide / Build — window-level components, Subwindow, floating layers                           | `references/spatial-windows-guide.md`                                 |
| Build — the component whitelist                                                                | `references/spatial-ui-components.md`                                 |
| Build — entry chain + authoritative manifest meta-data values                                  | `references/manifest-and-entry.md`                                    |
| Build — root container is any `STAGE_*`                                                        | `references/stage.md`                                                 |
| Build — layered packages, ViewModel/UseCase, test floor                                        | `references/architecture-conventions.md`                              |
| Build — SpatialUI import lookup                                                                | `references/spatial-api-imports.md`                                   |
| Build — a required SpatialUI capability such as gesture, hover, depth, or Augment              | `../spatial-ui-ability/SKILL.md`, then only its matching reference(s) |
| Build / Verify — mandatory SpatialUI theme, component, interaction, and verifier contract      | `../spatial-ui-design-style/SKILL.md`                                 |
| Extract / Build — `intent_only` design package uses `sui-*` components                         | `references/spatialui-web-to-compose.md`                              |
| Extract / Build — resolve an explicit icon source                                              | `../pico-spatial-app-designer/references/icon-selection.md`           |
| Build — draw or materially repair a custom production UI icon                                  | `references/icon-drawing.md`                                          |
| Build — Figma tokens, visual feature mapping, fidelity contract                                | `references/figma-mapping.md`                                         |
| Build — new-project scaffold handoff (`pico-cli project create`)                               | `references/scaffold-handoff.md`                                      |
| Verify — smoke-build / Gradle sync failures                                                    | `references/build-failures.md`                                        |

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
`design-spec.json` is schema-valid and exactly embedded in `preview.html`,
every declared custom icon SVG exists and is embedded in the preview, and the
§6 Critique verdict is `pass`, then write
`<target>/.scratch/design_escalation_receipt.json`:

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
    "postBuildVerdict": "pass"
  }
}
```

Then extract from the design package per `references/design-package-bridge.md`.

For `intent_only`, this gate has a second mandatory output before Stage 2 can
pass: read every `kind: "spatialui"` node in `design-spec.json`, then build an
in-memory conversion inventory using
`references/spatialui-web-to-compose.md`. Every declared `sui-*` component must
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
- edge-pinned long-lived rails / tabs / toolbars are window ornaments (`TabBar` / `Toolbar` / `Subwindow`), not page children. Not being `multi_window` does not make something page content.
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

#### Module mode

- **Existing module:** keep namespace/package, manifest wiring, and entry chain. Allowed: new Compose files, drawables, strings, state holders. NOT allowed without explicit escalation: switching root container, changing `pico.spatial.windowcontainer.*` meta-data, introducing Stage-only APIs (anchor / ECS / env_mesh) inside a WindowContainer.
- **New project:** the project is created by `pico-cli project create` — never by hand. Delegate the scaffold step to `spatial-app-onboarding`, passing the resolved application ID unchanged and the Decide-stage container as the template (`ON_PLAIN → planar`, `IN_VOLUME → volumetric`, `STAGE_* → stage`). Resume only after it returns `<target>/.scratch/onboarding_handoff.json`. The handoff must be scaffold-only (`product_ui_implemented=false`); if onboarding implemented product UI, treat that as a failure and rebuild the UI here. Then build the requested experience on top of the generated entry point — do not re-scaffold, rewrite `mainApp`, or re-insert manifest meta-data.

> 🔴 **The CLI owns the project skeleton. This skill never hand-assembles one.**
>
> `pico-cli project create` owns the Gradle setup, dependency versions,
> repositories, package layout, `Main.kt` entry chain, and a fully-populated
> `AndroidManifest.xml` with container meta-data already in place. Do **not**
> author `build.gradle.kts`, `settings.gradle.kts`, `libs.versions.toml`, or
> `gradle-wrapper.properties` from scratch or from a remembered template — a
> hand-built skeleton drifts from the CLI baseline and fails in ways nobody can
> reproduce.
>
> What you legitimately do after the CLI runs:
>
> - write product Kotlin/Compose on top of the generated entry point
> - add dependency lines the design genuinely requires (for example the sense dependency when the design needs anchors)
> - for `STAGE_*`, edit the four `pico.spatial.stage.*` values the CLI already emitted so they match the chosen variant — all three variants share `--template stage`, so the CLI cannot know which one you decided on. The value matrix is in `references/manifest-and-entry.md` → "Choosing the Stage variant".
>
> If the project foundation is genuinely broken (unresolvable SDK, toolchain
> mismatch), re-create it with the CLI or hand off to `spatial-sdk-update`. Do
> not repair build foundations here — see `references/build-failures.md`.

Entry chain (created by the CLI; verify rather than rewrite):
`Application.onCreate { launch(::mainApp) }` → `mainApp(scope: SpatialAppScope)` → `DefaultWindowContainer {}` or `DefaultStage {}` → `SpatialLaunchActivity`.

**Android Studio sync is mandatory for new modules.** After a new module is
included, trigger **Sync Project with Gradle Files** before claiming the app runs
from the IDE. If no IDE-sync API is available, run the Gradle discovery proxy in
stage 5 and tell the user sync is still required.

#### UI rules

- Before emitting Compose, derive the required SpatialUI capability domains from
  the direct request or accepted upstream design facts. Read
  `../spatial-ui-ability/SKILL.md`, then load one matching `references/ability-*.md`
  for each required capability domain. Do not preload unrelated references.
  Treat those snippets as integrated implementation resources; do not start a
  separate app-generation workflow.
- Build from the decisions: root container → window ornaments → windows → regions → reusable components.
- For `intent_only`, implement every resolved row from the JSON → Compose
  conversion inventory. `sui-tab-bar`/`sui-toolbar`/`sui-subwindow`/
  `sui-augment` remain root/window ornaments; modal, menu, coachmark, popup, and
  snackbar mappings keep their SpatialUI state/host patterns. Translate JSON
  props, bindings, and events into typed Kotlin state and callbacks; never copy
  Web renderer mechanics into Kotlin.
- Resolve every declared icon before writing its Compose call site. Preserve
  user/Figma, app, and SDK sources. For `icon70://` assets, run the Designer's
  `scripts/icon-catalog.mjs resolve --spec ... --format android --out ...` and
  copy only referenced catalog vectors. For
  `design-assets/icons/<resource-name>.svg`, follow
  `references/icon-drawing.md` and create a matching Android VectorDrawable
  from the approved SVG geometry. Use all resulting resources through
  `painterResource(R.drawable.<resource-name>)` in `Icon` or the mapped icon
  slot; never substitute text, emoji, or an approximate catalog asset.
- **Set the container meta-data in `AndroidManifest.xml` to match the Decide stage.** It is the runtime source of truth and what verification reads back. See `references/manifest-and-entry.md`.
- **Spacing ownership and root fill are explicit.** A root-fill shell is edge-to-edge with insets on inner content; an outer-padding card carries its own margin. Give every gap exactly one owner — do not double-pad or drop the outer margin. See `references/layout-inference.md`.
- Apply the **component rules C0–C9** above. This is where they bind.
- Read `../spatial-ui-design-style/SKILL.md` and satisfy its pre-build admission
  rules before Compose UI. This is a mandatory phase of this workflow, not a
  separate app-generation workflow or a final lint. Preserve the native
  SpatialUI `ColorScheme` unchanged: do not construct or copy it to replace
  `fill*`, `label*`, interaction, status, hover/pressed, or divider roles.
  Custom design colors remain allowed as named app-owned tokens used directly.
  `windowConstraints(...)` is resize bounds, not first-open size.
- Do not add `Text.color` / `Icon.tint` merely to make a component slot's color
  explicit. Preserve component-owned foregrounds by default. For category,
  brand, selection, or toggle customization, check the effective content
  against the effective container in every affected state. In particular,
  avoid dark-on-dark, light-on-light, white on light gray, and white on bright
  category fills. `labelPrimaryLight` is a bright-on-dark role, not a generic
  selected-state foreground. Translucent fills must be judged over their
  underlying surface.
- Do not carry design-review apparatus into the product UI. Viewport presets, data-mode controls, token legends, coverage badges, and implementation notes are omitted unless the source requirement identifies them as real user features.
- Preserve every extracted radius on the bounded content surface that owns it.
  Structural `layout` and `domain_visual` regions remain transparent. For each
  app-authored surface restored from `design-spec.json`, place exactly one
  `// design-style: design-surface <node-id>` immediately before its
  `.background(...)` or content `Card(...)`. Do not add app-authored
  `.backgroundMaterial(...)`, borders, or `BorderStroke` to content containers.
- Keep business UI 2D unless the design justifies 3D; Stage-only APIs stay out of WindowContainer flows.
- For a `STAGE_*` root: host 3D via `SpatialView` + ECS entities (`Entity()` / `Entity.load(...)` + `content.addEntity(...)`) and attach 2D controls with `AttachmentPanel(id){}` positioned in meters on an ECS anchor. Never a flat `Box`/`Column`/`Canvas` page, never a bare Compose overlay. See `references/stage.md`.

#### Architecture rules (HARD)

Read `references/architecture-conventions.md` before writing code. The checker
enforces layered packages, a thin `Main.kt`, MVI-lite state, repository
boundaries, mandatory ViewModel tests, and UseCase + tests when the screen has
non-trivial business rules, filtering, sorting, selection, or transformation.

### Stage 5 — Verify

#### 5a. Machine gates

When `design-spec.json` exists, write
`.scratch/design_implementation_map.json` before running the command. Follow
`references/design-package-bridge.md` §E: record the current design file hash,
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

When `design-spec.json` exists, design-style admission also scans actual Kotlin
for app-authored surfaces. Every `.background(...)` or content `Card(...)` must
carry a valid `design-style: design-surface <node-id>` marker whose node declares
a fill, and one node ID may mark at most one background call. Any
`.backgroundMaterial(...)`, `.border(...)`, or `BorderStroke(...)` in app
source is a hard failure. This negative scan prevents extra decoration from
being hidden by an otherwise correct implementation receipt.

Do NOT paraphrase JSON results — read `design_fidelity_result.json.passed`,
`passed` / `failures_or_explicit_none` / `warnings_or_explicit_none` literally.
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
- in `existing_module` mode, module resources reused before adding new ones
- every icon follows the declared source priority; bundled icons match their
  catalog vector, and custom drawables preserve the accepted SVG geometry,
  transparent cutouts, 24 x 24 viewport, semantic tint, and accessibility text

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

---

## Exit checklist

Complete only when ALL hold:

1. `validate_workflow_and_build.sh <target>` exits 0 **and** `verification_summary.json.clean == true`. Only Gradle sync / runtime launch may be environment-degraded, and a degraded run is not complete unless explicitly accepted in the handoff.
2. For new modules, Android Studio **Sync Project with Gradle Files** has been triggered, or the handoff states the user must run it before the first IDE run.
3. `implementation_scan_result.json`, `gradle_sync_result.json`, `architecture_check_result.json`, `unit_tests_result.json` all → `"passed": true`.
4. When `design-spec.json` exists,
   `design_fidelity_result.json.passed == true`, its SHA-256 matches the
   authoritative design file, and `mapped_refs == required_refs`. When no
   design JSON exists, it records `applicable=false` and the handoff does not
   claim JSON fidelity.
5. `design_style_result.json.passed == true` with 0 errors and no skip/degraded bypass. When the design declares custom colors, they were passed via `--design-color`; the verifier proved exact value coverage and that the native SpatialUI `ColorScheme` was not overridden.
6. For `generation_mode=new_project`, `.scratch/onboarding_handoff.json` records `scaffold_only=true`, `product_ui_implemented=false`, `build_passed=true`, `resume_skill=spatial-design-to-app`.
7. For `intent_only`, `.scratch/intent-brief.md` exists and is non-empty.
8. For no-visual inputs, the matching design gate passed: a Designer-produced
   package has `.scratch/design_escalation_receipt.json` with
   `status=designer_passed`, `designSpecValid=true`, and
   `previewMatchesSpec=true`; a user-provided package was accepted during
   routing and verification ran with
   `--design-gate-result user_package_passed`.
9. For `intent_only`, every `kind: "spatialui"` node in
   `design-spec.json` maps to and is implemented with its corresponding
   SpatialUI Compose API.
10. For `visual_design` runs that used the `codin-d2c-figma-to-code` tools, `figma_hooks_result.json` shows verify then cleanup, each exactly once. When those tools were unavailable, the run was re-routed per stage 1b (`visual_reference`, or BLOCKED) and the handoff says so — an unavailable prerequisite is never a silently skipped gate.
11. SpatialUI component slots inherit component-owned content colors by
    default; every custom state color choice has a readable effective
    foreground/background pair without a duplicate child-slot override.
12. Every declared icon resolves to a real asset; catalog-backed icons pass
    `icon-catalog.mjs verify`, and custom SVG icons have matching 24 x 24
    VectorDrawables.
13. No pitfall below was triggered.
14. No app-authored content border or material exists, and every app-authored
    Kotlin surface is traceable to a fill-owning design node.

Final handoff:

```text
- Container: <chosen + why>
- Window model: <chosen + why>
- Mode: <existing module update | new scaffold | incremental_patch>
- Path: <module path | output path>
- Designer gate: <passed | blocked | not_required>
- Figma MCP: <hooks_run | unavailable_rerouted_to_visual_reference | not_applicable>
- Android Studio sync: <done | user must run Sync Project with Gradle Files>
- Assumptions: <explicit list or 'none'>
- Remaining inferred/mock parts: <list>
- Verification: <verification_summary.json result, including every warning and skip>
```

## Pitfalls (do not)

- skip workspace inspection when the user names a module (default to `existing_module`)
- **hand-assemble a project skeleton** — `build.gradle.kts` / `settings.gradle.kts` / `libs.versions.toml` / the wrapper / the base manifest all belong to `pico-cli project create`; authoring them from a template is how a project silently drifts off the CLI baseline
- **repair a broken build foundation by editing Gradle files from memory** — re-create with the CLI or hand off to `spatial-sdk-update`
- jump straight from input to code without extracting facts first
- **silently switch the root container in an existing module** — a container change re-runs the Decide stage, then updates manifest, `Main.kt`, coordinates, ornaments, and runtime launch together
- **invent `multi_window` without disconnected-surface evidence** — no machine gate can catch this
- **use a Stage-only API from a WindowContainer flow**
- **hide architecture-impacting assumptions instead of stating them**
- defer container × feature legality to stage 5 (decide inline in stage 3)
- confuse an overlay with a window — popup menus stay in one panel
- leave root fill implicit or record spacing without an owner
- emit a `STAGE_*` root as a flat Compose page (`Box`/`Column`/`Canvas`), or drop immersive content into a 2D WindowContainer tree
- treat a `DefaultWindowContainer` + secondary `Stage(id=…)` app as a "mixed root" — that is a valid single-root app; only two coexisting _default_ roots are illegal
- carry `TabBar`/`Toolbar`/`Subwindow` into a Stage, or `AttachmentPanel` into a window
- migrate a container to fix a compile or visual symptom
- invent SDK names; only the whitelist
- **present the Figma route as executable without checking the `d2c_*` tools first** — the plugin does not provision them; an absent prerequisite means re-route or BLOCKED, never a quietly dropped verify hook
- flatten a mapped `sui-*` component into hand-built Compose primitives during
  `intent_only` conversion
- copy design facts into `design_implementation_map.json` without inspecting the
  finished source; source mappings and evidence must point at the code that
  implements each fact
- over-spatialize a 2D settings UI (most belong in `ON_PLAIN`)
- implement screenshot passthrough, floor/trees/skybox, or system safety lines as app content
- fill Step Output with mechanical PASS — Reflection must cite a real fact or rule
- run the full flow on a small patch; use `incremental_patch`
- emit code before reading `architecture-conventions.md` and `spatial-ui-design-style/SKILL.md`

**Honesty:** A 2D reference under-specifies a spatial app. State explicitly when
passthrough / depth / hover / haptics / gestures were inferred, and flag that
anchors and Full Space behaviors need a device to validate.

**Clarification:** ask the user only when one of these is truly unresolved — no
visual reference is available, target module / output cannot be inferred,
multiple window interpretations are equally plausible and materially change the
app structure, or a package / namespace conflict cannot be resolved safely.
Otherwise proceed with the safest default and state the assumption.
