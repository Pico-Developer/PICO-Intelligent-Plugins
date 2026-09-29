---
name: develop-pico-unity-apps
description: Develop, configure, migrate, debug, and optimize XR apps and spatial apps with PICO Unity SDK 6.0.0. Use when TRAE CLI needs to inspect a Unity project for PICO integration; choose among PICO XR, Unity OpenXR, and PICO Spatial modes; create an immersive XR or spatial scene; implement controllers, hands, eye tracking, body tracking, passthrough, anchors, spatial mesh, foveated rendering, compositor layers, haptics, spatial cameras, spatial input, or spatial UI; migrate legacy PICO namespaces; configure Android builds and permissions; diagnose build, rendering, tracking, device, SpatialAdapter, or performance problems; or prepare a PICO app for on-device validation. Prefer pico-unity-spatial for Spatial setup and the specific spatialadapter skills for concrete Spatial Adapter APIs.
license: 'Apache-2.0'
---

# Develop XR and Spatial Apps with PICO Unity SDK

## Routing Boundary

Use this skill for project-wide audits, mode selection, migration, Android builds, and broader diagnostics. For PICO Spatial setup and feature routing, prefer [pico-unity-spatial](../pico-unity-spatial/SKILL.md). For concrete Spatial Adapter scene, camera, input, component, or runtime APIs, select the narrower skill from [spatialadapter-runtime-overview](../spatialadapter-runtime-overview/SKILL.md) instead of loading multiple overlapping workflows.

## Core Principles

- Inspect project facts before changing the project. Do not infer the Unity version, SDK mode, render pipeline, or enabled capabilities from the request alone.
- Treat PICO as an Android-based XR target. Distinguish Unity Editor simulation, streaming preview, PICO Emulator, and validation on physical devices.
- Select the development mode before selecting APIs. Do not mix namespaces or configuration paths from PICO XR, Unity OpenXR, and PICO Spatial in one implementation.
- Prefer SDK Portal, Project Validation, official samples, and Building Blocks. Build configurations manually only when those paths cannot meet the requirement.
- Treat device capabilities, system version, permissions, graphics API, and package versions as part of the feature contract. A capability matrix does not mean every device supports the feature.
- Cite the basis for version-sensitive conclusions. This skill is based on a PICO Unity SDK 6.0.0 documentation snapshot. If the project uses another version, check package documentation or current official documentation first.

## Workflow

### 1. Audit the Project

Run the read-only inventory script from the Unity project root:

```powershell
python "<skill-dir>\scripts\inspect_pico_unity_project.py" .
```

Use `--json` for machine-readable output. Read [inspect_pico_unity_project.py](scripts/inspect_pico_unity_project.py) to understand the inspection scope.

Confirm at least:

- The Unity version in `ProjectSettings/ProjectVersion.txt`.
- XR, Input System, AR Foundation, XR Hands, XRI, and URP dependencies in `Packages/manifest.json` and local package paths.
- Current mode evidence, legacy namespaces, and existing `XR Origin`, `PXR_Manager`, Spatial Camera, or OpenXR Features.
- Android build target, IL2CPP/ARM64, minimum API, graphics API, render mode, color space, and URP/HDR/MSAA settings.
- Target device, PICO OS version, and required hardware such as eye-tracking cameras or Motion Trackers.

If the supplied directory is not a Unity project, locate the root that contains `Assets`, `Packages`, and `ProjectSettings`.

### 2. Select the Development Mode

Read [mode-selection.md](references/mode-selection.md), then state the selected mode and rationale:

- **PICO XR**: Prefer PICO-specific capabilities, the broadest feature coverage, and high-performance immersive experiences or games.
- **Unity OpenXR**: Prefer cross-platform deployment when the required capabilities fit its supported subset.
- **PICO Spatial**: Prefer UI-centric experiences, lightweight 3D, cross-application collaboration, or spatial extensions of mobile apps.

Default to PICO XR when the requirement includes Face Tracking, Object Tracking, Shared Spatial Anchor, Plane Detection, SecureMR, Environment Depth, Light Estimation, Adaptive Resolution, Super Resolution, Sharpening, Building Blocks, or Live Preview, unless the user accepts a capability downgrade.

Do not treat PICO Spatial as another XR Loader. It uses Spatial Camera and `ByteDance.PICO.Spatial`, with a distinct runtime, component synchronization model, and support boundary.

### 3. Establish a Minimal Working Baseline

Build and validate a minimal scene before adding product features:

