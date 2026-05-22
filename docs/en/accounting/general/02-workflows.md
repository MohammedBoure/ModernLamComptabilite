# 02 - Functional Workflows

## Opening a New Month

| Step | Description |
| --- | --- |
| Period selection | Select month and year. |
| Period creation | Create the month if the period does not exist. |
| List loading | Display active employees, suppliers, and known partners. |
| Month status | The month starts with `Open` status. |

## Daily Cash Work

| Step | Description |
| --- | --- |
| Expense entry | Enter date, designation, and amount. |
| Real amount entry | Record the physical cash amount. |
| SOFTLAM amount entry | Record the Virtual Amount from SOFTLAM. |
| Difference calculation | Automatically calculate Difference. |
| Justification | A remark is required when a difference exists. |

```text
Difference = Real Amount - Virtual Amount
```

## Cash and Safe Tracking

| Step | Description |
| --- | --- |
| Daily movement entry | Cash CV, Cash C, TPE, expenses, reimbursement, convention, subcontractors. |
| Daily total calculation | Automatic daily total calculation. |
| Monthly update | Update total, min, max, average. |
| Safe update | Entries and exits affect the Real Safe Net. |

## Supplier Tracking

| Step | Description |
| --- | --- |
| Supplier registration | Select or create the supplier. |
| Invoice/order entry | Enter category, amount, and details. |
| Payment entry | Enter payment amount and payment mode. |
| Remaining balance calculation | Automatically calculate remaining balance. |
| Status | Paid, Partial, or Unpaid. |

```text
Remaining Balance = Amount - Payment
```

## Subcontractors and Conventions

| Step | Description |
| --- | --- |
| Operation entry | Identify subcontractor or convention. |
| Amount entry | Enter file or operation amount. |
| Payment entry | Enter payment and payment mode. |
| Remaining balance calculation | Automatically calculate remaining balance. |
| Report | Display in Subcontractor Statement or Convention Statement. |

## Attendance

| Step | Description |
| --- | --- |
| Month selection | Display days and active employees. |
| Code entry | Use P, ABS, G, GV-J, GV-N, C, C.M, REC, P+. |
| Totals calculation | Total attendance, absence, leave, and guards. |
| Salary link | Totals feed the Salary Report. |

## Salaries

| Step | Description |
| --- | --- |
| Attendance retrieval | Read monthly attendance results. |
| Manual values | Bonuses, penalties, and advances. |
| Salary calculation | Calculate final salary according to validated rules. |
| Validation | The report remains Draft before validation. |
| Payment | After payment, the status becomes Paid. |

## Monthly Closing

Conditions:

- No unjustified cash differences.
- Supplier and partner data complete.
- Salary report finalized.
- Monthly balance calculated.
- Main reports verified.

Result:

- The month becomes `Closed`.
- Ordinary modifications are blocked.
- Reports remain available for printing and archiving.
