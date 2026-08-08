# Visual System Spec · <project name>

> Role: `visual_designer` (visual direction) and `spatial_design_system_designer` (component synthesis, data trust reconciliation) | Workflow stage(s): `visual_direction` → `composition_synthesis` → `design_system` (layout / component / visual / data-trust facts) | Upstream inputs: selected concept, experience architecture, research evidence, quality contract, state graph, approved visual reference | Downstream recipients: Prototype / Frontend Engineer, QA, Design Lead
>
> This document carries this role's **LLM reasoning information** and **direct description of outputs**. It is not bound to any JSON Schema or validator error codes; mandatory gates are expressed through this document's structured Markdown required tables, evidence anchors, and the `block` status.

## 0. Reasoning Guidance (how this role reasons)

- **Only make visual and design-system decisions**: visual hierarchy, typography, color semantics, materials, component anatomy, responsive behavior, motion fallback. Do not define task priorities or state flows, and do not substitute for human approval.
- **Visual direction comes first**: before freezing design-system facts, generate and compare 2–3 spatial visual directions; the selected direction becomes the "approved visual reference." Subsequent design-system sections record that direction and do not reinvent the aesthetic. A direction that only swaps color / theme / icons / copy is not substantially different.
- **The visual language is derived from project semantics**: brand personality, environment, mood, risk, content density, physical metaphor, domain symbols; different domains cannot simply swap colors, and at least two rejected visual directions must be recorded.
- **Visuals and components are the source of truth for the implementation handoff**: express them with structured data (dimensions, ratios, Grid, state tables), **not prose**. Prose like "magenta + square border = critical" cannot be consumed stably by engineering. Any design change must be reflected in the delivery facts (swapping a hex / family must show up in the structured fields).
- **Components are derived from tasks, data, and interactions**: domain knowledge only provides terminology and rules, not a catalog that must be reused. Each core component declares its source task, source data, purpose, anatomy (including layout and sizing), data bindings, variants, states, layout role, and accessibility.
- **Data is runtime fidelity**: display-only fields carry human-readable copy; status/enum fields are translated via the color-semantic `label` and never echo the machine enum.
- **Prohibitions**: presenting project-derived rules as official PICO rules; scoring by visual similarity to a reference case; disguising review metadata such as design theses / layer names / component classifications / skeleton region names as end-user copy.

## 1. Direct Description of Outputs

This role delivers: **visual direction candidates and the selection (approved visual reference) → visual language (tokens / typography / color semantics / materials) → component specs (structured anatomy) → data display and semantic contract**. Each section below is the structured description of these outputs.

## 2. Spatial Visual Direction Candidates (2–3)

> Each direction defines a spatial thesis, first-view composition, container relationships, depth plan, information hierarchy, interaction cues, spatial value, Dashboard risk, and preview/render instructions. Directions that only swap color are rejected.

| Direction | Spatial Thesis | First-View Composition | Container Relationships | Depth Plan | Information Hierarchy | Interaction Cues | Spatial Value | Dashboard Risk |
|---|---|---|---|---|---|---|---|---|
| Direction 1 | | | | | | | | |
| Direction 2 | | | | | | | | |

- **Selected direction (approved visual reference)**: <name + selection rationale; must be confirmed by a human or approved through a structured design-effect review>
- **Rejected visual directions (≥2)**: <direction + rejection rationale>

## 3. Design Tokens (the single contract between design and code)

> tokens, typography, color semantics, and materials are the source of truth for styling that downstream implementers consume verbatim; values must be precise (colors in hex).

| Token | Value | Semantics / Usage |
|---|---|---|
| accent | | Accent color |
| surface | | Neutral material surface |
| brandPrimary | | Brand primary color |
| radius | | Corner radius |
| spacing | | Spacing baseline |

### 3.1 Typography hierarchy

> Each level: `family (grotesk/sans/mono/serif) · size · line · weight`. Implementers infer the display/title/metric/body/caption roles by descending size + mono for domain neutrality, and do not rely on specific key names (domain-custom key names such as asset/decision can also be consumed).

| Role / Key | family | size | line | weight |
|---|---|---|---|---|
| display | | | | |
| title | | | | |
| metric | | | | |
| body | | | | |
| caption | | | | |

### 3.2 Color semantics colorSemantics (dual-channel: color + shape)

