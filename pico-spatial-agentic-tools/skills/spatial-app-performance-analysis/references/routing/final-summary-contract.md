# Final Summary Output Contract

Final summary only aggregates topic outputs by reference and adds the cross-topic evidence chain; do not duplicate per-topic analysis content.

## 1. File Naming
- File name: `final-summary.md`
- Location: the current run's session directory `session-output-<timestamp>/`

## 2. Session Output Directory Convention

Each analysis run MUST write into its own timestamped session directory so that different runs never overwrite each other. Create the root once at the start of a run and reuse it for every artifact of that run:

- Root: `session-output-<timestamp>/`
- `<timestamp>` format: `YYYYMMDD-HHMMSS` (e.g. `session-output-20260804-103012/`)
- Resolve the concrete root once, then write every capture, topic, summary, and report of that run under it. Do not fall back to a bare `session-output/`.

```text
session-output-<timestamp>/
├── performance-data/            # all collected intermediate performance data
│   ├── trace-perf.perfetto-trace
│   ├── fast-perf.json
│   ├── trace-probe-detail.yaml  # spatial_probe.py output
│   └── report-data.json         # query_report_data.py output
├── topic-result/                # per-topic analysis outputs
│   ├── output-spatial-engine.md
│   ├── output-binder.md
│   └── output-cpu-sched.md
├── final-summary.md             # final aggregation (references topic-result/*)
├── root-cause-classification.yaml  # standalone closed-taxonomy artifact (see root-cause-classification-contract.md)
└── report.html                  # generate_report.py output
```


## 3. Reference Rules
- Each executed topic must have one file: `output-<topic>.md`
- Put topic outputs under `<session-output-dir>/topic-result/`
- Reference topic outputs with relative runtime paths such as ./topic-result/output-binder.md.
- Do not copy topic YAML headers or full body content into `final-summary.md`
- Topic summary text in the index table must stay to one line

## 4. `final-summary.md` Format
### 4.1 YAML Header
| Field | Description |
| --- | --- |
| `issue_type_key` | Deduplicated union of all topic `issue_type_key` values |
| `activated_subprotocols` | Deduplicated union of topics actually activated by Analysis Topic Routing |
| `conclusion_level` | Overall confidence; use the worst topic level |
| `root_cause` | One-sentence cross-topic integrated root cause |
| `next_actions` | Merged and deduplicated actions with priority and source links |
| `limitations` | Merged limitations |
| `topic_outputs` | Topic list with topic name, file path, and topic `conclusion_level` |
| `routing_registry` | One status for every topic in the Common Topic Map: `executed`, `not_activated`, or `blocked`, with evidence references |
`conclusion_level` order: `confirmed` → `likely` → `candidate` → `insufficient_evidence`

### 4.2 Body Sections
- `A. Topic Output Index`: table of executed topics, output links, topic `conclusion_level`, one-line root cause summary
- `B. Cross-Topic Evidence-Chain Analysis`: newly written causal / temporal / dependency chain across topic outputs
- `C. Directions to Extend`: unexecuted topics, trigger signal, and missing required evidence
- `D. Final Action Plan`: merged actions sorted by priority with source topic links

### 4.3 Closure Check (Required Before Finalizing)
Before emitting the final summary, verify that no evidence-backed clue was left unexecuted:
- Every sub-protocol named in any topic's `activated_subprotocols` MUST appear in `A. Topic Output Index` with its own executed `output-<topic>.md`. If it does not, either execute it now or remove it from `activated_subprotocols`; an activated sub-protocol with no executed output is a contract violation.
- A topic activated and executed with `topic_state.execution: completed_with_evidence_gap` still counts as executed. Preserve its `closure_level`, concrete evidence gaps, and capped `conclusion_level` in the index.
- `routing_registry` is mandatory. Every topic in the Common Topic Map must be present, including topics that were not activated. `not_activated` requires evidence showing that temporal overlap or dependency relevance failed; `blocked` requires the exact missing minimum evidence. An omitted registry entry is a routing failure.
- **PICO Spatial KB gate barrier**: when the target is a PICO Spatial diagnosis and a `pico-spatial-knowledge` MCP or configured PerformanceKB backend is exposed, `extensions.knowledge_base.gate.complete` MUST be `true` before any topic or the final summary may emit `confirmed` or `likely`. If the gate is incomplete (missing stages, failed probe/retrieval, or backend not consulted), cap `conclusion_level` at `candidate` for any KB-relevant conclusion and `insufficient_evidence` when the gap removes required discriminating evidence, and record the missing stages in `limitations`. This barrier does not apply to generic OS6 workflows with no exposed backend; those follow the unavailable-backend fallback in [Performance Knowledge Base Usage Constraints](../common/knowledge-base-usage.md).
- `C. Directions to Extend` may only contain clues whose required evidence is genuinely missing. For each entry, the specific missing evidence must be named. A clue whose evidence already exists in the current trace must NOT be parked here — it must have been executed as its own topic instead.
- A partially analyzed chain (for example Binder proven on the caller side but never resolved on the callee side, while the trace still contains the callee) does not count as an executed topic for the unresolved side; state the concrete missing evidence, do not present it as complete.

