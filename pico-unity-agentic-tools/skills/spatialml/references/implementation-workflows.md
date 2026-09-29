# Unity SpatialML Implementation Workflows

Use this reference when implementing, reviewing, or debugging a SpatialML graph in an existing PICO
Unity project. It adapts the reusable Unity documentation workflows without requiring their source
Markdown files to exist in the user's project.

## Retrieve Current Unity SDK Facts

The stage order and guardrails below are stable. Exact C# types, methods, operator operands/results,
mode restrictions, and cleanup behavior must come from the installed project's code and the
`pico-dev-knowledge` graph.

1. Inspect `Packages/manifest.json`, the resolved PICO Unity SDK, existing SpatialML code, and the
   Spatial Adapter setting.
2. Use `spatialml doctor` when live CLI execution is in scope to distinguish Unity XR mode from Unity
   Spatial mode and to separate project readiness from optional pySpatialML capabilities.
3. Query `pico-dev-knowledge` with `Unity SpatialML`, the detected mode, and the workflow goal. Follow
   the workflow result with the exact operator/core-API card before writing bindings.
4. Prefer public APIs and patterns confirmed by the installed project. If the graph is unavailable,
   identify unverified API details rather than guessing from another SDK.

Useful query shapes:

- `Unity SpatialML <XR|Spatial> Provider Pipeline Tensor TensorMapping execution lifecycle`
- `Unity SpatialML <XR|Spatial> VST preprocessing LiteRT TFLite model inference`
- `Unity SpatialML <XR|Spatial> <operator task> operands results tensor shape mode support`
- `Unity SpatialML <XR|Spatial> UV image detection camera world 3D placement`
- `Unity SpatialML <XR|Spatial> visible output glTF scene graph component texture text`
- `Unity SpatialML <XR|Spatial> global tensor readback privacy permission synchronization`

Do not require `docs/securemr/...` paths in the consuming project. Those pages are indexed knowledge
sources, not plugin runtime files.

## Plan The Feature

Write the graph as:

```text
acquire -> preprocess -> infer -> postprocess -> synchronize -> transform -> output
                                                               \-> optional readback
```

Record every stage's tensor name, shape, channels, data type, numeric range, coordinate space, owner,
and lifetime. Identify whether Unity needs the value or it can stay protected inside SpatialML.

Before manual construction, search Pipeline Zoo. If a package supplies producer and display pipelines,
preserve its shared globals, submit bindings, and dependency order. Execute through the generated
`SpatialMLPipelineZooAsset` wrappers; do not reconstruct or bypass the package graph.

Build providers, pipelines, operators, model configuration, and durable tensors once. Repeatedly
execute the graph; do not allocate or rebuild it in `Update()`. Tie cleanup and event unsubscription to
Unity lifecycle, and release package globals/pipelines before their provider owner according to the
retrieved SDK contract.

## Select Unity XR Or Spatial Output

Runtime mode and privacy/readback mode are separate decisions.

| Unity mode                           | Rendering owner | Visible SpatialML output                                                                     |
| ------------------------------------ | --------------- | -------------------------------------------------------------------------------------------- |
| XR (`isSpatialAdapter` disabled)     | Unity XR app    | Current XR glTF, pose, visibility, text, and texture operators or a package display pipeline |
| Spatial (`isSpatialAdapter` enabled) | SpatialEngine   | Current scene-graph visibility and component/property update operators                       |

For XR camera workflows, verify the current see-through setup. For Spatial mode, verify Spatial Adapter
and the container dimensions needed by output. Never use XR glTF output operators as the SpatialEngine
path, and never use Spatial scene-graph/component output as the Unity XR glTF path.

## Camera-To-Model And LiteRT/TFLite

1. Acquire only the image and metadata outputs needed by the graph. Keep stereo images, timestamp, and
   camera intrinsics from one coherent frame when later projection depends on them.
2. Match image tensors to provider dimensions unless resizing is intentional.
3. Establish the model contract: real input/output node names, counts, shapes, data types, quantization,
   HWC/CHW layout, color order, crop/resize, normalization, and output semantics.
