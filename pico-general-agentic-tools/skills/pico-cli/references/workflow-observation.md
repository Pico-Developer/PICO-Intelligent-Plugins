# Export and summarize Workflow observations

Use the public CLI's persisted event pages and Run/Result reads to inspect one explicit Run.
The companion [`summarize-workflow-events.mjs`](../scripts/summarize-workflow-events.mjs) ships
inside this `pico-cli` Skill in the public general plugin. It needs Node.js 20 or later and no
additional packages. Keep its companion `workflow-control-summary.mjs` beside the main script. Load the script through your Host's installed Skill resources; resolve its
local path before invoking it. Repository automation scripts are not required.

## Save a bounded export

Check your installed CLI's command help before exporting:

```bash
pico-cli workflow events read --help
pico-cli workflow run read --help
pico-cli workflow result read --help
```

Choose the Run ID explicitly. Save each response to a new file and preserve the original bytes.
Use shell noclobber, or another exclusive-create mechanism, to protect earlier exports:

```bash
set -C
WORKFLOW_RUN_ID=run-123e4567-e89b-42d3-a456-426614174000
pico-cli --version > cli-version.txt
pico-cli workflow run read "$WORKFLOW_RUN_ID" --format json > run.json
pico-cli workflow result read "$WORKFLOW_RUN_ID" --format json > result.json
pico-cli workflow events read "$WORKFLOW_RUN_ID" --after 0 --limit 1000 --format json > events-0001.json
```

`events read` returns a JSON object with `workflow`, `runId`, `events`, `nextCursor`, `hasMore`
and `terminal`. It accepts `--limit` from 1 through 1000. Inspect the page before continuing:

- If `hasMore` is true, use that page's `nextCursor` as the next `--after` and save to the next new
  file. For example, when `nextCursor` is 1000:

  ```bash
  pico-cli workflow events read "$WORKFLOW_RUN_ID" --after 1000 --limit 1000 --format json > events-0002.json
  ```

- Stop this export when `hasMore` is false. An active Run is complete only through this cursor;
  it may produce later events. Export a fresh snapshot separately when needed.
- If `hasMore` is true and the cursor does not advance, stop and report the export gap. Use a
  bounded number of page reads; never poll indefinitely.
- A missing persisted cursor or conflicting Run identity is an export failure. Keep the failed
  response alongside the successful pages for diagnosis.

For an active Run, `result read` may return `pico-workflow-result-read/v1` with `available: false`,
`runStatus` and `result: null`. Preserve that response. A terminal node event does not establish
that the entire Run succeeded. Read Run and Result again into new files after terminal publication.

Record the CLI version, Workflow name/version, Run ID, export time and file SHA-256 in a separate
receipt. On macOS use `shasum -a 256 <file>`; on Windows use PowerShell
`Get-FileHash -Algorithm SHA256 <file>`. Preserve any package identity/digest supplied by your
release receipt. The summarizer does not invent a missing package digest or export timestamp.

## Recompute offline

List page files explicitly in export order, starting at `--after 0`. Supply Run and Result files
when available. `--run` requires the Run export; `--result` requires the Result export or its
unavailable response. Swapping these file roles fails before output creation. The output path
must be new:

```bash
node "<installed-pico-cli-skill>/scripts/summarize-workflow-events.mjs" --help
node "<installed-pico-cli-skill>/scripts/summarize-workflow-events.mjs" \
  --output observations-summary.json --run run.json --result result.json \
  events-0001.json events-0002.json
```

For a one-page export, pass only that page. `--run` and `--result` are optional. Without them,
Run status and Result outcome stay unknown. An incomplete export ending in `hasMore: true` is
marked `exportComplete: false` and `degraded`; fetch the remaining pages before treating the
export as complete.

The script reads only the named files, performs no discovery or network access, and writes a
separate JSON file. It does not invoke a Host, change a Run, install tools or send telemetry.
Errors exit with code 1 and never overwrite an existing output. Interruption keeps the platform's
normal process signal behavior; no Workflow operation is started by this script.

## Read the fixed summary fields

