# SearchField

A pill-shaped `TextField` for queries: 280 wide, at least 48 high, radius 100.

## Details
- Leading search glyph (20dp) tinted `labelQuaternary`; clear button while focused with text; Search is the keyboard action.
- Fill `fillTertiary`, `fillSecondary` while focused; text `bodyLarge` in `labelPrimary`; placeholder `labelQuaternary`. No error state. Hover is the native spatial hover effect on a PICO device, not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white).

## When to use
- **Use for:** filtering or finding content on a screen.
- **Don't use for:** entering a value into a form (use `TextField`), an in-page find with next and previous buttons.
- **Alternatives:** `TextField` with a leading icon for non-search text.
- **Do:** put it at the top of the list it filters; search on submit and as the wearer types only if results are cheap.
- **Don't:** place two search fields in one window.

## Web API
- `<sui-search-field>` attributes: `value`, `placeholder`, `disabled`, `width`, `container-color`, `text-color`, `placeholder-color`, `focus-color`.
- Events: `value-change`, `search` (Enter, `detail.value`).

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
