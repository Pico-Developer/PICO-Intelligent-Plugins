---
name: pico-env-doctor
description: >-
  Verify-first environment workflow for environment-dependent PICO Spatial
  execution. Must run before tasks that actually execute pico-cli, query the
  pico-dev-knowledge MCP server, install or update plugin/host integration,
  or start PICO emulator/device workflows, and whenever the user asks to verify,
  doctor, health-check, repair, set up, update, or reconnect the PICO Spatial
  agent environment. Reuse a successful result once per host session unless the
  environment may have changed. Repair commands require explicit user
  authorization or a task that clearly asks for setup/update/start behavior.
  Checks whether pico-cli exists and reports the installed version/channel
  state, discovers supported commands before using doctor-style checks, and
  explains host restart requirements.
license: 'Apache-2.0'
allowed-tools: Bash(node --version) Bash(npm --version) Bash(command -v:*) Bash(pico-cli:*)
---

# pico-env-doctor — Verify-first PICO environment workflow

## Scope and trigger policy

Run this skill **first** only for environment-dependent execution tasks, such as:

- Running `pico-cli` commands as part of the requested work.
- Querying the `pico-dev-knowledge` MCP server.
- Installing, setting up, updating, or reconnecting plugin/host integration.
- Starting PICO emulator/device workflows whose success depends on local setup.

Do **not** treat this skill as a universal gate for every Spatial task. It is
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
owned by the `spatial-sdk-update` skill — surface it only when the user
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

## Session reuse rule

Do not rerun the full environment check on every turn. Reuse the latest
successful `pico-env-doctor` result once per host session when all of the
following remain true:

- The current workspace and target host/tooling are the same.
- No setup/update/install/start command has run since the last check.
- No new failure signal suggests the environment changed.
- The user did not explicitly ask to re-verify.

Re-run the skill when any of those conditions is false.

## Repair authorization rule

Read-only diagnosis is allowed whenever this skill is in scope. Repair actions
such as `pico-cli update`, `pico-cli setup`, `pico-cli plugin update`, package
installation, or other environment mutation must only run when one of the
following is true:

- The user explicitly asked to repair, set up, update, reconnect, or fix the environment.
- The task itself clearly requires setup/update/start behavior to complete.

If the user asked only to verify or diagnose, stop after diagnosis and report
the exact repair command that would be appropriate instead of executing it.

## Capability-discovery rule

`pico-cli doctor` is the top-level environment summary when the installed build
exposes it. Treat it as a read-only orchestrator: it should report CLI runtime
health and point to module-specific doctors or fallback commands, not perform
setup, plugin updates, package installs, or long-running MCP launches by itself.

The CLI can grow module doctors over time, but a user's installed build may not
expose every command. Discover capabilities before using them; this keeps the
workflow useful across public, internal, old, and newly released CLI builds.

Start with bootstrap and help discovery when `pico-cli` is available:

```bash
node --version
npm --version
command -v pico-cli || echo "pico-cli not on PATH"
pico-cli --version
pico-cli --help
pico-cli doctor --help
pico-cli setup --help
pico-cli plugin --help
pico-cli plugin doctor --help
pico-cli update --help
pico-cli plugin update --help
pico-cli knowledge --help
pico-cli knowledge doctor --help
```

Before the first invocation of each doctor command selected for the current
check, run that exact command's `--help` form. For example,
`pico-cli --help` does not replace `pico-cli doctor --help`, and
`pico-cli plugin --help` does not replace `pico-cli plugin doctor --help`.
Do not infer support from another command's help or from this Skill's examples.

Do not invoke a doctor command with `--agent-tool` until its own help has shown
the accepted values. A general environment check does not need `--agent-tool`;
omit it unless the user requested a specific Host or the check must inspect one
explicitly. Host display names, executable names, and `pico-cli` identifiers are
different namespaces:

| Host        | Canonical `--agent-tool` | Executable | Accepted alias |
| ----------- | ------------------------ | ---------- | -------------- |
| Claude Code | `claude-code`            | `claude`   | `claude`       |
| Trae CLI    | `traecli`                | `traex`    | none           |

Use the canonical identifier in generated commands. Treat the command's current
`--help` output as authoritative for all other Hosts and aliases; do not derive
an identifier from an executable name. The `claude` compatibility alias belongs
only to the current `--agent-tool` option. The deprecated `--tool` option accepts
canonical Host IDs only, so `--tool claude` is invalid; `trae` remains invalid for
both options.

