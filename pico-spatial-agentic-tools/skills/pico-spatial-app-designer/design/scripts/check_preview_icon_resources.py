#!/usr/bin/env python3
"""Check static Preview icon references against its runtime and local files; no JS execution."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from urllib.request import url2pathname
import xml.etree.ElementTree as ET


PAIRED = {
    "sui-button",
    "sui-toggle-button",
    "sui-chip",
    "sui-button-chip",
    "sui-toggleable-chip",
    "sui-removable-chip",
    "sui-list-item",
    "sui-side-navigation-item",
    "sui-menu-item",
    "sui-text-field",
    "sui-text-area",
}
SINGLE = {
    "sui-icon-button",
    "sui-toggle-icon-button",
    "sui-option",
    "sui-symbol-slider",
    "sui-alert-dialog",
}
VOID = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class PreviewParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        node = dict(tag=tag, attrs=dict(attrs), line=self.getpos()[0], children=[])
        self.nodes.append(node)
        if self.stack:
            self.stack[-1]["children"].append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break


def local_file(reference, base):
    """Use document URL semantics, independent of the checker's working directory."""
    parsed = urlsplit(urljoin(base, reference))
    if parsed.scheme != "file" or parsed.netloc not in ("", "localhost"):
        raise ValueError("Cannot statically check a non-local URL: " + reference)
    return Path(url2pathname(parsed.path))


def check_preview(preview):
    preview = Path(preview).resolve()
    issues, refs = [], []

    def issue(code, node, attribute, message, level="error"):
        issues.append(
            dict(
                level=level,
                code=code,
                path=str(preview),
                line=node["line"],
                element=node["attrs"].get("id", node["tag"]),
                attribute=attribute,
                message=message,
            )
        )

    parser = PreviewParser()
    try:
        parser.feed(preview.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        issue("preview-file", dict(line=1, tag="document", attrs={}), "", str(exc))
        return issues
    document_url = preview.as_uri()
    base = next(
        (
            urljoin(document_url, n["attrs"]["href"])
            for n in parser.nodes
            if n["tag"] == "base" and n["attrs"].get("href")
        ),
        document_url,
    )

    def add(node, attr, kind="name"):
        value = node["attrs"].get(attr)
        if value:
            refs.append((node, attr, value, kind))

    def slot_children(node, slot):
        return [child for child in node["children"] if child["attrs"].get("slot", "") == slot]

    def custom_images(node):
        if node["tag"] == "img":
            if node["attrs"].get("src"):
                add(node, "src", "file")
            else:
                issue(
                    "icon-file",
                    node,
                    "src",
                    "Custom icon image needs a local src; review dynamic sources manually.",
                )
        for child in node["children"]:
            custom_images(child)

    for node in parser.nodes:
        tag, attrs = node["tag"], node["attrs"]
        if tag == "sui-icon":
            if attrs.get("src"):
                add(node, "src", "file")
            else:
                add(node, "name" if "name" in attrs else "glyph")
        elif tag in SINGLE:
            custom = (
                slot_children(node, "")
                if tag in {"sui-icon-button", "sui-toggle-icon-button"}
                else []
            )
            if custom:
                for child in custom:
                    custom_images(child)
            else:
                add(node, "icon")
        if tag in PAIRED or tag == "sui-link":
            for slot in ("trailing",) if tag == "sui-link" else ("leading", "trailing"):
                custom = slot_children(node, slot)
                if custom:
                    for child in custom:
                        custom_images(child)
                else:
                    add(node, slot + "-icon")
        if tag in {"sui-circular-progress", "sui-symbolic-circular-progress"}:
            add(node, "symbol")
        if tag in {"sui-segment-control", "sui-side-navigation", "sui-tab-bar"}:
            for name in (attrs.get("icons") or "").split(","):
                if name.strip():
                    refs.append((node, "icons", name.strip(), "name"))

    registries = None
    if any(kind == "name" for _, _, _, kind in refs):
        scripts = [
            n
            for n in parser.nodes
            if n["tag"] == "script"
            and n["attrs"].get("src")
            and Path(urlsplit(n["attrs"]["src"]).path).name == "components.js"
        ]
        try:
            if len(scripts) != 1:
                raise ValueError("Expected one referenced components.js runtime for named icons.")
            runtime = local_file(scripts[0]["attrs"]["src"], base)
            source = runtime.read_text(encoding="utf-8")
            registries = {}
            for key in ("ICON_ALIASES", "ICONS", "GLYPHS"):
                match = re.search(r"\bconst\s+" + key + r"\s*=\s*", source)
                if not match:
                    raise ValueError("Runtime registry unavailable: " + key)
                registry, _ = json.JSONDecoder().raw_decode(source[match.end() :])
                if not isinstance(registry, dict):
                    raise ValueError("Runtime registry must be an object: " + key)
                registries[key] = registry
        except (OSError, UnicodeError, ValueError) as exc:
            registries = None
            node = scripts[0] if scripts else dict(line=1, tag="document", attrs={})
            issue("icon-runtime", node, "src", str(exc))

    for node, attr, value, kind in refs:
        if kind == "file":
            try:
                target = local_file(value, base)
                if not target.is_file():
                    raise ValueError("Icon file does not exist: " + str(target))
                if not target.stat().st_size:
                    raise ValueError("Icon file is empty: " + str(target))
                if target.suffix.lower() == ".svg":
                    root = ET.parse(target).getroot()
                    if root.tag not in ("svg", "{http://www.w3.org/2000/svg}svg"):
                        raise ValueError("Icon file is not an SVG: " + str(target))
            except (OSError, ValueError, ET.ParseError) as exc:
                issue("icon-file", node, attr, str(exc))
        elif registries is not None:
            icon_id = registries["ICON_ALIASES"].get(value)
            if icon_id not in registries["ICONS"] and value not in registries["GLYPHS"]:
                issue("icon-name", node, attr, "Unknown or ambiguous icon name/ID: " + value)
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preview", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    issues = check_preview(args.preview)
    report = dict(
        status="FAIL" if issues else "PASS",
        scope="static-html-icon-references",
        errors=len(issues),
        issues=issues,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in issues:
            print(
                f"{item['path']}:{item['line']} #{item['element']} {item['attribute']}: {item['message']}"
            )
        print(
            f"[preview-icons] {report['status']} errors={len(issues)} (static HTML references only)"
        )
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
