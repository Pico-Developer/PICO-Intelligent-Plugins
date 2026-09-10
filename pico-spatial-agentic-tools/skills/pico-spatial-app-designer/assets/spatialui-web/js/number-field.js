/*
 * NumberField — mirrors NumberField.kt.
 * Default height 40, width 152 (min 100 / small 80).
 * Kotlin default colors (defaultNumberFieldColors):
 *   container=fillTertiary, focused=fillSecondary, text=labelPrimary,
 *   error=error, +/- btn container=fillLight, content=inherited (labelPrimary).
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

export class SuiNumberField extends SuiElement {
  static get observedAttributes() { return ["value", "min", "max", "step", "size", "disabled", "width", "error", "container-color", "text-color", "focus-color", "button-color"]; }
  attributeChangedCallback(name) {
    if (name === "value" && this._internalWrite) return;
    super.attributeChangedCallback(name);
  }
  render() {
    const disabled = this.bool("disabled");
    const small = this.attr("size", "default").toLowerCase() === "small";
    const h = small ? 32 : 40;
    const width = this.num("width", 152);
    const min = this.num("min", -Infinity), max = this.num("max", Infinity), step = this.num("step", 1);
    const isError = this.bool("error");
    // `value` is the single source of truth: re-sync on every render so an
    // external (controlled) update is reflected, keeping the last committed
    // value when the attribute is absent.
    this._value = this.hasAttribute("value") ? this.num("value", 0) : (this._value ?? 0);
    const clamp = (v) => Math.max(min, Math.min(max, v));
    const containerC = this.attr("container-color", themeColor("fillTertiary"));
    const textC = this.attr("text-color", themeColor("labelPrimary"));
    const focusC = isError ? themeColor("error") : this.attr("focus-color", themeColor("fillSecondary"));
    const btnBg = this.attr("button-color", themeColor("fillLight"));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .field { display:flex; align-items:center; width:${width}px; height:${h}px; padding:4px;
          background:${containerC}; border-radius:10px; box-sizing:border-box;
          border:1px solid transparent; transition:border-color .12s ease; caret-color:${themeColor("fillPrimary")}; }
        .field:focus-within { border-color:${focusC}; }
        .field.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .btn { width:44px; height:${h - 8}px; border:none; background:transparent; cursor:pointer;
          color:${textC}; font-size:20px; line-height:1; border-radius:8px;
          display:inline-flex; align-items:center; justify-content:center; transition:background-color .12s; }
        .btn:hover { background:${btnBg}; }
        .val { flex:1; text-align:center; background:transparent; border:none; outline:none;
          color:${textC}; font-size:16px; font-weight:500; font-family:inherit; width:100%; }
      </style>
      <div class="field ${disabled ? "sui-disabled" : ""}">
        <button class="btn dec">−</button>
        <input class="val" inputmode="numeric" value="${this._value}">
        <button class="btn inc">+</button>
      </div>`;
    const input = this.shadowRoot.querySelector(".val");
    const update = (v) => { this._value = clamp(v); input.value = this._value; this._internalWrite = true; this.setAttribute("value", String(this._value)); this._internalWrite = false; emit(this, "value-change", { value: this._value }); };
    this.shadowRoot.querySelector(".dec").addEventListener("click", () => update(this._value - step));
    this.shadowRoot.querySelector(".inc").addEventListener("click", () => update(this._value + step));
    input.addEventListener("change", () => update(parseFloat(input.value) || 0));
  }
}
define("sui-number-field", SuiNumberField);
