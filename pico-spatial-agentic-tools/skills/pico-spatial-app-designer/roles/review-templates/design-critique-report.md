# Design Critique Report · <project name>

> Role: independent reviewers (`evidence_integrity_reviewer` / `spatial_concept_reviewer` / `design_coherence_reviewer` / `prototype_qa_reviewer` / `delivery_readiness_reviewer`) + generation-time Critic self-check | Workflow stage(s): `problem_evidence_review` / `spatial_concept_review` / `design_system_review` / `critic` / `patch` / `delivery_readiness_review` | Downstream recipients: PM, Interaction Designer, Visual Designer, QA
>
> This document carries each reviewer role's **LLM reasoning information** and **direct description of outputs**. It is not bound to any JSON Schema or validator error codes; mandatory gates are expressed through this document's structured Markdown required tables, independent review evidence, and the `block` status.

## 0. Reasoning Guidance (how the reviewer reasons)

- **Separation of duties**: specialized roles are responsible for generation, independent roles are responsible for review, and delivery status is derived from the review gate results. Reviewers only output findings, impact, evidence, and patch goals; they **must not directly rewrite the reviewed artifact**, and **must not** overstep to declare downstream app generation, PICO runtime, or device validation as ready.
- **Reviewers must differ from the generator of the content being reviewed** (independence).
- **Review status is separated from downstream validation**: the design delivery status only describes whether the design package passed the complete review gate; it does not represent downstream implementation or device validation.
- **Patches are bounded**: when it does not pass, emit a local patch, do not rewrite the entire design; each patch corresponds to a problem, target node, and expected improvement.

Review focus at each gate:

| Review Gate | Reviewer Role | Review Focus |
|---|---|---|
| Problem and evidence | evidence_integrity_reviewer | source quality, scope, confidence, unsupported claims, assumptions disguised as facts, missing validation plans |
| Spatial concept | spatial_concept_reviewer | whether tasks produce decisions, whether the spatial thesis has a valid 2D alternative, whether assumptions are substantively different, whether selection uses evidence and comfort constraints |
| Design system | design_coherence_reviewer | **first check component structural fidelity, then check semantic coverage**: verify component by component against the fixed 8 sections (basic fields, anatomy.layout, sizing, metrics, renderSpec, dataBindings, variants, states); any missing one is `block`, and the shared state table and coverage reconciliation cannot offset it. After the structure fully passes, re-review tables A/B/C (data-entity bindings, actionable-decision interactions, primary-component sub-states) and visual/container/layout/accessibility/error-recovery/data-trust consistency |
| Preview implementation | prototype_qa_reviewer | **first check input readiness, then check item-by-item implementation fidelity**: the five mapping tables of state/transition, renderSpec elements, dataBindings normal value/fallback, variants/component-specific states, responsive/Reduce Motion; a name appearing does not count as evidence, any missing core item is `block` |
| Delivery readiness | delivery_readiness_reviewer | traceability completeness, package consistency, risks, limitations, review gate status, and design delivery readiness |

## 1. Direct Description of Outputs

This report delivers: **review verdicts at each gate → item-by-item "good UI" scoring → quality-dimension scoring → originality audit → process audit → pass/risk verdict → patch list**. The sections below are the structured descriptions of these outputs.

### Reviewer Invocation Evidence

| Review Gate | reviewerRole | invocationId | contextPolicy | reviewed artifact revision | Independently rebuilt evidence | Verdict |
|---|---|---|---|---|---|---|
| Problem and evidence | evidence_integrity_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / block |
| Spatial concept | spatial_concept_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / block |
| Design system | design_coherence_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / block |
| Preview implementation | prototype_qa_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / block |
| Delivery self-review | delivery_readiness_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / block |
| Delivery readiness | delivery_readiness_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / block |

