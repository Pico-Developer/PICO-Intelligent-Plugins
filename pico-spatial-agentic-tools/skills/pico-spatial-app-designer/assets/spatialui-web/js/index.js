/*
 * SpatialUI Web — barrel module.
 * Importing this file registers every SpatialUI custom element and installs
 * the PicoTheme (default vibrant/glass color scheme) on :root, exactly as
 * PicoTheme() in Compose installs the ambient ColorScheme via CompositionLocal.
 */
import { PicoTheme } from "./tokens.js";

import "./text.js";
import "./icon.js";
import "./button.js";
import "./icon-button.js";
import "./toggle-button.js";
import "./switch.js";
import "./checkbox.js";
import "./badge.js";
import "./chip.js";
import "./slider.js";
import "./progress.js";
import "./divider.js";
import "./segment-control.js";
import "./tab-bar.js";
import "./text-field.js";
import "./search-field.js";
import "./number-field.js";
import "./stepper.js";
import "./link.js";
import "./list-item.js";
import "./page-control.js";
import "./option.js";
import "./side-navigation.js";
import "./title-bar.js";
import "./scroll-indicator.js";
import "./wheel-picker.js";
import "./date-picker.js";
import "./augment.js";
import "./spatial-popup.js";
import "./api-aliases.js";
import "./advanced-controls.js";
import "./composition-items.js";
import "./date-range-picker.js";
import "./menu.js";
import "./dialogs.js";
import "./feedback.js";
import "./window-components.js";

// Install the default (vibrant/glass) theme on documentElement. Consumers can
// override any subtree by calling PicoTheme.install({scheme, colorScheme}, el)
// or by setting --sui-* CSS variables on an ancestor element.
PicoTheme.install({ scheme: "vibrant" });

/** Expose PicoTheme on window for console / non-module usage. */
if (typeof window !== "undefined") window.PicoTheme = PicoTheme;

/** Catalog used by the preview page. */
export const COMPONENTS = [
  "sui-text", "sui-icon", "sui-button", "sui-icon-button", "sui-toggle-button",
  "sui-switch", "sui-checkbox", "sui-badge", "sui-dot-badge", "sui-number-badge",
  "sui-chip", "sui-slider", "sui-linear-progress", "sui-circular-progress",
  "sui-divider", "sui-segment-control", "sui-tab-bar", "sui-text-field", "sui-search-field",
  "sui-number-field", "sui-stepper", "sui-link", "sui-list-item",
  "sui-page-control", "sui-option", "sui-side-navigation", "sui-title-bar",
  "sui-scroll-indicator", "sui-wheel-picker", "sui-timepicker", "sui-date-picker",
  "sui-augment", "sui-spatial-popup",
  "sui-tri-state-checkbox", "sui-button-chip", "sui-toggleable-chip", "sui-removable-chip",
  "sui-text-area", "sui-horizontal-divider", "sui-vertical-divider",
  "sui-toggle-icon-button", "sui-symbol-slider", "sui-segment-slider",
  "sui-symbolic-circular-progress", "sui-progress-page-control", "sui-stereo-image",
  "sui-segment-item", "sui-side-navigation-section", "sui-side-navigation-item",
  "sui-basic-scroll-indicator", "sui-date-range-picker",
  "sui-menu", "sui-sub-menu", "sui-menu-item", "sui-basic-menu-item",
  "sui-basic-alert-dialog", "sui-alert-dialog", "sui-date-picker-dialog",
  "sui-basic-sheet", "sui-sheet", "sui-head-image-sheet",
  "sui-snackbar-host", "sui-coachmark", "sui-simple-coachmark",
  "sui-rich-coachmark", "sui-image-coachmark", "sui-toolbar", "sui-subwindow",
];

export { PicoTheme };
