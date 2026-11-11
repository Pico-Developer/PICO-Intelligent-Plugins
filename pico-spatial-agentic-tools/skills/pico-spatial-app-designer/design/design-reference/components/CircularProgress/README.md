# CircularProgress

A ring for progress or waiting. Sizes: Max 40, Regular 30, Small 20 (default). Stroke is 10% of the size, at least 2.

## Details
- Determinate: track `fillTertiary`, indicator `interaction`, starting at 12 o'clock, round caps (the sweep is shortened by half a stroke).
- Indeterminate: a 345-degree arc that fades in from its tail, color `labelPrimaryLight`, one turn per second, updated at 30fps.
- `SymbolicCircularProgressIndicator` puts a symbol in the center in the indicator color.

## When to use
- **Use for:** loading with unknown duration, or compact progress inside a button or row.
- **Don't use for:** a long download (use `LinearProgress` with a label), a value the wearer sets (use `Slider`).
- **Alternatives:** `LinearProgress`.
- **Do:** use Max for a blocking wait, Small inline; keep the indeterminate ring white on dark or colored backdrops, or override the color.
- **Don't:** show it for waits under a few hundred milliseconds.

## Web API
- `<sui-circular-progress>` (also `<sui-symbolic-circular-progress>`) attributes: `value`, `indeterminate`, `size` (`max`, `regular`, `small`, or px), `stroke-width`, `edge-style`, `track-color`, `progress-color`, `color`, `symbol`.
- Determinate mode uses `progress-color` for the indicator and `track-color` for the track. Indeterminate mode uses `color` for the spinning arc; `progress-color` does not affect this mode. The preview explicitly sets `color="var(--label-darkest-alpha)"` for contrast on its light background. If omitted, the indeterminate color remains the default white (`labelPrimaryLight`), suited to a dark backdrop.

## Preview and shared rules

[Open this family’s preview](preview.html). The first section preserves the reference examples. Any added section is labelled as a Plan recommendation and sets its overrides explicitly. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
