# Kotlin Spatial App Main Thread Jank Analysis Workflow

This document is used to analyze main thread jank, ANR, dropped frames, UI rendering latency, and Input response latency in spatial apps built based on the Kotlin Spatial SDK. Analysis must start from trace evidence, first locating the time window where the user-visible abnormal frame or input latency occurs, and then placing main thread Slices, SpatialFrames, SpatialMetrics, and system-side events on the same timeline for judgment.

## Topic Execution Instructions

This subprotocol is executed only when the Main protocol in [Analysis Topic Routing](../routing/analysis-topic-routing.md) adds it to the execution queue. The Main protocol owns activation. Execute this subprotocol from Applicable Scenarios through the Spatial Trace Probe, over-budget frame localization, main-thread drill-down, closure assessment, and output. Hand back cross-topic evidence to the Main protocol; do not activate or load other subprotocols from this document.

This protocol only retains the analysis process and determination rules. Perfetto SQL is concentrated in [Kotlin Spatial App Main Thread Jank SQL Query Set](../sql-query/sql-kotlin-spatial-app-jank.md). When executing SQL, first replace placeholders such as package name, time window, and `doFrame` start/end times.

## Applicable Scenarios

- Spatial apps built based on the Kotlin Spatial SDK.
- Main thread jank, ANR, dropped frames.
- UI rendering latency, Input response latency.
- Suspicious dependencies exist between Kotlin / Java UI logic, Spatial SDK calls, OpenXR frame loop, or system service calls.

## Entry Signals and First Analysis Step

When any of the following user-visible or evidence signals appears, routing
must add this topic as an entry topic:

- The user reports obvious App jank, UI stutter, delayed input, or an App-side
  responsiveness problem.
- Quick diagnosis shows App dropped frames, AppProduce anomalies, or reports
  explicitly pointing out App main thread related dropped frames.
- The trace shows `Choreographer#doFrame` exceeding 11.11ms (90fps) /
  16.67ms (60fps), or App main thread Slices covering Late / Miss / Discard
  Frame anomaly windows.

The first execution step is to locate and verify the App over-budget frame
window. Do not use the absence of a previously computed `doFrame` result as a
reason to route directly to Binder. Binder, locks, GC, I/O, and scheduling are
causal branches discovered during this topic and returned to Analysis Topic
Routing for dynamic activation.

## Spatial Trace Probe Pre-check

Before entering main thread jank analysis, execute `spatial_probe.py` to confirm that the target App process and frame driving thread are visible in the trace. It has internally split process detection into two independent methods:
- `probe_app_identity()`: Checks target App process + frame driving thread, writing to `identities.target_app` and `identities.app_frame_driving_threads`.
- `probe_spatial_runtime_identity()`: Checks SPR / OpenXR Runtime / compositor, writing to corresponding fields.

The two methods are independent try/except; one failure does not affect the other.

If the target process, frame driving thread, `OpenXRClientSpatialFrames`, or critical Spatial Slices are not visible, do not directly draw a root cause conclusion; first supplement the trace collection or confirm the package name, time window, and trace configuration.

**Frame Driving Thread Localization Convention**: The frame driving thread name of a spatial app is not `main`, but the last segment of the package name (e.g., `xample.galaxian`). **The real `utid` must be read from the `identities.app_frame_driving_threads.candidates[0].utid` in the probe output (`trace-probe-detail.yaml`); hardcoding the thread name `main` is prohibited.**

Example command call:

```bash
python3 scripts/spatial_probe.py --trace <trace.perfetto-trace> --package <target.package.name>
```

`spatial_probe.py` performs its own trace loading through the `pico-cli perf` session flow. Only fall back to manual trace loading or exporting according to the [PICO CLI Perf Usage Guide](../common/tools.md) when troubleshooting probe failures or validating the underlying session behavior directly.

## Analysis Workflow

Main thread jank analysis follows the classic drill-down logic of Android jank analysis: first find the `Choreographer#doFrame` that exceeds the frame budget in the main thread, and then drill down to judge where the time was spent. There are only two core branches: first, the thread is running, but long leaf Slices or slow function calls consumed the budget; second, the thread is not running, being in a state of waiting, uninterruptible wait, or runnable scheduling latency, necessitating further investigation of blocking or scheduling causes.

