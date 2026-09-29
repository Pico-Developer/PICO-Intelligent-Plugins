---
name: spatialml
description: Create, extend, author, validate, or debug SpatialML-enabled Kotlin Spatial SDK apps, and route Unity SpatialML work to PICO Unity Agentic Tools. Use for SpatialML, SecureMR, OpenMR, custom pipeline/package, Pipeline Zoo, operator selection, LiteRT/TFLite inference, VST/camera-to-model graphs, 2D-to-3D placement, Spatial output, tensor synchronization, or readback/debugging in a PICO app. Also use when spatial input implicitly feeds ML detection, classification, segmentation, pose estimation, recognition, or model-driven tracking. Covers Kotlin SDK sequencing, setup/doctor diagnosis, pySpatialML delegation, SDK knowledge retrieval, implementation workflows, package loading, validation, authoring, and pipeline versus whole-app debugging.
license: 'Apache-2.0'
---

# SpatialML App Workflow

Add SpatialML to an existing Kotlin Spatial SDK app, then validate the integration. SpatialML is not
a separate project type and this skill must not replace Kotlin SDK setup. Unity
SpatialML is owned by the PICO Unity Agentic Tools plugin, not by this workflow.

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
- normal parent-SDK project creation, scene work, UI, emulator use, or performance diagnosis.

When the request is ambiguous, identify the intended input, inference task, and output. If it only
uses a platform-provided tracking result, stay with the Kotlin SDK workflow. If it runs a model or
constructs a SpatialML pipeline over that data, use this skill.

## Guide Beginners From Natural Language

When the user is new, let them describe the experience instead of requiring command names or
SpatialML terminology. Read `references/natural-language-quickstart.md` and translate the request into
Kotlin SDK, SpatialML, Pipeline Zoo, application, and verification steps.

- Inspect the current project to distinguish Kotlin Spatial SDK from Unity before asking.
- For Unity, hand the complete request to PICO Unity Agentic Tools' `spatialml` skill. Do not continue
  with this workflow's setup, package, implementation, or runtime instructions.
- If the workspace is empty and the SDK is unspecified, use Kotlin Spatial SDK. Do not route
  SpatialML to WebSpatial.
- Treat a requested SpatialML behavior as an app feature. For a new Kotlin app, apply the global
  executable-design gate before project creation: route through `spatial-design-to-app`, which uses
  `pico-spatial-app-designer` when the user did not provide an executable design. Onboarding may run
  only as that workflow's scaffold substep. Direct `spatial-app-onboarding` is reserved for an
  explicitly featureless parent scaffold.
- Restate the requested experience as `input -> inference -> output`, call out any unresolved model or
  privacy/readback decision in plain language, then execute as much of the workflow as the environment
  and current capabilities allow.
- Explain confirmations, manual steps, and unavailable capabilities when they occur. Do not
  make beginners copy internal command sequences merely to advance the workflow.
- End with build/run evidence from the Kotlin SDK, emulator, or device, or state exactly what remains
  unverified and why.

## Route The Request

- For service logging, global tensor probes, zero/stale output, or readback permission failures,
  use this plugin's `spatialml-debugging` skill. It owns the debug flag, capture, value inspection,
  and cleanup workflow; resume this skill for broader graph or package changes.

- A Unity project or explicit Unity request leaves this plugin immediately: hand the complete request
  to PICO Unity Agentic Tools' `spatialml` skill. If it is unavailable, report `BLOCKED`, name the
  missing plugin, and require installation plus an agent-host restart.
- For a new Kotlin SpatialML app, apply its project-creation route before resuming this skill. A
  feature-bearing Kotlin app routes through `spatial-design-to-app` and its
  designer gate; onboarding is only a scaffold substep. Do not make SpatialML a separate project type.
- For Pipeline Zoo discovery, selection, installation, adaptation, import, loader use, or package
  verification, stay in this skill and read `references/pipeline-zoo.md` before acting.
- A full app request continues from the package sub-workflow into Kotlin application integration,
  build, and runtime verification. A package-only request may stop after verification and SDK-owned
  placement.
- For project readiness, use the `spatialml onboard` → Kotlin SDK setup → `spatialml setup` →
  `spatialml doctor` sequence.
- For custom package validation or model inspection, use the registered `spatialml pipeline verify`,
  `spatialml model inspect`, and `spatialml model visualize` commands.
