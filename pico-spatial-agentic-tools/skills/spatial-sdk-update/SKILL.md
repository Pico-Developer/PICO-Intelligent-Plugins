---
name: spatial-sdk-update
description: Upgrades existing PICO Spatial/MR projects to a newer PICO Spatial SDK and PICO OS 6-compatible toolchain. Trigger for SDK/BOM, Gradle/AGP/Kotlin/NDK, deprecated or missing Spatial APIs, legacy spatial container managers, or compatibility migration in a project that is already Spatial/MR. Do NOT trigger for converting a traditional 2D Android app into a Spatial app; use porting-android-app for that.
license: 'Apache-2.0'
---

# spatial-sdk-update

Use this skill when you need to help the user upgrade an existing PICO Spatial SDK project (especially Android/Kotlin projects) to a newer version of the PICO Spatial SDK. This involves more than just simple API name replacements; it includes dependency resolution and project configuration upgrades.

Boundary: this skill assumes the project is already a PICO Spatial/MR
application. If the primary task is to transform a traditional Android
phone/tablet app into Spatial containers and interaction patterns, route to
`porting-android-app` instead.

Trigger boundary: only run this skill when the user explicitly asks to upgrade,
migrate, or change the Spatial SDK version (or when a build failure they asked
you to fix is unambiguously caused by an SDK version change). Upgrading the
business SDK is a user-initiated action — do not proactively propose or start an
SDK upgrade, and do not prompt users who only want to keep building against
their current version. When you notice a newer SDK exists but the user has not
asked to upgrade, at most mention it as an optional aside and continue with the
current version. Environment health and CLI/plugin/PICO development knowledge version
checks belong to `pico-env-doctor`, not here.

## Required Environment and Emulator Handoffs

Apply this gate only before environment-dependent execution; purely static code reading, planning, and edits do not require it.

1. Reuse the latest successful `pico-env-doctor` result only within the same Host session when the workspace, target Host, and tooling are unchanged, no setup/update/install/start command has run since, no new failure signal exists, and the user has not requested re-verification.
2. Otherwise activate `pico-env-doctor` before running any `pico-cli` command or querying `pico-dev-knowledge` MCP. Continue only after a healthy result; if it reports a blocker, stop the dependent execution and report that blocker.
3. After the gate passes, keep SDK selection and migration in this skill. Hand every device/emulator operation—including target discovery, emulator install/start/stop, APK install/launch, file transfer, screenshots/recordings, and device logs—to `spatial-emulator-usage`, then resume here with its evidence or blocker.

## Macro Upgrade Flow

Before initiating any code modifications, follow this closed-loop, iterative upgrade strategy:

```mermaid
graph TD
    Z[Phase 0: Discover Available SDK Versions, Select Target Line & Sync PICO development knowledge] --> A[Phase 1: Build & Dependency Fixes]
    A --> B{Gradle Sync Success?}
    B -- No --> C[Troubleshoot AGP/Compose/NDK Conflicts]
    C --> B
    B -- Yes --> D[Phase 2: Core API Migration & Adaptation]
    D --> E{Compile Success?}
    E -- No --> F[Analyze Errors/Deprecations and Replace]
    F --> E
    E -- Yes --> T[Phase 2.5: Sync Matching Spatial Toolchain]
    T --> G[Phase 3: Runtime Compliance (Store & Runtime Safety)]
    G --> H{No Runtime Crash?}
    H -- No --> I[Investigate Crash & Apply Fixes]
    I --> H
    H -- Yes --> J[Upgrade Migration Complete]
```

## Phase 0: Target Version and PICO development knowledge

Goal: establish the target Spatial SDK line before changing project files, then align the local PICO development knowledge used by MCP and future agent lookups.

- **[Must] Identify the current project SDK line from project evidence first**:
  - Prefer `gradle/libs.versions.toml` (`spatialBom` or equivalent), then direct Gradle BOM declarations such as `implementation(platform("com.pico.spatial:bom:<version>"))`.
  - If Gradle metadata is unclear, inspect build errors, lockfiles, project-local `.pico-env.json`, and existing generated setup notes before assuming a version.
  - Normalize the target SDK to the `major.minor` knowledge line. Example: SDK `0.13.5` maps to knowledge version `0.13`.
