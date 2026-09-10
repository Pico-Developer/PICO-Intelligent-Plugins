# Spatial Performance Analysis Tool Guide

All scripts in this file are located in the `scripts/` directory of the SKILL root directory, and the agent can execute them directly via bash. Please ensure adb is connected to the target device before execution.

This file is used for data capture, trace loading, diagnostic table query, and quick inspection in PICO OS6 performance analysis. When no trace, SQL result, or live report is available, prioritize obtaining minimum available evidence from here, then return to the main Skill routing to select the Spatial, Binder, Memory, or CPU scheduling workflow.

## pico-cli perf Commands Overview

Basic format:

```bash
pico-cli perf <resource> <action> [options]
```

| Command                           | Action                                                                              |
| --------------------------------- | ----------------------------------------------------------------------------------- |
| `pico-cli perf doctor check`      | Check if toolchains like `adb`, `trace_processor_shell`, etc. are available         |
| `pico-cli perf doctor install`    | Install missing perf toolchain                                                      |
| `pico-cli perf trace record`      | Capture Perfetto trace from device                                                  |
| `pico-cli perf daemon start`      | Start perf daemon required for trace loading, querying, and decoding                |
| `pico-cli perf daemon status`     | View daemon status, port, version, and active sessions                              |
| `pico-cli perf daemon stop`       | Stop perf daemon                                                                    |
| `pico-cli perf trace load <file>` | Load trace into an analysis session, with optional spatial app diagnosis            |
| `pico-cli perf trace query`       | Execute SQL query on a loaded session                                               |
| `pico-cli perf trace analysis`    | Run built-in trace analysis queries for frames, counters, and HTML overview reports |
| `pico-cli perf trace decode`      | Decode session to JSON, Markdown, text, or table                                    |
| `pico-cli perf live run`          | Generate performance inspection report based on real-time sampling                  |

## 1. Performance Data Capture

### Recommended: One-click Capture Script capture_perf_data.py

> **Invocation Method**: The agent can invoke this script by executing `python scripts/capture_perf_data.py --app <package> --duration <seconds> [-s <serial>] [--simple-perf-script <path>] [--output-root <dir>]` via `bash`.

`capture_perf_data.py` is used to start and stop multi-path performance capture at once, reducing time window inconsistency issues caused by manually executing commands separately. The script captures the following three types of data simultaneously:

| Data        | Output File                 | Description                                                                                                                             |
| ----------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| fast perf   | `fast-perf.json`            | Live performance report, suitable for quickly judging FPS, GPU, temperature, and jank overview                                          |
| trace perf  | `trace-perf.perfetto-trace` | Perfetto trace, used for subsequent session loading, querying SpatialFrames / Slice / scheduling evidence, etc.                         |
| simple perf | `simple-perf.data`          | simpleperf sampling results, used for analyzing hotspot functions and call stacks; enabled only when `--simple-perf-script` is provided |
| summary     | `collector-summary.yaml`    | Meta-information of this capture, output paths, file sizes, warnings, and limitations                                                   |

Internally, the script calls `pico-cli perf live start/stop` and `pico-cli perf trace record/stop`. If simpleperf is enabled, it also starts simpleperf sampling through the specified app profiler script and pulls `perf.data` after stopping.

#### Parameter Description

| Parameter                     | Required | Default Value | Description                                                                                               |
| ----------------------------- | -------- | ------------- | --------------------------------------------------------------------------------------------------------- |
| `--app <package>`             | Yes      | None          | Target application package name, e.g., `com.example.galaxian`                                             |
| `--serial <device>`           | No       | None          | ADB device serial number; when set, the script writes both `ANDROID_SERIAL` and `PICO_CLI_DEVICE`         |
| `--duration <seconds>`        | No       | None          | Automatic stop duration in seconds; if not passed, stop manually by `Ctrl+C` or SIGTERM                   |
| `--simple-perf-script <path>` | No       | None          | Path to `app_profiler.py`; skip simpleperf and only capture live + trace if not passed or path is invalid |
| `--output-root <dir>`         | No       | `.`           | Output root directory; the script creates a `perf-data-YYYYMMDD-HHMMSS` subdirectory under it             |
| `--python-cmd <python>`       | No       | `python`      | Python command used to execute the profiler script, e.g., `python3` or Python in a virtual environment    |

#### Typical Usage

Without simpleperf, capturing only fast perf and trace perf:

```bash
python scripts/capture_perf_data.py \
  --app com.picoxr.example \
  --serial <device_serial> \
  --duration 60 \
  --output-root ./session-output-<timestamp>/performance-data
```

