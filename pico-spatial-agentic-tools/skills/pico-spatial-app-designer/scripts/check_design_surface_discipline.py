#!/usr/bin/env python3
"""Check design-spec.json surface, color-token, and typography discipline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


COLOR_ROLES = {
    "fillPrimary",
    "fillSecondary",
    "fillTertiary",
    "fillLight",
    "labelPrimaryLight",
    "labelPrimary",
    "labelSecondary",
    "labelTertiary",
    "labelQuaternary",
    "lightenHover",
    "lightenPressed",
    "error",
    "alert",
    "passable",
    "interaction",
    "dividerLine",
}

TYPOGRAPHY_BASE_CEILING_DP = 20
SPATIAL_UI_TYPOGRAPHY_SIZES_DP = {
    "displayLarge": 40,
    "displayMedium": 32,
    "displaySmall": 28,
    "headlineLarge": 24,
    "headlineMedium": 20,
    "headlineSmall": 16,
    "titleLarge": 20,
    "titleMedium": 16,
    "titleSmall": 14,
    "labelLarge": 14,
    "labelMedium": 12,
    "bodyLarge": 16,
    "bodyLargeMultiline": 16,
    "bodyMedium": 14,
    "bodyMediumMultiline": 14,
    "bodySmall": 12,
}
COMPONENT_OWNED_TEXT_SLOT_COMPONENTS = {
    "sui-side-navigation",
    "sui-title-bar",
}
AUTHORITATIVE_STYLE_SOURCES = {
    "user",
    "figma",
    "screenshot",
}
INTERACTIVE_PART_STATES = {
    "active",
    "checked",
    "focused",
    "selected",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design_spec", type=Path)
    return parser.parse_args()


def is_app_surface(node: dict[str, Any]) -> bool:
    appearance = node.get("appearance")
    if not isinstance(appearance, dict):
        return False
    fill = appearance.get("fill")
    return isinstance(fill, str) and bool(fill.strip())


def has_fill(appearance: Any) -> bool:
    if not isinstance(appearance, dict):
        return False
    fill = appearance.get("fill")
    return isinstance(fill, str) and bool(fill.strip())


def check_part_appearance(
    appearance: Any,
    location: str,
    color_tokens: set[str],
    errors: list[str],
) -> None:
    if not isinstance(appearance, dict):
        return
    if "borderWidthDp" in appearance or "borderColor" in appearance:
        errors.append(
            f"{location} declares a border field; borderWidthDp and borderColor "
            "are not part of the app appearance contract"
        )
    if "material" in appearance:
        errors.append(
            f"{location} declares material; material is system-owned and is not "
            "part of the app appearance contract"
        )
    for field in ("fill", "foreground"):
        token = appearance.get(field)
        if isinstance(token, str) and token and token not in color_tokens:
            errors.append(f"{location}.{field} references unknown color token {token!r}")


def typography_size_dp(theme: Any, token: str) -> int | float | None:
    typography = theme.get("typography") if isinstance(theme, dict) else None
    style = typography.get(token) if isinstance(typography, dict) else None
    size = style.get("sizeDp") if isinstance(style, dict) else None
    if isinstance(size, (int, float)) and not isinstance(size, bool):
        return size
    return SPATIAL_UI_TYPOGRAPHY_SIZES_DP.get(token)


def collect_layout_text_descendants(
    node_id: str,
    nodes: dict[str, dict[str, Any]],
    collected: set[str],
    path: set[str],
) -> None:
    if node_id in path:
        return
    node = nodes.get(node_id)
    if node is None:
        return
    if node.get("kind") == "text":
        collected.add(node_id)
        return
    if node.get("kind") != "layout":
        return
    children = node.get("children")
    if not isinstance(children, list):
        return
    next_path = {*path, node_id}
    for child_id in children:
        if isinstance(child_id, str):
            collect_layout_text_descendants(child_id, nodes, collected, next_path)


def has_authoritative_style_evidence(node: dict[str, Any]) -> bool:
    evidence = node.get("styleOverrideEvidence")
    return (
        isinstance(evidence, dict)
        and evidence.get("source") in AUTHORITATIVE_STYLE_SOURCES
        and isinstance(evidence.get("reference"), str)
        and bool(evidence["reference"].strip())
    )


SURFACE_TITLE_COMPONENTS = {
    "sui-subwindow",
    "sui-spatial-popup",
    "sui-alert-dialog",
    "sui-basic-alert-dialog",
    "sui-date-picker-dialog",
    "sui-sheet",
    "sui-basic-sheet",
    "sui-head-image-sheet",
}


def resolve_surface_titles(value: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Resolve explicit headings through unique ancestry, never from prose/name heuristics.

    Shared by design validation and the Kotlin verifier so both grant the same
    narrow exemption. Invalid, detached, duplicate, or ambiguous titles fail closed.
    """
    nodes: dict[str, dict[str, Any]] = {}
    duplicate_ids: set[str] = set()
    for node in value.get("nodes", []):
        if isinstance(node, dict) and isinstance(node.get("id"), str):
            if node["id"] in nodes:
                duplicate_ids.add(node["id"])
            nodes[node["id"]] = node
    parents: dict[str, list[str]] = {}
    for node_id, node in nodes.items():
        for child in node.get("children", []) if isinstance(node.get("children"), list) else []:
            if isinstance(child, str):
                parents.setdefault(child, []).append(node_id)
    titles: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    owners: dict[str, list[str]] = {}
    for node_id, node in nodes.items():
        if "textRole" not in node:
            continue
        if node.get("textRole") != "surface_title" or node.get("kind") != "text":
            errors.append(f"node {node_id!r} has invalid textRole; surface_title is only for text")
            continue
        style = node.get("textStyle")
        token = style.get("typography") if isinstance(style, dict) else None
        if (
            not isinstance(token, str)
            or token not in SPATIAL_UI_TYPOGRAPHY_SIZES_DP
            or not isinstance(node.get("content"), str)
            or not node["content"].strip()
        ):
            errors.append(
                f"surface_title {node_id!r} needs nonempty content and an exact typography token"
            )
            continue
        current = node_id
        visited: set[str] = set()
        owner = None
        in_native_title = False
        while True:
            if current in visited or current in duplicate_ids:
                owner = None
                break
            visited.add(current)
            ancestors = parents.get(current, [])
            if not ancestors:
                break
            if len(ancestors) != 1:
                owner = None
                break
            current = ancestors[0]
            ancestor = nodes[current]
            if owner is None and ancestor.get("component") in COMPONENT_OWNED_TEXT_SLOT_COMPONENTS:
                in_native_title = True
            if (
                owner is None
                and ancestor.get("kind") == "spatialui"
                and ancestor.get("component") in SURFACE_TITLE_COMPONENTS
            ):
                owner = current
            # Continue to the root to reject cycles or ambiguous ownership above
            # the nearest surface too; a malformed graph is never an exemption.
        if in_native_title:
            errors.append(f"surface_title {node_id!r} cannot be inside a native title component")
            continue
        if owner is None:
            errors.append(
                f"surface_title {node_id!r} needs unique ancestry to a Subwindow, dialog, Sheet, or popup"
            )
            continue
        if nodes[owner].get("component") == "sui-sheet":
            errors.append(
                f"surface_title {node_id!r} cannot replace Sheet's native short title slot"
            )
            continue
        titles[node_id] = {"owner": owner, "typography": token}
        owners.setdefault(owner, []).append(node_id)
    for owner, node_ids in owners.items():
        if len(node_ids) > 1:
            errors.append(
                f"surface {owner!r} has multiple surface_title nodes; use one bound title node"
            )
            for node_id in node_ids:
                titles.pop(node_id, None)
    return titles, errors


