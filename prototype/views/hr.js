(() => {
  "use strict";
  const M = window.ModernLamPrototype;
  const {
    state,
    monthNames,
    renderHeader,
    renderMetrics,
    renderSection,
    renderTable,
    renderForm,
    scopedRows,
    activeRows,
    defaultDate,
    employeeName,
    optionList,
    number,
    money,
    statusPill,
    escapeHtml,
  } = M;

  const hrTabs = ["Identity", "Contract", "Leave", "Attendance", "Salaries", "Documents", "History"];

  function renderHR() {
    const activeTab = getActiveHrTab();
    const selectedEmployee = getSelectedEmployee();
    const employeeOptions = visibleEmployees().map((employee) => [employee.id, employee.fullName]);

    return `
      ${renderHeader("Human Resources", "Employee file, contracts, leave balances, attendance, salary history, documents, and audit trail.")}
      ${renderHRAlerts()}
      ${renderSection("Employee List", renderEmployeeList())}
      ${renderSection(
        "Employee File",
        `
          ${renderEmployeeFileSelector(selectedEmployee, employeeOptions)}
          ${renderTabs(activeTab)}
          <div class="employee-file-body">
            ${selectedEmployee ? renderTabContent(activeTab, selectedEmployee, employeeOptions) : `<div class="empty-state">No employee selected.</div>`}
          </div>
        `
      )}
    `;
  }

  function getActiveHrTab() {
    const tab = localStorage.getItem(HR_TAB_KEY) || "Identity";
    return hrTabs.includes(tab) ? tab : "Identity";
  }

  function getSelectedEmployee() {
    const stored = localStorage.getItem(HR_EMPLOYEE_KEY);
    return visibleEmployees().find((employee) => employee.id === stored) || visibleEmployees()[0] || null;
  }

  function renderEmployeeFileSelector(employee, employeeOptions) {
    return `
      <div class="filter-bar employee-file-selector">
        <label>Employee
          <select data-hr-employee>${optionList(employeeOptions, employee?.id || "")}</select>
        </label>
        ${
          employee
            ? renderMetrics([
                { label: "Status", value: employee.status || "" },
                { label: "Age", value: calculateAge(employee.birthDate) || "N/A" },
                { label: "Leave Balance", value: leaveLabel(employee.id) },
                { label: "Active Contract", value: activeContractLabel(employee.id) },
              ])
            : ""
        }
      </div>
    `;
  }

  function renderTabs(activeTab) {
    return `
      <div class="tabs employee-tabs">
        ${hrTabs.map((tab) => `<button class="tab${activeTab === tab ? " active" : ""}" type="button" data-hr-tab="${escapeHtml(tab)}">${escapeHtml(tab)}</button>`).join("")}
      </div>
    `;
  }

  function renderTabContent(tab, employee, employeeOptions) {
    if (tab === "Identity") return renderIdentityTab(employee);
    if (tab === "Contract") return renderContractTab(employee, employeeOptions);
    if (tab === "Leave") return renderLeaveTab(employee, employeeOptions);
    if (tab === "Attendance") return renderAttendanceTab(employee);
    if (tab === "Salaries") return renderSalariesTab(employee);
    if (tab === "Documents") return renderDocumentsTab(employee, employeeOptions);
    return renderHistoryTab(employee);
  }

  function renderIdentityTab(employee) {
    return `
      <div class="grid two">
        ${renderForm(
          "New Employee",
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
        ${renderPanel(
          "Identity",
          renderTable(
            [
              { label: "Field", key: "field" },
              { label: "Value", key: "value" },
            ],
            [
              { field: "Full Name", value: employee.fullName },
              { field: "Function", value: employee.function },
              { field: "Birth Date", value: employee.birthDate },
              { field: "Age", value: calculateAge(employee.birthDate) },
              { field: "Birth Place", value: employee.birthPlace },
              { field: "Address", value: employee.address },
              { field: "Phone 01", value: employee.phone01 },
              { field: "Phone 02", value: employee.phone02 },
              { field: "Social Security Number", value: employee.socialSecurityNumber },
              { field: "ANEM Number", value: employee.anemNumber },
              { field: "Status", value: employee.status },
            ]
          )
        )}
      </div>
    `;
  }

  function renderContractTab(employee, employeeOptions) {
    return `
      <div class="grid two">
        ${renderForm(
          "Contract",
          "contract",
          [
            { name: "employeeId", label: "Employee", type: "select", options: employeeOptions, value: employee.id, required: true },
            { name: "hireDate", label: "Hire Date", type: "date", value: defaultDate(), required: true },
            { name: "cnasRegistrationDate", label: "CNAS Date", type: "date" },
            { name: "contractType", label: "Contract", type: "select", options: ["CDI", "CDD", "Internship", "Other"] },
            { name: "startsAt", label: "From", type: "date", value: defaultDate(), required: true },
            { name: "endsAt", label: "To", type: "date" },
            { name: "resignationDate", label: "Resignation", type: "date" },
            { name: "status", label: "Status", type: "select", options: ["Active", "Expired", "Resigned"], value: "Active" },
            { name: "remark", label: "Remark", type: "textarea", full: true },
          ],
          "Save contract"
        )}
        ${renderPanel(
          "Contracts",
          renderTable(
            [
              { label: "Hire Date", key: "hireDate" },
              { label: "CNAS", key: "cnasRegistrationDate" },
              { label: "Contract", key: "contractType" },
              { label: "From", key: "startsAt" },
              { label: "To", key: "endsAt" },
              { label: "Resignation", key: "resignationDate" },
              { label: "Status", value: (row) => statusPill(row.status), html: true },
              { label: "Remark", key: "remark" },
            ],
            contractsFor(employee.id),
            { collection: "contracts", empty: "No contracts for this employee." }
          )
        )}
      </div>
    `;
  }

  function renderLeaveTab(employee, employeeOptions) {
    return `
      <div class="grid two">
        ${renderForm(
          "Leave Balance",
          "leave",
          [
            { name: "employeeId", label: "Employee", type: "select", options: employeeOptions, value: employee.id, required: true },
            { name: "year", label: "Year", type: "number", value: state.selected.year, required: true },
            { name: "acquiredDays", label: "Acquired Days", type: "number", min: 0, step: "0.5", required: true },
            { name: "usedDays", label: "Used Days", type: "number", min: 0, step: "0.5" },
            { name: "remark", label: "Remark", type: "textarea", full: true },
          ],
          "Save leave"
        )}
        ${renderPanel(
          "Leave",
          renderTable(
            [
              { label: "Year", key: "year" },
              { label: "Acquired", key: "acquiredDays" },
              { label: "Used", key: "usedDays" },
              { label: "Remaining", key: "remainingDays" },
              { label: "Remark", key: "remark" },
            ],
            leavesFor(employee.id),
            { collection: "leaves", empty: "No leave balances for this employee." }
          )
        )}
      </div>
    `;
  }

  function renderAttendanceTab(employee) {
    const rows = scopedRows("attendance").filter((row) => row.employeeId === employee.id);
    return renderPanel(
      "Attendance",
      renderTable(
        [
          { label: "Date", key: "date" },
          { label: "Code", key: "dayCode" },
          { label: "Note", key: "note" },
          { label: "Status", value: (row) => statusPill(row.status), html: true },
        ],
        rows,
        { empty: "No attendance entries for this month." }
      )
    );
  }

  function renderSalariesTab(employee) {
    const rows = scopedRows("salaryReports").filter((row) => row.employeeId === employee.id);
    return `
      <div class="read-only-note">Read-only salary history.</div>
      ${renderPanel(
        "Salary History",
        renderTable(
          [
            { label: "Period", value: () => `${monthNames[state.selected.month - 1]} ${state.selected.year}` },
            { label: "Salary", key: "finalSalary", amount: true, format: money },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
            { label: "Remark", key: "remark" },
          ],
          rows,
          { empty: "No salary history for this month." }
        )
      )}
    `;
  }

  function renderDocumentsTab(employee, employeeOptions) {
    const docs = activeRows("attachments").filter((row) => row.employeeId === employee.id);
    return `
      <div class="grid two">
        ${renderForm(
          "Document",
          "document",
          [
            { name: "employeeId", label: "Employee", type: "select", options: employeeOptions, value: employee.id, required: true },
            { name: "documentType", label: "Type", type: "select", options: ["Identity", "Contract", "CNAS", "Leave", "Salary", "Other"] },
            { name: "title", label: "Title", required: true },
            { name: "reference", label: "Reference" },
            { name: "note", label: "Note", type: "textarea", full: true },
          ],
          "Save document"
        )}
        ${renderPanel(
          "Documents",
          renderTable(
            [
              { label: "Type", key: "documentType" },
              { label: "Title", key: "title" },
              { label: "Reference", key: "reference" },
              { label: "Note", key: "note" },
              { label: "Created At", value: (row) => (row.createdAt ? new Date(row.createdAt).toLocaleString() : "") },
            ],
            docs,
            { collection: "attachments", empty: "No documents for this employee." }
          )
        )}
      </div>
    `;
  }

  function renderHistoryTab(employee) {
    const relatedTypes = new Set(["employees", "contracts", "leaves", "attachments", "attendance", "salaryReports"]);
    const rows = state.auditLogs.filter((row) => relatedTypes.has(row.entityType) && employeeHistoryMatches(row, employee.id)).slice(0, 80);
    return renderPanel(
      "History",
      renderTable(
        [
          { label: "Date", value: (row) => new Date(row.createdAt).toLocaleString() },
          { label: "User", key: "user" },
          { label: "Action", key: "action" },
          { label: "Entity", key: "entityType" },
          { label: "Reason", key: "reason" },
        ],
        rows,
        { empty: "No history for this employee yet." }
      )
    );
  }

  function renderEmployeeList() {
    const filters = getHrFilters();
    const functions = uniqueOptions(visibleEmployees().map((employee) => employee.function));
    const rows = filteredEmployees(filters).map((employee, index) => ({
      ...employee,
      number: index + 1,
      activeContract: activeContractLabel(employee.id),
      yearLeave: leaveLabel(employee.id),
      age: calculateAge(employee.birthDate),
    }));

    return `
      <div class="filter-bar hr-filter-bar">
        <label>Search
          <input type="search" value="${escapeHtml(filters.search)}" data-hr-list-filter="search" placeholder="Employee name">
        </label>
        <label>Function
          <select data-hr-list-filter="function">${optionList([["", "All functions"], ...functions.map((item) => [item, item])], filters.function)}</select>
        </label>
        <label>Status
          <select data-hr-list-filter="status">${optionList([["", "All statuses"], ["Active", "Active"], ["Inactive", "Inactive"]], filters.status)}</select>
        </label>
        <label>Contract
          <select data-hr-list-filter="contract">${optionList(
            [
              ["", "All contracts"],
              ["active", "Active contract"],
              ["missing", "No active contract"],
              ["ending", "Ending soon"],
            ],
            filters.contract
          )}</select>
        </label>
        <button class="text-btn" type="button" data-action="reset-hr-filters">Reset</button>
      </div>
      ${renderTable(
        [
          { label: "Number", key: "number" },
          { label: "Full Name", key: "fullName" },
          { label: "Function", key: "function" },
          { label: "Birth Date", key: "birthDate" },
          { label: "Age", key: "age" },
          { label: "Phone 01", key: "phone01" },
          { label: "Phone 02", key: "phone02" },
          { label: "Status", value: (row) => statusPill(row.status), html: true },
          { label: "Active Contract", key: "activeContract" },
          { label: "Year Leave", key: "yearLeave" },
        ],
        rows,
        { collection: "employees", empty: "No employees match these filters." }
      )}
    `;
  }

  function renderHRAlerts() {
    const activeEmployees = visibleEmployees().filter((employee) => employee.status === "Active");
    const noContract = activeEmployees.filter((employee) => !activeContract(employee.id));
    const endingSoon = activeRows("contracts").filter((contract) => contract.status === "Active" && contract.endsAt && daysUntil(contract.endsAt) >= 0 && daysUntil(contract.endsAt) <= 45);
    const missingLeave = activeEmployees.filter((employee) => !currentYearLeave(employee.id));
    const alerts = [
      {
        title: "No active contract",
        text: noContract.length ? `${noContract.length} active employees` : "All active employees covered",
        severity: noContract.length ? "blocking" : "info",
      },
      {
        title: "Contract ending soon",
        text: endingSoon.length ? `${endingSoon.length} contracts within 45 days` : "No contracts ending soon",
        severity: endingSoon.length ? "warning" : "info",
      },
      {
        title: "Current-year leave balance",
        text: missingLeave.length ? `${missingLeave.length} employees missing balance` : "Leave balances exist",
        severity: missingLeave.length ? "warning" : "info",
      },
    ];

    return `<div class="alert-list hr-alerts">${alerts.map(renderHRAlert).join("")}</div>`;
  }

  function renderHRAlert(alert) {
    return `
      <div class="alert-item ${escapeHtml(alert.severity)}">
        <span class="alert-copy">
          <strong>${escapeHtml(alert.title)}</strong>
          <span>${escapeHtml(alert.text)}</span>
        </span>
        <span class="alert-severity">${escapeHtml(alert.severity)}</span>
      </div>
    `;
  }

  function renderPanel(title, body) {
    return `<div class="panel-block"><h3>${escapeHtml(title)}</h3>${body}</div>`;
  }

  function visibleEmployees() {
    return activeRows("employees");
  }

  function getHrFilters() {
    return {
      search: localStorage.getItem(HR_SEARCH_FILTER_KEY) || "",
      function: localStorage.getItem(HR_FUNCTION_FILTER_KEY) || "",
      status: localStorage.getItem(HR_STATUS_FILTER_KEY) || "",
      contract: localStorage.getItem(HR_CONTRACT_FILTER_KEY) || "",
    };
  }

  function filteredEmployees(filters) {
    const search = filters.search.trim().toLowerCase();
    return visibleEmployees().filter((employee) => {
      const matchesSearch = !search || employee.fullName.toLowerCase().includes(search);
      const matchesFunction = !filters.function || employee.function === filters.function;
      const matchesStatus = !filters.status || employee.status === filters.status;
      const contract = activeContract(employee.id);
      const matchesContract =
        !filters.contract ||
        (filters.contract === "active" && Boolean(contract)) ||
        (filters.contract === "missing" && !contract) ||
        (filters.contract === "ending" && contract?.endsAt && daysUntil(contract.endsAt) >= 0 && daysUntil(contract.endsAt) <= 45);
      return matchesSearch && matchesFunction && matchesStatus && matchesContract;
    });
  }

  function uniqueOptions(values) {
    return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b));
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

  function activeContract(employeeId) {
    return activeRows("contracts").find((row) => row.employeeId === employeeId && row.status === "Active");
  }

  function activeContractLabel(employeeId) {
    const contract = activeContract(employeeId);
    if (!contract) return "None";
    return `${contract.contractType} from ${contract.startsAt}${contract.endsAt ? ` to ${contract.endsAt}` : ""}`;
  }

  function contractsFor(employeeId) {
    return activeRows("contracts").filter((row) => row.employeeId === employeeId);
  }

  function currentYearLeave(employeeId) {
    return activeRows("leaves").find((row) => row.employeeId === employeeId && number(row.year) === state.selected.year);
  }

  function leavesFor(employeeId) {
    return activeRows("leaves").filter((row) => row.employeeId === employeeId);
  }

  function leaveLabel(employeeId) {
    const leave = currentYearLeave(employeeId);
    return leave ? `${leave.remainingDays} days` : "No balance";
  }

  function daysUntil(date) {
    const target = new Date(date);
    if (Number.isNaN(target.getTime())) return Number.POSITIVE_INFINITY;
    return Math.ceil((target.getTime() - Date.now()) / 86400000);
  }

  function employeeHistoryMatches(row, employeeId) {
    if (row.entityType === "employees" && row.entityId === employeeId) return true;
    return [row.oldValues, row.newValues].some((value) => String(value || "").includes(employeeId) || String(value || "").includes(employeeName(employeeId)));
  }

  M.registerView("hr", renderHR);
})();
