# `<Topic Name>` Analysis Topic Template

Use this template when adding or restructuring an analysis subprotocol. The subprotocol document describes how to investigate one topic; it does not decide whether the subprotocol should be activated. Activation is owned by the Main protocol in [Analysis Topic Routing](../routing/analysis-topic-routing.md).

## Subprotocol Responsibility

State:

- what phenomenon or mechanism this topic investigates;
- what evidence the topic can confirm, narrow, or rule out;
- what evidence it must hand back to the Main protocol.

Do not make `primary root cause`, `majority of budget`, `confirmed`, or `server-side closure` prerequisites for entering the topic. Those are post-analysis judgments.

## Subprotocol Execution Contract

When this subprotocol is added to the execution queue, execute this document in order. A subprotocol remains executed even when its evidence chain is incomplete. In that case, report the exact evidence gap and cap the conclusion level.

Every topic execution must produce:

1. `activation_context`: the signal, abnormal window, and dependency relation that caused the Main protocol to add this subprotocol;
2. `evidence`: stable evidence IDs and the observations derived from them;
3. `analysis_steps`: the checks performed and their results;
4. `closure`: the deepest causal-chain layer reached and concrete missing data;
5. `causal_assessment`: `background_noise`, `candidate`, `contributor`, `amplifier`, `upstream_cause`, or `primary_cause`;
6. `controller_handoff`: cross-topic evidence that the Main protocol should assess after this subprotocol completes;
7. `limitations` and `next_actions`.

The subprotocol must not activate, skip, or load another subprotocol. If its evidence is relevant outside its own scope, hand the evidence and its causal relationship back to the Main protocol. Only the Main protocol applies the Activation Gate, updates the execution queue, and decides whether another subprotocol runs.

## Evidence Availability

List the minimum evidence needed to execute this topic and distinguish:

- evidence available now;
- evidence missing but queryable from the current trace;
- evidence unavailable from the current artifacts.

If the topic can execute partially, continue with the available evidence and record a partial closure. Do not reject the topic merely because the strongest conclusion is not yet provable.

## Analysis Steps

Define the topic-specific evidence order. Each step should state:

1. the question being answered;
2. the trace/query/log evidence to inspect;
3. the interpretation of positive, negative, and missing results;
4. the cross-topic evidence to hand back to the Main protocol, if the result reveals one.

Prefer causal-chain steps over keyword counting. A long slice or frequent keyword is not sufficient to establish a root cause.

## Closure Levels

Define ordered closure levels for this topic. Use a level that reflects how far the evidence chain was actually resolved, for example:

```text
signal
path_relevance
mechanism
downstream_cause
verified_cause
```

The topic may be `executed` at any level. A lower closure level limits `conclusion_level`; it does not remove the topic from the execution results.

Every major step must leave an auditable record in the output:

- the query, artifact, or observation used;
- the time-window overlap and affected thread/process;
- the quantitative result where available;
- the causal interpretation;
- the negative or alternative result that was ruled out;
- every cross-topic evidence item handed to the controller.
- for a PICO Spatial diagnosis with an exposed KB backend, recording `extensions.knowledge_base` is mandatory and governed by the [PICO Spatial PerformanceKB Mandatory Gate](../common/knowledge-base-usage.md): record the selected observations, the window-anchored query, and every gate stage status. When the backend is unavailable or retrieval fails, record that status instead of inventing KB evidence; do not silently omit the record.

At minimum, a topic execution must contain one path-level observation, one mechanism-level drill-down, and one closure/limitation judgment. A topic is not deep enough if it only repeats the symptom, names a long slice, identifies a service, or gives generic optimization advice without showing the intermediate evidence.

## Controller Handoff

After completing the topic-specific analysis, hand back only evidence that crosses the topic boundary. Do not name, activate, or prescribe another subprotocol. The handoff should contain:

```yaml
controller_handoff:
  - evidence_refs: [<stable evidence ids>]
    signal: <observed cross-topic signal>
    time_window: <overlap with the abnormal window>
    dependency_relation: direct | dependency | adjacent | unrelated
    question_for_controller: <what the main controller should assess>
```

An empty handoff is valid. The Main protocol independently scans the shared topic registry and applies the Activation Gate; it must not infer that no other subprotocol is relevant merely because this handoff is empty.

## Output Supplement

Add topic-specific fields under `extensions.<topic-key>` in the unified [Output Contract](../routing/output-contract.md). Keep the common lifecycle fields in the topic output:

```yaml
topic_state:
  activation: activated
  execution: completed | completed_with_evidence_gap | blocked
  closure_level: <topic-defined level>
  causal_role: <topic-defined role>
  controller_handoff: [<cross-topic evidence items>]
```

## Topic Checklist

- [ ] The topic has no independent Activation Gate.
- [ ] The topic can execute with partial evidence.
- [ ] Closure level is separate from activation and causal priority.
- [ ] Cross-topic evidence is handed to the Main protocol without naming or activating another subprotocol.
- [ ] The output contains quantitative path and mechanism evidence, not only a symptom or recommendation.
- [ ] At least one alternative explanation is explicitly ruled out or marked unresolved.
- [ ] Missing evidence is concrete and minimal.
- [ ] Output follows the unified output contract.
