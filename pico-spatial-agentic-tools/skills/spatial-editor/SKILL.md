---
name: spatial-editor
description: 'Plans and runs managed Spatial Editor workflows to create or revise Editor-owned scenes, assets, composition, materials, effects, visual inspection, or packages. When an existing .bundle and .scenes.json pair only needs to be integrated or loaded into an app, use spatial-app-dev-workflow instead; do not reopen Editor.'
license: 'Apache-2.0'
---

# Spatial Editor Workflow

Use this Skill for Editor-owned 3D assets, scene composition, materials, effects,
visual review, packaging, and handoff. Kotlin Entity implementation, runtime
behavior, app builds, and device validation remain with the calling app workflow.

## Load Only What The Current State Needs

This Skill owns workflow intent and task decomposition. It deliberately does not
duplicate form schemas or error-code handling.

| Current need                                                                   | Action                                                                                                 |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| Choose Editor, decompose content, run the normal lifecycle, or prepare handoff | Continue with this file.                                                                               |
| Submit any Handoff                                                             | Read `contracts.md` from this Skill directory and obey the current live `next.submission.inputSchema`. |
| Handle a rejection, error, blocked Run, interruption, or user decision         | Read `recovery.md` from this Skill directory before acting.                                            |

Never reconstruct a form from this overview. Never preload `recovery.md` during a
healthy run, and never guess an error meaning that it defines.

## Ownership And Safety

Spatial Editor owns generated or imported models, primitive-authored prototypes
and other structural or dimension-driven geometry, Editor hierarchy and transforms,
materials, lighting/effects intent, visual inspection, and packaged authored content.
Use `spatial-sdk-scene-builder` when
Kotlin code owns Entity creation, runtime hierarchy, behavior, or dynamic transforms.
When both apply, Editor authors and packages first; app code consumes the handoff.

All production mutations and packaging must remain inside the managed public
Workflow Run. Before starting it, do not invoke a direct Editor readiness command or
start a standalone bootstrap session for the target project. A read-only status
check is allowed, but the Workflow Session must establish and own its Editor
process. If another session owns the same project, resolve ownership before writing.

Never bypass the Workflow Service or its Drivers with direct backend mutation,
scene creation, packaging, or unmanaged edits. Reflected `get_scene_info` and
`get_entity_info` calls are read-only observations and do not require a Workflow Handoff.

## Managed Workflow

Start through the stable `start_editor_workflow` compatibility facade. It starts the
public `spatial-3d-generation` root with `backendPreference="editor"`; never start the Editor Child directly or supply an internal Workflow ID.

Use the current working directory as `workspace_root` unless the user selected
another workspace. Treat the Workflow-returned `projectPath` as authoritative.
When the user selects an existing scene entry, pass its canonical project-relative
`Sources/Scenes/*.usd[a|c]` path as `target_scene_path`; do not leave it to the
model-plan placeholder heuristic.
Headless is the default; request GUI only for a reason allowed by `contracts.md`.

The normal loop is:

1. Start one public production Run for the workspace and goal.
2. Resume the initial `author-scene-spec` Handoff with every requested semantic
   subject and count.
3. At `editor-model-plan`, submit distinct model archetypes only. Repeated
   occurrences, final transforms, primitives, groups, materials, and runtime nodes
   belong to scene planning.
4. Let deterministic work advance. When `next.action="wait"`, call `next.tool` with
   its returned bounded arguments.
5. Inspect every required model/material view and submit the current review.
6. Before scene planning, inspect the live hierarchy with `get_scene_info`, then
   inspect every existing target with `get_entity_info`.
7. Submit one complete Scene Plan from accepted bounds, imported transforms,
   orientation evidence, current scene facts, and task-derived acceptance.
8. Inspect the final six world-axis views, front three-quarter view, and required
   `top_down_orthographic` view. Request supplemental evidence only for real
   occlusion.
9. Accept only when physical, semantic, visual, functional, and deterministic
   spatial-quality checks pass.
10. Let the managed Run package, write provenance and handoff metadata, and clean up.

The current Workflow checks the live `get_viewport_screenshot` schema before final
scene capture. When it returns `EDITOR_ORTHOGRAPHIC_CAPTURE_UNSUPPORTED`, do not
retry, omit fields, or substitute a perspective image. The installed Spatial Editor
package must be updated to a republished build that exposes both
`camera_projection` and `camera_orthographic_size`; then resume the same Run and
choose `recapture_current`.

Treat every Workflow MCP response as one observation of the public Run. Read
`runId`, `current`, `next`, `error`, and terminal `result`/`artifacts`/`evidence`,
then discard the previous response.

For any submit action, call `next.tool` with `next.arguments` plus one `input` object
that validates against `next.submission.inputSchema`. Use
`next.submission.kind`; never infer task IDs, revisions, or wait durations.
`get_editor_workflow_status` is observation-only. During model work,
`current.module`, `current.phase`, and `current.models` provide compact progress.
`advance_editor_workflow` is a deprecated observation-only compatibility entry.

