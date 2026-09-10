/*
 * Link — mirrors Link.kt. Text-like button, content defaults to interaction color.
 * Sizes Regular minHeight 24 / Max 32; optional trailing icon.
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

export class SuiLink extends SuiElement {
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
