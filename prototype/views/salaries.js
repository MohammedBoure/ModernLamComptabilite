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
    isClosedPeriod,
    renderHeader,
    closedNotice,
    renderMetrics,
    totals,
    money,
    renderSection,
    renderAssumptionNotice,
    renderTable,
    scopedRows,
    renderForm,
    renderField,
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
    const salaryRows = scopedRows("salaryReports");
    const draftRows = salaryRows.filter((row) => row.status === "Draft").length;
    const actions = `<button class="text-btn secondary" type="button" data-action="generate-salaries" title="Generate drafts">+ Generate Drafts</button>`;
    return `
      ${renderHeader("Salaries", "Monthly salary report with additions, deductions, validation, and payment status.", actions)}
      ${closedNotice()}
      ${renderAssumptionNotice("Prototype assumptions - payroll decisions still tracked", [
        "Official salary formula is not final.",
        "Guard prices and absence unit are manual prototype inputs.",
        "Leave treatment, day 15 rule, and carry-over remain open decisions.",
      ])}
      ${renderMetrics([
        { label: "Draft Salaries", value: draftRows, detail: "Blocks monthly closing" },
        { label: "Validated", value: salaryRows.filter((row) => row.status === "Validated").length, detail: "Ready to pay" },
        { label: "Paid", value: salaryRows.filter((row) => row.status === "Paid").length, detail: "Closed payroll rows" },
      ])}
      ${renderSalaryForm(employeeOptions)}
      ${renderSection("Prototype Salary Formula", renderFormulaNote())}
      ${renderSection(
        "Salary Report",
        renderTable(
          [
            { label: "Person", value: (row) => employeeName(row.employeeId) },
            { label: "Position", value: (row) => employeeFunction(row.employeeId) },
            { label: "Net Salary", key: "baseNetSalary", amount: true, format: money },
            { label: "Additions", value: (row) => money(salaryAdditions(row)), amount: true },
            { label: "Absence", key: "absence", amount: true, format: money },
            { label: "Deductions", value: (row) => money(salaryDeductions(row)), amount: true },
            { label: "Salary", key: "finalSalary", amount: true, format: money },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
            { label: "Actions", value: renderSalaryActions, html: true },
          ],
          salaryRows,
          { collection: "salaryReports" }
        )
      )}
    `;
  }

  function renderSalaryForm(employeeOptions) {
    const disabled = isClosedPeriod();
    return `
      <div class="form-card salary-form">
        <h2>Salary Row</h2>
        <form data-form="salary">
          <div class="salary-form-grid">
            <fieldset class="salary-group">
              <legend>Base</legend>
              ${renderField({ name: "employeeId", label: "Employee", type: "select", options: employeeOptions, required: true }, disabled)}
              ${renderField({ name: "baseNetSalary", label: "Net Salary", type: "number", min: 0, step: "0.01", required: true }, disabled)}
              ${renderField({ name: "status", label: "Status", type: "select", options: salaryStatuses, value: "Draft" }, disabled)}
            </fieldset>
            <fieldset class="salary-group additions">
              <legend>Additions</legend>
              ${renderField({ name: "overtimePresence", label: "Extra Attendance", type: "number", min: 0, step: "0.01" }, disabled)}
              ${renderField({ name: "lamTravel", label: "LAM Travel", type: "number", min: 0, step: "0.01" }, disabled)}
              ${renderField({ name: "nightGuard", label: "Night Guard", type: "number", min: 0, step: "0.01" }, disabled)}
              ${renderField({ name: "fridayDayGuard", label: "Friday Day Guard", type: "number", min: 0, step: "0.01" }, disabled)}
              ${renderField({ name: "fridayNightGuard", label: "Friday Night Guard", type: "number", min: 0, step: "0.01" }, disabled)}
              ${renderField({ name: "bonus", label: "Bonus", type: "number", min: 0, step: "0.01" }, disabled)}
            </fieldset>
            <fieldset class="salary-group deductions">
              <legend>Deductions</legend>
              ${renderField({ name: "absence", label: "Absence", type: "number", min: 0, step: "0.01" }, disabled)}
              ${renderField({ name: "penalties", label: "Penalties", type: "number", min: 0, step: "0.01" }, disabled)}
              ${renderField({ name: "advances", label: "Advances", type: "number", min: 0, step: "0.01" }, disabled)}
            </fieldset>
            <fieldset class="salary-group tracked">
              <legend>Tracked</legend>
              ${renderField({ name: "leave", label: "Leave", type: "number", min: 0, step: "0.01" }, disabled)}
              ${renderField({ name: "remark", label: "Remark", type: "textarea", full: true }, disabled)}
            </fieldset>
          </div>
          <div class="action-row">
            <button class="text-btn primary" type="submit" title="Save salary"${disabled ? " disabled" : ""}>+ Save salary</button>
          </div>
        </form>
      </div>
    `;
  }

  function renderFormulaNote() {
    return `
      <div class="formula-note">
        <strong>Prototype formula assumption</strong>
        <span>Net Salary + Extra Attendance + LAM Travel + Guards + Bonus - Absence - Penalties - Advances.</span>
        <span>Guard prices, absence unit, leave treatment, and the official payroll rule remain tracked decisions.</span>
      </div>
    `;
  }

  function salaryAdditions(row) {
    return number(row.overtimePresence) + number(row.lamTravel) + number(row.nightGuard) + number(row.fridayDayGuard) + number(row.fridayNightGuard) + number(row.bonus);
  }

  function salaryDeductions(row) {
    return number(row.absence) + number(row.penalties) + number(row.advances);
  }

  function renderSalaryActions(row) {
    const disabled = isClosedPeriod();
    return `
      <div class="row-actions">
        <button class="text-btn" type="button" data-salary-status="Validated" data-id="${escapeHtml(row.id)}" title="Validate salary"${disabled || row.status !== "Draft" ? " disabled" : ""}>Validate</button>
        <button class="text-btn secondary" type="button" data-salary-status="Paid" data-id="${escapeHtml(row.id)}" title="Mark salary paid"${disabled || row.status === "Paid" ? " disabled" : ""}>Mark Paid</button>
      </div>
    `;
  }

  function employeeFunction(employeeId) {
    const employee = state.employees.find((row) => row.id === employeeId);
    return employee ? employee.function : "";
  }


  M.registerView('salaries', renderSalaries);
})();
