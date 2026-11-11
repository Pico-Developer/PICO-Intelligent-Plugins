# Content Form and Container Selection Guide

## 1. Purpose and Decision Principles

Use this guide during Frame to select the content form, the primary role of 2D or 3D content, and the container. Base these decisions on the user's task, usage context, and the value of spatial presentation so that the resulting spatial form supports the intended experience.

The main focus is on 2D-only experiences and mixed 2D/3D experiences. Fully 3D experiences are also valid when the task calls for them.

### Make Design Decisions Proactively

Users do not need to provide a complete design brief or specify the content form, container, or exact dimensions. Frame should use the user's goal, available context, and this guide to develop a suitable design direction.

- Treat explicit user goals and constraints as decision inputs.
- Make design choices that can reasonably be inferred from the task and context, and briefly explain the rationale.
- When several options are viable, select the one that best serves the current task without adding unrelated product scope. The existence of alternatives is not, by itself, a reason to ask a question.
- Do not ask questions merely because model size, page layout, or container names are unspecified. Do not seek separate confirmation for hypothetical additional features.

### Ask Only When Necessary

Reason from the available context first. Ask a necessary question only when the core intent remains materially ambiguous and reasonable inference cannot produce a suitable design direction.

Ask about the user's task, such as, "Are you mainly evaluating furniture dimensions and placement, or visual style?" Do not require users to make a technical choice between Planar, Volume, and Stage.

The decision items in this guide describe Frame's reasoning and outputs. They are not a questionnaire that users must complete.

## 2. Decision Flow

Follow this reasoning path. Continue directly when the available information supports a suitable choice:

> User task → Spatial value → Content form and primary role → Spatial organization → Container selection

| Step | What Frame Determines |
| --- | --- |
| User task | What the user primarily wants to accomplish, including known goals and constraints. |
| Spatial value | How 3D presentation helps understanding, observation, or manipulation, and whether a flat presentation is already sufficient. |
| Content form and primary role | Whether the experience is 2D-only, mixed, or fully 3D; for mixed content, which form carries the core task and which supports it. |
| Spatial organization | Whether content belongs within a page, occupies a bounded volume, or is organized through relationships within an environment or scene. |
| Container selection | Which container fits the task and spatial organization, considering its size boundaries and space-state behavior. |

Asking the user is not a mandatory step. Different answers could lead to different designs, but that alone does not require clarification. First determine whether the current goal supports a reasonable recommendation.

## 3. Content Form Selection Rules

Content form determines how information and objects are presented. Establish the task value of 3D first, then decide the primary role of 2D or 3D content.

| Content Form | Selection Basis | Examples |
| --- | --- | --- |
| 2D only | A flat presentation sufficiently supports reading, searching, filtering, form entry, or comparing specifications. | Information lists, settings pages, and form tools. |
| Primarily 2D with supporting 3D | The main task follows a page flow; 3D supports understanding, inspection, or selection. | Browsing product information and rotating an embedded model to inspect its appearance. |
| Primarily 3D with supporting 2D | The main task centers on observing or manipulating spatial objects or scenes; 2D provides explanations, settings, and controls. | Inspecting mechanical structures, manipulating 3D exhibits, or arranging a spatial scene. |
| Fully 3D | The task is primarily accomplished through spatial objects or scenes, without a need for a flat interface. | Experiences centered on manipulating spatial objects, as required by the specific task. |

Apply these rules:

- Determine the primary role from the core task, not screen coverage, model size, or the number of controls.
- Give 3D a concrete purpose, such as viewing different sides, understanding structure, or evaluating spatial relationships. Do not add 3D simply because the application runs on a spatial device.
- Ordinary interface shadows, elevation, and layering effects do not automatically create a need for 3D objects.
- Select content form and container separately. Mixed 2D/3D content or primarily 3D content does not automatically imply a particular container.

## 4. Container Selection Rules

The container determines how content occupies space and how users work with it. Frame should decide whether content is best organized as a page, displayed within a bounded volume, or arranged as a spatial scene, then select a container using its size and space-state boundaries.

### 4.1 Container Selection Table

| Container | Selection Basis | Typical Examples | Size and Spatial Boundaries |
| --- | --- | --- | --- |
| **Planar: Page Window** | Content is primarily organized as a page. Text, buttons, and embedded models share the page layout, and the system default depth accommodates the intended presentation. | A furniture detail page with product information, purchase controls, and a rotatable chair preview. | Width and height can be set; depth uses the system default. Main content is constrained by the window's width, height, and depth. |
| **Volumetric: Volume Window, referred to below as Volume** | A model or group of models needs an explicitly arranged 3D display region, while the experience remains contained within a bounded window. | Giving furniture its own 3D display region, or reserving space for an exploded mechanical assembly. | Width, height, and depth can be defined. Content remains constrained by the window boundaries after movement, rotation, scaling, or expansion. |
| **Stage: Spatial Scene** | Content is organized through relationships with a room, floor, the space around the user, or an immersive environment; or the task requires scene-level environment control. | Placing furniture at actual scale in a room, room-scale assembly instruction, or a virtual showroom. | Content is not constrained by the box-shaped boundaries of a WindowContainer. Opening a Stage enters Full Space and hides other applications' windows. The Stage style determines real-world visibility. |

