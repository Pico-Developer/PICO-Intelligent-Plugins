## Designer gate receipt templates

Set `input_mode` to the current run's declared mode. Do not copy an
`intent_only` receipt into `product_doc` or no-visual `hybrid` runs.

### `intent_only` receipt

```json
{
  "schema_version": 1,
  "phase": "designer_gate",
  "input_mode": "intent_only",
  "visual_asset_present": false,
  "gate_required": true,
  "status": "designer_passed",
  "pre_gates": {
    "designDocComplete": true,
    "designSpecValid": true,
    "previewMatchesSpec": true,
    "postBuildVerdict": "pass"
  }
}
```

### `product_doc` receipt

```json
{
  "schema_version": 1,
  "phase": "designer_gate",
  "input_mode": "product_doc",
  "visual_asset_present": false,
  "gate_required": true,
  "status": "designer_passed",
  "pre_gates": {
    "designDocComplete": true,
    "designSpecValid": true,
    "previewMatchesSpec": true,
    "postBuildVerdict": "pass"
  }
}
```

### No-visual `hybrid` receipt

```json
{
  "schema_version": 1,
  "phase": "designer_gate",
  "input_mode": "hybrid",
  "visual_asset_present": false,
  "gate_required": true,
  "status": "designer_passed",
  "pre_gates": {
    "designDocComplete": true,
    "designSpecValid": true,
    "previewMatchesSpec": true,
    "postBuildVerdict": "pass"
  }
}
```
