# Binder System Service Resolution SQL Query Set

This document supplements the execution details for "precisely locating the system service corresponding to a Binder call" in `analysis-binder.md`. The goal is not merely to prove that Binder activity exists, but to locate a Binder wait on the critical path as precisely as possible to:

1. Caller thread
2. transaction name / code clues
3. Callee process / binder thread
4. The corresponding system service or service class
5. Server-side slowness factors (slow function / lock / GC / scheduling / downstream Binder)

Before execution, replace placeholders: `<target.package.name>`, `<window_start_ns>`, `<window_end_ns>`, `<caller_thread_name>`, `<binder_ts_ns>`, `<binder_end_ns>`.

Execution contract: run these SQL snippets through `pico-cli perf trace query --session <sessionId> --sql "..."` after `pico-cli perf trace load`. If the daemon/session is gone, restart the daemon and reload the trace; do not invoke `trace_processor_shell` directly during normal analysis.

---

## query-01-caller-binder-slices.sql: Binder Slices Within a Caller-Side Key Thread

Purpose: first confirm which Binder slices exist in the issue window on the caller-side key thread (main thread / frame-driving thread / Spatial key thread), and which ones are the longest.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms,
  s.depth
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND t.name = '<caller_thread_name>'
  AND s.ts < <window_end_ns>
  AND s.ts + s.dur > <window_start_ns>
  AND (
    s.name GLOB '*binder*'
    OR s.name GLOB '*Binder*'
    OR s.name GLOB '*transact*'
    OR s.name GLOB '*Transaction*'
  )
ORDER BY s.dur DESC
LIMIT 100;
```

---

## query-02-caller-transaction-clues.sql: Extract transaction Naming Clues

Purpose: extract more readable AIDL/interface-name clues from Binder-related slices in the entire caller process, and prioritize checking whether there are method names that can be directly mapped to system services.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  COUNT(*) AS cnt,
  ROUND(MAX(s.dur) / 1000000.0, 3) AS max_ms,
  ROUND(SUM(s.dur) / 1000000.0, 3) AS total_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND s.ts < <window_end_ns>
  AND s.ts + s.dur > <window_start_ns>
  AND (
    s.name GLOB 'AIDL::*'
    OR s.name GLOB '*I*Service*'
    OR s.name GLOB '*scheduleTransaction*'
    OR s.name GLOB '*Window*'
    OR s.name GLOB '*Audio*'
    OR s.name GLOB '*Input*'
    OR s.name GLOB '*Power*'
  )
GROUP BY p.name, t.name, s.name
ORDER BY total_ms DESC, max_ms DESC
LIMIT 100;
```

---

## query-03-system-server-binder-reply-hotspots.sql: system_server binder reply Hotspots

Purpose: within the same window, find which binder threads in `system_server` are the busiest and slowest to reply, to lock down candidate server-side threads.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  COUNT(*) AS cnt,
  ROUND(SUM(s.dur) / 1000000.0, 3) AS total_ms,
  ROUND(MAX(s.dur) / 1000000.0, 3) AS max_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = 'system_server'
  AND s.ts < <window_end_ns>
  AND s.ts + s.dur > <window_start_ns>
  AND (
    s.name = 'binder reply'
    OR s.name = 'binder transaction'
  )
GROUP BY p.name, t.name, s.name
ORDER BY total_ms DESC, max_ms DESC
LIMIT 100;
```

---

## query-04-system-server-service-slices-near-binder.sql: Server-Side Business Slices Near Binder Hotspots

Purpose: when you only know that a binder reply is slow, search for service class/module slices near it to infer the system service from business slices.

Note: replace `<binder_ts_ns>` and `<binder_end_ns>` with the start/end timestamps of a slow `binder reply` or slow `binder transaction`.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms,
  s.depth
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = 'system_server'
  AND s.ts < <binder_end_ns>
  AND s.ts + s.dur > <binder_ts_ns>
  AND s.name NOT IN ('binder reply', 'binder transaction')
ORDER BY s.dur DESC, s.ts ASC
LIMIT 200;
```

Interpretation highlights:

- If `AudioService` / `PlaybackActivityMonitor` is hit: prioritize attributing it to audio services.
- If `InputManagerService` / `InputDispatcher` is hit: prioritize attributing it to input services.
- If `WindowManagerService` / `WindowState` / `IWindowSession` is hit: prioritize attributing it to window services.
- If `PowerManagerService` / `WakeLock` is hit: prioritize attributing it to power management.
- If `ActivityTaskManagerService` / `scheduleTransaction` is hit: prioritize attributing it to lifecycle / ATMS.

