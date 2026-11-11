# PICO Spatial Agentic Tools Plugin Guidance

This installed plugin provides skills and references for AI coding agents: Claude Code, Cursor, Codex, GitHub Copilot, Trae CLI, OpenCode V2, CodeBuddy Code, Qoder CLI, Antigravity CLI, and Grok CLI.

This plugin is configured into each PICO Spatial SDK project by the general plugin's `pico-project-setup` Skill (`pico-cli project configure --platform spatial`). The general plugin is installed once per user and provides `pico-project-setup`, `pico-cli`, `knowledge-query`, and the `pico-dev-knowledge` MCP; those names are available here without being part of this plugin.

## Prepared Accessibility Goals

Reject requests requiring immediate reactions to random events or moving hazards before
generating code or querying the device. Current A11Y does not support that gameplay.

For an authorized runtime-only end goal with the project, device and current baseline supplied,
load `skills/spatial-accessibility/SKILL.md` directly. Use its Runtime Goal Shortcut: read the
standard goal catalogue and runtime rules once. Identify the current and requested scenario
from its facts and public markers before dispatch. Current state unknown: one compact query.
Real-time gameplay: report unsupported and stop; never switch modes or try a goal first.
Scene facts requiring real-time reaction take precedence over unknown/static labels.
A supplied source-proven static initial state goes directly to one goal; do not query to recheck it.
Missing scene facts fail closed; invalid real-time fact types are rejected explicitly.
Cosmetic NPC movement that does not affect the requested actions is not a rejection reason.
Only a supported scenario proceeds through one `interact route --goal`.
Do not list the workspace, discover commands, read the full Contract or regenerate a plan.
Preserve supplied project and device bindings. Report CLI time as CLI time; report full Agent
time only when measured externally. Reactive gameplay stops before actions.

## Conditional Environment Pre-Flight

Run `pico-env-doctor` before environment-dependent execution tasks: running environment-dependent `pico-cli` commands beyond help/version discovery, querying `pico-dev-knowledge` MCP, installing/updating plugin host integration, or starting emulator/device workflows. It is not a universal gate for purely local code reading, architecture discussion, static code edits, or project analysis that does not depend on live local tooling.

Record the result once per host session and reuse it when the workspace, host, and tooling have not changed. Re-run the complete doctor only when environment setup or the CLI/plugin/toolchain/Host integration changed, a new failure signal appears, or the user asks to re-verify. Emulator/device/app lifecycle work such as emulator image install, create/start/stop, or APK install/launch refreshes only the affected target state and does not by itself invalidate the complete report.

## Available Skills

Installed Skill names: `threejs-to-spatial`, `porting-android-app`, `spatial-app-onboarding`, `spatial-design-to-app`, `pico-spatial-app-designer`, `spatial-sdk-guideline`, `spatial-app-dev-workflow`, `spatial-accessibility`, `spatial-sdk-update`, `spatial-editor`, `spatial-bundle-scene-reader`, `spatial-sdk-scene-builder`, `pico-env-doctor`, `pico-cli`, `pico-cli-device-target`, `pico-cli-screenshot`, `capture-camera`, `pico-emulator-usage`, `spatial-app-performance-workflow`, `spatial-ui-ability`, `spatial-ui-design-style`, `spatialml`, `spatialml-debugging`.
Use the Task Routing rules below to select and load the matching Skill instructions.

General owns `pico-env-doctor`, `pico-emulator-usage`, `pico-cli-device-target`, `pico-cli-screenshot`, and `capture-camera`. Use these directly for shared tooling and capture; do not install the Spatial plugin for a Unity or standalone device task. A missing device during a required runtime check routes to `pico-emulator-usage`: use an available compatible emulator when authorized, or report the required device capability. A screenshot does not substitute for application runtime validation.

## Task Routing

- Use `capture-camera` for target-relative camera pose and trajectory work: object or App orbits, six faces, in-place turns, and recording camera movement. When that work ends in a still PNG, `capture-camera` owns the pose plan while `pico-cli-screenshot` owns target classification, capture-mode selection, and readable-PNG validation. Current-view still requests go directly to `pico-cli-screenshot`.
- **Existing Editor handoff takes precedence over 3D authoring routes.** If an existing Spatial SDK app has a co-located `<name>.bundle` and `<name>.scenes.json` and the request is to integrate, load, or validate that authored scene in the app, enter `spatial-app-dev-workflow` as the enclosing workflow. Inspect the files before selecting any 3D subskill. Use `spatial-bundle-scene-reader` to read an existing manifest on demand; never load a whole `.scenes.json`, and do not assume component data is present in it. Do not activate `spatial-editor` to recreate or repackage existing content. Use `spatial-sdk-scene-builder` only as a subordinate step when the integration also needs Kotlin Entity hierarchy, placement, or loading code; return to the app workflow for the build and APK check. If the request changes authored content, use native Editor tools unless the prompt explicitly selects the Editor workflow under Spatial Editor Activation, then resume app integration.
- For SpatialML service logs, `debug.pico.spatialml.debug`, operator runtime failures, zero/stale
  tensor output, or explicit global tensor inspection, use `spatialml-debugging`
  (`skills/spatialml-debugging/SKILL.md`). It owns capture, SDK readback, and debug cleanup.

