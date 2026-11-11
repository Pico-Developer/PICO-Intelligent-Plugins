# pico-cli Command Families

Use this reference to choose the right `pico-cli` command family. In a configured project, the
platform plugin's Skills own application workflows; general owns shared diagnosis, device/emulator, screenshot, and camera workflows, including outside projects.

## Discovery First

When command shape is unclear, inspect help before guessing:

```bash
pico-cli --help
pico-cli doctor --help
pico-cli <family> --help
pico-cli <family> <command> --help
```

Use `pico-cli doctor --format json` as the broad environment summary when the
installed CLI exposes it. It reports user-level setup, the current project's
platform plugin, knowledge, and toolchains, and lists the next action for each
weak area. Root doctor is diagnostic by default but not unconditionally
read-only. When the release catalog cache is missing, stale, or incompatible,
it may prepare the cache and add conditional `host-write`, `network`, and
`long-running` effects. In a strictly read-only context, skip root doctor and
inspect only the nearest project-local `.pico-env.json` (or
`~/.pico/.pico-env.json`), the Host's local plugin manifest or registry entry,
and installed plugin files. These static checks do not refresh the release
catalog and therefore cannot verify catalog freshness. `pico-cli doctor --fix`
applies only the supported repairs when separately authorized.

Use the installed CLI's help to verify command names and flags.

## Setup, Project, and Plugin Commands

| Goal                                    | Command family                | Notes                                                                                                                                           |
| --------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Broad CLI environment diagnostics       | `pico-cli doctor`             | Diagnostic summary with conditional catalog-cache effects; add `--project <path>` for a specific project and `--fix` for supported repairs.     |
| Install user-level host integration     | `pico-cli setup`              | Run once per user. Installs the general plugin for the selected Agent Hosts and the machine-wide toolchains.                                    |
| Inspect a project                       | `pico-cli project detect`     | Read-only; reports the engineering platform, the configured platform, and whether setup is complete.                                            |
| Configure a project for AI development  | `pico-cli project configure`  | Writes the platform plugin into the project; drive it through `pico-project-setup`.                                                             |
| Create a project from a template        | `pico-cli project create`     | Uses the configured project platform; the platform creation Skill that `pico-project-setup` hands off runs it.                                  |
| Refresh installed plugins               | `pico-cli plugin update`      | Refreshes the user-level general plugin and the current project's platform plugin.                                                              |
| Serve PICO development knowledge as MCP | `pico-cli knowledge:server`   | MCP launch entry used by the general plugin `.mcp.json`; Verify Host discovery and approval after setup; reload only when the Host requires it. |
| Select a knowledge version              | `pico-cli knowledge use <v>`  | Pins the version in the current configured project, otherwise the user level; setup reruns keep the pin.                                        |
| Run a managed sub-CLI                   | Catalog command / `tool exec` | Inspect `pico-cli tool list --format json`; use the exact command when ready and on PATH, otherwise use the stable tool-ID fallback.            |

When a managed CLI is `ready` and the top-level `onPath` is `true`, run its exact catalog `command` directly.
When `onPath` is `false`, use `pico-cli tool exec <name> <args...>` as the stable tool-ID fallback. If a direct launch is attempted, retry it once through `tool exec` only when the Agent or Host confirms an executable resolution failure before the managed CLI starts, such as POSIX shell `command not found`, Node `ENOENT` identifying the executable, Windows `not recognized as an internal or external command`, PowerShell `CommandNotFoundException`, or an equivalent launch diagnostic.
Do not infer launcher failure from the managed CLI's own stderr or output after it starts, even if that output contains `command not found`; report the business error without retrying it.
Use `pico-cli tool which <name> --format json` only for path diagnostics. Follow the reported compatibility action when the catalog entry is absent or not ready; do not infer a regional executable name.

Managed CLI refresh is separate from plugin refresh: discover `pico-cli tool update --help`,
then use `pico-cli tool update --check --format json` for drift inspection. An authorized
`pico-cli tool update` re-pins the selected region's tools to the running CLI's catalog;
upgrade pico-cli in the existing channel to advance that catalog. Follow reported initialization,
region, prerequisite, or catalog errors rather than treating every result as an installed update.

## Emulator Lifecycle

| Goal                                    | Command family                                      | Notes                                                                                                                                                      |
| --------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Check emulator prerequisites            | `pico-cli emulator doctor`                          | Use before setup/start when environment readiness is unknown.                                                                                              |
| Diagnose emulator prerequisites         | `pico-cli emulator setup`                           | Read-only diagnostic guidance; inspects legacy storage without migrating it and routes repair to `doctor --fix`, `emulator install`, or `emulator create`. |
| List AVDs                               | `pico-cli emulator list`                            | `--managed-only` focuses on CLI-created PICO AVDs.                                                                                                         |
| Create/start/status/stop/delete AVDs    | `pico-cli emulator create/start/status/stop/delete` | Check `emulator status --format json` before and after lifecycle changes.                                                                                  |
| Collect emulator logs                   | `pico-cli emulator dump-logs`                       | Use for emulator crash/debug evidence.                                                                                                                     |
| Delete downloaded emulator bundle/cache | `pico-cli emulator delete-image`                    | Destructive; use only when explicitly requested.                                                                                                           |
| Read latest launch log                  | `pico-cli emulator log [avd] --last`                | Read a Primer launch log; keep dump-logs for exported evidence. Omitting `avd` selects the current running emulator or the sole managed AVD.               |

