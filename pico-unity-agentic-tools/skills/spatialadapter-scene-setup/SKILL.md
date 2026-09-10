---
name: spatialadapter-scene-setup
description: Use when setting up a Unity scene for Spatial Adapter, PICO Spatial, or Unity Spatial and the scene needs a SpatialCamera component.
license: 'Apache-2.0'
---

# SpatialAdapter Scene Setup

## Overview

Use this skill when preparing a Unity scene for `Spatial Adapter`, `PICO Spatial`, or `Unity Spatial`. The first setup check is whether the active scene already contains a `SpatialCamera` component. If one exists anywhere in the scene, leave it alone. If none exists, create an empty GameObject named `SpatialCamera`, add the `SpatialCamera` component to it, and set its `Dimensions` field to `(1.5, 1.5, 1.5)`.

## Trigger Keywords

- `Spatial Adapter`
- `PICO Spatial`
- `Unity Spatial`
- `SpatialCamera`
- `scene setup`
- `setup Unity scene`

## When to Use

- Use when a user asks to set up a Unity scene for Spatial Adapter.
- Use when a user asks to set up a Unity scene for `PICO Spatial`.
- Use when a user asks to set up a Unity scene for `Unity Spatial`.
- Use when validating a new or imported scene before Spatial Adapter runtime testing.
- Use when a scene is missing its `SpatialCamera` setup.
- Do not use when the task is only to explain the `SpatialCamera` API without changing the scene.

## Required Behavior

- Inspect the active Unity scene for any existing `SpatialCamera` component.
- If at least one `SpatialCamera` exists, do not create another one.
- If none exists:
  - Create an empty GameObject named `SpatialCamera`.
  - Add the `SpatialCamera` component.
  - Set `SpatialCamera.Dimensions = new Vector3(1.5f, 1.5f, 1.5f)`.
  - Register the creation with Unity Undo support.
- Prefer operating on the active scene only.

## Unity MCP Pattern

Use `Unity_RunCommand` and wrap the logic in `internal class CommandScript : IRunCommand`.

```csharp
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;
using ByteDance.PICO.SpatialAdapter;

internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        Scene scene = SceneManager.GetActiveScene();
        if (!scene.IsValid())
        {
            result.LogError("No active scene is available.");
            return;
        }

        SpatialCamera existingCamera = FindSpatialCameraInScene(scene);
        if (existingCamera != null)
        {
            result.Log("SpatialCamera already exists on {0}", existingCamera.gameObject);
            return;
        }

        GameObject cameraObject = new GameObject("SpatialCamera");
        result.RegisterObjectCreation(cameraObject);
        SpatialCamera camera = cameraObject.AddComponent<SpatialCamera>();
        camera.Dimensions = new Vector3(1.5f, 1.5f, 1.5f);
        EditorSceneManager.MarkSceneDirty(scene);
        result.Log("Created {0} with SpatialCamera Dimensions {1}", cameraObject, camera.Dimensions);
    }

    private static SpatialCamera FindSpatialCameraInScene(Scene scene)
    {
        foreach (GameObject rootObject in scene.GetRootGameObjects())
        {
            SpatialCamera camera = rootObject.GetComponentInChildren<SpatialCamera>(true);
            if (camera != null)
            {
                return camera;
            }
        }

        return null;
    }
}
```

## Quick Reference

- Search target: `SpatialCamera` component in the active scene.
- Create only when missing.
- New object name: `SpatialCamera`.
- New component: `SpatialCamera`.
- Default `SpatialCamera.Dimensions`: `(1.5, 1.5, 1.5)`.
- Use Undo-aware creation through `result.RegisterObjectCreation(...)`.

## Common Mistakes

- Creating duplicate `SpatialCamera` objects instead of checking the scene first.
- Searching assets or prefabs instead of the active scene hierarchy.
- Forgetting to register object creation, which weakens Undo and tracking behavior.
- Forgetting to set the default `Dimensions` to `(1.5, 1.5, 1.5)` on a newly created `SpatialCamera`.
- Renaming the created GameObject to something other than `SpatialCamera`.
