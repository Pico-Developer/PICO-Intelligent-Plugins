# PICO Spatial Agentic Tools Plugin Guidance

This installed plugin provides skills and references for AI coding agents such as Claude Code, Cursor, Codex, GitHub Copilot, and Trae CLI.

## Conditional Environment Pre-Flight

Run `pico-env-doctor` (`skills/pico-env-doctor/`) as a required pre-flight only for environment-dependent execution tasks: running `pico-cli`, querying `pico-dev-knowledge` MCP, installing/updating plugin host integration, or starting emulator/device workflows. It is not a universal gate for purely local code reading, architecture discussion, static code edits, or project analysis that does not depend on live local tooling.

Record the result once per host session and reuse it for a short time when the workspace, host, and tooling have not changed. Re-run it only when setup changed, a new failure signal appears, or the user asks to re-verify.

Read-only checks are allowed when the skill is in scope. Repair commands such as `pico-cli setup`, `pico-cli plugin update`, package installation, or other environment mutation require explicit user authorization or a task that clearly asks for setup/update/start behavior.

## Plugin Guidance Overview

The plugin provides domain-specific guidance for building and maintaining **PICO OS 6** spatial applications. Skills are not code libraries. They are host-loaded prompts plus bundled references for implementation, onboarding, migration, and diagnosis work.

Agents may read this file from a copied or linked project context. In that case, the current working directory is the user's application project, not the plugin source or marketplace root. Do not assume the consuming project contains plugin manifests, plugin source files, `.mcp.json`, or `skills/` directories unless those files actually exist there.

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

Spatial Editor is the default path for editor-authored 3D content. Users do not need to mention Spatial Editor explicitly. Activate `spatial-editor` when a request or workflow step needs editor-created scenes or assets, visual composition or tuning, materials, lighting, effects, visual inspection, custom component declaration sync, or packaged Editor content for app integration.

An explicit request for Kotlin/Spatial SDK Entity implementation is code-owned scene work and routes to `spatial-sdk-scene-builder`; it is not an unavailable-Editor fallback. Do not activate Spatial Editor solely for SDK/API explanation, Kotlin/Compose implementation, code-defined Entity creation or placement, Gradle repair, emulator/device work, runtime debugging, transform-only planning, or runtime control of existing 3D content. A generic request to create a visual 3D scene remains an Editor task when the user has not requested Kotlin/Spatial SDK ownership.

A 3D content-production step may skip Spatial Editor only when:

1. The user explicitly asks not to use Spatial Editor.
2. Current runtime capability inspection shows that Spatial Editor cannot satisfy any part of the 3D content requirement. If it can satisfy part of the requirement, use it for that part.
3. Spatial Editor is actually unavailable because installation, download, startup, connection, authorization, or backend readiness failed and reasonable recovery steps did not restore it.

Do not infer exceptions 2 or 3 without runtime evidence. Record the exception and evidence before using an App/ECS fallback. For combined editor and app tasks, use Spatial Editor for the 3D content-production step, then resume app integration, runtime behavior, UI, and validation.

An initial `get_editor_status` result with `phase=idle`, `editorRunning=false`,
or `recoverable=false` is not unavailable-editor evidence. `recoverable` only
reports whether a previous managed headless session can be resumed. For
editor-authored work, activate `spatial-editor` and call
`start_editor_workflow`; the managed Controller owns installation, startup,
readiness, recovery, and cleanup. Do not call `ensure_editor_ready` as a
preflight for that managed workflow. Before using an App/ECS fallback, follow
the workflow's structured recovery action once and record the blocker, recovery
attempted, degraded scope, and user-visible impact.

Editor scene mutation must go through live editor runtime capabilities. Do not directly author `.usd`, `.usda`, `.spatialproject`, or other editor-owned scene files. Dynamic editor backend tools must be selected from the current runtime tool list; do not rely on static backend tool names in skill text.

