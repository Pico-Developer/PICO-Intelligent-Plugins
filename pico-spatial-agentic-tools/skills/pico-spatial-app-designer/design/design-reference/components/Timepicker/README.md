# Timepicker

One to three wheels for hours, minutes and seconds. 416 wide, 16 between wheels (the wheels share the width: 128 each for three), 7 rows of 44 (308 high).

## Details
- Each wheel is a `WheelPicker`. Hours run 0 to 23, minutes and seconds 0 to 59. An optional unit text follows the number (`labelLarge`).
- A wheel starts on its middle row (index 3) unless a value is set. Seconds can be dropped with `seconds="false"`; at least one wheel stays.
- Hover is the native spatial effect on a PICO device; the web build approximates it with the non-spatial fallback (12% white).

## When to use
- **Use for:** setting a time of day or a duration.
- **Don't use for:** a date (use `DatePicker`), a free numeric value (use `NumberField`).
- **Alternatives:** `WheelPicker` for any other ordered list, `NumberField` for one number.
- **Do:** name the field, identify each column, and drop seconds unless they matter. Distinguish a clock time from a duration and use explicit units for durations.
- **Don't:** use it for time zones or durations beyond a day.

## Web API
- `<sui-timepicker>` attributes: `hour`, `minute`, `second`, `seconds` (`false` hides the seconds wheel), `hours-text`, `minutes-text`, `seconds-text`, `row-number` (odd), `width`.
- Events: `hours-change`, `minutes-change`, `seconds-change` (`detail.value`), `time-change` (`detail.hour`, `minute`, `second`).

## Preview scenarios

The examples are stacked with a 40px gap between sections. Both keep the reference 416px width, 16px wheel gaps and seven rows; headings, column labels and live results are caller-provided page content.

- **Reminder time:** 24-hour clock, initially 09:30. `seconds="false"` shows only Hours and Minutes; `hours-text="h"` and `minutes-text="min"` identify the selected values. The result updates as HH:mm and omits seconds.
- **Countdown duration:** initially 1 h 20 min 30 s. `seconds="true"` shows Hours, Minutes and Seconds; `hours-text="h"`, `minutes-text="min"`, `seconds-text="s"` make the units explicit. The result uses duration units rather than a clock-time label. Hours remain 0–23, so this example is for durations under 24 hours.

Listen to `time-change` to refresh the result. Hiding the seconds wheel does not remove `second` from the event payload; omit it from the clock-time display when seconds are hidden. These inline examples update immediately and do not schedule a reminder or start a countdown.

## Plan grouping and handoff

For a coordinated multi-field picker, group the complete field set on one intentional `fillLight` surface with consistent insets when the design needs that grouping. Do not add separate extra backgrounds around each wheel and another around the group. A single picker does not automatically need a new wrapper surface. This concerns caller-added grouping; retain the control's own selected indicator.

Record actual row count, size, selected values and units. The reference seven-row wheel remains its baseline; do not substitute the old spatial-web wheel dimensions. Browser inertia, infinite scrolling and native interaction feedback are approximations. Confirm the chosen value through the surrounding task's action semantics, rather than adding a redundant submit button to an immediate control.

## Preview and shared rules

[Open this family’s preview](preview.html). It demonstrates clock time without seconds and duration with seconds; the visibility and unit attributes are explicit. Any added Plan recommendation sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
