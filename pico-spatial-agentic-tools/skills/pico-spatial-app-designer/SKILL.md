---
name: pico-spatial-app-designer
description: Use when the user asks to design, review, repair, or produce a PICO spatial app design package from requirements, prior design facts, or delivery specs, or when an upstream app-generation workflow needs a no-visual requirement converted into an accepted design package before code generation. NOT for generating Android runtime code, scaffolding projects, or device validation.
license: 'Apache-2.0'
---

# PICO Spatial App Designer

Produce an accepted design package before App implementation. Run the six stages below in order for the requested design package. When invoked by a managed design Handoff, stay inside that Handoff and follow its supplied receipt contract. Otherwise return the actual design artifacts and verification to the caller without inventing a Workflow receipt. Preserve the original request and intent brief scope; record decisions and review outcomes in design-doc.md. Stage instructions live here; design/ contains supporting guides, component references, examples and scripts.

## When to Use

- Designing a PICO spatial app UI from a text intent or product description
- Producing design-spec.json, preview.html, and design-doc.md for app generation
- Reviewing or repairing an existing design package before implementation

## 1. Frame

Identify the user's core task, usage context, and spatial value. Read [Content Form and Container Selection](design/container-selection.md) to determine the content form, the primary role of 2D or 3D, and the appropriate container.

Infer a suitable direction from the available context. Ask only when a critical ambiguity prevents a reasonable decision.

Record the decision and rationale using the guide's Frame output template, then continue to Explore for pages, layouts, and functional relationships.

## 2. Explore

Based on the requirements and Frame's decisions, determine the 2D pages, panels, 3D objects, and environment resources needed. Define their content, dimensions, layouts, and relationships as the basis for Plan's interface and scene production.

Actively consider TabBar for a small set of stable main destinations and Toolbar for related operations on the current content, selection, page task or ongoing session. Include their intended destinations or operations and affected content in the corresponding page and layout descriptions.

### References

Read the relevant guides for the actual scenario. Combine them as needed and use the applicable sections.

| Guide                                     | When to Read                                                                                             |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| [layout-2d.md](design/layout-2d.md)       | When designing the dimensions and internal layout of 2D pages or panels.                                 |
| [layout-mixed.md](design/layout-mixed.md) | When a page includes models, a Volume is used, or models and 2D interfaces need to be arranged together. |
| [layout-stage.md](design/layout-stage.md) | When using Stage to determine scene resources, placement in the environment, and viewing arrangements.   |

### Output

Record the following in the existing design record:

- **2D content:** Pages, panels, and action regions, including their actual content, dimensions, and main layout regions.
- **3D content:** Required models and environment resources, including quantities, appearance references, dimensions or presentation scale, units, placement references, positions, orientations, grouping, and required changes or operations.
- **Relationships:** Necessary page navigation, opening and closing behavior, 2D/3D control or state updates, and state retention.

Keep primary content visible as the task requires. Supporting information may open on demand and remain visible; short tasks or confirmations may appear temporarily. Do not add pages, supporting panels, or interactions merely to fill out the design. Use tables and sketches where useful.

### Handoff to Plan

Explore establishes page structure, content and functional relationships. Plan selects and configures components, including the controls within any chosen TabBar and Toolbar, typography, icons, exact padding and spacing, and implementation details, then arranges validation. Plan uses existing resources or placeholders and records creation/modification requirements. Compose App executes the existing Spatial Editor workflow for pending 3D resources. Explore does not produce scenes.

## 3. Plan

