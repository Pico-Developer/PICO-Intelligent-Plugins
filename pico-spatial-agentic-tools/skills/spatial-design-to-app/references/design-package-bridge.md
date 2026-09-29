# Design Package Bridge

Turn accepted design facts into the evidence that drives code generation. The
source may be `pico-spatial-app-designer` or a user-provided executable design
package.

The accepted package persists the executable design IR as `design-spec.json`.
This bridge reads that JSON directly and carries its facts into the Decide and
Build stages. Do not transcribe it into another intermediate schema and do not
recover facts from HTML/CSS. On the Designer path, the additional persisted artifact is
`.scratch/design_escalation_receipt.json`, because it records that the designer
pass really happened and passed.

`pico-spatial-app-designer` is a lean, host-LLM-orchestrated
Frame→Explore→Plan→Critique→Build→Critique loop. It delivers a three-artifact
package: rationale in `design-doc.md`, executable facts in `design-spec.json`,
and a SpatialUI Web `preview.html` rendered from an exact embedded copy of that
JSON.

## 0. Boundary declaration (read first — it constrains everything below)

| Boundary                                     | Rule                                                                                                                                                                                                                 |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No write-back to the design package          | The bridge only **reads** it; never modify `design-doc.md`, `design-spec.json`, or `preview.html`.                                                                                                                   |
| Terms ≠ enums                                | The design package uses PICO design terminology (WindowContainer Planar, Stage Progressive, TabBar…). These terms are **not equal to** this skill's enums (`ON_PLAIN` / `STAGE_PROGRESSIVE` / window ornaments).     |
| The bridge prepares evidence; Decide commits | Mapping terms to enums, checking legality, and committing to a container / window model all happen in the **Decide** stage using `structure-decisions.md`. The bridge may record leaning evidence, never a decision. |
| JSON is authoritative                        | Read implementation facts from `design-spec.json`. Use `design-doc.md` for rationale and `preview.html` only for visual acceptance evidence. A conflict is a package failure, not permission to choose HTML.         |
| Gate-result consumption                      | Consume a package after either the Designer receipt records `status=designer_passed` with all pre-gates true, or Stage 1 accepts a user-provided executable package as `user_package_passed`. A package that merely exists on disk is not enough.                   |

---

## A. Input: design package fact sources

### A.1 Design package location and pre-gates

The Designer-produced package has this shape:

```
<design-package>/
├── design-doc.md      # §1 Frame · §2 Explore · §3 Plan · §4 Critique(pre-build) · §5 Build manifest · §6 Critique(post-build)
├── design-spec.json   # schema-valid executable design IR; source of truth for code generation
├── preview.html       # SpatialUI Web rendering of the embedded spec (web_design_validation_only)
└── design-assets/
    └── icons/*.svg    # only when custom icon drawing was required
```

For a user-provided package, Stage 1 must confirm that it was supplied with the
request and contains information architecture, page structure, and a state
model, then stage its executable JSON at
`<target>/.scratch/design-spec.json` before recording `user_package_passed`.

`design-spec.json` follows
`pico-spatial-app-designer/assets/design-spec.schema.json` and owns surfaces,
dimensions, theme, assets, node hierarchy, component props, states,
transitions, data cases, and responsive rules. `design-doc.md` is filled from
the designer's template and carries rationale and review evidence:

| Section                      | Contents the bridge reads                                                                                                        |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **§1 Frame**                 | subject, viewer/context, the single job, spatial justification table (affordance + 2D counterfactual per core task), assumptions |
| **§2 Explore**               | ≥3 alternatives, decision matrix, chosen direction + rejection reasons                                                           |
| **§3 Plan**                  | Human-readable summary of `design-spec.json`, signature and layout rationale                                                     |
| **§4 Critique (pre-build)**  | generic-default simulation, hard-check table                                                                                     |
| **§5 Build**                 | coverage manifest (states/transitions/components/bindings/tiers)                                                                 |
| **§6 Critique (post-build)** | independent coverage rebuild, quality-bar table, patch log, **verdict** (`pass` / `changes_requested` / `block`)                 |

**Designer pre-gates (all required on the Designer path):**

