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

These four rules are absolute. They override personal preference, library
shortcut, and generic Compose / Material habits.

| #   | Scenario                      | Highest-Priority API                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Allowed Exception                                                                                                                                                                                                                                                                                                                                                                                |
| --- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Theme wrapping                | `PicoTheme { ... }` at the root Activity / `WindowContainer` / `Stage`. **For a design-driven flow, call `systemColorScheme(...)` once and explicitly assign all 16 public roles in `.copy(...)`: exact design tokens for overridden roles and `role = system.role` for deliberate Vibrant inheritance. Inject the complete result with `PicoTheme(colorScheme = …)`. A partial copy or plain `PicoTheme {}` is a hard failure. Custom colors without a PICO role remain named tokens.** | Plain `PicoTheme {}` is allowed only when there is genuinely no design product to restore (e.g. a throwaway internal scaffold). Inherited adaptive roles remain system Vibrant values, but their assignments must still be explicit in the complete scheme.                                                                                                                                      |
| 2   | UI components                 | `com.pico.spatial.ui.design.*` built-ins                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Only when no built-in fits — then custom (see `references/custom-component.md`)                                                                                                                                                                                                                                                                                                                  |
| 3   | Custom hover visuals          | `Modifier.spatialHoverEffect`                                                                                                                                                                                                                                                                                                                                                                                                                                                            | None — never reimplement with `hoverable + animateFloatAsState(scale)`                                                                                                                                                                                                                                                                                                                           |
| 4   | Window / root-node background | **Use the system-default `Material.Regular` glass** — write nothing on the root. The on/off switch differs by container: `DefaultWindowContainer` → manifest `pico.spatial.windowcontainer.materialbackground` (per-Activity); `WindowContainer(...)` / `Augment(...)` → DSL parameter `enableMaterialBackground` (default `true`).                                                                                                                                                      | To switch glass style or go opaque, first flip the **right** switch off (`materialbackground="0"` for `DefaultWindowContainer`, `enableMaterialBackground = false` for `WindowContainer/Augment`), then either `Modifier.backgroundMaterial(enable = true, style = Material.<Style>)` or `// design-style: opaque-root` + `Modifier.background(<role>)`. **Never paint solid color over glass.** |
| 5   | Text foreground resolution    | Every app-authored `Text` must resolve a foreground color. On ordinary `Box` / `Row` / `Column` surfaces, pass `color = PicoTheme.colorScheme.labelPrimary` (or the intended semantic `label*` / state role) explicitly. `PicoTheme` provides a `ColorScheme` but does **not** provide `LocalContentColor`; a bare `Text` can render black on dark glass.                                                                                                                                | A direct child slot of a SpatialUI component that provides `LocalContentColor` may inherit it, but mark the call with `// design-style: inherited-content-color <provider>`. Do not assume CSS-like inheritance from a parent background or from `PicoTheme`.                                                                                                                                    |

## Five Core Principles

1. **Always wrap with `PicoTheme`, and restore the design's palette.** Top-level
   `Activity` / `DefaultWindowContainer` / `Stage` MUST be wrapped with
   `PicoTheme { ... }`. The default `colorScheme` calls
   `systemColorScheme(LocalContext.current)` internally, so plain
   `PicoTheme { ... }` is enough **only when there is genuinely no design product
   to restore**. The objective is to reproduce the final design deliverable, so
   when Figma, a screenshot/design package, or the design colors the caller
   passes to `verify-design-style.sh --design-color`
   provides a coordinated theme — its primary/accent color plus the semantic
   palette that is color-matched to it — read `systemColorScheme(...)` once,
   explicitly assign all 16 public roles in `.copy(...)`, override every
   declared role with the exact design value, forward inherited values as
   `role = system.role`, and pass the result through
   `PicoTheme(colorScheme = ...)`. **Custom colors are explicitly allowed.** A
   design value that has no matching PICO role (a brand hue, a decorative accent)
   is still first-class: carry it verbatim through a named brand token in the
   theme layer or an annotated fixed literal
   (`// design-style: fixed-figma-color <source>`) — do not snap it to the
   nearest default role. Merely referencing default `PicoTheme.colorScheme.*`
   roles does not preserve the design palette and MUST fail review. A partial
   `systemColorScheme(...).copy(...)` also fails because it leaves part of the
   final theme contract implicit.
