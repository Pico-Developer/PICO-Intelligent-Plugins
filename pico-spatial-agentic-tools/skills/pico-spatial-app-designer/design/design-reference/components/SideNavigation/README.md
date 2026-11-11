# SideNavigation

A vertical list of page destinations. The component already supplies 24dp horizontal content padding; its internal minimum width is 100dp.

Each SideNavigationItem selects a distinct page in the adjacent content region. Switch that page's TitleBar and body together, including its title, applicable subtitle/actions and content sections, while keeping the navigation visible. These pages share the same window; they do not require separate native windows or duplicated TitleBar implementations. Page-specific sections such as a featured collection belong only to the corresponding page. Use an in-page filter control when the intent is only to filter the current page's collection.

## Details
- Header `displaySmall` (28/34, 700) in `labelSecondary`. Sections have 16 top padding and a `titleSmall` title in `labelQuaternary` (padding 16/2/8/14).
- Items: radius 24, padding 8, gap 8, `bodyLarge`; leading and trailing boxes at least 32x32. Selected `fillSecondary` with `labelPrimary`; unselected transparent. The minimum is applied to the width (48), so a text-only item is 36 high and one with an icon is 48.
- Items show the 12% pressed overlay on the web; on device hover is native.

## When to use
- **Use for:** the main destinations of a large window, three or more.
- **Don't use for:** two or three sibling views (use `SegmentControl`), a bar above the window (use `TabBar`), a list of content (use `ListItem`).
- **Alternatives:** `TabBar` for a handful of top-level destinations.
- **Do:** group with sections; keep names to one or two words.
- **Don't:** nest items more than one level.

## Web API
- `<sui-side-navigation>` attributes: `items` (comma list), `icons`, `selected-index`, `header`. Or compose `<sui-side-navigation-section label>` and `<sui-side-navigation-item label selected leading-icon>` children.
- Events: `select` (`detail.index`, `detail.value`). `value` uses the item's `value` attribute, falling back to its label. `index` / `selected-index` use a flat, zero-based order across the whole navigation: shorthand items first, then child items in DOM order, including all sections.
- The Web container keeps one selected destination across these items. Use one initial `selected` child, or set `selected-index` on the container. Keep all sections inside that same container; each separate navigation has its own selection scope. A section provides layout/title only.

## Grouped destinations

Use child items for grouping; the `items` shorthand only creates a flat list. Place sibling sections inside one navigation:

```html
<sui-side-navigation header="Library">
  <sui-side-navigation-section label="Media">
    <sui-side-navigation-item label="Photos" value="photos"
      leading-icon="ic_image_fill" selected></sui-side-navigation-item>
    <sui-side-navigation-item label="Albums" value="albums"
      leading-icon="ic_folder"></sui-side-navigation-item>
  </sui-side-navigation-section>
  <sui-side-navigation-section label="Collections">
    <sui-side-navigation-item label="Favorites" value="favorites"
      leading-icon="ic_star"></sui-side-navigation-item>
  </sui-side-navigation-section>
</sui-side-navigation>
```

Selecting Favorites clears Photos. Sections do not create separate selection groups or expand/collapse behavior. See the preview's **Reference composition · grouped destinations** for a minimal interactive example, and **sidebar and page** for grouped navigation that updates the adjacent page. When filtering, hide a section when all its destinations are hidden.

### Native SDK mapping

Native `SideNavigation` and `SideNavigationSection` provide layout; they do not manage selection or add click actions. Share one destination state across all sections, and apply `Modifier.clickable` to each item, as in the SDK demo:

```kotlin
var destination by remember { mutableStateOf("photos") }
SideNavigation(header = { Text("Library") }) {
    SideNavigationSection(title = { Text("Media") }) {
        SideNavigationItem(
            selected = destination == "photos",
            modifier = Modifier.clickable { destination = "photos" },
        ) { Text("Photos") }
    }
    SideNavigationSection(title = { Text("Collections") }) {
        SideNavigationItem(
            selected = destination == "favorites",
            modifier = Modifier.clickable { destination = "favorites" },
        ) { Text("Favorites") }
    }
}
```

