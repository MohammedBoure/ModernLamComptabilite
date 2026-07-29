from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDoubleSpinBox, QLineEdit, QDialogButtonBox, QDateEdit, QComboBox, QInputDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
from database import data_manager

class CompteSGADialog(QDialog):
    def __init__(self, parent=None, transaction_id=None, data_row=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie de Chèque / Opération Bancaire")
        self.setMinimumWidth(450)
        self.transaction_id = transaction_id
        self.setup_ui()
        if data_row:
            self.load_data(data_row)
        else:
            self.date_edit.setDate(QDate.currentDate())

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("La Date :", self.date_edit)

        self.txt_beneficiaire = QLineEdit()
        form_layout.addRow("Bénéficiaire :", self.txt_beneficiaire)

        self.txt_cheque = QLineEdit()
        form_layout.addRow("N° Chèque :", self.txt_cheque)
        
        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["SORTIE (Débit)", "ENTRÉE (Crédit)"])
        form_layout.addRow("Type d'opération :", self.cmb_type)

        self.spin_montant = QDoubleSpinBox()
        self.spin_montant.setMaximum(999999999.0)
        self.spin_montant.setButtonSymbols(QDoubleSpinBox.NoButtons)
        form_layout.addRow("Montant :", self.spin_montant)

        self.txt_designation = QLineEdit()
        form_layout.addRow("Désignation :", self.txt_designation)

        layout.addLayout(form_layout)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def load_data(self, r):
        # We need to parse the date from string or directly if it's a date object
        date_str = str(r.get('date_transaction', ''))
        d = QDate.fromString(date_str, "yyyy-MM-dd")
        if d.isValid():
            self.date_edit.setDate(d)
            
        self.txt_beneficiaire.setText(r.get('beneficiaire') or '')
        self.txt_cheque.setText(r.get('n_cheque') or '')
        
        entrees = float(r.get('entrees') or 0)
        sorties = float(r.get('sorties') or 0)
        
        if entrees > 0:
            self.cmb_type.setCurrentIndex(1) # Entrée
            self.spin_montant.setValue(entrees)
        else:
            self.cmb_type.setCurrentIndex(0) # Sortie
            self.spin_montant.setValue(sorties)
            
        self.txt_designation.setText(r.get('designation') or '')

    def get_data(self):
        is_entree = (self.cmb_type.currentIndex() == 1)
        montant = self.spin_montant.value()
        return {
            'date_transaction': self.date_edit.date().toString("yyyy-MM-dd"),
            'n_cheque': self.txt_cheque.text().strip(),
            'beneficiaire': self.txt_beneficiaire.text().strip(),
            'entrees': montant if is_entree else 0.0,
            'sorties': 0.0 if is_entree else montant,
            'designation': self.txt_designation.text().strip()
        }


