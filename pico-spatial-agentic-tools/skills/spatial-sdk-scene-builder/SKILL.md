---
name: spatial-sdk-scene-builder
description: Implements and repairs code-owned Entity scenes in a PICO Spatial Android/Kotlin app, including loading, hierarchy, transforms, placement, alignment, clipping, and validation. For a feature-bearing new app, use only after spatial-design-to-app and spatial-app-onboarding establish an accepted design and scaffold. Use spatial-editor for new or revised Editor-authored content. When an existing `.bundle` and `.scenes.json` pair needs app integration, this skill may handle the Kotlin Entity step within the enclosing app integration workflow. Do not infer Kotlin ownership merely because an app will consume Editor-authored content.
license: 'Apache-2.0'
---

# Build 3D Scenes with PICO Spatial SDK

## Outcome

Implement the requested scene outcome as PICO Spatial SDK Kotlin code. Select
the request scope before editing:

- **Complete-scene mode:** create, assemble, reproduce, or materially revise the
  requested scene and own the complete runnable result.
- **Focused-placement mode:** repair or implement the requested placement of one
  Entity or a bounded subset inside an existing scene. Preserve unrelated
  hierarchy, composition, behavior, and transforms; do not expand the request
  into a full-scene redesign.

Both modes are first-class uses of this skill. Static placement is not a reason
to route away from this skill when Kotlin code owns the Entity. Lights,
particle emitters, and other effect-bearing Entities remain in scope when the
task is to create, attach, transform, or validate them in code.

A transform plan or coordinate calculation is supporting evidence, not the
implemented result. If a feature-bearing request starts from an empty directory,
enter through `spatial-design-to-app` and its executable-design gate. That workflow
may use `spatial-app-onboarding` only to establish the scaffold; resume this skill
for scene implementation after the accepted design and scaffold exist. A genuinely
featureless scaffold or first-runnable demo may use onboarding directly. Existing
apps that request a local Entity change stay in this skill and do not re-enter the
new-app design gate.

## Ownership Boundary

- Use this skill when the requested deliverable is Kotlin code that owns Entity
  creation or loading, hierarchy, transforms, bounds-aware relationships, or
  scene validation.
- Use `spatial-editor` when the requested deliverable is an editor-authored
  scene, model or effect resource, visual composition/tuning, or packaged
  editor content.
- Do not infer Kotlin ownership merely because authored content will later be
  used by an app. A generic request to create a visual 3D scene remains an
  Editor task unless Kotlin/Spatial SDK Entity implementation is also requested.
- When both are required, use Spatial Editor for authored content and return to
  this skill for Kotlin Entity integration and placement.
- Use `spatial-sdk-guideline` for broader API behavior such as light parameters,
  particle-system behavior, materials, animation, physics, and interaction;
  this skill still owns the participating Entities' hierarchy and transforms.

The ownership and capability lists above classify work; they do not prescribe scene
content. Create, preserve, reject, or route an Entity or relationship only when the
current request, accepted scene contract, asset evidence, or existing implementation
requires it. Do not turn a listed capability or example relationship into a default
object, layout, or acceptance condition.

## SDK Knowledge Support

`pico-dev-knowledge` is available for Spatial SDK documentation, API facts,
examples, and version-related context. Before choosing or implementing a new or
non-trivial Spatial SDK API, first identify the project's exact SDK version from
its local declarations, then call `pico-dev-knowledge` `query_graph` for that
version. This is required for API availability and semantics that are easy to misapply,
including ECS Systems and Components, units, SpatialView and WindowContainer
coordinate spaces, owner-relative visual bounds, `getVisualBounds`, public
coordinate conversion, transform ownership, lifecycle, and threading.

Do not require a knowledge query for a simple edit that only changes existing
project values without choosing or interpreting an SDK API. If the matching
knowledge query is unavailable, returns no result, or does not answer the needed
fact, only then inspect the project's installed public SDK artifacts or run a
focused compile/runtime experiment. AAR/JAR extraction or public-signature
inspection is last-resort evidence: do not inspect private members or depend on
decompiled-only APIs, and do not infer units, lifecycle, threading, or recommended
usage from a method signature. Report any unresolved semantic gap instead of
guessing. Combine retrieved facts with project-local evidence and this skill's
workflow references; neither a lookup nor a signature alone is runtime proof.

The managed Workflow may enter the Builder/Codegen Handoff before this research
is complete. Stay in that Handoff while resolving the project version and API
evidence: before the first Kotlin write or `spatialcraft.spatial-codegen-change-set/v1`
submission, identify the version, call `query_graph`, and read the returned public
documentation or API-reference locations. A `query_graph` response that only
identifies candidate documents is not itself the API answer.

