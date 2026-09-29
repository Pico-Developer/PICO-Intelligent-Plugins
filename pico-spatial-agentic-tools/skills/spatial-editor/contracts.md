# Spatial Editor Workflow Handoff Contracts

Read this module for the exact interaction contract between the Agent and the public
Spatial Editor Workflow Service.

- Read `SKILL.md` for workflow selection, task decomposition, visual planning, and
  handoff.
- Read this file before submitting any public Editor Handoff through
  `resume_editor_workflow`.
- Read `recovery.md` when a submission is rejected or the public Run returns an
  error, blocked state, or user-decision Handoff.

This file is the sole source of truth for Agent-authored forms. `SKILL.md` must not
redefine these fields, and `recovery.md` may refer to them but must not fork them. If
the live MCP input schema differs from this document, obey the live schema and report
the version mismatch.

## Interaction Rules

1. Use the public Workflow facade for module execution. For live read-only
   observations, call the reflected Editor MCP `get_scene_info` and
   `get_entity_info` tools directly; do not route them through a Workflow Handoff.
2. Treat `runId`, `current`, `next`, `result`, `error`, `artifacts`, and `evidence`
   as authoritative. The MCP returns the compact
   `spatialcraft.editor-workflow-response/v1` projection; internal composition,
   snapshot, empty fields, and submission echoes are intentionally not exposed.
3. Follow the current public state:
   - `next.action` beginning with `submit_`: use `next.submission.kind`, then call
     `next.tool` with `next.arguments` plus one `input` matching its Schema.
   - `next.action="wait"`: call `next.tool` with the returned bounded arguments.
   - no `next`: inspect terminal `result`, `error`, `artifacts`, and `evidence`.
4. Never reconstruct fixed Workflow arguments. Use the returned `run_id`, `task_id`,
   `expected_revision`, and `max_wait_ms` from `next.arguments`.
5. Consume each public Run observation once. After every tool call, replace all
   cached `current`, `next`, IDs, allowed actions, and evidence with the newly
   returned values before selecting another operation.
6. Never use `advance_editor_workflow` for normal execution. It is a deprecated
   observation-only compatibility entry, not a state transition.
7. Omit optional fields without a task-derived value. Never submit placeholders,
   comments, JSONC trailing commas, or both sides of a mutually exclusive choice.
8. Stable IDs and Editor names must match `^[A-Za-z_][A-Za-z0-9_]*$`.
9. Vector objects always contain finite numeric `x`, `y`, and `z`. Positive vectors
   require every component to be greater than zero.
10. A schema or semantic form rejection preserves the same Run and current Handoff.
    Read `EDITOR_HANDOFF_INPUT_INVALID` details or the Handoff's previous-input
    message, correct only the named paths, and resubmit with the latest revision.

## Start Form

Start through `start_editor_workflow`. Its returned `runId` is the only Editor
control identity. Do not invoke a direct Editor readiness command or launch a
standalone bootstrap session for the target project first; the managed Workflow
Session owns Editor startup. A read-only status check is allowed.

```jsonc
{
  "workflow_kind": "production",
  "workspace_root": "<absolute workspace root>",
  "goal": "<current user goal>",
  "project_path": "<optional absolute project override>",
  "target_scene_path": "<optional Sources/Scenes/*.usd[a|c] entry>",
  "project_name": "<optional stable project name>",
  "preferred_mode": "headless",
  "gui_reason": "<required only with gui>",
}
```

| Field               | Requirement                                                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `workflow_kind`     | Use `production` for new or existing content. `revision` is optional legacy inheritance.                                                     |
| `workspace_root`    | Required for production and must be absolute. Revision inherits it.                                                                          |
| `base_run_id`       | Required only for revision; use the completed parent run ID.                                                                                 |
| `goal`              | Required current user goal.                                                                                                                  |
| `project_path`      | Optional absolute override. Omit unless explicitly needed.                                                                                   |
| `target_scene_path` | Optional canonical project-relative scene entry under `Sources/Scenes`; it remains authoritative even when the target is an empty `Hi.usda`. |
| `project_name`      | Optional stable name. It must match an existing project selected by `project_path`.                                                          |
| `preferred_mode`    | Omit or use `headless`. Use `gui` only when visible Editor interaction is required.                                                          |
| `gui_reason`        | Required only with `gui`: `user_requested`, `authentication`, `capture_fallback`, or `tool_requires_gui`.                                    |

## Scene Specification Form

The first Handoff of every production or revision Run is `author-scene-spec`.
Translate the user goal into a backend-neutral Scene Spec. `subjects` must contain
every requested semantic object or environment that the later model and scene plans
need to account for; do not submit an empty placeholder array.

```jsonc
{
  "run_id": "<current public run id>",
  "task_id": "author-scene-spec",
  "expected_revision": "<next.arguments.expected_revision>",
  "input": {
    "schemaVersion": "spatialcraft.scene-generation-spec/v1",
    "sceneId": "<stable scene id>",
    "name": "<display scene name>",
    "objective": "<current user goal>",
    "coordinateSystem": {
      "handedness": "right",
      "upAxis": "Y",
      "unitsPerMeter": 1,
    },
    "subjects": [
      {
        "id": "<stable subject id>",
        "kind": "prop",
        "description": "<required semantic object>",
        "count": 1,
      },
    ],
  },
}
```

Use a separate subject for each distinct requested model archetype. Describe
ground, room, or other non-model geometry as `environment`, `structure`, or
`decoration`; `plan-scene` later decides whether it becomes a primitive.

## Model Production Plan Form

