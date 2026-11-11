# Standalone UI Workflow Compatibility

Read only for an explicitly selected standalone UI flow or a Run already executing
`spatial-design-to-app`. General app delivery uses `spatial-app-dev-workflow`;
stage-specific UI guidance does not require this workflow.

For a short `intent_only` request in this selected mode, run the registered public
`spatial-design-to-app` Workflow. Start it with the user's unchanged intent, a
workspace-relative target, `generationMode`, and the user's `applicationId` when
explicitly provided. Inspect the installed descriptor and CLI help for its actual
input and operation contract. Complete each caller-agent Handoff using its supplied
instructions and Output Schema, then resume the same public Run.

The sequence is `feature_definition -> design -> design_review -> compose_app ->
compose_review`. The first `feature_definition` caller-agent Handoff owns intent
normalization and creation of `<target>/.scratch/intent-brief.md`. Do not create or
overwrite that artifact before the Handoff. Keep existing Runs on their pinned
contract. A recoverable prerequisite failure leaves the Handoff unanswered and the
Run waiting; do not submit invented success.

Do not start a nested `spatial-design-to-app` Workflow from its `compose-app`
Handoff. Use the implementation and validator sections in the skill as that task's
contract. Figma, screenshot, long-form PRD, hybrid and incremental inputs retain
the existing source-specific declarative flow when that standalone flow is selected.

This workflow writes application code and uses the device. Do not execute it
concurrently with a dev writer against the same app/device. Its Domain path does
not inherit dev's LangGraph caller-pause capability. Check public control support.
A completed UI flow provides its actual artifacts and verification results; use dev
guidance for remaining app delivery without repeating accepted work.
