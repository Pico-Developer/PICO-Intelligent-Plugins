/*
 * Copyright 2026 PICO. All rights reserved.
 *
 * NOTICE: All information contained herein is, and remains the property of PICO.
 * The intellectual and technical concepts contained herein are proprietary to PICO
 * and may be covered by patents, patents in process, and are protected by trade
 * secret or copyright law. Dissemination of this information or reproduction of
 * this material is strictly forbidden unless prior written permission is obtained
 * from PICO.
 */

import { spawn } from 'node:child_process';
import fsSync from 'node:fs';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DEFAULT_HOT_TIMEOUT_MS = 3_000;
const BACKGROUND_WARM_TIMEOUT_MS = 60_000;
const BACKGROUND_WARM_LOCK_TTL_MS = 5 * 60_000;
const BACKGROUND_WARM_ENV = 'PICO_CLI_HOOK_BACKGROUND_WARM';
const MAX_INPUT_BYTES = 256 * 1024;
const SKILL_TOKEN = /(^|\s)\$([a-z0-9]+(?:-[a-z0-9]+)*)(?=$|\s|[.,!?;:，。！？；：])/giu;
const CLI_PACKAGE = '@picoxr/pico-cli';
const CLI_REGISTRY = undefined;

export async function runAgentHookWrapper({ host, wrapperUrl, stage }) {
  const startedAt = Date.now();
  const wrapperPath = fileURLToPath(wrapperUrl);
  const catalogPath = path.join(path.dirname(wrapperPath), 'catalog.json');
  const wrapperDirectory = path.dirname(wrapperPath);
  const nestedTraeInstall =
    host === 'traecli' &&
    path.basename(path.resolve(wrapperDirectory, '../../..')) === '.trae' &&
    path.basename(path.resolve(wrapperDirectory, '../..')) === 'cli';
  const pluginRoot = resolvePluginRoot(host)?.trim();
  const nativePluginInstall =
    pluginRoot &&
    equivalentPath(
      ['codebuddy', 'grok', 'qoder'].includes(host)
        ? path.resolve(pluginRoot, 'hooks')
        : path.resolve(pluginRoot, 'host-assets', host, 'hooks'),
      wrapperDirectory,
    );
  const projectRoot = nativePluginInstall
    ? resolveGlobalProjectRoot(host)
    : path.resolve(wrapperDirectory, nestedTraeInstall ? '../../../..' : '../../..');
  const bundledLocalEntry = undefined;
  const localEntry = process.env.PICO_CLI_HOOK_ENTRY?.trim() || bundledLocalEntry;
  const executable = localEntry
    ? { command: process.execPath, prefixArgs: [] }
    : resolveNpxExecutable();
  const diagnosticDirectory = process.env.PICO_CLI_HOOK_DIAGNOSTIC_DIR?.trim();
  const testTimeoutMs = Number(process.env.PICO_CLI_HOOK_TEST_TIMEOUT_MS);
  const hotTimeoutMs =
    diagnosticDirectory && Number.isSafeInteger(testTimeoutMs) && testTimeoutMs > 0
      ? testTimeoutMs
      : DEFAULT_HOT_TIMEOUT_MS;
  const chunks = [];
  let inputBytes = 0;
  let childAttempt = 0;

  for await (const chunk of process.stdin) {
    inputBytes += chunk.length;
    if (inputBytes > MAX_INPUT_BYTES) return;
    chunks.push(chunk);
  }
  const input = await normalizeHostInput(host, stage, Buffer.concat(chunks), catalogPath);
  if (
    !input?.length ||
    !(await shouldForward(
      host,
      input,
      catalogPath,
      projectRoot,
      nativePluginInstall ? pluginRoot : undefined,
    ))
  )
    return;
  const commonArgs = [
    'telemetry',
    'ingest-hook',
    '--host',
    host,
    '--catalog',
    catalogPath,
    '--project-root',
    projectRoot,
  ];

  if (localEntry) {
    await run([localEntry, ...commonArgs], input, hotTimeoutMs);
    return;
  }

  const npxArgs = ['--yes', ...registryArgs()];
  const hotResult = await run(
    [...npxArgs, '--offline', CLI_PACKAGE, ...commonArgs],
    input,
    hotTimeoutMs,
  );
  if (hotResult === 'ok') return;
  startBackgroundWarm(wrapperPath);

  async function run(args, stdin, timeoutMs) {
    return new Promise((resolve) => {
      const attempt = ++childAttempt;
      let timedOut = false;
      let finished = false;
      let ingestCompleted = false;
      const stages = [];
      let stderrBuffer = '';
      const childSpawnStartedAt = Date.now();
      stages.push({
        stage: 'child-spawn-start',
        source: 'wrapper',
        atMs: childSpawnStartedAt,
        elapsedMs: childSpawnStartedAt - startedAt,
      });
      const child = spawn(executable.command, [...executable.prefixArgs, ...args], {
        env: { ...process.env, PICO_CLI_HOOK_STAGE_DIAGNOSTIC: '1' },
        stdio: ['pipe', 'ignore', 'pipe'],
        windowsHide: true,
        detached: process.platform !== 'win32',
      });
      const childSpawnedAt = Date.now();
      stages.push({
        stage: 'child-spawned',
        source: 'wrapper',
        atMs: childSpawnedAt,
        elapsedMs: childSpawnedAt - startedAt,
      });
      child.stderr?.setEncoding('utf8');
      child.stderr?.on('data', (chunk) => {
        stderrBuffer = `${stderrBuffer}${chunk}`.slice(-16 * 1024);
        const lines = stderrBuffer.split('\n');
        stderrBuffer = lines.pop() ?? '';
        for (const line of lines) {
          if (!line.startsWith('PICO_HOOK_STAGE ')) continue;
          try {
            const stage = JSON.parse(line.slice('PICO_HOOK_STAGE '.length));
            if (stage?.source !== 'cli' || typeof stage.stage !== 'string') continue;
            if (stage.stage === 'ingest-complete') ingestCompleted = true;
            if (diagnosticDirectory) stages.push(stage);
          } catch {
            // Ignore malformed diagnostic output.
          }
        }
      });
      const timer = setTimeout(async () => {
        if (finished) return;
        timedOut = true;
        finished = true;
        child.stdin.destroy();
        await terminateChildTree(child);
        child.stderr?.destroy();
        const outcome = ingestCompleted ? 'ok' : 'timeout';
        recordDiagnostic(attempt, {
          outcome,
          childPid: child.pid,
          timeoutMs,
          timedOut: true,
          ingestCompleted,
          stages,
        });
        resolve(outcome);
      }, timeoutMs);
      child.on('error', (error) => {
        if (finished) return;
        finished = true;
        clearTimeout(timer);
        recordDiagnostic(attempt, {
          outcome: 'spawn-error',
          error: String(error),
          childPid: child.pid,
          timeoutMs,
          stages,
        });
        resolve('failed');
      });
      child.on('close', (code) => {
        if (finished) return;
        finished = true;
        clearTimeout(timer);
        const outcome =
          timedOut && !ingestCompleted
            ? 'timeout'
            : code === 0 || ingestCompleted
              ? 'ok'
              : 'failed';
        recordDiagnostic(attempt, {
          outcome,
          exitCode: code,
          timedOut,
          ingestCompleted,
          childPid: child.pid,
          timeoutMs,
          stages,
        });
        resolve(outcome);
      });
      child.stdin.on('error', () => undefined);
      child.stdin.end(stdin);
    });
  }

  function recordDiagnostic(attempt, details) {
    if (!diagnosticDirectory) return;
    try {
      fsSync.mkdirSync(diagnosticDirectory, { recursive: true });
      const invocation = process.env.PICO_CLI_HOOK_DIAGNOSTIC_INVOCATION ?? 'unknown';
      const safeInvocation = invocation.replace(/[^a-z0-9._-]/giu, '_').slice(0, 64) || 'unknown';
      fsSync.writeFileSync(
        path.join(diagnosticDirectory, `${safeInvocation}-${process.pid}-${attempt}.json`),
        `${JSON.stringify({
          invocation,
          attempt,
          wrapperPid: process.pid,
          recordedAt: new Date().toISOString(),
          ...details,
        })}\n`,
        'utf8',
      );
    } catch {
      // Diagnostics must preserve the production Hook's fail-open behavior.
    }
  }
}

