# Managed Shader Graph Material Production

Order: saved assembly → selected Shader Graph authoring and binding → `produce-particles`
→ final freeze and seven-view review.

The main Agent selects material routes before SceneSpec. Ordinary opaque colors use
default PBR RGBA; suitable existing materials are preserved. Only behavior beyond
RGBA/default appearance or an explicit Graph request is selected with
`generation="generate"`. Optional agent-added roughness/metallic polish must not turn
ordinary colored surfaces into mandatory Graph work.

After creating geometry, assembly submits `candidate.inventory.shaderGraphTasks`:

```json
[
  {
    "id": "GlassClear",
    "materialName": "GlassClear",
    "description": "Transparent pale cyan glass; the castle remains visible from outside with restrained edge highlights.",
    "targetEntityPaths": ["/Castle/GlassGlobe"]
  }
]
```

Paths in this example illustrate the form; use actual observed surface paths.
Copy each selected SceneSpec material's `id` and complete description. Split actual
surface targets within broad subjects, such as Palace walls versus roofs.
One fresh ACP Agent receives only these tasks. No scene objective, subject catalog,
all-material correspondence table or cleanup scope is sent. An absent or empty
list skips production; `auto`, omitted generation and `preserve` entries stay out.

The parent accepts optional `material.backend` / `material.timeoutMs`; a configured
particle backend is reused by default. Supply the current verified ACP host when
`configure-scene-materials` requests it. No second specification Agent is launched.
The complete serialized task is bounded to 64 KiB UTF-8. Oversized inputs report
not-started before dispatch; requirements are never truncated or paged through
native host-file reads.

For material and particle backend configuration, keep model and reasoning effort separate:
`{"host":"codex","model":"gpt-6.1-sol","reasoningEffort":"high"}`.
The optional `reasoningEffort` must be supported and confirmed by the execution session;
omit it to retain the Host's default. Do not copy a composite standard ACP model label such as
`gpt-6.1-sol[high]` into `model`. Generic Workflow CLI selection uses the corresponding
`--agent-model gpt-6.1-sol --agent-reasoning-effort high` flags.

## Resolve and author

