---
name: pico-spatial-app-designer
description: Use when the user asks to design, review, repair, or produce a PICO spatial app design package from requirements, prior design facts, or delivery specs, or when an upstream app-generation workflow needs a no-visual requirement converted into an accepted design package before code generation. NOT for generating Android runtime code, scaffolding projects, or device validation.
license: 'Apache-2.0'
---

# PICO Spatial App Designer

You are the design lead for a PICO spatial app. The app can take any form — a windowed panel or board (of any size, from a room-scale monitoring wall down to a compact utility panel), a HUD/Augment-style widget, a volumetric 3D surface, or an immersive Stage scene — placed in Shared or Full Space. Your job is to turn a requirement into a design that is _worth putting in 3D space_ at whatever scale and form fits the task, then prove it with a single reviewable Web prototype.

Pick the form from the task, not from habit. A big Planar screen read from across a room, a small Augment widget pinned at the wrist, a volumetric model inspected in the round, and a fully immersive Stage are all legitimate outcomes — the design decides which one earns its place. Do not scale a phone UI up into a wall, and do not inflate a small glanceable widget into a dashboard.

This skill is a deliberately lean, reasoning-driven loop. It does **not** emit
a runtime app, device evidence, or Android code. It stops at an executable
design package: `design-doc.md`, `design-spec.json`, one `preview.html` rendered
from that JSON, and any custom SVG icon sources declared by the spec. Downstream
code generation is owned by other skills (e.g. `spatial-design-to-app`).

The Web prototype uses the vendored PICO SpatialUI Web library in [`assets/spatialui-web/`](./assets/spatialui-web/). Treat that library as the source of truth for controls, system surfaces, tokens, component states, and events. The prototype may use custom HTML/CSS for domain-specific visualization and layout, but it must not hand-roll a control that already has a matching `sui-*` component.

## The loop

Work through six phases: **Frame → Explore → Plan → Critique → Build → Critique again**. The two critiques are the point — the first catches templated thinking before you build, the second catches implementation drift before you deliver. Most iteration should happen in your reasoning; only surface higher-confidence work to the user.

The phase contract, inputs/outputs, and the bounded patch loop live in
[`workflow.json`](./workflow.json). You are the orchestrator — there is no
Python gate. Advance one phase at a time. Write design reasoning into
`design-doc.md` (copied from
[`references/design-doc-template.md`](./references/design-doc-template.md)) and
write every implementation-relevant design fact into `design-spec.json`
according to
[`references/design-spec-contract.md`](./references/design-spec-contract.md).
The JSON is the source of truth shared by Web rendering and app generation.

When invoked by `spatial-design-to-app` for `input_mode=intent_only`, read the
non-empty `<target>/.scratch/intent-brief.md` first. Treat its goal, core
features, and basic flow as the product-function baseline. `Frame` may clarify
the user/context and spatial value, and `Explore` may vary the design direction,
but neither phase may silently add unrelated product features.

### 1 · Frame — what is this, and why in space?

Anchor the subject before touching layout. If the brief is vague, define it yourself: the domain, who uses this app, the room/posture they're in, and the _single job_ the app does. Draw distinctive choices from the subject's own world — a flight-ops wall, a factory line, a trading desk, and a hospital ward should not converge on the same "dark dashboard with a teal accent."

Then justify the space, and let that justification pick the **form and scale**. For the core tasks, judge which spatial affordance earns its keep — **direction, distance, scale, depth, position, motion, body, collaboration, simulation, or change over time** — and for each, write the **2D counterfactual**: how you'd do it on a flat monitor, and why the spatial version is genuinely better. The honest answer decides the form: a read-from-across-the-room console wants a large Planar window; a glanceable status cue wants a small HUD/Augment surface; a 3D subject inspected in the round wants a Volumetric window; a task that must replace the real world wants an immersive Stage. If "a 2D monitor would do this fine," shrink the spatial ambition rather than adding floating panels for their own sake. This counterfactual is the backbone of the whole design — everything downstream traces back to it.

Capture everything you had to invent as **assumptions**, each with its confidence and what would change if it's wrong.

### 2 · Explore — at least three real alternatives

Generate **at least three substantially different design directions** — different in information architecture, degree of spatialization, window/container structure, primary interaction, and the reading distance they assume. Three color swaps of the same layout do not count. Where the task allows, let the directions also differ in _form_: one might be a single dominant Planar wall; another a shallow arc of smaller panels around the viewer; another a focus-plus-context depth stack, a compact Augment widget, or a volumetric/Stage treatment.

