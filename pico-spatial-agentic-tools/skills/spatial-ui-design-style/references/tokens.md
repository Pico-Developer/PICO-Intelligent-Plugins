# Tokens Reference — Color / Typography / Motion / Locals

Application-side entry points only. Library-private tokens
(`DimensionTokens`, `ColorTokens`, ...) are `@RestrictTo(LIBRARY)` and **must
not** be imported from app code.

## 1. Color Roles (`PicoTheme.colorScheme.*`, 16 roles)

- Fill: `fillPrimary` / `fillSecondary` / `fillTertiary` / `fillLight`
- Text/icon foreground: `labelPrimary` / `labelPrimaryLight` / `labelSecondary`
  / `labelTertiary` / `labelQuaternary`
- State layers: `lightenHover` / `lightenPressed`
- Semantic colors: `error` / `alert` / `passable` / `interaction`
- Divider: `dividerLine`

```kotlin
// ✅ Correct — for business cards / inner containers
Box(Modifier.background(PicoTheme.colorScheme.fillPrimary))
Text("Hello", color = PicoTheme.colorScheme.labelPrimary)

// ❌ Wrong — hardcoded color
Box(Modifier.background(Color(0xFF1A1A1A)))

// ❌ Wrong — fillPrimary on the WINDOW ROOT while the system glass is still
//          on. For DefaultWindowContainer the switch is the launcher
//          <activity> manifest meta-data
//          `pico.spatial.windowcontainer.materialbackground` (default "1");
//          for WindowContainer(...) / Augment(...) it is the DSL parameter
//          `enableMaterialBackground` (default true). A solid color over
//          the glass kills both the glass and vibrant linkage. See
//          references/window-background.md.
```

> Scope reminder: `fillPrimary / fillSecondary / fillTertiary` are intended for
> business cards and inner containers, not the window root. The window root
> is already glass by default (see `window-background.md`).

## 2. Typography Roles (`PicoTheme.typography.*`)

- display: `displayLarge / Medium / Small`
- headline: `headlineLarge / Medium / Small`
- title: `titleLarge / Medium / Small`
- body: `bodyLarge / bodyMedium / bodySmall`
- label: `labelLarge / Medium / Small`

> Some SDK versions also expose multi-line / tiny variants (e.g.
> `bodyLargeMultiline`, `bodyMediumMultiline`, `bodyTiny`). Check IDE
> auto-complete on the current SDK before relying on them; the 15
> roles above are the always-present subset.

```kotlin
Text(
    "Title",
    style = PicoTheme.typography.titleMedium,
    color = PicoTheme.colorScheme.labelPrimary,
)
```

### Text foregrounds are not CSS-inherited

`PicoTheme(colorScheme = ...)` provides `LocalColorScheme`, not
`LocalContentColor`. A `Text` whose `color` and `style.color` are both
unspecified reads `LocalContentColor`; outside a component that explicitly
provides it, the value remains `Color.Unspecified` and can render black. This is
especially visible on dark glass.

```kotlin
// ✅ Ordinary Box / Row / Column surface: resolve the foreground explicitly.
Text("Reef health", color = PicoTheme.colorScheme.labelPrimary)

// ✅ Direct SpatialUI component slot: inherit the component's state-aware
// content color and make that decision auditable.
Button(
    onClick = onStart,
    colors = ButtonDefaults.buttonColors(
        containerColor = PicoTheme.colorScheme.interaction,
        contentColor = PicoTheme.colorScheme.labelPrimaryLight,
    ),
) {
    // design-style: inherited-content-color Button
    Text("Start")
}

// ❌ Wrong on an ordinary dark surface: PicoTheme alone does not provide
// LocalContentColor.
Text("Reef health", style = PicoTheme.typography.titleMedium)
```

For a large custom surface with one foreground role, application code may wrap
the content in
`CompositionLocalProvider(LocalContentColor provides PicoTheme.colorScheme.labelPrimary)`.
Still mark each inherited `Text` with
`// design-style: inherited-content-color <provider>` so the verifier can
distinguish deliberate inheritance from an accidental missing color.

## 3. Sizes / Spacing

- Use `Modifier.padding(16.dp)` etc. directly with business constants.
- Prefer component-provided defaults: `ButtonDefaults.Regular`, `ChipsDefaults.Small`, ...
- **Do not** import `DimensionTokens` (library-private).

## 4. Motion

`MotionTokens.*` is exposed as an `object` but should still be a last resort.
Prefer built-in components, `tween`, or `spring` first. When you explicitly
want design-system timing/easing:

- `MotionTokens.bezierEasingStandard / Decelerate / Accelerate`
- `MotionTokens.springEasingGradual.toSpring()`
- `MotionTokens.durationShort1..3`

## 5. CompositionLocals (Application-Side)

| Local                    | Purpose                                                                                                                                      | Example                                                                                               |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `LocalContentColor`      | Current content color; `Text` and `Icon` read it by default                                                                                  | `CompositionLocalProvider(LocalContentColor provides PicoTheme.colorScheme.labelPrimary) { ... }`     |
| `LocalDisableAlpha`      | Disabled alpha (default `0.3f`)                                                                                                              | `Modifier.alpha(if (enabled) 1f else LocalDisableAlpha.current)`                                      |
| `LocalIndication`        | Indication for `clickable`; `PicoTheme` already provides `PicoIndication`                                                                    | `Modifier.clickable(interactionSource = ..., indication = LocalIndication.current) {}`                |
| `LocalAudioEffectPlayer` | System audio-effect player (mainly for custom toggle audio); name and package vary by SDK version — verify with IDE auto-complete before use | `LocalAudioEffectPlayer.current.playSystem(SpatialSoundEffect.StateOn)` (subject to SDK confirmation) |

> `ProvideContentColor` is internal. From app code use
> `CompositionLocalProvider(LocalContentColor provides ...)`.

## 6. Package Lookup

| Topic                    | Package / Key Types                                                                                                                                                                                                                                   |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Theme entry              | `com.pico.spatial.ui.design.PicoTheme`, `ColorScheme`, `Typography`, `systemColorScheme(Context)`                                                                                                                                                     |
| Composition Locals       | `com.pico.spatial.ui.design.LocalContentColor`, `LocalDisableAlpha`; Compose `LocalIndication`; `com.pico.spatial.ui.platform.LocalAudioEffectPlayer`                                                                                                 |
| Built-in components      | `com.pico.spatial.ui.design.*`                                                                                                                                                                                                                        |
| Windows / overlays       | `com.pico.spatial.ui.design.windows.*`                                                                                                                                                                                                                |
| Menus                    | `com.pico.spatial.ui.design.menu.*`                                                                                                                                                                                                                   |
| Hover effects            | `com.pico.spatial.ui.foundation.hover.*`                                                                                                                                                                                                              |
| Haptics                  | `com.pico.spatial.ui.foundation.haptic.*`                                                                                                                                                                                                             |
| App DSL                  | `com.pico.spatial.ui.foundation.dsl.*`                                                                                                                                                                                                                |
| 3D content               | `com.pico.spatial.ui.foundation.content.*`                                                                                                                                                                                                            |
| 3D modifiers / geometry  | `com.pico.spatial.ui.foundation.layout.*` (depth, padding3D, alignDepth, Box3D, layout3D); `com.pico.spatial.ui.foundation.geometry.*` (DpOffset3D, IntOffset3D, Rotation3D, Scale3D, NormalizedPoint3D)                                              |
| Vibrant / materials      | `com.pico.spatial.ui.foundation.vibrant.*` (vibrantEffect, withVibrant, animateColorVibrantAsState); `com.pico.spatial.ui.foundation.material.backgroundMaterial`; `com.pico.spatial.ui.platform.Material` (None / Regular / Thick / Thickest / Thin) |
| Window-attached ornament | `com.pico.spatial.ui.foundation.window.Augment` (NOT in `design.windows.*`)                                                                                                                                                                           |
| Spatial gestures         | `com.pico.spatial.ui.foundation.gesture.*`                                                                                                                                                                                                            |

## 7. Color-Scheme Mechanics and Decision Rules

`PicoTheme { ... }` defaults to `systemColorScheme(LocalContext.current)`.
That default is valid only when there is no design product to restore. **The
goal is to reproduce the final design deliverable's coordinated theme** — its
primary/accent color together with the semantic palette that was color-matched
to it. When Figma, a screenshot/design package, or the design colors the caller
passes to `verify-design-style.sh --design-color` provide that theme, the app
MUST derive a complete custom scheme from `systemColorScheme(...)`, explicitly
assign all 16 public roles, override matching roles with exact design values,
and inject it through `PicoTheme(colorScheme = ...)`. Roles that remain
adaptive are still written explicitly as `role = system.role`.
Using the stock semantic roles without overriding their values makes the app
wear the default PICO palette and is a hard fidelity failure.

