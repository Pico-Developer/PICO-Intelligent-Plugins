# Design Package Bridge

Convert the Markdown design facts delivered by `pico-spatial-app-designer` into
the `spatial-design-to-app` Phase 3 three-artifact set: `evidence_packet.json` /
`normalized_spatial_spec.json` / `assumption_ledger.json`. This is the core seam
of the "no-visual requirement → design first → then generate code" path.

This file is a `spatial-design-to-app` `references/` document, **not an
adapter**: it has no adapter frontmatter, is not registered in
`../adapters/_registry.json`, and occupies no `input_mode`. It is referenced by name
from `intent-adapter` / `prd-adapter` only when
`.scratch/design_escalation_receipt.json` has `status=designer_passed`, to guide
them through a high-confidence extraction from the design package that replaces
the original shallow text extraction.

## 0. Boundary declaration (read first — it constrains everything below)

| Boundary                                  | Rule                                                                                                                                                                                                                                                                                         |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No write-back to the design package       | The bridge only **reads** the design package; its outputs are written to `<target>/.scratch/`, and it never modifies `review/*.md` / `preview.html`.                                                                                                                                         |
| Terms ≠ enums                             | The design package uses PICO design terminology (WindowContainer Planar, Stage Progressive, TabBar…); these terms are **not equal to** the downstream enums (`ON_PLAIN` / `STAGE_PROGRESSIVE` / `window_chrome_ornaments`…).                                                                 |
| Term→enum mapping happens downstream only | The mapping from terms to enums happens downstream only. The bridge is responsible for **preparing evidence + normalizing intent**; the **final decision** on container / window model is **left to Phase 4** (`container-decision.md` / `window-model-decision.md` run the legality check). |
| No Phase 4/5 artifacts                    | The bridge does not produce `container_decision` / `window_model_decision` / `spatial_layout_contract` / `patch_contract`, and does not produce `design-spec.json`.                                                                                                                          |
| No new schema fields                      | It may only write existing fields of the existing three-artifact schemas — no new top-level fields, no new `input_mode`.                                                                                                                                                                     |
| Receipt-gated consumption                 | The bridge consumes a design package only after `design_escalation_receipt.json` records `status=designer_passed`, all three pre-gates, `bridge_allowed=true`, and `adapter_extraction=design_package_bridge`. A design package that merely exists on disk is not enough.                    |

> Key discipline: the bridge turns design facts into "evidence
> (`evidence_packet.facts.*`) + normalized intent (`normalized_spatial_spec.*`)".
> It **may record leaning evidence for container/window**, but it does not commit
> to the container or window model at the bridge layer — that is Phase 4's job.

---

## A. Input: design package fact sources

### A.1 Design package location and pre-gates

The design package is delivered by `pico-spatial-app-designer`, landing in its
review template directory (six `review/*.md` role docs + one `preview.html`
preview):

```
<design-package>/
├── review/
│   ├── pm-requirement-spec.md        # product requirements (intent + quality contract + assumptions)
│   ├── uxr-research-report.md         # research evidence + domain model + baseline anchors
│   ├── interaction-spatial-spec.md    # container / attachment / window sizing / state graph
│   ├── visual-system-spec.md          # tokens / component anatomy / window-internal layout
│   ├── design-critique-report.md      # main-thread acceptance record + review conclusions
│   └── preview-qa-report.md           # preview coverage manifest + mapping table
└── preview.html                       # web preview approximation (web_design_validation_only)
```

**Pre-gates (all required; without them the design package must not be
consumed):**

| Gate                            | Source                                                          | Pass condition                                                                                                 |
| ------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Design delivery ready           | `design-critique-report.md`                                     | `designStatus = ready_for_design_delivery`                                                                     |
| Downstream generation allowed   | `design-critique-report.md` main-thread acceptance table        | `downstreamAppGenerationAllowed = yes`                                                                         |
| Main-thread acceptance recorded | `design-critique-report.md` §main-thread acceptance / `HG-HOST` | The main thread has re-read the trace/critique/preview QA and **re-derived** the above statuses, with a record |

