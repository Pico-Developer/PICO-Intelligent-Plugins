# Authoring Quality And Efficient Evidence

Read the applicable section before authoring detailed requirements, selecting a
container, or starting a capture batch. Both paths use the authoring and verification
methods below. Direct work uses documented native Editor tools and evidence scoped
to the task. Handoffs, candidate submissions, receipts and Workflow Gates apply
only inside a managed Run. Follow the live schema for the path in use.

## Managed Scene Specification Counts

Before the first `author-scene-spec` submission, read the subject count range and
subject-array limit from the live schema. Split counts above the per-subject limit
into distinct subject IDs and non-overlapping placement ranges. Keep each count
within the allowed range and verify that the split counts sum to the requested total.
Update material `subjectIds` and composition references to cover every new subject.
Recompute each split total and the scene's geometry total; geometry-free groups
contribute no Primitive count. Keep the accepted descriptions, materials and layout.
Validate the full input against `next.submission.inputSchema` before calling Resume.
These are specification limits; execution batches follow their own tool limits.

## Requirements And Evidence Coverage

At authoring entry, map each explicit requirement to its source, target entities,
verification method and current result. In a managed Run, keep the accepted
`sourceContract` and existing criterion IDs, and revisit the mapping before submitting
the candidate.

- Verify counts, dimensions, widths and grounding with documented scene/entity
  queries and measurements. A whole-scene image cannot establish an exact width.
- Verify appearance, openings, contacts and route continuity with useful views;
  combine measurements and multiple views when the requirement needs both.
- In a managed Run, compare the mapping with the projected criteria. If only
  `editor_delivery_completed` is present, report the uncovered requirements as a
  projection limitation and still check them against the source request. Package
  readiness alone does not establish their acceptance.
- For direct work, capture only the relevant views needed to verify the change.
  Save and verify the actual scene or deliverable using those views and measurements.
- In a managed Run, finish scripts, binding edits and saves before freezing the
  candidate. Keep the seven required whole-scene views. Default extra local/detail screenshots: zero.
  Add them only for unresolved requirements; they count as formal evidence only when supplied
  by the live review input. Use its existing labels, criteria and fields.
- An unsatisfied or unproven mandatory requirement blocks your passing judgment.
  Use applicable findings to return it to its owner. If the live contract cannot
  express the needed evidence or correction, report that limitation rather than
  repeatedly recapturing an unchanged scene or claiming full coverage.

## Unified Scene Authoring

Generation/import/review only adds prerequisites. After assets pass, models and
primitives use one arrangement recipe, followed by conditional material work and final review.
Use bounded scripts that mix instances, primitives, transforms and
enhancements in dependency order. There is no mandatory primitive-first or
model-first stage, or routine detail-capture stage.

### Formal Lighting

