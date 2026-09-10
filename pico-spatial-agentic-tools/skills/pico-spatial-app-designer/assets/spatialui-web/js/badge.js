/*
 * Badge / DotBadge / NumberBadge — mirrors Badge.kt.
 * Dot size 12 (default color = error). Badge sizes ExtraSmall 12(r=2) / Small 18(r=4) / Regular 24(r=4).
 * NumberBadge: Small 16 / Regular 20, pill, bg=error, content=labelPrimaryLight, overflow "N+".
 */
import { SuiElement, define, themeColor } from "./base.js";

export class SuiDotBadge extends SuiElement {
  static get observedAttributes() { return ["color"]; }
  render() {
    const color = this.attr("color", themeColor("error"));
    this.shadowRoot.innerHTML = `
      <style>:host{display:inline-flex}.dot{width:12px;height:12px;border-radius:50%;background:${color};}</style>
      <div class="dot"></div>`;
  }
}
define("sui-dot-badge", SuiDotBadge);

const BADGE_SIZE = { extrasmall: { h: 12, r: 2, pad: 3 }, small: { h: 18, r: 4, pad: 4 }, regular: { h: 24, r: 4, pad: 8 } };

export class SuiBadge extends SuiElement {
  static get observedAttributes() { return ["size", "text", "background-color", "content-color"]; }
  render() {
    const s = BADGE_SIZE[this.attr("size", "small").toLowerCase()] || BADGE_SIZE.small;
    const bg = this.attr("background-color", themeColor("fillPrimary"));
    const fg = this.attr("content-color", themeColor("labelPrimaryLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .badge { min-width:${s.h}px; height:${s.h}px; padding:0 ${s.pad}px; border-radius:${s.r}px;
          background:${bg}; color:${fg}; display:inline-flex; align-items:center; justify-content:center;
          font-size:12px; line-height:16px; font-weight:500; font-family:inherit; }
      </style>
      <div class="badge"><slot>${this.attr("text", "")}</slot></div>`;
  }
}
define("sui-badge", SuiBadge);

export class SuiNumberBadge extends SuiElement {
  static get observedAttributes() { return ["number", "threshold", "overflow", "size", "background-color"]; }
  render() {
    const h = this.attr("size", "small").toLowerCase() === "regular" ? 20 : 16;
    const number = this.num("number", 0);
    const threshold = this.num("threshold", 99);
    const bg = this.attr("background-color", themeColor("error"));
    const fg = themeColor("labelPrimaryLight");
    const label = number > threshold ? `${threshold}+` : `${number}`;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .badge { min-width:${h}px; height:${h}px; padding:0 ${h < 18 ? 4 : 6}px; border-radius:${h / 2}px;
          background:${bg}; color:${fg}; display:inline-flex; align-items:center; justify-content:center;
          font-size:10px; line-height:14px; font-weight:600; font-family:inherit; }
      </style>
      <div class="badge">${label}</div>`;
  }
}
define("sui-number-badge", SuiNumberBadge);
