/*
 * SideNavigation / SideNavigationItem — mirrors SideNavigation.kt.
 * Item shape r=24 (RadiusHuge), content padding 8, leading/trailing size 32, gap 8.
 * Kotlin default colors (defaultSideNavigationItemColors):
 *   header title         = labelSecondary
 *   section label        = labelQuaternary
 *   unselected item:     container=transparent, content=labelPrimary
 *   selected item:       container=fillSecondary, content=labelPrimary
 */
import { SuiElement, define, emit, Dimension, themeColor } from "./base.js";

export class SuiSideNavigation extends SuiElement {
  static get observedAttributes() { return ["items", "selected-index", "header", "header-color", "selected-container-color", "content-color"]; }
  render() {
    const items = (this.attr("items", "") || "").split(",").map((s) => s.trim()).filter(Boolean);
    const sel = this.num("selected-index", 0);
    const header = this.attr("header");
    const headerC = this.attr("header-color", themeColor("labelSecondary"));
    const contentC = this.attr("content-color", themeColor("labelPrimary"));
    const selBg = this.attr("selected-container-color", themeColor("fillSecondary"));
    const hoverBg = themeColor("fillLight");
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .nav { display:flex; flex-direction:column; gap:4px; min-width:200px; }
        .header { padding:8px 12px; font-size:20px; line-height:26px; font-weight:700;
          color:${headerC}; }
        .item { display:flex; align-items:center; gap:8px; padding:8px; border-radius:${Dimension.RadiusHuge}px;
          color:${contentC}; font-size:16px; line-height:20px; font-weight:600; font-family:inherit;
          cursor:pointer; user-select:none; background:transparent; transition:background-color .12s ease;
          border: none; width: 100%; text-align: left; position:relative; overflow:hidden; }
        .item::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; border-radius:inherit; }
        .item:hover::after { background: ${hoverBg}; }
        .item.active { background:${selBg}; color:${contentC}; }
        .item.active::after { background: transparent; }
        .dot { width:32px; height:32px; border-radius:50%; background:${themeColor("fillTertiary")};
          display:inline-flex; align-items:center; justify-content:center; font-size:16px; flex:0 0 auto; position:relative; z-index:1; }
        .item > span:last-child { position:relative; z-index:1; }
        .item.active .dot { background:${themeColor("fillLight")}; }
      </style>
      <div class="nav">
        ${header ? `<div class="header">${header}</div>` : ""}
        ${items.map((label, i) => `
          <button class="item ${i === sel ? "active" : ""}" data-i="${i}">
            <span class="dot">${label.charAt(0)}</span><span>${label}</span>
          </button>`).join("")}
      </div>`;
    this.shadowRoot.querySelectorAll(".item").forEach((it) => {
      it.addEventListener("click", () => {
        const i = +it.dataset.i;
        this.setAttribute("selected-index", String(i));
        emit(this, "select", { index: i, value: items[i] });
      });
    });
  }
}
define("sui-side-navigation", SuiSideNavigation);
