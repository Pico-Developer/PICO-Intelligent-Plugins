---
name: pico-spatial-app-designer
description: Use when the user asks to design, review, repair, or produce a PICO spatial app design package from requirements, prior design facts, or delivery specs, or when an upstream app-generation workflow needs a no-visual requirement converted into an accepted design package before code generation. NOT for generating Android runtime code, scaffolding projects, or device validation.
license: 'Apache-2.0'
---

# PICO Spatial App Designer

## 0. When to Use

Applicable when:

- The user asks to derive a PICO spatial App design from natural-language requirements;
- The user asks to produce human-collaboration-facing role-based design documents and a Web validation prototype;
- The user asks to review, repair, or improve a spatial App's design solution or delivery spec.

Not applicable for:

- Generating an Android / PICO runtime project;
- Building a standalone website or generic browser demo detached from design facts;
- Performing real-device, emulator, device-evidence, or dual-end consistency validation;
- Migrating an existing 2D Android App to the Spatial SDK.

Routing note: when `spatial-design-to-app` receives a no-visual app-generation request (`intent_only`, `product_doc`, or text-only `hybrid`), it may invoke this skill first to produce the accepted design package. This skill still stops at role-based design documents and `preview.html`; downstream app artifacts, container/window enum decisions, Android code, build, install, launch, and device evidence remain owned by `spatial-design-to-app` after its bridge consumes the accepted package.

## 1. Core Definitions

What this Skill reuses is the **design workflow, reasoning framework, quality standards, and validation mechanism**, not the layout, component combinations, state structure, visual style, or preview template of any case.

This version is a **pure-LLM-reasoning-driven** refactor: there are no longer any deterministic Python gates, JSON Schema parameter-passing layer, or validator error codes. Reasoning information is passed only through the **role Markdown** (`roles/review-templates/*.md`) corresponding to each workflow step; the "outputs" declared by each engine are described directly as structured Markdown and are no longer bound to a Schema format.

Every new requirement must go through the following high-level stage summary from scratch; the complete execution order, stage count, roles, and inputs/outputs are governed by [`workflow.json`](./workflow.json). Consecutive reasoning by the same professional role writing into the same role document is merged into one stage (which may reference multiple engines), for a total of 17 stages:

1. Intent Interpretation (intent)
2. Research (domain research + competitive benchmark + domain model)
3. Project Quality Contract (quality contract)
4. Problem & Evidence Review (independent review gate)
5. Task and Decision Modeling (task / decision model)
6. Concept Formation (spatial value + design hypotheses + concept selection)
7. Spatial Concept Review (independent review gate)
8. Visual Direction (visual direction candidates + approved visual reference)
9. Spatial Structure (experience / container architecture + window attachment + window sizing + state graph)
10. Composition Synthesis (layout synthesis)
11. Design System (layout / component / visual language / interaction / motion / data trust)
12. Design System Review (independent review gate)
13. Web Prototype (single-file preview.html)
14. Preview Review (prototype QA review gate)
15. Delivery Self-check (process / originality audit + Design Critic, merged)
16. Graph Patch (bounded local patch)
17. Delivery Readiness Review (delivery readiness gate)

Generating interfaces directly from the user Prompt is prohibited; selecting a layout template from a case and then swapping the content is prohibited. A new project must not derive layout, state, components, or visual direction from cases, templates, or historical assets.

## 2. Definition of High Quality

High quality is not "all fields filled in" or "no rule errors", but rather:

- The user task is transformed into a clear decision result;
- Spatialization is driven by direction, distance, scale, position, motion, collaboration, or simulation value;
- The container and experience hierarchy are independently derived from the current requirement;
- The layout is synthesized from task relationships, data relationships, operation frequency, and the central comfort zone;
- Components are generated from domain semantics, data, and interaction needs, rather than picked from a fixed catalog;
- The visual language is derived from project semantics, environment, and risk state;
- At least three substantially different design hypotheses are compared;
- Every key decision can be traced to a requirement, rule, evidence, or assumption;
- The final output is human-collaboration-facing role-based design documents + a Web validation prototype;
- Independent review checks task depth, design tradeoffs, original derivation, and design deliverability.

## 3. Mandatory Workflow

