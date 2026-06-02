"use strict";

const STORE_KEY = "modernlam.prototype.v1";
const VIEW_KEY = "modernlam.prototype.activeView";
const REPORT_KEY = "modernlam.prototype.reportType";
const CASH_CLOSING_DATE_FILTER_KEY = "modernlam.prototype.cashClosing.date";
const CASH_CLOSING_USER_FILTER_KEY = "modernlam.prototype.cashClosing.user";
const SUPPLIER_FILTER_KEY = "modernlam.prototype.suppliers.search";
const SUPPLIER_CATEGORY_FILTER_KEY = "modernlam.prototype.suppliers.category";
const SUPPLIER_STATUS_FILTER_KEY = "modernlam.prototype.suppliers.status";
const PARTNER_TYPE_FILTER_KEY = "modernlam.prototype.partners.type";
const HR_TAB_KEY = "modernlam.prototype.hr.tab";
const HR_EMPLOYEE_KEY = "modernlam.prototype.hr.employee";
const HR_SEARCH_FILTER_KEY = "modernlam.prototype.hr.search";
const HR_FUNCTION_FILTER_KEY = "modernlam.prototype.hr.function";
const HR_STATUS_FILTER_KEY = "modernlam.prototype.hr.status";
const HR_CONTRACT_FILTER_KEY = "modernlam.prototype.hr.contract";

const labInfo = {
  name: "ModernLam - Laboratoire d'Analyses Medicales",
  nif: "NIF prototype",
  rip: "RIP prototype",
};

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
