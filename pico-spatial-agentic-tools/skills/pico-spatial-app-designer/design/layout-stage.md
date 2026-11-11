# Stage Scene Layout Guide

## 1. Purpose and References

Use this guide during Explore after Frame has selected Stage. Determine which models and environment resources the scene needs, and how its content relates to the user, the environment, and any independent windows. Carry forward Frame's task, primary role of 2D or 3D, and real or virtual environment intent.

This guide adds scene placement rules to the existing layout guides:

| Design Decision | Reference |
| --- | --- |
| Internal regions, navigation, lists, grids, forms, and scrolling within a 2D page or panel. | `layout-2d.md` |
| Model presentation dimensions, scale, model/panel arrangements, and `AttachmentPanel` placement and transform-following behavior. | `layout-mixed.md`, Sections 2 and 4 |
| Dimensions and internal layout of an independent Planar or Volume window used within Stage. | `layout-2d.md` and the applicable window sections of `layout-mixed.md` |
| Scene resources, placement references, environment relationships, initial viewing arrangements, and scene regions when needed. | This guide |

Stage can use independent Planar and Volume windows alongside objects placed directly in the scene. These are different hosting choices:

- **An independent Volume window within Stage:** specify its width, height, and depth, then allocate space for its contents using `layout-mixed.md`. Its contents remain subject to the window boundaries.
- **Models and panels placed directly in Stage:** specify their own dimensions, separation, and positions. There is no Volume container size to set unless a Volume window is actually used.

For example, a sofa placed directly on the room floor needs sofa dimensions and a placement agreement. A sofa displayed inside a Volume window needs both sofa presentation dimensions and Volume dimensions.

Explore records design and production agreements. Plan selects Preview details and records scene creation/modification requirements for Compose App to execute through the existing Editor workflow. Explore does not create the scene. Exact component padding, spacing, typography, and icons remain in Plan.

## 2. Determine Scene Content

Before arranging the scene, Explore determines what must be available or produced.

| Content | What to Specify |
| --- | --- |
| **Subject models** | Specific objects, quantities, appearance references, actual dimensions or presentation scale, and required changes such as material variants, movement, or part expansion. |
| **Environment resources** | Whether floors, walls, platforms, rooms, or other environment objects need to be created; their task purpose, appearance, dimensions or extent, and quantities where relevant. |
| **2D interfaces and independent windows** | The information, selection, and action interfaces needed for the task, and whether each belongs directly in the scene or in an independent window. |

Choose resources from the task:

- **Furniture placement in a real room:** provide the furniture model; the visible real room does not require a replacement room model.
- **A virtual furniture showroom:** identify the furniture and the floor, walls, display platforms, or other environment resources actually needed.
- **Assembly instruction:** identify the equipment, independently presented or manipulated parts, and the interfaces that explain the current task.

Using Stage does not require a complete virtual room, multiple display regions, or a panel for every object.

Record dimensions and units using `layout-mixed.md`, Section 2. Use the same record for the resource inventory and layout agreements. Specific asset files, import settings, material parameters, and production workflow details are resolved during Compose App and its Editor workflow, preserving the accepted design requirements.

## 3. Establish Placement References and Environment Relationships

Content within a window can be arranged relative to its page regions or container. Content placed directly in Stage needs an explicit placement reference.

| Scenario | Additional Placement Agreement |
| --- | --- |
| **Placement in a real environment** | Identify the selected location or surface, which point on the object aligns to it, and how the initial orientation is determined. |
| **Guidance around a real object** | Identify the equipment or part being described, where its instructions appear, and which working area must remain visible. |
| **Presentation in a virtual environment** | Identify the scene region and how objects align to its floor, walls, or platforms; arrange multiple regions only when the task needs them. |
| **A workspace in front of the user** | Specify placement relative to the user's initial position and viewing direction, and whether the arrangement subsequently stays fixed in the scene. |

Apply these rules:

- Name the reference for directions such as left, right, above, and in front. The user's right, the object's right, and the platform's right are not interchangeable.
- Give related content a shared placement reference, then use `layout-mixed.md`, Section 4, for the arrangement within that group.
- For real environments, the user may choose the actual position at runtime. Specify the placement rule rather than inventing a fixed room coordinate.
- Initial placement relative to the user does not imply continuous following. Use the attachment and transform-following rules in `layout-mixed.md` to describe subsequent behavior.
- Treat floor alignment, wall alignment, and correspondence to real equipment as design requirements. Real-world visibility alone does not establish these relationships; Plan resolves the positioning or tracking approach.
- Identify the environment relationships that must remain visible for the task. For furniture evaluation, preserve the view needed to compare the furniture with its surroundings; for equipment guidance, keep the relevant working area visible.
- Record the reference for spatial positions. Plan maps these agreements into the appropriate coordinate space; a scene-level placement description is not automatically an entity's local transform.

Example:

> Align the sofa's bottom center to the floor position selected by the user. Initially face the sofa toward the user. Place the product panel on the right relative to that initial viewing direction, using the model/panel arrangement rules in `layout-mixed.md`.

For a virtual showroom, the reference could instead be a platform center or a designated position in a display region. Specify only the environment relationships needed for the task.

## 4. Establish the Initial View and Any Scene Regions

### Initial View

On entry, or after the user places the content, specify:

- The direction in which the primary object or region appears.
- Which side of the subject provides its initial presentation.
- Where the controls needed to begin the task can be found.

When the user selects a real-world placement, describe the resulting viewing relationship rather than fixing all positions in advance.

Example:

> After placement, the user can see the furniture's main presentation side and locate the position-adjustment controls. Supporting information does not cover the surroundings needed to assess the placement.

Choose distances and heights according to object size, task, and viewing method. Stage has no universal window-size preset; any numerical scene example is a scenario-specific design choice.

### Additional Views and Regions, When Needed

| Task Need | Additional Layout Decision |
| --- | --- |
| **One viewing direction is sufficient** | Arrange the subject and necessary interfaces around that direction. |
| **Side or rear views are necessary** | Specify whether users rotate the object, move around it, or switch viewing positions. Reserve space according to the chosen approach. |
| **Several display regions are necessary** | Identify the initial region, the relative positions of other regions, and how users access them. |
| **Several objects must be compared** | Provide a viewing arrangement from which the relevant objects can be observed together. |

Do not add routes, multiple observation points, or display regions when the task does not require them.

Explore specifies the viewing and spatial requirements. Plan checks the simulated Preview and records unverified items. Compose App and its Editor workflow verify actual visibility, occlusion, and interaction usability after implementation.

### Record the Result

Add the applicable scene content, placement references, environment relationships, and viewing arrangements to the existing design record. Use an inventory, placement table, or scene sketch as needed; do not create duplicate inventories for each guide.

For a sofa in a real room, this record identifies the sofa resource, its dimensions, the selected-floor placement rule, initial orientation, and required view of the surroundings. Use `layout-mixed.md` for its panel dimensions and relative arrangement, and `layout-2d.md` for the panel's internal layout.

Record application-specific selection, control, opening, closing, and state-retention behavior alongside these agreements, using the content-relationship output in `layout-mixed.md`, Section 5. Static scenes do not require additional interaction merely to fill out the record.
