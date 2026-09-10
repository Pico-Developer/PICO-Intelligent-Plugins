# VST (Passthrough)

## Tool

`pico_xr_vst` — actions: `enable` / `disable` / `status`

## Dependency

- XR Origin present
- A PICO runtime enabled in XR Plug-in Management (PICO-native **or** PICO
  OpenXR — see SKILL.md §3.1). User prerequisite; this skill does not toggle it.

## Cheatsheet

### Enable VST

- Pre: XR Origin (via orchestration step B.1) — only if `xr_origin` is missing.
- Call: `pico_xr_vst(action=enable)`.
- No settle loop needed — VST does not trigger compile.

### Disable VST

- No deps to check.
- Call: `pico_xr_vst(action=disable)`.

### Status

- Call: `pico_xr_vst(action=status)`.

## Typical pipeline — enable (XR Origin already present)

```
pico_xr_status()                    → xr_origin=ok, vst=off
pico_xr_vst(action=enable)          → ok
pico_xr_status()                    → vst=on   (internal verify)
Save Scene                          → ok
```

### Typical pipeline — disable

```
pico_xr_vst(action=disable)         → ok
pico_xr_status()                    → vst=off  (internal verify)
Save Scene                          → ok
```

## Notes

- Spatial Mesh depends on VST being enabled. If the user asks to enable
  Spatial Mesh and VST is off, the orchestration loop will enable VST first
  (step B.2).
- Enable turns on `PXR_ProjectSetting.videoSeeThrough` so `PXR_BuildProcessor`
  emits `enable_vst` in the Android manifest; disable clears only that flag.
  The shared `PXR_Manager` component (mounted on the XR Origin root by
  `EnsureXROrigin`) is never added or removed here.
- **PICO OpenXR runtime.** When the project runs on the OpenXR loader
  (`ENABLE_PICO_OPENXR_SDK`), passthrough is gated by the PICO `PassthroughFeature`
  OpenXR feature asset, which must be ENABLED on the Android build target. On
  enable, the C# layer flips it on by reflection (mirrors the SDK's
  `PXR_Utils.EnableOpenXRFeature<PassthroughFeature>()`); on the PICO-native
  path this is a harmless no-op. The agent does nothing extra — but the OpenXR
  loader + PICO feature group must already be enabled by the user (SKILL.md
  §3.1); the skill does not toggle providers.