> If any of the three gates fails (`designStatus != ready_for_design_delivery`,
> no `downstreamAppGenerationAllowed=yes`, or no main-thread acceptance record),
> **do not run this bridge**: fall back to the `intent-adapter` / `prd-adapter`
> shallow extraction, and record the "no complete design, low evidence
> confidence" assumption in `assumption_ledger.json` (see §F).

The downstream receipt must mirror this decision before the bridge runs. These
are the minimum JSON artifact fields expected by
`check_workflow_artifacts.py`; `Gate result: PASS | BLOCKED` is a prose Step
Output field, not a receipt JSON field:

```json
{
  "schema_version": 1,
  "phase": "1.5a_design_escalation_gate",
  "input_mode": "intent_only",
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

### A.2 Six documents → fact-source mapping

| Design package document       | Facts provided                                                                                                                                                                                                                                       | Three-artifact fields fed (downstream)                                                                                                                                                                                                                                                             |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pm-requirement-spec.md`      | §2–§5 intent definition (frozen items: domain, risk, default space, core scenario), §7 quality contract, §6 assumption list, §3 Key Moment, task/user goals                                                                                          | `product_intent`; `facts.app_type_candidates`; `facts.user_tasks`; `assumption_ledger[]` (§6 assumptions)                                                                                                                                                                                          |
| `uxr-research-report.md`      | §3 five research evidence classes (market/user/domain/platform/safety), decision-time baseline, domain model, evidence gaps                                                                                                                          | `facts.data_requirements`; research anchors in `evidence_trace[]`; `assumption_ledger[]` (evidence gaps → assumptions)                                                                                                                                                                             |
| `interaction-spatial-spec.md` | §7.2 container selection (Space State + WindowContainer form + Stage tier), §8 window attachment decision matrix, §9 window sizing derivation (default/min/max dp, scene tier, official baseline, hit target ≥56dp, body ≥12dp), §10 state graph     | `spatial_intent` (with container leaning evidence + `spatial_features`); `window_intent` (with `surfaces` + window model leaning evidence); `layout_intent` (regions/repeated_structures/states + sizing/spacing intent); `facts.spatial_cues` / `facts.interaction_cues` / `facts.visible_states` |
| `visual-system-spec.md`       | §3 design tokens (radius/spacing/typography/colorSemantics/materials incl. glassStyle Thin/Regular/Thick/Thickest), §5.0 window-internal layout (contentInset/grid/region mapping), §5 per-component anatomy (metrics: padding/gap/radius/hitTarget) | `layout_intent` (`root_fill` / `spacing_ownership` intent); `facts.regions` / `facts.repeated_structures`; visual facts → `assumption_ledger[]`                                                                                                                                                    |
| `design-critique-report.md`   | Main-thread acceptance record, `rederivedDesignStatus`, `downstreamAppGenerationAllowed`, per-review gate conclusions, open findings                                                                                                                 | Pre-gate evidence (§A.1); acceptance anchors in `evidence_trace[]`                                                                                                                                                                                                                                 |
| `preview-qa-report.md`        | Coverage Manifest (design-fact denominator), item-by-item mapping table, coverage checklist, device-validation boundary (`not_performed`)                                                                                                            | Consistency evidence → `evidence_trace[]`; uncovered items → `unknowns[]`                                                                                                                                                                                                                          |

> `preview.html` serves only as a web logic approximation
> (`web_design_validation_only`); it **must not** be treated as evidence of PICO
> physical size or device color shift. The authoritative source for sizes and
> spacing is `interaction-spatial-spec.md §9` and `visual-system-spec.md §5.0`,
> not the preview's CSS pixels.

---

## B. PICO term → container enum mapping table

Read the container facts from `interaction-spatial-spec.md §7.2` (container
selection) and turn them into **container evidence/leaning that supports Phase
4**. Legal enums: `ON_PLAIN` / `IN_VOLUME` / `STAGE_MIXED` / `STAGE_PROGRESSIVE`
/ `STAGE_FULL`.

