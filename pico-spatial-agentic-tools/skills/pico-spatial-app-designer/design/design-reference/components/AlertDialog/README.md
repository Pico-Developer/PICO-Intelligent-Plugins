# AlertDialog

A modal window for a decision. `Thick` material from the system; radius 20 (`radiusExtraLarge`).

## Layout
- Width 480 (horizontal buttons) or 360 (vertical), at least 184 high, padding 32, at most the window height minus 64.
- Head: icon and title. Horizontal: a row with 12 gap and 8 vertical padding; vertical: a centered column. Title `headlineLarge` (24/30, 700) in `fillPrimary`.
- Missing icon/title regions occupy no space. Without an icon, the horizontal title aligns with the content's start edge. The preview uses a 28px `ic_delete` icon.
- Content: 8 vertical padding, `labelSecondary`; the samples use `bodyMediumMultiline` (14/22).
- Buttons come 24 below the content. The samples use Regular buttons that share the row equally with gap 8, primary on the right; vertical dialogs stack full-width buttons.
- It is modal and, by default, not dismissed by outside tap or Back.

## When to use
- **Use for:** a decision the wearer must make before continuing, or an irreversible action to confirm.
- **Don't use for:** feedback that needs no answer (use `Snackbar`), a form or long content (use `Sheet`), a hint (use `Coachmark`), a list of commands (use `Menu`).
- **Alternatives:** `Sheet`, `Snackbar`, `Menu`.
- **Do:** name the action in the buttons (Delete, not OK); at most two buttons, primary on the right; say what cannot be undone.
- **Don't:** stack dialogs or ask for something the screen could undo.

## Web API
- `<sui-alert-dialog>` attributes: `title`, `message`, `icon`, `orientation` (`vertical`), `corner-radius`, `dismiss-on-click-outside`, `dismiss-on-escape`, `hidden` (remove it to show). Slots: `icon`, `title`, default (content), `buttons`.
- Events: `dismiss-request` (`detail.reason`).

## Button layout and BasicAlertDialog

The paired Regular buttons in this preview follow the SDK's `AlertDialogSample`: both use equal weight in a full-width row, with an 8dp gap. Regular is 48dp high. This is a sample composition; the native `buttons` slot accepts caller-owned layouts, including a compact end-aligned single action in `SimpleAlertDialogSample`.

`BasicAlertDialog` supplies the modal window and material only. The caller owns all inner layout, typography, padding and exit actions; use it when the standard icon/title/content/buttons structure does not fit. Prefer standard AlertDialog for ordinary confirmations, including when only its content slot needs customization.

The Basic preview demonstrates a caller-owned replacement confirmation: width 560px (limited to viewport minus 64px), padding 32px, section gaps 24px, a grouped saved/new file summary on `fillLight`, and end-aligned Regular Cancel/Replace buttons with an 8px gap. These are explicit example choices, not BasicAlertDialog defaults. Cancel preserves the saved file; Replace updates the displayed saved-file size and reports the result. Both actions close the dialog. Outside-click and Escape dismissal remain disabled by default; no default close button or title layout is added to the Basic component.

Both file entries use the local `ic_document` icon (`ICON7-S255`, `assets/icons/svg/forms/ic_document.svg`) at 24px, with a 12px gap before the file details. The icon identifies file content and keeps the default primary foreground (`labelPrimary`); no explicit tint is needed. It is hidden from assistive technology because the adjacent filename already describes the file. Use `<sui-icon name="ic_document" size="24" aria-hidden="true"></sui-icon>` rather than an emoji or a text character.

## Plan dialog actions and dismissal

Preserve this family's native title hierarchy and decision-button layout. Bottom Cancel/Delete or Cancel/Apply is a valid pair of decisions. The Sheet guidance about duplicate exits does not require removing a decision button or adding another TitleBar/close to these dialogs.

Opening removes `hidden`. `dismiss-request` must be handled by the app; the examples hide the surface. Outside click and Escape are opt-in through `dismiss-on-click-outside` and `dismiss-on-escape`, not guaranteed default exits. The task determines whether draft changes are discarded, applied or retained. In DatePickerDialog, keep negative/positive actions in their own slots and show the committed date outside the picker. Browser Escape is not proof of native Back behavior.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