function resolveGlobalProjectRoot(host) {
  const hostRoot =
    host === 'claude-code'
      ? process.env.CLAUDE_PROJECT_DIR
      : host === 'cursor'
        ? process.env.CURSOR_PROJECT_DIR
        : undefined;
  return path.resolve(hostRoot?.trim() || process.cwd());
}

function resolvePluginRoot(host) {
  if (host === 'claude-code') return process.env.CLAUDE_PLUGIN_ROOT;
  if (host === 'cursor') return process.env.CURSOR_PLUGIN_ROOT;
  if (host === 'codex' || host === 'copilot' || host === 'traecli') return process.env.PLUGIN_ROOT;
  if (host === 'codebuddy') return process.env.CODEBUDDY_PLUGIN_ROOT;
  if (host === 'grok') return process.env.GROK_PLUGIN_ROOT;
  if (host === 'qoder') return process.env.QODER_PLUGIN_ROOT;
}

function equivalentPath(left, right) {
  try {
    return fsSync.realpathSync(left) === fsSync.realpathSync(right);
  } catch {
    return path.resolve(left) === path.resolve(right);
  }
}

async function normalizeHostInput(host, stage, input, catalogUrl) {
  if (host !== 'antigravity') return input;
  if (stage !== 'post') return undefined;
  let payload;
  let catalog;
  try {
    payload = JSON.parse(input.toString('utf8'));
    catalog = JSON.parse(await fs.readFile(catalogUrl, 'utf8'));
  } catch {
    return undefined;
  }
  const conversationId =
    typeof payload?.conversationId === 'string' ? payload.conversationId : undefined;
  const stepIdx = Number.isSafeInteger(payload?.stepIdx) ? payload.stepIdx : undefined;
  const toolName = normalizeAntigravityMcpTool(payload?.toolCall, catalog);
  if (!conversationId || stepIdx === undefined || !toolName) return undefined;
  return Buffer.from(
    JSON.stringify({
      session_id: conversationId,
      turn_id: String(stepIdx),
      tool_use_id: `${conversationId}:${stepIdx}`,
      hook_event_name:
        typeof payload.error === 'string' && payload.error ? 'PostToolUseFailure' : 'PostToolUse',
      tool_name: toolName,
    }),
  );
}