- **[Must] Discover the available SDK versions from the Maven repository before choosing the target**:
  - The Spatial SDK is resolved from a Maven repository — the external distribution ships as a local Maven repo under `~/.m2/repository` (`mavenLocal()`); internal/organization setups may add a URL-based repository. Read the versions the repository actually offers instead of guessing a bump.
  - Enumerate the published BOM versions from the resolved repository. For the local repo, list the version directories (and read `maven-metadata.xml` when present) under the BOM artifact:
    ```bash
    ls ~/.m2/repository/com/pico/spatial/bom
    cat ~/.m2/repository/com/pico/spatial/bom/maven-metadata.xml 2>/dev/null
    ```
    For a URL-based repository, read `<repo-url>/com/pico/spatial/bom/maven-metadata.xml`. The repository holds the full version history, so any previously published version remains selectable — never assume an older version is unavailable.
  - **Default to the newest published version** that is compatible with the target ROM coverage (see Phase 3), unless the user explicitly pins a specific version. When the user names a version, verify it exists in the enumerated list before adopting it; if it is missing, report the available versions instead of silently falling back.
  - If the repository cannot be read (SDK zip not extracted, repository not configured, or offline), report that exact blocker and the current project line rather than assuming the latest version. Do not fabricate a target version.
  - Carry the selected full version into Phase 1 (the BOM/version-catalog edit) and its `major.minor` line into the PICO development knowledge sync below.
- **[Must] Sync the matching PICO development knowledge after the target line is known**:
  - Run:
    ```bash
    pico-cli knowledge pull <major.minor> --platform spatial --projectRoot <projectRoot>
    ```
  - Example:
    ```bash
    pico-cli knowledge pull 0.13 --platform spatial --projectRoot /path/to/project
    ```
  - Omit `--project` only when the current working directory is the intended project root. The command defaults to the current directory and writes `<projectRoot>/.pico-env.json`.
  - This command installs or refreshes the PICO development knowledge and updates only the knowledge-related keys in `.pico-env.json` (`version`, `platform`, `agentVaultWorkspace`), preserving unrelated project-local keys.
  - Use `--source auto` by default. Pass `--source global` or `--source cn` only when the user or environment explicitly requires one of those sources.
- **[Must] Switch the live MCP knowledge graph to the installed workspace**:
  - Read the just-written `<projectRoot>/.pico-env.json` and extract `agentVaultWorkspace`.
  - Build the workspace directory as:
    ```text
    <PICO_HOME>/<agentVaultWorkspace>
    ```
    This workspace directory must contain `graphify-out/graph.json`.
  - Call the PICO development knowledge MCP `switch_workspace` tool with that workspace directory.
    ```text
    switch_workspace(workspace=<PICO_HOME>/<agentVaultWorkspace>)
    ```
  - Immediately call the same MCP server's `graph_stats` tool:
    ```text
    graph_stats()
    ```
    Treat successful stats output as confirmation that the new graph is loaded. If switching fails, keep the file changes but report that live MCP knowledge remained on the previous workspace.

## Phase 1: Build & Config

Goal: Quickly fill core gaps, resolve the most urgent build and compatibility issues, and ensure the project can compile under the new PICO ecosystem.

- **[Must] Upgrade Gradle, AGP, and Kotlin (keep versions consistent)**: PICO OS 6 and newer Spatial SDK versions generally require a modern Android toolchain. If Gradle sync fails, upgrade the project to a compatible combo (e.g., **AGP 8.x** with the matching Gradle wrapper), and set **Kotlin** to a version compatible with your AGP + Android Studio (do not guess a major jump). Ensure the **Compose Compiler** configuration matches the Kotlin version (use the official Compose–Kotlin compatibility table).
  - **SDK levels**: Keep `compileSdk = 35` and typically `targetSdk = 35` for PICO OS 6 projects. Note: upgrading `targetSdk` to 35 may introduce standard Android behavioral changes (e.g., edge-to-edge enforcement or stricter foreground service permissions); address these if the user encounters related issues.
  - **minSdk**: Do **not** blindly force `minSdk = 35`. Keep it aligned with the project baseline / template / business constraints, and only raise it if the user explicitly targets that requirement.
