---
name: pico-aps-cli
description: Operate the regional PICO APS CLI for PICO AI Generation Service credit tasks, including checking the current credit balance, available or frozen credits, package expiry and refresh time; getting or opening the APS Web recharge or top-up page; and querying credit transaction history or ledger entries such as deductions, refunds, grants, adjustments, freezes, and request IDs. Trigger for equivalent APS requests in any language. APS is a general service, not a PICO application-store wallet, order, purchase, or payment service.
license: 'Apache-2.0'
allowed-tools: 'Bash(pico-cli tool list *) Bash(pico-cli tool which pico-aps *) Bash(pico-cli tool exec pico-aps *) Bash(pico-aps-cli-cn *) Bash(pico-auth-cli-cn *)'
---

# APS CLI

Use the catalog-selected managed CLI command directly for APS credit operations. APS is a shared
service; it does not depend on a Spatial or Unity project, a connected device, or the current
working directory.

## When NOT to Use

- PICO application-store wallets, orders, purchases, payments, invoices, or billing disputes
- SGS generation or artifact operations — use `pico-sgs-cli`
- PICO login or credential lifecycle operations — use `pico-auth-cli`
- Generic pico-cli discovery, setup, or diagnostics — use `pico-cli`

## Availability

The Skill name is region-independent. Never infer an executable from a regional suffix. Inspect the
active catalog:

```bash
pico-cli tool list --format json
```

Find `toolId: "pico-aps"`. The top-level `region`, `onPath`, and that entry's `command` are
authoritative. If it is absent or unavailable, preserve the reported compatibility action. If it
is not installed, guide the user to run `pico-cli setup`.

When the entry is `ready` and `onPath` is `true`, run its exact `command` directly. The current CN
catalog returns:

```bash
pico-aps-cli-cn <args...>
```

Do not derive that name from the Skill name or a region suffix. Only when `onPath` is `false`, or
the exact catalog command fails with `command not found`, use:

```bash
pico-cli tool exec pico-aps <args...>
```

`pico-cli tool which pico-aps --format json` is for path diagnostics, not primary execution. Do not
switch region or use another region's command. For explicit managed CLI maintenance, use
`pico-cli tool update`. Root `pico-cli update` refreshes activated managed CLIs only after it
successfully installs a replacement CLI, and `pico-cli cleanup` removes them.

## Choose a command

Read the matching reference before running a command. For a request spanning capabilities, read
each matching reference and run the commands separately.

| User intent                                                                                        | Command        | Read first                                               |
| -------------------------------------------------------------------------------------------------- | -------------- | -------------------------------------------------------- |
| Current available or frozen credits, categories, package expiry, refresh time                      | `balance`      | [references/balance.md](references/balance.md)           |
| APS Web recharge page URL, optionally opened in the default browser                                | `recharge`     | [references/recharge.md](references/recharge.md)         |
| Credit ledger, deductions, refunds, grants, adjustments, freezes, request IDs, time-range activity | `transactions` | [references/transactions.md](references/transactions.md) |

Do not substitute APS data for PICO application-store wallet balances or historical orders. This
skill cannot create purchases, submit payments, confirm recharge results, inspect invoices, or
resolve billing disputes. A recharge URL is not a completed recharge; a ledger entry is not an
order or proof of payment.

## Run safely

Treat every user-supplied value as opaque data. Pass paths, URLs, IDs, timestamps, and other values
as exactly one shell argument using shell-safe quoting or escaping. Never splice user text into
options, operators, redirections, or command fragments. If a value cannot be represented safely,
stop and ask the user for a safe input form.

Run every APS and Auth CLI command in one user and credential-store permission context. On macOS
these CLIs read the user's Keychain. If the execution environment can sandbox Keychain access,
request host or elevated execution before the first PICO CLI command and reuse that same permission
context for the entire workflow. Do not run APS in a restricted context and diagnose it with Auth
in an elevated context; permission changes do not mean the user's login state changed.

1. Use the selected command with `--json`, adding only supported options supplied or clearly
   requested by the user. In particular, open the browser only when explicitly requested.
2. Check the process exit code before interpreting output. Exit `0` yields one JSON object on
   stdout with `ok: true` and the expected `command`; nonzero exits yield a safe JSON error on
   stderr. The recharge browser-open failure is a special case described in its reference.
3. Report the requested data. Preserve returned URLs, signed amounts, timestamps, time zones,
   identifiers, and pagination semantics.

The CLI owns endpoint selection, request signing, login-state injection, timeout handling, browser
launch, and response validation. Do not reconstruct HTTP requests or signatures, modify the CLI
package, or fall back to a hand-written `curl` request.

## Report results

Use **PICO AI Generation Service credits** as the user-facing credit name; shorten it to
**credits** when context is clear.
Keep CLI names, environment variables, and response fields unchanged. For an explicit balance
request or an APS-backed generation completion, follow the reporting rules in
[references/balance.md](references/balance.md). Do not assume native Agent generation uses APS
credits.

## Recover login

When an APS command exits `3` with `code: NOT_LOGGED_IN`, preserve its sanitized error. Inspect
`stage` before diagnosing it: `auth_store` means the local credential read failed and the request
was not sent; `auth_inject` means refresh, signing, or header injection failed and the request was
not sent; `backend` means the request reached APS and was rejected, so preserve
`details.backend_code` and `details.log_id` when present.

First run the catalog-selected Auth command's read-only `--json status` check in the same
credential-store-capable permission context that will run APS.

- If status returns `authenticated: false`, tell the user to run Auth `login` in that same context.
  Do not start interactive login on their behalf. After the user confirms login succeeded, retry
  the original APS command once.
- If status returns `authenticated: true` after APS ran with restricted or different permissions,
  classify the failure as an execution-context mismatch. Do not run `login` or `refresh`; retry APS
  at most once in the same credential-store-capable context.
- If status returns `authenticated: true` and APS already used the same credential context, run
  Auth `refresh`, then `status`, exactly once. If refresh succeeds, do not retry APS automatically.
  Report the original sanitized APS error and its safe identifiers to the user for escalation.
- If refresh returns `NOT_LOGGED_IN`, tell the user to log in. If it fails for another reason,
  report both safe errors. Local `status` alone does not prove server-backed login health.

## Handle errors and protect credentials

Use the safe top-level `stage` before interpreting a request failure. Do not describe `auth_store`
or `auth_inject` as an APS rejection, and do not describe `backend` as proof that the credential
store is empty. Preserve backend `details.backend_code` and `details.log_id`.

| Exit | Response                                                                                                                                                             |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `2`  | Correct invalid options using the relevant subcommand help                                                                                                           |
| `3`  | For `NOT_LOGGED_IN`, follow Recover login. For other business or validation errors, report the error without inventing data                                          |
| `4`  | Browser launch failed after a recharge URL was returned; follow the recharge reference                                                                               |
| `5`  | If the access key is missing, ask the user to configure `PICO_APS_ACCESS_KEY` in the executing environment. The CLI obtains SK automatically before each APS request |
| `6`  | Report network, timeout, cancellation, or HTTP failure and suggest retry only when appropriate                                                                       |

Never print, summarize, persist, or return AK, SK, Cookie, Authorization, request signatures, or
credential-bearing commands. Do not ask the user to paste credentials into chat.
