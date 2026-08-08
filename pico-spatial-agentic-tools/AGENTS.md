# PICO Spatial Agentic Tools Plugin Guidance

This installed plugin provides skills and references for AI coding agents such as Claude Code, Cursor, Codex, GitHub Copilot, and Trae CLI.

## Conditional Environment Pre-Flight

Run `pico-env-doctor` (`skills/pico-env-doctor/`) as a required pre-flight only for environment-dependent execution tasks: running `pico-cli`, querying `pico-dev-knowledge` MCP, installing/updating plugin host integration, or starting emulator/device workflows. It is not a universal gate for purely local code reading, architecture discussion, static code edits, or project analysis that does not depend on live local tooling.

Record the result once per host session and reuse it for a short time when the workspace, host, and tooling have not changed. Re-run it only when setup changed, a new failure signal appears, or the user asks to re-verify.

Read-only checks are allowed when the skill is in scope. Repair commands such as `pico-cli setup`, `pico-cli plugin update`, package installation, or other environment mutation require explicit user authorization or a task that clearly asks for setup/update/start behavior.

## Plugin Guidance Overview

The plugin provides domain-specific guidance for building and maintaining **PICO OS 6** spatial applications. Skills are not code libraries. They are host-loaded prompts plus bundled references for implementation, onboarding, migration, and diagnosis work.

Agents may read this file from a copied or linked project context. In that case, the current working directory is the user's application project, not the plugin source or marketplace root. Do not assume the consuming project contains plugin manifests, plugin source files, `.mcp.json`, or `skills/` directories unless those files actually exist there.

## Agent Roles

This plugin supports a basic three-role collaboration model. Different hosts may expose these roles differently, but agents should keep the responsibility boundaries clear.

### Planner

- Purpose: analyze the request, clarify constraints, select the right skill, and break work into executable steps.
- Hard boundary: Planner must not write, edit, or generate code.

### Generator

- Purpose: implement the planned change in code, configuration, or documentation using the selected skill and references.
- Hard boundary: Generator should not skip planning for ambiguous work or claim correctness without verification.

### Evaluator

- Purpose: assess the Generator's output for correctness, compatibility, regressions, and missing validation.
- Hard boundary: Evaluator is responsible for assessment, not primary implementation.

## Skill Activation Model

- Treat each installed plugin skill as self-contained workflow and routing guidance.
- Run `pico-env-doctor` before environment-dependent `pico-cli`, MCP, plugin setup/update, or emulator/device workflows when the environment is suspect or has not been checked in this host session. Reuse a fresh healthy result instead of rerunning it by reflex.
- `pico-env-doctor` is only the pre-flight gate. It does not replace the task-specific workflow skill. After it passes, requests to start/stop a PICO emulator, install/launch an APK or app, inspect devices, move files, capture screenshots/recordings, collect logcat, or clean up emulator resources must continue with `spatial-emulator-usage`.
- Prefer the most specific skill for the current job instead of mixing multiple skills by default.
- Read the selected skill's `SKILL.md` through the host/plugin mechanism when a skill-specific workflow is needed, then load bundled references only when needed.
- For non-trivial Spatial SDK/API facts, prefer `pico-dev-knowledge` MCP when available; use skill references for workflow guidance, stable curated baselines, and fallback context. Do not force MCP lookup for issues already proven by project-local code, build output, or tests.
- `spatial-app-onboarding` is reusable across projects. It should inspect the current project state and scaffold only when the workspace is empty or not yet a Spatial SDK project.
- **SpatialUI is mandatory for generated apps.** Any spatial app produced or continued through `spatial-app-onboarding` (and any follow-up feature work) must build all 2D UI with SpatialUI (`com.pico.spatial.ui.*`) wrapped in `PicoTheme`. Material/Material3 (`androidx.compose.material`, `material3`, `MaterialTheme`) is forbidden. Route UI design decisions through `spatial-ui-design-style` and capability snippets through `spatial-ui-ability`.

## Knowledge Source Selection

