---
name: pico-env-doctor
description: Diagnoses PICO CLI, plugin, Host, MCP, and shared-tool readiness across Spatial, Unity, and standalone use. Use when verifying or repairing the PICO environment, updating tooling, reconnecting MCP, or another Skill needs readiness for live CLI, knowledge, emulator, or device work. NOT for help/version discovery, static code edits, architecture discussion, or application SDK upgrades. Use pico-cli for help/version discovery.
license: 'Apache-2.0'
allowed-tools: Bash(node --version) Bash(npm --version) Bash(command -v:*) Bash(pico-cli:*)
---

# pico-env-doctor — Verify-first PICO environment workflow

## When to Use

- Verifying the PICO agent environment before running pico-cli or MCP queries
- Diagnosing plugin, Host, or MCP connection failures
- Setting up, updating, or repairing PICO tooling integration
- The user asks to health-check, doctor, or verify the PICO environment

## When NOT to Use

- Pure code reading, architecture discussion, or static edits — no live tooling needed
- Generic CLI command usage after environment is healthy — use `pico-cli`
- Project creation or platform setup — use `pico-project-setup`

## Scope and trigger policy

Run this skill **first** only for environment-dependent execution tasks, such as:

- Running environment-dependent `pico-cli` commands beyond help/version discovery.
- Querying the `pico-dev-knowledge` MCP server.
- Installing, setting up, updating, or reconnecting plugin/host integration.
- Starting PICO emulator/device workflows whose success depends on local setup.

Do **not** treat this skill as a universal gate for every PICO task. It is
not required for purely local code reading, architecture discussion, static code
edits, or project analysis that does not depend on a live `pico-cli`, plugin,
or MCP environment.

### Scope boundary: AI tooling only, not the business SDK

This skill validates the **AI tooling environment** — that `pico-cli`, the
intelligent plugin, and the PICO development knowledge are present, current, and mutually
aligned (including the PICO development knowledge ↔ project-SDK `major.minor` alignment in
Step 5). It does **not** validate, gate, or recommend a change to the project's
business Spatial SDK/BOM version. Reading the project SDK line is only for
PICO development knowledge alignment; never turn that read into "your SDK is outdated,
upgrade it". Upgrading the business SDK is a separate, user-initiated action
owned by the configured platform’s SDK-update workflow — surface it only when the user
explicitly asks to upgrade, and otherwise leave the project's SDK version
untouched.

When this skill is in scope, do not run the dependent CLI/MCP workflow or claim
the environment is healthy until the environment has been checked or the
remaining blocker is clearly reported.

Treat a broken or stale environment as the default assumption when the user mentions:

- `pico-cli` missing, old, failing, or returning unknown commands.
- Plugin setup, missing skills, or host integration problems.
- `pico-dev-knowledge` MCP absent, disconnected, or failing to start.
- Requests to verify, doctor, health-check, repair, set up, update, or reconnect
  the PICO Spatial agent environment.

## Default developer path

For the first real environment-dependent task in a session, run the comprehensive root doctor
with the actual project/resource roots and Host. Inspect the whole report, including CLI/plugin
freshness and shared tools, even when only one capability is needed. Report unrelated findings
with a next action; do not hide them or install every optional dependency to make the report green.
Only a failure that affects the requested task blocks that task. A timeout, offline check, or skipped
probe means readiness is unverified, not healthy; continue only work with sufficient independent evidence.

Strongly recommend the latest compatible CLI in the user's existing distribution/release channel
and its matching plugin release. Follow Step 2 for freshness checks and Step 4 for plugin updates.
Keep deliberate version pins and beta/stable choices visible. A recommendation is not permission
to upgrade: when the user defers, state the implications and continue supported work. Do not
reinterpret a CLI/tooling update as permission to upgrade the application's SDK/BOM.

## Session reuse rule

Do not rerun the full environment check on every turn. Reuse the latest
completed `pico-env-doctor` report and its task-specific readiness evidence within the host session when all of the
following remain true:

- The current workspace and target host/tooling are the same.
- No environment setup, CLI/plugin/toolchain update, or Host-integration installation has run since the last check.
- No new failure signal suggests the environment changed.
- The user did not explicitly ask to re-verify.

Emulator, device, and app lifecycle operations—including emulator image install, create/start/stop,
and APK install/launch—do not by themselves invalidate the complete report. In a later turn in the
same unchanged Host session, reuse it and refresh only the affected target-specific check; do not
rerun the full environment doctor solely because one of those lifecycle operations ran.

Unrelated recorded warnings/errors do not invalidate an otherwise usable task-specific result;
keep them in the report rather than rerunning until everything is green. Re-run affected checks
when any condition changes, and run the complete diagnosis when the user requests it.

