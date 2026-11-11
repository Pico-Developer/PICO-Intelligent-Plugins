# Task query and download commands

Use this reference after the SGS CLI skill selects `get_task` or `download` for an existing SGS
task.

## Task identity

Both commands require one exact `<task_id>` and explicit `--type 3d|image`. The services use
different endpoints and task ID spaces, so the CLI cannot infer the type. If prior generation
context does not establish it, ask the user whether the task is `3d` or `image`; never probe both
endpoints.

## Query and monitor

Run one query with:

```bash
pico-sgs-cli-cn get_task <task_id> --type <3d|image> --json
```

On exit `0`, require `ok: true` and interpret the normalized `data.status`:

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
an existing task, query immediately and then every 10 seconds while it remains `pending` or
`running`. Use the user's deadline, or a bounded `5m` deadline when none is supplied. Do not reset
the deadline after transient errors. Retry exit `6` `NETWORK_TEMPORARY` only within that read-only
polling deadline; stop on terminal status or any non-recoverable error.

## Download artifacts

Collect an explicit output prefix, then run:

```bash
pico-sgs-cli-cn download <task_id> --type <3d|image> \
  -o <prefix> --json
```

The output value is a filename prefix, not a directory or complete final filename:

| Task type       | Output names           |
| --------------- | ---------------------- |
| 3D              | `{prefix}.{glb         | fbx    | obj}` |
| One image       | `{prefix}.{png         | jpeg}` |
| Multiple images | `{prefix}_{index}.{png | jpeg}` |

Only `succeeded` tasks can be downloaded. `pending` or `running` exits `6` without writing an
artifact; `failed` exits `10`.

Existing targets are rejected before artifact fetch. Add `--force` only when the user explicitly
authorizes replacing existing regular files:

```bash
pico-sgs-cli-cn download <task_id> --type <3d|image> \
  -o <prefix> --force --json
```

Never use `--force` for a directory or symbolic link. The CLI still rejects non-regular targets.

The optional download `--timeout <positive-duration>` controls one shared batch deadline and
defaults to `3m`. The duration requires `ms`, `s`, or `m`. Multi-file downloads are serial and
committed as one batch; on failure, the CLI cleans temporary files and rolls back replacement work
when possible.

## Interpret the download result

On exit `0`, require `ok: true` and return final local files from `data.paths` exactly as produced.
On exit `12`, report the safe download, path, overwrite, network, size-limit, cleanup, or rollback
error without claiming that partial output is valid.

The CLI owns signed-URL validation, redirects, streaming, the cumulative size limit, naming,
conflict checks, and transactional commit. Do not expose signed artifact URLs or replace the
download command with `curl` or a custom downloader.
