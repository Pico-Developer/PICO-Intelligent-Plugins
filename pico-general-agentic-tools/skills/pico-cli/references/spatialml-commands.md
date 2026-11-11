# pico-cli SpatialML Commands

Use this reference when the user asks how to set up, diagnose, search for, install, verify, inspect, or
visualize SpatialML content through `pico-cli`.

## Choose the scope

Pipeline search, package verification, and model inspection/visualization can run without an SDK
project. Use the explicit package/model path or search query and check the selected command's help
and tool prerequisites. Do not create/configure a project or install a platform plugin for these
standalone tasks, including when the caller happens to be in a Unity directory.

Project onboarding, setup, readiness diagnosis, and pipeline installation support Kotlin Spatial
SDK, Unity, and Native OpenXR projects. Use these commands for cross-SDK assessment and installation;
hand SDK-owned initialization, source integration, and repairs to the configured platform plugin.
Use `pico-project-setup` only when the development task needs project/platform configuration.

## Project Integration Order

1. Assess the intended SDK project without changing it:

   ```bash
   pico-cli spatialml onboard --project <project-path> --format json
   ```

2. Follow the returned SDK-specific prerequisite or handoff before SpatialML setup:
   - Kotlin: prepare the Spatial SDK project through `pico-project-setup` if the SDK is missing.
   - Unity: complete the Unity platform plugin's initialization when the PICO Unity SDK is missing.
   - Native OpenXR: apply the returned SecureMR extension and lifecycle integration instructions.
     pico-cli does not rewrite application-specific OpenXR source.
3. Configure or validate SpatialML after those prerequisites are ready:

   ```bash
   pico-cli spatialml setup --project <project-path> --format json
   ```

4. Check SDK-specific readiness and delegated host-tool capabilities:

   ```bash
   pico-cli spatialml doctor --project <project-path> --format json
   ```

`onboard` and `doctor` are read-only assessments for all three SDKs. `doctor` may run a host-tool
capability check, but does not install the SDK or repair project files.

| SDK           | `setup` project behavior                                                                                                                                                          |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kotlin        | May update the application's Gradle dependency/BOM configuration, version catalog, and experimental API Manifest metadata. Requires an existing Spatial SDK project.              |
| Unity         | Validates the PICO Unity SDK and Pipeline Zoo importer without editing project files. Missing initialization or importer support returns an action for the Unity platform plugin. |
| Native OpenXR | Returns readiness when the SecureMR extension is enabled, otherwise manual source-integration instructions; does not rewrite native application code.                             |

Native readiness here is based on detected project/source configuration. It does not prove the
OpenXR extension is available on a device or that a pipeline runs correctly. Package installation
only places assets; native runtime loading and lifecycle integration remain application-specific.

When project prerequisites are ready, `setup` also attempts to install or upgrade pySpatialML on
the host for all three SDKs. Incomplete project prerequisites skip that installation; host-tool
installation failure returns an action-required result with manual guidance. Inspect `changes`,
`instructions`, `projectStatus`, and `pyspatialml` in the JSON result and report project and host effects.

## Project Commands

| Goal                               | Command                                                     | Notes                                                                                                                                                   |
| ---------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Detect the SDK and next setup step | `pico-cli spatialml onboard --project <path> --format json` | Read-only Kotlin, Unity, or Native OpenXR assessment with SDK-specific next actions.                                                                    |
| Configure or validate SpatialML    | `pico-cli spatialml setup --project <path> --format json`   | Kotlin may edit project files; Unity validates; Native reports readiness/manual integration. May install the shared host tool after prerequisites pass. |
| Diagnose project readiness         | `pico-cli spatialml doctor --project <path> --format json`  | Read-only SDK/mode checks, Unity importer readiness, delegated host-tool capabilities, and next actions.                                                |

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
and, for project integration, the project mode. Rank packages by reusable pipeline topology, not only by repository or model name.
Prefer the candidate requiring the fewest model-facing changes.

### Install

```bash
pico-cli spatialml pipeline install <picoxr/repository-id> \
  --project <project-path> \
  --format json
```

Installation downloads and extracts the complete ZIP before committing it to the SDK-specific destination.
The default `--overwrite fail` refuses an existing package; use `--overwrite replace` only when replacing it is intended.

- Kotlin installs into the adapter-resolved application assets location.
- Native OpenXR installs into the detected Android application's `src/main/assets/SpatialML/<package>`;
  when no Android module is detected, it uses the project's `assets/SpatialML/<package>`.
  Multiple Android application modules are ambiguous and require manual destination selection.
- Unity stages the source under `.pico-cli/spatialml-downloads` and invokes the PICO Unity SDK importer
  to create `.bytes` files and a `SpatialMLPipelineZooAsset` under `Assets/SpatialMLPipelineZoo/<package>`.
  Pass `--unity-editor <executable-path>` when the Editor executable needs to be selected explicitly:

  ```bash
  pico-cli spatialml pipeline install <picoxr/repository-id> \
    --project <unity-project-path> --unity-editor <unity-editor-executable> --format json
  ```

  If automatic import is unavailable, inspect the action-required result and its retained `sourcePath`.
  Follow the returned Unity platform repair or use **PICO > SpatialML > Import SpatialML Pipeline Zoo Package**
  with that source directory. Staging alone is not a successful import; direct copying does not create
  the required Unity assets. Preserve pinned, local, embedded, or custom SDK sources during repairs.

For adaptation, preserve the installed package and work on a separately named copy. Compare the old
and new model's input/output count, names, shape/layout, dtype, quantization, normalization, and
semantics. Update affected preprocessing, post-processing, bindings, constants, and downstream
branches before validating the derived package. The install command accepts a Zoo repository id; it
does not install arbitrary local derived packages.

### Runtime Loading

When integrating into a Kotlin Spatial SDK app, load the complete package through its package loader. Package JSON may be
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
`uv tool install --upgrade --python 3.13 --system-certs 'pyspatialml-pico>=0.5.3'`; pico-cli supports pySpatialML 0.5.3 or newer.
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

For project operations, report the detected SDK, project path, changed or installed paths, and any
explicit handoff. For standalone operations, report the query or input package/model path and the
actual result or artifact; do not invent an SDK/project requirement or report an unverified result
as successful.