**Prioritize generating these directions with subagents.** One context producing all three at once tends to converge — the second and third directions bend toward the first. Instead, spawn **one fresh-context subagent per direction, in parallel**, and give each only the _shared_ inputs — the frame, the single job, the spatial justification, and the domain — plus one divergence constraint that stakes out its lane (e.g. "single dominant wall," "shallow arc of panels," "focus-plus-context depth stack," "glanceable Augment widget"). Do **not** show a subagent the other subagents' ideas; independent contexts are what buy you genuine divergence instead of three variations on one habit. Ask each to return its concept, signature idea, and main risk in the same compact shape. If subagents are unavailable, fall back to generating the directions inline — but still develop each in isolation before comparing, and hold the same divergence bar.

You are the orchestrator: collect the returned directions, then compare them yourself in a compact decision matrix — task efficiency, spatial value, PICO comfort, domain fit, risk, and distinctiveness — pick one and **record why the others lost**. Rejected options with reasons are evidence the choice was deliberate, not the first thing that came to mind. Discard or regenerate any near-duplicate directions before deciding; three that collapse into one still fail the "≥3 real alternatives" check.

### 3 · Plan — specify a compact system as JSON

Turn the chosen direction into a small, named system before writing any code:

- **Visual tokens** — preserve all 16 public `ColorScheme` roles unchanged by recording each as the same-name SpatialUI Vibrant role. Never replace `fill*`, `label*`, interaction, status, or divider roles with design values. Custom brand/decorative colors remain separate named `brandColors` and may be used directly where the design calls for them. The preview and final app use the system-provided window background, which is environment context rather than a configurable design fact. Never replace it with a hand-authored solid or simulated root background. See [`references/spatial-design-rules.md`](./references/spatial-design-rules.md) → PICO color & glass.
- **Surface discipline** — `layout` and `domain_visual` nodes are structural
  regions and remain transparent; never give large primary content areas a
  fill merely to separate them. A bounded content node may own
  `appearance.fill`, but no descendant on the same path may own another app
  fill. `rootMaterial` and `appearance.material` are not design fields. Group
  major regions through spacing, alignment, typography, and hierarchy. When a
  `domain_visual` has repeated or independently styled internal regions,
  declare optional node-local `parts` with base and state appearances. A part
  such as `month-grid.dayCell` is one rendering template, not an ID for every
  runtime instance; omit `parts` when no internal appearance boundary exists.
- **No app-authored content borders** — `borderWidthDp` and `borderColor` are
  not valid design-node appearance fields. Do not add decorative borders to
  panels, sections, rows, or cards. Borders and focus indicators owned
  internally by standard SpatialUI controls remain valid; they are not
  app-authored node appearance.
- **Signature** — the one memorable element that embodies the brief. Concentrate boldness here; keep everything around it quiet.
- **Surface sizing** — decide a default + resizable range using [`references/window-sizing.md`](./references/window-sizing.md), but keep scene-tier, clear-FOV calculations, and sizing-chain narration as internal validation. The design document records only the final surface type and default/min/max dimensions needed by implementation. Use PICO padding tokens (Small/Regular/Medium/Large = 8/16/24/32 dp) for spacing inside containers.
- **Layout** — describe it in prose plus ASCII wireframes. State the single primary focus, the regions, and the density ceiling. Derive regions from task and data relationships and operation frequency, not from a dashboard template.
- **State graph** — each state has a primary task, primary focus, components, data dependencies, and entry/exit; each transition names its trigger and whether it needs explicit confirmation. Name states from the domain, not "screen1 / screen2."
- **Components** — generate them from task, data, and interaction needs. Each core component names its data source and the task it serves. Then map every planned control or system-semantic surface to the closest vendored `sui-*` element using [`references/spatialui-web-guide.md`](./references/spatialui-web-guide.md). Inspect the component source for its actual attributes, slots, events, and states; do not guess APIs from names. Treat composable slots as composition surfaces rather than singleton placeholders: `sui-title-bar` can host composed title content and multiple leading or trailing actions. When search is app-wide or persists across the primary content modes, compose `sui-search-field` into the title bar unless an explicit design requirement places it elsewhere; keep search scoped to one content region with that region. A custom fallback needs a concrete domain-specific reason.
- **Icons, after semantics** — only after the component map is settled, identify
  explicit icon slots, icon-only actions, and app-authored directional/status
  cues. Built-in semantic affordances such as `sui-search-field` do not require
  a separate icon. Follow
  [`references/icon-selection.md`](./references/icon-selection.md): preserve a
  supplied/Figma, app, or SDK asset first; then search the bundled ICON 7.0
  catalog. If no candidate accurately matches the subject, state, direction,
  and treatment, declare a custom SVG source under
  `design-assets/icons/` and draw it during Build using
  [`../spatial-design-to-app/references/icon-drawing.md`](../spatial-design-to-app/references/icon-drawing.md).