Use the fastest reliable source for the question type instead of treating any source as universally authoritative.

- Use project-local files first for project structure, dependency versions, build errors, package names, and existing implementation strategy.
- Use the selected skill first for workflow routing, task-specific procedure, response shape, and stable playbooks.
- Use `pico-dev-knowledge` MCP as the preferred retrieval source for non-trivial Spatial SDK/API facts, version-sensitive behavior, broader documentation lookup, and cross-reference discovery.
- Use bundled references and examples for stable baselines, known-good patterns, and offline fallback.
- Use SDK classes, `source.jar`, decompiled code, or binaries only for last-resort validation, exact symbol checks, or resolving conflicts between higher-level sources.

Do not force a knowledge-graph lookup for purely project-local fixes whose cause and remedy are already proven by local code, build output, or tests.

## Investigation Order (Hard Rule)

Before proposing a new implementation strategy for Spatial SDK behavior, gather knowledge in this order:

1. Inspect the user's project-local instructions, build files, manifests, and dependency declarations enough to identify the current project context, SDK version, current implementation, and failure signal when possible.
2. Select and read the most relevant skill instructions for workflow/routing guidance, especially `spatial-sdk-guideline` for day-to-day Spatial SDK development flow and scene-surface-placement guidance.
3. Query the `pico-dev-knowledge` MCP knowledge graph when the task depends on non-trivial SDK/API facts, version-sensitive behavior, broader documentation lookup, or cross-reference discovery.
4. Read related bundled references and examples, plus project-local examples that demonstrate the same pattern, preferring examples that match the project's SDK version.
5. Verify the current implementation behavior in the user's project through code inspection, builds, logs, runtime evidence, or focused experiments as appropriate.
6. Inspect SDK classes, `source.jar`, decompiled code, or binaries only as last-resort source validation, exact-symbol checks, or conflict resolution.

`pico-dev-knowledge` is the preferred retrieval source for non-trivial Spatial SDK/API facts because it can be updated more frequently and covers broader documentation, examples, and best practices than bundled skill references. `spatial-sdk-guideline` remains important for skill workflow, curated stable baselines, and specialized playbooks. Neither should override verified project-local evidence.

If `pico-dev-knowledge` is unavailable, continue with selected skill guidance, bundled references, project evidence, and last-resort source validation as needed, and explicitly state that the MCP lookup could not be performed.

Do not start by reading `source.jar` or SDK binaries when knowledge graph context, higher-level documentation, examples, and project evidence are available.

Do not replace an existing implementation strategy until the current strategy has been proven incorrect by documentation, examples, knowledge-graph evidence, current behavior, or last-resort SDK source validation.

## Routed Project Hard Rules

These rules are especially important when this plugin guidance is copied, linked, or referenced from a user's project-local `AGENTS.md` routing file during setup.

- **Project-local authority wins.** The user's project-local `AGENTS.md`, Gradle files, manifests, package names, source tree, build scripts, and explicit requirements override generic plugin guidance. Do not assume plugin repository layout, marketplace manifests, `.mcp.json`, bundled skill directories, or plugin source files exist in the user's project unless verified.
- **Ground advice in the project's actual version.** Before giving Spatial SDK API advice or modifying code, identify the Spatial SDK version from project-local dependency declarations, lockfiles, generated metadata, or build output when possible. Do not assume latest-version behavior applies to an older project.
- **Use public APIs first.** Prefer documented public APIs, `pico-dev-knowledge` evidence, bundled references, and examples. Do not recommend internal, hidden, unstable, generated, reflection-only, or decompiled-only SDK APIs unless the user explicitly asks for low-level investigation and the risk is clearly stated. Use `source.jar` to understand behavior, not to invent unsupported integration points.
- **Do not invent APIs.** Do not fabricate Spatial SDK classes, methods, Gradle coordinates, manifest entries, permissions, CLI flags, wrapper APIs, or lifecycle behavior. If a claim cannot be grounded in `pico-dev-knowledge`, docs, examples, project evidence, or last-resort source validation, mark it as unconfirmed.
- **Disclose retrieval limits.** Do not claim to have used `pico-dev-knowledge`, `spatial-sdk-guideline`, bundled references, or examples unless they were actually loaded or queried for the task. If MCP or bundled references are unavailable, continue with the next best source and explicitly state what could not be checked.
- **Reread routing after context compaction.** After conversation summarization, context compaction, or resuming a long-running task, reread the user's project-local `AGENTS.md` and the linked plugin context/routing files before continuing Spatial SDK work.
- **Prefer minimal, reversible changes.** Preserve the user's existing architecture and strategy unless it has been proven incorrect or insufficient. Do not introduce new abstractions, wrappers, dependencies, or large rewrites just because they look cleaner or newer.
- **Verify before claiming success.** Do not claim an implementation works unless it has been verified by an appropriate signal: build result, test result, emulator/device run, log evidence, screenshot, recording, or direct code-path inspection. If verification was not run, state what remains unverified and give the exact recommended verification step.

