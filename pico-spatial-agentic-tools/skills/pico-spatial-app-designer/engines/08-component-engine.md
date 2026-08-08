# Component Synthesis Engine

## Responsibilities

Derive components from the selected concept's tasks, data, interactions, and window default / min / max. Domain knowledge only provides terminology and rules; it is not a mandatory catalog. Every core component records `derivedFromTasks`, `derivedFromData`, purpose, structured anatomy, data bindings, variants, states, layout role, and accessibility behavior.

Role: `spatial_design_system_designer`. Reasoning conclusions are recorded in [`roles/review-templates/visual-system-spec.md`](../roles/review-templates/visual-system-spec.md) (Section 5, Component Definition Spec · Structured Anatomy).

## Inputs

- Composition synthesis, state graph, PICO methodology window sizing (default / min / max, content area, reflow), approved visual references
- Task / Decision Model, domain model, research evidence
- Reasoning conclusions from upstream stages

## Output (direct description, no longer bound to a Schema)

Directly describe each component in structured Markdown; prose-style definitions are prohibited:

- **Traceability**: `derivedFromTasks` (task IDs must genuinely exist in the Task / Decision Model and cannot be dangling references), `derivedFromData` (the associated data entities).
- **Structured anatomy anatomy.layout**: describe the internal structure with a Grid / region split, declaring the role and content of each region, and pair it with `sizing` to give proportions or fixed size tiers; the component's outer frame must not exceed the content area under its owning window's default / min / max, and Compact / Constrained must correspond to the reflow of interaction §9; do not use vague narratives like "a card shows information".
- **label**: a human-readable title, text that will be visible on the future UI; it cannot be a raw component type, layer name, or internal identifier.
- **runtimeRole**: a stable implementation role (such as `primaryMetric`, `decisionList`, `statusBadge`, `control`, `navigation`, `detailPanel`, or a project-specific role) that describes behavior rather than visual decoration.
- **renderSpec.elements[]**: ordered visible elements, each containing a stable `id`, a visible `label` (if applicable), an element `type`, an optional `bind`, and the state / semantic role required for implementation.
- **dataBindings[]**: each runtime data dependency, indicating the source path, target element / property, fallback behavior, and whether the value is purely for display or semantically driven.
- **variants / states**: primary components (`priority: primary`, or domain components whose layout role is primary focus / key subject) should cover enough real business variants and states so that density, exceptions, and edge cases can be consumed by implementers.
- **domain depth**: domain-specialized components should embody workflows and decision variables, avoiding a situation where generic components take up too high a proportion and degrade into a templated interface.

Implementation-critical component information must be carried by the structured fields above. Do not rely on `purpose`, comments, or prose to convey visible labels, roles, visible elements, or data bindings.

## Incompressible Structure Contract (component-finalization blocking condition)

> **The complete structure block is a delivery contract, not a writing suggestion.** Information "appearing semantically" does not equal structural compliance. Regardless of the number of components, domain complexity, context length, or delivery deadline, every core component must retain an independent, isomorphic, locatable complete structure block; do not merge fields, collapse tables, or replace component-specific facts with a shared paragraph just to shorten the document.

### The fixed structure for each core component

| Order | Required Structure | Minimum Content Requirement | Prohibited Compressed Form |
|---|---|---|---|
| 1 | Base field table | `derivedFromTasks`, `derivedFromData`, `purpose`, `layoutRole`, `priority`, `runtimeRole` filled in on separate lines | merging `purpose / layoutRole / priority` onto one line |
| 2 | `Anatomy · Layout (anatomy.layout)` | ASCII structure diagram + Grid / spatial region definition + alignment and spacing | writing only a single line `Grid: rows...` |
| 3 | `Anatomy · Sizing (sizing)` | independent table; at least Regular + Compact, or an explanation that a tier is not applicable and why; each tier must declare the applicable window tier (default / min / max or Large / Compact / Constrained) and whether it falls within the content area | stuffing sizing into the base fields or metrics |
| 4 | `Anatomy · Internal Metrics (metrics)` | background, radius, padding, gap, stroke, icon/text, hitTarget on separate lines; write `N/A + reason` for non-applicable items | stringing them into one line with semicolons |
| 5 | `Render Elements renderSpec.elements[]` | one line per visible element, including a stable id, label, type, bind, and state / semantic role | an untitled element list or comma-separated enumeration |
| 6 | `Data Bindings dataBindings[]` | one line per source path, including target property, fallback, display-only / semantic | a `bindings: a/b/c` path string or "same as above" |
| 7 | `Variants variants` | list the variants and their structural / behavioral differences; write `none + reason` if there are no variants | omission |
| 8 | `States states` | a component-specific state table, including trigger, visual parameters, size changes, motion, accessibility, stacking precedence | a one-line state enumeration; referencing only a shared state table |

