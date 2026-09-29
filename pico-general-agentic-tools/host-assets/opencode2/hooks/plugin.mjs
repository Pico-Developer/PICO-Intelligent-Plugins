import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const pluginDirectory = path.dirname(fileURLToPath(import.meta.url));
const managedSkillPath = /(?:^|[\/])[.]opencode[\/]skills[\/][a-z0-9]+(?:-[a-z0-9]+)*[\/](?:SKILL[.]md|scripts[\/].+)$/iu;
const managedMcpServers = ["pico-spatial-editor","pico-dev-knowledge"];

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
    event.tool === 'read' &&
    event.status === 'completed' &&
    managedSkillFile(filePath);
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
    child.stdin.end(JSON.stringify({
      hook_event_name: event.status === 'error' ? 'PostToolUseFailure' : 'PostToolUse',
      session_id: event.sessionID,
      turn_id: event.id,
      tool_use_id: event.id,
      tool_name: mcpTool ?? event.tool,
      tool_input: isSkillRead ? { path: filePath } : event.input,
    }));
    child.unref();
  } catch {
    // Observation must never affect OpenCode tool execution.
  }
}

export default {
  id: 'pico-general-agentic-tools',
  async setup(ctx) {
    await ctx.tool.hook('execute.after', forwardRelevantTool);
  },
};
