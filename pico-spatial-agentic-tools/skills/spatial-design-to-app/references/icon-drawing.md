# ICON 7.0 Production Icon Drawing Reference

Use this reference when a PICO app needs a new or materially repaired UI icon.
It adapts the production rules from the ICON 7.0 handoff dated 2026-09-16 to
the source-to-app workflow. It is not a replacement for an icon supplied by
Figma, an existing app resource, an SDK-owned icon, or a matching bundled ICON
7.0 asset.

## Source authority and reuse order

Resolve the source before drawing. Use the first available authoritative asset:

1. A user-supplied Figma/download asset or explicit reference image.
2. An existing approved icon in the target app or current product icon family.
3. An SDK-owned icon that expresses the same semantics and state.
4. An exact semantic match in the bundled ICON 7.0 catalog.
5. A newly drawn ICON 7.0-style vector following this reference.

Do not redraw an available source merely to make it look more generic. When a
reference image exists, preserve its recognisable silhouette, direction,
topology, and defining relationships, while normalizing its production geometry
to the 24 dp system. Never trace raster noise or inherit arbitrary pixel size,
color, stroke, or flattening from a screenshot.

Before drawing, record these decisions in working notes:

- semantic subject and state;
- treatment: line, fill, or a deliberate line/fill pair;
- canonical resource name;
- nearest approved family relative, if one exists;
- reference-only features that must survive normalization.

Use the name to settle meaning and the visual source to settle silhouette and
arrangement. If they conflict materially, preserve the named meaning and report
the conflict instead of silently changing the subject.

## Production workflow

1. **Inventory the meaning.** Identify the object, state, direction, and whether
   the component needs line and fill variants. Tab-like selected/unselected
   pairs normally use line when unselected and fill when selected.
2. **Select a family relative.** Match by semantic family and treatment first,
   then by silhouette and construction. Reuse its footprint, stroke rhythm,
   corners, negative-space strategy, and container-to-symbol spacing.
3. **Choose the visible footprint.** Keep the root canvas at 24 x 24 and size
   only the artwork using the table below.
4. **Construct editable geometry.** Keep meaningful parts such as container,
   symbol, slash, badge, and cutout separable. Use real transparent holes or
   Boolean subtraction rather than a background-colored mask.
5. **Review at 24 dp.** Check silhouette, apparent mass, internal clearance,
   endpoints, joins, cutouts, and optical alignment at intended size. Enlarged
   inspection is diagnostic; final acceptance happens at 1x.
6. **Export and integrate.** Preserve the 24 x 24 coordinate system, use a real
   vector resource, and render it through SpatialUI `Icon` or the appropriate
   built-in component slot.

## Canvas and visible footprint

The asset coordinate system is always **24 x 24**. The visible artwork normally
occupies a smaller footprint; 24 x 24 is not permission to fill the canvas.

| Shape / aspect  | Ordinary or complex | Simple primitive   |
| --------------- | ------------------- | ------------------ |
| Circle / square | 20 x 20 or 18 x 18  | 16 x 16 or 14 x 14 |
| Vertical        | 16 x 20             | 12 x 16            |
| Horizontal      | 20 x 16             | 16 x 12            |
| Compact-wide    | 20 x 18             | 16 x 14            |

Use the ordinary tier for multi-part silhouettes or meaningful internal
structure: home, trash, refresh, devices, media, Wi-Fi, or a container with an
inner symbol. Use the simple tier for plus, minus, close, ellipsis, a single
chevron, or a bare low-detail mark. Extra-wide 22 x 14 / 24 x 12 and extra-tall
14 x 22 / 12 x 24 footprints are reserved for inherently elongated subjects.

Source-defined irregular silhouettes may depart from the table when forcing
them into a generic rectangle would destroy their identity. They still must fit
inside the 24 x 24 canvas, retain margin, and remain legible at intended size.

### Container proportions

- A line circle with an inner symbol uses a 21 x 21 rendered ring centered at
  `(1.5, 1.5)`, with a 2 dp stroke aligned inside. Its inner symbol is roughly
  8.5 x 9.5, with a continuous band of clear space around it.
- A filled circle is normally 20 x 20 centered at `(2, 2)`; its central positive
  or negative mark may occupy roughly 10 x 10. Do not force line and fill
  versions into identical bounds because filled shapes carry more mass.
- A compact square or rounded rectangle with internal detail is normally 18 x
  18 centered at `(3, 3)`, with any stroke kept inside the rendered footprint.
