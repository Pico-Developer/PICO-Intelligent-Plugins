# PICO Spatial Design Rules & Vocabulary

Two things live here: the **spatial-affordance vocabulary** you use to justify putting an app in space (and to pick its form and scale) in the Frame phase, and the **hard checks** the pre-build critique runs. The checks aren't bureaucracy — each one guards against a specific way spatial designs go generic or uncomfortable. They apply to any form: a Planar window of any size, a HUD/Augment widget, a Volumetric surface, or an immersive Stage.

## Spatial-affordance vocabulary

When you justify "why in space" in the Frame phase, go through these affordances task by task. For each core task, name which one earns the spatialization, then write the **2D counterfactual** — how you'd do the same task on a flat monitor, and why the spatial version is genuinely better. If a flat monitor does it just as well, don't spatialize that part. The strength and kind of affordance also picks the **form**: room-scale reading → large Planar; a glanceable persistent cue → small HUD/Augment; a 3D subject in the round → Volumetric; replacing the real world → Stage.

| Affordance        | It earns its keep when…                               | Example                                             |
| ----------------- | ----------------------------------------------------- | --------------------------------------------------- |
| **Direction**     | information belongs to a real bearing around the user | alerts anchored to the physical zone they came from |
| **Distance**      | importance maps to how close something is             | critical KPI pulled near, context pushed back       |
| **Scale**         | true size matters or a view needs to be room-sized    | a floor plan or timeline read at wall scale         |
| **Depth**         | focus-plus-context via layering beats tabs            | live feed in front, history stacked behind          |
| **Position**      | persistent placement builds spatial memory            | the same panel always at the user's right           |
| **Motion**        | movement conveys state change, not decoration         | a value physically sliding between zones            |
| **Body**          | reaching/turning is a natural, low-cost input         | grabbing a panel to compare side by side            |
| **Collaboration** | multiple people share one anchored surface            | a shared ops wall everyone sees identically         |
| **Simulation**    | a 3D subject must be inspected in the round           | a product or machine model beside its data          |
| **Time**          | change over time reads better spread in space         | a process laid out along a spatial track            |

The 2D counterfactual is the originality backbone: a spatial decision that can't beat its own flat-screen version isn't defensible.

## Anti-patterns — design against these

- **Scaled-up phone panel** — a spatial surface is not a phone UI at 4×. Re-derive layout for a room-distance, wide-FOV, head-and-hand context (and, for a small widget, for a glanceable one-thing role).
- **Form-by-habit** — reaching for a big dashboard when the task is a glanceable cue, or a flat panel when a 3D subject wants Volumetric. Let the spatial justification pick the form and scale.
- **Widget wall** — a grid of tiles with no single primary focus and no decision the app drives. Lead with the app's one job.
- **Floating panels for atmosphere** — extra windows that add no task value cost comfort and clarity. Every surface earns its place.
- **Generic dark dashboard** — near-black background + one acid/teal accent + hairline rules is the AI default. If your palette isn't from the subject's world, it's a template.
- **Head-turn to read core content** — core content outside the 65°×40° clear-FOV zone. Sizing failure, not preference.
- **Room-occluding default** — an oversized initial window that blocks the environment and creates pressure.
- **Attachment reflex** — reaching for a Toolbar/TabBar/Subwindow/Augment/Popup by habit. Justify placement first; `None` or in-place control is often right.
- **Domain reskin** — same layout and structure across domains, only copy/colors/icons swapped.

## Pre-build hard checks (critique gate)

Any of these sends you back to revise, not tune later:

1. **Fewer than three real alternatives** were compared, or the rejected ones have no recorded reason.
2. **A core task has no 2D counterfactual**, or the spatialization can't beat its flat version.
3. **A surface size was not internally validated** against content type, clear-FOV, readable/clickable floors, and default/min/max bounds, or a Planar window defaults to a fixed 1280×720 / 1600×900 without calibration. Keep the calculation out of the final design document; record only implementation-relevant dimensions.
4. **Core content falls outside the 65°×40° clear-FOV zone**, or hit target <56 dp / body <12 dp.
5. **An attachment** (TabBar, Toolbar, Subwindow, SpatialPopup, Augment, Sheet/Dialog) was added without comparing it against `None` / in-place control, or carries mismatched semantics (navigation in a Toolbar, tools in a TabBar, primary content in an Augment).
6. **Domain-swap test fails** — changing the domain and colors would leave the design essentially unchanged.
7. **A core component has no data source or task**, or the layout has no derivation evidence.
8. **The app has no single primary focus** or drives no clear decision/task outcome.

