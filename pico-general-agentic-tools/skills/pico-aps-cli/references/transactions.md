# Transactions command

Use this reference after the APS CLI skill selects `transactions` for the PICO AI Generation
Service credit ledger history. One item is one append-only credit-package ledger entry, not an
application-store order or proof of payment.

## Filters and command

Use only filters supplied or clearly requested by the user:

| Option                       | Meaning and constraint                                      |
| ---------------------------- | ----------------------------------------------------------- |
| `--app-id '<appId>'`         | Positive application ID                                     |
| `--txn-type <1-8>`           | APS ledger transaction type from the table below            |
| `--start-time '<RFC3339>'`   | Inclusive lower creation-time bound                         |
| `--end-time '<RFC3339>'`     | Inclusive upper bound; cannot precede start time            |
| `--page <page>`              | Positive page number; defaults to `1`                       |
| `--page-size <1-100>`        | Page size; defaults to `20`, maximum `100`                  |
| `--request-id '<requestId>'` | Application-scoped business request ID; requires `--app-id` |

| Type | Meaning              |
| ---- | -------------------- |
| `1`  | Deduct               |
| `2`  | Refund               |
| `3`  | Grant                |
| `4`  | Expire clear         |
| `5`  | Operation adjustment |
| `6`  | Freeze               |
| `7`  | Freeze offset        |
| `8`  | Freeze rollback      |

Map unambiguous wording to the enum. When wording could mean multiple types, omit the type filter
and explain that results include all transaction types. Do not invent an app ID, request ID, time
range, or type. Preserve an RFC3339 time zone supplied by the user; if they give a local time
without an offset, ask for its time zone before querying.

Start with:

```bash
pico-aps-cli-cn transactions --json
```

For one business request, pair `--app-id` with `--request-id`. For example:

```bash
pico-aps-cli-cn transactions --app-id '<appId>' --request-id '<requestId>' --json
```

## Interpret the result

On exit `0`, require `ok: true` and `command: "transactions"`, then read the top-level
`transactions` object. `items` are the current page, `total` is the matching entry count,
`page` is the returned page, and `page_size` is its effective size.

Each item may include `txn_id`, `request_id`, `txn_type`, signed `amount`, `instance_id`,
`credit_type`, `app_id`, `capability`, `created_at`, `freeze_order_id`, `payment_order_id`,
`grant_id`, `operator`, and `remark`. Preserve the amount sign and the time zone in `created_at`.
Do not aggregate entries merely because they share a `request_id`; one business request can create
multiple rows across credit packages. A payment-related field does not prove payment succeeded.

Report filters, matching total, and page coverage. If the user explicitly asks for all matching
entries, follow subsequent pages with the same filters and `--page-size 100` until collected items
cover `total`; never present the first page as complete when more pages exist. On failure, report
the safe JSON error from stderr without inventing ledger data.
