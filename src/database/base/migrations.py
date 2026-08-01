"""Recorded, additive schema migrations for FINANCELAM."""

from __future__ import annotations

import logging

import mysql.connector


SYSTEM_ROLES = (
    ("ADMIN", "Administrateur"),
    ("DIRECTION", "Direction"),
    ("ACCOUNTANT", "Comptable"),
    ("CASHIER", "Caissier"),
    ("HR", "Ressources humaines"),
    ("VIEWER", "Lecture seule"),
)


ROLE_PERMISSIONS = (
    ("ADMIN", "*"),
    ("DIRECTION", "FINANCIAL_WRITE"),
    ("DIRECTION", "CASH_WRITE"),
    ("DIRECTION", "HR_WRITE"),
    ("DIRECTION", "REPORT_READ"),
    ("DIRECTION", "PERIOD_CLOSE"),
    ("DIRECTION", "REPORT_EXPORT"),
    ("ACCOUNTANT", "FINANCIAL_WRITE"),
    ("ACCOUNTANT", "PERIOD_CLOSE"),
    ("ACCOUNTANT", "REPORT_EXPORT"),
    ("CASHIER", "CASH_WRITE"),
    ("HR", "HR_WRITE"),
    ("VIEWER", "REPORT_READ"),
)

def _column_exists(cursor, table_name, column_name):
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE %s", (column_name,))
    return cursor.fetchone() is not None


def _ensure_column(cursor, table_name, column_name, definition):
    if not _column_exists(cursor, table_name, column_name):
        cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {definition}")


def _index_exists(cursor, table_name, index_name):
    cursor.execute(f"SHOW INDEX FROM `{table_name}` WHERE Key_name = %s", (index_name,))
    return cursor.fetchone() is not None


def _ensure_index(cursor, table_name, index_name, columns):
    if not _index_exists(cursor, table_name, index_name):
        cursor.execute(f"ALTER TABLE `{table_name}` ADD INDEX `{index_name}` ({columns})")

def _apply_legacy_compatibility(cursor):
    for name, definition in {
        "nin": "VARCHAR(50) NULL",
        "type_contrat": "VARCHAR(50) NULL",
        "photo_path": "VARCHAR(500) NULL",
        "date_fin_contrat": "DATE NULL",
        "remarque_drh": "TEXT NULL",
        "heures_travail_jour": "DECIMAL(5,2) NOT NULL DEFAULT 8.00",
    }.items():
        _ensure_column(cursor, "Employes", name, definition)

    _ensure_column(cursor, "Presences", "heure_entree", "TIME NULL")
    _ensure_column(cursor, "Presences", "heure_sortie", "TIME NULL")
    _ensure_column(cursor, "Fiches_Paie", "statut", "ENUM('DRAFT', 'VALIDATED', 'PAID', 'VOID') NOT NULL DEFAULT 'DRAFT'")
    _ensure_column(cursor, "Fiches_Paie", "validated_by", "VARCHAR(100) NULL")
    _ensure_column(cursor, "Fiches_Paie", "validated_at", "DATETIME NULL")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Utilisateurs (
            id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            nom_complet VARCHAR(255) NOT NULL,
            permissions JSON NULL,
            role_code VARCHAR(30) NOT NULL DEFAULT 'ADMIN',
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB"""
    )
    _ensure_column(cursor, "Utilisateurs", "role_code", "VARCHAR(30) NOT NULL DEFAULT 'ADMIN'")
    _ensure_column(cursor, "Utilisateurs", "is_active", "TINYINT(1) NOT NULL DEFAULT 1")
    _ensure_column(cursor, "Utilisateurs", "created_at", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
    _ensure_column(cursor, "Utilisateurs", "updated_at", "DATETIME NULL")
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS presences_remarques (
            id_remarque INT AUTO_INCREMENT PRIMARY KEY,
            id_employe INT NOT NULL,
            mois TINYINT NOT NULL,
            annee YEAR NOT NULL,
            remarque TEXT NULL,
            UNIQUE KEY uq_presence_remarque (id_employe, mois, annee),
            CONSTRAINT fk_presence_remarque_employe FOREIGN KEY (id_employe)
                REFERENCES Employes(id_employe) ON DELETE CASCADE
        ) ENGINE=InnoDB"""
    )


