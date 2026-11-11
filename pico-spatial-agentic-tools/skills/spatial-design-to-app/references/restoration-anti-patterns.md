# Restoration Anti-Patterns

Read this reference before writing Compose UI from accepted design evidence.

## Button used as a content container

`Button` represents a concise command. Do not use it as the outer shell for a
card, catalog tile, metadata group, or read-only detail panel merely to obtain
hover, click, background, selected, or disabled styling. A `Button` may compose
a compact command label, optional icons, and loading state; rich heterogeneous
content belongs to an item or layout component. Generated two-line explanatory
commands are not an exception. Recognized container misuse fails the scanner;
comments cannot suppress it. Do not extract rich content into helpers to evade
the rule. Focus, hover, and click needs do not justify a Button shell.

```kotlin
// Wrong: a rich selectable item becomes one oversized command button.
Button(
    onClick = onSelect,
    modifier = Modifier.height(150.dp),
) {
    Column {
        Icon(painter = appIcon, contentDescription = null)
        Text(app.title)
        Text(app.release)
        Text(app.metadata)
    }
}

// Wrong: disabled Button styling is used as a read-only surface.
Button(
    onClick = {},
    enabled = false,
) {
    Column {
        AppDescription()
        CompatibilityMetadata()
    }
}

// Correct for a standard actionable information row.
ListItem(
    modifier = Modifier.clickable(onClick = onSelect),
    // Preserve the restoration default when the design omits padding.
    padding = PaddingValues(16.dp),
    headlineContent = { Text(app.title) },
    supportingContent = { Text(app.metadata) },
)

// Correct when no built-in matches the accepted rich item layout.
Column(
    modifier = modifier
        .clip(itemShape)
        .spatialHoverEffect()
        .clickable(onClick = onSelect)
        .padding(16.dp),
) {
    AppArtworkAndMetadata()
}

// Correct for a read-only detail region.
Column(modifier = modifier) {
    AppDescription()
    CompatibilityMetadata()
}
```

Prefer the closest semantic SpatialUI component before composing a custom
interactive layout. When a custom layout is necessary, hover and interaction
must share the same hit-target modifier chain.

## Padding a container that owns its decoration

Do not apply content padding to a container that also hosts a full-size
decoration child. Padding reduces the bounds passed to every child, so
`matchParentSize()` matches the inset content area instead of the component's
outer bounds.

```kotlin
// Wrong: padding also shrinks the decoration.
Box(modifier = modifier.padding(12.dp)) {
    DecorationLayer(Modifier.matchParentSize()) // Background, accepted outline, or selection fill.
    Content()
}

// Correct: padding applies only to content.
Box(modifier = modifier) {
    DecorationLayer(Modifier.matchParentSize()) // Covers the full outer bounds.
    Content(Modifier.padding(12.dp))
}
```

## Custom interactive component without spatial hover

Do not restore an app-owned custom composable as an interactive target with
`Modifier.clickable`, `combinedClickable`, `selectable`, or `toggleable`
without applying `Modifier.spatialHoverEffect` before the interaction on the
same hit-target modifier chain.

This requirement still applies when the accepted component is transparent and
has no background or `appearance.fill`. It applies only to app-owned custom
composables, not SpatialUI built-in components.

```kotlin
// Wrong: the custom click target has no spatial pointing feedback.
Column(
    modifier = modifier
        .clickable(onClick = onClick),
) {
    Content()
}

// Correct: hover and click use the same hit-target modifier chain.
Column(
    modifier = modifier
        .spatialHoverEffect()
        .clickable(onClick = onClick),
) {
    Content()
}
```
