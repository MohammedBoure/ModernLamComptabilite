(() => {
  "use strict";
  const M = window.ModernLamPrototype;
  const {
    state,
    monthNames,
    roles,
    renderHeader,
    renderMetrics,
    renderSection,
    renderTable,
    renderForm,
    renderAssumptionNotice,
    closingChecklist,
    documentationCoverage,
    coverageFollowUpTasks,
    openQuestions,
    statusPill,
    prototypeSettings,
    currentUserDisplayName,
    auditOperation,
    currentPeriodKey,
    escapeHtml,
  } = M;

  function renderAdmin() {
    const settings = prototypeSettings();
    const checklistRows = sortedClosingChecklist();
    const blockers = checklistRows.filter((row) => !row.ok);
    const period = state.periods.find((row) => `${row.year}-${String(row.month).padStart(2, "0")}` === currentPeriodKey());

    return `
      ${renderHeader(
        "Administration",
        "Prototype control center for users, permissions, periods, closing, audit, settings, backup, and browser-storage controls.",
        `<button class="text-btn secondary" type="button" data-action="download-backup" title="Download backup">B Backup</button>
         <button class="text-btn danger" type="button" data-action="reset-data" title="Reset prototype data">X Reset</button>`
      )}
      ${renderMetrics([
        { label: "Current User", value: currentUserDisplayName(), detail: "Prototype setting" },
        { label: "Active Users", value: state.users.filter((row) => row.isActive).length, detail: `${state.users.length} total users` },
        { label: "Period Status", value: period?.status || "", detail: `${monthNames[state.selected.month - 1]} ${state.selected.year}` },
        { label: "Closing Blockers", value: blockers.length, detail: blockers.length ? "Review checklist" : "Ready to close", severity: blockers.length ? "blocking" : "info" },
      ])}
      ${renderPrototypeSettingsForm(settings)}
      ${renderUserForm()}
      ${renderSection("Users", renderUsersTable())}
      ${renderAssumptionNotice("Prototype assumption - closing authorization", [
        "Close/Reopen controls are visible in the prototype for testing.",
        "The role authorized to close or reopen a month remains a tracked open decision.",
      ])}
      ${renderSection("Accounting Periods", renderPeriodsTable(), renderPeriodActions())}
      ${renderSection("Monthly Closing Checklist", renderClosingChecklist(checklistRows), renderPeriodActions())}
      ${renderSection("Audit Log", renderAuditLog())}
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
            { label: "Status", value: (row) => statusPill(row.status), html: true },
            { label: "Prototype Treatment", key: "prototypeTreatment" },
          ],
          openQuestions()
        )
      )}
    `;
  }

  function renderPrototypeSettingsForm(settings) {
    return renderForm(
      "Prototype Settings",
      "settings",
      [
        { name: "labName", label: "Lab Name", value: settings.labName, required: true, span: 2 },
        { name: "nif", label: "NIF", value: settings.nif, required: true },
        { name: "rip", label: "RIP", value: settings.rip, required: true },
        { name: "currentUserDisplayName", label: "Current User Display Name", value: settings.currentUserDisplayName, required: true, span: 2 },
      ],
      "Save settings"
    );
  }

  function renderUserForm() {
    return renderForm(
      "User",
      "user",
      [
        { name: "username", label: "Username", required: true },
        { name: "fullName", label: "Full Name", required: true },
        { name: "role", label: "Role", type: "select", options: roles },
        { name: "isActive", label: "Status", type: "select", options: [["true", "Active"], ["false", "Inactive"]], value: "true" },
      ],
      "Save user"
    );
  }

  function renderUsersTable() {
    return renderTable(
      [
        { label: "Username", key: "username" },
        { label: "Full Name", key: "fullName" },
        { label: "Role", key: "role" },
        { label: "Status", value: (row) => statusPill(row.isActive ? "Active" : "Inactive"), html: true },
        { label: "Last Login", value: (row) => (row.lastLoginAt ? new Date(row.lastLoginAt).toLocaleString() : "") },
      ],
      state.users,
      { collection: "users" }
    );
  }

  function renderPeriodsTable() {
    return renderTable(
      [
        { label: "Month", value: (row) => monthNames[row.month - 1] },
        { label: "Year", key: "year" },
        { label: "Status", value: (row) => statusPill(row.status), html: true },
        { label: "Opened At", value: (row) => formatDateTime(row.openedAt) },
        { label: "Opened By", key: "openedBy" },
        { label: "Closed At", value: (row) => formatDateTime(row.closedAt) },
        { label: "Closed By", key: "closedBy" },
        { label: "Reopened At", value: (row) => formatDateTime(row.reopenedAt) },
        { label: "Reopened By", key: "reopenedBy" },
        { label: "Close Note", key: "closeNote" },
      ],
      state.periods
    );
  }

  function renderClosingChecklist(rows) {
    return renderTable(
      [
        { label: "Priority", key: "priority" },
        { label: "Condition", key: "item" },
        { label: "Status", value: (row) => statusPill(row.ok ? "Ready" : "Blocking"), html: true },
        { label: "Detail", key: "detail" },
      ],
      rows
    );
  }

  function renderAuditLog() {
    return renderTable(
      [
        { label: "Date", value: (row) => formatDateTime(row.createdAt) },
        { label: "User", key: "user" },
        { label: "Operation", value: (row) => statusPill(auditOperation(row)), html: true },
        { label: "Action", key: "action" },
        { label: "Entity", key: "entityType" },
        { label: "Entity ID", key: "entityId" },
        { label: "Old Values", value: (row) => shortValue(row.oldValues) },
        { label: "New Values", value: (row) => shortValue(row.newValues) },
        { label: "Reason", key: "reason" },
      ],
      state.auditLogs.slice(0, 120),
      { empty: "No audit entries." }
    );
  }

  function renderPeriodActions() {
    return `
      <button class="text-btn primary" type="button" data-period-status="Closed" title="Close selected month">Close</button>
      <button class="text-btn" type="button" data-period-status="Under review" title="Mark selected month under review">Review</button>
      <button class="text-btn" type="button" data-period-status="Open" title="Reopen selected month">Reopen</button>
    `;
  }

  function sortedClosingChecklist() {
    return closingChecklist()
      .map((row) => ({ ...row, priority: row.ok ? "Ready" : "Blocker" }))
      .sort((a, b) => Number(a.ok) - Number(b.ok) || a.item.localeCompare(b.item));
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

  function formatDateTime(value) {
    return value ? new Date(value).toLocaleString() : "";
  }

  function shortValue(value) {
    const text = String(value || "");
    return text.length > 80 ? `${text.slice(0, 77)}...` : text;
  }

  M.registerView("admin", renderAdmin);
})();
