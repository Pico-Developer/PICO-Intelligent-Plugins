# Report Generation SQL Query Library

> Note: This file collects commonly used Perfetto Trace Processor (SQL) queries for "report generation/chart rendering".
>
> - Applicable to: PICO OS6 performance analysis (the trace has been imported into Perfetto / trace_processor can execute SQL).
> - Convention: `${xxx}` in SQL represents parameters (injected by the report-generation script/manual replacement).
> - Reminder: Differences in trace versions/capture methods may cause slight differences in slice/track naming. If no data is returned, prioritize using `select * from slice limit 50;` and `select * from track limit 50;` to confirm naming before fine-tuning the WHERE filters.
> - Execution contract: run manual SQL through `pico-cli perf trace query --session <sessionId> --sql "..."` after `pico-cli perf trace load`. If the daemon/session is gone, restart the daemon and reload the trace; do not invoke `trace_processor_shell` directly during normal analysis.

---

## 1. App Process Over-Budget Frame Bucket Distribution

### Purpose / Corresponding Report Module
- **Module**: `App over-budget frame bucket distribution` (bar chart/pie chart both acceptable)
- **Goal**: In the App main thread’s `Choreographer#doFrame`, count the duration distribution of frames that **exceed the frame budget** (`dur > budget_ns`).

### Parameters
- `${app_package}`: package name (usually equals the process name, e.g. `com.xxx.yyy`)
- `${budget_ns}`: frame budget (ns)
  - 90fps default: `11111111`

### Returned Fields
- `bucket`: over-budget ratio bucket (relative to `budget_ns`)
- `cnt`: number of over-budget frames in the bucket
- `avg_dur_ms / p50_dur_ms / p90_dur_ms / p99_dur_ms`: duration statistics in the bucket (ms)

### SQL
```sql
-- App main thread: Choreographer#doFrame over-budget frame bucket distribution
-- Depends on: slice / thread_track / thread / process

WITH doframe AS (
  SELECT
    s.ts,
    s.dur,
    p.name AS process_name,
    t.name AS thread_name
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = ${app_package}
    AND t.is_main_thread = 1
    AND s.name = 'Choreographer#doFrame'
    AND s.dur IS NOT NULL
),
slow AS (
  SELECT
    ts,
    dur,
    CAST(dur AS DOUBLE) / CAST(${budget_ns} AS DOUBLE) AS over_ratio
  FROM doframe
  WHERE dur > ${budget_ns}
),
classified AS (
  SELECT
    ts,
    dur,
    over_ratio,
    CASE
      WHEN over_ratio <= 1.25 THEN '(1.00, 1.25]x'
      WHEN over_ratio <= 1.50 THEN '(1.25, 1.50]x'
      WHEN over_ratio <= 2.00 THEN '(1.50, 2.00]x'
      WHEN over_ratio <= 3.00 THEN '(2.00, 3.00]x'
      WHEN over_ratio <= 4.00 THEN '(3.00, 4.00]x'
      ELSE '(4.00, +∞)x'
    END AS bucket
  FROM slow
)
SELECT
  bucket,
  COUNT(*) AS cnt,
  ROUND(AVG(dur) / 1e6, 3) AS avg_dur_ms,
  ROUND(quantile(dur, 0.50) / 1e6, 3) AS p50_dur_ms,
  ROUND(quantile(dur, 0.90) / 1e6, 3) AS p90_dur_ms,
  ROUND(quantile(dur, 0.99) / 1e6, 3) AS p99_dur_ms
FROM classified
GROUP BY bucket
ORDER BY
  CASE bucket
    WHEN '(1.00, 1.25]x' THEN 1
    WHEN '(1.25, 1.50]x' THEN 2
    WHEN '(1.50, 2.00]x' THEN 3
    WHEN '(2.00, 3.00]x' THEN 4
    WHEN '(3.00, 4.00]x' THEN 5
    ELSE 6
  END;
```

---

## 2. SPR (Spatial Runtime) Frame Duration Bucket Distribution

### Purpose / Corresponding Report Module
- **Module**: `SPR frame duration bucket distribution`
- **Goal**: **Directly extract the dur of SPR frame slices** from the trace as the frame duration, and count by buckets.

### Notes (Adjusted Based on Trace Verification)
- This does **not** query an independent track named `SpatialFrames`.
- **Correct definition**: query **top-level** `SpatialRFrame` slices on the `Eng-Render` thread under the `com.pico.spatial.runtime` process.
  - track (thread) name: `Eng-Render`
  - slice name pattern: `SpatialRFrame %`
  - only take top-level frames with `depth = 0` to avoid double-counting child slices
- **Verified in practice**: 2674 frames, range 1.45ms ~ 7.17ms, all normal.

### Parameters
- None

