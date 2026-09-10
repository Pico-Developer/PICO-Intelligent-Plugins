# Scene Validation

Read this reference before declaring a PICO Spatial SDK scene complete.

## Contents

- Validate the source
- Build and launch
- Collect runtime evidence
- Review the complete scene
- Handle failures
- Report completion

## Validate the Source

Inspect the final diff and confirm that the intended app path owns the scene.
Check that the implementation:

- loads or creates each required Entity exactly once per scene lifecycle
- attaches the intended hierarchy before bounds-dependent placement
- uses public coordinate conversion and bounds APIs
- applies transforms in the correct parent or owner space
- retains a base transform or otherwise makes updates idempotent
- destroys or deliberately retains the scene when its owner leaves composition

When the implementation contains bounds-aware placement, run the bundled gate
after the final source edit:

```bash
python3 /absolute/path/to/spatial-sdk-scene-builder/scripts/check-placement-source.py \
  --source app/src/main/java/com/example/scene/MuseumScene.kt \
  --source app/src/main/java/com/example/scene/Placement.kt \
  --out artifacts/reports/placement-source-check.json
```

Resolve the gate path relative to this skill's `SKILL.md`. Pass only the Kotlin
files or focused directories that implement the changed scene or placement;
repeat `--source` as needed. Use `--source-root` only when the entire selected
directory is placement-specific. Do not scan a whole app merely because it is
the default Android module: unrelated Compose code can legitimately use density
or physical-length APIs.

The gate intentionally separates high-confidence `violations` from heuristic
`advisories`. Violations determine `passed` and the process exit code.
Advisories never change either one: they highlight patterns worth reviewing,
such as an unnamed bounds owner, resource construction in `SpatialView.update`,
repeated identical mesh factories, incomplete containment-evidence signals,
center-only containment, or a target-inclusive region.

Do not mechanically rewrite valid code just to remove an advisory. Project
helpers, split source files, and deliberate composition choices can supply the
missing context; review each advisory against the selected scope and explain
why it applies or does not. Positive API counts are also informational because
not every valid placement needs every API and accepted helpers may hide the
direct call. Fix reported violations rather than weakening the gate. A passing
gate does not prove that the scene looks correct or that every runtime
constraint holds.

## Build and Launch

Use `spatial-app-dev-workflow` for the enclosing edit/build/install/launch loop.
Use `spatial-emulator-usage` for emulator or device selection, screenshots,
recordings, and logs.

After the final edit:

1. Build the affected app and resolve compilation errors.
2. Install and launch the intended activity or experience.
3. Watch for crashes, asset-load failures, and relevant log errors.
4. Navigate to the scene and allow asynchronous assets and layout to stabilize.
5. Re-run the scene after lifecycle recreation when duplicate or stale Entities
   are a plausible risk.

## Collect Runtime Evidence

For each hard spatial relationship, emit or collect structured evidence that
uses one compact contract:

```json
{
  "sceneRevision": "window-size-or-content-revision",
  "constraintId": "stable-relationship-id",
  "target": { "id": "...", "boundsScope": "body" },
  "referenceId": "optional-support-or-anchor-id",
  "region": {
    "id": "optional-independent-region-id",
    "source": "explicit-owner-local-region",
    "bounds": { "min": [0, 0, 0], "max": [0, 0, 0] }
  },
  "boundsOwner": "placementOwner",
  "safeRegion": {
    "source": "SpatialView-and-WindowContainer-intersection",
    "bounds": { "min": [0, 0, 0], "max": [0, 0, 0] }
  },
  "baseDesignEnvelope": { "min": [0, 0, 0], "max": [0, 0, 0] },
  "selectedTransform": {
    "uniformScale": 1.0,
    "translation": [0, 0, 0]
  },
  "finalPlannedBounds": { "min": [0, 0, 0], "max": [0, 0, 0] },
  "finalVisualBounds": { "min": [0, 0, 0], "max": [0, 0, 0] },
  "margin": [0, 0, 0],
  "epsilon": 0.001,
  "numericStatus": "PASS",
  "conflictAxis": null,
  "reason": null,
  "visualStatus": "UNOBSERVED"
}
```

Use `numericStatus` values `PASS`, `FAIL`, or `BLOCKED`. For `FAIL`, populate
the exact `conflictAxis` (`X`, `Y`, `Z`, or a named multi-axis set); for
`BLOCKED`, record the missing or stale evidence in an adjacent reason field.
Use `visualStatus` values `PASS`, `FAIL`, or `UNOBSERVED` independently of the
numeric result.

Omit genuinely inapplicable optional objects, but do not omit the named bounds
owner, revision, bounds scope, selected scale/translation or placement delta,
final planned and remeasured visual bounds, epsilon, and result. For a bounded
complete scene, also include the safe region and base design envelope. A
permitted region must have provenance independent of the target; a target-
inclusive union cannot prove containment.

For placement code, one `SpatialPlacementEvidence` record may carry this data.
Do not accept an unexplained `Vector3`, a pivot/center-only assertion, or a
screenshot alone as proof of a hard containment, contact, or non-overlap
requirement.

## Review the Complete Scene

Capture viewpoints that show the entire composition and any important local
relationship. Review:

- object presence and asset-load success
- hierarchy-driven grouping and orientation
- human-scale proportions and relative scale
- focal point, spacing, occlusion, and overall composition
- clipping against the intended SpatialView or WindowContainer
- behavior after resize, animation, tracking, manipulation, or lifecycle changes
  when those behaviors are in scope

Visual review proves scene quality that coordinate records cannot. Numeric
evidence proves hard spatial constraints that a favorable camera angle can hide.
Require both when the contract contains both kinds of acceptance criteria.

Mark an important relationship `visualStatus = UNOBSERVED` when the available
capture cannot reveal its relevant axis. In particular, a front view cannot by
itself establish a visual pass for body/support or body/container depth along Z.
Do not add validation-only camera or scene-pose workarounds to this skill; report
the missing viewpoint for the enclosing validation workflow to resolve.

## Handle Failures

Stop and report the exact condition when required asset evidence is unavailable,
a visual bound is empty, a logical region is undefined, coordinate spaces are
incompatible, measured data is stale, an exact relationship conflicts with
containment, or the target does not fit on an axis.

Do not silently substitute collision bounds, resize an explicitly non-scalable
or exact-size Entity, resize a container, clamp a relationship, or invent a
fallback transform. Uniform fitting remains allowed by default for flexible
content when it is explicit and reported. State which scene requirements remain
implemented and which requirement the failure blocks.

## Report Completion

Report the implemented source locations, scene hierarchy, asset and scale
evidence, important transforms, build/launch result, source-gate output, runtime
evidence path, and reviewed screenshot or recording paths. Describe the complete
scene outcome first; present calculations and plans as supporting evidence.
