# Source Build Readiness

Read this after Stage 2 resolves the publish root and before publishing that root to GitHub. The
gate proves that the remote build service can resolve every external Gradle/Maven dependency
without private credentials, internal repositories, a developer's Maven local repository, or
pre-populated machine caches.

## Scope

- Apply this gate to every Android Spatial publish root and every Unity-exported Android Gradle
  repository.
- Apply the same gate to a UE, Godot, or custom-stack publish root when it contains a Gradle build.
  Otherwise keep the requirement to document how the reviewed APK is produced and obtained.
- Repository visibility does not weaken this gate. A private GitHub repository may use the
  read-only VibeLab Deploy Key, but its external build dependencies must still be anonymously
  available from public repositories.
- Project-owned modules and generated artifacts committed inside the publish root are not external
  Maven dependencies. They must use repository-relative paths and must not depend on files elsewhere
  on the developer's machine.

## First-release validation timing

Before first-release `add`, run these checks against the approved working-tree build inputs.
Requirements below that say committed or included in the approved Git commit mean inclusion in the
single combined source/config commit after `add`, not a preliminary commit before it. Validate the
files now; before that commit is pushed, verify every required local module, binary, and prebuilt
runtime asset is tracked in it and preserves the validated build inputs. If build inputs change,
repeat static inspection, package validation, and isolated resolution before source publication.
Existing-app checks continue to use the selected published revision. This timing adjustment does
not weaken the public Maven, credential isolation, supported toolchain, or clean-cache requirements.

## Public source path gate

For a public repository, run the bundled [source path checker](../scripts/Check-VibeLabSourcePaths.py)
against the publish root before staging, then against the exact approved source SHA before every
push. This checks the candidate source and all reachable history of the selected commit separately:

```bash
python3 "<skill-dir>/scripts/Check-VibeLabSourcePaths.py" --project "<publish-root>" --worktree
python3 "<skill-dir>/scripts/Check-VibeLabSourcePaths.py" --project "<publish-root>" --revision "<approved-source-sha>"
```

Require an exit status of 0 at both applicable checkpoints. A clean working tree or final commit
does not clear a finding in a reachable ancestor. Report only the category, repository-relative
file, and commit if present. Stop and reconcile the approved source when a finding is present or
history cannot be inspected. Do not rewrite history or force-push as an automatic recovery.

## Blocking repository contract

Inspect every repository declaration and dependency source reachable from the selected build,
including `settings.gradle`, `settings.gradle.kts`, root and included builds, `buildSrc`,
`build.gradle`, `build.gradle.kts`, version catalogs, and Gradle properties.

Require all of the following:

1. Every external Maven coordinate resolves anonymously from a declared public HTTPS repository.
   Standard declarations such as `google()`, `mavenCentral()`, and `gradlePluginPortal()` are
   acceptable. A custom repository is acceptable only when the required artifacts can actually be
   fetched from it without authentication or private network access.
2. No build file, plugin-management block, dependency-resolution block, init script, or generated
   Gradle file calls `mavenLocal()`. Do not accept it merely because a public repository appears
   later in the repository order.
3. No repository uses `file:`, a developer home directory, an absolute local path, localhost, a
   private network address, an internal-only hostname, or another machine-specific location.
4. No repository requires a username, password, token, HTTP header credential, credential-bearing
   URL, environment-provided secret, or organization-only authentication helper.
5. Every repository-relative local module or binary referenced by the build exists in the publish
   root and is included in the approved Git commit. It must not be resolved from `~/.m2`, another
   Maven local path, an untracked export directory, or an undeclared sibling checkout.

Treat a repository declaration hidden in an included build, convention plugin, generated export, or
subproject exactly like one in the root project. Do not infer compliance from the root
`repositories` block alone.

## Build-tool contract

The final Gradle build must use only the supported Gradle, JDK, and Android SDK toolchain. Inspect
Gradle tasks and plugins, included builds, shell or PowerShell scripts, package manifests, generated
build files, and other commands reachable from the selected release/package task.

Require all of the following:

1. The build does not invoke `node`, `npm`, `npx`, `yarn`, `pnpm`, `bun`, or another undeclared
   build-time tool. Installing one of these tools on the build service is not a valid remediation.
2. Web pages and other content that require Node-based generation are built locally before
   publication. Commit the resulting runtime assets inside the publish root and make Gradle consume
   those files without regenerating them.
