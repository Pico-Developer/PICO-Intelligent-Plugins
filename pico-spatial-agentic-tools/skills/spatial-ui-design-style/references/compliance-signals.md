# Compliance Signals (Machine-Readable Rules)

Each rule below maps the four highest-priority constraints and migrated
SpatialUI D2C checklist items into grep-able patterns. Used by `../scripts/verify-design-style.sh`, the upstream
`d2c_verify_code` `ruleContext`, evals, and CI hooks.

> Scope: application source trees only — typically
> `**/src/main/java/**/*.kt`, `**/src/main/kotlin/**/*.kt`.
> Generated assets (`*/res/**`, `*/build/**`, `*/generated/**`) are exempt.

## R1 — PicoTheme wrapping (REQUIRED)

| Type            | Pattern                                                    | Rule                                   |
| --------------- | ---------------------------------------------------------- | -------------------------------------- |
| MUST appear     | `PicoTheme(`                                               | At least one occurrence in app sources |
| MUST NOT appear | `MaterialTheme(...)` / `MaterialTheme { ... }` (including fully qualified calls) | Material theme leakage; whitespace and line breaks before the call delimiter are covered; comments and literals are ignored |
| MUST NOT appear | `MaterialTheme\.colorScheme` / `MaterialTheme\.typography` | Use `PicoTheme.*`                      |

### R1b — Preserve native `ColorScheme`; isolate custom colors

When the caller declares authoritative design colors — via
`verify-design-style.sh --design-color <token>=<#hex>` (repeatable), or via
`facts.visual_tokens.theme_overrides[]` / `facts.visual_tokens.semantic_colors[]`
in a legacy `.scratch/evidence_packet.json` — the following become hard gates:

| Type            | Pattern / evidence                                                 | Rule                                                                                         |
| --------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| MUST NOT appear | `PicoTheme(colorScheme = ...)`, `ColorScheme(...)`, or `systemColorScheme(...).copy(...)` | Native SpatialUI roles, including `fill*`, must not be redefined |
| MUST NOT appear | A `--design-color` whose token name is a native `ColorScheme` role | Custom colors need app-owned names and cannot masquerade as overrides                         |
| MUST appear     | Every exact custom design hex as a Kotlin color literal            | No declared app-owned color may be dropped                                                    |
| Allowed         | Plain `PicoTheme { ... }` and `PicoTheme.colorScheme.<role>`       | Built-in components retain the unchanged system Vibrant palette                               |
| Allowed         | Named app token with `fixed-figma-color` evidence                  | Custom brand/decorative colors remain available without mutating the framework color contract |

The verifier normalizes six-digit design values such as `#FF6B4A` to Kotlin
ARGB form `0xFFFF6B4A`. Custom brand slots still require the exact value to be
present in the theme/token layer even when they are not native `ColorScheme`
properties.

The caller passes only app-owned custom colors. Native role names such as
`fillPrimary`, `labelPrimary`, `interaction`, and `error` are reserved and
rejected as custom token names. Convert CSS `rgba(...)` values to `#AARRGGBB`.

## R2 — Built-in design components first (RECOMMENDED, soft check)

| Type          | Pattern                                   | Rule                                                                                 |
| ------------- | ----------------------------------------- | ------------------------------------------------------------------------------------ |
| Should appear | `import com\.pico\.spatial\.ui\.design\.` | At least one design import per UI module                                             |
| Inspect       | `@Composable\s+fun\s+My[A-Z]\w*Button`    | Custom `*Button` re-implementation — review whether built-in `Button` was considered |

## R3 — Custom hover MUST use `spatialHoverEffect`

| Type      | Pattern                                     | Rule                                                                          |
| --------- | ------------------------------------------- | ----------------------------------------------------------------------------- |
| Allowed   | `Modifier\.spatialHoverEffect`              | Highest-priority hover API                                                    |
| Forbidden | `\.hoverable[ \t]*\(`                       | Reimplemented hover, including chained `Modifier.padding(...).hoverable(...)` |
| Forbidden | `animateFloatAsState\([^)]*scale[^)]*hover` | Custom hover scale animation                                                  |

## R4 — Window / container root background: respect the system glass

**Default rule**: every PICO window container ships with `Material.Regular`
glass on by default. The application MUST NOT paint a solid color or
another material on top.

**On/off switch differs by container kind**:

