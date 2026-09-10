/*
 * SpatialUI Design Tokens — Web port.
 *
 * Faithfully mirrors the PICO SpatialUI design tokens defined in:
 *   spatialui/design/src/main/kotlin/com/pico/spatial/ui/design/tokens/ColorTokens.kt
 *   spatialui/design/src/main/kotlin/com/pico/spatial/ui/design/tokens/DimensionTokens.kt
 *   spatialui/design/src/main/kotlin/com/pico/spatial/ui/design/tokens/TypeScaleTokens.kt
 *   spatialui/design/src/main/kotlin/com/pico/spatial/ui/design/ColorScheme.kt (defaultColorScheme / vibrantColorScheme)
 *   spatialui/design/src/main/kotlin/com/pico/spatial/ui/design/PicoTheme.kt
 *
 * Compose Color(0xAARRGGBB) values are converted to CSS rgba() here.
 * Components do NOT import ColorScheme literals directly — they read CSS custom
 * properties (var(--sui-fill-primary) etc.) installed by PicoTheme.install(...),
 * which mirrors how PicoTheme() in Compose pushes ColorScheme through
 * CompositionLocal. Callers can override any role at any subtree by providing
 * an element with --sui-* overrides, or via PicoTheme.provide({colorScheme}, el).
 */

/** Convert a Compose 0xAARRGGBB int-literal into a CSS rgba() string. */
export function argb(hex) {
  const v = typeof hex === "string" ? parseInt(hex, 16) : hex >>> 0;
  const a = ((v >>> 24) & 0xff) / 255;
  const r = (v >>> 16) & 0xff;
  const g = (v >>> 8) & 0xff;
  const b = v & 0xff;
  return `rgba(${r}, ${g}, ${b}, ${+a.toFixed(4)})`;
}

/** Raw color tokens (mirrors ColorTokens.kt Default object). */
export const ColorTokens = {
  FillBgthinAlpha: argb(0x33ffffff),
  FillDarkerAlpha: argb(0xff282828),
  FillLightAlpha: argb(0x26ffffff),
  FillNeutralAlpha: argb(0x0a000000),
  FillPrimary: argb(0xff282828),
  FillSecondaryAlpha: argb(0x66ffffff),
  FillSemilightAlpha: argb(0x66ffffff),
  FillTertiaryAlpha: argb(0x0a000000),
  LabelDarkAlpha: argb(0x66000000),
  LabelDarkestAlpha: argb(0xff000000),
  LabelLightAlpha: argb(0x66ffffff),
  LabelPrimary: argb(0xff000000),
  LabelPrimaryLight: argb(0xffffffff),
  LabelQuaternaryAlpha: argb(0x4d000000),
  LabelSecondaryAlpha: argb(0xcc000000),
  LabelSemidarkAlpha: argb(0xa6000000),
  LabelTertiaryAlpha: argb(0x80000000),
  LabelUltradarkAlpha: argb(0xcc000000),
  LineDividerLine: argb(0x1f808080),
  SemanticAlert: argb(0xffffbf00),
  SemanticError: argb(0xffff4d4d),
  SemanticInteraction: argb(0xff3377ff),
  SemanticPassable: argb(0xffb3ff66),
  StateLightenHoverAlpha: argb(0x1fffffff),
  StateLightenPressedAlpha: argb(0x1fffffff),
  SubBlack12: argb(0x1f000000),
  SubBlue100: argb(0xff3377ff),
  SubGray100: argb(0xff333333),
  SubGreen100: argb(0xffb3ff66),
  SubOrange100: argb(0xffffbf00),
  SubRed100: argb(0xffff4d4d),
  SubWhite100: argb(0xffffffff),
  SubWhite40: argb(0x66ffffff),
  SubWhite60: argb(0x99ffffff),
  SubWhite80: argb(0xccffffff),
  SubYellow100: argb(0xffffff99),
  SliderKnobActiveAlpha: argb(0xffe6e6e6),
  SliderKnobNormalAlpha: argb(0x3dffffff),
};

/**
 * The named ColorScheme roles (mirrors ColorScheme class constructor).
 * Every value is a CSS color string. Consumers can pass a partial override
 * to defaultColorScheme() / vibrantColorScheme() or construct a full one.
 */
const COLOR_SCHEME_KEYS = [
  "fillPrimary",
  "fillSecondary",
  "fillTertiary",
  "fillLight",
  "labelPrimaryLight",
  "labelPrimary",
  "labelSecondary",
  "labelTertiary",
  "labelQuaternary",
  "lightenHover",
  "lightenPressed",
  "error",
  "alert",
  "passable",
  "interaction",
  "dividerLine",
];

function mergeScheme(base, overrides) {
  const out = { ...base };
  if (overrides) for (const k of Object.keys(overrides)) if (overrides[k] != null) out[k] = overrides[k];
  return out;
}

