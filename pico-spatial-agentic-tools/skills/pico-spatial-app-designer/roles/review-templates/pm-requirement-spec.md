# Spatial App Requirement Spec · <project name>

> Role: `product_strategist` | Workflow stage(s): `intent_draft` → `quality_contract_freeze` | Upstream inputs: user's raw requirements, `research_analyst` evidence/domain model | Downstream recipients: UXR, Interaction / Spatial Designer, Design Lead
>
> This document carries this role's **LLM reasoning information** and **direct description of outputs**. It is not bound to any JSON Schema or validator error codes; mandatory gates are expressed through this document's structured Markdown required tables, evidence anchors, and the `block` status.

## 0. Reasoning Guidance (how this role reasons)

- **Make decisions only at the product-outcome layer**: the outcomes the user must achieve, success criteria, and risk boundaries. Do not overstep into deciding layout, components, or visual direction, or substitute for human approval.
- **Requirement → intent extraction**: from the user's natural language, identify domain, sub-domain, target users, use scenarios, posture, frequency, duration, core tasks, key decisions, risks, data, AI, sensors, permissions, and collaboration.
- **A gap is an assumption, no implicit guessing**: write any unknown information into the "assumptions list" with `confidence / impact / validation plan`; do not present it as a factual statement.
- **The quality contract is derived from this requirement**, not copied from historical projects or templates. The contract must be usable by downstream roles as an acceptance anchor and starting point for traceability.
- **Prohibitions**: bypassing upstream stages; presenting the project's own derivations as PICO official hard rules; manufacturing a "sense of space" by adding floating windows; hiding assumptions, error states, or failure paths.

## 1. Direct Description of Outputs

This role delivers two facts: the **intent definition** (draft → frozen) and the **quality contract**. The sections below are the structured descriptions of these two outputs; filling in every item completely constitutes a complete delivery.

## 2. Background and Problem (intent definition · foundation)

- **One-sentence requirement description**: <describe in a paragraph of natural language what problem this app solves>
- **Target users**: <who uses it; if there are multiple types, list each separately>
- **Use scenarios**: <in what environment and at what moment it is used>
- **Wearing posture**: <sitting / standing / moving>
- **Frequency and duration**: <how often it is used, how long each session lasts>
- **Preliminary judgment of spatial necessity**: <why this experience is worth building as a spatial app rather than an ordinary app>

## 3. Key Moment (the linchpin of spatial value)

- **The moment a screen cannot achieve**: <the highlight moment that best embodies spatial value>
- **Placement on the immersion spectrum**: <Window → Volume → Full Space, marking which tier each core feature falls into>
- **Entry path**: <start from a window by default, letting the user control immersion themselves; do not go fully immersive right away>

## 4. Product Research (baseline anchors)

| Dimension | Content | Source |
|---|---|---|
| Competitor feature matrix | <what similar apps do / do not do> | <link / report> |
| Decision duration baseline | <how long a glance decision should take, how long fine-tuning dwell should last, with sourced anchors> | <source> |
| Industry safety · comfort conventions | <existing conventions on safety boundaries, vestibular-visual consistency, motion-sickness handling, etc.> | <source> |

## 5. Intent Definition (frozen items)

- **Domain / sub-domain**: <the domain it belongs to>
- **Risk level**: <low / medium / high>
- **Default space**: <Shared Space / Full Space>
- **Core scenario list**: <scenario 1, scenario 2, …>
- **Data / AI / sensors / permissions**: <whether real-time data, AI inference, or sensor input is used, and which permissions must be requested>
- **Collaboration**: <whether multi-user / multi-device collaboration is involved>

## 6. Assumptions List (missing information, must not be treated as fact)

| # | Assumption | Confidence | Impact | Validation Plan |
|---|---|---|---|---|
| 1 | | high / medium / low | | |

## 7. Quality Contract (acceptance criteria)

> Derived from this requirement, serving as the anchor for the Design Critic and the traceability table.

- **Required business outcomes**: <list of acceptance-testable outcomes>
- **Success / efficiency criteria**: <time or efficiency targets>
- **Risks and must-not-fail items**: <high-risk confirmations, safety boundaries, etc.>
- **Preference for default number of visible primary windows**: <how many primary WindowContainers may be visible at once by default; if Stage-only, declare it here>
- **Preference for domain-specialized components**: <the expected richness the domain components should reach>
- **Preference for real-time data trust**: <whether alerts must carry a source, etc.>
- **PICO platform and spatial-design hard constraints**: <key platform-compliance items>
- **Originality requirement**: <make a defensible differentiation on top of the market baseline>
- **Design / readability / downstream-implementation acceptance plan**: <how to verify the design is complete, the docs are readable, and the implementation is handoff-ready>

## 8. Requirements Traceability

| Requirement | Implementation Node | Validation Method |
|---|---|---|
| | | |

## 9. Minimum Completeness Gate

> This table is self-checked by `product_strategist` and independently re-reviewed by `evidence_integrity_reviewer`.
> A section that exists but still contains placeholders, a key table that has only an empty sample row, or acceptance criteria that are unverifiable or lack evidence anchors are all considered unmet.
> When any row is `block`, this document's `minimumCompletenessGate=block` and the overall
> `designStatus=invalid`, and it must not proceed to subsequent design stages.

| Check Item | Minimum Pass Condition | Evidence Anchor | Verdict |
|---|---|---|---|
| Background and intent | one-sentence requirement, users, scenario, posture, frequency/duration, and spatial necessity all have facts or explicit assumptions | §2–§5 | pass / block |
| Assumption governance | every unknown item has confidence, impact, and a validation plan; no implicit guessing | §6 | pass / block |
| Quality contract | all nine contract items are complete; outcomes/efficiency/risks are acceptance-testable and constraint sources are traceable | §7 | pass / block |
| Requirements traceability | every required business outcome maps to at least one implementation node and validation method | §8 | pass / block |

| Field | Value |
|---|---|
| minimumCompletenessGate | pass / block |

## 10. Delivery and Recipients

- **Deliverables**: intent definition + quality contract (this document is their human-readable source of fact)
- **Recipients**: UXR, Interaction / Spatial Designer, Design Lead

---

> Format convention: every "why" must have a source (traceable); missing information goes into the assumptions list with confidence/impact/validation plan; acceptance items must be quantifiable; do not dress up the project's derivations as PICO official rules.