Use stable, distinct destination IDs for the state; labels may repeat across groups. The Web runtime's automatic selection and numeric `selected-index` are preview conveniences, not native SDK parameters.

## Plan recommendation: a full-height sidebar beside the page

Keep the sidebar at full page height. Put the current right page's TitleBar above its own body, not above the sidebar/page pair. Supply the sidebar header through Web `slot="header"` / native `header`. Its title band is 96 high: one 34-high line centered with 31 above/below and an extra start inset of 8. Preserve the reference header type/color. Global SearchField follows with no extra top inset; use a 28 gap below search. Without search, omit that gap. The search edge aligns with SideNavigation's content edge, already inset by 24dp, not the inset title text.

### Padding ownership

The Web component and native SideNavigation already provide the horizontal 24dp. Do not add that padding again to the component host, an outer wrapper or the whole header. The header title starts at **24 + 8 = 32dp** from the navigation edge: apply only the extra 8dp inside its title container, not another 32dp.

| Space | Owner | Application setting |
| --- | --- | --- |
| Navigation horizontal inset | SideNavigation internals | Already 24dp on each side; no repeated outer padding |
| Header title's extra start inset | Header title container | 8dp, within the existing 24dp |
| Item content inset | SideNavigationItem internals | Start 16dp; top/end/bottom 8dp |
| Space between items | Parent list | 4dp gap, outside selected item surfaces |

Web item insets use `content-padding="8" padding-start="16"`; native uses `contentPadding = PaddingValues(start = 16.dp, top = 8.dp, end = 8.dp, bottom = 8.dp)`. Native item-level `Modifier.padding` adds external space and is not a substitute for `contentPadding`. Use parent `gap:4px` / `Arrangement.spacedBy(4.dp)` for sibling spacing. The header and item content have different intentional insets; check their visible edges without adding compensating padding. Record only application-added layout padding in Spec, and record item content overrides as component props; do not restate the built-in 24dp as extra `layout.paddingDp`.

Keep the header to one identity title and optional global search. Do not add introductions, counts or status lines just to fill the header; place required information with the content it describes. If both sidebar and page search are present, give them distinct, clear search scopes rather than duplicating the same search.

| Value | Reference baseline above | This Plan's explicit recommendation |
| --- | --- | --- |
| Item minimum height | Text-only can be 36; icon row 48 | Minimum 48 even without icon |
| Item padding | 8 all around | Start 16; top/end/bottom 8 |
| Sibling gap | No guaranteed 4 gap | Parent list gap 4 |
| Header/search organization | Caller supplies it | 96 title band; optional search; 28 below search |

Use child items when applying these values; the `items` shorthand does not forward per-item overrides:

```html
<div style="display:flex;flex-direction:column;gap:4px">
  <sui-side-navigation-item label="Library" leading-icon="ic_book"
    default-min-height="48" content-padding="8" padding-start="16"
    selected></sui-side-navigation-item>
  <sui-side-navigation-item label="Photos" leading-icon="ic_image_fill"
    default-min-height="48" content-padding="8" padding-start="16"></sui-side-navigation-item>
</div>
```

Use meaningful local icons with navigation labels in generated pages, following the Preview's icon-and-label compositions. If a real item intentionally has no icon, do not reserve an empty icon slot or synthesize a first-letter icon. The 48 minimum still applies. Parent spacing stays outside each selected surface. Record item insets/minimum, list gap, sidebar width and header/search dimensions in Spec. Native explicitly applies `heightIn(min = 48.dp)`, item content padding and parent `spacedBy(4.dp)`; do not infer them from this reference's defaults.

## Preview and shared rules

[Open this family’s preview](preview.html) before composing a sidebar page. Inspect **Plan recommendation · sidebar and page**, switch Books / Photos / Favorites / Albums, and observe the title and content update together. Read its header slot and padding setup as well as its icon choices; README text alone does not replace this example. The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
