/* DateRangePicker — the range-selection counterpart to sui-date-picker. */
import { SuiElement, define, emit, escapeHtml, themeColor } from "./base.js";

const WEEKDAYS = ["S", "M", "T", "W", "T", "F", "S"];
const MONTHS = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

function dateValue(year, month, day) {
  return year + "-" + String(month + 1).padStart(2, "0") + "-" + String(day).padStart(2, "0");
}

function timeValue(value) {
  if (!value) return null;
  const date = new Date(value + "T00:00:00Z");
  return Number.isNaN(date.getTime()) ? null : date.getTime();
}

export class SuiDateRangePicker extends SuiElement {
  static get observedAttributes() { return ["year", "month", "start", "end", "disabled"]; }

  render() {
    const today = new Date();
    const year = Math.round(this.num("year", today.getFullYear()));
    const month = Math.min(11, Math.max(0, Math.round(this.num("month", today.getMonth()))));
    const start = this.attr("start");
    const end = this.attr("end");
    const startTime = timeValue(start);
    const endTime = timeValue(end);
    const disabled = this.bool("disabled");
    const firstDay = new Date(year, month, 1).getDay();
    const days = new Date(year, month + 1, 0).getDate();
    const cells = Array(firstDay).fill(null).concat(Array.from({ length: days }, (_, index) => index + 1));
    const classes = (day) => {
      const value = dateValue(year, month, day);
      const time = timeValue(value);
      return [value === start ? "start" : "", value === end ? "end" : "",
        startTime != null && endTime != null && time > startTime && time < endTime ? "between" : ""]
        .filter(Boolean).join(" ");
    };
    this.shadowRoot.innerHTML = [
      "<style>:host{display:inline-flex}.calendar{width:416px;padding:16px;color:", themeColor("labelPrimary"),
      ";box-sizing:border-box}.calendar.disabled{opacity:var(--sui-disable-alpha,.4);pointer-events:none}",
      ".head{height:32px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between}",
      ".title{font:700 20px/26px sans-serif}.nav{width:32px;height:32px;border:0;border-radius:50%;background:transparent;",
      "color:inherit;font-size:20px;cursor:pointer}.nav:hover{background:var(--sui-lighten-hover)}",
      ".grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}.wk,.day{height:32px;display:grid;place-items:center}",
      ".wk{font-size:12px;color:", themeColor("labelQuaternary"), "}.day{position:relative;border:0;background:transparent;",
      "color:inherit;font:500 14px/18px sans-serif;cursor:pointer;border-radius:16px}.day:hover{background:var(--sui-lighten-hover)}",
      ".day.between{border-radius:0;background:", themeColor("fillLight"), "}.day.start,.day.end{background:",
      themeColor("fillSecondary"), ";border-radius:16px}.empty{visibility:hidden}</style>",
      '<div class="calendar ', disabled ? "disabled" : "", '"><div class="head"><button class="nav prev">‹</button><span class="title">',
      escapeHtml(MONTHS[month] + " " + year), '</span><button class="nav next">›</button></div><div class="grid">',
      WEEKDAYS.map((weekday) => '<div class="wk">' + weekday + "</div>").join(""),
      cells.map((day) => day == null ? '<span class="empty"></span>' :
        '<button class="day ' + classes(day) + '" data-day="' + day + '">' + day + "</button>").join(""),
      "</div></div>",
    ].join("");
    this.shadowRoot.querySelector(".prev").addEventListener("click", () => this.changeMonth(year, month, -1));
    this.shadowRoot.querySelector(".next").addEventListener("click", () => this.changeMonth(year, month, 1));
    this.shadowRoot.querySelectorAll(".day").forEach((day) => day.addEventListener("click", () => {
      const value = dateValue(year, month, Number(day.dataset.day));
      const valueTime = timeValue(value);
      if (!start || end || valueTime < startTime) {
        this._rendered = false;
        this.removeAttribute("end");
        this.setAttribute("start", value);
        this.render();
        this._rendered = true;
        emit(this, "range-change", { start: value, end: null });
      } else {
        this.setAttribute("end", value);
        emit(this, "range-change", { start, end: value });
      }
    }));
  }

  changeMonth(year, month, amount) {
    const value = new Date(year, month + amount, 1);
    this.setAttribute("year", String(value.getFullYear()));
    this.setAttribute("month", String(value.getMonth()));
  }
}

define("sui-date-range-picker", SuiDateRangePicker);
