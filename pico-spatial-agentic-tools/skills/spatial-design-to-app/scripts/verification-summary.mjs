/*
 * Copyright 2026 PICO Immersive Pte. Ltd.
 * SPDX-License-Identifier: Apache-2.0
 */

import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const SCHEMA_VERSION = 'spatialcraft.compose-verification/v1';
export const REQUIRED_CHECKS = Object.freeze([
  'handoff_receipts',
  'implementation_scan',
  'experimental_api',
  'design_fidelity',
  'gradle_sync',
  'smoke_build',
  'runtime_launch',
  'architecture',
  'unit_tests',
  'design_style',
]);
// All project files are inputs except generated outputs/caches at project or Gradle module roots.
// Same-named directories inside source/assets remain inputs.
// Keep selection here: the wrapper and bundled gate consume this same module.
const GENERATED_DIRECTORIES = new Set([
  '.scratch',
  '.git',
  '.gradle',
  '.kotlin',
  '.idea',
  '.cxx',
  'build',
  'node_modules',
]);
const digest = (bytes) => createHash('sha256').update(bytes).digest('hex');
const sameInputs = (left, right) =>
  left?.target === right?.target &&
  left?.sourceDigest === right?.sourceDigest &&
  left?.designDigest === right?.designDigest;
const scratchPath = (target, name) => path.join(target, '.scratch', name);

// Shared by validation and every Gradle launcher: the nearest ancestor wrapper
// owns both the build invocation and its input tree (including sibling projects).
async function resolveGradleRoot(target, signal) {
  let directory = await fs.realpath(target);
  for (;;) {
    signal?.throwIfAborted();
    try {
      if ((await fs.stat(path.join(directory, 'gradlew'))).isFile()) return directory;
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
    const parent = path.dirname(directory);
    if (parent === directory) return null;
    directory = parent;
  }
}

export async function captureValidationInputs(target, signal, designText) {
  signal?.throwIfAborted();
  const realTarget = await fs.realpath(target);
  const gradleRoot = await resolveGradleRoot(realTarget, signal);
  const hash = createHash('sha256').update('pico-compose-validation-inputs/v2\0');
  hash.update(JSON.stringify(['gradle-root', gradleRoot]));
  await visit(gradleRoot ?? realTarget, '', new Set());
  let design = designText;
  if (design === undefined) {
    try {
      design = await fs.readFile(scratchPath(realTarget, 'design-spec.json'));
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      design = null;
    }
  }
  signal?.throwIfAborted();
  return {
    target: realTarget,
    sourceDigest: hash.digest('hex'),
    designDigest: design === null ? null : digest(design),
  };

  async function visit(directory, relative, ancestors) {
    signal?.throwIfAborted();
    const real = await fs.realpath(directory);
    if (ancestors.has(real)) throw new Error('Validation inputs contain a directory cycle.');
    const branch = new Set([...ancestors, real]);
    const entries = await fs.readdir(directory, { withFileTypes: true });
    entries.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
    const isModule = entries.some((entry) =>
      ['build.gradle', 'build.gradle.kts'].includes(entry.name),
    );
    // Packaged samples may contain Gradle markers; source/assets subtrees take precedence.
    const isSourceTree = relative.split('/').some((part) => part === 'src' || part === 'assets');
    for (const entry of entries) {
      signal?.throwIfAborted();
      const file = path.join(directory, entry.name);
      const name = path.posix.join(relative, entry.name);
      const stat = entry.isSymbolicLink() ? await fs.stat(file) : entry;
      if (stat.isDirectory()) {
        if (GENERATED_DIRECTORIES.has(entry.name) && (!relative || (isModule && !isSourceTree)))
          continue;
        hash.update(JSON.stringify(['directory', name]));
        await visit(file, name, branch);
      } else if (stat.isFile()) {
        hash.update(JSON.stringify(['file', name, digest(await fs.readFile(file))]));
      } else throw new Error(`Unsupported validation input: ${name}`);
    }
  }
}

async function writeJson(file, value) {
  const temporary = `${file}.${randomUUID()}.tmp`;
  try {
    await fs.writeFile(temporary, JSON.stringify(value, null, 2) + '\n');
    await fs.rename(temporary, file);
  } finally {
    await fs.rm(temporary, { force: true });
  }
}

export async function beginVerification(target) {
  await fs.mkdir(path.join(target, '.scratch'), { recursive: true });
  await writeJson(scratchPath(target, 'verification_summary.json'), {
    passed: false,
    clean: false,
    status: 'running',
    stale: true,
  });
  await fs.rm(scratchPath(target, 'verification_inputs.json'), { force: true });
  const invocation = { invocationId: randomUUID(), inputs: await captureValidationInputs(target) };
  await writeJson(scratchPath(target, 'verification_inputs.json'), invocation);
  return invocation;
}

export async function completeVerification(target) {
  const invocation = JSON.parse(
    await fs.readFile(scratchPath(target, 'verification_inputs.json'), 'utf8'),
  );
  const summary = JSON.parse(
    await fs.readFile(scratchPath(target, 'verification_summary.json'), 'utf8'),
  );
  const current = await captureValidationInputs(target);
  const changed = !sameInputs(current, invocation.inputs);
  const skips = summary.skips ?? [];
  const result = {
    ...summary,
    schemaVersion: SCHEMA_VERSION,
    ...invocation,
    checks: Object.fromEntries(
      REQUIRED_CHECKS.map((check) => [check, skips.includes(check) ? 'skipped' : 'passed']),
    ),
  };
  if (changed) {
    Object.assign(result, {
      passed: false,
      clean: false,
      stale: true,
      status: 'failed',
      exit_code: 1,
    });
    result.warnings = [
      ...(summary.warnings ?? []),
      'Validation inputs changed while checks were running.',
    ];
  }
  await writeJson(scratchPath(target, 'verification_summary.json'), result);
  return result;
}

export async function verifyCurrentVerification(summary, target, signal, designText) {
  signal?.throwIfAborted();
  if (
    !summary ||
    summary.schemaVersion !== SCHEMA_VERSION ||
    typeof summary.invocationId !== 'string' ||
    !summary.invocationId ||
    !summary.inputs
  ) {
    throw new Error(
      'Verification summary must identify its validator invocation and current inputs.',
    );
  }
  if (
    summary.clean !== true ||
    summary.passed !== true ||
    summary.status !== 'passed' ||
    summary.stale !== false ||
    !Array.isArray(summary.skips) ||
    summary.skips.length
  ) {
    throw new Error('Verification summary must preserve passed, current, unskipped checks.');
  }
  const checks = summary.checks;
  if (
    !checks ||
    JSON.stringify(Object.keys(checks).sort()) !== JSON.stringify([...REQUIRED_CHECKS].sort()) ||
    REQUIRED_CHECKS.some((check) => checks[check] !== 'passed')
  ) {
    throw new Error('Verification summary does not contain the required passed check set.');
  }
  const current = await captureValidationInputs(target, signal, designText);
  if (!sameInputs(current, summary.inputs)) {
    throw new Error('Verification summary is stale for the current source or accepted design.');
  }
}

if (process.argv[1] && (await fs.realpath(process.argv[1])) === fileURLToPath(import.meta.url)) {
  try {
    const [command, target] = process.argv.slice(2);
    if (!target || !['begin', 'complete', 'gradle-root'].includes(command))
      throw new Error('Usage: verification-summary.mjs <begin|complete> <target>');
    if (command === 'gradle-root') console.log((await resolveGradleRoot(target)) ?? '');
    else if (command === 'begin') await beginVerification(target);
    else await completeVerification(target);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
