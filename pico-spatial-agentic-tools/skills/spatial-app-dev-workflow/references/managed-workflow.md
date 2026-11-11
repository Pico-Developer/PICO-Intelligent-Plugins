# Managed Dev Workflow

Use this for the `spatial-app-dev-workflow` 4.0 contract. Inspect the installed
package before acting; historical Runs retain their original package contract.
The shared `pico-cli` skill owns general command discovery and its
Workflow control and takeover reference owns common control semantics. This reference
adds dev-specific roles, inputs, supervision, and handover responsibilities.

## What executes

The workflow coordinates Agent roles and keeps execution/checkpoint facts. Roles
use the same development and specialist guidance as direct execution; a Run is
not a substitute for application verification.

| Node / stage          | Responsibility and expected material                                                                                                                                             |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prepare`             | Establish the execution context and project root. This runtime step is not the onboarding skill and does not prove a runnable app exists.                                        |
| `planner`             | Interpret the request and materials; produce the iteration goal and plan.                                                                                                        |
| `designer`            | Form the design needed for implementation, with references and visual artifacts where relevant. Apply UI design guidance without launching a second app implementation workflow. |
| `impl-planner`        | Arrange the next implementation task, reuse completed work, and dispatch or guide independent asset production when needed.                                                      |
| `builder`             | Implement the assigned app task, integrate available assets, and perform build, runtime, accessibility and device verification.                                                  |
| `critic`              | Delegate independent review of the implementation and evidence, then consolidate pass or rework.                                                                                 |
| `coordinator-handoff` | Ask the caller to handle the saved asset wait or finish request; inspect its actual input schema.                                                                                |
| `finalize`            | Produce the Run's final result from the saved completion facts.                                                                                                                  |

Normal route:

`prepare → planner → designer → impl-planner → builder → critic`

Critic pass returns to impl-planner for the next decision. The first two accepted
reworks return to the same Builder task; the third returns accumulated reports to
impl-planner. Impl-planner can return to Designer, start a build task, or request
coordinator handling. These routes do not guarantee eventual convergence.

## Recommended Designer capabilities

For work that needs a new visual direction, prefer an Agent environment where the
Designer can actually use image-generation tools. Generated concept art is often
better suited than programmatic drawings to exploring overall appearance,
materials, lighting and atmosphere, and can provide a clearer visual benchmark
for later implementation and review. Verify the tools available to the managed
Agent; a model name or tools in the caller's session do not establish availability
inside the Designer invocation. Respect the selected Host/model.

Reuse suitable existing designs and references rather than generating images for
every task. Diagrams, SVG and prototypes remain useful for structure, layout and
interaction. Concept art communicates a target; it does not prove SDK feasibility
or the quality of the implemented application.

This is a capability recommendation, not a launch prerequisite or an extra
confirmation step. If image generation is unavailable, explain the relevant
limitation and continue with existing visual references and suitable methods.
Do not silently change the user's Host/model or install tools to obtain it.

## Start with the actual package and caller

1. Read `pico-cli workflow describe spatial-app-dev-workflow --format json` and the installed command help. Confirm the input contract and available controls.
2. Reuse the caller's reliably captured Host/model or the user's explicit selection. If capture is unavailable, obtain a valid explicit `--agent-tool` / `--agent-model` pair. Do not guess the model or silently change a fixed selection to Auto.
3. Put the goal, acceptance expectations, project location and existing material references in an input JSON file. Keep working handover files in the project.
4. Start the Run once and save its real identifier. If acknowledgment is interrupted, inspect existing execution facts before creating another Run.

Minimal input, replacing the example project path and request:

```json
{
  "request": "Implement the agreed app increment and verify its acceptance criteria.",
  "projectRoot": "/absolute/path/to/project",
  "materials": ["handover/development-context.md"]
}
```

Create the referenced handover before starting, or omit the optional `materials`
entry when there are no existing materials. Input fields:

| Field                              | Meaning                                                                                                                                                                 |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `request`                          | Required nonempty task, including constraints and expected result.                                                                                                      |
| `projectRoot`                      | Required absolute target project directory. Runtime freezes the selected root for this Run; a missing directory can be created when execution starts.                   |
| `materials`                        | Optional references to existing decisions, designs, code/evidence notes and handovers. They are inputs for Agents to read, not an automatic copy of previous Run state. |
| `startAt`                          | Defaults to `planner`; `impl-planner` is the supported continuation entry when a usable design already exists. It is not an arbitrary node selector.                    |
| `existingDesign`                   | Nonempty design context required when starting at `impl-planner`. Describe the accepted design and where its source artifacts are.                                      |
| `assetDirectory`, `assetGuidePath` | Optional project asset location and free-form progress/brief Markdown; defaults are `assets-production` and `assets-production/ASSETS.md`.                              |

```sh
pico-cli workflow start spatial-app-dev-workflow --input dev-input.json --format json
```

Add explicit Host/model flags only when selected or required. Do not add local
maintainer launcher overrides to normal user inputs. Dev roles default to full
tool permissions without repeated approval; this is not a cross-Host filesystem
sandbox or authority to exceed the requested task.

## Observe and show the work

Read the Run with `pico-cli workflow run read <run-id> --format json`. `run read`
is a current observation; `events read` provides recorded event history. Neither
is a waiting loop. Use a finite observation budget and a delay between reads when
following progress. A `waiting` Run needs handoff handling, not an indefinite
terminal-state waiter. A quiet Run is not proof of failure.

After launch, obtain the local viewer link with:

```sh
pico-cli workflow web <run-id>
```

The command returns a real URL after starting or reusing a background viewer.
Give that URL to the user; opening a browser is optional. The viewer observes the
Run. Closing the viewer does not cancel execution, and the workflow viewer is not
an application preview. Do not invent a port or append unsupported JSON flags.

Inspect actual reports and visual/runtime artifacts when reporting progress or
completion. A successful Run status alone is insufficient evidence of app quality.
When a handoff appears, read its current task, input schema and revision, handle
the requested operation, then resume that exact handoff.

## Guide the right Agent

Read the Run and `pico-cli workflow guidance targets <run-id> --format json`.
Use a valid target's actual node/task identity with the role table above to
understand its responsibility. A missing optional summary does not prevent this;
an old node name does not prove an Agent is still active. Never manufacture an
invocation ID from a role name.

Submit once through the shared CLI guidance contract and retain its request ID.
Advice may be delivered through active Host steering or a follow-up in the managed
task/session. The runtime chooses according to available capability and delivery
outcome; the caller does not launch a duplicate follow-up itself. It is not a
promise to interrupt an active tool call.

Read the receipt: accepted means persisted; delivered means accepted by the Host
or that managed continuation started. Check later outputs for actual adoption.
On unknown delivery, read the same request instead of resending. On definite
target rejection, refresh targets and decide whether another live role can use
the advice. Explain a retargeting decision; do not silently send it elsewhere.

For a change of goal, Builder may understand the feedback, but do not promise a
specific reroute from natural-language guidance. If the current role cannot act
on it, use public pause/cancel and a deliberate handover. There is no durable
Run-wide feedback inbox that guarantees delivery to a future role.

## Independent asset work

Impl-planner can dispatch an asset Agent without stopping the main app workflow
for ordinary start/guide operations. It records the actual task/control references
in Run state and supplies them to subsequent roles. Asset progress and meaning
live in project Markdown; the asset Agent may itself use an Editor workflow.

Use only the task's returned controls and runtime-supplied instructions. A saved
ACP session ID by itself is not a reconnect or guidance API. Independent asset
sessions are not recipients in the public dev guidance targets list. Do not turn
a private node command into a user-facing dev entry point.

Wait for the required asset output before integrating it; other non-conflicting
app work can proceed. At a finish/wait handoff, inspect the saved asset task and
known Editor Runs. Root pause/cancel does not automatically stop them: explicitly
stop or transfer ownership and keep that result in the handover. An uncertain
cleanup result does not permit starting a competing producer.
