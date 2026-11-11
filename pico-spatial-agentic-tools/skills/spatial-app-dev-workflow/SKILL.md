---
name: spatial-app-dev-workflow
description: >-
  Guides PICO Spatial SDK app development from a new idea or an existing project
  through design, implementation, verification, and delivery. Use when building
  an app, adding features, repairing behavior, or continuing development; covers
  direct execution and an explicitly selected managed dev workflow. NOT for
  standalone SDK migration or performance profiling; use spatial-sdk-update or
  spatial-app-performance-workflow for those tasks.
license: 'Apache-2.0'
---

# Spatial App Development Workflow

Use this skill as the development backbone for new and existing PICO Spatial SDK
Android/Kotlin apps. It coordinates the whole requested increment and loads
specialist guidance when needed. Onboarding establishes the project; UI skills
supply design and implementation knowledge; neither changes who owns the overall
request merely because it was read first.

Reading this skill does not start a managed Workflow Run. The current Agent can
carry out the development loop directly, or launch the dev workflow under the
execution choice below. Both paths aim at complete delivery, including review,
repair, and evidence. In a managed role, apply the relevant steps to that role's
assignment; do not launch another dev workflow from inside it or compete with its
current application writer.

The operating rhythm is:

`understand request and project → design the increment → implement → build → install/launch → observe → review and repair → report evidence → next increment`

This skill coordinates feature work and verification. Read only the specialist
material needed for the current stage:

- `spatial-app-onboarding` for a missing project scaffold and its initial runnable baseline; return to the current development request with project facts and evidence.
- `pico-spatial-app-designer` for product/UI design artifacts and previews when needed.
- `spatial-design-to-app` for UI structure decisions, design fidelity, implementation and validation methods. Use the material for the current stage; reading it is not an instruction to launch its full managed workflow. Keep overall app delivery here.
- `spatial-sdk-guideline` for Stage/WindowContainer, ECS, resources, interaction, physics, coordinates, and performance-budget API patterns.
- Read `../spatial-sdk-guideline/reference/experimental-apis.md` before enabling
  any API marked with an experimental opt-in annotation declared by the
  selected PICO Spatial SDK version; source opt-in and application Manifest
  runtime opt-in are one atomic change.
- Use the SDK version and dependency coordinates already declared by the project; do not hard-code or introduce a fixed Spatial SDK version unless the user explicitly asks for a migration.
- `spatial-ui-ability` / `spatial-ui-design-style` for SpatialUI Compose capabilities and visual style.
- `spatial-sdk-guideline` playbooks (e.g. `../spatial-sdk-guideline/playbooks/scene-surface-placement.md`) for wall/table/floor placement.
- `spatial-sdk-scene-builder` for code-owned scene composition and placement, including scoped guidance when integrating existing scene content.
- `spatial-accessibility` for accessible names, roles, state, focus, typed Entity actions, Attachment ownership, current-app queries, semantic audits, and published 2D/spatial actions.
- `spatial-editor` when an app requirement needs new 3D model asset generation, editor-created scene objects, primitive-geometry prototypes, fine 3D assets, a composed spatial scene, multi-object visual arrangement, materials, lighting, particles, animation, custom component declaration sync for Editor authoring, or other complex 3D visual effects that are not already available. New 3D model asset generation uses Spatial Editor by default unless the user explicitly requests not to use Spatial Editor. Resume this workflow after `spatial-editor` returns reusable authored content, integration handoff paths when packaged files are needed, component sync results, or a clear blocker.
- `pico-emulator-usage` owns every device/emulator operation reached by this workflow; return here for app-specific implementation and evidence evaluation.
- `spatial-app-performance-workflow` for real-device performance diagnosis with `pico-cli perf` and Perfetto; do not use emulator-only checks as proof of frame-rate quality.

These capability descriptions define routing boundaries, not content defaults. Delegate
only the authored content, runtime behavior, and verification work actually required
by the current request or existing project contract. Do not add asset types, effects,
relationships, or acceptance conditions merely because a routing description mentions
that the delegated skill can support them.

## When to Use

