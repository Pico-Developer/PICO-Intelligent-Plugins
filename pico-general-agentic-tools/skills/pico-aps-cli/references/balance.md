# Balance command

Use this reference after the APS CLI skill selects `balance` for current PICO AI Generation Service
credit questions or an APS-backed generation workflow balance check.

## Inputs and command

Run `pico-aps-cli-cn balance --json` with the command selected by the parent Skill. Add
`--app-id '<appId>'` only for a positive
application ID supplied by the user; do not invent one or reinterpret another identifier. For example:

```bash
pico-aps-cli-cn balance --app-id '<appId>' --json
```

## Interpret the result

On exit `0`, require `ok: true` and `command: "balance"`, then read the top-level `balance` object:

| Field                    | Meaning                                                                |
| ------------------------ | ---------------------------------------------------------------------- |
| `total_available`        | Total credits currently available                                      |
| `total_frozen`           | Credits currently frozen                                               |
| `biz_free_available`     | Business-specific free credits                                         |
| `common_free_available`  | Common free credits                                                    |
| `subscription_available` | Subscription credits                                                   |
| `purchase_available`     | Credits obtained through an earlier purchase                           |
| `items`                  | Individual credit packages, app association, frozen amount, and expiry |
| `next_refresh_at`        | Next expected balance refresh time                                     |
| `subscription_expire_at` | Subscription expiry time                                               |

Treat absent optional timestamps as unavailable, not immediate expiry, and preserve returned time
zones. `purchase_available` is a credit category, not a purchase or order-query capability.

On failure, report the safe JSON error from stderr and its smallest useful next action. Do not
infer a balance from a failed request.

## Query and reporting policy

| Context                                          | Action                                                                                                                                                                                                                                                        |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Explicit balance request                         | Report available and frozen credits first; add requested details. Report query failure truthfully                                                                                                                                                             |
| Before a single generation                       | Do not query credits                                                                                                                                                                                                                                          |
| Before a batch                                   | Check available credits and expected consumption using available CLI/service capabilities; do not invent endpoints or commands. If potentially insufficient, warn and confirm whether to continue. Warn once that the batch may consume more credits and time |
| After generation or the whole batch              | If APS is available, query once and briefly report verified remaining available credits; do not query per asset                                                                                                                                               |
| Automatic completion query unavailable or failed | Deliver generation results without proactively mentioning the missing balance; never reuse an old balance or infer generation failure                                                                                                                         |
| Ordinary discussion, polls, repeated downloads   | Do not query balance routinely                                                                                                                                                                                                                                |

Show categories, expiry, or balance differences only when requested or relevant. A balance
difference alone is not a task charge; require matching ledger or settlement evidence.
