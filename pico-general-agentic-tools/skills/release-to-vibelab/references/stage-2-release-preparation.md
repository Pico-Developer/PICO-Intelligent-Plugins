## Stage 2 - Prepare configuration, assets, and GitHub

### Resolve the publish root

Use the project-detection result from Stage 0 and the bounded marker fallback from
[references/submission-quality.md](submission-quality.md). Map Spatial to
`android_spatial`, Unity to `unity`, an Unreal project marker to `ue`, and a Godot project marker to
`godot`.

- PICO Spatial (`platform = spatial`): keep the source project as the publish root and set
  `build.tech_stack = android_spatial`.
- Unity (`platform = unity`): read [references/unity-android-export.md](unity-android-export.md) and run the
  bundled export scripts under `$SKILL_DIR/scripts/`. The export requires Windows or macOS, PICO
  XR, and a separate approved target Git repository. Run the preflight, obtain target-replacement
  approval, then complete the verified export. Set the resulting target repository as the publish
  root and set `build.tech_stack = unity`.
- UE or Godot: keep the source project as the publish root, set `build.tech_stack` to `ue` or
  `godot`, and require repository instructions that identify how the reviewed release APK is
  produced. Do not invent an engine export procedure.
- Any other unresolved classification: keep the source project as the publish root, collect one
  truthful custom `build.tech_stack` value of at most 20 characters, and skip platform-specific
  conversion.

For Unity, stop when the host is unsupported, preflight fails, or the export cannot prove its
required result. Do not fall back to publishing the Unity source repository as if it were the
exported Android repository.

Read [references/source-build-readiness.md](source-build-readiness.md) now. Before GitHub
publication, require Android Spatial package validation and the Unity APK validation report, then
require every Gradle publish root to pass the reference's repository, toolchain, Editor-artifact,
and isolated-resolution gates. Block GitHub publication and Release `add` for private, internal, or
machine-local Maven state, build-time Node or undeclared tools, or build-time Spatial Editor. For
UE, Godot, or a custom stack, apply the gate when Gradle is present; otherwise require
installable-package documentation and a final release APK for the submission-quality checks.

After this point, run every Release, GitHub, and Git operation in the resolved publish root. Store
`vibelab.yaml`, `.vibelab/` state, and publishing assets there. The Unity source project remains
separate and must not receive the target repository's Release state.

Read the `pico-release-cli` provider Skill before the first Release invocation. Keep its JSON, state,
and failure rules authoritative for every later Release call.

### Initialize or import configuration

Do not collect or invent Release configuration keys before initialization. The installed Release
CLI owns the schema and creates the authoritative field inventory.

When `vibelab.yaml` is absent for a new app, run:

```bash
<pico-release-cli> --json init
```

For an existing remote app without local configuration, run:

```bash
<pico-release-cli> --json init --from-app <app_id>
```

Add `--force` only when the user explicitly approves overwriting an existing `vibelab.yaml`.
`init --from-app` also initializes `.vibelab/state.json` and uses `uri:` references for unchanged
remote assets. `init` already appends `.vibelab/` to `.gitignore` (creating the file when absent);
never add a second `.vibelab/` entry by hand. `vibelab.yaml` is release source, not local state:
never add it to `.gitignore`, and always include it in the release commit.
Root `assets/` is local publishing input: require `/assets/` in the publish root's `.gitignore`,
keep it out of the Git index, and preserve its working-tree files.

After initialization, parse the exact config file created by the CLI and use its keys as the
collection checklist. The current `<pico-release-cli>` contract creates
`<project-root>/vibelab.yaml`; do not relocate it to `VibeLab/vibelab.yaml` or create a parallel
manifest. If a future provider version returns a different config path, use that returned path
instead of guessing.

For an existing `vibelab.yaml`, preserve its schema and values and collect only missing fields or
user-requested changes. Every collected or generated Release field must be written back to this one
authoritative config file before validation. Do not store Release field values in notes, sidecar
JSON, asset references, or orchestration state.

### Prepare assets

- Follow the approved asset-preparation mode before device discovery, launch, or capture:
  - In `user-supplied` mode, do not discover, check, start, or require an emulator or physical
    device. Name the required files, confirm runtime origin, and validate them when available.
  - In `agent-prepared` mode, resolve a compatible target and matching installed provider, then
    prepare only the assets named in the approved plan.
  - For a missing or invalid user-supplied runtime-media asset, report the exact replacement and keep
    waiting unless the user explicitly switches it to `agent-prepared`; only then perform the device
    checks for that delegated asset. Agent-prepared runtime-media mode does not authorize
    application-icon conversion; that requires a separate, icon-specific choice below.
