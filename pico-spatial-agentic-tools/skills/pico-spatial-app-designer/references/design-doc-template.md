# Spatial App Design Doc — <project name>

> Copy this file to `design-doc.md` in your working directory and fill each section as you move through the six phases. This is the single carrying layer for the design's reasoning. Delete the guidance italics as you go. Keep facts in PICO design terminology (Shared/Full Space, WindowContainer Planar/Volumetric, Stage) — no code enums.

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

### Visual tokens

The design's own colors drive the theme — downstream builds a **complete custom `ColorScheme` from these values and injects it into `PicoTheme(colorScheme = …)`**. Define every public role below. Use an exact hex for fixed design values; otherwise write `inherit SpatialUI Vibrant <role>`. No role may be omitted from the final `systemColorScheme(...).copy(...)`.

| `ColorScheme` role  | Exact hex or explicit Vibrant inheritance   | Used for |
| ------------------- | ------------------------------------------- | -------- |
| `fillPrimary`       | `inherit SpatialUI Vibrant fillPrimary`     |          |
| `fillSecondary`     | `inherit SpatialUI Vibrant fillSecondary`   |          |
| `fillTertiary`      | `inherit SpatialUI Vibrant fillTertiary`    |          |
| `fillLight`         | `inherit SpatialUI Vibrant fillLight`       |          |
| `labelPrimaryLight` | `#` or inheritance                          |          |
| `labelPrimary`      | `inherit SpatialUI Vibrant labelPrimary`    |          |
| `labelSecondary`    | `inherit SpatialUI Vibrant labelSecondary`  |          |
| `labelTertiary`     | `inherit SpatialUI Vibrant labelTertiary`   |          |
| `labelQuaternary`   | `inherit SpatialUI Vibrant labelQuaternary` |          |
| `lightenHover`      | `inherit SpatialUI Vibrant lightenHover`    |          |
| `lightenPressed`    | `inherit SpatialUI Vibrant lightenPressed`  |          |
| `error`             | `#` or inheritance                          |          |
| `alert`             | `#` or inheritance                          |          |
| `passable`          | `#` or inheritance                          |          |
| `interaction`       | `#` or inheritance                          |          |
| `dividerLine`       | `#` or inheritance                          |          |

**Brand / decorative tokens outside `ColorScheme`**

| Token name | Exact hex | Used for |
| ---------- | --------- | -------- |
|            | `#`       |          |

**Semantic colors** — for any status the screen encodes by color, give the design color, a **non-color redundant cue** (shape/icon), and the **human-readable UI label** (not the raw data enum). Fill only if the screen has status semantics.

| Status | Design color / role | Redundant cue (shape/icon) | UI label |
| ------ | ------------------- | -------------------------- | -------- |
|        |                     |                            |          |

**Type** — display face, body face, type scale (map to `PicoTheme.typography.*`: display/headline/title/body/label; override the Typography where the design's type differs from default).

**Materials / depth** — glass tier per surface (`Thin/Regular/Thick/Thickest`) and depth language. The window root is system `Material.Regular` glass by default — **never paint a solid color / `fillPrimary` on the window root** (it kills the glass + vibrant linkage); `fill*` roles are for inner cards/containers. Under passthrough, key text/forms need a thicker glass tier or a solid backing to keep contrast.

**Glass premise** — the root surface is the vendored SpatialUI Web `vibrant` theme with its `Material.Regular` glass. Design and judge contrast on that actual library surface. Do not define a substitute gray root, custom blur recipe, or opaque background token.

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
| Single primary focus / clear decision                       |       |          |

_Only proceed to Build once all pass._

## 5 · Build — coverage manifest

_The denominator for the second critique. See `./preview-guide.md`._

| #   | Kind (state/transition/component/binding) | From design doc | Implemented in preview.html (selector/where) |
| --- | ----------------------------------------- | --------------- | -------------------------------------------- |

## 6 · Critique again

**Independent coverage rebuild** — _diff between the manifest and what's actually triggerable in the prototype._

**Quality bar**

| Criterion                                                                        | Met? | Evidence |
| -------------------------------------------------------------------------------- | ---- | -------- |
| App's job is a clear decision/task outcome                                       |      |          |
| Form/scale follows the spatial justification                                     |      |          |
| Spatialization justified affordance-by-affordance                                |      |          |
| ≥3 alternatives compared, rejects have reasons                                   |      |          |
| Every window/surface records final default/min/max dimensions                    |      |          |
| Design derives from domain (survives domain-swap)                                |      |          |
| SpatialUI bundle is inline; mapped tags are registered, present, and event-wired |      |          |
| No unjustified native/hand-rolled duplicate of an available `sui-*` control      |      |          |
| Root surface uses SpatialUI Web `vibrant` + `Material.Regular` glass             |      |          |
| No design/debug-only controls appear in the product UI                           |      |          |
| preview.html is a triggerable state machine, full coverage                       |      |          |
| Signature present, surroundings quiet                                            |      |          |

**Patch log** (max 3 rounds)

| Round | Problem | Target | Expected improvement | Re-ran Build+critique? |
| ----- | ------- | ------ | -------------------- | ---------------------- |

**Device validation** — `not_performed` (Web validates logic/layout only; real-device comfort/occlusion/size/performance not verified).

**Verdict** — _pass / changes_requested / block, with the reason. If unmet after 3 rounds, state what's still unmet plainly._
