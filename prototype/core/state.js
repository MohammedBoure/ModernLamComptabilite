"use strict";

function loadState() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) return JSON.parse(raw);
  } catch (error) {
    console.warn("Could not load prototype state", error);
  }
  return seedState();
}

function normalizeState(input) {
  const base = seedState();
  const output = { ...base, ...input };
  Object.keys(base).forEach((key) => {
    if (Array.isArray(base[key]) && !Array.isArray(output[key])) output[key] = [];
  });
  if (!output.selected) {
    const now = new Date();
    output.selected = { month: now.getMonth() + 1, year: now.getFullYear() };
  }
  output.settings = { ...base.settings, ...(input?.settings || {}) };
  ensurePeriod(output.selected.month, output.selected.year, output);
  return output;
}

function saveState() {
  localStorage.setItem(STORE_KEY, JSON.stringify(state));
}

let state = normalizeState(loadState());
let activeView = localStorage.getItem(VIEW_KEY) || "dashboard";
let activeReport = localStorage.getItem(REPORT_KEY) || "encashment";
let toast = "";
const viewRenderers = {};
let reportDatasetProvider = null;

function currentPeriodKey() {
  return makePeriodKey(state.selected.month, state.selected.year);
}

function ensurePeriod(month, year, targetState = state) {
  let period = targetState.periods.find((item) => item.month === month && item.year === year);
  if (!period) {
    period = {
      id: id(),
      month,
      year,
      status: "Open",
      openedAt: new Date().toISOString(),
      openedBy: targetState.settings?.currentUserDisplayName || defaultPrototypeSettings.currentUserDisplayName,
      closedAt: "",
      closedBy: "",
      closeNote: "",
    };
    targetState.periods.push(period);
  }
  return period;
}

function getPeriod() {
  return ensurePeriod(state.selected.month, state.selected.year);
}

function isClosedPeriod() {
  return getPeriod().status === "Closed";
}

function formatDate(value) {
  if (!value) return "";
  return value;
}

function defaultDate(day = 1) {
  return `${state.selected.year}-${pad(state.selected.month)}-${pad(day)}`;
}

function daysInMonth() {
  return new Date(state.selected.year, state.selected.month, 0).getDate();
}
