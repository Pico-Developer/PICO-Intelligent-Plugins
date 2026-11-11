# TabBar

A floating bar above the window for top-level destinations. Material is applied by the system; the web build uses a flat `#cacaca` container.

## Details

- Bar 64 high (padding 8 around 48 high items), radius 32; up to 7 items, each at least 64 wide, equal width, gap 4, radius 24, 8 horizontal padding (16 when the content is wide).
- Selected item `fillPrimary` with `labelPrimaryLight`; others transparent with `labelPrimary`. The main content is `titleMedium` text or an icon; a badge sits 6 from the top, 16 past the main content.
- With an icon and a label per item the bar expands to 88 on hover and shows the labels (`labelMedium` selected, `bodySmall` others) after a 1000ms dwell (`HoverDelayMillis`); the items grow from 48 to 72. A selected item can also open an extra content row (56 high); that is not built here.

## When to use

- **Use for:** the top-level sections of an app window, up to seven.
- **Don't use for:** switching views of the same content (use `SegmentControl`), a long list of destinations (use `SideNavigation`), actions (use `Toolbar`).
- **Alternatives:** `SideNavigation` for many or nested destinations at the same navigation level, `SegmentControl` for local view modes. A sidebar within the selected main destination can coexist with TabBar.
- **Do:** use icons plus a short label; keep the order stable.
- **Don't:** use more than seven items, or mix text-only and icon items.

## Web API

- `<sui-tab-bar>` attributes: `items` (comma list), `icons`, `badges` (comma list, empty for none), `selected-index`, `show-labels`, `expand-on-hover` (default on), `hover-delay` (ms, default 1000), `container-color`.
- Events: `select` (`detail.index`, `detail.value`).

## Plan placement and navigation

Follow Explore's [navigation decision](../../../layout-2d.md#4-navigation-and-content-switching). Actively consider TabBar for a small set of stable main destinations; record a task-specific reason when a suitable opportunity uses another carrier. Each destination keeps its own layout: horizontal categories and a grid, or a sidebar and right page, are both valid. A single-task window needs no invented tabs.

Record destination identity, selected state, host window, switching targets and state retained on return. Selection must change actual destination content. Main tabs, side navigation and local filters affect different regions; do not duplicate the same destination set in both bars. In-page categories and sidebars are ordinary page structure, not TabBar's native extra-content slot.

The reference preview retains the original icon-and-label and text-only bars, followed by a small Discover / Playlists / Library example. Its title and description changes demonstrate selection wiring, not a complete destination implementation. For layered navigation, follow the Explore decision above and the [SideNavigation guide](../SideNavigation/README.md); preserve the selected destination's local layout and state as required by the application.

Use meaningful icons and available labels so unfamiliar icons are not the only explanation. Browser layout shows content and selection; native attachment/hover expansion requires device verification. Native `extraContent` is a separate optional capability, not required for in-page categories or sidebars.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. The added destination section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
