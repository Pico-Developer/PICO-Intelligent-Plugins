# Process Audit Critic

Verify that the design was independently derived: complete process trace, at least three hypotheses, evidence-based selection, requirements traceability, layout derivation, component derivation and design package deliverability. Report missing reasoning artifacts; do not compare visual similarity to a golden design.

Preview process fidelity is mandatory: verify the input readiness table predates generation, the five implementation mapping tables use design-fact items as denominators, and the independent QA evidence is not copied from the generator. If any preview implementation fact changed after `preview.html` or `preview-qa-report.md` was produced, require `preview_build` → `preview_review` → `delivery_self_review` rerun; “product semantics unchanged” is not an exemption.

Audit must fail when:

- any reasoning stage directly claims `pass` instead of closing a complete receipt
  with `completed / blocked`;
- the trace lists stage names or summaries but omits per-stage inputs read,
  instruction files, artifact writes, revisions, or timestamps;
- two or more receipts were batch-written after their artifacts already existed,
  or their timing/order cannot be reconciled with artifact revisions;
- stage receipts were reconstructed after artifact completion;
- a review does not name the exact reviewed revision;
- `preview.html` is older than any active preview source revision;
- Preview QA or delivery self-review references a superseded preview revision;
- invalidated records are still counted as pass.
- any core role document fails its own `minimumCompletenessGate`;
- Coverage Manifest is missing, uses an unsupported zero denominator, or differs
  from the independently rebuilt QA denominator.

Status impact is mandatory: receipt, revision, minimum-document, or Preview
denominator failures make `designStatus=invalid`; missing independent review
evidence makes `designStatus=review_blocked`. A quality score cannot offset either
status.
