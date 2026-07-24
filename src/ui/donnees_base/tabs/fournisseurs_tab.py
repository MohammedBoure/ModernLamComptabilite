from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PySide6.QtCore import Qt
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
        self.tbl_fournisseurs.setColumnCount(4)
        self.tbl_fournisseurs.setHorizontalHeaderLabels([
            "ID", "Fournisseur", "Solde Initial", "Lié à Stock"
        ])
        self.tbl_fournisseurs.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbl_fournisseurs.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_fournisseurs.setSelectionBehavior(QTableWidget.SelectRows)
        
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
            linked = "Oui" if row.get('stock_supplier_id') else "Non"
            self.tbl_fournisseurs.setItem(i, 3, QTableWidgetItem(linked))
            
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
