---
name: pico-emulator-usage
description: Operates PICO emulators and connected devices for Spatial, Unity, and standalone APK tasks. Use when starting or stopping an emulator, installing or launching APKs, diagnosing startup crashes or flash exits, transferring files, collecting logs, or cleaning up emulator resources. NOT for screenshots, camera movement or recording, environment diagnosis, or application feature development. Use pico-cli-screenshot for still capture.
license: 'Apache-2.0'
---

# PICO Emulator and Device Usage

Use this skill for operating the local **PICO emulator**, a connected **ADB
device**, or the app/files/logging workflows around them through real
`pico-cli` commands.

This skill is for **execution-oriented environment work**, not for general
Kotlin/UI feature implementation. Trigger it directly when the requested
emulator/device workflow is already clear. When a request begins as generic
`pico-cli` help, `pico-cli` may route here after identifying this command
family.

## When NOT to Use

- Static 2D screenshots — use `pico-cli-screenshot`
- Camera movement or recording — use `capture-camera`
- Environment health verification — use `pico-env-doctor`
- App feature development — use `pico-project-setup` to select the configured platform workflow.

## What This Skill Should Do

When triggered, the agent should:

- prefer the high-level `pico-cli` commands over raw `adb` when the CLI already covers the workflow
- choose the smallest command sequence that solves the user's problem
- verify the environment before claiming success
- verify recording artifacts exist on the host before claiming capture succeeded
- explain blockers clearly when the machine or device state prevents progress
- when no device is online and runtime verification is required, use an available compatible PICO emulator through authorized `pico-cli emulator start`; if startup is not authorized or the task requires real hardware, report the blocker and required target instead of silently skipping verification
- avoid destructive cleanup unless the user explicitly asked for it

## When To Use This Skill

Use this skill for requests like:

- "Start or stop the PICO emulator"
- "Check whether the emulator is installed correctly"
- "Create an AVD for the PICO emulator"
- "Install, launch, stop, or uninstall an APK on the current emulator/device"
- "Collect logcat, crash clues, recordings, or emulator logs"
- "Push or pull files from the current emulator/device"
- "Check battery, props, device info, or connected devices"
- "Clean up CLI-created emulator instances safely"

Do not use this skill as the primary skill when the request is mainly:

- Spatial SDK feature implementation
- project scaffolding from templates
- SDK version upgrade or migration

In those cases, use the more specific skill first and bring this one in only if the work reaches a real emulator/device operation step.

For screenshot requests, use `pico-cli-screenshot`; this skill does not choose
between flat and spatial screenshot modes.

## Core Rules

### 0. Run the environment preflight first

Before the first environment-dependent operation in a Host session (help/version discovery is exempt):

1. Reuse the latest successful `pico-env-doctor` result when the workspace, target Host, and tooling are unchanged, no environment setup, CLI/plugin/toolchain update, or Host-integration install has run since, no new failure signal exists, and the user has not requested re-verification.
2. Emulator, device, and app lifecycle operations—including emulator image install, create/start/stop, and APK install/launch—do not by themselves invalidate that complete report. On a later turn in the same unchanged Host session, reuse it and refresh only the task-specific target state needed now, such as `emulator doctor`, `device list`, or `emulator status`; do not rerun the full environment doctor solely because one of those lifecycle operations ran.
3. Otherwise activate `pico-env-doctor` and inspect the comprehensive report. Continue when task-required capabilities are verified; report unrelated findings without forcing every optional tool to pass.
4. Do not substitute `pico-cli emulator doctor`, `device list`, or `emulator list` for the initial environment gate; those commands are task-specific checks that run after the environment preflight.

### 1. Prefer host execution for emulator startup

On Windows and macOS, `pico-cli emulator start` must prefer an authorized host
execution channel that runs the locally installed emulator/QEMU bundle directly.
The sandbox must not be the default startup channel when a compliant host
channel is available.

