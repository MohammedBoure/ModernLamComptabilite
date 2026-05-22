# English Documentation - ModernLam Accounting Software

This documentation presents ModernLam Accounting Software in English. It is organized into two main parts: management documentation for accounting, direction, and human resources, and technical documentation for design and implementation.

## Reference Report

| Type | File | Notes |
| --- | --- | --- |
| Main report | [Rapport Logiciel Comptabilite PDF](<../../Rapport Logiciel Comptabilité_720ec9a3-2c6d-4f36-87b8-5ecbc04ea00e.pdf>) | Initial source for tables, modules, calculations, and remarks. |

## Sections

| Section | Link | Audience | Content |
| --- | --- | --- | --- |
| Accounting and administrative documentation | [accounting/README.md](./accounting/README.md) | Accounting, direction, HR | General documentation, accountant-readable technical accounting documentation, UI organization. |
| Technical documentation | [technical/README.md](./technical/README.md) | Design, development, maintenance | Detailed interfaces, data model, rules, permissions, printing, implementation plan. |

## Reference Reading Order

| Order | Section | Purpose |
| --- | --- | --- |
| 1 | [accounting/general/README.md](./accounting/general/README.md) | Understand the software from the business perspective. |
| 2 | [accounting/accounting-technical/README.md](./accounting/accounting-technical/README.md) | Understand stored data, calculations, and accounting controls. |
| 3 | [accounting/ui/README.md](./accounting/ui/README.md) | Understand screen layout and interface organization. |
| 4 | [technical/README.md](./technical/README.md) | Access technical specifications. |
| 5 | [technical/08-data-model.md](./technical/08-data-model.md) | Review the internal data model. |

## Documentation Maintenance Rules

- Any change to a calculation rule must be reflected in the technical documentation and, when it affects business interpretation, in the accounting documentation.
- Any screen change must be reflected in the UI documentation and, when necessary, in the technical specifications.
- Any new administrative decision must be reflected in the rules or in the open questions.
