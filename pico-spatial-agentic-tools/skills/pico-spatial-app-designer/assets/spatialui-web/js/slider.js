/*
 * Slider — mirrors Slider.kt / Figma "Slider" component set.
 * Sizes only govern thickness (track height / knob dot / thumb area):
 *   Small   8 / 18 / 32
 *   Regular 24 / 18 / 32
 *   Max     48 / 32 / 48
 * Length is independent of size (Figma's 240/360 artboards are just example
 * frames). Width defaults to 240px and is overridable via the `width` attribute
 * ("240", "320px", "100%", …) so sliders align regardless of size.
 * Colors are driven by PicoTheme (fillTertiary / fillSecondary / labelPrimaryLight)
 * and may be overridden per-instance with track-color / progress-color / thumb-color.
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

const SPECS = {
  small: { track: 8, thumb: 18, area: 32 },
  regular: { track: 24, thumb: 18, area: 32 },
  max: { track: 48, thumb: 32, area: 48 },
};

const DEFAULT_WIDTH = 240;

export class SuiSlider extends SuiElement {
  static get observedAttributes() { return ["value", "min", "max", "size", "width", "disabled", "track-color", "progress-color", "thumb-color"]; }
  attributeChangedCallback(name) {
    if (name === "value" && this._internalWrite) return;
    super.attributeChangedCallback(name);
  }
  render() {
    const s = SPECS[this.attr("size", "regular").toLowerCase()] || SPECS.regular;
    const disabled = this.bool("disabled");
    const min = this.num("min", 0), max = this.num("max", 1);
    const rawW = this.attr("width");
    const width = rawW == null ? `${DEFAULT_WIDTH}px` : (/^\d+$/.test(rawW) ? `${rawW}px` : rawW);
    // `value` is the single source of truth: re-sync on every render so an
    // external (controlled) update is reflected, keeping the last committed
    // value when the attribute is absent.
    this._value = this.hasAttribute("value") ? this.num("value", 0) : (this._value ?? 0);

    const trackColor = this.attr("track-color", themeColor("fillTertiary"));
    const progressColor = this.attr("progress-color", themeColor("fillSecondary"));
    const thumbColor = this.attr("thumb-color", themeColor("labelPrimaryLight"));

    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .slider { position:relative; width:${width}; height:${s.area}px; display:flex; align-items:center;
          cursor:pointer; touch-action:none; }
        .slider.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .track, .progress { position:absolute; top:50%; transform:translateY(-50%);
          height:${s.track}px; border-radius:${s.track / 2}px; }
        .track { left:0; right:0; background:${trackColor}; }
        .progress { left:0; width:0;
          background:${progressColor}; overflow:hidden; }
        .progress::after { content:""; position:absolute; inset:0; background:transparent;
          transition:background-color .12s ease; pointer-events:none; }
        .slider:hover .progress::after, .slider.dragging .progress::after {
          background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .thumb { position:absolute; top:50%; transform:translateY(-50%); z-index:1;
          width:${s.thumb}px; height:${s.thumb}px; border-radius:50%;
          background:${thumbColor}; box-shadow:0 0 4px 0 rgba(0,0,0,0.12); }
      </style>
      <div class="slider ${disabled ? "sui-disabled" : ""}" role="slider" tabindex="0" aria-valuenow="${this._value}" aria-valuemin="${min}" aria-valuemax="${max}">
        <div class="track"></div>
        <div class="progress"></div>
        <div class="thumb"></div>
      </div>`;

    const el = this.shadowRoot.querySelector(".slider");
    const progress = this.shadowRoot.querySelector(".progress");
    const thumb = this.shadowRoot.querySelector(".thumb");

    // Position the thumb/progress from the current value — no DOM rebuild.
    // Measure the actual rendered width so percentage / responsive widths work.
    // Match the native/Figma geometry: the invisible thumb area travels inside
    // the component, while the visible knob is centered within that area. The
    // rounded progress cap extends behind the knob so no square cut is exposed.
    const paint = () => {
      const len = el.getBoundingClientRect().width || DEFAULT_WIDTH;
      const travel = Math.max(0, len - s.area);
      const range = max - min;
      const frac = range === 0 ? 0 : Math.max(0, Math.min(1, (this._value - min) / range));
      const thumbAreaLeft = frac * travel;
      const progressWidth = Math.min(len, s.track + thumbAreaLeft);
      progress.style.width = `${progressWidth}px`;
      thumb.style.left = `${thumbAreaLeft + (s.area - s.thumb) / 2}px`;
      el.setAttribute("aria-valuenow", String(this._value));
    };
    paint();

    if (disabled) return;

    const setFromX = (clientX) => {
      const rect = el.getBoundingClientRect();
      const travel = Math.max(1, rect.width - s.area);
      const frac = Math.max(
        0,
        Math.min(1, (clientX - rect.left - s.area / 2) / travel),
      );
      this._value = min + frac * (max - min);
      this._internalWrite = true;
      this.setAttribute("value", String(this._value));
      this._internalWrite = false;
      paint();
      emit(this, "value-change", { value: this._value });
    };

    const move = (ev) => setFromX(ev.clientX);
    const up = (ev) => {
      el.classList.remove("dragging");
      el.releasePointerCapture?.(ev.pointerId);
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
    el.addEventListener("pointerdown", (ev) => {
      ev.preventDefault();
      el.classList.add("dragging");
      el.setPointerCapture?.(ev.pointerId);
      setFromX(ev.clientX);
      window.addEventListener("pointermove", move);
      window.addEventListener("pointerup", up);
    });
    // Keyboard support.
    el.addEventListener("keydown", (ev) => {
      const stepPx = (max - min) / 100;
      if (ev.key === "ArrowRight" || ev.key === "ArrowUp") { this._value = Math.min(max, this._value + stepPx); }
      else if (ev.key === "ArrowLeft" || ev.key === "ArrowDown") { this._value = Math.max(min, this._value - stepPx); }
      else return;
      ev.preventDefault();
      this._internalWrite = true;
      this.setAttribute("value", String(this._value));
      this._internalWrite = false;
      paint();
      emit(this, "value-change", { value: this._value });
    });
  }
}
define("sui-slider", SuiSlider);
