# Experience Engine

## Responsibilities

Plan Glance, Explore, and Immerse; not all three layers are required, and immersion must have clear task value.

Role: `interaction_xr_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 7, Experience and Container Architecture).

## Inputs

- Selected concept, approved visual reference
- Reasoning conclusions from upstream stages

## Outputs (direct description, no longer bound to a Schema)

Describe the experience architecture directly in structured Markdown:

- Experience-layer division (Glance / Explore / Immerse are just usable vocabulary, not a mandatory template);
- Each layer's responsibilities, host, entry/exit, and fallback;
- The clear task value of the immersion layer.

## Prohibitions

- Bypassing upstream stages;
- Describing project-derived conclusions as PICO official hard rules;
- Manufacturing a "sense of space" by adding floating windows;
- Hiding assumptions, error states, or failure paths.
