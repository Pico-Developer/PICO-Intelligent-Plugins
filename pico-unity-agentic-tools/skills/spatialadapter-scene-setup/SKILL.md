---
name: spatialadapter-scene-setup
description: Use to inspect, create, or repair SpatialCamera presence in a Spatial Adapter scene, including a missing or duplicate scene camera. General project setup belongs to pico-unity-spatial; window configuration and target following belong to their topic skills. Platform names alone do not activate this skill.
license: 'Apache-2.0'
---

# SpatialAdapter Scene Setup

## When NOT to Use

- Input handling or ray interaction — use `spatialadapter-input-api`
- Runtime initialization — use `spatialadapter-runtime-core-api`
- Spatial SDK scene building — use the Spatial plugin scene builder skill

## Overview

Use this skill when preparing a Unity scene for `Spatial Adapter`, `PICO Spatial`, or `Unity Spatial`. The first setup check enumerates every `SpatialCamera` component in the active scene, including inactive GameObjects. Leave exactly one existing camera unchanged, create one when none exists and setup is authorized, and treat multiple cameras as a blocking duplicate condition until the user chooses which camera to keep.

## Compatibility and Scope

Confirm Spatial mode from `.pico-cli/config.json` when available, installed packages, and scene evidence; ask before changing anything if they conflict. Verify that the installed package exposes `ByteDance.PICO.SpatialAdapter.SpatialCamera`. A validation-only request reports whether the component is missing and does not create it. Before scene editing, verify the running Editor and `Unity_RunCommand` availability and schema. If unavailable, report the missing capability and provide the manual Editor steps below without claiming a scene change.

## Trigger Keywords

- inspect scene SpatialCamera presence
- add or create SpatialCamera
- repair a missing or duplicate SpatialCamera

Platform names alone do not activate this skill. Require a request to inspect, create, or repair the scene camera. Use [pico-unity-spatial](../pico-unity-spatial/SKILL.md) for general project setup, [spatialadapter-camera-window-api](../spatialadapter-camera-window-api/SKILL.md) for window configuration, and [spatialadapter-spatial-camera-focus](../spatialadapter-spatial-camera-focus/SKILL.md) for target following.

## When to Use

- Use when a user explicitly asks to inspect, add, or repair `SpatialCamera` in a scene.
- Use when checking a new or imported scene for a missing or duplicate `SpatialCamera`.
- Use when a scene is missing its `SpatialCamera` setup.
- Do not use when the task is only to explain the `SpatialCamera` API without changing the scene.

## Required Behavior

- Enumerate all `SpatialCamera` components in the active Unity scene, including inactive GameObjects.
- If exactly one `SpatialCamera` exists, preserve it and its configuration.
- If none exists and the user authorized scene setup:
  - Create an empty GameObject named `SpatialCamera`.
  - Add the `SpatialCamera` component.
  - Set `SpatialCamera.Dimensions = new Vector3(1.5f, 1.5f, 1.5f)`.
  - Register the creation with Unity Undo support.
- If multiple `SpatialCamera` components exist, report every hierarchy path and stop. A validation-only request must not remove anything.
- Repair duplicates only after the user explicitly authorizes the repair and identifies the `SpatialCamera` to keep. Remove duplicate components with Undo support; do not delete their GameObjects or unrelated components.
- Prefer operating on the active scene only.

## Unity MCP Pattern

After tool discovery confirms `Unity_RunCommand` and its `IRunCommand` contract, wrap the creation logic in `internal class CommandScript : IRunCommand`. Run this write example only for an authorized setup request, not for read-only validation.

