# Container & Window-Model Decisions

The two most consequential choices when generating a PICO Spatial App: which
root container the app registers, and how its surfaces are arranged. Both are
decided in the **Decide** stage, before any Kotlin is written, and both must be
justified against concrete evidence.

Getting either wrong is expensive: the container is registered at install time
in `AndroidManifest.xml`, decides whether the app runs in Shared Space or Full
Space, and determines which APIs are even legal. Changing it later means
rewriting the manifest, the entry chain, coordinates, and ornaments together.

---

## Part 1 — Container

### Terminology mapping (skill-internal vs official SDK)

Five internal enums, mapped to official PICO concepts (verified against
`pico-cli project create` generated output):

| Skill enum          | pico-cli template       | Root DSL                 | Authoritative manifest meta-data                                                                                                |
| ------------------- | ----------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `ON_PLAIN`          | `--template planar`     | `DefaultWindowContainer` | `pico.spatial.windowcontainer.style="1"` (Form.Planar)                                                                          |
| `IN_VOLUME`         | `--template volumetric` | `DefaultWindowContainer` | `pico.spatial.windowcontainer.style="2"` (Form.Volumetric); 3D `defaultsize=WxHxD`; extra `volumealignment` + `volumebasepanel` |
| `STAGE_MIXED`       | `--template stage`      | `DefaultStage`           | `pico.spatial.stage.style="1"` (StageStyle.Mixed)                                                                               |
| `STAGE_PROGRESSIVE` | `--template stage`      | `DefaultStage`           | `pico.spatial.stage.style="2"` (StageStyle.Progressive) + `immersion` / `immersion_min` / `immersion_max` (range 0–100)         |
| `STAGE_FULL`        | `--template stage`      | `DefaultStage`           | `pico.spatial.stage.style="3"` (StageStyle.Full)                                                                                |

This manifest meta-data is also what `scan_implementation.py` reads back to
verify the container — it is the runtime source of truth, which is why no
separate declaration artifact is needed.

Important caveats:

- `ON_PLAIN` / `IN_VOLUME` are **not** official SDK class names — they are this
  skill's decision shorthand for two manifest-`style` variants of
  `DefaultWindowContainer`.
- `MIXED` / `PROGRESSIVE` / `FULL` correspond to `StageStyle` and are chosen via
  the **`pico.spatial.stage.style` manifest meta-data** (NOT via a code
  parameter to `openStage(...)`). All three share the same `--template stage`
  base project; only the `style` value differs.
- `pico.spatial.stage.style="0"` exists as Automatic and currently defaults to
  Mixed; not exposed as a separate enum because runtime behaviour collapses to
  STAGE_MIXED.
- See `spatial-anchor.md` for the authority status of world-tracking class names.

### Decision priority

1. **explicit user requirement** — if the user clearly asks for immersive stage / passthrough / anchors / skybox, honor that
2. **existing module architecture** — in existing-module mode, keep the current root unless there is a real reason to change it
3. **input semantics** — visual or textual cues, only after checking 1 and 2
4. **safe default** — if still ambiguous, choose the least disruptive option

### Decision tree

```
Start with the target module, not just the raw reference input.

Q1: Did the user explicitly ask for immersive / stage-only behavior
    (anchors, environment mesh, boundless scene, skybox, passthrough scene)?
├─ YES → choose Stage that matches the requested experience
└─ NO
   Q2: In existing module mode, does the module already use DefaultWindowContainer or DefaultStage?
   ├─ YES → keep that root unless the input clearly requires a different container
   └─ NO
      Q3: Does the input show or describe a real-world / passthrough background behind free spatial content?
      ├─ YES
      │  ├─ content is primarily free 3D scene content → Stage · MIXED
      │  ├─ content is mostly a single flat panel → WindowContainer · ON_PLAIN
      │  └─ content is a boxed panel with visible depth/front-face UI → WindowContainer · IN_VOLUME
      └─ NO
         ├─ virtual environment with adjustable immersion → Stage · PROGRESSIVE
         ├─ fully immersive world with no real-world background → Stage · FULL
         └─ otherwise → WindowContainer · ON_PLAIN
```

