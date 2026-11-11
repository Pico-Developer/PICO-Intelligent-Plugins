# Publishing Metadata Collection

Read this before collecting or generating Release fields in Stage 2. It defines where field values
come from, the precedence and generation rules, and the region-language alignment constraint. The
orchestration Skill owns the timing, the write-back to one `vibelab.yaml`, the pre-add approval, and
the post-add machine-result reconciliation; this reference owns the collection policy.

## Field sources by path

The available field sources differ by initialization path:

- New app (`init` without `--from-app`): the CLI writes a local template with no remote data. There
  is no app ID and no `.vibelab/state.json` yet, so no imported remote value exists. Resolve every
  key only from explicit user-supplied values, existing project evidence, conversation context, and
  AI generation for the remainder.
- Existing remote app (`init --from-app <app_id>`): the CLI pre-fills keys from the pulled version
  and references unchanged assets as `uri:`. Treat those as imported remote values and collect only
  missing fields or user-requested changes.

## Field collection matrix

Use this per-field matrix to decide, for each `vibelab.yaml` key, who supplies the value and how the
Agent fills it in handle-everything mode. Treat an explicit user value as authoritative; use the AI
strategy only for keys the user leaves unset. The Release CLI `add` command owns the real
schema, limits, and sizes below; the specs here are collection hints, not a second source of truth.

### Application and version metadata (`vibelab.yaml` -> `app.*`, `version.*`)

| Field         | `vibelab.yaml` key | Schema contract                                                                                                                              | User-supplied source                  | Handle-everything strategy                                                                                                                                              |
| ------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| App name      | `app.name`         | Required, trimmed 1-50 chars; must identify the same application as the built/installed package and runtime UI                               | User names the app                    | Resolve from manifest/product configuration and runtime branding; generate 2-12 Chinese characters or 4-24 English/mixed-width characters that name the core experience |
| Slogan        | `app.slogan`       | Required, trimmed 1-80 chars                                                                                                                 | User writes it                        | Generate a 20-40 character scene/action plus core-benefit sentence from supported capabilities; do not repeat the app name or list features                             |
| Description   | `app.description`  | Required, trimmed 1-1000 chars; inline text, not a path                                                                                      | User provides the description text    | Generate 300-800 characters of evidence-backed Markdown: an approximately 200-character opening, 3-5 core capabilities, operation method, and use scenarios             |
| Content tags  | `app.tags`         | Required, single-select: exactly one distinct value from the selected regional Provider's `add` validation options; trimmed and deduplicated | User selects one authoritative preset | Select exactly one best-fit preset using the exact values from Provider `add` validation; do not generate free-form tags or translate the fixed values                  |
| App category  | `app.category`     | Required: `game` or `application`                                                                                                            | User selects the category             | Use `game` only for levels, scoring, win/loss, or character progression; otherwise use `application`; review it with the description and tags                           |
| Version name  | `version.name`     | Required, trimmed 1-50 chars; must equal the final APK `android:versionName`                                                                 | User sets the name                    | Use `V<major>.<minor>.<patch>`, with `V1.0.0` for the first release; verify the exact value from the final APK                                                          |
| Version notes | `version.notes`    | Required, trimmed 1-1000 chars; inline text, not a path                                                                                      | User writes the notes text            | Generate 100-300 characters in 3-6 concrete Added/Improved/Fixed items from the feature summary or actual git diff; use localized equivalents and avoid generic filler  |

Use the exact content-tag option values returned by the selected regional Provider's `add`
validation, whether Chinese or English. Preserve the returned value verbatim; do not translate it
or force its language to match the publishing copy. CN normally returns Chinese values and US/ROW
normally returns English values, but the actual returned options are authoritative. Do not reuse
another region's option list. The Provider guide's CN Chinese presets and English concept
explanations are not a cross-region enum source. For this orchestration, select from actual regional
`add` options rather than generalizing those examples. If documentation and actual validation
conflict, stop and verify the selected Provider's contract; do not bypass validation, translate,
guess, or switch region. If no authoritative option list is available, request it before selection.
Imported tags may be normalized to the first
valid preset or `other` by `init --from-app`; surface that normalization as a Provider-generated
semantic change, review the exact diff and obtain approval, preserve explicit user intent, and
request a valid selection when the previous free-form tag is unsupported. An invalid explicit
value is not permission to silently replace it with `other`.

