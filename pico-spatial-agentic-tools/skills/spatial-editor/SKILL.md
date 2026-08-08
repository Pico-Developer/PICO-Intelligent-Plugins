---
name: spatial-editor
description: 'Preferred workflow for generating, creating, composing, or materially modifying 3D content in a Spatial app. Trigger for scenes, entities, models, asset composition, materials, lighting, effects, visual inspection, custom component declaration sync, or packaged editor-to-app handoff, even when the user does not mention Spatial Editor.'
license: 'Apache-2.0'
metadata:
  version: '1.0.0'
---

# Spatial Editor

Use Spatial Editor as the default 3D content-production step inside a broader Spatial app workflow. The editor owns scene state and authored assets; app code owns runtime interaction, business logic, build, install, and device validation.

## When To Use

Use this skill when the request needs one or more of:

- Editor-created scenes, entities, hierarchy, primitives, or object layout.
- 3D asset generation, import, conversion, repair, or visual tuning.
- Multi-object composition, materials, lighting, particles, animation, or other visual effects.
- Visual inspection or iterative adjustment of editor-authored content.
- A packaged editor handoff for a Spatial app.
- Synchronizing an app ECS component declaration for editor authoring.

Do not use it only for:

- SDK/API explanation, Kotlin/Compose work, Gradle repair, emulator/device work, or runtime crash debugging.
- Bounding-box measurement, scale estimation, transform planning, or layout JSON with no authored-content step.
- Loading an existing bundle when no editor content must change.

For mixed app and editor requests, complete the authored-content step here, then return the result to the app workflow.

## Allowed Exceptions

A 3D content-production step may skip this workflow only when:

1. The user explicitly asks not to use Spatial Editor.
2. Current runtime capability inspection shows that Spatial Editor cannot satisfy any part of the 3D content requirement.
3. Spatial Editor is actually unavailable because installation, download, startup, connection, authorization, or backend readiness failed and reasonable recovery steps did not restore it.

If Spatial Editor can satisfy any part of the requirement, use it for that part and return the remaining capability gaps to the app workflow. Exceptions 2 and 3 require runtime evidence. Report the capability result or failure and the recovery steps attempted; do not silently replace the entire editor step with App/ECS implementation.

## Runtime Contract

The plugin exposes a stable managed gateway through `pico-spatial-editor`. Its stable lifecycle and handoff tools are:

- `ensure_editor_ready`
- `get_editor_status`
- `show_editor_window`
- `stop_editor`
- `pack_editor_bundle`

Editor backend tools are dynamic. Read the tools visible in the current host session and choose capabilities by their runtime descriptions and schemas. Do not rely on backend tool names, arguments, or availability copied from this skill.

If the host does not show refreshed backend tools after the editor becomes ready, follow the bootstrap response and reconnect or restart the MCP session before continuing.

## Safety Rules

- Call `ensure_editor_ready` before any editor operation unless current managed status already reports `backendConnected=true`.
- Treat `backendConnected=false`, missing runtime tools, authorization failure, or startup failure as a blocker to scene mutation. Attempt the recovery directed by the gateway before returning an unavailable-editor exception.
- Never bypass the editor by directly authoring `.usd`, `.usda`, `.spatialproject`, or other editor-owned scene files.
- Inspect current editor state before mutation and verify the result afterward using the runtime capabilities available in the session.
- Use documented editor scripting APIs only. Read runtime documentation before generating a script, and keep batch scripts bounded.
- Preserve the current project and scene when the user asks to continue existing work.
- For new authored content, create and verify a task-specific scene before adding entities unless the user explicitly names an existing scene to modify.
- Do not place new content under a suspiciously scaled or stale root. Create a fresh scene or clarify the intended migration.

## Meter-Scale Scene Gate

Before importing, instantiating, visually previewing, screenshotting, or packaging
newly generated 3D content, verify the active task scene uses normal meter-scale
semantics:

- The scene metadata must declare meter-scale units, such as
  `metersPerUnit = 1`, and a known editor up axis.
- The authored root and every ancestor of the imported asset instance must have
  effective scale `(1, 1, 1)` unless the user explicitly requested migration of
  an existing scaled scene.
- Check the scene before import, after import, and again after save when the
  workflow depends on physical size or visual scale.
- If the active scene root or ancestor chain contains a scale such as `0.01`,
  stop using that scene for new content. Create a fresh task-specific scene or
  ask before migration/cleanup.
- Do not compensate for a scaled scene by applying an inverse scale such as
  `100` to the asset instance. Scene-scale problems are not model-generation
  failures and must not trigger another generation attempt.

## Scene Hierarchy Policy

Use hierarchy to express transform ownership and lifecycle ownership first, and
use functional categories to keep the scene understandable. Keep one normal
stage root with identity transform, and keep normal authored scene content as
descendants of it. "Below the root" does not mean every entity must be a direct
child. For a multi-object authored scene, choose identity-transform semantic
groups below that root according to the actual content and behavior. The
following tree is only a non-exhaustive illustration, not a required hierarchy
or naming schema:

```text
Root
  Environment
    Architecture
    Terrain
    StaticProps
  Actors
    Characters
    Animals
  DynamicObjects
    Vehicles
    MovingProps
  Interactables
  Effects
  RuntimeAnchors
```