- Use `<publish-root>/assets/` as the only local publishing-asset directory. For Unity this is in
  the exported Android repository. Tell users to place supplied files there, using names such as
  `icon.jpg`, `landscape.png`, `detail-1.png` through `detail-5.png`, `demo.mp4`, and
  `demo-cover.png`.
- Treat root publishing `assets/` as local-only upload input. Never stage it. This does not apply to
  source-controlled application resources such as `app/src/main/assets/`.
- Require 4-6 entries in `app.detail_images[]`, defaulting to five. Retained `uri:` references count
  toward the selected total; prepare or request the remaining distinct runtime images instead of
  duplicating an existing image.
- Never discover, select, copy, or convert a publishing asset from `.scratch/`, hidden design
  directories, previews, mockups, design evidence, or intermediate outputs; never configure those
  paths in `vibelab.yaml`.
- Retain unchanged `uri:` assets imported by `init --from-app`.
- Treat the application icon as user-controlled and use the application-provided launcher icon as
  the source. If it already satisfies the required JPEG format, `.jpg` or `.jpeg` extension,
  dimensions, and size, select it or copy it byte-for-byte under `assets/`. If it is machine-invalid,
  stop and offer exactly two choices: the user provides a compliant review file based on that source,
  or the user gives explicit, icon-specific authorization for the Agent to convert or resize that
  source into a compliant review file under `assets/`; never overwrite the application's source
  icon. An authorized preparation may change only encoding, file extension, dimensions, and
  compression needed by the machine contract; preserve the artwork, identity, visible composition,
  aspect ratio, padding, and color intent. Never generate, crop, pad, redraw, recolor, add or remove
  content, or repair manual-review risks. After either path, rerun the
  full icon validation. If the resulting file has an advisory manual-review risk, ask whether the
  user will replace it and rerun validation or explicitly accept the stated rejection risk and
  continue with the exact reviewed file. Never default to conversion or risk acceptance. A
  machine-invalid icon cannot continue to Release `add`.
- The product view in `app.landscape`, `app.detail_images[]`, `app.videos[].file`, and
  `app.videos[].cover` must originate from the actual running application on a selected online
  emulator or physical device. User-supplied landscape, detail, video, and cover files are accepted
  only under `assets/` with explicit runtime-origin confirmation. Apply the same gates to `other`.

Only in `agent-prepared` mode, launch the application on the selected target and route missing-image
capture to the matching installed platform screenshot provider. If none can validate the correct
mode, report a blocker instead of guessing or using an intermediate. Require target type, device
ID, mode, dimensions, and a verified path under `assets/`. For runtime media, conversion may
change dimensions and format, but not the captured application content. This runtime-media
permission does not grant icon-conversion permission; icon conversion requires the separate,
explicit, icon-specific authorization above.

For `platform = spatial`, generate Agent-prepared multi-angle detail screenshots as follows:

1. Classify the running content before moving the camera:
   - For a Stage or volumetric experience with one stable focal subject, load the user-level
     general plugin's `capture-camera` Skill. It owns fresh-frame subject grounding, bounded lateral
     and vertical probes, typed camera plans, composition refinement, screenshot validation, and
     camera reset.
   - For a window application, keep the window directly in front of the viewer and use the platform
     screenshot provider to capture distinct meaningful runtime states. Do not create variety by
     showing a planar window edge-on or from behind.
   - For passthrough or mixed-reality content whose physical-camera view would not follow injected
     virtual Pose, do not use target-relative multi-angle capture. Use validated current-view runtime
     screenshots or keep the delegated asset blocked.
2. Capture the approved 4-6 distinct detail images. For Stage or volumetric content, use the
   viewpoints named in the approved plan. When none were specified, use this ordered five-image
   default: prepared front, front-left at 35 degrees, front-right at 35 degrees, elevated front, and
   lowered front. This is a bounded set, not an automatic six-face or 360-degree set. Window
   applications and passthrough or mixed-reality content must instead provide the approved number
   of distinct meaningful runtime states or current-view moments under the classification above.
