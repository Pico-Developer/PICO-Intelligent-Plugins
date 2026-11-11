# Spatial Editor v7 Recovery

This file owns error interpretation and recovery actions for current v7. Read `contracts.md` for corrections; follow live recovery actions for unlisted errors. For old Scene Plan or blanket light restrictions, verify the Host-selected Skill path and full resource closure against the effective distribution; see Host Skill Consistency in `references/authoring-quality.md`. Repository checks alone do not verify Host loading.

## Recovery Procedure

1. Read the latest public Run observation, not an earlier response or Snapshot-only state. Record root `runId`, `current`, `next`, `result`, `error` and saved artifacts. Replace cached stage/child observations; missing current progress is unknown.
2. Compare failed Resume with preceding `next.arguments.task_id` and live Schema. Task mismatch is sequencing error; required fields absent from Schema indicate contract mismatch.
3. Correct the named field or defect using latest `next.tool`/`next.arguments`; discard old arguments.
4. When no applicable action remains, record the exact code/message/details and assess documented recovery options under Main Agent Recovery Rounds below. Do not infer success or bypass an active Workflow Service.
5. On transport failure, reconnect the same active Run; never edit persisted state.
6. Current Workflow v7 uses default PBR during geometry creation and accepts only current contracts. Obsolete inputs and state are rejected without migration; never edit persisted versions or use old forms to bypass validation.
7. `WORKFLOW_RESUME_STALE` rejects the submission before acceptance. Use fresh `next.arguments` and `next.submission`; submit only if the task still applies, or follow its wait. Normal revision growth is not scene corruption. Never repeat completed Editor operations or send concurrent submissions to repair a stale number.
8. For a current published `system-recovery` Handoff, review its instructions and preserved outputs, then decide whether recovery is appropriate. If so, use `submit_editor_workflow` with the returned task ID/revision, `task_type="recovery"` and `input={}`. Do not invent a recovery task or reopen a terminal Run.

## Main Agent Recovery Rounds

The main Agent must actively resolve confirmed blockers rather than treating an error code
or `retryable=false` as proof that the overall task cannot be completed.
A blocker needs current error, activity, receipt or scene evidence of work that cannot advance;
elapsed time, missing activity and a normal bounded wait alone are insufficient.

For the same confirmed blocker, perform three recovery rounds while the Run remains active:

1. Inspect the latest root observation, the named cause, current Handoff and relevant saved
   scene/operation evidence. Keep an attempt record with the cause, chosen remedy and result.
2. Apply a targeted supported correction through the current Handoff or managed gateway,
   or a documented reconnect/recovery operation. If an option cannot be applied, record its
   specific constraint and assess another documented remedy; do not fabricate an execution
   or repeat an unchanged failed call.
3. Verify whether work can advance and whether the requested scene state was preserved.
   Count the diagnosis, correction and verification together as one round. A resolved blocker
   ends its attempt record; a genuinely different blocker gets its own record.

Normal waits/status reads, automatic Worker retries and successful Handoff progression are
not failed recovery rounds. Keep persisted backend budgets unchanged; this is the main
Agent's recovery budget, not permission to reset asset counters or force an unavailable
Resume. Preserve completed work and avoid duplicate submissions when acceptance is known
or uncertain. After three unsuccessful rounds, cancel the root and follow Cancellation
And Cleanup, then Native Editor Fallback. If Runtime terminates sooner, read its actual
result and proceed to fallback after cleanup instead of attempting terminal Resume.

## Current v7 Gate And Workspace Recovery

- `EDITOR_CAPTURE_ARGUMENT_NOT_READ_ONLY`: use `captureInputSchema` and allowed fit modes in the frozen window.
- `EDITOR_API_SIGNATURE_UNRESOLVED`: report the failed full lookup without guessing/repeating brief; use another documented operation if suitable.
- **Material details:** replay the same ID/arguments with `response_mode="full"` or read `receipt.resultRef`. Concatenate chunk `text` in order. On archive/read errors, inspect receipts; do not repeat completed writes.
- **Frame/camera conflict:** for a candidate overview, remove `entity_path`, `frame`, `camera_mode` and explicit camera controls; retain render/delivery fields for default whole-scene framing. Do not add returned camera defaults back as controls.
  Removing `camera_mode` alone may still fail on entity framing; do not repeat that request. For a specific view, use `frame="none"`, no `entity_path` and schema-supported camera controls.
  See Capture Arguments in `contracts.md`. Reread workspace before retrying with a new operation ID.
