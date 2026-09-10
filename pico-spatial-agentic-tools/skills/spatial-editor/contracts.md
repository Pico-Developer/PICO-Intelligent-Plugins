# Spatial Editor Controller Contracts

Read this module for the exact interaction contract between the Agent and the managed
Spatial Editor Workflow Controller.

- Read `SKILL.md` for workflow selection, task decomposition, visual planning, and
  handoff.
- Read this file before any `submit_editor_*` or
  `request_editor_scene_evidence` call.
- Read `recovery.md` when a submission is rejected or the Controller returns an
  error, interruption, or user-decision gate.

This file is the sole source of truth for Agent-authored forms. `SKILL.md` must not
redefine these fields, and `recovery.md` may refer to them but must not fork them. If
the live MCP input schema differs from this document, obey the live schema and report
the version mismatch.

## Interaction Rules

1. Use only managed tools while a workflow is active. Do not call dynamic Editor
   backend tools directly.
2. Copy `run_id`, `gateId`, `evidenceId`, `sceneFingerprint`, allowed actions, and
   entity references from the current Controller result. Never reuse stale values.
3. Follow `nextAction.type`:
   - `advance`: call `advance_editor_workflow`.
   - `wait`: call `wait_editor_workflow`; do not poll with repeated `advance` calls.
   - `submit_manifest`: submit the production Manifest or revision plan.
   - `submit_review`: inspect all required evidence, then submit one review.
   - `submit_scene_plan`: submit a complete final Scene Assembly Plan.
   - `submit_decision`: ask the user and submit only an allowed action.
   - `resume`: call `resume_editor_workflow` before any other workflow operation.
4. Consume each Controller result once. After every tool call, replace the previous
   `phase`, `status`, `nextAction`, IDs, and allowed actions with the newly returned
   values before selecting another tool.
5. Never use an advance-then-wait helper or a dispatcher that handles only some
   action types. An automated dispatcher must exhaustively handle every type above
   and stop on an absent or unknown action rather than falling through to `advance`.
6. Omit optional fields without a task-derived value. Never submit placeholders,
   comments, JSONC trailing commas, or both sides of a mutually exclusive choice.
7. Stable IDs and Editor names must match `^[A-Za-z_][A-Za-z0-9_]*$`.
8. Vector objects always contain finite numeric `x`, `y`, and `z`. Positive vectors
   require every component to be greater than zero.

## Start Form

```jsonc
{
  "workflow_kind": "production",
  "workspace_root": "<absolute workspace root>",
  "goal": "<current user goal>",
  "project_path": "<optional absolute project override>",
  "project_name": "<optional stable project name>",
  "preferred_mode": "headless",
  "gui_reason": "<required only with gui>",
}
```

| Field            | Requirement                                                                                                      |
| ---------------- | ---------------------------------------------------------------------------------------------------------------- |
| `workflow_kind`  | Omit or use `production` for new/external content. Use `revision` for every change to a completed managed scene. |
| `workspace_root` | Required for production and must be absolute. Revision inherits it.                                              |
| `base_run_id`    | Required only for revision; use the completed parent run ID.                                                     |
| `goal`           | Required current user goal.                                                                                      |
| `project_path`   | Optional absolute override. Omit unless explicitly needed.                                                       |
| `project_name`   | Optional stable name. It must match an existing project selected by `project_path`.                              |
| `preferred_mode` | Omit or use `headless`. Use `gui` only when visible Editor interaction is required.                              |
| `gui_reason`     | Required only with `gui`: `user_requested`, `authentication`, `capture_fallback`, or `tool_requires_gui`.        |

## Production Manifest Form

Submit through `submit_editor_manifest` with `workflow_kind="production"`.

