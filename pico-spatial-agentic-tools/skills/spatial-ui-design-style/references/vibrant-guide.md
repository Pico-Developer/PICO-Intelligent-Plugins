---
title: Vibrant Rendering and Color System
audience: spatial-ui-design-style / any SpatialUI Compose code-generation flow
trigger: restoring the design deliverable's coordinated theme, using custom colors, choosing Vibrant levels, preserving fixed colors, or inferring adaptive colors from Figma / screenshots
migrated_from: legacy-d2c-reference/vibrant-guide.md (Phase B1.4)
---

# Vibrant Rendering and Color System

Vibrant is one of the core rendering features of SpatialUI. A UI that uses Vibrant adapts its brightness and darkness to the current background and material context so that it stays readable across changing environments.

---

## 1. Vibrant Levels

```kotlin
enum class Vibrant {
    Darkest,
    UltraDark,
    Darker,
    Semidark,
    Dark,
    Neutral,
    Light,
    SemiLight,
    UltraLight,
    LightenPressed,
    None,
    Unspecified,
}
```

| Level                                             | Typical Use                                     |
| ------------------------------------------------- | ----------------------------------------------- |
| `Darkest`                                         | main body text, main titles                     |
| `UltraDark`                                       | emphasized foreground                           |
| `Darker`                                          | primary filled actions, accent-like backgrounds |
| `Semidark`                                        | section headings, supporting labels             |
| `Dark`                                            | secondary foreground, icons                     |
| `Neutral`                                         | cards, list rows, secondary button backgrounds  |
| `Light`                                           | large in-window content sections                |
| `SemiLight`                                       | selected state fill, slider progress            |
| `UltraLight`                                      | very weak foreground                            |
| `LightenPressed`                                  | automatic pressed overlay                       |
| `None`                                            | preserve the original color                     |
| `None` via `Modifier.vibrantEffect(Vibrant.None)` | stop Vibrant propagation                        |
| `Unspecified`                                     | inherit from the parent context                 |

---

## 2. Two API Styles

### 2.1 Convenient style (recommended for most cases)

```kotlin
import com.pico.spatial.ui.foundation.vibrant.Vibrant
import com.pico.spatial.ui.foundation.vibrant.withVibrant
import com.pico.spatial.ui.graphics.Vibrant
```

#### Typical usage

```kotlin
Modifier.background(color = Color.Vibrant.withVibrant(Vibrant.Light))

Text("Title", color = Color.Vibrant.withVibrant(Vibrant.Darkest))

Button(
    colors = ButtonDefaults.buttonColors(
        containerColor = Color.Vibrant.withVibrant(Vibrant.Neutral),
        contentColor = Color.Vibrant.withVibrant(Vibrant.Darkest)
    )
) { Text("Secondary") }

Icon(painter = ..., tint = Color.Vibrant.withVibrant(Vibrant.Dark))

Icon(painter = ..., tint = Color.Red.withVibrant(Vibrant.None))
Icon(painter = ..., tint = Color.Unspecified)

Color(0xff28ad00).withVibrant(Vibrant.UltraDark)
```

### 2.2 Low-level style (for propagation control)

```kotlin
import com.pico.spatial.ui.foundation.vibrant.vibrantEffect

Box(modifier = Modifier.vibrantEffect(Vibrant.Dark).background(Color.Vibrant))
Modifier.background(vibrant = Vibrant.Neutral, color = Color.Vibrant, shape = RectangleShape)
```

> **Rule**: unless you need explicit propagation control, prefer the convenient style in §2.1.

---

## 3. Propagation Rules

### 3.1 Default inheritance

A parent Vibrant context propagates to children automatically.

```kotlin
Box(modifier = Modifier.vibrantEffect(Vibrant.Light).background(Color.Vibrant)) {
    Text("Inherited", color = Color.Vibrant)
    Box(modifier = Modifier.background(Color.Blue))
}
```

### 3.2 Child override

```kotlin
Text("Dark overrides Light", color = Color.Vibrant.withVibrant(Vibrant.Dark))
```

### 3.3 Terminating propagation

```kotlin
Text("Pure color", color = Color.Red.withVibrant(Vibrant.None))

Box(modifier = Modifier.vibrantEffect(Vibrant.None)) {
    Text("Unaffected by Vibrant", color = Color.Red)
}
```

---

## 4. Mixing Rules

| Context Vibrant | Color Value                           | Rendered Result                     |
| --------------- | ------------------------------------- | ----------------------------------- |
| none            | `Color.Red`                           | standard red                        |
| none            | `Color.Vibrant`                       | black                               |
| `Light`         | `Color.Red`                           | `Light` mixed with red              |
| `Light`         | `Color.Vibrant`                       | pure `Light`                        |
| any             | `Color.Red.withVibrant(Vibrant.None)` | pure red, unaffected by the context |

---

## 5. Vibrant Style Reference

