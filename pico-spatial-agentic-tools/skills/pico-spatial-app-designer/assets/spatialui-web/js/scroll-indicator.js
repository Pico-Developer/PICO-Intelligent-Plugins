/*
 * ScrollIndicator — mirrors ScrollIndicator.kt.
 * Kotlin default colors (defaultScrollIndicatorColors):
 *   track=labelQuaternary (alpha 0.2 normal / 0.9 hover),
 *   thumb=labelPrimary (alpha 0.5 normal / 1.0 hover),
 *   hot-area background=fillLight (alpha 0 normal / 1 hover).
 */
import { SuiElement, define, themeColor } from "./base.js";

export class SuiScrollIndicator extends SuiElement {
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
