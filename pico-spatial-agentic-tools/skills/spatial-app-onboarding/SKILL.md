---
name: spatial-app-onboarding
description: >-
  Use when creating or repairing the first runnable PICO Spatial SDK Android/Kotlin
  project, independently or as a caller's scaffold subtask. Covers project creation,
  configuration and initial build/install/launch evidence. NOT for full product
  delivery or post-scaffold feature work; use spatial-app-dev-workflow with the
  appropriate design and implementation guidance.
license: 'Apache-2.0'
---

# Spatial App Onboarding Skill

You are a **Spatial advisor and rapid executor**.

Your job is to get the user to a **working first Spatial project on the shortest stable path**.
Do not turn onboarding into a long interview. Start with `pico-cli project create`, keep the workflow reliable, and leave behind a project that is easy to continue.

## When to Use

- Creating a first runnable PICO Spatial project in an empty directory
- Scaffolding a new project with `pico-cli project create`
- Generic quickstart or demo without specific product features

## Required Environment and Emulator Handoffs

Apply this gate only before environment-dependent execution; purely static code reading, planning, and edits do not require it.

1. Reuse the latest successful `pico-env-doctor` result within the same Host session when the workspace, target Host, and tooling are unchanged, no environment setup, CLI/plugin/toolchain update, or Host-integration install has run since, no new failure signal exists, and the user has not requested re-verification. Emulator/device/app lifecycle operations such as emulator create/start and APK install/launch do not by themselves invalidate that complete report; on a later turn, refresh only the affected target-specific state.
2. Otherwise activate `pico-env-doctor` before running any `pico-cli` command or querying `pico-dev-knowledge` MCP. Continue only after a healthy result; if it reports a blocker, stop the dependent execution and report that blocker.
3. After the gate passes, keep project scaffolding and first-run stabilization in this skill. Hand every device/emulator operation—including target discovery, emulator install/start/stop, APK install/launch, file transfer, screenshots/recordings, and device logs—to `pico-emulator-usage`, then resume here with its evidence or blocker.

`pico-cli project create` command shape:

```bash
pico-cli project create --sdk-type spatial --name <name> --package <package> --template <planar|volumetric|stage> [--dir <path>] [--sdk <version>] [--force]
```

Do not pass the project name as a positional argument. Do not invent template
names such as `minimal` or `quickstart`. For a generic, minimal, or unspecified
quickstart, use `--template planar`.

Deliver:

- a runnable Spatial project scaffolded through `pico-cli project create`
- a project structure the user and later agents can understand quickly
- a first version that supports incremental follow-up work without unnecessary rewrites

## SpatialUI Is Mandatory (Hard Constraint)

Every project you scaffold or continue under this skill must build its 2D UI **entirely with SpatialUI**. This is non-negotiable and applies to first-run scaffolding and every later iteration.

Rules:

- **Use SpatialUI for all 2D UI.** Components come from `com.pico.spatial.ui.design.*` (and `com.pico.spatial.ui.design.windows.*` / `menu.*`). Prefer built-in SpatialUI components before writing any custom Composable.
- **Wrap the root with `PicoTheme`.** The entry `Activity`/root Composable (and each `WindowContainer`/`Stage` tree) must be wrapped in `PicoTheme { ... }` so `colorScheme`, `typography`, `LocalIndication`, and audio/haptic behavior are in place.
- **Route colors and typography through theme roles.** Use `PicoTheme.colorScheme.<role>` and `PicoTheme.typography.<role>`. Do not hardcode `Color(0x...)` or `TextStyle(fontSize = ...)`.
- **Material/Material3 is forbidden.** Do not import or keep `androidx.compose.material`, `androidx.compose.material3`, `MaterialTheme`, `Scaffold`, or any Material component/theme. If the generated template or a dependency pulls Material in, remove it (see the self-check below).
- **Defer SpatialUI design decisions to the design-style skill.** When non-trivial UI work is needed, consult the `spatial-ui-design-style` skill for token roles, component choice, and native-feeling hover/haptics/audio; consult `spatial-ui-ability` for specific spatial-capability snippets.

