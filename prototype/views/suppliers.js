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

  function renderSupplierFilters(filters) {
    return renderSection(
      "Filters",
      `<div class="filter-bar">
        <label>Supplier
          <input type="search" value="${escapeHtml(filters.supplier)}" placeholder="Search supplier" data-supplier-filter="supplier">
        </label>
        <label>Category
          <select data-supplier-filter="category">
            ${optionList([["", "All categories"], ...supplierCategories.map((category) => [category, category])], filters.category)}
          </select>
        </label>
        <label>Status
          <select data-supplier-filter="status">
            ${optionList([["", "All statuses"], ...paymentStatuses.map((status) => [status, status])], filters.status)}
          </select>
        </label>
        <button class="text-btn" type="button" data-action="reset-supplier-filters" title="Reset supplier filters">Reset</button>
      </div>`
    );
  }

  function renderSuppliers() {
    const filters = {
      supplier: localStorage.getItem(SUPPLIER_FILTER_KEY) || "",
      category: localStorage.getItem(SUPPLIER_CATEGORY_FILTER_KEY) || "",
      status: localStorage.getItem(SUPPLIER_STATUS_FILTER_KEY) || "",
    };
    const supplierQuery = filters.supplier.trim().toLowerCase();
    const filteredSuppliers = state.suppliers.filter((supplier) => {
      const matchesSupplier = !supplierQuery || supplier.name.toLowerCase().includes(supplierQuery);
      const matchesCategory = !filters.category || supplier.category === filters.category;
      return matchesSupplier && matchesCategory;
    });
    const searchedSupplierIds = new Set(
      state.suppliers.filter((supplier) => !supplierQuery || supplier.name.toLowerCase().includes(supplierQuery)).map((supplier) => supplier.id)
    );
    const filteredTransactions = scopedRows("supplierTransactions").filter((row) => {
      const matchesSupplier = !supplierQuery || searchedSupplierIds.has(row.supplierId);
      const matchesCategory = !filters.category || row.category === filters.category;
      const matchesStatus = !filters.status || row.status === filters.status;
      return matchesSupplier && matchesCategory && matchesStatus;
    });
    const visibleTransactionIds = new Set(filteredTransactions.map((row) => row.id));
    const filteredPayments = scopedRows("payments").filter((row) => row.targetType === "supplier" && visibleTransactionIds.has(row.targetId));
    const supplierOptions = state.suppliers.map((supplier) => [supplier.id, supplier.name]);
    const transactionOptions = scopedRows("supplierTransactions")
      .filter((row) => number(row.remainingAmount) > 0)
      .map((row) => [row.id, `${supplierName(row.supplierId)} - ${money(row.remainingAmount)} remaining`]);
    return `
      ${renderHeader("Suppliers", "Supplier register, invoices, payments, and remaining balances.")}
      ${closedNotice()}
      ${renderSupplierFilters(filters)}
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
          filteredSuppliers,
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
            { label: "Mode", key: "paymentMode" },
            { label: "Reference", key: "reference" },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
            { label: "Observation", key: "observation" },
          ],
          filteredTransactions,
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
          filteredPayments,
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