GOVERNANCE_DDL = (
    """CREATE TABLE IF NOT EXISTS Roles (
        code VARCHAR(30) PRIMARY KEY,
        label VARCHAR(100) NOT NULL,
        is_system_role TINYINT(1) NOT NULL DEFAULT 1
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Role_Permissions (
        role_code VARCHAR(30) NOT NULL,
        permission_code VARCHAR(100) NOT NULL,
        PRIMARY KEY (role_code, permission_code),
        CONSTRAINT fk_role_permission_role FOREIGN KEY (role_code)
            REFERENCES Roles(code) ON DELETE CASCADE
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Accounting_Periods (
        id_period INT AUTO_INCREMENT PRIMARY KEY,
        annee YEAR NOT NULL,
        mois TINYINT NOT NULL,
        status ENUM('OPEN', 'PENDING_CLOSE', 'CLOSED', 'REOPENED') NOT NULL DEFAULT 'OPEN',
        opened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        opened_by VARCHAR(100) NOT NULL,
        closed_at DATETIME NULL,
        closed_by VARCHAR(100) NULL,
        close_note TEXT NULL,
        UNIQUE KEY uq_accounting_period (annee, mois)
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Audit_Events (
        id_event BIGINT AUTO_INCREMENT PRIMARY KEY,
        actor_username VARCHAR(100) NOT NULL,
        action_code VARCHAR(100) NOT NULL,
        entity_type VARCHAR(100) NOT NULL,
        entity_id VARCHAR(100) NULL,
        period_id INT NULL,
        old_values JSON NULL,
        new_values JSON NULL,
        reason TEXT NULL,
        outcome ENUM('SUCCESS', 'DENIED', 'FAILED') NOT NULL DEFAULT 'SUCCESS',
        section_code VARCHAR(100) NULL,
        tab_code VARCHAR(100) NULL,
        actor_role VARCHAR(30) NULL,
        event_category VARCHAR(50) NOT NULL DEFAULT 'BUSINESS',
        message TEXT NULL,
        request_id CHAR(36) NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_audit_period (period_id),
        INDEX idx_audit_entity (entity_type, entity_id),
        INDEX idx_audit_created (created_at),
        INDEX idx_audit_actor_created (actor_username, created_at),
        INDEX idx_audit_section_tab (section_code, tab_code),
        INDEX idx_audit_outcome (outcome)
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Period_Reopen_Requests (
        id_request INT AUTO_INCREMENT PRIMARY KEY,
        period_id INT NOT NULL,
        requested_by VARCHAR(100) NOT NULL,
        reason TEXT NOT NULL,
        status ENUM('PENDING', 'APPROVED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
        approved_by VARCHAR(100) NULL,
        approved_at DATETIME NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_reopen_period FOREIGN KEY (period_id)
            REFERENCES Accounting_Periods(id_period) ON DELETE RESTRICT
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Calculation_Policies (
        id_policy INT AUTO_INCREMENT PRIMARY KEY,
        policy_code VARCHAR(100) NOT NULL,
        version_no INT NOT NULL,
        effective_from DATE NOT NULL,
        definition_json JSON NOT NULL,
        approval_status ENUM('DRAFT', 'APPROVED', 'RETIRED') NOT NULL DEFAULT 'DRAFT',
        approved_by VARCHAR(100) NULL,
        approved_at DATETIME NULL,
        notes TEXT NULL,
        UNIQUE KEY uq_calculation_policy (policy_code, version_no)
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Profitability_Movements (
        id_movement INT AUTO_INCREMENT PRIMARY KEY,
        source_period_id INT NOT NULL,
        destination_period_id INT NOT NULL,
        amount DECIMAL(15,2) NOT NULL,
        movement_type ENUM('CARRYOVER', 'ALLOCATION', 'REVERSAL') NOT NULL,
        designation VARCHAR(255) NOT NULL,
        status ENUM('PENDING', 'APPROVED', 'VOID') NOT NULL DEFAULT 'PENDING',
        approved_by VARCHAR(100) NULL,
        approved_at DATETIME NULL,
        created_by VARCHAR(100) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_profit_source FOREIGN KEY (source_period_id)
            REFERENCES Accounting_Periods(id_period) ON DELETE RESTRICT,
        CONSTRAINT fk_profit_destination FOREIGN KEY (destination_period_id)
            REFERENCES Accounting_Periods(id_period) ON DELETE RESTRICT
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Monthly_Carryovers (
        id_carryover INT AUTO_INCREMENT PRIMARY KEY,
        period_id INT NOT NULL,
        carryover_type VARCHAR(50) NOT NULL,
        amount DECIMAL(15,2) NOT NULL,
        source_period_id INT NULL,
        notes TEXT NULL,
        UNIQUE KEY uq_carryover (period_id, carryover_type, source_period_id),
        CONSTRAINT fk_carryover_period FOREIGN KEY (period_id)
            REFERENCES Accounting_Periods(id_period) ON DELETE RESTRICT
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Payroll_Rates (
        id_rate INT AUTO_INCREMENT PRIMARY KEY,
        rate_code VARCHAR(50) NOT NULL,
        amount DECIMAL(15,2) NOT NULL,
        effective_from DATE NOT NULL,
        effective_to DATE NULL,
        approved_by VARCHAR(100) NULL,
        notes TEXT NULL,
        UNIQUE KEY uq_payroll_rate (rate_code, effective_from)
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Employee_Contracts (
        id_contract INT AUTO_INCREMENT PRIMARY KEY,
        id_employe INT NOT NULL,
        contract_type VARCHAR(50) NOT NULL,
        starts_on DATE NOT NULL,
        ends_on DATE NULL,
        cnas_registered_on DATE NULL,
        resignation_on DATE NULL,
        status ENUM('ACTIVE', 'ENDED', 'CANCELLED') NOT NULL DEFAULT 'ACTIVE',
        notes TEXT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_contract_employee FOREIGN KEY (id_employe)
            REFERENCES Employes(id_employe) ON DELETE RESTRICT
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Leave_Ledger (
        id_leave INT AUTO_INCREMENT PRIMARY KEY,
        id_employe INT NOT NULL,
        period_id INT NULL,
        entry_type ENUM('ACCRUAL', 'TAKEN', 'ADJUSTMENT') NOT NULL,
        days DECIMAL(6,2) NOT NULL,
        effective_on DATE NOT NULL,
        notes TEXT NULL,
        created_by VARCHAR(100) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_leave_employee FOREIGN KEY (id_employe)
            REFERENCES Employes(id_employe) ON DELETE RESTRICT
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Import_Batches (
        id_batch INT AUTO_INCREMENT PRIMARY KEY,
        source_filename VARCHAR(500) NOT NULL,
        source_sha256 CHAR(64) NOT NULL,
        status ENUM('STAGED', 'VALIDATED', 'IMPORTED', 'REJECTED') NOT NULL DEFAULT 'STAGED',
        imported_by VARCHAR(100) NOT NULL,
        imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        reconciliation_json JSON NULL,
        UNIQUE KEY uq_import_source (source_sha256)
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Import_Rows (
        id_import_row BIGINT AUTO_INCREMENT PRIMARY KEY,
        batch_id INT NOT NULL,
        sheet_name VARCHAR(255) NOT NULL,
        source_row INT NOT NULL,
        source_reference VARCHAR(500) NULL,
        entity_type VARCHAR(100) NOT NULL,
        payload_json JSON NOT NULL,
        status ENUM('STAGED', 'IMPORTED', 'REJECTED') NOT NULL DEFAULT 'STAGED',
        rejection_reason TEXT NULL,
        entity_id VARCHAR(100) NULL,
        UNIQUE KEY uq_import_row (batch_id, sheet_name, source_row, entity_type),
        CONSTRAINT fk_import_row_batch FOREIGN KEY (batch_id)
            REFERENCES Import_Batches(id_batch) ON DELETE CASCADE
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Export_History (
        id_export BIGINT AUTO_INCREMENT PRIMARY KEY,
        report_name VARCHAR(150) NOT NULL,
        period_id INT NULL,
        export_format ENUM('PDF', 'XLSX', 'CSV') NOT NULL,
        file_path VARCHAR(1000) NOT NULL,
        generated_by VARCHAR(100) NOT NULL,
        generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        is_official TINYINT(1) NOT NULL DEFAULT 0,
        CONSTRAINT fk_export_period FOREIGN KEY (period_id)
            REFERENCES Accounting_Periods(id_period) ON DELETE SET NULL
    ) ENGINE=InnoDB""",
    """CREATE TABLE IF NOT EXISTS Documents (
        id_document BIGINT AUTO_INCREMENT PRIMARY KEY,
        entity_type VARCHAR(100) NOT NULL,
        entity_id VARCHAR(100) NOT NULL,
        filename VARCHAR(500) NOT NULL,
        storage_path VARCHAR(1000) NOT NULL,
        mime_type VARCHAR(150) NULL,
        uploaded_by VARCHAR(100) NOT NULL,
        uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_document_entity (entity_type, entity_id)
    ) ENGINE=InnoDB""",
)


