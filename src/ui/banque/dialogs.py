from PySide6.QtWidgets import QMessageBox, QLineEdit, QDoubleSpinBox, QDateEdit, QTextEdit, QSpinBox, QComboBox
from PySide6.QtCore import QDate
from ui.base_dialog import BaseDialog
from database import data_manager

class VehiculeServiceDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Suivi Véhicule" if record else "Nouveau Suivi Véhicule", parent)
        self.record = record
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.val_km = QSpinBox()
        self.val_km.setMaximum(99999999)
        
        self.val_carburant = QDoubleSpinBox()
        self.val_carburant.setMaximum(999999.0)
        
        self.cb_type = QComboBox()
        self.cb_type.addItems(["GPL", "ESSENCE"])
        
        self.txt_details = QTextEdit()
        self.txt_details.setMaximumHeight(80)
        
        self.form_layout.addRow("Date Suivi:", self.txt_date)
        self.form_layout.addRow("Kilométrage (KM):", self.val_km)
        self.form_layout.addRow("Montant Carburant:", self.val_carburant)
        self.form_layout.addRow("Type Carburant:", self.cb_type)
        self.form_layout.addRow("Détails / Remarques:", self.txt_details)

        if record:
            self.txt_date.setDate(QDate.fromString(str(record.get('date_suivi')), "yyyy-MM-dd"))
            self.val_km.setValue(int(record.get('kilometrage', 0) or 0))
            self.val_carburant.setValue(float(record.get('montant_carburant', 0.0) or 0.0))
            self.cb_type.setCurrentText(str(record.get('type_carburant', 'GPL')))
            self.txt_details.setPlainText(record.get('details', '') or '')

    def save_data(self):
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            if self.record.get('id_transaction_coffre'):
                data_manager.db.update_record(
                    "Mouvement_Coffre", "id_transaction", self.record['id_transaction_coffre'],
                    {
                        "date_transaction": date_str,
                        "montant": self.val_carburant.value(),
                        "designation": f"Carburant {self.cb_type.currentText()} ({self.val_km.value()} km) - {self.txt_details.toPlainText().strip()}"
                    }
                )
            success, _ = data_manager.db.update_record(
                "Vehicule_Service", "id_suivi", self.record['id_suivi'],
                {
                    "date_suivi": date_str,
                    "kilometrage": self.val_km.value(),
                    "montant_carburant": self.val_carburant.value(),
                    "type_carburant": self.cb_type.currentText(),
                    "details": self.txt_details.toPlainText().strip()
                }
            )
        else:
            success = data_manager.banque.add_vehicule_log(
                date_str, self.val_km.value(), self.val_carburant.value(),
                self.cb_type.currentText(), self.txt_details.toPlainText().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class CompteSGADialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Transaction Compte SGA" if record else "Nouvelle Transaction Compte SGA", parent)
        self.record = record
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.txt_cheque = QLineEdit()
        self.txt_beneficiaire = QLineEdit()
        
        self.val_entrees = QDoubleSpinBox()
        self.val_entrees.setMaximum(999999999.0)
        
        self.val_sorties = QDoubleSpinBox()
        self.val_sorties.setMaximum(999999999.0)
        
        self.txt_designation = QTextEdit()
        self.txt_designation.setMaximumHeight(80)
        
        self.form_layout.addRow("Date Transaction:", self.txt_date)
        self.form_layout.addRow("Numéro Chèque:", self.txt_cheque)
        self.form_layout.addRow("Bénéficiaire:", self.txt_beneficiaire)
        self.form_layout.addRow("Entrées (Dépôt):", self.val_entrees)
        self.form_layout.addRow("Sorties (Paiement):", self.val_sorties)
        self.form_layout.addRow("Désignation / Motif:", self.txt_designation)

        if record:
            self.txt_date.setDate(QDate.fromString(str(record.get('date_transaction')), "yyyy-MM-dd"))
            self.txt_cheque.setText(record.get('n_cheque', '') or '')
            self.txt_beneficiaire.setText(record.get('beneficiaire', '') or '')
            self.val_entrees.setValue(float(record.get('entrees', 0.0) or 0.0))
            self.val_sorties.setValue(float(record.get('sorties', 0.0) or 0.0))
            self.txt_designation.setPlainText(record.get('designation', '') or '')

    def save_data(self):
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Compte_SGA", "id_transaction", self.record['id_transaction'],
                {
                    "date_transaction": date_str,
                    "n_cheque": self.txt_cheque.text().strip(),
                    "beneficiaire": self.txt_beneficiaire.text().strip(),
                    "entrees": self.val_entrees.value(),
                    "sorties": self.val_sorties.value(),
                    "designation": self.txt_designation.toPlainText().strip()
                }
            )
        else:
            success = data_manager.banque.add_sga_transaction(
                date_str, self.txt_cheque.text().strip(), self.txt_beneficiaire.text().strip(),
                self.val_entrees.value(), self.val_sorties.value(), self.txt_designation.toPlainText().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class EtatEncaissementDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Encaissement" if record else "Nouvel Encaissement", parent)
        self.record = record
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.txt_des = QLineEdit("DIVERS CLIENTS")
        self.val_montant = QDoubleSpinBox()
        self.val_montant.setMaximum(999999999.0)
        
        self.txt_obs = QTextEdit()
        self.txt_obs.setMaximumHeight(80)
        
        self.form_layout.addRow("Date d'Encaissement:", self.txt_date)
        self.form_layout.addRow("Désignation / Client:", self.txt_des)
        self.form_layout.addRow("Montant Encaissement:", self.val_montant)
        self.form_layout.addRow("Observations:", self.txt_obs)

        if record:
            self.txt_date.setDate(QDate.fromString(str(record.get('date_encaissement')), "yyyy-MM-dd"))
            self.txt_des.setText(record.get('designation', ''))
            self.val_montant.setValue(float(record.get('montant', 0.0) or 0.0))
            self.txt_obs.setPlainText(record.get('observations', '') or '')

    def save_data(self):
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Etat_Encaissement", "id_encaissement", self.record['id_encaissement'],
                {
                    "date_encaissement": date_str,
                    "designation": self.txt_des.text().strip(),
                    "montant": self.val_montant.value(),
                    "observations": self.txt_obs.toPlainText().strip()
                }
            )
        else:
            success = data_manager.banque.add_encaissement(
                date_str, self.txt_des.text().strip(), self.val_montant.value(), self.txt_obs.toPlainText().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")
