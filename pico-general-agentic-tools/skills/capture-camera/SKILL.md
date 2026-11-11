---
name: capture-camera
description: Controls viewpoints and camera trajectories in PICO spatial scenes. Use when composing a subject view, orbiting an object or app, moving or holding a camera pose, or recording continuous video. NOT for ordinary still screenshots, device classification, or emulator and application lifecycle operations. Use pico-cli-screenshot for ordinary still screenshots.
license: 'Apache-2.0'
---

# Capture Camera

Use `pico-cli camera` for camera control. `pico-cli capture camera` remains a compatible
entry to the same runtime. Camera movement and observation do not require a screenshot
or recording. Add `camera move --screenshot <new-path>` only when an endpoint PNG is
requested; `--out` stores plan evidence.

For a target-relative still, this Skill owns the pose or trajectory plan. Hand target
classification, capture-mode selection, and final readable-PNG validation to
`pico-cli-screenshot` without letting that handoff recompute the camera plan. A still
of the current or already-held view routes directly to `pico-cli-screenshot`.

Interpret user language in the Agent and send version-1 typed plans through `--intent-json`
to the CLI. The Agent fills the existing action parameters; the CLI does not need a
phrase or synonym matcher for every action. Explicit in-place rotation uses `kind: "in-place"` with no target or grounding
and keeps position fixed, even when no object is visible. Read
[language and local motion](references/language-and-local-motion.md) before compiling.

For centered observation, ground the subject and preserve the current direction with
a relative zero-angle `observe`. For moving subjects, use semantic tracking and fresh
frame/update evidence; [language and local motion](references/language-and-local-motion.md) gives the recipe.

Complete horizontal and vertical sweeps default to four seconds. Preserve explicit
user durations. Measure launch, grounding, preparation, recorder startup, motion,
finalization, and total wall time; motion duration alone is not recording latency.

Camera motion during recording is exposed only on emulators. On real devices,
camera movement without recording and moved-view screenshots remain supported,
as do ordinary screenshots and recordings at a held/current view. Stop an owned
ordinary recording before moving the real-device camera; never interrupt another
owner's recording to satisfy a rejected request.

Read the complete request, select its subject, and compile one ordered camera plan. The user names
objects and views; the Agent derives image rectangles. Never ask the user for world coordinates,
read private model transforms, or infer a target from an APK name.

Natural language is the Agent-facing input. Do not require the user or an upstream orchestrator to supply
CLI flags, image rectangles, world coordinates, a Pivot, probe poses, or typed camera JSON. When the
request names a subject and a direction or axis, identify that subject in fresh images, ground its
complete visible extent, derive its center axis, and preserve the requested direction in the
compiled plan. This includes top, bottom, side, back, horizontal, vertical, and center-axis views.
Missing precomputed targeting data is work for this Skill, not a reason to reject or reinterpret the
request as an in-place turn.

For a named subject's front, side, or back without an explicit numeric bearing, identify its facing
direction in the fresh images. Use visible shape cues such as a face, muzzle, tail, or front panel;
the initial camera view is not automatically the subject's front. Compile the requested semantic
view against the retained grounded reference. For example, when that reference already shows a
profile, another 90-degree orbit may show the face rather than the requested side. Inspect the
endpoint and correct the semantic bearing with the validated target if needed. Reuse the current
session's evidence for this decision; do not repeat grounding solely to rename a view.
Explicit numeric or relative angles retain their stated reference and value. Report geometric
bearing and observed subject-facing direction separately; a 90/180-degree readback alone does not
prove a side/back view.

## When to Use

- Natural-language camera movement, viewpoints, orbits, or recordings in a spatial scene
- Capturing a specific angle or composition of a 3D object or app window
- Recording continuous camera trajectories for demonstration or review

## When NOT to Use

- Static 2D screenshots of the current display — use `pico-cli-screenshot`
- Device target classification — use `pico-cli-device-target`
- Emulator lifecycle or app installation — use `pico-emulator-usage`

## Interpret The Request

- A named object is one target-centered subject. Ground only that object's complete visible
  rectangle.
- A named group is one target-centered composite. Ground every required member separately and use
  their union for the center axis and radius.
