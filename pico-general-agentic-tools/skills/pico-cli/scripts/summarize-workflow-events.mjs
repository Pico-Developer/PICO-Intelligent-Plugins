/*
 * Copyright 2026 PICO Immersive Pte. Ltd.
 * SPDX-License-Identifier: Apache-2.0
 */

import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { summarizeWorkflowControl } from './workflow-control-summary.mjs';

const tokenFields = {
  inputTokens: ['inputTokens', 'input_tokens'],
  outputTokens: ['outputTokens', 'output_tokens'],
  cachedInputTokens: ['cachedReadTokens', 'cachedInputTokens', 'cached_input_tokens'],
  cachedWriteTokens: ['cachedWriteTokens', 'cacheWriteTokens', 'cached_write_tokens'],
  reasoningTokens: ['thoughtTokens', 'reasoningTokens', 'reasoning_tokens'],
  totalTokens: ['totalTokens', 'total_tokens'],
};
const record = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value) => (typeof value === 'string' && value.trim() ? value : null);
const number = (value) =>
  typeof value === 'number' && Number.isSafeInteger(value) && value >= 0 ? value : null;
const canonical = (value) =>
  JSON.stringify(value, (_, item) =>
    record(item)
      ? Object.fromEntries(
          Object.keys(item)
            .sort()
            .map((key) => [key, item[key]]),
        )
      : item,
  );
const elapsed = (start, end) =>
  start && end && Date.parse(end.recordedAt) >= Date.parse(start.recordedAt)
    ? Date.parse(end.recordedAt) - Date.parse(start.recordedAt)
    : null;

