# Preview Guide — the Web validation prototype

`preview.html` proves that `design-spec.json` can render into a coherent product
experience before anyone writes runtime code. Its scope is fixed:
**`web_design_validation_only`**. It never validates real-device comfort,
occlusion, physical size, or performance — and it never contains Android/PICO
runtime code, device evidence, or parity claims.

The prototype must be both **triggerable and visually resolved**. A static mock
proves no behavior; a mechanically complete but weak layout is not ready for app
generation. A reviewer must be able to click through every state, inspect
fallback and error data, reach confirmation dialogs, and judge the composition
at the declared default and minimum sizes.

## Step 1 — validate the JSON source

Write `design-spec.json` before any HTML and validate it against
`../assets/design-spec.schema.json`. Follow `design-spec-contract.md` for
cross-reference checks that JSON Schema cannot prove: unique IDs; resolvable
initial state, surface roots, children, assets, states, action/transition
targets; acyclic node ownership; and registered `sui-*` component names.
Then run `python3 scripts/check_design_surface_discipline.py
<path-to-design-spec.json>`. Do not build the Preview while that check reports
a structural region fill, app-authored content border, or nested surfaces.

Build the coverage manifest directly from the JSON:

- **Surfaces** — each surface, its root, and min/default/max dimensions.
- **States** — each state and its per-surface roots.
- **Transitions** — each trigger and confirmation contract.
- **Actions** — each event target and its state mutation or transition.
- **Nodes** — every layout, SpatialUI component, text, media, and domain visual.
- **Bindings** — every path against normal, fallback, and error data.
- **Responsive rules** — every bounded override.
- **Assets** — every referenced asset and its purpose.

## Step 2 — build against the manifest

Single self-contained file (inline CSS/JS, no external deps or runtime file
reads). Start by reading
[`design-spec-contract.md`](./design-spec-contract.md) and
[`spatialui-web-guide.md`](./spatialui-web-guide.md). When the spec contains
icon assets, also read [`icon-selection.md`](./icon-selection.md). Then inline the complete
`../assets/spatialui-web/spatialui.bundle.js` in a `<script>` before the app
script.

Required skeleton:

```html
<style>
  body {
    background-color: #dad6d3;
    background-image: none;
  }
</style>
<main id="app" data-design-spec-revision="1"></main>
<script id="pico-design-spec" type="application/json">
  { "...exact contents of design-spec.json..." }
</script>
<script>
  const designSpec = JSON.parse(document.querySelector('#pico-design-spec').textContent);
  renderDesign(designSpec, document.querySelector('#app'));
</script>
```

The embedded object must be semantically identical to `design-spec.json`.
Whitespace is irrelevant; parsed values are not. Requirements:

- **A spec-driven node renderer** — resolve the active state's surface roots and
  recursively render node IDs. Product markup is not hand-authored beside it.
- **Transparent structural regions** — `layout` and `domain_visual` nodes only
  arrange or render content and never own `appearance.fill`. Do not infer a
  fill, radius, or border from an id, name, purpose, layout mode, or words such
  as `panel`, `section`, `card`, `row`, `column`, or `grid`. Reject
  `rootMaterial` and `appearance.material`; neither is part of the design
  contract.
- **One canonical fill path** — app-authored CSS does not declare arbitrary
  backgrounds. Use only
  `[data-design-surface] { background:
  var(--pico-design-surface-fill); }`; set the attribute and custom property
  from a node's declared fill, and render each filled node once.
- **A real state machine** — the initial state, actions, transitions, and
  targets come from the JSON; local mutations plus back/exit paths work.
- **SpatialUI controls** — instantiate each declared `sui-*` component and wire
  its declared public `CustomEvent`. Native controls or hand-rolled dialogs are
  allowed only when the catalog has no equivalent and the spec records why.