> The following subsections are organized in the order of the 17 stages in [`workflow.json`](./workflow.json); if a reasoning stage references multiple engines, the focus of each engine is listed as sub-items, but they still belong to the same stage and are written into the same role document. The engine numbering stays unchanged (`engines/*.md`); only the stage grouping is merged.

### Stage 1 — Intent Interpretation (`intent`)

Engine [`01-intent-interpreter.md`](./engines/01-intent-interpreter.md). Extract domain, sub-domain, users, context, posture, frequency, duration, tasks, decisions, risks, data, AI, sensors, permissions, and collaboration. All missing information is written into the assumptions list, with confidence, impact, and validation plan. Carried in [`pm-requirement-spec.md`](./roles/review-templates/pm-requirement-spec.md).

### Stage 2 — Research (`research`)

The same `research_analyst` role consecutively completes domain research, competitive benchmark, and domain modeling, writing into [`uxr-research-report.md`](./roles/review-templates/uxr-research-report.md). Research must be grounded in the current requirement, user materials, and traceable evidence, uniformly covering the five categories of market / user / domain / platform / safety (write explicit evidence gaps where evidence is missing):

- **Domain research** ([`02a-domain-research-engine.md`](./engines/02a-domain-research-engine.md), corresponding to `user` / `domain` / `platform` / `safety` evidence): retrieve and organize the professional knowledge truly relevant to the current requirement—domain workflows, decision variables, data entities and timeliness, professional risks, and user mental models.
- **Competitive benchmark** (the competitive-benchmark hard requirement of [`02a-domain-research-engine.md`](./engines/02a-domain-research-engine.md), corresponding to `market` evidence): **analyze at least three** similar / adjacent products (when there are fewer than three XR competitors, 2D same-task competitors may be included with platform differences noted), summarizing each across multiple dimensions—**functional needs, interaction experience, visual experience, spatial capability usage**—distilling the "strengths worth absorbing" and the "anti-patterns to avoid", and aggregating them into **our differentiation opportunities** based on PICO spatial capabilities. Absorption only takes effect at the requirement / opportunity level; do not copy competitors' layouts / state graphs / components / visuals (constrained by the §4 originality hard rules). Carried in [`uxr-research-report.md`](./roles/review-templates/uxr-research-report.md) §3A.
  - **Value that runs through downstream**: the §3A competitive benchmark is not a one-time archive; it must be explicitly consumed at each stage—Stage 3 quality contract anchors the differentiation goal to "our differentiation opportunities"; Stage 5 task model uses the functional column to verify coverage completeness; Stage 6 spatial value uses the spatial capability column against the 2D counterfactual to find differentiated space; Stage 6 concept selection's market-differentiation `evidenceRefs` reference §3A entries; Stage 8 visual direction uses the visual column for differentiation / dashboardization-risk comparison (observe only, do not reuse); Stage 15 delivery self-check verifies whether the differentiation opportunities are truly realized and that absorption has not overstepped.
- **Domain model** ([`02-domain-engine.md`](./engines/02-domain-engine.md)): precipitate the research into a structured domain model—workflows, decision variables, data entities and timeliness, professional risks, anti-patterns—as input to the quality contract and task model.

### Stage 3 — Project Quality Contract (`quality_contract`)

Engine [`00-quality-contract-engine.md`](./engines/00-quality-contract-engine.md). Define the quality contract based on the current requirement (and the completed intent and research), rather than selecting a case template. Outputs: the results the user must accomplish, success time / efficiency criteria, risks and must-not-fail items, hard constraints of the PICO platform and spatial design norms, domain evidence needs, design originality requirements, and the design and readability acceptance plan. Carried in [`pm-requirement-spec.md`](./roles/review-templates/pm-requirement-spec.md).

### Stage 4 — Problem & Evidence Review (`problem_evidence_review`, review gate)

The independent `evidence_integrity_reviewer` verifies sources, assumptions, evidence gaps, risks, and contract consistency, outputting findings, impact, evidence, and patch goals, written into [`design-critique-report.md`](./roles/review-templates/design-critique-report.md).

### Stage 5 — Task and Decision Model (`task_model`)

Engine [`03-task-decision-engine.md`](./engines/03-task-decision-engine.md). Establish the task graph and decision graph: who, in what scenario, based on what information, makes what decision; what are the consequences of a wrong decision; how tasks depend on one another. Carried in [`interaction-spatial-spec.md`](./roles/review-templates/interaction-spatial-spec.md).

