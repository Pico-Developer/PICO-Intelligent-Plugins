# TextArea

The multi-line `TextField`: same fill, radius 12, type and error rules, 280 wide and at least 48 high, content aligned to the top. It grows with its text up to `maxLines`.

## Layout
- Left padding 12, text padding 12 vertical, 12 on the right; no clear button or leading icon. Text `bodyLarge`, supporting text `bodySmall` 4 below.
- `showScrollIndicator` adds a `ScrollIndicator` 3dp outside the right edge. Hover is the native spatial hover effect on a PICO device, not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white).

## When to use
- **Use for:** notes, messages, descriptions.
- **Don't use for:** a single line (use `TextField`), a search query (use `SearchField`).
- **Alternatives:** `TextField` for one line.
- **Do:** set a minimum number of lines that matches the expected input; cap the height with `max-lines` when the window is short.
- **Don't:** use it for values that have a fixed format.

## Multi-line examples

The first preview keeps the SDK defaults: one initial line and no line-count cap. TextArea has no clear button, including while focused with text entered.

The additional Plan recommendation uses `min-lines="3"` and `max-lines="6"` for notes. The three examples show an empty three-line area, content growing to four lines, and long content scrolling inside a six-line viewport. `max-lines` limits the visible height, not how much text can be entered; deleting text shrinks the area back to its minimum.

## Web API
- `<sui-text-area>` (or `<sui-text-field multiline>`) attributes: `value`, `placeholder`, `supporting-text`, `error`, `disabled`, `readonly`, `width`, `min-lines`, `max-lines`, colors as `TextField`.
- Events: `value-change`.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
