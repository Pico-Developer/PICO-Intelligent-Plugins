# PICO Auth CLI Reference

Run every command with the exact catalog-selected command established by the parent Skill. The
examples below use the current CN catalog value, `pico-auth-cli-cn`. Use
`pico-cli tool exec pico-auth` only when that command is not on `PATH`.

## Global options

| Option            | Meaning                                                   |
| ----------------- | --------------------------------------------------------- |
| `--json`          | Emit machine-readable JSON; prefer this for automation    |
| `--verbose`       | Emit additional diagnostics; use only for troubleshooting |
| `--help`, `-h`    | Show help                                                 |
| `--version`, `-v` | Show the installed CLI version                            |

Place global options before the subcommand for consistency:

```bash
pico-auth-cli-cn --json status
```

## `status`

```bash
pico-auth-cli-cn --json status
```

This command reads local state only. It does not contact the server or refresh credentials.

Common fields include `ok`, `status`, `authenticated`, `expires_at`, `scopes`, and `reason`. A locally valid status does not prove that the server has not revoked the credentials early.

## `login`

```bash
pico-auth-cli-cn --json login
pico-auth-cli-cn --json login --timeout 120s
pico-auth-cli-cn --json login --scope '<scope>' --scope '<other_scope>'
```

- `--timeout <duration>` sets the authorization wait time and accepts `ms`, `s`, or `m` units.
- `--scope <scope>` requests an additional scope and can be repeated.
- A valid existing login is preserved unless `--force` is used.
- `--force` removes existing local state and must only be used for an explicit new login or account switch.

Split flow:

```bash
pico-auth-cli-cn --json login --no-wait
pico-auth-cli-cn --json login --resume '<device_code>'
```

The first command returns `device_code`, `user_code`, `verification_uri`, and `expires_at` in
JSON mode. Forward only the current `verification_uri` login link to the user exactly as returned
by the CLI. Do not display `user_code` or instruct the user to enter an authorization code:
`user_code` remains in JSON only for compatibility. The current browser flow requires no user-code
input. Guide the user to sign in to their PICO account if needed, confirm authorization, and return
to the CLI. Account sign-in may still require an SMS verification code or password entered by the
user in the browser, not in the Agent conversation.

Keep `device_code` for the same flow's `--resume` command, not for display or browser input. Resume
after authorization without asking the user to supply either code. Exit code `4` with a `pending`
status means authorization is not complete; resume the same flow later rather than starting
another login.

## `refresh`

```bash
pico-auth-cli-cn --json refresh
```

This command contacts the server and can rotate stored credentials.

- Success saves the refreshed login state.
- `NOT_LOGGED_IN` with exit code `3` means a new login is required.
- A server-confirmed invalid or expired refresh credential removes the unusable local state.
- `REFRESH_FAILED` with exit code `6` represents a temporary, network, or unrecognized refresh failure and preserves local state.

Do not add shell timing output when another process expects pure JSON.

## `logout`

```bash
pico-auth-cli-cn --json logout
```

This command removes local login and pending-login state. It does not revoke server-side authorization. Confirm the user's intent before running it.

## End-to-end verification

Run this sequence only when the user explicitly requests a full login and logout check:

```bash
pico-auth-cli-cn --json status
pico-auth-cli-cn --json login
pico-auth-cli-cn --json status
pico-auth-cli-cn --json refresh
pico-auth-cli-cn --json logout
pico-auth-cli-cn --json status
```

## JSON streams

- Final successful results are written to stdout.
- Structured errors are written to stderr.
- Interactive login progress can also be written to stderr before the final result.
- Parse stdout and stderr separately, then use the process exit code to determine the outcome.
- Do not classify every stderr object as a failure.

## Exit codes

| Code | Meaning                                        | Recommended action                                                |
| ---: | ---------------------------------------------- | ----------------------------------------------------------------- |
|  `0` | Success                                        | Parse the result                                                  |
|  `1` | Unknown failure                                | Report sanitized diagnostics                                      |
|  `2` | Invalid arguments                              | Review `--help` and correct the command                           |
|  `3` | Not logged in or login state unavailable       | Run `login`                                                       |
|  `4` | Authorization pending                          | Complete authorization and retry `login --resume`                 |
|  `5` | Login flow or credentials expired              | Start a new login                                                 |
|  `6` | Network, timeout, or temporary service failure | Check connectivity and retry a limited number of times            |
|  `7` | Local credential storage unavailable           | Check local access; clean unreadable state only with user consent |
|  `8` | Authorization declined                         | Let the user decide whether to retry                              |

## Safety

- Treat every user-supplied scope, device code, duration, and other value as opaque data. Pass each
  value as exactly one shell argument using shell-safe quoting or escaping; never splice it into
  options, operators, redirections, or command fragments.
- If a value cannot be represented safely, stop and ask the user for a safe input form.
- Never display or save tokens, private keys, authorization headers, or request signatures.
- Do not enable shell tracing around authentication commands.
- Treat `device_code` as a login-flow handle, not an access token; do not display it to the user.
- Do not display `user_code`, even when it is present in compatibility JSON or login progress.
- Do not approve browser authorization for the user.
- Report only login status, expiration, granted scopes, the next action, and recoverability.
