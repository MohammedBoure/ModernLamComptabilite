"use strict";

function exportCurrentReportCsv() {
  const dataset = getReportDataset();
  const rows = dataset.rows;
  const headers = dataset.columns.map((column) => column.label);
  const lines = [headers.join(",")];
  rows.forEach((row, index) => {
    lines.push(
      dataset.columns
        .map((column) => {
          const value = column.value ? column.value(row, index) : row[column.key];
          return `"${String(value ?? "").replaceAll('"', '""')}"`;
        })
        .join(",")
    );
  });
  download(`${activeReport}-${currentPeriodKey()}.csv`, lines.join("\n"), "text/csv");
  recordExport(dataset.title, "CSV");
}

function recordExport(reportName, format) {
  state.reportExports.unshift({
    id: id(),
    reportName,
    period: currentPeriodKey(),
    format,
    generatedBy: "Admin",
    generatedAt: new Date().toISOString(),
  });
  audit("Report export", "reportExports", reportName, { reportName, format, period: currentPeriodKey() });
  saveState();
}

function download(filename, content, type = "application/json") {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function downloadBackup() {
  download(`modernlam-prototype-backup-${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(state, null, 2), "application/json");
  showToast("Backup downloaded.");
}

function resetData() {
  const confirmed = window.confirm("Reset all browser prototype data?");
  if (!confirmed) return;
  const freshState = seedState();
  Object.keys(state).forEach((key) => delete state[key]);
  Object.assign(state, freshState);
  saveState();
  showToast("Prototype data reset.");
  render();
}
