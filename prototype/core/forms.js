"use strict";

function setPeriod(month, year) {
  state.selected = { month: number(month), year: number(year) };
  ensurePeriod(state.selected.month, state.selected.year);
  saveState();
  render();
}

function setPeriodStatus(status) {
  const period = getPeriod();
  const before = { ...period };
  if (status === "Closed") {
    const blockers = closingChecklist().filter((item) => !item.ok);
    if (blockers.length) {
      period.status = "Under review";
      audit("Monthly closing blocked", "accounting_periods", period.id, blockers, before, "Automatic closing checklist failed");
      saveState();
      showToast(`Closing blocked: ${blockers.map((item) => item.item).join(", ")}.`);
      render();
      return;
    }
  }
  period.status = status;
  if (status === "Closed") {
    period.closedAt = new Date().toISOString();
    period.closedBy = currentUserDisplayName();
    period.closeNote = "Closed from prototype checklist.";
  }
  if (before.status === "Closed" && status !== "Closed") {
    period.reopenedAt = new Date().toISOString();
    period.reopenedBy = currentUserDisplayName();
    period.reopenNote = "Reopened from prototype controls.";
  }
  const action = status === "Closed" ? "Monthly closing" : before.status === "Closed" ? "Reopening closed month" : "Set period status";
  audit(action, "accounting_periods", period.id, period, before);
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

function nextAttendanceCode(currentCode) {
  if (!currentCode) return dayCodes[0];
  const index = dayCodes.indexOf(currentCode);
  if (index === -1) return dayCodes[0];
  return index === dayCodes.length - 1 ? "" : dayCodes[index + 1];
}

function setQuickAttendance(employeeId, date) {
  if (isClosedPeriod()) {
    showToast("Closed period is read-only.");
    return;
  }
  const existing = state.attendance.find((row) => row.periodKey === currentPeriodKey() && row.employeeId === employeeId && row.date === date && row.status !== "Cancelled");
  const nextCode = nextAttendanceCode(existing?.dayCode || "");
  if (existing) {
    existing.status = "Cancelled";
    audit("Replace attendance", "attendance", existing.id, existing);
  }
  if (!nextCode) {
    saveState();
    showToast("Attendance cleared.");
    render();
    return;
  }
  addRecord("attendance", {
    employeeId,
    date,
    dayCode: nextCode,
    note: "Quick grid entry",
    status: "Validated",
  });
}

function updateSalaryStatus(recordId, status) {
  if (isClosedPeriod()) {
    showToast("Closed period is read-only.");
    return;
  }
  const row = state.salaryReports.find((item) => item.id === recordId);
  if (!row) {
    showToast("Salary row not found.");
    return;
  }
  if (!salaryStatuses.includes(status)) {
    showToast("Unknown salary status.");
    return;
  }
  const before = { ...row };
  row.status = status;
  const action = status === "Validated" ? "Salary validation" : status === "Paid" ? "Salary payment" : "Update salary status";
  audit(action, "salaryReports", row.id, row, before);
  saveState();
  showToast(`Salary marked ${status}.`);
  render();
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
      showToast("Blocking: remark is required when a difference exists.");
      return;
    }
    addRecord("cashClosures", {
      date: data.date,
      user: data.user,
      realAmount: number(data.realAmount),
      virtualAmount: number(data.virtualAmount),
      difference,
      remark: data.remark.trim(),
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
    const orderTotal = number(data.orderTotal);
    if (paidAmount > 0 && !data.paymentMode) {
      showToast("Payment mode is required when paid amount exists.");
      return;
    }
    if (paidAmount > orderTotal) {
      showToast("Paid amount cannot exceed order total.");
      return;
    }
    const record = {
      supplierId: data.supplierId,
      category: data.category,
      date: data.date,
      orderTotal,
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
    const amount = number(data.amount);
    if (payment > 0 && !data.paymentMode) {
      showToast("Payment mode is required when payment exists.");
      return;
    }
    if (payment > amount) {
      showToast("Payment cannot exceed remaining balance.");
      return;
    }
    const record = {
      type: data.type,
      name: data.name,
      amount,
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
    if (!dayCodes.includes(data.dayCode)) {
      showToast("Unknown attendance code.");
      return;
    }
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

  if (formId === "document") {
    addRecord("attachments", {
      employeeId: data.employeeId,
      documentType: data.documentType,
      title: data.title,
      reference: data.reference,
      note: data.note,
      createdAt: new Date().toISOString(),
    });
  }

  if (formId === "user") {
    const saved = {
      id: id(),
      createdAt: new Date().toISOString(),
      username: data.username,
      fullName: data.fullName,
      role: data.role,
      isActive: data.isActive === "true",
      lastLoginAt: "",
    };
    state.users.push(saved);
    audit("Create user", "users", saved.id, saved);
    audit("Permission change", "users", saved.id, { username: saved.username, role: saved.role, isActive: saved.isActive }, "", "User role/status saved");
    saveState();
    showToast("Saved in browser storage.");
    render();
  }

  if (formId === "settings") {
    const before = { ...(state.settings || {}) };
    state.settings = {
      labName: data.labName.trim() || defaultPrototypeSettings.labName,
      nif: data.nif.trim() || defaultPrototypeSettings.nif,
      rip: data.rip.trim() || defaultPrototypeSettings.rip,
      currentUserDisplayName: data.currentUserDisplayName.trim() || defaultPrototypeSettings.currentUserDisplayName,
    };
    audit("Update prototype settings", "prototype_settings", "settings", state.settings, before, "Prototype settings saved");
    saveState();
    showToast("Prototype settings saved.");
    render();
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
