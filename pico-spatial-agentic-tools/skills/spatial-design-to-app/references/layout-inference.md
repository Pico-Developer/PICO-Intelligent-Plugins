# Layout Inference

Companion guide for `visual_reference` work between **window model selection** and **contract freeze**.

Use this file when `SKILL.md` already tells you **what** artifacts must exist, but you still need help deciding **how to decompose a screenshot/mockup into semantic regions** instead of ad-hoc boxes.

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

| Visual pattern | Likely layout meaning |
|---|---|
| Left narrow column + wide right content | sidebar + content |
| Narrow list pane + wide detail pane with richer content | master-detail |
| Rounded outer frame around everything | single panel root |
| Rounded frame that **touches the window edges** (background bleeds to the edge) | `root fill + internal inset` — root fills the window, inset lives on inner content |
| Rounded card with visible margin/gap **between the card and the window edge** | `outer padding card` — root is an inset card carrying its own outer padding |
| Small floating rectangle overlapping a panel edge | popup / overlay |
| Repeated identical rows with icons and text | list template |
| Large pane with section title + right-side actions | content section with header |

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
Do not record inset/padding/gap as a loose number without deciding which node owns
it, and do not leave whether the root shell fills the window implicit. Every gap
must map to one owner in `spacing_ownership`, and `root_fill` must be explicit.
Confusing `root fill + internal inset` with `outer padding card` produces edge-inset
and margin bugs at codegen time (see `layout-schema.md` → "Spacing ownership & root
fill").

## Minimum review checklist

Before freezing `content_layout_metrics`, `visual_content_contract`, or `regions[]`, verify:

- Did I identify the root panel correctly?
- Did I decide `root_fill` (`fill_window` vs `padded_card`) explicitly, and map every inset/padding/gap to an owner in `spacing_ownership`?
- Did I separate persistent regions from overlays?
- Did I mark repeated structures?
- Did I preserve visible state?
- Did I choose one coherent layout tree rather than mixing multiple interpretations?

> Back to: SKILL.md Phase 3 (Visual input guardrails) / Phase 5 (Plan)
