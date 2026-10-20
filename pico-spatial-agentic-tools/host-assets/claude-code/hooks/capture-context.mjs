#!/usr/bin/env node
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
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_INPUT_BYTES = 1024 * 1024;
const CAPTURE_TIMEOUT_MS = 3_000;
const RUNTIME_HOSTS = new Set(['claude-code', 'codex', 'traex']);
const SHELL_TOOLS = new Set(['Bash', 'exec_command', 'shell_command']);
const WORKFLOW_MCP_SERVERS = new Set(['pico-spatial-editor', 'pico_spatial_editor']);
const WORKFLOW_START_TOOLS = new Set(['start_editor_workflow', 'start_3d_generation_workflow']);
export const WORKFLOW_START_MATCHER = `^(?:${[...SHELL_TOOLS].join('|')}|(?:mcp__(?:${[
  ...WORKFLOW_MCP_SERVERS,
].join('|')})__)?(?:${[...WORKFLOW_START_TOOLS].join('|')}))$`;
// Local setup replaces this exact declaration so a source build does not call an unrelated PATH CLI.
const bundledLocalEntry = undefined;
export const PICO_AGENT_HOOK_FAILURE_MODE = 'non-blocking';

export function shouldCaptureWorkflowContext(
  payload,
  { trustedCliEntry = bundledLocalEntry } = {},
) {
  const toolName = payload?.tool_name;
  if (typeof toolName !== 'string') return false;
  if (isWorkflowStartTool(toolName)) return true;
  if (!SHELL_TOOLS.has(toolName)) return false;
  const command = payload?.tool_input?.command ?? payload?.tool_input?.cmd;
  return typeof command === 'string' && isWorkflowStartCommand(command, trustedCliEntry);
}

function isWorkflowStartTool(toolName) {
  if (WORKFLOW_START_TOOLS.has(toolName)) return true;
  const match = /^mcp__(.+)__(start_editor_workflow|start_3d_generation_workflow)$/u.exec(toolName);
  return Boolean(match && WORKFLOW_MCP_SERVERS.has(match[1]));
}

export async function runWorkflowCallerContextHook(
  host,
  {
    input = readStandardInput(),
    spawnProcess = spawn,
    timeoutMs = CAPTURE_TIMEOUT_MS,
    terminate,
  } = {},
) {
  // Caller-context capture is observational. No failure in this function may reject the Host Hook.
  try {
    if (!RUNTIME_HOSTS.has(host)) return;
    const rawInput = await input;
    if (!rawInput) return;
    let payload;
    try {
      payload = JSON.parse(rawInput);
    } catch {
      return;
    }
    if (!shouldCaptureWorkflowContext(payload)) return;
    const terminateChild = terminate ?? (await loadLifecycleTermination());

    const executable = bundledLocalEntry
      ? { command: process.execPath, prefixArgs: [bundledLocalEntry] }
      : {
          command: process.platform === 'win32' ? 'pico-cli.cmd' : 'pico-cli',
          prefixArgs: [],
        };
    const args = [
      ...executable.prefixArgs,
      'workflow',
      'capture-context',
      host,
      '--integration',
      'pico-spatial-agentic-tools',
    ];
    // Windows batch shims require cmd.exe. Only fixed internal argv reaches its
    // command string; the untrusted Host event remains byte-exact stdin.
    const batchShim = process.platform === 'win32' && !bundledLocalEntry;
    await runCaptureProcess({
      args: batchShim ? ['/d', '/s', '/c', [executable.command, ...args].join(' ')] : args,
      command: batchShim ? process.env.ComSpec || 'cmd.exe' : executable.command,
      input: rawInput,
      spawnProcess,
      terminate: terminateChild,
      timeoutMs,
    });
  } catch {
    // Missing/old CLIs, malformed Host input, stream failures, and timeouts all fail open.
  }
}

async function loadLifecycleTermination() {
  const lifecycle = await import('./agent-hook-process-lifecycle.mjs');
  if (typeof lifecycle.terminateAgentHookChildTree !== 'function') {
    throw new Error('Agent Hook lifecycle helper lacks terminateAgentHookChildTree.');
  }
  return lifecycle.terminateAgentHookChildTree;
}