- **[Must] Remove Conflicting UI Dependencies (Compose)**: If the project uses **SpatialUI** components, you must exclude native AndroidX Jetpack Compose conflicting dependencies (e.g., `androidx.compose.ui:ui`, `ui-graphics`, `ui-text`, `androidx.compose.foundation:foundation`) using `exclude` or `configurations.all { resolutionStrategy { ... } }` in the module's `build.gradle.kts`.
- **[Must] Upgrade the Spatial SDK version at the right source of truth (BOM / Version Catalog)**:
  - Use the target version selected from the Maven repository in Phase 0 (default newest compatible, or the user-pinned version verified to exist). Do not introduce a version that was not confirmed available.
  - If the project uses **Version Catalog** (has `gradle/libs.versions.toml`), update the single version key (commonly `spatialBom`) and keep dependencies on `implementation(platform(libs.spatial.bom))`.
  - If the project does not use Version Catalog, update the BOM line directly: `implementation(platform("com.pico.spatial:bom:<new_version>"))` and keep module dependencies (`com.pico.spatial.core:core`, `com.pico.spatial.ui:*`, etc.) unchanged unless build errors require changes.
- **[Recommended] Common AGP 8+ upgrade pitfalls to check** (fix only if they appear during sync/build):
  - **BuildConfig**: AGP 8+ may stop generating `BuildConfig` by default; enable it if the project relies on `BuildConfig.*` or `buildConfigField`.
  - **Non-transitive R**: After upgrading AGP, resource IDs may fail if the project relied on legacy cascading `R` behavior; update resource references per-module.
  - **Namespace / Manifest cleanup**: Ensure `namespace` is set in `build.gradle.kts`, and remove legacy Manifest-only identifiers (e.g., module-level `package=` in `AndroidManifest.xml`) when they conflict with AGP rules.
- **[Must] Handle NDK Configurations**: The target system (PICO OS 6) **only supports the `arm64-v8a`** architecture. Ensure NDK ABI filtering is explicitly set in `build.gradle.kts`: `ndk { abiFilters.add("arm64-v8a") }`.
- **[Must] Strip GMS (Google Mobile Services) Dependencies**: PICO OS 6 operates without GMS. If GMS/Firebase dependencies are found during the upgrade/migration, they must be removed or commented out. Actively advise the user to implement alternatives.
- **[Must] AndroidManifest cleanup for PICO OS 6 / AGP 8+**: Ensure `namespace` is defined in `build.gradle(.kts)` and remove legacy Manifest-only identifiers that can break modern builds.
  - Remove module-level `package="..."` from `AndroidManifest.xml` when present (namespace is the source of truth).
  - Remove any legacy `android:launchMode="..."` attribute injected into `<activity>` declarations (especially the Spatial container/launch activity) unless the user explicitly requires a specific launch mode and it is known to be supported.

## Phase 2: Runtime & Logic (Core API Migration)

Goal: Eliminate all `unresolved reference` and `Deprecated` errors encountered at compile time, enabling business logic to run on the new architecture.

- **[Must] Replace Deprecated and Relocated Packages & Classes**:
  - **UI and Spatial Container Migration**: In spatial apps, developers are used to older interfaces for container control. In the new version, prioritize migrating to declarative Compose components and unified engine entry points like `SpatialApp`.
  - **Gesture and Control Refactoring**: Methods within click logic (e.g., `TapGestureDetector`) have `@Deprecated` markers. You must search for `pointerInput` and corresponding replacement methods to handle user taps or drags.
- **[Must] Reverse Engineer Replacements from Errors**:
  - If "class not found" errors occur, analyze the PICO SDK error messages (such as `ReplaceWith` deprecation warnings) to infer the new API.
  - Proactively search for similar interfaces in the project, or use global `grep` in the SDK's `source.jar` or `dependencies` cache to locate alternative names.
- **[Must] Remove Internally Restricted APIs (@RestrictTo)**:
  - Interfaces marked with `@RestrictTo(RestrictTo.Scope.LIBRARY_GROUP_PREFIX)` are **strictly forbidden from being used by the application side**. If legacy code accesses interfaces that are now restricted, those calls must be decisively removed or replaced with alternative official public APIs.

## Phase 2.5: Spatial Toolchain Before Runtime Validation

Goal: ensure the matching Spatial Editor and PICO Emulator are available after the project compiles, before running the app or investigating runtime crashes.