- **Real icon geometry** — resolve every `icon70://7.0/<name>` to its bundled
  SVG and every `design-assets/icons/*.svg` source to the exact custom SVG drawn
  during Build. Inline the SVG in its declared slot so `currentColor` supplies
  tint. Do not render emoji, Unicode glyphs, icon-font characters, filename
  text, runtime file reads, or absolute paths.
- **Theme installation** — use SpatialUI Web's unchanged Vibrant
  `ColorScheme`. Treat `theme.colorScheme` as same-name role references only;
  expose custom `brandColors` separately and never overwrite native roles.
- **Sample data in three cases** — normal, fallback (missing/stale), and error
  come from `dataCases` and render through the same node graph.
- **High-risk actions gated by a dialog** — destructive or irreversible actions show explicit confirmation.
- **Natural responsive reflow** — apply `responsiveRules` between each surface's
  min/default/max bounds and honor `prefers-reduced-motion`. Do not add a
  visible layout-tier or viewport-preset switch.
- **Windows at default size**, with the sizing intent legible (a room-scale surface should _look_ room-scale, not phone-scale, in the mock; a small widget should read as glanceable).
- **Stable selectors** — give state containers and key elements stable ids/classes so the critique can assert against them.
- **No HTML-only facts** — user-facing text, assets, design colors, dimensions,
  component ordering, states, and transition targets do not originate in HTML,
  CSS, or renderer constants.

Represent the PICO context with the library itself: keep SpatialUI Web's default
`vibrant` theme and render the app root with its `Material.Regular` glass
background variable/style. Do not substitute a fixed gray panel, custom
`backdrop-filter`, or opaque app root for that material. Set the page `body`
background to the fixed light neutral preview environment `#DAD6D3`, with no
background image. This renderer-owned context reveals glass translucency and is
not an app-owned token or a `design-spec.json` value. Keep the 32 dp window
radius and make the spatial intent readable without pretending the surface is a
phone screen.

The preview is the product surface, not a design inspector. Do not render
viewport-mode selectors, data-source simulators, coverage status, token
swatches, implementation notes, or keyboard-help copy unless the brief
explicitly makes one of them a user-facing feature. Exercise
fallback/error states through test hooks in script or temporary review tooling,
not persistent controls in the delivered UI.

## Step 3 — generation-side mapping and visual pass

Right after building, record how each manifest row maps into the prototype:
surface/state → rendered root, transition → trigger, node → DOM, SpatialUI
mapping → registered tag + selector + public event, binding →
normal/fallback/error, responsive rule → applied layout change, and asset →
rendered element. If you cannot trace a rendered element back to a JSON ID, it
is an HTML-only design fact and must be removed.

Inspect the rendered page, not just its source:

1. open every state at each surface's default size;
2. resize to the declared minimum and confirm intentional reflow;
3. exercise normal, fallback, error, and confirmation paths;
4. check hierarchy, spacing rhythm, text fit, contrast, asset quality, and the
   signature element;
5. verify `getComputedStyle(document.body).backgroundColor` is
   `rgb(218, 214, 211)` and `backgroundImage` is `none`;
6. fix design problems in `design-spec.json`, increment its revision, and
   regenerate the preview.

Renderer changes are reserved for generic mapping defects and declared
`domain_visual` implementations.

## What "done" looks like

`design-spec.json` is valid and exactly embedded; every manifest row is rendered
and triggerable; mapped controls are registered `sui-*` elements wired through
public events; normal/fallback/error data are testable; high-risk transitions
are blocked by a SpatialUI dialog; natural responsive reflow and reduced-motion
are respected. The root uses SpatialUI Web glass, the delivered UI contains no
design/debug-only controls, and visual review passes at default and minimum
sizes. Any stale JSON snapshot, HTML-only design fact, or available SpatialUI
control replaced by a native equivalent without a documented reason is a
`block`. Any renderer-authored layout background, radius, or border absent from
the corresponding JSON node is also a `block`.
