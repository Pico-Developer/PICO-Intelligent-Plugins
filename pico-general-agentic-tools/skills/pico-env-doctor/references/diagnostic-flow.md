## The flow: bootstrap → discover → diagnose → knowledge-version alignment → authorized repair → re-verify

## Contents

- [Step 1 — Bootstrap the runtime and CLI](#step-1--bootstrap-the-runtime-and-cli)
- [Step 2 — Check the installed `pico-cli` version and channel](#step-2--check-the-installed-pico-cli-version-and-channel)
- [Step 3 — Discover command support and run available doctors](#step-3--discover-command-support-and-run-available-doctors)
- [Step 4 — Verify plugin state, then run the explicit lifecycle action](#step-4--verify-plugin-state-then-run-the-explicit-lifecycle-action)
- [Step 5 — Verify PICO development knowledge version alignment with the project SDK](#step-5--verify-pico-development-knowledge-version-alignment-with-the-project-sdk)
- [Step 6 — Verify MCP visibility and launch path](#step-6--verify-mcp-visibility-and-launch-path)
- [Step 7 — Re-verify](#step-7--re-verify)

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

1. **Prefer the CLI's own diagnostic doctor path.** If the installed CLI exposes
   `pico-cli doctor`, run it before repair commands. It reports the installed
   version/distribution and available module doctors, but it does **not** yet
   perform a live latest-version lookup — its `cli.version` check reads the
   cached self-update result. First refresh that cache with
   `pico-cli update --check`, then run `pico-cli doctor` so its version check
   reflects the latest data instead of reporting a skipped/stale
   ("No fresh pico-cli update check is cached") result. `update --check` is
   non-installing but stateful: it performs network/process work and writes the
   persistent CLI update cache. It does not prepare scoped plugin-update state.
   In a strictly read-only context, obtain Host write authorization first or skip
   this refresh and report that the cached result may be stale. Treat the
   output as diagnosis and routing guidance, and only run an installing/applying
   update command after the output or the user's request makes that action explicit:
   ```bash
   pico-cli update --check --format json    # non-installing; writes update cache
   pico-cli doctor --format json --project <path> --platform <spatial|unity>
   ```
   For a project task, point doctor at the actual target and assert its platform.
   For standalone tools or knowledge questions, omit `--project` and `--platform` unless the task
   explicitly targets a project. Doctor may still detect a project from the current directory;
   that incidental context does not authorize project configuration or platform-specific repair.
   If a project task reports a `doctor.platform` error or `targetPlatform: null`,
   resolve the target, assertion, or configuration problem before platform-specific repairs.
   A non-null target does not prove the platform assertion passed. Shared capabilities
   can continue with their own verified readiness.
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
pico-cli knowledge --help
pico-cli knowledge doctor --help
pico-cli primer --help
pico-cli primer doctor --help
pico-cli setup --help
pico-cli update --help
pico-cli plugin update --help
```

Then:

- If `pico-cli doctor` exists and its conditional catalog-cache effects are
  authorized, run it first as the broadest top-level summary.
  When the task targets a project, pass `--project <path>` (or run from that
  directory) so the project section, including the AGENTS.md routing check, is
  included; add `--platform spatial` or `--platform unity` to assert the
  platform the workflow needs.
- If the root doctor or a module doctor reports `[error]` in plain output or
  `status: "error"` in JSON, report that finding and its `next:`/`nextAction`. Block only operations that depend on the failed capability; continue independently verified work. Example: plugin inspection errors
  should fix host plugin-list access before retrying; plugin findings should
  route to their explicit setup, project configure, or plugin update next action; primer `[error]`
  should route to primer environment repair; an MCP `[error]` should route to
  MCP/setup verification.
- If module doctors exist (`knowledge doctor`, `primer doctor`), run
  the module that matches the failure. Prefer `--format json` when supported.
  Preserve the diagnosed target: `knowledge doctor` has no project/root flags and uses its
  working directory. Run it with the resolved session resource root as cwd (or the project
  root when those roots match); do not verify session A's selection after diagnosing project B.
  Discover each other module's own target options instead of inventing root-doctor flags.
- If a module doctor is absent or marked as skipped/planned by root doctor,
  continue with the concrete plugin/MCP/setup checks below and say that the
  installed CLI does not expose that module doctor yet.

Report real output. Do not assume the environment is fine because a help command
succeeded.

### Step 4 — Verify plugin state, then run the explicit lifecycle action

Treat the `plugin.doctor` and `project.plugin.doctor` checks as decision points
for explicit lifecycle repair, not as proof that the root doctor command had no
side effects. For each finding, use its exact `nextAction`; do not collapse
different findings into one generic repair. When the CLI itself is outdated, run
`pico-cli update` before `pico-cli setup` or plugin lifecycle commands — strongly recommend updating within the current channel first. Preserve a deliberate pin or
deferred update and continue commands supported by that version; do not silently change channels.

**Authorization gate:** only enter this step when the repair authorization rule
above is satisfied. Otherwise, report the exact setup/update command that should
be run and why it is needed, but do not execute it.

Use this mapping:

| Plugin doctor finding               | Explicit action                                                                                                                                                             |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PLUGIN_SETUP_REQUIRED`             | Run the reported `pico-cli setup` command so knowledge, user-level dependencies, and the general plugin are initialized together.                                           |
| `PLUGIN_NOT_INSTALLED`              | Run the reported `pico-cli setup` (user level) or `pico-cli project configure` (project) command for the missing Host.                                                      |
| `PLUGIN_REPAIR_REQUIRED`            | Run the reported `pico-cli setup` or `pico-cli project configure` command to reconcile the env-recorded resources.                                                          |
| `PLUGIN_PROJECT_CONTEXT_INCOMPLETE` | Non-blocking. Only project Agent routing is missing; run the reported `pico-cli project configure` command when authorized; `doctor --fix` does not change project context. |
| `PLUGIN_UPDATE_AVAILABLE`           | Run the reported `pico-cli plugin update` command.                                                                                                                          |
| `PLUGIN_PLATFORM_MISMATCH`          | Run the reported `pico-cli project configure` command and review the platform change; `plugin update` does not switch platforms.                                            |
| `PLUGIN_SOURCE_HANDOFF_REQUIRED`    | Run setup to review and authorize the source-to-release handoff.                                                                                                            |
| `PLUGIN_SOURCE_MISMATCH`            | Blocking. The user-level plugin source does not match this CLI release, so `project configure` will fail; run the reported `pico-cli setup` command first.                  |
| `PLUGIN_UPDATE_UNKNOWN`             | Keep current resources unchanged and retry doctor later, or run an explicit update when network access is available and authorized.                                         |
| `PLUGIN_HEALTHY`                    | No mutation.                                                                                                                                                                |

Current lifecycle command shapes are:

```bash
pico-cli setup --agent-tool <every Host to keep>
pico-cli project configure --platform <spatial|unity> --agent-tool <host> [--project <path>]
pico-cli plugin update --agent-tool <host>
```

`setup` installs the user-level plugin; `project configure` installs the
project's platform plugin. `setup --agent-tool` is the complete user-level Host
set: a recorded Host left out of the list loses its general plugin, so never
shorten the Host list that doctor reports. Use the Host, platform, and project
from doctor output rather than guessing them. Preserve any explicit `--workspace-root` on
project diagnosis and configuration calls; the engineering and resource roots may differ. For non-interactive setup or
configure execution, add `--yes` only after the authorization gate has been
satisfied.

Follow the finding's `nextAction`: `project.general` requires the reported setup command;
missing or drifted project resources/context may require project configure. Do not apply a
blanket configure rule to every `project.*` finding. Already-tracked managed files require an
authorized Git-index change; configure does not untrack them. Committed legacy MCP/Hook entries
need review of the exact entries and removal only when authorized and no longer needed;
configure preserves unowned entries that teammates may still use. For configure repairs:

```bash
pico-cli project configure --platform <spatial|unity> --project <path> --agent-tool <host> --yes --format json [--workspace-root <session-root>]
```

Reuse the target platform from the original diagnosis. If detection must be repeated, run
`pico-cli project detect --project <path> --format json` with the same engineering target and
append `--workspace-root <session-root>` when provided. Never use a bare cwd-based detection
to choose the platform for another project. Preserve the resource root on configuration as
shown above; it must not silently move Host resources into a nested engineering directory.
When configure reports `CONFIRMATION_REQUIRED`
or `PROJECT_PLATFORM_CONFLICT`, stop and ask the user instead of switching
platforms.

For “fix everything available on this machine” setup requests, or if doctor
reports that the setup environment or setup-owned dependencies are missing, use
the broader setup path. Standalone repair needs no project configuration or platform
selection. Use plugin update only for Hosts already recorded by setup or project configuration:

```bash
# The Hosts reported by doctor plus the Hosts the user wants to add
pico-cli setup --agent-tool <every Host to keep> --yes
```

Re-verify after setup. Run plugin update only for a remaining update finding with its scope
reviewed: the command covers the user-level plugin and the configured project selected by its
working directory or `--project`. Do not silently update an unrelated current project during a
standalone repair.

Only when the original task also authorizes project development or project configuration,
continue through `pico-project-setup` with the intended project and resource roots. Do not
configure the current directory merely because user-level setup was repaired.

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
  command, not only file existence or the setup ledger. After approval, use the
  Host's supported discovery or affected MCP reconnect and verify the project SDK
  knowledge again. Reload the session only if that Host requires it.

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
  graphify dependencies surface install failures this way. Primer/PICO_HOME and
  PICO development knowledge failures also become warnings after general is installed;
  follow their `pico-cli doctor --fix` retry action after addressing the cause.
  Verify the affected capability before using it; unrelated tasks may continue.
- **skipped** — non-blocking. An optional dependency was not provisioned. Usually
  no action is needed; install it only when a workflow actually requires it.
- **error** — fails setup with `dependency_failure` after the independent phases
  finish. In the current setup, Primer/PICO_HOME, Knowledge, Unity CLI, uv, and Graphify
  preparation are warnings once the general plugin is installed; a dependency
  error is reserved for failures that keep setup from completing, such as managed
  CLI preparation. Read the reported dependency name; the warning
  bullets above describe non-fatal outcomes and must not be called fatal.

So read the setup log, find the specific dependency and its outcome, and fix that
one root cause instead of re-running `setup` blindly. A single warning does not
mean the whole environment is broken, and repeated `setup` runs will not resolve a
condition that requires a manual fix.

| Dependency                    | What it provides                                     | If it warns / fails                                                                                                                                                                                                                      |
| ----------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PICO development knowledge    | The PICO development knowledge the MCP server serves | Non-blocking setup `warning`; verify Knowledge readiness before querying. Fix the reported download/environment cause, then follow `pico-cli doctor --fix` and verify MCP query tools.                                                   |
| `uv` (Python runtime/manager) | Python environment used by graphify and Python tools | Non-blocking `warning`. Usually missing network or Python toolchain — install a working Python / restore outbound network yourself, then re-run `setup` once. Re-running alone will not install a missing toolchain.                     |
| graphify                      | Knowledge-graph tooling (depends on `uv`/Python)     | Non-blocking `warning`. Fix `uv`/Python first, then re-run `setup` once. It will not fail `setup`; the run completes with a graphify warning you can act on when knowledge-graph tooling is needed.                                      |
| profiler                      | Perfetto/profiler support for `pico-cli perf` work   | Inspect `pico-cli perf --envelope doctor check`; for required missing dependencies, follow its authorized install action (such as `pico-cli perf doctor install --all`). Setup and ordinary doctor do not install profiler dependencies. |

#### On-demand tools (not installed by setup)

The PICO Emulator and Spatial Editor are **on-demand** tools. They are not
required for a healthy base environment and are intentionally **not** installed
by `pico-cli setup`; they are pulled the first time a workflow actually needs
them, which keeps the initial install small. Interpret absence according to the
command entry point:

- Root `pico-cli doctor` in a Spatial project treats a cleanly uninstalled
  optional Emulator or Editor as `[skip]`; its JSON overview value is null and the plain
  overview row is omitted. Report "not installed yet" and use the authorized on-demand
  workflow when required, not a base-environment failure.
- Standalone `pico-cli editor doctor` validates Editor readiness specifically.
  If Spatial Editor is not installed, it reports `editor.installation` as
  `[error]`, returns overall `FAILED`, and points to
  `pico-cli editor install -y`. Use this standalone command when the user's task
  requires Editor or explicitly asks to diagnose Editor readiness; do not
  relabel its failure as a benign root-doctor skip.
- Install one only when the user's task actually requires it — for example an
  emulator run/device workflow, or opening the Spatial Editor — or when the user
  explicitly asks to install it. At that point the on-demand pull is triggered
  through the owning workflow (for example `pico-emulator-usage`), not by this
  skill preemptively.
- Any `[error]`, including standalone Editor doctor's missing-installation
  result, is an actionable finding under the usual authorization rule. Only the
  root doctor's cleanly uninstalled optional-tool state is a benign `[skip]`.

### Step 5 — Verify PICO development knowledge version alignment with the project SDK

For Unity, report the configured mode and Unity knowledge selection separately from SDK package
evidence in `Packages/manifest.json`, `Packages/packages-lock.json`, and installed package metadata.
The overview's Unity SDK field currently reads only root `package.json.version`; it does not
establish the installed SDK package version or knowledge alignment. If the actual version or its
relationship to the selected knowledge cannot be established, report alignment as unverified;
do not invent a version mapping, infer a Spatial BOM line, or impose Spatial SDK/ROM checks on
picoxr/openxr. For standalone questions, use `knowledge-query` with the requested platform/version
without project configure.

For a configured Spatial SDK project only, the local PICO development knowledge
selected on disk for `pico-dev-knowledge` must match the project's Spatial SDK line. This step
verifies disk selection only, not the graph an already-connected MCP currently serves. Before any
query, use the general plugin's `knowledge-query` Skill with the engineering
`--project <target-dir>` and distinct resource `--workspace-root <session-root>`; its live activation,
query, and restore protocol also applies after configure or an authorized knowledge repair.

Choose one evidence path before claiming version alignment:

- **Authorized doctor path:** use this path only when the task permits root
  doctor's conditional catalog-cache effects or Host write and network access
  have been authorized. Run root doctor from the target project directory,
  assert Spatial, and use its overview as the authoritative snapshot for this
  run.
- **Strictly read-only fallback:** do not run root doctor because it may prepare
  the release catalog cache. On an older CLI that still exposes standalone
  `plugin doctor`, skip that command for the same reason. Read only
  static local records: the project's SDK declaration, the nearest project-local
  `.pico-env.json` (or `~/.pico/.pico-env.json` when no project-local record
  exists), the Host's local plugin manifest or registry entry, and installed
  plugin files. Label their values as non-authoritative static observations.
  Explicitly report that root doctor was not run, the authoritative overview was
  not verified, catalog freshness was not verified, and SDK–PICO development
  knowledge alignment was not verified. Do not infer a match or mismatch and do
  not synthesize the six overview rows from those records.

On the authorized doctor path, run:

```bash
pico-cli doctor --format json --project <path> --platform spatial
```

If the calling setup/onboarding flow supplied a separate resource workspace, append the same
`--workspace-root <session-root>` to this command and to authorized `doctor --fix` calls. Preserve
the engineering root for SDK evidence and the resource root for Host/Knowledge state. Do not
reconfigure the child project just because a diagnosis omitted the workspace parameter.

1. **Read the project SDK version** from
   `data.overview.sdk.version`, then normalize it to `major.minor`
   (`6.1.9` → `6.1`). The Doctor resolves this value from the current project
   directory.
2. **Read the PICO development knowledge version** from
   `data.overview.picoDevelopmentKnowledge`. The Doctor resolves the effective
   knowledge selection (project, otherwise user level) and prefers the actual
   `agentVaultWorkspace` version when it is present.
3. **Inspect the setup Doctor check** in `data.checks[]` before comparing. If it
   reports inconsistent recorded and workspace versions, treat that warning as
   a real alignment finding and use the overview's workspace-derived PICO
   development knowledge version.
4. **Compare the two `major.minor` values**:
   - **Match** → report this check as `[ok]` (project SDK line and disk knowledge
     selection agree; live MCP workspace is not verified by doctor).
   - **Mismatch** → report the finding and prompt the user to align the version
     lines. Do not silently pick one side. The PICO development knowledge is realigned to
     the project SDK line with (subject to the repair authorization rule):
     ```bash
     pico-cli knowledge pull <major.minor>
     pico-cli knowledge use <major.minor> --project <resourceRoot>
     ```
     where `<major.minor>` is the project SDK line read in step 1 and `<resourceRoot>` is the
     configured resource workspace (the engineering root when no separate workspace was used). This
     downloads the knowledge data; only the use command rewrites the knowledge selection keys in `.pico-env.json` (`version` and
     `agentVaultWorkspace`) while preserving the configured `platform` and unrelated project-local keys.
     The use command also pins that version: later `pico-cli setup`, `project configure`, and
     `doctor --fix` runs keep it instead of moving to the latest knowledge.
     Passing `<major.minor>` explicitly is preferred here.
   - **Cannot determine one side** (`sdk` is `null` because no target platform
     resolved, `sdk.status` is `no-project` / `unresolved`, or
     `picoDevelopmentKnowledge` is `null`) → report which
     overview field is unresolved and its Doctor-provided next action instead
     of assuming they match. Use `pico-cli setup` or the `knowledge pull` then `knowledge use` sequence
     only when the setup Doctor check identifies missing PICO development
     knowledge.

Skip this step for tasks with no target project directory; without a project
there is no SDK version to align the PICO development knowledge against. This
does not remove the reporting requirement to distinguish a doctor-backed
overview from the strictly read-only fallback.

### Step 6 — Verify MCP visibility and launch path

The general plugin, which `pico-cli setup` installs once per user, declares the
`pico-dev-knowledge` server in its `.mcp.json`; setup may translate it into a
Host-specific configuration. Platform plugins do not ship this server. A
project MCP file that still declares its own `pico-dev-knowledge` entry shadows
the user-level server; `pico-cli project detect --format json` with the same explicit
project/workspace-root pair used for diagnosis lists such entries under `data.legacy.committedEntries`. When the project's selected
knowledge version is not installed, the server serves the user-level selection
of the same platform and adds a startup fallback note to `graph_stats`; that note is not
proof of the live workspace after subsequent switches. `pico-cli knowledge doctor`
reports the same case as `KNOWLEDGE_SELECTION_SKIPPED`. A project of another
platform, such as Unity next to a Spatial user-level selection, gets no
fallback and reports missing knowledge data that `pico-cli doctor --fix`
installs for the project. Inspect the Host's effective
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
When inspecting a plugin payload, check that the general plugin's `.mcp.json`
exists, parses, and contains the expected `pico-dev-knowledge` server entry. In an active agent
host, prefer host-visible MCP status where available, such as `/mcp`, `/doctor`,
`claude --debug mcp`, or the MCP tools exposed in the current session.

Important: `pico-cli knowledge doctor` currently verifies whether the local MCP server
can be resolved and started from the CLI side. It does **not** prove that a
host like Claude, Codex, Cursor, or Trae has loaded that MCP config into the current session.
Verify the advertised tools in the current Host before concluding that the MCP is visible.
If they are already callable, continue in the same session.

If setup or plugin update changed `.mcp.json` or host plugin registration, the
current session may not see the change. Inspect Host approval and connection status, then use
its supported discovery or reconnect action for the affected MCP only. Ask for a session reload
only when that Host requires it to discover the registration. Do not prescribe a full-session
restart merely because setup, update, or project configure ran. Continue file/CLI work while an
MCP-dependent step is blocked, and report the exact missing capability.

#### MCP connection root causes → fix

When the server is missing or will not connect, match the symptom to the cause
and apply the targeted fix instead of only re-running setup and hoping:

| Root cause                                           | How to spot it                                    | Fix                                                                                                                                                                                                                                                                                     |
| ---------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Host has not loaded changed registration             | Required tools absent after setup/update          | Check approval and use supported discovery/reconnect for that MCP; reload the session only if the Host requires it.                                                                                                                                                                     |
| `node`/`npx` not on `PATH`                           | `node --version` or `command -v npx` fails        | Install Node.js 20+ / fix `PATH`, then retry.                                                                                                                                                                                                                                           |
| Launcher cannot fetch the package (offline/registry) | Standalone launch errors while downloading        | Fix network or registry reachability, or install `pico-cli` globally so the host uses the local binary instead of fetching.                                                                                                                                                             |
| `pico-cli` too old; `knowledge:server` missing       | `pico-cli knowledge --help` lacks the subcommand  | Update `pico-cli` (Step 2), then retry.                                                                                                                                                                                                                                                 |
| Knowledge-graph data not provisioned                 | Launch starts but errors on missing graph/data    | Follow the knowledge finding's owner-aware repair, using authorized `pico-cli doctor --fix` with the same project/workspace roots when supported. Preserve its platform/version; user-level setup does not repair an arbitrary project selection. Then verify the graph and Host tools. |
| `.mcp.json` missing or lacks the server entry        | Inspect the general plugin's `.mcp.json`          | Restore general through authorized setup; use the Host's supported discovery/reconnect and verify tools.                                                                                                                                                                                |
| Project selection skipped                            | `KNOWLEDGE_SELECTION_SKIPPED` in knowledge doctor | Repair using the same project/resource roots; use knowledge-query to activate the repaired workspace on the connected MCP.                                                                                                                                                              |

Report which root cause applied; do not just say "restarted and hoped".

If MCP still fails after the targeted repair and supported reconnect, report the relevant doctor output and exact Host-visible error.

### Step 7 — Re-verify

After every authorized repair:

1. Re-run the relevant version/help/doctor checks.
2. Re-run host setup/update only if the previous output still shows a concrete
   gap.
3. Inspect actual Host-visible skills and MCP tools; continue in the same session
   when the required capabilities are callable.
4. If capabilities remain missing, inspect authorization and use supported
   discovery or reconnect for the affected MCP. Report remaining blockers; a
   session reload is needed only when the Host requires it.
