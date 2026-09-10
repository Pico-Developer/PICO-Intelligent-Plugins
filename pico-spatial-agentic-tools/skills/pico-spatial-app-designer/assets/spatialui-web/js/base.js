/*
 * Shared helpers for SpatialUI web components.
 *
 * Components read colors from the --sui-* CSS custom properties installed by
 * PicoTheme.install() (see tokens.js). This mirrors Compose: PicoTheme() pushes
 * ColorScheme via CompositionLocal, and components read the ambient theme.
 */
import { PicoTheme, Dimension, TypeScale, DISABLE_ALPHA } from "./tokens.js";

export { PicoTheme, Dimension, TypeScale, DISABLE_ALPHA };

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

export function themeVar(role) {
  return VAR_MAP[role] || `--sui-${role.replace(/[A-Z]/g, (c) => "-" + c.toLowerCase())}`;
}

export function themeColor(role) {
  return `var(${themeVar(role)})`;
}

/** Shared base class: a shadow-root element with themed reactive attributes. */
export class SuiElement extends HTMLElement {
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
export const baseCss = `
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
export function typeStyle(role) {
  const t = TypeScale[role] || TypeScale.bodyLarge;
  return `font-weight:${t.weight};font-size:${t.size}px;line-height:${t.line}px;`;
}

/** Emit a bubbling, composed CustomEvent. */
export function emit(el, name, detail) {
  el.dispatchEvent(new CustomEvent(name, { detail, bubbles: true, composed: true }));
}

/** Escape untrusted text before inserting it into a component template. */
export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

/** Define a custom element once (safe against duplicate registration). */
export function define(tag, klass) {
  if (!customElements.get(tag)) customElements.define(tag, klass);
}

