# Kotlin Spatial App Main-Thread Jank SQL Query Set

This document centralizes the Perfetto SQL used by `analysis-kotlin-spatial-app-jank.md`. Before execution, replace placeholders with real values: `<target.package.name>`, `$FRAME_THREAD_UTID`, `$WINDOW_START_NS`, `$WINDOW_END_NS`, `$FRAME_BUDGET_NS`, `<doframe_start_ns>`, `<doframe_end_ns>`.

Execution contract: run these SQL snippets through `pico-cli perf trace query --session <sessionId> --sql "..."` after `pico-cli perf trace load`. If the daemon/session is gone, restart the daemon and reload the trace; do not invoke `trace_processor_shell` directly during normal analysis.

Unified parameter convention: for new queries, prefer placeholders named like `$FRAME_THREAD_UTID`, `$WINDOW_START_NS`, `$WINDOW_END_NS`, `$FRAME_BUDGET_NS`. Among them, `$FRAME_THREAD_UTID` must be read from `trace-probe-detail.yaml` at `identities.app_frame_driving_threads.candidates[0].utid`. Hardcoding the thread name `main` is forbidden. query-01 ~ query-10a must all pin down the frame-driving thread by `$FRAME_THREAD_UTID`, to avoid misjudgment caused by `t.name = 'main'`.

Before adapting or interpreting these queries, follow [Perfetto Trace Basics](../common/perfetto-trace-basics.md). In particular, all `ts` and `dur` values are Perfetto trace-processor nanoseconds in the loaded session. Do not invent, round, normalize, or manually "align" a window such as `s.ts BETWEEN 1250000000 AND 1260000000` unless those exact bounds came from a prior verified trace row in the same session. After locating an abnormal `doFrame`, carry its exact `s.ts` and `s.ts + s.dur` into drill-down queries, or prefer a CTE that selects the anchor row and joins dependent queries in the same SQL. If a time-window query unexpectedly returns no rows, first validate `trace_bounds`, `MIN/MAX(ts)` for the exact table/thread/filter, and the anchor row identity through `pico-cli perf trace query`; do not switch to `trace_processor_shell`.

## query-01-overbudget-doframe.sql: Query Over-Budget doFrame

Purpose: locate all over-budget `Choreographer#doFrame` slices on the frame-driving thread of the target process. The budget threshold is defined by `$FRAME_BUDGET_NS`. For 90Hz scenarios it is usually `11111111`; for 60Hz scenarios it can be `16666667`.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND t.utid = $FRAME_THREAD_UTID
  AND s.name GLOB '*Choreographer#doFrame*'
  AND s.dur > $FRAME_BUDGET_NS
  AND s.ts < $WINDOW_END_NS
  AND s.ts + s.dur > $WINDOW_START_NS
ORDER BY s.dur DESC
LIMIT 100;
```

## query-02-doframe-thread-state-bucket.sql: Summarize Thread-State Ratio Within doFrame

Purpose: split a single over-budget `doFrame` into ratios of running, sleeping, uninterruptible, runnable, etc., to decide the first drill-down direction.

```sql
WITH frame_thread AS (
  SELECT t.utid
  FROM thread t
  JOIN process p ON t.upid = p.upid
  WHERE p.name = '<target.package.name>'
    AND t.utid = $FRAME_THREAD_UTID
), states AS (
  SELECT
    ts.state,
    ts.io_wait,
    ts.blocked_function,
    MAX(ts.ts, <doframe_start_ns>) AS overlap_start_ns,
    MIN(ts.ts + ts.dur, <doframe_end_ns>) AS overlap_end_ns
  FROM thread_state ts
  JOIN frame_thread ft ON ts.utid = ft.utid
  WHERE ts.ts < <doframe_end_ns>
    AND ts.ts + ts.dur > <doframe_start_ns>
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
    overlap_start_ns,
    overlap_end_ns,
    overlap_end_ns - overlap_start_ns AS overlap_dur
  FROM states
  WHERE overlap_end_ns > overlap_start_ns
)
SELECT
  state_bucket,
  ROUND(SUM(overlap_dur) / 1000000.0, 3) AS overlap_ms,
  ROUND(100.0 * SUM(overlap_dur) / (<doframe_end_ns> - <doframe_start_ns>), 1) AS pct_of_doframe,
  GROUP_CONCAT(DISTINCT state) AS raw_states,
  GROUP_CONCAT(DISTINCT blocked_function) AS blocked_functions