```jsonc
{
  "run_id": "<current run id>",
  "workflow_kind": "production",
  "manifest": {
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
| `source.assetPath`                   | No          | Absolute local path. Use with `reuse_required`; never combine with `generate_fresh`.                                                                                                                                                                                                                                        |
| `provider`                           | No          | Explicit overrides only. `faceCount` is a positive integer.                                                                                                                                                                                                                                                                 |
| `position`, `rotationEuler`, `scale` | No          | Initial hints only; final transforms belong to the Scene Plan. Scale components are positive.                                                                                                                                                                                                                               |
| `targetHeightMeters`                 | No          | Positive evidenced target height. Do not combine with non-identity `scale`.                                                                                                                                                                                                                                                 |
| `expectedBoundsMeters`               | No          | Evidence-backed positive extent limits and non-negative tolerance.                                                                                                                                                                                                                                                          |
| `captureViewSet`                     | No          | Omit or use `six_axis`; no other value is valid.                                                                                                                                                                                                                                                                            |
| `frontRequirement`                   | No          | `required`, `assess`, or `none`.                                                                                                                                                                                                                                                                                            |
| `orientationRequirement`             | No          | `forward_and_up`, `up_axis`, `assess`, or `none`.                                                                                                                                                                                                                                                                           |
| `models[].acceptance`                | Yes         | Non-empty observable model criteria.                                                                                                                                                                                                                                                                                        |
| `primitives`                         | No          | Legacy compatibility only. New workflows define final primitives in the Scene Plan.                                                                                                                                                                                                                                         |
| `materials`                          | Yes         | May be empty.                                                                                                                                                                                                                                                                                                               |
| material target                      | Exactly one | Set `targetModelId` or `targetPrimitiveId`, never both/neither. A primitive target may forward-reference a later Plan primitive.                                                                                                                                                                                            |
| `materials[].properties`             | No          | Explicit Editor authoring values. Provide them whenever exact color, emission, opacity, roughness, metallic value, or render mode is acceptance-critical.                                                                                                                                                                   |
| `properties.color`                   | No          | Normalized RGB object. The Controller maps it to Editor `color: [r,g,b]`.                                                                                                                                                                                                                                                   |
| normalized material values           | No          | `opacity`, `roughness`, `metallic`, and `opacityThreshold` are from 0 to 1.                                                                                                                                                                                                                                                 |
| `properties.emissiveStrength`        | No          | Non-negative explicit emission strength. Pair it with `color` when emission color matters.                                                                                                                                                                                                                                  |
| material render switches             | No          | Boolean `transparent`, `depthWrite`, and `depthTest`; documented blend and culling enums only.                                                                                                                                                                                                                              |
| `materials[].outputPath`             | Yes         | Absolute committed USDA path.                                                                                                                                                                                                                                                                                               |
| `materials[].acceptance`             | Yes         | Non-empty observable material criteria.                                                                                                                                                                                                                                                                                     |
| `scene.mode`                         | Yes         | `create` or `modify`. Delivered managed scenes never use production modify; use revision.                                                                                                                                                                                                                                   |
| `scene.name`                         | Conditional | Required for `create`.                                                                                                                                                                                                                                                                                                      |
| `scene.expectedPath`                 | Conditional | Required for external `modify`; exact active scene path.                                                                                                                                                                                                                                                                    |
| `scene.prompt`, `acceptance`         | Yes         | Composition intent and non-empty whole-scene criteria.                                                                                                                                                                                                                                                                      |
| `scene.runtimeNodes`                 | No          | Declare only nodes required by downstream runtime code. For create-mode managed entities, use `./...` relative to the discovered scene root (`.` means the root); never derive the root from `scene.name`. Use absolute paths only for already-evidenced existing entities. The handoff contains normalized absolute paths. |
| `enhancements`                       | No          | Requested `lighting`, `animation`, or `effect` work only. Acceptance is non-empty.                                                                                                                                                                                                                                          |
| `requiredCapabilities`               | No          | Known hard capability names only; do not guess.                                                                                                                                                                                                                                                                             |
| `delivery`                           | No          | Explicit destination/name overrides; it does not enable packaging.                                                                                                                                                                                                                                                          |

`blendingMode` is one of `OPAQUE`, `TRANSPARENT`, `MASKED`, `ADD`, or
`FADE`. `faceCulling` is one of `NONE`, `FRONT`, or `BACK`. The Controller maps
camelCase Manifest fields to the Editor's `emissive_strength`, `blending_mode`,
`face_culling`, `depth_write`, `depth_test`, and `opacity_threshold` arguments.

## Revision Plan Form

For a completed managed scene, start with `workflow_kind="revision"` and
`base_run_id`, then submit:

```jsonc
{
  "run_id": "<revision run id>",
  "workflow_kind": "revision",
  "revision_plan": {
    "schemaVersion": "1.0",
    "sceneFingerprint": "<exact revisionContext fingerprint>",
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
| `remove_entity`    | `entityPath`, `reason`                                             | Exact inherited top-level path from `revisionContext.entities`.                                                                        |
| `recompose`        | none                                                               | Requests a new full Scene Plan without inventing an asset change.                                                                      |

Set `allowUserModifiedTargets=true` only after explicit user approval. After revision
asset work, the final Scene Plan includes every retained, added, or updated primitive;
omit only explicitly removed primitives.

## Review Form

Submit only at `waiting_for_agent_review`. Copy the current gate, evidence, and every
required view.

```jsonc
{
  "run_id": "<current run id>",
  "review": {
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
| unchanged material revision                              | Invalid          | The effective prompt or properties must change. The Controller rejects an identical retry instead of consuming another attempt.                                                                                                                 |
| `frontAssessment`                                        | Conditional      | Required by active front policy. Verdict: `verified`, `not_applicable`, or `inconclusive`.                                                                                                                                                      |
| front evidence                                           | Conditional      | Verified requires passing `viewId` or `evidenceViewIds`.                                                                                                                                                                                        |
| front reason                                             | Conditional      | Not applicable uses `rotational_symmetry` or `no_intrinsic_front`.                                                                                                                                                                              |
| `orientation`                                            | Conditional      | Required by active orientation policy. Verdict: `verified`, `axisymmetric`, `not_applicable`, `ambiguous`, `inconclusive`, or `not_required`. `ambiguous` is valid only for an imported existing model under `orientationRequirement="assess"`. |
| orientation axis                                         | Conditional      | Verified uses Editor-world `worldForwardAxis`: `+X`, `-X`, `+Y`, `-Y`, `+Z`, or `-Z`.                                                                                                                                                           |
| orientation reason                                       | No               | `rotational_symmetry`, `full_rotational_symmetry`, or `no_intrinsic_axes`.                                                                                                                                                                      |
| ambiguous orientation                                    | Conditional      | Requires non-empty `evidenceViewIds`, concrete `reason`, and confidence of at least `0.8`. It means the imported model itself has no reliably identifiable semantic forward; use `inconclusive` when evidence is insufficient.                  |
| confidence                                               | No               | Finite number from 0 to 1.                                                                                                                                                                                                                      |

Never infer Up Axis from screenshots. Use Controller `sourceUpAxis`,
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

## Scene Mutation Form

Use only while waiting for a Scene Plan:

```jsonc
{
  "run_id": "<current run id>",
  "plan": {
    "schemaVersion": "1.0",
    "sceneFingerprint": "<exact current fingerprint>",
    "operations": [
      {
        "op": "<remove|instantiate|duplicate|set_transform>",
      },
    ],
  },
}
```

| Operation       | Required fields                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------ |
| `remove`        | `entityPath`, `reason`; it must be the only operation in that plan.                              |
| `instantiate`   | `modelId`, new stable `instanceId`, stable `name`, `position`; optional rotation/scale.          |
| `duplicate`     | `sourceInstanceId`, new stable `instanceId`, stable `name`, `position`; optional rotation/scale. |
| `set_transform` | `entityPath` plus at least one of position, rotation, or positive scale.                         |

Use 1-50 operations. Refresh the fingerprint after every successful mutation. An
unmanaged removal requires a Controller user-decision gate.

## Scene Plan Form

`plan.primitives` is the authoritative final primitive set for new and revision
workflows. It is evaluated together with model placements and optional groups.
The current `scenePlanningContext.runtimeNodes` array is also mandatory planning
input: each root-relative runtime node must be created or preserved at its declared
path and parent by the submitted placements, primitives, and groups.

```jsonc
{
  "run_id": "<current run id>",
  "plan": {
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
    "relationships": ["<task-derived relationship>"],
    "notes": "<optional non-executable note>",
  },
}
```

The form is a field map, not a default layout. Remove unused alternatives.

| Field                            | Required    | Rule                                                                                                         |
| -------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------ |
| `schemaVersion`                  | Yes         | Exactly `"1.0"`.                                                                                             |
| `sceneFingerprint`               | Yes         | Exact current planning fingerprint.                                                                          |
| `placements`                     | Yes         | Exactly one per current model; `[]` only when models are empty.                                              |
| placement position               | Yes         | Final world-space pivot in meters, derived from bounds/support/clearance.                                    |
| placement orientation            | No          | `preserve_imported`; `yaw_from_imported` plus `yawDegrees`; or `absolute_euler` plus `rotationEuler`.        |
| legacy placement `rotationEuler` | No          | Do not combine with `orientation`.                                                                           |
| placement scale                  | No          | Positive; preserve imported scale by default.                                                                |
| placement rationale              | Yes         | Non-empty, evidence-based.                                                                                   |
| `primitives`                     | No          | Final primitive set after bounds are known. Model-only omits it; primitive-only uses `placements: []`.       |
| primitive fields                 | Conditional | ID/type/name/position/positive size/acceptance/rationale required; parent/rotation/normalized RGBA optional. |
| `groups`                         | No          | Identity-transform semantic hierarchy.                                                                       |
| group fields                     | Conditional | ID/name/members required; optional parent group. IDs/names are stable ASCII.                                 |
| member reference                 | Conditional | Exactly one matching reference for its `kind`; never a path or bare string.                                  |
| membership                       | Conditional | One group per managed member; hierarchy must be acyclic with unique sibling names.                           |
| relationships, notes             | No          | Task-derived semantic relationships and concise non-executable context.                                      |

Use `scenePlanningContext.worldBounds`, pivot facts, imported transforms, reviewed
`worldForwardAxis`, support surfaces, and clearance. Do not copy coordinates from
this form. Preserve imported orientation by default; world yaw is a delta around
`+Y`, not a replacement for the model child's imported rotation.

## Supplemental Evidence Form

Use only after inspecting the complete current scene evidence and only when real
occlusion prevents a reliable decision:

```jsonc
{
  "run_id": "<current run id>",
  "request": {
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

## User Decision Form

Submit only after presenting the current allowed actions to the user:

```jsonc
{
  "run_id": "<current run id>",
  "decision": {
    "gateId": "<exact pending decision gate>",
    "action": "<one returned allowed action>",
    "candidateEntityPath": "<optional current candidate path>",
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

## Pre-Submission Checklist

Before every form submission:

1. Read the latest Controller result and confirm its workflow phase and
   `nextAction.type`; do not act from a cached response.
2. Copy current run/gate/evidence/fingerprint values.
3. Remove placeholders and non-applicable optional fields.
4. Validate stable identifiers, absolute paths, positive dimensions, and normalized
   colors.
5. Validate cross-references and exactly-one target/member discriminators.
6. Ensure arrays satisfy required completeness: all review views, all model
   placements, and the complete final revision primitive set.
7. Submit once. If rejected, do not guess or repeatedly advance; read `recovery.md`
   and correct the named field or state.
