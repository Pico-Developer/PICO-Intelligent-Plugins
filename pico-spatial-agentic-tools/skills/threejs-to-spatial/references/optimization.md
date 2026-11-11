# Lossless Optimization Evaluation

Before entering acceptance, use an independent performance gate to answer two questions: whether the current build meets the
contract budgets, and whether each optimization truly preserves business behavior. Migration only guarantees "it runs", not
"it runs well"; artifacts that directly replicate the Web implementation are usually slower than the source app on high draw
calls, full-page re-composition, and per-frame logic.

## 1. Prerequisites

- The target project has been generated according to the frozen contract and built successfully.
- Every page, state, flow, and input in the contract can be reached on the target device.
- The measurement device, ROM, SDK version, and container are consistent with the contract, and are written into the report.
- Each metric category has an explicit measurement method: `pico-cli perf`, Perfetto Trace, engine statistics, or in-app timing.

Data from different devices or different containers must not be mixed within the same report.

## 2. Budgets

Budgets are determined by device capability and business goals, and Web-side values are not taken directly as targets:

- Frame time: p95 frame time at the target refresh rate and the allowed ratio of stutter frames.
- Draw cost: draw call or batch upper limit.
- Geometry and instances: upper limits for total vertices, instances, and dynamic mesh update volume.
- Memory: upper limits for resident texture and mesh memory.
- Startup: cold start to first frame, and time for repeated scene entry.
- Material warm-up: PSO warm-up cost on first load when using ShaderGraph.

Measurements of the source Web app serve only as a "business load reference", used to confirm that scene complexity and
interaction density have not been reduced, and not as a basis for cross-platform numerical equivalence.

## 3. Measurement Requirements

- Cold path and hot path are recorded separately: first load, repeated load after warm-up completes, and page round trips.
- Each metric records the sample count, statistical basis (such as p50/p95), and the raw evidence file path.
- Measurement must cover all pages and major states in the contract, and must not measure only the default idle frame.
- Values must come from actual runtime; code structure, model count, or admission score cannot replace measurement.

## 4. Lossless Optimization Checklist

The following optimizations are preferred under the premise of preserving contract behavior:

- Repeated geometry and particles use `MeshInstancesResource` or entity/instance pools.
- Share `MeshResource`, materials, and textures, building a registry by scene lifecycle.
- Batch static content to reduce independent `ModelEntity` instances and material switching.
- Group transparent and semi-transparent content by `DrawOrderGroup` to control overdraw.
- Use LOD or distance-based visibility for distant and low-attention content; the resolution states required by the contract must still be achievable.
- Compress textures to the target display size, removing desktop-only ultra-high-resolution assets from the source project.
- Split SpatialUI re-composition scope by state to avoid full-page re-composition and per-frame state writes.
- Register ECS Systems only when needed; keep per-frame logic bounded and within budget limits.
- Control the number of ShaderGraphs by load batch; put cold loading on an asynchronous path with a loading state.

## 5. Losslessness Determination

Each optimization must simultaneously have:

- Same-semantic visual evidence before and after the optimization;
- Same-semantic interaction evidence before and after the optimization;
- Before and after measurement values on the same device, ROM, SDK build, and container;
- All affected pages, states, and flows in the contract still fully reachable.

Any change that alters visible results, interaction feedback, or state semantics is not an optimization but a degradation: it must
enter the approval process of the mapping report and `degradation-decision.json`, and cannot be counted as optimization benefit.

## 6. Report and Gate

The artifact is `optimization-report.json`, with field definitions in `artifact-contract.md`. The report must
list budgets, each measurement, each optimization and its evidence, and remaining risks.

Conditions for entering acceptance:

- All contract measurements meet budgets;
- Every optimization is marked as lossless with before and after evidence;
- There is no unexplained budget gap.

If budgets are still exceeded after completing all lossless optimizations, stop the conversion and report the measured gap, modify the contract, or request
degradation approval; it is not permitted to close out by lowering acceptance standards, deleting states, or skipping measurements.

## 7. Common Performance Issues

- Independent material and independent draw call per object, especially when loading ShaderGraph materials per entity.
- High-resolution textures and uncompressed formats from the source project copied directly into the target.
- Full-page UI re-composing entirely on every frame or every state change.
- Unbounded ECS per-frame allocation, collision queries, or object creation.
- Transparent layer count and particle count without upper limits, causing overdraw and GPU queueing.
- ShaderGraphs concentrated in synchronous first-frame loading, exposing PSO warm-up cost on the interaction path.
