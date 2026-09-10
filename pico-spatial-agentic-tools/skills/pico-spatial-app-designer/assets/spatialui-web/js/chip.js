/*
 * Chips — mirrors Chips.kt (ButtonChip / ToggleableChip / RemovableChip).
 * Sizes: Small h=32 (r=16, hpad 16 / with leading 12), Regular h=40 (r=38, hpad 20 / with leading 16).
 * Kotlin default colors (from defaultChipColors / defaultToggleableChipColors):
 *   ButtonChip:         container=fillSecondary, content=labelPrimary
 *   ToggleableChip off: container=fillTertiary,  content=labelPrimary
 *   ToggleableChip on:  container=fillSecondary, content=labelPrimary
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

const SIZES = {
  small: { h: 32, r: 16, hpad: 16, hpadLeading: 12, fs: 14, lh: 18, fw: 600 },
  regular: { h: 40, r: 38, hpad: 20, hpadLeading: 16, fs: 16, lh: 20, fw: 600 },
};

export class SuiChip extends SuiElement {
  static get observedAttributes() { return ["size", "disabled", "selected", "toggle", "removable", "label", "leading-icon", "container-color", "content-color"]; }
  render() {
    const s = SIZES[this.attr("size", "small").toLowerCase()] || SIZES.small;
    const disabled = this.bool("disabled");
    const toggle = this.bool("toggle");
    const selected = this.bool("selected");
    const removable = this.bool("removable");
    const leadingIcon = this.attr("leading-icon");
    const hasLeading = leadingIcon != null;
    const active = toggle && selected;
    const defaultBg = active ? themeColor("fillSecondary") : (toggle ? themeColor("fillTertiary") : themeColor("fillSecondary"));
    const defaultFg = themeColor("labelPrimary");
    const bg = this.attr("container-color", defaultBg);
    const fg = this.attr("content-color", defaultFg);
    const hpad = hasLeading ? s.hpadLeading : s.hpad;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .chip { display:inline-flex; align-items:center; gap:4px; height:${s.h}px;
          padding:0 ${hpad}px; border-radius:${s.r}px; background:${bg}; color:${fg};
          font-weight:${s.fw}; font-size:${s.fs}px; line-height:${s.lh}px; font-family:inherit;
          cursor:pointer; user-select:none; position:relative; overflow:hidden;
          transition:background-color .12s ease; }
        .chip.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .chip::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .chip:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .chip:active::after { background: var(--sui-lighten-pressed, rgba(255,255,255,0.20)); }
        .lead { display:inline-flex; width:${s.fs + 2}px; height:${s.fs + 2}px; align-items:center; justify-content:center; }
        .close { margin-left:2px; opacity:.8; font-size:${s.fs}px; }
      </style>
      <div class="chip ${disabled ? "sui-disabled" : ""}" role="button">
        ${hasLeading ? `<span class="lead">${leadingIcon}</span>` : ""}
        <span><slot>${this.attr("label", "Chip")}</slot></span>
        ${removable ? `<span class="close">✕</span>` : ""}
      </div>`;
    this.shadowRoot.querySelector(".chip").addEventListener("click", (e) => {
      if (disabled) return;
      if (removable && e.target.classList.contains("close")) {
        emit(this, "remove", {});
        return;
      }
      if (toggle) {
        const next = !selected;
        this.toggleAttribute("selected", next);
        emit(this, "checked-change", { selected: next });
      }
      emit(this, "click-action", {});
    });
  }
}
define("sui-chip", SuiChip);
