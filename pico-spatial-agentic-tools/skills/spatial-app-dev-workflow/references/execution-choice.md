# Execution Choice and User Interaction

Read this when choosing or changing the execution mode, or explaining progress.
Use the user's language. The English examples below illustrate intent, not a keyword
allowlist. Recognize equivalent intent in any language, using context and negation;
do not require an exact phrase. Translate response examples naturally into the user's language.

When referring to this managed execution in user-facing explanations, suggestions,
confirmation questions, launch acknowledgements or progress/control reports, say
**pico-cli's built-in `spatial-app-dev-workflow`**, preserving the identifier when
translating. Internal shorthand is fine; bare "workflow" or "dev workflow" does not
identify this package to a user who may have other workflows. Interpret the intent
table in context: if a generic workflow request could refer to another system,
establish the intended workflow rather than silently starting this one.

## Standard explanation

Use this as the canonical explanation when introducing, recommending or clarifying
the managed mode, or when asking about a proposed switch. Translate it naturally
into the user's language and adapt it to the actual task; preserve the workflow
identifier and the cost warning. Do not recite it on every progress update or
repeat a disclosure the user already understands.

> pico-cli's built-in `spatial-app-dev-workflow` is an orchestrated development workflow provided by `pico-cli workflow`. It handles similar app-development tasks to the `spatial-app-dev-workflow` Skill, including planning, design, implementation, review and verification. With the Skill alone, I carry out that process directly; with the orchestrated workflow, managed roles advance it within a saved Run, and I can inspect outputs, relay guidance, pause or cancel it. It is suited to longer tasks with several development increments when you want to delegate execution and mainly provide direction or decisions. Role startup, repeated context loading, handoffs and review turns add substantial overhead: expect significantly higher Token usage and total elapsed time than direct execution. For a small change, doing it directly is usually preferable. If the workflow fails or stops producing useful results, I can stop it, preserve its project changes and artifacts, and take over directly once its previous execution has stopped.

Task duration is a recommendation factor, not automatic launch authorization.
Both execution modes aim at complete delivery; a long task or review loop can
also be handled directly. Do not imply that orchestration guarantees a better
result or that an initial choice prevents switching later. The saved Run is
execution bookkeeping; useful progress also lives in project files and artifacts.

If a choice is still needed, connect the explanation to this task and ask whether
to start **pico-cli's built-in `spatial-app-dev-workflow`** or do it directly.
If the user already selected or authorized that workflow, briefly acknowledge the
choice and proceed; the cost warning does not create another confirmation gate.

## Choose from intent and context

| User intent                                                                     | Action                                                                                                                                                                  |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| “do it directly”, “do not start a workflow”                                     | Do the work directly. Do not repeatedly offer the rejected mode.                                                                                                        |
| “start the dev workflow”, “use a workflow”, “hand continuation to the workflow” | Launch within the request. Briefly disclose relevant costs/permissions without waiting for another confirmation.                                                        |
| “go ahead”, “continue on your own”, “I will be away”, `/goal`                   | Continue within the current mode and authorization. These can mean autonomous direct work. Offer a switch only when useful.                                             |
| “resume the previous workflow (task)”                                           | Identify the existing Run and read its state. Use its supported Resume contract, including checkpoint recovery after timeout; do not silently create a replacement Run. |
| “resume the previous task” without Run context                                  | Continue the known task; do not infer a Workflow Run from this phrase alone.                                                                                            |
| “choose how to execute and finish it”                                           | Choose within the user's delegated scope, explain the choice and workflow costs before launch, and proceed.                                                             |
| “what is a workflow?”, “must we use one?”, “do not start one”                   | Explain or respect the refusal; a keyword in a question or negation is not launch intent.                                                                               |

