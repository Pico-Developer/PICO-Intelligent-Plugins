/* Text — mirrors Typography roles from Typography.kt / TypeScaleTokens.kt. */
import { SuiElement, define, typeStyle, themeColor } from "./base.js";

export class SuiText extends SuiElement {
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
