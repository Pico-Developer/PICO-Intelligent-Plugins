# Icons

896 ICON 7.0 resources from the supplied local pack, with stable IDs, English search, a visual browser and drawing guidance. This package keeps one catalog and one SVG tree; duplicate CSV/Markdown catalogs, the ZIP, and the old generated preview are omitted. The source directory beside design-reference is unchanged.

## Choose an icon

1. Search the action or object in English: `search`, `share`, `play`, `wifi`, `settings`.
2. Inspect the results in [the icon browser](preview.html); compare silhouette, direction and treatment at 24px.
3. Use the returned stable `id` and `path`. Five names occur more than once; those names are deliberately not resolved by the renderer. Use their IDs to choose the actual asset.
4. Keep icons consistent within a navigation or action group. Do not assume every icon has an outline/filled pair; `unspecified` means the source did not classify its style. Selection can be expressed by the component's state colors.
5. Review the Preview source: verify each final icon name/ID against the runtime's catalog aliases or built-in glyphs, and check that referenced custom resources exist and are wired into the intended component or slot. A search keyword is not necessarily a valid icon name. If no suitable resource exists, follow [drawing.md](drawing.md), save the drawing and reference the actual resource in Preview.

For example, `cut` describes the intended action but is not a registered icon name in this runtime. Search for scissors and use the matching resource's returned name/ID. If a required cursor has no suitable existing resource, draw and save an SVG, then reference that file; writing `icon="cursor"` alone does not create an icon. Source review includes icons in disabled buttons and buttons that also have text. Visual inspection supplements this check for display problems; a visible button or label is not proof that its icon reference is valid.

```sh
python3 assets/icons/search.py "share" --limit 8
python3 assets/icons/search.py "play" --category media --json
python3 assets/icons/search.py --list-categories
python3 assets/icons/search.py --id ICON7-P001 --paths
python3 assets/icons/search.py --id ICON7-P001 --svg
```

Run these from the design-reference root. Python 3.9+ is sufficient; no packages or network access are needed. Short English aliases are supported. `requires_confirmation` flags ambiguous meaning or interaction metadata in the source catalog: compare the actual shape and intended action before choosing; it does not mean routine library use needs an approval step.

## Color and size

```html
<!-- Default independent foreground: labelPrimary. -->
<sui-icon name="ic_share" size="24"></sui-icon>
<!-- Explicit icon color. -->
<sui-icon name="ic_share" size="24" tint="#3377ff"></sui-icon>
<!-- Default Button uses white for both its text and its icon. -->
<sui-button text="Share" leading-icon="ic_share"></sui-button>
<!-- A control-level override changes its text and built-in icon together. -->
<sui-button text="Share" leading-icon="ic_share"
  content-color="#3377ff" container-color="var(--fill-light-alpha)"></sui-button>
```

`name` accepts a unique catalog name or a stable ID. Prefer IDs in the final design record. The reference examples' short aliases (such as `settings`, `image` and `copy_link`) resolve to this local pack; their mapping is in catalog.json. New designs should use catalog names/IDs. Unknown or ambiguous names produce a console warning and no fake letter/text icon.

An individual Icon's explicit `tint` wins. Without it, an Icon inside a control's slot uses that control's content color; an independent Icon uses the system primary foreground. This does not mean an independent Icon copies an arbitrary colored parent. Disabled opacity is applied by the containing control to its whole content. See the [Icon preview](../../components/Icon/preview.html) for default, explicit, slotted and disabled examples.

All delivered SVGs use one color. 894 originals require only visible ink-color normalization, preserving existing mask/clip definitions and their white mask paint. The two resources with green details use transparent cutouts so those details remain visible when tint changes. No multicolor API is added. Masks are scoped per rendered instance to avoid collisions when the same icon appears twice. `source_sha256` preserves the original file identity, `sha256` identifies the adapted SVG. For native VectorDrawable export, preserve these cutouts with path subtraction or equivalent clipping; do not paint fake white holes or assume an SVG mask can be pasted into Android XML unchanged.

`<img src="...svg">` does not expose an Icon tint parameter. Use `<sui-icon name="...">`. For application-owned SVG files, `src` on `sui-icon` renders the file's alpha silhouette with the selected tint via a CSS mask; use same-origin HTTP URLs. Raster artwork belongs to an image component, not this monochrome Icon path.

## If the catalog has no suitable asset

Use [drawing.md](drawing.md): 24×24 coordinates, footprint and stroke rules, transparent negative space, optical alignment, naming and SVG/native delivery. Reuse existing assets first. No separate drawing skill is installed by this reference bundle; the linked file is the complete drawing instruction entry.
