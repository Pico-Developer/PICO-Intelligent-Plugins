# Three.js → Spatial SDK Capability Mapping

## 1. Mapping Contract

Every `capability-inventory.json` item must appear exactly once in `mapping-report.json`.

```json
{
  "capability_id": "geometry.instancing",
  "mapping_level": "direct",
  "target_ownership": "kotlin_code",
  "spatial_primitive": ["MeshInstancesResource"],
  "conversion_rule": "Share MeshResource and materials, and write transforms plus permitted custom data per instance",
  "quality_loss": [],
  "validation": ["Instance count matches", "Key instance transforms match"],
  "version_evidence": [
    {
      "sdk_version": "<discovered-stable-version>",
      "source": "local-api-or-official-doc",
      "symbol": "MeshInstancesResource"
    }
  ]
}
```

`mapping_level`:

- `direct`: the target SDK has a public equivalent capability.
- `rebuild`: semantics are preserved, but the architecture or state flow must be rewritten.
- `approximate`: the purpose is preserved, with an explicit quality loss accepted.
- `drop`: remove a non-core capability.
- `block`: a core capability has no acceptable implementation.

`direct`, `rebuild`, and `approximate` must include `version_evidence` for the
currently selected SDK version. Use `block` when a public symbol cannot be
verified, and do not cite another version to fill the gap.

`target_ownership`:

- `kotlin_code`: created and driven by Spatial SDK Kotlin/ECS code.
- `source_asset`: only load external assets that already exist in the input project and have been registered.
- `editor_authored`: when shading semantics are limited to the surface or vertex stage, reconstruct the
  inventoried `material.*` capabilities with Spatial Editor and ShaderGraph; the output is a material
  bundle exported by the Editor pipeline, loaded and attached by Kotlin.
- `dropped`: not included in the target implementation.

`asset.*` capabilities must be `source_asset` when retained. `material.*` capabilities may use
`kotlin_code` or `editor_authored` under `rebuild|approximate`; all other non-`asset.*` capabilities
must be `kotlin_code`. `drop|block` must be `dropped`.

`approximate|drop|block` is not an initial choice. For each degradation that affects the experience,
first record:

- `native_attempts[].approach`: the attempted native Spatial SDK implementation.
- `native_attempts[].evidence`: API, build, runtime, or performance evidence.
- `native_attempts[].outcome`: `api_unavailable`, `semantic_mismatch`,
  `runtime_failed`, or `performance_failed`.
- `native_attempts[].limitation`: why full semantics cannot be achieved.
- `degradation_reason`: the conclusion that justifies the degradation.

Without the above evidence, the mapping report is invalid.

## 2. Default Mapping

The table below is the first-release decision baseline. The actual level may be tightened according to
criticality, but must not be loosened without evidence.

