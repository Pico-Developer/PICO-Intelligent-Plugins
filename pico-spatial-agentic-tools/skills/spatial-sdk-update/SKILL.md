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

## When to Use

- Upgrading an existing project to a newer PICO Spatial SDK version
- Migrating deprecated Spatial API calls after an SDK bump
- Resolving SDK version compatibility issues

## When NOT to Use

- Creating a new project — use `spatial-app-onboarding`
- Porting a 2D Android app to Spatial — use `porting-android-app`
- Day-to-day feature work — use `spatial-app-dev-workflow`

## Required Environment and Emulator Handoffs

Apply this gate only before environment-dependent execution; purely static code reading, planning, and edits do not require it.

1. Reuse the latest successful `pico-env-doctor` result within the same Host session when the workspace, target Host, and tooling are unchanged, no environment setup, CLI/plugin/toolchain update, or Host-integration install has run since, no new failure signal exists, and the user has not requested re-verification. Emulator/device/app lifecycle operations such as emulator create/start and APK install/launch do not by themselves invalidate that complete report; on a later turn, refresh only the affected target-specific state.
2. Otherwise activate `pico-env-doctor` before running any `pico-cli` command or querying `pico-dev-knowledge` MCP. Continue only after a healthy result; if it reports a blocker, stop the dependent execution and report that blocker.
3. After the gate passes, keep SDK selection and migration in this skill. Hand every device/emulator operation—including target discovery, emulator install/start/stop, APK install/launch, file transfer, screenshots/recordings, and device logs—to `pico-emulator-usage`, then resume here with its evidence or blocker.

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
    pico-cli knowledge pull <major.minor>
    pico-cli knowledge use <major.minor> --project <resourceRoot>
    ```
  - Example:
    ```bash
    pico-cli knowledge pull 0.13
    pico-cli knowledge use 0.13 --project /path/to/project
    ```
  - Resolve the selection owner with `pico-cli project detect --project <target-dir> --format json`, preserving `--workspace-root <session-root>` when distinct. Pass the directory containing its `knowledge.filePath` as `<resourceRoot>` to `knowledge use --project`. The project must already be configured by `pico-cli project configure`; otherwise the use command fails before writing and names that command. Without `--project`, the use command targets the configured project that contains the current directory, or the user level outside one.
  - The pull command downloads or refreshes the knowledge data without changing environment selection. The use command reads the existing `.pico-env.json` `platform`, selects that platform's installed workspace, and updates only `version` plus `agentVaultWorkspace`. It preserves `platform` and unrelated keys and pins the version, so later setup, project configure, and `doctor --fix` runs keep it. A failed selection preserves the previous record.
  - Use `--source auto` by default. Pass `--source global` or `--source cn` only when the user or environment explicitly requires one of those sources.
- **[Must] Query the selected version through the shared live MCP protocol**:
  - Use the general plugin's `knowledge-query` Skill for each migration lookup. Pass the engineering
    `--project <target-dir>` and distinct resource `--workspace-root <session-root>`, along with the
    selected target SDK version and the API question.
  - Follow its usable-baseline, live activation, query, and restore protocol. After `knowledge use`,
    the new disk selection is the restore baseline; a successful CLI selection does not switch an
    already-connected MCP. Do not maintain a separate switch/stats sequence here or treat
    `graph_stats` as proof of the live workspace. Use the shared fallback if activation is unavailable.

## Phase 1: Build & Config

Goal: Quickly fill core gaps, resolve the most urgent build and compatibility issues, and ensure the project can compile under the new PICO ecosystem.

- **[Must] Upgrade Gradle, AGP, and Kotlin (keep versions consistent)**: PICO OS 6 and newer Spatial SDK versions generally require a modern Android toolchain. If Gradle sync fails, upgrade the project to a compatible combo (e.g., **AGP 8.x** with the matching Gradle wrapper), and set **Kotlin** to a version compatible with your AGP + Android Studio (do not guess a major jump). Ensure the **Compose Compiler** configuration matches the Kotlin version (use the official Compose–Kotlin compatibility table).
  - **SDK levels**: Keep `compileSdk = 35` and typically `targetSdk = 35` for PICO OS 6 projects. Note: upgrading `targetSdk` to 35 may introduce standard Android behavioral changes (e.g., edge-to-edge enforcement or stricter foreground service permissions); address these if the user encounters related issues.
  - **minSdk**: Do **not** blindly force `minSdk = 35`. Keep it aligned with the project baseline / template / business constraints, and only raise it if the user explicitly targets that requirement.
- **[Must] Resolve Compose dependency conflicts when present**: After upgrading the Spatial SDK BOM, run Gradle sync or dependency resolution. Add Compose exclusions (e.g., `androidx.compose.ui:ui`, `ui-graphics`, `ui-text`, `androidx.compose.foundation:foundation`) only when dependency-resolution evidence identifies a concrete conflict with SpatialUI's bundled Compose artifacts. Do not add exclusions as an unconditional step; include only the conflicting modules identified by the evidence.
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
  - If "class not found" or "unresolved reference" errors occur, follow the Investigation Order defined in `spatial-sdk-guideline`: check project evidence and deprecation messages first, then use the general `knowledge-query` Skill for the replacement API, then inspect bundled references and examples.
  - Only fall back to `source.jar` or dependency-cache `grep` when the preceding steps cannot resolve the replacement. Do not start with `source.jar` when knowledge graph context, skill references, and project evidence are available.
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
    pico-cli editor install --editor-version <major.minor> --yes
    ```
  - Activate `pico-emulator-usage` with the selected SDK `major.minor` line. The handoff must require `pico-cli emulator install --version <major.minor>` and pass `--version <major.minor>` to every create/start command. It owns emulator doctor/install and returns the usable bundle/AVD/version or the exact host/artifact blocker. Do not duplicate those commands here.
  - Emulator source selection is automatic. Do not request or pass a source override in the handoff.
  - If a tool install fails because no artifact matches the current host, report the returned fallback state. Do not claim runtime validation is fully covered unless a usable matching Editor/Emulator is actually available.
  - If a tool install or doctor command is unavailable in the user's installed pico-cli, report that exact blocker before claiming runtime validation is possible.
