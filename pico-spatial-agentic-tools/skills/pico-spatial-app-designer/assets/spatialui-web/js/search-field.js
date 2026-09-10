/*
 * SearchField — mirrors SearchField.kt. Width 280, cornerRadius 100 (pill), leading search icon.
 * Kotlin default colors (defaultSearchFieldColors):
 *   container=fillTertiary, focused indicator=fillSecondary,
 *   text=labelPrimary, placeholder=labelQuaternary, search icon=labelQuaternary.
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

export class SuiSearchField extends SuiElement {
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