function normalizeAntigravityMcpTool(toolCall, catalog) {
  // Antigravity 1.2.8 reports MCP calls through this built-in tool. Keep this
  // adapter limited to the observed contract: guessing from other tool-name
  // shapes would weaken the unique catalog-ownership boundary.
  if (toolCall?.name !== 'call_mcp_tool') return undefined;
  const serverId = toolCall?.args?.ServerName;
  const toolName = toolCall?.args?.ToolName;
  if (typeof serverId !== 'string' || typeof toolName !== 'string') return undefined;
  return normalizeAntigravityMcpServerTool(serverId, toolName, catalog);
}

function normalizeAntigravityMcpServerTool(serverId, toolName, catalog) {
  if (!/^[a-z0-9]+(?:[-_][a-z0-9]+)*$/iu.test(serverId)) return undefined;
  if (!/^[a-z0-9_]+$/iu.test(toolName)) return undefined;
  const matches = catalogPlugins(catalog).flatMap((plugin) =>
    Array.isArray(plugin?.mcpServers)
      ? plugin.mcpServers
          .filter(
            (candidate) =>
              typeof candidate === 'string' &&
              candidate.replaceAll('-', '_').toLowerCase() ===
                serverId.replaceAll('-', '_').toLowerCase(),
          )
          .map((candidate) => `mcp__${candidate}__${toolName.toLowerCase()}`)
      : [],
  );
  return matches.length === 1 ? matches[0] : undefined;
}

