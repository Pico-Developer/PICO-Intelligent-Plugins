# Code Generation Execution Playbook

## 1. Frozen Inputs

Before generation, confirm the following files exist and pass validation:

- `environment.json`
- `source-project.json`
- `capability-inventory.json`
- `experience-inventory.json`
- `mapping-report.json`
- `admission-report.json`, where `status=full|degraded_approved` and
  `admitted=true`
- `degradation-decision.json` (only when admission or the finished product is below 100)
- `conversion-contract.json`
- `verification-plan.json`

Implementation consumes only these files. When a contract error is found, return it to the contract
stage for correction; do not bypass it temporarily in code.

First branch by `target_ownership`:

- `kotlin_code`: a Kotlin/ECS implementation must be generated.
- `source_asset`: only copying or format-converting source files that already exist in the inventory
  is allowed.
- `dropped`: no implementation is generated.

## 2. Creating the Project

Use the name, package name, container, and SDK version from `conversion-contract.json`:

```bash
pico-cli project create \
  --dir <output_project> \
  --name <app_name> \
  --package <package_name> \
  --template <container> \
  --sdk <sdk_version>
```

Must not use `--force` to overwrite an existing Gradle project. When the target directory is
non-empty, stop and request a new output location.

Container selection:

- `planar`: the main body is a 2D workflow, with 3D only for local display.
- `volumetric`: the main body is a bounded 3D viewer or product showcase.
- `stage`: the source project is WebXR, room-scale, or an immersive experience.

## 3. Package Structure

Add to the template's existing entry chain:

```text
app/src/main/java/<package>/
├── scene/          Entity creation, hierarchy, and scene root
├── resources/      Models, meshes, materials, textures, and lifecycle
├── systems/        Per-frame ECS Systems
├── interaction/    Hit testing, gestures, controllers, and state transitions
├── ui/             SpatialUI components and state
└── domain/         Rendering-independent behavior, math, and state machines
```

Preserve the responsibility boundaries of the template's `Main.kt`, `SpatialApplication.kt`, and
`LaunchActivity.kt`; do not rebuild the entry point.

## 4. Scene and Coordinates

- Handle spatial composition in a fixed order:
  1. Create in scratch a probe shell consistent with the target SDK, container, window
     configuration, and final page layout geometry. Copy
     `assets/probes/SpatialViewVisibleRegionProbe.kt`, modify only the package, attach
     `captureSpatialViewVisibleRegion(probe)` to the final `SpatialView` modifier, and call
     `probe.bind(content)` in `initial`.
  2. Launch the probe shell, extract the complete JSON from the `SPATIAL_FIT_MEASUREMENT ` log, and
     save it verbatim as the profile's `measurement_file`. The outer window size cannot substitute
     for this artifact.
  3. Copy `assets/probes/three-scene-aabb-probe.mjs` in the source project, call
     `measureThreeSceneAabb` for the fully assembled state and each state where the extent changes,
     and save each returned object verbatim as the state's `measurement_file`.
  4. Freeze the complete page UI region to obtain a `usable_region` that does not contend with the
     UI.
  5. Clarify the physical meaning of the source units and convert them to meters, then compute the
     unified fit scale and placement.
  6. Finally check the occlusion relationships among models, UI, and interaction targets.
- `validate_spatial_fit.py` does not access the Runtime and does not perform measurement; it reads
  `measurement_file`, recomputes the context fingerprint, original corners, and AABB, and then
  validates the fit.

Minimal target probe integration:

```kotlin
val fitProbe = remember {
    SpatialViewVisibleRegionProbe(profileId = "main-default", sdkVersion = sdkVersion)
}
SpatialView(
    modifier = finalModifier.captureSpatialViewVisibleRegion(fitProbe),
    initial = { content, _ ->
        fitProbe.bind(content)
        initializeScene(content)
    },
)
```

The source side calls after each state stabilizes:

```js
measureThreeSceneAabb({ root: sceneRoot, stateId: 'fully-assembled' })
```
- Create a single `migrated-scene-root` that uniformly carries the unit, forward axis, and overall
  fit transform.
- Build Entities according to the source scene's parent-child relationships; do not flatten all
  objects.
- All 3D lengths ultimately use meters.
- Handle Stage front as `-Z`.
- `units_to_meters` expresses only real unit conversion; window adaptation uses an independent
  dimensionless `uniform_scale`, and the two must not be mixed into one empirical coefficient.
- The unified scale for each layout profile is computed as
  `min(usable_axis_size / (source_axis_size * units_to_meters))`; axis sizes are aligned by
  `axis_mapping`, and zero-size axes do not participate in the minimum computation.
- After loading a model, read the actual bounds and compare them with the contract AABB, then apply
  the frozen unified scale and translation. Must not mechanically copy the source model's `scale`,
  `position`, or camera distance.
- The target AABB of all animations and interaction key states must fall within the measured
  clipping box; the reference state must also fall within the usable region reserved for the
  complete UI.
- For skinned models, keep the model root scale at 1, and use an outer wrapper Entity when
  necessary.

## 5. Geometry, Materials, and Assets

- Use MeshResource factories verified by the current SDK for basic geometry.
- Convert static custom BufferGeometry into supported MeshModel data.
- For dynamic geometry, implement only the bounded updates approved by the contract; do not
  replicate arbitrary WebGL buffer management.
- Use MeshInstancesResource or a Kotlin-managed shared entity pool for InstancedMesh.
- Procedural models retain code ownership and must not be exported offline as GLB, USD, OBJ, PLY, or
  SPZ.
