# Divider

A hairline. Thickness **0.5dp**, color `dividerLine` (`sub-black-12`, 12% black). `HorizontalDivider` fills the width, `VerticalDivider` fills the height. No interaction.

## When to use
- **Use for:** separating groups inside one surface, such as menu sections or a toolbar's regions.
- **Don't use for:** separating rows of a list (give `ListItem` its own surface and a gap instead), or as a decorative rule.
- **Alternatives:** spacing (`gapMedium` 12, `gapLarge` 16) and surfaces (`fillLight` rows) do most of the separating in this system.
- **Do:** keep it inside the padding of its container.
- **Don't:** stack dividers between every item or tint it.

## Web API
- `<sui-divider>` (also `<sui-horizontal-divider>`, `<sui-vertical-divider>`) attributes: `orientation`, `thickness` (default 0.5), `color`.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
