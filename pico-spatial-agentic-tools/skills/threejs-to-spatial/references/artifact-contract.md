# Migration Artifact Contract

All artifacts are located in:

```text
<output>/.scratch/threejs-to-spatial/
```

Before code generation, the environment, source project, capability, full experience, mapping,
admission, conversion contract, and acceptance plan artifacts must already exist; when below
100 points, a user-approved degradation decision is also required. JSON uses UTF-8, paths are
recorded relative to the source project or target project root, and machine-private prefixes such as
the user home directory are not written.

## 1. environment.json

Producer: environment discovery stage. Consumer: project creation, API evidence gathering, acceptance stage.

```json
{
  "schema_version": 1,
  "pico_cli_version": "0.5.0",
  "sdk_version": "<discovered-stable-version>",
  "sdk_evidence": ["pico-cli project create --help", "local template metadata"],
  "templates": ["planar", "volumetric", "stage"],
  "java": {"version": "21", "home": "..."},
  "android_sdk": {"available": true},
  "emulator": {"available": false, "serial": null}
}
```

Failure behavior: when the SDK version, template, or Java/Android build environment cannot be
confirmed, do not proceed to generation.

## 2. source-project.json

Producer: source project discovery stage. Consumer: capability inventory.

```json
{
  "schema_version": 1,
  "source_root": ".",
  "language": "typescript",
  "three_version": "0.185.1",
  "build_tool": "vite",
  "entrypoints": ["src/main.ts"],
  "source_globs": ["src/**/*.ts"],
  "asset_roots": ["public", "src/assets"],
  "framework": "native-three",
  "dependencies": {"three": "^0.185.1"}
}
```

`language`: `javascript|typescript|mixed`.

`framework` must be `native-three`.

`source_root` is resolved relative to the directory containing `source-project.json`, and an
absolute path may also be used. The capability inventory validation must be able to access that
directory.

## 3. capability-inventory.json

Producer: source inventory stage. Consumer: mapping, admission, and migration contract.

```json
{
  "schema_version": 1,
  "capabilities": [
    {
      "id": "scene.hierarchy",
      "criticality": "visual_core",
      "confidence": "high",
      "asset_paths": [],
      "evidence": [
        {
          "file": "src/main.ts",
          "line": 18,
          "symbol": "scene.add",
          "reason": "the subject model is added to the main scene"
        }
      ],
      "notes": "subject hierarchy"
    }
  ]
}
```

The same `id` may appear only once. `evidence` has at least one item; `line` is a positive integer.

`asset_paths` of `asset.*` capabilities must list relative file paths that already exist in the
input project. `asset_paths` of other capabilities must be empty or omitted. Files exported after
the program runs or newly generated during migration must not enter that list. The validator
confirms that each path actually exists under `source_root`.

## 4. experience-inventory.json

Producer: full web page analysis stage. Consumer: migration contract and acceptance plan.

```json
{
  "schema_version": 1,
  "pages": [
    {
      "id": "main",
      "route": "/",
      "source_files": ["src/App.ts", "src/styles.css"],
      "regions": ["header", "scene", "control-panel"],
      "states": ["default", "loading", "selected"],
      "responsive_modes": ["desktop", "mobile"],
      "visual_baselines": [
        {
          "id": "main-desktop-default",
          "evidence": "reference/main-desktop-default.png",
          "viewport": "desktop",
          "state": "default"
        },
        {
          "id": "main-mobile-selected",
          "evidence": "reference/main-mobile-selected.png",
          "viewport": "mobile",
          "state": "selected"
        },
        {
          "id": "main-desktop-loading",
          "evidence": "reference/main-desktop-loading.png",
          "viewport": "desktop",
          "state": "loading"
        }
      ]
    }
  ],
  "flows": [
    {
      "id": "select-object",
      "page_ids": ["main"],
      "steps": [
        {"id": "tap", "action": "click the subject", "expected": "enter the selected state"}
      ],
      "source_evidence": [
        {"file": "src/App.ts", "line": 42, "reason": "click state transition"}
      ]
    }
  ],
  "inputs": [
    {
      "id": "pointer-select",
      "page_id": "main",
      "source_event": "pointerdown",
      "expected": "select the hit object",
      "source_evidence": [
        {"file": "src/App.ts", "line": 39, "reason": "pointer binding"}
      ]
    }
  ]
}
```

