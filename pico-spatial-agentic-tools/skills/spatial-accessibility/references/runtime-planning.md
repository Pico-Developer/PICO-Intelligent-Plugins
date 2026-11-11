# Runtime Planning

Read before gameplay or multi-step end-goal requests.

- Classify the requested behavior before code, source scans or device queries. A request to
  react immediately to moving hazards, unpredictable events or timed targets is already enough
  to reject current A11Y gameplay. Report unsupported with zero queries and zero actions.
  Existing scene facts or supplied current public state can also decide it without a query.
  Do not query merely to confirm a rejection or a supplied source-proven static scene.
  Supplied prepared mode/initial state counts as current state: if it matches a source-proven
  static scenario, dispatch the goal directly. Its initial observation checks eligibility within
  the same CLI call. Do not add a separate query to verify setup.
- Identify the scenario before choosing actions. The catalogue includes `scenarios[]` with
  source-derived `facts`, public `markers` and each goal's `surfaceIds`. Match supplied current
  public state, or one compact package query's `controls[]` / `content[]` names, values and
  semantic IDs. A missing or ambiguous gameplay scene is unknown, never static by default.
- Assess the behavior, not just a `suitability` label or a mode name. Autonomous movement,
  hazards, timed targets or random events that affect the required actions need real-time
  observation and reaction. Such gameplay is unsupported by the current A11Y chain, even when
  every individual action is published or a goal happens to be labeled static. Report the scene,
  factual behavior and A11Y limitation, then stop before any goal, route, act or batch dispatch.
  Do not disable events, select a simpler mode, substitute a static goal or try faster retries.
  Do not suggest mode switching or promise to play a substituted task after reporting unsupported.
  Static menus and source-proven threat-free tasks are assessed separately.
- Read the facts of the scene whose public markers match the current UI, even if it is not in
  the static goal's `surfaceIds`. `facts.interaction.requiresRealTimeReaction=true` is decisive:
  report unsupported and stop with zero goal calls, regardless of `suitability` being missing,
  `unknown` or `static`. A query already establishes this; never ask the CLI to try the goal
  to decide whether these facts are valid.
- Establish suitability from the persisted Contract's scenario rules. Unpredictable changes that
  require observing and reacting before the next bounded ROM action completes are unsupported.
  Missing response deadlines, public state, or completion semantics also block such gameplay.
  Stop before mutation; never classify by repeatedly failing. Static menus and explicitly
  threat-free modes remain eligible. Cosmetic NPC movement alone is not a blocker.
- Treat `SCENARIO_UNSUPPORTED` as a terminal runtime result. Report the supported scenario;
  do not follow it with a query, action, retry or a suggestion to query or relabel the Contract.
- A local event-driven controller could handle published state and deadlines without an AI turn
  per action. This Skill provides no such controller; do not install a service or claim support.
- Derive a host Contract goal from initial state, preconditions, action duration, ordering and public
  completion conditions. The goal is Craft data; application or ROM changes are not needed.
  Do not treat a controls-only inventory or successful dispatch as a task contract.
- Match a natural-language end goal to `capabilityGraph.goals[].id` and issue one
  `interact route --project <project> --goal <id> --compact --format json`. JEV compiles the
  dependency order once and handles navigation and necessary observations within that call.
- A goal may declare a bounded `policy` instead of fixed steps when action effects need feedback.
  The CLI selects the next source-derived rule from current public state without a model turn.
  `policy.until` stops dispatch; the separate final completion still proves the business outcome.
  A rule's optional `oppositeOf` names its source-proven inverse. Before immediately reversing,
  prefer another eligible rule; retain the reversal when no alternative applies.
  Read `.pico/accessibility/contract.goals.json` (or the supplied catalogue) directly and let the
  CLI validate the full Contract. Missing scene facts are unknown, not static. A malformed
  `interaction` object or non-boolean `requiresRealTimeReaction` is invalid, not a truthy flag.
  If gameplay facts are missing or conflict, stop and report that a new source assessment is needed.
  Do not inspect the wrapper or help, or probe support by playing.
  Use the project path and device binding from current task context without rediscovery.
- `--reuse-targets` requires stable targets, labels, visibility, enabled state, and action schemas
  throughout that batch. Do not use it across navigation or with state-dependent selectors.
  Reuse ends with the process; no node IDs or runtime snapshots persist across commands.
- Respect declared asynchronous completion and cooldowns. Never accelerate by overwriting an
  accepted action still in progress. A step declares source-proven synchronous `returned`
  completion or `observed` public predicates, plus a justified optional `settleMs`.
  If timing cannot be honored, stop rather than guessing. Timers do not prove a business goal.
- Fixed plans can observe a single stable leaf's fields through the original ROM `node` command.
  Absence, new widgets, policy eligibility and inputs still require a complete observation.
  `fullObservations` and `nodeObservations` report this distinction; a node read never makes a
  cached package tree current.
