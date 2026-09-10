# SDK Scene Authoring

Read this reference before creating a new PICO Spatial SDK scene, changing
Entity loading or hierarchy, or altering the scene lifecycle.

## Contents

- Inspect the host app
- Define the scene contract
- Design the Entity hierarchy
- Implement in lifecycle order
- Load and retain Entities
- Apply transforms and responsive updates
- Clean up and hand off

## Inspect the Host App

Read the repository's `AGENTS.md` and project-specific instructions first.
Identify:

- the Android module that owns the Spatial experience
- the current Stage, `WindowContainer`, and `SpatialView` structure
- the Composable or controller that owns the scene lifecycle
- the project's accepted Entity, component, system, and resource-loading patterns
- packaged asset locations and any existing scene state holder
- the build, install, launch, screenshot, and log commands already used by the
  project

Extend the existing architecture. Do not replace a working container model or
create a parallel scene framework merely to implement one scene.

## Define the Scene Contract

Turn the request into an implementable contract before editing code. Record:

| Field         | Required decision                                                                        |
| ------------- | ---------------------------------------------------------------------------------------- |
| Scene purpose | What the user should perceive or be able to do                                           |
| Elements      | Stable ID, source, required state, and body/detail/support/container/anchor/overlay role |
| Hierarchy     | Parent of each Entity and which transforms should be inherited                           |
| Scale policy  | Flexible uniform scale, explicit exact size, or explicitly non-scalable                  |
| Bounds scope  | Which final body or detail bounds prove each relationship                                |
| Composition   | X/Y/Z relationships, spacing, focal point, and viewing direction                         |
| Region        | Stage, SpatialView, bounded WindowContainer, or independently defined logical volume     |
| Behavior      | Static, animated, physics-driven, tracked, or user-manipulated                           |
| Acceptance    | Numeric conditions and viewpoints that can reveal each important relationship            |

Resolve contradictions before implementation. Treat omitted artistic choices as
composition decisions, but do not treat missing asset units, bounds, pivots, or
orientation metadata as artistic freedom.

## Design the Entity Hierarchy

For a bounded complete scene, create an identity `placementOwner` beneath the
active spatial content and a `fittedSceneRoot` beneath it. Put the accepted base
composition under `fittedSceneRoot`; that root owns the one outer fit transform,
while `placementOwner` owns safe-region and final-bounds evidence. Use child
groups when several objects must move, rotate, enable, or disappear together.

For an unbounded Stage scene or focused placement that needs no outer fit, use
the smallest stable hierarchy that preserves existing architecture. Still keep
independently compared objects beneath a named compatible bounds owner.

Use parents for inherited transforms, not as substitutes for logical volumes. A
shelf Entity does not automatically define its empty cavity; a room model does
not automatically define the safe region in which every object must fit. Define
tabletops, shelves, wall patches, slots, and other design regions explicitly.

Keep stable references to important Entities. Avoid rediscovering them by scene
order or allocating duplicate Entities during recomposition.

For repeated programmatic geometry, keep a scene-lifetime resource registry and
reuse meshes by geometry specification and materials by immutable definition.
Read `primitive-scene-resources.md` before implementing that pattern.

## Implement in Lifecycle Order

Use this order for a deterministic scene:

1. Create the identity owner, base scene root, resource registry, and required
   Entities through an intentional one-shot construction path.
2. Attach the complete parent-child hierarchy to the spatial content.
3. Apply verified orientation and the accepted per-object scale policy.
4. Solve internal three-axis support, containment, contact, and anchor
   relationships from final body bounds.
5. Wait until required assets and view/container dimensions are available.
6. For a bounded composition, calculate and apply one outer fit transform.
7. Re-query final visual bounds in the named owner and verify every constraint.
8. Store the revision or size key that makes future updates intentional.

Do not measure detached or partially loaded hierarchies and then reuse those
bounds after attachment. Do not add a newly solved delta repeatedly on every
Compose update; retain a base transform or make the update idempotent.

## Load and Retain Entities

Use the resource-loading pattern accepted by the host project. For a packaged
scene or model asset supported by the Entity loader, use the Entity API:

```kotlin
val model = Entity.loadSuspend("asset://model.usdz")
sceneRoot.addChild(model)
```

Do not pass a USDZ scene asset to `MeshResource.load()`. That API expects a mesh
resource and can fail with `FORMAT_UNSUPPORTED` for a scene asset.

A compact state holder may retain the authored hierarchy across recompositions:

```kotlin
private class SceneState {
    var root: Entity? = null
    val entities = mutableMapOf<String, Entity>()
    var appliedRevision: Any? = null
}
```

Keep the holder local to the owning Composable or its ViewModel. Do not make it
a global scene registry unless the application architecture already requires
one.

Create repeated primitive resources through the scene state's retained
resource registry. Do not call mesh or material factories unconditionally from
`SpatialView.update` or unrelated recompositions.

## Apply Transforms and Responsive Updates

Treat `TransformComponent.position` as parent-local. Apply an absolute accepted
base transform once, or reset to the retained base transform before resolving a
fresh delta. Report a missing required `TransformComponent` instead of silently
skipping the Entity.

Recalculate affected transforms after:

- asset or hierarchy replacement
- scale, orientation, or enabled-state changes
- SpatialView or WindowContainer resize
- animation, physics, tracking, or user manipulation when the constraint must
  remain live

Prefer one-shot or event-driven recomputation for static scenes. Use a stable
revision key to avoid unrelated recompositions rebuilding or re-placing the
scene.

## Clean Up and Hand Off

Destroy or deliberately retain the scene root when its owning Spatial content
leaves composition. Clear retained Entity references when the hierarchy is
destroyed. Verify that returning to the screen does not duplicate the scene.

Hand off an implemented scene, not only a proposed hierarchy. Include the
important source locations and explain which scene requirements are verified,
which remain assumptions, and which are blocked.