Each page must list all visible regions, user states, responsive modes, and visual baselines. Each
flow must list complete steps; the Three.js canvas counts as only one page region.

## 5. mapping-report.json

Producer: capability mapping stage. Consumer: admission scoring and migration contract.

```json
{
  "schema_version": 1,
  "sdk_version": "<discovered-stable-version>",
  "mappings": [
    {
      "capability_id": "scene.hierarchy",
      "mapping_level": "direct",
      "target_ownership": "kotlin_code",
      "spatial_primitive": ["Entity"],
      "conversion_rule": "create the Entity hierarchy according to the source parent-child relationships",
      "quality_loss": [],
      "validation": ["key node count and parent-child relationships are consistent"],
      "native_attempts": [],
      "degradation_reason": null,
      "version_evidence": [
        {
          "sdk_version": "<discovered-stable-version>",
          "source": "official-doc",
          "symbol": "com.pico.spatial.core.ecs.Entity"
        }
      ]
    }
  ]
}
```

Each inventory id must be mapped exactly once. `drop` and `block` may omit `spatial_primitive` and
`version_evidence`; all other levels must provide them.

`target_ownership` can only be `kotlin_code|source_asset|editor_authored|dropped`.
Retained implementations of `asset.*` use `source_asset`; `material.*` may use `kotlin_code` or
`editor_authored` in the `rebuild|approximate` case; implementations of the remaining capabilities
use `kotlin_code`; `drop|block` use `dropped`. `editor_authored` means that the capability is
reproduced by Spatial Editor and ShaderGraph, and the artifact is the material bundle exported by
the Editor pipeline.

Experience-related `approximate|drop|block` must fill in `native_attempts` and
`degradation_reason`. Each attempt records `approach`, `evidence`, `outcome`, and
`limitation`; `outcome` can only be `api_unavailable`, `semantic_mismatch`,
`runtime_failed`, or `performance_failed`.

## 6. admission-report.json

Producer: `score_admission.py`. Consumer: Skill stage gate.

```json
{
  "schema_version": 1,
  "target_score": 100.0,
  "floor": 70.0,
  "score": 82.5,
  "shortfall": 17.5,
  "status": "needs_degradation_approval",
  "admitted": false,
  "requires_degradation_approval": true,
  "degraded_capabilities": ["effect.particles-cpu"],
  "hard_blockers": [],
  "low_confidence_core": [],
  "weighted_total": 20.0,
  "weighted_retained": 16.5,
  "counts": {
    "direct": 3,
    "rebuild": 2,
    "approximate": 1,
    "drop": 1,
    "block": 0
  }
}
```

`status` can only be:

- `full`: 100 points, may proceed to contract freeze.
- `needs_degradation_approval`: 70-99 points, must stop and request user approval.
- `degraded_approved`: the user has approved all gaps, may continue.
- `rejected`: below 70, any blocker exists, or a core capability is low-confidence.

When `admitted=false`, creating the target project is not allowed. 70 points is not a success criterion.

## 7. degradation-decision.json

Producer: the migration Agent after explicit user confirmation. Consumer: admission and final artifact fidelity scorer.

```json
{
  "schema_version": 1,
  "status": "approved",
  "approved_capabilities": ["effect.particles-cpu"],
  "approval_evidence": "the user confirmed acceptance of the reduction in particle count and blending effects"
}
```

`approved_capabilities` must exactly match `degraded_capabilities` in the admission report.
The Agent must not generate approval on its own.

## 8. conversion-contract.json

Producer: migration planning stage. Consumer: code generation and acceptance.

The AABB and scale values in the following example only demonstrate the field relationships and are
not default dimensions. Every migration must replace them with measured values from the current
source scene and target container.

### 8.1 Measurement Artifacts

The source scene and target visible region must first be generated as independent JSON files by the
runtime probes in `assets/probes/`. The common fields are as follows:

