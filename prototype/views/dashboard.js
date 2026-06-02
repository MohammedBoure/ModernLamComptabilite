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
    daysInMonth,
    pad,
    optionList,
    number,
    sum,
    statusPill,
    escapeHtml
  } = M;
  function renderDashboard() {
    const t = totals();
    const unjustified = scopedRows("cashClosures").filter((row) => number(row.difference) !== 0 && !row.remark.trim()).length;
    const draftSalaries = scopedRows("salaryReports").filter((row) => row.status === "Draft").length;
    const partialSuppliers = scopedRows("supplierTransactions").filter((row) => row.status !== "Paid").length;
    const balanceReady = t.globalRevenue !== 0 || t.expensesTotal !== 0;
    const alerts = [
      [unjustified === 0, "Cash differences", unjustified === 0 ? "No unjustified differences" : `${unjustified} need remarks`],
      [partialSuppliers === 0, "Supplier balances", partialSuppliers === 0 ? "No open supplier balance" : `${partialSuppliers} open balances`],
      [draftSalaries === 0, "Salary report", draftSalaries === 0 ? "No draft salaries" : `${draftSalaries} draft rows`],
      [balanceReady, "Monthly balance", balanceReady ? "Calculated from current data" : "No financial data yet"],
    ];
    return `
      ${renderHeader("Dashboard", "Monthly financial summary, alerts, and closing readiness.")}
      ${closedNotice()}
      ${renderMetrics([
        { label: "Cash CV", value: money(t.cashCv) },
        { label: "Cash C", value: money(t.cashC) },
        { label: "TPE", value: money(t.tpe) },
        { label: "Real Safe Net", value: money(t.realSafeNet) },
        { label: "Global Revenue", value: money(t.globalRevenue) },
        { label: "Profitability", value: money(t.profitability) },
        { label: "Net Profitability", value: money(t.netProfitability) },
        { label: "Supplier Remaining", value: money(t.supplierRemaining) },
      ])}
      ${renderSection(
        "Monthly Alerts",
        `<div class="alert-list">${alerts
          .map(([ok, title, text]) => `<div class="alert-item ${ok ? "ok" : ""}"><strong>${escapeHtml(title)}</strong><span>${escapeHtml(text)}</span></div>`)
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
