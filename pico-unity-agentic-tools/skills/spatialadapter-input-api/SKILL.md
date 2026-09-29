---
name: spatialadapter-input-api
description: 'Use for concrete Spatial Input implementation in Spatial Adapter, PICO Spatial, or Unity Spatial: target selection, click, tap, pinch, drag, manipulation, colliders, EnhancedTouch mapping, SpatialInputSupport, SpatialInputDevice, and interaction IDs.'
license: 'Apache-2.0'
---

# SpatialAdapter Input API

## Overview

Use this skill when you need the Spatial Adapter input bridge between backend interaction data and Unity input systems. It covers interaction enums, state structs, target lookup, required collider setup for interactive objects, drag/manipulation patterns, and the custom `SpatialInputDevice` and `SpatialInputControl` types.

## Compatibility and Scope

Confirm Spatial mode from the saved `mode`, installed package, and scene evidence; ask if they conflict. Verify `ByteDance.PICO.SpatialAdapter`, Input System APIs, and the project's render pipeline before using the templates or creating URP materials. API explanations are read-only. Before scene changes, verify the running Editor and an available scene-editing tool; if unavailable, report the blocker and provide manual steps. Preserve existing scripts and configured materials, wait for successful compilation after script writes, register Undo, and save the intended scene after authorized changes.

## Trigger Keywords

- `Spatial Adapter`
- `PICO Spatial`
- `Unity Spatial`
- `SpatialInputSupport`
- `Spatial Input`
- `IndirectPinch`
- target selection
- click, tap, or pinch
- drag or manipulation
- target collider

## When to Use

- Use when converting Spatial Adapter interaction data into idiomatic Unity `EnhancedTouch.Touch` or custom Input System flows.
- Use when reading or mutating `SpatialInputState`.
- Use when mapping `touchId` values to Spatial Adapter interaction slots.
- Use when routing interaction logic based on the currently hit `GameObject`.
- Use when handling click, tap, pinch, or target-selection interactions.
- Use when deciding what collider an interactable GameObject should have for Spatial Input.
- Use when a user wants to drag or manipulate GameObjects with Spatial Adapter input.
- Use when debugging primary versus secondary spatial input device state.

## Quick Reference

- `InteractionType`: `Touch`, `Pinch`, `IndirectPinch`.
- `SpatialInputSupport.GetTargetObject(int)`: returns the currently targeted `GameObject` for an interaction slot.
- `SpatialInputSupport.GetInputState(Touch)`: returns a copy of the mapped spatial input state.
- `SpatialInputSupport.GetInputStateReference(Touch)`: returns a mutable reference to the stored state.
- `SpatialInputDevice`: custom Unity `InputDevice` with `primary` and `secondary` controls.
- `SpatialInputDevice.Initialize()`: registers custom layouts before scene load in player builds.
- `SpatialInputState`: value type carrying device pose, phase, positions, interaction ID, and target object lookup.
- If a GameObject handles Spatial Input in its scripts, that GameObject must also have a `Collider` so it can be targeted.
- Match collider type to the visual mesh shape when possible:
  - cubic or box-like meshes: prefer `BoxCollider`, or `SphereCollider` when a rounded approximation is acceptable
  - elongated or capsule-like meshes: prefer `CapsuleCollider`
  - round meshes: prefer `SphereCollider`
- Prefer the simplest collider that matches the object shape closely enough for reliable interaction.
- For drag/manipulation scenarios, use the sample pattern from `ManipulationDemo`:
  - first search the project for `PieceSelectionBehavior.cs` and `ManipulationInputManager.cs`
  - if both scripts already exist, add `PieceSelectionBehavior` to each manipulative GameObject, create a yellow Material using the `Universal Render Pipeline/Lit` shader, assign it to that object's `PieceSelectionBehavior.selectedMaterial`, and ensure the scene has one active `ManipulationInputManager`
  - if either script is missing, do not pretend the component can be attached anyway; first import the sample scripts or create project-local equivalents with the same responsibilities, let Unity compile, and then attach `PieceSelectionBehavior`
  - let `ManipulationInputManager` read `SpatialInputSupport.GetInputState(touch)` and drive the selected object
