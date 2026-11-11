---
name: pico-cli
description: Generic pico-cli usage guide for command discovery, command-family selection, help/version checks, output formats, device targeting, safe defaults, managed sub-CLI invocation, and command-level emulator, device, app, capture, log, perf, and SpatialML usage. Use whenever the user asks which pico-cli command or command family to run, in any project or outside a project. Routes environment diagnosis to pico-cli doctor and project creation or SDK work to pico-project-setup. NOT for environment readiness verification (pico-env-doctor), project creation or SDK workflows (pico-project-setup), or multi-step emulator/device/screenshot workflows owned by the specialized general Skills.
license: 'Apache-2.0'
---

# pico-cli Usage Skill

Use this skill when the user asks how to use `pico-cli` itself: which command family to choose, how to discover options, how to target a device, how to inspect JSON output, or how to make a safe first command sequence.

This is a **routing and CLI-usage skill**, not the owner of every workflow implemented by `pico-cli`. It works the same outside a project, in a Spatial project, and in a Unity project.

## Reference Loading

Load shared references only when needed:

For active Workflow guidance, pause/resume, waiting Handoffs, or takeover by another main Agent, load `references/workflow-control.md`. Discover current recipients with `workflow guidance targets`; use bounded Run reads to notice waiting. `workflow wait` does not return merely because the Run is waiting. Read public state together with the package Skill's role/responsibility and route descriptions; a last-completed snapshot or a node name is not a live invocation. Dynamic task summary is optional. Submit once to the actual returned target and read the same request receipt; accepted, delivered and adopted are different facts.

For dev workflow goal changes, preserve project files and a free-form handover, wait for the old writer to stop, then use the installed package's documented `startAt`/existing-design input to create a new Run. Its Skill owns the exact input example and independent asset controls. Pausing or cancelling the root Run alone does not prove an independent asset Agent or its Editor Runs stopped.

Managed dev roles request full tool permissions by default, so project work does not require approval for every tool call. Agents should keep direct reads/writes and handover files in the project. Existing location/symlink checks cover corresponding client permission callbacks; native bypass and shell execution do not create a forced project sandbox across Hosts. Explicit user limits, OS and organization controls still apply. This does not force every Host to disable its native sandbox. Cursor uses its ACP full-tool agent mode with client permission responses; the native Cursor run remains a QA boundary. See `references/workflow-control.md` for Auto model selection and current guidance limitations.

Workflow token observation distinguishes cache reads from cache writes. A missing field is unknown; do not derive an unreported total by adding input and output. Do not count a parent task aggregate again alongside its Host continuation invocations. Local event observation, online reporting/registration, and data queryable in the telemetry platform require separate evidence.

Workflow telemetry is not enabled by default in this release input: no Workflow lifecycle or Token event is registered for upload. Local events and summaries remain available. Enabling production reporting requires event-field registration, review of concrete distribution/region/eventNames entries with evidenceRef and verifiedAt in the release-owned adoption manifest, a rebuilt package, and verification that the official package reports queryable data. An ordinary CLI flag or environment variable cannot force unregistered events on.

| Reference                              | Load when                                                                                                           |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `references/command-families.md`       | Choosing the right `pico-cli` command family or explaining what each family owns                                    |
| `references/spatialml-commands.md`     | Exact SpatialML command names, flags, output states, or availability boundaries                                     |
| `references/conventions-and-safety.md` | Device targeting, output formats, verification, destructive commands, raw `adb` fallback, or long-running commands  |
| `references/troubleshooting.md`        | CLI installation, unknown commands, missing devices, command discovery, or first-pass diagnosis                     |
| `references/workflow-observation.md`   | Exporting one Workflow Run as paginated JSON, checking observation coverage, or recomputing a fixed offline summary |

## When To Use

Use this skill for requests like:

- "How do I use `pico-cli`?"
- "Which `pico-cli` command should I run for this?"
- "Show me the command families in `pico-cli`."
- "How do I get JSON output from `pico-cli`?"
- "How do I pick a target device?"
- "When should I use `pico-cli adb` instead of `pico-cli app` or `pico-cli device`?"
- "What is the safe way to inspect my emulator/device/app state first?"
- "Which `pico-cli spatialml` command should I use?"

## Route Away For Specialized Work

- Environment, plugin, Skill, or MCP problems: use `pico-env-doctor` for scope, freshness checks, and authorized repair. Help/version discovery alone does not require the full preflight.

For a known target project, pass `--project <target-dir>` to root doctor. When setup supplied a
separate session resource root, also preserve `--workspace-root <session-root>` on diagnosis and
authorized repair calls. Do not infer that an engineering directory owns Host resources stored
at its parent, or drop either path from a copied recovery command.

- Use `capture-camera` for camera movement, held viewpoints, and continuous camera recordings, and `pico-cli-screenshot` for still screenshots. Both work from any directory when the target supports the requested capability.

- Creating a project, choosing the Spatial or Unity platform, configuring a project for AI development, or SDK and app-code work: use `pico-project-setup`. It configures the project's platform plugin, whose Skills own SDK, UI, scene, and application implementation workflows.
- Use `pico-emulator-usage` for emulator/device lifecycle, APK operations, logs, and files, and `pico-cli-device-target` to resolve a concrete target. Platform Skills retain application, performance, and SpatialML ownership. This Skill supplies generic command usage.

## Core Workflow

1. Identify the user's goal in one sentence.
2. Select the command family and explain why.
3. Prefer discovery commands before state-changing commands:
   - `pico-cli --help`
   - `pico-cli doctor --help`, then `pico-cli doctor --format json` when available for broad diagnostics
   - `pico-cli <family> --help`
   - `pico-cli <family> <command> --help`
4. Prefer JSON output when a command supports it and the result will drive later decisions.
5. Choose explicit device targeting when more than one target may exist.
6. For destructive or long-running actions, confirm intent before proceeding.
7. Report actual command results and next smallest useful step.

Root doctor is diagnostic by default but not unconditionally read-only; load
`command-families.md` for its conditional catalog-cache effects and the strictly
read-only fallback.

## Quick Command-Family Map

Use this summary for routing; load `command-families.md` for details.

| Goal                                      | Start with                                                                                     |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Broad environment/plugin/MCP diagnostics  | `pico-cli doctor --format json`; `pico-cli doctor --fix` for supported repairs                 |
| Install or refresh agent plugins          | `pico-cli setup` once per user; `pico-cli plugin update` to refresh                            |
| Detect or configure a project             | `pico-cli project detect --format json`; configuration goes through `pico-project-setup`       |
| Check emulator prerequisites or lifecycle | `pico-cli emulator ...`                                                                        |
| Inspect connected devices                 | `pico-cli device ...`                                                                          |
| Install/launch/inspect app packages       | `pico-cli app ...`                                                                             |
| Transfer or inspect device files          | `pico-cli files ...`                                                                           |
| Capture screenshots                       | `pico-cli capture screenshot ...`                                                              |
| Accessibility snapshots and actions       | `pico-cli interact query\|perform`                                                             |
| Read logs                                 | `pico-cli log`, `pico-cli app logcat`                                                          |
| Performance profiling and Perfetto        | `pico-cli perf ...`                                                                            |
| Camera movement, observation and orbits   | `pico-cli camera ...`; follow general’s `capture-camera`; `capture camera` remains compatible  |
| SpatialML project and Pipeline Zoo work   | `pico-cli spatialml ...`; start with `spatialml onboard`, `doctor`, or `pipeline search`       |
| Run a managed sub-CLI prepared by setup   | `pico-cli tool list`; catalog `command` or `tool exec` fallback                                |
| Raw device escape hatch                   | `pico-cli adb ...` or `pico-cli shell ...` only when high-level commands do not cover the need |

