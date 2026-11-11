---
name: update-pico-unity-sdk
description: Migrates legacy PICO Unity SDKs to com.bytedance.pico.xr. Use when upgrading PICO Integration or PICO OpenXR SDKs, including Unity 6000+ MCP prerequisites.
license: 'Apache-2.0'
---

# Migrate to the Unified PICO XR SDK

The new **PICO XR SDK** (`com.bytedance.pico.xr`) merges the two previous PICO Unity packages into one. It ships **both** backends in a single package — the proprietary PXR loader path and the Unity OpenXR feature path — but renames every package, assembly, and root namespace. This skill drives the migration when a developer is on one of the legacy SDKs.

## When to Invoke

Trigger this skill when the developer:

- Asks to "update / upgrade / migrate" the PICO Unity SDK, or to consolidate the old Integration and OpenXR SDKs onto the new one.
- Has a project that depends on `com.unity.xr.picoxr` or `com.unity.xr.openxr.picoxr` and is adopting `com.bytedance.pico.xr`.
- Reports post-import errors: missing `Unity.XR.PXR` / `Unity.XR.OpenXR.Features.PICOSupport` namespaces, unresolved `Unity.XR.PICO` / `Unity.XR.OpenXRPICO` assembly references, duplicate assemblies/native libs, or XR loader fails to start.

## SDK Identity Map (verified from the packages in this workspace)

|                         | Legacy Integration SDK                                   | Legacy OpenXR SDK                      | **Unified PICO XR SDK**                                                                                                                                                                 |
| ----------------------- | -------------------------------------------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Package name            | `com.unity.xr.picoxr`                                    | `com.unity.xr.openxr.picoxr`           | `com.bytedance.pico.xr`                                                                                                                                                                 |
| Display name            | PICO Integration                                         | PICO OpenXR Plugin                     | PICO XR                                                                                                                                                                                 |
| Example version         | 3.4.0 / 3.2.0                                            | 1.4.1 / 1.4.0                          | 0.13.1                                                                                                                                                                                  |
| Min Unity               | 2021.3                                                   | 2021.3                                 | **2022.3**                                                                                                                                                                              |
| Runtime asmdef          | `Unity.XR.PICO`                                          | `Unity.XR.OpenXRPICO`                  | `ByteDance.PICO.XR`                                                                                                                                                                     |
| Root namespace (PXR)    | `Unity.XR.PXR`                                           | —                                      | `ByteDance.PICO.XR`                                                                                                                                                                     |
| Root namespace (OpenXR) | —                                                        | `Unity.XR.OpenXR.Features.PICOSupport` | `ByteDance.PICO.OpenXR`                                                                                                                                                                 |
| Other assemblies        | `Pico.Platform`, `Pico.Spatializer`, `PICOXR.TobSupport` | `PICO.Platform`, etc.                  | `ByteDance.PICO.Platform`, `ByteDance.PICO.Enterprise`, `ByteDance.PICO.XR.Spatializer`, `ByteDance.PICO.Interaction`, `ByteDance.PICO.CameraPack`, `ByteDance.PICO.Spatial.Stage`, ... |

Key point: in the unified SDK **all PICO XR runtime code is gated behind a scripting define**. The PXR loader backend uses `ENABLE_PICO_XR_SDK`; the Unity OpenXR backend uses `ENABLE_PICO_OPENXR_SDK`. **Without the appropriate define, every `PXR_*` type compiles to nothing** — the developer will see hundreds of `CS0103: The name 'PXR_MixedReality' does not exist in the current context` errors. The AI must add the define in Phase B before running the compile check.

### Unity 6000+ AI/MCP package prerequisite

The PICO MCP Extensions package supports Unity `6000.0+` and depends on Unity Assistant. When the selected migration target is Unity `6000.0` or newer, the AI **must ensure both packages resolve before the final compile check**:

| Package                             | Required source                                                                                                                                      |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `com.bytedance.pico.mcp-extensions` | `https://github.com/Pico-Developer/Unity-MCP-Extensions.git#main`                                                                                    |
| `com.unity.ai.assistant`            | A Unity Registry version compatible with the selected Unity 6000 Editor; PICO MCP Extensions `0.1.1` declares a minimum dependency of `2.9.0-pre.2`. |

