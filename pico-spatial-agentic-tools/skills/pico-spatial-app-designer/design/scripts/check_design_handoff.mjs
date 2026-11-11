import fs from 'node:fs/promises';
import path from 'node:path';
import { parseArgs } from 'node:util';
import { checkDesignHandoff } from './design-handoff.mjs';

let issues = [];
try {
  const { values, positionals } = parseArgs({
    allowPositionals: true,
    options: { target: { type: 'string' }, 'asset-root': { type: 'string' } },
  });
  if (positionals.length !== 1)
    throw new Error(
      'Usage: node check_design_handoff.mjs <design-spec.json> --target <project-directory>',
    );
  const specPath = path.resolve(positionals[0]);
  const base = path.dirname(specPath);
  const projectRoot = path.resolve(
    values.target ?? (path.basename(base) === '.scratch' ? path.dirname(base) : base),
  );
  const spec = JSON.parse(await fs.readFile(specPath, 'utf8'));
  let preview;
  try {
    if (typeof spec?.metadata?.preview !== 'string' || !spec.metadata.preview.trim())
      throw new Error('Missing metadata.preview.');
    preview = await fs.readFile(
      path.resolve(base, spec.metadata.preview.replaceAll('\\', '/')),
      'utf8',
    );
  } catch (error) {
    issues.push({
      level: 'error',
      code: 'preview-file',
      path: '$.metadata.preview',
      message: String(error),
    });
  }
  issues.push(
    ...(await checkDesignHandoff({
      spec,
      preview,
      projectRoot,
      specPath,
      ...(values['asset-root'] ? { assetRoot: path.resolve(values['asset-root']) } : {}),
    })),
  );
} catch (error) {
  issues.push({ level: 'error', code: 'input', path: '$', message: String(error) });
}
console.log(
  JSON.stringify(
    { status: issues.length ? 'FAIL' : 'PASS', errors: issues.length, issues },
    null,
    2,
  ),
);
process.exitCode = issues.length ? 1 : 0;
