# Performance Knowledge Base (pico-spatial-knowledge) Usage Constraints

This Skill is trace / evidence-driven. PerformanceKB is read-only, assistive
input for candidate hypotheses, disambiguation rules, and evidence checklists;
it cannot prove the current root cause or replace current-trace evidence.

## 1. Mandatory Gate Contract

This is the normative gate for PICO Spatial performance diagnosis when the
`pico-spatial-knowledge` MCP or another configured PerformanceKB backend is
exposed. Use the available read-only backend and record its name and status.
The stages must run in order:

1. `reference_loaded`: read this document before KB-derived guidance,
   leaf-level drilling, or a root-cause conclusion.
2. `probe`: with MCP exposed, call `graph_stats` and record the real result.
3. `global_triage`: call `query_graph` with the global triage query below.
4. `category_specific`: issue at least one category-specific query for every
   still-relevant reported symptom/category.
5. `window_anchored`: after abnormal-window and leaf/mechanism evidence,
   query the observed mechanism with same-window correlation to refine the
   current candidate set.
6. `pre_conclusion_cross_check`: before `root_cause`,
   `primary_root_cause`, or a `confirmed` / `likely` primary diagnosis,
   query the provisional primary candidate together with its strongest
   remaining alternative and missing discriminator. This challenges the
   ranking; it does not repeat the window-anchored query.
7. `recorded`: record backend, retrieval results, every stage status, exact
   canonical IDs, and skipped/unavailable reasons.

The gate is complete only when every applicable stage has a real tool result,
the order is preserved, and output records the same status. A prose claim, a
query count, a trace-local rule result, or a title without its canonical ID
does not satisfy it. A failed probe or retrieval makes later retrieval stages
`skipped` with a reason and leaves `gate.complete: false`; do not fabricate
results to complete the gate.

Until completion, `diagnostic_contract.conclusion_state` is only `candidate`
or `unknown_need_more_evidence`. In the unified topic report, use the
corresponding `conclusion_level` of `candidate` or `insufficient_evidence`.
Do not treat a KB match as current-Trace proof or its recommendation as the
active repair.

Recommended output:

```yaml
extensions:
  knowledge_base:
    backend: pico-spatial-knowledge
    status: available|unavailable|retrieval_failed|not_applicable
    gate:
      reference_loaded: true
      probe: completed|failed|skipped
      global_triage: completed|failed|skipped
      category_specific: completed|failed|skipped
      window_anchored: completed|failed|skipped
      pre_conclusion_cross_check: completed|failed|skipped
      complete: true|false
    matched_entries: [PERF-...]
    selected_observations: []
    missing_stages: []
    limitation: null
```

`matched_entries` contains only exact frontmatter IDs returned by the backend.
Never infer IDs from labels, titles, paths, filenames, or query text.

## 2. Query Construction

Before refining a KB search, send this global-triage query and wait for its
result:

```text
global bottleneck triage multiple concurrent performance signals no fixed optimization order same degraded interval causal direction thread state
```

Use English symptoms and trace-counter names from the current window, adding
lifecycle, frequency, same-window correlation, thread state, and
producer/consumer direction when useful.

- A category-specific query covers each still-relevant symptom/category; a
  window-anchored query covers the observed leaf/mechanism and same-window
  correlation. The pre-conclusion query compares the provisional primary
  candidate with the strongest remaining alternative and discriminator.
- Keep App-producer and Runtime-consumer/scene-complexity queries separate.
  Same-window overlap makes candidates comparable; it does not make one causal
  path.
- Do not use SDK API/class names, overly generic terms such as `Node`, `Graph`,
  or `content`, entry IDs, exact titles, paths, or filename stems.
- Do not add large numbers of variants. If a category query returns only one
  side of a competing attribution, retry once with both categories, the shared
  counter, and the missing discriminator; report a retrieval gap if it still
  misses the candidate.

## 3. Evidence and Result Boundaries

- Search ranking does not equal root cause ranking. KB output supplies
  candidates and checks; the current trace supplies window, owner, first-late
  edge, thread state, direct leaf duration, and before/after evidence.
- A returned `trace_slice`, `trace_counter`, or suggested check is not an
  automatic query obligation. Select it only if it maps to the current process
  and window, is observable, and distinguishes remaining hypotheses. Record
  selected observations as `planned`, `queried`, `unavailable`,
  `not_applicable`, or `deferred`, with a reason.
- Compare competing candidates against same-window evidence and record each as
  `selected`, `secondary`, `rejected`, or `insufficient`.
- An empty callback, one long parent slice, Binder count, geometry count,
  first-use hitch, high GPU memory, object reuse, or one improved metric alone
  cannot prove a root cause or fix completion.
- If KB and trace disagree, trace prevails and the inconsistency is stated.
  If no match exists, state `KB coverage missing`.
- Keep `workflow_status` separate from `conclusion_level`. For PICO reports,
  keep `extensions.knowledge_base` and `diagnostic_contract` semantically
  consistent, including matched entries, evidence boundaries, recommendation
  tuple, control boundaries, and next measurement.

## 4. Permissible Recommended Action Boundaries

Only the following recommendation kinds are allowed:

- A repair using independently verified public App capabilities or
  content-authoring controls.
- A Runtime-observable measurement that discriminates remaining candidates.
- A rollbackable experiment clearly marked as a hypothesis, not a fix.

Before using a returned recommendation, verify `applies_when`,
`evidence_required`, project capability, `action_surface`, and `agent_behavior`.
Select at most one active recommendation. If no repair is supported but a
developer-controllable cause is distinguishable, use a measurement
recommendation; otherwise state the limitation and stop generating repairs.

Valid action surfaces are `app_code`, `spatial_editor`, `source_asset`, and
`measurement`. Runtime-internal mechanisms are control boundaries only and
must never be converted into an application repair.

## 5. Unavailable or Failed Backend

For generic OS6 workflows, KB retrieval is assistive and must not block trace
analysis. If `pico-spatial-knowledge` is unavailable or retrieval fails,
record the status, missing stages, and limitation; state that the KB is
unavailable and continue strictly with trace / empirical evidence. Do not
claim the gate completed or emit a KB-backed confirmed/likely conclusion. A
trace-only conclusion remains governed by the unified output contract and must
state that no KB cross-check was possible.