Adapt, combine, rename, or omit these groups to match the task. Do not create
empty groups or reorganize an already coherent scene merely to reproduce this
example. Create only groups that serve the current scene, and give every entity
one primary parent.

Choose the documented node type according to its responsibility:

- Use an `Xform` when a group needs a shared transform or inherited state
  control.
- Use a `Scope` for pure organization when the group must not introduce a
  transform.
- Preserve specialized imported nodes such as mesh and skeletal hierarchy under
  a semantic wrapper instead of converting their internal types.

Top-level classification groups should normally keep identity transform.
Movable assembly roots and attachment nodes below them may use intentional local
transforms required by their behavior.

Choose the parent in this order:

1. If an entity has a clear owner and must inherit that owner's transform or
   lifecycle, place it below a stable semantic attachment or control node owned
   by that entity.
2. If several entities form one movable assembly, place them below one semantic
   assembly root.
3. Place autonomous characters and animals below an actor group.
4. Place non-autonomous moving objects, vehicles, and moving props below a
   dynamic-object group.
5. Place independent interactive objects below an interaction group when no
   owner or movable assembly already determines their parent.
6. Place static world content below an environment group.

Do not duplicate an entity across categories. Express secondary properties such
as interactive, grabbable, breakable, or selectable through runtime components,
metadata, or app logic when those capabilities exist.

Use a parent-child relationship only when inherited transform, active/visible
state, opacity, or lifecycle ownership is intended. Shared events, synchronized
animation commands, or common business state alone do not justify reparenting
independent entities; coordinate those relationships through runtime systems or
components.

For held, mounted, or equipped content:

- Parent it to a stable semantic anchor such as `RightHandAnchor`, not to an
  incidental generated mesh node.
- Preserve world transform when attaching or detaching, then author the required
  local offset relative to the anchor.
- When ownership ends, reparent it to the appropriate dynamic or interaction
  group while preserving world transform.

Keep imported model internals private. Prefer a semantic wrapper or assembly
root around the imported instance rather than rewriting generated asset
hierarchy. A single standalone preview asset may be a direct child of the stage
root, but do not leave every model as an unorganized direct child in a
multi-object production scene. Also avoid semantically empty wrapper chains that
add depth without transform, lifecycle, organization, or runtime-contract value.

When one model needs both a fixed import-axis correction and dynamic runtime
motion, separate those transform owners. Use a stable runtime-facing control
wrapper for dynamic position and rotation, and keep the imported visual as its
child with the fixed axis correction and verified source orientation. Do not
apply the fixed import correction and runtime yaw to the same node. This wrapper
is required only when those responsibilities differ; do not add it to static
content without a transform-ownership reason. Report the runtime control path,
visual child path, fixed correction, and verified asset-local forward/up axes in
the handoff.

Create a sibling of the normal stage root only when an explicit runtime,
packaging, export, or existing-scene contract requires multiple top-level
prims. Otherwise create semantic groups below the existing root.

Give runtime-facing nodes unique, stable, predictable semantic names. Use only
letters, digits, and underscores, with a letter or underscore as the first
character. Do not depend on a global name lookup returning the intended entity
when duplicate names exist; resolve from a known semantic parent or stable path
when the runtime supports it.

Before reorganizing existing content, inspect stable app-facing paths,
attachments, animation bindings, references, and ancestor transforms. Do not
silently break an existing runtime contract. After creation or reparenting,
verify the final parent path, absence of hierarchy cycles, preserved world
transform where required, effective active/visible state, inherited opacity,
world-space bounds, downstream lookup paths, and identity scale on the stage
root and top-level semantic groups. Report the resulting semantic hierarchy and
stable runtime-facing paths at handoff.

## AI Model Generation Attempt Limit

For each user-requested 3D asset, allow at most three generation attempts before
requiring a user decision. An attempt is any submitted model-generation task,
including one that fails, times out, or produces no asset. Changing provider,
prompt style, quality, polygon budget, or text/image generation does not reset
the counter and may still require prior user approval under the live runtime
tool instructions.

- Search `AI-Asset` and reuse a suitable existing asset before generating.
- Stop early when a generated candidate satisfies the user's explicit
  requirements. Do not consume the remaining attempts merely to improve an
  aesthetic preference or acceptance criterion that the user did not request.
- After each successful attempt, run the progressive Generated Model Visual
  Acceptance Gate below. Stop quality-only capture escalation after one valid
  standalone image passes, but continue orientation evidence when downstream
  behavior requires an unresolved asset-local forward/up basis. Do not generate
  another candidate without evidence that requires escalation. Treat subjective
  visual quality as a user decision.
- Before accepting, integrating, or packaging a newly generated candidate,
  complete the Generated Model Visual Acceptance Gate below.
- Before submitting a fourth attempt, remain headless, present each successful
  candidate's valid visual evidence and Project Browser path, summarize failed
  attempts, and ask the user to select a candidate, authorize more generation,
  or explicitly request GUI inspection.
- Call `show_editor_window` at this review point only when the user selects GUI
  inspection.
- If no candidate succeeded, stop after the third attempt, report the failures,
  and ask whether to continue without opening GUI automatically.
- Explicit approval to continue starts one new batch of at most three attempts.
  Apply the same review gate again; approval is not unlimited retry permission.

