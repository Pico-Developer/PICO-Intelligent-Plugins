# Shared native component conventions

This reference supports the downstream Compose component mapping and shared style checks.
Designer authoring follows [Write Spec](../design/spec-writing.md) and its
[current validator](../design/scripts/check_design_spec.py). The accepted Preview
is authored before Spec; record its design facts without requiring an embedded
JSON renderer or regenerating the Preview from JSON.

### Typography token ceiling

App-authored text references exact public SpatialUI typography token names,
such as `headlineSmall`, `titleMedium`, or `bodyLarge`. Do not collapse them
into ambiguous family aliases such as `headline`, `title`, or `body`. Design packages must use exact token names.

`titleLarge` (20sp) is the soft ceiling for app-authored text. Prefer a token
whose size is strictly below 20sp for ordinary body and metadata. Semantic
dialog, Sheet, popup, and detail-window titles keep a native title slot or a
stronger exact title token. Do not remove the title or reduce it to body size
to clear a warning. Record its role and hierarchy in the design document.
An explicit token at or above that ceiling
is allowed when the composition genuinely needs the stronger focal point, but
`check_design_surface_discipline.py` emits a warning for ordinary content and the design document
must explain why it is necessary. Text rendered by a SpatialUI component's
native default does not declare `textStyle` and is not checked.

Custom headings within `sui-subwindow`, `sui-spatial-popup`, dialog, and custom
BasicSheet/HeadImageSheet families declare `textRole: "surface_title"` on a `kind: "text"` node. The field
is optional at schema level and currently has only that value; the Subwindow
content-title contract below requires it.
Standard `sui-sheet` uses its short native title slot and cannot declare a
custom `surface_title` exemption. Its title inherits native typography.
Subwindow has no built-in title slot, but its children must include a TitleBar.
Only a window title placed outside that TitleBar in the content region uses
this explicit semantic role. A heading inside TitleBar or another native title
component cannot declare `surface_title`. Use one bound title node per
content surface and an exact `textStyle.typography` token. Its nearest owning
surface component is resolved through unique node ancestry. Detached, ambiguous,
empty, or multiply declared surface titles are errors, not exemptions. Layout
wrappers between a surface and its title are allowed.

Validated surface-title nodes bypass only the ordinary-content typography ceiling.
They retain schema, native-token, color, line-limit, and surface-discipline checks.
The title is the largest text within its own content surface; inspect that
hierarchy in the open state. Do not mark body or metadata as surface_title.
Explicit larger ordinary content still produces the existing review warning.

During Compose restoration, put exactly one line immediately before the matching
`Text` call: `// design-style: surface-title <node-id>`. Pass the accepted
`design-spec.json` to the style verifier. It resolves the same title contract,
requires the same typography token, and rejects reused markers as exemptions.
A marker without the matching accepted title is not authority. Native title
slots that inherit component typography need no custom-title marker.

Component-owned slot text in `TitleBar` and `SideNavigation` omits `textStyle`
by default and inherits typography and foreground from the owning component, except for
the primary TitleBar title weight 700 applied explicitly during restoration.
The declared TitleBar subtitle uses the canonical explicit style described below.
Put non-visual constraints such as `maxLines` in `textBehavior`. Only add other
`textStyle` to those slots when the original user requirement, Figma node, or
screenshot explicitly requires an override, and record that source in
`styleOverrideEvidence`:

```json
{
  "id": "navigation-title",
  "kind": "text",
  "content": "Store",
  "textBehavior": { "maxLines": 1 }
}
```

```json
{
  "id": "compact-navigation-title",
  "kind": "text",
  "content": "Store",
  "textStyle": { "typography": "titleMedium", "color": "labelSecondary" },
  "styleOverrideEvidence": {
    "source": "user",
    "reference": "Use a compact title in the side navigation."
  }
}
```

