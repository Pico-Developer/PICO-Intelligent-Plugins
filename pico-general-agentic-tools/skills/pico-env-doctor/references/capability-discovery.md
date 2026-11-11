## Capability-discovery rule

## Contents

- [Command and Host discovery](#command-and-host-discovery)
- [Result shape and diagnosis scope](#result-shape-and-diagnosis-scope)
- [Full-chain version overview (top of doctor output)](#full-chain-version-overview-top-of-doctor-output)
- [Task readiness and authorized repair](#task-readiness-and-authorized-repair)

`pico-cli doctor` is the top-level environment summary when the installed build
exposes it. Root doctor is diagnostic by default but not unconditionally
read-only. When the release catalog cache is missing, stale, or incompatible,
it may prepare the cache and add conditional `host-write`, `network`, and
`long-running` effects. In a strictly read-only context, skip root doctor.
Instead, inspect the nearest project-local `.pico-env.json` (or
`~/.pico/.pico-env.json`), the Host's local plugin manifest or registry entry,
and installed plugin files. These static checks do not refresh the release
catalog and therefore cannot verify catalog freshness. Root doctor should report
CLI runtime health and point to module-specific doctors or fallback commands,
not perform setup, plugin updates, package installs, or long-running MCP launches
by itself.

The CLI can grow module doctors over time, but a user's installed build may not
expose every command. Discover capabilities before using them; this keeps the
workflow useful across public, internal, old, and newly released CLI builds.

### Command and Host discovery

Start with bootstrap and help discovery when `pico-cli` is available:

```bash
node --version
npm --version
command -v pico-cli || echo "pico-cli not on PATH"
pico-cli --version
pico-cli --help
pico-cli doctor --help
pico-cli setup --help
pico-cli update --help
pico-cli plugin update --help
pico-cli knowledge --help
pico-cli knowledge doctor --help
```

Before the first invocation of each doctor command selected for the current
check, run that exact command's `--help` form. For example,
`pico-cli --help` does not replace `pico-cli doctor --help`, and
`pico-cli knowledge --help` does not replace `pico-cli knowledge doctor --help`.
Do not infer support from another command's help or from this Skill's examples.

Current CLIs report Host plugin diagnostics through root `pico-cli doctor` (the
`plugin.doctor` check) and no longer expose `plugin doctor`, `plugin install`,
`plugin uninstall`, or `plugin list`. When one of those commands fails as
removed, follow the replacement the error names; do not retry it.

Do not invoke a doctor command with `--agent-tool` until its own help has shown
the accepted values. A general environment check does not need `--agent-tool`;
omit it unless the user requested a specific Host or the check must inspect one
explicitly. Host display names, executable names, and `pico-cli` identifiers are
different namespaces:

| Host        | Canonical `--agent-tool` | Executable           | Accepted alias |
| ----------- | ------------------------ | -------------------- | -------------- |
| Claude Code | `claude-code`            | `claude`             | `claude`       |
| Trae CLI    | `traecli`                | `traecli` or `traex` | none           |

Use the canonical identifier in generated commands. Treat the command's current
`--help` output as authoritative for all other Hosts and aliases; do not derive
an identifier from an executable name. The `claude` compatibility alias belongs
only to the current `--agent-tool` option. The deprecated `--tool` option accepts
canonical Host IDs only, so `--tool claude` is invalid; `trae` remains invalid for
both options.

If the installed CLI exposes doctor commands, prefer JSON for machine-readable
results and plain output for a quick human summary:

```bash
pico-cli doctor --format json
pico-cli knowledge doctor --format json
pico-cli primer doctor --format json
```

### Result shape and diagnosis scope

Expected doctor JSON shape, when supported, follows the CLI `tool-result`
contract:

```json
{
  "tool_name": "doctor",
  "tool_status": "SUCCESS|PARTIAL|FAILED",
  "summary": "human-readable one-line result",
  "data": {
    "targetPlatform": "spatial|unity|null",
    "hostPlatform": "darwin|linux|win32",
    "project": {
      "root": "/abs/project",
      "basis": "explicit|configured-ancestor|engineering-root|cwd",
      "platform": "spatial|unity|null",
      "configured": true,
      "mixed": false
    },
    "checks": [
      {
        "id": "runtime",
        "status": "ok|warn|error|skip",
        "checks": []
      }
    ]
  },
  "errors": [],
  "resources": [],
  "meta": { "format": "json", "truncated": false }
}
```

Root doctor diagnoses two levels and groups `data.checks[]` by them:

- runtime: host runtime basics, such as Node.js.
- common-doctors ("User-level doctors"): checks that never depend on a project
  platform, such as npm, emulator guidance, perf readiness, setup state, MCP
  knowledge, managed CLIs, `unity.cli` (a warning outside Unity projects), and
  `plugin.doctor` for the user-level general plugin.
- spatial-doctors, unity-doctors, or project-doctors ("<Platform> project
  doctors"): checks for the resolved project, such as primer-cli/PICO SDK and
  Spatial Editor for Spatial projects, `project.configure`,
  `project.plugin.doctor` for the project's platform plugin,
  `project.context.doctor` for the managed AGENTS.md routing, `project.general`
  (`PROJECT_HOST_GENERAL_MISSING`: a project Host lacks the user-level general
  plugin; run the reported `pico-cli setup --agent-tool ...` command),
  `project.gitignore`, and `project.legacy`. The section is omitted when the directory is not a
  project, such as the user home or an unrelated folder.

`data.project` (or `null`) names the resolved project root, how it was found,
its platform, whether `pico-cli project configure` has configured it, and
whether its Hosts record more than one platform (`PROJECT_PLATFORM_MIXED`).

### Full-chain version overview (top of doctor output)

When the authorized doctor path is selected, `pico-cli doctor` renders a compact
version overview at the **top** of its report, above the grouped checks. This is
the single full-chain status board — there is **no separate `status` command**;
do not look for one or invent one. Read this overview first and report it
verbatim; it is the fastest answer to "what versions am I on across the
toolchain". Under the strictly read-only fallback, this overview is not
available: use the static checks described below and report the unverified
fields instead of inventing overview values.

The overview covers six rows (plus **Project plugin** for a configured project).
Aggregating them triggers no extra capability beyond the doctor checks the run
already collected, but obtaining the overview still requires running root doctor
under its conditional-effects contract:

- **CLI**: installed `pico-cli` version.
- **Plugin**: the user-level general plugin identity/version recorded by
  `pico-cli setup`. A **Project plugin** row follows when the project records a
  platform plugin. Both are declared state, not proof of the plugin loaded by
  the current Host session. Read the `plugin.doctor` and `project.plugin.doctor`
  checks' `details.result` (`scope`, `envPath`, and per-Host findings) before
  acting; when Host records disagree, do not treat the overview's single value
  as a complete machine-wide answer.
- **SDK**: for Spatial, the bound SDK/BOM version read from the target project
  (`no spatial project in current directory` / `spatial project found, version unresolved`
  when it cannot be read). For Unity, the current CLI reads only the target root's
  `package.json.version`, not its installed Unity SDK packages. A valid Unity project without
  that file can therefore report `no-project`, and a returned version can belong to an unrelated
  root package. Report the raw field with this limitation; establish Unity SDK evidence separately
  from the configured mode, `Packages/manifest.json`, `Packages/packages-lock.json`, and installed
  package metadata. Do not infer SDK readiness or knowledge alignment from this overview field.
- **PICO development knowledge**: the PICO development knowledge version.
- **Emulator**: the highest installed PICO emulator bundle version.
- **Editor**: the highest installed Spatial Editor version.

In plain output the overview is an `Overview` block of `- <Row>: <value>` lines
(`unknown` when a row cannot be resolved); in JSON it is the `data.overview`
object with `cli`, `pluginName`, `sdk`, `picoDevelopmentKnowledge`, `emulator`,
and `editor` fields, plus `projectPluginName` for a configured project. The Emulator and Editor rows come from checks that root
doctor already runs (common-doctors and the Spatial project section), so a normal
`pico-cli doctor` run from a configured Spatial project is enough to populate
the available values. You do not need to run `emulator doctor` / `editor doctor` separately
just to fill the overview. Uninstalled optional tools have null JSON overview values and their
plain overview rows are omitted; inspect the detailed checks for absence/readiness guidance.
Do not synthesize missing rows or treat an omitted row as proof of readiness or a failure.

On the authorized doctor path, root doctor always runs the user-level checks. It resolves the project the same
way `project configure` does: `--project <path>` first (parent directories are
not searched), otherwise the nearest configured ancestor of the current
directory, then the Spatial or Unity engineering root, then the current
directory. The project platform comes from the project's Host records,
otherwise from its engineering files; never from a knowledge selection. Pass
`--project` when the Agent session does not run inside the target project:

```bash
pico-cli doctor --format json --project <path>
pico-cli doctor --format json --project <path> --platform <spatial|unity>
```

The optional `--platform` value asserts the expected project platform; it never
selects or overrides the target. If the assertion differs, root doctor reports
a `doctor.platform` error and preserves the actual detected `targetPlatform`;
checks for that actual platform still run. Resolve the target or assertion mismatch
before platform-specific repair. Do not treat `--platform` as a filter or a repair
safety interlock; a null target means no project platform was resolved.

In the user home, `~/.pico*`, or a directory with no project files, root doctor
reports only the user level. Apart from conditional release-catalog cache
preparation, it does not write to the user or project configuration unless an
authorized fix command is run.

Use status consistently. The following status summary applies to ordinary root doctor;
`doctor --fix` can return SUCCESS with advisory warnings remaining. After repairs inspect the
remaining checks and verify the requested capability rather than treating SUCCESS as all-green.

### Task readiness and authorized repair

- `SUCCESS`: no reported error or warning; skipped checks can still be present and are not readiness evidence.
- `PARTIAL`: at least one warning and no error; inspect which capability it affects.
- `FAILED`: at least one check reported `error`. This does not by itself prove
  the app cannot build, install, or run.

Never infer "the app cannot run" from the top-level status alone. Read
`data.checks[]` and identify which check carries `error`, then judge whether that
check is on the path the user's task actually needs (runtime, SDK/Primer,
Android SDK, emulator/device, Editor) or is project setup only.
`project.context.doctor` is project setup: it reports whether the Agent Host
loads PICO AGENTS routing for this project, is always a `warn` when incomplete,
and never blocks build, install, or launch. Plugin doctor reports the same gap as
the non-blocking `PLUGIN_PROJECT_CONTEXT_INCOMPLETE` finding.

When reading plain doctor output, use the bracketed labels as the action signal:

- `[ok]`: healthy.
- `[skip]`: intentionally not checked or optional for the current workflow; do
  not treat this as a failure unless the skipped capability is required for the
  user's task.
- `[warn]`: checked and incomplete, but not an automatic blocking repair. Report
  the finding and `next:` guidance so the developer can decide whether to
  configure that part now.
- `[error]`: a blocking issue. Inspect `repair[]`: `mode=automatic` identifies a
  fix supported by root `doctor --fix`, while `mode=manual` identifies an
  explicit operator action or module-level command. Run either only when the
  repair authorization rule allows it.

For JSON output, treat `status: "error"` the same as a plain `[error]` line.
Use `repair[]`, `errors[]`, the check `details`, and any `nextAction` value to
choose the smallest follow-up command. Do not assume every error is automatically
repairable. Do not continue into emulator/device/MCP/project work while a
required check is `[error]` or `status: "error"`.

Use automatic root or project-context fixes only when their doctor result marks
the repair as supported. Root doctor may conditionally prepare the release
catalog cache as described above, but its embedded `plugin.doctor` and
`project.plugin.doctor` checks do not execute the lifecycle repair suggested by
a plugin finding. Follow its explicit `nextAction`:

```bash
pico-cli doctor --format json --project <path> --agent-tool <host> --fix
```

Carry the same explicit engineering `--project` and, when supplied, resource `--workspace-root`
through diagnosis, approved fixes, and configuration. Do not replace that target with the session cwd.

`--fix` repairs user-level findings, including `unity.cli`, whether or not a
project is resolved, and repairs the knowledge selection in the level that
selects it: the project when its `.pico-env.json` records knowledge fields,
otherwise the user level. It does not change project plugins, project context,
or `.gitignore`. Follow each project's finding-specific `nextAction`; a `project.*`
prefix alone does not imply configure can repair it. Use reported setup for `project.general`,
and configure for missing/drifted project resources or context when that finding requests it:

```bash
pico-cli project configure --platform <spatial|unity> --project <path> --agent-tool <host> --yes --format json [--workspace-root <session-root>]
```

`plugin.doctor` reads the user-level `~/.pico/.pico-env.json`;
`project.plugin.doctor` reads the project `.pico-env.json`. A Host missing the
user-level general plugin receives a `pico-cli setup` recommendation; a Host
missing its project platform plugin or project context receives a
`pico-cli project configure` recommendation; an outdated plugin receives a
`pico-cli plugin update` recommendation. Doctor never executes them.

Older CLI builds may still expose `plugin doctor`, `plugin doctor --fix`, and
`plugin install`. Do not use `--fix` on those builds: its repair dispatch differs
by version and may invoke broader setup or an incorrect plugin lifecycle
operation. Read the finding and run its explicit `nextAction` instead.

Avoid repair loops. For any one finding, run its authorized repair **at most
once**, then re-run the relevant doctor to re-verify. If the same `[error]` /
`status: "error"` remains, do not run that repair again — and do not switch to a
different command or a re-worded variant hoping to work around the same finding.
Stop and report the remaining blocker, the command already attempted, and the
latest doctor output and exact host-visible error. Many findings are conditions
`pico-cli` cannot fix by re-running (missing toolchain, offline registry, host
trust); repeating commands only wastes effort without resolving them.

If root or module doctor commands are absent, do **not** invent them and do not
treat their absence as a failed environment by itself. Fall back to the supported
checks and repair commands below, then report which doctor-style commands were
unavailable.
