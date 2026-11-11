# Motion

Spatial UI moves with springs for position and size, and cubic-beziers for fades. Values come from `MotionTokens` (`motion.xml`); machine-readable copies are in `motion.json`, and `runtime/tokens.css` carries `--duration-*`, `--ease-*` and `--spring-*` variables (the spring ones are CSS `linear()` curves sampled from the real spring, with `--spring-*-ms` as the settle time).

## Choosing

- Move or resize a window, panel or sheet: spring `steady` (damping 1, stiffness 450). Slow background changes: `gradual` (1, 50).
- Toggle, select, press response: spring `rapid` (1, 850) or `instant` (1, 2500). No overshoot on controls.
- Overshoot (`snappy` 0.75/150, `fair` 0.5/450, `bouncy` 0.35/550) is for entrances and rewards. Never on text-carrying controls or anything in the wearer's gaze path while reading.
- Fades and color changes: bezier `standard` (0.3, 0, 0.2, 1) with `short1`-`short2` (120-180ms). Entering: `decelerate`; leaving: `accelerate`. The `power*` curves are for large moves only.
- Durations: short 120/180/240, medium 300/360/420, long 540/600/660/720 ms. `medium4` is 1000ms: the tab bar hover dwell and slow loops.

## Hover and press

- Hover on a PICO device is the **native spatial hover effect** (gaze or ray): scale, offset and alpha animated by the system through `spatialHoverEffect`. It is not a color and the app does not draw it. Built-in components apply it; use `spatialHoverEffect` only on custom views, with active and inactive branches calling the same builders.
- Where the platform is not spatial, `PicoIndication` falls back to a flat overlay: **12% white (`0x1FFFFFFF`) for both hover and pressed.** The web build uses this fallback; `lightenHover` (`fillSemilight`, 40% white) in the color scheme is not what is drawn.
- Pressed draws `lightenPressed` (12% white, `state-lighten-pressed-alpha`) under the content and plays the controller haptic; it must start within one frame.
- `Switch` and `ListItem` draw no overlay. `ScrollIndicator` hover transitions take 0ms; `TabBar` waits 1000ms (`HoverDelayMillis`) before it expands.
- Disabled controls do not animate and sit at alpha 0.3.

## Where the SDK uses which motion

- Switch thumb and its inner shadow: spring `rapid`. Checkbox content and toggleable chip colors: spring `instant`. Removable chip: spring `rapid` (alpha, scale to 0.95).
- Slider tap: `durationMedium1` (300ms) with the standard bezier. Segment slider dots on hover: `durationShort2` (180ms) standard, scale 2.
- Tab bar expand and item clip: `durationMedium3` (420ms) standard. Page control and wheel picker snapping: spring `instant`.
- Indeterminate circular progress: one turn per 1000ms, updated at 30fps.

## Rules

- Animate only opacity, color, scale and offset. Do not animate blur or the glass material.
- Keep paired states shape-identical so they can interpolate.
- Respect reduced motion: replace springs with a 120ms fade.

## Vibrant colors

A `Vibrant` level is categorical, so it cannot be interpolated: animating a color that carries a level with `animateColorAsState` loses the level. Animate the raw color and re-apply `.withVibrant(vibrant)` to each value, put `Modifier.vibrantEffect(vibrant)` on the node, or use `animateColorVibrantAsState` (spring by default), which only supports colors with the same level. Nothing in the web build animates vibrant levels. See `vibrant.md`.