> When any `invocationId` is empty, `contextPolicy=unavailable`, the review does not reference the exact active revision, or "independently rebuilt evidence=no", the corresponding gate can only be `block`. When any independent review evidence is missing, the overall design status is at least `review_blocked` and cannot be offset by other reviewers, the quality total score, or worker self-assessment.

## 2. Review Scope and Gate Records

- **Reviewed objects**: <interaction spec / visual spec / preview prototype version number>
- **Review basis**: PICO "good UI" checklist + quality-contract acceptance criteria + product-research market baseline
- **Review execution records**: <fill in reviewer invocation, contextPolicy, and reviewedRevision; no external-role approval is required>

| Review Gate | Reviewer Role | required | reviewedRevision | blockingFindings | Review recommendation (pass / changes_requested / block) | Evidence |
|---|---|---|---:|---|---|---|
| Problem and evidence | evidence_integrity_reviewer | yes | | | | |
| Spatial concept | spatial_concept_reviewer | yes | | | | |
| Design system | design_coherence_reviewer | yes | | | | |
| Preview implementation | prototype_qa_reviewer | yes | | | | |
| Delivery self-review | delivery_readiness_reviewer | yes | | | | |
| Delivery readiness | delivery_readiness_reviewer | yes | | | | |

### 2.1 Delivery Status

| Field | Value |
|---|---|
| reviewGateStatus | pass / block / changes_requested |
| minimumCompletenessGate | pass / block |
| designStatus | draft / invalid / review_blocked / changes_requested / ready_for_design_delivery |
| deliveryStatus | draft / invalid / review_blocked / changes_requested / ready_for_design_delivery |
| designDeliveryReady | no / yes |
| downstreamAppGenerationReady | no |

> The status priority is fixed as `invalid > review_blocked > changes_requested >
> ready_for_design_delivery > draft`. Only when all required hard gates and review gates are `pass`,
> there is no active P0/P1 blocking finding, and main-thread acceptance passes is
> `deliveryStatus=ready_for_design_delivery` allowed. This status only means the design package is delivery-ready; it does not mean
> PICO runtime or device validation is ready.

### 2.1A Hard Gate Summary (required before the delivery verdict)

> The reviewer and main thread must rebuild the verdict from the original documents; do not copy the worker's `pass`. When any required evidence
> is empty, that row can only be `block`.

| hard gate | pass condition | Evidence Anchor | Verdict |
|---|---|---|---|
| HG-TRACE | 17 stage receipts item by item, in order, not reconstructed after the fact; fields and revisions complete | execution-trace §2 | pass / block |
| HG-REVIEW | all review stages have an independent invocation, exact revision, and rebuilt evidence | this report's Reviewer Invocation Evidence + preview-qa-report §2.0 | pass / block |
| HG-DOCS | the six core documents pass the Minimum Completeness Gate | §2.1B | pass / block |
| HG-COMPONENT | all core components have the fixed 8-section structure complete | §2.2–§2.3 | pass / block |
| HG-PREVIEW | Manifest exists, the five tables are complete, and the generation-side and QA denominators are consistent | preview-qa-report §2–§3 | pass / block |
| HG-REVISION | the revisions of the active artifact, review, and derived outputs are consistent | execution-trace §4–§5 | pass / block |
| HG-FINDINGS | no active P0/P1 blocking finding | §8 Patch + findings | pass / block |
| HG-HOST | the main thread has read the acceptance evidence and re-derived designStatus | §2.1C | pass / block |

**Status derivation rules:**

- HG-TRACE / HG-DOCS / HG-PREVIEW / HG-REVISION any `block`:
  `designStatus=invalid`.
- HG-REVIEW / HG-COMPONENT / HG-FINDINGS any `block`:
  `designStatus=review_blocked`.
- An active patch goal exists: `designStatus=changes_requested`.
- Only when all rows are `pass`: `designStatus=ready_for_design_delivery`.

### 2.1B Minimum Completeness Re-review of Core Role Documents