Do not package or integrate a candidate as the accepted result when multiple
candidates remain under review unless the user has selected one or the task has
an objective requirement that leaves only one valid candidate. Do not package
or integrate a visually unverified candidate. A request to reduce the screenshot
count does not waive the requirement for at least one valid standalone image
with `qualityVerdict=pass` for each accepted generated model.

## Generated USDZ Scale Adjustment (Editor Only)

Use this workflow only after Spatial Editor has generated a USDZ locally and the
current editor-authoring task requires importing that generated asset into the
active target scene at a user-specified physical height.

Do not use this workflow for planning-only transforms, structured layout
configuration, app-side runtime loading, or assets that were not generated by
the current Spatial Editor workflow. Those concerns remain outside this skill.

1. Confirm that the intended Spatial Editor target scene is active and passes
   the Meter-Scale Scene Gate.
2. Locate the exact generated USDZ source output and inspect its composed root
   USD stage. Record the effective `upAxis`, `metersPerUnit`, and raw X/Y/Z
   bounding-box extents. The source-asset bounding box is the sole dimensional
   evidence for native size.
3. Select the native height in stage units from the source stage's up axis:

   ```text
   upAxis = Y: nativeHeightInStageUnits = Y extent
   upAxis = Z: nativeHeightInStageUnits = Z extent
   ```

   Then normalize it to meters:

   ```text
   nativeAssetHeightMeters =
     nativeHeightInStageUnits * metersPerUnit
   ```

   Require positive finite values for `metersPerUnit` and
   `nativeAssetHeightMeters`. Do not infer native dimensions from a Spatial
   Editor instance, screenshot, container size, or visual estimate. If the
   effective metadata or source bounding box cannot be obtained, stop and report
   the blocker instead of applying a guessed scale.

4. Apply a non-default scale only when the user explicitly specifies a positive
   finite `targetHeightMeters`. Calculate:

   ```text
   editorRootScale = targetHeightMeters / nativeAssetHeightMeters
   ```

   `editorRootScale` belongs only to this Spatial Editor target-scene operation;
   it is not app-side runtime configuration.

5. Import or instantiate the generated USDZ once with root scale `(1, 1, 1)`,
   then apply `editorRootScale` exactly once.
6. Query that same target-scene instance's world-space bounds after scaling and
   use the target scene's declared up axis to verify that its final height matches
   `targetHeightMeters`. Use instance bounds only for final-result verification,
   never as native-size input or as the basis for a second compensating scale.
7. Save the target scene after verification.
8. Record every non-default scale in the consuming project's `AGENTS.md`,
   including the source metadata and dimensions, target dimensions, exact scale,
   and verification evidence.
9. Report the target scene, generated asset path, source `upAxis`,
   `metersPerUnit`, source bounding box, selected height axis, calculated scale,
   and verified final bounds in the editor handoff.

## Visual Inspection Strategy

Use this strategy when inspecting a standalone model, determining model
orientation, validating model placement, or reviewing scene composition. Read
the live screenshot and camera schemas first; do not invent unsupported
parameters.

### Generated Model Visual Acceptance Gate

Every newly generated model that is about to be accepted, integrated, or
packaged must be inspected as a standalone asset. The gate passes only when the
current asset fingerprint has at least one valid isolated, target-framed image
with `qualityVerdict=pass`. Scene-composition screenshots, bounds queries,
source-asset inspection, and successful packaging cannot substitute for this
standalone visual evidence.

Actually inspect image content; file existence, readback, byte count, and
resolution are insufficient. Create a structured evidence record for every
captured image used in the decision containing:

```text
imagePath
captureSucceeded
imageActuallyInspected
targetPresent
fullyFramed
cameraFrame
cameraDirection
semanticView
visibleDefects
qualityVerdict
frameAppliedReported
framingVerified
cameraPosition
cameraForward
targetCenter
imageHash
stateRestored
```

Use only `pass`, `fail`, `inconclusive`, or `unverified` for `qualityVerdict`.
It cannot be `pass` unless `imageActuallyInspected`, `targetPresent`, and
`fullyFramed` are all true and no objective defect violates an explicit
requirement. If the host cannot inspect image content, set
`imageActuallyInspected=false` and `qualityVerdict=unverified`; do not claim
visual acceptance.

Maintain one model-level acceptance record for every distinct generated asset
fingerprint:

```text
assetPath
assetFingerprint
passedEvidencePath
modelVisualVerdict
frontViewRequired
frontEvidencePath
orientationRequired
orientationVerdict
localForwardAxis
localUpAxis
orientationEvidencePaths
```

Set `modelVisualVerdict=pass` only when `passedEvidencePath` identifies an
existing standalone image whose evidence record has `qualityVerdict=pass` for
the same current `assetFingerprint`. Replacing or modifying the asset invalidates
the record and requires new evidence. Use only `verified`, `inconclusive`, or
`not_required` for `orientationVerdict`. A passing model-quality verdict does
not imply verified orientation.

Set `frontViewRequired=true` when the model has a discernible semantic front,
including people, animals, vehicles, buildings with an entrance facade,
directional props, and controls with a user-facing side. Set it to `false` only
when the model genuinely has no meaningful front, such as an amorphous rock or
a rotationally symmetric prop; an unknown front is not evidence that no front
exists. When `frontViewRequired=true`, `modelVisualVerdict=pass` additionally
requires `frontEvidencePath` to identify a valid passing standalone image with
`semanticView=front` or `semanticView=front_three_quarter`. The semantic front
features must be visibly unobscured, and that image must also be used as
`passedEvidencePath`. A fixed automatic view from the rear or an unidentified
candidate direction cannot close the acceptance gate.

