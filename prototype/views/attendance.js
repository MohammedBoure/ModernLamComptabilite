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
  function renderAttendance() {
    const employeeOptions = state.employees.filter((row) => row.status !== "Inactive").map((employee) => [employee.id, employee.fullName]);
    const grid = renderAttendanceGrid();
    return `
      ${renderHeader("Attendance", "Monthly attendance grid using P, ABS, G, GV-J, GV-N, C, C.M, REC, and P+.")}
      ${closedNotice()}
      ${renderForm(
        "Attendance Entry",
        "attendance",
        [
          { name: "employeeId", label: "Employee", type: "select", options: employeeOptions, required: true },
          { name: "date", label: "Date", type: "date", value: defaultDate(), required: true },
          { name: "dayCode", label: "Code", type: "select", options: dayCodes, required: true },
          { name: "note", label: "Note", type: "textarea", full: true },
        ],
        "Save attendance",
        { periodScoped: true }
      )}
      ${renderSection("Monthly Grid", grid)}
      ${renderSection(
        "Attendance Entries",
        renderTable(
          [
            { label: "Date", key: "date" },
            { label: "Employee", value: (row) => employeeName(row.employeeId) },
            { label: "Code", key: "dayCode" },
            { label: "Note", key: "note" },
          ],
          scopedRows("attendance"),
          { collection: "attendance" }
        )
      )}
    `;
  }

  function renderAttendanceGrid() {
    const days = Array.from({ length: daysInMonth() }, (_, index) => index + 1);
    const employees = state.employees.filter((row) => row.status !== "Inactive");
    if (!employees.length) return `<div class="empty-state">No active employees.</div>`;
    const rows = employees
      .map((employee) => {
        const cells = days
          .map((day) => {
            const date = `${state.selected.year}-${pad(state.selected.month)}-${pad(day)}`;
            const entry = scopedRows("attendance").find((row) => row.employeeId === employee.id && row.date === date);
            const code = entry ? entry.dayCode : "";
            return `<td class="day-cell ${codeClass(code)}">${escapeHtml(code)}</td>`;
          })
          .join("");
        const totals = countCodes(employee.id);
        return `<tr><td>${escapeHtml(employee.fullName)}</td>${cells}<td>${totals.present}</td><td>${totals.absence}</td><td>${totals.guards}</td><td>${totals.leave}</td></tr>`;
      })
      .join("");
    return `
      <div class="table-wrap attendance-grid">
        <table>
          <thead>
            <tr><th>Employee</th>${days.map((day) => `<th class="day-cell">${day}</th>`).join("")}<th>P</th><th>ABS</th><th>Guards</th><th>Leave</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  function codeClass(code) {
    if (code === "P" || code === "P+") return "code-p";
    if (code === "ABS") return "code-abs";
    if (["G", "GV-J", "GV-N"].includes(code)) return "code-guard";
    return "";
  }

  function countCodes(employeeId) {
    const rows = scopedRows("attendance").filter((row) => row.employeeId === employeeId);
    return {
      present: rows.filter((row) => ["P", "P+"].includes(row.dayCode)).length,
      absence: rows.filter((row) => row.dayCode === "ABS").length,
      guards: rows.filter((row) => ["G", "GV-J", "GV-N"].includes(row.dayCode)).length,
      leave: rows.filter((row) => ["C", "C.M"].includes(row.dayCode)).length,
    };
  }


  M.registerView('attendance', renderAttendance);
})();
