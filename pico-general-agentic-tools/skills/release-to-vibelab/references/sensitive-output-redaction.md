# Sensitive Output Redaction

Apply this reference before running Auth, Release, `gh`, Git, capture, conversion, or project
detection commands in the release workflow. Redact command output before it reaches terminal
summaries, logs, files, telemetry, or the final report.

## Never expose

Treat these values and equivalent variants as secrets:

- access, refresh, bearer, session, OAuth, device, or personal access tokens;
- cookies and `Set-Cookie` values;
- `Authorization`, proxy authorization, and registry authentication headers;
- `GH_TOKEN`, `GITHUB_TOKEN`, and credentials returned by `gh auth`;
- private SSH keys, private Deploy Keys, signing keys, and passphrases;
- passwords, client secrets, webhook secrets, and credential-bearing URLs;
- temporary authentication files and their contents.

Never run `gh auth token`, `gh auth status --show-token`, print credential environment variables, or
enable verbose HTTP tracing in this workflow.

## Values that may be reported

Report only values needed to identify or resume the release:

- non-sensitive Auth status and expiry;
- GitHub `owner/repository`, canonical credential-free repository URL, visibility, branch, and full
  commit SHA;
- Release `app_id`, `version_id`, operation status, draft URL, and redacted error code;
- local repository-relative asset paths, validation results, dimensions, sizes, and color-profile
  names;
- the VibeLab Deploy Key repository identifier, fingerprint, observed `read_only` state, and
  installation or reuse status.

A public key is not a private credential, but its complete value is not reportable. Handle it only
in memory or through a restrictive temporary file used directly by `gh repo deploy-key add`.
Never print, attach, or relay it as a manual-install fallback.

Do not report signed asset URLs, including query parameters such as signatures, expirations, or
access tokens. Do not report developer-specific absolute paths. Normalize files under the publish
root to repository-relative paths; for paths outside that root, report only a safe resource kind or
basename when needed for diagnosis.

## Nested Release receipt projection

Apply this projection to Stage 5 `push` before any stdout summary, persisted diagnostic, or final
report. Preserve nesting and classify fields before emission; a denylist-only recursive dump is
not safe. Container names do not make arbitrary contents reportable.

| Actual Provider source                                                      | Safe projection                                                                                                                                                                                                                                                  |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data.draft` or `error.details.draft`                                       | Non-empty `app_id`, `version_id`, scalar `release_channel` and `update_type`; match IDs to the trusted draft. Exclude `assets` and arbitrary sibling fields. Keep the exact Stage 4 preview URL separately; do not replace it from this receipt.                 |
| `data.submission` or `error.details.submission`                             | Record whether the original receipt is missing, null, empty, or present; report only actual non-sensitive identifier/status fields after field-level classification, preserving their exact paths and scalar values. There is no assumed universal inner schema. |
| `data.warnings`                                                             | Sanitized bounded warning text/count. Never relay raw warning strings containing paths, credentials, or signed URLs. Distinguish absent warnings from an observed empty array.                                                                                   |
| `data.final_version`, `error.details.status`, `error.details.remote_status` | Allowlisted app/version IDs and actually observed scalar build/review status, with source and phase. Never relabel it as original submission receipt status.                                                                                                     |
| `error.details`                                                             | Typed `submitted`, `phase`, `write_outcome`, `retryable`, `draft_preserved`, and non-empty app/version IDs. Project nested draft/submission by the rows above; no raw `details` dump.                                                                            |

For an unfamiliar submission object, inspect its shape privately and expose only current-stage
allowlisted scalar facts whose meaning is supported by the actual Provider response. Never stringify
an entire `submission`, `draft`, `final_version`, error object, array, or nested descendant to bypass
projection. Do not automatically report a field named `message`, `url`, or `key`: unknown strings
may contain credentials, complete Deploy Keys, signed asset links, or developer-specific paths.
Missing, malformed, conflicting, or unclassifiable fields stay unknown or are omitted with safe
receipt-availability metadata. Never replace a missing or fully filtered receipt with `{}`; distinguish
an actually empty original object from an unavailable summary. Preserve safe siblings when one field
is excluded, and keep warning/readback provenance without leaking rejected values.

Receipt summary booleans and statuses are derived orchestration facts, not new YAML, Provider, or
machine-state fields. For `phase: submit_review`, interpret `write_outcome` only as review-write
reconciliation. Do not treat local `committed: false` as failed submission; the Provider also clears
it after successful submission. Successful submission or a saved draft does not prove cloud clone,
build, review, or publication success. Never retry a write to recover missing receipt information.

## Command construction

- Pass secrets through the owning CLI's credential store. Do not place them in command arguments,
  shell history, temporary scripts, or project files.
- Use `gh auth status --hostname github.com` for GitHub API authentication checks. Its success does
  not prove HTTPS or SSH Git transport readiness. Keep the API result, protocol-specific transport
  result, push result, and remote-SHA readback as separate audit events for public and private
  repositories.
- Reject Git remote URLs containing user information, tokens, passwords, or sensitive query
  parameters. Normalize reports to `https://github.com/<owner>/<repository>` or
  `git@github.com:<owner>/<repository>.git`.
