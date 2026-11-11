# pico-dev-knowledge MCP Capability Reference

Reference for all tools exposed by the `pico-dev-knowledge` MCP server. Load this file when a
skill needs precise parameter or behavior details beyond what the AGENTS.md summary provides.

## Server Identity

- **MCP server name:** `pico-dev-knowledge`
- **Launched by:** `pico-cli knowledge:server` (spawns `graphify serve`)
- **Transport:** stdio (stdin/stdout JSON-RPC)
- **Tool discovery:** Host registers tools with platform-specific prefixes. Never hardcode full
  tool names — search the available tool list for names ending in `graph_stats`, `query_graph`,
  and `switch_workspace`.

## Tools

### query_graph

Search the knowledge graph using natural language questions or keywords. Returns relevant nodes
and edges as text context via BFS or DFS traversal.

Use the Host-advertised schema for parameter names, supported options, and ranges.
For traversal selection, request BFS or DFS only through the option that schema
actually exposes; do not guess a `strategy` or `mode` argument. If no traversal
option is exposed, use the tool's default.

| Parameter        | Type            | Required | Description                                                                                                        |
| ---------------- | --------------- | -------- | ------------------------------------------------------------------------------------------------------------------ |
| `question`       | string          | Yes      | Natural language question or keyword search                                                                        |
| `depth`          | integer         | No       | Traversal depth, within the advertised range                                                                       |
| `token_budget`   | integer         | No       | Max output tokens 1–100000                                                                                         |
| `max_degree`     | integer         | No       | Stop traversal at nodes with degree > this value (0=unlimited). Filters hub/super nodes.                           |
| `query_variants` | array of string | No       | Alternate phrasings or rewrites of the same question (max 10). Useful for cross-language or terminology expansion. |
| `sort_by`        | string          | No       | Node sort order: `degree` (hub nodes first) or `relevance` (query targets first)                                   |

**Returns:** Text content with relevant nodes, edges, and traversal context.

### graph_stats

Return summary statistics about the loaded knowledge graph.

| Parameter | Type | Required | Description            |
| --------- | ---- | -------- | ---------------------- |
| (none)    | —    | —        | No parameters required |

**Returns:** Node count, edge count, community count, and confidence breakdown.

**Use cases:**

- Verify the MCP server is live and a graph is loaded.
- Inspect the loaded graph's scope before querying.
- Compare graph size after a workspace switch.

### switch_workspace

Switch to a different graphify-out workspace. Hot-reloads the graph without restarting the MCP
server.

| Parameter   | Type   | Required | Description                                                        |
| ----------- | ------ | -------- | ------------------------------------------------------------------ |
| `workspace` | string | Yes      | Path to the new workspace directory (must contain `graphify-out/`) |

**Returns:** Confirmation of the switch or an error if the workspace is invalid.

**Behavior:**

- Idempotent: switching to the already-active workspace is a no-op.
- One MCP session has exactly one active workspace at a time.
- After an attempted switch, restore the validated baseline under the Skill’s restoration
  protocol. Permission denial stops the workflow and takes precedence over restoration or retry.

## Workspace Model

- A single MCP server session supports one active workspace at a time.
- `graph_stats` reports graph statistics, not the live workspace path. Establish the usable
  disk-selection restore baseline and explicitly activate the target as described in the Skill.
- `switch_workspace` hot-swaps to a different version's data.
- Restore the validated baseline after the query under the Skill’s restoration protocol.
  Permission denial or pending approval stops recovery; report the last confirmed state and
  wait for user instructions without retrying through another execution context. Ordinary
  errors or timeouts may use the main-thread recovery described in Step 4. If that recovery
  remains incomplete, report it without claiming the baseline was restored.
- Workspace paths come from the Agent Vault layout managed by `pico-cli setup`.

## Unavailable State

When no knowledge graph is configured (missing `graphify`, no installed vault, or no
`graph.json`):

- The server completes the MCP handshake normally.
- `tools/list` returns a single stub `graph_stats` tool with description prefixed by
  `[Unavailable]`.
- All `tools/call` invocations return `isError: true` with a diagnostic message.
- The server does not crash — the host sees a connected but empty server.

**Diagnosis:** Run `pico-env-doctor` to identify and repair the missing component. The most
common causes are: graphify binary not installed, no Agent Vault version installed, or
`.pico-env.json` not pointing to a valid workspace.
