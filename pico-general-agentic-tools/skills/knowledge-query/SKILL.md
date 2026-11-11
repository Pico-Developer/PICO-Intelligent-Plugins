---
name: knowledge-query
description: >-
  Interactive knowledge-base querying for PICO development questions. Delegates
  the actual query work to a subagent to keep main conversation context lean.
  Use when the user asks a development question that requires searching the
  pico-dev-knowledge graph, wants to query a specific platform's knowledge, or
  explicitly says "search the knowledge base" / "query the knowledge graph".
license: 'Apache-2.0'
---

# Knowledge Query

Interactive development knowledge lookup via the `pico-dev-knowledge` MCP server, which the general
plugin installs at the user level. Queries the knowledge selected for the current project by
default, delegates the full query flow (including any workspace switch) to a subagent, and returns a
structured summary without consuming the main conversation's context window.

## When To Use

- User asks a development question that benefits from knowledge-graph search (e.g. "how to
  implement a 3D video player demo", "how does portal component work")
- User explicitly requests knowledge lookup ("search the knowledge base", "query the graph")
- Cross-platform comparison queries ("how does X differ between spatial and unity")
- Broad SDK/API fact lookup that goes beyond bundled skill references
- Automated API lookup, including when the platform is already known

## When NOT To Use

- Trivial questions answerable from project-local code or bundled skill references
- Project-local debugging (build errors, config issues) — route to project evidence
- Environment/setup issues — use general’s `pico-env-doctor` in Spatial, Unity, and standalone
  sessions; preserve the actual project and session resource roots.
- Project creation or SDK setup — use `pico-project-setup`
- CLI command discovery or usage — use `pico-cli`
- When no knowledge can be queried — follow [Fallback](#fallback)

---

## MCP Tool Discovery

When query parameters or connection states need clarification, load
[the MCP capability reference](references/mcp-capability.md). The Host-advertised tool schema
is authoritative for available parameters; the activation, restoration, and permission-denial
protocol below applies to every query.
Automated lookups follow the same activation, query, and restoration protocol; knowing the
platform does not establish the live workspace. When the validated default target matches the
request, use it without an additional platform-confirmation question, as in Step 2.

The MCP server is named `pico-dev-knowledge`. It exposes three tools: `graph_stats`,
`switch_workspace`, and `query_graph`. Different hosts register MCP tools with different name
prefixes and normalize separators: Claude exposes e.g.
`mcp__pico_dev_knowledge__graph_stats` (underscores), while other hosts keep the original
hyphenated server name. Never hardcode a full tool name and never assume hyphens survive.
Search your available tool list for entries whose name:

- **ends in** `graph_stats`, `switch_workspace`, or `query_graph`, and
- **contains** the server identifier in either normalized form: `pico-dev-knowledge`
  (hyphenated) or `pico_dev_knowledge` (underscored).

Use the matched full names in all subsequent calls — pass them through verbatim, do not
re-normalize them. If any required tool is missing, the query protocol is unavailable: do not
invent its name or skip activation/restore. State which tools are missing and follow
[Fallback](#fallback). If only unavailable `graph_stats` is advertised, follow
[Recover an Unavailable Connection](#recover-an-unavailable-connection). When
`pico-cli project detect --format json` reports `userEnvironment.setupComplete: false` or the
current Host is missing from `userEnvironment.generalHosts`, suggest running `pico-cli setup`;
otherwise inspect the Host's MCP status and approval state. Use its supported discovery or
reconnect action for `pico-dev-knowledge`, then verify the advertised tools. A missing tool list
alone does not prove setup ran after the session started. Request a session reload only when the
Host requires it to load the registration; do not make full-session restart the default repair.

Record the three discovered full names — they must be passed to the subagent in Step 3.

### Recover an Unavailable Connection

If only `[Unavailable] graph_stats` is advertised, or a health probe reports that the connection
started in unavailable mode, its diagnostic describes startup state, not current disk state.
Repeat Step 1 with the same project and session resource roots and inspect `pico-cli doctor`
with those roots. Repair missing dependencies only with the existing authorization rules below.
Once the selected graph and graphify are ready, use the Host's supported reconnect / restart-MCP
action for **only `pico-dev-knowledge`**. If disk dependencies are already repaired, reconnect
instead of repeating setup, configure, or downloads. Rediscover all three required tools and
require a successful `graph_stats` probe before resuming Step 3 with a newly validated restore
baseline. The old connection does not reload repaired dependencies. If the Host cannot reconnect,
follow its activation requirements; a full-session restart is not the default repair. Until
recovery succeeds, use [Fallback](#fallback) without switching or querying.

---

## Main Thread Workflow

The main thread handles platform discovery, user interaction, and tool name discovery.
The query itself is delegated to a subagent when available, or executed inline otherwise.

### Step 1: Resolve the Default Target

Execute via Bash:

```bash
pico-cli project detect --format json
```

When the caller supplied an engineering project and a separate session resource root, preserve
both as `--project <target-dir> --workspace-root <session-root>` on detection and root `doctor`
calls (including authorized `doctor --fix`). Without a separate resource root, pass the known
target with `--project`; do not substitute the session cwd for a different requested project.
The returned `knowledge.filePath` identifies the selection owner; a `knowledge use --project`
command targets the directory containing that file, which may differ from the engineering root.

`data.knowledge` is the effective selection: `level` (`project` when the project selected its own
knowledge, otherwise `user`), `version`, `platform`, `workspace`, and `graphExists`. Use that
workspace as the default target only when it is non-null and `graphExists` is true.

The effective workspace recorded on disk is NOT proof of the workspace the server currently serves: a previous
question may have switched it and failed to restore, and the tools never report the live
serving workspace (see Subagent Prompt Template). Use a usable disk selection as the **restore baseline**,
never as proof that a switch can be skipped. Always resolve workspace paths to **absolute**
form: prefer the paths
printed by `pico-cli knowledge list`; if `data.knowledge.workspace` looks relative (for example
`6.1/agent-vault/spatial`), join it with the PICO_HOME path from `pico-cli doctor` or
`pico-cli project detect` before passing it to the subagent.

When `workspace` is `null` or `graphExists` is `false`, the selected knowledge is not usable and is
never a `switch_workspace` target; the MCP server may already serve a user-level selection of the
same platform instead, and never serves another platform's knowledge for the project.
Tell the user that `pico-cli doctor --fix` reinstalls the selected version at the level that owns
the selection without changing the selection. Do not run it without the user's confirmation; until
it runs, follow [Fallback](#fallback) without calling `switch_workspace` or delegating an MCP query.
Do not choose a temporary workspace when the restore baseline is unavailable: the tools cannot
identify the server's live fallback workspace, so restoring it cannot be guaranteed. After an
authorized repair, repeat Step 1 and require a usable baseline before any MCP workspace switch.

### Step 2: Confirm or Change the Target

Use the default target when it exists and the user did not ask for another platform or version.
Still activate that workspace before querying and restore the validated baseline afterward, as in
Step 3; choosing the default does not permit a direct query without activation.

When the user asks for another platform or version, when the question is about the other platform,
list what is installed (only after Step 1 established a usable restore baseline):

```bash
pico-cli knowledge list
```

Parse the output to extract version, platform, and workspace path from each line (the printed
workspace is an absolute path — use it verbatim). Filter by the platform and version the user
requested. If exactly one usable workspace matches, use it without asking the user to repeat that
choice, even when it differs from the default. Ask only when the request leaves multiple plausible
targets. Never substitute the sole installed entry when it does not match the requested target.
If the requested knowledge is missing or no entries are returned, report the missing target and
offer an authorized knowledge pull; until available, follow [Fallback](#fallback). Choosing a query
target does not authorize installation or changing the persistent knowledge selection.

Querying another workspace is a temporary switch for this question only. To change the project's
default knowledge, follow `pico-cli`'s persistent selection procedure with explicit `--project`
selection-owner or `--user`; setup does not need to run
again. The use command pins that version, so later setup and project configure runs keep it.

### Step 3: Delegate or Execute

If the Agent tool is available, spawn a subagent with the Subagent Prompt Template below.
Otherwise execute the same steps inline in the main thread and inform the user:

> Note: Executing knowledge query inline (subagents not available in this environment).

The subagent must verify that the passed MCP tools are present in its own catalog before calling
them. Passing tool names does not grant access. If tools are absent only in the subagent and no
switch was attempted, execute the same workflow inline with the main thread's available tools and
normal permissions; do not repeat delegation or reinstall dependencies.

Permission denial takes precedence over every retry, restoration, reconnect, and main-thread
fallback rule in this Skill. Stop the current MCP workflow; do not retry the denied operation or
delegate it to another execution context. Report the denied operation and the last confirmed
activation/restoration outcome. If a switch succeeded or its outcome is unknown and restoration
is not confirmed, report "restoration incomplete" with the starting and target paths and wait for
the user's further instructions. A denied initial activation is not proof that the workspace changed.

Pass to the subagent (or use inline):

- The user's original question (verbatim)
- The target platform workspace path (absolute)
- The starting workspace path (absolute) — the usable effective disk selection from Step 1;
  the restore baseline, because the tools do not report the serving workspace themselves
- 2-3 query_variants (alternate phrasings you pre-generate)
- The three discovered MCP tool full names (from MCP Tool Discovery above)

### Step 4: Present Results

When the subagent returns (or inline execution completes), relay the structured summary to
the user directly.

Only for ordinary execution errors or timeouts, with no permission denial or pending approval,
recover workspace state yourself: the starting workspace is
the usable restore baseline from Step 1. If a switch was performed for this question, call
`switch_workspace` with the absolute starting workspace path to restore it. Do not try to read
the current workspace from `graph_stats` — it returns graph statistics only, never the workspace.
If it reports an unavailable connection before switching, follow
[Recover an Unavailable Connection](#recover-an-unavailable-connection), then retry the query only
after rediscovery and health verification; there is no workspace switch to restore in that case.

---

## Subagent Prompt Template

The subagent handles the full lifecycle: always activate the target, query, restore, format,
subject to the permission-denial stop rule below.

```
You are a knowledge-graph query agent. Complete these steps and return a structured summary.

## Task
Answer: "<USER_QUESTION>"

## Info
- Platform: <PLATFORM>
- Version: <VERSION>
- Target workspace (absolute): <TARGET_WORKSPACE_PATH>
- Starting workspace (absolute): <STARTING_WORKSPACE_PATH>

## MCP Tools
Use these exact tool names (discovered by the caller):
- graph_stats: <GRAPH_STATS_TOOL_NAME>
- switch_workspace: <SWITCH_WORKSPACE_TOOL_NAME>
- query_graph: <QUERY_GRAPH_TOOL_NAME>

## Instructions

First verify that all three tools above are available in your own tool catalog. If any are absent,
return the missing names without switching workspace; the caller can execute the workflow inline.
Permission denial overrides every retry, restoration, reconnect, and caller fallback rule below.
If any call is denied, stop the MCP workflow without further calls; do not retry it or ask the
caller to repeat it. Report the denied operation and last confirmed activation/restoration outcome,
not a missing tool or unhealthy server. If activation succeeded or its outcome is unknown and
restoration is not confirmed, report "restoration incomplete" with both workspace paths and wait
for the user's further instructions. A denied initial activation does not prove a workspace change.

The MCP tools do not report which workspace they are serving: `graph_stats` returns only graph
statistics (nodes/edges/communities), never a workspace path. The starting workspace is given
above — it is the usable effective disk selection validated by the caller. If the starting
workspace is missing or known to have no graph, abort before any switch; never substitute the
target as the restore baseline or guess the server's fallback path.

1. Health probe:
   - Call the graph_stats tool (no arguments).
   - If it returns a non-permission error, abort the query and report that the knowledge server is unhealthy;
     do not attempt a switch to work around it.
   - If the error says this connection started in unavailable mode, return that exact diagnostic
     and ask the caller to follow Recover an Unavailable Connection: verify disk dependencies,
     reconnect only pico-dev-knowledge, rediscover all three tools, and verify health before retrying.
     Do not repeat setup/downloads based on the historical startup diagnostic.

2. Activate the target workspace BEFORE every query (do not skip by comparing paths):
   - Call switch_workspace with workspace="<TARGET_WORKSPACE_PATH>", the absolute path.
   - The disk effective selection is not live server state: the server may already have been
     switched by another question, so a target equal to the starting path is not proof that a
     switch is unnecessary. Activating it explicitly is cheap and makes the active workspace
     match the question deterministically.
   - Relative paths do not resolve reliably; always pass absolute paths.
   - Verify the response contains "Switched to workspace: <TARGET_WORKSPACE_PATH>" (a no-op
     re-activation is a success too). For non-permission failures, if the response isError or mentions "workspace not found",
     abort the query, restore the validated starting workspace, and report the exact path and
     error — do not guess an alternative path.

3. Query the knowledge graph:
   - Call the query_graph tool using its advertised schema. Supply the question and
     include the following optional settings only when supported:
     - question: "<USER_QUESTION>"
     - query_variants: [<VARIANT_1>, <VARIANT_2>]
     - depth: 3
     - token_budget: 4000
   - Select BFS through the advertised traversal option when available; otherwise
     use the tool's default. Do not invent a `mode` or `strategy` parameter.

4. Restore workspace after every query, unless the permission-denial stop rule applies:
   - Because step 2 always activates the target, always re-activate
     workspace="<STARTING_WORKSPACE_PATH>", the absolute starting path, including when target
     equalled starting (the explicit re-activation is the restore) and regardless of whether the
     query succeeded or failed for non-permission reasons.
   - If restoration fails for a non-permission reason, retry once, then report the failure with
     the workspace path. A restoration denial must not trigger that retry or caller recovery;
     report "restoration incomplete" and wait for the user's further instructions.

5. Return in this EXACT format (nothing else):

### Knowledge Query Results

**Platform:** <platform> | **Version:** <version>

**Summary:**
<2-3 sentence overview answering the question>

**Key Findings:**
1. <finding with relevant API/class/concept>
2. <finding>
3. <finding>

**Code Patterns:**
<relevant code snippets or API usage if found in the graph>

**Related Concepts:**
- <concept> — <brief relevance>

**Explore Further:**
- <suggested follow-up query>
```

---

## Workspace Restoration (Hard Rule)

Permission denial takes priority over this restoration rule: stop automatic MCP calls, including
restoration retries and main-thread recovery. An unresolved authorization prompt is not an ordinary
execution timeout. Report any unconfirmed restoration and wait for the user's further instructions.

Before using the MCP query workflow, require a non-null restore baseline with an existing graph.
If it is unavailable, use Fallback without switching. The target workspace MUST be activated before every query (a path comparison with the disk
effective selection is not allowed, since the tools never report the live serving workspace),
and the absolute starting workspace (the effective selection passed by the caller) MUST be
re-activated after querying, whether the query succeeded or failed for non-permission reasons.

Once a switch has been attempted, restore the validated baseline on non-permission errors or
execution timeouts too, including ordinary target activation errors. Retry a failed restoration
once only for a non-permission failure, then report the failure with the workspace path.

---

## Fallback

When no knowledge workspace can be queried, still answer the question:

After a permission denial, use only already permitted project evidence or bundled references.
Report the denial; do not treat it as a reason to repair dependencies, reconnect, or retry MCP calls.

1. State that the answer does not come from the knowledge graph and why (no MCP connection, no
   installed knowledge, or a missing workspace).
2. Answer from project evidence and the references bundled with the installed PICO Skills, such as
   an installed Spatial `spatial-sdk-guideline` for Spatial SDK API facts.
3. Give the repair action that matches the cause: `pico-cli setup`, `pico-cli knowledge pull`,
   or `pico-cli doctor --fix` for missing dependencies; Host reconnect for `pico-dev-knowledge`
   when dependencies are ready but the connection remains unavailable.

---

## Error Handling

| Situation                                                                  | Action                                                                                                                                                                                 |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Permission denied (takes priority over all rows below)                     | Stop MCP calls; no automatic retry, restore, reconnect, or handoff. Report the denied operation and any incomplete restoration; wait for user instructions.                            |
| No knowledge entries installed                                             | Suggest `pico-cli knowledge pull`; answer through [Fallback](#fallback)                                                                                                                |
| Selected workspace is missing                                              | Suggest `pico-cli doctor --fix`; use Fallback without switching until a usable restore baseline is established                                                                         |
| MCP tools not found                                                        | Inspect Host status/approval; use supported MCP discovery or reconnect, and reload only if required by that Host                                                                       |
| Only unavailable `graph_stats`, or an unavailable-connection health error  | Follow [Recover an Unavailable Connection](#recover-an-unavailable-connection); verify dependencies, reconnect only `pico-dev-knowledge`, rediscover all three tools and verify health |
| `graph_stats` errors for non-permission reasons                            | Abort; report that the knowledge server is unhealthy — do not treat stats absence as workspace state                                                                                   |
| `switch_workspace` fails for non-permission reasons                        | Report the attempted absolute path and error; verify `graphify-out/graph.json` exists for that workspace                                                                               |
| `query_graph` returns empty                                                | Try query_variants; if still empty, ask user to rephrase                                                                                                                               |
| Subagent execution times out or errors, without denial or pending approval | Main agent restores the absolute starting workspace if a switch happened; reports partial results                                                                                      |
