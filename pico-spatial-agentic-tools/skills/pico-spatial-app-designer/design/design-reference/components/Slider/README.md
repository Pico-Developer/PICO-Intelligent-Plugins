# Slider

A value on a continuous scale: a capsule track with a round thumb.

## Sizes (`SliderSpec`)
| Size | Thumb area | Thumb | Track height | Component size |
|---|---|---|---|---|
| Small | 32 | 18 | 8 | 336x32 |
| Regular (default) | 32 | 18 | 24 | 320x32 |
| Max | 48 | 32 | 48 | 312x48 |

- The track is always 312 long; the component adds `thumbArea - trackHeight` when the thumb area is larger.
- Track `fillTertiary`. Progress `fillSecondary`, which becomes `lightenPressed` (12% white) while hovered, pressed or dragged. Thumb `labelPrimaryLight`; while pressed or dragged a radial glow at 30% alpha appears around it.
- Hover changes the progress color without showing the thumb glow. The glow appears on press/drag and disappears on release, even if the pointer remains over the slider.
- Tapping animates the value over `durationMedium1` (300ms, standard easing); dragging follows the pointer. The native progress region also uses a device spatial hover effect; the Web preview reproduces the color feedback and thumb glow, not that compositor effect. Disabled alpha 0.3.

## When to use
- **Use for:** volume, brightness, size: a value where the exact number does not matter.
- **Don't use for:** picking one of a few named steps (use `SegmentSlider`), an exact number (use `NumberField`), progress that the wearer does not control (use `LinearProgress`).
- **Alternatives:** `SymbolSlider` when an icon explains the value, `SegmentSlider` for steps, `Stepper` for small integers.
- **Do:** use Regular in windows, Max for large touch targets in volumes; show the value elsewhere if it matters.
- Give an application slider a visible setting name and a meaningful range/unit. Put any current-value readout beside the slider and update it on `value-change`; these labels belong to the application composition, not the base Slider.
- **Don't:** use Small for a value that needs precision; add tick labels on a continuous slider.

## Web API
- `<sui-slider>` attributes: `value`, `min`, `max` (default 0 to 1), `size` (`small`, `regular`, `max`), `width` (overrides the component width), `disabled`, `track-color`, `progress-color`, `thumb-color`.
- Events: `value-change` (`detail.value`), `value-change-finished`. Keyboard: arrows, Home, End.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).

The size reference labels Small, Regular and Max without changing their defaults. The brightness recommendation uses Regular at width 240, range 0–100 and initial value 40, with a live percentage readout. It demonstrates a setting control; it does not change the device's actual brightness.
