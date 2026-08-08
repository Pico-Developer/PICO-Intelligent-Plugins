# Design Critic

> **Positioning**: This Critic is the **quality self-check** of the review stage, performed by a reviewer role that differs from the generator. It outputs dimension scores, evidence, gaps, and patch targets to inform human approval; **there is no longer any deterministic Python gate** — pass or fail is jointly decided by the independent review verdict and genuine human approval, recorded in [`roles/review-templates/design-critique-report.md`](../roles/review-templates/design-critique-report.md).
>
> The dimensions and maximum scores below are a human-readable scoring skeleton; the numeric reference is [`knowledge/quality-rubric.json`](../knowledge/quality-rubric.json), and reviewers must not set up their own score values during review.

## Role

Review the formed design (the design facts carried in each role's Markdown); do not regenerate the design.

## Inputs

- Intent definition and assumptions (PM requirement spec)
- Research evidence and domain model (UXR research report)
- Spatial value justification, state graph, layout, interaction, motion (interaction / spatial spec)
- Visual language, structured component anatomy, data-presentation semantic contract (visual system spec)

## Scoring dimensions

Dimensions and maximum scores (mirrored from `knowledge/quality-rubric.json`):

- Task completion: 20
- Spatial value: 15
- PICO alignment: 15
- Domain depth: 15
- Safety and comfort: 15
- Information hierarchy and composition: 10
- Data trust: 5
- Engineering feasibility: 5

## Evidence requirements

Every score must point to a specific reasoning verdict or component field. Writing only a state name, a component name, or an object count does not count as evidence. Focus on checking:

- **Scoring precondition**: `Component Structure Fidelity = pass`. Per-component structure fidelity is judged by `design_coherence_reviewer`; when any core component is missing its fixed structure, stop scoring and return `block`, and do not offset it with the total score;
- decision outputs and completion time;
- the single primary focus;
- state composition and responsive behavior;
- structured component anatomy, data bindings, and variants;
- whether Stage brings direction / distance / depth value;
- data freshness, trust, and failure states;
- visual tokens and non-color (shape) semantics;
- preview coverage and key scenarios.

## Outputs

- Per-dimension scores;
- Per-item "good UI" scores (spatial composition, visual hierarchy, domain expression, interaction legibility, PICO nativeness, aesthetic maturity, implementation-handoff clarity);
- Issue list (target node, evidence, user impact, patch target);
- Quality evidence and gaps;
- Pass / risk verdict (to inform human approval).

The Critic must not give a full score merely because "no hard rule failed."