| Gate                | Source                      | Pass condition                                                                                        |
| ------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------- |
| Design doc complete | `design-doc.md` §1–§6       | All six sections filled (not placeholders); §3 Plan sizing table, state graph, and components present |
| Design spec valid   | `design-spec.json`          | Schema-valid; IDs are unique and every reference resolves                                             |
| Preview parity      | JSON + `preview.html`       | Embedded JSON is semantically identical; no executable design fact exists only in HTML                |
| Post-build verdict  | `design-doc.md` §6 Critique | The §6 Critique-again **verdict is `pass`** — quality bar met, no active blocking finding             |

> If any gate fails (`design-doc.md` incomplete, invalid/divergent
> `design-spec.json`, or §6 verdict is `changes_requested` / `block`), **do not
> run this bridge and do not fall back to HTML or shallow text extraction to
> keep generating**:
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
    "designSpecValid": true,
    "previewMatchesSpec": true,
    "postBuildVerdict": "pass"
  }
}
```

### A.2 Artifact fields → downstream facts

| Source                                        | Facts provided                                                                                    | Downstream use                                                        |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `design-spec.json.experience`                 | subject, user/context, single job, space/form, signature                                          | product and spatial intent                                            |
| `design-spec.json.surfaces`                   | surface type, roots, final default/min/max dp or meter dimensions, placement                      | container evidence, window intent, constraints                        |
| `design-spec.json.nodes`                      | exact hierarchy, layout ownership, SpatialUI components/props/events, text, media, domain visuals | regions, repeated structures, JSON → Compose inventory                |
| `design-spec.json.theme`                      | immutable 16-role references, brand tokens, type, spacing                                         | native `PicoTheme`, app tokens, typography, spacing ownership             |
| `design-spec.json.states/transitions/actions` | initial/visible states, per-surface roots, triggers, local mutations, confirmation contracts      | typed UI state, ViewModel events, navigation/window behavior          |
| `design-spec.json.dataCases`                  | normal, fallback, and error samples                                                               | domain/UI state requirements and test cases                           |
| `design-spec.json.responsiveRules`            | bounded per-node overrides                                                                        | adaptive Compose layout                                               |
| `design-spec.json.assets`                     | asset kind, source, purpose, alternative text                                                     | resource acquisition and app resources                                |
| `design-doc.md` §1/§2/§4/§6                   | spatial rationale, rejected alternatives, assumptions, critique verdict                           | decision evidence and acceptance trace                                |
| `preview.html`                                | accepted rendered appearance and interaction behavior from the embedded spec                      | visual comparison only; never an independent source for codegen facts |

For `assets[].kind: "icon"`, follow the source rather than approximating it:

- `icon70://7.0/<name>` resolves through the Designer's
  `scripts/icon-catalog.mjs`; materialize only referenced catalog vectors.
- `design-assets/icons/<resource-name>.svg` is an accepted custom drawing.
  Read `icon-drawing.md`, preserve its path geometry and transparent holes in a
  matching Android VectorDrawable, and keep the SVG unchanged as the design
  authority.
- User/Figma, app, and SDK assets retain their original authority and are not
  replaced by a catalog or custom approximation.

`preview.html` has scope `web_design_validation_only`; it must not be treated as
evidence of PICO physical size, device color shift, or implementation
structure. The authoritative source for those facts is `design-spec.json`.

### A.3 Spatial Design JSON → Compose conversion (`intent_only`)

For `input_mode=intent_only`, component conversion is a hard part of the
designer bridge rather than a later visual interpretation.

1. Read every node in `design-spec.json`.
2. Inventory each node with `kind: "spatialui"` and its component, props,
   bindings, events, children, visibility, and surface hierarchy.
3. Resolve each declared component through `spatialui-web-to-compose.md`.
4. Carry one in-memory conversion row per node:

   ```text
   node_id | web_component | compose_api | props_and_state | callback | hierarchy
   ```

5. Reconcile the inventory with the preview only as a parity check. A
   preview-only product component is a blocking package defect; do not add it to
   the inventory until the designer repairs `design-spec.json`.

Conversion preserves semantics, not Web syntax:

| JSON evidence                                                   | Compose consequence                                                                            |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| node `props`, `bindings`, `visibleInStates`                     | typed UI state and explicit visibility                                                         |
| node `events` + matching transition                             | callbacks dispatched to the state holder/ViewModel                                             |
| node `children`                                                 | composable content lambdas                                                                     |
| convenience string/list props                                   | explicit child composables/DSL items                                                           |
| `sui-tab-bar`, `sui-toolbar`, `sui-subwindow`, `sui-augment`    | root/window-level sibling; never an in-page `Row`/`Box` imitation                              |
| modal/menu/popup/coachmark/snackbar components                  | corresponding SpatialUI window/host pattern with explicit visibility/dismissal                 |
| node `layout`, `appearance`, `theme`, and `responsiveRules`     | dp/token-based Compose layout and styling; Web CSS pixels are not copied                       |
| `domain_visual.rendererKey`, purpose, props, bindings, children | a deliberate app implementation preserving the declared semantics, data, dimensions, and style |

**Gate:** every declared `sui-*` component resolves to a mapped Compose API.
Because the current SpatialUI Web catalog has production counterparts, a
mapped component cannot fall through to `// TODO(missing-component)` or
hand-built primitives. If a component is unknown, stop and repair the
design/mapping before Build.

---

## B. PICO term → container enum mapping table

Read container facts from `design-spec.json.experience.space/form` and
`surfaces[].type`, then turn them into **container evidence** for the Decide
stage. Use `design-doc.md` only for the spatial rationale. Legal enums:
`ON_PLAIN` / `IN_VOLUME` / `STAGE_MIXED` / `STAGE_PROGRESSIVE` / `STAGE_FULL`.

| Design package container fact (`experience` + `surfaces`)                                         | Container enum (Decide-stage evidence) | Space State | `spatial_features` cues                                                       |
| ------------------------------------------------------------------------------------------------- | -------------------------------------- | ----------- | ----------------------------------------------------------------------------- |
| WindowContainer · Planar (Shared Space, depth locked to 640dp, 2D-dominant; may embed smaller 3D) | `ON_PLAIN`                             | Shared      | No passthrough/skybox; small 3D uses `model_3d` (`SpatialModelView`)          |
| WindowContainer · Volumetric (Shared Space, scalable cube, contains larger 3D)                    | `IN_VOLUME`                            | Shared      | `model_3d`; still no passthrough/skybox; anchor/env_mesh **forbidden**        |
| Stage · Mixed (immersion tier 0, passthrough real-world background)                               | `STAGE_MIXED`                          | Full        | `passthrough` (**only** `STAGE_MIXED`); may use `anchor`/`env_mesh`/free 3D   |
| Stage · Progressive (immersion 0–100, may include skybox / virtual environment)                   | `STAGE_PROGRESSIVE`                    | Full        | `skybox` (only `STAGE_PROGRESSIVE`/`STAGE_FULL`); may use `anchor`/`env_mesh` |
| Stage · Full (immersion 100, fully immersive with no real background)                             | `STAGE_FULL`                           | Full        | `skybox`; no passthrough; may use `anchor`/`env_mesh`                         |

> A `pico-spatial-app-designer` package leans toward a **Planar
> WindowContainer** (`ON_PLAIN`) for most windowed apps, but the designer now
> covers any form. Read the form from JSON and confirm its rationale in §1
> Frame: a Volumetric leaning appears when a 3D subject must be inspected in the
> round, and a Stage leaning (`STAGE_MIXED` / `STAGE_PROGRESSIVE` /
> `STAGE_FULL`) when the design explicitly requires passthrough or a virtual
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

Read layout and attachment facts from `design-spec.json.surfaces`,
`states[].surfaceRoots`, and the `nodes` hierarchy (side navigation, tabs,
toolbars, popups, subwindows, master/detail panes). Use the design document for
placement/lifecycle rationale, then turn the facts into **window model
evidence** for the Decide stage. Legal window model enums: `single_panel` /
`single_panel_with_popup` / `sidebar_content` / `master_detail` /
`window_plus_subwindow` / `multi_window`.

| Design package layout/attachment fact                                                  | Window model (Decide-stage evidence) | Key criterion                                                     |
| -------------------------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------------------------- |
| Only in-place controls / `None`, single main window                                    | `single_panel`                       | No independent overlay, no second persistent surface              |
| Transient menu / contextual overlay (overlay, not persistent)                          | `single_panel_with_popup`            | Overlay in tone; **not** a persistent subwindow                   |
| Side rail (side navigation) + content region                                           | `sidebar_content`                    | `Row(sidebar, content)` inside one window                         |
| List → detail (list + detail as two persistent panes side by side)                     | `master_detail`                      | Two persistent panes belong to the **same** coordinated window    |
| Persistent subwindow (side-attached, height-locked filling the host, shared lifecycle) | `window_plus_subwindow`              | One launcher; auxiliary window shares the main window's lifecycle |
| Independent launcher / independent lifecycle / independently placed multiple windows   | `multi_window`                       | **Must** have disconnected-surface evidence (see below)           |

