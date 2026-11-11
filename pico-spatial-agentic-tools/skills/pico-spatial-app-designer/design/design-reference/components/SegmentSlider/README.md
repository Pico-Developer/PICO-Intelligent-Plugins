# SegmentSlider

A slider that snaps to a fixed number of steps, drawn as dots on the track instead of a progress fill.

## Details
- `segment-count` counts intervals, not options. A count of 4 creates 5 selectable positions, numbered 0–4; four options require a count of 3. The selected `step` is a zero-based position in `0..segment-count`.
- Sizes and colors as `Slider`; dots are 6dp in `fillSecondary` (`segmentDotColor`), at `startEdge + i / count * total` (`segmentCount + 1` dots).
- Dragging snaps near a dot (hot area `min(8, spacing / 2 - 2)`); releasing and tapping choose the nearest step. The thumb glow shows only on the pressed step.
- Dots grow 2x on hover on device (Small also whitens them). Hover is the native spatial effect on a PICO device; the web build approximates it with the non-spatial fallback.

## When to use
- **Use for:** a few named levels: quality (Low to High), text size.
- **Don't use for:** a continuous value (use `Slider`), two or three exclusive views (use `SegmentControl`).
- **Alternatives:** `Slider`, `SegmentControl`, `Option`.
- **Do:** keep to about three to seven steps; label the ends outside the control.
- Map each position to its application meaning and show the current named level. Keep endpoint names and the mapping visible beside the control rather than relying on unlabeled dots.
- **Don't:** use it for yes/no (use `Switch`).

## Web API
- `<sui-segment-slider>` attributes: `step` (current zero-based position), `segment-count` (number of intervals, at least 1), `size`, `width`, `disabled`, `track-color`, `thumb-color`, `dot-color`.
- Events: `step-change` (`detail.step`, selected position), `value-change` (`detail.value`, fraction). During dragging, round `detail.value * segmentCount` to preview the nearest level; `step-change` reports the selected position on release, tap or keyboard selection.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).

The original example labels all five positions and shows the current position without changing `step="2"` or `segment-count="4"`. The added quality example uses Regular at width 240, four intervals and initial step 2, mapping positions 0–4 to Off, Low, Medium, High and Max. Its live readout shows the nearest level while dragging and the selected level after release.
