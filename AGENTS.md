# PICO Intelligence Plugin Guidance

This file provides agent-facing guidance for the installed PICO intelligence marketplace context.

Agents may read this guidance while operating inside a user's own project directory. Treat the current working directory as the user's application project unless the user or local project files prove otherwise.

## Working Boundary

- Use the installed PICO plugins as supplemental guidance for the PICO development platform configured for the current project.
- Do not assume the user's project is the plugin source, a marketplace root, or a plugin package.
- Do not expect plugin manifests, plugin payload folders, or bundled `skills/` directories to exist inside the user's project unless they are actually present.
- Prefer the user's project files, project-local `AGENTS.md`, build scripts, and package metadata for repository-specific commands and constraints.
- When plugin guidance conflicts with project-local instructions, follow the project-local instructions and explain the conflict if it affects the task.

## How to Use This Guidance

- When the user asks to install PICO CLI or configure PICO development tools for the first time, read and follow `docs/pico-cli-installation-guide.md` before running setup. This bootstrap guide is available before plugin Skills are installed.
- [`pico-general-agentic-tools`](pico-general-agentic-tools/AGENTS.md) is the entry plugin that
  `pico-cli setup` installs once per user. It provides the `pico-project-setup`, `pico-cli`, and
  `knowledge-query` Skills and the user-level `pico-dev-knowledge`, `pico-spatial-editor`, and
  `unity-mcp` servers. Verify Host discovery and backend readiness before using their tools.
- When PICO development starts in a project whose platform plugin is not configured yet, or the
  user wants to create a PICO Spatial or Unity project, use `pico-project-setup`. It detects the
  project and configures the matching platform plugin into that project.
- In a configured PICO Spatial SDK project, follow
  [`pico-spatial-agentic-tools`](pico-spatial-agentic-tools/AGENTS.md); in a configured PICO Unity
  project, follow [`pico-unity-agentic-tools`](pico-unity-agentic-tools/AGENTS.md).
- Select the most specific installed skill from the plugin that matches the user's project platform and request.
- Load skill instructions and bundled references through the host/plugin mechanism rather than by assuming local paths in the user's project.
- Keep implementation, build, install, launch, and verification work scoped to the user's project unless explicitly asked to inspect or maintain the plugin itself.
- For setup/update issues, prefer `pico-cli setup`, `pico-cli project configure`, `pico-cli plugin update`, and `pico-cli doctor` over manual edits to host plugin state.