Before integration or packaging, enumerate every distinct newly generated asset
fingerprint referenced by the intended scene or package and reconcile it
one-to-one with these records. Stop when any model is missing a current
`passedEvidencePath`; do not use final-scene evidence as a replacement.

### Evidence Validity Gate

Before capture, resolve the exact inspection root and target subtree. Confirm
the target is effectively active and visible through its ancestor chain and has
valid world-space visual bounds with finite min/max, center, and non-zero
extent. Stop and diagnose the target state when these checks fail.

A successful capture call or an existing PNG proves only that image readback
succeeded. Before using a screenshot as evidence, inspect the image and confirm
that the intended target is present, fully framed for the current check, and not
replaced by an empty frame, grid, background, or unrelated object.

A reported `frameApplied=true` proves only that the backend accepted or attempted
the framing request. It is not proof that the offscreen camera actually points
at the target or that the target appears in the image.

If a capture reports that entity framing was skipped, not applied, or
overridden by explicit camera parameters, correct the capture and repeat it.
Missing views, invalid framing, occlusion, or an empty image are capture
problems, not model-generation failures. They must not consume the generation
attempt budget or trigger regeneration.

### Capture Execution Hard Gate

Run every model and scene capture serially. Complete validation and the evidence
record for one image before issuing the next capture request. A user request to
"only recapture files" or skip a quality verdict may waive the final verdict,
but it does not waive target resolution, required standalone isolation, camera
sanity checks, serial execution, or state restoration.

After every capture:

1. Compare the requested inspection frame, direction, target center, and camera
   distance with the returned camera state when the runtime provides it.
2. Using the runtime-documented camera-forward convention, calculate:

   ```text
   toTarget = normalize(targetCenter - cameraPosition)
   alignment = dot(normalize(cameraForward), toTarget)
   ```

   Treat the camera as misdirected when the vectors are not closely aligned.
   A tolerance around five degrees (`alignment < cos(5 degrees)`) is a useful
   default unless the runtime declares another tolerance.

3. Confirm the camera is outside the target bounds and, when camera intrinsics
   and projection data are available, that the target's projected bounds lie
   inside the image with the required `frameFill`. Otherwise use actual
   image-content inspection as the framing authority.
4. Actually inspect the image content and complete all evidence fields. Tool
   metadata cannot set `imageActuallyInspected`, `targetPresent`,
   `fullyFramed`, or `qualityVerdict=pass` by itself.
5. Compare `imageHash` with other required views. Treat exact duplicate hashes
   for different requested camera directions as a capture-state failure by
   default. Accept them only when independently verified camera states differ
   as requested and documented model symmetry explains the identical image;
   otherwise correct camera state and recapture.

If `frameAppliedReported=true` but camera alignment, projected bounds, or image
content is invalid, set `framingVerified=false` and do not count the image as
standalone evidence. Retry with an explicit camera that looks at the verified
world-space bounds center, uses the calculated distance, and omits entity
framing parameters. If the host cannot inspect the image, keep the saved file
only as an unverified artifact and stop before acceptance, integration, or
packaging.

When both an exact camera position and target are known, use
`camera_mode="look_at"` with `frame="none"`, `camera_position`, and either
`camera_target` or `camera_entity_path`. Do not calculate or pass
`camera_rotation_euler` for this path. Use `set_transform` only with a complete
`camera_position` plus `camera_rotation_euler` pair. Provide `camera_up` when
the requested direction is vertical or otherwise makes the default up vector
ambiguous.

### Camera Coordinate Frame And Distance

Use the center `C` of the final world-space visual bounds as the camera target,
not the entity transform origin. Define `view_from_+X` to mean that the camera
is on the target's positive X side and looks toward `C`.

- For intrinsic generation-quality inspection or semantic model-orientation
  detection, derive camera directions from the model-local axes transformed by
  the final instance rotation, including any import axis-conversion root.
  Normalize the transformed basis so scale does not distort direction.
- For placement-direction and scene-layout inspection, derive camera directions
  from the scene world axes.

For a requested unit direction `n` from the target center to the camera:

```text
cameraPosition = C + n * d
lookAt = C
```

Choose an up vector that is not parallel to the viewing direction, especially
for top and bottom views, then build an orthonormal camera basis.

For a perspective camera with vertical FOV `Fv` and aspect ratio `A`, derive:

```text
Fh = 2 * atan(A * tan(Fv / 2))
```

Project the inspected bounds into the chosen camera basis. Let `W`, `H`, and
`D` be its projected half-width, half-height, and half-depth. Let `frameFill`
be the target fraction of the available half-viewport occupied by the projected
bounds. Use:

```text
d = D + max(
  W / (frameFill * tan(Fh / 2)),
  H / (frameFill * tan(Fv / 2))
)
```

Use `frameFill` between `0.9` and `1.0`, preferring `0.9` for normal validation,
and ensure `d - D` remains beyond the near clip plane. A lower `frameFill`
moves the camera farther away and leaves more visible border. If only a
bounding-sphere radius `R` is available, use:

