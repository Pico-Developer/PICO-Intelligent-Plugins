# Spatial Engine Analysis Workflow

Used to analyze frame anomalies in spatial apps on PICO OS6, including `SpatialFrames`, `SpatialMetrics`, dropped frames, jank, and unified rendering budget issues.

## Topic Execution Instructions

This subprotocol is executed only when the Main protocol in [Analysis Topic Routing](../routing/analysis-topic-routing.md) adds it to the execution queue. The Main protocol owns activation. Execute this subprotocol from Spatial Trace Probe through abnormal-frame identification, bottleneck judgment, pressure-source tracing, closure assessment, and output. Hand back cross-topic evidence to the Main protocol; do not activate or load other subprotocols from this document.

The jank pressure of Spatial Engine comes from the submission of APP. Therefore, when analyzing the jank of Spatial Engine, you cannot stay at the Spatial Engine level and need to analyze the source of the pressure in depth.

## Spatial Trace Probe

Before entering Spatial analysis, use `spatial_probe.py` to check whether the trace contains Spatial characteristics.

**Invocation Commands:**

```bash
# Output compact YAML summary (recommended)
python scripts/spatial_probe.py \
  --trace <path/to/trace.perfetto-trace> \
  --package <package>

# Output full check report
python scripts/spatial_probe.py \
  --trace <path/to/trace.perfetto-trace> \
  --package <package> \
  --detail \
  --output <path/to/probe-result.yaml>
```

**Probe Checks:**

| Check Item | Description |
|---|---|
| `spatial_frames` | Whether the `OpenXRClientSpatialFrames` table exists and has data |
| `spatial_abnormal_frames` | Whether the `SpatialRuntimeAbnormalFrames` table exists |
| `spatial_bottlenecks` | Whether the `SpatialBottleneckEvents` table exists |
| `spatial_metrics` | Whether `TargetAppMetricCounterStates` / `spatial_metrics_definitions` exist |
| Target process | Whether the target App process is recorded in the trace |
| Key threads | Whether `Spatial_Main`, `Eng-Render`, `XR_Wait`, `RenderThread`, `compositor`, etc. are visible |

**How to Interpret Probe Results:**
- `observed`: The table exists and has data; you can enter the corresponding analysis step.
- `not_observed`: The table exists but has no data; record it as an analysis constraint.
- `missing_evidence`: The table is not in the schema; the trace did not collect this capability.
- Even if the Probe partially fails, analysis can still be performed within the scope of available evidence; missing evidence should be marked as constraints in the conclusion.

`spatial_probe.py` handles trace loading itself. Only fall back to the manual `daemon -> load` workflow in [tools.md](../common/tools.md) when troubleshooting probe failures or validating the underlying `pico-cli perf` session behavior directly.

## Core Three-step Analysis Method

### 1. Identify Abnormal Frames (SpatialFrame)

First locate the abnormal time window from `SpatialFrame`.

**Execute Query:**

```sql
SELECT * FROM OpenXRClientSpatialFrames
 WHERE name GLOB "Late *"
  OR name GLOB "Miss *"
  OR name GLOB "Early *"
  OR name GLOB "Discard *"
```

**Analysis Key Points:**
- What type of frame anomaly? (Late / Miss / Early / Discard)
- What is the abnormal time window?
- How do the CPU time and GPU time behave for the anomaly?

No cross-topic activation rules belong here. Hand back any relevant frame-pipeline, phase, and dependency evidence to the Main protocol.

### 2. Determine Bottleneck Type (SpatialMetrics)

Starting from the Spatial Runtime abnormal frame window, combine `SpatialMetrics` data to determine whether the bottleneck is more CPU- or GPU-oriented.

**Analysis Directions:**
- **GPU bottleneck**: Focus on Draw Call, triangle count, vertex count, Overdraw, Shader / material complexity, texture and Mesh memory.
- **CPU bottleneck**: Focus on animation, physics, entity updates, Portal, Media, 2D Render Effect, spatial audio, or other App-side resource usage.

The full metrics dictionary for SpatialMetrics is maintained separately in:
- [spatial-metrics.md](../common/spatial-metrics.md)

No cross-topic activation rules belong here. Hand back metric, phase, and pressure-source evidence to the Main protocol.

### 3. Trace Pressure Sources (APP Context)

After locating GPU / CPU bottlenecks, continue to combine spatial app process analysis to trace the pressure source.

