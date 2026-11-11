---
name: pico-cli-device-target
description: Classifies a selected ADB target as real PICO hardware or an emulator. Use when device-type evidence is needed for screenshot mode selection or a target-specific workflow. NOT for capture, recording, app installation, or emulator lifecycle operations. Use pico-cli-screenshot for still capture.
license: 'Apache-2.0'
---

# PICO CLI Device Target

Classify the selected ADB target before screenshot mode selection. This skill
only distinguishes real PICO hardware from an emulator. It does not capture
screenshots, record videos, install apps, or choose a capture mode.

## When to Use

- Determining whether a connected ADB target is real PICO hardware or an emulator
- Pre-capture device classification when the capture mode depends on target type
- Verifying device type before choosing a platform-specific workflow

## When NOT to Use

- Capturing screenshots or images — use `pico-cli-screenshot`
- Camera movement or recording — use `capture-camera`
- Emulator lifecycle management — use `pico-emulator-usage`

## Resolution

1. Run:

   ```bash
   pico-cli device list --format json
   ```

2. Use `pico-cli device info --device <id> --format json` or
   `pico-cli device props --device <id> --format json` when the device list
   does not identify the target.
3. Classify each target:
   - an Android Emulator/AVD is `emulator`
   - connected PICO HMD hardware is `real-device`
   - if neither can be established, stop rather than guessing

Do not infer the target type from the serial format alone. Use the device
model, properties, and emulator state when available.

## Result

Return exactly one target type to the caller:

```text
emulator | real-device
```

If the type cannot be established, report the evidence used and do not return
a target type.
