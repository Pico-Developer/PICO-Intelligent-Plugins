/* AlertDialog, DatePickerDialog and Sheet families. */
import { SuiElement, define, emit, escapeHtml, themeColor } from "./base.js";

class SuiModalSurface extends SuiElement {
  constructor() {
    super();
    this._cleanup = [];
  }

  connectedCallback() {
    super.connectedCallback();
    this.setAttribute("popover", "manual");
    this.activate();
  }

  disconnectedCallback() {
    this.deactivate();
    try { this.hidePopover?.(); } catch (_) { /* Already detached or unsupported. */ }
  }

  attributeChangedCallback(name, oldValue, newValue) {
    super.attributeChangedCallback(name, oldValue, newValue);
    if (oldValue !== newValue && this.isConnected) queueMicrotask(() => this.activate());
  }

  deactivate() { this._cleanup.splice(0).forEach((cleanup) => cleanup()); }

  activate() {
    this.deactivate();
    if (this.hidden) return;
    try {
      if (!this.matches(":popover-open")) this.showPopover?.();
    } catch (_) { /* Fixed-position fallback. */ }
    const backdrop = this.shadowRoot.querySelector(".backdrop");
    if (!backdrop) return;
    if (this.dismissOnOutside()) {
      const outside = (event) => {
        if (event.target === backdrop) this.requestDismiss("outside-pointer", event);
      };
      backdrop.addEventListener("pointerdown", outside);
      this._cleanup.push(() => backdrop.removeEventListener("pointerdown", outside));
    }
    if (this.dismissOnEscape()) {
      const escape = (event) => {
        if (event.key === "Escape" && !event.defaultPrevented) {
          event.preventDefault();
          this.requestDismiss("escape-key", event);
        }
      };
      this.ownerDocument.addEventListener("keydown", escape, true);
      this._cleanup.push(() => this.ownerDocument.removeEventListener("keydown", escape, true));
    }
    this.shadowRoot.querySelector(".panel")?.focus({ preventScroll: true });
  }

  dismissOnOutside() { return this.bool("dismiss-on-click-outside"); }
  dismissOnEscape() { return this.bool("dismiss-on-escape"); }
  requestDismiss(reason, sourceEvent) { emit(this, "dismiss-request", { reason, sourceEvent }); }

  modalCss(radius, material = "thick") {
    const background = material === "thickest"
      ? "var(--Background-MaterialThickest,rgba(255,255,255,.72))"
      : "var(--Background-MaterialThick,rgba(255,255,255,.58))";
    return [
      ":host{position:fixed;inset:0;display:block;width:auto;height:auto;margin:0;padding:0;border:0;",
      "background:transparent;z-index:var(--sui-modal-z-index,1200);font-family:inherit}",
      ":host([hidden]){display:none!important}.backdrop{position:absolute;inset:0;display:grid;place-items:center;padding:32px;",
      "background:rgba(0,0,0,.28);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}",
      ".panel{max-width:calc(100vw - 64px);max-height:calc(100vh - 64px);overflow:auto;outline:none;color:",
      themeColor("labelPrimary"), ";background:", background, ";backdrop-filter:blur(64px) saturate(1.2);",
      "-webkit-backdrop-filter:blur(64px) saturate(1.2);border-radius:", radius,
      "px;box-shadow:0 30px 90px rgba(0,0,0,.38),inset 0 0 0 1px rgba(255,255,255,.3)}",
      "*,*::before,*::after{box-sizing:border-box}",
    ].join("");
  }
}

export class SuiBasicAlertDialog extends SuiModalSurface {
  static get observedAttributes() { return ["corner-radius", "dismiss-on-click-outside", "dismiss-on-escape", "hidden"]; }
  dismissOnOutside() { return !this.hasAttribute("dismiss-on-click-outside") || this.bool("dismiss-on-click-outside"); }
  dismissOnEscape() { return !this.hasAttribute("dismiss-on-escape") || this.bool("dismiss-on-escape"); }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    this.shadowRoot.innerHTML = "<style>" + this.modalCss(radius) +
      "</style><div class=\"backdrop\"><div class=\"panel\" part=\"surface\" role=\"alertdialog\" aria-modal=\"true\" tabindex=\"-1\"><slot></slot></div></div>";
  }
}
define("sui-basic-alert-dialog", SuiBasicAlertDialog);

