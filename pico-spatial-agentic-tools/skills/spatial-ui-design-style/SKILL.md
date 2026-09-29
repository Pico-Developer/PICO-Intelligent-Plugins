---
name: spatial-ui-design-style
description: >-
  Use when any upstream workflow emits or edits SpatialUI Compose UI code and
  needs PicoTheme, SpatialUI built-in components, theme role routing,
  hover/haptics, glass background, Material bans, or design-style verifier
  admission. This is a mandatory Compose UI sub-contract, not a primary
  app-generation, scaffold, design-package, or 3D scene workflow.
license: 'Apache-2.0'
---

# SpatialUI Design-Style Skill — Hard Constraints for Compose UI

This skill is the **code-admission ruleset** for any PICO spatial application
that emits Compose UI. It is intentionally short. Detailed guidance is split
into [`references/`](./references); read on demand.

Routing boundary: this skill is a mandatory sub-contract whenever Compose UI is emitted or edited. It should be loaded by `spatial-design-to-app`, `spatial-app-onboarding`, screenshot/Figma codegen, or manual UI-edit flows before writing UI code. It is not the primary route for app generation, scaffold creation, design-package production, container/window-model decisions, or 3D scene planning.

## Highest-Priority Decision Table (Read First)

These rules are absolute. They override personal preference, library
shortcut, and generic Compose / Material habits.

| #   | Scenario                        | Highest-Priority API                                                                                                                                                                                                                                                                                                                                                                                                                                            | Allowed Exception                                                                                                                                                                                                                                                                                                                                                                                |
| --- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Theme wrapping                  | `PicoTheme { ... }` at the root Activity / `WindowContainer` / `Stage`. **Keep the native SpatialUI `ColorScheme` unchanged: do not pass `colorScheme`, construct `ColorScheme(...)`, or call `systemColorScheme(...).copy(...)` to replace `fill*`, `label*`, interaction, status, hover/pressed, or divider roles. Custom colors are allowed only as named app-owned tokens used directly by the intended content.**                                          | None for generated app UI.                                                                                                                                                                                                                                                                                                                                                                       |
| 2   | UI components                   | `com.pico.spatial.ui.design.*` built-ins                                                                                                                                                                                                                                                                                                                                                                                                                        | Only when no built-in fits — then custom (see `references/custom-component.md`)                                                                                                                                                                                                                                                                                                                  |
| 3   | Custom hover visuals            | `Modifier.spatialHoverEffect`                                                                                                                                                                                                                                                                                                                                                                                                                                   | None — never reimplement with `hoverable + animateFloatAsState(scale)`                                                                                                                                                                                                                                                                                                                           |
| 4   | Window / root-node background   | **Use the system-default `Material.Regular` glass** — write nothing on the root. The on/off switch differs by container: `DefaultWindowContainer` → manifest `pico.spatial.windowcontainer.materialbackground` (per-Activity); `WindowContainer(...)` / `Augment(...)` → DSL parameter `enableMaterialBackground` (default `true`).                                                                                                                             | To switch glass style or go opaque, first flip the **right** switch off (`materialbackground="0"` for `DefaultWindowContainer`, `enableMaterialBackground = false` for `WindowContainer/Augment`), then either `Modifier.backgroundMaterial(enable = true, style = Material.<Style>)` or `// design-style: opaque-root` + `Modifier.background(<role>)`. **Never paint solid color over glass.** |
| 5   | Foreground / background pairing | Prefer SpatialUI component-owned state colors. In a component slot that provides `LocalContentColor`, omit `Text.color` / `Icon.tint` so content inherits the component foreground. On an ordinary app-owned surface, choose an intentional semantic foreground for the actual background. When customizing a state, consider its effective container and content colors together; do not infer white text or a dark fill merely because the state is selected. | Explicit slot colors are allowed only when the accepted design requires them and they remain readable against that component state's effective background. A foreground may remain unchanged across states when it is readable on every corresponding background.                                                                                                                                |
| 6   | Content surface discipline      | Structural `layout` / `domain_visual` regions remain transparent. Do not add app-authored borders or material. When a `design-spec.json` exists, every app-authored `background` or content `Card` maps exactly once to a bounded content node with `appearance.fill`; `.backgroundMaterial(...)` is forbidden for restoration.                                                                                                                                 | Standard SpatialUI control internals, input focus, accessibility focus, dialogs, popups, and system window backgrounds keep their library-owned treatment. They are not app-authored layout decoration.                                                                                                                                                                                          |

