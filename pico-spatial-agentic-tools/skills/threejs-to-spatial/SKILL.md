---
name: threejs-to-spatial
description: Convert native Three.js projects into PICO Spatial SDK spatial apps. Use when migrating Three.js, WebGL, or WebXR frontend projects. Do not use for React Three Fiber or existing Spatial app patches.
license: 'Apache-2.0'
---

# Three.js To Spatial

Convert a native Three.js project into a new PICO Spatial SDK Android/Kotlin
project by rebuilding supported semantics. This is a gated, lossy migration, not
source-to-source translation. Pursue complete source-visible behavior and page
experience first while expressing code-owned content through Spatial SDK native
capabilities. Reduced fidelity is an evidenced, user-approved exception,
not the implementation target.

## When to Use

- Converting a native Three.js/WebGL/WebXR project into a PICO Spatial SDK app
- Migrating Three.js scene graphs, materials, and interactions to Spatial ECS
- Planning the architecture mapping from Three.js to Kotlin Spatial SDK

## When NOT to Use

- React Three Fiber or framework-wrapped Three.js — not supported by this skill
- Patching an existing Spatial SDK app — use `spatial-app-dev-workflow`
- Porting a 2D Android app — use `porting-android-app`

## Boundaries

Accept:

- JavaScript or TypeScript projects that import `three` or `three/addons`.
- Static scenes, loaded assets, animation, bounded runtime behavior, common
  interactions, audio, and the complete surrounding web page experience.
- A new output project created with the locally available Spatial SDK.
- Existing source-authored model, texture, audio, and video files whose
  provenance can be traced to the input project.
- Editor-authored ShaderGraph material bundles for an inventoried shader whose
  semantics stay within surface or vertex shading, whose inputs map to graph
  node ports, and whose bundle build channel is available.

Reject before project generation:

- React Three Fiber, Threlte, TresJS, Babylon.js, or another scene abstraction.
- A request to patch an existing Spatial SDK project.
- A source whose core experience depends on an unsupported renderer pipeline,
  arbitrary GLSL that ShaderGraph cannot reproduce, GPU compute, render targets,
  multi-camera composition, or complex browser runtime behavior.

Use Spatial Editor and ShaderGraph as a fidelity path for inventoried shader and
material semantics, delivered through the editor bundle. ShaderGraph covers
surface and vertex shading: evaluate it first for a shader whose stage, inputs,
and node coverage all fit the graph model, and mark the capability `approximate`
or `block` when any of those three conditions fails. Do not use WebView or a
retained Three.js runtime. The generated app owns its scene in Kotlin with
Spatial ECS and rebuilds the complete page UI, state, navigation, overlays, and
controls with SpatialUI.

Programmatically created geometry, animation, particles, trails, decals, and
procedural textures remain code-owned. Rebuild them with Kotlin, ECS,
`MeshResource`, `MeshModel`, `MeshInstancesResource`, runtime materials, and
systems. Shader-defined source materials are the exception: reproduce them
through ShaderGraph when the stage and inputs fit and evaluation proves
equivalence, and keep the material loading and scene wiring in Kotlin. Never
export or bake code-owned content into GLB, USD, OBJ, images, a Spatial Editor
bundle, or another prefabricated asset.
If a code-owned source capability cannot be expressed with the admitted Spatial
APIs, approximate it in code, drop it when non-core, or reject the migration.

## Required References

Read these files in phase order:

1. `references/threejs-capability-taxonomy.md`
2. `references/spatial-capability-mapping.md`
3. `references/artifact-contract.md`
4. `references/admission-policy.md`
5. `references/conversion-playbook.md`
6. `references/optimization.md`
7. `references/verification.md`

For exact Spatial SDK symbols, inspect the locally selected SDK's public
documentation, template, or dependency source. Never infer a current API from a
different SDK version.

## Workflow

### Phase 1 - Discover Environment And Source

Run the PICO environment check before calling `pico-cli` or an SDK knowledge
server. Discover, do not hardcode:

- highest locally usable stable Spatial SDK version;
- available `planar`, `volumetric`, and `stage` templates;
- Android/JDK and emulator readiness;
- the runtime probe path for the actual target 3D spatial region's clipping box
  under the selected container and final page layout;
- source Three.js version, entrypoints, build tool, modules, assets, and UI.

Write `environment.json` and `source-project.json`. Stop if the source framework
is outside the supported boundary.

### Phase 2 - Inventory Semantic Capabilities

Use the taxonomy to inspect imports, constructors, method calls, configuration,
assets, shader strings, render-loop code, DOM, and external runtime libraries.

Prefer an AST parser already present in the source project. Do not install a
parser into the source. If no parser is available, use `rg` to collect
candidates and inspect the relevant source manually.