**`window_chrome_ornaments[]` (docked attachment) mapping:** when `TabBar` /
`Toolbar` / `Subwindow` nodes act as docked attachments, record them as
`window_chrome_ornaments[]` entries (`type ∈ TabBar / Toolbar / Subwindow`). They
are **sibling nodes of the main window**, not page child nodes (do not stuff them
into `windows[].children` or `regions[]`).

```json
"window_chrome_ornaments": [
  { "type": "TabBar", "placement": "Top", "note": "JSON node + rationale: top-center persistent navigation, sibling of main window" },
  { "type": "Toolbar", "placement": "Bottom", "note": "JSON node + rationale: bottom-center action bar" }
]
```

**Hard gate for multi_window (consistent with `structure-decisions.md`'s
`overlay_vs_multi_window`):**

| Situation                                                                                                                                                                         | Result                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| JSON has separate surfaces and the design rationale explicitly states "independent placement / independent size / independent lifecycle / separate bounds / independent launcher" | Disconnected-surface evidence holds → can support `multi_window`                                 |
| Design package only describes overlay / popup / dropdown / anchored / attached-to-main-panel                                                                                      | Judged **not** `multi_window` (would be BLOCKed); should land in `single_panel_with_popup`       |
| No disconnected evidence at all                                                                                                                                                   | `multi_window` is BLOCKed; state the missing evidence explicitly and hand it to the Decide stage |

> The bridge must carry both the JSON surface/node evidence and the exact design
> rationale about "independent surface vs overlay" so the Decide stage's
> disconnected-surface judgment has grounds. Ownership of the decision: the
> final window model decision belongs to the Decide stage, via the
> Subwindow-vs-`multi_window` escalation in `structure-decisions.md`.

---

## D. Surface sizing methodology → window constraints / root_fill / spacing_ownership

### D.1 JSON surfaces → window size constraints

Read the default / min / max (dp), aspect ratio, and resize range from the
`design-spec.json.surfaces` entries, and map them into the layout window size
constraints (for the Build stage to use; the bridge first records sizing intent
in `layout_intent`).

| JSON surface sizing fact                                               | Layout contract window constraint | Legal domain / floor                                                             |
| ---------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------- |
| Planar default (e.g. 1280×720dp official baseline, content-calibrated) | Window default size intent        | Legal domain 320×180dp ~ 2700×1800dp; depth fixed at 640dp (not configurable)    |
| Planar min / max (the resize range)                                    | Window min / max intent           | Falls within the legal domain                                                    |
| Hit target floor                                                       | Interaction hit-region constraint | ≥ 56×56dp                                                                        |
| Body font floor                                                        | Body readability constraint       | ≥ 12dp                                                                           |
| Aspect-ratio policy                                                    | Aspect-ratio intent               | 16:9 not mandatory; choose by content (list/timeline/comparison/reading/console) |

> Prohibition: **do not** let codegen fall back to 1600×900, and **do not** treat
> 1280×720 as the final fixed value for all projects. Sizes come from the
> content-derived JSON surface entries; the bridge only transports, it does not
> guess. (See the designer's
> `pico-spatial-app-designer/references/window-sizing.md` for the chain that
> produced them.)

### D.2 JSON theme + nodes → root_fill + spacing_ownership

Read the padding tokens (Small/Regular/Medium/Large = 8/16/24/32 dp) and the
layout/appearance values from `design-spec.json.theme` and `nodes`. See
"Spacing ownership & root fill" in `layout-inference.md`: every inset/padding/gap
must have a **unique owner node**, and `root_fill` must be set explicitly.

