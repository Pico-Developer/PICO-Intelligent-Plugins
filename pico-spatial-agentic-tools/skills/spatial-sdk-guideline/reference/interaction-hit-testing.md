# Interaction and Hit Testing

## What this covers

- Minimal prerequisites for 3D interaction
- Hit testing and targeting patterns
- Spatial gesture recognizers and common pitfalls
- Hover feedback for gaze/selection
- Unit/coordinate mapping for drag/transform

## Minimal prerequisites (if interaction “does not work”)

Distinguish these two cases:

1. **Programmatic hit testing** (`scene.rayCast(...)`, `scene.convexCast(...)`)

- The target needs `CollisionComponent` with at least one shape.

2. **User interaction** (gaze / tap / drag / transform gestures)

- The target needs both `CollisionComponent` and `InteractableComponent`.

Without collision shapes, the system has nothing to hit.

Checklist:

- [ ] Does the entity have `CollisionComponent`?
- [ ] Are there shapes in `collisionShape`?
- [ ] If this is user interaction rather than a raycast, does the entity have `InteractableComponent`?
- [ ] Is the collision boundary aligned with the visible mesh?

## Component contracts

### CollisionComponent

```kotlin
class CollisionComponent(
    val collisionShape: List<ShapeResource>,
    val physicsMaterial: PhysicsMaterialResource,
    val collisionResponseMode: CollisionResponseMode = CollisionResponseMode.COLLIDER_FULL,
    val collisionFilter: CollisionFilter = CollisionFilter.COLLISION_FILTER_DEFAULT,
    val collisionInfoDetailLevel: CollisionInfoDetailLevel = CollisionInfoDetailLevel.BRIEF,
)
```

- `collisionShape` and `physicsMaterial` are required. An empty shape list means there is nothing to hit.
- Shapes are in meters and local to the entity:
  - `ShapeResource.createBox(Vector3)` takes **full extents**, not half extents.
  - `ShapeResource.createSphere(radius)`.
  - `ShapeResource.createCapsule(height, radius)` where `height` includes the spherical caps.
  - `createConvexMesh(mesh)` / `createStaticMesh(mesh)` for precise but costlier shapes.
- `collisionShape` is assignable at runtime, so bounds can be swapped without removing the component.
- `collisionResponseMode` changes physical response and contact reporting, not whether the entity can be hit: `TRIGGER_FULL` / `TRIGGER_LITE` report contacts without pushing, `COLLIDER_FULL` also responds.
- `collisionFilter` governs collider-versus-collider rules: `group` is what this entity is, `mask` is what it may hit, and both directions must pass.
- `PhysicsMaterialResource()` defaults are `staticFriction = 0.6f`, `dynamicFriction = 0.6f`, `restitution = 0f`. Spatial Editor's collision UI shows different defaults; runtime attachment uses these SDK values.
- No mesh and no other component are required for `scene.rayCast` to hit the entity.

### InteractableComponent

- Marker component: no fields, no parameters, no `enabled` flag. Presence is the only state.
- Requires `CollisionComponent` on the same entity.
- Enable or disable interaction by adding or removing the component.
- Removing it keeps the collider hit-testable by `scene.rayCast`; user input callbacks stop because the gesture detectors require this component.
- `Entity.enabled` is not an interaction switch; it hides the entity.

### HoverEffectComponent

- Marker component: no style, color, intensity, or distance fields.
- Requires `CollisionComponent` and `InteractableComponent`.
- There is one implicit runtime highlight. Adding the component to a parent also highlights its children.
- The hover region follows the collider, not the rendered mesh.
- Not the same as `Modifier.spatialHoverEffect`, which styles Compose content and does not configure ECS entities.

Component contracts live here; the gesture catalog and per-gesture recipes live in
`spatial-ui-ability/references/ability-gestures.md`.

## Collider choice for interaction

Two common approaches:

- **Bounding-box collider** (recommended default): cheap, may be less precise.
- **Mesh-based collider**: precise, higher cost.

Rule:

