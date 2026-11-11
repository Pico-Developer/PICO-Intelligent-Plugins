# PICO CLI Installation and Setup Guide for AI Agents

Give this page to an AI coding agent when you want it to install PICO CLI and configure PICO development tools. Configuration has two steps:

1. `pico-cli setup` runs once per user. It installs the general PICO plugin for each selected Agent tool and the shared developer tools.
2. `pico-cli project configure` runs once per project. It installs the PICO Spatial or PICO Unity plugin into that project.

The agent must inspect the environment first, confirm the parameters with you, show each complete command, and report the verification results.

## Operating Rules

- Treat the project directory as user data. Do not create, overwrite, or delete project files outside the setup flow described here.
- Do not use `sudo`, change file ownership, edit shell startup files, or change npm configuration unless the user approves that specific action.
- Before running a command that changes the machine, project, or supported Agent tool, explain what it will change and obtain approval.
- Use the installed CLI's help output as the final authority. If an option in this guide is unavailable, stop and show the mismatch instead of guessing a replacement.
- Never run a command while it still contains a placeholder such as `<PROJECT_ABSOLUTE_PATH>`.
- Do not hand-edit Skills, MCP, Hook, or plugin files that setup manages. When setup cannot configure something, report it instead of reproducing setup by hand. The only manual steps are the ones this guide lists for a specific Agent tool.

## 1. Inspect the Environment

PICO CLI requires Node.js 20 or later, npm, and Git. Start with read-only checks:

```shell
node --version
npm --version
git --version
```

If a prerequisite is missing or Node.js is older than version 20, explain the problem and ask the user before installing or upgrading anything.

## 2. Install PICO CLI

If PICO CLI is not already available, show this command and obtain approval before running it:

```shell
npm install -g @picoxr/pico-cli
```

Verify the installed command and inspect the current setup contract:

```shell
pico-cli --version
pico-cli setup --help
pico-cli project configure --help
```

If installation or command discovery fails, show the original error. Do not change npm permissions, `PATH`, shell configuration, or the selected Node.js installation without separate approval.

- For a permission error such as `EACCES`, do not retry with `sudo`. Offer a user-level npm prefix or a Node.js version manager, and apply it only after approval.
- For a network timeout, retry once. If it fails again, ask whether the user has an npm registry mirror or proxy to use for this one installation, for example `npm install -g @picoxr/pico-cli --registry <REGISTRY_URL>`. Do not write it into npm configuration unless the user asks.
- If the install succeeds but `pico-cli` is not found, check it with `command -v pico-cli` on macOS or Linux, or `Get-Command pico-cli` in PowerShell. `npm prefix -g` prints the npm global prefix, not always the executable directory: on macOS and Linux the executables are in its `bin` subdirectory, and on Windows they are in the prefix directory itself. Show that directory and ask before changing `PATH`.

## 3. Confirm the Setup Parameters

Resolve the following values from the user's request and the current workspace, then ask the user to confirm them together:

- **Region**: where PICO downloads and services are routed.
  - `cn` for the Chinese mainland.
  - `row` for the rest of the world.
  - `us` for the United States.

  Non-interactive setup fails when no region was saved by an earlier setup, so always include the confirmed region in the command. A later run can reuse the saved region, but stating it explicitly avoids silently keeping an outdated choice.

  Suggest a region from what the user has said about their location or network, but always let the user confirm it. PICO CLI does not detect the region before setup; it only warns during setup when the selected region does not match the detected environment.

