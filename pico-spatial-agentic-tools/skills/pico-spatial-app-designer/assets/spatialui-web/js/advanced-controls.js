/* Missing public SpatialUI control variants. */
import { SuiElement, define, emit, escapeHtml, themeColor } from "./base.js";

function copyAttributes(from, to, excluded = []) {
  for (const attribute of from.attributes) {
    if (!excluded.includes(attribute.name)) to.setAttribute(attribute.name, attribute.value);
  }
}

class SuiControlProxy extends SuiElement {
  renderProxy(tagName, forced = {}, excluded = []) {
    const target = document.createElement(tagName);
    copyAttributes(this, target, excluded);
    for (const [name, value] of Object.entries(forced)) target.setAttribute(name, value);
    target.innerHTML = "<slot></slot>";
    this.shadowRoot.innerHTML = "<style>:host{display:inline-flex}</style>";
    this.shadowRoot.append(target);
    return target;
  }
}

export class SuiToggleIconButton extends SuiControlProxy {
  static get observedAttributes() { return ["checked", "disabled", "size", "icon"]; }
  render() {
    const target = this.renderProxy("sui-icon-button", { toggle: "" }, ["checked"]);
    target.toggleAttribute("selected", this.bool("checked"));
    target.addEventListener("checked-change", (event) => {
      event.stopPropagation();
      const checked = Boolean(event.detail.selected);
      this.toggleAttribute("checked", checked);
      emit(this, "checked-change", { checked });
    });
  }
}
define("sui-toggle-icon-button", SuiToggleIconButton);

export class SuiSymbolSlider extends SuiControlProxy {
  static get observedAttributes() { return ["value", "min", "max", "size", "width", "disabled", "icon"]; }
  render() {
    const icon = this.attr("icon", "♪");
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.wrap{display:flex;align-items:center;position:relative}",
      ".symbol{position:absolute;left:12px;z-index:2;color:var(--sui-label-primary-light);pointer-events:none}</style>",
      '<div class="wrap"><span class="symbol">', escapeHtml(icon), "</span></div>",
    ].join("");
    const target = document.createElement("sui-slider");
    copyAttributes(this, target, ["icon"]);
    target.addEventListener("value-change", (event) => emit(this, "value-change", event.detail));
    this.shadowRoot.querySelector(".wrap").append(target);
  }
}
define("sui-symbol-slider", SuiSymbolSlider);

export class SuiSegmentSlider extends SuiElement {
  static get observedAttributes() { return ["step", "segment-count", "size", "width", "disabled"]; }
  render() {
    const count = Math.max(1, Math.round(this.num("segment-count", 4)));
    const step = Math.min(count, Math.max(0, Math.round(this.num("step", 0))));
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.wrap{position:relative}.ticks{position:absolute;inset:0 16px;pointer-events:none}",
      ".ticks i{position:absolute;top:50%;width:2px;height:6px;border-radius:2px;background:var(--sui-label-primary-light);",
      "transform:translate(-50%,-50%);opacity:.55}</style><div class=\"wrap\"><sui-slider min=\"0\" max=\"",
      count, "\" value=\"", step, "\"></sui-slider><div class=\"ticks\">",
      Array.from({ length: count + 1 }, (_, index) => '<i style="left:' + index / count * 100 + '%"></i>').join(""),
      "</div></div>",
    ].join("");
    const target = this.shadowRoot.querySelector("sui-slider");
    for (const name of ["size", "width", "disabled"]) {
      if (this.hasAttribute(name)) target.setAttribute(name, this.getAttribute(name));
    }
    target.addEventListener("value-change", (event) => {
      const next = Math.min(count, Math.max(0, Math.round(event.detail.value)));
      this.setAttribute("step", String(next));
      emit(this, "step-change", { step: next, segmentCount: count });
    });
  }
}
define("sui-segment-slider", SuiSegmentSlider);