async function shouldForward(host, input, catalogUrl, projectRoot, nativePluginRoot) {
  let payload;
  let catalog;
  try {
    payload = JSON.parse(input.toString('utf8'));
    catalog = JSON.parse(await fs.readFile(catalogUrl, 'utf8'));
  } catch {
    return false;
  }
  if (!payload || typeof payload !== 'object') return false;
  if (host === 'claude-code') return true;

  const eventName = payload.hook_event_name;
  if (['UserPromptSubmit', 'beforeSubmitPrompt'].includes(eventName)) {
    return hasCatalogSkillToken(payload.prompt, catalog);
  }
  if (host === 'codex') return shouldForwardCodex(payload, catalog, projectRoot);
  if (host === 'traecli') {
    return shouldForwardReadOrMcp(payload, catalog, projectRoot, '.trae/skills', {
      nativePluginRoot,
    });
  }
  if (host === 'cursor') return shouldForwardCursor(payload, catalog, projectRoot);
  if (host === 'copilot') {
    return shouldForwardReadOrMcp(payload, catalog, projectRoot, '.github/skills', {
      mcpHost: 'copilot',
    });
  }
  if (host === 'codebuddy') return shouldForwardCodeBuddy(payload, catalog, projectRoot);
  if (host === 'qoder')
    return shouldForwardClaudeCompatible(payload, catalog, projectRoot, '.qoder/skills');
  if (host === 'grok') return shouldForwardGrok(payload, catalog, projectRoot);
  if (host === 'opencode2') {
    return shouldForwardReadOrMcp(payload, catalog, projectRoot, '.opencode/skills', {
      readToolNames: ['read'],
      readPathFields: ['path'],
    });
  }
  if (host === 'antigravity') return isCatalogMcpPayload(payload, catalog);
  return false;
}

function shouldForwardClaudeCompatible(payload, catalog, projectRoot, skillsDirectory) {
  if (payload.tool_name === 'Skill') return true;
  return shouldForwardReadOrMcp(payload, catalog, projectRoot, skillsDirectory);
}

function shouldForwardCodeBuddy(payload, catalog, projectRoot) {
  if (payload.tool_name === 'DeferExecuteTool') {
    const nestedToolName = payload.tool_input?.toolName;
    if (typeof nestedToolName !== 'string') return false;
    return isCatalogMcpPayload({ ...payload, tool_name: nestedToolName }, catalog);
  }
  return shouldForwardClaudeCompatible(payload, catalog, projectRoot, '.codebuddy/skills');
}

function shouldForwardGrok(payload, catalog, projectRoot) {
  if (payload.tool_name === 'Skill') return true;
  if (typeof payload.tool_name === 'string' && !payload.tool_name.startsWith('mcp__')) {
    const normalized = { ...payload, tool_name: `mcp__${payload.tool_name}` };
    if (shouldForwardReadOrMcp(normalized, catalog, projectRoot, '.grok/skills')) return true;
  }
  // Grok labels its user-facing Read capability `read_file` in Hook payloads,
  // and provides its target as tool_input.target_file.
  return shouldForwardReadOrMcp(payload, catalog, projectRoot, '.grok/skills', {
    readToolNames: ['Read', 'read_file'],
    readPathFields: ['file_path', 'path', 'target_file'],
  });
}