### Stage 6 — Concept Formation (`concept_formation`)

The same `interaction_xr_designer` role consecutively completes spatial value justification, design hypotheses, and concept selection, writing into [`interaction-spatial-spec.md`](./roles/review-templates/interaction-spatial-spec.md):

- **Spatial value** ([`03-spatial-value-engine.md`](./engines/03-spatial-value-engine.md)): judge item by item—direction, distance, scale, depth, position, motion, body, collaboration, simulation, and change over time—and provide the 2D counterfactual at the same time. When spatial value is insufficient, using Stage is prohibited.
- **Design hypotheses** ([`03a-design-hypothesis-engine.md`](./engines/03a-design-hypothesis-engine.md)): generate at least three substantially different design hypotheses, differing in the information organization model, degree of spatialization, container structure, user path, primary interaction, risk, and engineering cost. Do not just generate three different color schemes.
- **Concept selection** ([`03b-concept-selection-engine.md`](./engines/03b-concept-selection-engine.md)): use a decision matrix to compare each hypothesis—task efficiency, spatial value, PICO comfort, domain depth, risk, accessibility, engineering feasibility, and distinctiveness. Record the unselected options and the reasons for rejection, and provide a qualitative market-differentiation justification.

### Stage 7 — Spatial Concept Review (`spatial_concept_review`, review gate)

The independent `spatial_concept_reviewer` verifies task decisions, spatial necessity, the 2D counterfactual, hypothesis diversity, and selection evidence, outputting findings and patch goals, written into [`design-critique-report.md`](./roles/review-templates/design-critique-report.md).

### Stage 8 — Visual Direction (`visual_direction`)

Engine [`03c-visual-direction-engine.md`](./engines/03c-visual-direction-engine.md). Before entering architecture, 2–3 spatial visual directions must be generated, comparing their first view, container relationships, depth layering, information hierarchy, interaction cues, spatial value, and failure risk. The selected direction becomes the approved visual reference, approved by human confirmation or a structured design-effect review; do not treat logical verification as aesthetic approval. Carried in [`visual-system-spec.md`](./roles/review-templates/visual-system-spec.md).

### Stage 9 — Spatial Structure (`spatial_structure`)

The same `interaction_xr_designer` role consecutively derives the experience and container architecture, window attachment, window sizing, and state graph, writing into [`interaction-spatial-spec.md`](./roles/review-templates/interaction-spatial-spec.md):

- **Experience and container architecture** ([`04-experience-engine.md`](./engines/04-experience-engine.md), [`05-container-engine.md`](./engines/05-container-engine.md)): independently derive the experience hierarchy based on the selected solution. Glance / Explore / Immerse are just available vocabulary, not a mandatory template. Define the WindowContainer (its form Planar / Volumetric must be set), and the responsibilities, host, entry/exit, and fallback of the Stage and window attachments. No project may add a Toolbar by default; the window attachment decision matrix must be completed first, and the conclusion is allowed to be None.
- **Window attachment selection** ([`05a-window-attachment-engine.md`](./engines/05a-window-attachment-engine.md)): for each "auxiliary need outside or beside the window", first determine its **placement mode** (Docked / Wraparound / in-window), then select the corresponding attachment or None. The core distinguishing axis of an attachment is the placement mode, not size; a Subwindow's height is locked to fill the host. When deciding, you must explicitly compare `InlineControl` (place in situ) with `None` (add no attachment). Do not treat a Toolbar as navigation, a TabBar as a tool area, or an Augment as a primary content container.
- **PICO-methodology window sizing** ([`07b-window-sizing-engine.md`](./engines/07b-window-sizing-engine.md), required reading [`knowledge/spatial-window-sizing-methodology.md`](./knowledge/spatial-window-sizing-methodology.md)): window size must be determined per the PICO spatial window-sizing methodology, setting the default size and the resizable range. Each WindowContainer must first distinguish Planar / Volumetric and the unit basis, then determine the scene tier (auxiliary / HUD, productivity / main content, media / immersion, spatial-anchored / 3D), the official baseline, viewing conditions, worldScale, default distance, clear-field-of-view verification (core 65°×40° / secondary 85°×55°), hit-target / font-size lower limits, attachment occupancy, default / min / max, and the Large / Compact / Constrained reflow strategy. A Planar 2D task is allowed to use 1280×720dp as the official default baseline, but it must be calibrated by scene, content, and field of view; do not treat 1280×720 as the final fixed size for all projects.
- **State graph** ([`06-screen-graph-engine.md`](./engines/06-screen-graph-engine.md)): each state must have a primary task, decision output, primary focus, layout, components, data dependencies, entry/exit, back, and exception states; each transition declares the trigger event, the action performed, and whether explicit confirmation is needed. State naming must come from project semantics and must not mechanically copy case states.

