# Credit estimation command

Use this reference after the SGS CLI skill selects `estimate_credits` for a pre-generation credit
estimate.

## Choose the generation

Use exactly one supported generation name:

| Intended task                   | Generation       |
| ------------------------------- | ---------------- |
| Text-to-3D                      | `text_to_3d`     |
| Image-to-3D                     | `image_to_3d`    |
| Text-to-image or image-to-image | `image_generate` |

The estimate is read-only. It does not create a task, freeze credits, validate that the eventual
generation is executable, or promise the final charge. The later generation request's freeze is
authoritative.

## Build the estimate

Start with:

```bash
pico-sgs-cli-cn estimate_credits '<text_to_3d|image_to_3d|image_generate>' --json
```

Add only model and billing-related options explicitly supplied or requested by the user.

For `text_to_3d` and `image_to_3d`, supported estimation options are:

| Option                       | Accepted values                                                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `--model`                    | `tripo-v3.1`, `rodin-2.5-extreme-low`, `rodin-2.5-low`, `rodin-2.5-medium`, `rodin-2.5-high`, or `rodin-2.5-extreme-high` |
| `--quality`                  | `default` or `high`                                                                                                       |
| `--texture` / `--no-texture` | Mutually exclusive explicit texture choice                                                                                |
| `--texture-quality`          | `standard` or `high`                                                                                                      |
| `--target-polycount`         | Positive decimal int32 from `1` through `2147483647`                                                                      |

For `image_generate`, supported estimation options are:

| Option                              | Accepted values                                                                          |
| ----------------------------------- | ---------------------------------------------------------------------------------------- |
| `--image '<reference-placeholder>'` | Repeat once per intended reference image; only the count is used                         |
| `--model`                           | `seedream-5-pro`                                                                         |
| `--size`                            | A non-empty size such as `1K`, `1.5K`, `2K`, or `WIDTHxHEIGHT`; the service validates it |
| `--output-format`                   | `png` or `jpeg`                                                                          |
| `--background`                      | `opaque` or `transparent`                                                                |
| `--watermark` / `--no-watermark`    | Mutually exclusive explicit watermark choice                                             |

Do not add `--prompt`; prompt content does not affect the estimate and is never sent. For
`image_to_3d`, do not add `--image`; image content does not affect its current estimate.

For `image_generate`, reference count selects text-to-image or image-to-image pricing. Add one fixed
non-sensitive placeholder per intended image instead of real paths, URLs, or URIs:

```bash
pico-sgs-cli-cn estimate_credits image_generate \
  --image '<reference-placeholder>' --image '<reference-placeholder>' --json
```

The CLI uses only the number of repeated `--image` options. It does not inspect paths, read local
files, access image URLs, upload images, or send placeholder values. The current capability accepts
at most 10 reference images. A successful estimate does not prove that the later generation
request is valid.

Never add `--wait` or `--timeout`; estimation has no asynchronous task. Do not add `--extra`,
layer-decomposition, or sequential-image compatibility options because the CLI rejects them before
authentication or network access.

## Interpret the result

On exit `0`, require this exact data shape:

```json
{ "ok": true, "data": { "required_credits": 4 } }
```

Report `data.required_credits` as an estimate, not a balance, frozen amount, or final price. No task
ID exists. Querying the user's remaining balance is a separate APS operation.

## Handle errors

The CLI performs one request with a 30-second deadline and never retries automatically.

- Exit `6` is a temporary network, timeout, or HTTP 408/5xx failure. No task or freeze exists, so a
  manual retry is safe when useful.
- Exit `2` is an argument, model, or capability rejection. Correct the request without treating it
  as a failed generation.
- Exit `10` is a business rejection. Preserve the safe JSON code, message, and action.
- Exit `1` is an internal, unknown, or response-protocol failure. Preserve sanitized
  `details.backend_code` and `details.log_id` when present.
- `SUBMISSION_OUTCOME_UNKNOWN` must never occur for estimation. If it does, stop and report a CLI
  contract defect instead of treating a task as possibly created.

For authentication, signing, or service-availability exits not listed above, follow the root SGS
Skill's error contract and preserve the CLI's safe action.
