# Design Package Bridge

Turn the design facts delivered by `pico-spatial-app-designer` into the evidence
that drives code generation. This is the core seam of the "no-visual requirement
→ design first → then generate code" path.

This skill generates code directly from design facts and does not persist
intermediate workflow JSON, so the bridge produces **understanding, not
artifacts**: you read the design package, extract the facts listed below, and
carry them into the Decide and Build stages. The one thing that _is_ persisted is
`.scratch/design_escalation_receipt.json`, because it records that the designer
pass really happened and passed.

`pico-spatial-app-designer` is a lean, host-LLM-orchestrated
Frame→Explore→Plan→Critique→Build→Critique loop. It delivers a **single design
document** `design-doc.md` plus one `preview.html`.

## 0. Boundary declaration (read first — it constrains everything below)

| Boundary                                     | Rule                                                                                                                                                                                                                                      |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No write-back to the design package          | The bridge only **reads** it; never modify `design-doc.md` / `preview.html`.                                                                                                                                                              |
| Terms ≠ enums                                | The design package uses PICO design terminology (WindowContainer Planar, Stage Progressive, TabBar…). These terms are **not equal to** this skill's enums (`ON_PLAIN` / `STAGE_PROGRESSIVE` / window ornaments).                          |
| The bridge prepares evidence; Decide commits | Mapping terms to enums, checking legality, and committing to a container / window model all happen in the **Decide** stage using `structure-decisions.md`. The bridge may record leaning evidence, never a decision.                      |
| Receipt-gated consumption                    | Consume a design package only after `design_escalation_receipt.json` records `status=designer_passed` with both pre-gates (`designDocComplete=true`, `postBuildVerdict=pass`). A design package that merely exists on disk is not enough. |

---

## A. Input: design package fact sources

### A.1 Design package location and pre-gates

The design package is delivered by `pico-spatial-app-designer` as a single
design document plus one preview prototype:

```
<design-package>/
├── design-doc.md      # §1 Frame · §2 Explore · §3 Plan · §4 Critique(pre-build) · §5 Build manifest · §6 Critique(post-build)
└── preview.html       # web preview approximation (web_design_validation_only)
```

`design-doc.md` is filled from the designer's `pico-spatial-app-designer/references/design-doc-template.md`
and is the single carrying layer of design facts. Its section map:

| Section                      | Contents the bridge reads                                                                                                                                                                                                                                                   |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **§1 Frame**                 | subject, viewer/context, the single job, spatial justification table (affordance + 2D counterfactual per core task), assumptions                                                                                                                                            |
| **§2 Explore**               | ≥3 alternatives, decision matrix, chosen direction + rejection reasons                                                                                                                                                                                                      |
| **§3 Plan**                  | Visual tokens (colors/type/materials + padding tokens), signature element, **Surface sizing table** (type/tier/clear-FOV/default/min/max), **Layout** (ASCII wireframe, regions, single focus), **State graph** (states + transitions), **Components** (data source + task) |
| **§4 Critique (pre-build)**  | generic-default simulation, hard-check table                                                                                                                                                                                                                                |
| **§5 Build**                 | coverage manifest (states/transitions/components/bindings/tiers)                                                                                                                                                                                                            |
| **§6 Critique (post-build)** | independent coverage rebuild, quality-bar table, patch log, **verdict** (`pass` / `changes_requested` / `block`)                                                                                                                                                            |

**Pre-gates (all required; without them the design package must not be
consumed):**

| Gate                | Source                      | Pass condition                                                                                        |
| ------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------- |
| Design doc complete | `design-doc.md` §1–§6       | All six sections filled (not placeholders); §3 Plan sizing table, state graph, and components present |
| Post-build verdict  | `design-doc.md` §6 Critique | The §6 Critique-again **verdict is `pass`** — quality bar met, no active blocking finding             |

> If either gate fails (`design-doc.md` incomplete, or §6 verdict is
> `changes_requested` / `block`), **do not run this bridge and do not fall back
> to shallow text extraction to keep generating**:
> stop before extraction and report `BLOCKED`, listing the missing sections or
> the unmet verdict. Only resume once the design package is complete and the
> designer records `status=designer_passed`. `check_handoff_receipts.py` rejects
> `fallback_accepted` as a continuation path for no-visual inputs.

