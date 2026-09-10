/* SpatialUI Web — auto-bundled standalone build.
   Do not edit directly; edit js/*.js and rerun build-standalone.mjs. */
(function(){
'use strict';

/* ===== tokens.js ===== */
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
function argb(hex) {
  const v = typeof hex === "string" ? parseInt(hex, 16) : hex >>> 0;
  const a = ((v >>> 24) & 0xff) / 255;
  const r = (v >>> 16) & 0xff;
  const g = (v >>> 8) & 0xff;
  const b = v & 0xff;
  return `rgba(${r}, ${g}, ${b}, ${+a.toFixed(4)})`;
}

/** Raw color tokens (mirrors ColorTokens.kt Default object). */
const ColorTokens = {
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
function defaultColorScheme(overrides) {
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
function vibrantColorScheme(overrides) {
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
const Dimension = {
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
const TypeScale = {
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
const DISABLE_ALPHA = 0.4;

/**
 * Write the --sui-* CSS custom properties that back every component onto a
 * target element. Mirrors what PicoTheme() {} Composable does via
 * CompositionLocalProvider — any subtree under `target` will read these vars.
 */
function installThemeVariables(scheme, target = document.documentElement) {
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
const PicoTheme = {
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
const ColorScheme = defaultColorScheme();


/* ===== base.js ===== */
/*
 * Shared helpers for SpatialUI web components.
 *
 * Components read colors from the --sui-* CSS custom properties installed by
 * PicoTheme.install() (see tokens.js). This mirrors Compose: PicoTheme() pushes
 * ColorScheme via CompositionLocal, and components read the ambient theme.
 */

{ PicoTheme, Dimension, TypeScale, DISABLE_ALPHA };

// Resolve a --sui-* CSS variable on an element, falling back to the live
// PicoTheme.colorScheme value if the variable is not yet set (e.g. before
// install() has run, or inside disconnected trees).
const VAR_MAP = {
  fillPrimary: "--sui-fill-primary",
  fillSecondary: "--sui-fill-secondary",
  fillTertiary: "--sui-fill-tertiary",
  fillLight: "--sui-fill-light",
  labelPrimaryLight: "--sui-label-primary-light",
  labelPrimary: "--sui-label-primary",
  labelSecondary: "--sui-label-secondary",
  labelTertiary: "--sui-label-tertiary",
  labelQuaternary: "--sui-label-quaternary",
  lightenHover: "--sui-lighten-hover",
  lightenPressed: "--sui-lighten-pressed",
  error: "--sui-error",
  alert: "--sui-alert",
  passable: "--sui-passable",
  interaction: "--sui-interaction",
  dividerLine: "--sui-divider-line",
};

function themeVar(role) {
  return VAR_MAP[role] || `--sui-${role.replace(/[A-Z]/g, (c) => "-" + c.toLowerCase())}`;
}

function themeColor(role) {
  return `var(${themeVar(role)})`;
}

/** Shared base class: a shadow-root element with themed reactive attributes. */
class SuiElement extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }
  connectedCallback() {
    if (!this._rendered) {
      this.render();
      this._rendered = true;
    }
  }
  attributeChangedCallback() {
    if (this._rendered) this.render();
  }
  bool(name) {
    return this.hasAttribute(name) && this.getAttribute(name) !== "false";
  }
  attr(name, fallback = null) {
    return this.getAttribute(name) ?? fallback;
  }
  num(name, fallback) {
    const v = this.getAttribute(name);
    return v == null ? fallback : parseFloat(v);
  }
  render() {}
}

/**
 * Base CSS shared by every component. Hover/pressed overlays use the theme
 * lightenHover/lightenPressed tokens so they follow PicoTheme automatically.
 */
const baseCss = `
  :host { display: inline-flex; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  :host([disabled]) { pointer-events: none; opacity: var(--sui-disable-alpha, 0.4); }
  * { box-sizing: border-box; }
  .sui-interactive {
    position: relative; cursor: pointer; user-select: none;
    transition: filter .12s ease, background-color .12s ease, transform .12s ease;
    outline: none;
  }
  .sui-interactive::after {
    content: ""; position: absolute; inset: 0; border-radius: inherit;
    background: transparent; transition: background-color .12s ease; pointer-events: none;
  }
  .sui-interactive:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
  .sui-interactive:active::after { background: var(--sui-lighten-pressed, rgba(255,255,255,0.20)); }
  .sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
`;

/** Return a CSS font shorthand for a TypeScale role. */
function typeStyle(role) {
  const t = TypeScale[role] || TypeScale.bodyLarge;
  return `font-weight:${t.weight};font-size:${t.size}px;line-height:${t.line}px;`;
}

/** Emit a bubbling, composed CustomEvent. */
function emit(el, name, detail) {
  el.dispatchEvent(new CustomEvent(name, { detail, bubbles: true, composed: true }));
}

/** Escape untrusted text before inserting it into a component template. */
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

/** Define a custom element once (safe against duplicate registration). */
function define(tag, klass) {
  if (!customElements.get(tag)) customElements.define(tag, klass);
}



/* ===== overlay-position.js ===== */
/*
 * Pure positioning helpers shared by Augment and SpatialPopup.
 * Keeping geometry independent from DOM APIs makes it easy to verify.
 */

const NAMED_POINTS = {
  "top-left": { x: 0, y: 0, z: 1 },
  "top-left-front": { x: 0, y: 0, z: 1 },
  top: { x: 0.5, y: 0, z: 1 },
  "top-center": { x: 0.5, y: 0, z: 1 },
  "top-front": { x: 0.5, y: 0, z: 1 },
  "top-center-front": { x: 0.5, y: 0, z: 1 },
  "top-right": { x: 1, y: 0, z: 1 },
  "top-right-front": { x: 1, y: 0, z: 1 },
  left: { x: 0, y: 0.5, z: 1 },
  "center-left": { x: 0, y: 0.5, z: 1 },
  "center-left-front": { x: 0, y: 0.5, z: 1 },
  center: { x: 0.5, y: 0.5, z: 1 },
  front: { x: 0.5, y: 0.5, z: 1 },
  "center-front": { x: 0.5, y: 0.5, z: 1 },
  right: { x: 1, y: 0.5, z: 1 },
  "center-right": { x: 1, y: 0.5, z: 1 },
  "center-right-front": { x: 1, y: 0.5, z: 1 },
  "bottom-left": { x: 0, y: 1, z: 1 },
  "bottom-left-front": { x: 0, y: 1, z: 1 },
  bottom: { x: 0.5, y: 1, z: 1 },
  "bottom-center": { x: 0.5, y: 1, z: 1 },
  "bottom-front": { x: 0.5, y: 1, z: 1 },
  "bottom-center-front": { x: 0.5, y: 1, z: 1 },
  "bottom-right": { x: 1, y: 1, z: 1 },
  "bottom-right-front": { x: 1, y: 1, z: 1 },
};

function finite(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

/** Parse a named point or an "x,y,z" normalized tuple. */
function parseNormalizedPoint(value, fallback = "center") {
  const source = String(value || fallback).trim();
  const tuple = source.split(",").map((part) => Number(part.trim()));
  if (tuple.length >= 2 && tuple.every(Number.isFinite)) {
    return { x: tuple[0], y: tuple[1], z: tuple[2] ?? 1 };
  }

  const normalized = source
    .trim()
    .replace(/([a-z0-9])([A-Z])/g, "$1-$2")
    .replace(/[_.\s]+/g, "-")
    .toLowerCase();
  if (NAMED_POINTS[normalized]) return { ...NAMED_POINTS[normalized] };
  return { ...(NAMED_POINTS[fallback] || NAMED_POINTS.center) };
}

/** Align one normalized content point to a normalized point on the host. */
function computeAugmentPosition(
  anchorRect,
  contentSize,
  anchorPoint,
  contentAlignment,
  offset = {},
) {
  return {
    x: anchorRect.left + anchorRect.width * anchorPoint.x
      - contentSize.width * contentAlignment.x + finite(offset.x),
    y: anchorRect.top + anchorRect.height * anchorPoint.y
      - contentSize.height * contentAlignment.y + finite(offset.y),
    z: finite(offset.z),
  };
}

function horizontalPosition(anchorRect, width, placement, direction) {
  const rtl = direction === "rtl";
  switch (placement) {
    case "to-start-of": return rtl ? anchorRect.right : anchorRect.left - width;
    case "center": return anchorRect.left + (anchorRect.width - width) / 2;
    case "align-end": return rtl ? anchorRect.left : anchorRect.right - width;
    case "to-end-of": return rtl ? anchorRect.left - width : anchorRect.right;
    case "align-start":
    default: return rtl ? anchorRect.right - width : anchorRect.left;
  }
}

function verticalPosition(anchorRect, height, placement) {
  switch (placement) {
    case "align-top": return anchorRect.top;
    case "center": return anchorRect.top + (anchorRect.height - height) / 2;
    case "align-bottom": return anchorRect.bottom - height;
    case "below": return anchorRect.bottom;
    case "above":
    default: return anchorRect.top - height;
  }
}

/** Position a popup with the SDK HorizontalPlacement/VerticalPlacement model. */
function computePopupPosition(
  anchorRect,
  contentSize,
  horizontalPlacement = "align-start",
  verticalPlacement = "above",
  offset = {},
  direction = "ltr",
) {
  return {
    x: horizontalPosition(anchorRect, contentSize.width, horizontalPlacement, direction)
      + finite(offset.x),
    y: verticalPosition(anchorRect, contentSize.height, verticalPlacement) + finite(offset.y),
    z: finite(offset.z),
  };
}

/** Clamp a popup to a viewport when clipping-enabled is explicitly requested. */
function clampPosition(position, contentSize, viewport, padding = 0) {
  const maxX = Math.max(padding, viewport.width - contentSize.width - padding);
  const maxY = Math.max(padding, viewport.height - contentSize.height - padding);
  return {
    ...position,
    x: Math.min(Math.max(position.x, padding), maxX),
    y: Math.min(Math.max(position.y, padding), maxY),
  };
}


/* ===== overlay.js ===== */
/* Shared top-layer lifecycle for SpatialUI floating window components. */

let nextOverlayLayer = 0;

const overlayCss = [
  ":host {",
  "position:fixed;inset:auto;top:0;left:0;display:block;width:max-content;margin:0;padding:0;",
  "border:0;overflow:visible;color:inherit;background:transparent;font-family:inherit;",
  "pointer-events:auto;z-index:var(--sui-overlay-z-index,1000);",
  "transform:translate3d(var(--sui-overlay-x,0px),var(--sui-overlay-y,0px),var(--sui-overlay-z,0px))",
  "rotateX(var(--sui-overlay-rotate-x,0deg)) rotateY(var(--sui-overlay-rotate-y,0deg))",
  "rotateZ(var(--sui-overlay-rotate-z,0deg));",
  "transform-origin:var(--sui-overlay-origin-x,50%) var(--sui-overlay-origin-y,50%);}",
  ":host([hidden]){display:none!important;}",
  "*,*::before,*::after{box-sizing:border-box;}",
  ".surface{position:relative;display:flex;color:var(--sui-label-primary);",
  "box-sizing:border-box;overflow:hidden;isolation:isolate;",
  "box-shadow:0 18px 54px rgba(0,0,0,.24),inset 0 0 0 1px ",
  "var(--sui-overlay-border,rgba(255,255,255,.28));}",
  ".surface.material-regular{background:var(--Background-MaterialRegular,rgba(255,255,255,.34));",
  "backdrop-filter:blur(50px) saturate(1.18);-webkit-backdrop-filter:blur(50px) saturate(1.18);}",
  ".surface.material-thick{background:var(--Background-MaterialThick,rgba(255,255,255,.58));",
  "backdrop-filter:blur(64px) saturate(1.22);-webkit-backdrop-filter:blur(64px) saturate(1.22);}",
  ".surface.material-none{background:transparent;box-shadow:none;}",
  "::slotted(*){box-sizing:border-box;}",
].join("");

function numericAttribute(element, name, fallback = 0) {
  const value = Number(element.getAttribute(name));
  return Number.isFinite(value) ? value : fallback;
}

/** Base class used by sui-augment and sui-spatial-popup. */
class SuiOverlayElement extends SuiElement {
  constructor() {
    super();
    this._anchorElement = null;
    this._positionFrame = 0;
    this._overlayCleanup = [];
  }

  get anchorElement() { return this._anchorElement; }

  set anchorElement(value) {
    if (value !== null && !(value instanceof Element)) {
      throw new TypeError("anchorElement must be an Element or null");
    }
    this._anchorElement = value;
    if (this.isConnected) this._activateOverlay();
  }

  connectedCallback() {
    super.connectedCallback();
    this.setAttribute("popover", "manual");
    this.style.setProperty("--sui-overlay-z-index", String(1000 + nextOverlayLayer++));
    this._activateOverlay();
  }

  disconnectedCallback() {
    this._deactivateOverlay();
    try { this.hidePopover?.(); } catch (_) { /* Already detached or unsupported. */ }
  }

  attributeChangedCallback(name, oldValue, newValue) {
    super.attributeChangedCallback(name, oldValue, newValue);
    if (oldValue !== newValue && this.isConnected) this._activateOverlay();
  }

  resolveAnchor() {
    if (this._anchorElement?.isConnected) return this._anchorElement;
    const id = this.getAttribute("for");
    if (id) {
      const root = this.getRootNode();
      return root.getElementById?.(id) || this.ownerDocument?.getElementById(id) || null;
    }
    return this.previousElementSibling || this.parentElement;
  }

  shouldDismissOnOutsidePointer() { return false; }
  shouldDismissOnEscape() { return false; }

  requestDismiss(reason, sourceEvent) {
    emit(this, "dismiss-request", { reason, sourceEvent });
  }

  _deactivateOverlay() {
    if (this._positionFrame) cancelAnimationFrame(this._positionFrame);
    this._positionFrame = 0;
    this._overlayCleanup.splice(0).forEach((cleanup) => cleanup());
  }

  _activateOverlay() {
    this._deactivateOverlay();
    if (this.hidden) return;
    try {
      if (!this.matches(":popover-open")) this.showPopover?.();
    } catch (_) { /* Fixed-position fallback. */ }

    const anchor = this.resolveAnchor();
    const surface = this.shadowRoot.querySelector(".surface");
    if (!anchor || !surface) {
      this.style.visibility = "hidden";
      const mutationObserver = new MutationObserver(() => {
        if (this.resolveAnchor()) this._activateOverlay();
      });
      mutationObserver.observe(this.ownerDocument.documentElement, { childList: true, subtree: true });
      this._overlayCleanup.push(() => mutationObserver.disconnect());
      return;
    }

    this.style.visibility = "hidden";
    const schedule = () => {
      if (this._positionFrame) return;
      this._positionFrame = requestAnimationFrame(() => {
        this._positionFrame = 0;
        this._updatePosition(anchor, surface);
      });
    };

    if (typeof ResizeObserver !== "undefined") {
      const resizeObserver = new ResizeObserver(schedule);
      resizeObserver.observe(anchor);
      resizeObserver.observe(surface);
      this._overlayCleanup.push(() => resizeObserver.disconnect());
    }
    window.addEventListener("resize", schedule);
    window.addEventListener("scroll", schedule, true);
    this._overlayCleanup.push(() => window.removeEventListener("resize", schedule));
    this._overlayCleanup.push(() => window.removeEventListener("scroll", schedule, true));

    if (this.shouldDismissOnOutsidePointer()) {
      const onPointerDown = (event) => {
        const path = event.composedPath();
        const insideNestedOverlay = path.some((node) =>
          node instanceof SuiOverlayElement && this.contains(node));
        if (!path.includes(this) && !path.includes(anchor) && !insideNestedOverlay) {
          this.requestDismiss("outside-pointer", event);
        }
      };
      this.ownerDocument.addEventListener("pointerdown", onPointerDown, true);
      this._overlayCleanup.push(() =>
        this.ownerDocument.removeEventListener("pointerdown", onPointerDown, true));
    }

    if (this.shouldDismissOnEscape()) {
      const onKeyDown = (event) => {
        if (event.key === "Escape" && !event.defaultPrevented) {
          event.preventDefault();
          this.requestDismiss("escape-key", event);
        }
      };
      this.ownerDocument.addEventListener("keydown", onKeyDown, true);
      this._overlayCleanup.push(() =>
        this.ownerDocument.removeEventListener("keydown", onKeyDown, true));
    }
    schedule();
  }

  _updatePosition(anchor, surface) {
    if (!this.isConnected || !anchor.isConnected) {
      this.style.visibility = "hidden";
      return;
    }
    this.prepareSurface(anchor, surface);
    const anchorRect = anchor.getBoundingClientRect();
    const contentSize = { width: surface.offsetWidth, height: surface.offsetHeight };
    let position = this.calculatePosition(anchorRect, contentSize, anchor);
    if (this.bool("clipping-enabled")) {
      position = clampPosition(
        position,
        contentSize,
        { width: window.innerWidth, height: window.innerHeight },
        numericAttribute(this, "viewport-padding", 0),
      );
    }
    this.style.setProperty("--sui-overlay-x", position.x + "px");
    this.style.setProperty("--sui-overlay-y", position.y + "px");
    this.style.setProperty("--sui-overlay-z", (position.z || 0) + "px");
    this.style.setProperty(
      "--sui-overlay-rotate-x",
      numericAttribute(this, "rotation-x", 0) + "deg",
    );
    this.style.setProperty(
      "--sui-overlay-rotate-y",
      numericAttribute(this, "rotation-y", 0) + "deg",
    );
    this.style.setProperty(
      "--sui-overlay-rotate-z",
      numericAttribute(this, "rotation-z", 0) + "deg",
    );
    this.style.visibility = "visible";
  }

  prepareSurface() {}
  calculatePosition() { return { x: 0, y: 0, z: 0 }; }

  offset(defaultY = 0) {
    return {
      x: numericAttribute(this, "offset-x", 0),
      y: numericAttribute(this, "offset-y", defaultY),
      z: numericAttribute(this, "offset-z", 0),
    };
  }
}


/* ===== text.js ===== */
{
/* Text — mirrors Typography roles from Typography.kt / TypeScaleTokens.kt. */

class SuiText extends SuiElement {
  static get observedAttributes() { return ["variant", "color", "text"]; }
  render() {
    const variant = this.attr("variant", "bodyLarge");
    const color = this.attr("color", themeColor("labelPrimaryLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline; }
        span { ${typeStyle(variant)} color:${color}; font-family: inherit; }
      </style>
      <span><slot>${this.attr("text", "")}</slot></span>`;
  }
}
define("sui-text", SuiText);

}

/* ===== icon.js ===== */
{
/*
 * Icon — mirrors Icon.kt. Default size 24, tint = LocalContentColor (labelPrimaryLight).
 * Renders slotted SVG / glyph / a src image, applying size + tint (via currentColor).
 */

class SuiIcon extends SuiElement {
  static get observedAttributes() { return ["size", "tint", "glyph", "src"]; }
  render() {
    const size = this.num("size", 24);
    const tint = this.attr("tint", themeColor("labelPrimaryLight"));
    const src = this.attr("src");
    const glyph = this.attr("glyph");
    let content;
    if (src) content = `<img src="${src}" width="${size}" height="${size}" alt="">`;
    else if (glyph) content = glyph;
    else content = `<slot></slot>`;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; color:${tint}; }
        .icon { width:${size}px; height:${size}px; display:inline-flex; align-items:center;
          justify-content:center; font-size:${size}px; line-height:1; color:${tint}; }
        ::slotted(svg), svg { width:${size}px; height:${size}px; fill:currentColor; }
      </style>
      <span class="icon">${content}</span>`;
  }
}
define("sui-icon", SuiIcon);

}

/* ===== button.js ===== */
{
/*
 * Button — mirrors Button.kt.
 * Sizes (minWidth/minHeight, cornerRadius, textStyle):
 *   Max:     104x56, r=32,  20/26/500
 *   Regular:  81x48, r=102, titleMedium 16/20/600
 *   Small:    69x40, r=20,  labelLarge  14/18/600
 *   Min:      57x32, r=16,  labelMedium 12/16/600
 * Default colors: container=fillPrimary, content=labelPrimaryLight (overridable).
 */

const SIZES = {
  max: { minW: 104, minH: 56, r: 32, hpad: 24, fs: 20, lh: 26, fw: 500 },
  regular: { minW: 81, minH: 48, r: 102, hpad: 20, fs: 16, lh: 20, fw: 600 },
  small: { minW: 69, minH: 40, r: 20, hpad: 16, fs: 14, lh: 18, fw: 600 },
  min: { minW: 57, minH: 32, r: 16, hpad: 12, fs: 12, lh: 16, fw: 600 },
};

class SuiButton extends SuiElement {
  static get observedAttributes() { return ["size", "disabled", "container-color", "content-color", "text"]; }
  render() {
    const s = SIZES[this.attr("size", "regular").toLowerCase()] || SIZES.regular;
    const disabled = this.bool("disabled");
    const container = this.attr("container-color", themeColor("fillPrimary"));
    const content = this.attr("content-color", themeColor("labelPrimaryLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-flex; }
        .btn {
          display: inline-flex; align-items: center; justify-content: center; gap: 4px;
          min-width: ${s.minW}px; min-height: ${s.minH}px;
          padding: 0 ${s.hpad}px; border-radius: ${s.r}px;
          background: ${container}; color: ${content};
          font-weight: ${s.fw}; font-size: ${s.fs}px; line-height: ${s.lh}px;
          font-family: inherit; border: none; cursor: pointer; user-select: none;
          transition: filter .12s ease; position: relative; overflow: hidden;
        }
        .btn.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .btn:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .btn:active::after { background: var(--sui-lighten-pressed, rgba(255,255,255,0.20)); }
        ::slotted(*) { display: inline-flex; align-items: center; }
      </style>
      <button class="btn ${disabled ? "sui-disabled" : ""}" ${disabled ? "disabled" : ""}>
        <slot name="leading"></slot>
        <span><slot>${this.attr("text", "Button")}</slot></span>
        <slot name="trailing"></slot>
      </button>`;
    this.shadowRoot.querySelector(".btn").addEventListener("click", () => {
      if (!disabled) emit(this, "click-action", {});
    });
  }
}
define("sui-button", SuiButton);

}

/* ===== icon-button.js ===== */
{
/*
 * IconButton / ToggleIconButton — mirrors IconButton.kt.
 * Sizes: Min 38x32, Small 46x40, Regular 56x48, Max 66x56. Shape r=35 (pill).
 */

const SIZES = {
  min: { minW: 38, minH: 32, icon: 16 },
  small: { minW: 46, minH: 40, icon: 20 },
  regular: { minW: 56, minH: 48, icon: 24 },
  max: { minW: 66, minH: 56, icon: 28 },
};

class SuiIconButton extends SuiElement {
  static get observedAttributes() { return ["size", "disabled", "container-color", "content-color", "icon", "selected", "toggle"]; }
  render() {
    const s = SIZES[this.attr("size", "regular").toLowerCase()] || SIZES.regular;
    const disabled = this.bool("disabled");
    const toggle = this.bool("toggle");
    const selected = this.bool("selected");
    const container = this.attr("container-color",
      toggle && selected ? themeColor("interaction") : themeColor("fillPrimary"));
    const content = this.attr("content-color", themeColor("labelPrimaryLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-flex; }
        .btn {
          display: inline-flex; align-items: center; justify-content: center;
          min-width: ${s.minW}px; min-height: ${s.minH}px; border-radius: 35px;
          background: ${container}; color: ${content};
          border: none; cursor: pointer; position: relative; overflow: hidden;
          transition: background-color .12s ease;
        }
        .btn.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .btn:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .btn:active::after { background: var(--sui-lighten-pressed, rgba(255,255,255,0.20)); }
        .icon { width:${s.icon}px; height:${s.icon}px; display:inline-flex; align-items:center; justify-content:center; font-size:${s.icon}px; }
        ::slotted(*) { width:${s.icon}px; height:${s.icon}px; }
      </style>
      <button class="btn ${disabled ? "sui-disabled" : ""}" ${disabled ? "disabled" : ""}>
        <span class="icon"><slot>${this.attr("icon", "★")}</slot></span>
      </button>`;
    this.shadowRoot.querySelector(".btn").addEventListener("click", () => {
      if (disabled) return;
      if (toggle) {
        const next = !selected;
        this.toggleAttribute("selected", next);
        emit(this, "checked-change", { selected: next });
      }
      emit(this, "click-action", {});
    });
  }
}
define("sui-icon-button", SuiIconButton);

}

/* ===== toggle-button.js ===== */
{
/*
 * ToggleButton — mirrors ToggleButton.kt.
 * Kotlin default colors (defaultToggleButtonColors):
 *   checked:   container=fillSecondary, content=labelPrimary
 *   unchecked: container=fillTertiary,  content=labelPrimary
 */

const SIZES = {
  max: { minW: 104, minH: 56, r: 32, hpad: 24, fs: 20, lh: 26, fw: 500 },
  regular: { minW: 57, minH: 32, r: 16, hpad: 12, fs: 12, lh: 16, fw: 600 },
  small: { minW: 69, minH: 40, r: 20, hpad: 16, fs: 14, lh: 18, fw: 600 },
  min: { minW: 57, minH: 32, r: 16, hpad: 12, fs: 12, lh: 16, fw: 600 },
};

class SuiToggleButton extends SuiElement {
  static get observedAttributes() { return ["size", "disabled", "checked", "text", "checked-container-color", "container-color", "content-color"]; }
  render() {
    const s = SIZES[this.attr("size", "regular").toLowerCase()] || SIZES.regular;
    const disabled = this.bool("disabled");
    const checked = this.bool("checked");
    const defaultContainer = checked ? themeColor("fillSecondary") : themeColor("fillTertiary");
    const defaultContent = themeColor("labelPrimary");
    const container = checked
      ? this.attr("checked-container-color", this.attr("container-color", defaultContainer))
      : this.attr("container-color", defaultContainer);
    const content = this.attr("content-color", defaultContent);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-flex; }
        .btn {
          display:inline-flex; align-items:center; justify-content:center; gap:4px;
          min-width:${s.minW}px; min-height:${s.minH}px; padding:0 ${s.hpad}px;
          border-radius:${s.r}px; background:${container}; color:${content};
          font-weight:${s.fw}; font-size:${s.fs}px; line-height:${s.lh}px;
          font-family:inherit; border:none; cursor:pointer; user-select:none;
          position:relative; overflow:hidden; transition:background-color .12s ease;
        }
        .btn.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .btn:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .btn:active::after { background: var(--sui-lighten-pressed, rgba(255,255,255,0.20)); }
      </style>
      <button class="btn ${disabled ? "sui-disabled" : ""}"><slot>${this.attr("text", "Toggle")}</slot></button>`;
    this.shadowRoot.querySelector(".btn").addEventListener("click", () => {
      if (disabled) return;
      const next = !checked;
      this.toggleAttribute("checked", next);
      emit(this, "checked-change", { checked: next });
    });
  }
}
define("sui-toggle-button", SuiToggleButton);

}

/* ===== switch.js ===== */
{
/*
 * Switch — mirrors Switch.kt.
 * Track 32x20 (r=10), thumb 16, checked-circle padding 2, thumb travel = 32-16-2*2 = 10.
 * checkedTrack=interaction, uncheckedTrack=fillTertiary, thumb=labelPrimaryLight.
 */

class SuiSwitch extends SuiElement {
  static get observedAttributes() { return ["checked", "disabled", "track-color", "thumb-color", "checked-track-color"]; }
  render() {
    const checked = this.bool("checked");
    const disabled = this.bool("disabled");
    const W = 32, H = 20, PAD = 2, THUMB = 16;
    const travel = W - THUMB - PAD * 2;
    const trackOn = this.attr("checked-track-color", themeColor("interaction"));
    const trackOff = this.attr("track-color", themeColor("fillTertiary"));
    const thumbC = this.attr("thumb-color", themeColor("labelPrimaryLight"));
    const track = checked ? trackOn : trackOff;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .wrap { padding:8px 4px; display:inline-flex; cursor:pointer; }
        .wrap.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .track { position:relative; width:${W}px; height:${H}px; border-radius:${H / 2}px;
                 background:${track}; transition:background-color .18s ease; }
        .thumb { position:absolute; top:${PAD}px; left:${PAD}px; width:${THUMB}px; height:${THUMB}px;
                 border-radius:50%; background:${thumbC};
                 transform:translateX(${checked ? travel : 0}px); transition:transform .18s cubic-bezier(.2,.8,.2,1);
                 box-shadow:${checked ? "none" : "0 1px 4px rgba(0,0,0,0.16)"}; }
      </style>
      <div class="wrap ${disabled ? "sui-disabled" : ""}" role="switch" aria-checked="${checked}">
        <div class="track"><div class="thumb"></div></div>
      </div>`;
    this.shadowRoot.querySelector(".wrap").addEventListener("click", () => {
      if (disabled) return;
      const next = !checked;
      this.toggleAttribute("checked", next);
      emit(this, "checked-change", { checked: next });
    });
  }
}
define("sui-switch", SuiSwitch);

}

/* ===== checkbox.js ===== */
{
/*
 * Checkbox / TriStateCheckbox — mirrors CheckBox.kt.
 * Hit box 32, content circle Regular 18 / Small 14, border 1.5.
 * off: circle stroke=labelSecondary. on/indeterminate: fill=labelPrimary, mark=labelPrimaryLight.
 */

class SuiCheckbox extends SuiElement {
  static get observedAttributes() { return ["state", "checked", "disabled", "size"]; }
  get state() {
    const s = this.attr("state");
    if (s) return s;
    return this.bool("checked") ? "on" : "off";
  }
  render() {
    const disabled = this.bool("disabled");
    const size = this.attr("size", "regular").toLowerCase() === "small" ? 14 : 18;
    const st = this.state;
    const BOX = 32;
    const bg = themeColor("labelPrimary");
    const mark = themeColor("labelPrimaryLight");
    const border = themeColor("labelSecondary");
    let inner;
    if (st === "off") {
      inner = `<div style="width:${size}px;height:${size}px;border-radius:50%;
        border:1.5px solid ${border};box-sizing:border-box;"></div>`;
    } else {
      const glyph = st === "indeterminate"
        ? `<div style="width:${size * 0.5}px;height:2px;border-radius:1px;background:${mark};"></div>`
        : `<svg width="${size * 0.66}" height="${size * 0.66}" viewBox="0 0 24 24" fill="none">
             <path d="M5 12.5l4.5 4.5L19 7.5" stroke="${mark}" stroke-width="2.6"
               stroke-linecap="round" stroke-linejoin="round"/></svg>`;
      inner = `<div style="width:${size}px;height:${size}px;border-radius:50%;background:${bg};
        display:flex;align-items:center;justify-content:center;">${glyph}</div>`;
    }
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .box { width:${BOX}px; height:${BOX}px; display:flex; align-items:center; justify-content:center;
               border-radius:50%; cursor:pointer; transition:background-color .12s ease; }
        .box.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .box:hover { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
      </style>
      <div class="box ${disabled ? "sui-disabled" : ""}" role="checkbox" aria-checked="${st === "on"}">${inner}</div>`;
    this.shadowRoot.querySelector(".box").addEventListener("click", () => {
      if (disabled) return;
      const next = st !== "on";
      this.setAttribute("state", next ? "on" : "off");
      this.toggleAttribute("checked", next);
      emit(this, "checked-change", { checked: next });
    });
  }
}
define("sui-checkbox", SuiCheckbox);

}

/* ===== badge.js ===== */
{
/*
 * Badge / DotBadge / NumberBadge — mirrors Badge.kt.
 * Dot size 12 (default color = error). Badge sizes ExtraSmall 12(r=2) / Small 18(r=4) / Regular 24(r=4).
 * NumberBadge: Small 16 / Regular 20, pill, bg=error, content=labelPrimaryLight, overflow "N+".
 */

class SuiDotBadge extends SuiElement {
  static get observedAttributes() { return ["color"]; }
  render() {
    const color = this.attr("color", themeColor("error"));
    this.shadowRoot.innerHTML = `
      <style>:host{display:inline-flex}.dot{width:12px;height:12px;border-radius:50%;background:${color};}</style>
      <div class="dot"></div>`;
  }
}
define("sui-dot-badge", SuiDotBadge);

const BADGE_SIZE = { extrasmall: { h: 12, r: 2, pad: 3 }, small: { h: 18, r: 4, pad: 4 }, regular: { h: 24, r: 4, pad: 8 } };

class SuiBadge extends SuiElement {
  static get observedAttributes() { return ["size", "text", "background-color", "content-color"]; }
  render() {
    const s = BADGE_SIZE[this.attr("size", "small").toLowerCase()] || BADGE_SIZE.small;
    const bg = this.attr("background-color", themeColor("fillPrimary"));
    const fg = this.attr("content-color", themeColor("labelPrimaryLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .badge { min-width:${s.h}px; height:${s.h}px; padding:0 ${s.pad}px; border-radius:${s.r}px;
          background:${bg}; color:${fg}; display:inline-flex; align-items:center; justify-content:center;
          font-size:12px; line-height:16px; font-weight:500; font-family:inherit; }
      </style>
      <div class="badge"><slot>${this.attr("text", "")}</slot></div>`;
  }
}
define("sui-badge", SuiBadge);

class SuiNumberBadge extends SuiElement {
  static get observedAttributes() { return ["number", "threshold", "overflow", "size", "background-color"]; }
  render() {
    const h = this.attr("size", "small").toLowerCase() === "regular" ? 20 : 16;
    const number = this.num("number", 0);
    const threshold = this.num("threshold", 99);
    const bg = this.attr("background-color", themeColor("error"));
    const fg = themeColor("labelPrimaryLight");
    const label = number > threshold ? `${threshold}+` : `${number}`;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .badge { min-width:${h}px; height:${h}px; padding:0 ${h < 18 ? 4 : 6}px; border-radius:${h / 2}px;
          background:${bg}; color:${fg}; display:inline-flex; align-items:center; justify-content:center;
          font-size:10px; line-height:14px; font-weight:600; font-family:inherit; }
      </style>
      <div class="badge">${label}</div>`;
  }
}
define("sui-number-badge", SuiNumberBadge);

}

/* ===== chip.js ===== */
{
/*
 * Chips — mirrors Chips.kt (ButtonChip / ToggleableChip / RemovableChip).
 * Sizes: Small h=32 (r=16, hpad 16 / with leading 12), Regular h=40 (r=38, hpad 20 / with leading 16).
 * Kotlin default colors (from defaultChipColors / defaultToggleableChipColors):
 *   ButtonChip:         container=fillSecondary, content=labelPrimary
 *   ToggleableChip off: container=fillTertiary,  content=labelPrimary
 *   ToggleableChip on:  container=fillSecondary, content=labelPrimary
 */

const SIZES = {
  small: { h: 32, r: 16, hpad: 16, hpadLeading: 12, fs: 14, lh: 18, fw: 600 },
  regular: { h: 40, r: 38, hpad: 20, hpadLeading: 16, fs: 16, lh: 20, fw: 600 },
};

class SuiChip extends SuiElement {
  static get observedAttributes() { return ["size", "disabled", "selected", "toggle", "removable", "label", "leading-icon", "container-color", "content-color"]; }
  render() {
    const s = SIZES[this.attr("size", "small").toLowerCase()] || SIZES.small;
    const disabled = this.bool("disabled");
    const toggle = this.bool("toggle");
    const selected = this.bool("selected");
    const removable = this.bool("removable");
    const leadingIcon = this.attr("leading-icon");
    const hasLeading = leadingIcon != null;
    const active = toggle && selected;
    const defaultBg = active ? themeColor("fillSecondary") : (toggle ? themeColor("fillTertiary") : themeColor("fillSecondary"));
    const defaultFg = themeColor("labelPrimary");
    const bg = this.attr("container-color", defaultBg);
    const fg = this.attr("content-color", defaultFg);
    const hpad = hasLeading ? s.hpadLeading : s.hpad;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .chip { display:inline-flex; align-items:center; gap:4px; height:${s.h}px;
          padding:0 ${hpad}px; border-radius:${s.r}px; background:${bg}; color:${fg};
          font-weight:${s.fw}; font-size:${s.fs}px; line-height:${s.lh}px; font-family:inherit;
          cursor:pointer; user-select:none; position:relative; overflow:hidden;
          transition:background-color .12s ease; }
        .chip.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .chip::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .chip:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .chip:active::after { background: var(--sui-lighten-pressed, rgba(255,255,255,0.20)); }
        .lead { display:inline-flex; width:${s.fs + 2}px; height:${s.fs + 2}px; align-items:center; justify-content:center; }
        .close { margin-left:2px; opacity:.8; font-size:${s.fs}px; }
      </style>
      <div class="chip ${disabled ? "sui-disabled" : ""}" role="button">
        ${hasLeading ? `<span class="lead">${leadingIcon}</span>` : ""}
        <span><slot>${this.attr("label", "Chip")}</slot></span>
        ${removable ? `<span class="close">✕</span>` : ""}
      </div>`;
    this.shadowRoot.querySelector(".chip").addEventListener("click", (e) => {
      if (disabled) return;
      if (removable && e.target.classList.contains("close")) {
        emit(this, "remove", {});
        return;
      }
      if (toggle) {
        const next = !selected;
        this.toggleAttribute("selected", next);
        emit(this, "checked-change", { selected: next });
      }
      emit(this, "click-action", {});
    });
  }
}
define("sui-chip", SuiChip);

}

/* ===== slider.js ===== */
{
/*
 * Slider — mirrors Slider.kt / Figma "Slider" component set.
 * Sizes only govern thickness (track height / knob dot / thumb area):
 *   Small   8 / 18 / 32
 *   Regular 24 / 18 / 32
 *   Max     48 / 32 / 48
 * Length is independent of size (Figma's 240/360 artboards are just example
 * frames). Width defaults to 240px and is overridable via the `width` attribute
 * ("240", "320px", "100%", …) so sliders align regardless of size.
 * Colors are driven by PicoTheme (fillTertiary / fillSecondary / labelPrimaryLight)
 * and may be overridden per-instance with track-color / progress-color / thumb-color.
 */

const SPECS = {
  small: { track: 8, thumb: 18, area: 32 },
  regular: { track: 24, thumb: 18, area: 32 },
  max: { track: 48, thumb: 32, area: 48 },
};

const DEFAULT_WIDTH = 240;

class SuiSlider extends SuiElement {
  static get observedAttributes() { return ["value", "min", "max", "size", "width", "disabled", "track-color", "progress-color", "thumb-color"]; }
  attributeChangedCallback(name) {
    if (name === "value" && this._internalWrite) return;
    super.attributeChangedCallback(name);
  }
  render() {
    const s = SPECS[this.attr("size", "regular").toLowerCase()] || SPECS.regular;
    const disabled = this.bool("disabled");
    const min = this.num("min", 0), max = this.num("max", 1);
    const rawW = this.attr("width");
    const width = rawW == null ? `${DEFAULT_WIDTH}px` : (/^\d+$/.test(rawW) ? `${rawW}px` : rawW);
    // `value` is the single source of truth: re-sync on every render so an
    // external (controlled) update is reflected, keeping the last committed
    // value when the attribute is absent.
    this._value = this.hasAttribute("value") ? this.num("value", 0) : (this._value ?? 0);

    const trackColor = this.attr("track-color", themeColor("fillTertiary"));
    const progressColor = this.attr("progress-color", themeColor("fillSecondary"));
    const thumbColor = this.attr("thumb-color", themeColor("labelPrimaryLight"));

    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .slider { position:relative; width:${width}; height:${s.area}px; display:flex; align-items:center;
          cursor:pointer; touch-action:none; }
        .slider.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .track, .progress { position:absolute; top:50%; transform:translateY(-50%);
          height:${s.track}px; border-radius:${s.track / 2}px; }
        .track { left:0; right:0; background:${trackColor}; }
        .progress { left:0; width:0;
          background:${progressColor}; overflow:hidden; }
        .progress::after { content:""; position:absolute; inset:0; background:transparent;
          transition:background-color .12s ease; pointer-events:none; }
        .slider:hover .progress::after, .slider.dragging .progress::after {
          background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .thumb { position:absolute; top:50%; transform:translateY(-50%); z-index:1;
          width:${s.thumb}px; height:${s.thumb}px; border-radius:50%;
          background:${thumbColor}; box-shadow:0 0 4px 0 rgba(0,0,0,0.12); }
      </style>
      <div class="slider ${disabled ? "sui-disabled" : ""}" role="slider" tabindex="0" aria-valuenow="${this._value}" aria-valuemin="${min}" aria-valuemax="${max}">
        <div class="track"></div>
        <div class="progress"></div>
        <div class="thumb"></div>
      </div>`;

    const el = this.shadowRoot.querySelector(".slider");
    const progress = this.shadowRoot.querySelector(".progress");
    const thumb = this.shadowRoot.querySelector(".thumb");

    // Position the thumb/progress from the current value — no DOM rebuild.
    // Measure the actual rendered width so percentage / responsive widths work.
    // Match the native/Figma geometry: the invisible thumb area travels inside
    // the component, while the visible knob is centered within that area. The
    // rounded progress cap extends behind the knob so no square cut is exposed.
    const paint = () => {
      const len = el.getBoundingClientRect().width || DEFAULT_WIDTH;
      const travel = Math.max(0, len - s.area);
      const range = max - min;
      const frac = range === 0 ? 0 : Math.max(0, Math.min(1, (this._value - min) / range));
      const thumbAreaLeft = frac * travel;
      const progressWidth = Math.min(len, s.track + thumbAreaLeft);
      progress.style.width = `${progressWidth}px`;
      thumb.style.left = `${thumbAreaLeft + (s.area - s.thumb) / 2}px`;
      el.setAttribute("aria-valuenow", String(this._value));
    };
    paint();

    if (disabled) return;

    const setFromX = (clientX) => {
      const rect = el.getBoundingClientRect();
      const travel = Math.max(1, rect.width - s.area);
      const frac = Math.max(
        0,
        Math.min(1, (clientX - rect.left - s.area / 2) / travel),
      );
      this._value = min + frac * (max - min);
      this._internalWrite = true;
      this.setAttribute("value", String(this._value));
      this._internalWrite = false;
      paint();
      emit(this, "value-change", { value: this._value });
    };

    const move = (ev) => setFromX(ev.clientX);
    const up = (ev) => {
      el.classList.remove("dragging");
      el.releasePointerCapture?.(ev.pointerId);
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
    el.addEventListener("pointerdown", (ev) => {
      ev.preventDefault();
      el.classList.add("dragging");
      el.setPointerCapture?.(ev.pointerId);
      setFromX(ev.clientX);
      window.addEventListener("pointermove", move);
      window.addEventListener("pointerup", up);
    });
    // Keyboard support.
    el.addEventListener("keydown", (ev) => {
      const stepPx = (max - min) / 100;
      if (ev.key === "ArrowRight" || ev.key === "ArrowUp") { this._value = Math.min(max, this._value + stepPx); }
      else if (ev.key === "ArrowLeft" || ev.key === "ArrowDown") { this._value = Math.max(min, this._value - stepPx); }
      else return;
      ev.preventDefault();
      this._internalWrite = true;
      this.setAttribute("value", String(this._value));
      this._internalWrite = false;
      paint();
      emit(this, "value-change", { value: this._value });
    });
  }
}
define("sui-slider", SuiSlider);

}

/* ===== progress.js ===== */
{
/*
 * ProgressIndicators — mirrors LinearProgressIndicator.kt & CircularProgressIndicator.kt.
 * Linear: width 240, Small h=4 / Regular h=8. Circular: Small 20 / Regular 30 / Max 40, stroke=10% of size (min 2).
 * Colors (from Kotlin defaults):
 *   Linear:   track=fillTertiary, bar=labelPrimaryLight
 *   Circular: track=fillTertiary, bar=interaction (determinate) / labelPrimaryLight (indeterminate)
 */

class SuiLinearProgress extends SuiElement {
  static get observedAttributes() { return ["value", "size", "indeterminate", "track-color", "progress-color"]; }
  render() {
    const h = this.attr("size", "regular").toLowerCase() === "small" ? 4 : 8;
    const indeterminate = this.bool("indeterminate");
    const value = Math.max(0, Math.min(1, this.num("value", 0.4)));
    const trackC = this.attr("track-color", themeColor("fillTertiary"));
    const barC = this.attr("progress-color", themeColor("labelPrimaryLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .track { width:240px; height:${h}px; border-radius:${h / 2}px; background:${trackC}; overflow:hidden; position:relative; }
        .bar { position:absolute; top:0; bottom:0; background:${barC}; border-radius:${h / 2}px; }
        .det { left:0; width:${value * 100}%; }
        .indet { width:40%; animation:sui-linear 1.4s infinite; }
        @keyframes sui-linear { 0%{left:-40%} 100%{left:100%} }
      </style>
      <div class="track"><div class="bar ${indeterminate ? "indet" : "det"}"></div></div>`;
  }
}
define("sui-linear-progress", SuiLinearProgress);

const CIRC = { small: 20, regular: 30, max: 40 };

class SuiCircularProgress extends SuiElement {
  static get observedAttributes() { return ["value", "size", "indeterminate", "track-color", "progress-color"]; }
  render() {
    const size = CIRC[this.attr("size", "max").toLowerCase()] || CIRC.max;
    const stroke = Math.max(2, size * 0.1);
    const indeterminate = this.bool("indeterminate");
    const value = Math.max(0, Math.min(1, this.num("value", 0.6)));
    const r = (size - stroke) / 2;
    const c = 2 * Math.PI * r;
    const dash = indeterminate ? c * 0.25 : c * value;
    const trackC = this.attr("track-color", themeColor("fillTertiary"));
    const defaultBar = indeterminate ? themeColor("labelPrimaryLight") : themeColor("interaction");
    const barC = this.attr("progress-color", defaultBar);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        svg { transform: rotate(-90deg); }
        .spin { transform-origin:center; animation:sui-spin 1s linear infinite; }
        @keyframes sui-spin { to { transform: rotate(270deg); } }
      </style>
      <svg width="${size}" height="${size}" class="${indeterminate ? "spin" : ""}">
        <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none"
          stroke="${trackC}" stroke-width="${stroke}"/>
        <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none"
          stroke="${barC}" stroke-width="${stroke}" stroke-linecap="round"
          stroke-dasharray="${dash} ${c}"/>
      </svg>`;
  }
}
define("sui-circular-progress", SuiCircularProgress);

}

/* ===== divider.js ===== */
{
/*
 * Divider — mirrors Divider.kt. thickness 0.5, color dividerLine. Horizontal or vertical.
 */

class SuiDivider extends SuiElement {
  static get observedAttributes() { return ["orientation", "color", "thickness"]; }
  render() {
    const vertical = this.attr("orientation", "horizontal") === "vertical";
    const color = this.attr("color", themeColor("dividerLine"));
    const t = this.num("thickness", 0.5);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:${vertical ? "inline-flex" : "block"}; ${vertical ? "align-self:stretch;" : "width:100%;"} }
        .line { background:${color};
          ${vertical ? `width:${t}px; height:100%; min-height:24px;` : `height:${t}px; width:100%;`} }
      </style>
      <div class="line"></div>`;
  }
}
define("sui-divider", SuiDivider);

}

/* ===== segment-control.js ===== */
{
/*
 * SegmentControls — mirrors SegmentControls.kt.
 * Container bg=fillTertiary, container padding 4, item gap 4.
 * Sizes: Small h=40 / Regular h=48 / Rich h=88.
 * Selected item bg=fillSecondary / content=labelPrimary; unselected content=labelTertiary.
 */

const H = { small: 40, regular: 48, rich: 88 };

class SuiSegmentControl extends SuiElement {
  static get observedAttributes() { return ["options", "selected-index", "size", "disabled"]; }
  render() {
    const items = (this.attr("options", "") || "").split(",").map((s) => s.trim()).filter(Boolean);
    const h = H[this.attr("size", "small").toLowerCase()] || H.small;
    const sel = this.num("selected-index", 0);
    const disabled = this.bool("disabled");
    const pad = 4, gap = 4;
    const outerR = Dimension.RadiusLarge;
    const innerR = outerR - pad;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .bar { display:inline-flex; gap:${gap}px; padding:${pad}px; height:${h}px; border-radius:${outerR}px;
          background:${themeColor("fillTertiary")}; box-sizing:border-box; }
        .bar.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .seg { display:inline-flex; align-items:center; justify-content:center; padding:0 12px;
          border-radius:${innerR}px; font-size:16px; line-height:20px; font-weight:600; font-family:inherit;
          cursor:pointer; user-select:none; color:${themeColor("labelTertiary")}; transition:all .15s ease;
          background:transparent; border:none; }
        .seg.active { background:${themeColor("fillSecondary")}; color:${themeColor("labelPrimary")}; }
        .seg:not(.active):hover { color:${themeColor("labelPrimary")};
          background: var(--sui-lighten-hover, rgba(255,255,255,0.08)); }
      </style>
      <div class="bar ${disabled ? "sui-disabled" : ""}" role="tablist">
        ${items.map((label, i) => `<button class="seg ${i === sel ? "active" : ""}" data-i="${i}">${label}</button>`).join("")}
      </div>`;
    this.shadowRoot.querySelectorAll(".seg").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (disabled) return;
        const i = +btn.dataset.i;
        this.setAttribute("selected-index", String(i));
        emit(this, "select", { index: i, value: items[i] });
      });
    });
  }
}
define("sui-segment-control", SuiSegmentControl);

}

/* ===== tab-bar.js ===== */
{
/*
 * TabBar — mirrors the PICO OS 7 Tab Bar specification.
 * Supports horizontal text/icon tabs, icon labels, vertical icon tabs,
 * badges, hover expansion, and an optional secondary tab row.
 * Icon slots use icon-N; the hover menu can override them with expanded-icon-N.
 *
 * Colors are driven by PicoTheme:
 *   - Material bar background = component-level glass variable
 *   - Active tab = fillPrimary / labelPrimaryLight
 *   - Inactive tab = dark label on the light material
 *   - Focus ring = interaction
 *   - Badge = error
 */

const DEFAULT_ICONS = ["◷", "♧", "◇", "▤", "▭", "⌕", "○"];

function list(value, preserveEmpty = false) {
  const values = (value || "").split(",").map((item) => item.trim()).slice(0, 7);
  return preserveEmpty ? values : values.filter(Boolean);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

class SuiTabBar extends SuiElement {
  static get observedAttributes() {
    return [
      "items", "icons", "badges", "selected-index", "type", "orientation",
      "show-labels", "expand-on-hover", "sub-items", "sub-selected-index",
      "disabled", "equal-width",
    ];
  }

  render() {
    const previousBar = this.shadowRoot.querySelector(".bar");
    const items = list(this.attr("items", "最近,通知,空间,文章,书库,搜索"));
    const icons = list(this.attr("icons", ""), true);
    const badges = list(this.attr("badges", ""), true);
    const subItems = list(this.attr("sub-items", ""));
    const type = this.attr("type", "icon").toLowerCase();
    const vertical = this.attr("orientation", "horizontal").toLowerCase() === "vertical";
    const showLabels = !vertical && type === "icon" && this.bool("show-labels");
    const expandOnHover = this.hasAttribute("expand-on-hover")
      ? this.bool("expand-on-hover")
      : !vertical && type === "icon" && !showLabels;
    const horizontalHoverLabels = !vertical && type === "icon" && expandOnHover;
    const verticalHoverPanel = vertical && expandOnHover;
    this._expanded = Boolean(
      expandOnHover && (
        this._expanded ||
        previousBar?.matches(":hover") ||
        previousBar?.matches(":focus-within")
      )
    );
    const equalWidth = this.bool("equal-width");
    const selected = Math.min(Math.max(this.num("selected-index", 0), 0), Math.max(items.length - 1, 0));
    const subSelected = Math.min(
      Math.max(this.num("sub-selected-index", 0), 0),
      Math.max(subItems.length - 1, 0),
    );
    const hasSubTabs = !vertical && type === "icon" && showLabels && subItems.length > 0;
    const mode = vertical ? "vertical" : type === "icon" ? "icon-mode" : "text-mode";

    const barBg = "var(--Background-MaterialRegular, rgba(255, 255, 255, .34))";
    const barBorder = `var(--Line-Border,
      var(--sui-tab-bar-border, color(display-p3 1 1 1 / .34)))`;
    const activeTabBg = themeColor("fillPrimary");
    const activeTabFg = themeColor("labelPrimaryLight");
    const inactiveFg = themeColor("labelPrimary");
    const verticalActiveBg = themeColor("fillPrimary");
    const subActiveBg = themeColor("fillPrimary");
    const subActiveFg = themeColor("labelPrimaryLight");
    const focusRing = themeColor("interaction");
    const badgeBg = themeColor("error");
    const badgeFg = themeColor("labelPrimaryLight");
    const hoverOverlay = "var(--sui-lighten-hover, rgba(255,255,255,0.12))";

    const tabs = items.map((label, index) => {
      const active = index === selected;
      const badge = badges[index];
      const icon = icons[index] || DEFAULT_ICONS[index % DEFAULT_ICONS.length];
      const iconContent = `
        <span class="glyph" aria-hidden="true">
          <slot name="icon-${index}">${escapeHtml(icon)}</slot>
        </span>`;
      const labelContent = `<span class="label">${escapeHtml(label)}</span>`;
      return `
        <button class="tab ${active ? "active" : ""}" role="tab"
          aria-selected="${active}" tabindex="${active ? 0 : -1}" data-index="${index}">
          ${mode === "text-mode" ? labelContent : iconContent}
          ${showLabels || horizontalHoverLabels ? labelContent : ""}
          ${badge ? `<span class="badge" aria-label="${escapeHtml(badge)}">${escapeHtml(badge)}</span>` : ""}
        </button>`;
    }).join("");

    const hoverTabs = verticalHoverPanel ? items.map((label, index) => {
      const active = index === selected;
      const badge = badges[index];
      const icon = icons[index] || DEFAULT_ICONS[index % DEFAULT_ICONS.length];
      return `
        <button class="hover-tab ${active ? "active" : ""}" role="tab"
          aria-selected="${active}" tabindex="${active ? 0 : -1}" data-index="${index}">
          <span class="glyph" aria-hidden="true">
            <slot name="expanded-icon-${index}">${escapeHtml(icon)}</slot>
          </span>
          <span class="hover-label">${escapeHtml(label)}</span>
          ${badge ? `<span class="badge" aria-label="${escapeHtml(badge)}">${escapeHtml(badge)}</span>` : ""}
        </button>`;
    }).join("") : "";

    const subTabs = subItems.map((label, index) => `
      <button class="sub-tab ${index === subSelected ? "active" : ""}" role="tab"
        aria-selected="${index === subSelected}" tabindex="${index === subSelected ? 0 : -1}"
        data-sub-index="${index}">${escapeHtml(label)}</button>
    `).join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: inline-flex;
          box-sizing: border-box;
          font-family: inherit;
        }
        :host([disabled]) { opacity: ${DISABLE_ALPHA}; pointer-events: none; }
        * { box-sizing: border-box; }
        button { border: 0; margin: 0; font: inherit; letter-spacing: 0; }
        .bar {
          display: inline-flex;
          position: relative;
          align-items: center;
          justify-content: center;
        }
        .bar.horizontal {
          flex-direction: ${hasSubTabs ? "column" : "row"};
          gap: ${hasSubTabs ? 8 : 0}px;
          padding: ${hasSubTabs
            ? "3px 3px calc(7px + env(safe-area-inset-bottom, 0px))"
            : "7px 7px calc(7px + env(safe-area-inset-bottom, 0px))"};
          min-height: ${hasSubTabs ? 148 : showLabels ? 88 : 64}px;
          border-radius: 32px;
          border: 1px solid ${barBorder};
          background: ${barBg};
          backdrop-filter: blur(50px);
          -webkit-backdrop-filter: blur(50px);
        }
        .bar.horizontal.hover-labels {
          transition: min-height .18s ease;
        }
        .bar.vertical { flex-direction: column; gap: 8px; }
        .tabs {
          display: flex;
          align-items: center;
          justify-content: center;
          flex-direction: ${vertical ? "column" : "row"};
          gap: ${vertical ? 8 : 4}px;
          ${hasSubTabs ? `
            padding: 4px;
            border-radius: 28px;
            background: ${themeColor("fillTertiary")};
          ` : ""}
        }
        .tab, .sub-tab, .hover-tab {
          position: relative;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          flex: ${equalWidth && !vertical ? "1 1 0" : "0 0 auto"};
          min-width: 0;
          color: ${inactiveFg};
          background: transparent;
          cursor: pointer;
          user-select: none;
          outline: none;
          transition: background-color .14s ease, color .14s ease, box-shadow .14s ease,
            width .18s ease, height .18s ease, padding .18s ease, gap .18s ease;
        }
        .tab::after, .sub-tab::after, .hover-tab::after {
          content: "";
          position: absolute;
          inset: 0;
          border-radius: inherit;
          background: transparent;
          pointer-events: none;
          transition: background-color .12s ease;
        }
        .tab:hover::after, .tab:focus-visible::after,
        .sub-tab:hover::after, .sub-tab:focus-visible::after,
        .hover-tab:hover::after, .hover-tab:focus-visible::after {
          background: ${hoverOverlay};
        }
        .tab:focus-visible, .sub-tab:focus-visible, .hover-tab:focus-visible {
          box-shadow: 0 0 0 2px ${focusRing};
        }
        .horizontal .tab {
          height: ${showLabels ? 72 : 48}px;
          border-radius: 24px;
        }
        .text-mode .tab {
          padding: 0 16px;
          font-size: 16px;
          line-height: 20px;
          font-weight: 600;
        }
        .icon-mode .tab {
          width: ${hasSubTabs ? 80 : 64}px;
          padding: 14px 8px;
          flex-direction: column;
          gap: ${showLabels ? 8 : 0}px;
        }
        .horizontal .tab.active {
          color: ${activeTabFg};
          background: ${activeTabBg};
        }
        .vertical .tab {
          width: 48px;
          height: 48px;
          padding: 0;
          gap: 4px;
          flex-direction: row;
          justify-content: flex-start;
          border-radius: 28px;
          border: 1px solid ${barBorder};
          color: ${inactiveFg};
          background: ${barBg};
          overflow: visible;
        }
        .vertical .tab.active { background: ${verticalActiveBg}; color: ${activeTabFg}; }
        .vertical .tab .glyph {
          width: 48px;
          height: 48px;
          flex: 0 0 48px;
        }
        .hover-panel {
          position: absolute;
          left: 64px;
          top: -12px;
          display: flex;
          flex-direction: column;
          align-items: stretch;
          gap: 8px;
          min-width: 165px;
          padding: 11px;
          border-radius: 16px;
          border: 1px solid ${barBorder};
          background: ${barBg};
          box-shadow: 0 16px 32px rgba(0,0,0,.18);
          backdrop-filter: blur(50px);
          -webkit-backdrop-filter: blur(50px);
          opacity: 0;
          visibility: hidden;
          pointer-events: none;
          transform: translateX(-8px);
          transform-origin: left center;
          transition: transform .18s ease, visibility 0s linear .18s;
          z-index: 10;
        }
        .hover-panel::before {
          content: "";
          position: absolute;
          left: -16px;
          top: 0;
          width: 16px;
          height: 100%;
        }
        .vertical.expand:hover .hover-panel,
        .vertical.expand:focus-within .hover-panel,
        .vertical.expand.is-expanded .hover-panel {
          opacity: 1;
          visibility: visible;
          pointer-events: auto;
          transform: translateX(0);
          transition-delay: 0s;
        }
        .hover-tab {
          width: 100%;
          height: 48px;
          padding: 0 18px 0 14px;
          gap: 4px;
          justify-content: flex-start;
          border-radius: 28px;
          color: ${inactiveFg};
          white-space: nowrap;
        }
        .hover-tab.active {
          color: ${activeTabFg};
          background: ${verticalActiveBg};
        }
        .hover-tab .glyph { flex: 0 0 20px; }
        .hover-label {
          max-width: 192px;
          overflow: hidden;
          text-overflow: ellipsis;
          font-size: 14px;
          line-height: 18px;
          font-weight: 600;
        }
        .glyph {
          position: relative;
          display: inline-flex;
          width: 20px;
          height: 20px;
          align-items: center;
          justify-content: center;
          flex: 0 0 20px;
          color: currentColor;
          font-size: 20px;
          line-height: 20px;
        }
        ::slotted(svg) { width: 20px; height: 20px; fill: currentColor; color: currentColor; }
        ::slotted(img) { width: 20px; height: 20px; object-fit: contain; }
        .icon-mode .tab .label {
          display: block;
          max-width: 56px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          font-size: 12px;
          line-height: 16px;
          font-weight: 500;
        }
        .icon-mode .tab.active .label { font-weight: 600; }
        .horizontal.hover-labels .label {
          max-height: 0;
          opacity: 0;
          transform: translateY(-2px);
          transition: max-height .18s ease, opacity .12s ease, transform .18s ease;
        }
        .horizontal.hover-labels:hover,
        .horizontal.hover-labels:focus-within,
        .horizontal.hover-labels.is-expanded {
          min-height: 88px;
        }
        .horizontal.hover-labels:hover .tab,
        .horizontal.hover-labels:focus-within .tab,
        .horizontal.hover-labels.is-expanded .tab {
          height: 72px;
          gap: 8px;
        }
        .horizontal.hover-labels:hover .label,
        .horizontal.hover-labels:focus-within .label,
        .horizontal.hover-labels.is-expanded .label {
          max-height: 16px;
          opacity: 1;
          transform: translateY(0);
        }
        .badge {
          position: absolute;
          top: ${vertical ? 0 : 6}px;
          right: ${vertical ? -2 : 4}px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-width: 16px;
          height: 16px;
          padding: 0 4px;
          border-radius: 999px;
          color: ${badgeFg};
          background: ${badgeBg};
          font-size: 10px;
          line-height: 14px;
          font-weight: 600;
          z-index: 3;
        }
        .horizontal.icon-mode .badge {
          left: calc(50% + 10px);
          right: auto;
        }
        .hover-tab .badge { top: 0; right: -2px; }
        .sub-tabs {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
          padding: 0 4px;
        }
        .sub-tab {
          height: 48px;
          padding: 0 16px;
          border-radius: 8px;
          font-size: 14px;
          line-height: 18px;
          font-weight: 500;
        }
        .sub-tab.active {
          border-radius: 24px;
          color: ${subActiveFg};
          background: ${subActiveBg};
          font-weight: 600;
        }
      </style>
      <nav class="bar ${vertical ? "vertical" : "horizontal"} ${mode} ${verticalHoverPanel ? "expand" : ""} ${horizontalHoverLabels ? "hover-labels" : ""} ${this._expanded ? "is-expanded" : ""}"
        aria-label="Tab bar">
        <div class="tabs" role="tablist" aria-orientation="${vertical ? "vertical" : "horizontal"}">
          ${tabs}
        </div>
        ${verticalHoverPanel ? `<div class="hover-panel" role="tablist" aria-label="Expanded tab menu">${hoverTabs}</div>` : ""}
        ${hasSubTabs ? `<div class="sub-tabs" role="tablist">${subTabs}</div>` : ""}
      </nav>`;

    this.shadowRoot.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", () => this._selectTab(Number(tab.dataset.index), items));
      tab.addEventListener("keydown", (event) => this._onKeydown(event, ".tab", vertical, items));
    });
    this.shadowRoot.querySelectorAll(".sub-tab").forEach((tab) => {
      tab.addEventListener("click", () => this._selectSubTab(Number(tab.dataset.subIndex), subItems));
      tab.addEventListener("keydown", (event) => this._onSubKeydown(event, subItems));
    });
    this.shadowRoot.querySelectorAll(".hover-tab").forEach((tab) => {
      tab.addEventListener("click", () => this._selectTab(Number(tab.dataset.index), items));
      tab.addEventListener("keydown", (event) => this._onKeydown(event, ".hover-tab", true, items));
    });
    if (expandOnHover) this._bindExpansionState();
  }

  _selectTab(index, items) {
    const keepExpanded = this._preserveExpansion();
    this.setAttribute("selected-index", String(index));
    if (keepExpanded) this._restoreExpansion();
    emit(this, "select", { index, value: items[index] });
  }

  _selectSubTab(index, items) {
    const keepExpanded = this._preserveExpansion();
    this.setAttribute("sub-selected-index", String(index));
    if (keepExpanded) this._restoreExpansion();
    emit(this, "sub-select", { index, value: items[index] });
  }

  _preserveExpansion() {
    const bar = this.shadowRoot.querySelector(".bar");
    if (!bar || !this.bool("expand-on-hover")) return false;
    this._expanded =
      this._expanded ||
      bar.classList.contains("is-expanded") ||
      bar.matches(":hover") ||
      bar.matches(":focus-within") ||
      (bar.classList.contains("horizontal") && bar.offsetHeight > 64);
    return this._expanded;
  }

  _restoreExpansion() {
    this._expanded = true;
    this.shadowRoot.querySelector(".bar")?.classList.add("is-expanded");
    queueMicrotask(() => {
      if (!this._expanded) return;
      this.shadowRoot.querySelector(".bar")?.classList.add("is-expanded");
    });
  }

  _bindExpansionState() {
    const bar = this.shadowRoot.querySelector(".bar");
    if (!bar) return;
    const isCurrent = () => this.shadowRoot.querySelector(".bar") === bar;
    const expand = () => {
      if (!isCurrent()) return;
      this._expanded = true;
      bar.classList.add("is-expanded");
    };
    const collapse = () => {
      if (!isCurrent()) return;
      this._expanded = false;
      bar.classList.remove("is-expanded");
    };
    bar.addEventListener("pointerenter", expand);
    bar.addEventListener("pointerleave", collapse);
    bar.addEventListener("focusin", expand);
    bar.addEventListener("focusout", () => {
      requestAnimationFrame(() => {
        const current = this.shadowRoot.querySelector(".bar");
        if (current === bar && !current.matches(":focus-within") && !current.matches(":hover")) collapse();
      });
    });
  }

  _onKeydown(event, selector, vertical, items) {
    const previous = vertical ? "ArrowUp" : "ArrowLeft";
    const next = vertical ? "ArrowDown" : "ArrowRight";
    if (![previous, next, "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const tabs = [...this.shadowRoot.querySelectorAll(selector)];
    const current = Number(event.currentTarget.dataset.index);
    let index = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 :
      (current + (event.key === next ? 1 : -1) + tabs.length) % tabs.length;
    this._selectTab(index, items);
    requestAnimationFrame(() => this.shadowRoot.querySelector(`${selector}[data-index="${index}"]`)?.focus());
  }

  _onSubKeydown(event, items) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const tabs = [...this.shadowRoot.querySelectorAll(".sub-tab")];
    const current = Number(event.currentTarget.dataset.subIndex);
    const index = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 :
      (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
    this._selectSubTab(index, items);
    requestAnimationFrame(() => this.shadowRoot.querySelector(`[data-sub-index="${index}"]`)?.focus());
  }
}

define("sui-tab-bar", SuiTabBar);

}

/* ===== text-field.js ===== */
{
/*
 * TextField / TextArea — mirrors TextField.kt.
 * MinHeight 48, DefaultWidth 280, cornerRadius RadiusMediumLarge(12), borderWidth 1.
 * Kotlin default colors (defaultTextFieldColors):
 *   container=fillTertiary, focused indicator=fillSecondary,
 *   text=labelPrimary, placeholder=labelQuaternary, supporting=labelTertiary,
 *   error indicator=error, cursor=fillPrimary.
 */

class SuiTextField extends SuiElement {
  static get observedAttributes() { return ["value", "placeholder", "disabled", "multiline", "width", "supporting-text", "clearable", "error", "container-color", "text-color", "placeholder-color", "focus-color", "supporting-color"]; }
  render() {
    const disabled = this.bool("disabled");
    const multiline = this.bool("multiline");
    const width = this.num("width", 280);
    const r = Dimension.RadiusMediumLarge;
    const support = this.attr("supporting-text");
    const isError = this.bool("error");
    const clearable = this.bool("clearable");
    const containerC = this.attr("container-color", themeColor("fillTertiary"));
    const textC = this.attr("text-color", themeColor("labelPrimary"));
    const phC = this.attr("placeholder-color", themeColor("labelQuaternary"));
    const focusC = isError
      ? themeColor("error")
      : this.attr("focus-color", themeColor("fillSecondary"));
    const supC = this.attr("supporting-color", isError ? themeColor("error") : themeColor("labelTertiary"));
    const tag = multiline ? "textarea" : "input";
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .wrap { width:${width}px; }
        .wrap.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .field { display:flex; align-items:center; width:100%; min-height:48px;
          background:${containerC}; border-radius:${r}px; border:1px solid transparent;
          padding:0 12px; transition:border-color .12s ease; caret-color:${themeColor("fillPrimary")}; }
        .field:focus-within { border-color:${focusC}; }
        input, textarea { flex:1; background:transparent; border:none; outline:none;
          color:${textC}; font-size:16px; line-height:20px; font-weight:500;
          font-family:inherit; padding:12px 0; resize:${multiline ? "vertical" : "none"}; }
        textarea { min-height:48px; }
        input::placeholder, textarea::placeholder { color:${phC}; opacity:1; }
        .clear { cursor:pointer; color:${phC}; padding:4px;
          display:${clearable ? "inline-flex" : "none"}; background:transparent; border:none; font-size:14px; }
        .support { margin-top:4px; font-size:12px; line-height:16px; color:${supC}; }
      </style>
      <div class="wrap ${disabled ? "sui-disabled" : ""}">
        <div class="field">
          <${tag} placeholder="${this.attr("placeholder", "")}" ${disabled ? "disabled" : ""}>${multiline ? this.attr("value", "") : ""}</${tag}>
          <button class="clear">✕</button>
        </div>
        ${support ? `<div class="support">${support}</div>` : ""}
      </div>`;
    const input = this.shadowRoot.querySelector(tag);
    if (!multiline) input.value = this.attr("value", "");
    input.addEventListener("input", () => emit(this, "value-change", { value: input.value }));
    const clear = this.shadowRoot.querySelector(".clear");
    if (clear) clear.addEventListener("click", () => { input.value = ""; emit(this, "value-change", { value: "" }); input.focus(); });
  }
}
define("sui-text-field", SuiTextField);

}

/* ===== search-field.js ===== */
{
/*
 * SearchField — mirrors SearchField.kt. Width 280, cornerRadius 100 (pill), leading search icon.
 * Kotlin default colors (defaultSearchFieldColors):
 *   container=fillTertiary, focused indicator=fillSecondary,
 *   text=labelPrimary, placeholder=labelQuaternary, search icon=labelQuaternary.
 */

class SuiSearchField extends SuiElement {
  static get observedAttributes() { return ["value", "placeholder", "disabled", "width", "container-color", "text-color", "placeholder-color", "focus-color", "icon-color"]; }
  render() {
    const disabled = this.bool("disabled");
    const width = this.num("width", 280);
    const containerC = this.attr("container-color", themeColor("fillTertiary"));
    const textC = this.attr("text-color", themeColor("labelPrimary"));
    const phC = this.attr("placeholder-color", themeColor("labelQuaternary"));
    const iconC = this.attr("icon-color", phC);
    const focusC = this.attr("focus-color", themeColor("fillSecondary"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .field { display:flex; align-items:center; gap:8px; width:${width}px; min-height:48px;
          background:${containerC}; border-radius:100px; border:1px solid transparent;
          padding:0 16px; transition:border-color .12s ease; }
        .field.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .field:focus-within { border-color:${focusC}; }
        .icon { color:${iconC}; display:inline-flex; }
        input { flex:1; background:transparent; border:none; outline:none; color:${textC};
          font-size:16px; line-height:20px; font-weight:500; font-family:inherit; padding:12px 0; }
        input::placeholder { color:${phC}; opacity:1; }
        .clear { cursor:pointer; color:${phC}; padding:4px; background:transparent; border:none; font-size:14px; }
      </style>
      <div class="field ${disabled ? "sui-disabled" : ""}">
        <span class="icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/>
            <path d="M20 20l-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </span>
        <input placeholder="${this.attr("placeholder", "Search")}" ${disabled ? "disabled" : ""}>
        <button class="clear">✕</button>
      </div>`;
    const input = this.shadowRoot.querySelector("input");
    input.value = this.attr("value", "");
    input.addEventListener("input", () => emit(this, "value-change", { value: input.value }));
    this.shadowRoot.querySelector(".clear").addEventListener("click", () => {
      input.value = ""; emit(this, "value-change", { value: "" }); input.focus();
    });
  }
}
define("sui-search-field", SuiSearchField);

}

/* ===== number-field.js ===== */
{
/*
 * NumberField — mirrors NumberField.kt.
 * Default height 40, width 152 (min 100 / small 80).
 * Kotlin default colors (defaultNumberFieldColors):
 *   container=fillTertiary, focused=fillSecondary, text=labelPrimary,
 *   error=error, +/- btn container=fillLight, content=inherited (labelPrimary).
 */

class SuiNumberField extends SuiElement {
  static get observedAttributes() { return ["value", "min", "max", "step", "size", "disabled", "width", "error", "container-color", "text-color", "focus-color", "button-color"]; }
  attributeChangedCallback(name) {
    if (name === "value" && this._internalWrite) return;
    super.attributeChangedCallback(name);
  }
  render() {
    const disabled = this.bool("disabled");
    const small = this.attr("size", "default").toLowerCase() === "small";
    const h = small ? 32 : 40;
    const width = this.num("width", 152);
    const min = this.num("min", -Infinity), max = this.num("max", Infinity), step = this.num("step", 1);
    const isError = this.bool("error");
    // `value` is the single source of truth: re-sync on every render so an
    // external (controlled) update is reflected, keeping the last committed
    // value when the attribute is absent.
    this._value = this.hasAttribute("value") ? this.num("value", 0) : (this._value ?? 0);
    const clamp = (v) => Math.max(min, Math.min(max, v));
    const containerC = this.attr("container-color", themeColor("fillTertiary"));
    const textC = this.attr("text-color", themeColor("labelPrimary"));
    const focusC = isError ? themeColor("error") : this.attr("focus-color", themeColor("fillSecondary"));
    const btnBg = this.attr("button-color", themeColor("fillLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .field { display:flex; align-items:center; width:${width}px; height:${h}px; padding:4px;
          background:${containerC}; border-radius:10px; box-sizing:border-box;
          border:1px solid transparent; transition:border-color .12s ease; caret-color:${themeColor("fillPrimary")}; }
        .field:focus-within { border-color:${focusC}; }
        .field.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn { width:44px; height:${h - 8}px; border:none; background:transparent; cursor:pointer;
          color:${textC}; font-size:20px; line-height:1; border-radius:8px;
          display:inline-flex; align-items:center; justify-content:center; transition:background-color .12s; }
        .btn:hover { background:${btnBg}; }
        .val { flex:1; text-align:center; background:transparent; border:none; outline:none;
          color:${textC}; font-size:16px; font-weight:500; font-family:inherit; width:100%; }
      </style>
      <div class="field ${disabled ? "sui-disabled" : ""}">
        <button class="btn dec">−</button>
        <input class="val" inputmode="numeric" value="${this._value}">
        <button class="btn inc">+</button>
      </div>`;
    const input = this.shadowRoot.querySelector(".val");
    const update = (v) => { this._value = clamp(v); input.value = this._value; this._internalWrite = true; this.setAttribute("value", String(this._value)); this._internalWrite = false; emit(this, "value-change", { value: this._value }); };
    this.shadowRoot.querySelector(".dec").addEventListener("click", () => update(this._value - step));
    this.shadowRoot.querySelector(".inc").addEventListener("click", () => update(this._value + step));
    input.addEventListener("change", () => update(parseFloat(input.value) || 0));
  }
}
define("sui-number-field", SuiNumberField);

}

/* ===== stepper.js ===== */
{
/*
 * Stepper — mirrors Stepper.kt. Height 40, width 152 (min 115), r=10.
 * Kotlin default colors: container=fillTertiary, value text=labelPrimary,
 *                        +/- button content=fillLight, container=transparent.
 */

class SuiStepper extends SuiElement {
  static get observedAttributes() { return ["value", "step", "editable", "decreasable", "increasable", "disabled", "container-color", "text-color", "button-color"]; }
  attributeChangedCallback(name) {
    if (name === "value" && this._internalWrite) return;
    super.attributeChangedCallback(name);
  }
  render() {
    const disabled = this.bool("disabled");
    const editable = this.bool("editable");
    const step = this.num("step", 1);
    const decreasable = this.getAttribute("decreasable") !== "false";
    const increasable = this.getAttribute("increasable") !== "false";
    // `value` is the single source of truth: re-sync on every render so an
    // external (controlled) update is reflected, keeping the last committed
    // value when the attribute is absent.
    this._value = this.hasAttribute("value") ? this.attr("value", "0") : (this._value ?? "0");
    const containerC = this.attr("container-color", themeColor("fillTertiary"));
    const textC = this.attr("text-color", themeColor("labelPrimary"));
    const btnC = this.attr("button-color", themeColor("fillLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .row { display:flex; align-items:center; min-width:152px; height:40px; padding:4px;
          background:${containerC}; border-radius:10px; box-sizing:border-box; caret-color:${themeColor("fillPrimary")}; }
        .row.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn { width:44px; height:32px; border:none; background:transparent; border-radius:8px;
          color:${btnC}; font-size:20px; cursor:pointer; display:inline-flex;
          align-items:center; justify-content:center; transition:background-color .12s; }
        .btn:hover:not(:disabled) { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .btn:disabled { opacity:.4; cursor:default; }
        .val { flex:1; text-align:center; background:transparent; border:none; outline:none;
          color:${textC}; font-size:16px; line-height:20px; font-weight:400;
          font-family:inherit; width:100%; padding:0 4px; }
      </style>
      <div class="row ${disabled ? "sui-disabled" : ""}">
        <button class="btn dec" ${decreasable ? "" : "disabled"}>−</button>
        <input class="val" ${editable ? "" : "readonly"} value="${this._value}">
        <button class="btn inc" ${increasable ? "" : "disabled"}>+</button>
      </div>`;
    const input = this.shadowRoot.querySelector(".val");
    const onStep = (dir) => { emit(this, "step", { step: dir * step }); };
    this.shadowRoot.querySelector(".dec").addEventListener("click", () => onStep(-1));
    this.shadowRoot.querySelector(".inc").addEventListener("click", () => onStep(1));
    input.addEventListener("change", () => { this._value = input.value; this._internalWrite = true; this.setAttribute("value", String(this._value)); this._internalWrite = false; emit(this, "value-change", { value: input.value }); });
  }
}
define("sui-stepper", SuiStepper);

}

/* ===== link.js ===== */
{
/*
 * Link — mirrors Link.kt. Text-like button, content defaults to interaction color.
 * Sizes Regular minHeight 24 / Max 32; optional trailing icon.
 */

class SuiLink extends SuiElement {
  static get observedAttributes() { return ["size", "disabled", "text", "color"]; }
  render() {
    const disabled = this.bool("disabled");
    const max = this.attr("size", "regular").toLowerCase() === "max";
    const color = this.attr("color", themeColor("interaction"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .link { display:inline-flex; align-items:center; gap:2px; min-height:${max ? 32 : 24}px;
          color:${color}; font-size:${max ? 16 : 14}px; line-height:${max ? 20 : 18}px; font-weight:600;
          font-family:inherit; cursor:pointer; user-select:none; background:none; border:none; padding:0; }
        .link.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .link:hover { text-decoration:underline; }
      </style>
      <button class="link ${disabled ? "sui-disabled" : ""}"><slot>${this.attr("text", "Link")}</slot><slot name="trailing"></slot></button>`;
    this.shadowRoot.querySelector(".link").addEventListener("click", () => {
      if (!disabled) emit(this, "click-action", {});
    });
  }
}
define("sui-link", SuiLink);

}

/* ===== list-item.js ===== */
{
/*
 * ListItem — mirrors ListItem.kt.
 * MinHeight 60, MinWidth 360, shape r=16, bg=fillLight.
 * Kotlin default colors (defaultListItemColors):
 *   container=fillLight, headline=labelPrimary, supporting=labelTertiary,
 *   leading/trailing=Unspecified (inherits content color -> labelPrimary).
 */

class SuiListItem extends SuiElement {
  static get observedAttributes() { return ["headline", "supporting", "leading-icon", "trailing-icon", "disabled", "container-color", "headline-color", "supporting-color"]; }
  render() {
    const disabled = this.bool("disabled");
    const leading = this.attr("leading-icon");
    const trailing = this.attr("trailing-icon");
    const supporting = this.attr("supporting");
    const bg = this.attr("container-color", themeColor("fillLight"));
    const headC = this.attr("headline-color", themeColor("labelPrimary"));
    const supC = this.attr("supporting-color", themeColor("labelTertiary"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:flex; }
        .item { display:flex; align-items:center; min-height:60px; min-width:360px; width:100%;
          padding:16px 4px 16px 16px; border-radius:${Dimension.RadiusLarge}px; background:${bg};
          cursor:pointer; box-sizing:border-box; transition:background-color .12s ease;
          color:${headC}; position:relative; overflow:hidden; }
        .item.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .item::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .item:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .lead { margin-right:12px; display:inline-flex; align-items:center; font-size:22px; }
        .text { flex:1; min-width:0; position:relative; z-index:1; }
        .headline { color:${headC}; font-size:16px; line-height:20px; font-weight:600; }
        .support { color:${supC}; font-size:14px; line-height:18px; font-weight:500; margin-top:4px; }
        .trail { margin-left:16px; margin-right:8px; display:inline-flex; align-items:center; color:${supC}; position:relative; z-index:1; }
      </style>
      <div class="item ${disabled ? "sui-disabled" : ""}">
        ${leading ? `<span class="lead">${leading}</span>` : ""}
        <div class="text">
          <div class="headline"><slot name="headline">${this.attr("headline", "Headline")}</slot></div>
          ${supporting ? `<div class="support">${supporting}</div>` : ""}
        </div>
        ${trailing ? `<span class="trail">${trailing}</span>` : `<slot name="trailing"></slot>`}
      </div>`;
    this.shadowRoot.querySelector(".item").addEventListener("click", () => {
      if (!disabled) emit(this, "click-action", {});
    });
  }
}
define("sui-list-item", SuiListItem);

}

/* ===== page-control.js ===== */
{
/*
 * PageControl — mirrors PageControl.kt. Dot radius 4, dot space 12, vertical padding 8.
 * Kotlin default colors (defaultPageControlColors):
 *   selected dot   = labelPrimaryLight
 *   unselected dot = fillSecondary
 */

class SuiPageControl extends SuiElement {
  static get observedAttributes() { return ["count", "index", "disabled", "selected-color", "unselected-color"]; }
  render() {
    const count = this.num("count", 5);
    const index = this.num("index", 0);
    const disabled = this.bool("disabled");
    const r = 4, space = 12, dot = r * 2;
    const activeC = this.attr("selected-color", themeColor("labelPrimaryLight"));
    const inactiveC = this.attr("unselected-color", themeColor("fillSecondary"));
    let dots = "";
    for (let i = 0; i < count; i++) {
      const active = i === index;
      dots += `<div class="dot ${active ? "active" : ""}" data-i="${i}"></div>`;
    }
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .bar { display:inline-flex; align-items:center; gap:${space}px; padding:8px 0; }
        .bar.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .dot { width:${dot}px; height:${dot}px; border-radius:${r}px; background:${inactiveC};
          cursor:pointer; transition:width .2s ease, background-color .2s ease; }
        .dot.active { width:${dot * 3}px; background:${activeC}; }
      </style>
      <div class="bar ${disabled ? "sui-disabled" : ""}">${dots}</div>`;
    this.shadowRoot.querySelectorAll(".dot").forEach((d) => {
      d.addEventListener("click", () => {
        if (disabled) return;
        this.setAttribute("index", d.dataset.i);
        emit(this, "select", { index: +d.dataset.i });
      });
    });
  }
}
define("sui-page-control", SuiPageControl);

}

/* ===== option.js ===== */
{
/*
 * Option — mirrors Option.kt. MinWidth 120, MinHeight 48, gap 4.
 * Kotlin default colors (defaultOptionColors):
 *   checked:   bg=fillSecondary, content=labelPrimary
 *   unchecked: bg=fillTertiary,  content=labelPrimary
 */

class SuiOption extends SuiElement {
  static get observedAttributes() { return ["checked", "disabled", "label", "icon", "checked-container-color", "container-color", "content-color"]; }
  render() {
    const checked = this.bool("checked");
    const disabled = this.bool("disabled");
    const icon = this.attr("icon");
    const defaultBg = checked ? themeColor("fillSecondary") : themeColor("fillTertiary");
    const defaultFg = themeColor("labelPrimary");
    const bg = checked
      ? this.attr("checked-container-color", this.attr("container-color", defaultBg))
      : this.attr("container-color", defaultBg);
    const fg = this.attr("content-color", defaultFg);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .opt { display:inline-flex; flex-direction:column; align-items:center; justify-content:center; gap:4px;
          min-width:120px; min-height:48px; padding:8px 12px; border-radius:${Dimension.RadiusLarge}px;
          background:${bg}; color:${fg}; cursor:pointer; user-select:none; box-sizing:border-box;
          position:relative; overflow:hidden; transition:background-color .12s ease; }
        .opt.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .opt::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .opt:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .icon { font-size:22px; display:inline-flex; position:relative; z-index:1; }
        .label { font-size:16px; line-height:20px; font-weight:600; font-family:inherit; position:relative; z-index:1; }
      </style>
      <div class="opt ${disabled ? "sui-disabled" : ""}" role="radio" aria-checked="${checked}">
        ${icon ? `<span class="icon">${icon}</span>` : ""}
        <span class="label"><slot>${this.attr("label", "Option")}</slot></span>
      </div>`;
    this.shadowRoot.querySelector(".opt").addEventListener("click", () => {
      if (disabled) return;
      this.toggleAttribute("checked", true);
      emit(this, "checked-change", { checked: true });
    });
  }
}
define("sui-option", SuiOption);

}

/* ===== side-navigation.js ===== */
{
/*
 * SideNavigation / SideNavigationItem — mirrors SideNavigation.kt.
 * Item shape r=24 (RadiusHuge), content padding 8, leading/trailing size 32, gap 8.
 * Kotlin default colors (defaultSideNavigationItemColors):
 *   header title         = labelSecondary
 *   section label        = labelQuaternary
 *   unselected item:     container=transparent, content=labelPrimary
 *   selected item:       container=fillSecondary, content=labelPrimary
 */

class SuiSideNavigation extends SuiElement {
  static get observedAttributes() { return ["items", "selected-index", "header", "header-color", "selected-container-color", "content-color"]; }
  render() {
    const items = (this.attr("items", "") || "").split(",").map((s) => s.trim()).filter(Boolean);
    const sel = this.num("selected-index", 0);
    const header = this.attr("header");
    const headerC = this.attr("header-color", themeColor("labelSecondary"));
    const contentC = this.attr("content-color", themeColor("labelPrimary"));
    const selBg = this.attr("selected-container-color", themeColor("fillSecondary"));
    const hoverBg = themeColor("fillLight");
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .nav { display:flex; flex-direction:column; gap:4px; min-width:200px; }
        .header { padding:8px 12px; font-size:20px; line-height:26px; font-weight:700;
          color:${headerC}; }
        .item { display:flex; align-items:center; gap:8px; padding:8px; border-radius:${Dimension.RadiusHuge}px;
          color:${contentC}; font-size:16px; line-height:20px; font-weight:600; font-family:inherit;
          cursor:pointer; user-select:none; background:transparent; transition:background-color .12s ease;
          border: none; width: 100%; text-align: left; position:relative; overflow:hidden; }
        .item::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; border-radius:inherit; }
        .item:hover::after { background: ${hoverBg}; }
        .item.active { background:${selBg}; color:${contentC}; }
        .item.active::after { background: transparent; }
        .dot { width:32px; height:32px; border-radius:50%; background:${themeColor("fillTertiary")};
          display:inline-flex; align-items:center; justify-content:center; font-size:16px; flex:0 0 auto; position:relative; z-index:1; }
        .item > span:last-child { position:relative; z-index:1; }
        .item.active .dot { background:${themeColor("fillLight")}; }
      </style>
      <div class="nav">
        ${header ? `<div class="header">${header}</div>` : ""}
        ${items.map((label, i) => `
          <button class="item ${i === sel ? "active" : ""}" data-i="${i}">
            <span class="dot">${label.charAt(0)}</span><span>${label}</span>
          </button>`).join("")}
      </div>`;
    this.shadowRoot.querySelectorAll(".item").forEach((it) => {
      it.addEventListener("click", () => {
        const i = +it.dataset.i;
        this.setAttribute("selected-index", String(i));
        emit(this, "select", { index: i, value: items[i] });
      });
    });
  }
}
define("sui-side-navigation", SuiSideNavigation);

}

/* ===== title-bar.js ===== */
{
/*
 * TitleBar — mirrors TitleBar.kt. Height 96, horizontal padding 24, actions gap 8.
 * Kotlin default colors (defaultTitleBarColors):
 *   title=labelSecondary, leading/trailing actions=labelPrimary. Container is transparent.
 */

class SuiTitleBar extends SuiElement {
  static get observedAttributes() { return ["title", "width", "title-color", "action-color"]; }
  render() {
    const width = this.num("width", 480);
    const titleC = this.attr("title-color", themeColor("labelSecondary"));
    const actionC = this.attr("action-color", themeColor("labelPrimary"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:flex; }
        .bar { display:flex; align-items:center; gap:8px; min-height:96px; width:${width}px;
          padding:0 24px; box-sizing:border-box; }
        .lead { display:inline-flex; align-items:center; gap:8px; color:${actionC}; }
        .title { flex:1; font-size:20px; line-height:26px; font-weight:600; font-family:inherit;
          color:${titleC}; padding:0 16px; }
        .trail { display:inline-flex; align-items:center; gap:8px; color:${actionC}; }
      </style>
      <div class="bar">
        <span class="lead"><slot name="leading"></slot></span>
        <span class="title"><slot name="title">${this.attr("title", "Title")}</slot></span>
        <span class="trail"><slot name="trailing"></slot></span>
      </div>`;
  }
}
define("sui-title-bar", SuiTitleBar);

}

/* ===== scroll-indicator.js ===== */
{
/*
 * ScrollIndicator — mirrors ScrollIndicator.kt.
 * Kotlin default colors (defaultScrollIndicatorColors):
 *   track=labelQuaternary (alpha 0.2 normal / 0.9 hover),
 *   thumb=labelPrimary (alpha 0.5 normal / 1.0 hover),
 *   hot-area background=fillLight (alpha 0 normal / 1 hover).
 */

class SuiScrollIndicator extends SuiElement {
  static get observedAttributes() { return ["orientation", "fraction", "thumb-fraction", "length", "track-color", "thumb-color"]; }
  render() {
    const vertical = this.attr("orientation", "vertical") === "vertical";
    const length = this.num("length", 200);
    const thumbFrac = Math.max(0.05, Math.min(1, this.num("thumb-fraction", 0.3)));
    const frac = Math.max(0, Math.min(1, this.num("fraction", 0)));
    const thick = 4;
    const thumbLen = length * thumbFrac;
    const pos = (length - thumbLen) * frac;
    const trackC = this.attr("track-color", themeColor("labelQuaternary"));
    const thumbC = this.attr("thumb-color", themeColor("labelPrimary"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .wrap { position:relative; border-radius:${thick / 2}px; padding:2px; transition:background-color .12s ease;
          ${vertical ? `width:${thick + 4}px; height:${length}px;` : `height:${thick + 4}px; width:${length}px;`} }
        .wrap:hover { background:${themeColor("fillLight")}; }
        .track { position:relative; border-radius:${thick / 2}px; background:${trackC}; opacity:.2; transition:opacity .12s ease;
          ${vertical ? `width:${thick}px; height:${length}px;` : `height:${thick}px; width:${length}px;`} }
        .wrap:hover .track { opacity:.9; }
        .thumb { position:absolute; border-radius:${thick / 2}px; background:${thumbC}; opacity:.5; transition:opacity .12s ease;
          ${vertical ? `width:${thick}px; height:${thumbLen}px; top:${pos}px;` : `height:${thick}px; width:${thumbLen}px; left:${pos}px;`} }
        .wrap:hover .thumb { opacity:1; }
      </style>
      <div class="wrap">
        <div class="track"><div class="thumb"></div></div>
      </div>`;
  }
}
define("sui-scroll-indicator", SuiScrollIndicator);

}

/* ===== wheel-picker.js ===== */
{
/*
 * WheelPicker / Timepicker — mirrors Timepicker.kt & WheelPickerDefaults.
 * Item height 40, indicator shape r=12, indicator bg=fillSecondary.
 * selected text=labelPrimary, unselected text=labelTertiary. Timepicker width 416, gap 16.
 */

const ITEM_H = 40;
const VISIBLE = 5;

class SuiWheelPicker extends SuiElement {
  static get observedAttributes() { return ["items", "index", "width", "disabled"]; }
  render() {
    const items = (this.attr("items", "") || "").split(",").map((s) => s.trim()).filter(Boolean);
    const width = this.num("width", 120);
    const disabled = this.bool("disabled");
    const idx = this.num("index", 0);
    const listH = ITEM_H * VISIBLE;
    const padCount = (VISIBLE - 1) / 2;
    const pads = Array.from({ length: padCount }, () => `<div class="item pad"></div>`).join("");
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .wheel { position:relative; width:${width}px; height:${listH}px; overflow:hidden;
          -webkit-mask-image:linear-gradient(transparent, rgba(0,0,0,.5) 14%, #000 44%, #000 56%, rgba(0,0,0,.5) 86%, transparent);
          mask-image:linear-gradient(transparent, rgba(0,0,0,.5) 14%, #000 44%, #000 56%, rgba(0,0,0,.5) 86%, transparent); }
        .wheel.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .band { position:absolute; left:0; right:0; top:${padCount * ITEM_H}px; height:${ITEM_H}px;
          border-radius:${Dimension.RadiusMediumLarge}px; background:${themeColor("fillSecondary")}; pointer-events:none; }
        .scroll { position:absolute; inset:0; overflow-y:scroll; scroll-snap-type:y mandatory;
          scrollbar-width:none; }
        .scroll::-webkit-scrollbar { display:none; }
        .item { height:${ITEM_H}px; display:flex; align-items:center; justify-content:center;
          scroll-snap-align:center; font-size:16px; font-weight:500; font-family:inherit;
          color:${themeColor("labelTertiary")}; transition:color .1s ease; }
        .item.sel { color:${themeColor("labelPrimary")}; font-weight:600; }
        .pad { scroll-snap-align:none; }
      </style>
      <div class="wheel ${disabled ? "sui-disabled" : ""}">
        <div class="band"></div>
        <div class="scroll">
          ${pads}
          ${items.map((t, i) => `<div class="item ${i === idx ? "sel" : ""}" data-i="${i}">${t}</div>`).join("")}
          ${pads}
        </div>
      </div>`;
    const scroll = this.shadowRoot.querySelector(".scroll");
    const itemsEls = this.shadowRoot.querySelectorAll(".item[data-i]");
    scroll.scrollTop = idx * ITEM_H;
    let raf;
    scroll.addEventListener("scroll", () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const i = Math.round(scroll.scrollTop / ITEM_H);
        itemsEls.forEach((el) => el.classList.toggle("sel", +el.dataset.i === i));
        if (i !== +(this.getAttribute("index") || -1)) {
          this.setAttribute("index", String(i));
          emit(this, "select", { index: i, value: items[i] });
        }
      });
    });
  }
}
define("sui-wheel-picker", SuiWheelPicker);

class SuiTimepicker extends SuiElement {
  static get observedAttributes() { return ["hour", "minute", "second", "seconds"]; }
  render() {
    const showSeconds = this.getAttribute("seconds") !== "false";
    const pad2 = (n) => String(n).padStart(2, "0");
    const hours = Array.from({ length: 24 }, (_, i) => pad2(i)).join(",");
    const mins = Array.from({ length: 60 }, (_, i) => pad2(i)).join(",");
    const h = this.num("hour", 0), m = this.num("minute", 0), s = this.num("second", 0);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .tp { display:inline-flex; align-items:center; gap:16px; width:416px; justify-content:center; }
        .colon { color:${themeColor("labelPrimary")}; font-size:20px; font-weight:600; }
      </style>
      <div class="tp">
        <sui-wheel-picker items="${hours}" index="${h}" width="96"></sui-wheel-picker>
        <span class="colon">:</span>
        <sui-wheel-picker items="${mins}" index="${m}" width="96"></sui-wheel-picker>
        ${showSeconds ? `<span class="colon">:</span>
        <sui-wheel-picker items="${mins}" index="${s}" width="96"></sui-wheel-picker>` : ""}
      </div>`;
  }
}
define("sui-timepicker", SuiTimepicker);

}

/* ===== date-picker.js ===== */
{
/*
 * DatePicker — mirrors DatePicker.kt.
 * Width 416, date cell 32, header 32.
 * Kotlin default colors (defaultDatePickerColors):
 *   primary content/day text=labelPrimary,
 *   week header/inactive dates=labelQuaternary,
 *   selected-date bg=fillSecondary / text=labelPrimary,
 *   today bg=fillPrimary / text=labelPrimaryLight,
 *   date-range in-between bg=fillLight,
 *   nav buttons container=transparent / content=labelPrimary.
 */

const WEEKDAYS = ["S", "M", "T", "W", "T", "F", "S"];
const MONTHS = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

class SuiDatePicker extends SuiElement {
  static get observedAttributes() { return ["year", "month", "selected"]; }
  render() {
    const today = new Date();
    let year = this.num("year", today.getFullYear());
    let month = this.num("month", today.getMonth());
    const selected = this.attr("selected");
    const first = new Date(year, month, 1);
    const startDay = first.getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const cells = [];
    for (let i = 0; i < startDay; i++) cells.push(null);
    for (let d = 1; d <= daysInMonth; d++) cells.push(d);
    const isToday = (d) => d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
    const isSelected = (d) => selected === `${year}-${month}-${d}`;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .cal { width:416px; padding:16px; box-sizing:border-box; color:${themeColor("labelPrimary")}; }
        .head { display:flex; align-items:center; justify-content:space-between; height:32px; margin-bottom:16px; }
        .title { font-size:20px; line-height:26px; font-weight:700; }
        .nav { background:none; border:none; color:${themeColor("labelPrimary")}; font-size:20px; cursor:pointer;
          width:32px; height:32px; border-radius:50%; transition:background-color .12s; display:inline-flex;
          align-items:center; justify-content:center; padding:0; }
        .nav:hover { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .grid { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; }
        .wk { text-align:center; font-size:12px; font-weight:600; color:${themeColor("labelQuaternary")}; height:32px; line-height:32px; }
        .cell { height:32px; display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:500;
          border-radius:50%; cursor:pointer; color:${themeColor("labelPrimary")}; transition:background-color .12s; position:relative; }
        .cell::after { content:""; position:absolute; inset:0; background:transparent; border-radius:50%; transition:background-color .12s; pointer-events:none; }
        .cell:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .cell.today { background:${themeColor("fillPrimary")}; color:${themeColor("labelPrimaryLight")}; }
        .cell.today::after { background:transparent; }
        .cell.selected { background:${themeColor("fillSecondary")}; color:${themeColor("labelPrimary")}; }
        .cell.selected::after { background:transparent; }
        .empty { visibility:hidden; }
      </style>
      <div class="cal">
        <div class="head">
          <button class="nav prev">‹</button>
          <span class="title">${MONTHS[month]} ${year}</span>
          <button class="nav next">›</button>
        </div>
        <div class="grid">
          ${WEEKDAYS.map((w) => `<div class="wk">${w}</div>`).join("")}
          ${cells.map((d) => d == null
            ? `<div class="cell empty"></div>`
            : `<div class="cell ${isSelected(d) ? "selected" : isToday(d) ? "today" : ""}" data-d="${d}">${d}</div>`).join("")}
        </div>
      </div>`;
    this.shadowRoot.querySelector(".prev").addEventListener("click", () => {
      if (month === 0) { this.setAttribute("year", year - 1); this.setAttribute("month", 11); }
      else this.setAttribute("month", month - 1);
    });
    this.shadowRoot.querySelector(".next").addEventListener("click", () => {
      if (month === 11) { this.setAttribute("year", year + 1); this.setAttribute("month", 0); }
      else this.setAttribute("month", month + 1);
    });
    this.shadowRoot.querySelectorAll(".cell[data-d]").forEach((c) => {
      c.addEventListener("click", () => {
        const d = +c.dataset.d;
        this.setAttribute("selected", `${year}-${month}-${d}`);
        emit(this, "date-select", { year, month, day: d });
      });
    });
  }
}
define("sui-date-picker", SuiDatePicker);

}

/* ===== augment.js ===== */
{
/* Augment — a window-attached ornament matching SpatialUI foundation Augment. */

class SuiAugment extends SuiOverlayElement {
  static get observedAttributes() {
    return [
      "for", "anchor", "alignment", "offset-x", "offset-y", "offset-z",
      "rotation-x", "rotation-y", "rotation-z", "corner-radius",
      "enable-material-background", "focusable", "size-behavior", "window-size-behavior",
      "clipping-enabled", "viewport-padding", "hidden",
    ];
  }

  render() {
    const materialEnabled = !this.hasAttribute("enable-material-background")
      || this.bool("enable-material-background");
    const focusable = !this.hasAttribute("focusable") || this.bool("focusable");
    const radius = Math.max(0, this.num("corner-radius", Dimension.RadiusLarge));
    const alignment = parseNormalizedPoint(this.attr("alignment", "bottom-center"));
    this.style.setProperty("--sui-overlay-origin-x", alignment.x * 100 + "%");
    this.style.setProperty("--sui-overlay-origin-y", alignment.y * 100 + "%");
    this.shadowRoot.innerHTML = [
      "<style>",
      overlayCss,
      ".surface{width:max-content;height:max-content;max-width:none;max-height:none;",
      "border-radius:", radius, "px;}</style>",
      '<div class="surface ', materialEnabled ? "material-regular" : "material-none", '" ',
      'part="surface" role="region" ', focusable ? 'tabindex="-1"' : "inert", ">",
      "<slot></slot></div>",
    ].join("");
  }

  prepareSurface(anchor, surface) {
    const behavior = this.attr(
      "window-size-behavior",
      this.attr("size-behavior", "adaptive"),
    ).toLowerCase();
    const rect = anchor.getBoundingClientRect();
    surface.style.width = behavior === "match-container-width" ? rect.width + "px" : "max-content";
    surface.style.height = behavior === "match-container-height" ? rect.height + "px" : "max-content";
  }

  calculatePosition(anchorRect, contentSize) {
    return computeAugmentPosition(
      anchorRect,
      contentSize,
      parseNormalizedPoint(this.attr("anchor", "top-front"), "top-front"),
      parseNormalizedPoint(this.attr("alignment", "bottom-center"), "bottom-center"),
      this.offset(),
    );
  }
}

define("sui-augment", SuiAugment);

}

/* ===== spatial-popup.js ===== */
{
/* SpatialPopup — an anchor-relative, dismissible floating spatial surface. */

class SuiSpatialPopup extends SuiOverlayElement {
  static get observedAttributes() {
    return [
      "for", "horizontal-placement", "vertical-placement", "offset-x",
      "offset-y", "offset-z", "rotation-x", "rotation-y", "rotation-z",
      "corner-radius", "default-min-width", "default-min-height",
      "disable-material-background", "focusable", "dismiss-on-click-outside",
      "dismiss-on-escape", "clipping-enabled", "viewport-padding", "hidden",
    ];
  }

  render() {
    const materialDisabled = this.bool("disable-material-background");
    const focusable = !this.hasAttribute("focusable") || this.bool("focusable");
    const radius = Math.max(0, this.num("corner-radius", Dimension.RadiusExtraLarge));
    const minWidth = Math.max(0, this.num("default-min-width", Dimension.WidthMedium));
    const minHeight = Math.max(0, this.num("default-min-height", Dimension.HeightMin));
    this.shadowRoot.innerHTML = [
      "<style>",
      overlayCss,
      ".surface{min-width:", minWidth, "px;min-height:", minHeight,
      "px;width:max-content;height:max-content;max-width:none;max-height:none;border-radius:",
      radius, "px;}</style>",
      '<div class="surface ', materialDisabled ? "material-none" : "material-thick", '" ',
      'part="surface" role="dialog" aria-modal="false" ',
      focusable ? 'tabindex="-1"' : "inert", "><slot></slot></div>",
    ].join("");
  }

  shouldDismissOnOutsidePointer() {
    return !this.hasAttribute("dismiss-on-click-outside")
      || this.bool("dismiss-on-click-outside");
  }

  shouldDismissOnEscape() {
    return !this.hasAttribute("dismiss-on-escape") || this.bool("dismiss-on-escape");
  }

  calculatePosition(anchorRect, contentSize, anchor) {
    const direction = getComputedStyle(anchor).direction === "rtl" ? "rtl" : "ltr";
    return computePopupPosition(
      anchorRect,
      contentSize,
      this.attr("horizontal-placement", "align-start").toLowerCase(),
      this.attr("vertical-placement", "above").toLowerCase(),
      this.offset(Dimension.GapSmall),
      direction,
    );
  }
}

define("sui-spatial-popup", SuiSpatialPopup);

}

/* ===== api-aliases.js ===== */
{
/* Explicit Custom Element names for Kotlin composables represented by shared Web components. */

class SuiAliasElement extends SuiElement {
  static targetTag = "div";
  static forcedAttributes = {};
  static get observedAttributes() { return ["checked", "state", "disabled", "label", "size", "value", "placeholder", "width", "color", "thickness"]; }

  render() {
    const target = document.createElement(this.constructor.targetTag);
    for (const attribute of this.attributes) {
      if (attribute.name !== "style" && attribute.name !== "class") {
        target.setAttribute(attribute.name, attribute.value);
      }
    }
    for (const [name, value] of Object.entries(this.constructor.forcedAttributes)) {
      target.setAttribute(name, value);
    }
    target.innerHTML = "<slot></slot>";
    this.shadowRoot.innerHTML = "<style>:host{display:inline-flex}</style>";
    this.shadowRoot.append(target);
  }
}

class SuiTriStateCheckbox extends SuiAliasElement { static targetTag = "sui-checkbox"; }
class SuiButtonChip extends SuiAliasElement { static targetTag = "sui-chip"; }
class SuiToggleableChip extends SuiAliasElement {
  static targetTag = "sui-chip";
  static forcedAttributes = { toggle: "" };
}
class SuiRemovableChip extends SuiAliasElement {
  static targetTag = "sui-chip";
  static forcedAttributes = { removable: "" };
}
class SuiTextArea extends SuiAliasElement {
  static targetTag = "sui-text-field";
  static forcedAttributes = { multiline: "" };
}
class SuiHorizontalDivider extends SuiAliasElement {
  static targetTag = "sui-divider";
  static forcedAttributes = { orientation: "horizontal" };
}
class SuiVerticalDivider extends SuiAliasElement {
  static targetTag = "sui-divider";
  static forcedAttributes = { orientation: "vertical" };
}

define("sui-tri-state-checkbox", SuiTriStateCheckbox);
define("sui-button-chip", SuiButtonChip);
define("sui-toggleable-chip", SuiToggleableChip);
define("sui-removable-chip", SuiRemovableChip);
define("sui-text-area", SuiTextArea);
define("sui-horizontal-divider", SuiHorizontalDivider);
define("sui-vertical-divider", SuiVerticalDivider);

}

/* ===== advanced-controls.js ===== */
{
/* Missing public SpatialUI control variants. */

function copyAttributes(from, to, excluded = []) {
  for (const attribute of from.attributes) {
    if (!excluded.includes(attribute.name)) to.setAttribute(attribute.name, attribute.value);
  }
}

class SuiControlProxy extends SuiElement {
  renderProxy(tagName, forced = {}, excluded = []) {
    const target = document.createElement(tagName);
    copyAttributes(this, target, excluded);
    for (const [name, value] of Object.entries(forced)) target.setAttribute(name, value);
    target.innerHTML = "<slot></slot>";
    this.shadowRoot.innerHTML = "<style>:host{display:inline-flex}</style>";
    this.shadowRoot.append(target);
    return target;
  }
}

class SuiToggleIconButton extends SuiControlProxy {
  static get observedAttributes() { return ["checked", "disabled", "size", "icon"]; }
  render() {
    const target = this.renderProxy("sui-icon-button", { toggle: "" }, ["checked"]);
    target.toggleAttribute("selected", this.bool("checked"));
    target.addEventListener("checked-change", (event) => {
      event.stopPropagation();
      const checked = Boolean(event.detail.selected);
      this.toggleAttribute("checked", checked);
      emit(this, "checked-change", { checked });
    });
  }
}
define("sui-toggle-icon-button", SuiToggleIconButton);

class SuiSymbolSlider extends SuiControlProxy {
  static get observedAttributes() { return ["value", "min", "max", "size", "width", "disabled", "icon"]; }
  render() {
    const icon = this.attr("icon", "♪");
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.wrap{display:flex;align-items:center;position:relative}",
      ".symbol{position:absolute;left:12px;z-index:2;color:var(--sui-label-primary-light);pointer-events:none}</style>",
      '<div class="wrap"><span class="symbol">', escapeHtml(icon), "</span></div>",
    ].join("");
    const target = document.createElement("sui-slider");
    copyAttributes(this, target, ["icon"]);
    target.addEventListener("value-change", (event) => emit(this, "value-change", event.detail));
    this.shadowRoot.querySelector(".wrap").append(target);
  }
}
define("sui-symbol-slider", SuiSymbolSlider);

class SuiSegmentSlider extends SuiElement {
  static get observedAttributes() { return ["step", "segment-count", "size", "width", "disabled"]; }
  render() {
    const count = Math.max(1, Math.round(this.num("segment-count", 4)));
    const step = Math.min(count, Math.max(0, Math.round(this.num("step", 0))));
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.wrap{position:relative}.ticks{position:absolute;inset:0 16px;pointer-events:none}",
      ".ticks i{position:absolute;top:50%;width:2px;height:6px;border-radius:2px;background:var(--sui-label-primary-light);",
      "transform:translate(-50%,-50%);opacity:.55}</style><div class=\"wrap\"><sui-slider min=\"0\" max=\"",
      count, "\" value=\"", step, "\"></sui-slider><div class=\"ticks\">",
      Array.from({ length: count + 1 }, (_, index) => '<i style="left:' + index / count * 100 + '%"></i>').join(""),
      "</div></div>",
    ].join("");
    const target = this.shadowRoot.querySelector("sui-slider");
    for (const name of ["size", "width", "disabled"]) {
      if (this.hasAttribute(name)) target.setAttribute(name, this.getAttribute(name));
    }
    target.addEventListener("value-change", (event) => {
      const next = Math.min(count, Math.max(0, Math.round(event.detail.value)));
      this.setAttribute("step", String(next));
      emit(this, "step-change", { step: next, segmentCount: count });
    });
  }
}
define("sui-segment-slider", SuiSegmentSlider);

const CIRCULAR_SIZE = { small: 20, regular: 30, max: 40 };
class SuiSymbolicCircularProgress extends SuiElement {
  static get observedAttributes() { return ["value", "size", "symbol", "track-color", "progress-color", "symbol-color"]; }
  render() {
    const size = CIRCULAR_SIZE[this.attr("size", "max").toLowerCase()] || 40;
    const stroke = Math.max(2, size * 0.1);
    const value = Math.max(0, Math.min(1, this.num("value", 0.6)));
    const radius = (size - stroke) / 2;
    const circumference = 2 * Math.PI * radius;
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-grid;place-items:center}.wrap{display:grid;place-items:center;position:relative}",
      "svg{grid-area:1/1;transform:rotate(-90deg)}.symbol{grid-area:1/1;color:",
      this.attr("symbol-color", themeColor("labelPrimary")), ";font-size:", size * 0.38,
      "px;line-height:1}</style><div class=\"wrap\"><svg width=\"", size, "\" height=\"", size,
      "\"><circle cx=\"", size / 2, "\" cy=\"", size / 2, "\" r=\"", radius,
      "\" fill=\"none\" stroke=\"", this.attr("track-color", themeColor("fillTertiary")),
      "\" stroke-width=\"", stroke, "\"/><circle cx=\"", size / 2, "\" cy=\"", size / 2,
      "\" r=\"", radius, "\" fill=\"none\" stroke=\"", this.attr("progress-color", themeColor("interaction")),
      "\" stroke-width=\"", stroke, "\" stroke-linecap=\"round\" stroke-dasharray=\"",
      circumference * value, " ", circumference, "\"/></svg><span class=\"symbol\"><slot>",
      escapeHtml(this.attr("symbol", "✓")), "</slot></span></div>",
    ].join("");
  }
}
define("sui-symbolic-circular-progress", SuiSymbolicCircularProgress);

class SuiProgressPageControl extends SuiElement {
  static get observedAttributes() { return ["count", "index", "progress", "disabled", "selected-color", "unselected-color"]; }
  render() {
    const count = Math.max(1, Math.round(this.num("count", 5)));
    const selected = Math.min(count - 1, Math.max(0, Math.round(this.num("index", 0))));
    const progress = Math.min(1, Math.max(0, this.num("progress", 0.5)));
    const disabled = this.bool("disabled");
    const active = this.attr("selected-color", themeColor("labelPrimaryLight"));
    const normal = this.attr("unselected-color", themeColor("fillSecondary"));
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.bar{display:flex;align-items:center;gap:12px;padding:8px 0}",
      ".bar.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}.dot{width:8px;height:8px;border:0;border-radius:8px;background:",
      normal, ";padding:0;cursor:pointer;overflow:hidden}.dot.active{width:24px}.fill{height:100%;border-radius:inherit;background:",
      active, "}</style><div class=\"bar ", disabled ? "disabled" : "", "\">",
      Array.from({ length: count }, (_, index) => '<button class="dot ' + (index === selected ? "active" : "") + '" data-index="' + index + '">' +
        (index === selected ? '<span class="fill" style="display:block;width:' + (50 + progress * 50) + '%"></span>' : "") + "</button>").join(""),
      "</div>",
    ].join("");
    this.shadowRoot.querySelectorAll(".dot").forEach((dot) => dot.addEventListener("click", () => {
      if (disabled) return;
      const index = Number(dot.dataset.index);
      this.setAttribute("index", String(index));
      emit(this, "select", { index });
    }));
  }
}
define("sui-progress-page-control", SuiProgressPageControl);

class SuiStereoImage extends SuiElement {
  static get observedAttributes() { return ["src", "alt", "texture-layout", "eye", "width", "height", "fit"]; }
  render() {
    const layout = this.attr("texture-layout", "none").toLowerCase();
    const eye = this.attr("eye", "left").toLowerCase();
    const width = this.attr("width", "320px");
    const height = this.attr("height", "180px");
    const sideBySide = layout === "side-by-side";
    const topAndBottom = layout === "top-and-bottom";
    const imageWidth = sideBySide ? "200%" : "100%";
    const imageHeight = topAndBottom ? "200%" : "100%";
    const x = sideBySide && eye === "right" ? "50%" : "0";
    const y = topAndBottom && eye === "right" ? "50%" : "0";
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex;width:", width, ";height:", height,
      ";overflow:hidden}img{width:", imageWidth, ";height:", imageHeight,
      ";max-width:none;max-height:none;object-fit:", this.attr("fit", "cover"),
      ";transform:translate(-", x, ",-", y, ")}</style><img src=\"", escapeHtml(this.attr("src", "")),
      "\" alt=\"", escapeHtml(this.attr("alt", "")), "\">",
    ].join("");
  }
}
define("sui-stereo-image", SuiStereoImage);

}

/* ===== composition-items.js ===== */
{
/* Web equivalents for public Compose scope/slot components. */

class SuiSegmentItem extends SuiElement {
  static get observedAttributes() { return ["selected", "disabled", "label", "value"]; }
  render() {
    const selected = this.bool("selected");
    const disabled = this.bool("disabled");
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.item{min-height:32px;padding:0 12px;border:0;border-radius:12px;",
      "background:", selected ? themeColor("fillSecondary") : "transparent", ";color:",
      selected ? themeColor("labelPrimary") : themeColor("labelTertiary"),
      ";font:600 16px/20px sans-serif;cursor:pointer}.item:hover{background:", themeColor("fillLight"),
      "}.item.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}</style>",
      '<button class="item ', disabled ? "disabled" : "", '" role="tab" aria-selected="', selected,
      '"><slot>', escapeHtml(this.attr("label", "Segment")), "</slot></button>",
    ].join("");
    this.shadowRoot.querySelector("button").addEventListener("click", () => {
      if (!disabled) emit(this, "select", { value: this.attr("value", this.attr("label", "")) });
    });
  }
}
define("sui-segment-item", SuiSegmentItem);

class SuiSideNavigationSection extends SuiElement {
  static get observedAttributes() { return ["label"]; }
  render() {
    this.shadowRoot.innerHTML = [
      "<style>:host{display:flex;flex-direction:column;gap:4px}.label{padding:8px 12px;color:",
      themeColor("labelQuaternary"), ";font:600 12px/16px sans-serif}</style>",
      '<div class="label">', escapeHtml(this.attr("label", "")), "</div><slot></slot>",
    ].join("");
  }
}
define("sui-side-navigation-section", SuiSideNavigationSection);

class SuiSideNavigationItem extends SuiElement {
  static get observedAttributes() { return ["selected", "disabled", "label", "leading-icon", "trailing-icon", "value"]; }
  render() {
    const selected = this.bool("selected");
    const disabled = this.bool("disabled");
    this.shadowRoot.innerHTML = [
      "<style>:host{display:block}.item{width:100%;min-height:48px;padding:8px;border:0;border-radius:24px;display:flex;align-items:center;gap:8px;",
      "background:", selected ? themeColor("fillSecondary") : "transparent", ";color:", themeColor("labelPrimary"),
      ";font:600 16px/20px sans-serif;text-align:start;cursor:pointer}.item:hover{background:", themeColor("fillLight"),
      "}.item.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}.leading,.trailing{width:32px;display:grid;place-items:center}.label{flex:1}</style>",
      '<button class="item ', disabled ? "disabled" : "", '" aria-current="', selected ? "page" : "false",
      '"><span class="leading"><slot name="leading">', escapeHtml(this.attr("leading-icon", "")),
      '</slot></span><span class="label"><slot>', escapeHtml(this.attr("label", "Item")),
      '</slot></span><span class="trailing"><slot name="trailing">', escapeHtml(this.attr("trailing-icon", "")),
      "</slot></span></button>",
    ].join("");
    this.shadowRoot.querySelector("button").addEventListener("click", () => {
      if (!disabled) emit(this, "select", { value: this.attr("value", this.attr("label", "")) });
    });
  }
}
define("sui-side-navigation-item", SuiSideNavigationItem);

class SuiBasicScrollIndicator extends SuiElement {
  static get observedAttributes() { return ["orientation", "length", "fraction", "thumb-fraction"]; }
  render() {
    const vertical = this.attr("orientation", "vertical") === "vertical";
    const length = Math.max(24, this.num("length", 160));
    const fraction = Math.min(1, Math.max(0, this.num("fraction", 0)));
    const thumbFraction = Math.min(1, Math.max(0.05, this.num("thumb-fraction", 0.25)));
    const thumbLength = length * thumbFraction;
    const offset = (length - thumbLength) * fraction;
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.track{position:relative;border-radius:2px;background:", themeColor("fillTertiary"), ";",
      vertical ? "width:4px;height:" + length + "px" : "height:4px;width:" + length + "px", "}.thumb{position:absolute;border-radius:2px;background:",
      themeColor("fillSecondary"), ";", vertical ? "width:4px;height:" + thumbLength + "px;top:" + offset + "px" :
        "height:4px;width:" + thumbLength + "px;left:" + offset + "px", "}</style><div class=\"track\"><span class=\"thumb\"></span></div>",
    ].join("");
  }
}
define("sui-basic-scroll-indicator", SuiBasicScrollIndicator);

}

/* ===== date-range-picker.js ===== */
{
/* DateRangePicker — the range-selection counterpart to sui-date-picker. */

const WEEKDAYS = ["S", "M", "T", "W", "T", "F", "S"];
const MONTHS = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

function dateValue(year, month, day) {
  return year + "-" + String(month + 1).padStart(2, "0") + "-" + String(day).padStart(2, "0");
}

function timeValue(value) {
  if (!value) return null;
  const date = new Date(value + "T00:00:00Z");
  return Number.isNaN(date.getTime()) ? null : date.getTime();
}

class SuiDateRangePicker extends SuiElement {
  static get observedAttributes() { return ["year", "month", "start", "end", "disabled"]; }

  render() {
    const today = new Date();
    const year = Math.round(this.num("year", today.getFullYear()));
    const month = Math.min(11, Math.max(0, Math.round(this.num("month", today.getMonth()))));
    const start = this.attr("start");
    const end = this.attr("end");
    const startTime = timeValue(start);
    const endTime = timeValue(end);
    const disabled = this.bool("disabled");
    const firstDay = new Date(year, month, 1).getDay();
    const days = new Date(year, month + 1, 0).getDate();
    const cells = Array(firstDay).fill(null).concat(Array.from({ length: days }, (_, index) => index + 1));
    const classes = (day) => {
      const value = dateValue(year, month, day);
      const time = timeValue(value);
      return [value === start ? "start" : "", value === end ? "end" : "",
        startTime != null && endTime != null && time > startTime && time < endTime ? "between" : ""]
        .filter(Boolean).join(" ");
    };
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.calendar{width:416px;padding:16px;color:", themeColor("labelPrimary"),
      ";box-sizing:border-box}.calendar.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}",
      ".head{height:32px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between}",
      ".title{font:700 20px/26px sans-serif}.nav{width:32px;height:32px;border:0;border-radius:50%;background:transparent;",
      "color:inherit;font-size:20px;cursor:pointer}.nav:hover{background:var(--sui-lighten-hover)}",
      ".grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}.wk,.day{height:32px;display:grid;place-items:center}",
      ".wk{font-size:12px;color:", themeColor("labelQuaternary"), "}.day{position:relative;border:0;background:transparent;",
      "color:inherit;font:500 14px/18px sans-serif;cursor:pointer;border-radius:16px}.day:hover{background:var(--sui-lighten-hover)}",
      ".day.between{border-radius:0;background:", themeColor("fillLight"), "}.day.start,.day.end{background:",
      themeColor("fillSecondary"), ";border-radius:16px}.empty{visibility:hidden}</style>",
      '<div class="calendar ', disabled ? "disabled" : "", '"><div class="head"><button class="nav prev">‹</button><span class="title">',
      escapeHtml(MONTHS[month] + " " + year), '</span><button class="nav next">›</button></div><div class="grid">',
      WEEKDAYS.map((weekday) => '<div class="wk">' + weekday + "</div>").join(""),
      cells.map((day) => day == null ? '<span class="empty"></span>' :
        '<button class="day ' + classes(day) + '" data-day="' + day + '">' + day + "</button>").join(""),
      "</div></div>",
    ].join("");
    this.shadowRoot.querySelector(".prev").addEventListener("click", () => this.changeMonth(year, month, -1));
    this.shadowRoot.querySelector(".next").addEventListener("click", () => this.changeMonth(year, month, 1));
    this.shadowRoot.querySelectorAll(".day").forEach((day) => day.addEventListener("click", () => {
      const value = dateValue(year, month, Number(day.dataset.day));
      const valueTime = timeValue(value);
      if (!start || end || valueTime < startTime) {
        this._rendered = false;
        this.removeAttribute("end");
        this.setAttribute("start", value);
        this.render();
        this._rendered = true;
        emit(this, "range-change", { start: value, end: null });
      } else {
        this.setAttribute("end", value);
        emit(this, "range-change", { start, end: value });
      }
    }));
  }

  changeMonth(year, month, amount) {
    const value = new Date(year, month + amount, 1);
    this.setAttribute("year", String(value.getFullYear()));
    this.setAttribute("month", String(value.getMonth()));
  }
}

define("sui-date-range-picker", SuiDateRangePicker);

}

/* ===== menu.js ===== */
{
/* Menu, SubMenu, MenuItem and BasicMenuItem. */

class SuiMenuItem extends SuiElement {
  static get observedAttributes() {
    return ["title", "subtitle", "leading-icon", "trailing-icon", "disabled", "selected"];
  }
  render() {
    const disabled = this.bool("disabled");
    const selected = this.bool("selected");
    this.shadowRoot.innerHTML = [
      "<style>:host{display:block;min-width:160px}.item{width:100%;min-height:48px;padding:8px 12px;display:flex;align-items:center;gap:8px;",
      "border:0;border-radius:12px;background:", selected ? themeColor("fillSecondary") : "transparent", ";color:", themeColor("labelPrimary"),
      ";font-family:inherit;text-align:start;cursor:pointer}.item:hover{background:", themeColor("fillLight"), "}.item.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}",
      ".copy{flex:1;min-width:0}.title{font-size:16px;line-height:20px;font-weight:600}.subtitle{font-size:12px;line-height:16px;color:",
      themeColor("labelTertiary"), "}.icon{width:24px;display:grid;place-items:center}</style>",
      '<button class="item ', disabled ? "disabled" : "", '" role="menuitem"><span class="icon"><slot name="leading">',
      escapeHtml(this.attr("leading-icon", "")), '</slot></span><span class="copy"><span class="title"><slot>',
      escapeHtml(this.attr("title", "Menu item")), '</slot></span>', this.attr("subtitle") ? '<span class="subtitle">' + escapeHtml(this.attr("subtitle")) + "</span>" : "",
      '</span><span class="icon"><slot name="trailing">', escapeHtml(this.attr("trailing-icon", "")), "</slot></span></button>",
    ].join("");
    this.shadowRoot.querySelector("button").addEventListener("click", () => {
      if (!disabled) emit(this, "select", { value: this.attr("value", this.attr("title", "")) });
    });
  }
}
define("sui-menu-item", SuiMenuItem);

class SuiBasicMenuItem extends SuiElement {
  render() {
    this.shadowRoot.innerHTML = "<style>:host{display:block;min-width:160px}.row{display:flex;align-items:center;min-height:48px;width:100%}</style><div class=\"row\"><slot></slot></div>";
  }
}
define("sui-basic-menu-item", SuiBasicMenuItem);

class SuiMenuBase extends SuiOverlayElement {
  static get observedAttributes() {
    return ["for", "offset-x", "offset-y", "corner-radius", "max-height", "hidden",
      "dismiss-on-click-outside", "dismiss-on-escape", "clipping-enabled", "viewport-padding"];
  }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    const maxHeight = Math.max(48, this.num("max-height", 480));
    this.shadowRoot.innerHTML = [
      "<style>", overlayCss, ".surface{min-width:160px;max-width:320px;max-height:", maxHeight,
      "px;padding:8px;border-radius:", radius, "px;overflow:auto;flex-direction:column;gap:4px}</style>",
      '<div class="surface material-thick" part="surface" role="menu" tabindex="-1"><slot></slot></div>',
    ].join("");
  }
  shouldDismissOnOutsidePointer() { return !this.hasAttribute("dismiss-on-click-outside") || this.bool("dismiss-on-click-outside"); }
  shouldDismissOnEscape() { return !this.hasAttribute("dismiss-on-escape") || this.bool("dismiss-on-escape"); }
}

class SuiMenu extends SuiMenuBase {
  calculatePosition(anchorRect, contentSize, anchor) {
    return computePopupPosition(anchorRect, contentSize, "align-start", "below", this.offset(8), getComputedStyle(anchor).direction);
  }
}
define("sui-menu", SuiMenu);

class SuiSubMenu extends SuiMenuBase {
  calculatePosition(anchorRect, contentSize, anchor) {
    const direction = getComputedStyle(anchor).direction;
    const offset = this.offset();
    if (!this.hasAttribute("offset-x")) offset.x = direction === "rtl" ? -8 : 8;
    return computePopupPosition(anchorRect, contentSize, "to-end-of", "align-top", offset, direction);
  }
}
define("sui-sub-menu", SuiSubMenu);

}

/* ===== dialogs.js ===== */
{
/* AlertDialog, DatePickerDialog and Sheet families. */

class SuiModalSurface extends SuiElement {
  constructor() {
    super();
    this._cleanup = [];
  }

  connectedCallback() {
    super.connectedCallback();
    this.setAttribute("popover", "manual");
    this.activate();
  }

  disconnectedCallback() {
    this.deactivate();
    try { this.hidePopover?.(); } catch (_) { /* Already detached or unsupported. */ }
  }

  attributeChangedCallback(name, oldValue, newValue) {
    super.attributeChangedCallback(name, oldValue, newValue);
    if (oldValue !== newValue && this.isConnected) queueMicrotask(() => this.activate());
  }

  deactivate() { this._cleanup.splice(0).forEach((cleanup) => cleanup()); }

  activate() {
    this.deactivate();
    if (this.hidden) return;
    try {
      if (!this.matches(":popover-open")) this.showPopover?.();
    } catch (_) { /* Fixed-position fallback. */ }
    const backdrop = this.shadowRoot.querySelector(".backdrop");
    if (!backdrop) return;
    if (this.dismissOnOutside()) {
      const outside = (event) => {
        if (event.target === backdrop) this.requestDismiss("outside-pointer", event);
      };
      backdrop.addEventListener("pointerdown", outside);
      this._cleanup.push(() => backdrop.removeEventListener("pointerdown", outside));
    }
    if (this.dismissOnEscape()) {
      const escape = (event) => {
        if (event.key === "Escape" && !event.defaultPrevented) {
          event.preventDefault();
          this.requestDismiss("escape-key", event);
        }
      };
      this.ownerDocument.addEventListener("keydown", escape, true);
      this._cleanup.push(() => this.ownerDocument.removeEventListener("keydown", escape, true));
    }
    this.shadowRoot.querySelector(".panel")?.focus({ preventScroll: true });
  }

  dismissOnOutside() { return this.bool("dismiss-on-click-outside"); }
  dismissOnEscape() { return this.bool("dismiss-on-escape"); }
  requestDismiss(reason, sourceEvent) { emit(this, "dismiss-request", { reason, sourceEvent }); }

  modalCss(radius, material = "thick") {
    const background = material === "thickest"
      ? "var(--Background-MaterialThickest,rgba(255,255,255,.72))"
      : "var(--Background-MaterialThick,rgba(255,255,255,.58))";
    return [
      ":host{position:fixed;inset:0;display:block;width:auto;height:auto;margin:0;padding:0;border:0;",
      "background:transparent;z-index:var(--sui-modal-z-index,1200);font-family:inherit}",
      ":host([hidden]){display:none!important}.backdrop{position:absolute;inset:0;display:grid;place-items:center;padding:32px;",
      "background:rgba(0,0,0,.28);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}",
      ".panel{max-width:calc(100vw - 64px);max-height:calc(100vh - 64px);overflow:auto;outline:none;color:",
      themeColor("labelPrimary"), ";background:", background, ";backdrop-filter:blur(64px) saturate(1.2);",
      "-webkit-backdrop-filter:blur(64px) saturate(1.2);border-radius:", radius,
      "px;box-shadow:0 30px 90px rgba(0,0,0,.38),inset 0 0 0 1px rgba(255,255,255,.3)}",
      "*,*::before,*::after{box-sizing:border-box}",
    ].join("");
  }
}

class SuiBasicAlertDialog extends SuiModalSurface {
  static get observedAttributes() { return ["corner-radius", "dismiss-on-click-outside", "dismiss-on-escape", "hidden"]; }
  dismissOnOutside() { return !this.hasAttribute("dismiss-on-click-outside") || this.bool("dismiss-on-click-outside"); }
  dismissOnEscape() { return !this.hasAttribute("dismiss-on-escape") || this.bool("dismiss-on-escape"); }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    this.shadowRoot.innerHTML = "<style>" + this.modalCss(radius) +
      "</style><div class=\"backdrop\"><div class=\"panel\" part=\"surface\" role=\"alertdialog\" aria-modal=\"true\" tabindex=\"-1\"><slot></slot></div></div>";
  }
}
define("sui-basic-alert-dialog", SuiBasicAlertDialog);

class SuiAlertDialog extends SuiBasicAlertDialog {
  static get observedAttributes() {
    return [...SuiBasicAlertDialog.observedAttributes, "title", "message", "icon", "orientation"];
  }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    const vertical = this.attr("orientation", "horizontal") === "vertical";
    const width = vertical ? 360 : 480;
    this.shadowRoot.innerHTML = [
      "<style>", this.modalCss(radius), ".panel{width:", width, "px;min-height:184px;padding:32px;display:flex;flex-direction:column}",
      ".head{display:flex;align-items:center;justify-content:", vertical ? "center" : "flex-start", ";flex-direction:", vertical ? "column" : "row",
      ";gap:12px;padding-bottom:24px}.icon{font-size:28px}.title{font-size:24px;line-height:30px;font-weight:700}.content{flex:1;color:",
      themeColor("labelSecondary"), ";font-size:16px;line-height:24px}.buttons{display:flex;justify-content:flex-end;gap:8px;padding-top:24px}</style>",
      '<div class="backdrop"><div class="panel" part="surface" role="alertdialog" aria-modal="true" tabindex="-1"><div class="head"><span class="icon"><slot name="icon">',
      escapeHtml(this.attr("icon", "")), '</slot></span><span class="title"><slot name="title">', escapeHtml(this.attr("title", "")),
      '</slot></span></div><div class="content"><slot>', escapeHtml(this.attr("message", "")),
      '</slot></div><div class="buttons"><slot name="buttons"></slot></div></div></div>',
    ].join("");
  }
}
define("sui-alert-dialog", SuiAlertDialog);

class SuiDatePickerDialog extends SuiModalSurface {
  static get observedAttributes() { return ["title", "corner-radius", "dismiss-on-click-outside", "dismiss-on-escape", "hidden"]; }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 16));
    this.shadowRoot.innerHTML = [
      "<style>", this.modalCss(radius, "thickest"), ".panel{width:480px}.title{height:96px;padding:0 32px;display:flex;align-items:center;",
      "font-size:24px;line-height:30px;font-weight:700;color:", themeColor("labelSecondary"), "}.content{padding:0 32px 40px}",
      ".buttons{display:flex;justify-content:flex-end;gap:8px;padding:0 32px 32px}</style>",
      '<div class="backdrop"><div class="panel" part="surface" role="dialog" aria-modal="true" tabindex="-1"><div class="title"><slot name="title">',
      escapeHtml(this.attr("title", "")), '</slot></div><div class="content"><slot></slot></div><div class="buttons"><slot name="negative"></slot><slot name="positive"></slot></div></div></div>',
    ].join("");
  }
}
define("sui-date-picker-dialog", SuiDatePickerDialog);

class SuiBasicSheet extends SuiModalSurface {
  static get observedAttributes() { return ["corner-radius", "dismiss-on-click-outside", "dismiss-on-escape", "hidden"]; }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    this.shadowRoot.innerHTML = "<style>" + this.modalCss(radius) +
      ".panel{width:480px;min-width:360px;min-height:184px}</style><div class=\"backdrop\"><div class=\"panel\" part=\"surface\" role=\"dialog\" aria-modal=\"true\" tabindex=\"-1\"><slot></slot></div></div>";
  }
}
define("sui-basic-sheet", SuiBasicSheet);

class SuiSheet extends SuiBasicSheet {
  static get observedAttributes() { return [...SuiBasicSheet.observedAttributes, "title"]; }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    this.shadowRoot.innerHTML = [
      "<style>", this.modalCss(radius), ".panel{width:480px;min-width:360px;min-height:184px}.bar{min-height:96px;padding:0 32px;display:grid;",
      "grid-template-columns:1fr auto 1fr;align-items:center}.leading{justify-self:start}.title{font-size:20px;line-height:26px;font-weight:600}.trailing{justify-self:end}",
      ".content{padding:0 32px 32px;color:", themeColor("labelSecondary"), "}.bottom{padding-top:24px}</style>",
      '<div class="backdrop"><div class="panel" part="surface" role="dialog" aria-modal="true" tabindex="-1"><div class="bar"><span class="leading"><slot name="leading"></slot></span><span class="title"><slot name="title">',
      escapeHtml(this.attr("title", "")), '</slot></span><span class="trailing"><slot name="trailing"></slot></span></div><div class="content"><slot></slot><div class="bottom"><slot name="bottom"></slot></div></div></div></div>',
    ].join("");
  }
}
define("sui-sheet", SuiSheet);

class SuiHeadImageSheet extends SuiSheet {
  render() {
    super.render();
    const panel = this.shadowRoot.querySelector(".panel");
    const header = document.createElement("div");
    header.className = "header-image";
    header.innerHTML = '<slot name="header-image"></slot>';
    const style = document.createElement("style");
    style.textContent = ".header-image{position:relative;width:100%;overflow:hidden}.header-image slot::slotted(*){width:100%;display:block}";
    this.shadowRoot.append(style);
    panel.prepend(header);
  }
}
define("sui-head-image-sheet", SuiHeadImageSheet);

}

