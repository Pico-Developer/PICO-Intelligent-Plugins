# VibeLab Publishing Asset Guidance

Use this reference when selecting, reviewing, capturing, or converting publishing assets for
VibeLab.

The Release CLI remains authoritative for machine validation. If its current validation policy is
stricter than this guidance, follow the CLI result and report the difference.

## Source and placement gate

Use `<publish-root>/assets/` as the only directory for local files referenced by `vibelab.yaml`.
Tell users who provide their own media to place it there before review. Suggested names are
`icon.jpg`, `landscape.png`, `detail-1.png` through `detail-5.png`, `demo.mp4`, and
`demo-cover.png`; other names are acceptable when the resulting `vibelab.yaml` paths remain under
this directory.

This directory is local-only upload input. Require `/assets/` in the publish root's `.gitignore`
and keep every file under it out of the Git index. Do not apply this rule to source-controlled
application resources such as `app/src/main/assets/`.

Record one approved preparation mode before any emulator or physical-device availability check:

- `user-supplied`: do not discover, check, start, or require a device. Wait for the named files,
  require explicit runtime-origin confirmation for runtime media, and validate the files directly.
- `agent-prepared`: check a compatible target and matching capture provider only after the user
  delegates the named assets to the Agent.

If a user-supplied file is missing or invalid, report the exact replacement needed and keep the
same mode. Do not check a device unless the user explicitly delegates that asset to the Agent.
This delegation path applies only to runtime media. It does not authorize application-icon
conversion; that requires the separate, icon-specific decision gate below.

Never search for or reuse publishing media from:

- `.scratch/` or another hidden design-work directory;
- HTML/design previews, mockups, Figma exports, or design-review evidence;
- generated screenshots that do not show the running application;
- build, test, or conversion intermediates that lack runtime-capture provenance.

Meeting the required dimensions, format, or file size does not make one of these sources valid.
Do not copy an invalid source into `assets/` to make it appear publishable.

The application icon is the only image that need not originate from a runtime screenshot. It is a
user-controlled application-identity asset, not Agent-prepared runtime media. The
application-provided launcher icon is authoritative. Select an existing compliant review file or
copy it byte-for-byte when no conversion is required. Never generate or redesign application-icon
artwork, and never recover it from a design intermediate. When the authoritative source does not
meet the publishing file-format, dimensions, or size contract, the Agent may convert or resize it
only after explicit, icon-specific user authorization and must write a separate review file under
`<publish-root>/assets/`; never overwrite the application's source icon. Preserve its artwork,
identity, visible composition, aspect ratio, padding, and color intent; never crop, pad, redraw,
recolor, add or remove content, or alter it to hide a manual-review risk. Compare the exact review file with its authoritative
application-provided source, the installed launcher icon, app branding visible at runtime, and
package identity. For the landscape poster, detail images, videos, and video covers, the visible
product content must originate from the actual running application on an emulator or physical
device:

- For Agent-prepared media, record the selected target type and device ID, require the capture or
  recording command to succeed, and verify the resulting host file exists and is readable.
- For user-supplied media, require explicit confirmation of the same runtime origin without probing
  or starting a device.
- Keep every final approved file under `<publish-root>/assets/`.

A landscape poster may add a small amount of explanatory text or framing around an actual runtime
capture. A video cover must be a frame from the runtime recording or a separate runtime screenshot.
For runtime media, cropping, resizing, and format conversion are allowed under its approved mode.
This runtime-media permission does not grant icon-conversion permission; icon preparation follows
the separate authorization gate below. Replacing the captured application view with synthesized or
design-stage content is not allowed.

## Application icon

The same icon appears as:

- a circular icon in the device app library and Dock;
- a square icon on VibeLab pages.

Requirements and visual guidance:

1. Require a decodable JPEG file with a `.jpg` or `.jpeg` extension. Do not use PNG for the
   publishing icon even when the Release CLI can parse it.
2. Use a clear primary subject and keep it near the center.
3. Keep sufficient safe padding on every side.
4. Keep the primary subject inside the centered safe circle. The guidance uses a circle whose
   diameter is 80% of the image side.
5. Do not bake rounded corners or an outer border into the background; system clipping supplies the
   final shape.
6. Supply a sharp `1024 x 1024` image. This resolution supports the system's automatic icon-layer
   effect.
7. Verify that both circular and square crops preserve the subject and do not clip important
   content.

Good icons have one centered, separable subject with a simple background and generous padding. Poor
icons use a full app screenshot as the icon, place important content near the edge, or add their own
rounded frame.

### Icon decision gate

Validate the application-provided source and the exact review file:

1. If the application-provided source icon is already machine-valid under this workflow, select it
   or copy it byte-for-byte into `<publish-root>/assets/`, then validate the review file.
