---
name: spatialadapter-runtime-overview
description: Use when starting with Spatial Adapter, PICO Spatial, or Unity Spatial runtime APIs, choosing a Spatial Adapter topic skill, or reviewing Unity-facing surfaces.
license: 'Apache-2.0'
---

# SpatialAdapter Runtime Overview

## Overview

Use this skill as the discovery entry point for the Spatial Adapter runtime package. It summarizes the high-level Unity-facing APIs, explains when to prefer them over low-level native bridge calls, and points to the more specific package skills for runtime core, camera and windowing, input, and component APIs.

## Trigger Keywords

- `Spatial Adapter`
- `PICO Spatial`
- `Unity Spatial`
- `SpatialAdapterRuntime`
- `SpatialCamera`
- `Spatial Input`

## When to Use

- Use when you need a starting point for Spatial Adapter runtime APIs and do not yet know which topic skill is the right one.
- Use when working with `SpatialAdapterRuntime.Initialize()`, `SpatialCamera`, native text, video, surface-texture video, input, mesh sync, or dynamic textures.
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

- `spatialadapter-runtime-core-api`: initialization, scene graph, resources, mesh sync, dynamic textures, manager state, DTOs.
- `spatialadapter-camera-window-api`: `SpatialCamera`, spatial window lifecycle, modes, dimensions, metadata.
- `spatialadapter-input-api`: `SpatialInputSupport`, `SpatialInputDevice`, interaction state, touch mapping.
- `spatialadapter-components-api`: native text, video, surface-texture video, hover, shadow, collision, canvas sorting.

## Reference

Read `reference.md` in this folder for the original package-level overview, common return conventions, file map, and important agent notes.

## Common Mistakes

- Starting from low-level native bridge calls when a Unity-facing component or wrapper already exists.
- Assuming `bool`, `int`, and `IntPtr` return values follow generic conventions instead of the package-specific rules documented here.
- Expecting immediate synchronization after every property write on runtime-backed components.