2. **Prefer built-in design components.** Search `com.pico.spatial.ui.design.*`
   first; custom only when no built-in fits.
3. **Route through theme roles & SpatialUI modifiers.**
   Colors → `PicoTheme.colorScheme.<role>`;
   typography → `PicoTheme.typography.<role>`;
   click → `LocalIndication.current` + `controllerHapticFeedback`
   (shared `interactionSource`);
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

5. **Resolve every text foreground.** HTML/CSS `color` inheritance does not
   carry into SpatialUI Compose. `PicoTheme(colorScheme = ...)` installs
   `LocalColorScheme`, but it does not install `LocalContentColor`. Therefore,
   every `Text` on an ordinary layout surface must pass an explicit semantic
   `color`; otherwise `Text` can reach `BasicText` with `Color.Unspecified` and
   render black against dark glass. In a SpatialUI component slot that
   intentionally provides `LocalContentColor`, keep inheritance only with a
   nearby `// design-style: inherited-content-color <provider>` marker.

## Material Surface Shape (HARD)

`backgroundMaterial(...)` does not inherit a later `border(..., shape)`.
Every view-level material surface must establish its shape before the material:

```kotlin
val shape = RoundedCornerShape(8.dp)
Modifier
    .clip(shape)
    .backgroundMaterial(enable = true, style = Material.Regular)
    .border(1.dp, PicoTheme.colorScheme.dividerLine, shape)
```

Use one shared `shape` value for clipping and borders. A deliberately rectangular
material surface must place `// design-style: rectangular-material <reason>` on
the material line or immediately above its modifier chain. Missing pre-material
clipping is an error because it produces square material corners even when the
border appears rounded.

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
# Design deliverable declares brand/semantic colors — pass each one:
scripts/verify-design-style.sh <module-or-src-path> \
    --design-color <slot>=<#RRGGBB> [--design-color ...]

# Genuinely no design colors to restore — say so explicitly:
scripts/verify-design-style.sh <module-or-src-path> --no-design-colors
```

R1b needs to know the authoritative design colors. Passing neither flag is an
invocation error (exit 2) rather than a quiet skip, so a caller that forgets to
forward its colors cannot silently turn the fidelity gate into a no-op. A legacy
`.scratch/evidence_packet.json` is still read when present.

Pass the complete visual color inventory, not only the primary brand colors:
surface/fill colors, primary and secondary text, dividers/borders, semantic
states, and custom decorative colors all count. CSS `rgba(...)` values must be
converted to `#AARRGGBB` before being passed. Web-only environment simulation
colors are excluded only when the design package explicitly marks them as such.

The script enforces the rules in
[`references/compliance-signals.md`](./references/compliance-signals.md)
(R1–R7). For Figma-driven flows, also pass the same rule summary into
`d2c_verify_code` via `ruleContext` so the independent reviewer applies the
same yardstick — that tool comes from the external `codin-d2c-figma-to-code` MCP
server, so when it is unavailable, `verify-design-style.sh` remains the binding
gate and the missing independent review is disclosed rather than assumed passed.

## Delivery Checklist

Always emit, with the final code:

1. Built-in SpatialUI components used (names + packages).
2. Custom-component rules applied (token roles + modifiers).
3. Where `PicoTheme` is wrapped.
4. **Design-color mapping** — when a design deliverable exists, restore its
   coordinated theme. List every design token/value (primary/accent + the
   color-matched semantic palette), its `ColorScheme` role, custom brand token,
   or annotated fixed literal, and the `PicoTheme(colorScheme = …)` injection
   point. Confirm that no design color — including custom colors with no matching
   PICO role — silently falls back to the default PICO value.
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
7. **Text foreground audit**: confirm every ordinary-surface `Text` has an
   explicit semantic color and every intentional slot inheritance has a
   `design-style: inherited-content-color <provider>` marker.
8. `verify-design-style.sh` result (must be clean).

## Backlog

Review / update history lives in the repository change history.
Append new dated entries at the top using the template in that file.