Planar and Volume are two forms of the same `WindowContainer`. Their clearest SDK capability distinction is that Planar uses the system default depth, while Volume allows depth to be defined.

At this stage, determine the required spatial extent and organization. Exact dimensions, page regions, and model scaling algorithms can be decided later. For spatial interaction, consider the intended presentation scale and the range needed for required operations, rather than only the model's initial state.

### 4.2 Commonly Confused Boundaries

- **A model does not determine the container.** Planar can display actual 3D models, and models can rotate or scale in either Planar or Volume. Consider the task organization and spatial needs together.
- **Inspecting a model on its own does not automatically require Volume.** Volume is appropriate when the experience needs a defined 3D display region around the model. Local inspection can still take place within Planar.
- **Both Planar and Volume constrain main content.** 3D content outside the window's width, height, or depth is clipped. Configurable depth does not allow content to extend indefinitely.
- **Content not fitting does not automatically require Stage.** Consider presentation scale, model proportions, and content organization. Select Stage for large spatial presentations, environmental relationships, or scene-control needs.
- **An attached window is distinct from the main content region.** Attached windows can appear beside the main window. The main window's bounds do not need to contain both the model and every attached panel. Detailed placement belongs to the later layout stage.
- **Full Space and `StageStyle.Full` have different meanings.** Full Space gives the current application exclusive use of the space and hides other applications' windows. `StageStyle.Full` disables video passthrough. Stage can also use Mixed or Progressive to retain or adjust real-world visibility.
- **Select containers per task scenario.** An application can combine containers. After opening a Stage, the same application can still use Planar or Volume for menus, information, and tools.

For container and space-state behavior, see [PICO documentation: Understand spatial containers and space state](https://developer.picoxr.com/document/spatial-sdk/learn-about-spatial-containers-and-space-states/).

## 5. Scenario Examples

These examples illustrate reasoning. They are not fixed mappings from product categories or keywords to containers.

### Example 1: Information Browsing and Forms

> Task: Browse information, filter records, and complete forms → Content form: 2D only → Container: Planar → Rationale: A flat presentation already supports the task, and content fits a page structure.

### Example 2: Furniture Shopping with an Embedded Model Preview

> Task: Browse product information, compare prices, and rotate a model to inspect its appearance → Content form: Primarily 2D with supporting 3D → Container: Planar → Rationale: The main task follows product pages. The model supports appearance inspection and does not need a separate volumetric presentation.

### Example 3: Model Inspection with a Dedicated 3D Region

> Task: Inspect a mechanical model as a 3D exhibit and expand its parts to understand assembly relationships → Content form: Primarily 3D with 2D explanations and controls → Container: Volume → Rationale: The model and exploded parts need a defined 3D region, while the experience remains within window boundaries.

### Example 4: Room Placement and Spatial Scenes

> Task: Place furniture at actual scale in a real room to evaluate dimensions and placement → Content form: Primarily 3D with supporting 2D selection and controls → Container: Stage → Rationale: The task depends on relationships between the furniture, floor, walls, and other objects.

A virtual showroom can also use Stage, with content organized around a virtual environment rather than a real room.

The official [Welcome Space sample](https://github.com/Pico-Developer/PICO-Spatial-SDK-Sample-WelcomeSpace/blob/main/README.md) demonstrates an application combining Planar for pages, Volume for model inspection, and Stage for a prebuilt room scene.

### Proactive Decisions and Necessary Questions

| User Request | Frame's Response |
| --- | --- |
| "Design a furniture shopping application." | Develop a direction directly: the core task is browsing, comparing, and selecting products, so use primarily 2D pages. An embedded 3D preview can support appearance inspection within Planar. Do not ask separately about a dedicated volume or adding real-room placement. |
| "I have already chosen the furniture and want to know whether it suits my home." | Use the context first. If it remains unclear whether the user primarily means dimensions and placement or visual style, and no reasonable recommendation can be made, ask about that core intent. Do not ask the user to select a technical container. |

## 6. Frame Output Template

Record a clear content form and container selection, with a brief rationale.

```text
Frame Design Record
├─ User task: What the user wants to accomplish
├─ Spatial value: How spatial presentation supports the task
├─ Content form: 2D only / mixed with primary role / fully 3D
├─ Container: Planar / Volumetric / Stage
└─ Rationale: Explain the choice using the task, spatial organization,
              and container boundaries
```

Furniture shopping example:

```text
Frame Design Record
├─ User task: Browse and select furniture; understand appearance
│             and product information
├─ Spatial value: Rotate a 3D model to view its appearance from different sides
├─ Content form: Primarily 2D with an embedded 3D product preview
├─ Container: Planar
└─ Rationale: The main task takes place on flat pages. The model belongs
              to the product page and supports local appearance inspection.
```

For a 2D-only design, the spatial value entry can explain that a flat presentation already meets the task and no 3D objects are needed.

Frame establishes the content form, container, and spatial experience intent that affects the choice, such as rotating a model within a page, inspecting a dedicated volume, or placing objects in an environment. Specific pages, layouts, components, detailed interactions, and asset production belong to Explore and subsequent stages.
