/*
 * Checkbox / TriStateCheckbox — mirrors CheckBox.kt.
 * Hit box 32, content circle Regular 18 / Small 14, border 1.5.
 * off: circle stroke=labelSecondary. on/indeterminate: fill=labelPrimary, mark=labelPrimaryLight.
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

export class SuiCheckbox extends SuiElement {
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
