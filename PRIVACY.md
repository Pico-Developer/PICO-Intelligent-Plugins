# Privacy

This marketplace provides agent skills and MCP configuration for PICO Spatial SDK and PICO Unity development. The plugins do not intentionally upload prompts, tool calls, project files, logs, or other support artifacts to PICO services by themselves.

## MCP servers

The public plugins start their `pico-cli`-backed MCP servers through the public npm package. For example, the development knowledge server uses:

```bash
npx -y @picoxr/pico-cli knowledge:server
```

Public marketplace releases must not contain private package scopes, private registries, private repository URLs, or internal service URLs.

## User responsibility

Review generated code, logs, traces, screenshots, and device artifacts before sharing them. Do not include confidential source code, credentials, private repository URLs, access tokens, device identifiers, or unreleased product information in public issues or support requests.
