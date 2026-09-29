---
name: pico-unity-init
description: >-
  One-time PICO Unity project initialization wizard. Manual trigger only: use
  it only when the developer explicitly invokes `/pico-unity-init`; do not
  activate it passively or automatically for setup or development requests. On
  invocation, inspect `.pico-cli/config.json`: when
  `pico_unity_init_completed` is `true`, skip initialization and report that it
  has already run; when the field is absent or not `true`, run the initialization
  once. Empty projects select and copy a PICOXR, OpenXR, or PICOSpatial template;
  valid existing Unity projects receive incremental package setup. Record the selected
  development `mode` as `picoxr`, `openxr`, or `picospatial`, prepare Android,
  open the project, and set the completion marker only after success.
license: 'Apache-2.0'
---

# pico-unity-init

PICO Unity project one-time initialization wizard. Run this skill only after the developer explicitly invokes `/pico-unity-init`. Passive or automatic activation is forbidden, even when a request describes project initialization, project creation, or PICO SDK setup. Once invoked, the value of `pico_unity_init_completed` in `.pico-cli/config.json` is the sole completion signal. The existence of the file by itself is not a completion signal. This skill has no reset or post-init repair mode.

## Pre-trigger check (GUARDRAIL)

1. Confirm the current working project path (hereafter `$PROJECT_ROOT`). The project name `project_name` is the directory name (basename) of `$PROJECT_ROOT`; there is no need to ask the developer.
2. If `$PROJECT_ROOT/.pico-cli/config.json` exists, parse it before doing anything else. Do not decide from file existence alone:
   - **`pico_unity_init_completed` is exactly `true`** → stop immediately without asking questions, changing files, installing packages, or opening Unity. Reply exactly: `已使用过/pico-unity-init`. Do not delete `.pico-cli/config.json` for an SDK refresh or repair, and do not tell the developer to delete it. Route post-init package changes to `pico-unity-package-manager`, which uses `pico_xr_package` after the Unity Editor and MCP bridge are running. If the bridge is unavailable, ask the developer to restore the Editor/MCP connection first; do not fall back to rerunning initialization or editing `Packages/manifest.json`. A full project reset is a separate destructive workflow outside this skill and requires explicit authorization plus a backup.
   - **The field is absent or not `true`** → initialization has not completed under this contract. Because the developer explicitly invoked `/pico-unity-init`, continue with the initialization flow below. Preserve unrelated existing config fields when writing the final config.
   - **The file is malformed JSON** → stop and report the parse error. Do not overwrite it or treat it as an uninitialized project.
3. If `$PROJECT_ROOT/.pico-cli/config.json` does not exist, continue the explicitly invoked initialization flow below.

> This skill is executed by the **local agent running on the developer's own machine**. All file reads/writes and command execution act directly on the **developer's local project directory**. Always use the local shell (local `bash`) and local file operations directly; no remote sandbox is involved, and there is no need to go through proxy tools such as `mira_local_*`.

## Initialization flow overview

**Emptiness check first → branch handling**:

- **Valid existing Unity project** (Stage B): do not copy a template; directly **incrementally install the 3 packages** (AI Assistant / Unity MCP Extensions / PICO Unity SDK XR), skipping or upgrading based on existing dependency state.
- **Empty project** (Stage C → D): preferentially sparse-clone the corresponding template subdirectory (`PICOSpatial` / `PICOXR` / `OpenXR`) from `Pico-Developer/PICO-Unity-Project-Templates` (GitHub) into `$PROJECT_ROOT`; fall back to `pico-cli project create` on failure. Then modify `productName` / `ProjectVersion.txt`, and install the 3 packages.
- **Incomplete or invalid Unity project layout**: report every missing, wrong-type, or invalid core path and stop before collecting preferences or changing the project. Do not treat it as an empty project and do not attempt automatic repair.

**Shared wrap-up**: both branches finally open the project with `unity open ... --build-target Android`, letting Unity switch the Active Build Target to Android during startup (equivalent to the official Editor launch argument `-buildTarget Android`) — no need to switch manually after opening, and no dependency on MCP tools.

---

### Stage A — Read-only probing (do not ask the developer; run first)

Before popping up any form, complete the following read-only probing (shared by all branches):

