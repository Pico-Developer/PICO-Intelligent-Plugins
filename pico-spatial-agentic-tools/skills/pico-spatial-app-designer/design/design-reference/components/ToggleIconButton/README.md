# ToggleIconButton

A round icon button with a checked state. Colors are the `ToggleButton` ones (`fillSecondary` checked, `fillTertiary` unchecked, `labelPrimary` content); the shape is a circle.

## Sizes
- Min 38x32 (default), Small 46x40, Regular 56x48, Max 66x56. Icon sizes as `IconButton`.

## States
- Checked and unchecked by container color. Disabled alpha 0.3. Hover is the native spatial hover effect on a PICO device (gaze or ray), not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white) under the content.

## When to use
- **Use for:** an icon that is on or off: favorite, mute, bookmark.
- **Don't use for:** a one-shot action (use `IconButton`) or a setting with a label (use `Switch`).
- **Alternatives:** `ToggleButton` when a label is needed, `Checkbox` for list selection.
- **Do:** change the icon (outlined to filled) as well as the fill when the state flips.
- **Don't:** rely on the faint fill difference alone; add a tooltip or label for unfamiliar icons.

## Web API
- `<sui-toggle-icon-button>` attributes: `icon`, `checked`, `size`, `disabled`, `container-color`, `content-color`, `checked-container-color`.
- Events: `checked-change` (`detail.checked`), `click-action`.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
