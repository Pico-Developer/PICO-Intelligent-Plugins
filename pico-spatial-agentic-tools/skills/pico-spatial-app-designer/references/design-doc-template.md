# Spatial App Design Doc — <project name>

> Copy this file to `design-doc.md` in your working directory and fill each
> section as you move through the six phases. This carries rationale and review
> evidence; `design-spec.json` is the source of truth for executable design
> facts. Delete the guidance italics as you go. Keep facts in PICO design
> terminology (Shared/Full Space, WindowContainer Planar/Volumetric, Stage) —
> no code enums.

## 1 · Frame

**Subject** — _domain, and if the brief was vague, how you defined it._

**Viewer & context** — _who reads/operates this app; room, posture, reading distance._

**The single job** — _the one thing this app exists to do (a decision or task outcome, not "show data")._

**Spatial justification** — _for each core task, the affordance that earns spatialization + its 2D counterfactual. This also picks the form: Planar window (any size) / HUD-Augment widget / Volumetric / Stage._

| Core task | Affordance (direction/distance/scale/depth/position/motion/body/collaboration/simulation/time) | Why spatial beats flat | 2D counterfactual |
| --------- | ---------------------------------------------------------------------------------------------- | ---------------------- | ----------------- |
|           |                                                                                                |                        |                   |

**Assumptions** — _everything you had to invent._

| Assumption | Confidence | What changes if wrong |
| ---------- | ---------- | --------------------- |
|            |            |                       |

## 2 · Explore — alternatives

_At least three substantially different directions. Different IA, spatialization degree, container structure, primary interaction, reading distance — not three color swaps. Prefer generating each direction with a separate fresh-context subagent (spawned in parallel, blind to the others, seeded only with the shared frame/job/spatial-justification/domain plus one divergence constraint); fall back to isolated inline generation if subagents are unavailable. Note below how each was generated._

**Direction generation** — _subagent-per-direction (parallel) / inline-isolated, and why._

### Direction A — <name>

_Concept, signature idea, main risk._

### Direction B — <name>

### Direction C — <name>

**Decision matrix**

| Direction | Task efficiency | Spatial value | PICO comfort | Domain fit | Risk | Distinctiveness |
| --------- | --------------- | ------------- | ------------ | ---------- | ---- | --------------- |
| A         |                 |               |              |            |      |                 |
| B         |                 |               |              |            |      |                 |
| C         |                 |               |              |            |      |                 |

**Chosen: <A/B/C>** — _why it won._
**Rejected** — _why B and C lost (specific reasons, not "less good")._

## 3 · Plan

**Executable spec** — `design-spec.json`, schema version `1.0`, revision
`<revision>`. _Write and validate it before generating HTML. The tables below
summarize the spec for human review; if they disagree, repair the JSON and
regenerate the preview._

### Visual tokens

Preserve SpatialUI's native `ColorScheme`: every public role below must inherit
the same-name Vibrant role. Do not assign custom values to `fill*`, `label*`,
interaction, status, hover/pressed, or divider roles. Put any custom color in
the separate brand/decorative token table and consume it directly.

| `ColorScheme` role  | Required value                              | Used for |
| ------------------- | ------------------------------------------- | -------- |
| `fillPrimary`       | `inherit SpatialUI Vibrant fillPrimary`     |          |
| `fillSecondary`     | `inherit SpatialUI Vibrant fillSecondary`   |          |
| `fillTertiary`      | `inherit SpatialUI Vibrant fillTertiary`    |          |
| `fillLight`         | `inherit SpatialUI Vibrant fillLight`       |          |
| `labelPrimaryLight` | `inherit SpatialUI Vibrant labelPrimaryLight` |        |
| `labelPrimary`      | `inherit SpatialUI Vibrant labelPrimary`    |          |
| `labelSecondary`    | `inherit SpatialUI Vibrant labelSecondary`  |          |
| `labelTertiary`     | `inherit SpatialUI Vibrant labelTertiary`   |          |
| `labelQuaternary`   | `inherit SpatialUI Vibrant labelQuaternary` |          |
| `lightenHover`      | `inherit SpatialUI Vibrant lightenHover`    |          |
| `lightenPressed`    | `inherit SpatialUI Vibrant lightenPressed`  |          |
| `error`             | `inherit SpatialUI Vibrant error`           |          |
| `alert`             | `inherit SpatialUI Vibrant alert`           |          |
| `passable`          | `inherit SpatialUI Vibrant passable`        |          |
| `interaction`       | `inherit SpatialUI Vibrant interaction`     |          |
| `dividerLine`       | `inherit SpatialUI Vibrant dividerLine`     |          |

**Brand / decorative tokens outside `ColorScheme`**

| Token name | Exact hex | Used for |
| ---------- | --------- | -------- |
|            | `#`       |          |

**Semantic colors** — for any status the screen encodes by color, give the design color, a **non-color redundant cue** (shape/icon), and the **human-readable UI label** (not the raw data enum). Fill only if the screen has status semantics.

| Status | Design color / role | Redundant cue (shape/icon) | UI label |
| ------ | ------------------- | -------------------------- | -------- |
|        |                     |                            |          |

