# AttachmentPanel

A 2D Compose attachment placed in a `SpatialView` scene as an entity. Use it for information or controls attached to a scene group, an object or a part. It does not create a window or supply a glass background automatically.

**Default: transparent. Recommended for information and operation panels: explicitly add a Regular glass backing.** In Web, use `background="material"`; in native Compose, add the material to the attachment content root. This is an explicit design choice, not automatic SDK behavior. Short readable labels may remain transparent.

## Choose the panel

- **Ordinary layout:** place text and controls directly in the window content when they belong to the same layout as the model region. No additional panel or window is required.
- **Subwindow:** optionally put supplementary information or controls in a companion attached beside a Planar or Volume window. Volume does not require this arrangement. See [Subwindow](../Subwindow/README.md#beside-a-volume-window).
- **AttachmentPanel:** place 2D information or controls at a specified location in the `SpatialView` scene, such as a label above a sensor. Specify the scene group/object/part, placement and response to movement, rotation or scaling. It is positioned through the scene's entities, not automatically attached to a Volume window edge.
- A panel placed directly in Stage uses a scene attachment. An independent WindowContainer within Stage can still use its own Subwindow; the owner is that window, not Stage itself.

“Above the object” describes a location, not following behavior. A name label may move with the object; a control panel can belong to the display group and remain stable while the model rotates independently. Neither arrangement automatically faces the viewer.

## Transparent default and recommended background

**SDK default: no automatically added panel background.** The Web helper also stays transparent when `background` is omitted or set to `transparent`.

**Chain recommendation: explicitly add Regular glass for a bounded information or control panel containing multiple lines, grouped information or actions.** This keeps its content readable against the scene. Use a 32dp rounded content root for this workflow. The recommendation is not an SDK default: declare it in Preview and carry the same decision into Spec and App.

A short object label may intentionally remain transparent when it stays readable. Do not force every attachment to become a glass window. A component inside a transparent attachment may still have its own normal fill.

Glass belongs to the panel content root, not each nested layout. Keep inner layout wrappers transparent. `fillLight` on a content block is not a substitute for the panel's material. The scene itself does not acquire a full-window glass background merely because one attachment needs it.

## Composition

- Combine real `sui-icon`, Text, Button and other reference components inside the attachment. Icons describe the object, task or action; do not flatten controls into the scene drawing.
- Choose dimensions and internal padding explicitly. The helper supplies neither a fixed size nor content padding; the examples use their own values.
- Short labels need no TitleBar. A substantial task panel can use a TitleBar and body. Add a leading close/back IconButton only when the panel has that exit; a permanently visible label does not need one.
- Keep frequent controls reachable without obscuring the subject. Use actual action icons and meaningful text. Do not add hover to an informational attachment as if the entire region were clickable; its actionable controls provide their own feedback.

## Web API and usage

`<sui-attachment-panel>` is a Preview helper for the attachment's **2D appearance**. It is not a new native SDK API or a 3D engine.

| Item | Behavior |
| --- | --- |
| `background` | Omitted / `transparent`: no shell fill, blur or shadow. `material`: shared Regular glass simulation with radius 32. |
| Size and position | Caller-owned CSS `width`, `height` and layout/position. No default dimensions or automatic anchoring. |
| Default slot | Caller-owned UI content. No built-in title, footer or close control. |
| `hidden` | Caller-owned visibility. |
| Events | No attachment-specific action event. Listen to the events of its child controls. |

```html
<!-- Transparent label: the object relationship is stated in the design. -->
<sui-attachment-panel id="module-label">
  <span>Module A · Ready</span>
</sui-attachment-panel>

<!-- Explicitly backed information panel; these dimensions are example choices. -->
<sui-attachment-panel id="inspection-panel" background="material" style="width:320px">
  <div style="padding:24px;display:flex;flex-direction:column;gap:16px">
    <sui-text text="Module A" text-style="titleMedium"></sui-text>
    <sui-text text="Temperature: 24 °C" text-style="bodyMedium"></sui-text>
    <sui-button text="Mark inspected"></sui-button>
  </div>
</sui-attachment-panel>
```

The page owns the scene illustration, placement and event handlers. Do not pass a Web `background` attribute to native `AttachmentPanel(...)` or translate CSS pixels into scene meters.

## Native correspondence

The current SDK declares `AttachmentPanel(id, size = null, alignment = UNSPECIFIED, content)` inside `SpatialView(attachments = { ... })`. The content supplies its appearance; `attachments.entity(id)` retrieves the corresponding entity for placement or parenting.

For example, inside an existing `PicoTheme` scope (imports and application content omitted):

```kotlin
SpatialView(
    attachments = {
        AttachmentPanel("inspection") {
            Box(
                modifier = Modifier
                    .size(320.dp, 280.dp)
                    .clip(RoundedCornerShape(32.dp))
                    .backgroundMaterial(enable = true, style = Material.Regular),
            ) {
                InspectionContent() // Application-owned title, information and actions.
            }
        }
    },
    initial = { content, attachments ->
        val displayGroup = Entity()
        content.addEntity(displayGroup)
        attachments.entity("inspection")?.let { panel ->
            panel.components[TransformComponent::class.java]
                ?.setPosition(Vector3(0.4f, 0.2f, -1.0f))
            displayGroup.addChild(panel)
        }
    },
)
```

The position is an example in meters relative to `displayGroup`; it is not derived from the Web layout. Add the model to the appropriate group separately. For an intentionally transparent attachment, omit the material modifier. The 32dp clipping convention comes from this workflow; it is not a mandatory SDK radius. Do not reproduce the Preview shadow/blur as extra native decoration.

## What to record for App

For each panel, record its stable ID, scene/object attachment target, 2D dimensions and content, explicit transparent/Regular-glass choice, chosen radius/padding, spatial placement and units, orientation and move/rotate/scale-following behavior, plus relevant actions and visibility. Keep the panel's glass choice separate from ordinary application `appearance.fill`; browser blur and shadow are approximations, not business content nodes.

For example: “Inspection panel beside the equipment display group; Regular glass, radius 32, content padding 24; rotates neither with the equipment nor its selected part; Mark inspected updates the panel status.” A screen coordinate alone does not describe that relationship. Use the agreed Spec representation; the helper does not add a new JSON schema by itself.

## Preview examples

[Open the preview](preview.html) or read its source for working calls and interaction wiring:

1. **Transparent object label:** a short label parented under `module-label-anchor` on Module A. Move left/right translates the object parent, anchor and label together; Reset restores the initial position. This preview demonstrates translation only, not automatic viewer-facing behavior.
2. **Task information with glass:** a 320px information panel next to the object, an Icon, status and a working inspection action. A documentation-only toggle compares the same panel with the transparent default.
3. **Scene-bound control strip:** explicit glass, a rotate IconButton, Reset Button and a label; the strip stays stable while the subject rotates.

The objects and positions are browser illustrations. They do not validate ECS parenting, actual physical size, occlusion, ray input or viewpoint following. Ordinary 2D content and actions are real Web components.

## Source basis

Checked against the user's local SpatialSDK checkout at `d16142477`:

- `spatialui/foundation/src/main/kotlin/com/pico/spatial/ui/foundation/content/SpatialView.kt`: `AttachmentPanelBuilder` declaration.
- `spatialui/foundation/src/main/kotlin/com/pico/spatial/ui/foundation/content/SpatialUIAttachmentPanel.kt`: caller-provided Compose content.
- `SpatialAppSample/stagerendering/src/main/java/com/pico/spatial/sample/stage/rendering/content/MainScene.kt`: explicit material on attachment content and entity placement.
- `spatialui/integration-tests/demos/src/main/kotlin/com/pico/spatial/ui/demos/modules/attachmentpanelcomponent/SpatialViewAttachment.kt`: attachment as a child of an object entity.

The examples here are small adaptations, not copied SDK demo screens. Native snippets were checked against source, not built or device-tested.

## Recording the design in Spec

Use [3D Preview authoring](../../3d-preview.md) to record the owning scene/object, placement and whether the panel follows model movement. Keep these notes under the panel's stable ID. A panel to the right of a model may remain stationary or follow it; choose explicitly.

Record `props.background: "transparent"` or `"material"` in Spec, matching Preview. The latter requests the explicit Regular glass content background described above; it is not a native AttachmentPanel parameter. See the [character Preview and Spec](../../../spec-writing-reference/character-example/README.md).

The three examples use the shared `sui-volume` shell with explicit width, height and depth. The wireframe is schematic. Their DOM hierarchy demonstrates ownership; `sui-attachment-panel` does not supply an automatic anchor API. In native code, parent the attachment entity under the intended object/anchor entity; parent transforms include translation, rotation and scale. The third example instead keeps the control strip under the display group while rotating only the model.
