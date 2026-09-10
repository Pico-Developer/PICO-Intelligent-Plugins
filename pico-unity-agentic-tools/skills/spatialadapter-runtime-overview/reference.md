# SpatialAdapterRuntime API Skills

This folder is an AI-agent-oriented map of the public C# API surface in `SpatialAdapterRuntime`.

## How To Use These Docs

- Start with the highest-level Unity-facing APIs first:
  - `SpatialAdapterRuntime.Initialize()`
  - `SpatialCamera`
  - `SpatialAdapterNativeText`
  - `SpatialAdapterVideoComponent`
  - `SurfaceTextureVideoComponent`
  - `SpatialInputSupport`
  - `SpatialAdapterRuntime.SyncMesh()`
  - `SpatialAdapterRuntime.RegisterDynamicTexture()`
- Treat most `public static extern` methods on `SpatialAdapterRuntime` as low-level native bridge calls.
- Prefer component-driven workflows over directly invoking low-level native functions unless you are implementing new runtime integrations.

## Common Return Conventions

- `int` return value:
  - `0` means success.
  - Non-zero means the native/backend call failed or the request was rejected.
- `bool` return value:
  - `true` means the wrapper call completed successfully.
  - `false` means the wrapper detected a failure and already logged an error.
- `IntPtr` return value:
  - Native handle/pointer returned by the backend.
  - Treat `IntPtr.Zero` as failure or "no resource".
- `ref` return or `ref` parameter:
  - Caller shares mutable struct memory with the runtime/native layer.
  - Populate all required fields before calling.

## Files In This Folder

- `runtime-core.md`: session, scene graph, resource, mesh, and low-level native bridge APIs.
- `camera-and-window.md`: spatial window and camera configuration APIs.
- `input.md`: spatial interaction and Unity Input System integration APIs.
- `components.md`: native text, video, hover, shadow, collision, and canvas-related APIs.

## Important Agent Notes

- `SpatialAdapterRuntime.Instance` must exist before most runtime-driven component registration works.
- Many public types are DTO-style structs or serialized containers. They are part of the public API surface even when they do not expose many methods.
- `SpatialAdapterRuntime.UpdateMaterialDynamicTexture()` accepts `parameterName`, but the current implementation does not use it. The runtime always forwards the texture by material instance ID only.
- `SpatialCamera.CurrentConfiguration` falls back to `SpatialCamera.DefaultConfiguration` when no explicit configuration is assigned.
- Runtime components usually mark themselves dirty and synchronize on later frame updates. Setting a property often does not push immediately; it schedules sync.
