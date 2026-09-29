# Spatial Design Spec Contract

`design-spec.json` is the executable design intermediate representation shared
by the SpatialUI Web preview and downstream SpatialUI Compose generation. It is
the source of truth for implementation facts. `design-doc.md` explains why the
design was chosen; `preview.html` proves that the spec renders into a usable
experience.

Validate the file against
[`../assets/design-spec.schema.json`](../assets/design-spec.schema.json) before
building the preview.

## Artifact ownership

| Artifact           | Owns                                                                                                           | Must not own                                                                 |
| ------------------ | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `design-doc.md`    | framing, alternatives, rationale, assumptions, critique findings                                               | executable values that are absent from `design-spec.json`                    |
| `design-spec.json` | surfaces, dimensions, tokens, assets, node tree, component props, states, transitions, actions, and data cases | prose-only rationale or Android implementation enums                         |
| `preview.html`     | the renderer, SpatialUI Web runtime, interaction engine, and an exact embedded snapshot of the spec            | independent product copy, layout constants, component choices, or app states |

If these artifacts disagree, repair `design-spec.json`, regenerate
`preview.html`, and update the design document's summary. Never patch the HTML
with a second independent version of a design fact.

## Required model

The top-level object contains:

- `schemaVersion` — currently `1.0`.
- `metadata` — project name, source mode, and monotonically increasing
  `revision`. The HTML root records the same revision.
- `experience` — subject, user/context, single job, space/form, and signature.
- `theme` — all 16 immutable, same-name Vibrant `ColorScheme` references plus
  app-owned brand colors, typography, spacing, and the `vibrant` + `regular`
  root-glass premise.
- `surfaces` — one entry per window/surface with default/min/max dimensions and
  its root node.
- `initialStateId`, `states`, `transitions`, and `actions` — the complete
  triggerable state machine, including local mutations that do not navigate.
- `dataCases` — normal, fallback, and error samples.
- `nodes` — a flat, ID-addressed render tree.
- `responsiveRules` — bounded overrides between the declared surface sizes.
- `assets` — local/generated asset references and their product purpose.

IDs are stable and unique within each collection. References such as
`initialStateId`, `rootNodeId`, `children`, `trigger.nodeId`, event targets, and
`assetId` must resolve to an existing ID of the correct kind. A color entry with
`source: "vibrant"` must inherit the same role named by its containing
`colorScheme` property. Custom `brandColors` use lowerCamelCase app-owned names;
native `ColorScheme` role names are reserved.

## Node vocabulary

Use the smallest kind that preserves semantics:

| `kind`          | Purpose                                                                                       |
| --------------- | --------------------------------------------------------------------------------------------- |
| `layout`        | `row`, `column`, `grid`, `stack`, `overlay`, or scroll ownership                              |
| `spatialui`     | A real vendored `sui-*` component; `component` names the exact registered tag                 |
| `text`          | App-authored text with an explicit typography role and color role/token                       |
| `media`         | Image/video/model representation backed by an `assets[]` entry                                |
| `domain_visual` | A visualization with no SpatialUI control equivalent, such as a waveform, map, or 3D timeline |

A `domain_visual` node must provide `rendererKey`, `purpose`, and structured
`props`. It may have custom rendering code in `preview.html`, but all visible
content, input data, dimensions, colors, and interaction bindings still come
from the JSON. It must not be used to reimplement a button, field, selector,
menu, dialog, or other available `sui-*` control.

When a `domain_visual` contains a repeated or independently styled internal
region, its optional `parts` map declares that region's base `appearance` and
state appearances. A part ID is local to its node: `month-grid.dayCell`
identifies the `dayCell` template inside `month-grid`, not one ID for each
runtime date cell. Omit `parts` when the visual has no such internal appearance
boundary. Part appearances reuse the existing `fill`, `foreground`, `radiusDp`,
`opacity`, and `depthDp` fields; `fill` and `foreground` reference a native
color role or `theme.brandColors` token.

```json
{
  "id": "month-grid",
  "kind": "domain_visual",
  "rendererKey": "month-grid",
  "purpose": "Show the month and its event density",
  "props": {},
  "parts": {
    "dayCell": {
      "appearance": {
        "foreground": "labelPrimary"
      },
      "states": {
        "selected": {
          "fill": "selectedDayFill",
          "depthDp": 18
        }
      }
    }
  }
}
```

## Icon assets

