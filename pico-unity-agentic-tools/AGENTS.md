# PICO Unity Agentic Tools Plugin

This repository is a skills plugin for AI coding agents such as Claude Code, Cursor, Codex, and GitHub Copilot.

## Repository Overview

The plugin provides domain-specific guidance for building and maintaining **PICO OS 6** applications in **Unity**.
It ships two kinds of capability:

- **Skills** under `skills/` — prompts plus bundled references for feature orchestration and package management inside a Unity project.
- **CLI capability** — conventions for driving the project through CLI, covering both the `unity` CLI (Unity Hub) and `pico-cli`.

Skills here are not code libraries. They are prompts plus bundled references for implementation and diagnosis work.

## Skill Activation Model

- Treat each skill under `skills/` as self-contained.
- Read `SKILL.md` first and load references only when needed.
- Prefer the most specific skill for the current job instead of mixing multiple skills by default.
- Before ANY `pico_xr_*` MCP call, run the Unity MCP connection pre-check described in `pico-unity-buildingblocks` (Step 0). If no `pico_xr_*` tool is visible, stop and surface the connection warning instead of calling tools.
- After any mutating MCP action (`add` / `remove` / `update` / `import_sample` / `enable` / `configure`), run the post-write settle loop before invoking the next MCP tool — the Editor is domain-reloading.

## Available Skills

