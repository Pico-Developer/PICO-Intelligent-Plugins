# .pico-cli/config.json structure

Written to `$PROJECT_ROOT/.pico-cli/config.json` after initialization completes. If the file already exists without a completed marker, merge these fields while preserving unrelated fields.

## Fields

| Field                       | Source       | Type                    | Values                                                                                                                                                                          |
| --------------------------- | ------------ | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `project_name`              | Auto         | string                  | Directory name of the current project (basename of `$PROJECT_ROOT`)                                                                                                             |
| `mode`                      | Stage B/C    | string (single-choice)  | One of `picoxr`, `openxr`, or `picospatial`. For an empty project, this is the selected template mode: `PICOXR` → `picoxr`, `OpenXR` → `openxr`, `PICOSpatial` → `picospatial`. |
| `unity_version`             | Version form | string                  | Selected Unity 6+ LTS full version, e.g. `6000.0.73f1`                                                                                                                          |
| `platform`                  | Fixed        | string                  | Fixed to `android` (PICO is an Android platform; no other platforms allowed)                                                                                                    |
| `devices`                   | Form         | string[] (multi-choice) | `pico swan`, `pico 4 ultra`                                                                                                                                                     |
| `business_type`             | Form         | string (single-choice)  | `toB` or `toC`. The form asks "Building an enterprise edition?" — "Yes" → store `toB`, "No" → store `toC`.                                                                      |
| `pico_unity_init_completed` | Finalization | boolean                 | `true` only after every initialization step succeeds and Unity accepts the open command. This is the sole one-time completion marker.                                           |

## Example

```json
{
  "project_name": "MyPicoApp",
  "mode": "picoxr",
  "unity_version": "6000.0.73f1",
  "platform": "android",
  "devices": ["pico swan", "pico 4 ultra"],
  "business_type": "toB",
  "pico_unity_init_completed": true
}
```

After the developer explicitly invokes `/pico-unity-init`, the skill must parse this file before initialization. If `pico_unity_init_completed` is exactly `true`, skip every initialization action and reply `已使用过/pico-unity-init`. If the field is absent or not `true`, continue the current explicitly invoked initialization once. Config existence alone does not mean initialization completed. A malformed JSON file must be reported instead of overwritten. This schema describes initialization state; it does not authorize passive or automatic skill activation.

If the `.pico-cli/` directory does not exist, create the directory before the final write. Write valid JSON atomically, preserve unrelated fields in an existing config, and remove the obsolete `sdk` field. Do not write the completion marker on a failed or cancelled run. Do not delete `.pico-cli/config.json` for an SDK refresh or repair. Route post-init package changes to `pico-unity-package-manager` after the Unity Editor and MCP bridge are running. If the bridge is unavailable, restore the Editor/MCP connection first; do not fall back to rerunning initialization or editing `Packages/manifest.json`. A full project reset is a separate destructive workflow outside `pico-unity-init` and requires explicit authorization plus a backup.

Use the bundled `../scripts/write_config.py` helper for the final atomic merge. It validates `mode` and `business_type`, accepts repeated `--device` arguments, preserves unrelated fields, removes legacy `sdk`, and sets `pico_unity_init_completed` to `true`. Invoke it only after the initialization flow has succeeded.
