from PySide6.QtWidgets import QMessageBox, QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit, QTabWidget, QFormLayout, QWidget
from PySide6.QtCore import QDate
from ui.base_dialog import BaseDialog
from database import data_manager
from database.base.stock_connector import load_stock_db_config, get_stock_db_partners

class PartenaireDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Partenaire / Sous-Traitant" if record else "Ajouter Partenaire / Sous-Traitant", parent)
        from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QFormLayout
        self.setMinimumWidth(800)
        
        main_h_layout = QHBoxLayout()
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        
        form_gen = QFormLayout()
        form_contact = QFormLayout()
        form_addr = QFormLayout()
        form_fisc = QFormLayout()
        
        # --- Section 1: Général (Left) ---
        left_col.addWidget(QLabel("<h4 style='color:#007572; margin-top:0px; margin-bottom:0;'>--- Informations Générales ---</h4>"))
        self.txt_nom = QLineEdit()
        self.cb_type = QComboBox()
        self.cb_type.addItems(["SOUS_TRAITANT", "CONVENTION"])
        self.val_solde = QDoubleSpinBox()
        self.val_solde.setMaximum(999999999.0)
        self.txt_agrement = QLineEdit()
        
        self.cb_stock_map = QComboBox()
        self.cb_stock_map.addItem("Aucun (Sans liaison)", None)
        self.load_stock_partners()
        
        form_gen.addRow("Nom du Partenaire:", self.txt_nom)
        form_gen.addRow("Type:", self.cb_type)
        form_gen.addRow("Solde Initial (Dette pr.):", self.val_solde)
        form_gen.addRow("Numéro d'Agrément:", self.txt_agrement)
        form_gen.addRow("Même partenaire dans Stock:", self.cb_stock_map)
        left_col.addLayout(form_gen)
        
        # --- Section 2: Contact (Left) ---
        left_col.addWidget(QLabel("<h4 style='color:#007572; margin-top:10px; margin-bottom:0;'>--- Contact ---</h4>"))
        self.txt_contact_person = QLineEdit()
        self.txt_phone = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_website = QLineEdit()
        
        form_contact.addRow("Personne de Contact:", self.txt_contact_person)
        form_contact.addRow("Téléphone:", self.txt_phone)
        form_contact.addRow("E-mail:", self.txt_email)
        form_contact.addRow("Site Web:", self.txt_website)
        left_col.addLayout(form_contact)
        left_col.addStretch()
        
        # --- Section 3: Adresse (Right) ---
        right_col.addWidget(QLabel("<h4 style='color:#007572; margin-top:0px; margin-bottom:0;'>--- Adresse ---</h4>"))
        self.txt_addr1 = QLineEdit()
        self.txt_addr2 = QLineEdit()
        self.txt_city = QLineEdit()
        self.txt_postal = QLineEdit()
        
        form_addr.addRow("Adresse Ligne 1:", self.txt_addr1)
        form_addr.addRow("Adresse Ligne 2:", self.txt_addr2)
        form_addr.addRow("Ville:", self.txt_city)
        form_addr.addRow("Code Postal:", self.txt_postal)
        right_col.addLayout(form_addr)
        
        # --- Section 4: Fiscal & Banque (Right) ---
        right_col.addWidget(QLabel("<h4 style='color:#007572; margin-top:10px; margin-bottom:0;'>--- Fiscal & Banque ---</h4>"))
        self.txt_tax_id = QLineEdit()
        self.txt_comm_reg = QLineEdit()
        self.txt_bank_name = QLineEdit()
        self.txt_iban = QLineEdit()
        
        form_fisc.addRow("Identifiant Fiscal (NIF):", self.txt_tax_id)
        form_fisc.addRow("Registre de Commerce:", self.txt_comm_reg)
        form_fisc.addRow("Nom de la Banque:", self.txt_bank_name)
        form_fisc.addRow("IBAN / N° Compte:", self.txt_iban)
        right_col.addLayout(form_fisc)
        right_col.addStretch()
        
        main_h_layout.addLayout(left_col)
        main_h_layout.addSpacing(20)
        main_h_layout.addLayout(right_col)
        
        self.form_layout.addRow(main_h_layout)

        if record:
            self.txt_nom.setText(record.get('nom_partenaire', '') or '')
            self.cb_type.setCurrentText(str(record.get('type_partenaire', 'SOUS_TRAITANT')))
            self.val_solde.setValue(float(record.get('solde_initial', 0.0) or 0.0))
            self.txt_agrement.setText(record.get('agrement_number', '') or '')
            self.txt_contact_person.setText(record.get('contact_person', '') or '')
            self.txt_phone.setText(record.get('phone', '') or '')
            self.txt_email.setText(record.get('email', '') or '')
            self.txt_website.setText(record.get('website', '') or '')
            self.txt_addr1.setText(record.get('address_line1', '') or '')
            self.txt_addr2.setText(record.get('address_line2', '') or '')
            self.txt_city.setText(record.get('city', '') or '')
            self.txt_postal.setText(record.get('postal_code', '') or '')
            self.txt_tax_id.setText(record.get('tax_id_number', '') or '')
            self.txt_comm_reg.setText(record.get('commercial_reg_no', '') or '')
            self.txt_bank_name.setText(record.get('bank_name', '') or '')
            self.txt_iban.setText(record.get('bank_account_iban', '') or '')
            
            # Map stock partner association
            stock_id = record.get('stock_partner_id')
            if stock_id is not None:
                idx = self.cb_stock_map.findData(stock_id)
                if idx >= 0:
                    self.cb_stock_map.setCurrentIndex(idx)

    def load_stock_partners(self):
        try:
            config = load_stock_db_config()
            partners = get_stock_db_partners(config)
            for p in partners:
                self.cb_stock_map.addItem(p['Partner_Name'], p['Partner_ID'])
        except Exception as e:
            import logging
            logging.error(f"Error loading stock partners: {e}")

    def save_data(self):
        nom = self.txt_nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Attention", "Le nom est requis.")
            return
            
        data = {
            "nom_partenaire": nom,
            "type_partenaire": self.cb_type.currentText(),
            "solde_initial": self.val_solde.value(),
            "agrement_number": self.txt_agrement.text().strip() or None,
            "contact_person": self.txt_contact_person.text().strip() or None,
            "phone": self.txt_phone.text().strip() or None,
            "email": self.txt_email.text().strip() or None,
            "website": self.txt_website.text().strip() or None,
            "address_line1": self.txt_addr1.text().strip() or None,
            "address_line2": self.txt_addr2.text().strip() or None,
            "city": self.txt_city.text().strip() or None,
            "postal_code": self.txt_postal.text().strip() or None,
            "tax_id_number": self.txt_tax_id.text().strip() or None,
            "commercial_reg_no": self.txt_comm_reg.text().strip() or None,
            "bank_name": self.txt_bank_name.text().strip() or None,
            "bank_account_iban": self.txt_iban.text().strip() or None,
            "stock_partner_id": self.cb_stock_map.currentData()
        }
            
        if self.record:
            success, _ = data_manager.db.update_record(
                "Partenaires", "id_partenaire", self.record['id_partenaire'],
                data
            )
        else:
            success = data_manager.partenaires.add_partenaire(data)
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class OperationPartenaireDialog(BaseDialog):
    def __init__(self, parent=None, record=None, id_partenaire=None):
        super().__init__("Modifier Opération Partenaire" if record else "Nouvelle Opération Partenaire", parent)
        self.record = record
        
        self.cb_part = QComboBox()
        self.load_partenaires()
        
        self.txt_doc = QLineEdit("FACTURE")
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.txt_reception = QDateEdit()
        self.txt_reception.setDate(QDate.currentDate())
        self.txt_reception.setCalendarPopup(True)
        
        self.val_montant = QDoubleSpinBox()
        self.val_montant.setMaximum(999999999.0)
        
        self.txt_etat = QLineEdit("NON PAYE")
        self.txt_obs = QTextEdit()
        self.txt_obs.setMaximumHeight(80)
        
        self.form_layout.addRow("Partenaire:", self.cb_part)
        self.form_layout.addRow("Type Document (BL/Facture):", self.txt_doc)
        self.form_layout.addRow("Date Opération:", self.txt_date)
        self.form_layout.addRow("Date Réception:", self.txt_reception)
        self.form_layout.addRow("Montant Total:", self.val_montant)
        self.form_layout.addRow("État Paiement:", self.txt_etat)
        self.form_layout.addRow("Observations:", self.txt_obs)

        if record:
            idx = self.cb_part.findData(record.get('id_partenaire'))
            if idx >= 0:
                self.cb_part.setCurrentIndex(idx)
            self.txt_doc.setText(record.get('type_document', 'FACTURE'))
            self.txt_date.setDate(QDate.fromString(str(record.get('date_operation')), "yyyy-MM-dd"))
            self.txt_reception.setDate(QDate.fromString(str(record.get('date_reception')), "yyyy-MM-dd") if record.get('date_reception') else QDate.currentDate())
            self.val_montant.setValue(float(record.get('montant_total', 0.0) or 0.0))
            self.txt_etat.setText(record.get('etat_paiement', 'NON PAYE'))
            self.txt_obs.setPlainText(record.get('observation', '') or '')
        else:
            if id_partenaire:
                idx = self.cb_part.findData(id_partenaire)
                if idx >= 0:
                    self.cb_part.setCurrentIndex(idx)

    def load_partenaires(self):
        parts = data_manager.partenaires.get_partenaires()
        for p in parts:
            self.cb_part.addItem(p['nom_partenaire'], p['id_partenaire'])

    def save_data(self):
        p_id = self.cb_part.currentData()
        if not p_id:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord ajouter des partenaires.")
            return
            
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        date_rec = self.txt_reception.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Operations_Partenaires", "id_operation", self.record['id_operation'],
                {
                    "id_partenaire": p_id,
                    "type_document": self.txt_doc.text().strip(),
                    "date_operation": date_str,
                    "date_reception": date_rec,
                    "montant_total": self.val_montant.value(),
                    "etat_paiement": self.txt_etat.text().strip(),
                    "observation": self.txt_obs.toPlainText().strip()
                }
            )
        else:
            success = data_manager.partenaires.add_operation(
                p_id, self.txt_doc.text().strip(), date_str, date_rec,
                self.val_montant.value(), self.txt_etat.text().strip(), self.txt_obs.toPlainText().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class PaiementPartenaireDialog(BaseDialog):
    def __init__(self, parent=None, record=None, id_partenaire=None, id_operation=None):
        super().__init__("Modifier Paiement Partenaire" if record else "Enregistrer Paiement Partenaire", parent)
        self.record = record
        
        self.cb_op = QComboBox()
        self.load_operations(id_partenaire)
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.val_verse = QDoubleSpinBox()
        self.val_verse.setMaximum(999999999.0)
        
        self.txt_mode = QLineEdit("ESPECES")
        self.txt_ref = QLineEdit()
        self.txt_obs = QTextEdit()
        self.txt_obs.setMaximumHeight(80)
        
        self.form_layout.addRow("Opération concernée:", self.cb_op)
        self.form_layout.addRow("Date Paiement:", self.txt_date)
        self.form_layout.addRow("Montant Versé:", self.val_verse)
        self.form_layout.addRow("Mode de Paiement:", self.txt_mode)
        self.form_layout.addRow("Référence Paiement:", self.txt_ref)
        self.form_layout.addRow("Observations:", self.txt_obs)

        if record:
            idx = self.cb_op.findData(record.get('id_operation'))
            if idx >= 0:
                self.cb_op.setCurrentIndex(idx)
            self.txt_date.setDate(QDate.fromString(str(record.get('date_paiement')), "yyyy-MM-dd"))
            self.val_verse.setValue(float(record.get('montant_verse', 0.0) or 0.0))
            self.txt_mode.setText(record.get('mode_paiement', 'ESPECES'))
            self.txt_ref.setText(record.get('reference_paiement', ''))
            self.txt_obs.setPlainText(record.get('observations', '') or '')
        else:
            if id_operation:
                idx = self.cb_op.findData(id_operation)
                if idx >= 0:
                    self.cb_op.setCurrentIndex(idx)

    def load_operations(self, id_partenaire=None):
        if id_partenaire:
            ops = data_manager.partenaires.get_operations_list_by_partner(id_partenaire)
        else:
            ops = data_manager.partenaires.get_operations_list()
            
        for o in ops:
            label = f"{o['nom_partenaire']} - {o['date_operation']} ({o['montant_total']:.2f} DZD)"
            self.cb_op.addItem(label, o['id_operation'])

    def save_data(self):
        op_id = self.cb_op.currentData()
        if not op_id:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord enregistrer des opérations.")
            return
            
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Paiements_Partenaires", "id_paiement", self.record['id_paiement'],
                {
                    "id_operation": op_id,
                    "date_paiement": date_str,
                    "montant_verse": self.val_verse.value(),
                    "mode_paiement": self.txt_mode.text().strip(),
                    "reference_paiement": self.txt_ref.text().strip(),
                    "observations": self.txt_obs.toPlainText().strip()
                }
            )
        else:
            success = data_manager.partenaires.add_paiement(
                op_id, date_str, self.val_verse.value(),
                self.txt_mode.text().strip(), self.txt_ref.text().strip(), self.txt_obs.toPlainText().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")