Rules:

- Do **not** add either package to Unity `2022.3` or earlier projects. Both are Unity 6000+ prerequisites.
- Preserve an existing direct `com.unity.ai.assistant` version when it resolves for the target Editor.
- When no direct Assistant dependency exists, resolve PICO MCP Extensions first, read the Assistant version Unity selected in `packages-lock.json`, then add that resolved version as a direct `manifest.json` dependency and resolve once more. This makes the Assistant installation explicit and reproducible.
- After resolution, verify `packages-lock.json` contains both package identities. Verify the MCP Extensions package's `package.json` name is `com.bytedance.pico.mcp-extensions`.
- Wait for the package-change domain reload before attempting to use any `pico_xr_*` MCP tool. Package resolution alone does not prove that the Unity MCP bridge has rediscovered the extension tools.

### Platform / Framework namespace split (must-know)

The legacy `Pico.Platform` namespace was a single grab-bag. In the unified SDK it is split across several sub-namespaces, so a one-line `using Pico.Platform;` rarely covers everything:

| Legacy `using ...`                                                                                                | Unified replacement(s)                                      |
| ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `using Pico.Platform;`                                                                                            | `using ByteDance.PICO.Platform;` (top-level enums, helpers) |
| (services like `CoreService`, `UserService`, `RoomService`, `MatchmakingService`, `NetworkService`, `IAPService`) | `using ByteDance.PICO.Platform.Service;`                    |
| (`Message`, `Message<T>`, `MessageArray<T>`, `MessageQueue`)                                                      | `using ByteDance.PICO.Platform.Framework;`                  |
| `using Pico.Platform.Models;`                                                                                     | `using ByteDance.PICO.Platform.Models;`                     |
| (CLIB enums like `GameConnectionEvent`, `GameInitializeResult`)                                                   | `using ByteDance.PICO.Platform.CLIB;`                       |

When the developer's code touches any service or `Message<T>`, the AI must add **all** the sub-`using`s in that file, not just rename the top one.

## Auto-detection (the AI does this silently before asking anything)

Do not assume the session's current working directory is the Unity project root. Before talking to the developer or changing any file, the AI must:

1. Resolve the absolute project root from the caller or Host-provided `PROJECT_ROOT`. If it is unavailable, use a project path supplied by the developer or Host as the candidate; only as a fallback, walk upward from the session cwd to locate a candidate. Never use the cwd itself merely because this skill is installed under `<project>/.trae/skills/`.
2. Canonicalize and validate `$PROJECT_ROOT`. It must be the unique directory whose `Assets/` is a directory, whose `Packages/manifest.json` is a regular file containing valid JSON with a top-level `dependencies` object, and whose `ProjectSettings/ProjectVersion.txt` is a regular file containing `m_EditorVersion`. If no candidate or more than one candidate remains, stop without changing files and ask the developer for the absolute Unity project path. Use the validated absolute `$PROJECT_ROOT` for every later read, command, write, deletion, and replacement; before any destructive operation, verify its canonical target remains inside `$PROJECT_ROOT`.
3. Detect the legacy package — check **both** `$PROJECT_ROOT/Packages/manifest.json` **and** any embedded folder under `$PROJECT_ROOT/Packages/`. Legacy SDKs are very often shipped as a sibling folder (e.g. `Packages/PICO Unity Integration SDK-3.0.0-240902/`) whose `package.json` contains `"name": "com.unity.xr.picoxr"`. In that case `manifest.json` will _not_ list the package — Unity auto-resolves embedded packages by folder. Detection rule:
   - Look for `com.unity.xr.picoxr` / `com.unity.xr.openxr.picoxr` as a key in `manifest.json`, **and**
   - Glob `$PROJECT_ROOT/Packages/*/package.json` and read each `"name"` field.
   - Match either `com.unity.xr.picoxr` → backend = **PXR**, or `com.unity.xr.openxr.picoxr` → backend = **OpenXR**.
   - Both present → default to **PXR**, but tell the developer the OpenXR backend stays available behind `ENABLE_PICO_OPENXR_SDK`.
   - Neither → ask the developer to confirm this is actually a PICO project before proceeding.
