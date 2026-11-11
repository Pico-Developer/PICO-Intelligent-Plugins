# Already Open GUI Session Admission

Start the public Workflow and let its Session establishment inspect the open GUI.
`managedByCli=false` or `mcpServerRunning=false` alone does not prove admission is impossible.

The Workflow verifies the project lock PID, live process, installation, local instance
registry and process start identity. It rechecks evidence under the ownership state
lock and claims the GUI before connecting MCP. Another Owner prevents admission.
It saves the active scene before preparing the task scene. Saving must succeed.

The admitted GUI keeps its mode under the same Run Supervisor, lease and fencing token.
Scene editing, evidence, operation receipts and delivery use the managed Workflow.
Terminal cleanup leaves the user-visible GUI open.

On `EDITOR_GUI_ADOPTION_UNAVAILABLE`, ask the user to save and close that window,
then retry through the public Workflow. Missing registry information, an unavailable
process identity or changed evidence prevents admission. Never force-close the
window or start a standalone backend to bypass this result.