## Spatial Development Safety Rules

- **Container choice is architectural.** Do not switch between `Stage`, `WindowContainer`, subwindows, or plain 3D ECS content just to make code compile. Preserve the user's chosen container model unless project requirements or verified platform constraints prove it wrong.
- **Prefer ECS for 3D runtime behavior.** For non-trivial 3D content, scene state, animation, interaction, physics, anchors, or entity transforms, design around Spatial ECS entities/components/systems rather than using Compose or `SpatialView` recomposition as the primary 3D driver. Use `SpatialView(initial = { ... })` for one-time setup and attachment, then keep per-frame or sensor-driven 3D changes inside ECS systems, SDK tracking callbacks, or explicit entity/component updates.
- **Keep sensing and tracking paths low-latency.** When using `sense`, plane/world/mesh tracking, controller tracking, hand/body/HMD pose data, or other high-frequency spatial input, avoid routing the data through 2D UI state and then back into 3D from `SpatialView.update`. That 2D-to-3D feedback path adds avoidable latency and jitter. Prefer direct ECS-side updates, coalesced component writes, or SDK callback-to-entity pipelines with minimal main-thread work.
- **Lifecycle cleanup is mandatory.** Any code that starts tracking, registers listeners, opens containers, creates ECS entities, loads resources, or launches coroutines must also define the matching cleanup path for disposal, app pause/stop, or container close.
- **Surface and anchor work needs runtime evidence.** For plane, wall, table, anchor, room-geometry, or placement features, do not claim correctness from code alone. Verify with emulator/device capability checks, logs, screenshots/recordings, or clearly state that physical-device validation remains pending.
- **Interaction requires both input and collision evidence.** For tap, raycast, grab, drag, rotate, scale, or controller interaction bugs, check input source/controller state, target transforms, collision/hit-test components, entity visibility, and coordinate space before replacing the interaction model.
- **Performance fixes require measurements.** For stutter, frame drops, startup latency, high CPU/GPU load, or scene complexity, prefer `pico-cli perf`, Perfetto Trace, log evidence, or reproducible measurements. Do not guess root causes from code structure alone.
- **Asset changes need scale and budget checks.** When adding models, textures, lighting, particles, physics, or animations, consider units, bounding boxes, triangle/texture budgets, loading strategy, and device performance impact. Prefer measured transforms over eyeballed positions.
- **SpatialUI should stay app-side and public.** Use public SpatialUI APIs, PicoTheme roles, built-in components, and documented modifiers. Do not depend on restricted design-system internals or replicate native shell behavior manually unless the user explicitly needs a custom component and accepts the trade-off.

## Spatial Editor Activation

Spatial Editor is the default path for generating, creating, composing, or materially modifying 3D content. Users do not need to mention Spatial Editor explicitly. Activate `spatial-editor` when a request or workflow step needs new or changed 3D scenes, entities, models, hierarchy, asset composition, materials, lighting, effects, visual inspection, custom component declaration sync, or packaged content for app integration.