- `PieceSelectionBehavior` is the per-object hook for manipulable pieces. `ManipulationInputManager` is the shared manager that performs the actual selection and movement logic.
- In the lighter custom pattern, `PieceSelectionBehavior` does not require a `Rigidbody`; manipulable objects still need a suitable `Collider`, and `Rigidbody` should only be added when the project specifically needs physics behavior.
- After attaching `PieceSelectionBehavior`, create a yellow URP Lit material and assign it to `selectedMaterial` so selected objects have visible feedback.

## Manipulation Fallback

- A Unity component cannot be added to a GameObject unless the backing `MonoBehaviour` script exists in the project and compiles successfully.
- If the project does not contain `PieceSelectionBehavior.cs`, create that script first, wait for Unity to recompile, and only then add the `PieceSelectionBehavior` component to the target GameObject.
- If the project does not contain `ManipulationInputManager.cs`, create that script too and add one manager instance to the scene before expecting manipulation to work.
- The fallback implementation should preserve the same division of responsibility:
  - `PieceSelectionBehavior`: per-object selection state and optional visual feedback
  - `ManipulationInputManager`: shared scene manager that reads `SpatialInputSupport.GetInputState(touch)`, tracks the selected object by `interactionId`, and moves it during drag
- Minimum object requirements for the fallback path: `Collider` and `PieceSelectionBehavior`.
- `Rigidbody` is optional in the fallback path and should not be required by default when the manager directly updates the transform.
- After adding `PieceSelectionBehavior`, also create a yellow Material with the `Universal Render Pipeline/Lit` shader and assign it to the component's `selectedMaterial` field.
- If the user only wants simple tap or pinch reactions rather than drag/manipulation, prefer a smaller custom interaction script instead of generating the full manipulation pattern.

## Fallback Templates

- If the sample scripts are absent, generate both scripts before trying to add the component in Unity.
- Place them in a normal runtime scripts folder such as `Assets/Scripts/SpatialAdapterInput/`.
- After Unity recompiles successfully, add `PieceSelectionBehavior` to each manipulable GameObject, create a yellow Material using the `Universal Render Pipeline/Lit` shader, assign it to `selectedMaterial`, and create one scene object with `ManipulationInputManager`.
- A good default asset pattern is to save a material such as `Assets/Materials/<ObjectName>Selected.mat`, set its shader to `Universal Render Pipeline/Lit`, and set its base color to yellow.

`PieceSelectionBehavior.cs`

```csharp
using UnityEngine;

public class PieceSelectionBehavior : MonoBehaviour
{
    [SerializeField] Material selectedMaterial;

    MeshRenderer m_MeshRenderer;
    Material m_DefaultMaterial;

    public int SelectingPointer { get; private set; } = ManipulationInputManager.Deselected;

    void Awake()
    {
        m_MeshRenderer = GetComponent<MeshRenderer>();

        if (m_MeshRenderer != null)
            m_DefaultMaterial = m_MeshRenderer.sharedMaterial;
    }

    public void SetSelected(int pointer)
    {
        bool isSelected = pointer != ManipulationInputManager.Deselected;
        SelectingPointer = pointer;

        if (m_MeshRenderer != null && selectedMaterial != null)
            m_MeshRenderer.material = isSelected ? selectedMaterial : m_DefaultMaterial;
    }
}
```

`ManipulationInputManager.cs`

