# Spatial Editor v7 Handoff Contracts

This owns Agent forms; live `next.submission.inputSchema` is authoritative.
See `SKILL.md` for routing and `recovery.md` for rejections.

Primitive transforms/joints use `references/primitive-geometry.md`.

## Interaction Rules

1. Use the public root Run and its latest `current`, `next`, `error`, and terminal
   results. Consume each public Run observation once; replace cached submission
   arguments after each Workflow call.
2. For a submission, call `next.tool` with `next.arguments` plus one `input`
   matching `next.submission.inputSchema`. Use `next.submission.kind`; copy
   `run_id`, `task_id`, `task_type`, `expected_revision`, and `max_wait_ms` from `next.arguments`.
   If absent, choose `task_type` from `next.submission.taskTypes`.
   Submit only through `submit_editor_workflow`; obsolete forms are rejected.
3. For `next.action="wait"`, use its bounded wait. The Worker advances the Run;
   status reads observe it. All submissions use the current Resume Handoff.
4. Use reflected `get_scene_info` and `get_entity_info` for read-only facts.
   Scene assembly writes/captures use `execute_editor_operation` in the managed window.
   For native particle stages, read `particle-workflow.md` when SceneSpec declares particles.
5. Use finite vectors, task-derived dimensions and properties, and stable Editor
   names matching `^[A-Za-z_][A-Za-z0-9_]*$`. Remove placeholders, JSONC comments,
   trailing commas, and optional fields with no accepted value before submission.
6. Work in `agentWorkspace.directory` / `scratchDirectory` under project `.CacheData`.
   Read current paths and canonical IDs/digests, including `resultRef` chunks.
   Refresh missing views on the same Run/workspace; submissions map registered paths
   to original receipts. Keep published evidence and Editor caches/locks intact.

## Gate Action Map

The Editor Child has eleven module Gates; they do not require eleven Agent submissions.
Follow root `next`; session and asset preparation may run in parallel.

| Gate                      | Action and reuse                                                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `run-context`             | Start once with absolute workspace/project and goal. Correct rejected fields; keep an existing Run.                            |
| `editor-session`          | Worker establishes ownership; follow waits. Verify target when author-scene opens. Recover the same active session.            |
| `authoring-bootstrap`     | Submit the parent SceneSpec with strategies, counts and direction. Worker projects it; no second Scene Plan.                   |
| `asset-production`        | Review current preview batches; retain accepted models and revise only rejected items. No models means no review action.       |
| `material-production`     | One material Agent authors/binds selected Graph targets before particles. Supply its backend when requested.                   |
| `particle-production`     | Worker prepares declared effects in the same GUI scene. Supply a verified backend only when requested. Retain missing effects. |
| `author-scene-candidate`  | Arrange geometry and configure native PBR appearance, then submit the candidate. Reuse receipts.                               |
| `author-enhancements`     | Worker projects enhancements authored together. Wait unless next requests input; do not repeat material/lighting work.         |
| `review-evidence-capture` | Wait for Driver to capture seven whole-scene views; it reuses valid receipts and retries missing views.                        |
| `review-experience`       | Submit five checks, supported criteria and findings. Reuse image observations; return defects to their owner.                  |
| `delivery-package`        | Worker packages/verifies/registers. Follow waits; no empty form unless next requests it. Preserve work on failure.             |

After rejection/interruption refresh task/Schema; preserve work and correct fields.

Keep revision's inherited `existing-scene` bindings; only replacements enter production.
Groups describe scope, not inventory.

## Start Form And Target Scene

Production creates geometry with absolute `workspace_root` and `goal`.
When delivery specifies a project filename, pass its filename stem (without
`.spatialproject`) as `project_name` at startup, including when `project_path` is
an empty directory. Without a name, an empty directory uses its normalized
directory name. Existing projects keep their name; `sceneSpec.sceneId` names the
scene independently.
Revision uses root `base_run_id` and inherits project/scene/inventory; omit
`workflow_kind` or set `"revision"`, with no `target_scene_path`.
Select by verified target coverage and matching scene/provenance, not recency or success alone.
Material-only Floor requires parent `asset:Floor`; a pure-transform parent's empty
manifest cannot supply it. Initialization checks coverage before Session startup.
Empty manifests remain valid without material bindings and require `assetBindings: []`.
Verify the live active scene; do not assume startup opened it. On mismatch open the exact
Entry through the gateway and reread its fingerprint. Never substitute `Hi.usda`.
Default headless; primitives/material production select GUI for rendering checks.
Explicit GUI uses `preferred_mode="gui"` and `gui_reason="user_requested"`.

The facade requires `scene-package` and has no authoring-only mode.

## Scene Specification Form