After activation, read `spatial-editor/SKILL.md` for workflow and task decomposition.
Before any Agent-authored Controller submission, read
`spatial-editor/contracts.md`. When the Controller rejects a submission or returns
`errors[]`, `EDITOR_*`, `blocked`, `interrupted`, or a user-decision gate, read
`spatial-editor/recovery.md` before acting. These three files have exclusive ownership:
workflow guidance must not redefine forms, contracts must not interpret errors, and
recovery must not fork normal schemas.

## Available Skills

Installed Skill names: `porting-android-app`, `spatial-app-onboarding`, `spatial-design-to-app`, `pico-spatial-app-designer`, `spatial-sdk-guideline`, `spatial-app-dev-workflow`, `spatial-sdk-update`, `spatial-editor`, `spatial-sdk-scene-builder`, `pico-env-doctor`, `pico-cli`, `spatial-emulator-usage`, `spatial-app-performance-analysis`, `spatial-ui-ability`, `spatial-ui-design-style`, `plugin-audit`, `spatialml`.
Use the Task Routing rules below to select and load the matching Skill instructions.

## Task Routing

- **Sole, top-priority routing criterion for app generation — has the user already provided an executable design?** For any request to create or generate a usable app that carries any feature, page, or business flow, decide the route by one question only: did the user supply an executable design **with the request** — a visual asset (Figma URL, screenshot, mockup) **or** an explicit design package/structured design spec (at least information architecture + page structure + state model)?
  - **No** → route to `spatial-design-to-app` first; its designer gate escalates to `pico-spatial-app-designer` to produce and accept a design package, then generates code from those accepted facts. This holds even when the target directory is empty or the app is new, and regardless of whether the prompt says "create", "implement directly", or contains no "design" keyword.
  - **Yes** → implement from the provided design (visual asset → `spatial-design-to-app` directly; design package/spec → consume it directly), without a redundant design pass.
  - Do not decide this by application complexity, keyword presence, or design depth — only by whether an executable design is already provided. `spatial-app-onboarding` is only for "just an empty scaffold / first runnable demo with no product feature described", or as a scaffold-only substep called by `spatial-design-to-app`.
- Product-specific visual/codegen requests outrank onboarding. If the prompt includes any Figma URL, screenshot, mockup, visual reference image(s), multi-page product UI, PRD, or visual-fidelity requirement, route to `spatial-design-to-app` even when the target directory is empty or the app is new. `spatial-app-onboarding` may only be called later as a scaffold-only substep after `spatial-design-to-app` has resolved the evidence, container, and window model.
- Use `porting-android-app` when a traditional 2D Android phone/tablet app must be redesigned into a PICO Spatial app.
- Use `spatial-app-onboarding` only for create/bootstrap/scaffold/quickstart requests that need just an empty scaffold or a first runnable demo with **no** described product feature, page, or business flow (empty directory, a first runnable demo, a 3D model starter, or the fastest template-based setup path). The moment a request names any application feature/page/business flow — even a one-line intent with no visual asset — it is an app-generation request that must go to `spatial-design-to-app` per the sole criterion above.

- Use `spatial-sdk-guideline` for focused SDK API guidance, implementation patterns, and runtime debugging inside a PICO Spatial SDK project. Use its scene-surface-placement flow when the task is about attaching content to detected real-world surfaces such as walls, tables, floors, or other room geometry. For SDK/API facts inside that workflow, prefer `pico-dev-knowledge` when available.
- Use `spatial-app-dev-workflow` for iterative post-onboarding feature work where the agent should inspect project-local `AGENTS.md`, implement one requirement, build, install/launch in an emulator or device, capture evidence, inspect crash logs, and repair failures before moving to the next requirement.
- For new code-owned 3D behavior, use `spatial-sdk-scene-builder` for Entity hierarchy and placement and `spatial-sdk-guideline` for broader API behavior and an ECS-first implementation plan. Especially for `sense` or tracking-driven features, require an ECS-first plan unless project evidence shows the feature is purely 2D UI or a static one-time `SpatialView` attachment.