- **Material target path rejected:** resolve its absolute Editor path; convert verified hierarchy `Root/...` to `/Root/...`.
- **Submission transport timeout / `EDITOR_WORKFLOW_HANDOFF_ADVANCE_TIMEOUT`:** inspect `error.submissionStatus`; `RESUMED` confirms acceptance and must not be resubmitted. Otherwise acceptance is uncertain; call `get_editor_workflow_status` on the same root Run before deciding whether to submit again.
  Follow `next.action="wait"` during execution/publication even if old Handoff text remains.
  Resubmit only when fresh `next.submission` authorizes input; use its arguments. Reuse the same review only for unchanged candidate/evidence.
  Do not send concurrent Resume calls or infer acceptance from revision growth.
- `WORKFLOW_RESUME_TERMINAL`: read the same root result; this rejects Resume on a terminal Run, not necessarily the submitted review. `outcome="completed"` plus verified delivery means success; failed/blocked/cancelled outcomes keep their own recovery. Never resume a terminal Run.
- `EDITOR_PACKAGE_INTERRUPTED`: inspect preserved outputs and the reported
  interruption before an explicit retry. Normal packaging advances automatically;
  do not send empty submissions while `next.action="wait"`.
- **Unsupported `delivery="file"`:** use `delivery="auto"` if exposed or omit it. Read the live schema once; do not repeat enum probes.
- **Interaction Contract metadata missing:** use the four-field example in `contracts.md`. If the live Schema omitted
  `schemaVersion`, `owner`, `bindings` or `digest`, report the mismatch.
- **Target scene mismatch:** compare the requested path with the active scene.
  During `author-scene`, open the exact selected Entry through the documented
  managed gateway and reread its fingerprint. If unavailable, report the blocker;
  do not recreate the content in `Hi.usda`.
- **Security & Anti-Hallucination Lock:** the token must match the receiving Editor MCP process. Inspect workspace and the failed receipt.
  Read task-specific `get_spatial_editor_docs` through `execute_editor_operation`, then retry the documented script through the same gateway
  with its exact token, current fingerprint and a new operation ID. Do not cancel on the first token rejection; exhaust Main Agent Recovery Rounds before policy-driven cancellation.
- **GUI reason rejected:** start with `gui_reason="user_requested"` and `preferred_mode="gui"` when requested; do not switch an active session.
- **Rendering demands GUI:** headless supports offscreen capture; reconnect an outdated gateway.
- `EDITOR_ALL_ASSETS_MUST_PASS_BEFORE_ASSEMBLY`: complete every prerequisite model review.
- `EDITOR_ASSET_PLANNING_INVALID`: correct the named `authoringStrategy`; primitive-only
  work uses `modelGeneration="forbidden"` and geometry-free roots use `group`.
- `EDITOR_REVISION_PARENT_ASSET_COVERAGE_REQUIRED`: missing targets before Session startup. Read `parentRunId`, `missingAssetIds` and `reason` (empty or incomplete manifest).
  Select a completed root `base_run_id` with verified bindings covering exact requested subject IDs and matching current scene/provenance; recency alone is insufficient. Report a blocker if none qualifies.
  A changed parent needs a new revision Run; keep the failed Run immutable. Never invent primitives, copy unverified inventory or drop requested material work.
- `EDITOR_REVISION_LINEAGE_REQUIRED`: material/transform scopes require `workflow_kind="revision"` and root `base_run_id`; a production path cannot inherit assets. Confirm parent coverage first.
- `EDITOR_ASSET_REVIEW_MISMATCH`: reread current artifact digests and evidence IDs.
- `EDITOR_ASSET_REVISION_REQUIRES_FAILED_REVIEW`: provide an evidenced rejected generated asset before a changed prompt; imported/reused files are not replaced.
- `EDITOR_ASSET_REVISION_BUDGET_EXHAUSTED`: report the unresolved asset; do not reset counters.
- `EDITOR_SCENE_FINGERPRINT_DRIFT`: inspect actual scene evidence, retain the warning
  and continue the current Handoff. Use `get_editor_workspace.sceneFingerprint` for
  new operations; replay existing operations with their original arguments.
  Fingerprint drift alone does not require correction or a new Run. Scene identity,
  geometry, ownership and image/file integrity failures still require their normal recovery.
- **Script failure / automatic rollback:** a final guarded-length rejection requires smaller scripts; raw length excludes gateway guards and indentation. Reread workspace and inspect partial
  changes. `receipt.sceneChanged=true` disproves full restoration;
  `sceneStateVerified=false` means refresh failed. Repair only incomplete work
  with a new operation ID; do not instantiate already-created assets again.
  Only when it reports `reconciliationRequired=true`, pass its ID in the successful
  repair's `reconciles_operation_ids`; freeze stays blocked without it. Otherwise omit it.
