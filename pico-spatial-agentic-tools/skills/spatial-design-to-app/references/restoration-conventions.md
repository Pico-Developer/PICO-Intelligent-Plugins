### Custom surface-title restoration

Subwindow has no title slot. Restore accepted `textRole: "surface_title"` nodes
as ordinary `Text` using their exact typography token, with one
`// design-style: surface-title <node-id>` immediately before the call. Supply
`design-spec.json` to the style verifier. The exemption applies only to a valid
node, unique marker, and matching token; never suppress all typography warnings
inside an overlay. Preserve the largest local heading and inspect its open state.
Gap and Radius selection follows the shared Designer reference; existing padding
ownership, visible-content-top alignment, and frozen design facts remain intact.

### TitleBar body spacing and ordinary rows

By default, TitleBar and body are adjacent children of an unpadded page column:
body top padding is 0dp and the TitleBar-to-body gap is 0dp. Do not recreate
that gap with parent `spacedBy`, Spacer, margin, translation, or outer padding.
Keep TitleBar's native internal spacing. Put module gaps inside the body only.
Record nonzero overrides only when the original requirement or authoritative
visual evidence explicitly calls for them.

Ordinary horizontal content rows (title plus button, text plus icon, label plus
control) default to vertical centering. Write `layout.align: "center"` in the
spec; Preview uses `align-items: center` and Compose uses
`Alignment.CenterVertically`. Explicit top/end or text-baseline alignment for
multiline content, unequal text sizes, or independent columns retains priority;
record that relationship instead of centering every structural row. Component-
owned slot alignment remains native unless an evidenced override is accepted.

ListItem specs explicitly select `props["spacing-policy"]` (`canonical` by
default, `explicit` for evidenced internal-padding-dp overrides). Canonical
restoration passes `padding = PaddingValues(16.dp)`; Native omission uses end=4dp.
Every TitleBar spec explicitly declares `title-alignment`. Implementation review
compares actual parameters with spec using source_mappings or adjacent
`// design-node: <id>` anchors; opaque, missing, or ambiguous values produce
warnings with concrete review guidance, not blocking failures. See
[component mapping](./spatialui-web-to-compose.md).

### Component defaults and property-level overrides

Apply the [component-default contract](./spatial-ui-components.md): SideNavigationItem minimum height 48dp
(`Modifier.heightIn(min = 48.dp)`), content padding start 16dp and others 8dp,
and parent-list gap 4dp. TitleBar **primary title only** uses explicit
`fontWeight = FontWeight.Bold` (700); the SDK does not guarantee this weight.
TitleBar subtitles identified by `props["subtitle-node-id"]` are the canonical exception: declare `textStyle: { "typography": "bodyMedium", "color": "labelSecondary" }` on that text node, render it explicitly in Preview, and restore it as `Text(style = PicoTheme.typography.bodyMedium, color = PicoTheme.colorScheme.labelSecondary)` in Compose. Keep the existing title slot and composed title group; do not add a subtitle slot or infer subtitles by child order. This default needs no `styleOverrideEvidence`; other subtitle styles still require authoritative evidence.
Other slot typography and foreground remain inherited. Web uses the same
height and weight defaults. A property-level authoritative override changes
only that property; custom spacing never cancels the height default.

Record explicit height/weight requirements on the owning component using
`props["min-height-dp"]` / `props["title-font-weight"]` and
`styleOverrideEvidence` with a user/Figma/screenshot source and non-empty
reference. Do not manufacture override evidence from generated defaults.
Add a matching `// design-node: <node-id>` before the Compose call for these
overrides. Resolve the independent `side_navigation_item_height` and
`titlebar_title_weight` scanner failures and unverified warnings before
claiming fidelity; dynamic or opaque values are not verified passes.
