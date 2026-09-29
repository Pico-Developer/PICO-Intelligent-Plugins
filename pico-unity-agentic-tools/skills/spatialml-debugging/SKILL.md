---
name: spatialml-debugging
description: Debug PICO Unity SpatialML apps, pipelines, and operators in XR or Spatial mode using service logs and global tensor readback. Use for SecureMR/OpenMR runtime failures, blank inference output, zero or stale tensors, operator errors, debug.pico.spatialml.debug, verbose service logging, readback permission failures, NativeArray byte-count mistakes, or intermediate-value inspection. Covers mode-specific service coverage, asynchronous buffer/texture lifetime, evidence capture, and debug cleanup.
license: 'Apache-2.0'
---

# Debug SpatialML in Unity

Use this workflow in an existing PICO Unity project. Route Kotlin Spatial SDK work to the Spatial
plugin's `spatialml-debugging` skill. Use `spatialml` for general graph construction/package operations.
Do not reinitialize an existing Unity project just to debug its pipelines.

## Probe a Unity global output

- Inspect resolved SDK sources, scripting defines, provider backend, and Spatial Adapter configuration.
  **Unity XR uses the XR service; Unity Spatial uses the Spatial service.** Do not switch mode to
  obtain another service's log events. Reuse the installed Unity workflow for build/install/launch.
  Observe the Unity MCP connection precheck and settle loop when using Unity MCP; do not require an
  Editor mutation just to inspect ADB logs.
- Verify `ByteDance.PICO.SecureMR.Tensor` APIs against the installed SDK or current knowledge cards.
  Create a provider-level global, a matching pipeline reference, and a `TensorMapping` binding for
  the producer. Preserve generated package globals and wrapper execution. A pipeline-local tensor
  or reference is not itself a readable global; check `IsGlobalTensor`.
- Preserve producer-consumer execution dependencies and run identifiers through the installed API.
  Capture one run with continuous submission paused. Keep provider/pipeline creation outside per-frame
  loops. Readback is a snapshot, not proof that the desired producer was submitted or completed.
- Prefer the **instance** `Tensor.ReadbackBufferAsync<T>()` helper so the tensor's backend selects XR
  or Spatial transport. Match `T` to the actual numeric type, check length, and record exceptions,
  empty results and exposed native error codes. Some revisions return an empty array/null on failure.
  Generic type arguments do not dequantize values.
- Check whether `ReadbackIntoAsync<T>(NativeArray<T>)` exists before using it: older SDK revisions
  lack it. It returns **bytes**, can truncate to destination capacity, and requires storage to remain
  alive until completion. Validate expected bytes and scalar-size divisibility; do not use bytes as
  an element count or inspect unfilled capacity. Prevent overlapping writes to one destination.
- `ReadbackTextureAsync()` returns a disposable wrapper. XR uses a supported GPU texture path; Spatial
  uses a TextureResource path through its backend. Do not manually call static XR helpers in Spatial
  mode. Keep wrappers alive while used, then release under the installed SDK's lifecycle contract.
- On teardown, stop scheduling new work and settle pending reads before releasing destinations and
  provider-owned resources. A timeout in UI code does not cancel the native future; do not free its
  buffer or destroy its owner solely because a timer elapsed.

Example fragment inside an async method after ordering the producer; `globalOutput` must be verified
FLOAT32, and `expectedElements` includes channels:

```csharp
if (!globalOutput.IsGlobalTensor)
    throw new System.InvalidOperationException("Readback requires a global tensor.");
float[] values = await globalOutput.ReadbackBufferAsync<float>();
if (values == null || values.Length != expectedElements)
    throw new System.InvalidOperationException("Readback length mismatch; inspect SDK/service errors.");
// Compute finite/NaN/Inf/zero counts and min/max; retain at most a small sample.
```

## Retrieve service debugging knowledge

Query available `pico-dev-knowledge` tools for SpatialML service logging, global tensor readback,
`debug.pico.spatialml.debug`, and the detected SDK, runtime mode, and version. Retrieve the relevant
service behavior, readback, and operator API knowledge before writing bindings. If lookup is
unavailable, use the essential contract below and verify APIs against the installed SDK. Do not
invent MCP names or SDK methods.

## Capture a bounded reproduction

1. Inspect the project, SDK versions, current device selection and app/service state. Keep static
   analysis usable without a headset. Run the platform's required environment preflight only before
   live CLI, knowledge, or device execution. Use available pico-cli help to select app/device
   diagnostics; do not invent a SpatialML tensor-dump command. ADB commands below operate on the
   chosen device after its environment is ready.
2. Explain that enabling the property enables service logging **and a device-wide readback permission
   bypass**. Use an authorized development device and controlled data. Existing task authorization
   suffices; do not add a repeated confirmation gate. Keep logs/tensor exports local unless sharing
   is authorized.
