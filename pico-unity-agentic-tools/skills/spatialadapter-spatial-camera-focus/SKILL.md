---
name: spatialadapter-spatial-camera-focus
description: Use when a Spatial Adapter, PICO Spatial, or Unity Spatial scene should keep a target inside SpatialCamera bounds or follow it with SpatialCamera.
license: 'Apache-2.0'
---

# Spatial Adapter Spatial Camera Focus

## Overview

Use this skill when the user asks to focus the Spatial Adapter view on a target object, or when a target should remain inside the `SpatialCamera` bounds while moving. Prefer the project `SpatialCameraBoundsFollower` script when it exists.

## Compatibility and Scope

Confirm Spatial mode from the saved `mode`, installed package, and scene evidence; ask if they conflict. Verify the installed SpatialCamera API before using the template. Inspect existing scripts and components without overwriting them. Before scene changes, verify the running Editor and an available scene-editing tool; if unavailable, report the blocker and provide manual steps. After creating a script, wait for successful Unity compilation before attaching it. Reuse an existing follower, preserve Undo, and save the intended scene after authorized changes.

## Trigger Keywords

- `Spatial Adapter`
- `PICO Spatial`
- `Unity Spatial`
- `SpatialCamera`
- `SpatialCameraBoundsFollower`

## When to Use

- Use when the user asks to focus view on a scene object.
- Use when a target object can move outside the `SpatialCamera` bounds.
- Use when the `SpatialCamera` should adjust its position so the target remains visible.
- Use when configuring an existing `SpatialCamera` for target-following behavior.

## Setup

1. Inspect the active scene for an existing `SpatialCamera` component.
2. If no `SpatialCamera` exists, follow [spatialadapter-scene-setup](../spatialadapter-scene-setup/SKILL.md) first to create one.
3. Find the requested target object in the scene.
4. Check whether `SpatialCameraBoundsFollower` exists in the Unity project.
5. If `SpatialCameraBoundsFollower` is missing, create it from the fallback script template in this skill before attaching it.
6. Reuse a `SpatialCameraBoundsFollower` already on the camera; otherwise add it to the same GameObject as `SpatialCamera` after compilation succeeds.
7. Assign the requested target object to the follower `target` field or `Target` property.
8. Configure the follower:
   - `fallbackDimensions`: match the intended `SpatialCamera.Dimensions` if direct reflection cannot read dimensions.
   - `margin`: use a positive boundary margin such as `0.25`.
   - `followSpeed`: use a smooth follow speed such as `6`.
   - `followVertical`: keep `false` unless the target must be followed vertically.

## Behavior Contract

- The follower should not move the `SpatialCamera` while the target remains within the camera bounds minus `margin`.
- If the target exits the horizontal bounds, the `SpatialCamera` should shift on X and/or Z so the target is back inside the bounds.
- If `followVertical` is `true`, the same rule also applies to Y.
- The follower should run in `LateUpdate` so it reacts after target movement for the frame.

## Fallback Script Template

If the user project does not already contain `SpatialCameraBoundsFollower`, create `Assets/Scripts/SpatialCameraBoundsFollower.cs` with this implementation after verifying the camera uses world-aligned axes and unit world scale. This minimal template follows the target pivot, not its full renderer bounds; adapt the coordinate conversion for rotated or scaled cameras rather than applying world-axis bounds unchanged. Positive `followSpeed` eases toward the corrected position and may leave the target outside the margin temporarily; use `followSpeed <= 0` when immediate pivot containment is required.

```csharp
using System;
using UnityEngine;

public class SpatialCameraBoundsFollower : MonoBehaviour
{
    [SerializeField] Transform target;
    [SerializeField] Vector3 fallbackDimensions = new(4.05f, 1.8f, 3.5f);
    [SerializeField] float margin = 0.25f;
    [SerializeField] float followSpeed = 6f;
    [SerializeField] bool followVertical;

    Component m_SpatialCamera;
    Type m_SpatialCameraType;

    public Transform Target
    {
        get => target;
        set => target = value;
    }

    void Awake()
    {
        m_SpatialCamera = GetComponent("ByteDance.PICO.SpatialAdapter.SpatialCamera");
        m_SpatialCameraType = m_SpatialCamera != null ? m_SpatialCamera.GetType() : null;
    }

    void LateUpdate()
    {
        if (target == null)
            return;

        Vector3 dimensions = GetSpatialCameraDimensions();
        Vector3 desiredPosition = ComputeAdjustedCameraPosition(
            transform.position,
            target.position,
            dimensions,
            margin,
            followVertical);

        float interpolation = followSpeed <= 0f ? 1f : 1f - Mathf.Exp(-followSpeed * Time.deltaTime);
        transform.position = Vector3.Lerp(transform.position, desiredPosition, interpolation);
    }

    Vector3 GetSpatialCameraDimensions()
    {
        if (m_SpatialCamera == null || m_SpatialCameraType == null)
            return fallbackDimensions;

        var property = m_SpatialCameraType.GetProperty("Dimensions");
        if (property != null && property.PropertyType == typeof(Vector3))
            return (Vector3)property.GetValue(m_SpatialCamera);

        var field = m_SpatialCameraType.GetField("Dimensions");
        if (field != null && field.FieldType == typeof(Vector3))
            return (Vector3)field.GetValue(m_SpatialCamera);

        return fallbackDimensions;
    }

    public static Vector3 ComputeAdjustedCameraPosition(
        Vector3 cameraPosition,
        Vector3 targetPosition,
        Vector3 dimensions,
        float margin,
        bool followVertical)
    {
        Vector3 halfExtents = dimensions * 0.5f;
        halfExtents.x = Mathf.Max(0f, halfExtents.x - margin);
        halfExtents.y = Mathf.Max(0f, halfExtents.y - margin);
        halfExtents.z = Mathf.Max(0f, halfExtents.z - margin);

        Vector3 offset = targetPosition - cameraPosition;
        Vector3 adjustedPosition = cameraPosition;
        adjustedPosition.x += CalculateAxisShift(offset.x, halfExtents.x);
        adjustedPosition.z += CalculateAxisShift(offset.z, halfExtents.z);

        if (followVertical)
            adjustedPosition.y += CalculateAxisShift(offset.y, halfExtents.y);

        return adjustedPosition;
    }

    static float CalculateAxisShift(float offset, float halfExtent)
    {
        if (offset > halfExtent)
            return offset - halfExtent;
        if (offset < -halfExtent)
            return offset + halfExtent;
        return 0f;
    }
}
```

## Verification

- Confirm exactly one `SpatialCameraBoundsFollower` is attached to the `SpatialCamera` GameObject.
- If the script was created from the template, confirm Unity compiles it without errors.
- Confirm the follower target references the requested scene object.
- Confirm the `SpatialCamera` dimensions or `fallbackDimensions` cover the intended play area.
- Test or inspect that a target outside bounds produces an adjusted camera position.
- Save the scene after configuration.

## Common Mistakes

- Adding the follower to the target object instead of the `SpatialCamera` GameObject.
- Forgetting to assign the target, causing the follower to do nothing.
- Leaving `fallbackDimensions` smaller than the actual intended `SpatialCamera.Dimensions`.
- Enabling `followVertical` unnecessarily, which can make the spatial view bob up and down.
