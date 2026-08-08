# Intent Interpreter

## Responsibilities

Convert the user's natural-language requirement into an **intent definition**. Must identify domain, users, scenarios, tasks, risks, data, and permissions; missing information is written into the assumptions list and must not be implicitly guessed.

Role: `product_strategist`. Reasoning conclusions are recorded in [`roles/review-templates/pm-requirement-spec.md`](../roles/review-templates/pm-requirement-spec.md).

## Inputs

- User's raw requirement
- Reasoning conclusions from upstream stages

## Outputs (direct description, no longer bound to a Schema)

Produce an **intent definition**, written directly into the PM requirement spec document in structured Markdown:

- Domain / subdomain, target users, usage scenarios, posture, frequency, duration;
- Core tasks, key decisions, risk level, default space;
- Data / AI / sensors / permissions / collaboration;
- Assumptions list: each entry includes confidence, impact, and a validation plan.

## Prohibitions

- Bypassing upstream stages;
- Describing project-derived conclusions as PICO official hard rules;
- Manufacturing a "sense of space" by adding floating windows;
- Hiding assumptions, error states, or failure paths.