4. Run `unity projects info` against the validated `$PROJECT_ROOT` to read the project's current Editor version (used to validate the Q1 answer below).
5. When the chosen Editor is Unity `6000.0+`, inspect `$PROJECT_ROOT/Packages/manifest.json` and `$PROJECT_ROOT/Packages/packages-lock.json` for `com.bytedance.pico.mcp-extensions` and `com.unity.ai.assistant`. Record whether each is direct, transitive, missing, or version-locked.
6. Grep `$PROJECT_ROOT/Assets/` for `using Unity.XR.PXR;` / `using Unity.XR.OpenXR.Features.PICOSupport;` / `using Pico.Platform` / `using Pico.Platform.Models` and the `PXR_*` / `PICO*ControllerProfile` types so the namespace replacements in Phase B are scoped correctly.
7. Inventory every `*.asmdef` under `$PROJECT_ROOT/Assets/`. Any that reference `Unity.XR.PICO`, `Unity.XR.OpenXRPICO`, `Pico.Platform`, `PICO.Platform`, `Pico.Spatializer`, or `PICOXR.TobSupport` will need their references rewritten in Phase B.

When `$PROJECT_ROOT` is uniquely resolved and validated, the AI does **not** ask the developer to repeat it. If resolution or validation fails, asking for the absolute project path is mandatory; never guess it from the session cwd.

## Interactive Intake (the AI MUST ask these up-front)

Only two questions need a developer answer. Ask both in a single batch when possible. Do not assume defaults; do not start Phase B until both are answered.

### Q1. Unity Editor version

First run `unity editors --installed` to enumerate locally installed Editors, then ask:

> "Which Unity Editor version should the migrated project use?"

- Build the option list dynamically from the `unity editors --installed` output; use the **Version** column for the choices, the **Revision** column for `m_EditorVersionWithRevision`, and the **Status** column to check installation readiness. Mark versions `< 2022.3` as "(below required minimum)" but still list them.
- Add **"Keep current version"** — only valid if the project's current Editor version (from `unity projects info`) is already ≥ 2022.3. If it is < 2022.3, the AI must reject this choice and re-ask.
- Add **"Install a new version"** — if the developer wants something not in the list. Then ask Q1a.

#### Q1a. (Conditional) Which version to install?

> "Type the exact Unity version to install, e.g. `2022.3.62f2` or `6000.0.73f1`."

- The AI then calls `unity install <version> -m android -m android-sdk-ndk-tools -m android-open-jdk --accept-eula` in Phase B.

### Q2. Unified SDK install method

> "How will you supply `com.bytedance.pico.xr`?"

- `Git URL` → ask Q2a.
- `Local disk folder` → ask Q2b.
- `Tarball (.tgz)` → ask Q2c.
- `Embedded in Packages/ already` → ask Q2d (just confirm path).

#### Q2a. Git URL

> "Paste the Git URL, including any `#<tag|branch|commit>` and `?path=<subfolder>` if needed."
> Example: `https://git.example.com/pico/com.bytedance.pico.xr.git#v0.13.1`

#### Q2b. Local disk folder

> "Provide the absolute or project-relative path to the folder containing `package.json`."
> Example: `../PICO Unity SDK`

#### Q2c. Tarball path

> "Provide the path to the `.tgz` file."
> Example: `../Packages/com.bytedance.pico.xr-0.13.1.tgz`

#### Q2d. Embedded path

> "Confirm the embedded folder path under `Packages/` (must match `package.json`'s `name`)."
> Example: `Packages/com.bytedance.pico.xr/`

After both answers are gathered, the AI summarizes the plan ("Will upgrade to Unity X, install new SDK via method Y from Z, replace namespaces, etc."). The summary must display the validated absolute `$PROJECT_ROOT`, every legacy package or shared-module directory planned for recursive deletion, and the `$PROJECT_ROOT/Assets/` files / `.asmdef` files in the batch-replacement scope. Ask for explicit confirmation that these operations should run against that exact project path. Do not touch files until the developer confirms; if later discovery expands the deletion or replacement scope, stop and obtain confirmation again.

