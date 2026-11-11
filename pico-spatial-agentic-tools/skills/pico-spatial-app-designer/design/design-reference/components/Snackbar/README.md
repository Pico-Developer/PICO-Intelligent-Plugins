# Snackbar

A transient message at the bottom of the window. `Thickest` material; at least 56 high, at most 800 wide, 80 above the bottom edge, centered.

## Layout
- Radius 32 for one line, 20 once it wraps (height over 64).
- Padding: 20/16 horizontal/vertical; 20 start and 16 end with an action; 18 start and 20 end with a leading icon. The icon has a 16 end gap.
- Message `titleMedium` (16/20, 600, 24 line height when wrapped) in `labelPrimary`; description `bodySmall` in `labelTertiary`.
- The action is a Min `Button` on `fillSecondary` with `labelPrimary` text, 16 after the text.
- Shown for 3000ms by default, one at a time, 16ms between them. Window containers only.

## When to use
- **Use for:** confirming something that happened, with at most one action: Saved, Undo.
- **Don't use for:** a decision (use `AlertDialog`), an error that blocks (use `AlertDialog`), a hint (use `Coachmark`).
- **Alternatives:** `AlertDialog`, `Coachmark`.
- **Do:** keep the message to one short line; offer Undo for destructive results.
- **Don't:** use it for information that must not be missed or stay on screen.

## Web API
- `<sui-snackbar-host>` attributes: `position` (`top`, default bottom). Call `host.show(message, options)`; options: `description`, `leadingIcon`, `action`, `duration` (ms), `enableBackgroundMaterial`, `backgroundColor`. It returns a Promise of `'action-performed'` or `'dismissed'`.
- Events: `snackbar-result` (`detail.result`).

## Preview icon

The preview pairs “Saved to Library” with the local `ic_check_circle` success icon (`ICON7-P240`) at 24px and the existing Undo action. The icon keeps the default foreground, with the built-in 16px gap before the message. This is a component appearance/action example; it does not simulate a file-saving workflow.

```js
host.show('Saved to Library', { leadingIcon: 'ic_check_circle', action: 'Undo' });
```

## Plan composition boundary

Use the family for its stated purpose: commands (Menu), anchored content (SpatialPopup), guidance (Coachmark), or transient feedback (Snackbar). The title-bar close rule for task surfaces does not mean adding a TitleBar to these compact components. Keep ownership, trigger and dismissal clear, avoid a second wrapper background over the built-in surface, and use named local icons where an action needs one. See [general rules](../../general-rules.md) for operation scope and color choices.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
