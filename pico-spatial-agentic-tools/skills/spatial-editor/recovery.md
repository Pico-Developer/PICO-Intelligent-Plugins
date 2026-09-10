# Spatial Editor Controller Recovery

Read this module after the managed Spatial Editor Controller returns a rejected
submission, `errors[]`, `interrupted`, `waiting_for_user_decision`, or an
`EDITOR_*` error.

- Read `SKILL.md` for normal workflow selection, task decomposition, and handoff.
- Read `contracts.md` for the corrected form and exact field rules.
- This file owns error interpretation and recovery actions. It does not redefine
  normal forms or scene-design policy.

## Recovery Procedure

1. Read the latest persisted workflow result, not an earlier tool response.
2. Record `phase`, `status`, `nextAction`, every `errors[].code`, `retryable`, and
   `detail`.
3. Confirm that the rejected tool matched the immediately preceding
   `nextAction.type`. If it did not, classify the failure as an Agent sequencing
   error; do not attribute it to the Editor backend.
4. Use the most specific code below. The text after the first colon usually names the
   invalid field, entity, gate, or backend failure.
5. Preserve the same `run_id`. Never start a replacement run merely because a
   retryable submission was rejected.
6. Correct only the rejected contract or evidenced defect.
7. Follow the returned `nextAction`; do not call `advance_editor_workflow` while a
   corrected form, user decision, wait, or resume is required.
8. After every recovery call, discard the prior action and parse the newly returned
   state before doing anything else.
9. If an unknown code appears, report the exact code/message/detail and obey
   `retryable` plus `nextAction`. Do not infer success or bypass the Controller.

## Status Is Authoritative

| Status or next action                           | Required response                                                                                           |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `waiting_for_manifest` / `submit_manifest`      | Correct and resubmit a production Manifest.                                                                 |
| `waiting_for_revision_plan` / `submit_manifest` | Correct and resubmit `workflow_kind="revision"` with `revision_plan`.                                       |
| `waiting_for_scene_plan` / `submit_scene_plan`  | Correct and resubmit the complete Scene Plan.                                                               |
| `waiting_for_agent_review` / `submit_review`    | Inspect current evidence and submit a review bound to its IDs.                                              |
| `waiting_for_user_decision` / `submit_decision` | Present only returned allowed actions and submit the user's choice.                                         |
| `running` / `advance`                           | Advance once.                                                                                               |
| `running` / `wait`                              | Use `wait_editor_workflow`; repeat bounded waits only when another wait action is returned.                 |
| `interrupted` / `resume`                        | Call `resume_editor_workflow` before any other operation.                                                   |
| `failed`, `cancelled`, `completed`              | Terminal. Do not resume or mutate the run. Start revision only for a requested change to a completed scene. |

`cleanupPending=true` on a cancelled run does not make the run active again. The
Controller has already released its lease and session hold. After the environment
recovers, repeating `cancel_editor_workflow` retries only persisted asynchronous-task
cancellation and deferred session cleanup; it does not resume workflow execution.

## Manifest And Prompt Rejections

Some manifest validation failures are returned directly as tool errors rather than
persisted `errors[]`. Correct the named field using `contracts.md`.

