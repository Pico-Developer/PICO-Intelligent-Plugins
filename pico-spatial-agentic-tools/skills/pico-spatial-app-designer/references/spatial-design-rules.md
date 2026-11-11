# PICO Spatial Design Rules & Vocabulary

Two things live here: the **spatial-affordance vocabulary** you use to justify putting an app in space (and to pick its form and scale) in the Frame phase, and the **hard checks** the pre-build critique runs. The checks aren't bureaucracy — each one guards against a specific way spatial designs go generic or uncomfortable. They apply to any form: a Planar window of any size, a HUD/Augment widget, a Volumetric surface, or an immersive Stage.

## Spatial-affordance vocabulary

When you justify "why in space" in the Frame phase, go through these affordances task by task. For each core task, name which one earns the spatialization, then write the **2D counterfactual** — how you'd do the same task on a flat monitor, and why the spatial version is genuinely better. If a flat monitor does it just as well, don't spatialize that part. The strength and kind of affordance also picks the **form**: room-scale reading → large Planar; a glanceable persistent cue → small HUD/Augment; a 3D subject in the round → Volumetric; replacing the real world → Stage.

| Affordance        | It earns its keep when…                               | Example                                             |
| ----------------- | ----------------------------------------------------- | --------------------------------------------------- |
| **Direction**     | information belongs to a real bearing around the user | alerts anchored to the physical zone they came from |
| **Distance**      | importance maps to how close something is             | critical KPI pulled near, context pushed back       |
| **Scale**         | true size matters or a view needs to be room-sized    | a floor plan or timeline read at wall scale         |
| **Depth**         | focus-plus-context via layering beats tabs            | live feed in front, history stacked behind          |
| **Position**      | persistent placement builds spatial memory            | the same panel always at the user's right           |
| **Motion**        | movement conveys state change, not decoration         | a value physically sliding between zones            |
| **Body**          | reaching/turning is a natural, low-cost input         | grabbing a panel to compare side by side            |
| **Collaboration** | multiple people share one anchored surface            | a shared ops wall everyone sees identically         |
| **Simulation**    | a 3D subject must be inspected in the round           | a product or machine model beside its data          |
| **Time**          | change over time reads better spread in space         | a process laid out along a spatial track            |

The 2D counterfactual is the originality backbone: a spatial decision that can't beat its own flat-screen version isn't defensible.

## Padding

Choose app-authored content padding during **Plan**, before freezing the design
spec. These tokens describe content spacing; native components keep their own
internal padding.

| Token           |  dp | Default use                                                    |
| --------------- | --: | -------------------------------------------------------------- |
| Padding Small   |   8 | Small or compact app-authored controls, chips, and badges      |
| Padding Regular |  16 | Ordinary containers, cards, list items, and form groups        |
| Padding Medium  |  24 | Dialog content, information cards, and Sheet/coachmark content |
| Padding Large   |  32 | Window-to-content spacing and page-level reading regions       |

Main Planar windows and attached **Subwindows** default to Padding Large:
32dp at the left, right, and bottom of their body/content region. Attachment
and a smaller window size do not by themselves select a smaller padding token.
Below TitleBar, keep the existing 0dp body top padding and native header spacing.
Put the inset on a separate body child, not around the whole window, TitleBar,
or full-height SideNavigation. Bottom operations use the same 32dp horizontal
content guides; assign their bottom inset to the operation region when present.
Do not add another window inset to every nested card or ListItem.

