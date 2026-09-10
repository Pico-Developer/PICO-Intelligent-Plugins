/*
 * TabBar — mirrors the PICO OS 7 Tab Bar specification.
 * Supports horizontal text/icon tabs, icon labels, vertical icon tabs,
 * badges, hover expansion, and an optional secondary tab row.
 * Icon slots use icon-N; the hover menu can override them with expanded-icon-N.
 *
 * Colors are driven by PicoTheme:
 *   - Material bar background = component-level glass variable
 *   - Active tab = fillPrimary / labelPrimaryLight
 *   - Inactive tab = dark label on the light material
 *   - Focus ring = interaction
 *   - Badge = error
 */
import { SuiElement, define, emit, themeColor, DISABLE_ALPHA } from "./base.js";

const DEFAULT_ICONS = ["◷", "♧", "◇", "▤", "▭", "⌕", "○"];

function list(value, preserveEmpty = false) {
  const values = (value || "").split(",").map((item) => item.trim()).slice(0, 7);
  return preserveEmpty ? values : values.filter(Boolean);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export class SuiTabBar extends SuiElement {
  static get observedAttributes() {
    return [
      "items", "icons", "badges", "selected-index", "type", "orientation",
      "show-labels", "expand-on-hover", "sub-items", "sub-selected-index",
      "disabled", "equal-width",
    ];
  }

  render() {
    const previousBar = this.shadowRoot.querySelector(".bar");
    const items = list(this.attr("items", "最近,通知,空间,文章,书库,搜索"));
    const icons = list(this.attr("icons", ""), true);
    const badges = list(this.attr("badges", ""), true);
    const subItems = list(this.attr("sub-items", ""));
    const type = this.attr("type", "icon").toLowerCase();
    const vertical = this.attr("orientation", "horizontal").toLowerCase() === "vertical";
    const showLabels = !vertical && type === "icon" && this.bool("show-labels");
    const expandOnHover = this.hasAttribute("expand-on-hover")
      ? this.bool("expand-on-hover")
      : !vertical && type === "icon" && !showLabels;
    const horizontalHoverLabels = !vertical && type === "icon" && expandOnHover;
    const verticalHoverPanel = vertical && expandOnHover;
    this._expanded = Boolean(
      expandOnHover && (
        this._expanded ||
        previousBar?.matches(":hover") ||
        previousBar?.matches(":focus-within")
      )
    );
    const equalWidth = this.bool("equal-width");
    const selected = Math.min(Math.max(this.num("selected-index", 0), 0), Math.max(items.length - 1, 0));
    const subSelected = Math.min(
      Math.max(this.num("sub-selected-index", 0), 0),
      Math.max(subItems.length - 1, 0),
    );
    const hasSubTabs = !vertical && type === "icon" && showLabels && subItems.length > 0;
    const mode = vertical ? "vertical" : type === "icon" ? "icon-mode" : "text-mode";

    const barBg = "var(--Background-MaterialRegular, rgba(255, 255, 255, .34))";
    const barBorder = `var(--Line-Border,
      var(--sui-tab-bar-border, color(display-p3 1 1 1 / .34)))`;
    const activeTabBg = themeColor("fillPrimary");
    const activeTabFg = themeColor("labelPrimaryLight");
    const inactiveFg = themeColor("labelPrimary");
    const verticalActiveBg = themeColor("fillPrimary");
    const subActiveBg = themeColor("fillPrimary");
    const subActiveFg = themeColor("labelPrimaryLight");
    const focusRing = themeColor("interaction");
    const badgeBg = themeColor("error");
    const badgeFg = themeColor("labelPrimaryLight");
    const hoverOverlay = "var(--sui-lighten-hover, rgba(255,255,255,0.12))";

    const tabs = items.map((label, index) => {
      const active = index === selected;
      const badge = badges[index];
      const icon = icons[index] || DEFAULT_ICONS[index % DEFAULT_ICONS.length];
      const iconContent = `
        <span class="glyph" aria-hidden="true">
          <slot name="icon-${index}">${escapeHtml(icon)}</slot>
        </span>`;
      const labelContent = `<span class="label">${escapeHtml(label)}</span>`;
      return `
        <button class="tab ${active ? "active" : ""}" role="tab"
          aria-selected="${active}" tabindex="${active ? 0 : -1}" data-index="${index}">
          ${mode === "text-mode" ? labelContent : iconContent}
          ${showLabels || horizontalHoverLabels ? labelContent : ""}
          ${badge ? `<span class="badge" aria-label="${escapeHtml(badge)}">${escapeHtml(badge)}</span>` : ""}
        </button>`;
    }).join("");

    const hoverTabs = verticalHoverPanel ? items.map((label, index) => {
      const active = index === selected;
      const badge = badges[index];
      const icon = icons[index] || DEFAULT_ICONS[index % DEFAULT_ICONS.length];
      return `
        <button class="hover-tab ${active ? "active" : ""}" role="tab"
          aria-selected="${active}" tabindex="${active ? 0 : -1}" data-index="${index}">
          <span class="glyph" aria-hidden="true">
            <slot name="expanded-icon-${index}">${escapeHtml(icon)}</slot>
          </span>
          <span class="hover-label">${escapeHtml(label)}</span>
          ${badge ? `<span class="badge" aria-label="${escapeHtml(badge)}">${escapeHtml(badge)}</span>` : ""}
        </button>`;
    }).join("") : "";

    const subTabs = subItems.map((label, index) => `
      <button class="sub-tab ${index === subSelected ? "active" : ""}" role="tab"
        aria-selected="${index === subSelected}" tabindex="${index === subSelected ? 0 : -1}"
        data-sub-index="${index}">${escapeHtml(label)}</button>
    `).join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: inline-flex;
          box-sizing: border-box;
          font-family: inherit;
        }
        :host([disabled]) { opacity: ${DISABLE_ALPHA}; pointer-events: none; }
        * { box-sizing: border-box; }
        button { border: 0; margin: 0; font: inherit; letter-spacing: 0; }
        .bar {
          display: inline-flex;
          position: relative;
          align-items: center;
          justify-content: center;
        }
        .bar.horizontal {
          flex-direction: ${hasSubTabs ? "column" : "row"};
          gap: ${hasSubTabs ? 8 : 0}px;
          padding: ${hasSubTabs
            ? "3px 3px calc(7px + env(safe-area-inset-bottom, 0px))"
            : "7px 7px calc(7px + env(safe-area-inset-bottom, 0px))"};
          min-height: ${hasSubTabs ? 148 : showLabels ? 88 : 64}px;
          border-radius: 32px;
          border: 1px solid ${barBorder};
          background: ${barBg};
          backdrop-filter: blur(50px);
          -webkit-backdrop-filter: blur(50px);
        }
        .bar.horizontal.hover-labels {
          transition: min-height .18s ease;
        }
        .bar.vertical { flex-direction: column; gap: 8px; }
        .tabs {
          display: flex;
          align-items: center;
          justify-content: center;
          flex-direction: ${vertical ? "column" : "row"};
          gap: ${vertical ? 8 : 4}px;
          ${hasSubTabs ? `
            padding: 4px;
            border-radius: 28px;
            background: ${themeColor("fillTertiary")};
          ` : ""}
        }
        .tab, .sub-tab, .hover-tab {
          position: relative;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          flex: ${equalWidth && !vertical ? "1 1 0" : "0 0 auto"};
          min-width: 0;
          color: ${inactiveFg};
          background: transparent;
          cursor: pointer;
          user-select: none;
          outline: none;
          transition: background-color .14s ease, color .14s ease, box-shadow .14s ease,
            width .18s ease, height .18s ease, padding .18s ease, gap .18s ease;
        }
        .tab::after, .sub-tab::after, .hover-tab::after {
          content: "";
          position: absolute;
          inset: 0;
          border-radius: inherit;
          background: transparent;
          pointer-events: none;
          transition: background-color .12s ease;
        }
        .tab:hover::after, .tab:focus-visible::after,
        .sub-tab:hover::after, .sub-tab:focus-visible::after,
        .hover-tab:hover::after, .hover-tab:focus-visible::after {
          background: ${hoverOverlay};
        }
        .tab:focus-visible, .sub-tab:focus-visible, .hover-tab:focus-visible {
          box-shadow: 0 0 0 2px ${focusRing};
        }
        .horizontal .tab {
          height: ${showLabels ? 72 : 48}px;
          border-radius: 24px;
        }
        .text-mode .tab {
          padding: 0 16px;
          font-size: 16px;
          line-height: 20px;
          font-weight: 600;
        }
        .icon-mode .tab {
          width: ${hasSubTabs ? 80 : 64}px;
          padding: 14px 8px;
          flex-direction: column;
          gap: ${showLabels ? 8 : 0}px;
        }
        .horizontal .tab.active {
          color: ${activeTabFg};
          background: ${activeTabBg};
        }
        .vertical .tab {
          width: 48px;
          height: 48px;
          padding: 0;
          gap: 4px;
          flex-direction: row;
          justify-content: flex-start;
          border-radius: 28px;
          border: 1px solid ${barBorder};
          color: ${inactiveFg};
          background: ${barBg};
          overflow: visible;
        }
        .vertical .tab.active { background: ${verticalActiveBg}; color: ${activeTabFg}; }
        .vertical .tab .glyph {
          width: 48px;
          height: 48px;
          flex: 0 0 48px;
        }
        .hover-panel {
          position: absolute;
          left: 64px;
          top: -12px;
          display: flex;
          flex-direction: column;
          align-items: stretch;
          gap: 8px;
          min-width: 165px;
          padding: 11px;
          border-radius: 16px;
          border: 1px solid ${barBorder};
          background: ${barBg};
          box-shadow: 0 16px 32px rgba(0,0,0,.18);
          backdrop-filter: blur(50px);
          -webkit-backdrop-filter: blur(50px);
          opacity: 0;
          visibility: hidden;
          pointer-events: none;
          transform: translateX(-8px);
          transform-origin: left center;
          transition: transform .18s ease, visibility 0s linear .18s;
          z-index: 10;
        }
        .hover-panel::before {
          content: "";
          position: absolute;
          left: -16px;
          top: 0;
          width: 16px;
          height: 100%;
        }
        .vertical.expand:hover .hover-panel,
        .vertical.expand:focus-within .hover-panel,
        .vertical.expand.is-expanded .hover-panel {
          opacity: 1;
          visibility: visible;
          pointer-events: auto;
          transform: translateX(0);
          transition-delay: 0s;
        }
        .hover-tab {
          width: 100%;
          height: 48px;
          padding: 0 18px 0 14px;
          gap: 4px;
          justify-content: flex-start;
          border-radius: 28px;
          color: ${inactiveFg};
          white-space: nowrap;
        }
        .hover-tab.active {
          color: ${activeTabFg};
          background: ${verticalActiveBg};
        }
        .hover-tab .glyph { flex: 0 0 20px; }
        .hover-label {
          max-width: 192px;
          overflow: hidden;
          text-overflow: ellipsis;
          font-size: 14px;
          line-height: 18px;
          font-weight: 600;
        }
        .glyph {
          position: relative;
          display: inline-flex;
          width: 20px;
          height: 20px;
          align-items: center;
          justify-content: center;
          flex: 0 0 20px;
          color: currentColor;
          font-size: 20px;
          line-height: 20px;
        }
        ::slotted(svg) { width: 20px; height: 20px; fill: currentColor; color: currentColor; }
        ::slotted(img) { width: 20px; height: 20px; object-fit: contain; }
        .icon-mode .tab .label {
          display: block;
          max-width: 56px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          font-size: 12px;
          line-height: 16px;
          font-weight: 500;
        }
        .icon-mode .tab.active .label { font-weight: 600; }
        .horizontal.hover-labels .label {
          max-height: 0;
          opacity: 0;
          transform: translateY(-2px);
          transition: max-height .18s ease, opacity .12s ease, transform .18s ease;
        }
        .horizontal.hover-labels:hover,
        .horizontal.hover-labels:focus-within,
        .horizontal.hover-labels.is-expanded {
          min-height: 88px;
        }
        .horizontal.hover-labels:hover .tab,
        .horizontal.hover-labels:focus-within .tab,
        .horizontal.hover-labels.is-expanded .tab {
          height: 72px;
          gap: 8px;
        }
        .horizontal.hover-labels:hover .label,
        .horizontal.hover-labels:focus-within .label,
        .horizontal.hover-labels.is-expanded .label {
          max-height: 16px;
          opacity: 1;
          transform: translateY(0);
        }
        .badge {
          position: absolute;
          top: ${vertical ? 0 : 6}px;
          right: ${vertical ? -2 : 4}px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-width: 16px;
          height: 16px;
          padding: 0 4px;
          border-radius: 999px;
          color: ${badgeFg};
          background: ${badgeBg};
          font-size: 10px;
          line-height: 14px;
          font-weight: 600;
          z-index: 3;
        }
        .horizontal.icon-mode .badge {
          left: calc(50% + 10px);
          right: auto;
        }
        .hover-tab .badge { top: 0; right: -2px; }
        .sub-tabs {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
          padding: 0 4px;
        }
        .sub-tab {
          height: 48px;
          padding: 0 16px;
          border-radius: 8px;
          font-size: 14px;
          line-height: 18px;
          font-weight: 500;
        }
        .sub-tab.active {
          border-radius: 24px;
          color: ${subActiveFg};
          background: ${subActiveBg};
          font-weight: 600;
        }
      </style>
      <nav class="bar ${vertical ? "vertical" : "horizontal"} ${mode} ${verticalHoverPanel ? "expand" : ""} ${horizontalHoverLabels ? "hover-labels" : ""} ${this._expanded ? "is-expanded" : ""}"
        aria-label="Tab bar">
        <div class="tabs" role="tablist" aria-orientation="${vertical ? "vertical" : "horizontal"}">
          ${tabs}
        </div>
        ${verticalHoverPanel ? `<div class="hover-panel" role="tablist" aria-label="Expanded tab menu">${hoverTabs}</div>` : ""}
        ${hasSubTabs ? `<div class="sub-tabs" role="tablist">${subTabs}</div>` : ""}
      </nav>`;

    this.shadowRoot.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", () => this._selectTab(Number(tab.dataset.index), items));
      tab.addEventListener("keydown", (event) => this._onKeydown(event, ".tab", vertical, items));
    });
    this.shadowRoot.querySelectorAll(".sub-tab").forEach((tab) => {
      tab.addEventListener("click", () => this._selectSubTab(Number(tab.dataset.subIndex), subItems));
      tab.addEventListener("keydown", (event) => this._onSubKeydown(event, subItems));
    });
    this.shadowRoot.querySelectorAll(".hover-tab").forEach((tab) => {
      tab.addEventListener("click", () => this._selectTab(Number(tab.dataset.index), items));
      tab.addEventListener("keydown", (event) => this._onKeydown(event, ".hover-tab", true, items));
    });
    if (expandOnHover) this._bindExpansionState();
  }

  _selectTab(index, items) {
    const keepExpanded = this._preserveExpansion();
    this.setAttribute("selected-index", String(index));
    if (keepExpanded) this._restoreExpansion();
    emit(this, "select", { index, value: items[index] });
  }

  _selectSubTab(index, items) {
    const keepExpanded = this._preserveExpansion();
    this.setAttribute("sub-selected-index", String(index));
    if (keepExpanded) this._restoreExpansion();
    emit(this, "sub-select", { index, value: items[index] });
  }

  _preserveExpansion() {
    const bar = this.shadowRoot.querySelector(".bar");
    if (!bar || !this.bool("expand-on-hover")) return false;
    this._expanded =
      this._expanded ||
      bar.classList.contains("is-expanded") ||
      bar.matches(":hover") ||
      bar.matches(":focus-within") ||
      (bar.classList.contains("horizontal") && bar.offsetHeight > 64);
    return this._expanded;
  }

  _restoreExpansion() {
    this._expanded = true;
    this.shadowRoot.querySelector(".bar")?.classList.add("is-expanded");
    queueMicrotask(() => {
      if (!this._expanded) return;
      this.shadowRoot.querySelector(".bar")?.classList.add("is-expanded");
    });
  }

  _bindExpansionState() {
    const bar = this.shadowRoot.querySelector(".bar");
    if (!bar) return;
    const isCurrent = () => this.shadowRoot.querySelector(".bar") === bar;
    const expand = () => {
      if (!isCurrent()) return;
      this._expanded = true;
      bar.classList.add("is-expanded");
    };
    const collapse = () => {
      if (!isCurrent()) return;
      this._expanded = false;
      bar.classList.remove("is-expanded");
    };
    bar.addEventListener("pointerenter", expand);
    bar.addEventListener("pointerleave", collapse);
    bar.addEventListener("focusin", expand);
    bar.addEventListener("focusout", () => {
      requestAnimationFrame(() => {
        const current = this.shadowRoot.querySelector(".bar");
        if (current === bar && !current.matches(":focus-within") && !current.matches(":hover")) collapse();
      });
    });
  }

  _onKeydown(event, selector, vertical, items) {
    const previous = vertical ? "ArrowUp" : "ArrowLeft";
    const next = vertical ? "ArrowDown" : "ArrowRight";
    if (![previous, next, "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const tabs = [...this.shadowRoot.querySelectorAll(selector)];
    const current = Number(event.currentTarget.dataset.index);
    let index = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 :
      (current + (event.key === next ? 1 : -1) + tabs.length) % tabs.length;
    this._selectTab(index, items);
    requestAnimationFrame(() => this.shadowRoot.querySelector(`${selector}[data-index="${index}"]`)?.focus());
  }

  _onSubKeydown(event, items) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const tabs = [...this.shadowRoot.querySelectorAll(".sub-tab")];
    const current = Number(event.currentTarget.dataset.subIndex);
    const index = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 :
      (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
    this._selectSubTab(index, items);
    requestAnimationFrame(() => this.shadowRoot.querySelector(`[data-sub-index="${index}"]`)?.focus());
  }
}

define("sui-tab-bar", SuiTabBar);
