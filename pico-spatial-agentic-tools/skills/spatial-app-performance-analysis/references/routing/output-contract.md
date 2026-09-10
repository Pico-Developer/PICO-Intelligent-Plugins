---
issue_type_key: spatial_frame_abnormal
protocol: spatial-engine
activated_subprotocols: [binder, memory, cpu_sched]
topic_state:
  activation: activated
  execution: completed
  closure_level: server_cause
  causal_role: primary_cause
  controller_handoff: []
time_window: "2026-07-31 14:03:12 ~ 2026-07-31 14:03:25"
symptoms: "Obvious frame drops while dragging the model, with visual stutter and delayed head-tracking follow."
target:
  package: "com.example.spatial.app"
  process: "com.example.spatial.app"
  threads: ["Spatial_Main", "Eng-Render", "RenderThread"]
evidence:
  - id: e1
    type: perfetto_trace
    location: "trace-perf.perfetto-trace"
    one_line_finding: "Continuous Late Frames appear within the issue window, and the APP Produce stage exceeds the budget."
  - id: e2
    type: perfetto_sql
    location: "sql-report-queries.md#spatial"
    one_line_finding: "The peak window of Late/Miss Frames overlaps with Eng-Render runnable starvation."
  - id: e3
    type: screenshot
    location: "Perfetto screenshot provided by the user (SpatialFrames panel)"
    one_line_finding: "Late Frames are concentrated within 1–2 seconds after the drag gesture starts."
conclusion_level: likely
root_cause: "Within the issue window, the Eng-Render thread is runnable but not running for a long time, causing the EngineRender stage to exceed the budget and trigger Late Frames."
next_actions:
  - "Within the issue window, further confirm the contending threads (same CPU/same cluster) and scheduling policy; if needed, dive deeper via the cpu_sched sub-protocol."
  - "Reduce render workload on the drag path: reduce the number of objects updated per frame, merge DrawCalls, or lower material complexity."
  - "Collect another trace with GPU tracks/frequency enabled to rule out GPU/Compositor-side bottlenecks."
limitations:
  - "The current trace does not include full GPU counters, so it cannot confirm whether the GPU is saturated within the same window."
extensions:
  spatial:
    abnormal_frame_types: ["late"]
    stage: "EngineRender"
    bottleneck_side: "engine"
    pressure_source: "render_workload"
  cpu_sched:
    thread_state_summary: "Eng-Render: runnable but insufficient running"
    sched_latency_ms: 18.4
    runqueue: "big cluster rq length is relatively high"
    cpu_cluster_freq: "big cluster frequency briefly drops"
    contenders: ["system_server:Binder", "surfaceflinger"]
---

# Unified Output Contract

This document defines the unified output contract after any `analysis-*` topic analysis is completed. The goal is twofold: first, to ensure every analysis conclusion has a consistent structure for review and collaboration; second, to make it machine-queryable, aggregatable, and automatable via the YAML header (e.g., Graphify).

This contract consists of two parts: the top YAML header (required, machine-readable) and the main body with 6 sections (required, human-readable). Any topic must output at least these two parts. If topic-specific fields are needed, extend under `extensions` in the YAML.

## 1. YAML Header (Required, Machine-Readable)

The YAML header is used to structurally record "what the issue is, where the evidence is, how certain the conclusion is, and what to do next". Field conventions are as follows (all fields except `extensions` are recommended to be filled as much as possible; key fields must be filled).

### 1.1 Required Key Fields

- `issue_type_key`: performance issue type enum key (Graphify query primary key)
  - enum values:
    - `spatial_frame_abnormal`
    - `binder_latency`
    - `memory_gc_jank`
    - `cpu_sched_latency`
    - `spatial_audio_perf`
    - `app_main_thread_jank`
- `protocol`: the main protocol/current topic for this analysis (e.g., `spatial-engine` / `binder` / `memory` / `cpu_sched` / `spatial_audio` / `app_jank`)
- `activated_subprotocols`: list of activated sub-protocols (e.g., `[binder, memory, cpu_sched]`)
- `topic_state`: lifecycle state for the current topic. `activation` records that routing added the topic; `execution` is `completed`, `completed_with_evidence_gap`, or `blocked`; `closure_level` is defined by the topic; `causal_role` is the post-analysis role. These fields must not be inferred from one another.
- `controller_handoff`: optional list of cross-topic evidence items handed to the Main protocol. The subprotocol does not name, activate, or skip another subprotocol.
- `time_window`: the issue time window (recommended to write a readable time range or a timestamp range within the trace)
- `symptoms`: user-visible symptom summary (1–2 sentences)
- `target`: target package/process/key threads (recommended to include at least `package`/`process`; threads are optional)
- `evidence`: list of evidence items (each should include at least: evidence type, location, one-line conclusion)
- `conclusion_level`: conclusion confidence level
  - `confirmed`: evidence closed loop; can directly prove the root cause
  - `likely`: highly relevant with a plausible mechanism, but still missing 1–2 key evidence points
  - `candidate`: candidate direction; some correlation exists but insufficient to explain the whole symptom
  - `insufficient_evidence`: insufficient evidence; cannot form a reliable root cause
