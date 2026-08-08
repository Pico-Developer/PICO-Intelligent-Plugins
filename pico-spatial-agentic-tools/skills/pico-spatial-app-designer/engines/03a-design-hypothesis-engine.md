# Design Hypothesis Engine

## Responsibilities

Generate at least three substantially different spatial product concepts from the task graph and the spatial value graph.

Role: `interaction_xr_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 5, Design Hypotheses).

## Inputs

- Task / Decision Model, spatial value justification
- Reasoning conclusions from upstream stages

## Outputs (direct description, no longer bound to a Schema)

Describe ≥3 substantially different design hypotheses in structured Markdown. The differences must be reflected in:

- Information model;
- Container strategy;
- Spatialization approach;
- Navigation;
- Interaction;
- Engineering trade-offs.

Differing only in color / theme does not count as a substantial difference.

## Prohibitions

- Passing off color / skin differences as substantially different hypotheses;
- Describing project-derived conclusions as PICO official hard rules;
- Hiding assumptions, error states, or failure paths.
