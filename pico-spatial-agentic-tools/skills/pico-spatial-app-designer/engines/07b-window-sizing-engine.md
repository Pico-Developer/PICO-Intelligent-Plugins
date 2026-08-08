# PICO Spatial Window Sizing Methodology Engine

## Goal

Per the PICO spatial window sizing methodology, define a **default size + resizable range** for each WindowContainer. Sizing decisions do not start from a blank canvas and content area; instead, first determine the window type, official size baseline, field-of-view occupancy, and viewing distance, then calibrate with content, task, and hit targets.

In Shared Space, what a Planar window design controls is **field-of-view occupancy**, not absolute physical width/height; the system guarantees clarity across distance changes via Dynamic worldScale. Only Volumetric windows and 3D subjects use spatial volume as the primary basis.

Role: `interaction_xr_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 9, Window Sizing Derivation).

## Required Reading

Before deciding the size of any WindowContainer, you must read and apply [`knowledge/spatial-window-sizing-methodology.md`](../knowledge/spatial-window-sizing-methodology.md). This document only retains the executive summary; the numeric quick-reference, scene tiers, applicability boundaries, and comfort constraints are governed by that Knowledge document.

## Inputs

Task graph, state graph, layout regions, information topology, interaction goals, viewing posture, session duration, window attachment selections, and the reasoning conclusions from upstream stages.

## Derivation Order

1. **Determine window type and size baseline by content type**:
   - Familiar 2D reading / comparison / input / workflow tasks → Planar, default baseline starting from 1280×720dp, legal range 320×180dp ~ 2700×1800dp.
   - 3D objects / spatial volume as the subject → Volumetric, custom size by content volume, scaling always uniform.
2. **Assign to a scene tier**: auxiliary / HUD, productivity / main content, media / immersion, spatial anchoring / 3D. The tier determines whether the default size is near the lower bound, the 1280×720 baseline, a larger immersive window, or Volumetric volume.
3. **Declare the default viewing conditions**: posture, default distance, duration, worldScale. Planar by default launches about 1.75m in front of the wearer, typically adopting Dynamic worldScale.
4. **Constrain the upper bound with the clear field-of-view zone**: core content must fall within the clear field-of-view zone of 65° horizontal / 40° vertical; secondary content enters at most the 85° horizontal / 55° vertical peripheral field of view. Being so large that browsing the main content requires frequent head turning is a failure.
5. **Back out the lower bound from hit target, font size, and depth**: interaction hit targets must not be below 56×56dp; body text must not be below 12dp; a single line of long CJK body text is roughly within 50 characters; 3D content within a Planar must not exceed 640dp in depth.
6. **Calculate attachment and framework overhead**: clarify whether TitleBar, TabBar, Toolbar, Subwindow, Augment, etc. are outside the main content boundary, and deduct fixed overheads such as TitleBar 96dp, TabBar main area 64dp, and Toolbar minimum 64dp from the available content area.
7. **Generate default / min / max candidates**: give at least three candidates around the scene baseline, each explaining field-of-view occupancy, content capacity, interaction density, whitespace / crowding risk, and the reason for rejection.
8. **Determine the default value and resizable range**: the default value is the launch size after the methodology baseline is calibrated by content; min is constrained by the readability/clickability lower bounds; max is constrained by clear field of view, occlusion, and motion-sickness risk.
9. **Define content reflow rather than global scaling**: Large / Compact / Constrained are accomplished via collapsing, changing columns, layering, internal scrolling, and Sheet/Dialog transfer, not via a whole-scene transform: scale.

## Output (direct description, no longer bound to a Schema)

Describe in structured Markdown: content type, scene tier, window form, unit basis, default viewing distance, clear-field-of-view check, official baseline and resizable range, default / min / max, aspect-ratio policy, resize behavior, and the source of each value (PICO official constraint / scene tier / content / task / viewing conditions).

## PICO Official Size Constraints (inviolable platform baselines)

Derivations must fall within the PICO official constraints (fact source: PICO Developer Center "Set Properties for a WindowContainer"):

- **Planar depth locked at 640dp**: Planar derives only width × height; depth is fixed at 640dp, and the depth parameter of `defaultSize` has no effect for Planar; do not derive a custom depth for Planar.
- **Planar default baseline and size range**: familiar 2D / productivity tasks use 1280×720dp as the official default baseline, then calibrate by scene and content; Planar window width and height must fall within the official allowed interval of 320×180dp to 2700×1800dp.
- **Planar default distance and dynamic scale**: a Planar window by default launches about 1.75m in front of the wearer, adopting Dynamic worldScale by default, and the system dynamically scales upon distance changes to keep the relative field-of-view occupancy constant; therefore the core design object of Planar is "field-of-view occupancy + readability/clickability", not real physical width/height.
- **Only Volumetric has depth and is always uniform**: depth only takes effect for Volumetric; Volumetric scaling is always uniform (`UniformResizable`), and non-uniform options only make sense for Planar.
- **3D depth limit within a planar window**: 3D content displayed within a Planar must fall within the 640dp depth range; anything beyond it is clipped by the window boundary; large or body-surrounding 3D content should move into a Stage rather than enlarging the Planar.
- **ResizeType semantics**: `ContentMinSize` constrains only the minimum size (the window is not smaller than the content's minimum size); `ContentSize` constrains both maximum and minimum. When choosing resize behavior, align with these two official semantics rather than inventing your own.
- **WorldScale**: `Dynamic` (default, automatically scales with viewing distance, visually keeping a constant size) / `Fixed` (actual size fixed, does not change with distance). The window sizing derivation must declare which worldScale is adopted, because it determines whether the "logical size" equals the user's actual perceived size.
- **Field-of-view and hit-target baselines**: keep core content within the clear field-of-view zone of 65° horizontal / 40° vertical; secondary content no larger than 85° horizontal / 55° vertical; interaction targets no smaller than 56×56dp, and body text no smaller than 12dp.
- **Multi-window spacing and occlusion**: the default adjacency of multiple WindowContainers must declare at least 56dp of spacing, and explain the default number of main windows, the risk of occluding the real environment, and the attention cost.

## Prohibitions

- using 1600×900 as an unfounded fallback;
- treating 1280×720 as the final fixed size for all Planar projects without doing scene-tier, field-of-view, and content calibration;
- fixing all projects at 16:9;
- deriving PICO windows directly from a Web viewport;
- doing only transform: scale when shrinking;
- giving only the default size without declaring the min / max range and the user's resize behavior;
- saying only "suitable for Shared Space" without validating clear field of view, occlusion, hit targets, and fonts;
- describing project-level derivations as PICO official hard rules.