## Six Core Principles

1. **Always wrap with `PicoTheme`, and preserve its native palette.** Top-level
   `Activity` / `DefaultWindowContainer` / `Stage` MUST be wrapped with
   `PicoTheme { ... }`, which uses `systemColorScheme(LocalContext.current)`.
   Do not redefine or overwrite any public `ColorScheme` role, including
   `fill*`. **Custom colors remain explicitly allowed**: carry each through a
   named app-owned token in the theme layer or an annotated fixed literal
   (`// design-style: fixed-figma-color <source>`) and use it directly at the
   intended content call site. Do not pass custom colors into
   `PicoTheme(colorScheme = ...)`, `ColorScheme(...)`, or
   `systemColorScheme(...).copy(...)`.
2. **Prefer built-in design components.** Search `com.pico.spatial.ui.design.*`
   first; custom only when no built-in fits.
3. **Route through theme roles & SpatialUI modifiers.**
   Colors → `PicoTheme.colorScheme.<role>`;
   typography → `PicoTheme.typography.<role>`;
   click → `Modifier.clickable(...)`, which uses `LocalIndication.current` by
   default; add `controllerHapticFeedback` only when haptics are required, using
   the clickable's shared `interactionSource`;
   **hover MUST use `Modifier.spatialHoverEffect` — highest priority**;
   disabled → `LocalDisableAlpha.current`.
4. **Window / container root glass is system-provided; do not paint over it.**
   Every PICO window container ships with `Material.Regular` glass on by
   default — but the **on/off switch differs by container kind**:
   - `DefaultWindowContainer` → controlled per-Activity in the launcher
     `<activity>` manifest meta-data
     `pico.spatial.windowcontainer.materialbackground` (default `"1"`).
     There is no DSL knob for `DefaultWindowContainer`.
   - `WindowContainer(...)` / `Augment(...)` → controlled by the Kotlin
     DSL parameter `enableMaterialBackground: Boolean = true` on the
     constructor. Manifest meta-data does NOT apply to these.

   For the common case **write no background on the window root** — the
   system already paints the glass. To use a different glass style or to
   render no glass, first flip the **correct switch** for that container
   (manifest `"0"` for `DefaultWindowContainer`,
   `enableMaterialBackground = false` for `WindowContainer/Augment`), then
   either call `Modifier.backgroundMaterial(enable = true, style = Material.<Style>)`
   for a different style or add `// design-style: opaque-root` +
   `Modifier.background(PicoTheme.colorScheme.<role>)` for an opaque
   root. **Never paint a solid color (or `fillPrimary`) on top of the
   system glass — it defeats both the glass and vibrant linkage.**

5. **Preserve color ownership and readable pairs.** `PicoTheme` installs
   `LocalColorScheme`, not a blanket `LocalContentColor`, while SpatialUI
   components provide their own state-aware content colors inside supported
   slots. Prefer those component defaults and omit slot-level `Text.color` /
   `Icon.tint`. On an ordinary app-owned surface, select an intentional
   foreground for the actual background. When customizing selection, toggle,
   category, or brand colors, evaluate the effective container and content
   colors for every affected state together. Either color may remain unchanged
   when the resulting pair stays readable.
