# SpatialUI · Web Component Library

A framework-free Web Custom Element port of the PICO **SpatialUI** design system
(`spatialui/design`). Each Kotlin/Compose component gets its own JS file, driven
by design tokens lifted verbatim from the Kotlin source.

## Layout

```
spatialui-web/
├── index.html          # Live component gallery / preview page
└── js/
    ├── tokens.js        # ColorTokens, ColorScheme, Dimension, TypeScale (from *Tokens.kt)
    ├── base.js          # SuiElement base class + shared helpers
    ├── index.js         # Barrel: registers every element, installs theme vars
    └── <component>.js    # One file per component (button.js, switch.js, …)
```

## Source of truth

| Web token                     | Kotlin source                                                      |
| ----------------------------- | ------------------------------------------------------------------ |
| `ColorTokens` / `ColorScheme` | `tokens/ColorTokens.kt`, `ColorScheme.kt` (`defaultColorScheme()`) |
| `Dimension`                   | `tokens/DimensionTokens.kt`                                        |
| `TypeScale`                   | `tokens/TypeScaleTokens.kt`                                        |

Compose `Color(0xAARRGGBB)` literals are converted to CSS `rgba()` via `argb()`.
Sizes are dp → px 1:1.

## Components

`sui-text`, `sui-icon`, `sui-button`, `sui-icon-button`, `sui-toggle-button`,
`sui-switch`, `sui-checkbox`, `sui-badge` / `sui-dot-badge` / `sui-number-badge`,
`sui-chip`, `sui-slider`, `sui-linear-progress` / `sui-circular-progress`,
`sui-divider`, `sui-segment-control`, `sui-tab-bar`, `sui-text-field`, `sui-search-field`,
`sui-number-field`, `sui-stepper`, `sui-link`, `sui-list-item`, `sui-page-control`,
`sui-option`, `sui-side-navigation`, `sui-title-bar`, `sui-scroll-indicator`,
`sui-wheel-picker` / `sui-timepicker`, `sui-date-picker`, `sui-augment`,
`sui-spatial-popup`.

The extended parity set also includes `sui-toggle-icon-button`,
`sui-symbol-slider`, `sui-segment-slider`,
`sui-symbolic-circular-progress`, `sui-progress-page-control`,
`sui-date-range-picker`, `sui-stereo-image`, `sui-menu` /
`sui-sub-menu` / `sui-menu-item`, `sui-alert-dialog`,
`sui-date-picker-dialog`, `sui-sheet` / `sui-head-image-sheet`,
`sui-snackbar-host`, `sui-coachmark`, `sui-toolbar` and
`sui-subwindow`. Explicit alias elements are available for public Compose
variants such as `sui-text-area`, `sui-tri-state-checkbox`,
`sui-button-chip` and `sui-horizontal-divider`.

See [COMPONENT_PARITY.md](./COMPONENT_PARITY.md) for the complete public
Composable-to-Custom-Element mapping and the few non-visual infrastructure APIs
that intentionally do not create DOM elements.

## Usage

```html
<script type="module" src="./js/index.js"></script>

<sui-button size="regular" text="Continue"></sui-button>
<sui-switch checked></sui-switch>
<sui-slider size="regular" value="0.5"></sui-slider>
```

Components emit bubbling `CustomEvent`s (`click-action`, `checked-change`,
`value-change`, `select`, `date-select`, …) with a `detail` payload.

## Floating containers

`sui-augment` mirrors the SDK `Augment`: it attaches an ornament to a host
window using normalized `anchor` and `alignment` points. `sui-spatial-popup`
mirrors `SpatialPopup`: it is positioned relative to an anchor element and
emits `dismiss-request` for outside-pointer or Escape dismissal. Both use the
browser top layer when the Popover API is available and otherwise fall back to
a fixed overlay. They follow host resize, page resize, and scrolling.

```html
<div id="window-content">...</div>

<sui-augment for="window-content" anchor="TopFront" alignment="BottomCenter" offset-y="-16">
  <div style="padding: 16px 24px">Floating toolbar</div>
</sui-augment>

<sui-button id="popup-anchor" text="Open popup"></sui-button>
<sui-spatial-popup
  id="popup"
  for="popup-anchor"
  horizontal-placement="align-start"
  vertical-placement="above"
  offset-y="-8"
  hidden
>
  <div style="padding: 24px">Popup content</div>
</sui-spatial-popup>

<script>
  const popup = document.querySelector('#popup');
  document.querySelector('#popup-anchor').addEventListener('click-action', () => {
    popup.hidden = false;
  });
  popup.addEventListener('dismiss-request', () => {
    popup.hidden = true;
  });
</script>
```

Augment attributes:

- `for`: host element ID; alternatively set the `anchorElement` property.
- `anchor`: host normalized point (`TopFront`, `bottom-right`, or `x,y,z`).
- `alignment`: normalized point on the augment content.
- `offset-x`, `offset-y`, `offset-z`, `rotation-x/y/z`, `corner-radius`.
- `window-size-behavior` (or the shorter `size-behavior` alias): `adaptive`,
  `match-container-width`, or `match-container-height`.
- `enable-material-background`: defaults to `true`; set to `false` for no
  system-style Regular glass.
- `focusable`: defaults to `true`.

SpatialPopup attributes:

- `for`: anchor element ID; alternatively set the `anchorElement` property.
- `horizontal-placement`: `to-start-of`, `align-start`, `center`,
  `align-end`, or `to-end-of` (start/end automatically follow LTR/RTL).
- `vertical-placement`: `above`, `align-top`, `center`, `align-bottom`,
  or `below`.
- `offset-x`, `offset-y` (defaults to the SDK 8px menu gap), `offset-z`,
  `corner-radius`, `default-min-width`, and `default-min-height`.
- `disable-material-background`: switches off the default Thick glass.
- `dismiss-on-click-outside`, `dismiss-on-escape`, and `focusable` default to
  `true`.
- `clipping-enabled` optionally constrains either container to the viewport;
  the SDK-compatible default is unclipped.

## Preview

Open `index.html` in any modern browser, or serve the folder:

```bash
cd spatialui-web && python3 -m http.server 8000
# → http://localhost:8000
```

The gallery renders every component with interactive states and logs events inline.
