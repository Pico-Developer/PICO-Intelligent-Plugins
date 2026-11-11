# PICO Unity Agentic Tools

Project Skills for PICO Unity development, using the general plugin's shared CLI and MCP services. Helps AI agents assist with PICO OS 6 Unity Spatial setup, PICO Unity project initialization, legacy PICO SDK migration, PICO XR building-block orchestration, Unity Package Manager workflows, SpatialML, the Unity Hub CLI, device debugging, and PICO CLI device workflows.

## Contents

For confirmed `mode=picospatial`, an intent to run the current Unity app on a
PICO physical device or in an Emulator, or inspect its effect selects Play-to-PICO by default. Only an explicit
application packaging or APK request selects the build workflow. Requests such
as "Run it in the emulator and inspect the result" use the SpatialAdapter branch of
`pico-unity-buildingblocks`; the developer does not need to name Play-to-PICO.

- **Skills** (`skills/`) — host-loaded workflow and routing guidance for PICO Unity tasks:
  - `pico-unity-init` — initialize a PICO Unity project once, record `mode` as `picoxr`, `openxr`, or `picospatial`, install the required packages, open the project with Android as the target, and then set `pico_unity_init_completed: true` in `.pico-cli/config.json`. It runs on `/pico-unity-init`, and also automatically when the general plugin's `pico-project-setup` or another Unity Skill finds that a task needs a PICO Unity project that has not completed initialization; you do not need to type the command. Later runs skip initialization when that marker is present.
  - `pico-unity-buildingblocks` — orchestrate PICO XR building blocks (XR Origin, VST/Passthrough, Controller, Locomotion, Spatial Mesh, Plane, Hand tracking) in a running Unity Editor via the `pico_xr_*` MCP tools, with MCP pre-check, dependency resolution, domain-reload waits, and scene saving. SpatialAdapter Play-to-PICO preview selects an existing online ADB device, asks the user when multiple devices are available, and prepares Server, wired/wireless transport and Play Mode.
  - `pico-unity-package-manager` — manage Unity Package Manager packages and their samples through the `pico_xr_package` MCP tool (`list` / `info` / `add` / `remove` / `update` / `list_samples` / `import_sample`), including guarded post-init repair of recognized official PICO Unity SDK moving Git references, while waiting for the Editor only when the result confirms a recompile-triggering change; a missing-package remove returns `data.changed=false` and does not settle. These are the exact action tokens; user intents such as "install", "query", "list-samples", and "import-sample" map to `add`, `info`, `list_samples`, and `import_sample`.
  - `update-pico-unity-sdk` (`skills/update-pico-unity-sdk/`) — migrate projects from the legacy PICO Integration or PICO OpenXR packages to the unified `com.bytedance.pico.xr` SDK. It detects embedded and manifest packages, asks for the target Editor and SDK source before changing files, rewrites backend defines/namespaces/assemblies, adds Unity 6000 MCP prerequisites when applicable, and requires a clean headless compile before the developer completes XR settings and device verification.
  - `pico-unity-spatial` — guide general PICO Spatial setup, Shared Space / Full Space, spatial UI, Play-to-PICO, and supported feature selection; route concrete runtime work to the narrower Spatial Adapter skills.
  - `spatialadapter-runtime-overview` — explore or compare the Spatial Adapter API surface before choosing a topic skill.
  - `spatialadapter-scene-setup` — inspect or create the active scene's SpatialCamera without duplicates.
  - `spatialadapter-camera-window-api` — configure SpatialCamera, spatial windows, dimensions, modes, and configuration assets.
  - `spatialadapter-spatial-camera-focus` — keep a moving target inside SpatialCamera bounds.
  - `spatialadapter-input-api` — implement Spatial Input target selection, click / tap / pinch handling, colliders, EnhancedTouch mapping, dragging, and manipulation.
  - `spatialadapter-components-api` — work with native text, video, hover, grounding shadows, collider payloads, and canvas sorting.
  - `spatialadapter-runtime-core-api` — work with runtime initialization, resource registration, mesh synchronization, and dynamic textures.
  - `spatialml` — configure, implement, author, validate, diagnose, and extend SpatialML in an existing PICO Unity project, including pySpatialML-backed package/model tooling, Pipeline Zoo workflows, camera-to-model inference, operator selection, 2D-to-3D placement, XR/Spatial output, synchronization, and readback grounded in the SDK knowledge graph.
  - `spatialml-debugging` — capture Unity service logs and inspect global tensor outputs; Kotlin debugging uses the Spatial SDK project’s debugging Skill.