- Prefer execute-in-place or an explicit process allowlist for the local
  emulator/QEMU executable.
- Run the executable from its installed local bundle path. Do not start it from
  a sandbox path that migrates, statically injects, copies, or re-signs child
  executables.
- On macOS, preserve the original QEMU code signature and
  `com.apple.security.hypervisor` entitlement.
- On Windows, preserve the local emulator/QEMU process context and native
  acceleration path; do not route startup through a sandbox that changes the
  executable or its process identity.
- This host-execution rule applies to emulator start on both platforms.
  Inspection, status, ADB, log, and artifact commands may continue in the
  current sandbox.
- Do not disable sandbox protection globally and do not use an unauthorized
  sandbox escape.

If startup reports `HVF error: HV_DENIED`:

1. Treat `HYPERVISOR_RUNTIME_DENIED` as recoverable orchestration state,
   not as a reason to end the agent session.
2. Do not retry in the same execution context.
3. Do not reinstall the emulator, clear quarantine, delete an AVD, or stop an
   unrelated emulator when the installed QEMU signature and Hypervisor
   entitlement are valid.
4. Wait for the failed QEMU process to exit and release the AVD lock.
5. Relaunch the same AVD through an authorized host channel that preserves the
   original QEMU code identity.
6. Poll `pico-cli emulator status --format json` and use its
   `data.adbOnline=true` field only to confirm that ADB is online. The status
   JSON does not contain `sys.boot_completed`.
7. After ADB is online, run `pico-cli shell getprop sys.boot_completed --device "$DEVICE_ID"` for the
   same target. Resume the user's original workflow only when that command
   returns `1`. If the same `emulator start --format json` response already has
   `data.bootCompleted=true`, it may be used as the ready signal directly.
8. If the host has no compliant execution channel, report a recoverable blocker
   with the exact AVD and status/shell commands. Keep the session and collected
   evidence available for continuation.

### 2. Use the real CLI surface

Always use the real `pico-cli` command names that exist in the repository. Do not invent wrapper commands or undocumented flags.

### 2.1 Recover from an unavailable AVD

Before starting a named AVD, use `pico-cli emulator list --format json` to
confirm that the requested name is currently available.

- If the requested AVD is available, start that exact name.
- If it is unavailable, do not call `emulator start` with the unavailable name.
- Use the `availableAvds` values from the structured failure result to choose a
  compatible AVD and retry the original start workflow.
- Prefer a candidate matching the requested version or platform. If several
  candidates remain and no deterministic choice is possible, ask the user to
  choose one.
- If no AVD is available, create or install one before retrying.

Preferred command families:

- `pico-cli emulator ...`
- `pico-cli device ...`
- `pico-cli app ...`
- `pico-cli files ...`
- `pico-cli capture ...`
- `pico-cli log`

Fallback:

- do not use `pico-cli adb logcat` for first-pass AI routing; use `pico-cli log` or `pico-cli app logcat` instead
- do not jump straight to plain `adb` unless the user explicitly asks for raw adb behavior

### 3. Respect device targeting

Many commands operate on the "preferred current device".

Selection priority:

1. explicit `--device <id>`
2. `PICO_CLI_DEVICE`
3. `ADB_SERIAL`
4. automatic selection by the CLI

When multiple devices may exist, prefer passing `--device <id>` explicitly instead of relying on implicit selection.
After selecting a target, bind its exact returned identifier as `DEVICE_ID` and preserve it for the
whole workflow. Every later device-scoped `shell`, `app`, `files`, `capture`, and `log` command must
pass `--device "$DEVICE_ID"`; rediscover and replace it only when the chosen device disconnects.

### 3.5 Spatial interaction limitation

- do not use `pico-cli shell input tap x y` to drive volumetric or spatial windows
- treat `shell input tap` as a 2D Android surface fallback only, such as launcher lists, standard settings pages, or flat app UI that is known to live on a normal screen buffer
- if the target flow depends on volumetric window interaction, spatial hit testing, controller rays, or hand-gesture style input, report that the current CLI cannot automate it reliably without simulator-side input support
- when this limitation blocks a verification flow, say so clearly instead of spending turns retrying different tap coordinates

