---
name: spatial-sdk-guideline
description: Focused PICO Spatial SDK API and diagnostic guide (Android/Kotlin + Spatial ECS). Covers container choices, ECS concepts, resources, rendering, interaction, coordinates/units, and performance constraints; routes Kotlin Entity scene delivery to Scene Builder.
license: 'Apache-2.0'
---

# PICO Spatial SDK 3D Developer

## Description and Goals

Use this skill for focused SDK API guidance, isolated implementation patterns, and non-deliverable diagnosis in **PICO Spatial SDK on PICO OS 6** (Android + Kotlin + Jetpack Compose + Spatial ECS).

Route any requested edit that creates, loads, parents, transforms, arranges, places, or validates a Kotlin `Entity` hierarchy to `spatial-sdk-scene-builder`. This skill may provide the API facts that support that implementation, but it does not own the resulting scene change.

Goals:

- Pick the right container (**WindowContainer** vs **Stage**) and understand space-state constraints.
- Understand **ECS** (entities/components/systems) choices needed for maintainable, performant scene code.
- Explain resource-loading options (**USD preferred**, **glTF/GLB supported**, **AssetBundle** workflow) and their lifecycle constraints.
- Diagnose interaction prerequisites (**programmatic hit testing** needs `CollisionComponent`; **user interaction** needs `CollisionComponent + InteractableComponent`, plus targeting/gestures patterns).
- Avoid common pitfalls (threading, coordinate-handedness, unit conversions, physics-world scoping).
- Keep content within typical **performance budgets** for 90 fps.

## What This Skill Should Do

When asked a concrete SDK question or a diagnosis that does not itself require a Kotlin Entity scene edit, respond with:

1. **Project SDK evidence**: report the exact Spatial SDK BOM/version and the project file that declares it. Also report whether the nearest project `.pico-env.json` selects the matching major/minor knowledge line.
2. **Recommended approach** (what to use, where it lives, why), explicitly stating whether every non-trivial or version-sensitive API is available in that project SDK.
3. **Minimal implementation pattern** (small Kotlin snippet or pseudocode) that is compatible with the inspected project version.
4. **Checklist** to validate assumptions and catch common gotchas.
5. Links to the most relevant curated pages under `reference/`, plus any deeper support retrieved via `pico-dev-knowledge` MCP when the question needs broader or version-specific lookup.

Do not skip project inspection merely because the user asks a short API question. Read the actual version declaration, including version-catalog indirection such as `gradle/libs.versions.toml`, before recommending an API. If no project is available or the exact BOM cannot be resolved, say that compatibility is unverified and ask for the build files or exact version instead of silently assuming the newest installed SDK.

Treat the BOM and `.pico-env.json` as separate evidence:

- The exact BOM controls which APIs the project can compile against.
- The nearest project `.pico-env.json` selects the major/minor knowledge line. For example, BOM `6.0.x` must use knowledge line `6.0`, while BOM `6.1.x` must use `6.1`.
- If the project selector is missing or mismatched, identify a **knowledge-context mismatch**. Do not present MCP or globally selected knowledge as authoritative for the project. Continue with version-matched project files, release notes, examples, or SDK artifacts; recommend aligning the project selector before a fresh Agent session uses MCP knowledge.
- A matching knowledge line is necessary but not sufficient for patch-level API availability. Verify introductions, removals, and signatures against the exact BOM and, when code is changed, compile it.

When the user explicitly asks about an API unavailable in the current BOM, do not show it as project-compatible code. Give a compatible alternative first. You may describe the minimum SDK upgrade separately, including the required BOM and matching knowledge selector, without silently changing the project's SDK target.

For **model loading** answers, do not stop at the API call. Explicitly cover all of these points in the prose:

- Whether the requested model format is supported (`glTF/GLB` supported; `USD` preferred).
- The recommended loading path (`Entity.loadSuspend("asset://...")`, or synchronous `Entity.load(...)` inside `withContext(Dispatchers.IO)`).
- In Compose / `SpatialView` contexts, one-off loading and scene attachment should happen in `SpatialView(initial = { content, _ -> ... })`, then use `content.addEntity(root)` after loading succeeds. Do not frame this as an `update`-time operation.
- The returned value is the **root `Entity`** of the loaded hierarchy and should be attached to the scene after loading succeeds.
- Mesh-bearing child entities automatically expose `ModelComponent`.

## Core Concepts

### ECS: Entity / Component / System

- **Entity**: node in a hierarchy with a set of components.
- **Component**: data/config attached to an entity.
- **System**: per-frame logic (`update(SceneUpdateContext)`), usually driven by queries.
- **Scene**: owned by a container; queries and event subscriptions are scene-scoped.

Practical rule:

- Put one-off setup in spawn/initialization.
- Put continuous behavior in a **system**.

### Containers and Space States

**WindowContainer**

- Bounded content area; anything outside is clipped.
- Runs in **Shared Space** (multitasking) or can exist alongside Stage in Full Space.

**Stage**

- Unbounded immersive 3D container.
- **Full Space only**; opening Stage transitions the app to Full Space.
- **Only one Stage open at a time** per app.
- Right-handed coordinate system (+X right, +Y up, **+Z toward the user**). Origin at the user's feet.
- Configure a custom skybox + IBL before opening Stage; otherwise the environment appears black.
- `style` is chosen when calling `openStage(...)`; it cannot be changed dynamically after the Stage is open.

### Resources and Rendering

- **Models**: USD (`.usd/.usda/.usdc/.usdz`) preferred; **glTF/GLB supported**.
- **AssetBundle**: Editor-authored `.bundle` stored in APK assets; load via `AssetBundle.load("asset://...")`.
- First-class resource types: `MeshResource`, `Material` variants, `TextureResource`, `AnimationResource`, `ShapeResource`, etc.

### Coordinates and Units

- 3D spaces (Entity/Stage/SpatialView): generally **right-handed, meters**.
- 2D view space (Compose/View in a WindowContainer): **left-handed, virtual pixels** with +Y down.
- Mixing 2D + 3D requires **explicit conversions** (space + unit).

## Components Reference (By Topic)

> Detailed, self-contained references are bundled under `reference/`.

### ECS & Scene

- Entity hierarchy, components, systems, queries, cloning, events:
  - [ECS and Entities](reference/ecs-and-entities.md)

### Resources Loading

- USD/glTF loading, AssetBundle workflows, resource lifecycle:
  - [Resources Loading](reference/resources-loading.md)

### Materials, Lighting, Effects

- Unlit/PBR, blending, IBL, shadows, opacity, portal, transparent sorting:
  - [Materials, Lighting, and Effects](reference/materials-lighting-effects.md)

### Animation

- Skeletal/blendshape/tween/timeline, playback control, main-thread rules:
  - [Animation Playback and Control](reference/animation-playback.md)

### Physics & Collision

- Rigid bodies, collision shapes, physics world scoping, raycasts, events:
  - [Physics and Collision](reference/physics-collision.md)

### Interaction & Hit Testing

- Collision + Interactable prerequisites, targeting, gestures, hover, unit mapping:
  - [Interaction and Hit Testing](reference/interaction-hit-testing.md)

### Coordinates & Units

- Handedness, origins, conversion APIs, dp/px/meter helpers:
  - [Coordinates and Units](reference/coordinates-and-units.md)

### Performance

- Budgets, optimization checklists, common bottlenecks:
  - [Performance Budgets and Optimization Checklist](reference/performance-budgets.md)

## Playbooks

Sub-flows that compose this skill for specific scenarios live under `playbooks/`:

- [Scene Surface Placement](playbooks/scene-surface-placement.md) — placing entities on real-world planes (wall/table/floor) using `PlaneTrackingManager` and Stage.

## Implementation Patterns

### Pattern: Load and place a model asynchronously

- Prefer `Entity.loadSuspend("asset://...")` for the recommended async path.
- If you show synchronous loading, wrap `Entity.load(...)` in `withContext(Dispatchers.IO)`.
- `Entity.loadSuspend(...)` may be called directly on the main thread; after loading completes, entity/component operations return to the main thread.
- If the user asks about `.gltf` / `.glb`, explicitly say that **glTF/GLB is supported**, while **USD is still the preferred format** when the pipeline is under your control.
- In Compose container examples, prefer `SpatialView(initial = { content, _ -> ... })` for one-time loading/setup and use `content.addEntity(root)` there.
- Do not tell users to add freshly loaded entities from `update`; `update` is for reacting to state changes after initialization.
- Treat the result as a root entity hierarchy; mesh-bearing child entities expose `ModelComponent` automatically.
- Do not invent wrapper APIs such as `GLTFResource.load` or `ModelResource` for standard model loading answers.
- Add the loaded root entity to the scene/content only after success.
- Keep a clear ownership model for resources (who closes what, and when).

Recommended wording points for asset-loading answers:

- “`Entity.loadSuspend("asset://robot.glb")` is the recommended async loading path.”
- “In a `SpatialView`, load once in `initial` and call `content.addEntity(robotRoot)` after the load succeeds.”
- “The returned value is the root `Entity` of the loaded hierarchy, so add that root to the scene/content rather than only operating on a child.”
- “Child entities always have `TransformComponent`, and mesh-bearing child entities automatically expose `ModelComponent`.”

Minimal Kotlin pattern:

```kotlin
SpatialView(initial = { content, _ ->
  val robotRoot = Entity.loadSuspend("asset://robot.glb")
  content.addEntity(robotRoot)
})

// If you need mesh/material access later, inspect mesh-bearing child entities via ModelComponent.
```

### Pattern: Make an entity hittable and interactive

- Distinguish **programmatic hit testing** from **user interaction**.
- For `scene.rayCast(...)` / `scene.convexCast(...)`, the target only needs `CollisionComponent`.
- Add `CollisionComponent` with shapes.
- Add `InteractableComponent` when the user needs gaze/tap/drag interaction.
- If using gaze feedback: add `HoverEffectComponent`.
- Use targeting (e.g., `TargetEntity.any()` or `targetedToEntity = ...`) to scope gestures.

### Pattern: Control animations safely

- In Compose examples, prefer loading the animated entity once in `SpatialView.initial`, adding it with `content.addEntity(...)`, then starting playback on the main thread.
- For skeletal-animation answers, follow the official pattern: load the animated model root, then call `findSkinnedMeshEntity()` to get the skinned-mesh entity array/list, iterate it, and call `getAnimationResources()` on each skinned mesh entity before playing animation.
- For minimal looping examples, prefer the documented explicit-repeat form `val repeat = clip.repeat(3)` and then `repeat.use { skinnedMeshEntity.playAnimation(it) }` instead of inventing an “infinite repeat” helper.
- Make Timeline answers explicit: Timeline entities are played with `playTimeline()`, not `playAnimation()`.
- Mention `AnimationPlaybackController` when the user needs pause/resume/stop control, but do not force it into the smallest “just start looping” example.
- Keep the `AnimationPlaybackController` handle.
- Call animation APIs on the **main thread**.
- Close controllers when no longer needed.

### Pattern: Configure physics correctly

- Ensure interacting objects share the same `PhysicsWorldComponent` ancestor (or none).
- For physical collision response (blocking/bouncing), both sides must use `CollisionResponseMode.COLLIDER_FULL`.
- If the object should respond to gravity/forces, use `RigidBodyMode.DYNAMIC`.
- For minimal collision demos, explicitly show the shared `PhysicsWorldComponent` setup in code instead of only mentioning the default global world.
- Prefer simple collision shapes.
- Use raycasts for selection and interaction debugging.

### Pattern: Convert spaces and units explicitly

- Always state (in code and comments) the **source space** and **target space**.
- Convert **full transforms** (position + rotation + scale) when moving across containers.
- Convert units (dp/px ↔ meters) using the provided converters.

### Pattern: Answer Volumetric sizing questions without inventing a contract

Read [Coordinates and Units](reference/coordinates-and-units.md) before answering about a
Volumetric WindowContainer's size, unit, range, or default. The answer must preserve all of these
boundaries:

- Volumetric sizes may be expressed in **dp or meters**. Do not present either unit as the only
  supported choice.
- Never use a fixed dp-to-meter ratio. Convert with `PhysicalLengthConverter` (for Compose, obtain
  it through `LocalPhysicalLengthConverter.current`) and disclose that `worldScale` can affect the
  observed physical result.
- Treat `320 x 320 x 320` through `2700 x 2700 x 2700` as design guidance / an Editor-supported
  authoring range, not as a proven runtime hard limit.
- The available PICO OS 6.1 knowledge sources conflict on the default: one says
  `960 x 960 x 960`, another says `1280 x 1280 x 1280`. Report the conflict explicitly; do not
  select either value as authoritative. Ask for a target-version runtime/Editor check or an SDK
  owner ruling before claiming a default.

## Investigation Order

Before proposing a new implementation strategy, gather knowledge in this order:

1. Inspect the user's project-local files (build files, version catalogs, manifests, dependency declarations) to identify the exact Spatial SDK BOM, current implementation, and failure signal. Record the declaring file in the answer.
2. Inspect the nearest project `.pico-env.json`. Compare its knowledge `version` / `agentVaultWorkspace` major-minor line with the BOM; do not silently fall back to a global selector when answering for a project.
3. Read the most relevant skill instructions for workflow/routing guidance.
4. Query `pico-dev-knowledge` MCP for non-trivial SDK/API facts, version-sensitive behavior, or cross-reference discovery only after checking its project version alignment.
5. Read related bundled references and project-local examples that match the exact SDK version.
6. Verify current behavior through code inspection, builds, logs, or runtime evidence.
7. Inspect `source.jar` or SDK binaries only as last-resort source validation or exact-symbol checks.

Do not start with `source.jar` when knowledge graph context, higher-level docs, examples, and project evidence are available. Do not replace an existing implementation strategy until the current one is proven incorrect.

