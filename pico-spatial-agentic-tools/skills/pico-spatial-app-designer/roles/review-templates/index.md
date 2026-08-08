# Human Review Package · <project name>

> Target platform: PICO spatial | Generated at: <YYYY-MM-DD>

This directory is the **role-based reasoning layer** for human collaboration. Each document corresponds to a real professional role in the design pipeline,
carrying that role's **LLM reasoning information** in the corresponding workflow stage, and **directly describing** the "outputs" declared by each engine of that stage.

After the refactor, JSON Schema is no longer used as the in-flow parameter-passing and constraint layer: reasoning information is passed only in the role
Markdown corresponding to the flow; each engine's output is described directly in structured Markdown, no longer bound to the Schema format,
and no longer declares validator error codes. Mandatory gates are expressed through the minimum-completeness table inside each role document, per-item evidence anchors, independent review
records, and the `block / invalid` status.

## Role documents

| Document | Role | Carried workflow stage and reasoning |
|---|---|---|
| [PM Requirement Spec](pm-requirement-spec.md) | `product_strategist` | Intent extraction, assumptions list, quality contract |
| [UXR Research Report](uxr-research-report.md) | `research_analyst` | Five categories of research evidence, domain model, Persona, duration baseline, comfort boundaries |
| [Interaction / Spatial Design Spec](interaction-spatial-spec.md) | `interaction_xr_designer` | Task/decision model, spatial value, design hypotheses, selection, container architecture, window attachment, window sizing, state graph, motion, layout |
| [Visual System Spec](visual-system-spec.md) | `visual_designer` (including component synthesis and data trust) | Visual direction, Design Tokens, structured component anatomy, data-display semantic contract, materials and PICO numbers |
| [Design Critique Report](design-critique-report.md) | independent reviewers | Per-gate reviews, "good UI" scoring, originality and process audit, pass verdict and patch list |
| [Preview / QA Test Report](preview-qa-report.md) | `prototype_frontend_engineer` / `prototype_qa_reviewer` | Preview coverage, requirements traceability, Web logic tolerance, device validation boundary |
| [Execution Trace](execution-trace.md) | host orchestrator | Stage receipt, review invocation, artifact revision and invalidation rerun; does not carry design facts |

## Boundary conventions

- The design package's allowed output structure is fixed as:

  ```text
  review/
    index.md
    execution-trace.md
    pm-requirement-spec.md
    uxr-research-report.md
    interaction-spatial-spec.md
    visual-system-spec.md
    design-critique-report.md
    preview-qa-report.md
  preview.html
  ```

- This Skill only does PICO spatial design and Web prototype validation, and **does not generate** a runnable application project,
  device evidence, dual-end parity conclusions, `design-spec.json`, `design-graph.json`,
  or a downstream app-generation handoff.
- The preview validation scope is fixed as `web_design_validation_only`; subjective and physical bodily aspects such as comfort / occlusion / fatigue / input hit /
  physical size / performance must be delegated to device validation, and this design stage annotates them `not_performed`.
- Professional roles are responsible for generation, independent roles are responsible for review, and the delivery status is derived by the review gate; reviewers only produce
  findings and patch goals, do not rewrite the reviewed content, and do not overstep to declare downstream implementation or device validation status.
