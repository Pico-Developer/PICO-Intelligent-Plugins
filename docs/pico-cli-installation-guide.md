# PICO CLI Installation and Setup Guide for AI Agents

Give this page to an AI coding agent when you want it to install PICO CLI and configure PICO development tools for a project. The agent must inspect the environment first, confirm the setup target and write scope with you, show the complete setup command, and report the verification results.

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
```

If installation or command discovery fails, show the original error. Do not change npm permissions, `PATH`, shell configuration, or the selected Node.js installation without separate approval.

- For a permission error such as `EACCES`, do not retry with `sudo`. Offer a user-level npm prefix or a Node.js version manager, and apply it only after approval.
- For a network timeout, retry once. If it fails again, ask whether the user has an npm registry mirror or proxy to use for this one installation, for example `npm install -g @picoxr/pico-cli --registry <REGISTRY_URL>`. Do not write it into npm configuration unless the user asks.
- If the install succeeds but `pico-cli` is not found, check it with `command -v pico-cli` on macOS or Linux, or `Get-Command pico-cli` in PowerShell. `npm prefix -g` prints the npm global prefix, not always the executable directory: on macOS and Linux the executables are in its `bin` subdirectory, and on Windows they are in the prefix directory itself. Show that directory and ask before changing `PATH`.

## 3. Confirm the Setup Parameters

Resolve the following values from the user's request and the current workspace, then ask the user to confirm them together:

- **Project Directory**: the absolute path of the project to configure. Never infer a different project when the user has already supplied one.
- **Region**: where PICO downloads and services are routed.
  - `cn` for the Chinese mainland.
  - `row` for the rest of the world.
  - `us` for the United States.

  Non-interactive setup fails when no region was saved by an earlier setup, so always include the confirmed region in the command. A later run can reuse the saved region, but stating it explicitly avoids silently keeping an outdated choice.

  Suggest a region from what the user has said about their location or network, but always let the user confirm it. PICO CLI does not detect the region before setup; it only warns during setup when the selected region does not match the detected environment.

- **Setup scope**:
  - `local` configures project-level resources for the selected Agent tool. Host support and the exact files to be written are shown by the PICO CLI setup plan. Local scope limits the Agent tool's plugin resources to project files and does not require the Agent tool's own CLI.
  - `global` configures the integration for the current user across projects while linking guidance to the selected project. Global setup installs through the Agent tool itself, so that tool's CLI must be installed and available on `PATH` (Cursor requires the Cursor application).

  Either scope also changes user-level PICO state outside the project: it saves the selected region, prepares a Java runtime and `PICO_HOME` under the user's PICO directory, installs or refreshes PICO development knowledge data and records it for the project, and prepares the local knowledge query service with uv and Python. Include these effects when you ask the user to approve setup.

  Recommend `local` by default, because it keeps the Agent tool's plugin resources inside the selected project and does not depend on the Agent tool's CLI. Recommend `global` only when the user wants PICO tools in every project and the Agent tool's CLI responds to its version command. Trae IDE always uses `local`.

- **Development target**:
  - `spatial` for PICO Spatial development.
  - `unity` for PICO Unity development.

  Infer the target from the project and ask the user to confirm it:
  - A project with `ProjectSettings/ProjectVersion.txt` is a Unity project: suggest `unity`.
  - A Gradle project that declares the PICO Spatial SDK BOM (`com.pico.spatial`) in `gradle/libs.versions.toml` or `build.gradle(.kts)` is a Spatial project: suggest `spatial`.
  - For an empty directory or a project with neither marker, ask the user.

  Setup rejects a target that contradicts these project markers. If that happens, confirm the project directory with the user instead of changing project files.

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
  - Trae IDE: no dedicated value; follow [Trae IDE](#trae-ide) and use `traecli` with `local` scope.

Suggest the Agent tool you are running in, and add others only when the user asks for them. If the user only says "Trae", ask whether they mean Trae IDE or Trae CLI, because they are configured differently.

`--agent-tool` accepts several values separated by spaces, for example `--agent-tool codex traecli`. Configure only the Agent tools the user requested. Do not silently choose `all`; use it only when the user explicitly asks to configure every supported tool. `all` selects every Agent tool this PICO CLI release supports, not only the tools installed on the machine, so `global` setup fails for each tool whose CLI is missing. To configure only installed tools, check each tool's CLI and list the ones found explicitly.

Use a confirmation message equivalent to this one:

> Please confirm the PICO CLI setup parameters:
>
> - Project Directory: `<PROJECT_ABSOLUTE_PATH>`
> - Region: `<cn|row|us>`
> - Setup scope: `<local|global>`
> - Development target: `<spatial|unity>`
> - Supported Agent tool: `<AI_CODING_TOOL>`

### Trae IDE

Trae IDE does not have its own `--agent-tool` value. Its project Skills directory `.trae/skills/` and project MCP file `.trae/mcp.json` are the same paths that Trae CLI local setup manages, so configure Trae IDE with `--agent-tool traecli --scope local`. The Trae CLI executable is not required for local setup.

- Do not use `global` scope for Trae IDE. Trae CLI global setup installs into the Trae CLI plugin marketplace, which Trae IDE does not read.
- Setup also writes Trae CLI-only files under `.trae/cli/`. Trae IDE ignores them; do not move or copy them.
- PICO Hooks do not support Trae IDE yet. Do not create or edit `.trae/hooks.json` or the user-level Trae IDE `hooks.json`, and do not copy Trae CLI Hooks into them. Report that Hook-based capabilities are unavailable in Trae IDE.
- Trae IDE can import Claude Code Hooks. If the project is also configured for Claude Code and the user has enabled that import, Claude Code Hooks from `.claude/settings.json` also run in Trae IDE. Explain this and let the user decide whether to keep the import enabled.
- Trae IDE needs two settings that the user changes; do not edit Trae IDE settings yourself:
  - Settings > MCP > **Enable Project MCP**, which loads `.trae/mcp.json` from the project root. Without it, Trae IDE does not start the PICO MCP servers that setup configured.
  - The Settings > Rules import option that includes `AGENTS.md` in the context. Without it, Trae IDE does not read the project guidance that setup links in `AGENTS.md`.

## 4. Review and Run Setup

Replace every placeholder, show the exact command to the user, explain that it changes plugin and Agent-tool state, and ask for approval.

For a PICO Spatial project:

```shell
pico-cli setup \
  --agent-tool <AI_CODING_TOOL> \
  --region <cn|row|us> \
  --scope <local|global> \
  --platform spatial \
  --project "<PROJECT_ABSOLUTE_PATH>" \
  --yes
