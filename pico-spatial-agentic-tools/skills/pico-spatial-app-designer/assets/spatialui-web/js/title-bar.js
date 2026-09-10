/*
 * TitleBar — mirrors TitleBar.kt. Height 96, horizontal padding 24, actions gap 8.
 * Kotlin default colors (defaultTitleBarColors):
 *   title=labelSecondary, leading/trailing actions=labelPrimary. Container is transparent.
 */
import { SuiElement, define, themeColor } from "./base.js";

export class SuiTitleBar extends SuiElement {
  static get observedAttributes() { return ["title", "width", "title-color", "action-color"]; }
  render() {
    const width = this.num("width", 480);
    const titleC = this.attr("title-color", themeColor("labelSecondary"));
    const actionC = this.attr("action-color", themeColor("labelPrimary"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:flex; }
        .bar { display:flex; align-items:center; gap:8px; min-height:96px; width:${width}px;
          padding:0 24px; box-sizing:border-box; }
        .lead { display:inline-flex; align-items:center; gap:8px; color:${actionC}; }
        .title { flex:1; font-size:20px; line-height:26px; font-weight:600; font-family:inherit;
          color:${titleC}; padding:0 16px; }
        .trail { display:inline-flex; align-items:center; gap:8px; color:${actionC}; }
      </style>
      <div class="bar">
        <span class="lead"><slot name="leading"></slot></span>
        <span class="title"><slot name="title">${this.attr("title", "Title")}</slot></span>
        <span class="trail"><slot name="trailing"></slot></span>
      </div>`;
  }
}
define("sui-title-bar", SuiTitleBar);
