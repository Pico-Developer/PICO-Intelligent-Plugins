# Hand tracking (virtual hands)

## Tool

`pico_xr_hand` — actions: `enable` / `disable` / `status`

Trigger words: virtual hand / hand / hand interaction / hand tracking / hands.

## Dependency

- XR Origin present
- Hand-model prefabs, runtime-branched: PICO-native path needs the PICO
  `HandLeft` / `HandRight` prefabs (in the PICO SDK); OpenXR path needs the Unity
  XR Hands `HandVisualizer` sample (`com.unity.xr.hands`, imported on demand).
- **XRI `Hands Interaction Demo` sample** — enable imports this sample from
  `com.unity.xr.interaction.toolkit` to source the hand-interactor rig. Because
  importing a sample copies assets and triggers an Editor recompile, **enable is
  TWO-PHASE the first time** (see below). If XRI is not installed, the interactor
  cannot be mounted and the C# layer reports `error`.
- The hand _models_ are runtime-branched. On the **PICO-native** path they use
  the PICO-native prefabs (`PXR_Hand` + `HandLeft`/`HandRight`), which need no
  `com.unity.xr.hands` package. On the **OpenXR** path (`ENABLE_PICO_OPENXR_SDK`)
  the native `PXR_Hand` script is not compiled, so enable instead mounts the
  Unity **XR Hands `HandVisualizer`** prefabs (`Left Hand Tracking` /
  `Right Hand Tracking`, root = `XRHandSkeletonDriver`) from `com.unity.xr.hands`
  — mirroring the PICO SDK's own OpenXR hand building block (`GenerateXRHands`).
  Mounting the PICO prefabs under OpenXR would leave a missing-script on the
  prefab root, so the two paths must not be mixed.

## Cheatsheet

### Enable Hand

- Pre: XR Origin (via orchestration step B.1).
- Call: `pico_xr_hand(action=enable)`.
- **Mounts the hand models** (runtime-branched): on the PICO-native path the
  PICO `HandLeft` / `HandRight` prefabs; on the OpenXR path the Unity XR Hands
  `Left Hand Tracking` / `Right Hand Tracking` prefabs (imported on demand from
  the `HandVisualizer` sample — two-phase like the interactor rig). Either way
  they are mounted under the XR Origin's Camera Offset as agent-owned markers
  (`[PICO_MCP] Hand Left` / `[PICO_MCP] Hand Right`), the PICO project settings
  `handTracking = true` and `handTrackingSupportType = ControllersAndHands` are
  applied, and the mounted hands are wired into the XR Origin's
  `XRInputModalityManager`.
- **Mounts the XRI hand INTERACTOR rig** (defect ② + ③ fix): the PICO hand models
  are visual/tracking only and carry **no** interactor, so on their own a pinch
  can never become an XRI select and `pico_xr_grab` has nothing to grab with.
  Enable instantiates the sample's top-level `XR Origin Hands (XR Rig)` prefab
  (identified reflection-first by an `XROrigin` component + a
  `Camera Offset/Left Hand|Right Hand` structure, so we do not hardcode its
  filename), **unpacks it**, then **EXTRACTS its `Left Hand` / `Right Hand`
  interactor groups** into Camera Offset as agent-owned markers
  (`[PICO_MCP] Hand Interactor L` / `[PICO_MCP] Hand Interactor R`) and destroys
  the temporary rig. Each carries an Interactor component + a pinch-driven
  select `InputActionReference` + an Attach Transform — the three things XRI
  grab requires. This mirrors the PICO SDK's own `XRI Hand Interaction` building
  block. **Do NOT** try to source the interactor by instantiating stray leaf
  prefabs like `HandInteractorAffordances` or `PinchPointStabilized` —
  `Left Hand` / `Right Hand` only exist as GameObjects INSIDE the rig prefab,
  not as independent prefab assets.
