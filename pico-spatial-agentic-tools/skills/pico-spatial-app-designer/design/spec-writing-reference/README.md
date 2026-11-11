# Write Spec reference kit

Use this kit with the [English writing guide](../spec-writing.md).

## Files

- [Blank JSON template](design-spec.template.json): replace placeholders and null dimensions before delivery.
- [Preview](example/preview.html): directly authored with the shared SpatialUI Web library.
- [Paired Spec](example/design-spec.json): records the approved example structure and parameters.
- [Assets](example/assets): three fictional book covers and a local catalog close icon.

The format is `write-spec-draft-1`, the working contract for the redesigned flow. The example does not require a resizing range or a complete state machine.

## What the example does

The main window is a **weekend reading list**, not a settings page. It shows three fictional books with separate covers, authors, categories and short summaries. Collection is a title-bar action.

The 720 × 540 main window starts alone. Selecting a book opens a 360 × 540 Subwindow, 16dp to its right, top-aligned with no additional depth. The list stays visible and keeps its dimensions. Selecting another row updates the same detail window. Closing the detail clears row highlighting and preserves the list. The detail has its own title bar and leading close control.

The detail shows the selected book's identity and full introduction. “Start Preview” changes the detail body to a short local excerpt; “Back to Overview” restores the introduction. “Save List” toggles to “Saved”. These are local session interactions, not a production reading service or persisted library.

## Run

From the parent `refactor skill` directory:

```bash
python3 -m http.server 8766 --bind 127.0.0.1
```