`spatial-editor-workflow@5` establishes the Editor Session first, then
`produce-models` requests `editor-model-plan`. Submit only distinct model asset
archetypes that must be generated or explicitly reused. Final transforms and all
scene-owned work belong to the later Scene Plan.

For an existing scene, include `"scene": {"mode": "modify", "expectedPath": "<live scene path>"}`.
After the session is established, obtain the active path directly from
`get_scene_info` using `detail="tree"`, `max_depth=-1`,
`include_transforms=true`, `include_bounds=true`, and `limit=0`. Omission preserves
create-mode behavior. Layout-only work uses `models: []`. Old Run status never
selects or authorizes the target.
An empty default `Hi.usda` is a new-project placeholder unless the start request
declared it as `target_scene_path`. Without an explicit target, submit
`scene.mode="create"` so the workflow creates a task-named USDA. With an explicit
target, the runtime forces `modify` and preserves that exact entry even when it is empty.

```jsonc
{
  "run_id": "<current public run id>",
  "task_id": "editor-model-plan",
  "expected_revision": "<next.arguments.expected_revision>",
  "input": {
    "schemaVersion": "spatialcraft.editor-model-production-plan/v1",
    "models": [
      {
        "id": "<stable model id>",
        "prompt": "<complete provider-facing asset intent>",
        "name": "<stable Editor entity name>",
        "required": true,
        "source": {
          "strategy": "generate_fresh",
        },
        "provider": {
          "engine": "<explicit override>",
          "faceCount": "<positive integer>",
          "pbr": true,
          "modelVersion": "<explicit override>",
        },
        "targetHeightMeters": "<positive exact requested height>",
        "expectedBoundsMeters": {
          "minExtent": { "x": "<positive>", "y": "<positive>", "z": "<positive>" },
          "maxExtent": { "x": "<positive>", "y": "<positive>", "z": "<positive>" },
          "toleranceMeters": "<non-negative number>",
        },
        "captureViewSet": "six_axis",
        "frontRequirement": "assess",
        "orientationRequirement": "assess",
        "acceptance": ["<observable model criterion>"],
      },
    ],
  },
}
```

- `models` is the complete generated or explicitly reused asset-archetype worklist.
  Use `[]` for primitive-only scenes.
- Use one item per distinct asset. Additional occurrences reuse that accepted asset
  through `instances` in the Scene Plan.
- Every model requires an explicit `source.strategy` and a detailed standalone
  prompt of at least 20 characters. Cover the requested identity, silhouette and
  geometry, visible parts, appearance/material cues, and generation constraints;
  a category label alone is not a valid prompt.
- Use `source.strategy="generate_fresh"` for explicitly requested new models. It must
  not include `source.assetPath`.
- `reuse_required` never generates a replacement. Select either a prior accepted
  asset, an absolute `source.assetPath`, or a `source.query` that can resolve one;
  use `reuse_or_generate` only when either outcome satisfies the accepted contract.
- Set `models[].targetHeightMeters` only when the user prompt or accepted upstream
  contract provides that exact metric height. The Controller applies and verifies
  it after import. Omit it when unspecified; never infer a category default from
  words such as lamp, mailbox, vehicle, furniture, or person.
- Omit `position`, `rotationEuler`, and `scale`, even if a legacy model schema
  exposes them. `plan-scene` owns every final transform.
- Do not include primitives, groups, materials, runtime nodes, enhancements,
  delivery settings, or scene acceptance in this form.

## Legacy Production Manifest Form

The following `editor-manifest` form is retained only for resumable
`spatial-editor-workflow@2` Runs. A v5 Run never requests it directly; do not submit
it when the current Handoff is `editor-model-plan`.

Submit only when the current public Handoff requests `editor-manifest`. Use the exact
task ID returned by the Run even though the stable v1 task ID is shown below.

```jsonc
{
  "run_id": "<current public run id>",
  "task_id": "editor-manifest",
  "expected_revision": "<next.arguments.expected_revision>",
  "input": {
    "schemaVersion": "2.0",
    "models": [
      {
        "id": "<stable model id>",
        "prompt": "<provider-facing asset intent>",
        "name": "<stable Editor entity name>",
        "required": true,
        "source": {
          "strategy": "reuse_or_generate",
          "query": "<optional reuse query>",
          "assetPath": "<optional absolute local asset path>",
        },
        "provider": {
          "engine": "<explicit override>",
          "faceCount": "<positive integer>",
          "pbr": true,
          "modelVersion": "<explicit override>",
        },
        "position": { "x": 0, "y": 0, "z": 0 },
        "rotationEuler": { "x": 0, "y": 0, "z": 0 },
        "scale": { "x": 1, "y": 1, "z": 1 },
        "targetHeightMeters": "<positive number>",
        "expectedBoundsMeters": {
          "minExtent": { "x": "<positive>", "y": "<positive>", "z": "<positive>" },
          "maxExtent": { "x": "<positive>", "y": "<positive>", "z": "<positive>" },
          "toleranceMeters": "<non-negative number>",
        },
        "captureViewSet": "six_axis",
        "frontRequirement": "assess",
        "orientationRequirement": "assess",
        "acceptance": ["<observable model criterion>"],
      },
    ],
    "materials": [
      {
        "id": "<stable material id>",
        "targetModelId": "<model id>",
        "prompt": "<material intent>",
        "properties": {
          "preset": "<optional explicit preset>",
          "color": { "r": "<0..1>", "g": "<0..1>", "b": "<0..1>" },
          "opacity": "<0..1>",
          "roughness": "<0..1>",
          "metallic": "<0..1>",
          "emissiveStrength": "<non-negative number>",
          "transparent": "<boolean>",
          "blendingMode": "<documented enum>",
          "faceCulling": "<documented enum>",
          "depthWrite": "<boolean>",
          "depthTest": "<boolean>",
          "opacityThreshold": "<0..1>",
        },
        "outputPath": "<absolute USDA output path>",
        "required": true,
        "acceptance": ["<observable material criterion>"],
      },
    ],
    "scene": {
      "mode": "create",
      "name": "<stable scene name>",
      "prompt": "<whole-scene composition intent>",
      "runtimeNodes": [
        {
          "name": "<stable runtime node name>",
          "path": "./<path relative to the managed scene root>",
          "purpose": "<downstream runtime purpose>",
          "parentPath": ".",
          "transformOwner": "runtime",
        },
      ],
      "acceptance": ["<observable full-scene criterion>"],
    },
    "enhancements": [
      {
        "id": "<stable enhancement id>",
        "type": "lighting",
        "intent": "<requested enhancement intent>",
        "required": false,
        "targetPath": "<optional existing absolute path>",
        "requiredCapabilities": ["<known capability>"],
        "acceptance": ["<observable enhancement criterion>"],
      },
    ],
    "delivery": {
      "targetAppRoot": "<explicit app root>",
      "bundleName": "<stable bundle name>",
    },
  },
}
```