**Type** — display face, body face, type scale (map to `PicoTheme.typography.*`: display/headline/title/body/label; override the Typography where the design's type differs from default).

**Depth** — record only product-owned depth relationships. Do not choose or
record `rootMaterial` or per-node material tiers. The system owns the window
background; `fill*` roles are available only for bounded content nodes, never
for structural `layout` or `domain_visual` regions.

**Window-background premise** — preview the unchanged SpatialUI Web system
surface against the fixed environment color. Do not define a substitute root,
custom blur recipe, material field, or opaque background token.

### Signature element

_The one memorable thing; how the surroundings stay quiet around it._

### Surface sizing

_One row per window/surface. Validate sizing internally with `./window-sizing.md`, but record only dimensions consumed by implementation._

| Window / surface | Type (Planar/Volumetric/Stage) | Content | Default (dp / m) | Min | Max |
| ---------------- | ------------------------------ | ------- | ---------------- | --- | --- |

### Layout

_Prose + ASCII wireframe. Single primary focus, regions (from task/data/frequency), density ceiling._

```
+--------------------------------------------------+
|  ascii wireframe of the app at default size      |
+--------------------------------------------------+
```

### State graph

| State | Primary task | Primary focus | Components | Data deps | Entry/exit |
| ----- | ------------ | ------------- | ---------- | --------- | ---------- |

| Transition | From → To | Trigger | Explicit confirm? |
| ---------- | --------- | ------- | ----------------- |

### Components

_One block per core component: name, the task it serves, its data source, variants, and states._

### SpatialUI Web component map

_Read `./spatialui-web-guide.md`, then inspect the matching vendored component source. Map every control and system-semantic surface before Build. Custom fallback reasons must be domain-specific._

| Planned element | SpatialUI tag | API checked in                 | Public event/state | Custom fallback reason |
| --------------- | ------------- | ------------------------------ | ------------------ | ---------------------- |
|                 | `sui-*`       | `assets/spatialui-web/js/*.js` |                    | n/a                    |

## 4 · Critique (before build)

**Generic-default simulation** — _what a lazy prompt would produce for this brief._
**Where the plan risked that default, and what I changed.**
**Hard checks** (from `./spatial-design-rules.md`):

| Check                                                       | Pass? | Evidence |
| ----------------------------------------------------------- | ----- | -------- |
| ≥3 real alternatives with rejection reasons                 |       |          |
| Every core task has a 2D counterfactual                     |       |          |
| Form/scale follows the spatial justification (not habit)    |       |          |
| Every window/surface size was internally validated          |       |          |
| Attachments justified vs None/in-place                      |       |          |
| Domain-swap test (design would change)                      |       |          |
| Every core component has data source + task                 |       |          |
| All 16 `ColorScheme` roles are explicitly defined           |       |          |
| Every standard control/system surface maps to SpatialUI Web |       |          |
| `design-spec.json` is valid and all references resolve      |       |          |
| Surface-discipline check passes                             |       |          |
| Repeated-item depth is state/data-driven, never index-driven |       |          |
| Single primary focus / clear decision                       |       |          |

_Only proceed to Build once all pass._

## 5 · Build — coverage manifest

_Generate this denominator from `design-spec.json`, then render the HTML. See
`./preview-guide.md`._

| #   | Kind (surface/state/transition/action/node/binding/rule/asset) | JSON ID/path | Implemented in preview.html (selector/where) |
| --- | -------------------------------------------------------------- | ------------ | -------------------------------------------- |

## 6 · Critique again

**Independent coverage rebuild** — _rebuild from `design-spec.json`; diff it
against what is actually rendered and triggerable in the prototype._

**Quality bar**

| Criterion                                                                        | Met? | Evidence |
| -------------------------------------------------------------------------------- | ---- | -------- |
| App's job is a clear decision/task outcome                                       |      |          |
| Form/scale follows the spatial justification                                     |      |          |
| Spatialization justified affordance-by-affordance                                |      |          |
| ≥3 alternatives compared, rejects have reasons                                   |      |          |
| Every window/surface records final default/min/max dimensions                    |      |          |
| Design derives from domain (survives domain-swap)                                |      |          |
| `design-spec.json` is schema-valid and all references resolve                    |      |          |
| Embedded JSON exactly matches `design-spec.json`; no HTML-only design facts      |      |          |
| SpatialUI bundle is inline; mapped tags are registered, present, and event-wired |      |          |
| No unjustified native/hand-rolled duplicate of an available `sui-*` control      |      |          |
| Root leaves the SpatialUI Web system window background unchanged                |      |          |
| Structural layout/domain regions are transparent; no nested app-authored surfaces |      |          |
| Preview backgrounds use the canonical one-to-one data-design-surface path         |      |          |
| No app-authored content borders or renderer-invented surface decoration          |      |          |
| No design/debug-only controls appear in the product UI                           |      |          |
| preview.html is a triggerable state machine, full coverage                       |      |          |
| Rendered page passes visual review at default and minimum surface sizes          |      |          |
| Signature present, surroundings quiet                                            |      |          |

**Patch log** (max 3 rounds)

| Round | Problem | JSON target / renderer defect | Expected improvement | Revision | Re-ran Build+critique? |
| ----- | ------- | ----------------------------- | -------------------- | -------- | ---------------------- |

**Device validation** — `not_performed` (Web validates logic/layout only; real-device comfort/occlusion/size/performance not verified).

**Verdict** — _pass / changes_requested / block, with the reason. If unmet after 3 rounds, state what's still unmet plainly._
