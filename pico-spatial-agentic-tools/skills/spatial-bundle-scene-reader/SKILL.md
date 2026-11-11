---
name: spatial-bundle-scene-reader
description: >-
  Read an existing Spatial Editor .scenes.json and .bundle handoff on demand.
  Use when inspecting packed scenes, entry scenes, entity names, parent scopes,
  bounded subtrees, transforms, or manifest-to-runtime addressing.
  NOT for scene authoring or repackaging (spatial-editor), SDK component API
  guidance (spatial-sdk-guideline), Kotlin Entity edits (spatial-sdk-scene-builder),
  or complete app integration (spatial-app-dev-workflow).
license: 'Apache-2.0'
---

# Spatial Bundle Scene Reader

## When to Use

- A project already contains co-located `<name>.bundle` and `<name>.scenes.json`, and the question
  asks which scenes are packed, which scene is the entry, or whether an entity exists.
- Inspecting names, parent scopes, transforms, or bounded subtrees in an existing manifest.
- Mapping manifest addresses to runtime traversal as a subordinate inspection step in
  `spatial-app-dev-workflow`.

### Runtime scene identity

Use the delivered scene's `runtimeSceneKey` unchanged when loading the verified bundle.
The key depends on that bundle's actual packing root. For example, only when the root is
`Sources`, `Sources/Scenes/Room.usda` maps to `Scenes/Room`. Do not infer a fixed prefix
for new bundles. The scene name,
`sourcePath`, legacy `bundlePath` and authoring entry path are not load arguments.
For older/external bundles without this field, use a verified key from that exact bundle
or repackage it; do not strip/add `Scenes/` or choose an ambiguous suffix match.

## When NOT to Use

- Authoring, modifying, or repackaging scene content — use `spatial-editor`.
- SDK component API facts or runtime component diagnosis — use `spatial-sdk-guideline`.
- Implementing or editing Kotlin Entity loading, hierarchy, or behavior — use
  `spatial-sdk-scene-builder`.
- Complete integration, build, or APK validation — keep `spatial-app-dev-workflow` as the enclosing
  workflow; this reader only supplies manifest facts.

## Manifest Facts

Verified against a managed Workflow pack (`detail: "full"`, 1 scene, 2135 entities, 4.1 MB):

| Level  | Fields                                                                                                                                                  |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Top    | `schemaVersion` (`"0.1"`), `scope` (`bundle_scenes`), `activeScenePath`, `detail`, `sourceTool`, `source`, `scenes[]`, `warnings[]`                     |
| Scene  | `id`, `name`, `guid`, `sourcePath`, `bundlePath`, `runtimeSceneKey`, `container`, `entityCount`, `rootCount`, `hierarchy[]`, `entities[]`, `warnings[]` |
| Entity | `path`, `parentPath`, `name`, `entityId`, `protocolEntityId`, `type`, `transform`, `components[]`, `resources`, `bounds`, `active`                      |

`sourcePath` is the scene source (for example `Sources/Scenes/Room.usda`). `activeScenePath` is
the entry scene. `hierarchy` is a nested tree; `entities` is the same set flattened, so either can
answer structural questions.

## Hard Rules

1. **`<name>.scenes.json` is the only structural source.** Never infer structure from the
   `.bundle` binary, and never unpack it to look for entities.
2. **Never read the manifest whole.** A 2135-entity scene is ~4 MB (roughly one million tokens).
   Always run a bounded `jq` query and cap the output.
3. **Absent fields are unknown, not empty.** The current export reports `[]` for `components` and
   `null` for `bounds`, but the schema is additive. Check presence and content with a bounded query
   before concluding a field is unavailable. An absent or empty manifest component list does not
   prove that the loaded entity lacks components. Inspect runtime state before adding or replacing
   components, and use SDK references to interpret any exported component data.
4. **`entityId` and `protocolEntityId` are manifest-scoped, not runtime identities.** They change
   between runs. Never carry them into application code.
5. **`path` is manifest notation, not a runtime lookup key.** The SDK exposes no path-based
   lookup; resolving a path means walking one level at a time.