/* ===== feedback.js ===== */
{
/* SnackbarHost and Coachmark components. */

class SuiSnackbarHost extends SuiElement {
  constructor() {
    super();
    this._queue = [];
    this._active = null;
    this._timer = 0;
  }
  static get observedAttributes() { return ["position"]; }
  disconnectedCallback() { clearTimeout(this._timer); }
  render() {
    const position = this.attr("position", "bottom-center");
    this.shadowRoot.innerHTML = [
      "<style>:host{position:fixed;inset:0;pointer-events:none;z-index:1300}.host{position:absolute;left:50%;display:flex;flex-direction:column;gap:8px;",
      "transform:translateX(-50%);", position.startsWith("top") ? "top:80px" : "bottom:80px", "}.snack{min-width:320px;max-width:560px;min-height:56px;",
      "padding:12px 16px;border-radius:32px;display:flex;align-items:center;gap:12px;color:", themeColor("labelPrimary"),
      ";background:var(--Background-MaterialRegular,rgba(255,255,255,.55));backdrop-filter:blur(50px);box-shadow:0 18px 48px rgba(0,0,0,.24);pointer-events:auto}",
      ".icon{font-size:22px}.copy{flex:1}.title{font-size:16px;line-height:20px;font-weight:600}.description{font-size:12px;line-height:16px;color:",
      themeColor("labelTertiary"), "}.action{border:0;border-radius:16px;padding:8px 12px;background:", themeColor("fillSecondary"),
      ";color:inherit;font:600 12px/16px sans-serif;cursor:pointer}</style><div class=\"host\"><div id=\"slot\"></div><slot></slot></div>",
    ].join("");
    if (this._active) this.paintActive();
  }
  show(message, options = {}) {
    return new Promise((resolve) => {
      this._queue.push({ message, options, resolve });
      this.advance();
    });
  }
  dismiss(reason = "dismissed") {
    if (!this._active) return;
    clearTimeout(this._timer);
    const active = this._active;
    this._active = null;
    active.resolve(reason);
    emit(this, "snackbar-result", { result: reason });
    this.paintActive();
    setTimeout(() => this.advance(), 16);
  }
  advance() {
    if (this._active || !this._queue.length) return;
    this._active = this._queue.shift();
    this.paintActive();
    const duration = this._active.options.duration ?? 3000;
    if (duration !== Infinity) this._timer = setTimeout(() => this.dismiss("dismissed"), duration);
  }
  paintActive() {
    const slot = this.shadowRoot.querySelector("#slot");
    if (!slot) return;
    if (!this._active) { slot.innerHTML = ""; return; }
    const { message, options } = this._active;
    slot.innerHTML = [
      '<div class="snack"><span class="icon">', escapeHtml(options.leadingIcon || ""), '</span><div class="copy"><div class="title">',
      escapeHtml(message), '</div>', options.description ? '<div class="description">' + escapeHtml(options.description) + "</div>" : "",
      '</div>', options.action ? '<button class="action">' + escapeHtml(options.action) + "</button>" : "", "</div>",
    ].join("");
    slot.querySelector(".action")?.addEventListener("click", () => this.dismiss("action-performed"));
  }
}
define("sui-snackbar-host", SuiSnackbarHost);

class SuiCoachmark extends SuiOverlayElement {
  static variant = null;
  static get observedAttributes() {
    return ["for", "direction", "gap", "variant", "text", "title", "image", "button-text", "corner-radius", "hidden"];
  }
  render() {
    const direction = this.attr("direction", "to-end").toLowerCase();
    const variant = (this.constructor.variant || this.attr("variant", "simple")).toLowerCase();
    const radius = Math.max(0, this.num("corner-radius", variant === "simple" ? 8 : 16));
    this.shadowRoot.innerHTML = [
      "<style>", overlayCss, ".surface{overflow:visible;background:", themeColor("fillPrimary"), ";color:", themeColor("labelPrimaryLight"),
      ";border-radius:", radius, "px;box-shadow:0 18px 48px rgba(0,0,0,.3)}.body{position:relative;min-width:", variant === "simple" ? "160" : "300",
      "px;max-width:360px;padding:", variant === "simple" ? "16" : "24", "px}.title{font-size:20px;font-weight:700;margin-bottom:8px}.text{font-size:16px;line-height:24px}",
      ".image{width:100%;max-height:220px;object-fit:cover;border-radius:", Math.max(0, radius - 8), "px;margin-bottom:16px}.actions{display:flex;justify-content:flex-end;padding-top:16px}",
      ".tip{position:absolute;width:16px;height:16px;background:", themeColor("fillPrimary"), ";transform:rotate(45deg)}",
      direction === "to-start" ? ".tip{right:-8px;top:calc(50% - 8px)}" : "",
      direction === "to-end" ? ".tip{left:-8px;top:calc(50% - 8px)}" : "",
      direction === "above" ? ".tip{bottom:-8px;left:calc(50% - 8px)}" : "",
      direction === "below" ? ".tip{top:-8px;left:calc(50% - 8px)}" : "",
      "</style><div class=\"surface material-none\" part=\"surface\"><div class=\"body\"><span class=\"tip\"></span>",
      this.attr("image") ? '<img class="image" src="' + escapeHtml(this.attr("image")) + '" alt="">' : '<slot name="image"></slot>',
      this.attr("title") ? '<div class="title">' + escapeHtml(this.attr("title")) + "</div>" : '<slot name="title"></slot>',
      '<div class="text"><slot>', escapeHtml(this.attr("text", "")), '</slot></div><div class="actions"><slot name="button">',
      this.attr("button-text") ? '<sui-button size="min" text="' + escapeHtml(this.attr("button-text")) + '"></sui-button>' : "",
      "</slot></div></div></div>",
    ].join("");
  }
  calculatePosition(anchorRect, contentSize, anchor) {
    const direction = this.attr("direction", "to-end").toLowerCase();
    const gap = this.num("gap", 8);
    const rtl = getComputedStyle(anchor).direction;
    if (direction === "to-start") return computePopupPosition(anchorRect, contentSize, "to-start-of", "center", { x: rtl === "rtl" ? gap : -gap }, rtl);
    if (direction === "above") return computePopupPosition(anchorRect, contentSize, "center", "above", { y: -gap }, rtl);
    if (direction === "below") return computePopupPosition(anchorRect, contentSize, "center", "below", { y: gap }, rtl);
    return computePopupPosition(anchorRect, contentSize, "to-end-of", "center", { x: rtl === "rtl" ? -gap : gap }, rtl);
  }
}
define("sui-coachmark", SuiCoachmark);

class SuiSimpleCoachmark extends SuiCoachmark { static variant = "simple"; }
class SuiRichCoachmark extends SuiCoachmark { static variant = "rich"; }
class SuiImageCoachmark extends SuiCoachmark { static variant = "image"; }
define("sui-simple-coachmark", SuiSimpleCoachmark);
define("sui-rich-coachmark", SuiRichCoachmark);
define("sui-image-coachmark", SuiImageCoachmark);

}

