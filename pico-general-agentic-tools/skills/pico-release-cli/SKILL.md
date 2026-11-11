---
name: pico-release-cli
description: Operate the catalog-selected regional PICO Release CLI through its init, add, commit, push, and state workflow. Use for VibeLab configuration, draft publishing, previews, reviews, and status diagnostics.
license: 'Apache-2.0'
---

# VibeLab CLI

Use the catalog-selected managed CLI command directly for PICO Vibe Lab. It exposes one Git-like
five-command model: `init`, `add`, `commit`, `push`, and `state`. On first release, `add` allocates
the cloud draft and persists `app.id`; `commit` then updates that linked draft. For later releases,
`commit` auto-routes editable-draft overwrite, metadata-only Info Update, or new-build Version
Update.

## When NOT to Use

- End-to-end project release orchestration that includes project detection, publishing assets,
  GitHub setup, or Deploy Key installation — use `release-to-vibelab`
- PICO login or credential lifecycle operations — use `pico-auth-cli`
- Generic pico-cli discovery, setup, or diagnostics — use `pico-cli`

---

## 1. Resolve the Regional Executable

The Skill name is region-independent. Never infer an executable from a regional suffix. Inspect the
active catalog:

```bash
pico-cli tool list --format json
```

Find `toolId: "pico-release"`. The top-level `region`, `onPath`, and that entry's `command` are
authoritative. If it is absent or unavailable, preserve the reported compatibility action. If it
is not installed, guide the user to run `pico-cli setup`.

When the entry is `ready` and `onPath` is `true`, run its exact `command` directly. The current CN
catalog returns:

```bash
pico-release-cli-cn <args...>
```

Do not derive that name from the Skill name or a region suffix. Only when `onPath` is `false`, or
the exact catalog command fails with `command not found`, use:

```bash
pico-cli tool exec pico-release <args...>
```

`pico-cli tool which pico-release --format json` is for path diagnostics, not primary execution. Do
not switch region or use another region's command. For explicit managed CLI maintenance, use
`pico-cli tool update`. Root `pico-cli update` refreshes activated managed CLIs only after it
successfully installs a replacement CLI, and `pico-cli cleanup` removes them.

---

## 2. Core Rules for Agent Execution (Mandatory)

1. **Always Pass `--json`**:
   - Every `pico-release-cli-cn` invocation executed by an Agent MUST include `--json`.
   - On success (exit code `0`), `stdout` emits a JSON line: `{"ok":true,"data":...}`. JSON mode suppresses progress output.
   - On failure (non-zero exit code), `stderr` emits a single JSON line: `{"ok":false,"error":{"code":"...","message":"...","action":"...","details":{...}}}`.
2. **Never Blindly Retry `WRITE_OUTCOME_UNKNOWN` (Exit Code `5`)**:
   - `GET` requests automatically retry up to 3 times on network timeouts or HTTP 5xx errors.
   - `POST` writes (`commit`, `push`) **never auto-retry** on network or 5xx errors (except one retry after credential refresh on HTTP `401`).
   - When `commit` or `push` returns exit code `5`, run `pico-release-cli-cn --json state [app_id]` first and reconcile server state before retrying.
3. **Private GitHub Repositories (`repo_visibility: private`) & Deploy Keys**:
   - When `build.repo_visibility` is `private`, `add` and `commit` fetch the read-only SSH Deploy Key and return `deploy_key: { repo_url, title, public_key, settings_url }` in `data`.
   - Treat `public_key` as transient installation input: write it to a restrictive temporary file, pass that file directly to `gh repo deploy-key add`, and remove it during cleanup. Never print, attach, or relay the complete key.
   - Before `push`, verify through GitHub's REST response that the matching fingerprint exists with `read_only === true`. Report only repository identifier, fingerprint, read-only state, and installation or reuse status.
