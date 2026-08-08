# Domain Engine

## Responsibilities

Based on research evidence, organize specialized tasks, decision models, domain component concepts, spatial patterns, risks, and anti-patterns. Must not return only generic UI templates.

Role: `research_analyst`. Reasoning conclusions are recorded in [`roles/review-templates/uxr-research-report.md`](../roles/review-templates/uxr-research-report.md).

## Inputs

- Intent definition
- Research evidence
- Reasoning conclusions from upstream stages

## Outputs (direct description, no longer bound to a Schema)

Produce a **domain model**, written directly into the UXR research report document in structured Markdown:

- Domain workflows;
- Decision variables;
- Data entities and timeliness;
- Specialized risks;
- User mental models;
- Mature product patterns and anti-patterns (for semantic reference only, not a catalog that must be reused).

## Prohibitions

- Bypassing upstream stages;
- Describing project-derived conclusions as PICO official hard rules;
- Manufacturing a "sense of space" by adding floating windows;
- Hiding assumptions, error states, or failure paths.
