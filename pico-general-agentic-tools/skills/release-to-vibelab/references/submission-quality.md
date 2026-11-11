# VibeLab Submission Quality

Use this reference after the release APK is built and before the pre-add publishing review. It owns
the machine-verifiable alignment checks that improve submission quality without attempting to
replace manual content review.

## Boundary

This workflow verifies facts that can be derived from project files, the final APK, configured
metadata, or media files. It does not decide:

- advertising, cultural, policy, trademark, or other subjective copy compliance;
- whether a repository is sufficiently original or differs enough from a template or fork;
- whether named teammates or a reported AI model are truthful;
- whether every description claim has a one-to-one visual proof in a specific media item.

Generate copy only from project evidence and present metadata, feature tags, and media together in
the consolidated review. Leave subjective acceptance to the user and VibeLab reviewers.

## Technology-stack classification

Use the structured `pico-cli project detect --format json` result first. When it reports
`ambiguous`, `unknown`, or an unsupported platform, perform one bounded marker inspection:

| Evidence                                | `build.tech_stack` |
| --------------------------------------- | ------------------ |
| PICO Spatial Android SDK project        | `android_spatial`  |
| `ProjectSettings/ProjectVersion.txt`    | `unity`            |
| Exactly one `*.uproject` project marker | `ue`               |
| `project.godot`                         | `godot`            |

Do not classify from README prose or a repository name. If markers conflict, ask the user to choose
the actual build stack. If no supported marker exists, collect a truthful custom value of at most
20 characters instead of using `other` as a generic display label.

UE and Godot use the source repository as the publish root. They participate in the same metadata,
asset, GitHub, APK-manifest, preview, and submission flow. This Skill does not invent an export or
remote-build procedure for either engine; require repository instructions that identify how the
reviewed APK is produced.

## Final APK Manifest inspection

Inspect the final release APK produced from the selected build-input tree. Before the first source
commit, use the approved working tree; the later combined commit must preserve those build inputs.
An expected `app.id` write-back does not require rebuilding the APK. If code or build inputs change,
rebuild and repeat these checks before source publication. Do not substitute a source
`AndroidManifest.xml`, debug APK, stale artifact, or APK built from different source.

Prefer the Android SDK's structured manifest printer:

```bash
apkanalyzer manifest print <release.apk>
```

If `apkanalyzer` is unavailable, use the selected Android SDK build-tools `aapt2`:

```bash
aapt2 dump xmltree <release.apk> --file AndroidManifest.xml
```

Capture the process status before parsing output. A missing tool, failed command, ambiguous APK, or
unparseable result leaves APK alignment unverified and blocks Release `add`.

Extract:

- package identifier;
- `android:versionName`;
- application-level `<meta-data>` names and values used by VibeLab feature detection.

Apply this feature mapping:

| APK Manifest declaration             | Required `build.features` value |
| ------------------------------------ | ------------------------------- |
| `handtracking=1`                     | `hand_tracking`                 |
| `pico.swift.feature=1`               | `body_tracking`                 |
| `picovr.software.eye_tracking=true`  | `eye_tracking`                  |
| `picovr.software.face_tracking=true` | `expression_simulation`         |
| `enable_vst=1`                       | `mixed_reality`                 |
| `MRCsupport=1`                       | `mixed_reality_capture`         |
| `controller=1`                       | `controller_support`            |

`enable_mr_safeguard=1` may be reported as APK evidence, but it has no corresponding current
`build.features` value and must not be written as a custom feature. `avatar` is not derived from the
Manifest; include it only when explicit project evidence confirms an Avatar integration.

Require every mapped positive APK result in `build.features`. Reject a selected mapped feature when
the final APK does not declare it; correct the application Manifest and rebuild instead of changing
the field to make unsupported functionality appear available. `none` is valid only when no mapped
feature is present and Avatar is not selected.

## Version alignment

Generate `version.name` as `V<major>.<minor>.<patch>`, with `V1.0.0` for a first release. Require it
to exactly equal the final APK's `android:versionName`; changing only `vibelab.yaml` is not a repair.
For a Version Update that publishes a new build, require the proposed version name to differ from
the preceding VibeLab version name. For a metadata-only Info Update, preserve the online version
name and verify it against the corresponding APK instead of inventing a version increment.

Record the APK path as a repository-relative build result or safe basename, the extraction tool,
package identifier, version name, parsed feature declarations, and final selected feature values in
the consolidated review. Do not report the complete raw manifest.