### Key Differences Between Spatial Apps and Standard Android Jank Analysis

- Spatial apps do not have an independent RenderThread self-rendering thread. GPU submission and rendering instructions are uniformly managed by the Spatial Engine side and do not go through the App-side RenderThread. Therefore, **RenderThread should not be the primary analysis object**.
- The critical thread for frame production on the App side is the **frame driving thread** (the thread name is the last segment of the package name, not necessarily `main`), corresponding to the AppProduce phase: `SpatialApp_beforeFrameCallback` → `System_Update` → `System_SetComponentsChange` → `SpatialApp_afterFrameCallback`.
- Rendering bottlenecks should be analyzed on the Spatial Engine side (`Eng-Render`, GPU time, etc.) in `analysis-spatial-engine.md` and are not within the scope of this protocol.

### 1. Locating Over-budget Frames

In a 90fps scenario, the single-frame budget is 11.11ms. So first locate all over-budget frames(janks) on the target App frame-driving thread. SQL can refer to[query-10-frame-thread-overbudget-doframe](../sql-query/sql-kotlin-spatial-app-jank.md#query-10-frame-thread-overbudget-doframe).

### 2. Drill-down: Why is the frame over budget

- Do not jump directly to a conclusion from a Slice name; you must first answer whether the main thread was running, runnable but not getting CPU, or actively/passively waiting during this time.
- Then get the overlap duration of each state category within the jank frame, so you can know whether the over-budget is caused by Long Running time or Long Not Running time. SQL can refer to [query-02-doframe-thread-state-bucket.sql](../sql-query/sql-kotlin-spatial-app-jank.md#query-02-doframe-thread-state-bucketsql-summarize-thread-state-ratio-within-doframe).

```text
Frame over-budget
├─ Long Running time
│  ├─ Slow functions: Business logic / serialization / layout / Compose / Spatial SDK synchronous calls
│  ├─ GC / JIT: STW, SuspendAll, JIT compilation or class loading overlapping with doFrame
│  └─ Insufficient CPU power: frequency reduction, little cores, CPU time close to wall time but still over budget
└─ Long Not Running time
   ├─ Sleeping: Binder / locks / synchronous wait / IO wait
   ├─ Uninterruptible(D): Disk IO / page fault / kernel uninterruptible wait
   └─ Runnable: Scheduling latency / CPU competition / priority or core binding issues
```

#### 2.1 Long Running Time: Thread is running, but running slowly

- If `running` has the high proportion, query leaf Slices to get closer to real slow functions or slow operations. SQL can refer to [query-03-doframe-leaf-slices.sql](../sql-query/sql-kotlin-spatial-app-jank.md#query-03-doframe-leaf-slicessql-query-leaf-slices-within-doframe).
- Sort by duration, and judge whether the longest few leaf Slices belong to business logic, serialization, layout / Compose, resource loading, image / Shader / Mesh initialization, Spatial SDK calls, ECS / Entity updates, synchronous I/O, or complex calculations.

- When interpreting, do not just look at the largest parent Slice. For example, parent names like `Choreographer#doFrame`, `Traversal` or `Compose:recompose` only indicate the phase and cannot directly explain the root cause. You need to continue looking at leaf Slices or function sampling. If a leaf Slice hits synchronous resource loading, first-time initialization, complex layout, batch object creation, or Spatial SDK synchronous calls, optimization suggestions should be given in combination with the business path. If leaf Slices are very short but `doFrame` still times out, continue checking GC / JIT or turn to the Not Running path.

- When Running time is long but there is no single slow Slice, check if GC / JIT / class loading overlaps with `doFrame`. If there is no GC / JIT and the main thread is running almost all the time, turn to CPU power judgment to check for frequency reduction, little core operation, CPU contention, or high system load. CPU-side evidence is insufficient, hand the scheduling evidence to the Main protocol; do not just write "CPU busy".

#### 2.2 Long Sleeping / D Time: Thread is not running, in a waiting or uninterruptible wait state

- If `sleeping` or `uninterruptible` has the highest proportion, execute [query-04-doframe-sleeping-d-state.sql](../sql-query/sql-kotlin-spatial-app-jank.md#query-04-doframe-sleeping-d-statesql-query-s--d-state-segments-within-doframe) to view `thread_state` details. 

- If `S` / `D` fragments cover the main time consumption of `doFrame`, do not write the parent Slice name as the root cause. At this point, the conclusion should shift to "the main thread is in a waiting / uninterruptible wait state within doFrame," and the next step must answer:
  - What is being waited for
  - Who the wait object is
  - Whether it can explain the user-visible dropped frames, ANR, or Input latency.

- It must be combined with `blocked_function`, overlapping Slices, system events, and call chains for further drill-down:
  - Common directions for `S` are `Binder`, `locks`, `condition variables`, `synchronous wait`, or `ordinary IO`.
  - Common directions for `D` are `disk IO`, `page fault`, `file mapping`, `resource loading`, or `kernel uninterruptible wait`. 

#### 2.3 Long Runnable Time: Thread wants to run but did not get CPU

- If `runnable` has the high proportion, the check if the main thread is runnable but did not obtain CPU. SQL refer to [query-05-doframe-runnable-state.sql](../sql-query/sql-kotlin-spatial-app-jank.md#query-05-doframe-runnable-statesql-query-runnable-segments-within-doframe) 
  - If so, shift to `CPU scheduling evidence`(./analysis-cpu-scheduling.md): whether the runqueue becomes longer in the same window, whether there is high-priority thread preemption on the same CPU, whether the target thread is placed on little cores or low-frequency cores, and whether there are cgroup / affinity / priority anomalies.

- The root cause for the Runnable path cannot be written as "main thread stuck." The verifiable conclusion should fall to "scheduling latency caused `doFrame` to exceed budget," listing CPU competing threads, runqueue, frequency/core type, or priority evidence. When evidence is insufficient, hand the scheduling evidence to the Main protocol for supplementary analysis.

### 3. Blocking Cause Drill-down

#### 3.1 Binder Wait

If `binder transaction`, `transact`, `Transaction`, `system service calls` appear in the main thread, or `thread_state` shows the main thread sleeping in the corresponding window, hand the remote-wait evidence to the Main protocol.
- First execute [query-06-doframe-binder-slices.sql](../sql-query/sql-kotlin-spatial-app-jank.md#query-06-doframe-binder-slicessql-query-binder--transact-slices-within-doframe) to confirm if the wait is within the over-budget `doFrame`, and then find if the remote end is `system_server`, Runtime services, audio services, window / input services, or business processes.
- Then check what the callee is doing in the same window: whether it is running slow, runnable starvation, continuing to wait for Binder, or blocked by locks / I/O / GC.
- Hand the remote-wait evidence to the Main protocol, which decides whether to append another subprotocol to the execution queue.

#### 3.2 Lock Contention

- If `monitor contention`, `Object.wait`, `LockSupport.park`, `futex_wait`, `Mutex`, `ConditionVariable`, and other signals appear in the main thread Slices or logs, then check if these waits cover the `doFrame` over-budget window, and then check if there is a lock holder in the same process or related threads. SQL can refer to [query-07-doframe-lock-wait-slices.sql](../sql-query/sql-kotlin-spatial-app-jank.md#query-07-doframe-lock-wait-slicessql-query-lock-wait--park--futex-slices-within-doframe).
  - Do not directly write "main thread waiting for lock" as the root cause; the root cause is usually that the lock holder is slow to release the lock in slow functions, Binder, I/O, GC, or scheduling starvation.

- The troubleshooting steps are: 
  1. first locate the wait Slice; 
  2. then find the holder based on the lock name, call stack, thread name, or overlapping business logs; 
  3. finally analyze why the holder did not release. 

- If the holder is runnable but not running, hand back scheduling evidence; if the holder is in Binder, hand back remote-wait evidence; if the holder is covered by GC STW, hand back memory-pressure evidence. The Main protocol applies the shared Activation Gate.

#### 3.3 GC Stop-the-world

- If `SuspendAll`, Stop-the-world, GC pause overlap with the app jank frame window, then calculate the pause duration and overlap degree. SQL can refer to [query-08-gc-overlap-doframe.sql](../sql-query/sql-kotlin-spatial-app-jank.md#query-08-gc-overlap-doframesql-query-overlap-between-gc-and-main-thread-doframe).
- Only when the GC pause covers critical time in the over-budget window and can explain `doFrame` timeout, Input timeout, or abnormal frames, can it be a root cause candidate. If GC is just frequent during the same period but does not overlap, hand the memory evidence to the Main protocol for supplementary analysis.

#### 3.4 Input Timeout

- If `deliverInputEvent`, `ViewRootImpl`, `InputEventReceiver`, `Input dispatching timed out` appear or the ANR reason points to Input dispatching timeout, then align the input event processing window with `doFrame`, main thread leaf Slices, `thread_state`, Binder / lock / GC evidence. SQL can refer to [query-09-doframe-input-slices.sql](../sql-query/sql-kotlin-spatial-app-jank.md#query-09-doframe-input-slicessql-query-input--viewrootimpl-slices-within-doframe)

- Input timeout is not a root cause name; it is only a user-visible result. The root cause must still fall to the main thread running in a slow function, waiting for Binder, waiting for a lock, being paused by GC STW, or being runnable but not obtaining CPU at that time.

### 4. Spatial SDK Specific Checks

- Spatial SDK related checks should be integrated into the above drill-down process rather than as an independent parallel guesswork direction. If the main thread over-budget `doFrame` coincides with a Spatial abnormal frame window, continue to check if `AppProduce` in `OpenXRClientSpatialFrames` is extended. If AppProduce rises synchronously with `doFrame`, it indicates that App-side UI / scene submission might be the upstream of the abnormal frame. If AppProduce is normal while EngineRender, GPU, or compositor is abnormal, return to `analysis-spatial-engine.md` to judge if it is not a main thread root cause.

- Check if `XR_Wait` / `XR_BeginFrame` appear on the main thread and cover the `doFrame` window. If these waits are just normal frame rhythm control, they should not be written as the root cause. Only when they cause the main thread to fail to process UI/Input in time and overlap with abnormal frames or ANR windows can they be candidate root causes. If the main thread waits for Spatial SDK initialization, resource submission, scene entity updates, or native callbacks, while `Spatial_Main` waits for App-side results, system services, or other threads, record the cross-thread dependency chain and hand the evidence to the Main protocol.

- Refer to [spatial-metrics.md](../common/spatial-metrics.md) to judge if the CPU bottleneck comes from the Spatial SDK itself. `SpatialMetrics` is explanatory evidence and cannot be the final root cause alone; it must be judged jointly with `SpatialFrames`, main thread `doFrame`, leaf Slices, `thread_state`, `Spatial_Main`, or EngineRender in the same time window.

### 5. Root Cause Judgment Rules

- Root cause judgment must simultaneously meet the following conditions: the abnormal event is in the same time window as the user-visible phenomenon; it can be traced to a specific thread and specific Slice; GPU bottlenecks, Runtime-side causes, and OpenXR Compositor's own anomalies have been excluded.

- If the evidence can only prove "the main thread was very slow during a certain period" but cannot prove it caused Late/Miss/ANR, the conclusion should be downgraded to a candidate root cause, with constraints and next-step evidence collection directions clearly written.

## SQL Query Index

Full SQL see [Kotlin Spatial App Main Thread Jank SQL Query Set](../sql-query/sql-kotlin-spatial-app-jank.md). This protocol is called in the following order:

| Phase | Query |
|---|---|
| Locating over-budget `doFrame` | `query-01-overbudget-doframe.sql` |
| Summarizing thread state proportions within `doFrame` | `query-02-doframe-thread-state-bucket.sql` |
| Running path: Querying leaf Slices | `query-03-doframe-leaf-slices.sql` |
| Sleeping / D path: Querying wait states | `query-04-doframe-sleeping-d-state.sql` |
| Runnable path: Querying scheduling latency fragments | `query-05-doframe-runnable-state.sql` |
| Binder wait | `query-06-doframe-binder-slices.sql` |
| Lock contention | `query-07-doframe-lock-wait-slices.sql` |
| GC STW overlap | `query-08-gc-overlap-doframe.sql` |
| Input / ViewRootImpl alignment | `query-09-doframe-input-slices.sql` |

## Output Template

```text
1. Jank Time Window:
2. Jank Type:
3. Critical Slice/Event:
4. Root Cause Judgment:
5. Constraints:
6. Next Step Suggestions:
```

## Controller Handoff

Hand back the abnormal-window, critical-path, and mechanism evidence to the Main protocol. The Main protocol decides whether the evidence activates another subprotocol; this document does not name or activate other subprotocols.