/* ===== window-components.js ===== */
{
/* Toolbar and Subwindow window-attached containers. */

class SuiToolbar extends SuiOverlayElement {
  static get observedAttributes() {
    return ["for", "corner-radius", "focusable", "segmented", "offset-x", "offset-y", "offset-z", "hidden"];
  }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 32));
    const segmented = this.bool("segmented");
    const focusable = !this.hasAttribute("focusable") || this.bool("focusable");
    this.shadowRoot.innerHTML = [
      "<style>", overlayCss, ".surface{min-height:64px;max-width:min(960px,calc(100vw - 48px));padding:8px;border-radius:", radius,
      "px;align-items:center;gap:8px;overflow:auto}.surface.segmented{background:transparent;box-shadow:none;padding:0;gap:16px}",
      ".main,.supporting{min-height:64px;display:flex;align-items:center;gap:4px;padding:8px;border-radius:", radius,
      "px}.segmented .main,.segmented .supporting{background:var(--Background-MaterialRegular,rgba(255,255,255,.34));",
      "backdrop-filter:blur(50px);box-shadow:inset 0 0 0 1px rgba(255,255,255,.28)}</style>",
      '<div class="surface material-regular ', segmented ? "segmented" : "", '" part="surface" role="toolbar" ', focusable ? "" : "inert", ">",
      '<div class="main"><slot></slot></div>', segmented ? '<div class="supporting"><slot name="supporting"></slot></div>' : "", "</div>",
    ].join("");
  }
  calculatePosition(anchorRect, contentSize) {
    return computeAugmentPosition(
      anchorRect,
      contentSize,
      parseNormalizedPoint("bottom-front"),
      parseNormalizedPoint("bottom-center"),
      this.offset(32),
    );
  }
}
define("sui-toolbar", SuiToolbar);

