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
| MUST NOT appear | `MaterialTheme(`                                           | Material theme leakage                 |
| MUST NOT appear | `MaterialTheme\.colorScheme` / `MaterialTheme\.typography` | Use `PicoTheme.*`                      |

### R1b — Design colors MUST drive `PicoTheme` (REQUIRED when design evidence exists)

When the caller declares authoritative design colors — via
`verify-design-style.sh --design-color <slot>=<#hex>` (repeatable), or via
`facts.visual_tokens.theme_overrides[]` / `facts.visual_tokens.semantic_colors[]`
in a legacy `.scratch/evidence_packet.json` — the following become hard gates:

| Type                                         | Pattern / evidence                                                                                        | Rule                                                                                                                              |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| MUST appear                                  | `PicoTheme(... colorScheme = ...)`                                                                        | A design-driven app must inject a custom scheme; plain `PicoTheme {}` is not sufficient                                           |
| MUST appear                                  | Explicit assignments for all 16 public `ColorScheme` roles in the custom scheme                           | The final system color scheme must be complete; omitted copy parameters are not accepted                                          |
| MUST appear                                  | Every exact design hex as a Kotlin color literal in app source                                            | No declared brand/accent/semantic value may silently fall back to the stock PICO palette                                          |
| MUST appear for declared `ColorScheme` slots | Exact `<slot> = Color(<design value>)`, directly or through a named token, for any of the 16 public roles | The declared design value must override its matching `ColorScheme` role; placing the same HEX elsewhere does not satisfy the rule |
| Allowed                                      | Adaptive roles explicitly assigned as `<role> = system.<role>`                                            | Preserve system Vibrant behavior while keeping the complete theme contract visible                                                |

The verifier normalizes six-digit design values such as `#FF6B4A` to Kotlin
ARGB form `0xFFFF6B4A`. Custom brand slots still require the exact value to be
present in the theme/token layer even when they are not native `ColorScheme`
properties.

The caller must pass the complete app-owned color inventory. This includes
surface/fill colors, primary and secondary text, divider/border colors, semantic
states, and custom brand/decorative colors. Passing only prominent brand colors
is not a valid R1b invocation. Convert CSS `rgba(...)` tokens to `#AARRGGBB`.
Explicitly documented environment-only simulation colors are not app-owned.
Completeness is checked whenever authoritative design colors are supplied. The
16 required role names are `fillPrimary`, `fillSecondary`, `fillTertiary`,
`fillLight`, `labelPrimaryLight`, `labelPrimary`, `labelSecondary`,
`labelTertiary`, `labelQuaternary`, `lightenHover`, `lightenPressed`, `error`,
`alert`, `passable`, `interaction`, and `dividerLine`.

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

`backgroundMaterial(...)` receives no shape parameter and does not inherit the
shape from a later `border`. Every view-level material modifier chain must call
`.clip(shape)` before `.backgroundMaterial(...)`.

| Type              | Pattern / evidence                                                                   | Rule                                                                                |
| ----------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| Required          | `.clip(<shape>)` occurs before `.backgroundMaterial(...)` in the same modifier chain | Material pixels, hover bounds, and border use the intended shape                    |
| Required          | One shared shape value for `.clip(shape)` and `.border(..., shape)`                  | Prevent radius drift between material and border                                    |
| Forbidden         | `.backgroundMaterial(...)` with no earlier `.clip(...)`                              | Material remains rectangular, even if a later border uses `RoundedCornerShape(...)` |
| Allowed exception | `// design-style: rectangular-material <reason>`                                     | The design explicitly requires a rectangular material surface                       |

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

## R6 — Indication & haptics shared interactionSource

| Type                                                                                       | Pattern                                                                                                                                        | Rule                                                                          |
| ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Required when custom `.clickable(...)` or `.clickable { ... }` exists                      | `indication\s*=\s*LocalIndication\.current`                                                                                                    | PicoIndication routing                                                        |
| MUST appear in the same file when custom `.clickable(...)` or `.clickable { ... }` is used | `controllerHapticFeedback`                                                                                                                     | SpatialUI haptic routing; must share the clickable `MutableInteractionSource` |
| Inspect                                                                                    | two distinct `remember { MutableInteractionSource() }` in same Composable, one feeding `clickable`, another feeding `controllerHapticFeedback` | Likely desync — should share one source                                       |

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
| Forbidden | `import\s+androidx\.compose\.material3(\.                                            | $)`                                                                      | Material3 package import; prefer SpatialUI design built-ins                           |
| Forbidden | `import\s+androidx\.compose\.material(\.                                             | $)`                                                                      | Material v1 package import; prefer SpatialUI design built-ins                         |
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

## R9 — Resolved text foregrounds

`PicoTheme` provides the active `ColorScheme`, but it does not provide
`LocalContentColor`. Unlike CSS, a foreground color is not inherited from an
ordinary parent `Box`, `Row`, or `Column`.

| Type      | Signal                                                                                   | Rule                                                                                                                      |
| --------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Forbidden | App-authored `Text(...)` with neither a `color = ...` argument nor an inheritance marker | Text can reach `BasicText` with `Color.Unspecified` and render black on dark glass                                        |
| Required  | `color = PicoTheme.colorScheme.label*` or another intentional semantic state role        | Ordinary-surface text resolves its foreground explicitly                                                                  |
| Exception | `// design-style: inherited-content-color <provider>` immediately before or on the call  | The direct SpatialUI component slot or explicit `LocalContentColor` provider supplies a deliberate state-aware foreground |

The exception must name the provider, for example `Button`, `ButtonChip`,
`SegmentItem`, `AlertDialog`, or `CompositionLocalProvider`. It is not a blanket
file-level opt-out.

## Severity

| Severity  | Meaning                   | Example                                                                                             |
| --------- | ------------------------- | --------------------------------------------------------------------------------------------------- |
| `error`   | Hard violation — must fix | R1 missing PicoTheme; R1b design colors not injected; R3 hoverable; R4 stacking; R5 hardcoded color |
| `warning` | Likely violation — review | R2 custom Button; R6 split interactionSource                                                        |
| `info`    | Stylistic — recommended   | R2 missing design import in a UI-only module                                                        |

## Suggested Reviewer Prompt Fragment

```
You are reviewing PICO Spatial UI Compose code for compliance with the
spatial-ui-design-style skill. Apply the four highest-priority rules:
1. PicoTheme wraps the entry tree (R1). When a design deliverable exists, the
   app restores its coordinated theme: it builds a custom ColorScheme from the
   design's exact primary/accent + color-matched semantic values and injects it
   with PicoTheme(colorScheme = ...). Custom colors are explicitly allowed — a
   design value with no matching PICO role must be carried verbatim (named brand
   token or annotated fixed literal), never approximated with the nearest role.
   Plain PicoTheme {} or stock semantic values are a hard failure (R1b).
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
Also flag: hardcoded colors / typography (R5), missing LocalIndication (R6),
DimensionTokens imports (R7), and migrated D2C checklist regressions such as
Material3 component imports, invalid padding overloads, unstable lazy keys,
manual close glyphs, hardcoded placeholder image URLs, and suspicious modifier
ordering (R8). Require every Text foreground to resolve explicitly, or carry a
nearby `design-style: inherited-content-color <provider>` marker for a verified
SpatialUI slot (R9). Cite specific file:line.
```