/** Reads only explicitly supplied public event pages. Never calls a Host or mutates a Run. */
export function summarizeWorkflowEventPages(pages, { run = null, result = null } = {}) {
  if (!Array.isArray(pages) || !pages.length)
    throw new Error('At least one event page is required.');
  const events = new Map(),
    pageCopies = new Set();
  let workflow,
    runId,
    terminalCursor = null,
    lastCursor = 0,
    duplicateEvents = 0;
  for (const page of pages) {
    if (
      !record(page) ||
      page.schemaVersion !== 'pico-workflow-event-page/v0' ||
      !text(page.runId) ||
      !record(page.workflow) ||
      !text(page.workflow.name) ||
      !text(page.workflow.version) ||
      !Array.isArray(page.events) ||
      !Number.isSafeInteger(page.nextCursor) ||
      page.nextCursor < 0 ||
      typeof page.hasMore !== 'boolean' ||
      typeof page.terminal !== 'boolean' ||
      (page.terminal && page.hasMore)
    )
      throw new Error('Invalid public event page.');
    workflow ??= { name: page.workflow.name, version: page.workflow.version };
    runId ??= page.runId;
    if (
      page.runId !== runId ||
      page.workflow.name !== workflow.name ||
      page.workflow.version !== workflow.version
    )
      throw new Error('Pages contain conflicting Run or Workflow identities.');
    if (terminalCursor !== null && !page.terminal)
      throw new Error('Authoritative terminality regresses between pages.');
    const duplicatePage = pageCopies.has(canonical(page));
    const beforeCursor = lastCursor;
    let pageCursor = null;
    for (const event of page.events) {
      if (
        !record(event) ||
        event.schemaVersion !== 'pico-workflow-event/v0' ||
        event.runId !== runId ||
        !Number.isSafeInteger(event.cursor) ||
        event.cursor < 1 ||
        !text(event.type) ||
        !record(event.source) ||
        !text(event.source.kind) ||
        !record(event.data) ||
        !text(event.recordedAt) ||
        !Number.isFinite(Date.parse(event.recordedAt))
      )
        throw new Error('Invalid public event or mismatched Run identity.');
      if (pageCursor !== null && event.cursor !== pageCursor + 1)
        throw new Error('Event page contains a cursor gap or unordered events.');
      pageCursor = event.cursor;
      const prior = events.get(event.cursor);
      if (prior) {
        if (canonical(prior) !== canonical(event))
          throw new Error(`Conflicting event at cursor ${event.cursor}.`);
        duplicateEvents++;
      } else {
        if (event.cursor !== lastCursor + 1)
          throw new Error(`Missing event cursor ${lastCursor + 1}; export from after=0.`);
        if (terminalCursor !== null)
          throw new Error('Events appear after an authoritative terminal page.');
        events.set(event.cursor, event);
        lastCursor = event.cursor;
      }
    }
    if ((pageCursor !== null && pageCursor !== page.nextCursor) || page.nextCursor !== lastCursor)
      throw new Error('Page nextCursor conflicts with the exported events or regresses.');
    if (page.hasMore && !page.events.length)
      throw new Error('Page hasMore is true but its cursor does not advance.');
    if (page.hasMore && !duplicatePage && lastCursor === beforeCursor)
      throw new Error('Page hasMore is true but its cursor does not advance.');
    pageCopies.add(canonical(page));
    if (page.terminal) terminalCursor = page.nextCursor;
  }
  const lastPage = pages.at(-1);
  assertObservationIdentity(run, runId, workflow, 'run');
  assertObservationIdentity(result, runId, workflow, 'result');
  const visits = [],
    openVisits = new Map(),
    invocations = new Map();
  let missingVisitIds = 0,
    missingInvocationIds = 0,
    contextWindows = 0,
    unknownEvents = 0;
  const knownTypes = new Set([
    'run.created',
    'run.started',
    'run.suspended',
    'run.completed',
    'node.started',
    'node.completed',
    'node.progress',
    'agent.message.completed',
    'agent.progress',
    'tool.started',
    'tool.completed',
    'permission.requested',
    'permission.decided',
    'heartbeat',
    'warning',
    'error',
  ]);
  for (const event of events.values()) {
    const data = event.data,
      activity = data.activity,
      nodeId = text(data.nodeId),
      visitId = text(data.visitId),
      invocationId = text(data.invocationId);
    if (!knownTypes.has(event.type)) unknownEvents++;
    if (event.type === 'node.started' || event.type === 'node.completed') {
      if (!visitId) missingVisitIds++;
      const key = JSON.stringify([nodeId, visitId, data.replay === true]);
      let visit = visitId ? openVisits.get(key) : null;
      if (event.type === 'node.started' || !visit) {
        visit = {
          nodeId,
          visitId,
          ordinal: Number.isSafeInteger(data.ordinal) && data.ordinal > 0 ? data.ordinal : null,
          replay: typeof data.replay === 'boolean' ? data.replay : null,
          start: null,
          finish: null,
        };
        visits.push(visit);
      }
      if (event.type === 'node.started') {
        visit.start = event;
        if (visitId) openVisits.set(key, visit);
      } else {
        visit.finish = event;
        openVisits.delete(key);
      }
    }
    const invocationActivity = [
      'agent-task.started',
      'agent-task.finished',
      'invocation.started',
      'invocation.completed',
      'invocation.failed',
      'usage',
    ].includes(activity);
    if (activity === 'usage' && data.kind === 'context-window') {
      contextWindows++;
      continue;
    }
    if (invocationActivity && !invocationId) {
      missingInvocationIds++;
      continue;
    }
    if (!invocationId) continue;
    let invocation = invocations.get(invocationId);
    if (!invocation) {
      invocation = {
        invocationId,
        nodeId: null,
        agentId: null,
        sessionScope: null,
        parentIds: new Set(),
        taskStart: null,
        taskFinish: null,
        taskAcceptedValues: new Set(),
        taskResultIds: new Set(),
        transportStart: null,
        transportFinish: null,
        turnUsage: [],
        acpTerminalUsage: false,
        aggregateUsage: [],
      };
      invocations.set(invocationId, invocation);
    }
    if (text(data.parentInvocationId)) invocation.parentIds.add(data.parentInvocationId);
    for (const key of ['nodeId', 'agentId', 'sessionScope']) {
      const value = text(data[key]);
      if (value && invocation[key] && value !== invocation[key])
        throw new Error(`Conflicting ${key} for an invocation.`);
      if (value) invocation[key] = value;
    }
    if (activity === 'agent-task.started') invocation.taskStart ??= event;
    if (activity === 'agent-task.finished') {
      invocation.taskFinish ??= event;
      if (typeof data.accepted === 'boolean') invocation.taskAcceptedValues.add(data.accepted);
      if (text(data.resultInvocationId)) invocation.taskResultIds.add(data.resultInvocationId);
    }
    if (activity === 'invocation.started') invocation.transportStart ??= event;
    if (
      activity === 'invocation.completed' ||
      activity === 'invocation.failed' ||
      (event.type === 'error' && invocationId)
    )
      invocation.transportFinish ??= event;
    if (event.source.kind === 'agent-host' && data.usageStatus !== 'UNAVAILABLE') {
      if (activity === 'usage' && data.kind === 'turn') invocation.turnUsage.push(event);
      if (
        data.transport === 'acp' &&
        ['invocation.completed', 'invocation.failed'].includes(activity) &&
        record(data.usage)
      ) {
        invocation.acpTerminalUsage = true;
        invocation.turnUsage.push({ ...event, data: data.usage });
      }
      if (activity === 'invocation.completed' && data.transport === 'exec-jsonl')
        invocation.aggregateUsage.push(event);
    }
  }
  const agentInvocations = [...invocations.values()].map((invocation) => {
    // exec-jsonl may expose cumulative intermediate reports. Its completed aggregate owns
    // per-invocation accounting. ACP turn reports are merged once, never added together.
    const usageEvents = invocation.aggregateUsage.length
      ? invocation.aggregateUsage
      : invocation.turnUsage;
    const usage = Object.fromEntries(Object.keys(tokenFields).map((key) => [key, null]));
    const usageFieldStatus = Object.fromEntries(
      Object.keys(tokenFields).map((key) => [key, 'unknown']),
    );
    for (const event of usageEvents)
      for (const [field, aliases] of Object.entries(tokenFields)) {
        for (const alias of aliases) {
          const value = number(event.data[alias]);
          if (value === null) continue;
          if (usageFieldStatus[field] === 'conflict') continue;
          if (usage[field] !== null && usage[field] !== value) {
            usage[field] = null;
            usageFieldStatus[field] = 'conflict';
          } else {
            usage[field] = value;
            usageFieldStatus[field] = 'reported';
          }
        }
      }
    const [start, finish] = invocationInterval(invocation);
    return {
      invocationId: invocation.invocationId,
      parentInvocationId: invocation.parentIds.size === 1 ? [...invocation.parentIds][0] : null,
      attributionStatus: invocation.parentIds.size > 1 ? 'conflict' : 'observed',
      resultInvocationId:
        invocation.taskResultIds.size === 1 ? [...invocation.taskResultIds][0] : null,
      nodeId: invocation.nodeId,
      agentId: invocation.agentId,
      startedCursor: start?.cursor ?? null,
      finishedCursor: finish?.cursor ?? null,
      accepted:
        invocation.taskAcceptedValues.size === 1 ? [...invocation.taskAcceptedValues][0] : null,
      transportOutcome: invocation.transportFinish
        ? invocation.transportFinish.type === 'error' ||
          invocation.transportFinish.data.activity === 'invocation.failed'
          ? 'failed'
          : 'completed'
        : null,
      observedElapsedMs: elapsed(start, finish),
      observedUsage: usage,
      usageFieldStatus,
      conflictScope: Object.values(usageFieldStatus).includes('conflict')
        ? 'invocation-field'
        : null,
      usageSource: usageEvents.length
        ? invocation.aggregateUsage.length
          ? 'exec-jsonl-completed-aggregate'
          : invocation.acpTerminalUsage
            ? 'acp-terminal-or-turn'
            : 'reported-turn'
        : null,
    };
  });
  const byId = new Map(agentInvocations.map((call) => [call.invocationId, call]));
  const tasks = [...invocations.values()].filter(
    (invocation) => invocation.taskStart || invocation.taskFinish,
  );
  let attributionGaps = 0;
  for (const call of agentInvocations) {
    call.actualHostCall = Boolean(
      invocations.get(call.invocationId).transportStart ||
      invocations.get(call.invocationId).transportFinish ||
      call.usageSource,
    );
    call.acceptedOutput = null;
    if (
      (call.parentInvocationId &&
        (!tasks.some((task) => task.invocationId === call.parentInvocationId) ||
          call.parentInvocationId === call.invocationId ||
          invocations.get(call.parentInvocationId)?.parentIds.size)) ||
      (call.actualHostCall &&
        !call.parentInvocationId &&
        call.attributionStatus === 'observed' &&
        !tasks.some((task) => task.invocationId === call.invocationId))
    )
      call.attributionStatus = 'unknown';
    if (call.attributionStatus !== 'observed') attributionGaps++;
  }
  const managedTasks = tasks.map((task) => {
    const parent = byId.get(task.invocationId);
    const calls = agentInvocations.filter(
      (call) =>
        call.actualHostCall &&
        call.attributionStatus === 'observed' &&
        (call.invocationId === task.invocationId || call.parentInvocationId === task.invocationId),
    );
    const resultId = parent.resultInvocationId;
    const resultCall = calls.find((call) => call.invocationId === resultId);
    if (resultCall && parent.accepted !== null)
      for (const call of calls) call.acceptedOutput = call === resultCall ? parent.accepted : false;
    return {
      invocationId: task.invocationId,
      nodeId: parent.nodeId,
      agentId: parent.agentId,
      startedCursor: task.taskStart?.cursor ?? null,
      finishedCursor: task.taskFinish?.cursor ?? null,
      accepted: parent.accepted,
      resultInvocationId: resultCall ? resultId : null,
      resultAttributionStatus:
        task.taskResultIds.size > 1
          ? 'conflict'
          : resultId
            ? resultCall
              ? 'observed'
              : 'conflict'
            : 'unknown',
      hostInvocationIds: calls.map((call) => call.invocationId),
      observedUsage: Object.fromEntries(
        Object.keys(tokenFields).map((field) => {
          const values = calls
            .map((call) => call.observedUsage[field])
            .filter((value) => value !== null);
          return [field, values.length ? values.reduce((sum, value) => sum + value, 0) : null];
        }),
      ),
      usageFieldCoverage: Object.fromEntries(
        Object.keys(tokenFields).map((field) => [
          field,
          {
            reported: calls.filter((call) => call.usageFieldStatus[field] === 'reported').length,
            unknown: calls.filter((call) => call.usageFieldStatus[field] === 'unknown').length,
            conflict: calls.filter((call) => call.usageFieldStatus[field] === 'conflict').length,
            total: calls.length,
          },
        ]),
      ),
    };
  });
  attributionGaps += managedTasks.filter(
    (task) => task.resultAttributionStatus !== 'observed',
  ).length;
  attributionGaps += tasks.filter((task) => task.taskAcceptedValues.size > 1).length;
  const nodeVisits = visits.map((visit) => ({
    nodeId: visit.nodeId,
    visitId: visit.visitId,
    ordinal: visit.ordinal,
    replay: visit.replay,
    startedCursor: visit.start?.cursor ?? null,
    finishedCursor: visit.finish?.cursor ?? null,
    durationMs: number(visit.finish?.data.durationMs),
    observedElapsedMs: elapsed(visit.start, visit.finish),
  }));
  const missingStarts = nodeVisits.filter((visit) => visit.startedCursor === null).length;
  const missingFinishes = nodeVisits.filter((visit) => visit.finishedCursor === null).length;
  const lifecycleInvocations = tasks.map((task) => byId.get(task.invocationId));
  const missingAgentStarts = lifecycleInvocations.filter(
    (invocation) => invocation.startedCursor === null,
  ).length;
  const missingAgentFinishes = lifecycleInvocations.filter(
    (invocation) => invocation.finishedCursor === null,
  ).length;
  const totals = {},
    fieldCoverage = {};
  const actualCalls = agentInvocations.filter((call) => call.actualHostCall);
  for (const field of Object.keys(tokenFields)) {
    const values = actualCalls
      .map((invocation) => invocation.observedUsage[field])
      .filter((value) => value !== null);
    totals[field] = values.length ? values.reduce((sum, value) => sum + value, 0) : null;
    fieldCoverage[field] = {
      reported: values.length,
      unknown: actualCalls.filter((call) => call.usageFieldStatus[field] === 'unknown').length,
      conflict: actualCalls.filter((call) => call.usageFieldStatus[field] === 'conflict').length,
      total: actualCalls.length,
    };
  }
  const reported = actualCalls.filter((invocation) =>
    Object.values(invocation.observedUsage).some((value) => value !== null),
  ).length;
  const intervals = [...invocations.values()].flatMap((invocation) => {
    const [start, finish] = invocationInterval(invocation);
    return elapsed(start, finish) !== null
      ? [[Date.parse(start.recordedAt), Date.parse(finish.recordedAt)]]
      : [];
  });
  const degraded =
    lastPage.hasMore ||
    missingVisitIds ||
    missingInvocationIds ||
    missingStarts ||
    missingFinishes ||
    missingAgentStarts ||
    missingAgentFinishes ||
    unknownEvents ||
    attributionGaps;
  return {
    schemaVersion: 'pico-workflow-event-summary/v2',
    workflow,
    runId,
    lastCursor,
    terminal: {
      observed: lastPage.terminal,
      runStatus: text(run?.status) ?? text(result?.runStatus),
      resultAvailable: result === null ? null : result.available !== false,
      outcome: terminalResultOutcome(result),
    },
    eventCoverage: {
      scope: 'persisted-events-only',
      status: degraded ? 'degraded' : 'observed',
      exportComplete: !lastPage.hasMore,
      uniqueEvents: events.size,
      duplicateEvents,
      missingNodeVisitIds: missingVisitIds,
      missingNodeStarts: missingStarts,
      missingNodeFinishes: missingFinishes,
      missingInvocationIds,
      missingAgentStarts,
      missingAgentFinishes,
      unknownEventTypes: unknownEvents,
      attributionGaps,
      managedTaskCount: managedTasks.length,
      actualHostCallCount: agentInvocations.filter((call) => call.actualHostCall).length,
    },
    nodeVisits,
    agentInvocations,
    managedTasks,
    control: summarizeWorkflowControl(
      [...events.values()],
      runId,
      { outcome: terminalResultOutcome(result) },
      lastPage,
    ),
    observedUsage: {
      status:
        reported === 0
          ? 'unknown'
          : Object.values(fieldCoverage).some((coverage) => coverage.reported < coverage.total)
            ? 'partial'
            : 'reported',
      reportedInvocations: reported,
      totalInvocations: actualCalls.length,
      totals,
      fieldCoverage,
      excludedContextWindowObservations: contextWindows,
    },
    timing: {
      agentObservedMs: intervals.length ? unionDuration(intervals) : null,
      queueMs: null,
      modelInferenceMs: null,
      cost: null,
    },
    classification: {
      replayExecutions: nodeVisits.some(
        (visit) => visit.startedCursor !== null && visit.replay === null,
      )
        ? null
        : nodeVisits.filter((visit) => visit.startedCursor !== null && visit.replay === true)
            .length,
      businessRepairCount: null,
      reportCorrectionCount: null,
      businessMappingStatus: 'not-adopted',
      deliveryComplete: false,
    },
    unknownFields: [
      'queueMs',
      'modelInferenceMs',
      'cost',
      'businessRepairCount',
      'reportCorrectionCount',
      ...(!text(run?.status) && !text(result?.runStatus) ? ['runStatus'] : []),
      ...(!result || result.available === false ? ['resultOutcome'] : []),
      ...(lastPage.hasMore ? ['eventExport'] : []),
      ...Object.keys(tokenFields)
        .filter(
          (field) => fieldCoverage[field].reported < actualCalls.length || !actualCalls.length,
        )
        .map((field) => `usage.${field}`),
    ],
  };
}