### Stage 10 — Composition Synthesis (`composition_synthesis`)

Engine [`07a-composition-engine.md`](./engines/07a-composition-engine.md). Synthesize the layout from task relationships, data relationships, interaction frequency, and field-of-view constraints. Each layout records derivation evidence (task / data relationships, interaction frequency, spatial constraints), single primary focus, regions, density ceiling, responsive transformations, and rejected options. Do not select a template from a case layout ID.

### Stage 11 — Design System (`design_system`)

The same `spatial_design_system_designer` role consecutively precipitates layout, components, visual language, interaction, motion, and data trust, writing across two documents—component anatomy / Design Tokens / materials / data-presentation semantic contract go into [`visual-system-spec.md`](./roles/review-templates/visual-system-spec.md), and layout skeleton / eye-hand interaction / motion spec go into [`interaction-spatial-spec.md`](./roles/review-templates/interaction-spatial-spec.md):

- **Layout** ([`07-layout-engine.md`](./engines/07-layout-engine.md)): turn the synthesized layout into implementable regions, grid, and density rules.
- **Component synthesis** ([`08-component-engine.md`](./engines/08-component-engine.md)): components are generated from task, information, and interaction needs. Each core component must replicate the same **incompressible complete structure block**: base fields on separate lines, `anatomy.layout` (ASCII + Grid / world-space geometry), an independent `sizing` table, an item-by-item `metrics` table, `renderSpec.elements[]`, `dataBindings[]`, `variants`, a component-specific `states` table, and stacking precedence. A component's `sizing` / `metrics` must reference the default / min / max or Large / Compact / Constrained tier of the WindowContainer it belongs to, and fall into the corresponding content area. Do not merge fields, or change them into path strings / state enums, because a component is simple, the components are numerous, or under context or length pressure; a common state table also cannot replace a component-specific table; Stage / 3D components only change the spatial expression, not the structure. Domain terms may only serve as a semantic reference, not as a catalog that must be reused. All components first pass the **structural completeness checklist**, then complete **coverage reconciliation** (table A data entity → component binding, table B decision output → interaction, table C exhaustive enumeration of primary component sub-states).
- **Visual language** ([`09-visual-engine.md`](./engines/09-visual-engine.md)): the visual system must be derived from project semantics—brand personality, environment, emotion, risk, content density, physical metaphor, and domain symbols. `visualSystem` is the source of style facts consumed verbatim by the downstream implementer; it must be expressed with structured fields (`typography`, `colorSemantics` color + shape dual channel, `materials`, `tokens`) and record at least two rejected visual directions. Different domains cannot just swap colors.
- **Interaction / motion / data trust** ([`10-interaction-engine.md`](./engines/10-interaction-engine.md), [`11-motion-engine.md`](./engines/11-motion-engine.md), [`12-data-trust-engine.md`](./engines/12-data-trust-engine.md)): define gaze, pinch, drag / manipulate, controller fallback, system back, error recovery, high-risk confirmation, Reduce Motion, performance fallback, as well as data source, freshness, conflict, and offline. Data presentation follows the presentation semantic contract: pure-presentation paths fill in human-readable copy, semantic-enum paths are translated via `colorSemantics.label`, and machine enums are not echoed back.

### Stage 12 — Design System Review (`design_system_review`, review gate)

The independent `design_coherence_reviewer` first verifies the incompressible structure block component by component; if any core component lacks base fields, `anatomy.layout`, `sizing`, `metrics`, `renderSpec`, `dataBindings`, `variants`, or a specific `states`, the review must `block`, and this cannot be offset by an overall quality score, common norms, or coverage reconciliation. After all structure passes, then verify visual, architecture, state, layout, component, interaction, accessibility, and data consistency, outputting findings and patch goals, written into [`design-critique-report.md`](./roles/review-templates/design-critique-report.md).

