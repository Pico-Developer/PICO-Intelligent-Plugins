# SpatialUI Component Inventory

Prefer the supported components listed here. SpatialUI is declarative (Compose-style)
and lives under `com.pico.spatial.ui.{platform, foundation, design}`.

> **Hard rule for codegen**: do not invent names like `SpatialButton` or
> `XRPanel`. This inventory is not the full SDK API surface. For an unlisted
> API, verify the target SDK's signature and import before use. Do not replace
> a required spatial capability with a `Box` or `Text` placeholder.

## Container-level (root nodes)

| layout.json `type` | Kotlin DSL                       | Where it goes                                        |
| ------------------ | -------------------------------- | ---------------------------------------------------- |
| `WindowContainer`  | `DefaultWindowContainer { ... }` | `mainApp(scope: SpatialAppScope)`                    |
| `Stage`            | `DefaultStage { ... }`           | `mainApp(scope: SpatialAppScope)`                    |
| `Toolbar`          | `Toolbar { ... }`                | inside container; auto-positioned by container style |

`WindowContainer` planar vs volumetric style is primarily controlled by
manifest metadata such as `pico.spatial.windowcontainer.style = 1 / 2`.

Stage immersion mode is primarily controlled by manifest metadata such as
`pico.spatial.stage.immersion`, `immersion_min`, and `immersion_max`.

## Layout primitives

| `type`       | Kotlin                              | Notes                          |
| ------------ | ----------------------------------- | ------------------------------ |
| `Column`     | `Column(modifier) { ... }`          | vertical stack                 |
| `Row`        | `Row(modifier) { ... }`             | horizontal stack               |
| `Box`        | `Box(modifier) { ... }`             | overlay / absolute positioning |
| `LazyColumn` | `LazyColumn { items(...) { ... } }` | scrollable list                |
| `LazyRow`    | `LazyRow { items(...) { ... } }`    | horizontal scrollable list     |
| `Spacer`     | `Spacer(Modifier.size(...))`        | gap                            |

## Atomic components (`com.pico.spatial.ui.design`)

| `type`                                                            | Kotlin                                       | Common props                          |
| ----------------------------------------------------------------- | -------------------------------------------- | ------------------------------------- |
| `Text`                                                            | `Text(text)`                                 | `text`, `style`                       |
| `Button`                                                          | `Button(onClick) { Text(...) }`              | `text`, `enabled`, `variant`          |
| `IconButton`                                                      | `IconButton(onClick) { Icon(...) }`          | `icon`, `contentDescription`          |
| `ToggleButton` / `ToggleIconButton`                               | `ToggleButton(...)`, `ToggleIconButton(...)` | checked action state                  |
| `ButtonChip` / `Chip` / `RemovableChip` / `ToggleableChip`        | corresponding chip API                       | filter/tag/display semantics          |
| `Badge` / `DotBadge` / `NumberBadge`                              | corresponding badge API                      | status/count indicator                |
| `Icon`                                                            | `Icon(...)`                                  | icon glyph only                       |
| `TextField`                                                       | `TextField(value, onValueChange)`            | `placeholder`, `label`                |
| `TextArea`                                                        | `TextArea(value, onValueChange)`             | multiline input                       |
| `SearchField`                                                     | `SearchField(...)`                           | search-box semantics                  |
| `NumberField`                                                     | `NumberField(...)`                           | numeric input                         |
| `Stepper`                                                         | `Stepper(...)`                               | discrete increment/decrement          |
| `Switch`                                                          | `Switch(checked, onCheckedChange)`           | `enabled`                             |
| `Slider` / `SymbolSlider` / `SegmentSlider`                       | corresponding slider API                     | continuous/symbol/discrete adjustment |
| `Checkbox` / `TriStateCheckbox`                                   | corresponding checkbox API                   | boolean/indeterminate state           |
| `Option`                                                          | `Option(...)`                                | selectable option row                 |
| `Divider` / `HorizontalDivider` / `VerticalDivider`               | corresponding divider API                    | orientation-specific separation       |
| `CircularProgressIndicator` / `SymbolicCircularProgressIndicator` | corresponding circular progress API          | loading/progress with optional symbol |
| `LinearProgressIndicator`                                         | `LinearProgressIndicator()`                  | progress track                        |
| `PageControl` / `ProgressPageControl`                             | corresponding page-control API               | page index/progress                   |
| `ScrollIndicator` / `BasicScrollIndicator`                        | corresponding scroll-indicator API           | bind to real scroll state             |
| `DatePicker` / `DateRangePicker`                                  | corresponding date picker API                | date/date-range selection             |
| `Timepicker` / `WheelPicker`                                      | corresponding picker API                     | time/general wheel selection          |
| `Link`                                                            | `Link(...)`                                  | lightweight link action               |
| `ListItem`                                                        | `ListItem(...)`                              | standard row with content slots       |
| `TitleBar`                                                        | `TitleBar(...)`                              | composable page header                |
| `SideNavigation` / `SideNavigationSection` / `SideNavigationItem` | corresponding side-navigation API            | in-page side navigation               |
| `SegmentControl` / `SegmentItem`                                  | `SegmentControl { SegmentItem(...) }`        | segmented switching                   |
| `StereoImage`                                                     | `StereoImage(...)`                           | stereo texture layout                 |

