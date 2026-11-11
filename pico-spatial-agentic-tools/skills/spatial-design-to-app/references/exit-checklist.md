## Exit checklist

Complete only when ALL hold:

1. `validate_workflow_and_build.sh <target>` exits 0 **and** `verification_summary.json.clean == true`. Only Gradle sync / runtime launch may be environment-degraded, and a degraded run is not complete unless explicitly accepted in the handoff.
2. For new modules, Android Studio **Sync Project with Gradle Files** has been triggered, or the handoff states the user must run it before the first IDE run.
3. `implementation_scan_result.json`, `gradle_sync_result.json`, `architecture_check_result.json`, `unit_tests_result.json` all → `"passed": true`.
4. When `design-spec.json` exists,
   `design_fidelity_result.json.passed == true`, its SHA-256 matches the
   authoritative design file, and `mapped_refs == required_refs`. When no
   design JSON exists, it records `applicable=false` and the handoff does not
   claim JSON fidelity.
5. `design_style_result.json.passed == true` with 0 errors and no skip/degraded bypass. When the design declares custom colors, they were passed via `--design-color`; the verifier proved exact value coverage and that the native SpatialUI `ColorScheme` was not overridden.
6. For `generation_mode=new_project`, `.scratch/onboarding_handoff.json` records `scaffold_only=true`, `product_ui_implemented=false`, `build_passed=true`, `resume_skill=spatial-design-to-app`.
7. For `intent_only`, `.scratch/intent-brief.md` exists and is non-empty.
8. For no-visual inputs, the matching design gate passed: a Designer-produced
   package has `.scratch/design_escalation_receipt.json` with
   `status=designer_passed`, `designSpecValid=true`, and
   `previewMatchesSpec=true`; a user-provided package was accepted during
   routing and verification ran with
   `--design-gate-result user_package_passed`.
9. For `intent_only`, every `kind: "spatialui"` node in
   `design-spec.json` maps to and is implemented with its corresponding
   SpatialUI Compose API.
10. For `visual_design` runs that used the `codin-d2c-figma-to-code` tools, `figma_hooks_result.json` shows verify then cleanup, each exactly once. When those tools were unavailable, the run was re-routed per stage 1b (`visual_reference`, or BLOCKED) and the handoff says so — an unavailable prerequisite is never a silently skipped gate.
11. SpatialUI component slots inherit component-owned content colors by
    default; every custom state color choice has a readable effective
    foreground/background pair without a duplicate child-slot override.
12. Every declared icon resolves to its actual packaged resource and loading
    call under [Image and icon sources](./preview-first-restoration.md#image-and-icon-sources).
    SVGs use Coil with SVG support; original bitmaps use normal image loading.
    ICON 7.0 catalog-backed Android vectors pass `icon-catalog.mjs verify`.
13. No pitfall below was triggered.
14. No app-authored content border or material exists, and every app-authored
    Kotlin surface is traceable to a fill-owning design node.

Final handoff:

```text
- Container: <chosen + why>
- Window model: <chosen + why>
- Mode: <existing module update | new scaffold | incremental_patch>
- Path: <module path | output path>
- Designer gate: <passed | blocked | not_required>
- Figma MCP: <hooks_run | unavailable_rerouted_to_visual_reference | not_applicable>
- Android Studio sync: <done | user must run Sync Project with Gradle Files>
- Assumptions: <explicit list or 'none'>
- Remaining inferred/mock parts: <list>
- Verification: <verification_summary.json result, including every warning and skip>
