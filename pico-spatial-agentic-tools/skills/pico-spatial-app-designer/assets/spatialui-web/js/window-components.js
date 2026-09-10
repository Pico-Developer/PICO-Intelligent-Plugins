/* Toolbar and Subwindow window-attached containers. */
import { define, themeColor } from "./base.js";
import { SuiOverlayElement, overlayCss } from "./overlay.js";
import { computeAugmentPosition, parseNormalizedPoint } from "./overlay-position.js";

export class SuiToolbar extends SuiOverlayElement {
  static get observedAttributes() {
    return ["for", "corner-radius", "focusable", "segmented", "offset-x", "offset-y", "offset-z", "hidden"];
  }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 32));
    const segmented = this.bool("segmented");
    const focusable = !this.hasAttribute("focusable") || this.bool("focusable");
    this.shadowRoot.innerHTML = [
      "<style>", overlayCss, ".surface{min-height:64px;max-width:min(960px,calc(100vw - 48px));padding:8px;border-radius:", radius,
      "px;align-items:center;gap:8px;overflow:auto}.surface.segmented{background:transparent;box-shadow:none;padding:0;gap:16px}",
      ".main,.supporting{min-height:64px;display:flex;align-items:center;gap:4px;padding:8px;border-radius:", radius,
      "px}.segmented .main,.segmented .supporting{background:var(--Background-MaterialRegular,rgba(255,255,255,.34));",
      "backdrop-filter:blur(50px);box-shadow:inset 0 0 0 1px rgba(255,255,255,.28)}</style>",
      '<div class="surface material-regular ', segmented ? "segmented" : "", '" part="surface" role="toolbar" ', focusable ? "" : "inert", ">",
      '<div class="main"><slot></slot></div>', segmented ? '<div class="supporting"><slot name="supporting"></slot></div>' : "", "</div>",
    ].join("");
  }
  calculatePosition(anchorRect, contentSize) {
    return computeAugmentPosition(
      anchorRect,
      contentSize,
      parseNormalizedPoint("bottom-front"),
      parseNormalizedPoint("bottom-center"),
      this.offset(32),
    );
  }
}
define("sui-toolbar", SuiToolbar);

export class SuiSubwindow extends SuiOverlayElement {
  static get observedAttributes() {
    return ["for", "placement", "focusable", "offset-x", "offset-y", "offset-z",
      "rotation-x", "rotation-y", "rotation-z", "hidden"];
  }
  render() {
    const focusable = !this.hasAttribute("focusable") || this.bool("focusable");
    this.shadowRoot.innerHTML = [
      "<style>", overlayCss, ".surface{width:360px;height:100%;min-height:0;border-radius:32px;overflow:auto}</style>",
      '<div class="surface material-regular" part="surface" role="region" ', focusable ? 'tabindex="-1"' : "inert", "><slot></slot></div>",
    ].join("");
  }
  prepareSurface(anchor, surface) {
    surface.style.height = anchor.getBoundingClientRect().height + "px";
  }
  calculatePosition(anchorRect, contentSize, anchor) {
    const requested = this.attr("placement", "default").toLowerCase();
    const rtl = getComputedStyle(anchor).direction === "rtl";
    const placement = requested === "default" ? (rtl ? "left" : "right") : requested;
    const right = placement === "right";
    const defaultX = right ? 24 : -24;
    return computeAugmentPosition(
      anchorRect,
      contentSize,
      parseNormalizedPoint(right ? "top-right-front" : "top-left-front"),
      parseNormalizedPoint(right ? "top-left" : "top-right"),
      { ...this.offset(), x: this.hasAttribute("offset-x") ? this.num("offset-x", defaultX) : defaultX },
    );
  }
}
define("sui-subwindow", SuiSubwindow);
