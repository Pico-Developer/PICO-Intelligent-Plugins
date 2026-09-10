/*
 * Stepper — mirrors Stepper.kt. Height 40, width 152 (min 115), r=10.
 * Kotlin default colors: container=fillTertiary, value text=labelPrimary,
 *                        +/- button content=fillLight, container=transparent.
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

export class SuiStepper extends SuiElement {
  static get observedAttributes() { return ["value", "step", "editable", "decreasable", "increasable", "disabled", "container-color", "text-color", "button-color"]; }
  attributeChangedCallback(name) {
    if (name === "value" && this._internalWrite) return;
    super.attributeChangedCallback(name);
  }
  render() {
    const disabled = this.bool("disabled");
    const editable = this.bool("editable");
    const step = this.num("step", 1);
    const decreasable = this.getAttribute("decreasable") !== "false";
    const increasable = this.getAttribute("increasable") !== "false";
    // `value` is the single source of truth: re-sync on every render so an
    // external (controlled) update is reflected, keeping the last committed
    // value when the attribute is absent.
    this._value = this.hasAttribute("value") ? this.attr("value", "0") : (this._value ?? "0");
    const containerC = this.attr("container-color", themeColor("fillTertiary"));
    const textC = this.attr("text-color", themeColor("labelPrimary"));
    const btnC = this.attr("button-color", themeColor("fillLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .row { display:flex; align-items:center; min-width:152px; height:40px; padding:4px;
          background:${containerC}; border-radius:10px; box-sizing:border-box; caret-color:${themeColor("fillPrimary")}; }
        .row.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn { width:44px; height:32px; border:none; background:transparent; border-radius:8px;
          color:${btnC}; font-size:20px; cursor:pointer; display:inline-flex;
          align-items:center; justify-content:center; transition:background-color .12s; }
        .btn:hover:not(:disabled) { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .btn:disabled { opacity:.4; cursor:default; }
        .val { flex:1; text-align:center; background:transparent; border:none; outline:none;
          color:${textC}; font-size:16px; line-height:20px; font-weight:400;
          font-family:inherit; width:100%; padding:0 4px; }
      </style>
      <div class="row ${disabled ? "sui-disabled" : ""}">
        <button class="btn dec" ${decreasable ? "" : "disabled"}>−</button>
        <input class="val" ${editable ? "" : "readonly"} value="${this._value}">
        <button class="btn inc" ${increasable ? "" : "disabled"}>+</button>
      </div>`;
    const input = this.shadowRoot.querySelector(".val");
    const onStep = (dir) => { emit(this, "step", { step: dir * step }); };
    this.shadowRoot.querySelector(".dec").addEventListener("click", () => onStep(-1));
    this.shadowRoot.querySelector(".inc").addEventListener("click", () => onStep(1));
    input.addEventListener("change", () => { this._value = input.value; this._internalWrite = true; this.setAttribute("value", String(this._value)); this._internalWrite = false; emit(this, "value-change", { value: input.value }); });
  }
}
define("sui-stepper", SuiStepper);
