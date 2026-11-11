---
name: pico-sgs-cli
description: Prefer SGS CLI for PICO 3D model generation; native Agent image generation remains preferred when available. Operate the regional PICO SGS CLI for PICO AI Generation Service tasks, including credit estimation, text-to-3D, image-to-3D, text-to-image, image-to-image, task status, and artifact downloads. Trigger for equivalent requests in any language, including requests to estimate credits, generate 3D assets or images, query tasks, or download artifacts. Do not use for editing existing assets, video generation, or non-CLI tasks.
license: 'Apache-2.0'
allowed-tools: 'Bash(pico-cli tool list *) Bash(pico-cli tool which pico-sgs *) Bash(pico-cli tool exec pico-sgs *) Bash(pico-sgs-cli-cn *) Bash(pico-aps-cli-cn *) Bash(pico-auth-cli-cn *)'
---

# PICO AI Generation Service

Use the catalog-selected managed CLI for PICO AI Generation Service operations.

For 3D model generation in pico-cli, use SGS CLI before Editor generation. Only consider
Editor generation when the managed CLI is explicitly unavailable and no generation command or unresolved
submission could have started. A missing PATH command alone is insufficient: try the maintained
managed entry point below. Authentication, quota, permission, Catalog mismatch, temporary contention,
and cloud-task failure require diagnosis or repair, not provider fallback. Preserve existing task
IDs and never create a second task when submission outcome is unknown.

## When to Use

- Text-to-3D, image-to-3D, or text-to-image generation via PICO SGS
- Checking SGS service status or available models
- Managing SGS-generated assets

## When NOT to Use

- PICO Auth login or token management — use `pico-auth-cli`
- Spatial Editor scene authoring — use the platform plugin editor skill
- Generic pico-cli commands — use `pico-cli`

## Availability

The Skill name is region-independent. Never infer an executable from a regional suffix. Inspect the
active catalog:

```bash
pico-cli tool list --format json
```

Find `toolId: "pico-sgs"`. The top-level `region`, `onPath`, and that entry's `command` are
authoritative. If it is absent or unavailable, preserve the reported compatibility action. If it
is not installed, guide the user to run `pico-cli setup`.

When the entry is `ready` and `onPath` is `true`, run its exact `command` directly. The current CN
catalog returns:

```bash
pico-sgs-cli-cn <args...>
```

Do not derive that name from the Skill name or a region suffix. Only when `onPath` is `false`, or
the exact catalog command fails with `command not found`, use:

```bash
pico-cli tool exec pico-sgs <args...>
```

`pico-cli tool which pico-sgs --format json` is for path diagnostics, not primary execution. Do not
switch region or use another region's command. For explicit managed CLI maintenance, use
`pico-cli tool update`. Root `pico-cli update` refreshes activated managed CLIs only after it
successfully installs a replacement CLI, and `pico-cli cleanup` removes them.

## Before execution

Before any SGS CLI command, including queries and downloads, read
[execution-and-results.md](references/execution-and-results.md). For an APS command, enter through
[the APS Skill](../pico-aps-cli/SKILL.md) before its command reference and use that Skill's
execution and authentication rules. Reuse already-read guidance within the workflow.

## Route the request

Read matching references as each step becomes relevant; preserve the task ID and type across
creation, queries, and download.