| Three.js Capability | Default Level | Spatial Target or Disposition |
|---|---|---|
| `project.native-three` | rebuild | Move to an Android/Kotlin Spatial project |
| `project.typescript` | drop | Do not retain the TS toolchain after rewriting in Kotlin |
| `project.dynamic-import` | block | Staticize the runtime path first; reject if it cannot be staticized |
| `scene.hierarchy` | direct | Entity parent-child hierarchy |
| `scene.transform` | direct | TransformComponent, metric right-handed coordinates |
| `scene.layers` | rebuild | Entity grouping, visibility, DrawOrder, or a separate system |
| `geometry.primitive` | direct | Create base geometry with MeshResource in Kotlin |
| `geometry.buffer-static` | direct | Rebuild static meshes in Kotlin with MeshModel/MeshResource |
| `geometry.buffer-dynamic` | approximate | Kotlin fixed-topology updates or entity/instance pools; large-scale per-vertex updates are blocked |
| `geometry.instancing` | direct | Create MeshInstancesResource in Kotlin |
| `asset.gltf-glb` | direct | Entity.loadSuspend |
| `asset.usd` | direct | Entity.loadSuspend or model loading supported by the SDK |
| `asset.obj` | direct | Load directly when the current SDK supports it; otherwise pre-convert |
| `asset.fbx` | approximate | Pre-convert to GLB/USD; block if conversion fails |
| `asset.hdr` | approximate | Stage environment IBL or static textures; subject to container limits |
| `asset.texture` | direct | TextureResource |
| `asset.font` | rebuild | SpatialUI fonts; procedural 3D text switches to AttachmentPanel or is blocked |
| `asset.video` | rebuild | VideoMaterial/VideoComponent |
| `material.unlit` | direct | UnlitMaterial |
| `material.lambert-phong` | approximate | PhysicallyBasedMaterial parameter fitting |
| `material.pbr` | direct | PhysicallyBasedMaterial |
| `material.shader` | rebuild/approximate/block | Evaluate ShaderGraph and record `rebuild` only when the shading stage is limited to surface/vertex, the inputs can map to node ports, and the nodes can express it; record `approximate` when only visual closeness is achieved; if the conditions are not met, approximate in Kotlin or reject |
| `material.raw-shader` | block | Pipeline-level semantics such as self-managed render pipelines, multiple Passes, and render targets are beyond the graph model |
| `material.node-tsl` | rebuild/approximate/block | Evaluate ShaderGraph only when the graph semantics fall within surface/vertex shading; block if it includes compute, render targets, or pipeline control |
| `lighting.ambient` | rebuild | IBL or a low-cost ambient lighting strategy |
| `lighting.directional` | direct | DirectionalLightComponent |
| `lighting.point` | direct | PointLightComponent |
| `lighting.spot` | direct | SpotLightComponent |
| `lighting.ibl` | direct/approximate | ImageBasedLight or StageEnvironmentLighting |
| `lighting.shadow` | direct/approximate | Dynamic shadows or GroundingShadow |
| `animation.clip` | direct | AnimationResource and a playback controller |
| `animation.skeletal` | direct | Skinned mesh animation resources |
| `animation.morph` | direct | Blend Shape animation capability |
| `animation.procedural` | rebuild | Kotlin ECS System with controlled lifecycle |
| `render.webgl-renderer` | drop | Spatial Engine takes over rendering |
| `render.webgpu-renderer` | drop | Spatial Engine takes over rendering; WebGPU features are judged separately |
| `render.target` | block | Application-managed offscreen rendering chains are not exposed |
| `render.multi-camera` | block | Refers only to simultaneously present application-managed projections, multi-camera Passes, or compositing; named viewpoints and single-view observation do not belong to this item |
| `render.layers` | approximate | Rebuild with Entity visibility/ordering; per-Pass semantics are not retained |
| `render.postprocessing` | approximate/block | Approximate with materials/geometry; reject core screen effects |
| `interaction.raycast` | direct | CollisionComponent + Scene rayCast |
| `interaction.pointer` | rebuild | Spatial gestures and TargetEntity |
| `interaction.orbit-controls` | rebuild | Rebuild orbit observation through inverse rotation, scaling, and translation of the scene root or a view proxy |
| `interaction.transform-controls` | approximate | Spatial gesture editor; do not replicate desktop gizmos |
| `interaction.drag` | rebuild | Spatial drag/grab semantics |
| `view.camera-framing` | rebuild | Convert single-camera position/target/fov/zoom into inverse framing state on the scene root or view root |
| `view.camera-presets` | rebuild | Named viewpoint buttons drive the full orientation, pitch, look-at target, and scale state |
| `xr.session` | drop | Stage and container lifecycle take over |
| `xr.head-pose` | direct | HMD tracking provider or system camera semantics |
| `xr.controller` | direct | Controller tracking/input |
| `xr.hand-tracking` | direct | HandTrackingProvider |
| `xr.hit-test` | rebuild | Spatial raycast, plane/mesh perception |
| `physics.basic` | direct | Collision, RigidBody, PhysicsWorld |
| `physics.external` | approximate | Map a basic subset; engine-specific semantics must be blocked |
| `physics.constraints` | block | Complex joint and vehicle constraints are blocked |
| `effect.points-sprite` | approximate | Kotlin billboard meshes or instances |
| `effect.particles-cpu` | approximate | Kotlin bounded Entity/MeshInstances object pools |
| `effect.particles-gpu` | block | GPU simulation is blocked |
| `effect.ribbon-trail` | approximate | Kotlin bounded dynamic meshes or segmented instances |
| `effect.decal` | approximate | Kotlin planar/patch geometry; projector semantics are not retained |
| `effect.transparent-sorting` | rebuild | Blend modes + DrawOrderGroup |
| `audio.ambient` | direct | AmbientAudioComponent |
| `audio.positional` | direct | ObjectAudioComponent |
| `ui.basic-dom` | rebuild | PicoTheme + SpatialUI allowlisted controls |
| `ui.css2d-css3d` | rebuild | AttachmentPanel/SpatialUI |
| `ui.complex-dom` | rebuild/approximate | Fully rebuild with a SpatialUI component tree; only browser-specific semantics may be degraded |
| `ui.layout` | rebuild | Fully rebuild page regions with SpatialUI/Compose layout |
| `ui.navigation` | rebuild | Compose state and Spatial container navigation |
| `ui.forms` | rebuild | SpatialUI input, selection, validation, and submit state |
| `ui.overlay` | rebuild | SpatialPopup, Menu, Dialog, AttachmentPanel |
| `ui.hud` | rebuild | SpatialUI overlay or AttachmentPanel |
| `ui.responsive` | rebuild | Window constraints and adaptive Compose layout |
| `ui.state` | rebuild | ViewModel/state holders and deterministic state transitions |
| `ui.media` | rebuild | SpatialUI Image, Video, or registered source assets |
| `browser.canvas2d` | approximate/block | Rebuild with Kotlin Bitmap/TextureResource or SpatialUI; reject when it cannot be rebuilt |
| `browser.web-api` | block | Migrate item by item to Android/SDK; reject unknown dependencies |
| `runtime.frame-loop` | rebuild | ECS System.update |
| `runtime.object-pool` | rebuild | Scene lifecycle resource pools |
| `runtime.resource-lifecycle` | rebuild | destroy/close/unregister/cancel |
| `runtime.lod` | approximate | Tiered assets and distance systems |
| `runtime.culling` | rebuild | Engine culling first; retain necessary visibility logic |
| `runtime.batch` | direct/rebuild | MeshInstancesResource or shared resources |

