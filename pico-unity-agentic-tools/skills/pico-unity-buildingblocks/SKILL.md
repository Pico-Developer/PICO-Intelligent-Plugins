---
name: pico-unity-buildingblocks
description: |-
  Orchestrate PICO XR building blocks (XR Origin, VST/Passthrough, Controller
  models, Locomotion, Spatial Mesh, Hand tracking, and future blocks) in a
  Unity Editor via the `pico_xr_*` MCP tools. Handles MCP pre-check, dependency
  resolution (auto-installing packages, importing samples), domain-reload waits,
  enable/disable/configure actions, and scene saving.

  Trigger when the user wants to enable / disable / configure / query any
  PICO XR feature — passthrough, controllers, locomotion, spatial mesh, hand
  tracking / virtual hands / XR Hands / xr-hands / xrhands, etc. — or create an
  XR Origin / XR rig.
  Also trigger on requests to enable/disable/configure PICO XR features (passthrough, controllers, locomotion, spatial mesh, hand tracking/virtual hands/XR Hands/xr-hands/xrhands, etc.) or to create an XR Origin.
license: 'Apache-2.0'
---

# pico-unity-buildingblocks

## Prerequisites

- Unity Editor running with PICO MCP Extensions installed.
- The 7 `pico_xr_*` tools (`pico_xr_vst`, `pico_xr_controller`,
  `pico_xr_locomotion`, `pico_xr_spatial_mesh`, `pico_xr_hand`,
  `pico_xr_package`, `pico_xr_status`) are enabled in `Edit > Project Settings > AI > Unity MCP`.
- The AI client is connected to the Unity MCP bridge.

## 1. What this skill orchestrates

Six PICO XR feature blocks exposed as MCP tools:

| Block        | Tool                   | Actions                                       |
| ------------ | ---------------------- | --------------------------------------------- |
| VST          | `pico_xr_vst`          | `enable` / `disable` / `status`               |
| Controller   | `pico_xr_controller`   | `enable` / `disable` / `status`               |
| Locomotion   | `pico_xr_locomotion`   | `enable` / `disable` / `configure` / `status` |
| Spatial Mesh | `pico_xr_spatial_mesh` | `enable` / `disable` / `status`               |
| Hand         | `pico_xr_hand`         | `enable` / `disable` / `status`               |
| Aggregate    | `pico_xr_status`       | (no params) snapshot of all five blocks       |

All blocks share the same XR Origin in the scene. This skill ensures the
**XR Origin and its package/sample dependencies are in place** before any
block-level action runs, then performs the action, then reports back.

> **Single-active-camera invariant.** The agent XR Origin ships its own Main
> Camera. To avoid a multi-camera render conflict (which notably breaks VST
> passthrough), any time a block ensures the XR Origin the C# layer collapses
> the scene to **one** active camera: it switches off every _other_ enabled
> scene camera by setting `Camera.enabled = false` (and its paired
> `AudioListener`). This is **non-destructive and reversible** — foreign camera
> GameObjects are never disabled or destroyed, and every flip is `Undo`-able
> (Ctrl+Z) or restorable via `PICO MCP > Camera > Restore Foreign Cameras`.
> `pico_xr_status` reports the current camera picture under `data.camera`
> (`activeCameras`, `managedDisabled`, `single`).

## 2. Step 0 — MCP connection pre-check (MANDATORY)

Before ANY `pico_xr_*` call, verify that the AI IDE/CLI actually sees the
Unity MCP tools:

```
1. In your own tool registry, list MCP tools whose name starts with `pico_xr_`.
2. If you find ≥ 1 such tool → continue with Step 1.
3. If you find 0 → STOP and reply to the user with the warning below; do NOT
   proceed and do NOT attempt to call any tool.
```

### Warning template (verbatim, adjust language to the user)

> ⚠ **Unity MCP connection issue**
>
> I cannot find the PICO XR MCP tools (`pico_xr_vst`, `pico_xr_controller`,
> `pico_xr_locomotion`, `pico_xr_spatial_mesh`, `pico_xr_hand`,
> `pico_xr_package`, `pico_xr_status`) in my MCP tool list. The Unity MCP bridge is either not
> running or the PICO MCP Extensions are not exposed.
>
> Please:
>
> 1. Confirm the **Unity Editor** is running and the project is open.
> 2. Open **Edit > Project Settings > AI > Unity MCP** and confirm the
>    bridge status is **Running**.
> 3. In the **Tools** list, confirm the 7 `pico_xr_*` tools are listed and
>    enabled.
> 4. **Restart this AI client** so it re-discovers the MCP tools.
>
> Once you've done that, ask me again.

> NOTE: Some MCP clients refresh their tool registry only on session restart.
> Asking the user to restart the IDE/CLI is part of the fix, not just Unity.

## 3. Dependency matrix

