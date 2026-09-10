# Plane Detection

## Tool

`pico_xr_plane` — actions: `enable` / `disable` / `status`

## Dependency

- XR Origin present
- **VST enabled** (passthrough required by PICO)
- **The PICO-native runtime enabled** in XR Plug-in Management (the **PICO**
  loader, `ENABLE_PICO_XR_SDK`). Plane detection is **PICO-native ONLY** — it is
  **not** supported on the PICO OpenXR runtime (see the Notes). User
  prerequisite; this skill does not toggle it.

> **Plane detection does NOT run on PICO OpenXR.** Unlike Spatial Mesh, PICO
> ships **no** plane-detection OpenXR feature, so under the OpenXR loader the
> plane sense-data provider is never created and no plane data ever arrives. On
> that runtime `pico_xr_plane(action=enable)` returns `error`; the agent must
> STOP, relay the message, and guide the user to switch to the PICO-native
> loader (SKILL.md §3.1) — do NOT retry. `pico_xr_status` reports `runtime`
> (`native` / `openxr` / `none`); if it is `openxr`, tell the user plane
> detection is unsupported BEFORE attempting enable.

Plane Detection is the SensePack **sibling of Spatial Mesh**: both start a
sense-data system, then build and update meshes at runtime. The only
difference is the **data source** — Spatial Mesh consumes the SpatialMesh
provider (`PXR_Manager.SpatialMeshDataUpdated`), Plane Detection consumes the
PlaneDetection provider (`PXR_Manager.PlaneDetectionDataUpdated`). Because of
that kinship, this block mirrors Spatial Mesh in structure AND in its render
pipeline, and shares the same VST dependency.

## Driver

Plane rendering is driven by a **custom `PlaneDetectionManager`** (global
namespace) bundled in the MCP package alongside `SpatialMeshManager` (under
`Editor/SpatialMeshAssets~`). It reuses `SpatialMeshManager`'s render pipeline
VERBATIM — an object pool of wireframe mesh instances, a per-frame throttle,
the global `_TargetPosition` camera feed and the per-instance `_StartTime`
feed that drive the `Custom/TriangleFadeOutFromCenter` fade shader — so
detected planes render with the SAME visual as the spatial mesh. It calls
`PXR_MixedReality.StartSenseDataProvider(PlaneDetection)`, subscribes to
`PXR_Manager.PlaneDetectionDataUpdated` (PICO-native only — see the Notes),
bakes each plane's vertices to world space (`rotation*v+position`), and handles
the extra `MeshChangeState.Unchanged` that the plane stream emits. The driver
is guarded by `ENABLE_PICO_XR_SDK` and has **no OpenXR branch**.

> **Why NOT the SDK's `PXR_PlaneDetectionManager`?** The SDK driver feeds
> neither shader global (`_TargetPosition` / `_StartTime`) and overwrites the
> material color per semantic label — which clobbers the wireframe fade
> material. Reusing its prefab alone does NOT make the visual match Spatial
> Mesh. The custom `PlaneDetectionManager` fixes this by driving the fade
> shader exactly like `SpatialMeshManager` and NOT touching the material color.

> **Two-phase enable, exactly like Spatial Mesh.** Because the custom driver
> `.cs` must be copied into the project and compiled before it can be
> reflection-mounted, `enable` is **two-phase**:
>
> - **Phase 1** — the tool copies `PlaneDetectionManager.cs` + the shared
>   shaders/materials/prefab into `Assets/PICO_MCP/SpatialMesh`, which triggers
>   an Editor recompile. The response reports an import/recompile in progress
>   (`skipped`, `recompiling=true`).
> - **Settle loop** — poll `pico_xr_status` until the MCP bridge returns
>   (domain reload finished).
> - **Phase 2** — call `enable` again; now the type is loaded, so the tool
>   mounts and configures the driver.

## Inspector config (PlaneDetectionManager)

When enabling Plane Detection (phase 2), the driver is configured as follows
(identical to Spatial Mesh):

| Field (serialized name) | Value                                                                                                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `maxRenderPerFrame`     | `200`                                                                                                                                                        |
| `meshAmount`            | `300`                                                                                                                                                        |
| `meshContainer`         | the `[PICO_MCP] Plane` container Transform (sits at origin under the XR Origin)                                                                              |
| `meshPrefab`            | the **shared** bundled wireframe mesh prefab `MeshTriangleFadeOutPrefab` (material `Custom/TriangleFadeOutFromCenter`) — the SAME asset Spatial Mesh imports |
| `wireframeMaterial`     | the shared `TriangleFadeOutFromCenter.mat`                                                                                                                   |