```text
d = R / sin(frameFill * min(Fh, Fv) / 2)
```

When no reliable FOV is available, use `2 * R / frameFill` only as an initial
fallback. Validate the resulting image and increase the distance when the target
is clipped. Prefer runtime entity framing over this fallback. For an
orthographic camera, divide the fitted projected half-size by `frameFill`
instead of using perspective distance as the framing control.

### Standalone Model And Orientation Inspection

Use progressive evidence rather than always taking six views:

1. Isolate the model, resolve its final bounds and import-axis transforms, and
   decide `frontViewRequired` before accepting any image. Reuse persisted
   `localForwardAxis` and `localUpAxis` only when their evidence matches the
   current `assetFingerprint`.
2. When semantic forward `F` and up `U` are already verified, make the first
   quality capture a front-dominant three-quarter view. Transform `F` and `U`
   through the final model rotation, derive `right=normalize(cross(F, U))`, and
   use:

   ```text
   frontThreeQuarter = normalize(F - 0.35 * right + 0.20 * U)
   cameraPosition = C + frontThreeQuarter * d
   cameraTarget = C
   ```

   Capture with explicit `camera_mode="look_at"` and `frame="none"`, using the
   calculated bounds-fitting distance and transformed `U` as `camera_up`. Record
   `semanticView=front_three_quarter`. If the front features are not clearly
   visible from that offset, recapture directly from `F` and record
   `semanticView=front`.

3. When semantic forward is not yet verified, capture one candidate standalone
   image from model-local `(1, 1, 1)` using an explicit bounds-centered
   `look_at` camera. Label it only as a candidate direction. Do not use
   `camera_mode="auto"` or `frame="entity"` as final front evidence: their
   backend default yaw and pitch are fixed framing choices, not a determination
   of the model's semantic front.
4. Actually inspect the initial image and complete its evidence record. If it
   has `qualityVerdict=pass` and `frontViewRequired=false`, set
   `modelVisualVerdict=pass` and store its path as `passedEvidencePath`. If
   `frontViewRequired=true`, pass only when the image visibly establishes the
   front and is labeled `front` or `front_three_quarter`; store the same path as
   both `frontEvidencePath` and `passedEvidencePath`. A passing rear or candidate
   image may stop additional quality-only views, but it cannot set the
   model-level verdict to pass; continue only the views needed to identify and
   capture the front.
5. Before ending inspection, determine whether downstream behavior depends on
   an asset-local forward/up basis, including path following, facing a target,
   directional animation, spawning, attachment, or runtime yaw. Set
   `orientationVerdict=not_required` only when no such behavior or contract
   exists. Direction-dependent models must have `orientationVerdict=verified`
   with explicit `localForwardAxis` and `localUpAxis` before the agent authors,
   accepts, or packages any direction-dependent runtime logic.
   If orientation remains inconclusive, pause that integration and request a
   user decision; do not guess an axis or regenerate the model for uncertainty
   alone.
6. If the initial capture or framing is invalid, correct it and recapture the
   same evidence; this is not a model failure. If the valid inspected image is
   `unverified`, stop before acceptance unless image inspection can be restored.
7. If the valid inspected image is `fail` or `inconclusive`, if a required front
   has not been identified, or if required orientation remains `inconclusive`,
   complete a complementary `diagonal_A` and `diagonal_B` pair. Capture
   `diagonal_A` from model-local direction `(1, 1, 1)`, transforming it through
   the final model rotation, including import axis-conversion roots, and
   normalizing it:

   ```text
   localA = normalize((1, 1, 1))
   nA = normalize(transformDirection(finalModelRotation, localA))
   ```

   Capture `diagonal_B` from model-local direction `(-1, -1, -1)`, strictly
   opposite to `diagonal_A`:

   ```text
   localB = normalize((-1, -1, -1))
   nB = normalize(transformDirection(finalModelRotation, localB))
   dot(nA, nB) <= -0.999
   ```

   Use the same target center and `frameFill` for both views. A valid initial
   image from the exact `diagonal_A` direction may serve as `diagonal_A`; do not
   capture it again.

8. Inspect the pair separately for visual quality and intrinsic orientation. If
   sufficient valid evidence proves the explicit quality requirements with no
   objective defect, preserve the passing image-level verdict. Set
   `modelVisualVerdict=pass` immediately only when no front view is required.
   If the pair confirms an objective model defect, set `modelVisualVerdict=fail`;
   only then may regeneration begin. When the front or required orientation
   remains `inconclusive`, capture serial local-axis views as needed in this
   order: `+X`, `-X`, `+Y`, `-Y`, `+Z`, `-Z`. Inconclusive orientation, invalid
   capture, or unverified evidence must not trigger regeneration.
9. Label axis views as candidate directions, not front/back/left/right, until a
   screen, face, door, control panel, label, head/tail, or another semantic
   feature establishes the model's front.
10. After identifying semantic forward and up, capture one dedicated front or
    front-dominant three-quarter image with the explicit camera formula above.
    Actually verify that the semantic front is visible, set
    `frontEvidencePath`, and use this passing image as `passedEvidencePath`.
    This final capture is mandatory when `frontViewRequired=true`, even when an
    earlier rear or candidate image already proved mesh and material quality.