- "The whole App" is the union of all requested App-owned visible content, not the package name,
  background, or unrelated system UI.
- "Look around", "the surrounding space", or an explicit in-place turn has no subject target and
  keeps camera position fixed. Do not substitute it for "orbit around this object/group/App".
- A screenshot is endpoint evidence at the requested final view. A recording preserves the whole
  ordered trajectory in one recorder; do not replace one with the other.

Preserve explicit direction, angle, distance, action order, and relative-vs-grounded viewpoint.
Movement JSON always uses `distanceMeters`, never `distance`. When "a little" is the only amount, use
`0.01m`; any explicit numeric distance takes precedence.

For every natural-language request, generate the equivalent version-1 typed plan before
execution. Use the parameter contract and examples in
[language and local motion](references/language-and-local-motion.md). Preserve every
requested action in order, including compound translation and rotation. `sourceText`
retains the user's wording as context; it does not select actions. `--text` remains a
legacy explicit CLI input, not the Agent's translation route. Do not ask the user to
restate the request with a known phrase, and do not silently discard an unsupported clause.

## Ground The Subject

For one object, circle its tight visible rectangle. The rectangle must stop at the object's visible
silhouette: do not include its bed, floor contact patch, shadow, furniture, support surface, or a
nearby object just because it is touching or visually behind the subject. If the requested object is
animated, use the object's activity envelope, not the room or support underneath it. For a requested
group or the App's visible subject, circle each required member separately; `target.members` is
their minimum rectangle union. Exclude unrelated scenery and shadows. Rectangles use normalized
`[left, top, right, bottom]` in the full emulator screenshot. CLI `--target-roi` instead uses
`left,top,width,height`.

Before compiling any target-centered orbit, compare the proposed one-object rectangle with the
fresh frame. If its long side is mostly caused by background, furniture, bedding, floor, or another
static support rather than the named object itself, discard it and re-mark the object body. A broad
single rectangle that makes the object plus support rotate together is invalid evidence, even if
the runtime command would execute successfully.

If the named subject is not visible, search before rejecting the task or using an in-place turn:
`pico-cli capture camera search --device <serial> --out <new-directory> --format json`.
Inspect every returned frame and choose the tightest complete view. Move to its reported angles with
`capture camera batch`, mark a fresh rectangle, and refine a near-edge result with a bounded probe.
Never reuse the pre-search rectangle or treat a search frame as `sideValidation` or `verticalValidation`; search only reacquires the visible subject.

Use the initial probe's origin frames as the first subject image; a separate initial screenshot
is unnecessary. They are fresh full spatial views and also supply the grounding evidence.
If an extra standalone screenshot is needed for semantic feedback, use
`pico-cli capture screenshot --device <serial> --spatial --size 1920x1080 --out <new-path> --format json`.
Keep the same full viewport as the probe; an ordinary display screenshot can have different optics.

Obtain two fresh views and their actual camera poses:

```bash
pico-cli capture camera probe --device <serial> --out <new-directory> --offset 0.2 --format json
```

For a character or animal whose animation state is unknown in the current session, add
`--animated` to the first probe. This obtains the activity window immediately instead of collecting
a static probe and then repeating it for animation. Determine motion from these fresh frames,
never from the APK name or earlier observations.

For animation, add `--animated`. Each viewpoint retains at least two frames over at least two
seconds; slow native captures can extend this window. Inspect every returned frame and use each
member's maximum activity rectangle for that viewpoint. Animated probes return
an additional restored-origin group after the lateral group: `probe-0-*` (before), `probe-1-*`
(lateral), and `probe-2-*` (after). Keep the before and after rectangles.

When a fresh probe returns `contactSheet`, open `contactSheet.path` once to inspect every frame
in that run. Numbered tiles follow capture order; `contactSheet.tiles` maps each number to its
original `path`, basename, frame index, Pose, source size, and pixel `imageBounds` in the sheet.
The sheet is an additional visual aid, never replacement evidence. Ground normalized rectangles
within each tile's image area, not the entire sheet or its label strip; they refer to the full
original viewport. Inspect the mapped full-resolution PNG when detail or an edge is uncertain.
Keep every frame when deriving activity envelopes and representative members. If composition
returns a warning without a sheet, inspect every original frame. Never reuse an older sheet.

