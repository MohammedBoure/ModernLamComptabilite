# 07 - Functional Workflows

## New Month

Inputs:

- Month.
- Year.
- Responsible user.

Processing:

1. Period selection.
2. Creation if missing.
3. Active employee and supplier loading.
4. Status `Open`.

Outputs:

- Open period.
- Active entry for cash, safe, attendance, suppliers.

## Daily Cash

Inputs:

- Date.
- Cash expenses.
- Real Amount.
- Virtual Amount.
- Remark if gap exists.

Processing:

1. Expense recording.
2. Amount entry.
3. Difference calculation.
4. Mandatory remark if difference exists.

Outputs:

- Cash closing.
- Updated Difference Statement.
- Dashboard alerts.

## Suppliers

Inputs:

- Supplier.
- Invoice or order.
- Amount.
- Payment.
- Payment mode.

Processing:

1. Supplier attachment.
2. Amount recording.
3. Payment recording.
4. Remaining balance calculation.
5. Unpaid, Partial, or Paid status.

## Attendance and Salaries

Processing:

1. Attendance code entry.
2. Total calculation.
3. Salary Report generation.
4. Bonus, penalties, and advances addition.
5. Final salary calculation.
6. Validation then payment.

## Monthly Closing

Conditions:

- Justified differences.
- Generated reports.
- No Draft salaries.
- Visible remaining balances.
- Calculated balance.

Processing:

1. Closing checklist.
2. Automatic verification.
3. Validation by authorized role.
4. Switch to `Closed`.
5. Ordinary modifications blocked.

## Closed Month Modification

- Exceptional modification request.
- Mandatory reason.
- Administrator validation.
- Limited modification.
- Mandatory audit log.
- Balance recalculation.
- New closing.
