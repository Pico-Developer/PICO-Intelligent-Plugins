# Checkbox

A circular check control: a 32dp hit circle around an 18dp glyph circle (Small 14).

## Details
- Off: a ring, 1.5 stroke in `labelSecondary`. On: a filled `labelPrimary` circle with a white check . Indeterminate (`TriStateCheckbox`): the same fill with a horizontal bar.
- Turning on fades and scales the content in on spring `instant`; turning off swaps back at once.
- Hover is the native spatial hover effect on a PICO device (gaze or ray), not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white) under the content.

## When to use
- **Use for:** choices that are submitted together, or a "select all" with an indeterminate state (`TriStateCheckbox`).
- **Don't use for:** a setting that applies immediately (use `Switch`), one of several exclusive options (use `Option`).
- **Alternatives:** `Switch`, `Option`, `ToggleableChip` for tag-like multi-select.
- **Do:** pair it with a text label that is clickable too; use the indeterminate state for partial selection.
- **Don't:** use it alone as a standalone on/off setting.

## Web API
- `<sui-checkbox>` and `<sui-tri-state-checkbox>` attributes: `state` (`on`, `off`, `indeterminate`) or `checked`, `size` (`regular`, `small`), `disabled`, `background-color`, `content-color`, `border-color`.
- Events: `checked-change` (`detail.checked`, `detail.state`).

## Preview and shared rules

[Open this family’s preview](preview.html). The first section retains the six original state/size examples and adds clickable text labels. The second shows a Select all parent with Photos and Videos children, initially partially selected. Clicking a circle or its text toggles the same control; keyboard activation remains on the checkbox.

The parent shows `indeterminate` when some children are selected, `on` when all are selected, and `off` when none are selected. Activating a mixed parent selects all children; activating a checked parent clears them. This relationship is maintained by the example using `checked-change`; standalone Checkbox components do not discover or manage child items automatically. Labels use `semantic-label` to name the internal checkbox, and the disabled example remains unchanged when clicked.

See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
