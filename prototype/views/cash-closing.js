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
  function renderCashClosing() {
    const expenses = scopedRows("cashExpenses");
    const closures = scopedRows("cashClosures");
    const summary = Object.values(
      closures.reduce((acc, row) => {
        acc[row.user] ||= { user: row.user, net: 0, count: 0 };
        acc[row.user].net += number(row.difference);
        acc[row.user].count += 1;
        return acc;
      }, {})
    );
    return `
      ${renderHeader("Cash Closing", "Cash expenses, real amount control, SOFTLAM comparison, and difference statement.")}
      ${closedNotice()}
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
            { name: "remark", label: "Remark", type: "textarea", full: true },
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
          expenses,
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
          closures,
          { collection: "cashClosures" }
        )
      )}
      ${renderSection(
        "Difference Statement",
        renderTable(
          [
            { label: "User", key: "user" },
            { label: "Entries", key: "count" },
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
