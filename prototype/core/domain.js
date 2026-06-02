"use strict";

function activeRows(collection) {
  return state[collection].filter((row) => row.status !== "Cancelled");
}

function scopedRows(collection) {
  const key = currentPeriodKey();
  return activeRows(collection).filter((row) => row.periodKey === key);
}

function employeeName(employeeId) {
  const employee = state.employees.find((item) => item.id === employeeId);
  return employee ? employee.fullName : "Unknown employee";
}

function supplierName(supplierId) {
  const supplier = state.suppliers.find((item) => item.id === supplierId);
  return supplier ? supplier.name : "Unknown supplier";
}

function paymentTargetLabel(row) {
  if (row.targetType === "supplier") {
    const tx = state.supplierTransactions.find((item) => item.id === row.targetId);
    return tx ? supplierName(tx.supplierId) : "Supplier transaction";
  }
  const partner = state.partners.find((item) => item.id === row.targetId);
  return partner ? partner.name : "Partner";
}

function employeeFunction(employeeId) {
  const employee = state.employees.find((row) => row.id === employeeId);
  return employee ? employee.function : "";
}

function audit(action, entityType, entityId, newValues = "", oldValues = "", reason = "") {
  state.auditLogs.unshift({
    id: id(),
    user: "Admin",
    action,
    entityType,
    entityId,
    oldValues: typeof oldValues === "string" ? oldValues : JSON.stringify(oldValues),
    newValues: typeof newValues === "string" ? newValues : JSON.stringify(newValues),
    reason,
    createdAt: new Date().toISOString(),
  });
}

function addRecord(collection, record, action = "Create") {
  const saved = {
    id: id(),
    createdAt: new Date().toISOString(),
    ...record,
  };
  if (periodCollections.has(collection)) saved.periodKey = currentPeriodKey();
  state[collection].push(saved);
  audit(action, collection, saved.id, saved);
  saveState();
  showToast("Saved in browser storage.");
  render();
  return saved;
}

function cancelRecord(collection, recordId) {
  const row = state[collection].find((item) => item.id === recordId);
  if (!row) return;
  if (periodCollections.has(collection) && isClosedPeriod()) {
    showToast("Closed period is read-only.");
    return;
  }
  const before = { ...row };
  if (collection === "payments" && row.status !== "Cancelled") {
    if (row.targetType === "supplier") {
      const transaction = state.supplierTransactions.find((item) => item.id === row.targetId);
      if (transaction) {
        transaction.paidAmount = Math.max(0, number(transaction.paidAmount) - number(row.amount));
        updateSupplierStatus(transaction);
      }
    }
    if (row.targetType === "partner") {
      const partner = state.partners.find((item) => item.id === row.targetId);
      if (partner) {
        partner.payment = Math.max(0, number(partner.payment) - number(row.amount));
        updatePartnerStatus(partner);
      }
    }
  }
  if ("status" in row) row.status = "Cancelled";
  else state[collection] = state[collection].filter((item) => item.id !== recordId);
  audit("Cancel", collection, recordId, row, before);
  saveState();
  showToast("Record cancelled.");
  render();
}

function closedNotice() {
  return isClosedPeriod() ? `<div class="read-only-note">This month is closed. Period data is displayed as read-only.</div>` : "";
}

