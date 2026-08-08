# Web Prototype Engine

## Responsibilities

Role: `prototype_frontend_engineer`. Reasoning and verification conclusions are recorded in [`roles/review-templates/preview-qa-report.md`](../roles/review-templates/preview-qa-report.md).

Generate a single-file static Web validation prototype `preview.html` based only on the design-system facts (states, structured component anatomy, data bindings, visual tokens, interactions, and motion) captured in the upstream role documents. The prototype must expose every declared state, component-specific state, responsive window tier (Large / Compact / Constrained, corresponding to the default / min / max of interaction §9 or an explicit mapping), and Reduce Motion. Visible labels, components, bindings, layout semantics, and visual tokens must be traceable to the design facts in the corresponding role documents.

**The prototype is not a schematic where "the component name appeared".** `renderSpec.elements[]`, `dataBindings[]`, `variants`, component-specific `states`, transitions, and fallbacks are all implementation inputs that must be consumed item by item; the number of lines of code, visual complexity, or domain differences cannot lower the coverage standard.

## Inputs

- Design-system facts (visual system spec, interaction / spatial spec)
- PICO methodology window sizing (default / min / max, content area, reflow)
- Approved visual references
- Reasoning conclusions from upstream stages

### Input Readiness Gate (mandatory before generation)

`prototype_frontend_engineer` first fills in the table below in `preview-qa-report.md`. If any row is not `pass`, `preview_build` must `block`, and you must not guess, fill in, or substitute generic UI for missing facts.

| Input Fact | Pass Condition | Evidence |
|---|---|---|
| Design-system review | `design_system_review = pass` | `design-critique-report.md` gate record |
| States and transitions | every state contains entry, exit, return, exception, and trigger action | `interaction-spatial-spec.md` state graph / transition table |
| Core components | each component's 8-section structure and integrity checklist are all pass | `visual-system-spec.md` component blocks / checklist |
| Elements and bindings | each `renderSpec.elements[]` has a stable id; each `dataBindings[]` has a target, fallback, display/semantic | component blocks |
| Variants and component-specific states | each variant and state has trigger, visual, motion, accessibility, and stacking precedence | component blocks |
| Responsive window tiers and motion | Large / Compact / Constrained are each mapped to the window default / min / max or an explicit size tier, and Reduce Motion has explicit design facts | the two design specs |
| Visual grammar | typography, tokens, colorSemantics, materials are implementable and conflict-free | `visual-system-spec.md` |

Input readiness may only be judged on the basis of explicit section evidence; passing reasons such as "the semantics roughly exist", "the component is simple", or "the prototype is only for validation" are prohibited.

The generation side must not fill in its own "actual result" and "verdict" columns for the independent QA; the generation side only fills in the Manifest and the generation mapping. `prototype_qa_reviewer` must fill in the QA rebuild denominator and actual results in an independent invocation. A component name appearing, a CSS class existing, or a state dropdown existing cannot substitute for item-by-item implementation.

The top of the generated `preview.html` must contain a version-source comment:

```html
<!--
scope: web_design_validation_only
source-interaction-revision: <integer>
source-visual-revision: <integer>
source-design-system-review-revision: <integer>
preview-revision: <integer>
-->
```

### Preview Coverage Manifest (declarative denominator before generation)

After input readiness passes and before writing `preview.html`, you must first fill in the **Preview Coverage Manifest** in `preview-qa-report.md`. This is a Markdown declaration, not a script, schema, or validator; but it is the sole coverage denominator for subsequent implementation and QA. The Manifest at minimum lists item by item:

- **states / transitions**: one line per state and transition, including the source-fact anchor, trigger event, target state, and high-risk confirmation requirement.
- **`renderSpec.elements[]`**: one line per component element, including the component name, element id, visible label, binding, and conditional-hide rule.
- **`dataBindings[]`**: one line per binding, including the source path, target property, normal sample, fallback / error sample, display-only / semantic.
- **variants / component-specific states**: one line per variant, component state, and stacking combination, including the trigger method and the expected observable change.
- **responsive window tiers / Reduce Motion**: one line each for Large / Compact / Constrained / Reduce Motion; the responsive rows must state the corresponding window default / min / max, content-area change, and structural change, and must not write only whole-scene scaling.