- `DefaultWindowContainer` → per-Activity manifest meta-data
  `pico.spatial.windowcontainer.materialbackground` (default `"1"`).
  No DSL knob.
- `WindowContainer(...)` / `Augment(...)` → DSL parameter
  `enableMaterialBackground: Boolean = true`. Manifest meta-data does
  NOT apply.

**Switching glass style or going opaque** requires first flipping the
**right** switch off — manifest `"0"` for `DefaultWindowContainer`, or
`enableMaterialBackground = false` in the DSL call for
`WindowContainer(...)` / `Augment(...)`. Then either call
`Modifier.backgroundMaterial(enable = true, style = Material.<Style>)` for
a new glass style, or annotate the root with `// design-style: opaque-root`
and use `Modifier.background(PicoTheme.colorScheme.<role>)`.

Scope: outermost `Box` inside `DefaultWindowContainer { ... }`,
`WindowContainer(...) { ... }`, `Subwindow { ... }`, `Stage { ... }`, or
`Augment(...) { ... }`.

| Type                                                          | Pattern                                                                                                                                                               | Rule                                                                                                                                                                                                  |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Forbidden (reviewer-only — semantic)                          | `Modifier\.background\(\s*PicoTheme\.colorScheme\.` directly inside the root `Box` of a window container, **without** a nearby `// design-style: opaque-root` comment | Painting solid color over the system glass. **Note**: this rule needs context-aware scope (root Box vs. inner card). The shell verifier does not run this grep — it is delegated to the reviewer LLM. |
| Forbidden                                                     | `backgroundMaterial\([^)]*\)[ \t\r\n.]*background\(` (multi-line)                                                                                                     | Stacking glass + solid color                                                                                                                                                                          |
| Forbidden                                                     | `\.background[ \t]*\([ \t]*Color\(0x`                                                                                                                                 | Hardcoded color literal as background, including chained `.background(Color(...))`                                                                                                                    |
| Allowed exception                                             | `// design-style: opaque-root` immediately above a root `Modifier.background(PicoTheme.colorScheme.<role>)`                                                           | Documented opt-out (must pair with the right off-switch)                                                                                                                                              |
| Allowed                                                       | `Modifier\.backgroundMaterial\(enable\s*=\s*true,\s*style\s*=\s*Material\.` on the root                                                                               | Custom glass style (must pair with the right off-switch)                                                                                                                                              |
| Info reminder (`DefaultWindowContainer` scope)                | Custom glass / opaque-root override                                                                                                                                   | Reviewer should confirm `pico.spatial.windowcontainer.materialbackground="0"` exists in the launcher `<activity>` of the matching `AndroidManifest.xml`                                               |
| Info reminder (`WindowContainer(...)` / `Augment(...)` scope) | Custom glass / opaque-root override                                                                                                                                   | Reviewer should confirm the same `WindowContainer(...)` / `Augment(...)` call passes `enableMaterialBackground = false`                                                                               |
| Forbidden                                                     | A `WindowContainer(..., enableMaterialBackground = true) { Box(Modifier....background(<role>)) }` chain                                                               | DSL switch left at `true` while painting a solid color on the root                                                                                                                                    |

### R4b — View-level material shape

`backgroundMaterial(...)` receives no shape parameter. Every rounded view-level
material modifier chain must call `.clip(shape)` before
`.backgroundMaterial(...)`; a later border is neither required nor a substitute
for clipping.

| Type              | Pattern / evidence                                                                   | Rule                                                          |
| ----------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| Required          | `.clip(<shape>)` occurs before `.backgroundMaterial(...)` in the same modifier chain | Material pixels and hover bounds use the intended shape       |
| Forbidden         | `.backgroundMaterial(...)` with no earlier `.clip(...)`                              | Material remains rectangular                                  |
| Allowed exception | `// design-style: rectangular-material <reason>`                                     | The design explicitly requires a rectangular material surface |

## R5 — Theme-role routing (no hardcoded color / typography)

For Figma / screenshot-driven generation, 1:1 visual restoration has priority
for **explicit fixed decorative colors** that are not semantic theme roles. When
the XML / screenshot provides a distinctive literal color (for example a
translucent promotion chip, rating star, brand swatch, or artwork placeholder),
preserve it as a fixed color and annotate the same line:

