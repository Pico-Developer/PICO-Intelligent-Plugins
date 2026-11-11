# Capability Graph Authoring

Read this reference when deriving a surface graph, scenario facts, or Contract business goals.
`interact route` uses navigation edges; `interact route --goal` executes a goal through JEV.

The capability graph is a declarative file from application sources or a host-maintained derivation. It describes
which surfaces exist, how to move between them, and which published action each move triggers.
`accessibility contract init` imports it into `.pico` Contract state; `interact route` consumes it.
No application names, node IDs, or prompts are hard-coded in the CLI — the graph is data the
application exposes. A host-maintained graph does not require an APK or ROM change.

## File name and location

The source file must be named exactly:

```
pico_accessibility_capability_graph.xml
```

It is discovered under an Android `res/xml` resource directory. `contract init` looks in:

- `app/src/main/res/xml/pico_accessibility_capability_graph.xml`; and
- `<module>/src/<sourceSet>/res/xml/pico_accessibility_capability_graph.xml` for every source set
  that already declares a Spatial Accessibility component (derived from the Contract component
  source files).

Exactly one such file may exist. Two or more copies fail closed.

### Importing a graph from an explicit path (external applications)

When operating an application you did not build — or when one maintainer keeps one graph file per
package outside `res/xml` — pass the file explicitly instead of relying on `res/xml` discovery:

```bash
pico-cli accessibility contract init \
  --project <project-root> \
  --package <application-id> \
  --capability-graph <path-to>/<application-id>.xml \
  --format json
```

- `--capability-graph` accepts a project-relative or absolute path and overrides `res/xml`
  discovery. A missing file fails closed with `INVALID_CAPABILITY_GRAPH_SOURCE`.
- `--package` stamps the generated Contract's `packageName`, so one `<application-id>.xml` maps to
  one package's Contract. Keep one graph file per package (for example `graphs/com.vendor.app.xml`)
  so the agent can pick the file by package name.
- The imported graph is validated against the inventoried Contract components exactly like the
  `res/xml` path, then persisted into the Contract with its source path and SHA-256 digest.
  `project-audit` fails when that XML changes, disappears, or cannot be rediscovered; rerun
  `contract init` after reviewing the change. `interact route` then consumes the reviewed graph.

## Schema

```xml
<?xml version="1.0" encoding="utf-8"?>
<capabilityGraph version="1">
  <surface id="main-menu" label="Main Menu">
    <component semanticId="menu.start" />
    <marker semanticId="menu.root" />
  </surface>

  <surface id="chapter-1" label="Chapter 1">
    <component semanticIdPrefix="chapter1." />
    <marker semanticId="chapter1.root" />
  </surface>

  <route id="enter-chapter-1" from="main-menu" to="chapter-1">
    <action semanticId="menu.start" key="enter_chapter_1" />
  </route>
</capabilityGraph>
```

### Root

- `<capabilityGraph version="1">` is required; `version` must be exactly `"1"`.
- Must be safe, valid XML. `<!DOCTYPE>` and `<!ENTITY>` are rejected (no XXE).
- Limits: at most 128 `surface`, 512 `route`, and 4096 total component/marker references.

### `<surface>`

A surface is one logical screen/state the user can be on.

- `id` (required): unique surface identifier used by `route.from` / `route.to`.
- `label` (optional): human-readable name.
- `reuseTargets` (optional boolean): `true` declares that control selectors, labels, visibility,
  enabled state and action schemas stay stable during ordered actions on this surface.
  `interact batch` automatically reuses targets for semantic-selector actions declared on that
  one surface, excluding navigation edges. Value changes alone are allowed. Runtime window,
  structure and stale-node signals still invalidate reuse; the snapshot never leaves the process.
  Omit this attribute when stability is unknown.
- `<component>` (zero or more): components reachable/operable while on this surface.
- `<marker>` (zero or more): components whose runtime presence proves the user is on this surface.
  `interact route` polls markers to confirm each hop actually landed. Give every navigable surface
  at least one marker that is unique to it; a marker shared with another surface causes
  misdetection.

Each `<component>` and `<marker>` references Contract components by **exactly one** of:

- `semanticId="exact.id"` — must match exactly one Contract component; or
- `semanticIdPrefix="family."` — matches every Contract component whose `semanticId` starts with
  the prefix (useful for data-driven instances).

Supplying both, or neither, fails closed. A `semanticId` that matches zero or more-than-one
component fails closed; a prefix that matches zero components fails closed.