def check_subwindow_structure(value: dict[str, Any]) -> list[str]:
    """Check declared window regions, not labels or generated Kotlin structure."""
    nodes = {
        node["id"]: node
        for node in value["nodes"]
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }
    parents: dict[str, list[str]] = {}
    for node_id, node in nodes.items():
        for child in node.get("children", []) if isinstance(node.get("children"), list) else []:
            if isinstance(child, str):
                parents.setdefault(child, []).append(node_id)
    errors: list[str] = []

    def props(node: dict[str, Any]) -> dict[str, Any]:
        result = node.get("props")
        return result if isinstance(result, dict) else {}

    def ancestry(node_id: str) -> list[str] | None:
        chain: list[str] = []
        while node_id in nodes and node_id not in chain:
            chain.append(node_id)
            owners = parents.get(node_id, [])
            if not owners:
                return chain
            if len(owners) != 1:
                return None
            node_id = owners[0]
        return None

    def owned_path(node_id: str, owner: str) -> list[str] | None:
        chain = ancestry(node_id)
        if chain is None or owner not in chain:
            return None
        path = chain[: chain.index(owner)]
        if any(nodes[item].get("component") in SURFACE_TITLE_COMPONENTS for item in path):
            return None
        return path

    for bar_id, bar in nodes.items():
        if bar.get("kind") != "spatialui" or bar.get("component") != "sui-title-bar":
            continue
        subtitle_id = props(bar).get("subtitle-node-id")
        if subtitle_id is None:
            continue
        chain = ancestry(subtitle_id) if isinstance(subtitle_id, str) else None
        subtitle = nodes.get(subtitle_id) if isinstance(subtitle_id, str) else None
        slots = [
            child
            for child in bar.get("children", [])
            if child in nodes and props(nodes[child]).get("slot") == "title"
        ]
        if (
            not subtitle
            or subtitle.get("kind") != "text"
            or not isinstance(subtitle.get("content"), str)
            or not subtitle["content"].strip()
            or chain is None
            or bar_id not in chain
            or not any(slot in chain[: chain.index(bar_id)] for slot in slots)
            or any(nodes[item].get("kind") != "layout" for item in chain[1 : chain.index(bar_id)])
        ):
            errors.append(
                f"TitleBar {bar_id!r} subtitle-node-id must reference nonempty text in its title slot"
            )

    for window_id, window in nodes.items():
        if window.get("kind") != "spatialui" or window.get("component") != "sui-subwindow":
            continue
        prefix = f"Subwindow {window_id!r}"
        owned = {
            node_id: path
            for node_id in nodes
            if (path := owned_path(node_id, window_id)) is not None
        }
        bars = [
            item
            for item in owned
            if nodes[item].get("kind") == "spatialui"
            and nodes[item].get("component") == "sui-title-bar"
        ]
        if len(bars) != 1:
            errors.append(f"{prefix} needs exactly one uniquely owned TitleBar")
        position = props(window).get("title-position")
        title_id = props(window).get("title-node-id")
        if position not in ("titlebar", "content") or not isinstance(title_id, str):
            errors.append(
                f"{prefix} must declare title-position and title-node-id; update legacy spec"
            )
            continue
        title = nodes.get(title_id)
        title_path = owned.get(title_id)
        if (
            not title
            or title_path is None
            or title.get("kind") != "text"
            or not isinstance(title.get("content"), str)
            or not title["content"].strip()
        ):
            errors.append(
                f"{prefix} title-node-id must reference its uniquely owned nonempty text title"
            )
            continue
        if len(bars) != 1:
            continue
        bar_id = bars[0]
        bar = nodes[bar_id]
        bar_path = owned[bar_id]
        if any(
            nodes[parent].get("kind") != "layout"
            or props(nodes[parent]).get("slot") in ("content", "bottom-actions")
            for parent in bar_path[1:]
        ):
            errors.append(
                f"{prefix} TitleBar must be a header outside its content and bottom actions"
            )
        for child, parent in zip(bar_path, [*bar_path[1:], window_id]):
            children = nodes[parent].get("children", [])
            if not children or children[0] != child:
                errors.append(f"{prefix} TitleBar must be the first window region")
                break
        if props(bar).get("title-alignment") not in ("center", "center-in-bar"):
            errors.append(f"{prefix} TitleBar must declare the existing title-alignment policy")
        contents = [
            item
            for item, path in owned.items()
            if nodes[item].get("kind") == "layout"
            and props(nodes[item]).get("slot") == "content"
            and not any(nodes[parent].get("kind") != "layout" for parent in path[1:])
        ]
        if len(contents) != 1:
            errors.append(
                f"{prefix} needs one content layout with props.slot=content outside TitleBar"
            )
        title_slots = [
            item
            for item in bar.get("children", [])
            if item in owned and props(nodes[item]).get("slot") == "title"
        ]
        in_title_slot = any(slot in title_path for slot in title_slots)
        if position == "titlebar":
            if (
                len(title_slots) != 1
                or not in_title_slot
                or title.get("textRole") == "surface_title"
            ):
                errors.append(
                    f"{prefix} titlebar title must occupy the title slot without surface_title"
                )
        else:
            if bar_id in title_path or not any(item in title_path for item in contents):
                errors.append(
                    f"{prefix} content title must occupy its content region outside TitleBar"
                )
            if title.get("textRole") != "surface_title":
                errors.append(f"{prefix} content title must declare surface_title")
            if title_slots:
                errors.append(f"{prefix} content title must not also declare a TitleBar title slot")
            # The title must be the first item, allowing transparent layout wrappers.
            for child, parent in zip(title_path, title_path[1:]):
                if parent in contents or nodes[parent].get("kind") == "layout":
                    children = nodes[parent].get("children", [])
                    if not children or children[0] != child:
                        errors.append(f"{prefix} content title must be the first content item")
                        break
                if parent in contents:
                    break
        for node_id, path in owned.items():
            if nodes[node_id].get("textRole") == "surface_title" and (
                position != "content" or node_id != title_id
            ):
                errors.append(f"{prefix} only its declared content title may use surface_title")
            action = props(nodes[node_id]).get("navigation-action")
            if action is None:
                continue
            leading = [
                item
                for item in bar.get("children", [])
                if item in owned and props(nodes[item]).get("slot") == "leading"
            ]
            if (
                action not in ("back", "close")
                or nodes[node_id].get("component") != "sui-icon-button"
                or not any(item in path for item in leading)
            ):
                errors.append(
                    f"{prefix} navigation action {node_id!r} must be a back/close Icon Button in leading"
                )
    return errors