If the installed CLI exposes doctor commands, prefer JSON for machine-readable
results and plain output for a quick human summary:

```bash
pico-cli doctor --format json
pico-cli plugin doctor --format json
pico-cli knowledge doctor --format json
pico-cli primer doctor --format json
```

Expected doctor JSON shape, when supported, follows the CLI `tool-result`
contract:

```json
{
  "tool_name": "doctor",
  "tool_status": "SUCCESS|PARTIAL|FAILED",
  "summary": "human-readable one-line result",
  "data": {
    "targetPlatform": "spatial|unity|null",
    "hostPlatform": "darwin|linux|win32",
    "checks": [
      {
        "id": "runtime",
        "status": "ok|warn|error|skip",
        "checks": []
      }
    ]
  },
  "errors": [],
  "resources": [],
  "meta": { "format": "json", "truncated": false }
}
```

Root doctor groups `data.checks[]` by intent:

- runtime: host runtime basics, such as Node.js.
- common-doctors: checks shared by Spatial and Unity workflows, such as npm,
  emulator guidance, perf readiness, and MCP knowledge.
- spatial-doctors: Spatial-only checks, such as primer-cli/PICO SDK,
  Spatial Editor, pico-spatial-agentic-tools, and Spatial AGENTS.md routing.
- unity-doctors: Unity-only checks, such as `unity-cli`,
  pico-unity-agentic-tools, and Unity AGENTS.md routing.

### Full-chain version overview (top of doctor output)

`pico-cli doctor` renders a compact version overview at the **top** of its
report, above the grouped checks. This is the single full-chain status board —
there is **no separate `status` command**; do not look for one or invent one.
Read this overview first and report it verbatim; it is the fastest answer to
"what versions am I on across the toolchain".

The overview covers six rows, aggregated read-only from the doctor checks the
run already collected (it triggers no extra capability):

- **CLI**: installed `pico-cli` version.
- **Plugin**: plugin identity/version recorded for the selected effective setup
  scope. This is declared state, not proof of the plugin loaded by the current
  Host session. Read the plugin doctor `data.scope`, `data.envPath`, and per-Host
  findings before acting; when Host records disagree, do not treat the overview's
  single value as a complete machine-wide answer.
- **SDK**: the current bound Spatial SDK/BOM version read from the
  working-directory project (`no spatial project in current directory` /
  `spatial project found, version unresolved` when it cannot be read).
- **PICO development knowledge**: the PICO development knowledge version.
- **Emulator**: the highest installed PICO emulator bundle version.
- **Editor**: the highest installed Spatial Editor version.

In plain output the overview is an `Overview` block of `- <Row>: <value>` lines
(`unknown` when a row cannot be resolved); in JSON it is the `data.overview`
object with `cli`, `pluginName`, `sdk`, `picoDevelopmentKnowledge`, `emulator`,
and `editor` fields. The Emulator and Editor rows come from checks that root
doctor already runs (common-doctors and spatial-doctors), so a normal
`pico-cli doctor` run from a configured Spatial project is enough to populate
all six. You do not need to run `emulator doctor` / `editor doctor` separately
just to fill the overview. In this root-doctor context, a row reads `unknown`
and its check is `[skip]` when that optional tool is not installed; treat that
as "not provisioned yet" rather than a root-doctor failure.

Root doctor selects the effective setup platform automatically. Its optional
`--platform` value asserts the expected configured platform; it never selects
or overrides the target. Run it from the target project directory: a valid
local `.pico-env.json` takes precedence, and the global setup is used only when
no local file exists. If the local file is invalid or has no supported
platform, doctor does not fall back to global state; it runs common diagnostics
plus untargeted plugin diagnostics and asks the user to run `pico-cli setup`:

```bash
pico-cli doctor --format json --platform <spatial|unity>
```

If the assertion differs from setup, root doctor reports `doctor.platform`,
sets `targetPlatform` to `null`, skips both platform-specific sections, and
runs plugin doctor without a target so recorded Host resources remain
observable.

When run outside a project directory, root doctor reports project-context as a
non-blocking setup warning. It never writes to the current directory unless an
authorized fix command is run.

Use status consistently:

- `SUCCESS`: checked areas are healthy.
- `PARTIAL`: CLI is usable, but some optional/module checks warned or were
  skipped.
- `FAILED`: a blocking runtime/setup issue prevents normal use.

When reading plain doctor output, use the bracketed labels as the action signal:

- `[ok]`: healthy.
- `[skip]`: intentionally not checked or optional for the current workflow; do
  not treat this as a failure unless the skipped capability is required for the
  user's task.
- `[warn]`: checked and incomplete, but not an automatic blocking repair. Report
  the finding and `next:` guidance so the developer can decide whether to
  configure that part now.
- `[error]`: a blocking issue. Inspect `repair[]`: `mode=automatic` identifies a
  fix supported by root `doctor --fix`, while `mode=manual` identifies an
  explicit operator action or module-level command. Run either only when the
  repair authorization rule allows it.

For JSON output, treat `status: "error"` the same as a plain `[error]` line.
Use `repair[]`, `errors[]`, the check `details`, and any `nextAction` value to
choose the smallest follow-up command. Do not assume every error is automatically
repairable. Do not continue into emulator/device/MCP/project work while a
required check is `[error]` or `status: "error"`.

Use automatic root or project-context fixes only when their doctor result marks
the repair as supported. Plugin doctor is always read-only; follow its finding's
explicit lifecycle `nextAction` instead of asking doctor to mutate the environment:

```bash
pico-cli doctor --format json --platform spatial --agent-tool <host> --fix
pico-cli project context doctor --agent-tool <host> --fix --format json
pico-cli plugin doctor --agent-tool <host> --format json
```

The same root command diagnoses Unity when the effective setup platform is
Unity:

```bash
pico-cli doctor --format json --platform unity --agent-tool <host> --fix
pico-cli plugin doctor --agent-tool <host> --format json
```

When the effective platform is unknown or the assertion fails, `pico-cli doctor
--fix` makes no changes. Platform selection and its initial state write belong
to `pico-cli setup`.

Plugin doctor reports `agentHosts` from the nearest project-local
`.pico-env.json`; when no project-local record exists, it falls back to
`~/.pico/.pico-env.json`. An explicitly selected Host that is absent from an
existing setup scope is a diagnostic target and receives a plugin install
recommendation. A missing setup env, platform mismatch, or source-channel
handoff receives a setup recommendation. Doctor never executes either command.

Older CLI builds may still expose `plugin doctor --fix`. Do not use that legacy
flag: its repair dispatch differs by version and may invoke broader setup or an
incorrect plugin lifecycle operation. Read the finding and run the current
explicit setup/install/update command instead.

Avoid repair loops. For any one finding, run its authorized repair **at most
once**, then re-run the relevant doctor to re-verify. If the same `[error]` /
`status: "error"` remains, do not run that repair again — and do not switch to a
different command or a re-worded variant hoping to work around the same finding.
Stop and report the remaining blocker, the command already attempted, and the
latest doctor output and exact host-visible error. Many findings are conditions
`pico-cli` cannot fix by re-running (missing toolchain, offline registry, host
trust); repeating commands only wastes effort without resolving them.

If root or module doctor commands are absent, do **not** invent them and do not
treat their absence as a failed environment by itself. Fall back to the supported
checks and repair commands below, then report which doctor-style commands were
unavailable.

## The flow: bootstrap → discover → diagnose → knowledge-version alignment → authorized repair → re-verify

### Step 1 — Bootstrap the runtime and CLI

The CLI cannot diagnose itself if Node.js or `pico-cli` is missing.

```bash
node --version                       # Node.js 20+ required
npm --version                        # useful for public npm install/update paths
command -v pico-cli || echo "pico-cli not on PATH"
pico-cli --version                   # installed CLI version, if present
```

Heal the bootstrap layer before continuing:

- `node` missing or older than 20 → stop and tell the user to install Node.js 20+
  first.
- `pico-cli` not installed → install it through the user's normal channel.
  External/public users can use:
  ```bash
  npm install -g @picoxr/pico-cli
  ```
  Internal users should use their team's configured registry/scope instead.
- `pico-cli` installed but the version is older than the current stable release →
  prefer `pico-cli update` for a same-channel update when the CLI exposes the
  `update` command. Do not jump to `npm install -g` unless `pico-cli update` is
  unavailable or the user explicitly asks for a full reinstall.

### Step 2 — Check the installed `pico-cli` version and channel

Decide the update path by distribution BEFORE running any npm command. Internal
and external builds ship under different scopes and registries, so a public
`npm view`/`npm install` run against an internal install compares to, or
installs, the wrong build and can break the environment.