| Skill                        | Directory                            | When to use                                                                                                                                                                                                                                                                                                                             |
| ---------------------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pico-unity-buildingblocks`  | `skills/pico-unity-buildingblocks/`  | Orchestrate PICO XR building blocks (XR Origin, VST/Passthrough, Controller, Locomotion, Spatial Mesh) in a running Unity Editor via the `pico_xr_*` MCP tools. Handles MCP pre-check, dependency resolution, domain-reload waits, enable/disable/configure, and scene saving.                                                          |
| `pico-unity-package-manager` | `skills/pico-unity-package-manager/` | Manage Unity Package Manager packages and their samples through the `pico_xr_package` MCP tool (`install` / `remove` / `update` / `query` / `list-samples` / `import-sample`), waiting for the Editor to finish recompiling after every mutating action. Also called internally by `pico-unity-buildingblocks` to satisfy dependencies. |

## Task Routing

- Use `pico-unity-buildingblocks` when the user wants to enable / disable / configure / query any PICO XR feature — passthrough (VST), controllers, locomotion, spatial mesh — or create an XR Origin / XR rig inside a running Unity Editor.
- Use `pico-unity-package-manager` when the task is about installing, removing, updating, querying Unity packages, or listing / importing package samples, and whenever another skill needs to satisfy a package or sample dependency first.
- Always run the Unity MCP connection pre-check before the first `pico_xr_*` call in a session, and the post-write settle loop after every mutating call.
- Do not hand-edit `Packages/manifest.json` for package changes; go through `pico_xr_package`.
- Do not auto-install the PICO SDK from within the building-block flow; if a required prefab is missing, ask the user.

### Example Routing

- "Enable passthrough / turn on VST" -> `pico-unity-buildingblocks`
- "Add controller models to my scene" -> `pico-unity-buildingblocks`
- "Configure locomotion to teleport + continuous" -> `pico-unity-buildingblocks`
- "Enable spatial mesh" -> `pico-unity-buildingblocks` (VST is auto-resolved as a prerequisite)
- "What PICO XR features are currently enabled?" -> `pico-unity-buildingblocks` (`pico_xr_status`)
- "Install XR Interaction Toolkit / XR Hands / Input System" -> `pico-unity-package-manager`
- "Import the Starter Assets sample" -> `pico-unity-package-manager`
- "What version of `com.unity.xr.openxr` is installed?" -> `pico-unity-package-manager`
- "List all installed Unity packages" -> `pico-unity-package-manager`

## Commands

- `/pico-unity-init` — Initialize a PICO Unity project (probe empty/non-empty, collect SDK / Unity version / device / business-type preferences in a single form, copy the template, install PICO SDK XR / AI Assistant / MCP Extensions, write `.pico-cli/config.json`, and open the project with Android as the target platform).
  - **Manual trigger only.** Run it ONLY when the developer explicitly invokes `/pico-unity-init`. Do NOT trigger it passively or automatically — even if the developer says things like "initialize a PICO project", "create a new Unity XR project", or "set up the PICO SDK", wait for the explicit `/pico-unity-init` input.
  - Behavior details live in the command definition; this file only records the trigger contract.

## CLI Conventions

This plugin drives the project through two CLIs. Pick the one that matches the task.

### Platform and Device Info

- Read the current project's platform and target device(s) from `.pico-cli/config.json` in the current path (`$PROJECT_ROOT/.pico-cli/config.json`), written after `/pico-unity-init` completes.
  - `platform` — the build platform (always `android` for PICO devices).
  - `devices` — the target PICO device(s), e.g. `pico swan`, `pico 4 ultra`.
- The presence of this file also indicates the project has already been initialized. When you need platform or device context, read it from here instead of asking the user again.

### `unity` CLI (Unity Hub)

- Used for editor/version/project lifecycle. Common commands:
  - `unity editors --installed` — list locally installed editors.
  - `unity install <version> -m android` — install a new editor bundled with Android Build Support.
  - `unity install-modules -e <version> -m android` — add the Android module to an already-installed editor (check the **Status** column before re-installing).
  - `unity projects add <path>` — register a project into the Unity project list.
  - `unity open <path> --build-target Android` — open the project and switch the Active Build Target to Android.
- **Target platform is always Android.** PICO devices are Android-based; do not build for Windows / macOS / WebGL.
- References:
  - Use Unity CLI: https://docs.unity.com/en-us/hub/use-unity-cli
  - Unity CLI reference: https://docs.unity.com/en-us/hub/unity-cli-reference
  - Release notes: https://docs.unity.com/en-us/hub/release-notes

### `pico-cli`

- Generic PICO CLI for command-family selection, help/version/setup discovery, output formats, device targeting, safe defaults, and first-pass troubleshooting.
- `pico-cli` also backs the `pico-dev-knowledge` MCP server (see below).

## MCP / Unity Editor Integration

`.mcp.json` declares MCP servers that load automatically when the plugin is installed. Two servers are relevant:

- **`pico-dev-knowledge`** — A general knowledge-graph MCP server for PICO development, launched via `pico-cli`. It indexes documentation, API references, and best practices into a searchable graph.

  | Tool               | What it does                                                                                                                                          |
  | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `query_graph`      | Search the knowledge graph with natural-language questions or keywords. Supports `mode` (bfs/dfs), `depth` (1-6), and `token_budget` to bound output. |
  | `switch_workspace` | Hot-reload to a different version's knowledge data without restarting the server.                                                                     |

- **`unity`** — The Unity Editor MCP bridge, exposing the PICO MCP Extensions installed into the Unity project. It surfaces the six `pico_xr_*` tools (`pico_xr_vst`, `pico_xr_controller`, `pico_xr_locomotion`, `pico_xr_spatial_mesh`, `pico_xr_package`, `pico_xr_status`), which must be enabled under `Edit > Project Settings > AI > Unity MCP`. `pico-unity-buildingblocks` and `pico-unity-package-manager` operate entirely through these tools.
  - Requires the Unity Editor to be running with the project open and the bridge status **Running**.
  - Before any `pico_xr_*` call, run the Step 0 connection pre-check from `pico-unity-buildingblocks`; if the client sees 0 `pico_xr_*` tools, stop and ask the user to restart the AI client after confirming the bridge.
  - After every mutating call, run the post-write settle loop before the next MCP call.

## Host Integration Points

- Claude Code: `.claude-plugin/plugin.json`
- Codex: `.codex-plugin/plugin.json`
- Cursor: `.cursor-plugin/plugin.json`
- GitHub (Copilot/Workflow integrations): `.github/plugin/plugin.json`
- MCP config: `.mcp.json`
- Hosts should import this directory as the plugin root and resolve `skills/`, `commands/`, and `.mcp.json` using the relative paths defined in the host manifest.

## Published Layout

```text
.
├── .claude-plugin/                 # Claude Code plugin metadata
├── .codex-plugin/                  # Codex plugin metadata
├── .cursor-plugin/                 # Cursor plugin metadata
├── .github/plugin/                 # GitHub plugin metadata
├── commands/
│   └── pico-unity-init.md          # /pico-unity-init command (manual trigger only)
├── skills/
│   ├── pico-unity-buildingblocks/  # PICO XR building-block orchestration via pico_xr_* MCP tools
│   └── pico-unity-package-manager/ # Unity Package Manager package/sample subsystem via pico_xr_package
│
├── .mcp.json                       # MCP server declarations (pico-dev-knowledge, unity)
├── AGENTS.md                       # This file
├── CLAUDE.md                       # Claude-facing entry file
└── README.md                       # Plugin overview and installation notes
```

## Working Principles

- Use the most relevant skill first, then read only the references needed for the task.
- Always run the Unity MCP connection pre-check before the first `pico_xr_*` call, and never call `pico_xr_*` tools when the pre-check found 0 tools.
- After a mutating MCP action, run the settle loop before chaining the next MCP call; the Editor is reloading.
- Resolve dependencies from the outside in for `enable` / `configure` actions only; skip dependency resolution for `disable` / `status`.
- Keep the target platform on Android for all Unity operations.
- Do not hand-edit `Packages/manifest.json`; do not invent SDK APIs or hard-code package versions unless the user asks.

## Response Pattern

- Building-block work: open with one line stating the action, stream progress as a checklist (✓ / … / ✗) so auto-installs are visible, and close with the checklist. For mutating flows, the last line must reflect Save Scene. Only echo the full `pico_xr_status` table when the request itself is a status query.
- Package work: echo the result `summary`; on `already_present` say "no change made"; on `skipped` echo the `warning` and propose the fix; on `error` echo the error and stop instead of retrying blindly.
- If an MCP call returns `skipped` or `error`, stop, tell the user what blocked the workflow, suggest the next step, and wait — do not silently retry.

## Delivery Checklist

- selected skill and why it was chosen
- MCP pre-check result and any settle-loop waits
- packages/samples installed or changed and their outcome (new / already present / updated)
- feature blocks enabled/disabled/configured and the resulting state
- whether the scene was saved
- verification steps and expected results