/**
 * Default (non-vibrant / solid) color scheme.
 * Mirrors defaultColorScheme() in ColorScheme.kt. All fill/label colors are
 * fully specified; this is the "flat / non-glass" fallback.
 */
export function defaultColorScheme(overrides) {
  return mergeScheme(
    {
      fillPrimary: ColorTokens.FillDarkerAlpha, // 0xFF282828
      fillSecondary: ColorTokens.FillSemilightAlpha, // 0x66FFFFFF
      fillTertiary: ColorTokens.FillNeutralAlpha, // 0x0A000000
      fillLight: ColorTokens.FillLightAlpha, // 0x26FFFFFF
      labelPrimaryLight: ColorTokens.SubWhite100, // 0xFFFFFFFF
      labelPrimary: ColorTokens.LabelDarkestAlpha, // 0xFF000000
      labelSecondary: ColorTokens.LabelUltradarkAlpha, // 0xCC000000
      labelTertiary: ColorTokens.LabelSemidarkAlpha, // 0xA6000000
      labelQuaternary: ColorTokens.LabelDarkAlpha, // 0x66000000
      lightenHover: ColorTokens.FillSemilightAlpha,
      lightenPressed: ColorTokens.FillSemilightAlpha,
      error: ColorTokens.SubRed100,
      alert: ColorTokens.SubOrange100,
      passable: ColorTokens.SubGreen100,
      interaction: ColorTokens.SubBlue100,
      dividerLine: ColorTokens.SubBlack12,
    },
    overrides,
  );
}

/**
 * Vibrant (glass / material) color scheme.
 * Mirrors vibrantColorScheme() in ColorScheme.kt. On Android Vibrant.* colors
 * are runtime material colors (backdrop-blurred, tinted). On the web we
 * approximate glass with semi-transparent fills plus backdrop-filter blur.
 *
 * Color values mirror the Compose source:
 *   fillPrimary        = Vibrant.Darker     ≈ 0xE6101010 (deep glass)
 *   fillSecondary      = Vibrant.SemiLight  ≈ 0x66FFFFFF (mid glass)
 *   fillTertiary       = Vibrant.Neutral    ≈ 0x14FFFFFF (soft glass)
 *   fillLight          = Vibrant.Light      ≈ 0x26FFFFFF (light glass)
 *   labelPrimaryLight  = white (no vibrant)
 *   labelPrimary       = Vibrant.Darkest    ≈ 0xF0FFFFFF
 *   labelSecondary     = Vibrant.UltraDark  ≈ 0xCCFFFFFF
 *   labelTertiary      = Vibrant.Semidark   ≈ 0xA6FFFFFF
 *   labelQuaternary    = Vibrant.Dark       ≈ 0x66FFFFFF
 *   lightenHover/Pressed = Vibrant.SemiLight (0x66FFFFFF)
 *   error/alert/passable/interaction = same P-3 semantic colors as default
 *   dividerLine        = 0x1FFFFFFF with Vibrant.None (pure white alpha)
 */
export function vibrantColorScheme(overrides) {
  return mergeScheme(
    {
      fillPrimary: "rgba(16, 16, 16, 0.90)",     // Vibrant.Darker
      fillSecondary: "rgba(255, 255, 255, 0.40)", // Vibrant.SemiLight
      fillTertiary: "rgba(255, 255, 255, 0.08)",  // Vibrant.Neutral
      fillLight: "rgba(255, 255, 255, 0.15)",     // Vibrant.Light
      labelPrimaryLight: ColorTokens.SubWhite100,
      labelPrimary: "rgba(255, 255, 255, 0.94)",  // Vibrant.Darkest
      labelSecondary: "rgba(255, 255, 255, 0.80)", // Vibrant.UltraDark
      labelTertiary: "rgba(255, 255, 255, 0.65)", // Vibrant.Semidark
      labelQuaternary: "rgba(255, 255, 255, 0.40)", // Vibrant.Dark
      lightenHover: "rgba(255, 255, 255, 0.20)",
      lightenPressed: "rgba(255, 255, 255, 0.30)",
      error: "rgba(255, 77, 77, 1)",
      alert: "rgba(255, 191, 0, 1)",
      passable: "rgba(179, 255, 102, 1)",
      interaction: "rgba(51, 119, 255, 1)",
      dividerLine: "rgba(255, 255, 255, 0.12)",
    },
    overrides,
  );
}

/**
 * The active color scheme defaults. On the SDK runtime the default
 * LocalColorScheme is `vibrantColorScheme().adaptVibrantColor { defaultColorScheme() }`
 * — i.e. vibrant (glass) when Vibrant is available, otherwise the solid
 * default. On the web we can always render vibrant glass (backdrop-filter is
 * supported on all modern browsers), so default to vibrant. Callers who want
 * the flat scheme can call PicoTheme.install({scheme: "default"}, root).
 */
