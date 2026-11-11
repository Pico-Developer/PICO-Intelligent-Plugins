# Transparent PreviewSurface Authoring

Use this recipe during managed material production for transparent glass or another
alpha-blended surface. Preserve the existing geometry and unrelated materials.
Apply the parent task's authoring budget and reporting policy; this recipe adds no
new approval, visual gate, or workflow branch.

## Confirm the opacity input

Resolve the actual target binding and inspect the current Editor's selected shader
definition through `get_shader_node_catalog`. For
`ND_UsdPreviewSurface_surfaceshader`, the verified input is float `opacity`, with
default `1`. Author `inputs:opacity`; `inputs:diffuseOpacity` is not an alias on
this node. Keep other shader types subject to their own catalog contracts.

High-level `transparent_glass` presets and templates can accept `opacity = 0.055`
but generate `inputs:diffuseOpacity = 0.055`. The resulting graph can validate and
compile while the shader's actual opacity remains at its opaque default. Compare
the generated and normalized graph with the selected node's inputs before treating
a high-level tool response as success. Remove the unsupported attribute from that
shader and set its actual `opacity` input. Lowering the same high-level alpha again
does not correct the input name.

## Minimal candidate

After confirming the current node contract, use this self-contained candidate or
apply its fields to the target's existing graph. The material service normalizes
the example material path to the resolved binding; use the returned actual paths.
The value `0.055` is a verified clear-glass example, not a universal glass default.
Choose opacity and appearance from the accepted requirement.

```usda
#usda 1.0
(
    defaultPrim = "Root"
    metersPerUnit = 1
)

def Xform "Root"
{
    def Material "Glass" (
        customData = {
            string materialType = "SHADER_GRAPH"
            string blendingMode = "TRANSPARENT"
            string cullingMode = "BACK"
            bool depthTest = 1
            bool depthWrite = 0
        }
    )
    {
        token outputs:mtlx:surface.connect = </Root/Glass/PreviewSurface.outputs:out>

        def Shader "PreviewSurface"
        {
            uniform token info:id = "ND_UsdPreviewSurface_surfaceshader"
            color3f inputs:diffuseColor = (0.65, 0.85, 1)
            float inputs:opacity = 0.055
            float inputs:roughness = 0.04
            float inputs:metallic = 0
            token outputs:out
        }
    }
}
```

## Apply, inspect and save

1. Call `validate_material_usda` for the exact existing target. Require
   `can_preview = true` and zero errors, then inspect `normalized_usda_text` again:
   the active surface shader must retain `inputs:opacity` and the intended value
   or connected source. Confirm the surface connection targets its valid output;
   repair proven stale legacy outputs inside this material. Validation alone does
   not prove that the shader consumes every authored attribute.
2. Pass that normalized text to `preview_material_usda`. Let native compilation
   settle, then inspect an exterior screenshot with known background or interior
   objects. Keep the glass active and the camera outside. Verify both see-through
   content and any required glass outline/highlights; hiding the sphere or viewing
   from inside cannot establish transparency. For a surrounding glass shell, check
   another useful exterior angle when occlusion leaves the result uncertain.
3. If it remains opaque, inspect the effective graph's node ID, opacity input,
   surface connection and blend/depth/culling state. Repair the evidenced defect,
   revalidate and preview within the remaining budget. Preserve the last safe
   committed material and report unmet behavior if repair cannot finish.
4. Commit the accepted preview to a new unused material asset path. Immediately
   use documented Editor scene APIs to flush and save the exact target scene, such
   as `se.flush_scene_state()` and `se.scene.save_current()` after obtaining the
   native script auth token. A material asset commit or `binding_verified = true`
   does not establish that the scene was saved; treat
   `external_scene_save_status = "unverified"` as a pending scene-save checkpoint.
   Finish this checkpoint before cleanup or another row can consume the budget.
5. Reconcile the live binding with the saved target scene: confirm the actual
   Shader Graph identity, active surface source, opacity and render state. Read
   saved USD only for verification; never patch Editor-managed USD through file
   I/O. Save again after later binding changes and preserve this Graph during PBR
   cleanup. Reuse unchanged verified saves and observations.
6. Report the actual opacity input/value, render state, target/material identity,
   viewed image paths, save result and remaining limitations using the live report
   schema. If an authorized `se.scene.open` returns `was_loaded = true`, it reused
   an already loaded scene; do not report independent disk reload or process-restart
   verification or restart Editor merely to force a reread. Prefer
   `se.scene.reload(...)` with `discard_unsaved=False` and an available verified
   `expected_disk_digest`; require `status: "ok"` and recheck bindings and the image.
   Follow the owning workflow's bounded reopen policy; see
   [material-production.md](material-production.md) for the save/reload procedure.