1. **Prefer the CLI's own read-only doctor path.** If the installed CLI exposes
   `pico-cli doctor`, run it before repair commands. It reports the installed
   version/distribution and available module doctors, but it does **not** yet
   perform a live latest-version lookup — its `cli.version` check reads the
   cached self-update result. First refresh that cache with the read-only
   `pico-cli update --check`, then run `pico-cli doctor` so its version check
   reflects the latest data instead of reporting a skipped/stale
   ("No fresh pico-cli update check is cached") result. Treat the output as
   diagnosis and routing guidance; `update --check` does not install anything,
   so only run an install/update command after the output or the user's request
   makes that action explicit:
   ```bash
   pico-cli update --check --format json    # refresh the version cache (read-only)
   pico-cli doctor --format json --platform <spatial|unity>
   ```
   Run doctor from the target project directory and assert the platform needed
   by the workflow. If `targetPlatform` is `null`, resolve the reported
   assertion/setup problem instead of attempting platform-specific repairs.
2. **Internal / private install** (the CLI did not come from public npm): do NOT
   run `npm view` / `npm install` against a public package. Report the installed
   `pico-cli --version` and ask the user to update through their team's
   configured registry/channel.
3. **Confirmed public install only**: compare against public npm, and update only
   when the installed version is older:
   ```bash
   pico-cli --version
   pico-cli update --check --format json
   pico-cli update --yes --format json
   ```
   Then re-run `pico-cli --version`. Never update when already current.

If you cannot tell which distribution is installed, do not guess a public
update — prefer `pico-cli doctor --format json`, or ask the user which channel
they installed from.

### Step 3 — Discover command support and run available doctors

Inspect the installed command surface before deciding which checks to run:

```bash
pico-cli --help
pico-cli doctor --help
pico-cli plugin --help
pico-cli plugin doctor --help
pico-cli knowledge --help
pico-cli knowledge doctor --help
pico-cli primer --help
pico-cli primer doctor --help
pico-cli setup --help
pico-cli update --help
pico-cli plugin update --help
```

Then:

- If `pico-cli doctor` exists, run it first as the broadest read-only summary:
  use `--platform spatial` for Spatial workflows and `--platform unity` for
  Unity workflows. When the task targets a project directory, run the command
  from that directory so the project-context / AGENTS.md check is included.
- If the root doctor or a module doctor reports `[error]` in plain output or
  `status: "error"` in JSON, stop and follow that check's `next:`/`nextAction`
  guidance before running unrelated commands. Example: plugin inspection errors
  should fix host plugin-list access before retrying; plugin findings should
  route to their explicit setup/install/update next action; primer `[error]`
  should route to primer environment repair; an MCP `[error]` should route to
  MCP/setup verification.
- If module doctors exist (`plugin doctor`, `knowledge doctor`, `primer doctor`), run
  the module that matches the failure. Prefer `--format json` when supported.
- If a module doctor is absent or marked as skipped/planned by root doctor,
  continue with the concrete plugin/MCP/setup checks below and say that the
  installed CLI does not expose that module doctor yet.

Report real output. Do not assume the environment is fine because a help command
succeeded.

### Step 4 — Verify plugin state, then run the explicit lifecycle action

Treat plugin doctor as a read-only decision point. For each finding, use its
exact `nextAction`; do not collapse different findings into one generic repair.
When the CLI itself is outdated, run `pico-cli update` before `pico-cli setup`
or plugin lifecycle commands — keeping the CLI current is a prerequisite for
all downstream commands to work correctly.

**Authorization gate:** only enter this step when the repair authorization rule
above is satisfied. Otherwise, report the exact setup/update command that should
be run and why it is needed, but do not execute it.

Use this mapping:

| Plugin doctor finding            | Explicit action                                                                                                                     |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `PLUGIN_SETUP_REQUIRED`          | Run the reported `pico-cli setup` command so knowledge, platform dependencies, and plugin state are initialized together.           |
| `PLUGIN_NOT_INSTALLED`           | Run the reported `pico-cli plugin install` command for the missing Host in the existing setup scope.                                |
| `PLUGIN_REPAIR_REQUIRED`         | Run the reported `pico-cli plugin install` command to reconcile the same-platform env-recorded resources.                           |
| `PLUGIN_UPDATE_AVAILABLE`        | Run the reported `pico-cli plugin update` command.                                                                                  |
| `PLUGIN_PLATFORM_MISMATCH`       | Run setup and review the complete Host/platform plan; plugin lifecycle commands do not switch platforms.                            |
| `PLUGIN_SOURCE_HANDOFF_REQUIRED` | Run setup to review and authorize the source-to-release handoff.                                                                    |
| `PLUGIN_UPDATE_UNKNOWN`          | Keep current resources unchanged and retry doctor later, or run an explicit update when network access is available and authorized. |
| `PLUGIN_HEALTHY`                 | No mutation.                                                                                                                        |

