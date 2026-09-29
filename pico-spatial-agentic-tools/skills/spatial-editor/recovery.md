# Spatial Editor Workflow Recovery

Read this module after the public Spatial Editor Workflow Run rejects a Handoff,
returns an error, reaches `blocked`, or requests a user decision.

- Read `SKILL.md` for normal workflow selection, task decomposition, and handoff.
- Read `contracts.md` for the corrected form and exact field rules.
- This file owns error interpretation and recovery actions. It does not redefine
  normal forms or scene-design policy.

## Recovery Procedure

1. Read the latest public Run observation, not an earlier tool response or
   Snapshot-only state.
2. Record `runId`, `current`, `next`, `result`, `error`, `artifacts`, and `evidence`.
3. Confirm that the rejected Resume used the immediately preceding
   `next.arguments.task_id` and matched `next.submission.inputSchema`. If it did not, classify the
   failure as an Agent sequencing error; do not attribute it to the Editor backend.
4. Use the most specific code below. The text after the first colon usually names the
   invalid field, entity, gate, or backend failure.
5. Use the latest `next.tool` and fixed `next.arguments`. Never reuse arguments from
   the rejected request or start a replacement Run merely because a retryable
   submission was rejected.
6. Correct only the rejected contract or evidenced defect.
7. Follow `next.action`: execute only the named submit action, or use its bounded wait.
8. After every recovery call, discard the prior observation and parse the newly
   returned Run before doing anything else.
9. If an unknown code appears, follow `error.recovery`, report the exact
   code/message/details, and do not infer success or bypass the Workflow Service.

When public projection is unavailable, inspect the read-only snapshot at
`native-runtime/editor-modules/<module>/recovery.md`. It records the last persisted
phase/status, form attempts, model jobs, active asynchronous task, and recent errors.
Do not edit it or treat it as a submission channel; once transport recovers, continue
the same public Run and current Handoff.

## Status Is Authoritative

| Compact response state                | Required response                                                                                                |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `next.action="submit_scene_spec"`     | Submit the backend-neutral Scene Specification.                                                                  |
| `next.action="submit_produce_models"` | Correct and submit the model-only production plan.                                                               |
| `next.action="submit_revision_plan"`  | Correct and submit the optional linked revision plan.                                                            |
| `next.action="submit_scene_plan"`     | Correct and submit the complete Scene Plan.                                                                      |
| `next.action="submit_review"`         | Inspect current evidence, then submit the bound model/material/scene review.                                     |
| `next.action="submit_user_decision"`  | Present only returned allowed actions and submit the user's choice.                                              |
| `next.action="wait"`                  | Call `next.tool` with its returned `max_wait_ms`; status reads remain observation-only.                          |
| no `next`, terminal `current.status`  | Inspect result/artifacts. For further work, inspect the live project with get-info and start project-based work. |

`cleanupPending=true` on a cancelled Run does not make the Run active again. The
Editor Domain has already released its lease and session hold. After the environment
recovers, repeating `cancel_editor_workflow` retries only persisted asynchronous-task
cancellation and deferred session cleanup; it does not resume workflow execution.

## Form Rejections

