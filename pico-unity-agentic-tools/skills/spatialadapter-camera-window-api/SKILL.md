---
name: spatialadapter-camera-window-api
description: Use when working with SpatialCamera in Spatial Adapter, PICO Spatial, or Unity Spatial scenes, spatial windows, camera modes, dimensions, or configuration.
license: 'Apache-2.0'
---

# SpatialAdapter Camera And Window API

## Overview

Use this skill when you need the public camera-facing APIs that create and control Spatial Adapter windows. It covers `SpatialCamera`, reusable `SpatialCameraConfiguration` assets, and the mode-specific metadata that gets sent to the host system.

## Compatibility and Scope

Confirm Spatial mode from the saved `mode`, installed package, and scene evidence before changing the scene; ask if they conflict. Verify `ByteDance.PICO.SpatialAdapter` APIs against the installed package. API explanations are read-only. Before scene changes, verify the running Editor and an available scene-editing tool; if unavailable, report the blocker and provide manual steps. Preserve Undo and save the intended scene after authorized changes. For camera creation use [scene setup](../spatialadapter-scene-setup/SKILL.md); for target following use [camera focus](../spatialadapter-spatial-camera-focus/SKILL.md).

## Trigger Keywords

- `Spatial Adapter`
- `PICO Spatial`
- `Unity Spatial`
- `SpatialCamera`
- `SpatialCameraConfiguration`
- `Spatial Window`

## When to Use

- Use when opening, closing, or checking the active spatial window with `SpatialCamera`.
- Use when choosing between `CameraMode.Constrained` and `CameraMode.Unconstrained`.
- Use when reading or assigning `OutputConfiguration`, `DefaultConfiguration`, or `CurrentConfiguration`.
- Use when calculating the backend root transform for a spatial window.
- Use when debugging window sizing, default config fallback, or platform metadata generated from a camera configuration.

## Quick Reference

- `SpatialCamera.Current`: the currently open spatial window, or `null` when none is open.
- `SpatialCamera.DefaultConfiguration`: fallback configuration sourced from `SpatialAdapterResourceData`.
- `CurrentConfiguration`: returns explicit `OutputConfiguration` first, then falls back to `DefaultConfiguration`.
- `OpenWindow()`: closes any existing spatial window and opens this one.
- `CloseWindow()`: closes this camera if it is the active spatial window.
- `GetRootTransform()`: computes the matrix used to mirror the camera into the backend.
- `SpatialCameraConfiguration.GetData()`: converts a configuration asset into the compact native payload.
- `SpatialCameraConfiguration.GetCustomMetaData()`: builds host metadata keys for constrained or unconstrained mode.

## Reference

Read [reference.md](reference.md) for the full API map, serialized fields, mode behavior, metadata keys, and configuration details.

## Common Mistakes

- Opening a camera without a valid configuration and assuming the runtime always has a usable default fallback.
- Choosing `Unconstrained` for a normal bounded window when `Constrained` is the intended mode.
- Treating `WindowOpen` as a separate state flag. It is effectively whether this instance matches `SpatialCamera.Current`.
