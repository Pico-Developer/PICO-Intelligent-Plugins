## Self-heal rules and safe defaults

- Verify before fixing; re-verify after each fix.
- Discover the installed command surface before using doctor-style commands.
- Strongly recommend updating `pico-cli` within the current channel before `setup` or `plugin update` when it is outdated. Preserve explicit pins and deferred updates; continue supported work without upgrading the business SDK.
- Treat embedded plugin-doctor findings as diagnostic guidance while accounting
  for root doctor's conditional catalog-cache effects. Execute the
  finding-specific setup, project configure, or plugin update command explicitly,
  then rerun doctor once.
- For a Spatial SDK project task, confirm the PICO development knowledge line
  (`.pico-env.json` `agentVaultWorkspace`) matches the project SDK `major.minor`
  only on the authorized doctor path. Under the strictly read-only fallback,
  report the recorded values as non-authoritative and leave alignment unverified.
- Reuse the complete report and task-specific readiness evidence within the same host session; unrelated findings do not force repeated diagnosis.
- Do not run repair commands without explicit user authorization or a task that
  clearly requires setup/update/start behavior.
- Verify the required skills and callable MCP tools after changes. Prefer the
  Host's supported discovery or affected MCP reconnect; require a session reload
  only when the Host needs it to register the changed resources.
- Do not hand-edit host plugin manifests unless `pico-cli setup` cannot support
  the host and the user explicitly asks for manual setup guidance.

