# Stage (Immersive Container)

A `Stage` is an unbounded immersive container for spatial content. It is the
right choice when the input or user request implies a boundless scene,
passthrough spatial content, anchors, environment mesh, or a virtual world.

## Hard rules (don't violate)

1. **Use Stage only when the experience is truly immersive or stage-only.**
2. **Do not replace a working windowed module with Stage just because the input contains rich visuals.**
3. **Stage-only APIs must stay inside a Stage-based flow.**
4. **A Stage branch must not emit only a flat Compose page.** `DefaultStage { PicoTheme { StageScreen() } }` whose body is ordinary `Box` / `Column` / `Canvas` is a bug: it looks like a 2D panel, wastes the immersive container, and leaves 3D value unrealized. See "Stage content model" below.

## Three immersion levels

| Stage mode | Background | Typical cue |
|---|---|---|
| `MIXED` | Real world / passthrough behind virtual content | free spatial content in the real room |
| `PROGRESSIVE` | Adjustable blend between real and virtual | explicit immersion control or partial environment replacement |
| `FULL` | Pure virtual environment | fully immersive world, no real-world background |

## Registration

Use `DefaultStage {}` as the root DSL entry:

```kotlin
fun mainApp(scope: SpatialAppScope) =
    with(scope) {
        DefaultStage {
            PicoTheme {
                ImmersiveScene(modifier = Modifier.fillMaxSize())
            }
        }
    }
```

The stage style is declared in the launcher Activity metadata. Keep it aligned
with the selected container mode.

## Opening / closing a secondary stage flow

```kotlin
val nav = LocalSpatialNavigator.current

coroutineScope.launch {
    nav.openStage(
        id = "tutorial",
        style = StageStyle.Mixed,
    )
}
```

Close when the stage flow ends:

```kotlin
coroutineScope.launch { nav.closeStage() }
```

## Manifest metadata

The launcher Activity must carry the stage metadata:

```xml
<meta-data android:name="pico.spatial.stage.id" android:value="MainStage" />
<meta-data android:name="pico.spatial.stage.style" android:value="2" />
<meta-data android:name="pico.spatial.stage.immersion" android:value="50" />
<meta-data android:name="pico.spatial.stage.immersion_min" android:value="0" />
<meta-data android:name="pico.spatial.stage.immersion_max" android:value="100" />
```

For input-driven scaffolding:

- `STAGE_MIXED` → `style=1`, conservative mixed entry
- `STAGE_PROGRESSIVE` → `style=2`, `immersion=50`, `min=0`, `max=100`
- `STAGE_FULL` → `style=3`, `immersion=100`, `min=100`, `max=100`

## Stage content model

Treat a Stage as **Full Space + ECS/SpatialView content**, not a Compose page.
The failure mode to prevent: a Stage entry whose body is ordinary `Box` /
`Column` / `Canvas`, or immersive content (e.g. a radar/sphere) placed inside a
2D WindowContainer content tree so it renders as a flat 2D widget, or Stage
controls (summary / layers / timeline / exit) dropped in as plain Compose
overlays that end up invisible, unclickable, or detached from the 3D scene.

Root cause of that bug: confusing the `Stage` container with a Compose page, and
not modeling Stage as Full Space + ECS. 2D controls inside a Stage must be
attached to an ECS anchor via `AttachmentPanel`, never floated as a bare overlay.

### Every Stage branch must declare a 3D content strategy

Pick exactly one and record it in the handoff / contract:

- **ECS runtime entities** — build the scene in code (models, lights, panels) via
  `SpatialView` + `Entity()` / `Entity.load(...)`.
- **Editor-authored bundle** — load a pre-authored scene bundle with
  `Entity.load(name, AssetBundle.load("asset://...bundle"))`.
- **Explicit fallback** — if no real 3D content exists yet, state the fallback
  explicitly (e.g. "single SpatialModelView placeholder, immersive scene TBD"),
  so a flat page is a declared decision, not an accident.

### 3D content: `SpatialView` hosts the scene

`SpatialView` (`com.pico.spatial.ui.foundation.content`) is the container for 3D
content inside a Stage. Create entities in its `initial` lambda and add them with
`content.addEntity(...)`. There is **no** `scene.createEntity` / `spawnEntity` /
`entity {}` DSL — spawn with the `Entity()` constructor or `Entity.load(...)`,
then attach components via `components.set(...)`.

```kotlin
import com.pico.spatial.core.ecs.Entity
import com.pico.spatial.core.ecs.TransformComponent
import com.pico.spatial.ui.foundation.content.SpatialView

SpatialView(
    modifier = Modifier.fillMaxSize(),
    attachments = {
        // 2D controls attached to ECS anchors (see below)
        AttachmentPanel("summary") { SummaryPanel() }
        AttachmentPanel("timeline") { TimelinePanel() }
        AttachmentPanel("exit") { ExitButton() }
    },
) { content, attachments ->
    // ECS root entity; spatial children attach under it
    val root = Entity()
    content.addEntity(root)

    val model = Entity.load("radar", AssetBundle.load("asset://radar.bundle"))
    root.addChild(model)

    // position each attached 2D panel in meters, relative to the anchor
    attachments.entity("summary")?.apply {
        components[TransformComponent::class.java]?.setPosition(0f, 0.2f, -1.2f)
        root.addChild(this)
    }
}
```

### 2D UI in a Stage: `AttachmentPanel` on an ECS anchor

`AttachmentPanel(id) { ... }` is a DSL member of the `attachments { }` builder on
`SpatialView` — it is **not** a standalone composable and **not** a Compose
overlay. Each panel becomes an ECS entity; retrieve it with
`attachments.entity(id)`, give it a `TransformComponent` position **in meters**,
and parent it under your anchor/root with `addChild(...)`. Always state, per
panel, the anchor it attaches to and its metric position.

### Spatial objects: required ECS components

3D objects that should render and be interactable need the right components (all
in `com.pico.spatial.core.ecs`), added via `components.set(...)`. Mind the
dependency chain:

| Component | Purpose | Requires |
|---|---|---|
| `ModelComponent` | mesh + material to render | — |
| `TransformComponent` | position / rotation / scale (meters) | — |
| `CollisionComponent` | collider for hit-testing | — |
| `InteractableComponent` | pointer/gesture target | `CollisionComponent` |
| `HoverEffectComponent` | hover visual feedback | `CollisionComponent` + `InteractableComponent` |

### Reference sample

`SpatialAppSample/stagerendering/.../content/MainScene.kt` mixes `Entity.load`
3D models with several `AttachmentPanel` glass panels positioned in 3D;
`.../content/ControlPanel.kt` shows the stage-switch / exit controls.

For ECS details see `spatial-pack-3d.md`. For anchors see `spatial-anchor.md`.

## What to say explicitly in the handoff

Because a 2D reference under-specifies immersive behavior, always state:

- the chosen 3D content strategy (ECS runtime entities / editor-authored bundle / explicit fallback)
- for each 2D control: the `AttachmentPanel` anchor it attaches to and its metric position
- whether passthrough / environment / immersion level was inferred
- whether stage overlays are mocked or simplified
- whether anchors or environment-mesh behavior still require a real device

## When NOT to use Stage

- A simple 2D panel app → `WindowContainer · ON_PLAIN`
- Multiple apps need to coexist on screen → `WindowContainer`
- You don't need anchors / env mesh / ray casting / global skybox

If the input is basically a flat settings, dashboard, chat, or file panel,
`Stage` is usually the wrong choice.