6. **Editor enforces unique sibling Entity names for its exported assets; global names are not
   unique.** `DefaultMaterial` appeared 1035 times in a single scene. Still require exactly one
   runtime match under the current parent to verify the mapping. Multiple matches violate the
   expected constraint or indicate a mapping mismatch. Unknown external bundles need the same check.
7. **A manifest always pairs with a bundle of the same basename.** Verify `<name>.bundle` and
   `<name>.scenes.json` both exist. When `<name>.provenance.json` is present — the packer names it
   after the bundle, not as a bare `provenance.json` — compare its `bundle.digest.value` /
   `bundle.scenesDigest.value` (sha256) against the files. A sibling `checksums.json` carries the
   same values.
8. **Validate the schema before structural queries.** Require `schemaVersion == "0.1"`,
   `scope == "bundle_scenes"`, and a non-empty `scenes` array. Stop on missing or incompatible
   metadata. Report unavailable entity or hierarchy data instead of treating it as an empty scene.
9. **Select one scene before resolving entities.** Identify it by `sourcePath` and require exactly
   one scene match. A manifest path alone is insufficient across multiple scenes.

## Addressing Model

An entity address is the ordered chain of **child names from the manifest scope Entity**, such
as `Root/BuildingA/Door`. Editor's sibling-name constraint makes this chain unambiguous for exported
assets even though a name may recur in other branches. Establish the runtime Entity scope mapping
before traversal and verify exactly one matching direct child at each level.

Consequences:

- Resolve **per level**, not by passing the whole path to a lookup function.
- An address is only meaningful relative to a selected scene and declared root scope. Always state
  the scene `sourcePath` and root path used for the lookup.
- A name alone is insufficient input. Always pair it with a parent scope, or accept that the
  answer is a candidate set.
- Zero matches and multiple matches are both failures; report them instead of picking one.

## On-Demand Queries

Set the file once. Run these examples in the same Bash session. The wrapper limits each successful
output to 16,000 bytes; if exceeded, narrow the query or paginate before retrying. It reports the
limit instead of printing a truncated JSON document.

```bash
M=/path/to/app/src/main/assets/Room.scenes.json

jq -e '.schemaVersion == "0.1" and .scope == "bundle_scenes"
  and (.scenes | type == "array" and length > 0)' "$M" >/dev/null || {
  printf '%s\n' 'Missing or incompatible scene manifest metadata.' >&2
  exit 1
}

manifest_query() {
  local filter="$1"
  shift
  local LC_ALL=C
  local output
  output="$(jq -c --arg scene "${SCENE:-}" "$@" '
    def selectedScene:
      [.scenes[] | select(.sourcePath == $scene)]
      | if length == 1 then .[0] else error("Scene selection must match exactly once") end;
    def sceneEntities:
      selectedScene.entities
      | if type == "array" then . else error("Entity data unavailable") end;
    '"$filter" "$M")" || return 1
  if [ "${#output}" -gt 16000 ]; then
    printf '%s\n' 'Query output exceeds 16000 bytes; narrow or paginate it.' >&2
    return 1
  fi
  printf '%s\n' "$output"
}
```

Scene inventory and entry scene, with bounded pages and warnings:

```bash
manifest_query '{schemaVersion, scope, detail, activeScenePath,
  sceneCount: (.scenes|length),
  warningCount: ((.warnings // [])|length), warnings: (.warnings // [])[0:5]}' || exit 1
manifest_query '{sceneCount: (.scenes|length), offset: $offset,
  scenes: [.scenes[$offset:($offset + 10)][] |
    {name, sourcePath, runtimeSceneKey, entityCount, rootCount}]}' --argjson offset 0 || exit 1
```

Increase `offset` to read later pages. Select the user-specified scene by setting `SCENE` to its
inventory `sourcePath`. Otherwise use `activeScenePath` when present, then the first scene only
when the entry field is absent. An invalid entry path is a failure; do not silently fall back.