## Device Inspection and Shell

| Goal                            | Command family                                      | Notes                                                                |
| ------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------- |
| List/connect/disconnect devices | `pico-cli device list/connect/disconnect`           | Start with `device list --format json` when target state is unknown. |
| Inspect current target          | `pico-cli device info/battery/props`                | Prefer JSON for structured inspection.                               |
| Run shell command               | `pico-cli shell ...` or `pico-cli device shell ...` | Use only when no higher-level command covers the need.               |

## App Operations

| Goal                                        | Command family             | Notes                                                                            |
| ------------------------------------------- | -------------------------- | -------------------------------------------------------------------------------- |
| Install/list/info/launch/stop/uninstall app | `pico-cli app ...`         | Verify with `app info <package> --format json` after install or launch.          |
| Read device or running app logs             | `pico-cli app logcat`      | Use `--package <package>` for app-scoped logs; otherwise this reads device logs. |
| Watch for app crashes                       | `pico-cli app watch-crash` | Long-running diagnostic flow; report exact package and target.                   |

## Files and Capture

Use `pico-cli camera move/get/reset/probe/prepare` for camera control and centered
observation without media. `camera move --screenshot <path>` adds an endpoint PNG.
The compatible `capture camera` entry uses the same runtime. Camera motion during
recording is emulator-only; real devices retain moved-view screenshots and ordinary
screenshots/recording at the current held view.

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

| Goal                             | Command family               | Notes                                                                                     |
| -------------------------------- | ---------------------------- | ----------------------------------------------------------------------------------------- |
| Perf toolchain readiness         | `pico-cli perf doctor check` | Run first; it reports missing profiler prerequisites with next actions.                   |
| Real-time diagnosis              | `pico-cli perf live ...`     | Long-running; confirm the target package and device before starting.                      |
| Perfetto trace record/load/query | `pico-cli perf trace ...`    | Use explicit durations and output paths; base conclusions on trace evidence, not guesses. |

## SpatialML

Load `spatialml-commands.md` when the user needs exact syntax, flags, output handling, or
pySpatialML installation and delegation details. App integration and Pipeline Zoo adaptation belong
to the configured project's platform plugin.

| Goal                              | Command family                               | Notes                                                                                                                                              |
| --------------------------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Assess project onboarding         | `pico-cli spatialml onboard`                 | Read-only Kotlin, Unity, and Native OpenXR assessment; returns SDK-specific next actions.                                                          |
| Configure SpatialML               | `pico-cli spatialml setup`                   | Kotlin may edit project files; Unity validates; Native reports readiness/manual integration. May install pySpatialML after SDK prerequisites pass. |
| Diagnose SpatialML readiness      | `pico-cli spatialml doctor`                  | Read-only checks for all three SDKs, Unity importer support, and delegated host-tool capabilities.                                                 |
| Search Pipeline Zoo               | `pico-cli spatialml pipeline search`         | Network read; compare model-card descriptions and supported modes.                                                                                 |
| Install a Pipeline Zoo package    | `pico-cli spatialml pipeline install`        | Network and host write: Kotlin/Native assets placement or Unity importer; supports --unity-editor.                                                 |
| Verify a Pipeline Zoo package     | `pico-cli spatialml pipeline verify`         | Delegates package validation to installed pySpatialML 0.5.3 or newer.                                                                              |
| Inspect or visualize LiteRT model | `pico-cli spatialml model inspect/visualize` | Delegates model metadata and visualization to installed pySpatialML 0.5.3 or newer.                                                                |

## Low-level ADB-backed command family

Use `pico-cli adb ...` only when the higher-level family does not expose the operation. This is a
low-level ADB-backed family, but its subcommands do not all have the same contract:

True passthrough subcommands expose the corresponding low-level operation and preserve the
native ADB argument surface:

- `pico-cli adb shell`
- `pico-cli adb push`
- `pico-cli adb install` / `pico-cli adb uninstall`
- `pico-cli adb forward` / `pico-cli adb reverse`

`--device` before the passthrough boundary selects the pico-cli target. A downstream `--device` or
`--device=<value>` argument must follow a standalone `--`; every token after that boundary is
forwarded unchanged. This separator is mandatory because the same option spelling cannot otherwise
be assigned unambiguously to pico-cli or the downstream command.

`pico-cli adb logcat` is hybrid: structured logcat options use the CLI wrapper, while arguments
after the passthrough boundary are forwarded to native `adb logcat`.

`pico-cli adb devices`, `pico-cli adb getprop`, `pico-cli adb setprop`, and `pico-cli adb root`
are structured ADB-backed wrappers. They expose CLI-defined options and output rather than being
raw passthrough commands.

`pico-cli adb pull` is not a raw passthrough. It is a staged no-clobber wrapper with explicit
`--replace` behavior. Use its documented `<remote> [local]` arguments and wrapper options. If
native `adb pull` flags are required, run plain `adb pull` directly instead.

Prefer `pico-cli device`, `pico-cli files`, `pico-cli app`, or `pico-cli log` before raw ADB when those families cover the workflow.
