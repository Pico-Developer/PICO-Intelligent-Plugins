# SpatialUI Web → Compose Bridge

Use this reference after the `pico-spatial-app-designer` gate, especially for
`input_mode=intent_only`. The designer's `design-spec.json` declares SpatialUI
Web components as semantic proxies for the production SpatialUI Compose APIs
listed here. `preview.html` renders those declarations and is visual comparison
evidence, not the source for component discovery.

## Hard conversion contract

1. Read every `design-spec.json.nodes[]` entry with `kind: "spatialui"`.
2. Create an in-memory conversion inventory with one row per node:
   `node ID → Web component → semantic role → Compose API → props/state/callback → hierarchy`.
3. Use the mapped Compose API. A mapped `sui-*` tag is **not** eligible for
   `Box`/`Row`/`Text` reimplementation or
   `// TODO(missing-component)`.
4. Preserve component hierarchy. `design.windows` and `foundation.window`
   entries remain window-level/floating structures; they do not become page
   children just because the preview is HTML.
5. Translate behavior, not renderer syntax:
   - JSON props such as `checked`, `selected-index`, `value`, and visibility
     become state from the ViewModel/UI state holder;
   - JSON event bindings become typed Compose callbacks;
   - child node IDs become composable lambdas;
   - JSON theme, appearance, layout, and typography map through `PicoTheme`,
     component defaults, and dp-based Compose modifiers.
   - Button-family nodes preserve `props.size` from `design-spec.json`; when the
     Designer did not receive an explicit user-requested size, the expected
     value is `regular`, and the Compose implementation uses the corresponding
     regular component size rather than inferring a larger or smaller size.
   - App-authored text preserves its exact typography token. Prefer tokens
     below `titleLarge` (20sp); direct `Text.style` choices at or above that
     ceiling retain their design-review warning. When a component-owned
     `Text` / `Icon` slot has no explicit design typography or foreground,
     omit `style`, `color`, and `tint` so the component defaults remain in
     effect. For TitleBar and SideNavigation slots, an explicit design
     typography or foreground is authoritative only when the node also records
     `styleOverrideEvidence` from the original user requirement, Figma, or a
     screenshot.
