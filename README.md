# PICO Intelligence Plugins

This repository root is a marketplace container for PICO intelligence plugins.

## Current Plugins

- [`pico-spatial-agentic-tools`](pico-spatial-agentic-tools/): plugin manifests, reusable skills, and MCP configuration for PICO OS spatial app development.
- [`pico-unity-agentic-tools`](pico-unity-agentic-tools/): plugin manifests, reusable skills, and MCP configuration for PICO Unity development.

Host marketplace manifests at the root expose both plugin payloads to each supported agent platform. Select the platform that matches the project:

- `spatial` installs `pico-spatial-agentic-tools`.
- `unity` installs `pico-unity-agentic-tools`.

## Recommended Developer Setup

Use `pico-cli` to register this marketplace before starting your agent session. The setup flow currently supports Claude Code, Cursor, Codex, GitHub Copilot, and Trae CLI.

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

Install Node.js 18+ and the agent host you plan to use. Make sure the host CLI is available on `PATH`:

- Claude Code: `claude`
- Cursor: Cursor IDE
- Codex: `codex`
- GitHub Copilot: `copilot`
- Trae CLI: `traecli`

Install `pico-cli`:

```bash
npm install -g @picoxr/pico-cli
```

### 2. Run guided setup

The recommended path is the interactive setup flow:

```bash
pico-cli setup
```

`pico-cli setup` shows a plan, lets you choose supported agent hosts and a resource scope, and configures the hosts that are available on your machine. The scope defaults to `global` in the prompt. Choose `local` to link plugin context only from a specific project. Missing optional host CLIs are skipped with guidance; install that host later and rerun setup when needed.

For non-interactive or host-specific setup, pass explicit options:

```bash
# PICO Spatial SDK
pico-cli setup --agent-tool claude-code --platform spatial --scope global --yes
pico-cli setup --agent-tool cursor --platform spatial --scope global --yes
pico-cli setup --agent-tool codex --platform spatial --scope global --yes
pico-cli setup --agent-tool copilot --platform spatial --scope global --yes
pico-cli setup --agent-tool traecli --platform spatial --scope global --yes
pico-cli setup --agent-tool all --platform spatial --scope global --yes

# PICO Unity
pico-cli setup --agent-tool claude-code --platform unity --scope global --yes
pico-cli setup --agent-tool cursor --platform unity --scope global --yes
pico-cli setup --agent-tool codex --platform unity --scope global --yes
pico-cli setup --agent-tool copilot --platform unity --scope global --yes
pico-cli setup --agent-tool traecli --platform unity --scope global --yes
pico-cli setup --agent-tool all --platform unity --scope global --yes

# Project-local setup
pico-cli setup --agent-tool claude-code --platform unity --scope local --project /absolute/path/to/project --yes
```

`global` installs user-level plugin resources that can be used across projects and is also the default when `--yes` is used without `--scope`. `local` links plugin context for the directory passed with `--project`, or for the current directory when `--project` is omitted.

For Codex, this marketplace uses the workspace/local marketplace layout at `.agents/plugins/marketplace.json`; setup registers the marketplace and installs the selected plugin.

For Cursor, setup currently installs this plugin as a local plugin using the checked-in `.cursor-plugin` manifests. For Trae CLI, setup adds this repository as a local marketplace and installs or upgrades the plugin from that marketplace.

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

## License, Security, and Privacy

- License: Apache-2.0, see `LICENSE`.
- Security reporting: see `SECURITY.md`.
- Privacy and local support bundles: see `PRIVACY.md`.

Unless otherwise noted, all marketplace manifests, plugin manifests, skills, examples, and bundled references in this marketplace are licensed under Apache-2.0.
