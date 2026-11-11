# Workflow Limitations

Applies to the dev 4.0 contract examined for this draft. Check the installed
descriptor, Run's pinned version, live receipts, and release notes before relying
on a capability. Do not apply new-package guarantees to an old Run.

## Explain the relevant cost before launch

A managed workflow adds role startup, repeated context loading, handoffs, review
and possible rework. These can increase both Token usage and elapsed time without
improving the result. For a small, clear task that the current Agent could edit
and verify in a few minutes, that overhead may outweigh the work itself. Prefer
direct execution unless the user chooses a workflow. Small tasks do not need a
managed Run just to receive proper implementation and verification.

Explain this tradeoff when recommending a workflow or first launching one; do
not promise savings, better quality, stability or eventual completion. An explicit
workflow request is sufficient authorization for the execution mode: give a brief
relevant warning and proceed, without asking the user to reconfirm. Do not turn
this reference into a mandatory risk-acceptance checklist.

A workflow can repeat work, misread requirements, produce incomplete artifacts,
or get blocked by its tools. Inspect results and intervene when evidence stops
improving. Direct continuation or a new Run with a clear handover remains valid;
leaving the old Run does not discard the project's code, assets or other outputs.

Dev roles use full tool permissions without repeated per-tool approval. Host, OS
and organization restrictions still apply. Keeping files in the project is a
working convention, not proof of a universal filesystem sandbox. Do not claim
that reading this skill changes Host permissions or that no approval can ever occur.

## Review can lose sight of the overall goal

Development quality still depends on Agent judgment, including Critic's review.
As a task history grows, loss of attention to earlier requirements, missing context
or hallucinated context can lead reviewers to focus on local details while losing
track of the original goal and overall application quality. More review and rework
can then consume Tokens and time while producing fewer visible improvements in
later iterations. A separate Critic role does not eliminate this failure mode.

The external coordinating Agent and user should judge progress by actual artifacts
and user-visible results against the original request. Review counts, a long issue
list and repeated Critic verdicts are not evidence that the application is getting
better. Compare relevant design and runtime evidence to identify what still matters.

When review gets stuck on local details, use external guidance to redirect the
work: point out the mismatch with the goal, state the intended next-iteration
outcome, identify the priority problems and distinguish details that can wait.
The coordinating Agent should use the current workflow state and a valid guidance
target to address the relevant role. A user's direction can be relayed this way;
do not rely only on the internal review loop to correct itself.

Check the delivery receipt and subsequent reports or artifacts to see whether the
direction was adopted. Delivery does not prove adoption. If the intended role's
window has passed, do not claim guidance is queued for that future role; use an
appropriate current target or the supported pause/handover path. If guidance does
not restore useful progress, direct continuation or a new Run with a concise,
evidence-based handover remains an option, not a guaranteed cure.

## Controls have distinct completion conditions

| Capability       | Current boundary                                                                                                                                        | What the caller should do                                                                                                                             |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pause            | Safe root-node boundary on supported serial LangGraph; active tools/current node may finish first. Domain workflows do not gain pause support from dev. | Check the descriptor and actual `system:pause` waiting state before another writer takes over.                                                        |
| Resume           | Same Run, pinned package, declared handoff input. No generic arbitrary-state correction or cross-version migration.                                     | Use the current task/schema/revision; hand over to a new Run for incompatible changes.                                                                |
| Guidance         | Target-specific; delivery timing depends on Host and Runtime capability. No universal immediate tool interruption.                                      | Discover a real valid target and verify its request receipt and later output.                                                                         |
| Unknown steering | Delivery is uncertain; retained session continuity may become unavailable.                                                                              | Do not resend. Use only a documented package reset/recovery path; there is no generic reset command.                                                  |
| Future feedback  | No general Run-level feedback inbox or guaranteed retargeting to a future role.                                                                         | If no suitable target exists, preserve the message in project handover and deliberately choose guidance later, pause/new Run, or direct continuation. |
| Waiting          | A handoff may require caller action. Terminal wait/follow does not finish merely because the Run is waiting.                                            | Observe with a bounded budget and handle the handoff.                                                                                                 |
| Root stop        | Does not automatically stop independent asset owners or their Editor Runs.                                                                              | Query, stop or transfer those tasks separately.                                                                                                       |