```json
{
  "schema_version": 1,
  "measurement_kind": "target-visible-region",
  "producer": {
    "id": "spatialview-visible-region-probe",
    "version": 1
  },
  "captured_at_utc": "2026-09-30T00:00:00Z",
  "context": {
    "coordinate_from": "view-local-px",
    "coordinate_to": "spatial-view-local-meters",
    "profile_id": "main-default",
    "sdk_version": "6.1.9",
    "view_size_px": [800, 800, 800]
  },
  "context_fingerprint": "fnv1a32:5f7fbac0",
  "raw_box": {
    "space": "spatial-view-local-px",
    "min": [0, 0, 0],
    "max": [800, 800, 800],
    "size": [800, 800, 800]
  },
  "raw_corners": [
    [0, 0, 0], [0, 0, 800], [0, 800, 0], [0, 800, 800],
    [800, 0, 0], [800, 0, 800], [800, 800, 0], [800, 800, 800]
  ],
  "converted_corners_m": [
    [-0.4, 0.4, 0.4], [-0.4, 0.4, -0.4],
    [-0.4, -0.4, 0.4], [-0.4, -0.4, -0.4],
    [0.4, 0.4, 0.4], [0.4, 0.4, -0.4],
    [0.4, -0.4, 0.4], [0.4, -0.4, -0.4]
  ],
  "aabb_m": {
    "min": [-0.4, -0.4, -0.4],
    "max": [0.4, 0.4, 0.4],
    "size": [0.8, 0.8, 0.8]
  }
}
```

The source probe uses `measurement_kind=source-scene-aabb`,
`producer.id=three-runtime-aabb-probe`,
`raw_box.space=three-world-source-units`, and `aabb_source`. The target probe uses the fields in
the example above. `context_fingerprint` is generated by the probe, and the validator recomputes it.