def _apply_governance_schema(cursor):
    period_columns = (
        ("Mouvement_Caisse", "date_mouvement"),
        ("Details_Depenses_Caisse", "date_mouvement"),
        ("Cloture_Caisse", "date_cloture"),
        ("Mouvement_Coffre", "date_transaction"),
        ("Operations_Partenaires", "date_operation"),
        ("Paiements_Partenaires", "date_paiement"),
        ("Depenses_Achats", "date_facture"),
        ("Paiements_Fournisseurs", "date_paiement"),
        ("Vehicule_Service", "date_suivi"),
        ("Compte_SGA", "date_transaction"),
        ("Etat_Encaissement", "date_encaissement"),
        ("Station_Incineration", "date_suivi"),
        ("Presences", "date_presence"),
    )
    for table_name, date_column in period_columns:
        _ensure_column(cursor, table_name, "period_id", "INT NULL")
        cursor.execute(
            f"""INSERT IGNORE INTO Accounting_Periods (annee, mois, status, opened_by)
                SELECT YEAR(`{date_column}`), MONTH(`{date_column}`), 'OPEN', 'legacy-migration'
                FROM `{table_name}` WHERE `{date_column}` IS NOT NULL"""
        )
        cursor.execute(
            f"""UPDATE `{table_name}` target JOIN Accounting_Periods period
                ON period.annee = YEAR(target.`{date_column}`)
                AND period.mois = MONTH(target.`{date_column}`)
                SET target.period_id = period.id_period WHERE target.period_id IS NULL"""
        )
    _ensure_column(cursor, "Fiches_Paie", "period_id", "INT NULL")
    cursor.execute(
        """INSERT IGNORE INTO Accounting_Periods (annee, mois, status, opened_by)
            SELECT annee, mois, 'OPEN', 'legacy-migration' FROM Fiches_Paie"""
    )
    cursor.execute(
        """UPDATE Fiches_Paie salary JOIN Accounting_Periods period
            ON period.annee = salary.annee AND period.mois = salary.mois
            SET salary.period_id = period.id_period WHERE salary.period_id IS NULL"""
    )
    cursor.execute("UPDATE Fiches_Paie SET statut = 'VALIDATED' WHERE statut = 'DRAFT'")