- **Asset return/type mismatch:** use the unified recipe in `references/authoring-quality.md`;
  await imports, resolve entityPath, inspect names and repair only missing instances.
- `EDITOR_WORKSPACE_ASYNC_PENDING` / `EDITOR_AUTHORING_ASYNC_PENDING`: poll via identical replay or workspace; never resubmit creation. Unknown/canceling tasks stay pending.
- **Unavailable default-PBR controls:** retain defaults and report the limitation. Apply supported appearance directly in geometry scripts; see references/pbr-materials.md.
- `EDITOR_AUTHORING_FAILED_OPERATION_RECONCILIATION_REQUIRED`: inspect failed scene writes and reconcile them with a successful managed repair before candidate submission.
- **Enhancement missing:** optional static fallback needs `required=false` in accepted
  SceneSpec and `unsupportedWork [{id, reason}]`; never put missing work in `enhancementIds`.
- `EDITOR_LIGHT_ENTITY_REQUIRED` / `EDITOR_ENHANCEMENT_CAPABILITY_UNVERIFIED`: lighting uses documented
  `execute_script`; query `topic="lighting"` and verify actual lights/parameters. Static kinds never relabel missing motion.
- `EDITOR_SESSION_FAILED`: report phase/PID/endpoint/probe/cleanup. Startup/MCP: 60 seconds;
  connected scene readiness: 180. Retry requires verified cleanup; timeout does not prove an orphan.
- `EDITOR_WORKSPACE_OPERATION_CONFLICT`: inspect the conflicting receipt and actual state, then use a new ID for changed arguments.
- `EDITOR_WORKSPACE_READ_ONLY` / `EDITOR_AUTHORING_WINDOW_CLOSED`: use capture/review
  or findings that reopen authoring; no raw backend writes.
- **Session/fence errors:** reconnect only an active managed Run. Terminal Runs
  do not regain authority through the gateway.
- **Manifest coverage/count/entity errors:** create missing declared objects or
  correct their bindings; one real entity cannot satisfy distinct manifest occurrences.
- `EDITOR_ASSET_ENTITY_DUPLICATE`: the path exists but is claimed twice; inspect the two named asset IDs.
  A material/transform-only revision uses `group` scopes and inherited material subject IDs, not an extra primitive asset such as `FloorDarkening`.
  Correct the SceneSpec through an applicable task; never invent extra geometry or edit persisted manifests to satisfy a mistaken duplicate claim.
- `ASSET_PRODUCTION_UNAVAILABLE`: Worker-owned API-key capacity retries use three persisted waits.
  Follow `next.action="wait"`; a terminal result is exhausted or non-capacity failure.
- `EDITOR_REVIEW_CAPTURE_RECEIPT_REQUIRED`: use the archived path, hash and timestamp returned for the current frozen candidate.
- `EDITOR_EXPERIENCE_REVIEW_EVIDENCE_STALE`: recapture only through an applicable current window; old evidence cannot be made current by editing timestamps.
- `MODULE_GATE_FAILED` / `MODULE_REQUIRED_FAILED`: inspect the underlying reason.
  Failed checks or stale evidence need the applicable correction. A schema-valid,
  saved review followed by an internal missing-object error is a framework blocker,
  not proof of defective geometry or material.

`resolve_material_binding` is read-only and may not resolve native primitive defaults.
Candidate acceptance checks asset counts, ownership and the scene fingerprint without
requiring numeric readback or shared identity.

## Terminal Framework Failure

With `retryable=false` and no applicable `next`, preserve saved paths, checks, failed module,
root Run ID and exact error. A terminal Run is immutable, but its failure does not end the
main Agent's scene-delivery task. After confirmed drain and session release, follow Native
Editor Fallback to repair and deliver saved content. Do not start another full production
Run just to repeat completed authoring, fabricate gate success or rewrite terminal state.
Managed delivery still requires verified `.bundle`, `.scenes.json` and provenance.

## Retry Discipline

- Use the current applicable `next.action` for submission; `error.retryable` describes Runtime retry support, not whether the main Agent can diagnose, repair or use Native Editor Fallback. Never force an unavailable Handoff or terminal Resume.
- A new Run is not a retry exception. Do not repeat authoring for unchanged failed packaging.
- Correct a rejected form on the same Handoff; it does not consume a backend retry or authorize `advance`. A targeted correction with an unsuccessful verified result counts toward that blocker’s main Agent recovery rounds.
- Distinguish form rejection, evidence invalidation, bounded wait and framework failure.
  Record the named cause and what changed before each retry. If the same rejection
  repeats after that correction, inspect the contract/receipts; do not cycle through
  guessed fields, alternate camera parameters or a complete new Run.
