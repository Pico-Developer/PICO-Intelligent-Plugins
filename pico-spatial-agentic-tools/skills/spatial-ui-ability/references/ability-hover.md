# Hover Effects

Capability: `Modifier.spatialHoverEffect`, `spatialHoverEffectGroup`, `disableSpatialHoverEffect`.

## Preset Styles (Shortest Form)

```kotlin
import com.pico.spatial.ui.foundation.hover.spatialHoverEffect
import com.pico.spatial.ui.foundation.hover.SpatialHoverStyle

Box(
    Modifier
        .size(100.dp)
        .background(Color.Gray)
        .spatialHoverEffect()                          // default = SpatialHoverStyle.Default
        // or .spatialHoverEffect(style = SpatialHoverStyle.Highlight)
)
```

## Custom DSL

```kotlin
Box(
    Modifier
        .size(100.dp)
        .spatialHoverEffect {
            scale(if (it.isActive) 1.1f else 1f)
            offset(y = if (it.isActive) (-4).dp else 0.dp)
            alpha(if (it.isActive) 1f else 0.8f)
        }
)
```

## Custom Animation Curves

```kotlin
Modifier.spatialHoverEffect {
    animation(tween(durationMillis = 250, easing = FastOutSlowInEasing)) {
        scale(if (it.isActive) 1.05f else 1f)
    }
    animation(spring(stiffness = 700f)) {
        offset(y = if (it.isActive) (-4).dp else 0.dp)
    }
}
```

## Cross-View Coordination (Hover Group)

```kotlin
import com.pico.spatial.ui.foundation.hover.SpatialHoverEffectGroup
import com.pico.spatial.ui.foundation.hover.spatialHoverEffectGroup

val group = remember { SpatialHoverEffectGroup.obtain() }
Row {
    items.forEach { item ->
        Card(
            Modifier
                .spatialHoverEffectGroup(group)
                .spatialHoverEffect()
        ) { /* content */ }
    }
}
```

## Disable Hover For A Subtree

```kotlin
import com.pico.spatial.ui.foundation.hover.disableSpatialHoverEffect

Box(Modifier.disableSpatialHoverEffect(disabled = !isEnabled)) {
    // Button already ships hover internally — no Modifier.spatialHoverEffect needed.
    Button(onClick = {}) { Text("btn") }
}
```

## Notes

- **Only for custom composables.** SpatialUI built-in components (`Button`, `IconButton`, `Card`, `ToggleableChip`, ...) already apply `spatialHoverEffect` internally. Do NOT add `Modifier.spatialHoverEffect` on top of them — it double-applies the effect. Reach for `Modifier.spatialHoverEffect` only when you build your own hoverable composable that does not already ship the effect.
- The DSL block is evaluated twice (`isActive = true` and `false`). The number of declared effects must stay identical in both branches.
- Do not conditionally add or remove effects inside `if (isActive)`. Keep the effect structure fixed and vary only the values.
- Hover runs in the system process; application code cannot observe raw hover events directly.
- **`clip` must come before `spatialHoverEffect`** whenever the node has a rounded/clipped shape; otherwise the hover highlight and hit area follow the unclipped bounds instead of the visible shape. The relative order of `background` / `backgroundMaterial` and `spatialHoverEffect` does not matter.

```kotlin
Box(
    Modifier
        .size(100.dp)
        .clip(RoundedCornerShape(12.dp))     // clip first — hover/hit follow the clipped shape
        .spatialHoverEffect()
        .background(Color.Gray)
)
```

## Hover Not Working? Check This

1. Are you running on a Spatial platform? Hover is a system-level effect.
2. Did a parent disable hover with `disableSpatialHoverEffect`?
3. Does the DSL declare the same number of effects for both active and inactive states?
4. Is the content inside a `WindowContainer`?
5. Is the view visible and actually interactive?
6. Rounded shape but hover/hit spills outside it? Make sure `clip` comes before `spatialHoverEffect`.

## Imports

```kotlin
import com.pico.spatial.ui.foundation.hover.spatialHoverEffect
import com.pico.spatial.ui.foundation.hover.SpatialHoverStyle
import com.pico.spatial.ui.foundation.hover.SpatialHoverEffectGroup
import com.pico.spatial.ui.foundation.hover.spatialHoverEffectGroup
import com.pico.spatial.ui.foundation.hover.disableSpatialHoverEffect
```

---

See also: [`troubleshooting.md`](troubleshooting.md) for cross-cutting checks (Spatial platform, `WindowContainer`, modifier order).