def _apply_financial_operational_schema(cursor):
    """Additive fields needed for paid movements, annual SGA, and reversals."""
    _ensure_column(cursor, "Mouvement_Coffre", "payment_status", "ENUM('PENDING', 'PAID', 'VOID') NOT NULL DEFAULT 'PAID'")
    _ensure_column(cursor, "Mouvement_Coffre", "remarks", "TEXT NULL")
    _ensure_column(cursor, "Compte_SGA", "is_void", "TINYINT(1) NOT NULL DEFAULT 0")
    _ensure_column(cursor, "Compte_SGA", "void_reason", "TEXT NULL")
    _ensure_column(cursor, "Compte_SGA", "voided_by", "VARCHAR(100) NULL")
    _ensure_column(cursor, "Compte_SGA", "voided_at", "DATETIME NULL")
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS SGA_Opening_Balances (
            annee YEAR PRIMARY KEY,
            montant DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            source_year YEAR NULL,
            notes TEXT NULL,
            created_by VARCHAR(100) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_by VARCHAR(100) NULL,
            updated_at DATETIME NULL
        ) ENGINE=InnoDB"""
    )
    cursor.execute(
        """INSERT IGNORE INTO SGA_Opening_Balances (annee, montant, notes, created_by)
            SELECT 2025, entrees, 'Imported legacy opening balance', 'legacy-migration'
            FROM Compte_SGA
            WHERE designation = 'Solde Initial 2025' AND date_transaction = '2025-12-31'
            LIMIT 1"""
    )

def _seed_role_permissions(cursor):
    cursor.executemany(
        "INSERT IGNORE INTO Role_Permissions (role_code, permission_code) VALUES (%s, %s)",
        ROLE_PERMISSIONS,
    )

def _apply_activity_tracking_schema(cursor):
    for column_name, definition in {
        "actor_username": "VARCHAR(100) NULL",
        "action_code": "VARCHAR(100) NULL",
        "entity_type": "VARCHAR(100) NULL",
        "entity_id": "VARCHAR(100) NULL",
        "period_id": "INT NULL",
        "old_values": "JSON NULL",
        "new_values": "JSON NULL",
        "reason": "TEXT NULL",
        "outcome": "ENUM('SUCCESS', 'DENIED', 'FAILED') NOT NULL DEFAULT 'SUCCESS'",
        "section_code": "VARCHAR(100) NULL",
        "tab_code": "VARCHAR(100) NULL",
        "actor_role": "VARCHAR(30) NULL",
        "event_category": "VARCHAR(50) NOT NULL DEFAULT 'BUSINESS'",
        "message": "TEXT NULL",
        "request_id": "CHAR(36) NULL",
        "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
    }.items():
        _ensure_column(cursor, "Audit_Events", column_name, definition)
    _ensure_index(cursor, "Audit_Events", "idx_audit_entity", "`entity_type`, `entity_id`")
    _ensure_index(cursor, "Audit_Events", "idx_audit_created", "`created_at`")
    _ensure_index(cursor, "Audit_Events", "idx_audit_period", "`period_id`")
    _ensure_index(cursor, "Audit_Events", "idx_audit_actor_created", "`actor_username`, `created_at`")
    _ensure_index(cursor, "Audit_Events", "idx_audit_section_tab", "`section_code`, `tab_code`")
    _ensure_index(cursor, "Audit_Events", "idx_audit_outcome", "`outcome`")

def _upgrade_direction_permissions(cursor):
    """Give the partial administrator every operational permission except Users/Activity."""
    cursor.executemany(
        "INSERT IGNORE INTO Role_Permissions (role_code, permission_code) VALUES (%s, %s)",
        tuple(("DIRECTION", permission) for permission in (
            "FINANCIAL_WRITE", "CASH_WRITE", "HR_WRITE", "REPORT_READ", "PERIOD_CLOSE", "REPORT_EXPORT",
        )),
    )

def ensure_schema_objects(cursor):
    """Repair missing objects even when a legacy migration marker is present."""
    _apply_legacy_compatibility(cursor)
    for statement in GOVERNANCE_DDL:
        cursor.execute(statement)
    _apply_governance_schema(cursor)
    _apply_financial_operational_schema(cursor)
    _seed_role_permissions(cursor)
    _apply_activity_tracking_schema(cursor)
    _upgrade_direction_permissions(cursor)

def apply_migrations(connection):
    """Apply each migration once; any error aborts the caller transaction."""
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Schema_Migrations (
                version INT PRIMARY KEY, name VARCHAR(150) NOT NULL,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB"""
        )
        cursor.execute("SELECT version FROM Schema_Migrations")
        applied = {row[0] for row in cursor.fetchall()}
        migrations = (
            (1, "legacy_schema_compatibility", (), _apply_legacy_compatibility),
            (2, "accounting_governance", GOVERNANCE_DDL, _apply_governance_schema),
            (3, "financial_operational_controls", (), _apply_financial_operational_schema),
            (4, "seed_role_permissions", (), _seed_role_permissions),
            (5, "activity_tracking", (), _apply_activity_tracking_schema),
            (6, "direction_full_operational_permissions", (), _upgrade_direction_permissions),
        )
        for version, name, statements, upgrade in migrations:
            if version in applied:
                continue
            logging.info("Applying schema migration %s: %s", version, name)
            for statement in statements:
                cursor.execute(statement)
            upgrade(cursor)
            cursor.execute(
                "INSERT INTO Schema_Migrations (version, name) VALUES (%s, %s)",
                (version, name),
            )
        ensure_schema_objects(cursor)
        cursor.executemany("INSERT IGNORE INTO Roles (code, label) VALUES (%s, %s)", SYSTEM_ROLES)
    except mysql.connector.Error:
        logging.exception("Schema migration failed; transaction will be rolled back.")
        raise
    finally:
        cursor.close()
