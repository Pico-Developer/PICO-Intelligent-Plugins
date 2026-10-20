---
name: pico-cli-screenshot
description: Captures and validates PICO screenshots with pico-cli. Use for screenshot, 2D image, spatial FOV, layer capture, or visual evidence requests on an emulator or connected PICO device. Do not use for recording.
license: 'Apache-2.0'
---

# PICO CLI Screenshot

Capture a real screenshot through `pico-cli` and return inspectable evidence.
This skill owns screenshot mode selection and artifact validation, but target
classification belongs to `pico-cli-device-target`.

## Required Target Gate

Before choosing a capture mode, load `pico-cli-device-target` and resolve:

```text
emulator | real-device
```

Keep the selected device ID from the caller and do not capture when the target
is missing, ambiguous, or cannot be classified.

## Capture Selection

- real-device: use the spatial FOV path by default:

  ```bash
  pico-cli capture screenshot --device <id> --spatial \
    --size 1920x1080 --out <path>
  ```

  Do not try ordinary capture first. On PICO hardware it may produce
  distorted or tiled output, or fail.

- emulator with a flat 2D surface:

  ```bash
  pico-cli capture screenshot --device <id> --out <path>
  ```

- `emulator` with spatial content: use the spatial FOV path with the requested
  size.
- Add `--layer-id <id>` only when the request names a specific spatial layer.
- Pass `--replace` only when overwriting an existing artifact is explicitly
  allowed.

The capture command is a screenshot operation only. Do not route recording
requests here.

## Validation

After the command succeeds:

1. Confirm the output path exists on the host.
2. Confirm the file is a readable PNG, not just a successful command message.
3. Record the target type, device ID, capture mode, dimensions, and artifact
   path.
4. If capture fails or the image is distorted, report the exact failure and
   do not present the artifact as valid evidence.

Use the raw escape hatch only when the installed CLI does not expose the
required screenshot option:

```bash
pico-cli adb shell screencap --spatial --size 1920x1080 \
  -p /data/local/tmp/pico-screenshot.png --device <id>
pico-cli files pull /data/local/tmp/pico-screenshot.png <path> --device <id>
```

The high-level `pico-cli capture screenshot` command remains the preferred
path because it handles temporary files and host-side PNG validation.
