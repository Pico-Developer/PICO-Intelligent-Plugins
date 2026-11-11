/*
 * Copyright 2026 PICO Immersive Pte. Ltd.
 * SPDX-License-Identifier: Apache-2.0
 */

import { spawn } from 'node:child_process';
import { terminateAgentHookChildTree } from './agent-hook-process-lifecycle.mjs';
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
export const PICO_AGENT_HOOK_FAILURE_MODE = 'non-blocking';

export async function runAgentHookWrapper({ host, wrapperUrl, stage }) {
  const startedAt = Date.now();
  const wrapperPath = fileURLToPath(wrapperUrl);
  const catalogPath = path.join(path.dirname(wrapperPath), 'catalog.json');
  const wrapperDirectory = path.dirname(wrapperPath);
  const nestedTraeInstall =
    host === 'traecli' &&
    path.basename(path.resolve(wrapperDirectory, '../../..')) === '.trae' &&
    path.basename(path.resolve(wrapperDirectory, '../..')) === 'cli';
  const pluginRoot = resolvePluginRoot(host, wrapperDirectory)?.trim();
  const nativePluginInstall =
    pluginRoot && isNativePluginInstall(host, pluginRoot, wrapperDirectory);
  const nativePluginRoot = nativePluginInstall ? path.resolve(pluginRoot) : undefined;
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
  const remainingHotMs = () => Math.max(0, hotTimeoutMs - (Date.now() - startedAt));
  let childAttempt = 0;
  let inputExpired = false;
  let inputTimer;
  // The same hot-path deadline covers stdin and filtering, then only the
  // remaining budget is available to the child. A Host need not deliver EOF.
  const input = await Promise.race([
    prepareInput(),
    new Promise((resolve) => {
      inputTimer = setTimeout(() => {
        inputExpired = true;
        process.stdin.destroy();
        resolve(undefined);
      }, remainingHotMs());
    }),
  ]).finally(() => clearTimeout(inputTimer));
  if (!input || remainingHotMs() <= 0) return;

  async function prepareInput() {
    try {
      const chunks = [];
      let inputBytes = 0;
      for await (const chunk of process.stdin) {
        inputBytes += chunk.length;
        if (inputExpired || inputBytes > MAX_INPUT_BYTES) return;
        chunks.push(chunk);
      }
      if (inputExpired) return;
      const normalized = await normalizeHostInput(host, stage, Buffer.concat(chunks), catalogPath);
      if (inputExpired || !normalized?.length) return;
      const forward = await shouldForward(
        host,
        normalized,
        catalogPath,
        projectRoot,
        nativePluginRoot,
      );
      if (!inputExpired && forward) return normalized;
    } catch {
      // Broken, oversized and timed-out input all fail open.
    }
  }
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
    await run([localEntry, ...commonArgs], input, remainingHotMs());
    return;
  }

  const npxArgs = ['--yes', ...registryArgs()];
  const hotResult = await run(
    [...npxArgs, '--offline', CLI_PACKAGE, ...commonArgs],
    input,
    remainingHotMs(),
  );
  if (hotResult === 'ok') return;
  startBackgroundWarm(wrapperPath);

  async function run(args, stdin, timeoutMs) {
    if (timeoutMs <= 0) return 'timeout';
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
        await releaseChildAfterTimeout(child);
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
      }, remainingHotMs());
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

function resolvePluginRoot(host, wrapperDirectory) {
  if (host === 'claude-code') return process.env.CLAUDE_PLUGIN_ROOT;
  if (host === 'cursor') return process.env.CURSOR_PLUGIN_ROOT;
  if (host === 'codex' || host === 'copilot' || host === 'traecli') return process.env.PLUGIN_ROOT;
  if (host === 'codebuddy') return process.env.CODEBUDDY_PLUGIN_ROOT;
  if (host === 'grok') return process.env.GROK_PLUGIN_ROOT;
  if (host === 'qoder') return process.env.QODER_PLUGIN_ROOT;
  const authoredHostAsset =
    path.basename(path.dirname(wrapperDirectory)) === 'antigravity' &&
    path.basename(path.resolve(wrapperDirectory, '../..')) === 'host-assets';
  if (host === 'antigravity' && path.basename(wrapperDirectory) === 'hooks' && !authoredHostAsset) {
    return path.dirname(wrapperDirectory);
  }
}

