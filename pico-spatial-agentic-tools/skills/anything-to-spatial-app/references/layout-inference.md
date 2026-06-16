# Layout Inference

This guide covers the step between **window model selection** and **Kotlin generation**.

Goal: convert the source input into a stable, semantic layout tree instead of ad-hoc boxes.

## Inference order

### 1. Identify major regions first

Look for the biggest structural blocks before any component mapping:

- header / title bar
- sidebar / nav rail
- tab bar
- list region
- grid region
- detail pane
- footer / toolbar
- popup / overlay

If you start from icons or cards first, you will miss the page structure.

### 2. Find repeated structures

Explicitly detect repeated patterns such as:

- navigation items
- tabs
- list rows
- file cards
- option rows
- toolbar buttons

These should become templates, not copy-pasted unique elements.

### 3. Mark stateful elements

For each repeated structure, detect visible state when present:

- selected
- highlighted
- disabled
- locked
- expanded / collapsed
- focused
- searchable / filtered
- hovered / pressed when clearly implied

State is part of structure, not a later visual polish step.

### 4. Determine relationships

Record how regions relate:

- horizontal split (`Row`)
- vertical stack (`Column`)
- overlay anchored to parent
- centered floating card
- nested section inside content pane
- z-order between base content and overlays
- likely interaction trigger for each overlay or secondary panel

### 5. Only then map to components

Preferred sequence:

1. region tree
2. repeated templates
3. visible state
4. z-order / interaction assumptions
5. alignment / spacing
6. component mapping

## Suggested scratch shape

```json
{
  "regions": [
    {
      "id": "main_panel",
      "type": "panel",
      "layout": "row",
      "children": ["sidebar", "content"]
    },
    {
      "id": "sidebar",
      "type": "nav_region",
      "repeated": "nav_item",
      "states": ["selected"]
    },
    {
      "id": "content",
      "type": "content_region",
      "children": ["toolbar", "tabs", "list"]
    },
    {
      "id": "popup_menu",
      "type": "overlay",
      "anchor": "content.top_right",
      "repeated": "option_row",
      "trigger": "toolbar.more_button",
      "z_index": "above_content"
    }
  ],
  "repeated_structures": ["nav_item", "option_row", "content_card"],
  "states": ["selected_nav_item", "search_enabled", "popup_visible"]
}
```

## Heuristics

| Visual pattern | Likely layout meaning |
|---|---|
| Left narrow column + wide right content | sidebar + content |
| Narrow list pane + wide detail pane with richer content | master-detail |
| Rounded outer frame around everything | single panel root |
| Small floating rectangle overlapping a panel edge | popup / overlay |
| Repeated identical rows with icons and text | list template |
| Large pane with section title + right-side actions | content section with header |

## SpatialUI-first mapping hints

Once the structure is stable, prefer these first-choice mappings:

| Semantic region | First-choice SpatialUI mapping |
|---|---|
| persistent side nav | `SideNavigation` / `SideNavigationItem` |
| top tabs | `TabBar` or `SegmentControl` |
| toolbar actions | `Toolbar`, `IconButton`, or a custom `Row` |
| contextual popup | panel-local overlay, then `SpatialPopup` only if needed |
| secondary floating utility panel | `Subwindow` or additional `WindowContainer` only when independently persistent |
| search region | `SearchField` |

If a SpatialUI component is not a clear fit, keep the semantic structure and use plain Compose layout primitives rather than inventing SDK names.

## Anti-patterns

### Anti-pattern: Pixel-first box explosion
Do not translate every visual rectangle into a `Box` immediately.

### Anti-pattern: Ignoring overlay anchoring
An overlay should stay attached to the triggering region in your structure.

### Anti-pattern: Losing repeated-item semantics
If six rows share one structure, record one item template and six data instances.

### Anti-pattern: Generic Compose too early
Do not map everything to `Row` / `Column` / `Box` before you decide whether a real
SpatialUI component such as `SideNavigation`, `TabBar`, `Toolbar`, or `Subwindow`
matches the semantics.

## Minimum review checklist

Before code generation, verify:

- Did I identify the root panel correctly?
- Did I separate persistent regions from overlays?
- Did I mark repeated structures?
- Did I preserve visible state?
- Did I choose one coherent layout tree rather than mixing multiple interpretations?
