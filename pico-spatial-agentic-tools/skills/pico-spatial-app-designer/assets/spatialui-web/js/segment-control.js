/*
 * SegmentControls — mirrors SegmentControls.kt.
 * Container bg=fillTertiary, container padding 4, item gap 4.
 * Sizes: Small h=40 / Regular h=48 / Rich h=88.
 * Selected item bg=fillSecondary / content=labelPrimary; unselected content=labelTertiary.
 */
import { SuiElement, define, emit, Dimension, themeColor } from "./base.js";

const H = { small: 40, regular: 48, rich: 88 };

export class SuiSegmentControl extends SuiElement {
  static get observedAttributes() { return ["options", "selected-index", "size", "disabled"]; }
  render() {
    const items = (this.attr("options", "") || "").split(",").map((s) => s.trim()).filter(Boolean);
    const h = H[this.attr("size", "small").toLowerCase()] || H.small;
    const sel = this.num("selected-index", 0);
    const disabled = this.bool("disabled");
    const pad = 4, gap = 4;
    const outerR = Dimension.RadiusLarge;
    const innerR = outerR - pad;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .bar { display:inline-flex; gap:${gap}px; padding:${pad}px; height:${h}px; border-radius:${outerR}px;
          background:${themeColor("fillTertiary")}; box-sizing:border-box; }
        .bar.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .seg { display:inline-flex; align-items:center; justify-content:center; padding:0 12px;
          border-radius:${innerR}px; font-size:16px; line-height:20px; font-weight:600; font-family:inherit;
          cursor:pointer; user-select:none; color:${themeColor("labelTertiary")}; transition:all .15s ease;
          background:transparent; border:none; }
        .seg.active { background:${themeColor("fillSecondary")}; color:${themeColor("labelPrimary")}; }
        .seg:not(.active):hover { color:${themeColor("labelPrimary")};
          background: var(--sui-lighten-hover, rgba(255,255,255,0.08)); }
      </style>
      <div class="bar ${disabled ? "sui-disabled" : ""}" role="tablist">
        ${items.map((label, i) => `<button class="seg ${i === sel ? "active" : ""}" data-i="${i}">${label}</button>`).join("")}
      </div>`;
    this.shadowRoot.querySelectorAll(".seg").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (disabled) return;
        const i = +btn.dataset.i;
        this.setAttribute("selected-index", String(i));
        emit(this, "select", { index: i, value: items[i] });
      });
    });
  }
}
define("sui-segment-control", SuiSegmentControl);
