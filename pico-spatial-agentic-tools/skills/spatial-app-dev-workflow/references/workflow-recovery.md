# Workflow Recovery and Handover

Read this when handling waiting/failure, changing goals, or switching execution
modes. Read public state before acting. Use installed `pico-cli` control help and
Workflow control and takeover reference for exact flags and schemas; do not edit private
Store files, checkpoints, status values, or completed markers.

## Choose from the observed state

| Observed situation                       | Next action                                                                                                                      |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Running, suitable valid guidance target  | Submit advice to that actual invocation; inspect its receipt and subsequent output.                                              |
| Pause request accepted but still running | Allow the active node/tools to reach a supported safe boundary. Observe with a finite budget; do not start a second writer.      |
| `waiting`, task `system:pause`           | Resume the same Run using the current revision and empty-object input when ready.                                                |
| `waiting`, business handoff              | Read the task's input schema and instructions, complete the requested work, and resume that task. Do not substitute pause input. |
| `waiting`, checkpoint-recovery handoff   | Read the failure reason, repair any stated prerequisite, then retry the failed node through that handoff.                        |
| Failed, cancelled, or completed          | Do not relabel as paused. Inspect preserved work; use direct continuation or a new Run when needed.                              |
| Delivery/cleanup unknown                 | Query the original identity and inspect execution facts. Do not automatically resend, reset, or start a replacement producer.    |

A node failure is not universally converted to a resumable pause. The actual
failure-recovery contract and public state determine whether a repair handoff is
available. Resume's `--task` identifies that waiting task; `--input` supplies its
schema-defined response. They are not a generic replacement request and state patch.

