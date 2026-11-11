# Unified Output Contract

This document defines the unified output contract after any `analysis-*` topic analysis is completed. The goal is twofold: first, to ensure every analysis conclusion has a consistent structure for review and collaboration; second, to make it machine-queryable, aggregatable, and automatable via the sidecar meta JSON (e.g., Graphify).

Every topic analysis produces **two sibling files** in `session-output-<timestamp>/topic-result/`:

- `output-<topic>.md` — the **human-readable** body with the fixed 6 sections.
- `output-<topic>.meta.json` — the **machine-readable** sidecar; the authoritative source for all structured fields.

The `.md` and `.meta.json` MUST have the same basename and live in the same directory. The `.meta.json` carries all machine fields; the `.md` is pure Markdown (no YAML / no front matter).

## 1. Topic Meta JSON (Required, Machine-Readable)

The topic meta JSON is used to structurally record "what the issue is, where the evidence is, how certain the conclusion is, and what to do next". Field conventions are as follows (all fields except `extensions` are recommended to be filled as much as possible; key fields must be filled).

### 1.0 Minimal shape

```json
{
  "schema_version": "1.0",
  "topic": "spatial-engine",
  "protocol": "spatial-engine",
  "issue_type_key": ["spatial_frame_abnormal"],
  "activated_subprotocols": ["spatial-engine"],
  "topic_state": {
    "activation": "activated",
    "execution": "completed",
    "closure_level": "server_cause",
    "causal_role": "primary_cause",
    "controller_handoff": []
  },
  "conclusion_level": "likely",
  "time_window": "2026-07-31 14:03:12 ~ 2026-07-31 14:03:25",
  "symptoms": "Obvious frame drops while dragging the model, with visual stutter and delayed head-tracking follow.",
  "target": {
    "package": "com.example.spatial.app",
    "process": "com.example.spatial.app",
    "threads": ["Spatial_Main", "Eng-Render", "RenderThread"]
  },
  "evidence": [
    {
      "id": "e1",
      "type": "perfetto_trace",
      "location": "trace-perf.perfetto-trace",
      "one_line_finding": "Continuous Late Frames appear within the issue window, and the APP Produce stage exceeds the budget."
    }
  ],
  "root_cause": "Within the issue window, the Eng-Render thread is runnable but not running for a long time, causing the EngineRender stage to exceed the budget and trigger Late Frames.",
  "next_actions": [{ "action": "Reduce render workload on the drag path", "priority": "P0" }],
  "limitations": [
    "The current trace does not include full GPU counters, so it cannot confirm whether the GPU is saturated within the same window."
  ],
  "extensions": {
    "spatial": {
      "abnormal_frame_types": ["late"],
      "stage": "EngineRender",
      "bottleneck_side": "engine",
      "pressure_source": "render_workload"
    }
  },
  "sections_file": "output-spatial-engine.md",
  "sections_in_body": {
    "symptom": "① Symptom",
    "existing_evidence": "② Existing Evidence",
    "investigation_process": "③ Investigation Process",
    "root_cause_judgment": "④ Root Cause Judgment",
    "actions": "⑤ Actions (Optimization/Troubleshooting)",
    "limitations_and_next_validation": "⑥ Limitations and Next Validation"
  }
}
```

A larger end-to-end example lives at [`templates/topic_meta_example.json`](../../templates/topic_meta_example.json).

### 1.1 Required Key Fields

- `schema_version`: current contract version (string, currently `"1.0"`).
- `topic`: the current topic id (e.g., `spatial-engine` / `binder` / `memory` / `cpu_sched` / `spatial-audio` / `kotlin-spatial-app-jank`).
- `issue_type_key`: performance issue type enum key list (Graphify query primary key).
  - enum values:
    - `spatial_frame_abnormal`
    - `binder_latency`
    - `memory_gc_jank`
    - `cpu_sched_latency`
    - `spatial_audio_perf`
    - `app_main_thread_jank`
