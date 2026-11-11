## Command Map

### Stable result contract

Use the pico-cli tool-result envelope rather than parsing Primer output directly.
Keep reading data.avds[].name and iniPath for instance selection,
data.processRunning / data.adbOnline for status, and data.avd,
data.adbDeviceId, data.bundleVersion, and data.bootCompleted after start.
A PARTIAL start result is not ready: inspect diagnostics and poll the same target;
do not start another instance automatically. Emulator start is delegated to Primer;
native-only executable, port, wipe, kernel, extra-argument, and log-path overrides
are not supported. `--watch` and custom-name creation remain available.

### SDK Version Handoff

When the calling SDK workflow supplies a selected SDK `major.minor` line, treat
that line as an explicit emulator bundle requirement. Do not allow
`emulator create` or `emulator start` to silently select an unrelated
installed or latest bundle.

```bash
pico-cli emulator install --version <major.minor> -y
pico-cli emulator create --version <major.minor> -y
pico-cli emulator start --version <major.minor> --format json -y
```

- The CLI selects the download source automatically based on build channel and
  host region.
- Verify the returned `bundleVersion` matches the selected `major.minor` line
  after normalizing both values to `major.minor`. For example, returned
  `0.11.0` matches selected `0.11`; returned `0.12.0` does not.
- Record the returned managed AVD before handing runtime evidence back to
  the calling SDK workflow.

### Emulator Lifecycle

Use these for environment validation and emulator lifecycle control:

- `pico-cli emulator doctor`
  - Checks PICO SDK and emulator prerequisites
  - Android Studio is not an emulator doctor check; install or inspect it only for an Android Studio plugin workflow
  - Use first when setup health is unknown
- `pico-cli emulator setup`
  - Reports prerequisite state through read-only storage inspection and guides the user to `doctor --fix`, `emulator install`, or `emulator create`; it does not migrate storage or perform provisioning itself
  - Use when prerequisites are missing and the user wants help fixing the machine
- `pico-cli emulator list`
  - Lists available AVDs
  - Use `--managed-only` to focus on CLI-created PICO emulator AVDs
- `pico-cli emulator create`
  - Creates a PICO emulator AVD without launching it
  - Use when the user wants a persistent emulator instance created ahead of time
- `pico-cli emulator start`
  - Starts a chosen AVD and can download the emulator bundle if missing
  - Use when the user needs a runnable emulator session
  - Keep using pico-cli for boot readiness, device selection, custom launch options and watch mode
  - To create another instance, use pico-cli emulator start --version <major.minor> --new-instance --format json -y
  - Use `--version <major.minor>` to pin the emulator bundle; it matches an installed bundle first and downloads it when missing
- `pico-cli emulator status`
  - Checks process and adb visibility
  - Use before start/stop if state is unclear
- `pico-cli emulator stop`
  - Stops the running emulator
- `pico-cli emulator delete`
  - Deletes stopped CLI-created PICO AVDs; it rejects a target that is still running
  - Run a separate explicit `pico-cli emulator stop`, verify the target stopped, then request separate confirmation for deletion
  - Prefer `--avd <name>` for precise cleanup
- `pico-cli emulator log [avd] --last`
  - Read the latest Primer launch log directly; omit `avd` to target the current running emulator or the sole managed AVD. Use dump-logs for an exported evidence bundle
- `pico-cli emulator dump-logs`
  - Collects emulator-related logs for crash/debug analysis
- `pico-cli emulator delete-image`
  - Deletes downloaded PICO emulator bundle roots and download cache
  - Treat as destructive; use only with explicit user consent

Common examples:

```bash
pico-cli emulator doctor --format json
pico-cli emulator list --managed-only --format json
pico-cli emulator create --avd Pico_Emulator_0_11 -y
pico-cli emulator start --avd Pico_Emulator_0_11 --format json -y
pico-cli emulator status --format json
pico-cli emulator dump-logs --out /tmp/pico-cli-sim-logs
```

### Device Inspection

Use these when the task is about the currently connected emulator/device rather than emulator lifecycle itself:

- `pico-cli device list`
- `pico-cli device connect <address>`
- `pico-cli device disconnect <host:port>`
- `pico-cli device disconnect --all`
  - These forms are mutually exclusive. Never omit both selectors or combine them.
  - `--all` disconnects every TCP/IP ADB device; use it only when broad disconnection is explicitly intended.
