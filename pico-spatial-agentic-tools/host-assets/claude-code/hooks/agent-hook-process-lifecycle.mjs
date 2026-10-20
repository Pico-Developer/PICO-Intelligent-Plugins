/*
 * Copyright 2026 PICO. All rights reserved.
 *
 * NOTICE: All information contained herein is, and remains the property of PICO.
 * The intellectual and technical concepts contained herein are proprietary to PICO
 * and may be covered by patents, patents in process, and are protected by trade
 * secret or copyright law. Dissemination of this information or reproduction of
 * this material is strictly forbidden unless prior written permission is obtained
 * from PICO.
 */

import { spawn } from 'node:child_process';

const WINDOWS_HELPER_TIMEOUT_MS = 1_000;

export async function terminateAgentHookChildTree(child, options = {}) {
  if (!child?.pid) {
    child?.kill?.();
    return;
  }
  if ((options.platform ?? process.platform) !== 'win32') {
    const processGroupId = child.pid;
    try {
      process.kill(-processGroupId, 'SIGTERM');
    } catch {
      child.kill();
    }
    if (await waitForProcessGroupExit(processGroupId, 500)) return;
    try {
      process.kill(-processGroupId, 'SIGKILL');
    } catch {
      // The process group has already exited.
    }
    await waitForProcessGroupExit(processGroupId, 1_000);
    return;
  }

  await terminateWindowsTree(child, options.spawnProcess ?? spawn);
}

async function terminateWindowsTree(child, spawnProcess) {
  await new Promise((resolve) => {
    let helper;
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      // Keep the error listener until the helper closes: a kill error can arrive
      // after our deadline, and must not turn advisory cleanup into an uncaught error.
      helper?.unref?.();
      resolve();
    };
    const timer = setTimeout(() => {
      tryKill(child);
      tryKill(helper);
      finish();
    }, WINDOWS_HELPER_TIMEOUT_MS);
    timer.unref?.();
    try {
      helper = spawnProcess(
        process.env.ComSpec || 'cmd.exe',
        ['/d', '/s', '/c', 'taskkill', '/PID', String(child.pid), '/T', '/F'],
        { stdio: 'ignore', windowsHide: true },
      );
      helper.on('error', () => {
        if (finished) return;
        tryKill(child);
        finish();
      });
      helper.once('close', (code) => {
        if (finished) return;
        if (code !== 0) tryKill(child);
        finish();
      });
    } catch {
      tryKill(child);
      finish();
    }
  });
}

function tryKill(child) {
  try {
    child?.kill?.();
  } catch {
    // Cleanup is advisory even when the platform refuses termination.
  }
}

async function waitForProcessGroupExit(processGroupId, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (isProcessGroupAlive(processGroupId)) {
    if (Date.now() >= deadline) return false;
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
  return true;
}

function isProcessGroupAlive(processGroupId) {
  try {
    process.kill(-processGroupId, 0);
    return true;
  } catch (error) {
    return error?.code !== 'ESRCH';
  }
}