| Vibrant Style | Typical Use                             | Visual Cue                       |
| ------------- | --------------------------------------- | -------------------------------- |
| `Darkest`     | primary text, titles                    | deepest text on the page         |
| `UltraDark`   | emphasized foreground, dialog titles    | slightly stronger than body text |
| `Semidark`    | section labels, auxiliary headings      | medium-dark text                 |
| `Dark`        | icons, weaker information               | tinted icons and subdued text    |
| `Darker`      | primary button background               | filled action surface            |
| `Neutral`     | card, list, secondary button background | translucent secondary surfaces   |
| `Light`       | large content background                | broad light section              |
| `SemiLight`   | selected fill, slider progress          | stronger selected-state fill     |
| `None`        | preserve literal color                  | fixed-color icon or badge        |

---

## 6. Figma Color Decision Tree (when annotations exist)

Preserve the native SpatialUI `ColorScheme` and classify each design color
without modifying an existing role (see `tokens.md §7`):

```text
Figma token name
├── Has a `(Vibrant)` suffix?
│   └── Yes -> `Color.Vibrant.withVibrant(Vibrant.Xxx)`
├── Is it a semantic role?
│   └── Yes -> `PicoTheme.colorScheme.xxx` unchanged
├── Is it a semantic fixed color?
│   └── Yes -> `PicoTheme.colorScheme.xxx`
└── Is it a custom color (brand / decorative / product-specific state)?
    └── Keep it verbatim: named brand token, or
        `Color(0xFFxxxxxx) // design-style: fixed-figma-color <source>`
```

> Custom colors are explicitly allowed and are the correct choice whenever a
> design value has no matching PICO role. Never approximate a custom color with
> the nearest default role — that discards the design identity.

---

## 7. Screenshot Color Inference Chain (when Figma annotations do not exist)

Even without annotations, preserve native SpatialUI roles. Custom colors sampled
from the screenshot are allowed; keep them verbatim as named app-owned tokens
or annotated fixed literals and use them directly. Use the chain below to
classify the remaining adaptive hierarchy.

### Step 1: identify the element role

```text
What is this element?
├── text -> Step 2A
├── background -> Step 2B
├── button -> Step 2C
├── icon -> Step 2D
└── divider / border -> `PicoTheme.colorScheme.dividerLine`
```

### Step 2A: infer text color

```text
How important is the text?
├── main title / most important content -> `Vibrant.Darkest`
├── secondary title / emphasized content -> `Vibrant.UltraDark`
├── group heading / section label -> `Vibrant.Semidark`
├── body description / helper info -> `Vibrant.Dark`
├── faint helper / watermark -> `Vibrant.UltraLight`
└── button label -> depends on button type; see 2C
```

### Step 2B: infer background color

```text
What is the area and hierarchy?
├── large content region -> `Vibrant.Light`
├── card / list row / medium surface -> `Vibrant.Neutral`
├── selected / active background -> `Vibrant.SemiLight`
├── material / glass shell -> `enableMaterialBackground = true` or window-level material
└── fixed solid background -> use the literal color value
```

### Step 2C: infer button colors

```text
What is the button weight?
├── filled and most prominent -> primary button, use default filled colors (`Darker`-like accent)
├── light secondary surface -> `containerColor = Neutral`, `contentColor = Darkest`
├── transparent / ghost -> `containerColor = Transparent`, `contentColor = Darkest`
└── dangerous red action -> `containerColor = PicoTheme.colorScheme.error`
```

### Step 2D: infer icon colors

```text
What is the icon behavior?
├── follows text color -> `Vibrant.Dark` or `Vibrant.Darkest`
├── fixed semantic color -> `Color.Xxx.withVibrant(Vibrant.None)`
├── multicolor asset -> `tint = Color.Unspecified`
└── lightly blended foreground -> `Vibrant.Semidark`
```

### Step 3: cross-check the inference

```text
1. Does more important text use deeper Vibrant levels?
2. Does a `Neutral` card surface pair with sufficiently deep foreground text?
3. Is button contrast still strong enough?
4. Did you miss any translucent or material effect?
```

---

## 8. API Quick Reference

| API                                                            | Purpose                                                                                                           |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `PicoTheme { ... }`                                            | use the unchanged native SpatialUI color scheme                                                                   |
| `PicoTheme.colorScheme.<role>`                                 | consume an existing native semantic role                                                                          |
| `val BrandX = Color(0x…) // design-style: fixed-figma-color …` | define an app-owned custom color without replacing a native role                                                   |
| `Color.Vibrant.withVibrant(Vibrant.Xxx)`                       | recommended shorthand                                                                                             |
| `Color.Red.withVibrant(Vibrant.None)`                          | preserve a fixed literal color                                                                                    |
| `Color.Unspecified`                                            | preserve the original icon colors                                                                                 |
| `Modifier.vibrantEffect(vibrant)`                              | low-level Vibrant entry                                                                                           |
| `Modifier.vibrantEffect(Vibrant.None)`                         | stop propagation                                                                                                  |
| `Modifier.background(vibrant, color, shape)`                   | advanced background-only Vibrant control                                                                          |

---

## 9. App-level Vibrant Toggle (debugging only)

```xml
<meta-data android:name="com.pico.spatial.ui.isVibrant" android:value="false" />
```

If disabled, `Color.Vibrant` renders as black and the app must explicitly adapt the visual design.
