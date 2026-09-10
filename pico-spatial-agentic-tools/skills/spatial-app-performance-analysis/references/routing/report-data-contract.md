# HTML Report Data Contract

This document is the single source of truth for the data that the HTML report consumes. It exists because the report has three independent producers/consumers that must agree on the same field shapes:

1. `query_report_data.py` -> `report-data.json` (trace/fast-perf derived metrics)
2. `final-summary.md` + `topic-result/output-*.md` (agent-authored analysis)
3. `generate_report.py` -> injects both of the above into `reportData` inside `templates/pico-perf-report-template.html`

The template renders **only** the `reportData` object described in section 2. Any field the template renders MUST be listed here with a defined source and a defined missing-value behavior, so the report never falls back to mock data.

## 0. Core Rules

- **No mock data in a real report.** Every rendered field is either filled from a real source or explicitly blanked. When a field cannot be derived, it is set to an empty value and the template shows an empty-state placeholder — never a fabricated number, slice, or evidence string.
- **The template `reportData` literal ships as an empty skeleton.** It defines structure only (empty strings / arrays / zeros). `generate_report.py` constructs the complete object and replaces the entire literal in one operation; it must not depend on template defaults or merge partial data into example content.
- **HTML generation is transactional.** The generator validates the summary/topic references and the rendered topic names before atomically replacing `report.html`; a failed validation must not leave a new or partially written report.
- **Field names are fixed.** The template consumes the exact keys below. Producers must emit these keys verbatim (note: the template uses `snake_case` inside `details`, and `camelCase` elsewhere — see each field).
- **Adding a rendered field requires updating this contract**, the template, and `generate_report.py` together.

## 1. Data Sources

| Source | Produced by | Feeds |
|---|---|---|
| `report-data.json` | `query_report_data.py` | `quickDiagnosis.*`, `details.*` (buckets/stats/frame durations), `findings.frameSummary` |
| `final-summary.md` front-matter | agent (per [Final Summary Contract](final-summary-contract.md)) | `header.*`, `findings.rootCause`, `recommendations.*`, `header.activeProtocols` |
| `topic-result/output-*.md` | agent (per [Output Contract](output-contract.md)) | `analysisTopics[]`, `findings.evidence` |
| none (blanked) | — | `header.deviceModel/osVersion`; all metric fields are empty when `--report-data` is omitted |

## 2. `reportData` Schema (template consumes this)

### 2.1 `header` (object)

| Field | Type | Source | Required | Missing behavior |
|---|---|---|---|---|
| `appPackage` | string | final-summary `header.app_package` | Yes | empty -> PKG chip hidden |
| `appName` | string | final-summary `header.app_name` | Yes | falls back to a neutral title |
| `analysisTime` | string | final-summary `header.analysis_time` | Recommended | empty -> TIME chip hidden |
| `traceFileName` | string | final-summary `header.trace_file` | Recommended | empty -> TRACE chip hidden |
| `deviceModel` | string | final-summary `header.device_model` | Optional | empty -> DEVICE/OS chip hidden |
| `osVersion` | string | final-summary `header.os_version` | Optional | empty -> DEVICE/OS chip hidden |
| `summary` | string | final-summary `header.summary` | Recommended | empty -> summary line blank |
| `activeProtocols` | string[] | final-summary `activated_subprotocols` | Recommended | empty -> no protocol badges |

### 2.2 `quickDiagnosis` (object)

