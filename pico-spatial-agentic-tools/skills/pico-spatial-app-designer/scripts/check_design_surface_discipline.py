#!/usr/bin/env python3
"""Check design-spec.json surface and native color-token discipline."""

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
                check_part_appearance(part.get("appearance"), location, color_tokens, errors)
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
