# Host permissions for a configured coding project

Read this after configuring a Spatial or Unity coding project, before its development workflow or a
subagent handoff. The goal is fewer repeated permission interruptions without changing the Host's
authorization rules.

## What actually reduces interruptions

The Host owns all prompting, grant persistence, sandbox enforcement, and subagent permissions.
pico-cli and this Skill never grant permissions, edit Host permission files, or change the sandbox.

If effective permissions already suffice for the task, continue silently: do not display an
authorization checklist, recommend a restart, or request broader grants. Do not create extra
permission probes just to offer this guidance; use existing evidence and the necessary operations.

There is no universal "pre-approve a set of directories and tools" action for a session that is
already running, and Agents cannot register grants on the running Host's behalf. Therefore do not
invent an approval step or ask the user to approve work in the abstract. Common Host-native ways
to reduce repeated prompts include:

1. **Before a new session**: some Hosts document launch options that add workspace directories or
   start a workspace as trusted. Only when repeated operations would benefit and the current Host's
   own help documents a suitably scoped option, optionally mention it once with relevant concrete
   paths below, clearly scoped to a newly started session. Never invent
   flags or copy another Host's options; if the Host documents no such option, say nothing.
2. **During this session**: continue under the Host's existing rules. At a real prompt for an
   operation that will repeat, optionally explain a persistent choice only if the Host actually
   offers one with an appropriate scope. The user may keep per-operation approvals; never require
   or default to "always allow". The Host records any supported persistent choice the user makes.

Workspace trust, filesystem access, and MCP tool approval are separate controls. Explain only
what the Host documents for the offered option; trust does not itself grant writes or MCP calls.

`project configure --yes` answers pico-cli's own confirmation only; it is never a Host permission
grant. User consent never overrides Host or organization restrictions.

## Prepare the concrete paths the task needs

Resolve paths on this machine from structured, read-only diagnostics (`--format json` fields, never
plain text). Reuse setup/doctor/configure results; do not install or repair anything to produce
this list.

- **Project and assets:** resolved project/workspace roots and any user-selected external asset or
  output directory. Code, generated assets, and build outputs may need writes.
- **PICO toolchain and knowledge:** use the effective absolute PICO home from the environment or
  `~/.pico/config.json` (`picoHome`), confirmed by the actual diagnostics. If neither resolves it,
  omit it until a diagnostic supplies the installed location; do not guess a setup directory.
  Doctor reports the common PICO home and Android SDK paths; preserve `--workspace-root <session-root>` when applicable. Knowledge locations
  come from `pico-cli knowledge list --format json` as `workspacePath`; match the selected
  platform/version instead of listing every installed one. Knowledge data and installed tools
  normally need read/execute access only; installs and updates are separate writes.
- **CLI and emulator state:** `~/.pico/cli` holds CLI data; `~/.pico/avd` holds emulator runtime
  state and needs writes when an emulator runs. Include only what the planned commands need.
- **Plugin and Editor caches:** `~/.pico-cli/cache` is distinct from `~/.pico/cli`. It is the default
  plugin working directory; managed plugin staging uses `setup-global/managed-v1` beneath it,
  and Editor downloads use `downloads/editor`. These are candidate locations only: include a
  confirmed, task-relevant subdirectory for plugin installation/update or Editor download work,
  with the needed access, rather than requesting the entire cache directory by default.
- **Other tools and caches:** use actual evidence (for example `primer doctor`, `editor doctor`, or
  `emulator doctor` in JSON) for JDK, Android SDK, Editor/Unity installs, and build caches such as a
  Gradle user home. Do not assume they live under PICO_HOME; keep installed binaries separate from
  writable caches, logs, and runtime state.

Prefer the needed subdirectories over the entire home directory or every toolchain install. If a
path or its required access is unknown, omit it and let the concrete operation prompt later. This
list supports a launch-option suggestion and answers Host prompts accurately; by itself it grants
nothing.

## MCP tool approval is separate from directory access

A connected MCP server or readable graph is not permission to call its tools. Knowledge work uses
`graph_stats`, `query_graph`, and `switch_workspace`; `switch_workspace` changes server state and
must not be described as a read-only query. When offering a future-session launch option that
covers MCP, name these operations; otherwise the user approves them through the Host's normal tool
prompt.

## Offer at most once, then follow the decision

Only if permissions do not already suffice, repeated operations would benefit, and a suitable
Host option is actually available, optionally explain that option and the relevant confirmed paths
once, briefly. Tell the user they may keep normal per-operation approvals. Otherwise continue
without an authorization checklist or restart suggestion. Installed tools alone are not a reason
to request unrelated capabilities.

If the user declines or skips, continue permitted work under the existing rules and do not repeat
the offer in this project/Host context. A later operation may still trigger the Host's normal
prompt; that is expected. If an operation is denied, report that specific blocker; do not retry it
in another execution context, broaden the requested access, or treat a denial as a missing tool.

## Subagents

Pass resolved paths to subagents only as task parameters. A subagent must satisfy the Host's
approval in its own context; do not claim that inherited paths, the parent's grants, or a successful
CLI diagnostic give it sandbox or MCP access. If a Knowledge MCP tool is absent only in the
subagent, the main thread runs the authorized query and returns findings; this is not a reason to
reinstall dependencies or expand access, and it must not be used to bypass an actual denial.

Do not state or imply that one approval persists across sessions, covers every subagent, or makes
unattended execution ready. Let the first necessary operation verify effective access in the real
Host context.
