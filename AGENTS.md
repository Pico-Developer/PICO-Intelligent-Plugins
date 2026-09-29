# PICO Intelligence Plugin Guidance

This file provides agent-facing guidance for the installed PICO intelligence marketplace context.

Agents may read this guidance while operating inside a user's own project directory. Treat the current working directory as the user's application project unless the user or local project files prove otherwise.

## Working Boundary

- Use the installed PICO plugin as supplemental guidance for the selected PICO development platform.
- Do not assume the user's project is the plugin source, a marketplace root, or a plugin package.
- Do not expect plugin manifests, plugin payload folders, or bundled `skills/` directories to exist inside the user's project unless they are actually present.
- Prefer the user's project files, project-local `AGENTS.md`, build scripts, and package metadata for repository-specific commands and constraints.
- When plugin guidance conflicts with project-local instructions, follow the project-local instructions and explain the conflict if it affects the task.

## How to Use This Guidance

- When the user asks to install PICO CLI or configure PICO development tools for the first time, read and follow `docs/pico-cli-installation-guide.md` before running setup. This bootstrap guide is available before plugin Skills are installed.
- Route PICO Spatial SDK projects to
  [`pico-spatial-agentic-tools`](pico-spatial-agentic-tools/AGENTS.md).
- Route PICO Unity projects to [`pico-unity-agentic-tools`](pico-unity-agentic-tools/AGENTS.md).
- Treat [`pico-general-agentic-tools`](pico-general-agentic-tools/AGENTS.md) as the shared companion
  plugin installed with either platform. Route platform-neutral PICO knowledge queries to its
  `knowledge-query` Skill; users do not select this plugin as a separate development platform.
- Select the most specific installed skill from the plugin that matches the user's project platform and request.
- Load skill instructions and bundled references through the host/plugin mechanism rather than by assuming local paths in the user's project.
- Keep implementation, build, install, launch, and verification work scoped to the user's project unless explicitly asked to inspect or maintain the plugin itself.
- For setup/update issues, prefer `pico-cli setup`, `pico-cli plugin update`, and `pico-cli plugin doctor` over manual edits to host plugin state.
