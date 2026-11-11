# Editor Handoffs for App Integration

Read when consuming authored bundle files or syncing a custom component declaration.

## Consume Editor Bundle Handoffs When Present

Use this section only when a requirement provides, references, or depends on editor-authored bundle handoff files. A valid handoff contains these co-located files:

- `<bundleName>.bundle`: the app-loadable AssetBundle file.
- `<bundleName>.scenes.json`: the primary machine-readable contract for app integration, including scene, hierarchy, entity, warning, and per-scene container data.

Parsing rules:

1. Parse `<bundleName>.scenes.json` first. Do not inspect editor project files as the primary integration contract.
2. Validate `schemaVersion == "0.1"`. If the schema is missing or incompatible, stop and report the handoff incompatibility instead of guessing.
3. Use `<bundleName>.bundle` as the Android asset bundle identifier after the file is placed under `app/src/main/assets/`.
4. Choose the entry scene from `activeScenePath` when present, otherwise from the first `scenes[]` entry unless the user explicitly specifies another scene.
5. Treat the chosen scene's inline `container` as editor authoring-container data: it describes the content's minimum usable container recommendation after editor export, not an instruction to replace an existing app runtime container.
6. Preserve the app's existing runtime container shape when it is already clear from the project or completed Editor Workflow handoff metadata.
7. Choose the app presentation path by combining the app runtime container and the editor authoring container:
   - Existing app Stage/FullSpace runtime → use the existing Stage/FullSpace loading path.
   - Existing app Volume/WindowContainer/SpatialView runtime → preserve that bounded runtime shape and load the bundle inside it.
   - No app runtime container is known → use the chosen scene's inline `container` as the best available recommendation: Stage/FullSpace data suggests Stage/FullSpace; Plane/Volume/window/spatial-view data suggests the corresponding bounded loading path.
   - Missing or ambiguous runtime and authoring container data → do not silently choose. Ask the user which presentation mode should be used.
8. Verify `.bundle` and `.scenes.json` exist in `app/src/main/assets/` for Spatial app projects before changing loading code. Only pure editor handoff inspection may use editor-local `Build/` output.

Minimal expected scenes sidecar shape:

```json
{
  "schemaVersion": "0.1",
  "scope": "bundle_scenes",
  "activeScenePath": "Sources/Scenes/Hi.usda",
  "scenes": [
    {
      "sourcePath": "Sources/Scenes/Hi.usda",
      "container": {},
      "hierarchy": [],
      "entities": []
    }
  ],
  "warnings": []
}
```

Implementation rules:

- Keep the bundle and `.scenes.json` under `app/src/main/assets/` for Spatial app projects.
- Load the bundle by `asset://<bundleName>.bundle`, not by an absolute filesystem path.
- Follow `spatial-sdk-guideline/reference/resources-loading.md` for the current SDK bundle-loading API.
- Read `spatial-bundle-scene-reader` for bounded scene selection and loaded-scene scope verification.
  Use the selected scene's exact `runtimeSceneKey`; preserve case and every path segment.
  Keep the SDK return separate from the verified manifest scope Entity used for traversal.
  Apply the same mapping to all bundle model-loading interfaces, including `loadModel` and
  `loadModelSuspend`: they return the same hierarchy for the same packed model.
  For the observed Editor 6.2.5 / SDK 6.2.8 layout, its unique direct child supplies that scope;
  its name can change. Verify the complete top-level names and `rootCount` before resolving paths.
  Keep the manifest scope path, obtained from consistent top-level `parentPath` and `path`,
  separate from this runtime child's name.
  Unknown layouts are a blocker for Entity addressing. `rootCount` is not the outer child count,
  and runtime node totals need not equal manifest `entityCount`.
- Keep bundle names and scene paths stable runtime IDs.
- Configure the app Gradle `androidResources.noCompress` to include `bundle` when the app packages an Editor AssetBundle. The source setting alone is not delivery evidence; verify the built APK below.
- Mention any sidecar `warnings` in the final response and in local handoff docs when relevant.
- Mention public Workflow Result warnings separately from sidecar warnings. App/device screenshot or recording validation is still required for runtime size, scale, clipping, and visibility.

## Custom Component Declaration Handoff

Use this section when the app introduces or changes a Kotlin ECS `Component` that must be authored in Spatial Editor.

Separation of responsibilities:

- `spatial-editor` owns syncing the Kotlin `Component` declaration into the editor project's `.Component/component.json` through `pico-cli editor sync component`.
- This app workflow owns app-side runtime work: imports, `registerComponent<T>()` or the current SDK registration mechanism, bundle loading, build, install, launch, and runtime verification.

Do not manually edit `.Component/component.json` from this workflow. If the Editor declaration is missing or stale, route to `spatial-editor` and resume here after it reports `added`, `updated`, or `skipped`.

After declaration sync, remember:

- Editor visibility may require reopening the current Spatial Editor project or refreshing the component panel.
- Spatial app runtime behavior still requires app-side code to recognize the component.
- A successful declaration sync alone is not proof that the component works at runtime.
