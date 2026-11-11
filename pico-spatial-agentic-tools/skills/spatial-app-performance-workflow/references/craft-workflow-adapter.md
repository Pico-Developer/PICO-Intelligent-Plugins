# Craft performance Workflow adapter

Use this entry when the user requests `pico-cli workflow` or a Craft-managed Run.
The `performance-workflow` adapter starts a native Profiler Session and bridges its lifecycle.

## Select the route and inputs

Discover the installed adapter and its input schema:

```bash
pico-cli workflow list --format json
pico-cli workflow describe performance-workflow --format json
```

If the installed catalog has no `performance-workflow` adapter, use the native
`pico-cli perf workflow` entry.

The Craft input file uses a short route and a nested `input` object. For existing-Trace analysis,
save `craft-input.json`:

```json
{
  "workflow": "analysis",
  "input": {
    "workspace": "<initialized-profiler-workspace>",
    "package": "<package-name>",
    "agentProvider": "<native-agent-provider>",
    "agentModel": "<native-agent-model>",
    "trace": "<trace-file>",
    "goal": "<analysis-goal>"
  }
}
```

Every route requires `workspace`, `package`, `agentProvider`, and `agentModel` in `input`.
Add the selected route's fields; the installed schema is authoritative:

| Craft route    | Native Workflow ID                         | Route inputs                                                         |
| -------------- | ------------------------------------------ | -------------------------------------------------------------------- |
| `analysis`     | `performance.workflow.analysis`            | Supply existing Trace evidence                                       |
| `capture`      | `performance.workflow.capture-performance` | `sourceDir`, `spatialPerfTraceConfig`                                |
| `codings`      | `performance.workflow.codings`             | `sourceDir`, `buildCommand`, `testCommand`                           |
| `diagnose-e2e` | `performance.workflow.diagnose-e2e`        | `sourceDir`, `buildCommand`, `testCommand`, `spatialPerfTraceConfig` |

Use `input.config` to forward a native `pspp.workflow-config/v2` file, including a captured
`inputs.spatialPerfTrace` manifest. Craft-required fields still belong in the nested `input`.
App Run settings use the schema's `appRunCommand`, `appRunScript`, or `appRunConfig` fields.
Manual capture requires `captureDurationSec` and excludes App Run fields.

Reuse an initialized Profiler Workspace, or create one before execution:

```bash
pico-cli perf workflow workspace init \
  --workspace <workspace> --project-id <project-id> --domain performance
```

Add `--source-dir <source-dir>` for source-based routes. For input preflight, use native
`pico-cli perf workflow prepare` with the selected native ID, config, and equivalent CLI overrides.
The adapter calls native `run` directly; it does not add a prepare step or accept a prepare preview
as its input file.

## Start and read the result

```bash
pico-cli workflow start performance-workflow --input <craft-input.json> --format json
pico-cli workflow wait <craft-run-id> --timeout-ms <milliseconds> --format json
pico-cli workflow result read <craft-run-id> --format json
```

Use the returned **Craft Run ID** for these commands. The adapter observes its native Session;
the IDs are separate. A wait timeout does not establish completion; continue observing the same Run.
Read the terminal result, native response, and registered artifacts before reporting analysis
or verification success.

To cancel, use `pico-cli workflow cancel <craft-run-id>`; the adapter stops the native Session
and waits for native cancellation. This adapter does not support Craft resume.