1. **Classify the core Unity layout** (highest priority) using these three paths and expected types:

   - `$PROJECT_ROOT/Assets/` must be a directory.
   - `$PROJECT_ROOT/Packages/manifest.json` must be a regular file.
   - `$PROJECT_ROOT/ProjectSettings/ProjectVersion.txt` must be a regular file.

   Classify the project without changing it:

   - All three core paths are missing → **empty project**. Continue to Stage C → D. Other files such as `.git/`, `.gitignore`, or `README.md` do not make the directory an existing Unity project.
   - All three core paths have the expected types → **candidate existing Unity project**. Continue with the metadata validation below.
   - Any other combination, including a core path that exists with the wrong type → **incomplete or invalid Unity project layout**. List every missing or wrong-type core path, then stop. Do not open the form, copy a template, modify any project file, install packages, open Unity, or write `pico_unity_init_completed`. Do not create the missing paths or otherwise attempt automatic repair.

2. **Validate candidate project metadata** before classifying it as a valid existing Unity project:

   - Parse `$PROJECT_ROOT/Packages/manifest.json`. It must be valid JSON with a top-level object and a `dependencies` object.
   - Read `m_EditorVersion` from `$PROJECT_ROOT/ProjectSettings/ProjectVersion.txt`. It must be present and contain a recognizable Unity version with a numeric major version.
   - If either validation fails, classify the project as an **incomplete or invalid Unity project layout**, report the exact file and reason, and stop with the same no-change guarantees as above. Do not overwrite malformed metadata or silently substitute defaults.

3. **Additional reads for valid existing Unity projects**: retain the validated `m_EditorVersion` for the low-version gate in Stage B and the validated `dependencies` for the package checks in Stage B.
4. **Check installed editors** (only needed for empty projects): run `unity editors --installed` to split candidate Unity 6+ LTS versions into "installed / not installed" groups. **For a valid existing Unity project, if Stage B does not change the version, you may skip this step to save time.**

---

## Stage B — Valid existing Unity project branch (runs first; goes straight to incremental installation)

**Enter Stage B only when Stage A confirms that all three core paths have the expected types and both metadata files pass validation. Do not enter this branch merely because one core path exists. Execute B.1 → B.6 in order.**

### B.1 Low-version gate

- **Current version < Unity 6 (major version < 6000)**: ask "The current project's Unity version is `xxx`, which is below Unity 6. Upgrade?"
  - Choose "No" → **exit initialization immediately** (do not write config, do not continue).
  - Choose "Yes" → let the developer select a target Unity 6+ LTS version in the B.2 form.
- **Current version ≥ Unity 6**: ask "The current project's Unity version is `xxx`. Change the version?"
  - Choose "No" → keep the current version as `unity_version`; the B.2 form no longer shows the version selection item.
  - Choose "Yes" → the B.2 form requires selecting a target Unity 6+ LTS version.

### B.2 Minimal form collection (valid existing Unity project)

A valid existing Unity project does not copy a template, but the config still requires one concrete development mode. Reuse a valid existing `mode`, or map a legacy `sdk` value (`picoxr` → `picoxr`, `openxr` → `openxr`, `spatial` → `picospatial`). If neither is available, collect `mode` in the form. The form **collects only necessary preferences**:

| Field           | Control       | Options                           | When shown                                     |
| --------------- | ------------- | --------------------------------- | ---------------------------------------------- |
| `mode`          | Single-select | `picoxr`, `openxr`, `picospatial` | Only when it cannot be reused or migrated      |
| `unity_version` | Single-select | See "Version options" below       | Only when B.1 chose "upgrade / change version" |
| `devices`       | Multi-select  | `pico swan`, `pico 4 ultra`       | Always (**required, at least one**)            |
| `business_type` | Single-select | `Yes`, `No`                       | Always                                         |

> The values and mapping rules for `devices` and `business_type` are the same as in Stage C.

### B.3 Incrementally install the 3 packages (core logic)

Complete the compatibility preflight without modifying `Packages/manifest.json`. Only after every blocking decision is resolved may you build the full dependency change and commit it once. **Preserve all of the developer's other existing dependencies; only make incremental additions/changes.**

> **Why init writes the manifest directly (bounded exception):** `AGENTS.md` and `pico-unity-package-manager` forbid hand-editing `Packages/manifest.json` and require every package change to go through the `pico_xr_package` MCP tool. Initialization is the explicit exception: the Unity Editor is not open yet and the MCP bridge is not running, so `pico_xr_package` is unavailable — and MCP Extensions (which backs that bridge) is itself one of the packages installed here. Direct manifest writes are therefore limited to this bootstrap step. Once init finishes and the Editor/MCP bridge is up, all subsequent package changes must go through `pico_xr_package`.

