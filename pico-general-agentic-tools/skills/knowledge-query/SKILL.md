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

Interactive development knowledge lookup via the `pico-dev-knowledge` MCP server. Asks the user
which platform to query, delegates the full query flow (including workspace switch) to a subagent,
and returns a structured summary without consuming the main conversation's context window.

## When To Use

- User asks a development question that benefits from knowledge-graph search (e.g. "how to
  implement a 3D video player demo", "how does portal component work")
- User explicitly requests knowledge lookup ("search the knowledge base", "query the graph")
- Cross-platform comparison queries ("how does X differ between spatial and unity")
- Broad SDK/API fact lookup that goes beyond bundled skill references

## When NOT To Use

- Trivial questions answerable from project-local code or bundled skill references
- Project-local debugging (build errors, config issues) — route to project evidence
- Environment/setup issues — route to the platform plugin's environment doctor skill
- When `pico-dev-knowledge` MCP tools are unavailable — state the limitation and fall back

---

## MCP Tool Discovery

The MCP server is named `pico-dev-knowledge`. It exposes three tools: `graph_stats`,
`switch_workspace`, and `query_graph`. Different hosts register MCP tools with different name
prefixes, so never hardcode a full tool name. Search your available tool list for names containing
`pico-dev-knowledge` that end in `graph_stats`, `switch_workspace`, and `query_graph`. Use the
matched full names in all subsequent calls. If none of the three tools can be found, the MCP
server is not connected — state the limitation and suggest running `pico-cli setup`.

Record the three discovered full names — they must be passed to the subagent in Step 3.

---

## Main Thread Workflow

The main thread handles platform discovery, user interaction, and tool name discovery.
The query itself is delegated to a subagent when available, or executed inline otherwise.

### Step 1: Discover Available Platforms

Execute via Bash:

```bash
pico-cli knowledge list
```

Parse the output to extract version, platform, and workspace path from each line.

If no entries are returned, inform the user that no knowledge is installed and suggest running
`pico-cli setup`.

### Step 2: Ask User Which Platform

Present available platform+version combinations and ask the user to choose. If only one entry
exists, confirm it with the user rather than forcing a choice.

If the user is already discussing a specific platform and only that platform is installed, skip
the platform question and proceed directly.

### Step 3: Delegate or Execute

If the Agent tool is available, spawn a subagent with the Subagent Prompt Template below.
Otherwise execute the same steps inline in the main thread and inform the user:

> Note: Executing knowledge query inline (subagents not available in this environment).

Pass to the subagent (or use inline):

- The user's original question (verbatim)
- The target platform workspace path
- 2-3 query_variants (alternate phrasings you pre-generate)
- The three discovered MCP tool full names (from MCP Tool Discovery above)

### Step 4: Present Results

When the subagent returns (or inline execution completes), relay the structured summary to
the user directly.

If the subagent times out or errors, check workspace state yourself: call the `graph_stats` tool,
compare against the target workspace, and call `switch_workspace` to restore if needed.

---

## Subagent Prompt Template

The subagent handles the full lifecycle: switch if needed, query, restore, format.

```
You are a knowledge-graph query agent. Complete these steps and return a structured summary.

## Task
Answer: "<USER_QUESTION>"

## Info
- Platform: <PLATFORM>
- Version: <VERSION>
- Target workspace: <TARGET_WORKSPACE_PATH>

## MCP Tools
Use these exact tool names (discovered by the caller):
- graph_stats: <GRAPH_STATS_TOOL_NAME>
- switch_workspace: <SWITCH_WORKSPACE_TOOL_NAME>
- query_graph: <QUERY_GRAPH_TOOL_NAME>

## Instructions

1. Discover the current workspace:
   - Call the graph_stats tool (no arguments)
   - Record the returned workspace path as <CURRENT_WORKSPACE>
   - If unavailable, abort and report that workspace detection failed.

2. Compare: if <TARGET_WORKSPACE_PATH> == <CURRENT_WORKSPACE>, skip to step 4
   (no switch needed—the MCP server is already serving the requested workspace).

3. Switch workspace:
   - Call the switch_workspace tool with workspace="<TARGET_WORKSPACE_PATH>"

4. Query the knowledge graph:
   - Call the query_graph tool with:
     - question: "<USER_QUESTION>"
     - query_variants: [<VARIANT_1>, <VARIANT_2>]
     - mode: "bfs"
     - depth: 3
     - token_budget: 4000

5. Restore workspace (only if switch was performed in step 3):
   - Call the switch_workspace tool with workspace="<CURRENT_WORKSPACE>"
   - IMPORTANT: Always restore, even if earlier steps failed.
   - If restoration fails, retry once, then report the failure with the workspace path.

6. Return in this EXACT format (nothing else):

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

If a workspace switch was performed, the workspace MUST be restored to the captured
pre-query `<CURRENT_WORKSPACE>` after querying, regardless of whether the query succeeded or
failed.

If restoration fails, retry once, then report the failure with the workspace path.

---

## Error Handling

| Situation                      | Action                                                                                |
| ------------------------------ | ------------------------------------------------------------------------------------- |
| No knowledge entries installed | Stop; suggest `pico-cli setup`                                                        |
| MCP tools not found            | State that `pico-dev-knowledge` is not connected; suggest running `pico-cli setup`    |
| `graph_stats` unavailable      | Abort; report that workspace detection failed                                         |
| `switch_workspace` fails       | Report the attempted path; suggest checking `graphify-out/graph.json` exists          |
| `query_graph` returns empty    | Try query_variants; if still empty, ask user to rephrase                              |
| Subagent times out or errors   | Main agent calls `graph_stats`, restores workspace if needed, reports partial results |
