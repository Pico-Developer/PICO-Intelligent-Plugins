#!/usr/bin/env node

import { runAgentHookWrapper } from './runtime.mjs';

await runAgentHookWrapper({ host: "opencode2", wrapperUrl: import.meta.url, stage: process.argv[2] });
