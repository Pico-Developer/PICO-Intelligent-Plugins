# Particle Effects After Scene Specification

For managed execution, particle-only and mixed scene requests use the public Editor Run through
`start_editor_workflow`. First submit its `author-scene-spec` Handoff. Declare every
particle requirement in SceneSpec `effects` with `kind="particle"`, stable `id`,
and `description`, plus subject references or placement intent when relevant.
Use `acceptanceIds` to associate particle-only acceptance criteria with that effect;
this lets a recorded particle failure remain a visible gap without blocking the
rest of the scene. Detailed emitter parameters belong to the particle spec Agent.

## Managed Particle Preparation

After SceneSpec, the `produce-particles` module prepares all declared particles
after base scene assembly and saving, before final review capture. `produce-materials`
first authors and binds the submitted table. Particle production uses that material-complete
target scene, preserves its geometry, transforms and materials, and shares
the managed GUI Editor session. Scenes without particles retain their
ordinary production flow and mode.

The module uses one pair of fresh Agents for the full batch:

1. The specification Agent writes one Markdown document for all declared effects.
   It mounts no Editor MCP and derives layers, timing, motion, space, color,
   constraints, assumptions and acceptance criteria from the SceneSpec needs.
2. The production Agent receives that complete spec, mounts the existing native
   Editor MCP for the managed GUI instance, creates each effect beneath a distinct
   root in the prepared scene, inspects referenced subjects and their actual bounds
   for placement and scene-relative acceptance, observes playback, and explicitly saves the scene.

Keep the selected `particle_backend` host/model configuration. If the Run requests
backend configuration, submit the current Handoff using its live schema. A missing
backend is a configuration task; it does not authorize installing another bridge
or switching hosts. Follow root `next` waits and continuation arguments. The public
root remains the scene task's identity; an internal particle Run is preparation,
not the final scene delivery.

The Editor service owns particle Agents and control resources in an independent
runner process. Follow root waits while it runs; a Workflow Worker restart resumes
observation of the same batch. If a particle Agent cannot complete and the service
offers caller takeover, the Editor service cancels/releases that batch, retains
available outcomes and records missing effects. Final scene validation continues after
resource cleanup is confirmed. Follow root waits during normal cleanup. If
cancellation cannot confirm cleanup within ten seconds or runner ownership is
lost, the batch is blocked and the root reports the non-retryable
`EDITOR_PARTICLE_CLEANUP_UNCONFIRMED` error. Follow the reported recovery action;
automatic recovery is not promised. It does not publish a caller takeover. The
backend configuration Handoff above occurs before the runner starts.

Specification defaults to five minutes. Production defaults to twenty minutes and
five rounds. Optional `particle_budgets` fields `specMs`, `productionMs` and
`maxRounds` retain the existing bounded particle loop.

## Native Production And Reports

The production Agent performs this loop; integrated callers follow root waits.
Discover the native Editor tools and read their actual documentation before a new
kind of operation. The native MCP owns particle parameters, playback, screenshots
and explicit saving; the particle controller owns stages, rounds and reports.

1. Admit a round through the currently returned particle control task before
   modifying effects. A direct caller takeover with `roundOpen=true` finishes that
   existing round before requesting another.
2. Edit the prepared target scene through native tools. Keep unrelated content and
   report each declared SceneSpec effect ID against its own root node path.
3. Capture and inspect native frames as needed to assess shape, motion and
   dissipation against the particle spec, with no fixed screenshot count. Tool
   latency and imprecise capture timing can miss launch, burst or dissipation,
   or sample similar phases. Continue playback and capture more images within
   the remaining budget; replay playback only when native tools support it.
   Do not assume exact timestamps, precise seek or deterministic replay. A missed
   phase alone does not establish effect failure; report any remaining evidence
   gap. A successful call or image path alone does not establish acceptance.
4. Explicitly save and inspect the native save result. Submit `report` with the admitted `round`,
   scene/root paths, observed `imagePaths` without a fixed count, `save: {status, evidence?}`,
   `review: {items, summary}`, and per-effect outcomes using the current schema.
5. Unmet items may use another admitted round with fresh visual evidence while budget remains. Preserve
   successful effects when another effect cannot complete. Report every missing
   effect ID and reason when progress stops.

Reports carry `source="agent_reported"`: the controller validates report structure
and budgets, not image pixels, native task completion or saved-scene contents.
Passing effects require distinct observed image references supporting their review.
Distinguish observed results from assumptions and record unavailable evidence.
Retain the observed saved, unsaved or unknown state when production stops.

## Final Scene Validation And Delivery

`particleProduction.effects` hands off each declared effect as `succeeded` with
its root/scene path, or `failed` with a reason. Preserve successful roots already
placed against the assembled scene in the same GUI session. Particle effects
are prepared content rather than generic enhancements to recreate.
Caller writes and final capture are closed during production. Before final capture,
the Workflow verifies retained base nodes and successful effect roots, records missing
effects, and freezes the updated scene fingerprint for review and delivery.

Every failed particle remains missing, including effects marked `required`.
The Workflow carries these gaps into `unsupportedWork`; the Workflow does not
retry them automatically. Review the remaining scene normally and retain particle
gaps through final delivery instead of failing again on their linked particle-only
criteria. The final report lists every missing particle and its reason alongside
successful node paths. The public scene Run continues through its package gates.
This handoff uses same-scene nodes; it does not export a reusable particle template.

Cancel the public root through `cancel_editor_workflow` when requested and stop
native authoring calls. Cancellation does not prove native asynchronous work ended
or scene changes rolled back. Preserve visible GUI work and retained artifacts.

## Direct Particle Compatibility

Existing direct callers retain `start_particle_workflow`,
`get_particle_workflow_status`, `resume_particle_workflow`, `begin_particle_round`
and `cancel_particle_workflow`. These use an unprefixed `particleRunId`, native
`request`/`projectPath`/`backend`/`targetScene`/`budgets` fields, and stage tokens.
Their standalone delivery remains a saved scene. Existing `editor-particle:<id>`
identities also remain observable and resumable through the unified facade.

For a direct stage task, use the returned schema and `input.token` rather than a
scene revision. Direct production takeover may request `ensure_editor_ready` with
`open_gui=true`; compare its result with the retained Editor target. These entries
share the existing particle service and occupancy state. Observe or resume the
current Run rather than starting a duplicate. Use the SceneSpec-first path above
only when managed execution has been selected.

### Direct Caller Takeover And Recovery

Only the direct/legacy particle lifecycle forwards caller takeover. Follow a
returned takeover task using its current token and stage instructions; consumed
budgets and rounds remain effective. For specification, submit one Markdown
document with stable acceptance IDs such as `[A1]`. Ordinary missing details become
explicit assumptions; essential direction may require clarification.

For production takeover, use the returned target and existing GUI instance.
Inspect the current scene and native asynchronous tasks before repeating uncertain
work. Explain target mismatch or unresolved native work in the report. Keep
successful nodes and available reports when a stage fails.
