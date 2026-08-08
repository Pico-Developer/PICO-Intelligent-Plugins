# pico-cli Troubleshooting

Use this reference for first-pass diagnosis of generic `pico-cli` usage problems. Route to a specialized skill once the problem belongs to emulator/device/app/perf/project work.

## Start With the Exact Failure

Ask for or inspect:

- the full command that was run
- the complete error output
- the current working directory if the command depends on project layout
- target device/emulator state when the command touches a device
- host/plugin context when the command is about setup or skills

Do not diagnose from a paraphrase if the exact CLI error is available.

## Command Not Found

If `pico-cli` itself is unavailable, route the environment repair through `pico-env-doctor`. That skill owns the verify-first flow for Node/npm checks, public install guidance, version checks, plugin setup, and MCP readiness.

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

Route to `pico-env-doctor` when the problem is host setup, missing skills, stale plugin content, or `pico-dev-knowledge` MCP connectivity. That skill checks the installed CLI version, discovers supported setup/plugin/MCP commands before using doctor-style checks, repairs with `pico-cli setup` / `pico-cli plugin update`, and reminds the user to restart the host or open a new session after `.mcp.json` changes.

For support bundles after setup remains broken, prefer metadata-only audit first:

```bash
pico-cli plugin audit
```

## Device Not Found

Start with target discovery:

```bash
pico-cli device list --format json
pico-cli emulator status --format json
```

Then choose the narrowest next step:

- no emulator/device online -> route emulator lifecycle work to `spatial-emulator-usage`
- multiple devices -> rerun with explicit `--device <id>` / `-d <id>` where supported
- app-specific issue -> inspect `pico-cli app info <package> --format json`
- raw ADB-only issue -> consider `pico-cli adb devices` as an escape hatch

## Emulator Environment Not Ready

Use:

```bash
pico-cli emulator doctor --format json
```

If prerequisites are missing and the user wants to fix local emulator setup, route to `spatial-emulator-usage`.

## App Install or Launch Fails

Use:

```bash
pico-cli device list --format json
pico-cli app info <package> --format json
pico-cli app launch <package> --activity <activity>
pico-cli app logcat --lines 200 --level E
```

Route end-to-end diagnosis to `spatial-emulator-usage`. If the failure is caused by SDK/app code, switch to the relevant SDK or migration skill after collecting CLI evidence.

## Capture or File Transfer Fails

Check:

- target device id
- local output path / permissions
- remote path existence
- whether the command wrote the expected host artifact

Useful commands:

```bash
pico-cli files stat <remote> --format json
pico-cli capture screenshot --device <id> --out <path>
```

Route execution workflows to `spatial-emulator-usage`.

## Performance Tooling Fails

For `pico-cli perf` failures, route to `spatial-app-perf-diagnose`. That skill owns profiler toolchain setup, real-time diagnosis, trace capture, trace loading, and Perfetto query interpretation.

## Report Template

When reporting generic CLI troubleshooting, use:

1. **Observed failure**: exact command and error.
2. **Likely command family**: where the problem belongs.
3. **Inspection command**: the next read-only or low-risk command.
4. **Targeting/output note**: device id and `--format json` if relevant.
5. **Handoff**: specialized skill if the issue needs end-to-end execution.
