---
name: pico-project-setup
description: >-
  Entry point for PICO project setup and creating or extending Spatial SDK and Unity + PICO XR apps.
  Also routes standalone 3D asset/editor work, SpatialUI or SDK advice, porting, and
  device/emulator/toolchain questions without configuring a project. Detects the platform,
  installs project Skills when development requires them, and continues the matching Skill.
license: 'Apache-2.0'
allowed-tools: 'Bash(pico-cli project detect *) Bash(pico-cli project configure *) Bash(pico-cli plugin update*) Bash(mkdir *) Read'
---

# PICO Project Setup

`pico-cli setup` runs once per user and installs this general plugin with the global user-level
`pico-dev-knowledge`, `pico-spatial-editor`, and `unity-mcp` MCP entries. Once loaded and approved by
the Host, they can be discovered without project configure; live operation tools still require their
backend prerequisites. Platform Skills are installed per project by `pico-cli project configure`.
This skill routes PICO requests to Spatial development, Unity development, or capabilities without
configuring a project.

Do not run `pico-cli setup` yourself from this project-configuration Skill. User-level setup belongs to `pico-env-doctor` and requires an authorized setup task; project configuration does not replace it. Do not hand-edit
`.pico-env.json`, Host Skill directories, or Host MCP files.

## When to Use

- Creating a new PICO Spatial or Unity project from scratch
- Configuring an existing project for AI-assisted development
- First-time platform plugin installation into a project
- Switching between Spatial and Unity platform configurations

## When NOT to Use

- Environment health checks without project context — use `pico-env-doctor`
- Generic CLI command discovery — use `pico-cli`
- SDK version upgrades in an existing project — use the platform plugin SDK update skill
- Day-to-day feature development — use the platform plugin's workflow skills

## 1. Route the request

Classify the original request first — do not jump straight to detection.

### Route A — Develop a Spatial SDK app (build/extend a Kotlin Spatial project)

Creating a PICO Spatial app, adding scenes/ECS code, SpatialML pipelines, or integrating into an
existing Kotlin Spatial project. Resolve the roots in sections 2–3, then detect (4) → decide (5) →
configure spatial (6) → continue (7), and hand off complete app development to the
configured Spatial plugin's `spatial-app-dev-workflow` skill. A scaffold-only request
belongs to that plugin's `spatial-app-onboarding` skill. Preserve the original request and any scoped caller when returning from setup;
configuring the platform does not itself start a managed Workflow Run.

### Route B — Develop a Unity + PICO XR app

Creating a Unity project with PICO XR, Building Blocks, Spatial Adapter, or Unity SpatialML.
Continue with detect → decide → configure unity, then hand off to `pico-unity-init`.

### Route C — Use PICO capabilities without configuring a project

For a general-only installation, default to the installed `knowledge-query` Skill and global
`pico-dev-knowledge` MCP for SDK/API, SpatialUI design, porting, and integration advice. Use the
general `pico-cli` Skill for command discovery, `pico-env-doctor` for diagnosis,
`pico-emulator-usage` for emulator/device operations, `pico-cli-screenshot` for still evidence,
and `capture-camera` for camera movement/recording. These shared Skills need no platform plugin.

Use an already installed platform Skill when it fits the question, such as `spatial-ui-design-style`
or `spatial-ui-ability`. Otherwise stay with the general fallbacks above.

For 3D asset generation, editor workflows, or scene inspection, discover the global
`pico-spatial-editor` native tools as described in section 7. If the advertised schema supports
`workspace_root`, pass the user's controlled asset workspace explicitly to work without an SDK project;
verify the actual result rather than treating server discovery as Editor readiness.

For a direct 3D generation task, prefer the installed `pico-sgs-cli` for generation, query, or
download. Consider Editor generation only when the managed CLI is explicitly unavailable
before generation starts, with no existing task or unresolved submission. Auth, quota, cloud failure,
and temporary contention are not fallback conditions. If the request includes Editor import or validation, use the
available Editor tools with the original downloaded asset and check the actual
result. Using both services does not by itself require a Run.

When the user selects managed execution or needs its asset-supply or acceptance
contract, use `start_3d_generation_workflow` with the published
`spatialcraft.spatial-3d-generation-input/v2` Schema and `assetSupply`.
Select `backendPreference: "editor"` for Editor delivery or `"codegen"` for a
Spatial SDK/Kotlin scene. Use `fallbackPolicy: "forbid"` for managed Codegen or
when the user requires SGS. Preserve model subjects
and the user-authorized generation budget. The Workflow Driver submits SGS tasks;
use its current task ID if one exists. Codegen consumes the
original GLB without Editor; reuse an existing downloaded Source through the
owner/request/digest contract in `assetSupply.inputs[].existingSource`.