With simpleperf, capturing fast perf, trace perf, and simple perf simultaneously:

```bash
python scripts/capture_perf_data.py \
  --app com.picoxr.example \
  --serial <device_serial> \
  --duration 60 \
  --simple-perf-script ./app_profiler.py \
  --python-cmd python3 \
  --output-root ./session-output-<timestamp>/performance-data
```

Manually controlling the stop time:

```bash
python scripts/capture_perf_data.py --app com.picoxr.example --output-root ./session-output-<timestamp>/performance-data
# Stop by pressing Ctrl+C after reproducing the problem
```

#### Output Directory and Files

Each run generates an independent directory, for example:

```text
session-output-<timestamp>/performance-data/perf-data-20260730-192400/
├── fast-perf.json
├── trace-perf.perfetto-trace
├── simple-perf.data
└── collector-summary.yaml
```

Explanation:

| File                        | When Generated                            | Purpose                                                                                     |
| --------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------- |
| `fast-perf.json`            | Mandatory                                 | Quickly inspect FPS, GPU, temperature, jank, and raw timeseries                             |
| `trace-perf.perfetto-trace` | Mandatory                                 | Load into perf daemon to execute SQL or Spatial diagnosis                                   |
| `simple-perf.data`          | Mandatory only when simpleperf is enabled | Analyze hotspot functions and call stacks in combination with simpleperf tools              |
| `collector-summary.yaml`    | Mandatory                                 | Record capture status, commands, version, output path, file size, warnings, and limitations |

If `--simple-perf-script` is not provided, `collector-summary.yaml` will mark simpleperf as not mandatory and record a `simpleperf_not_enabled` limitation. If `--duration` is less than 30 seconds or the duration is not fixed, corresponding limitations will also be recorded in the limitations section.

### pico-cli perf trace record: Capture Perfetto Trace

```bash
pico-cli perf trace record [options]
```

| Parameter                  | Default Value                | Description                                                                  |
| -------------------------- | ---------------------------- | ---------------------------------------------------------------------------- |
| `-t, --duration <seconds>` | `60`                         | Capture duration in seconds                                                  |
| `-o, --output <path>`      | trace file in temp directory | Output trace path                                                            |
| `-p, --pbtx <name\|path>`  | `default`                    | PBTX preset name or path to custom `.pbtx` file                              |
| `--detach`                 | `false`                      | Start daemon-managed detached recording and return a trace record session ID |
| `--port <port>`            | `9500`                       | Daemon port for `--detach` mode                                              |

Common examples:

```bash
pico-cli perf trace record --duration 45 -o ./trace-45s.perfetto-trace
pico-cli perf trace record --pbtx ./configs/custom.pbtx -o ./custom.perfetto-trace
pico-cli perf trace record --detach -o ./live.perfetto-trace
pico-cli perf trace stop <traceRecordSessionId>
```

Detached trace capture must preserve the `traceRecordSessionId` returned by
`trace record --detach`; `trace stop` requires that ID.

### pico-cli perf live run: Real-time Performance Inspection

```bash
pico-cli perf live run [options]
```

| Parameter                  | Description                                                               |
| -------------------------- | ------------------------------------------------------------------------- |
| `--app <package_name>`     | Target application package name, e.g., `com.picoxr.example`               |
| `--adb <path>`             | Path to adb executable, can override `ADB_PATH` / `PROFILER_ADB` / `PATH` |
| `--device <device_id>`     | Specify device ID when multiple devices are connected                     |
| `-o, --output <path>`      | Explicitly specify report output path, needs to be used with `--save`     |
| `-t, --duration <seconds>` | Fixed runtime duration, automatically stops when reached                  |
| `--report-mode`            | Print PASS/FAIL verdicts per sample and imply `--save`                    |
| `--save`                   | Save JSON report, default path is `reports/live-report-<ISO>.json`        |

Main fields of the live report:

| Field           | Description                                                                                  |
| --------------- | -------------------------------------------------------------------------------------------- |
| `metadata`      | App package name, capture duration, number of samples, generation time                       |
| `diagnosis`     | Rule-based FPS diagnostic conclusions, including `status`, `category`, `rule`, `jankReports` |
| `summary`       | Aggregated information for App FPS, SPR FPS, GPU Usage, GPU Temp                             |
| `rawTimeseries` | Raw per-sample time series data                                                              |