### Build metadata (`vibelab.yaml` -> `build.*`)

| Field                        | `vibelab.yaml` key      | Works-information contract                                                                                                                                                                                               | User-supplied source                     | Handle-everything strategy                                                                                                                                                                                                                                           |
| ---------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GitHub repository URL        | `build.repo_url`        | Required effective value: canonical `https://github.com/<owner>/<repo>` without credentials or `.git` suffix                                                                                                             | Reuse or creation plan is user-approved  | Backfill the canonical credential-free URL after GitHub publication                                                                                                                                                                                                  |
| GitHub repository visibility | `build.repo_visibility` | Required: `public` or `private`                                                                                                                                                                                          | Reuse observed visibility or user choice | Preserve existing visibility; `public` may be recommended, but the `private` option must explain that non-public/proprietary/confidential source, restricted assets, or uncertainty about public distribution should use `private`; always require explicit approval |
| GitHub Commit ID             | `build.commit_sha`      | Required effective value: full 40-character SHA visible on the GitHub remote; the YAML key may be omitted only when Release resolves the same pushed `HEAD`                                                              | Not requested directly                   | Resolve after push, verify remotely, and include the full SHA in final review; never create a self-referential metadata commit                                                                                                                                       |
| Tech stack                   | `build.tech_stack`      | Required single-select: `android_spatial`, `unity`, `ue`, `godot`, or a custom string <= 20 chars                                                                                                                        | User selects or corrects it              | Use project detection plus bounded markers to select a preset; ask for a truthful custom value only when no preset matches                                                                                                                                           |
| AI IDE                       | `build.ai_tool`         | Required single-select: `Claude Code`, `Codex CLI`, `Cursor`, `GitHub Copilot`, `Trae CLI`, or custom `other` text <= 10 chars                                                                                           | User selects or corrects it              | Read from the runtime environment; ask when unavailable                                                                                                                                                                                                              |
| AI model                     | `build.ai_model`        | Required single-select, non-empty; prefer a provider candidate selected by fuzzy name match, with custom `other` only when no candidate matches                                                                          | User selects or corrects it              | Match the observed model against provider candidates without inventing one; ask the user to confirm the match or `other` value                                                                                                                                       |
| Feature tags                 | `build.features`        | Required, at least 1 item from `body_tracking`, `hand_tracking`, `eye_tracking`, `expression_simulation`, `avatar`, `mixed_reality`, `mixed_reality_capture`, `controller_support`, `none`; `none` is mutually exclusive | User selects from the fixed option set   | Preselect only capabilities supported by explicit project evidence; ask about uncertain values and include them in review                                                                                                                                            |
| Teammates                    | `build.teammates`       | Optional, 0-3 unique strings, each <= 10 chars; Discord teammate names are allowed                                                                                                                                       | User lists participating teammates       | Preserve imported values; otherwise default to `[]`                                                                                                                                                                                                                  |

### Publishing assets (`vibelab.yaml` -> `app.*`)

