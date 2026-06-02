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

function prototypeSettings() {
  const settings = state.settings || {};
  return {
    labName: settings.labName || defaultPrototypeSettings.labName,
    nif: settings.nif || defaultPrototypeSettings.nif,
    rip: settings.rip || defaultPrototypeSettings.rip,
    currentUserDisplayName: settings.currentUserDisplayName || defaultPrototypeSettings.currentUserDisplayName,
  };
}

function currentUserDisplayName() {
  return prototypeSettings().currentUserDisplayName;
}

function auditOperation(row) {
  const action = String(row.action || "").toLowerCase();
  if (action.includes("permission")) return "Permission change";
  if (action.includes("reopening")) return "Reopening closed month";
  if (action.includes("monthly closing") || action.includes("closing blocked")) return "Monthly closing";
  if (action.includes("salary validation")) return "Salary validation";
  if (action.includes("cancel")) return "Cancellation";
  if (action.includes("update") || action.includes("replace") || action.includes("payment") || action.includes("settings")) return "Modification";
  if (action.includes("create") || action.includes("seed") || action.includes("generate")) return "Creation";
  return "Audit";
}

function audit(action, entityType, entityId, newValues = "", oldValues = "", reason = "") {
  state.auditLogs.unshift({
    id: id(),
    user: currentUserDisplayName(),
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
  const movementConvention = sum(movements, "convention");
  const movementSubcontractors = sum(movements, "subcontractors");
  const cashExpenseTotal = sum(expenses, "amount");
  const safeExitsTotal = sum(exits, "amount");
  const paidAdditional = sum(additional.filter((row) => row.paymentStatus === "Paid"), "amount");
  const excludedAdditional = sum(additional.filter((row) => row.paymentStatus !== "Paid"), "amount");
  const profitMovementTotal = sum(profitMovements, "amount");
  const paidSubcontractors = sum(partners.filter((row) => row.type === "Subcontractor"), "payment");
  const paidConvention = sum(partners.filter((row) => row.type === "Convention"), "payment");
  const conventionRevenue = movementConvention + paidConvention;
  const subcontractorRevenue = movementSubcontractors + paidSubcontractors;
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
    movementConvention,
    movementSubcontractors,
    cashExpenseTotal,
    safeExitsTotal,
    paidAdditional,
    excludedAdditional,
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

function unjustifiedCashDifferences(rows = scopedRows("cashClosures")) {
  return rows.filter((row) => number(row.difference) !== 0 && !String(row.remark || "").trim());
}

function cashDifferenceStatement(rows = scopedRows("cashClosures")) {
  const statement = Object.values(
    rows.reduce((acc, row) => {
      const user = row.user || "Unknown user";
      const difference = number(row.difference);
      acc[user] ||= {
        user,
        count: 0,
        positiveDifference: 0,
        negativeDifference: 0,
        net: 0,
      };
      acc[user].count += 1;
      if (difference > 0) acc[user].positiveDifference += difference;
      if (difference < 0) acc[user].negativeDifference += difference;
      acc[user].net += difference;
      return acc;
    }, {})
  ).sort((a, b) => a.user.localeCompare(b.user));
  if (statement.length < 2) return statement;
  statement.push({
    user: "Total",
    count: sum(statement, "count"),
    positiveDifference: sum(statement, "positiveDifference"),
    negativeDifference: sum(statement, "negativeDifference"),
    net: sum(statement, "net"),
  });
  return statement;
}

function closingChecklist() {
  const t = totals();
  const unjustified = unjustifiedCashDifferences().length;
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
  const fridayRows = rows.length - nonFriday.length;
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
    const total = sum(nonFriday, key);
    const min = values.length ? Math.min(...values) : 0;
    const max = values.length ? Math.max(...values) : 0;
    const average = values.length ? values.reduce((acc, value) => acc + value, 0) / values.length : 0;
    return { label, total, min, max, average, rowsUsed: nonFriday.length, fridayRows };
  });
}

function safeSummaryTrace() {
  const t = totals();
  return [
    {
      metric: "Real Safe Net",
      value: t.realSafeNet,
      sourceTables: "cash_movements, additional_entries, profitability_movements, partners, safe_exits",
      incoming: `Cash CV ${money(t.cashCv)} + Cash C ${money(t.cashC)} + Paid Additional Entries ${money(t.paidAdditional)} + Profitability Movement ${money(t.profitMovementTotal)} + Paid Subcontractors ${money(t.paidSubcontractors)} + Paid Convention ${money(t.paidConvention)}`,
      outgoing: `Safe Exits ${money(t.safeExitsTotal)}`,
      formula: "Prototype assumption: Cash CV + Cash C + Paid Additional Entries + Profitability Movement + Paid Subcontractors + Paid Convention - Safe Exits",
    },
    {
      metric: "LAM Revenue",
      value: t.lamRevenue,
      sourceTables: "cash_movements",
      incoming: `Cash C ${money(t.cashC)} + Cash C ${money(t.cashC)} + Cash Movement Expenses ${money(t.movementExpenses)}`,
      outgoing: "No outgoing value in the prototype formula.",
      formula: "Prototype only: Cash C + Cash C + Expenses. Final rule is still tracked as an open question.",
    },
    {
      metric: "Convention Revenue",
      value: t.conventionRevenue,
      sourceTables: "cash_movements, partners",
      incoming: `Cash Movement Convention ${money(t.movementConvention)} + Paid Convention ${money(t.paidConvention)}`,
      outgoing: "No outgoing value.",
      formula: "Convention + Paid Convention",
    },
    {
      metric: "Subcontractor Revenue",
      value: t.subcontractorRevenue,
      sourceTables: "cash_movements, partners",
      incoming: `Cash Movement Subcontractors ${money(t.movementSubcontractors)} + Paid Subcontractors ${money(t.paidSubcontractors)}`,
      outgoing: "No outgoing value.",
      formula: "Subcontractors + Paid Subcontractors",
    },
    {
      metric: "Additional Entry Revenue",
      value: t.paidAdditional,
      sourceTables: "additional_entries",
      incoming: `Paid Additional Entries ${money(t.paidAdditional)}`,
      outgoing: `Unpaid or partial additional entries excluded ${money(t.excludedAdditional)}`,
      formula: "Prototype assumption: only Paid additional entries are counted until Additional Entries treatment is confirmed.",
    },
    {
      metric: "Global Revenue",
      value: t.globalRevenue,
      sourceTables: "safe_summary",
      incoming: `Real Safe Net ${money(t.realSafeNet)} + LAM Revenue ${money(t.lamRevenue)} + Convention Revenue ${money(t.conventionRevenue)} + Subcontractor Revenue ${money(t.subcontractorRevenue)} + Additional Entry Revenue ${money(t.paidAdditional)}`,
      outgoing: "No outgoing value.",
      formula: "Prototype assumption: Real Safe Net + LAM Revenue + Convention Revenue + Subcontractor Revenue + Additional Entry Revenue",
    },
  ];
}

function documentationCoverage() {
  return [
    {
      source: "spec/01, accounting/general/01",
      area: "Product overview",
      requirement: "ModernLam modules, target users, monthly operating principle, and prototype boundary.",
      prototypeCoverage: "Modules, users, periods, dashboard entry points, and browser-storage scope are visible.",
      status: "Covered",
      followUp: "Keep wording aligned when the production stack is selected.",
    },
    {
      source: "spec/02, accounting/ui/02",
      area: "Navigation and layout",
      requirement: "Top bar, side menu, period selector, common actions, statuses, tables, forms, and print behavior.",
      prototypeCoverage: "Side menu, period selectors, common save/cancel actions, statuses, tables, forms, and print CSS exist.",
      status: "Partially Covered",
      followUp: "Add current user/logout to the top bar and normalize action bars across all screens.",
    },
    {
      source: "accounting/ui/02",
      area: "Current user and logout",
      requirement: "Top bar must show the current user and logout action.",
      prototypeCoverage: "Current user display name is managed in Prototype Settings, rendered in the top bar, used by audit logs, and printed in reports; logout is not implemented.",
      status: "Partially Covered",
      followUp: "Add a browser-only logout/reset-session action when session behavior is needed.",
    },
    {
      source: "accounting/ui/02",
      area: "Filter bars",
      requirement: "Screens should expose month/year/status/search/category/supplier/employee filters where relevant.",
      prototypeCoverage: "The global period selector exists; screen-specific search and status/category filters are not implemented.",
      status: "Missing",
      followUp: "Add per-screen filter state and client-side row filtering for suppliers, HR, reports, and financial tables.",
    },
    {
      source: "spec/03, accounting/ui/01",
      area: "Dashboard",
      requirement: "Period status, summary cards, alerts, latest update, and navigation shortcuts.",
      prototypeCoverage: "Summary cards, period status, latest update, alerts, and clickable dashboard metrics are implemented.",
      status: "Covered",
      followUp: "No immediate prototype gap.",
    },
    {
      source: "spec/04.1, accounting/ui/01",
      area: "Cash Closing",
      requirement: "Cash expenses, differences, difference statement, validations, and tabbed organization.",
      prototypeCoverage: "Expenses, differences, calculated net/difference, remarks, and difference statement are present as sections.",
      status: "Partially Covered",
      followUp: "Convert the screen to documented tabs and add user/cash-desk placeholders if SOFTLAM source is confirmed.",
    },
    {
      source: "spec/04.2, accounting-technical/02",
      area: "Cash and Safe",
      requirement: "Cash movements, additional entries, safe exits, profitability movements, and safe summary calculations.",
      prototypeCoverage: "All listed operation types and total/min/max/average summary rows are represented in browser data.",
      status: "Covered",
      followUp: "No immediate prototype gap.",
    },
    {
      source: "spec/04.3, accounting-technical/02",
      area: "Monthly Balance",
      requirement: "Revenue, expenses, investments, withdrawals, profitability, and net profitability.",
      prototypeCoverage: "Monthly totals, withdrawals, investment totals, profitability, and net profitability are calculated from source data.",
      status: "Covered",
      followUp: "LAM Revenue remains tracked as an open rule, not finalized.",
    },
    {
      source: "spec/04.4, accounting/ui/01",
      area: "Suppliers",
      requirement: "Supplier list, journal, payments, remaining balance, statuses, categories, and details.",
      prototypeCoverage: "Supplier master data, transactions, partial payments, remaining balances, payment status, and journal are implemented.",
      status: "Partially Covered",
      followUp: "Add supplier filters and keep invoices/attachments/multi-category behavior as tracked decisions.",
    },
    {
      source: "spec/04.5, accounting/general/02",
      area: "Subcontractors and Conventions",
      requirement: "Partner tracking, payment, remaining balance, status, and statement support.",
      prototypeCoverage: "Partners are stored with type, payment, remaining balance, status, and report coverage.",
      status: "Covered",
      followUp: "No immediate prototype gap.",
    },
    {
      source: "spec/04.6, accounting-technical/02",
      area: "Attendance",
      requirement: "Daily attendance grid, day codes, guard codes, considered days, and monthly totals.",
      prototypeCoverage: "Attendance entry, day/guard codes, considered flag, and monthly employee summary are implemented.",
      status: "Covered",
      followUp: "No immediate prototype gap.",
    },
    {
      source: "spec/04.7, accounting-technical/02",
      area: "Salaries",
      requirement: "Salary report columns, calculation controls, validation, payment status, and payroll workflow.",
      prototypeCoverage: "Salary columns, final salary calculation, and statuses exist, but validation/payment are not separate workflow actions.",
      status: "Partially Covered",
      followUp: "Add explicit validate/pay buttons after final salary rules are confirmed.",
    },
    {
      source: "spec/05, accounting/general/03",
      area: "Reports and statements",
      requirement: "Supplier, subcontractor, vehicle, cheque, encashment, financial, HR, and payroll reports with filters.",
      prototypeCoverage: "All major report datasets render with preview, totals, official trace, print, CSV export, generation date, and user.",
      status: "Partially Covered",
      followUp: "Add report-specific filters/search and decide whether browser PDF generation is required or print-to-PDF is enough.",
    },
    {
      source: "spec/06, accounting/ui/01",
      area: "HR interfaces",
      requirement: "Employee list, employee file tabs, identity, contract, leave, attendance, salary, documents, and history.",
      prototypeCoverage: "Employee list, function/status/contract/search filters, tabs, identity, contracts, leave, attendance, read-only salary history, documents, alerts, and history are implemented.",
      status: "Covered",
      followUp: "No immediate prototype gap.",
    },
    {
      source: "accounting/ui/02",
      area: "Interface states",
      requirement: "Loading, empty, read-only, error, and saved states.",
      prototypeCoverage: "Empty states, read-only closed periods, validation alerts, and saved toast exist; loading state is absent.",
      status: "Missing",
      followUp: "Add a reusable loading state/skeleton for future async screens.",
    },
    {
      source: "spec/07, accounting/general/02",
      area: "Functional workflows",
      requirement: "New month, daily cash, suppliers, attendance/salaries, monthly closing, and closed-month modification.",
      prototypeCoverage: "New period creation, daily entry, supplier payments, salary generation, closing checklist, and read-only closed periods exist.",
      status: "Partially Covered",
      followUp: "Add the exceptional closed-month modification request and approval workflow.",
    },
    {
      source: "spec/07.6, spec/10",
      area: "Closed month modification",
      requirement: "Exceptional modification requires admin authorization, mandatory reason, audit trace, and recalculation.",
      prototypeCoverage: "Closed periods are protected and period status changes are audited, but no request/approval/reason workflow exists.",
      status: "Missing",
      followUp: "Create a local modification request queue with reason, approver, target record, and recalculation trace.",
    },
    {
      source: "spec/08, accounting-technical/01",
      area: "Data model",
      requirement: "Browser model should mirror users, periods, financial rows, payments, HR rows, reports, attachments, and audit logs.",
      prototypeCoverage: "Core financial, supplier, partner, HR, report export, and audit collections exist; attachments, cheques, encashments, and vehicle expenses are generated or implied rather than dedicated collections.",
      status: "Partially Covered",
      followUp: "Add dedicated browser collections for attachments, vehicle expenses, cheques, and encashments or document their mapping.",
    },
    {
      source: "spec/09, accounting-technical/02",
      area: "Business rules",
      requirement: "Cash, supplier, partner, safe net, revenue, profitability, salary, leave, and closing calculations.",
      prototypeCoverage: "Stable calculations are represented; LAM Revenue, Cash CV/Cash C role, TPE treatment, Additional Entries treatment, salary formula, guard prices, absence unit, leave rules, cheque running balance, SOFTLAM source, and close/reopen role remain explicit tracked decisions.",
      status: "Tracked",
      followUp: "Do not finalize unresolved formulas until the open questions are answered.",
    },
    {
      source: "spec/10",
      area: "Permissions and audit",
      requirement: "Roles, permission matrix, audit log, protected closed month, sensitive operations, and reasons.",
      prototypeCoverage: "Users, active/inactive status, documented permission matrix, categorized audit log, salary validation trace, closing/reopening trace, settings trace, and closed-period protection exist; permissions are not enforced per active user.",
      status: "Partially Covered",
      followUp: "Apply role-based UI disabling/hiding and require reasons for sensitive changes.",
    },
    {
      source: "spec/11, accounting/general/03",
      area: "Reporting and printing",
      requirement: "Draft/official reports, official PDF, Excel export, preview, file naming, and export history.",
      prototypeCoverage: "Preview, print, official trace, CSV export, history, totals, stamp/signature area, and lab identity exist.",
      status: "Partially Covered",
      followUp: "Add explicit PDF/Excel file generation or document the accepted browser-only substitute.",
    },
    {
      source: "spec/12",
      area: "Implementation roadmap",
      requirement: "Phases 0-8 and proposed MVP remain a planning guide, not business behavior.",
      prototypeCoverage: "Prototype modules broadly follow the roadmap without locking the final production stack.",
      status: "Tracked",
      followUp: "Use this as planning input for expansion commits, not as a final implemented rule.",
    },
    {
      source: "spec/13, docs/ar/spec/13",
      area: "Open questions",
      requirement: "Unresolved accounting, SOFTLAM, supplier, salary, leave, report, permission, and technical decisions.",
      prototypeCoverage: "Open decisions are listed one-by-one in Administration with Tracked status and prototype treatment, and assumption notices appear where unresolved rules are represented.",
      status: "Tracked",
      followUp: "Resolve with the user before changing LAM Revenue, salaries, leave, or permission rules.",
    },
  ];
}

function coverageFollowUpTasks() {
  return [
    ["Medium", "Logout/session control", "Add a browser-only logout/reset-session action if session behavior becomes part of the prototype.", "Planned"],
    ["High", "Filter bars", "Implement screen-specific search/status/category/supplier/employee filters with client-side row filtering.", "Missing"],
    ["High", "Closed month modification", "Create exceptional modification requests with mandatory reason, admin approval, audit trace, and recalculation marker.", "Missing"],
    ["Medium", "Interface states", "Add reusable loading state/skeleton so future async screens match the documented UI states.", "Missing"],
    ["Medium", "Navigation and layout", "Normalize action bars and add missing top-bar user controls across the shell.", "Planned"],
    ["Medium", "Cash Closing", "Refactor Cash Closing sections into documented tabs and add SOFTLAM trace placeholders only after source rules are confirmed.", "Planned"],
    ["Medium", "Reports and statements", "Add report-level filters/search and decide between generated PDF files or documented print-to-PDF behavior.", "Planned"],
    ["Medium", "Permissions and audit", "Enforce the permission matrix in the UI and require reasons for sensitive actions.", "Planned"],
    ["Low", "Data model", "Add dedicated local collections for attachments, vehicle expenses, cheques, and encashments or document their mapping.", "Planned"],
    ["Decision", "Business rules", "Keep LAM Revenue, Cash CV/Cash C role, TPE treatment, Additional Entries treatment, SOFTLAM source, official salary formula, guard prices, absence unit, leave rules, cheque running balance, and close/reopen roles tracked until confirmed.", "Tracked"],
  ].map((row) => ({ priority: row[0], area: row[1], task: row[2], status: row[3] }));
}

function openQuestions() {
  return [
    ["Accounting", "LAM Revenue formula", "Displayed only as a prototype formula in Cash & Safe and Monthly Balance."],
    ["Accounting", "Cash CV/Cash C role", "Values are shown as separate source columns; their final accounting meaning is not fixed."],
    ["Accounting", "TPE treatment", "TPE is reported as a source value; final revenue/cash treatment remains tracked."],
    ["Accounting", "Additional Entries treatment", "Paid entries are included as a prototype assumption only."],
    ["SOFTLAM", "SOFTLAM import/manual source", "Virtual Amount is manually entered in prototype; import/source rule is not final."],
    ["Salaries", "Official salary formula", "Salary screen labels the calculation as a prototype formula."],
    ["Salaries", "Guard prices", "Guard amounts are manual inputs; official prices are not fixed."],
    ["Salaries", "Absence unit", "Absence is a manual deduction amount; official unit is not fixed."],
    ["Leave", "Leave day 15 rule", "Not automated; leave balances are manual prototype rows."],
    ["Leave", "Leave carry-over", "Not automated; yearly balance behavior remains tracked."],
    ["Reports", "Cheque running balance", "Cheque report shows a tracked placeholder, not a final balance rule."],
    ["Permissions", "Role authorized to close/reopen", "Prototype shows controls but does not finalize the authorized role."],
    ["Accounting", "Partner recognition timing", "Partner payments and balances are shown; final recognition timing remains tracked."],
    ["Suppliers", "Supplier invoices and attachments", "Supplier rows accept references/observations; final attachment requirement remains tracked."],
  ].map((row) => ({ category: row[0], question: row[1], prototypeTreatment: row[2], status: "Tracked" }));
}
