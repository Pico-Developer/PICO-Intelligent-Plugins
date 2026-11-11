# PageControl

Dots for the position in a short set of pages. Item 32x24 (dot radius 4, spacing 12, vertical padding 8), `labelPrimaryLight` for the current dot, `fillSecondary` for the others.

## Details
- Up to 9 dots are shown (`NormalMax`), 16 for `ProgressPageControl`, never fewer than 5. With more pages the window slides and the dots at the edges shrink to 0.75 and 0.5.
- `ProgressPageControl` turns the current dot into a 16x8 pill that fills as the page scrolls. A custom icon can replace the current dot.
- Tapping another dot reports it; the dots have no hover or pressed color except the 12% pressed overlay on non-selected dots.

## When to use
- **Use for:** a carousel or onboarding with a handful of pages.
- **Don't use for:** navigation between app sections (use `TabBar`), long lists (use `ScrollIndicator`), progress of a task (use `LinearProgress`).
- **Alternatives:** `SegmentControl` when the pages have names.
- **Do:** center it under the content it controls; use the progress style when the pages scroll continuously.
- **Don't:** use it for a single page.

## Web API
- `<sui-page-control>` and `<sui-progress-page-control>` attributes: `count`, `index`, `progress` (progress style), `max-display-count`, `disabled`, `selected-color`, `unselected-color`.
- Events: `select` (`detail.index`).

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