### 4. Verify before and after

Before risky or multi-step operations:

- check environment or connectivity first
- verify the target emulator/device exists
- verify the expected output artifact or runtime state after execution

Typical preflight:

```bash
pico-cli emulator doctor --format json
pico-cli device list --format json
pico-cli emulator list --managed-only --format json
```

### 5. Prefer the least destructive path

Safe order:

- inspect
- create
- start
- operate
- collect evidence
- stop
- clean up only if requested

Do not delete emulator bundles, caches, or AVDs just to "reset everything" unless the user clearly requested cleanup.

## Command Map

When selecting commands or interpreting their results, load
[command-map.md](references/command-map.md) for emulator/device/app/capture/log
commands, result contracts, SDK-version handoff, and the raw ADB fallback.

## Scenario Playbooks

When the task needs a multi-step emulator/device operation, load the matching sequence in
[scenario-playbooks.md](references/scenario-playbooks.md), from readiness through cleanup.

## Safety Notes

### Destructive commands

Treat these as destructive. Show the concrete target set and obtain confirmation before using a
non-interactive confirmation flag such as `-y`, even when the user's initial request asked for
general cleanup:

- `pico-cli emulator delete`
- `pico-cli emulator delete-image`
- `pico-cli files rm`
- `pico-cli app uninstall`
- `pico-cli adb setprop`
- `pico-cli adb root`

### `emulator delete-image` caution

This command is intentionally limited to the PICO SDK bundle roots and the CLI download cache, but it is still destructive.

Before running it:

- stop the emulator first
- disclose that Windows cleanup can run `adb kill-server`, stopping the machine-wide shared ADB server for every client; other ADB users must reconnect afterward
- be extra careful on Windows, where `adb.exe` or Android Studio may still hold file locks
- do not run it as a generic troubleshooting shortcut

### `emulator start` caution

Before using `--watch`, make sure continuous recovery is actually needed and explain
that it keeps the command active. Use the standard one-shot Primer start path first.

### Emulator download patience

`pico-cli emulator start` or `pico-cli emulator install` may spend a long time downloading the emulator bundle.

- treat a long-running download as normal, especially when the machine is on Wi-Fi or a slower network
- a 10 minute download window is possible and does not mean the command failed
- do not report failure just because the command has been running for a while
- only treat the download as failed when the CLI returns an explicit failure result or error message
- if there is no failure result yet, assume the CLI is still downloading, verifying, or extracting
- when progress lines include a percentage such as `(... 35%)`, use that percentage when the user asks for progress
- if total bytes are shown, summarize progress in plain language, for example "about 35% downloaded"
- if the CLI only reports stage changes, explain the current stage honestly, such as "still downloading" or "now verifying files"

### Logging and watch mode

For long-running commands like:

- `pico-cli log --follow`
- `pico-cli app logcat --follow`
- `pico-cli app watch-crash ...`
- `pico-cli emulator start --watch`

Make sure the user asked for streaming/monitoring behavior or the debugging session truly needs it.

## Response Pattern

When using this skill, answer in this order:

1. state which emulator/device step you are performing
2. run the relevant `pico-cli` command(s)
3. report the actual outcome, not the intended outcome
4. if `HYPERVISOR_RUNTIME_DENIED` is returned, switch execution context,
   verify readiness, and continue the original workflow
5. if blocked, name the exact missing prerequisite or command failure
6. suggest the next smallest useful step

Never say the emulator is running, the APK is installed, or the screenshot/log was captured unless the command output confirms it.

If the emulator bundle is still downloading and no failure result has been returned yet, explicitly tell the user that the command is still in progress and that waiting is expected.

Never expose or invent internal emulator startup wait controls.
