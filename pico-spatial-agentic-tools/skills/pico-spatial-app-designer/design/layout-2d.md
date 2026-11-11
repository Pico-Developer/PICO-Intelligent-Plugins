# 2D Page Layout and Window Sizing Guide

## 1. Purpose and Scope

Use this guide during Explore, after Frame has established the content form and container. Determine the window dimensions, page regions, content arrangement, navigation structure, and placement of supporting information.

Design for a chosen, fixed window size. Layout changes caused by window resizing are outside the scope of this guide.

Explore establishes the page structure and relationships. Consider whether TabBar or Toolbar fits the task before arranging the page body. Plan selects concrete controls and specifies exact padding, spacing, typography, icons, and visual details.

## 2. Window Dimensions

Determine the window width, height, and unit from the content that users need to see at the same time.

The following dimensions are initial design candidates, not mandatory SDK size classes:

| Suggested Size    | Suitable Uses                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| **800 × 600 dp**  | Single-column settings, forms, articles, and simple detail pages.                              |
| **1280 × 720 dp** | Categories with content, lists with details, and typical product browsing.                     |
| **1600 × 900 dp** | Information-rich split layouts, comparisons, and large images displayed alongside information. |

Apply these principles:

- Choose dimensions based on the regions needed for the task, considering the main pages that share the window.
- Use scrolling for long lists and documents. Total content length does not directly determine window size.
- Increase the window area when multiple regions genuinely need to remain visible together.
- Pages within the same window use the selected dimensions, with their own internal layouts.
- Describe a TabBar above the window and attached panels beside it separately. Their space is not part of the main window's internal layout.
- Record dimensions with explicit units.

## 3. Common Page Layout Patterns

Select a pattern based on the task and content. Patterns can be combined.

| Pattern                                            | Suitable Tasks                                                                            | Example Region Arrangement                                                                                                                                                                       |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Title and single content region**                | Settings, forms, articles, and simple details.                                            | Place the title above the main content. When no title is needed, let the content occupy the page directly.                                                                                       |
| **Categories on the left, content on the right**   | Product browsing, resource libraries, and feature entry points.                           | Use a narrower category region and a larger content region. In a 1280 dp window, approximately 240 dp can be an initial allocation for categories.                                               |
| **List on the left, primary content on the right** | Browsing documents or images where reading or viewing the selected item is the main task. | Keep the object list visible beside the main content. In a 1280 dp window, approximately 360 dp can be an initial allocation for the list. Auxiliary properties and inspectors follow Section 6. |
| **Side-by-side content**                           | Comparing two objects or their properties.                                                | Usually allocate equal widths and arrange corresponding information in the same order.                                                                                                           |
| **Tools above, content below**                     | Search results, filtered lists, and resource grids.                                       | Place search, filtering, or sorting above the content they affect.                                                                                                                               |

Region dimensions are design targets. Plan resolves exact usable widths using the applicable padding and component specifications.

Additional rules:

- A category region may contain categories, a directory, or navigation. Name it according to its actual role.
- A list containing summaries or status information needs more width than a region containing only short category names.
- A title can belong to the whole page or to an individual pane.
- Combine patterns when useful. For example, the right side of a category-and-content layout may contain tools above a product grid.
- Titles, sidebars, and tool regions are optional. Include them when the task needs them.

## 4. Navigation and Content Switching

Use the page relationships to determine the main destinations and local content changes.

Actively consider TabBar for a small set of stable main destinations that users revisit, and describe which destinations it switches between. Many or deeply grouped destinations may suit a side region; a single-task window may not need main-destination switching.

| Form                                                   | Suitable Uses                                                                                 | Layout Rules                                                                                          |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **TabBar above the window**                            | An application has several primary destinations that users need to switch between frequently. | Place it above the main window, outside the internal page layout.                                     |
| **Categories, navigation, or a list in a side region** | Users need to retain their choices or context while viewing related content.                  | Use one region of a split layout. The selected item determines the content shown in the other region. |
| **In-page content switching**                          | A page contains related content sets, such as Installed and Not Installed.                    | Associate the switching area with the content it changes.                                             |
| **Return to the parent page**                          | Users enter a separate detail page from a browsing or list page.                              | Keep a discoverable return path to the parent page.                                                   |

When several navigation levels are present, give each a clear responsibility:

```text
Top TabBar          → Switch primary application destinations
Side navigation     → Switch pages within the current destination
Local switching     → Switch content sets within the current page
```

Combine these forms as needed; an application does not need all of them. TabBar does not prescribe the layout within a destination. Preserve a useful sidebar or object list; do not duplicate the same destination set in both the TabBar and sidebar.

For example, a store can keep one window-level TabBar while its destinations use different structures:

- **Browse:** in-page horizontal categories such as Recommended / Games / Apps, then type filters and a content grid.
- **My account:** left navigation such as App Management / Downloads / Subscriptions, with the selected page on the right. App Management can contain its own Installed / Not Installed switch.

The main Tab changes the destination; the sidebar changes a page within that destination; local categories and filters change their own content region. These in-page regions remain inside the main window. Describe any selections that need to persist on return as part of the page relationships. A navigation sidebar is primary page structure, not a subordinate detail panel.

## 5. Content Arrangement and Scrolling

Determine how each region presents its content and the order in which users read and act on it.

| Content Type                             | Suggested Arrangement     | What Explore Specifies                                                                                   |
| ---------------------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------- |
| Products, images, and resources          | Card grid.                | Information shown on each card, the relative emphasis of images and text, and the intended column count. |
| Records, files, and settings             | Vertical list.            | Primary information, supporting information, status, and actions for each item.                          |
| Parameters, properties, and explanations | Grouped information.      | Grouping, reading order, and the organization of labels and values.                                      |
| Information entry                        | Grouped form.             | Field order, grouping, and the location of submission actions.                                           |
| Object comparison                        | Aligned parallel content. | Corresponding fields appear in the same order to support comparison.                                     |