function isWorkflowStartCommand(command, trustedCliEntry, dialect = 'posix') {
  const commands = tokenizeBoundedShell(command, dialect);
  if (!commands) return false;
  for (const sequence of splitSequences(commands)) {
    let possible = undefined;
    for (const operand of splitAndOrList(sequence)) {
      const reachable =
        possible === undefined ||
        (operand.operator === '&&' ? possible.has('success') : possible.has('failure'));
      if (!reachable) continue;
      if (
        operand.pipeline.some((item) =>
          isWorkflowStartInvocation(item.tokens, trustedCliEntry, dialect),
        )
      )
        return true;
      const outcome = commandOutcomes(operand.pipeline.at(-1)?.tokens ?? [], dialect);
      if (possible === undefined) possible = outcome;
      else if (operand.operator === '&&') {
        possible = new Set([
          ...(possible.has('failure') ? ['failure'] : []),
          ...(possible.has('success') ? outcome : []),
        ]);
      } else {
        possible = new Set([
          ...(possible.has('success') ? ['success'] : []),
          ...(possible.has('failure') ? outcome : []),
        ]);
      }
    }
  }
  return false;
}

function splitSequences(commands) {
  const sequences = [];
  let current = [];
  for (const command of commands) {
    if ((command.operator === 'sequence' || command.operator === '&') && current.length) {
      sequences.push(current);
      current = [];
    }
    current.push({ ...command, operator: current.length ? command.operator : 'sequence' });
  }
  if (current.length) sequences.push(current);
  return sequences;
}

function splitAndOrList(sequence) {
  const operands = [];
  let pipeline = [];
  let operator = 'sequence';
  for (const command of sequence) {
    if ((command.operator === '&&' || command.operator === '||') && pipeline.length) {
      operands.push({ operator, pipeline });
      pipeline = [];
      operator = command.operator;
    }
    pipeline.push(command);
  }
  if (pipeline.length) operands.push({ operator, pipeline });
  return operands;
}

function isWorkflowStartInvocation(tokens, trustedCliEntry, dialect) {
  const unwrapped = unwrapInvocation(tokens);
  if (unwrapped.nested !== undefined) {
    return isWorkflowStartCommand(unwrapped.nested, trustedCliEntry, unwrapped.dialect);
  }
  const [program, first, second, third] = unwrapped.tokens;
  if (!program) return false;
  const executable = normalizedExecutable(
    dialect === 'cmd' && program.startsWith('@') ? program.slice(1) : program,
  );
  const cliOffset = executable === 'node' || executable === 'nodejs' ? 1 : 0;
  const cli =
    cliOffset === 0 ? executable === 'pico-cli' : isTrustedSourceCliEntry(first, trustedCliEntry);
  const group = cliOffset === 0 ? first : second;
  const action = cliOffset === 0 ? second : third;
  return Boolean(
    cli && ((group === 'workflow' && action === 'start') || group === 'workflow:start'),
  );
}

