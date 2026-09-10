# Scene Plan Format

Read this reference only when the task explicitly requires an offline layout
plan or `.spatialsdk/scene_transforms.json` configuration. A plan is an
intermediate artifact; it is not a completed SDK-authored scene.

## Output Location

Save `.spatialsdk/scene_transforms.json` at the user's project root unless the
request specifies another location. Write the accepted file only when every
required transform and bound is numeric and its units are verified.

## Minimum Contract

```json
{
  "schemaVersion": 1,
  "sceneContext": {
    "description": "...",
    "coordinateSpace": "sceneRoot-local",
    "axes": { "x": "right", "y": "up", "z": "front" },
    "assumptions": []
  },
  "sceneDimensionsMeters": {
    "min": [0, 0, 0],
    "max": [0, 0, 0],
    "size": [0, 0, 0]
  },
  "regions": [
    {
      "id": "independent-region-id",
      "source": "accepted design contract",
      "boundsMeters": {
        "min": [0, 0, 0],
        "max": [0, 0, 0]
      }
    }
  ],
  "elements": [
    {
      "id": "entity-id",
      "parent": "sceneRoot",
      "semanticRole": "body",
      "scalePolicy": "uniform-flexible",
      "sourcePath": "asset.ext",
      "originalBounds": {
        "min": [0, 0, 0],
        "max": [0, 0, 0],
        "units": "verified-source-unit",
        "evidence": "inspection method"
      },
      "finalBoundsMeters": {
        "min": [0, 0, 0],
        "max": [0, 0, 0]
      },
      "transform": {
        "translationMeters": [0, 0, 0],
        "rotationDegreesXYZ": [0, 0, 0],
        "scaleXYZ": [1, 1, 1]
      },
      "relationships": [
        {
          "type": "contained-by",
          "regionId": "independent-region-id",
          "boundsScope": "body"
        }
      ]
    }
  ]
}
```

Extensions may add fields but must not rename or omit the minimum fields.
Express each Entity transform in its declared parent's coordinate space. Keep
source-coordinate bounds distinct from final meter-space runtime bounds.
Use `uniform-flexible` as the default scale policy. Use `exact-size` or
`non-scalable` only when the asset or accepted requirement says so, and record a
no-fit conflict rather than changing that scale. Keep permitted regions in a
separate region collection or other independently sourced extension; do not
derive a region by unioning it with the target it validates.

List assumptions only for decisions that the accepted scene contract allows the
agent to make. Do not use `assumptions` to legitimize guessed source units,
bounds, pivots, or asset orientation.

If required evidence is missing, report the blocker and optionally show a
null-bearing draft in the response. Do not save that draft as the accepted
configuration, and do not claim that producing this file implements the scene.