- A standalone directional icon is not an inner symbol. Give a bare arrow, swap,
  or switch mark roughly 16-19 dp on its dominant axis, then balance the other
  axis optically.

## Stroke, corners, and connections

- Use a **2 dp primary stroke**. Internal linework may use 1.5 or 2 dp according
  to density; keep corresponding parts in a pair at the same weight. Negative
  lines must not be thinner than 1.5 dp.
- Open strokes use flat, perpendicular **butt** ends. Right-angle folds and
  arrow turns normally use mitered joins. Do not add round caps or joins merely
  to make the icon look softer.
- Inspect the rendered contour, not only the cap/join property. A filled path
  can contain a baked-in semicircular end even when metadata says the cap is
  flat.
- A real object contour, such as a microphone capsule, heart lobe, circular
  pivot, or rounded container, is not a line ending. Preserve its semantic
  curves while keeping constructed line terminals flat.
- Intended connections need a small positive overlap of painted envelopes so
  they do not rasterize with a hairline seam. Do not extend the connection into
  a protected hole or create a double-weight bulge.

Choose rectangular corner radius from the visible shape, not the canvas:

| Visible side length   | Default outer radius |
| --------------------- | -------------------- |
| 18 dp or larger       | 3 dp                 |
| 12 to less than 18 dp | 2 dp                 |
| 6 to less than 12 dp  | 1 dp                 |

For a stroked rounded rectangle, preserve `outer radius = inner radius + stroke
width`. Intersections and inscribed corners are sharp by default. Round an acute
corner only when the nearest approved master does so or a sharp 24 dp rendering
is visibly fragile. Apply the same decision across a pair or family.

## Direction, arrows, slashes, and mirrored pairs

- Build one canonical left/right or forward/backward icon and mirror the
  complete directional geometry around the x=12 canvas axis. Do not redraw the
  pair independently or mirror only its container.
- Keep readable letters and numerals upright when surrounding directional
  geometry is mirrored. Their size, baseline, and body-relative placement stay
  consistent across the pair.
- Repeated arrows, chevrons, sound waves, and controls share coordinates for
  tips, bends, baselines, and terminals. Opposing or parallel strokes retain at
  least 1 dp of visible negative space. This normally requires at least 2.5 dp
  between 1.5 dp centerlines or 3 dp between 2 dp centerlines.
- A 45-degree derivative must be remeasured after rotation. Recenter and, when
  needed, optically enlarge it so it has the same perceived size as the cardinal
  master rather than merely the same transform scale.
- The default slash is 26 x 2 at -45 degrees and may extend beyond the canvas
  before clipping. A slash/cut gap is normally 1.5 dp and may reduce to 1 dp only
  when the larger gap damages recognition.
- Keep slash edges parallel and represent the gap with transparency. A
  background-colored stripe is not a cutout and fails on glass or themed
  surfaces.

For refresh, rotate, reopen, and history symbols, reuse the nearest approved
curved-arrow master. The head should continue from the arc tangent rather than
appearing as a detached V, L, or generic triangle. In the approved two-arc
refresh treatment, the upper head is at the right end and the lower head at the
left end. When nesting a curved arrow in a compact container, redraw the arc at
1.5 dp if scaling the master would make it too thin.

## Fill, negative space, badges, and paint

- A filled counterpart is a related redraw, not a mechanically flooded line
  icon. Preserve the principal silhouette, simplify secondary details, and
  enlarge important cutouts until its optical mass matches the line relative.
- Circular negative spaces must be at least 2.5 x 2.5. Enlarge or simplify a
  negative mark when an equal measured size looks too weak at 24 dp.
- A badge is normally 10 x 10 at bottom-right. Move it to top-right only when it
  obscures the primary subject. Keep its separation/cutout parallel to the badge
  contour; text inside a badge is at least 10 sp.
- Keep three readable zones for a contained icon: canvas margin, outer container,
  and clear space around the inner symbol. Do not grow the symbol merely because
  it still fits mathematically.
- Author positive artwork as a single monochrome foreground, normally
  `#000000` in the source asset. At runtime, route its color through the
  component/theme tint. Do not bake near-black, white masks, or a second visible
  color into a monochrome icon. Preserve explicit multicolor source artwork only
  when the design requires it, and do not pass a tint that destroys those colors.

## Optical alignment

Geometric centering is a starting point, not the only acceptance criterion.
Choose the correct alignment reference before moving anything:

