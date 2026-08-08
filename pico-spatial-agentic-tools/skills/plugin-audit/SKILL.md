---
name: plugin-audit
description: Create a local pico-spatial-agentic-tools support bundle for plugin setup, host visibility, skill discovery, or MCP registration issues. Default to metadata-only collection; include a Claude Code transcript and extracted skill/MCP usage records only when the user explicitly requests and authorizes transcript export.
license: 'Apache-2.0'
allowed-tools: Bash(pico-cli plugin audit *) Bash(claude --version) Bash(codex --version) Bash(copilot --version)
---

# PICO Plugin Audit

Use this skill when the user wants a local support bundle for plugin setup,
host visibility, skill discovery, or MCP registration issues.

The default bundle is metadata-only. Transcript and usage extraction are an
optional, higher-sensitivity branch.

Do **not** use the word `diagnose` as this skill's invocation name. Use `plugin-audit`.

## Default Metadata-Only Flow

Run from the user's project root:

```bash
pico-cli plugin audit
```

Report the bundle path and the metadata files listed in `summary.md`. Do not add
`--transcript` merely because the user invoked this skill.

## Optional Transcript Flow

Use transcript export only when the user explicitly asks to include, inspect, or
export a Claude Code session transcript or skill/MCP usage records derived from
that transcript.

Before exporting, tell the user:

- the transcript may contain prompts, source code, file contents, tool arguments, tool outputs, MCP payloads, local paths, and secrets accidentally pasted into the session;
- the export is local-only and not automatically uploaded;
- they should review `session-transcript.jsonl`, `pico-spatial-agentic-tools-usage.json`, and `redaction-notes.md` before sharing externally.

Only run transcript export after the user has authorized it. A generic request
to audit plugin setup or create a support bundle is not transcript
authorization. A request that explicitly asks to export or inspect the
transcript counts as authorization.

Then run:

```bash
pico-cli plugin audit --transcript --yes
```

If the user provides a specific Claude Code session id, use:

```bash
pico-cli plugin audit --session <session-id> --transcript --yes
```

For the transcript flow, report the exact output paths for:

- `session-transcript.jsonl`
- `pico-spatial-agentic-tools-usage.json`
- `pico-spatial-agentic-tools-usage.md`

## Output Bundle

By default, the command writes a timestamped directory under:

```text
.pico-spatial-agentic-tools/plugin-audit/
```

Important files:

- `summary.md`: bundle overview and file locations
- `manifest.json`: privacy flags and output file paths
- `session-transcript.jsonl`: authorized local transcript export with light token-pattern redaction
- `pico-spatial-agentic-tools-usage.json`: structured usage records extracted from the transcript
- `pico-spatial-agentic-tools-usage.md`: human-readable usage table
- `plugin-config.json`: plugin metadata and skill list
- `redaction-notes.md`: review guidance before sharing

## Privacy Rules

- Never upload the bundle automatically.
- Do not paste the full transcript into chat.
- Remind the user to review and redact before sharing.
- If no transcript is found, ask the user for a Claude Code session id or to run from the project directory that produced the session.
