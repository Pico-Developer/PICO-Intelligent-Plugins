# SpatialPopup

An anchored surface for contextual content. Web placement approximates the native popup.

## Defaults and caller-owned content

- Minimum width 360 and height 184, radius 20, `Thick` material; constrained to the owning window in native and the available viewport in Web. The browser reserves an 8px edge guard.
- No built-in content padding, title region or Done button. The caller supplies content layout and spacing. Both examples explicitly use a 360px-wide content region with 24px padding; this is not a component inset.
- The native default position uses `HorizontalPlacement.alignStart()` and `VerticalPlacement.above(offset = 8.dp)`. The vertical offset is a signed coordinate adjustment: above is `anchor.top - popup.height + offset`, while below is `anchor.bottom + offset`. Positive 8 moves the popup down; it does not mean an 8px gap above the anchor.
- Outside click and Escape dismiss by default. Selection inside general popup content does not automatically dismiss it as a Menu command would.

## Web API
- `<sui-spatial-popup>`: `for` (anchor element ID), `hidden`, `corner-radius`, `default-min-width`, `default-min-height`, `disable-material-background`, `semantic-label`, `dismiss-on-click-outside`, `dismiss-on-escape`, `horizontal-placement`, `vertical-placement`, `offset-x`, `offset-y`. Default slot: content.
- `horizontal-placement`: `align-start` (default), `align-end`, `center`, `to-start`, `to-end`. `vertical-placement`: `above` (default), `below`, `align-top`, `center`, `align-bottom`. Offsets default to x=0 and y=8. These Web attributes express choices made through native `rememberSpatialPopupPositionProvider`; they are not invented Compose parameters.
- Use `default-min-width="0" default-min-height="0"` for an explicit content-sized Web example; native uses `Dp.Unspecified`. Removing the overrides restores the 360×184 baseline. Always provide `for` in an anchored example; the no-anchor inline fallback does not demonstrate native attachment.
- `dismiss-request` reports outside click or Escape.

## Two anchor examples

The preview uses one compact 456px-wide stage. Its IconButton/Button selector switches the anchor example in the same 248px-high canvas; only one example is visible at a time. Each example opens immediately when selected, keeping the popup itself visible as the reference. The canvas height accommodates the 184px popup, its anchor and the gap; it is not an application page or a Sheet height.

1. **Volume:** a Regular IconButton (`ic_volume_loud`) is the anchor. The popup uses above/start positioning with an explicit `offset-y="-8"`, leaving an 8px gap above the button and keeping its focus outline visible. This example override does not change the SDK-aligned default offset of +8. A SymbolSlider updates the percentage immediately; no Done action is needed. Closing and reopening preserves the value.
2. **File details:** a Small text Button with `ic_info_circle` is a different anchor. Its popup explicitly uses below/end positioning and contains a 24px `ic_document` plus file metadata. It is read-only, so outside click or Escape closes it.

Each trigger has its own ID and matching popup `for`. Opening one closes the other. Click the active trigger to close/reopen, or close through outside click/Escape. Popups sit outside content containers that might clip them. Web geometry follows anchor movement and scroll; overflow can flip above/below and clamp horizontally to remain visible. This browser edge policy is a preview convenience, not a claim that native placement automatically flips in the same way. Validate native spatial placement separately.

## Plan composition boundary

Use the family for its stated purpose: commands (Menu), anchored content (SpatialPopup), guidance (Coachmark), or transient feedback (Snackbar). The title-bar close rule for task surfaces does not mean adding a TitleBar to these compact components. Keep ownership, trigger and dismissal clear, avoid a second wrapper background over the built-in surface, and use named local icons where an action needs one. See [general rules](../../general-rules.md) for operation scope and color choices.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
