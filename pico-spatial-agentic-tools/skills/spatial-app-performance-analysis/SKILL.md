---
name: spatial-app-performance-analysis
description: Routing Skill for PICO OS6 performance analysis, using SKILL.md as the routing protocol layer to select reference workflows such as Spatial, Binder, Memory, or CPU scheduling based on user symptoms and evidence. Applicable to performance issues like jank, dropped frames, Late/Miss/Discard Frame, binder blocking, OOM, GC jitter, LMK, runqueue, thread scheduling anomalies, etc. on PICO OS6.
license: 'Apache-2.0'
---

# Spatial APP Performance Analysis

Analyze PICO OS6 performance issues based on evidence, rather than guessing the root cause based on symptom names alone. This Skill is a routing Skill: `SKILL.md` is responsible for workflow selection, while specific topic analysis methods are located under `references/`.

## Execution Conventions

**Important**: If the user directly provides performance data (at least including perfetto-trace) and the target app package (or the target app package can be parsed from the performance data), then `Collect Context` and `Capture Performance Data` can be skipped (this is very obvious).

1. Treat the directory containing this `SKILL.md` as the Skill root directory. All reference paths mentioned below are relative to this directory.
2. Establish one timestamped session output directory `session-output-<timestamp>/` (format `YYYYMMDD-HHMMSS`) at the start of each run, and write every artifact of that run (performance-data, topic-result, final-summary, report) under it. Different runs MUST use different directories so their products never overwrite each other; do not write into a bare `session-output/`. See the [Final Summary Contract](references/routing/final-summary-contract.md) for the directory layout.
3. If necessary data and context is not provided, execute in the mandatory order Collect Context -> Confirm Environment -> Capture Performance Data -> Analysis. If necessary data and context is provided, then enter the analysis workflow routing.
4. When this Skill runs under a plan mode, the planning phase MUST actually complete context collection and make a plan for how this analysis will run, rather than plan how to collect context, or how to collect data.
5. Select the entry topic from the observed symptom. Spatial Engine is the default entry for spatial-runtime and frame-pipeline anomalies. When the user reports App main/frame-driving thread jank, over-budget `doFrame`, UI/input latency, or App-side dropped frames, App Jank is a mandatory entry topic and must run before Binder or other causal extension topics.
6. Main protocol execution and dynamic expansion follow [Analysis Topic Routing](references/routing/analysis-topic-routing.md). Do not freeze the topic list at the beginning: the Main protocol consumes clues, loads subprotocols, merges their handoff evidence, and repeats until no executable clue remains.
7. Do not escalate keyword matches directly to root causes. It is necessary to distinguish between observed phenomena, correlation, mechanism explanation, and verified conclusions.
8. If evidence is insufficient, only output evidence gaps and request the minimum necessary data from the user; do not perform root cause analysis directly. Do not substitute static source-code reading or a "static performance checkup" for real performance evidence, and do not draw a performance conclusion from code structure alone; without a trace or performance evidence, stay in the evidence-gap state.
9. Do not load all topic documents before evidence exists. However, after each major evidence step, the coordinator MUST sweep the full topic registry and load every topic whose evidence passes the shared Activation Gate. Topic discovery is lazy, not selective: an empty lead list from the current topic is not evidence that another registered topic is inactive.
10. If the root cause is not proven, the conclusion must clearly state limitations and the evidence needed for next steps.
11. Performance analysis is a complex matter, so it does not require speed, but accuracy, stability, and completeness.
12. The fact that a slice takes the longest time does not necessarily mean it is the root cause; one must distinguish between "sustained pressure" and "the final straw."
13. Before writing Perfetto SQL or interpreting SQL results, follow [Perfetto Trace Basics](references/common/perfetto-trace-basics.md). In particular, `ts` / `dur` are trace-processor nanoseconds in the loaded session, issue windows must be derived from exact anchor rows or CTEs, and empty window results must be debugged by validating time bounds, identities, and joins before changing tools or conclusions.

## Collect Context

Skipped if Performance Data is provided, or if all context is provided directly by user.

Context collection is a mandatory step that must be actually executed before analysis, not just planned. Perform [Session Context Collection](references/common/session-context.md); see that file for complete rules. First auto-detect the detectable mandatory items yourself by running the read-only scripts (device type via `check_device.py`, APK type via `check_debuggable.py`), and ask the user only for what cannot be detected (typically the app package name). Then run the mandatory **Environment Confirmation Gate** in that file to confirm the resolved app package, device type, and APK type with the user before capturing data. Prefer the host's structured confirmation capability (for example `AskUserQuestion`) when available, and fall back to the plain-text follow-up template otherwise.