- `performed=true` means the handler accepted an action. Report dispatch and end-goal completion
  separately. Use a returned application result or one final public-state observation as evidence.
  If the goal is incomplete, inspect the failed step and public state; do not replay the goal.
  Accepted or uncertain steps are not safe restart points. The current interface does not resume
  a partially executed goal automatically.
- Benchmark new ephemeral Agent sessions with empty workspace caches and no previous transcripts.
  Ship source-derived Contract rules as product inputs, not a route learned from earlier test runs.
  Record planning, query, execution, and total time separately. Use the same application build,
  scenario, initial state, and success criteria for each comparison; preserve every failed run.
  Do not estimate full Agent time from a CLI duration. Without an external timer, omit Agent time.

## Source-derived Contract shapes

Establish SourceReady from readable, current application source, published semantics and matching
dependency digests. Unknown SourceReady or scene suitability blocks dispatch; do not guess a static
scene or probe it by playing. SourceReady is a readiness decision, not an extra Contract field.
For a trusted static scene with supplied initial state, derive the plan once and issue one goal call
with zero separate queries. Internal eligibility/completion observations remain inside that call.

Native Compose observations use component `kind: "2d"` and `binding.kind: "compose"`. For dynamic
text, keep `binding.nativeTextTemplates` identical to `runtimeSelector.textTemplates`; omit a fixed
`label`, `binding.nativeText` and fixed `runtimeSelector.text`. Read-only observations use `actions: []`.
This is a `components[]` entry; expressions are source provenance, never executable code:

```json
{
  "contractId": "progress",
  "kind": "2d",
  "semanticId": "source-only-progress",
  "source": { "file": "app/src/main/Status.kt", "line": 1 },
  "runtimeSelector": {
    "textTemplates": [
      {
        "parts": [
          "Progress ",
          { "expression": "state.completed" },
          "/",
          { "expression": "state.total" }
        ]
      }
    ]
  },
  "binding": {
    "kind": "compose",
    "ownerExpression": "Text",
    "nativeTextTemplates": [
      {
        "parts": [
          "Progress ",
          { "expression": "state.completed" },
          "/",
          { "expression": "state.total" }
        ]
      }
    ]
  },
  "actions": []
}
```

A surface's `scenario` requires suitability and named facts; an object containing only `id` is
invalid. Use the exact boolean field below, never a string or number. Declare source-proven behavior
and public markers; cosmetic NPC motion alone does not require real-time reaction:

```json
{ "suitability": "static", "facts": { "interaction": { "requiresRealTimeReaction": false } } }
```

Goal `timeoutMs` is an integer in `1..120000`; goal/observed-step completion `timeoutMs` and
optional `settleMs` are in `0..30000`; policy `maxActions` is in `1..256`. A policy uses empty
`steps` and `1..128` rules. Each rule references a declared component/action and public predicates.
This `goals[]` shape assumes `cue`, `control` and `progress` are declared; replace the source file,
64-character SHA-256 placeholder, predicates and timings with verified source facts before use:

```json
{
  "id": "finish",
  "label": "Finish task",
  "suitability": "static",
  "timeoutMs": 120000,
  "sourceDependencies": [
    { "file": "app/src/main/Status.kt", "sha256": "<64 lowercase hexadecimal source digest>" }
  ],
  "steps": [],
  "policy": {
    "maxActions": 256,
    "until": [{ "componentId": "progress", "field": "text", "equals": "Progress 3/3" }],
    "rules": [
      {
        "id": "advance",
        "when": [{ "componentId": "cue", "field": "text", "equals": "Continue" }],
        "action": { "componentId": "control", "key": "click", "arguments": {} },
        "completion": {
          "kind": "observed",
          "timeoutMs": 30000,
          "conditions": [{ "componentId": "progress", "field": "text", "changed": true }]
        }
      }
    ]
  },
  "completion": {
    "timeoutMs": 30000,
    "conditions": [{ "componentId": "progress", "field": "text", "equals": "Progress 3/3" }]
  }
}
```

Goal `preconditions` are invariants checked throughout execution, before navigation/actions and
policy decisions. Do not put initial progress such as `Progress 0/3` there: successful progress
would invalidate the goal. Keep initial-only state in the supplied setup or an entry step's
preconditions; put evolving feedback in rule `when`, step completion and final goal conditions.
Omit goal `preconditions` when no persistent qualification exists; an empty array is invalid.

When one public cue combines independent dimensions, such as horizontal and vertical corrections,
derive a condition variant for every valid combined cue so all relevant axis rules remain eligible
at the same time. Do not require a combined cue to equal a single-axis label or make axis rules
mutually exclusive. JEV still selects one action serially and reevaluates public feedback; preserve
the source's combination semantics without embedding an application-specific algorithm.

Public `text`, `value` and `stateDescription` Goal conditions also accept a nonempty literal
`includes` predicate (at most 4096 characters). Match source-proven cue context; it is case-sensitive,
without regular expressions or mixed comparison operators.
