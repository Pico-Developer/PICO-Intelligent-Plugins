---
name: pico-unity-package-manager
description: >-
  Manage Unity Package Manager packages and samples for PICO XR through the
  Unity MCP `pico_xr_package` tool. Maps install, remove, update, query,
  list-samples, and import-sample intents to exact action tokens; waits for
  Unity compilation/domain reload after mutations; and supports
  `pico-unity-buildingblocks` dependency setup.

  Trigger when the user names a package identifier (for example,
  `com.unity.xr.hands`) or pairs an install/remove/update/query intent with a
  concrete package name. Also trigger for listing installed packages or
  versions and importing or listing named samples. Do not trigger for
  feature-level requests such as enabling hand tracking or passthrough; route
  those to `pico-unity-buildingblocks`. Requires a running Unity Editor with
  PICO MCP Extensions installed and the MCP client connected.
license: 'Apache-2.0'
---

# pico-unity-package-manager

## 1. Background

This skill is the **low-level package/sample subsystem** of the PICO Unity MCP
extension. It wraps a single MCP tool:

```
pico_xr_package(action, identifier?, packageName?, version?, sampleName?, overwrite?)
```

where `action` is one of:

| action          | parameters                                                             | purpose                                   |
| --------------- | ---------------------------------------------------------------------- | ----------------------------------------- |
| `list`          | —                                                                      | Snapshot of all installed packages        |
| `info`          | `packageName`                                                          | Is package X installed? At what version?  |
| `add`           | `identifier` (e.g. `com.unity.xr.hands` or `com.unity.xr.hands@1.5.0`) | Install / switch version                  |
| `remove`        | `packageName`                                                          | Uninstall                                 |
| `update`        | `packageName`, `version?` (explicit to change an installed package)    | Install missing / switch explicit version |
| `list_samples`  | `packageName`, `version?`                                              | Samples declared by the package           |
| `import_sample` | `packageName`, `sampleName`, `overwrite?`, `version?`                  | Copy a sample into Assets/Samples/…       |

The underlying C# layer is **idempotent**:

- Adding an already-installed package returns `status=already_present` (no-op).
- Removing a not-installed package returns `status=ok` (no-op).
- Importing an already-imported sample returns `status=already_present` (no-op).
- Importing a sample whose **package is not installed** returns
  `status=skipped` with a `warning` — DO NOT treat as failure; treat as
  "need to install the package first."

## 2. Result envelope

Every call returns a `PXR_MCP_Result`:

```json
{
  "status":  "ok" | "already_present" | "skipped" | "error",
  "summary": "human-readable one-liner",
  "warning": "set when status=skipped",
  "error":   "set when status=error",
  "data":    { ... raw Step 1 POCO ... }
}
```

When relaying outcomes to the user, echo the `summary`. When the status is
`skipped`, echo the `warning` and classify it by action and workflow context:

- An `info` pre-check inside an explicit install / "ensure installed" request
  may continue to `add` under §4.1. The same result from a read-only query means
  "not installed" and MUST NOT trigger a write.
- An `import_sample` whose warning says its package is not installed is
  **transitional** only when the user requested that import or the current
  building-block flow already authorized dependency resolution. Follow
  §4.2/§4.3 (auto-install + settle loop + one retry).
- For any other `skipped`, propose the obvious fix and ask the user to confirm.

## 3. Mandatory workflow: domain-reload-safe writes

Successful mutations from `add`, `remove`, `update`, and `import_sample`
trigger a Unity Editor recompile / domain reload. **After any of these calls
returns `status=ok`**, run the **post-write settle loop** before invoking any
other PICO MCP tool — otherwise the next tool call may fail because the MCP
bridge is temporarily down during the reload. `status=already_present` is a
no-op and does not need a settle loop.

### Post-write settle loop

```
poll_pico_xr_status_until_ready(max_retries=10, interval_seconds=3):
    for i in 1..max_retries:
        try:
            r = call_mcp("pico_xr_status", {})
        except (tool_not_found, timeout, network_error):
            # Bridge is most likely mid-reload; just wait.
            sleep(interval_seconds)
            continue

        if r.status == "ok":
            return ok                # Editor is back online
        sleep(interval_seconds)

    return timeout("Unity did not become ready within "
                   + (max_retries * interval_seconds) + "s; "
                   + "ask the user to check the Unity Console for compile errors.")
```

This is the **only** correct way to bridge a domain reload from an external
MCP client.

This section owns `pico_xr_package` results only. Do not generalize its
mutating-action rule to every `pico_xr_*` feature mutation. Feature tools use
the result-driven boundary in `pico-unity-buildingblocks` §4.1: a normal
`status=ok` feature result does not require settling, while a documented
first-enable `status=skipped`, `data.recompiling=true` import transition does.

### When to call it

