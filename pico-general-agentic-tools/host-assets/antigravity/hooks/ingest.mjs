#!/usr/bin/env node

import { runAgentHookWrapper } from './runtime.mjs';

await runAgentHookWrapper({ host: "antigravity", wrapperUrl: import.meta.url, stage: process.argv[2] });
