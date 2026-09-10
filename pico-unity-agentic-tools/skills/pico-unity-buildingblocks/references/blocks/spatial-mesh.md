# Spatial Mesh

## Tool

`pico_xr_spatial_mesh` — actions: `enable` / `disable` / `status`

## Dependency

- XR Origin present
- **VST enabled** (passthrough required by PICO)
- A PICO runtime enabled in XR Plug-in Management (PICO-native **or** PICO
  OpenXR — see SKILL.md §3.1). User prerequisite; this skill does not toggle it.

## Driver

Spatial Mesh rendering is driven by **`SpatialMeshManager.cs`**, a
`MonoBehaviour` singleton that subscribes to the spatial-mesh data stream and
builds/pools per-block meshes at runtime (plus an optional convex-hull bounds
pass). The stream source depends on the runtime: on the **PICO-native** path it
is `PXR_Loader.meshSubsystem` + `PXR_Manager.SpatialMeshDataUpdated`; on the
**PICO OpenXR** path (`ENABLE_PICO_OPENXR_SDK`) the driver obtains the
`XRMeshSubsystem` from `SubsystemManager` (created by the `PICOSpatialMesh`
OpenXR feature) and subscribes to `OpenXRExtensions.SpatialMeshDataUpdated`. The
driver branches on the compile define, so the same asset works on both runtimes.
These runtime assets are bundled with — and imported by — the
MCP package alone (`Editor/SpatialMeshAssets~` in
`Unity-MCP-Extensions`); they are **not** carried by this skill. The
`pico_xr_spatial_mesh(action=enable)` tool copies them into the user project
(`Assets/PICO_MCP/SpatialMesh`) on first enable:

| Asset                                       | Role                                                                                           |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `SpatialMeshManager.cs`                     | The driver component. Attach to the Spatial Mesh root GameObject.                              |
| `MeshTriangleFadeOutPrefab.prefab`          | `Mesh Prefab` — per-block mesh template (MeshFilter + MeshRenderer + MeshCollider on layer 6). |
| `TriangleFadeOutFromCenter.shader` / `.mat` | `Wireframe Material` — the triangle fade-out-from-center wireframe effect.                     |
| `MR_Unlit.shader` / `TA_MR_Unlit.mat`       | `Mask` material (`TA/MR_Unlit`, writes depth for passthrough occlusion).                       |

> The `.meta` files are intentionally **not** bundled — the MCP tool lets
> Unity regenerate GUIDs on first import, then repairs the cross-references.
> After import, wire the serialized fields per the **Inspector config** table
> below.

## Inspector config (SpatialMeshManager)

When enabling Spatial Mesh, the `SpatialMeshManager` component must be
configured exactly as follows:

| Field (serialized name)                        | Value                                                                              |
| ---------------------------------------------- | ---------------------------------------------------------------------------------- |
| `Mask` (`m_mask`)                              | `TA_MR_Unlit`                                                                      |
| **General configuration**                      |                                                                                    |
| `Max Render Per Frame` (`maxRenderPerFrame`)   | `200`                                                                              |
| `Mesh Amount` (`meshAmount`)                   | `300`                                                                              |
| **Materials and containers**                   |                                                                                    |
| `Mesh Container` (`meshContainer`)             | `SpatialMesh` (Transform) — the Spatial Mesh root Transform                        |
| `Mesh Prefab` (`meshPrefab`)                   | `MeshTriangleFadeOutPrefab`                                                        |
| `Mesh Calc Prefab` (`meshCalcPrefab`)          | `ConvexHull` (project prefab; see note)                                            |
| `Wireframe Material` (`wireframeMaterial`)     | `TriangleFadeOutFromCenter`                                                        |
| `Transparent Material` (`transparentMaterial`) | `Transparent` (project material; see note)                                         |
| `Convex Hull` (`convexHull`)                   | `None (Game Object)` — left unassigned; created at runtime from `Mesh Calc Prefab` |