- `protocol`: the main protocol for this analysis (e.g., `spatial-engine` / `binder` / `memory` / `cpu_sched` / `spatial_audio` / `app_jank`).
- `activated_subprotocols`: list of activated sub-protocols (e.g., `["binder", "memory", "cpu_sched"]`).
- `topic_state`: lifecycle state for the current topic. `activation` records that routing added the topic; `execution` is `completed`, `completed_with_evidence_gap`, or `blocked`; `closure_level` is defined by the topic; `causal_role` is the post-analysis role. These fields must not be inferred from one another.
- `topic_state.controller_handoff`: optional list of cross-topic evidence items handed to the Main protocol. The subprotocol does not name, activate, or skip another subprotocol.
- `time_window`: the issue time window (recommended to write a readable time range or a timestamp range within the trace).
- `symptoms`: user-visible symptom summary (1–2 sentences).
- `target`: target package/process/key threads (recommended to include at least `package`/`process`; `threads` are optional).
- `evidence`: list of evidence items (each should include at least: evidence type, location, one-line conclusion).
- `conclusion_level`: conclusion confidence level
  - `confirmed`: evidence closed loop; can directly prove the root cause
  - `likely`: highly relevant with a plausible mechanism, but still missing 1–2 key evidence points
  - `candidate`: candidate direction; some correlation exists but insufficient to explain the whole symptom
  - `insufficient_evidence`: insufficient evidence; cannot form a reliable root cause
- `root_cause`: one-line root cause (when `insufficient_evidence`, you can write "Evidence is still missing; no conclusion yet").
- `next_actions`: list of next actions (optimization/troubleshooting/evidence supplementation). Each item is an object `{ "action": "...", "priority": "P0|P1|P2" }`.
- `limitations`: constraints/missing evidence (e.g., the trace misses some tracks, missing GC logs, etc.).
- `sections_file`: relative path (within the topic-result directory) to the sibling `.md` body file.
- `sections_in_body`: map of section id → the exact Markdown heading text used in the `.md` body. Downstream tools match headings verbatim.
- `extensions.knowledge_base`: record of KB assistance. For a PICO Spatial diagnosis with the general plugin's `pico-dev-knowledge` MCP exposed, this record is mandatory and governed by the [PICO Spatial PerformanceKB Mandatory Gate](../common/knowledge-base-usage.md): fill the actual backend name, gate stage statuses, matched entries, and selected observation states. Run retrieval through the general plugin's `knowledge-query` Skill rather than calling the MCP directly. For generic OS6 workflows with no exposed backend, it is optional and records the unavailable/retrieval-failed status instead. KB-derived content remains advisory and cannot replace trace evidence.

### 1.2 Recommended evidence Item Format

`evidence` is a list. Each list element is recommended to be an object:

- `id`: short stable id (`e1`, `e2`, ...) so downstream aggregation and classification steps can reference this evidence item unambiguously. Recommended for every item.
- `type`: e.g., `perfetto_trace` / `perfetto_sql` / `logcat` / `tombstone` / `screenshot` / `systrace` / `bugreport`, etc.
- `location`: path, link, screenshot description, or SQL file location
- `one_line_finding`: one-line conclusion (keep it "verifiable and traceable"; avoid vague words)

### 1.3 extensions: Topic Extension Fields (Optional)

Each topic can extend topic-specific fields under `extensions` in the topic meta JSON. Below is the recommended extension field set for each topic. You can fill them as needed based on actual evidence; omit missing fields.

- `extensions.spatial` (spatial frame abnormal / Spatial main protocol)
  - `abnormal_frame_types`: list of abnormal frame types (e.g., `late`/`miss`/`discard`)
  - `stage`: abnormal stage (`APP Produce` / `SPR Consume` / `EngineRender` / `GPU` / `Compositor`)
  - `bottleneck_side`: bottleneck side (e.g., `app`/`spr`/`engine`/`gpu`/`compositor`)
  - `pressure_source`: pressure source (e.g., `render_workload`/`binder_wait`/`gc`/`memory_pressure`, etc.)
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
  - `selected_observations`: list of `{ "name": "...", "state": "...", "reason": "..." }` where `state` is `planned` / `queried` / `unavailable` / `not_applicable` / `deferred`
  - `window_anchored_query`: one-line query and result summary, or an explicit skip reason

## 2. Main Body (Required, Fixed 6 Sections)

