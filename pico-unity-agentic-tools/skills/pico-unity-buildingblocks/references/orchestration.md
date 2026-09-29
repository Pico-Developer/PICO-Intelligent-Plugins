# Orchestration details

This file expands §4 of the main SKILL.md with full step-by-step details and
the domain-reload settle loop.

## Full orchestration loop

For ANY request "enable / configure / disable / query block B":

```
A. Snapshot
   r = call pico_xr_status()
   - If r.status != "ok": STOP and relay r.error.

B. For ENABLE / CONFIGURE actions, resolve dependencies (skip for DISABLE/STATUS):

   B.1 XR Origin dependency
       If r.data.xr_origin is missing (none of the four blocks shows an origin):
         B.1.a Ensure XRI package
               Use pico-unity-package-manager:
                 pico_xr_package(action=info, packageName=com.unity.xr.interaction.toolkit)
               If skipped:
                 pico_xr_package(action=add, identifier=com.unity.xr.interaction.toolkit)
                 → run the post-write settle loop (see below)
         B.1.b Ensure Starter Assets sample
               pico_xr_package(action=list_samples,
                                packageName=com.unity.xr.interaction.toolkit)
               If "Starter Assets" not in imported list:
                 pico_xr_package(action=import_sample,
                                  packageName=com.unity.xr.interaction.toolkit,
                                  sampleName="Starter Assets")
                 → run the post-write settle loop

   B.2 Block-specific extras
       If block is `spatial_mesh`:
         If r.data.vst.installed == false → first enable VST:
           call pico_xr_vst(action=enable)
           (no settle needed — VST does not trigger compile)
         Spatial Mesh is TWO-PHASE on first enable because its bundled
         `SpatialMeshManager.cs` must compile before it can be mounted:
           Phase 1: pico_xr_spatial_mesh(action=enable) copies the driver and
             visual assets into `Assets/PICO_MCP/SpatialMesh`. The call returns
             `status=skipped`, `data.recompiling=true`, and a warning that names
             the imported SpatialMeshManager assets.
           → record transition `spatial_mesh:SpatialMeshManager`, run the
             post-write settle loop, then retry the same enable once.
           Phase 2: the loaded driver is mounted and configured; enable returns
             `status=ok`. If the same transition is returned again after settle,
             STOP because the workflow made no progress.
       If block is `plane`:
         (Plane Detection is the SensePack sibling of Spatial Mesh and shares
          the same VST dependency AND the same bundled-asset / two-phase
          enable model — BUT it is PICO-NATIVE ONLY.)
         PICO-NATIVE ONLY: there is no plane-detection OpenXR feature, so plane
         detection does NOT run on the PICO OpenXR runtime. BEFORE resolving
         deps, check r.data.runtime from the step-A snapshot: if it is "openxr",
         STOP — do NOT enable VST, do NOT call pico_xr_plane(action=enable). Tell the
         user plane detection is unsupported on PICO OpenXR and guide them to
         switch to the PICO-native loader (SKILL.md §3.1). (If the agent still
         calls enable on OpenXR, the C# layer returns `error` with the same
         guidance — relay it and stop.)
         On the PICO-native runtime:
         If r.data.vst.installed == false → first enable VST:
           call pico_xr_vst(action=enable)
           (no settle needed — VST does not trigger compile)
         Like Spatial Mesh, Plane Detection is TWO-PHASE: its driver is a
         custom bundled `PlaneDetectionManager.cs` (mirrors SpatialMeshManager's
         pool + fade-shader pipeline, sourced from
         `PXR_Manager.PlaneDetectionDataUpdated`). It is NOT the SDK's
         PXR_PlaneDetectionManager — the SDK driver overwrites the material
         colour and does not feed the fade shader, so its visuals would not
         match Spatial Mesh.
           Phase 1: pico_xr_plane(action=enable) copies the driver .cs (+
             shared wireframe visual assets) into the project. The .cs import
             triggers a domain reload, so the first call returns
             `status=skipped` with `detail` mentioning recompiling.
           → run the post-write settle loop (poll pico_xr_status until the
             bridge returns) — SAME loop as a package install.
           → record transition `plane:PlaneDetectionManager`.
           Phase 2: call pico_xr_plane(action=enable) AGAIN; now
             PlaneDetectionManager is compiled/loaded, so it mounts + configures
             and returns `status=ok`.
       If block is `controller`:
         (No extra package install — PICO controller prefabs ship with the
          PICO SDK already in the project. The C# layer will report
          `error` with a clear message if the prefabs are missing; relay it
          verbatim and ask the user to install/update the PICO SDK.)
       If block is `hand`:
         Branch model dependencies by r.data.runtime BEFORE calling enable:
           If runtime is `native`:
             No extra package install for the MODELS. PICO HandLeft/HandRight
             prefabs ship with the PICO SDK. The C# layer reports `error` if
             they are missing; relay it and ask the user to verify/update the
             PICO SDK.
           If runtime is `openxr`:
             Ensure package `com.unity.xr.hands` with the package-manager §4.1
             flow. Then list its samples and ensure `HandVisualizer` is
             imported with §4.2/§4.3. Run the post-write settle loop after each
             successful package/sample mutation. These prefabs are the OpenXR
             hand MODELS; never prescribe PICO HandLeft/HandRight on this path.
           If runtime is `none`:
             STOP with the provider-missing guidance from SKILL.md §3.1.
         For BOTH native and OpenXR runtimes, ensure the XRI
         `Hands Interaction Demo` sample is imported before enable. Use the
         package-manager §4.2/§4.3 flow and settle after a successful import.
         Once those dependencies are ready, call hand enable. The tool still has
         an idempotent on-demand import fallback, but normal orchestration must
         not rely on it.
         After the runtime-specific models are ready, enable also wires them
          into the same XRInputModalityManager the controller block uses, so a
          connected controller natively auto-hides the hand models — no extra
          step and no dependency to resolve here.
          Enable also flips the OpenXR `HandTracking` + `HandInteractionProfile`
          features on (Android target, reflection, mirrors PICO SDK
          `PXR_Utils.EnableHandTrackingFeature()`) so a hand pinch surfaces as
          an XRI select input, AND adds the PICO hand pinch/grasp bindings to the
          XRI `Select` action (by invoking the PICO SDK's `XRI Hand Interaction`
          building block via reflection). This Select-action binding is the ACTION
          half of pinch->grab and was the missing piece that let controller grab
          work while hand grab did not — the controller preset binds Select, the
          hand action did not. Idempotent + no scene side effects.
          HAND-ONLY MUST NOT SHOW A CONTROLLER (defect ① fix): when the Controller
          module is not active, enable NULLS the modality manager's
          leftController/rightController refs so the generic (non-PICO)
          Starter-Assets controller does NOT resurface. A controller appears only
          when the user runs `pico_xr_controller` (which mounts the PICO prefab
          and re-binds those refs). So "add hand pick-up" alone yields hands only.
          HAND INTERACTOR FALLBACK IS TWO-PHASE (defect ② + ③ fix): a hand pinch surfacing
          as a select is only HALF of grab — something must RECEIVE that select.
          The runtime-specific hand models are visual/tracking only and carry no interactor,
          so enable instantiates the XRI `Hands Interaction Demo` sample's
          `XR Origin Hands (XR Rig)` prefab (identified reflection-first by an
          XROrigin component + a `Camera Offset/Left Hand|Right Hand` structure,
          so we do not hardcode its filename), UNPACKS it, then EXTRACTS its
          `Left Hand` / `Right Hand` interactor groups into our Camera Offset as
          agent-owned markers (`[PICO_MCP] Hand Interactor L` /
          `[PICO_MCP] Hand Interactor R`), and destroys the temporary rig. This
          is required because `Left Hand` / `Right Hand` only exist as
          GameObjects INSIDE the rig prefab — they are NOT independent prefab
          assets, so any "scan the sample for a prefab named *left/right*"
          approach picks unrelated affordance leaves and never mounts anything
          usable. If dependency pre-resolution was bypassed and enable must
          import that sample itself, the call returns `status=skipped` with
          `data.recompiling=true` and `detail` mentioning the sample.
            → run the post-write settle loop (poll pico_xr_status until the bridge
              returns) — SAME loop as a package install.
            Record transition `hand:Hands Interaction Demo`, then call
            pico_xr_hand(action=enable) AGAIN; now the sample is
            present, so it mounts the interactors and returns `status=ok`. Once
            the sample is imported, enable is single-phase.
          FAR-RAY MUST FOLLOW THE HAND (defect ③ fix): the interactor group's
          NearFar caster + line-visual line origin come from the sample rig as
          prefab OVERRIDES pointing at each hand's sibling `Aim Pose`. Extracting
          the group out of the rig silently drops those overrides, so the ray
          would fall back to the interactor GameObject (Camera Offset origin) and
          shoot from the head instead of the hand. Enable therefore re-wires the
          four references — `InteractionAttachController.transformToFollow`,
          both casters' `castOrigin`, and `CurveVisualController.lineOriginTransform`
          — to the local `Aim Pose` after reparent (reflection, R3).
       If block is `grab`:
         (Grab reuses the SAME XRI dependency as XR Origin — the
          com.unity.xr.interaction.toolkit package + `Starter Assets` sample —
          so B.1 already covers it; there is no EXTRA package to install here.
          Grab is DECOUPLED from hand vs controller: it does NOT re-show the
          controller module and does NOT add interactors to controller nodes.
          Whether a hand or controller is visible — and that a visible
          controller uses the PICO prefab — is owned by the input blocks
          (`pico_xr_controller` / `pico_xr_hand`), NOT by grab. So a full
          "controller grab" flow is `pico_xr_controller(action=enable)` +
          `pico_xr_grab(action=enable)`; a "hand grab" flow is
          `pico_xr_hand(action=enable)` + `pico_xr_grab(action=enable)`.
          `enable` only guarantees a scene XRInteractionManager exists (creating
          an agent-owned host only if none exists) and drops the grab marker.
          Because the broker alone makes nothing grabbable, an
          "enable grab for object X" request should be TWO calls: first
          pico_xr_grab(action=enable), then
          pico_xr_grab(action=make_grabbable, target="X"). If the user just
          wants a quick demo, call make_grabbable with no target to spawn a
          sample cube.
          make_grabbable resolves `target` against the ACTIVE scene by name or
          hierarchy path; if the object is not found, relay the error and ask
          the user for the exact name/path — do NOT guess.
          Grab does NOT copy any .cs driver and does NOT trigger a domain
          reload — no settle loop needed.)

C. Perform the action
   call pico_xr_<block>(action=<verb>, ...params)
   Interpret result by `status`:
     - ok               → relay summary
     - already_present  → relay summary + "no change made"
     - skipped          → classify by action + runtime + workflow context:
                          TRANSITIONAL first-enable: Spatial Mesh, Plane, or Hand
                          enable returns `data.recompiling=true`, and its
                          `detail`/`warning` identifies a documented driver/sample
                          import. Record a transition key of block + imported
                          driver/sample, run one bounded settle loop, then retry
                          the SAME action. Allow each distinct transition once.
                          OpenXR Hand can advance through `HandVisualizer` and
                          `Hands Interaction Demo` as separate transitions when
                          its dependencies were not pre-resolved.
                          TRANSITIONAL dependency: a package/sample is missing
                          while resolving dependencies for the current, already-
                          authorized enable/configure action. Follow the package-
                          manager §4.1-§4.3 fallback and its settle boundary.
                          A read-only package query is NOT an install permission.
                          For every other skipped, or if the same transition is
                          returned again after settle, relay the warning and ask
                          how to proceed. A new skipped is not progress unless it
                          names another documented transition for that block.
     - error            → relay summary + error, ask user how to proceed

   The complete allowlist of first-enable transition keys is:
     - `spatial_mesh:SpatialMeshManager`
     - `plane:PlaneDetectionManager`
     - `hand:HandVisualizer`
     - `hand:Hands Interaction Demo`
   Derive the key from the called tool plus the exact imported driver/sample
   named in `detail`/`warning`; do not infer it from the generic `summary`. Any
   other key is non-transitional and must stop.

   Side effects worth knowing (no extra step needed — handled by the C# layer):
     - The FIRST block that triggers EnsureXROrigin() mounts PXR_Manager on
       the XR Origin root (shared runtime event dispatcher for MR sense data).
     - Each MR block (vst / spatial_mesh / plane) turns ON its own
       PXR_ProjectSetting capability flag (videoSeeThrough / spatialMesh /
       planeDetection) on enable, so PXR_BuildProcessor emits the matching
       Android manifest meta-data + permission at build time. disable clears
       ONLY that block's flag; the shared PXR_Manager is never removed.
     - Enabling spatial_mesh or plane forces PICO Stereo Rendering Mode =
       MultiPass (PXR_Settings.stereoRenderingModeAndroid); MR sense-data
       composites incorrectly under Multiview. Project-level, not reverted on
       disable.
     - RUNTIME PROVIDER (PICO-native vs PICO OpenXR) is a USER prerequisite,
       NOT resolved here (SKILL.md §3.1). The block code branches on the
       compile define (`ENABLE_PICO_XR_SDK` vs `ENABLE_PICO_OPENXR_SDK`) and, on
       the OpenXR path, auto-enables the required OpenXR FEATURE asset on the
       Android target (VST → PassthroughFeature; spatial_mesh → PICOSpatialMesh)
       via reflection — mirrors the PICO SDK building
       blocks. But the agent NEVER installs/toggles the XR Plug-in Management
       LOADER. If neither define is set, the block returns error/skipped saying
       the driver type never appeared → STOP and use the provider-missing
       guidance template in SKILL.md §3.1; do NOT auto-fix or retry.
     - PLANE DETECTION IS PICO-NATIVE ONLY: it has no OpenXR feature and does
       NOT run on the PICO OpenXR runtime. When r.data.runtime == "openxr",
       plane enable returns `error` — STOP, relay it, and guide the user to the
       PICO-native loader (do NOT auto-fix or retry).
     - Plane Detection uses the SAME bundled fade-shader pipeline as Spatial
       Mesh: its custom `PlaneDetectionManager` reuses the shared wireframe
       mesh prefab + `TriangleFadeOutFromCenter` material, so the two MR
       meshes share one visual style / asset source. Because the driver .cs
       is imported on enable, Plane Detection is two-phase (see B.2).

D. Internal verification (NOT user-facing)
   call pico_xr_status() and verify the target block flipped as expected.
   - Use this only to detect a silent failure (e.g. tool returned ok but
     status snapshot says the block is still off).
   - Also confirm the single-active-camera invariant held:
     `r.data.camera.single == true` (i.e. `activeCameras == 1`). Any
     enable/configure that touched the XR Origin should collapse the scene to
     exactly one active camera. If `activeCameras > 1`, the agent XR Origin's
     Main Camera is competing with a foreign camera — warn the user (this
     usually breaks VST passthrough) rather than silently ignoring it.
   - DO NOT echo the snapshot to the user. The user does not need a status
     table on every action. (Exception: pure status queries.)

E. Save the scene
   For ANY mutating action in step C (enable / disable / configure that
   actually changed scene state), invoke the host's built-in Save Scene
   capability (NOT a PICO MCP tool — Unity MCP already exposes Save Scene
   for the active scene). This persists the XR Origin + block edits so the
   project survives a reload.
   - Skip for status-only flows.
   - Skip if step C returned `already_present` (nothing changed to save).
   - If the host does not expose a Save Scene tool, add one trailing line
     to the checklist: "⚠ Scene not saved — please save manually (⌘S / Ctrl+S)."
```