### Adaptation Rules

- **2D components within a WindowContainer**: `anatomy.layout` uses a row/column Grid and solid / dashed ASCII diagrams.
- **Component sizes constrained by the window**: a component's `sizing` must reference the default / min / max or Large / Compact / Constrained tier of its owning WindowContainer; the component's width/height, internal padding/gap, and hitTarget must hold within the corresponding window's content area. If a component cannot maintain a 56×56dp hit target or 12dp body text under min / Constrained, it should collapse, change columns, move to a Sheet/Dialog, or be marked as not applicable for that tier; do not scale text and targets as a whole.
- **Stage / 3D / world-space components**: still retain the exact same 8-section headings; `anatomy.layout` instead uses world anchors, local coordinates, orientation, metric (meter) ranges, and a spatial-region ASCII diagram. The spatial expression differs, but the structure contract does not change.
- **Assembly components**: the assembly-level complete block cannot replace the complete blocks of complex subcomponents. Wherever a subcomponent has an independent task, interaction, data binding, or real runtime substate, it must be split out into an independent complete block.
- **Shared specs**: shared state tables, shared metrics, and Design Tokens can only be referenced by components, not replace component-specific tables. Component tables must clearly state the referenced items and project-specific differences.
- **Length pressure**: reduce non-core components, split delivery batches, or clearly mark "incomplete"; do not pass off single-line compression as complete delivery.

### Component Structure Integrity Checklist

After all components are defined, the structure checklist must be filled in first, before entering coverage reconciliation. If any core component has any column marked "no" or lacks a corresponding section anchor, the design-system stage must not be marked complete, and the design-system review must return `block`.

| Core Component | Base fields on separate lines | anatomy.layout | sizing | metrics | renderSpec | dataBindings | variants | states + stacking precedence | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| | yes / no | yes / no | yes / no | yes / no | yes / no | yes / no | yes / no | yes / no | pass / block |

## Coverage Reconciliation (mandatory self-check before component finalization)

> Pure-reasoning-driven with no Schema gate, coverage verification relies entirely on actively completing this step. After all components have been anatomized and before entering the design-system review, you must fill in the following three reconciliation tables item by item and land them at the end of Section 5 of [`visual-system-spec.md`](../roles/review-templates/visual-system-spec.md). Purpose: to plug the two kinds of reasoning blind spots—"declared upstream, not caught by a component" (coverage hole) and "an actionable item treated as read-only" (granularity loss).

**Judgment rule**: if any row of the three tables has its "landing / gap disposition" column empty, or is marked "not presented" without giving a reason, it is judged a **coverage gap**—you must add a component / add an interaction / add a substate, or explicitly write "intentionally not presented + reason" (for example, domain evidence indicates the data has no decision value for the current task). Do not leave it blank and skip.

### Table A · Data Entity → Component Binding Reconciliation (guards against coverage holes)

Check item by item whether **each data entity / decision variable** declared by the UXR domain model (including timeliness fields such as buffer / network / freshness state) is caught by a component's `dataBinding`.

| Data Entity / Decision Variable (source: domain model) | Timeliness | Catching Component.dataBinding | Presentation / Semantic Method | Gap Disposition (add binding / intentionally not presented + reason) |
|---|---|---|---|---|

### Table B · Task Decision Output → Component Interaction Reconciliation (guards against granularity loss)

For **each "decision output"** in the Task / Decision Model, judge item by item: is it a **read-only display** or an **actionable decision**? Everything actionable must have a component catching its interaction behavior (`renderSpec` element + interaction); you cannot draw only a read-only primitive.

| Task ID · Decision Output | Read-only / Actionable | Catching Component + Interaction Behavior | Gap Disposition |
|---|---|---|---|

### Table C · Primary Component Substate Enumeration Reconciliation (guards against insufficient substates)

Primary components (`priority: primary`, or whose layout role is primary focus) must enumerate their **internal subcomponents** and **real runtime substates** (covering at least: loading / buffering / dragging or editing / empty / error / boundary disabled). Each substate must have a corresponding rendering primitive and data binding; do not stop at the assembly-level states.

| Primary Component → Subcomponent | Runtime Substate (enumerated) | Corresponding Rendering Primitive | Data Binding |
|---|---|---|---|

## Prohibitions

- copying a fixed component catalog wholesale from a domain pack or case study;
- describing internal structure with prose, evading `anatomy.layout` + `sizing`;
- defining component sizes on your own, divorced from the owning WindowContainer's default / min / max;
- letting generic components take up too high a proportion and masking domain depth;
- describing project-level derivations as PICO official hard rules;
- hiding assumptions, exception states, or failure paths.
