# PICO Unity Agentic Tools

Agentic tools for PICO Unity development (skills, commands, and MCP). Helps AI agents assist with PICO OS 6 Unity Spatial setup, PICO Unity project initialization, PICO XR building-block orchestration, Unity Package Manager workflows, the Unity Hub CLI, device debugging, and PICO CLI device workflows.

## Contents

- **Skills** (`skills/`) — host-loaded workflow and routing guidance for PICO Unity tasks:
  - `pico-unity-init` — initialize a PICO Unity project (probe empty/non-empty, collect SDK / Unity version / device / business-type preferences, copy the template, install PICO SDK XR / AI Assistant / MCP Extensions, write `.pico-cli/config.json`, and open the project with Android as the target platform). **Manual trigger only** (`/pico-unity-init`).
  - `pico-unity-spatial` — guide Unity PICO Spatial setup and feature routing for PICO OS 6, Shared Space / Full Space, spatial UI, Spatial Input, Play-to-PICO, XR Hands in PICO Spatial, and supported AR Foundation subsets.
  - `spatialadapter-runtime-overview` — choose the right Spatial Adapter runtime topic skill and review the package-level Unity-facing API surface.
  - `spatialadapter-scene-setup` — set up or validate a Unity Spatial / PICO Spatial scene with a `SpatialCamera`.
  - `spatialadapter-camera-window-api` — work with `SpatialCamera`, spatial windows, camera modes, dimensions, metadata, and configuration.
  - `spatialadapter-spatial-camera-focus` — keep a target object inside `SpatialCamera` bounds or make the `SpatialCamera` follow/focus it.
  - `spatialadapter-input-api` — implement Spatial Adapter input, `SpatialInputSupport`, EnhancedTouch mapping, target colliders, and manipulation.
  - `spatialadapter-components-api` — configure native text, video, surface-texture video, hover, grounding shadow, collider payloads, and canvas sorting.
  - `spatialadapter-runtime-core-api` — use `SpatialAdapterRuntime` initialization, resource registration, mesh sync, dynamic textures, and runtime DTOs.
  - `pico-unity-buildingblocks` — orchestrate PICO XR building blocks (XR Origin, VST/Passthrough, Controller, Locomotion, Spatial Mesh, Hand tracking) in a running Unity Editor via the `pico_xr_*` MCP tools, with MCP pre-check, dependency resolution, domain-reload waits, and scene saving.
  - `pico-unity-package-manager` — manage Unity Package Manager packages and their samples through the `pico_xr_package` MCP tool (`install` / `remove` / `update` / `query` / `list-samples` / `import-sample`), including guarded post-initialization repair of recognized official PICO Unity SDK moving Git references, while waiting for the Editor to finish recompiling after every mutating action.
  - `spatialml` — configure, implement, author, validate, diagnose, and extend SpatialML in an existing PICO Unity project, including pySpatialML-backed package/model tooling, Pipeline Zoo workflows, camera-to-model inference, operator selection, 2D-to-3D placement, XR/Spatial output, synchronization, and readback grounded in the SDK knowledge graph.
- **MCP** (`.mcp.json`) — wires the knowledge-graph and Unity Editor MCP servers:
  - `pico-dev-knowledge` (`pico-cli knowledge:server`) — knowledge-graph MCP server for PICO development, indexing docs, API references, and best practices into a searchable graph.
  - `unity` — Unity Editor MCP bridge exposing the seven PICO XR tools: `pico_xr_vst`, `pico_xr_controller`, `pico_xr_locomotion`, `pico_xr_spatial_mesh`, `pico_xr_hand`, `pico_xr_package`, and `pico_xr_status`.

## Create a Unity SpatialML Feature with Natural Language

Describe the result you want; you do not need to name SpatialML or know the commands. A useful prompt
includes the input, inference goal, and output:

```text
In this PICO Unity project, use the passthrough camera to estimate body pose and drive an avatar. Find
and import the closest Pipeline Zoo package through the Unity SDK importer, then build and verify the
app. Explain any manual Editor step in beginner-friendly language.
```

The `spatialml` skill should activate for requests like this because they combine spatial input with
model inference and an output. It should not activate for passthrough display, platform hand tracking,
spatial mesh, ordinary 3D model assets, or a generic AI assistant by themselves. SpatialML is added to
an existing PICO Unity project; if the PICO Unity SDK is missing, invoke `/pico-unity-init` explicitly,
then resume the original SpatialML request. If an initialized project's SDK is present but incomplete
or stale, use `pico-unity-package-manager` for the guarded Git repair path instead of invoking init
again.

## Installation

Install through the `pico-xr` marketplace using your agent host (Claude Code, Codex, Cursor, or GitHub Copilot). The guided command lets you choose the agent host and resource scope; the scope defaults to `global` in the prompt:

```sh
pico-cli setup --platform unity
```

The Unity plugin includes Unity Spatial / Spatial Adapter, PICO XR, Unity OpenXR, and SpatialML guidance. Agents choose the right skill from the user's request and project evidence; when the target workflow is ambiguous, they should ask whether the task is for PICO Spatial / Spatial Adapter, PICO XR, or Unity OpenXR.

For non-interactive setup, specify the scope explicitly:

```sh
# User-level resources available across projects
pico-cli setup --agent-tool claude-code --platform unity --scope global --yes

# Plugin context linked for one project
pico-cli setup --agent-tool claude-code --platform unity --scope local --project /absolute/path/to/project --yes
```

When `--yes` is used without `--scope`, setup defaults to `global`. A `local` setup uses the directory passed with `--project`, or the current directory when `--project` is omitted.

See `AGENTS.md` for agent guidance.

## License

Apache-2.0