3. Ground either the named focal subject or "the whole App" from fresh frames according to
   `capture-camera`; never derive the target from the package name or guess world coordinates.
   Keep probe frames, plans, and other targeting evidence outside the publish root. Write only the
   selected final screenshots to `<publish-root>/assets/`, using distinct paths such as
   `detail-1.png` through `detail-5.png`.
4. Inspect every captured view before conversion. Require the same intended subject, complete
   visible content, readable scale, stable framing, and a material viewpoint or runtime-state
   difference from the other selected images. Follow `capture-camera` refinement and retry rules
   when composition is recoverable. If a requested slot still fails or duplicates another view,
   report that file as missing; do not fill it with a copied, cropped, or near-duplicate image.
5. Reset the camera and verify cleanup after success, cancellation, or failure. Then convert only the
   accepted runtime screenshots to the required `2560 x 1440` outputs without replacing or
   synthesizing their application content. Record each final path, viewpoint or runtime state,
   target type, device ID, capture mode, dimensions, and runtime provenance.

This multi-angle route changes screenshot preparation only. Do not add camera motion to VibeLab
videos through this provider in this workflow; keep the existing recording path below until a
separate video-quality contract is adopted.

Resolve video in a separate optional question. Use these orchestration-only roles, not
`vibelab.yaml` keys:

- `video_for_stills`: a temporary runtime recording used only to extract approved poster or detail
  frames. Keep it outside `<publish-root>/assets/`; never map it to `app.videos[]`.
- `raw_publish_recording`: the session-owned source recording for a requested published video. It may
  include setup, cleanup, or pauses. Keep it outside `<publish-root>/assets/`; never map it directly
  to `app.videos[]`.
- `publish_video`: the validated continuous 30-60 second output derived from an accepted
  `raw_publish_recording`, or the exact accepted user-supplied publish file. Place it under
  `<publish-root>/assets/`. Only `publish_video` may map to `app.videos[].file`.
- `publish_video_cover`: a validated frame that occurs inside the exact corresponding
  `publish_video` segment. Place it under `<publish-root>/assets/`. Only `publish_video_cover` may
  map to `app.videos[].cover`.

Then apply these decisions:

- Ask only after the required icon, landscape poster, and 4-6 detail images are confirmed. Recommend
  including at least one video, then offer exactly three choices: Agent-prepared 30-60 second
  key-interaction video plus dedicated cover; user-supplied runtime video plus dedicated cover; or
  skip video.
- If the user chooses skip, record that decision and set `app.videos` to `[]`. A separately approved
  `video_for_stills` may still produce static assets, but it must not change that skip decision or
  enter `app.videos[]`. If temporary recording was not part of the approved still-capture plan, do
  not infer permission to record it. Also skip publication when a capability check proves that the
  selected device cannot record the required demonstration.
- In `user-supplied` mode, tell the user to provide both the requested runtime recording and its
  runtime-derived cover; require the accepted segment to be 30-60 seconds and do not inspect or
  launch a device.
- In `agent-prepared` mode, execute the scenario and ordered visible action sequence from the
  approved video choice with a target duration of 30-60 seconds. Do not seek another confirmation
  unless that choice must change. Before changing application state, validate the executable
  selected by `PICO_CLI_FFMPEG`, or `ffmpeg` from `PATH`, with `ffmpeg -version`. If unavailable,
  stop and present only these choices: configure an existing executable through `PICO_CLI_FFMPEG`;
  use a verified temporary binary outside the project; approve a persistent platform install
  (`brew install ffmpeg` on macOS or `winget install --id Gyan.FFmpeg --exact` on Windows); provide
  a runtime video and cover; or change the video choice to skip. Never install automatically. A
  persistent install must appear in the approved plan and receive explicit confirmation. Re-run the
  version check before any application action or `record start`; if it still fails, do not record.

  For an interactive Spatial scenario, load the configured platform's `spatial-accessibility` Skill
  and require its current inventory, Contract, build, and zero-error project/runtime audit gates. If
  those gates require source or Contract changes, obtain its one combined approval before editing or
  operating the application. Plan at least two distinct, meaningful, Contract-declared
  state-changing actions whose visible outcomes explain the core experience; never invent selectors
  or broaden actions for a more active-looking video. For other platforms, use only their installed
  workflow's declared interaction mechanism or user-assisted interaction. A genuinely passive
  scenario must show material animation or progression instead of fabricated actions.

  Start one session-owned recorder before the first action, perform the approved action sequence,
  then stop that same session:

  ```bash
  pico-cli capture record start --session <recording-session-id> --device <id> \
    --out <temporary-recording-path>/raw-publish-recording.mp4 --time <maximum-seconds> \
    --format json
  # Perform the approved Contract-declared actions through the installed platform workflow.
  pico-cli capture record stop --session <recording-session-id> --format json
  ```

  `record start` must report that recording is ready before any action. Always attempt `record stop`
  for the same session after success, action failure, cancellation, or timeout; a failed action or
  stop rejects that recording instead of silently publishing a partial flow. Never substitute the
  blocking `pico-cli capture record --time` form when the approved scenario requires interaction.

  Verify the `raw_publish_recording` MP4 exists and is readable, then inspect the beginning, the
  visible result after every planned action, and the end. Reject an interactive recording with no
  meaningful action, near-identical idle frames, only timer movement, or outcomes that do not match
  the Contract. Select one continuous bounded publishing segment lasting 30-60 seconds without
  reordering events or synthesizing application content, then write that segment as a separate
  `publish_video` under `<publish-root>/assets/`; never overwrite a user-supplied file. Verify the
  final file independently. Capture or extract `publish_video_cover` from a frame inside that exact
  accepted segment and write it under `<publish-root>/assets/`; do not use a frame outside the final
  segment or a design image. Record the source path, selected time range, output paths, and hashes.

