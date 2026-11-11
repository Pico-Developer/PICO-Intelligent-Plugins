# DateRangePicker

`DatePicker` with two ends. Same size (416x296), header, colors and day cells; the days from start to end sit on a `fillLight` capsule drawn per week row, and the start and end days get the `fillSecondary` selected circle.

## Behavior
- First tap sets the start. A second tap on the same or a later day sets the end; a tap on an earlier day replaces the start. With both set, the next tap starts a new range and clears the previous end.
- It does not use the selected-day text color override that `DatePicker` does. Hover is the native spatial effect on a PICO device; the web build approximates it with the non-spatial fallback (12% white).

## When to use
- **Use for:** a trip, a booking window, a report period.
- **Don't use for:** one date (use `DatePicker`).
- **Alternatives:** two `DatePicker`s only when the dates are unrelated.
- **Do:** show the start and end as text next to the picker; clear the range with a visible action.
- **Don't:** allow an end before the start (the picker never does).

## Web API
- `<sui-date-range-picker>` attributes: `start`, `end` (`YYYY-MM-DD`), `year` and `month`, `header-style`, `year-switchable`, `locale`.
- Events: `range-change` (`detail.start`, `detail.end` or null).

## Preview selection flow

The inline "Report period" example starts with a complete range, 2026-10-08 through 2026-10-17. It displays Start and End separately, alongside a status message. These are page-level fields; the calendar itself retains its SDK layout.

- Tap a date after a complete range: it becomes the new start and End says "Choose an end date".
- Tap the same or a later date: both values are displayed as a complete range.
- Tap an earlier date while choosing the end: it replaces the start; the end remains unselected.
- Use Clear range at either selection stage: remove both `start` and `end`, update the text to "Not selected", and disable Clear until a date is selected again. Removing attributes programmatically does not emit `range-change`, so the example also refreshes its text explicitly.

The example reads `start` and `end` on `range-change`; selection takes effect immediately. If the surrounding task requires Cancel/Apply, host the calendar in `DatePickerDialog` and keep draft and committed ranges separately, as described in [DatePicker](../DatePicker/README.md#inline-calendar-and-dialog).

## Preview and shared rules

[Open this family’s preview](preview.html). The example includes start-only, complete, reselected and cleared states through the interaction above, while retaining SDK calendar dimensions and spacing. Any added Plan recommendation sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