FROM bucketed
GROUP BY state_bucket
ORDER BY overlap_ms DESC;
```

## query-03-doframe-leaf-slices.sql: Query Leaf Slices Within doFrame

Purpose: when running ratio is highest, find the deepest time-consuming points within `doFrame` to avoid looking only at parent slice names.

```sql
WITH main_slices AS (
  SELECT
    s.id,
    s.parent_id,
    s.name,
    s.ts,
    s.dur,
    s.depth
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = '<target.package.name>'
    AND t.utid = $FRAME_THREAD_UTID
    AND s.ts >= <doframe_start_ns>
    AND s.ts + s.dur <= <doframe_end_ns>
), leaf_slices AS (
  SELECT ms.*
  FROM main_slices ms
  WHERE NOT EXISTS (
    SELECT 1
    FROM main_slices child
    WHERE child.parent_id = ms.id
  )
)
SELECT
  name AS leaf_slice_name,
  ts,
  dur,
  depth,
  ROUND(dur / 1000000.0, 3) AS dur_ms
FROM leaf_slices
ORDER BY dur DESC
LIMIT 50;
```

## query-04-doframe-sleeping-d-state.sql: Query S / D State Segments Within doFrame

Purpose: when sleeping or uninterruptible ratio is highest, confirm the frame-driving thread’s waiting segments, `io_wait`, and `blocked_function`.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  ts.ts,
  ts.dur,
  ROUND(ts.dur / 1000000.0, 3) AS dur_ms,
  ts.state,
  ts.io_wait,
  ts.blocked_function
FROM thread_state ts
JOIN thread t ON ts.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND t.utid = $FRAME_THREAD_UTID
  AND ts.ts < <doframe_end_ns>
  AND ts.ts + ts.dur > <doframe_start_ns>
  AND ts.state IN ('S', 'D')
ORDER BY ts.dur DESC
LIMIT 50;
```

## query-05-doframe-runnable-state.sql: Query Runnable Segments Within doFrame

Purpose: when runnable ratio is highest, confirm the time ranges where the frame-driving thread is runnable but does not get CPU.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  ts.ts,
  ts.dur,
  ROUND(ts.dur / 1000000.0, 3) AS dur_ms,
  ts.state,
  ts.io_wait,
  ts.blocked_function
FROM thread_state ts
JOIN thread t ON ts.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND t.utid = $FRAME_THREAD_UTID
  AND ts.ts < <doframe_end_ns>
  AND ts.ts + ts.dur > <doframe_start_ns>
  AND ts.state = 'R'
ORDER BY ts.dur DESC
LIMIT 50;
```

## query-06-doframe-binder-slices.sql: Query Binder / transact Slices Within doFrame

Purpose: confirm whether the frame-driving thread’s waiting comes from Binder or system service calls.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND t.utid = $FRAME_THREAD_UTID
  AND s.ts < <doframe_end_ns>
  AND s.ts + s.dur > <doframe_start_ns>
  AND (
    s.name GLOB '*binder*'
    OR s.name GLOB '*Binder*'
    OR s.name GLOB '*transact*'
    OR s.name GLOB '*Transaction*'
  )
ORDER BY s.dur DESC
LIMIT 50;
```

## query-07-doframe-lock-wait-slices.sql: Query Lock-Wait / park / futex Slices Within doFrame

