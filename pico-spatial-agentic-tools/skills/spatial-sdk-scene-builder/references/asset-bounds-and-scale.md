# Asset Bounds and Scale

Read this reference when an asset's source bounds, units, orientation, pivot, or
physical size is not already verified.

## Contents

- Keep source and runtime bounds separate
- Inspect source assets
- Interpret format-specific evidence
- Resolve USD and USDZ physical size
- Convert verified size into scale
- Hand source evidence into placement
- Stop on missing evidence

## Keep Source and Runtime Bounds Separate

Maintain two distinct records:

1. **Source bounds** describe geometry in the asset's composed source coordinate
   system. Use them to inspect native proportions, units, axes, and physical
   size.
2. **Runtime visual bounds** describe the loaded Entity after its hierarchy,
   scale, orientation, enabled state, and runtime representation are applied.
   Use them to solve and verify placement.

Neither record replaces the other. Never describe source bounds as final
rendered containment evidence, and never derive native asset size from an
arbitrarily transformed runtime or Editor instance.

## Inspect Source Assets

When source bounds or unit evidence is missing, run the bundled inspector with
an absolute asset path:

```bash
python3 /absolute/path/to/spatial-sdk-scene-builder/scripts/inspect_asset_bounds.py \
  /absolute/path/to/model.usdz
```

Resolve the script path relative to this skill's `SKILL.md`; do not assume the
user's project contains a `skills/` directory. Install
`scripts/requirements.txt` only when the inspector reports a missing
dependency.

The inspector emits structured JSON containing raw source-coordinate bounds,
axis and unit metadata when the format provides it, meter-space extents only
when a unit conversion is established, and explicit limitations. Treat
`unit_metadata.status = "unknown"` as unresolved; numeric values that merely
look human-scale are not unit evidence.

The inspector is conditional, not mandatory for every asset. Skip it when the
same facts are already verified by current source metadata, exporter records, a
sidecar, or an accepted project contract. Run it when those facts are missing,
conflicting, or need to be recorded for a scale decision.

## Interpret Format-Specific Evidence

- `.glb` and `.gltf`: report glTF source bounds with meter units and Y-up format
  semantics.
- `.obj` and `.stl`: report raw bounds, but leave units and up axis unknown
  unless separate project evidence establishes them.
- `.spz`: report point-center bounds only. The result does not expand Gaussian
  radii and cannot alone prove rendered containment or non-overlap.
- `.usd`, `.usda`, `.usdc`, and `.usdz`: inspect the composed stage and report
  effective `metersPerUnit`, `upAxis`, raw bounds, and meter-space extents.

Do not infer model-forward direction or pivot semantics merely from a format's
up-axis convention.

## Resolve USD and USDZ Physical Size

For a USD-family asset, use the composed source stage as the authority. Record:

- exact source path and asset fingerprint when available
- whether `metersPerUnit` and `upAxis` are authored or schema defaults
- raw X/Y/Z bounds and extents
- meter-space X/Y/Z extents
- selected height axis from `upAxis`

Select native height as follows:

```text
upAxis = Y: nativeHeightInStageUnits = Y extent
upAxis = Z: nativeHeightInStageUnits = Z extent

nativeAssetHeightMeters =
  nativeHeightInStageUnits * metersPerUnit
```

Require finite bounds, positive `metersPerUnit`, and a positive finite native
height. Do not:

- apply a generic `/100` conversion
- inspect only one referenced layer instead of the composed stage
- infer native dimensions from an Editor or runtime instance transform
- infer native dimensions from a screenshot, container, or visual estimate
- change scale to conceal placement, clipping, orientation, or coordinate-space
  errors

The similarly named scale workflow inside `spatial-editor` applies only to an
Editor-generated USDZ imported into an Editor-owned target scene. App-side
source inspection and Kotlin runtime scale decisions remain in this skill.

## Convert Verified Size into Scale

Treat native scale as source evidence, not an automatic runtime requirement.
Uniform scaling is permitted by default when it improves fit or visual harmony.
Record the selected runtime scale and its reason; do not add an identity scale
assignment merely to restate the default.

Preserve authored size only when the asset or accepted project contract
explicitly declares an exact physical size or marks the asset non-scalable. If
that requirement cannot fit, report no-fit and the conflict axis rather than
silently shrinking it.

When an explicit target height is required:

```text
uniformScale = targetHeightMeters / nativeAssetHeightMeters
```

For a non-USD scale change, use the same ratio with a verified source dimension
and accepted intended dimension. Preserve aspect ratio with uniform scale by
default. Apply non-uniform scale only when the accepted contract explicitly
permits distortion.

Account for source orientation before mapping width, height, and depth to PICO
X, Y, and Z. A verified up axis does not establish model-forward direction.

## Hand Source Evidence into Placement

Example: display `statue.usdz` at `1.20 m` tall, place it `0.02 m` above a
pedestal, and keep it inside a SpatialView.

Source inspection returns:

```text
metersPerUnit: 0.01
upAxis: Y
raw Y bounds: [-10, 70]
native height: (70 - (-10)) * 0.01 = 0.80 m
requested height: 1.20 m
uniform Kotlin Entity scale: 1.20 / 0.80 = 1.500
```

Apply the accepted uniform scale to the Kotlin Entity, attach its final
hierarchy, then query fresh runtime visual bounds. Solve placement from the
final faces:

```text
dy = pedestal.max.y + 0.02 - statue.min.y
dx = pedestal.center.x - statue.center.x
dz = pedestal.center.z - statue.center.z
```

Remeasure and verify the requested gap and containment. This example has an
explicit `1.20 m` physical-size requirement, so if the scaled statue does not
fit, report a no-fit conflict rather than shrinking it. Without an explicit
exact-size or non-scalable rule, a further reported uniform composition fit is
permitted by default.

## Stop on Missing Evidence

Stop only the affected requirement when required bounds, units, orientation,
pivot semantics, composed USD evidence, or runtime visual bounds cannot be
obtained. Report the exact missing evidence and downstream decisions it blocks.
Do not substitute guessed dimensions or label a provisional scale as verified.
