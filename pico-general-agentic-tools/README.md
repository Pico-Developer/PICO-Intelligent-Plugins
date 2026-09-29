# PICO General Agentic Tools

Cross-platform agentic tools shared by PICO Spatial and Unity development workflows. This plugin holds the skills that are not specific to one PICO development target.

## Contents

- **Skills** (`skills/`):
  - `knowledge-query` — interactive knowledge-graph lookup for PICO development questions. It asks which platform's knowledge to query, then delegates the whole query flow to a disposable subagent so the main conversation's context window stays clean.

This plugin declares no MCP servers of its own. `knowledge-query` uses the `pico-dev-knowledge` server that the platform plugin (`pico-spatial-agentic-tools` or `pico-unity-agentic-tools`) contributes, and reads the installed knowledge sets through `pico-cli knowledge list`. When those are absent, the skill reports the limitation instead of guessing.

## Installation

You do not select this plugin during setup. `pico-cli setup` installs it automatically alongside the platform plugin you choose, for the same agent host and resource scope:

```sh
pico-cli setup --platform spatial
pico-cli setup --platform unity
```

See the marketplace root README for the supported agent hosts, the `--agent-tool` values, and each host's install mechanism.

## Host Integration Points

The recommended path is `pico-cli setup`. If you manually inspect or import this plugin, use these standard entrypoints:

- Claude Code: `.claude-plugin/plugin.json`
- Codex: `.codex-plugin/plugin.json`
- Cursor: `.cursor-plugin/plugin.json`
- GitHub Copilot (and GitHub Workflow integrations): `.github/plugin/plugin.json`
- CodeBuddy Code: `.codebuddy-plugin/plugin.json`
- Qoder CLI: `.qoder-plugin/plugin.json`
- Grok CLI: `.grok-plugin/plugin.json`; Grok discovers `skills/` by convention, so its manifest declares only plugin identity
- Antigravity CLI: the plugin-level `plugin.json` at this directory's root
- Trae CLI: local marketplace installation driven by `pico-cli setup` / `pico-cli plugin update`
- OpenCode V2: no plugin manifest; `pico-cli setup` writes Skills into the OpenCode configuration

Hosts should import this directory as the plugin root and resolve `skills/` using the relative paths defined in the host manifest.

See `AGENTS.md` for agent guidance.

## License

Apache-2.0