- **Supported Agent tool**:
  - Claude Code: `claude-code`
  - Codex: `codex`
  - Cursor: `cursor`
  - GitHub Copilot: `copilot`
  - Trae CLI: `traecli`
  - OpenCode V2: `opencode2`
  - CodeBuddy Code: `codebuddy`
  - Qoder CLI: `qoder`
  - Antigravity CLI: `antigravity`
  - Grok CLI: `grok`

  Suggest the Agent tool you are running in, and add others only when the user asks for them. Trae IDE is not supported; see [Trae IDE](#trae-ide). If the user only says "Trae", ask whether they mean Trae IDE or Trae CLI.

  `--agent-tool` accepts several values separated by spaces, for example `--agent-tool codex traecli`. The list is the complete set of Agent tools configured for the user: a tool that an earlier setup configured and that is missing from the list is removed. Projects already configured for a removed tool then report a `project.general` error in `pico-cli doctor` until setup includes that tool again. Ask the user whether earlier tools should stay before you leave them out. Do not silently choose `all`; use it only when the user explicitly asks to configure every supported tool. `all` selects every Agent tool this PICO CLI release supports, not only the tools installed on the machine.

  Setup installs the general plugin through each Agent tool's own plugin mechanism, so some tools need their CLI on `PATH` (Cursor requires the Cursor application). Setup skips and reports a tool it cannot configure; that tool cannot be used for a project until a later setup configures it.

- **Project Directory** (optional): the absolute engineering project path to configure after setup. Never infer a different project when the user has supplied one. For user-level setup or questions that do not change a project, skip project configure and the development target.
- **Resource Workspace Root** (only when distinct from the project): the absolute session directory where the Host loads project resources. Confirm it explicitly and retain `--project <engineering-project> --workspace-root <resource-workspace>` in every configure, detect, doctor, and approved doctor repair. Do not create a local mapping or guess a parent directory. For example, later diagnostics use `pico-cli doctor --project <engineering-project> --workspace-root <resource-workspace>`. Doctor with only `--project` does not infer a resource association from parent directories.

- **Development target** (only with a project directory):
  - `spatial` for PICO Spatial development.
  - `unity` for PICO Unity development.

  Infer the target from the project and ask the user to confirm it:
  - A project with `ProjectSettings/ProjectVersion.txt` is a Unity project: suggest `unity`.
  - A Gradle project that declares the PICO Spatial SDK BOM (`com.pico.spatial`) in `gradle/libs.versions.toml` or `build.gradle(.kts)` is a Spatial project: suggest `spatial`.
  - A project directory with both markers is ambiguous: show the user both files and ask which target to use.
  - For an empty directory or a project with neither marker, ask the user.

  Markers count only inside the project directory, not in its parent directories. `project configure` rejects a target that contradicts the project's only marker. If that happens, confirm the project directory with the user instead of changing project files. With both markers, either target is accepted.

Setup changes only user-level state; it writes nothing into a project. It saves the region, prepares
a Java runtime and `PICO_HOME`, installs knowledge data and its uv/Python query service, installs
the Unity CLI, and registers the general plugin's global MCP entries (`pico-dev-knowledge`,
`pico-spatial-editor`, `unity-mcp`). Once the Host loads and approves them, tools can be discovered
without project configure; actual Editor/relay operations still require their backend prerequisites.
`project configure` installs platform Skills and guidance at the confirmed resource root, records
platform/knowledge selection in the resource workspace's `.pico-env.json` (the engineering project
when the roots match; use the returned `knowledge.picoEnvPath` or detect's `knowledge.filePath`), and maintains its managed
`.gitignore` block for Git projects. It does not create application files. Include these effects in approval.

Use a confirmation message equivalent to this one:

> Please confirm the PICO CLI setup parameters:
>
> - Region: `<cn|row|us>`
> - Supported Agent tool: `<AI_CODING_TOOL>`
> - Project Directory: `<PROJECT_ABSOLUTE_PATH>` (or "none")
> - Resource Workspace Root: `<WORKSPACE_ABSOLUTE_PATH>` (only when distinct)
> - Development target: `<spatial|unity>` (only with a project)

### Trae IDE

Trae IDE is not supported. It does not read the Trae CLI plugin marketplace where setup installs the general plugin, and PICO CLI has no Trae IDE value for `--agent-tool`. Tell the user that PICO development tools cannot be configured for Trae IDE, and offer a supported Agent tool instead. Do not copy Skills, MCP configuration, or Hooks into Trae IDE directories by hand.

## 4. Review and Run Setup

