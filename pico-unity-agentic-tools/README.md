# PICO Unity Agentic Tools

Agentic tools for PICO Unity development (skills, commands, and MCP). Helps AI agents assist with PICO OS 6 Unity Spatial setup, PICO Unity project initialization, PICO XR building-block orchestration, Unity Package Manager workflows, SpatialML, the Unity Hub CLI, device debugging, and PICO CLI device workflows.

## Contents

- **Skills** (`skills/`) — host-loaded workflow and routing guidance for PICO Unity tasks:
  - `pico-unity-init` — initialize a PICO Unity project once, record `mode` as `picoxr`, `openxr`, or `picospatial`, install the required packages, open the project with Android as the target, and then set `pico_unity_init_completed: true` in `.pico-cli/config.json`. **Manual trigger only** (`/pico-unity-init`); ordinary setup or development requests do not activate it automatically. Later explicit invocations skip initialization when that marker is present.
  - `pico-unity-buildingblocks` — orchestrate PICO XR building blocks (XR Origin, VST/Passthrough, Controller, Locomotion, Spatial Mesh, Plane, Hand tracking) in a running Unity Editor via the `pico_xr_*` MCP tools, with MCP pre-check, dependency resolution, domain-reload waits, and scene saving.
  - `pico-unity-package-manager` — manage Unity Package Manager packages and their samples through the `pico_xr_package` MCP tool (`list` / `info` / `add` / `remove` / `update` / `list_samples` / `import_sample`), including guarded post-init repair of recognized official PICO Unity SDK moving Git references, while waiting for the Editor to finish recompiling after every mutating action. These are the exact action tokens; user intents such as "install", "query", "list-samples", and "import-sample" map to `add`, `info`, `list_samples`, and `import_sample`.
  - `develop-pico-unity-apps` — develop, configure, migrate, debug, and optimize XR and spatial apps with PICO Unity SDK 6.0.0: audit a Unity project (read-only inspection script), select among PICO XR / Unity OpenXR / PICO Spatial modes, implement features (controllers, hands, eye/body tracking, passthrough, anchors, spatial mesh, foveated rendering, compositor layers, haptics, spatial camera/input/UI), migrate legacy PICO namespaces, configure Android builds/permissions, and diagnose build/rendering/tracking/device/performance problems.
  - `pico-unity-spatial` — guide PICO Spatial setup, Shared Space / Full Space, spatial UI, Play-to-PICO, and feature discovery; route concrete runtime work to the narrower Spatial Adapter skills.
  - `spatialadapter-runtime-overview` — discover the Spatial Adapter runtime API surface and choose a topic skill.
  - `spatialadapter-scene-setup` — inspect or create the active scene's SpatialCamera without duplicates.
  - `spatialadapter-camera-window-api` — configure SpatialCamera, spatial windows, dimensions, modes, and configuration assets.
  - `spatialadapter-spatial-camera-focus` — keep a moving target inside SpatialCamera bounds.
  - `spatialadapter-input-api` — implement Spatial Input target selection, click / tap / pinch handling, colliders, EnhancedTouch mapping, dragging, and manipulation.
  - `spatialadapter-components-api` — work with native text, video, hover, grounding shadows, collider payloads, and canvas sorting.
  - `spatialadapter-runtime-core-api` — work with runtime initialization, resource registration, mesh synchronization, and dynamic textures.
  - `spatialml` — configure, implement, author, validate, diagnose, and extend SpatialML in an existing PICO Unity project, including pySpatialML-backed package/model tooling, Pipeline Zoo workflows, camera-to-model inference, operator selection, 2D-to-3D placement, XR/Spatial output, synchronization, and readback grounded in the SDK knowledge graph.
- **MCP** (`.mcp.json`) — wires the PICO development knowledge graph through `pico-cli knowledge:server`. Unity Editor tools are provided by the project's Unity MCP bridge rather than this manifest.

## Spatial Workflow