Current lifecycle command shapes are:

```bash
pico-cli plugin install --scope <local|global> --agent-tool <host> --platform <spatial|unity> [--project <path>]
pico-cli plugin update --scope <local|global> --agent-tool <host> [--project <path>]
pico-cli setup --scope <local|global> --agent-tool <host> --platform <spatial|unity> [--project <path>]
```

Use the scope, Host, platform, and project from doctor output rather than
guessing them. For non-interactive plugin install/setup execution, add `--yes`
only after the authorization gate has been satisfied.

For project-context `[error]`, use the project context doctor fix instead of full
setup:

```bash
pico-cli project context doctor --agent-tool <host> --fix --format json
```

For “fix everything available on this machine” setup requests, or if doctor
reports that the setup environment or setup-owned dependencies are missing, use
the broader setup path. Use plugin update only for Hosts already recorded in an
existing setup scope:

```bash
# Spatial
pico-cli setup --scope global --agent-tool all --platform spatial
pico-cli plugin update --scope global --agent-tool all --platform spatial

# Unity
pico-cli setup --scope global --platform unity --agent-tool all
pico-cli plugin update --scope global --agent-tool all --platform unity
```

Treat a missing host CLI as an actionable skipped host, not as proof that every
host is broken. Tell the user which host command is missing and rerun the
matching setup command after they install that host.

`setup` is the right fallback when plugin setup dependencies are missing because
it owns the initial provisioning path for the plugin, skills, MCP metadata, and
supporting setup resources. Prefer rerunning `setup` over manual edits to host
plugin files.

#### Local installation versus Host activation

A successful local setup proves that managed resources were written, not that
the current Host session loaded them. Before reinstalling a missing local MCP:

- Codex and Trae CLI can discover project configuration but disable it until
  the user trusts that project. Skills may still load, and an existing global
  MCP can remain effective instead of the intended local server.
- Claude Code may show a project `.mcp.json` server as pending approval. Have
  the user review the project MCP prompt in that Host.
- Check the Host's project trust/configuration diagnostics and actual MCP
  command, not only file existence or the setup ledger. After approval, reload
  the Host session and verify the project SDK knowledge again.

Do not grant trust or bypass MCP approval as part of an automatic setup repair.
Report pending Host authorization separately from missing/broken installation.

#### Setup-phase dependencies

`pico-cli setup` also provisions the dependencies spatial skills rely on. Each
dependency finishes with one of three outcomes, and they are not equivalent:

- **warning** — non-blocking. `setup` completes, but the warning marks a residual
  condition `pico-cli setup` cannot fix on its own — a dependency it could not
  install (missing Python toolchain, offline/unreachable registry) or a state it
  could not record (host not trusting the project, a scope pointer it could not
  write). Re-running `setup` does **not** clear it. The user or agent must fix that
  root cause first (install the tool manually, restore connectivity, grant host
  trust), then re-run `setup` **at most once** to confirm. The `uv`, Unity CLI, and
  graphify dependencies surface install failures this way so a single missing tool
  never blocks the rest of setup.
- **skipped** — non-blocking. An optional dependency was not provisioned. Usually
  no action is needed; install it only when a workflow actually requires it.
- **error** — ultimately fatal. The independent setup phases still run to the end,
  but `setup` finishes by throwing a `dependency_failure` (`CliError`) so the run
  fails. This is reserved for the core PICO runtime — a failed `PICO_HOME`/Primer
  runtime or PICO development knowledge (Agent Vault) install — without which the
  environment cannot function. Fix the underlying environment/network cause, then
  re-run; do not loop.

So read the setup log, find the specific dependency and its outcome, and fix that
one root cause instead of re-running `setup` blindly. A single warning does not
mean the whole environment is broken, and repeated `setup` runs will not resolve a
condition that requires a manual fix.