| Field | Type | Source | Required | Missing behavior |
|---|---|---|---|---|
| `timeline` | string[] | `report-data.json.fps_trend[].time` (or `cpu_gpu_trend[].time`) | Yes only when fast-perf is available | empty -> Quick Diagnosis Overview hidden |
| `appFps` | number[] | `fps_trend[].app_fps` | Yes only when fast-perf is available | empty -> Quick Diagnosis Overview hidden |
| `sprFps` | number[] | `fps_trend[].spr_fps` | Yes only when fast-perf is available | empty -> Quick Diagnosis Overview hidden |
| `fps` | number[] | alias of `appFps` (back-compat) | Optional | — |
| `cpuLoad` | number[] | alias of `systemCpuLoad` when available, else `appCpuLoad` (back-compat) | Optional | — |
| `appCpuLoad` | number[] | `cpu_gpu_trend[].app_cpu` | Recommended when fast-perf is available | empty -> Quick Diagnosis Overview hidden when no other quick data exists |
| `systemCpuLoad` | number[] | `cpu_gpu_trend[].system_cpu` | Recommended when fast-perf is available | empty -> Quick Diagnosis Overview hidden when no other quick data exists |
| `gpuLoad` | number[] | `cpu_gpu_trend[].gpu_usage` | Recommended when fast-perf is available | empty -> Quick Diagnosis Overview hidden when no other quick data exists |
| `gpuFreq` | number[] | `cpu_gpu_trend[].gpu_freq` | Recommended when fast-perf is available | empty -> GPU frequency trend line omitted |
| `gpuTemp` | number[] | `cpu_gpu_trend[].gpu_temp` | Recommended when fast-perf is available | empty -> no temperature trend rendered |
| `metrics` | object[] | derived from series (see below) | Recommended when fast-perf is available | empty -> Quick Diagnosis Overview hidden when no other quick data exists |

`metrics[]` item: `{ key, label, value:number, unit:string, status:"normal"|"warning"|"abnormal", description:string }`. Derived by `generate_report.py` from `fast_perf_summary` when available, otherwise from the time series. The Quick Diagnosis Overview must expose the original seven fast-perf indicators when present, with these labels: APP FPS, SPR FPS, APP CPU Load, SPR CPU Load, SPR GPU Load, GPU Freq, and GPU Temp. `SPR CPU Load` uses warning >= 90 and abnormal >= 150; other `status` thresholds are defined in the script.

### 2.3 `findings` (object)

| Field | Type | Source | Required | Missing behavior |
|---|---|---|---|---|
| `frameSummary` | `{late,miss,discard}` numbers | `report-data.json.spr_frame_types` | Recommended | zeros |
| `evidence` | object[] | topics' `evidence` list | Recommended | empty -> "（无结构化证据条目）" |
| `rootCause` | `{description, confidence}` | final-summary `root_cause` + `conclusion_level` | Recommended | empty strings |

`evidence[]` item: `{ type:string, window:string, description:string }`. Mapped from each topic's YAML `evidence[]` as `type<-topic, window<-location, description<-one_line_finding`. `rootCause.confidence` maps `conclusion_level`: `confirmed->高`; all lower-confidence or unknown levels -> `一般`.

### 2.4 `details` (object — note: `snake_case` keys)

| Field | Type | Source | Required | Missing behavior |
|---|---|---|---|---|
| `frameBudgetMs` | number | template constant (11.11) | fixed | — |
| `app_frame_buckets` | object | `report-data.json` | Recommended | empty chart |
| `spr_frame_buckets` | object | `report-data.json` | Recommended | empty chart |
| `spr_frame_types` | object | `report-data.json` | Recommended | empty chart |
| `spr_cpu_buckets` | object | `report-data.json` | Recommended | empty chart |
| `spr_gpu_buckets` | object | `report-data.json` | Recommended | empty chart |
| `spr_stats` | object | `report-data.json` | Recommended | stat cards show 0 |
| `frameDurations` | number[] | `report-data.json.app_frame_durations_ms` | Recommended | `[]` -> per-frame chart skipped |
| `render_load_counter_groups` | object[] | `report-data.json.render_load_counter_groups` | Recommended | render-load sub-tabs show empty-state panels |
| `mesh_draw_call_count_series` | object[] | `report-data.json.mesh_draw_call_count_series` | Optional back-compat alias | used only when `render_load_counter_groups` is absent |
| `mesh_draw_call_count_stats` | object | `report-data.json.mesh_draw_call_count_stats` | Optional back-compat alias | used only when `render_load_counter_groups` is absent |

Bucket key orders are fixed by the template: app `["200ms+","100~200ms","33~100ms","22~33ms","11~22ms","<11ms"]`, spr frame `["33~50ms","22~33ms","11~22ms","<11ms"]`, stage `[">16ms","12~16ms","8~12ms","4~8ms","<4ms"]`, frame type `["Normal","Late","Miss","Early","Discard"]`.

`render_load_counter_groups[]` item:

