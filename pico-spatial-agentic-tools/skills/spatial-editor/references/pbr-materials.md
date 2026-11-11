# Default PBR During Geometry Creation

Primitives already have their own default PBR material. Use the live primitive and
default-material API to configure only supported appearance parameters in the same
geometry script. Keep defaults for unavailable parameters and explain the limitation.
Do not create material sources, share bindings, delete DefaultMaterial, or implement
normal-map file writing, saving or readback.

Read appearance requirements from `authoring.intent.sourceContract`.
Apply supported values directly in geometry scripts. Candidate inventory lists asset
occurrences through `assetBindings`; material registration and a separate material
creation task are unnecessary. Preserve unrelated scene and imported materials.
RGBA alone does not establish transparent blending or emission.

## Current Capability Evidence

Live testing on 2026-10-23 verified Cube, Sphere and Plane creation with an existing
`DefaultMaterial`, whose `materialentity.by_path(...).material_kind` is `PBR`.
The primitive constructors expose name, parent and position; they do not directly
accept RGBA, metallic or roughness.

RGBA is supported through the existing primitive entity:

```python
entity = se.Entity(primitive.path)
entity.set_color(r, g, b, a)
```

All four components are in [0,1]. This updates the bound PBR BaseColor directly
without creating a material or using `set_material_param`. Live Cube/Sphere/Plane
tests verified matching `entity.get_color()` values before and after scene save;
the original DefaultMaterial remained PBR. Apply requested colors during geometry
creation.

In that Editor build, `set_material_param` raises TypeError for `baseColorScale`
(RGBA), metallic, roughness, opacity, normalScale, reflectance, ambientOcclusion,
clearCoat, clearCoatRoughness, emissive and emissiveScale. Numeric getters have a
native variant conversion issue, and `list_material_params` has an unregistered
MaterialParamInfo return type. These failures concern the generic uniform API;
they do not disable the independent `Entity.set_color` API.
Use `set_color` for RGBA and retain defaults for other unavailable controls.
After an Editor update, query the exact live API with `detail="brief"` and verify needed parameters.
Do not turn unavailable optional parameters into a material completion blocker.

`resolve_material_binding` can report a missing UsdMaterialInfoComponent on a valid
primitive DefaultMaterial; it is not a required gate for this path.
`set_material_properties` uses a material preset that can create Graph material;
do not use it as a PBR fallback.

Keep script output concise and below the native 16 KiB limit. If output is truncated,
inspect existing geometry. A successful write stays successful; repair actual partial
failures with a new operation ID and reconcile only receipts that require it.
Candidate checks full manifest counts, ownership and the scene fingerprint. Appearance
is reviewed in the final seven scene views, without material isolation screenshots.