- Use `threejs-to-spatial` when the user asks to migrate or convert an existing native Three.js, WebGL, or WebXR project into a new Spatial SDK app. Do not use this route to patch an existing Spatial SDK app.
- Use `spatial-app-dev-workflow` as the development backbone for new and existing PICO Spatial apps, including UI, Entity/scene, and behavior changes. Read its execution-choice guidance before starting a managed dev Run; loading a skill or receiving a one-line app request does not authorize a workflow launch.
- Read specialist skills for the current stage: `spatial-app-onboarding` for a missing runnable scaffold, `pico-spatial-app-designer` for design deliverables, and `spatial-design-to-app` for UI design, implementation and verification methods. Existing design sources determine which design work is needed, not who owns the whole app request.
- Direct specialist entry is valid. Return scoped results to the caller; for complete app delivery, read `spatial-app-dev-workflow` and reuse already completed work. UI and behavior changes in one request stay in the same development loop.
- Use `porting-android-app` when a traditional 2D Android app must be redesigned into a PICO Spatial app.
- Use `spatial-app-onboarding` for an independently requested scaffold or as the scaffold/first-run subtask of the current caller. Return project facts and evidence to that caller; standalone follow-up development uses `spatial-app-dev-workflow`.
- Use `spatial-sdk-guideline` for focused SDK API guidance, implementation patterns, and runtime debugging inside a PICO Spatial SDK project. Its `Investigation Order` and `SDK Development Safety Rules` sections define the knowledge-gathering and safety constraints for all SDK work.
- Use `spatial-accessibility` for A11Y and model/panel actions through one `interact act`; named business goals use one `interact route --goal` through JEV. Also use it to author and audit published Android Accessibility semantics.
- For an existing Editor `.bundle` and `.scenes.json` handoff, keep app integration in `spatial-app-dev-workflow` and verify the built APK with `pico-cli app bundle verify <apk>` before installation.
- Use `spatial-sdk-scene-builder` for code-owned scene composition and placement. Runtime behavior changes that preserve the scene stay in the current App task. For managed Codegen work, use `start_3d_generation_workflow` with `backendPreference="codegen"`.
- Use `spatial-design-to-app` as stage-specific UI guidance. Its existing standalone UI workflow remains available when explicitly selected, and an existing Run keeps its own handoff contract. Do not automatically start it for `intent_only` or nest its application-writing/device loop inside dev design.
- Use `pico-spatial-app-designer` directly when the requested deliverable is design-only: design, review, repair, or produce a PICO Spatial app design package. It composes Preview in Plan, reviews it, then records Spec in Write Spec and checks consistency.
- Use `spatial-sdk-update` when the project is already Spatial/MR and needs SDK/toolchain/version alignment or deprecated-API migration.
- Use `spatial-editor` only when the user's prompt or an upstream app agent's delegation prompt explicitly requests a Spatial Editor workflow. Continue an already authorized Run through its current Handoff. Ordinary Editor requests use native tools and `pico-cli` for command discovery; apply the startup conditions below before creating any Run.
- Use `pico-env-doctor` as a required first step for tasks that actually execute `pico-cli`, query MCP, install/update plugin host integration, or start emulator/device workflows when the environment is suspect or unverified this session.
- Use the general plugin's `pico-cli` Skill when the task is about generic CLI usage: choosing a command family, discovering help/version/setup commands, understanding output formats, targeting devices, or first-pass troubleshooting.
- Use `pico-cli-device-target` before any workflow that must distinguish real PICO hardware from an emulator.
- Use `pico-cli-screenshot` for screenshot or spatial visual evidence requests. It consumes the target classification and owns screenshot mode selection and PNG validation.
- Use `pico-emulator-usage` when the task becomes an emulator/device workflow: preparing the machine, creating/starting a PICO emulator, checking devices, installing/launching APKs, diagnosing app startup crashes or flash exits, moving files, collecting recordings, reading logcat, or cleaning up resources. Screenshot requests are routed to `pico-cli-screenshot`. A request to install, launch, and diagnose a crashing APK routes here even when it mentions a physical device rather than an emulator.
- Use `spatial-app-performance-workflow` for Spatial app performance diagnose, including performance data capture, analysis, source code repair, and verification, including jank, frame drops, and high CPU/GPU load. The Skill composes the required stages and delegates detailed evidence analysis to specialist Skills.
- Use `spatial-ui-ability` for specific SpatialUI spatial capability snippets: gestures, Vibrant, hover, `windowConstraints`, `backgroundMaterial`, depth layout, `zOffset`, `rotate3D`, `scale3D`, or Augment-style windows.
- Use `spatial-ui-design-style` for SpatialUI application-side design consistency: PicoTheme wrapping, color/typography roles, preferring built-in components, or custom Compose UI behaving like native SpatialUI.
- Use `spatialml` for Kotlin Spatial SDK SpatialML/SecureMR/OpenMR setup and implementation, custom pipeline/package edits, Pipeline Zoo, and LiteRT/TFLite model inspection. Runtime service logs, global probes, zero/stale tensors, and readback permission failures start with `spatialml-debugging`, including requests that mention tensor mappings or execution order. Also activate when the user asks to inspect a concrete `.tflite`/LiteRT model — requesting input/output tensor names, dtypes, shapes, quantization, or metadata — even without the word "SpatialML". Do not trigger it for platform capabilities or generic AI features without model inference, or for conceptual model I/O discussion that names no concrete model file. In particular, do not activate for pure passthrough/VST display, camera configuration, or any camera/VST-feed access that does not involve model inference.
- Unity SpatialML belongs to the external **PICO Unity Agentic Tools** plugin. Hand implementation requests to that plugin's `spatialml` skill and runtime service diagnostics to its `spatialml-debugging` skill; do not apply this plugin's Kotlin workflow. A project holds one platform, so if the Unity plugin is not configured, report `BLOCKED` and continue `pico-project-setup` with the intended Unity engineering and resource roots. Read the returned continuation guidance and Skills in the current session; verify native Unity MCP tools before implementation, using only the affected MCP reconnect when required.
- Use the general plugin's `knowledge-query` Skill for cross-platform Q&A via subagent. Its `pico-dev-knowledge` MCP serves the knowledge version selected for this project.

