# Workflow control and takeover

Use the installed CLI and the pinned Run's public contracts. Begin with `pico-cli workflow describe <name> --format json`, then `pico-cli workflow run read <run-id> --format json`. Do not edit private checkpoints or Store files.

## Observe a Run with a time budget

`run read` and `events read` return one observation. `workflow wait --timeout-ms <milliseconds>` and `events follow` wait for terminal completion; **waiting is not terminal**, so these commands do not hand control back just because a Handoff appears. Use bounded `run read` polling, with a finite overall deadline and a delay between reads. Stop polling to handle `waiting`; report the current Run and Handoff when the budget expires. Do not leave an unbounded background waiter.

For a waiting Run, read `waiting.handoff.kind`, `taskId`, `inputSchema`, and the current `revision`. Business Handoffs use their own schema. A checkpoint-recovery Handoff requires repairing its stated external failure before acknowledging. Cancellation terminates the Run; it is not a resumable pause.

## Discover and guide an active task

1. Run `pico-cli workflow guidance targets <run-id> --format json`.
2. Choose an entry with `valid: true` using its declared task/node identity, status and the package Skill's role/responsibility and route descriptions. `responsibility` and dynamic `summary` may be null; the Skill may supply the documented role meaning, but must never supply or guess an invocation identity. Null summary does not block basic guidance. A last-completed node or old snapshot does not prove a current active Agent. `capability` distinguishes supported managed continuation from verified direct steering; every submission still needs its own receipt. A read failure is not an empty target list.
3. Write a JSON file using the exact returned `invocationId`:

   ```json
   {
     "requestId": "guide-1",
     "invocationId": "<returned-target-id>",
     "message": "Use the newly confirmed requirement in this task."
   }
   ```

4. Run `pico-cli workflow guidance submit <run-id> --input guidance.json --format json`, then `pico-cli workflow guidance read <run-id> --request-id guide-1 --format json`.

Admission `accepted` means durable storage. `pending` can mean queued or in-flight; the targets projection exposes pending/sending request state. `delivered` means the Host accepted steering or the managed continuation actually started, not that the Agent adopted or completed the requested change. Inspect subsequent public results. Managed continuation stays within the same task, owner, deadline, permissions and session contract.

Targets can expire between discovery and submit. After rejection, refresh targets; do not replace the target ID on an already used request ID. Internal continuation IDs are not submission recipients: keep the returned business invocation ID. When taking over, inspect outstanding `requests` before submitting anything new.

For `unknown`, query the same request ID and **do not resend**. Uncertain ACP steering makes that connection unusable for successor turns; queued guidance may be undelivered, and retained tasks require the package's explicit session reset. Reset does not retroactively decide or resend the unknown request. There is no generic CLI reset shortcut. Omit `feedbackId`: this release has no Run-level feedback entities, and nonempty values are rejected.

## Pause and resume

Only generated checkpoint-enabled serial LangGraph supports caller pause. Check `workflow describe` → `control.pause.supported` and `beforeNodes`. Domain active pause is unsupported; the public catalog now includes spatial-app-dev-workflow@4.0.0 with generated checkpoint-enabled LangGraph, plus four Domain packages. The public dev supports adopted safe-boundary pause; the four Domain packages do not. Check the installed descriptor and actual pause state.

```sh
pico-cli workflow pause <run-id> --revision <observed-revision> --request-id pause-1 --format json
```

Omitting `--before` requests the next safe root-node boundary. A named target must be in `beforeNodes` and not already dispatched; cyclic targets are unavailable. Active tools and the current node can finish before the pause takes effect. `requested` is not proof of stopping; bounded-read until `waiting` with `taskId: system:pause` and use that new revision.

Create `empty-object.json` containing `{}`, then:

```sh
pico-cli workflow resume <run-id> --task system:pause --revision <waiting-revision> --input empty-object.json --format json
```

Resume preserves the Run and completed work. Verify the first continuation or next public Handoff instead of treating acceptance as completion. Retry the same pause request identity after an uncertain acknowledgement. Nonempty correction is not a generic replacement for guidance: it requires an explicitly adopted package validation/application contract; do not invent private-state edits or submit a correction to an undeclared package.

## Model selection and current Host boundaries

Use the actual caller context or explicit paired `--agent-tool <host> --agent-model <model>` values. Explicit selection wins and belongs to the caller; do not replace it with a guessed default. Copilot Auto inherits the ACP `auto` selector. A fixed model A requests exactly A; if the Host does not advertise A, fail rather than silently falling back to Auto. Preserve the requested selector and actually reported model as separate facts. Automatic inheritance requires a reliable context anchor and complete event interval; otherwise provide explicit parameters. Copilot restore, model switching, TUI and Windows behavior still need their own real-environment evidence. Qoder CN Auto inheritance is not supported in this release; select an explicit advertised model.

