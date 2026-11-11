# Icon

A single ICON 7.0 icon with editable size, tint and accessible description.

## Web API
- `<sui-icon>`: `name`, `size`, `tint`, `semantic-label`; `src` accepts a custom monochrome SVG silhouette (see the adaptation notes below).

## Local catalog and tint

All 896 supplied local icons are available through unique catalog names and stable IDs. Use [English search and the icon browser](../../assets/icons/README.md) before drawing. The runtime contains the full catalog, not only the original example names. Duplicate names require a stable ID.

Independent Icon default: system primary foreground. `tint="#3377ff"` explicitly changes it. In a control's slot, an untinted Icon uses that control's foreground; a dark primary Button therefore gives it the same white as the label. Explicit tint wins. Change a Button's `content-color` to change text and icon together. The added preview shows default, explicit, slotted, custom control and disabled examples.

`src` is a monochrome alpha-mask source in this bundle, so tint also applies. Use same-origin SVG URLs served over HTTP. Prefer catalog `name` for local library assets; it works offline without fetching. No multicolor or `tint="none"` mode is exposed in this Plan. [Drawing rules](../../assets/icons/drawing.md) explain missing-asset production and transparent cutouts.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