## 3. Procedural Content Ownership

Migration results for procedural geometry, textures, material composition, animation, particles, trails,
and decals must demonstrate native Spatial SDK capabilities:

- Use `MeshResource` for base shapes.
- Use `MeshModel` for custom vertices, indices, UVs, and normals.
- Use `MeshInstancesResource` for repeated instances.
- Use ECS Systems and runtime resource updates for dynamic behavior.
- Use bounded entity pools, instances, or dynamic meshes for particles and trails.

Exporting or baking the above content into GLB, USD, OBJ, PLY, SPZ, images, videos, animation files,
or Spatial Editor bundles is prohibited. When code-side capability is insufficient, choose a code
approximation, deletion of non-core content, or admission rejection; visual similarity does not
justify assetization.

Only files that already existed in the `asset.*` inventory before migration may enter the target assets.
Format conversion must preserve a one-to-one source relationship, and the contract must record the
original path, target path, and conversion method.

`editor_authored` covers only `material.*` capabilities: shader semantics are reconstructed by
ShaderGraph, and the contract records the graph source file, evaluation evidence, and Kotlin loading
code. Geometry, animation, particles, trails, decals, and procedural textures must not be pre-authored
through Spatial Editor.

## 4. Full Web Page Experience

Page migration is performed per complete page, not per Three.js canvas. All visible page regions,
navigation, forms, overlays, HUD, state, input, and responsive modes must be included in
`experience-inventory.json` and mapped one-to-one in the migration contract.

Complex layout is not itself a reason for rejection. Prefer rebuilding the information architecture,
visual hierarchy, and interaction states with SpatialUI/Compose; only when content genuinely depends
on browser-specific runtime and has no native expression may it be degraded or blocked, after
attempt evidence is left behind.

## 5. Coordinates and Camera

Both Three.js and Spatial 3D coordinates can be treated as metric right-handed spaces, but the source
project's units must not be assumed to be meters. The migration contract must state:

- Evidence of the source units and the target metric ratio.
- The conversion from the source forward axis and the model forward axis to the target Stage forward `-Z`.
- The source scene AABB for the fully assembled state and all range-changing states.
- The clipped AABB measured at runtime for the target 3D space region under the current container and
  full page layout (the current probe implementation covers the actual `SpatialView` 3D render region).
