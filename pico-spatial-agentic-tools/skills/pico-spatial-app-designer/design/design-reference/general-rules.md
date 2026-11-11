# General design rules

These rules and recommendations apply to this Design-to-App Plan without changing SDK defaults. Mandatory background restrictions are stated below; recommended values remain optional. Record actual customizations on their owning nodes in Spec.

## Content ownership and expression

Use the page responsibilities and content relationships established in Explore when writing copy and composing components. Apply the following rules while building the page.

### Place content with the subject it explains

Decide what a piece of content describes before choosing its location. Its placement should make that relationship clear.

| Content purpose                                            | Placement                                                                                                   |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Identify the window or explain its overall purpose         | Keep it in the window title group. Use an optional TitleBar subtitle for the purpose or content scope.      |
| Name or explain a specific section                         | Place it with that section and the content it introduces.                                                   |
| Describe an object's properties or status                  | Place it in that object's item or detail region, with the subject identifiable.                             |
| Explain an operation's conditions or how to perform it     | Keep it near the relevant operation or target.                                                              |
| Explain an empty/error state or report an operation result | Show it in the affected content region or the appropriate feedback surface when that state or event occurs. |

For example, Spatial Shelf already has its name in TitleBar. "Find your next app for your space" explains the whole window; place it below the name in the title group rather than as a standalone first body row. The body can begin with categories and applications. See [TitleBar composition](components/TitleBar/README.md#plan-composition-title-subtitle-and-page-search).

A section heading must introduce an actual section. "Recommended apps" above a recommendation collection is valid. "No saved apps yet" belongs in the collection's empty state, and "Drag the model to see its back" belongs near the model interaction. These are not window subtitles. Omit the subtitle when the window needs no further explanation; keep an existing subtitle with its title when adding search.

### Merge repetition that adds no information

Do not repeat the same title in TitleBar and immediately below it. Also avoid successive labels that restate the same object, selection or purpose in different words. A second region showing the same information needs a distinct contribution, such as additional detail, useful actions or context needed to understand it independently.

For example, a calendar highlights day 12 while its detail stacks "Selected date · 12", "October 12" and "Today's agenda". Use one detail title, "October 12 · Agenda", and begin the body with the agenda. Keep the date needed to identify the detail independently; remove the redundant selection explanation and synonymous headings.

List summaries and full details may coexist. Section headings, useful summaries, intentionally persistent navigation and object identification in a separate detail surface remain valid. Judge the information and role of each occurrence, rather than deleting every repeated word.

### Give copy a concrete purpose

Use copy to identify an object, explain a group, communicate a state, guide an operation or present requested business information. Do not invent slogans, welcome messages or generic descriptions merely to fill space. For example, omit an unsolicited "Make management more efficient" line when it conveys no specific information.

Make vague information meaningful instead of automatically deleting it. A status such as "Normal" needs an identifiable subject; place it with that subject or clarify what is normal. Keep design rationale, component names and implementation notes out of the product UI unless they are part of the requested product content.

For user-supplied copy, first correct placement or clarify meaning before considering removal. Preserve explicitly requested brand expression.

## Navigation and attached tools

Explore owns [navigation structure](../layout-2d.md#4-navigation-and-content-switching) and [task-tool selection](../layout-2d.md#task-tools-and-toolbar). Plan implements those decisions and the controls inside them. If an appropriate opportunity was missed or the structure needs to change, update the Explore record before continuing. Use these compositions without turning them into mandatory page templates:

| Page/task                                              | Consider                                      | Concrete composition                                                                                                                                                 |
| ------------------------------------------------------ | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Music app with Discover, Playlists and Library         | TabBar for app destinations                   | Icon + label for each destination; selection changes the page. Playback tools remain available through a Toolbar if playback spans those pages.                      |
| Store with Browse and My account                       | One TabBar with different destination layouts | Browse contains horizontal categories and a grid; My account contains a left sidebar and right page. Local switches affect only their own region.                    |
| Photo viewer with repeated zoom, rotate and comparison | Toolbar attached to the viewer window         | Main group: previous, next, rotate. Optional supporting group: compare or info. It stays available while inspecting the image.                                       |
| Editing or selection task                              | Toolbar with mixed content                    | Combine mode controls, relevant parameters, text commands and concise context such as selection count. Update content with the task; supporting content is optional. |
| Library with many destinations and groups              | Full-height SideNavigation                    | Icon + label items on the left; a separate TitleBar above the right page. Global search lives in the sidebar; current-page search in that page's title region.       |
| A Wi-Fi settings row                                   | ListItem with trailing Switch                 | The action belongs beside that setting; it does not require a Toolbar.                                                                                               |
| List/grid views of the same collection                 | SegmentControl                                | Switch the presentation of one collection; do not add another app-level navigation bar for this.                                                                     |

Preserve useful left/right layouts within a TabBar destination. Navigation and tools can coexist at different scopes; do not repeat the same destinations or operations in multiple places. The [TabBar](components/TabBar/README.md) and [Toolbar](components/Toolbar/README.md) guides describe task suitability and provide the original component reference previews. [SideNavigation](components/SideNavigation/README.md) supplies the sidebar composition details. Task-content suggestions do not replace the SDK's component sizing, spacing and composition rules.

TabBar and Toolbar are window fittings on native. Use the library elements in Web; do not replace them with a decorative capsule made from ordinary layout. Native attachment belongs to the WindowContainer. Web coordinates and offsets are preview geometry, not new native positioning parameters.

## Operation placement

- Put a back or close IconButton at the leading/top-left position of a task surface that has a title bar. Use back for returning within a flow and close for leaving the surface; specify which action it performs.
- Put a few familiar auxiliary actions, such as help or more, in the title bar's trailing region. Give icon-only actions accessible names. An IconButton is appropriate only when its symbol is understandable.
- Put long-label actions and primary form submissions in the task's action region, usually at the bottom right. When Explore chose Toolbar for page-wide pending edits, preserve its Save/Apply/Discard group instead of duplicating it in the page. A short but consequential action such as Install can still belong in a local action region; text length alone does not decide priority.
- A Sheet already provides a title region and default leading close. Use those slots. A Subwindow needs its own TitleBar and content organization. A BasicSheet supplies only the surface, so its caller supplies the header and exit.
- Keep the native decision layout of AlertDialog and DatePickerDialog. Cancel/Delete or Cancel/Apply expresses a decision and can remain in the bottom row; do not force an extra title-bar close into every dialog family.

### Button rows and compact regions

When there is room, align a single action or a group to the right, with a visible gap between buttons. In a narrow content region, let its primary button fill that region. For multiple buttons in a narrow region, choose equal widths or a vertical arrangement according to priority and label lengths; avoid overflowing or truncating a label.

```html
<!-- Wide content: the parent owns alignment and the 8px gap. -->
<div style="display:flex;justify-content:flex-end;gap:8px">
  <sui-button text="Save" leading-icon="ic_check"></sui-button>
</div>
<!-- Compact content: one primary action fills its region. -->
<div style="width:280px;max-width:100%">
  <sui-button text="Continue" style="display:flex;width:100%"></sui-button>
</div>
```

### Avoid duplicate exits

This is a local composition rule, not an extra pre-design checklist. If the Sheet's top-left close and a bottom Cancel both discard the same changes and exit, use one exit. Keep Save at the bottom for submission. Decide whether an unsaved-change prompt is needed from the task. Keep two actions when they genuinely perform different operations.

## Backgrounds and colors

For an application Preview, use the runtime's [Preview window helpers](runtime/README.md#application-preview-windows): `sui-preview-stage` supplies the browser backdrop and `sui-planar-window` supplies the main window material and radius. Pass the chosen window dimensions through page CSS; the shell has no fixed size or content padding. Avoid adding another page-authored background to reproduce that window material. An explicitly transparent window uses `background="transparent"`. These helpers do not replace the meaningful content backgrounds described below or alter Sheet/Subwindow materials.

Scene attachments have a different background default: `AttachmentPanel` does not supply glass automatically. Short labels may stay transparent; bounded information/control panels should explicitly request a glass backing in Preview and record it for App. The glass belongs to the attachment content root, not every nested layout. This is separate from ordinary content fills and does not give the entire Volume/Stage a background. See [AttachmentPanel](components/AttachmentPanel/README.md).

There are three separate things to draw:

1. **Window material:** the system surface behind the page, Sheet, dialog or toolbar. The browser's translucent fill is an approximation of that surface.
2. **Control surfaces:** ListItem, Button, TextField, selected navigation and other components already draw their own fill. Prefer their supported color parameters for a deliberate override.
3. **Application content:** photos, artwork, charts and a specifically designed bounded content region may need their own colors or background.

A decorative illustration or patterned background can be a reusable image asset. Keep it separate from ordinary content fills and system window material: save the artwork, then record where and how it is displayed. Do not flatten text, controls or interaction into a background image. See [application visual assets](runtime/README.md#application-visual-assets) for the file/Preview handoff and a book-cover example.

Pages, bodies, columns, list/grid organizing containers and large content sections must remain transparent over the system window material. Separate them with spacing and headings. A local item, card or cell may have a background such as `fillLight`; do not nest application-authored backgrounds inside another application-authored background, including state-dependent fills. Standard controls retain their built-in surfaces, and image pixels are not additional UI fill layers. Do not use an image or a large “card” to bypass the transparent-layout rule. For custom interactive blocks, describe the base appearance and relevant selected/active/focused/checked appearance. Existing components already supply their own surfaces and states; use those capabilities first.

For example, a calendar designed with individually filled date cells:

```text
Window: system-provided background
└── Calendar layout: transparent; arranges the cells
    ├── Date cell: base background
    ├── Date cell: base background
    └── Selected date: explicit selected-state background
```

Here the date cells are content surfaces; the layout arranging them needs no additional base. Avoiding nested backgrounds must not erase the cells' intended backgrounds. This is one calendar design, not a requirement that every calendar use filled cells. Text-only groups, images and intentionally transparent content need not become filled tiles.

A Row, Column or spacing wrapper must remain transparent. For example, a Sheet → transparent form layout → TextField does not need both a filled form wrapper and another filled field wrapper around the field's existing fill. Keep layout-only wrappers transparent, while preserving meaningful content backgrounds. Record each deliberately added surface and its chosen color role/token.

Separate ordinary content groups with spacing and headings; do not add decorative borders to their layout containers. Component-provided borders, error outlines and focus indicators remain valid.

Do not simulate a native material with extra app-painted blur, borders or shadows on top of the native component. Do not give a transparent structural node a radius that is later interpreted as a new filled surface.

Choose the semantic role from [color-roles.json](color-roles.json), then use its mapped value from [tokens.json](tokens.json). Describe system colors by role/token name and reference the corresponding CSS variable in Web; do not hard-code copies of system HEX values in page styles. Use `labelPrimary` for normal foreground, supporting roles for secondary text, `labelPrimaryLight` on the appropriate dark control fill, and semantic error/alert/success colors for those meanings. Photos and charts do not need to be forced into control colors. Define separately named application colors for deliberate brand or content accents; do not globally redefine the system roles to color one region.

### Icon color in a concrete component

An independent Icon uses the system primary foreground by default; `tint` selects a specific color. In a Button, the default icon and its text use that Button's content color. For example, the default dark Button has white text and a white icon; a disabled Button fades both together. Set the Button's `content-color` when both should change. Give an individual Icon a `tint` only when it intentionally differs. See [Icon](components/Icon/README.md) for runnable examples.

The role descriptions explain when to choose each existing role; the role-to-token mapping and values are unchanged. Use the selected component's supported color parameters for explicit overrides. [Vibrant](vibrant.md) explains the scene-dependent native effect and preview differences.

## Spacing and alignment

Group strongly related content with smaller gaps, keep peer items consistently spaced, and use larger gaps to distinguish modules. Prefer spacing and headings over a divider between every group. Read the existing gap/padding token usage when choosing application-owned layout values; preserve documented component spacing.

- The parent layout owns the gap between siblings. Each component owns the padding inside its surface. For independent ListItems, use a parent gap of 8 and explicitly set each item's recommended internal padding to 16 on all four sides. The reference default end padding is 4; it remains 4 when not overridden.
- Below a normal page TitleBar, the recommended content padding is start/end/bottom 32 and top 0. Keep the 96-high TitleBar separate; adding another top 32 would double the intended separation. This is a page recommendation, not a blanket override for all controls or Sheet variants.
- In a sidebar/page composition, do not pad the entire root row. SideNavigation owns its horizontal 24; the right TitleBar owns its horizontal 24 and title inset; the right body owns its content padding. See the explicit [SideNavigation example](components/SideNavigation/preview.html).
- Use the reference 8/12/16 gap tokens and 8/16/24/32 inset tokens. Component-specific values and explicit recommendations, such as the SideNavigation item gap, remain as documented by that component.
- Align visible icon/text edges, including internal insets. Aligning only the outer boxes can leave the content misaligned. Preserve consistent widths and gutters in repeated groups.
- When a list or grid has column headings, align each heading with the actual text or icon below it. Share column widths and gaps between the header and rows, accounting for item padding. For example, if filenames start 16 inside each row, the Name heading must account for that inset too. Preserve this alignment when resizing; this does not require adding headings to every grid.
- A block spanning multiple grid rows has height `n × rowHeight + (n − 1) × gap`. Include the intervening gaps when aligning it to neighboring blocks.
- Keep fixed controls reachable and scroll long content deliberately. A narrower preview must not silently crop action labels or the only exit; choose a documented width, reflow or scrolling behavior.

### Body and bottom actions

Keep a deliberate gap between body content and its action buttons. Window-edge padding and the content-to-action gap are separate distances. When the body and actions share one content container, apply the window inset once:

```text
TitleBar
Content container: start/end/bottom 32, top 0
├── Body content
├── Gap chosen for the content/action relationship
└── Right-aligned button group
```

Do not add the same window inset again inside the action group. A separate bottom action region is useful when actions stay fixed while the body scrolls; it shares the body's horizontal alignment and owns the bottom window inset. Keep content-to-action separation in that arrangement too. Do not apply this page convention over the defaults of every Sheet or dialog.

## Nested corners

Application-authored backgrounds must not nest. A cropped image or a standard control can still sit within a local content surface; preserve its intended shape and the control defaults. Where image and enclosing contours visually correspond, account for the inset when choosing the crop radius. A radius is not permission to add another background.

## Typography, controls and state

The original component type roles stay in [tokens](tokens.json). Inherit standard component typography and color. Existing user/reference-backed exceptions must identify their source; the only additional exception in this iteration is the optional TitleBar primary-title weight described here. It does not authorize changes to subtitle, search or action styles. The recommended page TitleBar primary title uses weight 700 rather than the reference titleLarge 600; apply the weight to that title only. Subtitles stay at bodyMedium, actions and search text retain their own styles. Choose Body for descriptions and reading text, appropriate supporting styles for timestamps/counts, and title styles for actual headings. Use existing multiline variants for continuous paragraphs where available. Do not promote ordinary supporting information into a display heading or shrink a real component title to satisfy a separate body-size limit.

Use Button for actions, not as a wrapper around a complex content tile. Use the appropriate layout and interactive component when the target includes an image, several text lines or several independent controls. A custom interactive target's visible shape, clip, hover and click region should agree. Do not stack another hover effect on a built-in control that already has one.

### Hover for click targets

Every enabled click, selection or toggle target must have perceptible hover feedback. Use a component's existing feedback where provided; for custom regions use [spatialHoverEffect](runtime/README.md#spatialhovereffect) rather than writing another hover style. Hover and click apply to the same target and shape. Keep an ordinary read-only region free of feedback that suggests an action. Disabled targets must not show enabled hover feedback.

ListItem now includes whole-row hover in this Web bundle; do not add a separate helper call or outer hover wrapper. Button and other components with built-in feedback keep their existing treatment. Hover is a preview indication, not a reason to add arbitrary scale or Z offsets.

Record the hover requirement on the owning design node, together with its actual action. For a custom region, App restoration puts `.spatialHoverEffect()` on that component's Modifier, before its click/selection behavior. Built-in native components that already provide hover need no additional modifier. The Web helper's DOM argument is only an element reference; it is not a Spec dimension, native argument or extra design node.

Show relevant selected, disabled, empty and long-content states. In a runnable design, navigation should change the shown page and task actions should have an observable result, not merely change their own highlight. Examples here demonstrate component behavior; application state and services still need the app implementation.

## Actual values in Spec

A recommendation becomes part of the design only when applied. Record the chosen value on the relevant component or layout rather than writing "use recommended/default style". For example:

| Design decision                  | Record                                                               |
| -------------------------------- | -------------------------------------------------------------------- |
| Recommended ListItem insets      | start 16, end 16, top 16, bottom 16; parent gap 8                    |
| Reference ListItem untouched     | omit padding overrides; referenced defaults apply                    |
| Recommended page title           | primary title weight 700; subtitle separately specified              |
| Recommended sidebar item         | min height 48; start 16; top/end/bottom 8; parent gap 4              |
| Toolbar with supporting controls | host window, task scope, main/supporting content and attachment kind |
| Chosen icon                      | stable catalog ID, resource path, size and default/explicit tint     |

The Web attribute names belong to this preview library; the native implementation uses the corresponding SDK arguments documented by the component. There is no requirement here to adopt the old spatial-web attributes or to change the Spec schema.
