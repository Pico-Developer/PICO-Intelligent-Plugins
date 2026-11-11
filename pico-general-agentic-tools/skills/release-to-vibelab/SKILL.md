---
name: release-to-vibelab
description: Orchestrate one-click VibeLab draft upload or review submission through PICO Auth and Release CLIs. Use when the user asks to upload, publish, or release an app to VibeLab.
license: 'Apache-2.0'
---

# Release to VibeLab

Own the end-to-end sequence. Provider Skills own individual CLI usage; bundled references own
specialized policy. Do not duplicate their detailed contracts here.

## When NOT to Use

- Release CLI command syntax or single-command diagnosis without project orchestration — use
  `pico-release-cli`
- PICO login or credential lifecycle operations — use `pico-auth-cli`
- Generic project development, build, or test work without a VibeLab release request

## Provider routing

Load each provider only when the workflow reaches its responsibility:

| Need                                    | Provider                                                                      | Load point                                                       |
| --------------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| PICO login and credential state         | [`pico-auth-cli`](../pico-auth-cli/SKILL.md)                                  | Immediately before Stage 1                                       |
| VibeLab config, drafts, and review      | [`pico-release-cli`](../pico-release-cli/SKILL.md)                            | Before the first Release call in Stage 2                         |
| Spatial multi-angle runtime screenshots | `capture-camera` from the user-level general plugin                           | After selecting a Spatial target in Agent-prepared asset capture |
| Spatial runtime video actions           | `spatial-accessibility` from the configured Spatial platform plugin           | Before recording an interactive Spatial scenario                 |
| Stage 2 release preparation             | [`stage-2-release-preparation.md`](references/stage-2-release-preparation.md) | When entering Stage 2                                            |
| Unity Android repository export         | [`unity-android-export.md`](references/unity-android-export.md)               | After Unity detection in Stage 2                                 |
| Source build readiness                  | [`source-build-readiness.md`](references/source-build-readiness.md)           | After resolving the Stage 2 publish root                         |
| Submission quality and APK alignment    | [`submission-quality.md`](references/submission-quality.md)                   | After the final release APK is built in Stage 2                  |
| Publishing asset policy                 | [`vibelab-asset-guidelines.md`](references/vibelab-asset-guidelines.md)       | Before asset review in Stage 2                                   |
| Output allowlisting and redaction       | [`sensitive-output-redaction.md`](references/sensitive-output-redaction.md)   | Before the first command in Stage 0                              |
| Cross-platform execution reliability    | [`execution-reliability.md`](references/execution-reliability.md)             | Before the first command in Stage 0                              |
| Publishing metadata collection          | [`publishing-metadata.md`](references/publishing-metadata.md)                 | Before collecting fields in Stage 2                              |

Read each provider once per run unless its file changes. Follow the provider when command syntax,
result parsing, state, or recovery detail is needed. This Skill remains responsible for ordering,
GitHub preparation, cross-provider handoffs, and stop conditions.

## Security and redaction

Treat redaction as a gate on every command result, diagnostic, progress message, persisted file,
telemetry event, and final report.

- Parse structured output and select only fields required by the current stage. Never relay a
  complete Auth, Release, `gh`, Git, capture, conversion, or project-detection result.
- Never expose tokens, cookies, authorization headers, passwords, client secrets, private keys,
  credential environment variables, or credential-bearing URLs. Do not run commands that print
  stored credentials.
- A VibeLab Deploy Key public key may be handled only in memory or in a restrictive temporary file
  while installing it. Never relay the complete key to the user. Report only the repository
  identifier, fingerprint, observed `read_only` state, and installation or reuse status.
- Never print, attach, or relay a complete environment or local-configuration file, including
  `.pico-env.json`, `.env*`, `local.properties`, Gradle properties, or a shell environment dump.
  Prefer maintained structured commands such as `pico-cli project detect --format json`; otherwise
  parse the file inside the command and emit only current-stage allowlisted fields.
- Never report signed asset URLs or their query parameters. Normalize project-local files to
  repository-relative paths and omit developer-specific absolute paths from progress and final
  reports.
