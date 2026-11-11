# Cross-Platform Execution Reliability

Apply this contract to every command in the release workflow on every host platform. It owns
execution-context selection, dependent-step failure propagation, and long-running process
observation. Provider Skills still own their command syntax and structured business errors.

## Execution-context gate

Classify the exact command channel before using it. A workspace sandbox may allow ordinary project
files while denying `.git/index`, a host credential store, the system temporary directory, or
another path outside the workspace. One successful capability is not evidence for another.

- Run Auth and Release status checks in the same channel that will run later Release operations.
  `STORE_UNAVAILABLE` or an equivalent local-store permission error means that channel cannot read
  the host credential store; it does not mean the user is logged out. Preserve the error and move
  the operation to an approved host channel. Do not clear, refresh, or replace credentials.
- Read-only Git commands do not prove that the channel can create `.git/index.lock`. Do not create
  or remove an index lock as a probe. At the first approved Git mutation, treat `Permission denied`
  or `Access is denied` for the index or lock as `GIT_INDEX_CONTEXT_UNAVAILABLE`. Stop dependent
  commit/push work and resume that same approved mutation only through a channel authorized for the
  exact project and paths. Do not diagnose repository corruption or retry in the same sandbox.
- Do not assume `C:\tmp`, `C:/tmp`, `/tmp`, a drive or filesystem root, or another host path is
  writable. Prefer the owning CLI's output-directory creation. When an Agent-owned directory is
  still necessary, choose a task-scoped location allowed by the selected channel, resolve its exact
  path, create it as one fail-closed step, and verify it is a directory before any dependent script
  or file operation.
- A change of channel does not broaden release scope. Preserve the approved project, paths, app and
  version IDs, repository, and operation. Use the Host's normal approval flow when the authorized
  channel requires approval.

## Command outcome contract

Prefer a process API that accepts an argument array and returns stdout, stderr, and exit status as
separate values. Do not join dependent operations in one shell expression or rely on its last
statement to represent earlier work.

Keep the business result and shell transport result distinct:

- `operation_exit_code` is the owning native command's status.
- `shell_exit_code` must be nonzero when the operation failed.
- `completed` means the requested business step completed successfully, not merely that the shell
  produced a report.
- A structured `ok: false` result remains failure even if a formatter exited zero. Conversely, a
  tool-level timeout is not proof that the child business process failed.

Start a dependent step only after the prerequisite returned zero and its required artifact or
structured result was verified. Parsing and bounded evidence emission may run after failure, but a
successful formatter, evidence write, or cleanup step never converts the prerequisite into success.

### PowerShell

When Windows PowerShell 5.1 or PowerShell 7 is the only available runner:

1. Set `$ErrorActionPreference = 'Stop'` for cmdlets, and add `-ErrorAction Stop` to a cmdlet whose
   failure controls the workflow.
2. Invoke one native process, capture `$LASTEXITCODE` immediately, and preserve it before parsing,
   redacting, formatting, or writing evidence.
3. Cleanup must retain the original status. End the shell invocation with `exit $commandStatus`
   when it is nonzero.
4. A successful `ConvertTo-Json`, `Set-Content`, or `Out-File` never decides the status of an earlier
   business command.

### POSIX shells

When `sh`, Bash, or zsh is the only available runner:

1. Invoke one native process and capture `$?` immediately, before a pipeline, conditional formatter,
   cleanup command, or evidence write. Do not use `PIPESTATUS` or `pipestatus` as a portable repair.
2. Do not rely on `set -e` alone: its behavior changes inside conditions, functions, substitutions,
   and pipelines. Use an explicit `if command; then command_status=0; else command_status=$?; fi`
   boundary for a workflow-controlling command.
3. Preserve the original status through redaction and cleanup, then `exit "$command_status"` when
   it is nonzero.
4. A successful `jq`, `tee`, `printf`, redirection helper, or evidence write never decides the
   status of an earlier business command.

## Long-running process lifecycle

Clean Gradle dependency resolution and other release preparation may exceed short Agent command
deadlines on any operating system. Use one managed invocation and preserve its identity from start
through terminal result.

1. Before launch, compare the Host observation limit with the repository's clean-build allowance.
   Use a 30-minute overall allowance by default for an isolated Gradle build unless repository
   evidence requires a larger bounded value. If the Host cannot observe for that long, start the
   build through a managed process facility that returns durable process identity and log paths;
   do not launch it through a shorter blocking call and reconstruct the result later.
2. Record the process ID, start time, command fingerprint, isolated `GRADLE_USER_HOME`, empty Maven
   local path, stdout/stderr log paths, and the platform-native ownership handle without exposing
   environment secrets. Stream or persist output while the process runs.
3. Poll the same process identity. Do not start another Gradle invocation to answer whether the
   first one finished. A cache-reusing rerun is recovery evidence only and never replaces the
   original empty-cache result.
4. Treat an observer deadline as `OBSERVER_TIMEOUT`, with process state `running`, `terminated`, or
   `unknown`. It is not `BUILD_FAILED`. Continue observation only when the same process identity is
   still owned. If ownership is lost, source readiness remains unproven.
5. If cancellation or the overall deadline requires termination, stop only the complete process
   tree owned by that invocation. Record the termination separately from a natural process exit.
6. Accept isolated-build success only when the same invocation supplies both exit code zero and its
   successful terminal build evidence. `BUILD SUCCESSFUL` without the process exit code, or exit
   zero from a later cache-warm rerun, is incomplete evidence.

### Platform-specific process ownership

- On Windows, retain an owned Job Object or equivalent process-tree handle that covers the launcher,
  Python helper, Gradle wrapper, Java children, and Gradle daemon children. Terminate that owned tree,
  never processes selected only by executable name.
- On macOS and Linux, start the invocation in an owned process group or session. Send signals only
  to that group; use a bounded `TERM` grace period before `KILL`, and record which signal established
  the terminal state.
- If the available Host cannot retain platform-native ownership across observations, stop before
  launching the long process and report an execution-capability blocker.

## Stable failure classifications

| Evidence                                                      | Classification                       | Recovery                                                                                     |
| ------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------- |
| Release `STORE_UNAVAILABLE` or local-store permission failure | `HOST_CREDENTIAL_STORE_UNAVAILABLE`  | Use an approved host channel; do not relogin automatically                                   |
| `.git/index.lock` permission failure                          | `GIT_INDEX_CONTEXT_UNAVAILABLE`      | Stop Git dependents and resume the same mutation in the approved project-scoped host channel |
| Temporary-directory permission failure                        | `TEMP_DIRECTORY_CONTEXT_UNAVAILABLE` | Select an allowed task-scoped path; do not run file/camera dependents                        |
| Tool exit `124` or an observation deadline with no child exit | `OBSERVER_TIMEOUT`                   | Observe the same owned process, or report terminal state unknown                             |

## Verification

- Every failed prerequisite produces a nonzero outer shell status and no dependent side effect.
- PowerShell and POSIX-shell regression cases both preserve the owning command's failure.
- Release local-store permission errors are not reported as logged-out credentials.
- Git index permission errors do not trigger lock deletion, repository repair, commit, or push.
- A temporary-directory creation failure prevents script generation, file writes, and camera work.
- An observer timeout preserves the original process identity or reports source readiness unproven.
- Windows tree and POSIX process-group termination affect only the owned invocation.
- A clean-cache build passes only with exit zero and terminal success from the same invocation.