Every inventory item needs a stable capability id, source file and line,
criticality, confidence, and concise evidence. Asset capabilities also need the
paths of files that already exist in the source project. Text matches are
candidates, not high-confidence conclusions.

Write `experience-inventory.json` for the entire page, including every route or
page, visible region, overlay, user-visible state, transition, user flow,
keyboard/pointer/touch/XR input, responsive mode, and visual baseline. The
Three.js canvas is one region in this inventory, not the complete product.

Copy `assets/probes/three-scene-aabb-probe.mjs` into temporary source
instrumentation. Run `measureThreeSceneAabb` in the source runtime after each
complete assembled, animation, interaction, or view state settles, and save
each returned object as an unedited JSON measurement artifact. Record the
source-unit meaning separately. Source object `position`, `scale`, camera
distance, or model dimensions are not target meter values. A manually authored
AABB is not measurement evidence.

Validate:

```bash
python3 scripts/validate_inventory.py \
  --source-project <scratch>/source-project.json \
  --inventory <scratch>/capability-inventory.json

python3 scripts/validate_experience.py \
  --inventory <scratch>/experience-inventory.json
```

### Phase 3 - Map And Admit

Map every inventoried capability to exactly one level:

- `direct`
- `rebuild`
- `approximate`
- `drop`
- `block`

Include a version-specific public API evidence string for every `direct`,
`rebuild`, or `approximate` mapping. An unverified Spatial symbol is not usable;
mark the item `block` until it is verified.

Choose mappings in this order: native Spatial API, ShaderGraph reproduction for
inventoried `material.*` capabilities that stay within surface or vertex
shading, Kotlin/ECS rebuild, Kotlin/ECS approximation, non-core drop, rejection.
Asset baking is not a mapping level and cannot improve the admission score. When
ShaderGraph reproduces the shader semantics with equivalent behavior for every
contracted state, record the mapping as `rebuild`; record `approximate` only for
a visually close result with behavioral or quality difference.

Score the mapping:

```bash
python3 scripts/score_admission.py \
  --inventory <scratch>/capability-inventory.json \
  --mapping <scratch>/mapping-report.json \
  --output <scratch>/admission-report.json
```

Admission measures whether a complete implementation path exists, not whether
the generated app has already implemented it. A `rebuild` mapping can retain
full admission credit, but it earns no delivered outcome credit until the
behavior is implemented and exercised through the source-equivalent user flow.
Never turn an unfinished interaction or view implementation into a platform
limitation.

Proceed only when:

- no capability is `block`;
- no core capability has low scan confidence;
- weighted experience score is 100.

`100` is the target. `70` is only the absolute lower bound for a proven,
user-approved degradation; it is never a target, quality bar, or reason to stop
implementation. Every experience-impacting `approximate`, `drop`, or `block`
must record the native approaches attempted, evidence, and concrete limitation.

When the score is 70-99, emit `needs_degradation_approval`, present every gap,
and stop. Continue only after the user explicitly approves all listed gaps in
`degradation-decision.json`, then rerun `score_admission.py` with `--decision`.
Below 70 or on any blocker, reject the migration.

On rejection, deliver the reports and minimum source-side changes that could
remove blockers. Do not create an Android project.

### Phase 4 - Freeze The Conversion Contract

Write `conversion-contract.json` and `verification-plan.json`.

Before writing fit values, create a temporary SDK-version-matched probe harness
under scratch using the selected container and the frozen final page-layout
geometry. For SpatialView-hosted regions, copy
`assets/probes/SpatialViewVisibleRegionProbe.kt` into that harness, change only
its package declaration, and attach `captureSpatialViewVisibleRegion` to the
exact planned `SpatialView` modifier. Bind the same probe from the
`SpatialView.initial` callback. Run the harness and save the emitted
`SPATIAL_FIT_MEASUREMENT` JSON for every layout profile. The probe reads the
final 3D Compose layout size and converts all eight local-view corners through
`SpatialViewContent.convertPosition`.

The contract must account for every capability and explicitly list:

- target SDK version and container template;
- entity hierarchy and resources;
- source-state AABBs, source-unit-to-meter evidence, and axis mapping;
- the actual target 3D spatial region's runtime-measured clipping AABB in
  meters for every distinct container and page-layout profile;
- the usable AABB after the complete UI layout and clearance are reserved;
- the uniform fit scale, translation, and calculated target AABB for every
  measured source state;
- ECS systems and lifecycle;
- animation, interaction, physics, audio, and SpatialUI mappings;
- approximated and dropped behavior with user-visible loss;
- code ownership for every implemented capability, including every
  `editor_authored` material capability, its authored graph source, and the
  Kotlin loading code;
