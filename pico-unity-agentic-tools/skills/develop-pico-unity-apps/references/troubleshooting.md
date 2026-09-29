# Troubleshooting Guide

## Contents

- Evidence collection
- Decision tree
- High-risk configuration combinations
- Common symptoms
- Logging and performance
- Report template

## Evidence Collection

Save the following information before making changes:

- Full Unity version.
- PICO Unity SDK, OpenXR Plugin, XRI, XR Hands, AR Foundation, and URP versions.
- Development mode, target device, and PICO OS version.
- Build Target, Scripting Backend, Architecture, and Minimum/Target API.
- Graphics API order, Render Mode, Color Space, and URP/HDR/MSAA/Post Processing settings.
- Portal screenshots or configuration state and failed Project Validation items.
- Minimal reproduction steps and the first failure timestamp.
- Unity Console, Editor.log, Android build log, and `adb logcat`.

Do not capture only the last exception. Preserve the first error and its surrounding context.

## Decision Tree

### Compilation Fails

1. Check legacy namespaces: `Unity.XR.PXR` and `Unity.XR.OpenXR.Features.PICOSupport`.
2. Check whether Runtime code references an `.Editor` namespace.
3. Check asmdef platforms and Version Defines.
4. Check whether old packages remain or duplicate types exist.
5. Check whether script errors are blocking SpatialAdapter package import.
6. Restore compilation before running Portal or Package Importer again.

### Build Fails

1. Run Project Validation.
2. Confirm Android, IL2CPP, ARM64, and API 29+.
3. Check Custom Manifest/Gradle files and third-party plugin merges.
4. Check keystore and alias configuration, but never print passwords.
5. Check Minify; the PICO XR documentation snapshot reports that enabling Minify can cause crashes.
6. Check current known issues for Unity 2022 Development Builds.

### APK Starts with a Black Screen or Stalls During Loading

1. Read the first native, Java, or Unity error in `adb logcat`.
2. Confirm that the Provider is unique and matches the target mode.
3. Check XR Origin, Main Camera, Audio Listener, and `PXR_Manager`.
4. Check Activity, orientation, PICO metadata, and manifest merge.
5. Check the graphics API against the device and Unity versions.
6. Check Proguard configuration for Release builds.
7. For Unity 6 + URP + OpenGL + Multi-pass + MSAA, change at least one condition.

### Head or Controller Tracking Does Not Work

1. Check application focus, tracking origin, and whether Input Actions are enabled.
2. Check the Controller Interaction Profile and left/right bindings.
3. Check whether both old and new Tracked Pose Driver components exist.
4. Check focus restoration after Home or Quick Menu.
5. Check device connection, Developer Mode, and the selected Run Device.
6. Reproduce in a minimal XRI or OpenXR sample to separate SDK and product issues.

### Hand, Eye, or Body Tracking Returns No Data

1. Query device capabilities; do not assume every PICO device supports the feature.
2. Check Portal/Feature settings, Interaction Profiles, and manifest permissions.
3. Check device feature switches and calibration.
4. Confirm that the Provider is Running.
5. Check whether it restarts after focus loss or pause.
6. Check package versions and PICO OS.

### VST or Passthrough Does Not Display

1. Disable Main Camera HDR on Unity 6.
2. Check camera background alpha, clear flags, and URP post-processing.
3. Check the Passthrough/OpenXR Feature.
4. Check the OpenXR Plugin version; the documentation snapshot reports issues in 1.16.x and later.
5. For the OpenXR 1.16.x workaround, evaluate importing XR Composition Layers and adding the required component.
6. Check camera and spatial-data permissions.

### FFR or ETFR Does Not Work

1. Confirm whether the current mode is FFR or ETFR; they are mutually exclusive.
2. For ETFR, query eye-tracking support and confirm calibration and permissions.
3. PICO XR ETFR Project Validation may require OpenGLES3 as the first Graphics API.
4. The OpenXR documentation snapshot states that ETFR supports OpenGL only and subsampling supports Vulkan only.
5. FFR with OpenXR and OpenGL may require Multi-pass.
6. With URP, disable HDR, post-processing, and renderer features that create intermediate textures.
7. Inspect support, enable, level, result, and eye-texture recreation fields in logs.

### PICO Spatial Crashes or Content Does Not Synchronize

1. Do not instantiate GameObjects or Prefabs in `Awake()`; move creation to `Start()`.
2. Re-export after reordering siblings in the scene hierarchy; clean the project `temp/` directory according to the known issue.
3. Do not change Collider types at runtime.
4. Check whether the component is in the Spatial support matrix.
5. Use SpatialAdapter synchronization APIs for dynamic materials and textures.
6. Check whether Spatial Camera is Constrained or Unconstrained and whether the feature requires Full or Shared Space.
7. Use only supported Shader Graph nodes and complete Spatial bundle export.