Write the receipt before generating code. `check_handoff_receipts.py` requires
these fields (`Gate result: PASS | BLOCKED` is prose Step Output, not a receipt
field):

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
    "postBuildVerdict": "pass"
  }
}
```

### A.2 design-doc.md sections → fact-source mapping

| design-doc.md section        | Facts provided                                                                                                                              | Three-artifact fields fed (downstream)                                                                                                                               |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **§1 Frame**                 | subject/domain, viewer & room context, the single job, per-task spatial affordance + 2D counterfactual, assumptions                         | `product_intent`; app type, user tasks, spatial cues, and any assumptions worth stating                                                                              |
| **§2 Explore**               | chosen design direction, rejected alternatives + reasons                                                                                    | `spatial_intent` leaning narrative; rejection anchors in `evidence_trace[]`                                                                                          |
| **§3 Plan · Surface sizing** | per-window type (Planar/Volumetric), final default/min/max dp or meter values                                                               | `spatial_intent` (container leaning + `spatial_features`); `window_intent` (`surfaces` + window-model leaning); `layout_intent` sizing intent; `facts.window_sizing` |
| **§3 Plan · Layout**         | ASCII wireframe, regions (from task/data/frequency), single primary focus, density ceiling                                                  | `layout_intent.regions`; `facts.regions`                                                                                                                             |
| **§3 Plan · State graph**    | states (task/focus/components/data/entry-exit), transitions (trigger + confirm)                                                             | `facts.visible_states`; `facts.interaction_cues`; `layout_intent.states`                                                                                             |
| **§3 Plan · Components**     | per core component: data source + task served, variants, states; `SpatialUI Web component map` (`sui-*`, API, event/state, fallback reason) | `facts.repeated_structures`; `facts.data_requirements`; Web → Compose conversion inventory                                                                           |
| **§3 Plan · Visual tokens**  | complete 16-role theme contract, brand tokens, SpatialUI glass/material use, type pairing, padding tokens (8/16/24/32 dp)                   | complete design-driven `ColorScheme` definition (see §D.4), root glass / spacing ownership intent; state genuinely-inferred visual guesses explicitly                |
| **§6 Critique (post-build)** | verdict, quality-bar evidence, device-validation boundary (`not_performed`)                                                                 | Pre-gate evidence (§A.1); acceptance anchor in `evidence_trace[]`                                                                                                    |
| **§5 Build + preview.html**  | coverage manifest, triggerable state machine                                                                                                | Consistency evidence → `evidence_trace[]`; uncovered items → `unknowns[]`                                                                                            |

> `preview.html` serves only as a web logic approximation
> (`web_design_validation_only`); it **must not** be treated as evidence of PICO
> physical size or device color shift. The authoritative source for sizes and
> spacing is `design-doc.md §3 Plan` (Surface sizing + Visual tokens), not the
> preview's CSS pixels.

### A.3 SpatialUI Web → Compose conversion (`intent_only`)

For `input_mode=intent_only`, component conversion is a hard part of the
designer bridge rather than a later visual interpretation.

1. Read §3 `SpatialUI Web component map`.
2. Inventory every actual `sui-*` tag in `preview.html`; ignore tags that appear
   only inside the inlined runtime source.
3. Resolve each used tag through `spatialui-web-to-compose.md`.
4. Carry one in-memory conversion row per tag:

   ```text
   web_tag | semantic_role | compose_api | state_and_callback | hierarchy
   ```

5. Reconcile the design-doc map with the preview. A preview-only tag is added to
   the inventory; a design-doc-only tag remains required if §5 coverage says it
   represents a designed state.

Conversion preserves semantics, not Web syntax:

| Web evidence                                                 | Compose consequence                                                                             |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| `checked`, `selected-index`, `value`, `hidden`               | typed UI state and explicit visibility                                                          |
| `click-action`, `select`, `checked-change`, picker events    | callbacks dispatched to the state holder/ViewModel                                              |
| default/named slot                                           | composable content lambda                                                                       |
| CSV convenience attributes                                   | explicit child composables/DSL items                                                            |
| `sui-tab-bar`, `sui-toolbar`, `sui-subwindow`, `sui-augment` | root/window-level sibling; never an in-page `Row`/`Box` imitation                               |
| modal/menu/popup/coachmark/snackbar tags                     | corresponding SpatialUI window/host pattern with explicit visibility/dismissal                  |
| CSS token values                                             | authoritative §3 token mapped through `PicoTheme`/component defaults; CSS pixels are not copied |

**Gate:** every used `sui-*` tag resolves to a mapped Compose API. Because the
current SpatialUI Web catalog has production counterparts, a mapped tag cannot
fall through to `// TODO(missing-component)` or hand-built primitives. If a tag
is unknown, stop and repair the mapping/reference before Build.

