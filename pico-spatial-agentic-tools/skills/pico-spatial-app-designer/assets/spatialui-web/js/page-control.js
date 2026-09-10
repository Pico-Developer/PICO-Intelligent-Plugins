/*
 * PageControl — mirrors PageControl.kt. Dot radius 4, dot space 12, vertical padding 8.
 * Kotlin default colors (defaultPageControlColors):
 *   selected dot   = labelPrimaryLight
 *   unselected dot = fillSecondary
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

export class SuiPageControl extends SuiElement {
  static get observedAttributes() { return ["count", "index", "disabled", "selected-color", "unselected-color"]; }
  render() {
    const count = this.num("count", 5);
    const index = this.num("index", 0);
    const disabled = this.bool("disabled");
    const r = 4, space = 12, dot = r * 2;
    const activeC = this.attr("selected-color", themeColor("labelPrimaryLight"));
    const inactiveC = this.attr("unselected-color", themeColor("fillSecondary"));
    let dots = "";
    for (let i = 0; i < count; i++) {
      const active = i === index;
      dots += `<div class="dot ${active ? "active" : ""}" data-i="${i}"></div>`;
    }
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .bar { display:inline-flex; align-items:center; gap:${space}px; padding:8px 0; }
        .bar.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .dot { width:${dot}px; height:${dot}px; border-radius:${r}px; background:${inactiveC};
          cursor:pointer; transition:width .2s ease, background-color .2s ease; }
        .dot.active { width:${dot * 3}px; background:${activeC}; }
      </style>
      <div class="bar ${disabled ? "sui-disabled" : ""}">${dots}</div>`;
    this.shadowRoot.querySelectorAll(".dot").forEach((d) => {
      d.addEventListener("click", () => {
        if (disabled) return;
        this.setAttribute("index", d.dataset.i);
        emit(this, "select", { index: +d.dataset.i });
      });
    });
  }
}
define("sui-page-control", SuiPageControl);
