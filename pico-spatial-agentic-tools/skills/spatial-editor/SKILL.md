---
name: spatial-editor
description: Run managed Spatial Editor workflows for scenes, assets, materials, review and packaging. Use only when the user's prompt or an upstream app agent's delegation prompt explicitly requests a Spatial Editor workflow (spatial-editor-workflow), or to continue an already authorized Run. NOT for requests merely to use Spatial Editor, standalone edits, inspection or packaging — use native Editor tools and pico-cli; existing bundle integration uses spatial-app-dev-workflow.
license: 'Apache-2.0'
---

# Spatial Editor Workflow

## When to Use

- An upstream agent building a PICO Spatial app explicitly requests the Editor workflow in its delegation prompt.
- The user explicitly requests a Spatial Editor workflow in their prompt.

These are the only conditions for starting a new production or revision Run.
Installing pico-cli, mentioning Spatial Editor, or requesting scene objects, materials,
geometry, lighting, effects, inspection or packaging does not by itself select a workflow.
For an already authorized active Run, continue its current Handoff without starting another Run.

Loading this Skill does not authorize a Run. Its managed ownership rules apply only after
explicit workflow selection; they cannot supply missing authorization. Ordinary upstream
Editor delegation also does not select a workflow. Apply this gate to every new Run,
including revisions suggested by recovery or delivery guidance.

- "Use Spatial Editor to create a scene" → native Editor tools, no new Run.
- "Use the Spatial Editor workflow to create a scene" → start the managed workflow.

## When NOT to Use

- Standalone Editor edits or inspection without either startup condition — use native
  Editor tools; use `pico-cli` for command discovery and standalone Editor lifecycle.
- Code-defined Entity scenes — use `spatial-sdk-scene-builder`
- UI panel layout — use `spatial-ui-ability`
- Existing bundle integration — use `spatial-app-dev-workflow`

## Load Only What The Current State Needs

See [3D execution choice](references/3d-execution.md) for direct execution and continuation;
its Editor startup rules use the explicit selection gate above.

This Skill owns workflow intent and task decomposition after a startup condition is met. Start one
`start_editor_workflow` Run and generate its SceneSpec first, including particle-only
requests. The public Run owns model inventory and bundle delivery.

- SceneSpec particle effects: read `particle-workflow.md` for managed preparation.
- Current v7: Read `contracts.md` from this Skill directory and follow
  `next.submission.inputSchema`.
- Primitive orientation or joints: read `references/primitive-geometry.md`.
- Native PBR, captures or containers: read `references/authoring-quality.md`.
- Before SceneSpec, read `references/material-design.md` and `references/material-selection.md`.
- Material production handoff or native recovery: read `references/material-production.md`.
  The material worker supplies its built-in Skill, including SGS image texture production
  and failure reporting, directly to the child Agent; no Host Skill lookup is required.
  For transparent surfaces, also read `references/transparent-preview-surface.md` for the
  catalog-confirmed opacity input, minimal graph, exterior preview and scene-save procedure.
- Rejection, interruption or blocker: Read `recovery.md` from this Skill directory;
  follow its current recovery actions.
- Saved scene/material verification: save → `se.scene.reload(...)` → inspect, with
  unsaved-change protection. Read `references/material-production.md`; ordinary
  persistence verification and packaging do not require restarting Editor.

This Skill supports current v7 Runs only; see `contracts.md`'s Gate Action Map.

## Ownership And Safety

Editor owns content and packaging; `spatial-sdk-scene-builder` owns Kotlin
Entities and runtime behavior. Apps consume Editor packages.

While an explicitly selected Run is active or still draining, mutations and packaging stay in its
managed gateway. After workflow selection and before Run startup,
do not invoke a direct Editor readiness command or start a standalone session for its target.
Read-only status is allowed; the Workflow Session must establish and own its Editor
process. Resolve other sessions' ownership before writing.

