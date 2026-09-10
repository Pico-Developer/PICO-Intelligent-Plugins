# SpatialML Implementation Workflows

Use this reference after the parent `spatialml` skill has identified an implementation, review, or
debugging task inside a Unity, Kotlin Spatial SDK, or Native OpenXR project. It adapts the reusable
workflow knowledge from the SDK documentation without assuming that any documentation repository or
Markdown path exists in the user's workspace.

## Ground Every SDK Detail In The Knowledge Graph

The workflow stages in this file are stable routing guidance. Exact classes, methods, operator names,
tensor encodings, permissions, and lifecycle rules are versioned SDK facts. Retrieve those facts from
`pico-dev-knowledge` before writing or changing non-trivial SDK code.

1. Inspect project-local manifests, dependencies, imports, and existing SpatialML code. Project-local
   evidence determines the SDK version and existing conventions.
2. Use `spatialml doctor` to confirm the detected SDK and runtime mode when live CLI execution is in
   scope. Do not infer mode only from the requested output.
3. Query `pico-dev-knowledge` with the SDK, mode, workflow goal, and named concept. Start broad enough
   to retrieve the workflow page, then query the relevant operator or API card for exact bindings.
4. Reconcile the result with project-local code. Prefer public documented APIs and preserve a working
   local pattern when it matches the installed SDK.
5. If the knowledge graph is unavailable, continue from project evidence and stable guidance here,
   but mark unverified API spelling or mode support instead of guessing.

Do not search for or require paths such as `docs/securemr/...`, `docs/spatialml/...`, or
`docs/spatialml-native/...` in the consuming project. Those source documents are inputs to the
knowledge graph, not runtime skill dependencies.

### Query Recipes

Adapt these as natural-language `query_graph` requests. Include the installed SDK version when known.

| Goal                     | Initial knowledge query                                                               | Follow-up evidence                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Core app graph           | `SpatialML <SDK> <mode> session pipeline tensor execution lifecycle cleanup`          | Core API and execution-model results                                                    |
| Camera to model          | `SpatialML <SDK> <mode> VST camera preprocessing model inference workflow`            | Camera, affine/resize, color, normalization, layout, and inference operator cards       |
| Select an operator       | `SpatialML <SDK> <mode> operator catalog <task>`                                      | The exact operator card, including operands, results, tensor contract, and mode support |
| LiteRT/TFLite inference  | `SpatialML <SDK> <mode> LiteRT TFLite model node bindings input output encoding`      | Model inference card plus model/tensor troubleshooting                                  |
| 2D to 3D placement       | `SpatialML <SDK> <mode> project image UV detection to camera and world space`         | VST metadata, projection, coordinate-transform, and output API results                  |
| Visible output           | `SpatialML <SDK> <mode> visible output rendering owner scene graph glTF texture text` | Mode-specific output operators and container/rendering rules                            |
| Pipeline ordering        | `SpatialML <SDK> <mode> pipeline synchronization dependency run handle global tensor` | Submit/execute ordering and placeholder/global binding APIs                             |
| Readback or tensor debug | `SpatialML <SDK> <mode> readback global tensor privacy permission debug`              | Readback API, resource cleanup, and privacy boundary                                    |

One broad query is not enough when code depends on exact operand names, shapes, enum values, or cleanup
semantics. Retrieve the specific API/operator result before coding those details.

## Select The SDK And Mode Adapter

Runtime mode and privacy mode are different decisions. `xr` versus `spatial` selects the rendering and
integration owner. Secure Mode versus Readback Mode selects whether protected results remain inside
SpatialML or cross into application memory.

