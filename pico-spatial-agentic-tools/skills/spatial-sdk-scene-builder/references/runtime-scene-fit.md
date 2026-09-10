# Runtime Scene Fit

Read this reference when a complete composition must remain inside a
`SpatialView`, a bounded `WindowContainer`, or their intersection.

## Separate Internal Layout from Outer Fit

Use two stages:

1. Build the base scene and solve its internal support, containment, contact,
   spacing, and anchor relationships.
2. Fit the resulting composition as one unit into the runtime safe region.

Do not shrink individual occupants opportunistically after solving the base
scene. Either select an intentional per-object scale while composing the base
scene, or apply one outer fit transform to the accepted composition.

## Use the Canonical Hierarchy

```text
SpatialView
└── placementOwner              // identity; owns runtime evidence
    └── fittedSceneRoot         // owns exactly one outer fit transform
        ├── scene group A
        ├── scene group B
        └── scene group C
```

Keep `placementOwner` identity-aligned with the SpatialView. Express the safe
region, transformed planned envelope, and remeasured final visual envelope
relative to this named Entity. Keep the base layout beneath
`fittedSceneRoot`; reset to its retained base transform before applying a fit
for a new size or revision.

## Default Scale Policy

Uniform scaling is permitted by default when it improves fit or visual harmony.
Record the selected scale and why it was selected.

- Preserve authored size only when an asset or accepted requirement explicitly
  declares `non-scalable` or an exact physical size.
- If an explicitly non-scalable or exact-size composition cannot fit, report
  no-fit and the conflict axis instead of shrinking it.
- Preserve aspect ratio. Use non-uniform scale only when the accepted contract
  explicitly permits distortion.
- A fit factor larger than one may be used to improve composition when the
  scene's human-scale and spacing intent allow enlargement. Filling all
  available space is not itself a requirement.

Source/native scale remains evidence about the asset. It does not silently
override the accepted runtime scale policy.

## Calculate One Uniform Fit

Let `b` be the base design envelope, `p` the safe region, and `m` a
non-negative margin, all with matching axes. Available size is:

```text
available = (p.max - m) - (p.min + m)
baseExtent = b.max - b.min
```

For a composition that may scale uniformly:

```text
fitLimit = min(
  available.x / baseExtent.x,
  available.y / baseExtent.y,
  available.z / baseExtent.z
)

selectedScale <= fitLimit
selectedScale > 0
```

Choose `selectedScale` from this limit plus the accepted aesthetic and
human-scale intent. Reject non-positive extents, empty regions, and non-finite
results. For an exact-size composition, use its accepted scale and check it
against the same limit without changing it.

Compute the transformed planned envelope using the selected scale and root
translation; do not compare pre-fit design bounds with post-fit visual bounds.
For uniform scale `s` around a retained base root origin `o`, each base point
`q` becomes:

```text
qFinal = rootTranslation + o + s * (q - o)
```

This compact equation assumes an axis-aligned base root. If its accepted base
transform includes rotation, transform all eight envelope corners through the
full retained base transform before constructing the owner-axis-aligned planned
envelope.

Center or align that transformed envelope inside the permitted interval using
the formulas in `placement-constraint-formulas.md`.

## Apply, Remeasure, and Refresh

1. Obtain the runtime safe region through the public conversion workflow in
   `spatialview-windowcontainer-bounds.md`.
2. Reset `fittedSceneRoot` to its retained base transform.
3. Apply the selected uniform fit transform exactly once: one scale and one
   translation on `fittedSceneRoot`.
4. Query fresh recursive visual bounds relative to `placementOwner`.
5. Verify final containment with the accepted margin and epsilon.
6. Emit both the transformed planned envelope and remeasured visual envelope
   in the same owner space.

Use a size/revision key so resize is a deliberate recomputation rather than a
cumulative transform. If the planned and visual envelopes disagree beyond the
accepted epsilon, report stale or incomplete bounds evidence instead of
changing scale until the discrepancy disappears.