## High-Risk Configuration Combinations

| Combination                                                          | Risk / Handling                                                                                |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| PICO XR + Unity 2022 Development Build                               | The snapshot reports crashes; verify whether the current SDK/Unity versions contain a fix      |
| Unity 6 + URP + OpenGL + Multi-pass + MSAA                           | Eye buffer may not render; change at least one condition                                       |
| Vulkan + URP + HDR                                                   | Underlay/VST or OpenXR rendering may fail; disable HDR                                         |
| URP + SSAO                                                           | Frame rate drops and memory/GPU usage rises; disable SSAO                                      |
| FFR + URP intermediate texture/post-processing                       | FFR may fail; reduce intermediate-texture paths                                                |
| AppSW + Content Protection                                           | Jitter and ghosting; do not enable both                                                        |
| Late Latching + Overlay/Underlay                                     | Layer jitter or rendering errors; do not enable both                                           |
| Super Resolution + Subsampling                                       | Project Validation conflict; choose one                                                        |
| Sharpening + Subsampling                                             | Project Validation conflict; choose one                                                        |
| OpenXR Plugin 1.10.0 + `eyeTextureResolutionScale`                   | Possible crash; upgrade to 1.11.0                                                              |
| OpenXR Plugin > 1.8.2 + Subsampling                                  | The snapshot reports that it does not work; pin or disable                                     |
| OpenXR Plugin 1.16.x+ + Passthrough                                  | VST may fail; verify the workaround                                                            |
| OpenGLES + Multiview + Composition Layer + XRI Starter/Hands samples | May crash on specific system versions; change graphics API, Render Mode, or sample combination |
| PICO 4 series + Unity 6 + Vulkan                                     | The documentation recommends Unity 2022 LTS or earlier for better compatibility                |

## Common Symptoms

### App Does Not Appear in the Library

- Look under Unknown Source.
- Check for `android.intent.category.LAUNCHER` in the manifest.
- Check whether a third-party SDK changed the launcher intent during manifest merge.

### Copyright Verification Failed / Illegal Signature

- Confirm that the App ID, signing certificate, and developer-console application configuration match.
- Do not use a debug keystore as a release certificate.
- Validate User Entitlement Check configuration and the signed-in account.

### No Network

- Check for `android.permission.INTERNET` in the manifest.
- Check `ACCESS_NETWORK_STATE` and the runtime network.
- Distinguish DNS/TLS failures, server errors, and permission issues.

### Scene Follows the HMD After Opening Quick Menu

Unity OpenXR known-issue path:

- Check `Tracked Pose Driver (Input System)` on Main Camera.
- The documented workaround replaces it with the legacy Input System `Tracked Pose Driver`.
- Validate the change in a minimal sample first and record its effect on XRI input.

### Composition Layer Is Vertically Mirrored or Has Incorrect Alpha

- Android Surface has a known vertical-mirroring issue through Unity XR Composition Layers.
- Overlay or Underlay may render incorrectly when alpha is 0.
- Do not flip the image twice in application code; record the texture source and UV transformation.

## Logging and Performance

### Logging

Windows PowerShell example:

```powershell
adb devices
adb logcat -c
adb logcat Unity:D PxrUnity:D AndroidRuntime:E *:S
```

If PowerShell expands `*:S` incorrectly, quote each argument:

```powershell
adb logcat "Unity:D" "PxrUnity:D" "AndroidRuntime:E" "*:S"
```

When collecting logs from an installed build, record the package name, device serial, PICO OS version, and reproduction time.

### Performance

1. Confirm the target refresh rate and stable frame rate.
2. Use Metrics HUD or XR Profiling Toolkit to identify CPU or GPU bounds.
3. Use Unity Profiler for scripts, rendering, GC, and physics.
4. Use Graphics Probe or Snapdragon Profiler for GPU stages.
5. Use RenderDoc for PICO or Frame Debugger for draw calls, overdraw, attachments, and layers.
6. Change one variable at a time: Graphics API, Render Mode, MSAA, FFR/ETFR, or viewport scale.
7. Report averages, P95/P99, dropped frames, and thermal/frequency state instead of one frame.

## Report Template

```text
Symptom:
First failing stage: compile / build / startup / feature / performance

Environment:
- Unity:
- PICO Unity SDK:
- Mode:
- Device / PICO OS:
- OpenXR / XRI / URP:
- Graphics API / Render Mode:

Minimal reproduction:
1.
2.
3.

Evidence:
- Project Validation:
- Editor.log:
- build log:
- adb logcat:

Ruled out:
-

Root cause:

Fix:

Regression risk:

Validation:
```
