# Mixed 2D/3D Layout Guide

## 1. Purpose and Scope

Use this guide during Explore, after Frame has established the content form, the primary role of 2D or 3D content, and the container.

Determine:

- The dimensions of the content and, when using Planar or Volume, its window.
- The arrangement of 2D pages, panels, controls, and 3D subjects.
- Whether 2D content belongs to the page layout, is an attachment within 3D content, or appears outside an independent window.
- The scale, placement, alignment, and grouping agreements shared by interface and scene production.

| Scenario                                                         | What This Guide Covers                                                                                                                                                  |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Models embedded in Planar pages**                              | The model's region within the page and its relationship to information and controls.                                                                                    |
| **Mixed content in Volume**                                      | Container width, height, and depth based on the model, 2D interface, and required operations.                                                                           |
| **3D-only Volume**                                               | Presentation scale, object arrangement, and required space.                                                                                                             |
| **Independent Planar or Volume windows used within Stage**       | The internal layout of those windows.                                                                                                                                   |
| **Models and supporting 2D interfaces placed directly in Stage** | Object and panel dimensions, their relative arrangement, and attachment behavior. Stage placement references and environment relationships come from `layout-stage.md`. |

Use `layout-stage.md` to determine scene resources, placement references, relationships to the environment, initial viewing arrangements, and any scene regions. Apply this guide to the relative layout of each model and its supporting interfaces. Use `layout-2d.md` for the internal organization of 2D pages and panels, including lists, grids, forms, navigation, and scrolling.

Carry forward Frame's task and primary-role decisions. For example, if Frame selected a page-led experience with supporting model inspection, allocate the model's page region according to that purpose.

Explore establishes design agreements. Plan composes Preview and records pending resource and interaction requirements. Compose App creates and integrates final 3D resources through the existing Editor workflow, then verifies the implementation. Exact component padding, spacing, typography, and icons belong to Plan.

## 2. Window and Content Dimensions

Choose dimensions based on what users need to see at the same time. Describe the following separately:

| Object                   | What to Specify                                                                                                              |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **Window, when used**    | Planar width and height, or Volume width, height, and depth. This also applies to independent windows used within Stage.     |
| **2D regions**           | Target dimensions or proportions for information regions, selectors, and panels.                                             |
| **Model display region** | The width, height, and depth reserved for the model, together with fitting requirements.                                     |
| **3D object**            | Whether actual scale matters and whether the object is shown at original scale, reduced, enlarged, or fitted proportionally. |
| **Space for operations** | Required rotation, movement, scaling, expansion, or animation, and the space to reserve for them.                            |

Model dimensions, presentation scale, panel dimensions, units, and space for operations apply to both window content and content placed directly in Stage. Page-region constraints apply to Planar; Volume reference sizes and box-shaped space budgets apply to Volume.

When Stage uses an independent Volume window, specify both the window's width, height, and depth and the dimensions of its contents. When models and panels are placed directly in Stage, specify their own dimensions, separation, and positions; there is no Volume container size to set. Their combined spatial footprint helps arrange them relative to other scene content and does not define a clipping box.

### Models Embedded in Pages

Allocate the model region from the page layout before deciding how the model fits:

- A detail page may provide a large, dedicated preview region.
- A model within an article or card takes its dimensions from that local region.
- The model's shape, proportions, and intended viewing direction influence the allocation.
- Preserve object proportions when appearance or dimensions matter.
- Planar uses the system default depth. Consider that boundary when planning the model presentation and required operations.

Embedded models do not need to use the reference dimensions for standalone Volume windows.

### Standalone Volume

The subject, any 2D content inside the container, and required operations jointly determine the window dimensions.

| Reference Size, Width × Height × Depth | Possible Starting Use                                                 |
| -------------------------------------- | --------------------------------------------------------------------- |
| **0.6 × 0.6 × 0.6 m**                  | A compact single-object display with little internal 2D content.      |
| **1.0 × 1.0 × 1.0 m**                  | A subject display with space reserved for viewing and manipulation.   |
| **1.2 × 0.8 × 0.8 m**                  | A subject displayed beside an internal information or settings panel. |

