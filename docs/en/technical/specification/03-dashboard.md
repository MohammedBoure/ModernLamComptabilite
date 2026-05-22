# 03 - Dashboard

## Objective

The Dashboard gives a quick monthly view: cash, safe, revenue, profitability, remaining balances, and alerts.

## Components

### Period

| Field | Description |
| --- | --- |
| Month | Displayed month. |
| Year | Displayed year. |
| Status | Open, Under review, Closed. |
| Last update | Last calculation. |

### Summary Cards

- Cash CV.
- Cash C.
- TPE.
- Expenses.
- Real Safe Net.
- Global Revenue.
- Profitability.
- Net Profitability.

### Alerts

- Unjustified cash difference.
- Supplier with remaining balance.
- Subcontractor or convention not settled.
- Salary not validated.
- Employee without active contract.
- Incomplete cheque.

## Rules

- Values are calculated from source screens.
- A card opens its source detail.
- Division-by-zero errors are shown as unavailable.
- A closed month displays read-only data.
