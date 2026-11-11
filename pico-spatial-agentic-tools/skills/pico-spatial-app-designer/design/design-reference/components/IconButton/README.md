# IconButton

A capsule that holds one icon. Same fill as `Button` (`fillPrimary` with `labelPrimaryLight`), no padding, radius 35.

## Sizes
- Max 66x56, Regular 56x48 (default), Small 46x40, Min 38x32 (minimum sizes; the icon is centered).
- Icon sizes used by the SDK samples: 24 / 20 / 18 / 16. `Icon` itself defaults to 24.
- `IconButtonDefaults.iconButtonSize(size)` gives a fixed square for custom shapes.

## States
- Disabled: alpha 0.3.
- Hover is the native spatial hover effect on a PICO device (gaze or ray), not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white) under the content.

## When to use
- **Use for:** a single, well-known action where an icon says enough: add, edit, close, share. Toolbars, title bars and sheet headers.
- **Don't use for:** an action that needs words (use `Button`), a persistent on/off (use `ToggleIconButton`), a close button inside a `Sheet` (the sheet supplies one).
- **Alternatives:** `Button` with a leading icon when the label helps, `ToggleIconButton` for state, `Link` for text in a paragraph.
- **Do:** use an outlined glyph and a Small or Regular size in toolbars; give it an accessible label.
- **Don't:** use an unfamiliar icon without a label nearby; put more than a few in one row.

## Web API
- `<sui-icon-button>` attributes: `icon` (built-in icon name such as `plus`, a built-in glyph such as `close`, or text), `size`, `disabled`, `container-color`, `content-color`. Put an `<svg>` in the default slot for a custom icon.
- Events: `click-action`.

## Plan composition

Use a named local icon and an accessible action label (`semantic-label`). Close/back belongs in the title region's leading position; concise auxiliary actions may be trailing. Keep substantial submit actions in the task's bottom action region. Prefer `content-color` to recolor the icon and `container-color` for its shell; do not stack an extra wrapper background/hover effect over the built-in control. The default/state color comes from the IconButton; use an explicit child Icon tint only for a deliberate exception.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