function shouldForwardCodex(payload, catalog, projectRoot) {
  if (isCatalogMcpPayload(payload, catalog)) return true;
  if (payload.hook_event_name !== 'PreToolUse' || payload.tool_name !== 'Bash') return false;
  const command = payload.tool_input?.command;
  if (typeof command !== 'string') return false;
  return splitShellCommand(command).some((tokens) => {
    const [program, ...arguments_] = unwrapShellCommand(tokens);
    if (!program) return false;
    const name = program
      .split('/')
      .at(-1)
      .replace(/\.exe$/iu, '')
      .toLowerCase();
    const candidates = scriptRunner(name)
      ? firstNonOption(arguments_)
      : documentReader(name)
        ? arguments_.filter((value) => value !== '--' && !value.startsWith('-'))
        : [];
    return candidates.some((candidate) =>
      isSkillPath(candidate, payload.cwd, projectRoot, '.agents/skills'),
    );
  });
}

// Codex may submit Bash commands through its login shell, e.g.
// `/bin/zsh -lc 'cat .agents/skills/<id>/SKILL.md'`.  Inspect only the
// explicit script argument for supported shell launchers, then apply the same
// reader and contained-path rules as a direct command.  This is deliberately
// not a general shell parser: unknown invocations remain unclassified.
function unwrapShellCommand(tokens) {
  const [program, ...arguments_] = tokens;
  if (!program) return tokens;
  const name = program
    .split('/')
    .at(-1)
    .replace(/\.exe$/iu, '')
    .toLowerCase();
  if (!['bash', 'zsh', 'sh'].includes(name)) return tokens;
  const scriptIndex = arguments_.findIndex((argument) => /^-[a-z]*c[a-z]*$/iu.test(argument));
  if (scriptIndex < 0) return tokens;
  const script = arguments_[scriptIndex + 1];
  return typeof script === 'string' ? splitShellCommand(script).flat() : tokens;
}

function shouldForwardCursor(payload, catalog, projectRoot) {
  if (payload.hook_event_name === 'afterMCPExecution') {
    return hasCatalogMcpServer(payload.mcp_server_name, catalog);
  }
  return shouldForwardReadOrMcp(payload, catalog, projectRoot, '.cursor/skills');
}

function shouldForwardReadOrMcp(payload, catalog, projectRoot, skillsDirectory, options = {}) {
  if (
    ![
      'PreToolUse',
      'PostToolUse',
      'PostToolUseFailure',
      'postToolUse',
      'postToolUseFailure',
    ].includes(payload.hook_event_name)
  ) {
    return false;
  }
  if (isCatalogMcpPayload(payload, catalog, options.mcpHost)) return true;
  const readToolNames = options.readToolNames ?? ['Read', 'view'];
  if (!readToolNames.includes(payload.tool_name) || payload.hook_event_name === 'PreToolUse') {
    return false;
  }
  const readPathFields = options.readPathFields ?? ['file_path', 'path'];
  const filePath = readPathFields
    .map((field) => payload.tool_input?.[field])
    .find((value) => typeof value === 'string');
  if (isSkillPath(filePath, payload.cwd ?? projectRoot, projectRoot, skillsDirectory)) return true;
  return options.nativePluginRoot
    ? isCatalogPluginSkillPath(
        filePath,
        payload.cwd ?? projectRoot,
        options.nativePluginRoot,
        catalog,
      )
    : false;
}

function hasCatalogSkillToken(prompt, catalog) {
  if (typeof prompt !== 'string') return false;
  const skills = new Set(catalogSkills(catalog));
  return [...prompt.matchAll(SKILL_TOKEN)].some((match) => skills.has(match[2]?.toLowerCase()));
}

function isCatalogMcpPayload(payload, catalog, host) {
  if (hasCatalogMcpServer(payload.mcp_server_name, catalog)) return true;
  const toolName = payload.tool_name;
  if (typeof toolName !== 'string') return false;
  const match = /^mcp__([a-z0-9]+(?:[-_][a-z0-9]+)*)__[a-z0-9_]+$/iu.exec(toolName);
  if (match) return hasCatalogMcpServer(match[1], catalog);
  return host === 'copilot' ? isCatalogCopilotMcpTool(toolName, catalog) : false;
}

