# Build Failure Diagnosis

For diagnosing a failing `smoke_build.sh` / Gradle sync during the Verify stage.

> **This file does not contain Gradle configuration templates, and that is
> deliberate.** The project's Gradle setup, dependency versions, repositories,
> and manifest are owned entirely by `pico-cli project create`. Copying config
> snippets out of a skill document is how a project drifts away from the CLI
> baseline and starts failing in ways no one can reproduce. If the Gradle
> foundation is broken, the answer is to re-create the project with the CLI or
> hand off to `spatial-sdk-update` — never to hand-patch build files from a
> remembered template.

## Symptom → cause

| Symptom                                                                     | Cause and fix                                                                                                                                                                                  |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Unresolved reference: <Component>`                                         | Check `spatial-ui-components.md` first — the component is probably invented or not in this SDK version. Do not "fix" it by adding a dependency.                                                |
| `Unresolved reference: SpatialLaunchActivity`                               | The Spatial UI platform dependency is missing from the module. The CLI baseline includes it; a project missing it was hand-assembled or partially migrated → `spatial-sdk-update`.             |
| `Unresolved reference: WorldTrackingManager` / `PlaneAnchor` / `MeshAnchor` | The sense dependency is missing. World / plane / mesh anchors all live under `com.pico.spatial.sense.*`, not `tracking`. Add the dependency the CLI template uses for anchor-capable projects. |
| `Could not find com.pico.spatial:bom`                                       | The Spatial SDK is not resolvable from the local Maven repository, or the repository declaration is missing. This is an environment/baseline problem → `spatial-sdk-update`.                   |
| `Could not resolve com.pico.spatial.ui:*`                                   | The BOM is not being applied as a platform constraint. Baseline problem → `spatial-sdk-update`.                                                                                                |
| `AGP X.Y requires Gradle Z`                                                 | Toolchain version mismatch. Do not hand-bump the wrapper → `spatial-sdk-update`.                                                                                                               |
| `IllegalStateException: not in Full Space`                                  | A Stage-only API was called from a WindowContainer flow. This is a Decide-stage error, not a build error: re-run the container decision (`structure-decisions.md`, `spatial-anchor.md`).       |
| `mainApp` not invoked / blank window after install                          | Entry chain or manifest wiring is broken. See `manifest-and-entry.md`.                                                                                                                         |
| `gradlew not found`                                                         | The target is not a CLI-generated project root. Verify the path, or create the project with `pico-cli project create`.                                                                         |

## Rule of thumb

Sort every build failure into one of three buckets:

1. **My generated code is wrong** — wrong component name, wrong import, wrong container for the API. Fix the code.
2. **My decision was wrong** — a Stage API in a window flow, an anchor in `ON_PLAIN`. Go back to the Decide stage; do not patch around it.
3. **The project foundation is wrong** — missing BOM, unresolvable SDK, toolchain mismatch. This skill does not repair build foundations. Re-create with `pico-cli project create`, or hand off to `spatial-sdk-update`.

Bucket 3 is never fixed by editing `build.gradle.kts` from memory.
