# pico-cli Command Families

Use this reference to choose the right `pico-cli` command family before reading a specialized skill.

## Discovery First

When command shape is unclear, inspect help before guessing:

```bash
pico-cli --help
pico-cli doctor --help
pico-cli <family> --help
pico-cli <family> <command> --help
```

Use `pico-cli doctor --format json` as the broad read-only environment summary
when the installed CLI exposes it. The root doctor should route to more specific
module doctors or fallback checks; it should not replace repair commands such as
`setup` or `plugin update`.

Use the repository command definitions as the source of truth for names and flags when editing this plugin.

## Setup and Plugin Commands

| Goal                                      | Command family                   | Notes                                                                                                                             |
| ----------------------------------------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Broad CLI environment diagnostics         | `pico-cli doctor`                | Read-only top-level summary; route repair details to `pico-env-doctor` when setup, plugin, or MCP is weak.                        |
| Install/configure host integration        | `pico-cli setup`                 | Use for Claude Code, Cursor, Codex, GitHub Copilot, or Trae CLI plugin-host setup. Route environment repair to `pico-env-doctor`. |
| Update plugin metadata/content            | `pico-cli plugin update`         | Host/plugin maintenance flow. Route stale plugin or missing skills to `pico-env-doctor`.                                          |
| Create local setup support bundle         | `pico-cli plugin audit`          | Metadata-only support evidence for plugin/MCP visibility issues; transcript mode requires explicit review.                        |
| Serve PICO dev knowledge graph as MCP     | `pico-cli mcp:dev-knowledge`    | MCP launch entry used by the public plugin `.mcp.json`; hosts load it after setup/restart.                                        |

## Project Creation

| Goal                               | Command family            | Notes                                                                                                       |
| ---------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Create a first Spatial SDK project | `pico-cli project create` | Route project bootstrap work to `spatial-app-onboarding`; choose and pass one supported `--template` value. |

## Emulator Lifecycle

| Goal                                    | Command family                                      | Notes                                                                       |
| --------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------- |
| Check emulator prerequisites            | `pico-cli emulator doctor`                          | Use before setup/start when environment readiness is unknown.               |
| Prepare emulator prerequisites          | `pico-cli emulator setup`                           | Use when doctor reports missing dependencies and the user wants setup help. |
| List AVDs                               | `pico-cli emulator list`                            | `--managed-only` focuses on CLI-created PICO AVDs.                          |
| Create/start/status/stop/delete AVDs    | `pico-cli emulator create/start/status/stop/delete` | Route execution workflows to `spatial-emulator-usage`.                      |
| Collect emulator logs                   | `pico-cli emulator dump-logs`                       | Use for emulator crash/debug evidence.                                      |
| Delete downloaded emulator bundle/cache | `pico-cli emulator delete-image`                    | Destructive; use only when explicitly requested.                            |

## Device Inspection and Shell

| Goal                            | Command family                                      | Notes                                                                |
| ------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------- |
| List/connect/disconnect devices | `pico-cli device list/connect/disconnect`           | Start with `device list --format json` when target state is unknown. |
| Inspect current target          | `pico-cli device info/battery/props`                | Prefer JSON for structured inspection.                               |
| Run shell command               | `pico-cli shell ...` or `pico-cli device shell ...` | Use only when no higher-level command covers the need.               |

## App Operations

| Goal                                        | Command family             | Notes                                                                        |
| ------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------- |
| Install/list/info/launch/stop/uninstall app | `pico-cli app ...`         | Route end-to-end install/launch/debug workflows to `spatial-emulator-usage`. |
| Read app logs                               | `pico-cli app logcat`      | Prefer before raw `adb logcat` when app-focused logging is enough.           |
| Watch for app crashes                       | `pico-cli app watch-crash` | Long-running diagnostic flow; report exact package and target.               |

## Files and Capture

| Goal                                       | Command family                | Notes                                                                        |
| ------------------------------------------ | ----------------------------- | ---------------------------------------------------------------------------- |
| Push/pull/list/mkdir/remove/cat/stat files | `pico-cli files ...`          | Treat `files rm` as destructive.                                             |
| Capture screenshot                         | `pico-cli capture screenshot` | Use explicit `--out <path>` and verify the host file exists.                 |
| Capture recording                          | `pico-cli capture record`     | Use explicit `--time <seconds>` and `--out <path>` for reviewable artifacts. |

## Logs

| Goal                    | Command family        | Notes                                                   |
| ----------------------- | --------------------- | ------------------------------------------------------- |
| General device logs     | `pico-cli log`        | Use tag/level/line filters for concise output.          |
| App logs                | `pico-cli app logcat` | Prefer for package-focused debugging.                   |
| Raw logcat escape hatch | `pico-cli adb logcat` | Use only when high-level log commands are insufficient. |

## Performance Profiling

| Goal                             | Command family              | Notes                                                                             |
| -------------------------------- | --------------------------- | --------------------------------------------------------------------------------- |
| Perf toolchain readiness         | `pico-cli perf doctor ...`  | Route to `spatial-app-perf-diagnose`.                                             |
| Real-time diagnosis              | `pico-cli perf monitor ...` | Route to `spatial-app-perf-diagnose`.                                             |
| Perfetto trace record/load/query | `pico-cli perf trace ...`   | Route to `spatial-app-perf-diagnose`; use trace evidence rather than speculation. |

## Raw ADB Escape Hatch

Use `pico-cli adb ...` only when the higher-level family does not expose the operation or the user explicitly needs raw ADB behavior.

Common raw escape hatches:

- `pico-cli adb devices`
- `pico-cli adb shell`
- `pico-cli adb pull` / `pico-cli adb push`
- `pico-cli adb install` / `pico-cli adb uninstall`
- `pico-cli adb logcat`
- `pico-cli adb forward` / `pico-cli adb reverse`
- `pico-cli adb getprop` / `pico-cli adb setprop`
- `pico-cli adb root`

Prefer `pico-cli device`, `pico-cli files`, `pico-cli app`, or `pico-cli log` before raw ADB when those families cover the workflow.