For an existing-model import, preserve the original file, task ID, and digest and inspect the
available asset input contract. If no reuse entry point exists or Editor does not support the
format, report the exact limitation. Do not regenerate the model or silently substitute a converted asset. If the requested managed path lacks v2 or `assetSupply`, report the missing field and recover tool discovery as described in section 7. Never treat an empty-asset
workflow as an equivalent entry point.

Do not scaffold a project and do not run `pico-cli project configure` for Route C. Do not install a platform plugin just to answer a question.
Read-only project context does not authorize configure. If the user later authorizes project creation
or implementation, reclassify that new task as Route A/B before following detect/configure.
If a required global MCP tool is absent, use the general fallbacks and report the missing capability;
follow section 7's Host-specific discovery/reconnect rules, not an automatic session restart.

### Out of scope

Generic Android apps, non-PICO OpenXR C++ projects, pure backend work, or anything without a PICO
intent: this Skill's supported scope is PICO Spatial SDK projects, PICO Unity projects, and the
global PICO MCP capabilities. State the boundary plainly and offer the two real options —
create a new PICO project (routes A/B) or integrate the PICO SDK into the existing app (porting
guidance) — without silently configuring the project as `spatial`.

## 2. Session workspace root

Keep `--project <target-dir>` for engineering evidence. If the project is nested under the session
directory, pass `--workspace-root <session-root>` so the Host discovers its resources there.
Carry that explicit pair through detect, configure, and later diagnostics:
`pico-cli doctor --project <target-dir> --workspace-root <session-root>` (and any approved `--fix`).
A standalone doctor `--project` does not infer a resource association from parent directories;
do not add a local mapping or guess a parent.

Omit `--workspace-root` when the roots match. Also omit it when the session directory is outside the
target's ancestors or is a reserved root (user home, filesystem root, or pico-cli state directory):
CLI rejects those resource roots. Configure the explicit target instead, continue through returned
files, and explain that native project resource discovery requires opening that target in the Host.

## 3. Resolve the target project directory

Before any detect/configure call, fix one absolute target directory and pass it to every
`project` command with `--project <dir>`. Otherwise commands inspect the session directory by
searching upward, and a session opened at A can accidentally configure A when the user asked for
B.

Default: the directory where the Agent session was opened. Otherwise use the directory the user
named (an existing project to configure, or the directory where they want a new project
created). Resolve it to an absolute path. Keep the same value in detect, configure, and any
later `project create --dir`.

`project configure` requires an existing directory. If the user authorized creating a new project
at a missing target, create only that directory (`mkdir -p "<target-dir>"`) before detect/configure.
For an existing-project request, report a missing target as a path error; do not create it silently.

## 4. Detect

```bash
pico-cli project detect --project <target-dir> --format json [--workspace-root <session-root>]
```

Read `data` from the Tool Result:

| Field                           | Meaning                                                                                    |
| ------------------------------- | ------------------------------------------------------------------------------------------ |
| `userEnvironment.setupComplete` | `false`: the user has not run `pico-cli setup`; ask them to run it, then stop.             |
| `projectRoot`                   | `null`: the working directory is the user home or a pico-cli state directory.              |
| `workspaceRoot`, `warning`      | The session root passed with `--workspace-root`, and the mismatch warning when it differs. |
| `platform`, `evidence`          | Platform the project files declare (`spatial`, `unity`, `ambiguous`, or `unknown`).        |
| `ambiguousEvidence`             | With `ambiguous`: the files at the project root that declare each platform.                |
| `configured.platforms`          | Platforms already configured in this project; empty when unconfigured.                     |
| `configured.mixed`              | `true`: Hosts disagree after a failed switch; configure again to repair.                   |
| `configured.hosts[].plugins[]`  | `updateAvailable: true` means the installed platform plugin is behind.                     |
| `legacy.userPlatformPlugins`    | Platform plugins left at the user level by an older setup; `pico-cli setup` migrates them. |

