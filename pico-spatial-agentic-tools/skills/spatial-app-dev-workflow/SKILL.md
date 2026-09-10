---
name: spatial-app-dev-workflow
description: 'Runs an iterative PICO Spatial SDK feature-development workflow after spatial-app-onboarding handoff. Use for follow-up requirements in an existing Spatial app: inspect AGENTS.md, plan/implement one increment, build, install, launch in the PICO emulator/device, capture screenshots, check success criteria, watch for crashes/logcat, and self-repair until verified or clearly blocked.'
license: 'Apache-2.0'
allowed-tools: 'Bash(pico-cli *) Bash(adb *) Bash(./gradlew *) Bash(git *) Read Edit Write'
---

# Spatial App Development Workflow

Use this skill for **post-onboarding development** in an existing PICO Spatial SDK Android/Kotlin project.
It continues from the project state left by `spatial-app-onboarding`: a runnable scaffold, a project-specific `AGENTS.md`, and a baseline that should already build/install/launch.

The operating rhythm is:

`handoff review → one requirement → implement → build → install/launch simulator/device → observe → fix crashes/logs → report evidence → next requirement`

This skill coordinates feature work and verification. When a step needs deeper domain guidance, consult the specific skill/reference named below instead of inventing APIs:

- `spatial-sdk-guideline` for Stage/WindowContainer, ECS, resources, interaction, physics, coordinates, and performance-budget API patterns.
- Use the SDK version and dependency coordinates already declared by the project; do not hard-code or introduce a fixed Spatial SDK version unless the user explicitly asks for a migration.
- `spatial-ui-ability` / `spatial-ui-design-style` for SpatialUI Compose capabilities and visual style.
- `spatial-sdk-guideline` playbooks (e.g. `../spatial-sdk-guideline/playbooks/scene-surface-placement.md`) for wall/table/floor placement.
- `spatial-sdk-scene-builder` for implementing or repairing code-owned Kotlin Entity scenes, hierarchy, asset loading, bounds-aware transforms, clipping, and runtime placement evidence.
- `spatial-editor` when a requirement needs new 3D model asset generation, editor-authored scenes, entities, asset composition, materials, effects, visual inspection, custom component declaration sync, or a packaged content handoff. New 3D model asset generation uses Spatial Editor by default unless the user explicitly requests not to use Spatial Editor.
- `spatial-emulator-usage` owns every device/emulator operation reached by this workflow; return here for app-specific implementation and evidence evaluation.
- `spatial-app-performance-analysis` for real-device performance diagnosis with `pico-cli perf` and Perfetto; do not use emulator-only checks as proof of frame-rate quality.

These capability descriptions define routing boundaries, not content defaults. Delegate
only the authored content, runtime behavior, and verification work actually required
by the current request or existing project contract. Do not add asset types, effects,
relationships, or acceptance conditions merely because a routing description mentions
that the delegated skill can support them.

## Required Environment and Emulator Handoffs

Apply this gate only before environment-dependent execution; purely static code reading, planning, and edits do not require it.

1. Reuse the latest successful `pico-env-doctor` result only within the same Host session when the workspace, target Host, and tooling are unchanged, no setup/update/install/start command has run since, no new failure signal exists, and the user has not requested re-verification.
2. Otherwise activate `pico-env-doctor` before running any `pico-cli` command or querying `pico-dev-knowledge` MCP. Continue only after a healthy result; if it reports a blocker, stop the dependent execution and report that blocker.
3. After the gate passes, keep task-specific implementation in this skill. Hand every device/emulator operation—including target discovery, emulator install/start/stop, APK install/launch, file transfer, screenshots/recordings, and device logs—to `spatial-emulator-usage`, then resume here with its evidence or blocker.

## 0. Start From the Onboarding Handoff

Before changing code:

