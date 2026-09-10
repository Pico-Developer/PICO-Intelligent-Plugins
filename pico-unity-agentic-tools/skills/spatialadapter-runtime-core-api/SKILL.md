---
name: spatialadapter-runtime-core-api
description: 'Use when working with SpatialAdapterRuntime core APIs in Spatial Adapter, PICO Spatial, or Unity Spatial scenes: initialization, resource registration, mesh sync, or textures.'
license: 'Apache-2.0'
---

# SpatialAdapter Runtime Core API

## Overview

Use this skill when you need the core `SpatialAdapterRuntime` API surface in the Spatial Adapter runtime package. Prefer the Unity-facing entry points first and treat low-level native bridge calls as implementation details unless you are extending the runtime itself.

## Trigger Keywords

- `Spatial Adapter`
- `PICO Spatial`
- `Unity Spatial`
- `SpatialAdapterRuntime`
- `SyncMesh`
- `SpatialAdapterResourceData`

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

Read `reference.md` in this folder for the full public API map, return conventions, fields, helper types, and payload structs.

## Common Mistakes

- Calling runtime registration or sync APIs before `SpatialAdapterRuntime.Instance` exists.
- Treating non-zero `int` return values as success. In this API, `0` generally means success.
- Assuming backend work happens immediately. Several operations are queued and applied later.
- Expecting `UpdateMaterialDynamicTexture()` to honor `parameterName`. The current implementation routes by material instance ID only.