When `projectRoot` is `null`: the resolved target directory is a user home or pico-cli state
directory. If the user already named a concrete project directory elsewhere in the conversation,
pass that absolute path as `--project` and re-run detect — there is no need to ask them to open a
new session just to re-run detect/configure. Only when no target directory can be determined at
all, ask the user to choose a target directory. Use the global native MCP discovery rules in
section 7 for dependent platform operations. Do not force a reload for file/CLI-only steps.

## 5. Decide the platform

1. `platform` is `spatial` or `unity`: use it. The platform comes from concrete project evidence
   (`evidence`), not from the vocabulary used in the request.
   - `ambiguous`: the project root declares both. Reuse `configured.platforms` only when it contains
     exactly one platform; otherwise show `ambiguousEvidence` and ask which SDK this task targets.
2. `platform` is `unknown`: there is no PICO SDK evidence in the target directory. Infer the SDK
   only from **explicit PICO intent** in the request:
   - Explicit PICO Spatial intent (PICO Spatial SDK, SpatialUI on PICO devices, PICO ECS) →
     `spatial`. A generic "create a PICO app" request does not identify this SDK.
   - Explicit Unity XR intent (Unity project, C#, URP, Building Blocks, Spatial Adapter) →
     `unity`.
   - Generic Android/Kotlin/Gradle or ECS project mentions, with no PICO evidence in the
     directory and no explicit PICO intent in the request: this Skill's supported scope is
     **PICO Spatial SDK (Android/Kotlin) projects and PICO Unity projects only**. Tell the user
     that a generic Android/Kotlin/ECS project is not automatically a PICO project, then offer
     the two real options: create a new PICO project here (`project create`, later in this flow),
     or integrate the PICO Spatial SDK into their existing app (the Spatial SDK onboarding flow).
     Do not silently configure a generic app as `spatial`.
   - Neither the project files nor the request name an SDK, for example "create a PICO app": ask
     the user which SDK to use, PICO Spatial SDK (Android/Kotlin) or Unity, and wait for the
     answer. Do not default to either platform.
3. If `configured.platforms` contains a different platform, confirm the correction before configure:
   it replaces the old platform plugin across recorded Hosts, including unselected Hosts.
   When the files declare a platform, correct stale plugin records to that declared platform;
   never change the engineering project's SDK to match stale records. When the files declare
   nothing, use the platform chosen in step 2. Do not switch to a platform the files exclude.

## 6. Configure

```bash
pico-cli project configure --platform <spatial|unity> --project <target-dir> --agent-tool current --yes --format json [--workspace-root <session-root>]
```

Use the target and resource-root rules in sections 2–3. If this configuration request explicitly
includes a knowledge version, discover and pass `--knowledge-version <version>`; omission preserves
an existing pin. A knowledge-version-only change belongs to `pico-cli`'s persistent selection procedure
and does not require reconfiguring the project.

Pass `--yes` only after any switch in section 5.3 was confirmed. Running configure again for the same
platform is safe; it refreshes the project, keeps a knowledge version pinned with
`pico-cli knowledge use`, and returns the continuation.

Branch on the top-level `tool_status` of the Tool Result (`SUCCESS`, `PARTIAL`, or `FAILED`), not
on the lowercase `data.status`. On `tool_status: FAILED`, branch on `errors[0].code`:

| Code                          | Action                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------- |
| `AGENT_HOST_UNRESOLVED`       | Ask the user which Agent Host they are using, then retry with `--agent-tool <host-id>`.     |
| `AGENT_HOST_NOT_SET_UP`       | This Host lacks the general plugin; ask the user to run the `pico-cli setup` command shown. |
| `SETUP_REQUIRED`              | Ask the user to run `pico-cli setup` and select a region, then stop.                        |
| `PROJECT_ROOT_REQUIRED`       | Ask for a project directory as in section 3.                                                |
| `PROJECT_PLATFORM_CONFLICT`   | The project files declare another platform; explain it and stop.                            |
| `PLATFORM_PLUGIN_UNAVAILABLE` | Run `pico-cli plugin update --project "<resource-root>"` (section 9), then retry once.      |
| `PLUGIN_SOURCE_UNAVAILABLE`   | Ask the user to run `pico-cli setup` again.                                                 |
| `PROJECT_WRITE_DENIED`        | Report the path that could not be written; do not retry with elevated permissions.          |
| `HOST_CONFIGURE_FAILED`       | One Host failed; report its message. Other Hosts may still be configured.                   |
| Any other code                | Report the message and stop.                                                                |

`tool_status: PARTIAL` means some Hosts or follow-up steps failed, for example
`KNOWLEDGE_SELECTION_FAILED` or `UNITY_CLI_UNAVAILABLE` (the message links the manual install guide);
report each entry in `errors[]` and continue with the configured Hosts.

## 7. Continue in the same session

After configuration succeeds, read the returned project guidance and the Skill file for the
route selected above. Continue the original request in the same session.

- `guidance[]`: platform `AGENTS.md` paths.
- `skills[]`: available Skill names and file paths.
- `mcpAfterReload[]`: retained native entries that need Host loading/approval.

The global user-level `pico-dev-knowledge`, `pico-spatial-editor`, and `unity-mcp` MCP servers are
independent of project configure. Discover native tools in the current Host catalog, accepting
hyphen/underscore server normalization (`pico-spatial-editor` / `pico_spatial_editor`,
`unity-mcp` / `unity_mcp`, `pico-dev-knowledge` / `pico_dev_knowledge`) and `mcp__` prefixes.
Call only exact advertised names and schemas; verify every required native tool before dependent work.

For `not-in-spatial-project`, use an advertised `workspace_root` for authorized non-coding asset
work (Route C); do not create/configure an SDK project to answer a question. For project-development
routes A/B, preserve the explicit engineering and resource roots when following configure guidance.

If the Unity relay is missing, discover and call `get_unity_relay_status` by its advertised name.
It exposes recovery status, not Unity Editor readiness or the native operation tool set.
Follow its hint to complete authorized Unity initialization / AI Assistant preparation and enable
Unity MCP in the open Editor. If the Host supports MCP restart/reconnect, reconnect only `unity-mcp`
with the necessary approval, then rediscover and verify the required native operation tools are visible.
Otherwise report the Host limitation and its supported recovery action. Do not promise hot recovery on the same transport.
Do not require an entire session restart for relay recovery or mistake status-only visibility for success.

Report every `data.hostActions[]` entry, including trust and approval. First installation or changed
user-level MCP entries must be loaded by the Host; whether resource discovery or MCP restart/reconnect
is supported depends on the actual Host. Continue file/CLI steps when possible, and reload only for a
confirmed Host resource-discovery requirement, not merely `restartRequired: true`. Do not repeatedly
configure to make tools appear. If `data.continuation` is `null`, report why from `hosts[]`.

### Host permissions for coding projects

For routes A/B, after the current Host is configured and before development or subagent handoff,
read [shared-directory-access.md](references/shared-directory-access.md). If effective permissions
already suffice, continue without an authorization checklist or restart suggestion. Only when
repeated operations would benefit and this Host documents a suitably scoped option, optionally
explain it once; a persistent choice at a real prompt is the user's option, never a requirement.
Do not invent an approval step or hand-edit Host permission files. Respect a decline and do not
gate project configuration on this guidance. Route C does not require this preparation.

## 8. Prepare the project before the original task

- Spatial: when the user asked to create or scaffold a project and the directory has no project
  files, continue with the creation Skill from `continuation.skills[]`. It runs
  `pico-cli project create --dir <target-dir>` and the first build, where `<target-dir>` is the
  same directory resolved in section 3.
- Unity: read `.pico-cli/config.json` in the project root. When the file is missing or
  `pico_unity_init_completed` is not `true`, and the request needs a working Unity project
  (creating one, building, or adding features), continue with the Unity initialization Skill from
  `continuation.skills[]` before the original task. It creates the project from a template in an
  empty directory or adds the PICO packages to an existing Unity project, then returns to the
  original task. Do not ask the user to type `/pico-unity-init`. Skip it for a question that
  changes no project.

Do not run `pico-cli project create` from this skill; the platform Skill owns template choice and
the steps that follow it.

## 9. Keep plugins current

When `configured.hosts[].plugins[].updateAvailable` is `true`, suggest
`pico-cli plugin update --project "<resource-root>"`, using detect's `workspaceRoot` (or `projectRoot`
when the roots match). Update's `--project` selects the recorded resources, so an unqualified command
from a different cwd may update the wrong project. It refreshes the user-level general plugin and
the selected project's platform plugin together. When
`legacy.userPlatformPlugins` is not empty, suggest re-running `pico-cli setup` once to migrate them.

## 10. Report

Summarize in a few lines:

1. Project root and platform, with the evidence or the reason for the inference.
2. Hosts configured, and any `hostActions` the user must take.
3. The Skill being continued, or what blocks continuation.
4. Any confirmed Host resource reload or affected MCP reconnect action, and what remains unverified.