Use already-discovered platform accessibility guidance when the task needs app-side implementation.
For shared accessibility inspection/actions in general-only or Unity sessions, discover `pico-cli interact --help` and the
selected subcommand's help, retain the explicit device and application target, and inspect the
returned accessibility tree before choosing an action. A missing platform Skill does not require
project configuration. If the selected app exposes no usable nodes/actions, report that limitation;
do not infer support from plugin installation or send guessed coordinates as an equivalent action.

## Managed Sub-CLIs

`pico-cli setup` prepares managed sub-CLIs and adds them to the user's shell `PATH`, but an Agent shell may not see that `PATH`. Inspect the active catalog before choosing the execution path:

```bash
pico-cli tool list --format json
```

When a managed CLI is `ready` and the top-level `onPath` is `true`, run its exact catalog `command` directly.
When `onPath` is `false`, use `pico-cli tool exec <name> <args...>` as the stable tool-ID fallback. If a direct launch is attempted, retry it once through `tool exec` only when the Agent or Host confirms an executable resolution failure before the managed CLI starts, such as POSIX shell `command not found`, Node `ENOENT` identifying the executable, Windows `not recognized as an internal or external command`, PowerShell `CommandNotFoundException`, or an equivalent launch diagnostic.
Do not infer launcher failure from the managed CLI's own stderr or output after it starts, even if that output contains `command not found`; report the business error without retrying it.
Do not infer a regional executable name. Use `pico-cli tool which <name> --format json` only for path diagnostics, not as the primary execution path. If the entry is absent or not ready, follow its reported compatibility action instead of attempting either invocation form.

If a managed tool is missing or stale, discover `pico-cli tool update --help`. When supported,
run `pico-cli tool update --check --format json`; authorized `pico-cli tool update` repairs the
running CLI's pinned set, not arbitrary latest upstream versions. `not-initialized` or `no-region`
requires setup through `pico-env-doctor`; resolve reported prerequisites for `blocked` and report
`catalog-invalid`. Older CLIs without tool update use the reported setup path. Recheck readiness;
do not replace managed tools with manual installs or rerun setup solely for a PATH-only issue.

## Persistent Knowledge Selection

Use this branch only when the user asks to change the saved knowledge version. For a temporary
version-specific question, use `knowledge-query` instead. Inspect `project detect` with the actual
project/workspace roots and `knowledge list`, and identify the requested selection owner and platform.
Within that platform, if the requested version is missing, use an authorized `knowledge pull <version>`
first. Select it with `knowledge use <version> --project <resource-root>` for the configured project,
or `knowledge use <version> --user` for user-level selection; do not let cwd select the write scope.
Verify the returned version/platform/owner and re-detect using the same roots. This changes disk
selection, not an already-running MCP workspace; later queries follow `knowledge-query` activation.
Do not use project configure to change an existing pin or silently switch the app's SDK/platform.

## Safe Defaults

- Prefer high-level `pico-cli` command families before raw `pico-cli adb`.
- Prefer `--format json` for inspection commands when the output will be parsed or compared.
- Prefer explicit `--device <id>` / `-d <id>` when multiple devices are connected.
- Inspect before writing, deleting, uninstalling, clearing logs, or starting a long-running watch.
- Treat `pico-cli shell ...` as a raw escape hatch: when no device is online, run `pico-cli emulator start` explicitly and wait for readiness before invoking shell.
- Do not route volumetric/spatial interaction through `pico-cli shell input tap x y`; that path only covers 2D screen-coordinate input and is not reliable for spatial containers.
- Do not invent command names or flags; use help output when uncertain.

## Response Pattern

When using this skill, answer in this shape:

1. **Intent**: the CLI goal you inferred.
2. **Recommended command family**: the family and why it fits.
3. **Suggested commands**: the minimal command sequence, starting with help/inspection when useful.
4. **Safety / targeting note**: device id, output format, destructive/long-running behavior if relevant.
5. **Handoff**: `pico-cli doctor` for environment problems, or `pico-project-setup` for project and SDK work, when the request goes beyond CLI usage.
