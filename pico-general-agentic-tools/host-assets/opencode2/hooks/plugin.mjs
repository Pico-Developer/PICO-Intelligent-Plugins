/*
 * Copyright 2026 PICO Immersive Pte. Ltd.
 * SPDX-License-Identifier: Apache-2.0
 */

import { spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

export const PICO_AGENT_HOOK_FAILURE_MODE = 'non-blocking';

const pluginDirectory = path.dirname(fileURLToPath(import.meta.url));
const captureCaller = true;
const managedSkillPath =
  /(?:^|\/)[.]opencode\/skills\/[a-z0-9]+(?:-[a-z0-9]+)*\/(?:SKILL[.]md|scripts\/.+)$/iu;
const managedMcpServers = ["pico-spatial-editor","pico-dev-knowledge","unity-mcp"];

export function managedSkillFile(filePath) {
  if (typeof filePath !== 'string') return false;
  const portablePath = filePath.replaceAll('\\', '/');
  if (portablePath.split('/').includes('..')) return false;
  return managedSkillPath.test(portablePath);
}

function managedMcpTool(tool) {
  if (typeof tool !== 'string') return;
  for (const serverId of managedMcpServers) {
    const prefix = `${serverId}_`;
    if (!tool.startsWith(prefix) || tool.length === prefix.length) continue;
    const toolName = tool.slice(prefix.length).replaceAll('-', '_');
    if (/^[a-z0-9_]+$/iu.test(toolName)) return `mcp__${serverId}__${toolName}`;
  }
}

function forwardRelevantTool(event) {
  if (event?.status !== 'completed' && event?.status !== 'error') return;
  const filePath = event?.input?.path;
  const isSkillRead =
    event.tool === 'read' && event.status === 'completed' && managedSkillFile(filePath);
  const mcpTool = managedMcpTool(event?.tool);
  if (!isSkillRead && !mcpTool) return;
  try {
    const child = spawn('node', [path.join(pluginDirectory, 'ingest.mjs')], {
      detached: process.platform !== 'win32',
      stdio: ['pipe', 'ignore', 'ignore'],
      windowsHide: true,
    });
    child.on('error', () => undefined);
    child.stdin.on('error', () => undefined);
    child.stdin.end(
      JSON.stringify({
        hook_event_name: event.status === 'error' ? 'PostToolUseFailure' : 'PostToolUse',
        session_id: event.sessionID,
        turn_id: event.id,
        tool_use_id: event.id,
        tool_name: mcpTool ?? event.tool,
        tool_input: isSkillRead ? { path: filePath } : event.input,
      }),
    );
    child.unref();
  } catch {
    // Observation must never affect OpenCode tool execution.
  }
}

async function currentOpenCodeContext(ctx, sessionID) {
  const controller = new AbortController();
  let onAbort;
  const timer = setTimeout(() => controller.abort(), 500);
  try {
    return await Promise.race([
      Promise.all([
        ctx.session.context({ sessionID }, { signal: controller.signal }),
        ctx.session.get({ sessionID }, { signal: controller.signal }),
      ]),
      new Promise((resolve) => {
        onAbort = () => resolve(undefined);
        controller.signal.addEventListener('abort', onAbort, { once: true });
      }),
    ]);
  } finally {
    clearTimeout(timer);
    if (onAbort) controller.signal.removeEventListener('abort', onAbort);
    controller.abort();
  }
}

export default {
  id: 'pico-general-agentic-tools',
  async setup(ctx) {
    try {
      await ctx.tool.hook('execute.after', forwardRelevantTool);
      const pendingShells = new Map();
      if (captureCaller)
        await ctx.shell.hook('create.before', (event) => {
          if (!event?.env || typeof event.env !== 'object') return;
          // Native SDK provenance blocks an outer snapshot even if this tool has no receipt.
          event.env.PICO_WORKFLOW_CALLER_HOST = 'opencode2';
          const identity = pendingShells.get(event.command);
          if (!identity) return;
          pendingShells.delete(event.command);
          if (Date.now() > identity.expiresAt) return;
          event.env.PICO_WORKFLOW_OPENCODE_RECEIPT = identity.receipt;
          event.env.OPENCODE_SESSION_ID = identity.sessionID;
        });
      if (captureCaller)
        await ctx.tool.hook('execute.before', async (event) => {
          try {
            if (event.tool !== 'bash' && event.tool !== 'shell') return;
            const { directReceiptInvocation, runWorkflowCallerContextHook } = await import(
              pathToFileURL(path.join(pluginDirectory, 'capture-context.mjs')).href
            );
            if (!directReceiptInvocation(event)) return;
            const current = await currentOpenCodeContext(ctx, event.sessionID);
            if (!current) return;
            const [messages, session] = current;
            const matched = messages.filter((message) => message.id === event.messageID);
            if (matched.length !== 1) return;
            await runWorkflowCallerContextHook('opencode2', {
              input: Promise.resolve(
                JSON.stringify({
                  ...event,
                  message: matched[0],
                  cwd: event.input?.workdir ?? session.location.directory,
                }),
              ),
              timeoutMs: 2500,
              emit: (output) => {
                if (!output.modifiedArgs) return;
                const command = output.modifiedArgs.command;
                const receipt = / --caller-receipt-v1 ([a-f0-9]{64})$/.exec(command)?.[1];
                if (!receipt) return;
                for (const [key, pending] of pendingShells)
                  if (Date.now() > pending.expiresAt) pendingShells.delete(key);
                if (pendingShells.size >= 128) return;
                pendingShells.set(command, {
                  receipt,
                  sessionID: event.sessionID,
                  expiresAt: Date.now() + 30000,
                });
                event.input = output.modifiedArgs;
              },
            });
          } catch {
            // Caller capture is observational; unavailable SDKs, evidence and CLIs fail open.
          }
        });
    } catch {
      // Telemetry registration must never prevent OpenCode from starting.
    }
  },
};