**Custom colors are explicitly allowed** — the design's palette wins over the
default PICO look. Any color the design uses must survive into the running app,
including colors that have no matching PICO role:

- A design value that maps to one of the 16 roles → override that role.
- A brand/decorative value with no matching role → carry it verbatim through a
  named brand token in the theme/token layer, or as an annotated fixed literal
  (`Color(0x…) // design-style: fixed-figma-color <source>`).
- Never snap a custom design color to "the nearest" default role — that loses
  the design identity and MUST fail review.

```kotlin
@Composable
fun ProductTheme(content: @Composable () -> Unit) {
    val system = systemColorScheme(LocalContext.current)
    val designColors =
        system.copy(
            fillPrimary = system.fillPrimary,
            fillSecondary = system.fillSecondary,
            fillTertiary = system.fillTertiary,
            fillLight = system.fillLight,
            labelPrimaryLight = system.labelPrimaryLight,
            labelPrimary = system.labelPrimary,
            labelSecondary = system.labelSecondary,
            labelTertiary = system.labelTertiary,
            labelQuaternary = system.labelQuaternary,
            lightenHover = system.lightenHover,
            lightenPressed = system.lightenPressed,
            error = system.error,
            interaction = Color(0xFFFF6B4A), // design-style: fixed-figma-color primary action
            passable = Color(0xFF89E0B0), // design-style: fixed-figma-color completion
            alert = Color(0xFFFFD166), // design-style: fixed-figma-color warning
            dividerLine = system.dividerLine,
        )
    PicoTheme(colorScheme = designColors, content = content)
}

// Custom brand color with no matching role: keep it as a named token so the
// design value is preserved verbatim and reused across the app.
val BrandTeal = Color(0xFF0FB9B1) // design-style: fixed-figma-color brand accent
```

Keep adaptive grayscale `fill*` / `label*` values from the system scheme unless
the design contract explicitly classifies a value as fixed, but forward each
one visibly in the complete copy. App code should still consume the result
through `PicoTheme.colorScheme` and must not import private token objects.

### Two color families

- **Adaptive grayscale hierarchy roles** (`label*`, `fill*`, `lightenHover`,
  `lightenPressed`) are already mapped to Vibrant levels by the SDK. Example
  equivalences: `labelPrimary` behaves like `Vibrant.Darkest`; `fillPrimary`
  behaves like a `Darker`-style fill; `fillTertiary` behaves like `Neutral`.
- **Fixed semantic colored roles** (`error`, `alert`, `passable`,
  `interaction`, `dividerLine`, and `labelPrimaryLight`) are SDK-side pure
  semantic colors and should be treated as already protected from unwanted
  Vibrant blending.

### Generation rules

- Treat the design deliverable's coordinated theme (primary/accent + the
  color-matched semantic palette) as required inputs, not optional suggestions.
  Every value must appear in the custom theme mapping or an explicitly
  documented custom brand token.
- A design-driven flow must contain an explicit
  `PicoTheme(colorScheme = ...)` call and a complete assignment of all 16
  `ColorScheme` roles. A wrapper that delegates to plain `PicoTheme {}` or a
  partial `.copy(...)` is non-compliant.
- If a Figma token name is a standard role (`Label Primary`, `Fill Tertiary`,
  `Error`, `Divider Line`), map the token name to `PicoTheme.colorScheme.xxx`
  and override that role with the design's exact value.
- Custom colors are allowed and expected for fidelity: a design value that has
  no matching PICO role (a brand hue, a decorative accent) must still be carried
  verbatim through a named brand token or an annotated fixed literal. Do not
  drop it and do not approximate it with the nearest default role.
- Do not hardcode adaptive hierarchy colors such as gray text values. Use the
  matching `PicoTheme.colorScheme.label*` role or `Color.Vibrant.withVibrant(...)`.
- Do not wrap stock semantic roles again, e.g. avoid
  `PicoTheme.colorScheme.error.withVibrant(Vibrant.None)`; use
  `PicoTheme.colorScheme.error` directly.
- If the design intentionally uses a translucent semantic color such as
  `Color(0xCCDDFF99)`, preserve the alpha with
  `Color(0xCCDDFF99).withVibrant(Vibrant.None)` instead of replacing it with an
  opaque stock role like `PicoTheme.colorScheme.passable`.
- For bright foreground on dark filled surfaces, prefer
  `PicoTheme.colorScheme.labelPrimaryLight` over `Color.White`.