function isCatalogCopilotMcpTool(toolName, catalog) {
  const normalizedToolName = toolName.toLowerCase();
  const matches = catalogPlugins(catalog).flatMap((plugin) =>
    Array.isArray(plugin?.mcpServers)
      ? plugin.mcpServers.filter((serverId) => {
          if (typeof serverId !== 'string') return false;
          const prefix = `${serverId.toLowerCase()}-`;
          return (
            normalizedToolName.startsWith(prefix) &&
            /^[a-z0-9_]+$/u.test(normalizedToolName.slice(prefix.length))
          );
        })
      : [],
  );
  const longestServerId = Math.max(0, ...matches.map((serverId) => serverId.length));
  return matches.filter((serverId) => serverId.length === longestServerId).length === 1;
}

function hasCatalogMcpServer(value, catalog) {
  if (typeof value !== 'string') return false;
  const token = normalizeToken(value);
  return catalogPlugins(catalog).some(
    (plugin) =>
      Array.isArray(plugin?.mcpServers) &&
      plugin.mcpServers.some(
        (server) => typeof server === 'string' && normalizeToken(server) === token,
      ),
  );
}

function catalogSkills(catalog) {
  return catalogPlugins(catalog).flatMap((plugin) =>
    Array.isArray(plugin?.skills) ? plugin.skills.filter((skill) => typeof skill === 'string') : [],
  );
}

function catalogPlugins(catalog) {
  return Array.isArray(catalog?.plugins) ? catalog.plugins : [];
}