The form exposes all fields but is not a payload to copy. Remove optional fields,
placeholder values, initial transforms without evidence, and provider overrides not
requested by the task.

### Manifest Field Rules

| Field                                | Required    | Rule                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------ | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schemaVersion`                      | Yes         | Exactly `"2.0"`.                                                                                                                                                                                                                                                                                                            |
| `models`                             | Yes         | Distinct generated/imported archetypes. Use `[]` for primitive-only work.                                                                                                                                                                                                                                                   |
| `models[].id`, `name`                | Yes         | Stable ASCII identifiers.                                                                                                                                                                                                                                                                                                   |
| `models[].prompt`                    | Yes         | One asset's positive generation intent; hard maximum 800 characters, operating target at most 700.                                                                                                                                                                                                                          |
| `models[].required`                  | No          | Defaults to required; use `false` only when omission is allowed.                                                                                                                                                                                                                                                            |
| `source.strategy`                    | No          | `reuse_or_generate`, `generate_fresh`, or `reuse_required`.                                                                                                                                                                                                                                                                 |
| `source.query`                       | No          | Task-derived reusable-asset search query.                                                                                                                                                                                                                                                                                   |
| `source.assetPath`                   | Conditional | Absolute local path for an explicit reusable asset. Never combine with `generate_fresh`; for `reuse_required`, omit it only when a prior accepted asset or `source.query` can resolve the required asset.                                                                                                                   |
| `provider`                           | No          | Explicit overrides only. `faceCount` is a positive integer.                                                                                                                                                                                                                                                                 |
| `position`, `rotationEuler`, `scale` | No          | Initial hints only; final transforms belong to the Scene Plan. Scale components are positive.                                                                                                                                                                                                                               |
| `targetHeightMeters`                 | No          | Positive target height copied from the user prompt or accepted upstream contract. Omit when unspecified; never infer a category default. Do not combine with non-identity `scale`.                                                                                                                                          |
| `expectedBoundsMeters`               | No          | Evidence-backed positive extent limits and non-negative tolerance.                                                                                                                                                                                                                                                          |
| `captureViewSet`                     | No          | Omit or use `six_axis`; no other value is valid.                                                                                                                                                                                                                                                                            |
| `frontRequirement`                   | No          | `required`, `assess`, or `none`.                                                                                                                                                                                                                                                                                            |
| `orientationRequirement`             | No          | `forward_and_up`, `up_axis`, `assess`, or `none`.                                                                                                                                                                                                                                                                           |
| `models[].acceptance`                | Yes         | Non-empty observable model criteria.                                                                                                                                                                                                                                                                                        |
| `primitives`                         | No          | Legacy compatibility only. New workflows define final primitives in the Scene Plan.                                                                                                                                                                                                                                         |
| `materials`                          | Yes         | May be empty.                                                                                                                                                                                                                                                                                                               |
| material target                      | Exactly one | Set `targetModelId` or `targetPrimitiveId`, never both/neither. A primitive target may forward-reference a later Plan primitive.                                                                                                                                                                                            |
| `materials[].properties`             | No          | Explicit Editor authoring values. Provide them whenever exact color, emission, opacity, roughness, metallic value, or render mode is acceptance-critical.                                                                                                                                                                   |
| `properties.color`                   | No          | Normalized RGB object. The Editor Domain maps it to Editor `color: [r,g,b]`.                                                                                                                                                                                                                                                |
| normalized material values           | No          | `opacity`, `roughness`, `metallic`, and `opacityThreshold` are from 0 to 1.                                                                                                                                                                                                                                                 |
| `properties.emissiveStrength`        | No          | Non-negative explicit emission strength. Pair it with `color` when emission color matters.                                                                                                                                                                                                                                  |
| material render switches             | No          | Boolean `transparent`, `depthWrite`, and `depthTest`; documented blend and culling enums only.                                                                                                                                                                                                                              |
| `materials[].outputPath`             | Yes         | Absolute committed USDA path.                                                                                                                                                                                                                                                                                               |
| `materials[].acceptance`             | Yes         | Non-empty observable material criteria.                                                                                                                                                                                                                                                                                     |
| `scene.mode`                         | Yes         | `create` or `modify`. Existing scenes may use modify regardless of previous Run status.                                                                                                                                                                                                                                     |
| `scene.name`                         | Conditional | Required for `create`.                                                                                                                                                                                                                                                                                                      |
| `scene.expectedPath`                 | Conditional | Required for external `modify`; exact active scene path.                                                                                                                                                                                                                                                                    |
| `scene.prompt`, `acceptance`         | Yes         | Composition intent and non-empty whole-scene criteria.                                                                                                                                                                                                                                                                      |
| `scene.runtimeNodes`                 | No          | Declare only nodes required by downstream runtime code. For create-mode managed entities, use `./...` relative to the discovered scene root (`.` means the root); never derive the root from `scene.name`. Use absolute paths only for already-evidenced existing entities. The handoff contains normalized absolute paths. |
| `enhancements`                       | No          | Requested `lighting`, `animation`, or `effect` work only. Acceptance is non-empty.                                                                                                                                                                                                                                          |
| `requiredCapabilities`               | No          | Known hard capability names only; do not guess.                                                                                                                                                                                                                                                                             |
| `delivery`                           | No          | Explicit destination/name overrides; it does not enable packaging.                                                                                                                                                                                                                                                          |

### Concurrent Fresh-Model Production

When a Model Production Plan contains multiple models whose
`source.strategy="generate_fresh"`, `produce-models` uses the persisted `ModelJob`
pipeline:

1. Submit generation prompts concurrently up to the returned generation budget.
2. Poll active provider tasks concurrently without importing.
3. Serialize completed imports and Editor screenshot mutations.
4. Present the first non-empty review queue item immediately; other provider tasks
   continue in the backend.
5. On failed model-quality review, provide `revisionPrompt`. The Controller deletes
   the rejected imported candidate, submits the replacement prompt, and continues
   consuming the remaining review queue.
6. The stage completes only after every required ModelJob reaches `accepted`.

Do not submit model prompts through direct Editor tools, wait for all jobs before
reviewing the first ready item, or create a separate Workflow Run per model.

`blendingMode` is one of `OPAQUE`, `TRANSPARENT`, `MASKED`, `ADD`, or
`FADE`. `faceCulling` is one of `NONE`, `FRONT`, or `BACK`. The Editor Domain maps
camelCase Manifest fields to the Editor's `emissive_strength`, `blending_mode`,
`face_culling`, `depth_write`, `depth_test`, and `opacity_threshold` arguments.

## Revision Plan Form

For optional legacy inheritance, start with `workflow_kind="revision"` and
`base_run_id` of a completed delivery. Normal project edits use production modify.
When the new public Run requests `editor-revision-plan`, submit:
Read the current scene fingerprint, managed targets, and modification status from the
revision planning context embedded in `next.submission.instructions`; these facts are
not part of the public lifecycle or stable Snapshot. Verify current scene/entity
facts through get-info.

```jsonc
{
  "run_id": "<revision public run id>",
  "task_id": "editor-revision-plan",
  "expected_revision": "<next.arguments.expected_revision>",
  "input": {
    "schemaVersion": "1.0",
    "sceneFingerprint": "<exact currentSceneFingerprint from Handoff instructions>",
    "scenePrompt": "<optional revised scene intent>",
    "sceneAcceptance": ["<optional revised scene criterion>"],
    "allowUserModifiedTargets": false,
    "operations": [
      {
        "op": "<one supported operation>",
      },
    ],
  },
}
```

`operations` contains 1-50 entries. Do not target the same item twice.

| Operation          | Required fields                                                    | Rule                                                                                                                                   |
| ------------------ | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `add_model`        | `model`                                                            | Complete new model work item with a new ID.                                                                                            |
| `remove_model`     | `modelId`, `reason`                                                | Removes a managed model requested by the user.                                                                                         |
| `regenerate_model` | `modelId`, `prompt`                                                | Replacement prompt; optional replacement `acceptance`.                                                                                 |
| `set_transform`    | `modelId` and at least one of `position`, `rotationEuler`, `scale` | Modify the inherited model in place.                                                                                                   |
| `add_primitive`    | `primitive`                                                        | Complete primitive: `id`, `type`, `name`, `position`, positive `sizeMeters`, non-empty `acceptance`; optional parent, rotation, color. |
| `remove_primitive` | `primitiveId`, `reason`                                            | Removes one inherited primitive.                                                                                                       |
| `update_primitive` | `primitiveId` and at least one mutable field                       | Mutable fields: position, rotation, positive size, normalized color.                                                                   |
| `remove_entity`    | `entityPath`, `reason`                                             | Exact inherited top-level path from the revision planning context in the Handoff instructions.                                         |
| `recompose`        | none                                                               | Requests a new full Scene Plan without inventing an asset change.                                                                      |

Set `allowUserModifiedTargets=true` only after explicit user approval. After revision
asset work, the final Scene Plan includes every retained, added, or updated primitive;
omit only explicitly removed primitives.

## Review Form

Submit only when the current public Handoff requests `review-editor-output` and its
input schema requests a review. Copy the current gate, evidence, and every required
view.

If a material target is hidden or temporal evidence is insufficient, submit
`semanticVerdict="inconclusive"` with an `evidenceRevision` that changes the camera
direction, camera target, or contextual `visibleEntityPaths`; omit `materialRevision`
and blocking findings. The Controller preserves that revision across the decision
Handoff and offers `recapture_current`, `inspect_in_gui`, and `cancel` without
committing the material or counting a failed material attempt. Follow the returned
decision gate before recapturing. A material revision still requires a failed review
with valid blocking evidence.

```jsonc
{
  "run_id": "<current public run id>",
  "task_id": "review-editor-output",
  "expected_revision": "<next.arguments.expected_revision>",
  "input": {
    "gateId": "<exact current gate id>",
    "evidenceId": "<exact current evidence id>",
    "views": [
      {
        "viewId": "<returned view id>",
        "imageActuallyInspected": true,
        "targetPresent": true,
        "fullyFramed": true,
        "visibleDefects": [],
        "qualityVerdict": "pass",
        "semanticView": "<returned semantic label>",
        "frontVisible": true,
        "notes": "<optional factual observation>",
      },
    ],
    "semanticVerdict": "pass",
    "blockingFindings": [
      {
        "category": "<allowed category>",
        "summary": "<observable consequence>",
        "evidenceViewIds": ["<failed inspected view id>"],
        "violatedRequirement": "<exact criterion when applicable>",
        "affectedEntityPaths": ["<known managed path>"],
      },
    ],
    "revisionPrompt": "<model retry replacement prompt>",
    "materialRevision": {
      "prompt": "<replacement material intent>",
      "properties": {
        "color": { "r": "<0..1>", "g": "<0..1>", "b": "<0..1>" },
        "emissiveStrength": "<non-negative number>",
      },
    },
    "evidenceRevision": {
      "cameraDirection": { "x": -1, "y": 0.5, "z": 1 },
      "cameraTarget": { "x": 0, "y": 0.75, "z": 0 },
      "visibleEntityPaths": ["/Root/ContextEntity"],
    },
    "frontAssessment": {
      "verdict": "verified",
      "viewId": "<passing inspected view>",
      "evidenceViewIds": ["<passing inspected view>"],
      "worldForwardAxis": "+Z",
      "reasonCode": "<allowed reason when applicable>",
      "reason": "<evidence rationale>",
      "confidence": 0.9,
    },
    "orientation": {
      "verdict": "verified",
      "worldForwardAxis": "+Z",
      "evidenceViewIds": ["<passing inspected view>"],
      "reasonCode": "<allowed reason when applicable>",
      "semanticFeatures": ["<observed feature>"],
      "reason": "<evidence rationale>",
      "confidence": 0.9,
    },
    "notes": "<optional overall note>",
  },
}
```

### Review Field Rules

| Field                                                    | Required         | Rule                                                                                                                                                                                                                                            |
| -------------------------------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gateId`, `evidenceId`                                   | Yes              | Exact current values; stale evidence is invalid.                                                                                                                                                                                                |
| `views`                                                  | Yes              | One record for every required evidence view.                                                                                                                                                                                                    |
| `imageActuallyInspected`, `targetPresent`, `fullyFramed` | Yes              | Boolean factual claims for that image.                                                                                                                                                                                                          |
| `visibleDefects`                                         | Yes              | Use `[]` when none. Observations alone do not fail a gate.                                                                                                                                                                                      |
| `qualityVerdict`                                         | Yes              | `pass`, `fail`, `inconclusive`, or `unverified`.                                                                                                                                                                                                |
| `semanticView`                                           | No               | Copy the returned label; do not invent one.                                                                                                                                                                                                     |
| `semanticVerdict`                                        | Yes              | `pass`, `fail`, or `inconclusive`.                                                                                                                                                                                                              |
| `blockingFindings`                                       | Conditional      | Required for `fail`; omit for pass/inconclusive.                                                                                                                                                                                                |
| finding category                                         | Yes when failing | `explicit_requirement_violation`, `broken_geometry`, `intersection`, `instability`, `floating`, `occlusion`, `scale_mismatch`, or `functional_obstruction`.                                                                                     |
| finding evidence                                         | Yes when failing | Cite inspected, present, framed `fail` views. Intersection, instability, floating, and scale mismatch require two distinct views.                                                                                                               |
| `violatedRequirement`                                    | Conditional      | Exact active acceptance criterion for `explicit_requirement_violation`.                                                                                                                                                                         |
| `revisionPrompt`                                         | Conditional      | Failed model-quality retry only; complete replacement prompt, hard max 800 and target max 700 characters.                                                                                                                                       |
| `materialRevision`                                       | Conditional      | Required for a failed material review while another preview attempt remains. Change `prompt`, structured `properties`, or both; invalid for passing/non-material reviews.                                                                       |
| `evidenceRevision`                                       | Conditional      | Required for material `inconclusive` recapture. Change at least one of `cameraDirection`, `cameraTarget`, or `visibleEntityPaths`; identical effective revisions are rejected without consuming capture budget.                                 |
| unchanged material revision                              | Invalid          | The effective prompt or properties must change. The Editor Domain rejects an identical retry instead of consuming another attempt.                                                                                                              |
| `frontAssessment`                                        | Conditional      | Required by active front policy. Verdict: `verified`, `not_applicable`, or `inconclusive`.                                                                                                                                                      |
| front evidence                                           | Conditional      | Verified requires passing `viewId` or `evidenceViewIds`.                                                                                                                                                                                        |
| front reason                                             | Conditional      | Not applicable uses `rotational_symmetry` or `no_intrinsic_front` and confidence of at least `0.8`.                                                                                                                                             |
| `orientation`                                            | Conditional      | Required by active orientation policy. Verdict: `verified`, `axisymmetric`, `not_applicable`, `ambiguous`, `inconclusive`, or `not_required`. `ambiguous` is valid only for an imported existing model under `orientationRequirement="assess"`. |
| orientation axis                                         | Conditional      | Verified uses Editor-world `worldForwardAxis`: `+X`, `-X`, `+Y`, `-Y`, `+Z`, or `-Z`.                                                                                                                                                           |
| orientation reason                                       | Conditional      | `axisymmetric` or `not_applicable` uses `rotational_symmetry`, `full_rotational_symmetry`, or `no_intrinsic_axes` and confidence of at least `0.8`.                                                                                             |
| ambiguous orientation                                    | Conditional      | Requires non-empty `evidenceViewIds`, concrete `reason`, and confidence of at least `0.8`. It means the imported model itself has no reliably identifiable semantic forward; use `inconclusive` when evidence is insufficient.                  |
| confidence                                               | Conditional      | Finite number from 0 to 1. It is required and must be at least `0.8` for `frontAssessment.not_applicable`, `orientation.axisymmetric`, `orientation.not_applicable`, and ambiguous imported orientation.                                        |