- **MCP** — this plugin ships no `.mcp.json`. The user-level general plugin provides `unity-mcp`, `pico-spatial-editor`, and `pico-dev-knowledge` through `pico-cli setup`. Project configure installs platform Skills without writing project MCP entries. `unity-mcp` runs `pico-cli unity mcp`, which starts the Editor relay installed by the Unity AI Assistant package (`com.unity.ai.assistant`); Host loading/approval and Editor readiness are separate checks.

## Spatial Workflow

Choose the narrowest Spatial Adapter skill for a concrete API or scene task, and use `pico-unity-spatial` for general Spatial setup. This published plugin intentionally does not ship a broad cross-mode SDK snapshot skill; check the saved `mode` against installed packages and scene evidence, then select an available specific skill.

Platform names alone route to `pico-unity-spatial` for general setup or feature selection. Concrete tasks use their topic skill directly; explicit API exploration or comparison uses `spatialadapter-runtime-overview`. For `SpatialCamera`, presence or creation uses `spatialadapter-scene-setup`, window configuration uses `spatialadapter-camera-window-api`, and target following uses `spatialadapter-spatial-camera-focus`. Clarify the intended action if only the class name is given.

The Spatial Adapter references describe `ByteDance.PICO.SpatialAdapter`; verify the installed package's version and signatures before generating code. Scene editing needs a running Unity Editor and an available scene-editing tool. The scene-setup example uses `Unity_RunCommand`; if unavailable, report that limitation and use manual Editor steps rather than claiming the scene was changed.

## Create a Unity SpatialML Feature with Natural Language

Describe the result you want; you do not need to name SpatialML or know the commands. A useful prompt includes the input, inference goal, and output:

```text
In this PICO Unity project, use the passthrough camera to detect faces and draw an overlay for each
face. Find and import `picoxr/face-mediapipe-pipeline` through the Unity SDK importer, then build and
verify the app. Explain any manual Editor step in beginner-friendly language.
```

The `spatialml` skill should activate for requests like this because they combine spatial input with model inference and an output. It should not activate for passthrough display, platform hand tracking, spatial mesh, ordinary 3D model assets, or a generic AI assistant by themselves. SpatialML is added to an existing PICO Unity project; if the PICO Unity SDK is missing, the agent runs `pico-unity-init` first, then resumes the original SpatialML request. If an initialized project's SDK is present but incomplete or stale, use `pico-unity-package-manager` for the guarded Git repair path instead of invoking init again.

## Installation

Install with `pico-cli` in two steps. `pico-cli setup` prepares the user environment once and installs the general plugin (`pico-general-agentic-tools`) for the Agent Hosts you choose; it does not install this plugin. The Unity plugin is then installed per Unity project:

```sh
pico-cli setup
pico-cli project configure --platform unity --project /absolute/path/to/unity-project
```

You can also ask the agent to set up the project: the general plugin's `pico-project-setup` skill detects the Unity project and runs `project configure`.

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

For non-interactive first-time setup, choose `--region cn`, `row`, or `us` for your location; `--yes` does not choose a region. Pass any `--agent-tool` value from the table above, or `all` for every supported Host:

```sh
# User level, once per machine
pico-cli setup --region row --agent-tool claude-code --yes

# One Unity project; only Hosts that already have the general plugin can be configured
pico-cli project configure --platform unity --project /absolute/path/to/unity-project --agent-tool claude-code --yes

# Refresh the general plugin and this project's Unity plugin later
pico-cli plugin update --project /absolute/path/to/unity-project
```

`project configure` writes project Skills and managed `AGENTS.md` routing, then returns continuation paths that the Agent can read in the same session. The three MCP servers remain owned by the user-level general plugin; configure does not add project MCP entries. A declared Unity project cannot be switched to Spatial. For an undeclared directory, an explicit platform change switches its recorded project Hosts and reports any partial failure.

See `AGENTS.md` for agent guidance.

## License

Apache-2.0

## SpatialML service debugging

Use `spatialml-debugging` (`skills/spatialml-debugging/`) in Unity projects for verbose service log capture,
operator failure diagnosis, and explicit global tensor inspection. The workflow checks the actual
SDK and service mode, correlates execution with values, and disables all debug flags afterward.
It explains the service readback permission bypass and resource cleanup.

For Kotlin Spatial SDK debugging, use the Spatial `spatialml-debugging` Skill in the Kotlin
project, configuring that project through `pico-project-setup` if needed. Unity debugging does
not require the Spatial plugin.