- In `agent-prepared` mode, if no emulator or physical device can run the application, report a
  runtime-media blocker. Never fall back to `.scratch/` or another intermediate source.
- If the selected device can run the application but a checked device capability cannot record the
  required demonstration, report that evidence and skip video publication. Missing FFmpeg, an
  unavailable provider, or a failed recording/action is not proof that the device lacks capability
  and must not silently remove video from the approved plan.
- Clean session-owned intermediate recordings after their derived assets pass validation, unless an
  approved evidence policy requires retention outside the publish root. Never delete or overwrite a
  user-supplied source video. On failure or cancellation, report and clean only Agent-owned temporary
  files; no intermediate file becomes a publishing asset by fallback.

Read the asset-guidance reference, review selected assets against it, then populate `vibelab.yaml`
only from project evidence, user-provided facts, imported remote values, or the approved plan.

Before reporting readiness, derive the exact asset set from `vibelab.yaml` and the approved plan.
Require 4-6 configured detail images, then require every path and command result, exact counts,
dimensions, sizes, and runtime provenance from the selected target or explicit user confirmation.
Review the publishing icon against its authoritative application source and the built/installed app
identity, then apply the icon decision gate in the asset guidance; reject exact or visual
near-duplicate images. Do not infer completion from a
glob, subset, or intended output path. Report blockers and only the verified subset. Release `add`
remains the authoritative validation before upload.

### Configure publishing metadata

After `init` or `init --from-app`, collect and generate the keys present in the generated
`vibelab.yaml`, before GitHub publication. Read
[references/publishing-metadata.md](publishing-metadata.md) for the field sources by
path, the precedence and generation rules, and the region-language alignment constraint.

Write every collected or generated value back to the one authoritative `vibelab.yaml`. Do not
write AI-generated copy or run a mutating Release command until the user approves the single
consolidated review. After approval, write the values; the later Release `add` command owns
authoritative length, format, asset, Git, and cross-field checks. When `add` fails, present the
structured issue and regenerate or edit only the affected field before returning to the review.

### Validate submission quality and the final APK

Read [references/submission-quality.md](submission-quality.md). Parse the final release
APK produced from the selected build-input tree (the approved working tree before the first
source commit), require `version.name` to equal its
`android:versionName`, and reconcile `build.features` with the APK Manifest mapping. A missing,
stale, ambiguous, or unparseable APK blocks GitHub publication and Release `add`.

Keep subjective copy compliance, repository originality, teammate identity, and AI-model
truthfulness outside this automated gate. Present generated metadata, parsed APK facts, selected
feature tags, and media together for user review without claiming that the Agent replaces VibeLab
manual review.

### Validate region-language alignment

Use the top-level `region` from the catalog query as the only language mapping:

- `cn` -> Chinese;
- `us` or `row` -> English.