## PICO color & glass (so the design survives code generation)

A spatial design fails to reproduce faithfully when its colors are recorded as
bare hex with no PICO grounding — but it _also_ fails if you just map them onto
the **default** `PicoTheme` roles, because then the app wears PICO's default
palette, not this design's. The right model: **the design's colors drive the
theme**. Downstream builds a custom `ColorScheme` from the design's values and
injects it via `PicoTheme(colorScheme = …)`; built-in components still read
`PicoTheme.colorScheme.*`, so they get _this design's_ colors while keeping glass
and vibrant behavior.

PICO has two color families, but the final theme contract is always complete:
record all 16 public `ColorScheme` roles. Each role must contain either an exact
design value or an explicit `inherit SpatialUI Vibrant <role>` decision. This
lets downstream define the entire `systemColorScheme(...).copy(...)` call rather
than relying on omitted parameters.

- **Brand / accent / fixed-semantic colors → override with the design's exact
  value.** These are the design's identity. Colors that match a fixed semantic
  role (`error` / `alert` / `passable` / `interaction` / `dividerLine` /
  `labelPrimaryLight`) go into the custom `ColorScheme` verbatim — these roles
  are SDK-side pure semantic colors, safe from unwanted vibrant blending.
  Brand / decorative colors with no matching `ColorScheme` role are carried
  verbatim as named brand tokens (Kotlin color literals) and referenced directly;
  they do **not** enter the `ColorScheme`.
- **Adaptive grayscale hierarchy (`fill*` / `label*`, hover/pressed) → keep
  adaptive by default.** The SDK maps these to Vibrant levels so text and
  surfaces stay readable across viewing distance and passthrough brightness.
  Record the _intended tone_ ("dark console surface", "primary text"); pin an
  exact grey only when the design deliberately demands it. Hardcoding greys here
  is a known way to break in-headset readability.

Other rules:

- **Design premise — SpatialUI Web glass is the background.** Load the vendored
  SpatialUI Web bundle first and keep its default `PicoTheme.install({
scheme: "vibrant" })`. The app surface itself uses the library's
  `Material.Regular` glass variables/styles; do not replace that surface with a
  fixed gray, opaque root, or independently authored blur recipe. Any room image
  or neutral page color sits behind the glass only to make translucency visible
  and is not a design token or deliverable requirement.
- **The window root is system glass** (`Material.Regular`) by default. Never put a
  solid color / `fillPrimary` on the window root — it kills the glass and vibrant
  linkage. `fill*` roles are for inner surfaces only.
- **Glass tiers express depth, not decoration**: `Thin` (background shows through)
  → `Thickest` (strong foreground focus). Under passthrough, panels with key
  text/forms need a thicker tier or a solid backing to keep contrast.
- **Status by more than color**: any color-coded status also needs a non-color
  cue (shape/icon) and a human-readable label.

> Color anti-patterns (part of the domain-swap check above): (1) a palette with no
> theming intent renders as a flat hardcoded page; (2) mapping the design's colors
> onto the _default_ theme roles throws the design's palette away and reproduces
> the generic PICO look. The design's brand/accent/semantic colors must actually
> drive the custom `ColorScheme`; all remaining roles must be explicitly
> inherited from the SpatialUI Vibrant scheme.

## Z-axis / depth layering (even inside Planar windows)

Spatial apps are not limited to flat 2D stacking — **Z-axis depth is available even inside a Planar WindowContainer**. Use it deliberately to express focus, priority, and physicality, not just as a CSS-style z-index for overlap fixes.

### Depth vocabulary & when to use it

