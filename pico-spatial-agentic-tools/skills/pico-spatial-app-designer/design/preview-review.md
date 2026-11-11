# Preview review

Assess whether the running Preview meets expectations for both content and layout. Evaluate content against the requirements and Explore record. Evaluate layout using screenshots of the running Preview, supported by source inspection or interaction when needed.

## Content meets expectations

Confirm that the Preview implements the page responsibilities, content inventory and relationships established by the requirements and Explore. The examples below illustrate how to judge a design; they do not prescribe a page structure or require all content to appear on the initial page.

For content ownership, repetition and copy purpose, see [general-rules.md](design-reference/general-rules.md#content-ownership-and-expression). For TitleBar composition, see the [TitleBar guide](design-reference/components/TitleBar/README.md#plan-composition-title-subtitle-and-page-search).

### Navigation and task tools are implemented

Use Explore's [navigation decisions](layout-2d.md#4-navigation-and-content-switching) and [Toolbar decisions](layout-2d.md#task-tools-and-toolbar) to review suitable opportunities and actual behavior:

- For a small set of stable main destinations, check that TabBar was actively considered. For related operations on the current content, selection, page task or ongoing session, check that Toolbar was actively considered. Resolve an omitted design decision; do not fail a design solely because a component is absent or judge it by component counts.
- Pages within TabBar destinations can retain horizontal categories, left/right layouts and local switching. Main tabs, sidebars and filters affect their intended regions without duplicating the same navigation. A navigation sidebar must not be moved away as though it were a supporting detail panel.
- Click main tabs, sidebar entries and local switches. Confirm that the main content changes and that returning retains selections as specified. Changing only a highlight, heading or explanatory sentence does not demonstrate a complete page transition.
- Toolbar text, mode selection, parameters and concise status match the current task. When the object or tool mode changes, action targets, enabled states and relevant parameters update together. Main and supporting groups follow functional relationships rather than a fixed number of icons.
- Enter or exit selection, create or apply changes, and switch main pages. Confirm that Toolbar appears, disappears or persists as specified. Parameters and commands must change content or task state; shared session tools must not reset unexpectedly on navigation.
- Item-level Open/Update actions retain clear targets. No features were added merely to fill a Toolbar, and the same operation group is not duplicated in the body and the Toolbar.

Review the affected scenarios and record the results. This check does not require every page to use both TabBar and Toolbar. Evaluate the visual composition against the component references and applicable SDK sizing, typography, spacing and configuration rules; working interactions alone do not establish design conformance.

### 1. Content is complete and accurate

- The main information and actions needed for the current task are present, rather than only page names or entry points.
- Supporting information, details and temporary content are available in their relevant scenarios.
- Titles, images, object information and status descriptions match the content currently displayed.
- Inspect icon references in the Preview source: names and IDs resolve through the runtime icon catalog, aliases or built-in glyphs, and custom resources exist and are connected to the intended component or slot. Cover standalone icons, icon buttons and icons within buttons, including disabled states and buttons with text. Correct missing references; when no suitable resource exists, create and connect one using the [icon drawing guide](design-reference/assets/icons/drawing.md). Visual inspection can reveal rendering problems, but does not replace reference validation.

For icon resource inspection, run this command from the Skill's `design/` directory:

```bash
python3 scripts/check_preview_icon_resources.py /path/to/preview.html
```

If the check fails, fix the references or add the missing custom resources, then rerun it. The script resolves icon names against the runtime actually referenced by the Preview and checks local files relative to the Preview's URL base, including `<base href>`. It does not resolve files relative to the command's working directory or search other directories for matching filenames. It checks static HTML references only. Icons created or changed dynamically by JavaScript still require source inspection; a passing static check does not validate those dynamic references.

**Problem:** A furniture detail view is required to show images, price, dimensions and color options, but contains only a name and introduction. Or the user selects the gray variant while the image and details still show the white variant.

**Acceptable:** The detail view shows images, price and color options, while dimensions can be expanded on demand. Information throughout the view refers to the same product and selected color.

### 2. Content hierarchy and disclosure are appropriate

- The main page is organized around the current task, with clear relationships among primary content, persistent supporting information and temporary content.
- Overviews, list summaries, object details and further settings have a clear hierarchy rather than being flattened into peer sections on the main page.
- Properties, inspectors and reference panels that persistently support the main task use Subwindow rather than squeezing into the main window as peer columns. Judge their role using the [supporting-information layout rules](layout-2d.md#6-supporting-information-and-temporary-content); needing simultaneous visibility alone does not justify placing them side by side inside the page.
- Deeper information appears through object selection, a detail view or expansion of the relevant region. Once shown, its owning object remains identifiable.
- Confirmations, short tasks and temporary settings appear after the relevant action, rather than staying expanded by default.
- Content that must be viewed or operated on together may appear simultaneously, with clear priority and ownership.

**Problem:** A spatial app store's browse page expands the full description, all screenshots, version history and permission details under every application. Summaries used for browsing and comparison are mixed with information intended for detailed inspection.

**Acceptable:** The app list retains icons, names, brief information and primary actions. Selecting an app opens its complete content in the appropriate detail dialog, supporting window or detail page, following Explore's design.

**Boundary:** A difference in content hierarchy does not automatically require hiding content. A file list and the selected file's preview, or image thumbnails and the main image, can jointly serve the current task. Not every page needs a detail dialog or supporting window.

### 3. Content ownership is clear

- Copy describing the purpose or scope of the entire window belongs with its title, rather than adding an extra body section without independent content.
- Section headings and descriptions correspond to actual sections.
- Object properties, instructions, status and feedback appear in the relevant region, making their subject and target clear.

**Problem: a spatial app store home page**

```plaintext
TitleBar
└─ Spatial App Store

Main content
├─ Find your next app for your space
├─ Categories: All / Games / Productivity
└─ App list
```

“Find your next app for your space” describes the whole window. It does not introduce a separate section, yet occupies its own first row in the body.

**Acceptable:**

```plaintext
TitleBar
├─ Title: Spatial App Store
└─ Subtitle: Find your next app for your space

Main content
├─ Categories: All / Games / Productivity
└─ App list
```

If the additional description is unnecessary, omit the subtitle.

**Boundary:** “This week's picks” should remain a body section heading when it introduces a group of recommended apps. “No favorites yet” belongs to the favorites region's empty state. “Drag the model to view the back” is an instruction for the model. Do not move all such content into TitleBar.

### 4. Repetition adds value

- Titles, descriptions, object identity and status do not repeat the same or nearly the same meaning in consecutive elements.
- Information repeated across regions adds detail, supports an action or provides context needed to understand each region independently.
- Necessary object identifiers, summaries and full details, and persistent navigation remain available.

**Problem:** After selecting the 12th in a calendar and opening its detail dialog, the dialog displays:

```plaintext
Selected date · 12
October 12
Daily schedule
...specific events...
```

Three successive labels repeat the same date and the purpose of its details, creating unnecessary hierarchy.

**Acceptable:**

```plaintext
Detail dialog title: October 12 · Schedule
Body: show the specific events directly
```

**Boundary:** The date can remain visible in both the calendar and the detail dialog so the dialog has a clear subject. A product name in a list and its detail title, or a list summary and a full description, may each serve a necessary purpose. Repeated wording alone does not establish a problem.

### 5. Content has a clear purpose

- Copy identifies objects, explains groups, describes state, guides actions or presents domain information.
- No generic slogans, welcomes or explanations were added automatically just to fill the page.
- Hints and status messages identify their subject; isolated labels such as “Normal” or “Completed” do not leave their meaning ambiguous.
- Design explanations, component names and implementation notes do not appear in the product interface unless they are part of the product content requested by the user.

**Problem:** A settings page adds “Make management more efficient” above its settings without conveying useful information. A device page shows “Normal” without indicating whether it describes connectivity, operation or another state.

**Acceptable:** Omit filler that conveys no information. Place status in the corresponding device region and state its actual meaning, such as “Connected.”

**Boundary:** Unclear content may be fixed by moving or clarifying it rather than deleting it. For user-provided copy, first correct its placement while preserving its meaning; retain explicitly requested brand expression.

## Layout meets expectations

### Evidence and scope

Open the running Preview and inspect screenshots before judging the layout checks below. Code, layout parameters or design descriptions alone do not establish that the layout meets expectations. Screenshots should cover the main pages and any detail dialogs, supporting regions or temporarily expanded content relevant to the assessment. The initial home-page view alone is insufficient to judge the whole Preview.

Review at the agreed design window size; window resizing is outside the current scope. Screenshots must show readable text, region boundaries and complete layout relationships. Retain the overall view when judging space allocation, ownership and spacing; use close-ups to supplement details. Capture detail dialogs and similar content while open. To judge their relationship to the main window, include the relevant main-window region in the screenshot.

For content that appears truncated, occluded or outside the visible region, inspect the corresponding Preview source to determine whether an effective scroll region or detail/expansion entry exists. Distinguish ordinary offscreen content and intentional omission from accidental clipping. Focus on important content with no access path and on obscured or clipped actions. Not every suspected truncation requires a scroll interaction, but `overflow: auto` alone does not prove reachability. Also inspect container dimensions, ancestor overflow and clipping constraints, space occupied by fixed regions, and the entry point's actual implementation. If the source is insufficient to establish reachability, perform the necessary interaction instead of marking the check as passed.

After layout changes, capture new screenshots of the affected pages or states. Do not mark views that were not inspected as passed.

### 1. Space allocation fits the task

- Primary regions receive space appropriate to the task and content volume; supporting regions do not crowd out primary content.
- No large empty areas lack a purpose, and one side is not conspicuously empty while the other is crowded.
- Regions with little content are not stretched without reason, separating related information unnecessarily.

**Problem:** A right-hand information region contains only two lines but occupies nearly half the window, leaving a very narrow product list on the left. Or a large gap separates the title from body content that is crowded against the bottom of the window.

**Acceptable:** Allocate space for the current task: the product list has enough room for browsing, supporting descriptions occupy an area suited to their content, and the title remains clearly associated with the body.

**Boundary:** Image display and model viewing or manipulation may need substantial space. Whitespace can also support reading. Judge empty space by its purpose and effect on other content, rather than trying to fill the page.

### 2. Regions and content ownership are visually clear

- Content regions are identifiable, with a clear visual relationship between primary and supporting content.
- Titles, descriptions, images and actions visibly belong to their region rather than floating between two groups.
- Content within a region forms a coherent group instead of being split apart by spacing or arrangement.

**Problem:** A “Recommended apps” heading sits between two app groups and is farther from the recommendations below, making it look like the end of the preceding list. Or action buttons sit between two content regions with no clear target.

**Acceptable:** The “Recommended apps” heading and its list form a clear group, separate from the preceding section. The action area is visually associated with the content it affects.

**Boundary:** Position, whitespace, alignment and heading hierarchy can distinguish regions; not every region needs a background, border or card. Content may belong to the correct region in the source while the rendered layout fails to communicate that relationship. That is still a layout problem.

### 3. Spacing communicates grouping

- Icons, text, descriptions and actions within an item remain associated, while different items are distinguishable.
- A module's heading and content are more closely associated with each other than with unrelated modules.
- Spacing among repeated items and similar modules is consistent, without isolated excessive or insufficient gaps.
- Accumulated nested padding does not make groups internally loose while crowding separate groups together.

**Problem:** A product image is far from its name, while that name sits immediately beside the next product's image. Or settings within a group have large gaps while two settings groups have almost no separation, reversing the apparent grouping.

**Acceptable:** Each product image and name are easily recognized as one item, with clear separation from adjacent products. Settings within a group form a continuous whole, with distinguishable gaps between groups.

**Boundary:** Smaller spacing within a region than between regions is a useful clue, not a requirement that every internal gap be smaller than every external gap. For example, an image viewing area and its controls may intentionally have space between them. The question is whether spacing implies the wrong grouping.

### 4. Corresponding content is aligned coherently

- Similar items, image/text combinations and action areas have no obvious edge drift or vertical misalignment.
- Headings and their content follow appropriate visible edges, centerlines or baselines; internal padding does not create unintended offsets.
- Adjacent regions intended to share an arrangement have coherent outer edges, without irregularities caused by omitted spacing.

**Problem:** A column heading aligns with a card's outer border, but the card's internal padding offsets the actual text. Or one large card and two smaller cards beside it align at the top but not at the bottom because the gap between the smaller cards was not included.

**Acceptable:** Column headings and their text share a visible starting edge. A large card and a small-card group intended to form one arrangement align at both top and bottom after accounting for the gap.

**Boundary:** Different regions need not all have equal width or height, and multiline text need not be mechanically centered against single-line text. Address obvious misalignment that breaks correspondence while retaining purposeful differences. A shared grid or aligned outer borders alone do not prove that visible content is aligned.

### 5. Content and actions are visible and reachable

- Information that must be read in full is not accidentally truncated, and containers do not clip icons, buttons or hints.
- Long content beyond the visible region has an effective scroll region or an expected entry to the complete content. Important content is not left unreachable.
- Dialogs, supporting regions and fixed action areas do not obscure information or the only action entry needed to complete the current task.

**Problem:** A detail dialog's body extends below its bottom without an effective scroll region, and its confirmation button is also clipped. Or a fixed Toolbar covers the last list item, with insufficient scroll range and bottom padding to reveal it fully.

**Acceptable:** Long text scrolls within a clear content region while required actions remain reachable. The fixed Toolbar and list leave enough room to view and operate on the final item. Assess suspected problems using the source-based evidence described above, with interaction checks when necessary.

**Boundary:** A list extending beyond the first screen is normal if it can be scrolled. A shortened summary with access to full details, or an image cropped as designed, is not automatically a problem. Distinguish intentional omission or cropping from important content that cannot be accessed.
