# Language and Local Motion

Interpret the user's complete description in the Agent and send version-1 `--intent-json`
parameters. Preserve all directions, angles, distances, units, media and compound action order;
do not forward Agent requests to the finite `--text` phrase parser.
After a specified translation, looking toward a subject uses `in-place` angles derived from its
fresh bearing, preserving the movement endpoint. A centered `observe` may add translation.

For an explicit in-place rotation or looking around, immediately compile
`kind: "in-place"` with no `target`. Do not identify objects, fit a center axis,
probe, or reject because no object is visible. Keep camera position fixed.
Previously held geometry does not change this request into an orbit.

For a requested right90-degree turn, use:

```bash
pico-cli camera move --device <serial> --intent-json \
  '{"version":1,"steps":[{"kind":"in-place","horizontalDegrees":90,"verticalDegrees":0}]}'
```

Positive horizontal angles turn right; negative angles turn left. Positive
vertical angles look up; negative angles look down. Preserve explicit durations
as `durationMs`; ordinary steps otherwise use the existing450ms default.

For a complete in-place turn, use `kind: "in-place"` and `sweep: "horizontal"` or
`"vertical"`. Complete turns default to four seconds. Translation steps likewise
do not need a subject. Ground only requests to center, inspect, or orbit a named
object, group, or App. Add media only when requested; hold the resulting camera
pose until an explicit restore request or task completion.

For requests to keep an object centered, ground it from fresh probe images and
use an English `camera move --text` instruction with that target, or a typed
zero-angle `observe` step with `relative: true`. Preserve the current observation
direction. For moving subjects, add `target.tracking.mode: "semantic"` and the
requested duration, then supply fresh `camera frame` / `camera update` members
during that window. Never invent a centered view when grounding is absent.

Endpoint capture returns `frame` evidence. Preserve an `unconfirmed` warning/PARTIAL result;
a pose ACK and successful PNG write alone do not prove the requested viewpoint is rendered.