3. The committed prebuilt artifacts are sufficient for a clean build. Do not rely on ignored output,
   an untracked sibling directory, a global package cache, or a developer-specific absolute path.
4. The final isolated build succeeds with Node-family executables unavailable. A local build that
   finds Node on the developer's `PATH` does not prove readiness.

## Spatial Editor artifact contract

The remote build service does not support modules that start or require PICO Spatial Editor during
the build. Inspect Gradle tasks, scripts, and generated build files for `pico-cli editor`, Spatial
Editor executables, editor projects, or editor-only generation steps.

When an Android Spatial app consumes Editor-authored content:

1. Package the accepted Editor project locally before publication:

   ```bash
   pico-cli editor pack --project <path-to-project.spatialproject> \
     --target-app-root <publish-root> --bundle-name <name>
   ```

2. Require the successful command result to identify co-located
   `app/src/main/assets/<name>.bundle` and
   `app/src/main/assets/<name>.scenes.json`. Both files must exist, be readable, and be included in
   the approved Git commit.
3. Configure the app module's Gradle `androidResources.noCompress` to include `bundle`. Do not
   rename or compress the bundle to work around this requirement.
4. Make the Gradle build consume the committed pair without invoking Spatial Editor, `editor pack`,
   or an editor-only module.
5. After building the APK, run:

   ```bash
   pico-cli app bundle verify <path-to-built.apk>
   ```

   Require the expected bundle to be present in APK assets with ZIP method 0 (stored). A successful
   Gradle build alone does not prove the bundle is loadable.

6. Keep `<name>.provenance.json` with local delivery evidence outside Android assets. If an older
   pack left a copy beside the bundle, pack reports its path and stops. Move that copy out of
   assets yourself, then pack and rebuild. Check the built APK
   with the [source path checker](../scripts/Check-VibeLabSourcePaths.py):

   ```bash
   python3 "<skill-dir>/scripts/Check-VibeLabSourcePaths.py" --apk "<path-to-built.apk>"
   ```

   Require exit status 0; APK assets must not contain Editor pack provenance or absolute paths
   in Editor scene metadata.

If the current Editor content cannot be prepackaged into this handoff, report an unsupported
build-time Editor dependency and block publication. Do not replace the content with a stale bundle
or omit the module silently.

## Isolated resolution check

Static inspection is necessary but not sufficient. Re-run the platform's maintained package
validation or release build with:

- a newly created temporary `GRADLE_USER_HOME`;
- an empty temporary Maven local directory supplied through `maven.repo.local`;
- no private-repository credential variables or user Gradle init scripts;
- the repository's Gradle wrapper;
- Node-family executables and PICO Spatial Editor unavailable to the build;
- `--no-daemon --refresh-dependencies`.

Apply the `execution-reliability.md` contract loaded in Stage 0 on every platform. A clean build uses
one managed process identity with a 30-minute default overall allowance unless repository evidence
requires a larger bounded value. A shorter observer deadline is `OBSERVER_TIMEOUT`, not a build
failure. Continue only by observing the same owned process; never substitute a cache-warm rerun for
the original empty-cache exit result. Success requires exit zero and terminal success evidence from
that same invocation.

Keep required public build inputs such as `JAVA_HOME`, the Android SDK path, and the approved project
configuration. Do not delete or alter the user's normal Gradle or Maven caches. Do not print the
environment while removing credential inputs.

The check passes only when the selected release/package task succeeds from that isolated state and
all external dependencies resolve through the inspected public repositories. A prior normal build,
an offline build, or an existing APK does not prove readiness. If network availability or repository
behavior prevents a clean resolution, report that readiness is unproven and block publication
instead of treating cached success as evidence.

## Findings and recovery

Report each failure using only the repository-relative file, safe line or block location, and one of
these categories:

- `maven-local`
- `private-or-internal-repository`
- `repository-credentials`
- `machine-local-dependency`
- `unsupported-build-tool`
- `uncommitted-prebuilt-artifact`
- `editor-at-build-time`
- `editor-handoff-incomplete`
- `bundle-compression`
- `public-resolution-unproven`

Never repeat a discovered credential or credential-bearing URL. Do not silently rewrite repository
configuration or vendor a dependency. Obtain approval for the remediation, rerun both static
inspection and isolated resolution, and continue only when the complete gate passes.