Visible Entity design changes remain in the dev application loop. Resolve the
requested design with the appropriate design/UI guidance before implementation;
Scene Builder performs the assigned Kotlin Entity work. In managed dev execution,
start through Planner/Designer when new design is needed, or use impl-planner with
a usable existing design. An accepted scene-only deliverable may use Scene Builder
directly. Existing bundle presence does not transfer the app request to another skill.

## 3D Execution

Prefer direct execution when it can meet the request. Select the authoring capability by
the deliverable; loading a Skill does not start a Run. See
`skills/spatial-editor/references/3d-execution.md` for direct execution and continuation.

### Spatial Editor Activation

Start a new `spatial-editor` workflow production or revision Run only when:

1. An upstream agent building a PICO Spatial app explicitly requests the Editor workflow in its delegation prompt.
2. The user explicitly requests a Spatial Editor workflow in their prompt.

Installing pico-cli, mentioning Spatial Editor, or asking to change a material, add geometry,
adjust a scene, inspect content or package it does not by itself select a workflow.
Standalone Editor tasks use the advertised native Editor tools; use `pico-cli` for command
discovery and standalone lifecycle. Verify the changed targets without creating a Run.
Continue an already authorized active Run through its current Handoff. If that Run owns the
scene, keep writes in its managed gateway; do not bypass fencing or start a replacement Run.
Previous workflow provenance alone does not authorize a new revision Run.
Loading a Skill or citing its managed ownership rules cannot authorize workflow startup.
Ordinary upstream Editor delegation does not select a workflow. These conditions apply to
every new Run, including revisions suggested by recovery or delivery guidance.

After resolving the required scene design, Kotlin/Spatial SDK Entity work uses `spatial-sdk-scene-builder` under the selected enclosing app workflow, or directly for an accepted scene-only deliverable. Do not activate Spatial Editor solely for SDK/API explanation, Kotlin/Compose implementation, Gradle repair, emulator/device work, runtime debugging, or transform-only planning.

For an admitted app-construction step, Spatial Editor remains the default for authored content.
That step may skip Spatial Editor only when:

1. The user explicitly asks not to use Spatial Editor.
2. Runtime capability inspection shows Spatial Editor cannot satisfy any part of the requirement.
3. Spatial Editor is actually unavailable after reasonable recovery steps.