Purpose: confirm whether the frame-driving thread’s waiting comes from lock contention, park, futex, or condition variables.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND t.utid = $FRAME_THREAD_UTID
  AND s.ts < <doframe_end_ns>
  AND s.ts + s.dur > <doframe_start_ns>
  AND (
    s.name GLOB '*monitor contention*'
    OR s.name GLOB '*Object.wait*'
    OR s.name GLOB '*LockSupport.park*'
    OR s.name GLOB '*futex*'
    OR s.name GLOB '*Mutex*'
    OR s.name GLOB '*ConditionVariable*'
  )
ORDER BY s.dur DESC
LIMIT 50;
```

## query-08-gc-overlap-doframe.sql: Query Overlap Between GC and Main-Thread doFrame

Purpose: determine whether `SuspendAll`, Stop-the-world, or GC pauses cover key time within an over-budget `doFrame`.

```sql
WITH main_slices AS (
  SELECT
    s.id,
    s.ts,
    s.ts + s.dur AS ts_end,
    s.name,
    s.dur
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = '<target.package.name>'
    AND t.utid = $FRAME_THREAD_UTID
    AND s.name GLOB '*Choreographer#doFrame*'
    AND s.ts < $WINDOW_END_NS
    AND s.ts + s.dur > $WINDOW_START_NS
), gc_slices AS (
  SELECT
    s.ts,
    s.ts + s.dur AS ts_end,
    s.name,
    s.dur
  FROM slice s
  WHERE s.ts < $WINDOW_END_NS
    AND s.ts + s.dur > $WINDOW_START_NS
    AND (
      s.name GLOB '*GC*'
      OR s.name GLOB '*Garbage*'
      OR s.name GLOB '*SuspendAll*'
      OR s.name GLOB '*Stop-the-world*'
    )
)
SELECT
  m.name AS main_slice,
  ROUND(m.dur / 1000000.0, 3) AS main_dur_ms,
  g.name AS gc_slice,
  ROUND(g.dur / 1000000.0, 3) AS gc_dur_ms,
  MAX(m.ts, g.ts) AS overlap_start_ns,
  MIN(m.ts_end, g.ts_end) AS overlap_end_ns,
  ROUND((MIN(m.ts_end, g.ts_end) - MAX(m.ts, g.ts)) / 1000000.0, 3) AS overlap_ms
FROM main_slices m
JOIN gc_slices g
  ON m.ts < g.ts_end AND m.ts_end > g.ts
ORDER BY overlap_ms DESC
LIMIT 50;
```

## query-09-doframe-input-slices.sql: Query Input / ViewRootImpl Slices Within doFrame

Purpose: when symptoms involve input latency or ANR, align input-event processing, `doFrame`, and frame-driving thread state.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND t.utid = $FRAME_THREAD_UTID
  AND s.ts < <doframe_end_ns>
  AND s.ts + s.dur > <doframe_start_ns>
  AND (
    s.name GLOB '*deliverInputEvent*'
    OR s.name GLOB '*ViewRootImpl*'
    OR s.name GLOB '*InputEventReceiver*'
    OR s.name GLOB '*Input*'
  )
ORDER BY s.dur DESC
LIMIT 50;
```


## query-10-frame-thread-overbudget-doframe.sql: Find Over-Budget Janky Frames by Frame-Driving Thread

Purpose: use the frame-driving thread `utid` pinned down in `trace-probe-detail.yaml` to find over-budget `Choreographer#doFrame`. This query replaces coarse filtering by thread name `main` to avoid missing cases where the frame-driving thread is not consistently named `main` in Spatial Apps. In 90Hz scenarios, `$FRAME_BUDGET_NS` is usually `11111111`; in 60Hz scenarios it can be `16666667`.

Parameter sources:

- `$TARGET_APP_PACKAGE_NAME`: the package name of target app, read from `trace-probe-detail.yaml` at `identities.target_app.candidates.requested_names`.
- `$FRAME_THREAD_UTID`: read from `trace-probe-detail.yaml` at `identities.app_frame_driving_threads.candidates[0].utid`.