- Use `spatial-design-to-app` when the user wants to create or substantially update a PICO Spatial app from Figma, screenshot/mockup, PRD, intent, hybrid inputs, or a bounded panel patch, and the work requires choosing or preserving container type, window model, and panel hierarchy. Do not use it for empty-dir bootstrap, SDK upgrade, legacy Android porting, pure perf diagnosis, or a standalone Kotlin Entity scene/placement task.

- Use `pico-spatial-app-designer` when the task is to design, review, repair, or produce a PICO Spatial app design package before implementation, such as turning requirements, prior design facts, or delivery specs into a structured design deliverable across the intent, research, spatial-structure, composition, design-system, preview, and delivery-readiness stages. It produces design deliverables and reviews; hand the approved design to `spatial-design-to-app` or `spatial-app-onboarding` for app code generation.

- **No-visual, no-design-package app requests are an entry-level routing rule, not just internal `spatial-design-to-app` behavior.** When `spatial-design-to-app` receives a no-visual-asset request (a one-line intent, a PRD, or a hybrid input with no Figma URL and no screenshot/mockup) that also lacks a user-provided executable design package, it must first delegate to `pico-spatial-app-designer` to produce and (via the main-thread gate) accept the design package, then consume the accepted design facts through `spatial-design-to-app`'s own design-package bridge to generate code. Per the sole criterion above, the entry router must send such requests to `spatial-design-to-app` in the first place rather than to `spatial-app-onboarding`. When visual assets exist (Figma or screenshot/mockup), this design escalation is not required and `spatial-design-to-app` proceeds directly. An executable design counts as "already provided" only when the **user** supplied it with the request — an agent's own short plan does not satisfy the gate.

