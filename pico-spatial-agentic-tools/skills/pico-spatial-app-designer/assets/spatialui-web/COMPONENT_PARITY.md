# SpatialUI Web component parity

This catalog maps every public visual Composable in `spatialui/design/api/current.txt`
to its Web Custom Element. Kotlin overloads share a tag and are selected with
attributes or slots. Defaults/state/provider APIs are JavaScript properties or
methods rather than DOM elements.

| SpatialUI API                       | Web component                    | Notes                                          |
| ----------------------------------- | -------------------------------- | ---------------------------------------------- |
| `Badge`                             | `sui-badge`                      | Text/content attribute or default slot         |
| `DotBadge`                          | `sui-dot-badge`                  | Direct equivalent                              |
| `NumberBadge`                       | `sui-number-badge`               | `number` and `threshold`                       |
| `Button`                            | `sui-button`                     | Named leading/trailing slots                   |
| `Checkbox`                          | `sui-checkbox`                   | `state=on/off`                                 |
| `TriStateCheckbox`                  | `sui-tri-state-checkbox`         | `state=indeterminate` supported                |
| `ButtonChip`                        | `sui-button-chip`                | Alias of the shared chip renderer              |
| `Chip`                              | `sui-chip`                       | Base chip                                      |
| `RemovableChip`                     | `sui-removable-chip`             | Emits `remove`                                 |
| `ToggleableChip`                    | `sui-toggleable-chip`            | Selectable chip                                |
| `CircularProgressIndicator`         | `sui-circular-progress`          | Determinate/indeterminate                      |
| `SymbolicCircularProgressIndicator` | `sui-symbolic-circular-progress` | Symbol slot/attribute                          |
| `DatePicker`                        | `sui-date-picker`                | Emits `date-select`                            |
| `DateRangePicker`                   | `sui-date-range-picker`          | Emits `range-change`                           |
| `Divider`                           | `sui-divider`                    | Orientation attribute                          |
| `HorizontalDivider`                 | `sui-horizontal-divider`         | Explicit alias                                 |
| `VerticalDivider`                   | `sui-vertical-divider`           | Explicit alias                                 |
| `Icon`                              | `sui-icon`                       | Text/icon slot representation                  |
| `IconButton`                        | `sui-icon-button`                | Direct equivalent                              |
| `LinearProgressIndicator`           | `sui-linear-progress`            | Direct equivalent                              |
| `Link`                              | `sui-link`                       | Emits `click-action`                           |
| `ListItem`                          | `sui-list-item`                  | Leading/trailing content attributes            |
| `NumberField`                       | `sui-number-field`               | Integer/float/double use the same number input |
| `Option`                            | `sui-option`                     | Selectable option                              |
| `PageControl`                       | `sui-page-control`               | Direct equivalent                              |
| `ProgressPageControl`               | `sui-progress-page-control`      | `progress` fraction                            |
| `ScrollIndicator`                   | `sui-scroll-indicator`           | Direction/fraction attributes                  |
| `BasicScrollIndicator`              | `sui-basic-scroll-indicator`     | Explicit low-level variant                     |
| `SearchField`                       | `sui-search-field`               | Direct equivalent                              |
| `SegmentControl`                    | `sui-segment-control`            | CSV convenience API                            |
| `SegmentItem`                       | `sui-segment-item`               | Composable child form                          |
| `Slider`                            | `sui-slider`                     | Direct equivalent                              |
| `SymbolSlider`                      | `sui-symbol-slider`              | Symbol attribute                               |
| `SegmentSlider`                     | `sui-segment-slider`             | Emits `step-change`                            |
| `SideNavigation`                    | `sui-side-navigation`            | CSV convenience API                            |
| `SideNavigationSection`             | `sui-side-navigation-section`    | Composable child form                          |
| `SideNavigationItem`                | `sui-side-navigation-item`       | Composable child form                          |
| `Stepper`                           | `sui-stepper`                    | Direct equivalent                              |
| `Switch`                            | `sui-switch`                     | Direct equivalent                              |
| `Text`                              | `sui-text`                       | Type-scale variant attribute                   |
| `TextArea`                          | `sui-text-area`                  | Multiline TextField alias                      |
| `TextField`                         | `sui-text-field`                 | Direct equivalent                              |
| `Timepicker`                        | `sui-timepicker`                 | Composes wheel pickers                         |
| `TitleBar`                          | `sui-title-bar`                  | Composed title; repeated actions               |
| `ToggleButton`                      | `sui-toggle-button`              | Direct equivalent                              |
| `ToggleIconButton`                  | `sui-toggle-icon-button`         | Emits `checked-change`                         |
| `WheelPicker`                       | `sui-wheel-picker`               | Direct equivalent                              |
| `BasicMenuItem`                     | `sui-basic-menu-item`            | Custom row slot                                |
| `MenuItem`                          | `sui-menu-item`                  | Title/subtitle/icon slots                      |
| `Menu`                              | `sui-menu`                       | Anchor-relative top-layer popup                |
| `SubMenu`                           | `sui-sub-menu`                   | End-aligned nested menu                        |
| `StereoImage`                       | `sui-stereo-image`               | `none` / `side-by-side` / `top-and-bottom`     |
| `AlertDialog`                       | `sui-alert-dialog`               | Structured slots                               |
| `BasicAlertDialog`                  | `sui-basic-alert-dialog`         | Raw dialog surface                             |
| `CoachmarkBox`                      | `sui-coachmark`                  | Anchor plus coachmark surface                  |
| `SimpleCoachmark`                   | `sui-simple-coachmark`           | Explicit variant alias                         |
| `RichCoachmark`                     | `sui-rich-coachmark`             | Explicit variant alias                         |
| `ImageCoachmark`                    | `sui-image-coachmark`            | Explicit variant alias                         |
| `DatePickerDialog`                  | `sui-date-picker-dialog`         | Title/action slots                             |
| `BasicSheet`                        | `sui-basic-sheet`                | Raw sheet surface                              |
| `HeadImageSheet`                    | `sui-head-image-sheet`           | Header-image slot                              |
| `Sheet`                             | `sui-sheet`                      | Title/action/bottom slots                      |
| `SnackbarHost`                      | `sui-snackbar-host`              | `show()` queue and `dismiss()`                 |
| `SpatialPopup`                      | `sui-spatial-popup`              | Anchor-relative top-layer popup                |
| `Subwindow`                         | `sui-subwindow`                  | Left/right host-attached panel                 |
| `TabBar`                            | `sui-tab-bar`                    | Direct equivalent                              |
| `Toolbar`                           | `sui-toolbar`                    | Legacy/segmented modes                         |

`PicoTheme` maps to the `PicoTheme` JavaScript API and CSS custom properties.
`ProvideTextStyle` maps to inherited CSS typography. Internal provider and selection
plumbing has no standalone visual element. `Augment` is a public foundation
container rather than a `spatialui/design` Composable and maps to `sui-augment`.
