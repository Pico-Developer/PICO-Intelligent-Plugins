# Visual Direction Engine

## Responsibilities

Before writing the final design facts, generate 2–3 spatial visual directions. Do not write layout IDs / component IDs first and then rationalize them after the fact.

Role: `visual_designer`. Reasoning conclusions are recorded in [`roles/review-templates/visual-system-spec.md`](../roles/review-templates/visual-system-spec.md) (Section 2, Spatial Visual Direction Candidates).

## Inputs

- Selected concept, research evidence, quality contract
- Reasoning conclusions from upstream stages

## Outputs (direct description, no longer bound to a Schema)

Describe each visual direction candidate in structured Markdown:

- Spatial thesis;
- First-view composition;
- Container relationship;
- Depth plan;
- Information hierarchy;
- Interaction affordances;
- Spatial value;
- Dashboard risk;
- Preview prompt / render instruction.

Reject directions that differ only in color, theme, icons, or copy.

Use of the competitive benchmark (differentiation-reference level): refer to the **visual experience** column of the §3A competitive benchmark in [`uxr-research-report.md`](../roles/review-templates/uxr-research-report.md) as a reference for differentiation and dashboard risk — identify visual clichés common across competitors (such as flat dashboard stacking) to proactively differentiate, and identify their readability / comfort shortcomings to avoid. Competitor visuals are **for observational reference only and must never be reused**: do not copy competitors' composition, color scheme, component appearance, or style; the visual direction must still be independently derived from the project semantics and the approved concept.

The selected direction becomes the **approved visual reference** (record the selected direction + selection rationale; requires human confirmation or a structured design-effect review). Subsequent design facts must record and follow this approved direction, and must not create a new direction.

## Prohibitions

- Writing layout / component IDs first and then rationalizing the visual direction;
- Passing off color / theme / icon differences as substantially different directions;
- Describing project-derived conclusions as PICO official hard rules;
- Copying a visual direction from case studies without independent derivation.