Generated-project SpatialUI self-check (run before declaring onboarding done):

1. Confirm the root is wrapped in `PicoTheme`.
2. Search the generated Kotlin/Gradle sources for forbidden Material usage, e.g. `androidx.compose.material`, `material3`, `MaterialTheme`. Any hit must be migrated to the SpatialUI equivalent and the Material dependency removed.
3. Rebuild after removal so the project still compiles against SpatialUI only.

## 0. Activation and Project State

This skill is reusable across projects. Do not create, delete, or depend on marker files inside the skill folder.

Routing boundary: this skill owns the first runnable scaffold and first-run stability loop. A scaffold is complete after project creation and build/install/launch evidence, or an explicit external blocker. Continue here only for scaffold repair, first launch/build/install completion, or the small changes needed for that baseline.

A model starter demo can establish this first runnable baseline by selecting a supported template and displaying the supplied model. It does not make onboarding the owner of subsequent product development; continue through `spatial-app-dev-workflow` when the request extends beyond that baseline.

A full product request belongs to `spatial-app-dev-workflow`. It may call onboarding with the resolved project constraints; existing UI/design materials do not prevent that scaffold subtask. Do not implement the full product or replace its design during onboarding. Direct scaffold-only requests are also supported.

When called by another skill or workflow, return to the actual caller with project facts, paths, configuration, build/runtime evidence and unresolved blockers. Do not select a different owner based on whether later work is UI or behavior. When called by an existing `spatial-design-to-app` flow, keep its specific scaffold receipt contract; it does not apply to all callers. For a standalone task followed by app development, read `spatial-app-dev-workflow` and reuse the created project. Design and scaffolding order depends on the available prerequisites.

At the start of each run:

1. Resolve the absolute target project supplied by the user or the calling `pico-project-setup` continuation. Inspect that target, not the session cwd, for an existing Spatial SDK project and project-specific guidance (`AGENTS.md` or `CLAUDE.md`, matched case-insensitively). Preserve a distinct resource workspace root in configure and environment handoffs: later diagnostics use `pico-cli doctor --project <project-root> --workspace-root <session-root>` and the same pair for any approved `--fix`. Doctor `--project` alone does not infer a resource association from parent directories; do not guess a parent or create a mapping.
2. If the project is empty or not yet a Spatial SDK project, run the onboarding workflow
3. If the project already has a Spatial SDK scaffold, continue from the current project state instead of restarting or overwriting it
4. If the target directory already contains project guidance, generate project files in that same directory; use the project name for `--name`, not as a child `--dir`, unless the user explicitly asks for a child directory
5. After scaffolding, classify requested 3D work by ownership:
   - route editor-authored scenes, assets, visual composition, materials, lighting, effects, or
     visual tuning through `spatial-editor`
   - hand Kotlin/code-owned Entity creation, loading, hierarchy, transforms, placement, or
     validation to `spatial-sdk-scene-builder`
   - when both are required, use each skill only for its owned portion

The Editor routing check transfers only the 3D content scope established by the user
request or an accepted upstream contract. It must not expand a generic app request
into additional authored objects, scene relationships, materials, effects, or visual
acceptance requirements.

## 1. Available Materials and Priority

Decision priority:

1. Start with `pico-cli project create`
2. Use docs and sources to verify constraints
3. Use the user prompt to refine the generated project

The `references/` folder is for **supplementary Spatial app development materials**. It should stay flexible so future iterations can add, remove, or revise files without changing the main workflow.

Current explicit entry points:

- Read `references/template-playbook.md` when API usage or implementation direction is unclear
- Read `references/template-playbook.md` again when a later turn requires migration or another branch decision
- Read `../spatial-design-to-app/references/scaffold-handoff.md` when this skill is invoked by `spatial-design-to-app` for a product-specific new project scaffold.

Tooling rule for onboarding:

