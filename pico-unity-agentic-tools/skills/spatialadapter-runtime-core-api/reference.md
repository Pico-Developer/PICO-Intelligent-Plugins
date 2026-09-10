# Runtime Core API

This file documents the main runtime entry points in `ByteDance.PICO.SpatialAdapter`.

## Recommended Entry Points

### `SpatialAdapterRuntime.Instance`

- Type: `SpatialAdapterRuntime`
- Meaning: singleton runtime component created from the scene.
- Output states:
  - Non-null: runtime is present and can register/sync objects.
  - `null`: runtime has not been created yet or has already been destroyed.

### `OnSendResourceFilesCallback`

- Type: `delegate void OnSendResourceFilesCallback(List<string> filenames)`
- Purpose: callback signature used when the runtime wants to expose the full list of resource files that should be sent to a device.
- Arguments:
  - `filenames`: full file paths for resources collected during resource registration.
- Output states:
  - Returns `void`.

### `OnSendResourceFiles`

- Type: `SpatialAdapterRuntime.OnSendResourceFilesCallback`
- Purpose: public static callback hook invoked in editor/standalone resource registration flow.
- Output states:
  - `null`: no listener registered.
  - Delegate instance: invoked with the resource file list before backend registration.

### `void Initialize()`

- Purpose: starts the Spatial Adapter session, sets up input support, registers the post-frame callback, and begins scene/resource synchronization.
- Arguments: none.
- Output states:
  - Returns `void`.
  - If `EnableSpatialAdapter` is `false`, the method exits immediately and does nothing.
  - If native session initialization fails, the method logs an error.

## Public Runtime Fields

These fields are public mostly for serialization/project-settings control. They still affect runtime behavior.

### `EnableSpatialAdapter`

- Type: `bool`
- Meaning:
  - `true`: runtime initializes and synchronizes content.
  - `false`: `Initialize()` exits early and the adapter is effectively disabled.

### `EnableRendering`

- Type: `bool`
- Meaning:
  - `true`: editor rendering remains enabled.
  - `false`: runtime applies rendering-minimization behavior in supported environments.

### `autoCreateSpatialCamera`

- Type: `bool`
- Meaning:
  - `true`: runtime creates a fallback `SpatialCamera` if none exists.
  - `false`: no camera is auto-created.

### `disabledFeatures`

- Type: `SpatialAdapterFeatureSet`
- Meaning: bitmask of runtime features that should be disabled.

### `colliderLayerMask`

- Type: `LayerMask`
- Meaning: only objects on included layers have collision data synchronized.

### `exportFormat`

- Type: `ExportFormat`
- Meaning: exported asset format expected by the runtime for scenes and some renderer/skinned-mesh logic.

### `disableUnlitTonemapping`

- Type: `bool`
- Meaning:
  - `true`: runtime requests unlit tonemapping to be disabled.
  - `false`: leaves default tonemapping behavior in place.

### `autoAddUIHoverEffect`

- Type: `bool`
- Meaning:
  - `true`: runtime auto-adds `SpatialAdapterHoverEffect` to `Selectable` UI objects that do not already have it.
  - `false`: hover effect is only present when explicitly added.

### `resourceData`

- Type: `SpatialAdapterResourceData`
- Meaning: resource-registration data source for prefabs, textures, materials, shader graphs, and default camera configuration.

### `sceneData`

- Type: `SpatialAdapterSceneData`
- Meaning: current exported scene path and root objects used for traversal/registration.

### `void ClearAllManagers()`

- Purpose: clears all cached runtime managers and queued sync work.
- Arguments: none.
- Output states:
  - Returns `void`.
  - After the call, runtime caches for UIDs, renderers, particles, canvases, text, video, hover, shadow, and surface textures are reset.

### `void OpenSpatialCamera(SpatialCamera camera)`

- Purpose: queues opening a spatial window for the supplied `SpatialCamera`.
- Arguments:
  - `camera`: the camera component whose current configuration is sent to the backend.
- Output states:
  - Returns `void`.
  - Backend open request is queued, not executed immediately.

### `void SyncSpatialCamera(SpatialCamera camera)`

- Purpose: queues a root transform update for an already opened spatial camera window.
- Arguments:
  - `camera`: the spatial camera whose root transform should be synchronized.
- Output states:
  - Returns `void`.
  - Backend transform update is queued, not executed immediately.

### `void CloseSpatialCamera(SpatialCamera camera)`

- Purpose: queues closing the native window associated with the camera's current configuration.
- Arguments:
  - `camera`: the spatial camera to close.
- Output states:
  - Returns `void`.
  - Backend close request is queued, not executed immediately.

### `void SyncMesh(MeshFilter meshFilter, VertexAttributeFlags flags)`

- Purpose: serializes the selected vertex streams and index buffer of a Unity mesh and sends them to the backend.
- Arguments:
  - `meshFilter`: the mesh owner whose `sharedMesh` is synchronized.
  - `flags`: bitmask describing which vertex attributes to include.
- Output states:
  - Returns `void`.
  - If the GameObject has no runtime UID yet, the method logs an error and the mesh is not sent.

### `static int RegisterDynamicTexture(Texture2D texture)`

