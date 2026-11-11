# Vibrant

Vibrant is how the SDK asks the PICO OS compositor to draw a color as a material effect that blends with whatever is behind the window, instead of a flat alpha color. It is a spatial-platform feature: the web components cannot reproduce it. This page records what the SDK does, so Compose code can use it correctly and the web preview can be read for what it is.

## What the SDK has

Package `com.pico.spatial.ui.foundation.vibrant` (the `foundation` module).

**`enum class Vibrant`**: `Darkest`, `UltraDark`, `Darker`, `Semidark`, `Dark`, `Neutral`, `Light`, `SemiLight`, `UltraLight`, `LightenPressed`, `None`, `Unspecified`. Internal levels run 1 to 9 for `Darkest` to `UltraLight`, 10 is taken by the hover effect, `LightenPressed` is 11. `None` disables the effect. `Unspecified` means "inherit from the parent". `Vibrant.takeOrElse { }` returns the value unless it is `Unspecified`.

**Two ways to apply it.**
- `Modifier.vibrantEffect(vibrant)` makes the node and everything after it in the chain (children included) render in vibrant mode. The effect is inherited; end it with `Modifier.vibrantEffect(Vibrant.None)`. It does nothing when the platform does not support vibrant or when the value is `Unspecified`. `Modifier.observeCurrentVibrantEffect { }` reads the inherited value (null when none).
- `Color.withVibrant(vibrant)` encodes the level into the color bits. The RGB stays, the color carries the level. `Color.obtainVibrant()` reads it back (`Unspecified` when absent) and `Color.containsVibrant()` tests for it.

**Encoded colors are fragile.** Animation interpolation, gradients, shaders and Android blending destroy the encoded level; the result falls back to the plain color. The level is categorical and cannot be interpolated, so you cannot animate from `Light` to `Dark`. To animate: animate the raw color and apply `.withVibrant()` to each value, or animate with `Modifier.vibrantEffect(vibrant)` on the node (recommended), or use `animateColorVibrantAsState(target)` (spring by default), which keeps the level but only between colors with the **same** level. For gradients, use pure colors and put `Modifier.vibrantEffect` on the component.

**`Color.Vibrant`** (from `com.pico.spatial.ui.graphics`, a module whose source is not part of the design module) is the base color the SDK's own scheme uses: `Color.Vibrant.withVibrant(Vibrant.Darker)`. It is documented as unsupported by `animateColorVibrantAsState`. The Playground emits this form for a vibrant level with no color chosen.

## Where it is switched on

`isSupportVibrant()` is true only when the platform is a spatial platform **and** the app manifest meta-data `com.pico.spatial.ui.isVibrant` is not false (default true). Everything else is the normal Android rendering.

`LocalColorScheme`, and so `PicoTheme { }` and `systemColorScheme(context)`, default to `vibrantColorScheme().adaptVibrantColor { defaultColorScheme() }`: the vibrant scheme when vibrant is supported, `defaultColorScheme()` otherwise. `adaptVibrantColor` simply picks the first value when supported and the lambda's value when not. `defaultColorScheme()` is the flat scheme in `runtime/tokens.css`; the web components are that scheme.

## `vibrantColorScheme()` role mapping

| Role | Vibrant level |
| --- | --- |
| `fillPrimary` | `Darker` |
| `fillSecondary` | `SemiLight` |
| `fillTertiary` | `Neutral` |
| `fillLight` | `Light` |
| `labelPrimary` | `Darkest` |
| `labelSecondary` | `UltraDark` |
| `labelTertiary` | `Semidark` |
| `labelQuaternary` | `Dark` |
| `lightenHover` | `SemiLight` |
| `lightenPressed` | `LightenPressed` |
| `labelPrimaryLight`, `dividerLine` | the flat white / black 12% color with `Vibrant.None` (opted out) |
| `error`, `alert`, `passable`, `interaction` | flat Display P3 colors, no vibrant |

## Opt-outs inside the SDK

- `ScrollIndicator` takes its default colors from `defaultColorScheme()`, not `PicoTheme.colorScheme`, so it never carries vibrant encoding.
- `Switch` does not animate its track color, by design, because its roles are vibrant.
- `CircularProgressIndicator` applies `Modifier.vibrantEffect(color.obtainVibrant())` to its canvas, so a vibrant progress color works.

## Web Preview limitations

The bundled components draw flat colors from [runtime/tokens.css](runtime/tokens.css), using the SDK's non-vibrant fallback. CSS transparency and backdrop blur do not reproduce the compositor's scene-dependent blend. Judge layout, content and component states here; verify vibrant appearance and material against the target scene on device.

When a design intentionally specifies a vibrant role or level, preserve that choice in its handoff even though the browser shows only the fallback. Do not sample a preview screenshot to invent a new native color. Status colors and artwork keep their own meaning; see [general rules](general-rules.md#backgrounds-and-colors).