> "The section exists" does not equal a pass. When it still contains placeholders, a key table has only an empty sample row, a sourced fact anchor is missing, or a summary replaces
> item-by-item facts, the verdict must be `block`.

| Document | Minimum structure / content threshold | Reviewer's actual evidence | Verdict |
|---|---|---|---|
| pm-requirement-spec.md | intent, assumptions, quality contract, requirements traceability complete and acceptance-testable | | pass / block |
| uxr-research-report.md | five categories of evidence/gaps, ≥3 competitors, domain model, Persona/Journey/duration/safety evidence complete | | pass / block |
| interaction-spatial-spec.md | principles, tasks, spatial value, ≥3 assumptions, selection, container/attachment/sizing, state/transition/exception/exit complete | | pass / block |
| visual-system-spec.md | visual direction, tokens, window structure, 8 sections per core component, coverage reconciliation complete | | pass / block |
| design-critique-report.md | independent review evidence, hard gate, findings/patch, status derivation complete | | pass / block |
| preview-qa-report.md | input readiness, Manifest, declarative checks, five tables, independent denominator reconciliation complete | | pass / block |

### 2.1C Main-Thread Acceptance Record (required before downstream handoff)

| Field | Value |
|---|---|
| hostAcceptanceId | <unique ID for this main-thread acceptance> |
| acceptedBy | main_thread_host_llm |
| evidenceRead | execution-trace.md / design-critique-report.md / preview-qa-report.md |
| rederivedDesignStatus | invalid / review_blocked / changes_requested / ready_for_design_delivery |
| blockingEvidence | <write none if there is none; must not be left empty> |
| downstreamAppGenerationAllowed | no / yes |
| acceptedAt | <ISO-8601> |

> A worker self-reporting `pass`, generating a complete file list, or writing out the 17 stage names does not constitute main-thread acceptance.
> Only when this table's evidence is complete, `rederivedDesignStatus=ready_for_design_delivery`, and
> `downstreamAppGenerationAllowed=yes` is calling the downstream app-generation skill allowed.

### 2.2 Component Structural Fidelity Verification (required at the design-system gate)

> One row per core component; "yes" must be accompanied by section or line-number evidence in `visual-system-spec.md`. If any item is "no", the design-system gate can only be filled as `block`, and must not continue to be judged as a pass by the quality total score.

| Core Component | Basic fields per row | anatomy.layout | sizing (references window default/min/max) | metrics (fall within content area) | renderSpec | dataBindings | variants | states + stacking precedence | Evidence Anchor | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| | yes / no | yes / no | yes / no | yes / no | yes / no | yes / no | yes / no | yes / no | | pass / block |

### 2.3 Design-System Denominator Reconciliation (required at the design-system gate)

| Denominator Type | Generation-side total | Reviewer-rebuilt total | Difference | Verdict |
|---|---:|---:|---:|---|
| Core components | | | | pass / block |
| Component 8-section evidence units | | | | pass / block |
| Data-entity bindings | | | | pass / block |
| Actionable decisions | | | | pass / block |

## 3. Item-by-Item "Good UI" Checklist Scoring

> Score item by item against the PICO good UI checklist (0–5), recording evidence and problem localization. Every deducted item must have evidence and problem localization.

| # | Checklist Item | Score (0–5) | Evidence / problem localization | Blocking |
|---|---|---|---|---|
| 1 | Depth information priority (near = important) | | | yes / no |
| 2 | Vestibular-visual consistency | | | |
| 3 | Eye-hand interaction usability | | | |
| 4 | Safety mode / boundary | | | |
| 5 | Central field of view first | | | |
| 6 | Single primary focus (primaryFocusCount=1) | | | |
| 7 | Window / dp-dmm unit conventions | | | |
| 8 | Component default size tiers | | | |
| 9 | Dual-channel semantics of color + text | | | |
| 10 | Visual restraint in dark environments | | | |
| ... | <complete per the full checklist> | | | |
| | **Total / average** | | | |

