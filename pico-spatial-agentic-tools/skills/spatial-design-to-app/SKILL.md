---
name: spatial-design-to-app
description: Use when creating or materially updating a product-specific PICO Spatial Android/Kotlin app from Figma, screenshot/mockup, PRD, intent, hybrid sources, or a bounded panel patch, and the task requires container, window model, panel hierarchy, implementation, and verification. For generic empty-dir quickstarts use spatial-app-onboarding. NOT for SDK upgrades, legacy Android porting, pure code review/refactor, old-baseline D2C A/B evaluation, or performance diagnosis.
license: 'Apache-2.0'
---

# Product-Specific Source → PICO Spatial Android App

> 🔴 **Mandatory reading** (progressive; read at the stage that needs it):
>
> 1. `references/spatial-ui-components.md` — before writing any Compose: the component whitelist. Names outside it do not exist.
> 2. `references/spatialui-web-to-compose.md` — after the designer gate for
>    `intent_only`: the complete `sui-*` → production Compose mapping.
> 3. `references/spatial-windows-guide.md` — window-level components, Subwindow, and the floating-layer family.
> 4. `references/architecture-conventions.md` — before writing Kotlin: layered packages + ViewModel/UseCase/Repository + unit-test floor.
> 5. `../spatial-ui-design-style/SKILL.md` — before writing Compose UI: PicoTheme / tokens / hover / haptics. A generation-time contract, not a final lint.

Generate code directly from the design. This skill does **not** produce
intermediate layout JSON — the container is recorded in `AndroidManifest.xml`,
the structure is the Kotlin you write, and verification reads both back.

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

Do not use this skill for a generic empty-directory quickstart whose only goal is
"create a first runnable Spatial project" — route that to
`spatial-app-onboarding`.

### Editor-authored content gate

When the accepted design requires editor-authored scenes, assets, visual
composition, materials, lighting, particles, or effects, activate
`spatial-editor` for that portion before implementing app-owned behavior. Call
`start_editor_workflow` and let the managed Controller establish readiness; do
not call `ensure_editor_ready` as a preflight. An initial lifecycle status does
not prove unavailability. Follow one structured workflow recovery action before
degrading to an App/ECS fallback.

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
| `visual_design`     | a Figma URL                                                                                    | frame hierarchy, regions, repeated structures, visible states, window-level candidates (TabBar / Toolbar / Subwindow / modal), design tokens, typography roles, assets/icons, spatial cues                            | Read "Figma inputs" below **first** — the route needs an external MCP this plugin does not ship. Fetch fails but a preview/screenshot exists → re-classify as `visual_reference` and say so. No visual fallback → BLOCKED. |
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

- **C0 — Resolve text foregrounds.** CSS `color` inheritance does not survive
  conversion to Compose. `PicoTheme` installs the color scheme but does not
  provide `LocalContentColor`. Every app-authored `Text` on an ordinary
  `Box` / `Row` / `Column` surface must pass
  `color = PicoTheme.colorScheme.<label-or-state-role>`. A direct SpatialUI
  component slot may inherit its state-aware content color only when the call
  is marked `// design-style: inherited-content-color <provider>`. Before
  build, audit all dark-surface text and run the design-style R9 verifier.