| Token                 | Size / line height / weight |
| --------------------- | --------------------------- |
| `displayLarge`        | 40 / 54 / 700               |
| `displayMedium`       | 32 / 40 / 700               |
| `displaySmall`        | 28 / 34 / 700               |
| `headlineLarge`       | 24 / 30 / 700               |
| `headlineMedium`      | 20 / 26 / 700               |
| `headlineSmall`       | 16 / 20 / 700               |
| `titleLarge`          | 20 / 26 / 600               |
| `titleMedium`         | 16 / 20 / 600               |
| `titleSmall`          | 14 / 18 / 600               |
| `bodyLarge`           | 16 / 20 / 500               |
| `bodyLargeMultiline`  | 16 / 24 / 500               |
| `bodyMedium`          | 14 / 18 / 500               |
| `bodyMediumMultiline` | 14 / 22 / 500               |
| `bodySmall`           | 12 / 16 / 500               |
| `labelLarge`          | 14 / 18 / 600               |
| `labelMedium`         | 12 / 16 / 600               |
| `labelSmall`          | 11 / 14 / 600               |

## Node vocabulary

Use the smallest kind that preserves semantics:

| `kind`          | Purpose                                                                                         |
| --------------- | ----------------------------------------------------------------------------------------------- |
| `layout`        | `row`, `column`, `grid`, `stack`, `overlay`, or scroll ownership                                |
| `spatialui`     | A real vendored `sui-*` component; `component` names the exact registered tag                   |
| `text`          | Text content; app-authored text has an explicit style, while component-owned slot text inherits |
| `media`         | Image/video/model representation backed by an `assets[]` entry                                  |
| `domain_visual` | A visualization with no SpatialUI control equivalent, such as a waveform, map, or 3D timeline   |

### Directional content padding

Size regions from actual content by default. Do not manufacture hierarchy with
empty placeholders, unsupported fixed/minimum heights, or large blank areas.
Use typography, ordinary spacing, grouping, and content instead. Media aspect
ratios, real previews, interaction space, or an authoritative visual source may
justify reserved space; record its dimensions in the spec and its purpose in
design-doc.md. Renderer-only sizing is not an accepted design fact.