/** Only an available Result establishes terminal outcome; a Run snapshot never does. */
function terminalResultOutcome(result) {
  if (!result || result.available === false) return null;
  if (result.schemaVersion === 'pico-workflow-result/v1') return text(result.outcome);
  if (result.schemaVersion === 'pico-workflow-run-result/v0')
    return ['SUCCEEDED', 'PARTIAL', 'BLOCKED', 'FAILED', 'CANCELLED'].includes(result.status)
      ? result.status
      : null;
  return null;
}

function invocationInterval(invocation) {
  return invocation.taskStart || invocation.taskFinish
    ? [invocation.taskStart, invocation.taskFinish]
    : [invocation.transportStart, invocation.transportFinish];
}

function unionDuration(intervals) {
  let total = 0,
    end = -Infinity;
  for (const [from, to] of intervals.sort((a, b) => a[0] - b[0])) {
    total += Math.max(0, to - Math.max(from, end));
    end = Math.max(end, to);
  }
  return total;
}

function assertObservationIdentity(observation, runId, workflow, role) {
  if (observation === null) return;
  const schemas =
    role === 'run'
      ? ['pico-workflow-run/v1']
      : ['pico-workflow-result/v1', 'pico-workflow-result-read/v1', 'pico-workflow-run-result/v0'];
  if (!record(observation) || !schemas.includes(observation.schemaVersion))
    throw new Error(`Invalid ${role} file schema.`);
  if (observation.runId !== runId)
    throw new Error('Run/Result identity does not match the event pages.');
  const name = observation.workflowId ?? observation.workflow?.name;
  const version = observation.workflowVersion ?? observation.workflow?.version;
  if (
    (name !== undefined && name !== workflow.name) ||
    (version !== undefined && version !== workflow.version)
  )
    throw new Error('Run/Result Workflow identity does not match the event pages.');
}

