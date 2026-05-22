# 08 - Modele de Donnees

هذا الملف يقترح نموذج بيانات أولي. الأسماء هنا ليست نهائية، لكنها تساعد على تحويل التقرير إلى قاعدة بيانات منظمة.

## مبادئ عامة

- كل جدول مالي يحتوي على `month`, `year`, `status`.
- كل سجل مهم يحتوي على `created_at`, `created_by`, `updated_at`, `updated_by`.
- الحذف المالي لا يكون حذف نهائي، بل `cancelled_at`, `cancelled_by`, `cancel_reason`.
- المدفوعات الجزئية تخزن في جدول payments مستقل.

## tables principales

### users

- id
- username
- full_name
- role
- password_hash
- is_active
- last_login_at

### accounting_periods

- id
- month
- year
- status
- opened_at
- opened_by
- closed_at
- closed_by
- close_note

### cash_expenses

- id
- period_id
- date
- designation
- amount
- remark
- attachment_id
- status

### cash_closures

- id
- period_id
- date
- user_id
- real_amount
- virtual_amount
- difference
- net
- remark
- status

### cash_movements

- id
- period_id
- date
- caisse_cv
- caisse_c
- tpe
- expenses
- reimbursement
- convention
- subcontractors
- total
- remark

### coffer_movements

- id
- period_id
- date
- type
- designation
- amount
- category
- remark

`type` يمكن أن يكون:

- entree
- sortie
- profitabilite
- correction

### additional_entries

- id
- period_id
- date
- amount
- detail
- payment_status
- remark

### profitability_movements

- id
- period_id
- date
- amount
- detail
- source_period_id
- destination_period_id
- movement_type

### monthly_balances

- id
- period_id
- caisse_cv_total
- caisse_c_total
- convention_total
- subcontracting_total
- additional_entries_total
- revenue_total
- expenses_total
- profitability
- investments_total
- net_profitability
- coffer_net_real
- calculated_at

## Fournisseurs

### suppliers

- id
- name
- category
- phone
- address
- notes
- is_active

### supplier_transactions

- id
- period_id
- supplier_id
- category
- date
- order_total
- paid_amount
- remaining_amount
- status
- observation

### payments

- id
- period_id
- target_type
- target_id
- date
- amount
- payment_mode
- reference
- note

`target_type` أمثلة:

- supplier_transaction
- subcontractor_transaction
- convention_transaction
- salary_report

## Sous-Traitants et Conventions

### subcontractors

- id
- name
- phone
- address
- notes
- is_active

### subcontractor_transactions

- id
- period_id
- subcontractor_id
- date
- amount
- received_at
- payment_mode
- paid_amount
- remaining_amount
- remarks
- status

### conventions

- id
- name
- contact
- phone
- notes
- is_active

### convention_transactions

- id
- period_id
- convention_id
- date
- amount
- received_at
- payment_mode
- paid_amount
- remaining_amount
- remarks
- status

## RH

### employees

- id
- full_name
- function
- birth_date
- birth_place
- address
- phone_01
- phone_02
- social_security_number
- anem_number
- status
- notes

### employee_contracts

- id
- employee_id
- hire_date
- cnas_registration_date
- contract_type
- starts_at
- ends_at
- resignation_date
- status
- notes

### employee_attendance

- id
- period_id
- employee_id
- date
- day_code
- garde_code
- is_considered
- note

### salary_reports

- id
- period_id
- employee_id
- base_net_salary
- overtime_presence
- deplacement_lam
- garde_nuit
- garde_vendredi_jour
- garde_vendredi_nuit
- absence
- prime
- conge
- penalites
- avances
- final_salary
- status
- remark

### leave_balances

- id
- employee_id
- year
- acquired_days
- used_days
- remaining_days
- calculated_at
- remark

## Etats

### vehicle_expenses

- id
- period_id
- date
- amount
- details
- mileage
- gpl_km_plus
- essence_km_plus
- remark

### cheques

- id
- year
- date
- beneficiary
- cheque_number
- amount
- entries
- exits
- designation
- month
- status

### encashments

- id
- period_id
- date
- designation
- observations
- amount
- printed_at
- printed_by

## Administration

### attachments

- id
- file_name
- file_path
- mime_type
- size
- uploaded_by
- uploaded_at

### audit_logs

- id
- user_id
- action
- entity_type
- entity_id
- old_values
- new_values
- reason
- created_at

## علاقات مهمة

- employee له عدة contracts، لكن عقد واحد actif.
- supplier_transaction يمكن أن يكون له عدة payments.
- subcontractor_transaction يمكن أن يكون له عدة payments.
- convention_transaction يمكن أن يكون له عدة payments.
- accounting_period يرتبط بكل العمليات الشهرية.
- monthly_balances يحسب من العمليات ولا يكون مصدر الإدخال الأساسي.

## قيود مطلوبة

- لا يسمح بتكرار cheque_number لنفس السنة إذا كان مستخدما.
- لا يسمح بتعديل سجل مالي في period مغلق بدون صلاحية.
- لا يسمح بمبلغ سلبي إلا في عمليات correction المحددة.
- لا يسمح بتاريخ خارج period المختار.
