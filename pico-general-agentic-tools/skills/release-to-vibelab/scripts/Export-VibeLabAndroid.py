#!/usr/bin/env python3
"""Export a Unity PICO XR project as a validated VibeLab Gradle repository."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional, Sequence


MIN_FREE_BYTES = 6 * 1024 * 1024 * 1024
FORBIDDEN_DIRS = {"build", ".gradle", ".cxx", "symbols", "Il2CppOutputProject"}
FORBIDDEN_SUFFIXES = {".apk", ".aab", ".keystore", ".jks"}


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_path(value: str, *, must_exist: bool = False) -> Path:
    path = Path(value).expanduser().resolve(strict=must_exist)
    return path


def read_unity_version(project: Path) -> str:
    version_file = project / "ProjectSettings" / "ProjectVersion.txt"
    if not version_file.is_file():
        fail(f"Unity version file is missing: {version_file}")
    match = re.search(
        r"^m_EditorVersion:\s*(\S+)\s*$",
        version_file.read_text(encoding="utf-8-sig"),
        re.MULTILINE,
    )
    if not match:
        fail(f"Cannot read m_EditorVersion from {version_file}")
    return match.group(1)


def resolve_unity_editor(
    requested: Optional[str], unity_version: str, host: str
) -> Path:
    candidates: list[Path] = []
    if requested:
        candidates.append(normalize_path(requested))
    if host == "Windows":
        candidates.extend(
            [
                Path(
                    rf"C:\Program Files\Unity\Hub\Editor\{unity_version}"
                    r"\Editor\Unity.exe"
                ),
                Path(
                    rf"C:\Program Files\Unity Hub\Editor\{unity_version}"
                    r"\Editor\Unity.exe"
                ),
            ]
        )
    else:
        candidates.extend(
            [
                Path(
                    f"/Applications/Unity/Hub/Editor/{unity_version}/"
                    "Unity.app/Contents/MacOS/Unity"
                ),
                Path.home()
                / "Applications"
                / "Unity"
                / "Hub"
                / "Editor"
                / unity_version
                / "Unity.app"
                / "Contents"
                / "MacOS"
                / "Unity",
            ]
        )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    fail(
        f"Unity {unity_version} was not found on {host}. "
        "Pass --unity-editor-path."
    )


def android_player_root(editor: Path, host: str) -> Path:
    if host == "Windows":
        return editor.parent / "Data" / "PlaybackEngines" / "AndroidPlayer"
    return editor.parent.parent / "PlaybackEngines" / "AndroidPlayer"


def version_key(value: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", value)
    return tuple(int(part) for part in parts)


def find_build_tool(sdk: Path, name: str) -> Path:
    candidates = [
        directory / name
        for directory in (sdk / "build-tools").iterdir()
        if directory.is_dir() and (directory / name).is_file()
    ]
    if not candidates:
        fail(f"Android build tool '{name}' was not found under {sdk}.")
    return max(candidates, key=lambda path: version_key(path.parent.name))


def find_gradle_launcher(android_root: Path) -> Path:
    candidates = list((android_root / "Tools" / "gradle" / "lib").glob(
        "gradle-launcher-*.jar"
    ))
    if not candidates:
        fail(f"Gradle launcher was not found under {android_root}.")
    return max(candidates, key=lambda path: version_key(path.name))


def run_logged(
    executable: Path,
    arguments: Sequence[str],
    log_path: Path,
    *,
    cwd: Optional[Path] = None,
    env: Optional[dict[str, str]] = None,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [str(executable), *map(str, arguments)],
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.write_text(completed.stdout or "", encoding="utf-8")
    if completed.returncode != 0:
        tail = "\n".join((completed.stdout or "").splitlines()[-80:])
        fail(
            f"Command failed with exit code {completed.returncode}: "
            f"{executable}\n{tail}"
        )


def open_unity_processes(project: Path, host: str) -> list[dict[str, Any]]:
    normalized = str(project).replace("\\", "/")
    if host == "Windows":
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            return []
        command = (
            "Get-CimInstance Win32_Process -Filter \"Name = 'Unity.exe'\" | "
            "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
        )
        completed = subprocess.run(
            [shell, "-NoProfile", "-Command", command],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0 or not completed.stdout.strip():
            return []
        parsed = json.loads(completed.stdout)
        records = parsed if isinstance(parsed, list) else [parsed]
        return [
            record
            for record in records
            if normalized.lower()
            in str(record.get("CommandLine") or "").replace("\\", "/").lower()
        ]

    completed = subprocess.run(
        ["/bin/ps", "-axo", "pid=,command="],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    matches: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        match = re.match(r"\s*(\d+)\s+(.+)", line)
        if not match:
            continue
        command_line = match.group(2)
        if (
            "/Unity.app/Contents/MacOS/Unity" in command_line
            and normalized in command_line.replace("\\", "/")
        ):
            matches.append(
                {"ProcessId": int(match.group(1)), "CommandLine": command_line}
            )
    return matches


def gradle_properties(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")) or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def set_gradle_property(path: Path, name: str, value: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    pattern = re.compile(rf"^(\s*{re.escape(name)}\s*=).*$", re.MULTILINE)
    if pattern.search(text):
        text = pattern.sub(lambda match: match.group(1) + value, text, count=1)
    else:
        text = text.rstrip() + f"\n{name}={value}\n"
    path.write_text(text, encoding="utf-8")


def find_pico_loader_guid(project: Path) -> str:
    matches: list[Path] = []
    marker = "ByteDance.PICO.XR.PXR_Loader"
    for asset in (project / "Assets").rglob("*.asset"):
        try:
            text = asset.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        if marker in text:
            matches.append(asset)
    if len(matches) != 1:
        fail(f"Expected one PICO XR loader asset, found {len(matches)}.")
    meta = Path(str(matches[0]) + ".meta")
    if not meta.is_file():
        fail(f"PICO XR loader metadata is missing: {meta}")
    guid_match = re.search(
        r"^guid:\s*(\S+)\s*$",
        meta.read_text(encoding="utf-8-sig"),
        re.MULTILINE,
    )
    if not guid_match:
        fail(f"Cannot read the PICO XR loader GUID from {meta}.")
    return guid_match.group(1)


def find_android_xr_settings(project: Path) -> str:
    matches: list[str] = []
    for asset in (project / "Assets").rglob("*.asset"):
        try:
            text = asset.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        if "m_Name: Android Providers" in text and "m_Loaders:" in text:
            matches.append(text)
    if len(matches) != 1:
        fail(f"Expected one Android XR Manager settings asset, found {len(matches)}.")
    return matches[0]


def validate_source_project(project: Path) -> dict[str, Any]:
    settings_path = project / "ProjectSettings" / "ProjectSettings.asset"
    settings = settings_path.read_text(encoding="utf-8-sig")

    def required(pattern: str, message: str, flags: int = re.MULTILINE) -> re.Match[str]:
        match = re.search(pattern, settings, flags)
        if not match:
            fail(message)
        return match

    application_id = required(
        r"^\s*applicationIdentifier:\s*\r?\n\s+Android:\s*([^\r\n]+)",
        "Android application identifier is missing.",
    ).group(1).strip()
    min_sdk = int(
        required(
            r"^\s*AndroidMinSdkVersion:\s*(\d+)\s*$",
            "Android minimum SDK is missing.",
        ).group(1)
    )
    if min_sdk < 29:
        fail("Android minimum SDK must be at least 29.")
    architecture = required(
        r"^\s*AndroidTargetArchitectures:\s*(\d+)\s*$",
        "Android target architectures are missing.",
    ).group(1)
    if architecture != "2":
        fail("Android target architectures must be ARM64 only.")
    custom_keystore = required(
        r"^\s*androidUseCustomKeystore:\s*(\d+)\s*$",
        "Android custom keystore setting is missing.",
    ).group(1)
    if custom_keystore != "0":
        fail("Custom Android keystore must be disabled.")
    backend = required(
        r"^\s*scriptingBackend:\s*\r?\n\s+Android:\s*(\d+)\s*$",
        "Android scripting backend is missing.",
        re.MULTILINE,
    ).group(1)
    if backend != "1":
        fail("Android scripting backend must be IL2CPP.")

    loader_guid = find_pico_loader_guid(project)
    xr_settings = find_android_xr_settings(project)
    providers = re.search(
        r"m_Name:\s*Android Providers.*?m_Loaders:\s*(.*?)(?=^--- !u!|\Z)",
        xr_settings,
        re.MULTILINE | re.DOTALL,
    )
    if not providers:
        fail("Android XR loader settings are missing.")
    loader_guids = re.findall(r"guid:\s*([0-9a-fA-F]+)", providers.group(1))
    if loader_guids != [loader_guid]:
        fail("Android XR loaders must contain only ByteDance.PICO.XR.PXR_Loader.")

    build_settings = (
        project / "ProjectSettings" / "EditorBuildSettings.asset"
    ).read_text(encoding="utf-8-sig")
    enabled_scenes = len(
        re.findall(r"^\s*-\s*enabled:\s*1\s*$", build_settings, re.MULTILINE)
    )
    if enabled_scenes == 0:
        fail("No enabled build scenes were found.")

    return {
        "application_id": application_id,
        "min_sdk": min_sdk,
        "enabled_scenes": enabled_scenes,
    }


def update_unity_library_gradle(path: Path) -> None:
    text = path.read_text(encoding="utf-8-sig")
    pattern = re.compile(
        r"^(\s*)jni\.srcDirs\s*=\s*\[[^\r\n]*Il2CppOutputProject[^\r\n]*\]\s*$",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    if len(matches) > 1:
        fail(f"Found multiple Il2CppOutputProject jni.srcDirs declarations in {path}")
    if len(matches) == 1:
        text = pattern.sub(
            lambda match: match.group(1) + "jni.srcDirs = []", text, count=1
        )
    elif not re.search(r"jni\.srcDirs\s*=\s*\[\s*\]", text):
        text = (
            text.rstrip()
            + "\n\nandroid {\n"
            + "    sourceSets {\n"
            + "        main {\n"
            + "            jni.srcDirs = []\n"
            + "        }\n"
            + "    }\n"
            + "}\n"
        )
    disable = "tasks.named('buildIl2Cpp').configure { enabled = false }"
    if not re.search(
        r"tasks\.named\(['\"]buildIl2Cpp['\"]\).*enabled\s*=\s*false", text
    ):
        text = text.rstrip() + f"\n\n{disable}\n"
    path.write_text(text, encoding="utf-8")


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        dirs_exist_ok=True,
        symlinks=True,
        copy_function=shutil.copy2,
    )


def sync_target(stage: Path, target: Path) -> None:
    for item in target.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            item.unlink()
    copy_tree(stage, target)


def remove_generated_outputs(root: Path) -> None:
    explicit = [
        root / "local.properties",
        root / "unityLibrary" / "src" / "main" / "jniStaticLibs",
    ]
    for path in explicit:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    directories = sorted(
        [
            path
            for path in root.rglob("*")
            if path.is_dir()
            and (
                path.name in FORBIDDEN_DIRS
                or path.name.endswith("_BurstDebugInformation_DoNotShip")
            )
        ],
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for path in directories:
        if path.exists():
            shutil.rmtree(path)
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES:
            path.unlink()


def file_inventory(root: Path, *, exclude_git: bool = False) -> dict[str, Any]:
    inventory: dict[str, Any] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if exclude_git and relative.parts and relative.parts[0] == ".git":
            continue
        inventory[relative.as_posix()] = {
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return inventory


def write_prebuilt_manifest(
    stage: Path, unity_version: str, ndk_version: str, il2cpp_hash: str
) -> None:
    properties = gradle_properties(stage / "gradle.properties")
    native_dir = stage / "unityLibrary" / "src" / "main" / "jniLibs" / "arm64-v8a"
    metadata = (
        stage
        / "unityLibrary"
        / "src"
        / "main"
        / "assets"
        / "bin"
        / "Data"
        / "Managed"
        / "Metadata"
        / "global-metadata.dat"
    )
    if not metadata.is_file():
        fail(f"Canonical global-metadata.dat is missing: {metadata}")
    native_inventory = [
        {"name": path.name, "sha256": sha256_file(path)}
        for path in sorted(native_dir.glob("*.so"))
    ]
    manifest = {
        "schema": 1,
        "processor_revision": "il2cpp-prebuild-v7-cross-platform",
        "il2cpp_so_sha256": il2cpp_hash,
        "global_metadata_sha256": sha256_file(metadata),
        "unity_version": unity_version,
        "unity_template_version": properties.get("unityTemplateVersion"),
        "ndk_version": ndk_version,
        "abi": ["arm64-v8a"],
        "target_sdk": int(properties["unity.targetSdkVersion"]),
        "application_id": properties.get("unity.applicationId"),
        "native_inventory": native_inventory,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    (stage / ".vibelab-prebuilt.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_report(path: Path, data: dict[str, Any], page_size_policy: str) -> None:
    warnings = "\n".join(f"- {warning}" for warning in data["warnings"]) or "- None."
    content = f"""# VibeLab PICO Android Gradle Export