| Code                              | Corrective action                                                                                                      |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_HANDOFF_INPUT_INVALID`    | Correct the reported paths using `next.submission.inputSchema`, then call `next.tool` with its latest fixed arguments. |
| `EDITOR_FORM_REJECTED`            | Read the semantic message, correct only that field in the current submission, and resubmit the same Run.               |
| `EDITOR_WORKFLOW_ACTION_MISMATCH` | Discard the stale task and use only the task and revision already returned in `next.arguments`.                        |

## Editor Package Compatibility

`EDITOR_ORTHOGRAPHIC_CAPTURE_UNSUPPORTED` means the connected Editor package does
not expose both `camera_projection` and `camera_orthographic_size` in the live
`get_viewport_screenshot` schema. This is not an Agent-correctable form error.
Do not retry with the same package, remove the parameters, or accept a perspective
image as top-down orthographic evidence. Update to a republished Editor package,
resume the preserved Run, and only then submit `recapture_current`; otherwise cancel
the Run.

## Model Plan, Manifest, And Prompt Rejections

After the Workflow Session exposes the Editor MCP tools, call `get_scene_info`
directly for the active hierarchy and `get_entity_info` directly for target
entities. These read-only queries need no Workflow form or wrapper. If the tools
are unavailable, restore the target project's Editor Session and refresh the MCP
tool list; do not fabricate an observation from an old Snapshot.

Model Production Plan and legacy Manifest validation failures are returned on the
same current Handoff, including structured JSON paths when schema validation fails.
Correct the named field using `contracts.md`.

| Code or message                   | Meaning                                                                                          | Corrective action                                                                                                                             |
| --------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_MODEL_PROMPT_TOO_LONG`    | Initial model prompt exceeds 800 characters.                                                     | Rewrite it as a complete positive asset prompt at or below 700 characters.                                                                    |
| `EDITOR_HANDOFF_INPUT_INVALID`    | The submitted object does not satisfy the current live Handoff Schema.                           | Correct the reported JSON paths and resubmit the same current Handoff; do not advance or start another Run.                                   |
| `EDITOR_MODEL_PLAN_INVALID`       | The model-only Plan could not be converted to the active production Manifest.                    | Correct the versioned model Plan, source strategy, or live-scene selector named in the message and resubmit `editor-model-plan`.              |
| `EDITOR_REVISION_PROMPT_REQUIRED` | A failed model-quality review did not provide a replacement prompt.                              | Resubmit the same review with a complete `revisionPrompt`; do not append feedback history.                                                    |
| `EDITOR_REVISION_PROMPT_TOO_LONG` | Replacement prompt exceeds 800 characters.                                                       | Rewrite at or below 700 characters while preserving accepted intent.                                                                          |
| unsupported manifest schema       | `schemaVersion` is not `2.0`.                                                                    | Use the production Manifest schema from `contracts.md`.                                                                                       |
| duplicate or empty item ID        | IDs are blank or collide across model, primitive, material, or enhancement work.                 | Assign unique stable ASCII IDs and update all references.                                                                                     |
| invalid semantic name             | An Editor name violates the stable ASCII identifier pattern.                                     | Replace it with `^[A-Za-z_][A-Za-z0-9_]*$`; keep display prose in prompts/rationales.                                                         |
| unknown model material target     | `targetModelId` does not match a Manifest model.                                                 | Correct the ID or remove the material work.                                                                                                   |
| material target count error       | Both/neither material target fields were provided.                                               | Set exactly one of `targetModelId` or `targetPrimitiveId`.                                                                                    |
| invalid path                      | Asset or material output is not absolute, or a runtime-node path is not absolute/`./`-relative.  | Correct the named path. For `scene.expectedPath`, copy the exact active-scene value returned by `get_scene_info`; it may be project-relative. |
| invalid vector/color/dimension    | A numeric field is missing, non-finite, non-positive where required, or outside normalized RGBA. | Correct the exact component; do not substitute guessed geometry.                                                                              |
| missing capability                | Required generation, import, or material authoring is not exposed.                               | Follow the current public state. After three attempts, present the user-decision Handoff actions; do not call backend APIs directly.          |

## Material Review Rejections

