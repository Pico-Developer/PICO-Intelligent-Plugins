# Repeated Unsuccessful Interaction Warning

Read when operating an application through `interact`, or when its result includes
`INTERACTION_FRICTION_HIGH`. This is a rolling efficiency warning, not a scene prohibition.
Existing authorization, scene restrictions and no-replay rules remain in force.

## Evidence And Counting

The CLI keeps bounded local history separately for each device/application across invocations.
It counts terminal operations and explicit follow-up `interact query` calls. Internal target
resolution, normal completion observation, animation and query volume alone are not failures.
Final completion observation timeout also does not prove an action failed. Preserve the real
dispatch receipt; report a business `unmet` outcome only when separate outcome evidence supports it.
`performed=true` only means acceptance; `changed=false` or `verified=false` alone does not
prove that the business expectation was missed.

Use the returned `operationId` to report an outcome only after checking the actual expected
business state. Preserve the action result and the operation ID; do not infer success from dispatch:

```bash
pico-cli interact feedback --device <serial> --package <package> \
  --operation-id <operation-id> --outcome unmet --format json
```

Use `--outcome met` when the expected business result is observed. Do not send extra queries just
to populate the monitor, and do not report `unmet` merely because an animation is still running.
Unknown or expired operation IDs are rejected. Repeated feedback does not add new failures.
A query response may return the preceding operation ID for late outcome feedback.

## Thresholds

Either rolling window can trigger the warning immediately when all its conditions hold:

| Window     | Action sample | Failure rate | At the minimum sample | Linked follow-up queries | Different unsuccessful operations |
| ---------- | ------------- | ------------ | --------------------- | ------------------------ | --------------------------------- |
| 10 minutes | At least 10   | At least 50% | At least 5 out of 10  | At least 3               | At least 3                        |
| 20 minutes | At least 20   | At least 50% | At least 10 out of 20 | At least 6               | At least 6                        |

The unsuccessful count must be at least half of the actual action count: 3 out of 10 and
9 out of 20 do not meet this threshold. Query and distinct-operation counts are additional
evidence conditions, not a lower failure-rate threshold. Successful actions do not trigger a warning.

These are initial product thresholds, not a claim about observed scene change rates. A frequent
successful workflow remains eligible. A repeated query cannot manufacture an unsuccessful action.
The CLI cannot determine the cause: scene changes, selectors or other application behavior may
contribute. Explain that uncertainty rather than declaring that animation makes AI unsupported.

## User Decision

When a warning is present:

1. Pause automatic retries. Explain the actual window, action count, unsuccessful count and
   follow-up query count in the user's language, then say that the scene may be changing too
   frequently for efficient AI operation. Do not report a confirmed cause.
2. Ask the user to choose **continue AI operation** or **manual takeover**. Wait for an explicit
   answer; silence is not consent. Do not silently continue or choose for the user.
3. Only after that answer, acknowledge the same warning ID:

```bash
pico-cli interact feedback --device <serial> --package <package> \
  --warning-id <warning-id> --decision continue --format json
```

For manual takeover use `--decision manual` and stop the automatic operation task. For continue,
replan from current state if needed and verify outcomes; never replay uncertain accepted work.
Both choices reset the acknowledged history. New unsuccessful operations can produce a new
warning. Before acknowledgment, repeated responses carry the same warning ID while current counts
are recomputed from rolling history; a pending decision can remain after counts fall below the threshold.
A stale ID cannot acknowledge a different or expired warning.

A suggested explanation is: "During the last N minutes I attempted A actions; F did not achieve
the expected result and I needed Q follow-up checks. The scene may be changing too frequently,
which can make AI operation less reliable or efficient. Would you like me to continue, or would
you prefer to take over manually?" Translate it and substitute only actual returned counts.

## Monitor Failure

`INTERACTION_MONITOR_UNAVAILABLE` means local statistics could not be maintained. It does not
change the original action result or prove a dynamic scene. Outcome/decision feedback that cannot
be stored is rejected; never claim the choice was acknowledged after such an error.