| Design package container fact (§7.2 terms)                                                        | Container enum (Phase 4 evidence) | Space State | `spatial_features` cues                                                       |
| ------------------------------------------------------------------------------------------------- | --------------------------------- | ----------- | ----------------------------------------------------------------------------- |
| WindowContainer · Planar (Shared Space, depth locked to 640dp, 2D-dominant; may embed smaller 3D) | `ON_PLAIN`                        | Shared      | No passthrough/skybox; small 3D uses `model_3d` (`SpatialModelView`)          |
| WindowContainer · Volumetric (Shared Space, scalable cube, contains larger 3D)                    | `IN_VOLUME`                       | Shared      | `model_3d`; still no passthrough/skybox; anchor/env_mesh **forbidden**        |
| Stage · Mixed (immersion tier 0, passthrough real-world background)                               | `STAGE_MIXED`                     | Full        | `passthrough` (**only** `STAGE_MIXED`); may use `anchor`/`env_mesh`/free 3D   |
| Stage · Progressive (immersion 0–100, may include skybox / virtual environment)                   | `STAGE_PROGRESSIVE`               | Full        | `skybox` (only `STAGE_PROGRESSIVE`/`STAGE_FULL`); may use `anchor`/`env_mesh` |
| Stage · Full (immersion 100, fully immersive with no real background)                             | `STAGE_FULL`                      | Full        | `skybox`; no passthrough; may use `anchor`/`env_mesh`                         |

**spatial_features legality (consistent with `check_layout_structure.py`'s
`stage_feature_legality`):**

| feature               | Allowed containers                  | Bridge recording rule                                                                                            |
| --------------------- | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `passthrough`         | `STAGE_MIXED` only                  | Record when the design package declares a Mixed tier + real-world background; entering a WindowContainer = BLOCK |
| `skybox`              | `STAGE_PROGRESSIVE` / `STAGE_FULL`  | Record when the design package declares a virtual environment/skybox                                             |
| `anchor` / `env_mesh` | Stage-only (Mixed/Progressive/Full) | Stage-only; **must not** enter `ON_PLAIN` / `IN_VOLUME`, otherwise `check_layout_structure.py` BLOCK             |
| `model_3d`            | Any container                       | 3D embedded inside a WindowContainer (`SpatialModelView`) also uses this; does not trigger Stage                 |

> Ownership of the decision: this table only **prepares container
> evidence/leaning for Phase 4**. The final Container Decision is made by Phase 4
> reading the legality table in `container-decision.md`. The bridge translates
> the terms into "leaning + feature cues" and writes them into `spatial_intent`
> (see §E.2); it **does not select the final container at the bridge layer**.

---

## C. Window attachment → window model / window_chrome_ornaments mapping

Read `interaction-spatial-spec.md §8` (window attachment decision matrix) and
turn it into **window model evidence that supports Phase 4**. Legal window model
enums: `single_panel` / `single_panel_with_popup` / `sidebar_content` /
`master_detail` / `window_plus_subwindow` / `multi_window`.

| Design package §8 attachment fact                                                               | Window model (Phase 4 evidence) | Key criterion                                                     |
| ----------------------------------------------------------------------------------------------- | ------------------------------- | ----------------------------------------------------------------- |
| Only `InlineControl` / `None`, single main window                                               | `single_panel`                  | No independent overlay, no second persistent surface              |
| `SpatialPopup` / transient menu / contextual overlay (overlay, not persistent)                  | `single_panel_with_popup`       | Overlay in tone; **not** a persistent subwindow                   |
| `SideNavigation` (side rail) + content region                                                   | `sidebar_content`               | `Row(sidebar, content)` inside one window                         |
| List → detail (list + detail as two persistent panes side by side)                              | `master_detail`                 | Two persistent panes belong to the **same** coordinated window    |
| Persistent `Subwindow` (side-attached, height-locked filling the host, shared lifecycle)        | `window_plus_subwindow`         | One launcher; auxiliary window shares the main window's lifecycle |
| Independent launcher / independent lifecycle / independently placed multiple `WindowContainer`s | `multi_window`                  | **Must** have disconnected-surface evidence (see below)           |

**`window_chrome_ornaments[]` (docked attachment) mapping:** when `TabBar` /
`Toolbar` / `Subwindow` act as docked attachments, record them as
`window_chrome_ornaments[]` entries (`type ∈ TabBar / Toolbar / Subwindow`). They
are **sibling nodes of the main window**, not page child nodes (do not stuff them
into `windows[].children` or `regions[]`).

