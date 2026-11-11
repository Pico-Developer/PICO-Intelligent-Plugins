### Stage 4 — Build

#### Module mode

- **Existing module:** keep namespace/package, manifest wiring, and entry chain. Allowed: new Compose files, drawables, strings, state holders. NOT allowed without explicit escalation: switching root container, changing `pico.spatial.windowcontainer.*` meta-data, introducing Stage-only APIs (anchor / ECS / env_mesh) inside a WindowContainer.
- **New project:** the project is created by `pico-cli project create` — never by hand. Delegate the scaffold step to `spatial-app-onboarding`, passing the resolved application ID unchanged and the Decide-stage container as the template (`ON_PLAIN → planar`, `IN_VOLUME → volumetric`, `STAGE_* → stage`). Resume only after it returns `<target>/.scratch/onboarding_handoff.json`. The handoff must be scaffold-only (`product_ui_implemented=false`); if onboarding implemented product UI, treat that as a failure and rebuild the UI here. Then build the requested experience on top of the generated entry point — do not re-scaffold, rewrite `mainApp`, or re-insert manifest meta-data.

> 🔴 **The CLI owns the project skeleton. This skill never hand-assembles one.**
>
> `pico-cli project create` owns the Gradle setup, dependency versions,
> repositories, package layout, `Main.kt` entry chain, and a fully-populated
> `AndroidManifest.xml` with container meta-data already in place. Do **not**
> author `build.gradle.kts`, `settings.gradle.kts`, `libs.versions.toml`, or
> `gradle-wrapper.properties` from scratch or from a remembered template — a
> hand-built skeleton drifts from the CLI baseline and fails in ways nobody can
> reproduce.
>
> What you legitimately do after the CLI runs:
>
> - write product Kotlin/Compose on top of the generated entry point
> - add dependency lines the design genuinely requires (for example the sense dependency when the design needs anchors)
> - for `STAGE_*`, edit the four `pico.spatial.stage.*` values the CLI already emitted so they match the chosen variant — all three variants share `--template stage`, so the CLI cannot know which one you decided on. The value matrix is in `./manifest-and-entry.md` → "Choosing the Stage variant".
>
> If the project foundation is genuinely broken (unresolvable SDK, toolchain
> mismatch), re-create it with the CLI or hand off to `spatial-sdk-update`. Do
> not repair build foundations here — see `./build-failures.md`.

Entry chain (created by the CLI; verify rather than rewrite):
`Application.onCreate { launch(::mainApp) }` → `mainApp(scope: SpatialAppScope)` → `DefaultWindowContainer {}` or `DefaultStage {}` → `SpatialLaunchActivity`.

**Android Studio sync is mandatory for new modules.** After a new module is
included, trigger **Sync Project with Gradle Files** before claiming the app runs
from the IDE. If no IDE-sync API is available, run the Gradle discovery proxy in
stage 5 and tell the user sync is still required.
