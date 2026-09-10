/* Shared top-layer lifecycle for SpatialUI floating window components. */
import { SuiElement, emit } from "./base.js";
import { clampPosition } from "./overlay-position.js";

let nextOverlayLayer = 0;

export const overlayCss = [
  ":host {",
  "position:fixed;inset:auto;top:0;left:0;display:block;width:max-content;margin:0;padding:0;",
  "border:0;overflow:visible;color:inherit;background:transparent;font-family:inherit;",
  "pointer-events:auto;z-index:var(--sui-overlay-z-index,1000);",
  "transform:translate3d(var(--sui-overlay-x,0px),var(--sui-overlay-y,0px),var(--sui-overlay-z,0px))",
  "rotateX(var(--sui-overlay-rotate-x,0deg)) rotateY(var(--sui-overlay-rotate-y,0deg))",
  "rotateZ(var(--sui-overlay-rotate-z,0deg));",
  "transform-origin:var(--sui-overlay-origin-x,50%) var(--sui-overlay-origin-y,50%);}",
  ":host([hidden]){display:none!important;}",
  "*,*::before,*::after{box-sizing:border-box;}",
  ".surface{position:relative;display:flex;color:var(--sui-label-primary);",
  "box-sizing:border-box;overflow:hidden;isolation:isolate;",
  "box-shadow:0 18px 54px rgba(0,0,0,.24),inset 0 0 0 1px ",
  "var(--sui-overlay-border,rgba(255,255,255,.28));}",
  ".surface.material-regular{background:var(--Background-MaterialRegular,rgba(255,255,255,.34));",
  "backdrop-filter:blur(50px) saturate(1.18);-webkit-backdrop-filter:blur(50px) saturate(1.18);}",
  ".surface.material-thick{background:var(--Background-MaterialThick,rgba(255,255,255,.58));",
  "backdrop-filter:blur(64px) saturate(1.22);-webkit-backdrop-filter:blur(64px) saturate(1.22);}",
  ".surface.material-none{background:transparent;box-shadow:none;}",
  "::slotted(*){box-sizing:border-box;}",
].join("");

function numericAttribute(element, name, fallback = 0) {
  const value = Number(element.getAttribute(name));
  return Number.isFinite(value) ? value : fallback;
}

/** Base class used by sui-augment and sui-spatial-popup. */
export class SuiOverlayElement extends SuiElement {
  constructor() {
    super();
    this._anchorElement = null;
    this._positionFrame = 0;
    this._overlayCleanup = [];
  }

  get anchorElement() { return this._anchorElement; }

  set anchorElement(value) {
    if (value !== null && !(value instanceof Element)) {
      throw new TypeError("anchorElement must be an Element or null");
    }
    this._anchorElement = value;
    if (this.isConnected) this._activateOverlay();
  }

  connectedCallback() {
    super.connectedCallback();
    this.setAttribute("popover", "manual");
    this.style.setProperty("--sui-overlay-z-index", String(1000 + nextOverlayLayer++));
    this._activateOverlay();
  }

  disconnectedCallback() {
    this._deactivateOverlay();
    try { this.hidePopover?.(); } catch (_) { /* Already detached or unsupported. */ }
  }

  attributeChangedCallback(name, oldValue, newValue) {
    super.attributeChangedCallback(name, oldValue, newValue);
    if (oldValue !== newValue && this.isConnected) this._activateOverlay();
  }

  resolveAnchor() {
    if (this._anchorElement?.isConnected) return this._anchorElement;
    const id = this.getAttribute("for");
    if (id) {
      const root = this.getRootNode();
      return root.getElementById?.(id) || this.ownerDocument?.getElementById(id) || null;
    }
    return this.previousElementSibling || this.parentElement;
  }

  shouldDismissOnOutsidePointer() { return false; }
  shouldDismissOnEscape() { return false; }

  requestDismiss(reason, sourceEvent) {
    emit(this, "dismiss-request", { reason, sourceEvent });
  }

  _deactivateOverlay() {
    if (this._positionFrame) cancelAnimationFrame(this._positionFrame);
    this._positionFrame = 0;
    this._overlayCleanup.splice(0).forEach((cleanup) => cleanup());
  }

