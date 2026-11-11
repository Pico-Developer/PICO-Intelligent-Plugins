# Menu

A popup list of commands anchored to a control. Radius 20 (`radiusExtraLarge`), padding 8, width 160 to 480 (the content width), at most 480 high and scrollable; `Thick` material from the system, a blurred fill on the web.

## Placement
- Below the anchor, aligned to its start, 8dp offset. A `SubMenu` opens to the end of its item, with its panel aligned to the item's top (SDK `VerticalPlacement.alignTop()`). The panel retains its own 8dp content padding.
- The icon preview explicitly sets `offset-y="-8"` on the submenu to align the **first child item row** with the parent item row. This compensates for panel padding; it is an example override, not the SDK's default panel position.
- The Web runtime follows the anchor with side/top placement on every frame. At viewport edges it flips sideways or clamps vertically; edge clamping may prevent exact row alignment. The runtime treats a child popup anchored to a parent item as part of that parent's interaction area. Keep the popup as a sibling to avoid transformed/material ancestors becoming a new fixed-position containing block, and close the child when the parent closes.

## MenuItem
- At least 48 high, radius 12, padding 16 start and 8 on the other sides, title `titleMedium` (16/20, 600) in `labelPrimary`, subtitle `labelMedium` (12/16, 600) in `labelTertiary`. Leading gap 8; trailing box at least 32 wide with 8 start gap.
- Pressed draws the 12% overlay. Dismisses on outside click and Back.

## When to use
- **Use for:** a short list of commands or choices that are hidden until asked for: More, Sort by, Share.
- **Don't use for:** confirmations (use `AlertDialog`), forms (use `Sheet`), always-visible navigation (use `SideNavigation`), a single binary choice (use `Switch`).
- **Alternatives:** `Sheet` for richer content, `AlertDialog` for a required decision, `Option` for visible choices.
- **Do:** keep to about seven items; put the destructive item last; add a subtitle only when it prevents a mistake.
- **Don't:** nest more than one level or mix icons and no icons.

## Web API
- `<sui-menu>` attributes: `for` (anchor id), `offset-x`, `offset-y`, `corner-radius`, `max-height`, `hidden`, `dismiss-on-click-outside`, `dismiss-on-escape`, `keep-open`. Children: `<sui-menu-item title subtitle leading-icon trailing-icon disabled>`.
- Events: `select` on the item (`detail.title`), `dismiss-request` on the menu.

## Icon examples and command callbacks

The preview includes leading icons for all command items, including Move to, Favorites and Archive. Move to also has a trailing directional arrow. Icons are 24px local catalog assets: Copy `ICON7-A059`, Share `ICON7-P003`, Delete `ICON7-P264`, folder `ICON7-S029`, star `ICON7-P564`, arrow `ICON7-P006`. BasicMenuItem demonstrates a caller-owned icon/text layout.

```html
<sui-menu-item title="Move to" leading-icon="ICON7-S029"
  trailing-icon="ICON7-P006" data-opens="nested-child"></sui-menu-item>
```

The example's `actions` map intentionally contains `null` callbacks. Selection demonstrates menu dismissal only; no clipboard, share or delete operation is performed and no success message is implied. Applications supply these callbacks and any confirmation or feedback required by the actual command. Keep business behavior outside the generic Menu component.

## Plan composition boundary

Use the family for its stated purpose: commands (Menu), anchored content (SpatialPopup), guidance (Coachmark), or transient feedback (Snackbar). The title-bar close rule for task surfaces does not mean adding a TitleBar to these compact components. Keep ownership, trigger and dismissal clear, avoid a second wrapper background over the built-in surface, and use named local icons where an action needs one. See [general rules](../../general-rules.md) for operation scope and color choices.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
