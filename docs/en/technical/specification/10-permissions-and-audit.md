# 10 - Permissions, Security, and Audit

## Roles

| Role | Description |
| --- | --- |
| Admin | Full permissions. |
| Direction | Consultation and validation according to scope. |
| Accountant | Accounting operations. |
| Cash Desk | Cash closing and differences. |
| HR | Employees, attendance, contracts, salaries. |
| Viewer | Read-only. |

## Simplified Matrix

| Screen | Admin | Direction | Accountant | Cash Desk | HR | Viewer |
| --- | --- | --- | --- | --- | --- | --- |
| Dashboard | Full | Read | Read | Limited | Limited | Read |
| Cash Closing | Full | Read | Full | Entry | No | Read |
| Cash & Safe | Full | Read | Full | Limited | No | Read |
| Suppliers | Full | Read | Full | No | No | Read |
| Attendance | Full | Read | Read | No | Full | Read |
| Salaries | Full | Read | Review | No | Full | Limited |
| Reports | Full | Full | Full | Limited | Limited | Read |
| HR | Full | Read | No | No | Full | Limited |
| Administration | Full | No | No | No | No | No |

## Audit Log

Traced operations:

- Financial creation, modification, cancellation.
- Amount modification.
- Salary validation.
- Monthly closing.
- Reopening a closed month.
- Employee or contract modification.
- Permission change.

Fields:

- user_id.
- action.
- entity_type.
- entity_id.
- old_values.
- new_values.
- reason.
- created_at.

## Closed Month

- Read-only by default.
- Printing and export allowed.
- Exceptional modification with Admin role.
- Mandatory reason.
- Balance recalculation after correction.
