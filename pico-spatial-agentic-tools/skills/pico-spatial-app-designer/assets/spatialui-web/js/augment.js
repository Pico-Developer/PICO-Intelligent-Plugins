/* Augment — a window-attached ornament matching SpatialUI foundation Augment. */
import { define, Dimension } from "./base.js";
import { SuiOverlayElement, overlayCss } from "./overlay.js";
import { computeAugmentPosition, parseNormalizedPoint } from "./overlay-position.js";

export class SuiAugment extends SuiOverlayElement {
  static get observedAttributes() {
    return [
      "for", "anchor", "alignment", "offset-x", "offset-y", "offset-z",
      "rotation-x", "rotation-y", "rotation-z", "corner-radius",
      "enable-material-background", "focusable", "size-behavior", "window-size-behavior",
      "clipping-enabled", "viewport-padding", "hidden",
    ];
  }

  render() {
    const materialEnabled = !this.hasAttribute("enable-material-background")
      || this.bool("enable-material-background");
    const focusable = !this.hasAttribute("focusable") || this.bool("focusable");
    const radius = Math.max(0, this.num("corner-radius", Dimension.RadiusLarge));
    const alignment = parseNormalizedPoint(this.attr("alignment", "bottom-center"));
    this.style.setProperty("--sui-overlay-origin-x", alignment.x * 100 + "%");
    this.style.setProperty("--sui-overlay-origin-y", alignment.y * 100 + "%");
    this.shadowRoot.innerHTML = [
      "<style>",
      overlayCss,
      ".surface{width:max-content;height:max-content;max-width:none;max-height:none;",
      "border-radius:", radius, "px;}</style>",
      '<div class="surface ', materialEnabled ? "material-regular" : "material-none", '" ',
      'part="surface" role="region" ', focusable ? 'tabindex="-1"' : "inert", ">",
      "<slot></slot></div>",
    ].join("");
  }

  prepareSurface(anchor, surface) {
    const behavior = this.attr(
      "window-size-behavior",
      this.attr("size-behavior", "adaptive"),
    ).toLowerCase();
    const rect = anchor.getBoundingClientRect();
    surface.style.width = behavior === "match-container-width" ? rect.width + "px" : "max-content";
    surface.style.height = behavior === "match-container-height" ? rect.height + "px" : "max-content";
  }

  calculatePosition(anchorRect, contentSize) {
    return computeAugmentPosition(
      anchorRect,
      contentSize,
      parseNormalizedPoint(this.attr("anchor", "top-front"), "top-front"),
      parseNormalizedPoint(this.attr("alignment", "bottom-center"), "bottom-center"),
      this.offset(),
    );
  }
}

define("sui-augment", SuiAugment);
