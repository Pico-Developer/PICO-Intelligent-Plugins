# Design Coherence Reviewer

Review the approved visual references, experience and container architecture, state graph, layout synthesis, and design system facts (carried in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) and [`roles/review-templates/visual-system-spec.md`](../roles/review-templates/visual-system-spec.md)) as a single integrated system. The reviewer must differ from the generator.

Output only impactful findings, evidence, and patch targets, written to [`roles/review-templates/design-critique-report.md`](../roles/review-templates/design-critique-report.md). Check visual drift, material and system glass usage (whether `treatment=glass` selects a `glassStyle` from the four system tiers `Thin/Regular/Thick/Thickest`, whether glass is used only inside a WindowContainer, whether tiers map to depth layers, whether component-level backgrounds obey "custom color and glass are mutually exclusive, not stacked" (corresponding to PICO-MATERIAL-004), whether panels carrying key states/body text/forms provide a contrast ruling under passthrough/MR, whether single-color legibility on passthrough/complex backgrounds uses Vibrant Style and is not misapplied to images/gradients, whether the Web preview is mistaken for device materials — corresponding to PICO-MATERIAL-001~003 and PICO-VIBRANT-001), the legality of space-state and container combinations (whether Shared/Full Space is declared, whether a Stage is wrongly placed inside Shared Space, whether choosing Stage declares the Full Space switch cost and stable exit, whether Planar depth is misconfigured, whether 1280×720 is treated as the final fixed size for all Planar projects without scene / field-of-view / content calibration — corresponding to PICO-SPACESTATE-001/002 and PICO-CONTAINER-002 / PICO-WINDOW-SIZING-003), the completeness of window structure and component metrics (whether every major window provides a window shell and an in-window layout structure diagram, whether default / min / max and the content area reference interaction §9, whether the semantics of solid/dashed boxes are correct, whether the region→component mapping has no orphan regions/unplaced components, whether every core component provides icon size/font size and family/corner radius/padding/element spacing/stroke/hit target and references a unified metric scale rather than prose or magic numbers, and whether component sizing/metrics fall within the content area of the owning window's default / min / max — corresponding to PICO-VISUAL-LAYOUT-001 and PICO-VISUAL-METRICS-001, and cross-check that it does not contradict interaction §14 spatial geometry), container / state / layout / component consistency, accessibility, error recovery, data trust, and traceability. Do not rewrite design facts, do not choose a different visual direction, and do not substitute for human approval.

## Component structure fidelity gate (before semantic coverage)

The reviewer must enumerate the core components one by one and check them against the fixed structure in [`engines/08-component-engine.md`](../engines/08-component-engine.md); do not merely check whether information "has appeared":

| Check Item | Pass Condition | Block Condition |
|---|---|---|
| Base fields | The six fields are on separate lines; task / data references are locatable | Merged fields, dangling references |
| anatomy.layout | Standalone title + ASCII diagram + Grid; Stage components have world anchor / coordinates / metric range | Single-line `Grid`, prose only |
| sizing | Standalone tier table, Regular / Compact / Constrained or a not-applicable rationale; each tier references the owning window's default / min / max and falls within the content area | Sizes stuffed into base fields, detached from window sizing tiers |
| metrics | Each metric on a separate line and referencing the scale | Semicolon-strung into one line |
| renderSpec | Each visible element on its own line, with stable id / label / type / bind / role complete | Untitled element enumeration |
| dataBindings | Each source path on its own line, with target / fallback / type complete | Path string, missing fallback |
| variants | Differences explicitly listed, or `none + rationale` | Omitted |
| states | Component-specific state table + stacking precedence | One-line enumeration, referencing only the shared state table |

**Ruling rules:**

- If any core component is missing any part of the fixed structure, the review recommendation must be `block`; it cannot be offset by the total score, coverage reconciliation, or the shared spec.
- The component structure completeness checklist must be all `pass` before the semantic coverage of tables A/B/C can be re-reviewed.
- "Limited length," "the component is simple," "the information is elsewhere," and "the shared states are the same" are none of them compression reasons.
- The review report must list per-component structure verification results and section evidence; it cannot merely write "components complete."

## Ruling order (do not skip steps)

1. Re-enumerate the core component list from the visual spec.
2. Locate the 8-part evidence anchors item by item for each component.
3. If any evidence anchor is empty, merged, unlocatable, or writes only the component name, immediately `block`.
4. Only after the structure is all `pass` can you check coverage tables A/B/C.
5. Only after coverage is all `pass` can you proceed to quality scoring.

`pass with assumptions` and `pass with implementation risk` cannot substitute for a blocking verdict. When a blocking item exists, the only legal recommendation is `block`.
