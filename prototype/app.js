(() => {
  "use strict";

  const STORE_KEY = "modernlam.prototype.v1";
  const VIEW_KEY = "modernlam.prototype.activeView";
  const REPORT_KEY = "modernlam.prototype.reportType";
  const app = document.getElementById("app");

  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  const navItems = [
    ["dashboard", "DB", "Dashboard"],
    ["cashClosing", "CC", "Cash Closing"],
    ["cashSafe", "CS", "Cash & Safe"],
    ["balance", "MB", "Monthly Balance"],
    ["suppliers", "SP", "Suppliers"],
    ["partners", "PC", "Partners"],
    ["attendance", "AT", "Attendance"],
    ["salaries", "SL", "Salaries"],
    ["reports", "RP", "Reports"],
    ["hr", "HR", "HR"],
    ["admin", "AD", "Administration"],
  ];

  const supplierCategories = [
    "Reagents & Consumables",
    "Subcontracting",
    "Taxes",
    "IT & Office",
    "Service Vehicle",
    "Rent",
    "Lab Energy",
    "Internal Expenses",
    "Salaries",
    "Subcontractor Transport",
    "Other Expenses",
    "Investment",
  ];

  const paymentModes = ["Cash", "Cheque", "Transfer", "TPE", "Other"];
  const partnerTypes = ["Subcontractor", "Convention"];
  const paymentStatuses = ["Paid", "Partial", "Unpaid"];
  const salaryStatuses = ["Draft", "Validated", "Paid"];
  const periodStatuses = ["Open", "Under review", "Closed"];
  const dayCodes = ["P", "ABS", "G", "GV-J", "GV-N", "C", "C.M", "REC", "P+"];
  const roles = ["Admin", "Direction", "Accountant", "Cash Desk", "HR", "Viewer"];
  const periodCollections = new Set([
    "cashExpenses",
    "cashClosures",
    "cashMovements",
    "additionalEntries",
    "safeExits",
    "profitabilityMovements",
    "supplierTransactions",
    "payments",
    "partners",
    "attendance",
    "salaryReports",
    "vehicleExpenses",
    "cheques",
    "encashments",
  ]);

  let state = normalizeState(loadState());
  let activeView = localStorage.getItem(VIEW_KEY) || "dashboard";
  let activeReport = localStorage.getItem(REPORT_KEY) || "encashment";
  let toast = "";
  const viewRenderers = {};
  let reportDatasetProvider = null;

  function loadState() {
    try {
      const raw = localStorage.getItem(STORE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (error) {
      console.warn("Could not load prototype state", error);
    }
    return seedState();
  }

  function seedState() {
    const now = new Date();
    const month = now.getMonth() + 1;
    const year = now.getFullYear();
    const key = makePeriodKey(month, year);
    const d = (day) => `${year}-${pad(month)}-${pad(day)}`;
    const employees = [
      {
        id: id(),
        fullName: "Nadia Benali",
        function: "Accountant",
        birthDate: "1991-04-12",
        birthPlace: "Oran",
        address: "ModernLam site",
        phone01: "0550000001",
        phone02: "",
        socialSecurityNumber: "CNAS-001",
        anemNumber: "ANEM-001",
        status: "Active",
      },
      {
        id: id(),
        fullName: "Karim Haddad",
        function: "Cash Desk",
        birthDate: "1988-09-22",
        birthPlace: "Tlemcen",
        address: "ModernLam site",
        phone01: "0550000002",
        phone02: "",
        socialSecurityNumber: "CNAS-002",
        anemNumber: "ANEM-002",
        status: "Active",
      },
      {
        id: id(),
        fullName: "Samira Mansouri",
        function: "HR",
        birthDate: "1994-01-18",
        birthPlace: "Sidi Bel Abbes",
        address: "ModernLam site",
        phone01: "0550000003",
        phone02: "",
        socialSecurityNumber: "CNAS-003",
        anemNumber: "ANEM-003",
        status: "Active",
      },
    ];
    const suppliers = [
      {
        id: id(),
        name: "BioPlus Reagents",
        category: "Reagents & Consumables",
        phone: "041000001",
        address: "Oran",
        notes: "Primary reagent supplier",
        isActive: true,
      },
      {
        id: id(),
        name: "OfficeLine",
        category: "IT & Office",
        phone: "041000002",
        address: "Alger",
        notes: "",
        isActive: true,
      },
    ];
    const supplierTransactionId = id();
    return {
      selected: { month, year },
      periods: [
        {
          id: id(),
          month,
          year,
          status: "Open",
          openedAt: now.toISOString(),
          openedBy: "Admin",
          closedAt: "",
          closedBy: "",
          closeNote: "",
        },
      ],
      employees,
      suppliers,
      cashExpenses: [
        {
          id: id(),
          periodKey: key,
          date: d(2),
          designation: "Small cash supplies",
          amount: 4200,
          remark: "Validated by accounting",
          attachmentRef: "receipt-001",
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      cashClosures: [
        {
          id: id(),
          periodKey: key,
          date: d(2),
          user: "Karim Haddad",
          realAmount: 128500,
          virtualAmount: 128500,
          difference: 0,
          remark: "",
          status: "Validated",
          createdAt: now.toISOString(),
        },
        {
          id: id(),
          periodKey: key,
          date: d(3),
          user: "Karim Haddad",
          realAmount: 141200,
          virtualAmount: 140900,
          difference: 300,
          remark: "Late manual receipt",
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      cashMovements: [
        {
          id: id(),
          periodKey: key,
          date: d(2),
          cashCv: 78000,
          cashC: 50500,
          tpe: 18700,
          expenses: 4200,
          reimbursement: 0,
          convention: 12500,
          subcontractors: 8300,
          total: 173200,
          remark: "",
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      additionalEntries: [
        {
          id: id(),
          periodKey: key,
          date: d(4),
          amount: 18000,
          detail: "Manual correction entry",
          paymentStatus: "Paid",
          remark: "",
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      safeExits: [
        {
          id: id(),
          periodKey: key,
          date: d(5),
          designation: "Rent payment",
          amount: 45000,
          category: "Rent",
          attachmentRef: "rent-note",
          remark: "",
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      profitabilityMovements: [
        {
          id: id(),
          periodKey: key,
          date: d(6),
          amount: 15000,
          detail: "Previous month carry-over",
          movementType: "Entry",
          sourcePeriod: "",
          destinationPeriod: key,
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      supplierTransactions: [
        {
          id: supplierTransactionId,
          periodKey: key,
          supplierId: suppliers[0].id,
          category: "Reagents & Consumables",
          date: d(6),
          orderTotal: 96000,
          paidAmount: 40000,
          remainingAmount: 56000,
          paymentMode: "Cheque",
          reference: "CH-102",
          status: "Partial",
          observation: "Partial payment",
          createdAt: now.toISOString(),
        },
      ],
      payments: [
        {
          id: id(),
          periodKey: key,
          targetType: "supplier",
          targetId: supplierTransactionId,
          date: d(6),
          amount: 40000,
          paymentMode: "Cheque",
          reference: "CH-102",
          note: "",
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      partners: [
        {
          id: id(),
          periodKey: key,
          type: "Subcontractor",
          name: "External Lab A",
          amount: 32000,
          payment: 32000,
          receptionDate: d(7),
          paymentMode: "Transfer",
          remainingBalance: 0,
          status: "Paid",
          remarks: "",
          createdAt: now.toISOString(),
        },
        {
          id: id(),
          periodKey: key,
          type: "Convention",
          name: "Company Convention B",
          amount: 54000,
          payment: 25000,
          receptionDate: d(8),
          paymentMode: "Cheque",
          remainingBalance: 29000,
          status: "Partial",
          remarks: "",
          createdAt: now.toISOString(),
        },
      ],
      attendance: [
        {
          id: id(),
          periodKey: key,
          employeeId: employees[0].id,
          date: d(1),
          dayCode: "P",
          note: "",
          status: "Validated",
          createdAt: now.toISOString(),
        },
        {
          id: id(),
          periodKey: key,
          employeeId: employees[1].id,
          date: d(1),
          dayCode: "G",
          note: "Night guard",
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      salaryReports: [
        {
          id: id(),
          periodKey: key,
          employeeId: employees[0].id,
          baseNetSalary: 70000,
          overtimePresence: 0,
          lamTravel: 4000,
          nightGuard: 0,
          fridayDayGuard: 0,
          fridayNightGuard: 0,
          absence: 0,
          bonus: 5000,
          leave: 0,
          penalties: 0,
          advances: 0,
          finalSalary: 79000,
          status: "Draft",
          remark: "",
          createdAt: now.toISOString(),
        },
      ],
      contracts: employees.map((employee) => ({
        id: id(),
        employeeId: employee.id,
        hireDate: "2023-01-01",
        cnasRegistrationDate: "2023-01-10",
        contractType: "CDI",
        startsAt: "2023-01-01",
        endsAt: "",
        resignationDate: "",
        status: "Active",
        remark: "",
        createdAt: now.toISOString(),
      })),
      leaves: employees.map((employee) => ({
        id: id(),
        employeeId: employee.id,
        year,
        acquiredDays: 30,
        usedDays: 4,
        remainingDays: 26,
        remark: "",
        createdAt: now.toISOString(),
      })),
      vehicleExpenses: [
        {
          id: id(),
          periodKey: key,
          date: d(9),
          amount: 6200,
          details: "Fuel",
          mileage: 75000,
          gplExtraKm: 0,
          essenceExtraKm: 120,
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      cheques: [
        {
          id: id(),
          periodKey: key,
          date: d(10),
          beneficiary: "BioPlus Reagents",
          chequeNumber: "CH-102",
          amount: 40000,
          entries: 0,
          exits: 40000,
          designation: "Supplier payment",
          month: monthNames[month - 1],
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      encashments: [
        {
          id: id(),
          periodKey: key,
          date: d(2),
          designation: "DIVERS CLIENTS",
          observations: "",
          amount: 128500,
          status: "Validated",
          createdAt: now.toISOString(),
        },
      ],
      users: [
        {
          id: id(),
          username: "admin",
          fullName: "Administrator",
          role: "Admin",
          isActive: true,
          lastLoginAt: now.toISOString(),
        },
      ],
      auditLogs: [
        {
          id: id(),
          user: "Admin",
          action: "Seed prototype data",
          entityType: "prototype",
          entityId: "initial",
          oldValues: "",
          newValues: "Initial browser data",
          reason: "Prototype setup",
          createdAt: now.toISOString(),
        },
      ],
      reportExports: [],
    };
  }

  function normalizeState(input) {
    const base = seedState();
    const output = { ...base, ...input };
    Object.keys(base).forEach((key) => {
      if (Array.isArray(base[key]) && !Array.isArray(output[key])) output[key] = [];
    });
    if (!output.selected) {
      const now = new Date();
      output.selected = { month: now.getMonth() + 1, year: now.getFullYear() };
    }
    ensurePeriod(output.selected.month, output.selected.year, output);
    return output;
  }

  function saveState() {
    localStorage.setItem(STORE_KEY, JSON.stringify(state));
  }

  function id() {
    return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  }

  function pad(value) {
    return String(value).padStart(2, "0");
  }

  function makePeriodKey(month, year) {
    return `${year}-${pad(month)}`;
  }

  function currentPeriodKey() {
    return makePeriodKey(state.selected.month, state.selected.year);
  }

  function ensurePeriod(month, year, targetState = state) {
    let period = targetState.periods.find((item) => item.month === month && item.year === year);
    if (!period) {
      period = {
        id: id(),
        month,
        year,
        status: "Open",
        openedAt: new Date().toISOString(),
        openedBy: "Admin",
        closedAt: "",
        closedBy: "",
        closeNote: "",
      };
      targetState.periods.push(period);
    }
    return period;
  }

  function getPeriod() {
    return ensurePeriod(state.selected.month, state.selected.year);
  }

  function isClosedPeriod() {
    return getPeriod().status === "Closed";
  }

  function formatDate(value) {
    if (!value) return "";
    return value;
  }

  function defaultDate(day = 1) {
    return `${state.selected.year}-${pad(state.selected.month)}-${pad(day)}`;
  }

  function daysInMonth() {
    return new Date(state.selected.year, state.selected.month, 0).getDate();
  }

  function number(value) {
    const parsed = Number(String(value || "0").replace(",", "."));
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function sum(rows, key) {
    return rows.reduce((total, row) => total + number(row[key]), 0);
  }

  function money(value) {
    return `${number(value).toLocaleString("fr-DZ", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    })} DA`;
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

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

  function showToast(message) {
    toast = message;
    window.setTimeout(() => {
      toast = "";
      render();
    }, 2200);
  }

  function statusClass(status) {
    return `status-${String(status || "").toLowerCase().replace(/\s+/g, "-")}`;
  }

  function statusPill(status) {
    return `<span class="status-pill ${statusClass(status)}">${escapeHtml(status || "")}</span>`;
  }

  function formData(form) {
    return Object.fromEntries(new FormData(form).entries());
  }

  function optionList(values, selected = "") {
    return values
      .map((item) => {
        const value = Array.isArray(item) ? item[0] : item;
        const label = Array.isArray(item) ? item[1] : item;
        return `<option value="${escapeHtml(value)}"${String(value) === String(selected) ? " selected" : ""}>${escapeHtml(label)}</option>`;
      })
      .join("");
  }

  function renderField(field, disabled = false) {
    const classes = ["field"];
    if (field.full) classes.push("full");
    if (field.span === 2) classes.push("span-2");
    const required = field.required ? " required" : "";
    const disabledAttr = disabled || field.disabled ? " disabled" : "";
    const value = field.value ?? "";
    const label = `<label for="${escapeHtml(field.name)}">${escapeHtml(field.label)}</label>`;
    if (field.type === "select") {
      return `<div class="${classes.join(" ")}">${label}<select id="${escapeHtml(field.name)}" name="${escapeHtml(field.name)}"${required}${disabledAttr}>${optionList(field.options || [], value)}</select></div>`;
    }
    if (field.type === "textarea") {
      return `<div class="${classes.join(" ")}">${label}<textarea id="${escapeHtml(field.name)}" name="${escapeHtml(field.name)}"${required}${disabledAttr}>${escapeHtml(value)}</textarea></div>`;
    }
    const type = field.type || "text";
    const step = field.step ? ` step="${escapeHtml(field.step)}"` : "";
    const min = field.min !== undefined ? ` min="${escapeHtml(field.min)}"` : "";
    return `<div class="${classes.join(" ")}">${label}<input id="${escapeHtml(field.name)}" name="${escapeHtml(field.name)}" type="${escapeHtml(type)}" value="${escapeHtml(value)}"${required}${disabledAttr}${step}${min}></div>`;
  }

  function renderForm(title, formId, fields, buttonLabel = "Save", options = {}) {
    const disabled = Boolean(options.periodScoped && isClosedPeriod());
    return `
      <div class="form-card">
        <h2>${escapeHtml(title)}</h2>
        <form data-form="${escapeHtml(formId)}">
          <div class="form-grid">
            ${fields.map((field) => renderField(field, disabled)).join("")}
          </div>
          <div class="action-row">
            <button class="text-btn primary" type="submit" title="${escapeHtml(buttonLabel)}"${disabled ? " disabled" : ""}>+ ${escapeHtml(buttonLabel)}</button>
          </div>
        </form>
      </div>
    `;
  }

  function renderTable(columns, rows, options = {}) {
    if (!rows.length) return `<div class="empty-state">${escapeHtml(options.empty || "No records for this view.")}</div>`;
    const actionHead = options.collection ? "<th>Action</th>" : "";
    const body = rows
      .map((row) => {
        const cells = columns
          .map((column) => {
            const raw = typeof column.value === "function" ? column.value(row) : row[column.key];
            const value = column.html ? raw : column.format ? column.format(raw, row) : escapeHtml(raw);
            const css = column.amount ? " class=\"amount\"" : "";
            return `<td${css}>${value}</td>`;
          })
          .join("");
        const actionCell = options.collection
          ? `<td><button class="icon-btn danger" type="button" title="Cancel" data-cancel="${escapeHtml(options.collection)}" data-id="${escapeHtml(row.id)}"${periodCollections.has(options.collection) && isClosedPeriod() ? " disabled" : ""}>X</button></td>`
          : "";
        return `<tr>${cells}${actionCell}</tr>`;
      })
      .join("");
    return `
      <div class="table-wrap">
        <table>
          <thead><tr>${columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("")}${actionHead}</tr></thead>
          <tbody>${body}</tbody>
        </table>
      </div>
    `;
  }

  function renderSection(title, body, actions = "") {
    return `
      <section class="section">
        <div class="section-head">
          <h2>${escapeHtml(title)}</h2>
          <div class="section-actions">${actions}</div>
        </div>
        <div class="section-body">${body}</div>
      </section>
    `;
  }

  function renderHeader(title, description, actions = "") {
    return `
      <div class="view-header">
        <div>
          <h1>${escapeHtml(title)}</h1>
          <p>${escapeHtml(description)}</p>
        </div>
        <div class="section-actions">${actions}</div>
      </div>
    `;
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

  function renderMetrics(items) {
    return `<div class="grid four">${items.map((item) => `<div class="metric"><span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.value)}</strong></div>`).join("")}</div>`;
  }

  function registerView(name, renderer) {
    viewRenderers[name] = renderer;
  }

  function setReportDatasetProvider(provider) {
    reportDatasetProvider = provider;
  }

  function getActiveReport() {
    return activeReport;
  }

  function getReportDataset() {
    if (reportDatasetProvider) return reportDatasetProvider();
    return { title: "Report", columns: [], rows: [], total: "" };
  }

  function renderTopbar() {
    const period = getPeriod();
    const years = Array.from({ length: 7 }, (_, index) => state.selected.year - 3 + index);
    return `
      <header class="topbar">
        <div class="brand">
          <img src="prototype/assets/modernlam-logo.svg" alt="ModernLam logo">
          <div class="brand-title">
            <strong>ModernLam Comptabilite</strong>
            <span>Browser Prototype</span>
          </div>
        </div>
        <div class="period-tools">
          <label>Month
            <select data-period-month>${monthNames.map((name, index) => `<option value="${index + 1}"${index + 1 === state.selected.month ? " selected" : ""}>${escapeHtml(name)}</option>`).join("")}</select>
          </label>
          <label>Year
            <select data-period-year>${years.map((year) => `<option value="${year}"${year === state.selected.year ? " selected" : ""}>${year}</option>`).join("")}</select>
          </label>
          ${statusPill(period.status)}
        </div>
        <div class="top-actions">
          ${periodStatuses.map((status) => `<button class="icon-btn" type="button" title="Set ${escapeHtml(status)}" data-period-status="${escapeHtml(status)}">${escapeHtml(status[0])}</button>`).join("")}
        </div>
      </header>
    `;
  }

  function renderSidebar() {
    return `
      <aside class="sidebar">
        <nav class="nav">
          ${navItems
            .map(([key, icon, label]) => `<button type="button" class="${activeView === key ? "active" : ""}" data-view="${escapeHtml(key)}"><span class="nav-icon">${escapeHtml(icon)}</span><span>${escapeHtml(label)}</span></button>`)
            .join("")}
        </nav>
      </aside>
    `;
  }

  function renderContent() {
    const view = viewRenderers[activeView] ? activeView : "dashboard";
    const renderer = viewRenderers[view];
    const body = renderer ? renderer() : `<div class="empty-state">The selected interface is not loaded.</div>`;
    return `<main class="content">${body}</main>`;
  }

  function render() {
    ensurePeriod(state.selected.month, state.selected.year);
    app.innerHTML = `
      <div class="app-shell">
        ${renderTopbar()}
        ${renderSidebar()}
        ${renderContent()}
      </div>
      ${toast ? `<div class="toast">${escapeHtml(toast)}</div>` : ""}
    `;
  }

  function setPeriod(month, year) {
    state.selected = { month: number(month), year: number(year) };
    ensurePeriod(state.selected.month, state.selected.year);
    saveState();
    render();
  }

  function setPeriodStatus(status) {
    const period = getPeriod();
    const before = { ...period };
    period.status = status;
    if (status === "Closed") {
      period.closedAt = new Date().toISOString();
      period.closedBy = "Admin";
    }
    audit("Set period status", "accounting_periods", period.id, period, before);
    saveState();
    showToast(`Period status set to ${status}.`);
    render();
  }

  function updateSupplierStatus(row) {
    row.remainingAmount = number(row.orderTotal) - number(row.paidAmount);
    if (number(row.remainingAmount) <= 0) row.status = "Paid";
    else if (number(row.paidAmount) > 0) row.status = "Partial";
    else row.status = "Unpaid";
  }

  function updatePartnerStatus(row) {
    row.remainingBalance = number(row.amount) - number(row.payment);
    if (number(row.remainingBalance) <= 0) row.status = "Paid";
    else if (number(row.payment) > 0) row.status = "Partial";
    else row.status = "Unpaid";
  }

  function salaryTotal(row) {
    return (
      number(row.baseNetSalary) +
      number(row.overtimePresence) +
      number(row.lamTravel) +
      number(row.nightGuard) +
      number(row.fridayDayGuard) +
      number(row.fridayNightGuard) +
      number(row.bonus) -
      number(row.absence) -
      number(row.penalties) -
      number(row.advances)
    );
  }

  function requireOpenPeriod(formId) {
    const periodScopedForms = new Set([
      "cashExpense",
      "cashClosure",
      "cashMovement",
      "additionalEntry",
      "safeExit",
      "profitabilityMovement",
      "supplierTransaction",
      "supplierPayment",
      "partner",
      "partnerPayment",
      "attendance",
      "salary",
      "vehicle",
      "cheque",
      "encashment",
    ]);
    if (periodScopedForms.has(formId) && isClosedPeriod()) {
      showToast("Closed period is read-only.");
      return false;
    }
    return true;
  }

  function handleSubmit(event) {
    const form = event.target.closest("form[data-form]");
    if (!form) return;
    event.preventDefault();
    const formId = form.dataset.form;
    if (!requireOpenPeriod(formId)) return;
    const data = formData(form);

    if (formId === "cashExpense") {
      addRecord("cashExpenses", {
        date: data.date,
        designation: data.designation,
        amount: number(data.amount),
        remark: data.remark,
        attachmentRef: data.attachmentRef,
        status: "Validated",
      });
    }

    if (formId === "cashClosure") {
      const difference = number(data.realAmount) - number(data.virtualAmount);
      if (difference !== 0 && !data.remark.trim()) {
        showToast("Remark is required when a difference exists.");
        return;
      }
      addRecord("cashClosures", {
        date: data.date,
        user: data.user,
        realAmount: number(data.realAmount),
        virtualAmount: number(data.virtualAmount),
        difference,
        remark: data.remark,
        status: "Validated",
      });
    }

    if (formId === "cashMovement") {
      const record = {
        date: data.date,
        cashCv: number(data.cashCv),
        cashC: number(data.cashC),
        tpe: number(data.tpe),
        expenses: number(data.expenses),
        reimbursement: number(data.reimbursement),
        convention: number(data.convention),
        subcontractors: number(data.subcontractors),
        remark: data.remark,
        status: "Validated",
      };
      record.total = record.cashCv + record.cashC + record.tpe + record.expenses + record.reimbursement + record.convention + record.subcontractors;
      addRecord("cashMovements", record);
    }

    if (formId === "additionalEntry") {
      addRecord("additionalEntries", {
        date: data.date,
        amount: number(data.amount),
        detail: data.detail,
        paymentStatus: data.paymentStatus,
        remark: data.remark,
        status: "Validated",
      });
    }

    if (formId === "safeExit") {
      addRecord("safeExits", {
        date: data.date,
        designation: data.designation,
        amount: number(data.amount),
        category: data.category,
        attachmentRef: data.attachmentRef,
        remark: data.remark,
        status: "Validated",
      });
    }

    if (formId === "profitabilityMovement") {
      addRecord("profitabilityMovements", {
        date: data.date,
        amount: number(data.amount),
        detail: data.detail,
        movementType: data.movementType,
        sourcePeriod: data.sourcePeriod,
        destinationPeriod: data.destinationPeriod,
        status: "Validated",
      });
    }

    if (formId === "supplier") {
      addRecord("suppliers", {
        name: data.name,
        category: data.category,
        phone: data.phone,
        address: data.address,
        notes: data.notes,
        isActive: true,
      });
    }

    if (formId === "supplierTransaction") {
      const paidAmount = number(data.paidAmount);
      if (paidAmount > 0 && !data.paymentMode) {
        showToast("Payment mode is required when paid amount exists.");
        return;
      }
      const record = {
        supplierId: data.supplierId,
        category: data.category,
        date: data.date,
        orderTotal: number(data.orderTotal),
        paidAmount,
        remainingAmount: 0,
        paymentMode: data.paymentMode,
        reference: data.reference,
        observation: data.observation,
        status: "Unpaid",
      };
      updateSupplierStatus(record);
      const saved = addRecord("supplierTransactions", record, "Create supplier transaction");
      if (paidAmount > 0) {
        const payment = {
          id: id(),
          periodKey: currentPeriodKey(),
          targetType: "supplier",
          targetId: saved.id,
          date: data.date,
          amount: paidAmount,
          paymentMode: data.paymentMode,
          reference: data.reference,
          note: "Initial payment",
          status: "Validated",
          createdAt: new Date().toISOString(),
        };
        state.payments.push(payment);
        audit("Create initial supplier payment", "payments", payment.id, payment);
        saveState();
        render();
      }
    }

    if (formId === "supplierPayment") {
      const transaction = state.supplierTransactions.find((row) => row.id === data.targetId);
      if (!transaction) {
        showToast("Select an invoice first.");
        return;
      }
      if (number(data.amount) > number(transaction.remainingAmount)) {
        showToast("Payment cannot exceed remaining balance.");
        return;
      }
      const before = { ...transaction };
      transaction.paidAmount = number(transaction.paidAmount) + number(data.amount);
      updateSupplierStatus(transaction);
      audit("Update supplier payment", "supplierTransactions", transaction.id, transaction, before);
      addRecord("payments", {
        targetType: "supplier",
        targetId: data.targetId,
        date: data.date,
        amount: number(data.amount),
        paymentMode: data.paymentMode,
        reference: data.reference,
        note: data.note,
        status: "Validated",
      });
    }

    if (formId === "partner") {
      const payment = number(data.payment);
      if (payment > 0 && !data.paymentMode) {
        showToast("Payment mode is required when payment exists.");
        return;
      }
      const record = {
        type: data.type,
        name: data.name,
        amount: number(data.amount),
        payment,
        receptionDate: data.receptionDate,
        paymentMode: data.paymentMode,
        remainingBalance: 0,
        status: "Unpaid",
        remarks: data.remarks,
      };
      updatePartnerStatus(record);
      const saved = addRecord("partners", record);
      if (payment > 0) {
        const savedPayment = {
          id: id(),
          periodKey: currentPeriodKey(),
          targetType: "partner",
          targetId: saved.id,
          date: data.receptionDate,
          amount: payment,
          paymentMode: data.paymentMode,
          reference: "",
          note: "Initial payment",
          status: "Validated",
          createdAt: new Date().toISOString(),
        };
        state.payments.push(savedPayment);
        audit("Create initial partner payment", "payments", savedPayment.id, savedPayment);
        saveState();
        render();
      }
    }

    if (formId === "partnerPayment") {
      const partner = state.partners.find((row) => row.id === data.targetId);
      if (!partner) {
        showToast("Select a partner first.");
        return;
      }
      if (number(data.amount) > number(partner.remainingBalance)) {
        showToast("Payment cannot exceed remaining balance.");
        return;
      }
      const before = { ...partner };
      partner.payment = number(partner.payment) + number(data.amount);
      partner.paymentMode = data.paymentMode;
      updatePartnerStatus(partner);
      audit("Update partner payment", "partners", partner.id, partner, before);
      addRecord("payments", {
        targetType: "partner",
        targetId: data.targetId,
        date: data.date,
        amount: number(data.amount),
        paymentMode: data.paymentMode,
        reference: data.reference,
        note: data.note,
        status: "Validated",
      });
    }

    if (formId === "attendance") {
      const existing = state.attendance.find((row) => row.periodKey === currentPeriodKey() && row.employeeId === data.employeeId && row.date === data.date && row.status !== "Cancelled");
      if (existing) {
        existing.status = "Cancelled";
        audit("Replace attendance", "attendance", existing.id, existing);
      }
      addRecord("attendance", {
        employeeId: data.employeeId,
        date: data.date,
        dayCode: data.dayCode,
        note: data.note,
        status: "Validated",
      });
    }

    if (formId === "salary") {
      const record = {
        employeeId: data.employeeId,
        baseNetSalary: number(data.baseNetSalary),
        overtimePresence: number(data.overtimePresence),
        lamTravel: number(data.lamTravel),
        nightGuard: number(data.nightGuard),
        fridayDayGuard: number(data.fridayDayGuard),
        fridayNightGuard: number(data.fridayNightGuard),
        absence: number(data.absence),
        bonus: number(data.bonus),
        leave: number(data.leave),
        penalties: number(data.penalties),
        advances: number(data.advances),
        status: data.status,
        remark: data.remark,
      };
      record.finalSalary = salaryTotal(record);
      addRecord("salaryReports", record);
    }

    if (formId === "vehicle") {
      addRecord("vehicleExpenses", {
        date: data.date,
        amount: number(data.amount),
        details: data.details,
        mileage: number(data.mileage),
        gplExtraKm: number(data.gplExtraKm),
        essenceExtraKm: number(data.essenceExtraKm),
        status: "Validated",
      });
    }

    if (formId === "cheque") {
      addRecord("cheques", {
        date: data.date,
        beneficiary: data.beneficiary,
        chequeNumber: data.chequeNumber,
        amount: number(data.amount),
        entries: number(data.entries),
        exits: number(data.exits),
        designation: data.designation,
        month: monthNames[state.selected.month - 1],
        status: "Validated",
      });
    }

    if (formId === "encashment") {
      addRecord("encashments", {
        date: data.date,
        designation: data.designation,
        observations: data.observations,
        amount: number(data.amount),
        status: "Validated",
      });
    }

    if (formId === "employee") {
      addRecord("employees", {
        fullName: data.fullName,
        function: data.function,
        birthDate: data.birthDate,
        birthPlace: data.birthPlace,
        address: data.address,
        phone01: data.phone01,
        phone02: data.phone02,
        socialSecurityNumber: data.socialSecurityNumber,
        anemNumber: data.anemNumber,
        status: data.status,
      });
    }

    if (formId === "contract") {
      if (data.endsAt && data.startsAt && new Date(data.endsAt) < new Date(data.startsAt)) {
        showToast("Contract end date cannot be before start date.");
        return;
      }
      if (data.status === "Active") {
        state.contracts.forEach((contract) => {
          if (contract.employeeId === data.employeeId && contract.status === "Active") contract.status = "Expired";
        });
      }
      addRecord("contracts", {
        employeeId: data.employeeId,
        hireDate: data.hireDate,
        cnasRegistrationDate: data.cnasRegistrationDate,
        contractType: data.contractType,
        startsAt: data.startsAt,
        endsAt: data.endsAt,
        resignationDate: data.resignationDate,
        status: data.status,
        remark: data.remark,
      });
    }

    if (formId === "leave") {
      const acquiredDays = number(data.acquiredDays);
      const usedDays = number(data.usedDays);
      addRecord("leaves", {
        employeeId: data.employeeId,
        year: number(data.year),
        acquiredDays,
        usedDays,
        remainingDays: acquiredDays - usedDays,
        remark: data.remark,
      });
    }

    if (formId === "user") {
      addRecord("users", {
        username: data.username,
        fullName: data.fullName,
        role: data.role,
        isActive: data.isActive === "true",
        lastLoginAt: "",
      });
    }
  }

  function generateSalaryDrafts() {
    if (isClosedPeriod()) {
      showToast("Closed period is read-only.");
      return;
    }
    let count = 0;
    state.employees
      .filter((employee) => employee.status !== "Inactive")
      .forEach((employee) => {
        const exists = scopedRows("salaryReports").some((row) => row.employeeId === employee.id);
        if (!exists) {
          const record = {
            id: id(),
            periodKey: currentPeriodKey(),
            employeeId: employee.id,
            baseNetSalary: 0,
            overtimePresence: 0,
            lamTravel: 0,
            nightGuard: 0,
            fridayDayGuard: 0,
            fridayNightGuard: 0,
            absence: 0,
            bonus: 0,
            leave: 0,
            penalties: 0,
            advances: 0,
            finalSalary: 0,
            status: "Draft",
            remark: "Generated draft",
            createdAt: new Date().toISOString(),
          };
          state.salaryReports.push(record);
          audit("Generate salary draft", "salaryReports", record.id, record);
          count += 1;
        }
      });
    saveState();
    showToast(`${count} salary drafts generated.`);
    render();
  }

  function exportCurrentReportCsv() {
    const dataset = getReportDataset();
    const rows = dataset.rows;
    const headers = dataset.columns.map((column) => column.label);
    const lines = [headers.join(",")];
    rows.forEach((row, index) => {
      lines.push(
        dataset.columns
          .map((column) => {
            const value = column.value ? column.value(row, index) : row[column.key];
            return `"${String(value ?? "").replaceAll('"', '""')}"`;
          })
          .join(",")
      );
    });
    download(`${activeReport}-${currentPeriodKey()}.csv`, lines.join("\n"), "text/csv");
    recordExport(dataset.title, "CSV");
  }

  function recordExport(reportName, format) {
    state.reportExports.unshift({
      id: id(),
      reportName,
      period: currentPeriodKey(),
      format,
      generatedBy: "Admin",
      generatedAt: new Date().toISOString(),
    });
    audit("Report export", "reportExports", reportName, { reportName, format, period: currentPeriodKey() });
    saveState();
  }

  function download(filename, content, type = "application/json") {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function downloadBackup() {
    download(`modernlam-prototype-backup-${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(state, null, 2), "application/json");
    showToast("Backup downloaded.");
  }

  function resetData() {
    const confirmed = window.confirm("Reset all browser prototype data?");
    if (!confirmed) return;
    const freshState = seedState();
    Object.keys(state).forEach((key) => delete state[key]);
    Object.assign(state, freshState);
    saveState();
    showToast("Prototype data reset.");
    render();
  }

  function handleClick(event) {
    const viewButton = event.target.closest("[data-view]");
    if (viewButton) {
      activeView = viewButton.dataset.view;
      localStorage.setItem(VIEW_KEY, activeView);
      render();
      return;
    }
    const statusButton = event.target.closest("[data-period-status]");
    if (statusButton) {
      setPeriodStatus(statusButton.dataset.periodStatus);
      return;
    }
    const cancelButton = event.target.closest("[data-cancel]");
    if (cancelButton) {
      cancelRecord(cancelButton.dataset.cancel, cancelButton.dataset.id);
      return;
    }
    const action = event.target.closest("[data-action]")?.dataset.action;
    if (!action) return;
    if (action === "generate-salaries") generateSalaryDrafts();
    if (action === "print") window.print();
    if (action === "official-report") {
      recordExport(getReportDataset().title, "Official PDF print");
      window.print();
    }
    if (action === "export-csv") exportCurrentReportCsv();
    if (action === "download-backup") downloadBackup();
    if (action === "reset-data") resetData();
  }

  function handleChange(event) {
    const monthSelect = event.target.closest("[data-period-month]");
    const yearSelect = event.target.closest("[data-period-year]");
    if (monthSelect || yearSelect) {
      const month = document.querySelector("[data-period-month]").value;
      const year = document.querySelector("[data-period-year]").value;
      setPeriod(month, year);
      return;
    }
    const reportSelect = event.target.closest("[data-report-select]");
    if (reportSelect) {
      activeReport = reportSelect.value;
      localStorage.setItem(REPORT_KEY, activeReport);
      render();
    }
  }

  document.addEventListener("submit", handleSubmit);
  document.addEventListener("click", handleClick);
  document.addEventListener("change", handleChange);

  function init() {
    saveState();
    render();
  }

  window.ModernLamPrototype = {
    state,
    monthNames,
    supplierCategories,
    paymentModes,
    partnerTypes,
    paymentStatuses,
    salaryStatuses,
    periodStatuses,
    dayCodes,
    roles,
    currentPeriodKey,
    pad,
    getPeriod,
    isClosedPeriod,
    formatDate,
    defaultDate,
    daysInMonth,
    number,
    sum,
    money,
    escapeHtml,
    activeRows,
    scopedRows,
    employeeName,
    supplierName,
    paymentTargetLabel,
    employeeFunction,
    audit,
    addRecord,
    cancelRecord,
    showToast,
    statusClass,
    statusPill,
    formData,
    optionList,
    renderField,
    renderForm,
    renderTable,
    renderSection,
    renderHeader,
    closedNotice,
    totals,
    renderMetrics,
    registerView,
    setReportDatasetProvider,
    getActiveReport,
    getReportDataset,
    init,
  };
})();