---

## B. PICO term → container enum mapping table

Read the container facts from `design-doc.md §3 Plan` (Surface sizing table +
Layout: window type Planar/Volumetric, Shared/Full Space, any Stage tier) and
turn them into **container evidence** for the Decide stage. Legal enums:
`ON_PLAIN` / `IN_VOLUME` / `STAGE_MIXED` / `STAGE_PROGRESSIVE` / `STAGE_FULL`.

| Design package container fact (§3 Plan terms)                                                     | Container enum (Decide-stage evidence) | Space State | `spatial_features` cues                                                       |
| ------------------------------------------------------------------------------------------------- | -------------------------------------- | ----------- | ----------------------------------------------------------------------------- |
| WindowContainer · Planar (Shared Space, depth locked to 640dp, 2D-dominant; may embed smaller 3D) | `ON_PLAIN`                             | Shared      | No passthrough/skybox; small 3D uses `model_3d` (`SpatialModelView`)          |
| WindowContainer · Volumetric (Shared Space, scalable cube, contains larger 3D)                    | `IN_VOLUME`                            | Shared      | `model_3d`; still no passthrough/skybox; anchor/env_mesh **forbidden**        |
| Stage · Mixed (immersion tier 0, passthrough real-world background)                               | `STAGE_MIXED`                          | Full        | `passthrough` (**only** `STAGE_MIXED`); may use `anchor`/`env_mesh`/free 3D   |
| Stage · Progressive (immersion 0–100, may include skybox / virtual environment)                   | `STAGE_PROGRESSIVE`                    | Full        | `skybox` (only `STAGE_PROGRESSIVE`/`STAGE_FULL`); may use `anchor`/`env_mesh` |
| Stage · Full (immersion 100, fully immersive with no real background)                             | `STAGE_FULL`                           | Full        | `skybox`; no passthrough; may use `anchor`/`env_mesh`                         |

> A `pico-spatial-app-designer` package leans toward a **Planar
> WindowContainer** (`ON_PLAIN`) for most windowed apps, but the designer now
> covers any form. Read the form from §1 Frame's spatial justification and §3
> Plan's surface sizing: a Volumetric leaning appears when a 3D subject must be
> inspected in the round, and a Stage leaning (`STAGE_MIXED` / `STAGE_PROGRESSIVE`
> / `STAGE_FULL`) when the design explicitly requires passthrough or a virtual
> environment. Do not force `ON_PLAIN` when the package justifies a 3D or
> immersive form.

**Spatial-feature legality (consistent with `structure-decisions.md`'s
`stage_feature_legality`):**

| feature               | Allowed containers                  | Bridge recording rule                                                                                                      |
| --------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `passthrough`         | `STAGE_MIXED` only                  | Record when the design package declares a Mixed tier + real-world background; entering a WindowContainer = BLOCK           |
| `skybox`              | `STAGE_PROGRESSIVE` / `STAGE_FULL`  | Record when the design package declares a virtual environment/skybox                                                       |
| `anchor` / `env_mesh` | Stage-only (Mixed/Progressive/Full) | Stage-only; **must not** enter `ON_PLAIN` / `IN_VOLUME` — `scan_implementation.py` blocks Stage-only APIs in a window flow |
| `model_3d`            | Any container                       | 3D embedded inside a WindowContainer (`SpatialModelView`) also uses this; does not trigger Stage                           |

> Ownership of the decision: this table only **prepares container
> evidence for the Decide stage**. The final Container Decision is made there
> reading the legality table in `structure-decisions.md`. The bridge translates
> the terms into "leaning + feature cues" and writes them into `spatial_intent`
> (see §E.2); it **does not select the final container at the bridge layer**.

---

## C. Attachments → window model / window_chrome_ornaments mapping

Read the layout and attachment facts from `design-doc.md §3 Plan` (Layout +
Components: side rails, tabs, toolbars, popups, subwindows, master/detail panes)
and turn them into **window model evidence** for the Decide stage. Legal window
model enums: `single_panel` / `single_panel_with_popup` / `sidebar_content` /
`master_detail` / `window_plus_subwindow` / `multi_window`.