```json
"window_chrome_ornaments": [
  { "type": "TabBar", "placement": "Top", "note": "§8 docked: top-center persistent navigation, sibling of main window" },
  { "type": "Toolbar", "placement": "Bottom", "note": "§8 docked: bottom-center action bar" }
]
```

**Hard gate for multi_window (consistent with `check_layout_structure.py`'s
`overlay_vs_multi_window`):**

| Situation                                                                                                                                       | Result                                                                                             |
| ----------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Design package §8 explicitly states "independent placement / independent size / independent lifecycle / separate bounds / independent launcher" | Disconnected-surface evidence holds → can support `multi_window`                                   |
| Design package only describes overlay / popup / dropdown / anchored / attached-to-main-panel                                                    | Judged **not** `multi_window` (would be BLOCKed); should land in `single_panel_with_popup`         |
| No disconnected evidence at all                                                                                                                 | `multi_window` is BLOCKed; missing evidence must be recorded in `unknowns[]` and handed to Phase 4 |

> The bridge must carry the exact wording from §8 about "independent surface vs
> overlay" as **textual evidence** into `evidence_packet` /
> `normalized_spatial_spec.evidence_trace`, so that Phase 4's disconnected-surface
> judgment has grounds. Ownership of the decision: the final window model decision
> belongs to Phase 4, via the Subwindow-vs-`multi_window` escalation in
> `window-model-decision.md`.

---

## D. Window sizing methodology → window constraints / root_fill / spacing_ownership

### D.1 §9 window sizing derivation → window size constraints

Read the default / min / max (dp), aspect ratio, and `ResizeRestriction` from
`interaction-spatial-spec.md §9` (Window Sizing Derivation), and map them into the
layout contract's window size constraints (for Phase 5 to use; the bridge first
records sizing intent in `layout_intent`).

| §9 fact                                                                | Layout contract window constraint | Legal domain / floor                                                             |
| ---------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------- |
| Planar default (e.g. 1280×720dp official baseline, content-calibrated) | Window default size intent        | Legal domain 320×180dp ~ 2700×1800dp; depth fixed at 640dp (not configurable)    |
| Planar min / max (ResizeRestriction: `ContentMinSize` / `ContentSize`) | Window min / max intent           | Falls within the legal domain                                                    |
| Hit target floor                                                       | Interaction hit-region constraint | ≥ 56×56dp                                                                        |
| Body font floor                                                        | Body readability constraint       | ≥ 12dp                                                                           |
| Aspect-ratio policy                                                    | Aspect-ratio intent               | 16:9 not mandatory; choose by content (list/timeline/comparison/reading/console) |

> Prohibition: **do not** let codegen fall back to 1600×900, and **do not** treat
> 1280×720 as the final fixed value for all projects. Sizes come from the
> content-derived result in §9; the bridge only transports, it does not guess.

### D.2 §5.0 contentInset / grid / per-component metrics → root_fill + spacing_ownership

Read `visual-system-spec.md §5.0` (window-internal layout: contentInset, Grid,
region→component mapping) and §5 per-component metrics (padding / gap / radius).
See "Spacing ownership & root fill" in `layout-schema.md`: every inset/padding/gap
must have a **unique owner node**, and `root_fill` must be set explicitly.

| §5.0 / §5 fact                                                                         | Maps to                         | Rule                                                                   |
| -------------------------------------------------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------- |
| Whether the window shell fills the window (edge-to-edge background/surface)            | `root_fill = fill_window`       | Root fills the window; edge spacing belongs to the **inner** container |
| Whether the window shell is a card with outer padding (does not touch the window edge) | `root_fill = padded_card`       | Root card carries its own outer padding; children sit inside           |
| `contentInset` (top/right/bottom/left dp)                                              | one `spacing_ownership[]` entry | `kind=padding`/`inset`, `owner` is the node carrying the inset         |
| Gap between regions (§5.0 spacing tier)                                                | one `spacing_ownership[]` entry | `kind=vertical_gap`/`horizontal_gap`, `owner` is the inner container   |
| Component-internal padding / element gap (§5 metrics)                                  | one `spacing_ownership[]` entry | `kind=padding`, `owner` is that child component                        |