| JSON fact                                                                              | Maps to                         | Rule                                                                   |
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
    "note": "design-spec node padding: root fill_window, inset owned by inner content, not root" },
  { "id": "region_gap", "value_dp": 16, "owner": "inner_content_column", "kind": "vertical_gap" },
  { "id": "card_padding", "value_dp": 16, "owner": "content_card", "kind": "padding" }
]
```

### D.3 JSON theme colors → native roles plus app-owned colors

Read the complete 16-role object from
`design-spec.json.theme.colorScheme`.
Every entry must preserve its same-name SpatialUI Vibrant role. Do not override
or reconstruct the native `ColorScheme`; use plain `PicoTheme { ... }`.

Custom design colors live in `theme.brandColors` and are app-owned. Carry them
separately (grounded in
`spatial-ui-design-style/references/tokens.md §7`):

| JSON theme fact                        | How to carry it                    | Codegen consequence                                             |
| -------------------------------------- | ---------------------------------- | --------------------------------------------------------------- |
| Native `ColorScheme` role              | Same-name Vibrant role             | Read through `PicoTheme.colorScheme.<role>` without overriding it |
| Custom brand/decorative color          | Named Kotlin color literal/token   | Use directly; never assign it to a native role                  |
| Semantic status needing a custom color | App-owned token plus non-color cue | UI shows the label and cue without changing SDK status tokens   |

Legal role names (16 total): fill
`fillPrimary/fillSecondary/fillTertiary/fillLight`, text
`labelPrimary/labelPrimaryLight/labelSecondary/labelTertiary/labelQuaternary`,
fixed semantic `error/alert/passable/interaction`, state
`lightenHover/lightenPressed`, and `dividerLine`.

> **Theming rule.** Never construct or copy `ColorScheme` to replace native
> roles. Collect custom design values into one `object <App>Colors` under
> `ui/theme/`; they may be Kotlin `Color(0x…)` literals or resources as described
> in `figma-mapping.md §7.2`. Never emit a solid color / `fillPrimary` on the
> window root.

Pass every custom `brandColors` value to Verify as
`--design-color <token>=<#hex>`. Native roles are not passed because the
verifier requires them to remain unchanged. If the package specifies no custom
colors, pass `--no-design-colors`.

---

## E. Implementation mapping receipt and JSON-to-App fidelity

After Build, write `<target>/.scratch/design_implementation_map.json`. This is a
verification-only receipt: Build never reads it, and it must describe facts
observed in the finished app. `check_design_fidelity.py` compares those facts
with the current `design-spec.json` before Gradle work begins.

The receipt has four responsibilities:

1. Pin the exact design revision with the raw-file SHA-256.
2. Record the implementation-side contract projection. The checker compares it
   recursively with the authoritative JSON and reports exact mismatch paths.
3. Map every contract entity to a source file, symbol, and concrete source token.
4. Prove complete coverage. Missing, duplicate, unknown, stale, or outside-target
   mappings are hard failures.

```json
{
  "schema_version": 1,
  "design_spec": {
    "path": "design-spec.json",
    "sha256": "<sha256 of the current file>"
  },
  "source_mappings": [
    {
      "file": "app/src/main/java/example/store/AppShelf.kt",
      "symbols": ["AppShelf", "WideAppGrid", "CompactAppGrid"],
      "evidence": ["Arrangement.spacedBy(16.dp)", "chunked(2)"],
      "design_refs": ["node:app-shelf", "responsive-rule:compact-store"]
    }
  ],
  "implementation": {
    "initialStateId": "discover",
    "surfaces": {},
    "nodes": {
      "app-shelf": {
        "kind": "domain_visual",
        "rendererKey": "app-shelf",
        "props": {
          "featuredCount": 1,
          "columns": 4
        },
        "layout": {
          "mode": "grid",
          "columns": 4,
          "gapDp": 16,
          "overflow": "hidden"
        }
      }
    },
    "states": {},
    "transitions": {},
    "actions": {},
    "responsiveRules": {},
    "dataCases": ["error", "fallback", "normal"],
    "assets": {}
  }
}
```

The implementation projection is deliberately narrower than the design IR:

| Section          | Compared implementation facts                                                                                                         |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| initial state    | `initialStateId`                                                                                                                      |
| surfaces         | every field except `id`                                                                                                               |
| nodes            | kind, component/renderer, content/asset, props, bindings, events, layout, appearance, text style, children, visibility, accessibility |
| states           | surface roots and entry action                                                                                                        |
| transitions      | from/to, trigger, confirmation                                                                                                        |
| actions          | executable type, transition, binding, value, payload; rationale-only `purpose` is excluded                                            |
| responsive rules | surface, condition, every node override                                                                                               |
| data cases       | exact case-name coverage                                                                                                              |
| assets           | kind, source, and alternative text; rationale-only `purpose` is excluded                                                              |

