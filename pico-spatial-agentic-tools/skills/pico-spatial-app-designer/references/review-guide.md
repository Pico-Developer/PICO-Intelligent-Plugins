# Review Guide — independent critique

The two critique phases are the heart of this skill. The lightweight version — you re-checking your own plan and prototype — is built into the loop and is enough for most requests. This guide is for when you want the critique to be genuinely independent: the user asks for a rigorous audit, the design is high-stakes, or the same context that built the design shouldn't be the one grading it.

## Why independence matters

A reviewer working in the same context that produced the design tends to confirm its own choices — it already believes the plan is good. Real review value comes from rebuilding the evidence from scratch. So for a serious pass, spawn a **fresh-context reviewer** (a subagent with no memory of how the design was made) and give it only the artifacts, not your reasoning about them.

## What the reviewer checks

Point the reviewer at `design-doc.md` and `preview.html` and ask it to **rebuild the judgment from the artifacts**, not accept the generator's summary:

**Design quality**

- Is the app's job a clear decision/task outcome, or a widget wall?
- Is each spatial affordance justified with a 2D counterfactual that actually beats the flat version?
- Were three real alternatives compared, with reasons the rejected ones lost?
- Was every window size validated internally, while the final document records only implementation-relevant default/min/max dimensions?
- Do layout, components, and visual language derive from the domain — would swapping the domain change the design?
- Is there a single primary focus, with the signature element readable and its surroundings quiet?

**Prototype fidelity** (rebuild the coverage denominator independently — do not copy the generation-side mapping)

- Every state and transition triggerable with a visible result?
- Each component and variant present and reachable?
- Is the vendored SpatialUI bundle inline, with every planned `sui-*` tag registered and wired through its documented public event?
- Does any native control or hand-rolled dialog duplicate an available SpatialUI Web component without a specific justified gap?
- Does the installed `PicoTheme` explicitly define all 16 roles, preserving SpatialUI Vibrant values where the design does not override them?
- Is the app root rendered on SpatialUI Web's `Material.Regular` glass rather than a custom gray/blur/opaque substitute?
- Each data binding shows normal, fallback, and error?
- Does viewport resizing produce natural reflow without exposing layout-tier or other design/debug-only controls; is reduced-motion respected?
- High-risk transitions blocked by a SpatialUI confirmation dialog?

## Verdicts and the patch loop

The reviewer outputs, per finding: the target (which state/component/window), the evidence, the user impact, and a patch goal. It returns one of:

- **pass** — clears the quality bar, no active blocking finding.
- **changes_requested** — patchable gaps; feed the patch goals into the bounded loop.
- **block** — a core fact is missing (a state with no trigger, a binding with no fallback, an unvalidated window size, an incomplete color scheme, or a non-SpatialUI glass root). A block is not offset by an overall score or "the Web only validates logic."

A reviewer only reports findings — it does **not** rewrite the design. Patches are applied by the generator in the Critique-again phase, capped at three rounds. Remember that any change to states, sizing, components, tokens, or interaction invalidates the old `preview.html` — re-run Build and re-review. If three rounds don't clear the bar, report what's still unmet plainly rather than lowering the bar.

## Device validation boundary

Device comfort, occlusion, physical size, input hit, and performance are **never** validated here — mark them `not_performed`. Passing this review means the design's logic and layout are sound and ready to hand to a downstream code-generation skill; it does not mean the experience is verified on a headset.