Under a plan mode, complete this entire step (detection + Environment Confirmation Gate) during the plan phase; do not defer it into a "how to collect context" plan item. In the same plan phase, also try to collect the reproduction path and user-visible symptom (Recommended, not Mandatory items that help shape the capture command and analysis entry) by presenting structured choices — for example numbered candidate scenarios `1` / `2` plus an `Other` free-text option — instead of an open-ended question. Neither the reproduction path nor the symptom is required to proceed: do not hard-block when the user is non-technical, cannot give reproduction steps, or cannot match any option. Offer an explicit "I can't describe it / you decide from the data" option, continue with capture using a default window (or data-derived candidates once data exists), and record any missing reproduction path / symptom as a limitation.

## Capture Performance Data

Skipped if Performance Data is provided directly by user.

After context collection is complete, execute [Performance Data Collection](references/common/capture-performance-data.md). Based on the results, decide whether to enter the data capture branch or the primary analysis routing. If capture is needed, run the mandatory **Capture Confirmation Gate** in that file to confirm the capture command and its parameters (app, serial, output, scope) with the user before executing it, and confirm the capture duration as its own separate step first; prefer the host's structured confirmation capability (for example `AskUserQuestion`) when available. Once data is ready, return to "Analysis Workflow Routing" below to select a topic.

Under a plan mode, the planning phase ends here by presenting the performance-data plan (the resolved capture command and parameters, or the list of existing artifacts to analyze) as the last step before execution. Do not actually run the capture command, load traces, or start topic analysis until the plan is approved.
When a trace exists but the identities of the target App, Spatial Runtime, OpenXR Runtime, compositor, or frame driving threads are not yet solidified, first execute `spatial_probe.py --detail --output session-output-<timestamp>/performance-data/trace-probe-detail.yaml` according to the [PICO CLI Perf User Guide](references/common/tools.md), using the compatibility entry `probe_identities()` to generate `trace-probe-detail.yaml`. This entry internally schedules `probe_app_identity()` and `probe_spatial_runtime_identity()`.
When users need to capture traces, load traces, query diagnostic tables, export reports, or perform live performance inspections, use the [PICO CLI Perf User Guide](references/common/tools.md).

## Analyze Performance Problem

- Incomplete session context, missing app package name, device type, or APK type: Use [Session Context Collection](references/common/session-context.md).
- When the user has not specified performance data Trace, do not use any local files or data without authorization. Use [Performance Data Collection](references/common/capture-performance-data.md) for capture.

### Entry Topic Selection

Use [Analysis Topic Routing](references/routing/analysis-topic-routing.md) to select the entry topic from the observed symptom. Spatial Engine is the entry topic for spatial-runtime or frame-pipeline anomalies. The entry topic is an analysis starting point, not a root-cause priority.

### Sub-Protocols

Sub-protocols dynamically trigger loading when relevant clues are found during the analysis of other protocols. There is no fixed priority between sub-protocols; sub-protocols are not mutually exclusive, but complementary; multi-clue parallelism is supported, as well as chain extensions, such as tracing from Binder waiting to CPU scheduling, and then to memory reclamation pressure.

- `activated sub-protocols`: The sub-protocol that has been hit and must be executed this round.
- `detected leads`: The list of clues that have been hit by the current trace will be recorded as long as the evidence in the window exists.
- `executed topics`: The output of the topic actually executed in the current round.
- `root_cause_priority`: It is only the priority sorting in the final summary and does not affect whether the topic is executed.

Current list of sub-protocols:

- [IPC/Binder Analysis Workflow](references/analysis-topic/analysis-binder.md)
- [Memory Analysis Workflow](references/analysis-topic/analysis-memory.md)
- [CPU Scheduling Analysis Workflow](references/analysis-topic/analysis-cpu-scheduling.md)
- [Spatial Audio Performance Analysis Workflow](references/analysis-topic/analysis-spatial-audio.md)
- [Kotlin Spatial App Jank Analysis Workflow](references/analysis-topic/analysis-kotlin-spatial-app-jank.md)

When multiple clues appear simultaneously, or when topics need to be activated and expanded during analysis, use [Analysis Topic Routing](references/routing/analysis-topic-routing.md).

### Mandatory Execution Rules After Routing

Main protocol routing is not the final analysis result. Add only the currently executable subprotocol to the execution queue, then enter its document. After every subprotocol completes, return its `controller_handoff` to [Analysis Topic Routing](references/routing/analysis-topic-routing.md). The Main protocol re-evaluates the Activation Gate and appends newly activated subprotocols. Do not output a fixed topic list and treat it as final.

The execution order is as follows:

1. Complete the normative [PICO Spatial PerformanceKB Mandatory Gate](references/common/knowledge-base-usage.md) before relying on KB guidance or finalizing a root-cause conclusion. KB retrieval remains assistive: never treat it as proof of the current root cause.
2. Execute the currently selected subprotocol according to its subprotocol contract, including availability checks, evidence sequence, closure assessment, controller handoff, and output requirements. For an App-side jank entry, execute `analysis-kotlin-spatial-app-jank.md` before any Binder, Memory, or CPU Scheduling extension.
3. Return the subprotocol's `controller_handoff` to the Main protocol before selecting the next queue item. Newly activated subprotocols are appended dynamically; they are not required to be known before the first subprotocol runs.
4. For directions to be extended, do not stop at the name list. You must clearly write the trigger signal, missing evidence, and which subprotocol the Main protocol should execute next or what data needs to be supplemented.
5. After each subprotocol is executed, consume its `controller_handoff` and run the full registry sweep in Analysis Topic Routing. If a new subprotocol passes the shared Activation Gate, the Main protocol adds it to the pending execution queue and continues until no new executable subprotocols remain.
6. Do not downgrade an evidence-backed clue into `next_actions`, "directions to be extended", or "next validation". Those buckets are only for clues whose required evidence is genuinely missing; using them to defer work that the current trace already supports is a prohibited shortcut.
7. For any activated chain, strong evidence on one side (for example the Binder caller side) does not complete that sub-protocol while the other side (the callee/server side) is still resolvable from the same trace.
8. Route by relevance, not by keyword presence. When several clues (Binder, GC/memory, runnable/CPU, main-thread, audio, or spatial frame pipeline) coexist, the Main protocol loads every subprotocol whose temporal overlap and dependency evidence pass the shared gate. Budget share and current root-cause ranking must not suppress an executable subprotocol.
9. Final conclusions can only be output after all selected topics have completed analysis. If a topic cannot be executed due to insufficient evidence, clearly mark the reason why that topic was not executed and the minimum evidence requirements in the conclusion.
10. Before finalization, perform the mandatory completion barrier in `final-summary-contract.md`: stage supplied inputs, close the routing ledger, execute every topic that passed the gate, write the summary and classification, then generate and validate `report.html`. A missing report or missing staged input is an artifact failure, not a reason to silently finish with Markdown/YAML only.

## Output Conventions

If only performing routing judgment and no topic has been executed yet, output:

```text
1. Primary Protocol
2. Activated Sub-protocols
3. Directions to be Extended
4. Judgment Basis
5. Missing Evidence
6. Next Actions
```

If at least one topic has been executed, every topic result MUST follow the unified contract in [Output Contract](references/routing/output-contract.md):

- Always emit a YAML header first, filling the required fields such as `issue_type_key`, `protocol`, `activated_subprotocols`, `target`, `evidence`, `conclusion_level`, `root_cause`, `next_actions`, and `limitations`.
- Then emit the fixed 6 human-readable sections defined in the same contract.
- Do not output only the 6 prose sections without the YAML header, because cross-topic aggregation depends on the machine-readable fields.

The required 6 body sections are:

```text
1. Symptom
2. Existing Evidence
3. Investigation Process
4. Root Cause Judgment
5. Actions (Optimization / Troubleshooting)
6. Limitations and Next Validation
```

For multi-topic sessions:

- Write one topic file per executed topic under `session-output-<timestamp>/topic-result/output-<topic>.md`, and each topic file MUST also follow the unified output contract above.
- Also produce `session-output-<timestamp>/final-summary.md` per [Final Summary Contract](references/routing/final-summary-contract.md). This summary keeps a YAML header plus Markdown body and is the canonical cross-topic aggregation artifact.
- As the final step, after `final-summary.md` exists, distill the topic outputs into `root-cause-classification.yaml` using the chain `abnormal window → critical path → budget owner → mechanism → evidence refs → category`; choose the most specific category only after the chain is proven, and use a conservative category or `undetermined` when it is not. Do not map Binder waits to service contention without server-side contention evidence, or scene-complexity counters to GPU without same-window GPU execution evidence. Keep this machine-checkable artifact separate from per-topic headers and `final-summary.md`; it is orthogonal to `issue_type_key`. See [Root Cause Classification Contract](references/routing/root-cause-classification-contract.md).
- When generating `report.html`, pass `session-output-<timestamp>/final-summary.md` to `generate_report.py`; the script is responsible for extracting the YAML header and body, then loading the referenced topic outputs. The exact data each report section requires is defined in the [HTML Report Data Contract](references/routing/report-data-contract.md); fields without a real source stay blank rather than being filled with placeholder data.

## Compatibility

This Skill operates primarily as a Markdown-driven routing Skill. Scripts under `scripts/` are provided as optional helpers for data capture, identity probing, report data querying, and report generation; they are not required for pure trace/SQL evidence analysis. No cloud services are required. For PICO Spatial performance diagnosis, an exposed `pico-spatial-knowledge` MCP or configured PerformanceKB is governed by the mandatory gate above; when no such backend is available, follow the explicit unavailable-backend fallback and record the limitation. When users provide Perfetto traces, SQL results, or screenshots, analyze existing evidence according to the selected reference workflow.