## Human vs AI Responsibilities (timeline)

Migration is split across three phases. The AI must follow this order and **must not** jump ahead — XR Plug-in Management settings are configured **after** the code migration, not before.

### Phase A — Before migration (developer)

1. (Recommended) **Back up the project** via Git commit or directory copy. The AI does not block on this, but should remind the developer once at the start.
2. Answer **Q1** (Unity Editor version) and **Q2** (unified SDK install source) when the AI asks.

### Phase B — During migration (AI-automated; developer just waits)

After the path-and-scope confirmation above, the AI executes the following without further interaction unless the deletion or batch-replacement scope changes. See the "Reference: Phase B step details" section below for exact commands and `manifest.json` snippets.

- If the chosen Editor version is not yet installed, run `unity install`.
- **Switch the project's Editor version by patching `ProjectSettings/ProjectVersion.txt` directly**, do **not** run `unity projects upgrade`. The `upgrade` command launches the Editor immediately to perform the upgrade, but at this point the legacy SDK is still in place, the new SDK isn't installed, the scripting define isn't set, and namespaces aren't replaced — opening the Editor here triggers hundreds of compile errors, asset-import failures, and possibly destructive auto-fixes. Instead, write the file in place:

  ```
  m_EditorVersion: <version>
  m_EditorVersionWithRevision: <version> (<revision>)
  ```

  Get `<revision>` from the **Revision** column of the `unity editors --installed` output or from another known-good `ProjectVersion.txt`. The Editor will not be invoked until Phase C, by which time the project is in a clean state.

- **For Unity `6000.0+` only, install the Unity MCP prerequisites before compiling:**

  1. Add or retain the direct `manifest.json` entry:

     ```json
     "com.bytedance.pico.mcp-extensions": "https://github.com/Pico-Developer/Unity-MCP-Extensions.git#main"
     ```

  2. Ensure `com.unity.ai.assistant` is a direct Unity Registry dependency. Reuse its existing version if it resolves. Otherwise first resolve the MCP Extensions dependency, copy the Assistant version selected in `packages-lock.json` into `manifest.json`, then resolve again.
  3. Read back `manifest.json` and `packages-lock.json`. Confirm both packages resolve, the MCP package is Git-sourced from the required URL, and its embedded `package.json` reports `com.bytedance.pico.mcp-extensions`.
  4. Treat this as a package-change reload boundary. Wait for the Unity domain reload to settle before any MCP validation or `pico_xr_*` tool call.

- Remove the legacy SDK:
  - If listed in `manifest.json` → delete the dependency entry.
  - **If embedded as a folder under `Packages/` (the common Integration SDK 3.x layout), delete the confirmed folder recursively.** Resolve it to an absolute canonical path, verify it is inside `$PROJECT_ROOT/Packages/`, and match its `package.json` name to the detected legacy package before deletion. On Windows the folder name often contains spaces (`PICO Unity Integration SDK-3.0.0-240902`); use a PowerShell script file driven by `powershell -NoProfile -ExecutionPolicy Bypass -File <path>.ps1` calling `Remove-Item -LiteralPath '<full path>' -Recurse -Force`. Inline `powershell -Command "..."` invocations through this skill's `Bash` tool can silently echo without executing — always read back the directory after deletion to **verify it is gone**, and re-run the script-file approach if it is not.
  - Also delete only the confirmed leftover folders / shared modules under `$PROJECT_ROOT/Assets/` and `$PROJECT_ROOT/Packages/` (`Pico.Platform` / `PICO.Platform`, `Pico.Spatializer`, `PICOXR.TobSupport`, old Enterprise native libs). If an additional candidate is discovered after confirmation, stop and add its absolute path to a new confirmation instead of deleting it immediately.