```json
{
  "schema_version": 1,
  "source_project": ".",
  "output_project": "../sample-spatial",
  "sdk_version": "<discovered-stable-version>",
  "target_mode": "new-project",
  "container": "stage",
  "package_name": "com.example.samplespatial",
  "app_name": "SampleSpatial",
  "capability_dispositions": [
    {
      "capability_id": "scene.hierarchy",
      "mapping_level": "direct",
      "ownership": "kotlin_code",
      "implementation": ["scene/SceneFactory.kt"],
      "visible_loss": [],
      "acceptance": ["key Entity hierarchy is consistent"]
    },
    {
      "capability_id": "asset.gltf-glb",
      "mapping_level": "direct",
      "ownership": "source_asset",
      "implementation": ["resources/SourceAssetLoader.kt"],
      "visible_loss": [],
      "acceptance": ["source model loads successfully"]
    },
    {
      "capability_id": "material.shader",
      "mapping_level": "rebuild",
      "ownership": "editor_authored",
      "implementation": ["resources/HeroMaterialLoader.kt"],
      "visible_loss": [],
      "acceptance": ["Fresnel outline matches the source shader in comparison"]
    }
  ],
  "scene": {
    "root_id": "migrated-scene-root",
    "units_to_meters": 1.0,
    "unit_evidence": ["source runtime measurement and source semantics"],
    "forward_conversion": "source -Z to Spatial -Z",
    "axis_mapping": ["+x", "+y", "+z"],
    "spatial_fit": {
      "source_bounds": [
        {
          "state_id": "fully-assembled",
          "aabb_source": {
            "min": [-1.0, -1.0, -1.0],
            "max": [1.0, 1.0, 1.0],
            "size": [2.0, 2.0, 2.0]
          },
          "measurement_file": "measurements/source-fully-assembled.json",
          "evidence": ["measurements/source-fully-assembled.json"]
        }
      ],
      "profiles": [
        {
          "id": "main-default",
          "visible_region": {
            "measurement_method": "runtime-clipping-box",
            "aabb_m": {
              "min": [-0.4, -0.4, -0.4],
              "max": [0.4, 0.4, 0.4],
              "size": [0.8, 0.8, 0.8]
            },
            "measurement_file": "measurements/contract-main-default.json",
            "evidence": ["measurements/contract-main-default.json"]
          },
          "usable_region": {
            "aabb_m": {
              "min": [-0.36, -0.36, -0.36],
              "max": [0.36, 0.36, 0.36],
              "size": [0.72, 0.72, 0.72]
            },
            "rationale": "reserve edge safety margins after the full UI layout is determined"
          },
          "fit": {
            "reference_state_id": "fully-assembled",
            "uniform_scale": 0.36,
            "translation_m": [0.0, 0.0, 0.0],
            "runtime_bounds_policy": "exact",
            "state_aabbs_m": [
              {
                "state_id": "fully-assembled",
                "aabb_m": {
                  "min": [-0.36, -0.36, -0.36],
                  "max": [0.36, 0.36, 0.36],
                  "size": [0.72, 0.72, 0.72]
                }
              }
            ],
            "rationale": "apply a uniform contain fit of the source AABB to the usable region"
          }
        }
      ]
    },
    "entities": []
  },
  "assets": [
    {
      "id": "source-robot",
      "source_capability": "asset.gltf-glb",
      "source_path": "public/models/robot.glb",
      "provenance": "source_existing",
      "output_path": "app/src/main/assets/models/robot.glb",
      "conversion": null
    },
    {
      "id": "hero-shader-material",
      "source_capability": "material.shader",
      "source_path": "authoring/hero-shader.graph.json",
      "provenance": "editor_authored",
      "shader_stage": "surface",
      "output_path": "app/src/main/assets/materials/hero.material.bundle",
      "conversion": "ShaderGraph reproduces the Fresnel outline of the source GLSL; runtime screenshots are compared to confirm semantic equivalence"
    }
  ],
  "systems": [],
  "interactions": [],
  "spatial_ui": [],
  "web_experience": {
    "pages": [
      {
        "source_page_id": "main",
        "composable": "ui/MainPage.kt",
        "mapped_regions": ["header", "scene", "control-panel"],
        "mapped_states": ["default", "loading", "selected"],
        "responsive_modes": ["desktop", "mobile"],
        "visual_targets": [
          "main-desktop-default",
          "main-mobile-selected",
          "main-desktop-loading"
        ],
        "acceptance": ["all page regions are visible on the target"]
      }
    ],
    "flows": [
      {
        "source_flow_id": "select-object",
        "implementation": ["interaction/SelectionController.kt"],
        "covered_steps": ["tap"],
        "acceptance": ["entering the selected state after clicking"]
      }
    ],
    "inputs": [
      {
        "source_input_id": "pointer-select",
        "implementation": ["interaction/SelectionGesture.kt"],
        "acceptance": ["spatial click hits the subject"]
      }
    ]
  },
  "cleanup": [],
  "approximations": [],
  "dropped": []
}
```

Constraints:

- `target_mode` is fixed to `new-project`.
- `container` can only be `planar|volumetric|stage`.
- `units_to_meters` represents the physical metric meaning of the source unit, and `unit_evidence`
  must be provided; it is not a visual scale value filled in to fit the window.
- `axis_mapping` records the source axis mapping in target X/Y/Z order; each source axis must be
  used exactly once.
- `spatial_fit.source_bounds` must cover the complete assembled state, as well as all animations,
  interactions, and viewpoint states that change the spatial extent; each `measurement_file` points
  to the raw output of `three-runtime-aabb-probe`.
- Each `spatial_fit.profiles[]` corresponds to one actual container and page layout.
  `visible_region` must come from the runtime clipping-box measurement of the target 3D spatial
  region in the final UI; the `measurement_file` of the current SpatialView-hosted region points to
  the raw output of `spatialview-visible-region-probe`. The outer window dimensions cannot be used
  as a substitute, and data from another project or layout cannot be reused.
- `measurement_file` relative paths are based on the contract file that contains them. Probe
  artifacts must retain the producer, time, context fingerprint, raw box, and 8 corners;
  `aabb_source` or `aabb_m` must be recomputable from these corners. An `evidence` string cannot
  substitute for the probe artifact.
