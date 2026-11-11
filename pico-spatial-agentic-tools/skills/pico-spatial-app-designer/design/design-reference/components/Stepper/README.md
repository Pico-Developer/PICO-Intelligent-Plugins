# Stepper

A compact increase and decrease control with the value between. 152 wide (minimum 115), at least 40 high, radius 10, `fillTertiary`, padding 4.

## Layout
- Two icon buttons 44x32 with a transparent container and glyph color `fillLight`; the value is `titleMedium` at normal weight (16/20, 400) in `labelPrimary`, centered with 4 horizontal padding.
- Glyphs: minus and add  or arrows . Pressing a button clears focus.
- On the non-vibrant fallback `fillLight` is 15% white, so the glyphs are faint on a light backdrop; set `button-color` to `labelPrimary` there. `increasable` and `decreasable` dim a button to 0.3. Hover is the native spatial hover effect on a PICO device, not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white).

## When to use
- **Use for:** small integer steps: copies, items, steps.
- **Don't use for:** large ranges (use `Slider` or `NumberField`), anything that needs a unit and typing (use `NumberField`).
- **Alternatives:** `NumberField`, `Slider`.
- **Do:** disable the end of the range with `increasable` / `decreasable`.
- **Don't:** use two for a range.

## Web API
- `<sui-stepper>` attributes: `value`, `step`, `editable`, `increasable`, `decreasable`, `icon-style` (`arrow`), `disabled`, `width`, `container-color`, `text-color`, `button-color`.
- Events: `step` (`detail.step`, signed), `value-change` (when edited). The element does not change `value` itself; update it from `step`.

## Preview and shared rules

[Open this family’s preview](preview.html). The minus/plus and arrow examples each start at 3 and maintain independent values. The example listens for `step`, adds `detail.step`, clamps the result to 1–5, then writes it back to `value`. At 1 it sets `decreasable="false"`; at 5 it sets `increasable="false"`. Moving away from an endpoint enables that button again. The range is an example choice, not a component default or built-in min/max API. The examples remain read-only in the middle and retain the original dimensions and explicit dark glyph color.

See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