Never bypass the Workflow Service or its Drivers for writes or packaging in a managed workspace.
For standalone work outside an active managed workspace, use the advertised native Editor tools
and verify the changed targets. If an active Run owns the scene, continue its authorized
editing Handoff; do not write around its fencing or create a replacement Run.
`get_scene_info` and `get_entity_info` are read-only and do not require a Workflow Handoff.
At `author-scene`, use `get_editor_workspace` and `execute_editor_operation`;
the gateway checks session, editing window, scene fingerprint and operation receipts.
Unexpected fingerprint drift is advisory: follow the current Handoff, inspect actual scene
evidence and retain warnings. Managed writes still update fingerprints and receipts normally.

## Managed Workflow

After choosing managed execution through the startup gate above, use the `start_editor_workflow` entry for the public
`spatial-3d-generation` root with `backendPreference="editor"`; never start the Editor Child directly.
Generate its SceneSpec first.
For SGS supplied assets, read `references/sgs-supplied-assets.md`.
Revision uses root `base_run_id`; production uses `workspace_root` and optional
`target_scene_path` for new geometry. Verify the active scene.
For `project_name` and filename rules, see `contracts.md`.
Legacy `content_kind` values remain compatible hints; SceneSpec determines particle work.
Default headless; explicit GUI uses `preferred_mode="gui"` and `gui_reason="user_requested"`.
SceneSpec materials/particles select GUI; see `references/session-admission.md`.

The normal loop is:

1. Start one public production or revision Run for the goal.
2. Resume the initial `author-scene-spec` Handoff with every subject/count.
   Keep models and structural primitives in the complete asset inventory.
   Check live `subjects[].count` limits; split excess and preserve totals/references.
   Set `authoringStrategy` to `generated-model`, `imported-model`, `editor-primitives`, or `group`;
   Imports: normalized workspace-relative USDZ or self-contained GLB `source.path`.
   Generation and import may coexist; import never requires a generation prompt.
   a geometry-free root is a group, not an extra model. Primitive-only uses
   `modelGeneration="forbidden"`; tags and `kind` do not select production.
   Declare `effects` with `kind="particle"`; follow `particle-workflow.md` for
   batch production after scene assembly, node bindings and missing-effect records.
3. Let model production advance. When `next.action="wait"`, call `next.tool` with
   its returned bounded arguments. Primitives do not enter model production.
4. At `review-editor-assets`, inspect all previews. Record `worldForwardAxis`,
   semantic features and opposite views when a front is visible. Use `not_applicable`
   for no intrinsic front. Use `ambiguous` only when a directional model's evidence
   is insufficient, and revise generated models only. Imported sources are retained;
   their asset review covers direction, with scene placement checked later.
   All prerequisite models must pass before assembly.
5. At `author-scene`, use `get_editor_workspace` and `execute_editor_operation`
   for one bounded arrangement recipe of models, primitives and enhancements.
   Split for script/output size or async dependencies; await imports.
   Use the reuse recipe in `references/authoring-quality.md`; query uncovered APIs
   with `detail="brief"` through the gateway and reuse its exact `auth_token` in scripts.
   Apply supported default PBR from `authoring.intent.sourceContract` during creation;
   see `references/pbr-materials.md`. Select Graph requirements with `generation="generate"`;
   after assembly submit `candidate.inventory.shaderGraphTasks` with observed target
   paths, material names and descriptions. The material Agent handles only these Graph
   tasks before particles; see `references/material-production.md`.
   Later changes use SceneSpec Revision with lineage.
   Finish writes before review; report progress every 60 seconds.
   Default extra local/detail screenshots: zero; use them only for a concrete open issue.
   Submit the candidate, complete asset inventory, successful operation
   receipts, and complete Interaction Contract from `contracts.md`.
6. At `capture-review-evidence`, follow returned waits while Driver captures the frozen
   candidate using six world-axis views and front three-quarter view. Driver fits cameras
   to bounds and retains valid receipts when retrying failed views.