| Concept                  | Use for                                                                           | SDK modifier                                 | Typical value                              |
| ------------------------ | --------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------ |
| **Selection lift**       | Selected/focused card, hero, or item physically rises forward                     | `zOffset`                                    | 8–24 dp toward +Z                          |
| **Hover feedback**       | Pointer/gaze hover makes an element pop slightly                                  | `zOffset { animate*AsState }`                | 2–6 dp toward +Z                           |
| **Glass material depth** | Cards/panels with `backgroundMaterial` automatically reserve depth                | `backgroundMaterial`                         | handled by SDK; don't stack zOffset on top |
| **Content thickness**    | Volumetric-looking tiles, buttons with physical presence                          | `depth`                                      | 4–12 dp                                    |
| **3D layering**          | Floating labels, badge overhang that doesn't need sibling nesting (within reason) | `Box3D` + `zOffset`                          | keep within 640 dp total depth             |
| **Attached ornaments**   | Tooltips, headers, or controls anchored to window corners/edges                   | `Augment(anchor = NormalizedPoint3D.*Front)` | use Augment, not manual zOffset            |

### Rules of thumb

- **Nearest = most important**: critical interaction or focused selection sits closest; background context recedes.
- **Depth = priority signal, not decoration**: don't push random elements forward just because you can. A lift must communicate state change (selected / pressed / hovered).
- **Keep depth inside 640 dp** for content inside a Planar window — past that it clips.
- **Animate depth changes**: a selected item rising forward should animate (300–400 ms ease), not teleport.
- **Don't stack zOffset on glass cards**: `backgroundMaterial` already reserves depth behind content; adding manual zOffset can cause depth-fighting.
- **Prefer Augment for persistent floating UI** (tooltip, toolbar, floating header) over in-layout zOffset — Augment is a real system window with proper layering and avoids clipping.
- **Sibling-first for overflow (2D)**: for badges/labels that only need to peek outside a rounded corner _within the same plane_, use sibling positioning (see below). Use Z-offset only when you genuinely want depth separation.

### PICO axis convention

When describing depth in design docs, use: **+X = right, +Y = up, +Z = toward the user** (forward). Receding = -Z.

## Component layout anti-patterns

- **Badge/label clipped by parent clip()**: When placing badges, tags, labels, notification dots, or floating indicators that should extend outside a rounded/shaped container (e.g. role tags on a card, unread dots on an avatar, corner ribbons), **use sibling positioning, not parent nesting**. Place the badge as a sibling Box in the same outer layout, positioned via `align(Alignment.TopEnd)` + offset, rather than nesting it inside the container Box that has `clip()` or `border()` applied. A clipped parent will always cut off content that extends past its rounded corners.

  ```kotlin
  // ❌ Bad: badge inside clipped parent → gets cut off
  Box(Modifier.clip(RoundedCornerShape(16.dp)).background(...)) {
    CardContent()
    Badge(Modifier.align(Alignment.TopEnd).offset(x=4.dp)) // clipped!
  }

  // ✅ Good: sibling relationship in unclipped outer Box
  Box {
    Box(Modifier.clip(RoundedCornerShape(16.dp)).background(...)) {
      CardContent()
    }
    Badge(Modifier.align(Alignment.TopEnd).offset(x=4.dp, y=(-2).dp)) // visible
  }
  ```

- **Hardcoded corner clipping on outer containers**: The window itself has a fixed 32 dp corner radius; inner containers with their own `clip()` create nested rounded rectangles that can trap overflow content. Reserve clipping for content that genuinely needs to be masked (images, scrollable lists); use `border()` alone for outlines that don't need to clip.

## Terminology boundary

Keep design facts in PICO **design** terminology, not downstream code enums:

- Use: Shared Space / Full Space; WindowContainer **Planar** / **Volumetric**; Stage Mixed / Progressive / Full.
- Don't use as design facts: `ON_PLAIN`, `IN_VOLUME`, `STAGE_MIXED`, `single_panel`, `window_plus_subwindow`. Those are downstream implementation enums owned by the code-generation skill, not this design package.
