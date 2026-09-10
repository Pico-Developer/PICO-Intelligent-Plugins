# Preview Guide — the Web validation prototype

`preview.html` proves the design's _logic and layout_ work before anyone writes runtime code. Its scope is fixed: **`web_design_validation_only`**. It never validates real-device comfort, occlusion, physical size, or performance — and it never contains Android/PICO runtime code, device evidence, or parity claims.

The prototype's value comes entirely from being **triggerable**, not pretty. A static mock proves nothing. A reviewer must be able to click through every state, see fallback and error data, and hit the confirmation dialogs.

## Step 1 — coverage manifest (before writing HTML)

List, from `design-doc.md`, every design fact the prototype must implement. This is the denominator you'll check against in the second critique. A name appearing in the doc is not the same as being implemented — the manifest makes the gap visible.

Enumerate:

- **States** — each state from the state graph.
- **Transitions** — each transition, its trigger, and whether it needs explicit confirmation.
- **Components** — each core component and its variants.
- **SpatialUI mappings** — each planned control/system surface, its `sui-*` tag, public event/state, and any justified custom fallback.
- **Data bindings** — each binding, with a normal value, a fallback (missing/stale), and an error sample.
- **Responsive behavior** — the natural CSS reflow between the recorded min/default/max window bounds, plus reduced-motion behavior. This is implementation behavior, not a visible product mode.

## Step 2 — build against the manifest

Single self-contained file (inline CSS/JS, no external deps or runtime file reads). Start by reading [`spatialui-web-guide.md`](./spatialui-web-guide.md), then inline the complete `../assets/spatialui-web/spatialui.bundle.js` in a `<script>` before the app script. Requirements:

- **A real state machine** — states are actual switchable views, transitions are wired to triggers, back/exit paths work.
- **SpatialUI controls** — use the mapped `sui-*` components and their public `CustomEvent`s. Native controls or hand-rolled dialogs are allowed only when the catalog has no equivalent and the manifest records why.
- **Theme installation** — keep the bundle's default `vibrant` scheme and call `PicoTheme.install({ scheme: "vibrant", colorScheme: { ... } })` with the design's complete 16-role contract after the bundle loads. Explicitly forward every inherited role from `PicoTheme.vibrantColorScheme()` and replace only roles with exact design values.
- **Sample data in three modes** — normal, fallback (missing/stale), and error — reachable so a reviewer can see each.
- **High-risk actions gated by a dialog** — destructive or irreversible actions show explicit confirmation.
- **Natural responsive reflow** — CSS responds to the available window width between min/default/max; honor `prefers-reduced-motion`. Do not add a visible layout-tier or viewport-preset switch.
- **Windows at default size**, with the sizing intent legible (a room-scale surface should _look_ room-scale, not phone-scale, in the mock; a small widget should read as glanceable).
- **Stable selectors** — give state containers and key elements stable ids/classes so the critique can assert against them.

Represent the PICO context with the library itself: keep SpatialUI Web's default
`vibrant` theme and render the app root with its `Material.Regular` glass
background variable/style. Do not substitute a fixed gray panel, custom
`backdrop-filter`, or opaque app root for that material. A room image or neutral
page color may sit behind the glass only to reveal translucency; it is not an
app-owned token. Keep the 32 dp window radius and make the spatial intent
readable without pretending the surface is a phone screen.

The preview is the product surface, not a design inspector. Do not render
viewport-mode selectors, data-source simulators, coverage status, token
swatches, implementation notes, or keyboard-help copy unless the brief
explicitly makes one of them a user-facing feature. Exercise
fallback/error states through test hooks in script or temporary review tooling,
not persistent controls in the delivered UI.

## Step 3 — generation-side mapping

Right after building, record how each manifest row maps into the prototype: state → view, transition → trigger, component → DOM, SpatialUI mapping → registered tag + selector + public event, and data binding → normal/fallback/error. Responsive behavior is reviewed from CSS and viewport resizing, not represented as a manifest row or product control. If you can't point to where a manifest row lives in the HTML, it isn't implemented — go back and add it.

## What "done" looks like

Every manifest row is implemented and triggerable; mapped controls are registered `sui-*` elements wired through public events; normal/fallback/error data are testable; high-risk transitions are blocked by a SpatialUI dialog; natural responsive reflow and reduced-motion are respected. The root uses SpatialUI Web glass and the delivered UI contains no design/debug-only controls. Any available SpatialUI control replaced by a native or hand-rolled equivalent without a documented reason is a `block`. A percentage or an overall impression does not offset a missing core fact.
