# Button

The primary action control: a clipped capsule on a solid `fillPrimary` fill with `labelPrimaryLight` text. Four fixed sizes; the width grows with the label.

## Sizes (dp = px)
- Max: min 104x56, radius 32, text 20/26 Medium, padding 24.
- Regular: min 81x48, radius 102 (full pill), `titleMedium` (16/20, 600), padding 20. Default.
- Small: min 69x40, radius 20, `labelLarge` (14/18, 600), padding 16.
- Min: min 57x32, radius 16, `labelMedium` (12/16, 600), padding 12.
- With a leading or trailing icon the minimum width and padding grow: width 120/104/85/71 and padding 24/24/20/16 (Max/Regular/Small/Min), gap 8/4/4/2. The SDK samples size icons 22/18/16/14.

## States
- Disabled: whole control at alpha 0.3, not clickable.
- Hover is the native spatial hover effect on a PICO device (gaze or ray), not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white) under the content.

## When to use
- **Use for:** the action the wearer takes in a window: Continue, Save, Delete, Join. One Regular or Max button is the primary action.
- **Don't use for:** switching a setting on or off (use `Switch`), toggling a pressed state (use `ToggleButton`), navigation inside text (use `Link`), a square icon-only action (use `IconButton`).
- **Alternatives:** `Link` for a quiet text action, `IconButton` for an icon, `ToggleButton` for a persistent on/off, `Chip` for a filter or tag action.
- **Do:** keep labels to a verb or one noun, sentence case; give every button in a row the same size; put the primary action on the right in a dialog.
- **Don't:** mix sizes in one row; put two primary buttons side by side; truncate a label (strings ship in 30+ locales and the button grows).

## Web API
- `<sui-button>` attributes: `size` (`max`, `regular`, `small`, `min`), `text`, `disabled`, `leading-icon`, `trailing-icon` (built-in icon name), `container-color`, `content-color`. The default slot replaces `text`; slots `leading` and `trailing` take your own icons.
- Events (bubbling `CustomEvent`, payload in `detail`): `click-action`.

## Plan composition: alignment and compact widths

For one or several buttons in a sufficiently wide action row, align the group right; the parent owns the 8 gap. In a narrow content region, one primary button should usually fill the available width. The preview includes both arrangements without changing Button's default minimum size. Multiple buttons in a narrow region may share width or stack according to priority and label length; do not truncate labels.

Use `leading-icon`/`trailing-icon` for a local icon that shares the Button's content color. An explicitly tinted slotted Icon may differ intentionally. Keep rich multi-line content and multiple independent actions out of a Button shell. See [operation placement](../../general-rules.md#operation-placement).

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