Require the application's default or primary user-facing runtime UI and all publishing copy written
to `vibelab.yaml` to use that language. In `agent-prepared` mode, inspect the running application on
the selected target. In `user-supplied` mode, require explicit user confirmation and matching
runtime-media evidence. A language switcher is acceptable only when the mapped language is the
default or primary experience for this release.

Unknown or mismatched application language blocks GitHub publication and Release `add`. Do not
translate metadata alone to mask a runtime mismatch. Localize the application, or switch to the
intended region through `pico-cli setup --region`, then repeat runtime and publishing-copy
validation.

### Prepare and publish GitHub source

GitHub API authentication and Git transport are separate gates for both public and private
repositories. The API gate uses `gh`; the transport gate uses the selected Git remote protocol. A
public repository still requires authenticated write access. Public skips the later Deploy Key
stage; private requires a verified read-only key. Resolve and record the intended target branch without assuming `main`: use an explicitly approved
branch, otherwise an observed existing remote branch, otherwise the current local branch for a new
repository. A first release does not require a local commit at this checkpoint. For an existing
linked app, preserve the selected full source SHA and update intent. Read and normalize an existing
`origin` without credentials. Never silently replace or rewrite an existing `origin`; stop for
approval when it identifies another owner or repository.

Inspect the intended repository before creation:

```bash
gh repo view <owner>/<repository> --json nameWithOwner,url,visibility,defaultBranchRef
```

Only an explicit `NOT_FOUND` result proves that creation is appropriate. Authentication,
authorization, network, protocol, or malformed-response failures are not absence and must stop the
flow. For an existing repository, preserve its observed visibility and do not propose changing it
merely to simplify publication. If no repository exists, ask whether the source has a
confidentiality requirement. When it does not, recommend `public` because it avoids Deploy Key
setup; when it does, recommend `private`. A recommendation is not consent: create the repository
only after the user explicitly approves owner, name, and `public` or `private` visibility.

The visibility question must explain source-disclosure risk, not only build mechanics:

- `Public`: it may be marked as recommended. State that anyone can view the repository, it is
  suitable when the source, publishing assets, and third-party licenses permit public
  distribution, and no Deploy Key is required.
- `Private`: tell the user to choose it for non-public source, proprietary or confidential
  information, restricted assets, or uncertainty about whether the project may be public. State
  that VibeLab requires a verified read-only Deploy Key.

The Private option description must include both the confidentiality criteria and the Deploy Key
requirement. Never infer permission to publish from project contents or choose visibility on the
user's behalf.

```bash
gh repo create <owner>/<repository> --source=. --private --remote=origin
gh repo create <owner>/<repository> --source=. --public --remote=origin
```

Do not combine repository creation and source upload with `--push`; keep creation, transport
verification, push, and readback as separate auditable stages. After creation, repeat `gh repo view`
and require the returned identity and visibility to equal the approved values. Re-read `origin` and
require it to identify that same credential-free repository.

Write the canonical credential-free repository URL without a `.git` suffix and the observed
visibility to `vibelab.yaml`. Keep `build.commit_sha` omitted through first-release `add` and the
single source commit; Release `commit` resolves the final local `HEAD`. Never write a SHA
into the commit it identifies, or set an empty or synthetic placeholder. For an existing linked
app, preserve any explicit source pin and the metadata-versus-code update intent; this optimization
does not change the existing-app SHA selection policy.

Fix the first-release classification before `add`; preserve its initial-draft proof across
corrections and resume using `publishing-metadata.md`. IDs written by `add` do not make it a later
release. Before the first Release write, show the pre-add
publishing review from `publishing-metadata.md`: include every user-supplied and AI-generated field,
asset, repository identity, platform result, selected region, required language, runtime-language
evidence, and application-identity evidence. For each selected asset, show the plain-language origin
from that reference and ask the user to confirm that it is suitable for this release. Do not add
origin fields to `vibelab.yaml`, require Git-SHA or APK-hash binding, or make an unknown source an
automatic blocker. On a first release, app ID, version ID, and the one final post-`add` Commit ID
are still pending at this checkpoint. There is no preliminary source commit to approve.
Block Release `add` when the application name does not match the built/installed app, when runtime
and publishing language do not match the selected region, or when selected images are exact or
visual near-duplicates. A machine-invalid icon also blocks `add` until the user supplies or
explicitly authorizes preparation of a compliant review file and validation passes. For an icon with
only a manual-review risk, do not alter it to hide the risk: continue with the exact reviewed file
only after the user explicitly accepts the stated rejection risk. Continue only after explicit
approval.