- Prefer bounding-box/sphere/capsule unless precision is required.

## Spatial gestures (Compose)

Common recognizers:

- `detectSpatialTapGesture(...)`
- `detectSpatialDragGesture(...)`
- `detectSpatialScaleGesture(...)`
- `detectSpatialRotateGesture(...)`
- `detectSpatialTransformGesture(...)`
- `detectSpatialPointerEvent(...)` (lower-level)

### Critical pitfall: one recognizer per pointerInput

Do **not** call multiple `detectSpatial*` functions inside the same `pointerInput { ... }` block.
They are mutually exclusive and can block each other.

Correct pattern:

```kotlin
Modifier
  .pointerInput(Unit) {
    detectSpatialDragGesture(context) { /* ... */ }
  }
  .pointerInput(Unit) {
    detectSpatialScaleGesture(context) { /* ... */ }
  }
```

## Targeting: limit what can be interacted with

Use `TargetEntity` to scope interactions:

- `TargetEntity.hit(entity)` → only that entity and its children.
- `TargetEntity.any { predicate }` → any entity matching a condition.

This is essential when multiple interactables exist.

## Programmatic hit testing gotchas

- `scene.rayCast(...)` and `scene.convexCast(...)` use the coordinate system of `referenceEntity`; if `referenceEntity == null`, the container space is used.
- If the ray origin starts **inside** a collider, that object will not be returned as a raycast hit.
- Use `convexCast(...)` when you need volume-based detection rather than an infinitely thin ray.

## Hover feedback

For gaze/selection highlighting on 3D entities:

- Add `HoverEffectComponent`.

Minimal recipe:

- `CollisionComponent` + `InteractableComponent` + `HoverEffectComponent`

## Enable and disable interaction at runtime

Keep the collider and toggle the two marker components:

```kotlin
// Disable user input; scene.rayCast still hits the collider.
entity.components.remove(HoverEffectComponent::class.java)
entity.components.remove(InteractableComponent::class.java)

// Re-enable later.
entity.components.set(InteractableComponent())
entity.components.set(HoverEffectComponent())
```

All component writes run on the main thread; off-main calls throw.

## Bundle-loaded entities

`AssetBundle.loadModel(...)` plus `SpatialViewContent.addEntity(...)` add no components, so attach the
collider and markers yourself. `SpatialModelView` instead adds a box `CollisionComponent` and
`InteractableComponent` to the model entity and its children automatically; check
`components.has<CollisionComponent>()` before replacing that collider.

## Symptom to cause

- Tap or gaze never reaches the app: `InteractableComponent` is missing.
- `scene.rayCast` returns nothing although the model is visible: `CollisionComponent` is missing or
  `collisionShape` is empty.
- Taps fire in empty space around the model: the collider is larger than the mesh.
- The collider is visibly offset from the mesh: the shape was built without the mesh-local
  translation; offset it with `offsetByTranslation(...)`.
- Disabling interaction also removes the hover highlight: `HoverEffectComponent` depends on
  `InteractableComponent`.
- Only one of two gestures ever works: two `detectSpatial*` calls share a single `pointerInput` block.

## Drag/transform mapping: units and handedness

### Unit mismatch

- Gesture deltas (e.g., `dragAmount`) can be reported in **pixels**.
- 3D transforms are in **meters**.

Convert px/dp → meters via:

- `LocalDensity.current`
- `LocalPhysicalLengthConverter.current`

### Coordinate mismatch

- View-space +Y is **down**.
- 3D (right-handed) +Y is **up**.

So mapping a drag delta to a world offset usually requires **inverting Y**.

Checklist when dragging feels wrong:

- [ ] Am I converting to meters before applying to `TransformComponent`?
- [ ] Did I invert Y when mapping view deltas to 3D space?
- [ ] Am I applying deltas in the correct reference space (local vs world)?

## InteractionKind (advanced routing)

Some gesture callbacks expose an `InteractionKind` indicating how input was performed.
Use it to differentiate behaviors (e.g., drag vs poke) within the same recognizer.