| Code or condition                                   | Meaning                                                                     | Corrective action                                                                                                                                            |
| --------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `EDITOR_MATERIAL_REVISION_REQUIRED`                 | A failed material review would otherwise repeat the same authoring request. | Resubmit the current review with `materialRevision` changing the prompt, structured properties, or both.                                                     |
| `EDITOR_MATERIAL_REVISION_UNCHANGED`                | The proposed revision produces the same effective material request.         | Change an acceptance-relevant value; do not spend another attempt on identical input.                                                                        |
| `EDITOR_MATERIAL_PREVIEW_UNCHANGED`                 | The new material capture has the same image hash as a prior attempt.        | Let the workflow return to material authoring, then change the structured properties or USDA before recapturing.                                             |
| `EDITOR_MATERIAL_REVISION_CONFLICT`                 | `materialRevision` was supplied for a passing or non-material review.       | Remove it and submit only the fields valid for the current gate.                                                                                             |
| `EDITOR_MATERIAL_EVIDENCE_REVISION_REQUIRED`        | Material recapture would repeat the same camera and visibility state.       | Submit a changed `evidenceRevision` with camera direction, target, or contextual visible entity paths.                                                       |
| `EDITOR_MATERIAL_EVIDENCE_REVISION_UNCHANGED`       | The effective evidence revision is identical to the previous one.           | Change an evidence-relevant field; the rejected input does not consume capture budget.                                                                       |
| `EDITOR_MATERIAL_EVIDENCE_REVISION_STALE`           | The revision is no longer bound to current material/scene evidence.         | Read the latest Run and submit against its current decision gate.                                                                                            |
| `EDITOR_MATERIAL_EVIDENCE_VISIBILITY_INVALID`       | A requested visible entity is invalid or absent from the managed scene.     | Use unique absolute entity paths from current scene inspection.                                                                                              |
| repeated preview hash                               | The Editor produced the same visual result for the revised request.         | Verify that structured properties were changed. If they were, report an Editor material-authoring defect instead of rewording the same request indefinitely. |
| intended color/emission absent                      | Free-text intent did not map to actual shader values.                       | Set explicit `properties.color` and `properties.emissiveStrength` in the Manifest or material revision.                                                      |
| MaterialX validation error with a compiled fallback | The Editor generated an invalid graph but still exposed a preview as ready. | Fail visual review, preserve the exact Editor log/USDA evidence, and revise through structured properties; never commit or report the fallback as accepted.  |

## Scene Plan Rejections

`EDITOR_SCENE_PLAN_INVALID` is a retryable wrapper. Its message contains the precise
validation failure. Preserve the current waiting Run, correct the full Plan, and
Resume the current `editor-scene-plan` Handoff again.

