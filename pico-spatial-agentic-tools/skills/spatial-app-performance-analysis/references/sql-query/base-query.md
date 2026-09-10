# Perfetto Basic Query Guide

> Note: This file collects basic Perfetto Trace Processor (SQL) troubleshooting queries. It is used to quickly pin down identity information for processes, threads, tracks, slices, counters, etc., before entering a formal topic analysis.
>
> - Applicable to: PICO OS6 / Spatial App performance analysis (the trace has been imported into Perfetto / trace_processor can execute SQL).
> - Convention: `${xxx}` in SQL represents parameters (injected by script/manual replacement). For string parameters, keep quotes when appropriate; for example, `${app_package}` can be replaced with `'com.xxx.yyy'`.
> - Time unit: Perfetto uses ns by default; the `dur_ms` field is only for human readability.
> - Reminder: Slice/track naming may differ across trace versions. If a query returns nothing, first use the track/basic-info queries in this document to confirm the naming, then fine-tune the filter conditions.
> - Execution contract: run these SQL snippets through `pico-cli perf trace query --session <sessionId> --sql "..."` after `pico-cli perf trace load`. If the daemon/session is gone, restart the daemon and reload the trace; do not invoke `trace_processor_shell` directly during normal analysis.
> - Before adapting or interpreting these queries, follow [Perfetto Trace Basics](../common/perfetto-trace-basics.md).
> - Timestamp anchoring: `ts` values are Perfetto trace-processor nanoseconds in the current loaded session. Do not manually round or invent absolute windows. When drilling down from an abnormal slice/frame, derive `${window_start_ns}` and `${window_end_ns}` from the exact anchor row (`s.ts`, `s.ts + s.dur`) or keep the anchor in a CTE in the same SQL. If a window query returns no rows, validate `trace_bounds`, table-specific `MIN/MAX(ts)`, and the exact anchor row in `pico-cli perf trace query` before changing tools or conclusions.

---

## 1. Check what tables/views are currently available

### Purpose

### SQL

```sql
SELECT name, type
FROM sqlite_master
ORDER BY type, name;

```

## 2. View the field structure of a table

### Purpose

View field list of the table.

### Parameters
- `${table_name}`

### SQL

```sql
PRAGMA table_info(${table_name});
```

## 3. Given a Package Name, Query Process pid / upid / Process Name

### Purpose
- Confirm the process identity in the trace based on the App package name.
- Suitable for pinning down `pid / upid / process_name` at the beginning of analysis.

### Parameters
- `${app_package}`: target package name or process name, e.g. `'com.xxx.yyy'`.

### Returned Fields
- `process_name`: the process name recorded in the trace.
- `pid`: system process ID.
- `upid`: Perfetto internal process ID; prefer it for subsequent joins.
- `start_ts / end_ts`: process lifecycle timestamps (ns); may be empty.

### SQL
```sql
-- Query target process pid / upid / process name by package name
-- Depends on: process

SELECT
  p.name AS process_name,
  p.pid,
  p.upid,
  p.start_ts,
  p.end_ts
FROM process p
WHERE p.name = ${app_package}
   OR p.name GLOB ${app_package} || '*'
ORDER BY p.start_ts ASC, p.pid ASC;
```

---

## 4. Given a Package Name, Query All Threads (tid / utid / Thread Name)

### Purpose
- Enumerate all threads under the target process to confirm identities such as the main thread, render threads, Binder threads, and business threads.

### Parameters
- `${app_package}`: target package name or process name, e.g. `'com.xxx.yyy'`.

### Returned Fields
- `process_name / pid / upid`: process identity.
- `thread_name`: thread name.
- `tid`: system thread ID.
- `utid`: Perfetto internal thread ID; prefer it for subsequent slice / thread_state queries.
- `is_main_thread`: whether it is the main thread.

