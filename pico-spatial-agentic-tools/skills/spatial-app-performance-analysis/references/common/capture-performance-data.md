# Capture Performance Data

After session context collection is complete, first determine whether the user has provided analyzable data, then decide whether to follow the data capture branch or the primary analysis routing.

- **Trace / SQL / Screenshot / Diagnostic Table Result Available**: Enter "Analysis Workflow Routing" directly, and select the Spatial, Binder, Memory, or CPU scheduling workflow based on symptoms and evidence.
- **No Trace or No Trace Session Loaded**: Enter the data capture branch first, prioritizing the one-click capture script(`capture_perf_data.py`); if only a Perfetto trace is needed, use the manual pico-cli workflow. After obtaining SpatialFrames, SpatialMetrics, Perfetto Slice, FastPerf, Simpleperf, or a live report, return to "Analysis Workflow Routing".
- **Trace Available but Process / Thread Identities Not Confirmed**: First execute `spatial_probe.py --detail` to generate `trace-probe-detail.yaml`. The probe will separately detect the target App process and App frame driving thread via `probe_app_identity()`, and separately detect Spatial Runtime, OpenXR Runtime, and compositor candidates via `probe_spatial_runtime_identity()`, then unified scheduling will be performed by `probe_identities()` while maintaining output structure compatibility.

## Capture Confirmation Gate

Before running any on-device capture command (the one-click `capture_perf_data.py` script or the manual pico-cli trace workflow), confirm the command and its parameters with the user, and confirm the capture duration as its own explicit step. This gate is mandatory because capture runs against a live device, drives the target App, and takes real capture time; the user may also need to adjust parameters first. It is a normal turn in the session, not a hard stop; capture simply waits for confirmation before running.

Behavior:

1. Present the exact command you intend to run and the resolved parameters, so the user can confirm or modify them before execution:
   - Target app package (`--app`).
   - Capture duration in seconds (`--duration`).
   - Device serial (`-s`), when multiple devices are attached or a serial was resolved.
   - Output root (`--output-root`), defaulting to `./session-output-<timestamp>/performance-data`.
   - `pico-cli` executable (`--pico-cli`), when the default command is not on `PATH`. On Windows the default resolves `pico-cli.cmd` automatically.
   - Capture scope (one-click Perfetto + FastPerf + Simpleperf, or a Perfetto-only manual workflow).
2. Confirm the capture duration as its own explicit step, separately from the rest of the command. The duration directly bounds how much of the problem window the trace can contain, so it must not be silently accepted as part of a bulk "run as-is": call out the resolved `--duration` value on its own and ask the user to confirm or change it before proceeding. Only after the duration is explicitly confirmed do you treat the remaining parameters as a group.
3. Wait for the user to confirm the command or provide modified parameters before executing it. Apply any user-provided parameter changes and re-show the final command when they are substantive.
4. Prefer a structured confirmation capability when the host agent supports one (for example `AskUserQuestion`): first ask the user to confirm the capture duration as a dedicated question (offer the resolved value plus common alternatives such as shorter/longer, and an `Other` free-text option). Then offer the full resolved command as the default "run as-is" option, plus an option to adjust the remaining parameters (serial, scope, output). When the host has no such capability, present the duration on its own line for confirmation and then the command in plain text for the user to confirm or edit. Do not hard-depend on any specific tool being available.
5. Run the gate once per capture. Skip it only when the user has already explicitly authorized this exact capture command (including its parameters, duration included) in this session. If the parameters change afterwards, confirm again.
6. Before the reproduction step is required, remind the user to reproduce the problem scenario during the capture window so the trace actually contains the anomaly.
7. If the APK type is `NOT_DEBUGGABLE` (release build), state the evidence impact before capturing: system Perfetto trace, `SpatialFrames` / `SpatialMetrics`, and `fast-perf` are still available, but app-level `simpleperf` call-stack profiling may fail or be skipped. Continue without blocking (per the Environment Confirmation Gate rule), and record any missing app-level CPU stacks as a limitation instead of treating the absence as evidence.

**Recommended: One-click Capture Script** (Captures Perfetto trace + FastPerf + Simpleperf simultaneously):

```bash
python scripts/capture_perf_data.py \
  --app <package> \
  --duration <seconds> \
  -s <serial> \
  --output-root ./session-output-<timestamp>/performance-data
```

Output files are stored under `session-output-<timestamp>/performance-data/`, including `trace-perf.perfetto-trace`, `fast-perf.json`, and `collector-summary.yaml`.

See [tools.md](tools.md) for detailed parameters.

- **Only Phenomenon Description, No Evidence**: Output minimum data requirements first, prioritizing requests for trace or `pico-cli perf live run` results; do not provide root cause conclusions directly.

After data is ready, return to SKILL.md to enter the analysis workflow routing.
