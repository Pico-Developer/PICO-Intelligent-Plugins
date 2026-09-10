/*
 * Divider — mirrors Divider.kt. thickness 0.5, color dividerLine. Horizontal or vertical.
 */
import { SuiElement, define, themeColor } from "./base.js";

export class SuiDivider extends SuiElement {
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
