# Play-to-PICO in SpatialAdapter mode

Use this workflow when the developer asks to preview the current SpatialAdapter
Unity project on a PICO physical device or in PICO Emulator, run Play-to-PICO,
or configure its wired/wireless connection. An explanation or status request remains read-only.

## Default preview intent

For confirmed `mode=picospatial`, an intent to run the current Unity app on a
PICO physical device or in an Emulator, or inspect its effect selects
Play-to-PICO by default. Only an explicit
application packaging or APK request selects the build workflow. The intent may
come from the request or existing context; naming Play-to-PICO, play-2-pico or
this skill is not required. Do not ask the user to choose preview versus APK
when this default applies.

| Request in a confirmed picospatial project                           | Route                                        |
| -------------------------------------------------------------------- | -------------------------------------------- |
| Run it on a PICO physical device and inspect the result              | Play-to-PICO                                 |
| Run it in the emulator and inspect the result                        | Play-to-PICO                                 |
| The changes are ready; preview them in the emulator                  | Play-to-PICO                                 |
| Run it — previous context targets Emulator preview                   | Play-to-PICO                                 |
| Do not package the app or produce an APK; preview it in the emulator | Play-to-PICO                                 |
| Build an APK and install it in the emulator for testing              | Explicit application build and install       |
| Install and launch this existing APK                                 | Existing APK operation; no application build |
| Explain emulator preview without running anything                    | Read-only explanation                        |
| Start only the emulator without running the project                  | Emulator management                          |

An APK mentioned as existing input or a negated request does not imply building
the Unity application. SpatialAdapterServer.apk installation is a preview
dependency; it does not authorize building the Unity application. Missing
Play-to-PICO tools or SDK capability produce a capability error; do not silently
fall back to application packaging. Clarify missing/conflicting mode evidence
before selecting this branch.

## Mode and capability gate

1. Compare `.pico-cli/config.json` mode, installed packages and the request.
   SpatialAdapter mode is `picospatial`; conflicting evidence requires a mode
   decision before any mutation. Do not switch the SDK mode automatically.
2. Discover the actual tool schema. `required_tools = {pico_xr_play_to_pico}`;
   `missing_tools = required_tools - visible_tools`. Report every missing tool
   and stop before the first mutation. Do not infer readiness from another tool.
3. Call `pico_xr_play_to_pico(action=status)`. Inspect
   `spatialAdapterAvailable`, `spatialAdapterEnabled` and the current operation.
   A missing SDK capability is not permission to install or upgrade the SDK.
4. This branch does not require a PICO/OpenXR loader or XR Origin. Do not call
   `pico_xr_vst`, create an XR rig, disable cameras, or resolve XR block packages.

## Start and continue

Call `pico_xr_play_to_pico(action=start, connection=wired)` for the default
transport. Optional parameters, after verifying their schema, are
`deviceSerial` and `nodePath`; wireless also accepts `hostIp`. `nodePath` is the
Node.js executable.

The MCP package owns the deterministic sequence:

1. Read `adb devices -l`. Only entries whose state is exactly `device` are
   selectable. The MCP does not install or start an Emulator.
2. If no device is online, `start` returns `errorCode=no_adb_device` before an
   operation is created. Tell the user that no usable ADB device is connected
   and ask them to connect a PICO physical device or start/connect PICO
   Emulator, then stop. Do not install an Emulator, retry indefinitely, or fall
   back to an application build.
3. If more than one device is online and `deviceSerial` was omitted, `start`
   returns `stage=device_selection_required` and `data.devices`. Do not choose
   a device yourself:
   - Prefer the host's user-question selection UI when it is available and can
     represent the returned candidates. Show each device's `displayName` and
     exact `serial`.
   - If no selection UI is available, send one numbered list in chat and wait
     for one user reply. Accept either the number or exact serial.
   - Resolve the answer to one returned serial, then retry `start` once with
     `deviceSerial=<selected serial>`. Do not create or poll an operation before
     the user selects a device.
