#!/usr/bin/env python3
"""Check local source candidates, reachable Git history, or a Spatial APK without printing contents."""

import argparse
import json
import re
import subprocess
import zipfile
from pathlib import Path

# Recognizable developer locations, not URLs, Android runtime paths or project-relative paths.
HOST_PATH = (
    r"(^|[^[:alnum:]_./:\\-])((file:/+)?/(Users|home|root|Volumes|private/tmp|private/var/folders|var/folders)/"
    r"[^[:space:]]|[A-Za-z]:[/\\]+[^[:space:]]|"
    r"[\\]{2,}[^[:space:]\\/\"<>|]+[\\/]+[^[:space:]\\/\"<>|]+)"
)
PROVENANCE_PATH = (
    r'"(path|scenesPath|entryScene)"[[:space:]]*:[[:space:]]*"(file:|/|[A-Za-z]:[/\\]|\\\\)'
)
PROVENANCE_SCHEMA = "spatialcraft.editor-pack-provenance/v1"
PROVENANCE_FILES = ":(glob)**/*.provenance.json"
ASSET_PROVENANCE = ":(glob)**/src/*/assets/**/*.provenance.json"
SOURCE_EXCLUSIONS = (":(exclude,glob)**/.pico-env.json",)
MAX_SCENES_BYTES = 16 * 1024 * 1024
SCENE_PATH_FIELDS = {
    "path",
    "sourcePath",
    "bundlePath",
    "scenesPath",
    "entryScene",
    "entry_scene",
    "activeScenePath",
    "active_scene_path",
    "runtimeSceneRoot",
}
ABSOLUTE_PATH = re.compile(r"^(?:[/\\]|[A-Za-z]:[/\\]|file:)", re.IGNORECASE)
COMMIT_ID = re.compile(r"^[0-9a-f]{40,64}$")


class InspectionError(Exception):
    pass


def git(root, args, *, grep=False):
    result = subprocess.run(
        ["git", "--no-replace-objects", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0 and not (grep and result.returncode == 1):
        raise InspectionError(f"git-{args[0]}-failed")
    return result.stdout


def scan_git(root, revisions, findings):
    for pattern, paths, category, fixed in (
        (HOST_PATH, (), "host-absolute-path", False),
        (PROVENANCE_PATH, (PROVENANCE_FILES,), "host-absolute-path", False),
        (PROVENANCE_SCHEMA, (ASSET_PROVENANCE,), "editor-provenance-in-assets", True),
    ):
        worktree = revisions is None
        output = git(
            root,
            [
                "grep",
                "--no-color",
                "--no-textconv",
                "-I",
                "-l",
                "-z",
                "-F" if fixed else "-E",
                "-e",
                pattern,
                *(["--untracked", "--exclude-standard"] if worktree else revisions),
                "--",
                *paths,
                *SOURCE_EXCLUSIONS,
            ],
            grep=True,
        )
        for entry in output.decode("utf-8", errors="replace").split("\0"):
            if not entry:
                continue
            commit, file = (None, entry) if worktree else entry.split(":", 1)
            finding = {"category": category, "file": file}
            if commit:
                finding["commit"] = commit
            findings.setdefault((category, file), finding)


def scan_revision(root, revision, findings):
    if git(root, ["rev-parse", "--is-shallow-repository"]).strip() == b"true":
        raise InspectionError("incomplete-git-history")
    head = git(root, ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"])
    head = head.decode("ascii").strip()
    if not COMMIT_ID.fullmatch(head):
        raise InspectionError("invalid-commit")
    commits = git(root, ["rev-list", head]).decode("ascii").splitlines()
    for i in range(0, len(commits), 32):
        scan_git(root, commits[i : i + 32], findings)
    return head


def scenes_contains_absolute_path(manifest):
    pending = [manifest]
    while pending:
        item = pending.pop()
        if isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, dict):
            for key, value in item.items():
                if (
                    key in SCENE_PATH_FIELDS
                    and isinstance(value, str)
                    and ABSOLUTE_PATH.match(value)
                ):
                    return True
                if isinstance(value, (list, dict)):
                    pending.append(value)
    return False


def scan_apk(apk, findings):
    with zipfile.ZipFile(apk) as archive:
        for entry in archive.infolist():
            file = entry.filename
            if file.startswith("assets/") and file.endswith(".provenance.json"):
                with archive.open(entry) as stream:
                    # Generated provenance is small; only the schema marker is needed.
                    if PROVENANCE_SCHEMA.encode("ascii") in stream.read(4096):
                        category = "editor-provenance-in-assets"
                        findings[(category, file)] = {"category": category, "file": file}
            elif file.startswith("assets/") and file.endswith(".scenes.json"):
                if entry.file_size > MAX_SCENES_BYTES:
                    category = "scenes-metadata-too-large"
                else:
                    with archive.open(entry) as stream:
                        payload = stream.read(MAX_SCENES_BYTES + 1)
                    if len(payload) > MAX_SCENES_BYTES:
                        category = "scenes-metadata-too-large"
                    else:
                        try:
                            manifest = json.loads(payload)
                        except (ValueError, RecursionError):
                            category = "invalid-scenes-metadata"
                        else:
                            if not scenes_contains_absolute_path(manifest):
                                continue
                            category = "host-absolute-path"
                findings[(category, file)] = {"category": category, "file": file}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Git publish root")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--worktree", action="store_true", help="scan tracked and non-ignored source")
    mode.add_argument("--revision", help="scan all commits reachable from this local revision")
    mode.add_argument(
        "--apk",
        type=Path,
        help="scan Android APK assets for Editor provenance and absolute scene paths",
    )
    args = parser.parse_args()
    findings = {}
    result = {"ok": False, "findings": []}
    try:
        if args.apk:
            scan_apk(args.apk, findings)
        else:
            root = Path(
                git(args.project, ["rev-parse", "--show-toplevel"]).decode("utf-8").rstrip("\n")
            )
            if args.worktree:
                scan_git(root, None, findings)
            else:
                result["commit"] = scan_revision(root, args.revision, findings)
    except (OSError, ValueError, InspectionError, zipfile.BadZipFile) as error:
        result["error"] = str(error) if isinstance(error, InspectionError) else "inspection-failed"
        print(json.dumps(result))
        return 2
    result["findings"] = sorted(
        findings.values(), key=lambda item: (item["file"], item["category"])
    )
    result["ok"] = not findings
    print(json.dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
