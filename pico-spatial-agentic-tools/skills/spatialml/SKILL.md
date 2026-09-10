---
name: spatialml
description: Create, extend, author, validate, or debug SpatialML-enabled Unity, Kotlin Spatial SDK, and Native OpenXR apps. Use for SpatialML, SecureMR, OpenMR, custom pipeline/package, Pipeline Zoo, operator selection, LiteRT/TFLite inference, VST/camera-to-model graphs, 2D-to-3D placement, mode-specific output, tensor synchronization, or readback/debugging in a PICO app. Also use when spatial input implicitly feeds ML detection, classification, segmentation, pose estimation, recognition, or model-driven tracking. Covers parent-SDK sequencing, setup/doctor diagnosis, pySpatialML installation and delegation, SDK knowledge retrieval, implementation workflows, loader/importer boundaries, validation, authoring, and pipeline versus whole-app debugging.
license: 'Apache-2.0'
---

# SpatialML App Workflow

Add SpatialML to an existing SDK-owned app, then validate the integration. SpatialML is not a
separate project type, and this skill must not replace Unity, Kotlin Spatial SDK, or Native OpenXR
project setup.

## Recognize SpatialML Intent

Activate this workflow for either explicit SpatialML artifacts or an implicit spatial-inference
feature. An implicit feature normally combines: a PICO/spatial app, sensor or tensor input, an ML
operation, and an app-visible or pipeline-visible result. Examples include detecting objects in VST
camera frames, segmenting the room image, estimating pose from camera input, classifying audio from
the microphone, or running a custom `.tflite` model on device.

Do not activate SpatialML for an adjacent capability by itself:

- passthrough/VST display, camera access, spatial mesh, platform hand tracking, or microphone capture
  without model inference;
- ordinary 3D model assets such as `.glb`, `.fbx`, or USD content;
- a cloud LLM, chatbot, or generic "AI assistant" feature that does not use SpatialML pipelines;
- normal Spatial SDK/Unity project creation, scene work, UI, emulator use, or performance diagnosis.

When the request is ambiguous, identify the intended input, inference task, and output. If it only
uses a platform-provided tracking result, stay with the owning SDK workflow. If it runs a model or
constructs a SpatialML pipeline over that data, use this skill.

## Guide Beginners From Natural Language

When the user is new, let them describe the experience instead of requiring command names or
SpatialML terminology. Read `references/natural-language-quickstart.md` and translate the request into
the owning-SDK, SpatialML, Pipeline Zoo, application, and verification steps.

- Inspect the current project to infer Unity, Kotlin Spatial SDK, or Native OpenXR before asking.
- If the workspace is empty and the SDK is unspecified, ask one concise SDK-choice question because
  the answer changes project creation. Offer Kotlin Spatial SDK or Unity; explain that Native OpenXR
  requires an existing project. Do not route SpatialML to WebSpatial.
- Treat a requested SpatialML behavior as an app feature. For a new Kotlin app, apply the global
  executable-design gate before project creation: route through `spatial-design-to-app`, which uses
  `pico-spatial-app-designer` when the user did not provide an executable design. Onboarding may run
  only as that workflow's scaffold substep. Direct `spatial-app-onboarding` is reserved for an
  explicitly featureless parent scaffold.
- Restate the requested experience as `input -> inference -> output`, call out any unresolved model or
  privacy/readback decision in plain language, then execute as much of the workflow as the environment
  and current capabilities allow.
- Explain confirmations, manual editor steps, and unavailable capabilities when they occur. Do not
  make beginners copy internal command sequences merely to advance the workflow.
- End with build/run evidence from the owning SDK, emulator, or device, or state exactly what remains
  unverified and why.

## Route The Request

- For a new SpatialML app, choose the requested parent SDK and apply its project-creation route before
  resuming this skill. A feature-bearing Kotlin app routes through `spatial-design-to-app` and its
  designer gate; onboarding is only a scaffold substep. Do not make SpatialML a separate project type.
- For Pipeline Zoo discovery, selection, installation, adaptation, import, loader use, or package
  verification, stay in this skill and read `references/pipeline-zoo.md` before acting.
- A full app request continues from the package sub-workflow into parent-SDK application integration,
  build, and runtime verification. A package-only request may stop after the package sub-workflow's
  verification and SDK-owned import or placement.
- For project readiness, use the `spatialml onboard` → owning SDK setup → `spatialml setup` →
  `spatialml doctor` sequence.