4. A single online device is selected automatically. An explicit serial must
   still be present and online when `start` runs; otherwise report
   `device_not_found` or `device_not_ready`.
5. Verify PICO/SpaceOS identity and `sys.boot_completed=1`. PICO physical
   devices and Emulators use the same flow; QEMU properties are not a
   prerequisite. Every device command uses the selected serial. A non-PICO
   device returns `device_not_pico` before Server or transport preparation.
6. For wireless only, check the computer and PICO device direct LAN subnet.
7. Query Android package `com.spatialadapter.server`. If absent, locate
   `Server/SpatialAdapterServer.apk` in the installed
   `com.bytedance.pico.spatialadapter` package and install it, then verify it.
   Existing installations are reused; never run the old `run.sh` that roots,
   uninstalls and reinstalls the Server.
8. Start SpatialAdapterServer and verify its process. Wired transport establishes
   and verifies only the selected device's `27182` forwarding rule. Do not remove
   unrelated forwarding rules.
9. Enter Play Mode through the MCP compatibility bridge, export once, connect
   once, and verify the Editor entered Play Mode. No SDK source edits or new
   SpatialAdapter compile-time dependency are required. Installed exporter and
   native runtime capabilities are still required to run the actual preview.

After a device is resolved, `status=pending` includes `operationId` and a stage
such as `validating_device`, `network_check`, `installing_server`,
`starting_server` or `entering_play`. The Host job keeps running and the MCP
resumes automatically when it completes. Do not issue another start. Poll
`pico_xr_play_to_pico(action=status, operationId=<returned ID>)` with bounded
waits and communicate progress. If the bridge temporarily disconnects during
Play Mode/domain reload, wait for reconnection and query the same operation.
An elapsed client wait is not a failed installation.

Report success only when `stage=running`, `connectionEstablished=true` and
`editorPlaying=true`. This confirms the native connection and Editor Play Mode;
it does not prove that every scene feature rendered correctly on the selected
PICO device. Visual interaction validation is a separate evidence step.

## Wired and wireless

- **Wired is default.** PICO physical devices and Emulators use ADB forwarding
  to `127.0.0.1:27182`; no LAN, Wi-Fi, subnet or network gateway check is needed.
- **Wireless is explicit.** Call
  `pico_xr_play_to_pico(action=start, connection=wireless, hostIp=<PICO device LAN IPv4>)`.
  The address must match an interface of the selected PICO device. Both IPs and
  real prefixes must agree on a direct subnet, with no routed gateway/NAT. Never compare just the
  first three IP octets. `network_not_same_lan` is terminal; do not fall back to
  wired automatically. Missing network facts produce
  `network_check_unavailable`. A same-subnet connection may still fail because
  of device isolation/firewall and is reported as a connection error.
- Typical NAT-based Emulator networking does not meet the wireless prerequisite.
  Explain the failure and let the developer select wired or a direct LAN setup.

## Stop and failure

Use `pico_xr_play_to_pico(action=stop, operationId=<returned ID>)` to cancel an
Server/transport preparation or end this Play session. Wait for cancellation to
finish if the result is pending. Stop restores SDK Play callbacks and temporary
export assets and removes only forwarding created by this operation. It does
not uninstall Server or manage Emulator lifecycle.

Relay a terminal `errorCode` and its concrete message. Use the returned
`logFile` for Server startup/install diagnosis. Do not retry Server installation
indefinitely, clear an AVD, root a device, change SDK mode or patch SDK scripts
as recovery.
`sdk_bridge_unsupported` means the installed SDK lacks the compatibility
signatures; report the missing signature rather than inventing a successful
preview. No scene save is needed unless this workflow included authorized
scene changes.

## Reference

The MCP package implements orchestration; the installed SDK supplies scene
export and native client functionality.