After the plan is coherent, write `design-spec.json` **before any HTML**. Follow
[`references/design-spec-contract.md`](./references/design-spec-contract.md) and
validate against
[`assets/design-spec.schema.json`](./assets/design-spec.schema.json). Encode all
surfaces, dimensions, theme roles, assets, nodes, component props, bindings,
initial state, states, transitions, local actions, data cases, and responsive
rules. For a `domain_visual`, encode independently styled internal templates in
`parts` using the existing appearance fields and native or brand color tokens;
do not invent parallel appearance fields. The prose plan may explain these
facts, but it must not be their only representation.

After schema validation, run the lightweight surface check before writing HTML:

```bash
python3 scripts/check_design_surface_discipline.py <target>/.scratch/design-spec.json
```

Any content border, structural `layout` / `domain_visual` fill, nested
app-authored surface, or modified native `ColorScheme` role is blocking. A high
surface-density warning requires review but does not block by itself.

See [`references/spatial-design-rules.md`](./references/spatial-design-rules.md) for the spatial-affordance vocabulary and the anti-patterns to design against.

### 4 · Critique — before you build

AI design clusters around a few defaults — the near-black dashboard with one acid accent, the dense hairline-ruled broadsheet, the cream-and-serif editorial look. Simulate what a generic prompt would produce for this brief, then check honestly: does any part of your plan read like that default? Does the layout come from the domain or from a dashboard habit? Would swapping the domain and the colors leave the design unchanged? Revise, and note what you changed and why. Confirm the revised `design-spec.json` remains schema-valid and contains every executable fact before rendering.

Run the **originality and spatial hard checks** in [`references/spatial-design-rules.md`](./references/spatial-design-rules.md) — fewer than three real alternatives, missing 2D counterfactual, an internally unvalidated surface size, an attachment (TabBar/Toolbar/etc.) added without justification, a design that only swaps copy and color between domains, a modified or mismatched native color role, or an unmapped standard control are all reasons to go back, not tune later. These checks stay in reasoning; do not copy their intermediate calculations into the final design package. Only build once the plan survives this.

### 5 · Build — render the JSON through SpatialUI Web

Build a **single self-contained `preview.html` from `design-spec.json`** that
validates the final product experience — scope is
`web_design_validation_only`. Embed an exact JSON snapshot, parse it at runtime,
and render its node graph with the vendored SpatialUI Web components. Product
markup must be a mount point rather than a second hand-authored design. The
renderer may implement generic mapping and declared domain visualizations, but
it must not contain independent product copy, tokens, dimensions, component
choices, states, or transition targets.

The result must be a _triggerable state machine_, not a static mock: the states
and transitions from the spec, real/fallback/error sample data, and any
high-risk confirmation dialog must all be reachable by clicking. Represent each
window/surface at its default size and make it reflow naturally from the spec's
responsive rules. Do not add visible design/debug controls such as viewport
presets, data-mode selectors, token legends, or implementation notes unless
they are genuine product features. Use the fixed light neutral
`#DAD6D3` as the `body` background, with no background image. This is
preview-only environment context, not an app-owned color or a
`design-spec.json` value.

Layout nodes with no `appearance` are transparent. The renderer must not infer
backgrounds, radii, or borders from node ids, names, or layout modes such as
`row`, `column`, `grid`, `panel`, `section`, or `card`. It must reject
`rootMaterial` and `appearance.material` rather than rendering them.
App-authored Preview CSS must not declare arbitrary backgrounds. Apply a
declared fill only through
`[data-design-surface] { background: var(--pico-design-surface-fill); }`, set
that attribute from the node ID, and create each filled node once. SpatialUI's
bundled component CSS remains library-owned.

Follow [`references/preview-guide.md`](./references/preview-guide.md) for the
coverage and JSON/HTML parity gates. Follow
[`references/spatialui-web-guide.md`](./references/spatialui-web-guide.md) for
the component map and event wiring. Inline the complete vendored
[`assets/spatialui-web/spatialui.bundle.js`](./assets/spatialui-web/spatialui.bundle.js)
into `preview.html` so the one-file prototype works offline. Apply the spec's
custom color scheme through `PicoTheme`; do not bypass the components by
styling native controls to resemble them.