```kotlin
.background(Color(0xCC99FFFF)) // design-style: fixed-figma-color discount chip
```

This exception is only for non-root decorative or brand/fidelity surfaces. It
does **not** allow painting a fixed color over the root window glass, nor does
it apply to grayscale text/fill roles that have named PICO tokens.

| Type              | Pattern                                                                                         | Rule                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Forbidden         | `Color\(0x[0-9A-Fa-f]{6,8}\)` without `// design-style: fixed-figma-color ...` on the same line | Hardcoded color                                                          |
| Allowed exception | `Color(0x...) // design-style: fixed-figma-color <source>`                                      | Explicit Figma / screenshot fixed color for non-root decorative fidelity |
| Forbidden         | `TextStyle\(fontSize\s*=`                                                                       | Hardcoded typography                                                     |
| Forbidden         | `\.alpha[ \t]*\([ \t]*0\.3f[ \t]*\)`                                                            | Hardcoded disabled alpha — use `LocalDisableAlpha.current`               |

## R6 — Indication & optional haptics

R6 is guidance, not a verifier admission check. The concise `clickable`
overload reads `LocalIndication.current` by default, and
`controllerHapticFeedback` is optional.

| Type    | Pattern                                                                                                                                        | Rule                                                                                      |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Inspect | `indication\s*=\s*null` on an ordinary click action                                                                                            | Prefer the default indication unless custom state audio or another explicit behavior needs it |
| Inspect | two distinct `remember { MutableInteractionSource() }` in same Composable, one feeding `clickable`, another feeding `controllerHapticFeedback` | When optional haptics are used, share the clickable's interaction source                  |

## R7 — Library-private tokens MUST NOT be imported

| Type      | Pattern                                                                           | Rule                   |
| --------- | --------------------------------------------------------------------------------- | ---------------------- |
| Forbidden | `import com\.pico\.spatial\.ui\.design\.tokens\.` (DimensionTokens / ColorTokens) | `@RestrictTo(LIBRARY)` |

## R8 — Migrated SpatialUI checklist heuristics

These checks come from the migrated SpatialUI D2C checklist. They are
intentionally best-effort grep signals; semantic cases still need reviewer
judgement.

| Type      | Pattern                                                                              | Rule                                                                     |
| --------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| Forbidden | `androidx.compose.material` / `androidx.compose.material3` imports or fully qualified references | Material and Material3 themes, components, and other package members are forbidden; comments and literals are ignored |
| Forbidden | `import com\.pico\.spatial\.ui\.design\.AlertDialog`                                 | `AlertDialog` lives in `design.windows`                                  |
| Inspect   | `collectAsState\(\)`                                                                 | Prefer `collectAsStateWithLifecycle()` for ViewModel state               |
| Inspect   | `key = { index }` / `key = { it.hashCode() }`                                        | Lazy keys should use stable item IDs                                     |
| Inspect   | `remember { mutableStateOf(true                                                      | false) }`                                                                | Visibility state for popup/dialog/menu/subwindow should usually be `rememberSaveable` |
| Forbidden | `.padding(horizontal = ..., bottom                                                   | top                                                                      | start                                                                                 | end = ...)`  | Invalid Compose padding overload; use explicit sides                         |
| Forbidden | `PicoTheme.colorScheme.(accent                                                       | primary                                                                  | secondary                                                                             | background   | surface                                                                      | onSurface | onPrimary)` | Guessed Material-style role; use PicoTheme roles or Vibrant |
| Inspect   | `.background(..., shape).clickable`                                                  | Prefer `clip(shape).spatialHoverEffect().clickable().background()`       |
| Inspect   | `.clickable(...)...spatialHoverEffect(` / `.clickable { ... }...spatialHoverEffect(` | Hover should precede clickable                                           |
| Inspect   | `.background(...).fillMaxWidth                                                       | size                                                                     | height                                                                                | width`       | Put layout before decoration                                                 |
| Inspect   | `modifier.fillMaxWidth                                                               | size                                                                     | height                                                                                | width`       | Ensure caller override is not blocked; consider defaults + `.then(modifier)` |
| Inspect   | large directional `padding(start                                                     | bottom                                                                   | end                                                                                   | top = N.dp)` | Confirm this is not manual TabBar / Toolbar avoidance                        |
| Inspect   | `Text("✕"                                                                            | "×"                                                                      | "x"                                                                                   | "X")`        | Prefer `IconButton` + vector icon for close actions                          |
| Inspect   | placeholder image URLs                                                               | Bind data from `uiState` / repository rather than hardcoded placeholders |