```csharp
using System.Collections.Generic;
using ByteDance.PICO.SpatialAdapter;
using UnityEngine;
using UnityEngine.InputSystem.EnhancedTouch;
using Touch = UnityEngine.InputSystem.EnhancedTouch.Touch;
using TouchPhase = UnityEngine.InputSystem.TouchPhase;

public class ManipulationInputManager : MonoBehaviour
{
    struct Selection
    {
        public PieceSelectionBehavior piece;
        public Vector3 positionOffset;
        public Quaternion rotationOffset;
    }

    public const int Deselected = -1;

    readonly Dictionary<int, Selection> m_CurrentSelections = new();

    void OnEnable()
    {
        EnhancedTouchSupport.Enable();
    }

    void OnDisable()
    {
        foreach (var selection in m_CurrentSelections.Values)
        {
            if (selection.piece != null)
                selection.piece.SetSelected(Deselected);
        }

        m_CurrentSelections.Clear();
        EnhancedTouchSupport.Disable();
    }

    void Update()
    {
        foreach (var touch in Touch.activeTouches)
        {
            SpatialInputState inputState = SpatialInputSupport.GetInputState(touch);
            int interactionId = inputState.interactionId;

            switch (inputState.phase)
            {
                case TouchPhase.Began:
                    TryBeginSelection(inputState, interactionId);
                    break;
                case TouchPhase.Moved:
                    UpdateSelectionPose(inputState, interactionId);
                    break;
                case TouchPhase.None:
                case TouchPhase.Ended:
                case TouchPhase.Canceled:
                    Deselect(interactionId);
                    break;
            }
        }
    }

    public static bool CanSelectTarget(bool isTouchInteraction, GameObject targetObject, PieceSelectionBehavior piece)
    {
        return !isTouchInteraction
            && targetObject != null
            && piece != null
            && piece.SelectingPointer == Deselected;
    }

    void TryBeginSelection(SpatialInputState inputState, int interactionId)
    {
        GameObject targetObject = inputState.targetObject;
        PieceSelectionBehavior piece = targetObject != null
            ? targetObject.GetComponent<PieceSelectionBehavior>()
            : null;

        if (!CanSelectTarget(inputState.type == InteractionType.Touch, targetObject, piece))
            return;

        Transform pieceTransform = piece.transform;
        Quaternion inverseDeviceRotation = Quaternion.Inverse(inputState.deviceRotation);

        if (m_CurrentSelections.TryGetValue(interactionId, out Selection existingSelection) && existingSelection.piece != null)
            existingSelection.piece.SetSelected(Deselected);

        piece.SetSelected(interactionId);
        m_CurrentSelections[interactionId] = new Selection
        {
            piece = piece,
            rotationOffset = inverseDeviceRotation * pieceTransform.rotation,
            positionOffset = inverseDeviceRotation * (pieceTransform.position - inputState.currentPosition)
        };
    }

    void UpdateSelectionPose(SpatialInputState inputState, int interactionId)
    {
        if (!m_CurrentSelections.TryGetValue(interactionId, out Selection selection) || selection.piece == null)
            return;

        Quaternion deviceRotation = inputState.deviceRotation;
        Vector3 position = inputState.currentPosition + deviceRotation * selection.positionOffset;
        Quaternion rotation = deviceRotation * selection.rotationOffset;
        selection.piece.transform.SetPositionAndRotation(position, rotation);
    }

    void Deselect(int interactionId)
    {
        if (!m_CurrentSelections.TryGetValue(interactionId, out Selection selection))
            return;

        if (selection.piece != null)
            selection.piece.SetSelected(Deselected);

        m_CurrentSelections.Remove(interactionId);
    }
}
```

- These templates are intentionally minimal and are suitable when the project lacks the sample `ManipulationDemo` scripts.
- If the project already includes richer versions of these scripts, prefer reusing those instead of generating duplicates with the same class names.

## Reference

Read [reference.md](reference.md) for enum values, field layouts, control definitions, and Unity Input System integration details.

## Common Mistakes

- Mixing zero-based Spatial Adapter `interactionId` values with one-based Unity `touchId` values.
- Mutating a copied `SpatialInputState` and expecting internal runtime state to change. Use the reference-returning API when mutation is required.
- Reimplementing target-object lookup instead of using `SpatialInputSupport.GetTargetObject()`.
- Handling Spatial Input on a GameObject that has no `Collider`, which makes the object untargetable.
- Using a collider shape that does not match the object's mesh closely enough, leading to confusing hit results.
- Adding custom drag logic directly to each object when the `ManipulationInputManager` plus `PieceSelectionBehavior` sample pattern already fits the requirement.
- Trying to add `PieceSelectionBehavior` when the project does not contain the backing script yet. Create or import the script first so Unity can compile the component type.
- Adding `PieceSelectionBehavior` to an object without also having a `ManipulationInputManager` active in the scene.
- Adding `PieceSelectionBehavior` but forgetting to create and assign a yellow `Universal Render Pipeline/Lit` material to `selectedMaterial`, which leaves selection feedback invisible.
- Keeping outdated `Rigidbody` and `isKinematic` assumptions in a transform-driven manipulation setup where the lighter pattern does not need them.
