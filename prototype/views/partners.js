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

  function renderPartnerFilters(typeFilter) {
    return renderSection(
      "Filters",
      `<div class="filter-bar">
        <label>Type
          <select data-partner-filter="type">
            ${optionList([["", "All types"], ...partnerTypes.map((type) => [type, type])], typeFilter)}
          </select>
        </label>
        <button class="text-btn" type="button" data-action="reset-partner-filters" title="Reset partner filters">Reset</button>
      </div>`
    );
  }

  function renderPartners() {
    const typeFilter = localStorage.getItem(PARTNER_TYPE_FILTER_KEY) || "";
    const filteredPartners = scopedRows("partners").filter((row) => !typeFilter || row.type === typeFilter);
    const visiblePartnerIds = new Set(filteredPartners.map((row) => row.id));
    const filteredPayments = scopedRows("payments").filter((row) => row.targetType === "partner" && visiblePartnerIds.has(row.targetId));
    const remainingTotal = sum(filteredPartners, "remainingBalance");
    return `
      ${renderHeader("Subcontractors & Conventions", "External partners, conventions, payments, and remaining balances.")}
      ${closedNotice()}
      ${renderPartnerFilters(typeFilter)}
      ${renderMetrics([
        { label: "Filtered Remaining", value: money(remainingTotal), detail: typeFilter || "All partner types" },
        { label: "Filtered Partners", value: filteredPartners.length, detail: "Visible rows" },
      ])}
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
            {
              name: "targetId",
              label: "Partner",
              type: "select",
              options: scopedRows("partners")
                .filter((row) => number(row.remainingBalance) > 0)
                .map((row) => [row.id, `${row.name} - ${money(row.remainingBalance)} remaining`]),
              required: true,
            },
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
          filteredPartners,
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
          filteredPayments,
          { collection: "payments" }
        )
      )}
    `;
  }


  M.registerView('partners', renderPartners);
})();
