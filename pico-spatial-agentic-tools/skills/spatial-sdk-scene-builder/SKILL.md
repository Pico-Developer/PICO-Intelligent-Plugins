---
name: spatial-sdk-scene-builder
description: Implements and repairs Entity-based 3D scenes in PICO Spatial Android/Kotlin code. Use when Kotlin must create or load, parent, position, rotate, scale, arrange, or validate one or more Spatial SDK Entities—a complete static or dynamic scene, or focused placement of one Entity or subset. Covers models, primitives, lights, particle/effect Entities, gaps, alignment, containment, non-overlap, and SpatialView or WindowContainer clipping. Also use for the 3D scene step of a new app requested from an empty directory, after spatial-app-onboarding establishes the project. Own code-defined hierarchy, transforms, bounds-aware placement, and validation. Use spatial-editor for editor-authored scene or asset content, visual authoring/tuning, or packaged editor handoffs; when both are needed, use each for its owned step. Do not infer Kotlin ownership merely because authored content will later be used by an app.
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
implemented result. If the request starts from an empty directory or an app
that has not completed its first runnable loop, use `spatial-app-onboarding` to
establish the project, then resume this skill for scene implementation.

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
examples, and version-related context. It can be consulted at any useful point.
Using it is neither a required step for every scene nor an action reserved for
late-stage failures. In particular, consider checking it for sensitive,
easy-to-misapply concepts such as SpatialView and WindowContainer coordinate
spaces, owner-relative visual bounds, `getVisualBounds`, public coordinate
conversion, transform ownership, lifecycle, and SDK-version API availability.
When used, combine the retrieved facts with project-local evidence and this
skill's workflow references; a lookup is not runtime proof.

## Workflow

1. **Establish the host app and scope.** If needed, complete onboarding first.
   Read project instructions, select complete-scene or focused-placement mode,
   locate the active `SpatialView`, Stage, or `WindowContainer`, find existing
   Entity and asset-loading patterns, and preserve the accepted architecture.
2. **Define the scoped contract.** For a complete scene, identify all required
   objects, assets, hierarchy, proportions, behavior, and acceptance viewpoints.
   Classify each relevant volume as a body, surface detail, support, container,
   anchor, or visual overlay. Define its X/Y/Z relationships and independent
   permitted regions before choosing transforms. For focused placement,
   identify the target, reference or permitted region, allowed transform
   changes, and invariants that must remain untouched. Record unknowns instead
   of inventing asset facts.
3. **Implement only the accepted scope.** Create or load code-owned Entities and
   alter hierarchy in complete-scene mode. In focused-placement mode, retain
   the existing hierarchy unless the request explicitly permits reparenting.
   Reuse code-created meshes and materials through a scene-lifetime resource
   owner. Apply verified orientation and an explicit scale policy. Read the
   relevant supporting guidance below before implementing a fragile or
   unfamiliar part.
4. **Resolve spatial constraints in two stages.** First solve internal support,
   contact, containment, alignment, and anchor relationships in the base scene.
   Then, when the complete composition is bounded, apply one explicit uniform
   fit on `fittedSceneRoot` beneath an identity `placementOwner`. Measure final
   visual bounds in that owner, and re-measure after every applied transform.
5. **Run and inspect.** Build, install, and launch through the enclosing app
   workflow. Check crashes and logs, collect numeric evidence for hard spatial
   constraints, capture useful viewpoints, and iterate until the scoped outcome
   meets the contract.

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
`spatial-app-dev-workflow` for the enclosing edit/build/install/launch loop and
`spatial-emulator-usage` for device evidence.

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
