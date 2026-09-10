/* Menu, SubMenu, MenuItem and BasicMenuItem. */
import { SuiElement, define, emit, escapeHtml, themeColor } from "./base.js";
import { SuiOverlayElement, overlayCss } from "./overlay.js";
import { computePopupPosition } from "./overlay-position.js";

export class SuiMenuItem extends SuiElement {
  static get observedAttributes() {
    return ["title", "subtitle", "leading-icon", "trailing-icon", "disabled", "selected"];
  }
  render() {
    const disabled = this.bool("disabled");
    const selected = this.bool("selected");
    this.shadowRoot.innerHTML = [
      "<style>:host{display:block;min-width:160px}.item{width:100%;min-height:48px;padding:8px 12px;display:flex;align-items:center;gap:8px;",
      "border:0;border-radius:12px;background:", selected ? themeColor("fillSecondary") : "transparent", ";color:", themeColor("labelPrimary"),
      ";font-family:inherit;text-align:start;cursor:pointer}.item:hover{background:", themeColor("fillLight"), "}.item.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}",
      ".copy{flex:1;min-width:0}.title{font-size:16px;line-height:20px;font-weight:600}.subtitle{font-size:12px;line-height:16px;color:",
      themeColor("labelTertiary"), "}.icon{width:24px;display:grid;place-items:center}</style>",
      '<button class="item ', disabled ? "disabled" : "", '" role="menuitem"><span class="icon"><slot name="leading">',
      escapeHtml(this.attr("leading-icon", "")), '</slot></span><span class="copy"><span class="title"><slot>',
      escapeHtml(this.attr("title", "Menu item")), '</slot></span>', this.attr("subtitle") ? '<span class="subtitle">' + escapeHtml(this.attr("subtitle")) + "</span>" : "",
      '</span><span class="icon"><slot name="trailing">', escapeHtml(this.attr("trailing-icon", "")), "</slot></span></button>",
    ].join("");
    this.shadowRoot.querySelector("button").addEventListener("click", () => {
      if (!disabled) emit(this, "select", { value: this.attr("value", this.attr("title", "")) });
    });
  }
}
define("sui-menu-item", SuiMenuItem);

export class SuiBasicMenuItem extends SuiElement {
  render() {
    this.shadowRoot.innerHTML = "<style>:host{display:block;min-width:160px}.row{display:flex;align-items:center;min-height:48px;width:100%}</style><div class=\"row\"><slot></slot></div>";
  }
}
define("sui-basic-menu-item", SuiBasicMenuItem);

class SuiMenuBase extends SuiOverlayElement {
  static get observedAttributes() {
    return ["for", "offset-x", "offset-y", "corner-radius", "max-height", "hidden",
      "dismiss-on-click-outside", "dismiss-on-escape", "clipping-enabled", "viewport-padding"];
  }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    const maxHeight = Math.max(48, this.num("max-height", 480));
    this.shadowRoot.innerHTML = [
      "<style>", overlayCss, ".surface{min-width:160px;max-width:320px;max-height:", maxHeight,
      "px;padding:8px;border-radius:", radius, "px;overflow:auto;flex-direction:column;gap:4px}</style>",
      '<div class="surface material-thick" part="surface" role="menu" tabindex="-1"><slot></slot></div>',
    ].join("");
  }
  shouldDismissOnOutsidePointer() { return !this.hasAttribute("dismiss-on-click-outside") || this.bool("dismiss-on-click-outside"); }
  shouldDismissOnEscape() { return !this.hasAttribute("dismiss-on-escape") || this.bool("dismiss-on-escape"); }
}

export class SuiMenu extends SuiMenuBase {
  calculatePosition(anchorRect, contentSize, anchor) {
    return computePopupPosition(anchorRect, contentSize, "align-start", "below", this.offset(8), getComputedStyle(anchor).direction);
  }
}
define("sui-menu", SuiMenu);

export class SuiSubMenu extends SuiMenuBase {
  calculatePosition(anchorRect, contentSize, anchor) {
    const direction = getComputedStyle(anchor).direction;
    const offset = this.offset();
    if (!this.hasAttribute("offset-x")) offset.x = direction === "rtl" ? -8 : 8;
    return computePopupPosition(anchorRect, contentSize, "to-end-of", "align-top", offset, direction);
  }
}
define("sui-sub-menu", SuiSubMenu);