### Returned Fields
- `bucket_ms`: frame duration bucket (ms)
- `cnt`: number of frames in the bucket
- `avg_dur_ms / p50_dur_ms / p90_dur_ms / p99_dur_ms`: duration statistics in the bucket (ms)

### SQL
```sql
-- SPR: Eng-Render thread top-level SpatialRFrame frame duration bucket distribution
-- Depends on: slice / thread_track / thread / process

WITH frames AS (
  SELECT
    s.ts,
    s.dur
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = 'com.pico.spatial.runtime'
    AND t.name = 'Eng-Render'
    AND s.name LIKE 'SpatialRFrame %'
    AND s.depth = 0
    AND s.dur IS NOT NULL
),
classified AS (
  SELECT
    ts,
    dur,
    (dur / 1e6) AS dur_ms,
    CASE
      WHEN (dur / 1e6) <= 8.0  THEN '(0, 8]'
      WHEN (dur / 1e6) <= 11.111 THEN '(8, 11.11]'
      WHEN (dur / 1e6) <= 16.667 THEN '(11.11, 16.67]'
      WHEN (dur / 1e6) <= 22.222 THEN '(16.67, 22.22]'
      WHEN (dur / 1e6) <= 33.333 THEN '(22.22, 33.33]'
      ELSE '(33.33, +∞)'
    END AS bucket_ms
  FROM frames
)
SELECT
  bucket_ms,
  COUNT(*) AS cnt,
  ROUND(AVG(dur_ms), 3) AS avg_dur_ms,
  ROUND(quantile(dur_ms, 0.50), 3) AS p50_dur_ms,
  ROUND(quantile(dur_ms, 0.90), 3) AS p90_dur_ms,
  ROUND(quantile(dur_ms, 0.99), 3) AS p99_dur_ms
FROM classified
GROUP BY bucket_ms
ORDER BY
  CASE bucket_ms
    WHEN '(0, 8]' THEN 1
    WHEN '(8, 11.11]' THEN 2
    WHEN '(11.11, 16.67]' THEN 3
    WHEN '(16.67, 22.22]' THEN 4
    WHEN '(22.22, 33.33]' THEN 5
    ELSE 6
  END;
```

---

## 3. FPS Trend (Per-Second, App + SPR)

### Purpose / Corresponding Report Module
- **Module**: `FPS trend (per-second)` (two lines: App FPS + SPR FPS)

### Note (No SQL)
- **Data source**: `rawData` in `fast-perf.json`.
- This trend chart does not depend on trace SQL; it can be parsed directly from `fast-perf.json` by the capture/report side.

### Parameters
- None (the report side reads by the `fast-perf.json` file path)

### Returned Fields (Recommended)
- `sec`: seconds relative to the start time
- `app_fps`: App FPS (per-second)
- `spr_fps`: SPR FPS (per-second)

---

## 4. CPU/GPU Trend

### Purpose / Corresponding Report Module
- **Module**: `CPU/GPU trend (per-second)` (lines: CPU, GPU, etc.)

### Note (No SQL)
- **Data source**: `rawData` in `fast-perf.json`.
- Does not depend on trace SQL; the report side parses and plots from `fast-perf.json`.

### Parameters
- None (the report side reads by the `fast-perf.json` file path)

### Returned Fields (Recommended)
- `sec`: seconds relative to the start time
- `cpu_util`: CPU utilization (or split by big/little cores)
- `gpu_util`: GPU utilization
- `cpu_freq`: CPU frequency (optional)
- `gpu_freq`: GPU frequency (optional)

---

## 5. Key Janky Frame Details (Top N Over-Budget Frames)

### Purpose / Corresponding Report Module
- **Module**: `Top N over-budget frame details table`
- **Goal**: Find the longest N over-budget `Choreographer#doFrame` instances to expand "key frames" for analysis in the report.

### Parameters
- `${app_package}`: package name
- `${budget_ns}`: frame budget (ns)
- `${top_n}`: Top N (default 20)

### Returned Fields
- `frame_seq`: frame index (sequence number by time ordering, convenient for referencing)
- `ts`: frame start time (ns, trace timeline)
- `dur_ms`: frame duration (ms)
- `over_ratio`: over-budget ratio (dur / budget)

### SQL
```sql
-- Top N over-budget doFrame (the longest N frames)

WITH doframe AS (
  SELECT
    s.ts,
    s.dur
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = ${app_package}
    AND t.is_main_thread = 1
    AND s.name = 'Choreographer#doFrame'
    AND s.dur IS NOT NULL
),
slow AS (
  SELECT
    ts,
    dur,
    CAST(dur AS DOUBLE) / CAST(${budget_ns} AS DOUBLE) AS over_ratio
  FROM doframe
  WHERE dur > ${budget_ns}
),
seq AS (
  SELECT
    ROW_NUMBER() OVER (ORDER BY ts) AS frame_seq,
    ts,
    dur,
    over_ratio
  FROM slow
)
SELECT
  frame_seq,
  ts,
  ROUND(dur / 1e6, 3) AS dur_ms,
  ROUND(over_ratio, 3) AS over_ratio
FROM seq
ORDER BY dur DESC
LIMIT COALESCE(${top_n}, 20);
```