### SQL
```sql
-- Query all threads of the target process by package name
-- Depends on: process / thread

SELECT
  p.name AS process_name,
  p.pid,
  p.upid,
  t.name AS thread_name,
  t.tid,
  t.utid,
  t.is_main_thread
FROM thread t
JOIN process p ON t.upid = p.upid
WHERE p.name = ${app_package}
   OR p.name GLOB ${app_package} || '*'
ORDER BY t.is_main_thread DESC, t.name ASC, t.tid ASC;
```

---

## 5. Given a Package Name, Query Frame-Driving Thread (Choreographer#doFrame or beginSpatialFrame Source)

### Purpose
- Find the actual frame-driving thread in the App process, to avoid hardcoding the thread name `main`.
- The result can be used as a manual validation reference for `trace-probe-detail.yaml`’s `identities.app_frame_driving_threads.candidates[0].utid`.

### Parameters
- `${app_package}`: target package name or process name, e.g. `'com.xxx.yyy'`.
- `${window_start_ns}`: window start (ns). Use `0` if no limit.
- `${window_end_ns}`: window end (ns). Use a sufficiently large value if no limit.

### Returned Fields
- `thread_name / tid / utid`: candidate frame-driving thread identity.
- `frame_slice_count`: number of matched frame-related slices.
- `first_ts / last_ts`: earliest/latest matched frame-related slice timestamps for that thread.
- `avg_dur_ms / max_dur_ms`: duration overview for frame-related slices.
- `matched_slice_names`: typical matched slice names.

### SQL
```sql
-- Find candidate frame-driving threads by package name: Choreographer#doFrame or beginSpatialFrame source
-- Depends on: slice / thread_track / thread / process

WITH frame_slices AS (
  SELECT
    p.name AS process_name,
    p.pid,
    p.upid,
    t.name AS thread_name,
    t.tid,
    t.utid,
    s.name AS slice_name,
    s.ts,
    s.dur
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE (p.name = ${app_package} OR p.name GLOB ${app_package} || '*')
    AND s.ts < ${window_end_ns}
    AND s.ts + s.dur > ${window_start_ns}
    AND (
      s.name GLOB '*Choreographer#doFrame*'
      OR s.name GLOB '*beginSpatialFrame*'
    )
)
SELECT
  process_name,
  pid,
  upid,
  thread_name,
  tid,
  utid,
  COUNT(*) AS frame_slice_count,
  MIN(ts) AS first_ts,
  MAX(ts) AS last_ts,
  ROUND(AVG(dur) / 1000000.0, 3) AS avg_dur_ms,
  ROUND(MAX(dur) / 1000000.0, 3) AS max_dur_ms,
  GROUP_CONCAT(DISTINCT slice_name) AS matched_slice_names
FROM frame_slices
GROUP BY process_name, pid, upid, thread_name, tid, utid
ORDER BY frame_slice_count DESC, max_dur_ms DESC;
```

---

## 6. Given utid, Query Thread Name / tid

### Purpose
- When `utid` is known, look up the thread name, system thread ID, and owning process.

### Parameters
- `${utid}`: Perfetto internal thread ID.

### SQL
```sql
-- Reverse lookup thread name / tid / owning process by utid
-- Depends on: thread / process

SELECT
  t.name AS thread_name,
  t.tid,
  t.utid,
  t.is_main_thread,
  p.name AS process_name,
  p.pid,
  p.upid
FROM thread t
LEFT JOIN process p ON t.upid = p.upid
WHERE t.utid = ${utid};
```

---

## 7. Given pid, Query upid (and Reverse Lookup)

### Purpose
- Convert between system `pid` and Perfetto internal `upid`.

### SQL: pid -> upid
```sql
-- Query upid by pid
-- Depends on: process

SELECT
  p.name AS process_name,
  p.pid,
  p.upid,
  p.start_ts,
  p.end_ts
FROM process p
WHERE p.pid = ${pid}
ORDER BY p.start_ts ASC;
```

### SQL: upid -> pid
```sql
-- Reverse lookup pid by upid
-- Depends on: process

SELECT
  p.name AS process_name,
  p.pid,
  p.upid,
  p.start_ts,
  p.end_ts
FROM process p
WHERE p.upid = ${upid};
```

---

