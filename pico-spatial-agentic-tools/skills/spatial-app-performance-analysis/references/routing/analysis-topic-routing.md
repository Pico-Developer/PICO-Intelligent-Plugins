# Analysis Topic Routing (Main Protocol)

This document is the Main protocol for the performance analysis workflow. It owns the analysis loop, clue management, Activation Gate, subprotocol selection, and completion decision. Individual `references/analysis-topic/analysis-*.md` files are subprotocols and own only topic-specific analysis.

## Routing State

Maintain these states throughout the run:

- `abnormal_window`: the user-visible frame, input, audio, memory, or other performance window being explained;
- `pending_leads`: observed signals not yet assessed by the Main protocol;
- `execution_queue`: subprotocol executions selected by the Main protocol;
- `executed_topics`: topics whose documents have been run, including partial executions;
- `directions_to_extend`: leads that are relevant but cannot execute because a named minimum evidence item is missing;
- `routing_ledger`: one record for every topic and lead, including activation decision, evidence refs, execution status, and reason for not executing;
- `root_cause_priority`: final ordering only; it never controls activation.

There is deliberately no immutable initial list of topics. The Main protocol starts with symptom-appropriate clues, selects the first subprotocol, and expands the worklist as subprotocols return new evidence. Spatial Engine is the default entry for spatial-runtime or frame-pipeline symptoms; it is not a universal first subprotocol for every kind of jank. Subprotocols never activate one another.

## Symptom-led Entry Topics

Before evaluating secondary leads, classify the user-visible symptom and add the corresponding entry subprotocol to the queue:

| Observed entry symptom | Entry topic | Entry behavior |
|---|---|---|
| App main/frame-driving thread jank, over-budget `doFrame`, UI/input latency, or App-side dropped frames | App Main Thread Jank | Must be added immediately and analyzed before causal extensions such as Binder, Memory, or CPU Scheduling |
| Spatial frame pipeline, APP Produce/SPR Consume, Late/Miss/Discard Frame, EngineRender, compositor, or GPU anomaly without App-side jank evidence | Spatial Engine | Use as the primary frame-pipeline entry |
| Explicit Binder blocking with no App-side jank signal | Binder | Analyze Binder directly, while still checking whether the caller is on a user-visible path |

For a spatial app, an App Jank entry also requires a frame-pipeline cross-check when the trace contains `OpenXRClientSpatialFrames`, `SpatialRuntimeAbnormalFrames`, `Spatial_Main`, `EngineRender`, `SpatialFrameCallback`, or `AppProduce` evidence. This cross-check is a Spatial Engine clue for the Main protocol even when the App side is currently the larger symptom. It must not be deferred until an optimization experiment proves that App work was insufficient.

“App has obvious jank” is itself an entry signal. Do not require the App Jank topic to first prove `doFrame` over budget before activating it; locating and quantifying the over-budget App frame is one of that topic's first analysis steps. A generic spatial jank description may activate both Spatial Engine and App Main Thread Jank when the evidence does not yet distinguish the side.

When App Main Thread Jank is an entry topic, Binder is not allowed to replace it as the initial focus merely because Binder slices are easier to recognize. Binder is normally appended after App Jank confirms a main-thread wait or a cross-process dependency, unless the user explicitly supplied a Binder incident independent of the App jank. The same rule applies to Spatial Audio: audio-service, `AudioTrack`, `AudioFlinger`, `ISpatializer`, audio creation, or spatializer-registration evidence on the critical path is enough to append Spatial Audio; a user-reported audio symptom is not required.

## Activation Gate

Evaluate every lead against the same shared gate:

1. **Temporal overlap**: the signal overlaps the `abnormal_window`, or the evidence establishes a direct dependency into that window.
2. **Dependency relevance**: the signal is on the user-visible critical path or is a plausible upstream dependency of a critical-path event.
3. **Executable evidence**: at least one topic-specific observation can be inspected now, from the trace, SQL result, log, metric, or supplied artifact.

If all three conditions hold, add the topic to `execution_queue`. Activation does not require proof that the topic is the primary cause, accounts for most of the budget, or has a complete caller/server/downstream closure.

Signals that only exist outside the abnormal window, are unrelated to the dependency chain, or are keyword-only with no executable observation remain unactivated. Record them only when they are useful as a limitation.

### Dependency Relevance

Critical-path relevance means that the user-visible result depends on the signal, not that the signal consumes the largest amount of time. For example, a synchronous Binder wait that blocks a frame-driving thread can pass the gate even when it occupies only part of the over-budget frame. Budget share affects causal priority after analysis; it does not veto activation.

Use these values when recording a lead:

```text
direct      signal is on the user-visible path
dependency  signal is an upstream/downstream dependency of that path
adjacent    signal overlaps the window but path relevance is unproven
unrelated   signal is outside the path or window
```

Only `direct` and `dependency` leads pass the Activation Gate. An `adjacent` lead may be promoted if a later topic establishes the dependency.

## Main Protocol Execution Loop

Execution is iterative and must not be reduced to a one-time routing decision or a frozen topic list.

1. Establish `abnormal_window` and register all symptom evidence as `pending_leads`.
2. The Main protocol evaluates the next pending clue with the Activation Gate and writes the decision to `routing_ledger`.
3. If the clue passes, the Main protocol appends the corresponding subprotocol execution to `execution_queue`.
4. The Main protocol loads and runs exactly that subprotocol; the subprotocol analyzes only its own topic.
5. The subprotocol returns its topic result and `controller_handoff` evidence to the Main protocol. An empty handoff is not a completion signal.
6. The Main protocol converts each handoff item into a new `pending_lead`, deduplicates it, and records the source evidence.
7. The Main protocol re-evaluates all pending leads and performs a full Common Topic Map sweep, appending every newly activated subprotocol to `execution_queue`; it never relies only on the subprotocol's suggested topic names.
8. The Main protocol repeats steps 4–7 until `execution_queue` is empty and a fresh full registry sweep produces no new executable lead.
9. Only after step 8 may it calculate causal priority and emit the final summary. Before emitting it, every registry entry must have a terminal ledger status: `executed`, `blocked` with a concrete missing minimum, or `not_activated` with evidence for the failed gate.

