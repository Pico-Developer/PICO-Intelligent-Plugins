# Development Mode Selection

## Contents

- Quick decision guide
- Capability differences
- Migration and mode-mixing boundaries
- Decision output template

## Quick Decision Guide

### Select PICO XR

Prefer PICO XR when any of these conditions apply:

- The product targets PICO only and needs the broadest PICO-native capability set.
- The app requires Face Tracking, Object Tracking, Shared Spatial Anchor, Plane Detection, SecureMR, Environment Depth, or Light Estimation.
- The app requires Adaptive Resolution, Super Resolution, Sharpening, PICO Building Blocks, or Live Preview.
- The app is a high-performance immersive game or experience with complex 3D, physics, effects, custom rendering, or deep device integration.

Use `ByteDance.PICO.XR` as the primary namespace. PICO XR is not an alias for Unity OpenXR mode.

### Select Unity OpenXR

Prefer Unity OpenXR when all of these conditions apply:

- Cross-platform deployment matters more than PICO-exclusive capabilities.
- The required capabilities are within the Unity OpenXR support subset.
- The team accepts platform abstraction through OpenXR Features, Interaction Profiles, and Unity XR packages.

This mode supports controllers, hands, eye tracking, body tracking, haptics, VST, spatial anchors, scene capture, spatial mesh, composition layers, FFR/ETFR, AppSW, and related features, but it does not cover the full PICO XR feature set.

Use `ByteDance.PICO.OpenXR` at runtime and `ByteDance.PICO.OpenXR.Editor` for Editor code. `Unity.XR.OpenXR.Features.PICOSupport` is a legacy migration source and should not be used for new implementations.

### Select PICO Spatial

Prefer PICO Spatial when these conditions apply:

- The experience is UI-centric and embeds only lightweight 3D content.
- The app must coexist or collaborate with other PICO OS 6 applications.
- The goal is to extend an Android or mobile application into a spatial experience.
- The product accepts Spatial Engine component, rendering, shader, and lifecycle boundaries.

Use `ByteDance.PICO.Spatial` and Spatial Camera. Do not reuse code that assumes `PXR_Manager`, a traditional Main Camera, or an OpenXR Loader.

Constrained Spatial Camera mode maps to Shared Space. Unconstrained mode maps to Full Space. Some capabilities are available only in Full Space.

## Capability Differences

The following table summarizes key differences from the SDK 6.0.0 documentation snapshot. See `feature-index.md` for the full navigation index.

| Capability                                          | PICO XR   | Unity OpenXR  | PICO Spatial                                          |
| --------------------------------------------------- | --------- | ------------- | ----------------------------------------------------- |
| XR Interaction Toolkit                              | Supported | Supported     | Full/Shared Space                                     |
| Hand tracking                                       | Supported | Supported     | Full Space                                            |
| Eye tracking                                        | Supported | Supported     | Not supported                                         |
| Face tracking                                       | Supported | Not supported | Not supported                                         |
| Body tracking                                       | Supported | Supported     | Not supported                                         |
| Object Tracking                                     | Supported | Not supported | Not supported                                         |
| VST                                                 | Supported | Supported     | Not supported                                         |
| Spatial Anchor                                      | Supported | Supported     | Not directly; AR Foundation Anchor in Full Space only |
| Shared Spatial Anchor                               | Supported | Not supported | Not supported                                         |
| Scene Capture / Spatial Mesh                        | Supported | Supported     | AR Foundation variants in Full Space only             |
| Plane Detection                                     | Supported | Not supported | Not supported                                         |
| SecureMR / Environment Depth / Light Estimation     | Supported | Not supported | Not supported                                         |
| FFR / ETFR / AppSW / Composition Layer              | Supported | Supported     | Not supported                                         |
| Adaptive Resolution / Super Resolution / Sharpening | Supported | Not supported | Not supported                                         |
| Building Blocks / Live Preview                      | Supported | Not supported | Not supported                                         |
| Platform / Enterprise Services                      | Supported | Supported     | Full/Shared Space                                     |

## Migration and Mode-Mixing Boundaries

- A project may support multiple build targets through business-level abstractions, but do not enable competing XR Providers in the same Player build.
- Isolate platform code in separate assemblies or adapters, selected through compile symbols and dependency boundaries.
- Similar type names do not imply API equivalence. Verify parameters, lifecycle, coordinate spaces, and return values.
- When migrating from the legacy PICO Unity Integration SDK, remove the old package before migrating `Unity.XR.PXR`.
- When migrating from the legacy PICO Unity OpenXR SDK, separate Runtime and Editor namespaces.
- Before switching from PICO XR to Unity OpenXR, create a capability gap table. Do not wait until runtime to discover missing features.
- Before converting a standard Android or Unity project to PICO Spatial, check component support, dynamic material and texture synchronization, supported Shader Graph nodes, and the `Awake()` restrictions.

## Decision Output Template

Use this structure:

```text
Recommended mode:
Evidence:
- Product target
- Required capabilities
- Cross-platform requirements
- Current project dependencies

Why not PICO XR:
Why not Unity OpenXR:
Why not PICO Spatial:

Version and device prerequisites:
Accepted downgrade or risk:
```