Do not activate it solely for SDK/API explanation, Kotlin/Compose implementation, Gradle repair, emulator/device work, runtime debugging, transform-only planning, or runtime control of existing 3D content.

A 3D content-production step may skip Spatial Editor only when:

1. The user explicitly asks not to use Spatial Editor.
2. Current runtime capability inspection shows that Spatial Editor cannot satisfy any part of the 3D content requirement. If it can satisfy part of the requirement, use it for that part.
3. Spatial Editor is actually unavailable because installation, download, startup, connection, authorization, or backend readiness failed and reasonable recovery steps did not restore it.

Do not infer exceptions 2 or 3 without runtime evidence. Record the exception and evidence before using an App/ECS fallback. For combined editor and app tasks, use Spatial Editor for the 3D content-production step, then resume app integration, runtime behavior, UI, and validation.

Editor scene mutation must go through live editor runtime capabilities. Do not directly author `.usd`, `.usda`, `.spatialproject`, or other editor-owned scene files. Dynamic editor backend tools must be selected from the current runtime tool list; do not rely on static backend tool names in skill text.

## Available Skills

| Skill                       | When to use                                                                                                                                                                                                                                                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `porting-android-app`       | Porting an Android app to PICO OS with Spatial SDK, including code refactoring, SDK integration, dependency resolution and UI adaption.                                                                                                                                                                            |
| `spatial-app-onboarding`    | Create, bootstrap, scaffold, or quickstart a first working PICO Spatial SDK Android/Kotlin project from templates; use for empty directories, new Spatial apps, first runnable demos, 3D model starter apps, and template-based setup.                                                                             |
| `spatial-design-to-app`     | Create or materially update a PICO Spatial Android/Kotlin app from Figma, screenshot/mockup, PRD, intent, hybrid sources, or a bounded panel patch when the task must choose or preserve container, window model, panel hierarchy, and layout regions.                                                             |
| `pico-spatial-app-designer` | Designing, reviewing, repairing, or producing a PICO Spatial app design package from requirements, prior design facts, or delivery specs, across intent, research, spatial structure, composition, design system, preview, and delivery-readiness review.                                                          |
| `spatial-sdk-guideline`     | Day-to-day PICO Spatial SDK development guidance, including `Stage` vs `WindowContainer`, ECS, resources, interaction, coordinates, units, and performance budgets. Includes a scene-surface-placement playbook for detected real-world surfaces.                                                                  |
| `spatial-app-dev-workflow`  | Iterative post-onboarding Spatial SDK feature workflow: implement one requirement, build, install/launch in emulator/device, capture evidence, inspect logs/crashes, and self-repair.                                                                                                                              |
| `spatial-sdk-update`        | Upgrading Spatial SDK versions, fixing deprecated or missing APIs, resolving AGP/Gradle/Kotlin/NDK compatibility problems, and migrating older projects.                                                                                                                                                           |
| `spatial-editor`            | Authoring scenes, entities, asset composition, materials, effects, visual inspection, custom component declarations, and packaged editor-to-app handoffs.                                                                                                                                                          |
| `spatial-sdk-scene-builder` | Planning realistic scene layout for 3D assets by measuring bounding boxes, deriving spatial transforms, and generating structured scene configuration.                                                                                                                                                             |
| `pico-env-doctor`           | Conditional verify-first environment workflow for tasks that execute `pico-cli`, use MCP, set up/update plugin hosts, or start emulator/device workflows: check install/version state, discover supported commands before doctor-style checks, reuse fresh session results, and explain host restart requirements. |
| `pico-cli`                  | Generic `pico-cli` usage guidance: command-family selection, help/version/setup discovery, output formats, device targeting, safe defaults, troubleshooting, and handoff to workflow-specific skills.                                                                                                              |
| `spatial-emulator-usage`    | Emulator-specific `pico-cli` supplement for multi-step emulator/device workflows, including environment checks, AVD lifecycle, APK install/launch, file transfer, screenshots, recordings, logcat, and safe cleanup.                                                                                               |
| `spatial-app-perf-diagnose` | Diagnosing Spatial App performance bottlenecks on real PICO devices using `pico-cli perf`, real-time diagnosis reports, and Perfetto Trace evidence across app, SPR, Eng-Render, and XR/compositor pipelines.                                                                                                      |
| `spatial-ui-ability`        | Looking up production-ready SpatialUI code snippets for gestures, Vibrant, hover effects, window constraints, depth layout, glass materials, Z offsets, 3D transforms, and Augment-style subwindows.                                                                                                               |
| `spatial-ui-design-style`   | Keeping SpatialUI Compose pages and custom components aligned with PICO design-system rules, including PicoTheme usage, token selection, built-in component preference, and native-feeling hover/haptics/audio.                                                                                                    |
| `plugin-audit`              | Creating a local support bundle for plugin setup or host visibility issues; include transcripts only when the user explicitly authorizes it.                                                                                                                                                                       |

