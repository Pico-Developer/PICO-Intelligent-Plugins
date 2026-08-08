# Perf CLI Usage

`Perf CLI` provides performance capture and analysis for PICO Spatial APP on connected devices. In this repository, invoke it through `pico-cli perf ...`.

## Command Overview

```bash
pico-cli perf <resource> <action> [options]
```

| Command | Description |
|---------|-------------|
| `pico-cli perf trace record` | Capture Perfetto trace from device |
| `pico-cli perf trace load <file>` | Load trace into a session; optionally run spatial diagnosis |
| `pico-cli perf trace query` | Execute SQL on a trace session |
| `pico-cli perf trace decode` | Decode trace data into other format |
| `pico-cli perf daemon start` | Start perf daemon |
| `pico-cli perf daemon stop` | Stop perf daemon |
| `pico-cli perf daemon status` | Check daemon status |
| `pico-cli perf live run` | Capture performance data onlive |
| `pico-cli perf doctor check` | Check the perf toolchains |
| `pico-cli perf doctor install` | Install the missing perf toolchains |

---

## trace record — Capture Perfetto Trace

Records a Perfetto trace from the connected device.

```bash
pico-cli perf trace record [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `-d, --duration <seconds>` | `30` | Capture duration in seconds |
| `-o, --out <path>` | `<tmpdir>/trace.pftrace` | Output file path |
| `--pbtx <name\|path>` | — | Preset name or path to pbtx config file |
| `--live` | `false` | Live recording mode; press Ctrl+C to stop |

### Examples

```bash
# 45-second capture to custom file
pico-cli perf trace record --duration 45 -o ./trace-45s.perfetto-trace

# Capture with custom pbtx config
pico-cli perf trace record --pbtx ./configs/custom.pbtx -o ./custom.perfetto-trace

