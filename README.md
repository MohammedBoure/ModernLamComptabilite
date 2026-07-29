# ModernLam - FINANCELAM

**FINANCELAM** is a comprehensive desktop financial management, accounting, HR, and governance system custom-built for **ModernLam - Laboratoire d'Analyses Médicales**.

The application is built in Python (PySide6 GUI) with a MySQL/MariaDB relational database backend. It transitions complex spreadsheet-based medical laboratory management into an enterprise-grade desktop system with full auditability, financial closing, role-based security, and automated reporting.

---

## 🌟 Key Features & Modules

- **HR & Payroll Management**: Employee records, contract tracking, daily attendance, night & Friday shifts, CNAS registration, monthly payslip generation, and leave balance ledger.
- **Daily Cash Register (Caisse)**: Daily counter collections (cash, TPE, convention fees, subcontractor fees), expense recording, and digital daily closing validation (`Cloture_Caisse`).
- **Safe Box Operations (Coffre)**: Master safe transactions categorized into revenues (LAM counter, conventions, subcontractors, supplementary inputs) and expenses.
- **Partner Relations (Subcontractors & Conventions)**: Invoicing, delivery slips, payment tracking, and balance statements for clinical partners and external laboratories.
- **Supplier & Purchase Management**: Supplier catalog, expense categorization (equipment vs. consumables), purchase order/invoice tracking, and supplier statement reports.
- **Logistics & Waste Management**: Service vehicle fuel and mileage tracking (GPL/Essence), and medical waste incineration station weight & cost logging.
- **Banking & Encashment**: SGA bank account statement tracking, cheque payments, initial annual balances, and encashment vouchers (`Etat_Encaissement`).
- **Governance & Audit Trail**: Period-based accounting lock (`Accounting_Periods`), period reopening workflows, role-based access control (RBAC), and immutable audit logs (`Audit_Events`).
- **Financial Analytics & Reporting**: Real-time monthly revenue breakdown, net profitability percentage calculation, and exportable official PDF/XLSX reports.

---

## 📁 Repository Structure

```text
FINANCELAM/
├── docs/                   # Business and technical documentation (AR, FR, EN)
├── excel/                  # Spreadsheet reference templates and legacy sheets
├── src/                    # System source code
│   ├── main.py             # PySide6 application entry point
│   ├── database/           # Database managers, connections, and migrations
│   │   ├── base/           # Schema creation, MySQL connector, migrations engine
│   │   └── *_manager.py    # Domain-specific repository services (HR, Caisse, Governance, etc.)
│   ├── services/           # Business logic, calculation policies, PDF & Excel report engines
│   ├── ui/                 # PySide6 UI views and modular navigation components
│   └── utils/              # Application utilities, logging, and helper functions
├── tests/                  # Automated test suites
├── pdf_settings.json       # PDF report styling configuration
├── requirements.txt        # Python package dependencies
├── VERSION                 # Current release version tag
└── README.md               # Project & Database Architecture Documentation
```

---

## 📊 Database Architecture & Data Structure (Schema)

The underlying MySQL database consists of **37 tables** and **6 analytical views** grouped into logical domain modules.

### 1. HR & Payroll Module

