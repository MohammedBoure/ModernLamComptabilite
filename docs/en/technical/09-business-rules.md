# 09 - Business Rules and Calculations

## Cash

```text
Difference = Real Amount - Virtual Amount
Net = Sum(Difference)
```

Rules:

- Remark required if Difference is not zero.
- Differences grouped by user and month.
- Differences do not automatically become profit or loss without a decision.

## Suppliers

```text
Remaining Balance = Order Total - Paid
```

Statuses:

- Paid if Remaining Balance = 0.
- Partial if Paid > 0 and Remaining Balance > 0.
- Unpaid if Paid = 0.

## Subcontractors and Conventions

```text
Remaining Balance = Amount - Payment
```

Payment Mode required if Payment exists.

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

## Revenue

```text
Global Revenue =
  Real Safe Net
  + LAM Revenue
  + Convention Revenue
  + Subcontractor Revenue
  + Additional Entry Revenue
```

Point to confirm:

```text
LAM Revenue = Cash C + Cash C + Expenses
```

This formula appears to repeat `Cash C`.

## Profitability

```text
Profitability = Revenue - Expenses
Net Profitability = Profitability - Investments
```

Ratios are not displayed when Revenue = 0.

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

The final formula must be functionally validated.

## Leave

```text
Leave Days = Leave days + 2.5 per worked month
```

The rule related to day 15 must be confirmed before implementation.

## Monthly Closing

Blocking cases:

- Unjustified differences.
- Draft salaries.
- Balance not calculated.
- Draft financial operations.