```bash
SCENE="$(jq -er '.activeScenePath // .scenes[0].sourcePath' "$M")" || exit 1
manifest_query 'selectedScene | {name, sourcePath, runtimeSceneKey, entityCount, rootCount}' || exit 1
SCENE_KEY="$(jq -er --arg scene "$SCENE" '
  [.scenes[] | select(.sourcePath == $scene)] |
  if length != 1 then error("Scene selection must match exactly once")
  else .[0].runtimeSceneKey |
    if type == "string" and length > 0 then . else error("Verified runtimeSceneKey required") end
  end' "$M")" || exit 1
```

Locate a direct child inside one parent scope. Exact `parentPath` matching prevents a nested
descendant with the same name from being mistaken for a sibling:

```bash
manifest_query '[sceneEntities[] | select(.name == $name and .parentPath == $parent)
  | {name, path, parentPath, transform}]
  | {scene: $scene, count: length, matches: .[0:10]}' \
  --arg name "Door" --arg parent "Root/BuildingA" || exit 1
```

Check a name across the selected scene to report candidates:

```bash
manifest_query '[sceneEntities[] | select(.name == $name) | {path, parentPath}]
  | {scene: $scene, count: length, sample: .[0:5]}' --arg name "Lamp" || exit 1
```

Extract a subtree, including the root, with depth measured relative to that root. Require the root
to exist exactly once before returning the bounded result:

```bash
manifest_query 'sceneEntities as $entities
  | [$entities[] | select(.path == $root)] as $roots
  | if ($roots|length) != 1 then error("Subtree root must match exactly once")
    else [$entities[] | select(.path == $root or (.path|startswith($root + "/")))
      | select(((.path|split("/")|length) - ($root|split("/")|length)) <= $maxDepth)
      | {path, name, type, transform}]
      | {scene: $scene, count: length, items: .[0:40]}
    end' --arg root "Root/Vegetation" --argjson maxDepth 3 || exit 1
```

Read the selected scene's top-level names, with bounded pages. These are children of the manifest
scope; its parent need not have its own entity or hierarchy record. First obtain the shared
`parentPath` from all top-level entries and verify their paths and count:

```bash
manifest_query 'selectedScene as $scene
  | $scene.hierarchy
  | if type != "array" or length == 0 then error("Top-level hierarchy unavailable") else . end
  | . as $roots | [.[].parentPath] | unique
  | if length != 1 then error("Top-level parent scopes must agree") else .[0] end
  | . as $scope
  | if type != "string" or length == 0 then error("Manifest scope unavailable")
    elif ($roots|length) != $scene.rootCount then error("Top-level count mismatch")
    elif any($roots[]; .path != ($scope + "/" + .name)) then error("Top-level path mismatch")
    else {scene: $scene.sourcePath, manifestScopePath: $scope, rootCount: $scene.rootCount}
    end' || exit 1
```

```bash
manifest_query 'selectedScene.hierarchy
  | if type != "array" then error("Hierarchy data unavailable") else . end
  | {scene: $scene, count: length, offset: $offset,
    roots: [.[$offset:($offset + 20)][] | {name, path, parentPath}]}' \
  --argjson offset 0 || exit 1
```

Collect all bounded pages before comparing the root names and `rootCount`; a partial page cannot
verify the complete root set. Use the verified shared `parentPath` as `selectedManifestScopePath`;
never substitute a fixed `Root` string or the runtime node's current name.
Report unavailable or inconsistent top-level data.

If `jq` is unavailable, use a `node -e` reader that prints only the selected fields. Do not fall
back to opening the file with a general file reader. Apply the same schema checks, unique scene
selection, result limits, and byte budget.

## Mapping a Manifest Path to the Runtime

All bundle model-loading interfaces return the same Entity hierarchy for the same packed model.
Apply this mapping to both `AssetBundle.loadModel(...)` and `loadModelSuspend(...)`, and to any
other bundle model-loading interface supported by the project's SDK. The loading interface does
not change the traversal starting scope. `preloadModel` and `releaseModel` return no Entity.

