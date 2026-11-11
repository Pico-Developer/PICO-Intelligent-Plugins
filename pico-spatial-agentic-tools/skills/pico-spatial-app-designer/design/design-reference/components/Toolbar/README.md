# Toolbar

A window-attached operation area for the current content, selection, page task or ongoing session. Its content can combine commands, modes, parameters and concise task information.

## When to use

- **Use for:** browsing/viewing, editing, media playback, selection/batch actions and page-wide apply/save/reset. A window-based 3D task can use it for manipulation modes and parameters.
- **Don't use for:** switching app destinations or sections (use `TabBar` or `SideNavigation`), the window's own title actions (use `TitleBar`), a menu of commands (use `Menu`).
- **Alternatives:** `TitleBar` for window-level actions, `Menu` for overflow.
- **Do:** compose the actual task controls: text buttons, icons, selectors, sliders, concise inputs and context/status such as current object or selection count. Select controls by meaning; icon-only buttons are one option, not the Toolbar template.
- Keep field/item-specific operations beside their subject when moving them obscures their target. Toolbar can expose a concise parameter or search input, but does not carry a full form or primary content page.

## Task composition and scope

Explore makes the [task-tool decision](../../../layout-2d.md#task-tools-and-toolbar) before arranging the body. Plan implements its operations, target, host window, visibility, state retention and mode/selection changes. If a suitable opportunity was omitted, correct the design record rather than quietly adding a decorative bar.

| Example         | Main content                                | Optional supporting content         | Behavior to preserve                                                                                  |
| --------------- | ------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Content viewer  | Current object/page, previous/next and zoom | Find input and search command       | All controls act on the current content; search selects a matching item.                              |
| Editing         | Tool selector and current tool's parameter  | Undo, Apply and Reset text commands | Switching modes reveals their own parameters; edits affect the canvas and can be undone or committed. |
| Batch selection | Selection count and actions on the set      | Exit-selection command              | Appears for the selected set; changing selection updates count and targets.                           |
| Playback        | Media information, transport and seek       | Volume and queue entry              | Playback state can survive destination switches when the session scope requires it.                   |

Both groups can contain controls and concise information. Keep related operations together; split only at a functional or priority boundary. Supporting content may be absent. A Selector inside Toolbar can choose a tool or view; previous/next commands change current content. Neither implies navigation to another main app destination.

Toolbar may belong to a single page or only to a selection; it need not persist across the app. For a shared session, keep its state and composition outside page switching. Preserve a useful left sidebar or object list while Toolbar operates on its current selection. Avoid duplicate page controls and do not invent features to fill available space.

## Web API

- `<sui-toolbar>` attributes: `for` (id of the window it hangs under; without it the bar is shown inline), `segmented`, `offset-x`, `offset-y`. Default slot = main content; slot `supporting` for the second segment.
- `container-color` sets the main segment background color; `supporting-container-color` sets the supporting segment background color.

The Web preview uses the segment geometry defaults below. It does not expose the native per-segment material, radius, padding, item-gap or minimum-width configuration as Web attributes. The `ToolbarDefaults.*Configuration` APIs described below are native-only; this preview cannot verify those overrides.

## Plan composition and attachment

Use the [reference preview](preview.html) during Plan. It retains the original compact icon tools and the playback main/supporting composition with a volume slider. Inspect its component sizes, spacing and attachment before adapting the controls to the task. The task-content candidates above describe broader uses; they are not additional visual examples in this preview.

At least 64 high, radius 32, padding 12 and item gap 8 in the legacy form. Segmented defaults: radius 32, padding 8, item gap 4 and minimum width 72 per segment, with a native-owned 16 gap. Width is limited to the screen minus 64. Overflow does not automatically scroll; choose relevant controls or expose contextual groups rather than packing every candidate into one bar.

| Form                         | Web                                                     | Native placement                                                  |
| ---------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------- |
| Legacy single group          | `for="host"`                                            | Bar bottom at window bottom +32dp                                 |
| Configurable main/supporting | `for="host" segmented` and optional `slot="supporting"` | Bar center at window bottom, including when supporting is omitted |

The same 64-high baseline makes these coincide. At larger heights the distinction matters. This bundle explicitly updates segmented Web placement to the second rule. `offset-x/y` are browser preview conveniences; do not copy them into invented Compose parameters.

Native `Toolbar` is composed beneath a WindowContainer and attaches automatically; ordinary layout nesting does not turn it into an in-flow Row. Visibility follows composition. A session-wide toolbar belongs outside page-switch composition. Use `ToolbarDefaults` configurable APIs only when supported by the target SDK: `content`, optional `supportingContent`, `contentConfiguration`, `supportingConfiguration`. Each segment configuration owns material, background, radius, padding, item gap and minimum width; the native gap between segments is system-owned.

```kotlin
Toolbar(
    content = {
        Text("Selected: $selectedCount")
        Button(onClick = onAddToCollection, enabled = selectedCount > 0) {
            Text("Add to collection")
        }
    },
    supportingContent = {
        Button(onClick = onExitSelection) { Text("Done") }
    },
    supportingConfiguration = ToolbarDefaults.supportingConfiguration(itemGap = 8.dp),
)
```

The snippet uses application-owned selection state and callbacks. It illustrates text, a command and an exit action; resolve their visual configuration from the SDK and component guides. Verify imports/API support against the app SDK. Do not simulate attachment with a rounded Row, absolute offsets or a `modifier` argument on Toolbar. Web `for` makes attachment visible but cannot verify native follow/focus behavior.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. The added playback section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