Export date: {data["date"]}
Target repository: `{data["target_repo"]}`

## Result

- Route: PICO XR / PXR Loader
- Host platform: {data["host_platform"]}
- Unity: `{data["unity_version"]}`
- Backend / ABI: IL2CPP / arm64-v8a
- Application ID: `{data["application_id"]}`
- Android SDK: min {data["min_sdk"]} / target {data["target_sdk"]}
- NDK: `{data["ndk_version"]}`
- `libil2cpp.so` SHA-256: `{data["il2cpp_hash"]}`
- Pre-slim APK native libraries: {data["native_library_count"]}
- Post-slim APK native libraries: {data["native_library_count"]}
- Final Gradle verification: `:unityLibrary:buildIl2Cpp SKIPPED`
- Page-size policy: `{page_size_policy}`
- Target file count: {data["file_count"]}

## Validation Warnings

{warnings}

## Boundaries

- The target repository contains no APK, AAB, keystore, `local.properties`,
  Gradle cache, build directory, symbols directory, or `Il2CppOutputProject`.
- The target repository's `.git` directory was preserved.
- This workflow did not commit, push, or add Git LFS.
- Local Gradle validation does not replace PICO headset runtime validation.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-path")
    parser.add_argument("--target-repo")
    parser.add_argument("--unity-editor-path")
    parser.add_argument("--report-path")
    parser.add_argument(
        "--page-size-policy", choices=("warn", "fail"), default="warn"
    )
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--keep-work-dir", action="store_true")
    parser.add_argument("--self-test-host", choices=("Windows", "Darwin"), help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    if sys.version_info < (3, 9):
        fail("Python 3.9 or newer is required.")
    args = parse_args()
    system = args.self_test_host or platform.system()
    if system not in {"Windows", "Darwin"}:
        fail("This export workflow supports Windows and macOS only.")
    host = "Windows" if system == "Windows" else "macOS"
    script = Path(__file__).resolve()
    skill_root = script.parent.parent
    project = (
        normalize_path(args.project_path, must_exist=True)
        if args.project_path
        else Path.cwd().resolve()
    )
    required_project_paths = (
        project / "Assets",
        project / "Packages" / "manifest.json",
        project / "ProjectSettings" / "ProjectVersion.txt",
    )
    if not required_project_paths[0].is_dir() or any(
        not path.is_file() for path in required_project_paths[1:]
    ):
        fail(
            f"Unity project root is invalid: {project}. Run from the Unity project "
            "root or pass --project-path."
        )
    target_value = args.target_repo or os.environ.get("VIBELAB_TARGET_REPO")
    if not target_value:
        fail(
            "Target repository is required. Pass --target-repo or set "
            "VIBELAB_TARGET_REPO."
        )
    target = normalize_path(target_value)
    report = (
        normalize_path(args.report_path)
        if args.report_path
        else project
        / "Docs"
        / f"VibeLab-Android-Gradle-Export-{dt.date.today().isoformat()}.md"
    )

    unity_version = read_unity_version(project)
    unity = resolve_unity_editor(args.unity_editor_path, unity_version, host)
    android_root = android_player_root(unity, host)
    suffix = ".exe" if host == "Windows" else ""
    ndk_host = "windows-x86_64" if host == "Windows" else "darwin-x86_64"
    java = android_root / "OpenJDK" / "bin" / f"java{suffix}"
    sdk = android_root / "SDK"
    ndk = android_root / "NDK"
    readelf = (
        ndk
        / "toolchains"
        / "llvm"
        / "prebuilt"
        / ndk_host
        / "bin"
        / f"llvm-readelf{suffix}"
    )
    gradle_launcher = find_gradle_launcher(android_root)
    zipalign = find_build_tool(sdk, f"zipalign{suffix}")
    validator = script.parent / "Validate-VibeLabApk.py"
    export_template = skill_root / "assets" / "VibeLabExport.cs"
    for required_path in (
        unity,
        java,
        readelf,
        gradle_launcher,
        zipalign,
        validator,
        export_template,
    ):
        if not required_path.is_file():
            fail(f"Required tool or asset is missing: {required_path}")

    source = validate_source_project(project)
    open_processes = [] if args.self_test_host else open_unity_processes(project, host)
    preflight = {
        "ok": True,
        "host_platform": host,
        "project": str(project),
        "target_repo": str(target),
        "unity_version": unity_version,
        "unity_editor": str(unity),
        "application_id": source["application_id"],
        "min_sdk": source["min_sdk"],
        "backend": "IL2CPP",
        "abi": "arm64-v8a",
        "xr_loader": "ByteDance.PICO.XR.PXR_Loader",
        "enabled_scenes": source["enabled_scenes"],
        "project_open_in_unity": bool(open_processes),
        "page_size_policy": args.page_size_policy,
    }
    if args.preflight_only:
        print(json.dumps(preflight, ensure_ascii=False, indent=2))
        return 0
    if args.validate_only:
        completed = subprocess.run(
            [
                sys.executable,
                str(validator),
                "--project",
                str(target),
                "--manifest",
                str(target / ".vibelab-prebuilt.json"),
                "--page-size-policy",
                args.page_size_policy,
            ],
            check=False,
        )
        return completed.returncode

    if open_processes:
        fail("This project is open in Unity. Close that Editor before the full export.")
    if not (target / ".git").is_dir():
        fail(f"Target repository must already contain .git: {target}")
    if shutil.disk_usage(tempfile.gettempdir()).free < MIN_FREE_BYTES:
        fail("At least 6 GiB free space is required on the temporary volume.")

    work = Path(tempfile.mkdtemp(prefix="vibelab-pico-export-"))
    raw = work / "raw"
    stage = work / "processed"
    logs = work / "logs"
    before_apk = work / "before.apk"
    after_apk = work / "after.apk"
    validation_json = work / "apk-validation.json"
    project_validation_json = work / "project-validation.json"
    lock = project / ".vibelab-export.lock"
    editor_directory = project / "Assets" / "Editor"
    editor_directory_existed = editor_directory.exists()
    temporary_export = editor_directory / "VibeLabExportSkill.cs"
    temporary_meta = Path(str(temporary_export) + ".meta")
    success = False
    lock_fd: Optional[int] = None

    try:
        try:
            lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            fail(f"Another VibeLab export may be running. Lock exists: {lock}")
        editor_directory.mkdir(parents=True, exist_ok=True)
        if temporary_export.exists():
            fail(f"Temporary Unity export entry already exists: {temporary_export}")
        shutil.copy2(export_template, temporary_export)
        raw.mkdir(parents=True)
        stage.mkdir(parents=True)
        logs.mkdir(parents=True)

        run_logged(
            unity,
            [
                "-batchmode",
                "-nographics",
                "-quit",
                "-projectPath",
                str(project),
                "-buildTarget",
                "Android",
                "-logFile",
                str(logs / "unity-compile.log"),
            ],
            logs / "unity-compile-process.log",
        )
        export_env = os.environ.copy()
        export_env["VIBELAB_EXPORT_DIR"] = str(raw)
        run_logged(
            unity,
            [
                "-batchmode",
                "-nographics",
                "-projectPath",
                str(project),
                "-buildTarget",
                "Android",
                "-executeMethod",
                "VibeLabExport.Run",
                "-logFile",
                str(logs / "unity-export.log"),
                "-quit",
            ],
            logs / "unity-export-process.log",
            env=export_env,
        )
        if not (raw / "unityLibrary").is_dir():
            fail("Unity did not produce a Gradle unityLibrary module.")
        copy_tree(raw, stage)
        (stage / "local.properties").write_text(
            f"sdk.dir={str(sdk).replace(os.sep, '/')}\n",
            encoding="ascii",
        )

        gradle_args = [
            "-classpath",
            str(gradle_launcher),
            "org.gradle.launcher.GradleMain",
            "-p",
            str(stage),
            "--no-daemon",
            "--console=plain",
            "--stacktrace",
        ]
        run_logged(
            java,
            [
                *gradle_args,
                ":unityLibrary:buildIl2Cpp",
                "--rerun-tasks",
            ],
            logs / "gradle-il2cpp.log",
            cwd=stage,
        )
        il2cpp = (
            stage
            / "unityLibrary"
            / "src"
            / "main"
            / "jniLibs"
            / "arm64-v8a"
            / "libil2cpp.so"
        )
        if not il2cpp.is_file():
            fail("The IL2CPP prebuild did not produce libil2cpp.so.")
        il2cpp_hash = sha256_file(il2cpp)

        run_logged(
            java,
            [*gradle_args, "assembleRelease"],
            logs / "gradle-before.log",
            cwd=stage,
        )
        release_apk = (
            stage
            / "launcher"
            / "build"
            / "outputs"
            / "apk"
            / "release"
            / "launcher-release.apk"
        )
        if not release_apk.is_file():
            fail(f"Release APK was not produced: {release_apk}")
        shutil.copy2(release_apk, before_apk)

        update_unity_library_gradle(stage / "unityLibrary" / "build.gradle")
        set_gradle_property(stage / "gradle.properties", "unityProjectPath", "")
        set_gradle_property(stage / "gradle.properties", "unity.projectPath", "")
        shutil.rmtree(stage / "unityLibrary" / "src" / "main" / "Il2CppOutputProject")
        for build_directory in (
            stage / "launcher" / "build",
            stage / "unityLibrary" / "build",
        ):
            if build_directory.exists():
                shutil.rmtree(build_directory)

        run_logged(
            java,
            [*gradle_args, "assembleRelease"],
            logs / "gradle-after.log",
            cwd=stage,
        )
        if not release_apk.is_file():
            fail("Post-slim release APK was not produced.")
        shutil.copy2(release_apk, after_apk)

        validator_args = [
            sys.executable,
            str(validator),
            "--before-apk",
            str(before_apk),
            "--after-apk",
            str(after_apk),
            "--expected-il2cpp",
            il2cpp_hash,
            "--zipalign",
            str(zipalign),
            "--readelf",
            str(readelf),
            "--gradle-log",
            str(logs / "gradle-after.log"),
            "--page-size-policy",
            args.page_size_policy,
            "--json-output",
            str(validation_json),
        ]
        completed = subprocess.run(validator_args, check=False)
        if completed.returncode != 0:
            fail("APK validation failed.")

        source_properties = (ndk / "source.properties").read_text(
            encoding="utf-8-sig"
        )
        ndk_match = re.search(
            r"^Pkg\.Revision\s*=\s*(\S+)\s*$",
            source_properties,
            re.MULTILINE,
        )
        if not ndk_match:
            fail("Cannot read the Unity NDK version.")
        ndk_version = ndk_match.group(1)
        write_prebuilt_manifest(stage, unity_version, ndk_version, il2cpp_hash)
        remove_generated_outputs(stage)

        completed = subprocess.run(
            [
                sys.executable,
                str(validator),
                "--project",
                str(stage),
                "--manifest",
                str(stage / ".vibelab-prebuilt.json"),
                "--page-size-policy",
                args.page_size_policy,
                "--json-output",
                str(project_validation_json),
            ],
            check=False,
        )
        if completed.returncode != 0:
            fail("Processed project validation failed.")

        sync_target(stage, target)
        stage_inventory = file_inventory(stage)
        target_inventory = file_inventory(target, exclude_git=True)
        if stage_inventory != target_inventory:
            fail("Target repository inventory differs from processed staging.")

        with (logs / "target-validation.log").open("w", encoding="utf-8") as stream:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(validator),
                    "--project",
                    str(target),
                    "--manifest",
                    str(target / ".vibelab-prebuilt.json"),
                    "--page-size-policy",
                    args.page_size_policy,
                ],
                text=True,
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=False,
            )
        if completed.returncode != 0:
            fail("Target repository validation failed.")

        apk_validation = json.loads(validation_json.read_text(encoding="utf-8"))
        first_apk = next(iter(apk_validation["apks"].values()))
        properties = gradle_properties(stage / "gradle.properties")
        write_report(
            report,
            {
                "date": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "target_repo": str(target),
                "host_platform": host,
                "unity_version": unity_version,
                "application_id": properties["unity.applicationId"],
                "min_sdk": properties["unity.minSdkVersion"],
                "target_sdk": properties["unity.targetSdkVersion"],
                "ndk_version": ndk_version,
                "il2cpp_hash": il2cpp_hash,
                "native_library_count": first_apk["native_library_count"],
                "warnings": apk_validation["warnings"],
                "file_count": len(stage_inventory),
            },
            args.page_size_policy,
        )
        success = True
        print(
            json.dumps(
                {
                    "ok": True,
                    "host_platform": host,
                    "target_repo": str(target),
                    "report": str(report),
                    "file_count": len(stage_inventory),
                    "il2cpp_sha256": il2cpp_hash,
                    "validation_warnings": len(apk_validation["warnings"]),
                    "committed": False,
                    "pushed": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    finally:
        for temporary in (temporary_export, temporary_meta):
            if temporary.exists():
                temporary.unlink()
        if (
            not editor_directory_existed
            and editor_directory.exists()
            and not any(editor_directory.iterdir())
        ):
            editor_directory.rmdir()
            editor_meta = Path(str(editor_directory) + ".meta")
            if editor_meta.exists():
                editor_meta.unlink()
        if lock_fd is not None:
            os.close(lock_fd)
        if lock.exists():
            lock.unlink()
        if success and not args.keep_work_dir:
            shutil.rmtree(work, ignore_errors=True)
        elif not success:
            print(
                f"Export failed. Diagnostic workspace retained at {work}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
