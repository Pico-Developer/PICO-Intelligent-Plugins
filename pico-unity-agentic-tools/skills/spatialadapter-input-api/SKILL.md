---
name: spatialadapter-input-api
description: Use for concrete Spatial Input implementation in Spatial Adapter, including target selection, click, tap, pinch, drag, manipulation, target colliders, EnhancedTouch mapping, SpatialInputSupport, SpatialInputDevice, and interaction IDs. Platform names alone do not activate this skill.
license: 'Apache-2.0'
---

# SpatialAdapter Input API

## When NOT to Use

- Native text, video, or visual components — use `spatialadapter-components-api`
- Camera or window lifecycle — use `spatialadapter-camera-window-api`
- Scene setup or SpatialCamera presence — use `spatialadapter-scene-setup`

## Overview

Use this skill when you need the Spatial Adapter input bridge between backend interaction data and Unity input systems. It covers interaction enums, state structs, target lookup, required collider setup for interactive objects, drag/manipulation patterns, and the custom `SpatialInputDevice` and `SpatialInputControl` types.

## Compatibility and Scope

Confirm Spatial mode from the saved `mode`, installed package, and scene evidence; ask if they conflict. Verify `ByteDance.PICO.SpatialAdapter`, Input System APIs, and the project's render pipeline before using the templates or creating a fallback selection material. API explanations are read-only. Before scene changes, verify the running Editor and an available scene-editing tool; if unavailable, report the blocker and provide manual steps. Preserve existing scripts and configured materials, wait for successful compilation after script writes, register Undo, and save the intended scene after authorized changes.

## Trigger Keywords

- `SpatialInputSupport`
- `Spatial Input`
- `IndirectPinch`
- target selection, click, tap, or pinch in Spatial Input
- drag or manipulate objects with Spatial Input
- Spatial Input target colliders and EnhancedTouch mapping

Platform names alone do not activate this skill. Require a Spatial Input API or interaction task. Ordinary Unity input or collider work without a Spatial Adapter integration remains with generic Unity skills; backend `ColliderData` conversion belongs to [spatialadapter-components-api](../spatialadapter-components-api/SKILL.md).

## When to Use

- Use when converting Spatial Adapter interaction data into idiomatic Unity `EnhancedTouch.Touch` or custom Input System flows.
- Use when reading or mutating `SpatialInputState`.
- Use when mapping `touchId` values to Spatial Adapter interaction slots.
- Use when routing interaction logic based on the currently hit `GameObject`.
- Use when handling click, tap, pinch, or target-selection interactions through Spatial Input.
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
  - if both scripts already exist, add `PieceSelectionBehavior` to each manipulative GameObject, preserve any assigned `PieceSelectionBehavior.selectedMaterial`, create a pipeline-compatible yellow selection material only when that field is empty, and ensure the scene has one active `ManipulationInputManager`
  - if either script is missing, do not pretend the component can be attached anyway; first import the sample scripts or create project-local equivalents with the same responsibilities, let Unity compile, and then attach `PieceSelectionBehavior`
  - let `ManipulationInputManager` read `SpatialInputSupport.GetInputState(touch)` and drive the selected object
- `PieceSelectionBehavior` is the per-object hook for manipulable pieces. `ManipulationInputManager` is the shared manager that performs the actual selection and movement logic.
- In the lighter custom pattern, `PieceSelectionBehavior` does not require a `Rigidbody`; manipulable objects still need a suitable `Collider`, and `Rigidbody` should only be added when the project specifically needs physics behavior.
- After attaching `PieceSelectionBehavior`, follow the guarded selection-material flow below so selected objects have visible feedback without replacing project configuration.

## Selection Material Fallback

- Preserve a non-null `selectedMaterial`; an existing project-configured material is authoritative and must not be replaced automatically.
- Only when `selectedMaterial` is null, determine the effective render pipeline with `QualitySettings.renderPipeline ?? GraphicsSettings.defaultRenderPipeline` before choosing a shader.
- Choose the fallback shader by the detected pipeline:
  - Built-in Render Pipeline (the effective pipeline asset is null): use `Standard`.
  - Universal Render Pipeline (`UniversalRenderPipelineAsset`): use `Universal Render Pipeline/Lit`.
  - High Definition Render Pipeline (`HDRenderPipelineAsset`): use `HDRP/Lit`.
- Detect URP and HDRP by the pipeline asset type or full type name so the fallback script does not require compile-time references to optional render-pipeline assemblies.
- For a custom or unknown SRP, stop and ask the user to provide a compatible material or shader; do not guess a shader.
- If `Shader.Find` returns null for the selected shader, stop and report the missing shader instead of creating a material with an invalid shader.
- Create a yellow material asset and assign it to `selectedMaterial` only after the pipeline and shader checks pass. Register the assignment with Undo and save the intended scene and material asset.

## Manipulation Fallback

- A Unity component cannot be added to a GameObject unless the backing `MonoBehaviour` script exists in the project and compiles successfully.
- If the project does not contain `PieceSelectionBehavior.cs`, create that script first, wait for Unity to recompile, and only then add the `PieceSelectionBehavior` component to the target GameObject.
- If the project does not contain `ManipulationInputManager.cs`, create that script too and add one manager instance to the scene before expecting manipulation to work.
- The fallback implementation should preserve the same division of responsibility:
  - `PieceSelectionBehavior`: per-object selection state and optional visual feedback
  - `ManipulationInputManager`: shared scene manager that reads `SpatialInputSupport.GetInputState(touch)`, tracks the selected object by `interactionId`, and moves it during drag
- Minimum object requirements for the fallback path: `Collider` and `PieceSelectionBehavior`.
- `Rigidbody` is optional in the fallback path and should not be required by default when the manager directly updates the transform.
- After adding `PieceSelectionBehavior`, preserve an assigned selection material or follow [Selection Material Fallback](#selection-material-fallback) when the field is empty.
- If the user only wants simple tap or pinch reactions rather than drag/manipulation, prefer a smaller custom interaction script instead of generating the full manipulation pattern.

## Fallback Templates

- If the sample scripts are absent, generate both scripts before trying to add the component in Unity.
- Place them in a normal runtime scripts folder such as `Assets/Scripts/SpatialAdapterInput/`.
- After Unity recompiles successfully, add `PieceSelectionBehavior` to each manipulable GameObject, apply the guarded selection-material flow above, and create one scene object with `ManipulationInputManager`.
- When a new fallback is required, a good default asset pattern is `Assets/Materials/<ObjectName>Selected.mat` with the pipeline-compatible shader and a yellow base color.

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
- Replacing an existing `selectedMaterial`, or creating a URP material in a Built-in, HDRP, or unknown-SRP project.
- Continuing after pipeline detection is inconclusive or `Shader.Find` returns null, which can create a broken selection material.
- Keeping outdated `Rigidbody` and `isKinematic` assumptions in a transform-driven manipulation setup where the lighter pattern does not need them.
