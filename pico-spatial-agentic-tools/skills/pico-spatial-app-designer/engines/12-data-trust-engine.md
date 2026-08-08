# Data Trust Engine

## Responsibilities

Define loading / fresh / aging / stale / offline / partial / conflicting / permission_denied / error, along with source, update time, and trustworthiness.

Role: `spatial_design_system_designer`. Reasoning conclusions are recorded in [`roles/review-templates/visual-system-spec.md`](../roles/review-templates/visual-system-spec.md) (Section 7, Data Display and Semantic Contract).

## Inputs

- Domain model, design-system facts
- Reasoning conclusions from upstream stages

## Output (direct description, no longer bound to a Schema)

Directly describe the data-trust and display contract in structured Markdown:

- **data states**: cover the relevant ones among loading / fresh / aging / stale / offline / partial / conflicting / permission_denied / error as the project needs; real-time data scenarios should cover them comprehensively and explain source, update time, and trustworthiness.
- **trust policy**: such as freshness always visible, stale never disguised as real-time, alerts always carrying source (declared as this project needs).
- **display-only paths displayOnlyPaths**: paths used only for display, not participating in semantic coloring; sample values must be end-user-readable text, and it is prohibited to leak database enum names, sensor codenames, or internal identifiers.
- **semantic enum paths semanticEnumPaths**: paths participating in coloring / state judgment / alert level / trend, each mapped to the `aliases` and `label` of the visual grammar's color semantics, guaranteeing that the visible UI displays a human-readable label.
- **display formatting rules formattingRules**: formatting rules for numbers, time, units, null values, permission errors, stale/offline, etc., declaring the input path, output format, fallback, and the applicable data states.

Any data meaning, display format, enum translation, or fallback behavior that affects the implementation result must be written into the structured fields above, not only described in narrative or notes.

## Prohibitions

- bypassing upstream stages;
- describing project-level derivations as PICO official hard rules;
- manufacturing a "sense of space" by adding floating windows;
- hiding assumptions, exception states, or failure paths.