const CIRCULAR_SIZE = { small: 20, regular: 30, max: 40 };
export class SuiSymbolicCircularProgress extends SuiElement {
  static get observedAttributes() { return ["value", "size", "symbol", "track-color", "progress-color", "symbol-color"]; }
  render() {
    const size = CIRCULAR_SIZE[this.attr("size", "max").toLowerCase()] || 40;
    const stroke = Math.max(2, size * 0.1);
    const value = Math.max(0, Math.min(1, this.num("value", 0.6)));
    const radius = (size - stroke) / 2;
    const circumference = 2 * Math.PI * radius;
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-grid;place-items:center}.wrap{display:grid;place-items:center;position:relative}",
      "svg{grid-area:1/1;transform:rotate(-90deg)}.symbol{grid-area:1/1;color:",
      this.attr("symbol-color", themeColor("labelPrimary")), ";font-size:", size * 0.38,
      "px;line-height:1}</style><div class=\"wrap\"><svg width=\"", size, "\" height=\"", size,
      "\"><circle cx=\"", size / 2, "\" cy=\"", size / 2, "\" r=\"", radius,
      "\" fill=\"none\" stroke=\"", this.attr("track-color", themeColor("fillTertiary")),
      "\" stroke-width=\"", stroke, "\"/><circle cx=\"", size / 2, "\" cy=\"", size / 2,
      "\" r=\"", radius, "\" fill=\"none\" stroke=\"", this.attr("progress-color", themeColor("interaction")),
      "\" stroke-width=\"", stroke, "\" stroke-linecap=\"round\" stroke-dasharray=\"",
      circumference * value, " ", circumference, "\"/></svg><span class=\"symbol\"><slot>",
      escapeHtml(this.attr("symbol", "✓")), "</slot></span></div>",
    ].join("");
  }
}
define("sui-symbolic-circular-progress", SuiSymbolicCircularProgress);

export class SuiProgressPageControl extends SuiElement {
  static get observedAttributes() { return ["count", "index", "progress", "disabled", "selected-color", "unselected-color"]; }
  render() {
    const count = Math.max(1, Math.round(this.num("count", 5)));
    const selected = Math.min(count - 1, Math.max(0, Math.round(this.num("index", 0))));
    const progress = Math.min(1, Math.max(0, this.num("progress", 0.5)));
    const disabled = this.bool("disabled");
    const active = this.attr("selected-color", themeColor("labelPrimaryLight"));
    const normal = this.attr("unselected-color", themeColor("fillSecondary"));
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.bar{display:flex;align-items:center;gap:12px;padding:8px 0}",
      ".bar.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}.dot{width:8px;height:8px;border:0;border-radius:8px;background:",
      normal, ";padding:0;cursor:pointer;overflow:hidden}.dot.active{width:24px}.fill{height:100%;border-radius:inherit;background:",
      active, "}</style><div class=\"bar ", disabled ? "disabled" : "", "\">",
      Array.from({ length: count }, (_, index) => '<button class="dot ' + (index === selected ? "active" : "") + '" data-index="' + index + '">' +
        (index === selected ? '<span class="fill" style="display:block;width:' + (50 + progress * 50) + '%"></span>' : "") + "</button>").join(""),
      "</div>",
    ].join("");
    this.shadowRoot.querySelectorAll(".dot").forEach((dot) => dot.addEventListener("click", () => {
      if (disabled) return;
      const index = Number(dot.dataset.index);
      this.setAttribute("index", String(index));
      emit(this, "select", { index });
    }));
  }
}
define("sui-progress-page-control", SuiProgressPageControl);

export class SuiStereoImage extends SuiElement {
  static get observedAttributes() { return ["src", "alt", "texture-layout", "eye", "width", "height", "fit"]; }
  render() {
    const layout = this.attr("texture-layout", "none").toLowerCase();
    const eye = this.attr("eye", "left").toLowerCase();
    const width = this.attr("width", "320px");
    const height = this.attr("height", "180px");
    const sideBySide = layout === "side-by-side";
    const topAndBottom = layout === "top-and-bottom";
    const imageWidth = sideBySide ? "200%" : "100%";
    const imageHeight = topAndBottom ? "200%" : "100%";
    const x = sideBySide && eye === "right" ? "50%" : "0";
    const y = topAndBottom && eye === "right" ? "50%" : "0";
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex;width:", width, ";height:", height,
      ";overflow:hidden}img{width:", imageWidth, ";height:", imageHeight,
      ";max-width:none;max-height:none;object-fit:", this.attr("fit", "cover"),
      ";transform:translate(-", x, ",-", y, ")}</style><img src=\"", escapeHtml(this.attr("src", "")),
      "\" alt=\"", escapeHtml(this.attr("alt", "")), "\">",
    ].join("");
  }
}
define("sui-stereo-image", SuiStereoImage);
