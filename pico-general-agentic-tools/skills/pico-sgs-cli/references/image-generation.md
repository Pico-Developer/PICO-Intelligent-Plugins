# Image generation and 3D references

Use the tool-selection rules in [SKILL.md](../SKILL.md). For image-only requests, generate the
requested image and use [execution-and-results.md](execution-and-results.md) for CLI
queries/downloads. The 3D-reference rules below apply only when an image will be used for 3D.

## Prepare a 3D reference

1. Identify the intended subject. Check completeness, main structure, background interference,
   occlusion, and strong shadows. Reuse suitable images; a complex background alone is not a
   failure.
2. If needed, edit with a reference-capable native tool or the user's chosen tool; use this service
   when native editing is unavailable. Preserve identity, shape, colors, and requested text or
   logos. Complete occluded parts instead of requesting a new photo by default. Inferred parts are
   not exact reconstruction; request more images when exact reproduction needs hidden structures.
3. Recheck the image. For independent batch assets, prepare separate, consistently styled
   references; do not feed a multi-object collage as one asset.

Default prompt:

> [Subject and user requirements], simple background, complete and clear subject, minimal
> occlusion, even lighting, no shadows needed, and a view that reveals the main structure.

Explicit text, logos, backgrounds, and composition take priority. For lettering or 3D text, specify
exact text and clear letterforms.

## Reference approval

Ask for approval in ordinary language without naming or citing the Skill. For example: "Does this
design work for you? Once confirmed, I will generate the 3D model."

| Situation                                                | Action                                                                         |
| -------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Initial 3D reference                                     | Show it and wait for explicit confirmation; silence or timeout is not approval |
| User requests revisions                                  | Revise and show again for confirmation                                         |
| Explicit waiver                                          | Skip initial confirmation within the authorized scope                          |
| Split images or faithful corrections of approved content | Apply the split-image self-check below; proceed without a second confirmation  |
| Ambiguous goal or material change                        | Clarify or obtain confirmation before proceeding                               |

Automatic cleanup does not approve new or materially changed content.

## Split-image self-check

Compare references derived from approved content with that content:

- Each subject is correct and complete; no missing parts or unrelated additions.
- No significant occlusion or obvious distortion; style and shape remain consistent.
- All required assets are represented.

Fix and recheck before generation. Passed checks allow generation without second approval; ask only
for ambiguous goals or material changes. This checks references, not the final assembled scene.

## Inputs and mode

`image_generate` always requires `--prompt`. The CLI selects the mode from reference inputs:

| Reference images                                         | Mode           |
| -------------------------------------------------------- | -------------- |
| None                                                     | Text-to-image  |
| One or more repeated `--image '<path\|url\|uri>'` values | Image-to-image |

Reference inputs may be HTTP(S) URLs, ImageX URIs, or existing regular local files. Local files are
uploaded automatically. One invocation must not mix public URLs with URI/local-file inputs. URI and
local files may be mixed, and their original order must be preserved.

When the user supplies an invalid mixture, ask them to choose one input family instead of dropping
or converting references. Do not upload files manually or call ImageX outside the CLI.

## Options and command

Use only options supplied or clearly requested by the user:

| Option                           | Accepted values and behavior                                     |
| -------------------------------- | ---------------------------------------------------------------- |
| `--model`                        | `seedream-5-pro`; this is the current default                    |
| `--size`                         | `1K`, `1.5K`, `2K`, or custom `WIDTHxHEIGHT`; omitted means `2K` |
| `--output-format`                | `png` or `jpeg`                                                  |
| `--background`                   | `opaque` or `transparent`                                        |
| `--watermark` / `--no-watermark` | Mutually exclusive explicit watermark choice                     |

The current `seedream-5-pro` model accepts at most 10 reference images. Preset sizes are `1K`,
`1.5K`, and `2K`. Custom size must contain 921600 to 4624220 total pixels with an aspect ratio from
1:16 through 16:1. After trimming surrounding whitespace, the prompt must contain 1 to 2000
characters.

Output defaults are `jpeg` and `opaque`. The watermark default is enabled. Transparent output
requires exactly one reference image and PNG; when the format is omitted, the service selects PNG.

Never pass these recognized compatibility options; the CLI rejects them before authentication or
task creation:

- `--layer-decomposition` / `--no-layer-decomposition`: layer decomposition is disabled.
- `--sequential-mode disabled|auto` / `--max-images <n>`: no sequential-image model is available.
- `--extra <json>`: the service does not consume this compatibility field.

Start with:

```bash
pico-sgs-cli-cn image_generate --prompt '<text>' --json
```

For ordered references:

```bash
pico-sgs-cli-cn image_generate --prompt '<text>' \
  --image '<first-path|url|uri>' --image '<second-path|url|uri>' --json
```

Add `--wait` only when the user asks to wait for terminal status:

```bash
pico-sgs-cli-cn image_generate --prompt '<text>' \
  --wait --timeout '<positive-duration>' --json
```

The duration requires `ms`, `s`, or `m`, defaults to `5m`, and is valid only with `--wait`.
Waiting does not download generated images.

If layer decomposition or sequential generation is the core requirement, explain its current
unavailability and do not submit a generation command.

## Interpret the result

On exit `0`, require `ok: true`, `data.task_id`, and a normalized `data.status`. Without `--wait`,
return the expected `pending` status. With `--wait`, terminal success returns `succeeded`; a wait
timeout exits `6` and preserves the task ID plus the last known status when available.

The result intentionally omits image URLs. For later status checks or download, use
[execution-and-results.md](execution-and-results.md) with `--type image`.

Never automatically retry `image_generate`. `SUBMISSION_OUTCOME_UNKNOWN` / exit `1` means the
service may already have created the task, so warn against resubmission. On other failures, report
the safe JSON error from stderr without inventing task data or rewriting server-owned validation.

When a `--wait` error contains `data.task_id`, the task was created and may still consume credits or
finish successfully. Return the task ID and last known status, do not run `image_generate` again,
and tell the user to wait before querying the same ID with `get_task --type image`.