FPS diagnostic rules use sliding window aggregation, where `[89.5, 90]` is approximately treated as the 90 range:

| Condition                | Conclusion                                           |
| ------------------------ | ---------------------------------------------------- |
| `APP FPS < SPR FPS ≈ 90` | App process jank                                     |
| `APP FPS < SPR FPS < 90` | App jank, and may indirectly affect System / Runtime |
| `APP FPS ≈ SPR FPS ≈ 90` | No obvious performance issues found, PASS            |
| Other                    | UNKNOWN, need to continue analyzing `rawTimeseries`  |

## 2. Environment Check

Before formal capture, it is recommended to use this group of three scripts to confirm the device type, APK debuggable state, and target App foreground state, avoiding unusable traces or live reports due to environment mismatch.

### check_device.py: Check Physical Device / Emulator

> **Invocation Method**: The agent can invoke this script by executing `python scripts/check_device.py [-s <serial>] [--detail] [--json]` via `bash`.

The script determines whether the currently connected device is a physical device or an emulator via adb, and also checks whether it is a PICO Swan device and the PICO OS version.

| Parameter               | Required | Description                                                         |
| ----------------------- | -------- | ------------------------------------------------------------------- |
| `-s, --serial <device>` | No       | Device serial number; mandatory when multiple devices are connected |
| `--detail`              | No       | Output detailed judgment information                                |
| `--json`                | No       | Output results in JSON format                                       |

Typical usage:

```bash
python scripts/check_device.py -s <device_serial> --detail
python scripts/check_device.py -s <device_serial> --json
```

The output includes `final_verdict` (`real-device` / `emulator`), `confidence`, `is_pico_swan`, and `pico_os` (`PICO_OS6` / `NOT_PICO_OS6`). The judgment logic is based on weighted scores from dimensions such as `ro.kernel.qemu`, `ro.hardware`, `ro.product.model`, `ro.product.manufacturer`, `ro.product.device`, `ro.build.fingerprint`, etc.

### spatial_probe.py — Spatial Trace Availability Probe

Check whether the loaded Spatial trace contains key tables like `OpenXRClientSpatialFrames`, `SpatialMetrics`, and target processes/threads, and output a YAML report. The external entry for the script is still `probe_identities()`, which is internally split into three segments according to responsibilities: `probe_app_identity()`, `probe_spatial_runtime_identity()`, and `probe_threads()`. `probe_app_identity()` only detects the target App process (`--package` / `--app-process`) and parses the App frame driving thread, writing to `identities.target_app` and `identities.app_frame_driving_threads`; `probe_spatial_runtime_identity()` only detects `com.pico.spatial.runtime`, `com.pico.xr.openxr_runtime`, and `compositor` / `surfaceflinger` candidates, writing to `identities.spr`, `identities.openxr_runtime`, and `identities.compositor_candidates`; `probe_threads()` keeps the key thread search logic unchanged, writing to `identities.key_threads`.

```bash
python scripts/spatial_probe.py \
  --trace <path/to/trace.perfetto-trace> \
  --package <package>
```

Common parameters: `--detail` (complete report), `--output <file>` (for example `./session-output-<timestamp>/performance-data/trace-probe-detail.yaml`), `--strict` (block analysis if probe fails)

**Frame Driving Thread Convention**: Subsequent SQL and topic analysis must read the frame driving thread `utid` from `identities.app_frame_driving_threads.candidates[0].utid` in `trace-probe-detail.yaml`; hardcoding the thread name `main` is prohibited.

### run_query.py — Compatibility Trace Session SQL Query Tool

Execute arbitrary SQL on a trace session managed by pico-cli and output JSON results.
This helper is a thin wrapper around `pico-cli perf trace query`, useful when SQL
is easier to pass via stdin or a file. It does not import the Python `perfetto`
package and must not launch `trace_processor_shell` directly.

```bash
python scripts/run_query.py \
  --session <sessionId> \
  --sql "SELECT * FROM OpenXRClientSpatialFrames LIMIT 5"
```

Common parameters: `--sql-file <path>` (read from .sql file), `--out <file>` (output to file), `--daemon-port <port>`

### check_debuggable.py: Check APK debuggable

> **Invocation Method**: The agent can invoke this script by executing `python scripts/check_debuggable.py -s <serial> --app <package> [--detail] [--json]` via `bash`.

The script checks whether the Android App installed on the device is a debuggable version, which is suitable for confirming the APK type before capture.