The main body (the `.md` file) explains "how the conclusion was reached". It must contain the following 6 sections. Each section heading MUST match the value declared in `sections_in_body`. Downstream renderers match the headings verbatim and extract the content between consecutive section headings.

### ① Symptom

Describe the user-visible symptom in plain language, and clearly state the trigger path and time window. Try to include "what operation triggers it, how long it lasts, whether it is reproducible, whether it is accompanied by frame drops/stutters/audio anomalies, etc.".

### ② Existing Evidence

List the obtained materials by evidence type, and provide a one-line conclusion for each item. Every evidence item should be traceable back to a specific location (trace file, SQL query, screenshot, log snippet, etc.).

### ③ Investigation Process

Describe the investigation steps in a reproducible way: which tracks/tables/metrics you started from, how you narrowed down the time window, how you aligned symptoms with system behavior, and why you ruled out other possibilities.

### ④ Root Cause Judgment

Provide a one-line root cause conclusion and describe the "evidence closed-loop degree", while marking the confidence level (consistent with `conclusion_level` in the sidecar JSON).

### ⑤ Actions (Optimization/Troubleshooting)

Provide actionable recommendations. Prefer actions that are "minimal change/fastest validation". For troubleshooting actions, specify what evidence to supplement, how to collect it, and what signals you expect to see.

### ⑥ Limitations and Next Validation

Clarify the boundary of the current analysis: what key evidence is missing, what assumptions are not yet verified, whether you need to recollect the trace (e.g., with sched, GPU counters, GC logs, etc.), and what it means if the next validation passes/fails.

## 3. Cross-File Reference Rules

To avoid ambiguity, cross-file references follow two simple rules:

- **Machine-to-machine references** → always point to the `.meta.json` (the authoritative entry).
  - Examples: `final-summary.meta.json.next_actions[].sources`, `final-summary.meta.json.topic_outputs[].file`.
- **Human / HTML display references** → point to the `.md`.
  - Examples: "see output-binder.md" in prose, "View topic details" button in the HTML report.

## 4. Full Output Example (spatial_frame_abnormal)

A complete topic sidecar example that can be reused directly lives at [`templates/topic_meta_example.json`](../../templates/topic_meta_example.json). Below we complete the example's 6 main-body sections (which live in the sibling `.md`) to demonstrate the integrated output of "machine-readable sidecar + human-readable body".

### ① Symptom

Within 1–2 seconds after dragging the model (continuous gesture operation), there are obvious frame drops accompanied by visual stutter; head-tracking follow is slightly delayed; the issue is reproducible with the same gesture.

### ② Existing Evidence

- Perfetto trace shows continuous Late Frames in `trace-perf.perfetto-trace` within the issue window.
- Perfetto SQL queries show the APP Produce stage exceeds the budget and the Eng-Render runnable starvation window overlaps with the Late Frame peak (see `references/sql-query/sql-report-queries.md#spatial`).
- A user-provided SpatialFrames screenshot concentrates Late Frames inside the 1–2s window after the drag starts.

### ③ Investigation Process

Starting from the SpatialFrames panel, narrowed the issue window to the first 2 seconds after the drag; aligned the Late Frame cluster with the Eng-Render runnable-but-not-running segments; ruled out GC storms (no concurrent copying STW in the same window) and spatial-audio IPC storms (no bursty audio create/destroy); converged on resource rebuild on scene switch as the dominant cause.

### ④ Root Cause Judgment

Resource rebuild on scene switch produces a GPU-bound workload spike that collapses the frame budget. `conclusion_level: likely` — the mechanism is plausible and strongly correlated, but GPU counters are missing and would be needed to upgrade to `confirmed`.

### ⑤ Actions (Optimization/Troubleshooting)

- Amortize scene-switch resource rebuild across multiple frames (P0).
- Reduce per-frame draw-call count on the drag path (P1).
- Recollect a trace with GPU tracks + frequency enabled to definitively rule out GPU saturation (troubleshooting).

### ⑥ Limitations and Next Validation

The current trace lacks GPU counters, so GPU saturation cannot be fully excluded as a concurrent root cause. If the next trace (with GPU counters) still shows the same Late Frame cluster while GPU is not saturated, this conclusion can be upgraded to `confirmed`; if GPU is saturated, the primary cause switches to the GPU-side bottleneck.
