# Final Summary Output Contract

Final summary only aggregates topic outputs by reference and adds the cross-topic evidence chain; do not duplicate per-topic analysis content.

A run's final summary is split into two sibling files in the session root:

- `final-summary.md` — the **human-readable** body with sections A/B/C/D.
- `final-summary.meta.json` — the **machine-readable** sidecar; the authoritative source for all structured fields.

The `.md` is pure Markdown (no YAML / no front matter). Everything machine-readable lives in the sidecar JSON.

## 1. File Naming
- Body: `final-summary.md`
- Sidecar: `final-summary.meta.json`
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
│   ├── simple-perf.data               # optional
│   ├── collector-summary.json         # produced by capture_perf_data.py
│   ├── trace-probe.json               # produced by spatial_probe.py
│   ├── trace-probe-detail.json        # produced by spatial_probe.py --detail
│   └── report-data.json
├── topic-result/
│   ├── output-<topic>.md              # human-readable body (6 sections)
│   └── output-<topic>.meta.json       # machine-readable sidecar
├── final-summary.md
├── final-summary.meta.json
├── root-cause-classification.json     # standalone final artifact
└── report.html
```

Rules:
- Create the session directory as the very first side effect of a run. Only one timestamped root may exist per run.
- Prefer writing capture tool outputs into `performance-data/<timestamped-dir>/` under this root (`capture_perf_data.py` uses that layout) and keep paths relative to the session root in every downstream reference.
- When documenting file paths in `references/`, examples, or user-facing output, always include the `session-output-<timestamp>/` prefix. Do not use the legacy `session-output/` without a timestamp.
- Downstream tools (`generate_report.py`, final summary, HTML report) MUST resolve inputs from the same session root to prevent cross-run contamination.
- Topic sidecar files and final summary sidecar files MUST be real files written to disk. `generate_report.py` reads them from the session directory, not from the conversation.

## 3. Topic Analysis Outputs

For every topic (`spatial-engine`, `binder`, `memory`, `cpu_sched`, `spatial-audio`, `kotlin-spatial-app-jank`, ...) actually executed by the Main protocol, you MUST produce **two sibling files**:

- `topic-result/output-<topic>.md` — human-readable body with the fixed 6 sections.
- `topic-result/output-<topic>.meta.json` — machine-readable sidecar (schema in [output-contract.md](output-contract.md)).

Both files MUST be real files on disk, both MUST have the same basename, and both MUST live in `topic-result/`. Downstream tooling (final summary, HTML report, root-cause classification) consumes the `.meta.json` for structured fields and references the `.md` for narrative display.

## 4. `final-summary.meta.json` (Machine-Readable Sidecar)

The sidecar JSON is the single source of truth for machine fields; `final-summary.md` must not duplicate them.

### 4.1 Required fields

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | Current contract version (`"1.0"`). |
| `header` | object | Report header fields that `generate_report.py` injects into the HTML template. See 4.2. |
| `issue_type_key` | string[] | Union of `issue_type_key` across activated topics (see [output-contract.md](output-contract.md) §1.1). |
| `activated_subprotocols` | string[] | List of subprotocols actually executed. |
| `conclusion_level` | string | Aggregate conclusion level across all activated topics. |
| `root_cause` | string | One-line cross-topic root cause summary. |
| `next_actions` | object[] | Each item `{ "action": string, "priority": "P0"|"P1"|"P2", "sources": string[] }`. `sources` MUST point to topic sidecar paths (`.meta.json`), not `.md`. |
| `limitations` | string[] | Cross-topic limitations and missing evidence. |
| `topic_outputs` | object[] | Each item `{ "topic": string, "conclusion_level": string, "file": "./topic-result/output-<topic>.meta.json" }`. `file` is the machine-readable topic sidecar consumed by `generate_report.py`; the body `.md` is resolved from the topic sidecar's `sections_file` or by replacing `.meta.json` with `.md`. |
| `routing_registry` | object[] | Each item `{ "topic": string, "status": "activated"|"not_activated"|"deferred", "evidence": string }`. |
| `sections_file` | string | Relative path to the body `.md`, usually `"final-summary.md"`. This is the field consumed by `generate_report.py`. |
| `summary_sections_in_body` | object | Map of section id → the exact Markdown heading used in the `.md` body. Downstream tools match headings verbatim. |

### 4.2 `header` sub-schema

```json
{
  "app_package": "com.example.spatial.app",
  "app_name": "Example Spatial App",
  "analysis_time": "2026-07-31 14:03:12 CST",
  "app_type": "no_debug",
  "device_type": "real",
  "device_model": "PICO 4 Ultra",
  "os_version": "6.1.0",
  "trace_file": "trace-perf.perfetto-trace",
  "fast_perf_file": "fast-perf.json",
  "simple_perf_file": "",
  "summary": "One-line report summary shown in the top banner."
}
```

`generate_report.py` reads these fields directly from `header.*`. Do not nest report-banner fields under `header.context` or `header.analysis_data`, otherwise the generated HTML banner will miss values such as `trace_file`, `device_model`, and `os_version`.

A full sidecar example lives at [`templates/final_summary_meta_example.json`](../../templates/final_summary_meta_example.json).

### 4.3 Cross-file reference rules

- **Machine-to-machine references** (`next_actions[].sources`, `topic_outputs[].file`) → always point to `.meta.json`.
- **Human / HTML display references** (topic sidecar `sections_file`, prose in `final-summary.md`) → point to `.md`.

## 5. `final-summary.md` Body (Human-Readable)

The body contains four fixed sections. Every section heading MUST match the value declared in `summary_sections_in_body` of the sidecar JSON. Downstream renderers match headings verbatim.

| Section id | Default heading | Content |
|---|---|---|
| `topic_index` | `A. Topic Output Index` | A compact table that lists each topic actually executed, its output file name (link to `.md`), its `conclusion_level`, and a one-line root-cause summary. |
| `evidence_chain` | `B. Cross-Topic Evidence-Chain Analysis` | A short narrative that connects the symptom window, the activated topic conclusions, and the shared evidence. Reference topic `.md` files by name; do not restate per-topic analysis bodies. |
| `directions` | `C. Directions to Extend` | For every topic not activated this run (and listed in `routing_registry`), state the trigger signals and the evidence that would need to be collected to re-open it. |
| `final_plan` | `D. Final Action Plan` | Dedup and consolidate `next_actions` from all topic sidecars, keeping priorities and source links to `.md` files. |

Length target: ≤ ~1 page in the browser (A + B compact; C short; D flat priority list).

## 6. HTML Report (`report.html`)

HTML generation is a required terminal stage of every analysis run; it is produced by [`generate_report.py`](../../scripts/generate_report.py) from the structured topic outputs. Treat it as a hard output requirement with the same priority as `final-summary.md` itself.

The Main protocol MUST complete the dynamic topic loop, write every executed topic output (both `.md` and `.meta.json`), perform the closure check, and write `final-summary.md` + `final-summary.meta.json` before invoking the HTML generator. The generator then resolves every `topic_outputs[].file`, builds a complete report data object, validates the rendered topic set, and atomically replaces `report.html`. If any reference, schema, template marker, or post-generation validation fails, treat HTML generation as failed and do not use a stale or partially written report.

HTML generation is a required terminal stage, not a best-effort enhancement. If fast-perf is unavailable, still generate `report-data.json` from the trace and pass it to `generate_report.py`; only the Quick Diagnosis Overview should be hidden. If trace-derived metric extraction fails completely, continue with `--report-data` omitted and accept explicit empty metric states. If summary parsing, topic resolution, template validation, or output replacement fails, record the exact failure in the final response and do not claim the analysis is complete; the session status is `completed_with_artifact_failure` until `report.html` is successfully validated.

`--report-data` is optional only for environments where metric extraction is unavailable. In that degraded mode the report must show empty metric/chart states. It must never inherit numbers, topics, evidence, or recommendations from the HTML template.

**Required inputs**
| Input | Source | Required |
|---|---|---|
| `--input` | Either `session-output-<timestamp>/final-summary.meta.json` **or** a bundled `analysis-output.json` file containing a top-level `analysis_topics` array (see [`templates/analysis_output_example.json`](../../templates/analysis_output_example.json)) | Yes |
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
  --input session-output-<timestamp>/final-summary.meta.json \
  --report-data session-output-<timestamp>/performance-data/report-data.json \
  --template templates/pico-perf-report-template.html \
  --out session-output-<timestamp>/report.html
```