- **Repairs the far-ray origin references** (defect ③ fix). The interactor
  groups rely on prefab OVERRIDES to point `NearFarInteractor.attachController`
  - both casters (`SphereInteractionCaster` / `CurveInteractionCaster`) +
    `LineVisual/CurveVisualController` at their sibling `Aim Pose` transform.
    Reparenting an inner object out of a prefab instance discards those overrides
    and every reference collapses to `null` — the ray then falls back to the
    interactor GameObject (Camera Offset origin) and no longer follows the hand.
    Enable therefore explicitly re-wires the four references to each hand's own
    `Aim Pose` after reparent (reflection-set: `transformToFollow`, `castOrigin`
    on both casters, `lineOriginTransform`). Skip this step and the pinch still
    grabs but the far-ray visually shoots from the head/rig root.
- **Does NOT surface a controller** (defect ① fix): a hand-only enable must never
  show the generic (non-PICO) Starter-Assets controller. Enabling the modality
  manager alone would resurface those baked-in controllers, so when the Controller
  module is not active the C# layer nulls the manager's `leftController` /
  `rightController` refs. A controller appears **only** when the user runs
  `pico_xr_controller` (which mounts the PICO prefab and re-binds those refs).
- **Also enables the OpenXR `HandTracking` + `HandInteractionProfile` features
  on the Android build target** (reflection, R3 — mirrors
  `PXR_Utils.EnableHandTrackingFeature()`) so the pinch is delivered as a select
  input on the OpenXR path. On the PICO-native path this is a harmless no-op and
  pinch is delivered via the native `PicoHandInteraction` device.
- **Adds the PICO hand pinch/grasp bindings to the XRI `Select` action** (defect
  ② part 2 — the ACTION half). Mounting the interactor rig only builds the
  _receiver_ of a select; something must still _deliver_ one. On the hand path the
  XRI `Select` action ships with **no** PICO device binding (the controller path
  worked only because its Starter-Assets preset already binds `Select`), so a
  pinch never became a select and nothing grabbed. Enable now invokes the PICO
  SDK's own `XRI Hand Interaction` building block
  (`PXR_BuildingBlocks(OpenXR)XRIHandInteraction.ExecuteBuildingBlockStatic()`, by
  reflection, R3) which adds `<PicoHandInteraction>{LeftHand|RightHand}/pinchTouched`
  - `/graspFirm` (and the OpenXR `<HandInteraction>{…}/pinchTouched`) to the
    shared `Select` / `Select Value` / `UI Press` actions. Idempotent (only adds a
    binding when absent) and has NO scene side effects — it only edits + saves the
    XRI Input Actions asset. Runs on **every** enable so it self-heals a project
    whose input asset predates this fix. If the SDK type is absent it logs a warning
    and the user must run that building block once manually.
- **TWO-PHASE (first enable only).** If the `Hands Interaction Demo` sample is not
  yet imported, the first `enable` imports it and returns a `skipped` /
  recompiling status. Run the post-write settle loop (poll `pico_xr_status` until
  the bridge returns), then call `pico_xr_hand(action=enable)` **again** — the
  second call mounts the interactors and returns `ok`. Once the sample is present,
  enable is single-phase.
- If the C# layer returns `error` mentioning a missing `HandLeft`/`HandRight`
  prefab, the user's PICO SDK install is incomplete; do NOT auto-fix — relay
  the error and ask them to verify/update the PICO SDK.

### Disable Hand

- No deps to check.
- Call: `pico_xr_hand(action=disable)`.
- Removes the `[PICO_MCP] Hand Left` / `[PICO_MCP] Hand Right` **and**
  `[PICO_MCP] Hand Interactor L` / `[PICO_MCP] Hand Interactor R` markers.

### Status

- Call: `pico_xr_hand(action=status)`.
- `installed` is true only when BOTH hand markers are present. If only one
  is mounted, `reason` explains the partial state.

## Typical pipeline — enable, FIRST time (sample not yet imported)

```
pico_xr_status()               → xr_origin=ok, hand=off
pico_xr_hand(action=enable)    → skipped (recompiling): models mounted, XRI
                                  "Hands Interaction Demo" sample imported,
                                  Editor recompiling
  → run the post-write settle loop (poll pico_xr_status until the bridge returns)
pico_xr_hand(action=enable)    → ok   (interactors now mounted)
pico_xr_status()               → hand=on   (internal verify)
Save Scene                     → ok
```

