/*
 * Option — mirrors Option.kt. MinWidth 120, MinHeight 48, gap 4.
 * Kotlin default colors (defaultOptionColors):
 *   checked:   bg=fillSecondary, content=labelPrimary
 *   unchecked: bg=fillTertiary,  content=labelPrimary
 */
import { SuiElement, define, emit, Dimension, themeColor } from "./base.js";

export class SuiOption extends SuiElement {
  static get observedAttributes() { return ["checked", "disabled", "label", "icon", "checked-container-color", "container-color", "content-color"]; }
  render() {
    const checked = this.bool("checked");
    const disabled = this.bool("disabled");
    const icon = this.attr("icon");
    const defaultBg = checked ? themeColor("fillSecondary") : themeColor("fillTertiary");
    const defaultFg = themeColor("labelPrimary");
    const bg = checked
      ? this.attr("checked-container-color", this.attr("container-color", defaultBg))
      : this.attr("container-color", defaultBg);
    const fg = this.attr("content-color", defaultFg);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .opt { display:inline-flex; flex-direction:column; align-items:center; justify-content:center; gap:4px;
          min-width:120px; min-height:48px; padding:8px 12px; border-radius:${Dimension.RadiusLarge}px;
          background:${bg}; color:${fg}; cursor:pointer; user-select:none; box-sizing:border-box;
          position:relative; overflow:hidden; transition:background-color .12s ease; }
        .opt.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .opt::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .opt:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .icon { font-size:22px; display:inline-flex; position:relative; z-index:1; }
        .label { font-size:16px; line-height:20px; font-weight:600; font-family:inherit; position:relative; z-index:1; }
      </style>
      <div class="opt ${disabled ? "sui-disabled" : ""}" role="radio" aria-checked="${checked}">
        ${icon ? `<span class="icon">${icon}</span>` : ""}
        <span class="label"><slot>${this.attr("label", "Option")}</slot></span>
      </div>`;
    this.shadowRoot.querySelector(".opt").addEventListener("click", () => {
      if (disabled) return;
      this.toggleAttribute("checked", true);
      emit(this, "checked-change", { checked: true });
    });
  }
}
define("sui-option", SuiOption);
