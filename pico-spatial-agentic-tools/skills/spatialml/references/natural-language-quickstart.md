# Create a SpatialML App with an AI Assistant

This guide is for someone who knows the experience they want but does not yet know SpatialML, SDK,
or `pico-cli` terminology. The user describes the outcome; the assistant selects the installed skills,
runs supported commands, edits the app, and explains any confirmation or manual step.

## One-Time Preparation

1. Install Node.js 20 or newer and an AI coding assistant supported by `pico-cli`, such as Claude
   Code, Codex, Cursor, GitHub Copilot, or Trae CLI.
2. Install `pico-cli` with `npm install -g @picoxr/pico-cli`.
3. Run `pico-cli setup` once, from outside any project directory. It installs the user-level PICO
   tools, skills, knowledge, and the global MCP servers (`pico-dev-knowledge`,
   `pico-spatial-editor`, `unity-mcp`) for the assistant you selected; it does not choose a platform
   plugin. When the assistant runs setup non-interactively (`--yes`), it must also pass a region
   explicitly, for example `--region cn`, because region is required on first run.
4. Open or create the project directory in that assistant and describe what you want to build. The
   assistant configures the project for the Kotlin Spatial SDK platform itself (`project configure`);
   you do not need to run another setup command.
5. Project configuration no longer adds project-level MCP servers — the MCP servers are user-level
   from setup and already available. A session reopen is only needed when the assistant cannot see
   newly installed project Skills in its tool list; otherwise project skills and guidance work in
   the current session.

After that, the user should normally speak to the assistant rather than manually reproduce the
commands in this guide. A useful first request is:

```text
Check that pico-cli, the PICO plugin, and the SpatialML development knowledge are ready for this
project. Explain anything I need to install or confirm.
```

## What to Tell the Assistant

A good request names four things in ordinary language:

1. **Parent SDK**: Kotlin Spatial SDK. Unity requests belong to PICO Unity Agentic Tools' `spatialml`
   skill.
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

If the SDK is unknown, the user can say:

```text
I am new to PICO development. I want an app that recognizes household objects from the passthrough
camera and labels them. Use Kotlin Spatial SDK, then create the first
runnable version and explain what you are doing as we go.
```

## What the Assistant Should Do

The assistant translates the natural-language request into this workflow:

1. Inspect the Kotlin Spatial SDK workspace and environment.
2. Reduce the feature to `input -> inference -> output` and surface only decisions that materially
   affect the app, such as SDK choice, model choice, or whether results must be read back to app code.
3. Use `spatial-app-dev-workflow` for a new Kotlin app's overall delivery, with
   `spatial-app-onboarding` for a missing scaffold and design/UI guidance as needed.
   Return to SpatialML setup and inference integration after project prerequisites are ready.
4. Run SpatialML setup and doctor, keeping project readiness separate from pySpatialML tool
   availability. Install `pyspatialml-pico` when package validation, model inspection, visualization,
   authoring, or package-scoped execution is needed and doctor reports that it is missing.
5. Search the `picoxr` Pipeline Zoo for an exact package or the closest reusable topology before
   considering custom work.
6. Install the package with the Kotlin SDK workflow and load it through the Kotlin package loader.
7. Add the minimum application code and scene/UI needed to present the result.
8. Build, install, launch, inspect logs, and capture runtime evidence. Camera, sensor, hardware
   acceleration, permissions, and rendering behavior need emulator/device evidence; a host-only test
   is not enough.

The assistant should keep going through safe, in-scope steps. It should pause only for a meaningful
choice, authorization, unavailable dependency, or manual SDK/editor action.

## Parent SDK Boundaries

- **Kotlin Spatial SDK:** use `spatial-app-dev-workflow` for app delivery, with
  `spatial-app-onboarding` for scaffolding and scoped design/UI guidance. Standalone
  onboarding supports a scaffold-only request. Pipeline packages load with
  `SpatialMLSession.loadPipelinePackageFromAssets(...)`.
- **Unity:** hand the complete request to PICO Unity Agentic Tools' `spatialml` skill. If that plugin is
  unavailable, report `BLOCKED` and continue `pico-project-setup` for the intended Unity engineering
  and resource roots. Read the returned continuation in the same session and verify native Unity
  tools before dependent work; follow the reported Host activation actions.
  SpatialML is not a standalone project type, and WebSpatial is not its parent SDK.

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
