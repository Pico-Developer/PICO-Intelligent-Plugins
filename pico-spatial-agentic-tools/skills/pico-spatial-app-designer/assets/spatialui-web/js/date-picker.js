/*
 * DatePicker — mirrors DatePicker.kt.
 * Width 416, date cell 32, header 32.
 * Kotlin default colors (defaultDatePickerColors):
 *   primary content/day text=labelPrimary,
 *   week header/inactive dates=labelQuaternary,
 *   selected-date bg=fillSecondary / text=labelPrimary,
 *   today bg=fillPrimary / text=labelPrimaryLight,
 *   date-range in-between bg=fillLight,
 *   nav buttons container=transparent / content=labelPrimary.
 */
import { SuiElement, define, emit, themeColor } from "./base.js";

const WEEKDAYS = ["S", "M", "T", "W", "T", "F", "S"];
const MONTHS = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

export class SuiDatePicker extends SuiElement {
  static get observedAttributes() { return ["year", "month", "selected"]; }
  render() {
    const today = new Date();
    let year = this.num("year", today.getFullYear());
    let month = this.num("month", today.getMonth());
    const selected = this.attr("selected");
    const first = new Date(year, month, 1);
    const startDay = first.getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const cells = [];
    for (let i = 0; i < startDay; i++) cells.push(null);
    for (let d = 1; d <= daysInMonth; d++) cells.push(d);
    const isToday = (d) => d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
    const isSelected = (d) => selected === `${year}-${month}-${d}`;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:inline-flex; }
        .cal { width:416px; padding:16px; box-sizing:border-box; color:${themeColor("labelPrimary")}; }
        .head { display:flex; align-items:center; justify-content:space-between; height:32px; margin-bottom:16px; }
        .title { font-size:20px; line-height:26px; font-weight:700; }
        .nav { background:none; border:none; color:${themeColor("labelPrimary")}; font-size:20px; cursor:pointer;
          width:32px; height:32px; border-radius:50%; transition:background-color .12s; display:inline-flex;
          align-items:center; justify-content:center; padding:0; }
        .nav:hover { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .grid { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; }
        .wk { text-align:center; font-size:12px; font-weight:600; color:${themeColor("labelQuaternary")}; height:32px; line-height:32px; }
        .cell { height:32px; display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:500;
          border-radius:50%; cursor:pointer; color:${themeColor("labelPrimary")}; transition:background-color .12s; position:relative; }
        .cell::after { content:""; position:absolute; inset:0; background:transparent; border-radius:50%; transition:background-color .12s; pointer-events:none; }
        .cell:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .cell.today { background:${themeColor("fillPrimary")}; color:${themeColor("labelPrimaryLight")}; }
        .cell.today::after { background:transparent; }
        .cell.selected { background:${themeColor("fillSecondary")}; color:${themeColor("labelPrimary")}; }
        .cell.selected::after { background:transparent; }
        .empty { visibility:hidden; }
      </style>
      <div class="cal">
        <div class="head">
          <button class="nav prev">‹</button>
          <span class="title">${MONTHS[month]} ${year}</span>
          <button class="nav next">›</button>
        </div>
        <div class="grid">
          ${WEEKDAYS.map((w) => `<div class="wk">${w}</div>`).join("")}
          ${cells.map((d) => d == null
            ? `<div class="cell empty"></div>`
            : `<div class="cell ${isSelected(d) ? "selected" : isToday(d) ? "today" : ""}" data-d="${d}">${d}</div>`).join("")}
        </div>
      </div>`;
    this.shadowRoot.querySelector(".prev").addEventListener("click", () => {
      if (month === 0) { this.setAttribute("year", year - 1); this.setAttribute("month", 11); }
      else this.setAttribute("month", month - 1);
    });
    this.shadowRoot.querySelector(".next").addEventListener("click", () => {
      if (month === 11) { this.setAttribute("year", year + 1); this.setAttribute("month", 0); }
      else this.setAttribute("month", month + 1);
    });
    this.shadowRoot.querySelectorAll(".cell[data-d]").forEach((c) => {
      c.addEventListener("click", () => {
        const d = +c.dataset.d;
        this.setAttribute("selected", `${year}-${month}-${d}`);
        emit(this, "date-select", { year, month, day: d });
      });
    });
  }
}
define("sui-date-picker", SuiDatePicker);