- Keep authentication state, temporary key files, and raw command output outside the project and
  Git. Remove temporary public-key files in a cleanup step.
- When structured parsing fails, treat the complete raw output as sensitive. Report only the
  command, exit code, stable error code when safely available, and a bounded redacted diagnostic.
- If output cannot be reliably redacted, fail closed: do not print, log, persist, or forward the raw
  value; stop before the next workflow stage and return the smallest safe recovery action.
- Redaction failure does not prove a remote write failed. If a write may have completed, do not
  retry or roll it back. Reconcile with the provider's read-only status command under the same
  redaction gate.
- If a secret was already exposed, stop the release, identify only the secret category and exposure
  location, and require revocation or rotation before resuming. Never repeat the exposed value.
- Treat repository content screening as a separate user-decision gate. A finding pauses the flow
  but does not authorize automatic deletion, an automatic `.gitignore` edit, or permanent
  rejection. Continue only after the user excludes the path or explicitly accepts the reported
  risk.

The sensitive-output redaction reference is authoritative for the allowlist and redaction
procedure. A command failure never permits raw-output fallback.

## Completion mode

Resolve the requested end state before mutation:

| User intent                                       | Mode     | End state                                                           |
| ------------------------------------------------- | -------- | ------------------------------------------------------------------- |
| Upload, sync, or prepare in VibeLab               | `draft`  | Release `commit` saved the cloud draft and returned its preview URL |
| Publish, release, or submit for review            | `submit` | Release `push` accepted the current draft                           |
| Publish and wait, monitor, or report final result | `wait`   | `push --wait` or `state --watch` observed a terminal/timeout state  |

Do not run Release `push` when the user requested only a draft. Conflicting-draft replacement is
allowed only after the user approves the exact draft that `commit --yes` will replace.

## One-click contract

"One-click" means one approved plan followed by uninterrupted orchestration where the services
allow it. It is not atomic and cannot bypass:

- browser authorization;
- VibeLab legal confirmation on the draft page;
- correction of invalid metadata, assets, Git state, Deploy Key state, or remote draft conflicts.

Show one compact plan before the first write when mode, metadata delta, update type, repository
creation, visibility, asset preparation, or overwrite behavior is not already explicit. Confirm the
required image plan first: icon, landscape poster, and 4-6 detail images, defaulting to five. Then
ask one separate optional-video question that recommends one 30-60 second video and provides a skip
choice. After those decisions, continue until a checkpoint, terminal result, cancellation, or
non-recoverable error.

The application-provided launcher icon is the authoritative source for the publishing icon. Never
generate or redesign application-icon artwork, and never substitute a design-stage intermediate,
preview, mockup, screenshot, or unrelated image. If that source already satisfies the publishing
contract, use it unchanged. If it does not satisfy the required JPEG format, `.jpg` or `.jpeg`
extension, dimensions, or size, stop and offer exactly two preparation paths: the user provides a
compliant review file based on the same application icon, or the user gives explicit, icon-specific
authorization for the Agent to convert or resize the application-provided source into a compliant
review file under `<publish-root>/assets/`. Never overwrite the application's source icon. Preserve
the source artwork, identity, visible composition, aspect ratio, padding, and color intent; do not
crop, pad, redraw, recolor, add or remove content, or repair manual-review risks. Resolve this choice
before any device availability check. Agent-prepared runtime-media mode does not authorize
application-icon conversion.

## Stage 0 - Preflight and plan

1. Read and apply the sensitive-output redaction and `execution-reliability.md` references before
   running any command on any platform; use their execution-context, outcome-propagation,
   temporary-path, and long-process contracts throughout.
2. Confirm the source project root. Initialize the publish root to that path; Stage 2 replaces it
   with the exported Android Gradle repository when Unity is detected.
3. Inspect source project facts and Git state without mutation. Never stage unrelated changes or
   authentication state.
4. Run one catalog query:

   ```bash
   pico-cli tool list --format json
   ```

