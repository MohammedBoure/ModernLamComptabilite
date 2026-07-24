from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDoubleSpinBox, QLineEdit, QDialogButtonBox, QComboBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
from database import data_manager

class FichePaieDialog(QDialog):
    def __init__(self, parent=None, emp_id=None, emp_name=None, base_salary=0.0, data_row=None):
        super().__init__(parent)
        self.setWindowTitle(f"Fiche de Paie - {emp_name}")
        self.setMinimumWidth(400)
        self.base_salary = base_salary
        self.emp_id = emp_id
        
        self.setup_ui()
        if data_row:
            self.load_data(data_row)
            
        self.calculate_final()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.spin_hs = self.create_spin()
        self.spin_deplacement = self.create_spin()
        self.spin_gn = self.create_spin()
        self.spin_gvj = self.create_spin()
        self.spin_gvn = self.create_spin()
        self.spin_absence = self.create_spin()
        self.spin_prime = self.create_spin()
        self.spin_conge = self.create_spin()
        self.spin_penalite = self.create_spin()
        self.spin_avance = self.create_spin()
        self.txt_remarque = QLineEdit()
        
        lbl_base = QLabel(f"<b>{self.base_salary:.2f} DA</b>")
        form_layout.addRow("Salaire de Base:", lbl_base)
        form_layout.addRow("Présence en + / HS (+):", self.spin_hs)
        form_layout.addRow("Déplacement LAM (+):", self.spin_deplacement)
        form_layout.addRow("Garde Nuit (+):", self.spin_gn)
        form_layout.addRow("Garde Ven - Jour (+):", self.spin_gvj)
        form_layout.addRow("Garde Ven - Nuit (+):", self.spin_gvn)
        form_layout.addRow("Prime (+):", self.spin_prime)
        form_layout.addRow("Congé (+):", self.spin_conge)
        
        # Separator
        sep = QLabel("<b>DÉDUCTIONS</b>")
        sep.setStyleSheet("color: red; margin-top: 10px;")
        form_layout.addRow(sep)
        
        form_layout.addRow("Absence (-):", self.spin_absence)
        form_layout.addRow("Pénalités (-):", self.spin_penalite)
        form_layout.addRow("Avances (-):", self.spin_avance)
        
        form_layout.addRow("Remarque:", self.txt_remarque)
        
        self.lbl_final = QLabel("<b>0.00 DA</b>")
        self.lbl_final.setStyleSheet("font-size: 16px; color: #1565c0;")
        form_layout.addRow("<b>SALAIRE FINAL:</b>", self.lbl_final)
        
        layout.addLayout(form_layout)
        
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def create_spin(self):
        spin = QDoubleSpinBox()
        spin.setMaximum(9999999.0)
        spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spin.valueChanged.connect(self.calculate_final)
        return spin
        
    def load_data(self, r):
        self.spin_hs.setValue(float(r.get('heures_sup_montant', 0)))
        self.spin_deplacement.setValue(float(r.get('deplacement', 0)))
        self.spin_gn.setValue(float(r.get('garde_nuit', 0)))
        self.spin_gvj.setValue(float(r.get('garde_vendredi_jour', 0)))
        self.spin_gvn.setValue(float(r.get('garde_vendredi_nuit', 0)))
        self.spin_absence.setValue(float(r.get('retenue_absence', 0)))
        self.spin_prime.setValue(float(r.get('prime', 0)))
        self.spin_conge.setValue(float(r.get('conge', 0)))
        self.spin_penalite.setValue(float(r.get('penalites', 0)))
        self.spin_avance.setValue(float(r.get('avances', 0)))
        self.txt_remarque.setText(r.get('remarques', ''))

    def calculate_final(self):
        additions = (
            self.spin_hs.value() + self.spin_deplacement.value() +
            self.spin_gn.value() + self.spin_gvj.value() + self.spin_gvn.value() +
            self.spin_prime.value() + self.spin_conge.value()
        )
        deductions = (
            self.spin_absence.value() + self.spin_penalite.value() + self.spin_avance.value()
        )
        self.final_salary = self.base_salary + additions - deductions
        self.lbl_final.setText(f"<b>{self.final_salary:.2f} DA</b>")

    def get_data(self):
        return {
            'heures_sup_montant': self.spin_hs.value(),
            'deplacement': self.spin_deplacement.value(),
            'garde_nuit': self.spin_gn.value(),
            'garde_vendredi_jour': self.spin_gvj.value(),
            'garde_vendredi_nuit': self.spin_gvn.value(),
            'retenue_absence': self.spin_absence.value(),
            'prime': self.spin_prime.value(),
            'conge': self.spin_conge.value(),
            'penalites': self.spin_penalite.value(),
            'avances': self.spin_avance.value(),
            'net_a_payer': self.final_salary,
            'remarques': self.txt_remarque.text().strip()
        }


class SalairesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.month = None
        self.year = None
        self.current_matrix = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_edit = QPushButton("✎ Ajouter / Éditer Fiche de Paie")
        self.btn_edit.setStyleSheet("background-color: #2196f3; color: white; padding: 5px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_edit.clicked.connect(self.on_edit)
        
        self.btn_delete = QPushButton("🗑 Supprimer Salaire")
        self.btn_delete.setStyleSheet("background-color: #f44336; color: white; padding: 5px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_delete.clicked.connect(self.on_delete)
        
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)

        self.tbl_salaires = QTableWidget()
        self.tbl_salaires.setAlternatingRowColors(True)
        self.tbl_salaires.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_salaires.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_salaires.setSelectionMode(QTableWidget.SingleSelection)
        self.tbl_salaires.verticalHeader().setVisible(False)
        self.tbl_salaires.verticalHeader().setDefaultSectionSize(35)
        
        self.tbl_salaires.doubleClicked.connect(self.on_edit)
        
        layout.addWidget(self.tbl_salaires)
        
        # TOTAL Row Table
        self.tbl_totals = QTableWidget()
        self.tbl_totals.setRowCount(1)
        self.tbl_totals.setColumnCount(16)
        self.tbl_totals.horizontalHeader().setVisible(False)
        self.tbl_totals.verticalHeader().setVisible(False)
        self.tbl_totals.setFixedHeight(35)
        self.tbl_totals.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_totals.setSelectionMode(QTableWidget.NoSelection)
        self.tbl_totals.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tbl_totals.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tbl_totals.setFrameShape(QTableWidget.NoFrame)
        
        # Adding a simple top border using a QFrame line instead of stylesheet for better theming
        from PySide6.QtWidgets import QFrame
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        layout.addWidget(self.tbl_totals)
        
        # Sync scrollbars and column resizing
        self.tbl_salaires.horizontalScrollBar().valueChanged.connect(self.tbl_totals.horizontalScrollBar().setValue)
        self.tbl_salaires.horizontalHeader().sectionResized.connect(self.on_section_resized)

    def on_section_resized(self, logicalIndex, oldSize, newSize):
        self.tbl_totals.setColumnWidth(logicalIndex, newSize)

    def load_data_filtered(self, month=None, year=None):
        if month is not None:
            self.month = month
        if year is not None:
            self.year = year
            
        m = getattr(self, "month", None)
        y = getattr(self, "year", None)
        if not m or not y:
            m = QDate.currentDate().month() if not m else m
            y = QDate.currentDate().year() if not y else y
            
        headers = [
            "N°", "Personne", "Poste", "Salaire Net", "Présence en + / HS", 
            "Déplacement LAM", "Garde Nuit", "Garde Ven - Jour", "Garde Ven - Nuit", 
            "Absence", "Prime", "Congé", "Pénalités", "Avances", "Salaire", "REMARQUE"
        ]
        
        self.tbl_salaires.clear()
        self.tbl_salaires.setColumnCount(len(headers))
        self.tbl_salaires.setHorizontalHeaderLabels(headers)
        
        self.current_matrix = data_manager.hr.get_salaires_matrix(m, y)
        self.tbl_salaires.setRowCount(len(self.current_matrix))
        
        total_cols = [0.0] * 12 # [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        
        for row_idx, r in enumerate(self.current_matrix):
            item_n = QTableWidgetItem(str(r['id_employe']))
            item_n.setData(Qt.UserRole, row_idx) # Save row index to map to current_matrix
            item_n.setTextAlignment(Qt.AlignCenter)
            
            item_nom = QTableWidgetItem(str(r['nom_prenom']))
            item_poste = QTableWidgetItem(str(r['fonction'] or ''))
            
            val_base = float(r['salaire_base'] or 0)
            total_cols[0] += val_base
            item_base = QTableWidgetItem(f"{val_base:.2f}")
            item_base.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_base.setBackground(QColor("#f0f4c3")) 
            
            self.tbl_salaires.setItem(row_idx, 0, item_n)
            self.tbl_salaires.setItem(row_idx, 1, item_nom)
            self.tbl_salaires.setItem(row_idx, 2, item_poste)
            self.tbl_salaires.setItem(row_idx, 3, item_base)
            
            cols_map = [
                (4, 'heures_sup_montant'), (5, 'deplacement'), (6, 'garde_nuit'),
                (7, 'garde_vendredi_jour'), (8, 'garde_vendredi_nuit'),
                (9, 'retenue_absence'), (10, 'prime'), (11, 'conge'),
                (12, 'penalites'), (13, 'avances')
            ]
            
            for col_idx, key in cols_map:
                val = float(r[key] or 0)
                total_cols[col_idx - 3] += val
                item = QTableWidgetItem(f"{val:.2f}" if val > 0 else "")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tbl_salaires.setItem(row_idx, col_idx, item)
                
            val_final = float(r['net_a_payer'] or 0)
            total_cols[11] += val_final
            item_final = QTableWidgetItem(f"{val_final:.2f}")
            item_final.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_final.setBackground(QColor("#bbdefb")) 
            font_final = QFont()
            font_final.setBold(True)
            item_final.setFont(font_final)
            self.tbl_salaires.setItem(row_idx, 14, item_final)
            
            item_rem = QTableWidgetItem(str(r['remarques'] or ''))
            self.tbl_salaires.setItem(row_idx, 15, item_rem)

        self.tbl_salaires.resizeColumnsToContents()
        
        # Populate totals table
        self.tbl_totals.clear()
        
        font_total = self.tbl_totals.font()
        font_total.setBold(True)
        
        item_lbl = QTableWidgetItem("TOTAL :")
        item_lbl.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item_lbl.setFont(font_total)
        self.tbl_totals.setItem(0, 2, item_lbl)
        
        for i, val in enumerate(total_cols):
            col_idx = 3 + i
            item_val = QTableWidgetItem(f"{val:.2f}")
            item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_val.setFont(font_total)
            self.tbl_totals.setItem(0, col_idx, item_val)
            
        # Match column widths exactly
        for i in range(16):
            self.tbl_totals.setColumnWidth(i, self.tbl_salaires.columnWidth(i))
            
        # Add padding to tbl_totals to account for tbl_salaires vertical scrollbar!
        scroll_width = self.tbl_salaires.verticalScrollBar().width() if self.tbl_salaires.verticalScrollBar().isVisible() else 20
        self.tbl_totals.setContentsMargins(0, 0, scroll_width, 0)

    def on_edit(self):
        selected = self.tbl_salaires.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un employé.")
            return
            
        row = selected[0].row()
        matrix_idx = self.tbl_salaires.item(row, 0).data(Qt.UserRole)
        data = self.current_matrix[matrix_idx]
        
        dialog = FichePaieDialog(
            self, 
            emp_id=data['id_employe'], 
            emp_name=data['nom_prenom'], 
            base_salary=float(data['salaire_base']), 
            data_row=data
        )
        
        if dialog.exec():
            res = dialog.get_data()
            m = getattr(self, "month", QDate.currentDate().month())
            y = getattr(self, "year", QDate.currentDate().year())
            
            success = data_manager.hr.add_fiche_paie(
                id_employe=data['id_employe'], mois=m, annee=y,
                prime=res['prime'], deplacement=res['deplacement'], garde_nuit=res['garde_nuit'],
                garde_vendredi_jour=res['garde_vendredi_jour'], garde_vendredi_nuit=res['garde_vendredi_nuit'],
                heures_sup_montant=res['heures_sup_montant'], conge=res['conge'], 
                retenue_absence=res['retenue_absence'], penalites=res['penalites'], 
                avances=res['avances'], net_a_payer=res['net_a_payer'], remarques=res['remarques']
            )
            if success:
                self.load_data_filtered()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

    def on_delete(self):
        selected = self.tbl_salaires.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un employé.")
            return
            
        row = selected[0].row()
        matrix_idx = self.tbl_salaires.item(row, 0).data(Qt.UserRole)
        data = self.current_matrix[matrix_idx]
        
        # Only delete if there's actually a fiche de paie (e.g. net_a_payer is different from base_salary, or we just call delete anyway)
        reply = QMessageBox.question(self, "Confirmation", f"Êtes-vous sûr de vouloir réinitialiser la fiche de paie de {data['nom_prenom']} pour ce mois ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            m = getattr(self, "month", QDate.currentDate().month())
            y = getattr(self, "year", QDate.currentDate().year())
            data_manager.hr.delete_fiche_paie(data['id_employe'], m, y)
            self.load_data_filtered()
