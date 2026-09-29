---
name: pico-unity-buildingblocks
description: >-
  Orchestrate PICO XR building blocks (XR Origin, VST/Passthrough, Controller
  models, Locomotion, Spatial Mesh, Hand tracking, Grab & drag, and future
  blocks) in a Unity Editor via the `pico_xr_*` MCP tools. Handles MCP
  pre-check, dependency resolution (auto-installing packages, importing
  samples), domain-reload waits, enable/disable/configure actions, and scene
  saving.

  Trigger when the user wants to enable / disable / configure / query any
  PICO XR feature — passthrough, controllers, locomotion, spatial mesh, hand
  tracking / virtual hands / XR Hands / xr-hands / xrhands, object grab & drag
  / pick-up / grabbable, etc. — or create an
  XR Origin / XR rig.
license: 'Apache-2.0'
---

# pico-unity-buildingblocks

## Prerequisites

- Unity Editor running with PICO MCP Extensions installed.
- The 9 `pico_xr_*` tools (`pico_xr_vst`, `pico_xr_controller`,
  `pico_xr_locomotion`, `pico_xr_spatial_mesh`, `pico_xr_plane`, `pico_xr_hand`,
  `pico_xr_grab`, `pico_xr_package`, `pico_xr_status`) are enabled in `Edit > Project Settings > AI > Unity MCP`.
- The AI client is connected to the Unity MCP bridge.
- **An XR runtime provider is enabled in `Project Settings > XR Plug-in
Management` (Android tab).** These blocks run on EITHER PICO runtime —
  PICO-native (`PICO` loader) or PICO OpenXR (`OpenXR` loader + the PICO OpenXR
  feature group). The building-block code auto-selects the right path at
  compile time (`#if ENABLE_PICO_OPENXR_SDK` vs `ENABLE_PICO_XR_SDK`), and the
  MR blocks (VST / Spatial Mesh) additionally auto-enable the required OpenXR
  _feature_ asset (Passthrough / PICO Spatial Mesh) when running on the OpenXR
  path. But **the loader/provider itself is a user prerequisite** — this skill
  does NOT install or toggle XR Plug-in Management loaders. If no PICO loader is
  enabled (neither define is set), STOP and guide the user to enable one; see
  §3.1.

## 1. What this skill orchestrates

Eight PICO XR feature blocks exposed as MCP tools:

| Block        | Tool                   | Actions                                            |
| ------------ | ---------------------- | -------------------------------------------------- |
| VST          | `pico_xr_vst`          | `enable` / `disable` / `status`                    |
| Controller   | `pico_xr_controller`   | `enable` / `disable` / `status`                    |
| Locomotion   | `pico_xr_locomotion`   | `enable` / `disable` / `configure` / `status`      |
| Spatial Mesh | `pico_xr_spatial_mesh` | `enable` / `disable` / `status`                    |
| Plane        | `pico_xr_plane`        | `enable` / `disable` / `status`                    |
| Hand         | `pico_xr_hand`         | `enable` / `disable` / `status`                    |
| Grab         | `pico_xr_grab`         | `enable` / `disable` / `status` / `make_grabbable` |
| Aggregate    | `pico_xr_status`       | (no params) snapshot of all seven blocks           |

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
> `pico_xr_locomotion`, `pico_xr_spatial_mesh`, `pico_xr_plane`, `pico_xr_hand`,
> `pico_xr_grab`, `pico_xr_package`, `pico_xr_status`) in my MCP tool list. The Unity MCP bridge is either not
> running or the PICO MCP Extensions are not exposed.
>
> Please:
>
> 1. Confirm the **Unity Editor** is running and the project is open.
> 2. Open **Edit > Project Settings > AI > Unity MCP** and confirm the
>    bridge status is **Running**.
> 3. In the **Tools** list, confirm the 9 `pico_xr_*` tools are listed and
>    enabled.
> 4. **Restart this AI client** so it re-discovers the MCP tools.
>
> Once you've done that, ask me again.

> NOTE: Some MCP clients refresh their tool registry only on session restart.
> Asking the user to restart the IDE/CLI is part of the fix, not just Unity.

## 3. Dependency matrix

The blocks have these prerequisites. Resolve from the **outside in**:

| Block            | Requires                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **XR Origin**    | Package `com.unity.xr.interaction.toolkit` + Sample `Starter Assets`                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **VST**          | XR Origin present + a PICO runtime enabled (§3.1). On the OpenXR path the C# layer auto-enables the `PassthroughFeature` OpenXR feature.                                                                                                                                                                                                                                                                                                                                                                                                     |
| **Controller**   | XR Origin present + PICO controller-model prefabs in PICO SDK                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **Locomotion**   | XR Origin present (Locomotion node is a child of XR Origin)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Spatial Mesh** | XR Origin present + **VST enabled** (passthrough required by PICO) + a PICO runtime enabled (§3.1). On the OpenXR path the C# layer auto-enables the `PICOSpatialMesh` OpenXR feature and reads the mesh from the OpenXR subsystem.                                                                                                                                                                                                                                                                                                          |
| **Plane**        | XR Origin present + **VST enabled** (passthrough required by PICO) + the **PICO-native** runtime enabled (§3.1). **PICO-native ONLY** — there is no plane-detection OpenXR feature, so on the PICO OpenXR runtime `pico_xr_plane(action=enable)` returns `error`; STOP and guide the user to the PICO-native loader.                                                                                                                                                                                                                         |
| **Hand**         | XR Origin present + runtime-specific models: **PICO-native** uses PICO SDK `HandLeft` / `HandRight`; **OpenXR** requires package `com.unity.xr.hands` + sample `HandVisualizer`. Both paths also require the XRI `Hands Interaction Demo` sample for the hand-interactor rig. Resolve these dependencies before `enable`; every new package/sample import has its own settle boundary. The C# layer flips OpenXR HandTracking + HandInteractionProfile (pinch→select) when OpenXR is active. Hand-only enable does NOT surface a controller. |
| **Grab**         | XR Origin present + XRI package + `Starter Assets` sample (interaction broker + interactable). Decoupled from hand/controller — needs an enabled input block (`pico_xr_controller` / `pico_xr_hand`) to supply the interactor. `make_grabbable` needs XRI only.                                                                                                                                                                                                                                                                              |

Implementation note: the `pico_xr_*` MCP tools themselves contain an
`EnsureXROrigin` call internally, so they will not crash if XR Origin is
missing — but you should still resolve it explicitly so the user sees what
happened, and so the agent can detect "Starter Assets sample missing" before
the C# layer logs an error.

### 3.1 XR runtime provider (PICO-native vs PICO OpenXR) — user prerequisite

Every block runs on ONE of two PICO runtimes, chosen by the loader enabled in
`Project Settings > XR Plug-in Management` (Android):

| Runtime     | XR Plug-in Management loader           | Compile define           |
| ----------- | -------------------------------------- | ------------------------ |
| PICO-native | **PICO**                               | `ENABLE_PICO_XR_SDK`     |
| PICO OpenXR | **OpenXR** + PICO OpenXR feature group | `ENABLE_PICO_OPENXR_SDK` |

What is automatic vs. what the user must do:

- **Automatic (handled by the MCP C# layer).** The block code branches at
  compile time on the define, so it picks the correct runtime path with no
  agent action. On the OpenXR path, the MR blocks also auto-enable the required
  OpenXR **feature** asset on the Android build target (VST → `PassthroughFeature`;
  Spatial Mesh → `PICOSpatialMesh`). **Plane detection is PICO-native only** — it
  has no OpenXR feature and does NOT run on the OpenXR path (on that runtime
  `pico_xr_plane(action=enable)` returns `error`), mirroring the PICO SDK's own building
  blocks.
- **User prerequisite (this skill does NOT do it).** Enabling the **loader /
  provider** in XR Plug-in Management is a project-setup step outside these MCP
  tools' scope — exactly like the PICO SDK itself. This skill NEVER installs a
  provider package nor toggles an XR Plug-in Management loader. If neither PICO
  define is set (no PICO loader enabled), a block returns `error`/`skipped`
  with a message that the driver type never appeared; STOP, relay it, and guide
  the user with the template below. Do NOT auto-install or retry.

#### Provider-missing guidance (verbatim, adjust language to the user)

> ⚠ **No PICO XR runtime is enabled**
>
> These building blocks need a PICO runtime active in
> **Project Settings > XR Plug-in Management** (Android tab). Please enable
> **one** of:
>
> - **PICO** (PICO-native runtime), or
> - **OpenXR** — then, under _OpenXR > Feature Groups_, enable the **PICO**
>   feature group.
>
> Then re-open the scene (let the Editor recompile) and ask me again. I don't
> change XR Plug-in Management providers for you — that's a project-setup step.

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

### 4.1 Reload boundary (authoritative)

Choose whether to settle from the MCP result, not merely from whether the
requested action mutates state:

| Result                                                                                                                                          | Settle before the next MCP call?                    |
| ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `pico_xr_package` `add` / `remove` / `update` / `import_sample` returns `status=ok`                                                             | **Yes**                                             |
| Spatial Mesh / Plane / Hand `enable` returns `status=skipped`, `data.recompiling=true`, and names one of the four documented import transitions | **Yes**, once per distinct transition               |
| The same first-enable transition repeats after its one settle/retry                                                                             | **No** — stop and report no progress                |
| VST / Controller / Locomotion / Grab `enable` / `configure` / `disable`                                                                         | **No**                                              |
| Any feature mutation returns a normal `status=ok` without a recompile transition                                                                | **No** — continue directly to internal verification |
| `status`, package `list` / `info` / `list_samples`, or `status=already_present`                                                                 | **No**                                              |

The four allowed first-enable transitions are
`spatial_mesh:SpatialMeshManager`, `plane:PlaneDetectionManager`,
`hand:HandVisualizer`, and `hand:Hands Interaction Demo`. Do not insert a
settle delay after every feature mutation: scene edits can be verified
immediately unless the result explicitly reports one of these reloads.

## On-demand references

| File                                | When to read                                                                |
| ----------------------------------- | --------------------------------------------------------------------------- |
| `references/orchestration.md`       | Before performing any block action; when a domain reload occurs             |
| `references/blocks/xr-origin.md`    | When creating / setting up XR Origin                                        |
| `references/blocks/vst.md`          | When enabling / disabling VST / passthrough                                 |
| `references/blocks/controller.md`   | When adding / removing controller models                                    |
| `references/blocks/locomotion.md`   | When enabling / configuring / disabling locomotion                          |
| `references/blocks/spatial-mesh.md` | When enabling / disabling spatial mesh                                      |
| `references/blocks/plane.md`        | When enabling / disabling plane detection                                   |
| `references/blocks/hand.md`         | When enabling / disabling hand tracking / virtual hands                     |
| `references/blocks/grab.md`         | When enabling / disabling object grab & drag, or making an object grabbable |

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
- If an action returns `error`, STOP, relay the error, suggest the obvious next
  step, and wait. Do NOT retry blindly.
- If an action returns `skipped`, classify it by action, runtime, and workflow context:
  - **Transitional first-enable recompile** — only
    `pico_xr_spatial_mesh(action=enable)`, `pico_xr_plane(action=enable)`, or
    `pico_xr_hand(action=enable)`, when `data.recompiling == true` and
    `detail`/`warning` identifies a documented driver/sample import. Track the
    transition by block plus imported driver/sample and run ONE bounded
    post-write settle loop before retrying the SAME action. Each distinct
    transition may advance once; the same transition repeating means no progress
    and must stop. OpenXR Hand may expose two distinct stages (`HandVisualizer`,
    then `Hands Interaction Demo`) when dependencies were not pre-resolved. The
    only valid transition keys are `spatial_mesh:SpatialMeshManager`,
    `plane:PlaneDetectionManager`, `hand:HandVisualizer`, and
    `hand:Hands Interaction Demo`; derive the key from the called tool plus the
    exact imported asset/sample named in `detail`/`warning`, not from `summary`.
  - **Transitional dependency resolution** — only a package/sample dependency
    step within the current, already-authorized `enable` / `configure` flow.
    Follow the pico-unity-package-manager §4.1-§4.3 fallback, including its
    settle boundary and single retry. A read-only package query does not
    authorize an install.
  - For every other `skipped`, and whenever the same transition is still
    `skipped` after its one retry, STOP, relay the warning, suggest the next
    step, and wait.

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
- DO NOT install or toggle an XR Plug-in Management **loader/provider**
  (PICO or OpenXR) or its provider package. The active runtime is a user
  project-setup prerequisite (§3.1). If no PICO runtime is enabled, STOP and
  use the provider-missing guidance template — never auto-fix it. (The MR
  blocks DO auto-enable the OpenXR _feature_ assets — Passthrough / Spatial
  Mesh — but that is the C# layer's job, not the agent's, and only happens once
  a loader is already active.)
- DO NOT call `pico_xr_locomotion(action=configure)` without parsing the user's
  intent first. The default preset is `Default`; if the user said "all",
  pass `All`; if they said "off", they probably mean
  `pico_xr_locomotion(action=disable)`.
- DO NOT echo raw JSON to the user. Always summarise.
- DO NOT echo `pico_xr_status` data after a single-block mutating action.
  Step D is for internal verification only. The user asked for one thing —
  reply about that one thing.
- DO NOT forget Save Scene at the end of mutating flows. Without it, the
  XR Origin edits vanish on Editor reload. Use the host's built-in Save
  Scene tool (Unity MCP exposes one) — no PICO MCP tool needed for this.
- DO NOT add a `pico_xr_scene` tool. Save Scene already lives in the host
  MCP surface; duplicating it in PICO MCP would be redundant.