Choose icons only after component semantics are fixed. Follow
[`icon-selection.md`](./icon-selection.md) for source priority and catalog
search. A built-in component such as `sui-search-field` owns its semantic
affordance and does not need a separate magnifier asset.

Every `sui-icon` node must reference an `assets[]` entry with `kind: "icon"`
through `assetId`; the schema enforces this requirement. Components with an
explicit icon slot may also reference the icon asset on their node.

Use `icon70://7.0/<name>` for a bundled catalog selection. When no authoritative
or bundled asset accurately matches, use
`design-assets/icons/<resource-name>.svg` and draw that source during Build
according to
[`../../spatial-design-to-app/references/icon-drawing.md`](../../spatial-design-to-app/references/icon-drawing.md).
The custom SVG is part of the design package and is the source for both the Web
preview and downstream Android vector materialization.

Do not put emoji, Unicode symbols, icon font characters, raw SVG path data, or
filesystem-absolute paths in `content` or component props.

`layout` and `appearance` use PICO design units and tokens rather than arbitrary
CSS strings. The Web renderer converts dp to px for preview only. Downstream
Compose consumes the same numeric dp values directly. Volumetric dimensions
retain their declared dp or meter unit; any dp-to-meter conversion must use
`PhysicalLengthConverter`, never a fixed ratio. Meter dimensions remain meters
for Stage surfaces.

## Surface discipline

`layout` and `domain_visual` nodes are structural regions and must remain
transparent. Use spacing, alignment, typography, and hierarchy to separate
large primary content areas. A bounded content node becomes an app-authored
surface only when its `appearance` declares a non-empty `fill`.

An internal `domain_visual` part may declare a fill because it describes a
bounded element within the transparent visual, not the visual's root region.

- On one root-to-content path, at most one bounded content node may own an
  app-authored surface; its descendants remain transparent.
- `borderWidthDp` and `borderColor` are not part of node `appearance`.
  Standard SpatialUI controls may retain their library-owned boundaries and
  focus indicators.
- `material` is not part of node `appearance`, and `rootMaterial` is not part
  of `theme`. Window and standard-component materials are system-owned runtime
  behavior, not design facts.
- `radiusDp` alone does not create a surface and is not counted as one.
- The system-provided window background is not represented in this contract and
  is not counted as an app-authored nested surface.

After schema validation and before rendering, run:

```bash
python3 scripts/check_design_surface_discipline.py <path-to-design-spec.json>
```

Errors block Preview generation. A high ratio of surfaced nodes is a review
warning only.

## Minimal example

```json
{
  "schemaVersion": "1.0",
  "metadata": {
    "projectName": "Focus Queue",
    "sourceMode": "intent_only",
    "revision": 1
  },
  "experience": {
    "subject": "triage",
    "user": "operations lead",
    "context": "seated at a shared desk",
    "singleJob": "select the next incident to resolve",
    "space": "shared",
    "form": "planar",
    "signature": "priority lane"
  },
  "theme": {
    "scheme": "vibrant",
    "colorScheme": {
      "fillPrimary": { "source": "vibrant", "role": "fillPrimary" },
      "fillSecondary": { "source": "vibrant", "role": "fillSecondary" },
      "fillTertiary": { "source": "vibrant", "role": "fillTertiary" },
      "fillLight": { "source": "vibrant", "role": "fillLight" },
      "labelPrimaryLight": { "source": "vibrant", "role": "labelPrimaryLight" },
      "labelPrimary": { "source": "vibrant", "role": "labelPrimary" },
      "labelSecondary": { "source": "vibrant", "role": "labelSecondary" },
      "labelTertiary": { "source": "vibrant", "role": "labelTertiary" },
      "labelQuaternary": { "source": "vibrant", "role": "labelQuaternary" },
      "lightenHover": { "source": "vibrant", "role": "lightenHover" },
      "lightenPressed": { "source": "vibrant", "role": "lightenPressed" },
      "error": { "source": "vibrant", "role": "error" },
      "alert": { "source": "vibrant", "role": "alert" },
      "passable": { "source": "vibrant", "role": "passable" },
      "interaction": { "source": "vibrant", "role": "interaction" },
      "dividerLine": { "source": "vibrant", "role": "dividerLine" }
    },
    "brandColors": { "queueAccent": "#66E0FF" },
    "typography": {
      "display": { "family": "sans-serif", "sizeDp": 40, "lineHeightDp": 48, "weight": 600 },
      "body": { "family": "sans-serif", "sizeDp": 16, "lineHeightDp": 24, "weight": 400 },
      "label": { "family": "sans-serif", "sizeDp": 14, "lineHeightDp": 20, "weight": 500 }
    },
    "spacing": { "small": 8, "regular": 16, "medium": 24, "large": 32 }
  },
  "surfaces": [
    {
      "id": "main",
      "type": "planar",
      "defaultSize": { "width": 1120, "height": 720, "unit": "dp" },
      "minSize": { "width": 720, "height": 540, "unit": "dp" },
      "maxSize": { "width": 1440, "height": 900, "unit": "dp" },
      "rootNodeId": "queue"
    }
  ],
  "initialStateId": "queue-state",
  "states": [{ "id": "queue-state", "surfaceRoots": { "main": "queue" } }],
  "transitions": [],
  "actions": [],
  "dataCases": {
    "normal": { "items": [{ "title": "Network latency" }] },
    "fallback": { "items": [] },
    "error": { "message": "Queue unavailable" }
  },
  "nodes": [
    {
      "id": "queue",
      "kind": "layout",
      "layout": { "mode": "column", "gapDp": 16, "paddingDp": 32 },
      "children": ["title"]
    },
    {
      "id": "title",
      "kind": "text",
      "content": "Focus Queue",
      "textStyle": { "typography": "display", "color": "labelPrimary" }
    }
  ],
  "responsiveRules": [],
  "assets": []
}
```

