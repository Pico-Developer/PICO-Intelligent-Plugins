# pico-cli SpatialML Commands

Use this reference when the user asks how to set up, diagnose, search for, install, verify, inspect, or
visualize SpatialML content through `pico-cli`.

## Required Order

SpatialML setup extends an existing Kotlin Spatial SDK project. It does not install or replace the
Kotlin SDK.

1. Start with an existing Kotlin Spatial SDK project. Hand Unity requests to PICO Unity Agentic
   Tools' `spatialml` skill.
2. Assess the project:

   ```bash
   pico-cli spatialml onboard --project <project-path> --format json
   ```

3. If onboarding reports that the Kotlin SDK is missing, complete its setup first.
   - Kotlin: create or prepare the Spatial SDK project through the normal project workflow.
4. Configure SpatialML only after the Kotlin SDK is ready:

   ```bash
   pico-cli spatialml setup --project <project-path> --format json
   ```

5. Check readiness:

   ```bash
   pico-cli spatialml doctor --project <project-path> --format json
   ```

Treat `onboard` and `doctor` as read-only assessment commands. `setup` may write project files, so
inspect its JSON result and report every changed path.

## Project Commands

| Goal                               | Command                                                     | Notes                                                           |
| ---------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| Detect the SDK and next setup step | `pico-cli spatialml onboard --project <path> --format json` | Routes to the Kotlin SDK workflow; it does not install the SDK. |
| Configure SpatialML                | `pico-cli spatialml setup --project <path> --format json`   | Run only after SDK setup; Kotlin may update project files.      |
| Diagnose project readiness         | `pico-cli spatialml doctor --project <path> --format json`  | Reports SDK, mode/configuration checks, and the next action.    |

If detection fails, confirm that `--project` points at the actual SDK project root. Do not create
generic marker files merely to make detection pass.

## Pipeline Zoo Commands

Prefer a reusable Pipeline Zoo package before greenfield package authoring. If no package is an exact
match, use the closest structurally compatible package as a base so its proven input handling,
operator plumbing, shape checks, coordinate mapping, and rendering can be retained.

### Search

```bash
pico-cli spatialml pipeline search "<capability>" --format json
```

Compare each result's `description`, `modes`, `model`, and `modelCardUrl` with the requested behavior
and project mode. Rank packages by reusable pipeline topology, not only by repository or model name.
Prefer the candidate requiring the fewest model-facing changes.

### Install

```bash
pico-cli spatialml pipeline install <picoxr/repository-id> \
  --project <project-path> \
  --format json
```

Installation downloads the ZIP into a temporary local directory and extracts the complete package
before Kotlin installation begins.

- Kotlin installs into the adapter-resolved project assets location.

For adaptation, preserve the installed package and work on a separately named copy. Compare the old
and new model's input/output count, names, shape/layout, dtype, quantization, normalization, and
semantics. Update affected preprocessing, post-processing, bindings, constants, and downstream
branches before validating the derived package. The install command accepts a Zoo repository id; it
does not install arbitrary local derived packages.

### Runtime Loading

Always load the complete package through the Kotlin SDK's package loader. Package JSON may be
inspected for a bounded adaptation, but application code must not reconstruct its graph:

- Kotlin calls `SpatialMLSession.loadPipelinePackageFromAssets(assetRoot, externalGlobals)` and uses
  the returned `PipelinePackageBundle`.

Do not substitute standalone JSON deserialization or hand-written operator, tensor, edge, scheduling,
or global-binding code for these loaders, including for a derived package.

### Verify

```bash
pico-cli spatialml pipeline verify --package <package-directory-or-zip> --format json
```

This command delegates to `pyspatialml package validate`. Install the public package with
`uv tool install --upgrade --python 3.13 --system-certs pyspatialml-pico`; pico-cli supports pySpatialML 0.5.0 or newer.
It resolves `pyspatialml` from `PATH`, or uses the executable named by `PICO_CLI_PYSPATIALML`. A
missing or incompatible executable returns `PSM_TOOL_UNAVAILABLE` with exit code `3`. Do not
substitute legacy Docker, QNN context-binary, or standalone JSON-pipeline tooling.

## Model Commands

```bash
pico-cli spatialml model inspect <model.tflite> --format json
pico-cli spatialml model visualize <model.tflite> --format json
```

These LiteRT/TFLite commands delegate to `pyspatialml model info` and
`pyspatialml visualize model`. pySpatialML owns LiteRT tool resolution; do not invoke `litert`
directly. If either command returns `PSM_TOOL_UNAVAILABLE`, repair the installation as described
above and do not claim inspection or visualization succeeded.

## Output Handling

All current SpatialML commands support `--format plain|json`; prefer JSON for agent workflows.

- `SUCCESS`: the requested read or operation completed.
- `PARTIAL`: a handoff or additional SDK-owned step remains.
- `FAILED`: inspect `errors`, `meta.hint`, and `meta.exitCode` before choosing the next action.

Always report the detected SDK, project path, changed or installed paths, and any explicit handoff.
