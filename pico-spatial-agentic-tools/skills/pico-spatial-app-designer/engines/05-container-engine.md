# Container Engine

First choose `WindowContainer` or `Stage` based on the nature of the task, then independently complete the window attachment decisions. Container selection and attachment selection are two distinct problems.

## Space State Problem (Space State: Shared vs Full)

Container decisions must first land in a space state (fact source: PICO Developer Center "Understand Spatial Containers & Space States" and "Manage the Space State of Spatial Apps"). Space state is not an optional backdrop; it determines **which containers are allowed to appear** and **whether the space is exclusive**:

- **Shared Space**: multiple apps can coexist at the same time, supporting multi-app collaboration and content blending. **Only the Planar and Volumetric WindowContainer types are supported; Stage is not**. Apps that are primarily 2D / lightweight-3D panels and need to coexist with the system or other apps run here.
- **Full Space**: a single app exclusively occupies the current space. **As soon as the foreground app opens a Stage, the system switches to Full Space**, and the other apps' windows recede to the background; here 1 Stage plus multiple WindowContainers can be placed at the same time. Closing the Stage falls back to Shared Space.

Criteria:
- Choosing `Stage` = actively entering Full Space and occupying the space exclusively. This is a costly decision and must declare the entry value, the explicit entry action, and the stable exit (closing the Stage to fall back) path.
- If only 2D / lightweight-3D panels are needed and coexistence with the system / other apps is desired → stay in Shared Space and use a WindowContainer (Planar / Volumetric); do not open a Stage gratuitously just to be "more immersive".
- The container list must be a legal combination: no Stage may appear inside Shared Space; anything containing a Stage is declared as Full Space.

## Container Problem

- Familiar reading, comparison, input, and workflow tasks: evaluate WindowContainer first.
- Direction, distance, scale, position, bodily participation, or spatial simulation directly affect understanding: evaluate Stage / Spatial Entity.
- A Stage must have a clear entry value, entry action, and stable exit path.
- A Stage is a boundless "region" whose center lands **under the user's feet** and is dynamically positioned with the HMD (right-handed coordinate system); only a Stage can request higher interaction / perception permissions (hand pose, spatial anchor, plane detection, and other MR capabilities).
- Stages are tiered by `immersion`: Automatic (system-determined, currently defaults to Mixed) / Mixed (immersion=0, virtual objects overlaid on the real environment) / Progressive (0–100, adjustable by the user through system UI, defaults to 50) / Full (100, fully virtual, a pure black background when no skybox is configured). The chosen tier must be consistent with the task's immersion needs, and it must be declared that exiting returns to the windowed state.

## WindowContainer Form Problem (Form: Planar vs Volumetric)

After choosing a WindowContainer, its `form` must be determined (PICO OS 6 officially divides WindowContainer into Planar and Volumetric; fact source: PICO Developer Center "Understand Spatial Containers & Space States"):

- **Planar**: a "flat panel" with finite thickness. It carries traditional 2D interfaces (continuing Jetpack Compose + Spatial UI) and is the ideal starting point for a 2D App or for porting a mobile/desktop application to PICO OS 6; it can also display smaller 3D objects. Choose Planar when the app is primarily 2D reading / comparison / input / workflow. **The depth of a Planar is fixed at 640dp and is not configurable** (the depth parameter of `defaultSize` only takes effect for Volumetric); the default size example in the official docs is 1280×720×640dp.
- **Volumetric**: a "cuboid" whose size can be dynamically adjusted, occupying a larger spatial volume. It blends 2D and 3D content and carries the display and interaction of larger 3D objects. **It runs in Shared Space and can interact with other apps' windows**; scaling is **always uniform** (the non-uniform options of `ContainerResizeRestriction` only take effect for Planar); the official default size example is 1280×1280×1280dp. Choose Volumetric when significant 3D interaction is needed within the window boundary.
- **Boundary and clipping**: a WindowContainer has clear spatial boundaries (a Planar by default launches about **1.75 meters** in front of the user, its center aligned with the headset's orientation; when the user adjusts distance, Dynamic worldScale keeps the relative field-of-view occupancy constant), and content beyond the boundary is clipped. If 3D content exceeds the window boundary, switch to a Stage (boundless) rather than forcing it into a Volumetric.
- **Note**: "dynamically adjustable size" is a characteristic of the Volumetric WindowContainer; do not confuse it with an Augment attachment—what an Augment is free to change is its distance and orientation relative to the window, not its width/height dimensions.

## Window Attachment Problem

- Page/view navigation: evaluate TabBar.
- High-frequency commands or tool modes: evaluate Toolbar.
- A persistent side-by-side auxiliary workspace: evaluate Subwindow.
- Anchoring temporary content: evaluate SpatialPopup.
- Spatial semantics around the window: evaluate Augment.
- Focused confirmation or a short workflow: evaluate Sheet / Dialog.
- Instructional hints: evaluate Coachmark.
- No clear value: None.

Do not use "every project needs a Toolbar" or "every app defaults to a fixed-size window" as input assumptions.