- Never use `cat`, `type`, `Get-Content`, `env`, `set`, or equivalent commands to emit a complete
  environment or local-configuration file or process environment. This includes `.pico-env.json`,
  `.env*`, `local.properties`, Gradle properties, credential stores, and environment dumps.
- Prefer a maintained structured command for the required fact. If none exists, parse the source
  inside the command and emit only explicitly named, current-stage allowlisted fields; field
  classification must happen before stdout or stderr is produced.
- Never pipe a Git, `gh`, or Release command whose exit status controls the workflow. A trailing
  filter, `head`, `tail`, `sed`, `jq`, or `echo` can replace the command's status. Do not recover it
  through Bash-only `PIPESTATUS`, zsh-only `pipestatus`, or `$?` / `$LASTEXITCODE` read after another
  command.
- Prefer a process API that returns stdout, stderr, and exit status separately. When only a shell is
  available, redirect raw output to a restrictive temporary file outside the project and capture
  the command status immediately:

  ```bash
  umask 077
  output_file="$(mktemp)"
  if command_to_run >"$output_file" 2>&1; then
    command_status=0
  else
    command_status=$?
  fi
  ```

  ```powershell
  $outputFile = New-TemporaryFile
  & command_to_run *> $outputFile
  $commandStatus = $LASTEXITCODE
  ```

  Do not run any intervening command before assigning `command_status` or `$commandStatus`. Parse
  and redact only after that assignment, report only allowlisted fields, remove the temporary file
  in cleanup, and decide process success from the captured status. Before the shell invocation
  returns, explicitly propagate a nonzero captured status (`exit $commandStatus` on PowerShell or
  `exit "$command_status"` on POSIX). A successful parser, `ConvertTo-Json`, `Set-Content`, cleanup,
  or evidence write must never replace the owning command's failure with shell exit zero.

- Process success does not prove the remote mutation. After a successful Git push, independently
  read the exact remote ref through the same protocol-appropriate guarded transport, preserve that
  read's exit status, and compare full 40-character local and remote SHAs. Do not pipe `ls-remote`
  through a parser whose status can replace Git's. After a `gh` mutation, read back the repository
  or key through structured API output. After a Release write, reconcile durable app/version state
  when the result is uncertain.
- A Git exit code such as 128 is generic. Preserve the actual code and a bounded redacted diagnostic
  under a stable result such as `GIT_TRANSPORT_FAILED`; do not call it
  `HTTPS_CREDENTIAL_HELPER_MISSING` unless redacted stderr evidence supports that non-authoritative
  `inferredCategory`. Distinguish authentication, authorization, transient network, remote absence,
  remote conflict, SSH transport, and SHA mismatch; retry only clearly transient network failures.
- When `pico-release-cli-cn` returns a public Deploy Key, write it only to a temporary regular file
  outside the project, set restrictive permissions, pass that file to `gh repo deploy-key add`, and
  remove it in a cleanup step. Do not emit the key before, during, or after installation.
- Never commit `.vibelab/`, root publishing `assets/`, Auth state, temporary key files, environment
  dumps, or logs.
- Always commit `vibelab.yaml`. It is release configuration and must not be added to `.gitignore`.
  Stage it explicitly and confirm it is present in the Git index.

## Mandatory local-state ignore gate

Project-root `.pico-env.json` is generated local runtime state and is never release source. Include
its ignore repair in the approved Stage 0 plan; do not inspect its contents to decide this policy.
After the Git worktree exists and before staging, use
`git check-ignore -v --no-index -- .pico-env.json` and require the matching source to be the
worktree's root `.gitignore`, not a global exclude or `.git/info/exclude`.