## 8. Query All Track Names (thread_track / process_track)

### Purpose
- View all thread track and process track names in the trace, and troubleshoot track naming for slices.

### SQL
```sql
-- Query all thread_track / process_track names
-- Depends on: thread_track / process_track / thread / process

SELECT
  'thread_track' AS track_kind,
  tt.id AS track_id,
  tt.name AS track_name,
  p.name AS process_name,
  p.pid,
  p.upid,
  t.name AS thread_name,
  t.tid,
  t.utid
FROM thread_track tt
JOIN thread t ON tt.utid = t.utid
LEFT JOIN process p ON t.upid = p.upid

UNION ALL

SELECT
  'process_track' AS track_kind,
  pt.id AS track_id,
  pt.name AS track_name,
  p.name AS process_name,
  p.pid,
  p.upid,
  NULL AS thread_name,
  NULL AS tid,
  NULL AS utid
FROM process_track pt
JOIN process p ON pt.upid = p.upid

ORDER BY track_kind, process_name, thread_name, track_name;
```

---

## 9. Given utid, Query All Slices in a Time Window (Including Hierarchy Depth)

### Purpose
- View the full slice stack of a thread within a specified time window, including `depth / parent_id`, to locate the time-consuming hierarchy.
- `${window_start_ns}` / `${window_end_ns}` should come from a verified anchor row in the same session. Avoid hand-written rounded windows such as `BETWEEN 1250000000 AND 1260000000`, because they can silently select the wrong part of the Perfetto timeline.

### SQL
```sql
-- Query all slices in a time window by utid, including hierarchy depth
-- Depends on: slice / thread_track

SELECT
  s.id AS slice_id,
  s.parent_id,
  s.depth,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms,
  MAX(s.ts, ${window_start_ns}) AS overlap_start_ns,
  MIN(s.ts + s.dur, ${window_end_ns}) AS overlap_end_ns,
  ROUND((MIN(s.ts + s.dur, ${window_end_ns}) - MAX(s.ts, ${window_start_ns})) / 1000000.0, 3) AS overlap_dur_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
WHERE tt.utid = ${utid}
  AND s.ts < ${window_end_ns}
  AND s.ts + s.dur > ${window_start_ns}
  AND s.dur IS NOT NULL
ORDER BY s.ts ASC, s.depth ASC, s.dur DESC;
```

---

## 10. Given utid, Summarize Thread State Distribution in a Time Window

### Purpose
- Determine whether the target thread is mostly running, runnable, sleeping, or uninterruptible within the window.

### SQL
```sql
-- Summarize thread state distribution in a time window by utid
-- Depends on: thread_state

WITH states AS (
  SELECT
    ts.state,
    ts.io_wait,
    ts.blocked_function,
    MAX(ts.ts, ${window_start_ns}) AS overlap_start_ns,
    MIN(ts.ts + ts.dur, ${window_end_ns}) AS overlap_end_ns
  FROM thread_state ts
  WHERE ts.utid = ${utid}
    AND ts.ts < ${window_end_ns}
    AND ts.ts + ts.dur > ${window_start_ns}
), bucketed AS (
  SELECT
    CASE
      WHEN state = 'Running' THEN 'running'
      WHEN state = 'R' THEN 'runnable'
      WHEN state = 'D' THEN 'uninterruptible'
      WHEN state = 'S' THEN 'sleeping'
      ELSE 'other'
    END AS state_bucket,
    state,
    io_wait,
    blocked_function,
    overlap_end_ns - overlap_start_ns AS overlap_dur
  FROM states
  WHERE overlap_end_ns > overlap_start_ns
)
SELECT
  state_bucket,
  ROUND(SUM(overlap_dur) / 1000000.0, 3) AS overlap_ms,
  ROUND(100.0 * SUM(overlap_dur) / (${window_end_ns} - ${window_start_ns}), 1) AS pct_of_window,
  GROUP_CONCAT(DISTINCT state) AS raw_states,
  GROUP_CONCAT(DISTINCT blocked_function) AS blocked_functions
FROM bucketed
GROUP BY state_bucket
ORDER BY overlap_ms DESC;
```

