# TitleBar

The top bar of a window or its current page. At least 96 high, 24dp horizontal padding.

In a SideNavigation layout, each item selects a page with its own TitleBar and body. The TitleBar identifies the current page: update its title and applicable subtitle, actions and search scope when the selected page changes. Keep the application identity in the SideNavigation header. A shared TitleBar implementation may render the selected page's values; it must not keep the previous page's heading while only the body changes.

## Details
- Title `titleLarge` (20/26, 600) in `labelSecondary`. Leading and trailing actions are rows with 8 gaps in `labelPrimary`.
- `TitleAlignment.Center` (default) puts the title after the leading actions with 8dp padding. `CenterInBar` centers it across the whole bar.

## When to use
- **Use for:** naming a window or current page and holding its main actions: back, close, done, more.
- **Don't use for:** section headings inside content, tabs (use `TabBar`), a toolbar of editing tools (use `Toolbar`).
- **Alternatives:** `Toolbar` for tools, `Sheet` which has its own title bar.
- **Do:** one or two actions on each side; use `IconButton` Small for them.
- Keep a long title readable without colliding with actions. This Plan supports a current-page search field in the title region; use the composed example below.

## Web API
- `<sui-title-bar>` attributes: `title`, `alignment` (`center-in-bar`), `width`, `title-color`, `leading-color`, `trailing-color`. Slots: `leading`, `trailing`, default (title).

## Component-only preview

The preview shows four standalone TitleBars: a title-only bar using `center-in-bar`, a title with leading/trailing actions using `center`, title plus subtitle, and title plus SearchField. The latter two use the default `center` alignment. It contains no list, result counter or simulated application page. Search retains the field's own typing/clear behavior; no data filtering is simulated.

All bars retain the 96px minimum height and built-in insets. The first two retain default title weight 600; the last two explicitly apply 700 only to `.primary-title`, leaving the subtitle and SearchField at their own styles. The search composition has an explicit 560px minimum example width and scrolls horizontally inside its preview region on narrow screens, preserving room for the 280px SearchField and actions. This is an example layout choice, not a TitleBar default.

## Plan composition: title, subtitle and page search

Use an optional subtitle to explain the window's purpose or current content scope. Keep that explanation with the primary title rather than as a standalone body row. Section descriptions, empty states and operation instructions stay with their own content or controls. Do not add a subtitle when no explanation is needed, or move it into the body to make room for search. See [content ownership and expression](../../general-rules.md#content-ownership-and-expression) for placement and repetition rules.

Keep a single title region. The primary page title is recommended at weight **700**; the reference default `titleLarge` remains **600**. Apply 700 only to the title, not the whole component or its search field. A subtitle may use bodyMedium (14/18, 500) and labelSecondary. Keep family, size and line height inherited for the primary title.

Choose alignment from the **whole TitleBar composition**, not just whether the title slot contains text:

- A bar containing only a single short plain-text title, with no subtitle, leading/trailing actions or other content, uses Web `alignment="center-in-bar"` / native `TitleAlignment.CenterInBar`.
- A title/subtitle group uses Web `alignment="center"` / native `TitleAlignment.Center`, even when there are no actions. Keep the two lines start-aligned as one readable information group.
- A bar with buttons, search or other content anywhere in it uses Web `alignment="center"` / native `TitleAlignment.Center`. A text title with a leading close/back button therefore uses `Center`.
- Preserve an explicit alignment from an accepted design or authoritative source when it overrides this composition rule. If a title/subtitle group is deliberately centered in the bar, specify the text alignment inside the group as well; `CenterInBar` centers the group, not each line of text automatically.

This is the refactored chain's alignment selection rule, not automatic component behavior. It replaces the previous chain's `CenterInBar` choice for text-only title/subtitle groups. The component default remains `Center`; explicitly set `center-in-bar` for a single short title with no other bar content, and record the chosen alignment in Spec so App implementation restores the same choice instead of inferring it from the previous rule. `Center` is the enum name for the normal title region; it does not mean horizontal centering across the whole bar.

The Web `center-in-bar` title layer has pointer events disabled; do not place a search control there. Keep the title group and interactive current-page search in the normal title slot with `alignment="center"`. Global search across destinations belongs in SideNavigation.

```html
<sui-title-bar>
  <div style="display:flex;align-items:center;gap:16px;width:100%">
    <div style="flex:1;min-width:0">
      <span style="font-weight:700">Library</span>
      <sui-text text="Downloaded books" text-style="bodyMedium"
        color="var(--label-ultradark-alpha)"></sui-text>
    </div>
    <sui-search-field placeholder="Search this library"></sui-search-field>
  </div>
  <sui-icon-button slot="trailing" icon="ic_ellipsis" size="small"
    semantic-label="More library actions"></sui-icon-button>
</sui-title-bar>
```

Use `text-style="bodyMedium"` for a `sui-text` typography role (see Text API); the preview uses that supported attribute. Native primary title uses an explicit `fontWeight = FontWeight.Bold`. Record weight 700 in Spec. Below this bar, normal page content starts with top padding 0 and start/end/bottom 32. Do not apply that body padding to the whole window or sidebar.

## Preview and shared rules

[Open this family’s preview](preview.html) and inspect the composition matching the page you are designing, including its icon actions and slots. For page switching, also open the [SideNavigation Preview](../SideNavigation/preview.html) and exercise **Plan recommendation · sidebar and page**: each selection changes the adjacent page title and content together. Read the example markup/styles as well as this README. The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
