---
name: spatialadapter-scene-setup
description: Use when setting up a Unity scene for Spatial Adapter, PICO Spatial, or Unity Spatial and the scene needs a SpatialCamera component.
license: 'Apache-2.0'
---

# SpatialAdapter Scene Setup

## Overview

Use this skill when preparing a Unity scene for `Spatial Adapter`, `PICO Spatial`, or `Unity Spatial`. The first setup check is whether the active scene already contains a `SpatialCamera` component. If one exists anywhere in the scene, leave it alone. If none exists, create an empty GameObject named `SpatialCamera`, add the `SpatialCamera` component to it, and set its `Dimensions` field to `(1.5, 1.5, 1.5)`.

## Compatibility and Scope

Confirm Spatial mode from `.pico-cli/config.json` when available, installed packages, and scene evidence; ask before changing anything if they conflict. Verify that the installed package exposes `ByteDance.PICO.SpatialAdapter.SpatialCamera`. A validation-only request reports whether the component is missing and does not create it. Before scene editing, verify the running Editor and `Unity_RunCommand` availability and schema. If unavailable, report the missing capability and provide the manual Editor steps below without claiming a scene change.

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
- If none exists and the user authorized scene setup:
  - Create an empty GameObject named `SpatialCamera`.
  - Add the `SpatialCamera` component.
  - Set `SpatialCamera.Dimensions = new Vector3(1.5f, 1.5f, 1.5f)`.
  - Register the creation with Unity Undo support.
- Prefer operating on the active scene only.

## Unity MCP Pattern

After tool discovery confirms `Unity_RunCommand` and its `IRunCommand` contract, wrap the creation logic in `internal class CommandScript : IRunCommand`. Run this write example only for an authorized setup request, not for read-only validation.

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

## Manual Editor Steps

1. Inspect the active scene hierarchy, including inactive objects, for a `SpatialCamera` component.
2. For validation-only requests, report the result and stop without creating anything.
3. For authorized setup, leave any existing SpatialCamera unchanged. Otherwise create an empty GameObject named `SpatialCamera`, add the component, and set Dimensions to `(1.5, 1.5, 1.5)`.
4. Save the intended scene. For an unsaved scene, ask for the asset path rather than choosing one silently.

## Verification

- Re-read the active scene and confirm the component exists and no duplicate was created.
- Confirm a newly created camera has Dimensions `(1.5, 1.5, 1.5)` and an existing camera's configuration was preserved.
- Before runtime testing, verify a usable explicit or default configuration with [camera and window APIs](../spatialadapter-camera-window-api/SKILL.md).
- Save the intended scene after changes and report the save result. Marking a scene dirty is not the same as saving it.

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
