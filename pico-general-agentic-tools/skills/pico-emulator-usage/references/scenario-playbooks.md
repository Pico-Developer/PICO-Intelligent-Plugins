## Scenario Playbooks

### Scenario 1: "I do not know whether the machine is ready"

Use:

```bash
pico-cli emulator doctor --format json
pico-cli emulator list --managed-only --format json
pico-cli device list --format json
```

Then:

- explain which prerequisite is missing
- recommend `emulator setup` only if the environment is not ready

### Scenario 2: "Create and launch a fresh emulator"

Use:

```bash
pico-cli emulator create --avd <name> -y
pico-cli emulator start --avd <name> --format json -y
pico-cli emulator status --format json
pico-cli device list --format json
```

On macOS, run the `emulator start` step through the compliant host execution
channel defined in Core Rule 1. Keep the remaining status and device checks in
the current session.

### Scenario 3: "Install and run an app for validation"

Use:

```bash
DEVICE_ID=<selected-device-id>
pico-cli app install <apk> --device "$DEVICE_ID"
pico-cli app launch <package> [--activity <activity>] --device "$DEVICE_ID"
pico-cli app logcat --package <package> --lines 200 --level E --device "$DEVICE_ID"
```

If the user wants visible evidence, hand off to `pico-cli-screenshot` with the selected
device ID and requested output path. That Skill owns target classification, capture mode,
and readable PNG validation. Use `capture-camera` when the request requires camera movement
or continuous recording; preserve the same device ID and let that Skill verify the evidence.

For a running app, `--package` scopes logs to its current PID. Bare `app logcat` is device-wide. For cross-process Spatial Runtime diagnosis, collect device-wide logs separately and correlate them with the app, PID and reproduction time.

### Scenario 4: "Collect crash/debug evidence"

Use:

```bash
DEVICE_ID=<selected-device-id>
pico-cli app watch-crash <package> --start --device "$DEVICE_ID"
# Device-wide evidence remains available after the app process has exited.
pico-cli app logcat --lines 300 --level E --device "$DEVICE_ID"
pico-cli emulator dump-logs --out <dir>
```

If visual evidence is required, hand off to `pico-cli-screenshot` with the
selected device context.

### Scenario 6: "Clean up what the CLI created"

First inspect the managed resources without deleting anything:

```bash
pico-cli emulator list --managed-only --format json
pico-cli emulator status --format json
pico-cli emulator delete-image --format json
```

Present the exact CLI-created AVDs, downloaded bundles, and caches proposed for deletion, then ask
the user to confirm that concrete scope. A broad request such as "clean up the emulator" is intent
to inspect and propose cleanup, not authorization to bypass this confirmation. The confirmation-required
result from the read-only `delete-image` preview is expected; retain its `data.targets` and
`data.planToken` as the bundle/cache scope. Pass that exact token when applying; if the CLI rejects
a stale plan, preview and confirm the changed scope again rather than dropping the token.
On Windows, the plan and confirmation must also disclose that bundle cleanup can run
`adb kill-server`, disconnecting every client of the machine-wide shared ADB server until it reconnects.

For a running AVD, first request confirmation for the exact stop target, run the stop, and verify it
is stopped. Then request a separate confirmation for deletion; do not combine both effects into one
advance confirmation:

```bash
pico-cli emulator stop --adb-device <id>
pico-cli emulator delete --avd <name> -y
```

Only include downloaded emulator bundles when the confirmed scope explicitly names them:

```bash
pico-cli emulator delete-image -y --plan-token <confirmed-preview-planToken>
```
