# Profiler performance Workflow command reference

All Workflow commands use `pico-cli perf workflow`. Use installed help for unknown options or
version mismatches.

## Workflow inputs

Prefer one native config for reusable project settings. An existing-Trace analysis config is:

```json
{
  "schemaVersion": "pspp.workflow-config/v2",
  "workflow": "performance.workflow.analysis",
  "inputs": {
    "trace": "<trace-file>",
    "userIntent": {
      "goal": "<analysis-goal>"
    }
  }
}
```

Reuse optional `agentRuntime`, `agentRuntimes`, `agentSessions`, and `budget` from known project
configuration. `agentRuntime` uses `provider` and `model`; no separate Agent fields are required
merely to invoke the CLI.

| Workflow                                   | Practical inputs                                                                           |
| ------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `performance.workflow.analysis`            | Existing Trace; analysis goal                                                              |
| `performance.workflow.capture-performance` | `sourceDir`, `appRun`, `spatialPerfTraceConfig`                                            |
| `performance.workflow.codings`             | `sourceDir`, Trace evidence, repair goal, `buildCommand`, `testCommand`; optional `appRun` |
| `performance.workflow.diagnose-e2e`        | `sourceDir`, `spatialPerfTraceConfig`, `buildCommand`, `testCommand`, goal, and `appRun`   |

The CLI derives target package and goal from `--package` and `--goal`, normalizes Trace evidence,
and derives `gateAppRun` from `appRun`. The selected Workflow Contract and prepare diagnostics own
input validity; do not invent empty App Run commands for human-controlled capture.

Reuse an initialized Workspace. To create one for execution:

```bash
pico-cli perf workflow workspace init \
  --workspace <workspace> --project-id <project-id> --domain performance
```

Add `--source-dir <source-dir>` for source-based routes. Prepare alone requires no initialized
Workspace or running daemon.

### Prepare and run with consistent inputs

Every prepare and run requires explicit `--workspace` and `--package`, including config-based calls.
The config's `workflow` selects the Workflow ID. CLI input overrides win; config paths are relative
to the config directory, while CLI paths are relative to the current directory.

For analysis with no config, use the same inputs for both commands:

```bash
pico-cli perf --envelope workflow prepare performance.workflow.analysis \
  --workspace <workspace> --package <package-name> --trace <trace-file> --goal "<goal>"
# Only after success and data.ready are both true:
pico-cli perf --envelope workflow run performance.workflow.analysis \
  --workspace <workspace> --package <package-name> --trace <trace-file> --goal "<goal>"
```

- `success: false`: input resolution failed; `data` may be absent.
- `success: true`, `data.ready: false`: resolve `data.diagnostics`, even if exit code is 0.
- `success: true`, `data.ready: true`: inspect `data.resolved`; runtime availability is not verified.

The preview is `pspp.workflow-prepare/v1`; do not overwrite a `pspp.workflow-config/v2` config with it.
`--trace-session-id`, `--require-existing-daemon`, `--wait`, and `--wait-timeout-ms` are run-only.
For a loaded Trace session, prepare using its known Trace file and bind the session ID only at run.

## Capture-to-analysis handoff

After direct capture is finalized, use its stop/status result:

| Capture output                                                   | Analysis input                                             |
| ---------------------------------------------------------------- | ---------------------------------------------------------- |
| `data.output.trace` or `data.output.channels.perfetto.tracePath` | `--trace <captured-trace-file>` or config `inputs.trace`   |
| `data.output.spatialPerfTrace`                                   | Config `inputs.spatialPerfTrace`: copy the complete object |
| `data.output.spatialPerfTracePath`                               | Read this manifest file if the returned object is absent   |

Use the analysis config above, adding the complete manifest to `inputs.spatialPerfTrace`.
Carry the package/device into `--package`/`--device` and the scenario/window into the goal.
Resolve artifact paths from the capture output location. Prepare and run this config with the
same overrides. Passing only the Trace drops companion fast-perf evidence; preserve the
manifest's channel statuses and report paths.

Direct capture finishes as `completed`, `partial`, `blocked`, or `failed`. A readable Perfetto Trace
is needed for this Trace-based analysis; disclose companion-channel gaps when usable data is partial.
The capture ID belongs to `spatial-trace status/stop`; analysis returns a separate Workflow Session ID.

## Session results

Check envelope `success` before reading status. A failed query leaves completion unknown.
Observe the returned Session ID using `workflow status`; terminal states are `completed`, `partial`,
`failed`, `cancelled`, and `interrupted`. A `paused` Session needs resume or stop.

Read result artifacts from `data.runDir` and the final Session output. Report analysis findings,
Build/Test/App Run results, or the final performance-gate verdict for the selected goal. Disclose
skipped App Run verification; code verification alone does not prove performance improvement.

`--wait-timeout-ms` bounds a run's optional `--wait` without cancelling the Session.
To stop a Session, use `pico-cli perf --envelope workflow stop <workflow-session-id>`.