It is prohibited to substitute merged declarations like "8 components are covered", "the state buttons are covered", or "all fallbacks are covered" for the Manifest. If any Manifest row lacks a source-fact anchor or an expected observable result, `preview_build` must `block`.

## Output (direct description, no longer bound to a Schema)

A single self-contained `preview.html`, annotated with the output scope `web_design_validation_only`, covering:

- the visible presentation of all declared states and transitions;
- the visible elements of each core component's `renderSpec.elements[]`, or explicit conditional-hide behavior;
- the normal sample, fallback, and display-only / semantic conversion of each `dataBindings[]`;
- the triggerable demonstration of each `variants` and component-specific `states`, plus stacking precedence;
- the three-tier responsive window reflow of Large / Compact / Constrained (mapped to default / min / max or an explicit size tier);
- Reduce Motion fallback;
- the components' visible labels, data-binding fallbacks, and dual-channel coloring of semantic color + shape;
- the font hierarchy, materials, and depth semantics consistent with the role documents.

The implementation structure must be able to prove the state graph is runnable, rather than only showing a static page. Minimum requirements:

- an explicit state table and transition table;
- a triggerable `renderScene(state)` or equivalent state-rendering mechanism;
- `normal / fallback / error` sample data switching that affects the corresponding bound elements;
- high-risk transitions (Stage entry / exit, dangerous operations) blocked by a confirmation Dialog;
- each core `renderSpec.elements[]` exposed via a stable selector (such as `data-preview-id`);
- variants and component-specific states have a triggerable entry point or explicit conditional-hide evidence;
- the responsive modes and Reduce Motion are presented through structural changes / motion fallback.

### Implementation Mapping (mandatory handoff on the generation side)

After generating the prototype, you must fill in the following five implementation-mapping tables in `preview-qa-report.md`; each row references a stable DOM selector, the demonstration trigger method, and the source-fact anchor. You must not compress multiple elements, bindings, or states into a single "covered" line.

1. **states / transitions → scene mapping**: one line per top-level state, exception state, and entry/exit/return transition.
2. **components / renderSpec.elements[] → DOM mapping**: one line per visible element; conditional hides must write the trigger condition.
3. **dataBindings[] → data / fallback mapping**: one line per binding, giving the normal sample and the fallback demonstration entry point separately.
4. **variants / component-specific states → triggerable behavior mapping**: one line per variant, state, and real stacking combination.
5. **responsive window tiers / Reduce Motion → reflow mapping**: one line each for the three responsive tiers and Reduce Motion, explaining the corresponding default / min / max, content-area change, and structural change, rather than whole-scene scaling.

Implementation selectors use a stable `id` or `data-preview-id` / `data-state` / `data-variant` / `data-binding`; they cannot reference only an easily-drifting CSS hierarchy. The coverage denominator must come from the item-by-item count of design facts, and cannot substitute "number of components" or "number of pages" for the number of elements, bindings, and states.

### Markdown Declarative Checks (in place of scripts)

The generation side must fill in a "declarative check checklist" in `preview-qa-report.md`, self-proving item by item:

| Check Item | Evidence That Must Be Declared |
|---|---|
| Coverage Manifest complete | the Manifest row count is consistent with the design-fact denominator, with 0 gaps or an explicit block |
| State machine exists | state table, transition table, render function / mechanism, current-state selector |
| DOM lookup entry | a stable selector for each `renderSpec.elements[]` |
| Data modes | normal / fallback / error sample data and trigger entry points |
| High-risk confirmation | Dialog selector, triggering transition, confirm / cancel paths |
| Responsive window tiers / Reduce Motion | the mapping of the three responsive tiers to the window default / min / max, content-area changes, and the trigger and structural assertion of Reduce Motion |

This table is still a Markdown document, not a deterministic validator; but when any row is blank, the generator must not mark the preview as complete.

## Prohibitions

- choosing a domain template or fabricating missing design facts;
- modifying upstream design facts;
- substituting a static screenshot, a hardcoded single sample, or the appearance of a top-level state name for triggerable component-specific states and fallbacks;
- merging multiple `renderSpec.elements[]`, `dataBindings[]`, or component-specific states into a single coverage record;
- continuing to generate when the input readiness gate has not passed, or skipping implementation-fact updates on the grounds that "the product semantics have not changed";
- generating Android / PICO runtime code, manufacturing device evidence, or claiming Web / PICO consistency;
- describing project-level derivations as PICO official hard rules.
