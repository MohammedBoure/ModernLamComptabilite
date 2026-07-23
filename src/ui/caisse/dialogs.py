from PySide6.QtWidgets import QMessageBox, QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit
from PySide6.QtCore import QDate
from ui.base_dialog import BaseDialog
from database import data_manager

class MouvementCaisseDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Mouvement Caisse" if record else "Nouveau Mouvement Caisse", parent)
        self.record = record
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.val_caisse_cv = QDoubleSpinBox()
        self.val_caisse_cv.setMaximum(999999999.0)
        
        self.val_caisse_c = QDoubleSpinBox()
        self.val_caisse_c.setMaximum(999999999.0)
        
        self.val_tpe = QDoubleSpinBox()
        self.val_tpe.setMaximum(999999999.0)
        
        self.val_depenses = QDoubleSpinBox()
        self.val_depenses.setMaximum(999999999.0)
        
        self.val_remboursement = QDoubleSpinBox()
        self.val_remboursement.setMaximum(999999999.0)
        
        self.val_convention = QDoubleSpinBox()
        self.val_convention.setMaximum(999999999.0)
        
        self.val_sous_traitants = QDoubleSpinBox()
        self.val_sous_traitants.setMaximum(999999999.0)
        
        self.form_layout.addRow("Date:", self.txt_date)
        self.form_layout.addRow("Caisse CV:", self.val_caisse_cv)
        self.form_layout.addRow("Caisse C:", self.val_caisse_c)
        self.form_layout.addRow("TPE:", self.val_tpe)
        self.form_layout.addRow("Dépenses:", self.val_depenses)
        self.form_layout.addRow("Remboursement:", self.val_remboursement)
        self.form_layout.addRow("Convention Mutuelle:", self.val_convention)
        self.form_layout.addRow("Sous-Traitants:", self.val_sous_traitants)

        if record:
            self.txt_date.setDate(QDate.fromString(str(record.get('date_mouvement')), "yyyy-MM-dd"))
            self.txt_date.setEnabled(False)
            self.val_caisse_cv.setValue(float(record.get('caisse_cv', 0.0) or 0.0))
            self.val_caisse_c.setValue(float(record.get('caisse_c', 0.0) or 0.0))
            self.val_tpe.setValue(float(record.get('tpe', 0.0) or 0.0))
            self.val_depenses.setValue(float(record.get('depenses', 0.0) or 0.0))
            self.val_remboursement.setValue(float(record.get('remboursement', 0.0) or 0.0))
            self.val_convention.setValue(float(record.get('convention', 0.0) or 0.0))
            self.val_sous_traitants.setValue(float(record.get('sous_traitants', 0.0) or 0.0))

    def save_data(self):
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Mouvement_Caisse", "date_mouvement", date_str,
                {
                    "caisse_cv": self.val_caisse_cv.value(),
                    "caisse_c": self.val_caisse_c.value(),
                    "tpe": self.val_tpe.value(),
                    "depenses": self.val_depenses.value(),
                    "remboursement": self.val_remboursement.value(),
                    "convention": self.val_convention.value(),
                    "sous_traitants": self.val_sous_traitants.value()
                }
            )
        else:
            success = data_manager.caisse.add_caisse_movement(
                date_str, self.val_caisse_cv.value(), self.val_caisse_c.value(),
                self.val_tpe.value(), self.val_depenses.value(), self.val_remboursement.value(),
                self.val_convention.value(), self.val_sous_traitants.value()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class DepenseCaisseDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Dépense Caisse" if record else "Ajouter Dépense Caisse", parent)
        self.record = record
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.txt_designation = QLineEdit()
        
        self.val_montant = QDoubleSpinBox()
        self.val_montant.setMaximum(999999999.0)
        
        self.form_layout.addRow("Date:", self.txt_date)
        self.form_layout.addRow("Désignation:", self.txt_designation)
        self.form_layout.addRow("Montant:", self.val_montant)

        if record:
            self.txt_date.setDate(QDate.fromString(str(record.get('date_mouvement')), "yyyy-MM-dd"))
            self.txt_designation.setText(record.get('designation', ''))
            self.val_montant.setValue(float(record.get('montant', 0.0) or 0.0))

    def save_data(self):
        if not self.txt_designation.text().strip():
            QMessageBox.warning(self, "Attention", "La désignation est requise.")
            return
            
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Details_Depenses_Caisse", "id_depense_caisse", self.record['id_depense_caisse'],
                {
                    "date_mouvement": date_str,
                    "designation": self.txt_designation.text().strip(),
                    "montant": self.val_montant.value()
                }
            )
        else:
            success = data_manager.caisse.add_depense_caisse(
                date_str, self.txt_designation.text().strip(), self.val_montant.value()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class ClotureCaisseDialog(BaseDialog):
    def __init__(self, parent=None, record=None):
        super().__init__("Modifier Clôture Caisse" if record else "Nouvelle Clôture Caisse", parent)
        self.record = record
        
        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.cb_user = QComboBox()
        self.load_employes()
        
        self.val_reel = QDoubleSpinBox()
        self.val_reel.setMaximum(999999999.0)
        
        self.val_virtuel = QDoubleSpinBox()
        self.val_virtuel.setMaximum(999999999.0)
        
        self.txt_remarques = QTextEdit()
        self.txt_remarques.setMaximumHeight(80)
        
        self.form_layout.addRow("Date de Clôture:", self.txt_date)
        self.form_layout.addRow("Utilisateur:", self.cb_user)
        self.form_layout.addRow("Montant Réel:", self.val_reel)
        self.form_layout.addRow("Montant Virtuel:", self.val_virtuel)
        self.form_layout.addRow("Remarques:", self.txt_remarques)

        if record:
            self.txt_date.setDate(QDate.fromString(str(record.get('date_cloture')), "yyyy-MM-dd"))
            self.cb_user.setCurrentText(str(record.get('utilisateur', '')))
            self.val_reel.setValue(float(record.get('montant_reel', 0.0) or 0.0))
            self.val_virtuel.setValue(float(record.get('montant_virtuel', 0.0) or 0.0))
            self.txt_remarques.setPlainText(record.get('remarques', '') or '')

    def load_employes(self):
        employes = data_manager.hr.get_employes_list()
        self.cb_user.addItem("") # Empty option first
        for emp in employes:
            self.cb_user.addItem(emp['nom_prenom'])

    def save_data(self):
        user_name = self.cb_user.currentText().strip()
        if not user_name:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un utilisateur.")
            return
            
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            # First ensure parent Mouvement_Caisse exists for that date (PK safety)
            data_manager.db.execute("INSERT IGNORE INTO Mouvement_Caisse (date_mouvement) VALUES (%s)", (date_str,))
            success, _ = data_manager.db.update_record(
                "Cloture_Caisse", "id_cloture", self.record['id_cloture'],
                {
                    "date_cloture": date_str,
                    "utilisateur": user_name,
                    "montant_reel": self.val_reel.value(),
                    "montant_virtuel": self.val_virtuel.value(),
                    "remarques": self.txt_remarques.toPlainText().strip()
                }
            )
        else:
            success = data_manager.caisse.add_cloture(
                date_str, user_name, 
                self.val_reel.value(), self.val_virtuel.value(), 
                self.txt_remarques.toPlainText().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

class MouvementCoffreDialog(BaseDialog):
    def __init__(self, parent=None, record=None, default_type="ENTREE"):
        super().__init__("Modifier Transaction Coffre" if record else "Nouvelle Transaction Coffre", parent)
        self.record = record
        
        if record:
            self.type_operation = str(record.get('type_operation', default_type))
            self.categorie_operation = str(record.get('categorie_operation', 'ENTREES_SUPP' if self.type_operation == 'ENTREE' else 'AUTRE_SORTIE'))
        else:
            self.type_operation = default_type
            self.categorie_operation = 'ENTREES_SUPP' if self.type_operation == 'ENTREE' else 'AUTRE_SORTIE'

        self.txt_date = QDateEdit()
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setCalendarPopup(True)
        
        self.val_montant = QDoubleSpinBox()
        self.val_montant.setMaximum(999999999.0)
        
        self.txt_des = QLineEdit()
        
        self.form_layout.addRow("Date Transaction:", self.txt_date)
        self.form_layout.addRow("Montant:", self.val_montant)
        self.form_layout.addRow("Désignation:", self.txt_des)

        if record:
            self.txt_date.setDate(QDate.fromString(str(record.get('date_transaction')), "yyyy-MM-dd"))
            self.val_montant.setValue(float(record.get('montant', 0.0) or 0.0))
            self.txt_des.setText(record.get('designation', ''))

    def save_data(self):
        if not self.txt_des.text().strip():
            QMessageBox.warning(self, "Attention", "La désignation est requise.")
            return
            
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        if self.record:
            success, _ = data_manager.db.update_record(
                "Mouvement_Coffre", "id_transaction", self.record['id_transaction'],
                {
                    "date_transaction": date_str,
                    "type_operation": self.type_operation,
                    "categorie_operation": self.categorie_operation,
                    "montant": self.val_montant.value(),
                    "designation": self.txt_des.text().strip()
                }
            )
        else:
            success = data_manager.caisse.add_coffre_movement(
                date_str, self.type_operation, self.categorie_operation,
                self.val_montant.value(), self.txt_des.text().strip()
            )
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