| Design package layout/attachment fact (§3 Plan)                                        | Window model (Decide-stage evidence) | Key criterion                                                     |
| -------------------------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------------------------- |
| Only in-place controls / `None`, single main window                                    | `single_panel`                       | No independent overlay, no second persistent surface              |
| Transient menu / contextual overlay (overlay, not persistent)                          | `single_panel_with_popup`            | Overlay in tone; **not** a persistent subwindow                   |
| Side rail (side navigation) + content region                                           | `sidebar_content`                    | `Row(sidebar, content)` inside one window                         |
| List → detail (list + detail as two persistent panes side by side)                     | `master_detail`                      | Two persistent panes belong to the **same** coordinated window    |
| Persistent subwindow (side-attached, height-locked filling the host, shared lifecycle) | `window_plus_subwindow`              | One launcher; auxiliary window shares the main window's lifecycle |
| Independent launcher / independent lifecycle / independently placed multiple windows   | `multi_window`                       | **Must** have disconnected-surface evidence (see below)           |

**`window_chrome_ornaments[]` (docked attachment) mapping:** when `TabBar` /
`Toolbar` / `Subwindow` act as docked attachments in §3 Plan, record them as
`window_chrome_ornaments[]` entries (`type ∈ TabBar / Toolbar / Subwindow`). They
are **sibling nodes of the main window**, not page child nodes (do not stuff them
into `windows[].children` or `regions[]`).

```json
"window_chrome_ornaments": [
  { "type": "TabBar", "placement": "Top", "note": "§3 Plan docked: top-center persistent navigation, sibling of main window" },
  { "type": "Toolbar", "placement": "Bottom", "note": "§3 Plan docked: bottom-center action bar" }
]
```

**Hard gate for multi_window (consistent with `structure-decisions.md`'s
`overlay_vs_multi_window`):**

| Situation                                                                                                                                            | Result                                                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Design package §3 Plan explicitly states "independent placement / independent size / independent lifecycle / separate bounds / independent launcher" | Disconnected-surface evidence holds → can support `multi_window`                                 |
| Design package only describes overlay / popup / dropdown / anchored / attached-to-main-panel                                                         | Judged **not** `multi_window` (would be BLOCKed); should land in `single_panel_with_popup`       |
| No disconnected evidence at all                                                                                                                      | `multi_window` is BLOCKed; state the missing evidence explicitly and hand it to the Decide stage |

> The bridge must carry the exact wording from §3 Plan about "independent surface
> vs overlay" as **explicit textual evidence**, so the Decide stage's disconnected-surface
> judgment has grounds. Ownership of the decision: the final window model decision
> belongs to the Decide stage, via the Subwindow-vs-`multi_window` escalation in
> `structure-decisions.md`.

---

## D. Surface sizing methodology → window constraints / root_fill / spacing_ownership

### D.1 §3 Plan window sizing table → window size constraints

Read the default / min / max (dp), aspect ratio, and resize range from the
`design-doc.md §3 Plan` Surface sizing table, and map them into the layout
window size constraints (for the Build stage to use; the bridge first records
sizing intent in `layout_intent`).

| §3 Plan sizing fact                                                    | Layout contract window constraint | Legal domain / floor                                                             |
| ---------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------- |
| Planar default (e.g. 1280×720dp official baseline, content-calibrated) | Window default size intent        | Legal domain 320×180dp ~ 2700×1800dp; depth fixed at 640dp (not configurable)    |
| Planar min / max (the resize range)                                    | Window min / max intent           | Falls within the legal domain                                                    |
| Hit target floor                                                       | Interaction hit-region constraint | ≥ 56×56dp                                                                        |
| Body font floor                                                        | Body readability constraint       | ≥ 12dp                                                                           |
| Aspect-ratio policy                                                    | Aspect-ratio intent               | 16:9 not mandatory; choose by content (list/timeline/comparison/reading/console) |

> Prohibition: **do not** let codegen fall back to 1600×900, and **do not** treat
> 1280×720 as the final fixed value for all projects. Sizes come from the
> content-derived Surface sizing table in §3 Plan; the bridge only transports, it
> does not guess. (See the designer's `pico-spatial-app-designer/references/window-sizing.md` for the chain
> that produced them.)