## 4. Quality-Dimension Scoring (Design Critic self-check)

> A generation-time subjective self-check, used to find quality gaps before submission. Every score must point to a specific node or field — a state name / component name / object count is not sufficient as evidence. Do not give a full score just because "no hard rule failed".

| Dimension | Max | Score | Evidence (specific node/field) |
|---|---|---|---|
| Task Completion | 20 | | |
| Spatial Value | 15 | | |
| PICO Alignment | 15 | | |
| Domain Depth | 15 | | |
| Safety & Comfort | 15 | | |
| Information Hierarchy | 10 | | |
| Data Trust | 5 | | |
| Engineering Feasibility | 5 | | |
| **Total / 100** | 100 | | |

Review focus: decision output and completion time; the single primary focus; state composition and responsive behavior; component anatomy/bindings/variants; whether the Stage brings direction/distance/depth value; data freshness/confidence/failure state; visual tokens and non-color semantics; preview coverage.

## 5. Originality Audit

> Audit standard: **not "whether there is zero reference", but "whether there is a defensible differentiation on top of the market baseline"**. Check both homogenization and whether a necessary paradigm already validated by competitors is missing. Copying a case's state sequence, layout IDs, component sequence, Toolbar structure, or visual concept (without requirement derivation) is judged a failure.

| Audit Dimension | Verdict | Evidence |
|---|---|---|
| Whether there is a defensible differentiation | <yes / no> | <unique points relative to competitors> |
| Whether homogenization / "AI flavor" exists | <yes / no> | <localization of similar points> |
| Whether a necessary paradigm validated by competitors is missing | <yes / no> | <missing items such as safety boundaries, indirect interaction, etc.> |
| templateReuse | <yes / no> | <source, should be no> |
| Whether cases were loaded during generation | <list> | <should be empty> |

## 6. Process Audit

> Verify whether the design was independently derived rather than mechanically applied. Report missing reasoning artifacts; do not compare visual similarity to a "golden design".

| Process Item | Satisfied | Evidence / gap |
|---|---|---|
| Complete process trace processTrace | | |
| At least three design hypotheses | | |
| Evidence-based selection | | |
| Requirements traceability requirementsTraceability | | |
| Layout has derivation | | |
| Components have a task/data source | | |
| Preview input readiness | | preview-qa-report §2.1 |
| Preview implementation fidelity | | preview-qa-report §3.1–§3.5; item-by-item denominators and independent evidence |
| Stages 13–15 re-run after implementation-fact changes | | version / time / change record |
| Design package is deliverable | | |

## 7. Pass / Risk Verdict

- **Whether the delivery gate is met**: <pass / conditional pass / patch>
- **Blocking issues (P0)**: <items that must be fixed before delivery>
- **Risk items (P1/P2)**: <items that can be iterated later but must be recorded>
- **Compliant highlights**: <design decisions worth keeping>

## 8. Patch List

> When it does not pass, emit a patch, do local repairs, do not rely on after-the-fact rework, and do not rewrite the entire design. Each patch contains a problem, target node, operation, and expected improvement; after patching, the relevant reviews must be re-run. At most four patch rounds.

| # | Target Node | Severity | Problem description (with before evidence) | Modification operation | Expected improvement / validation assertion | Patch Owner Role |
|---|---|---|---|---|---|---|
| 1 | | | | | | |

## 9. Delivery and Recipients

- **Deliverables**: review verdicts at each gate, item-by-item scoring, originality and process audits, patch list (this document is their human-readable source of fact)
- **Recipients**: PM, Interaction Designer, Visual Designer (fallback repairs), QA

---

> Format convention: every deducted item must have evidence and problem localization; reviewers only emit findings/patch goals, do not rewrite artifacts, and do not overstep to declare downstream implementation or device-validation status; the originality audit must check both "homogenization" and "missing necessary paradigm"; patch items must have closed-loop verdict criteria.
