# Motion Engine

## Responsibilities

Each motion declares trigger, purpose, duration, spatial range, reduce-motion, and performance fallback; camera movement and continuous flickering are prohibited.

Role: `spatial_design_system_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 13, Motion Spec).

## Inputs

- Composition synthesis, state graph, interaction spec
- Reasoning conclusions from upstream stages

## Output (direct description, no longer bound to a Schema)

Directly describe the motion spec in structured Markdown. Each motion gives: trigger, purpose, duration, spatial range, Reduce Motion fallback, performance fallback. Camera movement or continuous flickering must not be declared.

Also define the global accessibility contract: `reduceMotion`, `controllerFallback`, `colorIndependentSemantics`, `textScaling`, `stableExit`—these are the baseline of spatial-app usability and must be explicitly enabled and explained.

## Prohibitions

- bypassing upstream stages;
- describing project-level derivations as PICO official hard rules;
- manufacturing a "sense of space" by adding floating windows;
- hiding assumptions, exception states, or failure paths.
