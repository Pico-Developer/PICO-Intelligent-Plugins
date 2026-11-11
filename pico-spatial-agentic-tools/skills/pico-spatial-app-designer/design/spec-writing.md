# Write Spec — Record the approved design as JSON

## 1. Purpose and scope

Produce `design-spec.json` from the approved Preview. The App implementation should be able to recover the intended windows, content, components, layout, appearance, assets and essential visible states without making new visual design decisions.

This guide is written for the authoring agent. The deliverable remains JSON.

- **Standard components:** record identity, content, variant, explicit configuration and overrides. Omitted properties retain the referenced component defaults. Do not enumerate or inspect every default.
- **Application layout:** record dimensions, arrangement, alignment, padding, gaps and scrolling ownership.
- **Custom compositions:** describe their visual parts and the parameters needed to reconstruct them. A component name or renderer key alone is insufficient.

Work at the approved window size. Do not add resizing ranges, responsive breakpoints or a complete business state machine. Record enough state and interaction to explain what appears and what changes after the main actions.

Write Spec does not require screenshots. Critique reviews the actual design; Write Spec records it and checks applicable rules; [Consistency Review](../SKILL.md#6-consistency-review) checks the completed record against the Preview.

## 2. Inputs and output

Read the approved Preview markup, application CSS, component configuration, supplied slot content, asset references and relevant display logic. Use existing Frame/Explore records for container choices, ownership and spatial relationships.

Use [design-reference](design-reference/README.md) for component identity, parameter meaning and applicable rules. Consult an implementation only when a particular customization is unclear, rather than expanding all standard defaults.

Deliver:

1. `design-spec.json`.
2. The referenced application assets.
3. A resolvable design-reference version or snapshot.
4. A short account of unresolved issues in the existing design record, when necessary.

Application CSS overrides count as design decisions even when they are not HTML attributes. Preview-stage margins, scenery, debug controls, browser-only glass simulations and implementation-only wrappers do not belong in the application design tree.

If the approved implementation conflicts with a confirmed design decision or an applicable rule, identify the affected node and difference. Correct recording errors here. Return actual design changes to Plan, then update the Spec. Do not silently redesign the UI or describe a compliant UI that the Preview does not contain.

## 3. Authoring sequence

1. Identify the approved Preview revision and design dimensions.
2. Record windows, page responsibilities and ownership.
3. Build a node tree with stable IDs.
4. Record application layout and explicit component customizations.
5. Expand custom visual compositions and register actual assets.
6. Record initial values, selection appearance and essential action results.
7. Run the [Spec checker](scripts/check_design_spec.py), fix errors, review warnings and rerun it; complete the manual checks below.

Do not copy the DOM mechanically. Preserve a wrapper when it owns meaningful layout, padding, appearance or grouping. Omit wrappers that exist only for rendering mechanics.

## 4. JSON organization

The examples use `write-spec-draft-1`, a working format for the redesigned flow. Its meaning is defined here; the format is still being refined. Window-size ranges and a full state machine are not required.

| Field                      | Responsibility                                                                          |
| -------------------------- | --------------------------------------------------------------------------------------- |
| `metadata`                 | Project name, revision, Preview location and reference snapshot                         |
| `experience`               | Brief task and content/container form already decided upstream                          |
| `theme.brandColors`        | Explicit application colors, if used                                                    |
| `surfaces`                 | Windows, dimensions, roots, ownership and placement                                     |
| `nodes`                    | Flat list of layout, local content, component, text, media and specialized visual nodes |
| `assets`                   | Stable resource IDs, actual paths and purpose                                           |
| `initialStateId`, `states` | Initial visible state and relevant values                                               |
| `actions`                  | Main action results, without implementation code                                        |
| `dataCases`                | Optional content records or samples used by repeated/dynamic content                    |

Paths are relative to the Spec file. References may use a release version, a snapshot identifier or a file hash. Reference the shared library once rather than repeating its path on every component.

For a node corresponding to a Preview element, reuse its stable, unique HTML `id`. If a meaningful element has no ID, add the identifier to Preview without changing appearance or behavior, then record it. Do not infer identity from a CSS class, label or screen position. Component internals and rendering-only wrappers are not separate application nodes. Surface, asset and action IDs do not all need HTML counterparts; a `domain_visual.parts` entry is not automatically an independently addressable element.

For example, the TitleBar node declares `component: "sui-title-bar"` and `children: ["header-copy"]`; the `header-copy` layout node records its column/gap and text children. The matching HTML uses `<sui-title-bar id="main-titlebar">` and `<div id="header-copy" class="header-copy">`. Record both component identity and content ownership, not just the layout node in isolation.

Node IDs must be unique. `children` contains node IDs, not copied node objects. `assetId` identifies an entry in `assets`. `events` maps an event to an action ID. `bindings` identifies the content/state supplying a value; it is a design relationship, not an instruction to execute arbitrary expressions.

The same resource can be used by several nodes. Each usage records its own display dimensions and crop. For repeated structures, reuse an agreed template mechanism when available; otherwise list concrete nodes. Do not invent an undocumented template language.

## 5. Containers, windows and subordinate content

Record each surface's type, approved `defaultSize` including units, and `rootNodeId`. Windows and standard components retain their system material. Only a planar surface may record `windowBackground: "material"` (default) or `"transparent"`; transparency requires the explicit user decision in `windowBackgroundEvidence`. Do not introduce material fields on ordinary nodes or translate simulated Web blur/shadows into native overrides.

In Web Preview, `sui-preview-stage` is presentation scenery and `sui-planar-window` represents the planar surface. Record the latter's externally specified dimensions and material/transparent choice on the surface, keeping its application content under `rootNodeId`. Do not add either helper as a native component node. Do not copy the stage backdrop or the shell's simulated fill, blur and shadow into node appearance. See the [runtime example](design-reference/runtime/README.md#application-preview-windows).

For a companion surface, additionally record:

- `ownerSurfaceId`: the owning main surface.
- `placement`: side, alignment, actual gap and depth offset, with units.
- `initiallyVisible`: whether it is present before any selection.
- The action that opens it, how selection changes its content, and how it closes.

A selection-driven detail window belongs to the selected object. Do not make it a permanently visible peer region just to fill the page. Conversely, do not introduce a Subwindow solely to demonstrate the component: simultaneous access to the main content and details should serve the task.

A Subwindow must describe its own title bar, leading close/back control, body and relevant actions. Its root must not also be rendered as ordinary content inside the main window. Window ownership is a surface relationship, not a second parent in the content tree.

Use dp for 2D layout and sp for text. Specify units and coordinate references for 3D. The reference Web library treats px as the preview equivalent of dp/sp; this does not make scene meters interchangeable with dp.

## 6. Components and explicit overrides

Use `kind: "spatialui"` and the actual component identifier, such as `sui-list-item`. Put application configuration and explicit supported overrides in `props`. Use child nodes for caller-provided slot content.

- An untouched ListItem does not need padding declarations.
- `content-padding: 16` overrides all four internal insets.
- `padding-end: 16` overrides only the trailing inset; other sides remain default.
- Padding overrides replace the specified default; they are not additional spacing.
- A title-only weight change belongs to the title node, not the entire TitleBar. Weight 700 is optional; an unchanged title needs no override.

Use `props.title-node-id` on a TitleBar to identify its primary title when supplied as a child node; use `props.subtitle-node-id` for a composed subtitle. These are Spec references, not Web attributes. Each must point to its own text descendant through the default title slot (transparent layout wrappers are allowed). A simple `props.title` string may use the built-in title without a separate node. Do not mark a search label or leading action as the title.

```json
[
  {
    "id": "bar",
    "kind": "spatialui",
    "component": "sui-title-bar",
    "props": { "title-node-id": "heading" },
    "children": ["heading"]
  },
  {
    "id": "heading",
    "kind": "text",
    "content": "Library",
    "textStyle": { "overrides": { "weight": 700 } }
  }
]
```

Omitting `heading.textStyle` keeps the component default. Applying `textStyle` to `bar` or its layout wrapper is incorrect because it spreads to other text. The existing composed subtitle style `bodyMedium` / `labelSecondary` remains valid when explicitly referenced. Other changes to component-owned title/navigation text require `styleOverrideEvidence: {"source": "user" | "figma" | "screenshot", "reference": "..."}` from an existing design input; do not generate screenshots or invent evidence for this stage. This does not open arbitrary font/color overrides on other standard controls. Caller-authored content compositions, such as the text within a ListItem's custom headline layout, still declare their own text tokens.

For a Subwindow, record `regions: {"titleBarNodeId": "...", "bodyNodeId": "..."}` on the Subwindow node. Its TitleBar precedes its body; the leading IconButton records `props.navigation-action: "close"` or `"back"` and an event referencing the corresponding action. These references describe ownership, without imposing the previous library's named title/content slots or repeating default alignment.

Web attribute names identify the chosen configuration, not guaranteed native API names. Preserve the meaning of the parameter; App implementation maps it to the target component API.

An unmodified Button can be recorded simply as:

```json
{
  "id": "read",
  "kind": "spatialui",
  "component": "sui-button",
  "props": { "text": "Start Preview", "size": "regular" }
}
```

Do not expand its default radius, typography, colors or internal geometry.

### Layout versus component padding

`layout.paddingDp` belongs to an application layout region. Component internal padding belongs to the component's `props`. The parent owns sibling gaps.

```json
[
  {
    "id": "book-list",
    "kind": "layout",
    "layout": { "mode": "column", "gapDp": 8 },
    "children": ["book-row"]
  },
  {
    "id": "book-row",
    "kind": "spatialui",
    "component": "sui-list-item",
    "props": { "content-padding": 16 }
  }
]
```

This illustrates ownership; actual rows also need their content. Do not turn the parent's gap into bottom padding on each row.

## 7. Layout, text and appearance

### Layout

Record `mode`, dimensions and constraints actually used, `gapDp`, `paddingDp`, `align`, `justify`, `grow`, columns and overflow as relevant. Numeric padding applies to all sides; directional application padding uses top/right/bottom/left.

Fixed dimensions, minimum dimensions, content sizing and remaining-space allocation have different meanings. Do not replace one with another. A missing width does not automatically mean fill-parent. Describe the governing parent layout when relying on that relationship.

The example also uses `marginTop: "auto"` for an action group that sits at the bottom of its available content area. This is a placement relationship, not a fixed guessed gap.

### Typography

Application-authored text references an exact typography token and a color role. Standard component text and unmodified slots inherit their component styles.

Application-owned text uses `textStyle.typography` and `textStyle.color`; `textStyle.overrides` may record actual partial changes such as `weight`, `sizeSp`, `lineHeightSp` or `fontFamily`. Component-owned text inherits its defaults under the exceptions above. Unspecified properties still inherit the selected token or owning component. For example, the optional TitleBar primary-title customization is:

```json
{
  "id": "main-title",
  "kind": "text",
  "content": "Weekend Reading List",
  "textStyle": { "overrides": { "weight": 700 } }
}
```

Use `textBehavior` for actual line limits, wrapping and truncation when relevant. Do not automatically truncate every label or replace a local override with a global token change.

### Appearance and state

Record actual fills, foreground roles, radius and opacity on the owning node. System colors use role names such as `labelPrimary` and `fillLight`. Application colors use named entries in `theme.brandColors`.

Follow the [background rules](design-reference/general-rules.md#backgrounds-and-colors). `layout` and `domain_visual` organize transparent regions. A custom local item/card/cell that owns a fill uses `kind: "content"`; it can still have `layout` and `children`. Use `appearance.fill` for the base fill and `visualStates.<state>.appearance.fill` for state differences. This kind is not permission to fill a page, column or large section. App-authored fills must not nest. Standard controls use their own supported props; window materials and image pixels are separate.

Correct: transparent body → ListItem with its own component background. Incorrect: filled body → business card with another fill. Custom case: transparent calendar layout → individual `content` date cells. Keep the organizing calendar region transparent.

System roles and bundled token names may be referenced directly. Custom colors must be named in `theme.brandColors`, for example `{"bookAccent": "#84704F"}`, then referenced as `bookAccent`. Do not redefine a system role or token under that map. There is no need to repeat the system color table. Do not copy browser scenery or material simulations into the application appearance.

For a state-dependent component override, `visualStates` records only differences:

```json
{
  "visualStates": {
    "selected": { "props": { "container-color": "fillSecondary" } }
  }
}
```

Specify which action/state applies this override and when it is cleared. Standard hover and pressed behavior remain default; do not duplicate the Web simulation as a native effect.

## 8. Custom compositions and assets

A composition of an image, text and controls can be represented with ordinary layout, media, text and component nodes. A named card is not automatically a native SDK component.

For a genuinely specialized visualization, `domain_visual` may identify the rendering approach. Its internal independently styled regions still need their layout, appearance, resources and essential states. Use ordinary child nodes, or a `parts` object keyed by local part ID. Each part records its layout, appearance and optional `states` (state name → appearance differences); parts describe local visual units, not nested filled containers. Do not duplicate the same composition in both forms. A renderer key cannot replace these facts. Static artwork already delivered as a reusable image is different: use a `media` node and `assetId`; do not expand its internal SVG paths, circles or gradients into application layout nodes. Keep independently changing data, text and interaction as design nodes rather than flattening them into an image.

For each asset, record ID, kind, actual local path and purpose. Icons may also record their stable catalog ID. Do not substitute a similar image or same-named icon during restoration.

At each image usage, record dimensions or an explicit sizing relationship, fit, crop alignment and actual corner radius. For Icons, record size and explicit tint only if set. An omitted tint preserves the control-slot/default color behavior. Ordinary full-color cover images are not tintable Icons.

### Reusable artwork and decorative backgrounds

Preview-authored covers, illustrations and decorative backgrounds must have actual reusable asset files. Reuse the approved files instead of describing a similar image for App to redraw. SVG artwork keeps its original colors unless the design explicitly defines a variant or tint; the icon tint convention does not apply to every SVG. Internal artwork colors belong to the resource, while system UI colors continue to use roles/tokens.

For example, `assets/slow.svg` is registered once as `slow-cover`. The list's `cover-slow` node displays it at 60 × 80 with `fit: "cover"`, centered crop and radius 6; `detail-cover` selects the same asset through the book data and displays it at 72 × 96. See the [exact Preview/Spec example](spec-writing-reference/README.md#reusable-artwork-example). Do not reconstruct the cover's illustration as UI geometry or apply Icon tint to it.

A decorative background can also be a media node referring to an image asset. Record its owning region, placement behind foreground content, dimensions or sizing relationship, fit/crop and any actual opacity, tiling or state changes. Preserve the approved stacking and clipping relationships; a file path alone does not specify how the background is used. Do not register browser-stage scenery or simulated window glass as application artwork.

If Preview embeds an inline copy, the standalone delivered file must match it. If required artwork exists only in drawing code or an embedded payload, materialize the same approved artwork as an asset without redesigning it; return any appearance-changing extraction to Preview review. App may convert the resource to a supported native format while preserving its approved appearance; file delivery alone is not proof of native SVG support.

When content changes with selection, record the content dataset and binding. For example, `detail-cover.bindings.assetId` selects the chosen book's cover asset. Every selectable record must resolve to a real asset.

## 9. Essential behavior and optional 3D

For navigation and task tools, preserve Explore's decisions and the approved Preview using the existing surfaces, nodes, props, bindings, states and actions. Record the host window, actual destination/action target, selected value, visibility and necessary state retained on return. TabBar changes the main destination; a sidebar or local switch changes its own region. Preserve each destination's layout instead of flattening all levels into one navigation list.

For Toolbar, record the mixed content and main/supporting slot ownership, the content or selection acted on, and how tool modes, parameters, enablement and concise status change together. Specify whether it belongs to a page, selection or shared session, including entry/exit conditions. Keep shared task state across page switches only when the approved design requires it. Use existing action descriptions and node bindings; no new schema or full business state machine is needed. A text label or selection highlight alone does not record the intended operation result.

Record what the user initially sees and what the main actions change. Describe selection, panel visibility, relevant text changes and visual differences. Do not add timers, network calls, persistence or internal functions merely to make the JSON look executable.

The paired example uses actions for selecting a book, closing its detail, toggling collection status and switching between the introduction and a local reading sample. Action descriptions identify affected nodes and content; they do not claim a full reader or storage service exists.

For authored 3D content, record delivered scene/object references, coordinate system, units, size, position, orientation and necessary 2D/3D controls. Do not restate unchanged details already contained in the delivered scene or introduce 3D just to fill a template.

## 10. Completion checks

From the skill directory, run:

```bash
python3 scripts/check_design_spec.py /path/to/design-spec.json --target /path/to/project --json
```

Only the Spec path is required. The checker uses the bundled color/type catalogs, resolves assets and reference files relative to the Spec, and verifies hashes when provided. Optional `--asset-root /path/to/delivered-assets` resolves `assets[].src` from that directory instead; it is a handoff resource directory, not an Android runtime `res` folder. `--json` prints a machine-readable report. It does not execute Preview, bindings or app code.

- **ERROR:** fix the indicated JSON path/node and rerun. Exit code 1 means errors; 2 means the input or checker references cannot be read.
- **WARNING:** inspect the indicated item, fix an actual problem or briefly record why it is intentional in the existing design record. Exit code 0 means no errors, not that warnings have been reviewed.
- Change a recording mistake in Spec. Return an actual design conflict to Plan/Preview before updating Spec; do not change only the record to make validation pass.

The checker requires Python 3 and Node.js. `--target` is the application project root; when omitted, it defaults to the parent of a Spec directory named `.scratch`, or otherwise the Spec directory. It invokes the same handoff rules bundled into the Workflow gates: every `nodes[].id` occurs exactly once in static HTML (not only in JavaScript), and every application asset resolves to a file inside the real project root. It reports all independent node and resource errors together, including duplicate/missing HTML IDs, missing files and symlink/path escapes. Reference documentation and Preview runtime snapshots are separate from application assets. `--asset-root` changes asset resolution only; it never relaxes project containment. Fix the reported set, rerun after corrections and check the final files before submitting Design.

The script checks structure and references, fixed window sizes, Subwindow ownership/regions/exit, assets, declared fills and nesting, system/custom color references, materials, title references and scoped typography exceptions. It also runs `check_preview_icon_resources.py` on `metadata.preview`, checking static HTML icon references against that Preview's runtime and resolving local icon files relative to the Preview URL (including its base element), independently of the command's working directory. Dynamic JavaScript icon references still require source review; static success does not establish their validity or rendered visibility. Application text at or above 20sp raises a review warning; an explicitly referenced TitleBar title and a valid `surface_title` are exempt. Untouched component defaults are not expanded. For an independently drawn dialog/popup heading, `textRole: "surface_title"` is valid only on a text node with a typography token uniquely owned by the supported surface and explicitly referenced by that surface's `props.title-node-id`; it must not relabel ordinary body text or replace a native title slot.

Custom `domain_visual` regions without parts or children, rounded parts without fill, and interactive part states without a fill produce review warnings. This preserves the previous custom-part review without making every standard control restate its states.

**Checks requiring author review:** the script cannot establish that every approved Preview parameter was recorded, that a node labelled as a local `content` item is not actually a large section, that copy/spacing/emphasis is appropriate, or that descriptive bindings/actions express the intended visible result. It does not verify every component-specific parameter combination, resolve descriptive binding expressions, or authenticate a written exception source/version identifier. It also cannot compare artwork to inline drawing code or prove native rendering fidelity. Review those points from the approved implementation and existing design decisions; no screenshot is required here.

Check that:

- Every window and major content region is represented and has a clear owner.
- Application layout and custom composition parameters are not left only in CSS or renderer code.
- Standard components contain configuration and overrides, without an unnecessary dump of defaults.
- Padding, sibling gaps, local typography overrides and backgrounds have unambiguous owners.
- IDs, children, actions, assets and selection bindings resolve.
- Resources and reference snapshots are available.
- Preview-authored reusable artwork has a delivered file; inline copies and referenced files agree.
- Each image usage records its actual sizing, fit/crop and radius; decorative backgrounds also retain their owning region and placement behind content.
- Artwork keeps its intended palette and is not mistakenly tinted as an Icon; live UI and system materials have not been flattened into the asset.
- Initial display and essential visual state differences are described.
- The JSON parses and contains no unresolved template placeholders.

Apply the used component documentation and [general rules](design-reference/general-rules.md). Check actual customizations for duplicated backgrounds/insets/hover, incorrect title/body ownership, color-role misuse and recommendations mistakenly treated as SDK defaults. Do not audit every untouched component default.

Unresolved issues must identify the node, impact and next handling location. Never mark an unresolved design issue as passed. A complete Spec establishes a usable design record; it does not itself prove native rendering fidelity.

## 11. Template and paired example

See the [reference guide](spec-writing-reference/README.md), [blank JSON template](spec-writing-reference/design-spec.template.json), [book-list Preview](spec-writing-reference/example/preview.html) and [paired Spec](spec-writing-reference/example/design-spec.json).

The Preview is authored directly with the shared component library. It does not render from the Spec. The JSON records the independently authored design. The example's dimensions and content are illustrative, not global defaults.

## 3D placeholders and scene design notes

Follow [3D Preview authoring](design-reference/3d-preview.md). Read both the rendered implementation and `script[type="application/json"]#scene-design-notes`. This block contains design requirements, not executable scene code. Copy each entry unchanged into the same-ID node's optional `designNotes` object; retain the source wording so omissions can be checked. Also explain model intent in `purpose` and record confirmed interactions in `props`, `bindings`, `events` and referenced actions where applicable. Do not invent APIs for prose-only requirements. If notes contradict visible design or code, return the conflict to Plan.

A model uses `kind: "domain_visual"` with a stable `rendererKey`. `designNotes.represents` explicitly identifies the 3D model/scene; `previewRepresentation` distinguishes a placeholder from confirmed simplified appearance. `assetStatus` is `to-create` or `available`. Available assets use an `assetId` referring to a real entry in `assets`; pending resources stay in notes, never in fabricated `assets[].src` paths. `appearance`, `behaviors` and `previewLimitations` are arrays of nonempty English descriptions. Record only confirmed requirements, and name unknown appearance details explicitly. A part need not be created for each rendering-only SVG shape.

For scene attachments, retain `relationship` and `followBehavior` in `designNotes`: identify the scene/object, placement and response to model movement. HTML adjacency is not a native scene constraint. If numeric scene coordinates are confirmed, include units and reference frame in the description; do not infer meters from screen pixels. `layout` dimensions describe the Preview region. CSS radius is not a sphere radius; selection highlighting does not imply physical displacement.

For `sui-attachment-panel`, explicitly record `props.background` as `transparent` or `material`. This is the Web/Spec choice: the native AttachmentPanel is transparent by default, and an explicitly chosen Regular glass background is implemented on its content root. Do not copy simulated blur/shadow into native parameters. This narrow exception does not permit material fields or arbitrary backgrounds on other nodes.

See the [character example](spec-writing-reference/character-example/README.md). Browser audit compares note preservation and attachment background configuration. Native animation, geometry, asset quality and follow behavior remain unverified until tested in the native implementation. Matching notes only proves that the requirements survived the handoff.

## Volume Preview shell

For a Volume surface, require positive `defaultSize.width`, `height`, `depth` and `unit: "dp"`. Read these values from the approved `sui-volume` attributes; width and height are also its actual rendered border-box dimensions at 1dp = 1 CSS px. The shell's HTML ID must equal the surface ID; `rootNodeId` identifies an application-content descendant. The shell itself is not a spatialui node. This keeps the container record separate from model/attachment nodes without introducing another set of Web dimensions.

Do not copy the shell's background, schematic outline or size caption into app appearance or assets. Depth configuration can be compared with Spec, but browser geometry cannot verify actual depth, native clipping or physical containment. Native SDK units are resolved at implementation time, not by inventing a meter conversion in this record.
