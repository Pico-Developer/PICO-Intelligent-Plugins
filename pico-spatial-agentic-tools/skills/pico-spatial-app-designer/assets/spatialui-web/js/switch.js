/*
 * Switch — mirrors Switch.kt.
 * Track 32x20 (r=10), thumb 16, checked-circle padding 2, thumb travel = 32-16-2*2 = 10.
 * checkedTrack=interaction, uncheckedTrack=fillTertiary, thumb=labelPrimaryLight.
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

export class SuiSwitch extends SuiElement {
  static get observedAttributes() { return ["checked", "disabled", "track-color", "thumb-color", "checked-track-color"]; }
  render() {
    const checked = this.bool("checked");
    const disabled = this.bool("disabled");
    const W = 32, H = 20, PAD = 2, THUMB = 16;
    const travel = W - THUMB - PAD * 2;
    const trackOn = this.attr("checked-track-color", themeColor("interaction"));
    const trackOff = this.attr("track-color", themeColor("fillTertiary"));
    const thumbC = this.attr("thumb-color", themeColor("labelPrimaryLight"));
    const track = checked ? trackOn : trackOff;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .wrap { padding:8px 4px; display:inline-flex; cursor:pointer; }
        .wrap.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .track { position:relative; width:${W}px; height:${H}px; border-radius:${H / 2}px;
                 background:${track}; transition:background-color .18s ease; }
        .thumb { position:absolute; top:${PAD}px; left:${PAD}px; width:${THUMB}px; height:${THUMB}px;
                 border-radius:50%; background:${thumbC};
                 transform:translateX(${checked ? travel : 0}px); transition:transform .18s cubic-bezier(.2,.8,.2,1);
                 box-shadow:${checked ? "none" : "0 1px 4px rgba(0,0,0,0.16)"}; }
      </style>
      <div class="wrap ${disabled ? "sui-disabled" : ""}" role="switch" aria-checked="${checked}">
        <div class="track"><div class="thumb"></div></div>
      </div>`;
    this.shadowRoot.querySelector(".wrap").addEventListener("click", () => {
      if (disabled) return;
      const next = !checked;
      this.toggleAttribute("checked", next);
      emit(this, "checked-change", { checked: next });
    });
  }
}
define("sui-switch", SuiSwitch);
