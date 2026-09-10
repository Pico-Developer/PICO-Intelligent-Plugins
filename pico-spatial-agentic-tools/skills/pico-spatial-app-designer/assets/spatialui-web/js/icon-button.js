/*
 * IconButton / ToggleIconButton — mirrors IconButton.kt.
 * Sizes: Min 38x32, Small 46x40, Regular 56x48, Max 66x56. Shape r=35 (pill).
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

const SIZES = {
  min: { minW: 38, minH: 32, icon: 16 },
  small: { minW: 46, minH: 40, icon: 20 },
  regular: { minW: 56, minH: 48, icon: 24 },
  max: { minW: 66, minH: 56, icon: 28 },
};

export class SuiIconButton extends SuiElement {
  static get observedAttributes() { return ["size", "disabled", "container-color", "content-color", "icon", "selected", "toggle"]; }
  render() {
    const s = SIZES[this.attr("size", "regular").toLowerCase()] || SIZES.regular;
    const disabled = this.bool("disabled");
    const toggle = this.bool("toggle");
    const selected = this.bool("selected");
    const container = this.attr("container-color",
      toggle && selected ? themeColor("interaction") : themeColor("fillPrimary"));
    const content = this.attr("content-color", themeColor("labelPrimaryLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-flex; }
        .btn {
          display: inline-flex; align-items: center; justify-content: center;
          min-width: ${s.minW}px; min-height: ${s.minH}px; border-radius: 35px;
          background: ${container}; color: ${content};
          border: none; cursor: pointer; position: relative; overflow: hidden;
          transition: background-color .12s ease;
        }
        .btn.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .btn:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .btn:active::after { background: var(--sui-lighten-pressed, rgba(255,255,255,0.20)); }
        .icon { width:${s.icon}px; height:${s.icon}px; display:inline-flex; align-items:center; justify-content:center; font-size:${s.icon}px; }
        ::slotted(*) { width:${s.icon}px; height:${s.icon}px; }
      </style>
      <button class="btn ${disabled ? "sui-disabled" : ""}" ${disabled ? "disabled" : ""}>
        <span class="icon"><slot>${this.attr("icon", "★")}</slot></span>
      </button>`;
    this.shadowRoot.querySelector(".btn").addEventListener("click", () => {
      if (disabled) return;
      if (toggle) {
        const next = !selected;
        this.toggleAttribute("selected", next);
        emit(this, "checked-change", { selected: next });
      }
      emit(this, "click-action", {});
    });
  }
}
define("sui-icon-button", SuiIconButton);