If the request includes a vertical angle, use `--axis up --offset 0.2` for this
initial probe. Reuse its exact offset Pose and representative members as
`verticalValidation`, with that run's before/after rectangles for animation.
Then collect one independent lateral probe, normally `--offset 0.3`, for
`sideValidation`. This grounds both axes with two probe runs instead of three.
Do not reuse an initial observation as side validation. Vertical reuse requires
both the exact Pose and exact members; similar positions or re-marked rectangles
are not interchangeable evidence.
Choose an interior offset above `0.15m` if a smaller complete view is needed;
an exact minimum offset can round below the baseline limit at a translated origin.

Ground the same subjects in both images, retaining their returned poses in
`target.observations`. These are camera poses measured by the CLI, not model world coordinates.
Only use frames from the current App and camera session.

For an animated target, keep two distinct rectangles: `target.members` is the maximum activity
envelope for framing, while each `observations[].members` rectangle must come from one complete
representative frame near the median center for that viewpoint. Never use an activity envelope's
center as a parallax ray: changing legs, tail, or pose would masquerade as camera translation.

Silhouette centers from nearby parallel views can lie on the object's near surface, especially on
a flat board or moving subject. Two probe views create only a provisional fit. Do **not** create a
third validation image by issuing a target-centered 60-degree observation from that provisional
fit: it can make a multi-metre move around the wrong pivot.

Before any target angle or `sweep`, collect the third independent ray with a bounded lateral probe
from the original view. Use an offset between `0.15m` and `0.75m`, keep the wide-probe position at
least `0.15m` from every initial probe pose, and choose the largest offset whose representative
frame remains complete with margin. For a close animated subject, a `0→0.15m` initial probe and a
`0→0.3m` wide probe are often preferable to a clipped `0.6m` probe:

```bash
pico-cli capture camera probe --device <serial> --out <new-directory> --offset 0.6 --format json
```

Circle the same subject in a returned offset frame and use that frame's actual Pose and exact
members as `target.sideValidation`. The field name remains `sideValidation`, but its source is the
wide lateral probe, not a target orbit. The full member union must remain at least 3% inside every
viewport edge. If the subject is clipped or too close to an edge, reset and take a smaller bounded
lateral probe; never use a guessed radius or a provisional target orbit to obtain this evidence.
The runtime checks baseline, edge margin, forward ray distance, and ray intersection before it
changes the camera.

For an animated target, add `--animated` to this wide probe and attach its before/after original
view rectangles in `sideValidation.motionReference`. The runtime aligns the lateral ray's
midpoint motion to the first target observation before fitting depth and rejects it if the
compensated rectangle reaches within 3% of an edge. Keep that first observation as the common
reference across probe runs. Do not estimate before/after motion from a different probe run.

For any vertical target angle or vertical sweep, use the fresh initial-up probe above
or collect a separate vertical probe from the original view:

```bash
pico-cli capture camera probe --device <serial> --out <new-directory> --offset 0.35 --axis up --format json
```

Circle the same subject in that returned offset frame and use that frame's actual Pose and members
as `target.verticalValidation`. For animated targets, collect this probe with `--animated` and
attach its before/after original-view rectangles in `verticalValidation.motionReference`. A combined
horizontal+vertical orbit is valid only after both `sideValidation` and `verticalValidation` have
been grounded from fresh probe images. Do not start the recording or sweep from guessed JSON poses,
old rectangles, or an unvalidated current camera angle.

Submit the actual probe Pose and tight members with the requested target angle or sweep:

```json
{
  "target": {
    "members": [[0.2, 0.3, 0.8, 0.7]],
    "animated": true,
    "observations": ["the two fresh probe observations"],
    "sideValidation": {
      "pose": { "position": [0.6, 0, 0], "rotation": [1, 0, 0, 0] },
      "members": [[0.25, 0.4, 0.5, 0.7]],
      "motionReference": {
        "beforeMembers": [[0.3, 0.4, 0.55, 0.7]],
        "afterMembers": [[0.28, 0.4, 0.53, 0.7]]
      }
    },
    "verticalValidation": {
      "pose": { "position": [0, 0.35, 0], "rotation": [1, 0, 0, 0] },
      "members": [[0.3, 0.5, 0.55, 0.75]],
      "motionReference": {
        "beforeMembers": [[0.3, 0.4, 0.55, 0.7]],
        "afterMembers": [[0.28, 0.4, 0.53, 0.7]]
      }
    }
  }
}
```