| Action          | Settle required? |
| --------------- | ---------------- |
| `list`          | No (read-only)   |
| `info`          | No (read-only)   |
| `list_samples`  | No (read-only)   |
| `add`           | **Yes**          |
| `remove`        | **Yes**          |
| `update`        | **Yes**          |
| `import_sample` | **Yes**          |

## 4. Standard procedures

### 4.1 Install a package (idempotent)

```
1. Optional pre-check (only when user asked "make sure X is installed"):
     call pico_xr_package(action=info, packageName=X)
     - status=ok at desired version → tell user "already installed", STOP.
     - status=skipped (not installed) → continue.

2. call pico_xr_package(action=add, identifier=X[@version])
     - status=already_present → relay summary, STOP (no settle needed).
     - status=ok               → run post-write settle loop, then relay summary.
     - status=error            → relay summary + error, STOP and ask user.
```

### 4.2 Import a sample (idempotent)

```
1. call pico_xr_package(action=import_sample,
                         packageName=P, sampleName=S, overwrite=false)
     - status=already_present → relay summary, STOP.
     - status=skipped (warning="package P is not installed; ...")
         → fall back to 4.3 (auto-install then retry).
     - status=ok               → run post-write settle loop, then relay summary.
     - status=error            → relay summary + error, STOP and ask user.
```

### 4.3 Auto-install package then import sample

```
1. call pico_xr_package(action=add, identifier=P)
     - status=error            → STOP and ask user.
     - status=already_present  → relay summary, proceed directly to step 2 (no settle needed).
     - status=ok               → run post-write settle loop, then proceed to step 2.
2. call pico_xr_package(action=import_sample, packageName=P, sampleName=S)
     - status=already_present → relay summary, STOP.
     - status=ok              → run post-write settle loop, then relay summary.
     - status=skipped         → this is the one retry; relay summary + warning,
                                STOP and ask the user. Do NOT fall back to 4.3 again.
     - status=error           → relay summary + error, STOP and ask user.
```

### 4.4 Query

```
- "What packages are installed?"
    call pico_xr_package(action=list) → render `data.packages` as a table.

- "Is X installed?"
    call pico_xr_package(action=info, packageName=X) →
      status=ok       → "X is installed at version <data.version>."
      status=skipped  → "X is NOT installed."

- "What samples does X expose?"
    call pico_xr_package(action=list_samples, packageName=X) →
      render `data.samples` (displayName + imported flag) as a table.
```

### 4.5 Update or repair a package

```
1. For a registry package, call:
     pico_xr_package(action=update, packageName=P, version=V?)
     - To change an installed package, provide an explicit target `version`.
       Omitting `version` can install a missing package at the registry default,
       but an installed package may return `already_present`; that result does
       not prove it is the latest version.
     - status=already_present → relay summary, STOP (no settle needed).
     - status=ok              → run post-write settle loop, then relay summary.
     - status=skipped         → relay summary + warning, STOP and ask user.
     - status=error           → relay summary + error, STOP and ask user.

2. For an installed Git dependency, choose by source:
     - The official PICO Unity SDK (`com.bytedance.pico.xr`) pinned to its
       recognized moving branch uses the guarded refresh in §4.6; re-adding
       that exact captured Git URL there is the supported repair.
     - For any other Git dependency, the user must supply a different immutable
       tag or commit; call pico_xr_package(action=add, identifier=<new Git URL>)
       and apply the normal result handling above. Re-adding the same moving URL
       (for example, the same `#main` or `#develop` reference) returns
       `status=already_present`; it is a no-op and does not refresh
       `Packages/packages-lock.json`.
     - Never remove the package, hand-edit `Packages/manifest.json` or
       `Packages/packages-lock.json`, or claim that a lock was refreshed
       without a changed identifier.