After the summary is finalized, produce the standalone `root-cause-classification.yaml` as the last step per the [Root Cause Classification Contract](root-cause-classification-contract.md). Do NOT embed that classification into `final-summary.md`; keep it in its own file.

## 5. HTML Report (`report.html`)

The exact data every report section requires — the full `reportData` schema, each field's source, whether it is required, and how missing values degrade — is defined in the [HTML Report Data Contract](report-data-contract.md).

### 5.1 Get Overview data

Use `query_report_data.py` to get the single source of truth:
```bash
python3 scripts/query_report_data.py \
  --session <pico_cli_perf_session_id> \
  --trace <path_of_your_perfetto_trace> \
  --fast-perf <path_of_your_fast_perf_if_available> \
  --output <path_of_your_output_json_file>
```

`--fast-perf` is optional for report data generation. When it is missing, `query_report_data.py` must still write trace-derived `details` such as App frame buckets, SPR frame types, SPR CPU/GPU buckets, and SPR stats. In that mode, quick diagnosis trend fields are empty and the HTML report hides the Quick Diagnosis Overview section instead of showing empty charts.

Prefer passing the existing `pico-cli perf trace load` session ID. If `--session` is omitted, the script starts/uses the `pico-cli perf` daemon and loads the trace with `pico-cli perf trace load --spatial-diagnose true` before querying. The script must consume the Spatial diagnostic tables that `pico-cli perf trace load --spatial-diagnose true` creates, such as `OpenXRClientSpatialFrames`; it must not recreate those tables itself and must not invoke `trace_processor_shell` directly. If report-data generation fails, fix the `pico-cli perf` session/query path or record the artifact failure; do not switch to a direct trace processor fallback.

### 5.2 Generate HTML Report

Use `generate_report.py` to generate a html report. `generate_report.py` accepts two upstream shapes:

- A YAML file that already contains `analysis_topics` or `analysis_report`.
- The canonical `session-output-<timestamp>/final-summary.md` produced by this Skill. In this mode, the script extracts the Markdown file's YAML header, resolves `topic_outputs[*].file`, loads each referenced topic result, and synthesizes the `analysis_topics` payload automatically.

**Execution order and failure semantics**

The Main protocol MUST complete the dynamic topic loop, write every executed topic output, perform the closure check, and write `final-summary.md` before invoking the HTML generator. The generator then resolves every `topic_outputs[].file`, builds a complete report data object, validates the rendered topic set, and atomically replaces `report.html`. If any reference, schema, template marker, or post-generation validation fails, treat HTML generation as failed and do not use a stale or partially written report.

HTML generation is a required terminal stage, not a best-effort enhancement. If fast-perf is unavailable, still generate `report-data.json` from the trace and pass it to `generate_report.py`; only the Quick Diagnosis Overview should be hidden. If trace-derived metric extraction fails completely, continue with `--report-data` omitted and accept explicit empty metric states. If summary parsing, topic resolution, template validation, or output replacement fails, record the exact failure in the final response and do not claim the analysis is complete; the session status is `completed_with_artifact_failure` until `report.html` is successfully validated.

`--report-data` is optional only for environments where metric extraction is unavailable. In that degraded mode the report must show empty metric/chart states. It must never inherit numbers, topics, evidence, or recommendations from the HTML template.

**Required inputs**
| Input | Source | Required |
|---|---|---|
| `--yaml` | Either `session-output-<timestamp>/final-summary.md` or a YAML file containing `analysis_topics` array (one entry per topic) / `analysis_report` | Yes |
| `--report-data` | `session-output-<timestamp>/performance-data/report-data.json` (from `query_report_data.py`) | Optional only when metric extraction is unavailable; omission produces explicit empty metric states |
| `--template` | `templates/pico-perf-report-template.html` | Defaults to this path |
| `--out` | Output path | Defaults to `<session-output-dir>/report.html` |