## Task Routing

- Use `porting-android-app` when a traditional 2D Android phone/tablet app must be redesigned into a PICO Spatial app.
- Use `spatial-app-onboarding` for create/bootstrap/scaffold/quickstart requests involving an empty directory, a new PICO Spatial SDK app, a first runnable demo, a 3D model starter app, or the fastest template-based setup path.

- Use `spatial-sdk-guideline` for focused SDK API guidance, implementation patterns, and runtime debugging inside a PICO Spatial SDK project. Use its scene-surface-placement flow when the task is about attaching content to detected real-world surfaces such as walls, tables, floors, or other room geometry. For SDK/API facts inside that workflow, prefer `pico-dev-knowledge` when available.
- Use `spatial-app-dev-workflow` for iterative post-onboarding feature work where the agent should inspect project-local `AGENTS.md`, implement one requirement, build, install/launch in an emulator or device, capture evidence, inspect crash logs, and repair failures before moving to the next requirement.
- For new 3D behavior, favor `spatial-sdk-guideline` and an ECS-first implementation plan. Especially for `sense` or tracking-driven features, require an ECS-first plan unless project evidence shows the feature is purely 2D UI or a static one-time `SpatialView` attachment.

- Use `spatial-design-to-app` when the user wants to create or substantially update a PICO Spatial app from Figma, screenshot/mockup, PRD, intent, hybrid inputs, or a bounded panel patch, and the work requires choosing or preserving container type, window model, panel hierarchy, and layout regions. Do not use it for empty-dir bootstrap, SDK upgrade, legacy Android porting, pure perf diagnosis, or standalone 3D placement planning.

- Use `pico-spatial-app-designer` when the task is to design, review, repair, or produce a PICO Spatial app design package before implementation, such as turning requirements, prior design facts, or delivery specs into a structured design deliverable across the intent, research, spatial-structure, composition, design-system, preview, and delivery-readiness stages. It produces design deliverables and reviews; hand the approved design to `spatial-design-to-app` or `spatial-app-onboarding` for app code generation.

- When `spatial-design-to-app` receives a no-visual-asset request (a one-line intent, a PRD, or a hybrid input with no Figma URL and no screenshot/mockup), it should first delegate to `pico-spatial-app-designer` to produce and (via the main-thread gate) accept the design package, then consume the accepted design facts through `spatial-design-to-app`'s own design-package bridge to generate code. When visual assets exist (Figma or screenshot/mockup), this design escalation is not required and `spatial-design-to-app` proceeds directly.

