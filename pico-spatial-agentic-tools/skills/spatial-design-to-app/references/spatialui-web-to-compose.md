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
6. Do not copy Web-only convenience APIs into Kotlin. CSV attributes, string
   icons, `show()`, and HTML positioning are preview adapters. Resolve each icon
   through the declared source priority. For `icon70://7.0/<name>`, copy the
   referenced VectorDrawable with the Designer's `icon-catalog.mjs`. For
   `design-assets/icons/*.svg`, produce the matching VectorDrawable through
   `icon-drawing.md`. Use `painterResource`, apply the design token as tint, and
   never substitute a text glyph or emoji. Verify the current Kotlin signature
   in the SDK API/reference before coding.
7. A custom Compose component is allowed only for a `domain_visual` node that
   has no `sui-*` entry and no semantic SpatialUI match. Preserve its
   `rendererKey`, purpose, data bindings, dimensions, colors, and interaction
   contract; record the implementation choice in the conversion inventory.
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

| SpatialUI Web tag                | Compose API                         | Package             | Conversion note                                           |
| -------------------------------- | ----------------------------------- | ------------------- | --------------------------------------------------------- |
| `sui-badge`                      | `Badge`                             | `design`            | Default/content slot → `content`                          |
| `sui-dot-badge`                  | `DotBadge`                          | `design`            | Preserve semantic status color                            |
| `sui-number-badge`               | `NumberBadge`                       | `design`            | `number`/`threshold` remain numeric                       |
| `sui-button`                     | `Button`                            | `design`            | `click-action` → `onClick`; slots → icon lambdas          |
| `sui-checkbox`                   | `Checkbox`                          | `design`            | `state` → `checked` + `onCheckedChange`                   |
| `sui-tri-state-checkbox`         | `TriStateCheckbox`                  | `design`            | Map indeterminate state explicitly                        |
| `sui-button-chip`                | `ButtonChip`                        | `design`            | Label/icon slots and `onClick`                            |
| `sui-chip`                       | `Chip`                              | `design`            | Preserve clickable vs display-only semantics              |
| `sui-removable-chip`             | `RemovableChip`                     | `design`            | `remove` → `onTrailingRemoveClick`                        |
| `sui-toggleable-chip`            | `ToggleableChip`                    | `design`            | `selected` → `isToggleOn`; preserve default state colors and slot inheritance |
| `sui-circular-progress`          | `CircularProgressIndicator`         | `design`            | Select determinate overload from value presence           |
| `sui-symbolic-circular-progress` | `SymbolicCircularProgressIndicator` | `design`            | Symbol → `progressSymbol` slot                            |
| `sui-date-picker`                | `DatePicker`                        | `design`            | `date-select` → state callback                            |
| `sui-date-range-picker`          | `DateRangePicker`                   | `design`            | Start/end callbacks remain distinct                       |
| `sui-divider`                    | `Divider`                           | `design`            | Preserve orientation                                      |
| `sui-horizontal-divider`         | `HorizontalDivider`                 | `design`            | Direct orientation-specific API                           |
| `sui-vertical-divider`           | `VerticalDivider`                   | `design`            | Direct orientation-specific API                           |
| `sui-icon`                       | `Icon`                              | `design`            | `assetId` → exact drawable + `painterResource`            |
| `sui-icon-button`                | `IconButton`                        | `design`            | `assetId`/slot → exact drawable; event → `onClick`        |
| `sui-linear-progress`            | `LinearProgressIndicator`           | `design`            | Fraction → `progress` lambda                              |
| `sui-link`                       | `Link`                              | `design`            | `click-action` → `onClick`                                |
| `sui-list-item`                  | `ListItem`                          | `design`            | Slots stay on `ListItem`; `click-action` → modifier; slots inherit `ListItemColors` |
| `sui-number-field`               | `NumberField`                       | `design`            | Choose Int/Float/Double overload from domain model        |
| `sui-option`                     | `Option`                            | `design`            | `selected` → `onSelectChange`                             |
| `sui-page-control`               | `PageControl`                       | `design`            | Index/count → typed state and callback                    |
| `sui-progress-page-control`      | `ProgressPageControl`               | `design`            | Preserve index and progress separately                    |
| `sui-scroll-indicator`           | `ScrollIndicator`                   | `design`            | Bind to the real scroll/lazy state                        |
| `sui-basic-scroll-indicator`     | `BasicScrollIndicator`              | `design`            | Requires an explicit indicator state                      |
| `sui-search-field`               | `SearchField`                       | `design`            | `value`, change, and search callbacks                     |
| `sui-segment-control`            | `SegmentControl`                    | `design`            | CSV convenience API → explicit child items                |
| `sui-segment-item`               | `SegmentItem`                       | `design`            | Child of `SegmentControl`; selected state + callback; preserve default state colors and slot inheritance |
| `sui-slider`                     | `Slider`                            | `design`            | Preserve range, steps, and completion callback            |
| `sui-symbol-slider`              | `SymbolSlider`                      | `design`            | Symbol → `icon` slot                                      |
| `sui-segment-slider`             | `SegmentSlider`                     | `design`            | `step-change` → `onStepChange`                            |
| `sui-side-navigation`            | `SideNavigation`                    | `design`            | CSV convenience API → explicit sections/items             |
| `sui-side-navigation-section`    | `SideNavigationSection`             | `design`            | Child section with title/content slots                    |
| `sui-side-navigation-item`       | `SideNavigationItem`                | `design`            | Preserve selected state and slot content                  |
| `sui-stepper`                    | `Stepper`                           | `design`            | `step` event → `onStep`                                   |
| `sui-switch`                     | `Switch`                            | `design`            | `checked` + `onCheckedChange`                             |
| `sui-text`                       | `Text`                              | `design`            | Variant → `PicoTheme.typography` role                     |
| `sui-text-area`                  | `TextArea`                          | `design`            | Multiline state, validation, and support text             |
| `sui-text-field`                 | `TextField`                         | `design`            | Preserve leading/trailing/supporting slots                |
| `sui-timepicker`                 | `Timepicker`                        | `design`            | Use `TimepickerConfig` and typed callbacks                |
| `sui-title-bar`                  | `TitleBar`                          | `design`            | Title and action slots remain composable lambdas          |
| `sui-toggle-button`              | `ToggleButton`                      | `design`            | `checked-change` → `onCheckedChange`                      |
| `sui-toggle-icon-button`         | `ToggleIconButton`                  | `design`            | Checked state + icon content slot                         |
| `sui-wheel-picker`               | `WheelPicker`                       | `design`            | Items → count/getItemText; index → callback               |
| `sui-basic-menu-item`            | `BasicMenuItem`                     | `design.menu`       | Custom row content slot                                   |
| `sui-menu-item`                  | `MenuItem`                          | `design.menu`       | Preserve title/subtitle/icon/submenu slots                |
| `sui-menu`                       | `Menu`                              | `design.menu`       | Web anchor → current Compose position provider            |
| `sui-sub-menu`                   | `SubMenu`                           | `design.menu`       | Preserve nested menu ownership                            |
| `sui-stereo-image`               | `StereoImage`                       | `design`            | Map layout to `TextureLayout`; use real asset input       |
| `sui-alert-dialog`               | `AlertDialog`                       | `design.windows`    | Explicit visibility + dismiss/confirm state               |
| `sui-basic-alert-dialog`         | `BasicAlertDialog`                  | `design.windows`    | Use only when structured dialog is insufficient           |
| `sui-coachmark`                  | `CoachmarkBox`                      | `design.windows`    | Must wrap the actual target component                     |
| `sui-simple-coachmark`           | `SimpleCoachmark`                   | `design.windows`    | Render inside `CoachmarkBox` scope                        |
| `sui-rich-coachmark`             | `RichCoachmark`                     | `design.windows`    | Render inside `CoachmarkBox` scope                        |
| `sui-image-coachmark`            | `ImageCoachmark`                    | `design.windows`    | Render inside `CoachmarkBox` scope                        |
| `sui-date-picker-dialog`         | `DatePickerDialog`                  | `design.windows`    | Dialog state + picker content                             |
| `sui-basic-sheet`                | `BasicSheet`                        | `design.windows`    | Use only when structured sheets cannot express content    |
| `sui-head-image-sheet`           | `HeadImageSheet`                    | `design.windows`    | Header image remains a composable slot                    |
| `sui-sheet`                      | `Sheet`                             | `design.windows`    | Explicit visibility/dismissal; preserve action slots      |
| `sui-snackbar-host`              | `SnackbarHost`                      | `design.windows`    | Web `show()` → `LocalSnackbarHostState.current.show(...)` |
| `sui-spatial-popup`              | `SpatialPopup`                      | `design.windows`    | Web anchor → current popup position provider              |
| `sui-subwindow`                  | `Subwindow`                         | `design.windows`    | Root sibling; never flatten into a `Row` pane             |
| `sui-tab-bar`                    | `TabBar`                            | `design.windows`    | Root edge ornament; items use the current DSL             |
| `sui-toolbar`                    | `Toolbar`                           | `design.windows`    | Root action ornament; not an in-page bar                  |
| `sui-augment`                    | `Augment`                           | `foundation.window` | Root attached ornament; use only in WindowContainer       |

### Composed title bars

Do not reduce `sui-title-bar` to a string title and one action on each side.
The Compose API accepts structured `title` content, and both action lambdas may
emit multiple composables. Preserve an accepted title-bar composition inside
the `TitleBar(...)` call instead of moving its children into a sibling header
row.

When search is app-wide or persists across the primary content modes, and the
accepted design does not place it elsewhere, compose the mapped `SearchField`
with the title content:

```kotlin
TitleBar(
    modifier = Modifier.fillMaxWidth(),
    titleAlignment = TitleAlignment.Center,
    title = {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(24.dp),
        ) {
            Text(text = title)
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
with that region. Check the current SDK signature before choosing
`TitleAlignment.Center` or `TitleAlignment.CenterInBar`; wide title content and
asymmetric actions must not overlap.

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
    headlineContent = { Text(text = title) },
    supportingContent = { Text(text = description) },
    leadingContent = { Icon(painter = leadingIcon, contentDescription = null) },
    trailingContent = { Icon(painter = trailingIcon, contentDescription = null) },
)
```

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
