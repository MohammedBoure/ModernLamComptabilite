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
    closingChecklist,
    documentationCoverage,
    coverageFollowUpTasks,
    openQuestions,
    daysInMonth,
    pad,
    optionList,
    number,
    sum,
    statusPill,
    escapeHtml
  } = M;
  function renderAdmin() {
    return `
      ${renderHeader(
        "Administration",
        "Users, simplified permissions, audit log, backup, and browser-storage controls.",
        `<button class="text-btn secondary" type="button" data-action="download-backup" title="Download backup">B Backup</button>
         <button class="text-btn danger" type="button" data-action="reset-data" title="Reset prototype data">X Reset</button>`
      )}
      ${renderForm(
        "User",
        "user",
        [
          { name: "username", label: "Username", required: true },
          { name: "fullName", label: "Full Name", required: true },
          { name: "role", label: "Role", type: "select", options: roles },
          { name: "isActive", label: "Status", type: "select", options: [["true", "Active"], ["false", "Inactive"]], value: "true" },
        ],
        "Save user"
      )}
      ${renderSection(
        "Users",
        renderTable(
          [
            { label: "Username", key: "username" },
            { label: "Full Name", key: "fullName" },
            { label: "Role", key: "role" },
            { label: "Active", value: (row) => (row.isActive ? "Yes" : "No") },
            { label: "Last Login", value: (row) => (row.lastLoginAt ? new Date(row.lastLoginAt).toLocaleString() : "") },
          ],
          state.users,
          { collection: "users" }
        )
      )}
      ${renderSection(
        "Accounting Periods",
        renderTable(
          [
            { label: "Month", value: (row) => monthNames[row.month - 1] },
            { label: "Year", key: "year" },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
            { label: "Opened At", value: (row) => (row.openedAt ? new Date(row.openedAt).toLocaleString() : "") },
            { label: "Opened By", key: "openedBy" },
            { label: "Closed At", value: (row) => (row.closedAt ? new Date(row.closedAt).toLocaleString() : "") },
            { label: "Closed By", key: "closedBy" },
            { label: "Close Note", key: "closeNote" },
          ],
          state.periods
        )
      )}
      ${renderSection(
        "Monthly Closing Checklist",
        renderTable(
          [
            { label: "Condition", key: "item" },
            { label: "Status", value: (row) => statusPill(row.ok ? "Validated" : "Draft"), html: true },
            { label: "Detail", key: "detail" },
          ],
          closingChecklist()
        )
      )}
      ${renderSection("Permissions Matrix", renderPermissionsMatrix())}
      ${renderSection(
        "Documentation Coverage",
        renderTable(
          [
            { label: "Source", key: "source" },
            { label: "Area", key: "area" },
            { label: "Requirement", key: "requirement" },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
            { label: "Prototype Coverage", key: "prototypeCoverage" },
            { label: "Follow-up", key: "followUp" },
          ],
          documentationCoverage()
        )
      )}
      ${renderSection(
        "Coverage Follow-up Tasks",
        renderTable(
          [
            { label: "Priority", key: "priority" },
            { label: "Area", key: "area" },
            { label: "Task", key: "task" },
            { label: "Status", value: (row) => statusPill(row.status), html: true },
          ],
          coverageFollowUpTasks()
        )
      )}
      ${renderSection(
        "Open Decisions",
        renderTable(
          [
            { label: "Category", key: "category" },
            { label: "Decision to Validate", key: "question" },
          ],
          openQuestions()
        )
      )}
      ${renderSection(
        "Audit Log",
        renderTable(
          [
            { label: "Date", value: (row) => new Date(row.createdAt).toLocaleString() },
            { label: "User", key: "user" },
            { label: "Action", key: "action" },
            { label: "Entity", key: "entityType" },
            { label: "Entity ID", key: "entityId" },
            { label: "Reason", key: "reason" },
          ],
          state.auditLogs.slice(0, 80),
          { empty: "No audit entries." }
        )
      )}
    `;
  }

  function renderPermissionsMatrix() {
    const rows = [
      ["Dashboard", "Full", "Read", "Read", "Limited", "Limited", "Read"],
      ["Cash Closing", "Full", "Read", "Full", "Entry", "No", "Read"],
      ["Cash & Safe", "Full", "Read", "Full", "Limited", "No", "Read"],
      ["Suppliers", "Full", "Read", "Full", "No", "No", "Read"],
      ["Attendance", "Full", "Read", "Read", "No", "Full", "Read"],
      ["Salaries", "Full", "Read", "Review", "No", "Full", "Limited"],
      ["Reports", "Full", "Full", "Full", "Limited", "Limited", "Read"],
      ["HR", "Full", "Read", "No", "No", "Full", "Limited"],
      ["Administration", "Full", "No", "No", "No", "No", "No"],
    ].map((row) => ({
      screen: row[0],
      admin: row[1],
      direction: row[2],
      accountant: row[3],
      cashDesk: row[4],
      hr: row[5],
      viewer: row[6],
    }));
    return renderTable(
      [
        { label: "Screen", key: "screen" },
        { label: "Admin", key: "admin" },
        { label: "Direction", key: "direction" },
        { label: "Accountant", key: "accountant" },
        { label: "Cash Desk", key: "cashDesk" },
        { label: "HR", key: "hr" },
        { label: "Viewer", key: "viewer" },
      ],
      rows
    );
  }


  M.registerView('admin', renderAdmin);
})();
