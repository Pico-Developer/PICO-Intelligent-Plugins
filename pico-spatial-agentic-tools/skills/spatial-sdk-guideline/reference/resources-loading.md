# Resources Loading (Models / AssetBundle / Mesh / Material / Texture)

## What this covers

- Model formats and recommended choices (USD vs glTF)
- AssetBundle workflow (Spatial Editor `.bundle`)
- Async loading patterns (don’t block UI)
- Resource lifecycle: validity, persistence, and safe release

## Choose a model source

### Model formats

- **Preferred**: USD (`.usd/.usda/.usdc/.usdz`)
- **Supported**: glTF/GLB

Practical guidance:

- Use USD when you control the authoring pipeline and want best compatibility.
- Use glTF/GLB when integrating existing DCC/export workflows.

## AssetBundle (Spatial Editor pipeline)

### What it is

- Spatial Editor compiles one project into a `.bundle` stored in APK assets.
- The bundle can contain multiple scenes (USDA files) and resources.

### Load a bundle

```kotlin
val bundle = AssetBundle.load("asset://path/to/YourBundleName.bundle")
```

Best practice:

- Keep a reference and **close** it explicitly when done.

### Load a scene (USDA) from a bundle

- Copy the delivered scene's **`runtimeSceneKey`** verbatim into `loadModel`,
  `loadModelSuspend`, `preloadModel` and `releaseModel`. It is case-sensitive and has no source extension.
- `scene.name` is an authoring/display name; `sourcePath`, `bundlePath` and `entryScene`
  identify authoring files. None is a substitute for the runtime key.
- pico-cli records `runtimeSceneKey` in each `.scenes.json` scene, the pack response/MCP
  summary, and the selected Workflow output scene. The key depends on the actual pack root.
  For example, if that root is `Sources`, `Sources/Scenes/SubFolder/SceneName.usda`
  is delivered as `Scenes/SubFolder/SceneName`. Never infer a fixed prefix for new bundles.
- Older or externally packed bundles can use a different root. Obtain a verified key from
  that bundle or repackage it; never add/remove `Scenes/` or match only a basename to guess it.

```kotlin
val sceneKey = deliveredRuntimeSceneKey // copy the selected scene's verified runtimeSceneKey
val root = bundle.loadModel(sceneKey)
```

Before operating on scene elements, verify the runtime Entity corresponding to the selected
manifest scope. All bundle model-loading interfaces return the same Entity hierarchy for the same
packed model, including `loadModel` and `loadModelSuspend`; apply the same scope verification to
each returned Entity. `preloadModel` and `releaseModel` return no Entity.
Keep the manifest scope Entity separate from the returned entity: the verified Editor 6.2.5 / SDK 6.2.8
layout has an outer return without a manifest entity record, followed by a unique direct child.
The return's name corresponds to the requested model name; its child's default editor name is
`root` and can change. Identify that child by the verified hierarchy, without matching its name.
Keep the manifest scope path (verified from top-level `parentPath` and `path`) separate from the
child's runtime name. Compare that child's complete top-level names and count with the selected manifest
before walking direct children by name, requiring exactly one match at every level.
Zero or multiple matches must fail. Do not infer correspondence from a name or child order alone.
Unknown layouts remain unresolved; see `spatial-bundle-scene-reader` for scope verification and
the scoped resolver.

### Preload

For large scenes:

```kotlin
bundle.preloadModel(sceneKey)
```

### Load materials from a bundle

- Materials live under scene paths (example structure):
  - `"SceneName/Root/MyMaterials/pbrMaterial"`

```kotlin
val m = bundle.loadMaterial("SceneName/Root/MyMaterials/pbrMaterial")
val pbr = m as PhysicallyBasedMaterial
```

### Release bundle-cached data (two steps)

There are two distinct concepts:

1. **Destroy instances** you created (`Entity.destroy()`, `Resource.close()`).
2. **Release cached underlying data** in the bundle (`bundle.releaseModel(...)`, `bundle.releaseResource(...)`).

Example pattern:

```kotlin
val e = bundle.loadModel(sceneKey)
// ... use entity ...
e.destroy()               // release entity instance and its references
bundle.releaseModel(sceneKey) // release underlying cached model data
bundle.close()            // release the bundle and any remaining cached data
```

## Direct loading from assets (no bundle)

Use this for files shipped directly in APK assets, including `.gltf` / `.glb` models. `glTF/GLB` is supported, although `USD` remains the preferred format when you control the content pipeline.

### Model entities

For Compose-based container code, follow the general `SpatialView` pattern: do one-time entity loading in `initial`, then attach the loaded root entity with `content.addEntity(...)`.

```kotlin
SpatialView(initial = { content, _ ->
  val root = Entity.loadSuspend("asset://models/robot.glb")
  content.addEntity(root)
})
```

Guideline:

- Prefer `loadSuspend(...)` to avoid blocking the main thread.
- If you need to show the synchronous API instead, use `withContext(Dispatchers.IO) { Entity.load("asset://...") }`.
- `Entity.loadSuspend(...)` can be called directly on the main thread; after loading completes, entity/component access and mutation should run on the main thread.
- In `SpatialView`, use `initial` for one-time loading/setup; do not keep re-adding loaded entities from `update`.
- `Entity.loadSuspend(...)` returns the **root `Entity`** of the loaded model hierarchy, so add that root to the scene/content after loading succeeds.
- Loaded child entities automatically get `TransformComponent`, and mesh-bearing child entities automatically expose `ModelComponent` for mesh/material access.
- If you need to inspect or modify rendered parts after loading, traverse the hierarchy (for example with `getChildren()` / `findEntity(...)`) and read `ModelComponent` from the mesh-bearing child entities.

## Mesh, materials, textures (resource basics)

### Mesh

- Primitives:
  - `MeshResource.createBox(...)`, `createSphere(...)`, `createPlane(...)`, etc.
- Instancing (reduce draw calls):
  - `MeshInstancesResource` (many instances of same geometry)

### Materials

- Common: `UnlitMaterial`, `PhysicallyBasedMaterial`, `ShaderGraphMaterial`.
- Choose blending mode intentionally (Opaque/Transparent/Add/Fade/Masked).

### Textures

- `TextureResource.load(...)` or `TextureResource.create(Bitmap)`.

## Resource lifecycle (critical)

### Validity

- Most resources have `valid` (or equivalent). After release, `valid == false`.

### Persistence

- `resource.toGlobal()` persists the resource beyond typical ownership.
- You must later call `resource.close()` to unpersist and release.

### Common leak patterns

- Creating a resource and never attaching it to an entity/material.
- Persisting resources (`toGlobal()`) and forgetting to `close()`.

### Common “use-after-free” pattern

- Destroying the entity that owns a resource and then reusing the old resource handle.

Checklist:

- [ ] Do I know who owns each resource (entity, material, global)?
- [ ] When a screen/container closes, do I destroy entities and cancel subscriptions?
- [ ] If I used `toGlobal()`, do I have a matching `close()`?

## Packaging checklist (AssetBundle + models)

- [ ] Ensure `.bundle` is not compressed in the APK.
- [ ] If you ship `.usdz`, `.glb`, `.wav`, also ensure they are not compressed.
- [ ] Treat bundle names and scene paths as stable runtime IDs.