- Install the unified SDK using whichever of the four methods Q2 returned. Verify by reading back `manifest.json` and confirming the path/URL/name is correct.
- **Add the backend scripting define to `ProjectSettings/ProjectSettings.asset`** under `scriptingDefineSymbols`. PXR backend → append `;ENABLE_PICO_XR_SDK` to both the `Android:` and `Standalone:` lines. OpenXR backend → append `;ENABLE_PICO_OPENXR_SDK`. Without this step the compile check below will fail with `CS0103` for every `PXR_*` type even though the SDK is installed.
- Batch-replace namespaces in `Assets/`:
  - `using Unity.XR.PXR;` → `using ByteDance.PICO.XR;`
  - For OpenXR backend: `using Unity.XR.OpenXR.Features.PICOSupport;` → `using ByteDance.PICO.OpenXR;` (interaction types live under `ByteDance.PICO.OpenXR.Interactions`).
  - `using Pico.Platform.Models;` → `using ByteDance.PICO.Platform.Models;` (do this **before** the `Pico.Platform` substitution, otherwise the regex will swallow the `.Models` suffix).
  - `using Pico.Platform;` → `using ByteDance.PICO.Platform;`
  - For any file that uses services / `Message<T>` / CLIB enums, also add the extra sub-namespace `using` lines listed in the "Platform / Framework namespace split" table above.
  - Use a PowerShell script file (Get-ChildItem + ReadAllText/WriteAllText with UTF-8 BOM preserving) to do the rewrite — multi-line PowerShell pipelines piped via `powershell -Command` lose `$` variables in some shell wrappers.
- Repoint custom `.asmdef` references found in step 4 of auto-detection: `Unity.XR.PICO` → `ByteDance.PICO.XR`; `Unity.XR.OpenXRPICO` → `ByteDance.PICO.OpenXR`; `Pico.Platform` / `PICO.Platform` → `ByteDance.PICO.Platform`; `Pico.Spatializer` → `ByteDance.PICO.XR.Spatializer`; `PICOXR.TobSupport` → drop (folded into `ByteDance.PICO.Enterprise`).
- Replace deprecated/renamed APIs per the official changelog.
- Compile-check via `unity run . --editor-version <version> -- -batchmode -nographics -quit -logFile <path>`. The `-batchmode -nographics -quit` combo runs script compilation **without** opening the GUI Editor — this is the only Editor invocation allowed in Phase B; never use `unity open` or `unity projects upgrade` (both of which spawn the interactive Editor) until Phase C. `Grep` the log for `error CS|Aborting batchmode|compilation time` to confirm 0 errors **before** handing back. Iterate: each pass typically uncovers 1–2 missing sub-namespaces (Platform.Service, Platform.Framework, Platform.CLIB) and the define omission. Keep iterating until the log shows `compilation time: ...s` followed by no errors.
- At the end, hand the project back and tell the developer to perform Phase C.

### Phase C — After migration (developer; do these only after Phase B compiles clean)

> Doing these earlier is wasted effort because Phase B may rewrite settings.

1. Open the project in Unity. Go to **Project Settings → XR Plug-in Management → Android**:
   - PXR backend: enable the **PICO** provider.
   - OpenXR backend: confirm `ENABLE_PICO_OPENXR_SDK` is in the scripting define symbols (the AI added it in Phase B), enable **OpenXR**, then enable the **PICO XR Support** feature group and required features/controller profiles.
2. Run **Project Validation** and click **Fix** on each item.
3. Re-enter the **PICO Platform App ID** and any other private settings (the AI never fills credentials).
4. Build to a PICO device and smoke-test: tracking, controllers/hands, passthrough/MR, Platform/Enterprise calls.

For Unity `6000.0+`, also confirm **Edit → Project Settings → AI → Unity MCP** is Running and exposes the PICO MCP Extensions tools after the domain reload. If the tools are absent, restart the AI client before attempting building-block automation.

When the AI starts the skill, it should explicitly tell the developer: "Phase A — answer two questions; Phase B — I will handle automatically; Phase C — you will do XR settings, App ID, and device verification at the end." This prevents the developer from prematurely opening the XR Plug-in Management panel.

## Reference: Phase B step details

### Unity CLI commands