- **[Must] Check the matching Spatial toolchain before runtime validation**:
  - First inspect the full toolchain state with the root doctor when available:
    ```bash
    pico-cli doctor --format json --platform spatial
    ```
    Use the root doctor overview to read the current CLI, plugin, SDK, PICO
    development knowledge, emulator, and editor lines. Do not use
    `emulator doctor` as the SDK-version selector; emulator doctor is only for
    emulator readiness.
  - If the root doctor is unavailable or a module-level detail is needed, then
    inspect Spatial Editor state with its module doctor:
    ```bash
    pico-cli editor doctor --format json
    ```
  - If Spatial Editor for the target `major.minor` line is already installed and usable, record the detected path/version and do not download it again. Otherwise install or refresh it:
    ```bash
    pico-cli editor install --editor-version <major.minor>
    ```
  - Activate `spatial-emulator-usage` with the selected SDK `major.minor` line and any user-required source. The handoff must require `pico-cli emulator install <major.minor>` and pass `--bundle-version <major.minor>` to every create/start command. It owns emulator doctor/install and returns the usable bundle/AVD/version or the exact host/artifact blocker. Do not duplicate those commands here.
  - Use explicit sources such as global or CN only when the user or environment requires them, and pass that requirement into the handoff.
  - If a tool install fails because no artifact matches the current host, report the returned fallback state. Do not claim runtime validation is fully covered unless a usable matching Editor/Emulator is actually available.
  - If a tool install or doctor command is unavailable in the user's installed pico-cli, report that exact blocker before claiming runtime validation is possible.
- **[Must] Start a matching emulator when runtime validation needs one**:
  - Continue the `spatial-emulator-usage` handoff to inspect online targets. When it needs an AVD, require it to select from `pico-cli emulator list --managed-only --format json`; never use `emulator doctor` as the AVD selector. Before resuming migration, require the handoff result to normalize the returned `bundleVersion` and selected SDK to `major.minor`, confirm those version lines match, and identify the managed AVD it created or started.
  - Start the returned matching AVD when needed instead of stopping merely because no emulator is currently running.
  - That skill also owns APK install/launch, captures, and device/crash logs. Resume SDK migration here with its runtime evidence or concrete blocker.
  - Report runtime validation as skipped only when the handoff cannot provide a matching online emulator/device.

## Phase 3: Compliance & Capability (Platform Features)

Goal: Ensure the application runs smoothly and meets store listing standards.

- **[Must] SDK vs ROM major.minor compatibility (no runtime version checks required)**:
  - Align the first two segments of the SDK version (`major.minor`) with the target ROM version (`major.minor`).
  - If `SDK.major.minor` is **greater than** `ROM.major.minor`, the app is **not installable/runnable** on that ROM and will be **not visible** in the app store distribution channel for that ROM.
  - Only apps with `SDK.major.minor` **less than or equal to** `ROM.major.minor` can be installed and run on that ROM.
  - Before upgrading the SDK, confirm the target ROM coverage; if lower ROMs must be supported, do not upgrade the SDK beyond that ROM's `major.minor`.

- **[Must] Experimental API Compliance Warnings**:
  - Only APIs marked with annotations like `@ExperimentalSpatialApi` belong to the experimental category.
  - Experimental APIs will **prevent the app from being published on the PICO Store**.
  - A warning comment must be added before using or substituting such an API. The warning must clearly state:
    - This usage may block publishing on the PICO Store.
    - To enable experimental APIs, you must add the following `<meta-data>` under the `<application>` tag in `AndroidManifest.xml`:
      ```xml
      <meta-data
          android:name="pico.spatial.use_experimental_api"
          android:value="1" />
      ```
      Without explicit permission from the user, calls to these APIs should be commented out by default to prevent accidental compliance violations.

## Communication and Reporting

- After extensive build configuration changes (Phase 1) or package replacements (Phase 2), it is best to independently verify success by running `./gradlew build` before proceeding.
- Do not report the upgrade as complete after Gradle build success alone. Before finalizing, verify or explicitly report the state of:
  - Project SDK/BOM version.
  - PICO development knowledge pull result.
  - Project `.pico-env.json` `version`, `platform`, and `agentVaultWorkspace`.
  - Live knowledge MCP workspace switch and `graph_stats` result, or the exact blocker if MCP is unavailable.
  - Spatial Editor doctor/install state for the target line.
  - PICO Emulator doctor/install state for the target line, including any host-specific missing-artifact blocker.
  - Runtime target state: connected device or started matching emulator, or the exact blocker that prevented startup.
  - Final Gradle build result.
- Once the upgrade is complete, provide a summary to the user detailing:
  - [Phase 0] Which Spatial SDK versions the Maven repository offered, which target line was selected (and why — newest compatible vs user-pinned), and whether the matching PICO development knowledge was installed and recorded in `.pico-env.json`.
  - [Phase 1] Which build defects were fixed?
  - [Phase 2] Which core deprecated APIs were replaced?
  - [Phase 2.5] Whether Spatial Editor / PICO Emulator installs were refreshed before runtime validation.
  - [Phase 3] Where were runtime guards/fallbacks added (if any), and were any publishing-blocking experimental features utilized?