At `author-scene-spec`, submit identity, objective, coordinates and subjects/counts.
Check `subjects[].count`; split excess while preserving totals/references.
Use `next.submission.inputSchema`. Each subject selects
`authoringStrategy="generated-model"`, `"imported-model"`, `"editor-primitives"`, or `"group"`.
Imports: normalized workspace-relative USDZ or self-contained GLB `source.path`, no
`generationPrompt`. Worker pins sources, converts GLB natively and captures six axes;
do not hand-rebuild materials. Generation and import may mix.
Groups have no geometry and are not extra assets. Primitive-only uses `modelGeneration="forbidden"`.
Tags/`kind` do not select production; derive properties from accepted intent.
`generationPrompt` describes one product's connected parts; counts/placement stay in SceneSpec.
Authorized static fallback uses `required=false`; omission defaults to required.

Declare `effects` with `kind="particle"`, stable `id` and `description`.
For linked criteria, batch preparation and non-blocking gaps, read `particle-workflow.md`.

## Asset Review

At `review-editor-assets`, inspect every preview and metadata.
Submit current artifact digests, evidence IDs and six-axis `orientation` with
`worldForwardAxis`, semantic features and confidence. Use `not_applicable` for no front;
use `ambiguous` for insufficient directional evidence and revise generated models.
Imported sources receive direction-only review; ambiguous may pass with a reason.
Resolve direction before placement or report a blocker. Only generated requests allow
regeneration. All models must pass before editing. Use live `next.submission.taskTypes`.

## Author Scene And Candidate

Read `sourceContract` and applicable `references/authoring-quality.md` once.

Use `get_editor_workspace.sceneFingerprint` as
`execute_editor_operation.expected_scene_fingerprint` with unique `operation_id`, `tool`
and `arguments`. Replay identical requests. Unexpected fingerprint mismatch returns
`EDITOR_SCENE_FINGERPRINT_DRIFT`; retain the warning and continue the current Handoff.
Correct evidenced scene defects through the Workflow. After failure reread workspace even after claimed rollback.
Use `tool="execute_script"`; split for size/async dependencies.
Obtain the process token via `tool="get_spatial_editor_docs"` in the same gateway.
Reuse `importedEntityPath` as the first formal instance; inspect stale/foreign paths first.
Import only missing occurrences up to `count`: `count-1` when reusing one, `count` when none exist.
Do not retain hidden prototypes or create PrototypeCache by default; keep USDZ
files and acceptance records for recovery. Await script imports.
For `add_asset_to_scene`, wait its returned task via identical replay or workspace reads.
Pending receipts block writes/captures/submission.
Do not probe API aliases.
The token is not a gateway permission. Process changes need docs; changed retries need new IDs.
Query uncovered APIs with `detail="brief"` and exact name/topic; expand once to full.
If unresolved, follow `EDITOR_API_SIGNATURE_UNRESOLVED` recovery.

For truncation replay identical ID/arguments with `response_mode="errors_only"` or
`"full"`; see `receipt.resultRef`/`summaryRef` and `recovery.md`.

Verify absolute parents via `get_scene_info`/`get_entity_info`; never prepend `/Root`.
Compatibility flags are not visual proof; inspect the isolated image. Keep captures headless.
`se.scene.roots()` lists top-level assets; `roots()[0]` is not the implicit `/Root`.
For scene-root identity-transform groups, use documented `reparent_to_root`; verify parent, world transform and bounds.
Preserve accepted forward and named features; an opening normal is not a cone's base-to-tip direction.
Submit one `input`:

- `candidate.sceneFingerprint`: the current live fingerprint.
- `candidate.inventory.assetBindings`: every manifest item as
  `{assetId, entityPaths}` at its required count.
- `candidate.inventory.shaderGraphTasks`: only `SceneSpec.materials` requirements
  selected with `generation="generate"`, as
  `{id, materialName, description, targetEntityPaths}`. Copy the requirement id and
  description; provide actual surface paths observed after assembly. Basic RGBA and
  suitable existing materials stay with assembly. Omit the list or use `[]` when none.
  No full-scene material table or cleanup scope is required. The dedicated material
  Agent authors and binds Graph before particles, makes up to three attempts for each failed task,
  and records remaining failures as nonblocking warnings; read `references/material-production.md`.
- `candidate.inventory.enhancementIds`: authored enhancements; `[]` when none.
- `candidate.inventory.unsupportedWork`: optional gaps as `{id, reason}`; Worker also retains failed particles.
- `candidate.inventory.scenePath`: the verified saved scene entry.
- Omit `candidate.operationIds`; Driver archives all successful gateway receipt IDs,
  including docs and superseded captures. Explicit lists require exact successful
  `receipt.id` values from `get_editor_workspace.operations`; exclude failures.
- `candidate.evidence`: required evidence of the authored scene.
- `interactionContract`: all four fields below, including when there is no interaction.

Without app interaction, use:

```json
{
  "schemaVersion": "spatialcraft.editor-interaction-contract/v1",
  "owner": "application-code",
  "bindings": [],
  "digest": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
}
```

Use `input.interactionContract`; `bindings: []` alone is invalid.
Non-empty bindings follow the live Schema. Compute SHA-256 of the binding array's
canonical JSON, sorting object keys recursively and preserving array order.

