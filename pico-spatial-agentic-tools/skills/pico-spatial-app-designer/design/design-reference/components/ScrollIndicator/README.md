# ScrollIndicator

A floating scroll bar for a scrolling view. Vertical 18x120, horizontal 120x18.

## Details
- Layers: background `fillLight` (radius 16, hidden until hovered), then a 6dp inset area holding the track (`labelPrimary`, alpha 0.2, 0.5 on hover, radius 2) and the indicator (`labelPrimary`, alpha 0.5, 1 on hover). The inset area is scaled to 96/108 along the axis at rest and to 1 on hover. Hover transitions take 0ms.
- Pressing hides the track and shows 2dp scroll marks (alpha 0.8) that move with the offset; dragging scrolls the view. It only shows when the content scrolls.

## When to use
- **Use for:** long lists and menus where position matters. `TextArea` and `Menu` can show one.
- **Don't use for:** progress (use `LinearProgress`), pages (use `PageControl`).
- **Alternatives:** none; the system draws no other scroll bar.
- **Do:** place it 3dp outside the right edge of the scrolling content; add 15dp of hot area on the touch side.
- **Don't:** show it on content that fits.

## Web API
- `<sui-scroll-indicator>` attributes: `for` (id of a scrolling element to follow and drive), `orientation`, `fraction` (position 0 to 1), `thumb-fraction` (visible share), `length`, `track-color`, `thumb-color`, `background-color`, `marks-color`.
- Events: `scroll-request` (`detail.fraction`) when dragged.
- Both `<sui-scroll-indicator>` and `<sui-basic-scroll-indicator>` bind to a separate scrollable element via `for`. Neither accepts a content slot. The target needs a constrained viewport and `overflow: auto` on the intended axis; do not set fixed `fraction` or `thumb-fraction` values when demonstrating live scrolling.

```html
<div id="items" style="height:216px;overflow-y:auto">
  <!-- Enough list content to exceed the viewport. -->
</div>
<sui-scroll-indicator for="items"></sui-scroll-indicator>
```

## Preview and shared rules

[Open this family’s preview](preview.html). The disconnected fraction-only examples and unsupported Basic content slot have been replaced with bound vertical and horizontal lists, plus a Basic example that switches between fitting and overflowing content. Scroll the content or drag the indicator to check both directions of synchronization. Indicator appearance and pressed scroll marks retain the runtime defaults; list dimensions and card styling belong to the demo. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