Apply the [Editor Skill's HDRI restriction](../SKILL.md#lighting-and-effects).
Preserve the existing environment/background; lighting benchmarks do not authorize HDRI.

Spatial Editor 6.2.3 provides deterministic lighting through `execute_script`.
Do not require a dedicated lighting MCP tool. Query `get_spatial_editor_docs` in
the current Editor session (through the gateway for a managed Run) with
`topic="lighting"`, `query="Entity.configure_light"` and `detail="brief"`; expand
to full only when the signature is missing.

Create `DirectionalLight`, `PointLight` or `SpotLight` with documented
`se.scene.create_entity(type, name, parent)`. Configure through `Entity.configure_light`;
use `Entity.aim_at` for world-space direction. Directional and spot lights emit along
local `-Z`; point lights have no direction or shadows. Directional intensity uses lux,
point/spot intensity uses lumen. Project starting benchmarks for `DirectionalLight`:
sunlight about 1200 lux and high-intensity lighting about 1500 lux; values above 1500 lux
may degrade the authored result. For `PointLight` and `SpotLight`, artificial lighting is
about 6000 lumen, high-intensity lighting about 15000 lumen and dim-scene lighting about
2000 lumen. User-specified intensity takes priority. Adjust for intent, light count,
distance, attenuation, spot angle and exposure; avoid excessive combined brightness. These
are advisory values, not fixed defaults or gates, and the units are not physically equivalent.
Dim-scene lighting does not imply `environment` kind or an HDRI parameter.

Save and check `Entity.info().light.type` for the actual light component; `Entity.get_light()`
may inspect parameters. `get_scene_info` can project formal lights as `Xform`, so its entity
type is not a lighting verdict. Lighting acceptance checks existence only, with no lighting
screenshot or illumination review. In a managed Run, the seven views still review
the rest of the scene.
An enhancement ID, an emissive material or a decorative cube does not prove formal lighting.
Missing required lights must return to authoring.

### Arrangement Recipe

1. Read the current task requirements and inspect the workspace; use the verified
   reuse recipe below. If a managed Handoff supplies verified script signatures,
   query only APIs outside that list. Obtain the current process token once.
   Reuse verified signatures and the receiving process's token. Do not probe aliases
   such as `se.scene.find`, `se.scene.entity`, `se.get_entity`, `Entity.duplicate`
   or `Entity.set_name`.
   Empty groups use `create_entity` with type `Xform`, not `Entity`.
   Query `Entity.children` or top-level `se.get_entity_children` for child enumeration;
   `se.scene.get_entity_children` is not supported.
2. Use the verified project-relative `Sources/...` asset path. In a managed Run,
   pass the Handoff `editorAssetPath` unchanged. Reuse the accepted imported
   entity as the first formal instance: rename, reparent, place and bind its final
   path. `importedEntityPath` is a lookup hint; if stale or outside the selected
   scene, inspect live formal instances before importing. Create only missing
   occurrences up to `count`: `count-1` when reusing one, `count` when none exist.
   For `count=1`, reuse needs no additional import. Do not retain hidden prototypes
   or create PrototypeCache by default; keep USDZ files and acceptance records for
   recovery. A canary is conditional on an unverified import, orientation or scale contract.
3. Import with `se.scene.instantiate_asset_and_wait`; it returns the Entity. To
   overlap imports, use `instantiate_asset_async`, then `wait_import_task` until
   `status="completed"`, then `se.scene.get_entity(entityPath)` before rename,
   transform or binding. Do not treat a task ID/path string as an Entity.
4. Preserve imported rotation. Do not apply the importer's axis correction again.
   Verify bounds, grounding and semantic front; reuse the validated mapping.
5. Keep scripts below 10,000 characters; split only for size or async dependencies.
   Return `{instanceId, entityPath}` records. The reflected `add_asset_to_scene`
   remains suitable for individual operations; it does not define a model-only route.
   For managed operations, poll pending receipts by identical replay or workspace
   reads. For direct imports, use the native task status. Wait for completion before
   the next write or capture; do not resubmit creation.
6. After failure, inspect unique intended names and repair only missing work.
   Never replay the whole batch. Complete all formal instances and enhancements.
7. Remove leftover temporary prototypes, canaries, duplicate imports and their empty
   staging containers with the documented operations for the current path. Preserve
   verified instances and user-required content. Flush, verify deleted entities no
   longer exist, check bindings and counts, then save. In a managed Run, reread the
   fingerprint and submit the complete
   candidate inventory after cleanup. `active=false` or `visibility=invisible` is not deletion.

### Reusing An Imported Entity

For the `spatial_editor` Runtime CPython wrapper, `se.Entity(path)` wraps an existing
path; it does not create or import an entity. `entity.info()` validates that path and
returns its current scene facts. Do not search for an invented lookup alias or use
the separate `spatial.editor` plugin SDK as this wrapper's API contract.

Use this verified sequence for the first formal instance:

1. Verify the active scene and exact imported path with the managed workspace or
   `get_entity_info`. Use the returned path, not a root derived from the scene name.
2. Wrap the entity and intended parent using `se.Entity(verified_path)`; call
   `info()` on both before writes. Create only missing hierarchy groups as `Xform`.
3. Call `entity.rename(final_name)`, then `entity.reparent(parent_entity)`, checking
   each boolean result. For a scene-root parent use `entity.reparent_to_root()`.
4. Both successful operations update `entity.path`; retain the same wrapper and
   use its updated path for later calls and candidate bindings. Discard old paths.
5. Set the final transform after reparenting; verify parent, world bounds and
   placement with `entity.info()`. Preserve the reviewed imported orientation.

For script authorization, query `get_spatial_editor_docs` in the current Editor session with
`query="Entity.info"`, `topic="scene"`, `detail="brief"` once for the current
`auth_token`. The Handoff list and this recipe are verified signatures; do not
re-query them, and reuse them if the filtered block omits `Entity(path)`.
The returned `auth_token` is a process-local documentation acknowledgment issued
by the current Editor MCP service and checked before script execution. It is not
a PICO account login, SGS service credential, or authorization for another service.
Keep the existing flow: read task-specific docs, then pass the exact returned token
to `execute_script` through the same Editor backend. Use the managed gateway when
the Run owns writes. A restarted backend
requires a fresh documentation read; never invent a token or omit the parameter.
Do not print the token, save it in project files, or forward it to other services.
If Host approval flags this documented round trip as credential disclosure, explain
its issuer, purpose, and same-backend destination and request scoped user approval
for the current task. A description of the token does not override a Host denial;
retain the Run and report the blocker if approval is unavailable.

Do not use a generic `execute_script` query to discover the assembly API.
If the running version explicitly rejects this contract, stop and report the
version/signature mismatch; do not probe aliases or import another copy.

## PBR During Geometry Creation

Use each primitive's default PBR in the same operation that creates the geometry.
Read appearance requirements from the current task, or the accepted
`authoring.intent.sourceContract` in a managed Run. Apply only
parameters supported by the live default-material API. Read [PBR materials](pbr-materials.md) for current
capability evidence; retain defaults and report unavailable parameters.
RGBA is verified: call `se.Entity(primitive.path).set_color(r,g,b,a)` while creating
each primitive. This changes its existing PBR BaseColor;
the generic `set_material_param` TypeError does not affect this color API.

Preserve unrelated imported slots and retained materials. Change supported appearance in the geometry
script. Do not create sources,
share materials, delete defaults or implement normal-map file operations.
Keep native script output concise and below 16 KiB. After truncation, inspect
existing entities and preserve successfully created geometry.
In a managed Run, candidate acceptance verifies asset counts, ownership and the scene fingerprint.
Report progress every 60 seconds during authoring.

### Host Skill Consistency

Use the maintained Host setup/update or local preview flow to refresh the complete
plugin closure when installed instructions still request separate material submissions.
Repository guidance takes precedence during source development.

## Camera Fit For Scene Evidence

For managed final evidence, the driver projects all eight bounds corners into each camera basis, with a 10% margin,
near/far clip checks and nonparallel up vectors for exact vertical views. Current
explicit-camera offscreen rendering uses vertical FOV 60°, near 0.1 and far 1000.
Use the following calculations for direct or supplemental captures when needed.
Use current bounds and the actual projection, FOV and output aspect ratio.
For perspective capture, let `center=(min+max)/2`, `extent=max-min`,
`radius=length(extent)/2`, and `aspect=width/height`. Convert vertical FOV to radians.

```text
verticalHalfFov = verticalFov / 2
horizontalHalfFov = atan(aspect * tan(verticalHalfFov))
halfFov = min(verticalHalfFov, horizontalHalfFov)
distance = margin * radius / sin(halfFov)
cameraTarget = center
cameraPosition = center + distance * directionTowardCamera
```

A modest fit margin such as 1.05–1.15 is a calculation choice, not a scene dimension
or an extra MCP argument. The sine formula fits a sphere; `radius/tan(halfFov)`
does not account for the sphere's depth.

For tighter framing of an elongated scene, project all eight bounds corners,
relative to `center`, into the desired camera basis. Let `x` be camera-right, `y`
camera-up, and `z` point toward the camera:

```text
distance = max over corners (
  z + margin * abs(x) / tan(horizontalHalfFov),
  z + margin * abs(y) / tan(verticalHalfFov)
)
```

Also keep the nearest corner beyond the actual near clip plane and every corner
within the far clip plane. For orthographic capture, use the documented
orthographic size controls from projected extents rather than perspective FOV.
Check axis direction and a nonparallel camera-up vector. Never guess FOV units,
unsupported `fit_scene`/`margin` arguments, or a camera convention.

For supplemental captures, inspect each requested image and correct excessive empty
space or clipping while preserving its direction. Reuse valid receipts and retake
only invalid views. Driver-owned final capture still requires all six world-axis
views and `front_three_quarter`. Frozen capture permits
only `container_fit_mode="none"` or `"report_only"`, never a fit that mutates content.

## Container And Delivery Scale

Resolve whether requested dimensions apply to authored content, delivered physical
content, or both from the accepted request. Before selecting or changing a
container, read the documented Editor types, size and fit policy. Editor container
types and application runtime types are different vocabularies; do not assume an
SDK `Stage` is a supported Editor container or that `Plane` always preserves scale.

For a bounded container such as `Volume`, compare measured content extents with
the returned `sizeMeters` in all three axes and inspect its automatic-fit policy.
Use explicit meter values and units; device-point dimensions are not meters.
Preserve required absolute delivery dimensions with a documented compatible
configuration. If the requested container and dimensions cannot both be met,
report the conflict before expensive authoring/capture. Do not silently reinterpret
an absolute-size requirement as permission for a miniature.

For direct work, use the documented native container tools available in the
current Editor session. Read back the container settings and measured bounds,
save, and capture the views that verify the requested change. In a managed Run,
change settings only through its authoring operations. Reread bounds and the
fingerprint before capture; frozen review does not authorize container changes
or an unmanaged export.

At delivery, inspect the matching `sourcePath` entry in `scenes[].warnings` as well
as manifest-wide and provenance warnings. Surface `SCENE_AUTO_FIT_SCALED` even when
provenance warnings are empty. Report measured authoring size and the recorded fit
factor; fit warnings or post-export Editor Bounds alone do not prove that Bundle
geometry was resized. Verify Bundle data or runtime measurements before claiming
delivered physical dimensions.

The managed Package Gate checks provenance, byte digests, accepted Gate proof and exported scene
identity. It does not reobserve Editor or prove physical size. Absolute-size acceptance requires its own measurements and source
requirement check. Report any remaining scale conflict prominently with verified
artifact paths. Preserve terminal Runs; do not reopen them or automatically launch
another production Run to repair an already-delivered result.

## Capability Discovery And Compact Consumption

For supported lighting and effects, use the live capability response
and exact documented APIs. Distinguish a demonstrated supported path, explicitly
unavailable capabilities in the current managed environment, and unresolved
support. Missing search results do not establish version-wide non-support.
Check both project saving and bundle persistence before claiming persistent work;
Editor does not generate or register object/timeline animation. Keep material-local
motion in the material requirements and particles in their dedicated workflow.
Use only schema-supported probes. In a managed Run, an authorized static fallback
still needs `required=false` and the actual missing work in `inventory.unsupportedWork`.
Unresolved mandatory work cannot be marked complete on either path.

In a managed Run, read workspace at window entry, before candidate submission, and
after conflicts, failures or uncertain outcomes. Consume each response once and retain required
receipt IDs, current fingerprint and valid evidence. Use narrow documented
`get_entity_info`/`get_scene_info` queries for subsequent facts. Do not add paging
fields to an empty workspace schema, or treat a truncated receipt list as complete.
Read supplied archive references when necessary; report inaccessible required data.

Return a concise user summary with the outputs and evidence required by the task.
Include Gate status for managed delivery and report relevant scale warnings,
unsupported work and unresolved requirements on either path.
Link existing detail artifacts instead of copying every receipt or evidence row.
This reduces repeated consumption and reporting; it does not change the API's
response size or make omitted evidence formally acceptable.