function main(args) {
  if (args.includes('--help')) {
    console.log(
      'Usage: node summarize-workflow-events.mjs --output <new-summary.json> [--run <run.json>] [--result <result.json>] <page-1.json> [page-2.json ...]\nRead explicit JSON exports offline. Files must start at cursor 1 and be listed in export order. Output must not exist.',
    );
    return;
  }
  const files = [],
    options = {};
  for (let index = 0; index < args.length; index++) {
    const argument = args[index];
    if (['--output', '--run', '--result'].includes(argument)) {
      if (!args[index + 1] || args[index + 1].startsWith('--') || options[argument])
        throw new Error(`Invalid ${argument} option.`);
      options[argument] = args[++index];
    } else if (argument.startsWith('--')) throw new Error('Unknown summary option.');
    else files.push(argument);
  }
  if (!options['--output'] || !files.length)
    throw new Error('Supply --output and explicit event page files; use --help for usage.');
  const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
  const summary = summarizeWorkflowEventPages(files.map(read), {
    run: options['--run'] ? read(options['--run']) : null,
    result: options['--result'] ? read(options['--result']) : null,
  });
  fs.writeFileSync(options['--output'], JSON.stringify(summary, null, 2) + '\n', { flag: 'wx' });
}

if (
  process.argv[1] &&
  fs.realpathSync(process.argv[1]) === fs.realpathSync(fileURLToPath(import.meta.url))
) {
  try {
    main(process.argv.slice(2));
  } catch (error) {
    console.error(`Workflow summary failed: ${error.message}`);
    process.exitCode = 1;
  }
}