- source-existing assets, their provenance, and their approved handling;
- complete page, region, state, flow, input, and responsive-mode mappings.

Every `source_bounds[]` and `visible_region` records its probe output in
`measurement_file`. Paths are resolved relative to
`conversion-contract.json`. `validate_spatial_fit.py` is only a validator: it
loads these files, verifies producer metadata and context fingerprints, and
recomputes each AABB from the raw corners. It does not perform measurement and
must never be cited as measurement evidence.

Validate:

```bash
python3 scripts/validate_conversion_contract.py \
  --inventory <scratch>/capability-inventory.json \
  --mapping <scratch>/mapping-report.json \
  --contract <scratch>/conversion-contract.json

python3 scripts/validate_spatial_fit.py \
  --contract <scratch>/conversion-contract.json

python3 scripts/validate_experience.py \
  --inventory <scratch>/experience-inventory.json \
  --contract <scratch>/conversion-contract.json \
  --verification-plan <scratch>/verification-plan.json
```

The scratch probe harness is measurement instrumentation, not target
implementation. Do not generate target scene or application code until these
commands pass.

### Phase 5 - Generate The New Spatial Project

Create a new project with the version and container frozen in the contract:

```bash
pico-cli project create \
  --dir <output> \
  --name <name> \
  --package <package> \
  --template <planar|volumetric|stage> \
  --sdk <discovered-version>
```

Implement only the frozen contract. Use:

- Entity hierarchy and `TransformComponent` for the scene graph;
- the frozen axis conversion, meter conversion, uniform fit scale, and
  translation on one scene or view root;
- public mesh, material, texture, model, animation, physics, tracking, audio,
  and interaction APIs verified for the selected SDK, including
  `ShaderGraphMaterial` loading for contracted surface- or vertex-stage
  editor-authored materials;
- lifecycle-scoped ECS `System.update` for continuous behavior;
- SpatialUI under `PicoTheme` for the complete page and application flow.

Preserve or format-convert an asset only when it already exists in the source
inventory and the contract records its source path. An `editor_authored`
material bundle enters only when the contract records its authored graph source,
shader stage, and evaluation evidence. Do not create a model or image asset from
procedural source code. Define matching cleanup for entities, resources, systems,
providers, listeners, and coroutines.

### Phase 6 - Evaluate Lossless Optimization

Follow `references/optimization.md`. Migration alone is not a delivered result:
the spatial app must keep the complete business behavior and measured
performance that meets the contracted budget. A generated app that merely
reproduces the web experience can ship slower than its source.

Before verification:

- measure the current build on the contracted device, ROM, SDK version, and
  container, with every contracted page, state, and flow reachable;
- record frame time, stutter, draw calls or batches, instance and vertex counts,
  texture and mesh memory, startup or first-frame latency, and ShaderGraph warm-up
  where used;
- apply behavior-preserving optimizations such as instancing, batching, LOD,
  texture compression, draw-order grouping, UI recomposition, and bounded ECS
  systems;
- prove each optimization preserves the contracted visual and interaction
  semantics;
- write `optimization-report.json`.

Validate:

```bash
python3 scripts/validate_optimization.py \
  --report <scratch>/optimization-report.json \
  --inventory <scratch>/capability-inventory.json
```

Proceed to verification only when every contracted measurement passes its budget
and every optimization is lossless with evidence. A budget miss after all
lossless optimizations stops the conversion: report the measured gap, and either
revise the contract or request user approval through
`degradation-decision.json`. Never hide a budget miss behind a passing build,
and never count an unmeasured optimization as a gain.

### Phase 7 - Verify

Follow `references/verification.md`. Completion requires:

- all contract and static checks pass;
- the optimization report passes with every contracted budget met and every
  optimization lossless;
- Gradle discovery, build, and unit tests pass;
- emulator install and launch pass with no detected crash; ANR verification requires independent ANR-capable evidence;
- source and target are compared at the same semantic views and construction
  keyframes;
- every page/state/viewport has a target capture;
- every source flow and input in `verification-plan.json` is exercised;
- the current runtime clipping AABB is remeasured and every contracted scene
  state AABB remains inside it without clipping;
- the independent outcome-fidelity target is 100, with only explicitly
  approved degradation allowed below it.

Validate the runtime spatial evidence:

```bash
python3 scripts/validate_spatial_fit.py \
  --contract <scratch>/conversion-contract.json \
  --verification-result <scratch>/verification-result.json
```