### Stage 13 — Web Prototype (`preview_build`)

Engine [`14-prototype-engine.md`](./engines/14-prototype-engine.md). `prototype_frontend_engineer` first passes the Preview input readiness gate; if any component structure or implementation fact is incomplete it `block`s and must not guess-generate. After passing, first fill in the **Preview Coverage Manifest (declarative denominator)** in [`preview-qa-report.md`](./roles/review-templates/preview-qa-report.md), listing item by item from `interaction-spatial-spec.md` / `visual-system-spec.md` the states, transitions, `renderSpec.elements[]`, `dataBindings[]`, variants, component-specific states, responsive window tiers (Large / Compact / Constrained corresponding to default / min / max) / Reduce Motion, as the implementation input list for generating `preview.html`.

After generating `preview.html`, you must fill in item by item the five implementation mapping tables in the preview report: state/transition, `renderSpec.elements[]` → DOM, `dataBindings[]` normal value/fallback, variants/component-specific states, responsive window tier/Reduce Motion. The coverage denominator comes from the design-fact entries of the Coverage Manifest; a component or state name appearing does not count as implemented. The Preview must have a triggerable state-machine structure (state table, transition table, state rendering, normal/fallback/error sample data, high-risk confirmation Dialog), and must not be just a static display page. `mustNotProduce`: Android / PICO runtime, device evidence, parity conclusions.

### Stage 14 — Preview Review (`preview_review`, review gate)

`prototype_qa_reviewer` independently rebuilds the item-by-item denominator and verifies the five implementation mapping tables, and must not copy the generation side's conclusions. If any core element, actionable binding, fallback, variant, component-specific state, exception/safety/stable-exit path, or responsive window-tier scenario is missing, the review must `block`, and this cannot be offset by a percentage, an overall score, or "the Web only validates logic".

This stage introduces no scripts or deterministic validator; preventing fake coverage relies on the **Markdown declarative checklist** in [`preview-qa-report.md`](./roles/review-templates/preview-qa-report.md). QA must declare and back-check item by item: whether the Coverage Manifest is complete, whether each state / transition has a trigger and a visible result, whether each `renderSpec.elements[]` has a stable selector, whether each `dataBindings[]` has normal/fallback/error evidence, whether each variant / component-specific state is triggerable, whether responsive window tiers / Reduce Motion have structural assertions, and whether high-risk transitions are blocked by a Dialog. If any row of the checklist lacks a source fact, selector, trigger step, expected/actual result, or verdict, then `block`. Tolerance is limited to Web logical relationships; device validation is uniformly marked `not_performed`, recorded in [`preview-qa-report.md`](./roles/review-templates/preview-qa-report.md).

### Stage 15 — Delivery Self-check (`delivery_self_review`, review gate)

The same review stage merges the process audit, originality audit, and Design Critic ([`process-audit-critic.md`](./critics/process-audit-critic.md), [`originality-critic.md`](./critics/originality-critic.md), [`design-critic.md`](./critics/design-critic.md)): the process audit checks whether the full independent reasoning was truly gone through; the originality audit checks whether case structure was copied; the Design Critic checks task, spatial, domain, information, comfort, trust, and engineering quality. All three output scores, evidence, gaps, and verdicts, written into [`design-critique-report.md`](./roles/review-templates/design-critique-report.md), as input to the delivery readiness review.

### Stage 16 — Graph Patch (`patch`)

Only local repair, not rewriting the entire design. At most four rounds. Every Patch must correspond to a problem, a target node, and an expected improvement. Any change to state/transition, layout/responsive, component anatomy/sizing/metrics, `renderSpec`, `dataBindings`/fallback, variants, component states, tokens/materials, or interaction/Reduce Motion is a change to a Preview implementation input fact; regardless of whether the product semantics change, the old preview and old QA are immediately invalidated, and `preview_build`, `preview_review`, `delivery_self_review` must be re-run per [`workflow.json`](./workflow.json).

### Stage 17 — Delivery Readiness Review (`delivery_readiness_review`, review gate)

The independent delivery readiness review role checks the complete design and prototype package, the review verdicts of each gate, unclosed findings, and limitations, and gives a delivery recommendation. When all required review gates are `pass` and there is no active blocking finding, the delivery status can reach `ready_for_design_delivery`. This status does not mean downstream app generation, PICO runtime, or device validation is ready.