5. Require compatible, `ready` `pico-auth` and `pico-release` entries. If either entry reports
   `status: "unavailable"` (for example the selected region has no published product, or the
   region is not configured), stop as a blocker before any further command. Report that the
   selected region has no available managed Release/Auth CLI, relay the entry's reported message
   and compatibility action, and direct the user to confirm the region via `pico-cli setup
--region` or wait for that region's CLI to publish. If an entry is `not-installed`, guide the
   user to run `pico-cli setup`. Continue only with `ready` entries. Use each entry's resolved
   `command` as the executable: throughout this document `<pico-auth-cli>` and
   `<pico-release-cli>` are placeholders for the `pico-auth` and `pico-release` commands the
   catalog reports for the selected region (CN currently resolves them to `pico-auth-cli-cn` and
   `pico-release-cli-cn`). Never hardcode a regional suffix; always substitute the resolved
   command. The catalog's top-level `region` also fixes the required application and publishing
   language: `cn` requires Chinese; `us` and `row` require English.
6. Run each exact catalog command when it is on `PATH`. Only when a ready entry is not on `PATH`, or
   that exact executable returns `command not found`, use:

   ```bash
   pico-cli tool exec pico-auth <args...>
   pico-cli tool exec pico-release <args...>
   ```

7. Run `pico-cli project detect --format json` and consume its structured `projectRoot`,
   `platform` (engineering platform, e.g. `spatial`), evidence, and SDK version. The detector's
   `platform` value is not the `build.tech_stack` value; map it in Stage 2 (see below). A detector
   process failure, malformed result, protocol error, or cancellation is a blocker. For
   `ambiguous`, `unknown`, or an unsupported platform, use the bounded project-marker fallback in
   the submission-quality reference; do not collapse UE or Godot to `other`.
8. Require Git and `gh`. When `gh --version` reports that `gh` is not installed, install it for the
   current host, then re-verify with `gh --version` before continuing:
   - macOS: `brew install gh`.
   - Windows: `winget install --id GitHub.cli`.
   - Reject other hosts instead of guessing an installer. Stop as a blocker if installation cannot
     be verified.

   Then check GitHub authentication with `gh auth status --hostname github.com`; never request or
   print its token. When authentication is absent, run `gh auth login --web --hostname github.com`,
   then repeat the status check. A successful `gh auth status` proves GitHub API authentication; it
   does not prove Git transport readiness for either public or private repositories. Stage 2 owns
   the separate HTTPS or SSH transport gate. Do not run `gh auth setup-git` by default because it
   persistently changes the user's Git configuration; use the Stage 2 process-scoped HTTPS helper,
   unless the user explicitly authorizes a persistent repair.

9. Build one plan containing completion mode, new versus existing app, metadata versus code update,
   asset-preparation mode (`user-supplied` or `agent-prepared`), asset paths, and the plain-language
   origin of each selected asset for user suitability confirmation; these labels are review-only,
   not schema fields or SHA/APK binding. Include 4-6 required detail-image paths and runtime moments
   (default five), repository, visibility, allowed commit
   paths, mandatory `.pico-env.json` and root publishing `assets/` ignore repair when needed,
   selected region, required language, language-evidence source, and checkpoints. Confirm these
   required assets together. Then ask a separate video question with exactly these choices: Agent
   prepares one 30-60 second key-interaction video and dedicated cover; user supplies the video and
   dedicated cover; or skip video. Track video provenance with four orchestration-only roles, not
   `vibelab.yaml` keys: `video_for_stills`, `raw_publish_recording`, `publish_video`, and
   `publish_video_cover`. Intermediate roles stay outside `<publish-root>/assets/`. Only
   `publish_video` may map to `app.videos[].file`; only its corresponding `publish_video_cover` may
   map to `app.videos[].cover`.
   An Agent-prepared proposal names its scenario, visible action sequence, target duration, and
   expected result. For Agent-prepared Spatial Stage or volumetric detail images, also record any
   user-requested viewpoints; otherwise use the bounded five-view default in Stage 2. Resolve the
   asset-preparation mode before any device check, and never switch it implicitly. For Unity,
   include the separate local target Git repository and explicit target-replacement approval.
   Keep every user-visible task list synchronized with the repository visibility:
   - Before visibility is known, use neutral repository-access wording. Do not predeclare a Deploy
     Key task.
   - Immediately after visibility is observed or the user chooses it, update the remaining task
     list; do not preserve a stale static stage title.
   - For `public`, omit Stage 3 as a task and remove all Deploy Key wording from remaining task
     titles. A combined task may read `Stage 4-5: draft commit, preview, submit`.
   - For `private`, include the read-only Deploy Key work. A combined task may read
     `Stage 3-5: deploy key, draft commit, preview, submit`.
   - The Stage 3 implementation section below documents the private path; its existence never
     authorizes showing that work in a public-repository plan.

