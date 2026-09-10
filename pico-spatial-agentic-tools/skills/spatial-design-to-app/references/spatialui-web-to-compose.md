# SpatialUI Web → Compose Bridge

Use this reference after the `pico-spatial-app-designer` gate, especially for
`input_mode=intent_only`. The designer's `preview.html` is built from SpatialUI
Web components; those components are semantic proxies for the production
SpatialUI Compose APIs listed here.

## Hard conversion contract

1. Read `design-doc.md` §3 `SpatialUI Web component map` first, then inspect the
   actual `sui-*` tags used by `preview.html`.
2. Create an in-memory conversion inventory with one row per used tag:
   `web tag → semantic role → Compose API → state/callback → hierarchy`.
3. Use the mapped Compose API. A mapped `sui-*` tag is **not** eligible for
   `Box`/`Row`/`Text` reimplementation or
   `// TODO(missing-component)`.
4. Preserve component hierarchy. `design.windows` and `foundation.window`
   entries remain window-level/floating structures; they do not become page
   children just because the preview is HTML.
5. Translate behavior, not syntax:
   - attributes such as `checked`, `selected-index`, `value`, and `hidden`
     become state from the ViewModel/UI state holder;
   - DOM events become typed Compose callbacks;
   - named/default slots become composable lambdas;
   - CSS colors, radius, padding, and type map through `PicoTheme`, component
     defaults, and the authoritative design-doc tokens.
6. Do not copy Web-only convenience APIs into Kotlin. CSV attributes, string
   icons, `show()`, and HTML positioning are preview adapters. Verify the
   current Kotlin signature in the SDK API/reference before coding.
7. A custom Compose component is allowed only for a design-doc element that has
   no `sui-*` entry and no semantic SpatialUI match. Record the reason beside
   that element in the conversion inventory.

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
| `sui-toggleable-chip`            | `ToggleableChip`                    | `design`            | `selected` → `isToggleOn`                                 |
| `sui-circular-progress`          | `CircularProgressIndicator`         | `design`            | Select determinate overload from value presence           |
| `sui-symbolic-circular-progress` | `SymbolicCircularProgressIndicator` | `design`            | Symbol → `progressSymbol` slot                            |
| `sui-date-picker`                | `DatePicker`                        | `design`            | `date-select` → state callback                            |
| `sui-date-range-picker`          | `DateRangePicker`                   | `design`            | Start/end callbacks remain distinct                       |
| `sui-divider`                    | `Divider`                           | `design`            | Preserve orientation                                      |
| `sui-horizontal-divider`         | `HorizontalDivider`                 | `design`            | Direct orientation-specific API                           |
| `sui-vertical-divider`           | `VerticalDivider`                   | `design`            | Direct orientation-specific API                           |
| `sui-icon`                       | `Icon`                              | `design`            | Replace text glyph with a real drawable/vector            |
| `sui-icon-button`                | `IconButton`                        | `design`            | `click-action` → `onClick`                                |
| `sui-linear-progress`            | `LinearProgressIndicator`           | `design`            | Fraction → `progress` lambda                              |
| `sui-link`                       | `Link`                              | `design`            | `click-action` → `onClick`                                |
| `sui-list-item`                  | `ListItem`                          | `design`            | Headline/supporting/leading/trailing → slots              |
| `sui-number-field`               | `NumberField`                       | `design`            | Choose Int/Float/Double overload from domain model        |
| `sui-option`                     | `Option`                            | `design`            | `selected` → `onSelectChange`                             |
| `sui-page-control`               | `PageControl`                       | `design`            | Index/count → typed state and callback                    |
| `sui-progress-page-control`      | `ProgressPageControl`               | `design`            | Preserve index and progress separately                    |
| `sui-scroll-indicator`           | `ScrollIndicator`                   | `design`            | Bind to the real scroll/lazy state                        |
| `sui-basic-scroll-indicator`     | `BasicScrollIndicator`              | `design`            | Requires an explicit indicator state                      |
| `sui-search-field`               | `SearchField`                       | `design`            | `value`, change, and search callbacks                     |
| `sui-segment-control`            | `SegmentControl`                    | `design`            | CSV convenience API → explicit child items                |
| `sui-segment-item`               | `SegmentItem`                       | `design`            | Child of `SegmentControl`; selected state + callback      |
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

## Intent-only gate

For `input_mode=intent_only`, the designer package is incomplete for app
conversion if either condition holds:

- a used `sui-*` tag has no row in this mapping;
- a mapped tag is replaced by a hand-built equivalent without an explicit SDK
  availability failure.

Stop at Extract/Build and repair the mapping or component choice. Do not silently
fall back to custom Compose.