## R10 — Content surface discipline

Structural `layout` and `domain_visual` regions are transparent. App-authored
borders are forbidden on content containers. When a design spec is supplied,
app-authored material is also forbidden, and every app-authored background or
content `Card` must map exactly once to a bounded content node whose
`appearance` declares a fill.

| Type      | Pattern / evidence                                                                                          | Rule                                                              |
| --------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Forbidden | `.border(...)` or `BorderStroke(...)` in app Kotlin source                                                  | Do not separate content with app-authored borders                 |
| Forbidden | `.backgroundMaterial(...)` when `--design-spec` is supplied                                                 | Material is not part of the design or restoration contract       |
| Required  | `// design-style: design-surface <node-id>` immediately before an app surface call                          | Makes every generated background traceable to the accepted design |
| Forbidden | A surface marker naming a node without `appearance.fill`                                                    | Code added a surface that the design did not declare              |
| Forbidden | One surface node ID used by multiple background calls                                                       | One design fill was expanded into multiple implementation surfaces |
| Forbidden | `.background(...)` or content `Card(...)` without a valid marker when `--design-spec` is supplied           | Code added an untraceable surface                                 |

Library implementation sources are outside the verifier scope, so borders and
focus indicators owned internally by standard SpatialUI controls are not
reported.

## Severity

| Severity  | Meaning                   | Example                                                                                                                 |
| --------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `error`   | Hard violation — must fix | R1 missing PicoTheme; R1b native color role override or missing custom color; R3 hoverable; R4 stacking; R5 hardcoded color; R10 content border |
| `warning` | Likely violation — review | R2 custom Button                                                                                                        |
| `info`    | Stylistic — recommended   | R2 missing design import in a UI-only module                                                                            |

## Suggested Reviewer Prompt Fragment

```
You are reviewing PICO Spatial UI Compose code for compliance with the
spatial-ui-design-style skill. Apply the highest-priority rules:
1. PicoTheme wraps the entry tree (R1). Keep its native ColorScheme unchanged:
   do not construct `ColorScheme(...)` or call
   `systemColorScheme(...).copy(...)`. Custom colors are allowed only as named
   app-owned tokens or annotated fixed literals and must not replace `fill*`,
   `label*`, interaction, status, hover/pressed, or divider roles (R1b).
2. Prefer com.pico.spatial.ui.design.* built-ins; custom only when no built-in fits (R2).
3. Custom hover MUST use Modifier.spatialHoverEffect — never `hoverable + scale` (R3).
4. Window / container root background: every PICO window container ships with
   `Material.Regular` glass on by default. The application MUST NOT paint a
   solid color or another material on top. The on/off switch differs by
   container: `DefaultWindowContainer` → per-Activity manifest meta-data
   `pico.spatial.windowcontainer.materialbackground` (default "1", no DSL knob);
   `WindowContainer(...)` / `Augment(...)` → DSL parameter
   `enableMaterialBackground: Boolean = true`. To switch glass style or go
   opaque, the right switch MUST be flipped off first; then either
   Modifier.backgroundMaterial(enable=true, style=Material.<Style>) for a
   different glass, or `// design-style: opaque-root` + Modifier.background(<role>)
   for an opaque root. Stacking backgroundMaterial(...) + .background(...) on
   the same chain is forbidden (R4).
Also flag: hardcoded colors / typography (R5), DimensionTokens imports (R7),
and migrated D2C checklist regressions such as Material3 component imports,
invalid padding overloads, unstable lazy keys, manual close glyphs, hardcoded
placeholder image URLs, and suspicious modifier ordering (R8). Treat haptics
as optional; when present, confirm they share the clickable interaction source
(R6). Do not require every `Text` to spell out a color. Prefer component-owned
state colors and slot inheritance; when code customizes state colors, consider
the effective foreground and background together and avoid obvious
dark-on-dark, light-on-light, or white-on-light combinations. Keep structural
`layout` and `domain_visual` regions transparent, reject app-authored content
borders, and require every app surface to map exactly once to a surface-owning
design node when `design-spec.json` exists (R10). Cite specific file:line.
```