Never infer Up Axis from screenshots. Use Workflow `sourceUpAxis`,
`importedTransform`, and `editorWorldUpAxis`. If both front and orientation provide
`worldForwardAxis`, they must match.

For a reused pillow or similar imported model with no reliable semantic forward,
submit passing inspected views, `semanticVerdict: "pass"`, a
`frontAssessment.verdict` of `not_applicable` when appropriate, and:

```json
{
  "orientation": {
    "verdict": "ambiguous",
    "evidenceViewIds": ["<inspected view IDs>"],
    "reason": "<why no semantic forward is distinguishable>",
    "confidence": 0.8
  }
}
```

Do not attach `revisionPrompt`; an ambiguous imported orientation never requests
replacement generation.

## Direct Scene Mutation Compatibility Boundary

Direct live scene query and mutation are not public Workflow operations. Do not use
their deprecated compatibility entries during a new Run. Submit the complete Scene
Plan requested by the current `editor-scene-plan` Handoff, or start a linked revision
Run for a requested change to a completed scene.

## Scene Plan Form

Use `scenePlanningContext.sceneFingerprint` for the form binding. Obtain the current
hierarchy, paths, transforms, and bounds directly from `get_scene_info`, then call
`get_entity_info` with `entity_path` for every existing entity the Plan will change.
These native Editor MCP queries are read-only and require no extra orchestration or
wrapper.