- `root_cause`: one-line root cause (when `insufficient_evidence`, you can write "Evidence is still missing; no conclusion yet")
- `next_actions`: list of next actions (optimization/troubleshooting/evidence supplementation)
- `limitations`: constraints/missing evidence (e.g., the trace misses some tracks, missing GC logs, etc.)
- `extensions.knowledge_base`: record of KB assistance. For a PICO Spatial diagnosis with an exposed `pico-spatial-knowledge` MCP or configured PerformanceKB backend, this record is mandatory and governed by the [PICO Spatial PerformanceKB Mandatory Gate](../common/knowledge-base-usage.md): fill the backend, gate stage statuses, matched entries, and selected observation states. For generic OS6 workflows with no exposed backend, it is optional and records the unavailable/retrieval-failed status instead. KB-derived content remains advisory and cannot replace trace evidence.

### 1.2 Recommended evidence Item Format

`evidence` is a list. Each list element is recommended to be an object:

- `id`: short stable id (`e1`, `e2`, ...) so downstream aggregation and classification steps can reference this evidence item unambiguously. Recommended for every item.
- `type`: e.g., `perfetto_trace` / `perfetto_sql` / `logcat` / `tombstone` / `screenshot` / `systrace` / `bugreport`, etc.
- `location`: path, link, screenshot description, or SQL file location
- `one_line_finding`: one-line conclusion (keep it "verifiable and traceable"; avoid vague words)

### 1.3 extensions: Topic Extension Fields (Optional)

Each topic can extend topic-specific fields under `extensions` in the YAML header. Below is the recommended extension field set for each topic. You can fill them as needed based on actual evidence; omit missing fields.

- `extensions.spatial` (spatial frame abnormal / Spatial main protocol)
  - `abnormal_frame_types`: list of abnormal frame types (e.g., late/miss/discard)
  - `stage`: abnormal stage (`APP Produce` / `SPR Consume` / `EngineRender` / `GPU` / `Compositor`)
  - `bottleneck_side`: bottleneck side (e.g., app/spr/engine/gpu/compositor)
  - `pressure_source`: pressure source (e.g., render_workload/binder_wait/gc/memory_pressure, etc.)
- `extensions.binder` (Binder topic)
  - `caller`: caller (process/thread)
  - `callee`: callee (process/thread; often `system_server` or a service process)
  - `transaction_name_or_code`: transaction name or code
  - `wait_time_ms`: wait duration (ms)
  - `downstream_dependency`: downstream dependency (e.g., locks the service is waiting on, I/O, other Binder, CPU runnable starvation, etc.)
- `extensions.memory` (memory / GC topic)
  - `memory_metrics`: memory-metric summary (PSS/RSS/USS, heap, DMA-BUF, etc.)
  - `gc_events`: GC event summary (type, count, key timestamps, STW situation)
  - `lmk_oom`: LMK/OOM info (whether it happened, related process, timestamps)
  - `baseline_compare`: how it was compared with a baseline and the conclusion
- `extensions.cpu_sched` (CPU scheduling topic)
  - `thread_state_summary`: thread state summary (running/runnable/blocked, etc.)
  - `sched_latency_ms`: scheduling latency (ms)
  - `runqueue`: runqueue observation conclusion (length, which CPUs/clusters it concentrates on)
  - `cpu_cluster_freq`: CPU cluster frequency/core distribution summary
  - `contenders`: list of primary contending threads
- `extensions.spatial_audio` (spatial audio topic)
  - `api_type`: API type (e.g., AudioTrack/OpenSL ES/AAudio/engine wrapper, etc.)
  - `usage`: usage scenario/purpose
  - `instance_count`: instance count
  - `resource_format`: resource format (sample rate/channels/codec/buffer, etc.)
  - `lifecycle_issues`: lifecycle issues (leak/duplicate creation/no reuse, etc.)
  - `need_benchmark`: whether a benchmark is needed and why
- `extensions.app_jank` (App main-thread jank topic)
  - `jank_type`: `running_slow` / `binder_wait` / `lock_wait` / `gc_stw` / `runnable_starvation` / `io_d_state` / `input_timeout`
  - `key_slices`: list of key slices (e.g., `Choreographer#doFrame`, `deliverInputEvent`, etc.)
  - `doframe_budget_ms`: target budget (ms)
- `extensions.knowledge_base` (cross-topic KB assistance)
  - `status`: `available` / `unavailable` / `retrieval_failed`
  - `global_triage`: `matched` / `not_matched` / `query_failed` / `not_run`
  - `selected_observations`: list of `{name, state, reason}` where `state` is `planned` / `queried` / `unavailable` / `not_applicable` / `deferred`
  - `window_anchored_query`: one-line query and result summary, or an explicit skip reason

