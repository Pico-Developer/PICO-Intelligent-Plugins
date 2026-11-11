# SymbolSlider

A `Slider` with an icon inside the start of the track, in `labelPrimary`. Sizes, colors and behavior are the `Slider` ones (default Regular).

## Details
- The icon sits in the thumb area box at the start, padded by `(thumbArea - trackHeight) / 2`.
- The thumb fades in as it leaves the icon, using the SDK's distance threshold (`trackHeight / 2`). At zero the thumb is hidden and the icon stays visible; once clear of the icon the thumb is fully visible. This is a position-dependent fade, not a change to the icon.
- Hover changes the progress color; pressing or dragging also shows the thumb glow. The native progress region additionally uses a device spatial hover effect, which the Web preview does not reproduce.

## When to use
- **Use for:** volume, brightness and similar values where the icon names the quantity.
- **Don't use for:** values without a clear icon (use `Slider`), stepped values (use `SegmentSlider`).
- **Alternatives:** `Slider`, `SegmentSlider`.
- **Do:** pick a single-ink glyph.
- Pair the icon with a visible setting name and a current value when the value matters. Update the readout on `value-change`; keep the same unit and range at the endpoints.
- **Don't:** change the icon with the value in more than two states.

## Web API
- `<sui-symbol-slider>` attributes as `Slider` plus `icon` and `symbol-color`.
- Events: `value-change` (`detail.value`, in the configured range), `value-change-finished`.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).

The original Regular sun slider now has a Brightness label, a live percentage readout and 0%/100% endpoint labels. Its default 0–1 value maps to 0–100% in the readout. The added fixed references use Regular, width 240 and range 0–100 at 0%, 5%, 50% and 100%. They are inert snapshots, so inspecting them does not change their stated values. Use the original interactive slider to inspect the transition near zero; it does not change device brightness.
