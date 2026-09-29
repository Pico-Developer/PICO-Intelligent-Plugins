---
name: pico-unity-spatial
description: |
  Guide Unity PICO Spatial app setup and feature routing.
  Invoke for Unity Spatial, Unity PICO Spatial, Shared Space, Full Space,
  spatial UI, Play-to-PICO, or XR Hands and AR Foundation in PICO Spatial.
  Prefer narrower spatialadapter skills for concrete runtime API work.
  PICO OS 6 alone does not establish Spatial mode.
license: 'Apache-2.0'
---

# pico-unity-spatial

## Purpose

Use this skill for Unity projects targeting **PICO Spatial** rather than the PICO XR building-block path.

This is a routing and implementation-guidance skill. It does not call `pico_xr_*` MCP tools by default because those tools belong to the Unity PICO XR workflow.

## When To Use

Use this skill when the user says any of:

- `Unity Spatial`
- `PICO Spatial`
- `PICO OS 6` together with explicit Spatial intent or Spatial project evidence
- `Shared Space` or `Full Space`
- `Unity spatial app`
- `spatial UI`
- Play-to-PICO
- `XR Hands` in a PICO Spatial app
- `AR Foundation` in a PICO Spatial app

For explicit PICO XR feature orchestration, use the PICO XR workflow instead. A shared feature term such as hands or spatial mesh does not by itself authorize switching a configured Spatial project to another mode.

For Unity OpenXR or cross-mode auditing, migration, builds, and diagnostics, use [develop-pico-unity-apps](../develop-pico-unity-apps/SKILL.md). For concrete Spatial Adapter APIs, use the topic skills below instead of the general setup flow.

## Default Route

1. Confirm the project is a Unity project and targets Android for PICO devices.
2. Confirm the intended mode is `PICO Spatial`, not `PICO XR` or generic `Unity OpenXR`.
3. Read the saved `mode` from `.pico-cli/config.json` when available and compare it with the user's request, installed packages, and scene components. If they conflict, ask before switching modes or changing the scene.
4. If the Unity workflow is ambiguous, ask whether the user targets PICO Spatial / Spatial Adapter, PICO XR, or Unity OpenXR before switching assumptions.
5. Verify namespaces and APIs against the installed package. The Spatial Adapter topic skills describe `ByteDance.PICO.SpatialAdapter`; do not mechanically substitute `ByteDance.PICO.Spatial` from another SDK snapshot.
6. Keep API questions and read-only validation read-only. For scene changes, verify the running Editor and an available scene-editing tool; report missing capabilities instead of inventing calls or claiming execution.
7. Guide the user through PICO Spatial setup and validation before feature work.

## Setup Guidance

For a new Unity PICO Spatial project:

1. Install Unity with `Android Build Support`, `Android SDK & NDK Tools`, and `OpenJDK`.
2. Prefer a clean `Universal 3D` project unless project-local docs say otherwise.
3. Import the PICO Unity SDK package from disk.
4. Open `PICO Unity SDK Portal`.
5. Select `PICO Spatial` and apply the setup actions supported by the installed SDK Portal; use `Apply All` when available, otherwise apply the required items individually.
6. Run `Setup Project` / `Confirm Project Setup`.
7. Run `XR Plug-in Management > Project Validation` and fix required items.
8. Use Play-to-PICO first for iteration, then device/emulator build checks as needed.

## Feature Routing

Use PICO Spatial guidance for:

- Spatial app setup and validation.
- Unity UI in spatial contexts.
- `Shared Space` / `Full Space` decisions.
- `XR Hands` only when the mode and space support it.
- AR Foundation only for the subset supported by PICO Spatial.
- Play-to-PICO debugging.

### Spatial Adapter Topic Skills

| Task                                                   | Skill                                                                                  |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| Choose a runtime API topic                             | [spatialadapter-runtime-overview](../spatialadapter-runtime-overview/SKILL.md)         |
| Inspect or create SpatialCamera                        | [spatialadapter-scene-setup](../spatialadapter-scene-setup/SKILL.md)                   |
| Configure spatial windows, camera mode, or dimensions  | [spatialadapter-camera-window-api](../spatialadapter-camera-window-api/SKILL.md)       |
| Keep a moving target inside camera bounds              | [spatialadapter-spatial-camera-focus](../spatialadapter-spatial-camera-focus/SKILL.md) |
| Spatial Input, colliders, or manipulation              | [spatialadapter-input-api](../spatialadapter-input-api/SKILL.md)                       |
| Native text, video, hover, shadows, or canvas sorting  | [spatialadapter-components-api](../spatialadapter-components-api/SKILL.md)             |
| Runtime initialization, mesh sync, or dynamic textures | [spatialadapter-runtime-core-api](../spatialadapter-runtime-core-api/SKILL.md)         |

For concrete Spatial Input implementation, hand off immediately to
[spatialadapter-input-api](../spatialadapter-input-api/SKILL.md). That skill owns target
selection, click / tap / pinch handling, colliders, EnhancedTouch mapping, dragging, and
manipulation. Do not continue those tasks in this broad setup and routing skill.

## Key Checks

- Keep target platform on Android.
- For Unity UI, use World Space canvas patterns when the UI must exist in spatial context.
- Verify mode support before promising plane detection, environment depth, light estimation, or full XR Interaction Toolkit behavior.
- Do not assume PICO Spatial is a full replacement for PICO XR.

## Risks

- Do not route PICO Spatial requests into `pico_xr_*` MCP tools by default.
- Do not present Live Preview as the default PICO Spatial workflow; prefer Play-to-PICO.
- Do not auto-install or switch SDK modes without asking when the project already appears configured.
- If user needs high-performance immersive XR, advanced passthrough/VST, locomotion, or PICO XR-specific building blocks, ask whether they want to switch to the PICO XR skill path.