| Parameter           | Required | Description                          |
| ------------------- | -------- | ------------------------------------ |
| `-s, --sn <device>` | Yes      | Device serial number                 |
| `--app <package>`   | Yes      | Target App package name              |
| `--detail`          | No       | Output detailed judgment information |
| `--json`            | No       | Output results in JSON format        |

Typical usage:

```bash
python scripts/check_debuggable.py -s <device_serial> --app com.picoxr.example
python scripts/check_debuggable.py -s <device_serial> --app com.picoxr.example --json
```

The output is `DEBUGGABLE`, `NOT_DEBUGGABLE`, or `UNKNOWN`. The judgment logic will check the `DEBUGGABLE` flag in `dumpsys package` and verify debuggability via the `run-as` command simultaneously; if either is true, it is judged as `DEBUGGABLE`.

### check_foreground.py: Check App Foreground Status

> **Invocation Method**: The agent can invoke this script by executing `python scripts/check_foreground.py -s <serial> [--app <package>] [--detail] [--json]` via `bash`.

The script queries currently foreground-running Apps, or checks whether a specific App is in the foreground by specifying the package name.

| Parameter           | Required | Description                                                                          |
| ------------------- | -------- | ------------------------------------------------------------------------------------ |
| `-s, --sn <device>` | Yes      | Device serial number                                                                 |
| `--app <package>`   | No       | When a target package name is specified, output whether the App is in the foreground |
| `--detail`          | No       | Output detailed judgment information                                                 |
| `--json`            | No       | Output results in JSON format                                                        |

Typical usage:

```bash
python scripts/check_foreground.py -s <device_serial> --detail
python scripts/check_foreground.py -s <device_serial> --app com.picoxr.example
```

When `--app` is not specified, output the list of foreground App package names; when `--app` is specified, output true / false. The judgment logic will query `dumpsys activity activities`, `dumpsys activity`, and `dumpsys window` in turn, extracting foreground package names from fields like `mResumedActivity` and `mFocusedApp`.

### pico-cli perf doctor check/install: Toolchain Check and Installation

| Command                                      | Description                      |
| -------------------------------------------- | -------------------------------- |
| `pico-cli perf doctor check`                 | Check all key tools              |
| `pico-cli perf doctor check --tool tps`      | Only check trace processor shell |
| `pico-cli perf doctor check --tool adb`      | Only check adb                   |
| `pico-cli perf doctor install --tool <tool>` | Install specified tool           |
| `pico-cli perf doctor install --all`         | Install all missing tools        |

## 3. Performance Data Analysis

### pico-cli perf daemon: Analysis Service Management

`trace load`, `trace query`, and `trace decode` all depend on the perf daemon. Start it before loading a trace and stop it after completion.

| Command                              | Description                            |
| ------------------------------------ | -------------------------------------- |
| `pico-cli perf daemon start`         | Start daemon using default port `9500` |
| `pico-cli perf daemon start -p 9500` | Start daemon on specified port         |
| `pico-cli perf daemon status`        | View daemon status                     |
| `pico-cli perf daemon stop`          | Stop daemon                            |

### pico-cli perf trace load: Load Trace and Enable Spatial Diagnosis

```bash
pico-cli perf trace load <traceFile> [options]
```

| Parameter                          | Default Value           | Description                                  |
| ---------------------------------- | ----------------------- | -------------------------------------------- |
| `<traceFile>`                      | None                    | Absolute path to trace file, mandatory       |
| `--shell <path>`                   | `trace_processor_shell` | Path to trace processor shell                |
| `-p, --port <port>`                | `9500`                  | Daemon port                                  |
| `--metrics-config <path>`          | None                    | Custom metrics configuration JSON            |
| `--rules-config <path>`            | None                    | Custom rules configuration JSON              |
| `--spatial-diagnose <true\|false>` | `false`                 | Whether to enable spatial app rule diagnosis |

After loading, the session will be alive for reuse when the daemon is active. The recommended loading method for Spatial analysis:

```bash
pico-cli perf trace load /abs/path/to/trace.perfetto-trace --spatial-diagnose true
```

After enabling `--spatial-diagnose true`, focus on querying these diagnostic tables:

| Table Name                          | Description                                                                         |
| ----------------------------------- | ----------------------------------------------------------------------------------- |
| `OpenXRClientSpatialFrames`         | Status of each spatial engine frame, such as Normal / Late / Miss / Discard / Early |
| `SpatialRuntimeAbnormalFrames`      | Abnormal frame burst windows                                                        |
| `SpatialBottleneckEvents`           | Potential bottleneck events identified by rules                                     |
| `SpatialBottleneckRuleSuggesstions` | Optimization suggestions corresponding to each bottleneck rule                      |
| `TargetAppMetricCounterStates`      | App-level metric snapshots, such as DrawCall, Triangle, etc.                        |
| `spatial_metrics_definitions`       | SpatialMetrics metric definitions                                                   |