A subprotocol must not decide that another subprotocol is “not needed” merely because its own topic appears more time-consuming or more likely to be the root cause. It returns structured cross-topic evidence; only the Main protocol applies the Activation Gate and updates the queue.

```yaml
controller_handoff:
  signal: "App frame-driving thread waits for a remote transaction"
  time_window: "overlaps Late Frame window"
  dependency_relation: dependency
  evidence_refs: [app:e12]
  question_for_controller: "Assess whether another registered topic should inspect the dependency"
```

## Subprotocol Execution Contract

For each queued subprotocol:

1. Open and execute its subprotocol document from its availability/evidence section.
2. Write the subprotocol output even if the closure is partial.
3. Record `activation_context`, `topic_state`, evidence IDs, closure level, causal role, `controller_handoff`, limitations, and next actions.
4. Return the complete result to the Main protocol.
5. Do not load, activate, skip, or execute another subprotocol from inside the current subprotocol.

The queue is a Main-protocol worklist, not a fixed priority list. Suggested ordering is by entry-topic precedence, directness, time-window overlap, and evidence availability, but reordering must not discard another pending lead. A causal extension must not outrank an unexecuted symptom entry topic.

## Closure and Causal Assessment

Keep these decisions separate:

- `activation`: whether the topic was relevant enough to investigate;
- `execution`: whether the topic document was run;
- `closure_level`: how far the evidence chain was resolved;
- `causal_role`: what role the topic appears to play;
- `conclusion_level`: confidence in that assessment.

An evidence gap lowers closure and confidence. It does not undo activation or erase the topic output. A topic may be `contributor`, `amplifier`, or `upstream_cause` without being the independent primary cause.

## Common Topic Map

The following map is a starting registry, not a fixed execution plan:

| Topic | Typical activation lead | Topic document |
|---|---|---|
| Spatial Engine | Spatial frame anomaly or spatial rendering budget signal | `../analysis-topic/analysis-spatial-engine.md` |
| Binder | Critical-path remote wait, transaction, or service dependency | `../analysis-topic/analysis-binder.md` |
| Memory | GC, reclaim, PSS/RSS, OOM, or LMK signal on the relevant path | `../analysis-topic/analysis-memory.md` |
| CPU Scheduling | Runnable starvation, scheduling latency, runqueue, or contention | `../analysis-topic/analysis-cpu-scheduling.md` |
| Spatial Audio | Audio latency, underrun, audio-service hotspot, or spatial audio path | `../analysis-topic/analysis-spatial-audio.md` |
| App Main Thread Jank | Over-budget `doFrame`, input timeout, or App frame-driving thread delay | `../analysis-topic/analysis-kotlin-spatial-app-jank.md` |

The map does not impose a priority or limit the expansion depth. The following signals are executable clues for the Main protocol, not routing rules embedded in subprotocol documents:

- `SpatialFrameCallback`, `AppProduce`, `OpenXRClientSpatialFrames`, or any Late/Miss/Discard/EngineRender/Spatial_Main evidence overlapping the abnormal window activates Spatial Engine for a frame-pipeline cross-check.
- `AudioFlinger`, `IAudio*`, `AudioTrack`, `ISpatializer`, `createTrack`, `registerSoundPlayer`, audio decoding, or spatial-audio resource lifecycle evidence overlapping a critical-path frame activates Spatial Audio.
- A synchronous remote transaction on a critical-path thread activates Binder.
- GC, allocation, reclaim, PSS/RSS growth, or memory-pressure evidence on the dependency chain activates Memory.
- Runnable-but-not-running, runqueue, preemption, or scheduling-latency evidence activates CPU Scheduling.

## Finalization Rules

Before producing `final-summary.md`:

- every activated subprotocol has an executed subprotocol output, including partial outputs;
- every evidence-backed pending lead that passed the gate was executed or is recorded as blocked with a specific missing evidence item;
- every subprotocol in the Common Topic Map has a registry status (`executed`, `not_activated`, or `blocked`) and an evidence reference; an omitted subprotocol is a Main-protocol failure;
- for a PICO Spatial diagnosis with an exposed KB backend, the [PICO Spatial PerformanceKB Mandatory Gate](../common/knowledge-base-usage.md) is complete (`extensions.knowledge_base.gate.complete: true`); an incomplete gate caps every KB-relevant `conclusion_level` per the barrier in `final-summary-contract.md`;
- `directions_to_extend` contains only leads whose minimum evidence is missing;
- `root_cause_priority` is applied only after the Main-protocol loop is exhausted;
- multiple causal roles may coexist.

The routing ledger is a completion barrier, not explanatory prose. At minimum, keep one compact record per topic with `activation_decision`, `evidence_refs`, `dependency_relation`, `execution_status`, and `reason`. A topic that was mentioned by another topic but failed the gate is still recorded as `not_activated` or `blocked`; an omitted topic is not equivalent to a negative routing decision.

## Coordination Output

```text
1. Abnormal window:
2. Executed topics:
3. Pending leads:
4. Directions to extend:
5. Current analysis focus:
6. Evidence gaps:
7. Next actions:
```
