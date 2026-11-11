/* Copyright 2026 PICO. SPDX-License-Identifier: Apache-2.0 */
import { createHash } from 'node:crypto';

const activities = {
  'pause.requested': 'pauseRequestedCount',
  'pause.reached': 'effectivePauseCount',
  'pause.released': 'pauseReleasedCount',
  'pause.missed': 'pauseMissedCount',
  'resume.accepted': 'resumeAcceptedCount',
};
const canonical = (value) =>
  JSON.stringify(value, (_, item) =>
    item && typeof item === 'object' && !Array.isArray(item)
      ? Object.fromEntries(
          Object.keys(item)
            .sort()
            .map((key) => [key, item[key]]),
        )
      : item,
  );
const identifier = (value) => typeof value === 'string' && value.length > 0;

/** Consume only the control publisher's fixed, committed facts, never repair a log. */
export function summarizeWorkflowControl(events, runId, terminal, page = {}) {
  const identities = new Map(),
    valid = new Map(),
    conflicts = new Set();
  const gaps = [];
  const unknown = new Set();
  let duplicatePublications = 0;
  for (const event of events) {
    const d = event.data,
      activity = d.activity;
    const first = event.type === 'node.started' && d.continuationFirst === true;
    const metric =
      event.type === 'node.progress'
        ? activities[activity]
        : first
          ? 'resumeContinuedCount'
          : undefined;
    if (!metric) continue;
    const source = event.source.kind === 'workflow-runtime' && event.source.name === 'control';
    const pause = typeof activity === 'string' && activity.startsWith('pause.');
    const tuple = pause
      ? [runId, d.requestId, activity]
      : [runId, d.operationRequestId, first ? 'resume.first-node-started' : activity];
    const publicationId = createHash('sha256').update(canonical(tuple)).digest('hex');
    let okay =
      source &&
      identifier(pause ? d.requestId : d.operationRequestId) &&
      d.publicationId === publicationId &&
      Number.isSafeInteger(d.revision) &&
      d.revision >= 0 &&
      identifier(d.committedAt) &&
      Number.isFinite(Date.parse(d.committedAt));
    if (pause)
      okay &&=
        d.boundary === 'node-dispatch' &&
        (d.beforeNode === null || identifier(d.beforeNode)) &&
        (d.actualNext === null || identifier(d.actualNext));
    if (activity === 'pause.reached')
      okay &&=
        identifier(d.actualNext) &&
        d.taskId === 'system:pause' &&
        d.handoffKind === 'system-recovery';
    if (activity === 'pause.released')
      okay &&=
        identifier(d.actualNext) &&
        d.taskId === 'system:pause' &&
        Number.isSafeInteger(d.pauseRevision) &&
        d.pauseRevision >= 0 &&
        identifier(d.operationRequestId);
    if (activity === 'resume.accepted')
      okay &&=
        identifier(d.taskId) &&
        Number.isSafeInteger(d.pauseRevision) &&
        d.pauseRevision >= 0 &&
        (d.taskId !== 'system:pause' || identifier(d.pauseRequestId));
    if (first)
      okay &&=
        identifier(d.nodeId) &&
        identifier(d.visitId) &&
        Number.isSafeInteger(d.ordinal) &&
        d.ordinal > 0 &&
        typeof d.replay === 'boolean';
    if (!okay) {
      unknown.add(metric);
      gaps.push({ metric, cursor: event.cursor, reason: 'invalid-control-source-or-identity' });
      continue;
    }
    const signature = canonical({ type: event.type, source: event.source, data: d });
    const prior = identities.get(publicationId);
    if (prior && prior !== signature) {
      conflicts.add(metric);
      valid.delete(publicationId);
      gaps.push({ metric, cursor: event.cursor, reason: 'conflicting-control-publication' });
      continue;
    }
    if (prior) {
      duplicatePublications++;
      continue;
    }
    identities.set(publicationId, signature);
    valid.set(publicationId, {
      metric,
      operation: d.operationRequestId,
      request: d.requestId ?? d.pauseRequestId,
    });
  }
  const knownOutcome = [
    'completed',
    'partial',
    'blocked',
    'failed',
    'cancelled',
    'SUCCEEDED',
    'PARTIAL',
    'BLOCKED',
    'FAILED',
    'CANCELLED',
  ].includes(terminal.outcome);
  const complete =
    knownOutcome &&
    page.terminal === true &&
    page.hasMore === false &&
    (page.pendingControlPublications === 0 ||
      (!Object.hasOwn(page, 'pendingControlPublications') &&
        events.some((event) => event.type === 'run.completed')));
  const counts = Object.fromEntries(
    [...Object.values(activities), 'resumeContinuedCount'].map((metric) => {
      const count = [...valid.values()].filter((value) => value.metric === metric).length;
      return [
        metric,
        conflicts.has(metric) || unknown.has(metric) || (!count && !complete) ? null : count,
      ];
    }),
  );
  const accepted = [...valid.values()].filter((value) => value.metric === 'resumeAcceptedCount');
  const continued = [...valid.values()].filter((value) => value.metric === 'resumeContinuedCount');
  const matches = (parent, first) =>
    parent.operation === first.operation && (!parent.request || parent.request === first.request);
  for (const value of continued) {
    if (!accepted.some((parent) => matches(parent, value))) {
      counts.resumeContinuedCount = null;
      gaps.push({ metric: 'resumeContinuedCount', reason: 'missing-matching-resume-accepted' });
    }
  }
  for (const value of accepted) {
    if (!continued.some((first) => matches(value, first))) {
      counts.resumeContinuedCount = null;
      gaps.push({
        metric: 'resumeContinuedCount',
        operationRequestId: value.operation,
        reason: 'missing-first-node-started',
      });
    }
  }
  const status = terminal.outcome;
  counts.cancelledRunCount =
    status === 'cancelled' || status === 'CANCELLED'
      ? 1
      : status &&
          [
            'completed',
            'partial',
            'blocked',
            'failed',
            'SUCCEEDED',
            'PARTIAL',
            'BLOCKED',
            'FAILED',
          ].includes(status)
        ? 0
        : null;
  return {
    counts,
    scope: 'persisted-public-control-facts',
    duplicatePublications,
    gaps,
    unknownMetrics: Object.keys(counts).filter((key) => counts[key] === null),
  };
}