## 3a. Orchestration Contract (who drives these Stages)

This Skill **deliberately provides no Python orchestrator**, to stay model-agnostic: **the host LLM is the orchestrator**. The machine-readable version of the contract is in the `orchestration` field of [`workflow.json`](./workflow.json).

1. **Sequential progression**: execute in the order of `stages` in `workflow.json`; each stage has only three forms—
   - **reasoning stage**: the host LLM reads that stage's `engine` / `engines` (`engines/*.md`, `critics/*.md`) to complete the reasoning, and writes the conclusions directly into the corresponding sections of the role Markdown pointed to by `documentedIn`;
   - **review stage**: an independent reviewer role, different from the generator, outputs findings, impact, evidence, and patch goals, written into the design critique report.
2. **Bounded patch loop**: the `patch` stage is fulfilled by the host—after each round changes design facts, the preview generation, preview review, and delivery self-check (including the process / originality audit and Design Critic) must be re-run per `orchestration.loop.postPatchRerunStages` (`preview_build`, `preview_review`, `delivery_self_review`), until the review and self-check pass or the `max_patch_rounds` (4) limit is reached; if the limit is reached and it still does not pass, it is judged a failure, and the standard must not be relaxed.
3. **Authority relationship**: there are no longer any deterministic Python gates. Pass or fail is jointly decided by the independent review verdicts, the process / originality self-check, and the delivery readiness review, recorded in [`design-critique-report.md`](./roles/review-templates/design-critique-report.md).
4. **Bounded output scope**: a design-fact-driven Web design validation prototype is allowed, but Android / PICO runtime, device evidence, and parity conclusions are prohibited.
5. **Frozen-reasoning change control**: when frozen reasoning (intent, quality contract, evidence, selected concept, approved visual reference) changes, the affected old reviews must be marked invalidated and the relevant stages re-run.
6. **Preview implementation-fact change control**: any change to an implementation input fact invalidates the old `preview.html`, Preview QA, and delivery self-check; the host must re-run Stage 13–15. It must not be skipped with the excuse of "semantics unchanged", "just filling in tables / expanding structure", or "the preview is not a runtime".
7. **Per-stage receipt**: the host must advance only one stage at a time. On entering a stage, first record `startedAt` in [`execution-trace.md`](./roles/review-templates/execution-trace.md); on completion, immediately record the inputs, the instruction read, the artifact written, the revision, and the verdict, before entering the next stage.
8. **No after-the-fact trace reconstruction**: you must not, after all files are generated, work backward from the final files and back-fill that the 17 stages are complete. Missing, simultaneously batch-back-filled, or order-contradictory receipts make Process Audit require a `block`.
9. **Artifact revision and invalidation propagation**: each artifact revision must be a positive integer, recorded by `execution-trace.md`. A review must reference the exact revision, and a derived output must declare its source revision. If any review references a superseded revision, a derived output does not declare its source revision, or an old record is still counted as `pass` after being marked invalidated, delivery readiness must `block`.
10. **No direct pass without a receipt**: a reasoning stage has no `pass` verdict, and can only record `completed / blocked` in a complete
    receipt; only a review stage may record
    `pass / changes_requested / block`. Writing pass first and supplying evidence later, or replacing per-stage receipts with an "all stages complete"
    summary, both make `designStatus=invalid`.
11. **Minimum Completeness Gate**: the six core
    documents PM, UXR, Interaction, Visual, Critique, and Preview must each pass their own `minimumCompletenessGate`. A section heading existing, a very long file, a
    table with one empty sample row, or a worker's self-reported completion do not count as passing; any gate failure means
    `designStatus=invalid`.
12. **Status can only be derived**: the `designStatus` priority is fixed as
    `invalid > review_blocked > changes_requested > ready_for_design_delivery > draft`.
    You must not fill in a target status first and then look for evidence for it.

## 3b. Role Governance and Review Separation of Duties

> **Professional roles are responsible for generation, independent roles are responsible for review, and the delivery status is derived from the review gates.**