| Dependency                    | What it provides                                     | If it warns / fails                                                                                                                                                                                                  |
| ----------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PICO development knowledge    | The PICO development knowledge the MCP server serves | Core runtime — a hard failure is `error` and fails `setup` with `dependency_failure`. Usually network/registry reachability for the knowledge-pack download; fix connectivity, then re-run `setup` once.             |
| `uv` (Python runtime/manager) | Python environment used by graphify and Python tools | Non-blocking `warning`. Usually missing network or Python toolchain — install a working Python / restore outbound network yourself, then re-run `setup` once. Re-running alone will not install a missing toolchain. |
| graphify                      | Knowledge-graph tooling (depends on `uv`/Python)     | Non-blocking `warning`. Fix `uv`/Python first, then re-run `setup` once. It will not fail `setup`; the run completes with a graphify warning you can act on when knowledge-graph tooling is needed.                  |
| profiler                      | Perfetto/profiler support for `pico-cli perf` work   | Non-blocking for most tasks; re-run `setup` (or `pico-cli doctor`) once when perf workflows are needed.                                                                                                              |

#### On-demand tools (not installed by setup)

The PICO Emulator and Spatial Editor are **on-demand** tools. They are not
required for a healthy base environment and are intentionally **not** installed
by `pico-cli setup`; they are pulled the first time a workflow actually needs
them, which keeps the initial install small. Interpret absence according to the
command entry point:

- Root `pico-cli doctor --platform spatial` treats a cleanly uninstalled
  optional Emulator or Editor as `[skip]`, and its overview row reads `unknown`.
  Report that root-doctor result as "not installed yet; will be pulled on first
  use", not as a base-environment failure.
- Standalone `pico-cli editor doctor` validates Editor readiness specifically.
  If Spatial Editor is not installed, it reports `editor.installation` as
  `[error]`, returns overall `FAILED`, and points to
  `pico-cli editor install -y`. Use this standalone command when the user's task
  requires Editor or explicitly asks to diagnose Editor readiness; do not
  relabel its failure as a benign root-doctor skip.
- Install one only when the user's task actually requires it — for example an
  emulator run/device workflow, or opening the Spatial Editor — or when the user
  explicitly asks to install it. At that point the on-demand pull is triggered
  through the owning workflow (for example `spatial-emulator-usage`), not by this
  skill preemptively.
- Any `[error]`, including standalone Editor doctor's missing-installation
  result, is an actionable finding under the usual authorization rule. Only the
  root doctor's cleanly uninstalled optional-tool state is a benign `[skip]`.

### Step 5 — Verify PICO development knowledge version alignment with the project SDK

When the task targets a specific project directory, the local PICO development knowledge
served by the `pico-dev-knowledge` MCP must match the project's Spatial SDK
line. A mismatch means the MCP answers with a different SDK version's knowledge
than the code the agent is editing, which silently produces wrong API guidance.

Run root doctor from the target project directory, assert Spatial, and use its
overview as the single source of truth:

```bash
pico-cli doctor --format json --platform spatial
```

1. **Read the project SDK version** from
   `data.overview.sdk.version`, then normalize it to `major.minor`
   (`0.13.5` → `0.13`). The Doctor resolves this value from the current project
   directory.
2. **Read the PICO development knowledge version** from
   `data.overview.picoDevelopmentKnowledge`. The Doctor resolves the effective
   project-local/global environment state and prefers the actual
   `agentVaultWorkspace` version when it is present.
3. **Inspect the setup Doctor check** in `data.checks[]` before comparing. If it
   reports inconsistent recorded and workspace versions, treat that warning as
   a real alignment finding and use the overview's workspace-derived PICO
   development knowledge version.
4. **Compare the two `major.minor` values**:
   - **Match** → report this check as `[ok]` (project SDK line and knowledge
     line agree).
   - **Mismatch** → report the finding and prompt the user to align the version
     lines. Do not silently pick one side. The PICO development knowledge is realigned to
     the project SDK line with (subject to the repair authorization rule):
     ```bash
     pico-cli knowledge pull <major.minor> --platform spatial --projectRoot <projectRoot>
     ```
     where `<major.minor>` is the project SDK line read in step 1. This
     rewrites the knowledge keys in `.pico-env.json` (`version`, `platform`,
     `agentVaultWorkspace`) while preserving unrelated project-local keys.
     Passing `<major.minor>` explicitly is preferred here.
   - **Cannot determine one side** (`sdk.status` is `no-project` /
     `unresolved`, or `picoDevelopmentKnowledge` is `null`) → report which
     overview field is unresolved and its Doctor-provided next action instead
     of assuming they match. Use `pico-cli setup` / `pico-cli knowledge pull`
     only when the setup Doctor check identifies missing PICO development
     knowledge.

Skip this step for tasks with no target project directory; without a project
there is no SDK version to align the PICO development knowledge against.