When the root rule is missing, require the root-anchored `/.pico-env.json` pattern. If a pico-cli
managed block exists or the project is configured, use the maintained project-configuration repair
path and never hand-edit between its markers; otherwise add that exact rule once in the user-owned
section covered by the approved plan. Re-run the check after repair. If Git already tracks or stages
the file, stop and obtain confirmation before `git rm --cached -- .pico-env.json`; never delete or
modify the working-tree file.

## Mandatory publishing-assets ignore gate

`<publish-root>/assets/` contains local upload inputs and is never Git release source. This rule is
limited to the root publishing directory and does not apply to application build inputs such as
`app/src/main/assets/`.

Before staging, require the publish root's `.gitignore` to contain the root-anchored `/assets/`
pattern outside any pico-cli managed block. Verify it with
`git check-ignore -v --no-index -- assets/`, and require the matching source to be the worktree root
`.gitignore`, not a global exclude or `.git/info/exclude`. Add the rule once when missing.

If `git ls-files -- assets` returns tracked or staged paths, remove only those paths from the index
with `git rm -r --cached -- assets`; preserve every working-tree file. Re-run both checks and require
`git ls-files -- assets` to return no paths before creating the source commit. Never use
`git add -f` to bypass this gate.

## Repository content screening

Repository screening is a user-decision gate, not the same as output redaction. Run a basic review:

1. Before staging or pushing files to GitHub.
2. Again immediately before the first Release `commit` that associates a new project with VibeLab.

Review only the files approved for the release commit plus relevant repository configuration. Look
for likely personal or development API keys, credentials, private-key material, credential-bearing
URLs, and politically sensitive content that may be inappropriate for a public repository. This is
a best-effort Agent review, not a strict policy engine or a guarantee that every sensitive value is
detected.

For every finding:

- Report only the repository-relative path, line or field location when safe, and risk category.
  Never display the matched secret or reproduce sensitive content.
- Check whether the path is already ignored and whether Git already tracks or stages it.
- When the path is not safely excluded, ask the user whether to add the exact path or the narrowest
  suitable pattern to `.gitignore`. Modify `.gitignore` only after explicit confirmation.
- Adding an ignore rule is insufficient for an already tracked or staged file. Explain that state
  and obtain confirmation before unstaging it or removing it from the Git index. Never delete the
  working-tree file automatically.
- The user may explicitly state that a flagged file or key is required and approve retaining it.
  Record the decision by path and risk category, then continue without repeating the sensitive
  value. Do not silently override the finding or silently allow it.
- Let the user resolve or explicitly accept findings as one consolidated review. Do not interrupt
  the scan with one confirmation per match.

The second scan before Release `commit` is a fallback reminder, not a hard rule-based rejection. It must
surface new or unresolved findings and obtain a decision before continuing. If the scan discovers
that a credential has already reached a remote repository, stop and require revocation or rotation
under the exposed-secret rule; an ignore entry cannot remove repository history.

## Redaction procedure

Before relaying or persisting output:

1. Parse structured JSON when available.
2. Select an allowlist of fields needed by the current stage; do not print the complete object.
3. Replace secret field values with `[REDACTED]`.
4. Remove URL user information and redact sensitive query parameters or fragments.
   Omit signed asset URLs entirely; do not preserve their host, path, signature, or expiry in a
   report.
5. Redact header values and common inline forms such as `Bearer ...`, `token=...`, `password=...`,
   and private-key blocks.
6. Preserve the error code, stage, resource IDs, and safe recovery action so the result remains
   diagnosable.
7. If parsing fails, treat the complete raw output as sensitive and report only the command, exit
   code, and a bounded redacted diagnostic.

Redaction failure is fail-closed. Do not emit raw output merely because a command failed.

## Safe failure examples

Prefer:

```text
GitHub authentication is unavailable for github.com. Run gh auth login --web --hostname github.com.
```

Do not report:

```text
GH_TOKEN=...
Authorization: Bearer ...
https://user:token@github.com/owner/repository.git
```

Prefer:

```text
pico-release-cli-cn failed with WRITE_OUTCOME_UNKNOWN for app_id 123. Run a read-only status check
before retrying.
```

Do not paste the raw success or failure envelope when it contains unreviewed nested fields.
