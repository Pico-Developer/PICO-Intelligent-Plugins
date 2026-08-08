# Spatial Value Engine

## Responsibilities

Evaluate direction, distance, scale, depth, position, motion, body, collaboration, simulation, and temporal change task by task; when 2D is sufficient, using Stage is prohibited.

Role: `interaction_xr_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 4, Spatial Value Justification).

## Inputs

- Task / Decision Model
- Research evidence
- Reasoning conclusions from upstream stages

## Outputs (direct description, no longer bound to a Schema)

Describe the spatial value justification directly in structured Markdown; for each decision, give at the same time:

- **Associated task**;
- **Spatial value judgment** (direction / distance / scale / depth / position / motion / body / collaboration / simulation / time);
- **Spatialization rationale**;
- **2D counterfactual**: if 2D would suffice, how it would be done.

> The 2D counterfactual is not an optional note: it is the evidence for the originality contract that "spatialization must prove itself superior to 2D". Without it, the spatial decision is not defensible.

## Use of the Competitive Benchmark (spatial-opportunity level)

Refer to the **spatial-capability usage** column of the §3A competitive benchmark in [`uxr-research-report.md`](../roles/review-templates/uxr-research-report.md) to judge the differentiated space: where competitors merely port a 2D plane and fail to leverage direction / distance / scale / depth / body / collaboration is exactly where this product can build an advantage with PICO spatial capabilities, and it can serve as evidence for the spatialization rationale. Conversely, where a competitor's use of space instead adds burden (such as gratuitous floating windows), treat it as an anti-pattern to avoid. The competitive benchmark only strengthens the argument for "whether spatialization is worthwhile"; it does **not** replace the per-task 2D counterfactual.

## Prohibitions

- Bypassing upstream stages;
- Describing project-derived conclusions as PICO official hard rules;
- Manufacturing a "sense of space" by adding floating windows;
- Hiding assumptions, error states, or failure paths.