#### B.3.1 Read-only compatibility preflight

Use the validated dependency snapshot retained by Stage A to determine every package action before writing anything:

1. **AI Assistant (`com.unity.ai.assistant`)**:
   - Not present → plan to add version `2.17.0-pre.1`.
   - Present at another version → plan to upgrade to `2.17.0-pre.1`.
   - Already at `2.17.0-pre.1` → plan no change.
2. **Unity MCP Extensions (`com.bytedance.pico.mcp-extensions`)**:
   - Not present → select the dependency address now: SSH by default; if the developer has not configured a GitHub SSH key, use HTTPS as described in Stage D.4. Plan to add that selected address.
   - Already present and pointing to that repository → plan no change and preserve its existing address and ref.
3. **PICO Unity SDK (XR)**: when `com.bytedance.pico.xr` is present, try to read its version from the git URL `#ref`, then from `Library/PackageCache/com.bytedance.pico.xr@*/package.json`.
   - Not present → plan to add the three SDK dependencies listed in B.3.2.
   - Version ≥ 6.0.0 → plan no change; preserve the existing addresses and refs.
   - Version < 6.0.0 → ask: "The detected PICO Unity SDK (XR) version `xxx` is below 6.0.0. Upgrade to 6.0.0?"
     - Choose "No" → exit initialization immediately. If the developer declines any blocking change, exit with the original manifest unchanged; do not write config or alter any other project file.
     - Choose "Yes" → plan to replace all three SDK dependency keys with the values in B.3.2.
   - Version cannot be determined → plan no change and report: "PICO SDK XR is present but its version is unknown; upgrade skipped. To force a refresh, manually change the `#ref`."

This phase is read-only: do not write AI Assistant or MCP Extensions first and defer the SDK decision.

#### B.3.2 Build one complete dependency delta

Build one complete dependency delta in memory from the original validated manifest and the resolved preflight decisions:

- Set `com.unity.ai.assistant` to `2.17.0-pre.1` only when the preflight planned an add or upgrade.
- Add `com.bytedance.pico.mcp-extensions` with the selected SSH or HTTPS address only when it is missing.
- When the PICO SDK is missing or its confirmed upgrade was accepted, set these three keys together:
  ```json
  "com.bytedance.pico.spatialadapter": "https://github.com/Pico-Developer/PICO-Unity-SDK.git?path=/SpatialAdapter#main",
  "com.bytedance.pico.xr": "https://github.com/Pico-Developer/PICO-Unity-SDK.git?path=/XR#main",
  "com.plattar.unitygltf": "https://github.com/Pico-Developer/gltf-exporter.git?path=package/com.plattar.unitygltf#master"
  ```
- Leave every package whose preflight action was "no change" untouched, including its existing address or ref.

If the resulting dependency object is identical to the original, skip the manifest write.

#### B.3.3 Commit the manifest once

Apply the resolved delta as one atomic manifest update: preserve the original top-level object, replace only its `dependencies` value with the in-memory result, write valid JSON to a temporary sibling file in `$PROJECT_ROOT/Packages/`, parse that staged file to validate it, then atomically replace the original manifest. If staging or validation fails, remove the temporary file, leave the original manifest unchanged, report the error, and stop. Re-read the committed manifest and verify all planned values before continuing to B.4.

### B.4 Sync `ProjectVersion.txt` (only when B.1 chose to change the version)

If B.1 chose "upgrade / change version", set `m_EditorVersion` and `m_EditorVersionWithRevision` in `$PROJECT_ROOT/ProjectSettings/ProjectVersion.txt` to the `unity_version` selected in B.2.

### B.5 Prepare the Unity version

Refer to [references/unity-versions.md](references/unity-versions.md):

- If `unity_version` comes from the "not installed" list → `unity install <unity_version> -m android` (bundle-installs Android Build Support; this takes a while — inform the developer before running).
- If it comes from the "installed" list or you keep the current version → `unity install-modules -e <unity_version> -m android` to confirm Android is installed (check the **Status** column in the output; skip if already installed).

### B.6 Open the project and write the completed config

- Run `unity projects add $PROJECT_ROOT`; then run:
  ```bash
  unity open $PROJECT_ROOT --build-target Android
  ```
  `--build-target Android` is passed directly to the Unity Editor (equivalent to the official Editor launch argument `-buildTarget Android`); Unity switches the Active Build Target to Android during startup — no need to switch manually afterward, and no dependency on any MCP tool.
