# ICON 7.0 Selection and Rendering

Use the bundled ICON 7.0 catalog for app-authored icon slots in a
`design-spec.json`. The catalog contains 209 monochrome 24 x 24 assets:

- `../assets/icon-7.0/svg/` contains preview SVGs whose foreground is
  `currentColor`.
- `../assets/icon-7.0/android-vector/` contains matching Android
  VectorDrawable XML.
- `../assets/icon-7.0/catalog.json` contains searchable metadata, not SVG
  bodies.
- `../assets/icon-7.0/manifest.json` records the SHA-256 hash of every SVG and
  VectorDrawable.

## When to choose an icon

Choose component semantics and hierarchy first. Search the catalog during the
Designer **Plan** phase only when the accepted component has an explicit icon
slot, is an icon-only action, or needs an app-authored directional/status cue.

Do not add a separate icon when the chosen SpatialUI component already owns the
semantic affordance. For example, `sui-search-field` maps to `SearchField`; it
does not require a separate magnifier asset. Do not use icons as decoration or
to make a sparse layout look busier.

Resolve icon sources in this order:

1. A user-supplied Figma/download asset or explicit reference image.
2. An existing approved icon in the target app.
3. An SDK-owned icon that expresses the same semantics and state.
4. An exact semantic match in the bundled ICON 7.0 catalog.
5. A custom vector drawn through
   [`../../spatial-design-to-app/references/icon-drawing.md`](../../spatial-design-to-app/references/icon-drawing.md).

Do not select a merely similar bundled icon to avoid the drawing step. When no
candidate preserves the required subject, state, direction, and treatment,
record a custom icon requirement and draw it during Build.

## Search and resolve

Run commands from the `pico-spatial-app-designer` skill directory:

```bash
node scripts/icon-catalog.mjs search --query "download save" --limit 8
node scripts/icon-catalog.mjs resolve --name ic_download --format svg
```

Search returns only compact metadata. It never returns SVG path data. Inspect
the returned label, keywords, category, treatment, and direction before
selecting one result. Do not choose by filename similarity alone.

`ic_search`, `ic_message`, and `ic_message_fill` are known semantic mismatches.
Automatic search excludes them. Exact `resolve --name ...` remains available,
returns a warning, and requires visual review before use.

## Design-spec representation

Declare a selected catalog icon once in `assets[]`:

```json
{
  "id": "download-icon",
  "kind": "icon",
  "src": "icon70://7.0/ic_download",
  "purpose": "Download the selected recording",
  "alt": "Download"
}
```

Declare a custom drawn icon using a design-package-relative SVG path:

```json
{
  "id": "custom-mode-icon",
  "kind": "icon",
  "src": "design-assets/icons/ic_custom_mode.svg",
  "purpose": "Enter the product-specific mode",
  "alt": "Custom mode"
}
```

Reference either source from an explicit icon node:

```json
{
  "id": "download-symbol",
  "kind": "spatialui",
  "component": "sui-icon",
  "assetId": "download-icon",
  "accessibilityLabel": "Download"
}
```

An icon slotted into another SpatialUI component may use that component node's
`assetId`, provided the renderer maps the asset to the documented icon slot.
Do not encode an icon as an emoji, Unicode glyph, text character, data URL, or
untracked inline path.

## Preview rendering

For an `icon70://` asset, resolve the URI to the matching bundled SVG. For a
custom asset, read its design-package-relative SVG. Inline the complete SVG as
slotted content in both cases. Do not use `sui-icon[src]`: an `<img>` does not
inherit `currentColor`. The `sui-icon` or owning component supplies size and
tint.

Because `preview.html` is self-contained, the resolved SVG markup must be
embedded during generation. The delivered HTML must not fetch the catalog or
refer to the skill installation path at runtime.

## Compose materialization

Copy only bundled vectors referenced by the accepted spec:

```bash
node scripts/icon-catalog.mjs resolve \
  --spec <target>/design-spec.json \
  --format android \
  --out <target>/app/src/main/res/drawable
```

The command reports custom SVG assets separately and does not convert them.
Materialize those assets during the downstream Build phase by following
`spatial-design-to-app/references/icon-drawing.md`.

Use every resulting drawable through `painterResource(R.drawable.ic_name)` in
the mapped SpatialUI `Icon` or icon slot. Apply the intended `ColorScheme` role
as the Compose tint. Never replace the asset with a text glyph.

Verify catalog references, custom SVG sources, and target drawables:

```bash
node scripts/icon-catalog.mjs verify \
  --spec <target>/design-spec.json \
  --target-res <target>/app/src/main/res/drawable
```

A missing URI, absent `assetId`, missing drawable, changed catalog hash, invalid
custom SVG, or unknown icon is blocking. Repair the spec or materialized
resources before continuing.