Replace every placeholder, show the exact command to the user, explain that it changes user-level PICO and Agent-tool state, and ask for approval:

```shell
pico-cli setup \
  --agent-tool <AI_CODING_TOOL> \
  --region <cn|row|us> \
  --yes
```

`--yes` indicates that the user has already reviewed the complete command. Do not add it before the command and all resolved values have been shown to the user.

After approval, run the command non-interactively. Preserve the original setup output so warnings and failed steps can be reported accurately. If setup warns that the selected region does not match the detected environment, report the warning and ask whether the user wants to rerun with a different region.

Setup can take several minutes on a new machine because it also prepares a Java runtime, PICO development knowledge data, and the local knowledge query service. Let it finish instead of interrupting it as stalled while it is still producing output.

### Configure the Project

Skip this step when the user did not choose a project directory. In project command examples below,
include `--workspace-root` only for confirmed distinct roots; otherwise omit that entire option.
After setup succeeds, show this command with every placeholder replaced and ask for approval:

```shell
pico-cli project configure \
  --platform <spatial|unity> \
  --project "<PROJECT_ABSOLUTE_PATH>" \
  --workspace-root "<WORKSPACE_ABSOLUTE_PATH>" \
  --agent-tool <AI_CODING_TOOL> \
  --yes \
  --format json
```

Pass only Agent tools that setup configured. Running the command again for the same target is safe; it refreshes the project. Configuring a different target replaces the platform plugin for every Agent tool already configured in the project, so confirm that with the user first.

Read the JSON result. The top-level `tool_status` is `SUCCESS`, `PARTIAL`, or `FAILED`; `data` holds the configure result, and is `null` when the command failed before configuring any Agent tool. On `PARTIAL` or `FAILED`, `errors[]` names each problem with a `code` and a `message`:

| `code`                      | Action                                                                                            |
| --------------------------- | ------------------------------------------------------------------------------------------------- |
| `SETUP_REQUIRED`            | Setup has not completed for this user; return to [Review and Run Setup](#4-review-and-run-setup). |
| `AGENT_HOST_NOT_SET_UP`     | The Agent tool lacks the general plugin; rerun setup including that tool.                         |
| `PROJECT_PLATFORM_CONFLICT` | The project files declare the other target; confirm the project directory with the user.          |
| `PROJECT_ROOT_REQUIRED`     | The directory is missing or is the user's home directory; ask for a project directory.            |
| Any other code              | Report the message, then follow [Recover from Setup Failures](#5-recover-from-setup-failures).    |

`data.hostActions[]` lists actions the user must take in each Agent tool, such as approving project MCP servers or trusting the project. Report each of them.

## 5. Recover from Setup Failures

Read the end of the setup output before deciding what to do:

These rules apply to `pico-cli setup`. For `pico-cli project configure`, use the `errors[]` table in [Configure the Project](#configure-the-project) first.

- Exit status `0` means the selected Agent tool was configured. The output can still contain dependency warnings. Report them, and handle them through the read-only check in [Verify the Result](#6-verify-the-result).
- A non-zero exit status means setup did not complete. Read the error at the end of the output instead of matching a fixed prefix. Common forms are:
  - an option or parameter error, such as a missing region. Correct the command, show it to the user again, and rerun it.
  - a planning failure before confirmation, such as `Setup planning failed before confirmation`. No planned writes or dependency installation were started.
  - a failure while applying the plan, such as `Setup completed with failures` or `Setup completed with dependency failures`, which names the failed step and includes its error.

  Choose the fallback from the cause in the error, not from the step name.

Apply these rules to every recovery:

- Rerun the same approved command after fixing the cause. Both commands are safe to rerun: completed steps are reused and interrupted changes are recovered.
- Retry a transient network failure, such as a timeout or connection reset, once without changes. If it fails again, use the fallback instead of looping.
- Explain each fallback and get approval before installing software, using a proxy or mirror, or setting environment variables. Set environment variables only for the single command that needs them unless the user asks to persist them.
- Download software only from its official vendor channel, the user's package manager, or a mirror the user names.
- Do not disable TLS or certificate verification, do not use `sudo`, and do not copy files into directories that PICO CLI manages, such as `~/.pico` or `~/.pico-cli`. Do not edit the Agent tool's Skills, MCP, or Hook files to work around a failed step.

| Cause in the error                                                    | Fallback                                                                                                                                                                                                                        |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Java, a JDK, `javac`, or a Java download                              | Follow [Java Runtime Fallback](#java-runtime-fallback).                                                                                                                                                                         |
| A network timeout, connection reset, DNS failure, or blocked download | After the single retry, confirm that the selected region matches the user's network. Then ask whether the user has a proxy or mirror. Use only what the user provides, for the rerun only, and never substitute another source. |
| A missing tool, such as uv or the Unity CLI                           | With approval, install it from its official channel or the user's package manager, confirm that its version command works, and rerun setup.                                                                                     |
| Anything else                                                         | Run the read-only check in [Verify the Result](#6-verify-the-result) and follow the `repair` and `nextAction` values it reports.                                                                                                |

If a fallback is not possible, or the same step fails after it, stop. Report the failed step, the original error, and what was tried.

### Java Runtime Fallback

PICO CLI accepts an existing JDK 21 or later before it downloads one. It looks at `JAVA_HOME`, then JDKs registered with macOS, then `java` on `PATH`. A Java runtime without `javac` does not qualify.

1. Check for a usable JDK with `java -version` and `javac -version`. On macOS, `/usr/libexec/java_home -V` lists registered JDKs.
2. If no JDK 21 or later is available, ask the user to approve installing one from an official channel. Examples are Homebrew (`brew install --cask temurin@21`), WinGet (`winget install EclipseAdoptium.Temurin.21.JDK`), the Eclipse Temurin installer, or the user's own JDK distribution.
3. Rerun the approved setup command with `JAVA_HOME` set to that JDK for this command only. Do not set it in shell startup files unless the user asks. Use the same `JAVA_HOME` prefix when an approved `pico-cli doctor --fix` reports that the Java runtime could not be prepared.

macOS or Linux:

```shell
JAVA_HOME="<JDK_21_HOME>" pico-cli setup \
  --agent-tool <AI_CODING_TOOL> \
  --region <cn|row|us> \
  --yes
```

Windows PowerShell:

```shell
$previousJavaHome = $env:JAVA_HOME
try {
  $env:JAVA_HOME = "<JDK_21_HOME>"
  pico-cli setup --agent-tool <AI_CODING_TOOL> --region <cn|row|us> --yes
} finally {
  $env:JAVA_HOME = $previousJavaHome
}
```

PowerShell keeps `$env:` changes for the rest of the session, so the example restores the previous value when the command finishes.

## 6. Verify the Result

Run the comprehensive read-only check. `pico-cli doctor` always checks the user-level environment
and plugin. When a project was configured, retain `--project` for its engineering evidence and
`--workspace-root` for distinct Host resources, using the same pair as configure. Without an explicit
resource root, doctor checks resources at the project; it does not search parents for an association.
Pass `--platform` to assert the expected target. Omit all project/root/platform options when no project
was configured, and omit only `--workspace-root` when the two roots are the same.

```shell
pico-cli doctor \
  --project "<PROJECT_ABSOLUTE_PATH>" \
  --workspace-root "<WORKSPACE_ABSOLUTE_PATH>" \
  --agent-tool <AI_CODING_TOOL> \
  --platform <spatial|unity> \
  --format json
```

If the assertion does not match the project, doctor adds a structured `doctor.platform` error, still reports the project's actual target, and makes no project repairs. JSON consumers must accept `null` for both `data.targetPlatform` and `data.overview.sdk` when no project platform is found.

When a project was configured, also read its configuration. `--project` inspects that directory exactly, without searching parent directories:

```shell
pico-cli project detect --project "<PROJECT_ABSOLUTE_PATH>" --workspace-root "<WORKSPACE_ABSOLUTE_PATH>" --format json
```

Inspect the JSON and process exit status instead of relying only on the final console message. `pico-cli doctor` exits with `0` when every check passes, `4` for a usable environment with warnings, and `3` when a check reports an error. Each check in `data.checks[].checks[]` has an `id`, a `status` of `ok`, `warn`, `error`, or `skip`, and, when something needs attention, a `nextAction` and a `repair` list. Report each failed, warning, or skipped check with its `nextAction`. A wider environment finding does not by itself mean setup failed.

Setup is complete when the setup command succeeds and these checks are `ok` for the selected Agent tool:

- `plugin.doctor`, which covers the user-level plugin for the Agent tool.
- When a project was configured, `project.plugin.doctor`, which covers the project's platform plugin.
- When a project was configured, `project detect` lists the selected Agent tool under `data.configured.hosts` with the chosen target in `data.configured.platforms`.

Report every other finding separately as an environment item with its recommended next action. Ignore a `skip` unless the user needs that capability.

### Repair Findings

PICO CLI reports how to repair each finding, so decide from the check's `repair` entries and `nextAction`, not from its wording or from a list in this guide:

- If a check has a `repair` entry with `"mode": "automatic"`, `pico-cli doctor --fix` can repair it.
- Otherwise, `--fix` does not change it. Follow the check's `nextAction` or its manual `repair` command.

Do not run `--fix` automatically. First explain which checks it will repair and any downloads or
installations. After approval, retain the same engineering project, distinct resource workspace root,
and Agent tool as the read-only check. Omit both root options when no project was configured, or
omit only `--workspace-root` when the two roots are the same:

```shell
pico-cli doctor --fix \
  --project "<PROJECT_ABSOLUTE_PATH>" \
  --workspace-root "<WORKSPACE_ABSOLUTE_PATH>" \
  --agent-tool <AI_CODING_TOOL> \
  --format json
```

Read `data.fixed[]` for the result of each attempted repair, and `data.report` for the checks after the repair. The exit status describes the checks after the repair, not whether each repair succeeded, so always inspect both. Run `--fix` at most twice for the same check, and use the fallbacks in [Recover from Setup Failures](#5-recover-from-setup-failures) when a repair fails on Java or the network.

Without `--project`, `pico-cli doctor --fix` still repairs the user-level findings that have an automatic `repair` entry, such as the Java runtime or knowledge data. The report then has no project checks, and `data.fixed[]` is empty when nothing needed repair. `--fix` never installs a platform plugin; when the user chose a project, run the approved `pico-cli project configure` command.

For a manual `nextAction`, apply the same rules as for `--fix`:

- Get approval before running a command that installs software, downloads components, updates PICO CLI, or changes setup state.
- Some steps must run in the user's own shell, such as setting `PICO_HOME` or `JAVA_HOME`. Show the exact command to the user. Do not write it into shell startup files unless the user asks, and tell the user that a new terminal or Agent session needs the variable too.
- Checks for optional capabilities, such as the Spatial Editor, the emulator, or performance analysis, need action only when the user needs that capability.
- If a manual action would close Spatial Editor windows, ask the user to close them so unsaved work is preserved.

## 7. Continue or Load Agent Resources

Setup registers the global user-level `pico-dev-knowledge`, `pico-spatial-editor`, and `unity-mcp`
MCP servers independently of a project. First installation or changed user-level MCP entries must
still be loaded and approved by the actual Host. Installing files cannot inject tools into a running
session; whether the Host supports resource reload or MCP restart/reconnect must be checked, not assumed.
`project configure` adds platform Skills and guidance, not project-level MCP entries.

For project continuation, read `data.continuation.guidance[]` and the matching
`data.continuation.skills[].path`; `data.continuation.mcpAfterReload[]` identifies any retained native
entries needing Host loading/approval. Read files to continue guidance, but do not claim that reading
registers a Skill or MCP tool. Follow every `data.hostActions[]` entry for trust and approval.
Continue file/CLI steps where possible; reload only for a confirmed Host resource-discovery requirement.
Do not repeatedly configure to make tools appear or close/restart the user's Host without permission.

When MCP is needed, discover the global server's native tools in the current Host catalog, accepting
hyphen/underscore normalization (`pico-spatial-editor` / `pico_spatial_editor`, `unity-mcp` /
`unity_mcp`, `pico-dev-knowledge` / `pico_dev_knowledge`) and `mcp__` prefixes. Call only exact advertised names
and schemas and verify required tools before dependent operations; discovery alone is not backend readiness.
For a non-coding Editor action, pass the user's controlled asset workspace as `workspace_root` only
when the tool advertises that parameter. A `not-in-spatial-project` result is guidance, not permission
to create/configure an SDK project.

A missing Unity relay may expose only `get_unity_relay_status`. This is recovery status, not Unity
Editor readiness or the native operation tool set. Follow its hint to complete authorized Unity
initialization / AI Assistant preparation, open the project, and enable Unity MCP in the Editor.
For an already initialized project, restore its bridge without resetting or rerunning initialization.
If the Host supports MCP restart/reconnect, reconnect only `unity-mcp` with the necessary approval,
then rediscover and verify the required native operation tools are visible before resuming the task.
Otherwise report the Host limitation and its supported recovery action; do not claim every Host needs
no user action. Do not promise hot recovery on the same transport. Do not require an entire session restart
for relay recovery, and do not report status-only discovery as an operational Editor connection.

For general-only questions, use the installed general `knowledge-query` / `pico-cli` Skills and
knowledge MCP as fallbacks. Use an already installed platform Skill through its readable project
file or available Host entry; do not install platform Skills or scaffold/configure a project just to
answer a question. Authorized project creation or implementation follows the project's platform route.

The PICO MCP servers start through `npx`, so the first start can take longer while npm downloads
PICO CLI with the user's own npm configuration. On startup failure, use the Host's supported MCP
retry/reconnect action. If it keeps failing, report the original error and npm registry in use instead
of changing npm configuration. Verify live tool visibility after any approved Host action.

### Local override scope (Skills vs MCP)

Project-level resources override user-level resources only for **Skills**: a Skill the project
plugin provides replaces the same-named Skill from the user-level general plugin. This override
does **not** apply to MCP servers — the global `pico-dev-knowledge`, `pico-spatial-editor`, and
`unity-mcp` entries are user-level, and a leftover configuration that also declares one of these
names (for example an older user-level `pico-spatial-agentic-tools` plugin, or a hand-written
`.mcp.json`) can result in the same server being registered more than once in the Agent tool.

Duplicate registrations are not something to rely on: they can show up as duplicate MCP entries or
as ambiguous behavior. If the user sees a duplicated PICO MCP server, the recommended fix is to
disable the older entry in the Agent tool's plugin / MCP management UI — typically the legacy
user-level `pico-spatial-agentic-tools` plugin — rather than hand-editing Host MCP files.
`pico-cli doctor` reports this overlap as a read-only advisory; it does not remove any entry
automatically.

## Completion Report

Report all of the following:

- installed PICO CLI version
- region
- configured Agent tool
- setup result, including dependency warnings
- configured project path and development target, or that no project was configured
- `project configure` result, including `errors[]` and `hostActions[]`
- fallbacks that were applied, such as a user-installed JDK passed through `JAVA_HOME`, a proxy, or a mirror, and whether any of them were persisted
- `pico-cli doctor` result and process exit status
- each `pico-cli doctor --fix` run that the user approved, the repairs it attempted, and their results
- remaining checks that need manual action, with the action the user still has to take
- `project detect` result when a project was configured
- unresolved warnings, blocked steps, and their `nextAction` values
- remaining Host trust, approval, or supported resource-discovery actions from `hostActions[]`
- whether guidance/CLI work continues from `data.continuation`, which MCP needs reconnect, and whether required native operation tools were actually verified

For additional command details, use the installed CLI help:

```shell
pico-cli setup --help
pico-cli project configure --help
pico-cli doctor --help
pico-cli project detect --help
```
