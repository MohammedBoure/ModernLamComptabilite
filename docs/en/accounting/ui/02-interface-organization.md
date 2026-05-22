# 02 - Interface Element Organization

This document describes the functional organization of screens. It does not define the final visual design.

## General Structure

Each screen contains stable zones:

| Zone | Location | Content |
| --- | --- | --- |
| Top bar | Top of screen | Software name, month, year, month status, current user. |
| Side menu | Side of screen | Dashboard, Cash, Safe, Suppliers, Reports, HR. |
| Filter bar | Top of content | Month, year, status, search, report type. |
| Work area | Center | Main table or form. |
| Action bar | Top or bottom of work area | New, Save, Print, Export, History. |
| Totals area | Bottom of financial tables | Total, Remaining Balance, Difference, Profitability according to screen. |

## Top Bar

Content:

- ModernLam name or software name.
- Selected month and year.
- Status: Open, Under review, Closed.
- Current user.
- Logout.

Purpose:

- Identify the current period.
- Avoid confusion between months.
- Show whether the month is editable or closed.

## Side Menu

| Element | Screen |
| --- | --- |
| Dashboard | Monthly summary and alerts. |
| Cash Closing | Cash expenses and differences. |
| Cash & Safe | Cash and safe movements. |
| Suppliers | Suppliers, payments, remaining balances. |
| Subcontractors | Subcontractors and conventions. |
| Attendance | Monthly attendance. |
| Salaries | Salary report. |
| Reports | Reports and printing. |
| HR | Employees, contracts, leave. |

## Filter Bar

Common elements:

- Month.
- Year.
- Status.
- Search.
- Category.
- Supplier or employee depending on context.

Rules:

- Financial and administrative screens always display the period.
- Filters change the view, not the data.
- Period changes reload data.

## Tables

Each financial or administrative table contains:

- Column header.
- Data rows.
- Remarks column when needed.
- Total row when amounts exist.
- Status when needed: Paid, Partial, Unpaid, Draft, Validated.

Rules:

- Amounts are displayed in separate columns.
- Remaining Balance is displayed near Paid Amount.
- Differences are visible in the Differences screen.
- Closed months are displayed as read-only.

## Forms

A form is used to add or edit a record.

Elements:

- Input fields.
- Remarks.
- Attachments when needed.
- Save and Cancel buttons.
- Control message when a required field is missing.

Examples:

- Add cash expense.
- Add supplier.
- Add payment.
- Add employee.
- Add contract.

## Action Bar

| Button | Function |
| --- | --- |
| New | Create a record. |
| Save | Save modifications. |
| Cancel | Cancel entry. |
| Delete | Delete or cancel according to authorization. |
| Print | Print screen or report. |
| Export PDF | PDF export. |
| Export Excel | Excel export. |
| History | Show modifications. |

## Dashboard

| Zone | Content |
| --- | --- |
| Summary cards | Cash, Safe, Revenue, Profitability. |
| Alerts | Differences, remaining balances, unvalidated salaries, unclosed month. |
| Shortcuts | Cash Closing, Suppliers, Attendance, Reports. |
| Month summary | Month status and last update. |

## Cash Closing

Zones:

1. Month/year filter.
2. Cash Expenses tab.
3. Differences tab.
4. Difference Statement tab.
5. Expense and difference totals.

## Cash & Safe

Zones:

1. Cash Movement table.
2. Additional Entries table.
3. Safe Exits table.
4. Profitability Movement table.
5. Real Safe Net and Revenue summary.

## Suppliers

Zones:

1. Supplier or category list.
2. Operations/invoices table.
3. Payments table.
4. Total, Paid, Remaining Balance summary.
5. Supplier details.

## Attendance

Zones:

1. Month and year.
2. Employee table.
3. Day columns.
4. Attendance codes.
5. Employee or month totals.

## Salaries

Zones:

1. Month and year.
2. Employee/salary table.
3. Addition columns.
4. Deduction columns.
5. Final Salary.
6. Status: Draft, Validated, Paid.

## Reports

Zones:

1. Report type.
2. Period.
3. Preview.
4. PDF, Excel, Print actions.
5. Official version history when needed.

## HR

Zones:

1. Employee list.
2. Employee file.
3. Tabs: Identity, Contract, Leave, Attendance, Salaries, Documents.
4. Contract and leave alerts.

## Interface States

| State | Behavior |
| --- | --- |
| Loading | Loading indicator. |
| Empty | No-data message. |
| Read-only | Modification buttons disabled for closed month. |
| Error | Clear message without technical terms. |
| Saved | Save confirmation. |

## Printing and Preview

Before printing:

- Report preview.
- Title and period.
- Totals.
- Type: Draft or Official.

After official validation:

- Export or printing is recorded in history.