### `<scenario>` (optional, inside a surface)

Navigation edges alone do not describe gameplay or multi-step business goals. An application can
declare one scenario on a surface, with `suitability="static"` or `"reactive"` and named facts:

```xml
<scenario suitability="static">
  <fact name="preconditions" json='{"mode":"practice","threats":false}' />
  <fact name="actionTiming" json='{"save":{"completion":"public-status"}}' />
  <fact name="completion" json='{"publicState":"saved"}' />
</scenario>
```

Each fact has a unique non-empty `name` and a valid JSON `json` attribute. XML escaping still
applies. Limits: 1–128 facts and 65536 UTF-8 bytes for `JSON.stringify(facts)`, including names,
punctuation and escaping. XML import, Contract validation and persistence use the same budget.
Import preserves `capabilityGraph.surfaces[].scenario.facts`. The CLI interprets only the reserved
`interaction.requiresRealTimeReaction` boolean for eligibility; other gameplay facts remain data.
When present, `interaction` must be a JSON object and `requiresRealTimeReaction` must be a boolean.
Invalid types fail explicitly. Missing scenarios remain unknown; every goal action component must
belong to a surface with valid source-derived scenario facts before device access. Old action-only
graphs can omit scenarios. A static label never overrides a true real-time reaction fact.
Use facts for map geometry, action effects, preconditions, duration, cooldown and public completion
conditions. Facts must describe application behavior; never embed source bodies, prompts or a
previously successful action sequence. Keep current observed state separate from static map data.
An inventory without the needed scenario facts cannot promise first-run end-goal planning.
Derive suitability from source behavior: does the world change autonomously, does that affect
the requested actions, and must the operator react in real time? Record the causal facts and
their source. Current A11Y does not support that gameplay; do not infer support from available
buttons or mark it static to make a goal executable. Keep menus and genuinely threat-free
tasks separate, with public markers that identify the active scenario.

### `<goal>` (optional, inside the root)

Craft can derive a goal from existing source and public action semantics and keep it in a
host-local graph. Each `<goal json='...'>` contains a JSON object that imports into
`capabilityGraph.goals[]`. Components use the inventoried Contract IDs, including 2D components.
The executable sequence is data interpreted by the shared JEV runtime.

```json
{
  "id": "save-document",
  "label": "Save the document",
  "suitability": "static",
  "timeoutMs": 6000,
  "sourceDependencies": [{ "file": "app/src/main/App.kt", "sha256": "<current-source-sha256>" }],
  "steps": [
    {
      "id": "save",
      "action": { "componentId": "document-save", "key": "click" },
      "preconditions": [{ "componentId": "document-editor", "present": true }],
      "completion": {
        "kind": "observed",
        "timeoutMs": 2000,
        "conditions": [
          { "componentId": "document-status", "field": "stateDescription", "equals": "saved" }
        ]
      }
    }
  ],
  "completion": {
    "timeoutMs": 2000,
    "conditions": [
      { "componentId": "document-status", "field": "stateDescription", "equals": "saved" }
    ]
  }
}
```

- Omitted `dependsOn` preserves step order; an explicit array names dependencies, and `[]`
  declares none. Cycles, missing dependencies, undeclared actions and invalid arguments fail
  before execution. Execution remains serial.
- A completion is `returned` only when source proves synchronous completion, or `observed` with
  public predicates and a timeout. Optional `settleMs` is a source-proven settling/cooldown
  boundary; never invent one to hide application timing bugs.
- For effects requiring feedback, declare empty `steps` and one `policy` with `maxActions`
  (1–256), public `until` conditions and 1–128 ordered `rules`. Each rule has the same action and
  completion fields as a step, plus public `when` conditions; dependencies do not apply.
  Selection uses current public state in JEV, without a new model turn. Final goal conditions
  still prove completion after `until` ends selection.
- Optional rule `oppositeOf` references another rule whose effect is the source-proven inverse.
  Before an immediate reversal, prefer another matching rule in the declared order; allow the
  reversal if no alternative applies. This is a tie-break, not a learned navigation route.
- Goal `preconditions` declare runtime eligibility before dispatch and at every policy decision.
  A changed eligibility returns `SCENARIO_UNSUPPORTED` before the next action. Observed step
  conditions may use `changed: true` instead of `equals` to compare with pre-dispatch public state.
- Conditions test exact component presence, or exact `text`, `value`, `stateDescription`,
  `enabled`, `checked` or `selected` values. The final goal always requires public conditions.
