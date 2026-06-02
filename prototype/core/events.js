"use strict";

function handleClick(event) {
  const viewButton = event.target.closest("[data-view]");
  if (viewButton) {
    if (viewButton.dataset.report) {
      activeReport = viewButton.dataset.report;
      localStorage.setItem(REPORT_KEY, activeReport);
    }
    activeView = viewButton.dataset.view;
    localStorage.setItem(VIEW_KEY, activeView);
    render();
    return;
  }
  const statusButton = event.target.closest("[data-period-status]");
  if (statusButton) {
    setPeriodStatus(statusButton.dataset.periodStatus);
    return;
  }
  const cancelButton = event.target.closest("[data-cancel]");
  if (cancelButton) {
    cancelRecord(cancelButton.dataset.cancel, cancelButton.dataset.id);
    return;
  }
  const action = event.target.closest("[data-action]")?.dataset.action;
  if (!action) return;
  if (action === "generate-salaries") generateSalaryDrafts();
  if (action === "print") window.print();
  if (action === "official-report") {
    recordExport(getReportDataset().title, "Official PDF print");
    window.print();
  }
  if (action === "export-csv") exportCurrentReportCsv();
  if (action === "download-backup") downloadBackup();
  if (action === "reset-data") resetData();
}

function handleChange(event) {
  const monthSelect = event.target.closest("[data-period-month]");
  const yearSelect = event.target.closest("[data-period-year]");
  if (monthSelect || yearSelect) {
    const month = document.querySelector("[data-period-month]").value;
    const year = document.querySelector("[data-period-year]").value;
    setPeriod(month, year);
    return;
  }
  const reportSelect = event.target.closest("[data-report-select]");
  if (reportSelect) {
    activeReport = reportSelect.value;
    localStorage.setItem(REPORT_KEY, activeReport);
    render();
  }
}

document.addEventListener("submit", handleSubmit);
document.addEventListener("click", handleClick);
document.addEventListener("change", handleChange);

function init() {
  saveState();
  render();
}