2. If the source is machine-invalid because of JPEG encoding or extension, dimensions, or file size,
   stop before Release `add`, explain the exact failing requirement, and offer exactly two choices:
   - ask the user to provide a compliant JPEG file with a `.jpg` or `.jpeg` extension based on the
     same application icon;
   - ask the user to explicitly authorize the Agent to prepare a compliant review file from the
     application-provided source.
     Do not infer this permission from `agent-prepared` runtime media or a general release approval.
3. With explicit authorization, change only encoding, `.jpg`/`.jpeg` extension, dimensions, and
   compression needed by the machine contract, and write a separate review file under
   `<publish-root>/assets/`; never overwrite the application's source icon. Preserve the source icon
   artwork and visible composition, identity, aspect ratio, padding, and color intent. Never
   generate, crop, pad, redraw, recolor, add or remove content, or alter the icon to repair a
   manual-review risk. Record the source and output paths in the review, then rerun every icon
   validation against the output. Do not offer a force-submit path that the CLI cannot accept.
4. If the resulting file is machine-valid but has a manual-review risk, state the specific evidence
   and that review may reject the submission. Offer exactly two choices:
   - pause while the user modifies or replaces the icon, then validate the new file;
   - continue with the exact reviewed icon after the user explicitly accepts the rejection risk.
5. Never select conversion or the continue option by default, infer either authorization from a
   general release approval, or treat risk acceptance as proof that VibeLab will approve the icon.

Manual-review risks include a generic or different-product identity, mismatch with the installed
launcher icon or runtime branding, an unclear or edge-clipped subject, insufficient safe padding,
baked rounded corners or border, and poor circular or square crop behavior.

## Application poster

A high-quality poster may be shown as a large recommendation card.

Requirements and visual guidance:

1. Require a decodable JPEG or PNG file with a `.jpg`, `.jpeg`, or `.png` extension.
2. Use a `16:9` image at `2560 x 1440`.
3. Show a focused part of the application's core experience or main capability.
4. Use only a small amount of text when it helps explain the main capability.
5. Keep one obvious focal point.
6. Avoid a poster that contains only a simple symbol with no product context.
7. Avoid dense layouts with too many screens, labels, or competing subjects.

## Detail images and videos

Detail-page media must explain the actual in-app experience in more depth.

Use explicit orchestration roles and keep them out of the Provider schema:

- `video_for_stills` -> approved still images: temporary runtime input for extracting poster or
  detail frames; keep it outside `<publish-root>/assets/` and never map it to `app.videos[]`.
- `raw_publish_recording` -> `publish_video` -> `publish_video_cover`: keep the raw session recording
  outside `<publish-root>/assets/`; derive and independently validate one continuous final segment
  before writing `publish_video` under `assets/`, then extract the corresponding cover from inside
  that exact segment.
- Only `publish_video` maps to `app.videos[].file`, and only `publish_video_cover` maps to the same
  item's `app.videos[].cover`. Intermediate, failed, diagnostic, and still-extraction recordings are
  never publishing assets by fallback.

The cover frame must occur inside the exact accepted publish segment. Record role, source path,
selected time range when applicable, output path, and content hash. Never overwrite or delete a
user-supplied source video.

Hard requirements:

- Detail-image count: `4-6`, defaulting to `5`.
- Every detail image must be a decodable JPEG or PNG file with a `.jpg`, `.jpeg`, or `.png`
  extension.
- Video is optional. Recommend at least one and ask about it separately after confirming the
  required icon, poster, and 4-6 detail images; offer Agent-prepared, user-supplied, and skip
  choices.
- Aspect ratio: `16:9`.
- Dimensions: `2560 x 1440`.
- Each image: less than `5 MB`.
- Each video: less than `100 MB`.
- Included video: `30-60` seconds at `2560 x 1440`, with the core experience visible in the first
  three seconds, no black intro, no recording-tool watermark, and a dedicated cover.
- All detail media for one release should use a consistent visual style.
- Every image and video must show the actual running application captured from an emulator or
  physical device.

For Agent-prepared interactive videos:

- skip only when the user explicitly says video is not needed or a capability check proves the
  selected device cannot record the required demonstration;
- complete the FFmpeg availability and installation-approval gate before changing application state
  or starting the recording;
- start one session-owned recording before the first approved interaction and stop that same session
  after the complete scenario;
- perform at least two distinct, meaningful, Contract-declared state-changing actions during the
  recording for an interactive Spatial application;
- require a visible result for every planned action and reject an idle recording, near-identical
  frames, timer-only movement, or a flow that does not explain the core experience;
- select only one continuous bounded publishing segment; trimming setup, cleanup, or pauses must not
  reorder events or synthesize application content, and the accepted segment must be `30-60`
  seconds;
- write the accepted segment to a separate `publish_video` under `<publish-root>/assets/`; never use
  the `raw_publish_recording` path as its final destination and never overwrite a user-supplied file;
- show the core experience in the first three seconds and reject a black intro or recording-tool
  watermark;
- derive `publish_video_cover` from inside the exact accepted `publish_video` segment.