1. Read the project root `AGENTS.md`.
2. Inspect the current project structure, current branch/diff, and build files.
3. Identify package name, main launch activity, generated template/container type, and existing run commands from `AGENTS.md` or Gradle/manifest files.
4. Confirm the current user request is a follow-up feature/fix inside this project. If the directory is empty or not a Spatial SDK app, route to `spatial-app-onboarding` instead of using this workflow.
5. Preserve the existing scaffold and visible baseline unless the user explicitly asks for a migration.
6. If editor-authored content already exists as co-located `.bundle` and `.scenes.json` files, consume that handoff without reopening the editor.
7. Detect new 3D model asset generation before classifying runtime ownership. When the current task needs one or more new 3D model assets, activate `spatial-editor` first. Override this default only when the user explicitly says not to use Spatial Editor; Kotlin integration, an empty asset directory, or an eventual runtime-controlled Entity is not an implicit opt-out.
8. Classify each remaining 3D step by ownership: Kotlin/Spatial SDK Entity implementation, editor-authored content, or both. Do not infer Editor ownership merely because code-created Entities form a visible scene, and do not infer Kotlin ownership merely because Editor-authored content will later be used by the app.
9. For code-owned hierarchy, loading, transforms, arrangement, or placement, activate `spatial-sdk-scene-builder` and keep this workflow as the enclosing build/install/launch/verification loop.
10. For editor-authored scene or asset content, activate `spatial-editor` and resume app implementation only after its managed Controller returns a completed handoff or structured blocker.
11. For mixed work, use Spatial Editor for authored content and Scene Builder for Kotlin Entity integration and placement.

Handoff rule:

- Treat `AGENTS.md` as the local navigation source, not as a substitute for verification.
- If `AGENTS.md` is missing or stale, reconstruct the minimum facts from the repo and update it after the change.
- Do not restart project creation for follow-up requirements.

## 1. Work One Requirement at a Time

Convert the user's request into a small, observable increment.

For each requirement, write down internally:

- **Goal**: what user-visible behavior should change.
- **Touch points**: files/components likely affected.
- **Acceptance check**: what proves the goal works in the simulator/device.
- **Risk**: likely crash/build/runtime failure modes.

Ask at most one clarifying question only when the answer changes the architecture or visible behavior. Otherwise choose the smallest stable path, state the assumption, and proceed.

Prefer incremental edits over rewrites:

- Keep generated project conventions.
- Keep package names, activity names, asset paths, Gradle config, and template container shape stable unless the requirement demands otherwise.
- Use App/ECS for runtime state, behavior, interaction, sensing, simulation, and high-frequency updates. Do not treat runtime behavior as a reason to move the underlying supported 3D content-production work out of Spatial Editor.
- When Spatial Editor supports only part of the requirement, integrate its authored output and implement only the remaining unsupported or runtime portions in App/ECS.
- Use `spatial-sdk-guideline` references before writing nontrivial ECS, resource loading, interaction, physics, animation, or coordinate conversion code.
- Keep snippets idiomatic for the existing Kotlin/Compose style.

## 2. Build Before Runtime Verification

After each implemented increment, run host-side checks before launching:

```bash
./gradlew assembleDebug
```

If the project has relevant tests, run the narrowest meaningful checks first, then broader checks when affordable:

```bash
./gradlew testDebugUnitTest
```

For device-scoped instrumentation or liveness validation, hand the project root, selected target, and requested Gradle task to `spatial-emulator-usage`. It owns `connectedAndroidTest` execution and target diagnostics; resume this workflow with its test evidence or blocker.

Handle failures yourself:

1. Read the first actionable compiler/test error.
2. Fix the code or configuration.
3. Re-run the failed command.
4. Repeat until it passes or an external prerequisite blocks progress.

Do not ask the user to run Gradle, install, launch, or log commands unless an interactive/local prerequisite is outside agent control.

## 3. Hand Off Simulator or Device Preparation

After the build passes, activate `spatial-emulator-usage` to inspect target state and prepare a usable simulator or device. Give it the intended project, target SDK line when relevant, and any known device/AVD preference. It owns environment/connectivity checks, target selection, and emulator lifecycle commands.

Resume this workflow only after the handoff returns an online target or a concrete blocker. Preserve the returned target identifier for every later runtime operation, and report blockers such as missing Android SDK, no device, unauthorized/offline device, or emulator setup failure without claiming runtime verification.

## 4. Hand Off Install, Launch, and Observation

After `assembleDebug` succeeds and a target is online, activate `spatial-emulator-usage` again for APK installation, app launch/stop, screenshots or recordings, and device/app/crash logs. Supply the APK path, package, manifest activity when needed, acceptance check, artifact output directory, and target identifier. Do not reproduce those command sequences in this skill.

Immediately collect runtime evidence appropriate to the requirement:

- Static UI/model/state: screenshot.
- Interaction, animation, physics, timed transition, crash reproduction: screenshot plus logs for now.
- Nonvisual behavior or failure: logcat/crash output.
- Always request a fresh Android crash-buffer observation during the launch/verification window so native or framework crashes are not missed.
- Clearing logcat is a device mutation that discards older logs. Request it only when the verification needs an isolated fresh window, and record that the older logs were intentionally discarded.
- Tell the handoff not to use 2D screen-coordinate taps as proof for volumetric/spatial UI or Gaming-state transitions.

Verify capture files exist before claiming visual evidence was collected.

## 5. Check Against the Requirement, Not Just “App Launched”

For each completed increment, compare evidence against the acceptance check.

Use a concrete checklist:

- Build passed: `./gradlew assembleDebug` succeeded.
- Install passed: APK installed to the selected target.
- Launch passed: the app process/activity started successfully.
- No immediate crash: the returned crash-buffer and app/error evidence show no new fatal exception for the package during the verification window.
- Visible/behavioral goal met: screenshot, log, or test confirms the requested change.
- Regression guard: the previous onboarding baseline still works unless the requirement intentionally changed it.

When the requirement is visual or interactive, do not rely only on logs. Capture a screenshot and inspect it if possible. If automated visual inspection is insufficient, show the artifact path and ask the user to confirm what appears on-device. For volumetric/spatial containers, say explicitly that adb-backed screenshot and 2D tap automation may both be insufficient without simulator-side support.

## 6. Crash and Runtime-Failure Repair Loop

If the app crashes, freezes, fails to launch, or shows a blank/incorrect spatial scene, debug it yourself before handing back.

Crash loop:

1. Hand clean stop/launch reproduction and bounded crash/log collection to `spatial-emulator-usage`, using the same explicit target identifier and package/activity facts as the first run.
2. Ask for a freshly cleared crash buffer plus filtered app/runtime errors only when an isolated log window is required. Treat clearing as a device mutation, record that older logs were discarded, and request a bounded watcher rather than an unbounded log stream for timing-dependent failures.
3. Identify the first relevant exception for the package from the returned crash-buffer evidence first, then from app/error logs if needed. Capture the exception type, process/package, top app frame, and resource/API that failed.
4. Map the failure to a likely fix:
   - missing asset or bad `asset://` path → verify asset location and Gradle `noCompress`/packaging config.
   - Spatial SDK API misuse → read the relevant `spatial-sdk-guideline` reference and correct the API/thread/container usage.
   - entity not visible/interactive → check container, transform units, lighting/IBL, `CollisionComponent`, `InteractableComponent`, and scene attachment.
   - main-thread blocking or lifecycle issue → move loading/work to the recommended async/lifecycle location.
   - launch/activity issue → verify manifest package/activity and retry explicit `--activity`.
5. Apply the fix.
6. Rebuild locally, then hand reinstall/relaunch/log verification back to `spatial-emulator-usage`.

Do at least one self-repair attempt for actionable code/config crashes before asking the user. Stop and report clearly only when blocked by missing external prerequisites, missing private assets, nondeterministic device failure, or lack of enough error evidence.

## 7. Keep Documentation and Handoff Current

After a requirement is verified, update project-local handoff docs when the change affects future work:

- `AGENTS.md`: current behavior, key files, build/install/run commands, verification notes, and next likely tasks.
- Any project-specific artifact/readme path for screenshots, crash dumps, or debug logs.

Do not turn `AGENTS.md` into a tutorial. Keep it a concise navigation guide for the next agent.

## 8. Final Response Format

For each requirement, report the actual result in this order:

1. **Changed**: files and behavior implemented.
2. **Verified**: exact commands that passed.
3. **Runtime evidence**: target device/emulator, launch result, screenshot/log paths.
4. **Crash/log status**: whether any fatal errors were observed; if fixed, summarize root cause and fix.
5. **Blocked or remaining**: only if something could not be completed, with the exact blocker and next command/action.
6. **Next suggestions**: 1–3 state-aware follow-up options.

Never claim success for build, install, launch, screenshot, test, or crash-free status unless the command output or captured artifact confirms it.

## Per-Requirement Verification Handoff

1. Run `./gradlew assembleDebug` and any relevant local tests in this workflow.
2. Activate `spatial-emulator-usage` with the APK, package/activity, target preference, acceptance check, and required screenshot/recording/log artifacts.
3. Inspect its returned runtime evidence, diagnose and fix app code here, then repeat the handoff only when a new build needs runtime verification.

For interaction, animation, or physics requirements, request recording and focused log evidence plus explicit user confirmation when visual automation is insufficient.