- For custom package validation or model inspection, use the registered `spatialml pipeline verify`,
  `spatialml model inspect`, and `spatialml model visualize` commands.
- For implementing, reviewing, or debugging an SDK graph—including camera-to-model flow, operator
  selection, LiteRT inference, 2D-to-3D projection, mode-specific output, pipeline ordering, and
  readback—read `references/implementation-workflows.md` before changing code.
- Use the owning SDK's app-development workflow for application code, build, install, launch, and
  runtime validation. This skill owns the SpatialML integration steps, not the parent SDK.
- Use pySpatialML directly for authoring or isolated package execution that does not yet have a
  first-class pico-cli command. For example, use `pyspatialml package create`, `pyspatialml run host`,
  or `pyspatialml run device` for one identified package. Use pico-cli's app/device diagnostics for the
  complete built application, including crashes and SpatialML/OpenMR runtime evidence, regardless of
  whether its pipelines came from the Zoo or were created in code.
- If no package is an exact match, adapt the closest structurally compatible package instead of
  starting from nothing. Preserve its proven input plumbing, operator graph, shape handling, and
  rendering path; replace only the components required by the new use case.
- If no package offers a reusable topology, author the pipeline and package with the installed
  pySpatialML CLI. Do not infer package fields from existing Zoo packages or duplicate pySpatialML's
  validation rules in application code.

## Preflight External Unity Ownership

Unity workflow ownership is outside this plugin. Before promising or making a Unity-specific
handoff, inspect the live available skill inventory rather than assuming that **PICO Unity Agentic
Tools** (`pico-unity-agentic-tools`) is installed:

- A new Unity parent project requires the Unity plugin's manual-only `pico-unity-init` skill. Never
  invoke it automatically.
- An initialized Unity project that needs SDK repair or recovery of a missing
  `SpatialMLPipelineZooImporterCli` requires the Unity plugin's
  `pico-unity-package-manager` skill. Never route that project back to `pico-unity-init`.
- If Unity is explicitly requested and the required skill is absent, report `BLOCKED`. Name the
  missing plugin and skill, tell the user to install or expose the PICO Unity Agentic Tools plugin,
  and require a new agent-host session before retrying. Do not invent a local replacement workflow.
- If the parent SDK is undecided and the workspace is empty, disclose that the Unity route is
  unavailable and offer Kotlin Spatial SDK as an available alternative. Do not silently choose or
  switch the SDK.
- An already initialized Unity project may continue through supported CLI-only inspection, onboard,
  setup, or doctor steps that do not require a Unity-owned mutation. Stop with `BLOCKED` as soon as a
  missing SDK, SDK repair, package-manager action, or importer recovery requires the external plugin.

Do not promise a simple side-by-side install through `pico-cli plugin install`. One configured scope
records one plugin platform, cross-platform plugin install is rejected, and
`pico-cli setup --platform unity` can switch the complete configured environment for that scope.
Tell the user to review the setup plan, choose the intended scope and host, and restart the agent host
after the Unity plugin is available.

## Implement Or Debug An SDK Graph

Read `references/implementation-workflows.md` for code-level SpatialML work. Its workflow stages are
SDK-neutral, but exact APIs are not: detect Unity XR, Unity Spatial, Kotlin Spatial, or Native OpenXR,
then retrieve current operator/core-API facts from `pico-dev-knowledge` for that SDK and mode. Never
assume the SDK documentation Markdown files exist in the consuming project, and never translate a C#,
Kotlin, or C++ API name mechanically into another SDK.

Project-local manifests, dependencies, imports, code, and build output remain the implementation
authority. If the knowledge graph is unavailable, proceed from verified project evidence and the
stable reference workflow, but identify any API spelling or mode support that remains unconfirmed.

## Set Up In The Correct Order

Start with a project owned by one of the supported SDKs. If the request begins with an empty
workspace, complete the owning SDK's creation workflow before step 1:

1. Run `pico-cli spatialml onboard --project <project> --format json`.
2. If the result says the parent SDK is missing, complete that SDK's setup first.
   - Feature-bearing new Kotlin Spatial SDK apps: route through `spatial-design-to-app`. If the user
     did not provide an executable design, its `pico-spatial-app-designer` gate must produce and
     accept one before implementation. Use `spatial-app-onboarding` only as its scaffold substep.
     Direct onboarding is allowed only when the requested parent scaffold is explicitly featureless.
     Existing apps continue through their normal project workflow.
   - New Unity projects: after the external-skill preflight passes, hand off to the PICO Unity
     plugin's manual-only `pico-unity-init` skill. If it is unavailable, report `BLOCKED`; this skill
     does not install or alter the Unity SDK.
   - Initialized Unity projects needing SDK repair: after the external-skill preflight passes, hand
     off to `pico-unity-package-manager`. The manual-only `pico-unity-init` skill is not a repair
     path.
   - Native OpenXR projects: start from an existing PICO OpenXR project; do not ask Primer to create a
     Native project because Native is not a current Primer project type.