- If the local `unity` wrapper does not recognize `--build-target`, use the equivalent form (pass the argument through to the Editor):
  ```bash
  unity open $PROJECT_ROOT -- -buildTarget Android
  ```
  or directly `.../Unity -projectPath $PROJECT_ROOT -buildTarget Android`.
- If Unity reports "requested build target is not supported / Android module missing" on startup → go back to B.5 and use `unity install-modules -e <unity_version> -m android` to install Android Build Support, then re-run the `unity open` above.
- Only after all preceding initialization steps have succeeded and the `unity open` command has accepted the launch, merge `project_name`, `mode`, `unity_version`, `platform` (fixed `android`), `devices`, `business_type`, and `pico_unity_init_completed: true` into `$PROJECT_ROOT/.pico-cli/config.json`. Preserve unrelated existing fields, remove the obsolete `sdk` field if present, and write valid JSON atomically. See [references/config-schema.md](references/config-schema.md). If `.pico-cli/` does not exist, create it first.
- Perform that final merge with the bundled `scripts/write_config.py` helper. Resolve the directory containing this `SKILL.md` as `$PICO_INIT_SKILL_DIR`, and pass one `--device` argument for each selected device. For example:
  ```bash
  python3 "$PICO_INIT_SKILL_DIR/scripts/write_config.py" \
    --project-root "$PROJECT_ROOT" \
    --project-name "$project_name" \
    --mode "$mode" \
    --unity-version "$unity_version" \
    --device "pico swan" \
    --business-type "$business_type"
  ```
- If any initialization step fails or the developer cancels/exits at an earlier gate, do **not** write `pico_unity_init_completed: true`; a future explicit `/pico-unity-init` invocation may resume the one-time initialization.

---

## Stage C — One-shot form collection for empty projects

**Only executed when Stage A determines the project is empty.** Merge into **a single form** collected all at once:

| Field           | Control       | Options                           | When shown                          |
| --------------- | ------------- | --------------------------------- | ----------------------------------- |
| `mode`          | Single-select | `picoxr`, `openxr`, `picospatial` | Always                              |
| `unity_version` | Single-select | See "Version options" below       | Always                              |
| `devices`       | Multi-select  | `pico swan`, `pico 4 ultra`       | Always (**required, at least one**) |
| `business_type` | Single-select | `Yes`, `No`                       | Always                              |

> **`devices` is required**: if the developer submits without selecting any device, prompt "Please select at least one target device" and require re-selection; only after validation passes may Stage D begin.
>
> **`business_type` value mapping**: the form question is "**Are you developing an enterprise edition?**" with options "Yes / No". **"Yes" → `business_type = toB`; "No" → `business_type = toC`**. Store the final mapped value when writing config.json.

**Version options (refer to [references/unity-versions.md](references/unity-versions.md)):** use the `unity editors --installed` results from Stage A to split into "installed / not installed" groups for display.

---

## Stage D — Batch execution after empty-project submit

### D.1 Pull the template into `$PROJECT_ROOT`

Based on the form's `mode` selection, map the value to the **subdirectory name** in the upstream templates repo:

- `mode = picoxr` → subdirectory `PICOXR`
- `mode = openxr` → subdirectory `OpenXR`
- `mode = picospatial` → subdirectory `PICOSpatial`

**Preferred method (sparse clone, without git history)**: pull only the selected subdirectory's contents and lay them directly into `$PROJECT_ROOT`.

```bash
TEMPLATE_REPO="https://github.com/Pico-Developer/PICO-Unity-Project-Templates.git"
TEMPLATE_DIR="PICOXR"   # or "OpenXR" / "PICOSpatial", fill in per mode selection

# Use a temp directory for sparse checkout, taking only the needed subdirectory
TMP_TPL="$(mktemp -d)"
git clone --depth 1 --filter=blob:none --sparse "$TEMPLATE_REPO" "$TMP_TPL"
git -C "$TMP_TPL" sparse-checkout set "$TEMPLATE_DIR"

# Move the subdirectory contents (including hidden files) to $PROJECT_ROOT, then remove the temp dir.
# The template repo's Git metadata lives at "$TMP_TPL/.git" (the clone root), NOT inside
# "$TMP_TPL/$TEMPLATE_DIR/", so the glob below never moves any .git into $PROJECT_ROOT.
# We therefore only ever delete the validated temp directory and NEVER touch
# "$PROJECT_ROOT/.git" — any pre-existing project Git metadata is preserved.
shopt -s dotglob 2>/dev/null || true
mv "$TMP_TPL/$TEMPLATE_DIR/"* "$PROJECT_ROOT/"
rm -rf "$TMP_TPL"
```

