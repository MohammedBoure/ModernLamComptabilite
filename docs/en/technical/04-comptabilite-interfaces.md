# 04 - Accounting Interfaces

## 04.1 Cash Closing

Objective: record cash expenses and calculate the difference between Real Amount and Virtual Amount.

Tabs:

| Tab | Content |
| --- | --- |
| Cash Expenses | Date, designation, amount, remark. |
| Differences | Date, user, Real Amount, Virtual Amount, Difference, Net, Remarks. |
| Difference Statement | Difference summary by user. |

Rules:

```text
Difference = Real Amount - Virtual Amount
Net = Sum(Difference)
```

Remark required if Difference is not zero.

## 04.2 Cash & Safe

### Cash Movement

Columns:

- Date.
- Cash CV.
- Cash C.
- TPE.
- Expenses.
- Reimbursement.
- Convention.
- Subcontractors.
- Total.

Calculation rows:

- Total.
- Min (-Fri).
- Max (-Fri).
- Average (-Fri).

### Additional Entries

Columns:

- Date.
- Amount.
- Detail.
- Payment Status.
- Remark.

### Safe Exits

Columns:

- Date.
- Designation.
- Amount.
- Category.
- Attachment.
- Remark.

### Safe Summary

- Real Safe Net.
- LAM Revenue.
- Convention Revenue.
- Subcontractor Revenue.
- Additional Entry Revenue.
- Global Revenue.

## 04.3 Monthly Balance

Sections:

| Section | Fields |
| --- | --- |
| Monthly result | Cash CV, Cash C, Convention, Subcontracting, Additional Entries. |
| Withdrawals | Total Withdraw CV, Total Withdraw C, Total Withdraw S/T, Total Withdraw. |
| Profitability | Revenue, Expenses, Profitability. |
| Investments | Investments, Net Profitability. |

The screen is mainly calculated and read-only.

## 04.4 Suppliers

Categories:

- Reagents & Consumables.
- Subcontracting.
- Taxes.
- IT & Office.
- Service Vehicle.
- Rent.
- Lab Energy.
- Internal Expenses.
- Salaries.
- Subcontractor Transport.
- Other Expenses.
- Investment.

Columns:

- Number.
- Category.
- Supplier LAM.
- Order Total.
- Paid.
- Remaining Balance.
- Date.
- Observation.

```text
Remaining Balance = Order Total - Paid
```

## 04.5 Subcontractors & Conventions

Columns:

- Name.
- Amount.
- Payment.
- Reception Date.
- Payment Mode.
- Remaining Balance.
- Remarks.

```text
Remaining Balance = Amount - Payment
```

## 04.6 Attendance

Codes:

| Code | Meaning |
| --- | --- |
| P | Present. |
| G | Night Guard. |
| ABS | Absence. |
| REC | Recovery. |
| GV-J | Friday Day Guard. |
| GV-N | Friday Night Guard. |
| P+ | Extra Attendance / Overtime. |
| C.M | Sick Leave. |
| C | Leave. |

## 04.7 Salary Report

Columns:

- Person.
- Position.
- Net Salary.
- Extra Attendance / Overtime.
- LAM Travel.
- Night Guard.
- Friday Day Guard.
- Friday Night Guard.
- Absence.
- Bonus.
- Leave.
- Penalties.
- Advances.
- Salary.
- Remark.
