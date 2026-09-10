---
name: pico-unity-spatial
description: |
  Guide Unity PICO Spatial app setup and feature routing.
  Invoke when users mention Unity Spatial, Unity PICO Spatial, PICO OS 6,
  Shared Space, Full Space, Spatial Input, spatial UI, Play-to-PICO, XR Hands
  in PICO Spatial, or AR Foundation in PICO Spatial.
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
- `PICO OS 6`
- `Shared Space` or `Full Space`
- `Unity spatial app`
- `spatial UI`
- `Spatial Input`
- Play-to-PICO
- `XR Hands` in a PICO Spatial app
- `AR Foundation` in a PICO Spatial app

If the user says `PICO XR`, `PXR_Manager`, `XR Origin`, `VST`, `passthrough`, `locomotion`, controller models, spatial mesh, or asks to call `pico_xr_*` tools, use `pico-unity-buildingblocks` instead.

If the user says `OpenXR Plugin`, `PICO XR Feature Group`, `Interaction Profiles`, or cross-platform OpenXR, route to the Unity OpenXR guidance path and use package-management help only when package changes are needed.

## Default Route

1. Confirm the project is a Unity project and targets Android for PICO devices.
2. Confirm the intended mode is `PICO Spatial`, not `PICO XR` or generic `Unity OpenXR`.
3. Use explicit user wording and project evidence to keep routing on the PICO Spatial path.
4. If the Unity workflow is ambiguous, ask whether the user targets PICO Spatial / Spatial Adapter, PICO XR, or Unity OpenXR before switching assumptions.
5. Guide the user through PICO Spatial setup and validation before feature work.

## Setup Guidance

For a new Unity PICO Spatial project:

1. Install Unity with `Android Build Support`, `Android SDK & NDK Tools`, and `OpenJDK`.
2. Prefer a clean `Universal 3D` project unless project-local docs say otherwise.
3. Import the PICO Unity SDK package from disk.
4. Open `PICO Unity SDK Portal`.
5. Select `PICO Spatial` and click `Apply All`.
6. Run `Setup Project` / `Confirm Project Setup`.
7. Run `XR Plug-in Management > Project Validation` and fix required items.
8. Use Play-to-PICO first for iteration, then device/emulator build checks as needed.

## Feature Routing

Use PICO Spatial guidance for:

- Spatial app setup and validation.
- Unity UI in spatial contexts.
- Spatial Input, target selection, clicking, dragging, or touch-like interaction.
- `Shared Space` / `Full Space` decisions.
- `XR Hands` only when the mode and space support it.
- AR Foundation only for the subset supported by PICO Spatial.
- Play-to-PICO debugging.

## Key Checks

- Keep target platform on Android.
- Use Unity's new Input System when spatial input is required.
- For Unity UI, use World Space canvas patterns when the UI must exist in spatial context.
- Verify mode support before promising plane detection, environment depth, light estimation, or full XR Interaction Toolkit behavior.
- Do not assume PICO Spatial is a full replacement for PICO XR.

## Risks

- Do not route PICO Spatial requests into `pico_xr_*` MCP tools by default.
- Do not present Live Preview as the default PICO Spatial workflow; prefer Play-to-PICO.
- Do not auto-install or switch SDK modes without asking when the project already appears configured.
- If user needs high-performance immersive XR, advanced passthrough/VST, locomotion, or PICO XR-specific building blocks, ask whether they want to switch to the PICO XR skill path.
