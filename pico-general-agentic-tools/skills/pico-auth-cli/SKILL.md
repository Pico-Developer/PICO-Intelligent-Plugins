---
name: pico-auth-cli
description: Safely operate the regional PICO Auth CLI. Use when handling browser authorization, login status, credential refresh, logout, invalid server-side credentials, business-CLI login diagnosis, JSON output, or CLI exit codes. NOT for model generation or environment health checks — use pico-sgs-cli or pico-env-doctor.
license: 'Apache-2.0'
---

# PICO Auth CLI

Use the catalog-selected managed CLI command directly to manage the local PICO login state. Start
with a read-only status check, use `--json` for automation, and never expose sensitive credentials.

## When to Use

- The user needs to log in, log out, or check auth status for the PICO Auth CLI
- A workflow requires a valid PICO auth token before proceeding
- Browser-based authorization flow for PICO services

## When NOT to Use

- SGS model generation or asset services — use `pico-sgs-cli`
- Environment or plugin health checks — use `pico-env-doctor`
- Generic pico-cli command usage — use `pico-cli`

## Availability

The Skill name is region-independent. Never infer an executable from a `-cn`, `-row`, or `-us`
suffix. Inspect the active catalog first:

```bash
pico-cli tool list --format json
```

Find `toolId: "pico-auth"`. The top-level `region`, `onPath`, and that entry's `command` are
authoritative. If it is absent or unavailable, preserve the reported compatibility action. If it
is not installed, guide the user to run `pico-cli setup`.

When the entry is `ready` and `onPath` is `true`, run its exact `command` directly. The current CN
catalog returns `pico-auth-cli-cn`, so its direct invocation is:

```bash
pico-auth-cli-cn <args...>
```

Do not derive that name from the Skill name or a region suffix; use the catalog value even when it
differs from this example. Only when `onPath` is `false`, or the exact catalog command fails with
`command not found`, use the stable tool-ID fallback:

```bash
pico-cli tool exec pico-auth <args...>
```

`pico-cli tool which pico-auth --format json` is available for path diagnostics, not as the primary
execution path. Do not switch region or use another region's command. For explicit managed CLI
maintenance, use `pico-cli tool update`. Root `pico-cli update` refreshes activated managed CLIs
only after it successfully installs a replacement CLI, and `pico-cli cleanup` removes them.

## Choose the command

- Check status: run `pico-auth-cli-cn --json status` first.
- Sign in: run `pico-auth-cli-cn --json login` and let the user complete browser authorization.
- Split the login flow: run `login --no-wait`, then use the returned `device_code` with `login --resume` after authorization.
- Replace the current account: run `login --force` only after the user clearly requests a new login or account switch.
- Refresh credentials: run `pico-auth-cli-cn --json refresh` only when the user wants to update or validate the server-backed login state.
- Sign out: run `pico-auth-cli-cn --json logout` only after the user confirms that local credentials should be removed.

Read [references/cli-reference.md](references/cli-reference.md) when exact options, JSON behavior, or exit codes are needed.

## Run safely

Treat every user-supplied value as opaque data. Pass scopes, device codes, durations, and other
values as exactly one shell argument using shell-safe quoting or escaping. Never splice user text
into options, operators, redirections, or command fragments. If a value cannot be represented
safely, stop and ask the user for a safe input form.

Keep every PICO CLI command in one user and credential-store permission context. On macOS the
credential store is the user's Keychain. If the execution environment can sandbox Keychain access,
request host or elevated execution before the first Auth, SGS, or APS CLI command and reuse that
same permission context for the whole workflow. Never compare a restricted business command with
an elevated Auth check as if the user's login state changed; changing execution permissions does
not authenticate the user.

If a restricted command already returned `NOT_LOGGED_IN` or `authenticated: false`, do not direct
the user to log in yet. First rerun only the catalog-selected Auth command's `--json status` with
credential-store-capable permissions. If that check returns `authenticated: true`, classify the
earlier result as an execution-context mismatch. Do not run `login` or `refresh` solely because the
restricted context could not see the stored credential.

