package probe

import android.util.Log
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.onGloballyPositioned
import com.pico.spatial.core.container.SpatialViewContent
import com.pico.spatial.core.ecs.ViewCoordinateSpace
import com.pico.spatial.core.math.Vector3
import com.pico.spatial.ui.foundation.layout.IntSize3D
import com.pico.spatial.ui.foundation.layout.sizeIn3D
import java.nio.charset.StandardCharsets
import java.time.Instant
import org.json.JSONArray
import org.json.JSONObject

private const val PRODUCER_ID = "spatialview-visible-region-probe"
private const val PRODUCER_VERSION = 1
private const val LOG_TAG = "SpatialFitProbe"
private const val LOG_PREFIX = "SPATIAL_FIT_MEASUREMENT "

class SpatialViewVisibleRegionProbe(
    private val profileId: String,
    private val sdkVersion: String,
    private val emit: (String) -> Unit = { payload ->
        Log.i(LOG_TAG, "$LOG_PREFIX$payload")
    },
) {
    private var content: SpatialViewContent? = null
    private var size: IntSize3D? = null
    private var lastFingerprint: String? = null

    fun bind(content: SpatialViewContent) {
        this.content = content
        captureIfReady()
    }

    fun updateLayout(size: IntSize3D) {
        this.size = size
        captureIfReady()
    }

    fun capture(): String {
        val currentContent = checkNotNull(content) {
            "Bind SpatialViewContent before capturing its visible region"
        }
        val currentSize = checkNotNull(size) {
            "Wait for SpatialView layout before capturing its visible region"
        }
        require(currentSize.width > 0 && currentSize.height > 0 && currentSize.depth > 0) {
            "SpatialView must have positive width, height, and depth"
        }

        val context = JSONObject()
            .put("coordinate_from", "view-local-px")
            .put("coordinate_to", "spatial-view-local-meters")
            .put("profile_id", profileId)
            .put("sdk_version", sdkVersion)
            .put(
                "view_size_px",
                JSONArray()
                    .put(currentSize.width)
                    .put(currentSize.height)
                    .put(currentSize.depth),
            )
        val contextFingerprint = fnv1a32(canonicalContext(currentSize))
        val rawCorners = boxCorners(
            currentSize.width.toFloat(),
            currentSize.height.toFloat(),
            currentSize.depth.toFloat(),
        )
        val convertedCorners = rawCorners.map { point ->
            currentContent.convertPosition(
                point,
                ViewCoordinateSpace.Local,
                currentContent.localSpatialCoordinateSpace,
            )
        }
        val minimum = Vector3(
            convertedCorners.minOf(Vector3::x),
            convertedCorners.minOf(Vector3::y),
            convertedCorners.minOf(Vector3::z),
        )
        val maximum = Vector3(
            convertedCorners.maxOf(Vector3::x),
            convertedCorners.maxOf(Vector3::y),
            convertedCorners.maxOf(Vector3::z),
        )

        val measurement = JSONObject()
            .put("schema_version", 1)
            .put("measurement_kind", "target-visible-region")
            .put(
                "producer",
                JSONObject()
                    .put("id", PRODUCER_ID)
                    .put("version", PRODUCER_VERSION),
            )
            .put("captured_at_utc", Instant.now().toString())
            .put("context", context)
            .put("context_fingerprint", contextFingerprint)
            .put(
                "raw_box",
                boxJson(
                    Vector3(0f, 0f, 0f),
                    Vector3(
                        currentSize.width.toFloat(),
                        currentSize.height.toFloat(),
                        currentSize.depth.toFloat(),
                    ),
                    "spatial-view-local-px",
                ),
            )
            .put("raw_corners", vectorsJson(rawCorners))
            .put("converted_corners_m", vectorsJson(convertedCorners))
            .put("aabb_m", boxJson(minimum, maximum))

        return measurement.toString().also(emit)
    }

    private fun captureIfReady() {
        val currentSize = size ?: return
        if (content == null || currentSize.width <= 0 || currentSize.height <= 0 ||
            currentSize.depth <= 0
        ) {
            return
        }
        val fingerprint = fnv1a32(canonicalContext(currentSize))
        if (fingerprint == lastFingerprint) {
            return
        }
        capture()
        lastFingerprint = fingerprint
    }

    private fun canonicalContext(size: IntSize3D): String =
        buildString {
            append("{\"coordinate_from\":\"view-local-px\",")
            append("\"coordinate_to\":\"spatial-view-local-meters\",")
            append("\"profile_id\":")
            append(JSONObject.quote(profileId))
            append(",\"sdk_version\":")
            append(JSONObject.quote(sdkVersion))
            append(",\"view_size_px\":[")
            append(size.width)
            append(',')
            append(size.height)
            append(',')
            append(size.depth)
            append("]}")
        }
}

fun Modifier.captureSpatialViewVisibleRegion(
    probe: SpatialViewVisibleRegionProbe,
): Modifier = onGloballyPositioned { coordinates ->
    probe.updateLayout(coordinates.sizeIn3D)
}

private fun boxCorners(width: Float, height: Float, depth: Float): List<Vector3> =
    buildList {
        for (x in listOf(0f, width)) {
            for (y in listOf(0f, height)) {
                for (z in listOf(0f, depth)) {
                    add(Vector3(x, y, z))
                }
            }
        }
    }

private fun vectorJson(value: Vector3): JSONArray =
    JSONArray()
        .put(value.x.toDouble())
        .put(value.y.toDouble())
        .put(value.z.toDouble())

private fun vectorsJson(values: List<Vector3>): JSONArray =
    JSONArray().also { array ->
        values.forEach { array.put(vectorJson(it)) }
    }

private fun boxJson(
    minimum: Vector3,
    maximum: Vector3,
    space: String? = null,
): JSONObject =
    JSONObject().apply {
        if (space != null) {
            put("space", space)
        }
        put("min", vectorJson(minimum))
        put("max", vectorJson(maximum))
        put(
            "size",
            vectorJson(
                Vector3(
                    maximum.x - minimum.x,
                    maximum.y - minimum.y,
                    maximum.z - minimum.z,
                ),
            ),
        )
    }

private fun fnv1a32(value: String): String {
    var hash = 0x811c9dc5.toInt()
    for (byte in value.toByteArray(StandardCharsets.UTF_8)) {
        hash = hash xor (byte.toInt() and 0xff)
        hash *= 0x01000193
    }
    return "fnv1a32:%08x".format(hash)
}