## Stage 1 - Authenticate with PICO

Read the `pico-auth-cli` provider Skill now, then follow its status and login contracts.

Run:

```bash
<pico-auth-cli> --json status
```

- Continue when authenticated without forcing refresh.
- Otherwise run `<pico-auth-cli> --json login` and let the user complete browser authorization.
- Never run `login --force` or `logout` in this workflow.
- Resume from `status`; stop on pending, declined, expired, or unavailable authorization.

## Stage 2 - Prepare configuration, assets, and GitHub

Read and follow
[`stage-2-release-preparation.md`](references/stage-2-release-preparation.md) completely. It owns
publish-root resolution, configuration initialization, asset preparation, metadata and APK gates,
region-language alignment, GitHub publication, and the first-release single Git commit/push after
`add`. Do not enter Stage 3 until every Stage 2 gate in that reference passes.

## Stage 3 - Install the Private-Repository Deploy Key

Skip this stage for a public repository. For a private repository, use the Deploy Key metadata
returned by Release `add` (or, if repeated by `commit`, require it to match): `public_key`,
`title`, `settings_url`, and repository URL.

Inspect existing GitHub keys before adding one:

```bash
gh api --paginate \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "repos/<owner>/<repository>/keys"
gh repo deploy-key add <temporary-public-key-file> \
  --repo <owner>/<repository> --title "PICO Vibe Lab"
```

Use the GitHub REST response contract, not version-dependent normalized fields from
`gh repo deploy-key list --json`: collect every paginated array entry and accept only objects with
documented `id`, `title`, `key`, and boolean `read_only` fields. Compute fingerprints for the
returned public keys and reuse a fingerprint match instead of adding a duplicate. If no match
exists, add the key once, repeat the REST inspection, and require exactly one fingerprint match with
`read_only === true`. An authentication, authorization, network, pagination, malformed-response,
missing-field, or non-boolean-field failure is not an empty key list; stop without adding or
re-adding a key. GitHub Deploy Keys are read-only by default. Never pass `--allow-write`.

Create the temporary public-key file outside the project with restrictive permissions, remove it in
a cleanup step, and never print, attach, or relay its contents. If automatic installation is
unavailable, report a blocker with only the repository identifier and settings URL; do not expose
the key as a manual-install fallback. Report only the fingerprint, observed `read_only` state, and
installation or reuse status. Release `push` must not run until the matching key is verified as
read-only.

Remote SHA visibility, Release `add` validity, and a matching read-only Deploy Key prove only the
GitHub-side source configuration. They do not prove that a VibeLab build worker has cloned or
checked out the selected commit. Keep cloud clone status `unverified` through `commit`, successful
`push`, and any state that only says build validation or review is in progress. Mark it `verified`
only from explicit provider checkout success or an observed successful terminal build; report an
explicit checkout failure as `failed`. Never infer clone success from submission acceptance.

## Stage 4 - Save the Cloud Draft

Require matching non-empty app IDs in `vibelab.yaml` and `.vibelab/state.json`, then inspect remote
state:

```bash
<pico-release-cli> --json state <app_id>
```

Missing or conflicting app IDs are a `STATE_MISSING` or `STATE_CONFLICT` blocker. Inspect and
reconcile trusted config/state and remote evidence first; do not automatically run `add`, overwrite
configuration, or ask `commit` to create an app. Resynchronization requires an identified target and
user approval when overwriting; ambiguous first-allocation outcomes stop at read-only investigation.
Repeat repository content
screening immediately before the first `commit`. Treat this as a fallback reminder rather than an
automatic hard block, but do not silently continue past a new or unresolved finding. If a
discovered credential already reached the remote repository, require revocation or rotation before
proceeding.

