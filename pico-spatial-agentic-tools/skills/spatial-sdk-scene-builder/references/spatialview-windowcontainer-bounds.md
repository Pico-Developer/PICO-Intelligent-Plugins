# SpatialView and WindowContainer Bounds

Use this reference when a PICO Entity must remain inside a `SpatialView`, inside
the containing bounded `WindowContainer`, or inside their intersection.

## Contents

- Why coordinate conversion is the primary path
- Reusable measurement helper
- Public owner-coordinate pattern
- Compose lifecycle and usage example
- SpatialView versus WindowContainer
- Limitations

## Why Coordinate Conversion Is the Primary Path

`ViewCoordinateSpace.Local` starts at the current view's top-left-back corner.
`ViewCoordinateSpace.Global` starts at the containing WindowContainer's
top-left-back corner. `content.localSpatialCoordinateSpace` uses meters,
right-handed PICO axes, and the SpatialView center as its origin.

Use `convertPosition()` so the SDK handles virtual pixels, meters, handedness,
and view offset. The converted SpatialView top-left-back point directly gives
its three half-extents because the local spatial origin is the SpatialView
center. Do not derive its side lengths with display density,
`PhysicalLengthConverter`, or a meters-per-pixel calculation.

## Reusable Measurement Helper

This template assumes an ordinary axis-aligned SpatialView inside a
WindowContainer. `windowContentSizePx` must be the unpadded root content size of
that WindowContainer.

```kotlin
import androidx.compose.ui.unit.IntSize
import com.pico.spatial.core.container.SpatialViewContent
import com.pico.spatial.core.ecs.BoundingBox
import com.pico.spatial.core.ecs.ViewCoordinateSpace
import com.pico.spatial.core.math.Vector3
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

data class BoundedSpatialViewRegions(
    val spatialView: BoundingBox,
    val windowContainer: BoundingBox,
)

fun SpatialViewContent.measureBoundedRegions(
    windowContentSizePx: IntSize,
): BoundedSpatialViewRegions? {
    if (windowContentSizePx.width <= 0 || windowContentSizePx.height <= 0) {
        return null
    }

    val localSpace = localSpatialCoordinateSpace
    val spatialViewTopLeftBack =
        convertPosition(Vector3.ZERO, ViewCoordinateSpace.Local, localSpace)

    val spatialViewHalfExtent =
        Vector3(
            abs(spatialViewTopLeftBack.x),
            abs(spatialViewTopLeftBack.y),
            abs(spatialViewTopLeftBack.z),
        )
    if (
        spatialViewHalfExtent.x <= 0f ||
            spatialViewHalfExtent.y <= 0f ||
            spatialViewHalfExtent.z <= 0f
    ) {
        return null
    }

    val windowTopLeftBack =
        convertPosition(Vector3.ZERO, ViewCoordinateSpace.Global, localSpace)
    val windowBottomRightBack =
        convertPosition(
            Vector3(
                windowContentSizePx.width.toFloat(),
                windowContentSizePx.height.toFloat(),
                0f,
            ),
            ViewCoordinateSpace.Global,
            localSpace,
        )

    return BoundedSpatialViewRegions(
        spatialView =
            BoundingBox(
                center = Vector3.ZERO,
                halfExtent = spatialViewHalfExtent,
            ),
        windowContainer =
            windowContainerBounds(
                windowTopLeftBack,
                windowBottomRightBack,
                spatialViewHalfExtent.z,
            ),
    )
}

private fun windowContainerBounds(
    topLeftBack: Vector3,
    bottomRightBack: Vector3,
    depthHalfExtent: Float,
): BoundingBox {
    val center =
        Vector3(
            (topLeftBack.x + bottomRightBack.x) * 0.5f,
            (topLeftBack.y + bottomRightBack.y) * 0.5f,
            0f,
        )
    val halfExtent =
        Vector3(
            abs(bottomRightBack.x - topLeftBack.x) * 0.5f,
            abs(bottomRightBack.y - topLeftBack.y) * 0.5f,
            depthHalfExtent,
        )
    return BoundingBox(
        center = center,
        halfExtent = halfExtent,
    )
}
```

