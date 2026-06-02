(() => {
  "use strict";
  const M = window.ModernLamPrototype;
  const {
    state,
    monthNames,
    supplierCategories,
    paymentModes,
    partnerTypes,
    paymentStatuses,
    salaryStatuses,
    dayCodes,
    roles,
    getPeriod,
    renderHeader,
    closedNotice,
    renderMetrics,
    totals,
    money,
    renderSection,
    renderTable,
    scopedRows,
    renderForm,
    defaultDate,
    currentPeriodKey,
    supplierName,
    employeeName,
    paymentTargetLabel,
    employeeFunction,
    latestUpdate,
    daysInMonth,
    pad,
    optionList,
    number,
    sum,
    statusPill,
    escapeHtml
  } = M;

  function severityFor(count, activeSeverity = "warning") {
    return count > 0 ? activeSeverity : "info";
  }

  function renderAlert(alert) {
    const report = alert.report ? ` data-report="${escapeHtml(alert.report)}"` : "";
    return `
      <button class="alert-item ${escapeHtml(alert.severity)}" type="button" data-view="${escapeHtml(alert.view)}"${report} title="${escapeHtml(alert.title)}">
        <span class="alert-copy">
          <strong>${escapeHtml(alert.title)}</strong>
          <span>${escapeHtml(alert.text)}</span>
        </span>
        <span class="alert-severity">${escapeHtml(alert.severity)}</span>
      </button>
    `;
  }

  function renderDashboard() {
    const t = totals();
    const period = getPeriod();
    const lastUpdate = latestUpdate() || "No activity yet";
    const unjustified = scopedRows("cashClosures").filter((row) => number(row.difference) !== 0 && !row.remark.trim()).length;
    const draftSalaries = scopedRows("salaryReports").filter((row) => row.status === "Draft").length;
    const openSupplierRows = scopedRows("supplierTransactions").filter((row) => number(row.remainingAmount) > 0);
    const partialSuppliers = openSupplierRows.length;
    const supplierRemaining = sum(openSupplierRows, "remainingAmount");
    const openPartners = scopedRows("partners").filter((row) => number(row.remainingBalance) > 0).length;
    const partnerRemaining = sum(scopedRows("partners"), "remainingBalance");
    const employeesWithoutContracts = state.employees.filter((employee) => employee.status !== "Inactive" && !state.contracts.some((contract) => contract.employeeId === employee.id && contract.status === "Active")).length;
    const incompleteCheques = scopedRows("cheques").filter((row) => !row.beneficiary || !row.chequeNumber || number(row.amount) <= 0).length;
    const hasPeriodExport = state.reportExports.some((row) => row.period === currentPeriodKey());
    const alerts = [
      {
        title: "Cash differences",
        text: unjustified ? `${unjustified} need remarks` : "No unjustified differences",
        severity: severityFor(unjustified, "blocking"),
        view: "cashClosing",
      },
      {
        title: "Supplier balances",
        text: partialSuppliers ? `${partialSuppliers} open balances` : "No open supplier balance",
        severity: severityFor(partialSuppliers),
        view: "suppliers",
      },
      {
        title: "Partner balances",
        text: openPartners ? `${openPartners} not settled` : "All settled",
        severity: severityFor(openPartners),
        view: "partners",
      },
      {
        title: "Draft salaries",
        text: draftSalaries ? `${draftSalaries} draft rows` : "No draft salaries",
        severity: severityFor(draftSalaries, "blocking"),
        view: "salaries",
      },
      {
        title: "Active contracts",
        text: employeesWithoutContracts ? `${employeesWithoutContracts} missing contracts` : "All active employees covered",
        severity: severityFor(employeesWithoutContracts),
        view: "hr",
      },
      {
        title: "Cheques",
        text: incompleteCheques ? `${incompleteCheques} incomplete rows` : "No incomplete cheque rows",
        severity: severityFor(incompleteCheques),
        view: "reports",
        report: "cheque",
      },
      {
        title: "Closing export",
        text: hasPeriodExport ? "Export trace exists" : "No report/export trace",
        severity: hasPeriodExport ? "info" : "blocking",
        view: "reports",
      },
    ];
    return `
      ${renderHeader(
        "Dashboard",
        "Monthly financial summary, alerts, and closing readiness.",
        `<div class="dashboard-stamp"><strong>${escapeHtml(period.status)}</strong><span>Last update: ${escapeHtml(lastUpdate)}</span></div>`
      )}
      ${closedNotice()}
      ${renderMetrics([
        { label: "Period Status", value: period.status, detail: `${monthNames[state.selected.month - 1]} ${state.selected.year}`, view: "admin" },
        { label: "Cash CV", value: money(t.cashCv), view: "cashSafe" },
        { label: "Cash C", value: money(t.cashC), view: "cashSafe" },
        { label: "TPE", value: money(t.tpe), view: "cashSafe" },
        { label: "Expenses", value: money(t.expensesTotal), view: "balance" },
        { label: "Real Safe Net", value: money(t.realSafeNet), view: "cashSafe" },
        { label: "Global Revenue", value: money(t.globalRevenue), view: "balance" },
        { label: "Profitability", value: money(t.profitability), view: "balance" },
        { label: "Net Profitability", value: money(t.netProfitability), view: "balance" },
        { label: "Supplier Remaining", value: money(supplierRemaining), view: "suppliers", severity: partialSuppliers ? "warning" : "info" },
        { label: "Partner Remaining", value: money(partnerRemaining), view: "partners", severity: openPartners ? "warning" : "info" },
        { label: "Draft Salaries", value: draftSalaries, view: "salaries", severity: draftSalaries ? "blocking" : "info" },
        { label: "Incomplete Cheques", value: incompleteCheques, view: "reports", report: "cheque", severity: incompleteCheques ? "warning" : "info" },
        { label: "Last Update", value: lastUpdate, view: "admin" },
      ])}
      ${renderSection(
        "Monthly Alerts",
        `<div class="alert-list">${alerts
          .map(renderAlert)
          .join("")}</div>`
      )}
      ${renderSection(
        "Recent Audit",
        renderTable(
          [
            { label: "Date", value: (row) => new Date(row.createdAt).toLocaleString() },
            { label: "Action", key: "action" },
            { label: "Entity", key: "entityType" },
            { label: "User", key: "user" },
          ],
          state.auditLogs.slice(0, 8),
          { empty: "No audit entries." }
        )
      )}
    `;
  }


  M.registerView('dashboard', renderDashboard);
})();