| Code or message                   | Meaning                                                                                          | Corrective action                                                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_MODEL_PROMPT_TOO_LONG`    | Initial model prompt exceeds 800 characters.                                                     | Rewrite it as a complete positive asset prompt at or below 700 characters.                                            |
| `EDITOR_REVISION_PROMPT_REQUIRED` | A failed model-quality review did not provide a replacement prompt.                              | Resubmit the same review with a complete `revisionPrompt`; do not append feedback history.                            |
| `EDITOR_REVISION_PROMPT_TOO_LONG` | Replacement prompt exceeds 800 characters.                                                       | Rewrite at or below 700 characters while preserving accepted intent.                                                  |
| unsupported manifest schema       | `schemaVersion` is not `2.0`.                                                                    | Use the production Manifest schema from `contracts.md`.                                                               |
| duplicate or empty item ID        | IDs are blank or collide across model, primitive, material, or enhancement work.                 | Assign unique stable ASCII IDs and update all references.                                                             |
| invalid semantic name             | An Editor name violates the stable ASCII identifier pattern.                                     | Replace it with `^[A-Za-z_][A-Za-z0-9_]*$`; keep display prose in prompts/rationales.                                 |
| unknown model material target     | `targetModelId` does not match a Manifest model.                                                 | Correct the ID or remove the material work.                                                                           |
| material target count error       | Both/neither material target fields were provided.                                               | Set exactly one of `targetModelId` or `targetPrimitiveId`.                                                            |
| non-absolute path                 | Asset, material output, runtime node, or expected scene path violates its path rule.             | Submit the exact required absolute path.                                                                              |
| invalid vector/color/dimension    | A numeric field is missing, non-finite, non-positive where required, or outside normalized RGBA. | Correct the exact component; do not substitute guessed geometry.                                                      |
| missing capability                | Required generation, import, or material authoring is not exposed.                               | Follow the retry action. After three attempts, present the Controller's user-decision actions; do not call backend APIs directly. |

## Material Review Rejections

| Code or condition                                   | Meaning                                                                     | Corrective action                                                                                                                                            |
| --------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `EDITOR_MATERIAL_REVISION_REQUIRED`                 | A failed material review would otherwise repeat the same authoring request. | Resubmit the current review with `materialRevision` changing the prompt, structured properties, or both.                                                     |
| `EDITOR_MATERIAL_REVISION_UNCHANGED`                | The proposed revision produces the same effective material request.         | Change an acceptance-relevant value; do not spend another attempt on identical input.                                                                        |
| `EDITOR_MATERIAL_REVISION_CONFLICT`                 | `materialRevision` was supplied for a passing or non-material review.       | Remove it and submit only the fields valid for the current gate.                                                                                             |
| repeated preview hash                               | The Editor produced the same visual result for the revised request.         | Verify that structured properties were changed. If they were, report an Editor material-authoring defect instead of rewording the same request indefinitely. |
| intended color/emission absent                      | Free-text intent did not map to actual shader values.                       | Set explicit `properties.color` and `properties.emissiveStrength` in the Manifest or material revision.                                                      |
| MaterialX validation error with a compiled fallback | The Editor generated an invalid graph but still exposed a preview as ready. | Fail visual review, preserve the exact Editor log/USDA evidence, and revise through structured properties; never commit or report the fallback as accepted.  |

## Scene Plan Rejections

`EDITOR_SCENE_PLAN_INVALID` is a retryable wrapper. Its message contains the precise
validation failure. Keep the workflow at `waiting_for_scene_plan`, correct the full
Plan, and call `submit_editor_scene_plan` again.

| Code or detail                          | Meaning                                                                                                     | Corrective action                                                                                |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `EDITOR_SCENE_PLAN_REQUIRED`            | Advance was called before a valid Plan was accepted.                                                        | Submit a valid Plan; do not advance again first.                                                 |
| fingerprint mismatch / stale plan       | Plan fingerprint differs from current scene state.                                                          | Query/refresh scene context, rebuild the Plan against the new fingerprint, and resubmit.         |
| unknown or duplicate model              | Placement references an absent model or repeats one.                                                        | Use each current Manifest model ID exactly once.                                                 |
| missing models                          | One or more current Manifest models have no placement.                                                      | Add exactly one final placement for every listed model.                                          |
| unresolved model                        | The Controller has no managed entity path for the model.                                                    | Do not invent a path. Return to the current workflow action or report the missing managed asset. |
| invalid placement vector/scale          | Position/scale is malformed; scale is not positive.                                                         | Correct finite coordinates and positive scale.                                                   |
| incompatible orientation fields         | Legacy `rotationEuler` and `orientation` were both submitted, or orientation mode lacks its required value. | Use one orientation mechanism. Supply yaw for `yaw_from_imported` or Euler for `absolute_euler`. |
| missing rationale                       | Placement or plan-native primitive has no rationale.                                                        | Add a non-empty rationale grounded in current bounds and requested relationships.                |
| unknown primitive material target       | A Manifest material points to a primitive omitted from the final Plan.                                      | Add the intended primitive to `plan.primitives` or correct/remove the material target.           |
| duplicate primitive ID/name             | Primitive collides with a model/primitive ID or a sibling name.                                             | Rename the stable ID/name and update material/group references.                                  |
| invalid primitive                       | Unsupported type, non-positive dimensions, invalid transform/color, or empty acceptance.                    | Correct the field using the contract; do not move primitive geometry back to the Manifest.       |
| `EDITOR_SCENE_GROUP_IDENTIFIER_INVALID` | Group ID/name violates the ASCII pattern.                                                                   | Use the suggested stable identifier and update `parentGroupId` references.                       |
| unknown group parent                    | `parentGroupId` does not name a submitted group.                                                            | Correct/remove the parent reference.                                                             |
| group hierarchy cycle                   | Parent groups form a cycle.                                                                                 | Rebuild an acyclic hierarchy.                                                                    |
| unknown group member                    | Model, instance, or primitive reference is not managed/current.                                             | Use an ID from `scenePlanningContext` or this Plan.                                              |
| member in multiple groups               | One managed entity is claimed by more than one group.                                                       | Keep exactly one owning group.                                                                   |
| duplicate sibling/member name           | Resulting hierarchy would contain ambiguous siblings.                                                       | Rename the group/primitive/instance or change grouping.                                          |
| another scene root                      | A referenced entity is outside the current managed root.                                                    | Remove it from the Plan; never cross scene roots.                                                |
| group definition cannot change          | Authored hierarchy exists and the submitted group definition changed unexpectedly.                          | Preserve accepted groups or start an explicit revision/recomposition route.                      |
| required runtime node omitted           | The projected create-mode hierarchy does not satisfy `scenePlanningContext.runtimeNodes`.                   | Preserve valid existing groups, add the missing node/group at the exact declared path and parent, and resubmit the complete Plan. |

After any rejected Plan, use `errors[].message` to correct the named issue. Do not
discard valid placements, primitives, or groups unrelated to that issue.

## Review Rejections

| Code                                         | Meaning                                                                                     | Corrective action                                                                                                                                                                |
| -------------------------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_REVIEW_SCHEMA_INVALID`               | Enum, evidence reference, confidence, or conditional review field is invalid.               | Rebuild the review from current evidence using `contracts.md`.                                                                                                                   |
| `EDITOR_REVIEW_VIEW_MISSING`                 | A required evidence view was omitted.                                                       | Inspect and include every required current view.                                                                                                                                 |
| `EDITOR_REVIEW_VIEW_FAILED`                  | One or more views are failed but the whole review contract is inconsistent.                 | Use semantic `fail` and structured blocking evidence, or correct an unsupported failed view claim.                                                                               |
| `EDITOR_REVIEW_VERDICT_CONFLICT`             | A failed view conflicts with a pass/inconclusive semantic verdict.                          | Align the overall verdict and findings with the per-view evidence.                                                                                                               |
| `EDITOR_REVIEW_BLOCKING_FINDING_CONFLICT`    | Findings were supplied for a non-fail verdict.                                              | Remove findings or change the verdict only when evidence supports failure.                                                                                                       |
| `EDITOR_REVIEW_BLOCKING_EVIDENCE_REQUIRED`   | A fail verdict has no structured finding.                                                   | Add at least one valid `blockingFinding`.                                                                                                                                        |
| `EDITOR_REVIEW_BLOCKING_CATEGORY_INVALID`    | Finding category is outside the allowlist.                                                  | Choose the exact supported category matching the observable consequence.                                                                                                         |
| `EDITOR_REVIEW_BLOCKING_EVIDENCE_INVALID`    | Finding lacks summary/view IDs or cites an uninspected, absent, unframed, or non-fail view. | Cite only valid failed current evidence and provide a concrete summary.                                                                                                          |
| `EDITOR_REVIEW_MULTIVIEW_EVIDENCE_REQUIRED`  | A physical/depth finding has insufficient independent views.                                | Cite two distinct supporting failed views.                                                                                                                                       |
| `EDITOR_REVIEW_REQUIREMENT_UNVERIFIED`       | Explicit requirement finding does not quote an active criterion.                            | Copy the exact relevant Manifest acceptance criterion.                                                                                                                           |
| `EDITOR_MODEL_FRONT_UNVERIFIED`              | Active front policy was not satisfied.                                                      | Reinspect all model views and submit a supported front assessment.                                                                                                               |
| `EDITOR_MODEL_ORIENTATION_UNVERIFIED`        | Active orientation policy was not satisfied.                                                | Submit an allowed directional or evidence-backed non-directional result.                                                                                                         |
| `EDITOR_REQUIRED_REUSE_REVIEW_REJECTED`      | A required reusable asset received a failed quality or unresolved direction review.         | Keep the imported asset and current review gate. Resubmit direction-only evidence, using `orientation.verdict="ambiguous"` when appropriate; never provide a replacement prompt. |
| `EDITOR_REQUIRED_REUSE_GENERATION_FORBIDDEN` | A required reusable asset reached replacement generation through stale or invalid state.    | Follow the retry action, then present the returned user decision after three attempts. Do not generate or substitute another asset.                                            |
| `EDITOR_EVIDENCE_ASSET_STALE`                | Model evidence no longer matches the accepted asset.                                        | Follow recapture action; do not review stale images.                                                                                                                             |
| `EDITOR_EVIDENCE_SCENE_STALE`                | Scene evidence no longer matches the current scene.                                         | Recapture current scene evidence.                                                                                                                                                |

