/* Web equivalents for public Compose scope/slot components. */
import { SuiElement, define, emit, escapeHtml, themeColor } from "./base.js";

export class SuiSegmentItem extends SuiElement {
  static get observedAttributes() { return ["selected", "disabled", "label", "value"]; }
  render() {
    const selected = this.bool("selected");
    const disabled = this.bool("disabled");
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.item{min-height:32px;padding:0 12px;border:0;border-radius:12px;",
      "background:", selected ? themeColor("fillSecondary") : "transparent", ";color:",
      selected ? themeColor("labelPrimary") : themeColor("labelTertiary"),
      ";font:600 16px/20px sans-serif;cursor:pointer}.item:hover{background:", themeColor("fillLight"),
      "}.item.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}</style>",
      '<button class="item ', disabled ? "disabled" : "", '" role="tab" aria-selected="', selected,
      '"><slot>', escapeHtml(this.attr("label", "Segment")), "</slot></button>",
    ].join("");
    this.shadowRoot.querySelector("button").addEventListener("click", () => {
      if (!disabled) emit(this, "select", { value: this.attr("value", this.attr("label", "")) });
    });
  }
}
define("sui-segment-item", SuiSegmentItem);

export class SuiSideNavigationSection extends SuiElement {
  static get observedAttributes() { return ["label"]; }
  render() {
    this.shadowRoot.innerHTML = [
      "<style>:host{display:flex;flex-direction:column;gap:4px}.label{padding:8px 12px;color:",
      themeColor("labelQuaternary"), ";font:600 12px/16px sans-serif}</style>",
      '<div class="label">', escapeHtml(this.attr("label", "")), "</div><slot></slot>",
    ].join("");
  }
}
define("sui-side-navigation-section", SuiSideNavigationSection);

export class SuiSideNavigationItem extends SuiElement {
  static get observedAttributes() { return ["selected", "disabled", "label", "leading-icon", "trailing-icon", "value"]; }
  render() {
    const selected = this.bool("selected");
    const disabled = this.bool("disabled");
    this.shadowRoot.innerHTML = [
      "<style>:host{display:block}.item{width:100%;min-height:48px;padding:8px;border:0;border-radius:24px;display:flex;align-items:center;gap:8px;",
      "background:", selected ? themeColor("fillSecondary") : "transparent", ";color:", themeColor("labelPrimary"),
      ";font:600 16px/20px sans-serif;text-align:start;cursor:pointer}.item:hover{background:", themeColor("fillLight"),
      "}.item.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}.leading,.trailing{width:32px;display:grid;place-items:center}.label{flex:1}</style>",
      '<button class="item ', disabled ? "disabled" : "", '" aria-current="', selected ? "page" : "false",
      '"><span class="leading"><slot name="leading">', escapeHtml(this.attr("leading-icon", "")),
      '</slot></span><span class="label"><slot>', escapeHtml(this.attr("label", "Item")),
      '</slot></span><span class="trailing"><slot name="trailing">', escapeHtml(this.attr("trailing-icon", "")),
      "</slot></span></button>",
    ].join("");
    this.shadowRoot.querySelector("button").addEventListener("click", () => {
      if (!disabled) emit(this, "select", { value: this.attr("value", this.attr("label", "")) });
    });
  }
}
define("sui-side-navigation-item", SuiSideNavigationItem);

export class SuiBasicScrollIndicator extends SuiElement {
  static get observedAttributes() { return ["orientation", "length", "fraction", "thumb-fraction"]; }
  render() {
    const vertical = this.attr("orientation", "vertical") === "vertical";
    const length = Math.max(24, this.num("length", 160));
    const fraction = Math.min(1, Math.max(0, this.num("fraction", 0)));
    const thumbFraction = Math.min(1, Math.max(0.05, this.num("thumb-fraction", 0.25)));
    const thumbLength = length * thumbFraction;
    const offset = (length - thumbLength) * fraction;
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.track{position:relative;border-radius:2px;background:", themeColor("fillTertiary"), ";",
      vertical ? "width:4px;height:" + length + "px" : "height:4px;width:" + length + "px", "}.thumb{position:absolute;border-radius:2px;background:",
      themeColor("fillSecondary"), ";", vertical ? "width:4px;height:" + thumbLength + "px;top:" + offset + "px" :
        "height:4px;width:" + thumbLength + "px;left:" + offset + "px", "}</style><div class=\"track\"><span class=\"thumb\"></span></div>",
    ].join("");
  }
}
define("sui-basic-scroll-indicator", SuiBasicScrollIndicator);
