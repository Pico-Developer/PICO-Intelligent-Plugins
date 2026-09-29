# Scaffold Handoff Contract

This contract records the narrow handoff from `spatial-app-onboarding` back to
`spatial-design-to-app` during a product-specific `new_project` run.

## When This Applies

Use this handoff only when `spatial-design-to-app` has already resolved the
container and window model, and the Build stage needs a fresh Spatial SDK
project scaffold.

**The project skeleton is created by `pico-cli project create` — never by hand.**
Neither skill authors `build.gradle.kts`, `settings.gradle.kts`,
`libs.versions.toml`, the Gradle wrapper, or the base `AndroidManifest.xml`. The
CLI owns all of them, and a hand-assembled skeleton drifts off the CLI baseline.

`spatial-app-onboarding` owns only:

- running `pico-cli project create` with the resolved template
- preserving the generated entry chain
- first build / install / launch stabilization when the environment allows it
- writing `.scratch/onboarding_handoff.json`

`spatial-design-to-app` continues to own:

- product UI, pages, navigation, and visual-reference fidelity
- the design evidence, the container / window-model decision, and the assumptions
- architecture conventions, SpatialUI component mapping, and verification

## Required File

Write this file under the generated project target:

```text
<target>/.scratch/onboarding_handoff.json
```

## Schema

```json
{
  "schema_version": 1,
  "phase": "6_scaffold_handoff",
  "producer_skill": "spatial-app-onboarding",
  "consumer_skill": "spatial-design-to-app",
  "scaffold_only": true,
  "product_ui_implemented": false,
  "template": "planar",
  "package": "com.example.demo.p1234abcd",
  "package_source": "generated_default",
  "entry_points": [
    "app/src/main/java/com/example/demo/p1234abcd/Main.kt",
    "app/src/main/AndroidManifest.xml"
  ],
  "build_passed": true,
  "launch_checked": false,
  "launch_check_note": "adb device unavailable; build passed but launch was not checked",
  "resume_required": true,
  "resume_skill": "spatial-design-to-app"
}
```

## Field Rules

| Field                    | Rule                                                                                  |
| ------------------------ | ------------------------------------------------------------------------------------- |
| `schema_version`         | Must be `1`.                                                                          |
| `phase`                  | Must identify the scaffold handoff step; use `6_scaffold_handoff`.                    |
| `producer_skill`         | Must be `spatial-app-onboarding`.                                                     |
| `consumer_skill`         | Must be `spatial-design-to-app`.                                                      |
| `scaffold_only`          | Must be `true`.                                                                       |
| `product_ui_implemented` | Must be `false`; product UI belongs to `spatial-design-to-app`.                       |
| `template`               | One of `planar`, `volumetric`, or `stage`, mapped from the container decision.        |
| `package`                | Final Android application ID/package used by the scaffold.                            |
| `package_source`         | `user_provided` or `generated_default`; must match the upstream identity decision.    |
| `entry_points`           | Non-empty list of generated entry files that `spatial-design-to-app` should preserve. |
| `build_passed`           | Must be `true` before handoff.                                                        |
| `launch_checked`         | Boolean; `true` only when install/launch was actually checked.                        |
| `launch_check_note`      | Required when `launch_checked=false`; state the external blocker.                     |
| `resume_required`        | Must be `true`.                                                                       |
| `resume_skill`           | Must be `spatial-design-to-app`.                                                      |

## Hard Failures

Verification must fail when:

- `.scratch/onboarding_handoff.json` is missing for a `new_project` run
- `scaffold_only` is not `true`
- `product_ui_implemented` is not `false`
- `package` / `package_source` is missing, invalid, or a generated default does
  not match `com.example.<app-slug>.p<8-lowercase-hex-characters>`
- `build_passed` is not `true`
- `resume_skill` is not `spatial-design-to-app`

If onboarding added product UI before returning, discard that product UI and
rebuild it under `spatial-design-to-app` from the container and window-model
decision. Do not treat an onboarding-created product page as the final app
implementation.