> **Plane visual matches Spatial Mesh** by construction: same driver render
> pipeline, same wireframe prefab + material (single asset source: the MCP
> package's `Editor/SpatialMeshAssets~`). The `meshContainer` must sit at the
> origin because the driver bakes vertices to world space; the container is a
> fresh child of the XR Origin, so this holds.

## Cheatsheet

### Enable Plane Detection

- Pre: XR Origin (via orchestration step B.1) AND VST enabled (see orchestration step B.2).
- Call: `pico_xr_plane(action=enable)`.
- **Two-phase** (like Spatial Mesh):
  1. First `enable` — copies `PlaneDetectionManager.cs` + shared visual assets
     into `Assets/PICO_MCP/SpatialMesh`; returns `skipped` (`recompiling=true`).
  2. **Settle loop** — poll `pico_xr_status` until the bridge returns.
  3. Second `enable` — ensures the `[PICO_MCP] Plane` container under the XR
     Origin, mounts `PlaneDetectionManager`, configures the fields above; returns `ok`.
- If VST is not yet enabled, the orchestration loop will enable it first
  (step B.2): `pico_xr_vst(action=enable)`. No settle loop for VST — it does
  not trigger compile.

### Disable Plane Detection

- No deps to check.
- Call: `pico_xr_plane(action=disable)`.

### Status

- Call: `pico_xr_plane(action=status)`.

## Typical pipeline — enable (VST already on)

```
pico_xr_status()                  → xr_origin=ok, vst=on, plane=off
pico_xr_plane(action=enable)      → skipped (recompiling=true; driver imported)
pico_xr_status() [settle loop]    → poll until the MCP bridge returns (domain reload done)
pico_xr_plane(action=enable)      → ok  (mounts PlaneDetectionManager, configures fields)
pico_xr_status()                  → plane=on  (internal verify)
Save Scene                        → ok
```

### Typical pipeline — enable when VST is off

```
pico_xr_status()                  → xr_origin=ok, vst=off, plane=off
pico_xr_vst(action=enable)        → ok      (auto by orchestration step B.2)
pico_xr_plane(action=enable)      → skipped (recompiling=true; driver imported)
pico_xr_status() [settle loop]    → poll until the MCP bridge returns
pico_xr_plane(action=enable)      → ok      (mounts PlaneDetectionManager)
pico_xr_status()                  → vst=on, plane=on
Save Scene                        → ok
```

### Typical pipeline — disable

```
pico_xr_plane(action=disable)     → ok
pico_xr_status()                  → plane=off (internal verify)
Save Scene                        → ok
```

## Notes

- Plane Detection is **PICO-native ONLY**: it requires a PICO XR SDK installed
  with `ENABLE_PICO_XR_SDK` (the PICO-native loader) defined — the driver is
  guarded by `ENABLE_PICO_XR_SDK` alone. Unlike Spatial Mesh, PICO ships **no
  dedicated plane OpenXR feature**: the plane sense-data provider is created
  ONLY inside the native `PXR_Loader`
  (`UPxr_CreatePlaneDetectionSenseDataProvider`), so under the OpenXR runtime
  the provider never exists, `PXR_Manager.PlaneDetectionDataUpdated` never fires
  and `QueryPlaneAnchorAsync` has nothing to query.

  - **Native** (`ENABLE_PICO_XR_SDK`): `PXR_Manager` pumps its own event loop
    (`PXR_Manager.PollEvent`, driven by `PXR_Loader`), runs `QueryPlaneAnchor`
    on each sense-data update and fires `PXR_Manager.PlaneDetectionDataUpdated`;
    the driver only starts the provider and subscribes to that event.
  - **OpenXR** (`ENABLE_PICO_OPENXR_SDK`): **not supported.**
    `pico_xr_plane(action=enable)` returns `error` with a message to switch to
    the PICO-native loader. The agent must STOP, relay it, and guide the user
    (SKILL.md §3.1) — do NOT retry, do NOT mount the driver.

  If the type never loads after the settle loop on the native runtime, `enable`
  keeps returning `skipped`/`error` with a clear message — relay it and ask the
  user to install/update the PICO SDK. This block does NOT auto-install the PICO
  SDK or toggle providers.

- Because plane detection is a mixed-reality feature, VST/passthrough is a
  hard prerequisite — the orchestration loop enables it first if needed.
- Enable turns on `PXR_ProjectSetting.planeDetection` so `PXR_BuildProcessor`
  emits `enable_plane_detection` + the `SPATIAL_DATA` permission in the
  Android manifest; disable clears only that flag. Runtime event delivery is
  driven by the shared `PXR_Manager` (mounted on the XR Origin root by
  `EnsureXROrigin`, never added/removed by this block): it runs the plane query
  loop (`QueryPlaneAnchor` on every sense-data update) and fires
  `PlaneDetectionDataUpdated`, so the driver only starts the provider and
  subscribes.
- Enable also forces **PICO Stereo Rendering Mode = MultiPass**
  (`PXR_Settings.stereoRenderingModeAndroid`, shown in Project Settings > XR
  Plug-in Management > PICO). MR sense-data (passthrough + the plane mesh)
  mis-composites under Multiview/single-pass-instanced, so both Plane
  Detection and Spatial Mesh switch it to MultiPass on enable. This is a
  project-level setting — it is NOT reverted on disable.