Recommended forms:

1. Capture key application pages directly from the emulator or physical device.
   - For window applications, place the window directly in front of the viewer and make it occupy a
     large portion of the frame.
   - For Stage applications, capture an active usage moment or a scene that clearly shows the
     application's art direction.
2. Create a coherent series from runtime captures, using only a small amount of explanatory text.

For Agent-prepared PICO Spatial detail images:

- Use target-relative multi-angle capture only for Stage or volumetric content with a stable focal
  subject. Keep window applications directly in front of the viewer and create variety from distinct
  meaningful runtime states instead of edge-on or rear views.
- Capture five distinct detail images by default. Unless the approved plan names a 4-6 image set
  with other viewpoints, a Stage or volumetric set uses a prepared front view, front-left at 35
  degrees, front-right at 35 degrees, elevated front, and lowered front. This bounded five-view set
  is not six faces or a 360-degree set.
- For window applications, use 4-6 distinct meaningful runtime states, defaulting to five. For
  passthrough or mixed-reality content, use 4-6 distinct validated current-view runtime moments
  instead of injected virtual-Pose multi-angle capture.
- Keep the intended subject identity, framing scale, visual treatment, and readable edge margins
  consistent across viewpoints. The viewpoint must change materially without turning the subject
  away from the viewer or exposing an empty, clipped, or unrendered side.
- Do not use injected virtual-Pose multi-angle capture for passthrough or mixed-reality content when
  the physical-camera view does not follow that Pose.
- Keep probe images and targeting evidence outside the publish root. Only accepted final runtime
  screenshots belong under `<publish-root>/assets/`.

Reject or replace detail media when:

- the file bytes duplicate another selected image;
- the visible frame is identical or near-duplicate to another selected image after resizing,
  cropping, overlays, or format conversion;
- the application window is too small to inspect;
- the frame is blurry or the product content is unreadable;
- several unrelated interfaces compete in one frame;
- the frame is information-dense but has no clear subject;
- the media is attractive but does not reveal what the application does;
- a mixed set uses inconsistent styles, framing, or typography.

## Review checklist

Before reporting that the publishing asset set is ready, enumerate the exact configured local asset
paths from `vibelab.yaml` and compare them with the approved plan. Do not use `assets/*`, intended
output names, or a successful subset as proof that the complete set exists. If a capture,
generation, or conversion command warns, fails, or skips an input, treat that expected output as
missing until its corrected command succeeds and the resulting regular file is verified.

### Asset-origin review labels

In the pre-add review, describe each selected asset as user supplied, Agent prepared this run,
retained from a remote `uri:`, or derived from another approved asset. Use natural-language review
context rather than adding schema fields or persistent provenance state. These labels are
informational and non-blocking: they do not prove alignment with a Git SHA, APK hash, or source
version. An unknown source is reported as unknown and returned to the user for a continue, replace,
or Agent-prepare-again decision; it is not an automatic failure.

For every expected local asset, verify:

- every configured path is under `<publish-root>/assets/` and outside `.scratch/` or any other
  intermediate directory;
- the icon decodes as JPEG and has a `.jpg` or `.jpeg` extension;
- every poster, detail image, and video cover decodes as JPEG or PNG and has a matching allowed
  extension;
- the icon matches the actual built/installed application icon, runtime branding, and package
  identity;
- every selected image has a unique content hash, and pairwise visual comparison finds no identical
  or near-duplicate frames;
- every landscape, detail image, video, and video cover has verified emulator/device runtime
  provenance;
- 4-6 configured detail images are present and verified;
- the icon is `1024 x 1024` and survives both square and circular crops;
- each poster and detail asset is `2560 x 1440` at `16:9`;
- image and video byte sizes are below their respective limits;
- every included video is `30-60` seconds at `2560 x 1440`, shows the core experience in its first
  three seconds, has no black intro or recording-tool watermark, and has a dedicated cover;
- the observed icon, landscape, detail-image, video, and video-cover counts exactly match the
  configured paths;
- the poster communicates one main capability;
- detail media shows real application content at a readable scale;
- the detail set has consistent framing and visual treatment;
- no placeholder, unrelated, blurred, or purely atmospheric media is selected.

After the required images are confirmed, recommend one video and ask one separate optional-video
question with three choices: Agent-prepared `30-60` second key-interaction video and dedicated
cover; user-supplied runtime video and dedicated cover; or skip video. A skip choice means
`app.videos: []`. Verified device recording-capability absence is also a skip path; missing FFmpeg,
provider unavailability, or an individual recording failure does not satisfy it. In
`user-supplied` mode, wait for both files without checking a device. In `agent-prepared` mode, check
the target only after delegation and capture both. Do not complete the review until both files pass
this checklist or the skip reason is documented.

Report only the verified subset while any expected item is missing or unverified. Do not claim
compliance from this review alone. Run the Release CLI's structured validation before any upload.