- **C1 — Prefer built-ins.** If a whitelisted component matches the semantics, use it. Do not hand-roll an equivalent from `Box` + `Text` + `clickable`. `scan_implementation.py` warns when a UI uses too few SpatialUI built-ins.
- **C2 — Never invent SDK names.** Names outside the whitelist do not exist. When nothing fits, emit `Box` with `// TODO(missing-component): <description>` rather than inventing `SpatialButton` / `XRPanel`. Invented names are a hard failure.
- **C3 — Edge-pinned chrome is window-level.** Long-lived edge navigation / action strips are `TabBar` / `Toolbar` / `Subwindow` **siblings** of the main panel, not page children. Do not hand-roll `Box(Modifier.align(...))` capsule rows. `TabBar` / `Toolbar` take no `modifier` — the system owns their placement. For a deliberate in-page overlay, mark it `// spatial-ui: intentional-in-page-overlay <reason>`.
- **C4 — Semantics over appearance.** Search box → `SearchField`, not `TextField` + a magnifier icon. Filters/tags → `ButtonChip` / `RemovableChip` / `ToggleableChip`. In-page side nav → `SideNavigation` / `SideNavigationItem`. Segmented switch → `SegmentControl` / `SegmentItem`.
- **C5 — Smallest floating explanation first.** `in-page overlay` → `SpatialPopup` → `Subwindow` → `multi_window`. Short confirmation → `AlertDialog`; heavy modal → `Sheet`; teaching bubble → `CoachmarkBox`; transient feedback → `SnackbarHost` (a host + state pair, not a standalone composable).
- **C6 — No direct Material imports.** `androidx.compose.material3.*` / `material.*` are rejected by the design-style verifier.
- **C7 — Custom interactive components** must follow the design-style hover + haptics rules (`Modifier.spatialHoverEffect`; modifier order `clip → background/backgroundMaterial → spatialHoverEffect → clickable`), or use a built-in that already provides them.
- **C8 — Designer Web components map to SpatialUI Compose.** For
  `intent_only`, every `sui-*` component used by the passed design package must
  be converted through `references/spatialui-web-to-compose.md`. Do not
  reproduce a mapped component with Compose primitives. Web attributes/events
  become typed state and callbacks; Web slots become composable lambdas.

## Reference index (read on demand, never preemptively)

| Read when …                                                                                    | File                                     |
| ---------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Extract — decomposing a screenshot/mockup into regions, repeated structures, spacing ownership | `references/layout-inference.md`         |
| Route / Extract — no-visual input: designer gate + design-package facts                        | `references/design-package-bridge.md`    |
| Decide — container, window model, legality tables, escalation rules                            | `references/structure-decisions.md`      |
| Decide — `anchor` / `env_mesh` requested (BLOCK inside a WindowContainer)                      | `references/spatial-anchor.md`           |
| Decide / Build — window-level components, Subwindow, floating layers                           | `references/spatial-windows-guide.md`    |
| Build — the component whitelist                                                                | `references/spatial-ui-components.md`    |
| Build — entry chain + authoritative manifest meta-data values                                  | `references/manifest-and-entry.md`       |
| Build — root container is any `STAGE_*`                                                        | `references/stage.md`                    |
| Build — layered packages, ViewModel/UseCase, test floor                                        | `references/architecture-conventions.md` |
| Build — SpatialUI import lookup                                                                | `references/spatial-api-imports.md`      |
| Extract / Build — `intent_only` design package uses `sui-*` components                         | `references/spatialui-web-to-compose.md` |
| Build — Figma tokens, visual feature mapping, fidelity contract                                | `references/figma-mapping.md`            |
| Build — new-project scaffold handoff (`pico-cli project create`)                               | `references/scaffold-handoff.md`         |
| Verify — smoke-build / Gradle sync failures                                                    | `references/build-failures.md`           |

## Flow

| #   | Stage   | Output                                                                                                         | Gate                                  |
| --- | ------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| 1   | Route   | input mode, generation mode, target; Figma MCP availability for Figma URLs; designer gate for no-visual inputs | inputs and target explicit            |
| 2   | Extract | design facts, unknowns, conflicts, assumptions (stated, not filed)                                             | enough evidence to choose a container |
| 3   | Decide  | container + window model, with rejected alternatives                                                           | legality + singularity                |
| 4   | Build   | Kotlin / Compose / manifest                                                                                    | (verified in 5)                       |
| 5   | Verify  | machine gates + Figma hooks + structural self-review                                                           | all gates green                       |

`incremental_patch` skips stage 3 and inherits the existing container and window
model.

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

### 1c. Designer gate (no-visual inputs only)

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

