# Restoration Anti-Patterns

Read this reference before writing Compose UI from accepted design evidence.

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
