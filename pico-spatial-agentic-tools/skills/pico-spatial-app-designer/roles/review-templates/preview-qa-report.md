# Preview / QA Test Report · <project name>

> Role: `prototype_frontend_engineer` (generates the preview) + `prototype_qa_reviewer` (independent review) | Workflow stage(s): `preview_build` → `preview_review` | Upstream inputs: design-system facts (layout / components / interaction / motion / data), approved visual references | Downstream recipients: engineering implementation team, Design Lead, PM
>
> This document carries these two roles' **LLM reasoning information** and **direct description of outputs**. It is not bound to any JSON Schema or validator error codes; mandatory gates are expressed through this document's Coverage Manifest, item-by-item mapping tables, independent QA evidence, and the `block` status.

## 0. Reasoning Guidance (how this role reasons)

- **The preview is generated only from the design-system fact documents (`interaction-spatial-spec.md` / `visual-system-spec.md`)**: do not select a domain template, do not invent missing design facts, do not modify the design-fact documents, do not generate Android/PICO runtime, do not fabricate device evidence, and do not draw cross-platform parity conclusions.
- **The preview must cover** the declared states, components, data bindings, and visual tokens, as well as Large / Compact / Constrained and Reduce Motion, and must be labeled with the scope `web_design_validation_only`.
- **The coverage unit is the design-fact item, not the name**: verify item by item `renderSpec.elements[]`, `dataBindings[]`, variants, component-specific states, transitions, and fallbacks; a component name or state button appearing does not count as implementation fidelity.
- **The Coverage Manifest precedes preview generation**: before generating `preview.html`, first declare the design-fact denominator in this report; the Manifest is a Markdown declarative denominator, not a script, schema, or validator.
- **Declarative checks replace script checks**: preview fidelity is declared and back-checked item by item through this report's Markdown checklist; script output can only serve as auxiliary observation, and cannot replace the evidence chain of source fact → selector → trigger → result.
- **Validation boundary**: the preview only verifies Web logical relationships and declared token references; it does not do screenshot-level visual diff, and does not interpret CSS pixels as PICO physical sizes or device color differences.
- **QA review independence**: `prototype_qa_reviewer` differs from the generator, only emits findings, coverage records, and patch goals, does not modify the prototype or design-fact documents, does not do device validation, and does not substitute for human approval. **A Preview PASS must not be described as PICO runtime validation**.
- **Device-validation status is fixed as `not_performed`**: physical viewing distance, occlusion, fatigue, hit precision, runtime performance, and safety must be handed off to device validation.

## 1. Direct Description of Outputs

This role delivers: **preview coverage verification → requirements traceability → sample data → Web logic tolerance → device-validation boundary → defect list**. The sections below are the structured descriptions of these outputs.

## 2. Test Scope and Verdict

- **Object under test**: a single-file Web validation prototype driven by the design-fact documents
- **Validation scope**: `web_design_validation_only`
- **Source design-fact documents**: <list `interaction-spatial-spec.md` / `visual-system-spec.md` and their corresponding stage / commit, as prototype provenance anchors>
- **Overall verdict**: <pass / conditional pass / fail>

### 2.0 Reviewer Invocation Evidence

| Review Gate | reviewerRole | invocationId | contextPolicy | reviewed artifact revision | Independently rebuilt evidence | Verdict |
|---|---|---|---|---|---|---|
| Preview implementation | prototype_qa_reviewer | | fresh_context / isolated_subagent / unavailable | | yes / no | pass / block |

> When `invocationId` is empty, `contextPolicy=unavailable`, or "independently rebuilt evidence=no", the Preview Review can only be `block`.

### 2.1 Input Readiness Table (required before preview_build)

> If any item is not `pass`, a preview must not be generated or reused from an old one; the verdict must be `block`.