function totals() {
  const movements = scopedRows("cashMovements");
  const expenses = scopedRows("cashExpenses");
  const additional = scopedRows("additionalEntries");
  const exits = scopedRows("safeExits");
  const profitMovements = scopedRows("profitabilityMovements");
  const supplierTransactions = scopedRows("supplierTransactions");
  const partners = scopedRows("partners");
  const cashCv = sum(movements, "cashCv");
  const cashC = sum(movements, "cashC");
  const tpe = sum(movements, "tpe");
  const movementExpenses = sum(movements, "expenses");
  const cashExpenseTotal = sum(expenses, "amount");
  const safeExitsTotal = sum(exits, "amount");
  const paidAdditional = sum(additional.filter((row) => row.paymentStatus === "Paid"), "amount");
  const profitMovementTotal = sum(profitMovements, "amount");
  const paidSubcontractors = sum(partners.filter((row) => row.type === "Subcontractor"), "payment");
  const paidConvention = sum(partners.filter((row) => row.type === "Convention"), "payment");
  const conventionRevenue = sum(movements, "convention") + paidConvention;
  const subcontractorRevenue = sum(movements, "subcontractors") + paidSubcontractors;
  const realSafeNet = cashCv + cashC + paidAdditional + profitMovementTotal + paidSubcontractors + paidConvention - safeExitsTotal;
  const lamRevenue = cashC + cashC + movementExpenses;
  const globalRevenue = realSafeNet + lamRevenue + conventionRevenue + subcontractorRevenue + paidAdditional;
  const supplierExpenseTotal = sum(supplierTransactions, "orderTotal");
  const expensesTotal = movementExpenses + cashExpenseTotal + safeExitsTotal + supplierExpenseTotal;
  const investments = sum(supplierTransactions.filter((row) => row.category === "Investment"), "orderTotal") + sum(exits.filter((row) => row.category === "Investment"), "amount");
  const profitability = globalRevenue - expensesTotal;
  const netProfitability = profitability - investments;
  return {
    cashCv,
    cashC,
    tpe,
    movementExpenses,
    cashExpenseTotal,
    safeExitsTotal,
    paidAdditional,
    profitMovementTotal,
    paidSubcontractors,
    paidConvention,
    conventionRevenue,
    subcontractorRevenue,
    realSafeNet,
    lamRevenue,
    globalRevenue,
    supplierExpenseTotal,
    expensesTotal,
    investments,
    profitability,
    netProfitability,
    supplierRemaining: supplierTransactions.reduce((total, row) => total + number(row.remainingAmount), 0),
  };
}

function latestUpdate() {
  const dates = state.auditLogs.map((row) => new Date(row.createdAt).getTime()).filter(Number.isFinite);
  if (!dates.length) return "";
  return new Date(Math.max(...dates)).toLocaleString();
}

function hasActiveContract(employeeId) {
  return state.contracts.some((row) => row.employeeId === employeeId && row.status === "Active");
}

function closingChecklist() {
  const t = totals();
  const unjustified = scopedRows("cashClosures").filter((row) => number(row.difference) !== 0 && !row.remark.trim()).length;
  const draftSalaries = scopedRows("salaryReports").filter((row) => row.status === "Draft").length;
  const reportsGenerated = state.reportExports.some((row) => row.period === currentPeriodKey());
  const balanceCalculated = t.globalRevenue !== 0 || t.expensesTotal !== 0;
  const draftFinancial = [
    "cashExpenses",
    "cashClosures",
    "cashMovements",
    "additionalEntries",
    "safeExits",
    "profitabilityMovements",
    "supplierTransactions",
    "partners",
  ].reduce((count, collection) => count + scopedRows(collection).filter((row) => row.status === "Draft").length, 0);
  return [
    {
      key: "differences",
      item: "Justified differences",
      ok: unjustified === 0,
      detail: unjustified === 0 ? "All differences are justified." : `${unjustified} cash difference rows need remarks.`,
    },
    {
      key: "reports",
      item: "Generated reports",
      ok: reportsGenerated,
      detail: reportsGenerated ? "At least one official/export trace exists for this period." : "Generate or export a report before closing.",
    },
    {
      key: "salaries",
      item: "No Draft salaries",
      ok: draftSalaries === 0,
      detail: draftSalaries === 0 ? "Salary rows are validated or paid." : `${draftSalaries} salary rows are still Draft.`,
    },
    {
      key: "remaining",
      item: "Visible remaining balances",
      ok: true,
      detail: `Supplier remaining: ${money(t.supplierRemaining)}; partner remaining: ${money(sum(scopedRows("partners"), "remainingBalance"))}.`,
    },
    {
      key: "balance",
      item: "Calculated balance",
      ok: balanceCalculated,
      detail: balanceCalculated ? "Monthly balance can be calculated from current data." : "No financial source data exists yet.",
    },
    {
      key: "draftFinancial",
      item: "No Draft financial operations",
      ok: draftFinancial === 0,
      detail: draftFinancial === 0 ? "Financial rows are final enough for closing." : `${draftFinancial} financial rows are still Draft.`,
    },
  ];
}