7. At `review-editor-experience-v7`, the same caller agent inspects the evidence and
   submits checks and findings. Do not spawn a reviewer subagent. The scene is read-only.
   Failed checks return to the responsible production window; recapture after changes.
8. Worker packages, verifies and records provenance. Follow returned waits;
   submit packaging only when a live Handoff requests input.

Treat every Workflow MCP response as one observation of the public Run. Read
`runId`, `current`, `next`, `error`, terminal `result`/`artifacts`/`evidence`; replace cached
arguments and stage/child observations.

Judge `current.status`, `next.action` and `error` together. Follow non-terminal waits;
elapsed time is not a blocker. The main Agent owns recovery of confirmed blockers;
follow Error Recovery below and `recovery.md` for attempts, cancellation and finalization.

After project readiness, use `agentWorkspace.directory` under
`.CacheData/AgentWorkspace/<rootRunId>`; temporary work belongs in `scratchDirectory`.
Read current resource paths and exact IDs/digests. Refresh missing files on the same
Run/workspace; never browse internal Run folders, edit published evidence, or clean
Editor caches/locks. See `contracts.md`.

For submissions, call `next.tool` with `next.arguments` and `input` that
validates against `next.submission.inputSchema`; use `next.submission.kind`.
Use `submit_editor_workflow` with returned `task_type` or one `next.submission.taskTypes`
value matching the payload. `task_id`/`expected_revision` bind the Handoff.
`get_editor_workflow_status` is observation-only. `current.module`, `current.phase`,
and `current.models` provide compact progress.

A Handoff mismatch is a non-terminal rejection: the Workflow Service preserves the
current public waiting state. Refresh before retrying; see `recovery.md`.

## Error Recovery

The main Agent must try to resolve workflow blockers before declaring the overall task failed.
For the same confirmed blocker, perform three targeted recovery rounds: inspect current
evidence, apply an applicable documented correction, and verify the outcome. Record the cause,
what changed and the result of each round; do not blindly repeat a failed call.
Normal waits, status queries and automatic backend retries do not consume these rounds.

After three unsuccessful rounds, cancel the root with `cancel_editor_workflow`.
An explicit user cancellation remains immediate. If Runtime already terminated the Run,
inspect its result instead of trying to resume or cancel it. After confirmed task drain
and session cleanup/release, use an independent Editor session and advertised native MCP
tools to repair the partially generated scene and complete the requested delivery.
Preserve existing content and verify the repaired scene, save and delivery files.
For repair and delivery, the main Agent may reuse this Skill's current-stage authoring
and verification guidance; `recovery.md` selects the applicable references and execution path.
Only report overall task failure after recovery and applicable native Editor remedies
cannot satisfy the request. Report the original Run's terminal status separately from
the verified fallback result; never claim a cancelled or failed Run completed successfully.
Read `recovery.md` for the exact transition and evidence requirements.

## Task Decomposition

Before model production, separate:

1. Distinct generated/imported model archetypes.
2. Repeated occurrences that can reuse one accepted archetype.
3. Structural or dimension-driven primitives.
4. Requested material work and semantic targets.
5. Whole-scene relationships and acceptance.
6. Lighting and supported static/particle effects.
7. Downstream runtime-node and delivery contracts.

### Asset Archetypes And Reuse

Generate one archetype for shared form, appearance and role; separate assets with
different identity, function, geometry or acceptance.
Reuse is a design heuristic, not an acceptance gate.
Reuse the accepted imported entity as the first formal instance; import only
missing occurrences up to `count`. For stale/foreign paths, inspect live instances
first. Do not retain hidden prototypes or create PrototypeCache by default.
Keep USDZ files and acceptance records for recovery.

### Structural Primitives

Use primitives for dimension-driven floors, walls, columns, platforms, partitions,
and simple volumes. Use generated/imported assets when silhouette, topology,
curvature, ornament, or semantic identity requires authored geometry.

Classify orientation before authoring a primitive transform:

- A `Cone` has a signed semantic direction from its base toward its tip.
- A `Cylinder` or `Capsule` has a longitudinal axis, but its positive and negative
  ends are equivalent unless accepted input adds an observable end distinction.