> Each item: `color(#hex) · shape · label · desc · aliases[]`. `shape` takes `circle/square/triangle/dashed/diamond` (a color-independent redundant encoding, required for accessibility); `aliases[]` lists all aliases of that semantic in the data (including localized copy, such as "Out of Stock" or "Pending Lock") for machine matching; `label` is the human-readable copy shown in the runtime UI (such as "Critical"), which replaces the visible text when a data value is matched rather than echoing the machine enum.

| Semantic Key | color (#hex) | shape | label (human-readable copy) | desc | aliases[] (machine matching, including Chinese aliases) |
|---|---|---|---|---|---|
| | | circle/square/triangle/dashed/diamond | | | |

### 3.3 Materials

> Each item: `desc · treatment(matte/glass/opaque) · glassStyle(Thin/Regular/Thick/Thickest/none) · opacity`. The glass look is a **system capability of the PICO spatial platform**: the PICO Spatial SDK provides four glass background material tiers `Thin/Regular/Thick/Thickest` (increasing degree of blur behind the content, applied via `Modifier.backgroundMaterial(...)`; for a WindowContainer it is controlled by `enableMaterialBackground` and enabled by default). When `treatment=glass`, the `glassStyle` tier must be specified, and the implementer calls the system `Material.<tier>` directly at handoff. `matte`→ a solid card. The Web preview using `backdrop-filter: blur+semi-transparency` is only a preview approximation of the four-tier system glass, and is not equal to the real material on a PICO device.
>
> **Component-level backgrounds are optional, and a custom color and glass are mutually exclusive**: a component inside a window can have no background (none, falling directly onto the parent container), a custom color background (customColor, with the color set by the component, not limited to a solid color), **or** a glass background material (the four glassStyle tiers), but **the same component must not stack a custom color + glass at the same time**—pick one. The glass background material is **only available inside a WindowContainer**. Which one a component uses is declared in the "background" row of §5 "Anatomy · Internal Metrics".

| Material Name | desc | treatment | glassStyle | opacity |
|---|---|---|---|---|
| | | matte / glass / opaque | Thin / Regular / Thick / Thickest / none | |

### 3.4 Scale (spacing / corner radius / icons, unified baseline)

> Component metrics must reference a unified scale and must not each write their own set of magic numbers. Spacing is based on 4/8dp. All padding / gap / radius / iconSize in the §5 component metrics table and the §5.0 in-window layout should reference the tier names here or their dp values.

| Scale | Tier → Value (dp) | Usage |
|---|---|---|
| spacing | xs 4 / s 8 / m 16 / l 24 / xl 32 | Component padding, gap between components, margin |
| radius | s <value> / m <value> / l <value> | Buttons, cards, containers (must fall within the §8 PICO corner-radius spec) |
| iconSize | s <value> / m <value> / l <value> | Status icons, action icons, decorative icons |

## 4. Environment Adaptation Spec (hard spatial constraints)

- **No large blocks of high-saturation color in dark environments.**
- **Color does not carry semantics on its own**: color + shape/text dual-channel is mandatory.
- **Minimum font size and contrast at wearing distance**: <value>
- **Readability on glass / semi-transparent backgrounds**: <contrast handling rules; the glass background material is only available inside a WindowContainer, and Stage/3D scenes must provide a separate backing>
- **Vibrant Style (readability on passthrough/complex backgrounds)**: <a dynamic color-mixing system capability of PICO SpatialUI that adjusts element brightness in real time based on background brightness, used to keep passthrough/MR or highly dynamic backgrounds readable; app-level `com.pico.spatial.ui.isVibrant` toggle (on by default), with 9 tiers from darkest→ultralight. **Limitation: single color only, no image/gradient support**—regions containing an image/gradient must switch to a solid backing. Declare which panels/text in this project enable Vibrant and at which tier>
- **Spatial state and background controllability**: <in Full Space the background is controllable (a dark solid base is possible); in Shared Space / MR the passthrough background is not controllable, and key content must use a thicker glass tier, Vibrant, or a solid backing>
- **Environment adaptation**: <visual adjustment strategy for bright / dark / outdoor and other environments>

## 5. Component Definition Spec (structured anatomy, no prose)

> Each core component declares: source task, source data, purpose, layout role, priority, anatomy (layout + sizing), data bindings, variants, states. The component description must contain explicit dimensions (ratio or fixed value) and internal structure.
>
> **Structure is incompressible**: the "Component" block below must be fully copied for each core component. Do not merge multiple base fields into one row, do not compress `anatomy.layout` / `sizing` / `metrics` into a field value, and do not rewrite `renderSpec` / `dataBindings` / `variants` / `states` as untitled path strings or state enums. The shared state table can only supplement, not replace, a component's dedicated state table. Stage / 3D components only swap Grid for world anchors, local coordinates, orientation, and metric ranges, but the 8-section structure must still be preserved.

### 5.0 Window structure and in-window layout (structure diagram + dashed boxes, required)

> Visual design must first make clear "what the window looks like and how things are arranged inside it," and only then drop down to individual components. This section carries the **window-level** structure diagram; the spatial placement geometry (anchor/x/y/w/h/z, attachment docking relationships) is authoritative in interaction spec §14, and this section only visualizes and measures the in-window 2D layout. Copy this block for each primary WindowContainer. Window dimensions must reference the PICO methodology result in interaction §9 (default / min / max, content area, reflow), and must not define a separate window size in the visual stage.

**Window shell**

| Field | Content |
|---|---|
| Window / container name | <reference the name in the container list of interaction spec §7.2> |
| form | Planar / Volumetric (Planar depth locked at 640dp) |
| Logical dimensions | <default width × height dp, referencing the PICO methodology result in interaction spec §9, not self-invented> |
| min / max | <minimum / maximum content size or window size, referencing interaction §9; note the corresponding Compact / Constrained / Large> |
| Content safe inset contentInset | <top/right/bottom/left dp, referencing §3.4 spacing> |
| Docked attachment | <TabBar top center / Toolbar bottom center / Subwindow side, etc., referencing interaction §8; note whether it occupies space outside the main content boundary> |

**In-window layout structure diagram (ASCII; solid boxes = window/region boundaries, dashed boxes `┈`/`╌` = component placeholders)**

> The structure diagram must annotate: ① each region name and its embedded component names; ② the spacing tier between regions (referencing §3.4); ③ component placeholders are shown with dashed boxes, and solid boxes indicate window / region container boundaries.

```
┌──────────────────────────────────────────────┐ ← WindowContainer <name> <width×height dp>
│  contentInset: <m 16dp>                        │
│  ┌────────────────────────────────────────┐   │
│  │ Region A: <header / primary metric>       │   │ ← row1  height <dp>
│  │  ┌╌╌╌╌╌╌╌╌╌╌╌╌┐   ┌╌╌╌╌╌╌╌╌╌╌╌╌┐        │   │
│  │  ┊ Component<X> ┊   ┊ Component<Y> ┊        │   │ ← component placeholder (dashed box)
│  │  └╌╌╌╌╌╌╌╌╌╌╌╌┘   └╌╌╌╌╌╌╌╌╌╌╌╌┘        │   │
│  └────────────────────────────────────────┘   │
│         ↕ gap <m 16dp>                          │
│  ┌──────────────────┬─────────────────────┐   │
│  │ Region B: <main list> │ Region C: <details>   │   │ ← row2  2 columns <left:right ratio>
│  │  ┌╌╌╌╌╌╌╌╌╌╌╌┐   │  ┌╌╌╌╌╌╌╌╌╌╌╌┐      │   │
│  │  ┊ Component<Z> ┊   │  ┊ Component<W> ┊      │   │
│  │  └╌╌╌╌╌╌╌╌╌╌╌┘   │  └╌╌╌╌╌╌╌╌╌╌╌┘      │   │
│  └──────────────────┴─────────────────────┘   │
└──────────────────────────────────────────────┘
       ←── gap column spacing <l 24dp> ──→
```

- **Grid definition**: <number of rows and columns, height of each row / width of each column (dp or ratio), region spans, main-axis/cross-axis alignment>
- **Region → component mapping**: <each region name → the component placed in it (must correspond one-to-one with the component blocks below; no orphan regions, no unplaced components)>
- **Region spacing**: <each region gap referencing a §3.4 spacing tier>
- **Reflow**: <how regions collapse / rewrap / scroll internally under Large / Compact / Constrained, echoing interaction §9's default / min / max; must not scale text and hit targets as a whole>

### Component: <component name>

| Field | Content |
|---|---|
| Source task derivedFromTasks | <task ID, must actually exist in the task model> |
| Source data derivedFromData | <data entity / path> |
| Purpose | <which decision this component serves> |
| Layout role layoutRole | <primary_hero / primary_explore / critical_primary / supporting / status …> |
| Priority | primary / secondary |
| Runtime role runtimeRole | <primaryMetric / decisionList / statusBadge / control / navigation / detailPanel …(describes behavior, not visual decoration)> |

**Anatomy · Layout (anatomy.layout, Grid mode)**

> Solid boxes = component / sub-region boundaries, dashed boxes `╌` = internal element (icon / text / value / button) placeholders. Annotate the relative position of each element and the internal spacing.

```
┌─────────────────────────────┐
│ ┌╌╌╌╌┐ <Region A: title/primary metric>   │  ← row 1   ┊icon┊ + text, gap <s 8dp>
│ └╌╌╌╌┘                       │
├──────────────┬──────────────┤
│ <Region B>    │ <Region C>    │  ← row 2 (2 columns, column spacing <m 16dp>)
└──────────────┴──────────────┘
```

- **Grid definition**: <number of rows and columns, span of each region, alignment>

**Anatomy · Sizing**

| Tier | Width × Height (ratio or fixed value) | Notes |
|---|---|---|
| Regular | | Corresponds to the owning window's default / Large; must fall within the content area |
| Compact | | Corresponds to the owning window's Compact / min; note collapse, rewrap, or internal scrolling |
| Constrained | | If applicable, describe the minimum usable structure; if not applicable, state the rationale for switching to Sheet/Dialog or hiding |

**Anatomy · Internal metrics (metrics, dp/sp, no prose, reference the §3.4 scale)**

> The icons, text, corner radii, padding, element spacing, and strokes inside a component must be given explicit values (referencing the §3.4 tiers or dp/sp directly), and cannot merely say "icon a bit large" or "leave some margin." Font sizes reference the §3.1 typography roles; icons / spacing / corner radii reference §3.4. All metrics must, together with the `sizing` above, satisfy the content-area constraints of the owning window's default / min / max; text and hit targets must not be scaled as a whole under Compact / Constrained.

| Metric | Value | Source / Notes |
|---|---|---|
| background | none / custom color customColor`<#hex>` / glass glassStyle`<tier>` | **Optional, and custom color vs. glass are pick-one, mutually exclusive**: none=no background (falls directly onto the parent container); customColor=component's own color (referencing a §3.2/§3.3 token or #hex, not limited to a solid color); glass=one of the four §3.3 `glassStyle` tiers (`Modifier.backgroundMaterial`, only available inside a WindowContainer). A custom color + glass must not be stacked at the same time. |
| Corner radius radius | <§3.4 radius tier or dp; must fall within the §8 PICO corner-radius spec> | |
| Padding | <top/right/bottom/left dp, referencing §3.4 spacing> | |
| Internal element gap | <icon↔text, row↔row, item↔item gap, referencing §3.4> | |
| Stroke | <width dp + color referencing a §3.2 semantic color / token> | |
| Icon iconSize | <§3.4 iconSize tier or dp; note the tintable semantic color> | |
| Primary text | <referencing a §3.1 typography role, e.g. title: size/line/weight> | |
| Value / secondary text | <referencing a §3.1 typography role, e.g. metric / caption> | |
| Minimum hit target hitTarget | <dp, must be ≥ the §8 PICO minimum interaction hit target> | |

**Render elements renderSpec.elements[] (ordered visible elements)**

| id | Visible label | Element type | Binding bind | State / semantic role |
|---|---|---|---|---|
| | | | | |

**Data bindings dataBindings[]**

| Source path | Target element / property | fallback behavior | display-only / semantic |
|---|---|---|---|
| | | | display-only / semantic |

**Variants**: <list variants and their differences>

**States** (rebuilt around gaze)

| State | Trigger | Visual params (fill/stroke/opacity/blur/material) | Size change | Motion continuity (duration ms + easing, aligned with the interaction doc) | Accessibility alternative |
|---|---|---|---|---|---|
| default | No interaction | | | | |
| hover / focused | Eye looks at it | Clear highlight (stroke/brighten/micro-scale ≤1.05x) | ≤1.05x | | |
| pressed / selected | Hand pinch | Press feedback (sink/color change) | | | |
| disabled | Unavailable | Reduced contrast but readable, no highlight on gaze | | | Non-color label |
| loading | Async wait | Skeleton screen / progress | | | |
| empty | No data | Guidance copy + illustration | | | |
| error | Load/validation failure | Includes retry entry | | | |
| overflow | Exceeds container | Truncation / scroll / collapse rule | | | |

- **State stacking precedence**: `focused + selected`, `hover + disabled`, `loading + focused` <define combined behavior>

<!-- Copy the "Component" block above for each core component -->

### 5.1 Component structure completeness checklist (before coverage reconciliation)

> Verify the fixed structure component by component. If any column for any core component is "no" or the corresponding section anchor is missing, this stage's verdict can only be `block`; "the information already appears elsewhere," "shared states are already defined," or "limited space" must not be used as a reason to pass.

| Core Component | Base fields on separate rows | anatomy.layout | sizing | metrics | renderSpec | dataBindings | variants | states + stacking precedence | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| | yes / no | yes / no | yes / no | yes / no | yes / no | yes / no | yes / no | yes / no | pass / block |

### 5.2 Coverage reconciliation (performed after structure is complete)

#### Table A · Data entity → component binding

| Data entity / decision variable (referencing the UXR domain model) | Timeliness | Consuming component.dataBinding | Presentation / semantic method | Gap handling (add binding / intentionally not presented + rationale) |
|---|---|---|---|---|
| | | | | |

#### Table B · Task decision output → component interaction

| Task ID · decision output | read-only / actionable | Consuming component + `renderSpec` element + interaction behavior | Gap handling |
|---|---|---|---|
| | | | |

#### Table C · Exhaustive sub-states of primary components

| Primary component → sub-component | Runtime sub-states (loading / buffering / dragging or editing / empty / error / boundary-disabled and project-specific states) | Corresponding render primitive | Data binding |
|---|---|---|---|
| | | | |

## 6. Material and depth semantics

- **Material / glass tier / opacity per layer**: <define>
- **Depth cues**: <convey hierarchy with "near = important" rather than color stacking alone; PICO depth is Z-axis front-to-back layering, 2D content is always on the back of the "box," Planar depth locked at 640dp>
- **Mapping of system glass tiers to depth layers**: <declare which system glass tier (Thin/Regular/Thick/Thickest) or solid (matte) each layer uses; the thicker the tier = the more blurred the background and the more it emphasizes foreground focus, the thinner = the more visible the background and the closer to the environment layer. The glass background material is **only available inside a WindowContainer**; Stage / Volumetric 3D scenes cannot rely on glass for readability>

| Layer | Material treatment | glassStyle | opacity | Content carried | Meets contrast |
|---|---|---|---|---|---|
| Foreground focus panel | | | | | |
| Environment / backing layer | | | | | |

- **passthrough / MR readability adjudication**: <in a passthrough environment glass lets the real world show through; panels carrying key status, body text, or forms should choose a thicker tier or add a solid backing that guarantees contrast. Give the tier choice, adjudication, and contrast handling panel by panel, echoing §4 and PICO-COLOR "not by color alone." Where the SpatialUI side Tab Bar glass has a known display issue, a fallback must be declared>
- **Vibrant Style application list**: <PICO SpatialUI dynamic color-mixing capability, used for single-color panels and text on passthrough/complex/highly dynamic backgrounds. Declare item by item the elements enabling Vibrant, the tier, and the termination/propagation strategy; regions containing an image/gradient must not rely on Vibrant>

| Element / panel | Background controllability (Full/Shared/MR) | Vibrant tier (darkest→ultralight/none) | Propagation / termination | Fallback (solid backing / thicker glass) |
|---|---|---|---|---|
| | | | | |

## 7. Data display and semantic contract

> Declare how data is converted into user-visible UI.

- **Display-only paths displayOnlyPaths[]**: paths used only for display and not for coloring. Sample values must be end-user-readable copy (such as "Vibration Sensor Array" rather than `vibration_array`, "Bearing 3" rather than `bearing_3`).
- **Semantic enum paths semanticEnumPaths[]**: paths involved in coloring / state determination / alert level / trend, each mapped to the `aliases[]` and `label` of the §3.2 color semantics, guaranteeing that the visible UI shows human-readable labels.
- **Data states**: <cover the project-relevant ones among loading / fresh / aging / stale / offline / partial / conflicting / permission_denied / error as needed, and describe the source, update time, and trust>
- **Trust policy trustPolicy**: <e.g. freshness is always visible, stale is never disguised as real-time, alerts always carry a source, etc. (declare as this project needs)>

| Display format rules formattingRules | Input path | Output format | fallback | Applicable data states |
|---|---|---|---|---|
| | | | | |

## 8. PICO platform numeric spec

> The target platform is fixed as PICO spatial; numbers are governed by the official PICO spec and the Design Tokens above.

- **Corner radius**: <e.g. PICO 32dp>
- **Minimum font size**: <e.g. PICO 12dp; CJK body ≤17sp uses Medium>
- **Interaction hit target**: <e.g. PICO 56dp>
- **Central field-of-view zones**: <e.g. PICO 65° / 40°>

## 9. Asset Delivery

> Beyond sliced images/icons, there are also 3D models, materials, spatial audio, and environment assets. The core is "engineering can use it directly, and it does not blur or break at different distances."

### 9.1 2D bitmap / sliced image

| Item | Delivery spec |
|---|---|
| Format | PNG (with transparency) / WebP, avoid lossy compression that damages edges |
| Multiplier | Export by dp/dmm baseline |
| Naming | `component_state_multiplier`, uniformly lowercase with underscores, machine-parseable |
| Slice inset | Preserve a safe inset, annotate nine-patch stretch regions |

### 9.2 Iconography

| Item | Delivery spec |
|---|---|
| Format | Prefer SVG / vector to guarantee clarity at any wearing distance |
| Grid | Unified icon grid (such as a 24/28dp visual box), consistent line width |
| Naming classification | Group by semantics (action/status/nav), including filled/outline variants |
| Adaptation | Single-color tintable, following the Design Tokens semantic colors |

### 9.3 3D assets (specific to spatial apps)

| Item | Delivery spec |
|---|---|
| Polygon budget | Give a triangle/vertex upper bound, matching the performance budget (a constant frame rate is a hard indicator of immersion not breaking) |
| Material / PBR | Texture resolution upper bound, material channels (albedo/normal/roughness/metallic) |
| Scale / anchor | Real-world metric scale, model origin/anchor position, avoiding placement misalignment |
| LOD | Multiple levels of detail, reduce polygons at distance, control power draw and prevent thermal throttling |

> The specific 3D file format and import flow are governed by the official PICO spatial-engine conventions; this design spec does not lock the engine implementation.

### 9.4 Spatial audio / motion / environment assets

| Item | Delivery spec |
|---|---|
| Spatial audio | File format/sample rate, sound-source localization (whether it follows the space), feedback-sound list |
| Motion assets | Sprite sheet/timeline, with duration and easing attached, aligned with the Motion spec |
| Environment assets | Panorama/environment map resolution and format (if there is an immersive environment) |

### 9.5 Delivery method and engineering handoff

- **Single source**: assets follow the Design Tokens; colors/sizes are not hard-coded into the sliced images, and can be tinted at runtime.
- **Asset list**: one list (asset name × format × size/polygon count × usage × owning component) for QA to search.

## 10. Minimum Completeness Gate

> This table is self-checked by the visual/design-system generating role and independently re-reviewed by `design_coherence_reviewer`.
> Giving only style adjectives, a component list, or a shared state table does not constitute structural completeness. If any core component is missing a fixed structure block,
> any key token is still a placeholder, or the window layout and components cannot be mapped one-to-one, it is `block`. When any row is
> `block`, this document's `minimumCompletenessGate=block` and the overall `designStatus=invalid`.

| Check Item | Minimum Pass Condition | Evidence Anchor | Verdict |
|---|---|---|---|
| Visual direction | 2–3 substantially different directions, selection basis, ≥2 rejected directions and approval evidence complete | §2 | pass / block |
| Visual language | tokens, typography, colorSemantics, materials, scale are all consumable precise values with no mutually exclusive conflicts | §3–§4 | pass / block |
| Window structure | Each primary WindowContainer has a shell, ASCII/Grid, region→component mapping, spacing, and reflow | §5.0 | pass / block |
| Component structure | Each core component's base fields, anatomy.layout, sizing, metrics, renderSpec, dataBindings, variants, states all exist independently | §5 | pass / block |
| Coverage reconciliation | The structure-completeness checklist and the three reconciliation tables (data entity/decision output/primary component sub-states) have no unhandled gaps | §5.1–§5.2 | pass / block |
| Semantics and trust | Materials/depth, data display, fallback, data states, and trust policy are implementable and traceable | §6–§8 | pass / block |

| Field | Value |
|---|---|
| minimumCompletenessGate | pass / block |

## 11. Delivery and Recipients

- **Deliverables**: visual direction and approved reference, visual language tokens, component specs, data-display semantic contract, asset list (this document is their human-readable source of truth)
- **Recipients**: Prototype / Frontend Engineer, QA, Design Lead

---

> Format convention: Tokens are the single contract between design and code, and values must be precise (colors #hex); components use structured anatomy (layout Grid + sizing tiers), no prose; colors must use the color+shape dual-channel with a human-readable label; data does not echo the machine enum; PICO platform numbers must not be missing; any design change must be reflected in the delivery facts.
