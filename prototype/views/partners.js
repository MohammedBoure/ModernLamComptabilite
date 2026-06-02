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
  function renderPartners() {
    return `
      ${renderHeader("Subcontractors & Conventions", "External partners, conventions, payments, and remaining balances.")}
      ${closedNotice()}
      <div class="grid two">
        ${renderForm(
          "Partner Operation",
          "partner",
          [
            { name: "type", label: "Type", type: "select", options: partnerTypes },
            { name: "name", label: "Name", required: true },
            { name: "amount", label: "Amount", type: "number", min: 0, step: "0.01", required: true },
            { name: "payment", label: "Payment", type: "number", min: 0, step: "0.01" },
            { name: "receptionDate", label: "Reception Date", type: "date", value: defaultDate(), required: true },
            { name: "paymentMode", label: "Payment Mode", type: "select", options: ["", ...paymentModes] },
            { name: "remarks", label: "Remarks", type: "textarea", full: true },
          ],
          "Save partner",
          { periodScoped: true }
        )}
        ${renderForm(
          "Partner Payment",
          "partnerPayment",
          [
            { name: "targetId", label: "Partner", type: "select", options: scopedRows("partners").map((row) => [row.id, `${row.name} - ${money(row.remainingBalance)} remaining`]), required: true },
            { name: "date", label: "Date", type: "date", value: defaultDate(), required: true },
            { name: "amount", label: "Amount", type: "number", min: 0, step: "0.01", required: true },
            { name: "paymentMode", label: "Mode", type: "select", options: paymentModes, required: true },
            { name: "reference", label: "Reference" },
            { name: "note", label: "Note", type: "textarea", full: true },
          ],
          "Save payment",
          { periodScoped: true }
        )}
      </div>
      ${renderSection(
        "Partner Statement",
        renderTable(
          [
            { label: "Type", key: "type" },
            { label: "Name", key: "name" },
            { label: "Amount", key: "amount", amount: true, format: money },
            { label: "Payment", key: "payment", amount: true, format: money },
            { label: "Reception Date", key: "receptionDate" },
            { label: "Mode", key: "paymentMode" },
            { label: "Remaining", key: "remainingBalance", amount: true, format: money },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
            { label: "Remarks", key: "remarks" },
          ],
          scopedRows("partners"),
          { collection: "partners" }
        )
      )}
      ${renderSection(
        "Partner Payments",
        renderTable(
          [
            { label: "Date", key: "date" },
            { label: "Target", value: (row) => paymentTargetLabel(row) },
            { label: "Amount", key: "amount", amount: true, format: money },
            { label: "Mode", key: "paymentMode" },
            { label: "Reference", key: "reference" },
            { label: "Note", key: "note" },
          ],
          scopedRows("payments").filter((row) => row.targetType === "partner"),
          { collection: "payments" }
        )
      )}
    `;
  }


  M.registerView('partners', renderPartners);
})();
