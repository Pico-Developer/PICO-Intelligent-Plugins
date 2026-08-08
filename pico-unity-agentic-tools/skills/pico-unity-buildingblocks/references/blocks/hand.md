# Hand tracking (virtual hands)

## Tool

`pico_xr_hand` — actions: `enable` / `disable` / `status`

Trigger words: virtual hands / hand / hand interaction / hand tracking / hands.

## Dependency

- XR Origin present
- PICO hand-model prefabs (`HandLeft` / `HandRight`) in the PICO SDK
- No Unity `com.unity.xr.hands` package required — this block uses the
  PICO-native hand path (`PXR_Hand` component + PICO hand prefabs), so it
  does NOT trigger a package install or a domain reload.

## Cheatsheet

### Enable Hand
- Pre: XR Origin (via orchestration step B.1).
- Call: `pico_xr_hand(action=enable)`.
- Mounts `HandLeft` / `HandRight` prefabs under the XR Origin's Camera Offset
  as agent-owned markers (`[PICO_MCP] Hand Left` / `[PICO_MCP] Hand Right`),
  applies the PICO project settings `handTracking = true` and
  `handTrackingSupportType = ControllersAndHands`, and wires the mounted hands
  into the XR Origin's `XRInputModalityManager` so XRI auto-hides the hand
  models whenever a controller becomes tracked (and shows them again when the
  controller is dropped).
- If the C# layer returns `error` mentioning a missing `HandLeft`/`HandRight`
  prefab, the user's PICO SDK install is incomplete; do NOT auto-fix — relay
  the error and ask them to verify/update the PICO SDK.

### Disable Hand
- No deps to check.
- Call: `pico_xr_hand(action=disable)`.
- Removes the `[PICO_MCP] Hand Left` / `[PICO_MCP] Hand Right` markers.

### Status
- Call: `pico_xr_hand(action=status)`.
- `installed` is true only when BOTH hand markers are present. If only one
  is mounted, `reason` explains the partial state.

## Typical pipeline — enable (XR Origin already present)

```
pico_xr_status()               → xr_origin=ok, hand=off
pico_xr_hand(action=enable)    → ok   (or error if PICO SDK hand prefabs missing)
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

- PICO hand prefabs ship with the PICO SDK already in the project. No extra
  package install is needed.
- This block is idempotent: re-enabling when both markers already exist is a
  no-op (returns `already_present`).
- Enabling applies the PICO project settings (`handTracking = true` +
  `handTrackingSupportType = ControllersAndHands`) via reflection; if the PICO
  SDK project-setting type is absent, that step is a silent no-op, the hand
  models are still mounted, and the C# layer logs a warning that tracking will
  not run until Hand Tracking is enabled in the PICO XR project settings.
- `handTracking` is the ONLY runtime gate for the PICO-native hand path; if
  hands mount but do not track at runtime, verify this project setting is on.
- Controller auto-hide is handled natively by XRI's `XRInputModalityManager`
  (the hand GameObjects are registered as its `leftHand` / `rightHand`), so no
  custom runtime script and no domain reload are involved. Disabling the hand
  block unwires those references again.
- Do NOT auto-install the PICO SDK — it is outside the scope of these MCP tools.
