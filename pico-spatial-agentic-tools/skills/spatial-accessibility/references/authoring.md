# Accessibility Authoring

Read this reference only when creating, changing, migrating, or auditing application source.
Runtime-only natural-language operations do not need it.

## Ownership

- Native 2D View and Compose controls stay on Android's standard Accessibility path. Use standard
  controls and Compose/View semantics; do not add a parallel Craft declaration or proxy Entity.
- 3D Entities and Attachment owners use SpatialSDK `AccessibilityComponent` plus
  `SpatialViewContent.setAccessibilityActions`.
- Attachment content remains native 2D View/Compose content under its owner. Put panel transforms
  on the owner and ordinary button, switch, input, and text semantics on the native controls.
- Never install a companion APK, enable an `AccessibilityService`, use coordinates, inspect private
  ECS state, or invent an action.

Every meaningful Spatial owner needs:

1. `AccessibilityComponent(label, value)` with `isAccessibilityElement = true`;
2. a stable, unique, non-sensitive `semanticId`;
3. only the actions the application actually supports;
4. callbacks that return `true` only when handled;
5. current `value` updates after state changes.

All public SDK authoring APIs are main-thread APIs. Each `setAccessibilityActions` call replaces
the Entity's complete semantic ID and action configuration.

Publish each business action on the owner that is actually reachable at runtime, not behind a
separate selection step. If the 3D Entity's own node is not surfaced to the host tree (for example
its projected bounds fall outside the visible host area, or it is only reachable after clicking a
2D "inspect" proxy that opens a detail panel), its published actions cannot be resolved by one
`interact act`/`batch` and every operation degrades into select-then-query-then-act. Keep the owner
itself visible to the host Accessibility tree so `runtime-audit` discovers it and a single call can
target `semanticId:action` directly.

## Workflow

Inventory is a fast, read-only Spatial declaration index. It scans Kotlin production convention
roots and does not inspect native 2D controls or run Gradle.

```bash
pico-cli accessibility inventory \
  --project <project-root> --format json
pico-cli accessibility contract init \
  --project <project-root> \
  --package <application-id> \
  --force \
  --format json
```

The Agent edits application source directly. There is no `accessibility contract apply` command.
Rerun the two commands after changing Spatial owners.

The index reads direct `setAccessibilityActions` calls, literal strings, and file-local
`const val` strings. Computed IDs and custom source roots remain unresolved. Spatial Java
declarations block the static gate because the index cannot prove their owner/action coverage;
migrate them to supported Kotlin source or add a Java analyzer. State-dependent replacement actions
stay outside static action hints and must be covered by scenario runtime audit. Do not move business
logic merely to satisfy the index. Keep the valid SDK shape and complete the unresolved Contract
entry, or record an explicit approved exclusion.

Cross-helper Entity proof is deliberately narrow: the factory must be private, block-bodied, attach
the Component through `apply`, and explicitly return the owner; every caller and return path must
remain provable in the same file. `also` factories, expression-bodied factories, callable
references, import aliases, and ambiguous callers stay unresolved.

Native 2D source does not become a Spatial inventory candidate. Validate it with Compose semantic
assertions, Compose Accessibility Checks, Accessibility Scanner, TalkBack, Switch Access, Voice
Access, and the package runtime query.

## SDK Shape

```kotlin
entity.components.set(
    AccessibilityComponent(
        label = "Planet",
        value = "Not selected",
    ).apply {
        isAccessibilityElement = true
    }
)

content.setAccessibilityActions(
    entity = entity,
    semanticId = "scene.planet",
) {
    onClick(label = "Select") {
        selectPlanet(entity)
        true
    }
    customActions =
        listOf(
            CustomAccessibilityAction("Reset position") {
                resetPlanet(entity)
                true
            }
        )
    move(bounds = SpatialAccessibilityBounds(y = 0f..0.5f)) { position ->
        entity.components.get<AccessibilityComponent>()?.value =
            "Height ${(position.y * 100).roundToInt()} cm"
    }
    rotate()
    scale(range = 0.5f..2f)
}
```

Rules:

- `label` names the object. `value` describes its current state.
- Automation locates the Entity by `semanticId`, never by localized label, Entity UUID, or virtual
  node ID.
