---
name: spatialadapter-runtime-overview
description: Use when starting with Spatial Adapter, PICO Spatial, or Unity Spatial runtime APIs, choosing a Spatial Adapter topic skill, or reviewing Unity-facing surfaces.
license: 'Apache-2.0'
---

# SpatialAdapter Runtime Overview

## Overview

Use this skill as the discovery entry point for the Spatial Adapter runtime package. It summarizes the high-level Unity-facing APIs, explains when to prefer them over low-level native bridge calls, and points to the more specific package skills for runtime core, camera and windowing, input, and component APIs.

## Compatibility and Scope

Confirm PICO Spatial / Unity Spatial mode from `.pico-cli/config.json` when available and from installed packages and scene components. If evidence conflicts with the request, ask before switching modes. Verify `ByteDance.PICO.SpatialAdapter` types and signatures against the installed package; do not substitute `ByteDance.PICO.Spatial` names from another SDK snapshot. API discovery is read-only and does not require an Editor connection. Use a narrower skill directly when the topic is already known.

## Trigger Keywords

- `Spatial Adapter`
- `PICO Spatial`
- `Unity Spatial`
- `SpatialAdapterRuntime`
- `SpatialCamera`
- `Spatial Input`

## When to Use

- Use when you need a starting point for Spatial Adapter runtime APIs and do not yet know which topic skill is the right one.
- Use when comparing runtime, camera, input, or component APIs before choosing a topic. Once the topic is known, use its specific skill directly.
- Use when deciding whether to use a high-level Unity component workflow or a low-level `public static extern` runtime call.
- Use when you want the package-level return conventions and agent notes before diving into a narrower API area.

## Quick Reference

- Start with Unity-facing APIs first:
  - `SpatialAdapterRuntime.Initialize()`
  - `SpatialCamera`
  - `SpatialAdapterNativeText`
  - `SpatialAdapterVideoComponent`
  - `SurfaceTextureVideoComponent`
  - `SpatialInputSupport`
  - `SpatialAdapterRuntime.SyncMesh()`
  - `SpatialAdapterRuntime.RegisterDynamicTexture()`
- Treat most `public static extern` methods on `SpatialAdapterRuntime` as low-level native bridge calls.
- `SpatialAdapterRuntime.Instance` must exist before most runtime-driven registration works.
- Many component property writes mark objects dirty and synchronize on a later frame instead of pushing immediately.
- `SpatialCamera.CurrentConfiguration` falls back to `SpatialCamera.DefaultConfiguration` when no explicit configuration is assigned.

## Related Skills

- [pico-unity-spatial](../pico-unity-spatial/SKILL.md): general Spatial setup, space selection, and feature routing.
- [spatialadapter-scene-setup](../spatialadapter-scene-setup/SKILL.md): inspect or create the active scene's `SpatialCamera`.
- [spatialadapter-spatial-camera-focus](../spatialadapter-spatial-camera-focus/SKILL.md): keep a moving target inside camera bounds.
- [spatialadapter-runtime-core-api](../spatialadapter-runtime-core-api/SKILL.md): initialization, scene graph, resources, mesh sync, dynamic textures, manager state, DTOs.
- [spatialadapter-camera-window-api](../spatialadapter-camera-window-api/SKILL.md): `SpatialCamera`, spatial window lifecycle, modes, dimensions, metadata.
- [spatialadapter-input-api](../spatialadapter-input-api/SKILL.md): `SpatialInputSupport`, `SpatialInputDevice`, interaction state, touch mapping.
- [spatialadapter-components-api](../spatialadapter-components-api/SKILL.md): native text, video, surface-texture video, hover, shadow, collision, canvas sorting.

## Reference

Read [reference.md](reference.md) for the original package-level overview, common return conventions, file map, and important agent notes.

## Common Mistakes

- Starting from low-level native bridge calls when a Unity-facing component or wrapper already exists.
- Assuming `bool`, `int`, and `IntPtr` return values follow generic conventions instead of the package-specific rules documented here.
- Expecting immediate synchronization after every property write on runtime-backed components.
