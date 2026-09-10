# Camera And Window API

This file covers the public camera-facing APIs used to create and control spatial windows.

## `SpatialCamera`

### Role

- Unity component that represents a spatial window definition.
- The runtime opens at most one active spatial camera window at a time via `SpatialCamera.Current`.

### Nested Enum: `SpatialCamera.CameraMode`

- `Constrained`
  - Creates a bounded spatial window/container.
  - Uses size metadata from `SpatialCameraConfiguration`.
- `Unconstrained`
  - Creates a stage-style window/world presentation.
  - Used by the runtime when syncing `XROrigin` offsets.

### Static Property: `Current`

- Type: `SpatialCamera`
- Purpose: returns the camera whose spatial window is currently open.
- Output states:
  - A `SpatialCamera` instance when a window is open.
  - `null` when no spatial window is currently open.

### Static Property: `DefaultConfiguration`

- Type: `SpatialCameraConfiguration`
- Purpose: fallback configuration used when a camera has no explicit `OutputConfiguration`.
- Output states:
  - A configuration assigned from `SpatialAdapterResourceData.DefaultSpatialCameraConfiguration`.
  - `null` if no default has been configured yet.

### Property: `CurrentConfiguration`

- Type: `SpatialCameraConfiguration`
- Purpose: returns the active configuration for this camera.
- Output states:
  - `OutputConfiguration` when it is assigned.
  - `DefaultConfiguration` otherwise.

### Property: `Mode`

- Type: `SpatialCamera.CameraMode`
- Purpose: convenience accessor for `CurrentConfiguration.mode`.
- Output states:
  - `Constrained`
  - `Unconstrained`

### Property: `OutputDimensions`

- Type: `Vector3`
- Purpose: convenience accessor for `CurrentConfiguration.outputDimensions`.
- Output states:
  - Window dimensions in meters.

### Property: `WindowOpen`

- Type: `bool`
- Purpose: reports whether this camera is the active open spatial window.
- Output states:
  - `true`: this instance is `SpatialCamera.Current`.
  - `false`: another camera is active or no window is open.

### Serialized Fields

- `Dimensions`
  - Type: `Vector3`
  - Meaning: gizmo/reference size of the local camera volume.
- `OutputConfiguration`
  - Type: `SpatialCameraConfiguration`
  - Meaning: explicit configuration asset for this window.
- `OpenWindowOnLoad`
  - Type: `bool`
  - Meaning: if `true`, the camera opens its window in `Awake()`.

### `void OpenWindow()`

- Purpose: closes any currently active spatial window and opens this one.
- Arguments: none.
- Output states:
  - Returns `void`.
  - Sets `SpatialCamera.Current = this`.
  - Queues a backend open-window request through `SpatialAdapterRuntime.Instance`.

### `void CloseWindow()`

- Purpose: closes this spatial window if it is active.
- Arguments: none.
- Output states:
  - Returns `void`.
  - Sets `SpatialCamera.Current = null`.
  - Queues a backend close-window request.

### `Matrix4x4 GetRootTransform()`

- Purpose: calculates the matrix used to position the backend's root/window container relative to the Unity transform.
- Arguments: none.
- Output states:
  - Returns a `Matrix4x4` that combines:
    - inverse local/world transform
    - inverse `Dimensions` scale
    - backend window depth offset correction
    - `OutputDimensions` scale
- Use this when mirroring the camera into the backend.

## `SpatialCameraConfigurationData`

### Role

- Compact value type sent to native code for default window configuration and open-window calls.

### Constructor: `SpatialCameraConfigurationData(SpatialCamera.CameraMode mode, Vector3 outputDimensions)`

- Purpose: creates the struct sent to native code.
- Arguments:
  - `mode`: backend camera/window mode.
  - `outputDimensions`: output size in meters.
- Output states:
  - Returns a populated `SpatialCameraConfigurationData` value.

## `SpatialCameraConfiguration`

### Role

- `ScriptableObject` that stores reusable spatial window settings.

### Serialized Fields

- `outputDimensions`
  - Type: `Vector3`
  - Meaning: width, height, and depth of the spatial output volume in meters.
- `mode`
  - Type: `SpatialCamera.CameraMode`
  - Meaning: constrained window vs unconstrained stage behavior.

### `SpatialCameraConfigurationData GetData()`

- Purpose: converts the scriptable object into the compact native payload.
- Arguments: none.
- Output states:
  - Returns a new `SpatialCameraConfigurationData` containing the current `mode` and `outputDimensions`.

### `Dictionary<string, string> GetCustomMetaData()`

- Purpose: builds platform metadata used to describe the spatial window/container to the host system.
- Arguments: none.
- Output states:
  - Returns a metadata dictionary whose keys depend on `mode`.
  - For `Constrained`, keys include:
    - `pico.spatial.windowcontainer.id`
    - `pico.spatial.windowcontainer.style`
    - `pico.spatial.windowcontainer.defaultsize`
    - `pico.spatial.windowcontainer.minsize`
    - `pico.spatial.windowcontainer.maxsize`
    - `pico.spatial.windowcontainer.resizerestriction`
  - For `Unconstrained`, keys include:
    - `pico.spatial.stage.id`
    - `pico.spatial.stage.style`

## Agent Guidance

- If you need a normal bounded app window, prefer `CameraMode.Constrained`.
- If you need a stage/world-style presentation that follows XR origin behavior, prefer `CameraMode.Unconstrained`.
- If `OutputConfiguration` is omitted on a `SpatialCamera`, ensure `SpatialAdapterResourceData.DefaultSpatialCameraConfiguration` is set or the runtime may not have a usable fallback.