- Use `spatial-sdk-update` when the project is already Spatial/MR and needs SDK/toolchain/version alignment or deprecated-API migration.
- Use `spatial-editor` by default when the task generates, creates, composes, or materially modifies 3D content. Apply the three documented exceptions only with the required user direction or runtime evidence, and retain Editor ownership for any portion it can satisfy.
- Use `spatial-sdk-scene-builder` when the task is about measuring 3D assets, converting dimensions into realistic scale, or generating structured transforms, and the output is planning/configuration only. If the task also needs authored content, finish planning first and then activate `spatial-editor`.
- Use `pico-env-doctor` as a required first step for tasks that actually execute `pico-cli`, query MCP, install/update plugin host integration, or start emulator/device workflows when the environment is suspect or unverified this session. It checks install/version state, discovers the installed CLI command surface before using doctor-style commands, verifies plugin/MCP visibility, reuses fresh healthy session results, and reports any required host restart or remaining blocker. Run repair commands only when the user explicitly authorizes repair or the task clearly requires setup/update/start behavior.
- Use `pico-cli` when the task is about generic CLI usage: choosing a `pico-cli` command family, discovering help/version/setup commands, understanding output formats, targeting devices, safe defaults, raw `adb` fallback rules, or first-pass troubleshooting before a workflow is known.
- Use `spatial-emulator-usage` as a supplement to `pico-cli` when the task becomes an emulator/device workflow: preparing the machine for emulator work, creating or starting a PICO emulator, checking connected devices, installing or launching APKs/apps, moving files, collecting screenshots or recordings, reading logs/logcat, or cleaning up CLI-created emulator resources. This remains required after `pico-env-doctor` for direct requests such as "Start the PICO emulator", "启动 PICO 模拟器", "Install an APK to the current emulator", or "安装 APK 到当前模拟器".
- Use `spatial-app-perf-diagnose` when the task is to diagnose Spatial App performance on a real PICO device, especially stutter, frame drops, unstable frame pacing, high CPU/GPU load, scene complexity pressure, slow startup/loading, or when the user provides or requests Perfetto Trace analysis through `pico-cli perf`.
- Use `spatial-ui-ability` when the task is about a specific SpatialUI spatial capability or API snippet, such as gestures, Vibrant, hover, `windowConstraints`, `backgroundMaterial`, depth layout, `zOffset`, `rotate3D`, `scale3D`, or Augment-style windows.
- Use `spatial-ui-design-style` when the task is about SpatialUI application-side design consistency, such as PicoTheme wrapping, choosing color and typography roles, preferring built-in components, or making custom Compose UI behave like native SpatialUI.
- After onboarding has completed, future feature work should continue with the user's project-local `AGENTS.md` and the most relevant follow-up skill.
- For `spatial-sdk-guideline`, use the skill for workflow routing and stable playbooks; use `pico-dev-knowledge` MCP for non-trivial SDK/API facts, broader documentation retrieval, and version-specific lookup; use curated bundled reference pages for stable examples and fallback context; when deeper source validation is needed, follow the file paths returned in `pico-dev-knowledge` results.
- Do not invent SDK wrapper APIs or re-implement SDK internals when bundled references or `pico-dev-knowledge` already cover the topic.

## MCP Guidance

The plugin may declare MCP servers that the host loads when the plugin is installed. Currently relevant:

- **`pico-dev-knowledge`** — A knowledge graph MCP server for PICO Spatial App development. It indexes documentation, API references, examples, and best practices into a searchable graph structure. Use this server as the preferred retrieval source for non-trivial Spatial SDK/API knowledge questions when available, because it is broader and can be updated more frequently than bundled skill references. Use it to query development knowledge, find related concepts, and get contextual answers about PICO Spatial development.

  **Key tools:**

  | Tool               | What it does                                                                                                                                                                                                            |
  | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `query_graph`      | Search the knowledge graph using natural language questions or keywords. Returns relevant nodes and context via BFS/DFS traversal. Supports `mode` (bfs/dfs), `depth` (1-6), and `token_budget` to control output size. |
  | `switch_workspace` | Hot-reload to a different version's knowledge data, such as switching SDK knowledge versions, without restarting the server.                                                                                            |

- **`pico-spatial-editor`** — A managed Spatial Editor gateway. The host connects through `@picoxr/pico-cli editor:bootstrap`; editor installation and launch happen lazily when authored-content work begins. Stable lifecycle and handoff tools include `ensure_editor_ready`, `get_editor_status`, `show_editor_window`, `stop_editor`, and `pack_editor_bundle`. Select all editor backend capabilities from the live runtime tool list.