- A `Plane` has a signed normal only when face visibility, culling, or another
  accepted relationship makes the normal observable.
- A `Sphere` has no intrinsic direction. A `Cube` has no semantic front unless
  accepted input or a visible face distinction establishes one.

For every direction-sensitive primitive, derive the required world direction from
accepted scene intent or an explicit relationship, use the canonical Editor
primitive-axis mapping in `references/primitive-geometry.md`, and repeat that direction as an observable
primitive acceptance criterion. Never choose a direction from category convention,
hide an unresolved direction in `rationale`, or treat an axial primitive as having
a head and tail when its geometry does not distinguish them.

Choose joints from actual contact surfaces: use butt joints for sufficient flat-face
contact, and bounded insertion where curvature would leave only point/line contact.
Hide the entire inserted end, including corners, and check all exterior surfaces
for competing overlap. Internal contact/overlap is valid. These rules apply to all
geometry. Read joint selection and examples in `references/primitive-geometry.md`.

Defer final primitive transforms until accepted model bounds are known:

- Model-only: placements and optional instances.
- Mixed: placements, instances, and final primitives.
- Primitive-only: create declared primitives directly in the editing window.

The complete asset inventory retains primitive identity, count, and acceptance.
Create concrete primitive geometry and transforms in the authoring window after model
acceptance. Candidate submission checks that every declared primitive has live entity
bindings; final scene review checks its appearance and spatial relationships.

### Scene Intent And Hierarchy

Before candidate submission, delete temporary prototypes, canaries, duplicate imports
and empty staging containers; preserve required content and formal instances.
Verify absence/counts, save and reread the fingerprint. Hiding is not deletion.
Verify compound subjects' materials in the final seven views.

Use `references/material-design.md` for appearance. Explicit
color, emission, opacity, roughness, metallic behavior, and render mode use supported
properties. `Entity.set_color(r,g,b,a)` updates default PBR BaseColor.
Color alone does not prove emission or transparent blending.

Group coherent assemblies with identity-transform `Xform` nodes.
Declare `scene.runtimeNodes` only for downstream-addressable entities using `./...`
from the discovered managed root. Editor operations use verified absolute paths;
never derive a root path from `scene.name`.

## Visual And Spatial Review

Actually inspect every image referenced by current evidence. File existence, a
successful call, bounds, or a package is not visual proof.

For `reuse_required`, scope that model's evidence-image review to direction-related evidence only. Do not evaluate or fail geometry, appearance, topology, or detail,
and use `orientation.verdict="ambiguous"` when an imported model has no reliable
semantic front. This is not a request to generate a replacement; final scene review still
evaluates placement and physical/spatial defects.

Floating, unintended penetration, instability, unusable scale, obstruction and
requirement violations in the final seven-view review become delivery warnings. Depth findings need multiple views.
Natural occlusion in a valid axis view is not itself a finding or a reason to
retake it. Inspect all seven current views and cite the useful views per criterion.
Missing proof of any required criterion becomes a warning; never claim it fulfilled.
All seven-view findings continue to packaging. Deterministic scene identity, delivery-file
integrity and packaging failures remain blocking.

For a direction-sensitive primitive, compare its named semantic feature against
its exact acceptance criterion in at least two useful current views. Opposite
world-axis views are preferred for a signed direction such as a cone tip. A reversed
tip, normal, or required longitudinal axis is an explicit requirement violation and
must be recorded as an advisory finding in the final seven-view review.

Review contact and all exposed joint sides in useful current views. Record unintended
gaps, point/line-only connections, exposed coincident or near-coincident surfaces,
breakthrough, flicker or viewpoint-dependent seams as warnings. Internal contact/overlap is valid.
A hidden end or one clean image does not prove that exterior surfaces are safe.

Before final planning:

1. Read required runtime-node paths and parents.
2. Read world bounds and imported transforms for every accepted model.
3. Treat placement as the entity pivot; derive pivot-to-bottom and pivot-to-center.
4. Ground objects on real supports and derive spacing from measured extents.
5. Determine scale from measured bounds and scene relationships; never supply category-based default dimensions.
6. Preserve imported rotation unless evidenced semantic direction requires a world
   `+Y` heading delta.
7. Check containment, circulation, access, occlusion, and interpenetration.

Nonuniform scale uses local axes. An imported -90 degree X rotation maps local Y
to world Z and local Z to world Y. Map measured world-size ratios back through the
actual imported/parent rotation, then remeasure; do not blindly swap axes for other poses.

Axis-aligned bounds overlap alone does not prove penetration.

### Lighting And Effects

Preserve the existing scene environment and background. Do not set, replace or enable HDRI
through `set_environment_hdri` or equivalent scripts unless the user explicitly requests HDRI.
Brighter rendering, material previews, reflections and `lighting.kind="environment"` do not
authorize HDRI. Use supported non-HDRI lighting controls for requested illumination.
Do not apply app-runtime Stage skybox/IBL requirements to Editor scene authoring.

In managed SceneSpec, set `lighting.kind` to `"environment"`/`"light-entity"` and `effects[].kind` to
`"static"`/`"particle"`/`"other"`. Editor animation generation and registration are
unsupported; do not submit `kind="animation"` or disguise it as `other`.
Keep material-local motion in generated material requirements without an effect entry;
see `references/material-selection.md`. Managed particles use `particle-workflow.md`.
Lighting uses `execute_script`;
query `topic="lighting"` for `Entity.configure_light`, `aim_at` and `get_light`.
See `references/authoring-quality.md`; emission is not a light.

For an authorized managed fallback, set the SceneSpec effect `required=false`
and report its enhancement ID and reason in `inventory.unsupportedWork`.
Only implemented work belongs in `enhancementIds`. Missing required non-particle work blocks;
Resolve ordinary object/timeline animation through a supported workflow before
Editor submission.

## Existing Scenes

For a new managed material/transform request, use revision with root `base_run_id`.
Native fallback after a cancelled/failed Run follows Error Recovery above instead.
Previous workflow provenance alone does not authorize a new revision Run.
A runId is an execution record; it does not own permission to edit a scene.
Do not choose only the latest successful Run: its manifest may be empty.
Choose verified parent inventory covering each material target's exact subject ID
and accepted entity bindings; confirm scene/provenance still matches the project.
A material-only Floor change needs inherited `asset:Floor`, not a new primitive.
Coverage is checked before Session startup; see `recovery.md` for missing targets.
Pure transforms without material bindings may retain an empty manifest.

Preserve unrelated content; submit the complete retained and authored inventory
or `assetBindings: []` for an empty manifest. Correct rejections in the same active Run.

## Completion And Handoff

Report optional work in `unsupportedWork`.
To sync a Kotlin component declaration, use
`pico-cli editor sync component --component <KotlinComponentName>`;
use `--editor-project` or `--file` when multiple projects/files match.
Declaration sync alone does not change an entity.

For a managed delivery, after packaging and Session release, return:

- Project, accepted scene paths, and exact `runtimeSceneKey`.
- Co-located `<bundleName>.bundle`, `<bundleName>.scenes.json`, and provenance.
- Managed Run/revision/fingerprint/gate proof and SHA-256 digests.
- Runtime-node, orientation, material, warning, and unsupported-work results.

Distinguish saved verification from managed delivery; the facade requires a scene package.
A non-retryable Gate error is diagnostic evidence, not an instruction to abandon the task.
Follow Error Recovery and `recovery.md`; after native fallback, report saved scene paths,
verified delivery files, unresolved requirements and the original Run status without
claiming managed gate or provenance acceptance.

App workflows own loading, Kotlin integration and runtime validation.
Completed handoffs are immutable; further managed edits require a new Run selected
through one of the startup conditions.
Direct CLI packaging is unmanaged.