This is a design default, not a numeric acceptance gate. Edge-to-edge maps or
media may need another treatment. Review the actual composition rather than
accepting a written exception as proof or shrinking padding automatically at a
compact breakpoint. Declare the chosen values in the spec; Preview and Compose
restore them without independently adding a second default. See
[Directional content padding](design-spec-contract.md#directional-content-padding)
for the body example and rendered review guidance.

## Gap and radius

For app-authored layout, choose sibling gaps from this reference. Explicit
accepted design values and native component internals retain their own metrics.
Uniformity means one choice per repeated group, not one gap for the whole app.

| Token       |  dp | Default use                                                          |
| ----------- | --: | -------------------------------------------------------------------- |
| Gap Min     |   4 | Strongly related text, icon/label, and compact inline information    |
| Gap Small   |   8 | Independent ListItems, small cards, or buttons in one repeated group |
| Gap Regular |  12 | Content and a same-row action, or information groups within an item  |
| Gap Medium  |  16 | Same-kind larger cards or modules                                    |
| Gap Large   |  20 | Separation between different modules                                 |

Independent ListItems default to 8dp between items. Joined/grouped native lists
keep their connection/separator treatment instead of acquiring 8dp gaps.
Repeated siblings use one gap; cross-column rows intended to align share that
gap. Nested text gaps, item gaps, and section gaps are distinct decisions.

Choose radii only for custom bounded content surfaces that already legitimately
own a fill. Native components and system window shells keep their library-owned
shapes. A structural Row/Column does not gain a background or radius merely
because it is custom.

| Token               |  dp | Reference use                                                 |
| ------------------- | --: | ------------------------------------------------------------- |
| Radius Extra Huge   |  32 | Window-scale contour reference; do not override native shells |
| Radius Huge         |  24 | Large decorative cards                                        |
| Radius Extra Large  |  20 | Custom floating content surfaces                              |
| Radius Large        |  16 | Lists and content cards                                       |
| Radius Medium Large |  12 | Small content cards                                           |
| Radius Medium       |   8 | Inner nested content surfaces                                 |
| Radius Small        |   4 | Small fields, approximately 12–40dp high                      |
| Radius Min          |   2 | Very small surfaces, approximately 12dp high                  |

When visible outer and inner surfaces follow the same inset contour, choose a
smaller inner radius and inspect their concentric appearance. Independent native
capsule buttons and circular controls keep their own shape semantics. This rule
does not authorize nested fills prohibited by the surface-discipline contract.

Padding ownership and existing visible-content-top alignment remain unchanged.
Do not infer a new blanket page inset or extra top padding below TitleBar from
these gap/radius defaults. Native-owned padding is not applied a second time.

## Copy ownership and window headers

Every piece of copy needs an information responsibility and a matching region.
Window-purpose copy belongs to the window subtitle; a section heading must lead
an actual section; instructions must relate to an operation or state. Avoid
unassigned standalone copy, repeated titles, and generated slogans or welcome
messages that add no useful information. Preserve supplied copy by correcting
its placement before considering deletion.

Counterexample: Spatial Shelf already has its name in TitleBar, but
“Find the next app for your space” appears as a standalone first body row followed directly
by categories and the app shelf. It describes the whole window, not a separate
section. Put it below Spatial Shelf inside the title group; start the body with
categories. Standalone section headings, empty-state messages, and instructions
remain valid when they have a specific responsibility.

Selection-derived detail uses one title to identify the selected object and
its content. Do not repeat the master's selection state or stack synonymous
section headings above the same detail. Counterexample: the calendar highlights
12, while its detail repeats “Selected date · 12”, “October 12”, and “Today's events”.
Good case: the calendar highlights 12; the detail TitleBar reads “October 12 · Events”
and the body starts directly with the agenda. Keep object identity needed to
understand the detail independently; remove redundant status explanations.

A title-plus-search composition uses the complete title group: primary title
and optional subtitle in a Column, then flexible space and SearchField in the
same title-slot Row. Search must not displace the subtitle into the body.
Preserve the existing TitleBar alignment policy and native primary-title font.

Every Subwindow has its own TitleBar, a content region, and an optional bottom
operation region. Back/close navigation uses an Icon Button in the leading
slot, with the icon matching its actual behavior. A short title stays in the
TitleBar title slot. A long title may move to the start of content, retaining
the TitleBar and avoiding a duplicate title there. Do not add top padding to
simulate a header or compensate for this move.

Use the existing alignment policy: Center for bars with actions or search,
CenterInBar for text-only bars, unless authoritative design evidence overrides
it. Do not introduce a new whole-window centering algorithm. A few lightweight
short-label operations may occupy trailing actions; primary or more involved
operations belong at the bottom. Word count alone does not decide importance:
“Install” can remain the bottom primary action. One bottom button fills available
width; two align to the end with a consistent gap and clear priority. Review
excess operations rather than packing every available region with buttons.

Sheet uses its native title, leadingAction, trailingAction, and bottom slots;
do not add a second TitleBar. Apply the Subwindow operation-placement rules
above to Sheet's native slots. Close/cancel belongs only in the top-left leading
Icon Button (cross for close, arrow for actual back navigation); do not repeat
cancel at the bottom. Save/confirm is task-dependent, not mandatory for every
Sheet. Keep ordinary form Sheet titles short in the native title slot, with
inherited typography; do not move them into content or grant a surface_title
size exemption.

When one container has multiple independent picker field groups, wrap each
label and its complete picker in a consistent fillLight background, with equal
insets and clear inter-group spacing. A single picker group needs no additional
background by default. Do not group individual hour/minute columns separately.
Declare field-group appearance in spec; do not add renderer-only backgrounds.

These copy, length, and operation-priority decisions require semantic review.
The spec gate checks declared structure and ownership, not the meaning of prose
or whether a title is visually too long. See the Subwindow header contract in
`design-spec-contract.md` for the deterministic checks.

## Header rows above repeated content

For column headings above cells, cards, or list columns (calendars, tables, and
boards), share column boundaries, widths, and gaps between the heading row and
the content below. By default, align the heading and its corresponding content
on the same visible start edge, centerline, or end edge. An explicit source or
intentional design may use different alignments; record that choice.

Start/end alignment includes nested content insets: a heading aligned to a
cell's outer edge does not align with text padded inside that cell. Matching
padding is useful only when the containers share the same origin and bounds.
Center alignment uses the same content reference area and centerline.

For example, in a two-column board with start-aligned headings and card text,
both rows share the two column tracks and gap. Give each heading the same
effective start inset as the text in its cards. For a centered variant, align
the headings and content to their column's shared centerline instead.

Record the alignment reference and effective insets in the design document,
and encode the resolved widths, padding, gaps, and alignment in the existing
`design-spec.json` layout fields before freeze. For `domain_visual` components,
expose internal heading/content regions as child nodes or through a declared
renderer contract when needed; do not leave the relation only in preview CSS.
Render the preview from those declarations, including explicit alignment rather
than browser defaults. Restore the same relationship in Compose and preserve
it when resizing. Do not add parallel schema fields for this guidance.

## Toolbar task operations

Evaluate a window-attached Toolbar when an operation group acts on the current
content, selection, page task, or ongoing session. Media controls, content
browsing tools, editing tools, selection actions, and page-wide commit/reset
are useful candidates. A Toolbar can help keep these operations reachable while
content is browsed or scrolled, or give a task a clear operation area. Choose it
when that relationship helps; it is not mandatory or automatically preferred.
It may belong to one page or appear only for a selection, rather than persist
across the entire app.

Keep controls tied to a particular field, setting, list item, or card near that
content when moving them would obscure their target or add visual travel.
Settings with immediate per-item updates usually stay inline; settings with a
page-wide pending edit state may benefit from Save/Discard in a Toolbar. Avoid
duplicated controls and do not invent features to fill a bar. Record a short
suitability rationale for task operation groups in design-doc.md.

For a chosen Toolbar, decide whether it needs one group or distinct main and
supporting groups. Keep closely related, sequential operations together. Use
supportingContent when a secondary operation group has a clear functional or
priority boundary; do not split merely by button count. Both groups can compose
buttons, mode selectors, and concise context/status needed for the task.

- Media example: current track and transport controls in the main group;
  volume, queue, and lyrics in the supporting group.
- Content browser example: previous/next and viewing/search tools in the main
  group; favorite and information actions in the supporting group.

These are grouping examples, not required features or fixed button sets. A
Segment Control inside Toolbar can select a tool or view. App-category routing
still normally belongs to TabBar or SideNavigation; previous/next content
commands are not app-category navigation. Follow the Toolbar contract for
preview/Compose overload selection and attachment geometry.

## Anti-patterns — design against these

- **Container alignment mistaken for content alignment.** Matching column tracks
  or outer bounds does not align the visible text, icons, or controls inside
  them. Corresponding headings and repeated content must use the intended
  visible edge, centerline, or baseline, accounting for nested padding and slot
  insets. Mixed start/center alignment without an explicit design rationale is
  a defect, not proof that the shared grid is correct.

- **Scaled-up phone panel** — a spatial surface is not a phone UI at 4×. Re-derive layout for a room-distance, wide-FOV, head-and-hand context (and, for a small widget, for a glanceable one-thing role).
- **Form-by-habit** — reaching for a big dashboard when the task is a glanceable cue, or a flat panel when a 3D subject wants Volumetric. Let the spatial justification pick the form and scale.
- **Widget wall** — a grid of tiles with no single primary focus and no decision the app drives. Lead with the app's one job.
- **Floating panels for atmosphere** — extra windows that add no task value cost comfort and clarity. Every surface earns its place.
- **Generic dark dashboard** — near-black background + one acid/teal accent + hairline rules is the AI default. If your palette isn't from the subject's world, it's a template.
- **Head-turn to read core content** — core content outside the 65°×40° clear-FOV zone. Sizing failure, not preference.
- **Room-occluding default** — an oversized initial window that blocks the environment and creates pressure.
- **Attachment reflex** — reaching for a Toolbar/TabBar/Subwindow/Augment/Popup by habit. Choose the carrier from the content relationship. Persistent subordinate detail defaults to Subwindow; use `design-spec-contract.md` → Attached detail routing to justify an inline exception.
- **Layout stuffing** — treating every secondary thing as another child of the
  main `Row` / `Grid` because there is horizontal space. Standard menus,
  transient feedback, modal tasks, auxiliary status, and selection-derived
  detail have different component affordances. Multiple inline columns are
  fine when they are same-level peer content for the primary task; do not use
  column count as a substitute for deciding whether the content belongs in
  `Menu`, `SpatialPopup`, `Sheet`, `AlertDialog`, `Snackbar`, `Augment`,
  `Subwindow`, or an independent WindowContainer.
- **Peer-region inflation** — promoting sparse, duplicated, subordinate, or
  coordinate-incompatible information into a peer rail or column. A narrow
  event/status strip beside a month grid does not become a valid peer merely
  because it is visually separate; when it repeats events, has no independent
  task, and cannot align to the grid's time coordinates, keep the information
  attached to the relevant dates or reveal it on demand.
- **Backdrop compensation** — adding a broad dark background, extra
  Material/backing layer, nested fill, or divider to make an unresolved layout
  feel organized. Repair hierarchy and geometry at their source.
- **Empty-space hierarchy** — using empty placeholders, unsupported fixed or
  minimum heights, or large blank areas to imply importance. Size regions from
  actual content; reserved media, preview, or interaction space needs a purpose
  and dimensions in the spec.
- **Domain reskin** — same layout and structure across domains, only copy/colors/icons swapped.
- **Static index-based depth** — assigning repeated list, table, or card items
  different Z offsets from array index or visual order (for example 12/6/0) to
  imply importance. List order is not priority evidence. Keep repeated items
  coplanar unless an explicit user requirement or domain/interaction state
  identifies a selected, focused, or prioritized item; prefer the native
  component state treatment before adding an external `zOffset`.
- **Surface nesting** — giving a region a fill and then wrapping its ordinary
  child rows, sections, or cards in more app-authored filled surfaces. Choose
  one owner on each root-to-content path: the region or its content items.
- **Decorative content borders** — adding an app-authored border to panels,
  sections, list rows, or cards merely to separate content. Use spacing,
  alignment, typography, or one intentional surface instead. Standard control
  internals and accessibility focus indicators are not app-authored borders.

## Major-region qualification

Before a rail, column, panel, or window becomes a peer region, evaluate all six
questions. Record the rationale in `design-doc.md`; encode the resulting
implementation facts with the existing `purpose`, `role`, `trigger`,
`relationship`, and `presentation` fields.

| Test                     | A peer region needs                                              | If it fails                                  |
| ------------------------ | ---------------------------------------------------------------- | -------------------------------------------- |
| Independent task         | A user goal or decision that can be named separately             | Keep it subordinate to the owning task       |
| Unique information       | Information not already legible in the primary view              | Remove duplication or use local annotation   |
| Lifecycle / interaction  | Its own persistent interaction or meaningful show/hide lifecycle | Use disclosure, popup, feedback, or metadata |
| Coordinate compatibility | A spatial or temporal axis that composes with adjacent content   | Attach data to the compatible owner instead  |
| Duplication test         | No competing representation of the same fact at the same level   | Keep one authoritative representation        |
| Delete test              | Removing it materially harms the primary task                    | Delete it when the task remains intact       |

Passing one test is not sufficient. The set must justify peer status as a
whole. A subordinate region may still be useful; it simply needs a subordinate
presentation. These peer tests do not require an attached Subwindow to have an
independent task or lifecycle. Follow `design-spec-contract.md` → Attached detail
routing for selection-derived detail and inspectors.

## Pre-build hard checks (critique gate)

Any of these sends you back to revise, not tune later:

1. **Fewer than three real alternatives** were compared, or the rejected ones have no recorded reason.
2. **A core task has no 2D counterfactual**, or the spatialization can't beat its flat version.
3. **A surface size was not internally validated** against content type, clear-FOV, readable/clickable floors, and default/min/max bounds, or a Planar window defaults to a fixed 1280×720 / 1600×900 without calibration. Keep the calculation out of the final design document; record only implementation-relevant dimensions.
4. **Core content falls outside the 65°×40° clear-FOV zone**, or hit target <56 dp / body <12 dp.
5. **An attachment** (TabBar, Toolbar, Subwindow, SpatialPopup, Augment, Sheet/Dialog) was added without comparing it against `None` / in-place control, or carries mismatched semantics (app-category routing presented as task tools in a Toolbar, tools in a TabBar, primary content in an Augment).
6. **A component affordance is flattened into layout**: a standard action menu,
   nested menu branch, anchor-relative custom popup, short blocking decision,
   larger modal task, date picker, transient feedback, persistent auxiliary
   ornament, selection-derived detail, inspector, reference panel, or
   independent workspace is represented only as ordinary primary page
   `Row` / `Grid` content without an explicit same-level peer-content rationale
   or the matching SpatialUI presentation.
7. **A proposed peer region fails major-region qualification**: it lacks an
   independent task, unique information, lifecycle/interaction, or compatible
   coordinates; duplicates the primary view; or can be deleted without harming
   the primary task.
8. **Domain-swap test fails** — changing the domain and colors would leave the design essentially unchanged.
9. **A core component has no data source or task**, or the layout has no derivation evidence.
10. **The app has no single primary focus** or drives no clear decision/task outcome.
11. **A `layout` or `domain_visual` node declares a fill, or a root-to-content
    path contains more than one app-authored fill.** Structural regions stay
    transparent; the system-provided window background does not count.
12. **A design node declares `borderWidthDp` or `borderColor`.** These fields
    are not part of the appearance contract; content boundaries must not be
    created with app-authored borders.
13. **A design declares `theme.rootMaterial` or `appearance.material`.** Material
    is system-owned runtime behavior, not an app-authored design fact.
14. **Repeated list, table, or card items receive different depth values from
    child order or array index without explicit user-required, domain-data, or
    interaction-state evidence.** Ordinary repeated content remains coplanar;
    visual order alone cannot create priority.
15. **Physical anchors, plane detection, or cross-session restoration to the
    same real-world position are paired with Shared Space or a non-Stage form.**
    These capabilities require Full Space + Stage.

## PICO color & glass (so the design survives code generation)

A spatial design must preserve SpatialUI's existing semantic color contract.
All 16 public `ColorScheme` roles, including `fill*`, `label*`, interaction,
status, hover/pressed, and divider roles, remain the same-name values from the
Vibrant system scheme. Do not replace, redefine, or color-match those roles.

Custom colors are allowed, but they live only as named `brandColors`. Use those
app-owned tokens directly for intentional brand or decorative treatment; never
write them into `PicoTheme.colorScheme`, `systemColorScheme(...).copy(...)`, or
the vendored SpatialUI token definitions. This keeps built-in components and
their adaptive contrast behavior intact while still allowing product identity.

Other rules:

- **Design premise — the window background is system-owned.** Load the vendored
  SpatialUI Web bundle first and keep its default `PicoTheme.install({
scheme: "system" })`. Do not encode `rootMaterial` or `appearance.material`,
  and do not replace the system surface with a fixed gray, opaque root, or
  independently authored blur recipe. The preview body uses `#DAD6D3` with no
  background image. A Planar main window uses the shared library shell with
  Material.Regular's `#CACACA` fallback and subtle outline/shadow. Only an
  explicit user request permits `surface.windowBackground: "transparent"`,
  with `windowBackgroundEvidence`. Volume/Stage gain no new shell requirement.
  Body color and shell effects are environment context, not business tokens.
- **The window root background is system-owned.** Never put a solid color /
  `fillPrimary` on the window root. `fill*` roles are only for bounded content
  nodes, not large layout or domain regions.
- **Status by more than color**: any color-coded status also needs a non-color
  cue (shape/icon) and a human-readable label.

> Color anti-patterns (part of the domain-swap check above): (1) scattering
> anonymous literals through product code; (2) replacing an existing SpatialUI
> role such as `fillPrimary` with a design color. Preserve native roles and
> express custom colors as clearly named app-owned tokens.

## Z-axis / depth layering (even inside Planar windows)

Spatial apps are not limited to flat 2D stacking — **Z-axis depth is available even inside a Planar WindowContainer**. Use it deliberately to express focus, priority, and physicality, not just as a CSS-style z-index for overlap fixes.

### Depth vocabulary & when to use it

| Concept                | Use for                                                                           | SDK modifier                                 | Typical value                   |
| ---------------------- | --------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------- |
| **Selection lift**     | Selected/focused card, hero, or item physically rises forward                     | `zOffset`                                    | 8–24 dp toward +Z               |
| **Hover feedback**     | Pointer/gaze hover makes an element pop slightly                                  | `zOffset { animate*AsState }`                | 2–6 dp toward +Z                |
| **Content thickness**  | Volumetric-looking tiles, buttons with physical presence                          | `depth`                                      | 4–12 dp                         |
| **3D layering**        | Floating labels, badge overhang that doesn't need sibling nesting (within reason) | `Box3D` + `zOffset`                          | keep within 640 dp total depth  |
| **Attached ornaments** | Tooltips, headers, or controls anchored to window corners/edges                   | `Augment(anchor = NormalizedPoint3D.*Front)` | use Augment, not manual zOffset |

Subwindow-specific default: do not add extra z depth unless the original user
explicitly requests it. The focus/selection vocabulary above does not authorize
a nonzero Subwindow offset. See design-spec-contract.md → Attached detail routing.

### Scope boundaries

| Scope                                 | Rule                                                                                                                                                      |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Window, dialog, sheet, popup          | Use the matching SpatialUI system component and let it own layer placement; do not recreate window-level hierarchy with manual item `zOffset` values.     |
| Built-in component interaction state  | Prefer the component's native selected/focused/hovered treatment. Add external depth only for an explicit state and after runtime compatibility is known. |
| Repeated list, table, or card content | Keep siblings coplanar by default. Never derive stepped depth from array index or visual order.                                                           |
| Custom domain visualization           | Use depth only when an explicit structure or domain/interaction state defines what moves forward and when.                                                |

### Rules of thumb

- **Depth follows explicit structure or state**: importance must already be
  established by a user requirement, domain data, or interaction state before
  depth is assigned. Physical nearness must never be used to invent importance.
- **Depth = priority signal, not decoration**: don't push random elements forward just because you can. A lift must communicate state change (selected / pressed / hovered).
- **Built-in component boundary**: do not add external static `zOffset` values
  to SpatialUI built-ins merely to make ordinary content feel spatial. Prefer
  the component's native state treatment.
- **Keep depth inside 640 dp** for content inside a Planar window — past that it clips.
- **Animate depth changes**: a selected item rising forward should animate (300–400 ms ease), not teleport.
- **Prefer Augment for persistent floating UI** (tooltip, toolbar, floating header) over in-layout zOffset — Augment is a real system window with proper layering and avoids clipping.
- **Sibling-first for overflow (2D)**: for badges/labels that only need to peek outside a rounded corner _within the same plane_, use sibling positioning (see below). Use Z-offset only when you genuinely want depth separation.

### PICO axis convention

When describing depth in design docs, use: **+X = right, +Y = up, +Z = toward the user** (forward). Receding = -Z.

## Component layout anti-patterns

- **Badge/label clipped by parent clip()**: When placing badges, tags, labels, notification dots, or floating indicators that should extend outside a rounded/shaped container (e.g. role tags on a card, unread dots on an avatar, corner ribbons), **use sibling positioning, not parent nesting**. Place the badge as a sibling Box in the same outer layout, positioned via `align(Alignment.TopEnd)` + offset, rather than nesting it inside the container Box that has `clip()` applied. A clipped parent will always cut off content that extends past its rounded corners.

  ```kotlin
  // ❌ Bad: badge inside clipped parent → gets cut off
  Box(Modifier.clip(RoundedCornerShape(16.dp)).background(...)) {
    CardContent()
    Badge(Modifier.align(Alignment.TopEnd).offset(x=4.dp)) // clipped!
  }

  // ✅ Good: sibling relationship in unclipped outer Box
  Box {
    Box(Modifier.clip(RoundedCornerShape(16.dp)).background(...)) {
      CardContent()
    }
    Badge(Modifier.align(Alignment.TopEnd).offset(x=4.dp, y=(-2).dp)) // visible
  }
  ```

- **Hardcoded corner clipping on outer containers**: The window itself has a fixed 32 dp corner radius; inner containers with their own `clip()` create nested rounded rectangles that can trap overflow content. Reserve clipping for content that genuinely needs to be masked (images, scrollable lists). Keep ordinary groups transparent and use spacing or alignment instead of adding an outline.

## Terminology boundary

Keep design facts in PICO **design** terminology, not downstream code enums:

- Use: Shared Space / Full Space; WindowContainer **Planar** / **Volumetric**; Stage Mixed / Progressive / Full.
- Don't use as design facts: `ON_PLAIN`, `IN_VOLUME`, `STAGE_MIXED`, `single_panel`, `window_plus_subwindow`. Those are downstream implementation enums owned by the code-generation skill, not this design package.
