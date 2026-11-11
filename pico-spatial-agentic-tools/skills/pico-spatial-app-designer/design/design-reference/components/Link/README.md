# Link

A text-style button: transparent container, `interaction` blue text, radius 4. Only the text style changes with size.

## Sizes
- Regular: min height 24, horizontal padding 4, `bodyMedium` (14/18, 500). Default.
- Max: min height 32, padding 6, `bodyLarge` (16/20, 500).
- With a trailing icon the end padding is 2 (Regular) or 3 (Max); the SDK sample uses a 16dp icon.

## States
- Disabled alpha 0.3. Hover is the native spatial hover effect on a PICO device (gaze or ray), not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white) under the content.

## When to use
- **Use for:** a low-emphasis action or navigation that sits beside body text: Learn more, Terms, See all.
- **Don't use for:** the main action of a window (use `Button`), a destructive action, or anything that must be found at a glance.
- **Alternatives:** `Button` Min or Small for a bounded control, `ListItem` with a trailing arrow for a navigation row.
- **Do:** make the link text describe the destination ("Privacy policy", not "Click here").
- **Don't:** underline it (the blue is the cue) or set long sentences as a link.

## Web API
- `href` optionally renders a real browser link, with normal keyboard navigation and middle-click behavior. This is a Web extension; the Compose Link uses its click callback. Disabled links do not navigate.
- `<sui-link>` attributes: `text`, `size` (`regular`, `max`), `disabled`, `trailing-icon`, `color`.
- Events: `click-action`.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