### pico-cli perf trace query: Execute SQL Query

```bash
pico-cli perf trace query --session <sessionId> --sql "<SQL>"
pico-cli perf trace query --session <sessionId> --sql-file "<path_to_sql_file>"

```

| Parameter                | Default Value | Description                                                  |
| ------------------------ | ------------- | ------------------------------------------------------------ |
| `--session <id>`         | None          | Target session ID, mandatory                                 |
| `--sql <sql>`            | None          | SQL to be executed, mandatory                                |
| `--sql-file <query.sql>` | None          | Path to SQL file to execute, design for complex query        |
| `--execute`              | `false`       | Use `/execute` interface, suitable for non-SELECT statements |
| `-p, --port <port>`      | `9500`        | Daemon port                                                  |

Common SQL examples:

```bash
pico-cli perf trace query --session <sessionId> --sql "SELECT * FROM OpenXRClientSpatialFrames"
pico-cli perf trace query --session <sessionId> --sql "SELECT * FROM SpatialBottleneckEvents"
pico-cli perf trace query --session <sessionId> --sql "SELECT * FROM spatial_metrics_definitions"
```

To query abnormal frames, you can use:

```bash
pico-cli perf trace query \
  --session <sessionId> \
  --sql "SELECT * FROM OpenXRClientSpatialFrames WHERE name GLOB 'Late *' OR name GLOB 'Miss *' OR name GLOB 'Early *' OR name GLOB 'Discard *'"
```

### pico-cli perf trace analysis: Built-in Trace Analysis Queries

```bash
pico-cli perf trace analysis <query> [options]
```

Use built-in analysis queries when they match the investigation question; use
manual SQL through `trace query` for custom drill-downs or to validate specific
rows.

| Query                   | Description                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| `frame.appOverview`     | App frame overview statistics                                            |
| `frame.spatialOverview` | Spatial frame overview statistics                                        |
| `frame.appjanks`        | App jank frames                                                          |
| `frame.spatialjanks`    | Spatial abnormal frames                                                  |
| `frame.appSlowest`      | Slowest app frames                                                       |
| `frame.appBusyRunnings` | App jank frames whose main-thread Running state exceeds the frame budget |
| `frame.spatialSlowest`  | Slowest spatial frames                                                   |
| `counter`               | Process counter samples                                                  |
| `counter.spatialLoads`  | Default spatial load counter statistics for a spatial frame              |
| `report.overview`       | Combined HTML overview report                                            |

Common examples:

```bash
pico-cli perf trace analysis frame.appOverview --session <sessionId> --package <package>
pico-cli perf trace analysis frame.spatialjanks --session <sessionId> --table-format
pico-cli perf trace analysis report.overview --session <sessionId> --package <package> --output ./report.html
```

### Relationship with pico-cli Workflow

The one-click script is responsible for the parallelization and standardization of the "Capture Stage," and the output still goes back to the pico-cli analysis workflow:

```text
capture_perf_data.py
    -> fast-perf.json: Directly view live diagnosis / summary / rawTimeseries
    -> trace-perf.perfetto-trace: pico-cli perf daemon start
        -> pico-cli perf trace load --spatial-diagnose true
        -> pico-cli perf trace query
    -> simple-perf.data: Analyze hotspot functions and call stacks using simpleperf related tools
```

In other words, the script does not replace the analysis capabilities of `pico-cli perf`, but rather executes `pico-cli perf live start/stop` and `pico-cli perf trace record/stop` within the same capture window to ensure fast perf, trace perf, and simple perf are aligned as much as possible to the same reproduction scenario.

## Common Considerations

- In multi-device scenarios, use `--device`, `--serial`, `PICO_CLI_DEVICE`, or `ANDROID_SERIAL` to clearly identify the target device and avoid capturing the wrong device.
- Ensure the daemon is started before `trace load`, `trace query`, and `trace decode`.
- Do not directly invoke `trace_processor_shell` during normal analysis.
- If you want to suppress Node.js experimental warnings, set `NODE_NO_WARNINGS=1` before executing `pico-cli perf ...`.
- Use `pico-cli perf <resource> <action> --help` to view help for any sub-command.