When escalation requires the `diagonal_A` and `diagonal_B` pair, it always uses
the model-local frame, including when later work checks scene placement. After
that pair resolves the generation-quality question, placement-direction
validation may add world-space views.

Before semantic orientation is established, file names and evidence labels may
use only candidate-axis names such as `diagonal_A`, `diagonal_B`, or
`view_from_+X`; they must not use front/back/left/right. Once verified semantic
forward `F` and up `U` are available, derive a right-handed semantic basis and
the requested opposite diagonal pair:

```text
right = normalize(cross(F, U))
frontLeftUpper = normalize(F - right + U)
backRightLower = -frontLeftUpper
```

For every image, record whether `cameraFrame` is `model_local` or `world`, the
normalized camera direction in that frame, and the world-space target center.
Apply all import and axis-conversion roots before deriving model-local camera
directions; this rule is provider-independent.

Do not infer asset-local forward from an evidence label such as "angled rear
view", from a scene instance's current yaw, or from an assumed provider default.
A single image may verify orientation only when its known model-local camera
direction and visible semantic features uniquely establish forward and up.
Downstream runtime code must consume the verified asset-local axes or an
equivalent fixed correction; it must not assume `+Z`, `+X`, or a hard-coded yaw
formula without that evidence.

Do not assume world yaw `0` or `180` corresponds to the model's semantic front.
Stop escalating views once existing evidence proves the explicit observable
requirements. Regenerate only when sufficient valid evidence proves an
objective mismatch. Treat subjective visual quality as a user decision. Present
the valid headless evidence first and ask the user to accept the candidate,
authorize another attempt, or explicitly request GUI inspection.

### Inspection Isolation And Restoration

Isolate a target only for standalone model-quality or intrinsic-orientation
inspection. Do not hide context required for placement or scene-composition
evaluation.

Standalone recapture remains an isolation workflow even when the user does not
request a new quality verdict. Skipping validation never authorizes unrelated
scene content to remain visible or allows restoration to be skipped.

Isolation is a temporary visibility-state operation, not a layout operation.
Never isolate by translating entities far away, or by changing position,
rotation, scale, hierarchy, or parent paths of the target, its ancestors, or
unrelated content. Moving an entity by 100 meters, 10 kilometers, or any other
distance is not visual isolation.

Prefer a runtime capture-only isolation capability when available. Otherwise:

1. Snapshot the exact active, enabled, and visible state of every entity that
   may be changed. Also record the transform and parent path of the target, its
   ancestors, and every entity whose state will be changed so forbidden layout
   mutations can be detected during restoration.
2. Keep the target subtree and its complete ancestor chain enabled and visible.
   Hide only unrelated entities. Do not compare only scene-root paths, because
   a nested target would lose its required parent.
3. Perform captures without saving or packaging the temporary isolated state.
   Do not mark the scene's temporary isolation state as authored content.
4. Restore every captured state in a guaranteed cleanup step, including after
   capture failure.
5. Re-query the scene and compare active, enabled, visible, transform, parent
   path, and relevant bounds with the snapshot before setting
   `stateRestored=true`. Treat any mismatch as a blocker to further scene
   mutation or packaging.

If the temporary isolation state was accidentally saved, keep
`stateRestored=false`, restore and verify the original state, then save the
restored scene before continuing. A visually valid screenshot may remain image
evidence, but it cannot claim successful state restoration until this recovery
is complete.

### Scene Composition Inspection

Unlike standalone-model inspection, scene-composition inspection always starts
with three valid serial images: `baseline`, `diagonal_A`, and `diagonal_B`. A
passing baseline does not waive either diagonal.

1. Capture `baseline` from the resolved user viewpoint with the intended scene
   composition visible. Resolve that viewpoint in this order: an explicit
   user-provided view, a verified User/Camera/Spawn anchor, scene metadata, then
   the default fallback. Use `(0, 1.6, 0)` looking toward world `-Z` only for a
   confirmed Y-up scene using the default forward convention; otherwise convert
   the fallback through the verified scene up/forward axes.
2. Compute the center and framing distance from the bounds of the scene content
   relevant to the layout check. Capture `diagonal_A` from world-space direction
   `normalize((1, 1, 1))`.
3. Capture `diagonal_B` from world-space direction
   `normalize((-1, -1, -1))`, using the same target center and `frameFill`.
   Verify `dot(diagonal_A, diagonal_B) <= -0.999`.

Actually inspect all three images and complete an evidence record for each.
Do not pass scene visual inspection when any required image is invalid,
unverified, or missing. Add serial world-axis views from `+X`, `-X`, `+Y`,
`-Y`, `+Z`, and `-Z` only when the mandatory three-image set is insufficient
for an explicit scene-layout requirement.

- Use world-space directions for scene-layout evidence.
- Exclude sky, water, background shells, and other enclosing objects from
  diagnostic layout bounds when they dominate framing or occlude interior
  content. Temporarily hide an enclosing object only when inspecting content
  inside it; retain it when inspecting the enclosing object itself.
- After diagnostic isolation, restore all enclosing content and verify the
  restored scene state. If the baseline was invalidated by a scene change,
  recapture and inspect it; do not retain stale baseline evidence.

Check required visibility, relative scale, placement, unintended overlap,
floating/sinking, occlusion, and navigation or interaction clearance against
the user's explicit requirements.