  _activateOverlay() {
    this._deactivateOverlay();
    if (this.hidden) return;
    try {
      if (!this.matches(":popover-open")) this.showPopover?.();
    } catch (_) { /* Fixed-position fallback. */ }

    const anchor = this.resolveAnchor();
    const surface = this.shadowRoot.querySelector(".surface");
    if (!anchor || !surface) {
      this.style.visibility = "hidden";
      const mutationObserver = new MutationObserver(() => {
        if (this.resolveAnchor()) this._activateOverlay();
      });
      mutationObserver.observe(this.ownerDocument.documentElement, { childList: true, subtree: true });
      this._overlayCleanup.push(() => mutationObserver.disconnect());
      return;
    }

    this.style.visibility = "hidden";
    const schedule = () => {
      if (this._positionFrame) return;
      this._positionFrame = requestAnimationFrame(() => {
        this._positionFrame = 0;
        this._updatePosition(anchor, surface);
      });
    };

    if (typeof ResizeObserver !== "undefined") {
      const resizeObserver = new ResizeObserver(schedule);
      resizeObserver.observe(anchor);
      resizeObserver.observe(surface);
      this._overlayCleanup.push(() => resizeObserver.disconnect());
    }
    window.addEventListener("resize", schedule);
    window.addEventListener("scroll", schedule, true);
    this._overlayCleanup.push(() => window.removeEventListener("resize", schedule));
    this._overlayCleanup.push(() => window.removeEventListener("scroll", schedule, true));

    if (this.shouldDismissOnOutsidePointer()) {
      const onPointerDown = (event) => {
        const path = event.composedPath();
        const insideNestedOverlay = path.some((node) =>
          node instanceof SuiOverlayElement && this.contains(node));
        if (!path.includes(this) && !path.includes(anchor) && !insideNestedOverlay) {
          this.requestDismiss("outside-pointer", event);
        }
      };
      this.ownerDocument.addEventListener("pointerdown", onPointerDown, true);
      this._overlayCleanup.push(() =>
        this.ownerDocument.removeEventListener("pointerdown", onPointerDown, true));
    }

    if (this.shouldDismissOnEscape()) {
      const onKeyDown = (event) => {
        if (event.key === "Escape" && !event.defaultPrevented) {
          event.preventDefault();
          this.requestDismiss("escape-key", event);
        }
      };
      this.ownerDocument.addEventListener("keydown", onKeyDown, true);
      this._overlayCleanup.push(() =>
        this.ownerDocument.removeEventListener("keydown", onKeyDown, true));
    }
    schedule();
  }

  _updatePosition(anchor, surface) {
    if (!this.isConnected || !anchor.isConnected) {
      this.style.visibility = "hidden";
      return;
    }
    this.prepareSurface(anchor, surface);
    const anchorRect = anchor.getBoundingClientRect();
    const contentSize = { width: surface.offsetWidth, height: surface.offsetHeight };
    let position = this.calculatePosition(anchorRect, contentSize, anchor);
    if (this.bool("clipping-enabled")) {
      position = clampPosition(
        position,
        contentSize,
        { width: window.innerWidth, height: window.innerHeight },
        numericAttribute(this, "viewport-padding", 0),
      );
    }
    this.style.setProperty("--sui-overlay-x", position.x + "px");
    this.style.setProperty("--sui-overlay-y", position.y + "px");
    this.style.setProperty("--sui-overlay-z", (position.z || 0) + "px");
    this.style.setProperty(
      "--sui-overlay-rotate-x",
      numericAttribute(this, "rotation-x", 0) + "deg",
    );
    this.style.setProperty(
      "--sui-overlay-rotate-y",
      numericAttribute(this, "rotation-y", 0) + "deg",
    );
    this.style.setProperty(
      "--sui-overlay-rotate-z",
      numericAttribute(this, "rotation-z", 0) + "deg",
    );
    this.style.visibility = "visible";
  }

  prepareSurface() {}
  calculatePosition() { return { x: 0, y: 0, z: 0 }; }

  offset(defaultY = 0) {
    return {
      x: numericAttribute(this, "offset-x", 0),
      y: numericAttribute(this, "offset-y", defaultY),
      z: numericAttribute(this, "offset-z", 0),
    };
  }
}