6. **Keep content structure flat.** Structural `layout` and `domain_visual`
   regions remain transparent; use spacing, alignment, typography, and one
   bounded content surface instead of large panel or card-inside-card styling.
   App-authored content borders and material are forbidden. When restoring a
   design package, place exactly one
   `// design-style: design-surface <node-id>` immediately before every
   app-authored `.background(...)` or content `Card(...)`; the node must declare
   `appearance.fill`, and the ID must not be reused by another surface call.
   Reject `rootMaterial`, `appearance.material`, and `.backgroundMaterial(...)`
   rather than carrying them into app code.

## Stateful Color Restoration (HARD)

Use this decision order while generating or editing UI:

1. If a SpatialUI built-in already expresses the required state, keep its
   default colors and let `Text` / `Icon` slots inherit.
2. If the accepted design requires custom colors, configure them through the
   component's `colors` API when available. Do not then independently override
   the same slot foreground.
3. For a custom state implementation, identify each state's effective
   background and foreground. Consider both values, including unchanged
   defaults; do not require both values to change.
4. Treat `labelPrimaryLight` as a bright foreground for dark or emphasized
   backgrounds, not as a universal selected-state color.
5. Avoid obvious low-contrast combinations such as dark-on-dark,
   light-on-light, white on light gray, or white on a bright category color.
   Translucent fills such as `fillSecondary` depend on the surface beneath them,
   so judge the composed result rather than the token name alone.

See `references/tokens.md` for the role visual reference. Those literals are
diagnostic anchors only; generated app code continues to consume
`PicoTheme.colorScheme` roles.

## Material Surface Shape (HARD)

Every rounded view-level material surface must establish its shape before the
material:

```kotlin
val shape = RoundedCornerShape(8.dp)
Modifier
    .clip(shape)
    .backgroundMaterial(enable = true, style = Material.Regular)
```

A deliberately rectangular material surface must place
`// design-style: rectangular-material <reason>` on the material line or
immediately above its modifier chain. Missing pre-material clipping is an error
because it produces square material corners. Do not add a border merely to make
the material's shape visible.

## Minimal Compliant Skeleton

```kotlin
class MyApp : Application() {
    override fun onCreate() { super.onCreate(); launch(::mainApp) }
}

fun mainApp(scope: SpatialAppScope) = with(scope) {
    // Launcher window — Material.Regular glass is provided by the
    // <activity> manifest meta-data
    // `pico.spatial.windowcontainer.materialbackground="1"`.
    DefaultWindowContainer {
        PicoTheme {
            // ✅ Rule #4: do NOT add Modifier.background(...) /
            //    Modifier.backgroundMaterial(...) here unless you have first
            //    set that meta-data to "0".
            Box(Modifier.fillMaxSize()) {
                Text(
                    "Ready",
                    color = PicoTheme.colorScheme.labelPrimary,
                )
            }
        }
    }

    // Any extra window the app launches itself: glass is controlled by
    // the DSL parameter `enableMaterialBackground` (default true). Both
    // declaration styles are valid:
    //
    //  (A) Direct parameter style — used below
    //  (B) properties = { ... } DSL style — set fields inside the lambda,
    //      e.g. properties = { defaultSize = ...; enableMaterialBackground = false }
    //
    // Do NOT add a background on its root unless the matching switch is off.
    WindowContainer(
        id = "DetailPanel",
        form = Form.Planar,
        defaultSize = WindowContainerSize(width = 640.dp, height = 360.dp),
        // enableMaterialBackground = true // default; can be omitted
    ) {
        PicoTheme {
            Box(Modifier.fillMaxSize()) {
                DetailContent()
            }
        }
    }
}
```

## On-Demand References

Read the file under `references/` whose topic matches the current task.

