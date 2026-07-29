from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from database import data_manager
from ui.table_helper import make_table_editable
from ui.fournisseurs.dialogs import FournisseurDialog

class DonneesBaseFournisseursTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.tbl_fournisseurs = QTableWidget()
        self.tbl_fournisseurs.setColumnCount(5)
        self.tbl_fournisseurs.setHorizontalHeaderLabels([
            "ID", "Fournisseur", "Solde Initial", "Dans Etat Fournisseurs", "Lié à Stock"
        ])
        self.tbl_fournisseurs.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbl_fournisseurs.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_fournisseurs.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_fournisseurs.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        self.toolbar = make_table_editable(
            self.tbl_fournisseurs, "Fournisseurs", "id_fournisseur",
            lambda r: self.tbl_fournisseurs.item(r, 0).data(Qt.UserRole)
                      if self.tbl_fournisseurs.item(r, 0) else None,
            FournisseurDialog, self.load_data, self,
            add_callback=self.add_fournisseur,
            add_label="Nouveau Fournisseur",
            delete_callback=self.delete_fournisseur
        )
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.tbl_fournisseurs)

    def load_data(self):
        data = data_manager.db.fetch_all("SELECT * FROM Fournisseurs ORDER BY nom_fournisseur")
        self.tbl_fournisseurs.setRowCount(len(data))
        for i, row in enumerate(data):
            item_id = QTableWidgetItem(str(row['id_fournisseur']))
            item_id.setData(Qt.UserRole, row['id_fournisseur'])
            
            self.tbl_fournisseurs.setItem(i, 0, item_id)
            self.tbl_fournisseurs.setItem(i, 1, QTableWidgetItem(row['nom_fournisseur']))
            self.tbl_fournisseurs.setItem(i, 2, QTableWidgetItem(f"{float(row['solde_initial'] or 0):.2f}"))
            
            is_inclus = row.get('inclus_etat', 1) == 1
            item_inclus = QTableWidgetItem("Oui" if is_inclus else "Non (Exclu)")
            item_inclus.setTextAlignment(Qt.AlignCenter)
            if is_inclus:
                item_inclus.setForeground(QColor("#2e7d32"))
            else:
                item_inclus.setForeground(QColor("#c62828"))
            self.tbl_fournisseurs.setItem(i, 3, item_inclus)
            
            linked = "Oui" if row.get('stock_supplier_id') else "Non"
            item_linked = QTableWidgetItem(linked)
            item_linked.setTextAlignment(Qt.AlignCenter)
            self.tbl_fournisseurs.setItem(i, 4, item_linked)

    def on_cell_double_clicked(self, row, col):
        # Quick toggle if double clicking on 'Dans Etat Fournisseurs' column
        if col == 3:
            item_id = self.tbl_fournisseurs.item(row, 0)
            if not item_id:
                return
            id_fournisseur = item_id.data(Qt.UserRole)
            current_item = self.tbl_fournisseurs.item(row, 3)
            current_is_inclus = "Oui" in (current_item.text() if current_item else "")
            new_val = 0 if current_is_inclus else 1
            data_manager.db.update_record("Fournisseurs", "id_fournisseur", id_fournisseur, {"inclus_etat": new_val})
            self.load_data()
            
    def add_fournisseur(self):
        dlg = FournisseurDialog(self)
        if dlg.exec():
            self.load_data()
            
    def delete_fournisseur(self, id_fournisseur):
        reply = QMessageBox.question(
            self, "Confirmation", 
            "Voulez-vous vraiment supprimer ce fournisseur ? Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success = data_manager.fournisseurs.delete_fournisseur(id_fournisseur)
            if success:
                QMessageBox.information(self, "Succès", "Fournisseur supprimé avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", "Une erreur est survenue.")
            return success
        return False