A Handoff mismatch is a non-terminal rejection: the Workflow Service preserves the
current public waiting state. Read it again and submit only the current Handoff.
After interruption or reconnect, continue the same public `runId`. A persisted
`native-runtime/editor-modules/<module>/recovery.md` is read-only audit evidence,
not a state mutation channel.

## Task Decomposition

Before model production, separate:

1. Distinct generated/imported model archetypes.
2. Repeated occurrences that can reuse one accepted archetype.
3. Structural or dimension-driven primitives.
4. Requested material work and semantic targets.
5. Whole-scene relationships and acceptance.
6. Optional lighting, animation, or effects.
7. Downstream runtime-node and delivery contracts.

Do not turn undocumented preferences into requirements. Every criterion must trace
to the request or an accepted upstream contract.

### Asset Archetypes And Reuse

Reuse when occurrences share form, appearance, and semantic role. Put one archetype
in model production and additional occurrences in the Scene Plan. Reuse is a design heuristic, not an acceptance gate; keep separate assets when identity, function,
geometry, or acceptance differs.

### Structural Primitives

Use primitives for dimension-driven floors, walls, columns, platforms, partitions,
and simple volumes. Use generated/imported assets when silhouette, topology,
curvature, ornament, or semantic identity requires authored geometry.

Defer final primitive transforms until accepted model bounds are known:

- Model-only: placements and optional instances.
- Mixed: placements, instances, and final primitives.
- Primitive-only: empty models and placements, with final Plan primitives.

The Scene Plan owns concrete primitive definitions and transforms. Exact fields live
only in `contracts.md`.

### Scene Intent And Hierarchy

Create material work only for requested or contract-required properties. Explicit
color, emission, opacity, roughness, metallic behavior, and render mode require
structured properties. A primitive display color is only an RGBA fallback, not
proof of a PBR or emissive material.

Group only coherent assemblies that should be selected, moved, duplicated, or
inspected together. Groups are identity-transform `Xform` nodes. Declare `scene.runtimeNodes` only for downstream-addressable entities; use `./...` from the
discovered managed root and never derive a root path from `scene.name`.

## Visual And Spatial Review

Actually inspect every image referenced by current evidence. File existence, a
successful call, bounds, or a package is not visual proof.

For `reuse_required`, scope that model's evidence-image review to direction-related evidence only. Do not evaluate or fail geometry, appearance, topology, or detail,
and use `orientation.verdict="ambiguous"` when an imported model has no reliable
semantic front. This is not a request to generate a replacement; final scene review still
evaluates placement and physical/spatial defects.

Clearly evidenced floating, penetration, instability, unusable scale, obstruction,
or an explicit requirement violation blocks acceptance. Depth-dependent findings
need multiple views. Use inconclusive or supplemental evidence when visibility is
insufficient.

Before final planning:

1. Read required runtime-node paths and parents.
2. Read world bounds and imported transforms for every accepted model.
3. Treat placement as the entity pivot; derive pivot-to-bottom and pivot-to-center.
4. Ground objects on real supports and derive spacing from measured extents.
5. Determine scale from measured bounds and scene relationships; never supply category-based default dimensions.
6. Preserve imported rotation unless evidenced semantic direction requires a world
   `+Y` heading delta.
7. Check containment, circulation, access, occlusion, and interpenetration.

Axis-aligned bounds overlap alone does not prove penetration.

### Motion And Animation

For direction-sensitive motion, derive heading from velocity or trajectory tangent,
apply it to an identity-transform parent/runtime owner, and preserve the model
child's imported rotation and reviewed `worldForwardAxis`.

## Existing Scenes And Revision

A runId is an execution record; it does not own permission to edit a scene. For new
work in an existing project, inspect live scene/entity facts and use production
modify. An empty default `Hi.usda` is a placeholder unless the start request
explicitly names it as `target_scene_path` or inspection proves it has authored
content. Preserve unrelated content.

Linked revision is optional legacy inheritance for a completed parent delivery.
Read parent scene hints included in the current `editor-revision-plan` Handoff instructions and confirm them against live state. Preserve user-modified content
unless the user explicitly authorizes changing it.

After revision asset work, submit a complete final Scene Plan. Add structural work
through `add_primitive`, and include the complete retained primitive set. If a plan
or final review fails, correct it within the same Run; never replace the Run merely
to clear a rejection.

## Completion And Handoff

Required unsupported capabilities block. Optional unsupported work is reported in
`unsupportedWork`. Custom component declaration sync is separate and uses
`pico-cli editor sync component`.

A successful managed Run packages before cleanup. Return:

- Project and accepted scene paths.
- Co-located `<bundleName>.bundle`, `<bundleName>.scenes.json`, and provenance.
- Managed Run/revision/fingerprint/gate proof and SHA-256 digests.
- Runtime-node, orientation, material, warning, and unsupported-work results.

The calling app workflow owns loading, Kotlin integration, build, install, launch,
and runtime validation. A completed handoff is immutable; further authored changes
start a new managed Run against the live project. Direct CLI packaging is an
unmanaged escape hatch and is never a completed Workflow delivery.
