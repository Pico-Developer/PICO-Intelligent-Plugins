# Switch

An immediate on/off control. Hit box 40x36 around a 32x20 pill track and a 16 thumb inset 2, so the thumb travels 12.

## Details
- Checked track `interaction` (blue); unchecked track `fillTertiary` with an inner shadow (`0x14000000`, blur 20) that fades out as it turns on. Thumb `labelPrimaryLight` in both states.
- The thumb moves on spring `rapid` (damping 1, stiffness 850, about 390ms).
- No pressed overlay: the `Switch` draws no indication. On device hover is the native effect.
- Disabled: alpha 0.3.

## When to use
- **Use for:** a setting that takes effect the moment it flips: Wi-Fi, Do not disturb, Passthrough.
- **Don't use for:** a choice that is confirmed later with a button (use `Checkbox`), picking one of several (use `Option` or `SegmentControl`), a state that is an action (use `ToggleButton`).
- **Alternatives:** `Checkbox` for batch choices, `ToggleButton` or `ToggleIconButton` for toolbar toggles, `Option` for one-of-many.
- **Do:** put it in the trailing slot of a `ListItem` with the setting name as the headline.
- **Don't:** label it with the action ("Turn on Wi-Fi"); label the setting ("Wi-Fi") and let the switch show the state.

## Web API
- `<sui-switch>` attributes: `checked`, `disabled`, `checked-track-color`, `track-color`, `thumb-color`.
- Events: `checked-change` (`detail.checked`).

## Preview and shared rules

[Open this family’s preview](preview.html). The first section retains the four original on/off and disabled examples with text descriptions. The second composes a Bluetooth ListItem: a 24px `ic_bluetooth` leading icon, the setting name, and a Switch in the trailing slot, initially on. Click the Switch or activate it with Enter/Space to change its state immediately; there is no Save/Done step, separate status message or simulated device connection.

The example uses explicit 16px ListItem insets and allows the row to shrink below its default 360px minimum on narrow screens. Switch dimensions and colors retain their defaults. The setting name is also supplied as the Switch's `semantic-label`.

See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
