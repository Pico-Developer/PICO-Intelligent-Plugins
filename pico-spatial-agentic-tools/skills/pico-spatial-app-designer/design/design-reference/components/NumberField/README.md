# NumberField

A numeric input with minus and plus buttons. 152 wide (minimum 100, Small 80), 40 high (Small 32), radius 12 (Small 8).

## Layout
- Fill `fillTertiary`, `fillSecondary` while focused. Two square buttons the size of the height with 4 padding, each a `fillLight` tile (radius 8, Small 4) holding an 18dp plus or minus glyph in `labelPrimary`. Gap 4.
- The value is centered, `bodyLarge` (Small `bodySmall`); an optional unit follows it with a 2dp gap and hides while editing. The value is checked and clamped to the range when focus leaves.
- A button dims to alpha 0.3 at the end of the range. Hover is the native spatial hover effect on a PICO device, not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white).

## When to use
- **Use for:** an exact number that is also often nudged: quantity, volume step, size.
- **Don't use for:** a value on a continuous scale (use `Slider`), a small step without typing (use `Stepper`), free text (use `TextField`).
- **Alternatives:** `Stepper`, `Slider`.
- **Do:** set a range and a step; show the unit.
- **Don't:** use it for IDs or phone numbers.

## Web API
- `<sui-number-field>` attributes: `value`, `min`, `max`, `step`, `size` (`small`), `unit`, `fraction-digits`, `editable`, `disabled`, `width`, `container-color`, `text-color`, `focus-color`.
- Events: `value-change` (`detail.value`, a number).

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).


## Plan recommendation · meaningful numeric fields

The additional preview section demonstrates application choices, not SDK defaults:

| Example | Initial value | Range | Button step | Unit / display |
| --- | --- | --- | --- | --- |
| Quantity | 3 | 1–10 | 1 | items, no decimal places |
| Weight | 72.0 | 0–100 | 0.5 | kg, one decimal place |
| Quantity · lower limit (Small) | 1 | 1–10 | 1 | items, no decimal places |
| Weight · upper limit | 100.0 | 0–100 | 0.5 | kg, one decimal place |

Every added field explicitly sets `min`, `max`, `step`, `unit` and `fraction-digits`, and has a field name and a live current-value summary. The unit remains in the surrounding description while the inline unit hides during editing.

At the minimum, decrease is dimmed and unavailable; at the maximum, increase is dimmed and unavailable. Moving away from the limit enables the corresponding button again. The two boundary examples expose these states immediately and remain interactive.

Use + / − for the stated increments. Direct typing commits on blur or Enter and clamps out-of-range values to the nearest limit. `step` describes button increments; it does not snap typed values to step multiples. `fraction-digits` controls display formatting rather than validating allowed input precision. For example, weight 99.5 → + → 100.0 disables increase; quantity 1 → + → 2 enables decrease. Typing 20 into Quantity and leaving the field commits 10.