Immediately before the draft save, repeat Stage 2's source-readiness check after any Deploy Key or
browser checkpoint: the selected complete SHA must still match the guarded remote readback and the
tracked worktree must be clean. On first release, keep `build.commit_sha` omitted and require the
same final local `HEAD`; new source changes must be approved, published, and reverified first.

Run one smart draft save:

```bash
<pico-release-cli> --json commit
```

Release `commit` chooses and reports `data.mode`:

| Authoritative state and intent                                           | Required save semantics            |
| ------------------------------------------------------------------------ | ---------------------------------- |
| Initial never-online app draft created by `add`                          | `version_update` (app-draft save)  |
| Never-online Draft, ReviewFail, or BuildFailed app                       | `version_update` (app-draft save)  |
| Online app, metadata/assets only, version name and SHA unchanged         | `info_update`                      |
| Online/offline app with changed version name or commit SHA               | `version_create`                   |
| Existing editable draft for an online/offline later-release version flow | Provider-selected `version_update` |

The locked Provider performs the first-release app-draft save but reports
`data.mode === "version_update"` for that path. Accept this first-release result only with the
preserved initial `add` creation proof (`data.created_draft === true`) or the reconstructed initial-
draft evidence in `publishing-metadata.md`. A same-ID revalidation's `created_draft: false` does not
invalidate that proof. Remote state must still identify the app as never-online, and the `commit`
result's non-empty `app_id` and `version_id` must match the persisted app and current draft IDs. Missing or conflicting evidence is a Provider compatibility blocker. Do not infer
first-release semantics from `version_update` alone; for an online/offline later release it retains
its existing-version meaning.

If `commit` reports that an editable draft of another update type must be replaced, stop and
show the existing draft, requested target mode, and deletion consequence. Continue only after
explicit user approval, then rerun once with:

```bash
<pico-release-cli> --json --yes commit
```

Commands that upload uncached assets may print trace lines before their result. Parse only the last
non-empty stdout line as JSON. Preserve `data.mode`, `app_id`, `version_id`, update type,
Deploy Key metadata, agreement notice, and the exact Provider-returned `data.preview_url` verbatim.
Do not classify or infer how the Provider obtained that URL. For a private repository, verify any
returned key matches the installed key.

Stop here for `draft` mode after reporting the durable IDs and preview URL.

## Stage 5 - Confirm and Submit

Use the exact `data.preview_url` returned by Stage 4 `commit`. Give it to the user so they can
review or modify the uploaded draft and complete the agreement/legal confirmation. Never construct,
guess, or hardcode a preview or console URL. Treat the value as opaque: Do not append, remove, or
rewrite query parameters. If `commit` does not return a preview URL, stop as a blocker and report
the durable app/version IDs.

After the user returns, run a read-only state check and require the same editable version to remain
current and unlocked:

```bash
<pico-release-cli> --json state <app_id>
```

The on-page agreement confirmation is performed by the user in the browser; the CLI does not
perform or universally prove it. Do not modify confirmation fields on the user's behalf.

For `submit` mode:

```bash
<pico-release-cli> --json push
```

For `wait` mode:

```bash
<pico-release-cli> --json push --wait --interval 10s --timeout 30m
```

### Interpret the Provider submission receipt

Use the actual resolved Provider's structured result, not Stage 4's flat `commit` projection.
For the current public Provider, successful `push` returns `data.draft`, `data.submission`, and
`data.warnings`; `--wait` may additionally return `data.final_version`. `data.draft` identifies the
submitted draft; its presence does not prove another draft save. The submission payload comes from
the backend: inspect it rather than inventing inner fields or assuming a universal status key.

Before reporting or persisting receipt facts, apply the **Nested Release receipt projection** in
`sensitive-output-redaction.md`. Keep these summary concepts separate; they are orchestration
report fields, not additions to the Provider schema:

- `draft_saved`: `true` only from the preceding confirmed Release `commit` for the same draft;
  otherwise unknown. Never infer it from `data.draft` or from this `push`.