Choose the narrowest Spatial Adapter skill for a concrete API or scene task; use `pico-unity-spatial` for general Spatial setup and `develop-pico-unity-apps` for cross-mode audits, migration, builds, and diagnostics. Check the saved `mode` against installed packages and scene evidence before changing modes.

The Spatial Adapter references describe `ByteDance.PICO.SpatialAdapter`; verify the installed package's version and signatures before generating code. Scene editing needs a running Unity Editor and an available scene-editing tool. The scene-setup example uses `Unity_RunCommand`; if unavailable, report that limitation and use manual Editor steps rather than claiming the scene was changed.

## Create a Unity SpatialML Feature with Natural Language

Describe the result you want; you do not need to name SpatialML or know the commands. A useful prompt includes the input, inference goal, and output:

```text
In this PICO Unity project, use the passthrough camera to detect faces and draw an overlay for each
face. Find and import `picoxr/face-mediapipe-pipeline` through the Unity SDK importer, then build and
verify the app. Explain any manual Editor step in beginner-friendly language.
```

The `spatialml` skill should activate for requests like this because they combine spatial input with model inference and an output. It should not activate for passthrough display, platform hand tracking, spatial mesh, ordinary 3D model assets, or a generic AI assistant by themselves. SpatialML is added to an existing PICO Unity project; if the PICO Unity SDK is missing, invoke `/pico-unity-init` explicitly, then resume the original SpatialML request. If an initialized project's SDK is present but incomplete or stale, use `pico-unity-package-manager` for the guarded Git repair path instead of invoking init again.

## Installation

Install with `pico-cli`. The guided command lets you choose the agent host and resource scope; the scope defaults to `global` in the prompt:

```sh
pico-cli setup --platform unity
```

The `--agent-tool` value is on the left, the CLI it needs on the right. The marketplace root README describes each host's install mechanism:

| Host            | `--agent-tool` | Required CLI                          |
| --------------- | -------------- | ------------------------------------- |
| Claude Code     | `claude-code`  | `claude`                              |
| Cursor          | `cursor`       | Cursor IDE                            |
| Codex           | `codex`        | `codex`                               |
| GitHub Copilot  | `copilot`      | `copilot`                             |
| Trae CLI        | `traecli`      | `traecli`                             |
| OpenCode V2     | `opencode2`    | `opencode2` or verified V2 `opencode` |
| CodeBuddy Code  | `codebuddy`    | `codebuddy`                           |
| Qoder CLI       | `qoder`        | `qoder`                               |
| Antigravity CLI | `antigravity`  | `agy`                                 |
| Grok CLI        | `grok`         | `grok`                                |

The Unity plugin includes Unity Spatial / Spatial Adapter, PICO XR, Unity OpenXR, and SpatialML guidance. Agents choose the right skill from the user's request and project evidence; when the target workflow is ambiguous, they should ask whether the task is for PICO Spatial / Spatial Adapter, PICO XR, or Unity OpenXR.

For non-interactive setup, specify the scope explicitly. Pass any `--agent-tool` value from the table above, or `all` for every host available on this machine:

```sh
# User-level resources available across projects
pico-cli setup --agent-tool claude-code --platform unity --scope global --yes
pico-cli setup --agent-tool all --platform unity --scope global --yes

# Plugin context linked for one project
pico-cli setup --agent-tool claude-code --platform unity --scope local --project /absolute/path/to/project --yes
```

When `--yes` is used without `--scope`, setup defaults to `global`. A `local` setup uses the directory passed with `--project`, or the current directory when `--project` is omitted.

See `AGENTS.md` for agent guidance.

## License

Apache-2.0

## SpatialML service debugging

Use `spatialml-debugging` (`skills/spatialml-debugging/`) for verbose service log capture,
operator failure diagnosis, and explicit global tensor inspection. The workflow checks the actual
SDK and service mode, correlates execution with values, and disables all debug flags afterward.
It explains the service readback permission bypass and resource cleanup.
