import os
import json
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QFormLayout, QSpinBox, QMessageBox,
    QSizePolicy, QScrollArea, QTabWidget
)
from PySide6.QtCore import Qt
from database.base.stock_connector import (
    load_stock_db_config, test_stock_db_connection,
    get_stock_db_suppliers_full, get_stock_db_partners_full
)
from database import data_manager
from ui.settings.pdf_config_tab import PdfConfigWidget
from ui.settings.app_db_config_tab import AppDbConfigWidget
from ui.table_helper import get_svg_icon

PATH_COG = "M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"
PATH_DATABASE = "M12 2C6.48 2 2 4.02 2 6.5v11c0 2.48 4.48 4.5 10 4.5s10-2.02 10-4.5v-11C22 4.02 17.52 2 12 2zm0 18c-4.42 0-8-1.57-8-3.5v-1.58c1.92 1.06 4.8 1.58 8 1.58s6.08-.52 8-1.58v1.58c0 1.93-3.58 3.5-8 3.5zm0-4.5c-4.42 0-8-1.57-8-3.5v-1.58c1.92 1.06 4.8 1.58 8 1.58s6.08-.52 8-1.58v1.58c0 1.93-3.58 3.5-8 3.5zm0-4.5c-4.42 0-8-1.57-8-3.5V5.92c1.92 1.06 4.8 1.58 8 1.58s6.08-.52 8-1.58v1.58c0 1.93-3.58 3.5-8 3.5zm0-4.5c-4.42 0-8-1.57-8-3.5S7.58 3 12 3s8 1.57 8 3.5-3.58 3.5-8 3.5z"