- Template selection is part of the required `pico-cli project create` command.
  Keep the choice lightweight: inspect `pico-cli project create --help`, map the
  user prompt or upstream container contract to a supported template, and pass
  `--template`.
- Delegation is controlled by the active host/workflow, graph/orchestration
  plan, `.agents` roles, or explicit user request. This skill adds no extra
  delegation rule of its own.
- Before scaffolding, inspect `pico-cli project create --help` to discover the available `--template` modes and supported options.
- Always pass a supported `--template`. If the user does not specify one, choose
  `planar` for a generic/minimal quickstart, or the closest default from
  `references/template-playbook.md` when the prompt implies a specific shape.
- Pass user-provided creation facts such as `--dir`, `--name`, `--package`, `--sdk`, and `--force` when appropriate.

## 2. Workflow Rules

### 2.1 Stable shortest path

Default rhythm:

`quick judgment → scaffold MVP → route 3D work by ownership → integrate → build/install/launch → show result → continue`

Target: let the user see something working within about 3 turns whenever possible.

The shortest-path goal applies to project scaffolding, not to bypassing the owner of the requested
3D deliverable. After the runnable scaffold exists, activate `spatial-editor` only for
editor-authored content such as scenes, assets, visual composition, materials, lighting, effects,
or visual tuning. Hand Kotlin/code-owned Entity hierarchy and placement work to
`spatial-sdk-scene-builder`, then resume the enclosing app workflow after that skill completes.
When both kinds of work are present, use each skill for its owned portion.

For an editor-authored requirement, skip the editor step only when:

1. The user explicitly asks not to use Spatial Editor.
2. Runtime capability inspection shows that Spatial Editor cannot satisfy any part of the 3D content requirement.
3. Spatial Editor is actually unavailable after reasonable recovery from installation, download, startup, connection, authorization, or backend-readiness failure.

If Spatial Editor can satisfy part of the requirement, use it for that part.
Follow [3D execution choice](../spatial-editor/references/3d-execution.md) for the
Editor-owned work. For direct execution, use the documented Editor tools and
return verified content. For managed execution, call `start_editor_workflow`;
the public Workflow Service owns the Run lifecycle and Editor Domain Drivers
own installation, startup, readiness and recovery. For that path, do not call a
dynamic backend readiness tool as a preflight. An initial lifecycle status is
not failure evidence.

When the chosen path cannot complete the Editor deliverable, use its recovery
instructions and return the concrete blocker, repair attempted, and impact. Do
not substitute a different deliverable without the user's agreement.

### 2.2 Keep the core file generic

Keep domain-specific decision logic out of this main file.
When the workflow reaches a branch that depends on product shape, API usage, or implementation direction, consult the playbook in `references/` instead of embedding that knowledge here.
For first-run scaffolding, choose one supported `pico-cli project create`
template with the playbook when the user did not specify one. Do not invent
template names; current public modes are `planar`, `volumetric`, and `stage`
when advertised by `pico-cli project create --help`.

Use the playbook for:

- decision-making protocols
- API usage guidance
- migration decisions in later turns
- branch-specific questioning protocol

### 2.3 CLI-first scaffolding

Start from `pico-cli project create` and make minimal changes.
Do not invent a fresh project structure or manually choose among bundled template snapshots for first-run onboarding.

## 3. Scaffold Rules

Once the path is clear, start. Do not require an extra plan-confirmation turn.

For the generic "I have a 3D model file" quickstart request, choose the closest
supported 3D/model-friendly template from `pico-cli project create --help`, then
run `pico-cli project create` with that `--template` and keep the first pass
bundle-based, placeholder-friendly, and immediately runnable.

Execution order:

1. Choose and pass one supported `--template` value; use the user's explicit
   template/container mode, a calling workflow's resolved container contract, or
   the closest playbook default
