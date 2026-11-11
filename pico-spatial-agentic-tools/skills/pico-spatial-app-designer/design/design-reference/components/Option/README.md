# Option

A toggleable selection tile that the screen can compose into single-choice or multiple-choice groups. Minimum 120x48, radius 12 (`radiusMediumLarge`), padding 8 vertical and 16 horizontal, gap 4 between icon and label, `bodyLarge` (16/20, 500).

## Colors
- Selected: `fillSecondary` with `labelPrimary`. Unselected: `fillTertiary` with `labelPrimary`.
- It is a toggleable: pressing a selected option reports `selected = false`; the screen owns group membership, exclusivity and whether an empty selection is allowed.
- Disabled alpha 0.3. Hover is the native spatial hover effect on a PICO device (gaze or ray), not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white) under the content.

## When to use
- **Use for:** a few large, labelled choices: plan, language, mode. Lay them out in a row or grid.
- **Don't use for:** compact filters (use `Chip`), a view switcher (use `SegmentControl`), an on/off setting (use `Switch`).
- **Alternatives:** `SegmentControl` for two to four short views, `Checkbox` for many independent choices, `Chip` for tags.
- **Do:** give the group a label; keep the labels the same length.
- **Don't:** use more than about six; mix selected styling by hand.

## Selection rules

Option does not automatically deselect its siblings. The native SDK supports both single-choice and multiple-choice compositions through caller-owned state. The preview demonstrates three independent groups:

| Mode | Select another option | Press the selected option | Initial state |
| --- | --- | --- | --- |
| Multiple choice | Keep existing selections | Deselect that option; an empty group is allowed | Option A selected |
| Single choice, optional | Deselect the previous option | Clear the selection | No selection |
| Single choice, required | Deselect the previous option | Keep the current selection | Option A selected |

Maintain a set of selected IDs for multiple choice, or one selected ID (nullable for optional selection) for single choice. Listen for `checked-change` within the owning group, update that group's state and synchronize its options' `checked` attributes. In the required group, preserve the current ID on a deselection request and restore its `checked` attribute: the Web component toggles itself before emitting the event. These are page-level rules, not new Option attributes or changes to the component's toggle behavior.

Give each group a visible label and explain whether users may select several options or clear the selection. Groups on the same page must not clear each other's selections. Disabled options cannot be activated.

## Web API
- `<sui-option>` attributes: `label`, `checked`, `icon`, `disabled`, `checked-container-color`, `container-color`, `content-color`.
- Events: `checked-change` (`detail.checked`).

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference options as an explicitly labelled multiple-choice group. The two added single-choice sections are labelled as Plan recommendations; all three use the original component defaults and keep selection rules in the page. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
