# PICO Spatial Plugin Guidance

This file provides agent-facing guidance for the installed PICO intelligence plugin context.

Agents may read this guidance while operating inside a user's own project directory. Treat the current working directory as the user's application project unless the user or local project files prove otherwise.

## Working Boundary

- Use the installed PICO plugin as supplemental guidance for PICO OS spatial development workflows.
- Do not assume the user's project is the plugin source, a marketplace root, or a plugin package.
- Do not expect plugin manifests, plugin payload folders, or bundled `skills/` directories to exist inside the user's project unless they are actually present.
- Prefer the user's project files, project-local `AGENTS.md`, build scripts, and package metadata for repository-specific commands and constraints.
- When plugin guidance conflicts with project-local instructions, follow the project-local instructions and explain the conflict if it affects the task.

## How to Use This Guidance

- Select the most specific installed PICO Spatial skill for the user's request.
- Load skill instructions and bundled references through the host/plugin mechanism rather than by assuming local paths in the user's project.
- Keep implementation, build, install, launch, and verification work scoped to the user's project unless explicitly asked to inspect or maintain the plugin itself.
- For setup/update issues, prefer `pico-cli setup`, `pico-cli plugin update`, and the plugin audit workflow over manual edits to host plugin state.
