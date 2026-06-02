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
    employeeFunction,
    daysInMonth,
    pad,
    optionList,
    number,
    sum,
    statusPill,
    escapeHtml
  } = M;
  function renderSuppliers() {
    const supplierOptions = state.suppliers.map((supplier) => [supplier.id, supplier.name]);
    const transactionOptions = scopedRows("supplierTransactions").map((row) => [row.id, `${supplierName(row.supplierId)} - ${money(row.remainingAmount)} remaining`]);
    return `
      ${renderHeader("Suppliers", "Supplier register, invoices, payments, and remaining balances.")}
      ${closedNotice()}
      <div class="grid three">
        ${renderForm(
          "Supplier",
          "supplier",
          [
            { name: "name", label: "Supplier LAM", required: true, span: 2 },
            { name: "category", label: "Category", type: "select", options: supplierCategories },
            { name: "phone", label: "Phone" },
            { name: "address", label: "Address", span: 2 },
            { name: "notes", label: "Notes", type: "textarea", full: true },
          ],
          "Save supplier"
        )}
        ${renderForm(
          "Invoice or Order",
          "supplierTransaction",
          [
            { name: "supplierId", label: "Supplier", type: "select", options: supplierOptions, required: true },
            { name: "category", label: "Category", type: "select", options: supplierCategories },
            { name: "date", label: "Date", type: "date", value: defaultDate(), required: true },
            { name: "orderTotal", label: "Order Total", type: "number", min: 0, step: "0.01", required: true },
            { name: "paidAmount", label: "Paid", type: "number", min: 0, step: "0.01" },
            { name: "paymentMode", label: "Payment Mode", type: "select", options: ["", ...paymentModes] },
            { name: "reference", label: "Reference" },
            { name: "observation", label: "Observation", type: "textarea", full: true },
          ],
          "Save invoice",
          { periodScoped: true }
        )}
        ${renderForm(
          "Payment",
          "supplierPayment",
          [
            { name: "targetId", label: "Invoice", type: "select", options: transactionOptions, required: true },
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
        "Suppliers",
        renderTable(
          [
            { label: "Supplier", key: "name" },
            { label: "Category", key: "category" },
            { label: "Phone", key: "phone" },
            { label: "Address", key: "address" },
            { label: "Active", value: (row) => (row.isActive ? "Yes" : "No") },
          ],
          state.suppliers,
          { collection: "suppliers" }
        )
      )}
      ${renderSection(
        "Invoices and Orders",
        renderTable(
          [
            { label: "Date", key: "date" },
            { label: "Supplier", value: (row) => supplierName(row.supplierId) },
            { label: "Category", key: "category" },
            { label: "Order Total", key: "orderTotal", amount: true, format: money },
            { label: "Paid", key: "paidAmount", amount: true, format: money },
            { label: "Remaining", key: "remainingAmount", amount: true, format: money },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
            { label: "Observation", key: "observation" },
          ],
          scopedRows("supplierTransactions"),
          { collection: "supplierTransactions" }
        )
      )}
      ${renderSection(
        "Payments",
        renderTable(
          [
            { label: "Date", key: "date" },
            { label: "Target", value: (row) => paymentTargetLabel(row) },
            { label: "Amount", key: "amount", amount: true, format: money },
            { label: "Mode", key: "paymentMode" },
            { label: "Reference", key: "reference" },
            { label: "Note", key: "note" },
          ],
          scopedRows("payments").filter((row) => row.targetType === "supplier"),
          { collection: "payments" }
        )
      )}
    `;
  }

  function paymentTargetLabel(row) {
    if (row.targetType === "supplier") {
      const tx = state.supplierTransactions.find((item) => item.id === row.targetId);
      return tx ? supplierName(tx.supplierId) : "Supplier transaction";
    }
    const partner = state.partners.find((item) => item.id === row.targetId);
    return partner ? partner.name : "Partner";
  }


  M.registerView('suppliers', renderSuppliers);
})();