All model and scene screenshots must run serially. Screenshot operations share
camera and render state; parallel requests can overwrite camera parameters,
reuse the wrong frame, or produce multiple files from the same view.

### Orientation Evidence Record

After intrinsic model orientation is established, persist reusable evidence in
project metadata at `.spatialsdk/asset_orientations.json` when the workspace is
writable. Record at least:

```text
assetPath
assetFingerprint
orientationVerdict
localForwardAxis
localUpAxis
semanticFeatures
evidenceViews
confidence
```

Record asset-local orientation, not a scene instance's world rotation. Reuse
the record only when the asset fingerprint still matches; changed assets
require new evidence. If persistence is unavailable, return the same fields in
the handoff and state that orientation must be revalidated in a future session.

### Session Mode Hard Rule

Use a managed headless session by default. Start with `open_gui=false` unless
one of these allowlisted conditions already applies:

1. The user explicitly requests that the current or subsequent Editor workflow
   run in GUI mode, including manual inspection or editing.
2. Authentication, login, provider API-key entry, settings, or another required
   operation is confirmed to be GUI-only.
3. Offscreen capture is unsupported or still fails after the required
   capability check and retry.
4. An essential runtime tool explicitly reports `requiresGui=true` and no
   headless-compatible alternative exists.

Subjective quality review alone does not authorize GUI when the agent can
inspect valid offscreen images or present them to the user. After a temporary
GUI-only operation completes, treat the exception as a scoped state transition,
not as a sticky session preference. Unless the user explicitly requests that
subsequent work continue in GUI mode, complete this sequence before any
generation, capture, scene mutation, or packaging call:

1. Record the active project identity before switching to GUI.
2. Perform only the required GUI-only operation and wait for user confirmation
   when manual authentication, API-key entry, or provider configuration is
   involved.
3. Treat confirmation such as "configured" or "done" as the end of the GUI
   exception. Do not call `generate_3d_model` or another normal editor operation
   while reconnecting in GUI mode.
4. Wait for existing asynchronous tasks to become terminal and save the scene.
5. Explicitly call `ensure_editor_ready(open_gui=false)` for the same project.
   Omitting `open_gui` is forbidden here because it preserves the current GUI
   mode.
6. Call `get_editor_status` and require `sessionMode=headless`,
   `backendConnected=true`, and the same active project identity.
7. Resume generation or other automated work only after all checks pass.

Any mismatch is a blocker to subsequent automated editor work. Retry or report
the mode-switch failure; do not silently continue with `open_gui=true`.
Preserve GUI when the user explicitly requested that subsequent work continue
in GUI mode.

Calling `show_editor_window` outside this allowlist is a workflow violation.

### Screenshot Capture Mode

Before screenshot capture, inspect the live runtime tool schema and editor
capabilities when available. If the runtime exposes `get_editor_capabilities`,
call it before choosing capture parameters. Use `get_editor_status` when session
mode is uncertain.

- In headless mode, use `capture_mode="auto"` or `capture_mode="offscreen"`.
  Never force `capture_mode="viewport"` in a no-graphics session.
- In GUI mode, use `capture_mode="auto"` or `capture_mode="viewport"` unless
  the runtime schema recommends another available mode.
- Do not infer capture-mode support from the tool name. A tool named like
  `get_viewport_screenshot` may still support offscreen capture; the live schema
  and capability metadata are authoritative.
- If a headless screenshot fails with an error such as
  `capture_mode=viewport is unavailable in no-graphics mode`, retry once with
  `capture_mode="offscreen"` or `capture_mode="auto"` before considering GUI.
- Treat viewport-mode failure in headless as a capture-parameter error, not as
  proof that headless screenshots are unsupported.
- Open or switch to GUI for screenshots only under the Session Mode Hard Rule
  allowlist.

Screenshot capture errors, framing problems, or capture-mode mistakes are not
model-generation failures and must not trigger regeneration or consume the
generation-attempt budget.

## Async Task Liveness And Managed Cleanup

Start a managed headless Editor only immediately before the next step requires a
real Editor backend operation. Do not start or keep a headless session for
planning, explanation, app-code work, Gradle builds, web research, local image
inspection, or other work that does not require Editor.

After submitting an asynchronous Editor task:

1. Use the corresponding status capability declared by the live runtime schema
   until the task reaches a runtime-declared terminal state such as completed,
   failed, errored, or cancelled.
2. Poll every 20-30 seconds by default. When the actual headless idle timeout is
   known, keep the interval below half of that timeout; with the current
   two-minute default, never allow more than 60 seconds between Editor MCP
   status calls.
3. A short shell wait may separate polls, but shell waits and non-Editor tools
   do not keep the Editor session active and cannot replace status polling.
4. While a task is pending, do not start a blocking non-Editor operation that
   could exceed the next poll deadline. Finish the polling loop first.
5. Do not call `stop_editor`, `show_editor_window`, switch session mode, or
   switch projects while a task is pending. If the user asks to stop, use the
   runtime-declared cancellation capability when available and wait for a
   terminal result before changing the managed session.

Keep this polling in the foreground managed workflow. Do not create detached
shell loops, background keepalive jobs, independent Editor processes, or a
second managed session. A long-running Editor MCP call already in flight does
not require a separate keepalive loop.

