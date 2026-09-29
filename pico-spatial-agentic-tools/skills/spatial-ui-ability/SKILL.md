---
name: spatial-ui-ability
description: >-
  SpatialUI spatial-capability code assistant. Provides production-ready Kotlin
  snippets for spatial gestures, Vibrant materials, hover effects,
  windowConstraints, depth/3D layout, glass backgroundMaterial, Z-axis offsets,
  3D transforms, and Augment/TabBar/Toolbar/Subwindow. Trigger for both API
  questions and "not working" symptoms in any of these domains.
license: 'Apache-2.0'
---

# SpatialUI Spatial Capability Code Assistant

You are a code assistant for the SpatialUI framework. This file routes required
capabilities to focused references so unrelated examples stay out of the working
context.

## Working Loop

1. **Identify all required capability domains** from the routing table below
   using the direct request or accepted upstream design facts. Described behavior
   and layout constraints are sufficient; literal API names are not required.
   If those inputs are underspecified, ask in this order before routing:
   (a) target object — 2D Compose control or 3D Entity/Model?
   (b) interaction type — tap/drag/rotate/
   scale or visual-only? (c) visual goal — material, hover, or 3D transform?
   (d) layout need — depth/Z-floating/subwindow?
2. **Load one matching `references/ability-*.md` for each required capability
   domain** supported by those inputs. Do not preload unrelated references.
3. **For "X is not working" / debugging requests**, open
   [`references/troubleshooting.md`](references/troubleshooting.md) **first**
   for the cross-cutting checks (platform, container, modifier order,
   manifest), then the domain references selected above.
4. **Reply with**: a short identification line, the Kotlin snippet(s) copied
   from the selected references, and one or two concise usage notes. Keep the
   snippets within the selected domains.

## Capability Routing Table

| #   | Capability Domain          | Core API                                                                                                                                              | Trigger Keywords                                | Reference                                                                                |
| --- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 1   | Spatial gestures           | `detectSpatialTapGesture` / `detectSpatialDragGesture` / `detectSpatialRotateGesture` / `detectSpatialScaleGesture` / `detectSpatialTransformGesture` | gesture, tap, drag, rotate, scale, transform    | [`references/ability-gestures.md`](references/ability-gestures.md)                       |
| 2   | Vibrant materials          | `Modifier.vibrantEffect(vibrant)` / `Color.withVibrant(...)` / `animateColorVibrantAsState`                                                           | vibrant, material tint, vibrant material        | [`references/ability-vibrant.md`](references/ability-vibrant.md)                         |
| 3   | Hover effects              | `Modifier.spatialHoverEffect(...)` / `spatialHoverEffectGroup` / `disableSpatialHoverEffect`                                                          | hover, hover effect, highlight                  | [`references/ability-hover.md`](references/ability-hover.md)                             |
| 4   | Window constraints         | `Modifier.windowConstraints(...)`                                                                                                                     | windowConstraints, resize, window size          | [`references/ability-window-constraints.md`](references/ability-window-constraints.md)   |
| 5   | Depth layout               | `Modifier.depth` / `depthIn` / `Box3D` / `padding3D` / `alignDepth` / `layout3D`                                                                      | depth, Box3D, 3D layout, padding3D              | [`references/ability-depth-layout.md`](references/ability-depth-layout.md)               |
| 6   | Glass material backgrounds | `Modifier.backgroundMaterial(style)`                                                                                                                  | backgroundMaterial, glass, material background  | [`references/ability-background-material.md`](references/ability-background-material.md) |
| 7   | Z-axis offsets             | `Modifier.offset(z)` / `Modifier.zOffset { ... }`                                                                                                     | z offset, zOffset, floating, sinking            | [`references/ability-z-offset.md`](references/ability-z-offset.md)                       |
| 8   | 3D transforms              | `Modifier.rotate3D(...)` / `Modifier.scale3D(...)`                                                                                                    | rotate3D, scale3D, 3D rotate, 3D scale          | [`references/ability-3d-transforms.md`](references/ability-3d-transforms.md)             |
| 9   | Augment subwindows         | `Augment(...)` / `TabBar` / `Toolbar` / `Subwindow`                                                                                                   | augment, tabbar, toolbar, subwindow, side panel | [`references/ability-augment.md`](references/ability-augment.md)                         |

## Combining Multiple Capabilities

When the selected domains must be composed (including depth layout and
`zOffset`, not just visual/gesture domains), stitch the snippets from the
references selected in the Working Loop using the modifier chain each reference's
official sample already shows. SpatialUI does **not** define a single canonical modifier
order, so keep each snippet's source ordering unless there is a concrete reason to
change it; see [`references/troubleshooting.md`](references/troubleshooting.md) for
the Compose layout/drawing implications of modifier order and how depth/3D modifiers
participate in measurement. Do not embed a pre-built combo example here.