| Input Fact | Source Section / Version | Completeness Assertion | Verdict |
|---|---|---|---|
| Design-system review | design-critique-report | `design_system_review = pass` | pass / block |
| States and transitions | interaction-spatial-spec | states, exceptions, entry, exit, and return complete | pass / block |
| Core component 8-section structure | visual-system-spec | structural-completeness checklist all pass | pass / block |
| renderSpec.elements[] | visual-system-spec | each element has a stable id / label / type / bind / role | pass / block |
| dataBindings[] | visual-system-spec | each binding has target, fallback, display/semantic | pass / block |
| variants / component-specific states | visual-system-spec | trigger, visual, motion, accessibility, stacking precedence complete | pass / block |
| Responsive window tiers / Reduce Motion | both design specs | Large / Compact / Constrained map to window default / min / max or explicit size tiers, with fallback facts complete | pass / block |
| tokens / colorSemantics / materials | visual-system-spec | values complete and without mutually exclusive conflicts | pass / block |

### 2.2 Preview Coverage Manifest (declarative denominator before generation)

> This section is filled in before `preview.html` is generated. It is the sole coverage denominator for subsequent implementation mapping and QA back-checking. Do not use "all components covered" or "see preview" as a merged replacement for an item-by-item Manifest.

#### 2.2.1 State / transition denominator

| Type | ID | Source Fact Anchor | Trigger event / entry | Target / visible result | High-risk confirmation requirement | Verdict |
|---|---|---|---|---|---|---|
| state / transition | | interaction-spatial-spec § | | | yes / no / N/A | included / missing |

#### 2.2.2 `renderSpec.elements[]` denominator

| Component | element id | Source Fact Anchor | Visible label | bind | Conditional hide / show rule | Verdict |
|---|---|---|---|---|---|---|
| | | visual-system-spec § | | | | included / missing |

#### 2.2.3 `dataBindings[]` denominator

| Component | Source path | Target element / attribute | normal sample | fallback / error sample | display-only / semantic | Verdict |
|---|---|---|---|---|---|---|
| | | | | | | included / missing |

#### 2.2.4 variants / component-specific states denominator

| Component | variant / state / stacking combination | Source Fact Anchor | Trigger method | Expected observable change | Verdict |
|---|---|---|---|---|---|
| | | visual-system-spec § | | | included / missing |

#### 2.2.5 Responsive window tiers / Reduce Motion denominator

| Scenario | Source Fact Anchor | Corresponding window tier / content area | Trigger method | Expected structural change / motion fallback | Verdict |
|---|---|---|---|---|---|
| Large | | default / max / Large content area | | | included / missing |
| Compact | | min or Compact content area | | | included / missing |
| Constrained | | min lower bound or Constrained content area | | | included / missing |
| Reduce Motion | | N/A | | | included / missing |

### 2.3 Markdown Declarative Checklist (replaces scripts)

> This section is filled in after `prototype_frontend_engineer` generates, and independently re-reviewed by `prototype_qa_reviewer`. Each row must state the source fact, selector, trigger steps, expected result, actual result, and verdict; if any item is empty, preview implementation fidelity is `block`. Do not use script results, a component name appearing, or a state button existing as a replacement for this table.

| Check Item | Source Fact Denominator | Preview selector / structure | Trigger steps | Expected result | Actual result | Verdict |
|---|---|---|---|---|---|---|
| Coverage Manifest complete | all rows of §2.2 | N/A | manually compare design facts item by item | denominator has no merges, no dangling, no missing items | | pass / block |
| State machine exists | §2.2.1 | `data-state` / transition table / render function | switch each state | each state has a different primary task and visible result | | pass / block |
| Transitions can be triggered | §2.2.1 | `data-transition` / `data-action` | trigger each transition one by one | target state, action, and confirmation requirement match the design facts | | pass / block |
| renderSpec DOM back-check | §2.2.2 | `data-preview-id` / id | check the DOM item by item | each element has a stable selector and a visible/conditional-hide result | | pass / block |
| dataBindings normal/fallback/error | §2.2.3 | `data-binding` / sample data controls | switch normal/fallback/error | the corresponding bound element changes as expected | | pass / block |
| variants / component states | §2.2.4 | `data-variant` / state trigger | trigger item by item | the variant or state has an observable difference | | pass / block |
| High-risk confirmation Dialog | §2.2.1 high-risk transition | Dialog selector | trigger entry/exit/dangerous operation | the Dialog blocks, and both the confirm/cancel paths exist | | pass / block |
| Responsive window tiers / Reduce Motion | §2.2.5 | `data-responsive` / `data-reduce-motion` | switch the four scenarios | Large/Compact/Constrained correspond to window default/min/max or explicit size tiers; structural reflow / motion fallback, not overall scaling | | pass / block |

