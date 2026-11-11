---
name: spatialadapter-runtime-core-api
description: Use for SpatialAdapterRuntime initialization, resource registration, scene synchronization, mesh sync, dynamic textures, manager state, or runtime DTOs. Window lifecycle belongs to spatialadapter-camera-window-api; API exploration belongs to runtime-overview. Platform names alone do not activate this skill.
license: 'Apache-2.0'
---

# SpatialAdapter Runtime Core API

## When NOT to Use

- High-level API overview or topic comparison — use `spatialadapter-runtime-overview`
- Scene setup or camera configuration — use `spatialadapter-scene-setup`
- Input or interaction handling — use `spatialadapter-input-api`

## Overview

Use this skill when you need the core `SpatialAdapterRuntime` API surface in the Spatial Adapter runtime package. Prefer the Unity-facing entry points first and treat low-level native bridge calls as implementation details unless you are extending the runtime itself.

## Compatibility and Scope

Confirm Spatial mode from the saved `mode`, installed package, and scene evidence before implementation; ask if they conflict. Verify `ByteDance.PICO.SpatialAdapter` signatures and native return contracts against the installed package. API explanations are read-only. Before runtime execution or scene changes, verify the running Editor and the required tool; if unavailable, report the blocker rather than claiming execution. Wait for successful compilation after script writes and save the intended scene after authorized scene changes.

## Trigger Keywords

- `SpatialAdapterRuntime`
- `SyncMesh`
- `SpatialAdapterResourceData`
- runtime initialization, resource registration, or dynamic texture synchronization

Platform names alone do not activate this skill. Require a concrete runtime API topic. Use [spatialadapter-camera-window-api](../spatialadapter-camera-window-api/SKILL.md) for window lifecycle, even when its low-level methods are on `SpatialAdapterRuntime`; use [spatialadapter-runtime-overview](../spatialadapter-runtime-overview/SKILL.md) for API exploration or comparison.

## When to Use

- Use when initializing the Spatial Adapter session with `SpatialAdapterRuntime.Initialize()`.
- Use when registering or synchronizing scene objects, resources, prefabs, or runtime managers.
- Use when sending mesh data with `SyncMesh()` or working with `VertexAttributeFlags`.
- Use when registering dynamic textures or binding them to materials.
- Use when you need the meaning of public DTOs and structs such as `Transform3D`, `SpatialAdapterSceneData`, `SpatialAdapterResourceData`, `MeshData`, or `Collider`-adjacent runtime payloads.

## Quick Reference

- `SpatialAdapterRuntime.Instance`: singleton runtime component. Must exist before most runtime-driven registration works.
- `Initialize()`: starts the session, input support, post-frame callback, and synchronization flow.
- `ClearAllManagers()`: clears cached manager state and queued synchronization work.
- `OpenSpatialCamera()`, `SyncSpatialCamera()`, `CloseSpatialCamera()`: queue camera window operations through the runtime.
- `SyncMesh(MeshFilter, VertexAttributeFlags)`: serializes selected vertex streams and sends them to the backend.
- `RegisterDynamicTexture(Texture2D)`: returns a backend texture asset ID, or `-1` on failure.
- `UpdateMaterialDynamicTexture(Material, int, string)`: associates a backend texture with a backend material. The current implementation ignores `parameterName`.

## Reference

Read [reference.md](reference.md) for the full public API map, return conventions, fields, helper types, and payload structs.

## Common Mistakes

- Calling runtime registration or sync APIs before `SpatialAdapterRuntime.Instance` exists.
- Applying native status-code conventions to resource IDs. Status-code calls generally use `0` for success, but `RegisterDynamicTexture()` returns an asset ID and uses `-1` for failure.
- Assuming backend work happens immediately. Several operations are queued and applied later.
- Expecting `UpdateMaterialDynamicTexture()` to honor `parameterName`. The current implementation routes by material instance ID only.
