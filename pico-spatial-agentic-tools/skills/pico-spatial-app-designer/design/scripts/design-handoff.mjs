// Shared authoring checks: the Spec checker and bundled Workflow gates use this module.
import fs from 'node:fs/promises';
import path from 'node:path';

const object = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value) => typeof value === 'string' && value.trim().length > 0;
const localPath = (value) => value.replaceAll('\\', '/');
const issue = (code, location, message) => ({ level: 'error', code, path: location, message });

/** Collect independent node and resource failures without executing Preview JavaScript. */
export async function checkDesignHandoff({ spec, preview, projectRoot, specPath, assetRoot }) {
  const issues = [];
  if (!object(spec)) return [issue('input', '$', 'Expected a Spec object.')];
  if (!Array.isArray(spec.nodes)) {
    issues.push(issue('node-id', '$.nodes', 'Expected nodes[].'));
  } else if (typeof preview === 'string') {
    const markup = preview
      .replace(/<!--[\s\S]*?-->/gu, '')
      .replace(/<(script|style|textarea|title)\b[^>]*>[\s\S]*?<\/\1\s*>/giu, '');
    const counts = new Map();
    for (const tag of markup.matchAll(/<[a-z][\w-]*\b((?:"[^"]*"|'[^']*'|[^'">])*)>/giu)) {
      const id = [
        ...tag[1].matchAll(/([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/gu),
      ].find((attr) => attr[1].toLowerCase() === 'id');
      if (id) {
        const value = id[2] ?? id[3] ?? id[4];
        counts.set(value, (counts.get(value) ?? 0) + 1);
      }
    }
    const seen = new Set();
    for (const [index, node] of spec.nodes.entries()) {
      const location = `$.nodes[${index}].id`;
      if (!object(node) || !text(node.id) || seen.has(node.id)) {
        issues.push(issue('node-id', location, 'Design nodes need unique nonempty IDs.'));
        continue;
      }
      seen.add(node.id);
      const count = counts.get(node.id) ?? 0;
      if (count !== 1) {
        issues.push(
          issue(
            'preview-node-id',
            location,
            `Preview needs exactly one element with id ${node.id}. Found ${count} in static HTML; write the element in HTML before JavaScript runs.`,
          ),
        );
      }
    }
  }
  issues.push(...(await checkDesignAssets({ spec, projectRoot, specPath, assetRoot })));
  return issues;
}

/** Application assets are Spec-relative; runtime/reference snapshots are not application assets. */
export async function checkDesignAssets({ spec, projectRoot, specPath, assetRoot }) {
  const issues = [];
  if (!object(spec) || (spec.assets !== undefined && !Array.isArray(spec.assets))) {
    return [issue('asset-file', '$.assets', 'Expected assets[].')];
  }
  let realRoot;
  try {
    realRoot = await fs.realpath(projectRoot);
  } catch (error) {
    return [issue('asset-root', projectRoot, String(error))];
  }
  const base = assetRoot ?? path.dirname(specPath);
  for (const [index, asset] of (spec.assets ?? []).entries()) {
    const location = `$.assets[${index}].src`;
    if (!object(asset) || !text(asset.src) || asset.src.includes('://')) {
      issues.push(issue('asset-file', location, 'Expected a delivered local file path.'));
      continue;
    }
    const label = `${asset.id ?? index} (${asset.src})`;
    try {
      const resolved = await fs.realpath(path.resolve(base, localPath(asset.src)));
      const relative = path.relative(realRoot, resolved);
      if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
        issues.push(
          issue(
            'asset-outside-target',
            location,
            `Evidence escapes target: asset ${label} resolves to ${resolved}. Copy the original resource into the project and update assets[].src.`,
          ),
        );
      } else if (!(await fs.stat(resolved)).isFile()) {
        issues.push(issue('asset-file', location, `Asset ${label} is not a file: ${resolved}.`));
      }
    } catch (error) {
      issues.push(issue('asset-file', location, `Asset ${label} is unavailable: ${String(error)}`));
    }
  }
  return issues;
}