Do not infer exceptions 2 or 3 without runtime evidence. Once a startup condition is met, an idle, stopped, or non-recoverable backend status is not unavailable-editor evidence — call `start_editor_workflow` and follow its recovery. Every admitted production goal, including particle-only requests, starts with SceneSpec. Declare particle needs there and read `spatial-editor/particle-workflow.md` when they exist; the managed particle stage produces them after scene assembly and saving, before final review capture. Before a Handoff submission, read `spatial-editor/contracts.md`; after rejection or a user-decision result, read `spatial-editor/recovery.md`.

Once the managed Editor path is selected, keep SceneSpec, particle preparation and
Handoff submission within that Run.

## MCP Guidance

All `pico-dev-knowledge` queries, including those requested by a platform Skill or reference,
must use the general plugin's `knowledge-query` Skill. Pass the explicit engineering project as
`--project <target-dir>` and, when distinct, its resource workspace as
`--workspace-root <session-root>`. Follow that Skill's usable-baseline → live activation → query →
restore protocol, including its error and fallback rules; do not bypass it with a direct
`query_graph` call. This applies after same-session configure or `knowledge use` too. Disk selection
and doctor alignment do not prove which graph an already-connected server serves. Keep query
lifecycle ownership in `knowledge-query`; a full session restart is not the default remedy.

- **`pico-dev-knowledge`** — Knowledge graph MCP provided by the general plugin. `pico-cli project detect --format json` reports the effective disk selection, not the live server workspace. Preferred retrieval source for non-trivial Spatial SDK/API facts; broader and more frequently updated than bundled skill references.

  | Tool               | What it does                                                                                                                                                                                                            |
  | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `query_graph`      | Search the knowledge graph using natural language questions or keywords. Returns relevant nodes and context via BFS/DFS traversal. Supports `mode` (bfs/dfs), `depth` (1-6), and `token_budget` to control output size. |
  | `switch_workspace` | Hot-reload to a different version's knowledge data without restarting the server.                                                                                                                                       |

- **`pico-spatial-editor`** — The public 3D Workflow and Editor gateway. `spatial-sdk-scene-builder` uses `start_3d_generation_workflow`, `resume_3d_generation_workflow`, `get_3d_generation_workflow_status`, `wait_3d_generation_workflow`, and `cancel_3d_generation_workflow` with the Codegen backend. `spatial-editor` uses `start_editor_workflow`, typed `submit_editor_workflow`, `get_editor_workflow_status`, `wait_editor_workflow`, and `cancel_editor_workflow`, which fix the Editor backend. Callers control only the root Run; Child selection and execution remain managed.

Before every Editor workflow call, read the latest root Handoff task/revision and Schema
or the latest `waiting.handoff.taskId` from the public Run. Discard the previous
observation after each call and follow only the current Handoff.

### External MCP prerequisites (not provisioned by this plugin)

This plugin ships no `.mcp.json`; `pico-spatial-editor` and `pico-dev-knowledge` come from the general plugin's user-level configuration. Some skill routes additionally depend on an MCP server the user must configure in their own host:

| Capability                                                                                                              | Server                    | Required by                                                                                                     | If absent                                                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Figma extraction + D2C verification (`d2c_get_figma_data`, `d2c_download_icons`, `d2c_verify_code`, `d2c_cleanup_temp`) | `codin-d2c-figma-to-code` | `spatial-design-to-app` on the `visual_design` route; `spatial-ui-design-style` `d2c_verify_code` `ruleContext` | Re-route to a screenshot/mockup (`visual_reference`) or report BLOCKED — see `skills/spatial-design-to-app/SKILL.md` stage 1b. Never skip the verify hook silently. |

Check the live tool list before promising a route that needs one of these. If MCP tools are unavailable, continue with bundled references and clearly state which lookup could not be performed.

`pico-spatial-editor` is a global user-level MCP server from the general plugin; verify that the current Host has loaded and approved it. Discover its tools accepting hyphen/underscore Host normalization (`pico-spatial-editor` vs `pico_spatial_editor`, `mcp__` prefixed forms) and call them by their exact advertised names. For non-coding authoring, pass the user's explicit usable `workspace_root`; do not configure a platform just to make MCP available. For app development, keep the engineering and resource roots aligned through `pico-project-setup` and its returned continuation. If a tool returns `not-in-spatial-project`, correct the intended target or configure the Spatial project as appropriate; required backend tools and Editor readiness must still be verified. If tools are absent, inspect Host discovery and approval status. Prefer supported discovery or a server-specific reconnect; request a session reload only when this Host requires it to load the registration. Missing tools alone do not justify repeating setup or project configuration.