| Parent SDK                          | Runtime mode | Rendering/output owner                               | Implementation boundary                                                                                   |
| ----------------------------------- | ------------ | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Unity with Spatial Adapter disabled | XR           | Unity plus SpatialML XR glTF/text/texture output     | Use the Unity plugin's `spatialml` implementation reference for current C# APIs                           |
| Unity with Spatial Adapter enabled  | Spatial      | SpatialEngine scene graph/components                 | Use the Unity plugin's Spatial-mode adapter and container rules                                           |
| Kotlin Spatial SDK                  | Spatial      | SpatialEngine                                        | Use Kotlin fluent `Pipeline` APIs and SpatialML session/scene output retrieved from the Kotlin docs graph |
| Native OpenXR                       | XR           | OpenXR app plus protected glTF/render-command output | Prefer the documented `securemr_utils` layer; use raw extension APIs only for low-level validation        |

Do not translate APIs mechanically across rows. A Unity `Provider`/`TensorMapping` pattern, a Kotlin
fluent `Pipeline` call, and a Native C++ placeholder map may represent the same graph concept without
sharing names, ownership, or asynchronous behavior.

## Build The Graph By Stages

Express the feature as explicit stages before selecting APIs:

```text
acquire -> preprocess -> infer -> postprocess -> synchronize -> spatial transform -> output
                                                                    \-> optional readback
```

For each boundary, record the producer, consumer, shape, channels, data type, value range, coordinate
space, lifetime, and whether the tensor is local, a placeholder/reference, or global. This table is
also the fastest way to isolate most model and rendering bugs.

Before building a graph manually, check Pipeline Zoo for an exact package or reusable topology. When
a package already supplies acquisition, projection, scheduling, or display pipelines, preserve those
stages and their shared bindings. Load and execute the result through the owning SDK as described in
`pipeline-zoo.md`; do not reconstruct its graph from JSON.

Shared construction rules:

- Build sessions, pipelines, operators, models, and durable tensors once; submit or execute the graph
  repeatedly. Do not rebuild the graph in a frame/update loop.
- Keep intermediate signals pipeline-local unless another pipeline or explicit readback needs them.
- Use compatible global tensors and the SDK's documented binding mechanism for cross-pipeline data.
- Carry dependency/run handles between stages whose data must be ordered. Do not rely on incidental
  submission timing.
- Tie asynchronous work and resource cleanup to the parent SDK's lifecycle. Destroy children before
  their session/framework owner and release readback resources promptly.

## Camera-To-Model And LiteRT/TFLite Inference

1. Acquire only the VST outputs needed by the graph. Keep image, timestamp, camera intrinsics, and
   stereo data from one coherent capture when projection uses them.
2. Match image tensors to the configured session/provider dimensions unless a deliberate resize is
   part of preprocessing.
3. Establish the model contract before wiring inference: input/output names, counts, shapes, data
   types, quantization, HWC/CHW layout, color order, numeric range, resize/crop, and normalization.
4. Preprocess explicitly. Raw camera bytes are rarely a model-ready tensor.
5. Use portable `.tflite` model bytes and the documented LiteRT inference path. Select a supported
   CPU/GPU/NPU target only through the installed SDK's public API.
6. Allocate outputs to the real model contract, then apply task-specific postprocessing such as
   argmax, detection decoding, NMS, coordinate restoration, or normalization reversal.
7. Route results to protected output when app code only needs to show them. Add readback only when the
   application genuinely needs the data.

Do not copy model node names or preprocessing formulas from another sample unless inspection proves
the target model has the same contract. Do not revive QNN context binaries, Docker conversion, direct
LiteRT CLI fallback, or NPU AOT compilation.

## Operator Selection

Choose operators from the task, not from remembered class names:

- acquisition: VST, depth, microphone, or another protected input;
- preprocessing: affine crop/resize, color conversion, type conversion, normalization, layout change;
- inference and postprocessing: LiteRT inference, comparison/reduction, argmax, NMS, tensor math;
- spatial transforms: image/UV to camera space, camera to world/local space, transform construction;
- output: XR glTF/text/texture or SpatialEngine scene graph/component changes;
- diagnostics: explicit global-tensor readback or protected in-runtime debug output.