The two `root_fill` structures (must not be confused; see `layout-schema.md`):

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
  { "id": "content_inset", "value_dp": 16, "owner": "inner_content_column", "kind": "inset",
    "note": "§5.0 contentInset: root fill_window, inset owned by inner content, not root" },
  { "id": "region_gap", "value_dp": 16, "owner": "inner_content_column", "kind": "vertical_gap" },
  { "id": "card_padding", "value_dp": 16, "owner": "content_card", "kind": "padding" }
]
```

### D.3 Glass material facts

`visual-system-spec.md §3.3` (materials, incl. glassStyle `Thin/Regular/Thick/
Thickest`): the glass background material is **usable only inside a
WindowContainer** (Stage / 3D scenes need their own backing). The bridge records
it as a **visual fact / assumption** (see §E.1, §E.3); it **does not treat it as a
container decision** — it does not change the container leaning in §B.

---

## E. Design fact → three-artifact field-level fill rules

### E.1 `evidence_packet.json`

Required schema keys: `facts` (object), `unknowns` (array), `conflicts` (array),
`confidence` (object).

| Field                                          | Source                                                                                                          | Fill rule                                                                                                                                                       |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `facts.app_type_candidates`                    | pm §2–§5 intent definition                                                                                      | Induce the app archetype from domain / core scenario                                                                                                            |
| `facts.user_tasks`                             | pm tasks, interaction §3 task model                                                                             | User core task verbs/decisions                                                                                                                                  |
| `facts.regions`                                | visual §5.0 region mapping, interaction §14                                                                     | Main regions inside the window (header/sidebar/content/detail/toolbar…)                                                                                         |
| `facts.repeated_structures`                    | visual §5 component anatomy, §5.0 grid                                                                          | Repeated templates (nav_item/list_row/card/tab_item…)                                                                                                           |
| `facts.visible_states`                         | interaction §10 state graph, visual §5 states table                                                             | Visible states (selected/disabled/loading/empty/error…)                                                                                                         |
| `facts.spatial_cues`                           | interaction §7.2 container selection, pm §3 Key Moment                                                          | Spatial cues (flat_panel/visible_depth/passthrough_background/virtual_environment…)                                                                             |
| `facts.interaction_cues`                       | interaction §8 attachment, §12 input                                                                            | Interaction cues (search/tab_switch/list_selection/popup_open_close/drag_rotate_scale…)                                                                         |
| `facts.data_requirements`                      | uxr §3 domain model, visual §7 data contract                                                                    | Data entities / freshness / semantic enum requirements                                                                                                          |
| `unknowns[]`                                   | Assumptions/pending items still flagged in each doc, preview-qa uncovered items                                 | Keep as unknown, hand off for later resolution                                                                                                                  |
| `conflicts[]`                                  | Conflicts within the design package or against user constraints (e.g. §8 attachment contradicts §7.2 container) | Record without silently merging                                                                                                                                 |
| `confidence.{layout,interaction,spatial_mode}` | A delivery-ready design package                                                                                 | **Materially higher than shallow extraction** (e.g. `layout ≥ 0.8`), because the evidence comes from a delivered, main-thread-accepted, complete design package |

> **Custom facts key convention**: beyond the keys above, you may add traceable
> custom fact keys (such as `facts.container_leaning`, `facts.window_sizing`,
> `facts.disconnected_surfaces`, `facts.glass_materials`), and indicate the design
> package source in `note`. The naming must be referenceable by the Phase-5 layout
> contract's `evidence_trace.fact_ref` in the `facts.<key>` form (see §E.4).

Confidence example (contrasted against shallow extraction's `layout ≈ 0.35`):

```json
{
  "facts": {
    "app_type_candidates": ["physics_experiment_scene"],
    "user_tasks": ["set_slit_spacing", "observe_interference", "compare_patterns"],
    "regions": ["control_panel", "observation_view", "parameter_readout"],
    "repeated_structures": ["parameter_row", "preset_card"],
    "visible_states": ["running", "paused", "reset", "loading"],
    "spatial_cues": ["flat_panel"],
    "interaction_cues": ["slider_adjust", "play_pause", "tab_switch"],
    "data_requirements": ["slit_spacing_mm", "wavelength_nm", "screen_distance"],
    "container_leaning": {
      "toward": "ON_PLAIN",
      "source": "interaction-spatial-spec.md §7.2 WindowContainer Planar, Shared Space"
    },
    "window_sizing": {
      "default_dp": [1280, 720],
      "min_dp": [720, 480],
      "source": "interaction-spatial-spec.md §9"
    }
  },
  "unknowns": ["3d_model_asset_final_polycount"],
  "conflicts": [],
  "confidence": { "layout": 0.86, "interaction": 0.82, "spatial_mode": 0.8 }
}
```

### E.2 `normalized_spatial_spec.json`

Required schema keys: `request_context`, `product_intent`, `spatial_intent`,
`window_intent`, `layout_intent`, `ambiguities` (array), `evidence_trace` (array).

| Field              | Source                                                                  | Fill rule                                                                                                                                                                                                                          |
| ------------------ | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `request_context`  | Phase 1/2, pm §5 default space                                          | `generation_mode`, `target_module`/`output_dir`; existing mode records `existing_root_container` (legal container enum)                                                                                                            |
| `product_intent`   | pm §2–§5, §7 quality contract                                           | `app_type` / `primary_user_goal` / `core_tasks`                                                                                                                                                                                    |
| `spatial_intent`   | interaction §7.2, §B mapping table                                      | Record **container leaning evidence** (narrative, e.g. "§7.2 selects WindowContainer Planar / Shared Space, leans ON_PLAIN") + `spatial_features` (per §B legality) + `immersion_need`; **do not commit the final container here** |
| `window_intent`    | interaction §8, §C mapping table                                        | Record `surfaces[]` (e.g. `[{ "id": "main", "role": "primary_panel" }]`) + **window model leaning evidence** (narrative); sibling-node cues for docked attachments                                                                 |
| `layout_intent`    | interaction §9/§10, visual §5.0/§5                                      | `regions` / `repeated_structures` / `states`; the §D window sizing intent, `root_fill`, `spacing_ownership` intent                                                                                                                 |
| `ambiguities[]`    | Design package pending items, missing disconnected evidence in §C, etc. | Each `{ key, default_decision, reason }`, e.g. popup persistence defaults to `treat_as_overlay`                                                                                                                                    |
| `evidence_trace[]` | All documents                                                           | Each entry points to a concrete design package source (see §E.4)                                                                                                                                                                   |

> Discipline: `spatial_intent` / `window_intent` carry only **leaning evidence +
> spatial_features + surfaces**, recording the design package basis in narrative
> form; they **do not commit** the container and window model inside the bridge —
> the final decision belongs to Phase 4. (The `normalized_spatial_spec.json`
> schema optionally accepts the container/window intent fields, but per the
> repository's existing adapter contract, the bridge only provides evidence +
> normalized intent.)

### E.3 `assumption_ledger.json`

Schema: a JSON **array**; each entry requires the keys `assumption`, `impact`,
`confidence`.

| Source                                                                 | Conversion rule                                                                  |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| pm §6 assumption list (`confidence / impact / validation plan`)        | Convert each into `{ assumption, impact, confidence }`                           |
| uxr §3 evidence gaps                                                   | Convert into low-confidence assumptions, with `impact` noting the affected scope |
| visual inferences (glass tier, density, color semantic fallback, etc.) | Convert into visual assumptions                                                  |

```json
[
  {
    "assumption": "Control panel uses an ON_PLAIN single coordinated window, because §7.2 judges 2D read/write dominant with no immersion need",
    "impact": "container_choice,window_model",
    "confidence": 0.84
  },
  {
    "assumption": "Key readout panel uses the Thick glass tier to stay readable under passthrough (§3.3 visual inference)",
    "impact": "visual_material",
    "confidence": 0.7
  }
]
```

> If there are no assumptions at all, you must still write `[]`
> (`check_workflow_artifacts.py` requires `assumption_ledger.json` to exist).

### E.4 evidence_trace traceability rules

Each `evidence_trace` entry must point to a **concrete source in the design
package** to guarantee traceability:

```json
"evidence_trace": [
  { "claim": "container leans ON_PLAIN", "because": "interaction-spatial-spec.md §7.2 WindowContainer Planar / Shared Space" },
  { "claim": "window default 1280×720dp", "because": "interaction-spatial-spec.md §9 window sizing derivation" },
  { "claim": "root fills window, inset owned by inner content", "because": "visual-system-spec.md §5.0 contentInset + §3.4 spacing" },
  { "claim": "passed main-thread acceptance", "because": "design-critique-report.md rederivedDesignStatus=ready_for_design_delivery" }
]
```

**Handoff to the Phase 5 layout contract `evidence_trace`
(`check_workflow_artifacts.py`):** in the Phase 5 layout contract, every
`evidence_trace.fact_ref` **must** satisfy one of the following —

| fact_ref form                                                                                      | Meaning                                                                |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Starts with `facts.` (e.g. `facts.container_leaning`)                                              | References `evidence_packet.facts.<key>`; that key must actually exist |
| Starts with `decision.` / `container_decision.` / `window_model_decision.` / `phase4.` / `Phase 4` | References a Phase-4 decision field                                    |

> Therefore the evidence facts produced by this bridge **must be named so that
> later `fact_ref`s can reference them**: any fact you want a Phase 5 `fact_ref` to
> reference directly must go into `evidence_packet.facts.<key>`, with a readable,
> stable key name (such as `facts.window_sizing`, `facts.disconnected_surfaces`).
> The bridge's own outputs only need `claim + because` narrative traceability;
> `fact_ref` is a Phase 5 field, and this bridge does not produce Phase 5.

---

## F. Boundaries and non-goals

| Item                                | Rule                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No write-back to the design package | The bridge only reads the design package and writes outputs to `.scratch/`; it does not modify `review/*.md` / `preview.html`.                                                                                                                                                                                                                                                                                             |
| No `design-spec.json`               | The bridge does not produce the designer-side design-spec, nor Phase 4/5 artifacts.                                                                                                                                                                                                                                                                                                                                        |
| No final Phase 4 decision           | The **final commitment** to container / window model happens in Phase 4; the bridge only prepares evidence + normalized intent.                                                                                                                                                                                                                                                                                            |
| No new `input_mode`                 | The bridge is a `references/` document; it occupies no `input_mode` and is not in `_registry.json`.                                                                                                                                                                                                                                                                                                                        |
| No new top-level schema fields      | It only writes existing fields of the existing three-artifact schemas.                                                                                                                                                                                                                                                                                                                                                     |
| Block if a pre-gate fails           | When `designStatus != ready_for_design_delivery`, no `downstreamAppGenerationAllowed=yes`, no main-thread acceptance record, or no `status=designer_passed` receipt exists, the design package **must not** be consumed. Stop before app generation and report BLOCKED with the missing designer deliverables/gates; do not fall back to `intent-adapter` / `prd-adapter` shallow extraction for no-visual app generation. |

### F.1 Comparison against legacy shallow extraction

| Dimension           | Shallow extraction (no design package) | Design package bridge (this doc)                                    |
| ------------------- | -------------------------------------- | ------------------------------------------------------------------- |
| `confidence.layout` | ≈ 0.35                                 | ≥ 0.8 (from a delivered, main-thread-accepted design package)       |
| Window sizing       | None (codegen easily guesses wrong)    | From interaction §9 default/min/max, lands in `layout_intent`       |
| Spacing ownership   | Missing, prone to double padding       | §5.0/§5 → `root_fill` + `spacing_ownership`                         |
| Component anatomy   | None                                   | visual §5 per-component metrics                                     |
| Traceability        | Weak                                   | Each `evidence_trace` points to a concrete section of `review/*.md` |

### F.2 Validation-consistency self-check (reuse existing checkers, no new gate)

| Checker                       | What the bridge must guarantee                                                                                                                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `check_workflow_artifacts.py` | Three-artifact schema keys complete; `assumption_ledger.json` exists (use `[]` if none); Phase 5 `fact_ref` resolves to `facts.<key>`                                                                               |
| `check_layout_structure.py`   | `spatial_features` legality (passthrough→`STAGE_MIXED` only; skybox→PROGRESSIVE/FULL; anchor/env_mesh forbidden in WindowContainer); `multi_window` has disconnected-surface evidence                               |
| `check_adapter_contract.py`   | This document is a `references/` doc and is not scanned by this checker; the `intent-adapter` / `prd-adapter` that reference it must still not contain forbidden decision tokens or Phase-4 decision-doc references |
