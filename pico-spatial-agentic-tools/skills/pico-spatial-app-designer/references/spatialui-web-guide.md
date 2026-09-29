# SpatialUI Web Guide

`preview.html` must render the `spatialui` nodes declared in
`design-spec.json` with the vendored SpatialUI Web components in
`../assets/spatialui-web/`. They are the design-time Web counterparts of PICO
SpatialUI components, not optional decoration.

## Read in this order

1. `../assets/spatialui-web/COMPONENT_PARITY.md` to choose the closest native
   component.
2. The matching file under `../assets/spatialui-web/js/` to verify attributes,
   slots, emitted events, defaults, and states.
3. `../assets/spatialui-web/README.md` for theme and overlay usage.

Do not guess a component API from its tag name.

## Component-first rule

For every interactive or system-semantic element, declare and render the
matching `sui-*` component when one exists:

- commands: `sui-button`, `sui-icon-button`
- modes and selection: `sui-segment-control`, `sui-tab-bar`, `sui-option`,
  `sui-checkbox`, `sui-switch`, chips
- inputs: `sui-text-field`, `sui-search-field`, `sui-number-field`,
  `sui-slider`, `sui-stepper`, date/time pickers
- structure: `sui-title-bar`, `sui-side-navigation`, `sui-list-item`,
  `sui-divider`, progress and page controls
- overlays and feedback: `sui-alert-dialog`, `sui-sheet`, `sui-menu`,
  `sui-spatial-popup`, `sui-snackbar-host`, `sui-coachmark`
- spatial attachments: `sui-augment`, `sui-toolbar`, `sui-subwindow`

Custom HTML/CSS is still appropriate for a declared `domain_visual`, spatial
canvas content, data graphics, media, and generic layout rendering. Its
`rendererKey`, data, dimensions, colors, and interaction bindings live in
`design-spec.json`. It must not reimplement a button, field, selector, dialog,
menu, switch, chip, or other catalog component merely to change its appearance.

## TitleBar composition

Treat `sui-title-bar` as a composable header rather than a title string with
singleton action placeholders:

- the `title` slot may contain structured content such as a row of title text
  and a `sui-search-field`;
- the `leading` and `trailing` slots may each contain multiple controls;
- search that is app-wide or persists across the primary content modes belongs
  in the title bar unless an explicit design requirement places it elsewhere;
- search scoped to one content region stays with that region.

For a title plus global search, render both as one title-slot composition while
keeping window or navigation actions in their existing action slots:

```html
<sui-title-bar>
  <div slot="title">
    <sui-text>App title</sui-text>
    <sui-search-field placeholder="Search"></sui-search-field>
  </div>
  <sui-icon-button slot="leading"></sui-icon-button>
  <sui-icon-button slot="leading"></sui-icon-button>
  <sui-icon-button slot="trailing"></sui-icon-button>
  <sui-icon-button slot="trailing"></sui-icon-button>
</sui-title-bar>
```

The exact labels, controls, and spacing still come from the accepted design.
Do not split a composed title bar into a title bar followed by a duplicate
header row merely because it contains more than one control.

## Icon slots

Read [`icon-selection.md`](./icon-selection.md) when a mapped component has an
explicit icon slot. Resolve a selected `icon70://7.0/<name>` to its bundled SVG
or a `design-assets/icons/*.svg` source to the custom drawing produced during
Build, then insert the complete SVG as slotted content. Both forms use
`currentColor`, so the owning `sui-*` component controls tint.

Do not use the `glyph` or `icon` string convenience attributes for delivered
icons, and do not substitute emoji or Unicode symbols. Do not use
`sui-icon[src]` because its `<img>` cannot inherit the component tint. Built-in
semantic controls such as `sui-search-field` do not need an extra decorative
icon node.

## Theme the library, not around it

The bundle installs `PicoTheme` with `scheme: "vibrant"` by default. Keep that
native `ColorScheme` unchanged: every `theme.colorScheme` entry must reference
the same-name Vibrant role. Custom colors belong in `theme.brandColors` and may
be applied through app-owned CSS variables or component attributes; never pass
them as overrides to `PicoTheme.install(...)`.

The app root must use SpatialUI Web's `Material.Regular` glass variable/style.
Do not reproduce it with a custom translucent fill or custom blur. Behind the
glass, the page `body` uses the fixed light neutral preview environment
`#DAD6D3` with no background image. This renderer-owned color is not part of the
app theme or `design-spec.json`.

Use component attributes and CSS custom properties exposed by the runtime.
Do not pierce component shadow roots or duplicate their internal CSS.

## Keep `preview.html` self-contained

The final prototype remains one offline HTML file:

1. Read `../assets/spatialui-web/spatialui.bundle.js`.
2. Paste its complete contents into one inline `<script>` in `preview.html`.
3. Embed an exact `design-spec.json` snapshot in
   `<script id="pico-design-spec" type="application/json">`.
4. Put the generic node renderer and app state engine in a later inline
   `<script>`. Product values come from the parsed JSON.
5. Do not leave an absolute path, `file://` URL, module import, CDN, or runtime
   fetch in the output.

The vendored bundle contains no `</script>` token, so direct inline embedding is
safe. Do not minify or rewrite it while generating a design.

## Event wiring

Listen to each component's emitted `CustomEvent`, not its shadow-DOM internals.
Typical events include `click-action`, `checked-change`, `value-change`,
`select`, `date-select`, and `dismiss-request`; confirm the exact name and
`detail` shape in the component source.

## Required component map

Before Build, add one `kind: "spatialui"` node per planned control or system
surface in `design-spec.json` and summarize the mapping in `design-doc.md`:

| Planned element | SpatialUI tag | API checked in | Event/state | Custom fallback reason |
| --------------- | ------------- | -------------- | ----------- | ---------------------- |

The fallback reason must be specific. "Easier to style" and "faster to build"
are not valid reasons.

After Build, record the stable selector for each node and verify:

- the tag is registered in `window.SUI_COMPONENTS`;
- the rendered tag and props came from the matching JSON node;
- the element is present and reachable in the relevant state;
- the intended event changes visible app state;
- disabled, fallback, error, and confirmation states use library components
  where applicable;
- every declared icon asset resolves to exact inline SVG geometry in its
  intended slot and inherits the intended tint;
- no native `<button>`, `<input>`, `<select>`, `<textarea>`, or hand-rolled
  dialog duplicates an available `sui-*` component.
- the product UI contains no layout-tier, viewport-preset, token, data-mode, or
  coverage controls introduced only for design review.
