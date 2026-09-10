/* SpatialPopup — an anchor-relative, dismissible floating spatial surface. */
import { define, Dimension } from "./base.js";
import { SuiOverlayElement, overlayCss } from "./overlay.js";
import { computePopupPosition } from "./overlay-position.js";

export class SuiSpatialPopup extends SuiOverlayElement {
  static get observedAttributes() {
    return [
      "for", "horizontal-placement", "vertical-placement", "offset-x",
      "offset-y", "offset-z", "rotation-x", "rotation-y", "rotation-z",
      "corner-radius", "default-min-width", "default-min-height",
      "disable-material-background", "focusable", "dismiss-on-click-outside",
      "dismiss-on-escape", "clipping-enabled", "viewport-padding", "hidden",
    ];
  }

  render() {
    const materialDisabled = this.bool("disable-material-background");
    const focusable = !this.hasAttribute("focusable") || this.bool("focusable");
    const radius = Math.max(0, this.num("corner-radius", Dimension.RadiusExtraLarge));
    const minWidth = Math.max(0, this.num("default-min-width", Dimension.WidthMedium));
    const minHeight = Math.max(0, this.num("default-min-height", Dimension.HeightMin));
    this.shadowRoot.innerHTML = [
      "<style>",
      overlayCss,
      ".surface{min-width:", minWidth, "px;min-height:", minHeight,
      "px;width:max-content;height:max-content;max-width:none;max-height:none;border-radius:",
      radius, "px;}</style>",
      '<div class="surface ', materialDisabled ? "material-none" : "material-thick", '" ',
      'part="surface" role="dialog" aria-modal="false" ',
      focusable ? 'tabindex="-1"' : "inert", "><slot></slot></div>",
    ].join("");
  }

  shouldDismissOnOutsidePointer() {
    return !this.hasAttribute("dismiss-on-click-outside")
      || this.bool("dismiss-on-click-outside");
  }

  shouldDismissOnEscape() {
    return !this.hasAttribute("dismiss-on-escape") || this.bool("dismiss-on-escape");
  }

  calculatePosition(anchorRect, contentSize, anchor) {
    const direction = getComputedStyle(anchor).direction === "rtl" ? "rtl" : "ltr";
    return computePopupPosition(
      anchorRect,
      contentSize,
      this.attr("horizontal-placement", "align-start").toLowerCase(),
      this.attr("vertical-placement", "above").toLowerCase(),
      this.offset(Dimension.GapSmall),
      direction,
    );
  }
}

define("sui-spatial-popup", SuiSpatialPopup);
