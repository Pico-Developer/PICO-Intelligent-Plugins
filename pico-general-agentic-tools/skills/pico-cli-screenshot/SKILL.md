---
name: pico-cli-screenshot
description: Captures and validates PICO screenshots with pico-cli. Use when capturing a screenshot, 2D image, spatial FOV, layer image, or visual evidence on an emulator or connected PICO device. NOT for camera movement, continuous recording, target classification, or emulator startup. Use capture-camera for camera movement or recording.
license: 'Apache-2.0'
---

# PICO CLI Screenshot

Capture a real screenshot through `pico-cli` and return inspectable evidence.
This skill owns screenshot mode selection and artifact validation, but target
classification belongs to `pico-cli-device-target`.

## When to Use

- Capturing a 2D screenshot from an emulator or connected PICO device
- Spatial FOV or layer capture for visual evidence
- Validating app UI appearance after a build or deployment

## When NOT to Use

- Camera movement, orbits, or continuous recording — use `capture-camera`
- Device target classification — use `pico-cli-device-target`
- Emulator startup or app installation — use `pico-emulator-usage`

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
  -p /data/local/tmp/<unique-capture-id>.png --device <id>
pico-cli files pull /data/local/tmp/<unique-capture-id>.png <path> --device <id>
```

Allocate a unique remote filename for this attempt. After pull/validation, or on failure,
remove only that attempt's remote temporary file on the same device; never delete a shared
filename or another capture's artifact. Report cleanup failures separately from capture results.

The high-level `pico-cli capture screenshot` command remains the preferred
path because it handles temporary files and host-side PNG validation.
