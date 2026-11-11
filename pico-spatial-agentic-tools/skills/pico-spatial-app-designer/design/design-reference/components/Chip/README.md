# Chip

A compact label for a short tag or a property of an item. This reference page focuses on the basic SDK `Chip`, with text-only and leading-icon examples in Small and Regular sizes.

## Sizes
- Small: min height 32, radius 16 (`radiusLarge`), `labelMedium` (12/16, 600), padding 16 (12 with a leading icon), gap 2.
- Regular: min height 40, radius 38, `labelLarge` (14/18, 600), padding 20 (16 with a leading icon), gap 4.
- Icons in the SDK samples are 12dp.

## Appearance
- Background `fillSecondary`, foreground `labelPrimary`.
- Disabled alpha 0.3.
- An optional leading or trailing icon belongs to the label; it is not a separate click target. A trailing icon does not automatically create a remove action.

## When to use
- **Use for:** short content tags or item properties, such as Landscape, Music or Travel. Keep tags near the content they describe.
- **Don't use for:** a primary action (use `Button`), an icon-only action (use `IconButton`), or a group of large selectable choices (use `Option`).
- **Do:** use meaningful labels, keep them short, and let the parent layout wrap or space adjacent chips.
- **Don't:** use size or variant names as application content, or imply selection/removal behavior for a read-only label.

## Basic behavior

The native `Chip` accepts a nullable `onClick`. Pass `onClick = null` for a label without a click action. If a design needs a label action, supply a callback and define the observable result on the owning page. Basic Chip does not maintain a selection state or provide a remove control.

The preview uses read-only labels throughout. Small and Regular demonstrate size, while the icon example demonstrates an optional leading icon. Button, toggleable and removable variants are outside this page's current scope.

## Web API
- `<sui-chip>` attributes used here: `label`, `size` (`small`, `regular`), `leading-icon`, `trailing-icon`, `clickable`, `disabled`, `container-color`, `content-color`.
- Set `clickable="false"` for a read-only label. It has no button role, keyboard tab stop, pressed/hover feedback or `click-action` event. This Web-only attribute maps to native `Chip(onClick = null)` for click behavior; it is not a new native parameter.
- Omitting `clickable` preserves the runtime's existing clickable behavior. When an action is intended, listen for `click-action` and implement it on the page.
- Native basic Chip still applies `spatialHoverEffect` when enabled, even with `onClick = null`. The read-only Web preview intentionally omits interactive feedback to communicate its label-only purpose.

## Preview and shared rules

[Open this family's preview](preview.html). It shows only basic read-only Chip examples using the original component appearance defaults. Size names appear as section headings; the chips contain actual tags. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