- A successful operation supplies the next fingerprint; read workspace after conflicts/uncertain outcomes and before candidate submission. Do not repeat full inspection or API docs after every call.
- Retry only failed captures, retaining valid receipts for the same unchanged candidate within its freshness window. Capture retries do not repeat scene assembly.
- A bounded wait returning another wait is normal. Judge `current.status`, `next.action` and `error` together; a non-terminal Run with `next.action="wait"` continues on the same root, including after a recoverable submission rejection. Do not resubmit its review.
- Elapsed time, repeated waits, unchanged revision or a generic `execute-generation` phase do not prove blockage. Refresh the same root's public status and available current child/activity information; discard earlier material-stage observations when particles are active. Report progress or uncertainty every 60 seconds. Missing activity stays unknown; follow the returned wait unless independent current evidence confirms a blocker for Main Agent Recovery Rounds.
- Native operation completion and `saved=true` establish neither report acceptance nor completed review and packaging. Follow the latest root action through report submission and finalization.
- Preserve returned backend retry budgets and user-decision actions. Apply three main Agent recovery rounds per confirmed blocker; never reset persisted budgets, count ordinary waits as attempts or repeatedly request an unchanged user decision.
- Do not downgrade required work, weaken acceptance, delete user changes or bypass gates.

## Cancellation And Cleanup

The main Agent must call `cancel_editor_workflow` on the root after three unsuccessful
recovery rounds for the same confirmed blocker. An explicit user request can cancel
immediately. Waiting, suspected stalls, a transport timeout or stale stage information
alone do not establish a blocker or exhaust recovery. Child cancellation propagates
from the root; do not cancel a Child independently. A confirmed terminal Run requires
reading its result, not cancelling or resuming it.

Cancellation acceptance does not prove task drain or session release. Observe until the
root and attached work are terminal and managed execution, pending Editor tasks and
session cleanup/release are confirmed. `cleanupPending=true` permits only task cancellation
and deferred session cleanup retries; continue its wait. If drain or ownership is unknown,
diagnose it through documented status/cleanup operations and retain the uncertainty;
do not start independent scene writes, clear locks or take over an unverified process.
`cancelled` stays terminal; never resume it.
Cancellation does not roll back completed scene writes. Inspect operation receipts and the saved USDA before claiming no changes; `sceneChanged=true` contradicts that claim even when a later candidate was rejected. Report saved scene state separately from verified delivery packages; restore only with explicit authorization.

## Native Editor Fallback

After cancellation or an earlier Runtime terminal failure, the main Agent must attempt
to finish any partially generated scene through the advertised native Editor MCP tools
once task drain and session cleanup/release are confirmed.

For managed recovery or native repair and delivery, the main Agent may consult the current
`spatial-editor` Skill and the references relevant to the unfinished work:
`references/material-production.md` for material repair and persistence,
`particle-workflow.md` for particle authoring and visual checks, and
`references/authoring-quality.md` plus Completion And Handoff for scene and package verification.
Reuse those methods on retained content. During native fallback, use advertised native tools;
managed Handoffs, stage tokens, round control and receipts apply only to an active authorized Run.
Reading a Skill does not authorize a new Run or restore a terminal Run's write authority.

1. Use returned project/scene paths and saved outputs; inspect the actual retained scene,
   including incomplete writes. Preserve unrelated user content and completed assets.
   Do not browse private Run history to invent an inventory or rewrite workflow records.
2. Establish an independent Editor session through documented standalone lifecycle.
   Verify project, active scene and exclusive ownership. A terminal Run's old gateway,
   fencing token or descriptor cannot authorize fallback writes.
3. Repair the outstanding defects using currently advertised/documented native MCP
   capabilities. Inspect tool failures and try applicable supported remedies; do not
   weaken requirements, repeat completed authoring or pretend an unsupported API exists.
4. Save and inspect the final scene with real current screenshots and structural checks.
   Complete and validate the requested delivery files; for a scene package, verify the
   `.bundle` and co-located `.scenes.json` against the actual scene. File existence or a
   successful tool call alone is not proof of requirement fulfillment.
5. Report original Run status, repaired scene/delivery paths, verification evidence,
   warnings and unresolved work separately. Native completion does not establish
   managed review, gate acceptance or provenance; keep any earlier evidence unchanged.

Only declare the overall task failed when workflow recovery and applicable native
Editor remedies still cannot satisfy the request. Cite the three-round record when
applicable, fallback attempts, remaining blocker and retained scene/output paths.
If fallback cannot start because cleanup, ownership or required capabilities remain
unavailable, report that evidenced limitation instead of claiming it ran.
An explicit user request to stop ends execution; do not begin fallback against that request.
