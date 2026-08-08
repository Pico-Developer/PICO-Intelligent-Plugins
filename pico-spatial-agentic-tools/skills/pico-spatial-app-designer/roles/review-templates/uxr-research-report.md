# User Research Report · <project name>

> Role: `research_analyst` | Workflow stage(s): `evidence_research` → `domain_model` | Upstream inputs: intent draft, user materials, official platform rules | Downstream recipients: Interaction / Spatial Designer, Visual Designer, PM
>
> This document carries this role's **LLM reasoning information** and **direct description of outputs**. It is not bound to any JSON Schema or validator error codes; mandatory gates are expressed through this document's structured Markdown required tables, evidence anchors, and the `block` status.

## 0. Reasoning Guidance (how this role reasons)

- **Make judgments only at the evidence layer**: evidence classification, confidence, scope of applicability, evidence gaps. Do not decide business priorities, layout, or visual direction, and do not substitute for human approval.
- **Retrieve the specialized knowledge truly relevant to this requirement**, with sources limited to: official documentation, trustworthy public research, user-provided materials, and explicitly labeled assumptions. Do not read page structures, fixed component lists, or layout templates from fixed templates, historical cases, or external references.
- **Distinguish three states**:
  - **Evidence**: backed by an official / external / user-provided source; must state the source, scope, confidence, and observation time.
  - **Assumption**: a provisional judgment when sources are insufficient; must explain why it is needed, bound its scope, and provide a validation plan, with confidence lower than evidence.
  - **Evidence gap**: missing or unverified key information; explicitly state "what is unknown" and never treat the unknown as true.
- **Domain model**: on top of the evidence, organize the specialized tasks, decision model, domain component concepts, spatial patterns, specialized risks, and anti-patterns; domain knowledge only supplies terminology and rules, not a component catalog that must be reused.
- **Prohibitions**: treating assumptions as facts; copying a competitor's layout / state graph / component set / visual style; fabricating competitor facts, market share, pricing, or maturity; bypassing upstream stages; presenting the project's derivations as PICO official rules.

## 1. Direct Description of Outputs

This role delivers two facts: **research evidence** and the **domain model**. The research evidence must cover five categories: `market / user / domain / platform / safety`; when a source is missing, it must still be written explicitly as an evidence gap rather than omitted. The sections below are the structured descriptions of these two outputs.

## 2. Research Goals and Questions

- **Assumptions to be validated**: <assumptions from the intent definition>
- **Research methods**: <interviews / usability testing / hands-on competitor testing / log analysis>
- **Sample description**: <sample size, profile, recruitment criteria>

## 3. Five Categories of Research Evidence (including gaps)

> Each piece of evidence states: claim → source → source type → scope → confidence → observation time → validation plan. When there is no reliable source, write it as an "evidence gap" and note what validation is needed.

| Category | Evidence / Gap (claim) | Source | Source Type (official/external/user/assumption) | Scope | Confidence | Observation Time | Validation Plan |
|---|---|---|---|---|---|---|---|
| market | | | | | high/medium/low | | |
| user | | | | | | | |
| domain | | | | | | | |
| platform | | | | | | | |
| safety | | | | | | | |

- **Boundary of market evidence usage**: it can frame opportunities and risks, but **cannot** directly decide UI structure, state graph, component combinations, visuals, color, motion, or final interaction.
- **Handling source conflicts**: <record both parties' claims, or record as a gap and explain the validation needed>

## 3A. Competitive Benchmark (≥ 3 products, a first-class output of `market` evidence)

> Analyze at least three similar / adjacent products; when there are fewer than three XR competitors in the same domain, you may include same-task competitors from 2D or other platforms, but you must note the platform differences and migration risks in the "spatial-capability usage" column. When fewer than three, the reason must be stated in the gap notes below. This table is consumed by the market-differentiation contract (`evidenceRefs`) of concept selection (`03b`).

| # | Competitor / Platform | Feature needs (core tasks · key capabilities · missing capabilities · target-user scenarios) | Interaction experience (input method · core path · learning cost · anti-patterns) | Visual experience (hierarchy density · style · readability & comfort, observe only, do not reuse) | Spatial-capability usage (direction/distance/scale/depth/body/collaboration or 2D copy-over) | Source / type / observation time |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

**Per-product absorb / avoid distillation**

| # | Strengths worth absorbing (needs/opportunity layer) | Weaknesses / anti-patterns to avoid |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

- **Our differentiation opportunities (summary)**: <how this product, based on PICO spatial capabilities (spatial value + spatial-design guidelines), stands out, absorbs the strengths above, avoids the anti-patterns above, and improves competitiveness — to be referenced by `03b` market-differentiation `positioning` / `rationale`>
- **Sample and gap notes**: <whether the number of competitors reaches 3; if not, the reason and substitute samples; evidence gaps in each dimension>
- **Absorption-boundary declaration**: absorption applies only at the needs / opportunity layer; do not copy any competitor's layout, state graph, component combinations, or visual style (subject to the originality hard rule).

## 4. Domain Model (organizing specialized knowledge)