Workflow v7 uses each primitive's default PBR during geometry creation.
Read appearance requirements from `authoring.intent.sourceContract` and apply supported
parameters directly in geometry scripts. `Entity.set_color(r,g,b,a)` changes BaseColor.
See `references/pbr-materials.md` for live limitations; keep defaults and report
unavailable controls. Assembly needs no material registration. Accepted SceneSpec
descriptions provide semantic tasks for the managed material subflow.

Submit actual created/reused occurrences through `candidate.inventory.assetBindings`.
Completed-run changes use SceneSpec Revision with parent lineage.
Preserve unrelated imported materials.
Candidate submission verifies full manifest counts, asset ownership and the scene fingerprint,
then freezes writes. Material appearance uses final seven scene views.
Workspace summary remains bounded; full/replay reads details without writes.

## Capture Arguments

Driver owns the final seven-view captures. For a concrete supplemental inspection,
inspect the live schema and use these rules.

- Frozen capture uses `get_editor_workspace.captureInputSchema` or tools/list, retaining native render types/enums.
  `container_fit_mode` allows only `none` or `report_only`.
- With explicit `camera_mode` (e.g. `front_three_quarter`), position, target, rotation or orbit controls,
  set `arguments.frame="none"` and omit `arguments.entity_path`.
  Omitting `frame` may activate backend default framing and still conflict.
- For a candidate overview, pass render/delivery fields only, e.g. `{"width":1280,"height":960,"image_format":"png","delivery":"auto"}`.
  Omit `entity_path`, `frame`, `camera_mode` and explicit camera controls for default whole-scene framing.
  If entity framing still conflicts after removing `camera_mode`, remove both `frame` and `entity_path` too.
- Use `arguments.delivery="auto"` when supported or omit it; `"file"` requires the live schema to allow it.
- Preserve session mode for offscreen rendering; derive camera controls from live bounds, not example coordinates.

At `capture-review-evidence`, follow waits: Driver captures the six world-axis views
(`view_from_+X`, `view_from_-X`, `view_from_+Y`, `view_from_-Y`,
`view_from_+Z`, `view_from_-Z`) and `front_three_quarter` from the frozen bounds.
Driver archives each image, hash, timestamp and camera, reusing current valid receipts.
Manual `views` submission and historical capture Handoffs are unsupported.
These seven perspective views are required; a separate orthographic top view is not required.
Inspect current images once, then use them for the review without reopening them
unless evidence changes or an observation remains unresolved.

## Experience Review And Outcome

At `review-editor-experience-v7`, the same caller agent checks all seven supplied
images and returns only judgment fields from the live schema: `schemaVersion`,
`verdict`, `fulfilledCriteria`, `checks`, and `findings`.
Cover `scene-identity`, `hard-criteria`, `visual-composition`, `interaction-bindings`
and `operation-lineage`; cite supplied view labels for each. Pass requires every
required criterion in `fulfilledCriteria`, all checks pass and no open findings.
This describes the review verdict, not workflow admission: every seven-view quality finding,
including missing proof of a required criterion, is advisory and continues to packaging.
Record failed checks with `verdict: findings` and preserve concrete findings as delivery warnings.
Use `verdict: findings` whenever `findings` is nonempty, including retained material-report
warnings with all five checks passing. Do not invent a failed check when current evidence
supports pass. Check statuses use exactly `pass`/`fail`; material outcome statuses use
exactly `succeeded`/`failed`. The submission schema rejects `pass` with findings or failed
checks, and rejects `findings` with an empty findings array.
Never mark an unmet or unverified criterion fulfilled. Deterministic scene identity, delivery-file
integrity and packaging failures remain blocking.
Inspect all seven views; cite useful views per criterion and multiple views for depth/direction.
Natural occlusion is not a defect; do not recapture valid views for it.
Missing proof of a required criterion is insufficient evidence.
Read `materialProduction.report` once when supplied; preserve its limitations
in check summaries and advisory findings. Material-local motion does not
create an animation enhancement entry.
Cite supplied `evidenceViewLabels`. Runtime binds candidate identity, lineage and evidence;
never manufacture authority fields.
The package criterion concerns delivery readiness; claim `.bundle` completion only
after the downstream result verifies it.

Distinguish saved verification from bundle/manifest/provenance; preserve work on blockers.
For a new pack, include `scene.runtimeSceneKey` in the App handoff and copy it unchanged
to SDK loading. For older packages without a verified key, do not guess from the display
name or source path.

## Pre-Submission Checklist

Use the latest Handoff/revision/Schema, verify bindings/views and Interaction Contract,
submit once and correct rejections with `recovery.md`; do not act from a cached response or a Snapshot-only state.

Worker packages/verifies/registers and releases Session; headless stops, GUI stays open.
Follow waits. After timeout/WORKFLOW_RESUME_TERMINAL read the same root for fresh next/arguments.
Reuse reviews only for unchanged evidence. Apply `recovery.md` to waits/errors;
unexpected live fingerprint differences are warnings. Candidate/input identity, image and file digest
checks remain required; historical terminal Runs remain immutable.