function cashMovementStats() {
  const rows = scopedRows("cashMovements");
  const nonFriday = rows.filter((row) => {
    if (!row.date) return true;
    return new Date(row.date).getDay() !== 5;
  });
  const metrics = [
    ["cashCv", "Cash CV"],
    ["cashC", "Cash C"],
    ["tpe", "TPE"],
    ["expenses", "Expenses"],
    ["reimbursement", "Reimbursement"],
    ["convention", "Convention"],
    ["subcontractors", "Subcontractors"],
    ["total", "Total"],
  ];
  return metrics.map(([key, label]) => {
    const values = nonFriday.map((row) => number(row[key]));
    const total = sum(rows, key);
    const min = values.length ? Math.min(...values) : 0;
    const max = values.length ? Math.max(...values) : 0;
    const average = values.length ? values.reduce((acc, value) => acc + value, 0) / values.length : 0;
    return { label, total, min, max, average };
  });
}

function documentationCoverage() {
  return [
    ["Product overview", "Dashboard, modules, users, period status, and browser-only prototype scope are represented.", "Covered"],
    ["Navigation and layout", "Top bar, period selectors, side menu, content area, actions, statuses, and read-only closed month state.", "Covered"],
    ["Dashboard", "Summary cards, period status, last update, source-calculated values, and all documented alert types.", "Covered"],
    ["Accounting interfaces", "Cash Closing, Cash & Safe, Monthly Balance, Suppliers, Partners, Attendance, and Salaries.", "Covered"],
    ["Reports and statements", "Cash expenses, differences, cash/safe movement, balance, suppliers, partners, attendance, salary, vehicle, cheque, encashment, employees, contracts, leave.", "Covered"],
    ["HR interfaces", "Employee identity, contracts, leave, attendance and salary links, status and alerts.", "Covered"],
    ["Workflows", "New month creation, daily cash, supplier payments, attendance/salary generation, monthly closing checklist, closed-month read-only behavior.", "Covered"],
    ["Data model", "Every documented conceptual table has browser-storage collections or calculated rows.", "Covered"],
    ["Business rules", "Difference, remaining balance, safe net, revenue, profitability, salary and leave calculations are represented.", "Covered"],
    ["Permissions and audit", "Roles, permission matrix, users, audit log, closed-month protection and close/reopen tracing.", "Covered"],
    ["Reporting and printing", "Preview, print, official trace, CSV export, history, totals, stamp/signature and lab identity.", "Covered"],
    ["Implementation roadmap", "MVP and later phases are represented as prototype modules without selecting a final stack.", "Covered"],
    ["Open questions", "Unresolved decisions are listed in Administration so they remain visible before real implementation.", "Tracked"],
  ].map((row) => ({ area: row[0], prototypeCoverage: row[1], status: row[2] }));
}

function openQuestions() {
  return [
    ["Accounting", "Exact LAM Revenue formula; Cash CV/Cash C roles; TPE treatment; Additional Entries treatment; partner recognition timing."],
    ["SOFTLAM", "Virtual Amount source; manual entry or import; export format; difference by user or cash desk."],
    ["Suppliers", "Multi-category supplier; partial payment per invoice; invoice/purchase slip need; attachment requirement."],
    ["Salaries", "Official final salary formula; absence unit; guard prices; leave/sick leave treatment; advance carry-over."],
    ["Leave", "Day 15 rule; yearly carry-over; sick leave treatment; leave validation authorization."],
    ["Reports", "PDF identical to Excel or adapted; stamp/signature scope; encashment amount source; cheque running balance."],
    ["Permissions", "Roles allowed to close/reopen; Direction modification rights; HR financial visibility; Accountant employee visibility."],
  ].map((row) => ({ category: row[0], question: row[1] }));
}