```

### 4.6 Repair an initialized official PICO Unity SDK Git dependency

Use this procedure after initialization when SpatialML setup, doctor, or Pipeline Zoo reports that
the resolved `com.bytedance.pico.xr` package is incomplete or lacks
`SpatialMLPipelineZooImporterCli`. Do not route this case back to `/pico-unity-init`; its guard
intentionally stops when `.pico-cli/config.json` already exists.

```
1. Run the Unity MCP connection pre-check. The project must be open and the bridge ready.
2. Read Packages/manifest.json and capture the exact value of com.bytedance.pico.xr.
3. Classify that value without rewriting it:
     - recognized official PICO-Unity-SDK Git URL whose ref is known to be a moving branch (the
       shipped default is https://github.com/Pico-Developer/PICO-Unity-SDK.git?path=/XR#main)
       → continue.
     - pinned commit or tag, local/file dependency, embedded package, registry version, or any
       custom/unrecognized source, or a Git ref whose branch status is uncertain → report BLOCKED,
       show the current value, and ask the developer for the explicit target identifier. Do not
       replace it automatically.
4. call pico_xr_package(action=add, identifier=<the exact captured Git URL>)
     - status=error           → relay summary + error and STOP.
     - status=skipped         → relay summary + warning, report BLOCKED, and ask the developer.
     - status=ok              → run the post-write settle loop.
     - status=already_present → relay the summary; if the expected SDK capability is still absent,
                                report BLOCKED instead of looping the same request.
5. Rerun the operation that exposed the stale SDK:
     - pico-cli spatialml setup --project <unity-project> --format json
     - pico-cli spatialml doctor --project <unity-project> --format json
     - or the original pico-cli spatialml pipeline install command.
6. Confirm SpatialMLPipelineZooImporterCli is now available before reporting the repair complete.
```

Re-adding the exact moving Git URL is the refresh operation: Unity Package Manager resolves the
branch again and updates its lock. Do not substitute generic
`pico_xr_package(action=update, packageName=com.bytedance.pico.xr)` for this Git repair, and do not
remove the package first.

## 5. Identifier hints

- Package names use reverse-DNS (e.g. `com.unity.xr.interaction.toolkit`).
- Pin a version with `@`: `com.unity.xr.hands@1.5.0`.
- Git URLs work too (`https://github.com/...` or `git@github.com:...`); the
  underlying `Client.Add` handles them. Pass them as `identifier` unchanged —
  the C# layer's `SplitIdentifier` recognises `git@` prefixes and won't
  mistake them for `name@version`.
- Prefer an immutable tag or commit when changing an installed Git dependency
  outside the official PICO Unity SDK repair in §4.6. For those dependencies, a
  moving branch reference such as `#main` is not a refresh instruction, and
  re-adding the same URL is an idempotent no-op under this tool contract.
- Common reverse-DNS names for PICO workflows:
  - `com.unity.xr.interaction.toolkit` — XRI
  - `com.unity.xr.hands` — XR Hands
  - `com.unity.xr.openxr` — OpenXR plug-in
  - `com.unity.inputsystem` — Input System
- Common sample displayNames for XRI 3.x: `Starter Assets`, `Hands Interaction Demo`,
  `Meta Gaze Adapter`, `XR Device Simulator`.
- Common sample displayName for `com.unity.xr.hands`: `HandVisualizer`.

## 6. Error & warning surfaces (LLM-facing)

| Returned `status` | What to tell the user                                                           |
| ----------------- | ------------------------------------------------------------------------------- |
| `ok`              | Echo `summary`. If `data.previousVersion != null`, mention the upgrade.         |
| `already_present` | Echo `summary` and explicitly say "no change made; existing state kept".        |
| `skipped`         | Echo `summary` + `warning`, then apply the typed rules below.                   |
| `error`           | Echo `summary` + `error`. Suggest checking Unity Console; do NOT retry blindly. |

Typed `skipped` rules:

- `info` in a read-only query means "not installed"; report it without writing.
- `info` in an explicit install / ensure flow may continue to `add` under §4.1.
- `import_sample` with a missing-package warning in an already-authorized import
  or building-block dependency flow is **transitional**: follow §4.2/§4.3
  (auto-install + settle loop + one retry).
- Any other `skipped`, or the same package/sample import remaining `skipped`
  after its one retry, must stop and ask. A later `skipped` from a different
  documented building-block transition is classified by the owning workflow,
  not as a repeated package transition.

## 7. Anti-patterns (DO NOT)

- DO NOT skip the post-write settle loop on mutating calls. The next MCP call
  will fail because the bridge is offline during domain reload.
- DO NOT call `pico_xr_package(action=add)` followed by `import_sample` in the
  same agent turn without the settle loop in between.
- DO NOT hand-edit `Packages/manifest.json`; always go through `pico_xr_package`.
  The sole exception is `pico-unity-init`, which bootstraps the manifest directly
  before the Unity MCP bridge (and therefore `pico_xr_package`) is available; once
  initialization is done and the bridge is running, every package change goes
  through `pico_xr_package`.
- DO NOT hard-code package versions in your replies unless the user asks. Let
  the registry resolve "latest" when `version` is omitted.
- DO NOT classify `status=skipped` from its warning text alone. It is
  transitional only for the typed §2/§6 install or import contexts; follow the
  §4.1-§4.3 flow (settle loop + one retry) there. This mirrors the
  transitional-`skipped` exception in
  pico-unity-buildingblocks (`SKILL.md` §8 /
  `pico-unity-buildingblocks/references/orchestration.md` step C); keep the two
  skills consistent — stop-and-ask applies to non-transitional `skipped` or the
  same package/sample transition remaining `skipped` after its retry.
- DO NOT loop a failed `add` more than once without changing parameters; relay
  the error to the user and let them decide.
- DO NOT automatically replace pinned, local, embedded, registry, custom, unrecognized, or
  branch-uncertain PICO SDK sources during repair. Require an explicit target from the developer.
- DO NOT route an initialized project to `/pico-unity-init` for SDK repair.
- For Git dependencies outside the official PICO Unity SDK repair in §4.6, do not present the same
  moving Git URL as a package repair. An `already_present` result means no change was made; wait for
  an explicit refresh operation or use a user-supplied different immutable tag or commit.
