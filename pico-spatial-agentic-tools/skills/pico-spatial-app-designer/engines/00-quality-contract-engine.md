# Project Quality Contract Engine

Derive the quality contract from this brief. Do not adopt historical projects or visual templates.

Role: `product_strategist`. Reasoning conclusions are recorded in [`roles/review-templates/pm-requirement-spec.md`](../roles/review-templates/pm-requirement-spec.md) (Section 7, Quality Contract).

## Outputs (direct description, no longer bound to a Schema, no longer subject to validator gates)

The quality contract is derived from this requirement and serves as the anchor for all subsequent stages and design reviews. Define it directly in structured Markdown:

- **Required user outcomes (outcomes)**: an acceptance-testable list of outcomes that serves as the anchor for design reviews and the traceability table.
- **Success / efficiency criteria**: time or efficiency targets.
- **Risks and must-not-fail items**: high-risk confirmations, safety boundaries, etc.
- **Default visible primary-window orientation**: how many primary WindowContainers can be visible simultaneously by default; if a Stage-only architecture is adopted, declare it here.
- **Domain-specialized component orientation**: the expected richness that domain components should reach.
- **Real-time data trust orientation**: whether alerts are required to always carry a source, whether freshness is always visible, etc.
- **PICO platform and spatial-design hard constraints**: key platform compliance items.
- **Originality requirement**: make defensible differentiation on top of the market baseline. Differentiation goals must be anchored to the "our differentiation opportunities" in the §3A competitive benchmark summary of [`uxr-research-report.md`](../roles/review-templates/uxr-research-report.md) — specifying which competitor strengths this product should absorb, which anti-patterns to avoid, and which PICO spatial capabilities to use to build competitiveness, rather than vaguely claiming to be "better".
- **Design / readability / downstream implementation acceptance plan**: how to verify that the design is complete, the documentation is readable, and the implementation is handoff-ready.

> Contract first: the orientations above are the reasoning premises for all subsequent stages. If this stage does not define them explicitly, downstream reasoning loses its anchor and quality standards get quietly relaxed — therefore they must be explicitly defined here rather than left to defaults.
