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

Use the installed CLI's help to verify command names and flags.

## Setup and Plugin Commands

| Goal                                    | Command family              | Notes                                                                                                                             |
| --------------------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Broad CLI environment diagnostics       | `pico-cli doctor`           | Read-only top-level summary; route repair details to `pico-env-doctor` when setup, plugin, or MCP is weak.                        |
| Install/configure host integration      | `pico-cli setup`            | Use for Claude Code, Cursor, Codex, GitHub Copilot, or Trae CLI plugin-host setup. Route environment repair to `pico-env-doctor`. |
| Update plugin metadata/content          | `pico-cli plugin update`    | Host/plugin maintenance flow. Route stale plugin or missing skills to `pico-env-doctor`.                                          |
| Serve PICO development knowledge as MCP | `pico-cli knowledge:server` | MCP launch entry used by the public plugin `.mcp.json`; hosts load it after setup/restart.                                        |

## Project Creation

| Goal                               | Command family            | Notes                                                                                                       |
| ---------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Create a first Spatial SDK project | `pico-cli project create` | Route project bootstrap work to `spatial-app-onboarding`; choose and pass one supported `--template` value. |

## Emulator Lifecycle

| Goal                                    | Command family                                      | Notes                                                                                                                 |
| --------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Check emulator prerequisites            | `pico-cli emulator doctor`                          | Use before setup/start when environment readiness is unknown.                                                         |
| Diagnose emulator prerequisites         | `pico-cli emulator setup`                           | Read-only diagnostic guidance; route repair to `doctor --fix`, `emulator install`, or `emulator create` as suggested. |
| List AVDs                               | `pico-cli emulator list`                            | `--managed-only` focuses on CLI-created PICO AVDs.                                                                    |
| Create/start/status/stop/delete AVDs    | `pico-cli emulator create/start/status/stop/delete` | Route execution workflows to `spatial-emulator-usage`.                                                                |
| Collect emulator logs                   | `pico-cli emulator dump-logs`                       | Use for emulator crash/debug evidence.                                                                                |
| Delete downloaded emulator bundle/cache | `pico-cli emulator delete-image`                    | Destructive; use only when explicitly requested.                                                                      |

## Device Inspection and Shell

| Goal                            | Command family                                      | Notes                                                                |
| ------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------- |
| List/connect/disconnect devices | `pico-cli device list/connect/disconnect`           | Start with `device list --format json` when target state is unknown. |
| Inspect current target          | `pico-cli device info/battery/props`                | Prefer JSON for structured inspection.                               |
| Run shell command               | `pico-cli shell ...` or `pico-cli device shell ...` | Use only when no higher-level command covers the need.               |

## App Operations

| Goal                                        | Command family             | Notes                                                                            |
| ------------------------------------------- | -------------------------- | -------------------------------------------------------------------------------- |
| Install/list/info/launch/stop/uninstall app | `pico-cli app ...`         | Route end-to-end install/launch/debug workflows to `spatial-emulator-usage`.     |
| Read device or running app logs             | `pico-cli app logcat`      | Use `--package <package>` for app-scoped logs; otherwise this reads device logs. |
| Watch for app crashes                       | `pico-cli app watch-crash` | Long-running diagnostic flow; report exact package and target.                   |

## Files and Capture

| Goal                                       | Command family                | Notes                                                                        |
| ------------------------------------------ | ----------------------------- | ---------------------------------------------------------------------------- |
| Push/pull/list/mkdir/remove/cat/stat files | `pico-cli files ...`          | Treat `files rm` as destructive.                                             |
| Capture screenshot                         | `pico-cli capture screenshot` | Use explicit `--out <path>` and verify the host file exists.                 |
| Capture recording                          | `pico-cli capture record`     | Use explicit `--time <seconds>` and `--out <path>` for reviewable artifacts. |

## Logs

| Goal                    | Command family                            | Notes                                                         |
| ----------------------- | ----------------------------------------- | ------------------------------------------------------------- |
| General device logs     | `pico-cli log`                            | Use tag/level/line filters for concise output.                |
| App logs                | `pico-cli app logcat --package <package>` | Prefer for package-focused debugging when the app is running. |
| Raw logcat escape hatch | `pico-cli adb logcat`                     | Use only when high-level log commands are insufficient.       |

## Performance Profiling

| Goal                             | Command family             | Notes                                                                                    |
| -------------------------------- | -------------------------- | ---------------------------------------------------------------------------------------- |
| Perf toolchain readiness         | `pico-cli perf doctor ...` | Route to `spatial-app-performance-analysis`.                                             |
| Real-time diagnosis              | `pico-cli perf live ...`   | Route to `spatial-app-performance-analysis`.                                             |
| Perfetto trace record/load/query | `pico-cli perf trace ...`  | Route to `spatial-app-performance-analysis`; use trace evidence rather than speculation. |

## SpatialML

Route setup, diagnosis, validation, app integration, and Pipeline Zoo package work to the unified
`spatialml` skill. It loads its package reference for discovery, adaptation, installation, import,
loading, and verification. Load `spatialml-commands.md` when the user needs exact syntax, flags, output
handling, or pySpatialML installation and delegation details.

| Goal                              | Command family                               | Notes                                                                               |
| --------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------- |
| Assess project onboarding         | `pico-cli spatialml onboard`                 | Read-only for Kotlin; Unity workflow belongs to PICO Unity Agentic Tools.           |
| Configure SpatialML               | `pico-cli spatialml setup`                   | Run after Kotlin SDK setup; may modify Kotlin project files or return a handoff.    |
| Diagnose SpatialML readiness      | `pico-cli spatialml doctor`                  | Read-only checks with Kotlin-specific next actions.                                 |
| Search Pipeline Zoo               | `pico-cli spatialml pipeline search`         | Network read; compare model-card descriptions and supported modes.                  |
| Install a Pipeline Zoo package    | `pico-cli spatialml pipeline install`        | Network and host write; this plugin documents Kotlin placement.                     |
| Verify a Pipeline Zoo package     | `pico-cli spatialml pipeline verify`         | Delegates package validation to installed pySpatialML 0.5.0 or newer.               |
| Inspect or visualize LiteRT model | `pico-cli spatialml model inspect/visualize` | Delegates model metadata and visualization to installed pySpatialML 0.5.0 or newer. |

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