- Source dependency hashes are checked once before device access. Re-derive the goal when a source
  changes. Store declarative actions and semantics; do not embed code or a route learned from tests.
- Limits: 128 goals, 256 steps per goal, 64 predicates per condition set, 256 KiB per XML goal,
  a goal deadline of 1–120000 ms and observation/settle bounds of 0–30000 ms.
- The deadline prevents dispatching later steps after expiry. An in-flight ROM call may return
  after it; its accepted/uncertain result is preserved rather than hidden or replayed.
- Current goal mode requires `--project`; direct external graph action mode remains supported.
- Import also writes adjacent `contract.goals.json` with package, Contract path, goal IDs,
  labels, suitability, target surface IDs and scenario facts/public markers. Missing surface
  suitability is `unknown` in the catalogue. The Agent first recognizes the current and requested
  scenario; unsupported real-time gameplay stops before mutation. Supported goals use one
  `route --goal`; the CLI reads and validates the full Contract and declared dependencies.

### `<route>`

A route is one directed edge from one surface to another, performed by one published action.

- `id` (required): unique route identifier.
- `from` (required): source surface `id`.
- `to` (required): destination surface `id`.
- `<action>` (required, exactly one):
  - `semanticId` (required): must match exactly one Contract component.
  - `key` (required): must be an action key that component actually publishes.
  - `arguments` (optional): a JSON **object** string, e.g.
    `arguments='{"rotation":[0,0,0,1]}'`. Arrays or non-objects fail closed.

`arguments` is supported only after `contract init` resolves the action schema. Direct
`interact route --capability-graph <host-local.xml>` accepts parameterless navigation edges only;
use a project-backed Contract for parameterized navigation.

The referenced `semanticId:key` must be published by the Contract (verified at `contract init`),
otherwise it fails closed.

## Authoring rules

- Make every entry edge land deterministically. One "continue" action that resolves to a dynamic
  destination must be modeled as per-destination entry actions (for example `enter_chapter_1..N`),
  not a single edge whose static `to` is wrong when the save state differs.
- Each surface's marker must be unique to that surface and only render on it. A marker that also
  appears inside another surface makes surface detection ambiguous.
- Declare all reachable entry edges. A missing `menu -> chapter` edge forces a route failure and a
  recovery query at runtime.
- The action on an edge must be a real business/navigation action the owner publishes at runtime on
  a host-reachable node (see `authoring.md`), not a proxy button.

## Lifecycle

```bash
# 1. Author pico_accessibility_capability_graph.xml under res/xml, OR keep one
#    <application-id>.xml per package and import it explicitly.
# 2. Import it into Contract state (also refreshes Spatial declarations):
pico-cli accessibility contract init --project <project-root> --format json
#    External/explicit form, one graph per package:
pico-cli accessibility contract init \
  --project <project-root> \
  --package <application-id> \
  --capability-graph <path-to>/<application-id>.xml \
  --format json
# 3. Navigate and perform in one call, no intermediate model turn:
pico-cli interact route \
  --project <project-root> \
  --component <target-contract-id> \
  --action <published-action-key> \
  --format json
#    External runtime form, no project Contract required:
pico-cli interact route \
  --package <application-id> \
  --capability-graph <host-local>/<application-id>.xml \
  --semantic-id <target-semantic-id> \
  --action <published-action-key> \
  --format json
```

`--package` is taken from the Contract; pass `--package <application-id>` only when the Contract has
no `packageName`. `project-audit` treats a stale or source-unverified route graph as an error, so
re-run `contract init` whenever surfaces, markers, or edges change.

## AI operating loop with an imported graph

For an application whose graph is imported by package, the agent runs a 0-query loop:

1. Resolve the package's graph file (`<application-id>.xml`) and run `contract init --package <id>
--capability-graph <file>` once. On `INVALID_CAPABILITY_GRAPH_SOURCE`, read the message, fix the
   XML, and re-run until success.
2. Read the resulting Contract to understand what the app exposes: components (semanticId + actions)
   and the capabilityGraph (surfaces + routes). This is how the agent "knows what the app has"
   without scanning source.
3. Operate: `interact query` only when the starting surface is unknown; `interact act`/`batch` when
   already on the target surface; use project-backed
   `interact route --project <project> --component <target> --action <key>` or external
   `interact route --package <id> --capability-graph <xml> --semantic-id <target> --action <key>`
   to navigate across surfaces and perform in one call.
