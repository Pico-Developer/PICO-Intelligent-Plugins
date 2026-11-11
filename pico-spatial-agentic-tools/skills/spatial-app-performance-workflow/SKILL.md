---
name: spatial-app-performance-workflow
description: 'Entry Skill for PICO Spatial performance investigation, capture, Trace analysis, source repair, and end-to-end diagnosis. Use for jank, frame drops, high CPU/GPU load, performance input preparation, native pico-cli perf workflows, or the Craft adapter. Route deeper evidence interpretation to spatial-app-performance-analysis. NOT for app feature development or environment setup — use spatial-app-dev-workflow or pico-env-doctor.'
license: 'Apache-2.0'
---

# Spatial App Performance Workflow

Default to `pico-cli perf workflow`: select a Workflow, prepare its inputs,
run when ready, and read the result. The Workflows implement analysis, App Run, repair, and evaluation.

## When to Use

- Investigate Spatial app jank, frame drops, high CPU/GPU load, or Trace findings.
- Prepare performance inputs or capture data from an app the user operates.
- Invoke a Workflow for capture, analysis, source repair, or end-to-end diagnosis.

## When NOT to Use

- App feature development — use `spatial-app-dev-workflow`.
- Environment setup or CLI diagnostics — use `pico-env-doctor`.

## Workflow

### Choose the route

| User goal                                                             | Entry / Workflow ID                                       |
| --------------------------------------------------------------------- | --------------------------------------------------------- |
| Prepare or validate inputs without execution                          | `workflow prepare` for the selected Workflow              |
| Capture performance data on a human-controlled app                    | Direct `spatial-trace`                                    |
| Capture performance data on a human-controlled app, and then analyze  | `spatial-trace` command → `performance.workflow.analysis` |
| Capture performance data with Workflow-controlled App Run             | `performance.workflow.capture-performance`                |
| Analyze existing performance data                                     | `performance.workflow.analysis`                           |
| Repair performance issue in source code and verify Build/Test/App Run | `performance.workflow.codings`                            |
| Diagnose, repair, recapture performance data, and evaluate results    | `performance.workflow.diagnose-e2e`                       |

`codings` verifies source repairs; choose `diagnose-e2e` when the goal also requires recapture
and a performance evaluation.

For `pico-cli workflow` or Craft-managed execution, load
[Craft adapter usage](references/craft-workflow-adapter.md) for route mapping, input, and invocation.

### Composition examples

For goals spanning multiple stages, compose supported `perf` commands and Workflows.
If analysis is requested without data, check for existing evidence before planning capture.

| User request                                         | Selection condition                                                       | Composition                                                                  |
| ---------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Analyze performance, but no usable data is available | Workflow can drive the requested scenario using an App Run command/script | `performance.workflow.capture-performance` → `performance.workflow.analysis` |
| Capture and analyze an app the user has launched     | The user controls navigation and scenario execution                       | `spatial-trace` command → `performance.workflow.analysis`                    |
| Investigate remaining findings after a Workflow      | Detailed root-cause analysis or targeted Trace SQL is needed              | Selected Workflow → `spatial-app-performance-analysis`                       |

Use the same principle for other supported combinations. Reuse known commands/scripts,
clarify only missing choices, and carry completed capture evidence into analysis.

### Prepare and invoke the selected Workflow

Load [Workflow inputs](references/workflow-command-reference.md#workflow-inputs) for config examples
and route requirements. Reuse project inputs, commands, and Agent settings; ask only for missing
decisions. Execution needs an initialized Workspace; preparation-only requests skip initialization.

```bash
pico-cli perf --envelope workflow prepare \
  --workspace <workspace> --package <package-name> --config <workflow-config.json>
```

Check `success`, then `data.ready`. Resolve `data.diagnostics` and retry after inputs change;
**run only when both are true**. Prepare checks static inputs; confirm selected files and runtime
prerequisites that remain unknown. For preparation-only requests, return readiness and stop here.

Run with the **same config and input overrides**:

```bash
pico-cli perf --envelope workflow run \
  --workspace <workspace> --package <package-name> --config <workflow-config.json>
pico-cli perf --envelope workflow status <workflow-session-id> --workspace <workspace>
```

Retain `data.sessionId` and `data.runDir`; observe the same Session until terminal and read its
result artifacts. Alternatively, add `--wait` to run. A query failure or wait timeout does not
establish completion or justify a new run. See [Session results](references/workflow-command-reference.md#session-results).

### Capture an app the user operates

Use direct capture when the developer has already started the app. Confirm the device, package,
scenario, and sampling window, then record while the user performs the scenario:

```bash
pico-cli perf --envelope spatial-trace start \
  --channel perfetto,fast-perf --package <package-name> \
  --device <serial> --output-dir <output-dir>
pico-cli perf --envelope spatial-trace status <capture-id>
pico-cli perf --envelope spatial-trace stop <capture-id>
```

Check `success` and retain `data.captureId`. Stop after the user's completion signal or the
agreed sampling window; read status until capture is finalized. This command records the app
without installing or launching it.

For **capture and analysis**, carry the captured Trace and full multi-channel manifest into
`performance.workflow.analysis` using [Capture-to-analysis handoff](references/workflow-command-reference.md#capture-to-analysis-handoff).
Then prepare, run, and observe the analysis Workflow as above.

### Hand off further evidence analysis

Use the Workflow's findings directly when they satisfy the request. For deeper root-cause
investigation, targeted SQL, or a detailed evidence report, route to `spatial-app-performance-analysis`
after the selected stage. Pass the Trace/full capture manifest, package/device, scenario/window,
Workflow result and artifacts, and the remaining question. Reuse completed context and capture.

For an explicit SQL-only or evidence-only request, this Skill can hand the supplied evidence directly
to `spatial-app-performance-analysis`; no new Workflow Run is required. If new data is needed,
select its capture route here.

## Verification

- Preparation: report `ready` and remaining diagnostics.
- Capture: return finalized artifacts and actual sampling window; disclose partial or failed channels.
- Workflow: read the terminal result and its requested analysis, Build/Test/App Run, or evaluation
  outputs. A successful command submission alone does not establish task success.
