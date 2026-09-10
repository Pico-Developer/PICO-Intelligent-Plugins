# PICO Spatial Agentic Tools Plugin

Plugin manifests, skills, and MCP configuration for PICO OS 6 spatial development workflows.

## What is this?

`pico-spatial-agentic-tools` is a distributable plugin payload for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Cursor](https://cursor.com), [Codex](https://developers.openai.com/codex/), [GitHub Copilot](https://docs.github.com/en/copilot), and Trae CLI. It bundles host plugin manifests, reusable skills, and MCP configuration to help developers bootstrap, build, migrate, and diagnose PICO OS 6 spatial applications.

## Intended Audience (External Developers)

This repository is for developers building **PICO OS 6** spatial apps who want reusable agent skills to:

- bootstrap a first working project from templates
- speed up day-to-day Spatial SDK development and debugging
- implement or repair code-defined Kotlin Entity scenes with bounds-aware placement
- author and package 3D scenes through Spatial Editor
- place content onto detected real-world surfaces such as walls, tables, and floors
- upgrade or migrate older Spatial SDK projects safely
- diagnose on-device Spatial App performance bottlenecks with `pico-cli perf` and Perfetto Trace
- add SpatialML to existing Unity, Kotlin Spatial SDK, and Native OpenXR apps
- discover, adapt, and install reusable SpatialML Pipeline Zoo packages through each SDK's package
  loader

## End-to-End Setup Flow

Follow this flow before asking your AI agent to use the PICO Spatial skills.

### 1. Install prerequisites

Install Node.js 18+ and at least one supported agent host CLI.

| Host           | Required CLI | Public setup status                                                                                                                                          |
| -------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Claude Code    | `claude`     | `pico-cli setup` can register the marketplace and install the plugin.                                                                                        |
| Cursor         | Cursor IDE   | `pico-cli setup` is supported today; it installs the plugin locally using `.cursor-plugin` manifests because public Cursor marketplace flow is not used yet. |
| Codex          | `codex`      | `pico-cli setup` registers the `.agents/plugins/marketplace.json` marketplace and installs or updates the plugin.                                            |
| GitHub Copilot | `copilot`    | `pico-cli setup` can register or refresh the marketplace and install or update the plugin.                                                                   |
| Trae CLI       | `traecli`    | `pico-cli setup` can add the local marketplace and install or update the plugin through Trae CLI marketplace commands.                                       |

Install `pico-cli`:

```bash
npm install -g @picoxr/pico-cli
```

Verify the commands you need are on `PATH`:

```bash
pico-cli --version
claude --version     # for Claude Code
codex --version      # for Codex
copilot --version    # for GitHub Copilot
traecli --version    # for Trae CLI
```

### 2. Run guided setup

The recommended path is the interactive setup flow:

```bash
pico-cli setup
```

`pico-cli setup` prints a plan, lets you choose supported agent hosts and a resource scope, and configures the hosts available on your machine. The scope defaults to `global` in the prompt. Choose `local` to link plugin context only from a specific project. Missing optional host CLIs are skipped with guidance; install that host later and rerun setup when needed.

For non-interactive or host-specific setup, pass explicit options:

```bash
pico-cli setup --agent-tool claude-code --platform spatial --scope global --yes
pico-cli setup --agent-tool cursor --platform spatial --scope global --yes
pico-cli setup --agent-tool codex --platform spatial --scope global --yes
pico-cli setup --agent-tool copilot --platform spatial --scope global --yes
pico-cli setup --agent-tool traecli --platform spatial --scope global --yes
pico-cli setup --agent-tool all --platform spatial --scope global --yes

# Project-local setup
pico-cli setup --agent-tool claude-code --platform spatial --scope local --project /absolute/path/to/project --yes
```

`global` installs user-level plugin resources that can be used across projects and is also the default when `--yes` is used without `--scope`. `local` links plugin context for the directory passed with `--project`, or for the current directory when `--project` is omitted.

Codex setup uses this marketplace root's `.agents/plugins/marketplace.json` and installs the plugin with a qualified selector such as `pico-spatial-agentic-tools@pico-xr`. Cursor public setup is already supported and currently installs this plugin as a local plugin using `.cursor-plugin` manifests; it does not depend on a public Cursor marketplace flow. Trae CLI public setup adds this repository as a local marketplace and installs or upgrades the plugin from that marketplace.

```bash
codex plugin marketplace add <marketplace-root>
codex plugin add pico-spatial-agentic-tools@pico-xr
```

### 3. Start a new agent session

Close and reopen the configured host, or start a new agent session from your project directory. The new session should load:

- the host marketplace/plugin manifest
- skills under `skills/`
- MCP servers from `.mcp.json`

A quick smoke test is to ask the agent:

```text
Which PICO Spatial skills are available, and when should I use each one?
```

### 4. Keep the plugin updated

Update one host in global scope:

```bash
pico-cli plugin update --agent-tool claude-code --platform spatial --scope global
pico-cli plugin update --agent-tool cursor --platform spatial --scope global
pico-cli plugin update --agent-tool codex --platform spatial --scope global
pico-cli plugin update --agent-tool copilot --platform spatial --scope global
pico-cli plugin update --agent-tool traecli --platform spatial --scope global
```

Update all Agent Hosts recorded in global scope:

```bash
pico-cli plugin update --agent-tool all --platform spatial --scope global
```

Update the Spatial plugin for Codex in the current project:

```bash
pico-cli plugin update --agent-tool codex --platform spatial --scope local --project .
```

`plugin update` requires `--scope global|local` and only reads records from the
explicitly selected scope. `--scope local --project .` selects the current project's
`.pico-env.json`; `--scope global` selects global plugin records. `all` updates only
Hosts recorded in that scope; it does not install unconfigured Hosts or merge
project-local and global records.

## External Workflow Prerequisites

Some advertised routes cross into capabilities owned by another plugin or MCP server. They are not
bundled or provisioned by `pico-spatial-agentic-tools`:

| Route                                                                                | External prerequisite                                                                                  | Behavior when absent                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Create a new Unity SpatialML app                                                     | **PICO Unity Agentic Tools** (`pico-unity-agentic-tools`) with the manual-only `pico-unity-init` skill | If Unity was explicitly requested, report `BLOCKED` and explain that the Unity plugin must be installed and the agent host restarted. If the SDK is still undecided and the workspace is empty, the agent may disclose that Unity is unavailable and offer Kotlin Spatial SDK instead; it must not switch SDKs silently. |
| Repair an initialized Unity SDK or recover a missing SpatialML Pipeline Zoo importer | **PICO Unity Agentic Tools** with `pico-unity-package-manager`                                         | Continue CLI-only checks that do not need Unity-owned mutation, but report `BLOCKED` before a repair/importer handoff when the skill is unavailable. Do not route an initialized project back to `pico-unity-init`.                                                                                                      |

The agent must inspect the live available skill/tool inventory before promising one of these routes.
Installing the Unity plugin is a separate host-environment operation. In particular, do not assume
that `pico-cli plugin install` can add it beside an existing Spatial platform record: one configured
scope records one plugin platform, and cross-platform plugin install is rejected. Running
`pico-cli setup --platform unity` can switch the complete configured environment for that scope.
Review the setup plan, choose the intended scope and host, and start a new agent session after the
Unity plugin is available.

## Create a SpatialML App with Natural Language

You do not need to know SpatialML commands before asking an AI assistant for a feature. Describe the
experience in ordinary language and, when you can, include the parent SDK, input, inference goal, and
visible result. The assistant should route the request through the parent SDK, SpatialML setup, the
closest reusable Pipeline Zoo package, app integration, and emulator/device verification.

For example:

```text
I am new to PICO development. Build a Kotlin Spatial SDK app that detects faces from the passthrough
camera and draws a box around each face. Start with the closest Pipeline Zoo package, set up what is
needed, run it, fix crashes from the logs, and show me a screenshot. Explain choices and confirmations
in beginner-friendly language.
```

```text
In this existing PICO Unity project, estimate body pose from the camera and use it to drive an avatar.
Find and import the closest Pipeline Zoo package through the Unity SDK importer, then build and verify
the app. Do not replace the SDK that is already installed.
```

If the SDK is not specified, the assistant should inspect the workspace first. In an empty directory,
it should help choose between Kotlin Spatial SDK and Unity; Native OpenXR requires an existing PICO
OpenXR project. SpatialML is an integration in one of those parent SDKs, not a standalone project type,
and it is not a WebSpatial workflow.

A new Kotlin SpatialML app is feature-bearing by definition. It follows `spatial-design-to-app` and
the executable-design gate; when the request has no user-provided executable design,
`pico-spatial-app-designer` produces and accepts one first. `spatial-app-onboarding` may create the
project only as that workflow's scaffold substep. Direct onboarding is reserved for an explicitly
featureless parent scaffold.

The SpatialML skill also activates for implicit requests that combine spatial input with model
inference and an output, even when the prompt never says "SpatialML." Passthrough display, platform
hand tracking, spatial mesh, ordinary 3D model assets, or a generic chatbot do not activate it by
themselves. See `skills/spatialml/references/natural-language-quickstart.md` for more prompt templates,
the assistant's expected workflow, SDK boundaries, and beginner terminology.

## Contents

Distributable assets live under `skills/` (each host's `plugin.json` points to this directory). Currently included:

- `skills/porting-android-app/`: Porting an Android app to PICO OS with Spatial SDK, including code refactoring, SDK integration, dependency resolution, and UI adaption.
- `skills/spatial-app-onboarding/`: Reusable onboarding skill for creating or continuing a first working Spatial SDK app from templates, especially empty-directory quickstarts, new Spatial apps, and 3D model starter demos.
- `skills/spatial-sdk-guideline/`: Day-to-day PICO Spatial SDK 3D development guide (Stage/WindowContainer, ECS, asset loading, materials/lighting, animation, physics, interaction, coordinates/units, performance budgets, etc.). For non-trivial SDK/API facts, use `pico-dev-knowledge` MCP as the primary retrieval source when available; use curated pages under `skills/spatial-sdk-guideline/reference/` for workflow guidance, stable examples, and fallback context. Includes the `skills/spatial-sdk-guideline/playbooks/scene-surface-placement.md` sub-flow for placing content onto detected real-world surfaces (walls, tables, floors).
- `skills/spatial-design-to-app/`: Multi-source app generation and bounded panel patch skill for creating or materially updating a PICO Spatial Android/Kotlin app from Figma, screenshots/mockups, PRDs, intent-only prompts, hybrid inputs, or a constrained patch while preserving or choosing the right container, window model, and panel hierarchy. The Figma route requires the external `codin-d2c-figma-to-code` MCP server; the other input routes work with the servers this plugin provisions.
- `skills/pico-spatial-app-designer/`: PICO Spatial app design package skill for designing, reviewing, repairing, or producing a structured design deliverable from requirements, prior design facts, or delivery specs, covering the intent, research, spatial-structure, composition, design-system, preview, and delivery-readiness stages before app code generation.
- `skills/spatial-app-dev-workflow/`: Post-onboarding Spatial SDK implementation workflow for continuing from a project `AGENTS.md`, implementing one requirement at a time, building, installing/launching in the PICO emulator or device, collecting screenshot/recording/log evidence, and repairing crashes from logcat before handoff.
- `skills/spatial-sdk-update/`: PICO Spatial SDK version update/migration assistant (with risk notes and constraints).
- `skills/spatial-editor/`: Managed Spatial Editor authoring package split into `SKILL.md` for workflow/task decomposition, `contracts.md` for Agent-to-Controller forms, and `recovery.md` for rejected submissions, error codes, interruptions, and blockers.
- `skills/spatial-sdk-scene-builder/`: Kotlin/Spatial SDK Entity scene implementation and repair skill for code-owned hierarchy, asset loading, transforms, bounds-aware placement, SpatialView/WindowContainer clipping, and runtime validation. Explicit offline transform plans remain supported as intermediate artifacts; editor-authored scene or asset content stays with `spatial-editor`.
- `skills/pico-env-doctor/`: Verify-first environment workflow for tasks that execute `pico-cli`, query MCP, install/update plugin hosts, or start emulator/device workflows. It checks whether `pico-cli` is installed/current, discovers supported setup/plugin/MCP commands before doctor-style checks, allows short-term session reuse of healthy results, and requires explicit authorization before running repair commands.
- `skills/pico-cli/`: Generic `pico-cli` usage guide for command-family selection, help/version/setup discovery, output formats, device targeting, safe defaults, troubleshooting, and handoff to workflow-specific skills.
- `skills/spatial-emulator-usage/`: Emulator-specific `pico-cli` supplement for real emulator/device workflows, including emulator lifecycle, APK install/launch, file transfer, screenshots, recordings, and log/logcat workflows.
- `skills/spatial-app-performance-analysis/`: On-device Spatial App performance analysis skill for diagnosing stutter, frame drops, high CPU/GPU load, scene-complexity pressure, and slow startup/loading by combining `pico-cli perf` real-time diagnosis with Perfetto Trace evidence.
- `skills/spatial-ui-ability/`: SpatialUI capability lookup skill for production-ready Kotlin snippets covering gestures, Vibrant, hover effects, window constraints, depth layout, glass materials, Z offsets, 3D transforms, and Augment-style windows.
- `skills/spatial-ui-design-style/`: SpatialUI application-side design-system guide for PicoTheme usage, token and typography role selection, built-in component preference, and custom Compose UI that matches native SpatialUI interaction conventions.
- `skills/plugin-audit/`: Local metadata-only plugin setup audit for support workflows. It creates a user-reviewed support bundle without collecting prompts, source code, tool arguments, tool outputs, or transcripts by default.
- `skills/spatialml/`: Unified cross-SDK workflow for creating, extending, or debugging SpatialML-enabled apps after completing the owning SDK workflow. Its focused references cover beginner natural-language app creation, Pipeline Zoo discovery/adaptation/SDK-owned loading, and implementation workflows such as camera-to-model inference, operator selection, 2D-to-3D placement, mode-specific output, synchronization, and readback. Exact SDK APIs come from `pico-dev-knowledge`, not project-local copies of SDK documentation.

## Manual Entry Points

The recommended path is `pico-cli setup`, described above. If you manually inspect or import this plugin, use these standard entrypoints:

- Claude Code: `.claude-plugin/plugin.json`
- Codex: `.codex-plugin/plugin.json`
- Cursor: `.cursor-plugin/plugin.json`
- GitHub (Copilot/Workflow integrations): `.github/plugin/plugin.json`
- Trae CLI: local marketplace installation driven by `pico-cli setup` / `pico-cli plugin update`
- MCP config entry: `.mcp.json`

When imported manually, the host loads `skills/` and `.mcp.json` using the relative paths in `plugin.json`. Prefer `pico-cli setup` where available so host-specific registration, marketplace refresh, and plugin install/update are handled consistently.

## MCP and Plugin Audit

The public `.mcp.json` starts the knowledge and managed Spatial Editor gateway servers through `npx`:

```bash
npx -y @picoxr/pico-cli knowledge:server
npx -y @picoxr/pico-cli editor:bootstrap
```

The editor gateway installs and starts Spatial Editor lazily when an agent calls `start_editor_workflow`. The managed Controller owns execution order, retries, evidence gates, packaging, and cleanup. Editor download channels are selected by the pico-cli build policy and are not user-configurable.

These two servers are the only ones this plugin provisions. The Figma route in `skills/spatial-design-to-app/` additionally needs the `codin-d2c-figma-to-code` MCP server (`d2c_get_figma_data`, `d2c_download_icons`, `d2c_verify_code`, `d2c_cleanup_temp`) configured in your own host. Without it, that skill re-routes a Figma request to a screenshot/mockup flow or reports BLOCKED rather than generating unverified code — see `AGENTS.md` → "External MCP prerequisites".

For setup and visibility support, use the user-triggered plugin audit flow:

```bash
pico-cli plugin audit
pico-cli plugin audit --transcript --yes
```

Without `--transcript --yes`, the command writes a local metadata-only support bundle under `.pico-spatial-agentic-tools/plugin-audit/` by default. With `--transcript --yes`, it also writes `session-transcript.jsonl`, `pico-spatial-agentic-tools-usage.json`, and `pico-spatial-agentic-tools-usage.md` in that bundle. It does not automatically upload data. Review the generated `summary.md`, transcript, usage records, and `redaction-notes.md` before sharing anything externally.

Installing `pico-cli` is still the recommended setup path because setup/update commands and MCP server configuration expect the `pico-cli` command on `PATH`. When setup, plugin visibility, skill loading, or MCP connectivity is suspect, use the `pico-env-doctor` verify-first workflow before environment-dependent CLI or MCP work. It is not required for purely local code reading or static project analysis.

## License, Security, and Privacy

- License: Apache-2.0. The marketplace root `LICENSE` applies to this plugin, its skills, examples, and bundled references unless otherwise noted.
- Security reporting: see the marketplace root `SECURITY.md`.
- Privacy and local support bundles: see the marketplace root `PRIVACY.md`.

## Suggested Prompts (Examples)

These prompts demonstrate routing only; their subjects, quantities, relationships,
distances, and visual properties are not defaults for another task.

- "Check whether my `pico-cli`, PICO Spatial plugin, skills, and MCP environment are installed, current, and ready; fix anything safe to repair."
- "Create a new PICO Spatial app from scratch using the shortest stable template path."
- "I have an empty directory and want the fastest working Spatial SDK demo."
- "Use this Figma to redesign my existing app into a PICO Spatial app while preserving the right container and window model."
- "Build a new PICO Spatial app from this PRD and choose the correct container, window model, and panel hierarchy."
- "Patch this existing panel from a screenshot without changing the root container."
- "After the onboarding demo works, add tap-to-select for the model, run it in the emulator, and fix any crash from logs before you hand it back."
- "Continue from this Spatial SDK project's AGENTS.md and implement the next requirement; verify each step with build/install/launch evidence."
- "Create a new authored scene in Spatial Editor, inspect it visually, and package it for this app."
- "Should I use `Stage` or `WindowContainer` in PICO Spatial SDK? What are the constraints of each?"
- "What's the minimal Kotlin pattern to async-load a `glb` model in `SpatialView`? Should it go in `initial` or `update`?"
- "Why doesn't raycast/click interaction work? How should I configure `CollisionComponent` vs `InteractableComponent`?"
- "My physics collisions don't happen / don't block. How do I verify physics world scope and collider modes?"
- "Upgrade this project to the newest PICO Spatial SDK and fix deprecated APIs."
- "Create this complete scene using Kotlin Entities, then build and verify it on the emulator."
- "Apply the requested measured relationship between the named Entities without changing unrelated scene content."
- "Inspect these assets and generate an explicit `.spatialsdk/scene_transforms.json` plan before implementing the Kotlin scene."
- "Attach this panel to a real wall and keep it stable as the user moves."
- "Which `pico-cli` command should I use to inspect devices, app state, or emulator state?"
- "How do I get JSON output or choose a target device with `pico-cli`?"
- "Start the PICO emulator and check whether the environment is ready."
- "Install an APK to the current emulator and launch it."
- "Capture screenshot / recording / logcat from the current device."
- "My Spatial app stutters on a real device. Help me diagnose it with `pico-cli perf` and Perfetto Trace."
- "Analyze this Perfetto Trace and tell me whether the bottleneck is in the app, SPR, Eng-Render, or XR runtime/compositor."
- "Use `pico-cli perf doctor` / `live` / `trace` to investigate frame drops, high CPU/GPU load, or slow startup on device."
- "Convert this Figma page into SpatialUI Compose code for my PICO OS project."
- "Turn this screenshot into SpatialUI code and verify the project environment is ready to build."
- "How do I add `spatialHoverEffect`, `backgroundMaterial`, `zOffset`, or `rotate3D` to this SpatialUI component?"
- "Which `PicoTheme` colors, typography roles, and built-in components should I use so this custom SpatialUI UI looks native?"
- "Add SpatialML to this existing Kotlin Spatial SDK, Unity, or Native OpenXR app and verify the setup."
- "Create a new SpatialML app using Unity, Kotlin Spatial SDK, or Native OpenXR, with the owning SDK setup first."
- "I am new to PICO. Build an app that detects household objects from the passthrough camera, label them, run it, and show me the result. Help me choose Kotlin or Unity if needed."
- "Use microphone audio with my model.tflite to classify sounds and show the current label; explain anything I need to confirm."
- "Search the Pipeline Zoo for a pose package, compare the model cards, and install the best match."
- "No exact package matches; adapt the closest topology and load it through this SDK's package loader."
- "Import this Pipeline Zoo package into my Unity project and finish it through the SDK importer."
- "Check whether the PICO Spatial plugin is visible to my agent host and create a local support bundle with plugin-audit."

## Versioning & Change Tracking

- The plugin version is shared across host manifests that expose a version field. Checked-in source currently defines it in `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `.cursor-plugin/marketplace.json`, `.github/plugin/marketplace.json`, and the plugin-level `plugin.json` files.
- During publish automation, `target_version` overrides exported host manifest versions at publish time so the synced target repo matches the release input.
- On publish sync, a `.publish-meta.json` file (if enabled) is written for source commit and publish timestamp traceability.