## Core Rules

- **Project-local authority wins.** The user's project-local `AGENTS.md`, Gradle files, manifests, source tree, and explicit requirements override generic plugin guidance.
- **Ground advice in the project's actual version.** Identify the Spatial SDK version from project-local declarations before giving API advice. Do not assume latest-version behavior applies to an older project.
- **Use public APIs only.** Do not recommend internal, hidden, unstable, or decompiled-only SDK APIs unless the user explicitly asks and the risk is stated. Do not fabricate SDK classes, methods, Gradle coordinates, or lifecycle behavior.
- **Verify before claiming success.** Do not claim an implementation works unless verified by build result, test result, emulator/device run, log evidence, screenshot, or direct code-path inspection.
- **SpatialUI is mandatory for generated apps.** Build all 2D UI with SpatialUI (`com.pico.spatial.ui.*`) wrapped in `PicoTheme`. Material/Material3 is forbidden.

## Example Routing

These examples select a skill only. Their subjects, quantities, relationships, distances, and visual properties are not defaults for the routed task.

- "Migrate this native Three.js/WebGL/WebXR project into a new PICO Spatial SDK app" -> `threejs-to-spatial`; React Three Fiber and existing Spatial app patches stay outside this route.
- "Create a new PICO Spatial app from scratch" -> `spatial-app-dev-workflow`; use `spatial-app-onboarding` for the scaffold and specialist design guidance as needed.
- "Build a spatial app from this one-line idea / PRD, with no Figma or screenshot" -> `spatial-app-dev-workflow`, with `pico-spatial-app-designer` for the required design. A one-line request does not select managed execution.
- "Use this Figma to redesign my app into a SpatialUI-based PICO Spatial app" -> `spatial-app-dev-workflow`, reading `spatial-design-to-app` for Figma extraction, implementation fidelity and verification; reuse the supplied design.
- "Scaffold an empty first-runnable planar demo, nothing else" -> `spatial-app-onboarding`.
- "After onboarding, add grab interaction and verify it in the emulator" -> `spatial-app-dev-workflow`.
- "Should I use `Stage` or `WindowContainer`?" -> `spatial-sdk-guideline`.
- "Upgrade this project to the newest PICO Spatial SDK" -> `spatial-sdk-update`.
- "Use the Spatial Editor workflow to create and package this scene" -> `spatial-editor`.
- "Use Spatial Editor to create a scene" -> native Editor tools, without starting a workflow.
- "Change this scene material / add a few primitives" -> native Editor tools; use `pico-cli` for command discovery, without starting a workflow.
- "Which entities exist in this packaged scene, or what is under `Root/Vegetation`?" -> `spatial-bundle-scene-reader`.
- "Create this complete scene using Kotlin Entities" -> `spatial-sdk-scene-builder`.
- "Create a Kotlin Entity scene app in this empty directory" -> `spatial-app-dev-workflow`, with design guidance, `spatial-app-onboarding` and `spatial-sdk-scene-builder` for their scoped stages.
- "Build this Spatial app; the upstream agent delegates asset production to the Editor workflow" -> `spatial-editor` + `spatial-sdk-scene-builder`.
- "pico-cli is broken, or the plugin/MCP will not load" -> `pico-env-doctor`.
- "Which pico-cli command should I run?" -> `pico-cli`; "start the emulator and install this APK" -> `pico-emulator-usage`.
- "Install this APK on the device, launch it, and diagnose why it immediately crashes" -> `pico-emulator-usage`.
- "Diagnose real-device frame drops with pico-cli perf and Perfetto" -> `spatial-app-performance-workflow`.
- "Run SQL against an already loaded Perfetto session" -> `spatial-app-performance-workflow`, reusing the supplied session.
- "How do I add `spatialHoverEffect`?" -> `spatial-ui-ability`; "which `PicoTheme` roles should this component use?" -> `spatial-ui-design-style`.
- "Add SpatialML to this Kotlin Spatial SDK app" -> `spatialml`, with the Kotlin SDK workflow first.
- "Add SpatialML to this Unity app" -> the PICO Unity Agentic Tools plugin's `spatialml` skill.
- "Inspect this `.tflite` model or adapt the closest Pipeline Zoo package" -> `spatialml`.
- "What are the input and output tensor names, dtypes, and shapes of my model.tflite?" -> `spatialml`.
- "How do I install or update this plugin in my Host?" -> `pico-project-setup` for this project, or `pico-cli setup` for the user-level general plugin.
