# Task and Decision Engine

## Responsibilities

Build the task graph and the decision graph. They drive the subsequent architecture and synthesis.

Role: `task_decision_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 3, Task / Decision Model).

## Inputs

- Intent definition, quality contract, research evidence, domain model
- Reasoning conclusions from upstream stages

## Outputs (direct description, no longer bound to a Schema)

Describe the task graph and the decision graph in structured Markdown. For each task, state:

- Actor and context;
- Input evidence;
- Decision outcome;
- Error consequence;
- Frequency;
- Dependencies.

Task naming comes from the project semantics; do not mechanically copy case-study tasks.

## Use of the Competitive Benchmark (requirement-coverage level)

Use the **functional requirements** column of the §3A competitive benchmark in [`uxr-research-report.md`](../roles/review-templates/uxr-research-report.md) to verify the coverage completeness of the task graph: key tasks that competitors commonly have but this design lacks must be explicitly included or explained as deliberately omitted; competitors' functional gaps and interaction anti-patterns are opportunities this product can pursue. Absorption stays at "which tasks to cover / which anti-patterns to avoid"; it does **not** copy competitors' task sequences or operation paths.

## Prohibitions

- Fabricating tasks out of thin air, bypassing research evidence;
- Describing project-derived conclusions as PICO official hard rules;
- Hiding assumptions, error states, or failure paths.
