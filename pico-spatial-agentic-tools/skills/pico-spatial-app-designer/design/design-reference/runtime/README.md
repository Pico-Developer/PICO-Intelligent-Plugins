# Preview runtime

`components.js` is the reference repository's `src/sui.js` adapted for this bundle. `tokens.css` is the unmodified reference token stylesheet. `preview.css` only styles the documentation/example stage; do not treat its page background, borders or spacing as app defaults.

```html
<link rel="stylesheet" href="runtime/tokens.css">
<script src="runtime/components.js" defer></script>
```

Paths above assume an HTML file at the bundle root. Each component preview includes its own correct relative paths. There is no dependency on the current chain's spatial-web implementation.

## Application Preview windows

Load `tokens.css` and `components.js` from the delivered runtime (or embed their unchanged contents when the Preview must be a single HTML file). Use the Preview helpers below for the main window. `preview.css` is for the reference site's documentation pages; application Preview does not need it.

```html
<style>
  html, body { margin: 0; }
  .page-body { padding: 0 32px 32px; flex: 1; min-height: 0; overflow: auto; }
</style>
<sui-preview-stage>
  <sui-planar-window id="main-window" role="main" style="width:720px;height:540px">
    <sui-title-bar><span>Library</span></sui-title-bar>
    <div class="page-body"><!-- Compose the selected components here. --></div>
  </sui-planar-window>
</sui-preview-stage>
```

- `sui-preview-stage` supplies the neutral `#DAD6D3` browser backdrop, 40px presentation margin and scrolling when content is wider than the available space. Its backdrop and margin are not application design values.
- `sui-planar-window` supplies the existing runtime's regular material approximation (`rgba(202,202,202,.78)` and shared glass effect), the 32px window radius, content clipping and a column layout. It adds no content padding.
- Set width and height externally, in page CSS or the element's `style`, from the chosen layout. **720 × 540 is only this example's size.** The helper defines no default, minimum or maximum window dimensions and does not scale a specified window down to fit the browser.
- The default background is material; `background="material"` is an explicit equivalent. Use `background="transparent"` only for a design that explicitly calls for a transparent window. It removes the material fill, blur and material shadow; content and window geometry remain.
- Keep attached surfaces such as Subwindow and popup elements outside the planar shell, so its clipping and backdrop filter do not contain them. Anchor them with `for="main-window"`. Existing components retain their own material and placement behavior.

