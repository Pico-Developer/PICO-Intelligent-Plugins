## Component rules (HARD)

Read `./spatial-ui-components.md` before writing UI; read
`./spatial-windows-guide.md` when the design has window-level or
floating structure.

- **C0 — Preserve component colors and readable pairs.** Prefer SpatialUI
  component defaults for selection, toggle, and interaction states. When a
  component provides state-aware content color to a slot, leave `Text.color` /
  `Icon.tint` unspecified so the slot inherits it. On an ordinary app-owned
  surface, choose an intentional foreground for the actual background. When
  custom state colors are required, use the component `colors` API when
  available and consider each state's effective foreground and background
  together. Either color may remain unchanged when the resulting pair stays
  readable. Never infer white text or a dark fill merely because a state is
  selected.
- **C1 — Prefer built-ins without changing semantics.** If a whitelisted component matches the semantics, use it. Do not hand-roll an equivalent from `Box` + `Text` + `clickable`, but do not misuse `Button` as a card, catalog tile, metadata group, selectable layout, or read-only detail surface merely to increase built-in usage. `Button` is for a concise command. Use an actionable `ListItem` when its row semantics fit, a custom layout with spatial hover plus `clickable` / `selectable` for rich interactive content, or a plain layout for read-only content. `scan_implementation.py` warns when a UI uses too few SpatialUI built-ins and fails for recognized Button content containers. Generated Button content is limited to a concise command label, optional icons, and loading state. Do not generate multi-line explanatory commands or evade this rule by extracting rich content into a helper. Comments never grant an exemption; focus, hover, and click requirements are not exceptions. Opaque helper content still needs semantic review.
- **C2 — Never invent SDK names.** Prefer the maintained component inventory. For an unlisted API, verify its availability, signature, and import against the project's target SDK before use; do not treat an inventory omission as an SDK limitation. If no supported component fits, use an app-owned layout and record the unresolved scope rather than inventing `SpatialButton` / `XRPanel`. A placeholder does not satisfy a required interaction or spatial capability.
- **C3 — Edge-pinned chrome is window-level.** Long-lived edge navigation / action strips are window attachments (`TabBar` / `Toolbar` / `Subwindow`), not ordinary page layout. Toolbar may be declared inside a page Box/Column under WindowContainer; its placement remains window-owned and it consumes no page layout space. Do not hand-roll `Box(Modifier.align(...))` capsule rows. `TabBar` / `Toolbar` take no `modifier` — the system owns their placement. For a deliberate in-page overlay, mark it `// spatial-ui: intentional-in-page-overlay <reason>`.
- **C4 — Semantics over appearance.** Search box → `SearchField`, not `TextField` + a magnifier icon. Filters/tags → `ButtonChip` / `RemovableChip` / `ToggleableChip`. In-page side nav → `SideNavigation` / `SideNavigationItem`. Segmented switch → `SegmentControl` / `SegmentItem`.
- **C5 — Smallest floating explanation first.** `in-page overlay` → `SpatialPopup` → `Subwindow` → `multi_window`. Short confirmation → `AlertDialog`; heavy modal → `Sheet`; teaching bubble → `CoachmarkBox`; transient feedback → `SnackbarHost` (a host + state pair, not a standalone composable).
- **C6 — No direct Material imports.** `androidx.compose.material3.*` / `material.*` are rejected by the design-style verifier.
- **C7 — Custom interactive components** must follow the design-style hover + haptics rules (`Modifier.spatialHoverEffect`; modifier order `clip → background → spatialHoverEffect → clickable`), or use a built-in that already provides them.
- **C8 — Designer JSON components map to SpatialUI Compose.** For
  `intent_only`, every `kind: "spatialui"` node in `design-spec.json` must be
  converted through `./spatialui-web-to-compose.md`. Do not reproduce
  a mapped component with Compose primitives. JSON props/events become typed
  state and callbacks; node children become composable content. Use
  `preview.html` only to compare the accepted visual result.
- **C9 — Reuse icons before drawing.** Resolve icon sources in this order:
  user/Figma asset, existing app asset, exact bundled
  ICON 7.0 match, then a newly drawn icon. A catalog miss is not permission to
  choose a merely similar symbol. When a new or materially repaired icon is
  required, follow `./icon-drawing.md`. Load accepted SVGs through Coil
  and preserve monochrome theme tint according to
  [Image and icon sources](./preview-first-restoration.md#image-and-icon-sources).