Before staging, pass the redaction reference's mandatory `.pico-env.json` and root publishing
`assets/` ignore gates without reading `.pico-env.json` contents, then run repository content
screening across the approved commit paths. Review likely personal or development API keys,
credentials, private-key material, credential-bearing URLs, and politically sensitive content. Consolidate findings without
showing matched values. When a finding is not safely ignored, obtain the user's decision before
editing `.gitignore`, changing the Git index, retaining the file, or continuing. Never silently
modify or silently allow a finding. `vibelab.yaml` is not eligible for the ignore option; repair any
unsafe content inside it instead.

For public repositories, follow the [source path gate](source-build-readiness.md#public-source-path-gate) before staging and each push.

After the screening decision, require `git ls-files -- assets` to return no paths. For a first
release, do not create or push a preliminary Git commit before `add`. Defer staging until `add`
has written `app.id` and its result has been reconciled, so the source and final configuration enter
one commit together. For an existing linked app, retain the selected source commit/push before
Release `add`; do not apply the first-release omission of an explicit SHA to an existing source pin.

A host IDE or editor may inject an askpass proxy (`GIT_ASKPASS`, `SSH_ASKPASS`,
`VSCODE_GIT_ASKPASS_*`, `VSCODE_GIT_IPC_HANDLE`) that hijacks Git authentication. This affects both
public and private repository writes. Classify `origin` before any network Git command:

- For HTTPS remotes on `github.com`, clear the injected askpass variables and run every read-only
  transport check, push, retry inspection, and remote-SHA readback through the same process-scoped
  `gh` credential helper. Do not run `gh auth setup-git` by default or otherwise persistently mutate
  the user's Git configuration. It is an optional repair only after explicit user authorization.
- For SSH remotes, do not inject an HTTPS credential helper and do not silently rewrite the remote
  to HTTPS. Perform the same read-only transport, push, and SHA gates through SSH; report SSH key or
  host-verification failures as SSH transport failures.
- Reject unsupported or ambiguous remote protocols instead of guessing.

Prefer a process API with an argument array and a child environment that removes the askpass
variables on macOS and Windows. The following POSIX form illustrates the required HTTPS semantics;
it is not permission to rely on shell quoting where a process API is available:

```bash
unset GIT_ASKPASS SSH_ASKPASS VSCODE_GIT_ASKPASS_NODE VSCODE_GIT_ASKPASS_MAIN \
  VSCODE_GIT_ASKPASS_EXTRA_ARGS VSCODE_GIT_IPC_HANDLE
git -c credential.helper= -c credential.helper='!gh auth git-credential' -c core.askPass= \
  ls-remote origin
git -c credential.helper= -c credential.helper='!gh auth git-credential' -c core.askPass= \
  push -u origin "HEAD:<target-branch>"
git -c credential.helper= -c credential.helper='!gh auth git-credential' -c core.askPass= \
  ls-remote origin "refs/heads/<target-branch>"
```

Run the read-only transport check before Release `add` and the first push after repository creation
or selection. A new empty repository may return no refs with exit status zero; that proves read
transport readiness, not authenticated write access or a pushed source SHA. Only the later successful
push plus remote readback establishes source readiness. Capture each command's status and bounded
output independently. Never pipe a Git, `gh`, or Release command whose
result controls the workflow, and never append another command before capturing its exit status.
Run the command through a process API that returns the status separately, or follow the redaction
reference's POSIX shell or PowerShell capture pattern. Do not recover it through Bash-only `PIPESTATUS`,
zsh-only `pipestatus`, `$?` after a pipeline, or delayed
PowerShell `$LASTEXITCODE`.

After each push, parse the independently captured `ls-remote` output and require exactly the expected
`refs/heads/<target-branch>` entry. Require the full 40-character local and remote SHAs to match
exactly. A zero push status without that readback is insufficient. An exit code such as 128 is a
generic `GIT_TRANSPORT_FAILED` result, not proof of a missing credential helper. Preserve the real
exit code and only attach a bounded, redacted `inferredCategory` when stderr evidence supports it;
classify authentication, authorization, network, remote-not-found, remote-conflict, SSH, and SHA
mismatch separately. Retry only a clearly transient network failure.

Before first-release `add`, require approved publishing intent, content screening, verified repository identity/visibility, and protocol-specific read
transport readiness. With `build.commit_sha` omitted, `add` may use an older local HEAD or a missing HEAD; its missing-HEAD and dirty-worktree
warnings are expected here. Require the selected Provider to support this draft-first contract; an incompatible Provider is a blocker, not a reason to
insert an automatic preliminary push. It allocates an uncommitted cloud draft, not a submitted build. The CLI owns any provisional draft SHA; never
treat that provisional value as the final release SHA or copy it into `vibelab.yaml`. Do not fabricate a placeholder or use a preliminary commit to
satisfy this draft-creation step. Only these missing-HEAD and dirty-worktree warnings are expected; every other schema, asset, authentication,
repository, or build-readiness failure remains a blocker. The local APK and source-build readiness gates above still apply. Before `add`, validate the
approved working-tree build inputs, including prebuilt assets intended for the combined commit; after that commit, verify all required local modules
and artifacts are tracked. If any build input changes, repeat the maintained package validation and isolated-resolution checks before source
publication.

For an existing linked app, retain the pre-`add` source gate: require a real full 40-character `git rev-parse --verify HEAD` and guarded matching
readback of the selected source revision. When `build.commit_sha` is explicit, it must identify that selected pushed revision; otherwise use HEAD.
Preserve metadata-only versus new-build intent. Do not replace an existing metadata-only online SHA pin with current HEAD merely to apply the
first-release optimization.

Run Release `add` after the applicable first-release or existing-app gates:

```bash
<pico-release-cli> --json add
```

For the first allocation, require `data.valid === true`, `data.created_draft === true`, and non-empty app/version IDs. Re-read `vibelab.yaml` and
require its new `app.id` to equal `data.app_id`; require matching state IDs. A same-ID revalidation returns `created_draft: false`; retain the
initial-draft proof rather than requiring creation again. Stop on absent/conflicting IDs; preserve any returned `data.deploy_key` for Stage 3.

Read the post-add reconciliation in `publishing-metadata.md` before the first-release Git commit. Require no unexpected tracked mutation from `add`;
reconcile IDs, repository, and the semantic diff against the approved intent. An expected app-ID write-back is not a new content approval. If the diff
is non-empty, obtain approval only for the exact changed values and finish corrections before staging. Rerun `add` with the same trusted app ID only
when corrected validation inputs require it. Do not rerun `add` merely because the later source commit advanced `HEAD`.

For a first release, stage only approved paths, never root `assets/`, and explicitly run `git add -- vibelab.yaml`; require `git ls-files
--error-unmatch -- vibelab.yaml` to succeed. Create one ordinary Git commit containing the approved source and updated `vibelab.yaml`, including
`app.id`. Do not amend or rewrite existing history. For public repositories, pass the source path
checker on this exact commit before pushing. Push it through the same protocol-appropriate guarded transport, then verify the complete
40-character local SHA equals the target remote ref. This post-`add` SHA is the final effective Commit ID that Release `commit` binds to the initial
draft; keep `build.commit_sha` omitted. The normal first-release path has one Git commit/push, not one before and one after `add`. If push fails,
preserve the linked app and draft, reconcile the remote, and resume that same push; do not allocate another app, force-push, or delete state. If push
succeeds but remote readback fails or mismatches, stop before Stage 3 and Release `commit`. Inspect whether the exact reviewed commit is already
remote; reuse it when verified instead of creating another commit or blindly pushing again.

For an existing app that already had a trusted `app.id`, require `data.valid === true`, require its app ID to match the trusted local ID, and preserve
any returned `data.deploy_key` for Stage 3. Its pre-`add` source commit remains authoritative; do not add a second commit for unchanged config. If an
approved correction changes tracked content after a source push, commit/push the correction, verify its selected full remote SHA, and rerun `add` only
for changed validation inputs. One Git commit/push is the normal-path optimization, not a promise to skip required recovery or corrections.

Before every Release `commit`, recheck the selected full 40-character source SHA with guarded remote readback and require a clean tracked worktree;
stop on any missing or mismatched source evidence. The final commit must preserve the validated APK's build inputs; if those change, rebuild and
review. For a first release, use the final local `HEAD`, not the earlier `add` result or provisional draft SHA. Report durable IDs, repository,
visibility, final pushed Commit ID, and state agreement before leaving Stage 2. Remote SHA visibility is not proof that a cloud build worker has
cloned the source.
