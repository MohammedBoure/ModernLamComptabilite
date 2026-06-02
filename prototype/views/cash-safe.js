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
    renderAssumptionNotice,
    renderTable,
    scopedRows,
    renderForm,
    defaultDate,
    currentPeriodKey,
    supplierName,
    employeeName,
    paymentTargetLabel,
    employeeFunction,
    cashMovementStats,
    safeSummaryTrace,
    daysInMonth,
    pad,
    optionList,
    number,
    sum,
    statusPill,
    escapeHtml
  } = M;

  function renderSafeSourceTrace(rows) {
    return renderTable(
      [
        { label: "Metric", key: "metric" },
        { label: "Value", key: "value", amount: true, format: money },
        { label: "Source Tables", key: "sourceTables" },
        { label: "Values In", key: "incoming" },
        { label: "Values Out", key: "outgoing" },
        { label: "Formula", key: "formula" },
      ],
      rows,
      { empty: "No source trace yet." }
    );
  }

  function renderCashSafe() {
    const t = totals();
    const traceRows = safeSummaryTrace();
    return `
      ${renderHeader("Cash & Safe", "Daily cash movement, additional entries, safe exits, profitability movements, and safe summary.")}
      ${closedNotice()}
      ${renderAssumptionNotice("Prototype assumptions - accounting decisions still tracked", [
        "LAM Revenue formula is not final.",
        "Cash CV/Cash C roles are shown as source columns only.",
        "TPE treatment remains an open decision.",
        "Additional Entries are counted as paid-only prototype revenue until confirmed.",
      ])}
      <div class="grid two">
        ${renderForm(
          "Cash Movement",
          "cashMovement",
          [
            { name: "date", label: "Date", type: "date", value: defaultDate(), required: true },
            { name: "cashCv", label: "Cash CV", type: "number", min: 0, step: "0.01" },
            { name: "cashC", label: "Cash C", type: "number", min: 0, step: "0.01" },
            { name: "tpe", label: "TPE", type: "number", min: 0, step: "0.01" },
            { name: "expenses", label: "Expenses", type: "number", min: 0, step: "0.01" },
            { name: "reimbursement", label: "Reimbursement", type: "number", min: 0, step: "0.01" },
            { name: "convention", label: "Convention", type: "number", min: 0, step: "0.01" },
            { name: "subcontractors", label: "Subcontractors", type: "number", min: 0, step: "0.01" },
            { name: "remark", label: "Remark", type: "textarea", full: true },
          ],
          "Save movement",
          { periodScoped: true }
        )}
        ${renderForm(
          "Additional Entry",
          "additionalEntry",
          [
            { name: "date", label: "Date", type: "date", value: defaultDate(), required: true },
            { name: "amount", label: "Amount", type: "number", min: 0, step: "0.01", required: true },
            { name: "detail", label: "Detail", required: true },
            { name: "paymentStatus", label: "Payment Status", type: "select", options: paymentStatuses, value: "Paid" },
            { name: "remark", label: "Remark", type: "textarea", full: true },
          ],
          "Save entry",
          { periodScoped: true }
        )}
        ${renderForm(
          "Safe Exit",
          "safeExit",
          [
            { name: "date", label: "Date", type: "date", value: defaultDate(), required: true },
            { name: "designation", label: "Designation", required: true },
            { name: "amount", label: "Amount", type: "number", min: 0, step: "0.01", required: true },
            { name: "category", label: "Category", type: "select", options: supplierCategories, value: "Internal Expenses" },
            { name: "attachmentRef", label: "Attachment" },
            { name: "remark", label: "Remark", type: "textarea", full: true },
          ],
          "Save exit",
          { periodScoped: true }
        )}
        ${renderForm(
          "Profitability Movement",
          "profitabilityMovement",
          [
            { name: "date", label: "Date", type: "date", value: defaultDate(), required: true },
            { name: "amount", label: "Amount", type: "number", step: "0.01", required: true },
            { name: "detail", label: "Detail", required: true },
            { name: "movementType", label: "Type", type: "select", options: ["Entry", "Exit", "Carry-over"], value: "Entry" },
            { name: "sourcePeriod", label: "Source Period" },
            { name: "destinationPeriod", label: "Destination Period", value: currentPeriodKey() },
          ],
          "Save movement",
          { periodScoped: true }
        )}
      </div>
      ${renderSection(
        "Safe Summary",
        renderMetrics([
          { label: "Real Safe Net", value: money(t.realSafeNet), detail: "Formula trace below" },
          { label: "LAM Revenue", value: money(t.lamRevenue), detail: "Prototype assumption only" },
          { label: "Convention Revenue", value: money(t.conventionRevenue), detail: "Cash movement + paid convention" },
          { label: "Subcontractor Revenue", value: money(t.subcontractorRevenue), detail: "Cash movement + paid subcontractors" },
          { label: "Additional Entry Revenue", value: money(t.paidAdditional), detail: "Prototype paid-only assumption" },
          { label: "Global Revenue", value: money(t.globalRevenue), detail: "Summary total" },
        ])
      )}
      ${renderSection("Safe Summary Source Trace", renderSafeSourceTrace(traceRows))}
      ${renderSection(
        "Cash Movement Calculations (-Friday)",
        renderTable(
          [
            { label: "Column", key: "label" },
            { label: "Total (-Fri)", key: "total", amount: true, format: money },
            { label: "Min (-Fri)", key: "min", amount: true, format: money },
            { label: "Max (-Fri)", key: "max", amount: true, format: money },
            { label: "Average (-Fri)", key: "average", amount: true, format: money },
            { label: "Rows Used", key: "rowsUsed" },
            { label: "Fridays Excluded", key: "fridayRows" },
          ],
          cashMovementStats(),
          { empty: "No cash movement calculations yet." }
        )
      )}
      ${renderSection(
        "Cash Movements",
        renderTable(
          [
            { label: "Date", key: "date" },
            { label: "Cash CV", key: "cashCv", amount: true, format: money },
            { label: "Cash C", key: "cashC", amount: true, format: money },
            { label: "TPE", key: "tpe", amount: true, format: money },
            { label: "Expenses", key: "expenses", amount: true, format: money },
            { label: "Reimbursement", key: "reimbursement", amount: true, format: money },
            { label: "Convention", key: "convention", amount: true, format: money },
            { label: "Subcontractors", key: "subcontractors", amount: true, format: money },
            { label: "Total", key: "total", amount: true, format: money },
          ],
          scopedRows("cashMovements"),
          { collection: "cashMovements" }
        )
      )}
      ${renderSection(
        "Additional Entries",
        renderTable(
          [
            { label: "Date", key: "date" },
            { label: "Amount", key: "amount", amount: true, format: money },
            { label: "Detail", key: "detail" },
            { label: "Payment", key: "paymentStatus" },
            { label: "Remark", key: "remark" },
          ],
          scopedRows("additionalEntries"),
          { collection: "additionalEntries" }
        )
      )}
      <div class="safe-ledger-grid">
        ${renderSection(
          "Safe Exits",
          renderTable(
            [
              { label: "Date", key: "date" },
              { label: "Designation", key: "designation" },
              { label: "Amount", key: "amount", amount: true, format: money },
              { label: "Category", key: "category" },
              { label: "Attachment", key: "attachmentRef" },
              { label: "Remark", key: "remark" },
            ],
            scopedRows("safeExits"),
            { collection: "safeExits" }
          )
        )}
        ${renderSection(
          "Profitability Movements",
          renderTable(
            [
              { label: "Date", key: "date" },
              { label: "Amount", key: "amount", amount: true, format: money },
              { label: "Detail", key: "detail" },
              { label: "Type", key: "movementType" },
              { label: "Source", key: "sourcePeriod" },
              { label: "Destination", key: "destinationPeriod" },
            ],
            scopedRows("profitabilityMovements"),
            { collection: "profitabilityMovements" }
          )
        )}
      </div>
    `;
  }


  M.registerView('cashSafe', renderCashSafe);
})();