Preserve the existing environment and background during material authoring and previews.
Follow the [Editor Skill's HDRI restriction](../SKILL.md#lighting-and-effects);
material appearance or reflection checks do not authorize adding or replacing HDRI.

1. Verify the exact target scene in the authorized GUI session. Use the mounted
   native Editor MCP tools and their advertised schemas. Inspect brief topic
   documentation once per capability and cache unchanged discoveries.
2. Inspect the supplied target entity paths through bounded live scene queries. Use summaries,
   depth limits and projected fields; every observation stays within the supplied
   `maxObservationBytes` (4096 bytes). Preserve geometry, hierarchy, transforms,
   lights and unrelated or suitable existing materials. Missing targets
   receive an explained task failure; never guess targets.
3. Resolve actual bindings, authoring profiles and mesh slots/subsets when applicable.
   Use `ensure_material_authoring_target` if needed, then resolve again. Choose
   `apply_material_intent`, supported presets, `set_material_properties` or custom
   USDA for Shader Graph based on the requirement and verified capability. Reuse a
   suitable Graph when available. Compatible tasks may share
   a material, and one task may require multiple materials.
   For image-backed materials, follow the built-in SGS image-texture procedure
   described below before texture binding and preview.
4. Preview, settle compilation, inspect the actual result, commit and bind to the
   supplied targets. Verify actual material identity and bound count. Save the exact
   target scene and verify persistence. Default-material deduplication, orphan deletion
   and global material inventory cleanup are not part of this node.

For default PBR, current primitive authoring supports RGBA through `Entity.set_color`.
Alpha alone does not prove transparent blending; RGB alone does not prove emission.
Preserve suitable existing appearance. Required behavior beyond supported PBR needs
verified Graph execution; optional unavailable controls retain defaults.

## SGS image textures

The material worker compiles its built-in material Skill and sends it as ACP `skillText`.
That Skill owns catalog-selected SGS image generation, task query/download, credential and
credit boundaries, texture inspection/binding and failure handling. The child needs no
installed `pico-sgs-cli` Skill or external instruction file.

Generate images only for selected materials needing new textures; suitable existing textures,
ordinary RGBA and procedural Graphs need no image task. Explained texture failures remain
material warnings, preserve successful work and do not stop the parent scene workflow.
Report unresolved SGS task IDs/statuses in the affected material's `reason`;
`taskIds` remain material semantic IDs and `imagePaths` remain observed preview evidence.
Agent cleanup, scene identity and baseline-node presence remain safety checks;
matched-node snapshot differences follow the advisory acceptance rules below.

For independent native repair, the main Agent may use `pico-sgs-cli` for the same image-only
work. Do not apply the material repair budget to repeated paid generation submissions.

## Graph and persistence evidence

Inspect only the relevant supported node definitions, ports and connection types.
Templates and exported graphs are starting points; validate the normalized candidate
again after any rewrite. Do not carry stale ports or dangling surface connections.
For example, if the current `ND_UsdPreviewSurface_surfaceshader` definition exposes
`opacity`, use that input rather than an obsolete `diffuseOpacity`; do not rename
ports across unrelated shader types.

Material-local motion requires a connected Time node dependency reaching the actual
surface output. For flow, verify supported coordinate operations with nonzero speed.
An unused Time node, moving unrelated color or a static preview alone does not verify
flow. For transparency, verify supported blend/depth/culling settings and connected
opacity, then inspect an exterior preview with background or interior content visible
through the surface. Hidden surfaces and interior-only views are insufficient.

Use preview/export/commit results and a bounded saved-state reread to verify
persistence. The exact native tool response determines the file actually committed;
do not assume a successful preview or a template path proves the saved binding.
Prefer save → `se.scene.reload(...)` → inspect within the authorized editing window.
Use `discard_unsaved=False` and, when a verified expected disk digest is available,
`expected_disk_digest`. Require reload `status: "ok"`, then verify the active scene,
material bindings and actual image. `open()` returning `was_loaded: true` reused
loaded state; it is not independent disk verification or a reason to restart Editor.
Look for the scene reload API even when it is absent from the tool list; do not
infer restart is necessary from incomplete discovery. Restart only for an evidenced
process fault or explicitly requested process-restart verification, through the
owning lifecycle. Ordinary packaging continues without restart.
Keep successful work when another task fails. Capture only images needed for concrete
appearance questions and record those paths in the report.

## Retry failed tasks

For each failed semantic task, make up to three total attempts within the same Agent
session: the initial attempt, a correction based on the observed error, and a supported
alternative or further repair. Inspect actual state before retrying, retain successful
work and retry only the failed part. Do not duplicate materials or bindings, restart
the entire workflow or request per-task human approval.

After the third unsuccessful attempt, report `status: failed`, `attempts: 3` and a
compact reason including observed errors and remedies; continue independent tasks.
The absolute finalization deadline, cancellation and denied permissions still apply.
If these prevent further safe attempts, report the actual count and concrete reason;
never fabricate retries or repeat denied operations outside the sandbox.

## Finalization and report

Runtime supplies absolute `reportBy` and `finalizationStartsAt` after mount
preparation. Reserve up to three minutes (20% for smaller budgets) for settling,
saving and reporting. Read the clock before each phase or batch. At
`finalizationStartsAt`, stop discovery and authoring, settle previews, save and return
the report. Respect `maxPersistenceReopens`; do not restart unchanged audits.
Permission failures are concrete limitations, not permission to request elevated
sandbox access or retry outside the sandbox.

End with one standalone JSON object matching Runtime's supplied `outputSchema`.
Every `materials[].status` must be exactly `"succeeded"` or `"failed"`; do not return
`"success"`, `"failure"`, `"pass"` or `"completed"`. Check field names, enum literals,
task coverage and required evidence before ending the turn:

```json
{
  "scenePath": "Sources/Scenes/Main.usda",
  "previewsSettled": true,
  "saved": true,
  "materials": [
    {
      "name": "Flowing water surface",
      "taskIds": ["Water"],
      "status": "succeeded",
      "materialPath": "Sources/Materials/Water.usda",
      "boundCount": 3
    }
  ]
}
```

Every requested semantic task ID must appear in at least one outcome. Each success
needs an observed material identity and positive actual bound count; each failure
needs a reason and actual `attempts` count (0–3). Names and counts describe implementation results and do not have to
match task IDs or subject counts. Outcome names must be unique. `imagePaths` is optional. Individual explained
failures are warnings in `materialProduction.warnings` and do not block progression.
The Agent-report ingestion boundary normalizes the known `"success"` spelling to
`"succeeded"` before canonical validation; this does not establish material identity,
bindings, previews or persistence. Stored reports retain the canonical status words.

Execution interruption, invalid/missing reports and unconfirmed save/preview results
also produce warnings after Agent process cleanup is confirmed. Runtime observes the
actual current scene, verifies scene identity and baseline-node presence, and updates the scene fingerprint
before opening particle writes. Its warning receipt references that scene observation
and does not claim saving, settled previews or successful material work. Keep actual
`saved` / `previewsSettled` values truthful, including false on finalization failure.
Incomplete retry evidence is recorded as a warning, without inventing attempts.

Matched-node name, parent path, type, state and transform snapshot differences produce
one `EDITOR_MATERIAL_SCENE_SNAPSHOT_CHANGED` warning. Runtime retains successful material
outcomes and continues; final seven-view review assesses appearance. The warning references
before/after observations, the changed-node count and at most eight nodes with changed fields.
Production allows at most 256 task warnings plus this one aggregate scene warning.
Confirmed safety failures are persisted and replayed without repeated polling/inspection.
Unclassified transport or observation exceptions remain eligible for reconciliation.

An unconfirmed previous writer, lost scene ownership, different scene or missing baseline
node still prevents subsequent writes. A pre-dispatch skip verifies the original scene
identity and baseline-node presence, records snapshot/fingerprint differences as warnings,
and does not claim saving or previews. Historical cleanup metadata remains readable in old
receipts but is not current work.
