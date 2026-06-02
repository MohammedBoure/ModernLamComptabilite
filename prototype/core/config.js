"use strict";

const STORE_KEY = "modernlam.prototype.v1";
const VIEW_KEY = "modernlam.prototype.activeView";
const REPORT_KEY = "modernlam.prototype.reportType";

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
