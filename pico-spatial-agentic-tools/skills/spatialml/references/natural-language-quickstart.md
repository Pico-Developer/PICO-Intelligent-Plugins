# Create a SpatialML App with an AI Assistant

This guide is for someone who knows the experience they want but does not yet know SpatialML, SDK,
or `pico-cli` terminology. The user describes the outcome; the assistant selects the installed skills,
runs supported commands, edits the app, and explains any confirmation or manual step.

## One-Time Preparation

1. Install Node.js 18 or newer and an AI coding assistant supported by `pico-cli`, such as Claude
   Code, Codex, Cursor, GitHub Copilot, or Trae CLI.
2. Install `pico-cli` with `npm install -g @picoxr/pico-cli`.
3. From the intended project directory, run `pico-cli setup` and select the applicable PICO plugin and
   agent host.
4. Close and reopen the assistant so its skills, project guidance, and knowledge tools are reloaded.

After that, the user should normally speak to the assistant rather than manually reproduce the
commands in this guide. A useful first request is:

```text
Check that pico-cli, the PICO plugin, and the SpatialML development knowledge are ready for this
project. Explain anything I need to install or confirm.
```

## What to Tell the Assistant

A good request names four things in ordinary language:

1. **Parent SDK** when known: Kotlin Spatial SDK, Unity, or an existing Native OpenXR project.
2. **Input**: VST/passthrough camera, an image, depth, microphone/audio, or another tensor source.
3. **Inference goal**: detect, classify, segment, recognize, estimate pose, or run a particular
   LiteRT/TFLite model.
4. **Output**: boxes, labels, a mask, an overlay, an animation, audio, or data returned to app code.

The user can also ask the assistant to build, run, inspect logs, and show evidence in the same prompt.
For example:

```text
Build a Kotlin Spatial SDK app that uses the passthrough camera to detect faces and draws a box around
each face. Start with the closest reusable Pipeline Zoo package. Set up the project, run it in the
PICO emulator or on a connected device, fix crashes from the logs, and show me a screenshot. Explain
any choice or confirmation in beginner-friendly language.
```

```text
In this existing PICO Unity project, add on-device pose estimation from the camera and use the result
to drive an avatar. Find and import the closest Pipeline Zoo package through the Unity SDK importer,
then build and verify the app. Do not replace the PICO Unity SDK that is already installed.
```

```text
This is an existing Native OpenXR PICO app. Add a SpatialML pipeline that classifies microphone audio
with my model.tflite and shows the current label. Inspect the model contract first and tell me clearly
if model inspection or package verification is not available yet.
```

If the SDK is unknown, the user can say:

```text
I am new to PICO development. I want an app that recognizes household objects from the passthrough
camera and labels them. Help me choose between Kotlin Spatial SDK and Unity, then create the first
runnable version and explain what you are doing as we go.
```

## What the Assistant Should Do

The assistant translates the natural-language request into this workflow:

1. Inspect the workspace and environment. Infer the parent SDK when possible.
2. Reduce the feature to `input -> inference -> output` and surface only decisions that materially
   affect the app, such as SDK choice, model choice, or whether results must be read back to app code.
3. Apply the owning SDK's app-creation gate before changing SpatialML. A feature-bearing new Kotlin
   app goes through `spatial-design-to-app`; when the user supplied no executable design, its
   `pico-spatial-app-designer` gate produces and accepts one first. Onboarding is only a scaffold
   substep, except for an explicitly featureless parent scaffold.
4. Run SpatialML setup and doctor, keeping project readiness separate from pySpatialML tool
   availability. Install `pyspatialml-pico` when package validation, model inspection, visualization,
   authoring, or package-scoped execution is needed and doctor reports that it is missing.
5. Search the `picoxr` Pipeline Zoo for an exact package or the closest reusable topology before
   considering custom work.
6. Install/import with the owning SDK and load through that SDK's package loader.
7. Add the minimum application code and scene/UI needed to present the result.
8. Build, install, launch, inspect logs, and capture runtime evidence. Camera, sensor, hardware
   acceleration, permissions, and rendering behavior need emulator/device evidence; a host-only test
   is not enough.

The assistant should keep going through safe, in-scope steps. It should pause only for a meaningful
choice, authorization, unavailable dependency, or manual SDK/editor action.

## Parent SDK Boundaries

- **Kotlin Spatial SDK:** SpatialML inference is a product feature, so a new app routes through
  `spatial-design-to-app` and its executable-design gate. That workflow may call
  `spatial-app-onboarding` only to create the scaffold. Direct onboarding is reserved for an
  explicitly featureless parent scaffold. Pipeline packages load with
  `SpatialMLSession.loadPipelinePackageFromAssets(...)`.
- **Unity:** SpatialML is added only after the PICO Unity SDK is present. New Unity/PICO SDK setup uses
  the separately installed PICO Unity Agentic Tools plugin's explicit `/pico-unity-init` workflow.
  Before this handoff, inspect the live skill inventory. If Unity was explicitly requested and the
  skill is unavailable, report `BLOCKED` with plugin installation and host-restart guidance. If the
  SDK is undecided in an empty workspace, disclose that Unity is unavailable and offer Kotlin instead;
  never switch silently. An initialized SDK repair uses the Unity plugin's
  `pico-unity-package-manager`, not `/pico-unity-init`. Pipeline installation finishes only through
  the Unity SDK importer and its generated `SpatialMLPipelineZooAsset`.
- **Native OpenXR:** start from an existing PICO OpenXR project. Pipeline packages load through the
  Native samples' `SecureMrUtils::LoadModelPackagePipelinesFromAssets(...)` utility path.

SpatialML is not a standalone project type, and WebSpatial is not one of its parent SDKs.

## Terms a Beginner May See

- **Pipeline:** the ordered input, preprocessing, inference, post-processing, and output work.
- **Pipeline Zoo:** reusable packages that provide a proven pipeline as a starting point.
- **LiteRT/TFLite model:** the portable `.tflite` model used at runtime with JIT compilation.
- **Secure Mode:** keeps sensitive data inside the protected SpatialML path when app code does not
  need the raw result.
- **Readback Mode:** lets app code receive approved pipeline results when the feature needs them; the
  assistant must account for the corresponding permissions and privacy boundary.
- **`PARTIAL` doctor status:** the project may be correctly configured even if an optional delegated
  inspection or validation tool is not available. The assistant should explain the exact check rather
  than treating every `PARTIAL` result as project failure.
