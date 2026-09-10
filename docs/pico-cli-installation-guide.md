# PICO CLI Installation and Setup Guide for AI Agents

Give this page to an AI coding agent when you want it to install PICO CLI and configure PICO development tools for a project. The agent must inspect the environment first, confirm the setup target and write scope with you, show the complete setup command, and report the verification results.

## Operating Rules

- Treat the project directory as user data. Do not create, overwrite, or delete project files outside the setup flow described here.
- Do not use `sudo`, change file ownership, edit shell startup files, or change npm configuration unless the user approves that specific action.
- Before running a command that changes the machine, project, or supported Agent tool, explain what it will change and obtain approval.
- Use the installed CLI's help output as the final authority. If an option in this guide is unavailable, stop and show the mismatch instead of guessing a replacement.
- Never run a command while it still contains a placeholder such as `<PROJECT_ABSOLUTE_PATH>`.

## 1. Inspect the Environment

PICO CLI requires Node.js 18 or later, npm, and Git. Start with read-only checks:

```shell
node --version
npm --version
git --version
```

If a prerequisite is missing or Node.js is older than version 18, explain the problem and ask the user before installing or upgrading anything.

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

## 3. Confirm the Setup Parameters

Resolve the following values from the user's request and the current workspace, then ask the user to confirm them together:

- **Project Directory**: the absolute path of the project to configure. Never infer a different project when the user has already supplied one.
- **Setup scope**:
  - `local` configures project-level resources for the selected Agent tool. Host support and the exact files to be written are shown by the PICO CLI setup plan.
  - `global` configures the integration for the current user across projects while linking guidance to the selected project.
- **Development target**:
  - `spatial` for PICO Spatial development.
  - `unity` for PICO Unity development.
- **Supported Agent tool**:
  - Claude Code: `claude-code`
  - Codex: `codex`
  - Cursor: `cursor`
  - GitHub Copilot: `copilot`
  - Trae CLI: `traecli`

Do not silently choose `all`. Configure only the Agent tool requested by the user unless they explicitly ask to configure every supported tool.

Use a confirmation message equivalent to this one:

> Please confirm the PICO CLI setup parameters:
>
> - Project Directory: `<PROJECT_ABSOLUTE_PATH>`
> - Setup scope: `<local|global>`
> - Development target: `<spatial|unity>`
> - Supported Agent tool: `<AI_CODING_TOOL>`

## 4. Review and Run Setup

Replace every placeholder, show the exact command to the user, explain that it changes plugin and Agent-tool state, and ask for approval.

For a PICO Spatial project:

```shell
pico-cli setup \
  --agent-tool <AI_CODING_TOOL> \
  --scope <local|global> \
  --platform spatial \
  --project "<PROJECT_ABSOLUTE_PATH>" \
  --yes
```

For a PICO Unity project:

```shell
pico-cli setup \
  --agent-tool <AI_CODING_TOOL> \
  --scope <local|global> \
  --platform unity \
  --project "<PROJECT_ABSOLUTE_PATH>" \
  --yes
```

`--yes` indicates that the user has already reviewed the complete command. Do not add it before the command and all resolved values have been shown to the user.

After approval, run the command non-interactively. Preserve the original setup output so warnings and failed steps can be reported accurately.

## 5. Verify the Result

Run the comprehensive read-only check from the configured project directory. `pico-cli doctor` uses the current working directory as project context; it does not accept a project-path option.

```shell
cd "<PROJECT_ABSOLUTE_PATH>"
pico-cli doctor \
  --agent-tool <AI_CODING_TOOL> \
  --platform <spatial|unity> \
  --format json
```

When `local` scope was selected, also verify the project guidance routing from the same directory:

```shell
cd "<PROJECT_ABSOLUTE_PATH>"
pico-cli project context doctor \
  --agent-tool <AI_CODING_TOOL> \
  --format json
```

Inspect the JSON and process exit status instead of relying only on the final console message. Report each failed, partial, warning, or skipped check with its documented `nextAction`. A wider environment finding does not by itself mean setup failed.

Do not automatically run `--fix`, installation, update, or shell-configuration commands returned by a check. Explain the proposed action and obtain approval first.

Setup is complete when the setup command succeeds and the checks owned by this workflow pass for the selected Agent tool. For `local` scope, project context routing must also pass. Report unrelated environment findings separately with their recommended next actions.

## 6. Start a New Agent Session

The current Agent session started before the newly configured Skills and MCP servers were registered. Tell the user to start a new session from the configured project directory, or fully restart the selected Agent tool, before continuing PICO development.

Do not close or restart the user's Agent tool without permission. Do not claim the newly installed Skills or MCP servers are available in the current session.

## Completion Report

Report all of the following:

- installed PICO CLI version
- configured project path
- setup scope
- development target
- configured Agent tool
- setup result
- `pico-cli doctor` result and process exit status
- project context result when `local` scope was selected
- unresolved warnings, blocked steps, and their `nextAction` values
- requirement to start a new Agent session

For additional command details, use the installed CLI help:

```shell
pico-cli setup --help
pico-cli doctor --help
pico-cli project context doctor --help
```
