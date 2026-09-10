/* SnackbarHost and Coachmark components. */
import { SuiElement, define, emit, escapeHtml, themeColor } from "./base.js";
import { SuiOverlayElement, overlayCss } from "./overlay.js";
import { computePopupPosition } from "./overlay-position.js";

export class SuiSnackbarHost extends SuiElement {
  constructor() {
    super();
    this._queue = [];
    this._active = null;
    this._timer = 0;
  }
  static get observedAttributes() { return ["position"]; }
  disconnectedCallback() { clearTimeout(this._timer); }
  render() {
    const position = this.attr("position", "bottom-center");
    this.shadowRoot.innerHTML = [
      "<style>:host{position:fixed;inset:0;pointer-events:none;z-index:1300}.host{position:absolute;left:50%;display:flex;flex-direction:column;gap:8px;",
      "transform:translateX(-50%);", position.startsWith("top") ? "top:80px" : "bottom:80px", "}.snack{min-width:320px;max-width:560px;min-height:56px;",
      "padding:12px 16px;border-radius:32px;display:flex;align-items:center;gap:12px;color:", themeColor("labelPrimary"),
      ";background:var(--Background-MaterialRegular,rgba(255,255,255,.55));backdrop-filter:blur(50px);box-shadow:0 18px 48px rgba(0,0,0,.24);pointer-events:auto}",
      ".icon{font-size:22px}.copy{flex:1}.title{font-size:16px;line-height:20px;font-weight:600}.description{font-size:12px;line-height:16px;color:",
      themeColor("labelTertiary"), "}.action{border:0;border-radius:16px;padding:8px 12px;background:", themeColor("fillSecondary"),
      ";color:inherit;font:600 12px/16px sans-serif;cursor:pointer}</style><div class=\"host\"><div id=\"slot\"></div><slot></slot></div>",
    ].join("");
    if (this._active) this.paintActive();
  }
  show(message, options = {}) {
    return new Promise((resolve) => {
      this._queue.push({ message, options, resolve });
      this.advance();
    });
  }
  dismiss(reason = "dismissed") {
    if (!this._active) return;
    clearTimeout(this._timer);
    const active = this._active;
    this._active = null;
    active.resolve(reason);
    emit(this, "snackbar-result", { result: reason });
    this.paintActive();
    setTimeout(() => this.advance(), 16);
  }
  advance() {
    if (this._active || !this._queue.length) return;
    this._active = this._queue.shift();
    this.paintActive();
    const duration = this._active.options.duration ?? 3000;
    if (duration !== Infinity) this._timer = setTimeout(() => this.dismiss("dismissed"), duration);
  }
  paintActive() {
    const slot = this.shadowRoot.querySelector("#slot");
    if (!slot) return;
    if (!this._active) { slot.innerHTML = ""; return; }
    const { message, options } = this._active;
    slot.innerHTML = [
      '<div class="snack"><span class="icon">', escapeHtml(options.leadingIcon || ""), '</span><div class="copy"><div class="title">',
      escapeHtml(message), '</div>', options.description ? '<div class="description">' + escapeHtml(options.description) + "</div>" : "",
      '</div>', options.action ? '<button class="action">' + escapeHtml(options.action) + "</button>" : "", "</div>",
    ].join("");
    slot.querySelector(".action")?.addEventListener("click", () => this.dismiss("action-performed"));
  }
}
define("sui-snackbar-host", SuiSnackbarHost);

export class SuiCoachmark extends SuiOverlayElement {
  static variant = null;
  static get observedAttributes() {
    return ["for", "direction", "gap", "variant", "text", "title", "image", "button-text", "corner-radius", "hidden"];
  }
  render() {
    const direction = this.attr("direction", "to-end").toLowerCase();
    const variant = (this.constructor.variant || this.attr("variant", "simple")).toLowerCase();
    const radius = Math.max(0, this.num("corner-radius", variant === "simple" ? 8 : 16));
    this.shadowRoot.innerHTML = [
      "<style>", overlayCss, ".surface{overflow:visible;background:", themeColor("fillPrimary"), ";color:", themeColor("labelPrimaryLight"),
      ";border-radius:", radius, "px;box-shadow:0 18px 48px rgba(0,0,0,.3)}.body{position:relative;min-width:", variant === "simple" ? "160" : "300",
      "px;max-width:360px;padding:", variant === "simple" ? "16" : "24", "px}.title{font-size:20px;font-weight:700;margin-bottom:8px}.text{font-size:16px;line-height:24px}",
      ".image{width:100%;max-height:220px;object-fit:cover;border-radius:", Math.max(0, radius - 8), "px;margin-bottom:16px}.actions{display:flex;justify-content:flex-end;padding-top:16px}",
      ".tip{position:absolute;width:16px;height:16px;background:", themeColor("fillPrimary"), ";transform:rotate(45deg)}",
      direction === "to-start" ? ".tip{right:-8px;top:calc(50% - 8px)}" : "",
      direction === "to-end" ? ".tip{left:-8px;top:calc(50% - 8px)}" : "",
      direction === "above" ? ".tip{bottom:-8px;left:calc(50% - 8px)}" : "",
      direction === "below" ? ".tip{top:-8px;left:calc(50% - 8px)}" : "",
      "</style><div class=\"surface material-none\" part=\"surface\"><div class=\"body\"><span class=\"tip\"></span>",
      this.attr("image") ? '<img class="image" src="' + escapeHtml(this.attr("image")) + '" alt="">' : '<slot name="image"></slot>',
      this.attr("title") ? '<div class="title">' + escapeHtml(this.attr("title")) + "</div>" : '<slot name="title"></slot>',
      '<div class="text"><slot>', escapeHtml(this.attr("text", "")), '</slot></div><div class="actions"><slot name="button">',
      this.attr("button-text") ? '<sui-button size="min" text="' + escapeHtml(this.attr("button-text")) + '"></sui-button>' : "",
      "</slot></div></div></div>",
    ].join("");
  }
  calculatePosition(anchorRect, contentSize, anchor) {
    const direction = this.attr("direction", "to-end").toLowerCase();
    const gap = this.num("gap", 8);
    const rtl = getComputedStyle(anchor).direction;
    if (direction === "to-start") return computePopupPosition(anchorRect, contentSize, "to-start-of", "center", { x: rtl === "rtl" ? gap : -gap }, rtl);
    if (direction === "above") return computePopupPosition(anchorRect, contentSize, "center", "above", { y: -gap }, rtl);
    if (direction === "below") return computePopupPosition(anchorRect, contentSize, "center", "below", { y: gap }, rtl);
    return computePopupPosition(anchorRect, contentSize, "to-end-of", "center", { x: rtl === "rtl" ? -gap : gap }, rtl);
  }
}
define("sui-coachmark", SuiCoachmark);

class SuiSimpleCoachmark extends SuiCoachmark { static variant = "simple"; }
class SuiRichCoachmark extends SuiCoachmark { static variant = "rich"; }
class SuiImageCoachmark extends SuiCoachmark { static variant = "image"; }
define("sui-simple-coachmark", SuiSimpleCoachmark);
define("sui-rich-coachmark", SuiRichCoachmark);
define("sui-image-coachmark", SuiImageCoachmark);
