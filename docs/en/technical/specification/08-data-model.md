# 08 - Data Model

This model is an initial proposal. Names can evolve during implementation.

## Principles

- Every financial table is attached to a period.
- Important records contain creation and update metadata.
- Financial deletions are traced.
- Partial payments are managed in a payments table.

## Main Tables

### users

- id.
- username.
- full_name.
- role.
- password_hash.
- is_active.
- last_login_at.

### accounting_periods

- id.
- month.
- year.
- status.
- opened_at.
- opened_by.
- closed_at.
- closed_by.
- close_note.

### cash_expenses

- id.
- period_id.
- date.
- designation.
- amount.
- remark.
- attachment_id.
- status.

### cash_closures

- id.
- period_id.
- date.
- user_id.
- real_amount.
- virtual_amount.
- difference.
- net.
- remark.
- status.

### cash_movements

- id.
- period_id.
- date.
- cash_cv.
- cash_c.
- tpe.
- expenses.
- reimbursement.
- convention.
- subcontractors.
- total.
- remark.

### coffer_movements

- id.
- period_id.
- date.
- type.
- designation.
- amount.
- category.
- remark.

### additional_entries

- id.
- period_id.
- date.
- amount.
- detail.
- payment_status.
- remark.

### profitability_movements

- id.
- period_id.
- date.
- amount.
- detail.
- source_period_id.
- destination_period_id.
- movement_type.

### monthly_balances

- id.
- period_id.
- cash_cv_total.
- cash_c_total.
- convention_total.
- subcontracting_total.
- additional_entries_total.
- revenue_total.
- expenses_total.
- profitability.
- investments_total.
- net_profitability.
- real_safe_net.
- calculated_at.

## Suppliers and Payments

### suppliers

- id.
- name.
- category.
- phone.
- address.
- notes.
- is_active.

### supplier_transactions

- id.
- period_id.
- supplier_id.
- category.
- date.
- order_total.
- paid_amount.
- remaining_amount.
- status.
- observation.

### payments

- id.
- period_id.
- target_type.
- target_id.
- date.
- amount.
- payment_mode.
- reference.
- note.

## HR

### employees

- id.
- full_name.
- function.
- birth_date.
- birth_place.
- address.
- phone_01.
- phone_02.
- social_security_number.
- anem_number.
- status.

### employee_contracts

- id.
- employee_id.
- hire_date.
- cnas_registration_date.
- contract_type.
- starts_at.
- ends_at.
- resignation_date.
- status.

### employee_attendance

- id.
- period_id.
- employee_id.
- date.
- day_code.
- guard_code.
- is_considered.
- note.

### salary_reports

- id.
- period_id.
- employee_id.
- base_net_salary.
- overtime_presence.
- lam_travel.
- night_guard.
- friday_day_guard.
- friday_night_guard.
- absence.
- bonus.
- leave.
- penalties.
- advances.
- final_salary.
- status.

### leave_balances

- id.
- employee_id.
- year.
- acquired_days.
- used_days.
- remaining_days.

## Reports

- vehicle_expenses.
- cheques.
- encashments.
- attachments.
- audit_logs.

## Relations

- One employee can have multiple contracts, but only one active contract.
- One supplier transaction can have multiple payments.
- One period groups all monthly operations.
- monthly_balances is calculated from source operations.
