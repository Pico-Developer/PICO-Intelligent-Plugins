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
       If block is `controller`:
         (No extra package install — PICO controller prefabs ship with the
          PICO SDK already in the project. The C# layer will report
          `error` with a clear message if the prefabs are missing; relay it
          verbatim and ask the user to install/update the PICO SDK.)
       If block is `hand`:
         (No extra package install — PICO hand prefabs (HandLeft/HandRight)
          ship with the PICO SDK already in the project, and the PICO-native
          hand path needs no Unity XR Hands package. The C# layer will report
          `error` with a clear message if the prefabs are missing; relay it
          verbatim and ask the user to install/update the PICO SDK.
          Enable also wires the mounted hands into the same
          XRInputModalityManager the controller block uses, so a connected
          controller natively auto-hides the hand models — no extra step and
          no dependency to resolve here.
          Hand does NOT trigger a domain reload — no settle loop needed.)

C. Perform the action
   call pico_xr_<block>(action=<verb>, ...params)
   Interpret result by `status`:
     - ok               → relay summary
     - already_present  → relay summary + "no change made"
     - skipped          → relay summary + warning, ask user how to proceed
     - error            → relay summary + error, ask user how to proceed

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

Every time a `pico_xr_package` mutating action returns `status=ok`, you MUST
wait for the Unity Editor to finish recompiling before issuing the next MCP
call. Otherwise the bridge will be momentarily offline and your next call
will fail.

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
