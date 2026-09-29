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

### Role visual reference

The following ARGB values are visual anchors for understanding each role's
approximate lightness, opacity, and hue. SpatialUI versions generally preserve
these visual tendencies. Vibrant can change the final rendered values, but it
resolves roles independently and does not guarantee contrast between an
arbitrarily paired foreground and background. Use these anchors to anticipate
likely conflicts while generating code.

These values are not app tokens or an exact runtime-color contract. Do not
hardcode them into generated UI; continue to use
`PicoTheme.colorScheme.<role>`.

| Role                | Visual anchor | Typical tendency / use                            |
| ------------------- | -------------- | ------------------------------------------------- |
| `labelPrimary`      | `#FF000000`    | primary text and core content                     |
| `labelSecondary`    | `#CC000000`    | secondary text and supporting descriptions        |
| `labelTertiary`     | `#A6000000`    | tertiary text and weaker supporting information   |
| `labelQuaternary`   | `#66000000`    | placeholders, disabled hints, de-emphasized text  |
| `labelPrimaryLight` | `#FFFFFFFF`    | bright foreground on dark or emphasized fills    |
| `fillPrimary`       | `#FF282828`    | important compact fills and primary emphasis      |
| `fillSecondary`     | `#66FFFFFF`    | selected states and secondary emphasis            |
| `fillTertiary`      | `#0A000000`    | low-emphasis peer controls                        |
| `fillLight`         | `#26FFFFFF`    | very light backgrounds and broad content grouping |
| `lightenHover`      | `#66FFFFFF`    | hover lightening layer                            |
| `lightenPressed`    | `#66FFFFFF`    | pressed lightening layer                          |
| `error`             | `#FFFF4D4D`    | error state                                       |
| `alert`             | `#FFFFBF00`    | warning state                                     |
| `passable`          | `#FFB3FF66`    | success / pass state                              |
| `interaction`       | `#FF3377FF`    | links and interactive emphasis                    |
| `dividerLine`       | `#1F000000`    | divider line                                      |

Alpha-bearing fills such as `fillSecondary`, `fillTertiary`, and `fillLight`
must be evaluated after compositing over the actual underlying surface.

```kotlin
Box(
    // Correct when this bounded node owns the accepted dark design surface.
    // design-style: design-surface featured-card
    modifier = Modifier.background(PicoTheme.colorScheme.fillPrimary),
) {
    Text("Hello", color = PicoTheme.colorScheme.labelPrimaryLight)
}

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

> Scope reminder: `fillPrimary / fillSecondary / fillTertiary` may be used by
> the one app-authored surface owner selected for a content path, never by
> every nested group. They are not window-root fills. The window root is
> already glass by default (see `window-background.md`).

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

### Foreground ownership and contrast

`PicoTheme(colorScheme = ...)` provides `LocalColorScheme`, not
`LocalContentColor`. A `Text` whose `color` and `style.color` are both
unspecified reads `LocalContentColor`; outside a component that explicitly
provides it, the value can remain `Color.Unspecified`. SpatialUI components,
however, intentionally provide state-aware content colors to their supported
slots.

```kotlin
// Ordinary app-owned surface: choose a foreground for the actual background.
Text("Reef health", color = PicoTheme.colorScheme.labelPrimary)

// SpatialUI stateful component: keep its paired defaults and inherit the slot
// foreground. Do not add color merely to make the choice explicit.
ToggleableChip(
    isToggleOn = selected,
    onClick = onSelect,
    label = {
        Text("All days")
    },
)

// Custom component colors: configure the pair through one colors API and let
// the slot inherit.
Button(
    onClick = onStart,
    colors = ButtonDefaults.buttonColors(
        containerColor = PicoTheme.colorScheme.interaction,
        contentColor = PicoTheme.colorScheme.labelPrimaryLight,
    ),
) {
    Text("Start")
}
```

For a large custom surface with one foreground role, application code may wrap
the content in
`CompositionLocalProvider(LocalContentColor provides PicoTheme.colorScheme.labelPrimary)`.
There is no blanket requirement that every `Text` spell out `color = ...`.
Instead, keep one clear color owner: the built-in component, its `colors` API,
or the app-owned surface/provider.

For stateful UI, inspect each state's effective pair. A foreground may remain
unchanged when it stays readable across backgrounds. Avoid dark-on-dark,
light-on-light, white on light gray, and white on bright category fills.
`labelPrimaryLight` is not a generic selected-state foreground.

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
| `LocalIndication`        | Indication for `clickable`; `PicoTheme` provides `PicoIndication`, and the concise clickable overload reads it by default                     | `Modifier.clickable(onClick = onClick)`                                                               |
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
Keep that native scheme unchanged for every app, including design-driven
flows. Do not reconstruct or copy it to replace `fill*`, `label*`, interaction,
status, hover/pressed, or divider values.

**Custom colors are explicitly allowed.** Carry each design color through a
named app-owned token in the theme layer, or as an annotated fixed literal
(`Color(0x…) // design-style: fixed-figma-color <source>`), and use it directly
at the intended content call site. Never assign it to a native
`PicoTheme.colorScheme` role and never edit SpatialUI token source.

```kotlin
@Composable
fun ProductTheme(content: @Composable () -> Unit) {
    PicoTheme(content = content)
}

object ProductColors {
    val BrandTeal = Color(0xFF0FB9B1) // design-style: fixed-figma-color brand accent
}
```

App code consumes native semantic colors through `PicoTheme.colorScheme` and
must not import private token objects.

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

- Keep all 16 native roles untouched and consume them through
  `PicoTheme.colorScheme.<role>`.
- Do not construct a replacement `ColorScheme` or call
  `systemColorScheme(...).copy(...)`.
- If a Figma token name resembles a standard role, do not use that reserved
  name for a custom value. Give it an app-specific semantic name instead.
- Preserve every custom design color as a named app-owned token or annotated
  fixed literal. Do not drop it or approximate it with a native role.
- Do not hardcode adaptive hierarchy colors such as gray text values. Use the
  matching `PicoTheme.colorScheme.label*` role or `Color.Vibrant.withVibrant(...)`.
- Do not wrap stock semantic roles again, e.g. avoid
  `PicoTheme.colorScheme.error.withVibrant(Vibrant.None)`; use
  `PicoTheme.colorScheme.error` directly.
- Prefer built-in component color defaults for selection and toggle states.
  Let supported `Text` / `Icon` slots inherit the component content color.
- When custom state colors are required, use one component `colors` API where
  possible and consider the effective foreground and background together.
  Do not independently recolor a child slot after configuring the parent.
- If the design intentionally uses a translucent semantic color such as
  `Color(0xCCDDFF99)`, preserve the alpha with
  `Color(0xCCDDFF99).withVibrant(Vibrant.None)` instead of replacing it with an
  opaque stock role like `PicoTheme.colorScheme.passable`.
- For bright foreground on dark filled surfaces, prefer
  `PicoTheme.colorScheme.labelPrimaryLight` over `Color.White`.
