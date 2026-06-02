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
    unjustifiedCashDifferences,
    cashDifferenceStatement,
    daysInMonth,
    pad,
    optionList,
    number,
    sum,
    statusPill,
    escapeHtml
  } = M;

  function renderBlockingDifferenceAlert(rows) {
    if (!rows.length) return "";
    return `
      <div class="alert-list">
        <button class="alert-item blocking" type="button" data-view="cashClosing" title="Unjustified cash differences">
          <span class="alert-copy">
            <strong>Unjustified cash differences</strong>
            <span>${rows.length} rows need a remark before closing.</span>
          </span>
          <span class="alert-severity">blocking</span>
        </button>
      </div>
    `;
  }

  function renderCashClosingFilters(dateFilter, userFilter, closures) {
    const users = Array.from(new Set(closures.map((row) => row.user).filter(Boolean))).sort();
    return renderSection(
      "Filters",
      `<div class="filter-bar">
        <label>Date
          <input type="date" value="${escapeHtml(dateFilter)}" data-cash-closing-filter="date">
        </label>
        <label>User
          <select data-cash-closing-filter="user">
            ${optionList([["", "All users"], ...users.map((user) => [user, user])], userFilter)}
          </select>
        </label>
        <button class="text-btn" type="button" data-action="reset-cash-closing-filters" title="Reset filters">Reset</button>
      </div>`
    );
  }

  function renderCashClosing() {
    const expenses = scopedRows("cashExpenses");
    const closures = scopedRows("cashClosures");
    const dateFilter = localStorage.getItem(CASH_CLOSING_DATE_FILTER_KEY) || "";
    const userFilter = localStorage.getItem(CASH_CLOSING_USER_FILTER_KEY) || "";
    const filteredExpenses = expenses.filter((row) => !dateFilter || row.date === dateFilter);
    const filteredClosures = closures.filter((row) => (!dateFilter || row.date === dateFilter) && (!userFilter || row.user === userFilter));
    const summary = cashDifferenceStatement(filteredClosures);
    const blockingRows = unjustifiedCashDifferences();
    return `
      ${renderHeader("Cash Closing", "Cash expenses, real amount control, SOFTLAM comparison, and difference statement.")}
      ${closedNotice()}
      ${renderBlockingDifferenceAlert(blockingRows)}
      ${renderCashClosingFilters(dateFilter, userFilter, closures)}
      <div class="grid two">
        ${renderForm(
          "Cash Expense",
          "cashExpense",
          [
            { name: "date", label: "Date", type: "date", value: defaultDate(), required: true },
            { name: "designation", label: "Designation", required: true, span: 2 },
            { name: "amount", label: "Amount", type: "number", min: 0, step: "0.01", required: true },
            { name: "attachmentRef", label: "Document" },
            { name: "remark", label: "Remark", type: "textarea", full: true },
          ],
          "Save expense",
          { periodScoped: true }
        )}
        ${renderForm(
          "Daily Difference",
          "cashClosure",
          [
            { name: "date", label: "Date", type: "date", value: defaultDate(), required: true },
            { name: "user", label: "User", required: true },
            { name: "realAmount", label: "Real Amount", type: "number", min: 0, step: "0.01", required: true },
            { name: "virtualAmount", label: "Virtual Amount", type: "number", min: 0, step: "0.01", required: true },
            { name: "remark", label: "Remark when difference is not zero", type: "textarea", full: true },
          ],
          "Save difference",
          { periodScoped: true }
        )}
      </div>
      ${renderSection(
        "Cash Expenses",
        renderTable(
          [
            { label: "Date", key: "date" },
            { label: "Designation", key: "designation" },
            { label: "Amount", key: "amount", amount: true, format: money },
            { label: "Document", key: "attachmentRef" },
            { label: "Remark", key: "remark" },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
          ],
          filteredExpenses,
          { collection: "cashExpenses" }
        )
      )}
      ${renderSection(
        "Differences",
        renderTable(
          [
            { label: "Date", key: "date" },
            { label: "User", key: "user" },
            { label: "Real", key: "realAmount", amount: true, format: money },
            { label: "Virtual", key: "virtualAmount", amount: true, format: money },
            { label: "Difference", key: "difference", amount: true, format: money },
            { label: "Remark", key: "remark" },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
          ],
          filteredClosures,
          { collection: "cashClosures" }
        )
      )}
      ${renderSection(
        "Difference Statement by User",
        renderTable(
          [
            { label: "User", key: "user" },
            { label: "Entries", key: "count" },
            { label: "Positive Difference", key: "positiveDifference", amount: true, format: money },
            { label: "Negative Difference", key: "negativeDifference", amount: true, format: money },
            { label: "Net", key: "net", amount: true, format: money },
          ],
          summary,
          { empty: "No differences recorded." }
        )
      )}
    `;
  }


  M.registerView('cashClosing', renderCashClosing);
})();