### Cheat sheet: visual cues

| Input cue                                             | Strong signal for...                                                 |
| ----------------------------------------------------- | -------------------------------------------------------------------- |
| Toolbar bar with icons at the bottom of a flat panel  | ON_PLAIN                                                             |
| Toolbar at the bottom of a 3D cube's front face       | IN_VOLUME                                                            |
| 3D model rendered inside a rectangular panel boundary | IN_VOLUME, or ON_PLAIN + `SpatialModelView` if the rest is mostly 2D |
| Real room visible (chairs, floor, walls) behind UI    | Stage MIXED                                                          |
| Skybox / starfield / virtual room behind UI           | Stage PROGRESSIVE or FULL                                            |
| Slider or icon implying "see-through level"           | Stage PROGRESSIVE                                                    |
| HUD-style overlay locked to head                      | Possibly Stage FULL with head-locked content                         |
| Multiple disconnected panels                          | Multiple `WindowContainer`s, not multiple default roots              |

### Container × feature legality (apply inline, never defer to Verify)

Consult this during the container decision itself. If a requested feature is
illegal under the chosen container, revise the container, drop the feature, or
explicitly escalate the architecture change with justification.

| Feature                                     | ON_PLAIN     | IN_VOLUME    | STAGE_MIXED              | STAGE_PROGRESSIVE          | STAGE_FULL |
| ------------------------------------------- | ------------ | ------------ | ------------------------ | -------------------------- | ---------- |
| 2D Compose UI                               | ✅           | ✅           | ✅ (panels inside stage) | ✅                         | ✅         |
| `SpatialModelView` 3D inside panel          | ✅           | ✅           | ✅                       | ✅                         | ✅         |
| Free 3D entities in space (Spatial ECS)     | ❌           | ❌           | ✅                       | ✅                         | ✅         |
| World-tracking / plane / mesh anchor APIs † | ❌           | ❌           | ✅                       | ✅                         | ✅         |
| Environment mesh / `scene.rayCast`          | ❌           | ❌           | ✅                       | ✅                         | ✅         |
| Passthrough background                      | ✅ (default) | ✅ (default) | ✅                       | partial (immersion slider) | ❌         |
| Skybox / virtual environment                | ❌           | ❌           | ❌ (real world only)     | ✅                         | ✅         |
| Hand gesture / controller haptics           | ✅           | ✅           | ✅                       | ✅                         | ✅         |
| Multiple coexisting apps in shared space    | ✅           | ✅           | ❌ (Full Space)          | ❌                         | ❌         |

† Verified against PICO SpatialSDK source. World anchors live under
`com.pico.spatial.sense.world.*` (`WorldTrackingManager` / `WorldAnchor`); plane
sensing under `com.pico.spatial.sense.plane.*`; environment mesh under
`com.pico.spatial.sense.mesh.*`. ECS-side `AnchorEntity` / `AnchorComponent`
live in `com.pico.spatial.core.ecs`. All Stage-only APIs are marked
`@com.pico.spatial.core.annotation.RequiredFullSpace`. Full shapes and code
samples: `spatial-anchor.md`.

Hard implications:

- `anchor`, `env_mesh`, free 3D scene → **requires Stage**. Do NOT pick `ON_PLAIN` / `IN_VOLUME`.
- `skybox` / fully virtual environment → requires `STAGE_PROGRESSIVE` or `STAGE_FULL`. `STAGE_MIXED` keeps the real-world background.
- "Coexists with other apps" → requires WindowContainer. Stage forces Full Space.

### Gate — container legality

Before implementation:

- the container choice must not conflict with required spatial features
- existing-module mode must not silently switch root architecture

On failure: revise the spatial intent, remove the conflicting feature, or
explicitly escalate the architecture change with justification.

### Default root vs secondary containers