```sql
-- Find over-budget doFrame on the frame-driving thread within the issue window.
-- Note: the frame-driving thread utid must come from trace-probe-detail.yaml; hardcoding thread name main is forbidden.
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = $TARGET_APP_PACKAGE_NAME
  AND t.utid = $FRAME_THREAD_UTID
  AND s.name GLOB '*Choreographer#doFrame*'
  AND s.dur > $FRAME_BUDGET_NS
ORDER BY s.dur DESC
LIMIT 100;
```

### query-10a-worst-doframe-anchor.sql: Pick the Worst Frame as the Anchor

Purpose: from the results of `query-10`, directly pick the longest over-budget `doFrame` as the anchor for subsequent drill-down queries. The output `doframe_start_ns` and `doframe_end_ns` can be substituted into `<doframe_start_ns>` and `<doframe_end_ns>` in `query-02` ~ `query-09`.

When possible, keep this anchor in the same SQL statement as the drill-down query instead of copying timestamps by hand. This avoids drift from rounded, truncated, or cross-session timestamps.

```sql
-- Pick the worst over-budget doFrame in the issue window as the anchor for subsequent analysis.
-- doframe_start_ns / doframe_end_ns are used for drill-down queries on thread state, leaf slices, Binder, lock waits, GC, etc.
SELECT
  s.ts AS doframe_start_ns,
  s.ts + s.dur AS doframe_end_ns,
  s.dur AS doframe_dur_ns,
  ROUND(s.dur / 1000000.0, 3) AS doframe_dur_ms,
  t.utid AS thread_utid,
  t.name AS thread_name
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
WHERE t.utid = $FRAME_THREAD_UTID
  AND s.name GLOB '*Choreographer#doFrame*'
  AND s.dur > $FRAME_BUDGET_NS
  AND s.ts < $WINDOW_END_NS
  AND s.ts + s.dur > $WINDOW_START_NS
ORDER BY s.dur DESC
LIMIT 1;
```

### query-10b-anchor-thread-state-drilldown.sql: Derive the doFrame Window In-Query

Purpose: demonstrate the preferred pattern for follow-up queries. The abnormal frame is selected as an anchor CTE, and thread-state overlap uses the exact `doframe_start_ns` / `doframe_end_ns` derived from that row. Use the same pattern for leaf slices, Binder waits, lock waits, GC overlap, and input alignment.

```sql
WITH anchor AS (
  SELECT
    s.id AS doframe_slice_id,
    s.ts AS doframe_start_ns,
    s.ts + s.dur AS doframe_end_ns,
    s.dur AS doframe_dur_ns
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  WHERE tt.utid = $FRAME_THREAD_UTID
    AND s.name GLOB '*Choreographer#doFrame*'
    AND s.dur > $FRAME_BUDGET_NS
  ORDER BY s.dur DESC
  LIMIT 1
), states AS (
  SELECT
    ts.state,
    ts.io_wait,
    ts.blocked_function,
    MAX(ts.ts, anchor.doframe_start_ns) AS overlap_start_ns,
    MIN(ts.ts + ts.dur, anchor.doframe_end_ns) AS overlap_end_ns,
    anchor.doframe_dur_ns
  FROM thread_state ts
  JOIN anchor
  WHERE ts.utid = $FRAME_THREAD_UTID
    AND ts.ts < anchor.doframe_end_ns
    AND ts.ts + ts.dur > anchor.doframe_start_ns
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
    overlap_end_ns - overlap_start_ns AS overlap_dur,
    doframe_dur_ns
  FROM states
  WHERE overlap_end_ns > overlap_start_ns
)
SELECT
  state_bucket,
  ROUND(SUM(overlap_dur) / 1000000.0, 3) AS overlap_ms,
  ROUND(100.0 * SUM(overlap_dur) / MAX(doframe_dur_ns), 1) AS pct_of_doframe,
  GROUP_CONCAT(DISTINCT state) AS raw_states,
  GROUP_CONCAT(DISTINCT blocked_function) AS blocked_functions
FROM bucketed
GROUP BY state_bucket
ORDER BY overlap_ms DESC;
```