| Code or detail                          | Meaning                                                                                                     | Corrective action                                                                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_SCENE_PLAN_REQUIRED`            | Advance was called before a valid Plan was accepted.                                                        | Submit a valid Plan; do not advance again first.                                                                                   |
| fingerprint mismatch / stale plan       | Plan fingerprint differs from current scene state.                                                          | Query/refresh scene context, rebuild the Plan against the new fingerprint, and resubmit.                                           |
| unknown or duplicate model              | Placement references an absent model or repeats one.                                                        | Use each current Manifest model ID exactly once.                                                                                   |
| missing models                          | One or more current Manifest models have no placement.                                                      | Add exactly one final placement for every listed model.                                                                            |
| unresolved model                        | The Editor Domain has no managed entity path for the model.                                                 | Do not invent a path. Return to the current public state or report the missing managed asset.                                      |
| invalid placement vector/scale          | Position/scale is malformed; scale is not positive.                                                         | Correct finite coordinates and positive scale.                                                                                     |
| incompatible orientation fields         | Legacy `rotationEuler` and `orientation` were both submitted, or orientation mode lacks its required value. | Use one orientation mechanism. Supply yaw for `yaw_from_imported` or Euler for `absolute_euler`.                                   |
| missing rationale                       | Placement or plan-native primitive has no rationale.                                                        | Add a non-empty rationale grounded in current bounds and requested relationships.                                                  |
| duplicate/invalid instance identity     | A planned instance repeats an `instanceId`/name or uses a non-stable identifier.                            | Give every additional occurrence a unique ASCII `instanceId` and Editor entity `name`.                                             |
| unknown instance source                 | `sourceModelId` does not identify an accepted model asset.                                                  | Use a model ID from the current `scenePlanningContext.models`; do not add a duplicate Model Production Plan item solely for reuse. |
| unknown primitive material target       | A Manifest material points to a primitive omitted from the final Plan.                                      | Add the intended primitive to `plan.primitives` or correct/remove the material target.                                             |
| duplicate primitive ID/name             | Primitive collides with a model/primitive ID or a sibling name.                                             | Rename the stable ID/name and update material/group references.                                                                    |
| invalid primitive                       | Unsupported type, non-positive dimensions, invalid transform/color, or empty acceptance.                    | Correct the field using the contract; do not move primitive geometry back to the Manifest.                                         |
| unknown removal target                  | `removals` references a model, instance, or primitive not managed by the current Run.                       | Use an ID exposed by the latest Scene Planning Context; never submit an arbitrary entity path.                                     |
| retained and removed                    | The same scene node remains in placements/worklists/groups while also listed in `removals`.                 | Remove it from the new complete Plan or remove the deletion request.                                                               |
| `EDITOR_SCENE_GROUP_IDENTIFIER_INVALID` | Group ID/name violates the ASCII pattern.                                                                   | Use the suggested stable identifier and update `parentGroupId` references.                                                         |
| unknown group parent                    | `parentGroupId` does not name a submitted group.                                                            | Correct/remove the parent reference.                                                                                               |
| group hierarchy cycle                   | Parent groups form a cycle.                                                                                 | Rebuild an acyclic hierarchy.                                                                                                      |
| unknown group member                    | Model, instance, or primitive reference is not managed/current.                                             | Use an ID from `scenePlanningContext` or this Plan.                                                                                |
| member in multiple groups               | One managed entity is claimed by more than one group.                                                       | Keep exactly one owning group.                                                                                                     |
| duplicate sibling/member name           | Resulting hierarchy would contain ambiguous siblings.                                                       | Rename the group/primitive/instance or change grouping.                                                                            |
| another scene root                      | A referenced entity is outside the current managed root.                                                    | Remove it from the Plan; never cross scene roots.                                                                                  |
| group definition cannot change          | Authored hierarchy exists and the submitted group definition changed unexpectedly.                          | Preserve accepted groups or start an explicit revision/recomposition route.                                                        |
| required runtime node omitted           | The projected create-mode hierarchy does not satisfy `scenePlanningContext.runtimeNodes`.                   | Preserve valid existing groups, add the missing node/group at the exact declared path and parent, and resubmit the complete Plan.  |

After any rejected Plan, use `errors[].message` to correct the named issue. Do not
discard valid placements, instances, primitives, or groups unrelated to that issue.
Form validation attempts do not consume backend retry budget and remain on the same
`editor-scene-plan` Handoff.

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
| `EDITOR_REQUIRED_REUSE_GENERATION_FORBIDDEN` | A required reusable asset reached replacement generation through stale or invalid state.    | Follow the retry action, then present the returned user decision after three attempts. Do not generate or substitute another asset.                                              |
| `EDITOR_EVIDENCE_ASSET_STALE`                | Model evidence no longer matches the accepted asset.                                        | Follow recapture action; do not review stale images.                                                                                                                             |
| `EDITOR_EVIDENCE_SCENE_STALE`                | Scene evidence no longer matches the current scene.                                         | Recapture current scene evidence.                                                                                                                                                |

Do not turn optional appearance preferences into blocking findings. Do not fix a
review rejection by weakening an active acceptance criterion.
Every failed final scene review returns to `editor-scene-plan`, including the third
and later revision. Use the returned `previousPlan`, `reviewFeedback`, current
fingerprint, and current evidence to submit a corrected complete Plan.

## Revision Rejections

| Code                                        | Meaning                                                                                                     | Corrective action                                                                                                                                                                 |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_REVISION_REQUIRED`                  | Legacy runtime forced a delivered scene into revision.                                                      | Update the runtime. Current project-based work uses live get-info and production modify without a completed parent.                                                               |
| `EDITOR_REVISION_STALE`                     | Revision fingerprint no longer matches current scene.                                                       | Read the refreshed revision planning context from the latest Handoff instructions, rebuild operations, and resubmit.                                                              |
| `EDITOR_REVISION_USER_CHANGE_CONFLICT`      | Target changed outside the parent workflow.                                                                 | Preserve it by default. Ask the user before setting `allowUserModifiedTargets=true`.                                                                                              |
| `EDITOR_REVISION_TARGET_MISSING`            | Requested target was deleted by the user.                                                                   | Remove/update the operation; regenerate/add only when explicitly requested.                                                                                                       |
| `EDITOR_REVISION_SCENE_MISMATCH`            | Active scene differs from the parent's accepted final scene.                                                | Open/reconnect the exact scene path in the latest revision Handoff instructions; never fall back to production modify.                                                            |
| `EDITOR_REVISION_SCENE_FINGERPRINT_MISSING` | Current scene cannot provide identity evidence.                                                             | Reinspect/reconnect Editor; do not submit speculative revision operations.                                                                                                        |
| repeated/unknown revision target            | Operation duplicates a target or references an unknown model/primitive/entity.                              | Use IDs and paths from the latest revision Handoff instructions and one operation per target.                                                                                     |
| empty transform/update operation            | No mutable value was supplied.                                                                              | Add at least one allowed field or remove the no-op operation.                                                                                                                     |
| inherited target-height/scale conflict      | Legacy private state derived both `targetHeightMeters` and a current non-unit scale for an inherited model. | Keep the same revision Run and report the incompatible state. Do not remove/re-import models, create a replacement scene, or bypass the public Handoff with direct backend calls. |