| Field              | `vibelab.yaml` key    | Schema contract                                                                                                                                  | User-supplied source                                                                                                                              | Handle-everything strategy                                                                                                                                                                                                                                                                |
| ------------------ | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| App icon           | `app.icon`            | Required local path or `uri:` reference; this workflow requires JPEG with a `.jpg` or `.jpeg` extension; exactly `1024x1024`; <= 4 MB            | Use the application-provided launcher icon as the authoritative source; if needed, the user supplies a compliant review file based on that source | If the source is already compliant, select or copy it unchanged; otherwise ask the user to provide a compliant JPEG file with a `.jpg` or `.jpeg` extension or explicitly authorize the Agent to prepare a compliant review file from the same source; never generate or redesign artwork |
| Landscape poster   | `app.landscape`       | Required local path or `uri:` reference; `.jpg`, `.jpeg`, or `.png`; exactly `2560x1440`; <= 5 MB                                                | User places a runtime-capture-based poster under `<publish-root>/assets/`                                                                         | Capture the running app on an emulator/device and prepare one poster from that capture; include it in the review                                                                                                                                                                          |
| Detail screenshots | `app.detail_images[]` | CLI schema allows 1-7; this workflow targets 4-6 local paths or `uri:` references; `.jpg`, `.jpeg`, or `.png`; exactly `2560x1440`; <= 5 MB each | User places 4-6 confirmed emulator/device runtime captures under `<publish-root>/assets/`                                                         | Route actual running-app capture to the installed platform provider; default to 5 distinct images; never use `.scratch/`, previews, or mockups; review every image                                                                                                                        |
| Detail video       | `app.videos[].file`   | Optional in the CLI schema, 0-3 local paths or `uri:` references; `.mp4`; <= 100 MB each                                                         | User supplies an accepted 30-60 second `publish_video` under `assets/`, or chooses skip                                                           | Recommend one video and ask separately after required images; derive `publish_video` from `raw_publish_recording`, or accept the exact user-supplied publish file; never map intermediate recordings                                                                                      |
| Video cover        | `app.videos[].cover`  | Required for each video; local path or `uri:` reference; `.jpg`, `.jpeg`, or `.png`; exactly `2560x1440`; <= 5 MB                                | User supplies `publish_video_cover` from a frame inside the accepted publish video segment                                                        | Extract a real frame inside the exact corresponding `publish_video`; never use an out-of-segment frame or design intermediate; include every cover in the review                                                                                                                          |

New or redesigned icon artwork remains outside this Skill. The application-provided launcher icon
is the authoritative source. A format or dimension conversion is allowed only after explicit,
icon-specific user authorization and must preserve the source artwork and visible composition; the
normal `agent-prepared` runtime-media choice does not grant that authorization. Runtime screenshot
and video preparation is part of the release orchestration only when the approved plan uses
`agent-prepared` mode. In `user-supplied` mode, do not check or launch an emulator or physical
device; wait for the named files and validate their explicit runtime-origin confirmation. Switch an
individual missing or invalid runtime-media asset to Agent preparation only after explicit user
approval. Agent-prepared capture must use a matching installed platform Skill or the supported
`pico-cli capture` command. Read the asset-guidelines reference before reviewing any asset.

`app.description` and `version.notes` are inline text fields: write the finalized copy directly
into `vibelab.yaml` (the same way as `app.name` and `app.slogan`). A drafting Markdown file is only
a review convenience; never set these keys to a file path. Asset references belong only in
`app.icon`, `app.landscape`, `app.detail_images[]`, `app.videos[].file`, and
`app.videos[].cover`. Video provenance roles are orchestration-only, not schema extensions. Only the
`publish_video` and `publish_video_cover` roles map to `app.videos[].file` and
`app.videos[].cover`; `video_for_stills` and `raw_publish_recording` never map to Release fields and
remain outside `<publish-root>/assets/`.

## Precedence and generation rules

Apply these rules while filling the keys present in the generated `vibelab.yaml`:

1. Preserve every explicit user-supplied value. User choices override generated suggestions unless
   they violate an actual Release CLI validation rule.
2. Resolve required keys from the initialized config, existing project evidence, imported remote
   values, and conversation context. Collect only required decisions that remain unknown and cannot
   be safely inferred. For a new app there are no imported remote values, so unknown required keys
   come from project evidence or the user. Ask those minimum necessary questions together in one
   batch; do not ask one question per field or ask for facts already available.
