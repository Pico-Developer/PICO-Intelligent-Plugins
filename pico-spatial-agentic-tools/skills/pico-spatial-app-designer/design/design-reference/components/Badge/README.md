# Badge

Three small status elements.

## Elements
- `DotBadge`: a 12dp circle in `error`.
- `NumberBadge`: a pill 16 high (Small, padding 4) or 20 high (Regular, padding 6) in `error` with `labelPrimaryLight` text, 10/14 weight 600. Its minimum width equals its height. Above 99 it shows `99+`, or an ellipsis glyph (16x4) with `overflow="ellipsis"`.
- `Badge` (text): `bodySmall` (12/16) on `fillPrimary` with `labelPrimaryLight`. ExtraSmall min 12 high (radius 2, padding 3), Small 18 (radius 4, padding 4, default), Regular 24 (radius 4, padding 8). The height is the larger of the minimum and the text line, so ExtraSmall only fits a smaller text style.
- Badges have no interaction.

## When to use
- **Use for:** an unread or pending count on an icon or tab (`NumberBadge`), a quiet "something changed" mark (`DotBadge`), a short label such as New or Beta (`Badge`).
- **Don't use for:** status that needs reading (use text in a `ListItem`), long labels (use `Chip`), progress (use `LinearProgress`).
- **Alternatives:** `Chip` for a labelled tag the wearer can act on, `Snackbar` for transient feedback.
- **Do:** anchor a badge to the top end of its host icon; cap counts at 99.
- **Don't:** show a badge for zero; stack a dot and a number.

## Web API
- `<sui-dot-badge>`: `color`. `<sui-number-badge>`: `number`, `threshold` (default 99), `overflow` (`plus`, `ellipsis`), `size` (`small`, `regular`), `background-color`, `content-color`. `<sui-badge>`: `text` or default slot, `size` (`extrasmall`, `small`, `regular`), `background-color`, `content-color`.

## Composition: an unread badge outside an avatar

Crop the avatar content, not the entire avatar-and-badge group. Keep an outward-extending badge beside the clipped avatar in an unclipped positioning wrapper; otherwise the round avatar crop will cut off the badge. Leave room around the group so an ancestor does not clip it either. A badge fully inside its host does not require this arrangement.

```html
<div class="image-with-badge" role="img" aria-label="Profile, 8 unread updates">
  <div class="image-crop">
    <img src="../../assets/icons/svg/people/ic_person_fill.svg" alt="">
  </div>
  <sui-number-badge class="unread-badge" number="8" aria-hidden="true"></sui-number-badge>
</div>
```

```css
.image-with-badge {
  position: relative;
  width: 64px;
  height: 64px;
  overflow: visible;
}
.image-crop {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  background: var(--fill-light-alpha);
}
.image-crop img { display: block; width: 100%; height: 100%; object-fit: contain; padding: 12px; box-sizing: border-box; }
.unread-badge { position: absolute; top: 0; right: 0; transform: translate(25%, -25%); }
```

The preview adds this combination using a local profile SVG as the avatar image and the unchanged NumberBadge defaults. The round image crop is intentional; it is not a nested background contour that must adopt a smaller token radius.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
