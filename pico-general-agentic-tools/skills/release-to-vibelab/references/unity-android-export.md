# Unity PICO XR Android Export

Read this before the Unity branch of Stage 2 runs a full Android Gradle export. It records how to
invoke the bundled export scripts, the required project shape, the output contract, and known
warnings. The scripts live in this Skill's `scripts/` directory and the Editor template in its
`assets/` directory. Resolve the installed directory that contains the orchestration `SKILL.md` as
`$SKILL_DIR`.

Use the existing PICO XR route. Do not switch the project to PICO Spatial or Unity OpenXR.

## Prerequisites

- Install Python 3.9 or newer as `python` on Windows or `python3` on macOS.
- Windows uses the PowerShell launcher; macOS uses the shell launcher.
- Install Unity Android Build Support with Android SDK & NDK Tools and OpenJDK.
- Use the Unity version recorded in `ProjectSettings/ProjectVersion.txt`.

## Windows

1. Run the deterministic preflight:

   ```powershell
   pwsh -File "$SKILL_DIR/scripts/Export-VibeLabAndroid.ps1" `
     -PreflightOnly `
     -TargetRepo C:\path\to\gradle-repository
   ```

2. Close the Unity Editor for this project if preflight reports that it is open. Do not kill
   unrelated Unity processes.
3. Run the complete export:

   ```powershell
   pwsh -File "$SKILL_DIR/scripts/Export-VibeLabAndroid.ps1" `
     -TargetRepo C:\path\to\gradle-repository
   ```

4. Review the generated report and the target repository diff. Do not commit or push unless the user
   explicitly asks.

Use explicit parameters when paths differ:

```powershell
pwsh -File "$SKILL_DIR/scripts/Export-VibeLabAndroid.ps1" `
  -ProjectPath C:\path\to\UnityProject `
  -TargetRepo C:\path\to\GradleRepo `
  -UnityEditorPath C:\path\to\Editor\Unity.exe `
  -PageSizePolicy warn
```

## macOS

Use the shell entry point and pass the target repository:

```bash
bash "$SKILL_DIR/scripts/Export-VibeLabAndroid.sh" \
  --preflight-only \
  --target-repo "/path/to/gradle-repository"
```

Close this project's Unity Editor if preflight reports it is open, then run:

```bash
bash "$SKILL_DIR/scripts/Export-VibeLabAndroid.sh" \
  --target-repo "/path/to/gradle-repository"
```

The script discovers the standard Unity Hub application at
`/Applications/Unity/Hub/Editor/<version>/Unity.app`. Pass `--unity-editor-path` for a custom
installation. `VIBELAB_TARGET_REPO` can replace `--target-repo`.

Use `-ValidateOnly` on Windows or `--validate-only` on macOS to inspect an already processed target
repository without rebuilding.

## Required project shape

- Mode: PICO XR
- Android XR loader: `ByteDance.PICO.XR.PXR_Loader`
- Build backend: IL2CPP
- ABI: `arm64-v8a` only
- Android entry: Activity / `UnityPlayerActivity`
- Minimum SDK: 29 or newer
- Custom keystore: disabled
- At least one enabled build scene

The script reads the Unity version, application ID, SDK levels, tool versions, and loader asset GUID
from the project and selected Unity installation. It does not hard-code project identity or package
versions. The source project may contain unused loader assets, but Android `XRManagerSettings` must
list only the PICO loader.

## Inputs

- Unity project: defaults to the workspace running the orchestration; pass the project path when
  exporting a project elsewhere.
- Target Gradle repository: required through `-TargetRepo`, `--target-repo`, or
  `VIBELAB_TARGET_REPO`.
- Unity Editor: discovered from the version in `ProjectSettings/ProjectVersion.txt` using Unity
  Hub's standard installation path, or supplied explicitly.
- Export report: defaults to `Docs/VibeLab-Android-Gradle-Export-YYYY-MM-DD.md` under the Unity
  project.

The script derives Android SDK, NDK, OpenJDK, Gradle, `zipalign`, and `llvm-readelf` from the
selected Unity Editor. Do not hard-code a separate toolchain.

## VibeLab Method B

Run these steps in order:

1. Export a complete Unity Android Gradle project.
2. Run `:unityLibrary:buildIl2Cpp --rerun`.
3. Run `assembleRelease` and retain the first verification APK.
4. Keep the generated `libil2cpp.so` under `unityLibrary/src/main/jniLibs/arm64-v8a`.
5. Delete `Il2CppOutputProject`, clear `jni.srcDirs`, and disable `buildIl2Cpp`.
6. Run `assembleRelease` again and require `:unityLibrary:buildIl2Cpp SKIPPED`.
7. Prove the two APK ARM64 native inventories are identical.
8. Remove local-only and generated build outputs before repository synchronization.

## Required result

The export must:

- export enabled scenes as an Android Gradle project;
- force a fresh `:unityLibrary:buildIl2Cpp --rerun`;
- build and inspect a release APK before slimming;
- retain prebuilt ARM64 libraries in `jniLibs`;
- remove `Il2CppOutputProject`, clear `jni.srcDirs`, and disable `buildIl2Cpp`;
- build a second release APK and prove `:unityLibrary:buildIl2Cpp SKIPPED`;
- compare both APK native-library names and SHA-256 hashes;
- validate ELF64 AArch64 libraries, zip alignment, and the configured page-size policy;
- generate `.vibelab-prebuilt.json`;
- remove APKs, signing files, local machine properties, and build caches;
- mirror the processed project into the target repository while preserving `.git`;
- verify source and destination file hashes;
- write the export report with the host platform.

## Boundaries

- Require IL2CPP, ARM64 only, PICO Loader on Android, and custom keystore disabled.
- Support Windows and macOS only; reject Linux instead of guessing toolchain paths.
- Treat any package name, scene, Addressables, managed code, or native plugin change as requiring a
  complete rerun.
- Keep `page_size_policy=warn` for the current PICO plugin set unless the deployment target
  explicitly requires 16 KB pages.
- Never claim 16 KB compatibility while any packaged native library has `0x1000` LOAD alignment.
- Never add Git LFS, compress or split `libil2cpp.so`, rewrite `.git`, commit, or push automatically.
- On failure, preserve the temporary workspace and logs for diagnosis. Remove only the temporary
  Unity export entry from the source project.

## Warnings

- Run a full export on each supported host platform before claiming that platform is validated; a
  simulated preflight does not validate Unity or IL2CPP execution.
- Some PICO native plugin versions contain libraries with `0x1000` LOAD alignment. Keep
  `PageSizePolicy=warn` unless the deployment target explicitly requires 16 KB pages.
- Do not describe an export as compatible with 16 KB page devices while any packaged native library
  has alignment below `0x4000`.
- Check generated native library sizes against the hosting provider's file limits. Do not add Git
  LFS or alter binaries unless the repository owner explicitly chooses that policy.
- Unity export can update Addressables content state and generate
  `Assets/AddressableAssetsData/link.xml`; retain legitimate Unity-generated changes.
- Local validation does not replace PICO headset installation, input, tracking, Addressables
  loading, or performance validation.

## Rebuild triggers

Always run the complete workflow after changing any of the following:

- package name or version;
- enabled scenes;
- managed code or stripping settings;
- Addressables content;
- native plugins or PICO SDK;
- graphics or Android player settings;
- Unity Editor, NDK, SDK, Gradle, or AGP version.