- [`roles/role-contracts.json`](./roles/role-contracts.json) centrally defines every role's responsibilities, inputs, decision authority, prohibitions, allowed handoff targets, and allowed reviewers. The Role Contract bounds the allowed boundary; the actual Stage routing is governed by `workflow.json`.
- Each reasoning stage must declare a `primaryRole` and write the reasoning conclusions into the role document pointed to by `documentedIn`, leaving a role trace.
- The key review gates respectively check problem and evidence, spatial concept, design system, and delivery readiness.
- Preview / QA review is a mandatory Web-prototype-specific record: it must be provided by `prototype_qa_reviewer`, and `deviceValidation.status` must be `not_performed`.
- A reviewer can only output findings, impact, evidence, and patch goals, and must not directly rewrite the reviewed content.
- When frozen reasoning changes, a bounded Change Request must be used, and an invalidated review record must not be reused.

## 3c. Main-Thread Acceptance Gate

> The worker is responsible for producing outputs, and the main thread is responsible for receiving them. A worker self-reporting `pass` does not constitute delivery approval.

Before the main thread allows any downstream app generation, it must complete the following acceptance:

1. Actually read the final active revision of `review/execution-trace.md`,
   `review/design-critique-report.md`, and `review/preview-qa-report.md`; do not read only the worker summary;
2. Re-derive `designStatus` from the raw evidence, and check the timing, required fields,
   artifact revisions, and invalidation re-runs of the 17 stage receipts;
3. Check that each review stage has an independent `fresh_context / isolated_subagent` invocation,
   a non-empty `invocationId`, an exact `reviewedRevision`, and `evidenceRebuilt=yes`;
4. Check that the six core documents' Minimum Completeness Gate, component structure, Preview Manifest, five mapping tables, and
   QA independent-denominator reconciliation all pass;
5. In the "Main-Thread Acceptance Record" of `design-critique-report.md`, fill in the unique acceptance ID, evidence,
   re-derived status, blocking items, and time.

**Downstream-invocation hard rules:**

- `designStatus != ready_for_design_delivery`: entering app generation is prohibited;
- Main-Thread Acceptance Record missing: entering app generation is prohibited;
- Worker self-reporting ready, files complete, Preview openable, or overall score meeting the bar: none of these can replace the main-thread acceptance;
- Only when `designStatus=ready_for_design_delivery` and
  `downstreamAppGenerationAllowed=yes` may the main thread hand the design package to an external downstream skill.

## 4. Originality Hard Rules

Any one of the following is an immediate failure:

1. The originality declaration shows reuse of a fixed template;
2. A new project directly reuses a case's layout ID, state sequence, or component combination;
3. There are fewer than three design hypotheses;
4. The unselected options and reasons for rejection are not recorded;
5. The layout has no derivation evidence;
6. A core component has no task and data source;
7. The design result uses a generic Dashboard information architecture or a prefab domain template;
8. A fixed domain template or historical case structure is instantiated directly;
9. The quality score depends on visual similarity to a case;
10. Different requirements only swap copy, colors, or icons.

## 4A. Window Attachment and Sizing Hard Rules

Any one of the following is an immediate failure:

1. Adding a TabBar, Toolbar, Subwindow, SpatialPopup, Augment, Sheet/Dialog, or Coachmark without going through the window attachment decision matrix (including the explicit comparison with None / InlineControl);
2. Mechanically placing page / view navigation into a Toolbar, or mechanically placing tool commands into a TabBar;
3. Using an attachment to carry mismatched semantics, e.g. an Augment carrying primary navigation, a SpatialPopup carrying persistent information, or a Subwindow carrying a temporary menu;
4. All projects skipping the scene tier and field-of-view verification and directly using the same WindowContainer size or ratio;
5. A WindowContainer lacking the PICO methodology chain (content type → scene tier → official baseline → clear field of view → readable-clickable lower limits → default / min / max);
6. Falling back to 1600×900 when a size is missing, or treating 1280×720 as the final fixed size for all Planar projects;
7. Describing a Planar logical size as a PICO real-device physical size, or skipping the effect of worldScale / viewing distance on field-of-view occupancy;
8. Not declaring the Planar legal range (320×180dp ~ 2700×1800dp), depth 640dp, hit target 56×56dp, body text 12dp, and other readable-clickable lower limits;
9. Skipping the downstream implementation validation plan.

## 5. Quality Gate

