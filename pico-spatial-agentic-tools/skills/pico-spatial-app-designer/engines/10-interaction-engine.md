# Interaction Engine

## Responsibilities

Define gaze, pinch, drag, controller fallback, system back, high-risk confirmation, and recovery.

Role: `spatial_design_system_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 12, Eye-Hand Input Interaction Spec).

## Inputs

- Composition synthesis, state graph
- Reasoning conclusions from upstream stages

## Output (direct description, no longer bound to a Schema)

Directly describe the interaction spec in structured Markdown:

- system gesture support (all interactable elements support the indirect interaction of eye focus + pinch);
- gaze hover feedback state;
- gesture list (the mapping of pinch / drag / tap / zoom);
- controller fallback and system back;
- high-risk confirmation and error-recovery paths.

## Prohibitions

- bypassing upstream stages;
- describing project-level derivations as PICO official hard rules;
- manufacturing a "sense of space" by adding floating windows;
- hiding assumptions, exception states, or failure paths.
