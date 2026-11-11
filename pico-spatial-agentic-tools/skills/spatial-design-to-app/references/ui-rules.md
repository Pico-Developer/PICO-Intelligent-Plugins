#### UI rules

- Before emitting Compose, derive the required SpatialUI capability domains from
  the direct request or accepted upstream design facts. Read
  `../../spatial-ui-ability/SKILL.md`, then load one matching `references/ability-*.md`
  for each required capability domain. Do not preload unrelated references.
  Treat those snippets as integrated implementation resources; do not start a
  separate app-generation workflow.
- Build from the decisions: root container → window ornaments → windows → regions → reusable components.
- For `intent_only`, implement every resolved row from the JSON → Compose
  conversion inventory. `sui-tab-bar`/`sui-toolbar`/`sui-subwindow`/
  `sui-augment` remain root/window ornaments; modal, menu, coachmark, popup, and
  snackbar mappings keep their SpatialUI state/host patterns. Translate JSON
  props, bindings, and events into typed Kotlin state and callbacks; never copy
  Web renderer mechanics into Kotlin.
- Restore every declared component prop, state, callback, hierarchy, and layout
  fact from the frozen spec, including component size plus explicit width,
  height, padding, gap, alignment, justification, growth, and overflow. When a
  value is absent, preserve the Native component or Compose layout default
  unless a maintained canonical restoration pattern below explicitly applies.
  Do not invent fixed dimensions, spacing, or alignment merely to balance the
  composition or equalize siblings.
