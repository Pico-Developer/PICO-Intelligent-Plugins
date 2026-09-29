---
name: spatialml-debugging
description: Debug Kotlin PICO Spatial SDK SpatialML apps, pipelines, and operators using service logcat events and global tensor readback. Use for SecureMR/OpenMR runtime failures, blank inference output, zero or stale tensors, operator errors, debug.pico.spatialml.debug, verbose service logging, readback permission failures, and intermediate-value inspection. Covers the Spatial service, Kotlin readback extensions, tensor mappings, evidence capture, and debug cleanup; route Unity requests to the Unity plugin's corresponding skill.
license: 'Apache-2.0'
---

# Debug SpatialML in Kotlin Spatial SDK

Use this workflow for an existing Kotlin Spatial SDK app. Route Unity work to the Unity plugin's
`spatialml-debugging` skill. For general graph construction or package operations, use this plugin's
`spatialml` skill and its implementation/package references. A runtime debugging request does not
require a new design or onboarding workflow.

## Probe a Kotlin global output

- Detect the resolved `securemr` and `readback` artifacts/BOM and imports. This is the **Spatial
  service** path. Run `pico-env-doctor` before environment-dependent work, reusing a valid session
  result. Use `spatial-app-dev-workflow` and `spatial-emulator-usage` for relevant build/device work.
- Verify public APIs in the installed artifacts or current Kotlin knowledge cards. Readback extensions
  live in `com.pico.spatial.ml.readback`. Missing imports may mean the separate readback artifact is
  missing; follow the project's BOM rather than choosing a new version blindly.
- Allocate an appropriately typed `GlobalTensor` in the same session. Bind the producer's matching
  `PipelineTensorPlaceholder` at submission, or use the SDK's implicit global mapping where verified.
  For an intermediate, add a supported copy/result binding to that global. Never pass a local tensor
  directly to readback or treat assignment of a Kotlin variable as a tensor copy.
- Preserve `Pipeline.submit(...)`'s `RunTask` dependencies. Use app sequence markers and service
  events for correlation; access `runId` only if the resolved SDK exposes it publicly.
  Readback can wait for writers, but does not submit a producer. Pause continuous submission for a
  deterministic probe and avoid mutating an executing pipeline.
- Use `GlobalTensor.readbackContentSuspend()` and `TensorContent.use { ... }` for a CPU snapshot.
  Copy data or statistics inside the scope, using the verified type and native byte order. Include
  channels in expected element/byte counts. Do not hold `buffer` after close or call `applyChange()`
  while inspecting: it writes back to the tensor. The synchronous variant can block the UI thread.
- For dynamic textures, verify `readbackAsTextureResourceSuspend()` and the SDK's TextureResource
  ownership/release contract. Spatial readback returns a resource ID through its SDK, not an XR GPU
  handle. Keep the protected scene/container configuration when taking a diagnostic snapshot.
- A log showing `readback_request debug_bypass=1` is only a request. Compare `tensor_readback` byte
  metadata, exceptions, the returned buffer and normal SDK acknowledgment/release behavior.

For example, inside a suspend function after submitting the intended producer, with `globalOutput`
verified FLOAT32 and `expectedElements` including channels:

```kotlin
// Import com.pico.spatial.ml.readback.readbackContentSuspend.
globalOutput.readbackContentSuspend().use { content ->
    val bytes = content.buffer.duplicate().order(java.nio.ByteOrder.nativeOrder())
    bytes.rewind()
    require(bytes.remaining().toLong() == expectedElements.toLong() * 4L)
    val floats = bytes.asFloatBuffer()
    val sample = FloatArray(minOf(16, expectedElements))
    floats.get(sample)
    // Record bounded values/statistics and this probe's app-side sequence marker.
}
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