Open [the Preview](http://127.0.0.1:8766/spec-writing-reference/example/preview.html). Use a browser viewport wide enough for both fixed-size windows. The outer stage reserves space for the companion; that reserve is not part of the main window's design.

## Preview-to-Spec mapping

| Preview decision                                           | Spec location                                                              |
| ---------------------------------------------------------- | -------------------------------------------------------------------------- |
| Main window dimensions                                     | `surfaces.main.defaultSize`, `main-window.layout`                          |
| Companion ownership, gap, alignment and initial visibility | `surfaces.detail`                                                          |
| Actual Subwindow component and body                        | `book-detail`, `detail-content`, `detail-body`                             |
| Explicit title/subtitle and Subwindow regions              | TitleBar `props.title-node-id` / `subtitle-node-id`; `book-detail.regions` |
| Title-only weight 700                                      | `main-title` and `detail-heading`, `textStyle.overrides`                   |
| Body padding top 0, other sides 32                         | `body.layout` and `detail-body.layout`                                     |
| List gap 8 versus row internal padding 16                  | `book-list.layout.gapDp` versus each row's `props.content-padding`         |
| Three different 60 × 80 covers                             | `cover-*` nodes and their `assetId`                                        |
| Caller-owned title/author composition                      | `copy-*`, `name-*`, `meta-*` nodes                                         |
| Selected row fill                                          | Row `visualStates.selected` and selection actions                          |
| Detail cover 72 × 96, same asset as selected row           | `detail-cover` binding and book data records                               |
| Detail close Icon resource                                 | `close-icon` node and asset                                                |
| Bottom-right reading action                                | `detail-actions.layout`                                                    |
| Unmodified standard Button visuals                         | Button `props`; no duplicated default styles                               |
| Introduction/excerpt and button text changes               | Selection and reading action descriptions, `dataCases.books`               |

The same stable, unique HTML ID identifies each corresponding application node; Spec reuses that ID. Native window materials are represented semantically; the Web background and glass approximation are not native overrides.

## Reusable artwork example

The covers demonstrate the complete handoff: create the artwork once, use it in Preview, then reference that same file in Spec. The source [slow.svg](example/assets/slow.svg) contains the cover's colors and shapes. It is an image asset, not a monochrome Icon.

Preview references the file from an ordinary image element:

```html
<img id="cover-slow" class="cover" slot="leading" src="assets/slow.svg" alt="Cover of The Unhurried Days" />
```

The following is a focused extract from the paired Spec, not a complete standalone design:

```json
{
  "assets": [
    {
      "id": "slow-cover",
      "kind": "image",
      "src": "assets/slow.svg",
      "purpose": "Cover of The Unhurried Days"
    }
  ],
  "nodes": [
    {
      "id": "cover-slow",
      "kind": "media",
      "assetId": "slow-cover",
      "props": {
        "slot": "leading",
        "fit": "cover",
        "objectPosition": "center"
      },
      "layout": { "mode": "stack", "widthDp": 60, "heightDp": 80 },
      "appearance": { "radiusDp": 6 }
    }
  ]
}
```

The detail uses the same `slow-cover` asset through `selectedBook.coverAssetId`, at 72 × 96. Each use owns its display dimensions and crop; neither expands the SVG's internal drawing into Spec nodes. The close icon remains a separate `kind: "icon"` resource with its catalog identity.

A decorative background follows the same asset/media relationship, with its placement behind content and sizing/crop recorded on the owning composition. The browser's outer gradient and window-glass approximation in this example are not application artwork and should not be exported as background images. No additional decoration is needed to demonstrate the handoff.

## Using the template

Copy the template, replace every placeholder and null dimension, then add surfaces, nodes and actual resources. Paths are relative to the JSON. A file that parses is not necessarily a complete design. Do not introduce a Subwindow or duplicate this page layout unless the task benefits from it.

The example content and cover illustrations were created for this reference. The close icon is copied unchanged from the existing icon catalog; its ID is recorded in the Spec.

## Spec validation

From the parent `refactor skill` directory:

```bash
python3 scripts/check_design_spec.py spec-writing-reference/example/design-spec.json
python3 scripts/check_design_spec.py spec-writing-reference/example/design-spec.json --json
```

The completed example should report zero errors and zero warnings. The blank template intentionally fails until its placeholders, sizes and actual content are supplied. Its title inherits the standard default; the paired example demonstrates the optional title-only weight 700 override. Neither requires an expanded default-style table.

The Spec references the primary title explicitly and names the Subwindow's TitleBar/body and leading close action. These are recording fields, not additional Web attributes or UI changes. See [completion checks](../spec-writing.md#10-completion-checks) for warning handling, optional asset-root resolution and checks that still require author review.

## Verification

Checked JSON parsing, node/action/asset references and local documentation links. Browser checks passed for initial hidden detail, selection, changing books, local sample reading, closing and collection toggling. The companion measured 360 × 540 at a 16px right-hand gap with aligned tops. No page script errors were observed. Native restoration has not been tested.

## Browser consistency review

[Consistency Review](../../SKILL.md#6-consistency-review) uses the independently authored Preview and Spec. The Python checker validates the record; [`audit-preview.js`](../scripts/audit-preview.js) reads the running browser page and compares the supported recorded facts. It does not render from JSON, operate the UI or execute bindings.

Application elements represented by Spec nodes use the same unique HTML `id`. The example's `header-copy` group has its own ID because it owns column layout and a gap. Its parent remains `main-titlebar`, a `sui-title-bar`; the wrapper does not replace the component. Component-generated internals need no application IDs. Surface/action/resource identifiers are not all HTML identifiers. Only this new ID convention is supported.

Serve this directory using the local server above. In the opened example's browser execution context (DevTools or the agent's browser evaluation capability), after components, fonts and images have loaded:

```javascript
await import('../../scripts/audit-preview.js');
const specUrl = new URL('design-spec.json', location.href).href;
const spec = await (await fetch(specUrl)).json();
const initialReport = await auditDesignPreview(spec, {
  specUrl,
  scenario: 'Initial reading list',
  initial: true,
});
console.log(initialReport);
```

`specUrl` is the absolute location of the JSON; assets and reference paths resolve relative to it. Keep Preview and referenced files available from the local server. The audit reads color/type catalogs from `metadata.references`; missing catalogs produce unverified observations for affected properties. It does not authenticate snapshots; run Python validation first. The report identifies the page URL, Spec revision and scenario; rerun it after changes and do not reuse old evidence for new artifacts.

After the agent clicks the first book, run a post-action audit. Expectations come from the Spec/data and state which record justified them:

```javascript
const book = spec.dataCases.books.find((book) => book.id === 'slow');
const selectedReport = await auditDesignPreview(spec, {
  specUrl,
  scenario: 'Selected The Unhurried Days',
  initial: false,
  expectations: {
    'book-detail': { visible: true, source: 'actions.select-slow; surfaces.detail' },
    'detail-name': { content: book.title, source: 'dataCases.books[id=slow].title' },
    'detail-author': {
      content: book.authorAndTag,
      source: 'dataCases.books[id=slow].authorAndTag',
    },
    'detail-cover': { assetId: book.coverAssetId, source: 'dataCases.books[id=slow].coverAssetId' },
    'detail-description': {
      content: book.description,
      source: 'dataCases.books[id=slow].description; actions.select-slow',
    },
    'row-slow': {
      visualState: 'selected',
      source: 'actions.select-slow; nodes[row-slow].visualStates.selected',
    },
  },
});
console.log(selectedReport);
```

This is a partial expectation set, not a complete acceptance report. Supply remaining expectations or manually review remaining observations. `expectations` accepts only existing node IDs with a nonempty `source` and optional `visible`, `content`, `assetId`, `visualState`. Use `visualState: "base"` for the base appearance. Visibility expectations propagate to descendants; child-specific expectations take precedence. The source is a reviewer-provided explanation, not machine-authenticated evidence. Never read the actual UI to manufacture matching expectations.

Use `initial: true` only before interaction, against the initial Spec values. After any operation use `initial: false`: text without an explicit current expectation is reported as an observation requiring review, so an initial label such as “Start Preview” is not incorrectly treated as the expected label while reading. Descriptive bindings are never evaluated. Dynamic resources and visibility also require current expectations or author review.

Review these scenarios: initial list; select a book; select another book; start reading; return to introduction; close details; toggle collection on/off. Confirm changed content and resources, not only selection highlighting. The initial hidden detail has deferred geometry/content observations; inspect it after opening. Keep the viewport wide enough for both fixed windows so browser edge clamping does not change the intended companion placement.

### Supported comparisons and limits

- Node identity/count, registered and initialized components, nearest recorded parent through rendering wrappers, declared slots, TitleBar default-title ownership and declared region containment.
- Recorded fixed width/height, min/max constraints, padding, flex/grid gaps, row/column/grid mode, alignment, grow and overflow configuration. Automatic margins, complex grid relationships and unsupported layout fields remain unverified. Overflow configuration does not prove content accessibility.
- Rendered text (including `sui-text` shadow content), referenced typography size/line height/weight, explicit text overrides and colors. Partial overrides take precedence over token values. Unmodified component defaults are not enumerated.
- Known component readers for Text, ListItem, Button, IconButton, TitleBar, Subwindow, Icon, SideNavigation and SearchField. Internal padding adapters are limited to ListItem, Button, IconButton, TitleBar and Subwindow. Unknown readers/parameters remain unverified. Configuration observations such as Button `size` or outside-click settings do not claim every behavior or default style was exercised.
- Declared fill/foreground, opacity and corner radii on supported targets; selected appearance only with an explicit scenario selection. Color comparison uses the recorded role/token values and byte-normalized RGBA. Geometry allows 1 CSS px rounding; text, resource identity and component names are exact comparisons.
- Images: loaded state, resolved URL, dimensions, fit/crop and corner radius. Icons: rendered catalog ID for embedded library resources, or rendered mask URL for file-backed resources, plus explicit size/tint. The book example's close Icon uses its existing `ICON7-P239` catalog resource in Preview to avoid local-file CSS mask loading, while retaining the identical `assets/close.svg` for handoff. Inline artwork equivalence, resource conversion and image authenticity require separate review.
- Planar/Subwindow fixed dimensions and supported companion relationships. Physical size/depth and 3D placement cannot be established from Web measurements. Visibility means rendered presence, not a clipping/occlusion or visual-quality judgment.
- Events, descriptive bindings, custom `parts`, text behavior and unsupported properties are explicitly listed for author/scenario review. The script cannot discover every omitted node or CSS customization. It does not inspect every default, generate screenshots, resize the design, or validate native App restoration.

Each observation includes node, property, expected/actual values and `match`, `mismatch` or `unverified`. A report with mismatches returns `mismatch`; with outstanding items it returns `needs-review`. Even `checked` describes only reported fields. Preserve raw observations and add manual verification separately. Do not change an unverified result to pass without evidence.

## 3D placeholder example

[Character Preview and Spec](character-example/README.md) demonstrate a simplified 3D character, an explicit glass AttachmentPanel and an unsimulated animation preserved through scene design notes. For authoring instructions during Plan, start with [3D Preview authoring](../design-reference/3d-preview.md).