function splitShellCommand(command) {
  if (command.includes('`') || command.includes('$(')) return [];
  const tokens = [];
  let token = '';
  let quote;
  for (let index = 0; index < command.length; index += 1) {
    const character = command[index];
    if (quote) {
      if (character === quote) quote = undefined;
      else token += character;
      continue;
    }
    if (character === '\\') {
      const next = command[index + 1];
      if (next && /[\s'"`$;&|<>]/u.test(next)) {
        token += next;
        index += 1;
      } else {
        token += character;
      }
      continue;
    }
    if (character === "'" || character === '"') {
      quote = character;
      continue;
    }
    if (/\s/u.test(character)) {
      if (token) tokens.push(token);
      token = '';
      continue;
    }
    if (['&', '|', ';', '<', '>'].includes(character)) return [];
    token += character;
  }
  if (quote) return [];
  if (token) tokens.push(token);
  return tokens.length > 0 ? [tokens] : [];
}

function firstNonOption(arguments_) {
  const candidate = arguments_.find((value) => value !== '--' && !value.startsWith('-'));
  return candidate ? [candidate] : [];
}

function documentReader(program) {
  return ['cat', 'sed', 'head', 'tail', 'less', 'more', 'bat'].includes(program);
}

function scriptRunner(program) {
  return [
    'python',
    'python3',
    'bash',
    'zsh',
    'sh',
    'node',
    'deno',
    'ruby',
    'perl',
    'pwsh',
  ].includes(program);
}

function isSkillPath(candidate, cwd, projectRoot, skillsDirectory) {
  if (
    typeof candidate !== 'string' ||
    typeof cwd !== 'string' ||
    !cwd ||
    candidate.includes('$') ||
    candidate.includes('`')
  ) {
    return false;
  }
  const flavor = isWindowsPath(projectRoot) ? 'win32' : 'posix';
  const implementation = path[flavor];
  if (flavor === 'posix' && isWindowsPath(candidate)) return false;
  if (flavor === 'win32' && path.posix.isAbsolute(candidate) && !path.win32.isAbsolute(candidate))
    return false;
  const normalize = (value) => {
    const resolved = implementation.resolve(value);
    return flavor === 'win32' ? resolved.toLowerCase() : resolved;
  };
  const absolutePath = normalize(implementation.resolve(cwd, candidate));
  const skillsRoot = normalize(implementation.resolve(projectRoot, skillsDirectory));
  const relative = implementation.relative(skillsRoot, absolutePath).replaceAll('\\', '/');
  return /^(?:[a-z0-9]+(?:-[a-z0-9]+)*)\/(?:SKILL\.md|scripts\/.+)$/iu.test(relative);
}

function isCatalogPluginSkillPath(candidate, cwd, pluginRoot, catalog) {
  if (
    typeof candidate !== 'string' ||
    typeof cwd !== 'string' ||
    !cwd ||
    candidate.includes('$') ||
    candidate.includes('`')
  ) {
    return false;
  }
  const flavor = isWindowsPath(pluginRoot) ? 'win32' : 'posix';
  const implementation = path[flavor];
  if (flavor === 'posix' && isWindowsPath(candidate)) return false;
  if (flavor === 'win32' && path.posix.isAbsolute(candidate) && !path.win32.isAbsolute(candidate))
    return false;
  const normalize = (value) => {
    const resolved = implementation.resolve(value);
    return flavor === 'win32' ? resolved.toLowerCase() : resolved;
  };
  const absolutePath = normalize(implementation.resolve(cwd, candidate));
  const directRoot = normalize(implementation.dirname(pluginRoot));
  const cacheRoot = normalize(implementation.resolve(pluginRoot, '..', '..'));
  return (
    matchesCatalogPluginSkillPath(
      implementation.relative(directRoot, absolutePath),
      catalog,
      false,
    ) ||
    matchesCatalogPluginSkillPath(implementation.relative(cacheRoot, absolutePath), catalog, true)
  );
}

function matchesCatalogPluginSkillPath(relativePath, catalog, versioned) {
  const segments = relativePath.replaceAll('\\', '/').split('/');
  const skillsIndex = versioned ? 2 : 1;
  if (
    segments.length < skillsIndex + 3 ||
    segments.some((segment) => !segment || segment === '.' || segment === '..') ||
    segments[skillsIndex] !== 'skills'
  ) {
    return false;
  }
  if (versioned && !/^[a-z0-9][a-z0-9._+-]*$/iu.test(segments[1])) return false;
  const pluginId = segments[0]?.toLowerCase();
  const skillId = segments[skillsIndex + 1]?.toLowerCase();
  const resource = segments.slice(skillsIndex + 2).join('/');
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(skillId ?? '')) return false;
  if (resource !== 'SKILL.md' && !/^scripts\/.+/u.test(resource)) return false;
  const plugin = catalogPlugins(catalog).find(
    (entry) => typeof entry?.id === 'string' && entry.id.toLowerCase() === pluginId,
  );
  return (
    Array.isArray(plugin?.skills) &&
    plugin.skills.some((skill) => typeof skill === 'string' && skill.toLowerCase() === skillId)
  );
}

function isWindowsPath(value) {
  return path.win32.isAbsolute(value) && !path.posix.isAbsolute(value);
}

function normalizeToken(value) {
  return value.toLowerCase().replaceAll('-', '_');
}

async function terminateChildTree(child) {
  if (!child.pid) {
    child.kill();
    return;
  }
  if (process.platform !== 'win32') {
    const processGroupId = child.pid;
    try {
      process.kill(-processGroupId, 'SIGTERM');
    } catch {
      child.kill();
    }
    if (await waitForProcessGroupExit(processGroupId, 500)) return;
    try {
      process.kill(-processGroupId, 'SIGKILL');
    } catch {
      // The process group has already exited.
    }
    await waitForProcessGroupExit(processGroupId, 1_000);
    return;
  }
  await new Promise((resolve) => {
    const killer = spawn(
      process.env.ComSpec || 'cmd.exe',
      ['/d', '/s', '/c', 'taskkill', '/PID', String(child.pid), '/T', '/F'],
      { stdio: 'ignore', windowsHide: true },
    );
    killer.on('error', () => {
      child.kill();
      resolve();
    });
    killer.on('close', (code) => {
      if (code !== 0) child.kill();
      resolve();
    });
  });
}