- For implementing, reviewing, or debugging an SDK graph—including camera-to-model flow, operator
  selection, LiteRT inference, 2D-to-3D projection, Spatial output, pipeline ordering, and
  readback—read `references/implementation-workflows.md` before changing code.
- Use the Kotlin SDK's app-development workflow for application code, build, install, launch, and
  runtime validation. This skill owns the SpatialML integration steps, not Kotlin project setup.
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

## Implement Or Debug An SDK Graph

Read `references/implementation-workflows.md` for code-level SpatialML work. Retrieve current Kotlin
operator and core-API facts from `pico-dev-knowledge` for the detected SDK version and mode. Never
assume the SDK documentation Markdown files exist in the consuming project, and do not infer Kotlin
APIs mechanically from another SDK.

Project-local manifests, dependencies, imports, code, and build output remain the implementation
authority. If the knowledge graph is unavailable, proceed from verified project evidence and the
stable reference workflow, but identify any API spelling or mode support that remains unconfirmed.

## Set Up In The Correct Order

Start with a Kotlin Spatial SDK project. If the request begins with an empty workspace, complete the
Kotlin SDK's creation workflow before step 1:

1. Run `pico-cli spatialml onboard --project <project> --format json`.
2. If the result says the Kotlin SDK is missing, complete its setup first.
   - Feature-bearing new Kotlin Spatial SDK apps: route through `spatial-design-to-app`. If the user
     did not provide an executable design, its `pico-spatial-app-designer` gate must produce and
     accept one before implementation. Use `spatial-app-onboarding` only as its scaffold substep.
     Direct onboarding is allowed only when the requested parent scaffold is explicitly featureless.
     Existing apps continue through their normal project workflow.
3. Run `pico-cli spatialml setup --project <project> --format json`.
4. Run `pico-cli spatialml doctor --project <project> --format json` and address its next action.

`onboard` and `doctor` assess and explain. `setup` is the explicit SpatialML mutation step and only
runs after the Kotlin SDK is present. Read doctor's capability matrix separately from project checks:
a project can be ready while delegated pySpatialML capabilities remain unavailable. A missing or
incompatible pySpatialML executable makes doctor `PARTIAL`; invoking a delegated command still fails
with exit code `3`.

Install or update the supported public tool with:

```bash
uv tool install --upgrade --python 3.13 --system-certs pyspatialml-pico
pyspatialml --version
```

pico-cli supports pySpatialML 0.5.0 or newer and normally resolves `pyspatialml` from `PATH`. Set
`PICO_CLI_PYSPATIALML` to an explicit executable path when the command is installed elsewhere.

## Prefer Pipeline Zoo Packages

Read `references/pipeline-zoo.md` before working with a reusable package. It owns the complete Kotlin
package sub-workflow: trusted search and acquisition, structural selection, bounded
model adaptation, tensor-contract comparison, verification, Kotlin placement, and mandatory runtime
loading through the Kotlin SDK. Use it for package-only requests and as a sub-workflow of full
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
- Keep Kotlin binding and installation details in its adapter; do not fork the shared package
  validation rules by SDK.
- Treat a Pipeline Zoo search with `catalog.truncated=true` as non-exhaustive, and report its
  `continuationUrl` instead of claiming that no matching package exists.
- Always pass an explicit package directory or ZIP to `spatialml pipeline verify --package <path>`;
  verification never defaults to the current directory.
- Always load a package through the Kotlin SDK's package loader instead of reconstructing its graph
  from JSON.

## Verification Checklist

- Parent SDK setup completed before `spatialml setup`.
- `spatialml doctor` reports the expected SDK and mode.
- Pipeline Zoo was checked for both exact matches and structurally reusable bases before reporting
  that no suitable package exists.
- Any model replacement has an explicit old-versus-new tensor contract and updates all affected
  preprocessing, post-processing, bindings, and branches.
- The final package is loaded by the Kotlin SDK's package loader, not by app-side JSON graph
  reconstruction.
- Model and package use LiteRT/TFLite, not QNN context binaries.
- No Docker, bash-only conversion, direct `litert`, or AOT step was introduced.
- pySpatialML is at least version 0.5.0, or its availability error is reported with the install/update
  action.
- Final runtime behavior is verified in the Kotlin SDK, emulator, or selected device as appropriate.
