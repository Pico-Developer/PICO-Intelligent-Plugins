---
name: spatial-editor
description: 'Plans and runs managed Spatial Editor authoring and handoff workflows. Invoke for new or revised Editor-owned scenes, assets, composition, materials, effects, visual inspection, or packaging.'
license: 'Apache-2.0'
metadata:
  version: '2.47.0'
---

# Spatial Editor Workflow

Use this Skill to decide when Spatial Editor owns the work, decompose the authored
content, run the managed workflow, review visual results, and hand completed content
to downstream app work.

Do not use it for Kotlin Entity implementation, runtime behavior, build repair,
emulator/device validation, or loading an existing bundle without changing authored
content. Those concerns remain with the calling app workflow.

## Companion Skill Routing

This Skill owns workflow intent and task decomposition. It deliberately does not
duplicate form schemas or error-code handling.

| Situation                                                                                                                                                                         | Required Skill                                                          |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Deciding whether to use Editor, decomposing content, planning assets/layout, understanding lifecycle or handoff                                                                   | Continue with `spatial-editor`.                                         |
| Before `submit_editor_manifest`, `submit_editor_review`, `submit_editor_scene_plan`, `submit_editor_scene_mutation`, `request_editor_scene_evidence`, or `submit_editor_decision` | Read `contracts.md` from this Skill directory and use its current form. |
| Controller rejects a form, returns `errors[]`, `EDITOR_*`, `interrupted`, or a user-decision gate                                                                                 | Read `recovery.md` from this Skill directory before acting.             |

Never reconstruct a form from this workflow overview. Never interpret an error by
guessing from its name when `recovery.md` covers it.

## When To Use Editor

Spatial Editor owns:

- Generated or imported 3D model assets.
- Primitive-authored structural or dimension-driven geometry.
- Editor scene composition, visual hierarchy, materials, lighting, effects, and
  animation intent.
- Model, material, enhancement, and final scene visual inspection.
- Packaged Editor content and editor-to-app handoff.
- Custom component declaration sync required for later Editor authoring.

Use `spatial-sdk-scene-builder` instead when Kotlin/Spatial SDK code owns Entity
creation, hierarchy, placement, runtime behavior, or dynamic transforms. When both
apply, Editor produces authored content first and Scene Builder consumes the handoff.

## Managed Workflow

Do not call dynamic Editor backend tools directly during a managed workflow. The
Controller owns execution order, retries, generation/import polling, assembly,
packaging, cleanup, and persisted checkpoints.

The normal production lifecycle is:

1. Start one managed production run for the current workspace and goal.
2. Decompose the request and submit a production Manifest using `contracts.md`.
3. Follow `nextAction`. Advance deterministic steps once; use managed wait for
   long-running model generation/import.
4. Inspect every model evidence view and submit the bound Agent review.
5. When scene planning begins, query/mutate managed instances only when needed.
6. Use accepted model bounds, imported transforms, reviewed orientation, scene
   intent, and current instances to submit one complete Scene Assembly Plan.
7. Let the Controller assemble models, primitives, and groups before material work.
8. Inspect and submit every required material/enhancement review.
9. Inspect the final six world-axis views plus front three-quarter view. Request
   minimal supplemental evidence only for real occlusion.
10. Accept only when required physical, semantic, visual, and functional criteria are
    evidenced.
11. Let the Controller package the accepted scene, write handoff metadata, and clean
    up.

Treat every Controller result as one state-machine instruction. Before each workflow
tool call, read the latest result and dispatch its exact `nextAction.type`; after the
call, discard the previous instruction and parse the newly returned state. Never use
a generic advance-then-wait helper or an automatic progression loop that handles only
some action types.

Use `advance_editor_workflow` only for `advance` and `wait_editor_workflow` only for
`wait`. `submit_manifest`, `submit_review`, `submit_scene_plan`, `submit_decision`,
and `resume` are hard stops that require their matching action before any further
progression. If a non-terminal result has an absent or unknown action, stop and read
`contracts.md` and `recovery.md`; do not guess. After reconnect, fetch current status.
On interruption, read `recovery.md` and resume the persisted run.

An action mismatch is a non-terminal rejection: the Controller preserves the current
gate and returns its latest `nextAction`. Follow that action instead of abandoning or
replacing the run.

## Project Resolution

Use the current working directory as the absolute workspace root unless the user
explicitly selects another workspace.