### Step 6 — Verify MCP visibility and launch path

The plugin declares the `pico-dev-knowledge` server in `.mcp.json`, which setup
may translate into a Host-specific configuration. Inspect the Host's effective
server command, arguments, environment, and project working directory before
reproducing a startup failure. A direct CLI check is useful, but is not an
equivalent reproduction unless those launch details match:

```bash
pico-cli knowledge:server
```

An MCP command using `npx` can resolve a different CLI from the one that ran
setup or doctor. Multiple npm installation prefixes and existing npm caches
must be distinguished from a broken plugin or knowledge install. For a known
pico-cli-backed command, compare its version using the same command, package
arguments, registry, and npm prefix, replacing only `knowledge:server` with
`--version`. Do not print credentials while inspecting the environment. An
`npx` invocation may acquire a package, so apply the repair authorization rule
before executing it; otherwise report that runtime selection is unverified.
Changing PATH alone does not establish that the Host uses the intended npm
installation. Do not clear shared npm caches or rewrite portable project
configuration to a personal absolute path as an automatic repair.

This is a stdio server: a healthy run starts and then waits for input (no
immediate exit). Do not run it as an unbounded foreground check in an agent Bash
tool. Use it only as a bounded smoke test when reproducing MCP startup failures:
confirm it starts, then stop it; if it exits with an error, read that error.
When inspecting a plugin payload, check that `.mcp.json` exists, parses, and
contains the expected `pico-dev-knowledge` server entry. In an active agent
host, prefer host-visible MCP status where available, such as `/mcp`, `/doctor`,
`claude --debug mcp`, or the MCP tools exposed in the current session.

Important: `pico-cli knowledge doctor` currently verifies whether the local MCP server
can be resolved and started from the CLI side. It does **not** prove that a
host like Claude, Codex, Cursor, or Trae has already reloaded that MCP config
into the current session. A green knowledge doctor still requires a host restart or a
new session before concluding that the MCP is visible inside the host.

If setup or plugin update changed `.mcp.json` or host plugin registration, the
current session may not see the change. Tell the user to fully restart the host
or open a new agent session before declaring the MCP fixed.

#### MCP connection root causes → fix

When the server is missing or will not connect, match the symptom to the cause
and apply the targeted fix instead of only re-running setup and hoping:

| Root cause                                           | How to spot it                                   | Fix                                                                                                                         |
| ---------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| Host not restarted after setup/update                | MCP only changed after install in this session   | Fully restart the host or open a new session, then re-check.                                                                |
| `node`/`npx` not on `PATH`                           | `node --version` or `command -v npx` fails       | Install Node.js 20+ / fix `PATH`, then retry.                                                                               |
| Launcher cannot fetch the package (offline/registry) | Standalone launch errors while downloading       | Fix network or registry reachability, or install `pico-cli` globally so the host uses the local binary instead of fetching. |
| `pico-cli` too old; `knowledge:server` missing       | `pico-cli knowledge --help` lacks the subcommand | Update `pico-cli` (Step 2), then retry.                                                                                     |
| Knowledge-graph data not provisioned                 | Launch starts but errors on missing graph/data   | Re-run `pico-cli setup` so the PICO development knowledge is pulled (see setup dependencies), then retry.                   |
| `.mcp.json` missing or lacks the server entry        | Inspect the plugin payload `.mcp.json`           | Re-run `setup` for the host to restore the plugin and its `.mcp.json`, then restart.                                        |

Report which root cause applied; do not just say "restarted and hoped".

If MCP still fails after setup/update plus restart, report the relevant doctor output and exact host-visible error.

### Step 7 — Re-verify

After every authorized repair:

1. Re-run the relevant version/help/doctor checks.
2. Re-run host setup/update only if the previous output still shows a concrete
   gap.
3. Ask for or inspect host-visible skill/MCP status after a restart/new session.
4. Report remaining blockers instead of claiming success when the host has not
   reloaded yet.

## Findings → fix quick map