let _activeScheme = vibrantColorScheme();

/** Dimension tokens in dp === css px (mirrors DimensionTokens.kt). */
export const Dimension = {
  GapLarge: 16,
  GapMedium: 12,
  GapSmall: 8,
  HeightExtraLarge: 480,
  HeightMin: 184,
  PaddingLarge: 32,
  PaddingMedium: 24,
  PaddingRegular: 16,
  PaddingSmall: 8,
  RadiusExtraHuge: 32,
  RadiusHuge: 24,
  RadiusExtraLarge: 20,
  RadiusLarge: 16,
  RadiusMediumLarge: 12,
  RadiusMedium: 8,
  RadiusMin: 2,
  RadiusSmall: 4,
  WidthExtraLarge: 480,
  WidthHuge: 600,
  WidthLarge: 400,
  WidthMedium: 360,
  WidthMin: 160,
  WidthRegular: 320,
  WidthSmall: 240,
};

/** Type scale (mirrors TypeScaleTokens.kt). size / lineHeight in sp === px, weight numeric. */
export const TypeScale = {
  displayLarge: { size: 40, line: 54, weight: 700 },
  displayMedium: { size: 32, line: 40, weight: 700 },
  displaySmall: { size: 28, line: 34, weight: 700 },
  headlineLarge: { size: 24, line: 30, weight: 700 },
  headlineMedium: { size: 20, line: 26, weight: 700 },
  headlineSmall: { size: 16, line: 20, weight: 700 },
  titleLarge: { size: 20, line: 26, weight: 600 },
  titleMedium: { size: 16, line: 20, weight: 600 },
  titleSmall: { size: 14, line: 18, weight: 600 },
  bodyLarge: { size: 16, line: 20, weight: 500 },
  bodyLargeMultiline: { size: 16, line: 24, weight: 500 },
  bodyMedium: { size: 14, line: 18, weight: 500 },
  bodyMediumMultiline: { size: 14, line: 22, weight: 500 },
  bodySmall: { size: 12, line: 16, weight: 500 },
  bodyTiny: { size: 10, line: 12, weight: 500 },
  labelLarge: { size: 14, line: 18, weight: 600 },
  labelMedium: { size: 12, line: 16, weight: 600 },
  labelSmall: { size: 11, line: 14, weight: 600 },
};

/** Alpha applied to disabled components (LocalDisableAlpha default). */
export const DISABLE_ALPHA = 0.4;

/**
 * Write the --sui-* CSS custom properties that back every component onto a
 * target element. Mirrors what PicoTheme() {} Composable does via
 * CompositionLocalProvider — any subtree under `target` will read these vars.
 */
export function installThemeVariables(scheme, target = document.documentElement) {
  const cs = scheme || _activeScheme;
  const set = (k, v) => target.style.setProperty(k, v);
  for (const k of COLOR_SCHEME_KEYS) set(`--sui-${kebab(k)}`, cs[k]);
  for (const [k, v] of Object.entries(Dimension)) set(`--sui-dim-${kebab(k)}`, `${v}px`);
  set("--sui-disable-alpha", String(DISABLE_ALPHA));
  // Expose whether the active scheme is vibrant (so components can opt into
  // backdrop-filter: blur() only when appropriate).
  set("--sui-vibrant", "1");
}

function kebab(camel) {
  return camel.replace(/[A-Z]/g, (c) => "-" + c.toLowerCase());
}

/**
 * Public PicoTheme object — mirrors `object PicoTheme` in PicoTheme.kt.
 *   PicoTheme.colorScheme       -> current default ColorScheme (object)
 *   PicoTheme.install(opts, el) -> push a scheme onto an element (CSS vars)
 *   PicoTheme.provide(opts, el) -> alias for install (Compose-style naming)
 *   PicoTheme.defaultColorScheme(overrides)
 *   PicoTheme.vibrantColorScheme(overrides)
 */
export const PicoTheme = {
  get colorScheme() {
    return _activeScheme;
  },
  get typography() {
    return TypeScale;
  },
  defaultColorScheme,
  vibrantColorScheme,
  install(options = {}, target = document.documentElement) {
    const { scheme = "vibrant", colorScheme } = options;
    const factory =
      typeof scheme === "function"
        ? scheme
        : scheme === "default"
          ? defaultColorScheme
          : vibrantColorScheme;
    _activeScheme = factory(colorScheme);
    installThemeVariables(_activeScheme, target);
    return _activeScheme;
  },
  provide(options, target) {
    return this.install(options, target);
  },
};

/** Backwards-compatibility alias: the flat default scheme object. */
export const ColorScheme = defaultColorScheme();
