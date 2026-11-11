# Semantic Dynamic Tracking

Use the top-level `camera` family for this recipe; `capture camera` remains compatible.
Without recording, the same grounded semantic observation can hold a subject centrally.
Classify the target before adding recording: all camera motion during recording is
emulator-only. Real devices retain moved-view screenshots, camera observation without
recording, and ordinary recording at a held view.

For a moving subject whose silhouette can travel farther than local visual matching can prove, add
the following public semantic tracking contract to a valid grounded target (including the actual
probe `observations`). It keeps the camera worker, one Pose stream, and the current recording intact
while the Agent supplies fresh visible members:

```json
{
  "target": {
    "members": [[0.24, 0.35, 0.68, 0.72]],
    "animated": true,
    "framing": "medium",
    "tracking": {
      "mode": "semantic",
      "centerDeadband": 0.08,
      "scaleDeadband": 0.08,
      "cooldownMs": 1500,
      "maxViewportStep": 0.06,
      "maxRadiusStepMeters": 0.12,
      "semanticFrameMaxAgeMs": 15000
    }
  }
}
```

Start a long `observe` step using this grounded target, then repeat the following only while that
step is running:

```bash
pico-cli camera prepare --intent-json @semantic-track-plan.json --device <serial> --format json
pico-cli capture record start --session <id> --device <serial> --out <new-video.mp4> --time 180 --format json
pico-cli camera batch --intent-json @semantic-track-plan.json --device <serial> --format json
pico-cli camera frame --device <serial> --out <new-frame.png> --format json
pico-cli camera update --device <serial> --frame-sequence <sequence> \
  --target-members '[[left,top,right,bottom], ...]' --format json
pico-cli camera update --device <serial> --frame-sequence <sequence> \
  --target-lost --format json
pico-cli camera tracking --device <serial> --format json
```

`prepare` grounds the tracking target before the single recorder starts, so a recording with
`target.tracking` never silently falls back to a stale screenshot path. The actual motion interval
uses one screen recorder while the tracking preview samples low-frequency current-view screenshots,
so no host media decoder is required. `frame` returns a `sequence` bound to the current worker
preview. Mark the
subject or each required member on that exact PNG and pass the same sequence to `update`. Do not reuse
a sequence after the configured frame age. The update response is authoritative:

| Response                                               | Agent action                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `accepted` + `correctionQueued: true`                  | Keep observing; the bounded, smoothed center/radius correction is now in the shared trajectory.                                                                                                                                                                                               |
| `within-deadband`                                      | Continue recording; the current frame is already inside the requested composition band.                                                                                                                                                                                                       |
| `cooldown`                                             | Wait for a newer frame; do not retry the same frame.                                                                                                                                                                                                                                          |
| `frame-expired`, `frame-not-found`, `pose-not-aligned` | Request a new frame, re-mark its members, then submit one update.                                                                                                                                                                                                                             |
| `target-lost`                                          | For screenshots or pre-recording setup, stop local correction and run `capture camera search` to reacquire the subject before regrounding. During an owned recording, let the recorder finalize; its stop/result returns `CAMERA_TARGET_LOST` with the preserved MP4 and frame/Pose evidence. |

`centerDeadband`, `scaleDeadband`, `cooldownMs`, `maxViewportStep`, and
`maxRadiusStepMeters` are product controls, not debug constants. Keep a small deadband and bounded
step for stable coverage; lower the deadband or raise the per-step limits only when the caller
explicitly needs faster response. Report `--target-lost` only when the subject is not observable in
the exact exported frame. It is one terminal observation, not a confidence or safety level: the
runtime freezes the last acknowledged Pose, interrupts the active trajectory, and skips later
camera steps. A separately owned recording can still finalize and preserve its video before
returning failure; finalize it with `capture record stop`.

`capture camera tracking` is immediate while a long `batch` owns the motion queue. Use it to read
the active policy, number of accepted updates, queued corrections, and the last decision; do not use
the serialized `capture camera get` as a progress poll during that batch.
