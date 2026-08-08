# PICO Unity Agentic Tools

Agentic tools for PICO Unity development (skills, commands, and MCP). Helps AI agents assist with PICO OS 6 Unity project setup, PICO XR building-block orchestration, Unity Package Manager workflows, the Unity Hub CLI, device debugging, and PICO CLI device workflows.

## Contents

- **Skills** (`skills/`) — host-loaded workflow and routing guidance for PICO Unity tasks:
  - `pico-unity-buildingblocks` — orchestrate PICO XR building blocks (XR Origin, VST/Passthrough, Controller, Locomotion, Spatial Mesh, Hand tracking) in a running Unity Editor via the `pico_xr_*` MCP tools, with MCP pre-check, dependency resolution, domain-reload waits, and scene saving.
  - `pico-unity-package-manager` — manage Unity Package Manager packages and their samples through the `pico_xr_package` MCP tool (`install` / `remove` / `update` / `query` / `list-samples` / `import-sample`), waiting for the Editor to finish recompiling after every mutating action.
- **Commands** (`commands/`) — host-loaded slash commands:
  - `/pico-unity-init` — initialize a PICO Unity project (probe empty/non-empty, collect SDK / Unity version / device / business-type preferences, copy the template, install PICO SDK XR / AI Assistant / MCP Extensions, write `.pico-cli/config.json`, and open the project with Android as the target platform). **Manual trigger only.**
- **MCP** (`.mcp.json`) — wires the knowledge-graph server:
  - `pico-dev-knowledge` (`pico-cli mcp:dev-knowledge`) — knowledge-graph MCP server for PICO development, indexing docs, API references, and best practices into a searchable graph.

## Installation

Install through the `pico-xr` marketplace using your agent host (Claude Code, Codex, Cursor, or GitHub Copilot), for example:

```sh
pico-cli setup --plugin pico-unity-agentic-tools
```

See `AGENTS.md` for agent guidance.

## License

Apache-2.0