### 2.4 Preview Denominator Reconciliation (required for preview_review)

| Denominator Type | Design-fact total | Generation-side Manifest total | QA-rebuilt total | Difference | Verdict |
|---|---:|---:|---:|---:|---|
| States | | | | | pass / block |
| transition | | | | | pass / block |
| renderSpec.elements[] | | | | | pass / block |
| dataBindings[] | | | | | pass / block |
| variants / component states | | | | | pass / block |
| responsive / Reduce Motion | 4 | | | | pass / block |

### 2.5 Preview Hard Gate

> `prototype_qa_reviewer` must recount from the active design facts; do not copy the generation-side totals.
> A missing Coverage Manifest or inconsistent denominators, a design-fact total filled with 0 without basis, any Manifest
> row missing a source fact anchor, any generation-side/QA total being empty, or any difference not being 0 all make
> `previewImplementationFidelity=block` and the overall `designStatus=invalid`.

| hard gate | pass condition | Evidence | Verdict |
|---|---|---|---|
| HG-PREVIEW-INPUT | each row of §2.1 is pass and references the active revision | §2.1 | pass / block |
| HG-PREVIEW-MANIFEST | the five categories of denominators in §2.2 are listed item by item, with no merges, no empty rows, no dangling references | §2.2 | pass / block |
| HG-PREVIEW-CHECKS | each row of §2.3 has a source fact, selector, trigger, expected, actual, and verdict | §2.3 | pass / block |
| HG-PREVIEW-DENOMINATOR | design-fact total = generation-side Manifest total = QA-rebuilt total, differences all 0 | §2.4 | pass / block |
| HG-PREVIEW-MAPS | each denominator item in §3.1–§3.5 has exactly one implementation and one piece of independent validation evidence | §3.1–§3.5 | pass / block |

| Field | Value |
|---|---|
| previewImplementationFidelity | pass / block |
| minimumCompletenessGate | pass / block |
| designStatusImpact | none / invalid |

## 3. Preview Coverage

> The denominator comes from §2.2 Preview Coverage Manifest. Do not use "number of components" or "number of pages" to replace the number of elements, bindings, states, or scenarios; do not let §3 coverage be higher than the §2.3 declarative-check verdict.

| Coverage Item | Design-fact total | Verified item by item | Coverage rate | Missing / extra | Verdict |
|---|---:|---:|---:|---|---|
| Top-level states + transitions | | | | | pass / block |
| renderSpec.elements[] | | | | | pass / block |
| dataBindings[] normal value | | | | | pass / block |
| dataBindings[] fallback | | | | | pass / block |
| variants | | | | | pass / block |
| Component-specific states + stacking combinations | | | | | pass / block |
| visualTokens actually consumed | | | | | pass / block |
| colorSemantics color+shape+human-readable label | | | | | pass / block |
| Responsive + Reduce Motion | 4 | | | | pass / block |

- **Responsive modes (Large / Compact / Constrained)**: <list>
- **Reduce Motion**: <true / false>

### 3.1 State / transition → scenario implementation mapping

| Source state / transition | Source Fact Anchor | Trigger steps | Stable selector | Expected visible result | Actual result | Verdict |
|---|---|---|---|---|---|---|
| | | | `data-state` / `data-action` | | | pass / block |

### 3.2 Component / renderSpec.elements[] → DOM implementation mapping

> One row per `renderSpec.elements[]` element; do not merge by component.

| Component.element id | Source Fact Anchor | Visible label / conditional hide | DOM selector | Visual / semantic role | Actual result | Verdict |
|---|---|---|---|---|---|---|
| | | | `id` / `data-preview-id` | | | pass / block |

