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
