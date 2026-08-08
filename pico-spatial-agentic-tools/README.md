# PICO Spatial Agentic Tools Plugin

Plugin manifests, skills, and MCP configuration for PICO OS 6 spatial development workflows.

## What is this?

`pico-spatial-agentic-tools` is a distributable plugin payload for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Cursor](https://cursor.com), [Codex](https://developers.openai.com/codex/), [GitHub Copilot](https://docs.github.com/en/copilot), and Trae CLI. It bundles host plugin manifests, reusable skills, and MCP configuration to help developers bootstrap, build, migrate, and diagnose PICO OS 6 spatial applications.

## Intended Audience (External Developers)

This repository is for developers building **PICO OS 6** spatial apps who want reusable agent skills to:

- bootstrap a first working project from templates
- speed up day-to-day Spatial SDK development and debugging
- author and package 3D scenes through Spatial Editor
- place content onto detected real-world surfaces such as walls, tables, and floors
- upgrade or migrate older Spatial SDK projects safely
- diagnose on-device Spatial App performance bottlenecks with `pico-cli perf` and Perfetto Trace

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

`pico-cli setup` prints a plan, lets you choose supported agent hosts, and configures the hosts available on your machine. Missing optional host CLIs are skipped with guidance; install that host later and rerun setup when needed.

For non-interactive or host-specific setup, pass explicit options:

```bash
pico-cli setup --tool claude-code --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool cursor --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool codex --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool copilot --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool traecli --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool all --plugin pico-spatial-agentic-tools --yes
```

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

Update one host:

```bash
pico-cli plugin update --tool claude-code --plugin pico-spatial-agentic-tools
pico-cli plugin update --tool cursor --plugin pico-spatial-agentic-tools
pico-cli plugin update --tool codex --plugin pico-spatial-agentic-tools
pico-cli plugin update --tool copilot --plugin pico-spatial-agentic-tools
pico-cli plugin update --tool traecli --plugin pico-spatial-agentic-tools
```

Update all configured hosts:

```bash
pico-cli plugin update --tool all --plugin pico-spatial-agentic-tools
```

## Contents

Distributable assets live under `skills/` (each host's `plugin.json` points to this directory). Currently included:

- `skills/porting-android-app/`: Porting an Android app to PICO OS with Spatial SDK, including code refactoring, SDK integration, dependency resolution, and UI adaption.
- `skills/spatial-app-onboarding/`: Reusable onboarding skill for creating or continuing a first working Spatial SDK app from templates, especially empty-directory quickstarts, new Spatial apps, and 3D model starter demos.
- `skills/spatial-sdk-guideline/`: Day-to-day PICO Spatial SDK 3D development guide (Stage/WindowContainer, ECS, asset loading, materials/lighting, animation, physics, interaction, coordinates/units, performance budgets, etc.). For non-trivial SDK/API facts, use `pico-dev-knowledge` MCP as the primary retrieval source when available; use curated pages under `skills/spatial-sdk-guideline/reference/` for workflow guidance, stable examples, and fallback context. Includes the `skills/spatial-sdk-guideline/playbooks/scene-surface-placement.md` sub-flow for placing content onto detected real-world surfaces (walls, tables, floors).
- `skills/spatial-design-to-app/`: Multi-source app generation and bounded panel patch skill for creating or materially updating a PICO Spatial Android/Kotlin app from Figma, screenshots/mockups, PRDs, intent-only prompts, hybrid inputs, or a constrained patch while preserving or choosing the right container, window model, panel hierarchy, and layout regions.
- `skills/pico-spatial-app-designer/`: PICO Spatial app design package skill for designing, reviewing, repairing, or producing a structured design deliverable from requirements, prior design facts, or delivery specs, covering the intent, research, spatial-structure, composition, design-system, preview, and delivery-readiness stages before app code generation.
- `skills/spatial-app-dev-workflow/`: Post-onboarding Spatial SDK implementation workflow for continuing from a project `AGENTS.md`, implementing one requirement at a time, building, installing/launching in the PICO emulator or device, collecting screenshot/recording/log evidence, and repairing crashes from logcat before handoff.
- `skills/spatial-sdk-update/`: PICO Spatial SDK version update/migration assistant (with risk notes and constraints).
- `skills/spatial-editor/`: Managed Spatial Editor workflow for authoring scenes, entities, assets, materials, effects, visual inspection, custom component declarations, and packaged editor-to-app handoffs.
- `skills/spatial-sdk-scene-builder/`: Scene layout assistant for deriving realistic spatial transforms from 3D asset bounding boxes and generating structured scene configuration.
- `skills/pico-env-doctor/`: Verify-first environment workflow for tasks that execute `pico-cli`, query MCP, install/update plugin hosts, or start emulator/device workflows. It checks whether `pico-cli` is installed/current, discovers supported setup/plugin/MCP commands before doctor-style checks, allows short-term session reuse of healthy results, and requires explicit authorization before running repair commands.
- `skills/pico-cli/`: Generic `pico-cli` usage guide for command-family selection, help/version/setup discovery, output formats, device targeting, safe defaults, troubleshooting, and handoff to workflow-specific skills.
- `skills/spatial-emulator-usage/`: Emulator-specific `pico-cli` supplement for real emulator/device workflows, including emulator lifecycle, APK install/launch, file transfer, screenshots, recordings, and log/logcat workflows.
- `skills/spatial-app-perf-diagnose/`: On-device Spatial App performance diagnosis skill for analyzing stutter, frame drops, high CPU/GPU load, scene-complexity pressure, and slow startup/loading by combining `pico-cli perf` real-time diagnosis with Perfetto Trace evidence.
- `skills/spatial-ui-ability/`: SpatialUI capability lookup skill for production-ready Kotlin snippets covering gestures, Vibrant, hover effects, window constraints, depth layout, glass materials, Z offsets, 3D transforms, and Augment-style windows.
- `skills/spatial-ui-design-style/`: SpatialUI application-side design-system guide for PicoTheme usage, token and typography role selection, built-in component preference, and custom Compose UI that matches native SpatialUI interaction conventions.
- `skills/plugin-audit/`: Local metadata-only plugin setup audit for support workflows. It creates a user-reviewed support bundle without collecting prompts, source code, tool arguments, tool outputs, or transcripts by default.

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
npx -y @picoxr/pico-cli mcp:dev-knowledge
npx -y @picoxr/pico-cli editor:bootstrap
```

The editor gateway installs and starts Spatial Editor lazily when an agent calls `ensure_editor_ready`. Editor download channels are selected by the pico-cli build policy and are not user-configurable. The current rollout routes both public and internal builds to the regional beta channel.

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

- "Check whether my `pico-cli`, PICO Spatial plugin, skills, and MCP environment are installed, current, and ready; fix anything safe to repair."
- "Create a new PICO Spatial app from scratch using the shortest stable template path."
- "I have an empty directory and want the fastest working Spatial SDK demo."
- "Use this Figma to redesign my existing app into a PICO Spatial app while preserving the right container and window model."
- "Build a new PICO Spatial app from this PRD and choose the correct panel hierarchy and layout regions."
- "Patch this existing panel from a screenshot without changing the root container."
- "After the onboarding demo works, add tap-to-select for the model, run it in the emulator, and fix any crash from logs before you hand it back."
- "Continue from this Spatial SDK project's AGENTS.md and implement the next requirement; verify each step with build/install/launch evidence."
- "Create a new authored scene in Spatial Editor, inspect it visually, and package it for this app."
- "Should I use `Stage` or `WindowContainer` in PICO Spatial SDK? What are the constraints of each?"
- "What's the minimal Kotlin pattern to async-load a `glb` model in `SpatialView`? Should it go in `initial` or `update`?"
- "Why doesn't raycast/click interaction work? How should I configure `CollisionComponent` vs `InteractableComponent`?"
- "My physics collisions don't happen / don't block. How do I verify physics world scope and collider modes?"
- "Upgrade this project to the newest PICO Spatial SDK and fix deprecated APIs."
- "I have several 3D assets and need realistic scene positions, scales, and rotations based on their actual dimensions."
- "Attach this panel to a real wall and keep it stable as the user moves."
- "Which `pico-cli` command should I use to inspect devices, app state, or emulator state?"
- "How do I get JSON output or choose a target device with `pico-cli`?"
- "Start the PICO emulator and check whether the environment is ready."
- "Install an APK to the current emulator and launch it."
- "Capture screenshot / recording / logcat from the current device."
- "My Spatial app stutters on a real device. Help me diagnose it with `pico-cli perf` and Perfetto Trace."
- "Analyze this Perfetto Trace and tell me whether the bottleneck is in the app, SPR, Eng-Render, or XR runtime/compositor."
- "Use `pico-cli perf doctor` / `monitor` / `trace` to investigate frame drops, high CPU/GPU load, or slow startup on device."
- "Convert this Figma page into SpatialUI Compose code for my PICO OS project."
- "Turn this screenshot into SpatialUI code and verify the project environment is ready to build."
- "How do I add `spatialHoverEffect`, `backgroundMaterial`, `zOffset`, or `rotate3D` to this SpatialUI component?"
- "Which `PicoTheme` colors, typography roles, and built-in components should I use so this custom SpatialUI UI looks native?"
- "Check whether the PICO Spatial plugin is visible to my agent host and create a local support bundle with plugin-audit."

## Versioning & Change Tracking

- The plugin version is shared across host manifests that expose a version field. Checked-in source currently defines it in `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `.cursor-plugin/marketplace.json`, `.github/plugin/marketplace.json`, and the plugin-level `plugin.json` files.
- During publish automation, `target_version` overrides exported host manifest versions at publish time so the synced target repo matches the release input.
- On publish sync, a `.publish-meta.json` file (if enabled) is written for source commit and publish timestamp traceability.