For an actionable `ListItem`, keep `ListItem` as the root and put
`clickable(...)` on its modifier; never wrap it in `Button`. See
[`spatialui-web-to-compose.md`](./spatialui-web-to-compose.md#clickable-list-items)
for the complete mapping.

### Segment control sizing

Native `SegmentControl` and `SegmentItem` defaults are based on Small. Select
`size` from the accepted `design-spec.json`; Regular is shown below, not a
blanket default. Apply its height, radius, item padding, and text style together.
Changing only container height does not change the item typography. Leave
`Text.style` omitted so the title inherits `SegmentItem.textStyle`.

```kotlin
import com.pico.spatial.ui.design.containerCornerRadius
import com.pico.spatial.ui.design.itemContentPadding
import com.pico.spatial.ui.design.textStyle

var selectedIndex by remember { mutableIntStateOf(0) }
// Match the spec's size. Native defaults are Small; this design uses Regular.
val size = SegmentControlDefaults.Regular
val options = listOf("List", "Grid", "Space")

SegmentControl(
    modifier = Modifier.height(size.height),
    cornerRadius = size.containerCornerRadius(),
) {
    options.forEachIndexed { index, label ->
        SegmentItem(
            selected = selectedIndex == index,
            onClick = { selectedIndex = index },
            title = { Text(label) },
            contentPadding = size.itemContentPadding(),
            textStyle = size.textStyle(),
        )
    }
}
```

Preserve explicit accepted geometry overrides separately; otherwise use the
selected size's SDK helpers rather than unrelated hardcoded metrics.

### Side navigation

The standard example includes the complete page skeleton so padding ownership
is unambiguous. The root row has no blanket padding or gap, SideNavigation stays
full-height on the left, TitleBar stays full-width at the top of the right-hand
page, and only the page body receives normal content padding:

```kotlin
@Composable
fun SideNavigationPageSample() {
    val items = listOf("Featured", "Categories", "Installed", "Updates")
    val selectedItem = remember { mutableStateOf(items.first()) }
    val query = remember { mutableStateOf("") }

    Row(modifier = Modifier.fillMaxSize()) {
        SideNavigation(
            modifier = Modifier.width(316.dp).fillMaxHeight(),
            header = {
                Column(modifier = Modifier.fillMaxWidth()) {
                    Box(
                        modifier =
                            Modifier.fillMaxWidth()
                                .height(96.dp)
                                .padding(
                                    start = 8.dp,
                                    top = 31.dp,
                                    bottom = 31.dp,
                                ),
                        contentAlignment = Alignment.CenterStart,
                    ) {
                        // Keep SideNavigation header typography and color implicit.
                        Text(
                            text = "Spatial Store",
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                    SearchField(
                        value = query.value,
                        onValueChange = { query.value = it },
                        onSearch = { query.value = it },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = {
                            Text("Search apps", maxLines = 1)
                        },
                    )
                    Spacer(modifier = Modifier.height(28.dp))
                }
            },
        ) {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                items.forEach { item ->
                    SideNavigationItem(
                        selected = selectedItem.value == item,
                        contentPadding = PaddingValues(
                            start = 16.dp,
                            top = 8.dp,
                            end = 8.dp,
                            bottom = 8.dp,
                        ),
                        modifier = Modifier.heightIn(min = 48.dp).clickable {
                            // This selection also drives the corresponding page content.
                            selectedItem.value = item
                        },
                    ) {
                        Text(
                            text = item,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
            }
        }

        Column(modifier = Modifier.weight(1f).fillMaxHeight()) {
            TitleBar(
                modifier = Modifier.fillMaxWidth(),
                titleAlignment = TitleAlignment.CenterInBar,
                title = {
                    // Override only primary-title weight; inherit other typography and color.
                    Text(
                        text = selectedItem.value,
                        fontWeight = FontWeight.Bold,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                },
            )
            Box(
                modifier =
                    Modifier.weight(1f)
                        .fillMaxWidth()
                        .padding(start = 32.dp, top = 0.dp, end = 32.dp, bottom = 32.dp),
            ) {
                Text("Content for ${selectedItem.value}")
            }
        }
    }
}
```

This is the canonical restoration pattern when the accepted design leaves
SideNavigation spacing unspecified. Omitted design padding does not mean zero
runtime padding. Keep `contentPadding` absent so SideNavigation owns its SDK
default. For a title-only header, retain the same title box and omit only the
surrounding search composition:

```kotlin
header = {
    Box(
        modifier =
            Modifier.fillMaxWidth()
                .height(96.dp)
                .padding(
                    start = 8.dp,
                    top = 31.dp,
                    bottom = 31.dp,
                ),
        contentAlignment = Alignment.CenterStart,
    ) {
        Text(
            text = title,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
    }
}
```

`316.dp` is the canonical default when no explicit user requirement, Figma
measurement, screenshot measurement, or other authoritative visual source
specifies the SideNavigation width. Preserve an accepted evidenced width when
one exists, but do not introduce a narrower responsive override from available
space or a generic compact breakpoint alone. SideNavigation already supplies
24dp horizontal content padding. The header retains its extra 8dp start padding; SearchField remains aligned
to the SideNavigation content edge. The restoration sample's item label uses
16dp start padding independently of the header title.

Use the header SearchField only when the accepted page skeleton assigns
scope-wide search to the app or current Tab/module represented by this
SideNavigation. Current-page search stays in that page's TitleBar.
The header contains exactly one single-line upper-scope identity title. Do not
add a subtitle, description, eyebrow, status, or other second identity line;
the only optional second element is the task-required scope-wide SearchField.
When the accepted design leaves canonical spacing unspecified, do not add
padding to the whole header Column or pass `contentPadding` to `SideNavigation`; use the title Box
shown above, keep SearchField aligned to the SideNavigation content edge, and
retain the 28dp bottom Spacer only when search exists. Explicit visual evidence
may override the narrowest owning child rather than wrapping all header content
in one generic padding modifier. Keep header text styling implicit by default;
do not add custom font, typography, or color unless the accepted design
explicitly requires it.
When providing a SearchField placeholder, keep its text single-line by default.

When item spacing is unspecified in the accepted design, use the restoration
sample's `SideNavigationItem` content padding: start 16dp, end/top/bottom 8dp,
and 4dp between adjacent items via the containing Column's
`Arrangement.spacedBy(4.dp)`. These are design-to-app restoration defaults,
not SDK defaults or extra fields required from the design stage. Explicit user
requirements or authoritative design measurements override these sample values.

`SideNavigationItem` still owns its row width, shape, and selected background.
Do not add item-level `fillMaxWidth()` or `padding(...)`, or a `Spacer` after
every item by default. List spacing stays outside each item's selected background;
it adds no leading or trailing list gap. The sample imposes a minimum item height of 48dp via `heightIn`.

## Window-level / spatial-specific UI

| `type`                                                                  | Kotlin                                                                    | Notes                                                                                    |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `TabBar`                                                                | `TabBar { ... }`                                                          | window-level edge navigation, not page content                                           |
| `Toolbar`                                                               | `Toolbar { ... }`                                                         | window-level action strip                                                                |
| `Subwindow`                                                             | `Subwindow { ... }`                                                       | independently persistent auxiliary window                                                |
| `AlertDialog` / `BasicAlertDialog`                                      | corresponding alert-dialog API                                            | structured/raw confirmation dialog                                                       |
| `DatePickerDialog`                                                      | `DatePickerDialog(...)`                                                   | specialized date-selection dialog                                                        |
| `Sheet` / `BasicSheet` / `HeadImageSheet`                               | corresponding sheet API                                                   | structured/raw/header-image modal                                                        |
| `CoachmarkBox` / `SimpleCoachmark` / `RichCoachmark` / `ImageCoachmark` | corresponding coachmark API                                               | anchored instructional guidance                                                          |
| `SnackbarHost`                                                          | `SnackbarHost { ... }`                                                    | transient feedback host + state                                                          |
| `SpatialPopup`                                                          | `SpatialPopup(...) { ... }`                                               | lightweight anchored floating layer                                                      |
| `Menu` / `SubMenu` / `MenuItem` / `BasicMenuItem`                       | corresponding menu API                                                    | menu and nested-menu semantics                                                           |
| `Augment`                                                               | `Augment(...) { ... }`                                                    | foundation window-attached ornament                                                      |
| `SpatialView`                                                           | `SpatialView(initial = ..., update = ..., attachments = ...)`             | host ECS scene entities; Compose panels enter through attachments                        |
| `SpatialModelView`                                                      | `SpatialModelView(source = Source.assets("models/model.glb"), ...)`       | load a model into Compose layout; select the loading-state/content overload deliberately |
| `AttachmentPanel`                                                       | `AttachmentPanel(id) { ... }` inside `SpatialView(attachments = { ... })` | Compose content represented by a scene entity; position via `attachments.entity(id)`     |

An `AttachmentPanel` is not a `Subwindow` or a window-edge ornament. It can be
placed in a Volume's bounded `SpatialView` scene as well as a Stage scene.
Entity parenting determines whether it follows a model: use separate scene
entities when the panel should stay stationary while the model rotates.
Use the [AttachmentPanel reference](../../pico-spatial-app-designer/design/design-reference/components/AttachmentPanel/README.md)
for the native DSL and placement example. For model-targeted drag, read
[spatial gestures](../../spatial-ui-ability/references/ability-gestures.md).
For version and import resolution, see [API lookup](spatial-api-imports.md).

## Overlay / popup / subwindow boundary

Use these distinctions consistently:

| Input semantics                                    | First choice                                         |
| -------------------------------------------------- | ---------------------------------------------------- |
| small help bubble / tooltip / anchored menu        | overlay in the main panel, optionally `SpatialPopup` |
| detached but lightweight contextual floating layer | `SpatialPopup`                                       |
| long-lived tool panel or side detail window        | `Subwindow`                                          |
| multiple disconnected major surfaces               | true `multi_window` reasoning, not `SpatialPopup`    |

If the input is ambiguous, choose the smallest explanation first:

`overlay in main panel` → `SpatialPopup` → `Subwindow` → `multi_window`

## Imports cheat sheet (for codegen)

```kotlin
import com.pico.spatial.ui.foundation.dsl.*
import com.pico.spatial.ui.design.*
import com.pico.spatial.ui.design.windows.*
```

3D-related (Stage / SpatialModelView):

```kotlin
import com.pico.spatial.ui.foundation.content.*
```

Tracking / anchors (only valid in Stage; verified against SpatialSDK source — package is `com.pico.spatial.sense.*`, NOT `com.pico.spatial.tracking.*`):

```kotlin
import com.pico.spatial.sense.world.WorldTrackingManager
import com.pico.spatial.sense.world.WorldAnchor
import com.pico.spatial.sense.world.WorldTrackingResult
// Plane / mesh anchors:
// import com.pico.spatial.sense.plane.{PlaneTrackingManager, PlaneAnchor}
// import com.pico.spatial.sense.mesh.{MeshTrackingManager, MeshAnchor}
// ECS-side anchor entity:
// import com.pico.spatial.core.ecs.{AnchorEntity, AnchorComponent}
// import com.pico.spatial.core.ecs.anchor.AnchorTarget
```

## What's NOT here (do not emit)

These names look plausible but DO NOT exist in Spatial SDK:

- `SpatialButton`, `SpatialText`, `SpatialCard`, `SpatialList`
- `XRPanel`, `XRWindow`, `VRView`
- `Window`, `Screen`, `Page` (these are not Spatial container types)
- Anything from `androidx.compose.material3.*` directly — Spatial SDK has
  its own design module. Don't mix.

If an input needs something not on this list, generate a `Box` with a
`// TODO(missing-component): describe-what-was-here` comment rather than
inventing a name.

## Common mistakes

- Do not treat `SpatialPopup` as proof of `multi_window`; it is still a floating layer choice.
- Do not upgrade a master-detail page to `Subwindow` unless the detail panel is independently persistent.
- Do not use `TabBar` / `Toolbar` as ordinary page content containers. Toolbar may be declared inside a page `Column` or `Box`; it attaches to the current WindowContainer and occupies no ordinary layout space. See `spatial-windows-guide.md` → Toolbar for overloads and lifecycle.
- Prefer `SearchField` over a hand-built `TextField + search icon + placeholder` when the input clearly shows search-box semantics.
- A `TitleBar` containing only a plain-text title or text-only title/subtitle stack, with no leading/trailing actions or other content, uses `TitleAlignment.CenterInBar`. Buttons, search, or other content anywhere in the bar use `TitleAlignment.Center`; a title slot containing `SearchField` retains the full-width weighted-spacer pattern. Restore explicit spec alignment, and use this whole-bar rule when absent. Verify these enum values against the project SDK; explicit source alignment overrides the default.
- Keep slot typography and color implicit except primary TitleBar title weight 700
  and the text identified by `subtitle-node-id`, which explicitly uses `bodyMedium`
  / `labelSecondary` without override evidence. Other styles require that the accepted design overrides
  the exact slot and records `styleOverrideEvidence` from the original user
  requirement, Figma, or a screenshot.
- `TitleBar` APIs vary by SDK version: `title` is often a `@Composable` lambda and newer variants may use `endContent` rather than `actions`; verify the signature before assuming raw `String` / `actions` parameters. On versions with `leadingActions` / `trailingActions`, each lambda may emit multiple composables, and `title` may contain structured content such as a title plus a current-page `SearchField`. Preserve that composition instead of flattening its children into a sibling row.
- `TabBar` may expose DSL-style `item(...)` entries rather than a dedicated `TabItem`. Do not assume `icon = painterResource(...)` or `onClick = {}` parameters exist on every SDK version; common item shape is `item(text = ..., selected = ..., modifier = Modifier.clickable { ... }, itemIcon = { Icon(...) })`.
- Chips / tags can contain icons. If the design shows chip icons, model the chip content as a `Row` or slot-based structure instead of plain `Text`.
- `Button` is for a concise command, not a generic card, catalog tile, metadata group, or read-only detail surface. Use `ListItem` for a standard actionable row, a custom layout with spatial hover plus `clickable` / `selectable` when rich item layout is required, and a plain layout for read-only content.
- Configure `IconButton` through its component APIs: shell color via `colors = ButtonDefaults.buttonColors(containerColor = ...)`, render size via `IconButtonDefaults.iconButtonSize(...)`, outer size via `modifier = Modifier.size(...)`. Avoid painting `Modifier.background()` / `clip()` directly on the `IconButton` shell.
- **Do not rebuild `TabBar` / `Toolbar` by hand.** A rounded capsule pinned to the top/bottom/left/right edge of the window is a window-level fitting, not page content. The wrong shape looks like:

  ```kotlin
  // WRONG — collapses window_plus_subwindow back to single_panel_with_popup
  Box(modifier = Modifier.fillMaxSize()) {
      MainPage()
      Box(modifier = Modifier.align(Alignment.TopCenter)) {
          Row(Modifier.clip(RoundedCornerShape(24.dp)).background(...)) {
              tabs.forEach { /* clickable capsule */ }
          }
      }
  }
  ```

  The correct shape uses the SDK fitting under WindowContainer (including inside a page Composable), with no `align(...)` wrapping — the system positions it at the window edge:

  ```kotlin
  // CORRECT — true window-level edge navigation
  DefaultWindowContainer {
      PicoTheme {
          Box(modifier = Modifier.fillMaxSize()) {
              MainPage()
              TabBar(placement = TabBarPlacement.Top) {
                  tabs.forEach { tab ->
                      item(
                          text = tab.label,
                          selected = state.selected == tab,
                          modifier = Modifier.clickable { onSelect(tab) },
                          itemIcon = null,
                      )
                  }
              }
          }
      }
  }
  ```

  Note: window-level fittings (`TabBar` / `Toolbar`) do **not** accept a `modifier` parameter at the call site — their position is owned by the system. If you find yourself wanting to pass `Modifier.align(...)` into one of them, you have picked the wrong shape.

## Hover effects (verified against the current SpatialUI capability knowledge base)

PICO design rules require every hoverable container to use
`Modifier.spatialHoverEffect`. **Reimplementing hover via Compose's
`hoverable + animateFloatAsState(scale)` is BLOCKED** by the
`spatial-ui-design-style` verifier.

### Authoritative imports

| Symbol                                         | Fully-qualified name                                             |
| ---------------------------------------------- | ---------------------------------------------------------------- |
| `Modifier.spatialHoverEffect`                  | `com.pico.spatial.ui.foundation.hover.spatialHoverEffect`        |
| Spatial Hover `spring`                         | `com.pico.spatial.ui.foundation.hover.spring`                    |
| Spatial Hover `tween`                          | `com.pico.spatial.ui.foundation.hover.tween`                     |
| `SpatialHoverStyle.Default` / `.Highlight`     | `com.pico.spatial.ui.graphics.SpatialHoverStyle`                 |
| `Modifier.spatialHoverEffectGroup(group)`      | `com.pico.spatial.ui.foundation.hover.spatialHoverEffectGroup`   |
| `SpatialHoverEffectGroup.obtain()`             | `com.pico.spatial.ui.foundation.hover.SpatialHoverEffectGroup`   |
| `Modifier.disableSpatialHoverEffect(disabled)` | `com.pico.spatial.ui.foundation.hover.disableSpatialHoverEffect` |

### Four usage shapes

```kotlin
// 1. preset style (shortest)
import com.pico.spatial.ui.foundation.hover.spatialHoverEffect
import com.pico.spatial.ui.foundation.hover.spring
import com.pico.spatial.ui.foundation.hover.tween
import com.pico.spatial.ui.graphics.SpatialHoverStyle

Box(Modifier.size(100.dp).spatialHoverEffect())                     // = SpatialHoverStyle.Default
Box(Modifier.spatialHoverEffect(style = SpatialHoverStyle.Highlight))

// 2. custom DSL
Box(Modifier.spatialHoverEffect {
    scale(if (it.isActive) 1.1f else 1f)
    offset(y = if (it.isActive) (-4).dp else 0.dp)
    alpha(if (it.isActive) 1f else 0.8f)
})

// 3. custom animation curves
Modifier.spatialHoverEffect {
    animation(tween(durationMillis = 250)) { scale(if (it.isActive) 1.05f else 1f) }
    animation(spring(stiffness = 700f))    { offset(y = if (it.isActive) (-4).dp else 0.dp) }
}

// 4. cross-view coordination (hover group)
import com.pico.spatial.ui.foundation.hover.SpatialHoverEffectGroup
import com.pico.spatial.ui.foundation.hover.spatialHoverEffectGroup

val group = remember { SpatialHoverEffectGroup.obtain() }
items.forEach { Card(Modifier.spatialHoverEffectGroup(group).spatialHoverEffect()) { /* ... */ } }
```

Spatial Hover animation blocks must use the `tween` and `spring` imports shown
above. Do not substitute the same-named `androidx.compose.animation.core`
builders; they return Compose animation specs rather than `SpatialHoverAnimation`.

### Mandatory modifier order

```
clip → background → spatialHoverEffect → clickable
```

`clip` defines the shape first, `spatialHoverEffect` reads that shape, then
`clickable` appends the click behaviour. Wrong order → hover highlight does
**not** track the `clip` boundary. App-authored content borders are not part of
this chain.

### When NOT to add `spatialHoverEffect`

- Built-in interactive components (`Button`, `IconButton`, SpatialUI design
  components) **already include** hover; do not stack another one. To
  suppress, use `Modifier.disableSpatialHoverEffect(true)`.
- Only add `.spatialHoverEffect().clickable{}` manually for **custom
  clickable containers** or item composables (e.g. `SideNavigationItem`).

For full DSL coverage and edge cases see
`../../spatial-ui-ability/SKILL.md` § 3 Hover Effects and
`spatial-api-imports.md`.

### Canonical spacing policy and advisory review

Record `props["spacing-policy"]: "canonical"` on `sui-side-navigation` when
there is no user or authoritative visual spacing requirement. Use `"explicit"`
with evidenced overrides on their owning nodes otherwise. This is a restoration
directive, not a Native component parameter. Legacy omitted policy means canonical
only when there are no explicit spacing overrides; do not erase accepted overrides.

The canonical title band is 96dp and vertically centers one 34dp line with 31dp
above and below. SearchField follows with zero top inset and a 28dp bottom Spacer;
keep its Native height. Without search there is no search Spacer. Below TitleBar,
body top padding defaults to 0dp in design and restoration unless the user requests
otherwise. These defaults align the first visible search/item and body block.

`scan_implementation.py` reports advisory warnings for missing or unverifiable
canonical header, item content padding, and list spacing. Check the accepted spec
before repairing a warning; explicit source overrides take precedence. Opaque
helpers or mixed policies require review and must not be reported as verified.

### Independent ListItem spacing

Put gaps in the parent layout, outside each item's rounded surface:

```kotlin
Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
    ListItem(
        modifier = Modifier.fillMaxWidth(),
        padding = PaddingValues(16.dp),
        headlineContent = { Text("Spatial audio") },
    )
    ListItem(
        modifier = Modifier.fillMaxWidth(),
        padding = PaddingValues(16.dp),
        headlineContent = { Text("Media volume") },
    )
}
```

Counterexample — do not use the item's own modifier to create a sibling gap:

```kotlin
ListItem(
    modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
    padding = PaddingValues(16.dp),
    headlineContent = { Text("Spatial audio") },
)
```

The current SDK applies `clip(shape)` before the supplied modifier, then draws
its background inside that modifier. Bottom padding therefore becomes part of
the clip bounds while the background ends earlier, distorting the lower corners.
Use parent `Arrangement.spacedBy` or an external wrapper/Spacer for sibling gaps;
this does not prohibit the component's internal content padding.

### Component defaults and property-level overrides

SideNavigationItem defaults to a minimum height of 48dp, content padding of
start 16dp and top/end/bottom 8dp, and a parent-list gap of 4dp. Compose must
explicitly use `Modifier.heightIn(min = 48.dp)`; the Web item already has
`min-height:48px`. A gap or padding override never cancels the height default.
TitleBar primary-title text defaults to weight 700. Compose must explicitly use
`fontWeight = FontWeight.Bold` (import `androidx.compose.ui.text.font.FontWeight`),
since the SDK does not guarantee that weight. Keep its font family, size, line
height, and foreground inherited. Do not apply this weight to subtitles,
actions, SearchField text, or SideNavigation headers.

Only an original user requirement or authoritative Figma/screenshot evidence
can override a particular property. For a component-level height or weight
override, record `props["min-height-dp"]` or `props["title-font-weight"]` on the
owning component and `styleOverrideEvidence: { source, reference }` on that same
node. A fixed item height can instead use `layout.heightDp` with that evidence;
restore it with `Modifier.height(...)` and pass the same explicit height as the
Web item's `min-height-dp` attribute so its default minimum does not conflict.
Do not populate these override fields with inferred defaults. Other attributes
retain their defaults. Add `// design-node: <node-id>` immediately before the
corresponding Compose component when an override needs source/spec matching;
multiple state nodes may share a call only if their requirements agree.

The implementation scanner checks item height and primary-title weight
independently of spacing policy. Missing constraints or known incorrect values
fail. Dynamic values, opaque helpers, or ambiguous override correspondence are
unverified warnings requiring review, never verified evidence. Explicit
requirements are checked against their recorded value; unevidenced override
fields cannot exempt a default. Resolve these failures and warnings during
Compose review before claiming fidelity.
