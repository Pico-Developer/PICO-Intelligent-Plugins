# Composition Synthesis Engine

## Responsibilities

Synthesize each layout from task relationships, data relationships, interaction frequency, the PICO methodology window default / min / max, and spatial constraints. Do not pick layout names from a domain pack or case study.

Role: `spatial_design_system_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 14, Layout Skeleton and Placement Geometry).

## Inputs

- State graph, PICO methodology window sizing (default / min / max, content area, reflow), approved visual references
- Reasoning conclusions from upstream stages

## Output (direct description, no longer bound to a Schema)

Describe each layout in structured Markdown:

- derivation evidence (task relationships, data relationships, interaction frequency, spatial constraints);
- a single primary focus;
- region division (regions) and content ownership;
- density limits;
- responsive transformations (Large / Compact / Constrained reflow, which must correspond to the window default / min / max);
- rejected options and reasons.

## Prohibitions

- picking layout names from a domain pack or case study;
- inventing layout sizes divorced from the window default / min / max;
- replacing structured region / skeleton descriptions with prose;
- describing project-level derivations as PICO official hard rules;
- hiding assumptions, exception states, or failure paths.
