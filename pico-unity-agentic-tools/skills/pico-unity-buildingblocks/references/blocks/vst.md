# VST (Passthrough)

## Tool

`pico_xr_vst` — actions: `enable` / `disable` / `status`

## Dependency

- XR Origin present

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