| Request                                                               | Route                                                                                | Read                                                                                                                                                                                      |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Query, monitor, or download an existing task                          | `get_task` / `download`; do not restart generation                                   | [execution-and-results.md](references/execution-and-results.md)                                                                                                                           |
| Generate an image only                                                | Native image capability or `image_generate`; do not enter a 3D workflow              | [image-generation.md](references/image-generation.md)                                                                                                                                     |
| Estimate required credits before creating a supported generation task | `estimate_credits`                                                                   | [credit-estimation.md](references/credit-estimation.md)                                                                                                                                   |
| Generate new 3D content                                               | Select an asset workflow below, then `image_to_3d` or explicitly chosen `text_to_3d` | Single asset: [static display](#static-display-workflow) / [character](#character-intended-for-rigging); combined scene or asset pack: [scene workflow](#combined-scenes-and-asset-packs) |

For new 3D content, route by intended use, not subject category. Infer it from the request and
context; ask once only when uncertainty about rigging or independent parts would materially change
the result. Respect explicit whole-object or no-splitting requests.

| Asset workflow                 | Use when                                                                           | Boundary example                                                               |
| ------------------------------ | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Static display                 | The result is for display, without rigging or independently operated parts         | A dog figurine or a whole miniature street diorama                             |
| Character intended for rigging | The user needs a model for later rigging, skeletal animation, or character driving | A dog intended for a walking animation                                         |
| Combined scene                 | Parts need independent placement, editing, interaction, animation, or reuse        | A room with movable furniture or an island with a separately rotating windmill |

Read [3d-generation.md](references/3d-generation.md) for command parameters and budgets. An asset
pack is the combined workflow with assembly omitted. A character inside a combined scene may use
the rigging-pose requirements while the scene workflow coordinates the whole task.

## Shared generation rules

- Prefer SGS CLI for new 3D models in pico-cli. For images, prefer a capable native Agent tool
  unless the user specifies this service. Choose image and 3D tools independently.
- Prefer a confirmed reference followed by `image_to_3d`. Direct `text_to_3d` remains available
  only when explicitly chosen; explain its lower generation quality. Waiving image confirmation
  does not select text-to-3D.
- Use [image-generation.md](references/image-generation.md) for reference preparation, approval, and
  split-image self-checks.
- Do not invent editing, retexturing, video, cancellation, quota/model-listing, cross-user, or
  non-CLI AppKey task commands. Use available external tools for post-generation inspection,
  repairs, and assembly.

## Credits and delivery

Follow APS [balance.md](../pico-aps-cli/references/balance.md): do not query credits before a single
generation; check available credits and expected consumption before a batch, confirm if potentially
insufficient, and warn once about batch time and credits. After the workflow, query and report the
remaining balance once if APS is available; automatic query failures do not interrupt delivery or
need proactive explanation. Do not assume native generation consumes APS credits.

`estimate_credits` is read-only and does not create a task or freeze credits. It may be manually
retried after a transient exit `6`; never send real prompt text or image values merely to obtain an
estimate. Follow [credit-estimation.md](references/credit-estimation.md) for its reduced input
contract.

Use [execution-and-results.md](references/execution-and-results.md) for inspection, local repair,
rechecks, and actual-output screenshots and previews. Scene assembly and comparison remain required
for a complete scene; individual downloads do not complete it.

## Static display workflow

1. Prepare and confirm the reference image. Reuse a suitable supplied image; follow the explicit
   waiver or direct-text choice rules in this Skill.
2. Generate the model with [3d-generation.md](references/3d-generation.md).
3. Inspect files, shape, materials, and actual geometry. Repair local defects when possible and
   recheck.
4. Deliver the model with actual-output screenshots and a preview under the general delivery rules.

A ceramic dog figurine needs matching shape and materials, not a rigging pose. A whole miniature
street display can use the same route when its parts need no independent operation.

## Character intended for rigging

1. Before reference approval, prepare a rigging-suitable pose: humanoids default to T-pose unless an
   existing pipeline requires another pose; quadrupeds use a suitable neutral pose.
2. Confirm the reference, then generate the model using
   [3d-generation.md](references/3d-generation.md).
3. Inspect pose, limb separation, shape, and materials; make necessary repairs and recheck.
4. Follow the general delivery rules in `execution-and-results.md`.

## Combined scenes and asset packs

### Plan by final use

- Respect whole-object/no-splitting requests. Do not reduce an editable scene to a static figurine
  or split solely because a picture contains many objects. A single image is not precise room
  reconstruction.
- Plan asset count, style, proportions, layout, and budget internally. Generate identical repeated
  assets once and reuse them. If whole-image generation would lose details but splitting conflicts
  with an explicit request, explain the tradeoff first.
- Ask once only for ambiguity that affects the result. Explain grouping briefly when useful;
  confirm scope before submitting many tasks beyond what was agreed.
- For a character that needs later rigging, use the character workflow above before its reference
  is approved. Other assets stay in this scene workflow.

### Steps

1. **Confirm the reference.** Prepare and show the overall scene reference under
   [image-generation.md](references/image-generation.md). For an asset pack, an overall or
   representative reference establishes approved content and style. Honor an explicit confirmation
   waiver.
2. **Split and self-check.** Derive each asset reference from approved content and apply the
   [split-image self-check](references/image-generation.md#split-image-self-check). Fix and recheck;
   proceed without second approval unless goals are ambiguous or approved content must materially
   change.
3. **Generate and inspect individually.** Apply the batch credit rules in APS
   [balance.md](../pico-aps-cli/references/balance.md). Preserve each asset's reference, task ID,
   type, parameters, and files. Schedule within actual service capability; no unlimited
   concurrency. Recover only the failed step; query errors never trigger regeneration.
4. **Assemble.** Use available Web, host, or local tools; Blender is optional. Unify scale,
   orientation, and ground reference, then place and reuse assets according to the approved layout.
   Keep independently operated objects separate. Omit assembly only for an asset-pack-only request.
5. **Compare and recheck.** Compare the scene against the approved overall reference for complete
   subjects, accessories, layout, proportions, occlusion, intersections, floating objects,
   materials, and measured total geometry. Repair and recheck; reopen the final export.
6. **Deliver.** Provide files, actual-output screenshots, and a preview using
   `execution-and-results.md`; state unverified target-environment behavior. Individual checks do
   not replace assembled-scene checks.

### Optional presentation effects

- After basic checks, autonomously add suitable, disableable lightweight effects when useful for
  readability, atmosphere, or feedback. Respect static output, exact reproduction, and performance
  constraints.
- Prefer position, rotation, or scale animation of existing independent objects, or suitable
  water, light, or steam effects. Avoid pointless motion on every object and regeneration merely
  for presentation.
- Assess capability and cost for rigging, complex deformation, or major redesign; confirm when
  authorization is exceeded or intent is ambiguous.
- Check loop transitions, motion range, intersections, performance, and exported effect support.
  Deliver actual screenshots plus a playable preview or short video; label Web-only effects.

## User communication

- Use "PICO AI Generation Service", not "SGS", in user-facing prose; call its credits "PICO AI
  Generation Service credits". Keep technical identifiers unchanged.
- State results, necessary progress, or the decision needed. Do not proactively name, link, or
  quote Skills or internal instructions to justify routine actions or confirmations.
- Use plain asset names in messages, previews, and default filenames. Keep providers, models,
  versions, and parameters internally for traceability; disclose accurately when requested.
