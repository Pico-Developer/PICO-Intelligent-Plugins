# Feature Index

## How to Use This Index

Select the development mode first, then inspect the corresponding APIs, samples, and bundled documentation in the installed packages. This index identifies feature entry points and major constraints; it does not replace version-specific API definitions.

## Rendering and Performance

| Feature                       | Mode             | Implementation Entry                                   | Key Checks                                                                      |
| ----------------------------- | ---------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------- |
| FFR                           | PICO XR / OpenXR | `PXR_Manager` or OpenXR Foveated Rendering Feature     | Graphics API, Render Mode, URP intermediate texture, subsampling                |
| ETFR                          | PICO XR / OpenXR | Same entry plus eye tracking                           | Device has eye-tracking cameras; ETFR and FFR are mutually exclusive            |
| AppSW                         | PICO XR / OpenXR | Portal/OpenXR Feature and URP motion vectors           | Vulkan, Multiview, compatible shaders, Content Protection conflict              |
| Composition Layer             | PICO XR / OpenXR | PXR Composition Layer / XR Composition Layers provider | Overlay/Underlay, alpha, layer count, Late Latching conflict                    |
| Multiview                     | PICO XR / OpenXR | XR Plug-in/OpenXR Render Mode                          | Some features require Multi-pass; cubemap layer limitations                     |
| Late Latching                 | PICO XR / OpenXR | Manager/Feature                                        | Unity/package version; do not combine with Overlay/Underlay                     |
| Adaptive Resolution           | PICO XR          | PICO XR settings/API                                   | Not supported in Unity OpenXR                                                   |
| Super Resolution / Sharpening | PICO XR          | PICO XR settings/API                                   | Combination constraints with subsampling                                        |
| Render Viewport Scaling       | PICO XR / OpenXR | SDK API                                                | Do not assume identical behavior to `eyeTextureResolutionScale` across versions |
| Refresh Rate                  | PICO XR / OpenXR | SDK API/Feature                                        | Query supported values; do not hardcode device rates                            |
| Anti-Aliasing                 | PICO XR / OpenXR | Quality/URP/OpenXR                                     | Risk with Unity 6 + URP + OpenGL + Multi-pass + MSAA                            |

### ETFR Requirements

- PICO XR documentation lists devices with eye-tracking cameras, including PICO 4 Pro, PICO 4 Enterprise, and Project Swan.
- PICO XR documentation requires PICO OS 5.7.0 or later.
- PICO XR FFR/ETFR levels include Low, Med, High, and Top High; High and Top High have the same effect.
- The Unity OpenXR documentation snapshot states that ETFR supports OpenGL only, while subsampling supports Vulkan only. They cannot be combined through that path.
- The Unity OpenXR documentation snapshot pins subsampling to OpenXR Plugin 1.8.2.

## Input and Interaction

| Feature                       | Mode                                  | Implementation Entry                                | Key Checks                                                                         |
| ----------------------------- | ------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Controller/HMD                | All modes                             | XRI/Input System; Spatial can use `InputDevices`    | Left/right bindings, focus, disconnect                                             |
| Hand Tracking                 | PICO XR / OpenXR / Spatial Full Space | Building Blocks, XR Hands, Hand Interaction Profile | Package version, models, interaction profile                                       |
| Haptics                       | PICO XR / OpenXR                      | InputDevice or PICO haptic API                      | Device capability, buffered/non-buffered                                           |
| System Keyboard               | All modes                             | SDK/System Keyboard                                 | Focus and input-method lifecycle                                                   |
| Spatial Input                 | Spatial                               | EnhancedTouch, `SpatialInputState`                  | Current interaction is primarily Indirect Pinch; handle Began/Moved/Ended/Canceled |
| XR Spatial Pointer Interactor | Spatial                               | Spatial component                                   | Version requirements, Canvas/EventSystem                                           |

In PICO Spatial, `SpatialInputState.interactionId` commonly uses `0` for the left hand, `1` for the right hand, and `-1` for an empty state. Do not assume `Stationary` will occur.

## Tracking

| Feature         | PICO XR   | OpenXR        | Spatial                                      |
| --------------- | --------- | ------------- | -------------------------------------------- |
| Eye Tracking    | Supported | Supported     | Not supported                                |
| Face Tracking   | Supported | Not supported | Not supported                                |
| Body Tracking   | Supported | Supported     | Not supported                                |
| Object Tracking | Supported | Not supported | Not supported                                |
| Tracking Origin | Supported | Supported     | Use Spatial Camera and space-state semantics |

