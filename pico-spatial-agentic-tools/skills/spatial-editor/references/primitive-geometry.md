# Spatial Editor Primitive Geometry

Read this reference when authoring primitive transforms or connected joints.
Use the live Editor API signatures for operation arguments and measured bounds
for dimensions. These rules apply within the current managed authoring window.

## Primitive Orientation Convention

Classify the primitive feature whose direction is observable before choosing
Euler rotation. Do not use an unconstrained visual guess.

| Primitive             | Canonical zero-rotation feature | Direction rule                                                                                        |
| --------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `Cone`                | tip points along local `+Y`     | Signed. Base-to-tip direction must match the accepted world direction.                                |
| `Cylinder`, `Capsule` | longitudinal axis is local `Y`  | Axial. Ends are equivalent unless accepted input adds a visible end distinction.                      |
| `Plane`               | normal points along local `+Y`  | Signed only when visibility, culling, or an accepted relationship makes the normal observable.        |
| `Sphere`              | none                            | Omit rotation unless an attached or visible feature establishes orientation.                          |
| `Cube`                | none                            | Omit rotation unless dimensions, a visible face, or an accepted relationship establishes orientation. |

For an identity-transform parent, rotate canonical local `+Y` to a required
signed world direction with this Editor-space Euler mapping, in degrees:

| Required world direction | Euler rotation                 |
| ------------------------ | ------------------------------ |
| `+Y`                     | `{ "x": 0, "y": 0, "z": 0 }`   |
| `-Y`                     | `{ "x": 180, "y": 0, "z": 0 }` |
| `+X`                     | `{ "x": 0, "y": 0, "z": -90 }` |
| `-X`                     | `{ "x": 0, "y": 0, "z": 90 }`  |
| `+Z`                     | `{ "x": 90, "y": 0, "z": 0 }`  |
| `-Z`                     | `{ "x": -90, "y": 0, "z": 0 }` |

Dimensions describe the primitive's local pre-rotation geometry. For `Cone`,
`Cylinder`, and `Capsule`, keep height on local `Y`; do not move the height value
into the requested world-axis component after rotating. Use documented metric
creation or derive scale from canonical dimensions; meters are not scale multipliers.

For every direction-sensitive primitive:

1. Derive direction from accepted input or a task relationship. Without one,
   preserve zero rotation and do not invent a preferred direction.
2. Record the exact observable feature and direction in the accepted criteria
   and authoring rationale, for example "Cone tip points toward world +Z".
   A lampshade opening normal is not its base-to-tip direction; preserve the
   requested feature and the same world-forward convention throughout.
3. Prefer an identity-transform group or the existing scene root. If the parent
   is rotated, account for its verified transform before choosing local Euler values.
4. Inspect at least two useful current views during review. For signed direction,
   prefer opposing world-axis views that expose the feature.

Do not assign a fake positive end to a symmetric Cylinder or Capsule. A required
head/tail distinction must be visibly authored from accepted geometry or material intent.

## Select The Joint From Its Contact Surfaces

Preserve the accepted silhouette, dimensions and connection intent. Determine the
actual mating surfaces before choosing contact or insertion:

| Contact geometry                                                                    | Preferred construction                                                            |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Matching flat faces can provide sufficient internal contact                         | Use a face-to-face butt joint; terminate one member at the other's contact plane. |
| Flat-to-curved or curved-to-curved members would touch only at a point or line      | Use bounded insertion when the intended connection needs more than tangency.      |
| Insertion leaves overlapping exterior surfaces at the same or nearly the same depth | Change the joint or dimensions to remove the competing surfaces.                  |

Internal mating faces may coincide. Hidden interior volumes may overlap. The
defect is an exposed region where independently rendered surfaces coincide or
are close enough to compete in depth. This can occur on flat faces, cylinder or
cone caps, and duplicated or nearly coincident curved surfaces; it is not a
Cube-only rule. Ordinary intersection between distinct surfaces does not by
itself prove z-fighting.

### Flat Face Contact

For an axis-aligned beam resting on a post, preserve the beam and terminate the
post at the beam's underside:

```text
postTop = beamBottom
postCenterY = beamBottom - postHeight / 2
```

Verify that the intended contact area fits the supporting/mating face. The
internal contact faces can coincide while exposed side faces meet only along an
edge, without overlapping area. Use verified world-space faces for rotated
members. Do not add arbitrary gaps or tiny offsets to disguise duplicate faces.

## Embedded Primitive Joint Convention

Use bounded insertion when contact geometry or accepted design calls for it;
do not insert every connected primitive automatically.

1. Name one primitive as receiver and the other as inserted member. Determine the
   insertion axis and actual receiver surface from measured geometry.
2. Place the entire inserted terminal face inside the receiver with clearance,
   including its edges and corners. A terminal center inside a sphere or curved
   side is insufficient; the corners may still protrude. Adjust the member's
   cross-section or connection geometry if the full end cannot fit.
3. For verified parallel planar receiver faces, use a non-zero setback
   `s = min(0.1 * receiverThickness, max(0.001 m, 0.01 * receiverThickness))`.
   Penetration depth is within `[s, receiverThickness - s]`; for either entry side
   of `[receiverMin, receiverMax]`, the terminal coordinate stays within
   `[receiverMin + s, receiverMax - s]`.
4. For curved or rotated receivers, verify the actual surface and clearance over
   the full terminal face. World AABB planes do not describe curved surfaces or
   rotated faces; the planar setback formula alone cannot prove containment.
5. Inspect every exterior surface around the overlap, including front, back,
   top, bottom and opposite side where applicable. Insertion depth only constrains
   the terminal face; other surfaces must not form exposed coincident or
   near-coincident patches. Do not pass through the receiver unless accepted
   design explicitly calls for a visible through-member.
6. Keep the intended external end fixed when changing length. Recompute both
   local size and center position; changing only size moves both end faces.

### Connection Examples And Review

- Same-thickness rectangular beam and post: embedding can leave their front/back
  or top faces overlapping. Prefer a butt joint when it preserves the required
  shape; hiding only the inserted end does not resolve the side-face overlap.
- Rectangular member entering a sphere or a cylinder's curved side: tangency may
  produce only a point or line contact. Insert enough to hide the full terminal
  face and form the intended connection, then check the remaining exterior.
- Cylinder end cap against another flat face: evaluate it as flat-face contact.
  A circular silhouette does not make an overlapping cap safe.

Record the selected contact surfaces and observable acceptance, for example:

- "Post terminates at the beam underside with internal face contact and no gap."
- "Brace end, including corners, is hidden inside the curved receiver without breakthrough."
- "No exposed competing surfaces or view-dependent flicker occur at the joint."

Inspect useful current views that expose the connection and its other sides.
Check both the geometric cause and visible artifacts: a single clean image does
not prove that duplicate surfaces are absent. Intentional hidden overlap is not
an ordinary collision defect; do not replace a required embedded connection with
point/line tangency to satisfy an unrelated zero-penetration rule. A waiver or
rationale alone does not prove containment or absence of exterior overlap.
