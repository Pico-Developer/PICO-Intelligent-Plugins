#!/usr/bin/env node

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const ASSET_ROOT = path.resolve(SCRIPT_DIR, '../assets/icon-7.0');
const CATALOG_PATH = path.join(ASSET_ROOT, 'catalog.json');
const MANIFEST_PATH = path.join(ASSET_ROOT, 'manifest.json');
const ICON_URI_PATTERN = /^icon70:\/\/7\.0\/(ic_[a-z0-9_]+)$/u;
const CUSTOM_ICON_PATTERN = /^design-assets\/icons\/(ic_[a-z0-9_]+)\.svg$/u;

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function sha256(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function parseArgs(argv) {
  const [command, ...tokens] = argv;
  const options = { _: [] };

  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index];
    if (!token.startsWith('--')) {
      options._.push(token);
      continue;
    }

    const key = token.slice(2);
    const value = tokens[index + 1];
    if (!value || value.startsWith('--')) {
      options[key] = true;
      continue;
    }
    options[key] = value;
    index += 1;
  }

  return { command, options };
}

function loadCatalog() {
  const catalog = readJson(CATALOG_PATH);
  const byName = new Map(catalog.icons.map((icon) => [icon.name, icon]));
  return { catalog, byName };
}

function publicIcon(icon) {
  return {
    name: icon.name,
    uri: `icon70://7.0/${icon.name}`,
    label: icon.label,
    keywords: icon.keywords,
    category: icon.category,
    treatment: icon.treatment,
    autoSelectable: icon.autoSelectable,
    ...(icon.warning ? { warning: icon.warning } : {}),
  };
}

function tokenize(value) {
  return value
    .toLocaleLowerCase('en-US')
    .split(/[\s_./-]+/u)
    .filter(Boolean);
}

function scoreIcon(icon, query) {
  const normalizedQuery = query.trim().toLocaleLowerCase('en-US');
  const queryTokens = tokenize(normalizedQuery);
  const name = icon.name.toLocaleLowerCase('en-US');
  const label = icon.label.toLocaleLowerCase('en-US');
  const category = icon.category.toLocaleLowerCase('en-US');
  const keywords = icon.keywords.map((keyword) => keyword.toLocaleLowerCase('en-US'));
  let score = 0;

  if (name === normalizedQuery) score += 120;
  if (name === `ic_${normalizedQuery}`) score += 110;
  if (label === normalizedQuery) score += 100;
  if (name.includes(normalizedQuery)) score += 50;
  if (label.includes(normalizedQuery)) score += 45;
  if (keywords.some((keyword) => keyword === normalizedQuery)) score += 40;
  if (category === normalizedQuery) score += 25;

  for (const token of queryTokens) {
    if (name.includes(token)) score += 12;
    if (label.includes(token)) score += 10;
    if (keywords.some((keyword) => keyword.includes(token))) score += 8;
    if (category.includes(token)) score += 4;
  }

  return score;
}

export function searchCatalog(query, options = {}) {
  if (!query?.trim()) {
    throw new Error('search requires a non-empty --query');
  }

  const { catalog } = loadCatalog();
  const limit = Number(options.limit ?? 8);
  if (!Number.isInteger(limit) || limit < 1 || limit > 50) {
    throw new Error('--limit must be an integer from 1 to 50');
  }

  const matches = catalog.icons
    .filter((icon) => icon.autoSelectable)
    .filter((icon) => !options.category || icon.category === options.category)
    .filter((icon) => !options.treatment || icon.treatment === options.treatment)
    .map((icon) => ({ icon, score: scoreIcon(icon, query) }))
    .filter(({ score }) => score > 0)
    .sort(
      (left, right) => right.score - left.score || left.icon.name.localeCompare(right.icon.name),
    )
    .slice(0, limit)
    .map(({ icon, score }) => ({ ...publicIcon(icon), score }));

  return { query, count: matches.length, matches };
}

function iconNameFromUri(uri) {
  const match = ICON_URI_PATTERN.exec(uri);
  if (!match) {
    throw new Error(`unsupported ICON 7.0 URI: ${uri}`);
  }
  return match[1];
}

function iconAssetPath(icon, format) {
  if (format === 'svg') return path.join(ASSET_ROOT, icon.source.svg);
  if (format === 'android') return path.join(ASSET_ROOT, icon.source.androidVector);
  throw new Error('--format must be "svg" or "android"');
}

function resolveOne(name, format) {
  const { byName } = loadCatalog();
  const icon = byName.get(name);
  if (!icon) {
    throw new Error(`unknown ICON 7.0 icon: ${name}`);
  }

  const sourcePath = iconAssetPath(icon, format);
  return {
    ...publicIcon(icon),
    format,
    sourcePath,
    fileName: path.basename(sourcePath),
  };
}