- Upstream repo structure: three subfolders under the root, `PICOSpatial/`, `PICOXR/`, and `OpenXR/`, each an **independent, openable Unity project** (containing `Assets/`, `Packages/manifest.json`, `ProjectSettings/`, etc.), with the Unity Editor version unified at `6000.0.73f1`.
- This clone goes over GitHub HTTPS (443), following the network requirements of [Stage D.4](#d4-install-the-3-packages-ai-assistant--mcp-extensions--pico-sdk-xr); if the clone fails (no network / SSL issue / GitHub authentication blocked), immediately fall back to the **fallback method** below.

**Fallback method (used when the clone fails)**: call the `pico-cli` local template generator.

```bash
pico-cli project create --template <template> --name pico --package com.example.app
```

`<template>` is taken from the form's `mode` value:

- `mode = picoxr` → `--template picoxr`
- `mode = openxr` → `--template openxr`
- `mode = picospatial` → `--template PICOSpatial`

Run in `$PROJECT_ROOT`. The command generates a complete Unity project structure (`Assets/`, `Packages/manifest.json`, `ProjectSettings/`, `UserSettings/`, etc.).

> ⚠️ If the `pico-cli` command is also not found, tell the developer to install/configure `pico-cli` first (outside the scope of this skill); if both methods fail, have the developer confirm network or CLI status and re-run this skill.

> 💡 Whether using the preferred method or the fallback, once the output lands in `$PROJECT_ROOT`, the subsequent D.2 uniformly updates `productName` and `ProjectVersion.txt`, and D.4 uniformly writes the 3 package dependencies — templates from both sources converge to the same state via the later stages.

### D.2 Template post-processing: fix productName and ProjectVersion

After the template is generated, make two overrides:

#### D.2.1 Modify `productName` in `ProjectSettings/ProjectSettings.asset`

Change the value of the `productName` field to the **current project directory name** (i.e., `project_name` = basename of `$PROJECT_ROOT`).

`ProjectSettings.asset` is in Unity's YAML format; make a **precise line replacement** (only change the `productName:` line, do not touch other fields):

```bash
sed -i '' -E "s|^(  productName: ).*$|\\1${project_name}|" "$PROJECT_ROOT/ProjectSettings/ProjectSettings.asset"
# For GNU sed (Linux), just drop the '' argument: sed -i -E "..."
```

If `project_name` contains spaces or special characters, escape as needed first to ensure the written YAML is valid.

#### D.2.2 Modify `ProjectSettings/ProjectVersion.txt`

Change `m_EditorVersion` and `m_EditorVersionWithRevision` to the `unity_version` selected in the form (same logic as Stage B.4). The template's default version may differ from the selected version and must be overwritten.

### D.3 Prepare the Unity version

Same as Stage B.5:

- Not installed → `unity install <unity_version> -m android`.
- Installed → `unity install-modules -e <unity_version> -m android` to add Android (skip if already installed).

### D.4 Install the 3 packages (AI Assistant / MCP Extensions / PICO SDK XR)

After the empty-project template is generated, `Packages/manifest.json` already exists. **Write the following 5 keys directly into `dependencies` (merging with the template's existing dependencies; do not overwrite other non-conflicting dependencies in the template)**:

> **Bounded exception (same as B.3):** writing these keys straight into the manifest is allowed only because the Unity Editor is not open yet and the `pico_xr_package` MCP tool is not available during init bootstrap. After initialization completes and the Editor/MCP bridge is running, all package changes must go through `pico_xr_package` — do not hand-edit the manifest post-init.

```json
"com.unity.ai.assistant": "2.17.0-pre.1",
"com.bytedance.pico.mcp-extensions": "git@github.com:Pico-Developer/Unity-MCP-Extensions.git",
"com.bytedance.pico.spatialadapter": "https://github.com/Pico-Developer/PICO-Unity-SDK.git?path=/SpatialAdapter#main",
"com.bytedance.pico.xr": "https://github.com/Pico-Developer/PICO-Unity-SDK.git?path=/XR#main",
"com.plattar.unitygltf": "https://github.com/Pico-Developer/gltf-exporter.git?path=package/com.plattar.unitygltf#master"
```

> **MCP Extensions address note**: SSH by default (`git@github.com:...`); if the developer has not configured a GitHub SSH key, or the local network blocks SSH port 22, switch to HTTPS:
>
> ```json
> "com.bytedance.pico.mcp-extensions": "https://github.com/Pico-Developer/Unity-MCP-Extensions.git"
> ```
>
> The common error `ssh: connect to host github.com port 22: Operation timed out` = SSH 22 is blocked; handle in priority order:
>
> 1. Switch directly to the HTTPS dependency (recommended, uses port 443);
> 2. Route SSH over 443: add to `~/.ssh/config`
>    ```
>    Host github.com
>      Hostname ssh.github.com
>      Port 443
>      User git
>    ```
>    then verify with `ssh -T git@github.com`;
> 3. Use a proxy / switch to a company intranet mirror source.

> **Network prerequisite**: Unity will actually access `github.com` when resolving the 4 git dependencies above. If the developer's machine cannot access github.com or authentication fails (SSH `Permission denied (publickey)`, HTTPS `Authentication failed`, or `Could not resolve host`), this is a network/authentication issue, not a manifest-syntax issue. Tell the developer to handle it per the 3 items above; once network/authentication is restored, Unity re-resolves the dependencies with no need to change other steps.

### D.5 Register and open the project (switch to Android on startup)

```
unity projects add /path/to/$PROJECT_ROOT
unity open /path/to/$PROJECT_ROOT --build-target Android
```

- First `unity projects add`: add the project to Unity's known-projects list.
- Then `unity open ... --build-target Android`: let the Unity Editor switch the Active Build Target to Android **during startup**. `--build-target Android` is essentially equivalent to Unity's official Editor launch argument `-buildTarget Android`; the platform switch is performed by Unity itself — no need to switch manually after startup, and no dependency on any MCP tool.
- If the local `unity` wrapper does not recognize `--build-target`, use the equivalent form (pass the argument through to the Editor):
  ```bash
  unity open /path/to/$PROJECT_ROOT -- -buildTarget Android
  ```
  or invoke the Editor binary directly: `.../Unity -projectPath /path/to/$PROJECT_ROOT -buildTarget Android`.

> **The platform must be Android** (PICO devices only support Android builds). If Unity reports "requested build target is not supported / Android module missing / Android Build Support not installed" on startup:
>
> - When installing a new version, use `unity install <unity_version> -m android` (bundle install).
> - For an existing version, use `unity install-modules -e <unity_version> -m android` to add it.
>
> After adding it, re-run `unity open ... --build-target Android`.

### D.6 Write the completed config

Only after D.1-D.5 have succeeded and the `unity open` command has accepted the launch, merge `project_name`, `mode` (`picoxr`, `openxr`, or `picospatial`), `unity_version`, `platform` (fixed `android`), `devices`, `business_type`, and `pico_unity_init_completed: true` into `$PROJECT_ROOT/.pico-cli/config.json`. Preserve unrelated existing fields, remove the obsolete `sdk` field if present, and write valid JSON atomically. See [references/config-schema.md](references/config-schema.md). If `.pico-cli/` does not exist, create only the directory needed for `config.json`; do not create `downloads/`.

Use the bundled `scripts/write_config.py` helper as shown in B.6, passing the empty-project form's selected `mode` and one `--device` argument per selected device.

If any initialization step fails or the developer cancels/exits at an earlier gate, do **not** write `pico_unity_init_completed: true`; a future explicit `/pico-unity-init` invocation may resume the one-time initialization.

---

## After completion

Give the developer a brief report:

- Project type (empty / valid existing / incomplete or invalid Unity project layout);
- For an empty project, the **template source**: "GitHub sparse-clone `PICOSpatial|PICOXR|OpenXR`" or "fallback `pico-cli project create --template ...`";
- Unity version (if `ProjectVersion.txt` was rewritten, note the adjustment from `xxx` to the selected version);
- Handling result of the 3 packages: AI Assistant (**newly installed / already present, skipped / upgraded to 2.17.0-pre.1**), MCP Extensions (**newly installed / already present, skipped**), PICO SDK XR (including gltf-exporter and SpatialAdapter, 3 git dependencies total) (**newly installed / ≥6.0.0 skipped / <6.0.0 upgrade-overwritten / version unknown, skipped**);
- Target platform: switched by Unity on startup via `unity open ... --build-target Android`, noting whether it was "switched to Android by the CLI argument this time / switched to Android after installing Android Build Support and reopening";
- Selected devices and business type (`toB` / `toC`);
- Selected mode (`picoxr` / `openxr` / `picospatial`);
- The path where `config.json` was written and confirmation that `pico_unity_init_completed` is `true`.
