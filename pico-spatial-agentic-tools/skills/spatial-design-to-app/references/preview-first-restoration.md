# Restore Preview-first designs

Applies to write-spec-draft-1. Read the accepted Spec and the Designer's `design/design-reference/`, not its legacy references or bundle. Keep the accepted files immutable. Reuse the existing scaffold, Editor and validation workflows; do not add a workflow node.

## Resources and behavior

Plan uses placeholders and records requirements. During Compose, a model marked to-create must be produced using the Spatial Editor authoring path before integration. Follow the execution choice in the parent Skill; preserve the required handoff regardless of how it was produced. Reuse suitable existing resources; send explicit modification requirements to Editor when necessary. Preserve the Editor handoff and implement App-owned controls after delivery. Read all designNotes, including appearance, behaviors, previewLimitations, relationship and followBehavior. A behavior omitted from Web simulation is still required in App. Do not substitute the placeholder SVG for a model.

Extend `.scratch/design_implementation_map.json` with `model_deliveries`, keyed by model node ID. Each entry contains nonempty `resourcePaths` (project-relative actual model/bundle/scene or supported authored-content result files). Pending models also require `authoringResultPath`, the persisted Editor handoff. Do not rewrite assetStatus in the frozen Spec. The gate checks existence, not model quality; inspect actual loading/integration source and the Editor result during source review.

The implementation contract now preserves purpose, designNotes, parts, visualStates, regions and textBehavior, and actions[].purpose. In source_mappings, cover each `behavior:<node-id>:<zero-based-index>` as well as node/action IDs. Cite the actual behavior implementation symbols and evidence. Copying design prose into comments is not implementation proof; source review must confirm the action target and wiring. No screenshot is required.

## Image and icon sources

Resolve `assets[].src` relative to the accepted Spec and preserve the source
file's format and contents when packaging it. Copy file-backed SVGs into
`app/src/main/assets/` and load their packaged asset URI through Coil with SVG
support. Do not preconvert an accepted SVG into PNG or VectorDrawable, use
`qlmanage` or another thumbnail export, or redraw an approximate icon.

Add matching Coil Compose and SVG dependencies and register `SvgDecoder.Factory()`
on the app's shared `ImageLoader`. Load SVG artwork with `AsyncImage`; for a
monochrome icon slot, supply `rememberAsyncImagePainter` to SpatialUI `Icon` so
the component retains its theme tint. Preserve multicolor artwork through an
image component without monochrome tint. Restore accepted dimensions, fit,
alignment and clipping in Compose rather than baking them into a new image.

PNG and other bitmap sources retain their original format and use normal image
loading through Coil or existing local `painterResource` calls. Existing SDK
icons and accepted Android vector XML remain on their native loading path;
Figma `icon70://` assets may reuse the referenced bundled Android vector.

During `compose_review`, trace each `asset:<id>` from its accepted source to
the actual packaged file and loading call, including SVG decoder registration.
Verify that copied source files are unchanged, bitmap sources were not replaced
by thumbnails, and monochrome tint does not overwrite multicolor artwork. A
generic screen-function mapping or a clean build does not prove resource
fidelity. Keep unresolved loading or rendering findings explicit; source
inspection alone does not establish runtime rendering.

## Surfaces

Volume widths/heights/depths are dp. Do not recreate sui-volume's background, wireframe or label in App. For the first deterministic Kotlin adapter, map the surface to the actual source and use this explicit public SDK form (replace example dimensions):

```kotlin
// design-style: volume-container character-volume
WindowContainer(
    form = Form.Volumetric,
    defaultSize = WindowContainerSize(width = 900.dp, height = 600.dp, depth = 400.dp),
) {
    // Scene content
}
```

This marker identifies the container, not a child Box or resize constraints. The gate checks named literal dp values in this call. Dynamic expressions, other APIs and multiple/ambiguous configurations are not proven by the adapter; extend the adapter with grounded tests rather than changing the design or claiming success. This checks source configuration, not runtime depth or later mutations.

AttachmentPanel remains transparent unless Spec explicitly declares props.background=material. For that panel's content root only, use a clipped Regular glass modifier and place `// design-style: attachment-material <panel-id>` immediately before its modifier chain (within three preceding lines of backgroundMaterial). Use `.backgroundMaterial(enable = true, style = Material.Regular)`. R10 requires exactly one marked material call per declared glass panel and still rejects unapproved material elsewhere. Source review must confirm that the marked call is actually on that panel's content root, not a descendant or unrelated container. Transparent panels receive no glass. Preserve scene ownership and follow behavior.

For content backgrounds, R10 accepts content nodes and their visualStates, and declared domain_visual parts. Keep existing design-surface/design-part trace markers. The exception for glass does not authorize arbitrary material fields or nested backgrounds.

## Components and admission

Follow the new reference's explicit settings. Title-only bars use CenterInBar; title plus subtitle, actions or search use Center unless explicitly overridden. Preserve declared primary-title weight, icon names/assets and explicit tints. Use spatialHoverEffect for custom clickable areas; do not duplicate hover already supplied by standard controls such as ListItem. Do not change accepted defaults merely to satisfy legacy prose.

For the complete standalone UI workflow only, preserve existing outer fields in the design escalation receipt. New pre_gates require designDocComplete=true, designSpecValid=true, previewMatchesSpec=true, critiqueVerdict=pass and consistencyReviewVerdict=pass. Do not fabricate postBuildVerdict for the new flow.

Run validate_workflow_and_build.sh for the complete standalone UI workflow. A scoped dev assignment applies the relevant build, architecture, unit-test, launch and style checks without manufacturing escalation receipts or invoking the full aggregator. Final compose_review checks actual source/resource wiring and all explicit design requirements against clean machine results; it does not request screenshots. Retain unsupported or unverified claims explicitly; never present source token coverage as runtime validation.