- Component size may require several Native parameters. For SegmentControl,
  defaults are Small; preserve a declared size through height, corner radius,
  item content padding, and text style together. Follow the
  [Segment sizing example](././spatial-ui-components.md#segment-control-sizing).
- Body top padding below TitleBar defaults to 0dp unless the user requests
  otherwise. Restore the 96dp centered SideNavigation title band and optional
  SearchField with zero top inset and 28dp below using the canonical example.
  Consume `props["spacing-policy"]` as a mapping directive, not a Kotlin parameter;
  review `side_navigation_spacing` warnings against the accepted spec.
- Map Web TitleBar `props["title-alignment"]` values `center` / `center-in-bar`
  to Native `TitleAlignment.Center` / `TitleAlignment.CenterInBar`.
- Choose alignment from the whole TitleBar composition, not only its title
  slot: use `TitleAlignment.CenterInBar` only for a plain-text title (including
  a text-only title/subtitle stack) with no leading/trailing actions or other
  content. Use `TitleAlignment.Center` when buttons, search, or other content
  are present. Restore the explicit spec value; when absent, apply this same
  composition rule. Verify enum support against the project SDK. Preserve an
  explicit authoritative source override and review scanner warnings against
  the accepted spec.
- When a TitleBar title slot contains an identity title followed by a
  SearchField and the accepted design declares no explicit internal spacing
  override, restore it as a full-width Row with
  `Spacer(Modifier.weight(1f))` between the identity content and fixed-width
  SearchField. Do not add title-slot padding or `Arrangement.spacedBy`; native
  TitleBar owns its padding. Explicit user or visual-source layout evidence
  overrides this default.
- Resolve every declared icon before writing its Compose call site. Preserve
  user/Figma, app, and SDK sources. Follow
  [Image and icon sources](./preview-first-restoration.md#image-and-icon-sources):
  load accepted SVG files through Coil with SVG support, retain original bitmap
  files, and use `painterResource` for existing local Android drawables. For
  Figma `icon70://` assets, run the Designer's
  `scripts/icon-catalog.mjs resolve --spec ... --format android --out ...` and
  copy only referenced catalog vectors. Preserve SpatialUI icon slots and their
  theme tint for monochrome sources; never substitute text, emoji, or an
  approximate catalog asset.
- **Set the container meta-data in `AndroidManifest.xml` to match the Decide stage.** It is the runtime source of truth and what verification reads back. See `./manifest-and-entry.md`.
- Read the relational alignment patterns in `./layout-inference.md`
  for Figma, screenshot, and accepted-package restoration: shared outer edges
  for mixed tile sizes, header baselines, repeated-row rhythm, effective
  two-sided list insets, and overlay title/body hierarchy. Extract relations
  before generation; preserve them in the existing visual verification pass.
- **Spacing ownership and root fill are explicit.** A root-fill shell is edge-to-edge with insets on inner content; an outer-padding card carries its own margin. Give every gap exactly one owner — do not double-pad or drop the outer margin. See `./layout-inference.md`.
- Apply the **component rules C0–C9** above. This is where they bind.
- Preserve native component typography by omitting `Text.style` when the
  accepted design does not explicitly override it. For app-authored text,
  restore the exact accepted `PicoTheme.typography` token and prefer tokens
  below `titleLarge` (20sp) for ordinary body and metadata only. Dialog, Sheet,
  popup, and detail-window headings keep their semantic title role and stronger
  hierarchy; never shrink or remove them merely to clear a size warning. Use
  native title slots where available. A direct `Text(...)` style at or above that
  ceiling is a non-blocking design-style warning whose accepted-design source
  and necessity must remain visible through Compose review.
- Read `../../spatial-ui-design-style/SKILL.md` and satisfy its pre-build admission
  rules before Compose UI. This is a mandatory phase of this workflow, not a
  separate app-generation workflow or a final lint. Preserve the native
  SpatialUI `ColorScheme` unchanged: do not construct or copy it to replace
  `fill*`, `label*`, interaction, status, hover/pressed, or divider roles.
  Custom design colors remain allowed as named app-owned tokens used directly.
  `windowConstraints(...)` is resize bounds, not first-open size.
- Do not add `Text.color` / `Icon.tint` merely to make a component slot's color
  explicit. Preserve component-owned foregrounds by default. For category,
  brand, selection, or toggle customization, check the effective content
  against the effective container in every affected state. In particular,
  avoid dark-on-dark, light-on-light, white on light gray, and white on bright
  category fills. `labelPrimaryLight` is a bright-on-dark role, not a generic
  selected-state foreground. Translucent fills must be judged over their
  underlying surface.
- Restore the declared TitleBar subtitle as `bodyMedium` / `labelSecondary`
  without override evidence. Treat other TitleBar and SideNavigation slot
  typography or foreground as an accepted override only when the design node also records
  `styleOverrideEvidence` from the original user requirement, Figma, or a
  screenshot. Without that evidence, retain the Native slot default, omit
  `Text.style`, `Text.color`, or `Icon.tint`, and preserve a warning; do not
  reopen or mutate the frozen design.
- Do not carry design-review apparatus into the product UI. Viewport presets, data-mode controls, token legends, coverage badges, and implementation notes are omitted unless the source requirement identifies them as real user features.
- Preserve every extracted radius on the bounded content surface that owns it.
  Structural `layout` and `domain_visual` regions remain transparent. For each
  app-authored surface restored from `design-spec.json`, place exactly one
  `// design-style: design-surface <node-id>` immediately before its
  `.background(...)` or content `Card(...)`. Do not add app-authored
  `.backgroundMaterial(...)`, borders, or `BorderStroke` to content containers.
- Keep business UI 2D unless the design justifies 3D; Stage-only APIs stay out of WindowContainer flows.
- For a `STAGE_*` root: host 3D via `SpatialView` + ECS entities (`Entity()` / `Entity.load(...)` + `content.addEntity(...)`) and attach 2D controls with `AttachmentPanel(id){}` positioned in meters on an ECS anchor. Never a flat `Box`/`Column`/`Canvas` page, never a bare Compose overlay. See `./stage.md`.

#### Architecture rules (HARD)

Read `./architecture-conventions.md` before writing code. The checker
enforces layered packages, a thin `Main.kt`, MVI-lite state, repository
boundaries, mandatory ViewModel tests, and UseCase + tests when the screen has
non-trivial business rules, filtering, sorting, selection, or transformation.