| Concept                                     | Count                   | How it is configured                                                                                                                     |
| ------------------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `DefaultWindowContainer` / `DefaultStage`   | **exactly one** per app | AndroidManifest meta-data; runtime-guarded (registering two defaults throws)                                                             |
| `WindowContainer(id = …)` / `Stage(id = …)` | many allowed            | DSL parameters; opened via `navigator.openWindowContainer(id)` / `navigator.openStage(id)` (`navigator = LocalSpatialNavigator.current`) |

A `DefaultWindowContainer` app that also declares `Stage(id = …)` blocks is a
**valid single-root app**, not an illegal "mixed root". Only two coexisting
_default_ roots are illegal.

### Responsibility boundaries (never cross these)

| Surface         | Its toolkit                                                  |
| --------------- | ------------------------------------------------------------ |
| Stage           | `AttachmentPanel` on an ECS anchor; `SpatialView` + entities |
| WindowContainer | `TabBar` / `Toolbar` / `Subwindow` window fittings           |

Do not carry `TabBar` / `Toolbar` / `Subwindow` into a Stage, and do not put
`AttachmentPanel` inside a window.

### Container migration checklist

A container change is a Decide-stage change, not a build-time fix. In order:

1. re-run the container decision with the new evidence
2. update `AndroidManifest.xml` meta-data
3. update the `mainApp` root (`DefaultWindowContainer` ↔ `DefaultStage`)
4. update coordinates and content model (flat page ↔ ECS + `AttachmentPanel`)
5. re-verify runtime launch

Never migrate a container to make a compile error or visual glitch go away.

---

## Part 2 — Window model

Pick exactly one. Never output "A or B".

| Window model              | Use when                                                 | First implementation choice                                                                                                                                   |
| ------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `single_panel`            | one main panel, no independent overlay or second surface | one `DefaultWindowContainer` root, single panel hierarchy                                                                                                     |
| `single_panel_with_popup` | main panel plus dropdown / menu / contextual overlay     | same root; popup stays an overlay or `SpatialPopup`                                                                                                           |
| `sidebar_content`         | persistent left rail plus main content                   | one panel root with `Row(sidebar, content)`                                                                                                                   |
| `master_detail`           | list pane and detail pane visible simultaneously         | one panel root with two persistent panes                                                                                                                      |
| `window_plus_subwindow`   | primary window plus a secondary persistent tool panel    | main window plus `Subwindow`                                                                                                                                  |
| `multi_window`            | multiple clearly independent panels in space             | `DefaultWindowContainer` plus additional `WindowContainer(...)`, opened via `navigator.openWindowContainer(id)` (`navigator = LocalSpatialNavigator.current`) |

### Hard rules

- A popup / dropdown / context menu / tooltip / toast / hover card is **not** a second window.
- Sidebar + content in one rounded panel is **one** window.
- List + detail visible together is `master_detail`, not `multi_window`.

### Overlay vs second window cheat sheet

| Input clue                                                               | Usually means           |
| ------------------------------------------------------------------------ | ----------------------- |
| Small panel anchored to a button or top-right corner                     | overlay / popup         |
| Tooltip-like element that would close when focus changes                 | overlay                 |
| Sidebar + main content in one rounded panel                              | one window              |
| Main view + detail view sharing one outer card/panel                     | one window              |
| Two disconnected panels with separate bounds and no shared outer surface | likely multiple windows |

### Subwindow vs multi_window escalation

When the input shows more than one panel, do not jump to `multi_window`:

1. **Layered UI inside one panel** (popup / dropdown / contextual menu) → stay in `single_panel` or `single_panel_with_popup`. No new window.
2. **One persistent auxiliary tool panel in the same session** → `Subwindow` (`window_plus_subwindow`). One launcher, one manifest entry, shared lifecycle.
3. **Panels with independent lifecycle requirements, or independent sizes/positions remembered across launches** → additional `WindowContainer(...)` blocks (`multi_window`). Showing or hiding an auxiliary panel while using the main window does not by itself establish an independent lifecycle. Use the existing navigator and entry conventions when implementing the chosen windows.