Omit project overrides by default. The Controller deterministically creates or reuses
the standard project under the workspace. Supply a custom project path or name only
when the user explicitly requests it, then treat the Controller-returned
`projectPath` as authoritative for the entire run.

Headless is the default execution mode. Use GUI only when visible interaction is
required, such as an explicit user request or authentication. The exact start form
and allowed reasons live in `contracts.md`.

## Task Decomposition

Before submitting the Manifest, divide the goal into:

1. Distinct generated/imported model archetypes.
2. Repeated occurrences that can reuse one accepted archetype.
3. Structural or dimension-driven elements better authored as primitives.
4. Requested material work and its semantic targets.
5. Whole-scene relationships and acceptance criteria.
6. Optional lighting, animation, or effect work.
7. Downstream runtime-node and delivery contracts.

Do not turn undocumented preferences into requirements. Every acceptance criterion
must trace to the user request or an accepted upstream contract.

### Asset Archetypes And Reuse

The user does not need to say "reuse." Consider reuse when occurrences share the same
requested form, appearance, and semantic role. Represent one selected archetype in
the Manifest, then create additional managed instances during scene planning.

Reuse is a design heuristic, not an acceptance gate. Preserve separate model work
when geometry, appearance, function, identity, or acceptance requires meaningful
variation. Choose counts and arrangement from scene purpose, available space, and
measured bounds rather than a fixed default.

### Structural Primitives

Separate the structural envelope from independently placeable furniture, fixtures,
and equipment. Prefer supported primitives when an element is primarily defined by
dimensions, placement, openings, and finish. Typical non-normative candidates include
floors, ceilings, straight wall segments, columns, platforms, partitions, and simple
built-in volumes.

Use generated/imported models when silhouette, topology, curvature, ornamentation,
integrated detail, semantic identity, or a design reference requires authored
geometry. A requested finish alone does not require generated geometry.

For new workflows, defer final primitive position, rotation, and size until accepted
model bounds are available. The Scene Plan is the authority for final primitives:

- Model-only: placements, no plan primitives.
- Mixed: model placements and final primitives in the same Plan.
- Primitive-only: empty model list and placements, final geometry in Plan primitives.

Legacy Manifest primitives remain compatibility input only. Exact fields and material
forward references live in `contracts.md`.

### Materials

Create material work only for requested or contract-required surface properties.
Keep generated material preview, compilation, visual review, commit, and rollback
inside the Controller.

When exact color, emission, opacity, roughness, metallic behavior, or render mode is
part of acceptance, provide explicit `properties` through `contracts.md`; do not rely
on natural-language interpretation alone. A failed material review must change the
effective prompt or structured properties before another preview.

A primitive display color is only a normalized RGBA fallback. Never report it as an
emissive, PBR, or visually verified material. The Controller assembles plan-native
primitives first so material work can resolve their real managed paths.

### Scene Intent And Hierarchy

Whole-scene intent describes composition and requested relationships, not model
generation details. Derive hierarchy from editing and runtime semantics:

- Prefer a group for a coherent local assembly that should be selected, moved,
  duplicated, or inspected as one unit.
- Shared type or proximity alone is insufficient.
- Avoid broad wrappers, decorative one-member groups, and grouping that breaks
  independent interaction, animation ownership, or runtime paths.
- When the user or scene acceptance explicitly requires a named hierarchy, the Plan
  must include it.

Groups are identity-transform `Xform` nodes. The exact member discriminators,
identifier rules, and nesting constraints live in `contracts.md`.

Declare `scene.runtimeNodes` only for entities that downstream runtime code must
address. For create-mode managed content, use `./...` paths relative to the
Controller-discovered scene root; never derive a root path from `scene.name`. Use an
absolute path only when an existing path is already evidenced. The Controller
normalizes resolved paths in final validation and handoff.

## Visual Review

Actually inspect every image referenced by current evidence. A successful tool call,
file existence, bounds record, or package is not visual proof.

Use a conservative failure policy:

- When the user explicitly requires model reuse
  (`source.strategy="reuse_required"`), scope that model's evidence-image review to
  direction-related evidence only: semantic front, up-axis consistency, and imported
  orientation. Do not evaluate or fail geometry, appearance, topology, detail, or
  other model-quality characteristics, and do not request regeneration for them.
  When an imported existing model has no reliably identifiable semantic forward,
  use `orientation.verdict="ambiguous"` with inspected evidence and rationale. This
  is an accepted imported-asset result, not a request to generate a replacement.
  This exception is limited to model-quality review; final scene review still
  evaluates placement and physical/spatial defects.