async function waitForProcessGroupExit(processGroupId, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (isProcessGroupAlive(processGroupId)) {
    if (Date.now() >= deadline) return false;
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
  return true;
}

function isProcessGroupAlive(processGroupId) {
  try {
    process.kill(-processGroupId, 0);
    return true;
  } catch (error) {
    return error?.code !== 'ESRCH';
  }
}

function startBackgroundWarm(runtimePath) {
  try {
    const warmer = spawn(process.execPath, [runtimePath], {
      detached: true,
      env: { ...process.env, [BACKGROUND_WARM_ENV]: '1' },
      stdio: 'ignore',
      windowsHide: true,
    });
    warmer.on('error', () => undefined);
    warmer.unref();
  } catch {
    // Cache warming is best-effort and must never block the Host Hook.
  }
}

async function warmCliCache() {
  const lockPath =
    process.env.PICO_CLI_HOOK_WARM_LOCK_PATH?.trim() ||
    path.join(os.tmpdir(), 'pico-cli-agent-hook-warm.lock');
  const lock = acquireWarmLock(lockPath);
  if (lock === undefined) return;
  try {
    const executable = resolveNpxExecutable();
    await new Promise((resolve) => {
      let finished = false;
      const child = spawn(
        executable.command,
        [...executable.prefixArgs, '--yes', ...registryArgs(), CLI_PACKAGE, '--version'],
        {
          detached: process.platform !== 'win32',
          stdio: 'ignore',
          windowsHide: true,
        },
      );
      const finish = () => {
        if (finished) return;
        finished = true;
        clearTimeout(timer);
        resolve();
      };
      const timer = setTimeout(async () => {
        if (finished) return;
        finished = true;
        await terminateChildTree(child);
        resolve();
      }, BACKGROUND_WARM_TIMEOUT_MS);
      child.on('error', finish);
      child.on('close', finish);
    });
  } finally {
    fsSync.closeSync(lock);
    try {
      fsSync.unlinkSync(lockPath);
    } catch {
      // Another process may have already removed a stale lock.
    }
  }
}

function registryArgs() {
  return CLI_REGISTRY ? [`--registry=${CLI_REGISTRY}`] : [];
}

function acquireWarmLock(lockPath) {
  fsSync.mkdirSync(path.dirname(lockPath), { recursive: true });
  try {
    return fsSync.openSync(lockPath, 'wx');
  } catch (error) {
    if (error?.code !== 'EEXIST') return undefined;
    try {
      const stat = fsSync.statSync(lockPath);
      if (Date.now() - stat.mtimeMs < BACKGROUND_WARM_LOCK_TTL_MS) return undefined;
      fsSync.unlinkSync(lockPath);
      return fsSync.openSync(lockPath, 'wx');
    } catch {
      return undefined;
    }
  }
}

if (process.env[BACKGROUND_WARM_ENV] === '1') {
  try {
    await warmCliCache();
  } catch {
    // The detached warmer is best-effort and has no user-facing output.
  }
}

function resolveNpxExecutable() {
  if (process.platform !== 'win32') return { command: 'npx', prefixArgs: [] };
  const npmExecPath = process.env.npm_execpath?.trim();
  const candidates = [
    npmExecPath && path.join(path.dirname(npmExecPath), 'npx-cli.js'),
    path.resolve(path.dirname(process.execPath), 'node_modules/npm/bin/npx-cli.js'),
    path.resolve(path.dirname(process.execPath), '../lib/node_modules/npm/bin/npx-cli.js'),
  ].filter(Boolean);
  const npxCliPath = candidates.find((candidate) => fsSync.existsSync(candidate));
  if (!npxCliPath) {
    // A nonexistent script produces a normal non-zero child exit and preserves
    // the Hook's fail-open behavior without invoking a command shell.
    return { command: process.execPath, prefixArgs: [candidates[0] ?? 'npx-cli.js'] };
  }
  return { command: process.execPath, prefixArgs: [npxCliPath] };
}
