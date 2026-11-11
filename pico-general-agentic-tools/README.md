# PICO General Agentic Tools

The entry plugin for PICO development with AI agents. `pico-cli setup` installs it once per user, and
it works in every directory: outside a project, in a PICO Spatial project, and in a PICO Unity project.
Platform plugins are configured into each project from here, so one setup covers every project and SDK.

## Contents

- **Skills** (`skills/`):
  - `pico-project-setup` — detects whether the working directory is a Spatial or Unity project, configures the matching platform plugin into the project for the current agent host with `pico-cli project configure`, and continues the original task in the same session.
  - `pico-cli` — generic `pico-cli` usage: command discovery, command-family selection, output formats, device targeting, safe defaults, managed sub-CLIs, and command-level emulator, device, app, capture, log, perf, and SpatialML usage.
  - `pico-aps-cli` — regional APS credit balance, recharge-page, and transaction-history workflows.
  - `pico-auth-cli` — safe regional PICO browser authorization, login-state, refresh, and logout workflows.
  - `pico-sgs-cli` — guarded regional PICO Spatial Generation Service workflows for 3D and image generation, task status, monitoring, and artifact downloads.
  - `pico-release-cli` — regional VibeLab app configuration, asset, draft, deploy-key, review, status, offlining, and deletion workflows.
  - `release-to-vibelab` — end-to-end project detection, publishing-asset preparation, GitHub repository and Deploy Key setup, VibeLab draft upload, legal confirmation, and review submission across Auth and Release.
  - `knowledge-query` — interactive knowledge-graph lookup for PICO development questions. It uses the requested or configured knowledge target and asks only when a choice is needed, then delegates the whole query flow to a disposable subagent so the main conversation's context window stays clean.
- **MCP** (`.mcp.json`):
  - `pico-dev-knowledge` — the knowledge graph served by `pico-cli knowledge:server`, using the project's selection when present and the user-level selection otherwise.
  - `pico-spatial-editor` — the Spatial Editor / 3D workflow backend, available globally in every session; it reports a structured `not-in-spatial-project` degradation when the working directory is not a Spatial project.
  - `unity-mcp` — the Unity Editor bridge backend driven through the local Unity relay. When the relay cannot start, it exposes `get_unity_relay_status` with initialization guidance. After preparation, reconnect this MCP through the Host and verify the native Editor tools; relay presence alone does not prove readiness.

Load the general plugin once after first installation or an upgrade that changes its MCP entries. Later project configuration does not require a session restart to use these servers — they are user-level and start even without a configured project. Host approval, project trust, Editor installation/readiness, and platform-specific setup remain separate requirements that the servers surface through structured degradation hints rather than generic errors.

Managed CLI availability is release-, distribution-, and region-specific. Skill names stay stable
across regions; each Skill resolves its stable tool ID through the active pico-cli catalog instead
of hardcoding a regional package or command.

## Installation

Run setup once per user; it installs this plugin for the agent hosts you choose. Setup needs a
download region, and you choose it in one of two ways:

```sh
# Interactive: the wizard asks which region to use.
pico-cli setup

# Non-interactive: pass the region explicitly. One of cn (Chinese mainland), row (rest of world), us.
pico-cli setup --yes --region cn
```

Then open a project in your agent host and ask for PICO development work. `pico-project-setup`
configures the Spatial or Unity platform plugin into that project. When the agent session was opened
at a workspace root above the project directory, it passes `--workspace-root <dir>` so Host
resources land where the session actually loads them. Switching knowledge versions uses
`pico-cli knowledge pull <version>` and `pico-cli knowledge use <version>` and needs no setup
re-run.

See the marketplace root README for the supported agent hosts, the `--agent-tool` values, and each host's install mechanism.

## Host Integration Points

The recommended path is `pico-cli setup`. If you manually inspect or import this plugin, use these standard entrypoints:

- Claude Code: `.claude-plugin/plugin.json`
- Codex: `.codex-plugin/plugin.json`
- Cursor: `.cursor-plugin/plugin.json`
- GitHub Copilot (and GitHub Workflow integrations): `.github/plugin/plugin.json`
- CodeBuddy Code: `.codebuddy-plugin/plugin.json`
- Qoder CLI: `.qoder-plugin/plugin.json`
- Grok CLI: `.grok-plugin/plugin.json`; Grok discovers `skills/` and MCP by convention, so its manifest declares only plugin identity
- Antigravity CLI: the plugin-level `plugin.json` at this directory's root
- Trae CLI: local marketplace installation driven by `pico-cli setup` / `pico-cli plugin update`
- OpenCode V2: no plugin manifest; `pico-cli setup` writes Skills and MCP entries into the OpenCode configuration
- Plugin MCP source: `.mcp.json`; the Host loads the public defaults, while `pico-cli setup` materializes channel- and region-specific values for managed installations. Do not directly import an internal-channel `.mcp.json` as a portable ROW/US configuration.

To update the Trae CLI records explicitly:

```bash
# Update the user-level general plugin and the platform plugin of the project containing the current directory.
pico-cli plugin update --agent-tool traecli

# Select the project explicitly.
pico-cli plugin update --agent-tool traecli --project /absolute/path/to/project
```

`plugin update` always covers the general plugin at the user level. When the resolved project has a
recorded configuration, it also refreshes that project's platform plugin. Without `--project` it
uses the configured project that contains the current directory. It refreshes only plugins that are
already recorded.

Hosts should import this directory as the plugin root and resolve `skills/` and `.mcp.json` using the relative paths defined in the host manifest.

See `AGENTS.md` for agent guidance.

## License

Apache-2.0

## Shared device and environment tools

General also owns `pico-env-doctor`, `pico-emulator-usage`, `pico-cli-device-target`, `pico-cli-screenshot`, and `capture-camera`. They support standalone tools and configured Spatial or Unity projects. Device operations require a compatible target; they do not require the Spatial platform plugin. SDK implementation still belongs to the project’s platform plugin.

### Updating an existing installation after this migration

Use the CLI and plugin release from the same supported channel. `pico-cli plugin update --project "<resource-root>"` updates the user-level general plugin and the recorded project platform plugin together; use the root reported by project detection. For a standalone installation with no project, use the user-level update path shown by `pico-cli plugin update --help`. Read the updated project Skill files to continue. Verify required MCP tools separately and reconnect or reload only if needed. Do not manually retain a second copy of the moved Skills in the platform plugin.
