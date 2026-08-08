# .pico-cli/config.json structure

Written to `$PROJECT_ROOT/.pico-cli/config.json` after initialization completes.

## Fields

| Field | Source step | Type | Values |
|---|---|---|---|
| `project_name` | Auto | string | Directory name of the current project (basename of `$PROJECT_ROOT`) |
| `sdk` | Step 1 | string (single-choice) | `openxr` \| `picoxr` |
| `unity_version` | Step 2 | string | Selected Unity 6+ LTS full version, e.g. `6000.0.73f1` |
| `platform` | Fixed | string | Fixed to `android` (PICO is an Android platform; no other platforms allowed) |
| `devices` | Step 6 | string[] (multi-choice) | `pico swan`, `pico 4 ultra` |
| `business_type` | Step 7 | string (single-choice) | `toB` \| `toC`. The form asks "Building an enterprise edition?" — "Yes" → store `toB`, "No" → store `toC` (store the final value, not "Yes / No") |

## Example

```json
{
  "project_name": "MyPicoApp",
  "sdk": "picoxr",
  "unity_version": "6000.0.73f1",
  "platform": "android",
  "devices": ["pico swan", "pico 4 ultra"],
  "business_type": "toB"
}
```

> If the `.pico-cli/` directory does not exist, create the directory first and then write the file. The presence of config.json indicates the project has been initialized; subsequent triggers of the skill should skip initialization based on this.