For a long invocation that times out or appears stuck in `running`, first read
[timeout and incomplete cleanup](workflow-limitations.md#long-invocations-timeout-and-incomplete-cleanup).
A stale `running` observation is not proof of progress or permission to start a
replacement writer.

## Timeout or interrupted execution still reports running

1. Read `pico-cli workflow run read <run-id> --format json` and recent events. Save the failure reason, current revision and existing reports/artifacts. A timeout does not erase project changes.
2. If waiting at `system:checkpoint-recovery`, use `pico-cli workflow resume <run-id> --revision <current-revision> --format json`. No task ID or empty input file is needed for this system recovery. Normal pause and business Handoffs still use their task/input schema.
3. If still `running` with uncertain cleanup, Resume explains why retry is blocked and what to do. A live Worker or lease is a reason to observe with a bounded budget. Expiry alone does not prove the ACP agent or tools stopped.
4. Confirm the old node's ACP/tools and any externally launched work have stopped, and inspect saved outputs and side effects. If you cannot establish this, report the blocker instead of guessing or killing a historical PID. Separately owned asset tasks keep their own lifecycle. After confirming:

   ```bash
   pico-cli workflow resume <run-id> --revision <current-revision> --confirm-stopped --format json
   ```

   Resume validates ownership and the pinned checkpoint, prepares the recovery point and launches the retry. If a hard-exited owner left a Store lock, follow the bounded wait instruction and read the current revision before retrying; do not delete locks. An interrupted response preserves any committed recovery point. Read the Run before retrying; a saved checkpoint-recovery Handoff can be resumed with its current revision.

5. After admission, verify continuation or a new waiting point. The interrupted node may repeat work; completed nodes and project files are preserved, but external side effects are not rolled back.

Cancellation cannot be undone. Unsupported packages, terminal Runs or invalid
checkpoints require a new Run or direct continuation with preserved project work,
after the old writer has stopped. A fixed package remains fixed; recovery does
not update an old embedded timeout or runtime implementation. Check installed
`workflow resume --help` for `--confirm-stopped`; diagnostics and these instructions
are the supported path, without private reconciliation calls or binary inspection.

## Pause, then resume the same Run

Inspect `control.pause.supported` in the installed descriptor. For dev's supported
serial LangGraph path, omitting a named target requests the next safe root-node
boundary. Named `--before` targets must be in the descriptor's `beforeNodes`;
cyclic nodes cannot be assumed to support this targeting.

After a pause request, wait until public state actually reports `waiting` and
`system:pause`. Save the new revision. Follow the installed resume contract with
an input file containing `{}`. Same-Run resume keeps the pinned package and
completed work; it does not upgrade the package or provide arbitrary state edits.
Verify continuation or the next handoff after resume admission.

Builder retains its session within the same Run, including across Workers after a
durable pause or business handoff and confirmed Host/guidance cleanup. With the
same Host/model selection, Resume loads that session when the Host supports it;
actually changing `--agent-tool` or `--agent-model` starts a new session while
preserving Run progress and artifacts. Repeating the same selection does not
replace the session. Neither path bypasses uncertain prior execution or cleanup;
an unavailable load reports a continuity error rather than silently starting fresh.
These rules do not recover the separate asset owner or arbitrary interrupted
tool side effects.

If a control command is interrupted, query its original request/Run before trying
again. Ctrl+C on the client does not prove an already accepted action was undone.
Cancellation is terminal; it is not a pause that can later be resumed.

## Agent returned without a final decision

P and Critic must confirm a control decision as well as return a report. A guided
continuation can omit that confirmation even after an earlier call made a decision.
The Run then waits at `system:checkpoint-recovery`; the public reason explains
that the report was saved but the final decision is missing. This is not a request
to reconstruct private receipts or edit Run state.

1. Read `pico-cli workflow run read <run-id> --format json` or the WebUI's Action required panel. Check the current waiting task, reason, revision, and recovery instructions.
2. When the task is `system:checkpoint-recovery` and its schema requires an empty object, save a file named `resume-input.json` containing `{}`. Use the displayed Resume command with the current revision:

   ```bash
   pico-cli workflow resume <run-id> --task system:checkpoint-recovery --revision <current-revision> --input resume-input.json
   ```

3. Read public state again after admission. Resume retries the failed node from its saved checkpoint; previously completed nodes and project files are preserved. P/C retries automatically receive their matching saved, unconsumed report so they can reuse valid work and confirm a decision through the new call's control context. An older receipt is not silently adopted.

Resume acceptance is not proof that the retry completed. If the same failure
recurs, inspect the new report and guide the active retry to confirm its decision.
Use a finite retry budget. If it cannot converge, preserve the useful outputs and
choose direct continuation or a new Run after resolving writer ownership as below.
These instructions do not make failed or cancelled Runs resumable, recover an
unconfirmed live writer, or upgrade the package pinned by an existing Run.

## Continue directly or start a new Run

Use this when the goal changes substantially, the Run fails or stops making useful
progress, results are poor, recovery is unavailable, or the user chooses another
execution mode. Selecting pico-cli's built-in `spatial-app-dev-workflow` earlier
does not require the rest of the task to use it. The caller can stop it and take
over directly within existing task authorization; starting another Run is optional.
Explain the change using that explicit product/workflow identity, and honor any
current explicit instruction to remain in managed execution. Avoid repeating the
same failing loop without a changed input, repaired prerequisite, or new evidence.

Leaving a Run does not mean losing development progress. Progress lives in the
project changes and durable outputs: code, assets, design documents, and verification
evidence. The Run's state and handover records help explain that work; they are not
the work itself. Do not keep an unrecoverable Run alive just to preserve progress.
Inspect and reuse the actual project, including uncommitted changes. If its handover
is missing or stale, reconstruct the next steps from those files and available
evidence, and identify any decisions that cannot be recovered. Preserve useful Run
records for context, but do not require its checkpoint history to continue development.

1. If execution is still active, pause and wait for the safe boundary or cancel and confirm the app writer and device activity stopped. For a terminal Run, check for residual work rather than trying to resume it. Resolve any independent asset owner and known Editor Runs separately. Record what remains active and who will own it; uncertain stopping blocks a competing writer.
2. Preserve the project files and write a project-local handover: current request, changed goal, accepted design and visual materials, code already written, build/runtime evidence, incomplete work, blockers, and asset/control references. Never copy private control tokens into shared reports.
3. For direct continuation, the current Agent reads that handover and continues the dev loop from the actual state.
4. For a new Run with usable design, use the supported input below. If the goal needs new planning/design, use the normal `planner` entry with the handover as material.
5. Keep the old Run identity for traceability. A new Run has fresh task/review history; files and evidence are reused, not imported as completed checkpoint state.

```json
{
  "request": "Continue the revised goal described in handover/next-development.md.",
  "projectRoot": "/absolute/path/to/project",
  "startAt": "impl-planner",
  "existingDesign": "The accepted design is documented in design/app.md. Read it with the change notes in handover/next-development.md.",
  "materials": ["design/app.md", "handover/next-development.md"]
}
```

Use real existing paths and summarize material changes in the request. A sentence
claiming a design exists cannot replace the referenced design. Starting a new Run
does not repair a lost Host connection, missing model, unavailable device, or
unrecoverable asset session. Resolve those prerequisites or report the limitation.

If the old Run is parked rather than cancelled, do not resume it against a project
changed by the new writer without reconciling ownership and the intervening work.

## Finish with evidence

Report the execution outcome separately from application acceptance. Give the
artifacts that can be reused, verified effects, remaining gaps, and the chosen
continuation path. Stop or explicitly transfer any independent tasks. Preserve
uncertain production state rather than claiming cleanup succeeded.