| When you need to …                                                                                     | Read                                                                         |
| ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| Pick a built-in component, role, or sizing tier                                                        | [`references/builtins.md`](./references/builtins.md)                         |
| Resolve color / typography / motion / locals                                                           | [`references/tokens.md`](./references/tokens.md)                             |
| Write a custom Composable (param order, click + haptics + audio, disabled)                             | [`references/custom-component.md`](./references/custom-component.md)         |
| Decide window-root / Subwindow / Stage background                                                      | [`references/window-background.md`](./references/window-background.md)       |
| Customize hover visuals                                                                                | [`references/hover.md`](./references/hover.md)                               |
| Restore the design's theme palette, use custom colors, choose Vibrant levels, or infer adaptive colors | [`references/vibrant-guide.md`](./references/vibrant-guide.md)               |
| Use 3D modifiers, Augment, SpatialView, gestures, vibrant                                              | [`references/spatial-capabilities.md`](./references/spatial-capabilities.md) |
| Look up the full anti-pattern table                                                                    | [`references/anti-patterns.md`](./references/anti-patterns.md)               |
| Look up grep-able compliance rules                                                                     | [`references/compliance-signals.md`](./references/compliance-signals.md)     |

## Verify (REQUIRED before reporting "done")

After producing or editing Compose code, run the verifier and fix every
`error`-level finding:

```bash
# Design deliverable declares app-owned custom colors — pass each one:
scripts/verify-design-style.sh <module-or-src-path> \
    --design-color <token>=<#RRGGBB> [--design-color ...] \
    [--design-spec <path-to-design-spec.json>]

# Genuinely no design colors to restore — say so explicitly:
scripts/verify-design-style.sh <module-or-src-path> --no-design-colors
```

R1b needs to know the authoritative design colors. Passing neither flag is an
invocation error (exit 2) rather than a quiet skip, so a caller that forgets to
forward its colors cannot silently turn the fidelity gate into a no-op. A legacy
`.scratch/evidence_packet.json` is still read when present.

Pass every app-owned custom color, using a non-native token name. Native
`ColorScheme` roles are intentionally omitted because they remain unchanged.
CSS `rgba(...)` values must be converted to `#AARRGGBB` before being passed.

The script enforces the machine-checkable rules in
[`references/compliance-signals.md`](./references/compliance-signals.md).
Foreground/background pairing remains a generation-time responsibility rather
than a broad source scan. For Figma-driven flows, also pass the same rule summary into
`d2c_verify_code` via `ruleContext` so the independent reviewer applies the
same yardstick — that tool comes from the external `codin-d2c-figma-to-code` MCP
server, so when it is unavailable, `verify-design-style.sh` remains the binding
gate and the missing independent review is disclosed rather than assumed passed.

## Delivery Checklist

Always emit, with the final code:

1. Built-in SpatialUI components used (names + packages).
2. Custom-component rules applied (token roles + modifiers).
3. Where `PicoTheme` is wrapped.
4. **Design-color mapping** — list every custom design token/value and its
   app-owned declaration or annotated fixed literal. Confirm that native
   SpatialUI `ColorScheme` roles remain unchanged.
5. **Window / root-node background choice** — for **each** container the
   app launches (`DefaultWindowContainer`, every `WindowContainer(...)`,
   each `Augment(...)`), state which case applies:
   (a) using the system-default `Material.Regular` glass with no root
   background, (b) custom glass style after disabling the **right**
   switch (manifest for `DefaultWindowContainer`, DSL
   `enableMaterialBackground = false` for `WindowContainer/Augment`), or
   (c) explicit opaque root after disabling the same switch. Mention
   which switch was flipped and why.
6. **Custom hover handling**: confirm `Modifier.spatialHoverEffect` (never
   `hoverable + scale`).
7. **Color-pair audit**: confirm component slots inherit component-owned colors
   by default, and every custom state uses a readable effective foreground /
   background pair without duplicate slot overrides.
8. `verify-design-style.sh` result (must be clean).
9. **Surface discipline**: confirm structural `layout` and `domain_visual`
   regions are transparent, every app-authored surface maps exactly once to a
   fill-owning design node when a design spec exists, and no app-authored
   content border or material is present.

## Backlog

Review / update history lives in the repository change history.
Append new dated entries at the top using the template in that file.
