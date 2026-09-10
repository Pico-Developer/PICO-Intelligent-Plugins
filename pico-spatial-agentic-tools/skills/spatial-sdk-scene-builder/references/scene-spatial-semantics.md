# Three-Axis Scene Semantics

Read this reference before assigning final transforms in a complete scene that
contains bodies, surface details, supports, containers, cavities, or physical
trajectory anchors.

## Model Relationships Before Coordinates

PICO uses `+X` right, `+Y` up, and `+Z` front/toward the user. A convincing
front projection can still hide an invalid depth relationship. Treat Z as a
physical scene axis rather than a painter's layer used to keep silhouettes
visible.

Classify each relevant Entity or logical region:

| Role           | Meaning                                                                   |
| -------------- | ------------------------------------------------------------------------- |
| Body           | The object's volume used for support, contact, containment, and collision |
| Surface detail | Eyes, label, nose, decal, indicator, or trim attached to a body surface   |
| Support        | A tabletop, pouch, floor patch, beam, or other carrying surface           |
| Container      | An independently defined cavity, bay, shelf, slot, or safe volume         |
| Anchor         | A named launch, attachment, impact, or path endpoint                      |
| Visual overlay | A deliberately view-facing cue that does not claim a physical path        |

Surface details may protrude from their parent body. That does not justify
moving the entire body toward `+Z`. A body may also protrude from an open
container, but the accepted contract must name the open face and allowed
protrusion.

## Write a Three-Axis Contract

For every hard relationship, record:

- target body ID and bounds scope;
- reference support, container, or anchor ID;
- independent region or reference bounds source;
- X, Y, and Z relationship on final scaled and oriented bounds;
- margin, gap, contact epsilon, or allowed protrusion by axis;
- whether the relationship is physical or only a visual overlay;
- which viewpoints can reveal the relationship.

Do not use an Entity origin, equal pivot Z values, or a hand-maintained scene
envelope as a substitute for this contract. Equal pivots are neither necessary
nor sufficient when bodies have different depths or off-center pivots.

## Verify Support and Contact

For a body `t` carried by an axis-aligned support region `s`, a top-face contact
requires both vertical contact and footprint containment:

```text
abs(t.min.y - s.max.y) <= epsilon

s.min.x + margin.x <= t.min.x
t.max.x <= s.max.x - margin.x
s.min.z + margin.z <= t.min.z
t.max.z <= s.max.z - margin.z
```

Use the final body visual bounds. A center above the support does not prove that
the body's footprint is carried by it.

For a sling, seat, hook, or irregular support, define an explicit owner-local
support volume or named attachment anchors that approximate the intended
relationship. Do not treat the visible support mesh's whole recursive bounds as
its usable carrying region.

## Verify Independent Containment

Define a cavity or permitted depth band independently of the occupant. Never
construct the permitted region by unioning it with the target being validated.
For closed containment, verify all final target faces with the standard
containment interval.

For an open container, name the open axis and allowed protrusion. Example for a
front-open bay:

```text
X and Y: full containment with margins
Z back: target.min.z >= bay.min.z + backMargin - epsilon
Z front: target.max.z <= bay.max.z + allowedFrontProtrusion + epsilon
```

A target-center check may be diagnostic, but it cannot produce a hard
containment `PASS` when any required final face violates the region.

## Bind Physical Trajectories to Anchors

A physical trajectory must start and end at named anchors expressed in one
owner space. Verify all three components, including depth:

```text
distance(pathStart, launchAnchor) <= epsilon
distance(pathEnd, impactAnchor) <= epsilon
```

Construct the curve from full XYZ anchor values; do not calculate an XY arc and
assign a constant foreground Z. Sample the path or verify its curve definition
to show that depth changes continuously from launch to impact. Intermediate
samples or a curve envelope must remain consistent with the accepted path
volume when collision or non-overlap matters. If a dotted arc or reticle is
intentionally screen-facing, classify it as a visual overlay and do not present
it as physical trajectory evidence.

## Treat Numeric and Visual Evidence Separately

Remeasure final body bounds after hierarchy, scale, orientation, and fit are
applied. Numeric evidence establishes hard contact and containment. Visual
inspection establishes composition and catches semantic mistakes the selected
formula did not encode.

Request a side or oblique view when Z is important. If the available runtime
capture cannot reveal that axis, keep the numeric result and report
`visual=UNOBSERVED`; do not infer a visual pass from the front projection.