If MCP tools are unavailable in the current host session, continue with bundled references and clearly state which lookup could not be performed.

## Example Routing

- "Create a new PICO Spatial app from scratch" -> `spatial-app-onboarding`
- "Initialize an empty directory as a PICO Spatial SDK demo" -> `spatial-app-onboarding`
- "Scaffold a quick Spatial SDK starter app for my 3D model" -> `spatial-app-onboarding`
- "Use this Figma to redesign my app into a SpatialUI-based PICO Spatial app" -> `spatial-design-to-app`
- "Build a new PICO Spatial app from this PRD and preserve the right container/window model" -> `spatial-design-to-app` for the design/container contract, then `spatial-app-onboarding` for empty-directory scaffolding, then resume `spatial-design-to-app`
- "Patch this existing panel using this screenshot without changing the root container" -> `spatial-design-to-app`
- "Design a PICO Spatial app from these product requirements and give me a full design package" -> `pico-spatial-app-designer`
- "Build a spatial app from this one-line idea / PRD (no Figma or screenshot)" -> `pico-spatial-app-designer` to produce and accept the design package, then `spatial-design-to-app` consumes it via its design-package bridge to generate code
- "Review and repair this spatial app design deliverable before we start building it" -> `pico-spatial-app-designer`
- "After the onboarding demo works, add grab interaction and verify it in the emulator" -> `spatial-app-dev-workflow`
- "Continue this Spatial SDK project from AGENTS.md; implement each requested feature and fix crashes from logcat yourself" -> `spatial-app-dev-workflow`
- "Should I use `Stage` or `WindowContainer`?" -> `spatial-sdk-guideline`
- "Attach this panel to a real wall" -> `spatial-sdk-guideline` with the scene-surface-placement flow
- "Upgrade this project to the newest PICO Spatial SDK" -> `spatial-sdk-update`
- "Fix deprecated spatial APIs and old container manager code" -> `spatial-sdk-update`
- "Create a new authored bedroom scene and package it for this app" -> `spatial-editor`
- "Add materials and lighting to the current editor scene, then show me the result" -> `spatial-editor`
- "I need to place several models into a realistic room-scale scene" -> `spatial-sdk-scene-builder`
- "Measure these bedroom furniture models and generate `.spatialsdk/scene_transforms.json`" -> `spatial-sdk-scene-builder`
- "Measure these assets, then author the final composed scene" -> `spatial-sdk-scene-builder` + `spatial-editor`
- "pico-cli isn't working / the plugin or MCP won't load / check and fix my environment" -> `pico-env-doctor`
- "Is my pico-cli up to date? Update it and make sure the dev knowledge MCP is connected" -> `pico-env-doctor`
- "How do I use pico-cli / which pico-cli command should I run?" -> `pico-cli`
- "What does `pico-cli device` vs `app` vs `emulator` do?" -> `pico-cli`
- "Start the PICO emulator" -> `spatial-emulator-usage`
- "启动 PICO 模拟器" -> `spatial-emulator-usage`
- "Install an APK to the current emulator" -> `spatial-emulator-usage`
- "启动 PICO 模拟器并安装 /path/to/app-debug.apk 这个 APK" -> `spatial-emulator-usage`
- "Capture screenshot / recording / logcat from the device" -> `spatial-emulator-usage`
- "My Spatial app drops frames on a real device. Please diagnose it with pico-cli perf and Perfetto Trace." -> `spatial-app-perf-diagnose`
- "Analyze this Perfetto Trace and tell me whether the bottleneck is in the app, SPR, Eng-Render, or XR runtime/compositor." -> `spatial-app-perf-diagnose`
- "How do I add `spatialHoverEffect`, `backgroundMaterial`, or `rotate3D` to this card?" -> `spatial-ui-ability`
- "Which `PicoTheme` color and typography roles should this custom SpatialUI component use?" -> `spatial-ui-design-style`

- "How do I install or update this plugin in Claude Code, Cursor, Codex, GitHub Copilot, or Trae CLI?" -> `pico-cli` or plugin README/setup guidance