> **External references not bundled with the MCP package:** `Mesh Calc Prefab`
> (`ConvexHull`) and `Transparent Material` (`Transparent`) are existing
> project assets. If they are absent from the project, tell the user and ask
> them to assign these two fields manually — do NOT auto-create substitutes.
> `SpatialMeshManager` also depends on `ConvexHullCalculator` (referenced as
> `calc`), which must already exist in the project.

## Cheatsheet

### Enable Spatial Mesh

- Pre: XR Origin (via orchestration step B.1) AND VST enabled (see orchestration step B.2).
- Call: `pico_xr_spatial_mesh(action=enable)`.
- The tool ensures a Spatial Mesh root GameObject exists under the XR Origin
  and attaches the `SpatialMeshManager` driver.
- After the tool returns `ok`, verify the driver's serialized fields match the
  **Inspector config** table above. If `Mesh Calc Prefab` / `Transparent
Material` could not be resolved, relay the warning and ask the user to wire
  them manually.
- If VST is not yet enabled, the orchestration loop will enable it first
  (step B.2): `pico_xr_vst(action=enable)`. No settle loop needed — VST does
  not trigger compile.

### Disable Spatial Mesh

- No deps to check.
- Call: `pico_xr_spatial_mesh(action=disable)`.

### Status

- Call: `pico_xr_spatial_mesh(action=status)`.

## Typical pipeline — enable (VST already on)

```
pico_xr_status()                        → xr_origin=ok, vst=on, spatial_mesh=off
pico_xr_spatial_mesh(action=enable)     → ok  (attaches SpatialMeshManager driver)
   → verify Inspector config: maxRenderPerFrame=200, meshAmount=300,
     Mask=TA_MR_Unlit, meshPrefab=MeshTriangleFadeOutPrefab,
     wireframeMaterial=TriangleFadeOutFromCenter
pico_xr_status()                        → spatial_mesh=on  (internal verify)
Save Scene                              → ok
```

### Typical pipeline — enable when VST is off

```
pico_xr_status()                        → xr_origin=ok, vst=off, spatial_mesh=off
pico_xr_vst(action=enable)              → ok      (auto by orchestration step B.2)
pico_xr_spatial_mesh(action=enable)     → ok      (attaches SpatialMeshManager driver)
pico_xr_status()                        → vst=on, spatial_mesh=on
Save Scene                              → ok
```

### Typical pipeline — disable

```
pico_xr_spatial_mesh(action=disable)    → ok
pico_xr_status()                        → spatial_mesh=off (internal verify)
Save Scene                              → ok
```

## Notes

- Enable turns on `PXR_ProjectSetting.spatialMesh` so `PXR_BuildProcessor`
  emits `enable_mesh_anchor` + the `SPATIAL_DATA` permission in the Android
  manifest; disable clears only that flag. Runtime `SpatialMeshDataUpdated`
  events are dispatched by the shared `PXR_Manager` mounted on the XR Origin
  root by `EnsureXROrigin` (never added/removed by this block).
- **PICO OpenXR runtime.** On the OpenXR loader (`ENABLE_PICO_OPENXR_SDK`) the
  spatial-mesh subsystem is created by the PICO `PICOSpatialMesh` OpenXR feature,
  which must be ENABLED on the Android build target. On enable, the C# layer
  flips both `PassthroughFeature` (via the VST dependency) and `PICOSpatialMesh`
  on by reflection (mirrors the SDK's `PXR_Utils.EnableOpenXRFeature<T>()`), and
  the bundled `SpatialMeshManager` reads the mesh from the OpenXR subsystem +
  `OpenXRExtensions.SpatialMeshDataUpdated` instead of the native path. All
  automatic — but the OpenXR loader + PICO feature group must already be enabled
  by the user (SKILL.md §3.1); the skill does not toggle providers.
- Enable also forces **PICO Stereo Rendering Mode = MultiPass**
  (`PXR_Settings.stereoRenderingModeAndroid`, shown in Project Settings > XR
  Plug-in Management > PICO). MR sense-data (passthrough + the spatial mesh)
  mis-composites under Multiview/single-pass-instanced, so both Spatial Mesh
  and Plane Detection switch it to MultiPass on enable. This is a
  project-level setting — it is NOT reverted on disable.