Optional `entityEdits` operates on existing entities without importing them again:

```json
{
  "entityEdits": [
    {
      "entityPath": "/Root/Chair",
      "action": "transform",
      "position": { "x": 1, "y": 0, "z": 0 },
      "reason": "Move the requested chair"
    }
  ]
}
```

This is a field of the complete Scene Plan below. `action="transform"` accepts one
or more of `position`, `rotationEuler`, and positive `scale`; these are local
transforms. `action="remove"` accepts no transforms and removes only the scene entity.
Use absolute `/Root/` paths. Edits must not overlap each other or any other Plan
worklist target. Unlisted existing content is preserved.

The Scene Plan is the complete scene-authoring contract. It owns final model
placements, additional instances, primitives, groups, materials, runtime nodes,
enhancements, and executable scene acceptance. Use the parent contract embedded in
the Handoff plus accepted model bounds and orientation evidence; do not expect those
worklists from an earlier brief.

For model orientation, `preserve_imported` retains the full imported rotation;
`yaw_from_imported` applies a world +Y yaw delta; `absolute_euler` is an explicit
absolute override.

Spatial Editor cannot currently author real light or audio entities. Do not invent
Primitive substitutes. Omit unsupported deferred light/audio requirements from this
Run's executable acceptance and represent only supported optional enhancements.

