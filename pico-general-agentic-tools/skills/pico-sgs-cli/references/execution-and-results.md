# CLI execution and results

Before a command, read Run safely. For authentication or errors, read Recover login and Handle
errors and protect credentials. For existing tasks, read Task identity and the matching
query/download section. After a 3D download, read Inspect, repair, and recheck and Deliver a 3D
model.

## Run safely

Treat every user-supplied value as opaque data. Pass prompts, paths, URLs, URIs, IDs, timestamps,
and output prefixes as exactly one shell argument using shell-safe quoting or escaping. Never splice
user text into options, operators, redirections, or command fragments. If a value cannot be
represented safely, stop and ask the user for a safe input form.

Run every SGS, APS, and Auth CLI command in one user and credential-store permission context. On
macOS these CLIs read the user's Keychain. If the execution environment can sandbox Keychain
access, request host or elevated execution before the first PICO CLI command and reuse that same
permission context for the entire workflow. Do not run SGS in a restricted context and diagnose it
with Auth in an elevated context; permission changes do not mean the user's login state changed.

1. Collect only necessary inputs. Choose models, quality, and target face counts from explicit user
   requirements or this Skill's defined policies. Do not invent available models, capabilities,
   task types, or task IDs. Derive output format and paths from user requirements and workspace
   conventions; clarify when necessary.
2. Run the selected command with `--json`. Use supported parameters explicitly specified by the
   user or derived from this Skill's policies. Explicit user requirements take priority; the
   current CLI and service determine parameter limits.
3. Check the process exit code before interpreting output. Exit `0` yields one JSON object on
   stdout with `ok: true`; nonzero exits yield one safe JSON error object on stderr.
4. Preserve returned task IDs, normalized statuses, task types, and downloaded paths exactly.
   Never expose or reconstruct signed artifact URLs.
5. Never automatically retry a generation command. Creation has no idempotency key and may consume
   credits. `SUBMISSION_OUTCOME_UNKNOWN` means the service may already have created the task.
6. If a generation command using `--wait` exits nonzero with `data.task_id`, creation succeeded but
   observation was interrupted. Return the task ID, do not resubmit, and advise the user to wait
   before querying it again with `get_task` and the known task type.

The CLI owns OAuth injection, gateway signing, local-image upload, endpoint selection, polling,
download validation, and output redaction. Do not reconstruct HTTP or ImageX requests, edit the
installed package, or fall back to a hand-written `curl` request.

## Recover login

When an SGS command exits `3` with `code: NOT_LOGGED_IN`, preserve its sanitized error. Do not rerun
the generation command. Inspect `stage` first: `auth_store` means the local credential read failed
and the request was not sent; `auth_inject` means refresh, signing, or header injection failed and
the request was not sent; `backend` means the request reached the service and was rejected, so
preserve `details.backend_code` and `details.log_id` when present.

First run the catalog-selected Auth command's read-only `--json status` check in the same
credential-store-capable permission context that will run SGS.

- If status returns `authenticated: false`, tell the user to run Auth `login` in that same context.
  Do not start interactive login on their behalf. After login, retry a read-only query or download
  when appropriate; require explicit authorization before resubmitting generation.
- If status returns `authenticated: true` after SGS ran with restricted or different permissions,
  classify the failure as an execution-context mismatch. Do not run `login` or `refresh`. Never
  automatically rerun generation after changing permissions; require explicit authorization
  because the original submission outcome may be unclear.
- If status returns `authenticated: true` and SGS already used the same credential context, run
  Auth `refresh`, then `status`, exactly once. If refresh succeeds, do not retry SGS automatically.
  Report the original sanitized SGS error and safe backend identifiers for escalation.
- If refresh returns `NOT_LOGGED_IN`, tell the user to log in. If it fails for another reason,
  report both safe errors. Local `status` alone does not prove server-backed login health.

Never ask the user to paste OAuth credentials or device-signing material into chat.

## Handle errors and protect credentials

Use the safe top-level `stage` before interpreting a request failure. Do not describe `auth_store`
or `auth_inject` as a service rejection, and do not describe `backend` as proof that the credential
store is empty. Preserve backend `details.backend_code` and `details.log_id`.

| Exit    | Response                                                                                                                                             |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `1`     | Report a submission-side backend-internal, unknown, protocol, signing, or uncertain-submission failure; never retry generation                       |
| `2`     | Correct invalid syntax, enums, mutually exclusive flags, task type, or task ID usage                                                                 |
| `3`     | Follow Recover login; never automatically resubmit generation                                                                                        |
| `4`-`9` | Preserve the authentication, credential-store, network, timeout, or cancellation error and its action                                                |
| `10`    | Report task failure, quota rejection, access denial, or another business rejection                                                                   |
| `11`    | Report gateway or cross-service deployment/signing failure; do not request an AppKey                                                                 |
| `12`    | Report download, filesystem, overwrite, cleanup, or rollback failure                                                                                 |
| `13`    | A `get_task` or `download` query did not return a result. The task is unaffected; do not resubmit, and query it later with the same task ID and type |

Treat `recoverable` as metadata, not permission to repeat a credit-consuming create request.
Distinguish a failed query from failed generation. Exit `13` `TASK_QUERY_UNAVAILABLE` means only
that this query attempt failed; the task continues on the backend and may already be complete.
Never report the task as lost or ask the user to resubmit. Exit `1` `BACKEND_INTERNAL_ERROR`
instead comes from generation or submission; preserve safe backend identifiers and do not retry.

