---
name: spatialadapter-components-api
description: Use when working with Spatial Adapter, PICO Spatial, or Unity Spatial runtime components such as native text, video, hover, grounding shadow, or collider payloads.
license: 'Apache-2.0'
---

# SpatialAdapter Components API

## Overview

Use this skill when you need the component-facing public APIs in the Spatial Adapter runtime package. It covers native text, native and surface-texture video, hover and grounding shadow markers, collision conversion payloads, and canvas sorting synchronization.

## Compatibility and Scope

Confirm Spatial mode from the saved `mode`, installed package, and scene evidence before changing components; ask if they conflict. Verify `ByteDance.PICO.SpatialAdapter` APIs against the installed package. API explanations are read-only. Before scene changes, verify the running Editor and an available scene-editing tool; if unavailable, report the blocker and provide manual steps. Reuse existing components, preserve Undo, and save the intended scene after authorized changes.

## Trigger Keywords

- `Spatial Adapter`
- `PICO Spatial`
- `Unity Spatial`
- `SpatialAdapterGroundingShadow`
- `SpatialAdapterNativeText`
- `SpatialAdapterVideoComponent`

## When to Use

- Use when configuring `SpatialAdapterNativeText` and its background, sizing, and justification fields.
- Use when driving playback through `SpatialAdapterVideoComponent`.
- Use when targeting backend-decoded video into a surface texture with `SurfaceTextureVideoComponent`.
- Use when enabling backend hover or grounding shadow behavior on synchronized entities.
- Use when converting Unity colliders or UI rects into backend `ColliderData`.
- Use when syncing canvas sorting data for backend UI ordering.

## Quick Reference

- `SpatialAdapterNativeText`: backend-rendered text component. Property writes mark the component dirty and synchronize later.
- `SpatialAdapterVideoComponent`: native video component with `Play()`, `Pause()`, `Resume()`, `Stop()`, and `PlaymodeNone()`.
- `SurfaceTextureVideoComponent`: sends decoded video into a backend texture resource and supports mono or stereo layout modes.
- `SpatialAdapterHoverEffect` and `SpatialAdapterGroundingShadow`: marker components that register and deregister with the runtime on enable or disable.
- `ColliderData`: backend collision payload with constructors for box, sphere, capsule, mesh, and UI rect transforms.
- `HierarchicalLayerSortingData`: tracks canvas sorting-layer changes and reports whether sync is needed.

## Grounding Shadow Setup

When adding `SpatialAdapterGroundingShadow` to an object:

- Add `SpatialAdapterGroundingShadow` only to a GameObject that has a `MeshRenderer` or `SkinnedMeshRenderer`.
- If the requested object does not have either renderer, search all of its children for GameObjects with a `MeshRenderer` or `SkinnedMeshRenderer` and add `SpatialAdapterGroundingShadow` to every matching child instead.
- Report which child objects received `SpatialAdapterGroundingShadow` when the requested object itself was not a valid renderable target.
- If neither the object nor any child has a `MeshRenderer` or `SkinnedMeshRenderer`, do not add `SpatialAdapterGroundingShadow`; report that no valid renderable target exists.
- Inspect the active Unity scene for the ground plane object. If none exists or multiple candidates are ambiguous, ask which object should act as the ground; do not create a plane or modify an arbitrary candidate.
- Check whether the ground plane already has a `SpatialAdapterGroundingShadow` component.
- If the ground plane does not have one, add `SpatialAdapterGroundingShadow` to the ground plane too, using the same renderer-target rule above.
- Do not add duplicate `SpatialAdapterGroundingShadow` components to any final renderable target or ground plane renderable target.

## Reference

Read [reference.md](reference.md) for full property lists, payload field definitions, playback modes, collider conversion rules, and canvas sorting behavior.

## Common Mistakes

- Expecting native text or video property writes to push immediately. These components usually mark themselves dirty and synchronize later.
- Assuming `BackgroundCornerRadius` uses the same public type as its backing field. The property accepts `int` even though storage is `float`.
- Forgetting that `SurfaceTextureVideoComponent` flip flags modify local transform scale, not the native payload directly.
- Assuming every Unity collider type is converted. Unsupported collider shapes are ignored by the helper.
- Adding `SpatialAdapterGroundingShadow` only to the visible object and forgetting to ensure the scene ground plane also has one.
- Adding `SpatialAdapterGroundingShadow` to an empty parent or container object that has no `MeshRenderer` or `SkinnedMeshRenderer`; add it to all renderable children instead.
