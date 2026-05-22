# 08 - Modele de Donnees

Ce modele est une proposition initiale. Les noms peuvent evoluer lors de l'implementation.

## Principes

- Toute table financiere est rattachee a une periode.
- Les enregistrements importants contiennent creation et mise a jour.
- Les suppressions financieres sont tracees.
- Les paiements partiels sont geres dans une table payments.

## Tables principales

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
- caisse_cv.
- caisse_c.
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
- caisse_cv_total.
- caisse_c_total.
- convention_total.
- subcontracting_total.
- additional_entries_total.
- revenue_total.
- expenses_total.
- profitability.
- investments_total.
- net_profitability.
- coffer_net_real.
- calculated_at.

## Fournisseurs et paiements

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

## RH

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
- garde_code.
- is_considered.
- note.

### salary_reports

- id.
- period_id.
- employee_id.
- base_net_salary.
- overtime_presence.
- deplacement_lam.
- garde_nuit.
- garde_vendredi_jour.
- garde_vendredi_nuit.
- absence.
- prime.
- conge.
- penalites.
- avances.
- final_salary.
- status.

### leave_balances

- id.
- employee_id.
- year.
- acquired_days.
- used_days.
- remaining_days.

## Etats

- vehicle_expenses.
- cheques.
- encashments.
- attachments.
- audit_logs.

## Relations

- Un employe peut avoir plusieurs contrats, mais un seul contrat actif.
- Une transaction fournisseur peut avoir plusieurs paiements.
- Une periode regroupe toutes les operations du mois.
- monthly_balances est calcule depuis les operations sources.
