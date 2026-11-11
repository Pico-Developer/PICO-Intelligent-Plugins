---
name: pico-app-interaction
description: Execute existing-application actions and declared Contract/JEV goals on PICO targets; verify business completion from real receipts and operation-bound outcomes. Use when asked to operate a published control, achieve an application goal, report met/unmet feedback, or handle INTERACTION_FRICTION_HIGH and explicit continue/manual takeover. NOT for command syntax, package lifecycle or code authoring; use pico-cli, pico-emulator-usage or pico-project-setup.
license: 'Apache-2.0'
---

# PICO Application Interaction

This atomic Skill owns operating an existing application and reporting its business outcome.
It uses the existing `pico-cli interact` implementation. The CLI owns dispatch receipts,
operation IDs, bounded history, thresholds and feedback persistence; do not implement a second
monitor, controller or retry engine in this Skill.

## When to Use

- The user asks to operate a published control or achieve a declared goal in a running application.
- A platform assessment supplies a Contract/JEV plan for an existing application operation.
- Actual business evidence is available for an operation's `met` or `unmet` feedback.
- `INTERACTION_FRICTION_HIGH` requires a continue/manual decision, or the user answers a pending warning.

## When NOT to Use

- Command syntax, help, output formats or command discovery: use `pico-cli`.
- APK installation/launch or emulator lifecycle: use `pico-emulator-usage`.
- Selecting or classifying a device: use `pico-cli-device-target`.
- Environment readiness or repair: use `pico-env-doctor`.
- Capturing a still screenshot: use `pico-cli-screenshot`.
- Creating or changing application code or its SDK: use `pico-project-setup` to reach the owning platform workflow.

## Inputs and Completion

Use the supplied device, application package, user goal, current scene evidence and relevant
Contract or goal catalogue. Application facts, markers, action semantics and goal dependencies
belong in Contract; static ordering and completion waits belong in JEV.

The output is the original action/goal result, its real receipts, observed business outcome and
any pending user decision. `performed=true` proves acceptance, not business completion.
Missing input or evidence remains unknown; do not manufacture a successful outcome.

## Atomic Workflow

### 1. Establish scope and scene eligibility

Preserve the supplied device/package and any valid session-readiness evidence. Resolve only a
missing target through `pico-cli-device-target`; do not repeat environment setup for each action.
Use the current Contract's source-derived scene facts and markers, including `markerMatch=all`
when declared. A shared control or a static goal label alone does not identify the current scene.

A current scene requiring real-time reaction, or lacking evidence of static suitability, is not
suitable for AI operation through this path. Warn and stop before the next app input as soon as
the timing requirement is recognized; do not wait for an efficiency warning. Do not query merely
to confirm a known rejection, switch modes, disable events or modify the app to make it operable.
`SCENARIO_UNSUPPORTED` is terminal. A friction acknowledgement cannot override it.
Apply this rule to emulators and headsets. Explain the limitation and ask for manual operation or
read-only assistance; wait for the user before changing scope or sending further app input.

For a source-proven static setup supplied by the caller, use the declared goal directly; its
internal eligibility observation is sufficient. Use one scoped query only when a public target
or current state needed for an otherwise eligible operation is unknown:

```bash
pico-cli interact query --device <serial> --package <application-id> --compact --format json
```

### 2. Execute the smallest declared operation

For a current Contract control, make one published action call:

```bash
pico-cli interact act --device <serial> --package <application-id> --project <project> \
  --component <contract-id> --action <published-key> --arguments '<json-object>' \
  --refresh auto --compact --format json
```

Use `--refresh never` for a local mutation; `auto` is for a page-changing action. Preserve object
words in selectors and desired-state semantics. Do not substitute a toggle for an idempotent action,
guess coordinates, reuse stale node IDs or invent an unpublished action.

For a declared end goal, let Contract/JEV own the plan:

```bash
pico-cli interact route --device <serial> --project <project> --goal <goal-id> \
  --compact --format json
```

Preserve a supplied executable, project and custom Contract binding instead of rediscovering them.
Use a declared route for cross-surface navigation and an ordered batch only for compatible
same-surface operations. Do not learn application-specific routes by repeated trial and error.

### 3. Verify receipts and business evidence

Preserve original results, errors, exit status, `actionReceipt` and returned `operationId`.
Distinguish actual dispatch, accepted work, uncertain replies and completion observation.
An observation timeout is not an action failure. Never replay accepted or uncertain work.

Use returned application state or a necessary bounded follow-up observation to assess the expected
business outcome. Query frequency, cosmetic animation, `changed=false`, and `verified=false` alone
do not prove an unmet outcome. Report unknown when evidence is insufficient.

For operation-bound outcome feedback, load
[`references/interaction-friction-warning.md`](references/interaction-friction-warning.md).
Use only actual returned IDs on the same device and normalized package. The CLI validates and
persists feedback; do not edit its history or generate replacement IDs.

### 4. Handle an efficiency warning and user choice

For `INTERACTION_FRICTION_HIGH`, or an answer to a pending warning, load the same
[`references/interaction-friction-warning.md`](references/interaction-friction-warning.md).
Explain the actual counts and uncertain cause, then pause automatic retries for the user's choice.
Silence is not consent. A user choosing continue must successfully acknowledge the same warning
before any new operation; replan from current evidence without replaying accepted or uncertain work.
For manual takeover, acknowledge that warning and stop automatic operation without sending app input.

Both windows require at least 50% unsuccessful actions: a 10-minute sample of at least 10 actions
also needs at least 3 linked queries and 3 distinct unsuccessful operations; a 20-minute sample of
at least 20 actions needs at least 6 of each. The 3/6 evidence requirements do not make 3/10 failures
sufficient. Use the CLI's returned warning rather than recomputing or lowering these thresholds.

## Error Recovery

- Preserve target, action, observation and transport errors instead of replacing them with monitor status.
- `INTERACTION_MONITOR_UNAVAILABLE` does not prove a dynamic scene or change the original result.
  Do not claim outcome feedback or a user decision was saved after a persistence error.
- Unknown or expired IDs require current returned evidence; do not acknowledge a different warning.
- A pending warning can outlive its current threshold counts. Its CLI identity remains authoritative.

## Verification

- The actual device/package and current Contract scene qualify the operation; rejected scenes have no dispatch.
- Commands use published actions or a declared JEV goal, and original receipts/errors remain visible.
- Business completion is supported by returned state or an observed outcome, not acceptance alone.
- Outcome feedback uses the returned operation ID; continue/manual feedback uses the current warning ID.
- No retry resumes before an explicit user choice and successful acknowledgement; manual choice ends automation.

## Shortcuts to Resist

| Shortcut                                          | Required boundary                                                                     |
| ------------------------------------------------- | ------------------------------------------------------------------------------------- |
| "The action was accepted, so the goal succeeded." | Acceptance and business completion are separate evidence.                             |
| "A few failures are enough to warn."              | Require the CLI's full sample, 50% rate and linked-query/distinct-operation evidence. |
| "Continue lets me try an unsupported mode."       | User choice never overrides Contract scene eligibility.                               |
| "Move the loop into the generic CLI guide."       | This Skill owns application operation; `pico-cli` owns command usage.                 |
| "Start another monitor to recover the workflow."  | Existing CLI receipts, history and feedback are the single state implementation.      |