| Table Name | Description | Key Fields & Types |
| :--- | :--- | :--- |
| `Employes` | Employee Master Records | `id_employe` (PK, INT), `nom_prenom` (VARCHAR 255), `fonction` (VARCHAR 100), `salaire_base` (DECIMAL 15,2), `date_naissance`, `lieu_naissance`, `adresse`, `tel_1`, `tel_2`, `nss` (CNAS No), `n_anem`, `date_embauche`, `date_inscription_cnas`, `date_demission`, `nin`, `type_contrat`, `heures_travail_jour` |
| `Presences` | Daily Attendance Log | `id_presence` (PK, INT), `id_employe` (FK), `date_presence` (DATE), `etat_jour` (ENUM: PRESENT, RECUPERATION, GARDE_NUIT, GARDE_VENDREDI_JOUR, GARDE_VENDREDI_NUIT, ABSENCE, CONGE_MALADIE, CONGE, NON_CONSIDERE), `heures_sup` (DECIMAL 5,2), `heure_entree` (TIME), `heure_sortie` (TIME), `period_id` (FK) |
| `presences_remarques` | Monthly Attendance Notes | `id_remarque` (PK, INT), `id_employe` (FK), `mois` (TINYINT), `annee` (YEAR), `remarque` (TEXT) |
| `Fiches_Paie` | Monthly Employee Payslips | `id_paie` (PK, INT), `id_employe` (FK), `mois`, `annee`, `prime`, `deplacement`, `garde_nuit`, `garde_vendredi_jour`, `garde_vendredi_nuit`, `heures_sup_montant`, `conge`, `retenue_absence`, `penalites`, `avances`, `net_a_payer` (DECIMAL 15,2), `statut` (DRAFT, VALIDATED, PAID, VOID), `validated_by`, `validated_at`, `period_id` (FK) |
| `Employee_Contracts` | Employee Legal Contracts | `id_contract` (PK, INT), `id_employe` (FK), `contract_type`, `starts_on`, `ends_on`, `cnas_registered_on`, `resignation_on`, `status` (ACTIVE, ENDED, CANCELLED) |
| `Leave_Ledger` | Employee Annual Leave Balance Log | `id_leave` (PK, INT), `id_employe` (FK), `period_id` (FK), `entry_type` (ACCRUAL, TAKEN, ADJUSTMENT), `days` (DECIMAL 6,2), `effective_on` |
| `Payroll_Rates` | Configurable Payroll Rate Components | `id_rate` (PK, INT), `rate_code` (VARCHAR 50), `amount` (DECIMAL 15,2), `effective_from` (DATE), `effective_to` (DATE) |

---

### 2. Cash Register & Safe Module (Caisse & Coffre)

| Table Name | Description | Key Fields & Types |
| :--- | :--- | :--- |
| `Mouvement_Caisse` | Daily Cash Register Summary | `date_mouvement` (PK, DATE), `caisse_cv` (DECIMAL 15,2), `caisse_c` (DECIMAL 15,2), `tpe` (Card payment), `depenses`, `remboursement`, `convention`, `sous_traitants`, `period_id` (FK) |
| `Details_Depenses_Caisse` | Itemized Daily Counter Expenses | `id_depense_caisse` (PK, INT), `date_mouvement` (FK, DATE), `designation` (VARCHAR 255), `montant` (DECIMAL 15,2) |
| `Cloture_Caisse` | Daily Register Closing Records | `id_cloture` (PK, INT), `date_cloture` (FK, DATE), `utilisateur` (VARCHAR 100), `montant_reel` (Actual Cash), `montant_virtuel` (Expected System Cash), `remarques` |
| `Mouvement_Coffre` | Main Safe Box Ledger Transactions | `id_transaction` (PK, INT), `date_transaction` (DATE), `type_operation` (ENUM: ENTREE, SORTIE), `categorie_operation` (ENUM: CA_LAM, CA_CONVENTION, CA_ST, ENTREES_SUPP, AUTRE_SORTIE, DEPENSE_VEHICULE), `montant` (DECIMAL 15,2), `designation`, `payment_status` (PENDING, PAID, VOID), `remarks`, `period_id` (FK) |

---

### 3. Partner Management Module (Subcontractors & Conventions)

| Table Name | Description | Key Fields & Types |
| :--- | :--- | :--- |
| `Partenaires` | Subcontractors & Convention Profiles | `id_partenaire` (PK, INT), `nom_partenaire` (VARCHAR 255), `type_partenaire` (ENUM: SOUS_TRAITANT, CONVENTION), `solde_initial` (DECIMAL 15,2), `agrement_number`, `contact_person`, `phone`, `email`, `address_line1`, `tax_id_number`, `commercial_reg_no`, `bank_name`, `bank_account_iban`, `stock_partner_id` |
| `Operations_Partenaires` | Partner Invoices & Delivery Slips | `id_operation` (PK, INT), `id_partenaire` (FK), `type_document` (FACTURE, BL), `date_operation` (DATE), `date_reception`, `montant_total` (DECIMAL 15,2), `etat_paiement`, `observation`, `period_id` (FK), `stock_transfer_id` |
| `Paiements_Partenaires` | Payments Made to / Received from Partners | `id_paiement` (PK, INT), `id_operation` (FK), `date_paiement` (DATE), `montant_verse` (DECIMAL 15,2), `mode_paiement`, `reference_paiement`, `observations`, `period_id` (FK) |

---

### 4. Supplier Management & Expense Module