4. Preprocess explicitly with the operator set confirmed by the graph: affine crop/resize, color/type
   conversion, normalization, and layout conversion as required.
5. Configure the documented LiteRT model type/target and bind operands/results using the target
   model's real node contract. Do not copy names or formulas from an unrelated sample.
6. Apply task-specific postprocessing, then route the result to XR output, Spatial output, another
   pipeline, or explicit readback.

Use portable `.tflite` assets and runtime JIT. Do not introduce QNN context binaries, Docker
conversion, direct LiteRT CLI fallback, or NPU AOT compilation.

## Operator Selection

Query the Unity operator catalog by task, then retrieve each exact card before coding:

- VST/depth/audio acquisition;
- affine, color, type, normalization, and layout preprocessing;
- LiteRT inference, argmax/NMS, comparisons, reductions, and tensor math;
- UV/image to camera space and camera to world transforms;
- XR glTF/text/texture output or Spatial scene-graph/component output;
- global-tensor readback and protected debug output.

Verify configuration, operands, results, tensor attributes, and mode support. Pipeline Zoo JSON uses
the same underlying contracts and is not permission to guess an operand name or tensor shape.

## 2D-To-3D Placement

1. Keep the projection metadata from the same VST capture as the model input.
2. Convert model coordinates into the documented Unity SpatialML UV/image convention. Confirm origin,
   axis order, normalized versus pixel coordinates, and frame dimensions.
3. Project into camera space with the current SDK operator.
4. Apply explicit coordinate-system, scale, rotation, and offset corrections.
5. Resolve camera-to-world placement at the matching timestamp.
6. Feed the resulting transform to the selected XR or Spatial output adapter.

If an imported display pipeline already performs projection and placement, preserve it and execute it
after the producer pipeline. Mixed-frame metadata, swapped UV axes, stale global mappings, and missing
dependency handles are the first checks for jitter or implausible placement.

## Synchronization, Readback, And Debugging

1. Reduce the graph to the smallest failing stage.
2. Verify every local/reference/global tensor binding and every producer-consumer dependency. Capture
   and use the documented run identifier for dependent execution.
3. Compare the actual tensor contract and value range at each boundary. All-zero results usually point
   to initialization, mapping, or ordering; plausible shapes with wrong values usually point to
   preprocessing or encoding.
4. Prefer protected text/texture output when it answers the question without exporting data.
5. For Unity-side inspection, promote only the selected signal to a provider-level global tensor and
   use the documented asynchronous buffer or texture readback API. Pipeline-local tensors are not
   readback targets. Dispose texture/readback resources as required.
6. Treat readback as an explicit privacy boundary. Verify the current mode and permissions, and remove
   or gate diagnostic paths before production.
7. With Pipeline Zoo, inspect generated globals, submit bindings, manifest pipeline IDs, and wrapper
   execution before adding custom mappings. Do not debug the underlying pipeline in a way that bypasses
   package-created bindings.

Use pySpatialML for package-scoped tensor traces or model comparison. Use pico-cli's delegated
commands for package validation and model inspection/visualization, and use pico-cli/Unity/device
diagnostics for complete app logs, crashes, screenshots, and system traces.

## Completion Checklist

- Unity SDK and XR/Spatial mode were detected from project or doctor evidence.
- Non-trivial C# APIs and operator contracts were retrieved from `pico-dev-knowledge`, or unresolved
  details were reported explicitly.
- Pipeline Zoo was checked before building the graph manually.
- Tensor, model, coordinate, and dependency contracts are explicit.
- Output operators match the Unity rendering owner.
- Readback is global-tensor-only, intentional, permission-aware, and cleaned up.
- Graph resources are created once and released in the SDK-documented lifecycle order.
- The project builds and device-dependent camera, inference, placement, and output behavior has runtime
  evidence.

## Service Debug Channel

For verbose service events or an explicit global tensor probe, use this plugin's
`spatialml-debugging` skill. It covers the device-wide readback permission bypass, mode-specific
log coverage, SDK snapshot lifetimes, and setting `debug.pico.spatialml.debug` to `0` afterward.
Completion markers alone do not establish correct output; correlate ordinary errors and values.