- `unity editors --installed` — list installed Editor versions with their Revision and Status (used in Q1).
- `unity install <version> [-m <module>...] --accept-eula` — install a missing Editor + Android modules.
- `unity projects info` — show the project's current Editor version (used in auto-detection).
- **Do NOT use `unity projects upgrade` in Phase B.** That command immediately launches the interactive Editor against a still-broken project and produces noisy errors / dialogs / asset reimports. Patch `ProjectSettings/ProjectVersion.txt` directly (see Phase B) so the Editor is only opened later in Phase C, when the project is clean.
- `unity projects require` — assert the required version is installed (auto-installs if missing).
- `unity build [project] --target Android --execute-method <Type>.<Method>` — full-build path; both `--target` and `--execute-method` are required, so prefer `unity run` for a pure compile check.
- `unity run "$PROJECT_ROOT" --editor-version <version> --timeout <s> -- -batchmode -nographics -quit -logFile <path>` — recommended **compile-only verification** path. Spawns the Editor in headless batch mode, no GUI window. Always pass the validated absolute project root rather than `.` or another cwd-relative path. Anything after `--` is forwarded to the Editor.
- `unity open [project] --editor-version <version>` — launch the **interactive** Editor. **Phase C only.** Never call this from Phase B.
- `unity request` — send commands to a running Editor instance (use only when a specific automation case calls for it; do not assume it can replace the GUI steps in Phase C).

### Installing `com.bytedance.pico.xr` — four supported methods

After install, let Unity resolve dependencies (`com.unity.xr.management`, `com.unity.xr.interaction.toolkit`, `com.unity.xr.core-utils`, `com.unity.ugui`, `com.unity.textmeshpro`, plus `com.unity.xr.openxr` if the OpenXR backend is enabled). The AI should verify by reading back `manifest.json` and confirming the package resolves on next compile.

#### Method A — Git URL

Add to `Packages/manifest.json`:

```json
{
  "dependencies": {
    "com.bytedance.pico.xr": "https://git.example.com/pico/com.bytedance.pico.xr.git#v0.13.1"
  }
}
```

- Append `#<tag|branch|commit>` to pin the version.
- Append `?path=<subfolder>` if the package lives in a sub-directory of the repo (monorepo layout).
- The developer's machine must have `git` on `PATH`; private repos need pre-configured SSH/HTTPS auth.

#### Method B — Local disk folder

Add to `Packages/manifest.json` using the `file:` scheme; path is relative to the `Packages/` folder (or absolute):

```json
{
  "dependencies": {
    "com.bytedance.pico.xr": "file:../../PICO Unity SDK"
  }
}
```

- Useful when the developer keeps the SDK alongside the project.
- Unity treats it as a live mutable package — edits to that folder are reflected immediately.

#### Method C — Tarball (`.tgz`)

Add to `Packages/manifest.json`, again with `file:` plus a relative or absolute path to the tarball:

```json
{
  "dependencies": {
    "com.bytedance.pico.xr": "file:../Packages/com.bytedance.pico.xr-0.13.1.tgz"
  }
}
```

- Recommended for shipping a frozen, version-locked SDK to a team.

#### Method D — Embedded package

Copy the SDK folder into `Packages/` directly:

```
<project>/Packages/com.bytedance.pico.xr/
    package.json
    Runtime/...
    Editor/...
```

- Folder name must match `package.json`'s `"name"` field.
- No `manifest.json` entry is required — Unity auto-detects embedded packages.
- Typical when migrating from `Assets/` placement of the legacy SDK.

## Common Pitfalls

