# pico-cli Conventions and Safety

Use this reference when a skill needs shared `pico-cli` operating rules without duplicating them in its own `SKILL.md`.

## Prefer High-Level Commands

Prefer the highest-level command family that matches the task:

1. `pico-cli emulator`, `device`, `app`, `files`, `capture`, `log`, `project`, or `perf`
2. `pico-cli shell` for shell-only operations on the preferred device
3. `pico-cli adb ...` only as an escape hatch
4. plain `adb` only when the user explicitly asks for raw ADB or `pico-cli` cannot cover the task

This keeps output, device selection, and safety behavior consistent across workflows.

## Device Targeting

Many commands operate on the preferred current device.

Selection priority is generally:

1. explicit `--device <id>` or `-d <id>` when the command supports it
2. `PICO_CLI_DEVICE`
3. `ADB_SERIAL`
4. automatic CLI/device selection

When multiple devices or emulators may exist, first inspect targets and then pass the target explicitly:

```bash
pico-cli device list --format json
pico-cli app info <package> --device <id> --format json
pico-cli capture screenshot --device <id> --out <path>
```

If a command uses a command-specific target flag such as `--adb-device`, use that documented flag rather than inventing `--device`.

## Output Format

Prefer structured output when a command supports it and the result will drive later decisions:

```bash
pico-cli doctor --format json
pico-cli device list --format json
pico-cli device info --format json
pico-cli emulator doctor --format json
pico-cli emulator status --format json
pico-cli app info <package> --format json
```

Use human-readable output when the user only wants a quick display or when the command does not support JSON.

Do not claim a JSON contract exists unless the command help or repository contract confirms it.

## Verify Before and After

Before multi-step or state-changing operations:

- inspect environment or connectivity first
- identify the target emulator/device/app/package
- choose explicit target flags when needed
- state whether the next command writes host state, device state, or runs for a long time

After operations:

- verify runtime state when possible
- verify host artifacts exist after screenshots, recordings, logs, or pulled files
- report actual command results, not intended results

Common preflight patterns:

```bash
pico-cli doctor --format json
pico-cli emulator doctor --format json
pico-cli emulator status --format json
pico-cli device list --format json
pico-cli app info <package> --format json
```

## Destructive Commands

Confirm intent unless the user explicitly requested the destructive action:

- `pico-cli emulator delete`
- `pico-cli emulator delete-image`
- `pico-cli files rm`
- `pico-cli app uninstall`
- `pico-cli adb setprop`
- `pico-cli adb root`
- any command using wipe/reset/delete options

Do not use destructive cleanup as a generic troubleshooting shortcut.

## Long-Running Commands

Use long-running commands only when the user asked for streaming/monitoring or the debugging session truly needs it:

- `pico-cli log --follow`
- `pico-cli app logcat --follow`
- `pico-cli app watch-crash ...`
- `pico-cli emulator start --watch`
- `pico-cli perf monitor ...`
- `pico-cli perf trace record ...`

For bounded captures, prefer explicit durations and output paths.

## Artifact Reporting

For screenshot, recording, trace, log, and pull operations:

- prefer an explicit local output path
- verify the file exists after the command
- report the exact path
- do not claim capture/pull succeeded based only on command intent

## Unknown Commands or Flags

When uncertain:

```bash
pico-cli --help
pico-cli <family> --help
pico-cli <family> <command> --help
```

Do not invent wrapper commands or undocumented flags. If a desired operation is missing, say which command family gets closest and whether the next fallback is `pico-cli adb` or a specialized skill.