class SuiSubwindow extends SuiOverlayElement {
  static get observedAttributes() {
    return ["for", "placement", "focusable", "offset-x", "offset-y", "offset-z",
      "rotation-x", "rotation-y", "rotation-z", "hidden"];
  }
  render() {
    const focusable = !this.hasAttribute("focusable") || this.bool("focusable");
    this.shadowRoot.innerHTML = [
      "<style>", overlayCss, ".surface{width:360px;height:100%;min-height:0;border-radius:32px;overflow:auto}</style>",
      '<div class="surface material-regular" part="surface" role="region" ', focusable ? 'tabindex="-1"' : "inert", "><slot></slot></div>",
    ].join("");
  }
  prepareSurface(anchor, surface) {
    surface.style.height = anchor.getBoundingClientRect().height + "px";
  }
  calculatePosition(anchorRect, contentSize, anchor) {
    const requested = this.attr("placement", "default").toLowerCase();
    const rtl = getComputedStyle(anchor).direction === "rtl";
    const placement = requested === "default" ? (rtl ? "left" : "right") : requested;
    const right = placement === "right";
    const defaultX = right ? 24 : -24;
    return computeAugmentPosition(
      anchorRect,
      contentSize,
      parseNormalizedPoint(right ? "top-right-front" : "top-left-front"),
      parseNormalizedPoint(right ? "top-left" : "top-right"),
      { ...this.offset(), x: this.hasAttribute("offset-x") ? this.num("offset-x", defaultX) : defaultX },
    );
  }
}
define("sui-subwindow", SuiSubwindow);

}

