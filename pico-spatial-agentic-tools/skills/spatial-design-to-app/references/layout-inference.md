# Layout Inference

Companion guide for `visual_design` and `visual_reference` work, between **window model selection**
and **writing UI code**.

Use this when you need help deciding **how to decompose a screenshot or mockup
into semantic regions** instead of ad-hoc boxes.

## Region-first checklist

Identify the largest structural blocks before looking at icons, chips, or cards:

- header / title bar
- sidebar / nav rail
- tab bar
- list region
- grid region
- detail pane
- footer / toolbar
- popup / overlay

If you start from leaf elements first, you will usually miss the page structure.

## Heuristics

| Visual pattern                                                                  | Likely layout meaning                                                              |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Left narrow column + wide right content                                         | sidebar + content                                                                  |
| Narrow list pane + wide detail pane with richer content                         | master-detail                                                                      |
| Rounded outer frame around everything                                           | single panel root                                                                  |
| Rounded frame that **touches the window edges** (background bleeds to the edge) | `root fill + internal inset` — root fills the window, inset lives on inner content |
| Rounded card with visible margin/gap **between the card and the window edge**   | `outer padding card` — root is an inset card carrying its own outer padding        |
| Small floating rectangle overlapping a panel edge                               | popup / overlay                                                                    |
| Repeated identical rows with icons and text                                     | list template                                                                      |
| Large pane with section title + right-side actions                              | content section with header                                                        |

## Anti-patterns

### Anti-pattern: Pixel-first box explosion

Do not translate every visual rectangle into a `Box` immediately.

### Anti-pattern: Ignoring overlay anchoring

An overlay should stay attached to the triggering region in your structure.

### Anti-pattern: Losing repeated-item semantics

If six rows share one structure, record one item template and six data instances.

### Anti-pattern: Generic Compose too early

Do not reduce semantic regions to generic `Row` / `Column` / `Box` labels too early.
Finalize region roles first; component mapping belongs back in the main skill flow.

### Anti-pattern: Unowned spacing / ambiguous root fill

Do not treat an inset/padding/gap as a loose number without deciding which node
owns it, and do not leave the root shell's fill behaviour implicit. See "Spacing
ownership & root fill" below.

## Spacing ownership & root fill

Two structures look identical in a flat screenshot and produce different code.
Decide which one you are looking at **before** writing any modifier:

| Structure                      | What you see                                                                       | How it is built                                                                                                                           |
| ------------------------------ | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Root fill + internal inset** | The panel surface reaches the window edges; only the content inside is inset       | Root shell is edge-to-edge (`fillMaxSize`, background/surface on the root). Padding lives on the **inner** containers, never on the root. |
| **Outer padding card**         | A visibly smaller card floats inside the window, with background showing around it | The root carries its own outer padding/margin, and the card is the inset child.                                                           |

Rules:

1. **Decide root fill explicitly.** Never let codegen infer whether the root
   shell fills the window. Getting this wrong produces either an edge inset on a
   surface that should be flush, or a missing outer margin.
2. **Give every meaningful gap exactly one owner.** For each inset, padding, gap,
   or margin, name the single node responsible for it. Two nodes both applying
   the same gap is the most common source of double padding.
3. **Distinguish the two structures above before coding.** A frame touching the
   window edges is root fill; a card with a visible margin around it is an outer
   padding card.

## Relational alignment and repeated-item rhythm