3. `app.videos` is optional. Confirm the required icon, poster, and 4-6 detail images first, then
   recommend one video and ask one separate question with three choices: Agent-prepared 30-60
   second key-interaction video and dedicated cover; user-supplied runtime video and dedicated
   cover; or skip video. A verified device recording-capability absence also skips video. For
   included video, the user supplies the exact `publish_video` and `publish_video_cover` files in
   `user-supplied` mode; the Agent creates a `raw_publish_recording`, then derives and validates the
   two publish roles only in `agent-prepared` mode. Skip means `app.videos: []`. A separately approved
   `video_for_stills` remains intermediate and does not change that publishing decision.
4. When the user asks the Agent to handle everything, generate only missing publishing fields from
   the current project evidence and conversation context. Do not replace known facts or fabricate
   unsupported product claims.
   Apply the review-target lengths and structures in the field matrix to generated values. These are
   generation rules, not additional schema limits for user-supplied values.
5. Resolve the required language only from the catalog's selected region:
   - `cn`: the application's default or primary runtime UI and publishing copy must be Chinese.
   - `us` or `row`: the application's default or primary runtime UI and publishing copy must be
     English.

   Explicit user preference does not override this mapping. A language switcher is acceptable only
   when the mapped language is the default or primary experience for this release. Unknown or
   mismatched runtime language blocks publication until the application is localized or the user
   switches to the intended region with `pico-cli setup --region`.

6. Collect all AI-generated names, slogans, descriptions, tags, version notes, and other publishing
   copy into the consolidated pre-add publishing review. Show field, language, proposed value, and
   evidence source together with the user-supplied and imported values.
7. Let the user request regeneration of individual fields before approval, then update the same
   pre-add review. Do not interrupt generation with one confirmation per field, and do not request a
   separate approval for the generated subset.
8. Ask once for approval of the complete pre-add publishing intent. Only after that approval may the
   Agent write AI-generated copy to `vibelab.yaml` or execute a mutating Release command.
   User-provided and imported remote values remain distinguishable from generated values.

## Pre-add publishing review

Before the first Release write, show every user-supplied and AI-generated publishing field, asset,
repository identity, platform result, selected region, required language, runtime-language
evidence, and application-identity evidence. For each selected asset, show one of these
plain-language review labels, not new `vibelab.yaml` fields:

- user supplied;
- Agent prepared this run;
- retained remote `uri:` asset;
- derived from another approved asset, naming that source asset.

These labels describe how the selected file entered the release review; they do not prove that the
asset matches a Git SHA, APK hash, or source version. Do not require Git-SHA or APK-hash binding, and
do not block solely because an origin or source version is unknown. If the source is unknown, say so
plainly rather than inventing a label. Ask: "Confirm that the selected assets are suitable for this
release." Let the user continue using them, replace them, or ask the Agent to prepare them again.
Only the user's selection changes the approved asset set; no label automatically accepts or rejects
an asset.

For a first release, mark app ID, version ID, and the one final post-`add` Commit ID as pending
machine-derived values. Require explicit approval and read-only Git transport readiness before
Release `add`; do not create or push a preliminary source commit. After `add` writes `app.id`,
reconcile the result and approved content before the single Git commit/push.

## Preserve first-release identity and resume

At entry, classify a new allocation only when config and local state have no trusted app ID;
unreadable or conflicting state is a blocker, not permission to create another app. Preserve that
first-release classification and the initial `created_draft: true` app/version evidence throughout
the run. `add` writing IDs does not change the release intent. Corrected validation inputs may
require same-ID `add` again: expect `created_draft: false`, verify the same app/version, and retain
the initial-draft proof. Never require a second allocation to refresh that proof.

After interruption, use trusted config/state IDs, Release `state`, and Git/remote observations to
reconstruct the never-online editable initial draft and whether its source commit/push is pending.
Do not classify by app-ID presence alone. With matching IDs, no online version, and an editable
initial draft, retain the draft-first path; complete content/source checks and resume the pending
Git commit/push without re-allocating or requiring a preliminary remote SHA. If the reviewed
source/config commit is already pushed, reuse it rather than making another commit. Preserve the
initial `created_draft` result when available; otherwise the matching persisted and remote initial-
draft evidence reconstructs the proof. Do not forge a new `created_draft: true` result or a new
state file. Missing or ambiguous proof stops at read-only investigation, not another `add`.
The Provider does not persist `created_draft` as an allocation-history field; do not invent one.
Reconstruct the approved publishing intent as well as matching IDs and initial-draft state; a
never-online status or `version_update` mode alone is insufficient. If the previous approval cannot
be established, obtain approval of the current exact intent before the next write. Distinguish:

