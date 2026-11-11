# Admission and Degradation Rules

## 0. Scoring Responsibility

The admission score only decides whether it is worth generating the target project. The goal is
always 100% semantic and experiential coverage; it does not authorize the Agent to stop seeking
native implementations after reaching a lower score.

Admission does not evaluate performance. Post-generation runtime cost is judged separately by
`optimization-report.json` and the finished-product fidelity gate; the admission score,
`admitted=true`, or the `rebuild` mapping cannot serve as a performance conclusion.

Post-generation quality is judged by an independent finished-product fidelity gate. The admission
score and finished-product fidelity must not substitute for each other, and `admitted=true` in the
admission report must not be written as visual or interaction acceptance evidence.

## 1. Decision Order

Decide in the following order, and stop immediately when a preceding item fails:

1. The source framework is native Three.js.
2. The capability inventory structure is valid and the confidence of core items is not `low`.
3. Every capability has a unique mapping.
4. All capabilities have no `block`; non-core discards must explicitly use `drop`.
5. First complete all native mapping attempts with a target of 100 points.
6. When below 100, every gap has failed attempts, evidence, and a specific limitation.
7. At 70-99 points, the user has explicitly approved all degradation items.
8. The migration contract is complete, programmatic content retains Kotlin/ECS ownership, and
   neither WebView nor a retained Three.js runtime is used.

Admission failure delivers only analysis artifacts and minimal modification suggestions, and does
not create an Android project.

## 2. Scoring

Weights:

| Criticality | Weight |
|---|---:|
| `visual_core` | 3 |
| `interaction_core` | 3 |
| `runtime` | 2 |
| `infrastructure` | 0 |

Retention coefficients:

| Mapping level | Coefficient |
|---|---:|
| `direct` | 1.00 |
| `rebuild` | 1.00 |
| `approximate` | 0.55 |
| `drop` | 0.00 |
| `block` | 0.00 |

```text
score = sum(weight * coefficient) / sum(weight) * 100
```

The total score cannot override hard blockers: any `block` rejects the project.

States:

- `full`: 100 points.
- `needs_degradation_approval`: 70-99 points, stop generation and request user approval.
- `degraded_approved`: generation is allowed after the user approves all gaps.
- `rejected`: below 70 or a hard blocker exists.

Infrastructure replacement does not affect user experience, so it is not counted in the experience
score. A complete Kotlin/ECS `rebuild` preserves semantics and is not penalized.

## 3. Hard Blockers

Default blockers:

- Non-native Three.js scene abstractions.
- Core shaders that still cannot be reproduced after satisfying the three conditions of the
  surface/vertex stage, mappable inputs, and expressible nodes; self-managed render pipelines,
  multi-pass, render targets, uniform arrays or structs, `half`, and `samplerCube` inside a Custom
  Function all fall into this category.
- When a shader is recorded as `editor_authored` or `rebuild`, the bundle build channel is
  unavailable.
- Core RenderTarget, MRT, screen post-processing, or multi-camera composition.
- Core GPU compute/GPGPU particle or texture simulation.
- Core browser-specific runtime semantics that cannot be rebuilt by SpatialUI/Android.
- Core dynamic code imports whose runtime path cannot be statically resolved.
- Core physics that depends on complex joints, vehicles, or engine-specific behavior.
- Unknown Three.js APIs or third-party extensions control the core experience.
- The target Spatial SDK version cannot verify the required public APIs.
- The migration plan requires baking procedural geometry, animation, effects, or procedural
  textures into external assets, or prefabricating them with Spatial Editor.

## 4. Allowed Degradation

Only non-core capabilities may be directly `drop`ped. Typical allowed items:

- Desktop debug camera and GUI.
- Development-state stats panel.
- Non-core Bloom, tone, or screen flicker.
- Non-core decorative particles.
- Browser-specific resize, pointer lock, or fullscreen controls.

`approximate` must simultaneously satisfy:

- A feasible native Spatial SDK implementation path has been attempted, including a ShaderGraph
  reproduction evaluation for `material.*` capabilities.
- API, runtime, or performance evidence and the specific failure reason are recorded.
- The user purpose of the original capability is preserved.
- Visible or behavioral losses are explicit.
- There are executable acceptance items.
- Neither WebView nor a retained Three.js runtime is used.

Any experience-related `drop|block` must also record the same attempt evidence. 70-99 points is not
an automatic pass condition; it can continue only after the user explicitly approves all
capabilities in `degradation-decision.json`.

The system camera cannot be directly controlled by the application, which is insufficient to prove
that the viewing experience needs degradation. Named viewpoints, single-view orbit, pan, and zoom
should first be mapped to inverse transforms of the scene root or view root. The absence of these
implementations is a delivery gap, not a `block`; only when the application must control the
projection matrix, per-eye cameras, or same-frame multi-camera composition and the alternative path
cannot preserve the core purpose should it be treated as a rendering hard blocker.

## 5. Minimal Modification Suggestions

When rejecting, give source-project modification suggestions per blocker, for example:

- Change core ShaderMaterial to PBR + textures, or reproduce it with ShaderGraph first.
- Change post-processing glow to a geometric shell or emissive material.
- Change multi-camera composition to a single spatial scene.
- Change dynamic Canvas UI to structured text, buttons, and images.
- Replace GPU particles with bounded CPU/instanced particles.
- Reduce complex physics constraints to basic rigid bodies and collisions.
- Rewrite procedural models as MeshResource/MeshModel/Entity compositions instead of exporting GLB.

Suggestions must correspond to real blocker evidence; do not output generic rewrite suggestions.

## 6. Prohibited Ways to Adjust Scoring

- Must not lower criticality in order to pass the threshold.
- Must not mark unverified capabilities as `direct`.
- Must not change a core `block` to `drop`.
- Must not merge multiple high-risk capabilities into one low-weight entry.
- Must not omit capabilities created only dynamically at runtime.
- Must not relabel procedural capabilities as `asset.*` or `editor_authored` to bypass the code
  ownership gate.
- Must not use the admission score to support `verified`, visual pass, or interaction pass.
- Must not treat 70 points as the goal or completion line; must not apply for degradation without
  first pursuing 100 points.
- Must not have the Agent approve `degradation-decision.json` on behalf of the user.
- Must not merge multiple user-perceivable semantics into one broad capability and then use a single
  "existence check" to replace separate acceptance of animation keyframes, viewpoint presets,
  narrative UI, base environment, silhouette proportions, or material color.