def main() -> int:
    args = parse_args()
    try:
        value = json.loads(args.design_spec.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[error] surface-discipline-invalid-json: {exc}")
        return 1

    if not isinstance(value, dict) or not isinstance(value.get("nodes"), list):
        print("[error] surface-discipline-invalid-root: design-spec.json must contain nodes[]")
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    surface_titles, title_errors = resolve_surface_titles(value)
    errors.extend(title_errors)
    errors.extend(check_subwindow_structure(value))
    for surface in value.get("surfaces", []):
        if not isinstance(surface, dict):
            continue
        background = surface.get("windowBackground")
        evidence = surface.get("windowBackgroundEvidence")
        if "windowBackground" in surface and (
            surface.get("type") != "planar" or background not in ("material", "transparent")
        ):
            errors.append("windowBackground is a Planar-only material or transparent setting")
        if background == "transparent" and (not isinstance(evidence, str) or not evidence.strip()):
            errors.append(
                "transparent Planar window requires explicit user windowBackgroundEvidence"
            )
        if background != "transparent" and "windowBackgroundEvidence" in surface:
            errors.append("windowBackgroundEvidence is only valid for transparent Planar windows")
    theme = value.get("theme")
    if isinstance(theme, dict) and "rootMaterial" in theme:
        errors.append(
            "theme declares rootMaterial; window material is system-owned and "
            "is not part of the design contract"
        )
    color_scheme = theme.get("colorScheme") if isinstance(theme, dict) else None
    if isinstance(color_scheme, dict):
        for role in sorted(COLOR_ROLES):
            entry = color_scheme.get(role)
            if (
                not isinstance(entry, dict)
                or entry.get("source") != "vibrant"
                or entry.get("role") != role
            ):
                errors.append(
                    f"theme.colorScheme.{role} must preserve the same-name SpatialUI "
                    "Vibrant role; put custom colors in theme.brandColors"
                )
    color_tokens = set(COLOR_ROLES)
    brand_colors = theme.get("brandColors") if isinstance(theme, dict) else None
    if isinstance(brand_colors, dict):
        color_tokens.update(key for key in brand_colors if isinstance(key, str))

    nodes: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(value["nodes"]):
        if not isinstance(node, dict) or not isinstance(node.get("id"), str):
            continue
        node_id = node["id"]
        if node_id in nodes:
            errors.append(f"duplicate node id {node_id!r}")
            continue
        nodes[node_id] = node
        text_style = node.get("textStyle")
        typography_token = text_style.get("typography") if isinstance(text_style, dict) else None
        if isinstance(typography_token, str):
            size_dp = typography_size_dp(theme, typography_token)
            if (
                node_id not in surface_titles
                and size_dp is not None
                and size_dp >= TYPOGRAPHY_BASE_CEILING_DP
            ):
                warnings.append(
                    f"node {node_id!r} explicitly uses typography token "
                    f"{typography_token!r} ({size_dp:g}dp), which is at or above "
                    f"Title Large ({TYPOGRAPHY_BASE_CEILING_DP}dp); confirm that "
                    "this visual emphasis is necessary and explain it in design-doc.md"
                )
        appearance = node.get("appearance")
        if isinstance(appearance, dict) and (
            "borderWidthDp" in appearance or "borderColor" in appearance
        ):
            errors.append(
                f"node {node_id!r} declares a border field; borderWidthDp and "
                "borderColor are not part of the app appearance contract"
            )
        if isinstance(appearance, dict) and "material" in appearance:
            errors.append(
                f"node {node_id!r} declares material; material is system-owned "
                "and is not part of the app appearance contract"
            )
        if (
            node.get("kind") in {"layout", "domain_visual"}
            and isinstance(appearance, dict)
            and isinstance(appearance.get("fill"), str)
            and bool(appearance["fill"].strip())
        ):
            errors.append(
                f"structural node {node_id!r} ({node['kind']}) declares fill; "
                "large layout and domain regions must remain transparent"
            )
        parts = node.get("parts")
        if node.get("kind") == "domain_visual" and not parts:
            warnings.append(
                f"node {node_id!r} has no declared parts; inspect the rendered "
                "visual for repeated or independently styled internal regions. "
                "Declare those templates even when transparent, or confirm "
                "that no internal appearance boundary exists"
            )
        if parts is not None and node.get("kind") != "domain_visual":
            errors.append(
                f"node {node_id!r} declares parts but has kind {node.get('kind')!r}; "
                "parts are only valid on domain_visual nodes"
            )
        if isinstance(parts, dict):
            for part_id, part in parts.items():
                if not isinstance(part_id, str) or not isinstance(part, dict):
                    continue
                location = f"node {node_id!r} part {part_id!r} appearance"
                part_appearance = part.get("appearance")
                check_part_appearance(part_appearance, location, color_tokens, errors)
                radius_dp = (
                    part_appearance.get("radiusDp") if isinstance(part_appearance, dict) else None
                )
                if (
                    isinstance(radius_dp, (int, float))
                    and not isinstance(radius_dp, bool)
                    and radius_dp > 0
                    and not has_fill(part_appearance)
                ):
                    warnings.append(
                        f"node {node_id!r} part {part_id!r} declares radiusDp "
                        "but no base appearance.fill; confirm that this rounded "
                        "part is intentionally transparent"
                    )
                states = part.get("states")
                if not isinstance(states, dict):
                    continue
                for state_id, state_appearance in states.items():
                    if not isinstance(state_id, str):
                        continue
                    state_location = (
                        f"node {node_id!r} part {part_id!r} state {state_id!r} appearance"
                    )
                    check_part_appearance(
                        state_appearance,
                        state_location,
                        color_tokens,
                        errors,
                    )
                    if state_id.lower() in INTERACTIVE_PART_STATES and not has_fill(
                        state_appearance
                    ):
                        warnings.append(
                            f"node {node_id!r} part {part_id!r} state {state_id!r} "
                            "has no fill; interactive repeated regions should "
                            "normally declare an explicit state fill"
                        )

    component_owned_text_ids: set[str] = set()
    for node in nodes.values():
        if node.get("component") not in COMPONENT_OWNED_TEXT_SLOT_COMPONENTS:
            continue
        children = node.get("children")
        if not isinstance(children, list):
            continue
        for child_id in children:
            if isinstance(child_id, str):
                collect_layout_text_descendants(
                    child_id,
                    nodes,
                    component_owned_text_ids,
                    set(),
                )

    subtitle_ids = {
        node.get("props", {}).get("subtitle-node-id")
        for node in nodes.values()
        if node.get("component") == "sui-title-bar"
        and isinstance(node.get("props"), dict)
        and isinstance(node["props"].get("subtitle-node-id"), str)
    }
    for node_id, node in nodes.items():
        if node.get("kind") != "text":
            continue
        text_style = node.get("textStyle")
        canonical_subtitle = node_id in subtitle_ids and text_style == {
            "typography": "bodyMedium",
            "color": "labelSecondary",
        }
        if node_id in component_owned_text_ids and not canonical_subtitle:
            if isinstance(text_style, dict) and not has_authoritative_style_evidence(node):
                errors.append(
                    f"component-owned text node {node_id!r} overrides typography/color "
                    "without authoritative evidence; omit textStyle to inherit the "
                    "SpatialUI component default"
                )
        elif isinstance(node.get("content"), str) and not isinstance(text_style, dict):
            errors.append(
                f"app-authored text node {node_id!r} must declare textStyle; only "
                "component-owned slot text may inherit typography and foreground"
            )

    surface_ids = {node_id for node_id, node in nodes.items() if is_app_surface(node)}
    roots: list[str] = []
    for surface in value.get("surfaces", []):
        if isinstance(surface, dict) and isinstance(surface.get("rootNodeId"), str):
            roots.append(surface["rootNodeId"])
    for state in value.get("states", []):
        surface_roots = state.get("surfaceRoots") if isinstance(state, dict) else None
        if isinstance(surface_roots, dict):
            roots.extend(root for root in surface_roots.values() if isinstance(root, str))

    visited: set[tuple[str, str | None]] = set()
    nested_pairs: set[tuple[str, str]] = set()

    def visit(node_id: str, surface_ancestor: str | None, path: set[str]) -> None:
        if node_id in path:
            return
        state = (node_id, surface_ancestor)
        if state in visited:
            return
        visited.add(state)
        node = nodes.get(node_id)
        if node is None:
            return

        next_ancestor = surface_ancestor
        if node_id in surface_ids:
            if surface_ancestor is not None:
                nested_pairs.add((surface_ancestor, node_id))
            next_ancestor = node_id

        children = node.get("children")
        if not isinstance(children, list):
            return
        next_path = {*path, node_id}
        for child_id in children:
            if isinstance(child_id, str):
                visit(child_id, next_ancestor, next_path)

    for root in dict.fromkeys(roots):
        visit(root, None, set())
    for node_id in nodes:
        visit(node_id, None, set())

    for ancestor, descendant in sorted(nested_pairs):
        errors.append(
            f"surface {descendant!r} is nested under app surface {ancestor!r}; "
            "keep the child transparent or remove the ancestor surface"
        )

    node_count = len(nodes)
    if node_count >= 4 and len(surface_ids) / node_count > 0.5:
        warnings.append(
            f"{len(surface_ids)} of {node_count} nodes own a fill; "
            "review for excessive card-like surfaces"
        )

    for message in errors:
        print(f"[error] {message}")
    for message in warnings:
        print(f"[warning] {message}")
    print(
        "[surface-discipline] "
        f"{'FAIL' if errors else 'PASS'} "
        f"errors={len(errors)} warnings={len(warnings)} "
        f"app_surfaces={len(surface_ids)}/{node_count}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