| Finding                                                        | Fix                                                                                                                                                 |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Node missing or older than 20                                  | Install Node.js 20+ before continuing.                                                                                                              |
| `pico-cli` not on `PATH`                                       | Public: `npm install -g @picoxr/pico-cli`; internal: team channel.                                                                                  |
| `pico-cli` version needs review                                | Run `pico-cli update --check --format json`; when authorized, run `pico-cli update --yes --format json`.                                            |
| Unknown `pico-cli` command or option                           | Run help discovery; use only commands the installed CLI exposes.                                                                                    |
| Setup env is missing                                           | Run the setup command in `nextAction`; plugin commands do not initialize knowledge or platform dependencies.                                        |
| Host absent from an existing setup scope                       | Run the explicit plugin install command in `nextAction`.                                                                                            |
| Same-platform env-recorded plugin resources missing or drifted | Run the explicit plugin install command in `nextAction`, then rerun doctor.                                                                         |
| Plugin installed but stale                                     | Run the explicit plugin update command in `nextAction`, then rerun doctor.                                                                          |
| Recorded version drifts from the loaded manifest               | Run the explicit plugin update command in `nextAction` to realign the recorded version, then rerun doctor.                                          |
| Host registry loads the plugin from a different path           | Run the explicit setup command in `nextAction` to rebuild the registry, restart the host/new session, then rerun doctor.                            |
| Platform mismatch or source-channel handoff                    | Run setup and review its complete transition plan; do not combine plugin uninstall/install to switch the environment.                               |
| PICO development knowledge version mismatches project SDK line | Prompt the user to align, then run `pico-cli knowledge pull <major.minor> --platform spatial --projectRoot <projectRoot>` for the project SDK line. |
| MCP server absent or disconnected                              | Re-run setup/update, restart the host/new session, then inspect MCP status.                                                                         |
| Still broken after supported repair plus restart               | Report the relevant doctor output and exact host-visible error.                                                                                     |

## Self-heal rules and safe defaults

- Verify before fixing; re-verify after each fix.
- Discover the installed command surface before using doctor-style commands.
- Update `pico-cli` before running `setup` or `plugin update` when version
  evidence shows it is outdated. Keeping the CLI current is a prerequisite for
  all downstream commands to work correctly.
- Keep plugin doctor read-only. Execute the finding-specific setup/install/update
  command explicitly, then rerun doctor once.
- For a project task, confirm the PICO development knowledge line (`.pico-env.json`
  `agentVaultWorkspace`) matches the project SDK `major.minor`; prompt the user
  to align rather than silently picking a side.
- Reuse a healthy result within the same host session instead of rerunning this
  skill by reflex.
- Do not run repair commands without explicit user authorization or a task that
  clearly requires setup/update/start behavior.
- Restart the host or open a new session after plugin/MCP changes before
  declaring skills or MCP fixed.
- Do not hand-edit host plugin manifests unless `pico-cli setup` cannot support
  the host and the user explicitly asks for manual setup guidance.

## Anti-patterns

- Starting environment-dependent CLI/MCP/emulator work without this environment
  check when setup is suspect.
- Running `pico-cli doctor`, `pico-cli plugin doctor`, `pico-cli knowledge doctor`, or
  `pico-cli primer doctor` without first confirming the installed CLI exposes
  those commands.
- Using legacy `pico-cli plugin doctor --fix` instead of following the current
  finding-specific `nextAction`.
- Declaring MCP fixed in the same session that changed `.mcp.json` without a host
  restart/new session.
- Replacing `pico-cli setup` with manual plugin file edits as the first repair.
- Running `pico-cli update` / `pico-cli setup` / `pico-cli plugin update` automatically during a
  read-only verify/doctor request.
- Updating from a guessed internal package/scope/registry.

## Reporting format

When you run this skill, report:

1. **Full-chain version overview**: the six rows from the top of
   `pico-cli doctor` output — CLI, Plugin, SDK, PICO development knowledge, Emulator, and
   Editor — reported as-is (including any `unknown`/`not provisioned` rows).
2. **Environment status**: Node/npm, `pico-cli` path, installed version, latest
   version if checked, and whether an update was needed.
3. **Capabilities discovered**: which setup/plugin/MCP/doctor commands the
   installed CLI exposes.
4. **Findings**: each concrete gap with the relevant command output. For a
   project task, include the SDK–PICO development knowledge version alignment
   result from the Doctor overview.
5. **Actions taken**: exact install, setup, or update commands and their
   results.
6. **Restart needed?**: whether the user must restart the host or open a new
   session for skills/MCP to load.
7. **Next step / handoff**: the smallest next action, or the specialized skill to
   continue with (`pico-cli`, `spatial-emulator-usage`,
   `spatial-app-onboarding`, etc.).

## Related skills

- `pico-cli` — generic CLI usage and command-family selection once healthy.
- `spatial-emulator-usage` — emulator/device lifecycle once prerequisites pass.
- `spatial-app-onboarding` — project scaffolding after the environment is healthy.