| Table Name | Description | Key Fields & Types |
| :--- | :--- | :--- |
| `Categories_Depenses` | Expense Categories Lookup | `id_categorie` (PK, INT), `nom_categorie` (VARCHAR 150, UNIQUE - e.g. EQUIPEMENTS, CONSOMMABLES) |
| `Fournisseurs` | Vendor & Supplier Master Catalog | `id_fournisseur` (PK, INT), `nom_fournisseur` (VARCHAR 255), `solde_initial` (DECIMAL 15,2), `agrement_number`, `contact_person`, `phone`, `email`, `address_line1`, `tax_id_number`, `commercial_reg_no`, `bank_name`, `bank_account_iban`, `stock_supplier_id`, `inclus_etat` (TINYINT 1) |
| `Depenses_Achats` | Purchase Invoices / Expenses | `id_depense` (PK, INT), `id_fournisseur` (FK), `id_categorie` (FK), `type_document` (FACTURE, BL), `date_facture` (DATE), `montant_total` (DECIMAL 15,2), `mode_paiement`, `observation`, `period_id` (FK), `stock_br_id` |
| `Paiements_Fournisseurs` | Supplier Payment Transactions | `id_paiement` (PK, INT), `id_depense` (FK), `date_paiement` (DATE), `montant_verse` (DECIMAL 15,2), `mode_paiement`, `reference_paiement`, `observations`, `period_id` (FK) |

---

### 5. Logistics, Bank & Incineration Module

| Table Name | Description | Key Fields & Types |
| :--- | :--- | :--- |
| `Vehicule_Service` | Service Vehicle Fuel & Log | `id_suivi` (PK, INT), `date_suivi` (DATE), `kilometrage` (INT), `montant_carburant` (DECIMAL 15,2), `type_carburant` (ENUM: GPL, ESSENCE), `details`, `id_transaction_coffre` (FK), `period_id` (FK) |
| `Compte_SGA` | SGA Bank Account Transactions | `id_transaction` (PK, INT), `date_transaction` (DATE), `n_cheque` (VARCHAR 50), `beneficiaire` (VARCHAR 255), `entrees` (DECIMAL 15,2), `sorties` (DECIMAL 15,2), `designation`, `is_void` (TINYINT 1), `void_reason`, `voided_by`, `voided_at`, `period_id` (FK) |
| `SGA_Opening_Balances` | Bank Account Annual Initial Balance | `annee` (PK, YEAR), `montant` (DECIMAL 15,2), `source_year`, `notes`, `created_by` |
| `Etat_Encaissement` | Customer Encashment Vouchers | `id_encaissement` (PK, INT), `date_encaissement` (DATE), `designation` (VARCHAR 255), `montant` (DECIMAL 15,2), `observations`, `period_id` (FK) |
| `Station_Incineration` | Medical Waste Incineration Tracking | `id_incineration` (PK, INT), `date_suivi` (DATE), `date_remise` (DATE), `poids_kg` (DECIMAL 10,2), `prix_unitaire_kg` (DECIMAL 10,2), `montant_total` (DECIMAL 15,2), `etat_paiement` (ENUM: PAYE, NON_PAYE), `period_id` (FK) |

---

### 6. Governance, Security & System Audit Module

