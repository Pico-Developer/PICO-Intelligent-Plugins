# Grounding Recovery

Apply this policy inside the current camera session after each fresh probe or prepared view.

| Feedback or observation                                                                       | Required Agent action                                                                          |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Subject rectangle includes support, scenery, or another object                                | Re-mark the named subject from the fresh image; do not move the camera yet.                    |
| Subject is clipped or within the required edge margin                                         | Reset and retry a smaller bounded probe offset.                                                |
| Probe baseline is too small or rays are nearly parallel                                       | Reset and increase the bounded probe offset while the subject remains complete.                |
| Probe baseline is too large or the target leaves the frame                                    | Reset and decrease the bounded probe offset.                                                   |
| Side or vertical rays do not intersect consistently                                           | Reinspect coordinate orientation and same-subject rectangles, collect fresh probes, and refit. |
| Prepared view contains the wrong subject or rotates around a support                          | Discard the geometry, tighten the semantic members, and reground.                              |
| Subject is complete but too large, too small, or off-center                                   | Submit fresh members with `refine: true`, then re-screenshot and reevaluate.                   |
| A refine changes scale in the correct direction but remains outside the requested composition | Continue with another fresh refine; never guess a fixed radius.                                |
| A recoverable CLI input guard rejects missing or stale evidence                               | Collect the named fresh evidence and retry the unchanged natural-language goal.                |
| Device, transport, or rendering failure repeats without new usable evidence                   | Preserve the last evidence, clean up, and report the actual blocker.                           |

Do not stop after the first recoverable grounding, baseline, ray-intersection, edge-margin,
framing, or stale-frame rejection. Do not claim success from Pose geometry alone. Continue until
the requested media passes visual inspection, or until repeated fresh evidence shows no progress
and identifies a concrete non-recoverable blocker. Keep retries bounded and evidence-driven: never
repeat the same rectangle, probe distance, or stale frame after it has already failed.

## Target Schema

```json
{
  "members": [
    [0.2, 0.3, 0.5, 0.7],
    [0.6, 0.4, 0.8, 0.6]
  ],
  "animated": false,
  "framing": "medium",
  "observations": [
    {
      "pose": { "position": [0, 0, 0], "rotation": [1, 0, 0, 0] },
      "members": [
        [0.2, 0.3, 0.5, 0.7],
        [0.6, 0.4, 0.8, 0.6]
      ]
    },
    {
      "pose": { "position": [0.2, 0, 0], "rotation": [1, 0, 0, 0] },
      "members": [
        [0.15, 0.3, 0.45, 0.7],
        [0.55, 0.4, 0.75, 0.6]
      ]
    }
  ]
}
```

Example values demonstrate the schema; derive all members and poses from current-session images.