## Long invocations, timeout and incomplete cleanup

New runtime builds default to a **two-hour managed Agent invocation deadline**.
Explicit package invocation limits may differ; independent asset-owner timeouts
are separate. Guidance continuations share the same task budget rather than
receiving two more hours each. There is currently no user-facing Run timeout flag.
A Run keeps its pinned package: upgrading the CLI does not change an old bundle's
embedded deadline, which may still be 60 minutes.

An unfinished invocation may be interrupted at its deadline. Do not assume the
Agent receives an advance warning, automatically advances to Critic, or finishes
its current tool safely. Confirmed cleanup and a valid checkpoint-retry contract
can produce `waiting` with `system:checkpoint-recovery`.

`WORKFLOW_DRAIN_INCOMPLETE` means process exit was not confirmed. The Run may
remain `running`; that alone proves neither ongoing progress nor stopped
execution. Read `pico-cli workflow run read <run-id>` for its revision and failure
reason. Resume gives actionable refusal reasons. Only after confirming the old
node's ACP/tools/external work stopped and reviewing outputs/side effects, use
`pico-cli workflow resume <run-id> --revision <current-revision> --confirm-stopped`.
It prepares recovery and retries the interrupted node in one command, without
requiring a task ID or input file. If already waiting at checkpoint recovery,
`workflow resume <run-id> --revision <current-revision>` suffices. Normal pause and
business Handoffs keep their own task/input contract.

Retry does not roll back tool side effects or upgrade the pinned package. Live
ownership, cancellation, terminal state and invalid checkpoints cannot be bypassed.
Observe with a finite budget. Do not poll forever, rewrite Run files, kill a
historical PID, or start a second writer while the first may still be active.
If cleanup cannot be established, report the blocker. Older installed CLIs may
lack this Resume path; check `workflow resume --help` for `--confirm-stopped` and
use a supporting candidate, or hand over preserved work after old execution
stopped. Follow [recovery and handover](workflow-recovery.md).

## Host and model boundaries

Builder session reuse is scoped to one Run. Same-selection Resume can load its
session across Workers at a clean durable boundary; a changed Host/model selection
uses a new session. Both require confirmed cleanup. See
[recovery and session reuse](workflow-recovery.md#pause-then-resume-the-same-run)
for the load-capability and continuity-error boundaries; separate asset owners
have their own lifecycle.

Automatic caller identity depends on a supported entry path and reliable captured
context. If absent or ambiguous, use explicit Host/model selection; do not infer
it from nearby unrelated sessions. Explicit selection wins.

Copilot Auto uses the `auto` selector when reliably captured; a selected fixed
model must remain that fixed selection. Qoder CN Auto inheritance is unsupported
in the examined release: use an explicitly advertised model. A model visible in
the interactive Host is not automatically proven selectable through its ACP path.

Active steering availability varies by Host, distribution and version. Inspect
the actual target capability; source adapter existence is not live acceptance.
Windows, TUI and real Cursor behavior need their own environment evidence. A
pending QA result is not the same as an unsupported implementation. Do not invent
a universal support claim or deny a Host solely because it was not in a test sample.

Token information, when reported, can help understand cost; missing usage is not
zero usage. Do not promise a complete total across all Hosts, calls and nested
asset work, or an enforced spending limit that the current Run does not provide.

## UI, assets, and acceptance

The full managed UI workflow includes code writing and device verification. It
is not currently a design-only child that can safely run alongside dev's app
writer. Use its stage-specific skill guidance inside dev. Worktrees isolate file
directories but not the same installed package, emulator, or shared device logs.

An asset file on disk does not prove the asset workflow can resume or package it.
If production reached an intermediate candidate but later export/capture failed,
inspect that workflow's supported recovery contract. Do not promise recovery from
the retained files or launch duplicate production while cleanup is unknown.

A successful build, a finished Run, an Editor handoff and a visually correct app
are different claims. Verify the requested behavior and actual app output. A
design screenshot cannot alone prove implementation fidelity, and ordinary
device captures may be insufficient for spatial/volumetric interaction. Keep
unverified effects explicit and ask for the missing real-device observation when
automation cannot establish them.