If polling reports that the Editor restarted or the task is not found, do not
immediately submit a replacement task. First inspect `AI-Asset` and the expected
output path for an artifact already written by the original task. Any actual
resubmission remains part of the same generation-attempt budget.

Once no asynchronous task remains, do not send artificial keepalive calls. If
more Editor work is immediately required, continue it in the same managed
session. Otherwise save the current scene and call `stop_editor` before
performing lengthy non-Editor work, returning control, or completing a headless
workflow. Open the GUI for candidate review only after all submitted tasks are
terminal; an intentionally retained GUI session is user-visible and is not a
headless keepalive session.

## Workflow

1. Determine whether the request includes 3D content production or only planning, app code, or runtime control of existing content.
2. If the user explicitly rejects Spatial Editor, return that exception to the calling workflow without starting it.
3. Call `ensure_editor_ready`.
4. Confirm `backendConnected=true` and record the resolved project and session mode.
5. Read the live runtime capabilities, tool schemas, and editor documentation needed for the task.
6. Partition the requirement into supported and unsupported editor work. Continue with every supported 3D content step; return only unsupported portions to the app workflow.
7. For new content, create or switch to a task-specific scene and verify meter-scale assumptions.
8. Create, import, arrange, inspect, and save content through runtime editor capabilities.
9. Verify scene state and visual output with the live query or capture capabilities.
10. If downstream app integration is required, call `pack_editor_bundle`.
11. Before returning control to the user or a downstream workflow, close an active headless session with `stop_editor`.
12. Return the authored scene path, stable runtime-facing node contract, package paths, unsupported portions, exception evidence, and warnings to the calling app workflow.

## Session Behavior

`ensure_editor_ready` should be the default entry:

- Reuse a compatible managed editor installation and project when possible.
- Use an explicitly supplied `project_path` when the user provides one.
- Otherwise scan the workspace, or create the managed default project when none exists.
- First launch is headless unless the Session Mode Hard Rule allowlist already applies.
- `open_gui=true` targets a GUI session. Omitting it preserves the current managed mode when a session already exists.
- Switching project or session mode may save, stop, restart, and reconnect the managed editor.

Continue with scene operations only after managed/backend readiness succeeds. A visible window without `backendConnected=true` is not sufficient.

Use `show_editor_window` only under the Session Mode Hard Rule allowlist. A generic request to inspect or verify visual quality does not imply GUI mode; use valid offscreen evidence first. Keep GUI when the user explicitly requests that the current or subsequent workflow run in GUI mode. Return to headless after a temporary GUI-only operation as required by the hard rule.

Treat returning a final response, asking the user for the next decision, or handing packaged output to a downstream workflow as the end of the current editor lifecycle:

- If the active session is headless, call `stop_editor` before yielding control. Do this after the final save, verification, or `pack_editor_bundle` call.
- Preserve an active GUI session when the user explicitly requested that the current or subsequent workflow run in GUI mode, so the user can continue and close it manually. A temporary GUI-only operation should already have returned to headless.
- If session mode is uncertain, call `get_editor_status` before deciding whether to stop it.
- Do not rely on the headless idle timeout for normal cleanup; it is only a fallback for interrupted or failed workflows.
- Do not use arbitrary process termination as the normal workflow.

## App-Compatible Project Layout

When working from a Spatial app root, prefer:

```text
<appRoot>/editor-asset/src/main/res3d/SpatialPackContent
<appRoot>/editor-asset/src/main/res3d/SpatialPackContent/SpatialPackContent.spatialproject
```

Resolution order:

1. Use the user's explicit editor project path.
2. Search `<appRoot>/editor-asset/src/main/res3d/*/*.spatialproject`.
3. Open a unique match.
4. Create the default `SpatialPackContent` project when no match exists.
5. Ask the user to choose only when multiple candidates exist or the workspace root is genuinely ambiguous.

## Editor-To-App Handoff

Before packaging, define the smallest stable asset contract required by app code:

- Name only runtime-facing roots, anchors, attachment points, or control nodes.
- Keep decorative and construction hierarchy private to the authored asset.
- Use semantic stable names; do not expose generated names or incidental ordering.

Save through runtime editor capability, then call `pack_editor_bundle`. A successful handoff returns co-located:

- `<bundleName>.bundle`
- `<bundleName>.scenes.json`

Report `bundlePath`, `scenesPath`, intended entry scene, runtime-facing node names, container/runtime-fit notes, and warnings. App-side copying, loading code, build, install, and emulator/device verification belong to `spatial-app-dev-workflow`.

## Custom Component Declaration

When an app ECS component must be selectable in Spatial Editor:

1. Use the stable CLI component sync capability through `pico-cli editor sync component`.
2. Do not hand-edit `.Component/component.json`.
3. Report whether the declaration was added, updated, or skipped.
4. Return to the app workflow for runtime registration, build, and validation.

Successful declaration sync proves editor metadata was updated; it does not prove app runtime behavior.

## Completion Evidence

Report:

- Resolved editor project and authored scene.
- Managed session mode and backend readiness.
- Authored or changed content.
- Runtime inspection or visual evidence used for verification.
- Package paths and asset contract when integration is needed.
- Unsupported portions and the runtime capability evidence for them.
- Any editor availability failure and the recovery steps attempted.
- Warnings, reconnect requirements, or exact blockers.