Both modes can perform full implementation, review and repair. Direct execution
can be autonomous. Managed execution can receive frequent guidance. Without an
explicit workflow choice, prefer direct execution for a small, clear change that
can likely be implemented and checked in a few minutes. Repeated context loading,
role handoffs and review turns may cost more than the change itself. Longer workflow histories can also draw Agent review toward local details while
visible progress slows; see [review limitations](workflow-limitations.md#review-can-lose-sight-of-the-overall-goal). Task size
informs the recommendation; it does not override the user's choice. Do not infer
a mode from the user's experience, message frequency or willingness to review.

Cost and limitation warnings inform the user; they do not require acceptance.
For an explicit workflow request, say briefly, for example:

> I'll start pico-cli's built-in `spatial-app-dev-workflow`, provided by `pico-cli workflow`. Its separate roles and review steps add substantial Token and time overhead compared with doing this change directly. I'll use it for the agreed task and report its actual outputs and progress.

Then start within the existing authorization. Do not append "Are you sure?" or
wait for a reply to the warning. Do not repeat disclosures already understood.
Only an Agent-proposed switch without existing authorization needs a choice from
the user; missing required inputs and actual tool permissions remain separate.

## Offer a switch without interrupting useful work

When a user who has been directing each change leaves the task to the Agent:

> I can continue directly. For this longer task, I can also start pico-cli's built-in `spatial-app-dev-workflow`, provided by `pico-cli workflow`, with managed implementation and review roles. I can inspect its outputs, guide, pause or cancel it, and take over directly after stopping it if needed. Expect significantly higher Token usage and elapsed time. Shall I start pico-cli's built-in `spatial-app-dev-workflow`, or continue directly?

Until answered, continue useful work within the existing mode. Do not start
competing execution in anticipation of consent. If the user already authorized
workflow execution, act on that authorization instead of asking again.

Before the first launch, add the relevant permission fact in plain language:

> Agents in pico-cli's built-in `spatial-app-dev-workflow` use full tool permissions by default, without asking you to approve every operation. Host and machine permission limits still apply.

Do not promise that the workflow is faster, cheaper, more stable, or guaranteed to
finish. Describe observable mechanisms: separate implementation and review roles,
saved Run state, progress inspection, guidance, and supported pause/resume.

## Acknowledge a real launch

After obtaining a real Run ID and Web UI URL, report the accepted goal and provide
both. For example, replacing placeholders with actual facts:

> I've started pico-cli's built-in `spatial-app-dev-workflow` for <accepted goal>. Run: <actual Run ID>. View progress at <actual Web UI URL>. You can also ask me to inspect its outputs, submit guidance, pause or cancel it.

Return the link without forcing a browser window open. If the viewer cannot start,
say that and give the Run ID and current state. Do not invent a URL or imply the
app is already previewable just because its workflow viewer exists.

Only promise ongoing supervision when the current Host/session can actually keep
doing it. Otherwise explain that the user can return to this Run to check progress.

## Report outcomes as well as activity

When asked for progress, read current state and inspect the available artifacts.
Report what is finished with links to code, design, screenshots, recordings, APKs,
or other relevant outputs. Explain what has actually been verified, what is being
worked on, and what remains or needs a decision. Include the Web UI link when
available. If no preview exists yet, say so; do not substitute the node name for
the result or label an old screenshot as current.

For a pause, cancellation, or guidance request, distinguish request admission from
its observed effect. Keep the acknowledgment short; return with the actual outcome
when the control takes effect or the observation budget expires.

## Switch without losing work

Starting managed execution is not a commitment to keep using it for the rest of
the task. When it fails, stalls, or delivers poor results, the caller can stop it
and continue directly within existing task authorization. Explain the reason and
takeover plan, and honor any current explicit requirement to stay in managed
execution. Do not require a replacement Run, checkpoint repair, or successful
workflow completion before direct continuation. For example:

> Execution through pico-cli's built-in `spatial-app-dev-workflow` is no longer making useful progress. I'll stop its active execution, preserve the existing code and artifacts, and continue directly from the project state.

This is a plan, not proof of stopping. Confirm the old writer and device activity
stopped before editing or operating the device. If stopping remains uncertain,
report that blocker and avoid a competing writer. Follow
[recovery and handover](workflow-recovery.md#continue-directly-or-start-a-new-run).

Carry the same request, decisions, current code, assets, design and verification
evidence into the next mode. Record unfinished work and who owns any independent
asset task. Stop the previous application writer and its device activity before
the next writer takes over. A paused Run can preserve a checkpoint, but resuming
it after another writer changed the project requires reconciling those changes.
