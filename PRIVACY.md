# Privacy and Local Support Bundles

This marketplace provides agent skills and MCP configuration for PICO Spatial SDK development. The plugin does not intentionally upload prompts, tool calls, project files, logs, or support bundles to PICO services by itself.

## Local plugin audit bundles

The `pico-spatial-agentic-tools` plugin includes a user-triggered support workflow for setup and visibility debugging:

```bash
pico-cli plugin audit
```

The command writes a local bundle under `.pico-spatial-agentic-tools/plugin-audit/` by default. Without explicit transcript authorization, the bundle is metadata-only and is designed to avoid raw prompts, source files, tool arguments, tool outputs, device logs, screenshots, and session transcripts.

Generated files may include plugin manifest metadata, MCP configuration metadata, skill names, environment metadata such as platform and Node.js version, and user-run command suggestions. The bundle is not uploaded automatically. Review `summary.md` and `redaction-notes.md` before sharing anything externally.

## Session transcripts and debug logs

Session transcripts and host debug logs can contain prompts, source code, file contents, tool outputs, MCP payloads, local paths, and credentials accidentally pasted into the session. They are included only when the user explicitly runs `pico-cli plugin audit --transcript --yes`. In that mode, the bundle writes `session-transcript.jsonl`, `pico-spatial-agentic-tools-usage.json`, and `pico-spatial-agentic-tools-usage.md` locally and still does not upload anything automatically.

Review and redact transcript exports before sharing them externally.

## MCP servers

The public plugin starts MCP servers through the public npm package:

```bash
npx -y @picoxr/pico-cli mcp:dev-knowledge
```

Public marketplace releases must not contain private package scopes, private registries, private repository URLs, or internal service URLs.

## User responsibility

Review generated code, local support bundles, logs, traces, screenshots, and device artifacts before sharing them. Do not include confidential source code, credentials, private repository URLs, access tokens, device identifiers, or unreleased product information in public issues or support requests.
