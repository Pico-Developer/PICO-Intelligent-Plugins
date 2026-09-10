# Input API

This file documents the public input and interaction APIs under `ByteDance.PICO.SpatialAdapter`.

## Interaction Enums And Data

### `InteractionType`

- `Touch`
  - Direct touch-like interaction.
- `Pinch`
  - Pinch interaction.
- `IndirectPinch`
  - Indirect pinch interaction.

### `FrameAnchorData`

- Purpose: public anchor-change payload container.
- Fields:
  - `addedAnchorCount`: number of newly added anchors.
  - `addedAnchors`: pointer to the added-anchor buffer.
  - `updatedAnchorCount`: number of updated anchors.
  - `updatedAnchors`: pointer to the updated-anchor buffer.
  - `removedAnchorCount`: number of removed anchors.
  - `removedAnchors`: pointer to the removed-anchor buffer.

### `TrackableId`

- Purpose: public two-part identifier for tracked objects.
- Fields:
  - `subId1`: first half of the ID.
  - `subId2`: second half of the ID.

### `Handedness`

- `Invalid`
  - No valid handedness is known.
- `Left`
  - Left hand.
- `Right`
  - Right hand.

## `SpatialInputSupport`

### Role

- Static bridge between Spatial Adapter interaction data and Unity's Input System/EventSystem.
- Converts backend interaction data into:
  - `EnhancedTouch.Touch`
  - `SpatialInputDevice`
  - `PointerEventData` UI events

### `static GameObject GetTargetObject(int interactionId)`

- Purpose: returns the current target GameObject for a tracked interaction slot.
- Arguments:
  - `interactionId`: zero-based interaction slot index.
- Output states:
  - Target `GameObject` when one is currently associated with the interaction.
  - `null` when `interactionId < 0` or no valid target exists.

### `static SpatialInputState GetInputState(Touch touch)`

- Purpose: returns a copy of the spatial input state that corresponds to a Unity touch.
- Arguments:
  - `touch`: Unity `EnhancedTouch.Touch` whose `touchId` maps to a Spatial Adapter interaction slot.
- Output states:
  - Returns the current `SpatialInputState` value for `touch.touchId - 1`.

### `static ref SpatialInputState GetInputStateReference(Touch touch)`

- Purpose: returns a mutable reference to the same state used internally for the mapped touch.
- Arguments:
  - `touch`: Unity `EnhancedTouch.Touch` used to locate the interaction slot.
- Output states:
  - Returns a `ref SpatialInputState`.
  - Changes through the reference modify the stored input state directly.

## `SpatialInputControl`

### Role

- Custom Unity Input System control that exposes one `SpatialInputState` as sub-controls.

### Properties

- `devicePosition`
  - Type: `Vector3Control`
  - Meaning: device/controller/hand position for the interaction.
- `deviceRotation`
  - Type: `QuaternionControl`
  - Meaning: device/controller/hand rotation for the interaction.
- `type`
  - Type: `IntegerControl`
  - Meaning: encoded `InteractionType`.
- `phase`
  - Type: `TouchPhaseControl`
  - Meaning: current touch phase.
- `interactionId`
  - Type: `IntegerControl`
  - Meaning: interaction slot index.
- `currentPosition`
  - Type: `Vector3Control`
  - Meaning: current hit or pointer position.
- `startPosition`
  - Type: `Vector3Control`
  - Meaning: interaction start position.
- `deltaPosition`
  - Type: `Vector3Control`
  - Meaning: current minus start position.

### `SpatialInputState ReadUnprocessedValueFromState(void* statePtr)`

- Purpose: reads one `SpatialInputState` from an unmanaged state buffer.
- Arguments:
  - `statePtr`: pointer to the input state memory block.
- Output states:
  - Returns the decoded `SpatialInputState` value.

### `void WriteValueIntoState(SpatialInputState value, void* statePtr)`

- Purpose: writes one `SpatialInputState` into an unmanaged state buffer.
- Arguments:
  - `value`: state value to write.
  - `statePtr`: pointer to the destination state memory block.
- Output states:
  - Returns `void`.
  - The unmanaged state buffer is updated in place.

## `SpatialInputState`

### Role

- Public value type representing one active or inactive spatial interaction.

### Property: `format`

- Type: `FourCC`
- Purpose: identifies this state layout to Unity Input System.
- Output states:
  - Always returns `new('V', 'O', 'P', 'S')`.

### Fields And Computed Properties

- `devicePosition`
  - Type: `Vector3`
  - Meaning: device/controller/hand world position associated with the interaction.
- `deviceRotation`
  - Type: `Quaternion`
  - Meaning: device/controller/hand orientation.
- `typeId`
  - Type: `byte`
  - Meaning: raw stored interaction type.
- `phaseId`
  - Type: `byte`
  - Meaning: raw stored touch phase.
- `interactionId`
  - Type: `int`
  - Meaning: zero-based interaction slot.
- `type`
  - Type: `InteractionType`
  - Meaning: strongly typed wrapper over `typeId`.
- `phase`
  - Type: `TouchPhase`
  - Meaning: strongly typed wrapper over `phaseId`.
- `currentPosition`
  - Type: `Vector3`
  - Meaning: current position for the interaction.
- `startPosition`
  - Type: `Vector3`
  - Meaning: first recorded position for the interaction.
- `deltaPosition`
  - Type: `Vector3`
  - Meaning: `currentPosition - startPosition`.
- `targetObject`
  - Type: `GameObject`
  - Meaning: current target object resolved from `SpatialInputSupport`.
  - Output states:
    - Target `GameObject` when one is known.
    - `null` when no target is associated.

## `SpatialInputDevice`

### Role

- Custom Unity `InputDevice` exposing two `SpatialInputControl` children.

### Properties

- `primary`
  - Type: `SpatialInputControl`
  - Meaning: first interaction slot.
- `secondary`
  - Type: `SpatialInputControl`
  - Meaning: second interaction slot.

### `static void Initialize()`

- Purpose: forces static layout registration before scene load in player builds.
- Arguments: none.
- Output states:
  - Returns `void`.
  - Ensures Unity knows about `SpatialInputControl` and `SpatialInputDevice`.

## `SpatialInputDeviceState`

### Role

- Public input-state struct containing the primary and secondary spatial interactions.

### Property: `format`

- Type: `FourCC`
- Purpose: identifies this device state layout to Unity Input System.
- Output states:
  - Always returns `new('V', 'O', 'P', 'S')`.

### Fields

- `primary`
  - Type: `SpatialInputState`
  - Meaning: current state of the first interaction slot.
- `secondary`
  - Type: `SpatialInputState`
  - Meaning: current state of the second interaction slot.

## Agent Guidance

- Use Unity `EnhancedTouch.Touch` or the custom `SpatialInputDevice` when you want agent-generated gameplay/input code to remain idiomatic inside Unity.
- Use `SpatialInputSupport.GetTargetObject()` when interaction routing depends on the currently hit object.
- Treat `interactionId` as zero-based in Spatial Adapter code and `touchId` as one-based in Unity touch code. The runtime converts between them internally.