These are Web Preview helpers, not new native SDK components. In Spec, record the window under `surfaces`, including its chosen size and `windowBackground`; retain the content tree under its root. Do not create component nodes for these helper tags or copy the stage backdrop, simulated RGBA, blur or shadow into application appearance. See [Spec container guidance](../../spec-writing.md#5-containers-windows-and-subordinate-content).

## Scene attachments

Use [`sui-attachment-panel`](../components/AttachmentPanel/README.md) to show the 2D content of a scene-bound panel. It is transparent by default; `background="material"` explicitly selects the shared Regular glass simulation and radius 32. Width, height, content padding and placement remain caller-owned. It supplies no ECS anchoring or automatic following behavior. The [examples](../components/AttachmentPanel/preview.html) compare a transparent label, a backed task panel and a control strip. Volume content may use ordinary layouts directly, or optionally use [Subwindow](../components/Subwindow/README.md#beside-a-volume-window) for a separate window companion. AttachmentPanel is for 2D content positioned within the SpatialView scene. For information/action attachments, explicitly adding glass is recommended; transparency remains the default.

## What was preserved and changed

- Preserved all 42 business component-family pages and the 67 registered Web elements (including Basic and child variants). Baseline examples are retained except documented corrections such as Subwindow's ownerless/content-sized examples. Cover is the upstream site's landing page, not a component, and is omitted.
- Preserved tokens.json, color-roles.json, motion.json and tokens.css without value changes. Original component defaults remain the baseline except documented SDK-alignment fixes below. Added recommendations use attributes or normal parent layout and are labelled in previews/docs.
- Replaced the public icon lookup with the local 896-resource catalog, stable IDs and compatibility aliases. The reference component's internal control marks (check, small chevron, coachmark tip, etc.) remain internal implementation details. They are not an alternative application icon catalog.
- Icon tint works for registered resources and the alpha silhouette of custom `src` resources. Independent default is primary foreground; control slots use the control's foreground unless explicit tint is supplied.
- Added two Preview-only shell elements, `sui-preview-stage` and `sui-planar-window`, alongside the preserved 67 component elements. They unify the main window/background presentation without fixed window dimensions.
- Added the `spatialHoverEffect(element)` Web helper and built-in ListItem row hover. This is a Preview behavior addition, not a change to native SDK defaults or a new native parameter.
- Segmented Toolbar now omits an empty supporting segment. Its center aligns to the host's bottom edge, matching the configurable native overload described in the current chain. Legacy unsegmented placement is preserved. At the default height of 64 these positions coincide; they differ when height changes.
- SpatialPopup has its own 360×184 minimum, zero content padding and above/start default placement instead of inheriting Menu geometry. Its explicit placement attributes map to native position-provider choices; browser flipping/clamping remains a preview convenience. General content selection does not dismiss it.
- Subwindow has independent window geometry and lifecycle: fixed width 360, owner-matched height, gap 24, radius 32, Regular material and no menu padding. It defaults to no outside-click, Escape or selection dismissal, and closes when its owner disappears. It uses the shared positioned parent's coordinates without viewport clamping. Its two examples now show complete owner/companion pairs in horizontally scrollable stages; the previous ownerless/content-sized examples were replaced.
- SideNavigation now shares one selection scope across shorthand and child items, including sections. Selection/style updates preserve generated item nodes and keyboard focus. The original Collections section is inside its navigation; a minimal two-section example and grouped sidebar/page example demonstrate cross-section selection. See [SideNavigation guidance](../components/SideNavigation/README.md). Native selection remains caller-owned.
- Chip's reference page now focuses on basic labels. `clickable="false"` suppresses the Web button semantics, focus, feedback and action event, corresponding to native `Chip(onClick = null)` for click behavior. Existing clickable and specialized variants remain available in the runtime. Native basic Chip retains spatial hover even without a callback; read-only Web labels omit that feedback. See [Chip guidance](../components/Chip/README.md).
- Added standalone page loading, component/browser navigation, explicit composition examples and the icon browser. The existing BasicSheet example now includes its caller-owned title/close; the original SideNavigation Favorites item now includes a local star icon. The Sheet header uses a bundled SVG illustration at `assets/illustrations/lake-scene.svg`.

## Application visual assets

While authoring Preview, save reusable static covers, illustrations, diagrams and decorative backgrounds as application asset files. Reuse suitable supplied resources first. SVG suits static vector artwork; keep photographs and complex textures in an appropriate image format such as PNG or WebP. Simple fills, gradients, radii and layout can remain styles; not every CSS drawing needs conversion.

Application assets belong beside the application's design deliverables, not in this Skill's `design-reference/assets`. For example:

```text
design-output/
├── preview.html
├── design-spec.json
└── assets/
    └── slow.svg
```

Preview and handoff use the same artwork. If the Preview must be self-contained, inline that asset's content and also deliver its standalone file; update both when the artwork changes. Do not leave required artwork only in an inline SVG, data URL or drawing script without an accompanying reusable asset.

### Small example: a book cover

The [paired book example](../../spec-writing-reference/README.md#reusable-artwork-example) already follows this pattern. Its `assets/slow.svg` contains the illustration; the list uses it like this:

```html
<img id="cover-slow" slot="leading" src="assets/slow.svg"
     alt="Cover of The Unhurried Days"
     style="display:block;width:60px;height:80px;object-fit:cover;object-position:center;border-radius:6px">
```

Write Spec registers the file as an image asset and refers to it from the media node. The detail reuses the same file at 72 × 96. The SVG's paths are the artwork, not additional layout nodes. These sizes illustrate this example, not defaults for other images.

Keep full-color artwork's original palette; a cover or decorative SVG is not a tintable Icon merely because its format is SVG. Keep titles, controls, live data and interactive regions outside the artwork when they must remain independently readable, changeable or operable. Do not flatten a live chart or interactive diagram into its current screenshot.

For a decorative background image, record the owning region, placement behind content, dimensions or sizing relationship, fit/crop, and any intentional tiling, opacity or state changes. The image must not intercept foreground actions. System window materials, Preview scenery and component fills remain separate; do not bake them into an application background asset. A resource file does not replace these placement facts.

## Explicit customization available in this runtime

These attributes are already implemented by the reference library, beyond the short per-component API summaries:

| Attribute | Meaning in the Web runtime |
| --- | --- |
| `content-padding="16"` | Internal padding in px; for ListItem, all four sides. Sheet applies it to the body. |
| `padding-start/end/top/bottom="…"` | Individual physical insets; the Web build does not implement RTL mirroring. |
| `default-min-height="48"` | Root minimum height; does not set a fixed height. |
| `custom-width`, `custom-height` | Explicit host/root size. Use only when the design calls for it. |
| `corner-radius`, `gap` | Root radius/gap; behavior is component-specific. Toolbar radius affects its segments. |
| `font-size`, `line-height`, `font-weight` | Broad component text overrides. For TitleBar primary-only weight, style the slotted title instead. |
| `semantic-label` | Accessible label on the component's main part. |
| `material` | Web approximation: regular / thick / thickest / none. |

A parameter existing in Web does not establish an identically named native SDK parameter. Translate through the component's native notes, and use the target SDK's public API.

## spatialHoverEffect

`window.spatialHoverEffect(element)` adds the Web simulation of spatial pointing feedback to a connected region. Call it after the runtime has loaded and the element has mounted, for example in `DOMContentLoaded` when loading `components.js` with `defer`.

```html
<div id="file-item" role="button" tabindex="0" aria-pressed="false"
     style="border-radius:var(--radius-large);padding:var(--padding-regular);background:var(--fill-light-alpha)">
  Report.pdf
</div>
<script>
window.addEventListener('DOMContentLoaded', () => {
  const item = document.getElementById('file-item');
  spatialHoverEffect(item);
  const selectFile = () => {
    if (item.getAttribute('aria-disabled') === 'true') return;
    item.setAttribute('aria-pressed', 'true');
    // Render the selected file's details here.
  };
  item.addEventListener('click', selectFile);
  item.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      item.click();
    }
  });
});
</script>
```

The helper draws an approximately 12% white layer on hover, using `state-lighten-hover-alpha`. It follows the target's radius, leaves on pointer exit, does not intercept clicks and adds no scale or depth motion. It uses the target's `::before` pseudo-element and an isolated stacking context; reserve that pseudo-element for the feedback. Existing non-static positioning is preserved. For a mounted Web component with a `root`, `surface` or `field` part, it targets that internal surface; otherwise it targets the supplied element itself.

Disabled feedback is suppressed for `disabled` (except the Web convention `disabled="false"`), `aria-disabled="true"`, or a component's `.dis` state. The helper does not implement click actions, keyboard activation or disabled business logic: those remain with the component/page. An ordinary custom region should guard its action when disabled, as above. A connected region in a ShadowRoot is supported as well as a normal page element.

Button and other components already providing hover do not need this call. ListItem now includes it internally for every row; its existing `disabled` behavior, padding and click events are preserved. Do not add a separate outer hover layer. See the [working ListItem/custom-region example](../components/ListItem/preview.html).

### Mapping to App

The Web argument identifies a DOM element. Native `.spatialHoverEffect()` has no corresponding `target` argument: it affects the component receiving the Modifier chain.

```kotlin
Column(
    modifier = Modifier
        .clip(RoundedCornerShape(16.dp))
        .spatialHoverEffect()
        .clickable { openFile() }
) {
    Text("Report.pdf")
}
```

Record hover on that same design node, not as a DOM selector or a literal Web function call. Restore custom regions with the native modifier; for ListItem, Button and other native components with built-in hover, use the existing component treatment without an extra modifier. The Web layer simulates the feedback and does not prescribe the native effect's opacity or animation. This adds reference guidance only; it does not change the pipeline or Spec schema.

## Browser/native differences

The upstream reference inventory cites SDK source `dev/6.4.0`, revision `8047508`; its separate native host pins BOM 6.2.5. That is not proof of alignment to every SDK version. Browser checks in this bundle do not claim native or headset validation.

- Web uses px as the design preview equivalent of dp/sp. System fonts differ and can change text widths.
- Vibrant, compositor materials, actual ray/gaze-driven spatial hover, spatial depth, following, focus, haptics and sound are not reproduced. Mouse hover is approximated by component feedback and the helper above. See [Vibrant](../vibrant.md) and [Motion](../motion.md).
- Attached surfaces use 2D anchor geometry. Menus/popups may clamp to the viewport; Subwindow preserves its side attachment and follows its owner's height, so its preview stage should reserve room for both windows and allow scrolling. TabBar is a visual fitting example; native placement is WindowContainer-owned. A Subwindow depth offset is not a 3D scene.
- Dialog/Sheet viewport sizing approximates the owning window. The Web scrim is an approximation; focus trapping is not implemented. A standalone preview is not production browser-dialog accessibility code.
- Pickers simplify inertia, formatting, infinite wheels and native semantics. Right-to-left layout is not reproduced. Text selection UI and IME behavior require native verification.
- Menus, SpatialPopup and coachmarks clamp/flip in the browser, which is not evidence that the native component uses that same position policy.
- Sheet's bottom slot follows the content in the scrolling panel; it is not a guaranteed pinned footer. Specify the intended long-content scrolling behavior separately.

## Provenance

Reference: `hongyu.1217/AutoEva_SpatialDesignSystem`, commit `4b664e88ab230737e450deb1c5564f1fdf034dee`, acquired through bitscli. [UPSTREAM-NOTICE.md](UPSTREAM-NOTICE.md) is an archived upstream notice; its paths refer to that original repository, not this reorganized package. Its old icon inventory is replaced here by the supplied local pack dated 2026-10-20.


## 3D placeholders

Use ordinary HTML or SVG for simplified model regions; no SpatialView Web component is required. Follow [3D Preview authoring](../3d-preview.md) for stable IDs, scene design notes and an AttachmentPanel composition. A placeholder is not a final 2D asset or a native scene hierarchy.

## Volume Preview boundary

Use `sui-volume` for the Volume selected in Frame/Explore. Supply positive `width`, `height`, and `depth`, all in dp; no dimensions are defaulted. Width and height render as the host's border-box CSS pixel dimensions (1dp = 1px). Do not override them with conflicting CSS sizing or scaling.

```html
<sui-volume id="character-volume" width="900" height="600" depth="400">
  <div id="scene-root"><!-- Model placeholder and AttachmentPanel --></div>
</sui-volume>
```

The shell provides a faint background, inset wireframe and generated dimension caption. These are Preview aids, not native glass, walls, meshes or application nodes. They do not add padding or enlarge the declared layout bounds, and do not intercept pointer input. Depth is recorded and labelled, not measured from the schematic projection. Content layout and padding remain the caller's responsibility; the shell is not a 3D renderer or a native clipping simulation.

Use the shell ID as the Spec surface ID and an inner application node as `rootNodeId`. Record `{ "width": 900, "height": 600, "depth": 400, "unit": "dp" }` in `surface.defaultSize`. Browser audit locates the shell by surface ID, checks root containment, compares actual width/height and all three declared dimensions. Native SDK conversion and physical containment require later verification.
