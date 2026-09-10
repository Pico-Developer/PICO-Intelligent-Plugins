/*
 * TextField / TextArea — mirrors TextField.kt.
 * MinHeight 48, DefaultWidth 280, cornerRadius RadiusMediumLarge(12), borderWidth 1.
 * Kotlin default colors (defaultTextFieldColors):
 *   container=fillTertiary, focused indicator=fillSecondary,
 *   text=labelPrimary, placeholder=labelQuaternary, supporting=labelTertiary,
 *   error indicator=error, cursor=fillPrimary.
 */
import { SuiElement, define, emit, Dimension, themeColor } from "./base.js";

export class SuiTextField extends SuiElement {
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