Editor 6.2.5 / Android SDK BOM 6.2.8 was verified with FootballField (one authored top-level node)
and CubeHierarchyProbe (four authored top-level nodes), each loaded from its own bundle using
`loadModelSuspend`. Those device observations establish the following packed-scene layout:

```text
loadedScene                         SDK return; name corresponds to the requested model name
└─ manifestScopeRoot                unique direct child; name can change
   ├─ CubeHierarchyProbe            authored top-level node, may reuse the outer name
   ├─ BranchA
   ├─ BranchB
   └─ Root                          authored node, distinct from the scope Entity
```

The manifest may begin at `Root/BranchA` without an entity record for `Root`. Never invent a
manifest path for the outer return. `rootCount` describes the scope Entity's top-level children,
not `loadedScene.getChildren().size`. The returned root's Entity name corresponds to the requested
model name; keep using the delivered `runtimeSceneKey` rather than reconstructing it from that name.
Its child is a separate Entity whose default editor name is `root` and can be changed.
`Root` in the recorded manifest paths is an example scope, not a fixed runtime name.

For this verified layout, inspect only the return's direct children: require exactly one child,
then compare its complete direct-child name set and count with the selected manifest's
top-level entries and `rootCount`. Do not match that child's name against `root`, `Root` or the
manifest scope path. Keep the verified manifest scope path separate from its runtime name, so a
rename of this child does not change manifest addressing. Verify subsequent child names per level;
renaming those descendants can invalidate their manifest paths and must fail rather than guess.
Name agreement alone, child order, or a recursive search cannot establish correspondence.
Keep unknown layouts unresolved and report them; two added layers are not a universal SDK guarantee.

Keep `loadedScene` and the verified `manifestScopeRoot` separate. The resolver accepts the latter.
To resolve `Root/BranchA/Nested/Root/LeafCube`, remove only the verified scope prefix and walk
`BranchA → Nested → Root → LeafCube` through direct children.

The following helpers use the verified SDK `Entity.getName()` / `Entity.getChildren()` signatures.
Confirm them through `spatial-sdk-guideline` for the app's SDK version. Inputs must come from a
schema-validated, uniquely selected scene in a verified bundle/manifest pair.

```kotlin
data class VerifiedSceneScope(
    val manifestScopeRoot: Entity,
    val manifestScopePath: String
)

fun verifyLoadedSceneScope(
    loadedScene: Entity,
    manifestScopePath: String,
    expectedRootNames: List<String>,
    expectedRootCount: Int,
    diagnose: (String) -> Unit = {}
): VerifiedSceneScope? {
    fun fail(reason: String): VerifiedSceneScope? {
        diagnose(reason)
        return null
    }
    val path = manifestScopePath.trim('/')
    if (path.isEmpty() || path.split('/').any { it.isEmpty() || it == "." || it == ".." }) {
        return fail("Manifest scope unavailable or invalid")
    }
    if (expectedRootCount < 1 || expectedRootNames.size != expectedRootCount ||
        expectedRootNames.any { it.isEmpty() } ||
        expectedRootNames.distinct().size != expectedRootNames.size) {
        return fail("Manifest top-level data unavailable or inconsistent")
    }
    val children = loadedScene.getChildren()
    if (children.size != 1) {
        return fail("Unknown loaded layout: children=${children.size}, expected=1")
    }
    val scope = children.single()
    val actualRootNames = scope.getChildren().map { it.getName() }
    if (actualRootNames.sorted() != expectedRootNames.sorted()) {
        return fail("Top-level structure mismatch: expectedCount=$expectedRootCount, actualCount=${actualRootNames.size}")
    }
    return VerifiedSceneScope(scope, path)
}

fun resolveFrom(
    manifestScopeRoot: Entity,
    manifestScopePath: String,
    targetPath: String,
    diagnose: (String) -> Unit = {}
): Entity? {
    fun fail(reason: String): Entity? {
        diagnose(reason)
        return null
    }
    val root = manifestScopePath.trim('/')
    val target = targetPath.trim('/')
    if (root.isEmpty() || target.isEmpty()) return fail("Empty scope or target path")
    if (target != root && !target.startsWith("$root/")) {
        return fail("Outside verified scope: scope=$root, target=$target")
    }
    if (target == root) return manifestScopeRoot
    val segments = target.removePrefix("$root/").split('/')
    if (segments.any { it.isEmpty() || it == "." || it == ".." }) {
        return fail("Invalid target path: $target")
    }
    var current = manifestScopeRoot
    var parentPath = root
    for (segment in segments) {
        val matches = current.getChildren().filter { it.getName() == segment }
        if (matches.size != 1) {
            return fail("Entity resolution failed: target=$target, parent=$parentPath, child=$segment, matches=${matches.size}")
        }
        current = matches.single()
        parentPath += "/$segment"
    }
    return current
}
```