- **Forgetting the scripting define.** This is the #1 source of confusion: SDK installed, namespaces renamed, but compile fails with `CS0103: 'PXR_MixedReality' / 'PXR_System' / 'PXR_Plugin' does not exist`. Cause: `ENABLE_PICO_XR_SDK` (or `ENABLE_PICO_OPENXR_SDK`) missing from `scriptingDefineSymbols` in `ProjectSettings.asset`. Adding it makes hundreds of errors disappear at once.
- **Embedded legacy SDK not removed.** When the old SDK lives as `Packages/PICO Unity Integration SDK-3.x-yymmdd/` (not in `manifest.json`), simply editing `manifest.json` does nothing. The folder must be physically deleted. After deletion, the AI must list `Packages/` again and confirm the folder is gone — Windows path quoting bugs frequently make a delete look successful when it wasn't.
- **`Pico.Platform` only partially renamed.** Renaming the top-level using is not enough. Files using services or `Message<T>` must add `using ByteDance.PICO.Platform.Service;`, `using ByteDance.PICO.Platform.Framework;`, and (for CLIB enums like `GameConnectionEvent`/`GameInitializeResult`) `using ByteDance.PICO.Platform.CLIB;`. See the namespace-split table at the top.
- **Sed-style regex eats `.Models`.** Always replace `using Pico.Platform.Models;` _before_ `using Pico.Platform;`, otherwise a greedy regex on the latter consumes the `.Models` line.
- **`unity projects upgrade` opens the broken project in the GUI Editor.** Calling it during Phase B (when SDK swap / namespace replace / define add are not yet done) launches Unity against a still-broken project, triggering an avalanche of compile errors, popups, and possibly destructive auto-import side effects. **Don't run it.** Set the Editor version by editing `ProjectSettings/ProjectVersion.txt` in place — Unity only reads that file, no Editor launch is needed.
- **`ProjectVersion.txt` mismatch breaks `unity run`.** If the file still pins the old version, `unity run` reports "Editor X.Y.Z is not installed". Either patch the file (preferred) or pass `--editor-version <version>` explicitly to `unity run`.
- **PowerShell silently no-op'ing through `Bash`.** `powershell -Command "..."` from this skill's `Bash` tool may echo the command without executing it (variables get stripped). Use `powershell -NoProfile -ExecutionPolicy Bypass -File <script.ps1>` instead and write the actual PowerShell to a temporary file.
- **Unresolved namespaces** because `using Unity.XR.PXR;` / `using Unity.XR.OpenXR.Features.PICOSupport;` were not updated to the `ByteDance.PICO.*` equivalents.
- **Duplicate assemblies / native libs** when the old package or its shared modules (Platform, Spatializer, Enterprise, TobSupport) weren't fully removed before importing the unified SDK.
- **OpenXR features missing** because `ENABLE_PICO_OPENXR_SDK` isn't defined — the OpenXR backend code is compiled out without it.
- **No XR loader enabled / Unity version too low** — the unified SDK needs Unity 2022.3+ and the PICO (or OpenXR) provider re-enabled in XR Plug-in Management.
- **Missing Unity 6000 MCP prerequisites** — PICO XR can compile while `com.bytedance.pico.mcp-extensions` or `com.unity.ai.assistant` is absent, but PICO MCP tools will not become available. For Unity `6000.0+`, install and resolve both packages before declaring the migration complete.
- **Touching XR Plug-in Management before Phase B finishes** — Phase B may rewrite settings; configure it only in Phase C.
- **Silently switching backends** (PXR ↔ OpenXR) — different namespaces and components; do not switch unless the developer explicitly asked, and treat it as an intentional rewrite.

## Deprecated / changed PICO APIs (sanity-check after namespace replace)

Many `PXR_Input`, `PXR_MotionTracking`, `PXR_System`, `PXR_Boundary`, `PXR_FoveationRendering` members were deprecated/removed/renamed in recent versions:

- Many haptics / face APIs are deprecated.
- Body Tracking and Motion Tracker callbacks were renamed (e.g. `MotionTrackerConnectionAction`, `MotionTrackerPowerKeyAction`, `RequestMotionTrackerCompleteAction` replaced older equivalents).
- `Action<int> SessionStateChanged` became `Action<XrSessionState> SessionStateChanged`.

Cross-check against the official changelog (https://developer.picoxr.com/document/updates-unity/) for the exact starting and target versions before applying replacements.

## References

- Documentation: https://developer.picoxr.com/document/unity/
- Changelog / updates: https://developer.picoxr.com/document/updates-unity/
- Always verify the exact unified-package version, install source, and loader steps against the build the developer actually installs.