## Diagnostics & Support Bundles

For setup or host visibility issues, use the user-triggered plugin audit workflow:

```bash
pico-cli plugin audit
pico-cli plugin audit --transcript --yes
```

Without `--transcript --yes`, the command creates a local metadata-only support bundle under `.pico-spatial-agentic-tools/plugin-audit/` by default. With `--transcript --yes`, it also exports `session-transcript.jsonl` and extracted `pico-spatial-agentic-tools-usage.json` / `pico-spatial-agentic-tools-usage.md` files. It does not upload data automatically. Ask users to review `summary.md`, transcript exports, usage records, and `redaction-notes.md` before sharing the bundle externally.

The `plugin-audit` skill guides agents through this same workflow. Do not ask users to paste full session transcripts into chat; export local files and ask the user to review them first.

## Working Principles

- Use the most relevant skill first, then read only the references needed for the task.
- Treat the user's current project as the source of truth for project structure, build commands, package versions, local constraints, and writable files.
- Do not treat this copied/linked guidance as evidence that the current project is the plugin source or marketplace root.
- For `spatial-sdk-guideline`, start with the selected skill for workflow/playbook guidance; use `pico-dev-knowledge` MCP for non-trivial SDK/API fact-finding, broader retrieval, and version-specific lookup; use curated bundled reference pages for stable grounding and fallback context; when you need deeper source validation, use the file paths returned in `pico-dev-knowledge` results.
- For `spatial-app-onboarding`, inspect the current project state before scaffolding; continue from an existing Spatial SDK project instead of restarting unless the user asks for a fresh project.
- For `spatial-editor`, establish managed backend readiness before scene mutation and use the live runtime schema for backend capabilities.

- Keep answers specific to PICO OS 6 spatial development and grounded in bundled materials, project evidence, or `pico-dev-knowledge` results.
- For 3D behavior, default to ECS-side scene ownership. Use Compose/SpatialUI for panels and controls, not as the high-frequency control loop for entity transforms, tracking data, or sensed environment updates.

- For any generated or continued spatial app, build all 2D UI with SpatialUI wrapped in `PicoTheme` and keep the project free of Material/Material3; verify this before declaring onboarding or feature work complete.

- Do not invent SDK APIs, hardcode project-specific identifiers, or assume unsupported platform capabilities.
- For `plugin-audit`, create a local support bundle, include transcript/usage files only when the user authorizes it, and remind users to review it before sharing externally.

## Response Pattern

- SDK questions: provide a recommended approach, a minimal implementation pattern, a short validation checklist, and the most relevant `pico-dev-knowledge` findings when MCP is available and the question depends on non-trivial SDK/API facts; supplement with curated references when they add workflow guidance or stable examples.
- Post-onboarding feature work: continue from the user's project-local `AGENTS.md`, implement one requirement at a time, run Gradle checks, install/launch on emulator or device, collect screenshot/recording/log evidence, and repair actionable crashes before reporting success.
- Onboarding work: choose the shortest stable template path, scaffold with minimal changes, build/install/launch when possible, write a project-specific `AGENTS.md`, and suggest the next steps.
- Upgrade work: inspect the current SDK version source, fix toolchain mismatches first, rebuild, replace deprecated or moved APIs, rebuild again, and explain runtime or store-compliance impact.
- Editor work: establish or reuse the managed editor session, author and verify content through runtime capabilities, and package a handoff when app integration is required.
- Perf diagnosis work: verify device and profiling prerequisites first, prefer real `pico-cli perf` evidence over speculation, keep window-level findings and root-cause summaries reviewable, and clearly distinguish confirmed roots from waiting victims or hypotheses.
- If `pico-dev-knowledge`, bundled docs, project evidence, and fallback source validation do not support a claim, say so directly instead of inventing behavior.

## Delivery Checklist

- selected skill and why it was chosen
- changed files and rationale
- compatibility impact
- risk level
- verification steps and expected results
- curated references and any `pico-dev-knowledge` lookups used
