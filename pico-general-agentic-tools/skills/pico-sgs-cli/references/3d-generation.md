# 3D generation commands and policies

Follow the asset workflows in [SKILL.md](../SKILL.md). This reference defines command selection,
inputs, model and budget policies, and submission behavior.

## Choose the command

| Source                                                                       | Command       | Required input               |
| ---------------------------------------------------------------------------- | ------------- | ---------------------------- |
| Text description - available but not recommended; use when explicitly chosen | `text_to_3d`  | `--prompt '<text>'`          |
| One source image                                                             | `image_to_3d` | `--image '<path\|url\|uri>'` |

Use `image_to_3d` when an image is the source, even when the user also supplies an optional prompt.
It accepts exactly one image. Do not add placeholder prompt text when the user omits it.

## Options and inputs

Add supported options explicitly requested by the user or selected under the model, texture, and
polygon-budget policy below:

| Option                       | Accepted values and behavior                                                                                                |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `--model`                    | A case-sensitive slug available in the current service; see the list below                                                  |
| `--quality`                  | `default` or `high`; omitted means `default`                                                                                |
| `--texture` / `--no-texture` | Mutually exclusive explicit texture choice                                                                                  |
| `--texture-quality`          | `standard` or `high`                                                                                                        |
| `--target-polycount`         | Positive decimal int32; omitted means `20000`, or `200000` with `--quality high`; model-specific limits remain server-owned |

Current model availability:

- `tripo-v3.1`
- `rodin-2.5-extreme-low`
- `rodin-2.5-low`
- `rodin-2.5-medium`
- `rodin-2.5-high`
- `rodin-2.5-extreme-high`

The service routes omitted `--model` values as follows. Apply this Skill's selection policy first;
service defaults are not recommended for every task:

| Command       | `default` quality       | `high` quality           |
| ------------- | ----------------------- | ------------------------ |
| `text_to_3d`  | `rodin-2.5-extreme-low` | `rodin-2.5-extreme-high` |
| `image_to_3d` | `rodin-2.5-medium`      | `rodin-2.5-extreme-high` |

Do not add `--extra`. It is a reserved compatibility option that the CLI rejects before
authentication or task creation because the service does not consume it. Prompt content and
model-specific polycount limits remain server-owned.

Classify an `image_to_3d` source as follows:

- An absolute HTTP(S) URL is sent as a URL.
- An existing regular local file is uploaded automatically before task creation.
- An ImageX URI is sent as a URI.
- An explicit missing or non-regular path is invalid; do not reinterpret it as a URI.

Do not upload a local file manually or call ImageX outside the CLI.

## Model routing, texture quality, and scene polygon budget

Explicit user choices take priority. For a single asset, default to `--model tripo-v3.1`: it is
somewhat slower and generally produces better results. For batch-generated minor assets that
occupy only a small part of the asset group or scene, use `--quality default` without specifying
`--model`; do not apply this to all batch assets indiscriminately. Judge major and minor assets
separately and never invent a model.

Use `--texture-quality high` only when exceptionally high material quality is required. Do not make
it the ordinary default or confuse it with `--quality high`.

Allocate `--target-polycount` using existing assets, planned counts, importance, and reuse within
the current scene. For Swan applications, the recommended total for one scene is no more than
1,000,000 faces. For other platforms, use their actual requirements. This is a Swan scene-budget
recommendation, not a per-asset allowance or hard technical limit. Do not invent fixed allocation
ratios. State budget assumptions or ask for necessary information when context is insufficient.

Verify how the CLI target and inspection tool count geometry, including polygons versus triangles
and instance counts. Check actual exported models instead of treating the requested target as the
measured result; include scene instances of reused assets. If over budget, first try
appearance-preserving decimation or budget redistribution, then recheck.

## Run and interpret

Prefer JSON output:

```bash
pico-sgs-cli-cn text_to_3d --prompt '<text>' --json
pico-sgs-cli-cn image_to_3d --image '<path|url|uri>' --json
```

Append options requested by the user or selected under this Skill's policy. Add `--wait` only when
the user asks to wait for terminal status:

```bash
pico-sgs-cli-cn text_to_3d --prompt '<text>' \
  --wait --timeout '<positive-duration>' --json
```

The duration requires `ms`, `s`, or `m`, defaults to `5m`, and is valid only with `--wait`.
Waiting observes the task; it does not download the artifact.

On exit `0`, require `ok: true`, `data.task_id`, and a normalized `data.status`. Without `--wait`,
the expected status is `pending`. With `--wait`, return `succeeded` on terminal success. A wait
timeout exits `6` and preserves the task ID plus the last known status when available.

The result intentionally omits the artifact URL. For later status checks or download, use
[execution-and-results.md](execution-and-results.md) with `--type 3d`.

## Submission safety

Never automatically retry `text_to_3d` or `image_to_3d`. `SUBMISSION_OUTCOME_UNKNOWN` / exit `1`
means task creation may already have succeeded, so warn against resubmission. For other failures,
report the safe JSON error from stderr and its smallest useful action without inferring that a task
exists unless a task ID was returned.

When a `--wait` error contains `data.task_id`, the task was created and may still consume credits or
finish successfully. Return the task ID and last known status, do not run another generation
command, and tell the user to wait before querying the same ID with `get_task --type 3d`.