For every node whose `appearance` declares a fill, the mapped Kotlin source
must place
`// design-style: design-surface <node-id>` immediately before the corresponding
`.background(...)` or content `Card(...)`. Structural `layout` and
`domain_visual` nodes have no such call, and each node ID may identify at most
one background implementation. The design-style verifier performs the reverse
check as well: an app-authored surface call with no valid design-node marker,
or a repeated marker, fails. App-authored `.backgroundMaterial(...)`,
`.border(...)`, and `BorderStroke(...)` are always rejected for design-package
restoration.

Required reference names are
`state-model:initial`, `surface:<id>`, `node:<id>`, `state:<id>`,
`transition:<id>`, `action:<id>`, `responsive-rule:<id>`,
`data-case:<name>`, and `asset:<id>`. Each must appear exactly once across
`source_mappings[].design_refs`.

This gate catches semantic drift that legality checks cannot: for example,
`app-shelf.layout.mode=grid`, `columns=4`, and a compact override of
`columns=2`, `overflow=scroll` cannot be recorded as a single `row` without a
hard diff. Source anchors prevent a receipt from surviving file/symbol removal.
They do not prove arbitrary Kotlin behavior or pixel output, so Stage 5c still
compares the running app with the accepted preview or visual source.

---

## F. Boundaries and non-goals

| Item                                | Rule                                                                                                                                                                                                                                                             |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No write-back to the design package | The bridge only reads the design package and writes outputs to `.scratch/`; it does not modify `design-doc.md`, `design-spec.json`, or `preview.html`.                                                                                                           |
| No second design IR                 | Consume the accepted `design-spec.json` directly; do not produce another code-generation layout JSON or treat the Web DOM/CSS as an alternate source. The post-Build implementation mapping receipt in §E is verification-only and never feeds generation.       |
| No final decision                   | The **final commitment** to container / window model happens in the Decide stage; the bridge only prepares evidence.                                                                                                                                             |
| No new `input_mode`                 | The bridge is a `references/` document; it occupies no `input_mode` and adds no new one.                                                                                                                                                                         |
| No new top-level schema fields      | It only writes existing fields of the existing three-artifact schemas.                                                                                                                                                                                           |
| Block if a pre-gate fails           | On the Designer path, require all existing pre-gates and `status=designer_passed`. On the user-package path, require Stage 1 `user_package_passed`. Otherwise the package must not be consumed.                                                           |

### F.1 Comparison against legacy shallow extraction

| Dimension           | Shallow extraction (no design package)        | Design package bridge (this doc)                                                                        |
| ------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `confidence.layout` | ≈ 0.35                                        | ≥ 0.8 (from a complete design package with §6 verdict = pass)                                           |
| Surface sizing      | None (codegen easily guesses wrong)           | `surfaces` provides exact default/min/max dimensions                                                    |
| Spacing ownership   | Missing, prone to double padding              | node layout values preserve one explicit spacing owner                                                  |
| Component anatomy   | None                                          | `nodes[kind=spatialui]` drives the complete Compose conversion inventory                                |
| Color               | Guessed or scattered hex values               | Native roles stay unchanged; `theme.brandColors` maps to named app-owned tokens                         |
| Traceability        | Weak                                          | every implementation fact points to a stable JSON ID/path and can be compared with the accepted preview |

### F.2 Validation-consistency self-check

| Checker                     | What the bridge must guarantee                                                                                                                                           |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `check_handoff_receipts.py` | The accepted route is preserved: either a valid `designer_passed` receipt or `user_package_passed` with a staged JSON object                                             |
| `scan_implementation.py`    | Feature legality survives into code and the expanded SpatialUI vocabulary recognizes all mapped production components                                                    |
| `check_design_fidelity.py`  | The current design hash, implementation facts, full entity coverage, and source anchors match; running visual output remains an LLM/device review                        |
| `verify-design-style.sh`    | Every custom design color is passed as `--design-color`; generated code preserves native roles and contains each app-owned token value |
