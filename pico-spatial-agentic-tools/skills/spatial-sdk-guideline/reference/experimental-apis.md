# Experimental API Opt-In

Experimental Spatial SDK APIs have two independent gates. Kotlin source opt-in
only satisfies the compiler; it does not enable the API at runtime.

## Covered annotations

Apply this contract whenever the selected project SDK marks an API with an
experimental opt-in annotation declared by that PICO Spatial SDK version. For
example, current SDKs may declare `@ExperimentalSpatialApi`; other modules and
older or future releases may declare different `Experimental*` markers. Examples
are illustrative, not an exhaustive allowlist.

Inspect the exact symbol and marker declaration in the project's selected SDK
version. Do not infer that an entire feature family is experimental because one
symbol is annotated, and do not rely on a fixed marker-name inventory.

## Required consent

Experimental APIs may change or disappear and prevent publication to the PICO
Store. Explain that impact before enabling one. If the user has not explicitly
accepted the experimental API and publication risk, use a stable alternative or
leave the experimental path inactive.

Once use is authorized, treat the source and runtime opt-ins as one atomic
change. Do not leave active experimental code in the project with only one gate
configured.

## Source gate

Add the annotation required by the exact SDK API, for example:

```kotlin
@OptIn(ExperimentalSpatialApi::class)
fun useExperimentalFeature() {
    // Experimental API call.
}
```

Use the narrowest practical scope. Do not hide the annotation behind a blanket
compiler flag merely to suppress diagnostics.

## Runtime gate

The application module's main `AndroidManifest.xml` must contain this entry
directly under `<application>`:

```xml
<application ...>
    <meta-data
        android:name="pico.spatial.use_experimental_api"
        android:value="1" />
</application>
```

Apply the edit idempotently:

- Add the entry when it is missing.
- Change its value to `1` when it is disabled.
- Preserve a single existing entry whose value is already `1`.
- Do not place it under `<activity>`.
- Do not add a duplicate to override a conflicting declaration.
- If the application module is ambiguous, the manifest is invalid, or multiple
  conflicting entries exist, stop and report the ambiguity instead of guessing.

After both gates are configured, keep targeted error handling for documented
recoverable failures and expected experimental behavior changes. Do not use a
broad catch to conceal programming errors. Try-catch around the API call is not
a substitute for the runtime gate.

## Verification

Before building or delivering an implementation that contains an experimental
opt-in marker, run:

```bash
python3 <spatial-sdk-guideline-skill-dir>/scripts/check_experimental_api_opt_in.py \
  --target <project-root>
```

The checker resolves `Experimental*` markers used by Kotlin `@OptIn` or
`@file:OptIn` (and the other legal use-site targets `@get:`, `@set:`,
`@property:`, `@field:`, `@param:`, `@setparam:`, `@delegate:`, `@receiver:`)
through explicit `com.pico.spatial.*` imports, aliases, fully qualified names,
and PICO Spatial wildcard imports. It also detects module Gradle
`-opt-in=com.pico.spatial...Experimental*` and legacy `-Xopt-in` flags. This
package-aware convention lets newly introduced SDK markers participate without
changing the checker, while similarly named non-PICO annotations do not trigger
it. An unassociated Gradle opt-in is ambiguous and fails closed.

When an opt-in appears in a `com.android.library` module, the checker resolves
the runtime gate on each `com.android.application` module that transitively
depends on that library through `project(":...")` entries. A library opt-in
without any such consuming application module fails closed.

Then build the app and inspect the merged manifest or APK manifest. Confirm that
the effective application entry has exactly one
`pico.spatial.use_experimental_api` value and that it equals `1`. Runtime
verification must exercise the experimental path and check crash logs; a
successful Gradle build alone does not prove that the runtime gate is enabled.