### 3.3 dataBindings[] → data and fallback implementation mapping

> One row per binding; the normal value and fallback must each be demonstrable.

| Source path | Target element / attribute | Display-type / semantic-type | Normal sample and trigger | fallback and trigger | DOM / JS evidence | Verdict |
|---|---|---|---|---|---|---|
| | | display-only / semantic | | | | pass / block |

### 3.4 variants / component-specific states → behavior implementation mapping

> One row per variant, component-specific state, and declared stacking combination; a top-level page state cannot replace this table.

| Component | variant / state / stacking combination | Source Fact Anchor | Trigger steps | Expected visual / behavior / accessibility result | DOM / JS evidence | Verdict |
|---|---|---|---|---|---|---|
| | | | | | | pass / block |

### 3.5 Responsive window tiers / Reduce Motion → reflow implementation mapping

| Scenario | Source Fact Anchor | Corresponding window tier / content area | Trigger method | Must preserve | Structural change / motion fallback | Actual result | Verdict |
|---|---|---|---|---|---|---|---|
| Large | | default / max / Large content area | | primary task, primary focus, hit target | | | pass / block |
| Compact | | min or Compact content area | | primary task, primary focus, hit target | | | pass / block |
| Constrained | | min lower bound or Constrained content area | | primary task, primary focus, hit target | | | pass / block |
| Reduce Motion | | N/A | | state semantics and functional feedback | | | pass / block |

## 4. Requirements Traceability Table requirementsTraceability

> Map each task item by item to state + component, ensuring full requirement coverage and traceability.

| Requirement / task | Priority | Mapped state | Mapped component | Validation method | Coverage status |
|---|---|---|---|---|---|
| | | | | validate / preview_audit | covered / gap |

- **Requirement coverage rate**: <covered / total requirements = N%>
- **Uncovered requirements (gaps)**: <list and explain reasons>

## 5. Sample Data sampleData

> Sample data must look like the display data returned by a real app backend: pure display fields are filled with human-readable copy, status/enum fields are translated via color-semantic labels, and machine enums are not echoed back.

| Source path | Normal sample | fallback / exception sample | Mapped element | Human-readable conversion |
|---|---|---|---|---|
| | | | | |

## 6. Web Logic Consistency Tolerance (not physical tolerance)

| Tolerance Item | Range / standard |
|---|---|
| Logical geometric relationship | exact_id_relationship_match |
| Visual token reference | declared_group_reference_presence |
| Exclusions | screenshot_visual_diff, css_pixel_to_pico_physical_size, device_color_delta, web_pico_parity |

## 7. Device-Validation Boundary List (must be handed off to device validation, not performed at this stage)

> Device-validation status `deviceValidation.status`: `not_performed`. The following items cannot be closed-loop by Web preview.

| Validation Item | Ownership | Status |
|---|---|---|
| Physical viewing distance and arc-resolution readability | requires device validation | not_performed |
| Occlusion and central comfort zone | requires device validation | not_performed |
| Fatigue and sustained posture | requires device validation | not_performed |
| Hand and controller hit precision | requires device validation | not_performed |
| PICO runtime performance and safety behavior | requires device validation | not_performed |
| State / component / binding / token logical coverage | Web preview closed-loop | <pass / gap> |

## 8. Defect List Bug List

| # | ID | Severity | Description | Reproduction steps | Owning stage (fallback) | Status |
|---|---|---|---|---|---|---|
| | | | | | | |

## 9. Delivery and Recipients

- **Deliverables**: preview coverage verification, requirements traceability, sample data, Web logic tolerance, device-validation boundary, defect list (this document is their human-readable source of fact)
- **Recipients**: engineering implementation team, Design Lead, PM

---

> Format convention: the input readiness table precedes generation; the five implementation-fidelity tables are filled in item by item; a name appearing does not count as coverage; a missing core element, actionable binding, fallback, or exception/safety/stable-exit state is block; the device-validation boundary is labeled not_performed; a Preview PASS must not be described as PICO runtime validation.