- no reviewed source/config commit yet: complete checks and make the combined commit;
- reviewed commit exists locally but is not pushed: resume that ordinary push, not a new commit;
- the exact reviewed commit is already remote: verify it and reuse it;
- ambiguous IDs, draft, commit contents, or transport outcome: inspect read-only and stop mutation.

For existing-app reconciliation, retain its selected pre-`add` pushed revision and update intent.
Do not infer that an app with a trusted ID and online history qualifies for first-release recovery.

## Post-add machine-result reconciliation

After Release `add` has persisted the app ID, but before the first-release Git commit, reconcile
the machine-derived result against the approved pre-add review. Report:

- durable app ID, version ID, `created_draft`, canonical GitHub repository URL, and observed
  visibility; the final pushed Commit ID is still pending until the single source commit;
- agreement between `vibelab.yaml`, `.vibelab/state.json`, and the app/version IDs returned by
  Release `add`; its provisional SHA is not final source-readiness evidence;
- any unexpected tracked mutation produced by `add`;
- the semantic diff against the approved pre-add review, covering publishing fields, assets,
  repository identity or visibility, platform result, region/language evidence, application
  identity, and review-risk decisions.

Do not ask the user to approve unchanged publishing fields again. If the semantic diff is empty and
machine-derived values reconcile, record the result and continue to the single source commit without
another content approval. If the semantic diff is non-empty, show only the exact changed values,
evidence, and consequences, and require explicit approval only for that diff. A rejected diff returns
to correction; finish approved corrections before staging, rerunning `add` with the same trusted app
ID only when its validation inputs changed. Do not write the resolved SHA into the commit it
identifies. On a first release, keep `build.commit_sha` omitted through `add` and the single source
commit so Release `commit` resolves the final pushed `HEAD`.

After Git push, report the final full Commit ID and require matching local/remote SHA evidence,
matching app/version IDs, and a clean tracked worktree before Release `commit`. Do not repeat `add`
or create a second Git commit merely to refresh its earlier SHA. If a required correction happens
after the push, obtain approval for the exact diff and publish that correction with fresh SHA
verification; the normal-path one-push target never bypasses recovery or source-readiness gates.

Apply these delivery checks during pre-add approval and re-run them after `add` only when their input
or evidence changed:

- require `cn` releases to use Chinese and `us` / `row` releases to use English in both the
  application's default or primary runtime UI and publishing copy;
- reject an application name that names a different product, conflicts with the manifest/product
  configuration, or is not recognizable in the running app;
- compare the publishing icon with its authoritative application-provided source, the
  built/installed launcher icon, runtime branding, and package identity; block a machine-invalid
  file, but for a manual-review discrepancy follow the asset-guidance decision gate and continue
  only after explicit rejection-risk acceptance;
- require unique content hashes and pairwise visual review for all selected images; reject exact
  duplicates and near-duplicate frames even when their file names, crops, overlays, or formats
  differ;
- Android Spatial: require a successful package-validation result from the matching platform
  workflow.
- Unity: require the completed Android conversion and its APK validation report.
- UE or Godot: include the bounded marker evidence and verify the repository documents how the
  reviewed APK is produced.
- custom stack: state that no preset matched and verify the GitHub repository documents how users
  can obtain the installable package.

## Region-language alignment

Use runtime UI evidence from the selected target in `agent-prepared` mode. In `user-supplied` mode,
require explicit user confirmation plus matching runtime-media evidence. Translating only
`app.description`, `version.notes`, or other metadata does not resolve a runtime mismatch. Block
Release `add` until both the application experience and publishing copy match the selected region.
