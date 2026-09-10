# Hierarchy and Coordinate Spaces

Read this reference when an Entity transform depends on a parent chain, visual
bounds, a logical region, or coordinates from a SpatialView or WindowContainer.

## Contents

- Use PICO axes
- Use the canonical bounded-scene hierarchy
- Choose the transform owner
- Convert an owner-space delta into target-parent space
- Build a measurable hierarchy
- Select the correct bounds source
- Measure, solve, and remeasure
- Refresh stale layout data

## Use PICO Axes

Use `+X` for right, `+Y` for up, and `+Z` for front/toward the user. State any
asset-axis conversion separately from the runtime coordinate convention.

An Entity's `TransformComponent.position` is expressed in its parent coordinate
space. A translation delta is valid only when the target bounds, reference
bounds, and permitted region are expressed in that same owner's axes.

## Use the Canonical Bounded-Scene Hierarchy

For a complete scene that must fit bounded runtime content, use:

```text
SpatialView
└── placementOwner              // identity; owns bounds evidence
    └── fittedSceneRoot         // owns exactly one outer fit transform
        ├── scene group A
        ├── scene group B
        └── scene group C
```

Solve base-scene relationships below `fittedSceneRoot`, then apply the outer fit
to that root. Express the runtime safe region, transformed planned envelope, and
fresh final visual bounds relative to `placementOwner`. Do not compare a
pre-fit design envelope with a post-fit visual envelope.

Retain the base transform of `fittedSceneRoot` and reset it before each
size/revision-dependent fit. This prevents resize from applying cumulative
scale or translation.

## Choose the Transform Owner

Choose one owner before solving placement. For Entities beneath a common
identity owner:

```kotlin
val targetBounds =
    target.getVisualBounds(owner, recursive = true, enabledOnly = true)
val referenceBounds =
    reference.getVisualBounds(owner, recursive = true, enabledOnly = true)
```

The owner used by `getVisualBounds()` must be compatible with the coordinate
space that owns the target position. If an owner has its own transform, convert
logical-region corners into that owner before comparing them with Entity bounds.

## Convert an Owner-Space Delta into Target-Parent Space

`TransformComponent.position` belongs to the target's immediate parent. A delta
calculated from bounds in another owner space cannot be added directly when the
spaces differ by rotation or scale.

Treat the delta as a vector, not as a position. Convert two owner-space points
into the target-parent space and subtract them:

```kotlin
fun convertDeltaToTargetParent(
    deltaInOwner: Vector3,
    owner: Entity,
    targetParent: Entity,
): Vector3 {
    val ownerOriginInParent =
        targetParent.convertPositionFrom(Vector3.ZERO, owner)
    val ownerEndpointInParent =
        targetParent.convertPositionFrom(deltaInOwner, owner)
    return ownerEndpointInParent - ownerOriginInParent
}
```

Then apply the converted delta to the target's retained parent-local base
position:

```kotlin
val deltaInParent =
    convertDeltaToTargetParent(deltaInOwner, owner, targetParent)
targetTransform.position = targetBasePosition + deltaInParent
```

The subtraction removes the translated origin and preserves the linear effect
of rotation and non-uniform scale. Do not only inverse-rotate the delta, and do
not call `convertPositionFrom(deltaInOwner, owner)` once and treat the returned
point as a vector. Prefer these public conversion APIs over reconstructing or
inventing world-matrix access.

If the selected bounds owner is the target's immediate parent, no conversion is
needed. Make that identity explicit in compact helpers rather than relying on a
generic parameter named `owner`.

## Build a Measurable Hierarchy

Attach the complete hierarchy to `SpatialViewContent` before measuring. Reject
`BoundingBox.isEmpty()` rather than guessing an unloaded or disabled Entity's
size. The returned owner-axis-aligned visual box reflects the current hierarchy,
scale, and rotation.

Avoid recursive ancestor bounds that include the target itself. Measure the
intended visual child, use `recursive = false` when appropriate, or define a
logical region explicitly.

Use a direct identity child of the SpatialView as a public owner when view-local
regions and Entity visual bounds must share axes. Add a separate child for an
outer fit rather than transforming the evidence owner:

```kotlin
val placementOwner = Entity()
val fittedSceneRoot = Entity()
content.addEntity(placementOwner)
placementOwner.addChild(fittedSceneRoot)
fittedSceneRoot.addChild(reference)
fittedSceneRoot.addChild(target)
```

Do not access `content.localSpatialCoordinateSpace.origin`; the SDK marks that
origin Entity as library-restricted.

## Select the Correct Bounds Source

| Intended boundary                                                   | Source                                       |
| ------------------------------------------------------------------- | -------------------------------------------- |
| Rendered Entity envelope                                            | `entity.getVisualBounds(owner)`              |
| Shelf cavity, tabletop, slot, wall/floor patch, or design safe area | Explicit owner-local `BoundingBox`           |
| Current SpatialView                                                 | Convert `ViewCoordinateSpace.Local` corners  |
| Containing bounded WindowContainer                                  | Convert `ViewCoordinateSpace.Global` corners |
| Stage without a named surface or design region                      | No implicit global containment region        |

An Entity is a coordinate node, not automatically a usable volume. A rendered
shelf frame is not its empty cavity, and a room mesh is not automatically the
permitted region for every child.

## Measure, Solve, and Remeasure

Use this sequence:

1. Attach or update the complete hierarchy.
2. Apply accepted base scale and orientation.
3. Express all bounds and regions in the chosen owner space.
4. Reject empty or incompatible inputs.
5. Solve all requested internal relationship and region constraints together.
6. When required, apply one explicit outer fit on `fittedSceneRoot` and express
   the transformed planned envelope in the evidence owner.
7. Convert a placement delta into target-parent space when the bounds owner differs,
   then add it to the retained parent-local base position.
8. Query fresh visual bounds and verify every equality and interval with an
   epsilon.

Do not add a containment interval itself. Do not clamp an exact relationship
into a permitted interval, because clamping silently changes the requested
scene composition.

## Refresh Stale Layout Data

Invalidate measured bounds after asset or hierarchy replacement, transform or
enabled-state changes, view/container resize, and any animation, physics,
tracking, or user manipulation that affects a live guarantee. Prefer a one-shot
or event-driven refresh for static scenes and retain a revision key to prevent
accidental repeated deltas.
