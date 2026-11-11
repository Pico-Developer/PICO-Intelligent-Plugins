# PICO Intelligence Plugins

This repository root is a marketplace container for PICO intelligence plugins.

## Current Plugins

- [`pico-spatial-agentic-tools`](pico-spatial-agentic-tools/): project guidance and reusable skills for PICO OS spatial app development.
- [`pico-unity-agentic-tools`](pico-unity-agentic-tools/): project guidance and reusable skills for PICO Unity development.
- [`pico-general-agentic-tools`](pico-general-agentic-tools/): the entry plugin installed once per user; its `pico-project-setup` Skill configures the matching platform plugin into each project. It owns the user-level `pico-dev-knowledge`, `pico-spatial-editor`, and `unity-mcp` servers.

Host marketplace manifests at the root expose all three plugin payloads. Run `pico-cli setup` once for the user-level general plugin, then configure the platform that matches each project:

- `pico-cli project configure --platform spatial` installs project resources from `pico-spatial-agentic-tools`.
- `pico-cli project configure --platform unity` installs project resources from `pico-unity-agentic-tools`.

## Recommended Developer Setup

Use `pico-cli` to configure one or more supported hosts before starting your agent session. The setup flow supports every host listed under prerequisites below.

### Install with an AI coding agent

Copy the following instruction into your AI coding agent. The linked guide is written as an executable workflow: the agent inspects the environment, confirms the target and write scope, shows the final setup command for approval, runs setup, and verifies the result.

```text
Read and follow the PICO CLI Installation and Setup Guide for AI Agents:
https://github.com/Pico-Developer/PICO-Intelligent-Plugins/blob/main/docs/pico-cli-installation-guide.md

Inspect my environment first. Confirm the supported Agent tools and the complete setup command
with me before making changes. After setup, run the guide's read-only checks and report the
results.
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

`pico-cli setup` runs once per user. It shows a plan, lets you choose supported agent hosts, and installs the general PICO plugin (knowledge query and project setup) for each host at the user level, together with shared developer tools. It writes nothing into a project. A selected host whose CLI is missing is reported as failed with a retry command, and that run removes no hosts; install the host CLI, then rerun the command.

The PICO Spatial and PICO Unity plugins are installed per project. When you start PICO work in a project, the general plugin's `pico-project-setup` Skill detects the platform and runs `pico-cli project configure` for the current host. You can also run it yourself:

```bash
# User-level setup. Pass any --agent-tool value from the list above.
pico-cli setup --agent-tool claude-code --region row --yes

# Several hosts at once. The list is the complete set of hosts for this user.
pico-cli setup --agent-tool codex traecli --region row --yes

# Install the platform plugin into a project for the hosts set up above.
pico-cli project configure --platform spatial --project /absolute/path/to/project --yes
pico-cli project configure --platform unity --project /absolute/path/to/project --agent-tool claude-code --yes
```

`--region` selects where downloads and services are routed: `cn` for the Chinese mainland, `row` for the rest of the world, or `us` for the United States. Non-interactive setup requires it until a region has been saved by an earlier setup.

`--agent-tool` passed to setup is the complete set of hosts for the user; a host configured earlier and omitted from the list is removed. `project configure` defaults to every host that has the general plugin, and `--agent-tool current` selects the host it runs in.

Hosts differ in how setup delivers the plugin:

- Claude Code and GitHub Copilot: setup registers or refreshes the marketplace and installs or updates the plugin.
- Codex: this marketplace uses the workspace/local marketplace layout at `.agents/plugins/marketplace.json`; setup registers the marketplace and installs the selected plugin.
- Cursor: setup installs the plugin locally using the checked-in `.cursor-plugin` manifests, because the public Cursor marketplace flow is not used yet.
- Trae CLI and CodeBuddy Code: setup adds this repository as a local marketplace and installs or upgrades the plugin from that marketplace.
- Qoder CLI, Antigravity CLI, and Grok CLI: setup installs or updates the plugin from a prepared local bundle. Grok installs it as a trusted plugin so its Skills and MCP servers activate.
- OpenCode V2: setup writes Skills and MCP configuration into the OpenCode configuration you already use, rather than installing a host plugin.
- Trae IDE is not supported: it does not read the Trae CLI marketplace that setup uses. See the [installation guide](docs/pico-cli-installation-guide.md#trae-ide).

### Manual Codex MCP configuration

The recommended `pico-cli setup` flow installs the user-level general plugin. Its Codex manifest
loads MCP definitions from the plugin's `.mcp.json`; setup does not require duplicating them in
`[mcp_servers.*]` TOML tables. If you intentionally configure standalone MCP servers instead of
using the plugin, translate each server entry into the corresponding `mcp_servers` table in the
Codex configuration. Do not copy the `.mcp.json` wrapper verbatim or duplicate plugin-owned servers.

### 3. Load resources and continue

After first setup or changes to general's MCP entries, load and approve the general plugin as
required by the Host. Follow the reported `hostActions` for trust and resource discovery. Project
configure returns platform guidance and Skill paths that the agent can read to continue the task
in the same session. Verify the general plugin's required MCP tools separately; reconnect or reload
only when the Host requires it to make those tools available.

For plugin-specific capabilities and setup notes, see:

- [`pico-spatial-agentic-tools/README.md`](pico-spatial-agentic-tools/README.md)
- [`pico-unity-agentic-tools/README.md`](pico-unity-agentic-tools/README.md)
- [`pico-general-agentic-tools/README.md`](pico-general-agentic-tools/README.md) — the user-level entry plugin: project setup, `pico-cli` usage, and PICO knowledge querying

## License, Security, and Privacy

- License: Apache-2.0, see `LICENSE`.
- Security reporting: see `SECURITY.md`.
- Privacy: see `PRIVACY.md`.

Unless otherwise noted, all marketplace manifests, plugin manifests, skills, examples, and bundled references in this marketplace are licensed under Apache-2.0.
