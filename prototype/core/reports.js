"use strict";

function exportCurrentReportCsv() {
  const dataset = getReportDataset();
  const rows = dataset.rows;
  const headers = dataset.columns.map((column) => column.label);
  const generatedAt = new Date().toLocaleString();
  const lines = [
    "sep=,",
    csvLine(["Report", dataset.title]),
    csvLine(["Lab", prototypeSettings().labName]),
    csvLine(["NIF", prototypeSettings().nif]),
    csvLine(["RIP", prototypeSettings().rip]),
    csvLine(["Period", `${monthNames[state.selected.month - 1]} ${state.selected.year}`]),
    csvLine(["Print Date", generatedAt]),
    csvLine(["User", currentUserDisplayName()]),
    csvLine(["Total", dataset.total]),
    "",
    csvLine(headers),
  ];
  rows.forEach((row, index) => {
    lines.push(
      csvLine(dataset.columns.map((column) => (column.value ? column.value(row, index) : row[column.key])))
    );
  });
  download(`${activeReport}-${currentPeriodKey()}.csv`, `\uFEFF${lines.join("\r\n")}`, "text/csv;charset=utf-8");
  recordExport(dataset.title, "CSV");
}

function csvLine(values) {
  return values.map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(",");
}

function recordExport(reportName, format) {
  state.reportExports.unshift({
    id: id(),
    reportName,
    period: currentPeriodKey(),
    format,
    generatedBy: currentUserDisplayName(),
    generatedAt: new Date().toISOString(),
  });
  audit("Report export", "reportExports", reportName, { reportName, format, period: currentPeriodKey() });
  saveState();
  render();
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