A minimal compile/runtime probe is allowed only when the knowledge query and public
documentation or signatures still cannot establish the needed fact and the user has
authorized that bounded experiment. It must use evidenced public signatures; do not
guess production symbols and use compiler errors as discovery. A later Gradle build
is verification, not permission to invent symbols and repair them by trial and error.
If knowledge is unavailable, empty, or insufficient, use AAR/public-signature
inspection only after that failed query. If public signature evidence still cannot
establish required units, lifecycle, threading, or other semantics, leave Kotlin
unchanged, remain in the current Handoff, and report the exact blocker.

## Workflow

Use the public `spatial-3d-generation` root Workflow for both complete-scene and
focused-placement work. Never start `spatial-codegen-workflow` directly and never
submit a Child Run ID.

1. **Start one managed root Run.** Call `start_3d_generation_workflow` with a
   `spatialcraft.spatial-3d-generation-input/v1` input. Set
   `backendPreference="codegen"` and `delivery.formats=["spatial-sdk-kotlin-scene"]`.
   For production, provide the absolute workspace root and existing Spatial SDK
   project path. For a revision, provide the completed parent root Run in
   `lineage.parentRunId`; the facade resolves Child lineage.
2. **Define the scoped contract.** Resume the initial Scene Spec Handoff through
   the returned `next.tool` and `next.arguments`. For a complete scene, identify all
   required objects, assets, hierarchy, proportions, behavior, and acceptance
   viewpoints. For focused placement, identify the target, reference or permitted
   region, allowed transform changes, and invariants that must remain untouched.
3. **Resolve evidence, then author during the Codegen Handoff.** When the returned Handoff requests
   Kotlin scene authoring, inspect project instructions, identify the SDK version,
   complete the knowledge/public-document sequence above, locate the active
   `SpatialView`, Stage, or `WindowContainer`, and preserve existing patterns.
   Create or load code-owned Entities only in the accepted scope. Return
   `spatialcraft.spatial-codegen-change-set/v1` with one workspace-relative Kotlin
   `sceneEntry` and the exact `changedFiles`; do not run Gradle yourself.
4. **Resolve spatial constraints in two stages.** First solve internal support,
   contact, containment, alignment, and anchor relationships in the base scene.
   Then, when the complete composition is bounded, apply one explicit uniform fit
   on `fittedSceneRoot` beneath an identity `placementOwner`. Measure final visual
   bounds in that owner, and re-measure after every applied transform.
5. **Let the Workflow validate and build.** Call the returned bounded wait tool.
   The deterministic Codegen modules validate path ownership and changed sources,
   run the project's fixed Gradle wrapper with JDK 21, and publish source/build
   artifacts and evidence. Never replace this with an arbitrary shell command or
   claim success from the authoring response.
6. **Inspect the terminal result.** Require `backend="codegen"`,
   `scene.format="spatial-sdk-kotlin-scene"`, a source entry Artifact, successful
   build Evidence, and no required acceptance error. Use `spatial-emulator-usage`
   separately only when device launch, screenshots, recordings, or runtime logs are
   also required.

Treat every response as one observation. Follow only the returned `next.tool`,
`next.arguments`, and `next.submission.inputSchema`; never infer a task ID, revision,
or wait duration. Handoff responses select `resume_3d_generation_workflow`. Use
`get_3d_generation_workflow_status` only for observation,
`wait_3d_generation_workflow` to wake retryable work, and
`cancel_3d_generation_workflow` only with the root Run ID.

## Invariants

- Use PICO axes consistently: `+X` right, `+Y` up, and `+Z` front/toward the
  user.
- Treat Z as spatial depth, not as a front-view visibility layer. Place a body
  by its support, container, contact, alignment, or explicit protrusion rule;
  do not move the whole body toward `+Z` merely to keep its silhouette visible.
  Surface details may protrude from their body when that relationship is
  explicit.
- Use public Spatial SDK APIs. Do not access library-restricted coordinate
  internals or reconstruct meters manually from pixels.
- Do not guess source bounds, units, pivot semantics, up axis, or model-forward
  direction. Keep unresolved facts explicit.
- Apply translation in the space that owns the Entity's
  `TransformComponent.position`; do not mix parent-local, view-local, and
  container coordinates.
- Interpret a user-stated directional distance as clear distance between final
  visual bounds unless the user explicitly requests a pivot or anchor distance.
  Do not substitute Entity origins for visual faces or centers.