## Supplemental Evidence Rejections

| Code or condition                         | Meaning                                                     | Corrective action                                                                |
| ----------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `EDITOR_SCENE_EVIDENCE_INVALID`           | Request has invalid IDs, members, context, or views.        | Rebuild from current scene evidence using managed member IDs.                    |
| `EDITOR_SCENE_EVIDENCE_STALE`             | `baseEvidenceId` is not the current pending scene evidence. | Use the evidence ID from the latest public Handoff instructions and Snapshot.    |
| `EDITOR_SCENE_EVIDENCE_NOT_AVAILABLE`     | No active scene review can accept supplemental evidence.    | Follow the current public state; do not request evidence out of phase.           |
| `EDITOR_SCENE_EVIDENCE_LIMIT`             | Request/view budget is exhausted.                           | Review available evidence or submit inconclusive/fail as supported; do not loop. |
| `EDITOR_SCENE_EVIDENCE_CAPTURE_FAILED`    | Supplemental capture failed.                                | Follow retry/decision state; preserve the primary 6+1 evidence.                  |
| `EDITOR_CAPTURE_ISOLATION_RESTORE_FAILED` | Visibility could not be restored safely.                    | Stop review claims and follow the public Run blocker.                            |

## Waiting, Authentication, Provider, And Session Errors