function referencedIcons(specPath) {
  const spec = readJson(specPath);
  const specRoot = path.dirname(specPath);
  const iconAssets = new Map(
    (spec.assets ?? []).filter((asset) => asset.kind === 'icon').map((asset) => [asset.id, asset]),
  );
  const catalog = [];
  const custom = [];
  const external = [];

  for (const asset of iconAssets.values()) {
    if (asset.src.startsWith('icon70://')) {
      catalog.push({ assetId: asset.id, name: iconNameFromUri(asset.src) });
      continue;
    }

    const customMatch = CUSTOM_ICON_PATTERN.exec(asset.src);
    if (customMatch) {
      custom.push({
        assetId: asset.id,
        name: customMatch[1],
        sourcePath: path.resolve(specRoot, asset.src),
      });
      continue;
    }

    external.push({ assetId: asset.id, src: asset.src });
  }

  for (const node of spec.nodes ?? []) {
    if (node.kind !== 'spatialui' || node.component !== 'sui-icon') continue;
    if (!node.assetId) {
      throw new Error(`sui-icon node "${node.id}" is missing assetId`);
    }
    const asset = iconAssets.get(node.assetId);
    if (!asset) {
      throw new Error(`sui-icon node "${node.id}" references missing icon asset "${node.assetId}"`);
    }
  }

  return { catalog, custom, external };
}

function copyResolved(entries, outDir) {
  fs.mkdirSync(outDir, { recursive: true });
  return entries.map((entry) => {
    const targetPath = path.join(outDir, entry.fileName);
    fs.copyFileSync(entry.sourcePath, targetPath);
    return { ...entry, targetPath };
  });
}

export function resolveCatalog(options) {
  const format = options.format ?? 'android';
  let entries;
  let customIcons = [];
  let externalIcons = [];

  if (options.spec) {
    const seen = new Set();
    const references = referencedIcons(path.resolve(options.spec));
    entries = references.catalog
      .filter(({ name }) => {
        if (seen.has(name)) return false;
        seen.add(name);
        return true;
      })
      .map(({ assetId, name }) => ({ assetId, ...resolveOne(name, format) }));
    customIcons = references.custom;
    externalIcons = references.external;
  } else if (options.name) {
    entries = [resolveOne(options.name, format)];
  } else {
    throw new Error('resolve requires --name or --spec');
  }

  const resolved = options.out ? copyResolved(entries, path.resolve(options.out)) : entries;
  return {
    format,
    count: resolved.length,
    copied: Boolean(options.out),
    icons: resolved,
    customIcons,
    externalIcons,
  };
}

function validateCustomSvg(reference) {
  const errors = [];
  if (!fs.existsSync(reference.sourcePath)) {
    return [`missing custom icon SVG: ${reference.sourcePath}`];
  }

  const svg = fs.readFileSync(reference.sourcePath, 'utf8');
  const hasExpectedDimensions =
    /\bwidth="24"/u.test(svg) &&
    /\bheight="24"/u.test(svg) &&
    /\bviewBox="0 0 24 24"/u.test(svg);
  if (!hasExpectedDimensions) {
    errors.push(`${reference.name} custom SVG does not use a 24x24 canvas`);
  }
  if (!svg.includes('currentColor')) {
    errors.push(`${reference.name} custom SVG has no currentColor foreground`);
  }
  if (/<(?:script|foreignObject|image)\b|(?:href|src)="(?:https?:|data:)/u.test(svg)) {
    errors.push(`${reference.name} custom SVG contains unsupported embedded or external content`);
  }
  if (/<mask\b|fill="white"|fill="#(?:fff|ffffff)"/iu.test(svg)) {
    errors.push(`${reference.name} custom SVG uses a mask or background-colored fake cutout`);
  }
  return errors;
}

function validateAndroidVector(filePath, name) {
  if (!fs.existsSync(filePath)) return [`missing target drawable: ${filePath}`];

  const vector = fs.readFileSync(filePath, 'utf8');
  const errors = [];
  const hasExpectedDimensions =
    /android:width="24dp"/u.test(vector) &&
    /android:height="24dp"/u.test(vector) &&
    /android:viewportWidth="24"/u.test(vector) &&
    /android:viewportHeight="24"/u.test(vector);
  if (!hasExpectedDimensions) errors.push(`${name} target drawable does not use a 24x24 viewport`);
  if (!vector.includes('<path')) errors.push(`${name} target drawable has no path`);
  return errors;
}

