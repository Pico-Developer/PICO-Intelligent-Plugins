# WheelPicker

A list that snaps one row to the center. Rows 40 high with 4 margin (44 per row), 7 rows by default (308 high), padding 4 on the sides, clipped to a radius-12 shape.

## Details
- The selected row sits on a `fillSecondary` indicator (radius 12, 40 high, offset 2 in the row) and is drawn in `headlineLarge` (24/30, 700) in `labelPrimary`; other rows are `titleMedium` in `labelTertiary`, faded toward the edges (alpha 0, .5, 1 at 0%, 14%, 44% and the mirror). The rows under the indicator are hidden, and the indicator moves its own three texts with the scroll.
- Left and right text (`labelLarge`) sit outside the selected text, 8 from it.
- Snapping uses spring `instant`; a release with speed coasts first. Mouse wheel, arrow keys and dragging all work. The controller gives a haptic tick per row on device.
- Needs an odd number of rows and at least as many items as rows.

## When to use
- **Use for:** picking one value from an ordered list of 5 to 60: hours, minutes, a unit, a year.
- **Don't use for:** a short list of named choices (use `Option` or `SegmentControl`), a long unordered list (use a list and `SearchField`).
- **Alternatives:** `Menu`, `SegmentControl`, `NumberField`.
- **Do:** name the field, keep the items short and about equal in width, pair numeric values with appropriate units, and show the current selection nearby.
- **Don't:** use it for unordered choices or put two next to each other without a label.

## Web API
- `<sui-wheel-picker>` attributes: `items` (comma list) or `count` and `start` (numbers), `index`, `row-number` (odd, default 7), `left-text`, `right-text`, `width` (default 128), `disabled`, `item-color`, `selected-color`, `indicator-color`. Set `.items = [...]` in script for long lists.
- Events: `select` (`detail.index`, `detail.value`) when it settles on a new row.

## Preview field and result

The "Weight" example uses `count="51" start="40"` for the ordered values 40–90, in 1 kg steps. `index="22"` selects 62 initially and `right-text="kg"` provides the unit. It retains the default 128px width and seven rows; the field name, range hint and result are page-level content.

Read `picker.items[picker.index]` for the initial result, then use `select`'s `detail.value` to update "Selected weight: 62 kg" when the wheel settles. `detail.index` is the item's position, not its weight. Use numeric items with physical units; for named ordered lists such as months, omit the kg suffix.

## Plan grouping and handoff

For a coordinated multi-field picker, group the complete field set on one intentional `fillLight` surface with consistent insets when the design needs that grouping. Do not add separate extra backgrounds around each wheel and another around the group. A single picker does not automatically need a new wrapper surface. This concerns caller-added grouping; retain the control's own selected indicator.

Record actual row count, size, selected values and units. The reference seven-row wheel remains its baseline; do not substitute the old spatial-web wheel dimensions. Browser inertia, infinite scrolling and native interaction feedback are approximations. Confirm the chosen value through the surrounding task's action semantics, rather than adding a redundant submit button to an immediate control.

## Preview and shared rules

[Open this family’s preview](preview.html). It demonstrates a labelled numeric weight field with a unit and live selection result. Any added Plan recommendation sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