During Plan, apply the [Padding defaults](spatial-design-rules.md#padding) to
each main Planar window and Subwindow. Give each a separate body/content node
that owns the window inset. Default its left, right, and bottom to 32dp; below
TitleBar, default its top to 0dp unless the user explicitly requests otherwise.
Keep native header and navigation spacing; do not wrap page chrome in body
padding. If bottom operations are a separate sibling, give them the same
horizontal inset and let them own the window's bottom inset.

For example, a Subwindow with a TitleBar followed by a scrollable agenda uses
this body layout (its ListItems keep their own native internal padding):

```json
{
  "id": "detail-content",
  "kind": "layout",
  "props": { "slot": "content" },
  "layout": {
    "mode": "scroll",
    "grow": 1,
    "paddingDp": { "top": 0, "right": 32, "bottom": 32, "left": 32 }
  },
  "children": ["agenda-list"]
}
```

In pre-build critique, review the declared owner and values. In rendered
critique, compare the window's inner edge with the outer edge of its first-level
content blocks at default and minimum sizes. Missing declarations or departures
from 32dp are review prompts, not automatic failures. Request revision for a
concrete visible defect such as content touching the shell, excessive indentation,
or inconsistent content/action guides; identify the affected region and edge.
A written rationale alone does not establish visual correctness.

Do not diagnose duplicate padding by summing ancestor values: 32dp around a
card plus its own internal padding can be correct. Inspect whether two wrappers
are both adding the same window-to-content inset, accounting for native slot
insets and margins. Keep the body top decision independent: component height
and internal alignment may already provide space below the header.

`layout.paddingDp` already accepts either a uniform number or an object with
all four non-negative fields: `top`, `right`, `bottom`, and `left`. Use the
object when directions differ, and record the accepted values in the spec.
Preview maps these fields to the corresponding CSS padding edges; Compose
restores all four edges, preserving the physical left/right meaning (use
`absolutePadding` for a direct mapping), rather than collapsing them to a
uniform or horizontal/vertical value. Responsive changes must preserve this
directional representation.

When major content regions sit alongside each other, coordinate their visible
top starts unless an intentional offset has design evidence. When there is
only one region, review its vertical rhythm against the region above it.
Neither decision requires a side navigation. Apply this to app-owned content
layouts; it does not authorize overriding canonical component slot spacing
or adding padding around page chrome.

### Component affordance metadata

For every major region, command surface, or window-level component whose
placement affects implementation, record component-affordance metadata before
choosing the final row/grid layout:

| Field          | Values                                                                                                                      | Purpose                                                    |
| -------------- | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `role`         | `navigation`, `master-list`, `content`, `detail`, `auxiliary`, `modal-task`, `action-feedback`                              | What job the node serves in the product flow               |
| `trigger`      | `always-visible`, `selection-driven`, `command-driven`, `transient-feedback`                                                | How the node becomes relevant                              |
| `relationship` | `route`, `selects`, `peer`, `derives-from-selection`, `supports`, `confirms`, `reports-feedback`                            | How the node relates to the primary task or owning content |
| `presentation` | `inline`, `menu`, `submenu`, `popup`, `dialog`, `sheet`, `date-picker-dialog`, `snackbar`, `augment`, `subwindow`, `window` | Which SpatialUI presentation carries it                    |

Use these fields to prevent layout from becoming the component decision. A
multi-column body is valid for same-level peer content, for example two
planning views that must be compared continuously. It is not valid evidence by
itself for keeping selection-derived detail, status-only auxiliary information,
command-triggered panels, menus, confirmations, or transient feedback inside
the primary page `Row` / `Grid`.

Before assigning peer presentation, qualify the region in `design-doc.md`
against six questions: independent task, unique information,
lifecycle/interaction, coordinate-system compatibility, duplication, and the
delete test. The spec does not add another qualification field. Instead, encode
the accepted implementation decision with the existing node `purpose`, `role`,
`trigger`, `relationship`, and `presentation`, plus existing layout fields such
as padding, gap, alignment, sizing, overflow, and responsive rules.

A region that fails qualification remains subordinate even when it is visually
distinct. For example, a sparse vertical event/status rail beside a month grid
should not be a peer when it duplicates event facts, has no separate user task,
and cannot share the grid's temporal coordinates. Attach those facts to their
dates, expose them through selection, or use another subordinate presentation.

Component selection follows these affordances:

| Content need                                                                         | Preferred presentation |
| ------------------------------------------------------------------------------------ | ---------------------- |
| Standard action list, dropdown, or more actions                                      | `menu`                 |
| Nested branch inside an open menu                                                    | `submenu`              |
| Small custom anchor-relative panel or bubble                                         | `popup`                |
| Short blocking confirmation, warning, or acknowledge decision                        | `dialog`               |
| Larger modal settings, filter, export, selection, or short form task                 | `sheet`                |
| Date or deadline selection                                                           | `date-picker-dialog`   |
| Transient non-modal feedback such as saved/failed/undo                               | `snackbar`             |
| Lightweight persistent ornament attached around the main window                      | `augment`              |
| Long-lived selected-item detail, inspector, or reference panel tied to the main task | `subwindow`            |
| Independent workspace with its own lifecycle, placement, or launcher                 | `window`               |

`navigation` changes app/page routes. A `master-list` selects business objects
inside the current task; do not model object lists such as mail rows, photo
thumbnails, or catalog records as SideNavigation unless selecting them changes
the app/page route.

SideNavigationItem switches a distinct page or content context, such as a
collection, folder, channel, project, or playlist. During Plan, name each item's
destination and how its primary content, actions, or information organization
changes. Pages may share a layout template, but item selection must not merely
filter the current page by an attribute or change its selected styling. Keep
page-local filtering, sorting, and view-mode changes in page controls.

### Attached detail routing

Classify subordinate content before selecting its container. Brief contextual
content may use inline disclosure or a popup; persistent selection-derived
detail, inspectors, and reference information default to Subwindow. Selection
dependency and absence of an independent lifecycle support an attached
relationship and are not reasons to reject Subwindow. Inline detail needs a
positive rationale: simultaneous comparison, shared coordinates, or a concrete
interaction cost from separation. Independent lifecycle, launch, or placement
requirements distinguish a separate WindowContainer, not a Subwindow.

Subwindow belongs to a declared main window, not its body, list, or card. Plan
its shell to align with the main window's top and match its full height; body
padding affects only content inside the shell. Keep additional z offset at zero
(omit `offset-z` or set it to `0`) unless the original user explicitly requests
a depth offset; record that request in design-doc.md. Selection, focus,
hierarchy, or a spatial signature does not authorize extra depth.

Review the chosen relationship and, for attachments, placement, occlusion,
minimum size, reachability, and updates when selection changes.

A `domain_visual` node must provide `rendererKey`, `purpose`, and structured
`props`. It may have custom rendering code in `preview.html`, but all visible
content, input data, dimensions, colors, and interaction bindings still come
from the JSON. It must not be used to reimplement a button, field, selector,
menu, dialog, or other available `sui-*` control.

When a `domain_visual` contains a repeated or independently styled internal
region, it must declare a `parts` map for that region's base `appearance` and
state appearances. A part ID is local to its node: `month-grid.dayCell`
identifies the `dayCell` template inside `month-grid`, not one ID for each
runtime date cell. Omit `parts` when the visual has no such internal appearance
boundary. A transparent region still needs its part declaration when it is
repeated or independently styled. Trace each rendered template to a declared
part; a renderer loop does not substitute for that declaration. The static
checker warns when parts are absent, but rendered review must determine whether
omission is valid and detect omitted templates in partially declared maps.
Part appearances reuse the existing `fill`, `foreground`, `radiusDp`,
`opacity`, and `depthDp` fields; `fill` and `foreground` reference a native
color role or `theme.brandColors` token.

Repeated bounded cards, tiles, and cells normally declare a base
`appearance.fill`. A positive `radiusDp` normally accompanies that base fill so
the radius describes a visible surface rather than an accidental transparent
clip. Persistent interaction states such as `selected`, `active`, `focused`,
and `checked` normally declare their own state `fill`. Pure text, icon, media,
or intentionally transparent overlay parts do not need a fill.

```json
{
  "id": "month-grid",
  "kind": "domain_visual",
  "rendererKey": "month-grid",
  "purpose": "Show the month and its event density",
  "props": {},
  "parts": {
    "dayCell": {
      "appearance": {
        "fill": "fillSecondary",
        "foreground": "labelPrimary"
      },
      "states": {
        "selected": {
          "fill": "selectedDayFill",
          "depthDp": 18
        }
      }
    }
  }
}
```

## Icon assets

Choose icons only after component semantics are fixed. Follow
[`icon-selection.md`](./icon-selection.md) for source priority and catalog
search. A built-in component such as `sui-search-field` owns its semantic
affordance and does not need a separate magnifier asset.

Every `sui-icon` node must reference an `assets[]` entry with `kind: "icon"`
through `assetId`; the schema enforces this requirement. Components with an
explicit icon slot may also reference the icon asset on their node.

Use `icon70://7.0/<name>` for a bundled catalog selection. When no authoritative
or bundled asset accurately matches, use
`design-assets/icons/<resource-name>.svg` and draw that source during Build
according to
[`../../spatial-design-to-app/references/icon-drawing.md`](../../spatial-design-to-app/references/icon-drawing.md).
The accepted custom SVG is part of the design package. Preserve it unchanged
and follow the downstream [image and icon sources](../../spatial-design-to-app/references/preview-first-restoration.md#image-and-icon-sources).

Do not put emoji, Unicode symbols, icon font characters, raw SVG path data, or
filesystem-absolute paths in `content` or component props.

`layout` and `appearance` use PICO design units and tokens rather than arbitrary
CSS strings. The Web renderer converts dp to px for preview only. Downstream
Compose consumes the same numeric dp values directly. Volumetric dimensions
retain their declared dp or meter unit; any dp-to-meter conversion must use
`PhysicalLengthConverter`, never a fixed ratio. Meter dimensions remain meters
for Stage surfaces.

## Surface discipline

`layout` and `domain_visual` nodes are structural regions and must remain
transparent. Use spacing, alignment, typography, and hierarchy to separate
large primary content areas. A bounded content node becomes an app-authored
surface only when its `appearance` declares a non-empty `fill`.

An internal `domain_visual` part may declare a fill because it describes a
bounded element within the transparent visual, not the visual's root region.

- On one root-to-content path, at most one bounded content node may own an
  app-authored surface; its descendants remain transparent.
- `borderWidthDp` and `borderColor` are not part of node `appearance`.
  Standard SpatialUI controls may retain their library-owned boundaries and
  focus indicators.
- A Planar surface uses system Material.Regular by default. Optional
  `surface.windowBackground` is `material` or `transparent`; omission means
  `material`. Set `transparent` only for an explicit user request and preserve
  its quote or reference in `windowBackgroundEvidence`. Evidence is required
  only for transparent. These fields are not allowed on Volume/Stage surfaces.
  Transparency removes the material background, not the window container.
  This narrow configuration is restored to the Native window's material
  setting; Preview's outline/shadow are not app-authored design facts.
- `material` is not part of node `appearance`, and `rootMaterial` is not part
  of `theme`. Window and standard-component materials are system-owned runtime
  behavior; the surface-level transparency exception does not authorize
  custom materials, node fills, or simulated App backgrounds.
- `radiusDp` alone does not create a surface and is not counted as one.
- The system-provided window background is not represented in this contract and
  is not counted as an app-authored nested surface.

## Downstream handoff

`spatial-design-to-app` reads `design-spec.json` first:

- `surfaces` drives container/window evidence and constraints;
- `nodes` drives hierarchy, component-affordance metadata, and component conversion;
- `theme` drives `PicoTheme` and exact design colors;
- `initialStateId`, `states`, `transitions`, `actions`, and `dataCases` drive
  ViewModel/UI state;
- `responsiveRules` drives adaptive Compose layout;
- `assets` drives resource acquisition and attribution.

The downstream workflow may consult `preview.html` to understand the accepted
visual result, but it must not reverse-engineer implementation facts from HTML
or CSS when the JSON already owns them.

### TitleBar body spacing and ordinary rows

By default, TitleBar and body are adjacent children of an unpadded page column:
body top padding is 0dp and the TitleBar-to-body gap is 0dp. Do not recreate
that gap with parent `spacedBy`, Spacer, margin, translation, or outer padding.
Keep TitleBar's native internal spacing. Put module gaps inside the body only.
Record nonzero overrides only when the original requirement or authoritative
visual evidence explicitly calls for them.

Ordinary horizontal content rows (title plus button, text plus icon, label plus
control) default to vertical centering. Write `layout.align: "center"` in the
spec; Preview uses `align-items: center` and Compose uses
`Alignment.CenterVertically`. Explicit top/end or text-baseline alignment for
multiline content, unequal text sizes, or independent columns retains priority;
record that relationship instead of centering every structural row. Component-
owned slot alignment remains native unless an evidenced override is accepted.

Subwindow primary headings placed at the start of content default to `textRole: "surface_title"`
and `textStyle.typography: "headlineLarge"` (24sp / 30sp line height / 700 weight).
Choose one primary title and keep it larger than ordinary body and metadata.
Use another exact token only when the original user requirement or authoritative
visual evidence specifies it; record that evidence in the design document.
This default does not override TitleBar's inherited title typography except the primary-title weight 700. Compose
restores the accepted token without independently reducing its size.

### Subwindow header contract (spec gate)

Every `sui-subwindow` declares `props["title-position"]` (`titlebar` or
`content`) and `props["title-node-id"]` referencing its nonempty text title.
Missing declarations are errors; they
are not inferred from prose or silently treated as verified.

Encode exactly one independently owned `sui-title-bar` and one content layout
with `props.slot: "content"`. Layout wrappers are allowed, but shared ancestry,
cycles, or a nested Subwindow/dialog/Sheet/popup cannot provide the parent's
header or content. An optional bottom operation layout uses
`props.slot: "bottom-actions"`. These are spec region declarations, not new
Subwindow SDK parameters. For the web preview, the `content` and
`bottom-actions` region markers are consumed as design metadata: render those
wrappers in Subwindow's default slot without a DOM `slot` attribute, because
the web Subwindow component has only a default slot. TitleBar's `title`, `leading`, and
`trailing` slots remain real named slots.

Use the existing TitleBar slots: `props.slot: "title"`, `"leading"`, and
`"trailing"` on direct children of the bar; each slot can wrap composed content.
The bar declares the existing `title-alignment` value. With `title-position:
"titlebar"`, the referenced title belongs to its title slot and does not use
`surface_title`. With `title-position: "content"`, the referenced title is the
first item of content (transparent wrappers are allowed), declares
`surface_title` and an exact typography token, and the bar has no title slot.
Only this referenced content title may use `surface_title` in that Subwindow.
Do not declare a second window title in either region. This checks explicit
window-title declarations, not arbitrary unmarked duplicate prose.

Tag every back/close control with `props["navigation-action"]: "back"` or
`"close"`, regardless of its visible label. The gate requires such controls to
be `sui-icon-button` nodes in the owning bar's leading slot. It does not infer
navigation behavior from button text or action names. Slot `leading` maps to
Compose `leadingActions`; `trailing` maps to `trailingActions`.

A TitleBar may declare `props["subtitle-node-id"]` for its window subtitle.
When declared, this must reference a nonempty text node in its title slot,
including a composed title-group/search row. The copy-ownership review must
identify window-purpose text and declare it rather than leave it as an
unclassified body node.

TitleBar subtitles identified by `props["subtitle-node-id"]` are the canonical exception: declare `textStyle: { "typography": "bodyMedium", "color": "labelSecondary" }` on that text node, render it explicitly in Preview, and restore it as `Text(style = PicoTheme.typography.bodyMedium, color = PicoTheme.colorScheme.labelSecondary)` in Compose. Keep the existing title slot and composed title group; do not add a subtitle slot or infer subtitles by child order. This default needs no `styleOverrideEvidence`; other subtitle styles still require authoritative evidence.

Run schema validation and `check_design_surface_discipline.py` before freeze.
These structural violations are errors. Ordinary-content typography warnings
remain advisory. No new Compose position parser or implementation gate is
introduced by this contract. Consume `title-position`, `title-node-id`,
`subtitle-node-id`, and `navigation-action` as design directives; do not forward
them as invented Compose arguments.

### Explicit component defaults

Each ListItem declares `props["spacing-policy"]` as `canonical` or `explicit`.
Canonical internal padding is 16dp per edge; explicit mode requires
`props["internal-padding-dp"]` with numeric start/top/end/bottom. These component
props are distinct from the node's outer layout padding. Every TitleBar declares
`props["title-alignment"]` as `center` or `center-in-bar`. Missing declarations
produce advisory implementation warnings; enum and numeric schema validation
still checks supplied values. Record node-to-call anchors in source_mappings or
adjacent design-node comments so checks can compare actual code against spec.

### Component defaults and property-level overrides

SideNavigationItem defaults to a minimum height of 48dp, content padding of
start 16dp and top/end/bottom 8dp, and a parent-list gap of 4dp. Compose must
explicitly use `Modifier.heightIn(min = 48.dp)`; the Web item already has
`min-height:48px`. A gap or padding override never cancels the height default.
TitleBar primary-title text defaults to weight 700. Compose must explicitly use
`fontWeight = FontWeight.Bold` (import `androidx.compose.ui.text.font.FontWeight`),
since the SDK does not guarantee that weight. Keep its font family, size, line
height, and foreground inherited. Do not apply this weight to subtitles,
actions, SearchField text, or SideNavigation headers.

Only an original user requirement or authoritative Figma/screenshot evidence
can override a particular property. For a component-level height or weight
override, record `props["min-height-dp"]` or `props["title-font-weight"]` on the
owning component and `styleOverrideEvidence: { source, reference }` on that same
node. A fixed item height can instead use `layout.heightDp` with that evidence;
restore it with `Modifier.height(...)` and pass the same explicit height as the
Web item's `min-height-dp` attribute so its default minimum does not conflict.
Do not populate these override fields with inferred defaults. Other attributes
retain their defaults. Add `// design-node: <node-id>` immediately before the
corresponding Compose component when an override needs source/spec matching;
multiple state nodes may share a call only if their requirements agree.

The implementation scanner checks item height and primary-title weight
independently of spacing policy. Missing constraints or known incorrect values
fail. Dynamic values, opaque helpers, or ambiguous override correspondence are
unverified warnings requiring review, never verified evidence. Explicit
requirements are checked against their recorded value; unevidenced override
fields cannot exempt a default. Resolve these failures and warnings during
Compose review before claiming fidelity.

## Toolbar contract

Represent a Toolbar as a `spatialui` node with component `sui-toolbar`.
Use existing node props, children, visibility/state bindings, and actions; do
not add a parallel schema. Record its owning window ID in `props.for`, the
operation scope and single/main/supporting grouping rationale in design-doc.md,
and its page/selection/session visibility conditions in the existing state graph.

- Default children belong to native `content`; direct children with
  `props.slot: "supporting"` belong to `supportingContent`. A layout wrapper
  may group several children within a slot.
- `props.segmented: true` selects the configurable native overload, even with
  no supporting children. Omitted/false selects legacy `Toolbar { ... }`.
- Use `props["container-color"]` for the main segment background and
  `props["supporting-container-color"]` for the supporting segment background
  when the design requires an override. Otherwise keep the component defaults.
- Use the bundled Toolbar's default segment geometry. Do not introduce
  per-segment material, radius, padding, item-gap or minimum-width props that
  the Web runtime does not read. The
  [native Toolbar guide](../../spatial-design-to-app/references/spatial-windows-guide.md#82-toolbar)
  describes Compose configuration APIs; those native-only overrides are not
  verified by the current Web preview.
- Preserve `focusable` and native-only `followViewpoints` when specified.
  The static Web preview does not simulate viewpoint following.
- Configurable Toolbar centers its actual height on the owning window bottom
  edge (half overlap), with or without a supporting segment. Legacy Toolbar
  aligns its bottom to that edge then offsets downward by 32dp; do not conflate
  the overloads when content makes the bar taller than 64dp.
- Do not invent preview-only offsets as design facts to reposition a native
  Toolbar: its native attachment is system-owned. Keep the underlying content
  usable where the Toolbar overlaps the window.

Toolbar is a window attachment regardless of its declaration's nesting. In
Compose it may be declared inside a page Box/Column under WindowContainer; it
does not consume ordinary page layout space and needs no align, attach, or
register call. Its removal from composition removes the attachment. Shared
controls can be declared outside page switching; conditional controls use
conditional composition. Toolbar is not supported in Stage or ordinary Android
Compose without a spatial WindowContainer.