### D.2 §3 Plan Visual tokens (padding) + Layout → root_fill + spacing_ownership

Read the padding tokens (Small/Regular/Medium/Large = 8/16/24/32 dp) and the
Layout regions from `design-doc.md §3 Plan`, plus per-component spacing. See
"Spacing ownership & root fill" in `layout-inference.md`: every inset/padding/gap
must have a **unique owner node**, and `root_fill` must be set explicitly.

| §3 Plan fact                                                                           | Maps to                         | Rule                                                                   |
| -------------------------------------------------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------- |
| Whether the window shell fills the window (edge-to-edge background/surface)            | `root_fill = fill_window`       | Root fills the window; edge spacing belongs to the **inner** container |
| Whether the window shell is a card with outer padding (does not touch the window edge) | `root_fill = padded_card`       | Root card carries its own outer padding; children sit inside           |
| Container content padding (`Padding Large` 32dp = window-to-content)                   | one `spacing_ownership[]` entry | `kind=padding`/`inset`, `owner` is the node carrying the inset         |
| Gap between regions                                                                    | one `spacing_ownership[]` entry | `kind=vertical_gap`/`horizontal_gap`, `owner` is the inner container   |
| Component-internal padding / element gap (`Padding Small/Regular`)                     | one `spacing_ownership[]` entry | `kind=padding`, `owner` is that child component                        |

The two root-fill structures (must not be confused; see `layout-inference.md`):

```
root fill + internal inset (root_fill=fill_window)      outer padding card (root_fill=padded_card)
┌───────────────────────────┐                           ┌───────────────────────────┐
│ root fills window(edge bg) │                           │  outer margin(card off edge)│
│  ┌─────────────────────┐  │ ← edge inset on inner     │   ┌───────────────────┐    │ ← outer padding on card
│  │ inner content(w/ inset)│  │                           │   │ children(in card)  │    │
│  └─────────────────────┘  │                           │   └───────────────────┘    │
└───────────────────────────┘                           └───────────────────────────┘
```

```json
"spacing_ownership": [
  { "id": "content_inset", "value_dp": 32, "owner": "inner_content_column", "kind": "inset",
    "note": "§3 Plan Padding Large: root fill_window, inset owned by inner content, not root" },
  { "id": "region_gap", "value_dp": 16, "owner": "inner_content_column", "kind": "vertical_gap" },
  { "id": "card_padding", "value_dp": 16, "owner": "content_card", "kind": "padding" }
]
```

### D.3 Glass material facts

`design-doc.md §3 Plan · Visual tokens` (materials, incl. glass style): the glass
background material is **usable only inside a WindowContainer** (Stage / 3D
scenes need their own backing). The bridge records it as a **visual fact /
assumption** (see §E.1, §E.3); it **does not treat it as a container decision** —
it does not change the container leaning in §B.

### D.4 §3 Plan Visual tokens (colors) → design-driven theme

Read the complete 16-role table from `design-doc.md §3 Plan · Visual tokens`.
**The design's colors drive the theme** — the Build stage starts from
`systemColorScheme(...)`, explicitly assigns every public role in `.copy(...)`,
and injects the result via `PicoTheme(colorScheme = …)`. A role may preserve its
SpatialUI Vibrant system value, but it may not disappear through an omitted
parameter.

Two failure modes this prevents: (1) bare hex with no theming → flat hardcoded
page; (2) mapping the design's colors onto the _default_ theme roles → the
generic PICO palette, design colors thrown away.

PICO has two color families; carry each accordingly (grounded in
`spatial-ui-design-style/references/tokens.md §7`):

| §3 Plan color fact                                                                  | How to carry it                                              | Codegen consequence                                                                    |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| Brand / accent / fixed-semantic color that maps to a `ColorScheme` role + exact hex | role + hex; pass as `--design-color <role>=<#hex>` at Verify | Value goes verbatim into the custom `ColorScheme`; the design's identity is preserved  |
| Brand / decorative color with **no** matching `ColorScheme` role                    | named Kotlin color literal / token                           | Carried verbatim; does **not** enter `ColorScheme` (no role to bind to)                |
| Adaptive grayscale surface/text with explicit Vibrant inheritance                   | role + inherited system role                                 | Assignment uses `role = system.role` so the complete scheme stays visible and adaptive |
| Semantic status (color + shape cue + label)                                         | role + hex, plus the non-color cue                           | Override value into the scheme; UI shows the label, not a raw enum                     |
| Glass tier per surface                                                              | surface → tier                                               | Glass tier applied inside WindowContainer; never solid over root                       |