For a persistent auxiliary panel, use `Subwindow` unless a concrete requirement establishes rule #3. User wording such as "a separate window" or "open settings in a new window" describes presentation, but does not by itself establish independent lifecycle or placement memory. When the panel only configures the current main view, state that relationship and proceed with `Subwindow`; ask only if unresolved lifecycle or placement intent would change the decision.

Incremental examples:

- Add a font-size and sorting settings panel to the current notes app, preferably in a new window → `window_plus_subwindow`; these controls serve the current notes view.
- Add a companion window that must remain usable when the main window closes and retain its own size/position across launches → `multi_window`; the requirement supplies the independent lifecycle and placement facts.
- Change a label or control inside the existing panel → keep the existing window model; no window-structure review is needed.

> ⚠ No machine check can prove disconnected-surface evidence from code alone.
> An unjustified `multi_window` will pass every automated gate — this rule is
> yours to enforce during the Decide stage and the Verify self-review.

### Gate — window-model singularity

- exactly one primary `window_model`
- the closest competing alternative is explicitly rejected with a reason citing a concrete fact or a rule number above

Generic rejections ("not needed", "not applicable", "no evidence") are a BLOCK,
not a justification.

### Window-fitting vs in-panel overlay (HARD)

When a region is a "floating navigation strip", "edge tool strip", or
"persistent auxiliary panel", the implementation MUST use a SpatialUI
window-level fitting, not a hand-rolled `Box.align(...)` overlay inside the main
panel. Visual similarity (a rounded capsule pinned to the top) is not semantic
equivalence.

| Region semantics                                                                 | Correct implementation                                                                                 | Wrong implementation                                                            |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| Persistent navigation pinned to a window edge                                    | `TabBar(placement = TabBarPlacement.Top \| Bottom \| Start \| End)` as a **sibling** of the main panel | `Box.align(Alignment.TopCenter) { Row { … capsules … } }` inside the main panel |
| Persistent action strip / icon rail pinned to an edge                            | `Toolbar { … }` as a sibling of the main panel                                                         | hand-built `Row` with `clickable` icons in the page tree                        |
| Long-lived auxiliary panel sharing window lifecycle but rendering independently  | `Subwindow { … }`                                                                                      | a wide `Box` beside the main content with manual resize handling                |
| Surface with explicit independent lifecycle or remembered placement requirements | Additional `WindowContainer(...)` after the escalation decision above                                  | treating it as a main-window attachment solely because it contains tools        |
| In-content floater / anchored popup / contextual menu                            | `SpatialPopup` or an in-page overlay                                                                   | (ok to keep as `Box.align(...)` inside the page)                                |

`TabBar` and `Toolbar` do **not** accept a `modifier` — position is owned by the
system. If you want to pass `Modifier.align`, you have picked the wrong shape.

### Pre-code checklist (run BEFORE writing UI for each region)

1. Pinned to a window edge regardless of page scroll? → window-level fitting (`TabBar` / `Toolbar`)
2. Long-lived auxiliary surface that shares the main window's lifecycle? → `Subwindow`
3. Explicit independent lifecycle or remembered placement requirements? → additional `WindowContainer(...)` under the escalation rules above
4. Moves with page content / appears inside a card? → normal Composable in the page tree

Failing this checklist for a `TabBar`-shaped element is the single most common
regression in this skill. `scan_implementation.py` warns on the hand-rolled
shape, but the check is heuristic — handle it here, not at Verify.

Common rationalization to reject: _"it is not a second window, so it belongs in
the page tree."_ Not being `multi_window` only rules out an independent
lifecycle; it may still be a window-level ornament.

### Window sizing

First-open size comes from the manifest `defaultsize`, not from
`windowConstraints(...)` — that only bounds interactive resizing. Derive the
window size from the app-owned region of a reference image, never from the full
screenshot including the environment behind it.