Compared with measuring both views manually, this helper:

- needs only the WindowContainer root content size
- derives SpatialView X/Y/Z extents directly from the converted local corner
- converts only the WindowContainer's X/Y back-face corners
- reuses the SpatialView's converted Z extent because WindowContainer clipping
  does not introduce a separate 3D depth
- returns SDK `BoundingBox` values
- contains no density or px-to-meter arithmetic

## Use Only Public Owner Coordinates

Do not call `content.localSpatialCoordinateSpace.origin` from application code.
The SDK source marks that `origin` Entity as library-restricted.

Instead, create an identity owner as a direct SpatialView child. For a complete
bounded composition, put a separate fitted root beneath it and place scene
Entities below that root:

```kotlin
val placementOwner = Entity()
val fittedSceneRoot = Entity()
content.addEntity(placementOwner)
placementOwner.addChild(fittedSceneRoot)
fittedSceneRoot.addChild(reference)
fittedSceneRoot.addChild(target)

val targetBounds =
    target.getVisualBounds(
        relativeTo = placementOwner,
        recursive = true,
        enabledOnly = true,
    )
```

An identity `placementOwner` has the same axes and origin as
`content.localSpatialCoordinateSpace`, so the measured regions and
`getVisualBounds(placementOwner)` are compatible. If the owner is transformed,
convert the region corners into owner space before using them.

Keep the safe region, transformed planned envelope, and final visual bounds in
`placementOwner`. Apply one explicit outer scale/translation to
`fittedSceneRoot`; do not transform the evidence owner.

## Compose Lifecycle

Measure the WindowContainer root with `onSizeChanged` before padding:

```kotlin
var windowContentSizePx by remember { mutableStateOf(IntSize.Zero) }

Row(
    Modifier
        .fillMaxSize()
        .onSizeChanged { windowContentSizePx = it }
        .padding(48.dp),
) {
    // SpatialView(...)
}
```

Do not rely on non-zero size state inside `SpatialView.initial`: the first
callback can run before `onSizeChanged` updates Compose state. Create/load the
Entities in `initial`, then call `measureBoundedRegions()` and place them from
`update` after `windowContentSizePx` becomes valid.

The following is a compact usage pattern. It centers a loaded target in the
intersection of the SpatialView and WindowContainer, with a margin. In addition
to the helper imports, it uses Compose runtime state, `Modifier.onSizeChanged`,
`Entity`, `TransformComponent`, and `SpatialView`.