- `onClick` maps to Android `ACTION_CLICK`.
- `CustomAccessibilityAction` is argument-free and has a localized result label.
- `move`, `rotate`, and `scale` are SDK-managed parameterized operations. Declare them only when
  the application permits the transform.
- TalkBack cannot supply transform parameters. Add equivalent argument-free custom actions when a
  transform is required in a screen-reader flow.
- Pointer input and Accessibility actions should call the same business function.
- Do not manually construct the transform protocol or cache runtime action IDs.

Use `clearAccessibilityActions(entity)` to remove all actions while retaining the semantic ID and
description. Pass `semanticId = null` in a complete replacement to remove the ID.

## Attachment

The Attachment owner Entity carries the Spatial description, identity, and transforms. Its content
keeps native Android semantics.

```kotlin
attachments.entity("controls")?.let { panel ->
    panel.components.set(
        AccessibilityComponent(label = "Scene controls", value = "Ready")
    )
    content.setAccessibilityActions(panel, "scene.controls") {
        move(bounds = SpatialAccessibilityBounds(y = 0f..0.5f))
        scale(range = 0.5f..2f)
    }
}
```

Do not duplicate a content button action on the owner. The owner handles panel-level movement,
rotation, scale, and panel-wide operations.

## Contract

`.pico/accessibility/contract.json` is a generated Spatial audit artifact. It records source
anchors, runtime semantic IDs, declared actions, approved exclusions, and unresolved declarations.
Existing native 2D runtime components remain readable for backward compatibility, but inventory
does not create new 2D authoring entries.

For multi-surface applications, keep the reviewed route graph in
`app/src/<source-set>/res/xml/pico_accessibility_capability_graph.xml`. It resolves against
completed Contract components, not raw AST candidates.

```xml
<capabilityGraph version="1">
  <surface id="home">
    <component semanticId="app.home" />
  </surface>
  <surface id="details">
    <component semanticIdPrefix="app.details." />
    <marker semanticId="app.details.ready" />
  </surface>
  <route id="home-to-details" from="home" to="details">
    <action semanticId="app.home" key="open_details" />
  </route>
</capabilityGraph>
```

Each route's navigation action must deterministically land on the `to` surface it declares, and
every surface must be identified by a marker that is present only on that surface. A route whose
action resumes to a variable surface (for example a single "continue" control that re-enters
whichever surface was last saved) breaks route destination checks and forces recovery queries;
model it as a dedicated per-destination entry action instead. Do not reuse a marker component that
also exists on other surfaces, or surface detection becomes ambiguous. Declare the real entry edges
for every surface reachable from an entry point, not only the first one.

## Approval Gate

Before the first runtime operation, determine whether the project/package already has a current
Contract and passing project/runtime audits for the relevant scenario. If the baseline is absent or
stale, run inventory and Contract refresh, review the direct source edits and exclusions, then
present one bounded approval request covering source edits, build/install, both audits, and the
following runtime operation. Do not ask once per component, file, command, query, or action.

## Gates

Static Spatial gate:

```bash
pico-cli accessibility project-audit \
  --project <project-root> --format json
```

It blocks unresolved Spatial owners, unsupported Spatial Java, stale IDs/actions, missing Contract
coverage, and stale route graphs. Warnings require an explicit disposition.

Runtime gate after build, install, and launch:

```bash
pico-cli accessibility runtime-audit \
  --project <project-root> \
  --device <serial> \
  --package <application-id> \
  --format json
```

It proves that required Spatial nodes publish a non-empty label, semantic ID, current action schema,
and expected parent relation. Use `--scenario` and `--components` for one opened surface; other
components remain pending.

Report complete support only after:

- native 2D Android checks pass;
- Spatial project audit has zero errors;
- the app builds and launches;
- runtime audit is non-empty, non-truncated, and has zero errors;
- required TalkBack and device/manual gaps are disclosed.

## Cross-surface navigation (capability graph)

To let `interact route` navigate across surfaces automatically, the application ships a
`pico_accessibility_capability_graph.xml` under `res/xml` declaring its surfaces, markers, and
routes. Graph authoring is a separate reference selected directly by the Skill entry; do not
chain reference loads from this file. Single-surface operations do not need a graph.
