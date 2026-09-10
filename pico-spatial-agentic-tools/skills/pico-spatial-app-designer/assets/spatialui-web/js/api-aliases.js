/* Explicit Custom Element names for Kotlin composables represented by shared Web components. */
import { SuiElement, define } from "./base.js";

class SuiAliasElement extends SuiElement {
  static targetTag = "div";
  static forcedAttributes = {};
  static get observedAttributes() { return ["checked", "state", "disabled", "label", "size", "value", "placeholder", "width", "color", "thickness"]; }

  render() {
    const target = document.createElement(this.constructor.targetTag);
    for (const attribute of this.attributes) {
      if (attribute.name !== "style" && attribute.name !== "class") {
        target.setAttribute(attribute.name, attribute.value);
      }
    }
    for (const [name, value] of Object.entries(this.constructor.forcedAttributes)) {
      target.setAttribute(name, value);
    }
    target.innerHTML = "<slot></slot>";
    this.shadowRoot.innerHTML = "<style>:host{display:inline-flex}</style>";
    this.shadowRoot.append(target);
  }
}

class SuiTriStateCheckbox extends SuiAliasElement { static targetTag = "sui-checkbox"; }
class SuiButtonChip extends SuiAliasElement { static targetTag = "sui-chip"; }
class SuiToggleableChip extends SuiAliasElement {
  static targetTag = "sui-chip";
  static forcedAttributes = { toggle: "" };
}
class SuiRemovableChip extends SuiAliasElement {
  static targetTag = "sui-chip";
  static forcedAttributes = { removable: "" };
}
class SuiTextArea extends SuiAliasElement {
  static targetTag = "sui-text-field";
  static forcedAttributes = { multiline: "" };
}
class SuiHorizontalDivider extends SuiAliasElement {
  static targetTag = "sui-divider";
  static forcedAttributes = { orientation: "horizontal" };
}
class SuiVerticalDivider extends SuiAliasElement {
  static targetTag = "sui-divider";
  static forcedAttributes = { orientation: "vertical" };
}

define("sui-tri-state-checkbox", SuiTriStateCheckbox);
define("sui-button-chip", SuiButtonChip);
define("sui-toggleable-chip", SuiToggleableChip);
define("sui-removable-chip", SuiRemovableChip);
define("sui-text-area", SuiTextArea);
define("sui-horizontal-divider", SuiHorizontalDivider);
define("sui-vertical-divider", SuiVerticalDivider);
