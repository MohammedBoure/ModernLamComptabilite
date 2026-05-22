# 06 - HR Interfaces

## Employee List

Columns:

- Number.
- Full Name.
- Function.
- Birth Date.
- Age.
- Phone 01.
- Phone 02.
- Status.
- Active contract.
- Year leave.

Filters:

- Function.
- Status.
- Contract.
- Search by name.

## Employee File

Tabs:

| Tab | Content |
| --- | --- |
| Identity | Personal data. |
| Contract | Hiring, CNAS, contract. |
| Leave | Annual balance. |
| Attendance | Attendance by month. |
| Salaries | Salary history. |
| Documents | Attachments. |
| History | Modifications. |

## Identity

Fields:

- Full Name.
- Function.
- Birth Date.
- Calculated Age.
- Birth Place.
- Address.
- Phone 01.
- Phone 02.
- Social Security Number.
- ANEM Number.

## Contract

Fields:

- Hire Date.
- CNAS Registration Date.
- Contract.
- From.
- To.
- Resignation.
- Contract Status.
- Remark.

Rules:

- `To` cannot be before `From`.
- One active contract per employee.
- Resignation makes employee inactive starting from the indicated date.

## Leave

Fields:

- Year.
- Employee.
- Function.
- Hire Date.
- Acquired Days.
- Used Days.
- Remaining Balance.

Base rule:

```text
Leave Days = Leave days + 2.5 per worked month
```
