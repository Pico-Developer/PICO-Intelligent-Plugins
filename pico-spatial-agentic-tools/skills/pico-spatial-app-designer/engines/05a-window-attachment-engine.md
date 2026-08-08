# Window Attachment Selection Engine

## Goal

Do not select any window attachment by default. First identify the information / operation semantics, then choose among `TabBar`, `Toolbar`, `Subwindow`, `SpatialPopup`, `Augment`, `Sheet / Dialog`, `Coachmark`, a standalone `WindowContainer`, `InlineControl` (placed in-window in situ), or `None`.

Role: `interaction_xr_designer`. Reasoning conclusions are recorded in [`roles/review-templates/interaction-spatial-spec.md`](../roles/review-templates/interaction-spatial-spec.md) (Section 8, Window Attachment Decision Matrix).

## Distinguishing Axis: Placement Mode

The core distinguishing axis of an attachment is the **placement mode**, not size:

- **Docked**: fixed placement that follows the host window. `TabBar` (top center), `Toolbar` (bottom center), `Subwindow` (left / right side, and **always fills the host's height**—the lowest degree of size freedom).
- **Wraparound**: `Augment` supplements the spatial semantics around the associated window; its freedom lies in the **distance and orientation** relative to the window, not custom width/height, and its use is limited to five semantic categories: state, object relationships, direction, progress, or environmental explanation.
- **In-window**: `InlineControl` places the operation directly next to the content it acts on, with a scope limited to the current content / step; it is not an external attachment.

## PICO Capability Semantics

- **TabBar**: floats at the top center of a WindowContainer, used for navigation between different views / pages of the same WindowContainer. Suitable for page-level switching such as "Today / Radar / Seven-Day".
- **Toolbar**: floats at the bottom center of a WindowContainer, used for high-frequency commands or tool modes of the current workspace (measure, annotate, undo, layers, playback control). It must not replace page navigation.
- **Subwindow**: located on the left / right side of a WindowContainer, always filling the host's height. Suitable for a queue, catalog, property inspector, or collaboration panel that needs to stay side by side with the main task.
- **SpatialPopup**: a non-modal temporary interface displayed relative to an anchor and positioned above the current window. Suitable for context menus, filters, low-frequency options, and on-demand details.
- **Augment**: a spatial-semantic supplement around the associated window; it cannot carry primary navigation, long text, or critical forms.
- **Sheet / Dialog**: a temporary interface where the user must focus on handling, confirming, or completing a short workflow; a Dialog emphasizes an important prompt that must be responded to, while a Sheet suits a task panel with a title, content, and bottom actions.
- **InlineControl**: an in-window control tightly attached to the target element, with a scope limited to the current content / step.
- **Coachmark**: a brief instructional / explanatory note anchored to the UI; it does not carry regular navigation or a persistent workspace.
- **None**: when there is no additional spatial value or persistent need, do not add a window attachment.

## Decision Order

1. Is this navigation between different pages / views? Candidate `TabBar`.
2. Is this a persistent, high-frequency command or tool within the current workspace? Candidate `Toolbar`.
3. Is this an auxiliary workspace that needs to stay side by side at full height? Candidate `Subwindow`.
4. Is this anchored, temporary, on-demand non-modal content? Candidate `SpatialPopup`.
5. Is this expressing spatial state or object relationships around the window? Candidate `Augment`.
6. Is this a short task that needs focused handling or confirmation? Candidate `Sheet / Dialog`.
7. Does this operation act only on the current content / step and should it be placed in situ? Candidate `InlineControl`.
8. Is this a first-use hint? Candidate `Coachmark`.
9. When there is no clear value, choose `None`.

## Output (direct description, no longer bound to a Schema)

Give the window attachment decision matrix in structured Markdown, specifying for each item:

- **need**: the information / operation semantics to be solved;
- **placement mode**: Docked / Wraparound / In-window;
- **selectedType**: the chosen attachment type (or `None`);
- **hostContainerId**: the host window;
- **semanticRole / persistence / interactionFrequency**: semantic role, persistence, interaction frequency;
- **rationale**: the reason for the selection;
- **rejectedAlternatives**: rejected options and reasons, **which must explicitly compare `InlineControl` (in-situ placement) with `None` (no attachment)**;
- **validationPlan**: the on-device validation plan.

## Prohibitions

- continuing to use a certain attachment type in a new project just because a case study used it;
- treating a Toolbar as the bottom navigation of every app;
- treating a TabBar as a tool command area;
- adding attachments that have no task value just for a sense of space;
- failing to make an explicit comparison between "adding an attachment" and `None` (as well as `InlineControl`);
- having the same content appear simultaneously in the TabBar, the Toolbar, and in-window navigation (including InlineControl).
