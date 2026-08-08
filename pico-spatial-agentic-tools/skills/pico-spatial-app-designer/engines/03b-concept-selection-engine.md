# Concept Selection Engine

## Responsibilities

Score each hypothesis on task efficiency, spatial value, PICO comfort, domain depth, safety, accessibility, engineering feasibility, and distinctiveness. Select one, record the evidence, and retain the rejected options with rationale.

Role: `interaction_xr_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 6, Concept Selection Matrix).

## Inputs

- Design hypotheses, research evidence
- Reasoning conclusions from upstream stages

## Outputs (direct description, no longer bound to a Schema)

Provide in structured Markdown:

- **Selection matrix**: each hypothesis's scores and basis across the dimensions of task efficiency, spatial value, PICO comfort, domain depth, safety, accessibility, engineering feasibility, and distinctiveness;
- **Selected concept**: the chosen option and its evidence;
- **Rejected options**: retain the rejected concepts and the rationale.

### Market-differentiation contract (qualitative, not a matrix score)

`distinctiveness` remains the score in the decision matrix that measures a concept's originality and non-templated behavior, but it is **not** the complete market argument. Each selected concept must also include a separate qualitative description:

- **positioning**: the qualitative market positioning of the selected concept;
- **rationale**: an evidence-backed explanation of how this concept differs for the target market;
- **evidenceRefs**: cite research evidence IDs (including market evidence; when there is no market evidence, explicitly cite an evidence gap). Must cite specific entries and the "our differentiation opportunities" from the §3A competitive benchmark in [`uxr-research-report.md`](../roles/review-templates/uxr-research-report.md), explaining how the selected concept absorbs competitor strengths, avoids their anti-patterns, and fulfills the quality contract's differentiation goals as defensible positioning.

Rules:

- Market differentiation is required, qualitative, and evidence-backed;
- Do not assign a uniform numeric weight to market differentiation across projects;
- Market differentiation can explain positioning, risk, opportunity, and concept comparison;
- Market differentiation **must not** directly determine layout, state graph, component composition, visual style, color, or motion;
- A concept may be visually original but weak in market differentiation; record this faithfully and do not inflate `distinctiveness`.

## Prohibitions

- Describing project-derived conclusions as PICO official hard rules;
- Using market differentiation to directly determine layout / state graph / components / visuals;
- Hiding rejected options or inflating scores.