function isNativePluginInstall(host, pluginRoot, wrapperDirectory) {
  const expected =
    host === 'antigravity'
      ? path.resolve(pluginRoot, 'hooks')
      : ['codebuddy', 'grok', 'qoder'].includes(host)
        ? path.resolve(pluginRoot, 'hooks')
        : path.resolve(pluginRoot, 'host-assets', host, 'hooks');
  return equivalentPath(expected, wrapperDirectory);
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
  const normalizedTool = normalizeAntigravityTool(payload?.toolCall, catalog, payload);
  if (!conversationId || stepIdx === undefined || !normalizedTool) return undefined;
  const { carryRawError, ...normalizedPayload } = normalizedTool;
  const rawError = typeof payload.error === 'string' && payload.error ? payload.error : undefined;
  return Buffer.from(
    JSON.stringify({
      session_id: conversationId,
      turn_id: String(stepIdx),
      tool_use_id: `${conversationId}:${stepIdx}`,
      hook_event_name: rawError ? 'PostToolUseFailure' : 'PostToolUse',
      ...(carryRawError && rawError ? { error: rawError } : {}),
      ...normalizedPayload,
    }),
  );
}

function normalizeAntigravityTool(toolCall, catalog, payload) {
  if (toolCall?.name === 'call_mcp_tool') {
    const serverId = toolCall?.args?.ServerName;
    const toolName = toolCall?.args?.ToolName;
    if (typeof serverId !== 'string' || typeof toolName !== 'string') return undefined;
    const normalized = normalizeAntigravityMcpServerTool(serverId, toolName, catalog);
    return normalized ? { tool_name: normalized, carryRawError: false } : undefined;
  }
  // Antigravity 1.3.3 exposes project Skill access through these built-ins.
  // Normalize only the documented argument fields; the canonical path/catalog
  // gates below still decide whether this is a PICO-owned Skill invocation.
  if (toolCall?.name === 'view_file') {
    const filePath = toolCall?.args?.AbsolutePath;
    return typeof filePath === 'string' && filePath
      ? { tool_name: 'Read', tool_input: { file_path: filePath }, carryRawError: true }
      : undefined;
  }
  if (toolCall?.name === 'run_command') {
    const command = toolCall?.args?.CommandLine;
    if (typeof command !== 'string' || !command) return undefined;
    const cwd =
      typeof toolCall?.args?.Cwd === 'string' && toolCall.args.Cwd
        ? toolCall.args.Cwd
        : Array.isArray(payload?.workspacePaths) && typeof payload.workspacePaths[0] === 'string'
          ? payload.workspacePaths[0]
          : undefined;
    return {
      tool_name: 'Bash',
      tool_input: { command },
      ...(cwd ? { cwd } : {}),
      carryRawError: true,
    };
  }
  return undefined;
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
  if (host === 'codex') {
    return shouldForwardCodex(payload, catalog, projectRoot, nativePluginRoot);
  }
  if (host === 'traecli') {
    return (
      shouldForwardReadOrMcp(payload, catalog, projectRoot, '.trae/skills', {
        nativePluginRoot,
      }) ||
      shouldForwardShellSkillAccess(payload, catalog, projectRoot, '.trae/skills', {
        eventNames: ['PostToolUse', 'PostToolUseFailure'],
        toolNames: ['Bash', 'exec_command', 'shell_command'],
        nativePluginRoot,
      })
    );
  }
  if (host === 'cursor') {
    return shouldForwardCursor(payload, catalog, projectRoot, nativePluginRoot);
  }
  if (host === 'copilot') {
    return shouldForwardReadOrMcp(payload, catalog, projectRoot, '.github/skills', {
      mcpHost: 'copilot',
      nativePluginRoot,
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
  if (host === 'antigravity') {
    return (
      shouldForwardReadOrMcp(payload, catalog, projectRoot, '.agents/skills', {
        nativePluginRoot,
      }) ||
      shouldForwardShellSkillAccess(payload, catalog, projectRoot, '.agents/skills', {
        eventNames: ['PostToolUse', 'PostToolUseFailure'],
        toolNames: ['Bash'],
        nativePluginRoot,
      })
    );
  }
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

function shouldForwardCodex(payload, catalog, projectRoot, nativePluginRoot) {
  if (isCatalogMcpPayload(payload, catalog)) return true;
  return shouldForwardShellSkillAccess(payload, catalog, projectRoot, '.agents/skills', {
    eventNames: ['PostToolUse', 'PostToolUseFailure'],
    toolNames: ['Bash'],
    nativePluginRoot,
  });
}

function shouldForwardShellSkillAccess(
  payload,
  catalog,
  projectRoot,
  skillsDirectory,
  { eventNames, toolNames, nativePluginRoot },
) {
  if (!eventNames.includes(payload.hook_event_name) || !toolNames.includes(payload.tool_name)) {
    return false;
  }
  const command = payload.tool_input?.command;
  if (typeof command !== 'string') return false;
  const outerUnits = splitShellCommand(command);
  if (!outerUnits) return false;
  const units = [];
  for (const unit of outerUnits) {
    const unwrapped = unwrapShellCommand(unit);
    if (!unwrapped) return false;
    units.push(...unwrapped);
  }
  let matched = false;
  for (const unit of units) {
    const [stage, filter] = unit.stages;
    if (!stage || unit.stages.length > 2) return false;
    if (filter && !isLiteralSedRangeFilter(filter)) return false;
    const [program, ...arguments_] = stage;
    if (!program) return false;
    const name = portableProgramName(program);
    if (filter && isInertPrintfSegment(name, arguments_)) return false;
    if (isInertPrintfSegment(name, arguments_)) continue;
    const access = shellSkillAccess(name, arguments_);
    if (!access) return false;
    if (filter && access.kind !== 'document') return false;
    matched ||= access.candidates.some((candidate) => {
      // Shell candidates are expressions until tokenization proves otherwise. Structured
      // Host read callbacks pass literal paths and are validated by containment below.
      if (candidate.includes('$') || candidate.includes('`')) return false;
      const skillId = installedSkillId(
        candidate,
        payload.cwd,
        projectRoot,
        skillsDirectory,
        access.kind,
      );
      if (typeof skillId === 'string' && catalogSkills(catalog).includes(skillId)) return true;
      return nativePluginRoot
        ? isCatalogPluginSkillPath(
            candidate,
            payload.cwd ?? projectRoot,
            nativePluginRoot,
            catalog,
            access.kind,
          )
        : false;
    });
  }
  return matched;
}

function isLiteralSedRangeFilter(stage) {
  const [program, ...arguments_] = stage;
  return (
    typeof program === 'string' &&
    portableProgramName(program) === 'sed' &&
    arguments_.length === 2 &&
    arguments_[0] === '-n' &&
    /^\d+(?:,\d+)?p$/u.test(arguments_[1])
  );
}

function isInertPrintfSegment(program, arguments_) {
  const literalArguments = arguments_[0] === '--' ? arguments_.slice(1) : arguments_;
  return (
    program === 'printf' &&
    literalArguments.length > 0 &&
    (arguments_[0] === '--' || !arguments_[0].startsWith('-')) &&
    literalArguments.every((argument) => !argument.includes('$') && !argument.includes('`'))
  );
}

function shellSkillAccess(program, arguments_) {
  if (scriptRunner(program)) {
    const candidate = scriptRunnerCandidate(program, arguments_);
    return candidate ? { kind: 'script', candidates: [candidate] } : undefined;
  }
  if (!documentReader(program) || hasMutatingReaderOption(program, arguments_)) return undefined;
  const candidates = documentReaderCandidates(program, arguments_);
  return candidates ? { kind: 'document', candidates } : undefined;
}

function scriptRunnerCandidate(program, arguments_) {
  if (program === 'deno') {
    const runIndex = arguments_.indexOf('run');
    return runIndex === 0 ? firstRunnerOperand(program, arguments_.slice(1)) : undefined;
  }

  if (['pwsh', 'powershell'].includes(program)) {
    const fileIndex = arguments_.findIndex((argument) => /^-(?:f|file)$/iu.test(argument));
    if (
      fileIndex >= 0 &&
      arguments_
        .slice(0, fileIndex)
        .every((argument) => /^-(?:nologo|noprofile|noninteractive)$/iu.test(argument))
    ) {
      return arguments_[fileIndex + 1];
    }
    return fileIndex < 0 ? firstRunnerOperand(program, arguments_) : undefined;
  }

  return firstRunnerOperand(program, arguments_);
}

function firstRunnerOperand(program, arguments_) {
  let optionsEnded = false;
  for (let index = 0; index < arguments_.length; index += 1) {
    const argument = arguments_[index];
    if (!optionsEnded && argument === '--') {
      optionsEnded = true;
      continue;
    }
    if (!optionsEnded && argument.startsWith('-') && argument !== '-') {
      const option = runnerOption(program, argument);
      if (option === 'unknown') return undefined;
      if (option === 'value') index += 1;
      continue;
    }
    return argument;
  }
  return undefined;
}

function runnerOption(program, argument) {
  if (['python', 'python3'].includes(program)) {
    if (/^-(?:W|X)$/u.test(argument)) return 'value';
    if (/^-(?:W|X).+/u.test(argument)) return 'flag';
    return /^-(?:B|E|I|O|OO|P|q|s|S|u|v)$/u.test(argument) ? 'flag' : 'unknown';
  }
  if (['node', 'nodejs'].includes(program)) {
    if (argument === '--conditions') return 'value';
    if (/^--conditions=.+/u.test(argument)) return 'flag';
    if (/^(?:--no-warnings|--trace-warnings|--use-strict)$/u.test(argument)) return 'flag';
    return 'unknown';
  }
  if (['pwsh', 'powershell'].includes(program)) {
    return /^-(?:nologo|noprofile|noninteractive)$/iu.test(argument) ? 'flag' : 'unknown';
  }
  if (program === 'deno') {
    return /^(?:--allow-[a-z-]+(?:=.*)?|--cached-only|--no-check|--quiet)$/u.test(argument)
      ? 'flag'
      : 'unknown';
  }
  if (['bash', 'zsh', 'sh', 'ksh', 'ash', 'dash', 'fish'].includes(program)) {
    return /^-[eEux]+$/u.test(argument) ? 'flag' : 'unknown';
  }
  if (program === 'osascript') {
    if (/^-(?:l|s)$/u.test(argument)) return 'value';
    return 'unknown';
  }
  return 'unknown';
}

function documentReaderCandidates(program, arguments_) {
  const parsed = parseReaderArguments(program, arguments_);
  if (!parsed) return undefined;
  const { positional, suppliedExpression } = parsed;
  const fileOperands =
    ['grep', 'rg', 'ripgrep', 'sed'].includes(program) && !suppliedExpression
      ? positional.slice(1)
      : positional;
  // One command-level terminal cannot assign an outcome to individual files.
  // Requiring exactly one operand prevents an early exit or one failed target
  // from being reported as a successful access to another target.
  return fileOperands.length === 1 ? fileOperands : undefined;
}

function parseReaderArguments(program, arguments_) {
  const positional = [];
  let suppliedExpression = false;
  let optionsEnded = false;
  for (let index = 0; index < arguments_.length; index += 1) {
    const argument = arguments_[index];
    if (!optionsEnded && argument === '--') {
      optionsEnded = true;
      continue;
    }
    if (!optionsEnded && argument.startsWith('-') && argument !== '-') {
      const optionToken = argument.split('=', 1)[0];
      let option = optionToken;
      let optionKind = readerOption(program, option, argument);
      if (optionKind === 'unknown' && !optionToken.startsWith('--') && optionToken.length > 2) {
        const shortOption = optionToken.slice(0, 2);
        const shortKind = readerOption(program, shortOption, argument);
        if (shortKind !== 'unknown') {
          option = shortOption;
          optionKind = shortKind;
        }
      }
      if (optionKind === 'unknown') return undefined;
      const pathOption =
        ['get-content', 'gc'].includes(program) && /^-(?:path|literalpath)$/iu.test(option);
      if (pathOption) {
        if (argument.includes('=') || optionToken !== option) return undefined;
        const candidate = arguments_[index + 1];
        if (candidate === undefined) return undefined;
        positional.push(candidate);
        index += 1;
        continue;
      }
      const expressionOption = ['-e', '-f', '--regexp', '--expression', '--file'].includes(option);
      if (expressionOption) suppliedExpression = true;
      if (optionKind === 'value' && !argument.includes('=') && optionToken === option) index += 1;
      continue;
    }
    positional.push(argument);
  }
  return { positional, suppliedExpression };
}

function readerOption(program, option, argument) {
  if (['grep', 'rg', 'ripgrep'].includes(program)) {
    if (
      [
        '-A',
        '-B',
        '-C',
        '-e',
        '-f',
        '-g',
        '-m',
        '--after-context',
        '--before-context',
        '--binary-files',
        '--context',
        '--directories',
        '--exclude',
        '--exclude-dir',
        '--file',
        '--glob',
        '--include',
        '--label',
        '--max-count',
        '--regexp',
      ].includes(option)
    ) {
      return /^-[efgmnABC].+/u.test(argument) ? 'flag' : 'value';
    }
    return [
      '-F',
      '-H',
      '-I',
      '-i',
      '-L',
      '-l',
      '-n',
      '-s',
      '-v',
      '-w',
      '-x',
      '--fixed-strings',
      '--hidden',
      '--ignore-case',
      '--no-ignore',
      '--line-number',
    ].includes(option)
      ? 'flag'
      : 'unknown';
  }
  if (program === 'sed') {
    if (['-e', '-f', '--expression', '--file'].includes(option)) return 'value';
    return ['-n', '--quiet', '--silent'].includes(option) ? 'flag' : 'unknown';
  }
  if (['head', 'tail'].includes(program)) {
    if (['-c', '-n', '--bytes', '--lines', '--pid', '--sleep-interval'].includes(option)) {
      return 'value';
    }
    return ['-f', '-F', '-q', '-v', '-z', '--follow', '--quiet', '--verbose'].includes(option)
      ? 'flag'
      : 'unknown';
  }
  if (program === 'nl') {
    if (/^-[bdfhinpstvw].+/u.test(argument)) return 'flag';
    return ['-b', '-d', '-f', '-h', '-i', '-n', '-s', '-v', '-w'].includes(option)
      ? 'value'
      : 'unknown';
  }
  if (program === 'bat') {
    if (['-H', '-r', '--highlight-line', '--line-range', '--tabs'].includes(option)) return 'value';
    return ['-n', '-p', '--plain', '--paging=never'].includes(argument) ? 'flag' : 'unknown';
  }
  if (['get-content', 'gc'].includes(program)) {
    if (['-path', '-literalpath'].includes(option.toLowerCase())) return 'value';
    if (
      ['-delimiter', '-encoding', '-readcount', '-tail', '-totalcount'].includes(
        option.toLowerCase(),
      )
    )
      return 'value';
    return ['-raw', '-wait'].includes(option.toLowerCase()) ? 'flag' : 'unknown';
  }
  if (program === 'cat') {
    return /^-[benstuvAET]+$/u.test(argument) ||
      ['--number', '--number-nonblank', '--squeeze-blank', '--show-all'].includes(option)
      ? 'flag'
      : 'unknown';
  }
  return 'unknown';
}

function hasMutatingReaderOption(program, arguments_) {
  return (
    program === 'sed' &&
    arguments_.some(
      (argument) => /^-[^-]*i/iu.test(argument) || /^--in-place(?:$|=)/iu.test(argument),
    )
  );
}

// Codex may submit Bash commands through its login shell, e.g.
// `/bin/zsh -lc 'cat .agents/skills/<id>/SKILL.md'`.  Inspect only the
// explicit script argument for supported shell launchers, then apply the same
// reader and contained-path rules as a direct command.  This is deliberately
// not a general shell parser: unknown invocations remain unclassified.
function unwrapShellCommand(unit) {
  if (unit.stages.length !== 1) return [unit];
  const [tokens] = unit.stages;
  const [program, ...arguments_] = tokens ?? [];
  if (!program) return undefined;
  const name = portableProgramName(program);
  if (!['bash', 'zsh', 'sh'].includes(name)) return [unit];
  const scriptIndex = findCommandStringOption(arguments_);
  if (scriptIndex < 0) return [unit];
  if (
    scriptIndex !== arguments_.length - 2 ||
    !arguments_.slice(0, scriptIndex + 1).every(supportedCommandShellOption)
  ) {
    return undefined;
  }
  const script = arguments_[scriptIndex + 1];
  if (typeof script !== 'string') return undefined;
  const units = splitShellCommand(script);
  if (!units) return undefined;
  const usesErrexit = arguments_
    .slice(0, scriptIndex + 1)
    .some((argument) => argument.slice(1).includes('e'));
  return usesErrexit && units.length > 1 ? undefined : units;
}

function findCommandStringOption(arguments_) {
  for (let index = 0; index < arguments_.length; index += 1) {
    const argument = arguments_[index];
    // `--` and the first non-option both end the interpreter option prefix.
    // Any later `-c` belongs to the executed script, not to the shell itself.
    if (argument === '--' || argument === '-' || !argument.startsWith('-')) return -1;
    if (/^-[a-z]*c[a-z]*$/u.test(argument)) return index;
  }
  return -1;
}

function supportedCommandShellOption(argument) {
  if (!/^-[a-z]+$/u.test(argument)) return false;
  const flags = argument.slice(1);
  return [...flags].every((flag) => ['c', 'e', 'l'].includes(flag));
}

function shouldForwardCursor(payload, catalog, projectRoot, nativePluginRoot) {
  if (payload.hook_event_name === 'afterMCPExecution') {
    return hasCatalogMcpServer(payload.mcp_server_name, catalog);
  }
  return shouldForwardReadOrMcp(payload, catalog, projectRoot, '.cursor/skills', {
    nativePluginRoot,
  });
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
  if (
    !readToolNames.includes(payload.tool_name) ||
    !['PostToolUse', 'PostToolUseFailure', 'postToolUse', 'postToolUseFailure'].includes(
      payload.hook_event_name,
    )
  ) {
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
  if (command.includes('`') || command.includes('$(')) return undefined;
  const units = [];
  const stages = [];
  const tokens = [];
  let token = '';
  let tokenStarted = false;
  let quote;
  for (let index = 0; index < command.length; index += 1) {
    const character = command[index];
    // The evidence grammar supports only horizontal space and tab. Reject
    // line boundaries and other control whitespace rather than assigning them
    // shell semantics that differ across launchers.
    if (character.charCodeAt(0) < 0x20 && character !== '\t') return undefined;
    if (quote) {
      if (quote === '"' && character === '\\') {
        const next = command[index + 1];
        if (next === undefined || next === '\n' || next === '\r') return undefined;
        if (['$', '`', '"', '\\'].includes(next)) {
          token += next;
          tokenStarted = true;
          index += 1;
        } else {
          token += character;
          tokenStarted = true;
        }
        continue;
      }
      if (character === quote) quote = undefined;
      else token += character;
      continue;
    }
    if (character === '\\') {
      const next = command[index + 1];
      if (next && /[\s'"`$;&|<>]/u.test(next)) {
        token += next;
        tokenStarted = true;
        index += 1;
      } else {
        token += character;
        tokenStarted = true;
      }
      continue;
    }
    if (character === "'" || character === '"') {
      quote = character;
      tokenStarted = true;
      continue;
    }
    // In POSIX shells `#` starts a comment only at the beginning of a word.
    // Stop there so a path mentioned in a comment cannot become reader argv;
    // an embedded `#` remains part of the current word. A later newline would
    // begin another command, so reject the whole input instead of letting the
    // comment hide that boundary from the fail-closed rule above.
    if (character === '#' && !tokenStarted) {
      if (/[\r\n]/u.test(command.slice(index + 1))) return undefined;
      if (tokens.length > 0) stages.push([...tokens]);
      if (stages.length > 0) units.push({ stages: [...stages] });
      return units.length > 0 ? units : undefined;
    }
    if (character === ' ' || character === '\t') {
      if (tokenStarted) tokens.push(token);
      token = '';
      tokenStarted = false;
      continue;
    }
    if (character === ';') {
      if (tokenStarted) tokens.push(token);
      if (tokens.length === 0) return undefined;
      stages.push([...tokens]);
      units.push({ stages: [...stages] });
      stages.length = 0;
      tokens.length = 0;
      token = '';
      tokenStarted = false;
      continue;
    }
    if (character === '|') {
      if (tokenStarted) tokens.push(token);
      if (tokens.length === 0 || stages.length > 0) return undefined;
      stages.push([...tokens]);
      tokens.length = 0;
      token = '';
      tokenStarted = false;
      continue;
    }
    if (['&', '<', '>'].includes(character)) return undefined;
    token += character;
    tokenStarted = true;
  }
  if (quote) return undefined;
  if (tokenStarted) tokens.push(token);
  if (tokens.length > 0) stages.push(tokens);
  else if (stages.length > 0) return undefined;
  if (stages.length > 0) units.push({ stages });
  return units.length > 0 ? units : undefined;
}

function portableProgramName(program) {
  return (isWindowsExecutablePath(program) ? program.split(/[\\/]/u) : program.split('/'))
    .at(-1)
    .replace(/\.exe$/iu, '')
    .toLowerCase();
}

function documentReader(program) {
  return [
    'cat',
    'sed',
    'head',
    'tail',
    'more',
    'bat',
    'nl',
    'grep',
    'rg',
    'ripgrep',
    'od',
    'xxd',
    'strings',
    'tac',
    'view',
    'get-content',
    'gc',
  ].includes(program);
}

function scriptRunner(program) {
  return [
    'python',
    'python3',
    'bash',
    'zsh',
    'sh',
    'ksh',
    'ash',
    'dash',
    'fish',
    'node',
    'nodejs',
    'deno',
    'bun',
    'ruby',
    'perl',
    'pwsh',
    'powershell',
    'osascript',
  ].includes(program);
}

function isSkillPath(candidate, cwd, projectRoot, skillsDirectory) {
  return installedSkillId(candidate, cwd, projectRoot, skillsDirectory, 'document') !== undefined;
}

function installedSkillId(candidate, cwd, projectRoot, skillsDirectory, kind = 'document') {
  if (typeof candidate !== 'string' || typeof cwd !== 'string' || !cwd) {
    return undefined;
  }
  const flavor = isWindowsPath(projectRoot) ? 'win32' : 'posix';
  const implementation = path[flavor];
  // A backslash is not a POSIX path separator. Reject it rather than letting
  // later portable formatting turn a different file name into a Skill path.
  if (flavor === 'posix' && candidate.includes('\\')) return undefined;
  if (flavor === 'posix' && isWindowsPath(candidate)) return undefined;
  if (flavor === 'win32' && path.posix.isAbsolute(candidate) && !path.win32.isAbsolute(candidate))
    return undefined;
  const normalize = (value) => {
    const resolved = implementation.resolve(value);
    return flavor === 'win32' ? resolved.toLowerCase() : resolved;
  };
  const absolutePath = normalize(implementation.resolve(cwd, candidate));
  const skillsRoot = normalize(implementation.resolve(projectRoot, skillsDirectory));
  const relative = implementation.relative(skillsRoot, absolutePath).replaceAll('\\', '/');
  const match = (
    kind === 'script'
      ? /^([a-z0-9]+(?:-[a-z0-9]+)*)\/scripts\/.+/iu
      : /^([a-z0-9]+(?:-[a-z0-9]+)*)\/SKILL\.md$/iu
  ).exec(relative);
  return match?.[1]?.toLowerCase();
}

function isCatalogPluginSkillPath(candidate, cwd, pluginRoot, catalog, kind = 'document') {
  if (typeof candidate !== 'string' || typeof cwd !== 'string' || !cwd) {
    return false;
  }
  const flavor = isWindowsPath(pluginRoot) ? 'win32' : 'posix';
  const implementation = path[flavor];
  if (flavor === 'posix' && candidate.includes('\\')) return false;
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
  const versioned = isPluginVersionSegment(implementation.basename(normalize(pluginRoot)));
  return matchesCatalogPluginSkillPath(
    implementation.relative(versioned ? cacheRoot : directRoot, absolutePath),
    catalog,
    versioned,
    flavor,
    kind,
  );
}

function matchesCatalogPluginSkillPath(relativePath, catalog, versioned, flavor, kind) {
  const segments = relativePath.replaceAll('\\', '/').split('/');
  const skillsIndex = versioned ? 2 : 1;
  if (
    segments.length < skillsIndex + 3 ||
    segments.some((segment) => !segment || segment === '.' || segment === '..') ||
    !portableSegmentEquals(segments[skillsIndex], 'skills', flavor)
  ) {
    return false;
  }
  if (versioned && !isPluginVersionSegment(segments[1])) return false;
  const pluginId = segments[0]?.toLowerCase();
  const skillId = segments[skillsIndex + 1]?.toLowerCase();
  const resourceSegments = segments.slice(skillsIndex + 2);
  const resource = resourceSegments.join('/');
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(skillId ?? '')) return false;
  if (
    kind === 'document'
      ? !portableSegmentEquals(resource, 'SKILL.md', flavor)
      : resourceSegments.length < 2 ||
        !portableSegmentEquals(resourceSegments[0], 'scripts', flavor)
  ) {
    return false;
  }
  const plugin = catalogPlugins(catalog).find(
    (entry) => typeof entry?.id === 'string' && entry.id.toLowerCase() === pluginId,
  );
  return (
    Array.isArray(plugin?.skills) &&
    plugin.skills.some((skill) => typeof skill === 'string' && skill.toLowerCase() === skillId)
  );
}

function isPluginVersionSegment(value) {
  return /^\d+\.\d+\.\d+(?:-[0-9a-z.-]+)?(?:\+[0-9a-z.-]+)?$/iu.test(value);
}

function portableSegmentEquals(actual, expected, flavor) {
  return flavor === 'win32'
    ? actual?.toLowerCase() === expected.toLowerCase()
    : actual === expected;
}

function isWindowsPath(value) {
  return path.win32.isAbsolute(value) && !path.posix.isAbsolute(value);
}

function isWindowsExecutablePath(value) {
  return isWindowsPath(value) || /^\.{1,2}[\\/]/u.test(value);
}

function normalizeToken(value) {
  return value.toLowerCase().replaceAll('-', '_');
}

async function releaseChildAfterTimeout(child) {
  try {
    await terminateAgentHookChildTree(child);
  } catch {
    // Cleanup is advisory even when the operating system refuses termination.
  } finally {
    child.unref();
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
        await releaseChildAfterTimeout(child);
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