## Repair authorization rule

Read-only diagnosis is allowed whenever this skill is in scope. Repair actions
such as `pico-cli update`, `pico-cli setup`, `pico-cli plugin update`, package
installation, or other environment mutation must only run when one of the
following is true:

- The user explicitly asked to repair, set up, update, reconnect, or fix the environment.
- The task itself clearly requires setup/update/start behavior to complete.

If the user asked only to verify or diagnose, stop after diagnosis and report
the exact repair command that would be appropriate instead of executing it.

Permission denial takes precedence over retry, repair, and reconnect guidance. Stop the denied operation; do not retry through another context or subagent. Report it and continue only independently permitted work.

## Workflow and reference loading

1. For an environment-dependent task, check the session reuse rule above. If a valid report
   already establishes this task's readiness, continue with that evidence.
2. For a new diagnosis or uncertain command support, load
   [capability-discovery.md](references/capability-discovery.md) to determine supported commands,
   diagnosis scope, and permitted effects. Then load
   [diagnostic-flow.md](references/diagnostic-flow.md) for bootstrap, complete diagnosis,
   platform-specific knowledge alignment, and Host-visible verification.
3. When a finding needs repair, load [fix-quick-map.md](references/fix-quick-map.md) to identify
   the action and [self-heal-rules.md](references/self-heal-rules.md) for repair and reconnect
   constraints. Apply only authorized actions and re-verify the affected capability.
4. Report the evidence and handoff below. A supported task may continue with unrelated findings
   recorded; denied operations stop and unverified capabilities are not reported as healthy.

## Anti-patterns

- Starting environment-dependent CLI/MCP/emulator work without this environment
  check when setup is suspect.
- Running `pico-cli doctor`, `pico-cli knowledge doctor`, or `pico-cli primer doctor`
  without first confirming the installed CLI exposes those commands.
- Using legacy `pico-cli plugin doctor --fix` on an older CLI instead of following
  the finding-specific `nextAction`.
- Declaring MCP fixed from changed `.mcp.json` alone without verifying the actual
  Host-visible tools, or requiring a session restart when the tools already work.
- Replacing `pico-cli setup` with manual plugin file edits as the first repair.
- Running `pico-cli update` / `pico-cli setup` / `pico-cli plugin update` automatically during a
  read-only verify/doctor request.
- Updating from a guessed internal package/scope/registry.

## Reporting format

When you run this skill, report:

1. **Root-doctor evidence**, using the branch actually executed:
   - **Authorized doctor path:** report the overview fields actually returned at the top of
     `pico-cli doctor` output — CLI, Plugin, SDK, PICO development knowledge,
     Emulator, Editor, and managed CLIs when present — as-is, including any `unknown`/`not provisioned`
     rows.
   - **Strictly read-only fallback:** do not synthesize the six overview rows.
     Report:
     - `root doctor: not run (strictly read-only)`
     - `authoritative overview: not verified (root doctor not run)`
     - `catalog freshness: not verified`
     - `SDK–PICO development knowledge alignment: not verified`

     Include any static observations with their source paths and label them
     non-authoritative.
2. **Environment status**: Node/npm, `pico-cli` path, installed version, latest
   version if checked, and whether an update was needed.
3. **Capabilities discovered**: which setup/plugin/MCP/doctor commands the
   installed CLI exposes.
4. **Findings**: each concrete gap with the relevant command output. For a
   Spatial project on the authorized doctor path, compare the SDK and PICO development
   knowledge versions from the Doctor overview as described in Step 5 of the diagnostic flow.
   For Unity, report the configured mode, knowledge selection, and actual package evidence
   separately; the overview's Unity SDK field is not proof of installed SDK packages or
   knowledge alignment. Leave alignment unverified when the package version or its relationship
   to the selected knowledge is unknown. On the strictly read-only fallback, state that
   alignment remains unverified.
5. **Actions taken**: exact install, setup, or update commands and their
   results.
6. **Host activation**: which capabilities work in the current session, which MCP
   needs reconnecting, and whether the Host explicitly requires a session reload.
   After a targeted repair, use the Host's supported discovery or reconnect action
   for the affected MCP only. Require a session reload only when the Host cannot
   pick up MCP changes in the live session.
7. **Next step / handoff**: the smallest next action, or the specialized skill to
   continue with (`pico-cli`, `pico-emulator-usage`,
   `pico-project-setup`, etc.). When the task uses a separate session resource
   root, preserve `--workspace-root` on diagnosis and authorized repair calls.

## Related skills

- `pico-cli` — generic CLI usage and command-family selection once healthy.
- `pico-emulator-usage` — emulator/device lifecycle once prerequisites pass.
- `pico-project-setup` — route authorized Spatial or Unity project development.