class StockConfigWidget(QWidget):
    def __init__(self, parent=None, settings_path="pdf_settings.json"):
        super().__init__(parent)
        self.settings_path = settings_path
        self.settings = self.load_settings()
        self.init_ui()

    def get_default_settings(self):
        return {
            "stock_db_host": "127.0.0.1",
            "stock_db_port": 3306,
            "stock_db_user": "root",
            "stock_db_password": "root",
            "stock_db_name": "Lab_Inventory_Enterprise_DB"
        }

    def load_settings(self):
        defaults = self.get_default_settings()
        stock_env = "D:\\git\\StockLam\\.env"
        if os.path.exists(stock_env):
            try:
                with open(stock_env, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            k, v = line.split('=', 1)
                            k = k.strip()
                            v = v.strip()
                            if k == 'DB_HOST':
                                defaults['stock_db_host'] = v
                            elif k == 'DB_PORT':
                                try:
                                    defaults['stock_db_port'] = int(v)
                                except ValueError:
                                    pass
                            elif k == 'DB_USER':
                                defaults['stock_db_user'] = v
                            elif k == 'DB_PASSWORD':
                                defaults['stock_db_password'] = v
                            elif k == 'DB_NAME':
                                defaults['stock_db_name'] = v
            except Exception as e:
                logging.error(f"Error parsing StockLam .env for default settings: {e}")

        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for k, v in defaults.items():
                        if k in data:
                            defaults[k] = data[k]
            except Exception as e:
                logging.error(f"Error loading stock settings: {e}")
        return defaults

    def save_settings(self):
        try:
            existing = {}
            if os.path.exists(self.settings_path):
                try:
                    with open(self.settings_path, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                except Exception:
                    pass
            
            existing.update({
                "stock_db_host": self.edit_host.text().strip(),
                "stock_db_port": self.sp_port.value(),
                "stock_db_user": self.edit_user.text().strip(),
                "stock_db_password": self.edit_pass.text(),
                "stock_db_name": self.edit_name.text().strip()
            })

            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Succès", "Les paramètres de connexion ont été enregistrés avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de l'enregistrement: {e}")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title_label = QLabel("Connexion à la Base de Données Stock (StockLam)")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007572;")
        layout.addWidget(title_label)

        # 1. Connection Group
        group_conn = QGroupBox("Paramètres de Connexion MySQL")
        form_layout = QFormLayout(group_conn)
        form_layout.setSpacing(10)

        self.edit_host = QLineEdit(self.settings.get('stock_db_host', '127.0.0.1'))
        self.sp_port = QSpinBox()
        self.sp_port.setRange(1, 65535)
        self.sp_port.setValue(int(self.settings.get('stock_db_port', 3306)))
        
        self.edit_user = QLineEdit(self.settings.get('stock_db_user', 'root'))
        self.edit_pass = QLineEdit(self.settings.get('stock_db_password', ''))
        self.edit_pass.setEchoMode(QLineEdit.Password)
        self.edit_name = QLineEdit(self.settings.get('stock_db_name', 'Lab_Inventory_Enterprise_DB'))

        form_layout.addRow("Adresse IP / Hôte:", self.edit_host)
        form_layout.addRow("Port:", self.sp_port)
        form_layout.addRow("Nom d'utilisateur:", self.edit_user)
        form_layout.addRow("Mot de passe:", self.edit_pass)
        form_layout.addRow("Nom de la Base de données:", self.edit_name)

        buttons_layout = QHBoxLayout()
        self.btn_test = QPushButton("⚡ Tester la Connexion")
        self.btn_test.setStyleSheet("background-color: #37474f; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        self.btn_test.clicked.connect(self.test_connection)

        self.btn_save = QPushButton("💾 Enregistrer la configuration")
        self.btn_save.setStyleSheet("background-color: #2e7d32; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        self.btn_save.clicked.connect(self.save_settings)

        buttons_layout.addWidget(self.btn_test)
        buttons_layout.addWidget(self.btn_save)
        layout.addWidget(group_conn)
        layout.addLayout(buttons_layout)

        # 2. Sync Group
        group_sync = QGroupBox("Outils d'Importation & Synchronisation")
        sync_layout = QVBoxLayout(group_sync)
        sync_layout.setSpacing(15)

        lbl_sync_desc = QLabel(
            "Ces outils permettent d'importer directement les fournisseurs et partenaires de la base de données Stock "
            "dans ce programme de comptabilité. Le programme liera automatiquement les fiches existantes par nom "
            "et mettra à jour leurs coordonnées sans supprimer ni écraser vos écritures de caisse ou factures existantes."
        )
        lbl_sync_desc.setWordWrap(True)
        lbl_sync_desc.setStyleSheet("color: #555; font-size: 12px;")
        sync_layout.addWidget(lbl_sync_desc)

        sync_buttons = QHBoxLayout()
        self.btn_sync_suppliers = QPushButton("📥 Importer / Synchroniser les Fournisseurs")
        self.btn_sync_suppliers.setStyleSheet("background-color: #007572; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_sync_suppliers.clicked.connect(self.sync_suppliers)

        self.btn_sync_partners = QPushButton("📥 Importer / Synchroniser les Partenaires")
        self.btn_sync_partners.setStyleSheet("background-color: #00828a; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_sync_partners.clicked.connect(self.sync_partners)

        sync_buttons.addWidget(self.btn_sync_suppliers)
        sync_buttons.addWidget(self.btn_sync_partners)
        sync_layout.addLayout(sync_buttons)

        layout.addWidget(group_sync)
        layout.addStretch()

    def test_connection(self):
        config = {
            "host": self.edit_host.text().strip(),
            "port": self.sp_port.value(),
            "user": self.edit_user.text().strip(),
            "password": self.edit_pass.text(),
            "database": self.edit_name.text().strip()
        }
        success, msg = test_stock_db_connection(config)
        if success:
            QMessageBox.information(self, "Succès", "Connexion à la base de données Stock réussie !")
        else:
            QMessageBox.critical(self, "Échec", f"Impossible de se connecter à la base de données Stock :\n{msg}")

    def sync_suppliers(self):
        config = {
            "host": self.edit_host.text().strip(),
            "port": self.sp_port.value(),
            "user": self.edit_user.text().strip(),
            "password": self.edit_pass.text(),
            "database": self.edit_name.text().strip()
        }
        
        try:
            stock_suppliers = get_stock_db_suppliers_full(config)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de lire la base de données Stock :\n{e}")
            return

        imported = 0
        updated = 0

        for s in stock_suppliers:
            stock_id = s['Supplier_ID']
            name = s['Supplier_Name']
            
            existing = data_manager.db.fetch_one("SELECT * FROM Fournisseurs WHERE stock_supplier_id = %s", (stock_id,))
            if not existing:
                existing = data_manager.db.fetch_one("SELECT * FROM Fournisseurs WHERE nom_fournisseur = %s", (name,))

            data = {
                "nom_fournisseur": name,
                "stock_supplier_id": stock_id,
                "contact_person": s.get('Contact_Person'),
                "phone": s.get('Phone'),
                "email": s.get('Email'),
                "website": s.get('Website'),
                "address_line1": s.get('Address_Line1'),
                "address_line2": s.get('Address_Line2'),
                "city": s.get('City'),
                "postal_code": s.get('Postal_Code'),
                "tax_id_number": s.get('Tax_ID_Number'),
                "commercial_reg_no": s.get('Commercial_Reg_No'),
                "bank_name": s.get('Bank_Name'),
                "bank_account_iban": s.get('Bank_Account_IBAN')
            }

            if existing:
                data["inclus_etat"] = existing.get("inclus_etat", 1)
                success, _ = data_manager.db.update_record("Fournisseurs", "id_fournisseur", existing['id_fournisseur'], data)
                if success:
                    updated += 1
            else:
                data["inclus_etat"] = 1
                success = data_manager.fournisseurs.add_fournisseur(data)
                if success:
                    imported += 1

        QMessageBox.information(
            self, 
            "Synchronisation terminée", 
            f"La synchronisation des fournisseurs a été effectuée avec succès !\n\n"
            f"- Fournisseurs mis à jour (liés) : {updated}\n"
            f"- Nouveaux fournisseurs importés : {imported}"
        )

    def sync_partners(self):
        config = {
            "host": self.edit_host.text().strip(),
            "port": self.sp_port.value(),
            "user": self.edit_user.text().strip(),
            "password": self.edit_pass.text(),
            "database": self.edit_name.text().strip()
        }
        
        try:
            stock_partners = get_stock_db_partners_full(config)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de lire la base de données Stock :\n{e}")
            return

        imported = 0
        updated = 0

        for p in stock_partners:
            stock_id = p['Partner_ID']
            name = p['Partner_Name']
            
            existing = data_manager.db.fetch_one("SELECT * FROM Partenaires WHERE stock_partner_id = %s", (stock_id,))
            if not existing:
                existing = data_manager.db.fetch_one("SELECT * FROM Partenaires WHERE nom_partenaire = %s", (name,))

            data = {
                "nom_partenaire": name,
                "stock_partner_id": stock_id,
                "contact_person": p.get('Contact_Person'),
                "phone": p.get('Phone'),
                "email": p.get('Email'),
                "website": p.get('Website'),
                "address_line1": p.get('Address_Line1'),
                "address_line2": p.get('Address_Line2'),
                "city": p.get('City'),
                "postal_code": p.get('Postal_Code'),
                "tax_id_number": p.get('Tax_ID_Number'),
                "commercial_reg_no": p.get('Commercial_Reg_No'),
                "bank_name": p.get('Bank_Name'),
                "bank_account_iban": p.get('Bank_Account_IBAN'),
                "type_partenaire": "SOUS_TRAITANT"
            }

            if existing:
                data["type_partenaire"] = existing["type_partenaire"]
                success, _ = data_manager.db.update_record("Partenaires", "id_partenaire", existing['id_partenaire'], data)
                if success:
                    updated += 1
            else:
                success = data_manager.partenaires.add_partenaire(data)
                if success:
                    imported += 1

        QMessageBox.information(
            self, 
            "Synchronisation terminée", 
            f"La synchronisation des partenaires a été effectuée avec succès !\n\n"
            f"- Partenaires mis à jour (liés) : {updated}\n"
            f"- Nouveaux partenaires importés : {imported}"
        )

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 15)
        layout.setSpacing(10)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { height: 35px; width: 180px; }")

        self.tab_pdf = PdfConfigWidget(self)
        self.tab_stock = StockConfigWidget(self)
        self.tab_app = AppDbConfigWidget(self)

        self.tabs.addTab(self.tab_pdf, "Paramètres PDF")
        self.tabs.setTabIcon(0, get_svg_icon(PATH_COG, "#007572", 14))

        self.tabs.addTab(self.tab_stock, "Base de Données Stock")
        self.tabs.setTabIcon(1, get_svg_icon(PATH_DATABASE, "#007572", 14))

        self.tabs.addTab(self.tab_app, "Base de Données App")
        self.tabs.setTabIcon(2, get_svg_icon(PATH_DATABASE, "#007572", 14))

        layout.addWidget(self.tabs)
