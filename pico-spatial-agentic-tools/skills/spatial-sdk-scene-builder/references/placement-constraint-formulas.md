# Placement Constraint Formulas

Use these formulas only after the target, reference, and permitted region are
expressed as `BoundingBox` values in the coordinate space that owns the target's
`TransformComponent.position`.

## Contents

- Relationship constraints
- Containment constraints
- Support and contact constraints
- Open containment and allowed protrusion
- Combined relationship and containment
- Region intersection
- Verification

## Relationship Constraints

Let `t` be the current target bounds, `r` the reference bounds, and `g` a
non-negative clear gap. Each formula returns a translation component, not an
absolute pivot coordinate.

| Relationship | Required translation         |
| ------------ | ---------------------------- |
| on top       | `dy = r.max.y + g - t.min.y` |
| below        | `dy = r.min.y - g - t.max.y` |
| right        | `dx = r.max.x + g - t.min.x` |
| left         | `dx = r.min.x - g - t.max.x` |
| in front     | `dz = r.max.z + g - t.min.z` |
| behind       | `dz = r.min.z - g - t.max.z` |

Center alignment on another axis uses:

```text
dAxis = reference.center.axis - target.center.axis
```

For example, place a target to the right of a reference and align the other
visual centers. This compact helper requires `targetParent` to be the immediate
parent whose coordinate space owns `target.position`. If bounds were solved in
another owner space, first convert the resulting delta as described in
[`hierarchy-and-coordinate-spaces.md`](./hierarchy-and-coordinate-spaces.md).

```kotlin
@MainThread
private fun placeRightOf(
    target: Entity,
    reference: Entity,
    targetParent: Entity,
    gap: Float,
): Boolean {
    require(gap >= 0f)

    val targetBounds =
        target.getVisualBounds(targetParent, recursive = true, enabledOnly = true)
    val referenceBounds =
        reference.getVisualBounds(targetParent, recursive = true, enabledOnly = true)
    if (targetBounds.isEmpty() || referenceBounds.isEmpty()) return false

    val delta =
        Vector3(
            referenceBounds.max.x + gap - targetBounds.min.x,
            referenceBounds.center.y - targetBounds.center.y,
            referenceBounds.center.z - targetBounds.center.z,
        )
    val transform = target.components.get<TransformComponent>() ?: return false
    transform.position += delta
    return true
}
```

This remains correct when either model pivot is off center because the delta
uses current visual faces and centers.

## Containment Constraints

Let `p` be a permitted region, `t` the target's current bounds, `m` a
non-negative per-axis margin, `currentPosition` the current owner-local pivot
position, and `d` one concrete translation to apply.

Containment requires:

```text
p.min + m <= t.min + d
t.max + d <= p.max - m
```

The allowed **translation** interval on every axis is:

```text
dMin = p.min + m - t.min
dMax = p.max - m - t.max
```

`[dMin, dMax]` is a set of permitted deltas, not a value to add to the current
position. The target fits only when `dMin <= dMax` on X, Y, and Z. Select one
concrete delta on each axis:

```text
dChosen = dMin + (dMax - dMin) * u
0 <= u <= 1

finalPosition = currentPosition + dChosen
```

Choose `u` by semantic intent:

- `u = 0`: `dChosen = dMin`, for the left, bottom, or back edge
- `u = 0.5`: the interval midpoint, for center
- `u = 1`: `dChosen = dMax`, for the right, top, or front edge

If the caller needs the interval of legal final pivot positions rather than
legal translations, convert it explicitly:

```text
finalPositionMin = currentPosition + dMin
finalPositionMax = currentPosition + dMax
```

For an upper-right-front shelf-cavity placement:

```kotlin
@MainThread
private fun placeUpperRightFront(
    target: Entity,
    targetParent: Entity,
    cavity: BoundingBox,
    margin: Vector3,
): Boolean {
    require(margin.x >= 0f && margin.y >= 0f && margin.z >= 0f)

    val targetBounds =
        target.getVisualBounds(targetParent, recursive = true, enabledOnly = true)
    if (targetBounds.isEmpty()) return false

    val allowedDeltaMin = cavity.min + margin - targetBounds.min
    val allowedDeltaMax = cavity.max - margin - targetBounds.max
    if (
        allowedDeltaMin.x > allowedDeltaMax.x ||
            allowedDeltaMin.y > allowedDeltaMax.y ||
            allowedDeltaMin.z > allowedDeltaMax.z
    ) {
        return false
    }

    // u = 1 on every axis selects the right, top, and front edge.
    val chosenDelta = allowedDeltaMax
    val transform = target.components.get<TransformComponent>() ?: return false
    transform.position += chosenDelta
    return true
}
```

Use the SDK `BoundingBox(center, halfExtent)` for explicit regions; do not create
a parallel bounds type merely to hold `min` and `max`.

## Support and Contact Constraints

For a body `t` resting on an axis-aligned support region `s`, verify both the
contact face and the X/Z footprint. With non-negative margin `m`:

```text
abs(t.min.y - s.max.y) <= epsilon

s.min.x + m.x <= t.min.x
t.max.x <= s.max.x - m.x
s.min.z + m.z <= t.min.z
t.max.z <= s.max.z - m.z
```

If the body starts elsewhere, the exact vertical contact delta is:

```text
dy = s.max.y - t.min.y
```

Choose X/Z translation from the valid footprint-containment intervals. A pivot
or center above the support is not sufficient evidence; use final scaled and
oriented body visual bounds. Define the usable support region independently of
the target rather than using the support mesh's whole recursive envelope.

## Open Containment and Allowed Protrusion

For an open cavity, name the open face and encode the accepted protrusion
instead of weakening all-axis containment. For a front-open bay with permitted
front protrusion `a >= 0`:

```text
bay.min.x + margin.x <= target.min.x
target.max.x <= bay.max.x - margin.x
bay.min.y + margin.y <= target.min.y
target.max.y <= bay.max.y - margin.y
target.min.z >= bay.min.z + backMargin - epsilon
target.max.z <= bay.max.z + a + epsilon
```

The bay must be an explicit logical region or independently measured structure
region. Do not derive it from a union or envelope that already includes the
target, because that makes containment self-fulfilling.

## Combined Relationship and Containment

Solve an exact relationship component first, then prove that it lies within the
allowed containment interval:

```text
requiredDx = reference.max.x + gap - target.min.x
allowedDxMin = region.min.x + margin.x - target.min.x
allowedDxMax = region.max.x - margin.x - target.max.x

valid only when allowedDxMin <= requiredDx <= allowedDxMax
```

Repeat for every exact relationship or alignment component. For an axis with
only containment, choose one concrete edge, center, or ratio within its valid
translation interval.

Do not clamp `requiredDx` into the interval: clamping would silently violate the
requested gap or relationship. Report the conflicting axis instead.

## Region Intersection

When content must stay inside both a SpatialView and its bounded
WindowContainer, intersect the two regions first:

```text
safe.min = componentMax(spatialView.min, windowContainer.min)
safe.max = componentMin(spatialView.max, windowContainer.max)
```

The intersection exists only when `safe.min <= safe.max` on every axis. Apply
the containment formulas to that intersection.

## Verification

After moving the target, query fresh bounds and verify every constraint with a
small epsilon:

```text
right:
abs(target.min.x - reference.max.x - gap) <= epsilon

inside:
target.min >= region.min + margin - epsilon
target.max <= region.max - margin + epsilon
```

For animated or physics-driven objects, this verifies only the sampled pose.
For every hard result, state whether the compared bounds cover the body, a
surface detail, or the full recursive Entity. Use body bounds for support and
containment unless the contract explicitly requires a detail to fit too.