**Common Root Cause Directions:**
- **Rendering workload too heavy**: Due to the unified rendering pipeline mechanism, the 2D / 3D rendering tasks submitted by the app are too many (e.g., Draw Call, Effect, ViewAttachment, too many materials or model resources), causing EngineRender pressure.
- **Unreasonable resource usage**: Too many resources such as spatial audio, video, Portal, physics, animation, etc., causing higher App or Runtime CPU usage.
- **ECS update pressure**: The app-side custom System `update()` logic is too heavy, or Entity / Component states change too frequently.
- **Runtime-side processing pressure**: The scale or change volume of data submitted by the app is too large, making `Spatial_Main`, `SpatialMFrame`, or Runtime system processing longer.

No cross-topic activation rules belong here. Hand back pressure-source and critical-path evidence to the Main protocol.

## Evidence Order

Strictly execute the following evidence chain; do not infer in reverse:

```text
SpatialFrames (prove frame failures and delineate time window)
    -> SpatialMetrics (classify to judge CPU / GPU load characteristics)
        -> Perfetto Slice (locate specific phases, threads, and code)
            -> Business implementation (Kotlin / ECS / 3D scenes / resource configuration optimization suggestions)
```

## Phase Analysis

### APP Produce

Key Slices:
- `Choreographer#beginSpatialFrame`
- `3d_ec`
- `System_Update`
- `System_Update: {name}`
- `Choreographer#endSpatialFrame`

If these Slices become longer within the abnormal frame window, prioritize suspecting APP Produce. Check custom ECS `update()`, object allocations, collection churn, string concatenation, heavy per-Entity logic, synchronous I/O, lock waits, and complex computations on the UI thread.

### APP / SPR Handoff

This is an asynchronous handoff phase and cannot be understood as a normal function call stack.

Check:
- Whether the APP outputs 2D / 3D ECS data in time.
- Whether there is queuing between APP completion and SPR consumption.
- Whether the submission cadence of 2D and 3D ECS is imbalanced.
- Whether end-to-end latency comes from cadence mismatch in handoff.

### SPR Consume

Key processes / threads:
- `com.pico.spatial.runtime`
- `Spatial_Main`

Key Slices:
- `doFrameBegin()-*`
- `SpatialMFrame`
- `updateInput()-*`
- `*System`
- `doFrameEnd()-*`

If APP is normal but `Spatial_Main` becomes longer, prioritize suspecting Runtime-side ECS / system processing, input / node synchronization, scene data scale, or submitted data change volume.

### EngineRender / Submit

Key tracks:
- `Eng-Render`
- `gpu_frame_end`
- `frameRate`

If APP and SPR are normal, but `Eng-Render` or GPU completion becomes high, prioritize suspecting unified 2D / 3D rendering pressure: triangles, Draw Calls, material / Shader switches, texture bandwidth, transparent objects, Overdraw, visible objects, render target pressure.

### OpenXR Compositor

Key processes / threads:
- `com.pico.xr.openxr_runtime`
- `compositor`
- `XR_Wait`
- `pvrtrackingservice`
- `pxrseethroughservice`

If APP, SPR, and EngineRender all look normal but the final frame still fails, expand to OpenXR Server, compositor, tracking, and passthrough services.

## Bottleneck Judgment Matrix

| Observation Result | Priority Suspected Direction |
|---|---|
| High GPU time + high Draw Call / triangles / vertices | 3D scene complexity, material switching, Overdraw, unified rendering pressure |
| High CPU time + high Animation / Physics / Entity / Media metrics | Animation, physics, entity synchronization, media, or App-side resource usage |
| High CPU time + high 2D Render Effect / ViewAttachment | 2D content and 3D content competing for unified rendering budget |
| APP `System_Update` or `3d_ec` becomes longer | Kotlin business logic, ECS updates, input processing, App CPU |
| APP normal, `Spatial_Main` becomes longer | SPR Consume, Runtime systems, submitted data scale |
| APP and `Spatial_Main` normal, `Eng-Render` becomes longer | Unified 2D / 3D rendering, scene complexity, render submission |
| CPU normal, GPU time becomes longer | Geometry, pixels, textures, Shader, render target pressure |
| APP / SPR / EngineRender normal, but frames still fail | OpenXR, compositor, tracking, passthrough services |
| SpatialMetrics rules hit in the same window | Has reference value, but still requires Slice validation |

## Output Requirements

Conclusions must include:
1. **Phenomenon**: Abnormal frame type, continuity, time window.
2. **Evidence**: SQL query results, metrics indicators in the same window, critical Slice durations.
3. **Phase localization**: APP Produce / SPR Consume / EngineRender / GPU / Compositor.
4. **Pressure source**: Specific resources, components, or business logic causing the bottleneck.
5. **Action**: Targeted optimization suggestions.
6. **Constraints and next steps**: Explain what evidence is still missing and how to verify next.
