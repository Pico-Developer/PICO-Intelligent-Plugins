/*
 * Icon — mirrors Icon.kt. Default size 24, tint = LocalContentColor (labelPrimaryLight).
 * Renders slotted SVG / glyph / a src image, applying size + tint (via currentColor).
 */
import { SuiElement, define, themeColor } from "./base.js";

export class SuiIcon extends SuiElement {
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