Managed dev defaults to full tool permissions without repeated per-tool approval. Agents should keep direct reads/writes and handover files in the project. Existing location/symlink checks apply to the corresponding client permission callbacks; native bypass and shell execution do not create a forced project sandbox across Hosts. OS and organization controls still apply. Cursor uses ACP agent mode with full tool access and client permission responses: select the Host's actual `allow_once` option, or its actual `allow_always` option when that is the only allow option. This is not a claim of native Cursor bypass mode or a disabled OS sandbox. Cursor's real environment remains to be validated by QA; that pending validation is not an unsupported-Host declaration.

Submit guidance once to the public managed invocation and inspect its request receipt. Production capability declarations are scoped by distribution, platform and Host. Inspect the actual target capability and receipt; a declaration for one supported combination is not evidence that every Host and delivery path passed real validation. A supported direct attempt may be used; only a definite unsupported/not-delivered result permits the same task's managed continuation. Unknown delivery forbids automatic resend or continuation and requires explicit retained-session reset when applicable. Host `injected` means accepted by the Host; adoption still requires subsequent output. Guidance does not promise interruption of a running tool or immediate behavioral change. Independent asset sessions use the package's actual asset-owner endpoint, not the public guidance targets list.

## Change the goal and hand work to a new Run

The package Skill documents role responsibilities and normal routes. For dev, Planner sets the iteration goal, Designer forms the design, impl_planner arranges implementation, Builder implements and self-checks, and Critic independently reviews. Critic pass returns to impl_planner; the first two reworks return to the same Builder task and the third returns to impl_planner. These responsibilities help interpret a real target; they never generate its invocation ID.

First read `workflow run read`, optionally `workflow snapshot read`, and `workflow guidance targets`. If a suitable Agent is active, guidance may be enough. If it is unknown, ended, or absent, report that fact; do not secretly retarget the message. To replace the current goal, pause or cancel through public commands and wait for actual stopping before another writer takes over the project. Pause admission is not stopping: the active node and tools may finish before the safe boundary. Domain caller pause remains unsupported; inspect the installed descriptor instead of assuming pause is available. Cancel is terminal and cannot be resumed as a pause.

Keep the project, design, evidence, unfinished work and independent asset references in project-local Markdown. For a dev package supporting `startAt: "impl-planner"`, use a new `workflow start <installed-package-name> --input <new-input.json> --format json` with nonempty `existingDesign`, `materials` referencing that handover and the actual `projectRoot`. The package Skill supplies the complete input. The new P must read those files; old Run state is not automatically copied. New task/review history stays separate. Do not edit Store/checkpoints or reuse completed flags. Do not resume the parked old writer after the new Run changed the same project without deciding which execution owns continuation.

The root Run's pause/cancel does not automatically stop an independent asset owner or its known Editor Runs. Query their actual controls, then cancel or explicitly transfer them. Ordinary asset start/guide does not require a root coordinator Handoff; waiting and finish retain their package-defined duties. Do not add a Critic replan verdict, automatic replanning service or dev correction payload for this handover.

## Interrupted execution and checkpoint recovery

For a timed-out or interrupted LangGraph Run, read
`pico-cli workflow run read <run-id> --format json` for its current revision and
failure reason. If it is waiting at `system:checkpoint-recovery`, use
`pico-cli workflow resume <run-id> --revision <current-revision> --format json`.
Resume supplies the system acknowledgement; no task or input file is needed.
Normal pause and business Handoffs still require paired `--task` and `--input`.

If the Run remains `running` because cleanup was not confirmed, Resume reports
why it cannot retry yet. After confirming old ACP/tools/external work stopped and
reviewing saved outputs and side effects, use
`pico-cli workflow resume <run-id> --revision <current-revision> --confirm-stopped --format json`.
This validates ownership and the pinned checkpoint, prepares recovery and launches
the retry through the same Resume path. An expired claim alone does not prove
stopping. Active ownership, cancellation, terminal state and invalid checkpoints
cannot be overridden. If the command is interrupted, read the Run before retrying;
a prepared recovery Handoff remains usable with its current revision.

New builds default to a two-hour managed task deadline; guidance continuations
share that budget. Old pinned packages retain their embedded limits. There is no
public timeout override flag. Retry preserves completed nodes and project files;
external side effects are not rolled back. Check installed `workflow resume --help`
for `--confirm-stopped`. If absent, upgrade to a supporting candidate or continue
from preserved work after old execution has stopped. Use public commands and
readable diagnostics; do not search binaries for private calls or edit Run files.
