# Acceptance Protocol

## 1. Acceptance Prerequisites

The acceptance target must be an APK built from the current source code, and `optimization-report.json` must have passed.
Record before installation:

- Source code commit or working tree state.
- APK path, timestamp, and SHA-256.
- SHA-256 of `conversion-contract.json` and `verification-plan.json`.
- SHA-256 of `optimization-report.json` and the `validate_optimization.py` result.

## 2. Static Contract Gate

Execute:

```bash
python3 scripts/validate_inventory.py \
  --source-project <scratch>/source-project.json \
  --inventory <scratch>/capability-inventory.json

python3 scripts/validate_experience.py \
  --inventory <scratch>/experience-inventory.json

python3 scripts/score_admission.py \
  --inventory <scratch>/capability-inventory.json \
  --mapping <scratch>/mapping-report.json \
  --output <scratch>/admission-report.json

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

python3 scripts/validate_optimization.py \
  --report <scratch>/optimization-report.json \
  --inventory <scratch>/capability-inventory.json
```

Check:

- Every source capability has a unique destination.
- Every current SDK API has version evidence.
- Approximations and deletions all disclose impact.
- All programmatic source capabilities are implemented by Kotlin/ECS files, with no generated model, image, or animation assets.
- Every file in the target assets can be traced to an existing `asset_paths` in the inventory, or is registered as an
  `editor_authored` material artifact.
- The project has no Three.js or WebView runtime dependency; every Editor or ShaderGraph artifact is registered as an
  `editor_authored` material asset and carries the graph source file, shading stages, and restoration evaluation evidence.
- Continuous logic resides in ECS Systems.
- Creation behavior has symmetric cleanup.
- Source unit evidence, source state AABBs, target clip box, usable region, and the unified fit transform are computable and consistent.
- Every source state and target layout references an actually existing `measurement_file`; its producer,
  context fingerprint, raw boxes, 8 corner points, and derived AABB all pass recomputation.
- All pages, regions, states, responsive modes, flow steps, and inputs have target mappings.
- The optimization report passes: budgets met, every optimization lossless, measurement covering the contract pages and states.

## 3. Build Gate

```bash
./gradlew projects --console=plain
./gradlew :app:testDebugUnitTest :app:assembleDebug --console=plain
```

Pass conditions:

- Gradle can discover the `app` module.
- The unit test count is greater than zero and the failure count is zero.
- The Debug APK is produced.

New projects also need to trigger Android Studio's **Sync Project with Gradle Files**. When the Agent
cannot invoke IDE sync, it must list this pending item separately in the delivery.

## 4. Runtime Gate

First confirm the emulator window is visible and adb is ready, then execute:

```bash
pico-cli app install <apk>
pico-cli app launch <package>
pico-cli app watch-crash <package>
```

`app watch-crash` observes package/PID-correlated crash evidence. It does not
detect an unresponsive process or prove ANR absence. Verify ANR separately for
the same package and observation window; otherwise record ANR verification as pending.

Pass conditions:

- Installation succeeds.
- The target Activity launches successfully.
- The spatial container and 3D content actually appear in the scene.
- In the final page layout, the clip AABB of the target 3D spatial region is consistent with the frozen contract.
- The actual target AABBs of the fully assembled state and of all range-changing states do not cross the clip box.
- No package/PID-correlated crash is detected within the observation window.
- Any claim of ANR absence has independent ANR-capable evidence for that package and window.

The `RESUMED` state of an Android Activity cannot alone prove that spatial content is visible.

## 5. Visual Acceptance

The source Three.js project and the target app use pages, viewpoints, animation progress, and content states
with the same semantics from `verification-plan.json.views[]`. Must include:

- Every page or route.
- Every user-visible state and overlay.
- Every responsive mode.
- The primary 3D viewpoint.
- Every named viewpoint preset provided by the source project.
- A viewpoint that reveals depth, backface, or hierarchy relationships.
- The three construction keyframes `0.25`, `0.50`, `1.00`; add `0.00` when the source animation has a
  significant initial state.

Check item by item:

- Main body silhouette and proportions.
- Entity parent-child relationships and relative positions.
- Source unit to meter conversion, and the subject's physical scale after AABB fitting.
- No edge, near-plane, or depth clipping in any layout profile and animation/interaction key state.
- Material families, transparency relationships, and emission intent.
- Appearance order, local displacement, and convergence state of per-component, per-layer, or per-region animations.
- Framing direction, scale, and focus parts of the source project's named viewpoints.
- Narrative information such as model introductions, fact fields, stage text, and timelines.
- Environmental structures such as plinths, courtyards, ground, or other structures that carry the main body silhouette.
- SpatialUI information hierarchy, relative orientation, readability, and foreground occlusion relationships.
- Page region completeness, navigation relationships, form states, and HUD.
- Desktop and mobile layout reflow, line wrapping, and operability.

Screenshots cannot prove stereoscopic depth; supplement with multiple viewpoints, bounds, and head-motion parallax.

After completing runtime evidence collection, execute:

```bash
python3 scripts/validate_spatial_fit.py \
  --contract <scratch>/conversion-contract.json \
  --verification-result <scratch>/verification-result.json
```

First re-run `assets/probes/SpatialViewVisibleRegionProbe.kt` on the current APK and current layout,
save the new raw JSON, then write that path into `verification-result.json`. Acceptance files must not
reuse the `measurement_file` from the contract stage.