**What the report contains**
- Header: app package, app name, analysis time, trace file
- Quick Diagnosis Overview: FPS trend, CPU/GPU trend (from `report-data.json` when `fast-perf.json` was provided; hidden when absent)
- Data Overview: App frame buckets, SPR frame types, SPR CPU/GPU stage distribution (from `report-data.json`)
- Findings: free-form findings section
- Analysis Report Body: per-topic tab panels, each containing 6 sections (Symptom / Evidence / Investigation / Root Cause / Actions / Limitations)
- Limitations & Next Steps

**Command**
```bash
python3 scripts/generate_report.py \
  --yaml session-output-<timestamp>/final-summary.md \
  --report-data session-output-<timestamp>/performance-data/report-data.json \
  --template templates/pico-perf-report-template.html \
  --out session-output-<timestamp>/report.html
```

## 6. Full Example: `final-summary.md`
```md
---
issue_type_key: [spatial_frame_abnormal, binder_latency, cpu_sched_latency]
activated_subprotocols: [binder, cpu_sched]
conclusion_level: candidate
root_cause: "A short Binder-latency burst on the app critical path is amplified by callee-side CPU runnable starvation, which ultimately elongates the EngineRender/APP Produce stage and triggers clustered Late Frames."
next_actions:
  - action: "Confirm Binder critical transactions on the app main/frame-driving thread and validate whether reducing synchronous service calls reduces Late Frames."
    priority: P0
    sources: ["./topic-result/output-spatial-engine.md", "./topic-result/output-binder.md"]
  - action: "Identify the top callee-side contending threads and validate scheduling policy/frequency within the same window."
    priority: P1
    sources: ["./topic-result/output-cpu-sched.md"]
  - action: "Re-collect trace with GPU counters enabled to rule out GPU/Compositor saturation in the same window."
    priority: P2
    sources: ["./topic-result/output-spatial-engine.md"]
limitations:
  - "GPU counters are not available in the current trace, so GPU/Compositor saturation cannot be fully ruled out."
  - "Binder transaction naming is partial (missing some service-side context), so the exact service dependency chain is not fully closed."
topic_outputs:
  - topic: spatial-engine
    file: "./topic-result/output-spatial-engine.md"
    conclusion_level: likely
  - topic: binder
    file: "./topic-result/output-binder.md"
    conclusion_level: candidate
  - topic: cpu_sched
    file: "./topic-result/output-cpu-sched.md"
    conclusion_level: candidate
---
# Final Summary
## A. Topic Output Index
| Topic | Output | conclusion_level | One-line root cause summary |
|------:|:-------|:-----------------|:----------------------------|
| Spatial Engine | output-spatial-engine.md | likely | EngineRender/APP Produce exceeds budget; the abnormal-frame window overlaps with thread contention signals. |
| Binder | output-binder.md | candidate | App critical thread shows synchronous Binder waiting overlapping the frame-abnormal window, but the callee-side dependency is not fully closed. |
| CPU Scheduling | output-cpu-sched.md | candidate | Callee-side runnable starvation appears in the same window and can explain increased service latency, but contenders/policy still need confirmation. |
## B. Cross-Topic Evidence-Chain Analysis
The abnormal-frame window first appears as clustered Late Frames in the Spatial Engine view (output-spatial-engine.md). Within the same window, the app critical path shows synchronous waiting that aligns with Binder transactions (output-binder.md), suggesting that service calls are entering the frame budget.

The CPU scheduling topic further shows runnable-but-not-running pressure on the suspected callee side in the same window (output-cpu-sched.md). This supports the chain: callee-side scheduling congestion → increased service response time → app-side Binder waiting → elongated APP Produce / EngineRender → Late Frames.
## C. Directions to Extend
- Memory: Trigger signal = abnormal window overlaps GC/STW or PSS climbs rapidly; Required evidence = GC timeline, heap stats, STW overlap.
- Spatial Audio: Trigger signal = stutter is accompanied by playback latency / underrun / AudioServer hotspots; Required evidence = audio tracks, AudioService hotspots, app audio lifecycle.
## D. Final Action Plan
- P0: Reduce or remove synchronous Binder calls on the frame-critical path, then validate whether Late Frames decrease (sources: Spatial Engine, Binder).
- P1: Identify top contenders and verify scheduling policy/frequency changes on the callee side within the same window (source: CPU Scheduling).
- P2: Re-collect a trace with GPU counters enabled to rule out GPU/Compositor bottlenecks (source: Spatial Engine).
```
