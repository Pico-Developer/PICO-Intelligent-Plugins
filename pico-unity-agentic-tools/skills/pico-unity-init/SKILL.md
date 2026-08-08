---
name: pico-unity-init
license: 'Apache-2.0'
description: >-
  PICO Unity project initialization wizard (manual trigger only). Runs ONLY
  when the developer explicitly invokes `/pico-unity-init`; passive/automatic
  triggering is forbidden — even if the developer mentions similar intents
  (e.g. "initialize a PICO project", "create a new Unity XR project",
  "configure the PICO SDK"), do not self-trigger; wait for an explicit
  `/pico-unity-init`. Functionality first probes whether the project is empty.
  Non-empty then checks the 3 packages and incrementally installs as needed.
  Empty then sparse-clones the matching template (`PICOXR`/`OpenXR`) from
  `Pico-Developer/PICO-Unity-Project-Templates`, falling back to
  `pico-cli project create` on failure; then syncs version info and installs
  AI Assistant / MCP Extensions / PICO Unity SDK (XR). Finally writes
  `config.json` and opens the project via `unity open ... --build-target
  Android`, switching the Active Build Target to Android on startup.
---

# pico-unity-init

PICO Unity project initialization wizard. Run the initialization flow when `.pico-cli/config.json` under the project root does **not** exist; if the file already exists, the project has already been initialized — stop immediately and tell the developer there is no need to initialize again.

## Pre-trigger check (GUARDRAIL)

1. Confirm the current working project path (hereafter `$PROJECT_ROOT`). The project name `project_name` is the directory name (basename) of `$PROJECT_ROOT`; there is no need to ask the developer.
2. Check whether `$PROJECT_ROOT/.pico-cli/config.json` exists:
   - **Exists** → the project is already initialized; stop immediately and prompt: "This project is already initialized. To reset, manually delete `.pico-cli/config.json` and retry."
   - **Does not exist** → proceed to the initialization flow below.

> This skill is executed by the **local agent running on the developer's own machine**. All file reads/writes and command execution act directly on the **developer's local project directory**. Always use the local shell (local `bash`) and local file operations directly; no remote sandbox is involved, and there is no need to go through proxy tools such as `mira_local_*`.

## Initialization flow overview

**Emptiness check first → branch handling**:

- **Non-empty project** (Stage B): do not copy a template; directly **incrementally install the 3 packages** (AI Assistant / Unity MCP Extensions / PICO Unity SDK XR), skipping or upgrading based on existing dependency state.
- **Empty project** (Stage C → D): preferentially sparse-clone the corresponding template subdirectory (`PICOXR` / `OpenXR`) from `Pico-Developer/PICO-Unity-Project-Templates` (GitHub) into `$PROJECT_ROOT`; fall back to `pico-cli project create` on failure. Then modify `productName` / `ProjectVersion.txt`, and install the 3 packages.

**Shared wrap-up**: both branches finally open the project with `unity open ... --build-target Android`, letting Unity switch the Active Build Target to Android during startup (equivalent to the official Editor launch argument `-buildTarget Android`) — no need to switch manually after opening, and no dependency on MCP tools.

---

### Stage A — Read-only probing (do not ask the developer; run first)

Before popping up any form, complete the following read-only probing (shared by all branches):

1. **Emptiness check** (highest priority): check whether both `Assets/` directory **and** `Packages/manifest.json` are **missing at the same time**. Both missing → **empty project**; either present → **non-empty project**.
2. **Additional reads for non-empty projects**: read `m_EditorVersion` from `$PROJECT_ROOT/ProjectSettings/ProjectVersion.txt` (used for the low-version gate in Stage B). Read `dependencies` from `$PROJECT_ROOT/Packages/manifest.json` (used in Stage B to determine the current versions of the 3 packages).
3. **Check installed editors** (only needed for empty projects): run `unity editors --installed` to split candidate Unity 6+ LTS versions into "installed / not installed" groups. **For non-empty projects, if Stage B does not change the version, you may skip this step to save time.**

---

## Stage B — Non-empty project branch (runs first; goes straight to incremental installation)

**If Stage A determines the project is non-empty, do not take the empty-project branch; execute B.1 → B.6 in order.**

### B.1 Low-version gate

- **Current version < Unity 6 (major version < 6000)**: ask "The current project's Unity version is `xxx`, which is below Unity 6. Upgrade?"
  - Choose "No" → **exit initialization immediately** (do not write config, do not continue).
  - Choose "Yes" → let the developer select a target Unity 6+ LTS version in the B.2 form.
- **Current version ≥ Unity 6**: ask "The current project's Unity version is `xxx`. Change the version?"
  - Choose "No" → keep the current version as `unity_version`; the B.2 form no longer shows the version selection item.
  - Choose "Yes" → the B.2 form requires selecting a target Unity 6+ LTS version.

### B.2 Minimal form collection (non-empty project)