- `submitted`: `true` for a successfully parsed current-Provider `push` success envelope, or explicit
  `error.details.submitted === true`. For `WRITE_OUTCOME_UNKNOWN` in `phase: submit_review`,
  `write_outcome: committed` confirms submission through Provider readback, `uncommitted` confirms
  it had not taken effect at that readback, and `unknown` leaves it unknown. These values concern
  review submission, not the preceding draft save. Report the phase and evidence source.
- `version_id`: take the nested `data.draft.version_id` or error-details draft/version ID and require
  agreement with the trusted app/version from Stage 4. Conflicting IDs block continuation.
- `submission_status`: use only an actually present, safely projected submission status with its
  exact field path. Missing status stays unknown. Keep `final_version.status`, error-details status,
  and later `state` observations separate as build/review evidence, not submission receipt status.

Preserve safe receipt facts, sanitized warnings, process exit code, receipt availability, and each
fact's source. Never default a missing or filtered receipt to `submission={}`. A genuinely empty
original receipt is different from an unavailable receipt; neither by itself means submission failed.
For nonzero `push --wait`, inspect `error.details`: `submitted`, `phase`, `app_id`, `version_id`,
`draft`, and `submission` may prove submission already succeeded while waiting or review failed.
Keep that acceptance separate from wait failure, `REVIEW_REJECTED`, and publication success.

Never repeat `commit` or `push` to repair an incomplete summary. Reconcile with read-only `state`
for the same trusted app/version when necessary; label recovered facts as readback, not as the
original receipt. IDs reused from prior `commit` or local state retain those sources. If no trusted
app ID remains or evidence conflicts, stop at read-only investigation instead of guessing.

Release `push` submits the committed draft without re-saving it, which preserves edits made on the
web preview. A `WAIT_TIMEOUT` means review or build is still running, not that submission failed.
Resume observation without resubmitting:

```bash
<pico-release-cli> --json state <app_id> --watch --interval 10s --timeout 30m
```

## Failure and resume rules

- Fail closed at the first unmet Auth, detection, `add`, GitHub, Deploy Key, draft-state, or
  legal-confirmation gate.
- Never blindly retry Release `commit` or `push` after `WRITE_OUTCOME_UNKNOWN`. Run
  `<pico-release-cli> --json state [app_id]` first and reconcile the observed app/version state.
- Before retrying `gh repo create`, inspect with `gh repo view`. Before retrying Deploy Key
  installation, inspect the REST key list with `gh api`. Before retrying Git `push`, inspect the
  remote branch and commit SHA.
- Do not roll back by deleting an app, version, repository, Deploy Key, uploaded asset, config, or
  state file. The only draft replacement allowed here is the one Release `commit --yes` performs
  after explicit user approval of an update-type conflict.
- On cancellation, clean temporary public-key files and report completed stages, durable IDs,
  repository URL, pushed SHA, and the smallest safe resume action.
- Reconstruct progress from `vibelab.yaml`, `.vibelab/state.json`, Git/GitHub, and Release
  `state`. Do not create a second orchestration state file.

## Final report

Report:

- resolved Auth and Release command identities;
- detected project type and delegated conversion result, if any;
- selected region, required language, and runtime-language evidence;
- Auth status without credential material;
- validated repository-relative local and retained `uri:` asset references, without signed URLs or
  developer-specific absolute paths;
- credential-free GitHub URL, visibility, branch, pushed SHA, and Deploy Key fingerprint/status;
- cloud clone status (`unverified`, `verified`, or `failed`) with its provider evidence; absent
  explicit checkout or successful terminal-build evidence, report `unverified`;
- Release `commit` mode, `app_id`, `version_id`, update type, preview URL availability, and
  completion mode;
- `draft_saved`, `submitted`, `version_id`, and `submission_status` with safe nested receipt facts,
  sanitized warnings, receipt availability, and evidence source; review/build status or bounded
  timeout remains separate;
- blockers and the smallest safe resume action.

Apply the redaction reference. Never repeat a Deploy Key, report `commit` success as submission
success, or report review success before the actual observed terminal state.
