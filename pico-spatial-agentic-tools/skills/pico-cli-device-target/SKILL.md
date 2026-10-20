---
name: pico-cli-device-target
description: Classifies a selected ADB target as real PICO hardware or an emulator. Use before screenshot capture when the capture mode depends on the target type. Do not perform capture or other device workflows.
license: 'Apache-2.0'
---

# PICO CLI Device Target

Classify the selected ADB target before screenshot mode selection. This skill
only distinguishes real PICO hardware from an emulator. It does not capture
screenshots, record videos, install apps, or choose a capture mode.

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