Both loading examples use the same helpers. Call from the app's existing loading/lifecycle context;
stop when either helper returns `null`. `selectedTopLevelNames` must include all manifest root
pages, not a capped sample. `selectedManifestScopePath` is the verified shared top-level
`parentPath` obtained above. Prefer the suspend interface in UI loading code:

```kotlin
val loadedScene = bundle.loadModelSuspend(deliveredRuntimeSceneKey)
val mapping = verifyLoadedSceneScope(
    loadedScene, selectedManifestScopePath, selectedTopLevelNames, selectedRootCount
)
val target = mapping?.let {
    resolveFrom(it.manifestScopeRoot, it.manifestScopePath, targetManifestPath)
}
```

For an existing synchronous loading path, use `loadModel`; avoid blocking the UI during loading
and follow the app's SDK threading rules for subsequent Entity access:

```kotlin
val loadedScene = bundle.loadModel(deliveredRuntimeSceneKey)
val mapping = verifyLoadedSceneScope(
    loadedScene, selectedManifestScopePath, selectedTopLevelNames, selectedRootCount
)
val target = mapping?.let {
    resolveFrom(it.manifestScopeRoot, it.manifestScopePath, targetManifestPath)
}
```

Diagnostics are optional and silent by default; both helpers retain nullable results. When
investigating a failure, supply a callback that logs one bounded message with the target and failed
parent/segment or layout check. Resolve during initialization and retain the Entity; avoid
per-frame resolution. Log repeated identical failures only once or with rate limiting. A failed
lookup describes where matching stopped, not why the SDK returned no entity.

Geometry can have material Entity children. CubeHierarchyProbe had 15 authored nodes and 6
`DefaultMaterial` nodes: manifest `entityCount=21`, runtime total 23 including the outer return and
scope Entity. State whether counts include materials and wrappers; never require total runtime count
to equal `entityCount`, or assume a Cube is a leaf. Include exported material entries in structural
comparisons; if comparing authored nodes only, report that separate counting scope explicitly.

Do not substitute `entityId` for traversal, and do not assume a path-string lookup exists because the
manifest uses paths. Verify the child accessor against the project's SDK version through
`spatial-sdk-guideline` before writing code.

## Pairing Manifest Facts with the SDK

The manifest describes **structure only**. Use this table to connect each fact to the SDK surface
that consumes it, then read the owning reference rather than re-deriving the API here.

