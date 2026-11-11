/* Browser audit for write-spec-draft-1. Load in the running Preview, then await
 * auditDesignPreview(spec, { specUrl, scenario, initial, expectations }).
 * Reads the page; never repairs artifacts, drives interactions, or evaluates bindings.
 */
(() => {
  'use strict';
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o || {}, k);
  const parent = (el) => el.parentElement || el.getRootNode()?.host || null;
  const descendants = (root) => {
    const result = [];
    for (const el of root.querySelectorAll('*')) {
      result.push(el);
      if (el.shadowRoot) result.push(...descendants(el.shadowRoot));
    }
    return result;
  };
  const visible = (el) => {
    for (let p = el; p; p = parent(p)) {
      const s = getComputedStyle(p);
      if (s.display === 'none' || s.visibility === 'hidden' || s.visibility === 'collapse' || Number(s.opacity) === 0) return false;
    }
    return el.getClientRects().length > 0;
  };
  // Explicit adapters for this reference runtime. Unknown components remain unverified.
  const selectors = {
    'sui-text': '.text', 'sui-list-item': '.root', 'sui-button': '.root',
    'sui-icon-button': '.root', 'sui-title-bar': '.root', 'sui-subwindow': '.panel',
    'sui-icon': '.i', 'sui-side-navigation': '.root', 'sui-search-field': '.field',
  };
  const rendered = (el) => el.localName.startsWith('sui-')
    ? el.shadowRoot?.querySelector(selectors[el.localName] || ':not(*)') || null : el;
  const renderedText = (el) => {
    if (el.nodeType === Node.TEXT_NODE) return el.textContent;
    if (el.nodeType !== Node.ELEMENT_NODE) return '';
    if (el.localName === 'slot') {
      const assigned = el.assignedNodes({ flatten: true });
      return [...(assigned.length ? assigned : el.childNodes)].map(renderedText).join('');
    }
    if (!visible(el)) return '';
    const children = el.shadowRoot ? el.shadowRoot.childNodes : el.childNodes;
    return [...children].filter(n => !['style', 'script'].includes(n.localName)).map(renderedText).join('');
  };
  const px = (s) => /^-?\d+(\.\d+)?px$/.test(s) ? parseFloat(s) : null;
  const url = (value, base) => { try { return new URL(value, base).href; } catch { return null; } };
  const rgba = (value) => {
    if (!value || !CSS.supports('color', value)) return null;
    const ctx = new OffscreenCanvas(1, 1).getContext('2d', { willReadFrequently: true });
    ctx.fillStyle = value; ctx.fillRect(0, 0, 1, 1);
    return [...ctx.getImageData(0, 0, 1, 1).data];
  };

  globalThis.auditDesignPreview = async (spec, options = {}) => {
    if (spec?.schemaVersion !== 'write-spec-draft-1') throw new Error('Only write-spec-draft-1 is supported.');
    if (!options.specUrl || !options.scenario || typeof options.initial !== 'boolean') {
      throw new Error('Provide specUrl, a scenario label, and initial: true/false.');
    }
    const specUrl = new URL(options.specUrl, document.baseURI).href;
    const observations = [];
    const add = (nodeId, property, expected, actual, tolerance = 0, reason = '', source = 'spec') => {
      const measurable = actual !== undefined && expected !== undefined;
      const equal = tolerance ? Number.isFinite(expected) && Number.isFinite(actual) && Math.abs(expected - actual) <= tolerance
        : JSON.stringify(expected) === JSON.stringify(actual);
      observations.push({ nodeId, property, expected: expected ?? null, actual: actual ?? null,
        status: measurable ? (equal ? 'match' : 'mismatch') : 'unverified', tolerance, reason, source });
    };
    const unknown = (id, key, expected, actual, reason) => {
      observations.push({ nodeId: id, property: key, expected: expected ?? null, actual: actual ?? null,
        status: 'unverified', tolerance: 0, reason, source: 'spec' });
    };
    const expectedPreview = spec.metadata?.preview && url(spec.metadata.preview, specUrl);
    add('$preview', 'url', expectedPreview || undefined, location.href.split('#')[0]);
    const nodes = new Map(spec.nodes.map(n => [n.id, n]));
    const elements = descendants(document);
    const matches = (id) => elements.filter(e => e.id === id);
    const one = (id) => matches(id).length === 1 ? matches(id)[0] : null;
    const noteBlocks = matches('scene-design-notes');
    let sceneNotes = {};
    if (noteBlocks.length) {
      add('$scene', 'notes.block-count', 1, noteBlocks.length);
      try {
        if (noteBlocks[0].localName !== 'script' || noteBlocks[0].type !== 'application/json') throw new Error('Use an application/json script.');
        sceneNotes = JSON.parse(noteBlocks[0].textContent);
        if (!sceneNotes || Array.isArray(sceneNotes) || typeof sceneNotes !== 'object') throw new Error('Expected an object keyed by element ID.');
        add('$scene', 'notes.valid-json-object', true, true);
      } catch (error) {
        add('$scene', 'notes.valid-json-object', true, false, 0, error.message);
        sceneNotes = {};
      }
    }
    const canonical = v => Array.isArray(v) ? v.map(canonical) : v && typeof v === 'object'
      ? Object.fromEntries(Object.keys(v).sort().map(k => [k, canonical(v[k])])) : v;
    for (const id of new Set([...Object.keys(sceneNotes), ...spec.nodes.filter(n => n.designNotes).map(n => n.id)])) {
      add(id, 'notes.element-count', 1, matches(id).length);
      add(id, 'notes.spec-node', true, nodes.has(id));
      add(id, 'notes.preview-entry', true, own(sceneNotes, id));
      add(id, 'notes.spec-entry', true, own(nodes.get(id), 'designNotes'));
      if (own(sceneNotes, id) && own(nodes.get(id), 'designNotes')) {
        add(id, 'notes.preserved', canonical(sceneNotes[id]), canonical(nodes.get(id).designNotes));
        unknown(id, 'notes.native-behavior', null, null, 'Preserved requirements only; native geometry, animation and follow behavior require native validation.');
      }
    }
    const nodeParents = new Map(spec.nodes.flatMap(n => (n.children || []).map(id => [id, n.id])));
    const expectations = options.expectations || {};
    for (const [id, e] of Object.entries(expectations)) {
      if (!nodes.has(id) || !e.source?.trim()) throw new Error(`Expectation ${id} needs an existing node and a Spec/data source explanation.`);
      for (const key of Object.keys(e)) {
        if (!['source', 'visible', 'content', 'assetId', 'visualState'].includes(key)) throw new Error(`Unsupported expectation field: ${key}`);
      }
    }
    const reference = async (name) => {
      const entry = spec.metadata?.references?.find(r => r.path?.endsWith('/' + name) || r.path === name);
      if (!entry) return null;
      try { const r = await fetch(new URL(entry.path, specUrl)); return r.ok ? await r.json() : null; } catch { return null; }
    };
    const [tokens, roles] = await Promise.all([reference('tokens.json'), reference('color-roles.json')]);
    const colors = new Map((tokens?.color?.tokens || []).map(t => [t.name, t.value]));
    for (const r of roles?.roles || []) colors.set(r.name, colors.get(r.token));
    for (const [k, v] of Object.entries(spec.theme?.brandColors || {})) colors.set(k, v);
    const types = new Map((tokens?.type?.groups || []).flatMap(g => g.styles.map(t => [t.name.replace(/-([a-z])/g, (_, c) => c.toUpperCase()), t])));
    const colorCheck = (id, key, expected, actual) => {
      const value = colors.get(expected) || (expected === 'transparent' ? expected : null);
      if (!value) unknown(id, key, expected, actual, 'Color role/token could not be resolved from the recorded reference.');
      else add(id, key, rgba(value) ?? undefined, rgba(actual) ?? undefined, 0, `Declared color: ${expected}`);
    };
    const metric = (id, key, expected, target, css) => add(id, key, expected,
      target ? px(getComputedStyle(target)[css]) ?? undefined : undefined, 1, target ? '' : 'No supported rendered target.');
    const checkLayout = (id, el, layout) => {
      const style = getComputedStyle(el);
      for (const [key, value] of Object.entries(layout || {})) {
        const property = 'layout.' + key;
        const dimensions = { widthDp: 'width', heightDp: 'height', minWidthDp: 'minWidth', minHeightDp: 'minHeight', maxWidthDp: 'maxWidth', maxHeightDp: 'maxHeight' };
        if (key in dimensions) {
          // Fixed dimensions are visible border-box sizes; min/max are CSS constraints.
          if (key === 'widthDp' || key === 'heightDp') add(id, property, value, el.getBoundingClientRect()[dimensions[key]], 1);
          else metric(id, property, value, el, dimensions[key]);
        } else if (key === 'paddingDp') {
          for (const edge of ['top', 'right', 'bottom', 'left']) {
            const v = typeof value === 'number' ? value : value[edge];
            if (v !== undefined) metric(id, `${property}.${edge}`, v, el, 'padding' + edge[0].toUpperCase() + edge.slice(1));
          }
        } else if (key === 'gapDp') {
          const axes = style.display.includes('grid') ? ['rowGap', 'columnGap']
            : style.display.includes('flex') ? [style.flexDirection.startsWith('column') ? 'rowGap' : 'columnGap'] : [];
          if (!axes.length) add(id, property + '.layout-supported', true, false);
          for (const axis of axes) metric(id, property + '.' + axis, value, el, axis);
        } else if (key === 'mode' && ['row', 'column', 'grid'].includes(value)) {
          add(id, property + '.display', value === 'grid' ? 'grid' : 'flex', style.display.replace('inline-', ''));
          if (value !== 'grid') add(id, property + '.direction', value, style.flexDirection);
        } else if (key === 'align' || key === 'justify') {
          const expected = ({ start: 'flex-start', end: 'flex-end' })[value] || value;
          const actual = style[key === 'align' ? 'alignItems' : 'justifyContent'];
          add(id, property, expected, actual === 'start' ? 'flex-start' : actual === 'end' ? 'flex-end' : actual);
        } else if (key === 'grow') add(id, property, value, Number(style.flexGrow));
        else if (key === 'overflow') {
          if (value === 'scroll') add(id, property, true, ['auto', 'scroll'].includes(style.overflowY));
          else add(id, property, value, style.overflow);
        } else unknown(id, property, value, key === 'marginTop' ? style.marginTop : null, 'Layout relationship requires author review; not a measured fixed value.');
      }
    };
    const checkAppearance = (id, target, appearance, prefix) => {
      for (const [key, value] of Object.entries(appearance || {})) {
        const p = prefix + key;
        if (!target) { unknown(id, p, value, null, 'No supported rendered target.'); continue; }
        const s = getComputedStyle(target);
        if (key === 'fill' || key === 'foreground') colorCheck(id, p, value, s[key === 'fill' ? 'backgroundColor' : 'color']);
        else if (key === 'radiusDp') for (const corner of ['TopLeft', 'TopRight', 'BottomLeft', 'BottomRight']) metric(id, p + '.' + corner, value, target, 'border' + corner + 'Radius');
        else if (key === 'opacity') add(id, p, value, Number(s.opacity));
        else unknown(id, p, value, null, 'Unsupported appearance property.');
      }
    };
    for (const node of spec.nodes) {
      const id = node.id, found = matches(id), exp = expectations[id] || {};
      add(id, 'element.count', 1, found.length);
      if (found.length !== 1) continue;
      const el = found[0], target = rendered(el);
      if (node.kind === 'spatialui') {
        add(id, 'component', node.component, el.localName);
        add(id, 'component.registered', true, Boolean(customElements.get(el.localName)));
        add(id, 'component.initialized', true, Boolean(el.shadowRoot?.childElementCount));
      }
      const expectedParent = nodeParents.get(id);
      if (expectedParent) {
        let p = parent(el);
        while (p && !nodes.has(p.id)) p = parent(p);
        add(id, 'parent', expectedParent, p?.id || null);
      }
      if (node.props?.slot !== undefined) {
        add(id, 'slot', node.props.slot, el.slot);
        add(id, 'slot.assigned', node.props.slot, el.assignedSlot?.name ?? null);
      }
      for (const key of ['title-node-id', 'subtitle-node-id']) {
        if (!node.props?.[key]) continue;
        let child = one(node.props[key]);
        while (child && child.parentElement !== el) child = child.parentElement;
        add(id, 'props.' + key + '.default-slot', true, Boolean(child && child.assignedSlot?.name === ''));
      }
      for (const [region, childId] of Object.entries(node.regions || {})) add(id, 'regions.' + region, true, Boolean(one(childId) && el.contains(one(childId))));
      let visibilityOwner = id, expectedVisible, visibilitySource = 'spec';
      const visited = new Set();
      while (visibilityOwner && !visited.has(visibilityOwner)) {
        visited.add(visibilityOwner);
        const ancestorExpectation = expectations[visibilityOwner];
        if (own(ancestorExpectation, 'visible')) {
          expectedVisible = ancestorExpectation.visible;
          visibilitySource = ancestorExpectation.source;
          break;
        }
        const ancestor = nodes.get(visibilityOwner);
        const surface = spec.surfaces.find(s => s.rootNodeId === visibilityOwner);
        if (options.initial && surface) { expectedVisible = surface.initiallyVisible !== false; break; }
        if (ancestor?.bindings?.hidden || ancestor?.visibleInStates) break;
        visibilityOwner = nodeParents.get(visibilityOwner);
      }
      if (expectedVisible !== undefined) add(id, 'visible', expectedVisible, visible(el), 0, '', visibilitySource);
      else unknown(id, 'visible', null, visible(el), 'Provide a scenario expectation or review visibility manually.');
      if (!visible(el)) {
        unknown(id, 'rendered-content', null, null, 'Hidden now: geometry, text, assets and styles must be checked after opening.');
        continue;
      }
      checkLayout(id, el, node.layout);
      if (node.kind === 'text' || own(node.props, 'text') || own(node.props, 'title')) {
        const actual = renderedText(el).trim();
        const expected = own(exp, 'content') ? exp.content : options.initial && !node.bindings?.content
          ? node.kind === 'text' ? node.content : node.props.text ?? node.props.title : undefined;
        // A composite TitleBar includes actions; its title alone needs separate reading.
        const text = node.props?.title !== undefined && el.localName === 'sui-title-bar'
          ? el.shadowRoot?.querySelector('.title') : el;
        add(id, 'content', expected, text ? renderedText(text).trim() : actual, 0,
          expected === undefined ? 'Dynamic or post-action content needs a Spec/data-based scenario expectation or author review.' : '', exp.source || 'spec');
      }
      const ts = node.textStyle;
      if (ts) {
        const token = ts.typography && types.get(ts.typography);
        if (ts.typography && !token) unknown(id, 'textStyle.typography', ts.typography, null, 'Typography reference unavailable.');
        const wanted = { ...(token ? { sizeSp: px(token.fontSize), lineHeightSp: px(token.lineHeight), weight: token.fontWeight } : {}), ...ts.overrides };
        const style = target && getComputedStyle(target);
        for (const [key, value] of Object.entries(wanted)) {
          const css = { sizeSp: 'fontSize', lineHeightSp: 'lineHeight', weight: 'fontWeight', fontFamily: 'fontFamily' }[key];
          if (!css || !style) unknown(id, 'textStyle.' + key, value, null, 'No supported text style reader.');
          else if (key === 'weight') add(id, 'textStyle.' + key, Number(value), Number(style.fontWeight));
          else if (key === 'fontFamily') add(id, 'textStyle.' + key, value, style.fontFamily);
          else metric(id, 'textStyle.' + key, value, target, css);
        }
        if (ts.color) colorCheck(id, 'textStyle.color', ts.color, style?.color);
      }
      let appearance = node.appearance;
      let props = { ...node.props };
      if (node.visualStates) {
        if (own(exp, 'visualState')) {
          const variant = exp.visualState === 'base' ? {} : node.visualStates[exp.visualState];
          if (!variant) unknown(id, 'visualState', exp.visualState, null, 'Unknown visual state.');
          else { props = { ...props, ...variant.props }; appearance = { ...appearance, ...variant.appearance }; }
        } else unknown(id, 'visualState', Object.keys(node.visualStates), el.getAttribute('aria-selected'), 'Select a documented visual state in scenario expectations.');
      }
      checkAppearance(id, target, appearance, 'appearance.');
      for (const [key, value] of Object.entries(props)) {
        if (['slot', 'title-node-id', 'subtitle-node-id', 'text', 'title', 'fit', 'objectPosition'].includes(key)) continue;
        const p = 'props.' + key;
        if (key === 'background' && el.localName === 'sui-attachment-panel') {
          add(id, p, value, el.getAttribute('background') || 'transparent');
        } else if (['custom-width', 'custom-height'].includes(key)) {
          const axis = key === 'custom-width' ? 'width' : 'height';
          add(id, p, value, target?.getBoundingClientRect()[axis], 1);
        } else if (key === 'content-padding' || key.startsWith('padding-')) {
          const supported = ['sui-list-item', 'sui-title-bar', 'sui-subwindow', 'sui-button', 'sui-icon-button'].includes(el.localName);
          const edges = key === 'content-padding' ? ['Top', 'Right', 'Bottom', 'Left'] : [{ 'padding-top': 'Top', 'padding-end': 'Right', 'padding-bottom': 'Bottom', 'padding-start': 'Left' }[key]].filter(Boolean);
          if (!supported || !edges.length) unknown(id, p, value, null, 'No supported internal padding adapter.');
          else for (const edge of edges) {
            const directional = { Top: 'padding-top', Right: 'padding-end', Bottom: 'padding-bottom', Left: 'padding-start' }[edge];
            metric(id, p + '.' + edge, key === 'content-padding' && own(props, directional) ? props[directional] : value, target, 'padding' + edge);
          }
        } else if (key === 'corner-radius') checkAppearance(id, target, { radiusDp: value }, p + '.');
        else if (['container-color', 'content-color', 'tint'].includes(key)) {
          colorCheck(id, p, value, target && getComputedStyle(target)[key === 'container-color' ? 'backgroundColor' : 'color']);
        } else if (key === 'size' && el.localName === 'sui-icon') {
          add(id, p + '.width', value, el.getBoundingClientRect().width, 1);
          add(id, p + '.height', value, el.getBoundingClientRect().height, 1);
        } else if (['size', 'for', 'placement', 'depth', 'semantic-label', 'dismiss-on-click-outside'].includes(key) || (key === 'name' && el.localName === 'sui-icon')) {
          // Configuration checks do not claim that every behavioral effect was exercised.
          const actual = el.getAttribute(key);
          add(id, p + '.configuration', value, typeof value === 'boolean' ? actual === null ? undefined : actual !== 'false' : typeof value === 'number' ? actual === null ? undefined : Number(actual) : actual);
          if (key === 'dismiss-on-click-outside') unknown(id, p + '.behavior', value, null, 'Exercise outside-click behavior if required.');
        } else unknown(id, p, value, el.getAttribute(key), 'Unsupported or semantic parameter; requires author review.');
      }
      if (node.kind === 'media' || node.assetId || node.bindings?.assetId) {
        const assetId = own(exp, 'assetId') ? exp.assetId : !node.bindings?.assetId ? node.assetId : undefined;
        const asset = spec.assets?.find(a => a.id === assetId);
        let actual, catalogId;
        if (el.localName === 'img') {
          actual = el.currentSrc || el.src;
          add(id, 'asset.loaded', true, el.complete && el.naturalWidth > 0);
        } else if (el.localName === 'sui-icon') {
          catalogId = el.shadowRoot?.querySelector('.i > svg[data-icon-id]')?.getAttribute('data-icon-id');
          const mask = el.shadowRoot?.querySelector('.i > span');
          actual = mask && getComputedStyle(mask).maskImage.match(/url\(["']?(.*?)["']?\)/)?.[1];
        }
        if (catalogId) {
          add(id, 'asset.catalogId', asset?.catalogId, catalogId, 0,
            'Rendered local catalog identity; the retained asset file is the handoff resource.', exp.source || 'spec');
        } else {
          add(id, 'asset.url', asset ? url(asset.src, specUrl) ?? undefined : undefined, actual || undefined, 0,
            assetId === undefined ? 'Resolve the current asset binding from the selected data record.' : 'Resource identity only; inline artwork and native compatibility require review.', exp.source || 'spec');
        }
        if (node.props?.fit !== undefined) add(id, 'media.fit', node.props.fit, getComputedStyle(el).objectFit);
        if (node.props?.objectPosition !== undefined) add(id, 'media.objectPosition', node.props.objectPosition === 'center' ? '50% 50%' : node.props.objectPosition, getComputedStyle(el).objectPosition);
      }
      for (const key of ['events', 'bindings', 'parts', 'textBehavior']) if (node[key]) unknown(id, key, node[key], null, 'Declared relationships/parts/behavior need scenario or author review; not executed by this script.');
    }
    for (const surface of spec.surfaces) {
      if (surface.type === 'volume') {
        const shell = one(surface.id), root = one(surface.rootNodeId);
        add(surface.id, 'surface.shell-count', 1, matches(surface.id).length);
        add(surface.id, 'surface.shell', 'sui-volume', shell?.localName);
        add(surface.id, 'surface.root-contained', true, Boolean(shell && root && shell !== root && shell.contains(root)));
        add(surface.id, 'surface.unit', 'dp', surface.defaultSize.unit);
        if (shell) {
          for (const axis of ['width', 'height', 'depth']) {
            const attr = shell.getAttribute(axis);
            add(surface.id, 'surface.' + axis + '.declared', surface.defaultSize[axis], attr === null ? undefined : Number(attr));
          }
          if (visible(shell)) for (const axis of ['width', 'height']) {
            add(surface.id, 'surface.' + axis + '.rendered', surface.defaultSize[axis], shell.getBoundingClientRect()[axis], 1);
          }
          unknown(surface.id, 'surface.native-depth', surface.defaultSize.depth, null, 'Depth declaration only; schematic bounds do not verify native depth or clipping.');
        }
        continue;
      }
      const el = one(surface.rootNodeId);
      if (!el || !visible(el)) continue;
      const target = surface.type === 'subwindow' ? rendered(el) : el;
      if (!['planar', 'subwindow'].includes(surface.type) || surface.defaultSize.unit !== 'dp') {
        unknown(surface.rootNodeId, 'surface.geometry', surface.defaultSize, null, 'Web audit does not establish 3D or physical geometry.'); continue;
      }
      for (const axis of ['width', 'height']) add(surface.rootNodeId, 'surface.' + axis, surface.defaultSize[axis], target?.getBoundingClientRect()[axis], 1);
      if (surface.ownerSurfaceId) {
        const owner = spec.surfaces.find(s => s.id === surface.ownerSurfaceId);
        const anchor = owner && one(owner.rootNodeId);
        add(surface.rootNodeId, 'surface.owner', owner?.rootNodeId, el.getAttribute('for'));
        if (anchor && target && surface.placement) {
          const a = anchor.getBoundingClientRect(), b = target.getBoundingClientRect(), p = surface.placement;
          const gap = { right: b.left - a.right, left: a.left - b.right, above: a.top - b.bottom, below: b.top - a.bottom }[p.side];
          add(surface.rootNodeId, 'surface.gapDp', p.gapDp, gap, 1);
          if (p.depthDp === 0 && ['top', 'bottom'].includes(p.align)) add(surface.rootNodeId, 'surface.align', a[p.align], b[p.align], 1);
          else unknown(surface.rootNodeId, 'surface.align', p.align, null, 'This alignment/depth combination requires review.');
          unknown(surface.rootNodeId, 'surface.depthDp', p.depthDp, el.getAttribute('depth'), 'Web depth is a simulation, not native spatial evidence.');
        }
      }
      if (surface.windowBackground) {
        if (el.localName === 'sui-planar-window') add(surface.rootNodeId, 'surface.windowBackground', surface.windowBackground, el.getAttribute('background') || 'material');
        else unknown(surface.rootNodeId, 'surface.windowBackground', surface.windowBackground, null, 'No supported window shell adapter.');
      }
    }
    const summary = { match: 0, mismatch: 0, unverified: 0 };
    for (const o of observations) summary[o.status]++;
    return { schemaVersion: 'preview-consistency/v1', scenario: options.scenario, initial: options.initial,
      specUrl, previewUrl: location.href, specRevision: spec.metadata?.revision ?? null, checkedAt: new Date().toISOString(),
      expectations, summary, status: summary.mismatch ? 'mismatch' : summary.unverified ? 'needs-review' : 'checked',
      observations, limitations: ['Only reported fields were checked; omitted design facts need author review.',
        'Visibility is rendered presence, not proof against clipping/occlusion.', 'No native fidelity, full state-machine, screenshot or untouched-default audit.'] };
  };
})();