## 2. Main Body (Required, Fixed 6 Sections)

The main body explains "how the conclusion was reached". It must contain the following 6 sections, and it is recommended that each section can be quickly reproduced and verified by others.

### ① Symptom

Describe the user-visible symptom in plain language, and clearly state the trigger path and time window. Try to include "what operation triggers it, how long it lasts, whether it is reproducible, whether it is accompanied by frame drops/stutters/audio anomalies, etc.".

### ② Existing Evidence

List the obtained materials by evidence type, and provide a one-line conclusion for each item. Every evidence item should be traceable back to a specific location (trace file, SQL query, screenshot, log snippet, etc.).

### ③ Investigation Process

Describe the investigation steps in a reproducible way: which tracks/tables/metrics you started from, how you narrowed down the time window, how you aligned symptoms with system behavior, and why you ruled out other possibilities.

### ④ Root Cause Judgment

Provide a one-line root cause conclusion and describe the "evidence closed-loop degree", while marking the confidence level (consistent with `conclusion_level` in the YAML).

### ⑤ Actions (Optimization/Troubleshooting)

Provide actionable recommendations. Prefer actions that are "minimal change/fastest validation". For troubleshooting actions, specify what evidence to supplement, how to collect it, and what signals you expect to see.

### ⑥ Limitations and Next Validation

Clarify the boundary of the current analysis: what key evidence is missing, what assumptions are not yet verified, whether you need to recollect the trace (e.g., with sched, GPU counters, GC logs, etc.), and what it means if the next validation passes/fails.

## 3. Full Output Example (spatial_frame_abnormal)

The YAML header above already provides a complete example that can be reused directly. You can use it as a template: replace fields such as `issue_type_key`, `protocol`, `time_window`, `target`, `evidence`, `root_cause`, etc. with the real information for the current issue, and add `extensions.spatial` (and other activated sub-protocol extension fields) under `extensions` as needed.

Below we complete the example’s 6 main-body sections to demonstrate the integrated output of "machine-readable + human-readable".

### ① Symptom

Within 1–2 seconds after dragging the model (continuous gesture operation), there are obvious frame drops, the image stutters, and there is delayed follow during headset rotation. The user subjectively feels it as "every time I drag, it stutters". The issue is reproducible, and it is more obvious only after resource loading is completed in a particular scenario.

### ② Existing Evidence

Evidence 1: Perfetto trace (`trace-perf.perfetto-trace`) shows continuous Late Frames within the issue window, and the APP Produce stage clearly exceeds the budget. Evidence 2: SQL query results show that the peak window of Late/Miss Frames overlaps with Eng-Render runnable starvation (runnable but lacking running). Evidence 3: The SpatialFrames panel screenshot indicates Late Frames are concentrated within a short window after the drag gesture starts.

### ③ Investigation Process

First, use the user symptom to determine the issue window, and lock the Late Frame cluster in SpatialFrames/SpatialMetrics. Then align Eng-Render and related render-thread slices, and confirm that within the same window there is a signal of "the thread is runnable but cannot get CPU". Next, check whether there is an obvious long Binder wait or GC Stop-the-world overlapping the window, to rule out candidate directions such as "stuck in service calls" or "stuck in GC". The current evidence better supports that scheduling contention causes the EngineRender stage to exceed the budget.

### ④ Root Cause Judgment

The root cause judgment is: within the issue window, the Eng-Render thread is runnable but not running for a long time, causing the EngineRender stage to exceed the budget and trigger Late Frames. The confidence level is likely, because scheduling starvation highly matches the abnormal-frame window, but it still lacks full GPU counters and finer-grained evidence about contending threads/scheduling policy to fully close the loop.

### ⑤ Actions (Optimization/Troubleshooting)

It is recommended to first strengthen the evidence closed loop: within the same window, identify the primary contending threads (same CPU/same cluster) and CPU frequency changes; if needed, dive deeper via the cpu_sched sub-protocol. For optimization actions, prioritize reducing render workload on the drag path, such as reducing the number of objects updated per frame, merging DrawCalls, and lowering material complexity, and validate whether Late Frames significantly decrease. If anomalies still exist, recollect a trace with GPU counters/frequency data to rule out GPU/Compositor-side bottlenecks.

### ⑥ Limitations and Next Validation

The current limitation is that the trace does not include full GPU-side counters, so it cannot confirm whether the GPU is saturated in the same window; meanwhile, the identification of contending threads is still relatively coarse. Next validation proceeds in two parallel tracks: (1) recollect a trace including sched and GPU counters to verify whether scheduling starvation or GPU saturation better matches the abnormal-frame window; (2) reduce workload on the drag path and run regression validation—if Late Frames decrease accordingly, it further supports "EngineRender workload/scheduling contention" as the primary cause.
