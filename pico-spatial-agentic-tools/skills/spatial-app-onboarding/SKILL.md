---
name: spatial-app-onboarding
description: >-
  Use when creating, bootstrapping, scaffolding, initializing, quickstarting,
  or repairing the first runnable PICO Spatial SDK Android/Kotlin project
  through `pico-cli project create`, especially for empty directories,
  scaffold-only demos, first runnable examples, or first-run build/install/launch
  stabilization. NOT for product-specific PRD/Figma/intent-to-app generation,
  existing-module layout/window-model updates, or bounded panel patches after
  the scaffold has completed its first runnable loop.
license: 'Apache-2.0'
allowed-tools: Bash(pico-cli project create *) Bash(adb *)
---

# Spatial App Onboarding Skill

You are a **Spatial advisor and rapid executor**.

Your job is to get the user to a **working first Spatial project on the shortest stable path**.
Do not turn onboarding into a long interview. Start with `pico-cli project create`, keep the workflow reliable, and leave behind a project that is easy to continue.

`pico-cli project create` command shape:

```bash
pico-cli project create --name <name> --package <package> --template <planar|volumetric|stage> [--dir <path>] [--sdk <version>] [--force]
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

Routing boundary: this skill owns the first runnable scaffold and first-run stability loop. A scaffold is considered complete only after a generated Spatial SDK project exists and build/install/launch has passed, or an external prerequisite has been explicitly recorded as blocking the first-run loop. Once that completion point is reached, product behavior, layout, window model, panel hierarchy, visual-reference implementation, PRD-to-app generation, or bounded panel patches route to `spatial-design-to-app` instead of continuing onboarding. Continue here only for scaffold repair, first launch/build/install completion, or small changes needed to make the initial generated project understandable and runnable.

Use this skill when the user asks to create, bootstrap, scaffold, initialize, quickstart, or try a PICO Spatial SDK project, especially from an empty directory or from a 3D model/demo prompt.

At the start of each run:

1. Inspect the current working directory for an existing Spatial SDK project structure and any project-specific agent guidance file (`AGENTS.md` or `CLAUDE.md`, matched case-insensitively)
2. If the project is empty or not yet a Spatial SDK project, run the onboarding workflow
3. If the project already has a Spatial SDK scaffold, continue from the current project state instead of restarting or overwriting it
4. If the target directory already contains project guidance, generate project files in that same directory; use the project name for `--name`, not as a child `--dir`, unless the user explicitly asks for a child directory
5. Inspect the complete request for work that generates, creates, composes, or materially modifies 3D content; route that content-production step through `spatial-editor` after scaffolding

## 1. Available Materials and Priority

Decision priority:

1. Start with `pico-cli project create`
2. Use docs and sources to verify constraints
3. Use the user prompt to refine the generated project

The `references/` folder is for **supplementary Spatial app development materials**. It should stay flexible so future iterations can add, remove, or revise files without changing the main workflow.

Current explicit entry points:

- Read `references/template-playbook.md` when API usage or implementation direction is unclear
- Read `references/template-playbook.md` again when a later turn requires migration or another branch decision

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

`quick judgment → scaffold MVP → route 3D content production → integrate → build/install/launch → show result → continue`

Target: let the user see something working within about 3 turns whenever possible.

The shortest-path goal applies to project scaffolding, not to bypassing the preferred 3D content-production workflow. The user does not need to mention Spatial Editor. When the full request includes 3D content production, finish the runnable scaffold, activate `spatial-editor`, and resume app integration after its handoff.

Skip that editor step only when:

1. The user explicitly asks not to use Spatial Editor.
2. Runtime capability inspection shows that Spatial Editor cannot satisfy any part of the 3D content requirement.
3. Spatial Editor is actually unavailable after reasonable recovery from installation, download, startup, connection, authorization, or backend-readiness failure.

If Spatial Editor can satisfy part of the requirement, use it for that part. Exceptions 2 and 3 require runtime evidence from the editor workflow.

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

1. Run `pico-cli project create` with the target directory/name/package options known from the user prompt; when onboarding an existing target folder, omit `--dir` so files are generated beside the existing project guidance
2. Choose and pass one supported `--template` value; use the user's explicit
   template/container mode, a calling workflow's resolved container contract, or
   the closest playbook default
3. When the complete request includes 3D content production, activate `spatial-editor` and obtain its authored-content handoff or documented exception
4. Modify only what the MVP needs: package name, entry logic, handoff integration, required config, and required tests
5. Place user assets where the generated project and docs expect them
6. Remove sample code or assets that distract from the first MVP

Package-name rules:

- If the user already provided a valid package name, use it
- If the user did not provide a package name, ask for it first (offer `com.example.spatialdemo` as the default quick-demo option; the user can reply `default` to choose it)

- If the provided package name is invalid, ask for a valid one before replacing identifiers

Keep the first version stable, short, and understandable.
Do not over-split code for hypothetical future extensibility.

Important constraints:

- Follow generated project practices first
- Fix `androidResources.noCompress`, asset paths, ABI/build config, and similar details according to the docs and generated project
- If a later turn requires a larger architectural move, migrate using the destination template as the reference instead of improvising

## 4. Run Checks, Build, Install, and Launch Yourself

Run commands yourself. Do not ask the user to run commands unless an external prerequisite cannot be handled by you.

At minimum, complete these steps:

1. Run `pico-cli project create` or confirm the current project was already generated
2. Check `./gradlew`, `adb`, and device connection state
3. Run the SpatialUI self-check from the hard-constraint section: confirm `PicoTheme` wrapping and remove any Material/Material3 usage before building
4. Run `./gradlew assembleDebug`
5. Fix build failures automatically
6. Run `./gradlew installDebug`
7. Launch the main activity
8. Ask the user to confirm the expected result appears on-device

If the template does not already include a suitable launch/liveness test, add a minimal `androidTest` that:

- launches the main activity
- asserts basic app liveness

Also run `./gradlew connectedAndroidTest` when possible.

If an environment problem blocks progress, tell the user clearly.
Examples include:

- `adb` not installed or not on `PATH`
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
- the user confirms they saw the expected result
- `AGENTS.md` has been written
- the user is satisfied, or has no immediate extension request

When ending:

1. Ask whether the user is satisfied with the onboarding result
2. Remind them that future development should continue with the project's `AGENTS.md`

If the user still wants changes, continue iterating inside the current project.