4. **Web Preview & Agreement Confirmation Between `commit` and `push`**:
   - `commit` saves the cloud draft and returns `data.preview_url`.
   - Present the exact `data.preview_url` after `commit` and **before `push`** so the user can preview or edit the draft. Explicitly remind the user to check the agreement checkbox on the page before submission. Preserve every returned query parameter; never construct a fallback URL.
   - `push` submits the committed draft without re-saving it, so web preview edits are preserved.
5. **Switching Update Types Requires User Confirmation + `--yes`**:
   - `commit` auto-routes Info Update versus Version Update. If an editable draft of the other type exists, the CLI must delete and replace that conflicting draft.
   - In JSON/non-TTY mode, a conflicting draft without `--yes` aborts with exit code `2` (`ARGUMENT_INVALID`). Stop and obtain explicit user confirmation before rerunning `commit` with `--yes`. Never add `--yes` preemptively.
6. **Authentication & Secret Hygiene**:
   - The CLI consumes the existing local login state and does not provide `login` or `logout` subcommands. If authentication fails, report sanitized `error.code`, `error.message`, and `error.action`, then complete the indicated recovery through `pico-auth-cli` before retrying. Standard authentication uses the catalog-selected `pico-auth` command; the current CN command is `pico-auth-cli-cn login`.
   - Never print tokens, private keys, or authorization headers to logs.
7. **Commit `vibelab.yaml`; Ignore `.vibelab/` and Root Publishing `assets/`**:
   - `vibelab.yaml` is release source and MUST be committed. Never add it to `.gitignore`.
   - `.vibelab/` is local state and remains ignored.
   - Root `assets/` is a local publishing workspace and MUST be ignored and absent from the Git
     index. This does not apply to application build inputs such as `app/src/main/assets/`.

---

## 3. Command Reference (Git-like Five-Command Model)

### Global Options & Environment Variables

| CLI Flag           | Environment Variable | Description                                                                                                    |
| :----------------- | :------------------- | :------------------------------------------------------------------------------------------------------------- |
| `--json`           | -                    | Output structured JSON (`{ ok, data }` on `stdout`, `{ ok, error }` on `stderr`); disables interactive prompts |
| `-y, --yes`        | -                    | Skip confirmation when `commit` must replace a conflicting draft in JSON/non-TTY mode                          |
| `--ppe-env <lane>` | `VIBELAB_PPE_ENV`    | Inject PPE headers for an explicitly selected test lane; never infer a lane                                    |

> When `[app_id]` or `--app <app_id>` is omitted, the CLI prioritizes `app.id` in `vibelab.yaml` and falls back to
> `.vibelab/state.json` in the current working directory.

### Five Core Commands

