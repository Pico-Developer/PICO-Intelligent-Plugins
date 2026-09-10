# Components API

This file documents public component-facing APIs for text, video, collision, hover, shadow, and canvas sorting.

## Text

### `TextJustification`

- `Left`
  - Left-aligns text in the native background container.
- `Center`
  - Centers text.
- `Right`
  - Right-aligns text.
- `Justified`
  - Exposed in the API, but editor mock behavior currently treats it like centered text.
- `None`
  - Exposed in the API, but editor mock behavior currently treats it like centered text.

### `NativeTextData`

- Purpose: payload sent by `SpatialAdapterRuntime.UpdateTextComponent()`.
- Fields:
  - `text`: string content to render.
  - `textColor`: font color.
  - `textSize`: font size.
  - `insets`: internal padding rect.
  - `justification`: horizontal alignment mode.
  - `backgroundColor`: background fill color.
  - `backgroundSize`: background size in meters.
  - `backgroundCornerRadius`: rounded-corner radius in meters.

### `SpatialAdapterNativeText`

- Role: Unity component that renders text via the native backend instead of Unity mesh/UI text.

#### Settable Properties

- `Text`
  - Type: `string`
  - Meaning: updates the displayed string and marks the component dirty.
- `TextSize`
  - Type: `int`
  - Meaning: updates font size and marks the component dirty.
- `TextColor`
  - Type: `Color`
  - Meaning: updates the text color and marks the component dirty.
- `Justification`
  - Type: `TextJustification`
  - Meaning: updates horizontal alignment and marks the component dirty.
- `BackgroundColor`
  - Type: `Color`
  - Meaning: updates the background color and marks the component dirty.
- `BackgroundSize`
  - Type: `Vector2`
  - Meaning: updates native background width and height in meters.
- `BackgroundCornerRadius`
  - Type: `int`
  - Meaning: updates corner radius and marks the component dirty.
  - Note: backing storage is a `float`, but the public property accepts `int`.

#### Output Behavior

- Property writes do not push immediately.
- The component marks itself dirty and syncs during the runtime's later frame update.

### `MockTextComponent`

- Purpose: editor-only helper component used by the native text mock path.
- Field:
  - `nativeText`: associated `SpatialAdapterNativeText`.

## Video

### `VideoPlaybackMode`

- `Play`
  - Start playback.
- `Pause`
  - Pause playback.
- `Resume`
  - Resume playback.
- `Stop`
  - Stop playback.
- `None`
  - Keep current file/settings without issuing a new playback command.

### `NativeVideoData`

- Purpose: payload sent by `SpatialAdapterRuntime.UpdateVideoPlayerComponent()`.
- Fields:
  - `fileName`: source file name, expected under `StreamingAssets/Video`.
  - `playbackMode`: requested playback action.
  - `looping`: `1` for loop, `0` for no loop.
  - `volume`: playback volume scalar.
  - `speed`: playback speed scalar.

### `SpatialAdapterVideoComponent`

- Role: native-video playback component for a GameObject synchronized to the backend.

#### Settable Properties

- `Path`
  - Type: `string`
  - Meaning: sets the video file name/path string sent to native code.
- `PlayOnAwake`
  - Type: `bool`
  - Meaning: controls whether `Awake()` starts the component in `Play` or `None`.
- `Looping`
  - Type: `bool`
  - Meaning: toggles loop playback.
- `Volume`
  - Type: `float`
  - Meaning: sets playback volume.
- `Speed`
  - Type: `float`
  - Meaning: sets playback rate.

#### Playback Methods

##### `void Play()`

- Purpose: requests playback start.
- Arguments: none.
- Output states:
  - Returns `void`.
  - Sets internal playback mode to `Play` and marks dirty.

##### `void Stop()`

- Purpose: requests playback stop.
- Arguments: none.
- Output states:
  - Returns `void`.
  - Sets internal playback mode to `Stop` and marks dirty.

##### `void Pause()`

- Purpose: requests playback pause.
- Arguments: none.
- Output states:
  - Returns `void`.
  - Sets internal playback mode to `Pause` and marks dirty.

##### `void Resume()`

- Purpose: requests resume after a pause.
- Arguments: none.
- Output states:
  - Returns `void`.
  - Sets internal playback mode to `Resume` and marks dirty.

##### `void PlaymodeNone()`

- Purpose: clears any active playback command.
- Arguments: none.
- Output states:
  - Returns `void`.
  - Sets internal playback mode to `None` and marks dirty.

#### Property: `Data`

- Type: `ref NativeVideoData`
- Purpose: materializes the current payload that will be sent to native code.
- Output states:
  - Returns a mutable reference to the internal `NativeVideoData`.
  - Clears the dirty flag when accessed.

## Surface Texture Video

### `VideoDimensionMode`

- `VIDEO_2D`
  - Standard monoscopic video.
- `TOP_DOWN_3D_VIDEO`
  - Stereo top-down layout.
- `SIDE_BY_SIDE_3D_VIDEO`
  - Stereo side-by-side layout.
- `MULTIPLE_VIEW`
  - Multi-view layout.

