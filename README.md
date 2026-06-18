# PICO Intelligence Plugins

This repository root is a marketplace container for PICO intelligence plugins.

## Current Plugins

- [`pico-spatial-agentic-tools`](pico-spatial-agentic-tools/): plugin manifests, reusable skills, and MCP configuration for PICO OS spatial app development.

Host marketplace manifests at the root point each supported agent platform to the plugin payload under `pico-spatial-agentic-tools/`.

## Recommended Developer Setup

Use `pico-cli` to register this marketplace before starting your agent session. The setup flow currently supports Claude Code, Cursor, Codex, GitHub Copilot, and Trae CLI.

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

`pico-cli setup` shows a plan, lets you choose supported agent hosts, and configures the hosts that are available on your machine. Missing optional host CLIs are skipped with guidance; install that host later and rerun setup when needed.

For non-interactive or host-specific setup, pass explicit options:

```bash
pico-cli setup --tool claude-code --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool cursor --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool codex --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool copilot --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool traecli --plugin pico-spatial-agentic-tools --yes
pico-cli setup --tool all --plugin pico-spatial-agentic-tools --yes
```

For Codex, this marketplace uses the workspace/local marketplace layout at `.agents/plugins/marketplace.json`; setup registers the marketplace and installs the selected plugin.

For Cursor, setup currently installs this plugin as a local plugin using the checked-in `.cursor-plugin` manifests. For Trae CLI, setup adds this repository as a local marketplace and installs or upgrades the plugin from that marketplace.

### 3. Start a new agent session

After setup, close and reopen the configured host or start a new agent session from your project directory. The new session should load the marketplace manifests, `pico-spatial-agentic-tools` skills, and MCP servers.

For detailed host notes, update commands, Codex marketplace layout, and MCP startup details, see [`pico-spatial-agentic-tools/README.md`](pico-spatial-agentic-tools/README.md).

## License, Security, and Privacy

- License: Apache-2.0, see `LICENSE`.
- Security reporting: see `SECURITY.md`.
- Privacy and local support bundles: see `PRIVACY.md`.

Unless otherwise noted, all marketplace manifests, plugin manifests, skills, examples, and bundled references in this marketplace are licensed under Apache-2.0.