Legal role names (16 total): fill
`fillPrimary/fillSecondary/fillTertiary/fillLight`, text
`labelPrimary/labelPrimaryLight/labelSecondary/labelTertiary/labelQuaternary`,
fixed semantic `error/alert/passable/interaction`, state
`lightenHover/lightenPressed`, and `dividerLine`.

> **Theming rule.** Apply all 16 roles into a complete custom `ColorScheme` and
> inject it via `PicoTheme(colorScheme = …)`. A
> `systemColorScheme(context).copy(...)` call must name every role, forwarding
> inherited values as `role = system.role`. Collect exact design values into one
> `object <App>Colors` under `ui/theme/`: `ColorScheme`-slot values stay Kotlin
> `Color(0x…)` literals (the design-style R1b gate only reads `.kt` and rejects a
> `colorResource(...)` indirection for those slots), while non-semantic
> surface/text/brand colors may live in `res/color/*.xml` — see
> `figma-mapping.md §7.2`. Never emit a solid color / `fillPrimary` on the window
> root: the root is system `Material.Regular` glass; `fill*` roles are for inner
> cards and containers only.

**Every role-mapped color must be passed to the Verify stage** as
`--design-color <role>=<#hex>`. That is how R1b proves the design's palette was
actually restored rather than silently replaced by the stock one. If the design
package genuinely specifies no colors, pass `--no-design-colors` — the verifier
refuses to guess, because a silent "no colors found" would disable the gate
exactly when it matters.

---

## F. Boundaries and non-goals

| Item                                | Rule                                                                                                                                                                                                                                                                                                                                |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No write-back to the design package | The bridge only reads the design package and writes outputs to `.scratch/`; it does not modify `design-doc.md` / `preview.html`.                                                                                                                                                                                                    |
| No `design-spec.json`               | The bridge does not produce the designer-side design-spec.                                                                                                                                                                                                                                                                          |
| No final decision                   | The **final commitment** to container / window model happens in the Decide stage; the bridge only prepares evidence.                                                                                                                                                                                                                |
| No new `input_mode`                 | The bridge is a `references/` document; it occupies no `input_mode` and adds no new one.                                                                                                                                                                                                                                            |
| No new top-level schema fields      | It only writes existing fields of the existing three-artifact schemas.                                                                                                                                                                                                                                                              |
| Block if a pre-gate fails           | When `design-doc.md` is incomplete, its §6 verdict is not `pass`, or no `status=designer_passed` receipt exists, the design package **must not** be consumed. Stop before app generation and report BLOCKED with the missing designer deliverables/gates; do not fall back to shallow text extraction for no-visual app generation. |

### F.1 Comparison against legacy shallow extraction

| Dimension           | Shallow extraction (no design package)        | Design package bridge (this doc)                                                                       |
| ------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `confidence.layout` | ≈ 0.35                                        | ≥ 0.8 (from a complete design package with §6 verdict = pass)                                          |
| Surface sizing      | None (codegen easily guesses wrong)           | From §3 Plan Surface sizing default/min/max                                                            |
| Spacing ownership   | Missing, prone to double padding              | §3 Plan padding tokens → explicit root fill + per-node spacing owner                                   |
| Component anatomy   | None                                          | §3 Plan Components + complete `sui-*` → Compose conversion inventory                                   |
| Color               | Guessed hex, renders as a flat hardcoded page | §3 Plan defines all 16 roles; code injects a complete `ColorScheme` through `PicoTheme(colorScheme=…)` |
| Traceability        | Weak                                          | Each claim points to a concrete `design-doc.md` section                                                |

### F.2 Validation-consistency self-check

| Checker                     | What the bridge must guarantee                                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `check_handoff_receipts.py` | `design_escalation_receipt.json` exists with `status=designer_passed` and both pre-gates true before any code is written                                                       |
| `scan_implementation.py`    | Feature legality survives into code and the expanded SpatialUI vocabulary recognizes all mapped production components; semantic one-to-one mapping remains an LLM-owned review |
| `verify-design-style.sh`    | Every role-mapped design color is passed as `--design-color`; generated code explicitly assigns all 16 roles and injects the result through `PicoTheme(colorScheme = …)`       |
