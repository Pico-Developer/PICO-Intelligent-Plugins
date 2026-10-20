#!/usr/bin/env node

export const PICO_AGENT_HOOK_FAILURE_MODE = 'non-blocking';

try {
  const { runAgentHookWrapper } = await import('./runtime.mjs');
  await runAgentHookWrapper({ host: "traecli", wrapperUrl: import.meta.url, stage: process.argv[2] });
} catch {
  // Telemetry is observational and must never block the Host operation.
}