- **Domain workflow**: <the actual work steps of specialized users>
- **Decision variables**: <list of variables that influence key decisions>
- **Data entities and timeliness**: <core data objects, update frequency, timeliness sensitivity>
- **Specialized risks**: <consequences of misjudgment / misoperation>
- **User mental model**: <how users understand this domain>
- **Mature product patterns and anti-patterns**: <paradigms worth referencing; anti-patterns to avoid (for semantic reference only, not as a reuse catalog)>

## 5. Persona

> Build one Persona per target-user type; avoid designing for "everyone."

### Persona 1: <persona name / one-sentence tag>

| Dimension | Content |
|---|---|
| Basic information | <age range / occupation / XR experience (novice/advanced)> |
| Use scenario and frequency | <when, where, how often it is used> |
| Goals / motivations | <what they want to achieve through this app> |
| Pain points / frustrations | <where the current solution blocks them> |
| Spatial usage habits | <usual wearing posture (sitting/standing/moving), tolerable duration per session> |
| Accessibility needs | <low vision / color blindness / limited mobility, etc.; mark N/A if none> |
| Key quote (verbatim) | "<the user's own words>" |

<!-- If there are multiple personas, copy the table block above for Persona 2, Persona 3 -->

## 6. Journey Map

| Stage | Awareness / entry | First hands-on | Core use | Depth / immersion | Exit / return |
|---|---|---|---|---|---|
| User goal | | | | | |
| User behavior | | | | | |
| Touchpoints / scenarios (window/full space) | | | | | |
| Thoughts | | | | | |
| Emotion curve (😀/😐/😞) | | | | | |
| Pain points | | | | | |
| **Opportunities (design implications)** | | | | | |

- **Locating the emotional low point**: <the worst-experience segment in the journey, which must be addressed first>
- **Summary of key opportunities**: <opportunities that can be turned into interaction/visual needs, for downstream reference>

## 7. Key Findings

> Each finding follows: finding → evidence → confidence → design implication

| # | Finding | Evidence | Confidence | Design Implication |
|---|---|---|---|---|
| 1 | | | high / medium / low | |

## 8. Wearing Posture and Field-of-View Insights

- **Usual posture**: <distribution of sitting / standing / moving>
- **Arm range of motion**: <comfortable reachable area>
- **Information capacity of the central field of view**: <main content should stay within the field of view; the more centered, the more comfortable>
- **Field-of-view stability / fatigue threshold**: <the comfortable upper limit of continuous use duration>

## 9. Eye-Hand Interaction Usability

- **Gaze focus + pinch hit rate**: <measured data>
- **Low-load interaction assumption**: <hands can rest on the desk / legs, supporting indirect interaction>
- **Mis-touch and feedback**: <whether gaze hover feedback is clear>

## 10. Duration Baseline Data (for the task model to reference)

| Decision Type | Duration Anchor (value) | Source |
|---|---|---|
| Glance decision | <ms / s> | |
| Fine-tuning dwell | <s> | |

## 11. Motion Sickness / Fatigue and Safety

- **Motion-sickness risk scenarios**: <which motion / movement content is risky>
- **Whether High Motion labeling is needed**: <yes / no>
- **Recommended duration and rest cadence**: <e.g., start with 20–30 minutes for first-time use>

> Subjective sensations such as comfort / fatigue / motion sickness must be handed off to subsequent device validation (see the device-validation boundary in the preview QA report); this design stage draws no on-device conclusions.

## 12. Minimum Completeness Gate

> This table is self-checked by `research_analyst` and independently re-reviewed by `evidence_integrity_reviewer`.
> Empty tables, source-less claims, writing assumptions as facts, or replacing item-by-item evidence with an "already researched" summary are all `block`.
> When any row is `block`, this document's `minimumCompletenessGate=block` and the overall
> `designStatus=invalid`.

| Check Item | Minimum Pass Condition | Evidence Anchor | Verdict |
|---|---|---|---|
| Five categories of evidence | market / user / domain / platform / safety each have at least one traceable piece of evidence or an explicit evidence gap | §3 | pass / block |
| Competitive benchmark | ≥3 products each covering features, interaction, visuals, spatial capability; when fewer, an explicit blocking gap | §3A | pass / block |
| Domain model | workflow, decision variables, data entities and timeliness, specialized risks, mental model, and anti-patterns are complete | §4 | pass / block |
| User evidence | Persona, Journey, and key findings all have sources/confidence, not invented profiles | §5–§7 | pass / block |
| Quantitative and safety | decision duration, posture/field of view, eye-hand input, and motion sickness/fatigue all have values, sources, or explicit to-be-validated gaps | §8–§11 | pass / block |

| Field | Value |
|---|---|
| minimumCompletenessGate | pass / block |

## 13. Delivery and Recipients

- **Deliverables**: research evidence + domain model (this document is their human-readable source of fact)
- **Recipients**: Interaction / Spatial Designer, Visual Designer, PM

---

> Format convention: every finding must have "evidence + confidence" complete; all five categories of evidence present (write missing sources as gaps, do not omit); duration and comfort boundaries must resolve to values; assumptions must not be treated as facts; do not copy competitor structures.
