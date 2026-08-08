---
adapter: prd-adapter
input_mode: product_doc
status: active
owner: spatial-design-to-app
---

# PRD Adapter

Use this adapter when `Input Envelope.input_mode == "product_doc"` and the
strongest source is a PRD, feature spec, interaction document, or long-form app
description.

## 1. trigger

Match only when:

- `input_mode == "product_doc"`
- `input_sources[]` contains long-form text, markdown, doc content, or a PRD file
- no higher-trust Figma / screenshot source is the primary source

If the PRD is only supplemental to a Figma URL or screenshot, route through
`hybrid-adapter` so source priority and conflicts are explicit.

## 2. inputs

Read from `input_envelope.json`:

- `generation_mode`
- `target_module` / `output_dir`
- `input_sources[]` containing PRD text or file path
- explicit non-goals, platform constraints, and existing module facts from Phase 2
- `.scratch/design_escalation_receipt.json` for no-visual inputs
- if the receipt has `status=designer_passed`, the `pico-spatial-app-designer`
  `review/*.md` role docs plus `preview.html`; consume them only after the
  receipt records the three delivery gates (`designStatus = ready_for_design_delivery`,
  `downstreamAppGenerationAllowed = yes`, and a recorded main-thread
  acceptance) as defined in `../references/design-package-bridge.md`

## 3. produces

This adapter writes only existing workflow fields:

- `evidence_packet.json`
  - `facts.app_type_candidates`
  - `facts.user_tasks`
  - `facts.regions`
  - `facts.repeated_structures`
  - `facts.visible_states`
  - `facts.spatial_cues`
  - `facts.interaction_cues`
  - `facts.data_requirements`
  - `unknowns[]`
  - `conflicts[]`
  - `confidence.{layout,interaction,spatial_mode}`
- `normalized_spatial_spec.json`
  - `request_context`
  - `product_intent`
  - `spatial_intent`
  - `window_intent`
  - `layout_intent`
  - `ambiguities[]`
  - `evidence_trace[]`
- `assumption_ledger.json` when layout / visuals / spatial behavior are inferred

Do not add new top-level schema fields.

For no-visual app generation, the design escalation receipt selects a single
valid path:

- `status=designer_passed`: fill the artifacts by high-confidence extraction
  per `../references/design-package-bridge.md`, so `confidence` is materially
  higher than shallow extraction (for example `confidence.layout >= 0.8`).
- any missing receipt, `status=fallback_accepted`, or
  `adapter_extraction=shallow_text_extraction`: return `BLOCKED` to Phase 1.5a
  and run `pico-spatial-app-designer`; do not generate an app from shallow PRD
  text.

## 4. required_tools

None beyond local file reading and LLM extraction.

## 5. required_references

- `../references/evidence-extraction.md`
- `../references/input-normalization.md`
- `../references/architecture-conventions.md`
- `../references/design-package-bridge.md`

## 6. side_effects

- Writes `.scratch/evidence_packet.json`
- Writes `.scratch/normalized_spatial_spec.json`
- Writes `.scratch/assumption_ledger.json` when ambiguity exists

No external network calls or temp files are required.

## 7. failure_mode

- If the PRD file cannot be read, return `BLOCKED` to Phase 1 with the missing
  path or unreadable source.
- If the PRD lacks visual structure, keep visual details in `unknowns[]`, use the
  conservative evidence policy, and record layout assumptions.
- If the PRD requests Stage-only capabilities but the target module is windowed,
  record the conflicting evidence for Phase 4 legality resolution rather than
  silently switching root architecture.
- If the `pico-spatial-app-designer` design package is unavailable or any of the
  three delivery gates has not passed, return `BLOCKED` to Phase 1.5a with the
  missing designer deliverables/gates. A missing design package blocks
  no-visual app generation.

## Procedure

0. Read `.scratch/design_escalation_receipt.json`. If `status=designer_passed`,
   `bridge_allowed=true`, and `adapter_extraction=design_package_bridge`,
   extract by the field-level fill rules in
   `../references/design-package-bridge.md` instead of shallow PRD text. Record
   the container leaning and window leaning as narrative evidence for Phase 4 to
   decide, never as an adapter-level choice, and add one traceable
   `evidence_trace[]` entry per consumed `review/*.md` source. If the receipt is
   missing, `status=fallback_accepted`, or `adapter_extraction` is not
   `design_package_bridge`, return `BLOCKED` to Phase 1.5a.
1. Extract facts only: app goal, primary user tasks, data objects, navigation
   model, required states, explicit spatial words, and non-goals.
2. Treat descriptive UI language as weaker evidence than explicit architecture
   constraints. A phrase like "floating" may mean visual overlay, not a spatial
   window.
3. Normalize into one coherent app intent and evidence-backed layout / task
   structure. Do not choose the root container or window model in the adapter.
4. When visual evidence is absent, record the task-preserving structure that is
   known and leave root architecture selection to Phase 4.
5. Put every invented visual/layout choice in `assumption_ledger.json`.
