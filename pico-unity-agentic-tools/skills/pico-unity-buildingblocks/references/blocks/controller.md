# Controller models

## Tool

`pico_xr_controller` — actions: `enable` / `disable` / `status`

## Dependency

- XR Origin present
- PICO controller-model prefabs in PICO SDK

## Cheatsheet

### Enable Controller
- Pre: XR Origin (via orchestration step B.1).
- Call: `pico_xr_controller(action=enable)`.
- If the C# layer returns `error` mentioning a missing prefab path under
  `Packages/com.bytedance.pico.xr/...`, the user's PICO SDK install is
  incomplete; do NOT auto-fix — relay the error and ask them to verify the
  PICO SDK is present.

### Disable Controller
- No deps to check.
- Call: `pico_xr_controller(action=disable)`.

### Status
- Call: `pico_xr_controller(action=status)`.

## Typical pipeline — enable (XR Origin already present)

```
pico_xr_status()                    → xr_origin=ok, controller=off
pico_xr_controller(action=enable)   → ok   (or error if PICO SDK prefabs missing)
pico_xr_status()                    → controller=on   (internal verify)
Save Scene                          → ok
```

### Typical pipeline — disable

```
pico_xr_controller(action=disable) → ok
pico_xr_status()                    → controller=off (internal verify)
Save Scene                          → ok
```

## Notes

- PICO controller prefabs ship with the PICO SDK already in the project.
  No extra package install is needed.
- If prefabs are missing, the C# layer will report `error` with a clear
  message; relay it verbatim and ask the user to install/update the PICO SDK.
- Do NOT auto-install the PICO SDK — it is outside the scope of these MCP tools.
