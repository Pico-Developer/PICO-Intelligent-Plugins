# SpatialUI Web Guide

`preview.html` must use the vendored SpatialUI Web components in
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

For every interactive or system-semantic element, use the matching `sui-*`
component when one exists:

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

Custom HTML/CSS is still appropriate for domain-specific visualization,
spatial canvas content, data graphics, media, and layout wrappers. It must not
reimplement a button, field, selector, dialog, menu, switch, chip, or other
catalog component merely to change its appearance.

## Theme the library, not around it

The bundle installs `PicoTheme` with `scheme: "vibrant"` by default. Preserve
that glass baseline and install the design's complete scheme through
`window.PicoTheme.install({ scheme: "vibrant", colorScheme: { ... } })`.
Start from `PicoTheme.vibrantColorScheme()`, explicitly forward all 16 roles,
and replace the roles whose exact values are specified by the design. Do not
submit a partial color object whose omitted behavior is implicit.

The app root must use SpatialUI Web's `Material.Regular` glass variable/style.
Do not reproduce it with a custom translucent fill or custom blur. A page-level
room image or neutral color may exist behind the glass only as preview context.

Use component attributes and CSS custom properties exposed by the runtime.
Do not pierce component shadow roots or duplicate their internal CSS.

## Keep `preview.html` self-contained

The final prototype remains one offline HTML file:

1. Read `../assets/spatialui-web/spatialui.bundle.js`.
2. Paste its complete contents into one inline `<script>` in `preview.html`.
3. Put the app state machine in a later inline `<script>`.
4. Do not leave an absolute path, `file://` URL, module import, CDN, or runtime
   fetch in the output.

The vendored bundle contains no `</script>` token, so direct inline embedding is
safe. Do not minify or rewrite it while generating a design.

## Event wiring

Listen to each component's emitted `CustomEvent`, not its shadow-DOM internals.
Typical events include `click-action`, `checked-change`, `value-change`,
`select`, `date-select`, and `dismiss-request`; confirm the exact name and
`detail` shape in the component source.

## Required component map

Before Build, add one row per planned control or system surface:

| Planned element | SpatialUI tag | API checked in | Event/state | Custom fallback reason |
| --------------- | ------------- | -------------- | ----------- | ---------------------- |

The fallback reason must be specific. "Easier to style" and "faster to build"
are not valid reasons.

After Build, record the stable selector for each row and verify:

- the tag is registered in `window.SUI_COMPONENTS`;
- the element is present and reachable in the relevant state;
- the intended event changes visible app state;
- disabled, fallback, error, and confirmation states use library components
  where applicable;
- no native `<button>`, `<input>`, `<select>`, `<textarea>`, or hand-rolled
  dialog duplicates an available `sui-*` component.
- the product UI contains no layout-tier, viewport-preset, token, data-mode, or
  coverage controls introduced only for design review.