A non-empty project already has an SDK choice (determined by existing dependencies; the `sdk` field is left blank or marked `existing`). The form **collects only necessary preferences**:

| Field           | Control       | Options                     | When shown                                     |
| --------------- | ------------- | --------------------------- | ---------------------------------------------- |
| `unity_version` | Single-select | See "Version options" below | Only when B.1 chose "upgrade / change version" |
| `devices`       | Multi-select  | `pico swan`, `pico 4 ultra` | Always (**required, at least one**)            |
| `business_type` | Single-select | `Yes`, `No`                 | Always                                         |

> The values and mapping rules for `devices` and `business_type` are the same as in Stage C.

### B.3 Incrementally install the 3 packages (core logic)

Check the conditions below and write into the `dependencies` of `Packages/manifest.json`. **Preserve all of the developer's other existing dependencies; only make incremental additions/changes.**

#### B.3.1 AI Assistant (`com.unity.ai.assistant`)

- **Not present** in `dependencies` → write `"com.unity.ai.assistant": "2.17.0-pre.1"`.
- **Present but version is not 2.17.0-pre.1** in `dependencies` → upgrade to `"2.17.0-pre.1"` (treated as "not on the latest").
- Already present and the version is already `2.17.0-pre.1` → **skip**.

#### B.3.2 Unity MCP Extensions (`com.bytedance.pico.mcp-extensions`)

- **Not present** in `dependencies` → write the following git dependency (SSH by default; if the developer has not configured an SSH key, switch to HTTPS — see the note in Stage D.4):
  ```json
  "com.bytedance.pico.mcp-extensions": "git@github.com:Pico-Developer/Unity-MCP-Extensions.git"
  ```
- Already present (pointing to that repo) → **skip** (keep the existing address and ref unchanged).

#### B.3.3 PICO Unity SDK (XR) three git dependencies

Check whether `com.bytedance.pico.xr` exists in `dependencies`:

- **Not present** → write the following **3 git dependencies together** into `dependencies`:
  ```json
  "com.bytedance.pico.spatialadapter": "https://github.com/Pico-Developer/PICO-Unity-SDK.git?path=/SpatialAdapter#main",
  "com.bytedance.pico.xr": "https://github.com/Pico-Developer/PICO-Unity-SDK.git?path=/XR#main",
  "com.plattar.unitygltf": "https://github.com/Pico-Developer/gltf-exporter.git?path=package/com.plattar.unitygltf#master"
  ```
