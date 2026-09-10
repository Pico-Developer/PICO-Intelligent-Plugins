/*
 * WheelPicker / Timepicker — mirrors Timepicker.kt & WheelPickerDefaults.
 * Item height 40, indicator shape r=12, indicator bg=fillSecondary.
 * selected text=labelPrimary, unselected text=labelTertiary. Timepicker width 416, gap 16.
 */
import { SuiElement, define, emit, Dimension, themeColor } from "./base.js";

const ITEM_H = 40;
const VISIBLE = 5;

export class SuiWheelPicker extends SuiElement {
  static get observedAttributes() { return ["items", "index", "width", "disabled"]; }
  render() {
    const items = (this.attr("items", "") || "").split(",").map((s) => s.trim()).filter(Boolean);
    const width = this.num("width", 120);
    const disabled = this.bool("disabled");
    const idx = this.num("index", 0);
    const listH = ITEM_H * VISIBLE;
    const padCount = (VISIBLE - 1) / 2;
    const pads = Array.from({ length: padCount }, () => `<div class="item pad"></div>`).join("");
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .wheel { position:relative; width:${width}px; height:${listH}px; overflow:hidden;
          -webkit-mask-image:linear-gradient(transparent, rgba(0,0,0,.5) 14%, #000 44%, #000 56%, rgba(0,0,0,.5) 86%, transparent);
          mask-image:linear-gradient(transparent, rgba(0,0,0,.5) 14%, #000 44%, #000 56%, rgba(0,0,0,.5) 86%, transparent); }
        .wheel.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .band { position:absolute; left:0; right:0; top:${padCount * ITEM_H}px; height:${ITEM_H}px;
          border-radius:${Dimension.RadiusMediumLarge}px; background:${themeColor("fillSecondary")}; pointer-events:none; }
        .scroll { position:absolute; inset:0; overflow-y:scroll; scroll-snap-type:y mandatory;
          scrollbar-width:none; }
        .scroll::-webkit-scrollbar { display:none; }
        .item { height:${ITEM_H}px; display:flex; align-items:center; justify-content:center;
          scroll-snap-align:center; font-size:16px; font-weight:500; font-family:inherit;
          color:${themeColor("labelTertiary")}; transition:color .1s ease; }
        .item.sel { color:${themeColor("labelPrimary")}; font-weight:600; }
        .pad { scroll-snap-align:none; }
      </style>
      <div class="wheel ${disabled ? "sui-disabled" : ""}">
        <div class="band"></div>
        <div class="scroll">
          ${pads}
          ${items.map((t, i) => `<div class="item ${i === idx ? "sel" : ""}" data-i="${i}">${t}</div>`).join("")}
          ${pads}
        </div>
      </div>`;
    const scroll = this.shadowRoot.querySelector(".scroll");
    const itemsEls = this.shadowRoot.querySelectorAll(".item[data-i]");
    scroll.scrollTop = idx * ITEM_H;
    let raf;
    scroll.addEventListener("scroll", () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const i = Math.round(scroll.scrollTop / ITEM_H);
        itemsEls.forEach((el) => el.classList.toggle("sel", +el.dataset.i === i));
        if (i !== +(this.getAttribute("index") || -1)) {
          this.setAttribute("index", String(i));
          emit(this, "select", { index: i, value: items[i] });
        }
      });
    });
  }
}
define("sui-wheel-picker", SuiWheelPicker);

export class SuiTimepicker extends SuiElement {
  static get observedAttributes() { return ["hour", "minute", "second", "seconds"]; }
  render() {
    const showSeconds = this.getAttribute("seconds") !== "false";
    const pad2 = (n) => String(n).padStart(2, "0");
    const hours = Array.from({ length: 24 }, (_, i) => pad2(i)).join(",");
    const mins = Array.from({ length: 60 }, (_, i) => pad2(i)).join(",");
    const h = this.num("hour", 0), m = this.num("minute", 0), s = this.num("second", 0);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .tp { display:inline-flex; align-items:center; gap:16px; width:416px; justify-content:center; }
        .colon { color:${themeColor("labelPrimary")}; font-size:20px; font-weight:600; }
      </style>
      <div class="tp">
        <sui-wheel-picker items="${hours}" index="${h}" width="96"></sui-wheel-picker>
        <span class="colon">:</span>
        <sui-wheel-picker items="${mins}" index="${m}" width="96"></sui-wheel-picker>
        ${showSeconds ? `<span class="colon">:</span>
        <sui-wheel-picker items="${mins}" index="${s}" width="96"></sui-wheel-picker>` : ""}
      </div>`;
  }
}
define("sui-timepicker", SuiTimepicker);