```jsonc
{
  "run_id": "<current public run id>",
  "task_id": "editor-scene-plan",
  "expected_revision": "<next.arguments.expected_revision>",
  "input": {
    "schemaVersion": "1.0",
    "sceneFingerprint": "<exact scenePlanningContext fingerprint>",
    "placements": [
      {
        "modelId": "<current Manifest model id>",
        "position": { "x": 0, "y": 0, "z": 0 },
        "orientation": {
          "mode": "preserve_imported",
        },
        "scale": { "x": 1, "y": 1, "z": 1 },
        "rationale": "<bounds- and relationship-based reason>",
      },
    ],
    "instances": [
      {
        "instanceId": "<stable managed instance id>",
        "sourceModelId": "<accepted Manifest model id>",
        "name": "<stable Editor entity name>",
        "position": { "x": 1, "y": 0, "z": 0 },
        "orientation": {
          "mode": "preserve_imported",
        },
        "scale": { "x": 1, "y": 1, "z": 1 },
        "rationale": "<reason this additional occurrence is required>",
      },
    ],
    "primitives": [
      {
        "id": "<stable primitive id>",
        "type": "Cube",
        "name": "<stable Editor entity name>",
        "parentPath": "<optional existing path>",
        "position": { "x": 0, "y": 0, "z": 0 },
        "rotationEuler": { "x": 0, "y": 0, "z": 0 },
        "sizeMeters": { "x": 1, "y": 1, "z": 1 },
        "color": { "r": 0.5, "g": 0.5, "b": 0.5, "a": 1 },
        "acceptance": ["<observable primitive criterion>"],
        "rationale": "<bounds- and scene-intent-based reason>",
      },
    ],
    "groups": [
      {
        "id": "<stable group id>",
        "name": "<stable Xform name>",
        "parentGroupId": "<optional submitted group id>",
        "members": [
          { "kind": "model", "modelId": "<model id>" },
          { "kind": "instance", "instanceId": "<managed instance id>" },
          { "kind": "primitive", "primitiveId": "<plan primitive id>" },
        ],
      },
    ],
    "removals": [
      {
        "kind": "model",
        "modelId": "<accepted model id whose primary scene node is no longer needed>",
        "reason": "<why this scene node must be removed>",
      },
      {
        "kind": "instance",
        "instanceId": "<previous managed instance id>",
        "reason": "<why this scene node must be removed>",
      },
      {
        "kind": "primitive",
        "primitiveId": "<previous managed primitive id>",
        "reason": "<why this scene node must be removed>",
      },
    ],
    "materials": [
      {
        "id": "<stable material id>",
        "targetPrimitiveId": "<primitive id>",
        "prompt": "<material intent>",
        "properties": {
          "color": { "r": 0.1, "g": 0.1, "b": 0.1 },
          "roughness": 0.8,
          "metallic": 0,
        },
        "outputPath": "<absolute USDA output path>",
        "required": true,
        "acceptance": ["<observable material criterion>"],
      },
    ],
    "runtimeNodes": [
      {
        "name": "<stable runtime node name>",
        "path": "./<path relative to the managed scene root>",
        "purpose": "<downstream runtime purpose>",
        "parentPath": ".",
        "transformOwner": "runtime",
      },
    ],
    "enhancements": [
      {
        "id": "<stable enhancement id>",
        "type": "lighting",
        "intent": "<requested enhancement intent>",
        "required": false,
        "targetPath": "<optional existing absolute path>",
        "requiredCapabilities": ["<known capability>"],
        "acceptance": ["<observable enhancement criterion>"],
      },
    ],
    "spatialQuality": {
      "checks": [
        {
          "id": "main_aisle",
          "type": "corridor",
          "firstEntityPath": "/Root/LeftSeating",
          "secondEntityPath": "/Root/RightSeating",
          "widthAxis": "x",
          "minimumMeters": 1.2,
        },
      ],
    },
    "sceneAcceptance": ["<observable executable scene criterion>"],
    "relationships": ["<task-derived relationship>"],
    "notes": "<optional non-executable note>",
  },
}
```