```jsonc
{
  "id": "3d-render",
  "label": "3D Render",
  "process_name": "com.pico.spatial.runtime",
  "unit_label": "count",
  "counters": [
    {
      "name": "3D Mesh Draw Call Count",
      "process_name": "com.pico.spatial.runtime",
      "unit_label": "count",
      "series": [ { "ts_ns": "0", "ts_ms": 0, "time_s": 0, "value": 0 } ],
      "stats": { "count": 0, "avg": null, "max": null, "min": null, "first_ts_ns": "", "last_ts_ns": "", "process_name": "com.pico.spatial.runtime", "counter_name": "3D Mesh Draw Call Count" }
    }
  ]
}
```

The report renders each group as a sub-tab under Data Overview -> Render Loads. The default group configuration is read from `../render-load-counters.json` by `query_report_data.py`; adding a counter should normally be done by editing that JSON file rather than touching the HTML template.

Default groups:

- `3D Render`: `Draw Call Count`, `3D Mesh Draw Call Count`, `Particle Draw Call Count`, `Shadow Draw Call Count`, `Triangle Count`, `3D Mesh Triangle Count`, `Particle Triangle Count`, `Shadow Triangle Count`, `Vertex Count`, `3D Mesh Vertex Count`, `Particle Vertex Count`, `Shadow Vertex Count`
- `Memory`: `Texture2D Memory`, `Mesh Memory`, `Scene Graph Memory`

Each counter `series[]` item is `{ ts_ns:string, ts_ms:number|null, time_s:number|null, value:number|null }`. `ts_ns` is a string to preserve Perfetto nanosecond timestamp precision through JSON consumers. `time_s` is relative to the first sample of that specific counter. The template may downsample each series for rendering, but `stats` always describes the full event series.

`mesh_draw_call_count_series[]` item: same shape as a counter `series[]` item. It is retained only for compatibility with older report consumers.

`mesh_draw_call_count_stats`: `{ count:number, avg:number|null, max:number|null, min:number|null, first_ts_ns:string, last_ts_ns:string, process_name:string, counter_name:string }`.

### 2.5 `recommendations` (object)

| Field | Type | Source | Required | Missing behavior |
|---|---|---|---|---|
| `limitations` | string[] | final-summary `limitations` | Recommended | empty list |
| `nextSteps` | string[] | final-summary `next_actions` | Recommended | empty list |

### 2.6 `analysisTopics` (array — the report body)

Each item MUST be:

```jsonc
{
  "topic": "app_jank",              // from topic protocol
  "conclusion_level": "likely",
  "report": {
    "symptom": "string",
    "existing_evidence": [ { "type": "", "finding": "" } ],
    "investigation_process": "string",
    "root_cause_judgment": { "one_line": "", "conclusion_level": "", "reasoning": "" },
    "actions": [ "string" ],
    "limitations_and_next_validation": "string"
  }
}
```

The template filters `analysisTopics.filter(t => t && t.report)`; a topic without a `report` object is silently dropped, so `report` and its keys are mandatory. `generate_report.py` builds these from each `topic-result/output-*.md` (YAML header + the 6 body sections). Body section titles are matched tolerantly (circled `①` or arabic `1.`), per [Output Contract](output-contract.md).

