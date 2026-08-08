# Spatial Mesh

## Tool

`pico_xr_spatial_mesh` — actions: `enable` / `disable` / `status`

## Dependency

- XR Origin present
- **VST enabled** (passthrough required by PICO)

## Driver

Spatial Mesh rendering is driven by **`SpatialMeshManager.cs`**, a
`MonoBehaviour` singleton that subscribes to `PXR_Manager.SpatialMeshDataUpdated`
and builds/pools per-block meshes at runtime (plus an optional convex-hull
bounds pass). It ships with this skill under
[`../../assets/spatial-mesh/`](../../assets/spatial-mesh):

| Asset | Role |
|-------|------|
| `SpatialMeshManager.cs` | The driver component. Attach to the Spatial Mesh root GameObject. |
| `MeshTriangleFadeOutPrefab.prefab` | `Mesh Prefab` — per-block mesh template (MeshFilter + MeshRenderer + MeshCollider on layer 6). |
| `TriangleFadeOutFromCenter.shader` / `.mat` | `Wireframe Material` — the triangle fade-out-from-center wireframe effect. |
| `MR_Unlit.shader` / `TA_MR_Unlit.mat` | `Mask` material (`TA/MR_Unlit`, writes depth for passthrough occlusion). |

> The `.meta` files are intentionally **not** bundled — let Unity regenerate
> GUIDs on first import. After import, wire the serialized fields per the
> **Inspector config** table below.

## Inspector config (SpatialMeshManager)

When enabling Spatial Mesh, the `SpatialMeshManager` component must be
configured exactly as follows:

| Field (serialized name) | Value |
|-------------------------|-------|
| `Mask` (`m_mask`) | `TA_MR_Unlit` |
| **General configuration** | |
| `Max Render Per Frame` (`maxRenderPerFrame`) | `200` |
| `Mesh Amount` (`meshAmount`) | `300` |
| **Material and container** | |
| `Mesh Container` (`meshContainer`) | `SpatialMesh` (Transform) — the Spatial Mesh root Transform |
| `Mesh Prefab` (`meshPrefab`) | `MeshTriangleFadeOutPrefab` |
| `Mesh Calc Prefab` (`meshCalcPrefab`) | `ConvexHull` (project prefab; see note) |
| `Wireframe Material` (`wireframeMaterial`) | `TriangleFadeOutFromCenter` |
| `Transparent Material` (`transparentMaterial`) | `Transparent` (project material; see note) |
| `Convex Hull` (`convexHull`) | `None (Game Object)` — left unassigned; created at runtime from `Mesh Calc Prefab` |

> **External references not bundled in this skill:** `Mesh Calc Prefab`
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