class CompteSGATab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_matrix = []
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        self.selected_year = QDate.currentDate().year()

        # Annual SGA balance and its transactions are deliberately scoped to one fiscal year.
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel()
        self.lbl_title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.lbl_title.setFont(title_font)
        self.lbl_title.setStyleSheet("color: #1565c0; margin-bottom: 10px;")
        self.cmb_year = QComboBox()
        for year in range(self.selected_year - 2, self.selected_year + 3):
            self.cmb_year.addItem(str(year), year)
        self.cmb_year.setCurrentText(str(self.selected_year))
        self.cmb_year.currentIndexChanged.connect(self.on_year_changed)
        header_layout.addWidget(self.lbl_title, 1)
        header_layout.addWidget(QLabel("AnnÃ©e :"))
        header_layout.addWidget(self.cmb_year)
        layout.addLayout(header_layout)

        # Initial Balance Row
        initial_layout = QHBoxLayout()
        self.lbl_initial = QLabel()
        self.lbl_initial.setFont(QFont("Arial", 10, QFont.Bold))
        self.spin_initial = QDoubleSpinBox()
        self.spin_initial.setMaximum(999999999.0)
        self.spin_initial.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.spin_initial.setMinimumWidth(150)
        
        btn_update_initial = QPushButton("Mettre à jour")
        btn_update_initial.setStyleSheet("background-color: #78909c; color: white; border-radius: 4px; padding: 4px 10px;")
        btn_update_initial.clicked.connect(self.on_update_initial)
        
        initial_layout.addWidget(self.lbl_initial)
        initial_layout.addWidget(self.spin_initial)
        initial_layout.addWidget(btn_update_initial)
        initial_layout.addStretch()
        layout.addLayout(initial_layout)

        # Current Balance Row
        today_str = QDate.currentDate().toString("dd/MM/yyyy")
        current_layout = QHBoxLayout()
        lbl_current = QLabel(f"Montant du Compte Le {today_str} :")
        lbl_current.setFont(QFont("Arial", 10, QFont.Bold))
        self.lbl_solde_actuel = QLabel("0.00 DA")
        self.lbl_solde_actuel.setFont(QFont("Arial", 12, QFont.Bold))
        self.lbl_solde_actuel.setStyleSheet("color: #2e7d32; padding: 5px; background: #e8f5e9; border: 1px solid #81c784; border-radius: 4px;")
        current_layout.addWidget(lbl_current)
        current_layout.addWidget(self.lbl_solde_actuel)
        current_layout.addStretch()
        layout.addLayout(current_layout)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("+ Nouveau Chèque / Opération")
        self.btn_add.setStyleSheet("background-color: #4caf50; color: white; padding: 6px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_add.clicked.connect(self.on_add)
        
        self.btn_edit = QPushButton("✎ Modifier")
        self.btn_edit.setStyleSheet("background-color: #2196f3; color: white; padding: 6px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_edit.clicked.connect(self.on_edit)
        
        self.btn_delete = QPushButton("🗑 Supprimer")
        self.btn_delete.setStyleSheet("background-color: #f44336; color: white; padding: 6px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_delete.clicked.connect(self.on_delete)
        
        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Grid
        self.tbl_banque = QTableWidget()
        self.tbl_banque.setColumnCount(8)
        self.tbl_banque.setHorizontalHeaderLabels(["N°", "La Date", "Bénéficiaire", "N° Chèque", "Montant", "Entrées", "Sorties", "Désignation"])
        self.tbl_banque.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tbl_banque.horizontalHeader().setStretchLastSection(True)
        self.tbl_banque.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_banque.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_banque.setSelectionMode(QTableWidget.SingleSelection)
        self.tbl_banque.verticalHeader().setVisible(False)
        self.tbl_banque.verticalHeader().setDefaultSectionSize(35)
        self.tbl_banque.setAlternatingRowColors(True)
        
        self.tbl_banque.doubleClicked.connect(self.on_edit)
        
        layout.addWidget(self.tbl_banque)

    def on_year_changed(self):
        self.selected_year = int(self.cmb_year.currentData())
        self.load_data()

    def load_data(self):
        selected_year = self.selected_year
        self.lbl_title.setText(f"Etat de ChÃ¨que AnnÃ©e {selected_year}")
        self.lbl_initial.setText(f"Montant du Compte au 31/12/{selected_year - 1} :")
        # Load balances for the selected fiscal year.
        initial = data_manager.banque.get_solde_initial(selected_year)
        self.spin_initial.blockSignals(True)
        self.spin_initial.setValue(initial)
        self.spin_initial.blockSignals(False)
        
        actuel = data_manager.banque.get_solde_actuel(selected_year)
        self.lbl_solde_actuel.setText(f"{actuel:,.2f} DA".replace(",", " "))

        # Load grid
        self.current_matrix = data_manager.banque.get_sga_transactions(selected_year)
        self.tbl_banque.setRowCount(len(self.current_matrix))
        
        for i, row in enumerate(self.current_matrix):
            item_id = QTableWidgetItem(str(row['id_transaction']))
            item_id.setData(Qt.UserRole, i) # Store index to matrix
            item_id.setTextAlignment(Qt.AlignCenter)
            
            entrees = float(row.get('entrees') or 0)
            sorties = float(row.get('sorties') or 0)
            montant = max(entrees, sorties)
            
            # Format numbers
            str_montant = f"{montant:.2f}" if montant > 0 else "-"
            str_entrees = f"{entrees:.2f}" if entrees > 0 else "-"
            str_sorties = f"{sorties:.2f}" if sorties > 0 else "-"
            
            item_montant = QTableWidgetItem(str_montant)
            item_entrees = QTableWidgetItem(str_entrees)
            item_sorties = QTableWidgetItem(str_sorties)
            
            item_montant.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_entrees.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_sorties.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            if entrees > 0:
                item_entrees.setForeground(QColor("#2e7d32")) # Green for entries
            if sorties > 0:
                item_sorties.setForeground(QColor("#c62828")) # Red for exits
            
            self.tbl_banque.setItem(i, 0, item_id)
            self.tbl_banque.setItem(i, 1, QTableWidgetItem(str(row['date_transaction'])))
            self.tbl_banque.setItem(i, 2, QTableWidgetItem(str(row['beneficiaire'] or '')))
            self.tbl_banque.setItem(i, 3, QTableWidgetItem(str(row['n_cheque'] or '')))
            self.tbl_banque.setItem(i, 4, item_montant)
            self.tbl_banque.setItem(i, 5, item_entrees)
            self.tbl_banque.setItem(i, 6, item_sorties)
            self.tbl_banque.setItem(i, 7, QTableWidgetItem(str(row['designation'] or '')))
            
        if self.tbl_banque.rowCount() > 0:
            self.tbl_banque.resizeColumnsToContents()
            self.tbl_banque.setColumnWidth(2, 200) # Beneficiaire
            self.tbl_banque.setColumnWidth(7, 250) # Designation

    def on_update_initial(self):
        val = self.spin_initial.value()
        success = data_manager.banque.update_solde_initial(val, self.selected_year)
        if success:
            self.load_data()
        else:
            QMessageBox.critical(self, "Erreur", "Impossible de mettre à jour le solde initial.")

    def on_add(self):
        dlg = CompteSGADialog(self)
        if dlg.exec():
            res = dlg.get_data()
            success = data_manager.banque.add_sga_transaction(
                date_transaction=res['date_transaction'],
                n_cheque=res['n_cheque'],
                beneficiaire=res['beneficiaire'],
                entrees=res['entrees'],
                sorties=res['sorties'],
                designation=res['designation']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout.")

    def on_edit(self):
        selected = self.tbl_banque.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une transaction.")
            return
            
        row_idx = selected[0].row()
        matrix_idx = self.tbl_banque.item(row_idx, 0).data(Qt.UserRole)
        data = self.current_matrix[matrix_idx]
        
        dlg = CompteSGADialog(self, transaction_id=data['id_transaction'], data_row=data)
        if dlg.exec():
            res = dlg.get_data()
            success = data_manager.banque.update_sga_transaction(
                id_transaction=data['id_transaction'],
                date_transaction=res['date_transaction'],
                n_cheque=res['n_cheque'],
                beneficiaire=res['beneficiaire'],
                entrees=res['entrees'],
                sorties=res['sorties'],
                designation=res['designation']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la modification.")

    def on_delete(self):
        selected = self.tbl_banque.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une transaction.")
            return
            
        row_idx = selected[0].row()
        matrix_idx = self.tbl_banque.item(row_idx, 0).data(Qt.UserRole)
        data = self.current_matrix[matrix_idx]
        
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous annuler cette transaction ? Elle restera traÃ§able.", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            reason, accepted = QInputDialog.getText(self, "Motif d'annulation", "Motif obligatoire :")
            if not accepted:
                return
            try:
                data_manager.banque.delete_sga_transaction(data['id_transaction'], reason)
                self.load_data()
            except (ValueError, PermissionError) as error:
                QMessageBox.warning(self, "Annulation refusÃ©e", str(error))