function unwrapInvocation(tokens) {
  let current = [...tokens];
  for (let count = 0; count < 8; count += 1) {
    while (/^[A-Za-z_][A-Za-z0-9_]*=/u.test(current[0] ?? '')) current.shift();
    const executable = normalizedExecutable(current[0] ?? '');
    if (executable === 'env') {
      current = current.slice(1);
      while (current.length) {
        const option = current[0];
        if (option === '--') {
          current.shift();
          break;
        }
        if (option === '-i' || option === '--ignore-environment') {
          current.shift();
          continue;
        }
        if (option === '-u' || option === '--unset' || option === '-C' || option === '--chdir') {
          if (typeof current[1] !== 'string') return { tokens: [] };
          current = current.slice(2);
          continue;
        }
        if (option?.startsWith('-') && !option.startsWith('--')) {
          const short = option.slice(1);
          let consumesNext = false;
          let supported = short.length > 0;
          for (let index = 0; index < short.length; index += 1) {
            const flag = short[index];
            if (flag === 'i') continue;
            if (flag !== 'u' && flag !== 'C') {
              supported = false;
              break;
            }
            // GNU/POSIX short options that take an argument consume the rest
            // of their cluster, or the following token when the cluster ends.
            consumesNext = index === short.length - 1;
            break;
          }
          if (!supported || (consumesNext && typeof current[1] !== 'string')) return { tokens: [] };
          current = current.slice(consumesNext ? 2 : 1);
          continue;
        }
        if (/^--(?:unset|chdir)=.+/u.test(option ?? '')) {
          current.shift();
          continue;
        }
        if (option?.startsWith('-')) return { tokens: [] };
        break;
      }
      while (current[0]?.includes('=') && !current[0].startsWith('=')) current.shift();
      continue;
    }
    if (executable === 'command') {
      current = current.slice(1);
      while (current[0] === '-p') current.shift();
      if (current[0] === '--') current.shift();
      else if (current[0]?.startsWith('-')) return { tokens: [] };
      continue;
    }
    if (executable === 'exec') {
      current = current.slice(1);
      while (current.length) {
        if (/^-[cl]+$/u.test(current[0] ?? '')) {
          current.shift();
          continue;
        }
        if (current[0] === '-a') {
          if (typeof current[1] !== 'string') return { tokens: [] };
          current = current.slice(2);
          continue;
        }
        if (current[0] === '--') current.shift();
        else if (current[0]?.startsWith('-')) return { tokens: [] };
        break;
      }
      continue;
    }
    const args = current.slice(1);
    const shellFlags = ['bash', 'zsh', 'sh'].includes(executable)
      ? /^-[a-z]*c[a-z]*$/iu
      : executable === 'cmd'
        ? /^\/(?:c|k)$/iu
        : ['pwsh', 'powershell'].includes(executable)
          ? /^-(?:c|command)$/iu
          : undefined;
    if (!shellFlags) return { tokens: current };
    const commandIndex = args.findIndex((argument) => shellFlags.test(argument));
    if (commandIndex < 0 || typeof args[commandIndex + 1] !== 'string') {
      return { tokens: current };
    }
    // POSIX sh -c accepts subsequent operands as $0/$1; cmd and PowerShell instead
    // accept the remaining argv as their command when the caller omitted outer quotes.
    const nested = ['bash', 'zsh', 'sh'].includes(executable)
      ? args[commandIndex + 1]
      : args.slice(commandIndex + 1).join(' ');
    return {
      tokens: current,
      nested,
      dialect:
        executable === 'cmd'
          ? 'cmd'
          : executable === 'pwsh' || executable === 'powershell'
            ? 'powershell'
            : 'posix',
    };
  }
  return { tokens: current };
}

function commandOutcomes(tokens, dialect) {
  if (dialect !== 'posix') return new Set(['success', 'failure']);
  const executable = normalizedExecutable(unwrapInvocation(tokens).tokens[0] ?? '');
  if (executable === 'true') return new Set(['success']);
  if (executable === 'false') return new Set(['failure']);
  return new Set(['success', 'failure']);
}