- Develop a PICO Spatial app from an idea, design, or existing project.
- Add or repair UI, behavior, data handling, SDK/ECS integration, or authored-asset integration as part of an app requirement.
- Continue an existing development task, review its results, or manage an explicitly selected dev Workflow Run.
- Return from onboarding or a specialist UI/asset task to complete app integration and verification.

## When NOT to Use

- Standalone SDK migration — use `spatial-sdk-update`.
- Standalone device performance diagnosis — use `spatial-app-performance-workflow`.
- A design-only deliverable with no application implementation requested — use `pico-spatial-app-designer`.
- An isolated device/emulator operation — use `pico-emulator-usage`.

Direct entry into a specialist skill is valid. When its scoped work becomes part
of full app delivery, use this skill's development guidance without repeating
completed work. A UI-heavy request remains a valid dev request.

## Choose How to Execute

**Direct execution** means the current Agent does the work, autonomously or with
user input, following this Skill's development guidance. **Start the dev workflow**
means launching pico-cli's built-in `spatial-app-dev-workflow`, an orchestrated
workflow provided by `pico-cli workflow`. It handles similar application
development tasks through managed planning, design, implementation and review
roles, with persisted execution state. The caller follows progress, reviews
artifacts, and handles guidance and control. Both modes aim at complete delivery;
the difference is how execution is organized, not whether review and verification
are needed. Use the [standard explanation](references/execution-choice.md#standard-explanation)
when introducing or recommending the managed mode.

Choosing managed execution does not lock the task into that mode. If it fails,
stalls, or produces poor results, the caller can stop it and take over directly
within the task's authorization; a new Run is optional. Explain the change,
preserve and inspect existing project outputs, and confirm the previous app writer
and device activity stopped before taking over. Resolve independent asset/Editor
tasks separately. Do not keep a failing Run alive merely because it was selected
earlier; honor any current explicit instruction to remain in managed execution.
See [recovery and handover](references/workflow-recovery.md#continue-directly-or-start-a-new-run).

Prefer direct execution for small, well-scoped tasks that the current Agent can
likely edit and verify in a few minutes, or when the user wants to steer the next
changes closely or explicitly asks to do it directly. Workflow setup, repeated
context loading and role handoffs add substantial Token and time overhead and can cost more than the change
itself, without improving its result. This is a recommendation, not a task-size
ban: honor an explicit request to use the workflow. Offer the managed mode for
longer tasks spanning multiple development increments when the user wants to
delegate execution and mostly provide direction, decisions, or feedback. Frequent guidance
is still compatible with a workflow. Complexity, UI changes, a review loop, or a
long-running goal alone do not select one mode over the other.

Respect an explicit choice and an established preference. “go ahead”,
“continue on your own”, absence, and `/goal` alone do not authorize a switch. Keep an existing
execution mode when intent is unclear; for a new task without an established choice,
begin directly. When switching would be useful, offer it once with its cost:
**expect substantially higher Token usage and elapsed time than direct execution**.
Do not promise
better quality, lower cost, or more reliable completion without evidence.

Before a first workflow launch, also explain that dev roles use full tool
permissions without repeated per-tool approval, subject to Host/OS controls.
Cost and limitation warnings are informational, not approval gates. When the user
explicitly requests a workflow or has already authorized it, briefly state any
relevant new warning and proceed; do not ask whether they are sure, even for a
small task. Ask about a switch only when you propose one without existing
authorization. This does not replace missing task inputs or actual tool permissions.
In user-facing introductions, recommendations, launch or switch questions, and
progress/control reports, identify this managed mode as **pico-cli's built-in
`spatial-app-dev-workflow`**. Translate the surrounding words into the user's
language and preserve that exact workflow identifier. Do not identify it only as
"the workflow" or "the dev workflow": the user may have other workflows in their
environment. A generic user mention of "workflow" selects this package only when
the context identifies it; otherwise establish which workflow they mean. Reading
the Skill still does not launch it. Describe direct execution simply as "do it directly".
The English phrases here are examples, not a keyword allowlist. Recognize equivalent
intent in any language, using context and negation, and respond in the user's language.

Load these references only when relevant:

- [Execution choice and interaction](references/execution-choice.md): ambiguous intent, launch/switch suggestions, progress updates, and resuming “the previous workflow (task)”.
- [Managed dev workflow](references/managed-workflow.md): before starting or controlling a Run; roles, input, Web UI, guidance, and responsibility for independent assets.
- [Recovery and handover](references/workflow-recovery.md): a waiting/failed Run, changing goals, switching modes, or continuing in a new Run.
- [Workflow limitations](references/workflow-limitations.md): before a first launch and when a Host/control limitation affects the current task. Disclose the relevant consequence, not a wall of caveats.

## Workflow

Follow steps 0–8 for the requested increment. In managed mode, the caller uses the
workflow reference and evaluates returned evidence; assigned roles perform their
portion of this loop. The caller must not run a second implementation or device
verification loop against the same active work.

## Required Environment and Emulator Handoffs

Apply this gate only before environment-dependent execution; purely static code reading, planning, and edits do not require it.

1. Reuse the latest successful `pico-env-doctor` result within the same Host session when the workspace, target Host, and tooling are unchanged, no environment setup, CLI/plugin/toolchain update, or Host-integration install has run since, no new failure signal exists, and the user has not requested re-verification. Emulator/device/app lifecycle operations such as emulator create/start and APK install/launch do not by themselves invalidate that complete report; on a later turn, refresh only the affected target-specific state.
2. Otherwise activate `pico-env-doctor` before running any `pico-cli` command or querying `pico-dev-knowledge` MCP. Continue only after a healthy result; if it reports a blocker, stop the dependent execution and report that blocker.
   Do not treat a top-level `FAILED` alone as proof that the app cannot build or run: read `data.checks[]` and stop only for an `error` on the path this task needs. An incomplete `project.context.doctor` is a non-blocking project-setup warning.
3. After the gate passes, keep task-specific implementation in this skill. Hand every device/emulator operation—including target discovery, emulator install/start/stop, APK install/launch, file transfer, screenshots/recordings, and device logs—to `pico-emulator-usage`, then resume here with its evidence or blocker.

## 0. Establish or Read the Project Context

Before changing code:

1. Read the project root `AGENTS.md`.
2. Inspect the current project structure, current branch/diff, and build files.
3. Identify package name, main launch activity, generated template/container type, and existing run commands from `AGENTS.md` or Gradle/manifest files.
4. If no suitable project exists, use `spatial-app-onboarding` for scaffolding and initial verification, then continue this request with its handoff. For an existing project, reuse it. Design and scaffolding can occur in either order when their prerequisites allow; do not recreate a project just to match a sequence.
5. Preserve existing conventions and behavior outside the requested change. Use the current build/runtime evidence rather than assuming an earlier handoff is still runnable.
6. If editor-authored content already exists as co-located `.bundle` and `.scenes.json` files, inspect and reuse that handoff. For related UI/container changes, read the appropriate UI guidance below; bundle presence does not decide task ownership.
   Keep both files under `app/src/main/assets/` for a Spatial app. Configure Gradle `androidResources.noCompress` to include `bundle`; the built APK still needs the check below.
7. Detect new 3D model asset generation before classifying runtime ownership. When the current task needs one or more new 3D model assets, activate `spatial-editor` first. Override this default only when the user explicitly says not to use Spatial Editor; Kotlin integration, an empty asset directory, or an eventual runtime-controlled Entity is not an implicit opt-out.
8. Classify 3D work by the deliverable: Kotlin scene implementation, Editor-authored content, or both. Keep changes to existing runtime behavior in the current app task even when they use Entity or transform APIs.
9. Use Scene Builder for the code-owned scene step and keep app build and runtime verification here. Follow [3D execution choice](../spatial-editor/references/3d-execution.md); specialist guidance is usable directly within the current task.
10. For Editor-authored content, use `spatial-editor`. Integrate the verified authored content or requested handoff. A managed delivery needs its completed Result; a direct delivery uses the actual saved or packaged outputs. Independent app work may continue while assets are produced if ownership does not conflict.
11. For mixed work, use Spatial Editor for authored content and Scene Builder for Kotlin Entity integration and placement. For bundle integration or Kotlin ECS component declaration sync, load [Editor handoffs](references/editor-handoffs.md); keep runtime registration, build and verification in this dev loop.

Handoff rule:

- Treat `AGENTS.md` as the local navigation source, not as a substitute for verification.
- If `AGENTS.md` is missing or stale, reconstruct the minimum facts from the repo and update it after the change.
- Do not restart project creation for follow-up requirements.

## 1. Work One Requirement at a Time

Convert the user's request into a small, observable increment.

Include repairs to application code or configuration that block implementing or verifying that increment, even when the defect predates the request. Scope controls limit unrelated features and rewrites; a known startup failure is necessary repair work. Resolve it and continue the original requirement.

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
- When the requirement adds or changes a user-perceivable or user-operable control, Entity, or
  Attachment, apply `spatial-accessibility` before declaring the increment complete. Publish
  semantics in app code even when the ROM interaction backend is unavailable.

### Plan UI and structural changes with specialist guidance

Compare the requested change with the current controls, Entity hierarchy and placement, layout, panel hierarchy,
attachment/lifecycle relationships, and container/window declarations. When these
change, read `spatial-design-to-app` guidance for that stage, including its
`../spatial-design-to-app/references/structure-decisions.md` for window-model decisions. Establish the
accepted visual/structural intent before implementing it; a request for a “new
window” needs its placement and lifecycle understood.

Keep app-wide scope, implementation coordination, and delivery in this dev loop.
Use UI design guidance during design, UI implementation guidance during coding,
and fidelity/visual checks during verification. A specialist handoff should return
the decisions, artifacts, code changes if assigned, evidence, and remaining gaps
needed by the caller. Do not restart a completed design or onboarding phase.

A full managed UI workflow currently includes application writing and runtime
verification. Do not start it inside the dev workflow's design stage as if it
were design-only. Use stage-specific guidance instead. A standalone UI workflow
may own its own app task; two active workflows must not write the same app or
operate its device concurrently. Separate worktrees alone do not isolate the
installed package or emulator.

## 2. Build Before Runtime Verification

After each implemented increment, run the bundled experimental API consistency
check from the installed `spatial-sdk-guideline` skill before Gradle. Resolve
the script relative to that loaded skill; do not copy it into the user's
project:

```bash
python3 <spatial-sdk-guideline-skill-dir>/scripts/check_experimental_api_opt_in.py \
  --target <project-root>
```

An active experimental source opt-in with a missing, disabled, duplicate,
conflicting, malformed, or ambiguously targeted application Manifest entry
blocks the build and delivery flow. After it passes, run the host-side checks:

```bash
./gradlew assembleDebug
```

When this increment consumes an Editor `.bundle`, check the actual APK before install with `pico-cli app bundle verify app/build/outputs/apk/debug/app-debug.apk`, after the required `pico-env-doctor` gate.

The command must find at least one `assets/*.bundle` entry and every such entry must use ZIP method 0 (stored). If it fails, fix the app Gradle packaging configuration, rebuild, and rerun the check. Do not claim bundle integration is complete from `assembleDebug` or the Gradle setting alone. Record the verified APK path and bundle count in the final result.

If the project has relevant tests, run the narrowest meaningful checks first, then broader checks when affordable:

```bash
./gradlew testDebugUnitTest
```

For device-scoped instrumentation or liveness validation, hand the project root, selected target, and requested Gradle task to `pico-emulator-usage`. It owns `connectedAndroidTest` execution and target diagnostics; resume this workflow with its test evidence or blocker.

Handle failures yourself:

1. Read the first actionable compiler/test error.
2. Fix the code or configuration.
3. Re-run the failed command.
4. Repeat until it passes or an external prerequisite blocks progress.

Do not ask the user to run Gradle, install, launch, or log commands unless an interactive/local prerequisite is outside agent control.

## 3. Hand Off Simulator or Device Preparation

After the build passes, activate `pico-emulator-usage` to inspect target state and prepare a usable simulator or device. Give it the intended project, target SDK line when relevant, and any known device/AVD preference. It owns environment/connectivity checks, target selection, and emulator lifecycle commands.

Resume this workflow only after the handoff returns an online target or a concrete blocker. Preserve the returned target identifier for every later runtime operation, and report blockers such as missing Android SDK, no device, unauthorized/offline device, or emulator setup failure without claiming runtime verification.

## 4. Hand Off Install, Launch, and Observation

After `assembleDebug` succeeds and a target is online, activate `pico-emulator-usage` again for APK installation, app launch/stop, screenshots or recordings, and device/app/crash logs. Supply the APK path, package, manifest activity when needed, acceptance check, artifact output directory, and target identifier. Do not reproduce those command sequences in this skill.

Immediately collect runtime evidence appropriate to the requirement:

- Static UI/model/state: screenshot.
- Interaction, animation, physics, timed transition, crash reproduction: short recording.
- Nonvisual behavior or failure: logcat/crash output.
- Always request a fresh Android crash-buffer observation during the launch/verification window so native or framework crashes are not missed.

Verify capture files exist before claiming visual evidence was collected.

## 5. Verification — Check Against the Requirement

For each completed increment, compare evidence against the acceptance check.

Use a concrete checklist:

- Build passed: `./gradlew assembleDebug` succeeded.
- Experimental API check passed, and any active experimental path has exactly one effective application-level `pico.spatial.use_experimental_api=1` entry.
- Install passed: APK installed to the selected target.
- Launch passed: the app process/activity started successfully.
- No immediate crash: the returned crash-buffer and app/error evidence show no new fatal exception for the package during the verification window.
- Visible/behavioral goal met: screenshot, recording, log, or test confirms the requested change.
- Regression guard: the previous onboarding baseline still works unless the requirement intentionally changed it.
- Accessibility guard: changed controls and spatial Entities expose names, roles, current state and
  supported actions. Probe and audit the current package through the ROM UiAutomator extension;
  never install a helper APK or silently enable an Accessibility Service.

Accessibility is a completion gate, not an optional follow-up. For every changed user-perceivable
or user-operable surface:

1. Apply `spatial-accessibility`. Keep affected 2D controls on native View/Compose semantics and
   validate them with Android Accessibility tooling.
2. Run `accessibility inventory` for affected Entity and Attachment owners, edit their current
   SpatialSDK declarations directly, and refresh the A11Y Contract. Do not generate 2D proxy
   declarations or use a Contract source-apply step.
3. Run `pico-cli accessibility project-audit --project <project-root> --format json` before install.
4. Resolve all source-audit errors and explicitly disposition warnings.
5. After launch, run `pico-cli accessibility runtime-audit --project <project-root> --package
<application-id> --format json` and require a non-empty, non-truncated package snapshot with
   zero errors.
6. Use the `spatial-accessibility` Skill with one `interact act` call for a natural-language runtime
   action. Accessibility has no MCP surface. Read the relevant app source and pass the stable public
   selector/action key; reuse only a node/action pair returned in the current Agent context. The CLI
   resolves when absent and retries once after an explicit stale failure. Do not add a screenshot or
   follow-up query unless the result requires it.

When the requirement is visual or interactive, do not rely only on logs. Capture a screenshot or recording and inspect it if possible. If automated visual inspection is insufficient, show the artifact path and ask the user to confirm what appears on-device.

## 6. Crash and Runtime-Failure Repair Loop

If the app crashes, freezes, fails to launch, or shows a blank/incorrect spatial scene, debug it yourself before handing back.

Crash loop:

1. Hand clean stop/launch reproduction and bounded crash/log collection to `pico-emulator-usage`, using the same explicit target identifier and package/activity facts as the first run.
2. Ask for a freshly cleared crash buffer plus filtered app/runtime errors only when an isolated log window is required. Treat clearing as a device mutation, record that older logs were discarded, and request a bounded watcher rather than an unbounded log stream for timing-dependent failures.
3. Identify the first relevant exception for the package from the returned crash-buffer evidence first, then from app/error logs if needed. Capture the exception type, process/package, top app frame, and resource/API that failed.
4. Map the failure to a likely fix:
   - missing asset or bad `asset://` path → verify asset location and Gradle `noCompress`/packaging config.
   - Spatial SDK API misuse → read the relevant `spatial-sdk-guideline` reference and correct the API/thread/container usage.
   - entity not visible/interactive → check container, transform units, lighting/IBL, `CollisionComponent`, `InteractableComponent`, and scene attachment.
   - main-thread blocking or lifecycle issue → move loading/work to the recommended async/lifecycle location.
   - launch/activity issue → verify manifest package/activity and retry explicit `--activity`.
5. Fix the application source or packaged configuration responsible for the failure. Record device-data edits, resets, and other temporary workarounds as diagnostic experiments; they do not establish that the delivered app is repaired.
6. Rebuild locally, then hand reinstall verification to `pico-emulator-usage`. Confirm the installed APK contains the source/configuration repair before changing diagnostic device data again; an in-place APK reinstall may preserve app data.
7. On that newly installed repaired build, cover the triggering persisted-data state and the missing/invalid values relevant to the diagnosis. Use an isolated test package or explicitly recoverable test data; this failure-state coverage must finish before baseline restoration.
8. Restore every diagnostic device-data mutation to the agreed baseline (the captured pre-test value, or a user-approved clean state). If restoration fails, report the exact residual state and recovery command and do **not** claim completion. Do not clear unrelated user data or add clean-data checks to every healthy increment.
9. Only after successful restoration, relaunch the newly installed repaired build and repeat the final launch/crash/log check in the restored baseline state, without relying on the workaround.
10. Resume the original increment and verify its requested behavior. Writing only SharedPreferences/device data, or restoring startup without completing the requested feature, is an incomplete result.

Do at least one self-repair attempt for actionable code/config crashes before asking the user. Stop and report clearly only when blocked by missing external prerequisites, missing private assets, nondeterministic device failure, or lack of enough error evidence.

If the correct repair requires a business decision that the project does not establish, ask for that specific decision. A defect being pre-existing is not itself a blocker.

## 7. Keep Documentation and Handoff Current

Keep Agent-readable design, progress and handover files in the project. Runtime-owned Run records remain managed by pico-cli; do not edit them as a handover mechanism.

After a requirement is verified, update project-local handoff docs when the change affects future work:

- `AGENTS.md`: current behavior, key files, build/install/run commands, verification notes, and next likely tasks.
- Any project-specific artifact/readme path for screenshots, recordings, crash dumps, or debug logs.

Do not turn `AGENTS.md` into a tutorial. Keep it a concise navigation guide for the next agent.

## 8. Final Response Format

For each requirement, report the actual result in this order:

1. **Changed**: files and behavior implemented.
2. **Verified**: exact commands that passed.
3. **Runtime evidence**: target device/emulator, launch result, screenshot/recording/log paths.
4. **Crash/log status**: whether any fatal errors were observed; if fixed, summarize root cause and fix.
5. **Blocked or remaining**: only if something could not be completed, with the exact blocker and next command/action.
6. **Next suggestions**: 1–3 state-aware follow-up options.

For progress reports, include completed deliverables, current preview/evidence links, verified effects, remaining work and decisions needed. In managed mode include the real Run identity and Web UI link when available; a node name alone is insufficient. A completed Run does not itself prove application acceptance.

Never claim success for build, install, launch, screenshot, recording, test, or crash-free status unless the command output or captured artifact confirms it.

## Per-Requirement Verification Handoff

1. Run `./gradlew assembleDebug` and any relevant local tests in this workflow.
2. Activate `pico-emulator-usage` with the APK, package/activity, target preference, acceptance check, and required screenshot/recording/log artifacts.
3. Inspect its returned runtime evidence, diagnose and fix app code here, then repeat the handoff only when a new build needs runtime verification.

For interaction, animation, or physics requirements, request recording and focused log evidence plus explicit user confirmation when visual automation is insufficient.