# Live recording (stop with Ctrl+C)
pico-cli perf trace record --live -o ./live.perfetto-trace
```

---

## Daemon Management

The perf daemon serves trace analysis sessions. It must be running before `trace load`.

### daemon start

```bash
pico-cli perf daemon start [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `-p, --port <port>` | `9500` | Daemon listen port |

```bash
pico-cli perf daemon start
pico-cli perf daemon start -p 9500
```

### daemon stop

```bash
pico-cli perf daemon stop [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `-p, --port <port>` | `9500` | Daemon port |

```bash
pico-cli perf daemon stop
```

### daemon status

```bash
pico-cli perf daemon status [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `-p, --port <port>` | `9500` | Daemon port |

Returns daemon PID, port, version, and active sessions.

```bash
pico-cli perf daemon status
```

---

## trace load — Load Trace & Spatial Diagnosis

Loads a Perfetto trace file into a session and returns a session ID for subsequent `trace query` / `trace decode` operations. Optionally enables spatial app rule diagnosis.

```bash
pico-cli perf trace load <traceFile> [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `<traceFile>` | — | Absolute path to the trace file (required) |
| `--shell <path>` | `trace_processor_shell` | Path to trace_processor_shell binary |
| `-p, --port <port>` | `9500` | Daemon port |
| `--metrics-config <path>` | — | Custom metrics configuration JSON |
| `--rules-config <path>` | — | Custom rules configuration JSON |
| `--spatial-diagnose <true\|false>` | `false` | Enable spatial app rule diagnosis |

### Examples

```bash
# Basic load
pico-cli perf trace load /abs/path/to/trace.perfetto-trace

# Load with spatial diagnosis (recommended for full analysis)
pico-cli perf trace load /abs/path/to/trace.perfetto-trace --spatial-diagnose true

# Load with custom configs
pico-cli perf trace load /abs/path/to/trace.perfetto-trace \
  --spatial-diagnose true \
  --metrics-config ./metrics.json \
  --rules-config ./rules.json
```

### Spatial Diagnosis Tables

When `--spatial-diagnose true`, the following diagnostic tables become available:

| Table | Description |
|-------|-------------|
| `OpenXRClientSpatialFrames` | Frame status per spatial engine frame (Normal / Late / Miss / Discard / Early) |
| `SpatialRuntimeAbnormalFrames` | Abnormal frame burst windows |
| `SpatialBottleneckEvents` | Rule-detected potential bottlenecks |
| `SpatialBottleneckRuleSuggesstions` | Optimization suggestions per bottleneck rule |
| `TargetAppMetricCounterStates` | App-level metric counter snapshots (DrawCall, Triangle, etc.) |
| `spatial_metrics_definitions` | Spatial metric definitions |

---

## trace query — SQL Query on Session

Executes SQL queries against a loaded trace session.

```bash
pico-cli perf trace query [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--session <id>` | — | Target session ID (required) |
| `--sql <sql>` | — | SQL to execute (required) |
| `--execute` | `false` | Use `/execute` endpoint instead of `/query` |
| `-p, --port <port>` | `9500` | Daemon port |

### Examples

```bash
# Query spatial frames
pico-cli perf trace query \
  --session <sessionId> \
  --sql "SELECT * FROM OpenXRClientSpatialFrames"

# Query bottlenecks
pico-cli perf trace query \
  --session <sessionId> \
  --sql "SELECT * FROM SpatialBottleneckEvents"

# Query with execute (for non-SELECT statements)
pico-cli perf trace query \
  --session <sessionId> \
  --sql "CREATE VIEW ..." \
  --execute
```

---

## trace decode — Decode trace data

Decode trace data in various formats.

```bash
pico-cli perf trace decode [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--session <id>` | — | Target session ID (required) |
| `-o, --out <path>` | — | Output file path |
| `--format <type>` | `json` | Output format: `json`, `text`, `markdown`, `table` |
| `-p, --port <port>` | `9500` | Daemon port |

### Examples

```bash
# Decode as .json
pico-cli perf trace decode --session <sessionId> -o ./report.json

# Dxport as .systrace
pico-cli perf trace decode --session <sessionId> --format markdown -o ./report.systrace
```

---

## live run — capture performance data onlive

Collects real-time performance metrics for a fixed duration and outputs a structured report. Based on `adb logcat` data — suitable for fast performance inspection.

```bash
pico-cli perf live run [options]
```
| Option | Default | Description |
|  `--app <package_name>`    | - | Target app package name (e.g. com.picoxr.example)
|  `--adb <path>`            | - | Path to adb executable (optional, overrides ADB_PATH/PROFILER_ADB/PATH)
|  `--device <device_id>`    | - | Device ID to connect (if multiple connected)
|  `-o, --output <path>`     | - | Explicit report file path (requires --save)
|  `-d, --duration <seconds>`| - | Run for a fixed duration, then stop automatically
|  `--save`                  | - | Save the JSON report to the default path (reports/live-report-<ISO>.json)
|  `-h, --help`              | - | display help for command


### Examples

```bash
# 30-second live capture with terminal output and save into .json
pico-cli perf live run --app <your_app_package> --duration <seconds> --save --output <save_path>

### Report Structure

- **`metadata`**: app package, capture duration, sample count, generation timestamp
- **`diagnosis`**: rule-based FPS conclusions — `status`, `category`, `rule`, `jankReports`
- **`summary`**: aggregated App FPS, SPR FPS, GPU Usage, GPU Temp
- **`rawTimeseries`**: raw per-sample time-series data

### FPS Diagnostic Rules

Using sliding-window aggregation (`[89.5, 90]` ≈ `90` tier):

| Condition | Conclusion |
|-----------|------------|
| `APP FPS < SPR FPS ≈ 90` | App process is stuttering |
| `APP FPS < SPR FPS < 90` | App stuttering + possible indirect system impact |
| `APP FPS ≈ SPR FPS ≈ 90` | No performance issue (PASS) |
| Other | UNKNOWN — analyze `rawTimeseries` |

---

## doctor check - Check the perf toolchains

Check the perf toolchains(adb, trace_processor(tps)):
```bash
pico-cli perf doctor check [options]
`--tool <name>`：check single tool, such as `adb` / `tps`

# Examples:
# Check All
pico-cli perf doctor check
# Check trace_processor(tps)
pico-cli perf doctor check --tool tps
```

## doctor install - Install the missing perf toolchains

Install the missing toolchains for perf.
```bash
pico-cli perf doctor install [options]
```

options:
- `--tool <name>`：install single tool(`adb` / `tps`)
- `--all`：install all missing tools

Examples:
```shell
# install tps
pico-cli perf doctor install --tool tps
# install all
pico-cli perf doctor install --all
```


## Typical Analysis Workflow

```
1. Check or install toolchains
   ├── pico-cli perf doctor check
   └── pico-cli perf doctor install --tools xx (if missing)

2. Capture & Live (run in parallel)
   ├── pico-cli perf trace record --duration <seconds> --output <your_trace_output_path>
   └── pico-cli perf live run --app <pkg> --duration <seconds> --save --output <your_liveperf_output_path>

3. Start daemon
   └── pico-cli perf daemon start

4. Load trace with spatial diagnosis
   └── pico-cli perf trace load ./trace.perfetto-trace --spatial-diagnose true

5. Query & analyze
   ├── pico-cli perf trace query --session <id> --sql "SELECT ..."
   └── pico-cli perf trace decode --session <id> --output <your_findings_output_path>

6. Cleanup
   └── pico-cli perf daemon stop
```

---

## Notes

- Device selection: use `PICO_CLI_DEVICE` environment variable or `--device` where available.
- All trace analysis commands (`trace load`, `trace query`, `trace decode`) require a running daemon.
- To suppress Node.js experimental warnings:
  ```bash
  NODE_NO_WARNINGS=1 pico-cli perf ...
  ```
- For help on any subcommand: `pico-cli perf <resource> <action> --help`
