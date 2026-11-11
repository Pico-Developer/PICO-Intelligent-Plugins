# Capability Evidence and Boundary Cases

## Evidence hierarchy

Use current-build observations or exact-build documentation for route readiness.
Prefer a successful operation plus relevant readback/render/save evidence over an
accepted input schema. A tool signature proves neither rendered behavior nor a
working binding path.

Apply the **RGBA-only default-PBR authoring boundary** during scene assembly.
Required non-RGBA effects belong in accepted SceneSpec semantic tasks for the managed
material subflow. This assembly boundary does not establish an Editor build
identifier or Graph execution readiness.

Use historical tests to narrow the next query. Use general shading-model references
to avoid conceptual errors. Neither establishes current Editor capability.

## Historical Editor snapshot

The repository records the following live tests from **2026-10-23**. The exact
tested Editor build identifier is not recorded; this is historical evidence.

- Cube, Sphere, and Plane had a bound `DefaultMaterial` whose `material_kind` was
  `PBR`.
- `Entity.set_color(r, g, b, a)` updated BaseColor. `get_color()` matched all four
  components before and after save, and the material remained PBR.
- RGBA readback did not establish transparent blending. RGB/BaseColor did not
  establish emission or illumination of surrounding surfaces.
- The generic `set_material_param` API raised `TypeError` for BaseColor RGBA,
  metallic, roughness, opacity, normalScale, reflectance, ambientOcclusion,
  clearCoat, clearCoatRoughness, emissive, and emissiveScale. These failures
  did not invalidate the independent `Entity.set_color` entry point.
- Numeric getters and parameter enumeration had native binding errors.
- `resolve_material_binding` could fail on a valid primitive DefaultMaterial
  because of a missing `UsdMaterialInfoComponent`. Do not impose that resolver
  as a gate on a separately verified default-material path.
- `set_material_properties` could create a Graph through a preset. Do not classify
  the result as PBR from the tool name.

Bundled source:

- [Default PBR capability record](pbr-materials.md)

The recorded default-only workflow applies supported appearance controls during
primitive creation and reports limitations. This historical workflow is not proof
of a current graph generator, graph handoff, or material review gate. A decision
Skill cannot supply missing runtime integration.

## General model facts

- [OpenUSD Preview Surface specification](https://openusd.org/release/spec_usdpreviewsurface.html)
  describes PBR inputs including metallic, roughness, clearcoat, emission, opacity,
  IOR, normals, and textures. It does not promise that the Editor exposes every
  input, blend mode, refraction feature, or texture authoring path.
- [Unity Shader Graph PBR Master Node](https://docs.unity3d.com/Packages/com.unity.shadergraph@7.3/manual/PBR-Master-Node.html)
  demonstrates that graph authoring can implement PBR. Unity node support is not
  evidence that those nodes exist in Spatial Editor.

## Focused verification

Resolve the Editor build and advertised API for execution readiness; do not
re-probe known unavailable PBR controls during this RGBA-only selection test.
Check the current binding and material kind when observations are available.
If necessary, hand off a minimal isolated probe through the owning workflow:
one relevant object, one required control, concise before/after observations,
rendered evidence for visual behavior, and persistence checks for authored state.
Do not dump all material parameters or scan historical run directories.

For a graph candidate, identify the supported graph format, required computation
and render state, usable creation/reuse path, validation, rendering, binding, and
save behavior. Report unsupported steps precisely. Do not repeatedly probe a
known failing API or construct unsupported node names.

## Boundary cases

Apply the RGBA-only boundary to required behavior. Material names alone do not
establish the requirement, and suitable existing bindings remain reusable.

| Requirement                                                              | Decision under the current boundary                                                                     |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| Opaque red primitive; only BaseColor change required                     | PBR; execution readiness still needs the current color path and build                                   |
| Gray panel; default surface response accepted                            | PBR through RGBA; do not claim controlled metallic or roughness                                         |
| A metallic value, brushed reflections, or specific roughness is required | Graph requirement with a PBR-path gap; these controls are unavailable                                   |
| True transparent glass or refraction is required                         | Graph requirement; alpha readback does not establish transparent blending                               |
| Static luminous sign                                                     | Graph requirement for emission; bright BaseColor is insufficient                                        |
| Flickering emission                                                      | Graph requirement; emission and persistent animation exceed RGBA authoring                              |
| Flowing water with moving ripples                                        | Graph requirement for the requested flow/ripple behavior; do not assume a PBR texture/UV animation path |
| Animated dissolve with edge coloration                                   | Graph requirement for masking, edge coloration and temporal computation                                 |
| Holographic Fresnel bands                                                | Graph requirement for view-dependent and other requested effects                                        |
| Visible wood grain or normal-map relief                                  | Graph requirement if new authoring is needed; texture/normal assignment is unavailable in this PBR path |
| Extra metallic/roughness polish is explicitly optional                   | PBR with retained defaults and a reported limitation                                                    |
| Existing suitable imported material                                      | Preserve the observed binding, including its existing textures or Graph                                 |
| User explicitly requests a Shader Graph metallic material                | Honor Graph with a PBR surface model; reuse a suitable graph when possible                              |
| A glow requirement means lighting the room or emitting sparks            | Route light/particle work separately; a Graph material alone does not fulfill it                        |
| Required Graph authoring is unavailable in the current Editor build      | Keep the requirement and record a failed row with the concrete capability gap; continue other materials |

## Example report

This is a **provisional planning report**, grounded only in the historical snapshot.
It deliberately claims no current-build readiness.

```json
{
  "schemaVersion": 1,
  "stage": "plan",
  "editorBuild": null,
  "evidence": [
    {
      "id": "rgba-2026-10-23",
      "scope": "historical",
      "editorBuild": null,
      "checkedAt": "2026-10-23",
      "source": "pbr-materials.md",
      "claim": "Cube, Sphere and Plane BaseColor RGBA updated through Entity.set_color and survived save while DefaultMaterial remained PBR; tested build ID was not recorded."
    }
  ],
  "decisions": [
    {
      "id": "opaque-red-shell",
      "targetEntityPaths": [],
      "surfaceModel": "pbr",
      "route": "pbr_parameters",
      "status": "provisional",
      "trigger": "unresolved",
      "requiredFeatures": ["Opaque red BaseColor"],
      "optionalFeatures": [],
      "pbrGap": null,
      "reason": "The historical default-PBR color path is a plausible candidate; verify it on the current build before authoring.",
      "capabilityEvidenceRefs": ["rgba-2026-10-23"],
      "verificationPlan": [
        "Resolve the Editor build and exact shell entity paths.",
        "Verify the current default-PBR color path, rendered opaque color and persistence through the authorized workflow."
      ],
      "limitations": ["No current-build capability evidence is available."]
    }
  ]
}
```
