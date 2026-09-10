/*
 * Button — mirrors Button.kt.
 * Sizes (minWidth/minHeight, cornerRadius, textStyle):
 *   Max:     104x56, r=32,  20/26/500
 *   Regular:  81x48, r=102, titleMedium 16/20/600
 *   Small:    69x40, r=20,  labelLarge  14/18/600
 *   Min:      57x32, r=16,  labelMedium 12/16/600
 * Default colors: container=fillPrimary, content=labelPrimaryLight (overridable).
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

const SIZES = {
  max: { minW: 104, minH: 56, r: 32, hpad: 24, fs: 20, lh: 26, fw: 500 },
  regular: { minW: 81, minH: 48, r: 102, hpad: 20, fs: 16, lh: 20, fw: 600 },
  small: { minW: 69, minH: 40, r: 20, hpad: 16, fs: 14, lh: 18, fw: 600 },
  min: { minW: 57, minH: 32, r: 16, hpad: 12, fs: 12, lh: 16, fw: 600 },
};

export class SuiButton extends SuiElement {
  static get observedAttributes() { return ["size", "disabled", "container-color", "content-color", "text"]; }
  render() {
    const s = SIZES[this.attr("size", "regular").toLowerCase()] || SIZES.regular;
    const disabled = this.bool("disabled");
    const container = this.attr("container-color", themeColor("fillPrimary"));
    const content = this.attr("content-color", themeColor("labelPrimaryLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-flex; }
        .btn {
          display: inline-flex; align-items: center; justify-content: center; gap: 4px;
          min-width: ${s.minW}px; min-height: ${s.minH}px;
          padding: 0 ${s.hpad}px; border-radius: ${s.r}px;
          background: ${container}; color: ${content};
          font-weight: ${s.fw}; font-size: ${s.fs}px; line-height: ${s.lh}px;
          font-family: inherit; border: none; cursor: pointer; user-select: none;
          transition: filter .12s ease; position: relative; overflow: hidden;
        }
        .btn.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .btn:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .btn:active::after { background: var(--sui-lighten-pressed, rgba(255,255,255,0.20)); }
        ::slotted(*) { display: inline-flex; align-items: center; }
      </style>
      <button class="btn ${disabled ? "sui-disabled" : ""}" ${disabled ? "disabled" : ""}>
        <slot name="leading"></slot>
        <span><slot>${this.attr("text", "Button")}</slot></span>
        <slot name="trailing"></slot>
      </button>`;
    this.shadowRoot.querySelector(".btn").addEventListener("click", () => {
      if (!disabled) emit(this, "click-action", {});
    });
  }
}
define("sui-button", SuiButton);