- Do not fail an unrequested incidental detail unless it changes required identity,
  structure, semantics, function, or causes an evidenced physical/spatial defect.
- Any clearly evidenced floating, penetration, instability, unusable scale,
  obstruction, or explicit requirement violation blocks acceptance.
- Depth-dependent physical findings require multiple views.
- If evidence is insufficient, use inconclusive or request supplemental scene
  evidence for actual occlusion.
- A failed model-quality review supplies a fresh replacement prompt preserving valid
  user intent; it is not appended feedback history.

The exact review form, enums, conditional front/orientation fields, and blocking
evidence categories live only in `contracts.md`.

## Orientation And Layout

Every model is captured from all six Editor-world axes. Scene review uses the same
six axes plus an elevated front three-quarter view.

Up Axis is metadata, not a visual guess. Use Controller `sourceUpAxis`,
`importedTransform`, and `editorWorldUpAxis`. Visual review may establish semantic
`worldForwardAxis` after import.

Before final Scene Plan submission:

1. Read every `scenePlanningContext.runtimeNodes` entry and ensure the Plan creates
   or preserves its exact path and parent.
2. Read world bounds min/max/center/extent for every accepted model.
3. Treat placement position as entity pivot, not bounds center.
4. Derive pivot-to-bottom and pivot-to-center offsets from imported position and
   measured bounds.
5. Ground objects against their real support surface.
6. Derive spacing from both objects' horizontal half-extents and intentional
   clearance.
7. Preserve imported scale and full imported rotation by default.
8. Apply horizontal facing as a world `+Y` heading delta only when semantic direction
   matters.
9. Check support, containment, circulation, access, occlusion, scale, and
   interpenetration across the whole plan.

Axis-aligned bounds overlap is not conclusive penetration for curved, concave, nested,
or intentionally contacting geometry. Use all scene views before judging physical
validity.

### Motion And Animation

For a direction-sensitive moving model:

- Read reviewed `worldForwardAxis` and current `importedTransform`.
- Derive desired world heading from instantaneous velocity or trajectory tangent.
- Compute only the heading delta from reviewed semantic front to motion direction.
- Apply motion and heading to a dedicated identity-transform parent/runtime owner.
- Preserve the model child's complete imported rotation.

Never hardcode an unrelated fixed yaw, reset the child to identity, overwrite its
full quaternion with heading-only Euler rotation, or invent a front for a model whose
review established none.

## Revision Workflow

Every requested change to a completed managed scene uses a new revision run linked by
`base_run_id`. Do not resume a terminal run and do not start production modify for
that scene.

Revision inherits unaffected accepted assets, evidence, paths, primitives, instances,
and ownership. Use selective operations for requested additions, removals,
regeneration, transforms, primitive changes, entity removal, or recomposition.

Preserve user-modified content by default. Changing a target modified outside the
parent workflow requires explicit user approval. The accepted
`finalSceneSnapshot.scenePath` is authoritative for legacy handoff discrepancies.

After revision asset work, submit a complete final Scene Plan. Keep every retained
primitive in that Plan and omit only explicitly removed content. Use `contracts.md`
for revision operations and `recovery.md` for stale/conflicting revision state.

If a revision plan is rejected, preserve the same revision run and correct only that
plan. Never bypass the Controller with direct `execute_script`, scene creation, or
unmanaged primitive edits. Add a floor, wall, platform, or other structural primitive
through `add_primitive`, then include the complete retained primitive set in the
final Scene Plan.

## Capability Boundaries

Lighting, animation, and effects execute only through stable capabilities exposed by
the connected Editor. Required unsupported work blocks. Optional unsupported work is
reported in `unsupportedWork`. Do not replace missing capabilities with guessed
`execute_script` APIs.

Custom component declaration sync is separate from 3D production. Use
`pico-cli editor sync component` without starting a production workflow.

## Completion And Handoff

Every successful production or revision run packages the accepted scene before
cleanup. Do not call `pack_editor_bundle` as a second delivery step.

Return the completed handoff to the calling app workflow:

- Project and accepted scene paths.
- Co-located `<bundleName>.bundle` and `<bundleName>.scenes.json`.
- Runtime-node contracts.
- Accepted orientation records.
- Material/application results.
- Warnings and unsupported optional work.

The calling app workflow owns bundle loading, Kotlin integration, build,
installation, launch, and runtime validation. A completed handoff is immutable;
future authored changes start a revision.