- Use runtime Bitmap/TextureResource or code approximation for procedural textures; must not bake
  them into images.
- Keep procedural animation, particles, trails, and decals implemented as ECS Systems, instances,
  or dynamic meshes.
- Reuse meshes, materials, and textures; establish a scene lifecycle registry for shared resources.
- Only GLB/USD and other files that already existed in the source project before migration and are
  registered in `asset_paths` may be loaded once and attached in `SpatialView.initial` through the
  public asynchronous loading path.
- Existing FBX and other formats not directly supported in the source project may undergo
  one-to-one format conversion; the contract must record `source_path`, `output_path`,
  `provenance=format_conversion`, and the conversion method.
- Map Basic materials to Unlit, and Standard/Physical to PBR.
- For Lambert/Phong, only do the PBR approximation recorded in the contract.
- For `material.shader`, `material.raw-shader`, and `material.node-tsl`, first evaluate
  ShaderGraph against the three conditions: shading is limited to the surface/vertex stage, inputs
  can be mapped to node port types, and the required computation can be expressed by nodes or a
  Custom Function. When the conditions are satisfied and equivalence holds per state, produce the
  material bundle through the Editor pipeline, load it with `ShaderGraphMaterial`, and record the
  graph source file, shading stage, and evaluation evidence in the contract.
- Do not rewrite GLSL text, and do not introduce material extensions that are not registered in the
  contract.
- Editor and ShaderGraph carry only material semantics; procedural geometry, animation, particles,
  and procedural textures must not be prefabricated into bundles via the Editor.

For procedural content that cannot be expressed with the above Spatial SDK capabilities, choose
code approximation, deletion, or rejection according to criticality. Must not convert it into a
prefabricated asset in order to improve visual similarity.

After generation is complete, first run the lossless optimization evaluation in `optimization.md`,
then proceed to acceptance.

## 6. Animation and Per-Frame Logic

- Use SDK AnimationResource and playback controllers for asset animation.
- Bind skeletons and Blend Shapes according to the actual resources of the loaded model.
- Put procedural animation, object pools, lifetimes, movement, and collision state into custom ECS
  Systems.
- Systems are registered with the scene and unregistered when leaving the container.
- Must not use `SpatialView.update`, infinite Compose coroutines, or main-thread blocking loops in
  place of Tick.

## 7. Interaction and Tracking

- Map Raycaster semantics to CollisionComponent and scene raycast.
- User-interactable entities must have both CollisionComponent and InteractableComponent.
- Map Pointer/Drag/Scale/Rotate to Spatial gestures.
- Change OrbitControls to inverse rotation, scaling, and translation of the scene root, model
  wrapper, or a dedicated view root; do not control the system camera.
- Convert named camera presets into complete viewing states: azimuth, pitch, look target, framing
  scale, and vertical focus must take effect together; must not retain only a yaw constant.
- Provide hit surfaces or proxy interaction entities covering the visible region of the subject for
  model-inspection experiences; gesture hit testing, state updates, and final Transform changes all
  need runtime evidence.
- When an implementation approach is known but gestures, collision, or state flow are not yet
  integrated, mark it as not implemented; must not write it as a Spatial platform limitation or a
  completed `rebuild`.
- Delete WebXR session code; the container handles the spatial lifecycle.
- For head, controller, hand, and environment hit testing, use only provider/APIs verified by the
  current SDK.

## 8. DOM to SpatialUI

Use `experience-inventory.json` as the completeness denominator and implement item by item:

- Every page, route, and navigation entry.
- All regions such as header, sidebar, main, footer, control area, information area, and overlay.
- All user-visible states such as default, loading, empty, error, selected, disabled.
- Forms, lists, tabs, menus, dialogs, toasts, HUD, and media areas.
- Desktop, mobile, and the responsive modes actually supported by the source project.
- Complete user flows triggered by keyboard/mouse, touch, and XR input.

All UI uses SpatialUI and is wrapped by `PicoTheme`. Convert CSS into Compose/SpatialUI layout,
color, typography, hierarchy, and state semantics; do not mechanically translate selectors and pixel
positioning.

Migrate CSS2D/CSS3D information to AttachmentPanel. Complex HTML itself is not a blocking reason;
it should be split into a SpatialUI component tree and fully rebuilt. Only when browser-specific
runtime semantics truly cannot be expressed may it be approximated or blocked after recording
native attempt evidence and obtaining user degradation approval.

Must not generate only a 3D model showcase page, a temporary control panel, or a "feature example"
to replace complete source pages.

## 9. Lifecycle

Define symmetric cleanup for each creation behavior:

| Creation | Cleanup |
|---|---|
| Entity | `destroy()` |
| Resource | `close()` or owner destruction |
| ECS System | unregister |
| tracking provider | stop |
| event subscription | unsubscribe |
| coroutine | cancel |
| audio/video player | stop/release |

Use fixed-capacity pools for high-frequency created content. Capacity comes from the source project
peak or the migration contract; do not guess during implementation.

## 10. Unit Tests

At minimum cover:

- Source-to-target coordinate and unit conversion.
- AABB min/max/size consistency, axis mapping, unified fit formula, and clipping-box containment.
- State machines and animation stages.
- Mapping of interaction commands to domain state.
- Object pool capacity and return.
- Core business rules that must still be preserved after degradation.

Tests must not be padded with the template's built-in `ExampleUnitTest`.