Place actions according to their scope:

- Put page-level actions near the page title.
- Put filtering, sorting, and batch actions near the list they affect.
- Put actions for an individual object within its item or detail view.
- For page-wide pending edits, consider the Toolbar described below. Form submission can remain at the end of the form or in a fixed action area when that association is clearer; avoid duplicating it in both places.

### Task tools and Toolbar

Actively consider a window-attached Toolbar for related operations on the current content, selected objects, a page-wide task or an ongoing session. It is especially useful when those operations need to remain available while content changes or scrolls. Describe its main operations and the content they affect within the corresponding page description, using the actual task to identify suitable uses:

| Task                                      | Operations a Toolbar may carry                                                            |
| ----------------------------------------- | ----------------------------------------------------------------------------------------- |
| Media playback                            | Play or pause, switch media, and adjust playback position or volume.                      |
| Content viewing and browsing              | Switch the current item or page, zoom or fit the view, and find content.                  |
| Editing                                   | Change editing tools or modes, modify the current object, undo or redo, and save changes. |
| 3D inspection or manipulation in a window | Move, rotate or scale the current model, inspect its parts, and reset the view.           |
| Selection and batch work                  | Apply actions to selected items and exit selection.                                       |
| Page-wide pending changes                 | Preview, apply or discard changes to the current page.                                    |

TabBar switches between a window's main destinations; Toolbar can change a tool or mode within the current task. Toolbar's scope follows the task: an editing Toolbar may act on the selected object, a selection Toolbar may appear only while items are selected, and a playback Toolbar may remain available across main destinations. Include these relationships in the page description when the task requires them.

Keep single-item operations such as Open or Update associated with the item. A page with immediate per-field updates may not need a Toolbar; a task with page-wide pending changes may benefit from one.

Specify scrolling by region:

- Long lists, grids, and documents scroll as needed.
- Titles, navigation, and frequently used actions may remain visible.
- The panes of a split layout can scroll independently.
- Prefer one main scrolling region for a continuous reading flow.

Explore describes region relationships, content order, and which areas remain fixed or scroll. Plan specifies component heights, exact spacing, and padding.

## 6. Supporting Information and Temporary Content

The main window carries the current primary task. Persistent panels that support that content, such as object properties, inspectors, supplementary details and reference information, belong in a [Subwindow](design-reference/components/Subwindow/README.md). Needing to see both at once is not a reason to place subordinate information beside the primary content as a peer column inside the main window. Selection dependence and a shared lifecycle are compatible with a Subwindow.

Distinguish primary task content from supporting panels before choosing a multi-column layout. Side-by-side primary views can share the main window; an auxiliary panel remains subordinate even when it is visually distinct or needs frequent interaction.

| Information Need                                                                                                          | Possible Layout                                                               | Spatial Relationship to Specify                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Persistent object properties, inspectors, supplementary details or reference information used alongside the main content. | A Subwindow beside the main window.                                           | It sits outside the main window's content area, belongs to that window, and updates with the relevant object or selection. |
| A brief label or explanation belonging to an item or control.                                                             | Inline content beside that item or control, or a temporary popup when needed. | Keep its local association clear; it is not a separate persistent panel.                                                   |
| Additional actions, a short task, or confirmation information.                                                            | A temporary popup or dialog.                                                  | Position it relative to its trigger or the page, keeping information needed to complete the task visible.                  |

**Incorrect example:** An image editor puts its canvas, selected-object property inspector and supplementary reference information into three peer columns inside the main window. These regions are not all primary task content.

**Correct example:** Keep the canvas in the main window. Put the property inspector and related supporting information in a Subwindow that updates with the current selection, allowing users to continue editing the canvas.

**Boundary:** Two images being compared side by side are both primary task content and can stay in the main window. Navigation, inline labels and brief explanations do not need separate windows. Use Subwindow for an actual persistent supporting panel, not for every element below the page title.

In the current design record, specify:

- What information appears and which page or object it belongs to.
- Where it opens and whether users can continue interacting with the main content.
- How it updates when the page or selected object changes.
- When it closes.

Use these distinctions during Explore to establish the window relationship; Plan selects the detailed components and layout within each window.

## 7. Combined Example and Explore Output

Examples should show how dimensions, layout, and content work together. A fixed per-page task table is not required.

An application-management interface could use this structure:

```text
Window
└─ Specify the main window width, height, and unit

Above the window
└─ TabBar: primary application destinations

Inside the main window
├─ Categories or navigation on the left
│  └─ App Management, Downloads, Subscription History, etc.
└─ Content on the right
   ├─ Title: App Management
   ├─ Content switching: Installed / Not Installed
   ├─ Update information and an Update All action
   └─ Application list
      ├─ Icon, name, version, storage usage, and other relevant information
      ├─ Open, Update, and More actions on the corresponding items
      └─ Vertical scrolling
```

Explore then specifies the destination relationships, how additional actions open, and which page states should be retained.

The resulting design record should make clear:

- The window dimensions.
- Which pages are needed and what each contains.
- The layout and approximate space allocation of each page.
- The navigation and content-switching structure.
- Which regions scroll and which remain visible.
- Any attached panels, expandable regions, or temporary popups.
- The page and content relationships required by the current application.

Plan uses this record to select components and implement the detailed padding, spacing, typography, icons, and visual treatment.