| Command                                                                                     | Git analogy              | Contract                                                                                                                                                                                                                                                                         |
| :------------------------------------------------------------------------------------------ | :----------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pico-release-cli-cn init [--from-app <app_id>] [--force]`                                  | `git init` / `git clone` | Create the local template and `.gitignore` entry; with `--from-app`, pull the remote editing or online version, write `app.id` and retained `uri:` asset references, and initialize local state.                                                                                 |
| `pico-release-cli-cn add`                                                                   | `git add`                | Validate schema, assets, and local Git state; first release permits a missing HEAD and does not verify a remote push; return a private-repository Deploy Key; when no app ID exists, create the initial cloud draft and persist `app.id`.                                        |
| `pico-release-cli-cn commit [--app <app_id>]`                                               | `git commit`             | Update the linked cloud draft, upload changed assets with SHA-256 caching, update local state, and return `preview_url` plus the agreement notice.                                                                                                                               |
| `pico-release-cli-cn push [--wait] [--interval 10s] [--timeout 30m]`                        | `git push`               | Submit the committed draft without overwriting web preview edits; block when the draft has not been committed. With `--wait`, poll every `--interval` until a terminal build/review result.                                                                                      |
| `pico-release-cli-cn state [app_id] [--watch] [--interval 10s] [--timeout 30m] [--pending]` | `git status`             | Aggregate app detail, version history, `editing_version.review_records`, `editing_version.rejection_issues`, and `next_action`. Fetch `pending_version` with `use_pending_info=true` for pending Info Update or `--pending`; `--watch` polls while in Review or BuildValidating. |

### How `add` and `commit` Route Draft Operations

| Local and remote state                                                             | Result                                      | Behavior                                                                                                                                                       |
| :--------------------------------------------------------------------------------- | :------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `add`: no `app.id` in config or local state                                        | `created_draft: true`                       | Upload assets, create the initial cloud draft, persist IDs to config and state, and return `app_id`, `version_id`, and `preview_url`.                          |
| `add`: `app.id` is already present                                                 | `created_draft: false`                      | Validate inputs and synchronize local state without creating a duplicate draft.                                                                                |
| `commit`: no `app.id` in config or local state                                     | `STATE_MISSING` (exit code `7`)             | Do not create an app; run `add` first.                                                                                                                         |
| `commit`: never-online app with editable Draft, ReviewFail, or BuildFailed version | `mode: "version_update"`                    | Update the initial draft created by `add` with the final commit SHA.                                                                                           |
| `commit`: online app with matching version name and no changed explicit SHA        | `mode: "info_update"`                       | Save metadata/assets as Info Update (`update_type=1`), inheriting `repo_url`, `version_name`, and `commit_sha` from the online version without a code rebuild. |
| `commit`: online/offline app with changed version name or explicit SHA             | `mode: "version_create"`                    | Save a Version Update (`update_type=2`) that triggers a new build.                                                                                             |
| `commit`: existing editable draft of the same update type                          | `mode: "version_update"`                    | Overwrite the existing editing version.                                                                                                                        |
| `commit`: existing editable draft of another update type                           | `mode: "info_update"` or `"version_create"` | After explicit confirmation and `--yes`, replace the conflicting draft and report `replaced_version_id`.                                                       |

---

## 4. `vibelab.yaml` Schema & Asset Specifications

### Configuration Schema

```yaml
app:
  id: '1001' # Optional initially; `add` or `init --from-app` writes it in place
  name: My Vibe App # Required, trimmed 1-50 chars
  slogan: One-line summary # Required, trimmed 1-80 chars
  description: Full description # Required, trimmed 1-1000 chars
  tags: [] # Required: single-select, exactly 1 tag from the 11 fixed Chinese content-tag presets; populate before add
  category: game # Required: game | application
  icon: assets/icon.png # Required: local file path or uri:<remote_uri>
  landscape: assets/landscape.png # Required: local file path or uri:<remote_uri>
  detail_images: # Required: 4-6 items, local file path or uri:<remote_uri>
    - assets/detail-1.png
    - assets/detail-2.png
    - assets/detail-3.png
    - assets/detail-4.png
    - assets/detail-5.png
  videos: # Optional: 0-3 items (defaults to [])
    - file: assets/demo.mp4
      cover: assets/demo-cover.png
version:
  name: 1.0.0 # Required, trimmed 1-50 chars
  notes: Initial release notes # Required, trimmed 1-1000 chars
build:
  repo_url: https://github.com/owner/repo # Required: must match https://github.com/<owner>/<repo>(.git)
  repo_visibility: public # Required: public | private
  commit_sha: 0123456789abcdef0123456789abcdef01234567 # Optional: 40-char full hex SHA; falls back to local `git rev-parse HEAD` when omitted
  tech_stack: unity # Required: preset (`android_spatial` | `unity` | `ue` | `godot`) or custom string (<= 20 chars)
  ai_tool: Trae CLI # Required: preset (`Claude Code` | `Codex CLI` | `Cursor` | `GitHub Copilot` | `Trae CLI`) or custom string (<= 20 chars)
  ai_model: doubao-seed # Required, non-empty string
  features: # Required, at least 1 item:
    - hand_tracking #   body_tracking | hand_tracking | eye_tracking | expression_simulation |
      #   avatar | mixed_reality | mixed_reality_capture | controller_support | none
      #   Note: `none` is mutually exclusive with all other features
  teammates: [] # Optional: 0-3 unique strings, each <= 20 chars
