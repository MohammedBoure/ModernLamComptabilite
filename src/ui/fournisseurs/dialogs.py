from PySide6.QtWidgets import QMessageBox, QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit, QTabWidget, QFormLayout, QWidget, QCheckBox
from PySide6.QtCore import QDate
from ui.base_dialog import BaseDialog
from database import data_manager
from database.base.stock_connector import load_stock_db_config, get_stock_db_suppliers

class FournisseurDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Fournisseur" if record else "Ajouter Fournisseur", parent)
        self.record = record
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
        self.val_solde = QDoubleSpinBox()
        self.val_solde.setMaximum(999999999.0)
        self.txt_agrement = QLineEdit()
        
        self.cb_stock_map = QComboBox()
        self.cb_stock_map.addItem("Aucun (Sans liaison)", None)
        self.load_stock_suppliers()
        
        self.chk_inclus_etat = QCheckBox("Inclus dans Etat Fournisseurs")
        self.chk_inclus_etat.setChecked(True)
        
        form_gen.addRow("Nom du Fournisseur:", self.txt_nom)
        form_gen.addRow("Solde Initial (Dette pr.):", self.val_solde)
        form_gen.addRow("Numéro d'Agrément:", self.txt_agrement)
        form_gen.addRow("Même fournisseur dans Stock:", self.cb_stock_map)
        form_gen.addRow("", self.chk_inclus_etat)
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
            self.txt_nom.setText(record.get('nom_fournisseur', '') or '')
            self.val_solde.setValue(float(record.get('solde_initial', 0.0) or 0.0))
            self.txt_agrement.setText(record.get('agrement_number', '') or '')
            self.chk_inclus_etat.setChecked(bool(record.get('inclus_etat', 1)))
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
            
            # Map stock supplier association
            stock_id = record.get('stock_supplier_id')
            if stock_id is not None:
                idx = self.cb_stock_map.findData(stock_id)
                if idx >= 0:
                    self.cb_stock_map.setCurrentIndex(idx)

    def load_stock_suppliers(self):
        try:
            config = load_stock_db_config()
            suppliers = get_stock_db_suppliers(config)
            for s in suppliers:
                self.cb_stock_map.addItem(s['Supplier_Name'], s['Supplier_ID'])
        except Exception as e:
            import logging
            logging.error(f"Error loading stock suppliers: {e}")

    def save_data(self):
        nom = self.txt_nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Attention", "Le nom est requis.")
            return
            
        data = {
            "nom_fournisseur": nom,
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
            "stock_supplier_id": self.cb_stock_map.currentData(),
            "inclus_etat": 1 if self.chk_inclus_etat.isChecked() else 0
        }
            
        if self.record:
            success, _ = data_manager.db.update_record(
                "Fournisseurs", "id_fournisseur", self.record['id_fournisseur'],
                data
            )
        else:
            success = data_manager.fournisseurs.add_fournisseur(data)
            
        if success:
            self.centralWidget = True
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class DepenseFournisseurDialog(BaseDialog):
    def __init__(self, parent=None, record=None, id_fournisseur=None, category_name=None):
        super().__init__("Modifier Facture/Commande Fournisseur" if record else "Ajouter Facture/Commande Fournisseur", parent)
        self.record = record
        
        self.cb_fr = QComboBox()
        self.load_fournisseurs()
        
        self.cb_cat = QComboBox()
        self.cb_cat.addItem("EQUIPEMENTS", 1)
        self.cb_cat.addItem("CONSOMMABLES", 2)
        
        self.txt_doc = QLineEdit("FACTURE")
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.val_montant = QDoubleSpinBox()
        self.val_montant.setMaximum(999999999.0)
        
        self.txt_mode = QLineEdit("VIREMENT")
        self.txt_obs = QTextEdit()
        self.txt_obs.setMaximumHeight(80)
        
        self.form_layout.addRow("Fournisseur:", self.cb_fr)
        self.form_layout.addRow("Catégorie:", self.cb_cat)
        self.form_layout.addRow("Type Document:", self.txt_doc)
        self.form_layout.addRow("Date Facture:", self.txt_date)
        self.form_layout.addRow("Montant Total:", self.val_montant)
        self.form_layout.addRow("Mode Paiement Préféré:", self.txt_mode)
        self.form_layout.addRow("Observations:", self.txt_obs)

        if record:
            idx = self.cb_fr.findData(record.get('id_fournisseur'))
            if idx >= 0:
                self.cb_fr.setCurrentIndex(idx)
            idx_cat = self.cb_cat.findData(record.get('id_categorie'))
            if idx_cat >= 0:
                self.cb_cat.setCurrentIndex(idx_cat)
            self.txt_doc.setText(record.get('type_document', 'FACTURE'))
            self.txt_date.setDate(QDate.fromString(str(record.get('date_facture')), "yyyy-MM-dd"))
            self.val_montant.setValue(float(record.get('montant_total', 0.0) or 0.0))
            self.txt_mode.setText(record.get('mode_paiement', 'VIREMENT'))
            self.txt_obs.setPlainText(record.get('observation', '') or '')
        else:
            if id_fournisseur:
                idx = self.cb_fr.findData(id_fournisseur)
                if idx >= 0:
                    self.cb_fr.setCurrentIndex(idx)
            if category_name:
                idx_cat = self.cb_cat.findText(category_name.upper())
                if idx_cat >= 0:
                    self.cb_cat.setCurrentIndex(idx_cat)

    def load_fournisseurs(self):
        frs = data_manager.fournisseurs.get_fournisseurs_list()
        for f in frs:
            self.cb_fr.addItem(f['nom_fournisseur'], f['id_fournisseur'])

    def save_data(self):
        fr_id = self.cb_fr.currentData()
        if not fr_id:
            QMessageBox.warning(self, "Attention", "Veuillez choisir un fournisseur enregistré dans Données de base.")
            return
            
        cat_name = self.cb_cat.currentText()
        cat_id = data_manager.fournisseurs.ensure_category_exists(cat_name)
        
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Depenses_Achats", "id_depense", self.record['id_depense'],
                {
                    "id_fournisseur": fr_id,
                    "id_categorie": cat_id,
                    "type_document": self.txt_doc.text().strip(),
                    "date_facture": date_str,
                    "montant_total": self.val_montant.value(),
                    "mode_paiement": self.txt_mode.text().strip(),
                    "observation": self.txt_obs.toPlainText().strip()
                }
            )
        else:
            success = data_manager.fournisseurs.add_depense(
                fr_id, cat_id, self.txt_doc.text().strip(), date_str, 
                self.val_montant.value(), self.txt_mode.text().strip(), self.txt_obs.toPlainText().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class PaiementFournisseurDialog(BaseDialog):
    def __init__(self, parent=None, record=None, id_fournisseur=None, id_depense=None, month=None, year=None):
        super().__init__("Modifier Paiement Fournisseur" if record else "Enregistrer Paiement Fournisseur", parent)
        self.record = record
        self.month = month
        self.year = year
        self.depenses_map = {}
        
        self.cb_depense = QComboBox()
        self.load_depenses(id_fournisseur, month, year)
        self.cb_depense.currentIndexChanged.connect(self.on_depense_changed)
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.val_verse = QDoubleSpinBox()
        self.val_verse.setMaximum(999999999.0)
        
        self.txt_mode = QLineEdit("CHEQUE")
        self.txt_ref = QLineEdit()
        self.txt_obs = QTextEdit()
        self.txt_obs.setMaximumHeight(80)
        
        self.form_layout.addRow("Facture/Commande concernée:", self.cb_depense)
        self.form_layout.addRow("Date Paiement:", self.txt_date)
        self.form_layout.addRow("Montant Versé:", self.val_verse)
        self.form_layout.addRow("Mode de Paiement:", self.txt_mode)
        self.form_layout.addRow("Référence/Numéro Chèque:", self.txt_ref)
        self.form_layout.addRow("Observations:", self.txt_obs)

        if record:
            idx = self.cb_depense.findData(record.get('id_depense'))
            if idx >= 0:
                self.cb_depense.setCurrentIndex(idx)
            self.txt_date.setDate(QDate.fromString(str(record.get('date_paiement')), "yyyy-MM-dd"))
            self.val_verse.setValue(float(record.get('montant_verse', 0.0) or 0.0))
            self.txt_mode.setText(record.get('mode_paiement', 'CHEQUE'))
            self.txt_ref.setText(record.get('reference_paiement', ''))
            self.txt_obs.setPlainText(record.get('observations', '') or '')
        else:
            if id_depense:
                idx = self.cb_depense.findData(id_depense)
                if idx >= 0:
                    self.cb_depense.setCurrentIndex(idx)
            self.on_depense_changed()

    def load_depenses(self, id_fournisseur=None, month=None, year=None):
        if id_fournisseur:
            depenses = data_manager.fournisseurs.get_depenses_list_by_supplier(id_fournisseur, month, year)
        else:
            depenses = data_manager.fournisseurs.get_depenses_list(month, year)
            
        self.cb_depense.clear()
        self.depenses_map = {}
        
        for d in depenses:
            doc_type = d.get('type_document', 'FACTURE')
            date_str = str(d.get('date_facture', ''))
            total = float(d.get('montant_total', 0.0) or 0.0)
            reste = float(d.get('reste', 0.0) or 0.0)
            id_d = d['id_depense']
            
            label = f"{d['nom_fournisseur']} - {doc_type} du {date_str} | Total: {total:,.2f} DA | Reste à payer: {reste:,.2f} DA"
            self.cb_depense.addItem(label, id_d)
            self.depenses_map[id_d] = reste

    def on_depense_changed(self):
        if not self.record:
            id_d = self.cb_depense.currentData()
            if id_d in self.depenses_map:
                self.val_verse.setValue(self.depenses_map[id_d])

    def save_data(self):
        dep_id = self.cb_depense.currentData()
        if not dep_id:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord enregistrer des factures/commandes.")
            return
            
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Paiements_Fournisseurs", "id_paiement", self.record['id_paiement'],
                {
                    "id_depense": dep_id,
                    "date_paiement": date_str,
                    "montant_verse": self.val_verse.value(),
                    "mode_paiement": self.txt_mode.text().strip(),
                    "reference_paiement": self.txt_ref.text().strip(),
                    "observations": self.txt_obs.toPlainText().strip()
                }
            )
        else:
            success = data_manager.fournisseurs.add_paiement(
                dep_id, date_str, self.val_verse.value(), 
                self.txt_mode.text().strip(), self.txt_ref.text().strip(), self.txt_obs.toPlainText().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")