| Table Name | Description | Key Fields & Types |
| :--- | :--- | :--- |
| `Utilisateurs` | User System Accounts | `id_utilisateur` (PK, INT), `username` (VARCHAR 100, UNIQUE), `password_hash`, `nom_complet`, `permissions` (JSON), `role_code` (VARCHAR 30), `is_active` (TINYINT 1) |
| `Roles` | System Security Roles | `code` (PK, VARCHAR 30 - ADMIN, DIRECTION, ACCOUNTANT, CASHIER, HR, VIEWER), `label`, `is_system_role` |
| `Role_Permissions` | Role-to-Permission Mapping | `role_code` (PK/FK), `permission_code` (PK - e.g. PERIOD_CLOSE, FINANCIAL_WRITE) |
| `Accounting_Periods` | Financial Closing Lock Periods | `id_period` (PK, INT), `annee` (YEAR), `mois` (TINYINT), `status` (ENUM: OPEN, PENDING_CLOSE, CLOSED, REOPENED), `opened_at`, `opened_by`, `closed_at`, `closed_by`, `close_note` |
| `Period_Reopen_Requests` | Workflow Requests to Reopen Locked Periods | `id_request` (PK, INT), `period_id` (FK), `requested_by`, `reason`, `status` (PENDING, APPROVED, REJECTED), `approved_by`, `approved_at` |
| `Audit_Events` | Immutable System Audit Trail | `id_event` (PK, BIGINT), `actor_username`, `action_code`, `entity_type`, `entity_id`, `period_id`, `old_values` (JSON), `new_values` (JSON), `reason`, `created_at` |
| `Calculation_Policies` | Versioned Financial Calculation Rules | `id_policy` (PK, INT), `policy_code`, `version_no`, `effective_from`, `definition_json` (JSON), `approval_status` (DRAFT, APPROVED, RETIRED) |
| `Profitability_Movements` | Monthly Profitability Allocations | `id_movement` (PK, INT), `source_period_id` (FK), `destination_period_id` (FK), `amount`, `movement_type` (CARRYOVER, ALLOCATION, REVERSAL), `status` (PENDING, APPROVED, VOID) |
| `Monthly_Carryovers` | Monthly Carryover Balances | `id_carryover` (PK, INT), `period_id` (FK), `carryover_type`, `amount`, `source_period_id` |
| `Import_Batches` | Bulk Data Import Session Tracking | `id_batch` (PK, INT), `source_filename`, `source_sha256` (CHAR 64, UNIQUE), `status` (STAGED, VALIDATED, IMPORTED, REJECTED), `reconciliation_json` |
| `Import_Rows` | Staged Row Data for Bulk Imports | `id_import_row` (PK, BIGINT), `batch_id` (FK), `sheet_name`, `source_row`, `entity_type`, `payload_json` (JSON), `status` (STAGED, IMPORTED, REJECTED) |
| `Export_History` | Audit Log of Exported Official Reports | `id_export` (PK, BIGINT), `report_name`, `period_id` (FK), `export_format` (PDF, XLSX, CSV), `file_path`, `generated_by`, `is_official` |
| `Documents` | Linked File Attachments | `id_document` (PK, BIGINT), `entity_type`, `entity_id`, `filename`, `storage_path`, `mime_type`, `uploaded_by` |
| `Schema_Migrations` | Migration Versioning Log | `version` (PK, INT), `name` (VARCHAR 150), `applied_at` (DATETIME) |

---

### 7. Analytical Database Views

| View Name | Description | Key Calculated Metrics |
| :--- | :--- | :--- |
| `Vue_Chiffre_Affaire_Mensuel` | Monthly Revenue Breakdown | `annee`, `mois`, `ca_lam` (Counter revenue), `ca_convention`, `ca_st` (Subcontractors), `entrees_supp`, `chiffre_affaire_total` |
| `Vue_Etat_Fournisseurs` | Supplier Financial Balance Statements | `id_fournisseur`, `nom_fournisseur`, `total_commandes` (Orders total + initial balance), `total_paye` (Total payments made), `reste_a_payer` (Outstanding liability) |
| `Vue_Profitabilite_Mensuelle` | Monthly Net Profitability Statement | `annee`, `mois`, `chiffre_affaire_total`, `total_paie` (Total payroll), `total_depenses` (Total purchases), `profitabilite_nette` (Net profit), `pourcentage_profitabilite` (Profitability margin %) |
| `Vue_Solde_Compte_SGA` | SGA Bank Account Running Balance | `id_transaction`, `date_transaction`, `n_cheque`, `beneficiaire`, `entrees`, `sorties`, `designation`, `solde_actuel` (Running cumulative bank balance) |
| `Vue_Statistiques_Vehicule` | Vehicle Monthly Consumption Analytics | `annee`, `mois`, `type_carburant`, `total_depenses_carburant`, `distance_parcourue_km`, `cout_par_km` (Calculated cost per kilometer) |
| `Vue_Statistiques_Incineration` | Monthly Incineration Station Summary | `annee`, `mois`, `total_poids_kg`, `total_montant`, `total_non_paye`, `max_poids_kg`, `min_poids_kg`, `moyenne_poids_kg` |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **MySQL / MariaDB Server 8.0+**

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/YourOrg/FINANCELAM.git
   cd FINANCELAM
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Database Connection:**
   Update your database credentials in `src/database/base/config.py` (or via environment variables):
   ```python
   DB_HOST = "localhost"
   DB_USER = "root"
   DB_PASSWORD = "your_password"
   DB_NAME = "financelam_db"
   ```

4. **Initialize Schema & Launch Application:**
   ```bash
   python src/main.py
   ```
   *Note: Database tables, indexes, views, and migrations are auto-initialized on launch.*

---

## 📜 License & Confidentiality

Internal business software developed exclusively for **ModernLam - Laboratoire d'Analyses Médicales**. All rights reserved.