### `SurfaceTextureVideoData`

- Purpose: payload sent by `SpatialAdapterRuntime.UpdateSurfaceTextureVideoComponent()`.
- Fields:
  - `textureAssetId`: backend texture resource receiving decoded video frames.
  - `mode`: stereo/video layout mode.

### `SurfaceTextureVideoComponent`

- Role: component for videos rendered into a backend surface texture.

#### Properties

- `TextureAssetId`
  - Type: `int`
  - Meaning: texture resource ID that the backend video decoder should target.
- `VideoMode`
  - Type: `VideoDimensionMode`
  - Meaning: selects mono/stereo/multiview layout.
- `FlipXOrientation`
  - Type: `bool`
  - Meaning: flips local X scale one time when the component updates while dirty.
- `FlipYOrientation`
  - Type: `bool`
  - Meaning: flips local Y scale one time when the component updates while dirty.

#### Output Behavior

- Changing `TextureAssetId` or `VideoMode` marks the component dirty for backend sync.
- Flipping orientation changes Unity transform scale locally and does not directly alter the native data payload.

## Hover And Shadow

### `SpatialAdapterGroundingShadow`

- Role: marker/sync component that enables a grounding shadow on the backend entity.
- Public API:
  - No public properties or methods.
- Output behavior:
  - When enabled, it registers itself with `SpatialAdapterRuntime`.
  - When disabled, it deregisters itself.

### `SpatialAdapterHoverEffect`

- Role: marker/sync component that enables hover feedback on the backend entity.
- Public API:
  - No public properties or methods.
- Output behavior:
  - When enabled, it registers itself with `SpatialAdapterRuntime`.
  - When disabled, it deregisters itself.

## Collision

### `CollisionMode`

- `DEFAULT`
  - Default collision handling.
- `TRIGGER`
  - Trigger-style non-solid interaction.
- `COLLIDING`
  - Colliding/solid interaction mode.

### `CollisionShapeType`

- `BOX`
- `SPHERE`
- `CAPSULE`
- `MESH`

### `ColliderData`

- Purpose: one backend collision shape descriptor.

#### Fields

- `type`
  - Type: `CollisionShapeType`
  - Meaning: collider shape category.
- `size`
  - Type: `Vector3`
  - Meaning:
    - box: dimensions
    - sphere: radius copied across XYZ
    - capsule: `(height, radius, direction)`
    - mesh: placeholder `Vector3.one`
- `center`
  - Type: `Vector3`
  - Meaning: local collider center.
- `rotation`
  - Type: `Quaternion`
  - Meaning: local collider orientation. Capsules rotate based on axis direction.
- `isConvexMesh`
  - Type: `byte`
  - Meaning: `1` for convex mesh colliders, `0` otherwise.

#### Constructors

##### `ColliderData(BoxCollider collider)`

- Purpose: converts a Unity box collider into backend payload.
- Arguments:
  - `collider`: source collider.
- Output states:
  - Returns a `ColliderData` with `type = BOX`.

##### `ColliderData(RectTransform transform)`

- Purpose: creates a thin box collider from a UI rect.
- Arguments:
  - `transform`: source UI rect transform.
- Output states:
  - Returns a `ColliderData` with `type = BOX` and tiny Z thickness.

##### `ColliderData(SphereCollider collider)`

- Purpose: converts a Unity sphere collider.
- Arguments:
  - `collider`: source collider.
- Output states:
  - Returns a `ColliderData` with `type = SPHERE`.

##### `ColliderData(CapsuleCollider collider)`

- Purpose: converts a Unity capsule collider.
- Arguments:
  - `collider`: source collider.
- Output states:
  - Returns a `ColliderData` with `type = CAPSULE`.

##### `ColliderData(MeshCollider collider)`

- Purpose: converts a Unity mesh collider.
- Arguments:
  - `collider`: source collider.
- Output states:
  - Returns a `ColliderData` with `type = MESH`.

#### `static ColliderData[] GetColliderData(GameObject obj)`

- Purpose: gathers all supported `Collider` components on a GameObject and converts them into backend payloads.
- Arguments:
  - `obj`: source GameObject.
- Output states:
  - Returns an array of converted `ColliderData`.
  - Unsupported collider types are ignored.

## Canvas Sorting

### `HierarchicalLayerSortingData`

- Purpose: canvas sorting metadata synchronized to the backend.
- Fields:
  - `sortingLayer`: sorting layer ID cast to `sbyte`.
  - `orderInLayer`: sorting order cast to `short`.
  - `wasCreated`: internal state used to force the first sync.

### `HierarchicalLayerSortingData(Canvas canvas)`

- Purpose: initializes sorting metadata from a Unity canvas.
- Arguments:
  - `canvas`: source canvas.
- Output states:
  - Returns a new struct seeded from the canvas sorting layer and order.

### `bool Update(Canvas canvas)`

- Purpose: refreshes stored sorting values and reports whether backend sync is needed.
- Arguments:
  - `canvas`: current canvas state.
- Output states:
  - Returns `true` if sorting layer/order changed or the component has not been synced before.
  - Returns `false` if nothing changed.