3. Run `pico-cli spatialml setup --project <project> --format json`.
4. Run `pico-cli spatialml doctor --project <project> --format json` and address its next action.

`onboard` and `doctor` assess and explain. `setup` is the explicit SpatialML mutation step and only
runs after the parent SDK is present. Read doctor's capability matrix separately from project checks:
a project can be ready while delegated pySpatialML capabilities remain unavailable. A missing or
incompatible pySpatialML executable makes doctor `PARTIAL`; invoking a delegated command still fails
with exit code `3`.

Install or update the supported public tool with:

```bash
python3.13 -m pip install --upgrade pyspatialml-pico
pyspatialml --version
```

pico-cli supports pySpatialML 0.5.0 or newer and normally resolves `pyspatialml` from `PATH`. Set
`PICO_CLI_PYSPATIALML` to an explicit executable path when the command is installed elsewhere.

## Prefer Pipeline Zoo Packages

Read `references/pipeline-zoo.md` before working with a reusable package. It owns the complete
cross-SDK package sub-workflow: trusted search and acquisition, structural selection, bounded model
adaptation, tensor-contract comparison, verification, SDK-specific placement/import, and mandatory
runtime loading through the owning SDK. Use it for package-only requests and as a sub-workflow of full
app creation.

## Validate Or Inspect Custom Work

Use the stable pico-cli surface:

```bash
pico-cli spatialml pipeline verify --package <package-dir> --format json
pico-cli spatialml model inspect <model.tflite> --format json
pico-cli spatialml model visualize <model.tflite> --format json
```

These commands delegate to the installed `pyspatialml` executable and preserve its structured
`PSM_*` error code inside pico-cli's tool-result envelope. `PSM_TOOL_UNAVAILABLE` means the executable
is missing or incompatible; install or update `pyspatialml-pico`, confirm `pyspatialml --version`, or
set `PICO_CLI_PYSPATIALML`, then retry. Do not claim validation or inspection succeeded when an error
is returned.

pico-cli remains the SDK-aware orchestrator while pySpatialML owns package validation, authoring, model
metadata inspection, visualization, and execution/debugging of an identified pipeline. Do not route
general application debugging through pySpatialML: whole-app logs, crash
monitoring, process/service state, screenshots, and traces belong to pico-cli's app/device diagnostic
workflow. LiteRT-CLI is resolved by pySpatialML; agents must not invoke `litert` directly as a
substitute.

## Model And Package Rules

- Deploy portable LiteRT/TFLite (`.tflite`) models and rely on runtime JIT compilation.
- Do not generate QNN `.serialized.bin`/`.serialized.json` context binaries.
- Do not use Docker conversion scripts or choose between QNN 2.29 and 2.37.
- Do not expose `litert compile` or add an NPU AOT path.
- Treat pySpatialML's in-Python TFLite pipeline runtime as portable across supported Mac, Windows, and
  Linux hosts.
- Do not use a successful host run as proof of device-only behavior such as hardware-delegate
  performance, PICO runtime services, permissions, or camera/VST input.
- Keep package paths relative; reject leading `/` and `..`.
- Keep SDK-specific binding and installation details in adapters; do not fork the shared package
  validation rules by SDK.
- Always load a package through the detected SDK's package loader instead of reconstructing its graph
  from JSON.

## Verification Checklist

- Parent SDK setup completed before `spatialml setup`.
- `spatialml doctor` reports the expected SDK and mode.
- Pipeline Zoo was checked for both exact matches and structurally reusable bases before reporting
  that no suitable package exists.
- Any model replacement has an explicit old-versus-new tensor contract and updates all affected
  preprocessing, post-processing, bindings, and branches.
- The final package is loaded by the owning SDK's package loader, not by app-side JSON graph
  reconstruction.
- Model and package use LiteRT/TFLite, not QNN context binaries.
- No Docker, bash-only conversion, direct `litert`, or AOT step was introduced.
- pySpatialML is at least version 0.5.0, or its availability error is reported with the install/update
  action.
- Final runtime behavior is verified in the owning SDK, emulator, or selected device as appropriate.