`validate_spatial_fit.py` only reads, recomputes, and validates probe artifacts; it does not perform measurement.
`clipped=false` is also not a self-proving conclusion. Every state must record the target AABB measured at current
runtime; the validator will check that it is consistent with the frozen fit and lies within the clip box
re-measured in the same run. The default `runtime_bounds_policy=exact` requires the two to be equal.
If the SDK's public bounds API can only give conservative resource bounds that contain the actually visible
geometry, the contract may set `runtime_bounds_policy` to `conservative-contains-expected` and record the reason; in that case
the runtime AABB must contain the source-derived frozen fit, and must itself still not cross the measured clip box.

### 5.1 Final Product Fidelity Scoring

Completed acceptance uses fixed denominators and cannot delete scoring items based on project implementation status:

| Dimension | Weight | Acceptance Target |
|---|---:|---|
| `page_structure` | 15 | Page, region, navigation, and overlay completeness |
| `visual_layout` | 15 | Size, spacing, alignment, hierarchy, and occupied space |
| `ui_content_style` | 10 | Text, icons, images, colors, typography, and component semantics |
| `ui_states_responsive` | 10 | States, breakpoints, adaptivity, and mobile presentation |
| `user_flows_interaction` | 15 | Complete flows, inputs, feedback, and results |
| `scene_structure` | 10 | Entity hierarchy, silhouette, proportions, environment, metric scale, and unclipped AABB |
| `animation_timing` | 10 | Animation order, keyframes, pacing, and state transitions |
| `view_camera` | 5 | Source named viewpoints, framing direction, scale, and focus parts |
| `material_lighting` | 10 | Material families, colors, transparency, lighting, and light-dark hierarchy |

Each dimension is scored on `0..100`, and must be accompanied by same-semantic evidence for source and target and a brief judgment. The goal is
100 for the total score and for every dimension. Any dimension below 100 must be associated with
a capability already approved in `degradation-decision.json`.

Final product scoring evaluates only the currently operable artifact, not the feasibility of the plan, future plans, or the
`rebuild` intent in the mapping report. That a capability has been designed, that the API has been verified, and that the contract
records an implementation path cannot replace actual implementation and interaction evidence.

- When the source product relies on direct manipulation to inspect the subject, while the target has no triggerable
  rotate, pan, or zoom interaction, `user_flows_interaction` is recorded as `0`; buttons, timelines, and page navigation
  cannot substitute for the missing subject inspection flow. Under the fixed weight, this gap directly loses 15 points.
- When the source named viewpoints or observation orbits do not produce corresponding azimuth, pitch, look-at target, and framing scale
  in the target, `view_camera` is recorded as `0`. System camera immutability does not constitute an exemption; scene root inverse
  transform, view root, and fit/framing compensation should be attempted first. Under the fixed weight, this gap directly loses 5 points.
- "Technically rebuildable but currently not done" is an implementation gap; only "native attempt completed and semantics still
  unreachable" can be used to request degradation as a platform limitation.

Implementation gaps are written into `implementation_gaps`, and the final status is `incomplete`. It does not enter
`degradation-decision.json`, and the user cannot turn a missing implementation into a pass by approving degradation.

Degradation pass conditions are satisfied simultaneously:

- Total score at least `70`.
- Each dimension at least `70`.
- Every dimension below 100 is associated with an approved degradation capability.
- There is no unaccepted visible loss of `visual_core` or `interaction_core`.

Execute:

```bash
python3 scripts/score_outcome_fidelity.py \
  --observations <scratch>/outcome-observations.json \
  --decision <scratch>/degradation-decision.json \
  --output <scratch>/outcome-fidelity-report.json
```

Scoring is produced by evidence review; the script is responsible for fixed weights, completeness, lower bounds, and the final determination.
Build success, control presence, model recognizability, or admission score passing cannot replace this scoring. Without a degradation
decision, a score of 70-99 returns `needs_degradation_approval`, and delivery cannot be completed.

## 6. Interaction Acceptance

Execute `verification-plan.json.interactions[]` one by one:

- Establish the precondition state.
- Perform the action.
- Observe the results and logs.
- Record pass, fail, or inability to trigger in the emulator.

Capabilities that the emulator cannot fully prove, such as hand tracking, environment understanding, and real spatial scale,
require re-verification on a real device, and must keep the `implemented_unverified_runtime` designation.

## 7. Performance and Stability

Performance evidence comes from the stage 6 `optimization-report.json`; acceptance only re-checks whether it still holds:

- Stable frame behavior and stutter at the target refresh rate.
- First load, repeated scene entry, and first-frame latency.
- Object pool peaks and resource release.
- Transparent entities, dynamic lights, particle/instance counts, and draw calls.
- PSO warm-up cost when using ShaderGraph.

During acceptance, re-measure the key metrics in the report on the current APK; re-measured values must not be worse than
the reported values beyond the fluctuation range declared in the report, and must still meet the budgets. Performance
conclusions must come from measurement, and must not be inferred from code structure or admission score.

## 8. Completion Status

| Status | Condition |
|---|---|
| `verified` | Static, build, runtime, spatial fit, optimization budgets, visual, and interaction all pass, and final product fidelity is 100 |
| `degraded_approved` | All degradations have evidence and user approval, and the final product meets the degradation lower bounds |
| `incomplete` | A core capability that is implementable but not yet delivered exists |
| `implemented_unverified_runtime` | Code and build pass, but runtime/visual/interaction evidence is incomplete |
| `rejected_at_admission` | Admission failed; no target project was created |
| `failed` | Generated but the build or runtime gate failed |

The final report lists:

- SDK and container.
- Admission score, 100-point goal, gap, and degradation approval status.
- Final product fidelity total score and the nine dimension scores.
- Counts of the five mapping categories.
- Build, runtime, visual, and interaction evidence paths.
- All approximations, deletion items, and remaining risks.
