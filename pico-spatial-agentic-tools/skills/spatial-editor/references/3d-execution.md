# Choose and Continue 3D Execution

## Choose the path

1. Identify the requested result, what must stay unchanged, and how completion
   will be demonstrated. Select App, Kotlin scene, or Editor authoring guidance
   by the work it owns. Loading a Skill or using a 3D capability does not start a
   Run. Keep work on the same target inside its active managed Run when that Run
   owns the write.
2. Prefer direct execution whenever the current task and available tools can
   satisfy the complete request. This can include planning, batches, async
   operations, and iterative fixes. Object count, tool choice, and implementation
   terminology do not select an execution mode.
3. For Editor work, start a new managed Run only when the user's prompt or an upstream
   app Agent's delegation prompt explicitly requests the Editor workflow. Required evidence,
   dependencies or recovery properties cannot supply missing workflow selection.
   For code-owned work, start a managed 3D Run when explicitly requested, when the deliverable needs
   formal Run evidence, or when a required dependency, handoff, or recovery
   property cannot reliably be satisfied directly and the Run supplies it. Name
   that concrete requirement. When facts are missing, inspect the target before
   choosing. Do not use a Run to resolve an unclear scope or missing capability.

For direct Editor work, use the intended connected session. If it is not ready,
use `ensure_editor_ready` for the target project, then use its documented native
Editor tools. Verify the saved scene or requested output. In a managed Editor
Run, use its current tools and Handoffs instead of starting a direct session.

For direct entity component operations such as attaching, inspecting, editing, or
removing a custom component, use the tools advertised by the connected Editor
after readiness. If the needed tool is absent, report which operation is unavailable.
Kotlin component declaration sync does not change the entity.

For direct Editor model generation, retain the task ID returned by generation
and use `poll_generation_status` to check that task. If no task ID was returned,
report that the submission could not be confirmed.
`update_generation_progress` only changes the Editor display; its success does not
confirm submission, generation, or import. Verify the imported asset separately.

## Reuse the methods

Both paths can use the relevant authoring, asset reuse, spatial constraint,
verification and repair guidance. Apply it to the requested scope. When direct
results fall short, use the relevant method and verify the repair before
considering a different execution path. SceneSpec submission, Handoffs, approval
steps, and Run receipts apply only inside the managed path. Direct work may plan
without creating those artifacts.

## Continue after a Run fails

Use the live Run state. Waiting, uncertain submission, and recoverable failure
stay with the current Run and its published recovery actions. When that path
cannot continue, confirm its writer and conflicting in-flight work have stopped
before writing to the same target. Terminal status alone does not confirm cleanup.

Within the original authorization, inspect the actual project, accepted artifacts,
and known task outcomes. Continue directly using the available atomic tools for
only the remaining work. Reuse completed results and observe existing async tasks;
do not repeat completed operations or resubmit an uncertain generation or write.
Keep the original Run record. If ownership or a required capability is unresolved,
report the specific blocker rather than bypassing it.

## Verify the actual result

Keep the user's acceptance criteria across both paths. Direct work provides its
own build, saved scene, runtime checks, or verified outputs as applicable. A
managed delivery provides the evidence required by its Run contract. If direct
continuation completes work after failure, report the old Run outcome separately
from the verified task result and call out any missing required managed evidence.
Do not create a Run just to validate direct work.
