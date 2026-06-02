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
  const attendanceQuick = event.target.closest("[data-attendance-quick]");
  if (attendanceQuick) {
    setQuickAttendance(attendanceQuick.dataset.attendanceEmployee, attendanceQuick.dataset.attendanceDate);
    return;
  }
  const salaryStatusButton = event.target.closest("[data-salary-status]");
  if (salaryStatusButton) {
    updateSalaryStatus(salaryStatusButton.dataset.id, salaryStatusButton.dataset.salaryStatus);
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
  if (action === "reset-cash-closing-filters") {
    localStorage.removeItem(CASH_CLOSING_DATE_FILTER_KEY);
    localStorage.removeItem(CASH_CLOSING_USER_FILTER_KEY);
    render();
  }
  if (action === "reset-supplier-filters") {
    localStorage.removeItem(SUPPLIER_FILTER_KEY);
    localStorage.removeItem(SUPPLIER_CATEGORY_FILTER_KEY);
    localStorage.removeItem(SUPPLIER_STATUS_FILTER_KEY);
    render();
  }
  if (action === "reset-partner-filters") {
    localStorage.removeItem(PARTNER_TYPE_FILTER_KEY);
    render();
  }
}

function handleChange(event) {
  const supplierFilter = event.target.closest("[data-supplier-filter]");
  if (supplierFilter) {
    const keys = {
      supplier: SUPPLIER_FILTER_KEY,
      category: SUPPLIER_CATEGORY_FILTER_KEY,
      status: SUPPLIER_STATUS_FILTER_KEY,
    };
    const key = keys[supplierFilter.dataset.supplierFilter];
    if (supplierFilter.value) localStorage.setItem(key, supplierFilter.value);
    else localStorage.removeItem(key);
    render();
    return;
  }
  const partnerFilter = event.target.closest("[data-partner-filter]");
  if (partnerFilter) {
    if (partnerFilter.value) localStorage.setItem(PARTNER_TYPE_FILTER_KEY, partnerFilter.value);
    else localStorage.removeItem(PARTNER_TYPE_FILTER_KEY);
    render();
    return;
  }
  const cashClosingFilter = event.target.closest("[data-cash-closing-filter]");
  if (cashClosingFilter) {
    const key = cashClosingFilter.dataset.cashClosingFilter === "user" ? CASH_CLOSING_USER_FILTER_KEY : CASH_CLOSING_DATE_FILTER_KEY;
    if (cashClosingFilter.value) localStorage.setItem(key, cashClosingFilter.value);
    else localStorage.removeItem(key);
    render();
    return;
  }
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