Read [Gap and radius](../../pico-spatial-app-designer/references/spatial-design-rules.md#gap-and-radius)
for default sibling gaps and custom bounded surface radii. Existing padding
ownership and content-top constraints retain priority; do not add a blanket top
inset below TitleBar.

Read alignment as a relationship between visible references, not isolated
coordinates. During extraction, record the participating regions, reference
(top, bottom, text baseline, or content edge), gap owner, and resize behavior
in the existing extraction notes/design document. Encode resolved dimensions,
padding, gaps, growth, and alignment in existing layout fields; do not invent
parallel schema fields. For Figma, inspect Auto Layout and nested component
insets as well as bounding boxes. Distinguish measured facts from assumptions.

- **Heading row above a content grid.** Follow the
  [shared-column design rule](../../pico-spatial-app-designer/references/spatial-design-rules.md#header-rows-above-repeated-content).
  Preserve the spec's column boundaries, widths, gaps, and declared heading /
  content alignment. Start/end alignment includes the content's nested insets;
  center alignment uses a shared reference area and centerline. Do not center
  headings independently or align them to card edges when the accepted design
  aligns them to padded text. Missing relations are repaired in the design
  package before freeze, including internal regions of `domain_visual` nodes.
- **Shared-size or spanning modules (cells, ListItems, cards, or subregions).**
  When heights are close and contents fit, normalize to one row height and gap.
  When one module is substantially taller, prefer a complete integer row span
  from the same content origin: `spanHeight = n * rowHeight + (n - 1) * rowGap`.
  Titles align separately by baseline. Long or expanded content gets an explicit
  content-adaptive template rather than clipping to fit the span.
- **Large tile beside stacked small tiles.** Align the large tile's top and
  bottom with the complete stack's top and bottom. For two small rows,
  `largeHeight = 2 * smallHeight + rowGap`; for n rows,
  `largeHeight = sum(rowHeights) + (n - 1) * rowGap`. Share the parent band
  height or derive one dimension from this relation, rather than independently
  sizing each tile. Preserve image aspect/crop behavior. At narrow widths,
  reflow coherently instead of breaking the relation through clipping.
- **Calendar beside an upcoming-event list.** Compare the month heading and
  Upcoming heading on a shared baseline/header band. Compare the calendar
  cells and event rows on the content grid below that band; weekday labels
  are a separate structural band. When the source/request calls for it, use
  the calendar cell height and row gap for event rows, with compatible content
  insets. Do not stretch three events to match an entire multi-week calendar
  or assume every calendar/list pair must have equal row heights. Preserve
  longer text through wrapping/reflow rather than silently breaking the grid.
- **List-item edge balance.** Measure visible leading content to the surface
  edge and trailing control to the opposite edge. Include the item's padding,
  nested accessory padding, control bounds, and any slot margin. An asymmetric
  outer padding may produce balanced visible insets. Preserve native ListItem
  inset ownership before adding custom slot padding; for custom rows, give
  both edges an explicit owner. Let the text area consume remaining width,
  keep trailing commands inside the surface, and test long labels. Do not
  use only leading padding, remove trailing inset with fillMaxWidth, or add
  a second full inset to a native slot that already owns it.
- **Title-bar composition.** Only a plain-text title or text-only title/subtitle
  stack with no leading/trailing actions or other content uses `CenterInBar`.
  Buttons, search, or other content anywhere in the bar require `Center` by
  default; title plus SearchField retains the canonical weighted spacer.
  Restore explicit spec alignment; when absent, use the same whole-bar rule.
  Confirm API availability in the project SDK. Explicit source layout wins.
- **Overlay hierarchy.** Inspect the open dialog/Sheet/popup/detail state as a
  separate composition: semantic title, supporting metadata/body, then actions.
  A detail title must be distinguishable through native title treatment or a
  stronger exact title token, weight, and spacing. The ordinary-body size
  preference must not erase it. Do not invent headings for deliberately
  titleless transient feedback, or promote all overlay text to title size.

Review the accepted relations at the primary and minimum window sizes, including
long list labels, trailing actions, and an open overlay. Missing relations in a
new design are repaired before freeze. During restoration, implement accepted
facts exactly; report inherited defects instead of changing the frozen design.
Static source checks cannot prove visual edge/baseline alignment; use rendered
content bounds in the existing visual review pass.

## Minimum review checklist

Before freezing measured metrics, content semantics, or the region list, verify:

- Did I identify the root panel correctly?
- Did I decide `root_fill` (`fill_window` vs `padded_card`) explicitly, and map every inset/padding/gap to an owner in `spacing_ownership`?
- Did I separate persistent regions from overlays?
- Did I mark repeated structures?
- Did I preserve visible state?
- Did I choose one coherent layout tree rather than mixing multiple interpretations?

> Back to: SKILL.md — Extract stage (visual input guardrails) and Build stage (UI rules)

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