- `usable_region` is carved out from `visible_region` after the full UI region is determined, and
  states the rationale for reserving space for UI, interaction, and edge clipping.
- `fit.uniform_scale` is the dimensionless uniform scale after metric conversion:
  `min(usable_axis_size / (source_axis_size * units_to_meters))`. The target is forbidden from
  squeezing into the window using non-uniform scaling.
- `fit.state_aabbs_m` must be computed according to `axis_mapping`, `units_to_meters`,
  `uniform_scale`, and `translation_m`, and must cover all source states. The reference state must
  lie within `usable_region`, and all states must lie within `visible_region`.
- `fit.runtime_bounds_policy` may be omitted and defaults to `exact`, requiring the target runtime
  AABB to equal `state_aabbs_m`. Only when the target SDK's public bounds API returns a conservative
  resource bound that contains the actual visible geometry may `conservative-contains-expected` be
  used; in that case `runtime_bounds_rationale` must be provided, the target runtime AABB must
  contain the corresponding `state_aabbs_m`, and it must itself still lie entirely within the
  `visible_region` measured in the same run.
- Each inventory id must appear exactly once in `capability_dispositions`.
- The `mapping_level` of a disposition must be consistent with the mapping report.
- The `ownership` of a disposition must be consistent with the `target_ownership` of the mapping
  report.
- `approximate` must provide `visible_loss` and `acceptance`.
- `drop` must provide `visible_loss`.
- `direct|rebuild|approximate` must provide a non-empty `implementation`.
- `implementation` records only Kotlin files, and paths must end with `.kt`.
- `assets[]` accepts only source files already registered in the corresponding
  `asset.*.asset_paths`, or `editor_authored` material bundles associated with an inventoried
  `material.*` capability.
- `assets[].provenance` can only be `source_existing|format_conversion|editor_authored`.
- `format_conversion` must record a non-empty `conversion`; it only converts the format of existing
  files.
- For `editor_authored`, `source_path` records the path of the graph source file, `shader_stage` can
  only be `surface|vertex`, and `conversion` records the reproduction and evaluation method; its
  `source_capability` must be `material.*`.
- Each `editor_authored` material capability must correspond to at least one `editor_authored`
  asset.
- Procedural geometry, animation, effects, or procedural textures must not generate model, image,
  animation assets, or Editor bundles.
- `web_experience` must cover, item by item, the pages, regions, states, responsive modes, visual
  baselines, flow steps, and inputs of the experience inventory.
- Must not contain WebView or a retained Three.js runtime dependency.

## 9. verification-plan.json

Producer: migration planning stage. Consumer: runtime acceptance.

```json
{
  "schema_version": 1,
  "pages": ["main"],
  "flows": ["select-object"],
  "inputs": ["pointer-select"],
  "views": [
    {
      "baseline_id": "main-desktop-default",
      "source_evidence": "source-primary.png",
      "target_capture": "target-primary.png",
      "critical_features": ["subject proportions", "material family", "spatial scale"]
    },
    {
      "baseline_id": "main-mobile-selected",
      "source_evidence": "source-mobile-selected.png",
      "target_capture": "target-mobile-selected.png",
      "critical_features": ["mobile layout", "selected state", "control region"]
    },
    {
      "baseline_id": "main-desktop-loading",
      "source_evidence": "source-desktop-loading.png",
      "target_capture": "target-desktop-loading.png",
      "critical_features": ["loading state", "page skeleton", "state feedback"]
    }
  ],
  "interactions": [
    {
      "source_flow_id": "select-object",
      "source_input_ids": ["pointer-select"],
      "precondition": "the subject is visible",
      "action": "spatial click on the subject",
      "expected": "the subject enters the selected state"
    }
  ],
  "runtime_checks": ["install", "launch", "watch-crash"],
  "performance_checks": []
}
```

Each page state and responsive mode must have view evidence; each flow and input must have an
acceptance item.

## 10. outcome-observations.json

Producer: source/target comparison acceptance. Consumer: `score_outcome_fidelity.py`.

