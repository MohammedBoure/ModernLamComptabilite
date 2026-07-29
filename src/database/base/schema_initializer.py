import mysql.connector
import logging

from .migrations import apply_migrations

"""قانون قبل الكتابة هنا أي جدول تضيف او تعدل أي هيكل فيه
 سواء إضغافة أو حدف يجب ان تضاف أيضا تحت الجدول صيغفة alter
  من أجل أن يحصل دلك في تشعيل البرنامج القادم ملاحظة مهة لا يجدلب تجاهلها 
"""
SCHEMA_QUERIES = [
    # --- 1. HR & Payroll ---
    """CREATE TABLE IF NOT EXISTS Employes (
        id_employe INT AUTO_INCREMENT PRIMARY KEY,
        nom_prenom VARCHAR(255) NOT NULL,
        fonction VARCHAR(100),
        salaire_base DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT 'الراتب الأساسي',
        date_naissance DATE,
        lieu_naissance VARCHAR(255),
        adresse TEXT,
        tel_1 VARCHAR(20),
        tel_2 VARCHAR(20),
        nss VARCHAR(50) COMMENT 'رقم الضمان الاجتماعي',
        n_anem VARCHAR(50) COMMENT 'رقم وكالة التشغيل',
        date_embauche DATE,
        date_inscription_cnas DATE,
        date_demission DATE NULL
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Presences (
        id_presence INT AUTO_INCREMENT PRIMARY KEY,
        id_employe INT NOT NULL,
        date_presence DATE NOT NULL,
        etat_jour ENUM('PRESENT', 'RECUPERATION', 'GARDE_NUIT', 'GARDE_VENDREDI_JOUR', 'GARDE_VENDREDI_NUIT', 'ABSENCE', 'CONGE_MALADIE', 'CONGE', 'NON_CONSIDERE') NOT NULL,
        heures_sup DECIMAL(5,2) DEFAULT 0.00,
        FOREIGN KEY (id_employe) REFERENCES Employes(id_employe) ON DELETE CASCADE
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Fiches_Paie (
        id_paie INT AUTO_INCREMENT PRIMARY KEY,
        id_employe INT NOT NULL,
        mois TINYINT NOT NULL,
        annee YEAR NOT NULL,
        prime DECIMAL(15,2) DEFAULT 0.00,
        deplacement DECIMAL(15,2) DEFAULT 0.00,
        garde_nuit DECIMAL(15,2) DEFAULT 0.00,
        garde_vendredi_jour DECIMAL(15,2) DEFAULT 0.00,
        garde_vendredi_nuit DECIMAL(15,2) DEFAULT 0.00,
        heures_sup_montant DECIMAL(15,2) DEFAULT 0.00 COMMENT 'المقابل المالي للساعات الإضافية (Présence en + / HS)',
        conge DECIMAL(15,2) DEFAULT 0.00 COMMENT 'تعويض أو قيمة العطلة (Congé)',
        retenue_absence DECIMAL(15,2) DEFAULT 0.00 COMMENT 'خصم الغيابات',
        penalites DECIMAL(15,2) DEFAULT 0.00,
        avances DECIMAL(15,2) DEFAULT 0.00,
        net_a_payer DECIMAL(15,2) NOT NULL COMMENT 'الراتب النهائي المستحق الصرف',
        remarques TEXT COMMENT 'ملاحظات وتبريرات الخصومات أو المكافآت',
        FOREIGN KEY (id_employe) REFERENCES Employes(id_employe) ON DELETE CASCADE,
        UNIQUE KEY unique_paie_mois (id_employe, mois, annee)
    ) ENGINE=InnoDB;""",

    # --- 2. Caisse & Coffre ---
    """CREATE TABLE IF NOT EXISTS Mouvement_Caisse (
        date_mouvement DATE PRIMARY KEY,
        caisse_cv DECIMAL(15,2) DEFAULT 0.00,
        caisse_c DECIMAL(15,2) DEFAULT 0.00,
        tpe DECIMAL(15,2) DEFAULT 0.00,
        depenses DECIMAL(15,2) DEFAULT 0.00,
        remboursement DECIMAL(15,2) DEFAULT 0.00,
        convention DECIMAL(15,2) DEFAULT 0.00,
        sous_traitants DECIMAL(15,2) DEFAULT 0.00
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Details_Depenses_Caisse (
        id_depense_caisse INT AUTO_INCREMENT PRIMARY KEY,
        date_mouvement DATE NOT NULL,
        designation VARCHAR(255) NOT NULL,
        montant DECIMAL(15,2) NOT NULL,
        FOREIGN KEY (date_mouvement) REFERENCES Mouvement_Caisse(date_mouvement) ON DELETE CASCADE
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Cloture_Caisse (
        id_cloture INT AUTO_INCREMENT PRIMARY KEY,
        date_cloture DATE NOT NULL,
        utilisateur VARCHAR(100) NOT NULL,
        montant_reel DECIMAL(15,2) NOT NULL,
        montant_virtuel DECIMAL(15,2) NOT NULL,
        remarques TEXT,
        FOREIGN KEY (date_cloture) REFERENCES Mouvement_Caisse(date_mouvement) ON DELETE RESTRICT
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Mouvement_Coffre (
        id_transaction INT AUTO_INCREMENT PRIMARY KEY,
        date_transaction DATE NOT NULL,
        type_operation ENUM('ENTREE', 'SORTIE') NOT NULL,
        categorie_operation ENUM('CA_LAM', 'CA_CONVENTION', 'CA_ST', 'ENTREES_SUPP', 'AUTRE_SORTIE', 'DEPENSE_VEHICULE') NOT NULL DEFAULT 'AUTRE_SORTIE',
        montant DECIMAL(15,2) NOT NULL,
        designation VARCHAR(255) NOT NULL
    ) ENGINE=InnoDB;""",

    # --- 3. Sous-traitants & Conventions ---
    """CREATE TABLE IF NOT EXISTS Partenaires (
        id_partenaire INT AUTO_INCREMENT PRIMARY KEY,
        nom_partenaire VARCHAR(255) NOT NULL,
        type_partenaire ENUM('SOUS_TRAITANT', 'CONVENTION') NOT NULL,
        solde_initial DECIMAL(15,2) DEFAULT 0.00 COMMENT 'الديون السابقة المستوردة من أرقام العام الماضي',
        agrement_number VARCHAR(100) NULL,
        contact_person VARCHAR(150) NULL,
        phone VARCHAR(50) NULL,
        email VARCHAR(150) NULL,
        website VARCHAR(200) NULL,
        address_line1 VARCHAR(255) NULL,
        address_line2 VARCHAR(255) NULL,
        city VARCHAR(100) NULL,
        postal_code VARCHAR(20) NULL,
        tax_id_number VARCHAR(100) NULL,
        commercial_reg_no VARCHAR(100) NULL,
        bank_name VARCHAR(150) NULL,
        bank_account_iban VARCHAR(150) NULL,
        stock_partner_id INT NULL
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Operations_Partenaires (
        id_operation INT AUTO_INCREMENT PRIMARY KEY,
        id_partenaire INT NOT NULL,
        type_document VARCHAR(50) DEFAULT 'FACTURE' COMMENT 'نوع الوثيقة: BL أو FACTURE',
        date_operation DATE NOT NULL,
        date_reception DATE NULL,
        montant_total DECIMAL(15,2) NOT NULL,
        etat_paiement VARCHAR(100),
        observation TEXT,
        stock_transfer_id INT NULL,
        FOREIGN KEY (id_partenaire) REFERENCES Partenaires(id_partenaire) ON DELETE CASCADE
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Paiements_Partenaires (
        id_paiement INT AUTO_INCREMENT PRIMARY KEY,
        id_operation INT NOT NULL,
        date_paiement DATE NOT NULL,
        montant_verse DECIMAL(15,2) NOT NULL,
        mode_paiement VARCHAR(100),
        reference_paiement VARCHAR(100),
        observations TEXT,
        FOREIGN KEY (id_operation) REFERENCES Operations_Partenaires(id_operation) ON DELETE CASCADE
    ) ENGINE=InnoDB;""",

    # --- 4. Fournisseurs & Dépenses ---
    """CREATE TABLE IF NOT EXISTS Categories_Depenses (
        id_categorie INT AUTO_INCREMENT PRIMARY KEY,
        nom_categorie VARCHAR(150) NOT NULL UNIQUE
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Fournisseurs (
        id_fournisseur INT AUTO_INCREMENT PRIMARY KEY,
        nom_fournisseur VARCHAR(255) NOT NULL,
        solde_initial DECIMAL(15,2) DEFAULT 0.00,
        agrement_number VARCHAR(100) NULL,
        contact_person VARCHAR(150) NULL,
        phone VARCHAR(50) NULL,
        email VARCHAR(150) NULL,
        website VARCHAR(200) NULL,
        address_line1 VARCHAR(255) NULL,
        address_line2 VARCHAR(255) NULL,
        city VARCHAR(100) NULL,
        postal_code VARCHAR(20) NULL,
        tax_id_number VARCHAR(100) NULL,
        commercial_reg_no VARCHAR(100) NULL,
        bank_name VARCHAR(150) NULL,
        bank_account_iban VARCHAR(150) NULL,
        stock_supplier_id INT NULL,
        inclus_etat TINYINT(1) DEFAULT 1
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Depenses_Achats (
        id_depense INT AUTO_INCREMENT PRIMARY KEY,
        id_fournisseur INT NOT NULL,
        id_categorie INT COMMENT 'EQUIPEMENTS أو CONSOMMABLES',
        type_document VARCHAR(50) DEFAULT 'FACTURE',
        date_facture DATE NOT NULL,
        montant_total DECIMAL(15,2) NOT NULL,
        mode_paiement VARCHAR(100),
        observation TEXT,
        stock_br_id INT NULL,
        FOREIGN KEY (id_fournisseur) REFERENCES Fournisseurs(id_fournisseur) ON DELETE CASCADE,
        FOREIGN KEY (id_categorie) REFERENCES Categories_Depenses(id_categorie) ON DELETE SET NULL
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Paiements_Fournisseurs (
        id_paiement INT AUTO_INCREMENT PRIMARY KEY,
        id_depense INT NOT NULL,
        date_paiement DATE NOT NULL,
        montant_verse DECIMAL(15,2) NOT NULL,
        mode_paiement VARCHAR(100),
        reference_paiement VARCHAR(100),
        observations TEXT,
        FOREIGN KEY (id_depense) REFERENCES Depenses_Achats(id_depense) ON DELETE CASCADE
    ) ENGINE=InnoDB;""",

    # --- 5. Logistique & Banque ---
    """CREATE TABLE IF NOT EXISTS Vehicule_Service (
        id_suivi INT AUTO_INCREMENT PRIMARY KEY,
        date_suivi DATE NOT NULL,
        kilometrage INT NOT NULL,
        montant_carburant DECIMAL(15,2) NOT NULL,
        type_carburant ENUM('GPL', 'ESSENCE') NOT NULL,
        details TEXT,
        id_transaction_coffre INT NULL,
        FOREIGN KEY (id_transaction_coffre) REFERENCES Mouvement_Coffre(id_transaction) ON DELETE SET NULL
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Compte_SGA (
        id_transaction INT AUTO_INCREMENT PRIMARY KEY,
        date_transaction DATE NOT NULL,
        n_cheque VARCHAR(50),
        beneficiaire VARCHAR(255),
        entrees DECIMAL(15,2) DEFAULT 0.00,
        sorties DECIMAL(15,2) DEFAULT 0.00,
        designation TEXT
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Etat_Encaissement (
        id_encaissement INT AUTO_INCREMENT PRIMARY KEY,
        date_encaissement DATE NOT NULL,
        designation VARCHAR(255) DEFAULT 'DIVERS CLIENTS',
        montant DECIMAL(15,2) NOT NULL,
        observations TEXT
    ) ENGINE=InnoDB;""",

    """CREATE TABLE IF NOT EXISTS Station_Incineration (
        id_incineration INT AUTO_INCREMENT PRIMARY KEY,
        date_suivi DATE NOT NULL,
        date_remise DATE NULL,
        poids_kg DECIMAL(10,2) NOT NULL DEFAULT 0.00,
        prix_unitaire_kg DECIMAL(10,2) NOT NULL DEFAULT 110.00,
        montant_total DECIMAL(15,2) NOT NULL DEFAULT 0.00,
        etat_paiement ENUM('PAYE', 'NON_PAYE') NOT NULL DEFAULT 'NON_PAYE',
        observations TEXT
    ) ENGINE=InnoDB;""",

    # --- 6. Views ---
    """CREATE OR REPLACE VIEW Vue_Chiffre_Affaire_Mensuel AS
    SELECT 
        YEAR(date_transaction) AS annee,
        MONTH(date_transaction) AS mois,
        SUM(CASE WHEN categorie_operation = 'CA_LAM' THEN montant ELSE 0 END) AS ca_lam,
        SUM(CASE WHEN categorie_operation = 'CA_CONVENTION' THEN montant ELSE 0 END) AS ca_convention,
        SUM(CASE WHEN categorie_operation = 'CA_ST' THEN montant ELSE 0 END) AS ca_st,
        SUM(CASE WHEN categorie_operation = 'ENTREES_SUPP' THEN montant ELSE 0 END) AS entrees_supp,
        SUM(montant) AS chiffre_affaire_total
    FROM Mouvement_Coffre
    WHERE type_operation = 'ENTREE'
    GROUP BY YEAR(date_transaction), MONTH(date_transaction);""",

    """CREATE OR REPLACE VIEW Vue_Etat_Fournisseurs AS
    SELECT 
        f.id_fournisseur,
        f.nom_fournisseur,
        IFNULL(SUM(d.montant_total), 0) + f.solde_initial AS total_commandes,
        IFNULL((SELECT SUM(montant_verse) FROM Paiements_Fournisseurs p JOIN Depenses_Achats d2 ON p.id_depense = d2.id_depense WHERE d2.id_fournisseur = f.id_fournisseur), 0) AS total_paye,
        (IFNULL(SUM(d.montant_total), 0) + f.solde_initial) - IFNULL((SELECT SUM(montant_verse) FROM Paiements_Fournisseurs p JOIN Depenses_Achats d2 ON p.id_depense = d2.id_depense WHERE d2.id_fournisseur = f.id_fournisseur), 0) AS reste_a_payer
    FROM Fournisseurs f
    LEFT JOIN Depenses_Achats d ON f.id_fournisseur = d.id_fournisseur
    GROUP BY f.id_fournisseur, f.nom_fournisseur, f.solde_initial;""",

    """CREATE OR REPLACE VIEW Vue_Profitabilite_Mensuelle AS
    SELECT 
        v_ca.annee, 
        v_ca.mois,
        v_ca.ca_lam,
        v_ca.ca_convention,
        v_ca.ca_st,
        v_ca.entrees_supp,
        v_ca.chiffre_affaire_total,
        IFNULL((SELECT SUM(net_a_payer) FROM Fiches_Paie fp WHERE fp.annee = v_ca.annee AND fp.mois = v_ca.mois), 0) AS total_paie,
        IFNULL((SELECT SUM(montant_total) FROM Depenses_Achats da WHERE YEAR(da.date_facture) = v_ca.annee AND MONTH(da.date_facture) = v_ca.mois), 0) AS total_depenses,
        (v_ca.chiffre_affaire_total) - (
            IFNULL((SELECT SUM(net_a_payer) FROM Fiches_Paie fp WHERE fp.annee = v_ca.annee AND fp.mois = v_ca.mois), 0) + 
            IFNULL((SELECT SUM(montant_total) FROM Depenses_Achats da WHERE YEAR(da.date_facture) = v_ca.annee AND MONTH(da.date_facture) = v_ca.mois), 0)
        ) AS profitabilite_nette,
        IF(v_ca.chiffre_affaire_total > 0, 
            ROUND((((v_ca.chiffre_affaire_total) - (
                IFNULL((SELECT SUM(net_a_payer) FROM Fiches_Paie fp WHERE fp.annee = v_ca.annee AND fp.mois = v_ca.mois), 0) + 
                IFNULL((SELECT SUM(montant_total) FROM Depenses_Achats da WHERE YEAR(da.date_facture) = v_ca.annee AND MONTH(da.date_facture) = v_ca.mois), 0)
            )) / v_ca.chiffre_affaire_total) * 100, 2), 
            0
        ) AS pourcentage_profitabilite
    FROM Vue_Chiffre_Affaire_Mensuel v_ca;""",

    """CREATE OR REPLACE VIEW Vue_Solde_Compte_SGA AS
    SELECT 
        c1.id_transaction,
        c1.date_transaction,
        c1.n_cheque,
        c1.beneficiaire,
        c1.entrees,
        c1.sorties,
        c1.designation,
        (SELECT SUM(c2.entrees) - SUM(c2.sorties) 
         FROM Compte_SGA c2 
         WHERE c2.date_transaction <= c1.date_transaction AND c2.id_transaction <= c1.id_transaction) AS solde_actuel
    FROM Compte_SGA c1
    ORDER BY c1.date_transaction, c1.id_transaction;""",

    """CREATE OR REPLACE VIEW Vue_Statistiques_Vehicule AS
    SELECT 
        YEAR(date_suivi) AS annee,
        MONTH(date_suivi) AS mois,
        type_carburant,
        SUM(montant_carburant) AS total_depenses_carburant,
        (MAX(kilometrage) - MIN(kilometrage)) AS distance_parcourue_km,
        IF((MAX(kilometrage) - MIN(kilometrage)) > 0, 
           ROUND(SUM(montant_carburant) / (MAX(kilometrage) - MIN(kilometrage)), 2), 
           0) AS cout_par_km
    FROM Vehicule_Service
    GROUP BY YEAR(date_suivi), MONTH(date_suivi), type_carburant;""",

    """CREATE OR REPLACE VIEW Vue_Statistiques_Incineration AS
    SELECT 
        YEAR(date_suivi) AS annee,
        MONTH(date_suivi) AS mois,
        SUM(poids_kg) AS total_poids_kg,
        SUM(montant_total) AS total_montant,
        SUM(CASE WHEN etat_paiement = 'NON_PAYE' THEN montant_total ELSE 0 END) AS total_non_paye,
        MAX(poids_kg) AS max_poids_kg,
        MIN(poids_kg) AS min_poids_kg,
        AVG(poids_kg) AS moyenne_poids_kg
    FROM Station_Incineration
    GROUP BY YEAR(date_suivi), MONTH(date_suivi);"""
]