6. Do not copy Web-only convenience APIs into Kotlin. CSV attributes, string
   icons, `show()`, and HTML positioning are preview adapters. Resolve each icon
   through the declared source priority and follow
   [Image and icon sources](preview-first-restoration.md#image-and-icon-sources).
   Load accepted SVG files through Coil's `rememberAsyncImagePainter` in
   SpatialUI `Icon`; retain the component-owned or accepted explicit tint.
   For Figma `icon70://7.0/<name>`, copy the referenced VectorDrawable with the
   Designer's `icon-catalog.mjs` and use `painterResource`. Display multicolor
   artwork as an image without monochrome tint; never substitute a text glyph
   or emoji. Resolve Kotlin signatures through
   [API lookup](spatial-api-imports.md#target-sdk-api-resolution); reuse matching
   version evidence instead of repeating SDK discovery for every component.
7. A custom Compose component is allowed only for a `domain_visual` node that
   has no `sui-*` entry and no semantic SpatialUI match. Preserve its
   `rendererKey`, purpose, data bindings, dimensions, colors, and interaction
   contract; record the implementation choice in the conversion inventory.
   `Button` is a bounded command control, not a generic layout surface. Do not
   restore a rich selectable item or read-only detail region as
   `Button { Column { ... } }`. Prefer an actionable `ListItem` when its row
   semantics fit, an app-owned layout with spatial hover plus
   `clickable` / `selectable` for a custom interactive item, or a plain
   `Box` / `Column` for read-only content.
8. Compare the implementation with the accepted `preview.html`, but never add
   a component or design value found only in its DOM/CSS. A mismatch must be
   repaired in the design package before code generation.
9. Preserve Compose component color ownership. When the accepted design does
   not explicitly override a built-in's state colors, keep its default
   `colors` / background arguments and let supported `Text` / `Icon` slots
   inherit content color. When custom state colors are required, configure them
   through one component `colors` API where possible and evaluate each state's
   effective foreground/background pair. Do not infer white text from
   `selected=true`.

## Complete mapping

`Package` is relative to `com.pico.spatial.ui`.

| SpatialUI Web tag                | Compose API                         | Package                              | Conversion note                                                                                                                      |
| -------------------------------- | ----------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `sui-badge`                      | `Badge`                             | `design`                             | Default/content slot → `content`                                                                                                     |
| `sui-dot-badge`                  | `DotBadge`                          | `design`                             | Preserve semantic status color                                                                                                       |
| `sui-number-badge`               | `NumberBadge`                       | `design`                             | `number`/`threshold` remain numeric                                                                                                  |
| `sui-button`                     | `Button`                            | `design`                             | `click-action` → `onClick`; slots → icon lambdas                                                                                     |
| `sui-checkbox`                   | `Checkbox`                          | `design`                             | `state` → `checked` + `onCheckedChange`                                                                                              |
| `sui-tri-state-checkbox`         | `TriStateCheckbox`                  | `design`                             | Map indeterminate state explicitly                                                                                                   |
| `sui-button-chip`                | `ButtonChip`                        | `design`                             | Label/icon slots and `onClick`                                                                                                       |
| `sui-chip`                       | `Chip`                              | `design`                             | Preserve clickable vs display-only semantics                                                                                         |
| `sui-removable-chip`             | `RemovableChip`                     | `design`                             | `remove` → `onTrailingRemoveClick`                                                                                                   |
| `sui-toggleable-chip`            | `ToggleableChip`                    | `design`                             | `selected` → `isToggleOn`; preserve default state colors and slot inheritance                                                        |
| `sui-circular-progress`          | `CircularProgressIndicator`         | `design`                             | Select determinate overload from value presence                                                                                      |
| `sui-symbolic-circular-progress` | `SymbolicCircularProgressIndicator` | `design`                             | Symbol → `progressSymbol` slot                                                                                                       |
| `sui-date-picker`                | `DatePicker`                        | `design`                             | `date-select` → state callback                                                                                                       |
| `sui-date-range-picker`          | `DateRangePicker`                   | `design`                             | Start/end callbacks remain distinct                                                                                                  |
| `sui-divider`                    | `Divider`                           | `design`                             | Preserve orientation                                                                                                                 |
| `sui-horizontal-divider`         | `HorizontalDivider`                 | `design`                             | Direct orientation-specific API                                                                                                      |
| `sui-vertical-divider`           | `VerticalDivider`                   | `design`                             | Direct orientation-specific API                                                                                                      |
| `sui-icon`                       | `Icon`                              | `design`                             | `assetId` → exact SVG + Coil Painter, or existing Android drawable + `painterResource`; preserve semantic tint                       |
| `sui-icon-button`                | `IconButton`                        | `design`                             | `assetId`/slot → source-preserving Painter inside `Icon`; event → `onClick`                                                          |
| `sui-linear-progress`            | `LinearProgressIndicator`           | `design`                             | Fraction → `progress` lambda                                                                                                         |
| `sui-link`                       | `Link`                              | `design`                             | `click-action` → `onClick`                                                                                                           |
| `sui-list-item`                  | `ListItem`                          | `design`                             | Slots stay on `ListItem`; `click-action` → modifier; slots inherit `ListItemColors`                                                  |
| `sui-number-field`               | `NumberField`                       | `design`                             | Choose Int/Float/Double overload from domain model                                                                                   |
| `sui-option`                     | `Option`                            | `design`                             | `selected` → `onSelectChange`                                                                                                        |
| `sui-page-control`               | `PageControl`                       | `design`                             | Index/count → typed state and callback                                                                                               |
| `sui-progress-page-control`      | `ProgressPageControl`               | `design`                             | Preserve index and progress separately                                                                                               |
| `sui-scroll-indicator`           | `ScrollIndicator`                   | `design`                             | Bind to the real scroll/lazy state                                                                                                   |
| `sui-basic-scroll-indicator`     | `BasicScrollIndicator`              | `design`                             | Requires an explicit indicator state                                                                                                 |
| `sui-search-field`               | `SearchField`                       | `design`                             | `value`, change, and search callbacks                                                                                                |
| `sui-segment-control`            | `SegmentControl`                    | `design`                             | CSV options → child items; preserve size using the [Segment sizing example](./spatial-ui-components.md#segment-control-sizing)       |
| `sui-segment-item`               | `SegmentItem`                       | `design`                             | Child of `SegmentControl`; selected state + callback; preserve default state colors and slot inheritance                             |
| `sui-slider`                     | `Slider`                            | `design`                             | Preserve range, steps, and completion callback                                                                                       |
| `sui-symbol-slider`              | `SymbolSlider`                      | `design`                             | Symbol → `icon` slot                                                                                                                 |
| `sui-segment-slider`             | `SegmentSlider`                     | `design`                             | `step-change` → `onStepChange`                                                                                                       |
| `sui-side-navigation`            | `SideNavigation`                    | `design`                             | CSV convenience API → explicit sections/items                                                                                        |
| `sui-side-navigation-section`    | `SideNavigationSection`             | `design`                             | Child section with title/content slots                                                                                               |
| `sui-side-navigation-item`       | `SideNavigationItem`                | `design`                             | Preserve selected state and slot content                                                                                             |
| `sui-stepper`                    | `Stepper`                           | `design`                             | `step` event → `onStep`                                                                                                              |
| `sui-switch`                     | `Switch`                            | `design`                             | `checked` + `onCheckedChange`                                                                                                        |
| `sui-text`                       | `Text`                              | `design`                             | Variant → `PicoTheme.typography` role                                                                                                |
| `sui-text-area`                  | `TextArea`                          | `design`                             | Multiline state, validation, and support text                                                                                        |
| `sui-text-field`                 | `TextField`                         | `design`                             | Preserve leading/trailing/supporting slots                                                                                           |
| `sui-timepicker`                 | `Timepicker`                        | `design`                             | Use `TimepickerConfig` and typed callbacks                                                                                           |
| `sui-title-bar`                  | `TitleBar`                          | `design`                             | Title and action slots remain composable lambdas                                                                                     |
| `sui-toggle-button`              | `ToggleButton`                      | `design`                             | `checked-change` → `onCheckedChange`                                                                                                 |
| `sui-toggle-icon-button`         | `ToggleIconButton`                  | `design`                             | Checked state + icon content slot                                                                                                    |
| `sui-wheel-picker`               | `WheelPicker`                       | `design`                             | Items → count/getItemText; index → callback                                                                                          |
| `sui-basic-menu-item`            | `BasicMenuItem`                     | `design.menu`                        | Custom row content slot                                                                                                              |
| `sui-menu-item`                  | `MenuItem`                          | `design.menu`                        | Preserve title/subtitle/icon/submenu slots                                                                                           |
| `sui-menu`                       | `Menu`                              | `design.menu`                        | Web anchor → current Compose position provider                                                                                       |
| `sui-sub-menu`                   | `SubMenu`                           | `design.menu`                        | Preserve nested menu ownership                                                                                                       |
| `sui-stereo-image`               | `StereoImage`                       | `design`                             | Map layout to `TextureLayout`; use real asset input                                                                                  |
| `sui-alert-dialog`               | `AlertDialog`                       | `design.windows`                     | Explicit visibility + dismiss/confirm state                                                                                          |
| `sui-basic-alert-dialog`         | `BasicAlertDialog`                  | `design.windows`                     | Use only when structured dialog is insufficient                                                                                      |
| `sui-coachmark`                  | `CoachmarkBox`                      | `design.windows`                     | Must wrap the actual target component                                                                                                |
| `sui-simple-coachmark`           | `SimpleCoachmark`                   | `design.windows`                     | Render inside `CoachmarkBox` scope                                                                                                   |
| `sui-rich-coachmark`             | `RichCoachmark`                     | `design.windows`                     | Render inside `CoachmarkBox` scope                                                                                                   |
| `sui-image-coachmark`            | `ImageCoachmark`                    | `design.windows`                     | Render inside `CoachmarkBox` scope                                                                                                   |
| `sui-date-picker-dialog`         | `DatePickerDialog`                  | `design.windows`                     | Dialog state + picker content                                                                                                        |
| `sui-basic-sheet`                | `BasicSheet`                        | `design.windows`                     | Use only when structured sheets cannot express content                                                                               |
| `sui-head-image-sheet`           | `HeadImageSheet`                    | `design.windows`                     | Header image remains a composable slot                                                                                               |
| `sui-sheet`                      | `Sheet`                             | `design.windows`                     | Explicit visibility/dismissal; preserve action slots                                                                                 |
| `sui-snackbar-host`              | `SnackbarHost`                      | `design.windows`                     | Web `show()` → `LocalSnackbarHostState.current.show(...)`                                                                            |
| `sui-spatial-popup`              | `SpatialPopup`                      | `design.windows`                     | Web anchor → current popup position provider                                                                                         |
| `sui-subwindow`                  | `Subwindow`                         | `design.windows`                     | Root sibling; never flatten into a `Row` pane                                                                                        |
| `sui-attachment-panel`           | `AttachmentPanel`                   | `foundation.content` (builder scope) | Declare in `SpatialView(attachments = { ... })`; place its entity in the scene, preserving the declared parent and movement behavior |
| `sui-tab-bar`                    | `TabBar`                            | `design.windows`                     | Root edge ornament; items use the current DSL                                                                                        |
| `sui-toolbar`                    | `Toolbar`                           | `design.windows`                     | Root action ornament; not an in-page bar                                                                                             |
| `sui-augment`                    | `Augment`                           | `foundation.window`                  | Root attached ornament; use only in WindowContainer                                                                                  |

### Scene attachments

For `sui-attachment-panel`, use the
[AttachmentPanel reference](../../pico-spatial-app-designer/design/design-reference/components/AttachmentPanel/README.md)
for native declaration, appearance, and entity placement. Web row/group layout
does not establish native ECS parenting. A panel beside a rotating model stays
independent when its entity is not parented under that model's rotating entity.
Do not convert preview pixel offsets directly into scene meters. When the
design requires model-targeted drag, use the existing
[gesture reference](../../spatial-ui-ability/references/ability-gestures.md)
for hit targeting and drag units; it does not require changing a valid ECS implementation.

### Composed title bars

Do not reduce `sui-title-bar` to a string title and one action on each side.
The Compose API accepts structured `title` content, and both action lambdas may
emit multiple composables. Preserve an accepted title-bar composition inside
the `TitleBar(...)` call instead of moving its children into a sibling header
row.

For a two-line title with primary title and subtitle content, keep the inner
`Column` unforced unless the accepted design explicitly centers each line. For a bar with no actions or other content, let
`titleAlignment = TitleAlignment.CenterInBar` position the text-only title area against the whole bar; do not add
`horizontalAlignment = Alignment.CenterHorizontally` to that inner `Column` by
default. Keep the primary title on the component's implicit title styling and
render the semantic subtitle with a smaller, tertiary treatment:

```kotlin
TitleBar(
    modifier = Modifier.fillMaxWidth(),
    // Text-only bar, without leading/trailing actions or other content.
    titleAlignment = TitleAlignment.CenterInBar,
    title = {
        Column {
            Text(
                text = title,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = subtitle,
                style = PicoTheme.typography.bodySmall,
                color = PicoTheme.colorScheme.labelTertiary,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
    },
)
```

When the title slot contains an identity title group followed by a current-page
`SearchField`, and the accepted design declares no explicit internal spacing
override, restore the slot as a full-width `Row` and place a weighted `Spacer`
between the identity content and the fixed-width search field. The identity
content is a Column of primary title and optional subtitle; never move the
window subtitle into the body to make room for search. Do not add
title-slot padding or `Arrangement.spacedBy`; the native `TitleBar` owns its
outer and slot padding. An explicit user or visual-source layout fact overrides
this default.

```kotlin
TitleBar(
    modifier = Modifier.fillMaxWidth(),
    // Search-containing slot: distribute title and search within the available area.
    titleAlignment = TitleAlignment.Center,
    title = {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            // Keep slot typography and color implicit except primary-title weight 700.
            Text(text = title, fontWeight = FontWeight.Bold)
            // Consume the remaining title-slot width and keep search at its trailing edge.
            Spacer(modifier = Modifier.weight(1f))
            SearchField(
                value = query,
                onValueChange = onQueryChange,
                onSearch = onSearch,
                modifier = Modifier.width(searchWidth),
            )
        }
    },
    leadingActions = {
        IconButton(onClick = onPrimaryNavigation) {
            Icon(
                painter = primaryNavigationIcon,
                contentDescription = primaryNavigationDescription,
            )
        }
        IconButton(onClick = onSecondaryNavigation) {
            Icon(
                painter = secondaryNavigationIcon,
                contentDescription = secondaryNavigationDescription,
            )
        }
    },
    trailingActions = {
        IconButton(onClick = onPrimaryWindowAction) {
            Icon(
                painter = primaryWindowActionIcon,
                contentDescription = primaryWindowActionDescription,
            )
        }
        IconButton(onClick = onSecondaryWindowAction) {
            Icon(
                painter = secondaryWindowActionIcon,
                contentDescription = secondaryWindowActionDescription,
            )
        }
    },
)
```

Use the actual accepted children and dimensions rather than copying the
example actions or `24.dp` value. Search scoped to one content region remains
with that region. Wide title content and asymmetric actions must not overlap.

### Command buttons are not content containers

Use `Button` for a concise command such as Install, Retry, Save, or Confirm.
Do not use it as the shell for a card, catalog tile, metadata group, or
read-only detail panel merely to obtain hover, click, background, or disabled
styling. See
[`restoration-anti-patterns.md`](./restoration-anti-patterns.md#button-used-as-a-content-container)
for the rich-content anti-pattern and the custom clickable-layout alternative.

### Clickable list items

When `sui-list-item` declares `click-action`, keep `ListItem` as the component
and attach the action to its modifier:

```kotlin
ListItem(
    modifier = Modifier
        .fillMaxWidth()
        .clickable(
            enabled = enabled,
            onClick = onClick,
        ),
    // Preserve the restoration default when the design omits padding.
    padding = PaddingValues(16.dp),
    headlineContent = { Text(text = title, fontWeight = FontWeight.Bold) },
    supportingContent = { Text(text = description) },
    leadingContent = { Icon(painter = leadingIcon, contentDescription = null) },
    trailingContent = { Icon(painter = trailingIcon, contentDescription = null) },
)
```

When the accepted design omits ListItem padding, retain
`padding = PaddingValues(16.dp)` for 16dp on all four sides. This is the
design-to-app restoration default, not a claim about the SDK default. Omitted
design padding does not mean zero runtime padding and does not require extra
padding fields in the design stage. Do not omit this argument, replace it with
`PaddingValues(end = 16.dp)` (which zeros the other sides), or add another
`Modifier.padding(...)` by default. Explicit user requirements or authoritative
design measurements override this restoration value.

Do not convert it to `Button { ListItem(...) }`. That changes the component
hierarchy and button layout semantics. SpatialUI 6.1.9 `ListItem` already
provides its row hover treatment, so do not add another
`spatialHoverEffect()` around it. The concise `clickable` overload uses
`LocalIndication.current`; controller haptics are optional rather than a
condition for preserving the click action.

Keep `headlineContent`, `supportingContent`, `leadingContent`, and
`trailingContent` on the `ListItemColors` provided by the parent. If the design
requires a custom selected presentation, choose the effective
foreground/background set at the `ListItem` call and do not independently
recolor the child `Text` / `Icon` slots. A foreground may remain unchanged
across states when it is readable on every resulting background.

## Intent-only gate

For `input_mode=intent_only`, the designer package is incomplete for app
conversion if any condition holds:

- a declared `sui-*` component has no row in this mapping;
- a mapped tag is replaced by a hand-built equivalent without an explicit SDK
  availability failure.
- an icon asset is missing, replaced by text, or represented by a merely similar
  catalog icon instead of its authoritative or custom-drawn source;
- `preview.html` contains an app-owned component or design fact absent from
  `design-spec.json`.

Stop at Extract/Build and repair the mapping or component choice. Do not silently
fall back to custom Compose.

Only content-region Subwindow titles outside its TitleBar, and custom dialog/Sheet/popup headings declared with textRole: surface_title restore as Text with the accepted typography token and an immediately preceding // design-style: surface-title <node-id> marker. Pass the accepted design spec to the verifier; do not invent a Subwindow title slot.

### TitleBar alignment props

Map `props["title-alignment"]: "center-in-bar"` to
`TitleAlignment.CenterInBar`, and `"center"` to `TitleAlignment.Center`.
The latter preserves the remaining-space title slot with Native CenterStart
content alignment; it does not center the title text in the whole bar.
When absent, use CenterInBar only for a plain-text title or text-only
title/subtitle stack without leading/trailing actions or other content. Use
Center for buttons, search, or other content anywhere in the bar, including a
search-containing title slot, unless accepted source evidence overrides it.
`props["spacing-policy"]` on SideNavigation is a mapping directive; consume it
using the canonical restoration example or accepted explicit overrides, not as
a Kotlin argument.

### Advisory component contract checks

Every `sui-list-item` records `props["spacing-policy"]: "canonical"` unless
accepted user/design evidence requires `"explicit"`. Canonical means explicit
Native `padding = PaddingValues(16.dp)`, not omission that falls back to SDK
end=4dp. Explicit mode records `props["internal-padding-dp"]` with all four
`start`, `top`, `end`, `bottom` values; restore these as internal `padding`, not
`Modifier.padding` or layout padding. Parent layouts continue to own sibling gaps.
The policy is a restoration directive, not a Native argument.

Every TitleBar declares `props["title-alignment"]` in spec. During restoration,
compare the actual enum with the declared value, not a new composition inference.
Add `// design-node: <node-id>` immediately before a ListItem or TitleBar call
when existing implementation-map function anchors cannot uniquely locate it.
One shared call may list IDs separated by commas; their expected values must
agree or the dynamic state-to-parameter mapping remains unverified. Markers and
`source_mappings` locate code only; inspect actual call parameters, never accept
a receipt or comment as proof of correct values. Duplicate/unresolved links warn.

The implementation scan reports warnings only for missing, mismatched, or
unverified parameters and missing spec declarations. Each warning gives the
source/node, expected value when known, actual expression, and a review action.
Only uniform literal `PaddingValues(16.dp)` (or another literal in explicit mode)
is numerically recognized for ListItem at present. Other spellings, including
correct directional or horizontal/vertical forms, variables, and helpers, warn
as unverified rather than incorrect. Trace their definitions and manually check
all edges; correct code may remain, or use the canonical example to make static
checking possible. These warnings do not block validation or prove visual parity.

### Subwindow header design directives

Read the Subwindow header contract in
`../../pico-spatial-app-designer/references/design-spec-contract.md`. Preserve its
TitleBar/content/bottom-operation hierarchy and declared title placement.
`title-position`, `title-node-id`, `subtitle-node-id`, and `navigation-action`
are design directives, not SDK arguments. Subwindow's content/bottom-actions
slot markers identify normal layout regions; they do not invent native slots.
TitleBar leading/trailing map to leadingActions/trailingActions as before.

### Component defaults and property-level overrides

Apply the [component-default contract](spatial-ui-components.md): SideNavigationItem minimum height 48dp
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

### Full-width buttons

For `sui-button`, forward `props["fill-width"]` as the boolean `fill-width`
attribute. The component stretches both its host and internal button; do not use
external Shadow DOM selectors or defer this layout to Native. Compose restores
true as `Modifier.fillMaxWidth()`; false or absent keeps intrinsic width. Verify
the actual button bounds in install, installing, installed, and retry states.

## Toolbar restoration

Restore `sui-toolbar` as native Toolbar under its owning WindowContainer; a page
Box/Column declaration is valid and needs no align/attach/register. Preserve
page/selection visibility with composition and keep shared session controls
outside page switching when declared that way in the accepted design.

Without `segmented`, use the legacy `Toolbar(cornerSize = ...) { ... }` overload.
With `segmented=true`, use named `Toolbar(content = { ... }, ...)` even if no
supporting slot is present. Map the default slot to content, supporting slot to
supportingContent, and prefixed props using the Designer Web guide's Toolbar
configuration table to ToolbarDefaults.contentConfiguration() and
ToolbarDefaults.supportingConfiguration(). Convert padding from CSS edge order
to PaddingValues with physical left/right preserved (use absolute padding
values when needed). Preserve declared followViewpoints and focusable. Do not
flatten groups into a manually painted Row or translate preview offsets into
native positioning arguments. Legacy bottom+32dp and configurable center-on-edge
attachment differ for taller content; do not interchange the overloads. Confirm
API availability in the target SDK; report an unsupported overload rather than
silently changing the accepted design.