| Manifest fact                             | Runtime counterpart                                                                                                              | Read more                                         |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `<name>.bundle`                           | `AssetBundle.load("asset://.../<name>.bundle")`; hold it and close it explicitly                                                 | `spatial-sdk-guideline` › resources-loading       |
| `scenes[].runtimeSceneKey`                | Exact `bundle.loadModel(...)` / `loadModelSuspend(...)` argument; preserve case and all path segments                            | `spatial-sdk-guideline` › resources-loading       |
| `scenes[].sourcePath`                     | Authoring file identity; never derive the runtime key from this path or the scene display name                                   | this skill                                        |
| `activeScenePath`                         | Which scene to load first; otherwise use `scenes[0]`                                                                             | this skill                                        |
| `container` (`Stage` / `WindowContainer`) | Container choice and `spaceRequirement`; `Stage` is Full Space only                                                              | `spatial-sdk-guideline` › containers              |
| `rootCount`                               | Top-level count under the verified manifest scope Entity; not the outer return's child count                                     | this skill                                        |
| `path`                                    | Level-by-level `getChildren()` matched on `name`; never a runtime lookup key                                                     | this skill                                        |
| `name`                                    | `Entity.getName()`; Editor enforces unique sibling names; verify one direct-child match per level                                | `spatial-sdk-guideline` › ecs-and-entities        |
| `transform`                               | Local `TransformComponent` on that entity; parent-relative, rotation as a quaternion                                             | `spatial-sdk-guideline` › ecs-and-entities        |
| `active`                                  | Runtime enabled/visibility state for that entity                                                                                 | `spatial-sdk-guideline` › ecs-and-entities        |
| `components`                              | Absent or empty means runtime state is unknown; inspect it first, preserve existing components, and add only what the task needs | `spatial-sdk-guideline` › interaction-hit-testing |
| `resources`                               | When absent or empty, load materials and assets through the bundle; when present, resolve the listed assets first                | `spatial-sdk-guideline` › resources-loading       |
| `entityCount`                             | Manifest entry count; compare only with an explicit material/wrapper counting scope                                              | this skill                                        |

Typical sequence:

1. Load the chosen scene's exact `runtimeSceneKey` and verify its manifest scope Entity.
2. Resolve the target within that verified scope; stop on zero or multiple matches.
3. Inspect the target's runtime components through the owning SDK APIs. A manifest's empty
   `components` list is not evidence for removing, replacing, or recreating a collider.
4. Preserve existing component configuration. Add only missing components required by the requested
   behavior, following `spatial-sdk-guideline` › interaction-hit-testing or physics-collision.

Keep the boundary: this skill reads the handoff, `spatial-sdk-guideline` owns API facts,
`spatial-sdk-scene-builder` owns Kotlin scene edits, and `spatial-app-dev-workflow` owns app
integration. When a needed fact is absent from the manifest, say it is absent and route to runtime
ECS inspection or editor-side authoring — never invent the field.

## What the Current Export Cannot Answer

These limits belong to the current schema, not to the manifest format. Re-check field presence
before treating a row as unavailable; a later export may add it.

| Question                                | When the field is absent                     |
| --------------------------------------- | -------------------------------------------- |
| Which components an entity has          | Editor live query, or runtime ECS inspection |
| Physics / collision / interaction setup | Editor live query, or runtime ECS inspection |
| Material and Shader Graph parameters    | Editor live query, or runtime material APIs  |
| Mesh and texture resources              | Resolve via asset loading at runtime         |
| Entity bounds                           | Compute from runtime components              |

Names that look semantic (`*Light`, `*Collider`) are not evidence: in the current export every entity
reports `type: "Entity"`.

## Verification

Before reporting a resolved entity, confirm all of the following:

1. `<name>.bundle` and `<name>.scenes.json` both exist and share a basename.
2. `sha256` of both matches `<name>.provenance.json` (`bundle.digest`, `bundle.scenesDigest`) or a
   sibling `checksums.json` when either is present.
3. Schema metadata is compatible, the selected `sourcePath` matches exactly one scene, and entry
   selection agrees with what the app actually loads.
4. The manifest scope Entity is verified separately from the outer return, including its
   shared top-level `parentPath`, complete top-level names and `rootCount`. The outer return's
   unique direct child supplies the runtime scope regardless of its name; the resolved chain
   ends at exactly one entity.
   Treat zero or many matches, outside-scope paths and unknown layouts as failures.
5. Missing or empty exported component data is reported as unknown runtime state. Attribute any
   available data to its actual source and verify runtime components before proposing mutations.
6. Count comparisons explicitly include or exclude materials and wrappers; neither `rootCount`
   versus outer child count nor `entityCount` versus runtime total is an equality requirement.

## Related Skills

- `spatial-app-dev-workflow` — owns app integration and the build/APK check.
- `spatial-sdk-guideline` — owns SDK API facts and component contracts.
- `spatial-sdk-scene-builder` — owns Kotlin Entity implementation.
- `spatial-editor` — owns authored scene changes and repackaging.
