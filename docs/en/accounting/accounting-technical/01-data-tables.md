# 01 - Functional Tables and Stored Data

This document describes the tables visible or stored in the software from the accounting and administrative perspective. It is not the internal database model.

## Monthly Period

| Data | Description |
| --- | --- |
| Month | Accounting month concerned. |
| Year | Work year. |
| Month Status | Open, Under review, Closed. |
| Opening Date | Period creation date. |
| Closing Date | Closing date after validation. |

Purpose: attach all operations to a clear month and year.

## Cash Expenses

| Data | Description |
| --- | --- |
| Date | Expense date. |
| Designation | Reason or description. |
| Amount | Expense amount. |
| Remark | Additional information. |
| Document | Optional supporting document. |

Purpose: record cash exits.

## Cash Differences

| Data | Description |
| --- | --- |
| Date | Comparison day. |
| User | Person associated with the cash operation. |
| Real Amount | Physically present amount. |
| Virtual Amount | SOFTLAM or reference amount. |
| Difference | Calculated gap. |
| Net | Difference total by period or user. |
| Remarks | Difference justification. |

Purpose: control the gap between reality and SOFTLAM.

## Cash Movement

| Data | Description |
| --- | --- |
| Date | Movement day. |
| Cash CV | Cash CV amount. |
| Cash C | Cash C amount. |
| TPE | Electronic payments. |
| Expenses | Daily expenses. |
| Reimbursement | Refunded amounts. |
| Convention | Convention amounts. |
| Subcontractors | Subcontractor amounts. |
| Total | Daily total. |

Purpose: track cash by day and month.

## Additional Entries

| Data | Description |
| --- | --- |
| Date | Entry date. |
| Amount | Entry amount. |
| Detail | Source or reason. |
| Payment Status | Paid, unpaid, partial. |
| Remark | Additional information. |

Purpose: record entries not classified in primary cash.

## Safe Exits

| Data | Description |
| --- | --- |
| Date | Exit date. |
| Designation | Exit reason. |
| Amount | Amount taken out. |
| Category | Expense type. |
| Remark | Additional information. |

Purpose: record all exits from the safe.

## Monthly Balance

| Data | Description |
| --- | --- |
| Cash CV | Monthly Cash CV total. |
| Cash C | Monthly Cash C total. |
| Convention | Convention total. |
| Subcontracting | Subcontracting total. |
| Additional Entries | Additional entry total. |
| Revenue | Monthly revenue. |
| Expenses | Total expenses. |
| Profitability | Profitability before investments. |
| Investments | Investment total. |
| Net Profitability | Profitability after investments. |
| Real Safe Net | Real safe balance. |

Purpose: present the monthly result.

## Suppliers

| Data | Description |
| --- | --- |
| Supplier | Supplier name. |
| Category | Reagents, consumables, taxes, salaries, etc. |
| Date | Operation date. |
| Order Total | Order or invoice amount. |
| Paid | Paid amount. |
| Remaining Balance | Unpaid balance. |
| Status | Paid, Partial, Unpaid. |
| Observation | Additional note. |

Purpose: track supplier debt and payments.

## Payments

| Data | Description |
| --- | --- |
| Payment Date | Payment date. |
| Target Party | Supplier, subcontractor, or convention. |
| Amount | Payment amount. |
| Payment Mode | Cash, cheque, transfer, or other. |
| Reference | Cheque number or operation reference. |
| Remark | Additional information. |

Purpose: store partial or full payments.

## Subcontractors

| Data | Description |
| --- | --- |
| Subcontractor | Subcontractor name. |
| Amount | File amount. |
| Payment | Paid amount. |
| Reception Date | Reception date. |
| Payment Mode | Payment mode. |
| Remaining Balance | Amount still unpaid. |
| Remarks | Notes. |

Purpose: track external partners.

## Conventions

| Data | Description |
| --- | --- |
| Convention | Convention name. |
| Amount | File amount. |
| Payment | Paid amount. |
| Reception Date | Reception date. |
| Payment Mode | Payment mode. |
| Remaining Balance | Amount still unpaid. |
| Remarks | Notes. |

Purpose: track conventions and their payments.

## Attendance

| Data | Description |
| --- | --- |
| Employee | Employee name. |
| Month | Attendance month. |
| Day | Day of month. |
| Code | P, ABS, G, GV-J, GV-N, C, C.M, REC, P+. |
| Remark | Additional note. |

Purpose: store attendance and feed salaries.

## Salary Report

| Data | Description |
| --- | --- |
| Employee | Employee name. |
| Position | Function. |
| Net Salary | Base net salary. |
| Extra Attendance / Overtime | Extra attendance or overtime. |
| LAM Travel | Travel allowance. |
| Guards | Night guard and Friday guard. |
| Absence | Absence deduction. |
| Bonus | Bonus. |
| Penalties | Deductions or penalties. |
| Advances | Salary advances. |
| Final Salary | Final salary. |
| Remark | Note. |

Purpose: calculate and verify monthly salaries.

## Employees

| Data | Description |
| --- | --- |
| Full Name | Employee identity. |
| Function | Position held. |
| Birth Date | Date of birth. |
| Age | Calculated age. |
| Birth Place | Place of birth. |
| Address | Address. |
| Phone 01/02 | Phone numbers. |
| Social Security Number | Social security number. |
| ANEM Number | ANEM number. |

Purpose: store the employee administrative profile.

## Contracts

| Data | Description |
| --- | --- |
| Employee | Employee linked to the contract. |
| Hire Date | Hiring date. |
| CNAS Registration Date | CNAS date. |
| Contract | Contract type. |
| From | Start date. |
| To | End date. |
| Resignation | Exit date if any. |

Purpose: track employee contractual status.

## Leave

| Data | Description |
| --- | --- |
| Employee | Employee name. |
| Year | Leave year. |
| Hire Date | Hiring date. |
| Acquired Days | Acquired days. |
| Used Days | Consumed days. |
| Remaining Balance | Available balance. |
| Remark | Note. |

Purpose: track yearly leave balance.

## Service Vehicle

| Data | Description |
| --- | --- |
| Date | Operation date. |
| Amount | Expense amount. |
| Details | Details. |
| Mileage | Mileage. |
| GPL / Extra Kilometre | GPL data. |
| Essence / Extra Kilometre | Essence data. |

Purpose: track service vehicle expenses.

## Cheque Statement / SGA Account

| Data | Description |
| --- | --- |
| Date | Operation date. |
| Beneficiary | Beneficiary. |
| Cheque Number | Cheque number. |
| Amount | Amount. |
| Entries | Entries. |
| Exits | Exits. |
| Designation | Reason. |
| Month | Associated month. |

Purpose: track cheques and SGA account.

## Encashment Statement

| Data | Description |
| --- | --- |
| Day | Day number. |
| Date | Date of the day. |
| Designation | Often DIVERS CLIENTS. |
| Observations | Notes. |
| Amounts | Daily amount. |
| Total | Monthly total. |

Purpose: produce the monthly encashment report.
