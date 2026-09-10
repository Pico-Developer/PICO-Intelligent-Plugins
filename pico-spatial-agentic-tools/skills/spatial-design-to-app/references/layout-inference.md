# Layout Inference

Companion guide for `visual_reference` work, between **window model selection**
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

## Minimum review checklist

Before freezing measured metrics, content semantics, or the region list, verify:

- Did I identify the root panel correctly?
- Did I decide `root_fill` (`fill_window` vs `padded_card`) explicitly, and map every inset/padding/gap to an owner in `spacing_ownership`?
- Did I separate persistent regions from overlays?
- Did I mark repeated structures?
- Did I preserve visible state?
- Did I choose one coherent layout tree rather than mixing multiple interpretations?

> Back to: SKILL.md — Extract stage (visual input guardrails) and Build stage (UI rules)