2. Run `pico-cli project create --sdk-type spatial --dir <absolute-target-project>` with the known target/name/package options. Keep the explicit target even when it already contains guidance; omitting `--dir` targets the session cwd. After success, reuse a successful configure result from this session when it covers the same Host and project/resource roots, its selected Knowledge `major.minor` matches the SDK/BOM line in the generated Gradle files, and no new resource failure is reported. `project create` already restores the managed `.gitignore` block.
   When that evidence is unavailable, Knowledge needs alignment, or project resources need repair, run `pico-cli project configure --platform spatial --agent-tool current --yes --project <project-root> --format json` once, appending the original `--workspace-root <session-root>` when the roots differ. Configure can now select Knowledge against the generated SDK line. A deliberate Knowledge pin is preserved: if it differs from the SDK, follow `pico-env-doctor`'s alignment guidance instead of rerunning configure to change it. If `AGENT_HOST_UNRESOLVED` is returned, retry with the explicit Host id; report other failures without claiming configuration completion.
   Read `data.continuation.guidance[]` and the matching `data.continuation.skills[].path`; use `data.continuation.mcpAfterReload[]` only for any retained native entries needing Host loading/approval. For dependent MCP work, discover the global user-level `pico-spatial-editor` MCP in the Host catalog, accepting hyphen/underscore normalization and `mcp__` prefixes. Call only exact advertised names and verify the required native tools are visible before using them. Follow `data.hostActions[]` for trust or resource discovery; do not reconfigure just to make tools appear.
3. Route post-scaffold 3D work by ownership: obtain a `spatial-editor` handoff for editor-authored
   content, or hand Kotlin/code-owned Entity implementation to `spatial-sdk-scene-builder`; when
   both are required, preserve that split
4. Modify only what the MVP needs: package name, entry logic, handoff integration, required config, and required tests
5. Place user assets where the generated project and docs expect them
6. Remove sample code or assets that distract from the first MVP
7. When invoked as a `spatial-design-to-app` scaffold substep, write `<target>/.scratch/onboarding_handoff.json` before returning, record the final package and its `package_source`, and set `product_ui_implemented=false`. For that caller, product UI implementation resumes in `spatial-design-to-app`; other callers receive their own requested handoff, not a fabricated design-to-app receipt.

Package-name rules:

- If the user already provided a valid package name, use it unchanged. Explicit
  user values under `com.pico.*` or `com.picoxr.*` are allowed, but warn that
  PICO system account behavior may apply.
- When called by `spatial-design-to-app`, use the application ID from its
  feature/scaffold contract unchanged. Never derive a second package name.
- For an existing project, preserve its current `applicationId`; do not ask for
  a replacement merely because the user omitted a package name.
- For a new featureless quick demo without a package name, derive a safe
  `applicationId` once and continue without blocking. Normalize the project name
  to a lowercase Java-identifier app slug.
  For example: `OrbitDemo` becomes `com.example.orbitdemo`.
  Append the uniqueness suffix to generate
  `com.example.<app-slug>.p<8-lowercase-hex-characters>`. Persist that value in
  the generated Gradle project and reuse it for every retry or later run.
  Disclose it in the command and final handoff as a temporary demo identity.
  A later change creates a different installed application identity and can
  break the upgrade chain and continuity of app-local data. Deep links,
  provider authorities, and other package-keyed integrations can also break.
  Agent-generated package names must never use `com.pico.*` or `com.picoxr.*`.
- Ask for a package name only when identity must be resolved before proceeding:
  a formal release or migration, an explicit fixed-identity requirement, a
  detected package conflict on the target/device, or a deep link, provider
  authority, app-link, or integration contract that depends on it.
- If the user provides an invalid package name as a required identity, explain
  the validation problem and ask for a valid replacement.

Keep the first version stable, short, and understandable.
Do not over-split code for hypothetical future extensibility.

Important constraints:

- Follow generated project practices first
- Fix `androidResources.noCompress`, asset paths, ABI/build config, and similar details according to the docs and generated project
- If a later turn requires a larger architectural move, migrate using the destination template as the reference instead of improvising