| Code                                         | Meaning                                                                                     | Corrective action                                                                                                                                                                                                                                                       |
| -------------------------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_API_KEY_REQUIRED`                    | Provider authentication is missing and GUI setup was opened.                                | Tell the user to configure/save the key in Editor. Never request the secret. After confirmation submit `retry_after_authentication`.                                                                                                                                    |
| `MODEL_PROVIDER_REQUEST_FAILED`              | External provider rejected/failed the request.                                              | Record returned provider status/code/message and let the public Worker perform allowed retries. Only when the Run requests `editor-user-decision` ask the user to authorize `authorize_workflow_retry`, inspect in GUI, or cancel.                                      |
| `EDITOR_SESSION_INTERRUPTED`                 | Transport or Editor session was lost with a persisted checkpoint.                           | Preserve the public Run, read its latest state, and submit only a returned Handoff; do not start a new Run.                                                                                                                                                             |
| `EDITOR_SESSION_RECOVERY_FAILED`             | Automatic same-project recovery was exhausted.                                              | Preserve the run and report the session blocker; after environment recovery call resume.                                                                                                                                                                                |
| `EDITOR_REUSABLE_ASSET_MISSING`              | Required reusable asset cannot be found.                                                    | Provide/correct the explicit asset path or ask the user; never generate a substitute.                                                                                                                                                                                   |
| `EDITOR_REUSABLE_ASSET_IMPORT_FAILED`        | Required local asset import failed.                                                         | Report the Editor failure and retry only after the cause changes.                                                                                                                                                                                                       |
| `EDITOR_REUSABLE_ASSET_IMPORT_TIMEOUT`       | Import exceeded its managed deadline; this alone does not prove the file path is defective. | Preserve the exact `assetPath`, checkpoint, and backend detail, then follow the returned action. Attribute the failure to path scope only with controlled evidence, such as an explicit path rejection or a same-session retry whose only changed variable is the path. |
| `EDITOR_REUSABLE_ASSET_IMPORT_STATE_INVALID` | Persisted import state cannot be reconciled.                                                | Report the state mismatch and use the returned blocker/decision; do not claim another entity.                                                                                                                                                                           |
| `EDITOR_ASSET_IMPORT_DETACHED`               | Cancellation left a backend task detached.                                                  | Treat the run as cancelled and report the detached task; do not reuse it implicitly.                                                                                                                                                                                    |
| `EDITOR_CLEANUP_FAILED`                      | Post-cancellation cleanup failed after the run was durably marked terminal.                 | Keep the run cancelled and report the exact detail. `cleanupPending=true` means cleanup can be retried idempotently by repeating cancel after environment recovery; never resume the cancelled run or assume detached resources are reusable.                           |

## Assembly, Capture, And Final Validation Errors

These are execution/evidence failures, not form fields. Do not bypass the Workflow
Service or its Drivers.

| Code family                                                              | Meaning                                                                                           | Corrective action                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EDITOR_SCENE_ASSEMBLY_FAILED`                                           | Runtime scene assembly or a postcondition did not converge.                                       | Use returned `scenePlanningContext.previousPlan` and `reviewFeedback` to correct the named entity, then resubmit the complete Scene Plan. Do not repeatedly advance the same failing plan.                                                         |
| `EDITOR_SCRIPT_BLOCK_TOO_LARGE`                                          | One indivisible assembly block exceeds Editor limit.                                              | Reduce one oversized group/item operation; do not merely retry.                                                                                                                                                                                    |
| `EDITOR_CAPTURE_TOOL_ERROR`                                              | Screenshot tool failed.                                                                           | Follow retry/decision state; do not fabricate visual evidence.                                                                                                                                                                                     |
| `EDITOR_CAPTURE_VIEW_MISSING` / `EDITOR_CAPTURE_INVALID`                 | Required capture set is incomplete/invalid.                                                       | Recapture through the managed workflow.                                                                                                                                                                                                            |
| `EDITOR_CAPTURE_CAMERA_MISALIGNED` / `EDITOR_CAPTURE_FRAMING_UNVERIFIED` | Camera transform or framing is not proven.                                                        | Recapture; do not review the image as valid.                                                                                                                                                                                                       |
| `EDITOR_CAPTURE_DUPLICATE_IMAGE`                                         | Distinct required views produced duplicate evidence.                                              | Recapture the affected views.                                                                                                                                                                                                                      |
| `EDITOR_CAPTURE_ISOLATION_MISSING` / `UNAVAILABLE` / `UNVERIFIED`        | Target isolation could not be applied/proven.                                                     | Follow recapture or blocker; do not infer target quality.                                                                                                                                                                                          |
| `EDITOR_CAPTURE_STATE_NOT_RESTORED`                                      | Capture changed scene state and failed restoration.                                               | Stop acceptance and follow the current public recovery state.                                                                                                                                                                                      |
| `EDITOR_MODEL_BOUNDS_INVALID`                                            | Model bounds are missing/non-finite.                                                              | Reinspect or regenerate/import as directed.                                                                                                                                                                                                        |
| `EDITOR_MODEL_BOUNDS_TOO_SMALL` / `TOO_LARGE`                            | Measured bounds violate Manifest limits.                                                          | Fail review or revise the asset requirement; do not falsify scale.                                                                                                                                                                                 |
| `EDITOR_MODEL_TARGET_HEIGHT_MISMATCH`                                    | Applied target height did not converge.                                                           | Follow model retry/decision; verify bounds before planning.                                                                                                                                                                                        |
| `EDITOR_HIERARCHY_CYCLE`                                                 | Actual scene hierarchy is cyclic/invalid.                                                         | Correct hierarchy through a new valid Plan or revision.                                                                                                                                                                                            |
| `EDITOR_RUNTIME_NODE_MISSING` / `EDITOR_RUNTIME_NODE_PARENT_MISMATCH`    | The assembled hierarchy omitted or misplaced a required runtime node.                             | Follow `submit_scene_plan`, preserve already-authored groups, add or correct the required node, and resubmit the complete Plan in the same run.                                                                                                    |
| Other `EDITOR_RUNTIME_NODE_*`                                            | Runtime-node name or uniqueness contract failed.                                                  | Correct the Manifest contract in a new production/revision request; use `./...` from the managed scene root or an evidenced absolute path, and never substitute `scene.name` for the root.                                                         |
| `EDITOR_SCENE_IDENTITY_CHANGED`                                          | Active scene changed unexpectedly.                                                                | Reconnect the intended scene and refresh state; never package another scene.                                                                                                                                                                       |
| `EDITOR_FINAL_SCENE_FINGERPRINT_CHANGED`                                 | Scene changed after acceptance.                                                                   | Re-enter scene review/revision; do not package stale acceptance.                                                                                                                                                                                   |
| `EDITOR_DELIVERY_SCENE_MISMATCH`                                         | Packaged entry scene differs from accepted final scene.                                           | Correct active/entry scene identity and revalidate before packaging.                                                                                                                                                                               |
| `EDITOR_DELIVERY_PROVENANCE_INVALID`                                     | Delivery lacks matching managed Run, accepted revision, scene fingerprint, or passing gate proof. | Do not report completion or reuse the package as managed output; resume the active Run when possible, otherwise start a new managed Run.                                                                                                           |
| `EDITOR_RUN_TERMINAL`                                                    | A write or resume was attempted after the Run became terminal.                                    | Treat the terminal Result as immutable and start a new managed Run against the live project for further changes.                                                                                                                                   |
| `EDITOR_REQUIRED_ENHANCEMENT_UNSUPPORTED`                                | Required enhancement has no stable capability.                                                    | Follow the retry action. After three attempts, present only returned user-decision actions; do not emulate it with guessed scripts.                                                                                                                |
| `EDITOR_REQUIRED_ENHANCEMENT_REVIEW_FAILED`                              | Required enhancement failed review.                                                               | Correct/retry through the managed flow or report blocker.                                                                                                                                                                                          |
| `EDITOR_ACTIVE_SCENE_NOT_SWITCHED`                                       | Requested scene did not become active.                                                            | Reconnect/open the exact scene and retry the managed step.                                                                                                                                                                                         |
| `EDITOR_WORKFLOW_ACTION_MISMATCH`                                        | The submitted task did not match the latest public Handoff.                                       | Keep the unchanged Run and evidence IDs; read and submit the exact current Handoff. Do not start another Run or classify the rejection as a backend failure.                                                                                       |
| `EDITOR_BACKEND_TOOL_ERROR`                                              | A managed Editor backend operation failed.                                                        | Report exact message/detail and current public status; retry only when the public Run marks it retryable or exposes an applicable Handoff.                                                                                                         |
| `EDITOR_WORKFLOW_STEP_FAILED`                                            | A managed step failed; this can include an out-of-sequence call.                                  | Compare the submitted task ID with the immediately preceding public Handoff. If they mismatch, report an Agent sequencing error and do not blame or retry the backend. Then obey the latest public state and retry only when explicitly permitted. |