- Use `spatial-sdk-update` when the project is already Spatial/MR and needs SDK/toolchain/version alignment or deprecated-API migration.
- Use `spatial-editor` when the deliverable is editor-authored scene or asset content, visual authoring/tuning, or a packaged Editor handoff. Read its `contracts.md` before submissions and `recovery.md` only after rejection, interruption, blocker, or user-decision results.
- Use `spatial-sdk-scene-builder` when the requested deliverable is Kotlin/Spatial SDK code that creates or loads, parents, transforms, arranges, or validates one or more 3D Entities, including a complete code-defined scene or focused Entity placement. For an empty directory, complete `spatial-app-onboarding` first and then resume Scene Builder. When a request needs both editor-authored content and Kotlin Entity integration, use `spatial-editor` for the authored content and `spatial-sdk-scene-builder` for the code-owned integration and placement.
- Use `pico-env-doctor` as a required first step for tasks that actually execute `pico-cli`, query MCP, install/update plugin host integration, or start emulator/device workflows when the environment is suspect or unverified this session. It checks install/version state, discovers the installed CLI command surface before using doctor-style commands, verifies plugin/MCP visibility, reuses fresh healthy session results, and reports any required host restart or remaining blocker. Run repair commands only when the user explicitly authorizes repair or the task clearly requires setup/update/start behavior.
- Use `pico-cli` when the task is about generic CLI usage: choosing a `pico-cli` command family, discovering help/version/setup commands, understanding output formats, targeting devices, safe defaults, raw `adb` fallback rules, or first-pass troubleshooting before a workflow is known.
- Use `spatial-emulator-usage` as a supplement to `pico-cli` when the task becomes an emulator/device workflow: preparing the machine for emulator work, creating or starting a PICO emulator, checking connected devices, installing or launching APKs/apps, moving files, collecting screenshots or recordings, reading logs/logcat, or cleaning up CLI-created emulator resources. This remains required after `pico-env-doctor` for direct requests such as "Start the PICO emulator", "启动 PICO 模拟器", "Install an APK to the current emulator", or "安装 APK 到当前模拟器".
- Use `spatial-app-performance-analysis` when the task is to diagnose Spatial App performance on a real PICO device, especially stutter, frame drops, unstable frame pacing, high CPU/GPU load, scene complexity pressure, slow startup/loading, or when the user provides or requests Perfetto Trace analysis through `pico-cli perf`.
- Use `spatial-ui-ability` when the task is about a specific SpatialUI spatial capability or API snippet, such as gestures, Vibrant, hover, `windowConstraints`, `backgroundMaterial`, depth layout, `zOffset`, `rotate3D`, `scale3D`, or Augment-style windows.
- Use `spatial-ui-design-style` when the task is about SpatialUI application-side design consistency, such as PicoTheme wrapping, choosing color and typography roles, preferring built-in components, or making custom Compose UI behave like native SpatialUI.
- Use `spatialml` when a request explicitly mentions SpatialML, SecureMR, OpenMR, a custom pipeline/package, a Pipeline Zoo operation, or a LiteRT/TFLite model for a PICO app. Also use it when an app feature implicitly combines spatial input (such as camera/VST, depth, microphone/audio, or another tensor source), ML inference (such as detection, classification, segmentation, pose estimation, recognition, or model-driven tracking), and an output. For Pipeline Zoo discovery, selection, adaptation, installation, import, SDK loader use, or package verification, load `skills/spatialml/references/pipeline-zoo.md`; package-only requests remain within `spatialml` and may stop after the package sub-workflow. For camera-to-model implementation, operator selection, LiteRT inference, 2D-to-3D placement, mode-specific output, tensor synchronization, or readback/debugging, load `skills/spatialml/references/implementation-workflows.md` and query `pico-dev-knowledge` for the detected SDK and mode instead of expecting SDK-doc Markdown in the project. When no exact package match exists, choose the closest structurally compatible package and preserve its validated acquisition, tensor plumbing, coordinate mapping, and rendering while replacing only necessary model-facing components. At runtime, use Unity's generated `SpatialMLPipelineZooAsset`, Kotlin's `SpatialMLSession.loadPipelinePackageFromAssets(...)`, or Native's `SecureMrUtils::LoadModelPackagePipelinesFromAssets(...)`; never recreate the package graph from JSON. Do not trigger `spatialml` for passthrough/camera access, platform tracking, spatial mesh, ordinary 3D model assets, cloud chatbots, or generic AI-assistant features without model inference.
- For a beginner SpatialML request, read `skills/spatialml/references/natural-language-quickstart.md`, infer the parent SDK from the workspace when possible, and translate the experience to `input -> inference -> output`. A new feature-bearing Kotlin app must enter `spatial-design-to-app` and its executable-design gate; `spatial-app-onboarding` is only a scaffold substep, except for an explicitly featureless parent scaffold. Then sequence SpatialML setup, closest-package reuse, and runtime evidence. Never route SpatialML to WebSpatial.
- Unity SpatialML routes depend on external **PICO Unity Agentic Tools**
  (`pico-unity-agentic-tools`). Before a handoff, inspect the live available skills for manual-only
  `pico-unity-init` on new projects or `pico-unity-package-manager` for initialized SDK repair and
  importer recovery. If the required skill is absent, report `BLOCKED` with installation and host
  restart guidance. For an undecided empty workspace, offer Kotlin without switching silently. Do not
  claim `pico-cli plugin install` can co-install platforms: cross-platform install is rejected, while
  `pico-cli setup --platform unity` can switch the complete configured environment for that scope.
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

- **`pico-spatial-editor`** — A managed Spatial Editor gateway. Normal authored-content work uses `start_editor_workflow`, `submit_editor_manifest`, `advance_editor_workflow`, `submit_editor_review`, `submit_editor_scene_plan`, `request_editor_scene_evidence`, `submit_editor_decision`, `get_editor_workflow_status`, and `cancel_editor_workflow`. Lifecycle and dynamic backend tools are Controller implementation details during a managed workflow.

### External MCP prerequisites (not provisioned by this plugin)

`.mcp.json` declares only the servers listed above. Some skill routes additionally depend on an MCP server the user must configure in their own host:

| Capability                                                                                                              | Server                    | Required by                                                                                                     | If absent                                                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Figma extraction + D2C verification (`d2c_get_figma_data`, `d2c_download_icons`, `d2c_verify_code`, `d2c_cleanup_temp`) | `codin-d2c-figma-to-code` | `spatial-design-to-app` on the `visual_design` route; `spatial-ui-design-style` `d2c_verify_code` `ruleContext` | Re-route to a screenshot/mockup (`visual_reference`) or report BLOCKED — see `skills/spatial-design-to-app/SKILL.md` stage 1b. Never skip the verify hook silently. |

Check the live tool list before promising a route that needs one of these. An unavailable external prerequisite is a routing decision to disclose, not a gate to drop.

If MCP tools are unavailable in the current host session, continue with bundled references and clearly state which lookup could not be performed.

## Example Routing

These examples select a skill only. Their subjects, quantities, relationships,
distances, and visual properties are not defaults for the routed task.

- "Create a new PICO Spatial app from scratch" -> `spatial-app-onboarding` only for an empty scaffold or first-runnable demo with no product feature; a feature-bearing request with no user-provided design routes through `spatial-design-to-app`'s `pico-spatial-app-designer` gate.
- "Build a spatial app from this one-line idea / PRD, with no Figma or screenshot" -> `pico-spatial-app-designer`, then `spatial-design-to-app`; onboarding is not the feature workflow.
- "Use this Figma to redesign my app into a SpatialUI-based PICO Spatial app" -> `spatial-design-to-app` without a redundant design pass.
- "Scaffold an empty first-runnable planar demo, nothing else" -> `spatial-app-onboarding`.
- "After onboarding, add grab interaction and verify it in the emulator" -> `spatial-app-dev-workflow`.
- "Should I use `Stage` or `WindowContainer`?" -> `spatial-sdk-guideline`.
- "Upgrade this project to the newest PICO Spatial SDK" -> `spatial-sdk-update`.
- "Create and package the authored scene described by the request" -> `spatial-editor`.
- "Create this complete scene using Kotlin Entities" -> `spatial-sdk-scene-builder`.
- "Create a Kotlin Entity scene app in this empty directory" -> `spatial-app-onboarding` + `spatial-sdk-scene-builder`.
- "Generate the assets in Editor, then place them dynamically in Kotlin" -> `spatial-editor` + `spatial-sdk-scene-builder`.
- "pico-cli is broken, or the plugin/MCP will not load" -> `pico-env-doctor`.
- "Which pico-cli command should I run?" -> `pico-cli`; "start the emulator and install this APK" -> `spatial-emulator-usage`.
- "Diagnose real-device frame drops with pico-cli perf and Perfetto" -> `spatial-app-performance-analysis`.
- "How do I add `spatialHoverEffect`?" -> `spatial-ui-ability`; "which `PicoTheme` roles should this component use?" -> `spatial-ui-design-style`.
- "Add SpatialML to this existing Kotlin, Unity, or Native OpenXR app" -> `spatialml`, with the owning SDK workflow first.
- "Inspect this `.tflite` model or adapt the closest Pipeline Zoo package" -> `spatialml`.
- "How do I install or update this plugin in my Host?" -> `pico-cli` or plugin README/setup guidance.

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

- For `spatialml`, preserve LiteRT/TFLite runtime JIT, reuse or minimally adapt a Pipeline Zoo package before greenfield authoring, use pySpatialML for authoritative package authoring and validation when custom work is required, load packages only through the owning SDK's package loader, complete the owning SDK setup before SpatialML setup, and report pySpatialML installation errors honestly instead of invoking legacy conversion scripts.
- Do not invent SDK APIs, hardcode project-specific identifiers, or assume unsupported platform capabilities.
- For `plugin-audit`, create a local support bundle, include transcript/usage files only when the user authorizes it, and remind users to review it before sharing externally.

## Delivery Checklist

- selected skill and why it was chosen
- changed files and rationale
- compatibility impact
- risk level
- verification steps and expected results
- curated references and any `pico-dev-knowledge` lookups used