Implementation sequence:

1. Query device support.
2. Enable the Portal/Feature configuration and permissions.
3. Start the Provider.
4. Wait for Running state.
5. Read timestamped data with explicit space semantics.
6. Handle focus loss, pause, and device disconnect.
7. Stop and release resources.

## MR and Environment Sensing

| Feature               | PICO XR   | OpenXR        | Spatial                                 |
| --------------------- | --------- | ------------- | --------------------------------------- |
| Video Seethrough      | Supported | Supported     | Not supported                           |
| Spatial Anchor        | Supported | Supported     | AR Foundation Anchor in Full Space only |
| Shared Spatial Anchor | Supported | Not supported | Not supported                           |
| Scene Capture         | Supported | Supported     | Not supported                           |
| Spatial Mesh          | Supported | Supported     | AR Foundation Mesh in Full Space only   |
| Plane Detection       | Supported | Not supported | Not supported                           |
| Environment Depth     | Supported | Not supported | Not supported                           |
| Light Estimation      | Supported | Not supported | Not supported                           |
| MR Safeguard          | Supported | Supported     | Not supported                           |
| SecureMR              | Supported | Not supported | Not supported                           |

VST notes:

- Disable Main Camera HDR for the PICO XR path on Unity 6.
- Check known issues for combinations of URP post-processing, HDR, Vulkan, and Underlay/VST.
- Camera capabilities require permission and privacy fallback paths.

Spatial Anchor notes:

- Distinguish create, persist, load, unpersist, and share operations.
- Record the reference space and alignment semantics used by each Anchor.
- Do not treat successful local persistence as successful cloud sharing.

## Audio, Platform, and Enterprise Capabilities

- Spatial Audio is supported in PICO XR and Unity OpenXR, but not PICO Spatial.
- Platform Services are available in all three modes; Spatial supports them in Full and Shared Space.
- Enterprise Services are available in all three modes; Spatial supports them in Full and Shared Space.
- Content Protection is available in all three modes; Spatial supports it in Full and Shared Space.
- MRC is supported in PICO XR and Unity OpenXR.

For accounts, Entitlement, cloud storage, shared anchors, and enterprise APIs:

- Do not hardcode App IDs, tokens, or secrets.
- Call product APIs only after initialization completes.
- Distinguish Editor state, signed-out state, missing entitlement, network failure, and server errors.
- Enable and validate User Entitlement Check before release.

## PICO Spatial Specifics

### Spatial Camera

- Use one Spatial Camera per scene.
- Constrained mode enters Shared Space with clipping and capability limits.
- Unconstrained mode enters Full Space, closes other applications, and exposes more capabilities.
- Some Output Configuration changes do not take effect after the camera starts.

### Component Support Boundaries

- Transform, Audio, MeshFilter, Animation, 2D/3D Physics, Scripts, and NavMesh are supported.
- MeshRenderer is partially supported; full Lighting, Shadows, GI, and Probes are not supported.
- LineRenderer is not supported.
- Particle System, Canvas Renderer, Sprite Renderer, TMP, and Shader Graph are partially supported.
- Spatial Audio and Light Probes are not supported.

### Materials, Textures, and Video

- Dynamic material parameters require SpatialAdapter synchronization.
- `Material.SetTexture` updates only the Unity side unless the change is synchronized to Spatial Engine.
- Video options include Video Player, SpatialAdapterVideoComponent, and SurfaceTextureVideoComponent.
- High-resolution Video Player RenderTextures increase copy cost.
- For Android-native video, evaluate the SurfaceTexture producer-consumer pipeline first.

## Tool Selection

| Goal                           | Tool                                                              |
| ------------------------------ | ----------------------------------------------------------------- |
| Fast configuration and fixes   | PICO Portal, Project Validation                                   |
| Fast controller and hand setup | PICO Building Blocks, XRI Samples                                 |
| Editor-to-device preview       | Live Preview for PICO XR, Play-to-PICO for Spatial, PDC streaming |
| Logs and Inspector             | PICO Debugger, `adb logcat`                                       |
| Basic performance              | Metrics HUD, Unity Profiler                                       |
| XR performance comparison      | XR Profiling Toolkit                                              |
| GPU metrics                    | PICO Graphics Probe Tool, Snapdragon Profiler                     |
| Frame and rendering diagnosis  | RenderDoc for PICO, Unity Frame Debugger                          |
| Haptic assets                  | PICO Haptic Editor                                                |
