# SegmentControl

A row of exclusive segments on a `fillTertiary` track. Container padding 4, item gap 4, items share the width equally.

## Sizes
- Small: 40 high, radius 25, item padding 12/8, `labelMedium`. Default.
- Regular: 48 high, radius 24, item padding 12/11, `labelLarge`.
- Rich: 88 high, radius 12, item padding 12/17, icon above the title (gap 4), `labelLarge`. The SDK samples use 16dp icons in Small and 24dp in Rich.
- Items use the container radius.

## Colors
- Selected: `fillSecondary` with `labelPrimary`. Unselected: transparent with `labelTertiary`. Hover is the native spatial hover effect on a PICO device (gaze or ray), not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white) under the content.

## When to use
- **Use for:** switching between two to four views of the same content: Day / Week / Month.
- **Don't use for:** navigation between app sections (use `TabBar` or `SideNavigation`), independent filters (use `Chip`), big descriptive choices (use `Option`).
- **Alternatives:** `TabBar` for top-level navigation, `Option` for larger choices, `ToggleButton` for a single on/off.
- **Do:** keep labels short and of similar length; use Rich only when icons carry meaning.
- **Don't:** use more than five segments or let labels wrap.

## Web API
- `<sui-segment-control>` attributes: `options` (comma list), `icons` (comma list of icon names), `selected-index`, `size` (`small`, `regular`, `rich`), `disabled`, `container-color`. Give the host a width; segments share it.
- Events: `select` (`detail.index`, `detail.value`).

The Rich preview uses List / Grid / Gallery as peer views of the same three saved scenes. Its `select` handler changes only the layout of the existing content: compact rows, a three-column grid, or a horizontally scrollable gallery. Labels, item order and item count stay the same across views; the content remains secondary to the SegmentControl.

## Plan size and content rule

Small remains the reference/native default. Choose Small/Regular/Rich explicitly from the design; do not treat a Regular example as a new default. Size includes height, container radius, item padding and typography together. Changing only the height is incomplete.

Native composition uses the chosen `SegmentControlDefaults` size with `size.height`, `size.containerCornerRadius()`, `size.itemContentPadding()` and `size.textStyle()`; leave title Text style inherited from SegmentItem. Record deliberate overrides separately. Use the icon-bearing example when icons clarify list/grid modes; preserve concise labels and make the selected segment actually switch that content.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