Never print, summarize, persist, or return OAuth credentials, device signatures, gateway signing
material, upload credentials, signed artifact URLs, or credential-bearing commands.

## Task identity

`get_task` and `download` require one exact `'<task_id>'` and explicit `--type 3d|image`. The
services use different endpoints and task ID spaces, so the CLI cannot infer the type. If prior
context does not establish it, ask whether the task is `3d` or `image`; never probe both endpoints.

## Query and monitor

Run one query with:

```bash
pico-sgs-cli-cn get_task '<task_id>' --type '<3d|image>' --json
```

On exit `0`, require `ok: true` and interpret `data.status`:

| Status      | Meaning                                       |
| ----------- | --------------------------------------------- |
| `pending`   | Accepted but not yet processing               |
| `running`   | Processing                                    |
| `succeeded` | Terminal success; artifacts may be downloaded |
| `failed`    | Terminal failure                              |

Preserve useful non-sensitive metadata, but do not expect or reconstruct artifact URLs. A
task-not-found response can also mean the wrong type; ask the user to verify both values instead of
trying the other endpoint automatically.

`get_task` performs one query and has no `--wait` option. When the user explicitly asks to monitor
an existing task, query immediately and every 10 seconds while it remains `pending` or `running`.
Use the user's deadline or a bounded `5m` deadline. Do not reset the deadline after transient
errors. Within it, retry exit `6` `NETWORK_TEMPORARY` and exit `13` `TASK_QUERY_UNAVAILABLE`; stop
on terminal status or a non-recoverable error.

A query failure is not a generation failure. Keep the same task ID and type and query again later.

## Download artifacts

Collect an explicit output prefix, then run:

```bash
pico-sgs-cli-cn download '<task_id>' --type '<3d|image>' \
  -o '<prefix>' --json
```

The output value is a filename prefix, not a directory or complete final filename:

| Task type       | Output names                                 |
| --------------- | -------------------------------------------- |
| 3D              | `{prefix}.glb` with current service adapters |
| One image       | `{prefix}.{png\|jpeg}`                       |
| Multiple images | `{prefix}_{index}.{png\|jpeg}`               |

The CLI can parse compatible 3D format metadata, but current adapters produce GLB. Do not promise,
request, or infer FBX or OBJ output unless service capability changes.

Only `succeeded` tasks can be downloaded. `pending` or `running` exits `6` without writing an
artifact; `failed` exits `10`.

Existing targets are rejected before fetch. Add `--force` only when the user explicitly authorizes
replacing existing regular files:

```bash
pico-sgs-cli-cn download '<task_id>' --type '<3d|image>' \
  -o '<prefix>' --force --json
```

Never use `--force` for a directory or symbolic link. The CLI still rejects non-regular targets.

The optional `--timeout '<positive-duration>'` controls one shared batch deadline and defaults to
`3m`. Multi-file downloads are serial and committed as one batch; on failure, the CLI cleans
temporary files and rolls back replacement work when possible.

## Interpret the download result

On exit `0`, require `ok: true` and return final local files from `data.paths` exactly as produced.
On exit `12`, report the safe error without claiming partial output is valid. On exit `13`, the
pre-download status query did not return a result; the task is unaffected, so retry download later
or query the task first.

The CLI owns signed-URL validation, redirects, streaming, size limits, naming, conflict checks, and
transactional commit. Do not expose signed URLs or replace download with a custom downloader.

## Inspect, repair, and recheck

| Check      | Required action                                                                                                                                                                                     |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Files      | Verify readability and complete geometry/material loading. Recover existing results first; do not regenerate to recover a download                                                                  |
| Appearance | Compare front, side, and back views with the request and approved image for missing/extra structure, distortion, and texture defects. Exclude viewer, loading, and lighting issues first            |
| Budget     | Measure exported geometry under the scene-wide policy in [3d-generation.md](3d-generation.md#model-routing-texture-quality-and-scene-polygon-budget); mark unverified when evidence is insufficient |
| Repair     | Prefer local repair over regeneration. With tools and verification, fix clear fragments/spikes, normals, small mesh defects, material links, or reduce geometry while preserving silhouette/details |
| Recheck    | Keep the original and save repairs separately. Preserve design, UVs, materials, rigging, and animation. Compare the same view and other angles; recheck loading and counts. Revert harmful repairs  |

A sharp corner or small connected component alone is not grounds for deletion. Do not use global
smoothing to hide local defects or repeat blind repairs. Blender is optional. Confirm a specific
solution for unclear design intent, major redesign, or paid regeneration beyond authorization.

Report normal results briefly. For problems, explain impact, repairs, and remaining uncertainty.
Distinguish task success, file usability, visual inspection, and target-environment validation.

## Deliver a 3D model

1. Open the downloaded model in an available host/native preview or compatible browser viewer.
2. Use a neutral background and wait for geometry and materials to load. Capture at least one clear
   screenshot of the complete subject, silhouette, and materials; add useful angles. Do not add
   titles, provider/model labels, instruction cards, status overlays, or decorative panels.
3. Return the actual-model screenshot with the model file or download entry. Never substitute the
   reference image. A Web or playable preview may supplement screenshots, never replace them.
4. State whether effects are embedded in the model or Web-only. A preview does not authorize public
   deployment or asset upload. Follow the root Skill for naming and provider disclosure.

If preview is unavailable, deliver the file, explain why the screenshot remains incomplete, and do
not claim visual inspection succeeded.