- The available AABB after the full UI layout is retained.
- The unified fit transform of the scene root computed from the above boundaries.

The source AABB is produced by `three-scene-aabb-probe.mjs`; the target visible AABB is produced by
`SpatialViewVisibleRegionProbe.kt`. Both kinds of raw JSON must include the producer, run context,
context fingerprint, raw box, and 8 corner points. `validate_spatial_fit.py` only recomputes and
validates these artifacts; it does not perform measurement.

Numeric units in the source scene have no default physical meaning. A model `scale=1`, camera distance,
or nominal asset size must not be interpreted directly as a target metric size. First establish
physical units with `units_to_meters`, then use `uniform_scale` to fit the reference-state AABB
proportionally within the available region; the target transform must pass recomputation by
`validate_spatial_fit.py`.

Every layout profile and range-changing state must participate in the clipping check. Static
screenshots, a subject that "looks complete", or a single default frame cannot prove that the near
end, edges, and depth direction are not clipped.

A Three.js camera is not migrated as a render object, but the user-visible viewpoint semantics it
expresses must be migrated. Extract:

- the look-at target and the relative distance to the subject;
- the initial visible range;
- the near/far layering;
- the orientation, pitch, scale, look-at target, and focus region of named viewpoints;
- whether pointer interaction changes the observation orbit, the look-at target, or projection parameters;
- whether the desktop camera controls used for debugging can be removed.

That the system camera cannot be modified directly only changes the implementation means; it does not
automatically constitute an experience degradation. For a single observation view, prefer computing
the inverse transform from the source camera's relationship to the target and applying it to the scene
root, a model wrapper, or a dedicated view root; translating the look-at target, rotating the orbit,
and scaling the distance are also maintained by that proxy layer. Named viewpoints, orbiting, panning,
and zooming count as retained only after these paths are actually completed and verified.

`render.multi-camera` only refers to multiple projections, multiple Passes, per-eye cameras, or image
compositing within the same frame. A source project that has multiple camera presets, switches a
single camera at different times, or uses OrbitControls to change one observation view must not be
classified as a multi-camera hard block.

If the core experience requires the application to control projection matrices, per-eye cameras,
RenderTarget cameras, or multi-camera compositing, default to `block`.

## 6. Materials and Post-Processing

Mechanically rewriting GLSL text into Kotlin, or into rewritten GLSL source, is prohibited.
`material.*` capabilities are handled in the following order:

- Evaluate ShaderGraph when three conditions hold: shading applies only to the surface or vertex
  stage; external data can map to node input port types; and the required computation can be expressed
  by existing nodes or a Custom Function.
- When the conditions hold and every contract state can be equivalently reconstructed, use
  `ShaderGraphMaterial` to produce a material bundle through the Editor pipeline and record the mapping
  as `rebuild`.
- When only visual closeness is achieved, record the mapping as `approximate` and record the visible
  differences.
- Approximate with public Unlit/PBR parameters, textures, transparent blending, and geometric layering.
- Remove non-core effects; reject conversion for core effects.

Semantics outside the graph model are treated as blocked: self-managed render pipelines and multiple
Passes, render targets/MRT, GPU compute, custom blend equations and stencil operations, `uniform`
declarations and shader variants inside GLSL, uniform arrays or structs, `half`, and `samplerCube`
inside a Custom Function. In addition, the bundle build channel must be confirmed available; when a
bundle cannot be compiled and produced through the Editor, ShaderGraph is not an available
implementation option.

The first use of ShaderGraph requires PSO warm-up (local experience records give about 650 ms at the
Lit level and about 450 ms at the Unlit level, data pending re-measurement); migration planning should
control the number of graphs within the same load batch and record the measured warm-up cost during
the optimization evaluation stage.

## 7. Runtime Boundaries

- Continuous logic goes in custom ECS Systems, registered/unregistered with the container.
- Compose `SpatialView.update` responds only to state changes.
- The system renderer, camera, and XR framebuffer are not migrated to the application.
- Every provider, listener, coroutine, Entity, and Resource must have symmetric cleanup.
