#!/usr/bin/env python3
"""Validate the Write Spec record; no Preview execution or native fidelity claim.

Adapted from pico-spatial-app-designer/check_design_surface_discipline.py.
Uses Python's standard library, bundled catalogs and Node.js handoff checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

from check_preview_icon_resources import check_preview

REFERENCE = Path(__file__).resolve().parents[1] / 'design-reference'
KINDS = {'layout', 'content', 'spatialui', 'text', 'media', 'domain_visual'}
TITLE_COMPONENTS = {'sui-title-bar', 'sui-side-navigation'}
CUSTOM_TITLE_SURFACES = {'sui-subwindow', 'sui-spatial-popup', 'sui-alert-dialog',
                         'sui-basic-alert-dialog', 'sui-date-picker-dialog',
                         'sui-basic-sheet', 'sui-head-image-sheet'}
WINDOW_COMPONENTS = CUSTOM_TITLE_SURFACES | {'sui-sheet'}
INTERACTIVE_STATES = {'active', 'checked', 'focused', 'selected'}


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def has_fill(appearance):
    return isinstance(appearance, dict) and appearance.get('fill') not in (None, '', 'transparent')


def evidence(node):
    item = node.get('styleOverrideEvidence', {})
    return (isinstance(item, dict) and item.get('source') in {'user', 'figma', 'screenshot'}
            and nonempty(item.get('reference')))


def walk(value, path='$'):
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, f'{path}.{key}')
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f'{path}[{index}]')


class Checker:
    def __init__(self, spec_path, asset_root=None):
        self.base = Path(spec_path).resolve().parent
        self.asset_root = Path(asset_root).resolve() if asset_root else self.base
        self.issues = []
        roles = json.loads((REFERENCE / 'color-roles.json').read_text(encoding='utf-8'))
        tokens = json.loads((REFERENCE / 'tokens.json').read_text(encoding='utf-8'))
        self.roles = {entry['name'] for entry in roles['roles']}
        self.system_colors = self.roles | {entry['name'] for entry in tokens['color']['tokens']}
        self.colors = set(self.system_colors)
        self.type_sizes = {}
        for group in tokens['type']['groups']:
            for style in group['styles']:
                name = style['name']
                camel = re.sub(r'-([a-z])', lambda m: m[1].upper(), name)
                self.type_sizes[camel] = float(style['fontSize'].removesuffix('px'))
        runtime = (REFERENCE / 'runtime/components.js').read_text(encoding='utf-8')
        self.components = set(re.findall(r"(?:register|define)\('([^']+)'", runtime))

    def error(self, code, path, message):
        self.issues.append(dict(level='error', code=code, path=path, message=message))

    def warning(self, code, path, message):
        self.issues.append(dict(level='warning', code=code, path=path, message=message))

    def obj(self, value, path):
        if not isinstance(value, dict):
            self.error('object', path, 'Expected an object.')
            return {}
        return value

    def index(self, value, path, required=False):
        if not isinstance(value, list) or (required and not value):
            self.error('array', path, 'Expected a nonempty array.' if required else 'Expected an array.')
            return {}
        result = {}
        for i, raw in enumerate(value):
            item = self.obj(raw, f'{path}[{i}]')
            key = item.get('id')
            if not nonempty(key):
                self.error('id', f'{path}[{i}]', 'Expected a nonempty string id.')
            elif key in result:
                self.error('duplicate-id', f'{path}[{i}]', f'Duplicate id {key!r}.')
            else:
                result[key] = item
        return result

    def ref(self, value, choices, path):
        if not isinstance(value, str) or value not in choices:
            self.error('reference', path, f'Unresolved reference: {value!r}.')
            return False
        return True

    def file(self, value, path, base=None):
        if not nonempty(value) or '://' in value:
            self.error('file', path, 'Expected a delivered local file path.')
            return None
        target = (base or self.base) / value
        if not target.is_file():
            self.error('file', path, f'File does not exist: {target}.')
            return None
        return target

    def color(self, value, path, transparent=False):
        if transparent and value == 'transparent':
            return
        if not isinstance(value, str) or value not in self.colors:
            self.error('color', path, 'Use a bundled role/token or a separately declared brandColors name.')

    def appearance(self, raw, path, kind):
        value = self.obj(raw, path)
        for key in ('borderWidthDp', 'borderColor', 'material'):
            if key in value:
                self.error('appearance-field', f'{path}.{key}', 'App-painted borders/materials are not allowed; retain system component behavior.')
        for key in set(value) - {'fill', 'foreground', 'radiusDp', 'opacity', 'borderWidthDp', 'borderColor', 'material'}:
            self.error('appearance-field', f'{path}.{key}', 'Unknown appearance field; use the documented fill/foreground/radiusDp/opacity fields.')
        for key in ('fill', 'foreground'):
            if key in value:
                self.color(value[key], f'{path}.{key}', transparent=key == 'fill')
        if has_fill(value) and kind != 'content':
            self.error('background-owner', path, 'Only a local content item/cell may own an app fill; layout, large regions and domain roots stay transparent. Standard controls use supported props.')
        for key in ('radiusDp', 'opacity'):
            if key in value and (not number(value[key]) or value[key] < 0 or (key == 'opacity' and value[key] > 1)):
                self.error('appearance-value', f'{path}.{key}', 'Expected a nonnegative number (opacity: 0–1).')

    def props(self, raw, path, node):
        props = self.obj(raw, path)
        for key, value in props.items():
            if key == 'background' and node.get('kind') == 'spatialui' and node.get('component') == 'sui-attachment-panel':
                if value not in ('transparent', 'material'):
                    self.error('attachment-background', f'{path}.{key}', 'Choose transparent or material.')
                continue
            if key in {'style', 'css', 'background', 'background-image', 'fill'}:
                self.error('raw-style', f'{path}.{key}', 'Use supported component props or appearance.fill; raw styling cannot bypass background checks.')
            if key in {'material', 'surface-color', 'disable-material-background'}:
                self.error('material', f'{path}.{key}', 'Use system material; planar transparency belongs on the surface declaration.')
            elif key == 'tint' or key == 'color' or key.endswith('-color'):
                self.color(value, f'{path}.{key}', transparent=True)
                if node.get('kind') != 'spatialui' and key not in {'color', 'tint'}:
                    self.error('background-owner', f'{path}.{key}', 'Custom fills belong in appearance.fill on a local content node.')
            if key in {'font-weight', 'font-size', 'line-height', 'font-family', 'text-style', 'title-color', 'leading-color', 'trailing-color'}:
                if node.get('component') != 'sui-text' and not evidence(node):
                    self.error('component-text', f'{path}.{key}', 'Keep component text defaults; the optional 700 title override belongs only on its referenced text node.')
        return props

    def shapes(self, value):
        """Reject malformed known fields before graph/style checks use them."""
        def fields(raw, path, types):
            if not isinstance(raw, dict):
                return
            for key, expected in types.items():
                if key in raw and not isinstance(raw[key], expected):
                    self.error('field-type', path + '.' + key, f'Expected {expected.__name__}.')
        for i, node in enumerate(value.get('nodes', []) if isinstance(value.get('nodes'), list) else []):
            path = f'$.nodes[{i}]'
            fields(node, path, dict(kind=str, component=str, textRole=str, content=str,
                   textStyle=dict, props=dict, appearance=dict, layout=dict, bindings=dict,
                   children=list, visualStates=dict, events=dict, parts=dict, regions=dict,
                   styleOverrideEvidence=dict))
            if not isinstance(node, dict):
                continue
            for key in ('props', 'regions'):
                raw = node.get(key, {})
                if isinstance(raw, dict):
                    fields(raw, path + '.' + key, {name: str for name in raw if name.endswith('NodeId') or name.endswith('-node-id')})
            style = node.get('textStyle', {})
            fields(style, path + '.textStyle', dict(typography=str, color=str, overrides=dict))
            fields(node.get('styleOverrideEvidence'), path + '.styleOverrideEvidence', dict(source=str, reference=str))
        return not any(i['level'] == 'error' for i in self.issues)

    def check(self, value):
        value = self.obj(value, '$')
        if not self.shapes(value):
            return self.issues
        if value.get('schemaVersion') != 'write-spec-draft-1':
            self.error('format', '$.schemaVersion', 'Expected write-spec-draft-1.')
        for path, item in walk(value):
            if isinstance(item, str) and re.search(r'__[A-Z][A-Z0-9_]*__', item):
                self.error('placeholder', path, 'Replace the template placeholder before delivery.')
        nodes = self.index(value.get('nodes'), '$.nodes', True)
        surfaces = self.index(value.get('surfaces'), '$.surfaces', True)
        states = self.index(value.get('states'), '$.states', True)
        actions = self.index(value.get('actions'), '$.actions')
        assets = self.index(value.get('assets'), '$.assets')
        self.ref(value.get('initialStateId'), states, '$.initialStateId')
        theme = self.obj(value.get('theme', {}), '$.theme')
        for key in ('rootMaterial', 'typography'):
            if key in theme:
                self.error('theme-override', f'$.theme.{key}', 'Do not redefine system material/type tokens; record local text overrides.')
        brands = self.obj(theme.get('brandColors', {}), '$.theme.brandColors')
        for name, color in brands.items():
            if name in self.system_colors:
                self.error('system-color', f'$.theme.brandColors.{name}', 'A custom name must not shadow a system role/token.')
            elif not isinstance(color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?', color):
                self.error('brand-color', f'$.theme.brandColors.{name}', 'Declare #RRGGBB or #RRGGBBAA.')
            else:
                self.colors.add(name)
        for role, entry in self.obj(theme.get('colorScheme', {}), '$.theme.colorScheme').items():
            if role not in self.roles or entry != {'source': 'vibrant', 'role': role}:
                self.error('system-color', f'$.theme.colorScheme.{role}', 'Omit the system table or preserve the same-name Vibrant reference; custom colors belong in brandColors.')
        metadata = self.obj(value.get('metadata'), '$.metadata')
        preview = self.file(metadata.get('preview'), '$.metadata.preview')
        if preview:
            for issue in check_preview(preview):
                self.error(issue['code'], f"{issue['path']}:{issue['line']} #{issue['element']}.{issue['attribute']}", issue['message'])
        references = metadata.get('references')
        if not isinstance(references, list) or not references:
            self.error('references', '$.metadata.references', 'Record a resolvable reference snapshot.')
        else:
            for i, raw in enumerate(references):
                path = f'$.metadata.references[{i}]'
                ref = self.obj(raw, path)
                target = self.file(ref.get('path'), path + '.path')
                if 'sha256' in ref:
                    if target and ref['sha256'] != hashlib.sha256(target.read_bytes()).hexdigest():
                        self.error('snapshot-hash', path, 'File differs from the recorded sha256; confirm the intended reference revision.')
                elif not nonempty(ref.get('version')):
                    self.error('snapshot-version', path, 'Record sha256 or a resolvable version/snapshot identifier.')
        for aid, action in actions.items():
            if not nonempty(action.get('purpose')):
                self.error('action-result', f'actions[{aid}]', 'Describe the main visible result in purpose; a state machine is not required.')
        for path, item in walk(value.get('dataCases', {}), '$.dataCases'):
            if isinstance(item, dict):
                for key, resource in item.items():
                    if key == 'assetId' or key.endswith('AssetId'):
                        self.ref(resource, assets, path + '.' + key)

        children, parents, props = {}, {nid: [] for nid in nodes}, {}
        for nid, node in nodes.items():
            path = f'nodes[{nid}]'
            if node.get('kind') not in KINDS:
                self.error('node-kind', path, f'Expected one of {sorted(KINDS)}.')
            if node.get('kind') == 'spatialui' and node.get('component') not in self.components:
                self.error('component', path, 'Unknown component identifier in the bundled runtime.')
            raw_children = node.get('children', [])
            children[nid] = []
            if not isinstance(raw_children, list):
                self.error('children', path, 'children must be an array of node IDs.')
            else:
                for child in raw_children:
                    if self.ref(child, nodes, path + '.children'):
                        children[nid].append(child)
                        parents[child].append(nid)
            props[nid] = self.props(node.get('props', {}), path + '.props', node)
            for field in ('layout', 'bindings', 'textBehavior'):
                if field in node:
                    self.obj(node[field], path + '.' + field)
            layout = node.get('layout', {})
            for key, val in layout.items():
                if key in {'background', 'backgroundColor', 'fill', 'material', 'style', 'css'}:
                    self.error('layout-background', path + '.layout.' + key, 'Layout is transparent; appearance belongs to a local content owner.')
                if key.endswith('Dp'):
                    values = val.values() if isinstance(val, dict) and key == 'paddingDp' else [val]
                    if any(not number(v) or v < 0 for v in values):
                        self.error('layout-value', path + '.layout.' + key, 'Expected nonnegative dp values; record placement offsets separately.')
            for field in ('style', 'css', 'material'):
                if field in node or field in props[nid]:
                    self.error('raw-style', path + '.' + field, 'Record supported design fields; raw CSS/material declarations are not native design parameters.')
            if 'appearance' in node:
                self.appearance(node['appearance'], path + '.appearance', node.get('kind'))
            variants = self.obj(node.get('visualStates', {}), path + '.visualStates')
            for state, raw in variants.items():
                variant_path = path + '.visualStates.' + state
                variant = self.obj(raw, variant_path)
                if 'appearance' in variant:
                    self.appearance(variant['appearance'], variant_path + '.appearance', node.get('kind'))
                self.props(variant.get('props', {}), variant_path + '.props', node)
                if 'textStyle' in variant:
                    self.error('state-text-style', variant_path, 'This format records text styles on text nodes; state-dependent text styling needs an explicit supported representation.')
            for event, action in self.obj(node.get('events', {}), path + '.events').items():
                self.ref(action, actions, path + '.events.' + event)
            if 'assetId' in node:
                self.ref(node['assetId'], assets, path + '.assetId')
            bindings = node.get('bindings', {})
            if node.get('kind') == 'media' and 'assetId' not in node and not (isinstance(bindings, dict) and nonempty(bindings.get('assetId'))):
                self.error('media-source', path, 'Record assetId or a descriptive assetId binding and its dataCases resources.')
            parts = self.obj(node.get('parts', {}), path + '.parts')
            if 'parts' in node and node.get('kind') != 'domain_visual':
                self.error('parts-owner', path, 'parts belong only to domain_visual; ordinary compositions use children.')
            if 'designNotes' in node:
                notes = self.obj(node['designNotes'], path + '.designNotes')
                fields = ('represents', 'previewRepresentation', 'assetStatus') if node.get('kind') == 'domain_visual' else ('relationship', 'followBehavior')
                if node.get('kind') != 'domain_visual' and node.get('component') != 'sui-attachment-panel':
                    self.error('scene-notes-owner', path, 'Scene notes belong to a model or AttachmentPanel.')
                for key in fields:
                    if not nonempty(notes.get(key)):
                        self.error('scene-notes', path + '.designNotes.' + key, 'Expected a nonempty description.')
                if node.get('kind') == 'domain_visual':
                    if notes.get('assetStatus') not in ('to-create', 'available'):
                        self.error('scene-notes', path, 'assetStatus must be to-create or available.')
                    if notes.get('assetStatus') == 'available':
                        self.ref(notes.get('assetId'), assets, path + '.designNotes.assetId')
                for key in ('appearance', 'behaviors', 'previewLimitations'):
                    if key in notes and (not isinstance(notes[key], list) or not all(nonempty(v) for v in notes[key])):
                        self.error('scene-notes', path + '.designNotes.' + key, 'Expected an array of nonempty descriptions.')
            if node.get('kind') == 'domain_visual' and not parts and not raw_children and not node.get('designNotes'):
                self.warning('custom-detail', path, 'No parts or children: confirm whether independently styled internal regions are missing.')
            for pid, raw in parts.items():
                pp = path + '.parts.' + pid
                part = self.obj(raw, pp)
                appearance = self.obj(part.get('appearance', {}), pp + '.appearance')
                self.appearance(appearance, pp + '.appearance', 'content')
                if number(appearance.get('radiusDp')) and appearance['radiusDp'] > 0 and not has_fill(appearance):
                    self.warning('transparent-rounded-part', pp, 'Rounded part has no base fill; confirm that transparency is intended.')
                for state, appearance in self.obj(part.get('states', {}), pp + '.states').items():
                    self.appearance(appearance, pp + '.states.' + state, 'content')
                    if state in INTERACTIVE_STATES and not has_fill(appearance):
                        self.warning('part-state-fill', pp + '.states.' + state, 'No explicit state fill; review whether the intended state is expressed.')
                if 'children' in part or 'parts' in part:
                    self.error('nested-parts', pp, 'Use flat local parts or ordinary nodes; nested part containers are not supported.')

        # A tree must have unique parents and no cycles, including detached nodes.
        for nid, owners in parents.items():
            if len(owners) > 1:
                self.error('multiple-parents', f'nodes[{nid}]', 'A node has multiple parents or is repeated in one children array.')
        ancestry = {}
        for nid in nodes:
            chain, current = [], nid
            while len(parents[current]) == 1:
                current = parents[current][0]
                if current == nid or current in chain:
                    self.error('node-cycle', f'nodes[{nid}]', 'Cycle in node ancestry.')
                    break
                chain.append(current)
            ancestry[nid] = chain

        roots = set()
        for sid, surface in surfaces.items():
            path = f'surfaces[{sid}]'
            root = surface.get('rootNodeId')
            if self.ref(root, nodes, path + '.rootNodeId'):
                if parents[root] or root in roots:
                    self.error('surface-root', path, 'Each surface owns a distinct root outside other content trees.')
                roots.add(root)
            size = self.obj(surface.get('defaultSize'), path + '.defaultSize')
            for key in ('width', 'height'):
                if not number(size.get(key)) or size[key] <= 0:
                    self.error('window-size', path + '.defaultSize.' + key, 'Record a positive fixed design dimension.')
            if surface.get('type') == 'volume':
                if not number(size.get('depth')) or size['depth'] <= 0:
                    self.error('volume-depth', path + '.defaultSize.depth', 'Record a positive Volume depth in dp.')
                if size.get('unit') != 'dp':
                    self.error('volume-unit', path + '.defaultSize.unit', 'Volume Preview dimensions use dp.')
            if not nonempty(size.get('unit')):
                self.error('window-unit', path, 'Record the design dimension unit.')
            if not nonempty(surface.get('type')):
                self.error('surface-type', path, 'Record the selected container type.')
            if 'ownerSurfaceId' in surface:
                self.ref(surface['ownerSurfaceId'], surfaces, path + '.ownerSurfaceId')
            seen, current = {sid}, surface.get('ownerSurfaceId')
            while isinstance(current, str) and current in surfaces:
                if current in seen:
                    self.error('surface-cycle', path, 'Cycle in surface ownership.')
                    break
                seen.add(current)
                current = surfaces[current].get('ownerSurfaceId')
            bg = surface.get('windowBackground')
            if bg is not None and (surface.get('type') != 'planar' or bg not in ('material', 'transparent')):
                self.error('window-background', path, 'Only planar surfaces select material (default) or transparent.')
            if bg == 'transparent' and not nonempty(surface.get('windowBackgroundEvidence')):
                self.error('window-background', path, 'Transparent planar windows need the explicit user decision in windowBackgroundEvidence.')
            if 'material' in surface:
                self.error('material', path, 'Retain system window material; do not add arbitrary material choices.')
            if surface.get('type') == 'subwindow':
                self.ref(surface.get('ownerSurfaceId'), surfaces, path + '.ownerSurfaceId')
                if not isinstance(surface.get('initiallyVisible'), bool):
                    self.error('subwindow-visible', path, 'Record initiallyVisible as a boolean.')
                placement = self.obj(surface.get('placement'), path + '.placement')
                if not all(nonempty(placement.get(k)) for k in ('side', 'align')) or not all(number(placement.get(k)) for k in ('gapDp', 'depthDp')):
                    self.error('subwindow-placement', path, 'Record side, align, gapDp and depthDp.')
                if isinstance(root, str) and root in nodes and nodes[root].get('component') != 'sui-subwindow':
                    self.error('subwindow-root', path, 'A subwindow surface must reference its Subwindow root.')
        for sid, state in states.items():
            for surface, root in self.obj(state.get('surfaceRoots', {}), f'states[{sid}].surfaceRoots').items():
                self.ref(surface, surfaces, f'states[{sid}].surfaceRoots')
                if self.ref(root, nodes, f'states[{sid}].surfaceRoots.{surface}'):
                    roots.add(root)
                    if parents[root]:
                        self.error('state-root', f'states[{sid}]', 'State roots must be independent content-tree roots.')
        for nid in nodes:
            if nid not in roots and not any(root in ancestry[nid] for root in roots):
                self.error('detached-node', f'nodes[{nid}]', 'Node is not reachable from any surface/state root.')

        def path_to(child, owner):
            if child not in ancestry or owner not in ancestry[child]:
                return None
            return [child] + ancestry[child][:ancestry[child].index(owner)]

        # Explicit title references replace old named title-slot requirements.
        titles, subtitles, owned_text = set(), set(), set()
        for nid, node in nodes.items():
            if node.get('component') not in TITLE_COMPONENTS:
                continue
            for child, item in nodes.items():
                route = path_to(child, nid)
                if route and item.get('kind') == 'text' and all(nodes[x].get('kind') == 'layout' for x in route[1:]):
                    owned_text.add(child)
            if node.get('component') != 'sui-title-bar':
                continue
            for key, target_set in (('title-node-id', titles), ('subtitle-node-id', subtitles)):
                target = props[nid].get(key)
                if target is None:
                    continue
                route = path_to(target, nid) if isinstance(target, str) else None
                if (not route or nodes[target].get('kind') != 'text'
                        or not all(nodes[x].get('kind') == 'layout' for x in route[1:])
                        or any(props[x].get('slot') not in (None, '', 'default') for x in route)):
                    self.error('title-reference', f'nodes[{nid}].props.{key}', 'Reference an owned text node through the default title slot, not an action/search slot.')
                else:
                    target_set.add(target)
            if props[nid].get('title-node-id') is not None and props[nid].get('title-node-id') == props[nid].get('subtitle-node-id'):
                self.error('title-reference', f'nodes[{nid}]', 'Title and subtitle must be different nodes.')

        custom_titles = set()
        for nid, node in nodes.items():
            if 'textRole' not in node:
                continue
            owners = [p for p in ancestry[nid] if nodes[p].get('component') in WINDOW_COMPONENTS]
            owner = owners[0] if owners else None
            style = node.get('textStyle', {})
            if (node.get('textRole') != 'surface_title' or node.get('kind') != 'text'
                    or nid in owned_text or owner is None
                    or nodes[owner].get('component') not in CUSTOM_TITLE_SURFACES
                    or props[owner].get('title-node-id') != nid
                    or not isinstance(style, dict) or style.get('typography') not in self.type_sizes):
                self.error('surface-title', f'nodes[{nid}]', 'surface_title needs a uniquely owned, explicitly referenced custom surface heading with an exact typography token; it cannot replace a native title slot.')
            else:
                custom_titles.add(nid)

        for nid, node in nodes.items():
            path = f'nodes[{nid}]'
            if 'textStyle' in node and node.get('kind') != 'text':
                self.error('text-scope', path, 'Put textStyle on the owning text node, not a component or wrapper.')
            if node.get('kind') != 'text':
                continue
            if not nonempty(node.get('content')) and not nonempty(node.get('bindings', {}).get('content')):
                self.error('text-content', path, 'Record visible text or a descriptive content binding.')
            style = self.obj(node.get('textStyle', {}), path + '.textStyle')
            overrides = self.obj(style.get('overrides', {}), path + '.textStyle.overrides')
            title_exception = nid in titles and style == {'overrides': {'weight': 700}}
            subtitle_exception = nid in subtitles and style == {'typography': 'bodyMedium', 'color': 'labelSecondary'}
            if nid in owned_text:
                if style and not (title_exception or subtitle_exception or evidence(node)):
                    self.error('component-text', path, 'Inherit component text; only referenced primary-title weight 700 or the composed subtitle style is an unbacked exception.')
            elif not style and len(parents[nid]) == 1 and nodes[parents[nid][0]].get('kind') == 'spatialui':
                pass  # Unmodified direct slot text inherits its standard component.
            elif 'typography' not in style or 'color' not in style:
                self.error('app-text', path, 'Application text must name its typography token and color.')
            for key in set(style) - {'typography', 'color', 'overrides'}:
                self.error('text-field', path + '.textStyle.' + key, 'Unknown textStyle field.')
            for key in set(overrides) - {'weight', 'sizeSp', 'lineHeightSp', 'fontFamily'}:
                self.error('text-field', path + '.textStyle.overrides.' + key, 'Unknown text override field.')
            if 'typography' in style and style['typography'] not in self.type_sizes:
                self.error('typography', path, 'Use an exact camelCase typography token from the reference.')
            if 'fontFamily' in overrides and not nonempty(overrides['fontFamily']):
                self.error('text-value', path + '.textStyle.overrides.fontFamily', 'Expected a nonempty font family.')
            if 'color' in style:
                self.color(style['color'], path + '.textStyle.color')
            for key in ('weight', 'sizeSp', 'lineHeightSp'):
                if key in overrides and (not number(overrides[key]) or overrides[key] <= 0):
                    self.error('text-value', path + '.textStyle.overrides.' + key, 'Expected a positive numeric value.')
            size = overrides.get('sizeSp', self.type_sizes.get(style.get('typography')))
            if number(size) and size >= 20 and nid not in titles | custom_titles:
                self.warning('large-text', path, 'Explicit application text is at least 20sp; confirm the emphasis is needed. Component defaults are not expanded.')

        def app_fill(node):
            return has_fill(node.get('appearance')) or any(
                has_fill(v.get('appearance')) for v in node.get('visualStates', {}).values() if isinstance(v, dict)
            )

        filled = {nid for nid, node in nodes.items() if app_fill(node)}
        for nid in nodes:
            ancestors = [p for p in ancestry[nid] if p in filled]
            parts = nodes[nid].get('parts', {})
            part_fill = isinstance(parts, dict) and any(
                isinstance(p, dict) and (has_fill(p.get('appearance')) or (
                    isinstance(p.get('states'), dict) and any(has_fill(s) for s in p['states'].values())))
                for p in parts.values())
            if ancestors and (nid in filled or part_fill):
                self.error('nested-background', f'nodes[{nid}]', f'App background nested inside {ancestors[0]!r}; remove one layer. Potential state fills count too.')

        for nid, node in nodes.items():
            if node.get('component') != 'sui-subwindow':
                continue
            path = f'nodes[{nid}]'
            matching = [s for s in surfaces.values() if s.get('rootNodeId') == nid and s.get('type') == 'subwindow']
            if len(matching) != 1:
                self.error('subwindow-surface', path, 'Register this Subwindow as its own owned surface.')
            regions = self.obj(node.get('regions'), path + '.regions')
            bar, body = regions.get('titleBarNodeId'), regions.get('bodyNodeId')
            bar_route = path_to(bar, nid) if isinstance(bar, str) else None
            body_route = path_to(body, nid) if isinstance(body, str) else None
            bars = [child for child in nodes if nodes[child].get('component') == 'sui-title-bar'
                    and path_to(child, nid) and all(nodes[x].get('kind') == 'layout' for x in path_to(child, nid)[1:])]
            if not bar_route or bars != [bar]:
                self.error('subwindow-titlebar', path, 'Reference exactly one owned TitleBar outside body content.')
                continue
            if not body_route or nodes[body].get('kind') != 'layout' or bar in body_route or body in bar_route or any(nodes[x].get('kind') != 'layout' for x in body_route[1:]):
                self.error('subwindow-body', path, 'Reference a separate transparent body layout outside the TitleBar.')
            for child, parent in zip(bar_route, bar_route[1:] + [nid]):
                if not children[parent] or children[parent][0] != child:
                    self.error('subwindow-header-order', path, 'TitleBar must precede body content.')
                    break
            if not (props[bar].get('title-node-id') in titles or nonempty(props[bar].get('title'))):
                self.error('subwindow-title', path, 'The TitleBar needs a referenced primary title or a built-in title string.')
            exits = []
            for child in nodes:
                route = path_to(child, bar)
                if route and nodes[child].get('component') == 'sui-icon-button' and props[child].get('navigation-action') in ('close', 'back') and props[route[-1]].get('slot') == 'leading':
                    events = nodes[child].get('events', {})
                    if isinstance(events, dict) and any(isinstance(a, str) and a in actions for a in events.values()):
                        exits.append(child)
            if not exits:
                self.error('subwindow-exit', path, 'Provide a leading close/back IconButton with an action reference.')
        return self.issues


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('design_spec', type=Path)
    parser.add_argument('--asset-root', type=Path, help='Resolve assets[].src from this directory; other paths remain Spec-relative.')
    parser.add_argument('--target', type=Path, help='Project directory containing delivered assets; defaults to the parent of .scratch, or the Spec directory.')
    parser.add_argument('--json', action='store_true', help='Print a JSON report.')
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.design_spec.read_text(encoding='utf-8'), parse_constant=lambda c: (_ for _ in ()).throw(ValueError(f'Non-JSON constant: {c}')))
        checker = Checker(args.design_spec, args.asset_root)
        issues = checker.check(value)
        # Share the actual admission rules with Workflow; do not duplicate them in Python.
        command = ['node', str(Path(__file__).with_name('check_design_handoff.mjs')), str(args.design_spec.resolve())]
        if args.target:
            command.extend(['--target', str(args.target.resolve())])
        if args.asset_root:
            command.extend(['--asset-root', str(args.asset_root.resolve())])
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode not in (0, 1):
                raise ValueError(result.stderr.strip() or 'Handoff checker did not complete.')
            issues.extend(json.loads(result.stdout)['issues'])
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
            issues.append(dict(level='error', code='handoff-checker', path=str(args.design_spec),
                               message=f'Cannot run shared handoff checks; Node.js is required: {exc}'))
        exit_code = 1 if any(i['level'] == 'error' for i in issues) else 0
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        issues = [dict(level='error', code='input', path=str(args.design_spec), message=str(exc))]
        exit_code = 2
    report = dict(status='FAIL' if exit_code else 'PASS', errors=sum(i['level'] == 'error' for i in issues),
                  warnings=sum(i['level'] == 'warning' for i in issues), issues=issues)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for issue in issues:
            print(f"[{issue['level']}] {issue['code']} {issue['path']}: {issue['message']}")
        print(f"[write-spec] {report['status']} errors={report['errors']} warnings={report['warnings']}")
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