## 7. Full Example

### 7.1 `final-summary.meta.json`

```json
{
  "schema_version": "1.0",
  "header": {
    "app_package": "com.example.spatial.app",
    "app_name": "Example Spatial App",
    "analysis_time": "2026-07-31 14:03:12 CST",
    "app_type": "no_debug",
    "device_type": "real",
    "device_model": "PICO 4 Ultra",
    "os_version": "6.1.0",
    "trace_file": "trace-perf.perfetto-trace",
    "fast_perf_file": "fast-perf.json",
    "simple_perf_file": "",
    "summary": "A short report summary shown in the top banner."
  },
  "issue_type_key": ["spatial_frame_abnormal", "binder_latency", "cpu_sched_latency"],
  "activated_subprotocols": ["spatial-engine", "binder", "cpu_sched"],
  "conclusion_level": "candidate",
  "root_cause": "A short Binder-latency burst on the app critical path is amplified by callee-side CPU runnable starvation, which ultimately elongates the EngineRender/APP Produce stage and triggers clustered Late Frames.",
  "next_actions": [
    { "action": "Confirm Binder critical transactions on the app main/frame-driving thread and validate whether reducing synchronous service calls reduces Late Frames.",
      "priority": "P0",
      "sources": ["./topic-result/output-spatial-engine.meta.json", "./topic-result/output-binder.meta.json"] },
    { "action": "Identify the top callee-side contending threads and validate scheduling policy/frequency within the same window.",
      "priority": "P1",
      "sources": ["./topic-result/output-cpu-sched.meta.json"] },
    { "action": "Re-collect trace with GPU counters enabled to rule out GPU/Compositor saturation in the same window.",
      "priority": "P2",
      "sources": ["./topic-result/output-spatial-engine.meta.json"] }
  ],
  "limitations": [
    "GPU counters are not available in the current trace, so GPU/Compositor saturation cannot be fully ruled out.",
    "Binder transaction naming is partial (missing some service-side context), so the exact service dependency chain is not fully closed."
  ],
  "topic_outputs": [
    { "topic": "spatial-engine", "conclusion_level": "likely",
      "file": "./topic-result/output-spatial-engine.meta.json" },
    { "topic": "binder", "conclusion_level": "candidate",
      "file": "./topic-result/output-binder.meta.json" },
    { "topic": "cpu_sched", "conclusion_level": "candidate",
      "file": "./topic-result/output-cpu-sched.meta.json" }
  ],
  "routing_registry": [
    { "topic": "memory", "status": "not_activated", "evidence": "No OOM / GC storm signature observed in the issue window." },
    { "topic": "spatial-audio", "status": "not_activated", "evidence": "No audio IPC storm observed." }
  ],
  "sections_file": "final-summary.md",
  "summary_sections_in_body": {
    "topic_index": "A. Topic Output Index",
    "evidence_chain": "B. Cross-Topic Evidence-Chain Analysis",
    "directions": "C. Directions to Extend",
    "final_plan": "D. Final Action Plan"
  }
}
```

### 7.2 `final-summary.md`

```md
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
- P0: Reduce or remove synchronous Binder calls on the frame-critical path, then validate whether Late Frames decrease (sources: output-spatial-engine.md, output-binder.md).
- P1: Identify top contenders and verify scheduling policy/frequency changes on the callee side within the same window (source: output-cpu-sched.md).
- P2: Re-collect a trace with GPU counters enabled to rule out GPU/Compositor bottlenecks (source: output-spatial-engine.md).
```
