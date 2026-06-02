"use strict";

const app = document.getElementById("app");

function showToast(message) {
  toast = message;
  window.setTimeout(() => {
    toast = "";
    render();
  }, 2200);
}

function renderField(field, disabled = false) {
  const classes = ["field"];
  if (field.full) classes.push("full");
  if (field.span === 2) classes.push("span-2");
  const required = field.required ? " required" : "";
  const disabledAttr = disabled || field.disabled ? " disabled" : "";
  const value = field.value ?? "";
  const label = `<label for="${escapeHtml(field.name)}">${escapeHtml(field.label)}</label>`;
  if (field.type === "select") {
    return `<div class="${classes.join(" ")}">${label}<select id="${escapeHtml(field.name)}" name="${escapeHtml(field.name)}"${required}${disabledAttr}>${optionList(field.options || [], value)}</select></div>`;
  }
  if (field.type === "textarea") {
    return `<div class="${classes.join(" ")}">${label}<textarea id="${escapeHtml(field.name)}" name="${escapeHtml(field.name)}"${required}${disabledAttr}>${escapeHtml(value)}</textarea></div>`;
  }
  const type = field.type || "text";
  const step = field.step ? ` step="${escapeHtml(field.step)}"` : "";
  const min = field.min !== undefined ? ` min="${escapeHtml(field.min)}"` : "";
  return `<div class="${classes.join(" ")}">${label}<input id="${escapeHtml(field.name)}" name="${escapeHtml(field.name)}" type="${escapeHtml(type)}" value="${escapeHtml(value)}"${required}${disabledAttr}${step}${min}></div>`;
}

function renderForm(title, formId, fields, buttonLabel = "Save", options = {}) {
  const disabled = Boolean(options.periodScoped && isClosedPeriod());
  return `
    <div class="form-card">
      <h2>${escapeHtml(title)}</h2>
      <form data-form="${escapeHtml(formId)}">
        <div class="form-grid">
          ${fields.map((field) => renderField(field, disabled)).join("")}
        </div>
        <div class="action-row">
          <button class="text-btn primary" type="submit" title="${escapeHtml(buttonLabel)}"${disabled ? " disabled" : ""}>+ ${escapeHtml(buttonLabel)}</button>
        </div>
      </form>
    </div>
  `;
}

function renderTable(columns, rows, options = {}) {
  if (!rows.length) return `<div class="empty-state">${escapeHtml(options.empty || "No records for this view.")}</div>`;
  const actionHead = options.collection ? "<th>Action</th>" : "";
  const body = rows
    .map((row) => {
      const cells = columns
        .map((column) => {
          const raw = typeof column.value === "function" ? column.value(row) : row[column.key];
          const value = column.html ? raw : column.format ? column.format(raw, row) : escapeHtml(raw);
          const css = column.amount ? " class=\"amount\"" : "";
          return `<td${css}>${value}</td>`;
        })
        .join("");
      const actionCell = options.collection
        ? `<td><button class="icon-btn danger" type="button" title="Cancel" data-cancel="${escapeHtml(options.collection)}" data-id="${escapeHtml(row.id)}"${periodCollections.has(options.collection) && isClosedPeriod() ? " disabled" : ""}>X</button></td>`
        : "";
      return `<tr>${cells}${actionCell}</tr>`;
    })
    .join("");
  return `
    <div class="table-wrap">
      <table>
        <thead><tr>${columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("")}${actionHead}</tr></thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
}

function renderSection(title, body, actions = "") {
  return `
    <section class="section">
      <div class="section-head">
        <h2>${escapeHtml(title)}</h2>
        <div class="section-actions">${actions}</div>
      </div>
      <div class="section-body">${body}</div>
    </section>
  `;
}

function renderHeader(title, description, actions = "") {
  return `
    <div class="view-header">
      <div>
        <h1>${escapeHtml(title)}</h1>
        <p>${escapeHtml(description)}</p>
      </div>
      <div class="section-actions">${actions}</div>
    </div>
  `;
}

function renderMetrics(items) {
  return `<div class="grid four">${items
    .map((item) => {
      const inner = `<span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.value)}</strong>${item.detail ? `<small>${escapeHtml(item.detail)}</small>` : ""}`;
      const report = item.report ? ` data-report="${escapeHtml(item.report)}"` : "";
      const severity = item.severity ? ` metric-${escapeHtml(item.severity)}` : "";
      if (item.view) return `<button class="metric metric-button${severity}" type="button" data-view="${escapeHtml(item.view)}"${report} title="${escapeHtml(item.label)}">${inner}</button>`;
      return `<div class="metric">${inner}</div>`;
    })
    .join("")}</div>`;
}

function registerView(name, renderer) {
  viewRenderers[name] = renderer;
}

function setReportDatasetProvider(provider) {
  reportDatasetProvider = provider;
}

function getActiveReport() {
  return activeReport;
}

function getReportDataset() {
  if (reportDatasetProvider) return reportDatasetProvider();
  return { title: "Report", columns: [], rows: [], total: "" };
}

function renderTopbar() {
  const period = getPeriod();
  const years = Array.from({ length: 7 }, (_, index) => state.selected.year - 3 + index);
  return `
    <header class="topbar">
      <div class="brand">
        <img src="prototype/assets/modernlam-logo.svg" alt="ModernLam logo">
        <div class="brand-title">
          <strong>ModernLam Comptabilite</strong>
          <span>Browser Prototype</span>
        </div>
      </div>
      <div class="period-tools">
        <label>Month
          <select data-period-month>${monthNames.map((name, index) => `<option value="${index + 1}"${index + 1 === state.selected.month ? " selected" : ""}>${escapeHtml(name)}</option>`).join("")}</select>
        </label>
        <label>Year
          <select data-period-year>${years.map((year) => `<option value="${year}"${year === state.selected.year ? " selected" : ""}>${year}</option>`).join("")}</select>
        </label>
        ${statusPill(period.status)}
      </div>
      <div class="top-actions">
        ${periodStatuses.map((status) => `<button class="icon-btn" type="button" title="Set ${escapeHtml(status)}" data-period-status="${escapeHtml(status)}">${escapeHtml(status[0])}</button>`).join("")}
      </div>
    </header>
  `;
}

function renderSidebar() {
  return `
    <aside class="sidebar">
      <nav class="nav">
        ${navItems
          .map(([key, icon, label]) => `<button type="button" class="${activeView === key ? "active" : ""}" data-view="${escapeHtml(key)}"><span class="nav-icon">${escapeHtml(icon)}</span><span>${escapeHtml(label)}</span></button>`)
          .join("")}
      </nav>
    </aside>
  `;
}

function renderContent() {
  const view = viewRenderers[activeView] ? activeView : "dashboard";
  const renderer = viewRenderers[view];
  const body = renderer ? renderer() : `<div class="empty-state">The selected interface is not loaded.</div>`;
  return `<main class="content">${body}</main>`;
}

function render() {
  ensurePeriod(state.selected.month, state.selected.year);
  app.innerHTML = `
    <div class="app-shell">
      ${renderTopbar()}
      ${renderSidebar()}
      ${renderContent()}
    </div>
    ${toast ? `<div class="toast">${escapeHtml(toast)}</div>` : ""}
  `;
}