Before rendering, resolve every icon asset. Inline a bundled ICON 7.0 SVG when
the source is `icon70://7.0/<name>`. For a declared custom icon, draw and save
the 24 x 24 `currentColor` SVG at its `design-assets/icons/` path, then inline
that exact file. Do not use an emoji, text glyph, or approximate catalog match
as a placeholder for a required custom icon.

Use native HTML only where no SpatialUI component exists or for non-control document semantics. In particular, do not ship a native `<button>`, `<input>`, `<select>`, `<textarea>`, or hand-rolled dialog when the catalog has the corresponding `sui-*` component. Do not generate Android/PICO runtime, device evidence, or parity claims — the Web prototype validates _logic and layout_, never real-device comfort, occlusion, or physical size.

### 6 · Critique again — and patch, bounded

Review the built prototype against the spec, plan, and quality bar below.
Rebuild the coverage list independently from `design-spec.json` — a component
merely _appearing_ is not the same as being implemented and triggerable. Confirm
that the embedded JSON exactly matches the external file and that no
implementation fact exists only in HTML. Audit the component map too: every
mapped `sui-*` tag must be registered, present in its intended state, and wired
through its public event; any native-control duplicate is a blocking gap.

Inspect the actual rendered page at the default and minimum surface sizes. Do
not hand off a structurally complete but visually weak prototype: hierarchy,
spacing, typography, contrast, assets, responsive composition, and the
signature element must all clear the design quality bar. Verify the body's
computed `background-color` is `rgb(218, 214, 211)` and its computed
`background-image` is `none`. Where you find gaps, patch `design-spec.json`
first, increment its revision, regenerate the HTML, and review again. Patch
renderer code directly only for a generic rendering defect or a declared
`domain_visual`. **Cap it at three rounds.** If it still doesn't clear the bar
after three rounds, say so plainly rather than relaxing the bar.

For a heavier, independent review pass — or when the user explicitly asks for a rigorous audit — spawn a fresh-context reviewer per [`references/review-guide.md`](./references/review-guide.md) so the critique isn't marking its own homework.

## Quality bar

A spatial app design is ready to hand off when:

- The app's job is a clear decision or task outcome, not a wall of widgets.
- The chosen form and scale (Planar window / HUD-Augment widget / Volumetric / Stage) follow from the spatial justification, not from habit.
- Spatialization is justified affordance by affordance, each with its 2D counterfactual; nothing floats for decoration.
- At least three real alternatives were compared and the rejected ones have reasons.
- Every window/surface has an internally validated size and records only implementation-relevant default/min/max dimensions.
- Layout, components, and visual language derive from the domain; swapping the domain would meaningfully change the design.
- Standard controls and system surfaces use the vendored SpatialUI Web components; custom elements are limited to justified domain-specific content.
- Every explicit icon resolves through the declared source priority; unmatched
  needs have a reviewed custom 24 x 24 SVG rather than a glyph or placeholder.
- `design-spec.json` is schema-valid and is the sole executable source for
  tokens, dimensions, node hierarchy, content, states, transitions, and data.
- The surface-discipline check passes: no app-authored content border and no
  `rootMaterial` / `appearance.material` field, no structural
  `layout` / `domain_visual` fill, and no ancestor/descendant pair both own a
  fill.
- The `preview.html` is a triggerable state machine covering every product state, transition, component, and data binding (normal + fallback + error), with natural responsive reflow and no design/debug-only UI.
- The embedded spec equals `design-spec.json`; the rendered page has passed
  visual inspection at default and minimum surface sizes.
- The signature element is present and the surrounding design stays quiet enough to let it read.

## Outputs

1. **`design-doc.md`** — filled from [`references/design-doc-template.md`](./references/design-doc-template.md): frame + spatial justification, the three alternatives and the choice, the token system, surface sizing, state graph, components, and the two critiques.
2. **`design-spec.json`** — schema-valid executable design IR and the source of
   truth for both renderers.
3. **`preview.html`** — one self-contained SpatialUI Web validation prototype
   rendered from an exact embedded snapshot of `design-spec.json`, scope
   `web_design_validation_only`.
4. **`design-assets/icons/*.svg`** — only when the source-priority check reaches
   the custom drawing step; each file is referenced by `design-spec.json` and
   embedded into the preview.

Do not produce an Android/PICO project, runtime code, or device evidence.
Container/window _enum_ decisions (`ON_PLAIN`, `STAGE_MIXED`, …) and code belong
to the downstream skill, not here — keep design facts in PICO design terminology
(Shared/Full Space, WindowContainer Planar/Volumetric, Stage).