---

## 6. App Main-Thread Binder Call Statistics

### Purpose / Corresponding Report Module
- **Module**: `Binder call statistics within janky frame windows` (table: aggregate by target service/interface)
- **Goal**: Count Binder calls initiated by the App main thread within the "janky frame windows". Group by target service (or call name) and output count and average latency.

### Parameters
- `${app_package}`: package name
- `${budget_ns}`: frame budget (ns)

### Returned Fields
- `binder_name`: Binder slice name (used as an approximate proxy for the target service/interface; optionally apply a second-stage regex extraction)
- `cnt`: call count
- `avg_dur_ms`: average latency (ms)
- `p90_dur_ms`: P90 latency (ms)

### SQL
```sql
-- Note: Binder slice naming may differ across traces.
-- Here we approximate by using slices "on the App main thread" whose names contain the binder keyword.
-- If Binder events in your trace fall on other tracks (e.g., binder_driver / binder transaction, etc.),
-- first explore in the slice table with name like '%binder%', then adjust the WHERE filters.

WITH jank_frames AS (
  -- Janky frame windows: [ts, ts+dur) for over-budget doFrame
  SELECT
    s.ts AS frame_ts,
    s.ts + s.dur AS frame_ts_end
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = ${app_package}
    AND t.is_main_thread = 1
    AND s.name = 'Choreographer#doFrame'
    AND s.dur IS NOT NULL
    AND s.dur > ${budget_ns}
),
binder_calls AS (
  SELECT
    s.ts,
    s.dur,
    s.name AS binder_name
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = ${app_package}
    AND t.is_main_thread = 1
    AND s.dur IS NOT NULL
    AND (LOWER(s.name) LIKE '%binder%')
),
matched AS (
  SELECT
    b.binder_name,
    b.dur
  FROM binder_calls b
  JOIN jank_frames f
    ON b.ts >= f.frame_ts
   AND b.ts <  f.frame_ts_end
)
SELECT
  binder_name,
  COUNT(*) AS cnt,
  ROUND(AVG(dur) / 1e6, 3) AS avg_dur_ms,
  ROUND(quantile(dur, 0.90) / 1e6, 3) AS p90_dur_ms
FROM matched
GROUP BY binder_name
ORDER BY cnt DESC, avg_dur_ms DESC;
```

---

## 7. Process Counter Trend

### Purpose / Corresponding Report Module
- **Module**: `Render load counter trend`
- **Goal**: Query all events for one process-scoped counter, such as Spatial Runtime `3D Mesh Draw Call Count`, and return a time series suitable for report chart rendering.
- **Report integration**: `query_report_data.py` exposes this as `query_process_counter_series(client, process_name, counter_name)`. The report's multi-counter render-load section is driven by `../render-load-counters.json`; each configured counter calls this same parameterized SQL and is rendered under Data Overview -> Render Load (`渲染负载`) sub-tabs.

### Parameters
- `${process_name}`: process name, e.g. `'com.pico.spatial.runtime'`
- `${counter_name}`: counter track name, e.g. `'3D Mesh Draw Call Count'`

### Returned Fields
- `ts_ns`: counter event timestamp as text, preserving Perfetto ns precision through JSON consumers
- `ts_ms`: counter event timestamp in milliseconds
- `time_s`: seconds relative to the first sample of this counter
- `value`: counter value

### SQL
```sql
-- Process counter trend, parameterized by process and counter name.
-- Depends on: process / process_counter_track / counter_track / counter

WITH target_process AS (
  SELECT
    p.upid,
    p.pid,
    p.name AS process_name
  FROM process p
  WHERE p.name = ${process_name}
),
target_counter_track AS (
  SELECT
    ct.id AS track_id,
    ct.name AS track_name,
    pct.upid
  FROM counter_track ct
  JOIN process_counter_track pct ON pct.id = ct.id
  JOIN target_process tp ON tp.upid = pct.upid
  WHERE ct.name = ${counter_name}
),
samples AS (
  SELECT
    c.id,
    c.ts,
    c.value
  FROM counter c
  JOIN target_counter_track tct ON tct.track_id = c.track_id
),
bounds AS (
  SELECT MIN(ts) AS first_ts
  FROM samples
)
SELECT
  CAST(s.ts AS TEXT) AS ts_ns,
  ROUND(s.ts / 1000000.0, 3) AS ts_ms,
  ROUND((s.ts - b.first_ts) / 1000000000.0, 3) AS time_s,
  s.value AS value
FROM samples s
JOIN bounds b
ORDER BY s.ts ASC, s.id ASC;
```