- **Already present**, try to read the version from the `#ref` in the git URL or from the cached package's `package.json`:
  - Version **≥ 6.0.0** → **skip, do not update** (keep the developer's existing version, address, and ref).
  - Version **< 6.0.0** → ask the developer "The detected PICO Unity SDK (XR) version `xxx` is below 6.0.0. Upgrade to 6.0.0?"
    - Choose "No" → **exit the initialization flow immediately** (do not modify the manifest, do not write config).
    - Choose "Yes" → overwrite the corresponding keys with the 3 git dependencies above (write all 3 keys together, even if only `com.bytedance.pico.xr` was originally present).

> **Version-detection fallback**: when a git dependency (with `#ref` being a branch name such as `#main`) cannot yield a version number directly from the URL, try reading `version` from `Library/PackageCache/com.bytedance.pico.xr@*/package.json`; if there is no cache, treat it as "version cannot be determined" by default → the conservative approach is to **skip and not proactively upgrade**, only logging for the developer: "PICO SDK XR is present but its version is unknown; upgrade skipped. To force a refresh, manually change the `#ref`."

### B.4 Sync `ProjectVersion.txt` (only when B.1 chose to change the version)

If B.1 chose "upgrade / change version", set `m_EditorVersion` and `m_EditorVersionWithRevision` in `$PROJECT_ROOT/ProjectSettings/ProjectVersion.txt` to the `unity_version` selected in B.2.

### B.5 Prepare the Unity version

Refer to [references/unity-versions.md](references/unity-versions.md):

- If `unity_version` comes from the "not installed" list → `unity install <unity_version> -m android` (bundle-installs Android Build Support; this takes a while — inform the developer before running).
- If it comes from the "installed" list or you keep the current version → `unity install-modules -e <unity_version> -m android` to confirm Android is installed (check the **Status** column in the output; skip if already installed).

### B.6 Write config.json and open the project (switch to Android on startup)

- Write `project_name`, `sdk` (for a non-empty project fill in `existing`, do not ask again), `unity_version`, `platform` (fixed `android`), `devices`, and `business_type` into `$PROJECT_ROOT/.pico-cli/config.json`. See the config structure in [references/config-schema.md](references/config-schema.md). If `.pico-cli/` does not exist, create it first.
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

---

## Stage C — One-shot form collection for empty projects

**Only executed when Stage A determines the project is empty.** Merge into **a single form** collected all at once:

| Field           | Control       | Options                     | When shown                          |
| --------------- | ------------- | --------------------------- | ----------------------------------- |
| `sdk`           | Single-select | `openxr`, `picoxr`          | Always                              |
| `unity_version` | Single-select | See "Version options" below | Always                              |
| `devices`       | Multi-select  | `pico swan`, `pico 4 ultra` | Always (**required, at least one**) |
| `business_type` | Single-select | `Yes`, `No`                 | Always                              |

> **`devices` is required**: if the developer submits without selecting any device, prompt "Please select at least one target device" and require re-selection; only after validation passes may Stage D begin.
>
> **`business_type` value mapping**: the form question is "**Are you developing an enterprise edition?**" with options "Yes / No". **"Yes" → `business_type = toB`; "No" → `business_type = toC`**. Store the final mapped value when writing config.json.

**Version options (refer to [references/unity-versions.md](references/unity-versions.md)):** use the `unity editors --installed` results from Stage A to split into "installed / not installed" groups for display.

---

## Stage D — Batch execution after empty-project submit

### D.1 Pull the template into `$PROJECT_ROOT`

Based on the form's `sdk` selection, map the value to the **subdirectory name** in the upstream templates repo:

- `sdk = picoxr` → subdirectory `PICOXR`
- `sdk = openxr` → subdirectory `OpenXR`

**Preferred method (sparse clone, without git history)**: pull only the selected subdirectory's contents and lay them directly into `$PROJECT_ROOT`.

```bash
TEMPLATE_REPO="https://github.com/Pico-Developer/PICO-Unity-Project-Templates.git"
TEMPLATE_DIR="PICOXR"   # or "OpenXR", fill in per sdk selection

# Use a temp directory for sparse checkout, taking only the needed subdirectory
TMP_TPL="$(mktemp -d)"
git clone --depth 1 --filter=blob:none --sparse "$TEMPLATE_REPO" "$TMP_TPL"
git -C "$TMP_TPL" sparse-checkout set "$TEMPLATE_DIR"

# Move the subdirectory contents (including hidden files) to $PROJECT_ROOT, then remove the temp dir and .git
shopt -s dotglob 2>/dev/null || true
mv "$TMP_TPL/$TEMPLATE_DIR/"* "$PROJECT_ROOT/"
rm -rf "$TMP_TPL"
# After moving, $PROJECT_ROOT should not retain a .git; if mv accidentally brought the repo's .git over, force-clean it
rm -rf "$PROJECT_ROOT/.git"
```

- Upstream repo structure: two subfolders under the root, `PICOXR/` and `OpenXR/`, each an **independent, openable Unity project** (containing `Assets/`, `Packages/manifest.json`, `ProjectSettings/`, etc.), with the Unity Editor version unified at `6000.0.73f1`.
- This clone goes over GitHub HTTPS (443), following the network requirements of [Stage D.4](#d4-install-the-3-packages-ai-assistant--mcp-extensions--pico-sdk-xr); if the clone fails (no network / SSL issue / GitHub authentication blocked), immediately fall back to the **fallback method** below.

**Fallback method (used when the clone fails)**: call the `pico-cli` local template generator.

```bash
pico-cli project create --template <template> --name pico --package com.example.app
```

`<template>` is taken from the form's `sdk` value:

- `sdk = picoxr` → `--template picoxr`
- `sdk = openxr` → `--template openxr`

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

### D.5 Write config.json

Write `project_name`, `sdk` (`picoxr` or `openxr`), `unity_version`, `platform` (fixed `android`), `devices`, and `business_type` into `$PROJECT_ROOT/.pico-cli/config.json`. See the config structure in [references/config-schema.md](references/config-schema.md). If `.pico-cli/` does not exist, create it first (create only up to where `config.json` lives; do not create `downloads/`).

### D.6 Register and open the project (switch to Android on startup)

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

---

## After completion

Give the developer a brief report:

- Project type (empty project / non-empty project);
- For an empty project, the **template source**: "GitHub sparse-clone `PICOXR|OpenXR`" or "fallback `pico-cli project create --template ...`";
- Unity version (if `ProjectVersion.txt` was rewritten, note the adjustment from `xxx` to the selected version);
- Handling result of the 3 packages: AI Assistant (**newly installed / already present, skipped / upgraded to 2.17.0-pre.1**), MCP Extensions (**newly installed / already present, skipped**), PICO SDK XR (including gltf-exporter and SpatialAdapter, 3 git dependencies total) (**newly installed / ≥6.0.0 skipped / <6.0.0 upgrade-overwritten / version unknown, skipped**);
- Target platform: switched by Unity on startup via `unity open ... --build-target Android`, noting whether it was "switched to Android by the CLI argument this time / switched to Android after installing Android Build Support and reopening";
- Selected devices and business type (`toB` / `toC`);
- The path where `config.json` was written.