Stop app generation and run `pico-spatial-app-designer` to produce a design
package. Wait until its `design-doc.md` is complete **and** its §6 Critique
verdict is `pass`, then write `<target>/.scratch/design_escalation_receipt.json`:

```json
{
  "schema_version": 1,
  "phase": "designer_gate",
  "input_mode": "intent_only",
  "visual_asset_present": false,
  "gate_required": true,
  "status": "designer_passed",
  "pre_gates": { "designDocComplete": true, "postBuildVerdict": "pass" }
}
```

Then extract from the design package per `references/design-package-bridge.md`.

For `intent_only`, this gate has a second mandatory output before Stage 2 can
pass: read the design package's `SpatialUI Web component map` and
`preview.html`, then build an in-memory conversion inventory using
`references/spatialui-web-to-compose.md`. Every used `sui-*` tag must resolve to
its production Compose API, state/callback binding, and page-level or
window-level hierarchy. A mapped tag cannot become custom `Box`/`Row` UI.

**BLOCKED** if `pico-spatial-app-designer` is unavailable, the user declines the
design pass, either pre-gate fails, or a used `sui-*` tag cannot be resolved.
Do not continue with shallow text extraction or custom fallback —
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
- for `intent_only`, treat the designer's `SpatialUI Web component map` as
  implementation evidence: preserve each component's semantic role, state,
  slots, and hierarchy through the Web → Compose conversion inventory
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
- **New project:** the project is created by `pico-cli project create` — never by hand. Delegate the scaffold step to `spatial-app-onboarding`, passing the Decide-stage container as the template (`ON_PLAIN → planar`, `IN_VOLUME → volumetric`, `STAGE_* → stage`). Resume only after it returns `<target>/.scratch/onboarding_handoff.json`. The handoff must be scaffold-only (`product_ui_implemented=false`); if onboarding implemented product UI, treat that as a failure and rebuild the UI here. Then build the requested experience on top of the generated entry point — do not re-scaffold, rewrite `mainApp`, or re-insert manifest meta-data.

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

- Build from the decisions: root container → window ornaments → windows → regions → reusable components.
- For `intent_only`, implement every resolved row from the Web → Compose
  conversion inventory. `sui-tab-bar`/`sui-toolbar`/`sui-subwindow`/
  `sui-augment` remain root/window ornaments; modal, menu, coachmark, popup, and
  snackbar mappings keep their SpatialUI state/host patterns. Never copy HTML
  attributes or DOM event names into Kotlin.
- **Set the container meta-data in `AndroidManifest.xml` to match the Decide stage.** It is the runtime source of truth and what verification reads back. See `references/manifest-and-entry.md`.
- **Spacing ownership and root fill are explicit.** A root-fill shell is edge-to-edge with insets on inner content; an outer-padding card carries its own margin. Give every gap exactly one owner — do not double-pad or drop the outer margin. See `references/layout-inference.md`.
- Apply the **component rules C0–C7** above. This is where they bind.
- Read `../spatial-ui-design-style/SKILL.md` before Compose UI. When a design product exists, build a complete custom `ColorScheme`: call `systemColorScheme(...)` once, then explicitly assign all 16 public roles in `.copy(...)`, using exact design tokens for overridden roles and `role = system.role` for deliberate Vibrant inheritance. Inject it via `PicoTheme(colorScheme = …)`; a partial copy or plain `PicoTheme {}` is a fidelity failure. `windowConstraints(...)` is resize bounds, not first-open size.
- Do not carry design-review apparatus into the product UI. Viewport presets, data-mode controls, token legends, coverage badges, and implementation notes are omitted unless the source requirement identifies them as real user features.
- Preserve every extracted radius on the surface that owns it. For a
  view-level glass surface, declare one shape and apply
  `clip(shape) → backgroundMaterial(...) → border(..., shape)`.
  `border(..., RoundedCornerShape(...))` alone does not clip the material.
  Deliberately rectangular material requires
  `// design-style: rectangular-material <reason>`.