3. Record serial, build fingerprint, app/SDK build, runtime mode, service PIDs, and the current
   `debug.pico.spatialml.debug` value. Replace `SERIAL` in every command. Enable debugging and read
   back the property. Check command failures rather than assuming the write worked.

```text
adb devices -l
adb -s SERIAL shell getprop ro.build.fingerprint
adb -s SERIAL shell ps -A
adb -s SERIAL shell getprop debug.pico.spatialml.debug
adb -s SERIAL shell setprop debug.pico.spatialml.debug 1
adb -s SERIAL shell getprop debug.pico.spatialml.debug
```

4. Capture full logcat to a fresh local file before reproducing one small graph. Note the start/end
   times; stop with Ctrl-C or stop the tracked capture process. Do not clear existing log buffers.

```text
adb -s SERIAL logcat -v threadtime > spatialml-session.log
```

5. Filter the saved file with `rg -F 'SpatialMLDebug ' spatialml-session.log`. In PowerShell without
   ripgrep use `Select-String -Path spatialml-session.log -SimpleMatch 'SpatialMLDebug '`. Preserve
   the full log for ordinary errors and restrict analysis to the reproduction window.
6. Use the global-output probe above only if values are needed. Compare one boundary at a time:
   acquisition → preprocessing → inference → postprocessing → projection/output. Preserve package
   loader globals/bindings and producer dependencies; do not reconstruct a loaded package graph.
7. In a finally-style cleanup, stop new diagnostic work, settle pending reads, release resources,
   stop capture, set the debug property to `0` and verify it, even if the reproduction fails:

```text
adb -s SERIAL shell setprop debug.pico.spatialml.debug 0
adb -s SERIAL shell getprop debug.pico.spatialml.debug
```

Report denied property writes/cleanup; do not bypass image policy. Disabling does not revoke
already returned data or cancel admitted readbacks. Verify that fresh operations no longer emit
structured debug events.

## Essential service contract

- Use the non-persistent `debug.pico.spatialml.debug` property. Exact `1`, `true` or `TRUE` enables
  debugging; checks are live, independent of APK build type. Restart is unnecessary, but enable
  before graph construction to capture it.
- `SpatialMLDebug ` is a message prefix at INFO under tag `Secure MR::Server`. It is not a logcat
  tag. The emitting PID is the service; `pid=` in the event is the client. App-PID-only captures miss
  service events. A hidden log does not mean the bypass is off.
- Both services emit `task_enqueue`, `task_run_start`, `operator_execute_start/complete`,
  `task_run_complete`, `task_worker_complete` and supported readback requests. Spatial additionally
  emits structured API/lifecycle/wiring/model/submit events and `tensor_readback`/`tensor_readback_ack`.
  Do not diagnose absent Spatial-only events as XR failure.
- Correlate client PID, pipeline, task, operator and tensor handles within a service process/session.
  Handles are hexadecimal; Spatial `wait_for` is decimal. Events can interleave and execution may
  precede `submit`. `pipeline_load_summary` is a submit summary, not a package import event.
- Completion markers, including `status=ok`, do not establish valid output: operators can log errors
  internally and still return. Check ordinary service/LiteRT errors and values. A model's logged
  backend is requested, not measured. There is no `elapsed_ms` payload or uniform SDK/JNI tracing.
- The debug flag does not dump tensor values. Explicit SDK readback requires an
  owned global tensor. The bypass skips service readback permissions/AppOps, not ownership, SDK
  validation, tensor types, mappings, sensor availability, or transport support. Off-mode permissions
  come from operators registered by the client; a synthetic graph may need none.
- CPU buffer snapshots are supported in both services. XR uses GPU handles for supported dynamic
  textures; Spatial uses TextureResource IDs. The opposite texture transport is unsupported.
- For any value probe, record type, dimensions, channels, layout, expected bytes/range, quantization,
  producer and frame/task. Validate actual length, then summarize zeros, min/max, NaN/Inf and a bounded
  sample. A type parameter does not convert quantized data. Single-run probes avoid overwrite races;
  arbitrary sleeps do not establish producer completion.

## Deliver evidence

Report the SDK/mode and device build; reproduction and full log path; correlated error/task/operator;
probe contract and observed values; diagnosis versus remaining hypotheses; fix and verification;
property cleanup and resource status. Recheck the original issue and normal permission behavior with
debugging off. Remove or gate temporary instrumentation; measure performance with diagnostics off.
If no compatible device is available, deliver source/build findings and precise remaining device
checks without claiming runtime verification. Use pySpatialML for identified package/model
comparisons and platform diagnostics for whole-app/service evidence.