```csharp
using System.Collections.Generic;
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

        List<SpatialCamera> cameras = FindSpatialCamerasInScene(scene);
        if (cameras.Count > 1)
        {
            result.LogError("Found {0} SpatialCamera components in the active scene:", cameras.Count);
            foreach (SpatialCamera camera in cameras)
            {
                result.LogError("- {0}", GetHierarchyPath(camera.transform));
            }

            result.LogError("Choose the SpatialCamera to keep before authorizing duplicate repair.");
            return;
        }

        if (cameras.Count == 1)
        {
            result.Log("SpatialCamera already exists on {0}", cameras[0].gameObject);
            return;
        }

        GameObject cameraObject = new GameObject("SpatialCamera");
        result.RegisterObjectCreation(cameraObject);
        SpatialCamera camera = cameraObject.AddComponent<SpatialCamera>();
        camera.Dimensions = new Vector3(1.5f, 1.5f, 1.5f);
        EditorSceneManager.MarkSceneDirty(scene);
        result.Log("Created {0} with SpatialCamera Dimensions {1}", cameraObject, camera.Dimensions);
    }

    private static List<SpatialCamera> FindSpatialCamerasInScene(Scene scene)
    {
        List<SpatialCamera> cameras = new List<SpatialCamera>();
        foreach (GameObject rootObject in scene.GetRootGameObjects())
        {
            cameras.AddRange(rootObject.GetComponentsInChildren<SpatialCamera>(true));
        }

        return cameras;
    }

    private static string GetHierarchyPath(Transform target)
    {
        string hierarchyPath = target.name;
        while (target.parent != null)
        {
            target = target.parent;
            hierarchyPath = target.name + "/" + hierarchyPath;
        }

        return hierarchyPath;
    }
}
```

## Duplicate Repair

Treat duplicate detection and duplicate removal as separate operations. First enumerate and report the hierarchy paths without changing the scene. After the user explicitly chooses the camera to keep and authorizes the repair, resolve that path back to exactly one camera in the same active-scene list. If the path is missing or ambiguous, stop without mutation.

For every other camera, call `Undo.DestroyObjectImmediate(camera)` to remove the duplicate component only. Do not delete the containing GameObject, because it may hold unrelated components or user content. Mark the active scene dirty, save the intended scene, and re-enumerate the scene to confirm exactly one `SpatialCamera` remains.

## Manual Editor Steps

1. Inspect the active scene hierarchy, including inactive objects, and list every `SpatialCamera` component by hierarchy path.
2. For validation-only requests, report whether the count is zero, one, or multiple and stop without changing anything.
3. For authorized setup with no camera, create an empty GameObject named `SpatialCamera`, add the component, and set Dimensions to `(1.5, 1.5, 1.5)`.
4. If duplicates exist, ask which hierarchy path to keep. After explicit authorization, remove only the other `SpatialCamera` components with Undo support.
5. Save the intended scene. For an unsaved scene, ask for the asset path rather than choosing one silently.

## Verification

- Re-enumerate the active scene and confirm exactly one `SpatialCamera` exists after setup or repair.
- Confirm a newly created camera has Dimensions `(1.5, 1.5, 1.5)` and an existing camera's configuration was preserved.
- For duplicate repair, confirm the user-selected camera remains unchanged and the other GameObjects and unrelated components still exist.
- Before runtime testing, verify a usable explicit or default configuration with [camera and window APIs](../spatialadapter-camera-window-api/SKILL.md).
- Save the intended scene after changes and report the save result. Marking a scene dirty is not the same as saving it.

## Quick Reference

- Search target: every `SpatialCamera` component in the active scene, including inactive GameObjects.
- Create only when missing.
- Preserve exactly one existing camera; multiple cameras require an explicit keep choice before repair.
- New object name: `SpatialCamera`.
- New component: `SpatialCamera`.
- Default `SpatialCamera.Dimensions`: `(1.5, 1.5, 1.5)`.
- Use Undo-aware creation through `result.RegisterObjectCreation(...)`.
- Use Undo-aware duplicate component removal through `Undo.DestroyObjectImmediate(camera)`.

## Common Mistakes

- Creating duplicate `SpatialCamera` objects instead of checking the scene first.
- Returning after the first `SpatialCamera` match, which hides duplicate components elsewhere in the scene.
- Silently choosing which duplicate camera to keep or deleting an entire GameObject during component repair.
- Searching assets or prefabs instead of the active scene hierarchy.
- Forgetting to register object creation, which weakens Undo and tracking behavior.
- Forgetting to set the default `Dimensions` to `(1.5, 1.5, 1.5)` on a newly created `SpatialCamera`.
- Renaming the created GameObject to something other than `SpatialCamera`.