---

## query-05-system-server-lock-contention-near-binder.sql: Server-Side Lock Contention

Purpose: determine whether a slow server reply is slowed down by lock contention rather than the service itself running the whole time.

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
WHERE p.name = 'system_server'
  AND s.ts < <binder_end_ns>
  AND s.ts + s.dur > <binder_ts_ns>
  AND (
    s.name GLOB '*monitor contention*'
    OR s.name GLOB '*Object.wait*'
    OR s.name GLOB '*LockSupport.park*'
    OR s.name GLOB '*futex*'
    OR s.name GLOB '*Mutex*'
  )
ORDER BY s.dur DESC
LIMIT 100;
```

---

## query-06-system-server-gc-near-binder.sql: Server-Side GC Overlapping Binder

Purpose: confirm whether slow replies are amplified by GC / `ThreadFlipSuspendAll`.

```sql
SELECT
  p.name AS process_name,
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms
FROM slice s
LEFT JOIN thread_track tt ON s.track_id = tt.id
LEFT JOIN thread t ON tt.utid = t.utid
LEFT JOIN process p ON t.upid = p.upid
WHERE p.name = 'system_server'
  AND s.ts < <binder_end_ns>
  AND s.ts + s.dur > <binder_ts_ns>
  AND (
    s.name GLOB '*GC*'
    OR s.name GLOB '*Garbage*'
    OR s.name GLOB '*SuspendAll*'
    OR s.name GLOB '*Stop-the-world*'
    OR s.name GLOB '*concurrent mark compact*'
  )
ORDER BY s.dur DESC
LIMIT 100;
```

---

## query-07-service-keyword-summary.sql: Service Keyword Attribution Summary

Purpose: when you need to quickly provide the "most suspicious service candidates", aggregate business slices in the same window by service keywords to form high-confidence candidates.

```sql
WITH service_slices AS (
  SELECT
    s.name,
    s.dur,
    CASE
      WHEN s.name GLOB '*AudioService*' OR s.name GLOB '*PlaybackActivityMonitor*' OR s.name GLOB '*AudioTrack*' THEN 'audio'
      WHEN s.name GLOB '*InputManager*' OR s.name GLOB '*InputDispatcher*' OR s.name GLOB '*deliverInput*' THEN 'input'
      WHEN s.name GLOB '*WindowManager*' OR s.name GLOB '*WindowState*' OR s.name GLOB '*IWindowSession*' THEN 'window'
      WHEN s.name GLOB '*PowerManagerService*' OR s.name GLOB '*WakeLock*' THEN 'power'
      WHEN s.name GLOB '*ActivityTaskManager*' OR s.name GLOB '*scheduleTransaction*' OR s.name GLOB '*clientTransactionExecuted*' THEN 'activity_lifecycle'
      WHEN s.name GLOB '*PackageManager*' OR s.name GLOB '*ResourcesManager*' OR s.name GLOB '*AssetManager*' THEN 'package_or_resource'
      ELSE 'other'
    END AS service_group
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = 'system_server'
    AND s.ts < <window_end_ns>
    AND s.ts + s.dur > <window_start_ns>
)
SELECT
  service_group,
  COUNT(*) AS cnt,
  ROUND(SUM(dur) / 1000000.0, 3) AS total_ms,
  ROUND(MAX(dur) / 1000000.0, 3) AS max_ms
FROM service_slices
WHERE service_group != 'other'
GROUP BY service_group
ORDER BY total_ms DESC, max_ms DESC;
```

---

## Recommended Analysis Order

1. Run `query-01` first to confirm that the caller-side key thread is indeed stuck on Binder.
2. Run `query-02` to see whether there are direct interface/transaction clues.
3. Run `query-03` to lock down the slowest binder reply threads in `system_server`.
4. Pick the time ranges of the slowest one or two binder replies, then run `query-04`, `query-05`, and `query-06`.
5. If you still cannot get an exact service name, run `query-07` to produce high-confidence service candidates.

## Output Recommendations

In the final output, it is recommended to additionally include:

- `caller`: caller process/thread
- `transaction_name_or_code`: explicit method name, AIDL name, or `Unknown_Transaction_Code:x`
- `callee_process`: usually `system_server`
- `service_name_or_guess`: `AudioService` / `InputManagerService` / `WindowManagerService`, etc.
- `service_confidence`: `exact` / `high-confidence` / `candidate-only`
- `service_side_evidence`: summary of server-side business slices, lock contention, GC, scheduling, etc.
- `downstream_dependency`: whether you still need to continue tracing downstream server-side Binder/locks/scheduling