```json
{
  "schema_version": 1,
  "dimensions": [
    {
      "id": "page_structure",
      "score": 82,
      "evidence": [
        {
          "source": "reference/main-desktop.png",
          "target": "verification/main-desktop.png",
          "judgement": "page regions are complete; an approved deviation exists in the control region position"
        }
      ],
      "unverified_core_losses": [],
      "degradation_capabilities": ["effect.particles-cpu"],
      "implementation_gaps": []
    }
  ]
}
```

Must contain exactly the following nine dimensions:

- `page_structure`
- `visual_layout`
- `ui_content_style`
- `ui_states_responsive`
- `user_flows_interaction`
- `scene_structure`
- `animation_timing`
- `view_camera`
- `material_lighting`

Each `score` is `0..100`, `evidence` has at least one item, and each item must give source evidence,
target evidence, and a judgement at the same time. Core visible losses not yet accepted go into
`unverified_core_losses`. Declaring `rebuild` in `mapping-report.json` or
`conversion-contract.json` only indicates that the approach and target exist; it does not prove
that the current artifact has implemented it. Scoring must read target runtime evidence; when core
interaction or viewpoint results are missing, the corresponding dimension is scored according to
the actual deficiency.

Dimensions below 100 points must be classified:

- `implementation_gaps`: the target capability can be rebuilt, but the current artifact has not
  implemented or wired it up yet; the resulting status is `incomplete`, and it cannot be turned into
  complete via degradation approval.
- `degradation_capabilities`: only after native attempts have been completed and a semantic or
  quality loss has been proven may the user be asked to approve degradation.

## 11. outcome-fidelity-report.json

Producer: `score_outcome_fidelity.py`. Consumer: completion gate.

```json
{
  "schema_version": 1,
  "target_score": 100.0,
  "floor": 70.0,
  "dimension_floor": 70.0,
  "score": 78.4,
  "shortfall": 21.6,
  "status": "degraded_approved",
  "passed": true,
  "requires_degradation_approval": false,
  "observed_degradations": ["effect.particles-cpu"],
  "implementation_gaps": [],
  "dimensions": [],
  "failed_dimensions": [],
  "unverified_core_losses": []
}
```

100 points passes directly. 70-99 points can pass as `degraded_approved` only when every dimension
below 100 is associated with an approved capability, all nine dimensions are at least 70, the total
score is at least 70, and no unverified core losses exist.

When any `implementation_gaps` exist, the report status is fixed to `incomplete`; user approval of
degradation cannot convert an unimplemented capability into a delivered capability.

## 12. optimization-report.json

Producer: lossless optimization evaluation stage. Consumer: acceptance stage and final delivery.

```json
{
  "schema_version": 1,
  "target": {
    "device": "PICO 4 Ultra",
    "rom": "PICO OS 6.1",
    "sdk_version": "6.1.9",
    "container": "stage",
    "build_sha256": "<apk-sha256>"
  },
  "budget": {
    "frame_time_ms_p95": 16.7,
    "stutter_frame_ratio": 0.02,
    "draw_calls_max": 120,
    "texture_mesh_memory_mb": 512,
    "startup_ms": 2500,
    "shadergraph_warmup_ms": 1000
  },
  "measurements": [
    {
      "id": "scene-frame-time",
      "metric": "frame_time_ms_p95",
      "budget": 16.7,
      "value": 13.2,
      "unit": "ms",
      "method": "pico-cli perf",
      "evidence": "measurements/perf-scene-frame-time.json",
      "passed": true
    }
  ],
  "optimizations": [
    {
      "id": "instanced-particles",
      "capabilities": ["effect.particles-cpu"],
      "action": "MeshInstancesResource and a bounded instance pool replace per-entity particles",
      "behavior_preserved": true,
      "before_evidence": "measurements/particles-before.json",
      "after_evidence": "measurements/particles-after.json",
      "visual_parity": "verification/particles-parity.json",
      "measured_gain": "draw calls 420 -> 12"
    }
  ],
  "residual_risks": ["values are single-session measurements; re-measurement is required after a ROM upgrade"],
  "status": "passed"
}
```

Constraints:

- The four `target` items (device, ROM, SDK version, container) together with `build_sha256` must all
  be present; the same report must not mix measurements from different devices or containers.
