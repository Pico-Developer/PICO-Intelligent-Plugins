# Subwindow

A persistent companion attached to the left or right of its owning main window. The Web default follows the current SDK: fixed width 360, the owner's full height, gap 24, corner radius 32, Regular material, and no menu-style surface padding. Web px represent dp in this preview; width is not a percentage of the main window.

## Web API

- `<sui-subwindow for="main-window-id">`: `for` is required and identifies the owning window, not the opening button. Place the companion beside its owner in a shared positioned parent, outside the owner's clipped content.
- `placement`: `default`, `left`, `right`, `start`, or `end`. Default is right in LTR and left in RTL, following the current SDK implementation. `start`/`end` are logical Web aliases. Above/below are not Subwindow placements; use SpatialPopup for that relationship.
- `hidden`: caller-owned open/closed state. Show by removing `hidden`; close by setting it. Repeating an open action should keep it open.
- `focusable`: Web approximation controlling the surface's tab index; it does not reproduce native input/focus semantics.
- `depth`: legacy Web-only visual Y offset, default 0; not actual 3D depth or a native Subwindow parameter.
- `dismiss-on-click-outside` / `dismiss-on-escape`: default false. Explicit `"true"` opts into Web-only dismissal. Selecting content does not close a Subwindow.
- Default slot: caller-owned TitleBar and body. Content scrolls inside the matched-height surface instead of making the window taller.
- `dismiss-request`: cancelable event for optional implicit dismissal. The normal close button can directly set `hidden`.

The companion follows owner movement and resizing. Hiding or removing the owner closes the companion; showing the owner again does not reopen it automatically. Missing owners do not produce inline fallback cards. Companions retain their attachment geometry rather than clamping over the owner at viewport edges. Reserve room for the pair in a scrollable preview stage on narrow screens.

## Beside a Volume window

A Subwindow can accompany a **Volumetric WindowContainer**, not only a flat Planar page. Use it when equipment status, pet care actions, object properties or a selection inspector should form a separate companion beside the window. Ordinary text and controls may also remain directly in the window content; using Volume does not require Subwindow. Its owner is the Volume window; it does not follow an independently rotating model or a selected model part.

Use AttachmentPanel instead when the accepted design explicitly puts the UI in the `SpatialView` scene and binds it to a scene group, object or part. “Beside a 3D model” alone is not such a requirement. For controls placed directly in Stage, use a scene attachment; a separate WindowContainer hosted within Stage may still have its own Subwindow.

Subwindow already provides its Regular glass surface. Do not add another panel-wide material/background to its content. AttachmentPanel supplies no automatic glass, so a backed scene panel needs that explicit choice. See [AttachmentPanel's comparison and examples](../AttachmentPanel/README.md).

The Volume example below uses a transparent, explicitly sized DOM region to represent the owning volume's front projection. It has no Planar glass shell. The outlined bounds and simplified rotating object are presentation aids, not App UI or a real 3D renderer. The Subwindow keeps the current width, owner-height, gap and material defaults.

Native basis: the local SDK's `spatialui/design/src/main/kotlin/com/pico/spatial/ui/design/windows/Subwindow.kt` (`d16142477`) attaches through `AugmentImpl` to a window container, provides `Material.Regular` and matches container height. Choosing a Subwindow is a layout decision, not a requirement imposed by Volume. The example shows one optional composition.

## Plan rules: a complete companion surface

Use a Subwindow for continuing supplementary content belonging to a main window: an inspector, playback queue or details used while the primary task continues. Use Sheet for an interrupting short task, Menu for a command list, and AlertDialog for a decision.

Record the owning window, which action opens it, whether it persists across page changes, and what closes it. Keep outside-click and Escape dismissal disabled for a persistent companion. An opening button opens; the companion's own close button exits. The owner lifecycle is also an exit condition.

Compose one TitleBar, a body and an optional bottom operation region. Put close/back in the leading position; familiar auxiliary IconButtons can go trailing. Put a substantial text action at bottom-right, or full-width within a narrow region. Use recommended primary title weight 700 explicitly. Body normally has start/end/bottom 32 and top 0 below TitleBar. Let long content scroll inside the available height.

For a long title, the body can hold the complete text while the title bar retains a concise title or just necessary controls. Do not repeat the identical full title twice or delete the only close/back region. No global modal scrim is added to a persistent companion.

## Preview and shared rules

[Open the preview](preview.html). All three examples initially show the owner and its companion. The details example demonstrates height following; the photo inspector changes the displayed image and resets brightness. The Volume example rotates a simplified subject independently and updates its inspection status from the side panel. All examples use the component defaults for geometry and material. The previous ownerless placement example and content-sized inspector have been replaced because they did not represent Subwindow behavior.

See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences). Spatial focus, rotation, viewpoint following and actual system attachment still require native validation.

## Validation

Maintainer runtime regression checks live in the repository test suite. Browser review and native validation remain separate.