## Domain-reload settle loop

Enter this loop only when the result crosses the authoritative reload boundary
in SKILL.md §4.1:

- a `pico_xr_package` `add` / `remove` / `update` / `import_sample` returns
  `status=ok`; or
- Spatial Mesh / Plane / Hand `enable` returns `status=skipped`,
  `data.recompiling=true`, and identifies one of the documented first-enable
  import transitions.

Do not infer a reload from `enable`, `configure`, or `disable` alone. VST,
Controller, Locomotion, and Grab do not reload for those actions, and a normal
`status=ok` feature result proceeds directly to internal verification. Waiting
there adds latency and contradicts the feature-specific workflow.

When the result does cross the boundary, wait for the Unity Editor to finish
recompiling before issuing the next MCP call. Otherwise the bridge will be
momentarily offline and the next call can fail.

```
poll_pico_xr_status_until_ready(max_retries=10, interval_seconds=3):
    for i in 1..max_retries:
        try:
            r = call_mcp("pico_xr_status", {})
        except (tool_not_found, timeout, network_error):
            sleep(interval_seconds)
            continue                       # bridge mid-reload, wait
        if r.status == "ok":
            return ok                      # Editor back online
        sleep(interval_seconds)
    return timeout                         # 30s elapsed; ask user to inspect
                                           # Unity Console for compile errors
```

Tuning:

- Default `max_retries=10, interval_seconds=3` → up to 30s wait. Acceptable
  for fresh package installs.
- For an `import_sample` that copies large assets (e.g. XRI Starter Assets),
  bump to `max_retries=20`.
- If the loop times out, do NOT retry the original action automatically.
  Tell the user the install kicked off but the Editor did not return; they
  should check the Unity Console.
- Observed timings (for calibration only, your project may differ):
  `package add` ~12s, `import_sample` (Starter Assets) ~6s.
