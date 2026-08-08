# Layout and Window Sizing Engine

## Responsibilities

After determining default / min / max from the PICO window sizing methodology, combine user decisions, information topology, the central comfort zone, and window attachment footprint to form the layout skeleton; do not start from cards or a fixed Web canvas.

Role: `spatial_design_system_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 9, Window Sizing Derivation; Section 14, Layout Skeleton and Placement Geometry).

## Required Reading

Before landing the layout, you must read and follow the default / min / max, clear field of view, hit target, font size, depth, and attachment-overhead rules in [`knowledge/spatial-window-sizing-methodology.md`](../knowledge/spatial-window-sizing-methodology.md); do not establish a separate window sizing method at the layout stage.

## Inputs

- Composition synthesis, state graph, approved visual references
- Window attachment decisions
- Reasoning conclusions from upstream stages

## Output (direct description, no longer bound to a Schema)

Describe the sizing derivation for each WindowContainer and the skeleton for each Layout in structured Markdown:

**Window sizing derivation (per window)**:

- form / unit basis (Planar derives width and height in dp; Volumetric must declare its volume basis);
- scene tier and official baseline (Planar 2D/productivity tasks start from 1280×720dp; auxiliary, media, and 3D tiers are adjusted separately per the methodology);
- simultaneously visible content (simultaneousContent);
- information topology (informationTopology);
- interaction density (interactionDensity);
- viewing conditions (viewingContext: posture, distance, duration, worldScale);
- clear-field-of-view check (core content 65°×40°, secondary content no larger than 85°×55°);
- readability/clickability lower bounds (56×56dp hit target, 12dp body text, width-limit / column strategy for long body text);
- attachment footprint (accessoryFootprint: the external footprint of TabBar / Toolbar / Subwindow / Augment is calculated separately);
- candidate sizes (at least 3, covering default / min / max) and the reason for the selection;
- default, minimum content size, optional maximum content size;
- aspect-ratio policy and resize behavior.

**Per Layout**: task relationships, data relationships, interaction frequency, spatial constraints, and rejected options.

## Quality Rules

- Sizes must first be determined as a baseline per the PICO methodology, then calibrated by content and task;
- The default baseline for Planar 2D/productivity tasks is 1280×720dp; Planar width and height must fall within 320×180dp ~ 2700×1800dp, with depth fixed at 640dp;
- The external footprint of TabBar / Toolbar / Subwindow / Augment must be calculated separately;
- Small sizes are degraded via reflow, collapsing, layering, or internal scrolling; you cannot shrink text and targets as a whole;
- 16:9 is not required; lists, timelines, comparison canvases, reading, and consoles can produce different aspect ratios.

## Prohibitions

- using 1600×900 as an unfounded fallback;
- treating 1280×720 as the final fixed size for all Planar projects without doing scene, field-of-view, and content calibration;
- describing project-level derivations as PICO official hard rules;
- hiding assumptions, exception states, or failure paths.