The SDK contains a configuration example using a 0.6 m cube. The other dimensions are candidate design values for this guide. None are mandatory size classes, minimum sizes, SDK limits, or sizes validated for every object and interaction.

Use other dimensions when appropriate:

- Tall, narrow objects may need a taller, narrower volume.
- Objects that expand horizontally may need more width.
- A settings panel displayed beside the subject needs its own allocation.
- When comparing actual object sizes, specify whether the objects share a common presentation scale.
- Actual-size presentations should follow the object's dimensions and the task requirements.

Container dimensions, object dimensions, and reserved space are separate decisions. Do not assume that the model should fill the entire container.

### Dimensions and Units

- Use `dp` primarily for 2D windows, page regions, and ordinary panels.
- Describe an embedded model's 2D footprint in `dp` or as a proportion of its region.
- Volume dimensions may use `dp`; use meters when the design needs an explicit physical extent.
- Use meters for 3D asset dimensions and position agreements, and identify the reference object or coordinate space.
- Keep one authoritative unit for each dimension instead of maintaining two potentially inconsistent values.

The SDK's `WindowContainerSize` accepts both `Dp` and physical dimensions with a `LengthUnit`. Attachment sizing through `panelSize` also supports `dp` and meters. Plan uses the current UI context's conversion facilities when coordinating units; do not prescribe a universal fixed `dp`-to-meter ratio.

## 3. Layouts for Models Embedded in Pages

Use these patterns when users primarily browse, read, or select through a page, while a model helps them understand appearance, structure, or results.

| Pattern                              | Suitable Tasks                                  | Layout Guidance                                                                                |
| ------------------------------------ | ----------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Information and model preview**    | Product details and object introductions.       | Give information and the model separate regions, with explicit priority and width allocation.  |
| **Model above, information below**   | Appearance inspection and object introductions. | Concentrate the model presentation above descriptions, properties, and actions.                |
| **Selection list and model preview** | Choosing products, models, or alternatives.     | Keep the selection region visible and show the current object beside it.                       |
| **Model within an article**          | Tutorials and structural explanations.          | Place the model near its explanation and organize it within the reading sequence.              |
| **Model preview within a card**      | Browsing multiple objects.                      | Define the model footprint, summary information, and whether direct manipulation is available. |

For the selected pattern, specify:

- The model region's location and target dimensions or proportions.
- Which objects appear and how many are visible at once.
- Whether the model uses actual scale or a scaled presentation.
- Whether controls appear in the information region, near the model, or in an on-demand interface.
- Whether the model scrolls with the page or remains visible while information scrolls separately.

A model region may also contain 2D attachments, such as part labels, local information cards, or controls. These attachments and the model jointly occupy the region. Apply the attachment guidance in Section 4.

Use `layout-2d.md` for the page structure. Plan implements the detailed components, padding, spacing, typography, and icons.

## 4. Layouts for 3D Subjects with Supporting 2D Interfaces

Use these patterns when users primarily observe or manipulate a 3D subject and the 2D interface supplies tools, selection, settings, or explanations.

These patterns also apply to subjects and interfaces placed directly in Stage. Use `layout-stage.md` to establish where the group belongs in the scene, then use this section to arrange the content within that group.

| Pattern                                       | 2D Content                                                  | Layout Guidance                                                                                            |
| --------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Subject and compact action bar**            | A few frequent actions or panel entry points.               | Place it near the subject, usually in a horizontal arrangement, where it remains easy to find and operate. |
| **Subject and grouped toolbar**               | Editing, viewing, or manipulation tools.                    | Group tools by purpose and distinguish direct actions from controls that open more content.                |
| **Subject and information or settings panel** | Parameters, devices, properties, and explanations.          | Allocate a panel region and organize its content as grouped information, a list, or a form.                |
| **Selection panel and subject**               | Models, materials, alternatives, or parts.                  | Use a list, grid, or segmented control, with a clear relationship between the selection and the subject.   |
| **Object and local labels**                   | Part names, status, or brief explanations.                  | Keep labels concise and visibly associated with the corresponding object or part.                          |
| **Subject and on-demand panel**               | Detailed settings, supporting information, or a short task. | Open it from an identifiable entry point and retain the subject view needed for the task.                  |