## JSON to SpatialUI Web rendering

Build `preview.html` only after the JSON passes a structural review:

1. Inline the complete vendored `spatialui.bundle.js`.
2. Embed an exact JSON snapshot in
   `<script id="pico-design-spec" type="application/json">`.
3. Leave product markup as a mount point. Parse the embedded spec and render
   surface roots by resolving the active state's node IDs.
4. Apply each declared fill through the single canonical Preview rule
   `[data-design-surface] { background:
   var(--pico-design-surface-fill); }`. Set `data-design-surface` from the node
   ID, create each filled node once, and do not write background declarations
   for renderer-specific classes.
5. Install the unchanged Vibrant theme. Every entry in `theme.colorScheme`
   references its same-name SpatialUI role; resolve custom `brandColors`
   separately without overriding the built-in scheme.
5. Instantiate `spatialui` nodes as their declared `sui-*` custom elements.
   Apply declared props/bindings and listen to documented public events.
   Resolve bundled and custom icon assets to their exact inline `currentColor`
   SVG in the documented icon slot.
6. Dispatch the referenced action from `events`; actions perform local state
   mutation or invoke a transition. Render confirmation through the mapped
   SpatialUI dialog component.
7. Render normal/fallback/error data through the same node tree. Do not create a
   separate debug UI to switch cases.
8. Apply responsive rules within each surface's min/default/max range.

The renderer may contain algorithms, component adapters, and
`domain_visual` implementations. It may not contain product-specific text,
colors, dimensions, assets, node ordering, states, or transition targets.

## Iteration and visual acceptance

Use the rendered SpatialUI Web page as the design feedback surface. Inspect it
at every surface's default size and at least its minimum width, exercise every
transition, and inspect normal/fallback/error cases. Iterate until hierarchy,
spacing, typography, contrast, assets, responsive behavior, and the signature
element meet the quality bar.

Every design correction follows this order:

1. edit `design-spec.json`;
2. increment `metadata.revision`;
3. regenerate the embedded snapshot and rendered HTML;
4. re-run interaction and visual review.

Change renderer code directly only to fix a generic mapping/rendering defect or
to implement a declared `domain_visual.rendererKey`. A visually accepted
`preview.html` with stale or divergent JSON is a blocking failure.

## Downstream handoff

`spatial-design-to-app` reads `design-spec.json` first:

- `surfaces` drives container/window evidence and constraints;
- `nodes` drives hierarchy and component conversion;
- `theme` drives `PicoTheme` and exact design colors;
- `initialStateId`, `states`, `transitions`, `actions`, and `dataCases` drive
  ViewModel/UI state;
- `responsiveRules` drives adaptive Compose layout;
- `assets` drives resource acquisition and attribution.

The downstream workflow may consult `preview.html` to understand the accepted
visual result, but it must not reverse-engineer implementation facts from HTML
or CSS when the JSON already owns them.
