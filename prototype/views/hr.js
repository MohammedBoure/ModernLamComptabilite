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
  function renderHR() {
    const employeeOptions = state.employees.map((employee) => [employee.id, employee.fullName]);
    return `
      ${renderHeader("Human Resources", "Employees, contracts, leave balances, and administrative files.")}
      <div class="grid three">
        ${renderForm(
          "Employee",
          "employee",
          [
            { name: "fullName", label: "Full Name", required: true, span: 2 },
            { name: "function", label: "Function", required: true },
            { name: "birthDate", label: "Birth Date", type: "date" },
            { name: "birthPlace", label: "Birth Place" },
            { name: "phone01", label: "Phone 01" },
            { name: "phone02", label: "Phone 02" },
            { name: "socialSecurityNumber", label: "Social Security Number" },
            { name: "anemNumber", label: "ANEM Number" },
            { name: "status", label: "Status", type: "select", options: ["Active", "Inactive"], value: "Active" },
            { name: "address", label: "Address", type: "textarea", full: true },
          ],
          "Save employee"
        )}
        ${renderForm(
          "Contract",
          "contract",
          [
            { name: "employeeId", label: "Employee", type: "select", options: employeeOptions, required: true },
            { name: "hireDate", label: "Hire Date", type: "date", required: true },
            { name: "cnasRegistrationDate", label: "CNAS Date", type: "date" },
            { name: "contractType", label: "Contract", type: "select", options: ["CDI", "CDD", "Internship", "Other"] },
            { name: "startsAt", label: "From", type: "date", required: true },
            { name: "endsAt", label: "To", type: "date" },
            { name: "resignationDate", label: "Resignation", type: "date" },
            { name: "status", label: "Status", type: "select", options: ["Active", "Expired", "Resigned"], value: "Active" },
            { name: "remark", label: "Remark", type: "textarea", full: true },
          ],
          "Save contract"
        )}
        ${renderForm(
          "Leave Balance",
          "leave",
          [
            { name: "employeeId", label: "Employee", type: "select", options: employeeOptions, required: true },
            { name: "year", label: "Year", type: "number", value: state.selected.year, required: true },
            { name: "acquiredDays", label: "Acquired Days", type: "number", min: 0, step: "0.5", required: true },
            { name: "usedDays", label: "Used Days", type: "number", min: 0, step: "0.5" },
            { name: "remark", label: "Remark", type: "textarea", full: true },
          ],
          "Save leave"
        )}
      </div>
      ${renderSection(
        "Employees",
        renderTable(
          [
            { label: "Full Name", key: "fullName" },
            { label: "Function", key: "function" },
            { label: "Birth Date", key: "birthDate" },
            { label: "Age", value: (row) => calculateAge(row.birthDate) },
            { label: "Phone 01", key: "phone01" },
            { label: "Status", key: "status" },
            { label: "Active Contract", value: (row) => activeContractLabel(row.id) },
            { label: "Year Leave", value: (row) => leaveLabel(row.id) },
          ],
          state.employees,
          { collection: "employees" }
        )
      )}
      ${renderSection(
        "Contracts",
        renderTable(
          [
            { label: "Employee", value: (row) => employeeName(row.employeeId) },
            { label: "Hire Date", key: "hireDate" },
            { label: "CNAS", key: "cnasRegistrationDate" },
            { label: "Contract", key: "contractType" },
            { label: "From", key: "startsAt" },
            { label: "To", key: "endsAt" },
            { label: "Resignation", key: "resignationDate" },
            { label: "Status", key: "status" },
          ],
          state.contracts,
          { collection: "contracts" }
        )
      )}
      ${renderSection(
        "Leave",
        renderTable(
          [
            { label: "Employee", value: (row) => employeeName(row.employeeId) },
            { label: "Year", key: "year" },
            { label: "Acquired", key: "acquiredDays" },
            { label: "Used", key: "usedDays" },
            { label: "Remaining", key: "remainingDays" },
            { label: "Remark", key: "remark" },
          ],
          state.leaves,
          { collection: "leaves" }
        )
      )}
    `;
  }

  function calculateAge(date) {
    if (!date) return "";
    const birth = new Date(date);
    if (Number.isNaN(birth.getTime())) return "";
    const now = new Date();
    let age = now.getFullYear() - birth.getFullYear();
    const monthDiff = now.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < birth.getDate())) age -= 1;
    return age;
  }

  function activeContractLabel(employeeId) {
    const contract = state.contracts.find((row) => row.employeeId === employeeId && row.status === "Active");
    return contract ? `${contract.contractType} from ${contract.startsAt}` : "None";
  }

  function leaveLabel(employeeId) {
    const leave = state.leaves.find((row) => row.employeeId === employeeId && number(row.year) === state.selected.year);
    return leave ? `${leave.remainingDays} days` : "No balance";
  }


  M.registerView('hr', renderHR);
})();