There is no longer any deterministic Python scorer. Pass or fail is jointly decided by **the independent review verdicts + the process / originality self-check + the delivery readiness review**, recorded in [`design-critique-report.md`](./roles/review-templates/design-critique-report.md). The following dimensions and thresholds are a human-readable scoring skeleton, referencing [`knowledge/quality-rubric.json`](./knowledge/quality-rubric.json); reviewers must not set up their own scores:

- Process Audit = pass (whether it was truly derived independently)
- Requirements Traceability: key decisions are traceable
- Component Structure Fidelity = pass: the incompressible complete structure block and structural completeness checklist of each core component both pass; any missing segment means block, not participating in overall-score offsetting
- Preview Input Readiness = pass: design system review, state/transition, the component 8-segment structure, renderSpec, dataBindings/fallback, variants/states, responsive/motion, and visual language are all implementable
- Preview Implementation Fidelity = pass: the Preview Coverage Manifest, the Markdown declarative checklist, and the five implementation mapping tables are all independently verified item by item to be 100%; any core implementation fact missing, or any declarative-checklist row lacking evidence or a verdict, means block, not participating in overall-score offsetting
- Execution Trace Fidelity = pass: the 17 stage receipts are each filled in promptly item by item, with complete required fields,
  continuous revisions, and no after-the-fact reconstruction; missing any one means `designStatus=invalid`
- Independent Review Evidence = pass: all review stages have an independent invocation and rebuild
  evidence; missing any one means `designStatus=review_blocked`
- Core Document Minimum Completeness = pass: the minimum structure/content thresholds of the six core documents all pass;
  any failure means `designStatus=invalid`
- Host Acceptance = pass: the main thread has re-derived the status from the raw evidence and recorded the acceptance; when missing, downstream
  app generation is prohibited
- At least 3 design hypotheses
- The Selected Concept has a complete decision matrix and rejection reasons
- Task Completion ≥ 17/20
- PICO Alignment ≥ 13/15
- Domain Depth ≥ 13/15
- Safety and Comfort ≥ 14/15
- Information Hierarchy ≥ 9/10
- Originality Audit = pass
- Design-effect review = pass (human confirmation or structured review record)

## 6. Outputs

The human-collaboration-facing delivery has two layers:

1. **Role-based reasoning documents** ([`roles/review-templates/*.md`](./roles/review-templates/index.md)): `index.md` for navigation, plus the six role documents—PM requirement spec, UXR research report, interaction / spatial spec, visual system spec, design critique report, and preview / QA report. Each document is populated with facts by the corresponding professional role during the reasoning stage, and is the single carrying layer of design facts.
2. **Web validation prototype** `preview.html`: a single self-contained prototype, with scope fixed to `web_design_validation_only`.

No runnable app project, device evidence, or dual-end consistency report is generated. Passing the preview does not mean PICO real-device comfort, occlusion, fatigue, input hit, physical size, or performance has been validated.

### 6A. Design-Stage Terminology Boundary

- Container facts must use PICO design terminology: Shared Space / Full Space, WindowContainer Planar / Volumetric, Stage Mixed / Progressive / Full.
- Downstream scaffolding or app-generation enums such as `ON_PLAIN`, `IN_VOLUME`, `STAGE_MIXED`, `single_panel`, `window_plus_subwindow` must not serve as design facts.
- After the design is delivery-ready, a downstream skill may establish an independent adapter to convert the delivered Markdown facts into its implementation input; the adapter's output must not be written back into the design package or be treated as this Skill's output.
- This Skill is prohibited from producing `design-spec.json`, `design-graph.json`, an Android/PICO runtime project, or a downstream app-generation handoff.
- Once the design is delivery-ready and accepted, the concrete downstream consumer is `spatial-design-to-app`: it owns an independent `../spatial-design-to-app/references/design-package-bridge.md` (its own adapter/bridge, per the §6A independent-adapter authorization above) that converts this design package's delivered Markdown facts into its own implementation inputs (its `evidence` / `normalized` / `assumption` three-artifact set), and only then enters its Phase 4 container/window-model decisions and Phase 6 code generation. This Skill does not produce those downstream artifacts, the container/window enum decisions, or that generated code; that conversion and decision-making stay entirely on the downstream side, gated by the §3c Main-Thread Acceptance requirement (`designStatus=ready_for_design_delivery` plus a recorded acceptance) before any such handoff.