| Relationship                            | Alignment reference              |
| --------------------------------------- | -------------------------------- |
| Symmetric icon                          | canvas axes x=12 / y=12          |
| Symbol inside a symmetric container     | actual inner cavity              |
| Symbol inside an asymmetric device/card | usable foreground body or screen |
| Badge mark                              | badge cavity or semantic anchor  |
| Clock hand / gauge needle               | shared pivot or arc center       |

Symmetric marks such as plus, cross, pause, and concentric circles use exact
axes unless their usable body is offset. Directional or asymmetric marks such
as play triangles and chevrons may need a small evidenced shift. Apply the
smallest translation to the complete mark; do not change its silhouette, weight,
or proportions to repair a position-only defect.

Review outer-canvas balance and inner-symbol balance separately. A centered
outer frame does not prove that a play mark, letter, numeral, or transparent
cutout is centered in its own usable cavity. Pixel/path centroids are supporting
evidence, not automatic targets.

## Text and numerals inside icons

- Use a real approved product glyph or an outline from the approved font. Do not
  approximate letters with rectangles while calling them font glyphs.
- Typeset a word or number as one run with a shared baseline, cap height, and
  deliberate tracking. Preserve intrinsic glyph proportions; do not squeeze
  characters independently to make them fit.
- Keep font contour winding intact. Test counters and overlapping contours after
  conversion; use transparent Boolean subtraction for negative lettering, never
  white text.
- Align lettering to the usable body: for example, a display label belongs to
  the screen area, not screen plus stand or antenna. Preserve font-designed
  terminals and curves rather than applying the icon's line-cap rules to every
  glyph.
- If complete wording cannot satisfy font, silhouette, clearance, and minimum
  stroke constraints together, report the conflict and ask for a scoped text
  exception or a different layout. Do not silently distort the wording.

## Naming and delivery

Use `ic_<description>[_<state>][_fill][_rtl]` for resource filenames. The
description names the depicted object, not the workflow that happens to use it.
Add a state only for a real visual variant, `_fill` only for a filled treatment,
and an RTL suffix only when a separate asset is genuinely needed.

The approved design source is an SVG under
`design-assets/icons/<resource-name>.svg`:

- use `width="24"`, `height="24"`, and `viewBox="0 0 24 24"`;
- use editable path geometry and keep every visible path inside the viewport;
- use `currentColor` for monochrome positive artwork;
- preserve holes with fill type/winding or Boolean subtraction;
- do not use a white/background-colored shape as a fake cutout;
- do not embed raster data, fonts, scripts, external references, or transforms
  that cannot be represented faithfully by Android VectorDrawable.

During app Build, create a matching Android vector drawable:

- use `android:width="24dp"`, `android:height="24dp"`, and a 24 x 24 viewport;
- preserve the approved SVG path geometry and transparent holes;
- render it through SpatialUI `Icon`, `IconButton`, or the semantic component
  slot with an appropriate `contentDescription`; decorative icons may use
  `null`;
- follow `../../spatial-ui-design-style/references/tokens.md` for semantic tint
  and `../../spatial-ui-design-style/references/builtins.md` for component
  selection.

When Figma supplies `<Icon download-url>`, `d2c_download_icons` remains the
authoritative asset path. Preserve the downloaded geometry and dimensions; use
this reference only to diagnose or deliberately repair a production defect.

## Batch production

For roughly 20 or more icons, define semantic clusters and reusable templates
before drawing the set. Approve representative masters first, then produce each
asset from a small recipe containing name, subject, treatment, cluster, template,
footprint, parts, directional behavior, and multi-part relationship.

Run objective checks on every icon and a visual contact-sheet review at 24 dp.
If the same defect appears in three or more assets, repair the template and
regenerate its dependents instead of patching each child independently.

## Acceptance checklist

- Semantic meaning, state, direction, and topology match the request/source.
- Canvas and viewport are exactly 24 x 24; visible art uses a deliberate smaller
  footprint and never overflows.
- Primary/internal stroke, caps, joins, corners, and intended connections follow
  the selected family.
- Positive art is monochrome unless multicolor is explicitly required; holes,
  slashes, and badge gaps are transparent.
- Line/fill variants share a semantic center and silhouette while retaining
  independently balanced mass and negative space.
- Mirrored pairs are true mirrors; readable text stays upright.
- Outer frame and internal symbols both pass optical-alignment review at 1x.
- Resource naming is canonical, the vector loads successfully, and the final
  component uses semantic tint and accessibility text correctly.
- Only evidenced defects changed; conforming geometry and unrelated assets were
  preserved.