If `pico-dev-knowledge` is unavailable, continue with skill guidance, bundled references, and project evidence, and explicitly state that the MCP lookup could not be performed.

## SDK Development Safety Rules

- **Prefer ECS for 3D runtime behavior.** For non-trivial 3D content, scene state, animation, interaction, physics, anchors, or entity transforms, design around ECS entities/components/systems rather than using Compose or `SpatialView` recomposition as the primary 3D driver. Use `SpatialView(initial = { ... })` for one-time setup and attachment; keep per-frame or sensor-driven 3D changes inside ECS systems, SDK tracking callbacks, or explicit entity/component updates.
- **Keep sensing and tracking paths low-latency.** When using `sense`, plane/world/mesh tracking, controller/hand/body/HMD pose data, or other high-frequency spatial input, avoid routing data through 2D UI state and back into 3D from `SpatialView.update`. Prefer direct ECS-side updates, coalesced component writes, or SDK callback-to-entity pipelines with minimal main-thread work.
- **Lifecycle cleanup is mandatory.** Any code that starts tracking, registers listeners, opens containers, creates ECS entities, loads resources, or launches coroutines must define the matching cleanup path for disposal, app pause/stop, or container close.
- **Surface and anchor work needs runtime evidence.** For plane, wall, table, anchor, room-geometry, or placement features, do not claim correctness from code alone. Verify with emulator/device capability checks, logs, screenshots/recordings, or clearly state that physical-device validation remains pending.
- **Interaction requires both input and collision evidence.** For tap, raycast, grab, drag, rotate, scale, or controller interaction bugs, check input source/controller state, target transforms, collision/hit-test components, entity visibility, and coordinate space before replacing the interaction model.
- **Entity and animation APIs are `@MainThread`.** Entity/component operations return to the main thread after async loading; animation playback, controller management, and timeline APIs are also main-thread-only. Offloading them to background threads causes silent corruption or crashes.
- **`@ExperimentalSpatialApi` means unstable — disclose, opt-in, and guard.** APIs annotated with `@ExperimentalSpatialApi` may be renamed, changed, or removed in a future SDK version. Apps using them may be blocked from market publication. When recommending an experimental API, state it is experimental, require the caller to add `@OptIn(ExperimentalSpatialApi::class)`, wrap calls in try-catch to handle behavioral changes or unexpected exceptions gracefully, and note the market risk. Do not silently opt in or suppress the compiler error.
- **Performance fixes require measurements.** For stutter, frame drops, startup latency, high CPU/GPU load, or scene complexity, prefer `pico-cli perf`, Perfetto Trace, log evidence, or reproducible measurements. Do not guess root causes from code structure alone.
- **Asset changes need scale and budget checks.** When adding models, textures, lighting, particles, physics, or animations, consider units, bounding boxes, triangle/texture budgets, loading strategy, and device performance impact.
- **SpatialUI should stay app-side and public.** Use public SpatialUI APIs, PicoTheme roles, built-in components, and documented modifiers. Do not depend on restricted design-system internals or replicate native shell behavior manually unless the user explicitly needs a custom component and accepts the trade-off.

## Pitfalls and Checks

Use this as a pre-flight checklist:

- [ ] Am I in the right container? Stage requires Full Space; WindowContainers clip content.
- [ ] Stage rules: unbounded, **Full Space only**, **only one Stage at a time**, needs custom skybox/IBL, and `style` is not dynamically mutable.
- [ ] Programmatic hit testing needs `CollisionComponent`; user interaction needs **both** `CollisionComponent` and `InteractableComponent`.
- [ ] Gesture input: do not call multiple `detectSpatial*` recognizers in the same `pointerInput` block.
- [ ] Physics: all colliding bodies share the same physics world, and physical-response colliders use `COLLIDER_FULL` on both sides.
- [ ] Coordinates: Stage/Entity/SpatialView are right-handed meters; View space is left-handed pixels.
- [ ] SpatialView teardown is manual: entities are not auto-destroyed when the composable leaves composition.

## References

- [ECS and Entities](reference/ecs-and-entities.md)
- [Resources Loading](reference/resources-loading.md)
- [Materials, Lighting, and Effects](reference/materials-lighting-effects.md)
- [Animation Playback and Control](reference/animation-playback.md)
- [Physics and Collision](reference/physics-collision.md)
- [Interaction and Hit Testing](reference/interaction-hit-testing.md)
- [Coordinates and Units](reference/coordinates-and-units.md)
- [Performance Budgets and Optimization Checklist](reference/performance-budgets.md)

For deeper dives, prefer querying `pico-dev-knowledge` MCP for broader or version-specific documentation, and when source validation is needed, follow the file paths returned in `pico-dev-knowledge` results.