- Purpose: creates a backend texture resource directly from Unity `Texture2D` memory.
- Arguments:
  - `texture`: source texture. Supported formats are `RGBAFloat`, `RGBA64`, and `RGBA32`.
- Output states:
  - Returns backend texture asset ID, which is currently the Unity texture instance ID, on success.
  - Returns `-1` if the texture is null, has an unsupported format, or native texture creation fails.

### `static bool UpdateMaterialDynamicTexture(Material material, int textureAssetId, string parameterName = "_MainTex")`

- Purpose: associates a backend texture resource with a backend material resource.
- Arguments:
  - `material`: Unity material whose instance ID is used as the backend material asset ID.
  - `textureAssetId`: asset ID previously returned from `RegisterDynamicTexture()` or otherwise registered with the backend.
  - `parameterName`: intended material property name, but currently ignored by the implementation.
- Output states:
  - Returns `true` when the backend update succeeds.
  - Returns `false` when the backend update fails.

## Supporting Public Types

### `Transform3D`

- Purpose: simple local transform payload sent to native code.
- Fields:
  - `position`: local position.
  - `rotation`: local rotation.
  - `scale`: local scale.

### `Vec2i`

- Purpose: lightweight integer size struct used for texture dimensions.
- Constructor:
  - `Vec2i(int _x, int _y)`: stores width and height.

### `ExportFormat`

- Values:
  - `GLB`: export/runtime flow expects `.glb`.
  - `USDZ`: export/runtime flow expects `.usdz`.

### `SpatialAdapterFeatureSet`

- Values:
  - `None`: disables no features.
  - `DynamicMaterialParameterSync`: disables automatic material parameter synchronization when flagged in `disabledFeatures`.
  - `Placeholder`: spare flag retained to avoid Unity inspector issues with a single non-zero `[Flags]` value.

### `SpatialAdapterSceneData`

- Purpose: serialized scene payload used by the runtime to discover exported scene content.
- Fields:
  - `scenePath`: Unity scene asset path.
  - `exportedScenePath`: exported runtime asset path.
  - `rootObjects`: Unity root objects to register with the runtime.
- Method:
  - `CopyFrom(SpatialAdapterSceneData other)`: copies all public instance fields from `other`.

### `PathLookUp<T>`

- Purpose: maps a resource reference to its exported asset path.
- Fields:
  - `resource`: the Unity object or identifier to map.
  - `path`: exported asset path relative to the runtime's data root.
- Constructor:
  - `PathLookUp(T resource, string path)`: stores both values.

### `SpatialAdapterResourceData`

- Purpose: `ScriptableObject` describing resources that must be registered with the backend.
- Fields:
  - `PrefabLookUps`: prefab ID to exported asset path mappings.
  - `TextureLookUps`: texture object to exported asset path mappings.
  - `MaterialLookUps`: material object to exported asset path mappings.
  - `ShaderGraphLookUps`: shader graph/material IDs to exported asset path mappings.
  - `DefaultSpatialCameraConfiguration`: fallback `SpatialCameraConfiguration`.

### `PrefabId`

- Purpose: marks a prefab instance with the backend prefab identifier used for runtime instantiation/cloning.
- Property:
  - `PrefabIdentifier`: gets or sets the stored prefab ID.
- Delegate fields:
  - `OnPrefabInstantiated`: public `Action<PrefabId>` hook for prefab creation notifications.
  - `OnObjectDestroyed`: public `Action<GameObject>` hook for destroy notifications.

### `SpatialAdapterGameObjectTracker`

- Purpose: public tracking component attached to registered GameObjects.
- Fields:
  - `parent`: cached parent transform used to detect reparenting.
  - `uid`: backend entity UID.
  - `isValid`: whether the tracker still represents a live runtime entity.

### `PostFrameCallbackReceiver`

- Purpose: very-late `LateUpdate()` callback carrier used by the runtime.
- Field:
  - `postFrameCallback`: delegate invoked from `LateUpdate()`.

### `RegisterECSScope`

- Purpose: utility wrapper that temporarily activates a subtree while suppressing normal component enable/disable behavior.
- Constructor:
  - `RegisterECSScope(GameObject gameObject)`: begins the temporary registration scope.
- Method:
  - `Dispose()`: restores the original active/enabled state.

### `VertexAttributeFlags`

- Purpose: bitmask selecting which mesh vertex streams are sent in `SyncMesh()`.
- Values:
  - `NONE`
  - `POSITION`
  - `COLOR`
  - `UV0`
  - `UV1`
  - `TANGENT`
  - `NORMAL`
  - `JOINT_INDICES`
  - `JOINT_WEIGHTS`

### `VertexAttributes`

- Purpose: pointer bundle for mesh vertex arrays.
- Fields:
  - `positions`, `colors`, `uv0s`, `uv1s`, `tangents`, `normals`, `boneWeights`: native pointers to pinned arrays.
- Method:
  - `Clear()`: resets all pointers to `IntPtr.Zero`.

### `MeshData`

- Purpose: complete native mesh payload.
- Fields:
  - `vertexAttributes`: pinned vertex stream pointers.
  - `vertexAttributeFlags`: selected attribute mask.
  - `vertexCount`: number of vertices.
  - `indices`: pointer to pinned triangle index array.
  - `indexCount`: number of indices.
- Method:
  - `Clear()`: clears pointers, counts, and flags.