The verification result must reference a fresh target probe artifact, not the
contract-time measurement file. Preserve the raw probe JSON without editing.
Runtime state bounds default to exact equality with the source-derived frozen
fit. If the target SDK exposes only conservative native-resource bounds, the
contract may explicitly set `runtime_bounds_policy` to
`conservative-contains-expected` with a non-empty rationale; the runtime bounds
must then contain the frozen fit and remain fully inside the freshly measured
visible region.

Record feasible but unfinished behavior in `implementation_gaps`. Any such
entry makes the outcome `incomplete`; user degradation approval cannot convert
missing implementation into delivered behavior.

If the emulator or device is unavailable, report
`implemented_unverified_runtime`; do not claim the conversion complete.

## Hard Rules

- The capability inventory, mapping report, and frozen contract are the only
  authority for generation.
- Programmatic source content stays `kotlin_code` owned; only inventoried
  source files may use `source_asset` ownership; only inventoried `material.*`
  capabilities whose semantics stay within surface or vertex shading may use
  `editor_authored` ownership.
- Never bake procedural geometry, animation, effects, or procedural textures
  into model, image, or editor-bundle files.
- Unknown source APIs and unverified Spatial APIs block their path.
- Renderer and system-camera ownership stay with PICO Spatial Engine. Source
  viewpoint semantics remain application-owned: rebuild them through inverse
  scene-root transforms, view wrappers, fit/framing state, or another verified
  native representation before declaring a camera limitation.
- Do not classify named camera presets, single-view orbit, pan, zoom, or model
  inspection as `render.multi-camera`. That blocker is reserved for
  simultaneous application-controlled projection, per-eye cameras, or
  multi-camera render composition.
- A planned or declared `rebuild` is not implementation evidence. Missing
  interaction scores as missing interaction, even when the APIs and design are
  known.
- Never translate arbitrary shader source into Kotlin or rewritten GLSL text.
  Evaluate ShaderGraph only for a shader whose stage, graph-node coverage, and
  input types all fit; uniform arrays, structs, shader variants, `half`,
  samplerCube inside a custom function, custom blend equations, render targets,
  multi-pass composition, and GPU compute stay outside that path.
- Never claim completion while any contracted performance budget fails, and
  never treat a passing build or a working feature as a performance result.
- Never record an optimization gain without before-and-after measurement on the
  same device, ROM, SDK build, and container.
- Never trade contracted visible or interaction behavior for performance outside
  the recorded degradation path.
- Never hide a deletion or approximation behind a successful build.
- Never lower a capability's criticality to pass admission.
- Always pursue 100% capability and outcome fidelity first. Never treat 70 as
  the target, definition of done, or permission to stop.
- Never lower the target without failed native approaches, concrete evidence,
  and explicit user approval recorded in `degradation-decision.json`.
- Never copy source model scale, position, camera distance, or nominal asset
  dimensions into the target as if they were meters. Derive the root transform
  from measured source AABBs, explicit unit evidence, and the current runtime
  clipping box.
- Do not generate target scene code until every spatial layout profile passes
  `validate_spatial_fit.py`. Do not claim visual completion until runtime
  bounds for every contracted state pass the same validator.
- Never hand-fill `measurement_file` outputs or describe
  `validate_spatial_fit.py` as a measuring tool. Missing probe output, missing
  producer metadata, missing raw corners, or an AABB not derived from those
  corners blocks generation.
- Never use the admission score as completion, visual, or interaction evidence.
- Never treat the Three.js canvas as the whole project. Page UI, state,
  navigation, overlays, responsive behavior, and user flows are first-class.
- Never replace a complete page with a minimal demo, control panel, or showcase.
- Never merge distinct visible source semantics into one generic acceptance
  item. Construction timing, view presets, narrative UI, base/environment,
  silhouette/proportion, and palette/material response remain separately
  accountable when present.
- A visible loss in a `visual_core` or `interaction_core` capability must be
  represented in the outcome-fidelity rubric and source/target evidence.
- Never use `SpatialView.update` as a frame loop.
- Never create a partial Android project after admission fails.

## Handoff

Report:

- source path and detected Three.js version;
- selected Spatial SDK version and target container;
- measured clipping AABB, source AABB states, meter conversion, usable region,
  uniform fit scale, and runtime clipping result;
- admission score, 100-point target, shortfall, and degradation approval state;
- page/region/state/flow/input coverage counts;
- direct, rebuilt, approximated, dropped, and blocked capability counts;
- editor-authored material bundles, their authored graph sources, shader stage,
  and the shader capabilities they reproduce;
- optimization budget, measured results, applied lossless optimizations, and any
  remaining measured gap;
- output project path when admitted;
- build, runtime, visual, and interaction evidence;
- outcome-fidelity score and per-dimension scores;
- every remaining visible or behavioral loss.
