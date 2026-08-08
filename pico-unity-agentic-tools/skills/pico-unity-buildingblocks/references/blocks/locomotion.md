# Locomotion

## Tool

`pico_xr_locomotion` — actions: `enable` / `disable` / `configure` / `status`

## Dependency

- XR Origin present (Locomotion node is a child of XR Origin)

## Cheatsheet

### Enable Locomotion (whole root)
- Pre: XR Origin (via orchestration step B.1).
- Call: `pico_xr_locomotion(action=enable)`.

### Configure Locomotion subset
- Pre: XR Origin (via orchestration step B.1).
- Call: `pico_xr_locomotion(action=configure, presets="Move,Turn,Teleportation,Gravity")`.
- Valid preset tokens (case-insensitive, comma/space/`|`/`;` separated):
  `Move`, `Turn`, `Teleportation`, `GrabMove`, `Climb`, `Gravity`, `Jump`,
  `Default` (= Move|Turn|Teleportation|Gravity), `All`, `None`.

### Disable Locomotion (whole root)
- No deps to check.
- Call: `pico_xr_locomotion(action=disable)`.

### Status
- Call: `pico_xr_locomotion(action=status)`.

## Typical pipeline — enable (XR Origin already present)

```
pico_xr_status()                                     → xr_origin=ok, locomotion=off
pico_xr_locomotion(action=enable)                    → ok
pico_xr_status()                                     → locomotion=on  (internal verify)
Save Scene                                           → ok
```

### Typical pipeline — configure (enable first if off)

```
pico_xr_status()                                     → locomotion=on  (if off: enable first)
pico_xr_locomotion(action=configure, presets="Move,Turn,Gravity,Jump")
pico_xr_status()                                     → verify desired presets active
Save Scene                                           → ok
```

### Typical pipeline — disable

```
pico_xr_locomotion(action=disable)                   → ok
pico_xr_status()                                     → locomotion=off (internal verify)
Save Scene                                           → ok
```

## Notes

- Do NOT call `pico_xr_locomotion(configure)` without parsing the user's
  intent first. The default preset is `Default`; if the user said "all",
  pass `All`; if they said "off", they probably mean `pico_xr_locomotion(disable)`.