function validateBaseCatalog() {
  const errors = [];
  const { catalog, byName } = loadCatalog();
  const manifest = readJson(MANIFEST_PATH);

  if (catalog.icons.length !== 209)
    errors.push(`catalog has ${catalog.icons.length} icons, expected 209`);
  if (manifest.iconCount !== 209)
    errors.push(`manifest iconCount is ${manifest.iconCount}, expected 209`);
  if (byName.size !== catalog.icons.length) errors.push('catalog contains duplicate icon names');
  if (manifest.files.length !== catalog.icons.length) {
    errors.push('manifest and catalog icon counts differ');
  }

  for (const entry of manifest.files) {
    const icon = byName.get(entry.name);
    if (!icon) {
      errors.push(`manifest icon is absent from catalog: ${entry.name}`);
      continue;
    }

    for (const variant of ['svg', 'androidVector']) {
      const declared = entry[variant];
      const filePath = path.join(ASSET_ROOT, declared.path);
      if (!fs.existsSync(filePath)) {
        errors.push(`missing ${variant} file for ${entry.name}: ${declared.path}`);
      } else if (sha256(filePath) !== declared.sha256) {
        errors.push(`hash mismatch for ${declared.path}`);
      }
    }

    const svgPath = path.join(ASSET_ROOT, icon.source.svg);
    if (fs.existsSync(svgPath)) {
      const svg = fs.readFileSync(svgPath, 'utf8');
      if (!/viewBox="0 0 24 24"/u.test(svg))
        errors.push(`${icon.name} does not use a 24x24 viewBox`);
      if (!svg.includes('currentColor')) errors.push(`${icon.name} has no currentColor foreground`);
      if (/<mask\b|<clipPath\b|clip-path=/u.test(svg)) {
        errors.push(`${icon.name} contains unsupported mask or clip structure`);
      }
    }

    const vectorPath = path.join(ASSET_ROOT, icon.source.androidVector);
    if (fs.existsSync(vectorPath)) {
      const vector = fs.readFileSync(vectorPath, 'utf8');
      const hasExpectedDimensions =
        /android:width="24dp"/u.test(vector) &&
        /android:height="24dp"/u.test(vector) &&
        /android:viewportWidth="24"/u.test(vector) &&
        /android:viewportHeight="24"/u.test(vector);
      if (!hasExpectedDimensions) {
        errors.push(`${icon.name} does not use a 24x24 Android viewport`);
      }
      if (!vector.includes('<path')) errors.push(`${icon.name} Android vector has no path`);
      if (/android:(?:fillColor|strokeColor)="(?!#FF000000)[^"]+"/u.test(vector)) {
        errors.push(`${icon.name} Android vector contains a non-monochrome color`);
      }
    }
  }

  return errors;
}

export function verifyCatalog(options = {}) {
  const errors = validateBaseCatalog();
  let references = { catalog: [], custom: [], external: [] };

  if (options.spec) {
    try {
      references = referencedIcons(path.resolve(options.spec));
      for (const reference of references.catalog) {
        try {
          resolveOne(reference.name, 'android');
        } catch (error) {
          errors.push(error.message);
        }
      }
      for (const reference of references.custom) {
        errors.push(...validateCustomSvg(reference));
      }
    } catch (error) {
      errors.push(error.message);
    }
  }

  if (options['target-res']) {
    if (!options.spec) errors.push('--target-res requires --spec');
    const targetRoot = path.resolve(options['target-res']);
    for (const reference of references.catalog) {
      const targetPath = path.join(targetRoot, `${reference.name}.xml`);
      if (!fs.existsSync(targetPath)) {
        errors.push(`missing target drawable: ${targetPath}`);
        continue;
      }
      const source = resolveOne(reference.name, 'android');
      if (sha256(targetPath) !== sha256(source.sourcePath)) {
        errors.push(`target drawable differs from catalog: ${targetPath}`);
      }
    }
    for (const reference of references.custom) {
      const targetPath = path.join(targetRoot, `${reference.name}.xml`);
      errors.push(...validateAndroidVector(targetPath, reference.name));
    }
  }

  return {
    ok: errors.length === 0,
    iconCount: 209,
    checkedReferences: references.catalog.length + references.custom.length,
    catalogReferences: references.catalog.length,
    customReferences: references.custom.length,
    externalReferences: references.external.length,
    errors,
  };
}

function usage() {
  return [
    'Usage:',
    '  node scripts/icon-catalog.mjs search --query <terms> [--limit 8] [--category <id>] [--treatment line|fill]',
    '  node scripts/icon-catalog.mjs resolve --name <ic_name> [--format svg|android] [--out <directory>]',
    '  node scripts/icon-catalog.mjs resolve --spec <design-spec.json> --format android --out <drawable-directory>',
    '  node scripts/icon-catalog.mjs verify [--spec <design-spec.json>] [--target-res <drawable-directory>]',
  ].join('\n');
}

export function run(argv) {
  const { command, options } = parseArgs(argv);
  if (command === 'search') {
    return searchCatalog(options.query ?? options._[0], options);
  }
  if (command === 'resolve') {
    return resolveCatalog(options);
  }
  if (command === 'verify') {
    return verifyCatalog(options);
  }
  throw new Error(usage());
}

const invokedPath = process.argv[1] ? path.resolve(process.argv[1]) : '';
if (invokedPath === fileURLToPath(import.meta.url)) {
  try {
    const result = run(process.argv.slice(2));
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    if (result?.ok === false) process.exitCode = 1;
  } catch (error) {
    process.stderr.write(`${JSON.stringify({ ok: false, error: error.message }, null, 2)}\n`);
    process.exitCode = 1;
  }
}
