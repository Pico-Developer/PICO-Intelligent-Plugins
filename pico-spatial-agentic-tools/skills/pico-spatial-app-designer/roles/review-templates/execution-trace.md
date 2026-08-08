# Execution Trace · <project name>

> This document only records process evidence; it does not carry design facts and does not replace role documents or review verdicts.

## 1. Run Identity

| Field | Value |
|---|---|
| runId | <unique ID of this run> |
| userPromptDigest | <SHA256 of the user's original request or a stable host digest> |
| skillSource | <absolute path of the SKILL.md actually read> |
| workflowSource | <absolute path of the workflow.json actually read> |
| startedAt | <ISO-8601> |
| completedAt | <ISO-8601; leave empty if not completed> |

## 2. Stage Receipts

> The host advances only one stage at a time: fill that row's `startedAt` before starting, and fill in the remaining fields immediately after completion.
> A reasoning stage's `result` can only be `completed / blocked`, and a review stage can only be
> `pass / changes_requested / block`. Do not fill in `pass` directly and then backfill input, instruction,
> or artifact evidence; do not batch-rebuild receipts after all artifacts are complete.

| seq | stageId | kind | role | startedAt | completedAt | requiredInputsRead | instructionFilesRead | artifactWrites | artifactRevisionAfter | result |
|---:|---|---|---|---|---|---|---|---|---|---|
| 1 | intent | reasoning | product_strategist | | | | | | | pending |
| 2 | research | reasoning | research_analyst | | | | | | | pending |
| 3 | quality_contract | reasoning | product_strategist | | | | | | | pending |
| 4 | problem_evidence_review | review | evidence_integrity_reviewer | | | | | | | pending |
| 5 | task_model | reasoning | task_decision_designer | | | | | | | pending |
| 6 | concept_formation | reasoning | interaction_xr_designer | | | | | | | pending |
| 7 | spatial_concept_review | review | spatial_concept_reviewer | | | | | | | pending |
| 8 | visual_direction | reasoning | visual_designer | | | | | | | pending |
| 9 | spatial_structure | reasoning | interaction_xr_designer | | | | | | | pending |
| 10 | composition_synthesis | reasoning | spatial_design_system_designer | | | | | | | pending |
| 11 | design_system | reasoning | spatial_design_system_designer | | | | | | | pending |
| 12 | design_system_review | review | design_coherence_reviewer | | | | | | | pending |
| 13 | preview_build | reasoning | prototype_frontend_engineer | | | | | | | pending |
| 14 | preview_review | review | prototype_qa_reviewer | | | | | | | pending |
| 15 | delivery_self_review | review | delivery_readiness_reviewer | | | | | | | pending |
| 16 | patch | reasoning | spatial_design_system_designer | | | | | | | pending / not_needed |
| 17 | delivery_readiness_review | review | delivery_readiness_reviewer | | | | | | | pending |

> `patch` must leave a receipt even if no changes are needed, with `result=completed`, and write `none` in `artifactWrites`,
> stating there is no active patch goal; do not delete that row or use a blank to indicate a skip.

## 3. Review Invocations

| stageId | reviewerRole | invocationId | contextPolicy | reviewedRevision | evidenceRebuilt | recommendation |
|---|---|---|---|---|---|---|
| problem_evidence_review | evidence_integrity_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / changes_requested / block |
| spatial_concept_review | spatial_concept_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / changes_requested / block |
| design_system_review | design_coherence_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / changes_requested / block |
| preview_review | prototype_qa_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / changes_requested / block |
| delivery_self_review | delivery_readiness_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / changes_requested / block |
| delivery_readiness_review | delivery_readiness_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / changes_requested / block |

> If any row is missing a field, `contextPolicy=unavailable`, the role is played in the same context, or
> `evidenceRebuilt=no`, the overall design status is at least `review_blocked`; a generator's summary cannot serve as independent evidence.

## 4. Artifact Revisions

| artifact | revision | producedByStage | sourceRevisions | producedAt | supersedes | active |
|---|---:|---|---|---|---|---|
| pm-requirement-spec.md | 1 | intent | none | | none | yes |

> `preview.html` must reference the exact active revision of `interaction-spatial-spec.md`, `visual-system-spec.md`, and
> `design-critique-report.md#design_system_review`.

## 5. Invalidation And Rerun

| changeId | changedFact | oldRevision | invalidatedArtifacts | requiredRerunStages | rerunReceiptRefs | status |
|---|---|---|---|---|---|---|
| | | | | | | pending / complete |

## 6. Hard Gate Status Derivation

> This table is re-derived by the host from the raw evidence above and cannot copy the worker's self-assessment. The status priority is fixed as
> `invalid > review_blocked > changes_requested > ready_for_design_delivery > draft`.

| hard gate | Pass condition | Evidence | Verdict |
|---|---|---|---|
| HG-TRACE | 17 receipt rows in complete order; required fields non-empty; time and artifact revision explainable; no after-the-fact batch rebuild | §2 receipt row range | pass / block |
| HG-REVIEW | All 6 review stages have an independent invocation, an exact revision, and `evidenceRebuilt=yes` | §3 invocation row range | pass / block |
| HG-REVISION | active artifact revision, derived source revision, and invalidation/rerun records are consistent | §4–§5 | pass / block |
| HG-DOCS | PM / UXR / Interaction / Visual / Critique / Preview Minimum Completeness Gates all pass | Each document's Minimum Completeness Gate | pass / block |
| HG-PREVIEW | Coverage Manifest exists; the generation side and QA rebuild the same denominator; all five mapping tables complete | preview-qa-report §2–§3 | pass / block |
| HG-FINDINGS | No active P0/P1 blocking finding, patch closed | design-critique-report | pass / block |
| HG-HOST | The main thread has independently read the three acceptance evidence pieces and recorded the acceptance verdict | Host Acceptance Record | pass / block |

| Field | Value | Derivation Basis |
|---|---|---|
| designStatus | invalid / review_blocked / changes_requested / ready_for_design_delivery / draft | The hard gates above, manually filling `pass` is prohibited |
| designDeliveryReady | no / yes | yes only when `designStatus=ready_for_design_delivery` |
| downstreamAppGenerationAllowed | no / yes | yes only when HG-HOST=pass and designStatus is ready |

### Mandatory status derivation

- If any of HG-TRACE, HG-REVISION, HG-DOCS, or HG-PREVIEW is `block`:
  `designStatus | invalid`.
- If any HG-REVIEW is `block`: `designStatus=review_blocked`, and it must not be offset by other scores.
- With an active patch goal: `designStatus=changes_requested`.
- Only when all hard gates are `pass` may `ready_for_design_delivery` be written.

## 7. Completion Check

| Check Item | Verdict | Evidence |
|---|---|---|
| The 17 stage receipts are in complete order and written promptly per stage | pass / block | receipt row range + time |
| Each review has an independent invocation | pass / block | invocationId |
| All active artifact revisions are consistent | pass / block | revision table |
| Delivery status is derived by the review gate | pass / block | design-critique-report Delivery Status |
| All review gates pass | pass / block | Review Gate Record |
| deliveryStatus is consistent with reviewGateStatus | pass / block | Delivery Status |
| Design delivery readiness does not masquerade as downstream runtime readiness | pass / block | downstreamAppGenerationReady / device validation boundary |