For each selected operator, retrieve its SDK-specific card and verify constructor/configuration,
operands, results, tensor attributes, mode support, and lifecycle. Package declarations remain subject
to the same constraints; JSON does not bypass the operator contract.

## 2D-To-3D Placement

1. Keep the stereo images, timestamp, and camera intrinsics needed by projection from the same frame.
2. Convert model coordinates into the documented image/UV convention. Confirm normalized versus pixel
   coordinates, axis order, origin, and image dimensions.
3. Project image coordinates into camera space with the SDK's documented operator.
4. Apply explicit axis, scale, rotation, and offset adjustments; record both source and target spaces.
5. Use the capture timestamp when resolving camera-to-world/OpenXR-local transforms.
6. Hand the resulting transform to the selected mode's output adapter.
7. If a package display pipeline already performs projection and placement, preserve its shared camera
   metadata and dependency order instead of rebuilding the stage.

Wrong depth, objects behind the user, view-locked output, or jitter usually indicate mixed-frame
metadata, swapped UV axes, a missing space conversion, or a stale dependency—not a rendering problem.

## Choose The Visible Output Path

- **Unity XR:** query and use the current XR glTF/text/texture operators or generated package display
  pipeline. Unity owns the app rendering path.
- **Unity Spatial:** use the documented SpatialEngine scene-graph/component output path for
  SpatialAdapter-converted content. Do not mix in XR glTF output operators.
- **Kotlin Spatial SDK:** use SpatialML scene-graph output for protected display, or explicit readback
  followed by app-owned SpatialEngine entities. There is no Kotlin XR-mode adapter in this workflow.
- **Native OpenXR:** prefer protected glTF/render-command output through the utility layer. Keep poses
  in the intended OpenXR reference space and preserve `waitFor` dependencies.

Bind durable scene assets, textures, or visibility once when possible. Per-frame pipelines should
update only values that actually change.

## Readback And Debugging

Debug from the smallest failing stage outward:

1. Confirm graph topology, tensor ownership, placeholder/global mappings, and dependency handles.
2. Compare every boundary tensor against its expected contract. All-zero output commonly means an
   uninitialized tensor, wrong mapping, or execution-order problem. Semantically wrong but
   shape-compatible output commonly means preprocessing, encoding, or coordinate mismatch.
3. Use protected text/texture/scene output for inspection when it can answer the question without
   exporting data.
4. If app-side inspection is necessary, route only the selected signal into a compatible global
   tensor and use the SDK's documented asynchronous readback API. Local tensors are not readback
   targets.
5. Treat readback as a privacy boundary. Check mode, permissions, threading, and resource release;
   remove or gate diagnostic exports before production.
6. For a Pipeline Zoo graph, inspect generated shared tensors, submit bindings, pipeline IDs, and
   wrapper execution before adding custom mappings. Do not bypass the SDK/package wrapper while
   debugging.

Use pySpatialML for package-scoped execution, tensor tracing, and model comparison. Use pico-cli's
delegated commands for package validation and model inspection/visualization, and use pico-cli
app/device diagnostics for crashes, process state, complete app logs, screenshots, and system traces.

## Completion Checklist

- SDK and runtime mode were detected from project/doctor evidence.
- Exact SDK APIs and operator contracts were retrieved from `pico-dev-knowledge` or explicitly marked
  unverified when the graph was unavailable.
- Pipeline Zoo was checked before manual graph construction.
- Each stage has an explicit tensor and coordinate contract.
- Cross-pipeline values use compatible global bindings and explicit dependency ordering.
- The model is portable LiteRT/TFLite and its real node/shape/preprocessing contract is respected.
- Visible output matches the rendering owner; XR and Spatial output operators are not mixed.
- Readback exists only when app-side data is required and its privacy/permission/cleanup obligations
  are handled.
- Graph resources are built once, submitted repeatedly, and released in owner-safe order.
- Build/runtime evidence covers the target SDK and device-dependent behavior.