PicoTheme.install({ scheme: 'vibrant' });
window.PicoTheme = PicoTheme;
window.SUI_COMPONENTS = ["sui-text","sui-icon","sui-button","sui-icon-button","sui-toggle-button","sui-switch","sui-checkbox","sui-badge","sui-dot-badge","sui-number-badge","sui-chip","sui-slider","sui-linear-progress","sui-circular-progress","sui-divider","sui-segment-control","sui-tab-bar","sui-text-field","sui-search-field","sui-number-field","sui-stepper","sui-link","sui-list-item","sui-page-control","sui-option","sui-side-navigation","sui-title-bar","sui-scroll-indicator","sui-wheel-picker","sui-timepicker","sui-date-picker","sui-augment","sui-spatial-popup","sui-tri-state-checkbox","sui-button-chip","sui-toggleable-chip","sui-removable-chip","sui-text-area","sui-horizontal-divider","sui-vertical-divider","sui-toggle-icon-button","sui-symbol-slider","sui-segment-slider","sui-symbolic-circular-progress","sui-progress-page-control","sui-stereo-image","sui-segment-item","sui-side-navigation-section","sui-side-navigation-item","sui-basic-scroll-indicator","sui-date-range-picker","sui-menu","sui-sub-menu","sui-menu-item","sui-basic-menu-item","sui-basic-alert-dialog","sui-alert-dialog","sui-date-picker-dialog","sui-basic-sheet","sui-sheet","sui-head-image-sheet","sui-snackbar-host","sui-coachmark","sui-simple-coachmark","sui-rich-coachmark","sui-image-coachmark","sui-toolbar","sui-subwindow"];
})();