These numbers only demonstrate the contract. `sideValidation` and `verticalValidation` must use the
current candidate images and returned Poses, never copied rectangles, fixed world coordinates, or a
pose from a target orbit. `motionReference` is only for the same animated probe's before/after
origin frames.
Keep the requested final angle unchanged.

The [target schema](references/grounding-recovery.md#target-schema) lists the grounded member and observation fields.

These numbers only demonstrate the schema; derive actual values from current frames.
`framing: "medium"` is the default: the subject union targets a centered, readable longest side of
about `45%` of the viewport, with an acceptable `37%–53%` band. Use `"wide"` (`32%`) only for an
explicit overview/context request; use `"close"` (`55%`) only for an explicit close view. An explicit
`coverage` is the desired longest-side ratio and is limited to `0.25–0.65`; never use a fixed world
radius to obtain a framing. Treat coverage as an adaptive composition request, not a strict
acceptance threshold; preserve a reliable subject axis and radius before fine scale tuning.

After each target-centered move, inspect the new screenshot. If the subject is complete but too close,
too far, or off-center, submit the fresh semantic members in a `refine: true` target. The runtime
refines the pivot, returns `geometry.framing.adjustment` (`retreat`, `approach`, or `hold`), and changes
the next orbit radius from that current frame. Each correction keeps the radius change between `0.7x`
and `1.4x`: it prevents one uncertain fit from jumping into a crop while still allowing the Agent to
converge from new semantic feedback. This is a product capability, not a debugging rule:

For the first target frame, a complete subject that is merely larger than the requested composition
does not trigger an automatic retreat from a parallax estimate. It stays at the measured current
radius; only this fresh post-move semantic `refine` can authorize a retreat.

```json
{
  "version": 1,
  "target": {
    "members": [[0.12, 0.18, 0.88, 0.82]],
    "animated": true,
    "refine": true,
    "framing": "medium"
  },
  "steps": [{ "kind": "observe", "horizontalDegrees": 0, "verticalDegrees": 0 }]
}
```

The returned result includes `targetRadiusMeters` and `framing`; re-screenshot after the one
correction before deciding whether another fresh refine is needed. Do not repeatedly guess fixed
radii. Keep the moving subject's activity envelope when refining it; a single animation phase
does not establish its maximum extent. Static refinements refit parallax rays; animated refinements
update the fresh semantic direction at the established range instead of fitting different phases
to one fixed center. After grounding, reuse held geometry for later views; reground after the subject, App, or
viewport changes.

Before collecting a full target-centered orbit, first capture one prepared front view and inspect
the named subject. Do not treat the full orbit as the framing preflight. The returned
`geometry.framing` describes the input rectangles, not a measurement of the resulting screenshot.
Accept a complete, centered fresh image within the requested composition band without another
refinement, even when that earlier input reported `approach` or `retreat`. If the fresh image shows
the subject materially off-center, incomplete, or at the wrong scale, submit fresh members with `refine: true` and
recheck the front view before starting the orbit. A later orbit whose images show systematic
subject-center or scale drift does not pass merely because all poses lie on a precise circle:
reset, reground/refine from fresh images, and rerun the same natural-language request. Only report a
functional failure after the input and refinement mechanism has converged and the stable product
behavior still violates the request.

When using CLI target flags instead of a complete plan, pass the probe data through
`--target-observations <json>` on the initial target-centered command. A target without either
these observations or `refine: true` is rejected by the low-level runtime before it changes the
camera. This is an internal input guard, not a user-facing refusal path: collect the missing fresh
grounding and retry the same natural-language request. If the Skill repeatedly compiles an invalid
payload, fix the Skill/runtime mechanism rather than asking for a more implementation-specific
prompt.

## Close The Feedback Loop

A fresh Agent launches the selected model App once on the selected existing target.
Inspect whether that target App is already running before launching it. If another
model fixture from this task is visible, stop that fixture before launching the
selected App; preserve unrelated Apps. Compose the complete subject centrally
before recording. Do not launch another instance to repair framing.

A new Agent must complete target grounding and composition from fresh visual evidence without
precomputed rectangles, Poses, pivots, radii, or intervention from a previous Agent. Grounding is an
iterative visual control loop, not a one-shot command:

1. Capture a fresh front image, identify the named subject, and mark its complete visible extent.
2. Collect the required lateral and vertical probes and submit their actual Poses and fresh members.
3. Treat validation and geometry responses as feedback. Adjust only the input that the response
   identifies, then retry from a fresh image.
4. Capture a prepared front view before the requested endpoint. Inspect subject identity,
   completeness, center error, scale, and edge margin.
5. If identity or the fitted axis is wrong, reset and reground with corrected same-subject members.
   If identity and axis are right but scale or centering is wrong, submit one fresh `refine: true`
   correction, re-screenshot, and repeat while the result is still converging.
6. Execute the original natural-language endpoint or trajectory only after the preflight view is
   acceptable. Inspect the final screenshot or recording; if it exposes a stable grounding or
   composition error, reground or refine and rerun the same request.
7. Reset and verify cleanup after success, cancellation, or an unrecoverable error.

Load [grounding recovery](references/grounding-recovery.md) for the required response to probe,
framing, refinement, stale-evidence, and transport failures. Apply it within this feedback loop.

Continue until the requested media passes visual inspection under the user's acceptance criteria,
or a stable functional failure remains after valid fresh feedback. Judge usability from the
requested view, readable subject, and continuous motion; apply exact composition metrics when requested.
Do not stop after the first recoverable grounding, baseline, ray-intersection, edge-margin
or composition rejection. For insufficient parallax, increase the bounded probe offset; for clipping,
decrease the bounded probe offset; for a wrong subject axis, tighten the semantic members, and reground.
Use the returned failure to change the next input, and never
repeat the same rectangle, probe distance, or stale frame after it has already failed.

## Compile Once, Execute In Order

Use one version-1 plan with `steps`, like the terminal's ordered action mechanism. Preserve all
actions, units and fractional angles. One CLI invocation executes the plan through the same
device worker and Pose stream.

```json
{
  "version": 1,
  "sourceText": "view from the upper left at 30 degrees, move forward 20 centimeters, reset",
  "target": { "members": [[0.2, 0.3, 0.8, 0.7]], "animated": false },
  "steps": [
    { "kind": "observe", "horizontalDegrees": -30, "verticalDegrees": 30 },
    { "kind": "move", "direction": "forward", "distanceMeters": 0.2 },
    { "kind": "reset" }
  ]
}
```

Insert the measured observations and the fresh bounded-probe `sideValidation` into this target
before any nonzero target angle or full-subject sweep.

```bash
pico-cli capture camera batch --intent-json @camera-plan.json --device <serial> --format json
```

`capture camera move` accepts the same plan. The Agent compiles simple and complex
descriptions into typed parameters before execution. Keep all actions in order;
do not reduce a compound request to its first direction.

| Step            | Fields                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------- |
| `observe`       | `horizontalDegrees`, `verticalDegrees`, optional `relative`, `radiusMeters`, `durationMs`, `screenshot` |
| `observe` sweep | `sweep: "horizontal"` or `"vertical"`, optional `durationMs`                                            |
| `in-place`      | Angle fields or `sweep`; position stays fixed and no target is required                                 |
| `move`          | `direction: left/right/up/down/forward/backward`, positive `distanceMeters`                             |
| `reset`         | Restore original pose; a final reset outside recording also closes injection ownership                  |

Positive observation horizontal means right, negative left; positive vertical means above, negative
below. Both axes of “upper left 30 degrees” use 30 degrees. “From here”, “another”, or “relative”
uses `relative: true`; otherwise an observation uses the grounded reference. Moves use current
camera axes. Preserve decimal angles and convert centimeters/millimeters to meters.

Ordinary fixed and horizontal observations stay world upright without an extra camera roll.
An explicit vertical 360 follows one continuous great circle through top, back, bottom and front;
its continuous pole passage is not replaced with an endpoint flip.

## Screenshots And Recording

For current-view/held-camera stills, follow `pico-cli-screenshot` for target-specific mode and PNG validation.
For a new intent-based view, use the dedicated camera path (do not add `--spatial` or `--size`):

```bash
pico-cli capture screenshot --intent-json @view-plan.json --device <serial> \
  --out <new-view.png> --format json
```

The intent-based command executes the requested view, captures there, then restores the camera state
held before the call. It is rejected while a recording owns the camera, because an unowned pose
move would contaminate the requested video; a current-view screenshot remains safe while the Pose
is held. Without a held camera, the command closes its injection after capture. Do not end the plan
with reset, which would photograph the original view. Inspect the requested-angle image for center,
completeness, scale and upright orientation.

For a complete orbit, use a grounded typed sweep:

```bash
pico-cli capture record --intent-json @orbit-plan.json --device <serial> \
  --out <new-video.mp4> --time 12 --format json
```

The CLI prepares the subject before recording, starts one recorder, executes the continuous
trajectory, stops the recorder, and resets. A full horizontal and full vertical pair uses two
ordered sweep steps. The duration is shared across the steps.

For an entire task across multiple CLI calls:

```bash
pico-cli capture record start --session <id> --device <serial> --time 1800 --format json
pico-cli capture camera batch --intent-json @camera-plan.json --device <serial> --format json
pico-cli capture record stop --session <id> --format json
pico-cli capture camera reset --device <serial> --format json
```

`record start` waits for recorder readiness. The same worker and Pose stream continue through
successful camera commands and a reset during recording. Stop uses the same evidence session and
recording ownership ID. Never kill a generic recorder, assemble video from screenshots, or substitute
per-frame shell connections. A screenshot can be taken while the camera Pose is held.

For position-invariant full panoramas:

```bash
pico-cli capture record --camera-in-place --camera-axis horizontal --device <serial> \
  --out <new-video.mp4> --time 12 --format json
```

Use `vertical` for a vertical panorama. This rotates virtual surroundings; it does not rotate
physical headset cameras on a real device.

## Semantic Dynamic Tracking

For semantic tracking, load `references/semantic-dynamic-tracking.md` before preparing or
recording. It preserves the public target contract, exact command order, frame freshness, response
handling and owned-recording `target-lost` boundary. Keep the same camera worker, Pose stream and
recorder throughout that workflow.

## Six Faces

Use the same grounded target and six `observe` steps, each with its own `screenshot`:

| Face   | Horizontal | Vertical |
| ------ | ---------- | -------- |
| front  | 0          | 0        |
| right  | 90         | 0        |
| back   | 180        | 0        |
| left   | -90        | 0        |
| top    | 0          | 90       |
| bottom | 0          | -90      |

Execute one batch and reset after its images are saved. Material backface culling or occlusion can
hide a face; report the actual view rather than claiming that a reached Pose proves visible content.

## Results And Lifecycle

Read `capture camera get` for the actual pose, original pose, geometry, stream PID and injection
state. A completed command is evidence of motion; judge centering and scale from the actual media.
The requested subject union should remain basically at viewport center, with a readable size and
edge margins. Keep genuine rendering/occlusion limitations explicit.

Before emulator recording, the CLI disables adaptive VSYNC and reports
`emulatorVsyncAdjust: "false"` for the capture period. It restores `true` with readback after
completion, failure or cancellation. Check MP4 cadence and continuity, not just its existence.
The closed feedback loop above is required and stays inside this Skill and the current Agent
session; it does not require a separate metadata provider, color histogram, or external replan
service.
Invalid inputs and real device/transport errors remain errors; they must not be reported as success.

All visible camera moves use one `inject-hmd-stream` connection. Reset restores the original Pose,
closes the stream, and restores the tracking property. Emulator reset preserves default physical
mouse tracking and never calls `disable`; real devices restore their tracking source.
Idle expiry, cancellation and worker termination retain the lease/watchdog cleanup contract.
