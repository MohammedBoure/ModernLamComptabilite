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
  function renderBalance() {
    const t = totals();
    const rows = [
      ["Cash CV", t.cashCv],
      ["Cash C", t.cashC],
      ["Convention", t.conventionRevenue],
      ["Subcontracting", t.subcontractorRevenue],
      ["Additional Entries", t.paidAdditional],
      ["Revenue", t.globalRevenue],
      ["Expenses", t.expensesTotal],
      ["Profitability", t.profitability],
      ["Investments", t.investments],
      ["Net Profitability", t.netProfitability],
      ["Real Safe Net", t.realSafeNet],
    ].map(([indicator, value]) => ({ indicator, value }));
    return `
      ${renderHeader("Monthly Balance", "Calculated financial balance for the selected month.")}
      ${renderSection(
        "Monthly Result",
        renderMetrics([
          { label: "Revenue", value: money(t.globalRevenue) },
          { label: "Expenses", value: money(t.expensesTotal) },
          { label: "Profitability", value: money(t.profitability) },
          { label: "Investments", value: money(t.investments) },
          { label: "Net Profitability", value: money(t.netProfitability) },
          { label: "Real Safe Net", value: money(t.realSafeNet) },
        ])
      )}
      ${renderSection(
        "Balance Lines",
        renderTable(
          [
            { label: "Indicator", key: "indicator" },
            { label: "Value", key: "value", amount: true, format: money },
          ],
          rows
        )
      )}
    `;
  }


  M.registerView('balance', renderBalance);
})();
