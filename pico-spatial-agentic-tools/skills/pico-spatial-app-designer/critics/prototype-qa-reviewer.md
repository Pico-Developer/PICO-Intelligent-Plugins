# Prototype QA Reviewer

Independently review whether the Web validation prototype completely and accurately renders the design facts deposited in each role's documents. The reviewer must differ from the prototype generator.

Output only findings, coverage verification, patch targets, and validation boundaries, written to [`roles/review-templates/preview-qa-report.md`](../roles/review-templates/preview-qa-report.md). Check: input readiness, declared states, recovery paths, back navigation, responsive window tiers (whether Large / Compact / Constrained map to interaction §9's default / min / max and content area), visual tokens, `renderSpec.elements[]`, `dataBindings[]`, variants, component-specific states, fallback, and Reduce Motion.

## Implementation fidelity gate

The reviewer must independently establish the denominator from design facts and check the generation-side Coverage Manifest, the Markdown declarative checklist, and the five implementation mapping tables item by item:

| Check Aspect | Per-item Evidence Requirement | Block Condition |
|---|---|---|
| Input readiness | Each item has a design-document section anchor, and the design system review is pass | Generating despite missing facts, referencing an outdated section |
| Coverage Manifest | States, transitions, renderSpec, dataBindings, variants, component states, responsive denominators listed item by item | Manifest not filled, merged denominators, rows missing a source-fact anchor |
| Markdown declarative check | Each item declares source fact, selector, trigger, expected result, actual result, verdict | Writing only "covered / see preview," or missing any evidence |
| States / transitions | Each state and transition has a trigger, stable selector, visible result | Names only appearing in a menu, no back/exception path |
| renderSpec | Each element has a stable DOM selector, a visible label / conditional-hide rule | Merged counting by component name, missing elements |
| dataBindings | Each binding has a normal sample, target attribute, fallback demonstration, display/semantic conversion | Writing only hardcoded copy, fallback not triggerable |
| variants / specific states | Each variant, state, and declared stacking precedence has a trigger and an observable result | Implementing only top-level page states, using static screenshots in place of behavior |
| Responsive window tiers / Reduce Motion | Large / Compact / Constrained each have a default / min / max or an explicit sizing-tier mapping, content-area changes, and structure assertions; Reduce Motion has a trigger and structure assertion | Overall scaling only, only hiding content with no spec basis |
| tokens / semantics | Tokens have an actual consumption point; semantic values present color, shape, and a human-readable label simultaneously | Only declaring a CSS variable, relying only on color |

**Per-item evidence rules:**

- Every row must record: source-fact anchor, preview selector, trigger step, expected result, actual result, verdict.
- "Component name appears," "state button exists," "CSS variable declared," and "sample copy visible" do none of them constitute implementation evidence.
- The coverage denominator is taken respectively as the total counts of states/transitions, renderSpec elements, dataBindings, variants/specific states, and responsive/motion scenarios in the design facts; the top-level component count must not be used as a substitute.
- If any core element, actionable binding, fallback, exception state, stable exit, or safety state is missing, the review recommendation must be `block`; it cannot be offset by other coverage rates, visual scores, or the device-validation boundary.
- The generation-side tables cannot directly serve as pass evidence; the reviewer must actually read `preview.html` and independently re-review selectors and behavior.
- If the Coverage Manifest is missing or the denominators are inconsistent, a denominator is filled with 0 without basis, the generation-side total differs from the QA
  independently-rebuilt total, or any difference is non-0, you must return `block` and mark the overall
  `designStatus` impact as `invalid`; do not relax it via percentage rounding or "the core path is covered."
- This Skill neither requires nor allows handing Preview fidelity to a script / schema / validator for judgment; the check must be written into the Markdown declarations and per-item evidence tables of `preview-qa-report.md`. Script output can only serve as auxiliary observation; it cannot replace the checklist verdict, nor relax any missing item.

Do not modify the prototype or design facts. The review record must note that the review target is the current prototype version and the source design-fact version, and mark `deviceValidation.status` as `not_performed`. Preview passing is not equivalent to PICO on-device, device, comfort, performance, or cross-platform consistency validation.

## HTML independent reverse-lookup steps

1. The reviewer must re-read the current `preview.html`; it is not enough to read only the generation-side mapping tables.
2. For each `renderSpec` id, find a unique stable selector.
3. For each `dataBinding`, trigger normal and fallback/error separately.
4. For each transition, perform the trigger and observe the target state; "the state selector can be switched directly" cannot substitute for a transition.
5. For each high-risk action, verify the Dialog's blocking, confirmation, and cancellation.
6. Trigger Large, Compact, Constrained, and Reduce Motion separately.
7. If any row lacks a selector, trigger, actual result, or verdict, `block`.