Patterns can be combined. Specify actual content, such as “Expand, Reset, and Show Labels,” rather than only stating that a toolbar appears below the model.

### Decide Where the 2D Content Belongs

Volume does not require a Subwindow. Choose ordinary layout, a window companion, or a scene attachment according to the content relationship. These approaches can be combined:

```text
Volume window
├─ Window content: compose according to the task
│  ├─ Ordinary 2D layouts and controls (optional)
│  └─ SpatialView (when a 3D scene is needed)
│     ├─ Models
│     └─ AttachmentPanel (when 2D content belongs in the scene)
└─ Subwindow (optional companion attached to the window)
```

For equipment inspection, parameters can sit directly beside the model region in ordinary layout, or in a separate Subwindow. A temperature label placed above a sensor in the scene uses AttachmentPanel with an explicit spatial position or entity relationship. SpatialView hosts that scene; it is not necessarily a visible frame. An attachment need not rotate with the model: specify which group or part owns it and which transforms it follows.

AttachmentPanel is transparent by default. For an information or operation panel, explicitly add a Regular glass backing; short readable object labels may stay transparent. Preserve that choice in Preview and handoff. See [AttachmentPanel](design-reference/components/AttachmentPanel/README.md) and [Subwindow](design-reference/components/Subwindow/README.md#beside-a-volume-window).

Similar-looking arrangements can use different hosting approaches:

| Hosting Approach                               | Suitable Uses                                                             | Spatial Agreement                                                                                  |
| ---------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **A 2D region in the page**                    | Information or controls arranged alongside the model through page layout. | Specify the region, its dimensions, and its relationship to the model region.                      |
| **A 2D attachment within SpatialView**         | A panel, label, or action bar that forms part of the 3D content.          | Specify the attachment target, dimensions, placement, alignment, and transform-following behavior. |
| **An interface outside an independent window** | Supporting information beside the window or window-level navigation.      | Specify its placement relative to that window and its separate spatial footprint.                  |

“Place the panel to the right of the model” must also identify which hosting approach is intended.

The SDK's window-attached `TabBar`, `Toolbar`, and `Subwindow` require a `WindowContainer`. They can accompany an independent Planar or Volume window used within Stage. Apply the shared [navigation](layout-2d.md#4-navigation-and-content-switching) and [Toolbar decisions](layout-2d.md#task-tools-and-toolbar) to those windows during Explore, including model selection, manipulation modes and their parameters. A panel placed directly in the scene needs an explicit scene placement, for example through `AttachmentPanel`; Stage itself does not supply a main-window edge for these components.

### 2D Attachments within SpatialView

The SDK can use `AttachmentPanel` to add 2D content to the 3D entity structure. Design such attachments together with the model.

Specify:

- The information and controls displayed by the attachment.
- Whether it belongs to the display group, the whole model, or a particular part.
- Its target width and height, and its alignment reference, such as the center or an edge.
- Its position relative to the attachment target and its default orientation.
- How it responds when the object moves, rotates, or scales.

For example:

```text
Display group
├─ Model: rotates independently
└─ Control panel: remains stable relative to the display group
```

Or:

```text
Model part
└─ Name label: moves with the part
```

These arrangements express different behaviors. If the panel should keep facing the user, state that requirement explicitly; attaching it to a model does not itself specify that behavior.

Consider whether scaling the object should also scale the attachment's text and controls. Plan implements the entity hierarchy and transform behavior needed to satisfy the design.

For a group placed directly in Stage, use the scene placement reference from `layout-stage.md` and specify the attachment's position relative to that group or its objects. Positioning a group relative to the user's initial view does not imply that it continuously follows the user.

Use `layout-2d.md` for the attachment's internal lists, groups, and controls.

### Allocate Space According to the Hosting Approach

- Models, 2D attachments, and panels inside Volume share its available space.
- An attachment placed beside a model should not automatically be treated as content outside the window.
- Arrange interfaces outside the main window separately, with their own dimensions and positions.
- An embedded model region must accommodate both the model and its internal attachments.
- These window-boundary rules still apply to independent Planar and Volume windows used within Stage. For content placed directly in Stage, allocate room for the objects, attachments, separation, and required operations without imposing a Volume box around them.

Consider placement, orientation, and required operations as well as dimensions. If the model already fills a Volume, adding a panel beside it requires revisiting the allocation, presentation scale, or container dimensions.

Explore specifies reserved space and boundary requirements. After assets, panels, and interactions are implemented, Compose App verifies native clipping, occlusion, and usability; Plan checks only what its Preview actually simulates.

## 5. Examples and Required Outputs

The following examples illustrate the structure of a design record. Their dimensions and content serve their particular scenarios and are not universal requirements.

### Example A: A Furniture Detail Page in Planar

```text
Container
└─ Planar, 1280 × 720 dp

Page layout
├─ Top: Back control and product title
├─ Information region on the left
│  ├─ Name, price, and primary specifications
│  ├─ Color selection
│  └─ Favorite action
└─ Model preview region on the right
   ├─ Displays the current product
   ├─ Receives the main preview allocation
   └─ Fits the model proportionally, accounting for Planar's default depth

Presentation behavior
├─ Long information scrolls independently on the left
├─ The model remains visible and supports rotation
├─ Changing the color updates the model material
└─ Dimension details open on demand, with their hosting location specified
```

For the actual design, also specify the model region's dimensions or proportions, asset units, and initial orientation.

### Example B: A Model and Internal Parameter Panel in Volume

```text
Container
└─ Volume, 1.2 × 0.8 × 0.8 m

Space allocation
├─ Model region: reserve 0.6 × 0.6 × 0.6 m
├─ Parameter panel on the right: target width 0.35 m, height 0.5 m
└─ Remaining space accommodates separation and boundary clearance

Model
├─ Occupies the model region on the left
├─ Fits proportionally and initially presents its front
└─ Supports rotation for inspection

Parameter panel
├─ A 2D attachment within SpatialView
├─ Content: object name, grouped parameters, and Reset
├─ Located to the right of the model
├─ Vertically centered with the model region
├─ Faces the default viewing direction
└─ Remains stable while the model rotates independently

Content relationships
├─ Selecting another object updates the model and parameters
└─ Reset restores the model's default pose
```

The model region is a reserved space, not a requirement for the asset to fill that entire volume. Final fitting and interaction ranges are resolved during production.

### What Explore Delivers

Record the applicable information in the existing design record. A fixed task table for every page is not required.

| Design Object             | Required Information                                                                                                                                                                                                                                        |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hosting and container** | Identify direct Stage content or an independent window. For Planar or Volume, record container type, dimensions, and units. For direct Stage content, record scene placement according to `layout-stage.md` and the local model/interface arrangement here. |
| **2D content**            | The actual content, layout, and target dimensions of pages, panels, and action regions.                                                                                                                                                                     |
| **3D subjects**           | Objects, quantities, appearance references, grouping, and scale or fitting requirements.                                                                                                                                                                    |
| **Spatial agreements**    | Reserved space, placement, alignment reference, and orientation.                                                                                                                                                                                            |
| **2D attachments**        | Attachment target or reserved location, hosting approach, and transform-following behavior.                                                                                                                                                                 |
| **Content relationships** | Required opening, closing, selection, control, updates, and state retention.                                                                                                                                                                                |

Keep one shared design record. When using Stage, determine scene resources through `layout-stage.md` and add the relevant dimensions and interface relationships from this guide without duplicating the inventory.

Plan composes the interface Preview and model placeholders using the shared dimensions, placement and identifiers. Record pending 3D objects, attachment locations and capabilities for Write Spec. Compose App invokes Editor to produce missing resources and verifies the integrated presentation.