- **[Must] Start a matching emulator when runtime validation needs one**:
  - Continue the `pico-emulator-usage` handoff to inspect online targets. When it needs an AVD, require it to select from `pico-cli emulator list --managed-only --format json`; never use `emulator doctor` as the AVD selector. Before resuming migration, require the handoff result to normalize the returned `bundleVersion` and selected SDK to `major.minor`, confirm those version lines match, and identify the managed AVD it created or started.
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
  - Read
    [`../spatial-sdk-guideline/reference/experimental-apis.md`](../spatial-sdk-guideline/reference/experimental-apis.md)
    before migrating to an API marked with an experimental opt-in annotation
    declared by the selected PICO Spatial SDK version.
  - Experimental APIs will **prevent the app from being published on the PICO Store**.
  - Without explicit user acceptance of that risk, do not leave the
    experimental path active. Prefer a stable API or keep the proposed call
    inactive.
  - Once accepted, apply the narrow Kotlin opt-in and the application-level
    `pico.spatial.use_experimental_api=1` Manifest entry atomically. Run the
    bundled experimental API checker before the build; a missing, disabled,
    duplicate, conflicting, malformed, or ambiguously targeted entry blocks
    delivery.

## Communication and Reporting

- After extensive build configuration changes (Phase 1) or package replacements (Phase 2), it is best to independently verify success by running `./gradlew build` before proceeding.
- Do not report the upgrade as complete after Gradle build success alone. Before finalizing, verify or explicitly report the state of:
  - Project SDK/BOM version.
  - PICO development knowledge pull and use results.
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
