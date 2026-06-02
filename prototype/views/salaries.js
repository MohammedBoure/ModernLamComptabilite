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
    daysInMonth,
    pad,
    optionList,
    number,
    sum,
    statusPill,
    escapeHtml
  } = M;
  function renderSalaries() {
    const employeeOptions = state.employees.filter((row) => row.status !== "Inactive").map((employee) => [employee.id, employee.fullName]);
    const actions = `<button class="text-btn secondary" type="button" data-action="generate-salaries" title="Generate drafts">+ Generate Drafts</button>`;
    return `
      ${renderHeader("Salaries", "Monthly salary report with additions, deductions, validation, and payment status.", actions)}
      ${closedNotice()}
      ${renderForm(
        "Salary Row",
        "salary",
        [
          { name: "employeeId", label: "Employee", type: "select", options: employeeOptions, required: true },
          { name: "baseNetSalary", label: "Net Salary", type: "number", min: 0, step: "0.01", required: true },
          { name: "overtimePresence", label: "Extra Attendance", type: "number", min: 0, step: "0.01" },
          { name: "lamTravel", label: "LAM Travel", type: "number", min: 0, step: "0.01" },
          { name: "nightGuard", label: "Night Guard", type: "number", min: 0, step: "0.01" },
          { name: "fridayDayGuard", label: "Friday Day Guard", type: "number", min: 0, step: "0.01" },
          { name: "fridayNightGuard", label: "Friday Night Guard", type: "number", min: 0, step: "0.01" },
          { name: "absence", label: "Absence", type: "number", min: 0, step: "0.01" },
          { name: "bonus", label: "Bonus", type: "number", min: 0, step: "0.01" },
          { name: "leave", label: "Leave", type: "number", min: 0, step: "0.01" },
          { name: "penalties", label: "Penalties", type: "number", min: 0, step: "0.01" },
          { name: "advances", label: "Advances", type: "number", min: 0, step: "0.01" },
          { name: "status", label: "Status", type: "select", options: salaryStatuses, value: "Draft" },
          { name: "remark", label: "Remark", type: "textarea", full: true },
        ],
        "Save salary",
        { periodScoped: true }
      )}
      ${renderSection(
        "Salary Report",
        renderTable(
          [
            { label: "Person", value: (row) => employeeName(row.employeeId) },
            { label: "Position", value: (row) => employeeFunction(row.employeeId) },
            { label: "Net Salary", key: "baseNetSalary", amount: true, format: money },
            { label: "Overtime", key: "overtimePresence", amount: true, format: money },
            { label: "LAM Travel", key: "lamTravel", amount: true, format: money },
            { label: "Guards", value: (row) => money(number(row.nightGuard) + number(row.fridayDayGuard) + number(row.fridayNightGuard)), amount: true },
            { label: "Absence", key: "absence", amount: true, format: money },
            { label: "Bonus", key: "bonus", amount: true, format: money },
            { label: "Deductions", value: (row) => money(number(row.penalties) + number(row.advances)), amount: true },
            { label: "Salary", key: "finalSalary", amount: true, format: money },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
          ],
          scopedRows("salaryReports"),
          { collection: "salaryReports" }
        )
      )}
    `;
  }

  function employeeFunction(employeeId) {
    const employee = state.employees.find((row) => row.id === employeeId);
    return employee ? employee.function : "";
  }


  M.registerView('salaries', renderSalaries);
})();
