# Unity version detection and LTS list

## Detecting the current project's Unity version

Read `$PROJECT_ROOT/ProjectSettings/ProjectVersion.txt`, example content:

```
m_EditorVersion: 6000.0.73f1
m_EditorVersionWithRevision: 6000.0.73f1 (a166abc3bf0e)
```

The first segment of `m_EditorVersion` is the major version:
- `6000.x.y` → Unity 6 (i.e., "Unity 6 and later").
- Major version `< 6000` (e.g. `2022.3.x`, `2021.3.x`) → older than Unity 6.

## "Post-Unity 6 LTS" candidate list

When presenting selectable versions to the developer, list Unity 6-series LTS versions. Use the latest official LTS releases; before display, it's recommended to confirm the latest patch numbers in real time. Currently selectable (examples):

- `6000.0.x` LTS (Unity 6.0 LTS) — e.g. `6000.0.73f1`
- `6000.1.x` LTS (later LTS, if released)
- `6000.2.x` LTS (later LTS, if released)

> Note: only Unity 6 (6000-series) and later LTS versions are listed. Refer to the official Unity LTS release page for the actual available patch versions. When displaying, provide the full version string (including suffixes like `f1`) so the Unity CLI can precisely locate the installation.

## Query Unity editors installed on the local machine

Use the **Unity CLI** (not Unity Hub) to list installed editors on the local machine (executed by the local agent directly in the developer's local shell):

```
unity editors --installed
```

> Note: this skill uses the Unity CLI throughout (matching the toolchain used in the "register and open project" stage); Unity Hub is not used. The output is a list of installed version numbers (e.g. `6000.0.73f1`), used to split the candidate LTS into two groups.

## The two version-selection groups (for the Stage C form's version options)

When presenting to the developer, **you must split into two categories**:

- **2.1.1 Installed list**: versions found by `unity editors --installed` above that also belong to Unity 6+ LTS. When the developer picks one → use it directly as `unity_version`; no installation needed.
- **2.1.2 Not-installed list**: official Unity 6+ LTS versions not yet installed locally. When the developer picks one → install it first using the command below, then use it as `unity_version`.

Install a new Unity version (**must use `-m android` to bundle-install Android Build Support**; PICO is an Android platform):

```
unity install <VERSION> -m android
```

If an installed version lacks the Android module, use the command below to add Android to that existing version (check the **Status** column in the output to determine whether the module is already installed):

```
unity install-modules -e <VERSION> -m android
```

> If the Unity CLI is not installed locally, ask the developer to install the Unity CLI first before continuing. Installing a major version takes a while — notify the developer beforehand.

### Sync to Unity Hub after installation

Editors installed via `unity install` may not automatically appear in Unity Hub's "Installed editors" list (Unity Hub has no record of them). After installation completes, register the editor path with Unity Hub so it becomes visible:

- Locate the install path: the editor executable/install directory for that version listed in `unity editors --installed`.
- Have Unity Hub pick up the path (choose one):
  - Unity Hub GUI: Installs → top-right `Locate` (locate an existing install) → select the install directory of that version;
  - Or use the Unity Hub CLI to add an existing editor path (`... --headless install-path --set` / `editors --add <PATH>` — subject to what your local Hub version supports).

> Note: version queries and installations go through the **Unity CLI**; only the "make Hub aware of this editor" step involves a Unity Hub action. Developers not using Unity Hub can skip this subsection.

## Register and open the project (corresponds to Stage D.7)

When wrapping up initialization, first register the project into Unity's known-projects list (so the developer can later open it directly from the project list), then open it with the selected version, forcing the target platform to Android:

```
unity projects add /path/to/PROJECT_ROOT
unity open /path/to/PROJECT_ROOT --build-target Android
```

- `unity projects add <PROJECT_ROOT>`: add the project to Unity's known-projects list; does not launch the editor.
- `unity open ... --build-target Android`: open the project with the selected `unity_version` and set the Active Build Target to **Android**. PICO is an Android platform — other platforms like Windows / macOS / WebGL are not allowed. If multiple versions exist locally, make sure the version chosen in the form is the one being used; if that version lacks Android Build Support, install the Android module first before opening (bundle-install for a new version: `unity install <VERSION> -m android`; add-on install for an existing version: `unity install-modules -e <VERSION> -m android`; check the **Status** column in the output to confirm).
