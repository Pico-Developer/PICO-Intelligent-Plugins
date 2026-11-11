## Pitfalls (do not)

- skip workspace inspection when the user names a module (default to `existing_module`)
- **hand-assemble a project skeleton** — `build.gradle.kts` / `settings.gradle.kts` / `libs.versions.toml` / the wrapper / the base manifest all belong to `pico-cli project create`; authoring them from a template is how a project silently drifts off the CLI baseline
- **repair a broken build foundation by editing Gradle files from memory** — re-create with the CLI or hand off to `spatial-sdk-update`
- jump straight from input to code without extracting facts first
- **silently switch the root container in an existing module** — a container change re-runs the Decide stage, then updates manifest, `Main.kt`, coordinates, ornaments, and runtime launch together
- **invent `multi_window` without disconnected-surface evidence** — no machine gate can catch this
- **use a Stage-only API from a WindowContainer flow**
- **hide architecture-impacting assumptions instead of stating them**
- defer container × feature legality to stage 5 (decide inline in stage 3)
- confuse an overlay with a window — popup menus stay in one panel
- leave root fill implicit or record spacing without an owner
- emit a `STAGE_*` root as a flat Compose page (`Box`/`Column`/`Canvas`), or drop immersive content into a 2D WindowContainer tree
- treat a `DefaultWindowContainer` + secondary `Stage(id=…)` app as a "mixed root" — that is a valid single-root app; only two coexisting _default_ roots are illegal
- carry `TabBar`/`Toolbar`/`Subwindow` into a Stage, or treat `AttachmentPanel` as a window-level ornament; an attachment inside a Volume's `SpatialView` belongs to that bounded scene and does not require a Stage
- migrate a container to fix a compile or visual symptom
- invent SDK names or infer SDK unavailability solely from an inventory omission
- **present the Figma route as executable without checking the `d2c_*` tools first** — the plugin does not provision them; an absent prerequisite means re-route or BLOCKED, never a quietly dropped verify hook
- flatten a mapped `sui-*` component into hand-built Compose primitives during
  `intent_only` conversion
- copy design facts into `design_implementation_map.json` without inspecting the
  finished source; source mappings and evidence must point at the code that
  implements each fact
- over-spatialize a 2D settings UI (most belong in `ON_PLAIN`)
- implement screenshot passthrough, floor/trees/skybox, or system safety lines as app content
- fill Step Output with mechanical PASS — Reflection must cite a real fact or rule
- run the full flow on a small patch; use `incremental_patch`
- emit code before reading `architecture-conventions.md` and `spatial-ui-design-style/SKILL.md`

**Honesty:** A 2D reference under-specifies a spatial app. State explicitly when
passthrough / depth / hover / haptics / gestures were inferred, and flag that
anchors and Full Space behaviors need a device to validate.

**Clarification:** ask the user only when one of these is truly unresolved — no
visual reference is available, target module / output cannot be inferred,
multiple window interpretations are equally plausible and materially change the
app structure, or a package / namespace conflict cannot be resolved safely.
Otherwise proceed with the safest default and state the assumption.