**Fallback:** when a summary omits `topic_outputs` entirely, `generate_report.py` emits a single `analysisReport` object (built from the summary's `A./B./C./D.` sections) instead of `analysisTopics`. An explicitly present but empty `topic_outputs` is invalid, because it usually means the controller finalized before executing discovered topics. The template renders `analysisReport` only when `analysisTopics` is empty. Prefer the per-topic path; `analysisReport` is the degraded single-panel view.

### 2.7 `footer` (object)

| Field | Type | Source | Missing behavior |
|---|---|---|---|
| `generatedBy` | string | template constant | — |
| `protocolVersion` | string | template constant | — |

## 3. `report-data.json` JSON Schema (`query_report_data.py` output)

This is the machine contract for the capture-derived half. Field names are `snake_case` here and remapped into `reportData` by `generate_report.py`.

```jsonc
{
  "meta": {
    "trace_path": "string",
    "fast_perf_path": "string|null",
    "generated_at": "ISO-8601",
    "app_package": "com.example.app",
    "render_load_counter_config": "../render-load-counters.json"
  },
  "app_frame_buckets": { "200ms+": 0, "100~200ms": 0, "33~100ms": 0, "22~33ms": 0, "11~22ms": 0, "<11ms": 0 },
  "app_frame_durations_ms": [11.12, 16.67, 32.5],
  "spr_frame_buckets": { "33~50ms": 0, "22~33ms": 0, "11~22ms": 0, "<11ms": 0 },
  "spr_frame_types":   { "Normal": 0, "Late": 0, "Miss": 0, "Early": 0, "Discard": 0 },
  "spr_cpu_buckets":   { ">16ms": 0, "12~16ms": 0, "8~12ms": 0, "4~8ms": 0, "<4ms": 0 },
  "spr_gpu_buckets":   { ">16ms": 0, "12~16ms": 0, "8~12ms": 0, "4~8ms": 0, "<4ms": 0 },
  "spr_stats": { "total_frames": 0, "avg_frame_ms": 0, "avg_cpu_ms": 0, "avg_gpu_ms": 0, "min_frame_ms": 0, "max_frame_ms": 0 },
  "render_load_counter_groups": [
    {
      "id": "3d-render",
      "label": "3D Render",
      "process_name": "com.pico.spatial.runtime",
      "unit_label": "count",
      "counters": [
        {
          "name": "Draw Call Count",
          "process_name": "com.pico.spatial.runtime",
          "unit_label": "count",
          "series": [ { "ts_ns": "0", "ts_ms": 0, "time_s": 0, "value": 0 } ],
          "stats": { "count": 0, "avg": null, "max": null, "min": null, "first_ts_ns": "", "last_ts_ns": "", "process_name": "com.pico.spatial.runtime", "counter_name": "Draw Call Count" }
        }
      ]
    },
    {
      "id": "memory",
      "label": "Memory",
      "process_name": "com.pico.spatial.runtime",
      "unit_label": "bytes",
      "counters": []
    }
  ],
  "mesh_draw_call_count_series": [ { "ts_ns": "0", "ts_ms": 0, "time_s": 0, "value": 0 } ],
  "mesh_draw_call_count_stats": { "count": 0, "avg": null, "max": null, "min": null, "first_ts_ns": "", "last_ts_ns": "", "process_name": "com.pico.spatial.runtime", "counter_name": "3D Mesh Draw Call Count" },
  "fast_perf_summary": {
    "appFps": { "avg": 0, "max": 0, "min": 0 },
    "sysFps": { "avg": 0, "max": 0, "min": 0 },
    "gpuUsage": { "avg": 0, "max": 0 },
    "gpuFreq": { "avg": 0, "max": 0 },
    "systemCpu": { "avg": 0, "max": 0 },
    "appCpu": { "avg": 0, "max": 0 },
    "gpuTemp": { "start": 0, "end": 0, "max": 0 }
  },
  "fps_trend":     [ { "time": "0s", "app_fps": 0, "spr_fps": 0 } ],
  "cpu_gpu_trend": [ { "time": "0s", "app_cpu": 0, "system_cpu": 0, "gpu_usage": 0, "gpu_freq": 0, "gpu_temp": 0 } ]
}
```

All numeric fields may be `null` when a sample is missing; the report treats `null` as "no data" for that point, never as `0`-with-meaning. When `fast_perf_path` is `null`, `fps_trend` and `cpu_gpu_trend` are empty, the HTML report hides Quick Diagnosis Overview, and trace-derived `details` still populate Data Overview.

## 4. Producer Checklist

Before generating a report, confirm:

- `final-summary.md` front-matter has `header` (at least `app_package`), `root_cause`, `conclusion_level`, `limitations`, `next_actions`, `activated_subprotocols`, and `topic_outputs[]`.
- Each `topic_outputs[].file` exists and follows the [Output Contract](output-contract.md).
- Run `query_report_data.py` first and pass its `report-data.json` whenever trace SQL extraction succeeds. This script consumes the diagnostic tables produced by `pico-cli perf trace load --spatial-diagnose true`; it must not recreate Spatial diagnostic tables itself. If `fast-perf.json` is unavailable, still pass the trace-derived `report-data.json`; only Quick Diagnosis Overview is hidden.
- Invoke `generate_report.py` only after the Main protocol has completed its topic loop and finalized `final-summary.md`; do not generate HTML while topic outputs are still being added.
- After generation, verify that `report.html` contains every executed topic name and that the output is non-empty. A generation error is a failed artifact, not a reason to keep a stale previous report.
- `report-data.json`, when provided, matches section 3.
- Fields with no real source stay blank; do not hand-fill them with plausible numbers to "make the report look complete".