```kotlin
private class BoundedScene {
    var owner: Entity? = null
    var fittedRoot: Entity? = null
    var target: Entity? = null
    var fittedRootBasePosition = Vector3.ZERO
    var placedForSizes: Pair<IntSize, IntSize>? = null
}

@Composable
private fun BoundedModel(
    windowContentSizePx: IntSize,
    margin: Vector3,
) {
    require(margin.x >= 0f && margin.y >= 0f && margin.z >= 0f)

    val scene = remember { BoundedScene() }
    var spatialViewSizePx by remember { mutableStateOf(IntSize.Zero) }

    SpatialView(
        modifier =
            Modifier.onSizeChanged {
                spatialViewSizePx = it
            },
        initial = { content, _ ->
            val owner = Entity()
            val fittedRoot = Entity()
            val target = Entity.loadSuspend("asset://model.usdz")
            content.addEntity(owner)
            owner.addChild(fittedRoot)
            fittedRoot.addChild(target)
            scene.owner = owner
            scene.fittedRoot = fittedRoot
            scene.target = target
            scene.fittedRootBasePosition =
                fittedRoot.components.get<TransformComponent>()?.position
                    ?: Vector3.ZERO
        },
        update = update@{ content, _ ->
            if (
                windowContentSizePx == IntSize.Zero ||
                    spatialViewSizePx == IntSize.Zero
            ) {
                return@update
            }

            val sizeKey = windowContentSizePx to spatialViewSizePx
            if (scene.placedForSizes == sizeKey) return@update

            val owner = scene.owner ?: return@update
            val fittedRoot = scene.fittedRoot ?: return@update
            val target = scene.target ?: return@update
            val transform =
                fittedRoot.components.get<TransformComponent>() ?: return@update
            transform.position = scene.fittedRootBasePosition

            val regions =
                content.measureBoundedRegions(windowContentSizePx)
                    ?: return@update
            val safeRegion =
                intersect(regions.spatialView, regions.windowContainer)
                    ?: return@update
            val targetBounds =
                target.getVisualBounds(
                    relativeTo = owner,
                    recursive = true,
                    enabledOnly = true,
                )
            if (targetBounds.isEmpty()) return@update

            val allowedDeltaMin =
                safeRegion.min + margin - targetBounds.min
            val allowedDeltaMax =
                safeRegion.max - margin - targetBounds.max
            if (
                allowedDeltaMin.x > allowedDeltaMax.x ||
                    allowedDeltaMin.y > allowedDeltaMax.y ||
                    allowedDeltaMin.z > allowedDeltaMax.z
            ) {
                return@update // Report no-fit and the failed axis in production.
            }

            val chosenDelta =
                (allowedDeltaMin + allowedDeltaMax) * 0.5f
            transform.position = scene.fittedRootBasePosition + chosenDelta
            scene.placedForSizes = sizeKey
        },
    )

    DisposableEffect(Unit) {
        onDispose {
            scene.owner?.destroy()
            scene.owner = null
            scene.fittedRoot = null
            scene.target = null
            scene.placedForSizes = null
        }
    }
}

private fun intersect(a: BoundingBox, b: BoundingBox): BoundingBox? {
    val boundsMin =
        Vector3(
            max(a.min.x, b.min.x),
            max(a.min.y, b.min.y),
            max(a.min.z, b.min.z),
        )
    val boundsMax =
        Vector3(
            min(a.max.x, b.max.x),
            min(a.max.y, b.max.y),
            min(a.max.z, b.max.z),
        )
    if (
        boundsMin.x > boundsMax.x ||
            boundsMin.y > boundsMax.y ||
            boundsMin.z > boundsMax.z
    ) {
        return null
    }
    return BoundingBox(
        center = (boundsMin + boundsMax) * 0.5f,
        halfExtent = (boundsMax - boundsMin) * 0.5f,
    )
}
```

Keep the scene holder local to the Composable or its ViewModel; do not turn it
into a global placement framework. A production result should distinguish
unavailable bounds, empty intersection, and target no-fit instead of returning
silently as the compact example does.

The compact example demonstrates owner-compatible measurement and idempotent
root translation. When the complete composition also needs uniform fitting,
calculate and apply the scale on `fittedSceneRoot` using
`runtime-scene-fit.md`, then emit both planned and remeasured final bounds in
`placementOwner`.

Re-run measurement and placement when the WindowContainer or SpatialView
resizes. Keep a last-size/revision key if placement should not repeat on
unrelated recompositions. Destroy or retain Entities explicitly when the
SpatialView leaves composition.

## SpatialView versus WindowContainer

The two returned boxes are different:

- `spatialView` is centered at `Vector3.ZERO`
- `windowContainer` is shifted into the SpatialView's local spatial space

If the target must be visible in both, intersect them and constrain the target
to the intersection. Do not assume a nested or padded SpatialView fills the
WindowContainer.

This template is for bounded WindowContainer content. A Stage has no equivalent
global clipping box; use a named design or tracked-surface region there.

## Limitations

- The two-corner WindowContainer shortcut assumes an axis-aligned SpatialView.
  If a view transform rotates the coordinate axes, convert all eight
  WindowContainer corners and union them into an owner-local AABB.
- Coordinate conversion is valid only while the associated view exists.
- Re-query target visual bounds after asset load, hierarchy changes, scale, or
  rotation.
- Treat conversion and bounds comparisons with an epsilon rather than exact
  float equality.