## Cancellation And Cleanup

| Condition                       | Corrective action                                                                                                       |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| cancellation `status=requested` | Call the returned `next.tool`; a wait timeout does not mean cancellation failed.                                        |
| cancellation `status=cancelled` | The Run is terminal. Inspect preserved artifacts before starting new work.                                              |
| `cleanupPending=true`           | Repeat cancellation only after the environment recovers; never resume workflow execution from a cancelled Run.          |
| `WORKFLOW_CANCEL_UNSUPPORTED`   | Report the exact error and stop; do not simulate cancellation by deleting Run files or terminating unrelated processes. |

## Retry Discipline

- Retry only when `error.retryable=true` or `next.action` explicitly permits it.
- A retry uses the fixed arguments returned by the latest `next`.
- A rejected form is corrected and resubmitted; it is not followed by `advance`.
- A capture retry must not repeat already-applied scene assembly.
- A bounded wait returning another wait is normal; call wait again.
- Retry a recoverable workflow error exactly as returned for up to three Agent
  attempts. After the third failed attempt, stop autonomous retries and present
  the returned user-decision actions. Use `authorize_workflow_retry` only after
  the user explicitly authorizes a new retry batch.
- Form corrections and failed final-scene reviews are not backend retries: they stay
  on their current form Handoff until a valid Plan and passing review are accepted.
- `inspect_in_gui` only opens or preserves the GUI and leaves the decision gate
  active. After the user saves manual scene adjustments, submit
  `authorize_workflow_retry` when it is offered. For exhausted scene review,
  this returns to managed scene capture without reapplying the accepted Plan.
- Never downgrade required work, change acceptance criteria, delete user changes, or
  switch production/revision mode merely to clear an error.
