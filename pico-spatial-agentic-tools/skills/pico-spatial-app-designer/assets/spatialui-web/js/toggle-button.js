/*
 * ToggleButton — mirrors ToggleButton.kt.
 * Kotlin default colors (defaultToggleButtonColors):
 *   checked:   container=fillSecondary, content=labelPrimary
 *   unchecked: container=fillTertiary,  content=labelPrimary
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

const SIZES = {
  max: { minW: 104, minH: 56, r: 32, hpad: 24, fs: 20, lh: 26, fw: 500 },
  regular: { minW: 57, minH: 32, r: 16, hpad: 12, fs: 12, lh: 16, fw: 600 },
  small: { minW: 69, minH: 40, r: 20, hpad: 16, fs: 14, lh: 18, fw: 600 },
  min: { minW: 57, minH: 32, r: 16, hpad: 12, fs: 12, lh: 16, fw: 600 },
};

export class SuiToggleButton extends SuiElement {
  static get observedAttributes() { return ["size", "disabled", "checked", "text", "checked-container-color", "container-color", "content-color"]; }
  render() {
    const s = SIZES[this.attr("size", "regular").toLowerCase()] || SIZES.regular;
    const disabled = this.bool("disabled");
    const checked = this.bool("checked");
    const defaultContainer = checked ? themeColor("fillSecondary") : themeColor("fillTertiary");
    const defaultContent = themeColor("labelPrimary");
    const container = checked
      ? this.attr("checked-container-color", this.attr("container-color", defaultContainer))
      : this.attr("container-color", defaultContainer);
    const content = this.attr("content-color", defaultContent);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-flex; }
        .btn {
          display:inline-flex; align-items:center; justify-content:center; gap:4px;
          min-width:${s.minW}px; min-height:${s.minH}px; padding:0 ${s.hpad}px;
          border-radius:${s.r}px; background:${container}; color:${content};
          font-weight:${s.fw}; font-size:${s.fs}px; line-height:${s.lh}px;
          font-family:inherit; border:none; cursor:pointer; user-select:none;
          position:relative; overflow:hidden; transition:background-color .12s ease;
        }
        .btn.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .btn:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .btn:active::after { background: var(--sui-lighten-pressed, rgba(255,255,255,0.20)); }
      </style>
      <button class="btn ${disabled ? "sui-disabled" : ""}"><slot>${this.attr("text", "Toggle")}</slot></button>`;
    this.shadowRoot.querySelector(".btn").addEventListener("click", () => {
      if (disabled) return;
      const next = !checked;
      this.toggleAttribute("checked", next);
      emit(this, "checked-change", { checked: next });
    });
  }
}
define("sui-toggle-button", SuiToggleButton);