```

For a PICO Unity project:

```shell
pico-cli setup \
  --agent-tool <AI_CODING_TOOL> \
  --region <cn|row|us> \
  --scope <local|global> \
  --platform unity \
  --project "<PROJECT_ABSOLUTE_PATH>" \
  --yes
```

`--yes` indicates that the user has already reviewed the complete command. Do not add it before the command and all resolved values have been shown to the user.

After approval, run the command non-interactively. Preserve the original setup output so warnings and failed steps can be reported accurately. If setup warns that the selected region does not match the detected environment, report the warning and ask whether the user wants to rerun with a different region.

Setup can take several minutes on a new machine because it also prepares a Java runtime, PICO development knowledge data, and the local knowledge query service. Let it finish instead of interrupting it as stalled while it is still producing output.

## 5. Recover from Setup Failures

Read the end of the setup output before deciding what to do:

- Exit status `0` means the selected Agent tool was configured. The output can still contain dependency warnings. Report them, and handle them through the read-only check in [Verify the Result](#6-verify-the-result).
- A non-zero exit status means setup did not complete. Read the error at the end of the output instead of matching a fixed prefix. Common forms are:
  - an option or parameter error, such as a missing region. Correct the command, show it to the user again, and rerun it.
  - a planning failure before confirmation, such as `Setup planning failed before confirmation`. No planned writes or dependency installation were started.
  - a failure while applying the plan, such as `Setup completed with failures` or `Setup completed with dependency failures`, which names the failed step and includes its error.

  Choose the fallback from the cause in the error, not from the step name.

Apply these rules to every recovery:

- Rerun the same approved setup command after fixing the cause. Setup is safe to rerun: completed steps are reused and interrupted project changes are recovered.
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
  --scope <local|global> \
  --platform <spatial|unity> \
  --project "<PROJECT_ABSOLUTE_PATH>" \
  --yes
```

Windows PowerShell:

```shell
$previousJavaHome = $env:JAVA_HOME
try {
  $env:JAVA_HOME = "<JDK_21_HOME>"
  pico-cli setup --agent-tool <AI_CODING_TOOL> --region <cn|row|us> --scope <local|global> --platform <spatial|unity> --project "<PROJECT_ABSOLUTE_PATH>" --yes
} finally {
  $env:JAVA_HOME = $previousJavaHome
}
```

PowerShell keeps `$env:` changes for the rest of the session, so the example restores the previous value when the command finishes.

## 6. Verify the Result

Run the comprehensive read-only check from the configured project directory. `pico-cli doctor`
uses the current working directory as project context and automatically selects the effective setup
platform; it does not accept a project-path option. Pass `--platform` to assert the expected setup
platform without changing the diagnostic target.

```shell
cd "<PROJECT_ABSOLUTE_PATH>"
pico-cli doctor \
  --agent-tool <AI_CODING_TOOL> \
  --platform <spatial|unity> \
  --format json
```

If the assertion does not match the effective setup, doctor returns a structured platform error and
does not run either platform's specialized checks or repairs. JSON consumers must accept `null` for
both `data.targetPlatform` and `data.overview.sdk` when setup has not selected a valid platform or
the assertion fails.

When `local` scope was selected, also verify the project guidance routing from the same directory:

```shell
cd "<PROJECT_ABSOLUTE_PATH>"
pico-cli project context doctor \
  --agent-tool <AI_CODING_TOOL> \
  --format json
```

For Trae IDE, pass `traecli` as `<AI_CODING_TOOL>` in both checks.

Inspect the JSON and process exit status instead of relying only on the final console message. `pico-cli doctor` exits with `0` when every check passes, `4` for a usable environment with warnings, and `3` when a check reports an error. Each check in `data.checks[].checks[]` has an `id`, a `status` of `ok`, `warn`, `error`, or `skip`, and, when something needs attention, a `nextAction` and a `repair` list. Report each failed, warning, or skipped check with its `nextAction`. A wider environment finding does not by itself mean setup failed.

Setup is complete when the setup command succeeds and these checks are `ok` for the selected Agent tool:

- `plugin.doctor`, which covers plugin installation for the Agent tool.
- `project.context.doctor` when `local` scope was selected.

Report every other finding separately as an environment item with its recommended next action. Ignore a `skip` unless the user needs that capability.

### Repair Findings

PICO CLI reports how to repair each finding, so decide from the check's `repair` entries and `nextAction`, not from its wording or from a list in this guide:

- If a check has a `repair` entry with `"mode": "automatic"`, `pico-cli doctor --fix` can repair it.
- Otherwise, `--fix` does not change it. Follow the check's `nextAction` or its manual `repair` command.

Do not run `--fix` automatically. First tell the user which checks it will repair. Some repairs download large components, such as a JDK, Android SDK components, or knowledge data, or install software. After approval, run it from the project directory:

```shell
cd "<PROJECT_ABSOLUTE_PATH>"
pico-cli doctor --fix --format json
```

Read `data.fixed[]` for the result of each attempted repair, and `data.report` for the checks after the repair. The exit status describes the checks after the repair, not whether each repair succeeded, so always inspect both. Run `--fix` at most twice for the same check, and use the fallbacks in [Recover from Setup Failures](#5-recover-from-setup-failures) when a repair fails on Java or the network.

`pico-cli doctor --fix` changes nothing when setup has not recorded a development platform. It then reports `PICO platform is not configured`; rerun the approved setup command instead.

For a manual `nextAction`, apply the same rules as for `--fix`:

- Get approval before running a command that installs software, downloads components, updates PICO CLI, or changes setup state.
- Some steps must run in the user's own shell, such as setting `PICO_HOME` or `JAVA_HOME`. Show the exact command to the user. Do not write it into shell startup files unless the user asks, and tell the user that a new terminal or Agent session needs the variable too.
- Checks for optional capabilities, such as the Spatial Editor, the emulator, or performance analysis, need action only when the user needs that capability.
- If a manual action would close Spatial Editor windows, ask the user to close them so unsaved work is preserved.

## 7. Start a New Agent Session

The current Agent session started before the newly configured Skills and MCP servers were registered. Tell the user to start a new session from the configured project directory, or fully restart the selected Agent tool, before continuing PICO development.

Some Agent tools need an additional user action before the new session loads project resources:

- Codex loads the project `.codex/config.toml` written by `local` setup only after the user trusts the project.
- Trae IDE needs the **Enable Project MCP** and `AGENTS.md` import settings described in [Trae IDE](#trae-ide). In the new session, ask the user to confirm that the PICO Skills appear under the project Skills list and that the PICO MCP servers appear and start in the MCP list. Report any missing item instead of configuring it by hand.

The PICO MCP servers start through `npx`, so the first start in a new session can take longer while npm downloads PICO CLI with the user's own npm configuration. If an MCP server fails to start, ask the user to retry it from the Agent tool's MCP settings. If it keeps failing, report the error and the npm registry in use instead of changing npm configuration.

Do not close or restart the user's Agent tool without permission. Do not claim the newly installed Skills or MCP servers are available in the current session.

## Completion Report

Report all of the following:

- installed PICO CLI version
- configured project path
- region
- setup scope
- development target
- configured Agent tool, including Trae IDE when it was configured through `traecli`
- setup result, including dependency warnings
- fallbacks that were applied, such as a user-installed JDK passed through `JAVA_HOME`, a proxy, or a mirror, and whether any of them were persisted
- `pico-cli doctor` result and process exit status
- each `pico-cli doctor --fix` run that the user approved, the repairs it attempted, and their results
- remaining checks that need manual action, with the action the user still has to take
- project context result when `local` scope was selected
- unresolved warnings, blocked steps, and their `nextAction` values
- Agent-tool actions the user still needs to take, such as trusting the Codex project or enabling the Trae IDE **Enable Project MCP** and `AGENTS.md` import settings
- capabilities that are unavailable for the selected Agent tool, such as PICO Hooks in Trae IDE
- requirement to start a new Agent session

For additional command details, use the installed CLI help:

```shell
pico-cli setup --help
pico-cli doctor --help
pico-cli project context doctor --help
```