## Typical pipeline — enable (sample already imported)

```
pico_xr_status()               → xr_origin=ok, hand=off
pico_xr_hand(action=enable)    → ok   (models + interactors in one call;
                                  or error if PICO SDK hand prefabs missing)
pico_xr_status()               → hand=on   (internal verify)
Save Scene                     → ok
```

### Typical pipeline — disable

```
pico_xr_hand(action=disable)   → ok
pico_xr_status()               → hand=off (internal verify)
Save Scene                     → ok
```

## Notes

- PICO hand prefabs ship with the PICO SDK already in the project (PICO-native
  path). No extra package install is needed for the MODELS on that path. On the
  OpenXR path the models come from the Unity XR Hands `HandVisualizer` sample,
  which enable imports on demand (two-phase, same handshake as the interactor
  rig).
- The INTERACTOR rig comes from the XRI `Hands Interaction Demo` sample, which
  enable imports on demand (two-phase — see above). This is the ONLY thing that
  makes a pinch actually grab; mounting the models without an interactor (the old
  behaviour) looked correct but could not pick anything up.
- This block is idempotent: re-enabling when both hand markers AND both interactor
  markers already exist is a no-op (returns `already_present`).
- Enabling applies the PICO project settings (`handTracking = true` +
  `handTrackingSupportType = ControllersAndHands`) via reflection; if the PICO
  SDK project-setting type is absent, that step is a silent no-op, the hand
  models are still mounted, and the C# layer logs a warning that tracking will
  not run until Hand Tracking is enabled in the PICO XR project settings.
- `handTracking` is the ONLY runtime gate for the PICO-native hand path; if
  hands mount but do not track at runtime, verify this project setting is on.
- **Pinch → grab** has TWO halves and enable now wires BOTH:
  (1) the _action_ — a pinch must be DELIVERED as an XRI `Select`. This needs two
  things, both done on enable: the OpenXR `HandTracking` + `HandInteractionProfile`
  features are flipped on (OpenXR path; native path uses the `PicoHandInteraction`
  device), AND the PICO hand device bindings (`…/pinchTouched`, `…/graspFirm`) are
  added to the XRI `Select` action via the PICO SDK's `XRI Hand Interaction`
  building block. Enabling the OpenXR feature alone is NOT enough — without the
  `Select`-action binding the pinch is never routed to a select (this is exactly
  why controller grab worked but hand grab did not: the controller preset binds
  `Select`, the hand action did not).
  (2) the _receiver_ — the Hand Interactor rig (from the sample) is the GameObject
  that consumes that select and drives `pico_xr_grab`. Supplying either half alone
  (the old bug) meant nothing grabbed: no interactor = nothing receives the pinch;
  no `Select` binding = nothing delivers it.
- **Hand-only must not show a controller** (defect ①): enable keeps the generic
  Starter-Assets controller hidden by nulling the modality manager's controller
  refs when the Controller module is inactive. Controllers — always the PICO
  prefab — are owned solely by `pico_xr_controller`.
- **Far-ray must originate at the hand, not Camera Offset** (defect ③): the
  interactor group's `NearFarInteractor` casters + line-visual line origin come
  from the XRI rig as **prefab overrides**. Extracting the group with
  `PrefabUtility.InstantiatePrefab` + reparent silently drops those overrides,
  so enable re-wires `InteractionAttachController.transformToFollow`,
  `SphereInteractionCaster.castOrigin`, `CurveInteractionCaster.castOrigin` and
  `CurveVisualController.lineOriginTransform` on the reparented group to the
  hand's own `Aim Pose` transform. Symptom if this step is skipped: pinch still
  grabs, but the far ray visually shoots out from the head / rig root instead
  of the hand.
- Controller auto-hide (when a controller IS enabled) is handled natively by
  XRI's `XRInputModalityManager` (the hand GameObjects are registered as its
  `leftHand` / `rightHand`). Disabling the hand block unwires those references.
- Do NOT auto-install the PICO SDK — it is outside the scope of these MCP tools.