## 4. Run Local Checks, Then Hand Off Runtime Operations

Run scaffolding and local build commands in this skill. Do not ask the user to run commands unless an external prerequisite cannot be handled by you. Use `pico-emulator-usage` for the device/emulator portion instead of duplicating its command flow here.

At minimum, complete these steps:

1. Pass the required environment gate, then run `pico-cli project create` or confirm the current project was already generated.
2. Check the Gradle wrapper and local build prerequisites.
3. Run the SpatialUI self-check from the hard-constraint section: confirm `PicoTheme` wrapping and remove any Material/Material3 usage before building.
4. Run `./gradlew assembleDebug` and fix build failures automatically.
5. Activate `pico-emulator-usage` with the APK path, package/activity, target preference, and first-run acceptance check. It owns target/connectivity checks, install, launch, and runtime logs or captures.
6. Resume onboarding with the returned evidence or exact blocker, then ask the user to confirm the expected result appears on-device when a launch succeeded.

If the template does not already include a suitable launch/liveness test, add a minimal `androidTest` that:

- launches the main activity
- asserts basic app liveness

When the scaffold needs connected instrumentation or liveness validation, add the minimal `androidTest` here, then hand the project root, selected target, and `connectedAndroidTest` task to `pico-emulator-usage`. Resume onboarding with its test evidence or blocker; do not execute the device-scoped task directly in this skill.

If an environment problem blocks progress, tell the user clearly.
Examples include:

- device tooling not installed or not on `PATH`
- no connected device, unauthorized device, or offline device
- Android SDK or required SDK components missing
- any other external machine/device prerequisite that prevents install, launch, or test

When blocked by environment:

- say exactly which step failed
- say exactly what prerequisite is missing or broken
- include the relevant command/error summary
- say what work already succeeded and what remains blocked
- never imply install, launch, or test succeeded when it did not

Do not stop at “code is written” or “it compiles.”

## 5. Deliver a Project-Specific `AGENTS.md`

Write `AGENTS.md` in the project root only when no project-level agent guidance file (`AGENTS.md` or `CLAUDE.md`, matched case-insensitively) already exists. If one exists, append a short, clearly marked Spatial onboarding section to that existing file instead of replacing it.

It must at least capture:

- what this project currently does
- why this structure and implementation path were chosen
- the key files and their responsibilities
- which Spatial SDK capabilities are already in use
- the SpatialUI-only UI rule for this project (all 2D UI via SpatialUI + `PicoTheme`, no Material/Material3) so later agents keep following it
- the most natural next evolution paths
- how to build, install, and run it

## 6. Continue with Progressive Suggestions

After each visible result:

1. Briefly explain what you just changed
2. Offer 1–3 next-step suggestions strongly tied to the current project
3. Let the user choose one direction
4. Continue inside the current project instead of restarting onboarding questions

Extension suggestions should be progressive and state-aware.
Base them on the current project state, the available documentation, and the playbook in `references/`.

Do not default to a fixed menu. Inspect the current project first, then suggest the next step.

## 7. When Onboarding Ends

You may end onboarding when:

- the project builds successfully
- it has been installed and launched
- all 2D UI uses SpatialUI with `PicoTheme` wrapping and no Material/Material3 remains
- runtime evidence establishes the expected first-run result, or missing observation is recorded as a blocker without claiming verification
- `AGENTS.md` has been written
- remaining product work is handed back to the caller or clearly identified for the user

When ending:

1. Report the scaffold, configuration, first-run evidence and any blocker.
2. Return to the actual caller when invoked as a subtask. Preserve its existing design and unfinished request; do not ask the user to approve a second development mode merely because scaffolding ended.
3. For standalone onboarding, deliver the result. If application development continues, activate `spatial-app-dev-workflow` for the next increment, with UI or other specialist guidance as needed.
4. Stay in onboarding only for scaffold repair or completion of the first build/install/launch loop.

Do not reclaim follow-up work merely because the user wants more changes in the same project.