- When the bounds owner differs from the target's immediate parent, convert the
  solved delta with public Entity `convertPositionTo/From` APIs before applying
  it. Do not invent world-matrix access or apply an owner-space delta directly
  to parent-local `position`.
- Permit and report uniform scaling by default when it improves fit or visual
  harmony. Preserve authored size only when the asset or accepted requirement
  explicitly marks it non-scalable or exact-size; if that object cannot fit,
  report no-fit and the conflict axis. Apply non-uniform scale only when the
  accepted contract explicitly permits distortion.
- Treat source-asset bounds and final Entity visual bounds as different
  evidence. Use the bundled source inspector when asset units or native size
  are unresolved; use fresh `getVisualBounds(owner)` results for final
  placement after hierarchy, scale, and orientation are applied.
- For USD/USDZ, inspect the composed source stage, `metersPerUnit`, and `upAxis`.
  Do not apply a generic `/100` conversion or infer native size from an Editor
  instance, screenshot, or container.
- Derive hard contact, containment, and gap results from the final body visual
  bounds, not a pivot, center point, hand-maintained envelope, or a union that
  already includes the target. Define supports, cavities, slots, and safe
  regions independently of their occupants.
- For bounded complete scenes, use the canonical hierarchy
  `SpatialView -> placementOwner (identity) -> fittedSceneRoot (fit transform)`.
  Express the safe region, planned final envelope, and remeasured visual bounds
  relative to the named `placementOwner`; apply the fit exactly once.
- Do not conceal no-fit, clipping, stale-bounds, or coordinate-space failures
  with arbitrary `Vector3` values, silent clamping, or silent scaling.

## Load Supporting Guidance

Read only the references required by the current scene, except where a row says
to read a reference before completion.

| Task condition                                                                                               | Required guidance                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Create a scene, change Entity loading, alter hierarchy, or manage scene lifecycle                            | Read [SDK scene authoring](references/sdk-scene-authoring.md) before implementation.                                                                           |
| Create repeated primitives or other programmatic resources                                                   | Read [primitive scene resources](references/primitive-scene-resources.md).                                                                                     |
| Asset dimensions, units, orientation, pivot, or scale are not verified                                       | Read [asset bounds and scale](references/asset-bounds-and-scale.md) and run `scripts/inspect_asset_bounds.py` when it can resolve the missing source evidence. |
| Parent chains, owner spaces, visual bounds, or logical regions affect a transform                            | Read [hierarchy and coordinate spaces](references/hierarchy-and-coordinate-spaces.md).                                                                         |
| Requirements include on/under/left/right/front/behind, alignment, gaps, containment, margins, or non-overlap | Read [placement constraint formulas](references/placement-constraint-formulas.md).                                                                             |
| A complete scene contains bodies, surface details, supports, containers, cavities, or trajectory anchors     | Read [three-axis scene semantics](references/scene-spatial-semantics.md) before assigning final transforms.                                                    |
| Placement depends on `SpatialView`, bounded `WindowContainer`, or their clipping intersection                | Read [SpatialView and WindowContainer bounds](references/spatialview-windowcontainer-bounds.md).                                                               |
| A complete composition must fit a SpatialView, bounded WindowContainer, or their intersection                | Read [runtime scene fit](references/runtime-scene-fit.md).                                                                                                     |
| The task explicitly requires an offline transform plan or `.spatialsdk/scene_transforms.json`                | Read [scene plan format](references/scene-plan-format.md).                                                                                                     |
| The scene is ready to build, run, inspect, or hand off                                                       | Read [scene validation](references/scene-validation.md) before declaring completion.                                                                           |

Use `spatial-sdk-guideline` for broader SDK features such as material behavior,
light parameters, particle behavior, animation, physics, and interaction. Use
`spatial-emulator-usage` for optional device launch and runtime evidence after the
managed Codegen build succeeds.

## Completion Contract

For complete-scene mode, report the scene root, important Entities, hierarchy,
assets, coordinate spaces, complete composition, and reviewed full-scene views.
For focused-placement mode, report the target, reference or region, preserved
invariants, changed source locations, and views that prove the requested local
relationship; do not claim unrelated parts of the scene were revalidated.

For both modes, report verified scale and orientation evidence, bounds sources,
runtime constraint results, build and launch status, relevant source-gate and
log findings, screenshot or recording paths, and any exact blocker. Separate
numeric constraint status from visual status. If an available capture cannot
reveal an important axis or relationship, report `visual=UNOBSERVED`; a front
view alone does not prove a relationship hidden along Z. Do not present a
coordinate list or transform JSON alone as an implemented result.