- `budget` must include at least `frame_time_ms_p95`, `draw_calls_max`, `texture_mesh_memory_mb`,
  and `startup_ms`; when ShaderGraph is used, add `shadergraph_warmup_ms`.
- Every contract page and primary state must appear in the reachability description or evidence of
  `measurements[]`; measuring only the default idle frame does not count as coverage.
- The `passed` of `measurements[]` must be consistent with `value <= budget`, and `evidence` points
  to a raw artifact that actually exists.
- The `behavior_preserved` of `optimizations[]` must be `true`; `before_evidence`,
  `after_evidence`, `visual_parity`, and a non-empty `measured_gain` must all be provided.
- `capabilities` must reference capabilities that already exist in the inventory.
- Any change that alters visible results or interaction semantics does not go into
  `optimizations[]`; instead it goes through the approval process of `degradation-decision.json`.
- `status` can only be `passed`, `needs_degradation_approval`, or `incomplete`.
  `passed` requires that all measurements meet the budget and that no unexplained gaps exist.

## 13. verification-result.json

Producer: acceptance stage. Consumer: final delivery.

```json
{
  "schema_version": 1,
  "contract_valid": true,
  "build": {"passed": true, "command": "./gradlew :app:assembleDebug"},
  "tests": {"passed": true, "count": 4},
  "runtime": {
    "passed": true,
    "device": "emulator",
    "installed": true,
    "launched": true,
    "crash_free": true
  },
  "spatial_fit": {
    "profiles": [
      {
        "id": "main-default",
        "visible_region": {
          "measurement_method": "runtime-clipping-box",
          "aabb_m": {
            "min": [-0.4, -0.4, -0.4],
            "max": [0.4, 0.4, 0.4],
            "size": [0.8, 0.8, 0.8]
          },
          "measurement_file": "measurements/runtime-main-default.json",
          "evidence": ["measurements/runtime-main-default.json"]
        },
        "states": [
          {
            "state_id": "fully-assembled",
            "measured_aabb_m": {
              "min": [-0.36, -0.36, -0.36],
              "max": [0.36, 0.36, 0.36],
              "size": [0.72, 0.72, 0.72]
            },
            "clipped": false,
            "evidence": ["verification/fully-assembled-bounds.json"]
          }
        ]
      }
    ]
  },
  "visual": {"passed": true, "evidence": ["target-primary.png"]},
  "interactions": {"passed": true, "results": []},
  "optimization": {
    "passed": true,
    "report": "optimization-report.json",
    "remeasured": [
      {
        "metric": "frame_time_ms_p95",
        "value": 13.6,
        "budget": 16.7,
        "evidence": "measurements/verify-frame-time.json"
      }
    ]
  },
  "outcome_fidelity": {
    "passed": true,
    "score": 78.4,
    "status": "degraded_approved",
    "report": "outcome-fidelity-report.json"
  },
  "losses": [],
  "completion": "degraded_approved"
}
```

`completion` can only be:

- `verified`
- `degraded_approved`
- `incomplete`
- `implemented_unverified_runtime`
- `rejected_at_admission`
- `failed`

`verified` can be used only when all acceptance layers, optimization budgets, and final artifact
fidelity gates pass. The admission score is not completion evidence.

`optimization.passed` can only come from a report that has passed `validate_optimization.py`, and
`remeasured[]` must be re-measured values on the current APK. When the report is missing, the budget
is not met, or a re-measured value degrades beyond the fluctuation range declared in the report,
`verified` does not hold.

`interactions.passed` must come from the results of executing `verification-plan.interactions[]` one
by one. The presence of buttons, gesture API names, or planned Kotlin files in the target code
cannot substitute for actual hit, state update, and scene change evidence.

`spatial_fit.profiles` must be consistent with the profile set in the contract, and the target probe
must be re-run to measure the current container's visible AABB. Acceptance uses a new
`measurement_file` and must not reuse the contract-stage file. Each state records the target
runtime AABB, `clipped=false`, and evidence; if any of the planned value, runtime value, or current
clipping box is inconsistent, spatial fit cannot pass.