The form is a field map, not a default layout. Remove unused alternatives.

| Field                            | Required    | Rule                                                                                                                                                                                                       |
| -------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schemaVersion`                  | Yes         | Exactly `"1.0"`.                                                                                                                                                                                           |
| `sceneFingerprint`               | Yes         | Exact current planning fingerprint.                                                                                                                                                                        |
| `placements`                     | Yes         | Exactly one per current model; `[]` only when models are empty.                                                                                                                                            |
| placement position               | Yes         | Final world-space pivot in meters, derived from bounds/support/clearance.                                                                                                                                  |
| placement orientation            | Yes         | Provide exactly one of `orientation` or legacy `rotationEuler`. Use `preserve_imported` explicitly when no additional rotation is required.                                                                |
| legacy placement `rotationEuler` | Alternative | Absolute finite Euler values. Do not combine with `orientation`.                                                                                                                                           |
| placement scale                  | Yes         | Positive. Use `{x:1,y:1,z:1}` to preserve imported scale; change it only for an explicit user/upstream scale requirement.                                                                                  |
| placement rationale              | Yes         | Non-empty, evidence-based.                                                                                                                                                                                 |
| `instances`                      | Yes         | Complete additional-occurrence worklist; use `[]` when none. Reuse one `sourceModelId` as needed; every entry requires a unique stable `instanceId` and `name`.                                            |
| instance transform               | Yes         | Position, positive scale, rationale, and exactly one orientation mechanism follow the same rules as model placements.                                                                                      |
| `primitives`                     | Yes         | Complete final primitive set after bounds are known; use `[]` when none. Primitive-only scenes use `placements: []`.                                                                                       |
| primitive fields                 | Conditional | ID/type/name/position/positive size/acceptance/rationale required; rotation/normalized RGBA optional. Omit `parentPath` for grouped primitives; group membership determines their final parent.            |
| `groups`                         | Yes         | Complete identity-transform semantic hierarchy; use `[]` when none.                                                                                                                                        |
| group fields                     | Conditional | ID/name/members required; optional parent group. IDs/names are stable ASCII.                                                                                                                               |
| member reference                 | Conditional | Exactly one matching reference for its `kind`; never a path or bare string.                                                                                                                                |
| membership                       | Conditional | One deepest owning group per managed member; parent groups never repeat descendant members. Hierarchy must be acyclic with unique sibling names, and every leaf group must contain a supported member.     |
| `removals`                       | No          | Explicit removals of managed model/instance/primitive scene nodes. Remove the same item from placements/worklists/groups. Source asset files remain reusable and are never deleted.                        |
| `materials`                      | Yes         | Complete material worklist; use `[]` when none. Each item targets exactly one accepted model or submitted primitive.                                                                                       |
| `runtimeNodes`                   | Yes         | Complete runtime-owned node worklist; use `[]` when none. Prefer `./...` paths relative to the discovered scene root.                                                                                      |
| `enhancements`                   | Yes         | Complete requested lighting, animation, or effect worklist; use `[]` when none. Unsupported required work blocks.                                                                                          |
| `spatialQuality`                 | Yes         | Deterministic collision, clearance, corridor, bottleneck, and alignment checks bound to absolute current/planned entity paths. Empty checks are allowed only when no spatial relationship applies.         |
| spatial-quality thresholds       | No          | Per-check values override policy defaults. Conservative defaults are 0 m penetration, 0.9 m clearance, 1.2 m corridor/bottleneck, and 0.1 m alignment offset. Use `waiverReason` only for explicit intent. |
| `sceneAcceptance`                | Yes         | Complete non-empty executable whole-scene criteria. Omit unsupported deferred light/audio requirements.                                                                                                    |
| relationships, notes             | No          | Task-derived semantic relationships and concise non-executable context.                                                                                                                                    |

Use `scenePlanningContext.worldBounds`, pivot facts, imported transforms, reviewed
`worldForwardAxis`, support surfaces, and clearance. Do not copy coordinates from
this form. Preserve imported orientation by default; world yaw is a delta around
`+Y`, not a replacement for the model child's imported rotation.
When `scenePlanningContext.models[].presentInScene=false`, the primary node was
removed but the accepted asset remains reusable; add a new `instances` entry instead
of submitting a new model-production item.

Do not duplicate a `modelId` inside `placements`. Keep the accepted model's primary
entity there, and put every additional occurrence in `instances`. Groups may reference
a newly declared instance by its `instanceId` in the same Plan. Every instance
references the accepted `sourceModelId` and shared asset path; never create or rename
a copied USD/USDZ source file.

`removals` is one-shot. After successful assembly the persisted `previousPlan`
clears applied removals. On a later review-driven replan, copy the current
`previousPlan` and add only newly requested removals. Removing a primary model
removes only its scene node; its accepted source asset remains available for later
instances.

## Supplemental Evidence Form

Use only when the current `review-editor-output` Handoff input schema allows a
supplemental evidence request, after inspecting the complete current scene evidence,
and only when real occlusion prevents a reliable decision:

```jsonc
{
  "run_id": "<current public run id>",
  "task_id": "review-editor-output",
  "expected_revision": "<next.arguments.expected_revision>",
  "input": {
    "schemaVersion": "1.0",
    "baseEvidenceId": "<current scene evidence id>",
    "reason": "<concrete unresolved occlusion>",
    "occludedViewIds": ["<occluded original view>"],
    "members": [{ "kind": "model", "modelId": "<managed model id>" }],
    "contextMembers": [{ "kind": "primitive", "primitiveId": "<support id>" }],
    "viewIds": ["<smallest useful supplemental view>"],
  },
}
```

Members use the same model/instance/primitive discriminated references as groups.
`occludedViewIds` and `viewIds` contain 1-7 unique values from the six world-axis
views or `front_three_quarter`. Do not pass raw entity paths.

After supplemental capture, the next review Handoff exposes only the new isolated
captures in `Current review evidence`; inspect exactly its `payload.reviewViewIds`.
`primaryEvidenceId` and `supplementalEvidenceIds` preserve the complete evidence
lineage but do not require reopening earlier screenshots.

## User Decision Form

Submit only when the current Handoff requests `editor-user-decision`, after presenting
the current allowed actions to the user:

```jsonc
{
  "run_id": "<current public run id>",
  "task_id": "editor-user-decision",
  "expected_revision": "<next.arguments.expected_revision>",
  "input": {
    "gateId": "<exact pending decision gate>",
    "action": "<one returned allowed action>",
    "candidateEntityPath": "<optional current candidate path>",
    "evidenceRevision": "<required changed material evidence revision unless already supplied by the inconclusive review>",
    "keepGuiOpen": false,
    "notes": "<optional user decision note>",
  },
}
```

Never invent an action. Allowed actions can include:
`accept_current_candidate`, `authorize_generation_batch`,
`authorize_workflow_retry`, `authorize_scene_mutation`, `recapture_current`,
`continue_without_optional_work`, `inspect_in_gui`,
`retry_after_authentication`, `retry_after_provider_recovery`, and `cancel`.

At a `material-attempts:<id>` gate caused by authoring failure before preview,
`authorize_workflow_retry` may include `materialRevision` with a changed `prompt`,
`properties`, or `usdaText`. It corrects only the current material, resets its retry
batch, and returns to validation and preview. Previously accepted materials remain
accepted. Do not include this field for other decision actions or gates.

At `material:<id>` or `capture-attempts:material:<id>`, `recapture_current` requires
a changed `evidenceRevision`, either preserved from the inconclusive review or
included in the decision. The runtime binds it to current material evidence and
scene fingerprint; do not copy or invent those authority fields.

## Pre-Submission Checklist

Before every form submission:

1. Read the latest public Run and confirm `status="waiting"` with a Handoff; do not
   act from a cached response or a Snapshot-only state.
2. Copy the current `runId`, `next.arguments`, `next.submission`, gate,
   evidence, fingerprint, and allowed-action values. Pass that revision as
   `expected_revision`.
3. Remove placeholders and non-applicable optional fields.
4. Validate stable identifiers, absolute paths, positive dimensions, and normalized
   colors.
5. Validate cross-references and exactly-one target/member discriminators.
6. Ensure arrays satisfy required completeness: all review views, all model
   placements, and the complete final revision primitive set.
7. Submit once through `resume_editor_workflow`. If rejected, do not guess or call
   the deprecated advance entry; read `recovery.md` and correct the named field or
   state.

## Authored Material Graphs

Production material items and `materialRevision` may provide `usdaText` (non-empty,
at most 200,000 characters) for an authored ShaderGraph/MaterialX material. When
present, this text is authoritative: the Controller validates it with
`validate_material_usda` and previews only the normalized result with
`preview_material_usda`. Preset/property fields are not applied over the graph.
Omitting the field in a revision preserves the previously authored graph.

Discover actual node IDs and ports before authoring. Validation must explicitly
allow preview with zero errors. Existing visual review, commit and rollback remain
mandatory. For time-dependent effects, inspect multiple frames with a fixed camera
and verify persistence after saving/reopening; a time node or a single screenshot
is not proof of visible motion. Never report a static approximation as animated.

### Workflow Agent selection

The Editor workflow declares caller-only Agent tasks. Complete its handoffs in the calling session; do not select a managed Agent model to change the caller. A supplied model does not launch another Agent or change the 3D generation provider. Read the latest public Run and handoff before submitting a response.
