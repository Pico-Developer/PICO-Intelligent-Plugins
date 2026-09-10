# Perfetto Trace Basics for Performance Analysis

This document records the Perfetto Trace Processor basics that must be respected before writing SQL, choosing a time window, or drawing conclusions from query results. It is intentionally short: use it as a guardrail, then continue with the topic-specific SQL guides.

## How to Use `base-query.md`

Use [Perfetto Basic Query Guide](../sql-query/base-query.md) as the first SQL toolbox after reading this document. This basics document defines the rules for time windows, identity columns, joins, and empty-result debugging; `base-query.md` provides reusable SQL snippets for applying those rules to a real trace.

Start with `base-query.md` when you need to:

- List available tables/views and inspect table schemas.
- Confirm target process identity (`pid` / `upid`) from a package name.
- Enumerate threads and pin the real frame-driving `utid`.
- Inspect tracks (`thread_track`, `process_track`) before joining slices.
- Query slices or `thread_state` in a verified time window.
- Find counters, metadata, trace bounds, or other basic evidence before entering a topic-specific workflow.

Do not treat `base-query.md` as a replacement for topic protocols such as Spatial Engine, App Jank, Binder, Memory, CPU Scheduling, or Spatial Audio. Use it to solidify trace identity and window facts first, then continue with the relevant topic SQL guide. If a `base-query.md` query returns no rows, apply the empty-result checklist in this document before changing tools or conclusions.

## 1. Timebase and Units

- Perfetto `ts` and `dur` fields are in nanoseconds unless a query explicitly converts them.
- `ts` is on the trace processor timeline for the currently loaded trace/session. It is not wall-clock time and should not be treated as a human timestamp.
- `dur_ms` fields in this Skill are derived display fields, usually `ROUND(dur / 1000000.0, 3)`. Do not feed rounded `dur_ms` values back into ns-window SQL.
- Do not manually invent, round, or normalize absolute windows such as `s.ts BETWEEN 1250000000 AND 1260000000` unless both bounds came from verified rows in the same loaded session.

## 2. Window Anchoring

When drilling down from an abnormal frame, slice, Binder call, GC pause, or scheduling event, first choose an anchor row and derive the window from that row:

```sql
SELECT
  s.ts AS window_start_ns,
  s.ts + s.dur AS window_end_ns,
  s.dur AS dur_ns
FROM slice s
WHERE s.id = <anchor_slice_id>;
```

Prefer keeping the anchor and drill-down in the same SQL statement:

```sql
WITH anchor AS (
  SELECT s.ts AS start_ns, s.ts + s.dur AS end_ns
  FROM slice s
  WHERE s.id = <anchor_slice_id>
)
SELECT child.ts, child.dur, child.name
FROM slice child
JOIN thread_track tt ON child.track_id = tt.id
JOIN anchor
WHERE tt.utid = <target_utid>
  AND child.ts < anchor.end_ns
  AND child.ts + child.dur > anchor.start_ns
ORDER BY child.ts;
```

This avoids mistakes caused by copying rounded timestamps, mixing sessions, or using a visually nearby but incorrect range.

## 3. Overlap Semantics

Use interval overlap when checking whether an event happened inside a window:

```sql
event.ts < window_end_ns
AND event.ts + event.dur > window_start_ns
```

Avoid using only `event.ts BETWEEN window_start_ns AND window_end_ns`. A long event that starts before the window and continues into it is still relevant, especially for `thread_state`, Binder waits, GC pauses, and parent slices.

For overlap duration, clamp both sides:

```sql
MAX(event.ts, window_start_ns) AS overlap_start_ns,
MIN(event.ts + event.dur, window_end_ns) AS overlap_end_ns
```

Only count rows where `overlap_end_ns > overlap_start_ns`.

## 4. Identity Columns

- `pid` / `tid` are system IDs. They can be reused across time and should not be the primary join key inside Perfetto SQL.
- `upid` / `utid` are Perfetto internal IDs. Prefer them for joins against `process`, `thread`, `thread_track`, `slice`, and `thread_state`.
- A thread name such as `main` is not enough evidence. Spatial apps may drive frames from a package-named frame-driving thread. Use `trace-probe-detail.yaml` or an identity query to pin `utid`.
- A process or thread may have `start_ts` / `end_ts`; if multiple rows match a package or name, use the row whose lifetime overlaps the issue window.

## 5. Track and Slice Joins

Thread slices normally require this join pattern:

```sql
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
```

Do not assume every `slice.track_id` is a `thread_track`. Some slices belong to process tracks or other track types. If a query unexpectedly returns no rows, inspect `track`, `thread_track`, and `process_track` instead of immediately changing tools.

## 6. Empty Result Checklist

When a query unexpectedly returns no rows, validate in this order through `pico-cli perf trace query`:

1. Confirm the same session is still loaded and queryable.
2. Check `trace_bounds` or table-specific `MIN(ts), MAX(ts), COUNT(*)`.
3. Re-query the exact anchor row by stable ID or by all identifying fields.
4. Confirm `upid` / `utid` and track joins.
5. Relax only one filter at a time: process, thread, slice name, duration threshold, then time window.

An empty window query is not evidence that `pico-cli perf` is unstable, and it is not a reason to switch to `trace_processor_shell`.

## 7. Tooling Contract

For this Skill, normal trace SQL must go through `pico-cli perf trace query` after `pico-cli perf trace load`. Some diagnostic tables, such as `OpenXRClientSpatialFrames`, are produced by `pico-cli perf trace load --spatial-diagnose true`; direct `trace_processor_shell` sessions may not contain them.