1. Import PICO Unity SDK from the SDK's `XR/package.json`.
2. Select the mode in **PICO > Portal** and run **Apply All**; apply each item individually for PICO Spatial.
3. Open **Project Validation**, fix Required items, then evaluate Recommended and Optional items.
4. For PICO XR, import XR Interaction Toolkit 3.x Starter Assets and use Building Blocks for controller or hand setup.
5. For Unity OpenXR, import the required OpenXR Plugin samples and enable only the required PICO OpenXR Features.
6. For PICO Spatial, use Spatial Camera and remove assumptions that depend on a traditional XR Camera.
7. Switch to Android, build a feature-free APK, and validate startup, head tracking, and basic input on the target device or Emulator.

Read [implementation-guide.md](references/implementation-guide.md) for namespaces, scene structure, permissions, lifecycle, and validation requirements for each mode.

### 4. Implement the Feature

Follow this sequence: capability -> prerequisites -> Portal/Feature -> scene components -> permissions -> lifecycle -> device validation.

1. Check mode support and relevant topics in [feature-index.md](references/feature-index.md).
2. Search installed package API definitions and samples. Do not write type names from memory of an older SDK.
3. Wrap SDK calls behind a platform boundary so business logic does not directly depend on multiple mode APIs.
4. For asynchronous providers or tracking features, implement `Start/Stop`, status queries, permission denial, focus loss, and teardown.
5. Provide runtime authorization and fallback paths for sensitive capabilities such as eye, face, camera, microphone, and spatial data.
6. For ETFR, confirm that the device supports eye tracking. FFR and ETFR are mutually exclusive; do not describe FFR results as ETFR.
7. Do not silently modify a custom `AndroidManifest.xml`, Gradle files, keystore, or signing configuration. Explain the boundary between SDK-generated declarations and manual declarations first.

### 5. Validate

Validate from fastest to slowest:

1. Compile affected assemblies and clear Console compilation errors.
2. Run Project Validation. Do not hide actual dependencies with **Ignore build errors**.
3. Confirm exactly one XR Origin, Main Camera, and Audio Listener, or validate the applicable Spatial Camera rules.
4. Build an Android APK. For a PICO XR Development Build on Unity 2022, check current known issues first.
5. Collect startup and SDK logs with `adb logcat`, PICO Debugger, or PDC.
6. On a physical device, test permission denial, pause/resume, focus changes, recentering, controller disconnects, and unsupported-device paths.
7. Measure performance with Metrics HUD, XR Profiling Toolkit, Unity Profiler, or RenderDoc for PICO instead of relying on Editor FPS.

## Migration Rules

- Migrate the legacy PICO XR namespace `Unity.XR.PXR` to `ByteDance.PICO.XR`.
- Migrate the legacy OpenXR namespace `Unity.XR.OpenXR.Features.PICOSupport` to runtime `ByteDance.PICO.OpenXR` or Editor-only `ByteDance.PICO.OpenXR.Editor`.
- Use `ByteDance.PICO.Spatial` for PICO Spatial.
- When migrating the legacy Integration SDK, remove the old package, resolve compilation blockers, and then import the unified SDK. Add `ENABLE_PICO_XR_SDK` temporarily only when required for the transition.
- Do not perform a mechanical global replacement. Distinguish Runtime and Editor assemblies, API signature changes, serialized components, and prefab references.

## Troubleshooting Order

Read [troubleshooting.md](references/troubleshooting.md) and investigate by layer:

1. **Mode**: Verify that the current mode supports the feature.
2. **Version**: Verify compatibility among Unity, SDK, OpenXR, XRI, URP, and PICO OS.
3. **Configuration**: Check Portal, Project Validation, Features, graphics API, and render mode.
4. **Permissions**: Check manifest declarations, runtime authorization, Developer Mode, and device capabilities.
5. **Scene**: Check Origin, Camera, Manager, Interactor, and Provider lifecycle.
6. **Build**: Check Android, IL2CPP, ARM64, minimum API 29, signing, and Gradle.
7. **Runtime**: Use complete logs and reproduction steps to locate the first failure.

Do not start by deleting `Library`, reinstalling the SDK, or switching rendering backends. Preserve evidence and test one hypothesis at a time.

## Output Requirements

Always report:

- Current project facts: Unity version, SDK/packages, inferred mode, and evidence.
- Recommended mode and reasons for rejecting the other modes.
- Files to change, Unity Editor settings, and device-side prerequisites.
- Compatibility, permission, ABI/data-contract, and regression risks.
- Validation already performed, remaining device validation, and reproducible commands.