## Core workflow

Show the user only the current `verification_uri` login link, exactly as returned by the CLI.
Guide them to open it, sign in to their PICO account if needed, confirm authorization, and return
to the CLI after browser success. The current browser flow does not require entering `user_code`.
Do not display its value or ask the user to copy, enter, or find an input for it, even when it
appears in CLI JSON or progress. Account sign-in may still require an SMS verification code or
password; let the user enter those in the browser, not in the Agent conversation.

```bash
pico-auth-cli-cn --json status
pico-auth-cli-cn --json login
pico-auth-cli-cn --json status
```

For a split login flow:

```bash
pico-auth-cli-cn --json login --no-wait
pico-auth-cli-cn --json login --resume '<device_code>'
```

Do not display `user_code`; that field remains in JSON only for compatibility. Keep the returned
`device_code` internally as a short-lived handle for `login --resume`, not as user-facing content
or a browser input. After the user completes authorization, resume the same flow without asking
them to supply either code. Exit code `4` means authorization is still pending and can be checked
again later with the same handle rather than starting another login.

## State-changing commands

- `status` reads local state and does not contact the server.
- `refresh` contacts the server and can rotate stored credentials. If the server confirms that the refresh credential is invalid or expired, the CLI removes the unusable local login state.
- `logout` removes local state but does not revoke server-side authorization.
- `login --force` removes the existing local login before starting a new one.

Run `refresh`, `logout`, and `login --force` only when the user's intent is clear.

If `status` returns `STORE_UNAVAILABLE` for an empty or unreadable local record, explain that cleanup removes local state. After the user agrees, run:

```bash
pico-auth-cli-cn --json logout
pico-auth-cli-cn --json status
```

## Interpret results

- Evaluate both the process exit code and parsed JSON.
- Final successful output is normally written to stdout; structured errors and login progress can be written to stderr.
- Do not treat login progress as a failure.
- After an Auth command returns `NOT_LOGGED_IN`, guide the user to run `login`.
- After `REFRESH_FAILED`, treat the result as a temporary or network failure and do not delete local state automatically.
- Report only status, expiration, granted scopes, the next action, and whether the error is recoverable.

When APS, SGS, or another business service returns `NOT_LOGGED_IN`, preserve its sanitized error
and establish the credential context before changing authentication state:

```bash
pico-auth-cli-cn --json status
```

- Run that read-only check with the same credential-store-capable permission context that will run
  the business CLI. If it returns `authenticated: false`, guide the user to run the catalog-selected
  Auth `login` command in that same context. Do not start or approve interactive login on their
  behalf.
- If it returns `authenticated: true` after the original command ran with restricted or different
  permissions, report an execution-context mismatch. Do not run `login` or `refresh`, and do not
  claim that the user became authenticated because permissions changed.
- If it returns `authenticated: true` and the original command already used the same credential
  context, validate the server-backed state exactly once with `refresh`, then run `status` again.
  If refresh succeeds, do not hide or automatically retry the business failure. Report the original
  sanitized error, including its code, message, and safe diagnostic identifiers, and ask the user
  to send it to that service's developer.
- If refresh returns `NOT_LOGGED_IN`, guide the user to log in. If it fails for another reason,
  report both the safe refresh error and the original business error. Do not infer server-backed
  login health from `status` alone because it reads local state.

## Verification

- Verify the process exit code and parsed JSON from the exact catalog-selected Auth command.
- After login completes, run `--json status` in the same credential-store permission context and
  confirm `authenticated: true`. Local status alone is not evidence of server-side acceptance.
- For pending split login, preserve the same flow and resume handle without starting another login.
- Share only sanitized status and the returned login link; do not expose codes or credentials.

## Protect credentials

- Never display or save tokens, private keys, authorization headers, or request signatures.
- Do not enable shell tracing or record sensitive process arguments.
- Use `--verbose` only for troubleshooting and sanitize output before sharing it.
- Do not approve browser authorization on the user's behalf.