```

### Content Tag Selection

Select exactly one fixed Chinese content tag for `app.tags`. The 11 preset concepts are office
efficiency, utility tools, education/learning, social/lifestyle, media/entertainment, strategy/puzzle,
RPG, casual/puzzle, action/shooter, competitive/entertainment, and other. These English concept
labels are explanations, not allowed YAML values; do not translate them or invent a custom tag.
Use the exact allowed Chinese value returned by `add` validation when the selected Provider exposes
that list. `tags: []` above is an incomplete template, not a valid release configuration; fill it
with one authoritative preset before publishing.

The public CLI 0.1.10 validates preset membership after trimming, deduplicates repeated values, and
requires exactly one distinct content tag. An empty array, unsupported value, or multiple distinct
tags fails validation. Do not rely on deduplication to justify generating multiple tags.
For an existing app, `init --from-app` retains the first valid preset from remote metadata; if none
is valid, it initializes the `other` preset. Review this imported selection before the next write.
`push` also validates local configuration: old free-form or multiple distinct tags can fail with
`CONFIG_INVALID` before submission. This is not a draft re-save. Do not run `commit` merely to repair
that validation failure after web preview; reconcile trusted IDs/state and the approved tag choice.
If the exact list is unavailable, request the authoritative preset list or the user's verified
preset value and stop tag selection rather than guessing. Do not silently upgrade the CLI or
switch region to obtain it.

### Asset Validation Rules

| Asset Type       | Config Path           | Kind  | Allowed Formats           | Exact Dimensions | Max Size            | Count        |
| :--------------- | :-------------------- | :---- | :------------------------ | :--------------- | :------------------ | :----------- |
| App Icon         | `app.icon`            | Image | `.jpg` / `.jpeg` / `.png` | `1024x1024`      | `4 MB`              | 1 (required) |
| Landscape Poster | `app.landscape`       | Image | `.jpg` / `.jpeg` / `.png` | `2560x1440`      | `5 MB`              | 1 (required) |
| Detail Images    | `app.detail_images[]` | Image | `.jpg` / `.jpeg` / `.png` | `2560x1440`      | `5 MB`              | `4-6`        |
| Video File       | `app.videos[].file`   | Video | `.mp4`                    | Any              | `> 0 MB, <= 100 MB` | `0-3`        |
| Video Cover      | `app.videos[].cover`  | Image | `.jpg` / `.jpeg` / `.png` | `2560x1440`      | `5 MB`              | 1 per video  |

- **Remote Asset Prefix (`uri:`)**: Values starting with `uri:` (e.g., `uri:vibe-lab/icon.png`, generated by `pico-release-cli-cn init --from-app`) bypass local file validation and upload, preserving the existing remote URI. Replace with a local path to upload a new file.
- **Local State & Upload Cache**:
  - `.vibelab/state.json`: Stores `app_id`, `version_id`, `update_type`, `drafts`, and resolved `assets` URIs. Never stores credentials.
  - `.vibelab/cache.json`: Maps local file SHA-256 hashes to uploaded ImageX URIs so identical files are never re-uploaded.

---

## 5. Standard End-to-End Workflows (Unified Five-Step Flow)

### Workflow 1: First-Time App Creation & Review Submission

1. Initialize local configuration: `pico-release-cli-cn --json init`.
2. Edit `vibelab.yaml` and prepare assets.
3. Run `pico-release-cli-cn --json add`. Require `data.valid === true` and, on first release, `data.created_draft === true`; verify that `app.id` was written to `vibelab.yaml`. For a private repository, preserve and install the returned Deploy Key before submission.
   A first-release `add` may report the expected missing-HEAD or dirty-worktree warning; it does not
   verify that any commit exists on the GitHub remote.
4. Explicitly stage the updated `vibelab.yaml`, confirm it is in the Git index, then commit and push
   the source to GitHub. Never stage the root publishing `assets/` directory.
5. Run `pico-release-cli-cn --json commit`. Require `data.mode === "version_update"` for the initial draft, preserve durable IDs and the exact `data.preview_url`, then ask the user to preview/edit the draft and confirm the agreements.
6. After confirmation, run `pico-release-cli-cn --json push`, or add `--wait --interval 10s --timeout 30m` for bounded observation. Do not run `commit` again after web edits.
7. Inspect later progress with `pico-release-cli-cn --json state [app_id] [--watch]` without resubmitting.

### Workflow 2: Update an Existing App

1. If local state is absent, run `pico-release-cli-cn --json init --from-app <app_id> --force` after overwrite approval.
2. For metadata/assets only, keep the online version name and commit SHA; for a new build, push code and change version name and/or commit SHA.
3. Run the same `add -> commit -> preview/confirm -> push -> state` sequence. `add` synchronizes state from `app.id`; `commit` chooses Info Update, Version Update, or in-place draft overwrite.
4. If `commit` reports an update-type conflict, explain which draft would be replaced, obtain explicit user approval, then rerun once with `--yes`.

### Workflow 3: Resubmit an Editable Draft

When `state` reports Draft (1), ReviewFail (3), or BuildFailed (6):

1. Inspect `editing_version.rejection_issues` and `next_action`.
2. Fix metadata, assets, or code.
3. Run `add -> commit`, present the returned preview URL for confirmation, then run `push` or `push --wait`.

---

## 6. Exit Codes & Error Handling Matrix

| Exit Code | Error Code (`error.code`)              | Meaning                                                                          | Agent recovery action                                                                                                                |
| :-------: | :------------------------------------- | :------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
|    `0`    | -                                      | Success                                                                          | Parse `data` from the single JSON object on stdout.                                                                                  |
|    `1`    | `UNKNOWN` / `PROTOCOL_ERROR`           | Unexpected runtime error or malformed API response                               | Preserve the reported action and verify CLI/backend compatibility.                                                                   |
|    `2`    | `ARGUMENT_INVALID` / `CONFIG_INVALID`  | Invalid flags/config/assets or missing `--yes` for conflicting-draft replacement | Inspect sanitized `error.details.issues` or `error.message`, fix inputs, and rerun `add`; obtain confirmation before `commit --yes`. |
|    `3`    | `NOT_LOGGED_IN` / auth errors          | Missing, expired, or invalid credentials                                         | Follow the catalog-selected Auth Skill and retry after login.                                                                        |
|    `4`    | `NETWORK_TEMPORARY`                    | Read request failed after bounded retries                                        | Check connectivity after a read failure or auth-refresh network failure; retry the read.                                             |
|    `5`    | `WRITE_OUTCOME_UNKNOWN`                | `commit` or `push` outcome is uncertain                                          | Never retry blindly; run `state [app_id]` first.                                                                                     |
|    `6`    | `BUSINESS_REJECTED` / `INVALID_STATUS` | Backend rejected the operation or current state                                  | Inspect sanitized `details.backend_code`, run `state [app_id]`, and follow `error.action` / `next_action`.                           |
|    `7`    | `STATE_MISSING` / `STATE_CONFLICT`     | Required app/version IDs are missing/corrupt or the selected draft conflicts     | Run `add` to allocate `app.id`, pass `--app <app_id>`, or reinitialize with `init --from-app`.                                       |
|    `8`    | `UPLOAD_FAILED`                        | Asset upload failed                                                              | Check network/assets and rerun `add` or `commit`; cached uploads are reused.                                                         |
|    `9`    | `REVIEW_REJECTED`                      | `push --wait` observed ReviewFail or BuildFailed                                 | Inspect sanitized `error.details.rejection_issues` and `state`, fix issues, then run `add -> commit -> push`.                        |
|   `10`    | `WAIT_TIMEOUT`                         | Review/build is still in progress at timeout                                     | Resume read-only observation with `state [app_id] --watch`.                                                                          |
|   `130`   | `USER_CANCELLED`                       | User declined confirmation                                                       | Stop and preserve current state.                                                                                                     |