Develop the layout selected in Explore into a concrete design. Start with [design-reference](design/design-reference/README.md) and [general rules](design/design-reference/general-rules.md), then read each selected component's README and open its linked Preview in a browser. Inspect the relevant complete compositions and exercise their interactions before composing the application; README text alone is not sufficient. Read the example markup and styles to identify slots, built-in insets and explicit overrides. Follow the reference's [visual resource guidance](design/design-reference/README.md#visual-resources-and-examples) and [icon guide](design/design-reference/assets/icons/README.md). Define composition, visual properties, states and interactions. Distinguish component defaults from explicit design overrides.

Actively select meaningful icons and prepare 2D visual assets, such as application icons, covers, thumbnails, preview images and illustrations, to suit the product's content. Reuse suitable resources or obtain/create the needed artwork; the absence of user-supplied images is not a reason to default to a text-only design. While authoring Preview, save reusable artwork as application asset files and use the same resources in the design handoff. Follow the [visual asset guide](design/design-reference/runtime/README.md#application-visual-assets).

Copy selected application resources into `<target>/.scratch/assets/` before referencing them, preserving original bytes and formats (including SVG). Reference these delivered files from Preview and Spec; resolve `assets[].src` relative to the Spec. For example, eight SVGs referenced from a local plugin cache displayed correctly on the author's machine but failed admission with `Evidence escapes target`. Copy those originals into the project and update the references. Versioned component documentation/runtime references may remain external; they are not application assets.

For 3D content, reuse suitable existing resources or use simplified placeholders in Preview. Record confirmed appearance, required capabilities, spatial relationships and resource references in `scene-design-notes`. Mark missing resources as `assetStatus: "to-create"`. Plan does not invoke Editor to produce final 3D resources. During Compose App, `to-create` requires creation through the existing Spatial Editor workflow before integrating the resource and implementing its App behavior. Reuse existing resources that satisfy the accepted design; record any required modifications explicitly rather than silently recreating them.

Check the Preview against the agreed layout and spatial relationships. Carry chosen UI values, available application assets and pending 3D creation requirements forward to [Write Spec](#5-write-spec). Clearly identify what Web Preview only approximates.

Give each application element that will be recorded in Spec a stable, unique HTML `id`: meaningful layout groups, components, text and media. Keep IDs when copy or styling changes. Component-generated internals and rendering-only wrappers need no IDs. For example, `<sui-title-bar id="main-titlebar"><div id="header-copy" class="header-copy">…</div></sui-title-bar>` identifies both the component and its caller-owned title/subtitle layout. Do not add a wrapper merely to obtain an ID. Write Spec reuses these IDs; [Consistency Review](#6-consistency-review) uses them to locate the actual elements.

Write these elements directly in static HTML, including initially hidden pages/states. JavaScript may update content, visibility and interactions. For example, six cards created only by JavaScript looked correct in the browser but failed `Preview needs exactly one element with id card-space-painter`. Author the cards in HTML first so both the static checker and browser can find them; HTML strings inside scripts or comments do not count.

For 3D content, read [3D Preview authoring](design/design-reference/3d-preview.md). Preview may use simplified graphics to show model appearance, layout and interactions. Give each model region a stable ID and identify the 3D content it represents, confirmed appearance and required behavior. Reference available resources; explicitly mark resources not yet produced as to be created. Distinguish a placeholder from a simplified representation of approved appearance. Preserve confirmed behavior that Web cannot simulate in `scene-design-notes`; do not turn the placeholder into a final 2D asset. When using AttachmentPanel, show its content and chosen background and describe its spatial relationship to the model. Final 3D resource creation remains in Compose App as specified above.

Inherit the container type and dimensions established in Frame/Explore; do not select them again while composing Preview. Use the matching runtime shell. For Volume, use the `sui-volume` component with explicit width, height and depth in dp. Complete missing dimensions in Plan and synchronize the design record; return any necessary container-type change to the upstream decision.

### Plan deliverables

Deliver Preview, its referenced application assets, design decisions and scene-design-notes when needed. Do not create design-spec.json, an embedded full Spec, or a Spec node graph during Plan. Critique reviews the Preview next; Write Spec produces the formal Spec only after that review passes.

## 4. Critique

Open the running Preview and follow [preview-review.md](design/preview-review.md) to assess its content and layout. Check content against the requirements and Explore records, and use screenshots to inspect the main pages and relevant open or expanded states. For suspected clipping or occlusion, inspect the Preview source and verify through interaction when necessary.

Return to Plan to fix issues, then recheck the affected pages and states. Retain review screenshots, specific findings, and recheck results. Explicitly record unverified items rather than marking them as passed. Proceed to Write Spec after the review passes.

## 5. Write Spec

Follow [spec-writing.md](design/spec-writing.md) to produce `design-spec.json` from the approved Preview implementation. Record the fixed design size, windows, content, layout, explicit component settings, actual assets and essential visible changes so App can reproduce the design. Omitted standard component properties retain the referenced defaults. This stage requires no screenshots, resizing ranges or full business state machine.

From the skill's `design/` directory, run `python3 scripts/check_design_spec.py /path/to/design-spec.json --target /path/to/project --json`. Fix errors, review warnings and complete the guide's manual checks. Correct recording mistakes in Spec; return actual design problems to Plan/Preview, then update the record. Rerun validation after corrections. Record any intentional warning disposition or unresolved issue briefly in the existing design record; unresolved errors must not be marked passed.

Hand the Spec, referenced assets, component-reference version or snapshot, and validation results to [Consistency Review](#6-consistency-review). That stage compares the record with the running Preview. Static validation alone does not establish Preview consistency or native rendering fidelity. Changes to the checked artifacts require the affected checks to be repeated.

For 3D designs, also read the Preview's `script#scene-design-notes` JSON. Preserve every entry on the same-ID Spec node as `designNotes`, and record actionable requirements using the existing node/action fields as described in [the 3D guide](design/design-reference/3d-preview.md). Unsimulated behavior remains part of the design. Resolve conflicts with markup or interaction code instead of silently choosing one source.

## 6. Consistency Review

Compare the validated Spec with the approved Preview. Confirm that components, layout, content, resources and explicit settings are accurately and completely recorded.

Follow the [browser audit instructions](design/spec-writing-reference/README.md#browser-consistency-review) to run [the browser audit](design/scripts/audit-preview.js) from the documented working directory. Exercise the main interactions and check the resulting content and states. Manually review unsupported checks and important design details omitted from Spec.

Correct recording mistakes in Write Spec. Return design or Preview issues to Plan, repeat Critique where needed, then update Spec and recheck the affected content.

Deliver the corresponding Spec, Preview, resources and review results. Record unresolved or unverified items with their impact and follow-up location; do not mark them as passed.

## Delivery and repairs

Before returning the Design receipt, run the same Spec checker on the final files with `--target` set to the application project directory. It uses Node.js for the shared handoff checks: every `nodes[].id` must occur exactly once in static HTML, and every `assets[].src` must resolve to an existing file inside the real project directory, including through symlinks. The checker collects all independent node and resource errors in one report. Fix all reported errors together and rerun before submitting the current Handoff; do not submit a failing package to discover the next error in another Run. Record the command and result in design-doc.md. Recheck after changing any checked file.

Deliver `<target>/.scratch/design-doc.md`, `design-spec.json` and `preview.html`, plus referenced assets and a resolvable reference snapshot. When a parent Workflow requests its existing three-path receipt, return that exact receipt. For dev or direct callers, return these artifact paths, referenced assets, review evidence and unresolved gaps to the actual caller; broader development follows `spatial-app-dev-workflow`. Use write-spec-draft-1. The accepted Spec is the App handoff record; it is produced after Preview, not a mandatory page renderer input. Do not require embedded full-Spec parity or minimum-size variants.

All six stages must complete. Fix recording errors in Spec and rerun checks; fix design issues in Plan/Preview, then update Spec and repeat the affected reviews. Do not claim completion with blocking errors. Record review outcomes, warnings and unverified native requirements in design-doc.md. No Kotlin, scaffolding or device validation belongs in this skill.

Run commands shown in the stage references from the skill's `design/` directory; their relative resource paths are rooted there. Use only design/ for the redesigned flow. The root references/, scripts/ and ICON 7.0 assets support current Figma, Compose and shared style checks; they are not Designer authoring instructions. Do not mix their schemas, component defaults or JSON-first rendering requirements into the new flow. In the standalone UI Workflow, the outer design_review checks completeness. Implementation callers use spatial-design-to-app/references/preview-first-restoration.md and its source/resource gates; Web acceptance does not establish native behavior.
