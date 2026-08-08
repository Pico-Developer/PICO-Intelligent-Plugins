# Screen Graph Engine

## Responsibilities

Generate states and transitions with unique IDs; every state must have a container, focus, entry, exit, exception, and return path.

Role: `interaction_xr_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 10, State Graph / Transition Graph).

## Inputs

- Experience and Container Architecture, Task / Decision Model
- Reasoning conclusions from upstream stages

## Output (direct description, no longer bound to a Schema)

Directly describe the state graph in structured Markdown. For each state, give:

- container, primary focus, main task, decision output;
- layout, components, data dependencies;
- entry, exit / continue, exception-state recovery, return strategy;
- state names come from the project's semantics and do not mechanically copy case-study states.

Each transition explicitly declares:

- **trigger event**: a stable ID of a user / system / data event (e.g. `user.confirmSelection`, `data.refreshFailed`);
- **executed action**: the action ID or sequence executed before entering the next state (e.g. `openDetailPanel`, `requestRetry`), which must be mappable to the interaction spec;
- **whether explicit confirmation is required**: yes when Stage entry, dangerous operations, exit, or a critical decision is involved.

A Stage state must have an entry transition that requires explicit confirmation and a stable exit path; ordinary states also need an exit / continue path. All implementation-critical state-switching information lands in structured fields, not only describing trigger conditions, user actions, or side effects in natural language.

## Prohibitions

- bypassing upstream stages;
- describing project-level derivations as PICO official hard rules;
- manufacturing a "sense of space" by adding floating windows;
- hiding assumptions, exception states, or failure paths.
