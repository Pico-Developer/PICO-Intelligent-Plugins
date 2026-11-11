# pico-cli Troubleshooting

Use this reference for first-pass diagnosis of generic `pico-cli` usage problems. Shared emulator,
device and APK operations belong to general's `pico-emulator-usage`; still capture belongs to
`pico-cli-screenshot`, and camera movement/recording to `capture-camera`. Only SDK/application
implementation and app-level performance interpretation need the configured platform's Skills.

## Start With the Exact Failure

Ask for or inspect:

- the full command that was run
- the complete error output
- the current working directory if the command depends on project layout
- target device/emulator state when the command touches a device
- host/plugin context when the command is about setup or skills

Do not diagnose from a paraphrase if the exact CLI error is available.

## Command Not Found

If `pico-cli` itself is unavailable, check Node.js and npm, then follow the public installation guide and run `pico-cli setup` once. When `pico-cli` runs, `pico-cli doctor --format json` reports the remaining setup, plugin, MCP, and toolchain gaps.

Useful checks:

```bash
node --version
npm --version
command -v pico-cli || echo "pico-cli not on PATH"
pico-cli --help
pico-cli --version
pico-cli doctor --format json
```

## Unknown Command or Option

Use help discovery instead of guessing:

```bash
pico-cli --help
pico-cli <family> --help
pico-cli <family> <command> --help
```

## Plugin, Skills, or MCP Not Visible

Start with:

```bash
pico-cli doctor --format json
pico-cli project detect --format json
```

- General Skills or MCP tools missing: inspect the current Host and the user-level setup records. Run `pico-cli setup` when doctor/detect confirms this Host is not configured; an absent tool list alone does not prove setup is missing.
- Platform Skills missing in a project: use project detect to check this Host's platform configuration. If absent, use `pico-project-setup`; if present, inspect the Host's Skill discovery/loading status.
- Installed content is outdated: run `pico-cli plugin update`. If the installed version is current but the session has stale content, use the Host's supported rediscovery or reconnect action.

After MCP registration changes, inspect Host status and approval requirements. Use supported discovery or a server-specific reconnect, then verify the advertised tools. Request a session reload only when that Host requires it to load the registration. Do not bypass approval or infer native tool availability from successful CLI setup.

## Device Not Found

Start with target discovery:

```bash
pico-cli device list --format json
pico-cli emulator status --format json
```

Then choose the narrowest next step:

- no emulator/device online -> run `pico-cli emulator doctor --format json`, then `pico-cli emulator start`; poll `pico-cli emulator status --format json` until `data.adbOnline === true` before using device commands. Do not treat top-level `status === "SUCCESS"` or `data.processRunning === true` as device readiness. If the workflow also requires Android boot completion, run `pico-cli shell getprop sys.boot_completed --device <id>` and wait for `1`.
- multiple devices -> rerun with explicit `--device <id>` / `-d <id>` where supported
- app-specific issue -> inspect `pico-cli app info <package> --format json`
- raw ADB-only issue -> consider `pico-cli adb devices` as an escape hatch

## Emulator Environment Not Ready

Use:

```bash
pico-cli emulator doctor --format json
```

If prerequisites are missing, follow the next actions it reports; `pico-cli doctor --fix` repairs the supported ones.

## App Install or Launch Fails

Use:

```bash
pico-cli device list --format json
pico-cli app info <package> --format json
pico-cli app launch <package> --activity <activity>
pico-cli app logcat --lines 200 --level E
```

If the failure is caused by SDK or app code, collect this CLI evidence first and then continue with the configured project's platform Skills; use `pico-project-setup` when the project is not configured yet.

## Capture or File Transfer Fails

Check:

- target device id
- local output path / permissions
- remote path existence
- whether the command wrote the expected host artifact

Useful commands:

```bash
pico-cli files stat <remote> --format json
```

For screenshots, hand off to `pico-cli-screenshot` with the same device and requested output path;
follow its target-specific capture mode and readable-PNG validation. File-transfer evidence still
requires checking the expected local artifact before reporting success.

## Performance Tooling Fails

For `pico-cli perf` failures, start with `pico-cli perf --envelope doctor check` and follow its next actions. Trace interpretation and app-level performance diagnosis belong to the configured project's platform Skills.

## SpatialML Command Fails

Load `spatialml-commands.md` if exact command or output details are needed; app integration belongs
to the configured project's platform Skills. Preserve the distinction between project detection, setup,
package installation, and the installed pySpatialML delegation boundary.

- Detection failure: verify `--project` is the actual Kotlin Spatial SDK project root. Unity failures
  belong to the Unity platform plugin.
- Setup returns `action-required`: complete the returned parent-SDK or SDK-owned handoff; do not fake
  readiness by creating marker files.
- `PSM_TOOL_UNAVAILABLE` with exit code `3`: `pipeline verify`, `model inspect`, or `model visualize`
  could not find a compatible pySpatialML executable. Install or update it with
  `uv tool install --upgrade --python 3.13 --system-certs 'pyspatialml-pico>=0.5.3'`, verify `pyspatialml --version` reports 0.5.3
  or newer, and ensure it is on `PATH`. If it is installed elsewhere, set
  `PICO_CLI_PYSPATIALML` to its executable path. Do not substitute legacy Docker/QNN/JSON tooling.

## Report Template

When reporting generic CLI troubleshooting, use:

1. **Observed failure**: exact command and error.
2. **Likely command family**: where the problem belongs.
3. **Inspection command**: the next read-only or low-risk command.
4. **Targeting/output note**: device id and `--format json` if relevant.
5. **Handoff**: `pico-cli doctor` for environment gaps, or `pico-project-setup` for project and SDK work.
