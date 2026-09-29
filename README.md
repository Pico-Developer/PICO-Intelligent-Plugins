# PICO Intelligence Plugins

This repository root is a marketplace container for PICO intelligence plugins.

## Current Plugins

- [`pico-spatial-agentic-tools`](pico-spatial-agentic-tools/): plugin manifests, reusable skills, and MCP configuration for PICO OS spatial app development.
- [`pico-unity-agentic-tools`](pico-unity-agentic-tools/): plugin manifests, reusable skills, and MCP configuration for PICO Unity development.
- [`pico-general-agentic-tools`](pico-general-agentic-tools/): shared skills installed alongside either platform plugin.

Host marketplace manifests at the root expose all three plugin payloads to each supported agent platform. Select the platform that matches the project:

- `spatial` installs `pico-spatial-agentic-tools` and `pico-general-agentic-tools`.
- `unity` installs `pico-unity-agentic-tools` and `pico-general-agentic-tools`.

## Recommended Developer Setup

Use `pico-cli` to configure one or more supported hosts before starting your agent session. The setup flow supports every host listed under prerequisites below.

### Install with an AI coding agent

Copy the following instruction into your AI coding agent. The linked guide is written as an executable workflow: the agent inspects the environment, confirms the target and write scope, shows the final setup command for approval, runs setup, and verifies the result.

```text
Read and follow the PICO CLI Installation and Setup Guide for AI Agents:
https://github.com/Pico-Developer/PICO-Intelligent-Plugins/blob/main/docs/pico-cli-installation-guide.md

Inspect this project and my environment first. Confirm the project directory, setup scope,
development target, supported Agent tool, and complete setup command with me before making
changes. After setup, run the guide's read-only checks and report the results.
```

You can also [read the installation guide in this repository](docs/pico-cli-installation-guide.md).

### 1. Install prerequisites

Install Node.js 20+ and the agent host you plan to use. Make sure the host CLI is available on `PATH`. The `--agent-tool` value is on the left, the CLI it needs on the right:

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — `claude-code`: `claude`
- [Cursor](https://cursor.com) — `cursor`: Cursor IDE
- [Codex](https://developers.openai.com/codex/) — `codex`: `codex`
- [GitHub Copilot](https://docs.github.com/en/copilot) — `copilot`: `copilot`
- [Trae CLI](https://www.trae.ai/) — `traecli`: `traecli`
- [OpenCode V2](https://opencode.ai/v2/docs/skills/) — `opencode2`: `opencode2`, or the official `opencode` command when it reports version 2.x
- [CodeBuddy Code](https://www.codebuddy.ai/docs/cli/plugins-reference) — `codebuddy`: `codebuddy`
- [Qoder CLI](https://docs.qoder.com/cli/plugins) — `qoder`: `qoder`
- [Antigravity CLI](https://antigravity.google/docs/cli/plugins) — `antigravity`: `agy`
- [Grok CLI](https://docs.x.ai/build/features/skills-plugins-marketplaces) — `grok`: `grok`

Install `pico-cli`:

```bash
npm install -g @picoxr/pico-cli
```

### 2. Run guided setup

The recommended path is the interactive setup flow:

```bash
pico-cli setup
```

`pico-cli setup` shows a plan, lets you choose supported agent hosts and a resource scope, and configures the hosts that are available on your machine. The scope defaults to `global` in the prompt. Choose `local` to configure one project: setup links the host context, copies the selected plugins' skills, and reconciles that host's project MCP configuration. Missing optional host CLIs are skipped with guidance; install that host later and rerun setup when needed.

For non-interactive or host-specific setup, pass explicit options:

```bash
# PICO Spatial SDK. Pass any --agent-tool value from the list above.
pico-cli setup --agent-tool claude-code --platform spatial --scope global --yes

# Several hosts at once, or every host available on this machine.
pico-cli setup --agent-tool codex traecli --platform spatial --scope global --yes
pico-cli setup --agent-tool all --platform spatial --scope global --yes

# PICO Unity
pico-cli setup --agent-tool claude-code --platform unity --scope global --yes
pico-cli setup --agent-tool all --platform unity --scope global --yes

# Project-local setup
pico-cli setup --agent-tool claude-code --platform unity --scope local --project /absolute/path/to/project --yes
```

`global` installs user-level plugin resources that can be used across projects and is also the default when `--yes` is used without `--scope`. `local` writes project-scoped context, skills, and MCP configuration for the directory passed with `--project`, or for the current directory when `--project` is omitted.

Hosts differ in how setup delivers the plugin:

- Claude Code and GitHub Copilot: setup registers or refreshes the marketplace and installs or updates the plugin.
- Codex: this marketplace uses the workspace/local marketplace layout at `.agents/plugins/marketplace.json`; setup registers the marketplace and installs the selected plugin.
- Cursor: setup installs the plugin locally using the checked-in `.cursor-plugin` manifests, because the public Cursor marketplace flow is not used yet.
- Trae CLI and CodeBuddy Code: setup adds this repository as a local marketplace and installs or upgrades the plugin from that marketplace.
- Qoder CLI, Antigravity CLI, and Grok CLI: setup installs or updates the plugin from a prepared local bundle. Grok installs it as a trusted plugin so its Skills and MCP servers activate.
- OpenCode V2: setup writes Skills and MCP configuration into the OpenCode configuration you already use, rather than installing a host plugin.

### Manual Codex MCP configuration

The recommended `pico-cli setup` flow converts the plugin's `mcpServers`
definitions into Codex `[mcp_servers.*]` TOML tables automatically. If you
bypass setup and configure Codex manually, do not copy the `.mcp.json` wrapper
verbatim; translate each server entry into the corresponding `mcp_servers`
table in the Codex configuration.

### 3. Start a new agent session

After setup, close and reopen the configured host or start a new agent session from your project directory. The new session should load the marketplace manifests and the skills and MCP servers for the selected plugin.

For plugin-specific capabilities and setup notes, see:

- [`pico-spatial-agentic-tools/README.md`](pico-spatial-agentic-tools/README.md)
- [`pico-unity-agentic-tools/README.md`](pico-unity-agentic-tools/README.md)
- [`pico-general-agentic-tools/README.md`](pico-general-agentic-tools/README.md) — cross-platform skills, installed automatically alongside whichever platform plugin you choose

## License, Security, and Privacy

- License: Apache-2.0, see `LICENSE`.
- Security reporting: see `SECURITY.md`.
- Privacy: see `PRIVACY.md`.

Unless otherwise noted, all marketplace manifests, plugin manifests, skills, examples, and bundled references in this marketplace are licensed under Apache-2.0.
