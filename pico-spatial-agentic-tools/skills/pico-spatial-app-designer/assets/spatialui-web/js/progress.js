/*
 * ProgressIndicators — mirrors LinearProgressIndicator.kt & CircularProgressIndicator.kt.
 * Linear: width 240, Small h=4 / Regular h=8. Circular: Small 20 / Regular 30 / Max 40, stroke=10% of size (min 2).
 * Colors (from Kotlin defaults):
 *   Linear:   track=fillTertiary, bar=labelPrimaryLight
 *   Circular: track=fillTertiary, bar=interaction (determinate) / labelPrimaryLight (indeterminate)
 */
import { SuiElement, define, themeColor } from "./base.js";

export class SuiLinearProgress extends SuiElement {
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

export class SuiCircularProgress extends SuiElement {
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
