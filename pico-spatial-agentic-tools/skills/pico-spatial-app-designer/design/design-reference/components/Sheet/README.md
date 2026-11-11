# Sheet

A modal window for a task or a form. `Thick` material; radius 20.

## Layout
- Width 480 (minimum 360, maximum 600), at least 184 high, at most the window height minus 64.
- Title bar at least 96 high with 32 padding: leading action, centered title (`titleLarge` in `labelPrimary`), trailing action. The default leading action is a close `IconButton` Small (`fillTertiary`, `labelPrimary`).
- Content: padding 32 (no top padding under a title bar), gap 32, color `labelSecondary`; an optional `bottom` area follows.
- `HeadImageSheet`: an image on top with a Regular close button (`fillSecondary`, `labelPrimaryLight`) 16 from the corner; the title aligns to the start.
- Modal; not dismissed by outside tap or Back by default.

## When to use
- **Use for:** a short task that interrupts the window: pick a mode, edit details, share options.
- **Don't use for:** a yes/no decision (use `AlertDialog`), a list of commands (use `Menu`), feedback (use `Snackbar`).
- **Alternatives:** `AlertDialog`, `Menu`.
- **Do:** give it a title and one clear way out; put a required submit/confirm action in `bottom`. An immediate choice does not always need a second confirmation.
- **Don't:** open a sheet from a sheet.

## Web API
- `<sui-sheet>` and `<sui-head-image-sheet>` attributes: `title`, `closable` (`false` removes the close button), `width`, `corner-radius`, `dismiss-on-click-outside`, `dismiss-on-escape`, `hidden`. Slots: `leading`, `title`, `trailing`, default, `bottom`, and `header-image` (head image sheet).
- Events: `dismiss-request`.

## Preview: choosing a mode and local header artwork

The first Sheet contains a single-choice group: Reading, Cinema and Relax. Selecting an Option changes only the draft; Done commits the draft, updates the mode summary outside the Sheet and closes it. The built-in leading close discards the draft. Reopening restores the last committed choice. Clicking the selected Option keeps it selected, so this task always has exactly one mode.

Each Option explicitly uses 16px content padding and a 12px icon/content gap; the parent supplies an 8px row gap. The 24px local icons are `ic_book` (`ICON7-P467`), `ic_film` (`ICON7-P302`) and `ic_headset` (`ICON7-P414`). They use the default primary foreground and are decorative beside the mode labels. A 20px `ic_check` also marks the selected row. These are example composition choices, not changes to Option or Sheet defaults. Done uses a Regular Button in an end-aligned bottom action row.

The HeadImageSheet uses the local color illustration `assets/illustrations/lake-scene.svg`, with a 480×180 viewBox, rendered through `<img slot="header-image">` at full width and 180px high with `object-fit:cover`. It is artwork rather than a monochrome Icon. Keep the close button over the top-left of the image, 16px from its edges. Ordinary Sheet titles stay centered; HeadImageSheet titles stay start-aligned below the image.

## Plan rules: use the structure the variant already supplies

| Variant | Already supplied | Caller supplies |
| --- | --- | --- |
| Sheet | Surface, title/leading/trailing region, default top-left close, body and bottom slots | Form/task content and optional submit action |
| HeadImageSheet | Image region, top-left image close, start-aligned title, body and bottom slots | Header image and content; keep its image-specific close treatment |
| BasicSheet | Modal surface only | One coherent header/close, body and optional action region |

For normal forms, keep `title` or the `title` slot and the native title style. Do not insert a second TitleBar into Sheet's body. Use `trailing` for a concise auxiliary IconButton (for example Help); use the bottom region for Save or a longer primary action, usually right-aligned. An explicitly supplied `leading` action replaces the default close and must implement its own behavior.

If top-left close and bottom Cancel mean the same discard-and-exit operation, omit the duplicate bottom exit. This is a redundancy rule, not a ban on Cancel throughout the dialog family. A task may require an unsaved-change prompt or semantically different secondary action. HeadImageSheet preserves its close at top-left of the image (16 from the edges, Regular size), not the ordinary Sheet header position. BasicSheet requires an explicit exit; the added example shows one.

The maximum height is based on the owning native window. The standalone browser approximates it with viewport minus 64. The reference panel scrolls as a whole; `bottom` is not pinned. For long forms, specify whether the header/footer stay visible and which content scrolls; do not claim that a slot name guarantees that behavior. The short form example fits without scrolling.

`dismiss-request` asks the application to close; handle it and update visibility/state. Outside-click and Escape dismissal are opt-in here. The default close still works. Sheet actions should not submit data on close unless the task explicitly requires it.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