Do not turn optional appearance preferences into blocking findings. Do not fix a
review rejection by weakening an active acceptance criterion.

## Revision Rejections

| Code                                        | Meaning                                                                                                             | Corrective action                                                                                                                                                             |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_REVISION_REQUIRED`                  | A production modify request targets a completed managed scene.                                                      | Continue the converted run as revision using returned `baseRunId` and `revisionContext`; do not retry production modify.                                                      |
| `EDITOR_REVISION_STALE`                     | Revision fingerprint no longer matches current scene.                                                               | Read refreshed `revisionContext`, rebuild operations, and resubmit.                                                                                                           |
| `EDITOR_REVISION_USER_CHANGE_CONFLICT`      | Target changed outside the parent workflow.                                                                         | Preserve it by default. Ask the user before setting `allowUserModifiedTargets=true`.                                                                                          |
| `EDITOR_REVISION_TARGET_MISSING`            | Requested target was deleted by the user.                                                                           | Remove/update the operation; regenerate/add only when explicitly requested.                                                                                                   |
| `EDITOR_REVISION_SCENE_MISMATCH`            | Active scene differs from the parent's accepted final scene.                                                        | Open/reconnect the exact `finalSceneSnapshot.scenePath`; never fall back to production modify.                                                                                |
| `EDITOR_REVISION_SCENE_FINGERPRINT_MISSING` | Current scene cannot provide identity evidence.                                                                     | Reinspect/reconnect Editor; do not submit speculative revision operations.                                                                                                    |
| repeated/unknown revision target            | Operation duplicates a target or references an unknown model/primitive/entity.                                      | Use current `revisionContext` IDs/paths and one operation per target.                                                                                                         |
| empty transform/update operation            | No mutable value was supplied.                                                                                      | Add at least one allowed field or remove the no-op operation.                                                                                                                 |
| inherited target-height/scale conflict      | A legacy or stale Controller derived both `targetHeightMeters` and a current non-unit scale for an inherited model. | Keep the same revision and resubmit after updating the Controller. Do not remove/re-import models, create a replacement scene, or bypass `add_primitive` with direct scripts. |

## Scene Mutation And Evidence Rejections

| Code or condition                         | Meaning                                                     | Corrective action                                                                    |
| ----------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| mutation fingerprint mismatch             | Mutation is based on stale scene state.                     | Query the scene and rebuild against the returned fingerprint.                        |
| unmanaged deletion decision               | Removal targets unmanaged content.                          | Show exact paths to the user; submit `authorize_scene_mutation` only after approval. |
| mixed remove operation                    | Remove was combined with other mutations.                   | Submit that removal alone.                                                           |
| `EDITOR_SCENE_EVIDENCE_INVALID`           | Request has invalid IDs, members, context, or views.        | Rebuild from current scene evidence using managed member IDs.                        |
| `EDITOR_SCENE_EVIDENCE_STALE`             | `baseEvidenceId` is not the current pending scene evidence. | Use current `nextAction.evidenceId`.                                                 |
| `EDITOR_SCENE_EVIDENCE_NOT_AVAILABLE`     | No active scene review can accept supplemental evidence.    | Follow current `nextAction`; do not request evidence out of phase.                   |
| `EDITOR_SCENE_EVIDENCE_LIMIT`             | Request/view budget is exhausted.                           | Review available evidence or submit inconclusive/fail as supported; do not loop.     |
| `EDITOR_SCENE_EVIDENCE_CAPTURE_FAILED`    | Supplemental capture failed.                                | Follow retry/decision state; preserve the primary 6+1 evidence.                      |
| `EDITOR_CAPTURE_ISOLATION_RESTORE_FAILED` | Visibility could not be restored safely.                    | Stop mutation/review claims and follow the Controller blocker.                       |

## Waiting, Authentication, Provider, And Session Errors

| Code                                         | Meaning                                                                                     | Corrective action                                                                                                                                                                                                                                                       |
| -------------------------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_API_KEY_REQUIRED`                    | Provider authentication is missing and GUI setup was opened.                                | Tell the user to configure/save the key in Editor. Never request the secret. After confirmation submit `retry_after_authentication`.                                                                                                                                    |
| `MODEL_PROVIDER_REQUEST_FAILED`              | External provider rejected/failed the request.                                              | Record returned provider status/code/message and follow `advance` for the first three attempts. Only after Controller returns `submit_decision` ask the user to authorize `authorize_workflow_retry`, inspect in GUI, or cancel. |
| `EDITOR_SESSION_INTERRUPTED`                 | Transport or Editor session was lost with a persisted checkpoint.                           | Call `resume_editor_workflow`; do not start a new run.                                                                                                                                                                                                                  |
| `EDITOR_SESSION_RECOVERY_FAILED`             | Automatic same-project recovery was exhausted.                                              | Preserve the run and report the session blocker; after environment recovery call resume.                                                                                                                                                                                |
| `EDITOR_REUSABLE_ASSET_MISSING`              | Required reusable asset cannot be found.                                                    | Provide/correct the explicit asset path or ask the user; never generate a substitute.                                                                                                                                                                                   |
| `EDITOR_REUSABLE_ASSET_IMPORT_FAILED`        | Required local asset import failed.                                                         | Report the Editor failure and retry only after the cause changes.                                                                                                                                                                                                       |
| `EDITOR_REUSABLE_ASSET_IMPORT_TIMEOUT`       | Import exceeded its managed deadline; this alone does not prove the file path is defective. | Preserve the exact `assetPath`, checkpoint, and backend detail, then follow the returned action. Attribute the failure to path scope only with controlled evidence, such as an explicit path rejection or a same-session retry whose only changed variable is the path. |
| `EDITOR_REUSABLE_ASSET_IMPORT_STATE_INVALID` | Persisted import state cannot be reconciled.                                                | Report the state mismatch and use the returned blocker/decision; do not claim another entity.                                                                                                                                                                           |
| `EDITOR_ASSET_IMPORT_DETACHED`               | Cancellation left a backend task detached.                                                  | Treat the run as cancelled and report the detached task; do not reuse it implicitly.                                                                                                                                                                                    |
| `EDITOR_CLEANUP_FAILED`                      | Post-cancellation cleanup failed after the run was durably marked terminal.                 | Keep the run cancelled and report the exact detail. `cleanupPending=true` means cleanup can be retried idempotently by repeating cancel after environment recovery; never resume the cancelled run or assume detached resources are reusable.                           |

