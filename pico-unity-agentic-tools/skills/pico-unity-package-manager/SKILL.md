---
name: pico-unity-package-manager
license: 'Apache-2.0'
description: |
  Manage Unity Package Manager packages and their samples for PICO XR
  workflows via the Unity MCP `pico_xr_package` tool. Handles install, remove,
  update, query, list-samples, and import-sample operations, and waits for the
  Editor to finish recompiling / domain-reloading after every mutating action
  so downstream steps run safely. Also called internally by
  `pico-unity-buildingblocks` before enabling a feature block.

  Trigger when the user wants to install / add / 安装, remove / 卸载, or
  update / 升级 a Unity package (XRI, XR Hands, XR Interaction Toolkit, Input
  System, OpenXR, etc.), import / 导入 a package sample (e.g. Starter Assets), or query installed packages / versions / samples. Also triggered indirectly
  when another skill (e.g. pico-unity-buildingblocks) needs a package or
  sample.

  Prerequisites: Unity Editor running with PICO MCP Extensions installed (the
  `pico_xr_package` tool exposed by the Unity MCP bridge) and the MCP client
  connected; if not, see the connection-precheck in
  `pico-unity-buildingblocks`.
---

# pico-unity-package-manager

## 1. Background

This skill is the **low-level package/sample subsystem** of the PICO Unity MCP
extension. It wraps a single MCP tool:

```
pico_xr_package(action, identifier?, packageName?, version?, sampleName?, overwrite?)
```

where `action` is one of:

| action          | parameters                                                             | purpose                                  |
| --------------- | ---------------------------------------------------------------------- | ---------------------------------------- |
| `list`          | —                                                                      | Snapshot of all installed packages       |
| `info`          | `packageName`                                                          | Is package X installed? At what version? |
| `add`           | `identifier` (e.g. `com.unity.xr.hands` or `com.unity.xr.hands@1.5.0`) | Install / switch version                 |
| `remove`        | `packageName`                                                          | Uninstall                                |
| `update`        | `packageName`, `version?` (empty = latest)                             | Switch version                           |
| `list_samples`  | `packageName`, `version?`                                              | Samples declared by the package          |
| `import_sample` | `packageName`, `sampleName`, `overwrite?`, `version?`                  | Copy a sample into Assets/Samples/…      |

The underlying C# layer is **idempotent**:

- Adding an already-installed package returns `status=already_present` (no-op).
- Removing a not-installed package returns `status=ok` (no-op).
- Importing an already-imported sample returns `status=already_present` (no-op).
- Importing a sample whose **package is not installed** returns `status=skipped` with a `warning` — DO NOT treat as failure; treat as "need to install the package first."

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
`skipped`, echo the `warning` and propose the obvious fix (usually:
install the missing package, then retry the sample import).

## 3. Mandatory workflow: domain-reload-safe writes

Mutating operations (`add`, `remove`, `update`, `import_sample`) trigger a
Unity Editor recompile / domain reload. **After every mutating call** you
MUST run the **post-write settle loop** before invoking any other PICO MCP
tool — otherwise the next tool call may fail because the MCP bridge is
temporarily down during the reload.

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
     - status=error → STOP and ask user.
     - status=ok | already_present → run post-write settle loop.
2. call pico_xr_package(action=import_sample, packageName=P, sampleName=S)
     - Apply step 4.2 rules to the result.
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

## 5. Identifier hints

- Package names use reverse-DNS (e.g. `com.unity.xr.interaction.toolkit`).
- Pin a version with `@`: `com.unity.xr.hands@1.5.0`.
- Git URLs work too (`https://github.com/...` or `git@github.com:...`); the
  underlying `Client.Add` handles them. Pass them as `identifier` unchanged —
  the C# layer's `SplitIdentifier` recognises `git@` prefixes and won't
  mistake them for `name@version`.
- Common reverse-DNS names for PICO workflows:
  - `com.unity.xr.interaction.toolkit` — XRI
  - `com.unity.xr.hands` — XR Hands
  - `com.unity.xr.openxr` — OpenXR plug-in
  - `com.unity.inputsystem` — Input System
- Common sample displayNames for XRI 3.x: `Starter Assets`, `Hands Interaction Demo`,
  `Meta Gaze Adapter`, `XR Device Simulator`.

## 6. Error & warning surfaces (LLM-facing)

| Returned `status` | What to tell the user                                                           |
| ----------------- | ------------------------------------------------------------------------------- |
| `ok`              | Echo `summary`. If `data.previousVersion != null`, mention the upgrade.         |
| `already_present` | Echo `summary` and explicitly say "no change made; existing state kept".        |
| `skipped`         | Echo `summary` + `warning`. Propose the obvious fix and ask user to confirm.    |
| `error`           | Echo `summary` + `error`. Suggest checking Unity Console; do NOT retry blindly. |

## 7. Anti-patterns (DO NOT)

- DO NOT skip the post-write settle loop on mutating calls. The next MCP call
  will fail because the bridge is offline during domain reload.
- DO NOT call `pico_xr_package(action=add)` followed by `import_sample` in the
  same agent turn without the settle loop in between.
- DO NOT hand-edit `Packages/manifest.json`; always go through `pico_xr_package`.
- DO NOT hard-code package versions in your replies unless the user asks. Let
  the registry resolve "latest" when `version` is omitted.
- DO NOT treat `status=skipped` as a hard failure. It's an actionable warning.
- DO NOT loop a failed `add` more than once without changing parameters; relay
  the error to the user and let them decide.
