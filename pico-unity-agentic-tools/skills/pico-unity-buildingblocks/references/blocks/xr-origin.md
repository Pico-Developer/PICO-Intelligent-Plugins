# XR Origin

## Dependency

- Package `com.unity.xr.interaction.toolkit`
- Sample `Starter Assets` (imported from that package)

## Cheatsheet

XR Origin is not a standalone block tool — it is a shared dependency ensured
by the orchestration loop (step B.1). When `pico_xr_status()` shows
`xr_origin` is missing:

```
B.1.a Ensure XRI package
      pico_xr_package(action=info, packageName=com.unity.xr.interaction.toolkit)
      If skipped:
        pico_xr_package(action=add, identifier=com.unity.xr.interaction.toolkit)
        → run the post-write settle loop

B.1.b Ensure Starter Assets sample
      pico_xr_package(action=list_samples,
                       packageName=com.unity.xr.interaction.toolkit)
      If "Starter Assets" not in imported list:
        pico_xr_package(action=import_sample,
                         packageName=com.unity.xr.interaction.toolkit,
                         sampleName="Starter Assets")
        → run the post-write settle loop
```

The C# layer's `EnsureXROrigin()` finds or creates the agent XR Origin from
the XRI Starter Assets prefab. No separate `pico_xr_*` tool call is needed
to create the Origin itself — the block tools (VST, Controller, etc.) will
trigger `EnsureXROrigin()` internally.

## Notes — PXR_Manager on every XR Origin

`EnsureXROrigin()` mounts the PICO SDK **`PXR_Manager`** component on the XR
Origin **root** GameObject (above the Main Camera) — on both the create path
and the reuse path, so pre-existing rigs are upgraded in place. `PXR_Manager`
is the runtime event dispatcher: its `PollEvent()` fires the static
`SpatialMeshDataUpdated` / `PlaneDetectionDataUpdated` events that the Spatial
Mesh and Plane drivers subscribe to. Mounting it once here (rather than per
block) means **every** agent-generated XR Origin can drive the MR sense-data
features, not just VST/SpatialMesh/Plane.

- Reflection-resolved (`ByteDance.PICO.XR.PXR_Manager`, R3); silently skipped
  if the PICO SDK is not installed.
- Idempotent (R1): mounted only if absent.
- Non-destructive (R2): block `disable` never removes the shared
  `PXR_Manager` — only the per-block capability flag is cleared (see the VST /
  Spatial Mesh / Plane block docs).

The per-feature checkboxes shown in the `PXR_Manager` Inspector
(Video Seethrough / Spatial Mesh / Plane Detection / Hand Tracking …) are NOT
fields on the component — they are `bool` flags on the `PXR_ProjectSetting`
ScriptableObject, consumed at BUILD time by `PXR_BuildProcessor` to emit the
Android manifest `<meta-data>` + permissions. Each block turns on its own flag
on enable; without it the OS delivers no sense data even though the driver is
mounted.

## Typical pipeline — ensure XR Origin (when `xr_origin` is missing)

```
pico_xr_status()                                              → xr_origin=missing
pico_xr_package(action=info, packageName=com.unity.xr.interaction.toolkit)
  └─ if skipped: pico_xr_package(action=add, identifier=com.unity.xr.interaction.toolkit)
                  → settle loop (poll pico_xr_status until bridge online)
pico_xr_package(action=list_samples, packageName=com.unity.xr.interaction.toolkit)
  └─ if "Starter Assets" missing:
        pico_xr_package(action=import_sample, packageName=…, sampleName="Starter Assets")
                  → settle loop (poll pico_xr_status until bridge online)
pico_xr_status()                                              → xr_origin=ok
```

No `pico_xr_*` call creates the Origin GameObject directly — the next block
action (e.g. `pico_xr_vst(enable)`) invokes `EnsureXROrigin()` internally.

## Notes — single-active-camera invariant

The agent XR Origin ships its own Main Camera. A scene with more than one
active camera produces a multi-camera render conflict (most visibly it breaks
VST passthrough). So `EnsureXROrigin()` — which runs on **every** block
enable/configure, not just first creation — collapses the scene to a single
active camera:

- Every _other_ enabled scene camera has `Camera.enabled` set to `false`
  (and its paired `AudioListener` disabled). Cameras belonging to the agent
  XR Origin subtree are never touched.
- This is **non-destructive** (R2): foreign camera GameObjects are never
  `SetActive(false)`-ed or destroyed — only the `Camera` component is
  switched off, so it stops rendering but the object graph is intact.
- It is **reversible** (R5): every flip is `Undo`-recorded (Ctrl+Z restores
  it), and the MCP layer tracks exactly which cameras it disabled so
  `PICO MCP > Camera > Restore Foreign Cameras` re-enables only those —
  never a camera the user disabled themselves.
- It is **idempotent** (R1): cameras already off are skipped.

Observability: `pico_xr_status` returns `data.camera`:

| field             | meaning                                              |
| ----------------- | ---------------------------------------------------- |
| `activeCameras`   | cameras currently active-and-enabled (should be `1`) |
| `managedDisabled` | foreign cameras the MCP layer is holding disabled    |
| `single`          | `true` when exactly one active camera remains        |

Note: `disable`-ing a block (e.g. `pico_xr_vst(disable)`) does **not**
auto-restore foreign cameras — as long as the agent XR Origin and its Main
Camera remain in the scene, the invariant must still hold. Restore is an
explicit user action (menu item or Ctrl+Z).