## Assembly, Capture, And Final Validation Errors

These are execution/evidence failures, not form fields. Do not bypass the Controller.

| Code family                                                              | Meaning                                                            | Corrective action                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_SCENE_ASSEMBLY_FAILED`                                           | Runtime scene assembly or a postcondition did not converge.       | Use returned `scenePlanningContext.previousPlan` and `reviewFeedback` to correct the named entity, then resubmit the complete Scene Plan. Do not repeatedly advance the same failing plan.                                                               |
| `EDITOR_SCRIPT_BLOCK_TOO_LARGE`                                          | One indivisible assembly block exceeds Editor limit.               | Reduce one oversized group/item operation; do not merely retry.                                                                                                                                                                                       |
| `EDITOR_CAPTURE_TOOL_ERROR`                                              | Screenshot tool failed.                                            | Follow retry/decision state; do not fabricate visual evidence.                                                                                                                                                                                        |
| `EDITOR_CAPTURE_VIEW_MISSING` / `EDITOR_CAPTURE_INVALID`                 | Required capture set is incomplete/invalid.                        | Recapture through the managed workflow.                                                                                                                                                                                                               |
| `EDITOR_CAPTURE_CAMERA_MISALIGNED` / `EDITOR_CAPTURE_FRAMING_UNVERIFIED` | Camera transform or framing is not proven.                         | Recapture; do not review the image as valid.                                                                                                                                                                                                          |
| `EDITOR_CAPTURE_DUPLICATE_IMAGE`                                         | Distinct required views produced duplicate evidence.               | Recapture the affected views.                                                                                                                                                                                                                         |
| `EDITOR_CAPTURE_ISOLATION_MISSING` / `UNAVAILABLE` / `UNVERIFIED`        | Target isolation could not be applied/proven.                      | Follow recapture or blocker; do not infer target quality.                                                                                                                                                                                             |
| `EDITOR_CAPTURE_STATE_NOT_RESTORED`                                      | Capture changed scene state and failed restoration.                | Stop acceptance and follow Controller recovery.                                                                                                                                                                                                       |
| `EDITOR_MODEL_BOUNDS_INVALID`                                            | Model bounds are missing/non-finite.                               | Reinspect or regenerate/import as directed.                                                                                                                                                                                                           |
| `EDITOR_MODEL_BOUNDS_TOO_SMALL` / `TOO_LARGE`                            | Measured bounds violate Manifest limits.                           | Fail review or revise the asset requirement; do not falsify scale.                                                                                                                                                                                    |
| `EDITOR_MODEL_TARGET_HEIGHT_MISMATCH`                                    | Applied target height did not converge.                            | Follow model retry/decision; verify bounds before planning.                                                                                                                                                                                           |
| `EDITOR_HIERARCHY_CYCLE`                                                 | Actual scene hierarchy is cyclic/invalid.                          | Correct hierarchy through a new valid Plan or revision.                                                                                                                                                                                               |
| `EDITOR_RUNTIME_NODE_MISSING` / `EDITOR_RUNTIME_NODE_PARENT_MISMATCH`    | The assembled hierarchy omitted or misplaced a required runtime node. | Follow `submit_scene_plan`, preserve already-authored groups, add or correct the required node, and resubmit the complete Plan in the same run.                                                                                                       |
| Other `EDITOR_RUNTIME_NODE_*`                                            | Runtime-node name or uniqueness contract failed.                      | Correct the Manifest contract in a new production/revision request; use `./...` from the managed scene root or an evidenced absolute path, and never substitute `scene.name` for the root.                                                            |
| `EDITOR_SCENE_IDENTITY_CHANGED`                                          | Active scene changed unexpectedly.                                 | Reconnect the intended scene and refresh state; never package another scene.                                                                                                                                                                          |
| `EDITOR_FINAL_SCENE_FINGERPRINT_CHANGED`                                 | Scene changed after acceptance.                                    | Re-enter scene review/revision; do not package stale acceptance.                                                                                                                                                                                      |
| `EDITOR_DELIVERY_SCENE_MISMATCH`                                         | Packaged entry scene differs from accepted final scene.            | Correct active/entry scene identity and revalidate before packaging.                                                                                                                                                                                  |
| `EDITOR_REQUIRED_ENHANCEMENT_UNSUPPORTED`                                | Required enhancement has no stable capability.                     | Follow the retry action. After three attempts, present only returned user-decision actions; do not emulate it with guessed scripts.                                                                                                                               |
| `EDITOR_REQUIRED_ENHANCEMENT_REVIEW_FAILED`                              | Required enhancement failed review.                                | Correct/retry through the managed flow or report blocker.                                                                                                                                                                                             |
| `EDITOR_ACTIVE_SCENE_NOT_SWITCHED`                                       | Requested scene did not become active.                             | Reconnect/open the exact scene and retry the managed step.                                                                                                                                                                                            |
| `EDITOR_WORKFLOW_ACTION_MISMATCH`                                        | The requested workflow tool did not match the latest `nextAction`. | Keep the unchanged phase, gate, and evidence IDs; invoke the exact returned action. Do not start another run or classify the rejection as a backend failure.                                                                                          |
| `EDITOR_BACKEND_TOOL_ERROR`                                              | A managed Editor backend operation failed.                         | Report exact message/detail and current phase; retry only if Controller marks it retryable.                                                                                                                                                           |
| `EDITOR_WORKFLOW_STEP_FAILED`                                            | A managed step failed; this can include an out-of-sequence call.   | First compare the invoked tool with the immediately preceding `nextAction`. If they mismatch, report an Agent sequencing error and do not blame or retry the backend. Then obey the latest persisted status and retry only when explicitly permitted. |

## Retry Discipline

- Retry only when `retryable=true` or the current `nextAction` explicitly permits it.
- A retry uses the same `run_id`.
- A rejected form is corrected and resubmitted; it is not followed by `advance`.
- A capture retry must not repeat already-applied scene assembly.
- A bounded wait returning another wait is normal; call wait again.
- Retry a recoverable workflow error exactly as returned for up to three Agent
  attempts. After the third failed attempt, stop autonomous retries and present
  the returned user-decision actions. Use `authorize_workflow_retry` only after
  the user explicitly authorizes a new retry batch.
- `inspect_in_gui` only opens or preserves the GUI and leaves the decision gate
  active. After the user saves manual scene adjustments, submit
  `authorize_workflow_retry` when it is offered. For exhausted scene review,
  this returns to managed scene capture without reapplying the accepted Plan.
- Never downgrade required work, change acceptance criteria, delete user changes, or
  switch production/revision mode merely to clear an error.
