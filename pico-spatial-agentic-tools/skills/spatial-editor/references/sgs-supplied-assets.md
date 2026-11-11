# SGS Supplied Assets

In pico-cli, new model generation uses SGS CLI first. Pass root `assetSupply` (or facade
`asset_supply`) with an explicit user-authorized `maxSubmissions` budget. Do not start an
Editor-only generated-model path because the policy is absent; request the missing budget instead.
Use `fallbackPolicy="forbid"` when SGS CLI is required. `fallbackPolicy="editor"` allows the
Editor fallback only after the managed supply module proves the CLI unavailable before generation
starts and there is no task or unresolved submission for that subject. Auth, quota, permission,
Catalog mismatch, temporary contention, cloud-task failure, and import failure are not fallback
conditions. Do not replace a requested model with primitives or SVG after failure.

For managed model supply, use `start_3d_generation_workflow` with root input
`spatialcraft.spatial-3d-generation-input/v2`, an explicit `assetSupply` policy (`provider`,
`maxSubmissions`, and `fallbackPolicy`), and the Editor backend. Read current package versions and
schemas from the runtime; the integrated Editor package uses the v7 authoring contract. `inputs` use `provider="pico-sgs"` and identify text-to-3D, image-to-3D,
or existing-source reuse by `subjectId`. SceneSpec preserves those IDs, while orchestration owns
model instance counts. The managed supply module creates and downloads SGS tasks; do not create
the same task separately through the CLI. It persists proven-unavailable fallback decisions;
resuming does not retry those models through CLI after repair.

Do not retry an unknown submission or convert it to fallback generation. Import each source model
into Editor and complete six-axis screenshots, metadata, and review before scene orchestration.
This phase supports only self-contained GLB handoff. If a source-model review fails, report it and
require the caller to start a new supply Run explicitly. Do not use a revision prompt to resubmit
the cloud task automatically or replace it with Editor generation.

Continue through the root response's `next.tool` and `next.arguments`. Requests with no newly
generated models do not need a supply policy. Use the standalone `pico-sgs-cli` Skill for text-to-image and
image-to-image requests; this phase does not deliver an image directly as a model.