---

## 11. Query All Counter Track Names (Given a Package Name)

### Purpose
- Query counter track names associated with the target process, to locate counter data such as memory, frequency, FPS, and custom metrics.

### SQL
```sql
-- Query all counter track names associated with a given package name
-- Depends on: counter_track / counter / process_counter_track / process

SELECT
  ct.id AS track_id,
  ct.name AS track_name,
  p.name AS process_name,
  p.pid,
  p.upid,
  COUNT(c.ts) AS sample_count,
  MIN(c.ts) AS first_ts,
  MAX(c.ts) AS last_ts
FROM counter_track ct
LEFT JOIN process_counter_track pct ON ct.id = pct.id
LEFT JOIN process p ON pct.upid = p.upid
LEFT JOIN counter c ON c.track_id = ct.id
WHERE p.name = ${app_package}
   OR p.name GLOB ${app_package} || '*'
GROUP BY ct.id, ct.name, p.name, p.pid, p.upid
ORDER BY process_name, track_name;
```

---

## 12. Process / Thread Basic Info Summary (A Quick Overview SQL)

### Purpose
- A single SQL query to quickly overview the processes/threads related to the target package name, including thread_track count, slice count, and thread_state coverage.

### SQL
```sql
-- Quick overview of process / thread basic info for the target package name
-- Depends on: process / thread / thread_track / slice / thread_state

WITH target_process AS (
  SELECT
    p.upid,
    p.pid,
    p.name AS process_name,
    p.start_ts,
    p.end_ts
  FROM process p
  WHERE p.name = ${app_package}
     OR p.name GLOB ${app_package} || '*'
), thread_base AS (
  SELECT
    tp.process_name,
    tp.pid,
    tp.upid,
    tp.start_ts,
    tp.end_ts,
    t.utid,
    t.tid,
    t.name AS thread_name,
    t.is_main_thread
  FROM target_process tp
  JOIN thread t ON t.upid = tp.upid
), slice_by_thread AS (
  SELECT
    tb.utid,
    COUNT(s.id) AS slice_count
  FROM thread_base tb
  LEFT JOIN thread_track tt ON tt.utid = tb.utid
  LEFT JOIN slice s ON s.track_id = tt.id
  GROUP BY tb.utid
), thread_state_by_thread AS (
  SELECT
    tb.utid,
    COUNT(ts.ts) AS thread_state_count
  FROM thread_base tb
  LEFT JOIN thread_state ts ON ts.utid = tb.utid
  GROUP BY tb.utid
), per_thread AS (
  SELECT
    tb.*,
    COALESCE(sbt.slice_count, 0) AS slice_count,
    COALESCE(tsbt.thread_state_count, 0) AS thread_state_count
  FROM thread_base tb
  LEFT JOIN slice_by_thread sbt ON tb.utid = sbt.utid
  LEFT JOIN thread_state_by_thread tsbt ON tb.utid = tsbt.utid
), thread_rank AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY upid ORDER BY slice_count DESC, thread_state_count DESC) AS rn
  FROM per_thread
)
SELECT
  process_name,
  pid,
  upid,
  start_ts,
  end_ts,
  COUNT(DISTINCT utid) AS thread_count,
  COUNT(DISTINCT CASE WHEN slice_count > 0 THEN utid END) AS thread_track_count,
  SUM(slice_count) AS slice_count,
  SUM(thread_state_count) AS thread_state_count,
  GROUP_CONCAT(
    DISTINCT CASE
      WHEN is_main_thread = 1 THEN thread_name || '(tid=' || tid || ', utid=' || utid || ')'
    END
  ) AS main_thread,
  GROUP_CONCAT(
    CASE
      WHEN rn <= 8 THEN thread_name || '(tid=' || tid || ', utid=' || utid || ', slices=' || slice_count || ')'
    END
  ) AS top_threads_by_slice_count
FROM thread_rank
GROUP BY process_name, pid, upid, start_ts, end_ts
ORDER BY process_name, pid;
```
