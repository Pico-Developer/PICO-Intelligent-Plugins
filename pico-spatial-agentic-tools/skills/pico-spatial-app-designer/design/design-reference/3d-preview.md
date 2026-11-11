# 3D Preview authoring

Read this during Plan when the design contains models or scene attachments. A Web Preview may use HTML/SVG placeholders instead of real 3D assets. It must identify what should become 3D and preserve confirmed requirements that the picture cannot express.

## Compose the page

Load the shared runtime as described in [runtime](runtime/README.md). Give each model and panel a stable unique ID:

```html
<div id="character-model"><!-- Simplified character graphic --></div>
<sui-attachment-panel id="character-info-panel" background="material">
  <!-- Character information and actions -->
</sui-attachment-panel>
```

Do not infer native spatial parenting from this HTML. AttachmentPanel belongs inside the intended SpatialView scene; ordinary window content and Subwindow remain other choices. Explicit glass is recommended for information/action panels, while transparent labels remain possible. See [AttachmentPanel](components/AttachmentPanel/README.md).

## Preserve the design that cannot be drawn

Place one non-visible JSON block in the Preview. Keys must match element IDs. This is design metadata, not a renderer or a complete embedded Spec:

```html
<script type="application/json" id="scene-design-notes">
{
  "character-model": {
    "represents": "3D character model",
    "previewRepresentation": "Simplified placeholder; blue jacket is confirmed, facial details are not specified",
    "assetStatus": "to-create",
    "appearance": ["Stylized character wearing a blue jacket"],
    "behaviors": ["Rotate around the vertical axis", "Wave when Greet is activated"],
    "previewLimitations": ["Waving is not simulated; rotation only transforms the flat placeholder"]
  },
  "character-info-panel": {
    "relationship": "Inside the character scene, to the right of the character; exact scene distance is not yet specified",
    "followBehavior": "Remain stationary when the character rotates"
  }
}
</script>
```

For models, require nonempty `represents`, `previewRepresentation` and `assetStatus` (`to-create` or `available`). Optional `appearance`, `behaviors`, and `previewLimitations` are arrays of nonempty strings. Available resources additionally use `assetId`, which Write Spec resolves in `assets`; never invent a path for pending content. For attachments, require nonempty `relationship` and `followBehavior`. Write all descriptions in English. Escape `<` as `\u003c` if it occurs in JSON strings embedded in HTML.

Distinguish a pure placeholder (appearance still unspecified) from a simplified depiction of confirmed appearance. Only promise approved abilities; waving is an example, not a required model feature. Unknown details stay unknown. Existing delivered resources remain authoritative. Do not fabricate bones, animation controllers, dimensions or spatial coordinates to fill the record.

Keep notes aligned with visible layout and interaction code. Implement feasible Preview interactions; explicitly list omitted/simulated behavior. Do not display metadata as product copy. A separate example caption may explain its limitations.

## Write Spec from both sources

Reuse each ID. Models become `domain_visual` with a stable `rendererKey` and a purpose explicitly identifying 3D intent. Copy each notes entry unchanged into that node's `designNotes`, then record actions/bindings where appropriate. This small descriptive field preserves requirements without creating another model node format. Attachment notes go on the corresponding component node; background goes in its supported props.

A screen region's dp dimensions do not define model size in meters. SVG circles and CSS rounding do not define native geometry. Web highlighting does not imply a scene displacement. Preserve actual spatial units and reference frames only when confirmed.

Use the [complete character example](../spec-writing-reference/character-example/README.md) to see both outputs. Matching metadata demonstrates preservation, not that native geometry, animation or follow behavior has been implemented.

## Volume boundaries and dimensions

Inherit the container selected in Frame/Explore. For Volume, use [the shared `sui-volume` shell](runtime/README.md#volume-preview-boundary); do not hand-draw a separate boundary per page. Set width, height and depth explicitly in dp. Fill in dimensions that remain undecided during Plan and update the design record; do not silently switch the container type.

Its faint background, inset spatial outline and dimension caption identify the bounds. These are preview-only aids; the AttachmentPanel's explicitly selected glass is an actual design requirement. The shell renders width/height at 1dp = 1 CSS px. Its wireframe is schematic and does not encode a measurable physical depth. Do not maintain a second independent set of Web dimensions or convert these values to meters in Preview.

Map shell ID to surface ID and place application content under rootNodeId. Copy the three dimensions to surface.defaultSize with unit dp. Keep shell decoration out of the node tree. Internal content nodes may retain their own layout sizes; those describe content, not an alternate Volume size.
