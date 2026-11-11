# ListItem

A row on a `fillLight` surface. Minimum 360x60, radius 16 (`radiusLarge`), padding 16 start, 4 end, 16 top and bottom.

## Layout
- Headline `bodyLarge` (16/20, 500) in `labelPrimary`; supporting text `bodyMedium` (14/18, 500) in `labelTertiary`, 4 below.
- Leading content: end padding 12, vertically centered. Trailing content: start padding 16, minimum 40x40, centered. Their colors are unspecified, so they inherit.
- Heights: 60 for the headline alone, 74 with supporting text (16+20+4+18+16).
- This bundle adds built-in whole-row Web hover feedback: approximately 12% white lightening inside the row shape, cleared on pointer exit and suppressed while disabled. No extra helper call or wrapper is needed. The pressed appearance remains unchanged; connect `click-action` to the application behavior.

## When to use
- **Use for:** a settings row, a list entry, a result with a leading icon and a trailing control (`Switch`, chevron, `Badge`).
- **Don't use for:** a dense table, a menu entry (use `MenuItem`), a card with an image, or a navigation rail item (use `SideNavigation`).
- **Alternatives:** `MenuItem` inside a `Menu`, `SideNavigationItem` for navigation, `Option` for a choice tile.
- **Do:** one trailing control per row; use 360 as the narrowest width.
- **Don't:** put two actions in a row, or a long paragraph in supporting text.

## Web API
- `<sui-list-item>` attributes: `headline`, `supporting`, `leading-icon`, `trailing-icon`, `disabled`, `container-color`, `leading-color`, `headline-color`, `supporting-color`, `trailing-color`. Slots: `leading`, `headline`, `supporting`, `trailing`.
- Events: `click-action`.

## Hover and App restoration

All enabled ListItems in this bundle include the row hover simulation, including rows with trailing controls. This is a deliberate Preview addition to the reference implementation. It does not change row padding, colors at rest or the existing click event.

The current App restoration contract uses ListItem's native row hover. Do not wrap the native ListItem in another `Modifier.spatialHoverEffect()` or a Button just to obtain feedback. Keep its actual click action on the same row. The browser lightening is a preview approximation, not a native color/animation override.

For application-owned regions, use the [spatialHoverEffect helper](../../runtime/README.md#spatialhovereffect) instead. The family preview includes a custom file region with hover and click-to-select behavior, alongside enabled and disabled ListItems.

## Plan recommendation: explicit insets and parent spacing

The reference default above remains start/top/bottom **16**, end **4**. This Plan recommends **16 on all four sides**, especially with a trailing Switch or action. That recommendation is an override, not what an unset SDK parameter promises.

```html
<div style="display:flex;flex-direction:column;gap:8px">
  <sui-list-item headline="Wi-Fi" supporting="Connected to Office"
    leading-icon="ic_wifi" trailing-icon="ic_arrow_right"
    content-padding="16"></sui-list-item>
  <sui-list-item headline="Bluetooth" leading-icon="ic_bluetooth"
    content-padding="16"><sui-switch slot="trailing" checked></sui-switch></sui-list-item>
</div>
```

The original preview keeps end 4; the added preview shows end 16. Write the actual four insets and the parent's 8 gap in Spec. Native uses `padding = PaddingValues(16.dp)` and parent `Arrangement.spacedBy(8.dp)`. Do not add the sibling gap as `Modifier.padding(bottom = 8.dp)` on ListItem: its clip/background order can distort the lower corners. Preserve the icon and tail-control slots.

A row-level click must not duplicate a Switch's own event or toggle the value twice. Choose whether the whole row is clickable, and give each independent tail action its own behavior.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
