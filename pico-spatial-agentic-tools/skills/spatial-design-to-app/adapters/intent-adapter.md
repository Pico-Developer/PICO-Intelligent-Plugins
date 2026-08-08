---
adapter: intent-adapter
input_mode: intent_only
status: active
owner: spatial-design-to-app
---

# Intent Adapter

Use this adapter when `Input Envelope.input_mode == "intent_only"`.

## 1. trigger

Match only when the strongest source is a short natural-language app intent and
there is no Figma URL, screenshot, PRD, or bounded patch target.

Examples:

- "做一个资讯类空间应用"
- "实现一个杨氏双缝干涉实验空间应用"
- "做一个文件管理器面板"

## 2. inputs

Read from `input_envelope.json`:

- `generation_mode`
- `target_module` / `output_dir`
- `input_sources[]` where `type == "text_prompt"`
- any explicit user constraints captured during Phase 1
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
  - `facts.regions`
  - `facts.repeated_structures`
  - `facts.visible_states`
  - `facts.spatial_cues`
  - `facts.interaction_cues`
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
- `assumption_ledger.json` when ambiguity exists

Do not add new top-level schema fields.

For no-visual app generation, the design escalation receipt selects a single
valid path:

- `status=designer_passed`: fill the artifacts by high-confidence extraction
  per `../references/design-package-bridge.md`, so `confidence` is materially
  higher than shallow extraction (for example `confidence.layout >= 0.8`).
- any missing receipt, `status=fallback_accepted`, or
  `adapter_extraction=shallow_text_extraction`: return `BLOCKED` to Phase 1.5a
  and run `pico-spatial-app-designer`; do not generate an app from shallow text.

## 4. required_tools

None. This adapter is pure LLM extraction.

## 5. required_references

- `../references/evidence-extraction.md`
- `../references/input-normalization.md`
- `../references/design-package-bridge.md`

## 6. side_effects

- Writes `.scratch/evidence_packet.json`
- Writes `.scratch/normalized_spatial_spec.json`
- Writes `.scratch/assumption_ledger.json` when ambiguity exists

No external network, no MCP calls, no temp files outside `.scratch/`.

## 7. failure_mode

If the intent is too vague to infer an app archetype or target module / output,
return `BLOCKED` to Phase 1 and ask only for the missing architecture-impacting
information. Otherwise record weak-evidence assumptions in
`assumption_ledger.json` without choosing the root container or window model.

Weak-evidence extraction policy:

- record absence of explicit spatial features as evidence, not as a decision
- record absence of immersion need as evidence, not as a decision
- use `layout_intent.regions = ["header", "content"]` only as a provisional
  content-structure assumption when no better structure is explicit

If the `pico-spatial-app-designer` design package is unavailable or any of the
three delivery gates has not passed, return `BLOCKED` to Phase 1.5a with the
missing designer deliverables/gates. A missing design package blocks no-visual
app generation.

## Extraction procedure

0. Read `.scratch/design_escalation_receipt.json`. If `status=designer_passed`,
   `bridge_allowed=true`, and `adapter_extraction=design_package_bridge`,
   extract by the field-level fill rules in
   `../references/design-package-bridge.md` instead of shallow text. Record the
   container leaning and window leaning as narrative evidence for Phase 4 to
   decide, never as an adapter-level choice, and add one traceable
   `evidence_trace[]` entry per consumed `review/*.md` source. If the receipt is
   missing, `status=fallback_accepted`, or `adapter_extraction` is not
   `design_package_bridge`, return `BLOCKED` to Phase 1.5a.
1. Extract facts only: app archetype, task verbs, explicit spatial words,
   explicit architecture constraints.
2. Normalize to one app interpretation. Do not preserve multiple parallel app
   shapes unless there is a real conflict; record conflict or ambiguity instead.
3. Do not select a root container or window model. Preserve evidence that may
   later support a flat business UI, passthrough, 3D entities, volumetric depth,
   immersive environment, or multiple independent windows.
4. Every provisional layout/content assumption must appear in `assumption_ledger.json` with impact and
   confidence.

## Output template

The example below shows the legacy shallow text shape only as a field reference.
No-visual app generation must use an accepted design package; confidence is
materially higher and the facts are richer; see
`../references/design-package-bridge.md` §E.1.

```json
{
  "facts": {
    "app_type_candidates": ["<archetype>"],
    "regions": ["header", "content"],
    "repeated_structures": [],
    "visible_states": [],
    "spatial_cues": ["flat_panel"],
    "interaction_cues": []
  },
  "unknowns": ["visual_style", "exact_layout"],
  "conflicts": [],
  "confidence": {
    "layout": 0.35,
    "interaction": 0.45,
    "spatial_mode": 0.55
  }
}
```