export class SuiAlertDialog extends SuiBasicAlertDialog {
  static get observedAttributes() {
    return [...SuiBasicAlertDialog.observedAttributes, "title", "message", "icon", "orientation"];
  }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    const vertical = this.attr("orientation", "horizontal") === "vertical";
    const width = vertical ? 360 : 480;
    this.shadowRoot.innerHTML = [
      "<style>", this.modalCss(radius), ".panel{width:", width, "px;min-height:184px;padding:32px;display:flex;flex-direction:column}",
      ".head{display:flex;align-items:center;justify-content:", vertical ? "center" : "flex-start", ";flex-direction:", vertical ? "column" : "row",
      ";gap:12px;padding-bottom:24px}.icon{font-size:28px}.title{font-size:24px;line-height:30px;font-weight:700}.content{flex:1;color:",
      themeColor("labelSecondary"), ";font-size:16px;line-height:24px}.buttons{display:flex;justify-content:flex-end;gap:8px;padding-top:24px}</style>",
      '<div class="backdrop"><div class="panel" part="surface" role="alertdialog" aria-modal="true" tabindex="-1"><div class="head"><span class="icon"><slot name="icon">',
      escapeHtml(this.attr("icon", "")), '</slot></span><span class="title"><slot name="title">', escapeHtml(this.attr("title", "")),
      '</slot></span></div><div class="content"><slot>', escapeHtml(this.attr("message", "")),
      '</slot></div><div class="buttons"><slot name="buttons"></slot></div></div></div>',
    ].join("");
  }
}
define("sui-alert-dialog", SuiAlertDialog);

export class SuiDatePickerDialog extends SuiModalSurface {
  static get observedAttributes() { return ["title", "corner-radius", "dismiss-on-click-outside", "dismiss-on-escape", "hidden"]; }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 16));
    this.shadowRoot.innerHTML = [
      "<style>", this.modalCss(radius, "thickest"), ".panel{width:480px}.title{height:96px;padding:0 32px;display:flex;align-items:center;",
      "font-size:24px;line-height:30px;font-weight:700;color:", themeColor("labelSecondary"), "}.content{padding:0 32px 40px}",
      ".buttons{display:flex;justify-content:flex-end;gap:8px;padding:0 32px 32px}</style>",
      '<div class="backdrop"><div class="panel" part="surface" role="dialog" aria-modal="true" tabindex="-1"><div class="title"><slot name="title">',
      escapeHtml(this.attr("title", "")), '</slot></div><div class="content"><slot></slot></div><div class="buttons"><slot name="negative"></slot><slot name="positive"></slot></div></div></div>',
    ].join("");
  }
}
define("sui-date-picker-dialog", SuiDatePickerDialog);

export class SuiBasicSheet extends SuiModalSurface {
  static get observedAttributes() { return ["corner-radius", "dismiss-on-click-outside", "dismiss-on-escape", "hidden"]; }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    this.shadowRoot.innerHTML = "<style>" + this.modalCss(radius) +
      ".panel{width:480px;min-width:360px;min-height:184px}</style><div class=\"backdrop\"><div class=\"panel\" part=\"surface\" role=\"dialog\" aria-modal=\"true\" tabindex=\"-1\"><slot></slot></div></div>";
  }
}
define("sui-basic-sheet", SuiBasicSheet);

export class SuiSheet extends SuiBasicSheet {
  static get observedAttributes() { return [...SuiBasicSheet.observedAttributes, "title"]; }
  render() {
    const radius = Math.max(0, this.num("corner-radius", 20));
    this.shadowRoot.innerHTML = [
      "<style>", this.modalCss(radius), ".panel{width:480px;min-width:360px;min-height:184px}.bar{min-height:96px;padding:0 32px;display:grid;",
      "grid-template-columns:1fr auto 1fr;align-items:center}.leading{justify-self:start}.title{font-size:20px;line-height:26px;font-weight:600}.trailing{justify-self:end}",
      ".content{padding:0 32px 32px;color:", themeColor("labelSecondary"), "}.bottom{padding-top:24px}</style>",
      '<div class="backdrop"><div class="panel" part="surface" role="dialog" aria-modal="true" tabindex="-1"><div class="bar"><span class="leading"><slot name="leading"></slot></span><span class="title"><slot name="title">',
      escapeHtml(this.attr("title", "")), '</slot></span><span class="trailing"><slot name="trailing"></slot></span></div><div class="content"><slot></slot><div class="bottom"><slot name="bottom"></slot></div></div></div></div>',
    ].join("");
  }
}
define("sui-sheet", SuiSheet);

export class SuiHeadImageSheet extends SuiSheet {
  render() {
    super.render();
    const panel = this.shadowRoot.querySelector(".panel");
    const header = document.createElement("div");
    header.className = "header-image";
    header.innerHTML = '<slot name="header-image"></slot>';
    const style = document.createElement("style");
    style.textContent = ".header-image{position:relative;width:100%;overflow:hidden}.header-image slot::slotted(*){width:100%;display:block}";
    this.shadowRoot.append(style);
    panel.prepend(header);
  }
}
define("sui-head-image-sheet", SuiHeadImageSheet);