- Keep business UI 2D unless the design justifies 3D; Stage-only APIs stay out of WindowContainer flows.
- For a `STAGE_*` root: host 3D via `SpatialView` + ECS entities (`Entity()` / `Entity.load(...)` + `content.addEntity(...)`) and attach 2D controls with `AttachmentPanel(id){}` positioned in meters on an ECS anchor. Never a flat `Box`/`Column`/`Canvas` page, never a bare Compose overlay. See `references/stage.md`.

#### Architecture rules (HARD)

Read `references/architecture-conventions.md` before writing code. The checker
enforces layered packages, a thin `Main.kt`, MVI-lite state, repository
boundaries, mandatory ViewModel tests, and UseCase + tests when the screen has
non-trivial business rules, filtering, sorting, selection, or transformation.

### Stage 5 — Verify

#### 5a. Machine gates

```bash
bash scripts/validate_workflow_and_build.sh <target> \
    --input-mode <mode> --generation-mode <mode> [--visual-asset true] \
    --design-color <role>=<#hex> ...   # or --no-design-colors
    [--profile patch] [--skip-*] [--allow-degraded]
```

Eight steps: handoff receipts → implementation scan → Gradle sync → smoke build →
runtime launch → architecture → unit tests → design-style admission.

Pass **every** design-specified color with `--design-color`; pass
`--no-design-colors` only when the design genuinely specifies none. Omitting both
is an error, because a silent "no colors" would disable the fidelity gate exactly
when it matters.

Before invoking the verifier, compare the `--design-color` arguments against the
Stage 2 inventory. Counts and names must cover all app-owned surface/fill,
foreground, divider/border, semantic, and custom colors. Passing only the brand
accent set is a failed verification setup, even if the verifier itself exits 0.

Design-style admission is non-optional: a missing verifier, missing source root,
verifier failure, or `--skip-design-style` all fail the run.

Do NOT paraphrase JSON results — read `passed` / `failures_or_explicit_none` /
`warnings_or_explicit_none` literally. `verification_summary.json.clean: false`
means a degraded run and exits non-zero unless `--allow-degraded` was explicit.
Disclose every warning and skip; never imply a skipped gate passed.

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

#### 5c. Structural self-review (LLM-owned)

The machine cannot check these — do them yourself:

- repeated structures preserved as templates, not copy-pasted blocks
- selected / disabled / highlighted states represented in state holders
- **window model actually matches the built structure** (one primary surface for `single_panel` / `sidebar_content` / `master_detail`; a popup is not a second window)
- **`multi_window` is justified by disconnected-surface evidence** — no machine check covers this
- no UI invented beyond the input
- in `existing_module` mode, module resources reused before adding new ones

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
4. `design_style_result.json.passed == true` with 0 errors and no skip/degraded bypass. When the design declares colors, they were passed via `--design-color` and the verifier proved a complete 16-role `systemColorScheme(...).copy(...)`, explicit `PicoTheme(colorScheme = …)` injection, and exact value coverage.
5. For `generation_mode=new_project`, `.scratch/onboarding_handoff.json` records `scaffold_only=true`, `product_ui_implemented=false`, `build_passed=true`, `resume_skill=spatial-design-to-app`.
6. For no-visual inputs, `.scratch/design_escalation_receipt.json` records `status=designer_passed`.
7. For `intent_only`, every `sui-*` tag used by the passed design package maps
   to and is implemented with its corresponding SpatialUI Compose API.
8. For `visual_design` runs that used the `codin-d2c-figma-to-code` tools, `figma_hooks_result.json` shows verify then cleanup, each exactly once. When those tools were unavailable, the run was re-routed per stage 1b (`visual_reference`, or BLOCKED) and the handoff says so — an unavailable prerequisite is never a silently skipped gate.
9. Every app-authored `Text` resolves an explicit semantic foreground or has a
   verified `design-style: inherited-content-color <provider>` marker; no dark
   surface relies on CSS-like inheritance.
10. No pitfall below was triggered.

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
