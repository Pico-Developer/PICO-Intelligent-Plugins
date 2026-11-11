# DatePicker

A month calendar. Width 416. Header 32 high, a 16 gap, the weekday row (32 high, 4 below), then 6 week rows of 32dp days with 4 between rows: 296 high in all.

## Layout and colors
- Header `Navigation` (default): minimum-size icon buttons (38x32, transparent, `labelPrimary`) for previous and next year and month, with the month and year centered in `bodyLarge`. Header `Dropdown`: a content-width pill aligned to the calendar's start edge (left in LTR), with `labelLarge` text and a 16dp arrow. It opens a `Sheet` titled "Select Month" with a year wheel (0 to 4999) and a month wheel; the order follows the locale and uses locale-appropriate year/month unit labels.
- Weekday names are narrow, in `bodyMedium` and `labelQuaternary`; they start on the locale's first day of the week.
- Days are 32dp circles in `bodyMedium`. Days of the neighboring months are shown in `labelQuaternary` and can be picked. Today: `fillPrimary` with `labelPrimaryLight`. Selected: a `fillSecondary` circle fades in on spring `rapid`.
- Hover is the native spatial effect on a PICO device; the web build approximates it with the non-spatial fallback (12% white). Pressed draws the 12% overlay.

## When to use
- **Use for:** choosing one date: birthday, deadline, appointment.
- **Don't use for:** a range (use `DateRangePicker`), a time (use `Timepicker`), a date typed faster than it is found (use `TextField`).
- **Alternatives:** `DateRangePicker`, `Timepicker`, `WheelPicker` for custom lists.
- **Do:** embed `DatePicker` directly in a page or form when there is room for the calendar; use `DatePickerDialog` for a modal selection flow, or `Sheet` when the surrounding task calls for one. Show the chosen date outside the calendar and use the dropdown header when jumping years is common.
- **Don't:** squeeze the full calendar into a small area or combine both header styles in one picker.

## Inline calendar and dialog

`DatePicker` is the calendar content. Both `Navigation` and `Dropdown` are valid inline variants: they stay in the normal page layout and do not create a modal surface. The month/year header belongs to the calendar; it is not a dialog title. Listen to `date-select` to use the inline selection in the page or form.

`DatePickerDialog` is a separate modal container that hosts a `DatePicker`. Put a task title such as "Choose a date" in the dialog's `title` attribute or slot, and Cancel/Apply in its negative/positive slots. For this flow, keep a draft selection until Apply and show the committed result outside the dialog.

The container determines whether the calendar is inline or modal. A dialog title is optional in the SDK; omitting it does not make a dialog inline. Adding a page heading above an inline calendar does not make it a dialog either. The captions in the preview identify examples and are outside the components.

## Web API
- `<sui-date-picker>` attributes: `selected` (`YYYY-MM-DD`), `year` and `month` (the displayed month), `header-style` (`navigation`, `dropdown`), `year-switchable`, `locale`, `content-color`.
- Events: `date-select` (`detail.year`, `month`, `day`, `date`).
- `<sui-date-picker-dialog>`: 480 wide, `Thickest` material, radius 16, title `headlineLarge` in `labelSecondary` (96 high), content padding 32/32/40, buttons right-aligned with gap 8. Attributes `title`, `hidden`, `corner-radius`; slots `title`, default, `negative`, `positive`.

## Plan dialog actions and dismissal

Preserve this family's native title hierarchy and decision-button layout. Bottom Cancel/Delete or Cancel/Apply is a valid pair of decisions. The Sheet guidance about duplicate exits does not require removing a decision button or adding another TitleBar/close to these dialogs.

Opening removes `hidden`. `dismiss-request` must be handled by the app; the examples hide the surface. Outside click and Escape are opt-in through `dismiss-on-click-outside` and `dismiss-on-escape`, not guaranteed default exits. The task determines whether draft changes are discarded, applied or retained. In DatePickerDialog, keep negative/positive actions in their own slots and show the committed date outside the picker. Browser Escape is not proof of native Back behavior.

The preview provides Cancel and Apply in the negative/positive slots. Selecting a day updates a draft; Apply commits it and updates the result outside the dialog, while Cancel discards it. Each opening restores the committed selection and its displayed month. Outside-click and Escape dismissal remain explicitly disabled, matching the SDK defaults.

## Preview and shared rules

[Open this family’s preview](preview.html). The two inline variants are stacked vertically with a 40px gap between example sections, followed by a separate dialog example. Calendar dimensions and internal spacing retain the SDK defaults. Any added Plan recommendation sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
