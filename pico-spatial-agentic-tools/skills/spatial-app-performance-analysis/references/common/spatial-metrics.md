# SpatialMetrics Complete Metric Definitions

This file maintains the SpatialMetrics metric dictionary. `analysis-spatial-engine.md` is responsible for the analysis process, while this file is responsible for explaining metric meanings and usage principles.

These metrics come from `spatial-metrics.json` and are divided into 10 categories. Process sources include Runtime and App. 

During analysis, prioritize observing whether these metrics are elevated within the **abnormal frame or the app jank frame**, and combine with Perfetto Slice to determine if they are in the same window as the jank.

These data cannot be used as a direct indication of the root cause of SPR or APP jank. However, when the SPR or APP jank, these data can be used as clues to analyze the actual load of the scene and help locate the real source of jank pressure.

## Metric Types

SpatialMetrics currently includes the following types:
- 3D Render
- Animation
- Physics
- Portal
- Lighting
- Media
- Entity
- Resource
- 2D Render
- Memory

Process types include:
- Runtime: Better suited for explaining Spatial Runtime, unified rendering pipeline, and Runtime-side resource pressure.
- App: Better suited for backtracking what resources, components, Effects, or ECS data the application submitted.

## 3D Render

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| Draw Call Count | Runtime | Total Draw Call pressure |
| 3D Mesh Draw Call Count | Runtime | 3D Mesh draw submission pressure |
| Particle Draw Call Count | Runtime | Particle draw submission pressure |
| Shadow Draw Call Count | Runtime | Shadow draw submission pressure |
| Triangle Count | Runtime | Total triangle complexity |
| 3D Mesh Triangle Count | Runtime | 3D Mesh triangle complexity |
| Particle Triangle Count | Runtime | Particle triangle complexity |
| Shadow Triangle Count | Runtime | Shadow triangle complexity |
| Vertex Count | Runtime | Total vertex scale |
| 3D Mesh Vertex Count | Runtime | 3D Mesh vertex scale |
| Particle Vertex Count | Runtime | Particle vertex scale |
| Shadow Vertex Count | Runtime | Shadow vertex scale |

## Animation

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| animationResourceCount | App | Number of animation resources on the app side |
| Skeletal Animation Count | Runtime | Skeletal animation runtime pressure on the Runtime side |

## Physics

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| collisionComponentCount | App | Number of collision components, affecting physical calculation and synchronization pressure |
| rigidBodyComponentCount | App | Number of rigid body components, affecting physical simulation pressure |

## Portal

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| portalComponentCount | App | Number of Portal components |
| portalWorldComponentCount | App | Number of Portal Worlds |
| portalCrossableComponentCount | App | Number of crossable Portals |

## Lighting

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| directionalLightComponentCount | App | Number of directional light components on the app side |
| spotLightComponentCount | App | Number of spotlight components on the app side |
| pointLightComponentCount | App | Number of point light components on the app side |
| Visible Lights | Runtime | Total number of visible light sources on the Runtime side |
| Visible Spot Lights | Runtime | Number of visible spotlights on the Runtime side |
| Visible Point Lights | Runtime | Number of visible point lights on the Runtime side |
| Visible Directional Lights | Runtime | Number of visible directional lights on the Runtime side |

## Media

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| videoComponentCount | App | Number of video components |
| videoPlayerComponentCount | App | Number of video player components |

## Entity

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| modelComponentCount | App | Number of model components, affecting rendering submission and scene scale |
| transformComponentCount | App | Number of Transform components, affecting ECS update and synchronization scale |

## Resource

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| assetBundleCount | App | Number of AssetBundles |
| meshResourceCount | App | Number of Mesh resources |
| textureResourceCount | App | Number of Texture resources |
| physicallyBasedMaterialCount | App | Number of PBR materials |
| shapeResourceCount | App | Number of Shape resources |
| videoMaterialCount | App | Number of video materials |
| materialResourceCount | App | Total number of material resources |
| shaderGraphMaterialCount | App | Number of ShaderGraph materials, potentially bringing Shader / material complexity pressure |

## 2D Render

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| viewAttachmentCount | App | Number of ViewAttachments, affecting the 2D / 3D unified rendering budget |
| CPU Utilization | App | 2D rendering related CPU utilization on the app side |
| GPU Utilization | App | 2D rendering related GPU utilization on the app side |
| Effect_GlassEffectCount | App | Number of glass effects |
| Effect_3DClipCount | App | Number of 3D clipping effects |
| Effect_3DTRSCount | App | Number of 3D TRS effects |
| Effect_MeshRoundCornerCount | App | Number of mesh round corner effects |
| Effect_3DViewCount | App | Number of 3D View effects |
| Effect_TotalEffectsCount | App | Total number of 2D / 3D effects |

## Memory

| Metric | Process Type | Primary Explanation Direction |
|---|---|---|
| Texture2D Memory | Runtime | Texture memory pressure |
| Mesh Memory | Runtime | Mesh memory pressure |
| Scene Graph Memory | Runtime | Scene graph memory pressure |

## Usage Principles

- Bottleneck is only an auxiliary clue to help analyze the actual load situation of the scene, so conclusions cannot be drawn directly based on Bottleneck detection.
- Runtime metrics are better suited for explaining Spatial Runtime, unified rendering pipeline, and Runtime-side resource pressure.
- App metrics are better suited for backtracking what resources, components, Effects, or ECS data the application submitted.
- Within the same abnormal window, if Runtime rendering metrics are high while App resource / component metrics are also high, priority should be given to judging whether the rendering tasks or resource scale submitted by the application are too heavy.
- If the CPU bottleneck is obvious and Physics, Animation, Portal, Media, Entity, or 2D Render metrics on the App side are high, combined judgment should continue with application process Slices to determine if it is caused by app-side resource usage or ECS updates.
- If the GPU bottleneck is obvious and Draw Call, Triangle, Vertex, Light, or Memory metrics on the Runtime side are high, combined judgment should continue with `Eng-Render`, `gpu_frame_end`, and application resource metrics to determine the source of pressure.

## CPU / GPU Bottleneck Mapping

### Metrics More Biased Toward GPU

Priority focus:
- Triangle Count
- Vertex Count
- Visible Lights
- Texture2D Memory
- Mesh Memory
- Effect_TotalEffectsCount
- GPU Utilization
- Lighting

When these metrics rise, combine with `Eng-Render` and `gpu_frame_end` to judge whether it is a unified rendering pipeline or GPU-side bottleneck.

### Metrics More Biased Toward CPU

Priority focus:
- Draw Call Count
- 3D Mesh Draw Call Count
- Particle Draw Call Count
- Shadow Draw Call Count
- animationResourceCount
- Skeletal Animation Count
- collisionComponentCount
- rigidBodyComponentCount
- portalComponentCount
- videoComponentCount
- videoPlayerComponentCount
- modelComponentCount
- transformComponentCount
- CPU Utilization

When these metrics rise, combine with application process, `Spatial_Main`, `System_Update`, and `SpatialMFrame` to judge whether it is caused by the scale of data submitted by the app, ECS updates, resource lifecycle, or Runtime-side processing.
