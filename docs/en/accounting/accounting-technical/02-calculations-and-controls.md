# 02 - Accounting Calculations and Controls

This document presents calculations and controls visible to accounting and financial direction.

## Cash Closing

```text
Difference = Real Amount - Virtual Amount
```

| Case | Meaning | Treatment |
| --- | --- | --- |
| Difference = 0 | No gap | Operation stored without alert. |
| Difference > 0 | Real amount higher than SOFTLAM | Positive value with remark. |
| Difference < 0 | Real amount lower than SOFTLAM | Negative value with remark. |

Controls:

- Remark required when a difference exists.
- Every difference appears in the Difference Statement.
- Differences are totaled by user and by month.

## Suppliers

```text
Remaining Balance = Order Total - Paid
```

| Status | Condition | Meaning |
| --- | --- | --- |
| Unpaid | Paid = 0 | No payment. |
| Partial | Paid > 0 and Remaining Balance > 0 | Partial payment. |
| Paid | Remaining Balance = 0 | Full payment. |

Controls:

- Payment Mode required when a payment exists.
- Observation stored when clarification is needed.
- Partial payment remains visible until the balance is settled.

## Subcontractors and Conventions

```text
Remaining Balance = Amount - Payment
```

Controls:

- Reception Date is stored.
- Payment Mode required when a payment exists.
- Remaining Balance visible in the relevant statement.

## Real Safe Net

```text
Real Safe Net =
  Cash CV
  + Cash C
  + Paid Additional Entries
  + Profitability Movement
  + Paid Subcontractors
  + Paid Convention
  - Safe Exits
```

Controls:

- Safe Exits decrease the safe.
- Additional Entries are included according to payment status.
- Every amount must remain traceable to its source screen.

## Monthly Balance

| Indicator | Meaning |
| --- | --- |
| Revenue | Monthly revenue. |
| Expenses | Total expenses. |
| Profitability | Result before investments. |
| Investments | Investments. |
| Net Profitability | Result after investments. |

```text
Profitability = Revenue - Expenses
```

```text
Net Profitability = Profitability - Investments
```

Controls:

- Percentages are not displayed if revenue is zero.
- Every balance amount must have an identifiable source.

## Attendance

| Code | Meaning |
| --- | --- |
| P | Present. |
| ABS | Absence. |
| G | Night Guard. |
| GV-J | Friday Day Guard. |
| GV-N | Friday Night Guard. |
| C | Leave. |
| C.M | Sick Leave. |
| REC | Recovery. |
| P+ | Extra Attendance / Overtime. |

Controls:

- Unknown codes are not counted.
- Each day must have a clear code or remain empty according to entry policy.

## Salaries

```text
Final Salary =
  Net Salary
  + Extra Attendance / Overtime
  + LAM Travel
  + Night Guard
  + Friday Day Guard
  + Friday Night Guard
  + Bonus
  - Absence
  - Penalties
  - Advances
```

Controls:

- Bonus, penalties, and advances can include a remark.
- Salary Report remains Draft before validation.
- After validation, status becomes Validated.
- After payment, status becomes Paid.

## Leave

```text
Leave Days = Leave days + 2.5 for each worked month
```

Controls:

- Hire Date is used to calculate the balance.
- Used Days decrease Acquired Days.
- Remaining Balance represents available leave.

## Encashment Statement

Controls:

- One row is generated for each day of the month.
- Default designation can be `DIVERS CLIENTS`.
- Monthly total appears at the bottom of the report.
- Official version contains stamp and signature.