INDEX_QUERIES = [
    "CREATE INDEX idx_paie_date ON Fiches_Paie(annee, mois);",
    "CREATE INDEX idx_caisse_date ON Mouvement_Caisse(date_mouvement);",
    "CREATE INDEX idx_coffre_date ON Mouvement_Coffre(date_transaction);",
    "CREATE INDEX idx_op_partenaire_date ON Operations_Partenaires(date_operation);",
    "CREATE INDEX idx_depense_date ON Depenses_Achats(date_facture);"
]


class SchemaInitializerMixin:
    """Mixin that provides _initialize_schema() to the Database class."""

    def _initialize_schema(self):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(buffered=True)
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

                logging.info("Initializing schema tables and migrations...")
                
                for query in SCHEMA_QUERIES:
                    try:
                        cursor.execute(query)
                        while cursor.nextset():
                            pass
                    except mysql.connector.Error as err:
                        if err.errno in (1060, 1061, 1091, 1826):
                            pass
                        else:
                            logging.warning(f"Schema warning during query '{query[:30]}...': {err}")

                apply_migrations(conn)

                # Auto-migration check for existing databases
                for table in ["Fournisseurs", "Partenaires"]:
                    try:
                        cursor.execute(f"DESCRIBE {table}")
                        existing_cols = {row[0].lower() for row in cursor.fetchall()}
                        
                        fields = [
                            ("agrement_number", "VARCHAR(100) NULL"),
                            ("contact_person", "VARCHAR(150) NULL"),
                            ("phone", "VARCHAR(50) NULL"),
                            ("email", "VARCHAR(150) NULL"),
                            ("website", "VARCHAR(200) NULL"),
                            ("address_line1", "VARCHAR(255) NULL"),
                            ("address_line2", "VARCHAR(255) NULL"),
                            ("city", "VARCHAR(100) NULL"),
                            ("postal_code", "VARCHAR(20) NULL"),
                            ("tax_id_number", "VARCHAR(100) NULL"),
                            ("commercial_reg_no", "VARCHAR(100) NULL"),
                            ("bank_name", "VARCHAR(150) NULL"),
                            ("bank_account_iban", "VARCHAR(150) NULL"),
                            ("stock_supplier_id", "INT NULL"),
                            ("stock_partner_id", "INT NULL")
                        ]
                        
                        for col_name, col_type in fields:
                            if col_name.lower() not in existing_cols:
                                if col_name == "stock_supplier_id" and table != "Fournisseurs":
                                    continue
                                if col_name == "stock_partner_id" and table != "Partenaires":
                                    continue
                                logging.info(f"Migration: Adding column {col_name} to {table}...")
                                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                    except mysql.connector.Error as err:
                        logging.warning(f"Migration check warning for table {table}: {err}")

                # Auto-migration check for Depenses_Achats
                try:
                    cursor.execute("DESCRIBE Depenses_Achats")
                    existing_cols = {row[0].lower() for row in cursor.fetchall()}
                    if "stock_br_id" not in existing_cols:
                        logging.info("Migration: Adding column stock_br_id to Depenses_Achats...")
                        cursor.execute("ALTER TABLE Depenses_Achats ADD COLUMN stock_br_id INT NULL")
                except mysql.connector.Error as err:
                    logging.warning(f"Migration check warning for Depenses_Achats: {err}")
                    
                # Auto-migration check for Operations_Partenaires
                try:
                    cursor.execute("DESCRIBE Operations_Partenaires")
                    existing_cols = {row[0].lower() for row in cursor.fetchall()}
                    if "stock_transfer_id" not in existing_cols:
                        logging.info("Migration: Adding column stock_transfer_id to Operations_Partenaires...")
                        cursor.execute("ALTER TABLE Operations_Partenaires ADD COLUMN stock_transfer_id INT NULL")
                except mysql.connector.Error as err:
                    logging.warning(f"Migration check warning for Operations_Partenaires: {err}")

                # Auto-migration check for Mouvement_Coffre ENUM update
                try:
                    cursor.execute("ALTER TABLE Mouvement_Coffre MODIFY COLUMN categorie_operation ENUM('CA_LAM', 'CA_CONVENTION', 'CA_ST', 'ENTREES_SUPP', 'AUTRE_SORTIE', 'DEPENSE_VEHICULE') NOT NULL DEFAULT 'AUTRE_SORTIE'")
                except mysql.connector.Error as err:
                    logging.warning(f"Migration check warning for Mouvement_Coffre ENUM: {err}")

                # Auto-migration check for Vehicule_Service
                try:
                    cursor.execute("DESCRIBE Vehicule_Service")
                    existing_cols = {row[0].lower() for row in cursor.fetchall()}
                    if "id_transaction_coffre" not in existing_cols:
                        logging.info("Migration: Adding column id_transaction_coffre to Vehicule_Service...")
                        cursor.execute("ALTER TABLE Vehicule_Service ADD COLUMN id_transaction_coffre INT NULL")
                        cursor.execute("ALTER TABLE Vehicule_Service ADD CONSTRAINT fk_vehicule_coffre FOREIGN KEY (id_transaction_coffre) REFERENCES Mouvement_Coffre(id_transaction) ON DELETE SET NULL")
                except mysql.connector.Error as err:
                    logging.warning(f"Migration check warning for Vehicule_Service: {err}")

                # Auto-migration check for Fournisseurs (inclus_etat)
                try:
                    cursor.execute("DESCRIBE Fournisseurs")
                    existing_cols = {row[0].lower() for row in cursor.fetchall()}
                    if "inclus_etat" not in existing_cols:
                        logging.info("Migration: Adding column inclus_etat to Fournisseurs...")
                        cursor.execute("ALTER TABLE Fournisseurs ADD COLUMN inclus_etat TINYINT(1) DEFAULT 1")
                except mysql.connector.Error as err:
                    logging.warning(f"Migration check warning for Fournisseurs (inclus_etat): {err}")

                logging.info("Creating performance indexes...")
                for query in INDEX_QUERIES:
                    try:
                        cursor.execute(query)
                        while cursor.nextset():
                            pass
                    except mysql.connector.Error as err:
                        if err.errno == 1061: # Duplicate key name
                            pass
                        else:
                            logging.warning(f"Index creation warning: {err}")

                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                logging.info("✅ Schema initialized successfully.")

        except mysql.connector.Error as err:
            logging.error(f"❌ Failed to initialize schema: {err}")
