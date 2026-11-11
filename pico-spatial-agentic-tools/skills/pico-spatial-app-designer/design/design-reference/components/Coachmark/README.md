# Coachmark

A first-run hint bubble in `interaction` blue with `labelPrimaryLight` content and a 10x20 triangle tip pointing at its target. The window around it has 10dp padding so the tip draws outside the bubble.

## Variants
- Simple: minimum 64 high, padding 16, `bodyLarge`, radius 8, gap 16 before an optional button.
- Rich: width at least 300; image (384x210, inset 8, radius `cornerSize - 8`), title `headlineMedium` (20/26, 700, padding 24, 8 below), body `bodyMedium` (bottom padding 32), buttons right-aligned with gap 8 and padding 24. Without a title or image the body is `bodyLarge` with padding 24. Radius 8, or 16 with an image.
- Image: 480x270 with the image inset 8, radius 16, optional button offset 16,16.
- Buttons are `ButtonDefaults.Min` with `fillSecondary` and `labelPrimaryLight` (`CoachmarkButton`).
- Tip bias (offset from the leading edge): sides center for Simple and Image; Rich 26, 27 with a title, 245 with an image; above and below 30. The bubble sits `gap` (8) from the target.
- It is not dismissed by tapping outside.

## When to use
- **Use for:** pointing out a new or hidden feature once.
- **Don't use for:** errors or confirmations (use `Snackbar` or `AlertDialog`), repeated help, anything the wearer must act on.
- **Alternatives:** `Snackbar` for feedback, `AlertDialog` for a required decision, `Sheet` for longer onboarding.
- **Do:** one at a time, short text, a single "Got it" button; show it where it points.
- **Don't:** point at something that moves, or chain more than three.

## Web API
- `<sui-coachmark>` (also `<sui-simple-coachmark>`, `<sui-rich-coachmark>`, `<sui-image-coachmark>`) attributes: `for` (target id; without it the bubble is shown inline), `direction` (`to-start`, `to-end`, `above`, `below`), `variant`, `text`, `title`, `image`, `button-text`, `gap`, `corner-radius`, `hidden`. The default slot is the body; slots `title`, `image`, `button`.
- Events: `button-click` and `select` (the built-in button). The caller controls visibility; handle completion for all four tag names, including the variant aliases. Custom slotted buttons need their own close handler.
- The preview contains three minimal first-use scenarios: Simple introduces a pin control, Rich explains two-hand resizing beside a resize control, and Image demonstrates a gesture beside a window-corner fragment. Simple appears above its target, Rich below, and Image to the right. Each scene has its own target and Replay hint action; only one hint is visible at a time. Simple and Rich compose matching local icons and one Got it action; Rich puts the action at the bottom right. Image uses a local gesture SVG and one top-left close IconButton. These are example slot contents, not new built-in Coachmark defaults. There is no application page, navigation, document content or toolbar to distract from the target–hint relationship.

## Plan composition boundary

Use the family for its stated purpose: commands (Menu), anchored content (SpatialPopup), guidance (Coachmark), or transient feedback (Snackbar). The title-bar close rule for task surfaces does not mean adding a TitleBar to these compact components. Keep ownership, trigger and dismissal clear, avoid a second wrapper background over the built-in surface, and use named local icons where an action needs one. See [general rules](../../general-rules.md) for operation scope and color choices.

## Preview and shared rules

[Open this family’s preview](preview.html). The three first-use scenarios compose their icons, illustration and actions using the existing component slots. Their captions describe when to use each variant; the scene itself retains only the target and the hint. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
