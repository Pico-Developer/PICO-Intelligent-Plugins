# Design reference · Plan

Use this bundle to turn a page layout into a concrete design with components, icons and working Web examples. It brings together the reference component families, current usage guidance and working examples, with explicit additions for this Design-to-App chain.

## Start here

1. Use [general rules](general-rules.md) while completing the page design. Place copy with the subject it explains, merge repetition that adds no information, and give each piece of copy a concrete purpose. Implement Explore's navigation and task-tool decisions, including their scope and retained state. Resolve a missing or unsuitable structure in the design record before composing it; keep close and submit actions associated with their task.
2. Scan the [component overview](#components-in-this-system), compare candidates in [Choosing a component](#choosing-a-component), then read each selected family's README **and open its linked Preview in a browser**. Both are required: inspect the relevant complete composition and exercise its interactions, then read its markup/styles for slot usage, built-in insets and explicit overrides. Do not stop at the README or copy only an isolated control when the Preview provides the page composition you need. The family pages distinguish component defaults from explicit example choices.
3. Follow [Visual resources and examples](#visual-resources-and-examples) to actively choose icons and prepare suitable imagery. [Search the icon catalog](assets/icons/README.md), compare shapes in its visual browser, and use the same resources in Preview and handoff.
4. Record the actual chosen padding, spacing, title weight, icon and color decisions in Spec. A recommended value is not an implicit SDK default.

| Entry                                                             | Content                                                                                                       |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| [Component browser](index.html)                                   | 43 family pages: 42 reference families plus AttachmentPanel guidance and examples                             |
| [tokens.json](tokens.json) / [color-roles.json](color-roles.json) | Reference values and role mappings, with usage guidance                                                       |
| [General rules](general-rules.md)                                 | Content ownership and expression; cross-component navigation, actions, backgrounds, spacing and alignment     |
| [Motion](motion.md) / [Vibrant](vibrant.md)                       | Timing guidance and native/browser appearance differences                                                     |
| [Icons](assets/icons/README.md)                                   | 896 resources, English search, color usage and drawing rules                                                  |
| [Runtime](runtime/README.md#application-preview-windows)          | Loading the library, composing a window with external dimensions, customization attributes and preview limits |
| [Patterns](patterns/README.md)                                    | Placeholder for future complete app demos                                                                     |

Open `index.html` directly, or serve this folder:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory "/path/to/skill/design/design-reference"
```

Then open `http://127.0.0.1:8765/`. Component and icon previews share the same runtime. They need no build step, network font or external icon CDN. Prefer the local server for custom SVG `src` URLs.

Card remains outside this iteration. AttachmentPanel now has dedicated scene-panel guidance and examples. No full application pattern was imported.

## Visual resources and examples

Build visually rich designs with resources that help users recognize, browse and understand the content. App stores, media libraries and product browsing pages should actively use meaningful icons, covers, thumbnails or preview images to express their product type. Use icon-and-label compositions for navigation and suitable familiar actions, and give content objects recognizable visual identities. Choose resources for their purpose rather than filling an icon or image quota.

Use the existing Previews as working design references:

| Example                                                                     | What to inspect and try                                                                                                                                                          |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SideNavigation · sidebar and page](components/SideNavigation/preview.html) | Icon-and-label destinations, header slots and padding; switch destinations and observe the page title, content and content icon update together.                                 |
| [TitleBar compositions](components/TitleBar/preview.html)                   | Title, subtitle, icon actions and page search; inspect the appropriate composition and its slot ownership.                                                                       |
| [Sheet · Image sheet and edit form](components/Sheet/preview.html)          | Open the image sheet to inspect its full-color illustration; open the edit form for meaningful action icons and placement.                                                       |
| [Reading-list Preview](../spec-writing-reference/example/preview.html)      | Distinct book covers in the list; select different books to see the same artwork reused in the corresponding detail. Serve from the parent `design/` directory for this example. |

Adapt these patterns to the actual product, including their visual resources and interaction relationships. Example copy, artwork subjects and fixed dimensions are not universal defaults. Missing supplied imagery should lead to reusing, obtaining or creating suitable resources, not silently removing the image region or reducing the page to text. If a needed resource cannot be prepared, record that limitation explicitly.

System layout and material restraint does not require sparse content imagery. Application icons, covers, photographs and illustrations can retain their own palette; they are not extra structural background layers or automatically disposable decoration. Save reusable artwork and preserve its use in Preview and handoff through the [application visual asset guidance](runtime/README.md#application-visual-assets).

## Reference fundamentals

Spatial UI is a design language for windows floating in 3D space: translucent glass panels, black-on-light labels, a blue default interaction color, and rounded controls. It ships as a Compose module in the SDK. This system mirrors its tokens, defaults and glyphs; the components here are custom elements written from the Kotlin source, so sizes, colors and motion follow the SDK defaults.

## Content fundamentals

- Labels are short, sentence case, no trailing period: "Wi-Fi", "Connected to Office", "Done". Button text is a verb or a single noun.
- Address the wearer directly, second person, present tense. No emoji.
- Strings ship in 30+ locales (`values-*/strings.xml`), so leave room: Regular buttons grow from 81dp, never truncate a label.
- Name the action in dialog buttons ("Delete", not "OK") and the setting in a switch row ("Wi-Fi", not "Turn on Wi-Fi").

## Visual foundations

Use each component's documented defaults and apply Plan recommendations explicitly. For application-owned layout, text and content regions, use the selection guidance in [tokens](tokens.json); it does not replace component defaults.

**Choose a color role first.** Use [color roles](color-roles.json) to choose text, fill, state or semantic colors by purpose, then use the mapped token in Web. Record system color decisions by role/token name; do not copy their HEX values into page styles. Token definitions retain their actual color values. Deliberate brand/content colors use named application tokens, without redefining system roles.

For example, a local content tile can use `fillLight`, mapped to `fill-light-alpha`:

```css
.content-tile {
  background: var(--fill-light-alpha);
  color: var(--label-darkest-alpha); /* labelPrimary */
}
```

Choose a label role for text, a fill role for a deliberately filled surface, and `interaction`, `error`, `alert` or `passable` for the corresponding meaning. Existing controls keep their own foreground/background pairings and state handling. A role name such as `fillLight` is a design name, not a CSS color literal.

**Materials and fills.** Native window material responds to the spatial scene. Many default fills and labels use alpha whites and blacks; semantic colors and some content colors are opaque. Bounded content fills and the window material have different responsibilities.

- Ground: the window glass. Local items or cells can use `fillLight` (`fill-light-alpha`). Pages, bodies, columns, list organizers and large content sections must remain transparent; application-authored backgrounds must not nest. Preserve existing controls' fills, such as `fillTertiary` (`fill-neutral-alpha`) on inactive tracks. See the [calendar example](general-rules.md#backgrounds-and-colors).
- Text: `label-darkest-alpha` for primary, `label-ultradark-alpha` for titles, `label-semidark-alpha` for supporting text, `label-dark-alpha` for placeholders. On dark fills use `label-primary-light`.
- Action: `fill-darker-alpha` (#282828) with `label-primary-light` is the default primary button style. `semantic-interaction` (#3377ff) marks the _on_ state of switches, links and the coachmark. `semantic-error`, `semantic-alert`, `semantic-passable` are status only.
- Sub-palette (`sub-*`, each at 100/80/60/40%) is for content and 3D accents such as charts and avatars. Use supported component color overrides for intentional product themes. `sub-black-12` is the divider color.
- In the runtime, label and fill colors can be vibrant: they blend with the scene behind the window. The values here are the non-vibrant fallback (`defaultColorScheme`). See the Vibrant page (`vibrant.md`) for the levels, `withVibrant`, `vibrantColorScheme` and how the Playground approximates them.

**Shape.** Shape depends on the component. These are defaults, with overrides where its public API accepts them. Button radius by size: Max 32, Regular 102 (full pill), Small 20, Min 16. Text fields and options 12, list items and Min chips 16, Regular chips 38, side navigation items 24. Menus, dialogs and sheets 20; toolbars, the tab bar and single-line snackbars 32; coachmarks 8 (16 with an image).

**Spacing.** 8/12/16 gaps (`gap-small/medium/large`) between controls; 8/16/24/32 insets (`padding-*`). The size tokens include widths 160/240/320/360/400/480/600 (`width-*`) and height 184. They are reference values, not an exhaustive set of permitted application-window dimensions.

**Type.** One platform sans, five roles: Display (40/32/28, 700), Headline (24/20/16, 700), Title (20/16/14, 600), Body (16/14/12/10, 500), Label (14/12/11, 600). Multiline body variants add 4sp of leading. Sizes are in sp and map 1:1 to px here. The Kotlin module sets no custom font; this system's `sans` stack is a stand-in.

Choose type by the text's job: Display for a brief visual anchor, Headline for important section headings, Title for smaller headings, Body for descriptions and reading text, and Label for short functional labels. For paragraphs, use an existing multiline variant where available. These roles guide application-owned text; they do not replace a Button, TitleBar or other component's built-in text styles. Per-token usage is in [tokens.json](tokens.json).

**State.**

- Disabled: alpha 0.3 on the whole control.
- Hover: on a PICO device hover is the **native spatial hover effect** (gaze or ray), not a color. It is applied by `spatialHoverEffect` and the system draws it. Where the platform is not spatial, `PicoIndication` falls back to drawing 12% white (`0x1FFFFFFF`) for hover and for pressed. The web build here uses that fallback.
- ListItem in this bundle now includes a whole-row 12% Web hover approximation to match the current App restoration contract. Do not add another hover wrapper. Custom interactive regions use [spatialHoverEffect](runtime/README.md#spatialhovereffect).
- Pressed: `lightenPressed` (`state-lighten-pressed-alpha`, 12% white) drawn under the content, plus controller haptics. `Switch` and `ListItem` draw no pressed overlay.
- Focus: text fields use the `fillSecondary` fill; the web build adds a `semantic-interaction` outline for keyboard focus.
- Note `lightenHover` in the color scheme is `fill-semilight-alpha` (40% white). The Button family never draws it; do not use it as a hover color.

**Motion.** Springs for movement, cubic-beziers for fades; durations in `pico_sys_motion_*`. Springs (damping, stiffness): gradual 1/50, steady 1/450, rapid 1/850, instant 1/2500, snappy 0.75/150, fair 0.5/450, bouncy 0.35/550. Beziers: standard (0.3,0,0.2,1), decelerate (0.1,0.8,0.5,1), accelerate (0.15,0,0.5,0.2). Durations: short 120/180/240ms, medium 300/360/420ms, long 540/600/660/720ms. The switch thumb uses `rapid`, checkbox and chip fills use `instant`, tapping a slider uses `durationMedium1` with the standard curve. See `motion.md`.

## Vibrant

`Vibrant` (`foundation.vibrant`) asks the compositor to blend a color with the scene behind the window. `Modifier.vibrantEffect(vibrant)` applies it to a node and its children, `Color.withVibrant(vibrant)` encodes it in a color, and `vibrantColorScheme()` maps the roles to levels (`fillPrimary` Darker, `labelPrimary` Darkest, ...). It is on only on a spatial platform with the manifest flag `com.pico.spatial.ui.isVibrant` not false; otherwise `PicoTheme` uses `defaultColorScheme()`, which is what `runtime/tokens.css` and the web components draw. Details and the animation limits are in `vibrant.md` (the Vibrant page on the site).

## Iconography

Use the local [896-icon catalog](assets/icons/README.md) for all application icons. Search by English purpose/name, compare candidates in the [icon browser](assets/icons/preview.html), and use a stable ID when a name is ambiguous. Keep icon-bearing component examples as visual references. A missing asset is a reason to consult the [drawing rules](assets/icons/drawing.md), not to substitute an emoji or a letter.

The runtime resolves the full catalog and the short aliases used by the original previews. Independent icons have a primary-foreground default and accept explicit `tint`; icons in controls follow that control's content color unless overridden. All delivered assets are single-color. The original source pack remains untouched.

## Components in this system

Use this overview to learn what each family does, then use [Choosing a component](#choosing-a-component) to compare candidates. The component name opens its detailed guidance; Preview opens the working Web examples.

There are 43 family pages: 42 reference families plus AttachmentPanel guidance and examples. Related versions share one page: for example, AlertDialog includes BasicAlertDialog, and Sheet includes ordinary, header-image and BasicSheet versions. The versions column lists the main versions or compositions covered by each page; it is not a list of separate native APIs.

| Category               | Component family / guidance                               | Versions or examples on the page                 | Purpose                                                                                   | Web example                                         |
| ---------------------- | --------------------------------------------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Actions                | [Button](components/Button/README.md)                     | —                                                | Execute a one-time action such as Save, Delete or Continue.                               | [Preview](components/Button/preview.html)           |
| Actions                | [IconButton](components/IconButton/README.md)             | —                                                | Execute a familiar action through an icon, such as Close or Share.                        | [Preview](components/IconButton/preview.html)       |
| Actions                | [ToggleButton](components/ToggleButton/README.md)         | —                                                | Keep a tool function, such as Bold or Mute, enabled after a press.                        | [Preview](components/ToggleButton/preview.html)     |
| Actions                | [ToggleIconButton](components/ToggleIconButton/README.md) | —                                                | Represent a persistent tool state with an icon, such as Favorite or Mute.                 | [Preview](components/ToggleIconButton/preview.html) |
| Actions                | [Link](components/Link/README.md)                         | —                                                | Offer a lightweight action or destination beside text.                                    | [Preview](components/Link/preview.html)             |
| Selection and settings | [Switch](components/Switch/README.md)                     | —                                                | Turn an immediate setting on or off, such as Bluetooth.                                   | [Preview](components/Switch/preview.html)           |
| Selection and settings | [Checkbox](components/Checkbox/README.md)                 | Checkbox, TriStateCheckbox                       | Select independent items; use a mixed state for partially selected children.              | [Preview](components/Checkbox/preview.html)         |
| Selection and settings | [Option](components/Option/README.md)                     | —                                                | Present named choice tiles; the page manages single or multiple selection.                | [Preview](components/Option/preview.html)           |
| Content labels         | [Chip](components/Chip/README.md)                         | Basic Chip; text-only and icon examples          | Show a short tag or property near its content; the current preview uses read-only labels. | [Preview](components/Chip/preview.html)             |
| Input                  | [TextField](components/TextField/README.md)               | —                                                | Enter a single line of text, such as a name or title.                                     | [Preview](components/TextField/preview.html)        |
| Input                  | [TextArea](components/TextArea/README.md)                 | —                                                | Enter multiple lines, such as notes or a description.                                     | [Preview](components/TextArea/preview.html)         |
| Input                  | [SearchField](components/SearchField/README.md)           | —                                                | Enter a query to find or filter content.                                                  | [Preview](components/SearchField/preview.html)      |
| Input                  | [NumberField](components/NumberField/README.md)           | —                                                | Enter an exact number with typing and increment/decrement controls.                       | [Preview](components/NumberField/preview.html)      |
| Input                  | [Stepper](components/Stepper/README.md)                   | Minus/plus and arrow styles                      | Adjust a value in small steps; the page updates the value and range limits.               | [Preview](components/Stepper/preview.html)          |
| Input                  | [Slider](components/Slider/README.md)                     | —                                                | Adjust a continuous level, such as brightness.                                            | [Preview](components/Slider/preview.html)           |
| Input                  | [SymbolSlider](components/SymbolSlider/README.md)         | —                                                | Adjust a continuous level with an identifying icon, such as volume.                       | [Preview](components/SymbolSlider/preview.html)     |
| Input                  | [SegmentSlider](components/SegmentSlider/README.md)       | —                                                | Choose a level from an ordered set of discrete steps.                                     | [Preview](components/SegmentSlider/preview.html)    |
| Input                  | [DatePicker](components/DatePicker/README.md)             | Inline calendar; DatePickerDialog container      | Choose one date inline or in a separate confirmation dialog.                              | [Preview](components/DatePicker/preview.html)       |
| Input                  | [DateRangePicker](components/DateRangePicker/README.md)   | —                                                | Choose a start and end date for one period.                                               | [Preview](components/DateRangePicker/preview.html)  |
| Input                  | [Timepicker](components/Timepicker/README.md)             | Hour/minute/second columns                       | Choose a time or duration using labelled columns.                                         | [Preview](components/Timepicker/preview.html)       |
| Input                  | [WheelPicker](components/WheelPicker/README.md)           | —                                                | Choose a value from an ordered scrolling list.                                            | [Preview](components/WheelPicker/preview.html)      |
| Navigation and tools   | [TitleBar](components/TitleBar/README.md)                 | —                                                | Name a window and organize its window-level actions.                                      | [Preview](components/TitleBar/preview.html)         |
| Navigation and tools   | [TabBar](components/TabBar/README.md)                     | —                                                | Navigate between top-level app destinations above the window.                             | [Preview](components/TabBar/preview.html)           |
| Navigation and tools   | [SideNavigation](components/SideNavigation/README.md)     | Items and sections                               | Navigate between destinations in a vertical, optionally grouped list.                     | [Preview](components/SideNavigation/preview.html)   |
| Navigation and tools   | [Toolbar](components/Toolbar/README.md)                   | Main and supporting tool groups                  | Keep tools for the current task available beside the window.                              | [Preview](components/Toolbar/preview.html)          |
| Navigation and tools   | [SegmentControl](components/SegmentControl/README.md)     | Segments, including icon compositions            | Switch between sibling views of the same content.                                         | [Preview](components/SegmentControl/preview.html)   |
| Navigation and tools   | [PageControl](components/PageControl/README.md)           | Page-position styles                             | Show or control the position within a short series of pages.                              | [Preview](components/PageControl/preview.html)      |
| Feedback               | [Badge](components/Badge/README.md)                       | DotBadge, NumberBadge, text Badge                | Attach a small change mark, count or status label to its subject.                         | [Preview](components/Badge/preview.html)            |
| Feedback               | [CircularProgress](components/CircularProgress/README.md) | Determinate, indeterminate, symbolic             | Show compact known progress or a spinning wait indicator.                                 | [Preview](components/CircularProgress/preview.html) |
| Feedback               | [LinearProgress](components/LinearProgress/README.md)     | Small and Regular                                | Show a known completion fraction along a horizontal bar.                                  | [Preview](components/LinearProgress/preview.html)   |
| Feedback               | [Snackbar](components/Snackbar/README.md)                 | Message, optional icon and action                | Briefly report an operation result, optionally with one follow-up action.                 | [Preview](components/Snackbar/preview.html)         |
| Feedback               | [Coachmark](components/Coachmark/README.md)               | Simple, Rich and Image                           | Introduce a feature with a hint pointing at its target.                                   | [Preview](components/Coachmark/preview.html)        |
| Position feedback      | [ScrollIndicator](components/ScrollIndicator/README.md)   | Vertical and horizontal                          | Show the position of scrollable content.                                                  | [Preview](components/ScrollIndicator/preview.html)  |
| Dialogs and panels     | [AlertDialog](components/AlertDialog/README.md)           | AlertDialog, BasicAlertDialog                    | Present a decision or confirmation; Basic supplies the surface for caller-owned content.  | [Preview](components/AlertDialog/preview.html)      |
| Dialogs and panels     | [Sheet](components/Sheet/README.md)                       | Sheet, HeadImageSheet, BasicSheet                | Host a short task or form, with standard, header-image or caller-owned content layouts.   | [Preview](components/Sheet/preview.html)            |
| Dialogs and panels     | [Menu](components/Menu/README.md)                         | Menu, SubMenu and item layouts                   | Show commands associated with a control, including nested commands.                       | [Preview](components/Menu/preview.html)             |
| Dialogs and panels     | [SpatialPopup](components/SpatialPopup/README.md)         | —                                                | Show contextual content anchored to a particular control.                                 | [Preview](components/SpatialPopup/preview.html)     |
| Dialogs and panels     | [Subwindow](components/Subwindow/README.md)               | Planar and Volume owner examples                 | Keep supplementary information or controls beside an owning window.                       | [Preview](components/Subwindow/preview.html)        |
| Scene attachments      | [AttachmentPanel](components/AttachmentPanel/README.md)   | Transparent and explicitly backed examples       | Place 2D labels or controls relative to a scene group, object or part.                    | [Preview](components/AttachmentPanel/preview.html)  |
| Basic display          | [Text](components/Text/README.md)                         | Typography roles                                 | Display text with an appropriate role, wrapping and alignment.                            | [Preview](components/Text/preview.html)             |
| Basic display          | [Icon](components/Icon/README.md)                         | Local icon catalog                               | Display a named icon with explicit size and optional tint.                                | [Preview](components/Icon/preview.html)             |
| Basic display          | [ListItem](components/ListItem/README.md)                 | Leading, headline, supporting and trailing slots | Compose a content or setting row with its related icons, text and controls.               | [Preview](components/ListItem/preview.html)         |
| Basic display          | [Divider](components/Divider/README.md)                   | Horizontal and vertical                          | Separate related regions inside a surface with a thin line.                               | [Preview](components/Divider/preview.html)          |

The Web examples use custom elements from `runtime/components.js`. Their supported attributes, events and explicit example overrides are documented on the family pages. Browser previews approximate some native behavior, including spatial placement and materials; see [runtime notes](runtime/README.md) and each affected family's limitations. Card and StereoImage are outside this bundle's current scope.

## Choosing a component

Start with the user's task, then compare the content, interaction and space available. These are selection recommendations; overlapping capabilities do not imply that only one component can implement a behavior. Follow the selected family's documented API and composition rules, and use [general rules](general-rules.md) for page layout and operation placement.

### Pick one, pick many, or switch

| The wearer needs to                              | Prefer                                                                                                       | Selection guidance                                                                                                                                                          |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Turn a setting on or off immediately             | [Switch](components/Switch/README.md)                                                                        | Name the setting, such as Bluetooth; a ListItem can hold the name and trailing switch.                                                                                      |
| Select independent items or a batch of choices   | [Checkbox](components/Checkbox/README.md)                                                                    | Pair the control with a clickable label. Use TriStateCheckbox for a parent with partially selected children; the page manages the relationship and submission behavior.     |
| Choose among a few large named options           | [Option](components/Option/README.md)                                                                        | Suitable for choices such as quality or mode. The page defines single/multiple selection and whether an empty selection is allowed.                                         |
| Keep a tool function enabled after a press       | [ToggleButton](components/ToggleButton/README.md), [ToggleIconButton](components/ToggleIconButton/README.md) | Use compact tools such as Bold or Mute. Keep the function name stable and show its current state through the component.                                                     |
| Switch between sibling views of the same content | [SegmentControl](components/SegmentControl/README.md)                                                        | For short view names such as Day / Week / Month or List / Grid; app destinations belong in TabBar or SideNavigation.                                                        |
| Read a short content tag or property             | [Chip](components/Chip/README.md)                                                                            | The current page covers basic Chip and read-only labels. A click callback must be explicitly supplied for an action; basic Chip has no built-in selection or removal state. |

ToggleButton and Option both support a selected state. Choose by purpose and presentation: a compact toolbar function versus a larger named candidate in a choice group. Single versus multiple selection alone does not distinguish them. ButtonChip, ToggleableChip and removable variants are outside the current Chip page's scope; its basic examples do not demonstrate those behaviors.

### Trigger an action

| The wearer needs to                                              | Prefer                                        | Selection guidance                                                                                                                                       |
| ---------------------------------------------------------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Execute a labelled action, such as Save, Delete or Continue      | [Button](components/Button/README.md)         | Choose size for the region and task. Buttons in the same action row keep the same size; secondary priority does not automatically mean a smaller button. |
| Execute a familiar icon-only action                              | [IconButton](components/IconButton/README.md) | Use an understandable symbol and an accessible name; add a text label when the meaning needs explanation.                                                |
| Follow a destination or perform a lightweight action beside text | [Link](components/Link/README.md)             | Keep the label meaningful in its text context.                                                                                                           |

Use [operation placement](general-rules.md#operation-placement) for where actions belong and [Button composition](components/Button/README.md#plan-composition-alignment-and-compact-widths) for right-aligned, shared-width or full-width layouts.

### Enter a value

| The value is                                  | Prefer                                                                                   | Selection guidance                                                                                        |
| --------------------------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| One line of text                              | [TextField](components/TextField/README.md)                                              | Keep a visible field name; use the placeholder for an example.                                            |
| Several lines of text                         | [TextArea](components/TextArea/README.md)                                                | Provide room appropriate to notes, messages or descriptions.                                              |
| A search query                                | [SearchField](components/SearchField/README.md)                                          | Make the search scope clear from its position and label.                                                  |
| An exact number, also adjusted in steps       | [NumberField](components/NumberField/README.md)                                          | Use when typing a precise value or showing a unit is important.                                           |
| A value adjusted mainly with small increments | [Stepper](components/Stepper/README.md)                                                  | The page updates the value and enables/disables the endpoints; show the relevant range.                   |
| A level on a continuous scale                 | [Slider](components/Slider/README.md), [SymbolSlider](components/SymbolSlider/README.md) | Use SymbolSlider when an icon identifies the quantity. Supply the setting name and meaningful range/unit. |
| One of a few ordered levels                   | [SegmentSlider](components/SegmentSlider/README.md)                                      | Map each position to a named level; use Option for separate named candidates without a scale.             |
| One date                                      | [DatePicker](components/DatePicker/README.md)                                            | Embed the calendar when space permits; use DatePickerDialog for a modal selection and confirmation flow.  |
| A start and end date for one period           | [DateRangePicker](components/DateRangePicker/README.md)                                  | Show both endpoints and keep their relationship clear.                                                    |
| A time or duration                            | [Timepicker](components/Timepicker/README.md)                                            | Label the columns and distinguish clock time from duration.                                               |
| A value from another ordered list             | [WheelPicker](components/WheelPicker/README.md)                                          | Keep entries concise and identify the field and units.                                                    |

### Interrupt, inform, point

| The wearer needs to                                   | Prefer                                                                                                                          | Selection guidance                                                                                                                                    |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Make a decision before continuing                     | [AlertDialog](components/AlertDialog/README.md)                                                                                 | Use explicit decision actions. BasicAlertDialog supplies only the modal surface; its caller must supply the complete content and exit actions.        |
| Complete a short task or form                         | [Sheet](components/Sheet/README.md)                                                                                             | Choose ordinary or header-image Sheet for their supplied structure. BasicSheet requires caller-owned layout and an explicit exit.                     |
| Pick a command associated with a control              | [Menu](components/Menu/README.md)                                                                                               | Use a command list; add SubMenu for a nested command group.                                                                                           |
| Inspect or adjust contextual content beside a control | [SpatialPopup](components/SpatialPopup/README.md)                                                                               | Associate it with its trigger. Suitable for file details or a compact volume control; it is not limited to menu commands.                             |
| Keep auxiliary content beside a main window           | [Subwindow](components/Subwindow/README.md)                                                                                     | A persistent companion owned by the window, such as an inspector or playback queue. Define its open and close actions.                                |
| See a brief operation result                          | [Snackbar](components/Snackbar/README.md)                                                                                       | Transient feedback with at most one follow-up action. The default duration is 3 seconds and can be configured.                                        |
| Notice an unread count or small change marker         | [Badge](components/Badge/README.md)                                                                                             | Attach the mark to its subject; the owning page determines when it is shown.                                                                          |
| Learn about a feature at its location                 | [Coachmark](components/Coachmark/README.md)                                                                                     | A targeted hint with an explicit dismissal; use Simple, Rich or Image according to the content.                                                       |
| Wait when the completion fraction is unknown          | [CircularProgress](components/CircularProgress/README.md) with `indeterminate`                                                  | Use the spinning mode when there is no meaningful percentage to report.                                                                               |
| Track a known completion fraction                     | [LinearProgress](components/LinearProgress/README.md), or determinate [CircularProgress](components/CircularProgress/README.md) | Use a bar for a task with a name and percentage; use a ring where space is compact. Match the visible status and percentage to the reported progress. |

Use each surface's documented exit behavior. A required decision, a temporary anchored popup and a persistent companion have different dismissal needs. Progress indicators report task state; the owning surface determines whether other interaction is blocked.

### Place information beside a 3D subject

Ordinary text and controls can be arranged directly in Volume content. Optionally use [Subwindow](components/Subwindow/README.md#beside-a-volume-window) for a separate companion beside the window. Use [AttachmentPanel](components/AttachmentPanel/README.md) for 2D content positioned within a SpatialView scene. AttachmentPanel is transparent by default; information and operation panels should explicitly add a Regular glass backing, while short readable labels may remain transparent.

### Navigate

| The structure is                                               | Prefer                                                  | Selection guidance                                                                                                                                                                     |
| -------------------------------------------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A handful of top-level destinations                            | [TabBar](components/TabBar/README.md)                   | Actively consider during Explore; up to seven stable items. Each destination can contain horizontal categories or a sidebar and its own page layout.                                   |
| Many or grouped destinations                                   | [SideNavigation](components/SideNavigation/README.md)   | Use a vertical destination list with sections when grouping helps.                                                                                                                     |
| Sibling views of the same content                              | [SegmentControl](components/SegmentControl/README.md)   | Change the view of one collection, rather than navigate to a different app destination.                                                                                                |
| A window name and its window-level actions                     | [TitleBar](components/TitleBar/README.md)               | Use the documented title, subtitle, search and alignment compositions.                                                                                                                 |
| Operations on current content, selection, page task or session | [Toolbar](components/Toolbar/README.md)                 | Combine commands, modes, parameters and concise task information. Follow Explore's [task-tool decision](../layout-2d.md#task-tools-and-toolbar); main destinations stay in navigation. |
| Position within a short series of pages                        | [PageControl](components/PageControl/README.md)         | Use for a carousel or onboarding pages.                                                                                                                                                |
| Position within scrolling content                              | [ScrollIndicator](components/ScrollIndicator/README.md) | Bind it to the scrolling region; page dots and task progress serve different purposes.                                                                                                 |

## Using this system

**Designing or prototyping in HTML.** Load `runtime/tokens.css` and `runtime/components.js`, put the screen on a bright backdrop so the glass reads, then compose the `<sui-*>` elements shown in each component preview; each component's README lists its attributes and events. Use tokens such as `var(--fill-light-alpha)` for system roles. Declare named app tokens for a custom theme. Use a supported component color parameter or an application-owned token for intentional overrides; keep system-role values unchanged for ordinary layouts.

**Writing Compose in SpatialSDK.** The runtime already applies these tokens. Wrap the screen in `PicoTheme { ... }` and read roles, not hex: `PicoTheme.colorScheme.labelPrimary`, `PicoTheme.typography.titleMedium`. Use the components (`Button`, `Switch`, `ListItem`...) with their `*Defaults` sizes (`ButtonDefaults.Regular`). Override with `colors = ButtonDefaults.buttonColors(containerColor = ...)` only for a stated reason. Spacing and radii come from `DimensionTokens` (`GapLarge`, `RadiusLarge`).

**Mapping.** `fill-darker-alpha` = `colorScheme.fillPrimary`, `fill-semilight-alpha` = `fillSecondary` (and `lightenHover`), `fill-neutral-alpha` = `fillTertiary`, `fill-light-alpha` = `fillLight`, `label-darkest-alpha` = `labelPrimary`, `label-ultradark-alpha` = `labelSecondary`, `label-semidark-alpha` = `labelTertiary`, `label-dark-alpha` = `labelQuaternary`, `label-primary-light` = `labelPrimaryLight`, `state-lighten-pressed-alpha` = `lightenPressed`, `semantic-*` = `error`, `alert`, `passable`, `interaction`, and `sub-black-12` = `dividerLine`.

**Design recommendations.** Give each task a clear primary action. Use Switch for immediate settings and Checkbox for batch choices. ListItem’s 360dp width is a default; adapt layout through supported parameters. Confirm consequential destructive actions with an explicit verb and provide recovery where possible.

**Window material.** Dialogs, sheets, menus, the toolbar and snackbar are rendered by the system with a window material (Regular, Thick, Thickest). The web build approximates them with a blurred translucent fill and a soft shadow.

See [runtime notes](runtime/README.md) for known browser/native differences.

## Source

Reference repository: AutoEva_SpatialDesignSystem, commit `4b664e88ab230737e450deb1c5564f1fdf034dee`. Added recommendations come from the current Design-to-App design/Compose guidance and this discussion. See [runtime notes](runtime/README.md) for the adaptation record and [upstream notice](runtime/UPSTREAM-NOTICE.md).

## 3D content in Preview

When a design contains 3D models or scene attachments, read [3D Preview authoring](3d-preview.md) before composing the page. It covers simplified placeholders and design notes for behavior that Web cannot simulate.
