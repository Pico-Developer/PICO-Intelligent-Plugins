## Input type → what to extract

Classify once, then extract the facts in this row. Different inputs justify
different extraction tactics; they all converge on the same decisions.

| input_mode          | Trigger                                                                                        | Extract                                                                                                                                                                                                               | Special handling                                                                                                                                                                                                           |
| ------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `visual_design`     | a Figma URL                                                                                    | frame hierarchy, regions, repeated structures, visible states, window-level candidates (TabBar / Toolbar / Subwindow / modal), design tokens, typography roles, assets and icons, spatial cues                        | Read "Figma inputs" below **first** — the route needs an external MCP this plugin does not ship. Fetch fails but a preview/screenshot exists → re-classify as `visual_reference` and say so. No visual fallback → BLOCKED. |
| `visual_reference`  | screenshot / mockup / UI photo                                                                 | the above, plus: **app-owned bbox** (window size derives from this, _not_ the whole screenshot), panel padding, measured region rects, repeated item sizes and gaps, sidebar / search / chips / tabs / card semantics | Read `./layout-inference.md` first. Never treat passthrough, skybox, floor, scenery, or system safety lines as app content.                                                                                       |
| `product_doc`       | PRD / feature spec                                                                             | user tasks, page inventory, data entities, states and transitions, explicit non-goals                                                                                                                                 | No visual asset and no user-provided design package → **designer gate** first (below).                                                                                                                                     |
| `intent_only`       | one-line ask                                                                                   | app-type candidates, the single core task, implied page count                                                                                                                                                         | No visual asset and no user-provided design package → **designer gate** first (below). "Implement directly" does not skip it.                                                                                              |
| `hybrid`            | more than one of the above                                                                     | per-source facts plus the conflicts between them                                                                                                                                                                      | Resolve to one interpretation via the conflict priority below; never keep parallel truths. Contains Figma → Figma steps. No visual asset at all → designer gate.                                                           |
| `incremental_patch` | user names a file/panel/module, scope ≤ 1–2 regions, root container and window model unchanged | target files, inherited container and window model, regions touched, components and states to add, non-goals                                                                                                          | **Skip the Decide stage** (inherit). Verify with `--profile patch`.                                                                                                                                                        |

Routing tie-breakers:

| User says                                               | Routing             |
| ------------------------------------------------------- | ------------------- |
| "add a search field to `MainPanel.kt` in `myapp`"       | `incremental_patch` |
| "use this Figma to redesign `myapp`'s home page"        | `visual_design`     |
| "use this Figma to add a close button to `DetailPanel`" | `incremental_patch` |

If a patch turns out to require a container or window-model change, stop the
patch path and escalate to the full flow — do not silently rewrite a non-goal.

## Classification decision tree

### 1a. Classify the input

```
Step A — incremental_patch?
  IF user names a specific file/panel/module
     AND scope ≤ 1–2 regions or components
     AND root container and window model unchanged
  THEN input_mode = incremental_patch          → skip to Stage 2

Step B — visual_design?
  IF a Figma URL is present
  THEN input_mode = visual_design              → go to 1b (Figma prerequisite)

Step C — visual_reference?
  IF screenshot / mockup / UI photo is present (no Figma URL)
  THEN input_mode = visual_reference           → go to 1c

Step D — product_doc?
  IF PRD / feature spec, no visual asset
  THEN input_mode = product_doc                → go to 1d (designer gate)

Step E — intent_only?
  IF one-line ask, no visual asset, no doc
  THEN input_mode = intent_only                → go to 1d (designer gate)

Step F — hybrid?
  IF more than one source type
  THEN input_mode = hybrid
  → Resolve using conflict priority; follow whichever sub-route the resolved
    primary belongs to
```

For each, emit **Step Output** with classification, generation mode (`new_project` / `existing_module`), and target directory. Do not proceed until the routing gate holds.