| Field                             | Meaning                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `schemaVersion`                   | `pico-workflow-event-summary/v2`; an offline report version, independent of Runtime schemas.                                                                                                                                                                                                                                                                                                                                                                                                     |
| `workflow`, `runId`, `lastCursor` | Identity from the export and the highest contiguous persisted cursor. Mixed identities, cursor gaps, conflicting duplicate events, cursor regression and non-advancing pages fail. Exact repeated page files and overlapping identical events are deduplicated.                                                                                                                                                                                                                                  |
| `terminal`                        | Terminality from the last event page, plus the supplied authoritative Run status and Result outcome. Missing or unpublished results stay null.                                                                                                                                                                                                                                                                                                                                                   |
| `eventCoverage`                   | Coverage of persisted observations, including duplicate events, missing starts/finishes, missing visit/invocation IDs and unknown event types. Even an `observed` report cannot prove that best-effort producers persisted every observation.                                                                                                                                                                                                                                                    |
| `nodeVisits`                      | Separate observations for `nodeId`/`visitId` and replay. `durationMs` comes only from a completed node's reported duration; `observedElapsedMs` is the difference between recorded event timestamps. Incomplete nodes have no invented duration. Legacy events without visit IDs remain unpaired and degrade coverage.                                                                                                                                                                           |
| `agentInvocations`                | One record per `invocationId`, with task lifecycle, independent `accepted` and transport outcome, and known token fields. A transport completion does not fill in a missing task finish. Message or tool counts do not become invocation counts.                                                                                                                                                                                                                                                 |
| `observedUsage`                   | Sums of observed fields, with per-field coverage. Duplicate ACP turn reports are merged once per invocation; a conflicting numeric field is null/conflict for that invocation, with reported/unknown/conflict coverage; other statistics remain available. The completed `exec-jsonl` aggregate takes precedence over intermediate reports. Context-window reports are excluded from usage. Missing input/output/cache/reasoning/total fields stay null; partial sums remain explicitly partial. |
| `timing`                          | Union of completed Agent observation intervals, so overlapping Builders count once. Tool duration is already inside an Agent interval and is not added. This is persistence-time observation, not model inference time. Queue, inference and cost remain null.                                                                                                                                                                                                                                   |
| `classification`                  | Explicit observed replay executions. Business repair and report correction counts remain null pending the adopted receipt contract; graph back edges and repeated visits cannot establish either.                                                                                                                                                                                                                                                                                                |
| `unknownFields`                   | Fixed names for unknown quantities. The script does not estimate unreported tokens, queue time, inference or fees.                                                                                                                                                                                                                                                                                                                                                                               |

The summary uses a field whitelist and omits prompt/message text, tool outputs, artifact/source
paths, session scopes, Run errors and Result free text. Keep raw exports private by default; they
may contain user content and paths. Review declared Workflow/node/Agent identities before sharing
a summary. Attach original exports only when explicitly requested and after reviewing their content.

Real release acceptance still needs the final public package, a normal public installation and
an export from the same candidate's actual Run. Fixture exports establish the offline mechanism.

## Release accounting additions

`managedTasks` counts only parent task lifecycle records. Continuation Host calls retain distinct invocation IDs and explicit parentInvocationId; resultInvocationId points to the accepted final call. Usage and its coverage denominator count only real Host calls and then summarize those calls to the task, without adding task totals again. A task lifecycle without an original Host call does not become another usage observation. Missing/conflicting parent attribution remains a coverage gap; an orphan transport record does not become a managed task. The existing `agentInvocations.accepted` field records task acceptance when task lifecycle shares that identity. `acceptedOutput` records whether the actual call supplied the accepted final output: it is attributed only through the matching task `resultInvocationId`, stays null for missing provenance, and does not relabel the original call output when a continuation was adopted.

`control.counts` contains pauseRequestedCount, effectivePauseCount, pauseReleasedCount, pauseMissedCount, resumeAcceptedCount, resumeContinuedCount and cancelledRunCount. Counts consume the fixed committed control publications; an ordinary node.started, Host session event, pending publication hint or terminal status does not prove resumed execution. Missing or invalid publications remain null for the affected metrics. An authoritative terminal Result and a terminal final page with `hasMore: false` prove absent control activities as zero only when `pendingControlPublications` is zero. Current exports use `pendingControlPublications: null` when metadata is unreadable; this keeps the affected absent control counts unknown. A legacy page without that field also requires a persisted `run.completed` event; explicit unknown or positive pending remains unknown. Resume acceptance still requires a matching first-node publication. Control facts must come from `workflow-runtime/control`. Event reads are purely observational; only the owning write path can reconcile pending publications.

The business classification mapping is still not adopted in this checkpoint. `classification.deliveryComplete=false` explicitly prevents null repair/correction counts from being claimed as complete release accounting. A final adopted workflow mapping and effective coverage are required before acceptance.

This v2 implementation extends the earlier reviewed mechanism. Its changed calculations require independent Review and applicable regression evidence; the prior mechanism Review alone does not cover them. Fixed summaries still omit messages, prompts, tool output, source paths and session scopes. Offline export does not enable public automatic transmission.
