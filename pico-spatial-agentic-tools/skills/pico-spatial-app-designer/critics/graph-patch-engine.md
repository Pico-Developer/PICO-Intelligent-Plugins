# Graph Patch Engine

Make a **local patch** to design facts; never rewrite the entire design. Role: `spatial_design_system_designer`. Patch records are written to [`roles/review-templates/design-critique-report.md`](../roles/review-templates/design-critique-report.md).

## Patch principles

- Only make the minimal change to the problem nodes pointed out by the review findings;
- Preserve the accepted decisions that are unrelated to the problem;
- Bounded: at most `max_patch_rounds` (4) rounds;
- Every patch round must correspond to a problem ID, target node, before evidence, change content, expected improvement, and a verification assertion.

## Patch types (described semantically, no longer bound to Schema opcodes)

**Structural changes** (change set membership or relationships):

- add or remove a state / layout / component / attachment;
- move or reorder nodes;
- add a transition, or merge or split states.

**Field-level changes** (update a node's attributes):

- adjust size, priority, container ownership, experience tier;
- add an Augment / Toolbar / TabBar binding;
- add Reduce Motion, fallback, source, rationale, resize policy, sizing derivation, layout skeleton;
- merge similar content or supplement the justification.

## Rerun after patching

When a patch round changes design facts, the host must rerun the relevant stages per the `orchestration.loop.postPatchRerunStages` in [`workflow.json`](../workflow.json): regenerate the Web validation prototype, preview review, process / originality self-check, and design Critic, until the review and self-check pass or the round limit is reached. If the limit is reached without passing, judge it a failure; do not relax the standard.

Patching does not rerun the reference baseline, nor does it introduce any of the removed deterministic Python gates.
