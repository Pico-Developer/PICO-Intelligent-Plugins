# ToggleButton

A `Button` that keeps a checked state. Checked uses `fillSecondary`, unchecked `fillTertiary`, content `labelPrimary` in both.

## Sizes
- Same steps as `Button` (Max 104x56, Small 69x40, Min 57x32). **The default is Min**, and `Regular` is the same as Min, not the Regular button size.
- Icons and gaps follow `Button`.

## States
- Checked and unchecked differ only by container color; no animation between them.
- Disabled: alpha 0.3. Hover is the native spatial hover effect on a PICO device (gaze or ray), not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white) under the content.

## When to use
- **Use for:** a small filter or mode that stays on after the press: Bold, Mute, Grid view.
- **Don't use for:** an immediate system setting (use `Switch`), choosing one of several (use `SegmentControl` or `Option`), a one-shot action (use `Button`).
- **Alternatives:** `ToggleableChip` for tag-like filters, `ToggleIconButton` for an icon, `Checkbox` when a list of choices is submitted together.
- **Do:** keep labels short; show the checked state through the fill, not only the label.
- **Don't:** use the dark `Button` fill for a toggle; mix toggle buttons and action buttons in one group.

## Web API
- `<sui-toggle-button>` attributes: `text`, `checked`, `size`, `disabled`, `leading-icon`, `trailing-icon`, `checked-container-color`, `container-color`, `content-color`.
- Events: `checked-change` (`detail.checked`), `click-action`.

## Preview and shared rules

[Open this family’s preview](preview.html). The five examples retain the original sizes and initial checked states. Both default-size buttons are labelled Bold, starting unchecked and checked respectively. Small and Max also use Bold, with size captions outside the buttons. The icon example uses Mute with `ic_volume_slash`.

Button labels name the function and remain unchanged when toggled; fill and `aria-pressed` reflect the current state. External captions explicitly describe initial states rather than a live state. Each example toggles independently by click or Enter/Space. No editor or audio simulation is added. If a composition uses live On/Off text instead of a stable function name, update that text from `checked-change` so it agrees with `checked`.

See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