The blocks have these prerequisites. Resolve from the **outside in**:

| Block            | Requires                                                               |
| ---------------- | ---------------------------------------------------------------------- |
| **XR Origin**    | Package `com.unity.xr.interaction.toolkit` + Sample `Starter Assets`   |
| **VST**          | XR Origin present                                                      |
| **Controller**   | XR Origin present + PICO controller-model prefabs in PICO SDK          |
| **Locomotion**   | XR Origin present (Locomotion node is a child of XR Origin)            |
| **Spatial Mesh** | XR Origin present + **VST enabled** (passthrough required by PICO)     |
| **Hand**         | XR Origin present + PICO hand prefabs (HandLeft/HandRight) in PICO SDK |

Implementation note: the `pico_xr_*` MCP tools themselves contain an
`EnsureXROrigin` call internally, so they will not crash if XR Origin is
missing — but you should still resolve it explicitly so the user sees what
happened, and so the agent can detect "Starter Assets sample missing" before
the C# layer logs an error.

## 4. The block-action orchestration loop (summary)

For ANY request "enable / configure / disable / query block B":

```
A. Snapshot         — call pico_xr_status(); if not ok, STOP.
B. Resolve deps     — for ENABLE/CONFIGURE only (skip for DISABLE/STATUS):
                      B.1 XR Origin (XRI package + Starter Assets sample)
                      B.2 Block-specific extras (e.g. Spatial Mesh needs VST)
C. Perform action   — call pico_xr_<block>(action=<verb>, ...params)
D. Internal verify  — call pico_xr_status() silently to detect silent failure
E. Save scene       — host Save Scene tool (skip for status-only / no-change flows)
```

**Full step-by-step details and the domain-reload settle loop live in
[`references/orchestration.md`](references/orchestration.md).** Read it before
performing any block action or when a domain reload occurs.

## On-demand references

| File                                | When to read                                                    |
| ----------------------------------- | --------------------------------------------------------------- |
| `references/orchestration.md`       | Before performing any block action; when a domain reload occurs |
| `references/blocks/xr-origin.md`    | When creating / setting up XR Origin                            |
| `references/blocks/vst.md`          | When enabling / disabling VST / passthrough                     |
| `references/blocks/controller.md`   | When adding / removing controller models                        |
| `references/blocks/locomotion.md`   | When enabling / configuring / disabling locomotion              |
| `references/blocks/spatial-mesh.md` | When enabling / disabling spatial mesh                          |
| `references/blocks/hand.md`         | When enabling / disabling hand tracking / virtual hands         |

## 8. Reply style

- Open with one line stating what you are about to do.
- Stream intermediate progress as a checklist (✓ / … / ✗) so the user can
  see auto-installs happening.
- **Close with the checklist only.** Do NOT echo a post-action status
  table — the user doesn't need to see the full block matrix on every
  action; they only asked for the one thing they asked for.
- **Exception**: when the user's request IS a status query
  (e.g. "what's enabled?", "show PICO XR status"), the table IS the answer.
- For mutating flows, the last checklist line must reflect Save Scene:
  `✓ Scene saved` (or `⚠ Scene not saved — please save manually` when the
  host has no Save Scene tool).
- If you hit a `skipped` or `error` status anywhere, STOP, tell the user
  what blocked the workflow, suggest the obvious next step, and wait for
  their reply. Do NOT silently retry.

## 9. Anti-patterns (DO NOT)

- DO NOT skip Step 0 (MCP pre-check). It costs nothing and saves the user
  a confusing failure trace.
- DO NOT call `pico_xr_*` tools when Step 0 found 0 tools — there is
  nothing to call.
- DO NOT chain a mutating `pico_xr_package` call directly with another
  `pico_xr_*` call without the settle loop. The Editor will be reloading.
- DO NOT resolve dependencies for `disable` / `status` actions. They are
  read-only or destructive and should not auto-install packages.
- DO NOT auto-install the PICO SDK. If a Controller prefab is missing,
  ask the user — installing the PICO SDK is outside the scope of these
  MCP tools.
- DO NOT call `pico_xr_locomotion(configure)` without parsing the user's
  intent first. The default preset is `Default`; if the user said "all",
  pass `All`; if they said "off", they probably mean `pico_xr_locomotion(disable)`.
- DO NOT echo raw JSON to the user. Always summarise.
- DO NOT echo `pico_xr_status` data after a single-block mutating action.
  Step D is for internal verification only. The user asked for one thing —
  reply about that one thing.
- DO NOT forget Save Scene at the end of mutating flows. Without it, the
  XR Origin edits vanish on Editor reload. Use the host's built-in Save
  Scene tool (Unity MCP exposes one) — no PICO MCP tool needed for this.
- DO NOT add a `pico_xr_scene` tool. Save Scene already lives in the host
  MCP surface; duplicating it in PICO MCP would be redundant.