- `pico-cli device info`
- `pico-cli device battery`
- `pico-cli device props`
- `pico-cli shell [commands...]`
  - If no device is online, run `pico-cli emulator start` explicitly, wait for it to become ready, then retry the shell command
  - Do not imply that `pico-cli shell` bootstraps a managed AVD implicitly
  - Do not use `pico-cli shell input tap x y` for volumetric windows or spatial containers; it only injects 2D screen coordinates and is not a reliable path to enter gameplay or other spatial states

Examples:

```bash
pico-cli device list --format json
pico-cli device info --format json
pico-cli device battery --format json
pico-cli device props --filter pico --format plain
pico-cli shell getprop ro.product.model --device "$DEVICE_ID"
```

### App Operations

Use these after the target emulator/device is online:

- `pico-cli app install <apk>`
- `pico-cli app list`
- `pico-cli app info <package>`
- `pico-cli app launch <package> [--activity <activity>]`
- `pico-cli app stop <package>`
- `pico-cli app uninstall <package>`
- `pico-cli app logcat`
- `pico-cli app watch-crash <package>`

Examples:

```bash
pico-cli app install app/build/outputs/apk/debug/app-debug.apk --device "$DEVICE_ID"
pico-cli app info com.example.spatialdemo --format json --device "$DEVICE_ID"
pico-cli app launch com.example.spatialdemo --activity .platform.LaunchActivity --device "$DEVICE_ID"
pico-cli app logcat --package com.example.spatialdemo --lines 200 --level E --device "$DEVICE_ID"
pico-cli app watch-crash com.example.spatialdemo --start --interval 2 --device "$DEVICE_ID"
```

Important:

- if plain package launch fails, retry with `--activity`
- `app logcat --package` requires a running app and scopes to its current PID. Bare `app logcat` is device-wide; use it deliberately for system/cross-process diagnosis or after a crash, and correlate records with the package, PID and reproduction time.
- do not claim install or launch succeeded unless the command actually succeeded
- when an upstream app workflow requests connected instrumentation or liveness validation, this skill owns the device-scoped execution after the target is online. Run the project's existing Gradle wrapper task (for example `connectedAndroidTest`) against the selected target, return its exit result and device diagnostics or blocker, and leave test authoring and app/build repair to the upstream workflow.

### Files and Capture

Use these for moving assets, inspecting runtime files, and collecting visual evidence:

- `pico-cli files push <local> <remote>`
- `pico-cli files pull <remote> [local]`
- `pico-cli files ls [remote]`
- `pico-cli files mkdir <remote>`
- `pico-cli files rm <remote>`
- `pico-cli files cat <remote>`
- `pico-cli files stat <remote>`
- `pico-cli capture screenshot`
- `pico-cli capture record`

Capture guidance:

- hand every screenshot request to `pico-cli-screenshot`, which owns target classification, screenshot
  mode selection, the ADB fallback, and readable PNG validation
- hand camera movement or continuous recording to `capture-camera`, which owns the camera
  plan, recording execution, and artifact verification
- preserve the selected device ID, requested output path, and any explicit overwrite permission
  in either handoff; this skill supplies emulator/device readiness and lifecycle context
- the `capture screenshot` and `capture record` command families remain shared CLI capabilities;
  follow the owning capture Skill for their task-specific commands and verification

Examples:

```bash
pico-cli files mkdir /sdcard/Download/demo-assets --device "$DEVICE_ID"
pico-cli files push ./local.png /sdcard/Download/demo-assets/local.png --device "$DEVICE_ID"
pico-cli files ls /sdcard/Download/demo-assets -l --device "$DEVICE_ID"
pico-cli files stat /sdcard/Download/demo-assets/local.png --format json --device "$DEVICE_ID"
```

### Logs and Raw ADB Escape Hatch

Use these when the user needs low-level diagnostics:

- `pico-cli log`
- `pico-cli shell`
- `pico-cli log`
- `pico-cli app logcat`
- `pico-cli device props`

Prefer `pico-cli log` or `pico-cli app logcat` before any lower-level fallback. Do not route AI through `pico-cli adb logcat` first.

Examples:

```bash
pico-cli log --lines 150 --tag AndroidRuntime --level E --device "$DEVICE_ID"
pico-cli device props --filter ro.build.version.release --device "$DEVICE_ID"
pico-cli app logcat --lines 200 --level W --device "$DEVICE_ID"
```