function tokenizeBoundedShell(command, dialect = 'posix') {
  if (!command.trim()) return undefined;
  const commands = [];
  let tokens = [];
  let token = '';
  let quote;
  let operator = 'sequence';
  const flushToken = () => {
    if (token) tokens.push(token);
    token = '';
  };
  const flushCommand = (nextOperator = 'sequence') => {
    flushToken();
    if (tokens.length) commands.push({ operator, tokens });
    tokens = [];
    operator = nextOperator;
  };
  for (let index = 0; index < command.length; index += 1) {
    const character = command[index];
    if (
      dialect === 'posix' &&
      quote !== "'" &&
      (character === '`' || (character === '$' && command[index + 1] === '('))
    ) {
      const end = substitutionEnd(command, index);
      if (end === undefined) return undefined;
      // Opaque data can be an argument, never a trusted executable/group/action.
      token += '\0';
      index = end;
      continue;
    }
    if (quote) {
      if (dialect === 'posix' && quote === '"' && character === '\\') {
        const next = command[index + 1];
        if (next === '\n') index += 1;
        else if (next && /["\\`$]/u.test(next)) {
          token += next;
          index += 1;
        } else token += character;
        continue;
      }
      if (dialect === 'powershell' && quote === '"' && character === '`') {
        const next = command[index + 1];
        if (!next) return undefined;
        if (next === '\r' && command[index + 2] === '\n') index += 2;
        else index += 1;
        if (next !== '\r' && next !== '\n') token += next;
        continue;
      }
      if (character === quote) quote = undefined;
      else token += character;
      continue;
    }
    if (dialect === 'posix' && character === '\\') {
      const next = command[index + 1];
      if (next === '\n') {
        index += 1;
      } else if (next) {
        token += next;
        index += 1;
      } else token += character;
      continue;
    }
    if (dialect === 'cmd' && character === '^') {
      const next = command[index + 1];
      if (!next) return undefined;
      token += next;
      index += 1;
      continue;
    }
    if (dialect === 'powershell' && character === '`') {
      const next = command[index + 1];
      if (!next) return undefined;
      if (next === '\r' && command[index + 2] === '\n') index += 2;
      else index += 1;
      if (next !== '\r' && next !== '\n') token += next;
      continue;
    }
    if (character === '"' || (character === "'" && dialect !== 'cmd')) {
      quote = character;
      continue;
    }
    if (character === '#' && dialect !== 'cmd') {
      if (token) token += character;
      else {
        while (index + 1 < command.length && !/[\r\n]/u.test(command[index + 1])) index += 1;
      }
      continue;
    }
    if (character === '\r' || character === '\n' || (character === ';' && dialect !== 'cmd')) {
      if (character === '\r' && command[index + 1] === '\n') index += 1;
      flushCommand('sequence');
      continue;
    }
    if (character === '&' || character === '|') {
      const doubled = command[index + 1] === character;
      flushCommand(doubled ? `${character}${character}` : character);
      if (doubled) index += 1;
      continue;
    }
    if (/\s/u.test(character)) {
      flushToken();
      continue;
    }
    if (character === '<' || character === '>') {
      if (character === '<' && command[index + 1] === '<') return undefined;
      if (/^\d+$/u.test(token)) token = '';
      else flushToken();
      if (command[index + 1] === character) index += 1;
      if (command[index + 1] === '&') {
        let targetEnd = index + 2;
        while (/\d/u.test(command[targetEnd] ?? '')) targetEnd += 1;
        if (targetEnd === index + 2 && command[targetEnd] === '-') targetEnd += 1;
        if (targetEnd === index + 2) return undefined;
        index = targetEnd - 1;
        continue;
      }
      while (/[^\S\r\n]/u.test(command[index + 1] ?? '')) index += 1;
      const targetStart = command[index + 1];
      if (!targetStart || isRedirectionBoundary(targetStart, dialect)) return undefined;
      let redirectionQuote;
      for (index += 1; index < command.length; index += 1) {
        const next = command[index];
        if (dialect === 'posix' && next === '\\' && redirectionQuote !== "'") {
          const escaped = command[index + 1];
          if (!escaped) return undefined;
          if (redirectionQuote !== '"' || /["\\`$\n]/u.test(escaped)) index += 1;
          continue;
        }
        if (dialect === 'cmd' && !redirectionQuote && next === '^') {
          if (!command[index + 1]) return undefined;
          index += 1;
          continue;
        }
        if (dialect === 'powershell' && redirectionQuote !== "'" && next === '`') {
          const escaped = command[index + 1];
          if (!escaped) return undefined;
          if (escaped === '\r' && command[index + 2] === '\n') index += 2;
          else index += 1;
          continue;
        }
        if (
          dialect === 'posix' &&
          redirectionQuote !== "'" &&
          (next === '`' || (next === '$' && command[index + 1] === '('))
        ) {
          const end = substitutionEnd(command, index);
          if (end === undefined) return undefined;
          index = end;
          continue;
        }
        if (redirectionQuote) {
          if (next === redirectionQuote) redirectionQuote = undefined;
          continue;
        }
        if (next === '"' || (next === "'" && dialect !== 'cmd')) redirectionQuote = next;
        else if (/\s/u.test(next) || isRedirectionBoundary(next, dialect)) {
          index -= 1;
          break;
        }
      }
      if (redirectionQuote) return undefined;
      continue;
    }
    token += character;
  }
  if (quote) return undefined;
  flushCommand();
  return commands.length && commands.length <= 32 ? commands : undefined;
}

function isRedirectionBoundary(character, dialect) {
  return /[\r\n&|<>]/u.test(character) || (character === ';' && dialect !== 'cmd');
}

function substitutionEnd(command, start, nesting = 0) {
  if (nesting >= 8) return undefined;
  const backtick = command[start] === '`';
  let depth = 1;
  let quote;
  for (let index = start + (backtick ? 1 : 2); index < command.length; index += 1) {
    const character = command[index];
    if (character === '\\' && quote !== "'") {
      index += 1;
      continue;
    }
    if (backtick) {
      if (character === '`') return index;
      continue;
    }
    if (quote === "'") {
      if (character === quote) quote = undefined;
      continue;
    }
    if (character === '`' || (character === '$' && command[index + 1] === '(')) {
      const end = substitutionEnd(command, index, nesting + 1);
      if (end === undefined) return undefined;
      index = end;
      continue;
    }
    if (character === '"') {
      quote = quote ? undefined : '"';
      continue;
    }
    if (quote) continue;
    if (character === "'") {
      quote = character;
      continue;
    }
    // Comments/heredocs and case patterns can hide/unbalance closing delimiters. Keep those nested bodies
    // outside this static subset instead of exposing their text as commands.
    if (
      (character === '#' && /[\s;(]/u.test(command[index - 1] ?? '')) ||
      (character === '<' && command[index + 1] === '<') ||
      (command.startsWith('case', index) &&
        /[\s;(]/u.test(command[index - 1] ?? '') &&
        /[\s;&|()]/u.test(command[index + 4] ?? ''))
    )
      return undefined;
    if (character === '(') depth += 1;
    if (character === ')' && --depth === 0) return index;
  }
  return undefined;
}

function basename(value) {
  return value.replaceAll('\\', '/').split('/').at(-1) ?? '';
}

function normalizedExecutable(value) {
  return basename(value)
    .replace(/\.(?:cmd|exe)$/iu, '')
    .toLowerCase();
}

function isTrustedSourceCliEntry(value, trustedCliEntry) {
  if (typeof value !== 'string' || typeof trustedCliEntry !== 'string') return false;
  return path.resolve(value) === path.resolve(trustedCliEntry);
}

function runCaptureProcess(options) {
  return new Promise((resolve) => {
    let child;
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      resolve();
    };
    const timer = setTimeout(() => {
      if (finished) return;
      finished = true;
      releaseCaptureHandles(child);
      void Promise.resolve()
        .then(() => options.terminate(child))
        .then(resolve, resolve);
    }, options.timeoutMs);
    try {
      child = options.spawnProcess(options.command, options.args, {
        detached: process.platform !== 'win32',
        stdio: ['pipe', 'ignore', 'ignore'],
        windowsHide: true,
      });
      // The deadline owns the useful capture window. A failed best-effort tree
      // termination must not let the child handle extend the Host Hook lifetime.
      child.unref?.();
      child.once('error', finish);
      child.once('close', finish);
      child.stdin?.once('error', () => {
        if (finished) return;
        finished = true;
        clearTimeout(timer);
        releaseCaptureHandles(child);
        void Promise.resolve()
          .then(() => options.terminate(child))
          .then(resolve, resolve);
      });
      child.stdin?.end(options.input);
      child.stdin?.unref?.();
    } catch {
      finish();
    }
  });
}

function releaseCaptureHandles(child) {
  try {
    child?.stdin?.destroy?.();
  } catch {
    // A broken input pipe is already released enough for this advisory Hook.
  }
  child?.stdin?.unref?.();
  child?.unref?.();
}

async function readStandardInput() {
  try {
    const chunks = [];
    let bytes = 0;
    for await (const chunk of process.stdin) {
      bytes += chunk.length;
      if (bytes > MAX_INPUT_BYTES) return '';
      chunks.push(chunk);
    }
    return Buffer.concat(chunks).toString('utf8');
  } catch {
    return '';
  }
}

const isDirectExecution =
  process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isDirectExecution) await runWorkflowCallerContextHook(process.argv[2]);
