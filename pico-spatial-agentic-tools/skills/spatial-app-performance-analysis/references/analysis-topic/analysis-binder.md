# IPC/Binder Analysis Workflow

Used to analyze binder transaction latency, `system_server`, binder thread pools, service call timeouts, or performance issues caused by cross-process blocking in PICO OS6.

## Topic Execution Contract

This document is executed only after [Analysis Topic Routing](../routing/analysis-topic-routing.md) adds Binder to the execution queue. It does not define an Activation Gate. The main controller has already established the abnormal-window overlap, dependency relevance, and minimum executable evidence.

Execute the Binder evidence chain even when the final Binder conclusion may be only a contributor, amplifier, upstream cause, or candidate. A lack of server evidence lowers the closure level and conclusion confidence; it does not cancel the topic execution.

## Closure Boundary (Do Not Stop at the Caller Side)

Once Binder is queued, strong caller-side evidence is NOT a complete Binder analysis. Confirming that the caller (app main / frame-driving thread, Runtime thread) is blocked on Binder only closes the caller half. Whenever the trace still contains the callee side, callee-side resolution is a **required step of the current analysis**, not an optional follow-up:

- Do NOT downgrade "identify the exact callee service and why it is slow" into `next_actions`, "directions to extend", or a future validation. If the evidence to do it is already present, it belongs to THIS Binder analysis now.
- You must complete the closed loop in "Locating Binder-Corresponding Server-side and System Services" below (Caller -> transaction -> Callee binder thread -> Service class/module -> server-side slow cause), or explicitly state which specific evidence is missing and why the callee cannot be resolved from the current trace.
- Binder may only be marked `confirmed` after the callee side and server-side slow cause are resolved. Caller-side-only evidence caps the conclusion at `candidate` or `likely`, and the reason the callee is unresolved must be a concrete evidence gap, not "the caller side is already convincing enough".

## Availability Check

Before performing root cause analysis, confirm if the user has provided any of the following evidence:
- Perfetto Slice containing binder transaction or binder thread activity
- `system_server` Slice near the problem window
- Caller and callee process/thread names
- Time window where the user-visible problem occurred

If none are available, first request the user to supplement the Perfetto trace or binder activity screenshots near the problem window.

## Evidence Order

1. Confirm the time window of the user-visible problem.
2. Determine if the caller process/thread is blocked on binder or waiting for a service return.
3. Find the callee, usually `system_server` or a service process.
4. Judge if the binder latency coincides with the user phenomenon window.
5. Judge if the callee was running, runnable, blocked, or continuing to wait for other dependencies at that time.
6. Judge if Binder is background noise, a candidate, contributor, amplifier, upstream cause, or primary cause. This is a post-analysis assessment and must not be used to undo topic activation.

## Common Signals

- `binder transaction`
- `binder reply`
- `binder thread`
- `transact`
- `system_server`
- App thread waiting for remote service
- Binder thread pool exhaustion

## Root Cause Patterns

### Caller Waiting for Slow Service

Evidence needed:
- App or Runtime thread blocked on binder.
- Callee service work overlaps with the waiting time.
- Wait duration is in the same window as jank, dropped frames, or interaction latency.

### system_server Overload

Evidence needed:
- `system_server` is busy within the problem window, or runnable but with obvious scheduling latency.
- The corresponding service path is on the chain of App / Runtime.

### Binder is Not the Root Cause

Do not list Binder as the root cause in the following cases:
- Binder activity is not within the user phenomenon window.
- The caller is not on a user-visible path.
- The callee returns quickly, but frame anomalies occur in subsequent rendering / GPU / compositor stages.

## Locating Binder-Corresponding Server-side and System Services

When the analysis goal upgrades from "confirming there is a Binder wait" to "precisely locating which system service is being waited for," you cannot stay at the `binder transaction` / `binder reply` name level. You must complete the closed loop of **Caller -> transaction clue -> Callee binder thread -> Service class / Service module -> Server-side slow cause**.

### Target Output

Answer at least the following 5 questions:

1. **Who is waiting?** (Caller process / thread)
2. **What transaction is being waited for?** (AIDL interface name, transaction code, or at least transaction clues)
3. **Which process does the service fall into?** (Usually `system_server`, but could also be audio, media, or other independent service processes)
4. **Which system service / service class does it most resemble?** (e.g., `AudioService`, `InputManagerService`, `WindowManagerService`, `PowerManagerService`, `ActivityTaskManagerService`)
5. **Why is the server-side slow?** (Running slow, runnable starvation, lock contention, GC, continuing to wait for downstream Binder)

### Evidence Chain Layering

#### Layer 1: Caller Path and Dependency Confirmation

First prove that Binder is indeed on the user-visible path, not background noise:

- Binder wait must be within windows like abnormal frames, `doFrame`, input processing, APP Produce, SPR Consume, etc.
- If the caller is the main thread / frame driving thread, record the Binder wait's budget share and thread state. A majority share is useful for causal priority, but is not required for Binder to be on the critical dependency path or for this topic to execute.

#### Layer 2: Transaction Naming Clue Extraction

Priority is given to extracting transaction clues directly from slice names on the caller and binder threads. The following naming evidence levels are ranked from high to low:

1. **Precise Interface Name**: `AIDL::java::IApplicationThread::scheduleTransaction::server`, `AudioManager::...`, `IWindowSession::...`
2. **AIDL Interface but No Specific Method**: `AIDL::ndk::BinderConnection::Unknown_Transaction_Code:1::client`
3. **Generic Names Only**: `binder transaction`, `binder reply`

If only Category 3 is available, do not directly write "unable to locate service"; continue with Layer 3 and Layer 4 analysis.

#### Layer 3: Locating the Callee Binder Thread

Find within the `system_server` or target service process in the same time window:

- `binder reply`
- `binder transaction`
- Binder threads (`binder:*`)
- Server-side business slices overlapping with the waiting period

The goal is not just to prove that `system_server` is busy, but to narrow down as much as possible to **which binder thread is processing this call**.

#### Layer 4: Back-inferring System Services from Server-side Business Slices

If the transaction name is still generalized, look for service class / module names in the server-side slices overlapping with the binder reply. Common keywords include:

| Keywords | Priority Suspected Service |
|---|---|
| `AudioService`, `PlaybackActivityMonitor`, `AudioTrack` | Audio / Spatial Audio related services |
| `InputManager`, `InputDispatcher`, `deliverInput` | Input service |
| `WindowManager`, `WindowState`, `ViewRootImpl`, `IWindowSession` | Window / WMS |
| `PowerManagerService`, `WakeLock` | Power management |
| `ActivityTaskManager`, `scheduleTransaction`, `clientTransactionExecuted` | Activity / Lifecycle scheduling |
| `PackageManager`, `AssetManager`, `ResourcesManager` | Package / Resource management |
| `SensorService`, `DisplayManager` | Sensor / Display chain |

If binder reply can be aligned with these service class slices, even if the full mapping of the transaction code is not obtained, a "high-confidence service attribution" can be output.

#### Layer 5: Server-side Slow Cause Drill-down

Precise service location is only an intermediate result; finally, explain why the service is slow:

- Service thread is `Running`: Continue to check leaf slices / slow functions.
- If the service thread is `R`, hand scheduling evidence to the Main protocol for supplementary analysis.
- Service thread blocked by `monitor contention` / `futex`: Continue to check the lock holder.
- If the service thread overlaps with GC / `ThreadFlipSuspendAll`, hand memory evidence to the Main protocol for supplementary analysis.
- If the service thread itself is waiting for Binder, hand the downstream dependency evidence to the Main protocol and continue the chain through the Main loop.

### Positioning Results Grading

To avoid over-assertion, the confidence of "locating the service" is divided into 3 levels when outputting:

- **exact**: Explicit interface / service method names appear directly in the slice, allowing the service name to be written directly.
- **high-confidence**: The transaction name is incomplete, but the server-side business slice in the same window clearly points to a specific system service.
- **candidate-only**: Only `binder transaction` / `binder reply` is present, lacking service class or transaction clues, providing only candidate directions.

Only when it is `exact` or `high-confidence` is it recommended to directly write "waiting for a certain service" in the conclusion; otherwise, write "most suspicious service candidate."

### Recommended Execution Order

Execute in the following order to avoid skipping steps:

1. Find Binder slices in the problem window within the caller's thread.
2. Extract transaction names / AIDL clues.
3. Find binder reply hotspots in the same window within `system_server` / target service process.
4. Check server-side business slices around the hotspot binder threads.
5. Explain "why this service is slow" using service class names, module names, lock contention, GC, and scheduling evidence.
6. Finally, judge if Binder is a direct root cause or indirectly amplified by server-side GC / locks / scheduling.

Full SQL queries see:

- `../sql-query/sql-binder-service-resolution.md`

## Output Supplement Items

After the analysis, output according to the unified protocol defined in `output-contract.md`. Set `issue_type_key` to `binder_latency` and supplement the following topic fields in `extensions.binder`:
- caller: Caller (process/thread)
- callee: Callee (process/thread)
- transaction_name_or_code: Transaction name or code
- wait_time_ms: Wait duration (ms)
- downstream_dependency: Whether there are unresolved downstream dependencies
- service_name_or_guess: Located system service name or high-confidence candidate
- service_confidence: `exact` / `high-confidence` / `candidate-only`
- service_side_evidence: Summary of server-side business slices, locks, GC, scheduling evidence, etc.

## Controller Handoff

Hand back caller/callee, transaction, server-side, downstream-dependency, time-window, and critical-path evidence to the Main protocol. The Main protocol decides whether the evidence activates another subprotocol; this document does not name or activate other subprotocols.

## Topic Output State

The Binder topic output must distinguish activation, execution, closure, and causal assessment:

```yaml
topic_state:
  activation: activated
  execution: completed | completed_with_evidence_gap | blocked
  closure_level: signal | caller_path | transaction_callee | service_module | server_cause
  causal_role: background_noise | candidate | contributor | amplifier | upstream_cause | primary_cause
  controller_handoff: [<cross-topic evidence items>]
```

Use `completed_with_evidence_gap` when the topic ran but the trace cannot resolve the callee or server-side cause. Use `blocked` only when the minimum evidence needed to run even the caller-side checks is unavailable.
